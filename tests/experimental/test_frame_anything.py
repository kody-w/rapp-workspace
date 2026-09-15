"""Universal opaque framing is distinct from conditional RW/1 workspace adoption."""

import copy
from dataclasses import replace
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import unittest
import uuid

REPO = Path(__file__).resolve().parents[2]
REFERENCE = REPO / "protocols/rapp-workspace/grail-1.0/experimental/reference"
sys.path.insert(0, str(REFERENCE))
from common import Parent, Refusal, read_file, write_file
from frame_anything import run_frame_anything
from framing import capture_object, frame_object, synthesize_attempt
from test_frame_lens import Fixture, UTC


class FrameAnythingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.core = Parent(os.environ.get("RAPP1_PATH"))

    def setUp(self):
        self.root = REPO / ".validation/test-artifacts" / ("anything-" + uuid.uuid4().hex)
        self.root.mkdir(parents=True)
        self.addCleanup(shutil.rmtree, self.root)
        self.fx = Fixture(self.core, 110000)
        self.w = self.fx.w

    def pipeline(self, path):
        source, observation, before = frame_object(self.w, path, UTC)
        program = synthesize_attempt(self.core, self.w.body(source), self.w.body(observation))
        lens = self.w.lens("evidence-derived attempt", [observation], program, self.fx.owner, UTC)
        receipt, evidence, result = self.fx.trial(lens, [source, observation])
        return source, observation, lens, receipt, evidence, result, before

    def test_headline_matrix_frames_all_and_expects_conditional_refusals(self):
        lines = []
        report = run_frame_anything(self.core, self.root / "matrix", show=lines.append)
        self.assertEqual(report["concept"], "Frame Anything")
        self.assertEqual(report["objects_framed"], 6)
        self.assertEqual(report["workspace_adoptions"], 3)
        self.assertEqual(report["unresolved_objects"], 3)
        self.assertTrue(report["framing_is_not_workspace_adoption"])
        self.assertFalse(report["signed_grail_activation"])
        self.assertEqual(len(report["projection"]["entries"]), 3)
        self.assertEqual(report["refusal_driven_successes"], 1)
        self.assertGreaterEqual(report["stable_refusals"], 1)
        self.assertEqual(report["known_provider_adapters_used"], 0)
        self.assertFalse(report["preassigned_taxonomy"])
        self.assertGreater(report["frames_scanned"], 0)
        for stage in ("SOURCE FINGERPRINT", "OPAQUE FRAME", "LENS DECLARATION", "DECLARED READS",
                      "SUCCESSOR", "REFUSAL / UNRESOLVED", "VERIFICATION", "SOURCE PRESERVATION / ANCESTRY"):
            self.assertTrue(any(line.startswith("[" + stage + "]") for line in lines), stage)
        for item in report["inputs"]:
            self.assertEqual(item["framing"], "verified")
            if item["workspace_conversion"] == "unresolved":
                self.assertFalse(item["workspace_adopted"])
                self.assertIn("unresolved-adoption", item["negatives"])

    def test_arbitrary_file_and_foreign_manifest_are_framed_without_semantic_claims(self):
        path = self.root / "foreign-agent.manifest"
        raw = b'{"owner":"self-claimed","execute":"do-not-execute","workspace":"unbound/place"}'
        write_file(path, raw)
        source, obs, lens, receipt, evidence, result, before = self.pipeline(path)
        self.assertEqual(self.w.body(source)["semantics"], "unknown")
        self.assertIsNone(self.w.body(source)["native_identity"])
        self.assertEqual(self.w.body(result)["reason"], "incompatible-object-kind")
        self.assertEqual(self.w.body(result)["schema"], "rapp-workspace/1.0/workspace-unresolved")
        self.assertFalse(self.w.body(result)["adoption_eligible"])
        self.assertEqual(before, capture_object(path))
        self.assertEqual(path.read_bytes(), raw)

    def test_unresolved_cannot_be_adopted_even_with_exact_owner_consent_or_copy_lens(self):
        path = self.root / "blob"
        write_file(path, b"\x00\xff unknown")
        source, obs, lens, _, evidence, result, _ = self.pipeline(path)
        before = self.w.checkpoint()
        with self.assertRaisesRegex(Refusal, "unresolved successor"):
            self.fx.approve(self.w.adoption_payload(result, evidence))
        self.assertEqual(before, self.w.checkpoint())
        copier = self.fx.identity_lens(obs)
        _, copied_proof, copied = self.fx.trial(copier, [result])
        with self.assertRaisesRegex(Refusal, "unresolved successor"):
            self.fx.approve(self.w.adoption_payload(copied, copied_proof))
        self.assertEqual(self.w.projection()["entries"], [])

    def test_unconditional_projection_cannot_launder_an_arbitrary_file_into_a_workspace(self):
        path = self.root / "single"
        write_file(path, b"opaque")
        source, obs, _, _, _, _, _ = self.pipeline(path)
        program = {"op": "project", "tick": 0, "bindings": [
            {"name": "fake-workspace", "read": {"name": "metadata", "input": 0, "pointer": "/metadata/1/value"}}]}
        lens = self.w.lens("must-not-launder", [obs], program, self.fx.owner, UTC)
        before = self.w.checkpoint()
        with self.assertRaisesRegex(Refusal, "workspace-attempt assessment"):
            self.w.mutate(lens, [obs], UTC)
        self.assertEqual(before, self.w.checkpoint())

    def test_workspace_candidate_requires_verified_container_evidence(self):
        root = self.root / "tree"
        write_file(root / "unknown.a", b"A")
        source, obs, lens, _, proof, result, _ = self.pipeline(root)
        self.assertEqual(self.w.body(result)["reason"], "insufficient-workspace-evidence")
        write_file(root / "nested/unknown.b", b"B")
        source2, obs2, lens2, _, proof2, result2, before = self.pipeline(root)
        self.assertEqual(self.w.body(result2)["schema"], "rapp-workspace/1.0/workspace-successor")
        self.fx.approve(self.w.adoption_payload(lens2, proof2))
        self.fx.approve(self.w.adoption_payload(result2, proof2))
        self.fx.approve(self.w.route_payload(result2, "select"))
        self.assertEqual(len(self.w.projection()["entries"]), 1)
        self.assertEqual(before, capture_object(root))
        counterfeit = self.w.body(result2)
        counterfeit["source"] = source
        counterfeit["observation"] = obs
        with self.assertRaisesRegex(Refusal, "not justified"):
            self.w.append(counterfeit, UTC)

    def test_large_files_receive_honest_digest_only_framing_and_no_false_workspace_evidence(self):
        root = self.root / "large-tree"
        write_file(root / "large.data", b"x" * 70000)
        write_file(root / "small.data", b"data")
        source, _, _, _, _, result, before = self.pipeline(root)
        entries = self.w.body(source)["entries"]
        large = next(e for e in entries if e["bytes"] == 70000)
        self.assertEqual(large["coverage"], "digest-only")
        self.assertIsNone(large["octets_b64"])
        self.assertEqual(self.w.body(result)["reason"], "external-content-evidence-required")
        self.assertEqual(before, capture_object(root))

    def test_links_and_special_objects_are_opaque_and_never_followed_or_opened(self):
        target = self.root / "not-followed"
        write_file(target, b"retain target")
        link = self.root / "pointer"
        link.symlink_to(target.name)
        source, _, _, _, _, result, _ = self.pipeline(link)
        self.assertEqual(self.w.body(source)["object_kind"], "symlink")
        self.assertEqual(self.w.body(result)["reason"], "incompatible-object-kind")
        self.assertEqual(target.read_bytes(), b"retain target")
        fifo = self.root / "special"
        os.mkfifo(fifo)
        source, _, _, _, _, result, _ = self.pipeline(fifo)
        item = self.w.body(source)["entries"][0]
        self.assertEqual(item["coverage"], "metadata-only")
        self.assertIsNone(item["sha256"])
        self.assertIsNone(item["bytes"])
        self.assertEqual(self.w.body(result)["reason"], "incompatible-object-kind")

    def test_opaque_filename_octets_preserve_unusual_native_names(self):
        path = self.root / "odd ?\n雪.bin"
        write_file(path, b"\xff\x80opaque")
        source, _, _, _, _, result, before = self.pipeline(path)
        self.assertEqual(self.w.body(source)["object_kind"], "file")
        self.assertEqual(before, capture_object(path))
        self.assertEqual(self.w.body(result)["reason"], "incompatible-object-kind")

    def test_cli_fixture_path_emits_verified_unresolved_state_and_distinct_exit_status(self):
        fixture = self.root / "document"
        write_file(fixture, b'{"unknown":"structured document"}')
        output = (self.root / "cli").relative_to(REPO)
        completed = subprocess.run([
            sys.executable, "-B", str(REFERENCE / "frame_anything.py"),
            "--rapp1-path", str(self.core.path), "--fixture", str(fixture), "--output", str(output),
        ], cwd=REPO, capture_output=True, text=True, timeout=120)
        self.assertEqual(completed.returncode, 2, completed.stderr)
        for phase in ("SOURCE FINGERPRINT", "OPAQUE FRAME", "LENS DECLARATION", "DECLARED READS",
                      "REFUSAL / UNRESOLVED", "VERIFICATION", "SOURCE PRESERVATION / ANCESTRY"):
            self.assertIn("[" + phase + "]", completed.stdout)
        report = json.loads((REPO / output / "frame-anything-report.json").read_bytes())
        self.assertEqual(report["objects_framed"], 1)
        self.assertEqual(report["workspace_adoptions"], 0)
        self.assertEqual(report["unresolved_objects"], 1)
        self.assertEqual(report["scanner_verdict"], "COMPLIANT")
        self.assertTrue(report["framing_is_not_workspace_adoption"])

    def test_output_cannot_overlap_supplied_object_and_candidates_are_not_auto_adopted(self):
        root = self.root / "source"
        write_file(root / "x", b"x")
        write_file(root / "y", b"y")
        before = capture_object(root)
        with self.assertRaisesRegex(Refusal, "overlap"):
            run_frame_anything(self.core, root / "output", fixture=root, show=None)
        self.assertEqual(before, capture_object(root))
        report = run_frame_anything(self.core, self.root / "candidate", fixture=root, show=None)
        self.assertEqual(report["workspace_candidates"], 1)
        self.assertEqual(report["workspace_adoptions"], 0)
        self.assertEqual(report["projection"]["entries"], [])
