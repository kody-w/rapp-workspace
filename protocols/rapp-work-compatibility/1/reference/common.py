"""Strict local helpers and the explicitly pinned canonical RAPP/1 parent."""

from __future__ import annotations

import hashlib
import json
import os
import re
import stat
import subprocess
import types
import unicodedata
from pathlib import Path

PROFILE = "rapp-work-compatibility/1"
ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[2]
MAX_BYTES = 16 * 1024 * 1024


class Refusal(ValueError):
    pass


def require(condition: bool, reason: str) -> None:
    if not condition:
        raise Refusal(reason)


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def domain(value: object, depth: int = 1, active: set[int] | None = None) -> None:
    active = set() if active is None else active
    require(depth <= 64, "JSON depth")
    if isinstance(value, (dict, list)):
        require(id(value) not in active, "cyclic input refused")
        active.add(id(value))
    if isinstance(value, dict):
        for key, child in value.items():
            require(type(key) is str, "JSON object key must be text")
            domain(key, depth, active)
            domain(child, depth + 1, active)
    elif isinstance(value, list):
        for child in value:
            domain(child, depth + 1, active)
    elif isinstance(value, str):
        require(not any(0xD800 <= ord(char) <= 0xDFFF for char in value), "JSON surrogate")
    else:
        require(
            value is None
            or type(value) is bool
            or (type(value) is int and abs(value) <= 2**53 - 1),
            "JSON exact integer domain",
        )
    if isinstance(value, (dict, list)):
        active.remove(id(value))


def canonical_bytes(value: object) -> bytes:
    domain(value)
    return (
        json.dumps(
            value,
            ensure_ascii=False,
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        + "\n"
    ).encode("utf-8")


def strict_json(raw: bytes) -> object:
    require(type(raw) is bytes and len(raw) <= MAX_BYTES, "JSON byte budget")

    def pairs(items: list[tuple[str, object]]) -> dict[str, object]:
        value: dict[str, object] = {}
        for key, child in items:
            require(key not in value, "duplicate JSON key")
            value[key] = child
        return value

    def invalid_number(_value: str) -> object:
        raise Refusal("floating-point JSON is unsupported")

    try:
        value = json.loads(
            raw,
            object_pairs_hook=pairs,
            parse_float=invalid_number,
            parse_constant=invalid_number,
        )
    except (UnicodeError, json.JSONDecodeError, RecursionError) as error:
        raise Refusal("strict JSON refused") from error
    domain(value)
    return value


def read_file(path: Path, limit: int = MAX_BYTES) -> bytes:
    path = Path(path)
    parent = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        descriptor = os.open(
            path.name,
            os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK,
            dir_fd=parent,
        )
        try:
            before = os.fstat(descriptor)
            require(
                stat.S_ISREG(before.st_mode)
                and before.st_nlink == 1
                and before.st_size <= limit,
                "unsafe or oversized file",
            )
            chunks: list[bytes] = []
            count = 0
            while True:
                chunk = os.read(descriptor, min(65536, limit + 1 - count))
                if not chunk:
                    break
                chunks.append(chunk)
                count += len(chunk)
                require(count <= limit, "file byte budget")
            after = os.fstat(descriptor)
            named = os.stat(path.name, dir_fd=parent, follow_symlinks=False)
            fields = lambda value: (
                value.st_dev,
                value.st_ino,
                value.st_mode,
                value.st_nlink,
                value.st_size,
                value.st_mtime_ns,
                value.st_ctime_ns,
            )
            require(fields(before) == fields(after) == fields(named), "file changed during read")
            return b"".join(chunks)
        finally:
            os.close(descriptor)
    finally:
        os.close(parent)


def write_file(path: Path, raw: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(raw)


class Parent:
    """Load only the canonical RAPP/1 bytes pinned by Workspace/1 provenance."""

    def __init__(self, checkout: Path):
        require(checkout is not None, "explicit --rapp1-path required")
        self.path = Path(checkout)
        workspace_provenance = json.loads(
            read_file(REPO / "protocols/rapp-workspace/1/provenance.json")
        )
        pin = workspace_provenance["rapp1"]
        commit = subprocess.run(
            ["git", "-C", str(self.path), "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        require(commit == pin["commit"], "canonical RAPP/1 checkout commit mismatch")
        sources: dict[str, bytes] = {}
        for entry in pin["files"]:
            raw = read_file(self.path / entry["path"], MAX_BYTES)
            require(
                len(raw) == entry["bytes"] and sha(raw) == entry["sha256"],
                "canonical RAPP/1 byte substitution: " + entry["path"],
            )
            sources[entry["path"]] = raw
        self.r = types.ModuleType("rapp_work_compatibility_parent")
        self.r.__file__ = str(self.path / "rapp.py")
        exec(  # noqa: S102 - consumes only the exact pinned canonical RAPP/1 bytes
            compile(sources["rapp.py"], self.r.__file__, "exec"),
            self.r.__dict__,
        )
        head = None
        for line in sources["anchor/chain.jsonl"].splitlines():
            frame = self.r._strict_json(line)
            ok, step, reason = self.r.verify_frame(
                frame,
                head=head,
                stream_id_of_record=pin["anchor_stream"],
            )
            require(ok, f"canonical RAPP/1 authority refusal: {step}: {reason}")
            head = frame
        require(head is not None and wave(head) == pin["selected_head"], "authority head mismatch")
        require(
            head["payload"]["normative"]["text"].encode("utf-8") == sources["SPEC.md"],
            "canonical RAPP/1 normative materialization mismatch",
        )
        self.pin = pin

    def octets(self, value: object) -> bytes:
        domain(value)
        raw = self.r.canonical(value).encode("utf-8")
        require(len(raw) <= MAX_BYTES, "canonical byte budget")
        return raw

    def parse(self, raw: bytes) -> object:
        value = self.r._strict_json(raw)
        domain(value)
        require(self.octets(value) == raw, "noncanonical RAPP/1 JSON")
        return value

    def particle(self, value: object) -> dict[str, str]:
        self.octets(value)
        return {"space": "rapp/1:particle", "hash": self.r.H("rapp/1:particle", value)}


def wave(frame: dict[str, object]) -> dict[str, str]:
    return {"space": "rapp/1:wave", "hash": str(frame["frame_hash"])}


class SchemaSet:
    """The bounded Draft 2020-12 vocabulary used by this profile."""

    def __init__(self) -> None:
        self.documents = {
            path.name: json.loads(read_file(path))
            for path in sorted((ROOT / "schemas").glob("*.json"))
        }

    def validate(self, value: object, name: str | None = None) -> object:
        domain(value)
        if name is None:
            require(type(value) is dict and type(value.get("schema")) is str, "schema required")
            name = str(value["schema"]).removeprefix(PROFILE + "/") + ".schema.json"
        require(name in self.documents, "unsupported profile schema")
        self._check(value, self.documents[name])
        return value

    def _check(self, value: object, schema: dict[str, object]) -> None:
        if "$ref" in schema:
            file_name, fragment = str(schema["$ref"]).split("#")
            require(
                file_name in self.documents and fragment.startswith("/$defs/"),
                "unsupported schema reference",
            )
            target = self.documents[file_name]["$defs"][fragment.split("/")[-1]]
            self._check(value, target)
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
            require(
                any(type(value) is type(item) and value == item for item in schema["enum"]),
                "schema enum",
            )
        if "type" not in schema:
            return
        expected = {
            "object": dict,
            "array": list,
            "string": str,
            "integer": int,
            "boolean": bool,
            "null": type(None),
        }[schema["type"]]
        require(type(value) is expected, "schema type: " + str(schema["type"]))
        if expected is dict:
            required = set(schema.get("required", []))
            properties = schema.get("properties", {})
            require(required <= set(value), "schema required properties")
            if schema.get("additionalProperties") is False:
                require(set(value) <= set(properties), "schema additional properties")
            for key, child in value.items():
                require(key in properties, "schema unknown property")
                self._check(child, properties[key])
        elif expected is list:
            require(
                int(schema.get("minItems", 0)) <= len(value) <= int(schema.get("maxItems", 2**31)),
                "schema array bounds",
            )
            if schema.get("uniqueItems"):
                require(
                    len({canonical_bytes(item) for item in value}) == len(value),
                    "schema array duplicates",
                )
            for child in value:
                self._check(child, schema["items"])
        elif expected is str:
            require(
                int(schema.get("minLength", 0))
                <= len(value)
                <= int(schema.get("maxLength", 2**31)),
                "schema string bounds",
            )
            if "pattern" in schema:
                require(re.search(str(schema["pattern"]), value) is not None, "schema string pattern")
            require(unicodedata.normalize("NFC", value) == value, "profile strings must be NFC")
        elif expected is int:
            require(
                int(schema.get("minimum", -(2**53 - 1)))
                <= value
                <= int(schema.get("maximum", 2**53 - 1)),
                "schema integer bounds",
            )
