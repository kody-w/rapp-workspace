#!/usr/bin/env python3
"""Checksum-locked skill entry for the RAPP Work SDK/1 scaffold."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path, PurePosixPath
import sys
import types


ROOT = Path(__file__).resolve().parents[1]


def _verified_lock() -> tuple[dict, dict[str, bytes]]:
    path = ROOT / "rapp" / "agent.lock.json"
    if path.is_symlink() or not path.is_file():
        raise ValueError("rapp-work-sdk skill lock is missing or unsafe")
    try:
        lock = json.loads(path.read_bytes().decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ValueError("rapp-work-sdk skill lock is invalid") from error
    if not isinstance(lock, dict) or set(lock) != {
        "schema",
        "name",
        "version",
        "protocol",
        "files",
    }:
        raise ValueError("rapp-work-sdk skill lock is invalid")
    protocol = lock.get("protocol")
    entries = lock.get("files", [])
    if not isinstance(entries, list) or not all(isinstance(entry, dict) for entry in entries):
        raise ValueError("rapp-work-sdk skill lock is invalid")
    paths = [entry.get("path") for entry in entries]
    if (
        lock.get("schema") != "rapp-skill-lock/1"
        or lock.get("name") != "rapp-work-sdk"
        or lock.get("version") != "1.0.0"
        or not isinstance(protocol, dict)
        or set(protocol)
        != {
            "name",
            "profile_sha256",
            "manifest_sha256",
            "rapp_work_repository",
            "rapp_work_commit",
            "rapp_work_path",
            "rapp_work_spec_sha256",
            "rapp_work_spec_bytes",
        }
        or protocol.get("name") != "rapp-work-sdk/1"
        or not isinstance(protocol.get("profile_sha256"), str)
        or not isinstance(protocol.get("manifest_sha256"), str)
        or protocol.get("rapp_work_repository") != "https://github.com/kody-w/rapp-1"
        or not isinstance(protocol.get("rapp_work_commit"), str)
        or protocol.get("rapp_work_path") != "protocols/rapp-work/1/SPEC.md"
        or not isinstance(protocol.get("rapp_work_spec_sha256"), str)
        or type(protocol.get("rapp_work_spec_bytes")) is not int
        or not all(isinstance(relative, str) for relative in paths)
        or paths != sorted(paths)
        or len(paths) != len(set(paths))
    ):
        raise ValueError("rapp-work-sdk skill lock is invalid")
    captured = {}
    for entry in entries:
        if set(entry) != {"path", "sha256"} or not isinstance(entry["sha256"], str):
            raise ValueError("rapp-work-sdk skill lock entry is invalid")
        relative = entry["path"]
        if not isinstance(relative, str):
            raise ValueError("rapp-work-sdk skill lock path is unsafe")
        candidate = PurePosixPath(relative)
        if (
            not relative
            or "\\" in relative
            or candidate.is_absolute()
            or any(part in {"", ".", ".."} for part in candidate.parts)
        ):
            raise ValueError("rapp-work-sdk skill lock path is unsafe")
        target = ROOT.joinpath(*candidate.parts)
        if target.is_symlink() or not target.is_file():
            raise ValueError("rapp-work-sdk skill file is missing or unsafe: " + entry["path"])
        raw = target.read_bytes()
        if hashlib.sha256(raw).hexdigest() != entry["sha256"]:
            raise ValueError("rapp-work-sdk skill checksum mismatch: " + entry["path"])
        captured[relative] = raw
    actual = sorted(
        candidate.relative_to(ROOT).as_posix()
        for candidate in ROOT.rglob("*")
        if candidate.is_file()
        and "rapp/agent.lock.json"
        != candidate.relative_to(ROOT).as_posix()
        and "__pycache__" not in candidate.parts
        and candidate.suffix != ".pyc"
    )
    if actual != paths:
        raise ValueError("rapp-work-sdk skill lock does not cover the complete skill")
    profile_path = "vendor/rapp-work-sdk/1/profile.json"
    manifest_path = "vendor/rapp-work-sdk/1/manifest.json"
    profile_raw = captured.get(profile_path)
    manifest_raw = captured.get(manifest_path)
    if (
        profile_raw is None
        or manifest_raw is None
        or len(protocol["profile_sha256"]) != 64
        or len(protocol["manifest_sha256"]) != 64
        or len(protocol["rapp_work_commit"]) != 40
        or len(protocol["rapp_work_spec_sha256"]) != 64
        or protocol["rapp_work_spec_bytes"] <= 0
        or hashlib.sha256(profile_raw).hexdigest() != protocol["profile_sha256"]
        or hashlib.sha256(manifest_raw).hexdigest() != protocol["manifest_sha256"]
    ):
        raise ValueError("rapp-work-sdk skill protocol lock metadata is invalid")
    try:
        profile = json.loads(profile_raw.decode("utf-8"))
        manifest = json.loads(manifest_raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ValueError("rapp-work-sdk skill protocol bytes are invalid") from error
    if (
        not isinstance(profile, dict)
        or not isinstance(manifest, dict)
        or profile.get("profile") != "rapp-work-sdk/1"
        or profile.get("current_pin") != protocol["rapp_work_commit"]
        or profile.get("parent", {}).get("repository")
        != protocol["rapp_work_repository"]
        or profile.get("parent", {}).get("path") != protocol["rapp_work_path"]
        or profile.get("parent", {}).get("spec_sha256")
        != protocol["rapp_work_spec_sha256"]
        or manifest.get("profile") != "rapp-work-sdk/1"
    ):
        raise ValueError("rapp-work-sdk skill protocol lock binding is invalid")
    return (
        {
            "status": "verified-skill-lock",
            "name": lock["name"],
            "version": lock["version"],
            "files": len(entries),
        },
        captured,
    )


def verify_lock() -> dict:
    result, _ = _verified_lock()
    return result


def _implementation_path(captured: dict[str, bytes]) -> tuple[Path, bytes]:
    repository = ROOT.parents[2]
    canonical = repository / "protocols" / "rapp-work-sdk" / "1" / "reference" / "scaffold.py"
    vendored = ROOT / "vendor" / "rapp-work-sdk" / "1" / "reference" / "scaffold.py"
    relative = "vendor/rapp-work-sdk/1/reference/scaffold.py"
    source = captured.get(relative)
    if source is None:
        raise ValueError("pinned vendored RAPP Work SDK implementation is unavailable")
    if canonical.exists() or canonical.is_symlink():
        if canonical.is_symlink() or not canonical.is_file():
            raise ValueError("canonical RAPP Work SDK implementation is unsafe")
        if hashlib.sha256(canonical.read_bytes()).digest() != hashlib.sha256(source).digest():
            raise ValueError("canonical and vendored RAPP Work SDK implementations differ")
    return vendored, source


def _load():
    _, captured = _verified_lock()
    path, source = _implementation_path(captured)
    prefix = "vendor/rapp-work-sdk/1/"
    profile_files = {
        relative[len(prefix):]: raw
        for relative, raw in captured.items()
        if relative.startswith(prefix)
    }
    module = types.ModuleType("rapp_work_sdk_scaffold")
    module.__file__ = str(path)
    module.__dict__["_RAPP_WORK_SDK_VERIFIED_FILES"] = profile_files
    code = compile(source, str(path), "exec", dont_inherit=True)
    exec(code, module.__dict__)
    return module


_IMPLEMENTATION = None


def load_verified():
    global _IMPLEMENTATION
    if _IMPLEMENTATION is None:
        _IMPLEMENTATION = _load()
    return _IMPLEMENTATION


def install_workspace(*args, **kwargs):
    return load_verified().install_workspace(*args, **kwargs)


def verify_workspace(*args, **kwargs):
    return load_verified().verify_workspace(*args, **kwargs)


def plan_update(*args, **kwargs):
    return load_verified().plan_update(*args, **kwargs)


def update_workspace(*args, **kwargs):
    return load_verified().update_workspace(*args, **kwargs)


def discovery_from_path(*args, **kwargs):
    return load_verified().discovery_from_path(*args, **kwargs)


def main(argv: list[str] | None = None) -> int:
    arguments = list(sys.argv[1:] if argv is None else argv)
    if arguments == ["--preflight"]:
        print(json.dumps(verify_lock(), indent=2, sort_keys=True))
        return 0
    return load_verified().main(arguments)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError) as error:
        print(json.dumps({"status": "refused", "error": str(error)}, sort_keys=True), file=sys.stderr)
        raise SystemExit(1)
