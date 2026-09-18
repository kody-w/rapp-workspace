"""Bounded application JSON and explicit local I/O, never RAPP wire primitives."""

from __future__ import annotations

import contextlib
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import uuid

from schema_source import (
    MAX_CONTENT_BYTES, MAX_INT, MAX_JSON_DEPTH, MAX_JSON_NODES, MAX_SHARD_BYTES,
    RAPPID, ROOT, schema,
)

REPO = ROOT.parents[2]
SCHEMA = schema()


class Refusal(ValueError):
    """Input is unavailable, stale, ambiguous, corrupt, or outside the profile."""


def require(condition, reason):
    if not condition:
        raise Refusal(reason)


def sha(raw):
    require(type(raw) is bytes, "exact octets required")
    return hashlib.sha256(raw).hexdigest()


def domain(value):
    active = set()
    remaining = MAX_JSON_NODES

    def visit(item, depth):
        nonlocal remaining
        remaining -= 1
        require(remaining >= 0 and depth <= MAX_JSON_DEPTH, "JSON work/depth budget")
        if type(item) in (dict, list):
            require(id(item) not in active, "cyclic JSON")
            require(len(item) <= MAX_JSON_NODES, "JSON container budget")
            active.add(id(item))
            if type(item) is dict:
                require(len(item) <= 64, "JSON object member budget")
                for key, child in item.items():
                    require(type(key) is str, "JSON member must be text")
                    visit(key, depth + 1)
                    visit(child, depth + 1)
            else:
                for child in item:
                    visit(child, depth + 1)
            active.remove(id(item))
        elif type(item) is str:
            require(len(item) <= 4096 and item.isascii(), "bounded ASCII application string")
        else:
            require(
                item is None or type(item) is bool
                or (type(item) is int and abs(item) <= MAX_INT),
                "exact JSON integer domain",
            )

    visit(value, 0)


def _canonical_size(value, limit):
    used = 0

    def add(size):
        nonlocal used
        used += size
        require(used <= limit, "canonical application byte budget")

    def measure(item):
        if item is None:
            add(4)
        elif type(item) is bool:
            add(4 if item else 5)
        elif type(item) is int:
            add(len(str(item)))
        elif type(item) is str:
            add(len(json.dumps(
                item, ensure_ascii=False, separators=(",", ":"),
            ).encode("ascii")))
        elif type(item) is list:
            add(2 + max(0, len(item) - 1))
            for child in item:
                measure(child)
        else:
            add(2 + max(0, len(item) - 1))
            for key in sorted(item):
                measure(key)
                add(1)
                measure(item[key])

    measure(value)
    return used


def canonical(value, limit=MAX_SHARD_BYTES):
    domain(value)
    expected = _canonical_size(value, limit)
    raw = json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode("ascii")
    require(len(raw) == expected, "canonical application size mismatch")
    return raw


def parse(raw, limit=MAX_SHARD_BYTES, *, exact=True):
    require(type(raw) is bytes and len(raw) <= limit, "JSON byte budget")

    def pairs(items):
        value = {}
        for key, child in items:
            require(key not in value, "duplicate JSON member")
            value[key] = child
        return value

    def integer(value):
        require(len(value) <= 17, "integer text budget")
        result = int(value)
        require(abs(result) <= MAX_INT, "exact JSON integer domain")
        return result

    def invalid(_value):
        raise Refusal("non-integer JSON number")

    try:
        value = json.loads(
            raw.decode("ascii"), object_pairs_hook=pairs, parse_int=integer,
            parse_float=invalid, parse_constant=invalid,
        )
        rendered = canonical(value, limit)
        require(not exact or rendered == raw, "noncanonical application bytes")
        return value
    except (UnicodeError, json.JSONDecodeError, RecursionError) as error:
        raise Refusal("invalid application JSON") from error


def validate(value, name):
    """Only the fixed vocabulary in schema_source.py, not a general schema engine."""
    domain(value)
    require(name in SCHEMA["$defs"], "unknown application schema")

    def check(item, definition):
        if "$ref" in definition:
            target = definition["$ref"]
            require(target.startswith("#/$defs/"), "external schema reference refused")
            check(item, SCHEMA["$defs"][target.split("/")[-1]])
            return
        if "const" in definition:
            require(type(item) is type(definition["const"]) and item == definition["const"],
                    "schema const")
        if "enum" in definition:
            require(any(type(item) is type(choice) and item == choice
                        for choice in definition["enum"]), "schema enum")
        if "type" not in definition:
            return
        kind = {"object": dict, "array": list, "string": str, "integer": int}[definition["type"]]
        require(type(item) is kind, "schema type: " + definition["type"])
        if kind is dict:
            require(set(item) == set(definition["required"]), "closed object members")
            for key, child in item.items():
                check(child, definition["properties"][key])
        elif kind is list:
            require(definition["minItems"] <= len(item) <= definition["maxItems"],
                    "schema array bounds")
            for child in item:
                check(child, definition["items"])
        elif kind is str:
            require(definition["minLength"] <= len(item) <= definition["maxLength"],
                    "schema string bounds")
            require(re.fullmatch(definition["pattern"], item) is not None,
                    "schema string grammar")
            if definition == RAPPID:
                # This is an application field-length check, not identity authentication.
                owner, slug_tail = item[8:].split("/", 1)
                slug, _tail = slug_tail.rsplit(":", 1)
                require(1 <= len(owner) <= 39 and 1 <= len(slug) <= 100,
                        "full RAPPID component bounds")
        else:
            require(definition["minimum"] <= item <= definition["maximum"],
                    "schema integer bounds")

    check(value, SCHEMA["$defs"][name])
    return value


@contextlib.contextmanager
def directory(path, *, create=False):
    path = Path(path)
    require(".." not in path.parts, "path traversal refused")
    require(len(path.parts) <= 64 and len(os.fsencode(path)) <= 4096, "explicit path depth/byte budget")
    require(hasattr(os, "O_NOFOLLOW") and hasattr(os, "O_DIRECTORY"),
            "safe filesystem adapter unavailable; no weakened fallback")
    path = path.absolute()
    fd = os.open(path.anchor, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        for part in path.parts[1:]:
            if create:
                try:
                    os.mkdir(part, 0o700, dir_fd=fd)
                except FileExistsError:
                    pass
            next_fd = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
            os.close(fd)
            fd = next_fd
        yield fd
    except OSError as error:
        raise Refusal("unsafe or missing explicitly supplied directory") from error
    finally:
        os.close(fd)


def read_file(path, limit=MAX_CONTENT_BYTES):
    path = Path(path)
    with directory(path.parent) as parent:
        try:
            fd = os.open(path.name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=parent)
            try:
                before = os.fstat(fd)
                require(stat.S_ISREG(before.st_mode) and before.st_nlink == 1,
                        "regular unlinked-from-other-names file required")
                require(before.st_size <= limit, "file byte budget")
                count, chunks = 0, []
                while True:
                    chunk = os.read(fd, min(65536, limit + 1 - count))
                    if not chunk:
                        break
                    count += len(chunk)
                    require(count <= limit, "streaming byte budget")
                    chunks.append(chunk)
                after = os.fstat(fd)
                named = os.stat(path.name, dir_fd=parent, follow_symlinks=False)
                fields = lambda s: (
                    s.st_dev, s.st_ino, s.st_size, s.st_mode, s.st_nlink,
                    s.st_mtime_ns, s.st_ctime_ns,
                )
                require(fields(before) == fields(after) == fields(named),
                        "file changed during bounded read")
                return b"".join(chunks)
            finally:
                os.close(fd)
        except OSError as error:
            raise Refusal("explicit file unavailable; no fallback") from error


def write_file(path, raw):
    require(type(raw) is bytes, "exact output bytes required")
    path = Path(path)
    with directory(path.parent, create=True) as parent:
        if os.path.lexists(path):
            read_file(path, max(len(raw), MAX_CONTENT_BYTES))
        pending = ".index-pending-" + uuid.uuid4().hex
        fd = os.open(
            pending, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
            0o600, dir_fd=parent,
        )
        try:
            with os.fdopen(fd, "wb") as stream:
                stream.write(raw)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(pending, path.name, src_dir_fd=parent, dst_dir_fd=parent)
            os.fsync(parent)
        finally:
            try:
                os.unlink(pending, dir_fd=parent)
            except FileNotFoundError:
                pass


def pretty(value):
    return (json.dumps(value, ensure_ascii=True, indent=2) + "\n").encode("ascii")
