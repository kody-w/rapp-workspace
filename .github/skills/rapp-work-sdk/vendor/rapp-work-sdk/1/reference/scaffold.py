#!/usr/bin/env python3
"""Install and update the additive offline RAPP Work SDK/1 sidecar."""

from __future__ import annotations

import argparse
import copy
from contextlib import contextmanager
import ctypes
from datetime import datetime, timezone
import errno
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import sys


PROFILE_ID = "rapp-work-sdk/1"
SIDECAR_NAME = ".rapp-work"
MAX_JSON_BYTES = 4 * 1024 * 1024
HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")
RAPPID = re.compile(
    r"^rappid:@(?=[^/]{1,39}/)[a-z0-9]+(?:-[a-z0-9]+)*/"
    r"(?=[^:]{1,100}:)[a-z0-9]+(?:-[a-z0-9]+)*:[0-9a-f]{64}$"
)
UTC = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}\.[0-9]{3}Z$")
_VERIFIED_PROFILE_FILES = globals().get("_RAPP_WORK_SDK_VERIFIED_FILES")


class Refusal(ValueError):
    """Fail-closed profile refusal."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise Refusal(message)


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _json_domain(value: object, depth: int = 0) -> None:
    require(depth <= 64, "JSON depth exceeds profile limit")
    if isinstance(value, dict):
        for key, child in value.items():
            require(type(key) is str, "JSON object keys must be text")
            _json_domain(child, depth + 1)
    elif isinstance(value, list):
        for child in value:
            _json_domain(child, depth + 1)
    elif isinstance(value, str):
        require(
            not any(0xD800 <= ord(character) <= 0xDFFF for character in value),
            "JSON surrogate is forbidden",
        )
    else:
        require(
            value is None
            or type(value) is bool
            or (type(value) is int and abs(value) <= 2**53 - 1),
            "JSON values must use the exact integer domain",
        )


def canonical_bytes(value: object) -> bytes:
    _json_domain(value)
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def strict_json(raw: bytes, source: str) -> dict:
    require(len(raw) <= MAX_JSON_BYTES, f"{source} exceeds the JSON byte limit")

    def reject_duplicates(pairs):
        value = {}
        for key, item in pairs:
            if key in value:
                raise Refusal(f"duplicate JSON member in {source}: {key}")
            value[key] = item
        return value

    def reject_constant(value):
        raise Refusal(f"non-finite JSON value in {source}: {value}")

    try:
        value = json.loads(
            raw.decode("utf-8"),
            object_pairs_hook=reject_duplicates,
            parse_constant=reject_constant,
        )
    except UnicodeDecodeError as error:
        raise Refusal(f"{source} is not UTF-8") from error
    except json.JSONDecodeError as error:
        raise Refusal(f"invalid JSON in {source}: {error}") from error
    require(isinstance(value, dict), f"{source} must be a JSON object")
    _json_domain(value)
    return value


def utc_now() -> str:
    now = datetime.now(timezone.utc)
    return now.strftime("%Y-%m-%dT%H:%M:%S.") + f"{now.microsecond // 1000:03d}Z"


def _profile_root() -> Path:
    base = Path(__file__).resolve().parents[1]
    candidates = (base, base / "vendor" / "rapp-work-sdk" / "1")
    for candidate in candidates:
        if (candidate / "profile.json").is_file():
            return candidate
    raise Refusal("pinned rapp-work-sdk/1 profile bytes are unavailable")


PROFILE_ROOT = _profile_root()


def _profile_file_bytes(relative: str) -> bytes:
    if _VERIFIED_PROFILE_FILES is not None:
        require(
            isinstance(_VERIFIED_PROFILE_FILES, dict)
            and relative in _VERIFIED_PROFILE_FILES
            and isinstance(_VERIFIED_PROFILE_FILES[relative], bytes),
            f"verified skill bundle omitted profile file: {relative}",
        )
        return _VERIFIED_PROFILE_FILES[relative]
    path = PROFILE_ROOT.joinpath(*PurePosixPath(relative).parts)
    require(not path.is_symlink() and path.is_file(), f"unsafe profile file: {relative}")
    return path.read_bytes()


PROFILE_RAW = _profile_file_bytes("profile.json")
PROFILE = strict_json(PROFILE_RAW, "profile.json")
PROFILE_SHA256 = sha256(PROFILE_RAW)
PARENT_PIN = strict_json(
    _profile_file_bytes("parent-pin.json"),
    "parent-pin.json",
)


def _exact(value: dict, keys: set[str], label: str) -> None:
    require(set(value) == keys, f"{label} has missing or unknown fields")


def _text(value: object, label: str, maximum: int = 512) -> str:
    require(
        isinstance(value, str)
        and 0 < len(value) <= maximum
        and not any(ord(character) < 32 or ord(character) == 127 for character in value),
        f"{label} is invalid",
    )
    return value


def _hash40(value: object, label: str) -> str:
    require(isinstance(value, str) and HEX40.fullmatch(value) is not None, f"{label} is not a commit pin")
    return value


def _hash64(value: object, label: str) -> str:
    require(isinstance(value, str) and HEX64.fullmatch(value) is not None, f"{label} is not SHA-256")
    return value


def _rappid(value: object, label: str) -> str:
    require(isinstance(value, str) and RAPPID.fullmatch(value) is not None, f"{label} is not a RAPPID")
    return value


def _world(value: object, label: str = "world_id") -> str:
    return _text(value, label, 128)


def _utc(value: object, label: str) -> str:
    require(isinstance(value, str) and UTC.fullmatch(value) is not None, f"{label} is not canonical UTC")
    try:
        datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%fZ")
    except ValueError as error:
        raise Refusal(f"{label} is not a real UTC timestamp") from error
    return value


def _address(value: object, label: str) -> dict:
    require(isinstance(value, dict), f"{label} must be a RAPP/1 wave address")
    _exact(value, {"space", "hash"}, label)
    require(value["space"] == "rapp/1:wave", f"{label} must use the RAPP/1 wave space")
    _hash64(value["hash"], label + ".hash")
    return value


def validate_profile(value: dict) -> dict:
    _exact(
        value,
        {
            "schema",
            "profile",
            "parent",
            "workspace_sibling",
            "sidecar",
            "pins",
            "current_pin",
            "authority",
        },
        "profile",
    )
    require(value["schema"] == PROFILE_ID + "/profile" and value["profile"] == PROFILE_ID, "wrong SDK profile")
    parent = value["parent"]
    require(isinstance(parent, dict), "profile parent is invalid")
    _exact(parent, {"profile", "repository", "commit", "path", "spec_sha256"}, "profile parent")
    require(
        parent["profile"] == "rapp-work/1"
        and parent["repository"] == "https://github.com/kody-w/rapp-1"
        and parent["path"] == "protocols/rapp-work/1/SPEC.md",
        "profile parent binding is invalid",
    )
    _hash40(parent["commit"], "profile parent commit")
    _hash64(parent["spec_sha256"], "profile parent SPEC")
    sibling = value["workspace_sibling"]
    require(isinstance(sibling, dict), "workspace sibling pin is invalid")
    _exact(
        sibling,
        {
            "profile",
            "spec_sha256",
            "manifest_sha256",
            "identity_unchanged",
            "normative_bytes_unchanged",
        },
        "workspace sibling",
    )
    require(
        sibling["profile"] == "rapp-workspace/1"
        and sibling["identity_unchanged"] is True
        and sibling["normative_bytes_unchanged"] is True,
        "Workspace/1 sibling invariants are invalid",
    )
    _hash64(sibling["spec_sha256"], "Workspace/1 spec pin")
    _hash64(sibling["manifest_sha256"], "Workspace/1 manifest pin")
    sidecar = value["sidecar"]
    require(isinstance(sidecar, dict), "sidecar contract is invalid")
    _exact(
        sidecar,
        {
            "path",
            "mode",
            "network_default",
            "atomic_generation_pointer",
            "native_workspace_copy",
        },
        "sidecar contract",
    )
    require(
        sidecar
        == {
            "path": SIDECAR_NAME,
            "mode": "offline-first",
            "network_default": "disabled",
            "atomic_generation_pointer": True,
            "native_workspace_copy": False,
        },
        "sidecar safety contract changed",
    )
    pins = value["pins"]
    require(isinstance(pins, list) and 0 < len(pins) <= 32, "profile pins are invalid")
    seen_pins = set()
    seen_sequences = set()
    current_count = 0
    for item in pins:
        require(isinstance(item, dict), "profile pin is invalid")
        _exact(
            item,
            {
                "pin",
                "sequence",
                "spec_sha256",
                "status",
                "fresh_install",
                "profile_artifact",
            },
            "profile pin",
        )
        pin = _hash40(item["pin"], "profile pin")
        require(pin not in seen_pins, "duplicate profile pin")
        seen_pins.add(pin)
        sequence = item["sequence"]
        require(type(sequence) is int and 0 <= sequence <= 65535, "profile pin sequence is invalid")
        require(sequence not in seen_sequences, "duplicate profile pin sequence")
        seen_sequences.add(sequence)
        require(
            item["status"] in {"migration-source-only", "current"}
            and type(item["fresh_install"]) is bool,
            "profile pin status is invalid",
        )
        _hash64(item["spec_sha256"], "profile pin SPEC")
        artifact = item["profile_artifact"]
        if artifact is not None:
            require(isinstance(artifact, dict), "profile pin artifact is invalid")
            _exact(artifact, {"path", "sha256", "bytes"}, "profile pin artifact")
            require(
                artifact["path"] == f"history/{pin}/profile.json",
                "profile pin artifact path is invalid",
            )
            _hash64(artifact["sha256"], "profile pin artifact")
            require(
                type(artifact["bytes"]) is int
                and 0 < artifact["bytes"] <= MAX_JSON_BYTES,
                "profile pin artifact byte count is invalid",
            )
        if item["fresh_install"]:
            current_count += 1
            require(item["status"] == "current", "fresh pin is not current")
        else:
            require(
                item["status"] == "migration-source-only",
                "historical pin is not migration-source-only",
            )
    current = _hash40(value["current_pin"], "current profile pin")
    require(current in seen_pins and current_count == 1, "profile current pin is ambiguous")
    require(current == parent["commit"], "profile current pin does not match its parent commit")
    current_item = next(item for item in pins if item["pin"] == current)
    require(current_item["fresh_install"] is True, "profile current pin is not installable")
    require(current_item["profile_artifact"] is None, "current profile cannot self-pin its own bytes")
    require(
        current_item["spec_sha256"] == parent["spec_sha256"],
        "current pin consumes different rapp-work/1 bytes",
    )
    require(
        all(
            item["profile_artifact"] is not None
            for item in pins
            if item["pin"] != current
        ),
        "every historical pin must retain its exact profile artifact",
    )
    authority = value["authority"]
    require(isinstance(authority, dict), "profile authority boundary is invalid")
    _exact(
        authority,
        {
            "discovery_only",
            "hive_publication",
            "plugin_activation",
            "native_workspace_mutation",
            "grants_authority",
        },
        "profile authority",
    )
    require(
        authority
        == {
            "discovery_only": True,
            "hive_publication": False,
            "plugin_activation": False,
            "native_workspace_mutation": False,
            "grants_authority": False,
        },
        "profile authority boundary changed",
    )
    return value


def validate_parent_pin() -> None:
    _exact(
        PARENT_PIN,
        {
            "schema",
            "profile",
            "repository",
            "commit",
            "path",
            "spec_sha256",
            "spec_bytes",
            "vendored_path",
            "replacement_rule",
        },
        "parent pin",
    )
    require(
        PARENT_PIN["schema"] == PROFILE_ID + "/parent-pin"
        and PARENT_PIN["profile"] == "rapp-work/1"
        and PARENT_PIN["repository"] == "https://github.com/kody-w/rapp-1"
        and PARENT_PIN["path"] == "protocols/rapp-work/1/SPEC.md"
        and PARENT_PIN["replacement_rule"] == "reviewed-forward-profile-update-only",
        "parent pin contract is invalid",
    )
    _hash40(PARENT_PIN["commit"], "parent commit")
    _hash64(PARENT_PIN["spec_sha256"], "parent SPEC")
    require(type(PARENT_PIN["spec_bytes"]) is int and PARENT_PIN["spec_bytes"] > 0, "parent byte pin invalid")
    require(
        PROFILE["parent"]["commit"] == PARENT_PIN["commit"]
        and PROFILE["parent"]["spec_sha256"] == PARENT_PIN["spec_sha256"]
        and PROFILE["parent"]["repository"] == PARENT_PIN["repository"]
        and PROFILE["parent"]["path"] == PARENT_PIN["path"],
        "profile and parent pin disagree",
    )
    raw = _profile_file_bytes(PARENT_PIN["vendored_path"])
    require(
        len(raw) == PARENT_PIN["spec_bytes"]
        and sha256(raw) == PARENT_PIN["spec_sha256"],
        "vendored rapp-work/1 SPEC does not match its canonical commit pin",
    )


validate_profile(PROFILE)
validate_parent_pin()
PINS = {item["pin"]: item for item in PROFILE["pins"]}
CURRENT_PIN = PROFILE["current_pin"]


def _load_pin_profile_bytes() -> dict[str, bytes]:
    result = {}
    for pin, record in PINS.items():
        artifact = record["profile_artifact"]
        raw = (
            PROFILE_RAW
            if artifact is None
            else _profile_file_bytes(artifact["path"])
        )
        expected_hash = PROFILE_SHA256 if artifact is None else artifact["sha256"]
        expected_bytes = len(PROFILE_RAW) if artifact is None else artifact["bytes"]
        require(
            len(raw) == expected_bytes and sha256(raw) == expected_hash,
            f"retained profile artifact changed for pin {pin}",
        )
        if artifact is not None:
            historical = strict_json(raw, f"retained profile artifact for pin {pin}")
            parent = historical.get("parent")
            pins = historical.get("pins")
            require(
                historical.get("schema") == PROFILE_ID + "/profile"
                and historical.get("profile") == PROFILE_ID
                and historical.get("current_pin") == pin
                and isinstance(parent, dict)
                and parent.get("commit") == pin
                and parent.get("spec_sha256") == record["spec_sha256"]
                and isinstance(pins, list)
                and any(
                    isinstance(item, dict)
                    and item.get("pin") == pin
                    and item.get("spec_sha256") == record["spec_sha256"]
                    and item.get("fresh_install") is True
                    for item in pins
                ),
                f"retained profile artifact does not bind historical pin {pin}",
            )
        result[pin] = raw
    return result


PIN_PROFILE_BYTES = _load_pin_profile_bytes()


def _pin(value: str, label: str) -> dict:
    _hash40(value, label)
    require(value in PINS, f"{label} is unknown to this profile")
    return PINS[value]


def _require_secure_filesystem() -> None:
    require(
        os.name == "posix"
        and hasattr(os, "O_NOFOLLOW")
        and hasattr(os, "O_DIRECTORY"),
        "secure directory-fd filesystem operations are unavailable on this platform",
    )


def _absolute(path: Path) -> Path:
    candidate = path.expanduser()
    if not candidate.is_absolute():
        candidate = Path.cwd() / candidate
    require(".." not in candidate.parts, "parent traversal in filesystem path refused")
    return candidate


@contextmanager
def _directory_fd(path: Path):
    _require_secure_filesystem()
    absolute = _absolute(path)
    flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
    try:
        descriptor = os.open(absolute.anchor, flags)
        try:
            for component in absolute.parts[1:]:
                child = os.open(component, flags, dir_fd=descriptor)
                os.close(descriptor)
                descriptor = child
        except BaseException:
            os.close(descriptor)
            raise
    except OSError as error:
        raise Refusal(f"unsafe or missing directory path refused: {absolute}") from error
    try:
        yield descriptor
    finally:
        os.close(descriptor)


@contextmanager
def _open_directory_at(parent: int, name: str, *, private: bool = False):
    _require_secure_filesystem()
    require("/" not in name and name not in {"", ".", ".."}, "unsafe directory entry name")
    try:
        descriptor = os.open(
            name,
            os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
            dir_fd=parent,
        )
    except OSError as error:
        raise Refusal(f"unsafe or missing directory refused: {name}") from error
    try:
        info = os.fstat(descriptor)
        require(stat.S_ISDIR(info.st_mode), f"directory entry is not a directory: {name}")
        if private:
            require(
                info.st_uid == os.geteuid() and stat.S_IMODE(info.st_mode) == 0o700,
                f"sidecar directory must be owner-only mode 0700: {name}",
            )
        yield descriptor
    finally:
        os.close(descriptor)


def _same_object(left: os.stat_result, right: os.stat_result) -> bool:
    return left.st_dev == right.st_dev and left.st_ino == right.st_ino


def workspace_root(raw: str | Path) -> Path:
    root = _absolute(Path(raw))
    with _directory_fd(root) as descriptor:
        require(stat.S_ISDIR(os.fstat(descriptor).st_mode), "workspace root must be a real directory")
    return root


def _read_regular_at(
    parent: int,
    name: str,
    limit: int = MAX_JSON_BYTES,
    *,
    private: bool = False,
) -> bytes:
    _require_secure_filesystem()
    require("/" not in name and name not in {"", ".", ".."}, "unsafe file entry name")
    try:
        descriptor = os.open(
            name,
            os.O_RDONLY | os.O_NOFOLLOW | getattr(os, "O_NONBLOCK", 0),
            dir_fd=parent,
        )
    except FileNotFoundError as error:
        raise Refusal(f"required file is missing: {name}") from error
    except OSError as error:
        raise Refusal(f"unsafe file refused: {name}") from error
    try:
        before = os.fstat(descriptor)
        require(
            stat.S_ISREG(before.st_mode) and before.st_nlink == 1,
            f"regular non-hardlinked file required: {name}",
        )
        require(before.st_size <= limit, f"file exceeds byte limit: {name}")
        if private:
            require(
                before.st_uid == os.geteuid() and stat.S_IMODE(before.st_mode) == 0o600,
                f"sidecar file must be owner-only mode 0600: {name}",
            )
        chunks = []
        remaining = limit + 1
        while remaining:
            chunk = os.read(descriptor, min(remaining, 128 * 1024))
            if not chunk:
                break
            chunks.append(chunk)
            remaining -= len(chunk)
        raw = b"".join(chunks)
        after = os.fstat(descriptor)
        require(len(raw) <= limit, f"file exceeds byte limit: {name}")
        require(
            _same_object(before, after)
            and before.st_size == after.st_size == len(raw)
            and before.st_mtime_ns == after.st_mtime_ns
            and before.st_ctime_ns == after.st_ctime_ns,
            f"file changed during descriptor read: {name}",
        )
        return raw
    finally:
        os.close(descriptor)


def _safe_regular(path: Path, limit: int = MAX_JSON_BYTES, *, private: bool = False) -> bytes:
    with _directory_fd(path.parent) as parent:
        return _read_regular_at(parent, path.name, limit, private=private)


def _private_directory(path: Path) -> None:
    with _directory_fd(path) as descriptor:
        info = os.fstat(descriptor)
        require(
            info.st_uid == os.geteuid() and stat.S_IMODE(info.st_mode) == 0o700,
            f"sidecar directory must be owner-only mode 0700: {path}",
        )


def _pin_profile_sha256(pin: str) -> str:
    record = _pin(pin, "profile pin")
    artifact = record["profile_artifact"]
    return PROFILE_SHA256 if artifact is None else artifact["sha256"]


def _pin_profile_raw(pin: str) -> bytes:
    _pin(pin, "profile pin")
    return PIN_PROFILE_BYTES[pin]


def _workspace_identity_at(
    root_descriptor: int,
    explicit_world: str | None = None,
) -> dict:
    raw = _read_regular_at(root_descriptor, "rappid.json")
    value = strict_json(raw, "rappid.json")
    identity = _rappid(value.get("rappid"), "workspace rappid")
    native_world = value.get("world_id")
    if native_world is not None:
        _world(native_world, "native workspace world_id")
    if explicit_world is not None:
        _world(explicit_world, "requested world_id")
        require(
            native_world is None or native_world == explicit_world,
            "requested world_id conflicts with the native workspace world",
        )
    world = explicit_world if explicit_world is not None else native_world
    require(world is not None, "workspace world_id is required but is never written into native content")
    workspace_spec = value.get("workspace_spec")
    if workspace_spec is not None:
        _text(workspace_spec, "workspace_spec", 128)
    return {
        "rappid": identity,
        "world_id": world,
        "workspace_spec": workspace_spec,
        "identity_sha256": sha256(raw),
        "identity_bytes": raw,
    }


def workspace_identity(root: Path, explicit_world: str | None = None) -> dict:
    with _directory_fd(root) as descriptor:
        return _workspace_identity_at(descriptor, explicit_world)


def _write_file_at(parent: int, name: str, raw: bytes, mode: int = 0o600) -> None:
    require("/" not in name and name not in {"", ".", ".."}, "unsafe file entry name")
    descriptor = os.open(
        name,
        os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
        mode,
        dir_fd=parent,
    )
    try:
        os.fchmod(descriptor, mode)
        view = memoryview(raw)
        while view:
            written = os.write(descriptor, view)
            require(written > 0, f"short write refused: {name}")
            view = view[written:]
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _atomic_rename_backend():
    _require_secure_filesystem()
    library = ctypes.CDLL(None, use_errno=True)
    if sys.platform.startswith("linux"):
        function = getattr(library, "renameat2", None)
        require(function is not None, "atomic no-replace/exchange rename is unavailable")
        function.argtypes = [
            ctypes.c_int,
            ctypes.c_char_p,
            ctypes.c_int,
            ctypes.c_char_p,
            ctypes.c_uint,
        ]
        function.restype = ctypes.c_int
    elif sys.platform == "darwin":
        function = getattr(library, "renameatx_np", None)
        require(function is not None, "atomic no-replace/exchange rename is unavailable")
        function.argtypes = [
            ctypes.c_int,
            ctypes.c_char_p,
            ctypes.c_int,
            ctypes.c_char_p,
            ctypes.c_uint,
        ]
        function.restype = ctypes.c_int
    else:
        raise Refusal("atomic no-replace/exchange rename is unavailable on this platform")
    return function


def _rename_flags(
    source_parent: int,
    source: str,
    destination_parent: int,
    destination: str,
    flag: int,
) -> None:
    function = _atomic_rename_backend()
    result = function(
        source_parent,
        os.fsencode(source),
        destination_parent,
        os.fsencode(destination),
        flag,
    )
    if result != 0:
        code = ctypes.get_errno()
        if code == errno.EEXIST:
            raise FileExistsError(code, os.strerror(code), destination)
        if code == errno.ENOENT:
            raise FileNotFoundError(code, os.strerror(code), destination)
        raise OSError(code, os.strerror(code), destination)


def _rename_noreplace_at(
    source_parent: int,
    source: str,
    destination_parent: int,
    destination: str,
) -> None:
    _rename_flags(
        source_parent,
        source,
        destination_parent,
        destination,
        1 if sys.platform.startswith("linux") else 4,
    )


def _rename_exchange_at(
    source_parent: int,
    source: str,
    destination_parent: int,
    destination: str,
) -> None:
    _rename_flags(source_parent, source, destination_parent, destination, 2)


def _atomic_compare_swap_at(
    parent: int,
    name: str,
    expected: bytes,
    replacement: bytes,
) -> None:
    require(
        _read_regular_at(parent, name, private=True) == expected,
        "install pointer changed before compare-and-swap",
    )
    temporary = f".{name}.cas-{os.getpid()}-{os.urandom(8).hex()}"
    descriptor = os.open(
        temporary,
        os.O_RDWR | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
        0o600,
        dir_fd=parent,
    )
    exchanged = False
    created = None
    try:
        os.fchmod(descriptor, 0o600)
        view = memoryview(replacement)
        while view:
            written = os.write(descriptor, view)
            require(written > 0, "short install pointer staging write")
            view = view[written:]
        os.fsync(descriptor)
        created = os.fstat(descriptor)
        try:
            _rename_exchange_at(parent, temporary, parent, name)
            exchanged = True
        except FileNotFoundError as error:
            raise Refusal("install pointer disappeared during compare-and-swap") from error
        active = os.stat(name, dir_fd=parent, follow_symlinks=False)
        if not _same_object(created, active):
            _rename_exchange_at(parent, temporary, parent, name)
            exchanged = False
            raise Refusal("install pointer staging path changed during compare-and-swap")
        previous = _read_regular_at(parent, temporary, private=True)
        if previous != expected:
            require(
                _read_regular_at(parent, name, private=True) == replacement,
                "install pointer compare-and-swap entered an ambiguous raced state",
            )
            _rename_exchange_at(parent, temporary, parent, name)
            exchanged = False
            raise Refusal("install pointer changed during compare-and-swap")
        os.unlink(temporary, dir_fd=parent)
        exchanged = False
        os.fsync(parent)
    finally:
        if exchanged:
            _rename_exchange_at(parent, temporary, parent, name)
        os.close(descriptor)
        try:
            current = os.stat(temporary, dir_fd=parent, follow_symlinks=False)
        except FileNotFoundError:
            current = None
        if current is not None and created is not None and _same_object(created, current):
            os.unlink(temporary, dir_fd=parent)


def _remove_tree_at(parent: int, name: str, expected: os.stat_result) -> None:
    try:
        descriptor = os.open(
            name,
            os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
            dir_fd=parent,
        )
    except FileNotFoundError:
        return
    try:
        require(_same_object(expected, os.fstat(descriptor)), "temporary directory identity changed")
        for child in os.listdir(descriptor):
            info = os.stat(child, dir_fd=descriptor, follow_symlinks=False)
            if stat.S_ISDIR(info.st_mode):
                _remove_tree_at(descriptor, child, info)
            else:
                os.unlink(child, dir_fd=descriptor)
        os.fsync(descriptor)
    finally:
        os.close(descriptor)
    os.rmdir(name, dir_fd=parent)


def default_discovery(identity: dict, pin: str) -> dict:
    return {
        "schema": PROFILE_ID + "/discovery",
        "profile": PROFILE_ID,
        "installed_pin": pin,
        "workspace_rappid": identity["rappid"],
        "world_id": identity["world_id"],
        "organization_pointers": [],
        "hive_endpoints": [],
        "hive_vectors": [],
        "plugins": [],
        "skills": [],
        "static_apis": [],
        "network_default": "disabled",
        "discovery_only": True,
        "native_workspace_copied": False,
        "publication_authorized": False,
        "grants_authority": False,
    }


def _capability(entry: object, label: str) -> dict:
    require(isinstance(entry, dict), f"{label} entry is invalid")
    _exact(
        entry,
        {
            "id",
            "version",
            "locator",
            "sha256",
            "discovery_only",
            "activation_authorized",
            "execution_authorized",
            "grants_authority",
        },
        label,
    )
    _text(entry["id"], label + ".id", 128)
    _text(entry["version"], label + ".version", 64)
    _text(entry["locator"], label + ".locator", 1024)
    if entry["sha256"] is not None:
        _hash64(entry["sha256"], label + ".sha256")
    require(
        entry["discovery_only"] is True
        and entry["activation_authorized"] is False
        and entry["execution_authorized"] is False
        and entry["grants_authority"] is False,
        f"{label} entry attempts to grant authority",
    )
    return entry


def _sorted_unique(values: list, key, label: str) -> None:
    keys = [key(value) for value in values]
    require(keys == sorted(keys) and len(keys) == len(set(keys)), f"{label} must be unique and sorted")


def validate_discovery(value: dict, *, identity: dict | None = None, pin: str | None = None) -> dict:
    _exact(
        value,
        {
            "schema",
            "profile",
            "installed_pin",
            "workspace_rappid",
            "world_id",
            "organization_pointers",
            "hive_endpoints",
            "hive_vectors",
            "plugins",
            "skills",
            "static_apis",
            "network_default",
            "discovery_only",
            "native_workspace_copied",
            "publication_authorized",
            "grants_authority",
        },
        "discovery",
    )
    require(value["schema"] == PROFILE_ID + "/discovery" and value["profile"] == PROFILE_ID, "wrong discovery profile")
    discovered_pin = _hash40(value["installed_pin"], "discovery pin")
    _pin(discovered_pin, "discovery pin")
    _rappid(value["workspace_rappid"], "discovery workspace_rappid")
    _world(value["world_id"], "discovery world_id")
    if identity is not None:
        require(
            value["workspace_rappid"] == identity["rappid"]
            and value["world_id"] == identity["world_id"],
            "discovery belongs to another workspace or world",
        )
    if pin is not None:
        require(discovered_pin == pin, "discovery pin does not match its generation")
    organizations = value["organization_pointers"]
    require(isinstance(organizations, list) and len(organizations) <= 1024, "organization pointers are invalid")
    for item in organizations:
        require(isinstance(item, dict), "organization pointer is invalid")
        _exact(
            item,
            {
                "workspace_profile",
                "composite",
                "verification_status",
                "verification_receipt",
                "routing_only",
                "content_copied",
                "grants_authority",
            },
            "organization pointer",
        )
        require(item["workspace_profile"] == "rapp-workspace/1", "organization pointer is not Workspace/1")
        _address(item["composite"], "organization composite")
        require(
            item["verification_status"] in {"address-reference-only", "verified-local-receipt"},
            "organization verification status is invalid",
        )
        if item["verification_status"] == "verified-local-receipt":
            _address(item["verification_receipt"], "organization verification receipt")
        else:
            require(item["verification_receipt"] is None, "unverified organization pointer carries a receipt")
        require(
            item["routing_only"] is True
            and item["content_copied"] is False
            and item["grants_authority"] is False,
            "organization pointer attempts to copy content or grant authority",
        )
    _sorted_unique(organizations, lambda item: item["composite"]["hash"], "organization pointers")
    endpoints = value["hive_endpoints"]
    require(isinstance(endpoints, list) and len(endpoints) <= 256, "Hive endpoints are invalid")
    for item in endpoints:
        require(isinstance(item, dict), "Hive endpoint is invalid")
        _exact(
            item,
            {
                "id",
                "hive_rappid",
                "world_id",
                "transport",
                "locator_sha256",
                "verification_status",
                "verification_receipt",
                "publication_authorized",
                "grants_authority",
            },
            "Hive endpoint",
        )
        _text(item["id"], "Hive endpoint id", 128)
        _rappid(item["hive_rappid"], "Hive endpoint RAPPID")
        _world(item["world_id"], "Hive endpoint world")
        _text(item["transport"], "Hive endpoint transport", 64)
        _hash64(item["locator_sha256"], "Hive endpoint locator digest")
        require(item["verification_status"] in {"described-unverified", "verified"}, "Hive endpoint status is invalid")
        if item["verification_status"] == "verified":
            _address(item["verification_receipt"], "Hive endpoint verification receipt")
        else:
            require(item["verification_receipt"] is None, "unverified Hive endpoint carries a receipt")
        require(
            item["publication_authorized"] is False and item["grants_authority"] is False,
            "Hive endpoint receipt attempts to authorize publication",
        )
    _sorted_unique(endpoints, lambda item: item["id"], "Hive endpoints")
    vectors = value["hive_vectors"]
    require(isinstance(vectors, list) and len(vectors) <= 256, "Hive vectors are invalid")
    for item in vectors:
        require(isinstance(item, dict), "Hive vector is invalid")
        _exact(
            item,
            {
                "hive_rappid",
                "vector_sha256",
                "verification_status",
                "verification_receipt",
                "publication_authorized",
                "grants_authority",
            },
            "Hive vector",
        )
        _rappid(item["hive_rappid"], "Hive vector RAPPID")
        _hash64(item["vector_sha256"], "Hive vector digest")
        require(item["verification_status"] in {"described-unverified", "verified"}, "Hive vector status is invalid")
        _address(item["verification_receipt"], "Hive vector receipt")
        require(
            item["publication_authorized"] is False and item["grants_authority"] is False,
            "Hive vector receipt attempts to authorize publication",
        )
    _sorted_unique(vectors, lambda item: (item["hive_rappid"], item["vector_sha256"]), "Hive vectors")
    for field in ("plugins", "skills", "static_apis"):
        entries = value[field]
        require(isinstance(entries, list) and len(entries) <= 256, f"{field} entries are invalid")
        for item in entries:
            _capability(item, field)
        _sorted_unique(entries, lambda item: item["id"], field)
    require(
        value["network_default"] == "disabled"
        and value["discovery_only"] is True
        and value["native_workspace_copied"] is False
        and value["publication_authorized"] is False
        and value["grants_authority"] is False,
        "discovery attempts to enable effects or authority",
    )
    return value


def discovery_from_path(path: str | Path) -> dict:
    candidate = _absolute(Path(path))
    raw = _safe_regular(candidate)
    return strict_json(raw, str(candidate))


def validate_install(value: dict, identity: dict) -> dict:
    _exact(
        value,
        {
            "schema",
            "profile",
            "workspace_rappid",
            "world_id",
            "workspace_spec",
            "workspace_identity_sha256",
            "profile_sha256",
            "installed_pin",
            "current_pin",
            "current_generation_sha256",
            "discovery_sha256",
            "installed_utc",
            "updated_utc",
            "last_update_plan_digest",
            "sidecar_path",
            "mode",
            "network_default",
            "native_workspace_copied",
            "workspace_identity_preserved",
            "publication_authorized",
            "grants_authority",
        },
        "install state",
    )
    require(value["schema"] == PROFILE_ID + "/install" and value["profile"] == PROFILE_ID, "wrong install profile")
    require(
        value["workspace_rappid"] == identity["rappid"]
        and value["world_id"] == identity["world_id"]
        and value["workspace_spec"] == identity["workspace_spec"]
        and value["workspace_identity_sha256"] == identity["identity_sha256"],
        "install state does not preserve the native workspace identity",
    )
    _pin(value["installed_pin"], "installed pin")
    current_pin = _hash40(value["current_pin"], "current pin")
    _pin(current_pin, "current pin")
    require(
        value["profile_sha256"] == _pin_profile_sha256(current_pin),
        "install state profile checksum changed",
    )
    _hash64(value["current_generation_sha256"], "current generation digest")
    _hash64(value["discovery_sha256"], "current discovery digest")
    _utc(value["installed_utc"], "installed_utc")
    if value["updated_utc"] is not None:
        _utc(value["updated_utc"], "updated_utc")
    if value["last_update_plan_digest"] is not None:
        _hash64(value["last_update_plan_digest"], "last update digest")
    require(
        value["sidecar_path"] == SIDECAR_NAME
        and value["mode"] == "offline-first"
        and value["network_default"] == "disabled"
        and value["native_workspace_copied"] is False
        and value["workspace_identity_preserved"] is True
        and value["publication_authorized"] is False
        and value["grants_authority"] is False,
        "install state attempts to enable effects or authority",
    )
    return value


def validate_update(value: dict, identity: dict | None = None) -> dict:
    _exact(value, {"schema", "status", "plan_digest", "plan", "prepared_utc"}, "update")
    require(value["schema"] == PROFILE_ID + "/update", "wrong update profile")
    require(value["status"] in {"planned", "prepared"}, "update status is invalid")
    digest = _hash64(value["plan_digest"], "update plan digest")
    plan = value["plan"]
    require(isinstance(plan, dict), "update plan is invalid")
    _exact(
        plan,
        {
            "profile",
            "workspace_rappid",
            "world_id",
            "from_pin",
            "to_pin",
            "from_generation_sha256",
            "from_profile_sha256",
            "target_profile_sha256",
            "target_discovery_sha256",
            "operations",
            "network_access",
            "native_workspace_copy",
            "publication_authorized",
            "grants_authority",
        },
        "update plan",
    )
    require(plan["profile"] == PROFILE_ID, "wrong update plan profile")
    _rappid(plan["workspace_rappid"], "update workspace_rappid")
    _world(plan["world_id"], "update world_id")
    if identity is not None:
        require(
            plan["workspace_rappid"] == identity["rappid"]
            and plan["world_id"] == identity["world_id"],
            "update plan belongs to another workspace or world",
        )
    source = _pin(plan["from_pin"], "update from_pin")
    target = _pin(plan["to_pin"], "update to_pin")
    require(target["sequence"] > source["sequence"], "update is not a strict forward transition")
    _hash64(plan["from_generation_sha256"], "update source generation")
    require(
        plan["from_profile_sha256"] == _pin_profile_sha256(plan["from_pin"]),
        "update source profile hash is unknown or changed",
    )
    require(
        plan["target_profile_sha256"] == _pin_profile_sha256(plan["to_pin"]),
        "update targets another profile byte set",
    )
    _hash64(plan["target_discovery_sha256"], "update target discovery")
    require(
        plan["operations"]
        == ["write-complete-generation", "atomically-replace-install-pointer"]
        and plan["network_access"] is False
        and plan["native_workspace_copy"] is False
        and plan["publication_authorized"] is False
        and plan["grants_authority"] is False,
        "update plan attempts an unsupported effect",
    )
    require(digest == sha256(canonical_bytes(plan)), "update plan digest mismatch")
    if value["status"] == "planned":
        require(value["prepared_utc"] is None, "planned update already claims preparation")
    else:
        _utc(value["prepared_utc"], "prepared_utc")
    return value


def _generation_files(
    pin: str,
    discovery: dict,
    update: dict | None = None,
) -> dict[str, bytes]:
    files = {
        "profile.json": _pin_profile_raw(pin),
        "discovery.json": canonical_bytes(discovery),
    }
    if update is not None:
        files["update.json"] = canonical_bytes(update)
    return files


def generation_digest(files: dict[str, bytes]) -> str:
    manifest = {
        "schema": PROFILE_ID + "/generation",
        "files": [
            {"path": name, "sha256": sha256(raw), "bytes": len(raw)}
            for name, raw in sorted(files.items())
        ],
    }
    return sha256(canonical_bytes(manifest))


def _write_generation_at(parent: int, name: str, files: dict[str, bytes]) -> os.stat_result:
    os.mkdir(name, mode=0o700, dir_fd=parent)
    created = os.stat(name, dir_fd=parent, follow_symlinks=False)
    try:
        with _open_directory_at(parent, name, private=True) as descriptor:
            info = os.fstat(descriptor)
            require(_same_object(created, info), "generation temporary path changed")
            for filename, raw in sorted(files.items()):
                _write_file_at(descriptor, filename, raw)
            os.fsync(descriptor)
            return info
    except BaseException:
        try:
            current = os.stat(name, dir_fd=parent, follow_symlinks=False)
            require(
                _same_object(created, current),
                "generation temporary path was replaced",
            )
            if stat.S_ISDIR(current.st_mode):
                _remove_tree_at(parent, name, created)
        except FileNotFoundError:
            pass
        raise


def _generation_at(parent: int, name: str, pin: str, identity: dict) -> dict:
    with _open_directory_at(parent, name, private=True) as descriptor:
        info = os.fstat(descriptor)
        actual = set(os.listdir(descriptor))
        for entry in actual:
            entry_info = os.stat(entry, dir_fd=descriptor, follow_symlinks=False)
            require(
                stat.S_ISREG(entry_info.st_mode),
                f"unsafe generation entry refused: {entry}",
            )
        require(
            actual
            in (
                {"profile.json", "discovery.json"},
                {"profile.json", "discovery.json", "update.json"},
            ),
            f"generation {pin} is partial or contains conflicts",
        )
        profile_raw = _read_regular_at(descriptor, "profile.json", private=True)
        expected_profile = _pin_profile_raw(pin)
        require(
            profile_raw == expected_profile
            and sha256(profile_raw) == _pin_profile_sha256(pin),
            f"generation {pin} profile bytes changed",
        )
        discovery_raw = _read_regular_at(descriptor, "discovery.json", private=True)
        discovery = strict_json(discovery_raw, f"generation {pin} discovery")
        require(
            discovery_raw == canonical_bytes(discovery),
            f"generation {pin} discovery is not canonical",
        )
        validate_discovery(discovery, identity=identity, pin=pin)
        update = None
        if "update.json" in actual:
            update_raw = _read_regular_at(descriptor, "update.json", private=True)
            update = strict_json(update_raw, f"generation {pin} update")
            require(
                update_raw == canonical_bytes(update),
                f"generation {pin} update is not canonical",
            )
            validate_update(update, identity)
            require(
                update["status"] == "prepared"
                and update["plan"]["to_pin"] == pin,
                "generation update target mismatch",
            )
            require(
                update["plan"]["target_profile_sha256"] == sha256(profile_raw)
                and update["plan"]["target_discovery_sha256"] == sha256(discovery_raw),
                "generation update does not bind its profile and discovery bytes",
            )
        files = _generation_files(pin, discovery, update)
        return {
            "pin": pin,
            "profile_sha256": sha256(profile_raw),
            "discovery": discovery,
            "discovery_sha256": sha256(discovery_raw),
            "update": update,
            "digest": generation_digest(files),
            "stat": info,
        }


def _install_state(identity: dict, pin: str, discovery: dict, installed_utc: str) -> dict:
    files = _generation_files(pin, discovery)
    return {
        "schema": PROFILE_ID + "/install",
        "profile": PROFILE_ID,
        "workspace_rappid": identity["rappid"],
        "world_id": identity["world_id"],
        "workspace_spec": identity["workspace_spec"],
        "workspace_identity_sha256": identity["identity_sha256"],
        "profile_sha256": _pin_profile_sha256(pin),
        "installed_pin": pin,
        "current_pin": pin,
        "current_generation_sha256": generation_digest(files),
        "discovery_sha256": sha256(files["discovery.json"]),
        "installed_utc": installed_utc,
        "updated_utc": None,
        "last_update_plan_digest": None,
        "sidecar_path": SIDECAR_NAME,
        "mode": "offline-first",
        "network_default": "disabled",
        "native_workspace_copied": False,
        "workspace_identity_preserved": True,
        "publication_authorized": False,
        "grants_authority": False,
    }


def _case_insensitive_at(root: int) -> bool:
    if os.name == "nt":
        return True
    exact = os.stat("rappid.json", dir_fd=root, follow_symlinks=False)
    try:
        alias = os.stat("RAPPID.JSON", dir_fd=root, follow_symlinks=False)
    except FileNotFoundError:
        return False
    return _same_object(exact, alias)


def validate_sidecar(root: Path, explicit_world: str | None = None) -> dict:
    with _directory_fd(root) as root_descriptor:
        root_info = os.fstat(root_descriptor)
        root_names = set(os.listdir(root_descriptor))
        if _case_insensitive_at(root_descriptor):
            aliases = sorted(
                name
                for name in root_names
                if name.casefold() == SIDECAR_NAME.casefold()
            )
            require(
                aliases in ([], [SIDECAR_NAME]),
                "case-fold alias for .rapp-work is reserved",
            )
        require(SIDECAR_NAME in root_names, "RAPP Work SDK sidecar is not installed")
        with _open_directory_at(
            root_descriptor,
            SIDECAR_NAME,
            private=True,
        ) as sidecar_descriptor:
            sidecar_info = os.fstat(sidecar_descriptor)
            root_entries = set(os.listdir(sidecar_descriptor))
            require(
                root_entries == {"install.json", "generations"},
                "sidecar is partial or contains unmanaged entries",
            )
            install_raw = _read_regular_at(
                sidecar_descriptor,
                "install.json",
                private=True,
            )
            install = strict_json(install_raw, "install.json")
            require(
                install_raw == canonical_bytes(install),
                "install.json is not canonical",
            )
            recorded_world = _world(
                install.get("world_id"),
                "installed sidecar world_id",
            )
            if explicit_world is not None:
                _world(explicit_world, "requested world_id")
                require(
                    explicit_world == recorded_world,
                    "requested world_id conflicts with the installed sidecar world",
                )
            identity = _workspace_identity_at(
                root_descriptor,
                explicit_world or recorded_world,
            )
            validate_install(install, identity)
            with _open_directory_at(
                sidecar_descriptor,
                "generations",
                private=True,
            ) as generations_descriptor:
                generations_info = os.fstat(generations_descriptor)
                generation_names = sorted(os.listdir(generations_descriptor))
                require(generation_names, "sidecar has no generations")
                generations = {}
                for name in generation_names:
                    _pin(name, "generation pin")
                    require(name not in generations, "duplicate sidecar generation")
                    generations[name] = _generation_at(
                        generations_descriptor,
                        name,
                        name,
                        identity,
                    )
    installed_pin = install["installed_pin"]
    current_pin = install["current_pin"]
    require(installed_pin in generations and current_pin in generations, "install pointer names a missing generation")
    require(generations[installed_pin]["update"] is None, "initial generation cannot be an update")
    require(
        PINS[current_pin]["sequence"] >= PINS[installed_pin]["sequence"],
        "install history moved backwards",
    )
    chain = set()
    cursor = current_pin
    while True:
        require(cursor not in chain, "sidecar update history contains a cycle")
        chain.add(cursor)
        if cursor == installed_pin:
            break
        update = generations[cursor]["update"]
        require(update is not None, "updated generation lacks an update receipt")
        prior = update["plan"]["from_pin"]
        require(prior in generations, "update history names a missing source generation")
        require(
            update["plan"]["from_generation_sha256"] == generations[prior]["digest"],
            "update history source generation digest changed",
        )
        require(
            update["plan"]["from_profile_sha256"]
            == generations[prior]["profile_sha256"],
            "update history source profile digest changed",
        )
        cursor = prior
    extras = set(generations) - chain
    require(len(extras) <= 1, "sidecar contains a forked or ambiguous generation history")
    pending = []
    if extras:
        extra = generations[next(iter(extras))]
        update = extra["update"]
        require(
            update is not None
            and update["plan"]["from_pin"] == current_pin
            and update["plan"]["from_generation_sha256"] == generations[current_pin]["digest"],
            "sidecar contains an unrelated inactive generation",
        )
        pending.append(
            {
                "from_pin": current_pin,
                "to_pin": extra["pin"],
                "plan_digest": update["plan_digest"],
            }
        )
    current = generations[current_pin]
    require(
        install["current_generation_sha256"] == current["digest"]
        and install["discovery_sha256"] == current["discovery_sha256"],
        "install pointer digest does not match the active generation",
    )
    if current_pin == installed_pin:
        require(
            install["updated_utc"] is None and install["last_update_plan_digest"] is None,
            "initial install falsely claims an update",
        )
    else:
        current_update = current["update"]
        require(
            current_update is not None
            and install["updated_utc"] == current_update["prepared_utc"]
            and install["last_update_plan_digest"] == current_update["plan_digest"],
            "install pointer does not bind its active update receipt",
        )
    return {
        "identity": identity,
        "install": install,
        "install_raw": install_raw,
        "generations": generations,
        "pending_updates": pending,
        "root_stat": root_info,
        "sidecar_stat": sidecar_info,
        "generations_stat": generations_info,
    }


def _refuse_partial_install_roots(root: int) -> None:
    leftovers = [
        name
        for name in os.listdir(root)
        if name.casefold().startswith(f".{SIDECAR_NAME.lstrip('.')}.tmp-")
    ]
    require(not leftovers, f"partial RAPP Work SDK install state refused: {sorted(leftovers)}")


def _install(
    workspace: str | Path,
    *,
    world_id: str | None,
    discovery: dict | None,
    now: str | None,
) -> dict:
    root = workspace_root(workspace)
    pin = CURRENT_PIN
    pin_record = _pin(pin, "install pin")
    require(
        pin_record["fresh_install"] is True,
        "current profile pin is not available for fresh installation",
    )
    with _directory_fd(root) as root_descriptor:
        root_info = os.fstat(root_descriptor)
        identity = _workspace_identity_at(root_descriptor, world_id)
        _refuse_partial_install_roots(root_descriptor)
        names = set(os.listdir(root_descriptor))
        if _case_insensitive_at(root_descriptor):
            aliases = sorted(
                name for name in names if name.casefold() == SIDECAR_NAME.casefold()
            )
            require(
                aliases in ([], [SIDECAR_NAME]),
                "case-fold alias for .rapp-work is reserved",
            )
        sidecar_present = SIDECAR_NAME in names
    requested = copy.deepcopy(discovery) if discovery is not None else default_discovery(identity, pin)
    validate_discovery(requested, identity=identity, pin=pin)
    sidecar = root / SIDECAR_NAME
    if sidecar_present:
        state = validate_sidecar(root, world_id)
        require(state["install"]["current_pin"] == pin, "different pin requires an explicit update")
        if discovery is not None:
            require(
                canonical_bytes(requested)
                == canonical_bytes(state["generations"][pin]["discovery"]),
                "same-pin install conflicts with existing discovery",
            )
        return {
            "status": "already-installed",
            "workspace": str(root),
            "workspace_rappid": identity["rappid"],
            "world_id": identity["world_id"],
            "pin": pin,
            "generation_sha256": state["install"]["current_generation_sha256"],
            "sidecar": str(sidecar),
            "network_used": False,
            "native_workspace_copied": False,
            "workspace_identity_preserved": True,
        }
    stamp = now or utc_now()
    _utc(stamp, "install time")
    _atomic_rename_backend()
    temporary = f".{SIDECAR_NAME.lstrip('.')}.tmp-{os.getpid()}-{os.urandom(8).hex()}"
    with _directory_fd(root) as root_descriptor:
        require(
            _same_object(root_info, os.fstat(root_descriptor)),
            "workspace root changed during install",
        )
        _refuse_partial_install_roots(root_descriptor)
        require(
            SIDECAR_NAME not in os.listdir(root_descriptor),
            "RAPP Work SDK sidecar appeared during install",
        )
        require(
            _workspace_identity_at(root_descriptor, world_id)["identity_bytes"]
            == identity["identity_bytes"],
            "native workspace identity changed during install",
        )
        os.mkdir(temporary, mode=0o700, dir_fd=root_descriptor)
        temporary_info = os.stat(
            temporary,
            dir_fd=root_descriptor,
            follow_symlinks=False,
        )
        try:
            with _open_directory_at(
                root_descriptor,
                temporary,
                private=True,
            ) as temporary_descriptor:
                os.mkdir("generations", mode=0o700, dir_fd=temporary_descriptor)
                with _open_directory_at(
                    temporary_descriptor,
                    "generations",
                    private=True,
                ) as generations_descriptor:
                    _write_generation_at(
                        generations_descriptor,
                        pin,
                        _generation_files(pin, requested),
                    )
                    os.fsync(generations_descriptor)
                install = _install_state(identity, pin, requested, stamp)
                _write_file_at(
                    temporary_descriptor,
                    "install.json",
                    canonical_bytes(install),
                )
                os.fsync(temporary_descriptor)
            require(
                _workspace_identity_at(root_descriptor, world_id)["identity_bytes"]
                == identity["identity_bytes"],
                "native workspace identity changed during install",
            )
            try:
                _rename_noreplace_at(
                    root_descriptor,
                    temporary,
                    root_descriptor,
                    SIDECAR_NAME,
                )
            except FileExistsError as error:
                raise Refusal(
                    "RAPP Work SDK sidecar destination raced activation; nothing was overwritten"
                ) from error
            active = os.stat(
                SIDECAR_NAME,
                dir_fd=root_descriptor,
                follow_symlinks=False,
            )
            if not _same_object(temporary_info, active):
                _rename_noreplace_at(
                    root_descriptor,
                    SIDECAR_NAME,
                    root_descriptor,
                    temporary,
                )
                raise Refusal("install temporary path changed during activation")
            os.fsync(root_descriptor)
        finally:
            try:
                current = os.stat(
                    temporary,
                    dir_fd=root_descriptor,
                    follow_symlinks=False,
                )
            except FileNotFoundError:
                current = None
            if current is not None:
                require(
                    _same_object(temporary_info, current),
                    "install temporary path was replaced during activation",
                )
                _remove_tree_at(root_descriptor, temporary, temporary_info)
    state = validate_sidecar(root, world_id)
    return {
        "status": "installed",
        "workspace": str(root),
        "workspace_rappid": identity["rappid"],
        "world_id": identity["world_id"],
        "pin": pin,
        "generation_sha256": state["install"]["current_generation_sha256"],
        "sidecar": str(sidecar),
        "network_used": False,
        "native_workspace_copied": False,
        "workspace_identity_preserved": True,
    }


def install_workspace(
    workspace: str | Path,
    *,
    world_id: str | None = None,
    discovery: dict | None = None,
    now: str | None = None,
) -> dict:
    """Install the current exact profile pin. Existing other pins require update."""
    return _install(
        workspace,
        world_id=world_id,
        discovery=discovery,
        now=now,
    )


def plan_update(
    workspace: str | Path,
    *,
    from_pin: str,
    to_pin: str,
    plan_discovery: dict | None = None,
    world_id: str | None = None,
) -> dict:
    root = workspace_root(workspace)
    state = validate_sidecar(root, world_id)
    source = _pin(from_pin, "from_pin")
    target = _pin(to_pin, "to_pin")
    require(from_pin == state["install"]["current_pin"], "from_pin is not the active pin")
    require(target["sequence"] > source["sequence"], "downgrade or no-op update refused")
    current_discovery = state["generations"][from_pin]["discovery"]
    target_discovery = (
        copy.deepcopy(plan_discovery)
        if plan_discovery is not None
        else {**copy.deepcopy(current_discovery), "installed_pin": to_pin}
    )
    validate_discovery(target_discovery, identity=state["identity"], pin=to_pin)
    plan = {
        "profile": PROFILE_ID,
        "workspace_rappid": state["identity"]["rappid"],
        "world_id": state["identity"]["world_id"],
        "from_pin": from_pin,
        "to_pin": to_pin,
        "from_generation_sha256": state["generations"][from_pin]["digest"],
        "from_profile_sha256": state["generations"][from_pin][
            "profile_sha256"
        ],
        "target_profile_sha256": _pin_profile_sha256(to_pin),
        "target_discovery_sha256": sha256(canonical_bytes(target_discovery)),
        "operations": [
            "write-complete-generation",
            "atomically-replace-install-pointer",
        ],
        "network_access": False,
        "native_workspace_copy": False,
        "publication_authorized": False,
        "grants_authority": False,
    }
    result = {
        "schema": PROFILE_ID + "/update",
        "status": "planned",
        "plan_digest": sha256(canonical_bytes(plan)),
        "plan": plan,
        "prepared_utc": None,
    }
    validate_update(result, state["identity"])
    if state["pending_updates"]:
        pending = state["pending_updates"][0]
        require(
            pending["from_pin"] == from_pin
            and pending["to_pin"] == to_pin
            and pending["plan_digest"] == result["plan_digest"],
            "a different complete inactive update already exists",
        )
    return result


def update_workspace(
    workspace: str | Path,
    *,
    from_pin: str,
    to_pin: str,
    plan_digest: str,
    plan_discovery: dict | None = None,
    world_id: str | None = None,
    now: str | None = None,
) -> dict:
    _hash64(plan_digest, "supplied plan digest")
    root = workspace_root(workspace)
    planned = plan_update(
        root,
        from_pin=from_pin,
        to_pin=to_pin,
        plan_discovery=plan_discovery,
        world_id=world_id,
    )
    require(planned["plan_digest"] == plan_digest, "supplied plan digest does not match the exact update plan")
    state = validate_sidecar(root, world_id)
    identity = state["identity"]
    if state["pending_updates"]:
        existing_target = state["generations"][to_pin]
        prepared = existing_target["update"]
        discovery = existing_target["discovery"]
        require(
            prepared is not None and prepared["plan_digest"] == plan_digest,
            "inactive target generation does not match the exact update plan",
        )
        if plan_discovery is not None:
            require(discovery == plan_discovery, "inactive target discovery conflicts with the requested plan")
        stamp = prepared["prepared_utc"]
    else:
        discovery = (
            copy.deepcopy(plan_discovery)
            if plan_discovery is not None
            else {**copy.deepcopy(state["generations"][from_pin]["discovery"]), "installed_pin": to_pin}
        )
        stamp = now or utc_now()
        _utc(stamp, "update time")
        prepared = {
            **planned,
            "status": "prepared",
            "prepared_utc": stamp,
        }
        validate_update(prepared, identity)
    files = _generation_files(to_pin, discovery, prepared)
    expected_generation_digest = generation_digest(files)
    _atomic_rename_backend()
    with _directory_fd(root) as root_descriptor:
        require(
            _same_object(state["root_stat"], os.fstat(root_descriptor)),
            "workspace root changed during update",
        )
        require(
            _workspace_identity_at(root_descriptor, identity["world_id"])[
                "identity_bytes"
            ]
            == identity["identity_bytes"],
            "native workspace identity changed during update",
        )
        with _open_directory_at(
            root_descriptor,
            SIDECAR_NAME,
            private=True,
        ) as sidecar_descriptor:
            require(
                _same_object(state["sidecar_stat"], os.fstat(sidecar_descriptor)),
                "RAPP Work SDK sidecar changed during update",
            )
            with _open_directory_at(
                sidecar_descriptor,
                "generations",
                private=True,
            ) as generations_descriptor:
                require(
                    _same_object(
                        state["generations_stat"],
                        os.fstat(generations_descriptor),
                    ),
                    "RAPP Work SDK generation store changed during update",
                )
                generation_names = set(os.listdir(generations_descriptor))
                expected_existing = to_pin in state["generations"]
                if to_pin in generation_names:
                    require(
                        expected_existing,
                        "target generation destination raced activation; nothing was overwritten",
                    )
                    existing = _generation_at(
                        generations_descriptor,
                        to_pin,
                        to_pin,
                        identity,
                    )
                    require(
                        existing["digest"] == expected_generation_digest
                        and existing["update"] == prepared
                        and existing["discovery"] == discovery,
                        "existing target generation conflicts with the exact update plan",
                    )
                else:
                    require(
                        not expected_existing,
                        "verified target generation disappeared before activation",
                    )
                    temporary = (
                        f".tmp-{to_pin}-{os.getpid()}-{os.urandom(8).hex()}"
                    )
                    temporary_info = _write_generation_at(
                        generations_descriptor,
                        temporary,
                        files,
                    )
                    try:
                        built = _generation_at(
                            generations_descriptor,
                            temporary,
                            to_pin,
                            identity,
                        )
                        require(
                            built["digest"] == expected_generation_digest,
                            "prepared target generation digest mismatch",
                        )
                        try:
                            _rename_noreplace_at(
                                generations_descriptor,
                                temporary,
                                generations_descriptor,
                                to_pin,
                            )
                        except FileExistsError as error:
                            raise Refusal(
                                "target generation destination raced activation; nothing was overwritten"
                            ) from error
                        active = os.stat(
                            to_pin,
                            dir_fd=generations_descriptor,
                            follow_symlinks=False,
                        )
                        if not _same_object(temporary_info, active):
                            _rename_noreplace_at(
                                generations_descriptor,
                                to_pin,
                                generations_descriptor,
                                temporary,
                            )
                            raise Refusal(
                                "target generation temporary path changed during activation"
                            )
                        os.fsync(generations_descriptor)
                    finally:
                        try:
                            current = os.stat(
                                temporary,
                                dir_fd=generations_descriptor,
                                follow_symlinks=False,
                            )
                        except FileNotFoundError:
                            current = None
                        if current is not None:
                            require(
                                _same_object(temporary_info, current),
                                "target generation temporary path was replaced",
                            )
                            _remove_tree_at(
                                generations_descriptor,
                                temporary,
                                temporary_info,
                            )
                install = {
                    **state["install"],
                    "profile_sha256": _pin_profile_sha256(to_pin),
                    "current_pin": to_pin,
                    "current_generation_sha256": expected_generation_digest,
                    "discovery_sha256": sha256(files["discovery.json"]),
                    "updated_utc": stamp,
                    "last_update_plan_digest": plan_digest,
                }
                validate_install(install, identity)
                require(
                    _workspace_identity_at(
                        root_descriptor,
                        identity["world_id"],
                    )["identity_bytes"]
                    == identity["identity_bytes"],
                    "native workspace identity changed during update",
                )
                _atomic_compare_swap_at(
                    sidecar_descriptor,
                    "install.json",
                    state["install_raw"],
                    canonical_bytes(install),
                )
    verified = validate_sidecar(root, world_id)
    return {
        "status": "updated",
        "workspace": str(root),
        "workspace_rappid": identity["rappid"],
        "world_id": identity["world_id"],
        "from_pin": from_pin,
        "to_pin": to_pin,
        "plan_digest": plan_digest,
        "generation_sha256": verified["install"]["current_generation_sha256"],
        "network_used": False,
        "native_workspace_copied": False,
        "workspace_identity_preserved": True,
        "publication_authorized": False,
    }


def verify_workspace(workspace: str | Path, *, world_id: str | None = None) -> dict:
    root = workspace_root(workspace)
    state = validate_sidecar(root, world_id)
    return {
        "status": "verified",
        "workspace": str(root),
        "workspace_rappid": state["identity"]["rappid"],
        "world_id": state["identity"]["world_id"],
        "installed_pin": state["install"]["installed_pin"],
        "current_pin": state["install"]["current_pin"],
        "generation_sha256": state["install"]["current_generation_sha256"],
        "pending_updates": state["pending_updates"],
        "network_default": "disabled",
        "native_workspace_copied": False,
        "publication_authorized": False,
        "grants_authority": False,
    }


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description=__doc__)
    commands = root.add_subparsers(dest="command", required=True)
    install = commands.add_parser("install")
    install.add_argument("--workspace", required=True)
    install.add_argument("--world-id")
    install.add_argument("--discovery", type=Path)
    verify = commands.add_parser("verify")
    verify.add_argument("--workspace", required=True)
    verify.add_argument("--world-id")
    for name in ("plan-update", "update"):
        command = commands.add_parser(name)
        command.add_argument("--workspace", required=True)
        command.add_argument("--world-id")
        command.add_argument("--from-pin", required=True)
        command.add_argument("--to-pin", required=True)
        command.add_argument("--discovery", type=Path)
        if name == "update":
            command.add_argument("--plan-digest", required=True)
    commands.add_parser("profile")
    return root


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    if args.command == "profile":
        result = {
            "status": "verified-profile",
            "profile": PROFILE_ID,
            "profile_sha256": PROFILE_SHA256,
            "current_pin": CURRENT_PIN,
            "parent": PARENT_PIN,
            "network_default": "disabled",
        }
    elif args.command == "install":
        discovery = discovery_from_path(args.discovery) if args.discovery else None
        result = install_workspace(
            args.workspace,
            world_id=args.world_id,
            discovery=discovery,
        )
    elif args.command == "verify":
        result = verify_workspace(args.workspace, world_id=args.world_id)
    elif args.command == "plan-update":
        discovery = discovery_from_path(args.discovery) if args.discovery else None
        result = plan_update(
            args.workspace,
            from_pin=args.from_pin,
            to_pin=args.to_pin,
            plan_discovery=discovery,
            world_id=args.world_id,
        )
    else:
        discovery = discovery_from_path(args.discovery) if args.discovery else None
        result = update_workspace(
            args.workspace,
            from_pin=args.from_pin,
            to_pin=args.to_pin,
            plan_digest=args.plan_digest,
            plan_discovery=discovery,
            world_id=args.world_id,
        )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, Refusal, ValueError) as error:
        print(json.dumps({"status": "refused", "error": str(error)}, sort_keys=True), file=sys.stderr)
        raise SystemExit(1)
