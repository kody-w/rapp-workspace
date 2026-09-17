"""Exact file inventory and repository protocol-index binding."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from common import PROFILE, REPO, ROOT, read_file, sha, write_file


def record(base: Path, path: str) -> dict[str, object]:
    raw = read_file(base / path)
    return {"path": path, "sha256": sha(raw), "bytes": len(raw)}


def manifest() -> dict[str, object]:
    normative = ["SPEC.md", "safety-matrix.json", "runtime-manifest.json"] + [
        "schemas/" + path.name for path in sorted((ROOT / "schemas").glob("*.json"))
    ]
    reference = [
        "reference/" + path.name for path in sorted((ROOT / "reference").glob("*.py"))
    ]
    fixtures = [
        path.relative_to(ROOT).as_posix()
        for path in sorted((ROOT / "fixtures").rglob("*"))
        if path.is_file()
    ]
    tests = [
        path.relative_to(ROOT).as_posix()
        for path in sorted((ROOT / "tests").glob("test_*.py"))
    ]
    return {
        "schema": "rapp-work-compatibility-file-manifest/1",
        "profile": PROFILE,
        "human_name": "RAPP Work Compatibility/1",
        "parent": "rapp-workspace/1",
        "substrate": "rapp/1",
        "authority": False,
        "status": "optional-application-profile",
        "signed_activation": False,
        "normative": [record(ROOT, path) for path in normative],
        "reference": [record(ROOT, path) for path in reference],
        "tests": [record(ROOT, path) for path in tests],
        "fixtures": [record(ROOT, path) for path in fixtures],
        "documentation": [record(ROOT, "README.md")],
        "provenance": record(ROOT, "provenance.json"),
        "authority_boundary": "local-validation-and-external-controller-adoption-required",
        "dynamic_execution": "external-global-brainstem-only",
        "static_execution": "captured-byte-isolated-host-qualification-required",
        "generic_ceo_agent": "awaiting-exact-pin-not-included",
        "microsol_schema_boundary": "concrete-live-subscription-profile-only",
    }


def index_profile() -> dict[str, object]:
    prefix = "protocols/rapp-work-compatibility/1/"
    spec = record(REPO, prefix + "SPEC.md")
    files = record(REPO, prefix + "manifest.json")
    provenance = record(REPO, prefix + "provenance.json")
    package = record(
        REPO,
        prefix + "fixtures/softwarecoellc-vteam-hive/package.json",
    )
    return {
        "name": PROFILE,
        "human_name": "RAPP Work Compatibility/1",
        "parent": "rapp-workspace/1",
        "substrate": "rapp/1",
        "authority": False,
        "status": "optional-application-profile",
        "signed_activation": False,
        "spec_path": spec["path"],
        "spec_sha256": spec["sha256"],
        "spec_bytes": spec["bytes"],
        "manifest_path": files["path"],
        "manifest_sha256": files["sha256"],
        "manifest_bytes": files["bytes"],
        "provenance_path": provenance["path"],
        "provenance_sha256": provenance["sha256"],
        "provenance_bytes": provenance["bytes"],
        "schemas_path": prefix + "schemas",
        "conformance": prefix + "reference/conformance.py",
        "bill_fixture_package": package,
        "execution": "external-host-only",
        "grants_authority": False,
        "generic_ceo_agent": "awaiting-pin",
    }


def check_index() -> bool:
    index = json.loads(read_file(REPO / "protocols/index.json"))
    matches = [item for item in index["profiles"] if item["name"] == PROFILE]
    return (
        index.get("authority") is True
        and index.get("workspace_latest") == "rapp-workspace/1"
        and matches == [index_profile()]
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--write-index", action="store_true")
    arguments = parser.parse_args()
    manifest_path = ROOT / "manifest.json"
    raw = (json.dumps(manifest(), indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    if arguments.write:
        write_file(manifest_path, raw)
    if arguments.write_index:
        index_path = REPO / "protocols/index.json"
        index = json.loads(read_file(index_path))
        index["profiles"] = [
            item for item in index["profiles"] if item["name"] != PROFILE
        ] + [index_profile()]
        index["generated_utc"] = "2026-09-17T21:36:39.047Z"
        write_file(
            index_path,
            (json.dumps(index, indent=2, ensure_ascii=False) + "\n").encode("utf-8"),
        )
    good = manifest_path.is_file() and read_file(manifest_path) == raw and check_index()
    print("RAPP Work Compatibility/1 spec/schema/runtime/index pins: " + ("PASS" if good else "FAIL"))
    return int(not good)


if __name__ == "__main__":
    raise SystemExit(main())
