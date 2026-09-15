"""Explicit canonical dependency, bounded schema evaluation, and local safe I/O."""

import contextlib
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import types
import unicodedata
import uuid
from schema_source import PROFILE

ROOT = Path(__file__).resolve().parents[1]
MAX_BYTES = 1024 * 1024


class Refusal(ValueError):
    pass


def require(condition, reason):
    if not condition:
        raise Refusal(reason)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def wave(frame):
    return {"space": "rapp/1:wave", "hash": frame["frame_hash"]}


def address(value):
    require(isinstance(value, dict) and set(value) == {"space", "hash"}
            and value["space"] == "rapp/1:wave"
            and isinstance(value["hash"], str)
            and re.fullmatch(r"[0-9a-f]{64}", value["hash"] or "") is not None,
            "wave address required")
    return value["hash"]


def domain(value, depth=1):
    require(depth <= 64, "JSON depth")
    if isinstance(value, dict):
        for key, child in value.items():
            domain(key, depth)
            domain(child, depth + 1)
    elif isinstance(value, list):
        for child in value:
            domain(child, depth + 1)
    elif isinstance(value, str):
        require(not any(0xD800 <= ord(c) <= 0xDFFF for c in value), "JSON surrogate")
    else:
        require(value is None or type(value) is bool
                or (type(value) is int and abs(value) <= 2**53 - 1), "JSON exact integer domain")


@contextlib.contextmanager
def directory(path, create=False):
    path = Path(path)
    require(".." not in path.parts, "path escape")
    path = path.absolute()
    flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
    fd = os.open(path.anchor, flags)
    try:
        for part in path.parts[1:]:
            if create:
                try:
                    os.mkdir(part, 0o700, dir_fd=fd)
                except FileExistsError:
                    pass
            next_fd = os.open(part, flags, dir_fd=fd)
            os.close(fd)
            fd = next_fd
        yield fd
    except OSError as exc:
        raise Refusal("unsafe directory or symlink: " + str(exc)) from exc
    finally:
        os.close(fd)


def read_file(path, limit=MAX_BYTES):
    path = Path(path)
    with directory(path.parent) as parent:
        fd = os.open(path.name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=parent)
        try:
            before = os.fstat(fd)
            require(stat.S_ISREG(before.st_mode) and before.st_nlink == 1, "unsafe file or hardlink")
            require(before.st_size <= limit, "file byte budget")
            chunks, count = [], 0
            while True:
                raw = os.read(fd, min(65536, limit + 1 - count))
                if not raw:
                    break
                chunks.append(raw)
                count += len(raw)
                require(count <= limit, "file byte budget")
            after = os.fstat(fd)
            named = os.stat(path.name, dir_fd=parent, follow_symlinks=False)
            fields = lambda s: (s.st_dev, s.st_ino, s.st_mode, s.st_nlink, s.st_size, s.st_mtime_ns, s.st_ctime_ns)
            require(fields(before) == fields(after) == fields(named), "file identity changed during read")
            return b"".join(chunks)
        finally:
            os.close(fd)


def write_file(path, raw, immutable=False):
    path = Path(path)
    with directory(path.parent, create=True) as parent:
        if os.path.lexists(path):
            existing = read_file(path, max(len(raw), 16 * MAX_BYTES))
            if immutable:
                require(existing == raw, "immutable file collision")
                return
        name = ".pending-" + uuid.uuid4().hex
        fd = os.open(name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600, dir_fd=parent)
        try:
            with os.fdopen(fd, "wb") as stream:
                stream.write(raw)
                stream.flush()
                os.fsync(stream.fileno())
            if immutable:
                try:
                    os.link(name, path.name, src_dir_fd=parent, dst_dir_fd=parent, follow_symlinks=False)
                except FileExistsError:
                    require(read_file(path, len(raw)) == raw, "immutable file collision")
                os.unlink(name, dir_fd=parent)
            else:
                os.replace(name, path.name, src_dir_fd=parent, dst_dir_fd=parent)
            os.fsync(parent)
        finally:
            try:
                os.unlink(name, dir_fd=parent)
            except FileNotFoundError:
                pass


class Parent:
    def __init__(self, checkout):
        require(os.environ.get("RAPP_ALLOW_UNQUALIFIED_EXPERIMENTS") == "1",
                "withdrawn experiment disabled; not first-Grail conformance")
        require(checkout is not None, "explicit --rapp1-path required; no discovery fallback")
        self.path = Path(checkout)
        provenance = json.loads(read_file(ROOT / "provenance.json"))
        pin = provenance["rapp1"]
        commit = subprocess.run(
            ["git", "-C", str(self.path), "rev-parse", "HEAD"], check=True,
            capture_output=True, text=True).stdout.strip()
        require(commit == pin["commit"], "canonical checkout commit differs from inspection pin")
        sources = {}
        for entry in pin["files"]:
            raw = read_file(self.path / entry["path"], 16 * MAX_BYTES)
            require(sha(raw) == entry["sha256"] and len(raw) == entry["bytes"],
                    "canonical checkout byte substitution: " + entry["path"])
            sources[entry["path"]] = raw
        self.r = types.ModuleType("workspace_canonical_rapp")
        self.r.__file__ = str(self.path / "rapp.py")
        exec(compile(sources["rapp.py"], self.r.__file__, "exec"), self.r.__dict__)
        # The parent's retained pre-rev-14 lines have historical whitespace.
        # Verify their pinned octets and parent semantics, not our new payload encoding rule.
        chain = [self.r._strict_json(line) for line in sources["anchor/chain.jsonl"].splitlines()]
        head = None
        for frame in chain:
            ok, step, reason = self.r.verify_frame(frame, head=head, stream_id_of_record=pin["anchor_stream"])
            require(ok, f"canonical authority chain: {step}: {reason}")
            head = frame
        require(wave(head) == pin["selected_head"], "canonical authority head mismatch")
        normative = head["payload"]["normative"]
        require(normative["text"].encode("utf-8") == sources["SPEC.md"], "parent materialization mismatch")
        self.pin = pin
        self.schemas = SchemaSet(self)

    def octets(self, value):
        domain(value)
        raw = self.r.canonical(value).encode("utf-8")
        require(len(raw) <= MAX_BYTES, "canonical byte budget")
        return raw

    def parse(self, raw):
        require(isinstance(raw, bytes) and len(raw) <= MAX_BYTES, "JSON byte budget")
        try:
            value = self.r._strict_json(raw)
            require(self.octets(value) == raw, "noncanonical JSON bytes")
            return value
        except (ValueError, UnicodeError, TypeError, RecursionError) as exc:
            raise Refusal("JSON refused: " + str(exc)) from exc

    def particle(self, value):
        self.octets(value)
        return {"space": "rapp/1:particle", "hash": self.r.H("rapp/1:particle", value)}


class SchemaSet:
    """Only the vocabulary used by the checked-in schemas, not general JSON Schema."""

    def __init__(self, parent):
        self.parent = parent
        self.documents = {p.name: json.loads(read_file(p)) for p in sorted((ROOT / "schemas").glob("*.json"))}

    def validate(self, value, name=None):
        self.parent.octets(value)
        if name is None:
            require(isinstance(value, dict) and isinstance(value.get("schema"), str), "payload schema required")
            name = value["schema"].removeprefix(PROFILE + "/") + ".schema.json"
        require(name in self.documents, "unsupported payload schema")
        self._check(value, self.documents[name])
        return value

    def _check(self, value, schema, *, preserved_octets=False):
        if "$ref" in schema:
            file, fragment = schema["$ref"].split("#")
            require(file in self.documents and fragment.startswith("/$defs/"), "unsupported schema reference")
            self._check(value, self.documents[file]["$defs"][fragment.split("/")[-1]])
        if "oneOf" in schema:
            passes = 0
            for option in schema["oneOf"]:
                try:
                    self._check(value, option)
                    passes += 1
                except Refusal:
                    pass
            require(passes == 1, "schema oneOf")
        if "const" in schema:
            require(type(value) is type(schema["const"]) and value == schema["const"], "schema const")
        if "enum" in schema:
            require(any(type(value) is type(x) and value == x for x in schema["enum"]), "schema enum")
        if "type" not in schema:
            return
        expected = {"object": dict, "array": list, "string": str, "integer": int,
                    "boolean": bool, "null": type(None)}[schema["type"]]
        require(type(value) is expected, "schema type: " + schema["type"])
        if expected is dict:
            require(set(value) == set(schema["required"]), "closed schema member set")
            for name, child in value.items():
                self._check(child, schema["properties"][name], preserved_octets=name == "value_json")
        elif expected is list:
            require(schema["minItems"] <= len(value) <= schema["maxItems"], "schema array bounds")
            if schema["uniqueItems"]:
                require(len({self.parent.octets(x) for x in value}) == len(value), "schema array duplicates")
            for child in value:
                self._check(child, schema["items"])
        elif expected is str:
            require(schema["minLength"] <= len(value) <= schema["maxLength"], "schema string bounds")
            require(re.search(schema["pattern"], value) is not None, "schema string pattern")
            require(preserved_octets or unicodedata.normalize("NFC", value) == value,
                    "profile new strings MUST be NFC")
        elif expected is int:
            require(schema["minimum"] <= value <= schema["maximum"], "schema integer bounds")
