"""Synthetic first Workspace Grail/1 vectors. Requires explicitly supplied RAPP1_PATH."""

import copy
from dataclasses import replace
import hashlib
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
from common import Parent, Refusal, address, read_file, sha, wave, write_file
from pins import encode, historical_catalog, index_matches, manifest
from schema_source import CONTROL_DIR, PROFILE, schemas
from workspace import LocalConsent, Workspace, metadata_egg, migrate, plan_migration, snapshot

UTC = "2026-09-14T23:48:00.000Z"


class Fixture:
    def __init__(self, core, start=1):
        self.core, self.counter = core, start
        self.owner = self.mint("owner")
        self.identity = self.mint("workspace")
        self.w = Workspace(core, self.identity, "synthetic-world", LocalConsent(self.owner))
        self.w.birth(UTC)

    def mint(self, slug):
        # Reproducible UUIDv4 entropy is test-only. The canonical mint is unchanged.
        entropy = uuid.UUID(int=self.counter, version=4)
        self.counter += 1
        with patch.object(self.core.r.uuid, "uuid4", return_value=entropy):
            return self.core.r.mint_rappid("fictional", slug)

    def approve(self, payload):
        self.w.consent = replace(self.w.consent, decisions=self.w.consent.decisions |
                                {self.core.particle(payload)["hash"]})
        return self.w.append(payload, UTC)

    def observe(self, value="alpha", *, subject="node-a", tile=None, findings=(), stream=None):
        return self.w.observation(subject, "previously-unseen-shape",
                                  [{"name": "opaque-local-field", "value": value}], UTC,
                                  tile=tile, findings=findings, stream=stream)

    def project_lens(self, observation, *, name="local-purpose", proposer=None, synthesis="local-rule",
                     tick=0, contexts=False):
        program = {"op": "project", "tick": tick, "bindings": [
            {"name": name, "read": {"name": "observed-value", "input": 0, "pointer": "/metadata/0/value"}}]}
        if contexts:
            program["bindings"].append(
                {"name": "context", "read": {"name": "context-value", "input": 1, "pointer": "/metadata/0/value"}})
        return self.w.lens("candidate-local-lens", [observation], program, proposer or self.owner, UTC, synthesis)

    def identity_lens(self, observation):
        return self.w.lens("candidate-identity", [observation],
                           {"op": "identity", "read": {"name": "whole", "input": 0, "pointer": ""}},
                           self.owner, UTC)

    def trial(self, lens, sources, **kwargs):
        receipt = self.w.mutate(lens, sources, UTC, **kwargs)
        evidence = self.w.append(self.w.evidence_payload(receipt), UTC)
        return receipt, evidence, self.w.body(receipt)["successor"]

    def adopted(self, value="alpha", name="local-purpose"):
        source = self.observe(value)
        lens = self.project_lens(source, name=name)
        receipt, evidence, result = self.trial(lens, [source])
        self.approve(self.w.adoption_payload(lens, evidence))
        self.approve(self.w.adoption_payload(result, evidence))
        return source, lens, receipt, evidence, result

    def facts(self, facts, tick=0, stream=None):
        return self.w.append(self.w.payload("learned-projection", tick=tick,
                             facts=[{"name": name, "value": value} for name, value in facts],
                             native_compliance="unclaimed"), UTC, stream)


def build_demo(core):
    fixture = Fixture(core, 1000)
    w = fixture.w
    tile = w.append(w.scan_payload(["node-a", "node-b"], baseline_every=2), UTC)
    dimension = fixture.mint("dimension")
    child = w.dimension(dimension, tile, "learned-attention-unit", UTC)
    source = fixture.observe(tile=tile, findings=["unknown-shape"], stream=dimension)
    other = fixture.observe("beta", subject="node-b", tile=tile)
    report = w.append(w.report_payload(tile, [other, source]), UTC)
    follow = w.append(w.scan_payload(["node-a", "node-b"], previous=report, baseline_every=2), UTC)
    response = fixture.observe(tile=follow, stream=dimension)
    next_report = w.append(w.report_payload(follow, [response]), UTC)
    w.append(w.scan_payload(["node-a", "node-b"], previous=next_report, baseline_every=2), UTC)
    grandchild = fixture.mint("recursive-dimension")
    w.dimension(grandchild, child, "locally-discovered-subproblem", UTC)
    lens = fixture.project_lens(source, proposer=fixture.mint("model"), synthesis="model-candidate")
    receipt, evidence, result = fixture.trial(lens, [source])
    fixture.approve(w.adoption_payload(lens, evidence))
    fixture.approve(w.adoption_payload(result, evidence))
    fixture.approve(w.route_payload(result, "select"))
    fixture.approve(w.route_payload(result, "suppress"))
    branches = [fixture.mint("branch-" + str(i)) for i in range(2)]
    for branch in branches:
        w.dimension(branch, w.seed, "locally-grown-branch", UTC)
    left = fixture.facts([("observed-value", "beta"), ("stable", 1)], stream=branches[0])
    right = fixture.facts([("observed-value", "alpha"), ("stable", 1)], stream=branches[1])
    w.append(w.merge_payload([left], [right]), UTC)
    reads = w.body(receipt)["declared_reads"]
    w.append(w.reattach_payload(result, reads, [left, right]), UTC)
    w.append(w.reattach_payload(result, reads, [left]), UTC)
    copier = fixture.identity_lens(source)
    fixture.trial(copier, [lens])
    return fixture


class FrameLensTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.core = Parent(os.environ.get("RAPP1_PATH"))

    def setUp(self):
        parent = REPO / ".validation" / "test-artifacts"
        parent.mkdir(parents=True, exist_ok=True)
        self.root = parent / ("lens-" + uuid.uuid4().hex)
        self.root.mkdir()
        self.addCleanup(shutil.rmtree, self.root)
        self.fx = Fixture(self.core)
        self.w = self.fx.w

    def test_archived_20_bytes_are_exact_and_root_is_only_entry(self):
        raw = (REPO / "protocols/rapp-workspace/historical/pre-grail/2.0/SPEC.md").read_bytes()
        self.assertEqual((len(raw), sha(raw)), (10596, "86fe0ec4085e4f7bf33fe622519342bfed9f754ee4bdf45f41288129bf6e256c"))
        self.assertIn("first Grail", (REFERENCE.parent / "SPEC.md").read_text())
        self.assertNotEqual((REPO / "SPEC.md").read_bytes(), raw)

    def test_all_schemas_are_closed_bounded_and_reproducible(self):
        for filename, schema in schemas().items():
            self.assertEqual((REFERENCE.parent / "schemas" / filename).read_bytes(), encode(schema))
            def inspect(node):
                if isinstance(node, dict):
                    if node.get("type") == "object":
                        self.assertIs(node["additionalProperties"], False)
                        self.assertEqual(set(node["required"]), set(node["properties"]))
                    if node.get("type") == "array":
                        self.assertIn("maxItems", node)
                    if node.get("type") == "string":
                        self.assertIn("maxLength", node)
                    for child in node.values():
                        inspect(child)
                elif isinstance(node, list):
                    for child in node:
                        inspect(child)
            inspect(schema)

    def test_manifest_pins_every_normative_file_and_separates_authorities(self):
        value = manifest()
        self.assertEqual((REFERENCE.parent / "manifest.json").read_bytes(), encode(value))
        self.assertEqual({item["path"] for item in value["normative"]},
                         {"SPEC.md"} | {"schemas/" + name for name in schemas()})
        self.assertIs(value["authority"], False)
        self.assertEqual(value["parent"], "rapp/1")
        self.assertTrue(index_matches())
        self.assertEqual(value["profile"], "rapp-workspace/1.0")
        self.assertEqual(value["protocol_family"], "rapp-workspace/1")
        self.assertEqual(value["policy_status"], "first-grail-authority-candidate")
        self.assertIs(value["signed_grail_activation"], False)
        provenance = json.loads((REFERENCE.parent / "provenance.json").read_bytes())
        self.assertEqual(provenance["frame_chains"]["commit"], "0aeb8332f4bb20bc689aba217a704b463ba20105")
        self.assertFalse(provenance["frame_chains"]["copied_production_substrate"])

    def test_explicit_canonical_checkout_required_and_no_fallback(self):
        with self.assertRaisesRegex(Refusal, "explicit"):
            Parent(None)
        fake = self.root / "counterfeit-parent"
        fake.mkdir()
        (fake / "SPEC.md").write_bytes(b"substituted")
        with patch("common.subprocess.run") as runner:
            runner.return_value.stdout = self.core.pin["commit"]
            with self.assertRaisesRegex(Refusal, "byte substitution"):
                Parent(fake)

    def test_unique_seed_no_remint_no_fixed_taxonomy(self):
        before = self.w.checkpoint()
        with self.assertRaisesRegex(Refusal, "one seed"):
            self.w.birth(UTC)
        self.assertEqual(before, self.w.checkpoint())
        self.assertNotIn("providers", self.w.body(self.w.seed))
        self.assertNotIn("folders", self.w.body(self.w.seed))
        self.assertIs(self.w.body(self.w.seed)["fixed_taxonomy"], False)
        independent = Fixture(self.core, 100)
        self.assertNotEqual(independent.identity, self.fx.identity)
        self.assertNotEqual(independent.w.seed, self.w.seed)

    def test_different_machines_grow_different_local_vocabularies(self):
        self.fx.adopted("particle-lab", "arbitrary-local-constellation")
        other = Fixture(self.core, 100)
        other.adopted("garden", "a-new-purpose-not-in-the-protocol")
        self.assertNotEqual(self.w.projection(), other.w.projection())
        values = [self.w.body(entry["frame"])["facts"] for entry in self.w.projection()["entries"]]
        self.assertEqual(values[0][0]["name"], "arbitrary-local-constellation")

    def test_unknown_shape_is_opaque_unselected_and_unclaimed(self):
        source = self.fx.observe()
        payload = self.w.body(source)
        self.assertEqual(payload["source_state"], "opaque")
        self.assertEqual(payload["native_compliance"], "unclaimed")
        self.assertEqual(self.w.projection()["entries"], [])
        tampered = copy.deepcopy(payload)
        tampered["fingerprint"]["hash"] = "0" * 64
        with self.assertRaisesRegex(Refusal, "fingerprint"):
            self.w.append(tampered, UTC)

    def test_replay_and_negative_evidence_are_recomputed(self):
        source, lens, receipt, evidence, result = self.fx.adopted()
        self.assertEqual(self.w.body(evidence)["replays"][0], self.w.body(evidence)["replays"][1])
        self.assertEqual(self.w.body(result)["facts"][0]["value"], "alpha")
        self.assertEqual(len(self.w.frame(result)), 11)
        self.assertEqual(self.w.frame(result)["payload"]["schema"], PROFILE + "/derived-frame")
        forged = copy.deepcopy(self.w.body(evidence))
        forged["replays"][0]["hash"] = "f" * 64
        before = self.w.checkpoint()
        with self.assertRaisesRegex(Refusal, "evidence substitution"):
            self.w.append(forged, UTC)
        self.assertEqual(before, self.w.checkpoint())

    def test_incomplete_or_substituted_reads_refuse_before_any_frame(self):
        source = self.fx.observe()
        context = self.fx.observe("context", subject="node-b")
        lens = self.fx.project_lens(source, contexts=True)
        manifest = self.w.reads_payload(lens, [source], [context])
        for mutation in ("incomplete", "missing", "context", "read-value", "world"):
            bad = copy.deepcopy(manifest)
            if mutation == "incomplete":
                bad["complete"] = False
            elif mutation == "missing":
                bad["reads"].pop()
            elif mutation == "context":
                bad["contexts"] = []
            elif mutation == "read-value":
                bad["reads"][0]["value"]["hash"] = "0" * 64
            else:
                bad["world_id"] = "foreign"
            before = self.w.checkpoint()
            with self.subTest(mutation=mutation), self.assertRaises(Refusal):
                self.w.mutate(lens, [source], UTC, contexts=[context], declared=bad)
            self.assertEqual(before, self.w.checkpoint())

    def test_model_assistance_is_candidate_only_and_cannot_authorize_itself(self):
        source = self.fx.observe()
        lens = self.fx.project_lens(source, proposer=self.fx.owner, synthesis="model-candidate")
        receipt, evidence, result = self.fx.trial(lens, [source])
        payload = self.w.adoption_payload(lens, evidence)
        with self.assertRaisesRegex(Refusal, "independent local consent"):
            self.w.append(payload, UTC)
        with self.assertRaisesRegex(Refusal, "model cannot authorize"):
            self.fx.approve(payload)
        self.assertEqual(self.w.projection()["adopted"], [])
        independent = self.fx.project_lens(source, proposer=self.fx.mint("model"), synthesis="model-candidate")
        _, proof, _ = self.fx.trial(independent, [source])
        self.fx.approve(self.w.adoption_payload(independent, proof))
        self.assertIn(independent, self.w.projection()["adopted"])

    def test_output_requires_adopted_lens_and_exact_cas(self):
        source = self.fx.observe()
        lens = self.fx.project_lens(source)
        _, evidence, result = self.fx.trial(lens, [source])
        stale = self.w.adoption_payload(result, evidence)
        with self.assertRaisesRegex(Refusal, "not adopted"):
            self.fx.approve(stale)
        self.fx.approve(self.w.adoption_payload(lens, evidence))
        with self.assertRaisesRegex(Refusal, "CAS"):
            self.fx.approve(stale)
        self.fx.approve(self.w.adoption_payload(result, evidence))

    def test_source_preservation_receipts_and_forbidden_native_io_canaries(self):
        native = self.root / "synthetic-native"
        native.mkdir()
        (native / "not-observable.txt").write_bytes(b"SYNTHETIC SECRET MUST NEVER BE READ BY LENS")
        before_native = snapshot(native)
        source = self.fx.observe()
        lens = self.fx.project_lens(source)
        source_raw = self.w._raw[address(source)]
        original_reader = read_file
        def guarded(path, *args, **kwargs):
            self.assertFalse(Path(path).is_relative_to(native), "native content read")
            return original_reader(path, *args, **kwargs)
        with patch("workspace.read_file", guarded):
            receipt, _, result = self.fx.trial(lens, [source])
        self.assertEqual(before_native, snapshot(native))
        self.assertEqual(source_raw, self.w._raw[address(source)])
        entry = next(e for e in self.w.body(receipt)["preservation"] if e["frame"] == source)
        self.assertEqual(entry["before_sha256"], entry["after_sha256"])
        self.assertNotIn(b"SYNTHETIC SECRET", self.core.octets(self.w.body(result)))
        copy_of_source = self.w.frame(source)
        copy_of_source["payload"]["shape"] = "changed"
        self.assertNotEqual(copy_of_source, self.w.frame(source))
        forged = copy.deepcopy(self.w.body(receipt))
        forged["preservation"][0]["after_sha256"] = "0" * 64
        with self.assertRaisesRegex(Refusal, "preservation"):
            self.w.append(forged, UTC)

    def test_recursive_lens_on_lens_can_evolve_and_run_new_lens(self):
        source, original, _, _, _ = self.fx.adopted()
        modifier = self.w.lens("learned-lens-modifier", [source], {
            "op": "amend", "read": {"name": "whole", "input": 0, "pointer": ""},
            "changes": [{"pointer": "/label", "value": "new-local-lens"}]}, self.fx.owner, UTC)
        _, evidence, evolved = self.fx.trial(modifier, [original])
        self.fx.approve(self.w.adoption_payload(modifier, evidence))
        self.fx.approve(self.w.adoption_payload(evolved, evidence))
        self.assertEqual(self.w.body(evolved)["label"], "new-local-lens")
        self.assertEqual(self.w.body(original)["label"], "candidate-local-lens")
        _, _, result = self.fx.trial(evolved, [source])
        self.assertEqual(self.w.body(result)["facts"][0]["value"], "alpha")
        copier = self.fx.identity_lens(source)
        prior = original
        ancestry = set(self.w._raw)
        for _ in range(16):
            _, _, prior = self.fx.trial(copier, [prior])
        self.assertEqual(self.w.body(prior), self.w.body(original))
        self.assertTrue(ancestry <= self.w._raw.keys())

    def test_any_seed_or_control_frame_can_pass_a_lens_without_reauthorizing(self):
        source = self.fx.observe()
        copier = self.fx.identity_lens(source)
        seed = copy.deepcopy(self.w.seed)
        _, _, result = self.fx.trial(copier, [seed])
        self.assertEqual(self.w.seed, seed)
        self.assertEqual(self.w.body(result), self.w.body(seed))
        self.assertEqual(self.w.projection()["adopted"], [])

    def test_immutable_boundaries_and_unknown_programs_refuse(self):
        source = self.fx.observe()
        for key in ("world_id", "estate_rappid", "seed", "schema", "generation", "proposer_rappid", "synthesis"):
            lens = self.w.lens("bad-modifier", [source], {
                "op": "amend", "read": {"name": "whole", "input": 0, "pointer": ""},
                "changes": [{"pointer": "/" + key, "value": "replacement"}]}, self.fx.owner, UTC)
            before = self.w.checkpoint()
            with self.subTest(key=key), self.assertRaisesRegex(Refusal, "immutable"):
                self.w.mutate(lens, [source], UTC)
            self.assertEqual(before, self.w.checkpoint())
        bad = self.w.payload("lens-declaration", label="code-is-not-a-lens", proposer_rappid=self.fx.owner,
                             synthesis="model-candidate", observations=[source],
                             runtime_sha256=self.w.runtime_hash(), program={"op": "shell", "command": "ignored"})
        with self.assertRaises(Refusal):
            self.w.append(bad, UTC)

    def test_runtime_and_lens_drift_block_future_use_preserving_history(self):
        source, lens, receipt, evidence, result = self.fx.adopted()
        original = dict(self.w._raw)
        drift = self.w.payload("lens-drift", lens=lens, trial=receipt, replacement=None, reason="input-changed")
        with self.assertRaisesRegex(Refusal, "consent"):
            self.w.append(drift, UTC)
        self.fx.approve(drift)
        with self.assertRaisesRegex(Refusal, "suspended"):
            self.w.mutate(lens, [source], UTC)
        self.assertTrue(all(self.w._raw[k] == raw for k, raw in original.items()))
        fresh = self.fx.project_lens(source)
        with patch.object(Workspace, "runtime_hash", return_value="0" * 64):
            with self.assertRaisesRegex(Refusal, "runtime drift"):
                self.w.mutate(fresh, [source], UTC)

    def test_scan_tile_exhaust_delta_missing_and_periodic_baseline(self):
        tile = self.w.append(self.w.scan_payload(["node-a", "node-b", "node-c"], baseline_every=2), UTC)
        a = self.fx.observe(tile=tile, findings=["drift"])
        b = self.fx.observe(subject="node-b", tile=tile)
        report = self.w.append(self.w.report_payload(tile, [b, a]), UTC)
        self.assertEqual(self.w.body(report)["missing"], ["node-c"])
        follow = self.w.scan_payload(["node-a", "node-b", "node-c"], previous=report, baseline_every=2)
        self.assertEqual(follow["targets"], ["node-a", "node-c"])
        self.assertEqual(follow["mode"], "delta")
        wrong = copy.deepcopy(follow)
        wrong["targets"] = ["node-a", "node-b", "node-c"]
        with self.assertRaisesRegex(Refusal, "delta"):
            self.w.append(wrong, UTC)
        next_tile = self.w.append(follow, UTC)
        responses = [self.fx.observe(subject=name, tile=next_tile) for name in follow["targets"]]
        next_report = self.w.append(self.w.report_payload(next_tile, responses), UTC)
        baseline = self.w.scan_payload(follow["scope"], previous=next_report, baseline_every=2)
        self.assertEqual((baseline["mode"], baseline["targets"]), ("baseline", follow["scope"]))
        self.assertEqual(baseline["last_baseline_tick"], 2)

    def test_unchanged_subjects_have_zero_followup_and_signals_add_only_delta(self):
        tile = self.w.append(self.w.scan_payload(["node-a", "node-b"]), UTC)
        responses = [self.fx.observe(subject=name, tile=tile) for name in ["node-a", "node-b"]]
        report = self.w.append(self.w.report_payload(tile, responses), UTC)
        self.assertEqual(self.w.scan_payload(["node-a", "node-b"], previous=report)["targets"], [])
        self.assertEqual(self.w.scan_payload(["node-a", "node-b"], ["node-b"], report)["targets"], ["node-b"])
        with self.assertRaisesRegex(Refusal, "outside"):
            self.w.scan_payload(["node-a"], ["unapproved"])

    def test_reports_are_deterministic_and_refuse_duplicates_or_false_health(self):
        tile = self.w.append(self.w.scan_payload(["node-a", "node-b"]), UTC)
        a, b = self.fx.observe(tile=tile), self.fx.observe(subject="node-b", tile=tile)
        self.assertEqual(self.w.report_payload(tile, [a, b]), self.w.report_payload(tile, [b, a]))
        with self.assertRaisesRegex(Refusal, "duplicate"):
            self.w.report_payload(tile, [a, a])
        false = self.w.report_payload(tile, [a])
        false.update(complete=True, missing=[], exhaust=[])
        with self.assertRaisesRegex(Refusal, "report substitution"):
            self.w.append(false, UTC)

    def test_recursive_dimensions_chain_clock_and_late_attachment(self):
        parent = self.w.seed
        initial = self.w._raw[address(parent)]
        for depth in range(1, 5):
            stream = self.fx.mint("drill-" + str(depth))
            parent = self.w.dimension(stream, parent, "opaque-local-problem", UTC)
            self.assertEqual(self.w.body(parent)["depth"], depth)
        late_stream = self.fx.mint("late")
        late = self.w.dimension(late_stream, self.w.seed, "arrives-later", "2026-09-14T23:47:00.000Z")
        self.assertEqual(self.w._raw[address(self.w.seed)], initial)
        self.assertLess(self.w.frame(late)["utc"], self.w.frame(self.w.seed)["utc"])
        with self.assertRaisesRegex(Refusal, "utc"):
            self.w.append(self.w.payload("learned-projection", tick=1,
                          facts=[{"name": "clock", "value": 1}], native_compliance="unclaimed"),
                          "2026-09-14T23:46:00.000Z", late_stream)

    def test_dimension_merge_preserves_all_branches_and_exact_fidelity(self):
        branches = [self.fx.mint("branch-" + str(i)) for i in range(2)]
        ancestors = [self.w.dimension(branch, self.w.seed, "independent-local-history", UTC) for branch in branches]
        left = self.fx.facts([("a", 1), ("b", 2), ("conflict", "left"), ("one-sided", True)], stream=branches[0])
        right = self.fx.facts([("a", 1), ("b", 2), ("conflict", "right")], stream=branches[1])
        p = self.w.merge_payload([left], [right])
        self.assertEqual((p["numerator"], p["denominator"]), (2, 3))
        self.assertEqual(p["conflicts"], ["conflict"])
        self.assertEqual({address(x) for x in p["retained"]}, {address(left), address(right)})
        good = self.w.append(p, UTC)
        forged = copy.deepcopy(p)
        forged["retained"] = [left]
        with self.assertRaisesRegex(Refusal, "retained conflict"):
            self.w.append(forged, UTC)
        unique = self.fx.facts([("different", 3)])
        self.assertTrue(self.w.merge_payload([left], [unique])["no_shared_dimensions"])
        self.assertEqual(self.w.body(good), p)
        self.assertTrue(all(address(ref) in self.w._raw for ref in ancestors))

    def test_reattach_first_exact_noncontradiction_and_dry_hole_no_routing(self):
        _, _, receipt, _, result = self.fx.adopted()
        reads = self.w.body(receipt)["declared_reads"]
        bad = self.fx.facts([("observed-value", "wrong")])
        good = self.fx.facts([("observed-value", "alpha")])
        extra = self.fx.facts([("different", "unrelated")])
        before = self.w.projection()["entries"]
        proposed = self.w.reattach_payload(result, reads, [bad, good, extra])
        self.assertEqual(proposed["selected"], good)
        self.assertEqual(len(proposed["comparisons"]), 2)
        self.w.append(proposed, UTC)
        dry = self.w.reattach_payload(result, reads, [bad])
        self.assertEqual((dry["status"], dry["selected"]), ("dry-hole", None))
        self.w.append(dry, UTC)
        self.assertEqual(before, self.w.projection()["entries"])
        forged = copy.deepcopy(proposed)
        forged["selected"] = extra
        with self.assertRaisesRegex(Refusal, "reattach"):
            self.w.append(forged, UTC)

    def test_one_way_membrane_requires_exact_public_input_and_never_exports_private(self):
        other = Fixture(self.core, 500)
        public = other.observe("public-fixture")
        with self.assertRaisesRegex(Refusal, "membrane"):
            self.w.membrane(other.w, public, "inbound-public")
        self.w.consent = replace(self.w.consent, public_reads=frozenset({address(public)}))
        before = self.w.checkpoint()
        self.assertEqual(self.w.membrane(other.w, public, "inbound-public"), other.w._raw[address(public)])
        self.assertEqual(before, self.w.checkpoint())
        for direction in ("outbound-private", "outbound-dogg", "inbound-unverified"):
            with self.subTest(direction=direction), self.assertRaisesRegex(Refusal, "membrane"):
                self.w.membrane(other.w, public, direction)

    def test_registry_rebuild_restart_and_sticky_suppression(self):
        _, _, _, _, result = self.fx.adopted()
        self.fx.approve(self.w.route_payload(result, "select"))
        self.fx.approve(self.w.route_payload(result, "suppress"))
        with self.assertRaisesRegex(Refusal, "suppression wins"):
            self.fx.approve(self.w.route_payload(result, "select"))
        destination = self.root / "estate"
        self.w.save(destination)
        checkpoint = self.w.checkpoint()
        expected = self.core.octets(self.w.projection())
        (destination / "registry.json").write_bytes(b"not trusted JSON")
        restored = Workspace.load(self.core, destination, self.w.consent, checkpoint)
        self.assertEqual(self.core.octets(restored.projection()), expected)
        restored.save(destination)
        self.assertEqual((destination / "registry.json").read_bytes(), expected)
        (destination / "registry.json").unlink()
        restarted = Workspace.load(self.core, destination, self.w.consent, checkpoint)
        self.assertTrue(restarted.projection()["entries"][0]["suppressed"])
        with self.assertRaisesRegex(Refusal, "consent"):
            Workspace.load(self.core, destination, LocalConsent(self.fx.owner), checkpoint)
        self.fx.w = self.w = restarted
        self.fx.approve(self.w.route_payload(result, "re-add"))
        self.assertFalse(self.w.projection()["entries"][0]["selected"])

    def test_fresh_process_reconstructs_registry_from_history_and_external_consent(self):
        _, _, _, _, result = self.fx.adopted()
        self.fx.approve(self.w.route_payload(result, "suppress"))
        destination = self.root / "estate"
        self.w.save(destination)
        (destination / "registry.json").write_bytes(b"UNTRUSTED CACHE")
        checkpoint = self.root / "protected-checkpoint.json"
        consent = self.root / "owner-consent.json"
        checkpoint.write_bytes(self.core.octets(self.w.checkpoint()))
        consent.write_bytes(self.core.octets({"owner": self.w.consent.owner,
                                            "decisions": sorted(self.w.consent.decisions)}))
        script = """
import sys
sys.path.insert(0, sys.argv[1])
from common import Parent, read_file
from workspace import LocalConsent, Workspace
p = Parent(sys.argv[2])
c = p.parse(read_file(sys.argv[4]))
w = Workspace.load(p, sys.argv[3], LocalConsent(c['owner'], frozenset(c['decisions'])),
                   p.parse(read_file(sys.argv[5])))
print(p.r.canonical(w.projection()))
"""
        completed = subprocess.run(
            [sys.executable, "-B", "-c", script, str(REFERENCE), str(self.core.path),
             str(destination), str(consent), str(checkpoint)], capture_output=True, timeout=60)
        self.assertEqual(completed.returncode, 0, completed.stderr.decode())
        self.assertEqual(completed.stdout.rstrip(b"\n"), self.core.octets(self.w.projection()))
        self.assertEqual((destination / "registry.json").read_bytes(), b"UNTRUSTED CACHE")

    def test_shareable_skill_matches_project_entry_and_keeps_normative_contracts_separate(self):
        raw = (REPO / "SKILL.md").read_bytes()
        self.assertEqual(raw, (REPO / ".github/skills/rapp-workspace/SKILL.md").read_bytes())
        for capability in (b"frame_lens.py", b"workspace_manager.py", b"append_frame.py",
                           b"prepare_workspace.py", b"deploy_hive.py", b"metadata_egg"):
            self.assertIn(capability, raw)
        self.assertIn(b"protocols/rapp-workspace/grail-1.0/SPEC.md", raw)
        self.assertNotIn(b'"$schema":', raw)

    def test_tamper_path_identity_rollback_and_checkpoint_loss_refuse(self):
        self.fx.adopted()
        destination = self.root / "estate"
        self.w.save(destination)
        checkpoint = self.w.checkpoint()
        with self.assertRaisesRegex(Refusal, "protected checkpoint"):
            Workspace.load(self.core, destination, self.w.consent, None)
        raw = (destination / "history.jsonl").read_bytes()
        (destination / "history.jsonl").write_bytes(raw.splitlines()[0] + b"\n")
        with self.assertRaisesRegex(Refusal, "rollback"):
            Workspace.load(self.core, destination, self.w.consent, checkpoint)
        (destination / "history.jsonl").write_bytes(raw)
        identity = self.core.parse((destination / "rappid.json").read_bytes())
        identity["rappid"] = self.fx.mint("impostor")
        (destination / "rappid.json").write_bytes(self.core.octets(identity))
        with self.assertRaisesRegex(Refusal, "identity"):
            Workspace.load(self.core, destination, self.w.consent, checkpoint)

    def test_same_stream_fork_retains_both_branches_and_survives_restart(self):
        stream = self.fx.mint("dimension")
        genesis = self.w.dimension(stream, self.w.seed, "branch", UTC)
        left = self.fx.facts([("k", "left")], stream=stream)
        payload = self.w.payload("learned-projection", tick=0, facts=[{"name": "k", "value": "right"}],
                                 native_compliance="unclaimed")
        rival = self.core.r.build_frame("body.pulse", stream, 1, UTC, payload,
                                        self.w.frame(genesis)["payload_hash"])
        with self.assertRaisesRegex(Refusal, "stream-fork"):
            self.w.ingest(self.core.octets(rival))
        self.assertIn(rival["frame_hash"], self.w._raw)
        self.assertIn(address(left), self.w._raw)
        for ref in (left, wave(rival)):
            with self.assertRaisesRegex(Refusal, "forked"):
                self.w.frame(ref)
        destination = self.root / "fork"
        self.w.save(destination)
        restored = Workspace.load(self.core, destination, self.w.consent, self.w.checkpoint())
        self.assertEqual(restored._faults, self.w._faults)
        with self.assertRaisesRegex(Refusal, "forked"):
            restored.frame(left)
        self.assertIn(rival["frame_hash"], restored._raw)

    def test_frame_hash_envelope_and_world_substitutions_refuse(self):
        frame = self.w.frame(self.w.seed)
        for changed in ("payload", "hash", "envelope", "identity", "world", "sig"):
            raw = copy.deepcopy(frame)
            if changed == "payload":
                raw["payload"]["local_only"] = False
            elif changed == "hash":
                raw["frame_hash"] = "0" * 64
            elif changed == "envelope":
                raw["alternative_identity"] = "not a field"
            elif changed == "sig":
                raw["sig"] = "invalid"
            else:
                p = self.w.payload("learned-projection", tick=0, facts=[{"name": "k", "value": 1}],
                                   native_compliance="unclaimed")
                p["world_id" if changed == "world" else "estate_rappid"] = "foreign"
                raw = self.core.r.build_frame("body.pulse", self.fx.identity, 1, UTC, p, frame["payload_hash"])
            with self.subTest(changed=changed), self.assertRaises(Refusal):
                self.w.ingest(self.core.octets(raw))

    def test_links_hardlinks_escape_and_portable_path_vectors(self):
        real = self.root / "real"
        real.mkdir()
        (real / "file").write_bytes(b"data")
        linked = self.root / "alias"
        linked.symlink_to(real, target_is_directory=True)
        with self.assertRaises((Refusal, OSError)):
            read_file(linked / "file")
        hardlink = real / "hardlink"
        os.link(real / "file", hardlink)
        with self.assertRaisesRegex(Refusal, "hardlink"):
            read_file(hardlink)
        with self.assertRaisesRegex(Refusal, "escape"):
            write_file(self.root / ".." / "not-allowed", b"never")
        path_schema = self.core.schemas.documents["common.schema.json"]["$defs"]["path"]
        for value in ("../x", "/absolute", "C:/x", "a//b", "a/./b", "a\\b", "CON", "a/NUL.txt", "a.", "a\n"):
            with self.subTest(value=value), self.assertRaises(Refusal):
                self.core.schemas._check(value, path_schema)
        for value in ("a", CONTROL_DIR, "safe/metadata.json"):
            self.core.schemas._check(value, path_schema)

    def legacy_fixture(self, version="2.0"):
        legacy = self.root / ("legacy-" + version)
        legacy.mkdir()
        identity = {"schema": "rapp/1", "rappid": self.fx.identity, "world_id": self.w.world,
                    "workspace_spec": "rapp-workspace/" + version, "frames": "frames/"}
        (legacy / "rappid.json").write_text(json.dumps(identity, indent=2) + "\n")
        (legacy / "registry.json").write_text(json.dumps({
            "paths": ["fixtures/unchanged-native"], "suppressed": ["unknown-native-id"],
            "providers": {"previously-unmodeled": {"opaque": "KEEP EXACT BYTES"}}}, indent=2))
        (legacy / "source.txt").write_bytes(b"synthetic local source, never moved")
        (legacy / "link").symlink_to("source.txt")
        frames = []
        head = None
        (legacy / "frames").mkdir()
        for index in range(2):
            head = self.core.r.build_frame("body.pulse", self.fx.identity, index, UTC,
                                           {"legacy_event": index}, head["payload_hash"] if head else None)
            raw = self.core.octets(head)
            frames.append(raw)
            (legacy / "frames" / f"{index}.json").write_bytes(raw)
        return legacy, frames

    def migration_selection(self, frames, version="2.0"):
        pins = {
            "1.0": None,
            "1.1": "869d34e77a909365c844d239d6c8cdd0e70476a0fa4d828f7d58ec9b65c0e1a8",
            "2.0": "86fe0ec4085e4f7bf33fe622519342bfed9f754ee4bdf45f41288129bf6e256c",
        }
        return {"source_generation": "pre-grail", "source_spec": "rapp-workspace/" + version,
                "source_spec_sha256": pins[version], "legacy_frames": frames}

    def authorize_migration(self, legacy, selection):
        proposal = plan_migration(self.core, legacy, self.w.consent, UTC, **selection)
        return replace(self.w.consent, decisions=self.w.consent.decisions |
                       {self.core.particle(proposal)["hash"]})

    def test_20_migration_additive_exact_identity_path_source_suppression_and_history(self):
        legacy, frames = self.legacy_fixture()
        before = snapshot(legacy)
        registry = (legacy / "registry.json").read_bytes()
        selection = self.migration_selection(frames)
        consent = self.authorize_migration(legacy, selection)
        result = migrate(self.core, legacy, consent, UTC, **selection)
        self.assertEqual(result.estate, self.fx.identity)
        self.assertEqual(result.world, self.w.world)
        self.assertEqual(result.frame(result.seed)["seq"], 2)
        self.assertEqual(result.body(result.seed)["inherited_heads"], [wave(self.core.parse(frames[-1]))])
        self.assertEqual(before, snapshot(legacy))
        self.assertEqual((legacy / "registry.json").read_bytes(), registry)
        receipt = result.body(result._migration)
        self.assertEqual(receipt["legacy_registry_sha256"], sha(registry))
        again = migrate(self.core, legacy, consent, UTC, **selection, checkpoint=result.checkpoint())
        self.assertEqual(result.checkpoint(), again.checkpoint())
        self.assertIsNotNone(again.projection()["migration"])
        self.assertEqual(again.projection()["entries"], [])

    def test_migration_missing_history_changed_baseline_and_unsafe_sidecar_refuse(self):
        legacy, frames = self.legacy_fixture()
        selection = self.migration_selection(frames)
        with self.assertRaisesRegex(Refusal, "complete explicit legacy"):
            migrate(self.core, legacy, self.w.consent, UTC, **self.migration_selection([]))
        self.assertFalse((legacy / CONTROL_DIR).exists())
        consent = self.authorize_migration(legacy, selection)
        result = migrate(self.core, legacy, consent, UTC, **selection)
        (legacy / "registry.json").write_bytes(b'{"suppressed":["newer-decision"]}')
        with self.assertRaisesRegex(Refusal, "baseline changed"):
            migrate(self.core, legacy, consent, UTC, **selection, checkpoint=result.checkpoint())
        self.assertEqual((legacy / "registry.json").read_bytes(), b'{"suppressed":["newer-decision"]}')

    def test_all_pre_grail_source_versions_migrate_only_by_exact_owner_plan(self):
        for version in ("1.0", "1.1", "2.0"):
            with self.subTest(version=version):
                legacy, frames = self.legacy_fixture(version)
                selection = self.migration_selection(frames, version)
                before = snapshot(legacy)
                plan = plan_migration(self.core, legacy, self.w.consent, UTC, **selection)
                self.assertEqual(plan["source_generation"], "pre-grail")
                self.assertEqual(plan["generation"], "grail")
                self.assertEqual(before, snapshot(legacy))
                self.assertFalse((legacy / CONTROL_DIR).exists())
                with self.assertRaisesRegex(Refusal, "consent"):
                    migrate(self.core, legacy, self.w.consent, UTC, **selection)
                consent = self.authorize_migration(legacy, selection)
                result = migrate(self.core, legacy, consent, UTC, **selection)
                self.assertEqual(before, snapshot(legacy))
                self.assertEqual(result.body(result._migration), plan)
                self.assertEqual(result.frame(result.seed)["seq"], len(frames))
                identity = self.core.parse((legacy / CONTROL_DIR / "rappid.json").read_bytes())
                self.assertEqual(identity["workspace_spec"], PROFILE)
                self.assertEqual(identity["workspace_generation"], "grail")

    def test_historical_public_bytes_and_labels_are_not_current_grail_authority(self):
        catalog = historical_catalog()
        self.assertEqual(len(catalog["files"]), 8)
        self.assertFalse(catalog["authority"])
        for entry in catalog["files"]:
            raw = subprocess.check_output(["git", "show", entry["source_commit"] + ":" + entry["source_path"]], cwd=REPO)
            self.assertEqual(raw, (REPO / entry["path"]).read_bytes())
        index = json.loads((REPO / "protocols/index.json").read_bytes())
        active = [p for p in index["profiles"] if p["name"].startswith("rapp-workspace/")]
        self.assertEqual([p["name"] for p in active], ["rapp-workspace/grail-1.0"])
        self.assertEqual(active[0]["generation"], "first-grail")
        self.assertTrue(all(not item["authority"] for item in index["legacy_workspace_inputs"]))

    def test_reused_10_label_cannot_silently_reclassify_a_grail_estate(self):
        destination = self.root / "grail"
        self.w.save(destination)
        with self.assertRaisesRegex(Refusal, "pre-Grail migration lane"):
            plan_migration(self.core, destination, self.w.consent, UTC, **self.migration_selection([], "1.0"))
        legacy, frames = self.legacy_fixture("1.0")
        selection = self.migration_selection(frames, "1.0")
        with self.assertRaisesRegex(Refusal, "explicit pre-Grail"):
            plan_migration(self.core, legacy, self.w.consent, UTC, **{**selection, "source_generation": "grail"})
        with self.assertRaisesRegex(Refusal, "unavailable"):
            plan_migration(self.core, legacy, self.w.consent, UTC,
                           **{**selection, "source_spec_sha256": sha((REFERENCE.parent / "SPEC.md").read_bytes())})
        self.assertFalse((legacy / CONTROL_DIR).exists())

    def test_legacy_without_version_marker_requires_explicit_known_source_and_world(self):
        legacy, frames = self.legacy_fixture("1.1")
        identity = json.loads((legacy / "rappid.json").read_bytes())
        identity.pop("workspace_spec")
        identity.pop("schema")
        (legacy / "rappid.json").write_text(json.dumps(identity))
        selection = self.migration_selection(frames, "1.1")
        consent = self.authorize_migration(legacy, selection)
        result = migrate(self.core, legacy, consent, UTC, **selection)
        self.assertEqual(result.world, identity["world_id"])
        identity.pop("world_id")
        (legacy / "rappid.json").write_text(json.dumps(identity))
        with self.assertRaisesRegex(Refusal, "existing world_id required"):
            plan_migration(self.core, legacy, consent, UTC, **selection)

    def test_grail_generation_is_required_without_changing_the_frame_envelope(self):
        source = self.fx.observe()
        payload = self.w.body(source)
        self.assertEqual(payload["generation"], "grail")
        for changed in (None, "pre-grail"):
            altered = dict(payload)
            if changed is None:
                altered.pop("generation")
            else:
                altered["generation"] = changed
            with self.assertRaises(Refusal):
                self.w.append(altered, UTC)
        self.assertEqual(len(self.w.frame(source)), 11)
        with self.assertRaises(Refusal):
            self.w.append({**payload, "signed_grail_activation": True}, UTC)

    def test_pre_grail_payload_labels_remain_inert_during_migration(self):
        legacy, frames = self.legacy_fixture("1.0")
        old = self.core.parse(frames[1])
        old["payload"] = {"schema": PROFILE + "/verification-adoption",
                          "generation": "pre-grail", "decision": "adopt", "candidate": "not-authority"}
        old = self.core.r.build_frame(old["kind"], old["stream_id"], old["seq"], old["utc"],
                                      old["payload"], old["prev"])
        frames[1] = self.core.octets(old)
        (legacy / "frames/1.json").write_bytes(frames[1])
        selection = self.migration_selection(frames, "1.0")
        consent = self.authorize_migration(legacy, selection)
        result = migrate(self.core, legacy, consent, UTC, **selection)
        self.assertEqual(result.projection()["adopted"], [])
        self.assertIsNone(result._adoption_head)
        self.assertEqual(result._raw[old["frame_hash"]], frames[1])
        self.fx.w = self.w = result
        observed = self.fx.observe()
        lens = self.fx.identity_lens(observed)
        _, _, derivative = self.fx.trial(lens, [wave(old)])
        self.assertEqual(self.w.body(derivative), old["payload"])
        with self.assertRaisesRegex(Refusal, "generation"):
            self.w.body(derivative, "verification-adoption")

    def test_source_spec_pins_bind_exact_archived_variants_not_labels(self):
        legacy, frames = self.legacy_fixture()
        selected = self.migration_selection(frames)
        initial = next(e for e in historical_catalog()["files"] if
                       e["label"] == "rapp-workspace/2.0" and "/revisions/" in e["path"])
        plan = plan_migration(self.core, legacy, self.w.consent, UTC,
                              **{**selected, "source_spec_sha256": initial["sha256"]})
        self.assertEqual(plan["source_spec_sha256"], initial["sha256"])
        for value in (None, "0" * 64, self.migration_selection([], "1.1")["source_spec_sha256"]):
            with self.assertRaisesRegex(Refusal, "source specification pin"):
                plan_migration(self.core, legacy, self.w.consent, UTC,
                               **{**selected, "source_spec_sha256": value})
        self.assertFalse((legacy / CONTROL_DIR).exists())

    def test_metadata_only_native_estate_egg_is_inert_and_round_trips(self):
        self.fx.adopted()
        ids = [self.fx.mint("metadata-" + str(i)) for i in range(3)]
        egg, receipt = metadata_egg(self.w, ids, UTC)
        self.assertTrue(self.core.r.verify_egg(egg)[0])
        manifest, files = self.core.r.read_egg(egg)
        _, middle = self.core.r.read_egg(next(iter(files.values())))
        _, inner = self.core.r.read_egg(next(iter(middle.values())))
        self.assertEqual(inner["state/registry-projection.json"], self.core.octets(self.w.projection()))
        self.assertEqual(set(inner), {"state/registry-projection.json", "rappid.json", "soul.md"})
        self.assertEqual(receipt["egg"]["hash"], self.core.r.egg_address(manifest))
        self.assertEqual(receipt["publication"], "not-authorized")
        self.assertEqual(egg, metadata_egg(self.w, ids, UTC)[0])
        self.assertFalse(self.core.r.verify_egg(egg + b"unbound")[0])

    def test_canonical_json_depth_numbers_extra_fields_and_bounds_refuse(self):
        for raw in (b'{"a":1,"a":2}', b'{"a": 1}', b'{"a":1.0}', b'{"a":NaN}', b'{"a":9007199254740993}'):
            with self.subTest(raw=raw), self.assertRaises(Refusal):
                self.core.parse(raw)
        payload = self.w.payload("learned-projection", tick=0, facts=[{"name": "k", "value": 1}],
                                 native_compliance="unclaimed")
        for change in ({"unexpected": True}, {"tick": True}, {"world_id": "x" * 129},
                       {"facts": [{"name": "k", "value": "x" * 1025}]},
                       {"facts": [{"name": "k\n", "value": 1}]}):
            with self.subTest(change=change), self.assertRaises(Refusal):
                self.w.append({**payload, **change}, UTC)

    def test_retained_memory_and_disk_frame_tamper_cannot_feed_fresh_lens(self):
        source = self.fx.observe()
        lens = self.fx.project_lens(source)
        self.w.frame(source)
        original = self.w._raw[address(source)]
        tampered = self.core.parse(original)
        tampered["payload"]["metadata"][0]["value"] = "substituted"
        self.w._raw[address(source)] = self.core.octets(tampered)
        with self.assertRaisesRegex(Refusal, "tamper"):
            self.w.reads_payload(lens, [source])
        self.w._raw[address(source)] = original
        destination = self.root / "estate"
        self.w.save(destination)
        path = next(p for p in (destination / "streams").glob("*/frames/*.json") if p.read_bytes() == original)
        path.write_bytes(self.core.octets(tampered))
        with self.assertRaisesRegex(Refusal, "stored frame tamper"):
            Workspace.load(self.core, destination, self.w.consent, self.w.checkpoint())

    def test_supplied_manifest_must_bind_the_actual_mutation_arguments(self):
        source = self.fx.observe()
        alternate = self.fx.observe("other")
        lens = self.fx.project_lens(source)
        manifest = self.w.reads_payload(lens, [alternate])
        before = self.w.checkpoint()
        with self.assertRaisesRegex(Refusal, "arguments"):
            self.w.mutate(lens, [source], UTC, declared=manifest)
        self.assertEqual(before, self.w.checkpoint())

    def test_lens_itself_can_be_its_own_inert_source_without_losing_preservation(self):
        source = self.fx.observe()
        lens = self.fx.identity_lens(source)
        receipt, _, result = self.fx.trial(lens, [lens])
        self.assertEqual(self.w.body(result), self.w.body(lens))
        self.assertEqual(len(self.w.body(receipt)["preservation"]), 1)

    def test_existing_source_codepoints_are_preserved_not_normalized_by_lens(self):
        observation = self.fx.observe()
        lens = self.fx.identity_lens(observation)
        source = self.w.append({"retained_opaque_string": "e\u0301"}, UTC)
        original = self.w._raw[address(source)]
        _, _, result = self.fx.trial(lens, [source])
        self.assertEqual(self.w.body(result)["retained_opaque_string"], "e\u0301")
        self.assertNotEqual(self.w.body(result)["retained_opaque_string"], "é")
        self.assertEqual(self.w._raw[address(source)], original)

    def test_projection_stream_budget_defers_without_pruning_ancestors(self):
        for i in range(127):
            stream = self.fx.mint("bounded-" + str(i))
            self.w.dimension(stream, self.w.seed, "bounded-local-dimension", UTC)
        before = self.w.checkpoint()
        self.assertEqual(len(self.w.projection()["heads"]), 128)
        with self.assertRaisesRegex(Refusal, "stream budget"):
            self.w.dimension(self.fx.mint("over-budget"), self.w.seed, "no-silent-pruning", UTC)
        self.assertEqual(before, self.w.checkpoint())


if __name__ == "__main__":
    unittest.main()
