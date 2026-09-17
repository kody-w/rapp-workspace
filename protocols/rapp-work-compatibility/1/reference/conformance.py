"""Blocking conformance for the optional RAPP Work Compatibility/1 profile."""

from __future__ import annotations

import argparse
import json
import os
import sys
import unittest
from pathlib import Path

from common import REPO, ROOT, Parent, read_file, require, sha, write_file
from pins import check_index, manifest
from schema_source import encoded, schemas
from validator import (
    compile_static_agent,
    validate_capability_manifest,
    validate_handshake_package,
    validate_seed_capability_binding,
    verify_profile_frame,
)

FIXTURE = ROOT / "fixtures/softwarecoellc-vteam-hive"
AUTOBEST_FIXTURE = ROOT / "fixtures/generic-autobest-capability"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rapp1-path", type=Path, required=True)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(".validation/rapp-work-compatibility-1"),
    )
    arguments = parser.parse_args()
    require(
        not arguments.output.is_absolute() and ".." not in arguments.output.parts,
        "relative owned output required",
    )
    initial = read_file(ROOT / "manifest.json")
    expected = (json.dumps(manifest(), indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    require(initial == expected and check_index(), "profile manifest or index drift")
    for name, value in schemas().items():
        require(read_file(ROOT / "schemas" / name) == encoded(value), "schema drift: " + name)

    core = Parent(arguments.rapp1_path)
    os.environ["RAPP1_PATH"] = str(arguments.rapp1_path.absolute())
    sys.path.insert(0, str(ROOT / "reference"))
    suite = unittest.defaultTestLoader.discover(str(ROOT / "tests"), pattern="test_*.py")
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    require(
        result.wasSuccessful() and result.testsRun > 0 and not result.skipped,
        "profile tests failed",
    )

    source_frames = [
        core.parse(read_file(path))
        for path in sorted((FIXTURE / "source-frames").glob("*.json"))
    ]
    previous = None
    verified = 0
    for frame in source_frames:
        ok, step, reason = core.r.verify_frame(
            frame,
            head=previous,
            stream_id_of_record=frame["stream_id"],
        )
        require(ok, f"Bill source fixture refusal: {step}: {reason}")
        previous = frame
        verified += 1
    compatibility = core.parse(read_file(FIXTURE / "compatibility-frame.json"))
    verify_profile_frame(core, compatibility)
    verified += 1
    handshake = json.loads(read_file(FIXTURE / "handshake.json"))
    generated = compile_static_agent(compatibility, handshake)
    checked_agent = read_file(FIXTURE / "static-agent.py")
    require(generated == checked_agent, "static fixture reproduction failed")
    package = core.parse(read_file(FIXTURE / "package.json"))
    validate_handshake_package(package)
    capability_index = core.parse(read_file(ROOT / "capabilities/index.json"))
    capability_entry = capability_index["entries"][0]
    capability = core.parse(read_file(ROOT / capability_entry["path"]))
    validate_capability_manifest(capability)
    require(
        capability_entry["particle"] == core.particle(capability),
        "generic AutoBest capability particle mismatch",
    )
    workspace_seed = core.parse(read_file(AUTOBEST_FIXTURE / "workspace-seed.json"))
    ok, step, reason = core.r.verify_frame(
        workspace_seed,
        head=None,
        stream_id_of_record=workspace_seed["stream_id"],
    )
    require(ok, f"AutoBest Workspace seed refusal: {step}: {reason}")
    require(
        workspace_seed["payload"]["schema"] == "rapp-workspace/1/seed",
        "AutoBest fixture must bind an exact Workspace/1 seed",
    )
    verified += 1
    seed_binding = core.parse(
        read_file(AUTOBEST_FIXTURE / "seed-capability-binding.json")
    )
    binding_record = verify_profile_frame(core, seed_binding)
    validate_seed_capability_binding(binding_record, capability=capability, core=core)
    verified += 1
    require(read_file(ROOT / "manifest.json") == initial == expected, "input tree changed")

    report = {
        "profile": "rapp-work-compatibility/1",
        "parent": "rapp-workspace/1",
        "substrate": "rapp/1",
        "tests_run": result.testsRun,
        "failures": len(result.failures),
        "errors": len(result.errors),
        "skipped": len(result.skipped),
        "manifest_sha256": sha(initial),
        "rapp_frames_verified": verified,
        "source_frames_verified": len(source_frames),
        "compatibility_frames_verified": 1,
        "workspace_seed_frames_verified": 1,
        "seed_capability_frames_verified": 1,
        "bill_fixture": {
            "handshake_sha256": package["handshake"]["sha256"],
            "source_agent_sha256": package["source_agent"]["sha256"],
            "target_agent_sha256": package["target_agent"]["sha256"],
            "static_agent_sha256": package["static_agent"]["sha256"],
            "live_qualification_summary": {
                "signed_frames": 2,
                "artifacts": 9,
            },
        },
        "guarantees": {
            "rapp_integrity": "verified-nonzero-synthetic-fixture",
            "observation": "synthetic-fixture-plus-external-live-summary",
            "semantic_fidelity": "scoped-read-only-fixture-only",
            "current_authorization": "not-inferred",
            "safe_deployment": "refused-external",
        },
        "authority": False,
        "estate_activation": False,
        "model_calls_during_static_runtime": 0,
        "generic_ceo_agent": {
            "capability_particle": capability_entry["particle"],
            "agent_sha256": capability["agent"]["sha256"],
            "agent_bytes": capability["agent"]["bytes"],
            "skill_sha256": capability["skill"]["sha256"],
            "skill_bytes": capability["skill"]["bytes"],
            "activation": capability["activation"],
            "mutation": capability["mutation"],
            "authority_from_presence": capability["authority_from_presence"],
        },
        "microsol_generic_schema_shipped": False,
    }
    write_file(
        REPO / arguments.output / "conformance-results.json",
        (json.dumps(report, indent=2, sort_keys=True) + "\n").encode("utf-8"),
    )
    print(json.dumps(report, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
