"""Exact file inventory and protocol-index binding for Work Organization/1."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from workorg_common import PROFILE, REPO, ROOT, pretty_bytes, read_bytes, sha256


BRAND = "RAPP Work Organization/1"
GENERATED_UTC = "2026-09-17T21:36:39.279Z"


def record(base: Path, name: str) -> dict[str, object]:
    data = read_bytes(base / name)
    return {"path": name, "sha256": sha256(data), "bytes": len(data)}


def manifest() -> dict[str, object]:
    normative = ["SPEC.md", "limits.json", "safety-matrix.json"] + [
        "schemas/" + path.name for path in sorted((ROOT / "schemas").glob("*.json"))
    ]
    reference = ["reference/" + path.name for path in sorted((ROOT / "reference").glob("*.py"))]
    fixtures = [
        "fixtures/" + path.name for path in sorted((ROOT / "fixtures").glob("*.json"))
    ]
    evidence = [
        "docs/rapp-work.md",
        "docs/rapp-work-organization.md",
        "tools/work_organization.py",
        "tests/test_work_organization.py",
        "tests/test_work_organization_p0.py",
        ".github/skills/rapp-work-organization/SKILL.md",
        ".github/workflows/ci.yml",
    ]
    return {
        "schema": "rapp-work-organization-file-manifest/1",
        "profile": PROFILE,
        "brand": BRAND,
        "parent": "rapp/1",
        "status": "candidate",
        "conformance_class": "single-host-locked-handshake",
        "brainstem_modified": False,
        "host_authority": "external",
        "generic_ceo_agent": "pending-pin",
        "live_activation": False,
        "normative": [record(ROOT, name) for name in normative],
        "reference": [record(ROOT, name) for name in reference],
        "fixtures": [record(ROOT, name) for name in fixtures],
        "repository_evidence": [record(REPO, name) for name in evidence],
        "provenance": record(ROOT, "provenance.json"),
        "first_wild_handshake": {
            "id": "softwarecoellc-vteam-hive",
            "fixture": record(ROOT, "fixtures/softwarecoellc-vteam-hive-1.json"),
            "private_source_bytes_embedded": False,
        },
    }


def index_profile() -> dict[str, object]:
    base = "protocols/rapp-work-organization/1/"
    spec = record(REPO, base + "SPEC.md")
    files = record(REPO, base + "manifest.json")
    provenance = record(REPO, base + "provenance.json")
    fixture = record(REPO, base + "fixtures/softwarecoellc-vteam-hive-1.json")
    return {
        "name": PROFILE,
        "human_name": BRAND,
        "parent": "rapp/1",
        "status": "candidate",
        "generation": "application-profile",
        "conformance_class": "single-host-locked-handshake",
        "brainstem_modified": False,
        "host_authority": "external",
        "generic_ceo_agent": "pending-pin",
        "live_activation": False,
        "locked_runtime_model_calls": "forbidden",
        "spec_path": spec["path"],
        "spec_sha256": spec["sha256"],
        "spec_bytes": spec["bytes"],
        "manifest_path": files["path"],
        "manifest_sha256": files["sha256"],
        "manifest_bytes": files["bytes"],
        "provenance_path": provenance["path"],
        "provenance_sha256": provenance["sha256"],
        "provenance_bytes": provenance["bytes"],
        "schemas_path": base + "schemas",
        "conformance": base + "reference/conformance.py",
        "first_wild_handshake_fixture": fixture["path"],
        "first_wild_handshake_fixture_sha256": fixture["sha256"],
        "related_profiles": [
            "rapp-workspace/1",
            "rapp-hive/1",
            "rapp-federation/1",
        ],
    }


def check_index() -> bool:
    index = json.loads((REPO / "protocols/index.json").read_bytes())
    matches = [profile for profile in index["profiles"] if profile["name"] == PROFILE]
    return matches == [index_profile()]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--write-index", action="store_true")
    args = parser.parse_args()
    expected = pretty_bytes(manifest())
    path = ROOT / "manifest.json"
    if args.write:
        path.write_bytes(expected)
    if args.write_index:
        index_path = REPO / "protocols/index.json"
        index = json.loads(index_path.read_bytes())
        index["profiles"] = [
            profile for profile in index["profiles"] if profile["name"] != PROFILE
        ] + [index_profile()]
        index["generated_utc"] = GENERATED_UTC
        index_path.write_bytes(pretty_bytes(index))
    good = path.is_file() and path.read_bytes() == expected and check_index()
    print("RAPP Work Organization/1 file and index pins: " + ("PASS" if good else "FAIL"))
    return int(not good)


if __name__ == "__main__":
    raise SystemExit(main())
