#!/usr/bin/env python3
"""Exact-byte manifest and protocol-index pins for rapp-hive-autobest/1."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPOSITORY = ROOT.parents[2]
INDEX = REPOSITORY / "protocols" / "index.json"
MANIFEST = ROOT / "manifest.json"
PROFILE = "rapp-hive-autobest/1"
GENERATED_UTC = "2026-09-17T21:36:39.234Z"

HIVE_SPEC_SHA256 = "79aeef7bc5000f4a7b09483844b035c66adf817475540e583138f2e6b432c822"
HIVE_SCHEMA_SHA256 = "9b383535d6a2ad379e8c70b1a1cb3ab6ed3f9ca71114c37695e24fd8560415e0"
WORKSPACE_SPEC_SHA256 = "80135ae05e532f11810d31a5cf974050a8332c18bd45f16879a7286f213edfab"
WORKSPACE_MANIFEST_SHA256 = "f1165f947cb5d7554906012a174a854b28454403e41e8166925a364a68680370"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def record(path: Path) -> dict:
    data = path.read_bytes()
    return {
        "path": path.relative_to(ROOT).as_posix(),
        "sha256": sha(data),
        "bytes": len(data),
    }


def fixture_paths() -> list[Path]:
    return sorted(
        path
        for path in (ROOT / "fixtures").rglob("*")
        if path.is_file() and "__pycache__" not in path.parts and not path.name.endswith(".pyc")
    )


def manifest_document() -> dict:
    normative = [ROOT / "SPEC.md", ROOT / "schema.json", ROOT / "provenance.json"]
    reference = sorted((ROOT / "reference").glob("*.py")) + [ROOT / "reference" / "README.md"]
    return {
        "schema": "rapp-hive-autobest-file-manifest/1",
        "profile": PROFILE,
        "parent": "rapp/1",
        "status": "additive",
        "authority": False,
        "requires": [
            {
                "profile": "rapp-hive/1",
                "spec_sha256": HIVE_SPEC_SHA256,
                "schema_sha256": HIVE_SCHEMA_SHA256,
            },
            {
                "profile": "rapp-workspace/1",
                "spec_sha256": WORKSPACE_SPEC_SHA256,
                "manifest_sha256": WORKSPACE_MANIFEST_SHA256,
            },
        ],
        "registered_kinds": [
            "hive-autobest.compatibility",
            "hive-autobest.evolution",
            "hive-autobest.exhaust",
            "hive-autobest.mutation-offer",
        ],
        "generic_ceo_binding": {
            "status": "pending-external-pin",
            "authority_inferred": False,
        },
        "normative": [record(path) for path in normative],
        "reference": [record(path) for path in reference],
        "fixtures": [record(path) for path in fixture_paths()],
        "first_wild_handshake": {
            "handshake_sha256": "0c52264b81bf88dd8555defa9363a23d8eb8ef85c3c12f66ddcaaabfc85a8882",
            "source_lens_sha256": "679fff9531c0c8b13457d594f746c45da28925a7c1be40473e8ca00823db8671",
            "target_finalizer_sha256": "c056339f90fdd4e604dbefa40291f1b7b22946d26749b36230bb3b29dd8e2296",
            "verified_frames": 2,
            "verified_artifacts": 9,
        },
    }


def encoded(value: dict) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=False) + "\n").encode("utf-8")


def profile_entry(manifest_bytes: bytes) -> dict:
    spec = record(ROOT / "SPEC.md")
    schema = record(ROOT / "schema.json")
    provenance = record(ROOT / "provenance.json")
    return {
        "name": PROFILE,
        "human_name": "RAPP Hive AutoBest/1",
        "parent": "rapp/1",
        "status": "additive",
        "authority": False,
        "requires": ["rapp-hive/1", "rapp-workspace/1"],
        "spec_path": f"protocols/{PROFILE}/SPEC.md",
        "spec_sha256": spec["sha256"],
        "spec_bytes": spec["bytes"],
        "schema_path": f"protocols/{PROFILE}/schema.json",
        "schema_sha256": schema["sha256"],
        "schema_bytes": schema["bytes"],
        "manifest_path": f"protocols/{PROFILE}/manifest.json",
        "manifest_sha256": sha(manifest_bytes),
        "manifest_bytes": len(manifest_bytes),
        "provenance_path": f"protocols/{PROFILE}/provenance.json",
        "provenance_sha256": provenance["sha256"],
        "provenance_bytes": provenance["bytes"],
        "conformance": f"protocols/{PROFILE}/reference/conformance.py",
        "generic_ceo_binding": "pending-external-pin",
        "grants_authority": False,
    }


def updated_index(entry: dict) -> dict:
    index = json.loads(INDEX.read_text(encoding="utf-8"))
    index["generated_utc"] = GENERATED_UTC
    profiles = [value for value in index["profiles"] if value["name"] != PROFILE]
    insertion = next(
        (position + 1 for position, value in enumerate(profiles) if value["name"] == "rapp-hive/1"),
        len(profiles),
    )
    profiles.insert(insertion, entry)
    index["profiles"] = profiles
    return index


def write() -> None:
    manifest_bytes = encoded(manifest_document())
    MANIFEST.write_bytes(manifest_bytes)
    INDEX.write_bytes(encoded(updated_index(profile_entry(manifest_bytes))))


def check() -> None:
    expected_manifest = encoded(manifest_document())
    if not MANIFEST.is_file() or MANIFEST.read_bytes() != expected_manifest:
        raise SystemExit("manifest.json differs from exact profile files")
    expected_entry = profile_entry(expected_manifest)
    index = json.loads(INDEX.read_text(encoding="utf-8"))
    entries = [value for value in index["profiles"] if value["name"] == PROFILE]
    if entries != [expected_entry]:
        raise SystemExit("protocols/index.json does not carry the exact AutoBest profile pin")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    arguments = parser.parse_args(argv)
    if arguments.write:
        write()
    if arguments.check:
        check()
    if not arguments.write and not arguments.check:
        print(json.dumps(profile_entry(encoded(manifest_document())), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
