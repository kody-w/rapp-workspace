"""Profile-independent Work Organization/1 candidate conformance."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import unittest

from workorg_common import REPO, ROOT, pretty_bytes, read_bytes, sha256
from pins import check_index, manifest
from protocol import validate_bill_binding
from workorg_artifact import (
    ARTIFACT_RELATIVE,
    GENERIC_CEO_BYTES,
    GENERIC_CEO_PROFILE_SHA256,
    GENERIC_CEO_SHA256,
    GENERIC_CEO_SKILL_BYTES,
    GENERIC_CEO_SKILL_SHA256,
    validate_generic_ceo_artifact,
)
from workorg_schema_source import documents


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--report",
        type=Path,
        default=ROOT / "conformance-results.json",
    )
    args = parser.parse_args()
    initial = read_bytes(ROOT / "manifest.json")
    expected = pretty_bytes(manifest())
    if initial != expected or not check_index():
        raise SystemExit("Work Organization/1 manifest or index drift")
    for name, value in documents().items():
        if read_bytes(ROOT / "schemas" / name) != pretty_bytes(value):
            raise SystemExit("Work Organization/1 schema drift: " + name)
    bill = validate_bill_binding(
        json.loads(read_bytes(ROOT / "fixtures/softwarecoellc-vteam-hive-1.json"))
    )
    artifact_root = ROOT / ARTIFACT_RELATIVE
    generic_ceo = validate_generic_ceo_artifact(
        json.loads(read_bytes(artifact_root / "profile.json")),
        read_bytes(artifact_root / "agent.py"),
        read_bytes(artifact_root / "SKILL.md"),
    )
    sys.path.insert(0, str(REPO / "tests"))
    suite = unittest.TestSuite()
    loader = unittest.defaultTestLoader
    for pattern in ("test_work_organization.py", "test_work_organization_p0.py"):
        suite.addTests(loader.discover(str(REPO / "tests"), pattern=pattern))
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if not result.wasSuccessful() or result.testsRun == 0 or result.skipped:
        return 1
    if read_bytes(ROOT / "manifest.json") != initial:
        raise SystemExit("Work Organization/1 inputs changed during conformance")
    report = {
        "profile": "rapp-work-organization/1",
        "status": "candidate",
        "conformance_class": "single-host-locked-handshake",
        "tests_run": result.testsRun,
        "failures": len(result.failures),
        "errors": len(result.errors),
        "skipped": len(result.skipped),
        "schemas_checked": len(documents()),
        "manifest_sha256": sha256(initial),
        "first_wild_handshake": {
            "id": bill["id"],
            "handshake_profile_sha256": bill["handshake_profile"]["sha256"],
            "source_lens_sha256": bill["source_lens"]["sha256"],
            "target_finalizer_sha256": bill["target_finalizer"]["sha256"],
            "verified_frames": bill["source"]["verified_frames"],
            "verified_artifacts": bill["source"]["verified_artifacts"],
        },
        "private_source_bytes_embedded": False,
        "brainstem_modified": False,
        "locked_runtime_model_calls": 0,
        "generic_ceo_agent": {
            "status": generic_ceo["status"],
            "sha256": GENERIC_CEO_SHA256,
            "bytes": GENERIC_CEO_BYTES,
            "skill_sha256": GENERIC_CEO_SKILL_SHA256,
            "skill_bytes": GENERIC_CEO_SKILL_BYTES,
            "artifact_profile_sha256": GENERIC_CEO_PROFILE_SHA256,
        },
        "activation_artifact_ready": True,
        "live_activation": False,
        "rapp_frames_cryptographically_verified": 0,
        "scope": "profile-independent-structural-and-synthetic-reference",
        "input_tree_stable": True,
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    encoded = pretty_bytes(report)
    if not args.report.exists() or args.report.read_bytes() != encoded:
        args.report.write_bytes(encoded)
    print(json.dumps(report, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
