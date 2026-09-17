"""Uniquely named strict helpers for the Work Organization/1 reference."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path, PurePosixPath
import re
from typing import Any


PROFILE = "rapp-work-organization/1"
ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[2]
MAX_SAFE_INTEGER = (1 << 53) - 1
HASH_RE = re.compile(r"[0-9a-f]{64}\Z")
GIT_HASH_RE = re.compile(r"[0-9a-f]{40}\Z")
RAPPID_RE = re.compile(
    r"rappid:@(?=[^/]{1,39}/)[a-z0-9]+(?:-[a-z0-9]+)*/"
    r"(?=[^:]{1,100}:)[a-z0-9]+(?:-[a-z0-9]+)*:[0-9a-f]{64}\Z"
)


class Refusal(ValueError):
    """Stable protocol refusal."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


def require(condition: bool, code: str, message: str) -> None:
    if not condition:
        raise Refusal(code, message)


def canonical_bytes(value: Any) -> bytes:
    validate_plain_json(value)
    return json.dumps(
        value,
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def pretty_bytes(value: Any) -> bytes:
    validate_plain_json(value)
    return (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def particle(value: Any) -> str:
    return sha256(b"rapp/1:particle\n" + canonical_bytes(value))


def read_bytes(path: Path, limit: int = 16 * 1024 * 1024) -> bytes:
    require(path.is_file(), "REFUSE_FILE", f"Missing required file: {path}")
    data = path.read_bytes()
    require(len(data) <= limit, "REFUSE_LIMIT", f"File exceeds bound: {path}")
    return data


def read_json(path: Path, limit: int = 16 * 1024 * 1024) -> Any:
    data = read_bytes(path, limit)
    try:
        return json.loads(
            data.decode("utf-8"),
            object_pairs_hook=_unique_pairs,
            parse_float=_invalid_number,
            parse_constant=_invalid_number,
        )
    except (UnicodeError, json.JSONDecodeError, RecursionError) as error:
        raise Refusal("REFUSE_JSON", f"Invalid strict JSON: {path}") from error


def _unique_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        require(key not in result, "REFUSE_JSON", "Duplicate JSON member.")
        result[key] = value
    return result


def _invalid_number(_value: str) -> Any:
    raise Refusal("REFUSE_NUMBER", "Floats and nonfinite numbers are forbidden.")


def validate_plain_json(value: Any, depth: int = 0) -> None:
    require(depth <= 64, "REFUSE_DEPTH", "JSON nesting exceeds the profile bound.")
    if value is None or type(value) in (bool, str):
        return
    if type(value) is int:
        require(abs(value) <= MAX_SAFE_INTEGER, "REFUSE_NUMBER", "Integer is outside I-JSON.")
        return
    if type(value) is list:
        require(len(value) <= 10000, "REFUSE_LIMIT", "Array exceeds the profile bound.")
        for item in value:
            validate_plain_json(item, depth + 1)
        return
    if type(value) is dict:
        require(
            len(value) <= 10000 and all(type(key) is str for key in value),
            "REFUSE_OBJECT",
            "A bounded string-keyed object is required.",
        )
        for item in value.values():
            validate_plain_json(item, depth + 1)
        return
    raise Refusal("REFUSE_TYPE", "Only plain I-JSON values are supported.")


def exact_object(value: Any, keys: set[str], code: str = "REFUSE_SHAPE") -> dict[str, Any]:
    require(type(value) is dict and set(value) == keys, code, "Closed object shape required.")
    return value


def hash_value(value: Any, code: str = "REFUSE_HASH") -> str:
    require(type(value) is str and HASH_RE.fullmatch(value) is not None, code, "Invalid SHA-256.")
    return value


def git_hash(value: Any) -> str:
    require(
        type(value) is str and GIT_HASH_RE.fullmatch(value) is not None,
        "REFUSE_GIT_HASH",
        "Invalid Git SHA-1 transport identifier.",
    )
    return value


def bounded_int(value: Any, low: int, high: int, code: str = "REFUSE_NUMBER") -> int:
    require(
        type(value) is int and not isinstance(value, bool) and low <= value <= high,
        code,
        "Integer is outside the allowed range.",
    )
    return value


def safe_path(value: Any) -> str:
    require(type(value) is str and 0 < len(value) <= 1024, "REFUSE_PATH", "Invalid path.")
    assert isinstance(value, str)
    path = PurePosixPath(value)
    require(
        not path.is_absolute()
        and path.as_posix() == value
        and all(part not in {"", ".", ".."} for part in path.parts)
        and "\\" not in value
        and "\x00" not in value,
        "REFUSE_PATH",
        "Path must be normalized relative POSIX text.",
    )
    return value


def wave(value: Any) -> dict[str, str]:
    item = exact_object(value, {"space", "hash"}, "REFUSE_WAVE")
    require(item["space"] == "rapp/1:wave", "REFUSE_WAVE", "Wave space required.")
    hash_value(item["hash"], "REFUSE_WAVE")
    return item


def particle_ref(value: Any) -> dict[str, str]:
    item = exact_object(value, {"space", "hash"}, "REFUSE_PARTICLE")
    require(item["space"] == "rapp/1:particle", "REFUSE_PARTICLE", "Particle space required.")
    hash_value(item["hash"], "REFUSE_PARTICLE")
    return item


def egg(value: Any) -> dict[str, str]:
    item = exact_object(value, {"space", "hash"}, "REFUSE_EGG")
    require(item["space"] == "rapp/1:egg-manifest", "REFUSE_EGG", "Egg manifest space required.")
    hash_value(item["hash"], "REFUSE_EGG")
    return item


def content_head(value: Any) -> dict[str, Any]:
    item = exact_object(
        value,
        {"entry_id", "path", "mode", "sha256", "bytes", "content"},
        "REFUSE_CONTENT_HEAD",
    )
    require(
        type(item["entry_id"]) is str and 0 < len(item["entry_id"]) <= 256,
        "REFUSE_CONTENT_HEAD",
        "Invalid entry identifier.",
    )
    safe_path(item["path"])
    require(item["mode"] in {"100644", "100755"}, "REFUSE_CONTENT_HEAD", "Invalid file mode.")
    hash_value(item["sha256"], "REFUSE_CONTENT_HEAD")
    bounded_int(item["bytes"], 0, 1 << 30, "REFUSE_CONTENT_HEAD")
    particle_ref(item["content"])
    return item
