"""Run first Workspace Grail/1 candidate tests and scan nonzero emitted RAPP/1 frames."""

import argparse
import json
import os
from pathlib import Path
import sys
import unittest

from common import Parent, Refusal, ROOT, read_file, require, sha, write_file
from pins import REPO, encode, index_matches, manifest
from frame_anything import SCENARIO, run_frame_anything


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rapp1-path", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path(".validation/workspace-grail-conformance"))
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()
    if args.output.is_absolute() or ".." in args.output.parts or args.output == Path("."):
        parser.error("--output must be an owned relative artifact directory, not a temporary directory")
    core = Parent(args.rapp1_path)
    initial = read_file(ROOT / "manifest.json")
    require(initial == encode(manifest()), "profile manifest is stale")
    require(index_matches(), "protocol index is stale")
    os.environ["RAPP1_PATH"] = str(args.rapp1_path.absolute())
    sys.path.insert(0, str(REPO / "tests/experimental"))
    import test_frame_lens
    import test_unknown_native
    import test_frame_anything
    import test_iteration
    suite = unittest.TestSuite([
        unittest.defaultTestLoader.loadTestsFromTestCase(test_iteration.IterationTests),
        unittest.defaultTestLoader.loadTestsFromTestCase(test_frame_anything.FrameAnythingTests),
        unittest.defaultTestLoader.loadTestsFromTestCase(test_unknown_native.UnknownNativeTests),
        unittest.defaultTestLoader.loadTestsFromTestCase(test_frame_lens.FrameLensTests),
    ])
    result = unittest.TextTestRunner(verbosity=2 if args.verbose else 1).run(suite)
    if not result.wasSuccessful() or not result.testsRun or result.skipped:
        return 1
    proof = run_frame_anything(core, args.output)
    require(proof["unresolved_objects"] >= 1 and proof["workspace_adoptions"] >= 1,
            "headline acceptance must prove conditional adoption and expected unresolved outcomes")
    require(proof["refusal_driven_successes"] >= 1 and proof["stable_refusals"] >= 1,
            "headline acceptance must prove refusal-driven repair and stable honest refusal")
    require(read_file(ROOT / "manifest.json") == initial and initial == encode(manifest()), "inputs changed during test")
    report = {
        "profile": "rapp-workspace/1.0", "protocol_family": "rapp-workspace/1",
        "brand": "RAPP Workspace Grail/1", "generation": "grail",
        "status": "first-grail-authority-candidate", "signed_grail_activation": False,
        "conformance_class": "bounded-local-stdlib-ir", "owner_activated": False,
        "signed_estate_authority_verified": False, "live_native_profiles_observed": 0,
        "headline_scenario": SCENARIO, "concept": "Frame Anything",
        "objects_framed": proof["objects_framed"], "workspace_candidates": proof["workspace_candidates"],
        "workspace_adoptions": proof["workspace_adoptions"], "unresolved_objects": proof["unresolved_objects"],
        "bounded_iteration": True, "refusal_driven_successes": proof["refusal_driven_successes"],
        "stable_refusals": proof["stable_refusals"],
        "framing_is_not_workspace_adoption": True,
        "source_preservation_verified": proof["source_preservation_verified"],
        "ancestry_retained": proof["ancestry_retained"],
        "known_provider_adapters_used": 0, "preassigned_taxonomy": False,
        "tests_run": result.testsRun, "failures": 0, "errors": 0, "skipped": 0,
        "rapp1_commit": core.pin["commit"], "manifest_sha256": sha(initial),
        **{key: proof[key] for key in ("frames_emitted", "frames_scanned", "streams_scanned",
                                     "scanner_verdict", "findings", "scan_evidence")},
        "restart_equivalent": True, "input_tree_stable": True,
        "acceptance_proof": "frame-anything-report.json", "visible_phases": "phases.json",
        "limitations": [
            "synthetic local integrity and explicitly supplied consent, not signed estate activation",
            "universal framing is bounded opaque evidence, never automatic RW/1 workspace adoption",
            "standalone/insufficient/incompatible inputs emit unresolved successors, not fake workspaces",
            "no live model synthesis, automatic grafts, or deployment",
            "whole-store rollback needs an independently protected checkpoint",
        ],
    }
    write_file(args.output / "report.json", encode(report))
    print(json.dumps({k: v for k, v in report.items() if k not in ("scan_evidence", "limitations")}, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (Refusal, OSError, ValueError) as error:
        print("REFUSED: " + str(error), file=sys.stderr)
        raise SystemExit(1)
