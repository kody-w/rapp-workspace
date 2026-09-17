"""Verified atomic placement for a closed generated artifact bundle."""

from __future__ import annotations

import os
from pathlib import Path
import shutil
from typing import Any

from workorg_common import canonical_bytes, read_bytes, require, safe_path, sha256


def verify_bundle(manifest: dict[str, Any], files: dict[str, bytes]) -> None:
    require(
        manifest.get("schema") == "rapp-work-organization/1/artifact-bundle"
        and manifest.get("entrypoint") == "agent.py"
        and manifest.get("candidate_tests_are_independent_proof") is False
        and manifest.get("grants_authority") is False,
        "REFUSE_BUNDLE",
        "Invalid artifact manifest.",
    )
    entries = manifest.get("files")
    require(type(entries) is list and entries, "REFUSE_BUNDLE", "Bundle inventory required.")
    expected_paths = [entry["path"] for entry in entries]
    require(
        len(expected_paths) == len(set(expected_paths))
        and set(expected_paths) == set(files),
        "REFUSE_BUNDLE",
        "Bundle files and manifest inventory differ.",
    )
    for entry in entries:
        path = safe_path(entry["path"])
        data = files[path]
        require(
            entry["sha256"] == sha256(data) and entry["bytes"] == len(data),
            "REFUSE_BUNDLE",
            "Bundle file bytes differ from the manifest.",
        )
    require(
        manifest["aggregate_sha256"] == sha256(canonical_bytes(entries)),
        "REFUSE_BUNDLE",
        "Bundle aggregate commitment differs.",
    )


def _write_file(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    descriptor = os.open(path, flags, 0o400)
    try:
        with os.fdopen(descriptor, "wb", closefd=False) as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
    finally:
        os.close(descriptor)


def place_bundle(root: Path, manifest: dict[str, Any], files: dict[str, bytes]) -> dict[str, Any]:
    verify_bundle(manifest, files)
    root.mkdir(parents=True, exist_ok=True)
    aggregate = manifest["aggregate_sha256"]
    final = root / aggregate
    if final.exists():
        require(final.is_dir(), "REFUSE_PLACEMENT", "Existing bundle slot is not a directory.")
        observed = {
            entry["path"]: read_bytes(final / entry["path"], entry["bytes"] + 1)
            for entry in manifest["files"]
        }
        verify_bundle(manifest, observed)
        return {
            "schema": "rapp-work-organization/1/placement-receipt",
            "aggregate_sha256": aggregate,
            "entrypoint_sha256": sha256(observed["agent.py"]),
            "replayed": True,
            "atomic_directory_placement": True,
            "captured_bytes_executed": False,
            "grants_authority": False,
        }
    staging = root / f".{aggregate}.{os.getpid()}.stage"
    require(not staging.exists(), "REFUSE_PLACEMENT", "Staging slot already exists.")
    staging.mkdir(mode=0o700)
    try:
        for path, data in sorted(files.items()):
            _write_file(staging / safe_path(path), data)
        os.rename(staging, final)
        directory = os.open(root, os.O_RDONLY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
    except BaseException:
        if staging.exists():
            shutil.rmtree(staging)
        raise
    observed = {
        entry["path"]: read_bytes(final / entry["path"], entry["bytes"] + 1)
        for entry in manifest["files"]
    }
    verify_bundle(manifest, observed)
    return {
        "schema": "rapp-work-organization/1/placement-receipt",
        "aggregate_sha256": aggregate,
        "entrypoint_sha256": sha256(observed["agent.py"]),
        "replayed": False,
        "atomic_directory_placement": True,
        "captured_bytes_executed": False,
        "grants_authority": False,
    }
