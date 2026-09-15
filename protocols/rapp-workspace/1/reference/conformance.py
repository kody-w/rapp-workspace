"""Blocking Workspace/1 core safety-kernel conformance; no experimental grants or effects."""

import argparse
import json
import os
from pathlib import Path
import sys
import unittest

from common import Parent, ROOT, read_file, require, sha, write_file
from pins import REPO, encode, manifest, check_index
from safe_demo import run_demo


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rapp1-path", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path(".validation/workspace1-core-safe-conformance"))
    args = parser.parse_args()
    require(not args.output.is_absolute() and ".." not in args.output.parts, "relative owned output required")
    core = Parent(args.rapp1_path)
    initial = read_file(ROOT / "manifest.json")
    require(initial == encode(manifest()) and check_index(), "Workspace/1 core validator/runtime pin drift")
    os.environ["RAPP1_PATH"] = str(args.rapp1_path.absolute())
    sys.path.insert(0, str(REPO / "tests"))
    suite = unittest.defaultTestLoader.discover(str(REPO / "tests"), pattern="test_*.py")
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    require(result.wasSuccessful() and result.testsRun > 0 and not result.skipped,
            "blocking Workspace/1 core vectors failed")
    demo = run_demo(core, args.output / "proof")
    require(read_file(ROOT / "manifest.json") == initial == encode(manifest()), "input tree changed during checks")
    report = {
        "spec_id": "rapp-workspace/1", "brand": "RAPP Workspace/1",
        "tests_run": result.testsRun, "failures": len(result.failures), "errors": len(result.errors),
        "skipped": len(result.skipped), "input_tree_stable": True, "manifest_sha256": sha(initial),
        "guarantees": demo.get("guarantees", {}), "rapp_frames_verified": demo["rapp_frames_verified"],
        "scanner_scope": "RAPP-integrity-only", "protocol_authority": True,
        "signed_activation": False, "safely_deployable": False,
        "activation_mode": "synthetic", "activation_authenticated": False,
        "external_effects": "disabled", "prototype_results_are_not_acceptance": True,
    }
    write_file(args.output / "conformance-results.json", encode(report))
    print(json.dumps(report, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
