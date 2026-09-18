#!/usr/bin/env python3
"""Generate and verify repository-native checksum locks."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re


REPO = Path(__file__).resolve().parents[1]
WORK_SDK = REPO / ".github" / "skills" / "rapp-work-sdk"
PRIVATE_HIVE = REPO / ".github" / "skills" / "rapp-private-hive"
PROTOCOL = REPO / "protocols" / "rapp-work-sdk" / "1"


def encoded(value: object) -> bytes:
    return (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def locked_files(root: Path) -> list[dict]:
    return [
        {
            "path": path.relative_to(root).as_posix(),
            "sha256": sha256(path.read_bytes()),
        }
        for path in sorted(root.rglob("*"))
        if path.is_file()
        and not path.is_symlink()
        and path.relative_to(root).as_posix() != "rapp/agent.lock.json"
        and "__pycache__" not in path.parts
        and path.suffix != ".pyc"
    ]


def work_sdk_lock() -> dict:
    vendor = WORK_SDK / "vendor" / "rapp-work-sdk" / "1"
    profile_raw = (vendor / "profile.json").read_bytes()
    manifest_raw = (vendor / "manifest.json").read_bytes()
    parent = json.loads((vendor / "parent-pin.json").read_text(encoding="utf-8"))
    profile = json.loads(profile_raw.decode("utf-8"))
    if profile.get("current_pin") != parent.get("commit"):
        raise ValueError("RAPP Work SDK profile and parent pin disagree")
    return {
        "schema": "rapp-skill-lock/1",
        "name": "rapp-work-sdk",
        "version": "1.0.0",
        "protocol": {
            "name": "rapp-work-sdk/1",
            "profile_sha256": sha256(profile_raw),
            "manifest_sha256": sha256(manifest_raw),
            "rapp_work_repository": parent["repository"],
            "rapp_work_commit": parent["commit"],
            "rapp_work_path": parent["path"],
            "rapp_work_spec_sha256": parent["spec_sha256"],
            "rapp_work_spec_bytes": parent["spec_bytes"],
        },
        "files": locked_files(WORK_SDK),
    }


def private_hive_lock() -> dict:
    spec = PRIVATE_HIVE / "vendor" / "hive" / "SPEC.md"
    return {
        "schema": "rapp-skill-lock/1",
        "name": "rapp-private-hive",
        "version": "3.2.0",
        "protocol": {
            "name": "rapp-hive/1",
            "repository": "https://github.com/kody-w/RAPP",
            "path": "protocols/rapp-hive/1/SPEC.md",
            "spec_sha256": sha256(spec.read_bytes()),
        },
        "files": locked_files(PRIVATE_HIVE),
    }


def protocol_vendor_files() -> dict[str, bytes]:
    fixed = {
        "SPEC.md",
        "manifest.json",
        "parent-pin.json",
        "profile.json",
        "reference/scaffold.py",
    }
    for directory in ("fixtures", "history", "schemas", "vendor"):
        fixed.update(
            path.relative_to(PROTOCOL).as_posix()
            for path in (PROTOCOL / directory).rglob("*")
            if path.is_file() and not path.is_symlink()
        )
    return {relative: (PROTOCOL / relative).read_bytes() for relative in sorted(fixed)}


def sync_work_sdk_vendor() -> None:
    destination = WORK_SDK / "vendor" / "rapp-work-sdk" / "1"
    expected = protocol_vendor_files()
    actual = {
        path.relative_to(destination).as_posix(): path
        for path in destination.rglob("*")
        if path.is_file() or path.is_symlink()
    }
    for relative, path in actual.items():
        if relative not in expected:
            if path.is_symlink() or path.is_file():
                path.unlink()
            else:
                raise ValueError(f"unsafe stale SDK vendor entry: {relative}")
    for relative, raw in expected.items():
        target = destination / relative
        if target.exists() and (target.is_symlink() or not target.is_file()):
            raise ValueError(f"unsafe SDK vendor destination: {relative}")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)
    for path in sorted(destination.rglob("*"), reverse=True):
        if path.is_dir() and not any(path.iterdir()):
            path.rmdir()


def bind_private_hive() -> None:
    lock_raw = (WORK_SDK / "rapp" / "agent.lock.json").read_bytes()
    profile_raw = (
        WORK_SDK / "vendor" / "rapp-work-sdk" / "1" / "profile.json"
    ).read_bytes()
    profile = json.loads(profile_raw.decode("utf-8"))
    replacements = {
        "WORK_SDK_LOCK_SHA256": sha256(lock_raw),
        "WORK_SDK_PROFILE_SHA256": sha256(profile_raw),
        "WORK_SDK_CURRENT_PIN": profile["current_pin"],
    }
    path = PRIVATE_HIVE / "scripts" / "prepare_workspace.py"
    text = path.read_text(encoding="utf-8")
    for name, value in replacements.items():
        pattern = rf'^{name} = "[0-9a-f]+"\s*$'
        text, count = re.subn(
            pattern,
            f'{name} = "{value}"',
            text,
            count=1,
            flags=re.MULTILINE,
        )
        if count != 1:
            raise ValueError(f"cannot update {name}")
    path.write_text(text, encoding="utf-8")


def lock_for(name: str) -> tuple[Path, dict]:
    if name == "rapp-work-sdk":
        return WORK_SDK / "rapp" / "agent.lock.json", work_sdk_lock()
    if name == "rapp-private-hive":
        return PRIVATE_HIVE / "rapp" / "agent.lock.json", private_hive_lock()
    raise ValueError(f"unknown skill: {name}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "skills",
        nargs="*",
        choices=["rapp-work-sdk", "rapp-private-hive"],
    )
    parser.add_argument("--sync-work-sdk-vendor", action="store_true")
    parser.add_argument("--bind-private-hive", action="store_true")
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)
    if args.sync_work_sdk_vendor:
        sync_work_sdk_vendor()
    if args.bind_private_hive:
        bind_private_hive()
    names = args.skills or ["rapp-work-sdk", "rapp-private-hive"]
    failures = []
    for name in names:
        path, value = lock_for(name)
        raw = encoded(value)
        if args.write:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(raw)
        if not path.is_file() or path.read_bytes() != raw:
            failures.append(name)
    print(
        "Skill locks: "
        + ("PASS" if not failures else "FAIL " + ", ".join(failures))
    )
    return int(bool(failures))


if __name__ == "__main__":
    raise SystemExit(main())
