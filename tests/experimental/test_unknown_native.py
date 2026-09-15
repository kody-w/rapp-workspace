"""Owner-defined UNKNOWN-native → Grail acceptance vectors; synthetic roots only."""

import copy
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import unittest
from unittest.mock import patch
import uuid

REPO = Path(__file__).resolve().parents[2]
REFERENCE = REPO / "protocols/rapp-workspace/grail-1.0/experimental/reference"
sys.path.insert(0, str(REFERENCE))

from common import Parent, Refusal, address, sha, write_file
from demo import SCENARIO, fixture_inputs, run_demo
from native_lens import MAX_FILE_BYTES, capture_native, observe_native, synthesize_program
from test_frame_lens import Fixture, UTC


class UnknownNativeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.core = Parent(os.environ.get("RAPP1_PATH"))

    def setUp(self):
        self.root = REPO / ".validation/test-artifacts" / ("unknown-" + uuid.uuid4().hex)
        self.root.mkdir(parents=True)
        self.addCleanup(shutil.rmtree, self.root)
        self.fx = Fixture(self.core, 60000)

    def native(self, files=None, name="unseen-local-root"):
        root = self.root / name
        for path, raw in (files or {"undocumented/signal.strange": b"\x00\xff??? never a RAPP artifact"}).items():
            write_file(root / path, raw, immutable=True)
        return root

    def test_headline_starts_from_three_real_unknown_shapes_and_retains_recursive_history(self):
        printed = []
        result = run_demo(self.core, self.root / "proof", show=printed.append)
        self.assertEqual(result["scenario"], SCENARIO)
        self.assertEqual(result["previously_unknown_native_shapes"], 3)
        self.assertEqual(result["native_files_observed"], 9)
        self.assertEqual(result["different_candidate_programs"], 3)
        self.assertEqual(result["learned_binding_counts"], [3, 4, 5])
        self.assertEqual(result["native_identities_assigned"], 0)
        self.assertEqual(result["known_provider_adapters_used"], 0)
        self.assertFalse(result["preassigned_taxonomy"])
        self.assertFalse(result["signed_grail_activation"])
        self.assertTrue(result["source_bytes_and_layout_unchanged"])
        self.assertTrue(result["original_and_derived_frames_retained"])
        self.assertTrue(result["restart_equivalent"])
        self.assertEqual(result["frames_scanned"], result["frames_emitted"])
        self.assertGreater(result["frames_scanned"], 0)
        self.assertEqual(result["scanner_verdict"], "COMPLIANT")
        self.assertEqual(len(result["projection"]["entries"]), 3)
        for phase in ("BEFORE", "OBSERVATION", "LENS", "SUCCESSOR", "VERIFICATION", "RECURSIVE", "PROJECTION"):
            self.assertTrue(any(line.startswith("[" + phase + "]") for line in printed), phase)
        for case in result["cases"]:
            self.assertEqual(len(case["recursive"]), 4)
            self.assertEqual(len(case["negative_refusals"]), 5)
            self.assertNotEqual(case["derived_lens_rerun"], case["successor"])
            self.assertTrue(case["ancestry_complete"])
            self.assertTrue(case["source_bytes_unchanged"])
            native = self.root / "proof/native-fixtures" / case["subject"]
            self.assertFalse(list(native.rglob("rappid.json")))
        phases = json.loads((self.root / "proof/phases.json").read_bytes())
        self.assertEqual(phases[-1]["phase"], "PROJECTION")
        case = result["cases"][0]
        changed = self.root / "proof/native-fixtures" / case["subject"] / case["before"][0]["path"]
        changed.write_bytes(b"external synthetic change")
        with self.assertRaisesRegex(Refusal, "collision"):
            run_demo(self.core, self.root / "proof", show=None)
        self.assertEqual(changed.read_bytes(), b"external synthetic change")

    def test_new_layouts_and_labels_change_recipes_without_adapter_or_taxonomy_changes(self):
        files = {"not-a-provider/" + name: ("opaque " + name).encode()
                 for name in ("x.quux", "z.quux", "somewhere/a.blob", "elsewhere/b.blob", "extra/c.odd")}
        native = self.native(files)
        source, observation, _ = observe_native(self.fx.w, native, UTC)
        p, s = self.fx.w.body(observation), self.fx.w.body(source)
        with patch("native_lens.capture_native", side_effect=AssertionError("learner performed I/O")), \
                patch.object(self.core.r, "mint_rappid", side_effect=AssertionError("learner minted identity")):
            first = synthesize_program(self.core, p, s, 0)
            self.assertEqual(first, synthesize_program(self.core, p, s, 0))
        self.assertEqual({b["name"] for b in first["bindings"]}, set(files) | {"source:" + native.name})
        self.assertEqual({b["read"]["input"] for b in first["bindings"]}, {0, 1})
        smaller = self.native({"never-before/key.new": b"unrecognized"}, name="another-local-pattern")
        other, obs, _ = observe_native(self.fx.w, smaller, UTC)
        second = synthesize_program(self.core, self.fx.w.body(obs), self.fx.w.body(other), 0)
        self.assertNotEqual(self.core.particle(first), self.core.particle(second))
        self.assertNotEqual(len(first["bindings"]), len(second["bindings"]))

    def test_fixture_generator_is_not_a_provider_catalog(self):
        self.assertNotEqual(fixture_inputs(1), fixture_inputs(99991))
        for shapes in (fixture_inputs(1), fixture_inputs(99991)):
            self.assertEqual(sorted(len(files) for files in shapes.values()), [2, 3, 4])
            for files in shapes.values():
                self.assertNotIn("rappid.json", files)
                self.assertTrue(all(b'"spec":"rapp/1"' not in raw for raw in files.values()))

    def test_opaque_byte_and_observation_bindings_refuse_forged_equivalence(self):
        native = self.native()
        before = capture_native(native)
        source, observation, captured = observe_native(self.fx.w, native, UTC)
        self.assertEqual(before, captured)
        p = self.fx.w.body(observation)
        self.assertEqual(p["sources"], [source])
        p["metadata"][0]["value"] = "0" * 64
        p["fingerprint"] = self.core.particle(p["metadata"])
        checkpoint = self.fx.w.checkpoint()
        with self.assertRaisesRegex(Refusal, "observation/source mismatch"):
            self.fx.w.append(p, UTC)
        bad = self.fx.w.body(source)
        bad["files"][0]["octets_b64"] = "AAAA"
        with self.assertRaisesRegex(Refusal, "byte substitution"):
            self.fx.w.append(bad, UTC)
        self.assertEqual(checkpoint, self.fx.w.checkpoint())
        self.assertEqual(before, capture_native(native))

    def test_native_byte_and_file_budgets_refuse_before_frame_emission(self):
        large = self.native({"x.blob": b"x" * (MAX_FILE_BYTES + 1)}, name="oversized")
        many = self.native({f"file{i}.blob": b"data" for i in range(17)}, name="too-many")
        total = self.native({f"file{i}.blob": b"x" * MAX_FILE_BYTES for i in range(5)}, name="aggregate")
        for root in (large, many, total):
            before = self.fx.w.checkpoint()
            with self.subTest(root=root.name), self.assertRaisesRegex(Refusal, "budget"):
                observe_native(self.fx.w, root, UTC)
            self.assertEqual(before, self.fx.w.checkpoint())

    def test_native_no_follow_and_time_limits_do_not_read_or_modify_other_roots(self):
        outside = self.native({"preserve.blob": b"do not observe"}, name="outside")
        linked = self.native(name="linked")
        (linked / "escape").symlink_to(outside, target_is_directory=True)
        before = self.fx.w.checkpoint()
        with self.assertRaisesRegex(Refusal, "symlink"):
            observe_native(self.fx.w, linked, UTC)
        self.assertEqual(self.fx.w.checkpoint(), before)
        hard = self.native(name="hardlink")
        os.link(outside / "preserve.blob", hard / "external")
        with self.assertRaisesRegex(Refusal, "hardlink"):
            observe_native(self.fx.w, hard, UTC)
        ordinary = self.native(name="ordinary")
        with patch("native_lens.time.monotonic", side_effect=[0, 3]):
            with self.assertRaisesRegex(Refusal, "time budget"):
                observe_native(self.fx.w, ordinary, UTC)
        self.assertEqual((outside / "preserve.blob").read_bytes(), b"do not observe")
        self.assertEqual(self.fx.w.checkpoint(), before)

    def test_demo_refuses_unmanaged_or_changed_existing_inputs(self):
        root = self.root / "unmanaged"
        root.mkdir()
        (root / "owner-file").write_bytes(b"must stay")
        with self.assertRaisesRegex(Refusal, "unmanaged"):
            run_demo(self.core, root, show=None)
        self.assertEqual(list(p.name for p in root.iterdir()), ["owner-file"])
        self.assertEqual((root / "owner-file").read_bytes(), b"must stay")

    def test_one_command_demo_has_visible_pipeline_and_a_verifiable_report(self):
        relative = (self.root / "cli-proof").relative_to(REPO)
        completed = subprocess.run(
            [sys.executable, "-B", str(REFERENCE / "demo.py"),
             "--rapp1-path", str(self.core.path), "--output", str(relative), "--fixture-seed", "9127"],
            cwd=REPO, capture_output=True, text=True, timeout=120)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        for phase in ("BEFORE", "OBSERVATION", "LENS", "SUCCESSOR", "VERIFICATION", "PROJECTION", "PASS"):
            self.assertIn("[" + phase + "]", completed.stdout)
        report = json.loads((REPO / relative / "demo-report.json").read_bytes())
        self.assertEqual(report["fixture_seed"], 9127)
        self.assertEqual(report["different_candidate_programs"], 3)
        self.assertEqual(report["profile"], "rapp-workspace/1.0")
        self.assertFalse(report["signed_estate_authority_verified"])


if __name__ == "__main__":
    unittest.main()
