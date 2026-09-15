"""Blocking P0/P1 Workspace/1 core vectors. Public synthetic data only."""

import copy
from dataclasses import replace
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import unittest
from unittest.mock import patch
import uuid

REPO = Path(__file__).resolve().parents[1]
REFERENCE = REPO / "protocols/rapp-workspace/1/reference"
sys.path.insert(0, str(REFERENCE))
from common import Parent, Refusal, read_file, sha, wave
from pins import encode, manifest, check_index
from schema_source import GUARANTEES, PROFILE, RIGHTS, schemas
from safe_kernel import (Controller, EvaluatorImage, ExternalPolicy, Scope, delta_plan,
                         merge_measurement, reattach_measurement, verify_historical_archive)

NOW = "2026-09-15T03:12:29.000Z"
CONTRACT = {"operation": "identity-octets", "field": "", "coverage": "complete-captured-octets", "inverse": True}


def catalog_snapshot(entries):
    value = [
        {
            "id": entry["id"], "kind": entry["kind"], "parent": entry["parent"],
            "labels": entry["labels"], "metadata_sha256": entry["metadata_sha256"],
            "share_class": entry["share_class"],
        }
        for entry in sorted(entries, key=lambda item: item["id"])
    ]
    return sha(json.dumps(
        value, sort_keys=True, ensure_ascii=True, allow_nan=False,
        separators=(",", ":"),
    ).encode("ascii"))


def organization_tiles(catalog_id, groups, assignments, *, tree_id="organization", tile_count=1):
    snapshot = {
        "tree_id": tree_id,
        "catalog_id": catalog_id,
        "root_group": "root",
        "groups": groups,
        "assignments": sorted(
            assignments,
            key=lambda item: (item["entry_id"], item["group_id"]),
        ),
    }
    digest = sha(json.dumps(
        snapshot, sort_keys=True, ensure_ascii=True, allow_nan=False,
        separators=(",", ":"),
    ).encode("ascii"))
    return [
        {
            "schema": "rapp-workspace/organization-tree-tile/1",
            "tree_id": tree_id,
            "catalog_id": catalog_id,
            "root_group": "root",
            "tile_index": index,
            "tile_count": tile_count,
            "snapshot_sha256": digest,
            "groups": groups,
            "assignments": assignments[index::tile_count],
        }
        for index in range(tile_count)
    ]


class SafeKernelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.core = Parent(os.environ.get("RAPP1_PATH"))

    def setUp(self):
        self.root = REPO / ".validation/test-artifacts" / ("safe-" + uuid.uuid4().hex)
        self.root.mkdir(parents=True, mode=0o700)
        self.addCleanup(shutil.rmtree, self.root)
        self.source = self.root / "native.data"
        self.source.write_bytes(b"PUBLIC SYNTHETIC INPUT")
        self.scope = Scope("fixture", "stable-native-subject", str(self.source))
        with patch.object(self.core.r.uuid, "uuid4", return_value=uuid.UUID(int=191001, version=4)):
            rid = self.core.r.mint_rappid("fictional", "safe-instance")
        self.policy = ExternalPolicy(
            rid, "fixture-world", sha(read_file(REFERENCE.parent / "SPEC.md")),
            sha(read_file(REFERENCE.parent / "manifest.json")),
            frozenset({"capture", "local_synthesis", "retention", "adoption", "materialization"}),
            (self.scope,), max_attempts=16, max_frames=256)
        self.c = Controller(self.core, self.root / "controller", self.policy, now=NOW)
        self.addCleanup(self.c.close)
        self.c.seed(self.scope.subject())

    def candidate(self, raw=None, operation="identity-octets", field=""):
        if raw is None:
            raw = ("finite immutable captured data " + str(self.c._get("sequence"))).encode()
        captured = self.c.capture_octets(self.scope.subject(), raw)
        lens = self.c.synthesize(self.scope.subject(), captured["source"], operation, field)
        result = self.c.execute(self.scope.subject(), lens)
        return captured, lens, result

    def ready(self):
        cap, lens, result = self.candidate()
        self.c.approve_contract(CONTRACT)
        fidelity = self.c.fidelity(self.scope.subject(), result["frame"], CONTRACT)
        request, frontier = self.c.request_adoption(
            self.scope.subject(), result["frame"], fidelity, CONTRACT, "operation-one",
            integrity=result["rapp_integrity"], observation=cap["observation"])
        return cap, result, fidelity, request, frontier

    def test_unique_validator_and_exact_manifest_do_not_reuse_historical_ids(self):
        self.assertEqual(PROFILE, "rapp-workspace/1")
        self.assertTrue(check_index())
        self.assertTrue(json.loads((REPO / "protocols/index.json").read_bytes())["authority"])
        self.assertTrue(manifest()["authority"])
        self.assertEqual(read_file(REFERENCE.parent / "manifest.json"), encode(manifest()))
        p = self.c.body(self.c._get("root"))
        p["schema"] = "rapp-workspace/1.0/seed"
        with self.assertRaisesRegex(Refusal, "unsupported"):
            self.core.schemas.validate(p)
        with self.assertRaisesRegex(Refusal, "wrong-validator-or-spec-pin"):
            Controller(self.core, self.root / "wrong-pin", replace(self.policy, spec_sha256="0" * 64), now=NOW)
        self.assertFalse((self.root / "wrong-pin").exists())

    def test_guarantees_are_distinct_and_replay_does_not_imply_fidelity_or_deployment(self):
        cap, _, result = self.candidate()
        self.assertEqual(self.c.body(result["rapp_integrity"])["status"], "verified")
        self.assertEqual(self.c.body(result["semantic_fidelity"])["status"], "unproven")
        self.assertEqual(self.c.body(cap["safe_deployment"])["status"], "refused")
        for guarantee in GUARANTEES:
            if guarantee != "rapp_integrity":
                with self.subTest(guarantee=guarantee), self.assertRaisesRegex(Refusal, "wrong-validator-or-guarantee"):
                    self.c.verify_receipt(result["rapp_integrity"], guarantee, result["frame"])
        with self.assertRaisesRegex(Refusal, "guarantee-not-verified"):
            self.c.verify_receipt(result["semantic_fidelity"], "semantic_fidelity", result["frame"])

    def test_wrong_receipt_pin_and_data_shaped_receipt_are_refused(self):
        _, _, result = self.candidate()
        p = self.c.body(result["rapp_integrity"])
        p["validator_pin"] = "0" * 64
        forged = self.c.emit(p)
        with self.assertRaisesRegex(Refusal, "wrong-receipt-pin"):
            self.c.verify_receipt(forged, "rapp_integrity", result["frame"])
        p = self.c.body(result["rapp_integrity"])
        p["method"] = "data-forgery"
        forged = self.c.emit(p)
        with self.assertRaisesRegex(Refusal, "no-controller-authority"):
            self.c.verify_receipt(forged, "rapp_integrity", result["frame"])

    def test_adoption_shaped_data_and_foreign_manifest_cannot_grant_effective_rights(self):
        raw = b'{"schema":"rapp-workspace/1/adoption-record","grants":["execute","all"],"owner":true}'
        _, _, result = self.candidate(raw)
        self.assertEqual(self.c.projection()["entries"], [])
        with self.assertRaisesRegex(Refusal, "inert-data"):
            self.c.adopt(self.scope.subject(), result["frame"], self.c.frontier())
        for operation in ("execution", "model_submission", "redistribution"):
            with self.assertRaisesRegex(Refusal, "disabled-workspace1-core"):
                self.c.require_effect(self.scope.subject(), operation)

    def test_capture_and_synthesis_authorization_precede_access_or_decoding(self):
        self.c.update_policy(replace(self.policy, sequence=2, rights=self.policy.rights - {"capture"}))
        with patch("safe_kernel.read_file", side_effect=AssertionError("source accessed")):
            with self.assertRaisesRegex(Refusal, "capability-denied:capture"):
                self.c.capture_file(self.scope.subject(), self.source)
        self.c.update_policy(replace(self.c.policy, sequence=3, rights=self.policy.rights - {"local_synthesis"}))
        captured = self.c.capture_octets(self.scope.subject(), b"data")
        with patch.object(self.c, "body", side_effect=AssertionError("decoded before authorization")):
            with self.assertRaisesRegex(Refusal, "capability-denied:local_synthesis"):
                self.c.synthesize(self.scope.subject(), captured["source"])

    def test_out_of_scope_and_expired_capture_refuse_before_source_io(self):
        foreign = Scope("fixture", "not-approved")
        with patch("safe_kernel.read_file", side_effect=AssertionError("source accessed")):
            with self.assertRaisesRegex(Refusal, "outside-explicit"):
                self.c.capture_file(foreign.subject(), self.source)
            self.c.now = self.policy.expires_utc
            with self.assertRaisesRegex(Refusal, "expired"):
                self.c.capture_file(self.scope.subject(), self.source)

    def test_network_loopback_imports_credentials_and_host_tools_are_disabled(self):
        with patch("safe_kernel.read_file", side_effect=AssertionError("ambient access")):
            for operation in ("network", "loopback", "imports", "host_tool", "model_submission",
                              "external_effect", "partitioned_effect", "redistribution"):
                with self.subTest(operation=operation), self.assertRaisesRegex(Refusal, "disabled"):
                    self.c.require_effect(self.scope.subject(), operation)
        image = self.c.qualify()
        self.assertNotIn("__import__", image._evaluate.__globals__["__builtins__"])
        self.assertNotIn("open", image._evaluate.__globals__["__builtins__"])
        with self.assertRaisesRegex(Refusal, "disabled"):
            image.evaluate("python", b"ignored")

    def test_restrictions_intersect_through_sources_lenses_results_and_failures(self):
        restricted = self.c.restrictions()
        restricted["rights"]["adoption"] = False
        restricted["rights"]["materialization"] = False
        captured = self.c.capture_octets(self.scope.subject(), b"not-json", inherited=[restricted])
        lens = self.c.synthesize(self.scope.subject(), captured["source"], "json-field", "x")
        result = self.c.execute(self.scope.subject(), lens)
        for ref in (captured["source"], lens, result["frame"], result["semantic_fidelity"]):
            p = self.c.body(ref)
            self.assertFalse(p["restrictions"]["rights"]["adoption"])
            self.assertFalse(p["restrictions"]["rights"]["materialization"])
            self.assertTrue(p["restrictions"]["hashes_sensitive"])
            self.assertEqual(p["restrictions"]["privacy"], "godd")

    def test_capture_model_retention_redistribution_rights_are_separate(self):
        restrictions = self.c.restrictions()
        restrictions["rights"]["retention"] = False
        before = self.c.checkpoint()
        with self.assertRaisesRegex(Refusal, "inherited-restriction-denied:retention"):
            self.c.capture_octets(self.scope.subject(), b"not persisted", inherited=[restrictions])
        self.assertEqual(before, self.c.checkpoint())
        self.assertFalse(self.c.restrictions()["rights"]["model_submission"])
        self.assertFalse(self.c.restrictions()["rights"]["redistribution"])

    def test_unprovable_physical_deletion_is_disabled_before_capture(self):
        with self.assertRaisesRegex(Refusal, "erasure"):
            Controller(self.core, self.root / "must-not-exist", replace(self.policy, physical_deletion_required=True), now=NOW)
        self.assertFalse((self.root / "must-not-exist").exists())

    def test_exact_mapping_contract_and_inverse_required_for_fidelity(self):
        _, _, result = self.candidate()
        with self.assertRaisesRegex(Refusal, "externally-approved"):
            self.c.fidelity(self.scope.subject(), result["frame"], CONTRACT)
        self.c.approve_contract(CONTRACT)
        proof = self.c.fidelity(self.scope.subject(), result["frame"], CONTRACT)
        self.c.verify_receipt(proof, "semantic_fidelity", result["frame"], scope="complete-captured-octets")
        with self.assertRaisesRegex(Refusal, "scope-mismatch"):
            self.c.verify_receipt(proof, "semantic_fidelity", result["frame"], scope="native-behavior")

    def test_partial_field_mapping_is_not_complete_behavior_coverage(self):
        cap, _, result = self.candidate(b'{"a":1,"unmapped":2}', "json-field", "a")
        contract = {"operation": "json-field", "field": "a", "coverage": "selected-field-only", "inverse": False}
        self.c.approve_contract(contract)
        proof = self.c.fidelity(self.scope.subject(), result["frame"], contract)
        request, frontier = self.c.request_adoption(
            self.scope.subject(), result["frame"], proof, contract, "partial",
            integrity=result["rapp_integrity"], observation=cap["observation"])
        with self.assertRaisesRegex(Refusal, "scope-mismatch"):
            self.c.adopt(self.scope.subject(), request, frontier)

    def test_finite_octets_capture_is_separate_from_strict_interpretation(self):
        for raw in (b"\xff\xfe", b'{"a":1,"a":2}', b'{"a":9007199254740993}', b'{"a":NaN}'):
            with self.subTest(raw=raw):
                cap, _, result = self.candidate(raw, "json-field", "a")
                self.assertEqual(self.c.body(cap["rapp_integrity"])["status"], "verified")
                self.assertEqual(result["kind"], "refused")
                self.assertEqual(self.c.body(result["semantic_fidelity"])["status"], "refused")
        with self.assertRaisesRegex(Refusal, "finite-bounded"):
            self.c.capture_octets(self.scope.subject(), b"x" * 65537)
        with self.assertRaisesRegex(Refusal, "finite-bounded"):
            self.c.capture_octets(self.scope.subject(), iter([b"x"]))
        cycle = []
        cycle.append(cycle)
        with self.assertRaisesRegex(Refusal, "cyclic"):
            self.core.octets(cycle)

    def test_stable_descriptor_read_does_not_claim_coherent_native_snapshot(self):
        cap = self.c.capture_file(self.scope.subject(), self.source)
        self.assertEqual(self.c.body(cap["observation"])["method"], "stable-descriptor-not-coherent")
        self.assertEqual(self.c.body(cap["observation"])["scope"], "captured-octets-only")
        lens = self.c.synthesize(self.scope.subject(), cap["source"])
        result = self.c.execute(self.scope.subject(), lens)
        candidate = result["frame"]
        self.c.approve_contract(CONTRACT)
        proof = self.c.fidelity(self.scope.subject(), candidate, CONTRACT)
        request, frontier = self.c.request_adoption(
            self.scope.subject(), candidate, proof, CONTRACT, "native",
            integrity=result["rapp_integrity"], observation=cap["observation"])
        with self.assertRaisesRegex(Refusal, "native-coherent"):
            self.c.adopt(self.scope.subject(), request, frontier)

    def test_content_occurrence_subject_instance_are_not_conflated(self):
        first = self.c.capture_octets(self.scope.subject(), b"same")
        second = self.c.capture_octets(self.scope.subject(), b"same")
        self.assertNotEqual(first["source"], second["source"])
        a, b = self.c.body(first["source"]), self.c.body(second["source"])
        self.assertEqual(a["content"], b["content"])
        self.assertEqual(a["native_subject"], b["native_subject"])
        self.assertEqual(a["instance_rappid"], self.policy.instance_rappid)

    def test_suppression_survives_new_rendition_and_restart(self):
        self.c.suppress(self.scope.subject())
        self.c.capture_octets(self.scope.subject(), b"new rendition, same native subject")
        checkpoint = self.c.checkpoint()
        self.c.close()
        self.c = Controller(self.core, self.root / "controller", self.policy, now=NOW, checkpoint=checkpoint)
        self.addCleanup(self.c.close)
        _, _, _, request, frontier = self.ready()
        with self.assertRaisesRegex(Refusal, "suppression"):
            self.c.adopt(self.scope.subject(), request, frontier)

    def test_actual_necessary_synthesis_negative_enumeration_and_env_reads(self):
        _, lens, result = self.candidate(b'{"a":1}', "json-field", "a")
        p = self.c.body(result["frame"])
        self.assertEqual(p["actual_reads"], p["necessary_reads"])
        self.assertEqual(p["synthesis_reads"], p["actual_reads"])
        self.assertEqual(p["enumerations"][0]["kind"], "enumeration")
        self.assertEqual(p["environment"], [])
        _, missing, refused = self.candidate(b'{"a":1}', "json-field", "missing")
        self.assertEqual(refused["negative_reads"][0]["kind"], "negative")
        with self.assertRaisesRegex(Refusal, "ambient-environment"):
            self.c.execute(self.scope.subject(), lens, environment=["HOME"])
        cap = self.c.capture_octets(self.scope.subject(), b"other")
        fresh = self.c.synthesize(self.scope.subject(), cap["source"])
        with self.assertRaisesRegex(Refusal, "actual-read-trace-forgery"):
            self.c.execute(self.scope.subject(), fresh, actual_override=[])

    def test_merge_reports_correspondence_coverage_and_zero_overlap_unmeasured(self):
        with self.assertRaisesRegex(Refusal, "correspondence"):
            merge_measurement({"a": 1}, {"b": 1}, None)
        measured = merge_measurement({"a": 1}, {"a": 2}, {"pairs": [["a", "a"]]})
        self.assertEqual(measured["numerator"], 0)
        self.assertEqual(measured["denominator"], 1)
        self.assertEqual(len(measured["conflicts"]), 1)
        empty = merge_measurement({"a": 1}, {"b": 1}, {"pairs": [["a", "a"]]})
        self.assertEqual(empty["status"], "unmeasured")
        self.assertIsNone(empty["numerator"])
        self.assertIsNone(empty["denominator"])
        self.assertFalse(empty["coverage_complete"])

    def test_reattach_requires_coverage_not_only_noncontradiction(self):
        p = reattach_measurement({"required": "a"}, {})
        self.assertEqual(p["status"], "unresolved")
        self.assertEqual(p["missing_coverage"], ["required"])
        self.assertFalse(p["adopted"])
        self.assertEqual(reattach_measurement({"x": "a"}, {"x": "b"})["contradictions"], ["x"])

    def test_root_budget_depth_noop_and_pingpong_terminate(self):
        _, lens, _ = self.candidate(b'{"a":1,"b":2}')
        duplicate = self.c.execute(self.scope.subject(), lens)
        self.assertEqual(duplicate["reason"], "repeated-state-fixed-point")
        cap = self.c.capture_octets(self.scope.subject(), b'{"a":1,"b":2,"new":3}')
        first = self.c.synthesize(self.scope.subject(), cap["source"], "json-field", "a")
        second = self.c.synthesize(self.scope.subject(), cap["source"], "json-field", "b")
        third = self.c.synthesize(self.scope.subject(), cap["source"], "json-field", "new")
        self.c.execute(self.scope.subject(), first)
        self.c.execute(self.scope.subject(), second)
        stopped = self.c.execute(self.scope.subject(), third)
        self.assertEqual(stopped["reason"], "no-progress-or-oscillation")
        depth = self.c.execute(self.scope.subject(), first, depth=32)
        self.assertEqual(depth["reason"], "attempt-or-depth-budget")

    def test_stop_capacity_is_reserved_and_children_cannot_reset_attempt_budget(self):
        self.c.update_policy(replace(self.policy, sequence=2, max_attempts=1))
        _, lens, _ = self.candidate()
        result = self.c.execute(self.scope.subject(), lens, depth=1)
        self.assertEqual(result["kind"], "stopped")
        self.assertTrue(self.c.body(result["frame"])["reserved_stop"])
        with self.assertRaisesRegex(Refusal, "budget-reset"):
            self.c.update_policy(replace(self.c.policy, sequence=3, max_attempts=2))

    def test_historical_integrity_survives_missing_evaluator_but_fresh_execution_refuses(self):
        self.candidate()
        frames = [row[0] for row in self.c.db.execute("SELECT raw FROM frames ORDER BY seq")]
        original = read_file
        def unavailable(path, *args, **kwargs):
            if str(path).endswith("total_eval.py"):
                raise OSError("old evaluator unavailable")
            return original(path, *args, **kwargs)
        with patch("safe_kernel.read_file", unavailable):
            proof = verify_historical_archive(self.core, frames, self.policy.instance_rappid)
            self.assertEqual(proof["rapp_integrity"], "verified")
            self.assertEqual(proof["semantic_fidelity"], "historical-evaluator-unavailable")
            with self.assertRaises(OSError):
                self.c.qualify()

    def test_delta_requires_fresh_complete_baseline_and_excludes_generated_output(self):
        old = "2026-01-01T00:00:00.000Z"
        future = "2027-01-01T00:00:00.000Z"
        p = delta_plan(["a"], ["a"], old, NOW, [], [])
        self.assertEqual(p["mode"], "baseline-required")
        self.assertFalse(p["current_clean_claim"])
        self.assertEqual(delta_plan(["a", "b"], ["a"], future, NOW, [], [])["mode"], "baseline-required")
        with self.assertRaisesRegex(Refusal, "generated-output"):
            delta_plan(["a"], ["a"], future, NOW, [], ["a"])
        with self.assertRaisesRegex(Refusal, "disabled"):
            self.c.require_effect(self.scope.subject(), "live_delta")

    def test_single_writer_partition_refusal_and_fork_latch(self):
        with self.assertRaisesRegex(Refusal, "single-writer"):
            Controller(self.core, self.root / "controller", self.policy, now=NOW)
        with self.assertRaisesRegex(Refusal, "partition"):
            Controller(self.core, self.root / "partition", replace(self.policy, partitioned=True), now=NOW)
        original = self.c._head()
        payload = dict(original["payload"])
        payload["world_id"] = "rival-data"
        rival = self.core.r.build_frame("body.pulse", self.policy.instance_rappid, 0, NOW, payload, None)
        with self.assertRaisesRegex(Refusal, "fork-latched"):
            self.c.observe_owned_fork(self.core.octets(rival))
        checkpoint = self.c.checkpoint()
        self.c.close()
        self.c = Controller(self.core, self.root / "controller", self.policy, now=NOW, checkpoint=checkpoint)
        self.addCleanup(self.c.close)
        with self.assertRaisesRegex(Refusal, "fork-latched"):
            self.c.capture_octets(self.scope.subject(), b"no new authorization")

    def test_live_migration_without_behavior_and_snapshot_proof_is_disabled_before_io(self):
        before = self.source.read_bytes()
        with patch("safe_kernel.read_file", side_effect=AssertionError("migration accessed source")):
            with self.assertRaisesRegex(Refusal, "disabled-workspace1-core:live_migration"):
                self.c.require_effect(self.scope.subject(), "live_migration")
        self.assertEqual(self.source.read_bytes(), before)

    def test_complete_frontier_rejects_suppression_policy_source_and_routing_races(self):
        for change in ("suppression", "policy", "source", "graph", "runtime"):
            with self.subTest(change=change):
                cap, result, fidelity, request, frontier = self.ready()
                if change == "suppression":
                    self.c.suppress(self.scope.subject())
                elif change == "policy":
                    self.c.update_policy(replace(self.c.policy, sequence=self.c.policy.sequence + 1))
                elif change == "source":
                    self.c.capture_octets(self.scope.subject(), b"new current binding")
                elif change == "graph":
                    self.c.authorization_receipt(self.scope.subject(), result["frame"], "capture")
                else:
                    frontier = {**frontier, "runtime_sha256": "0" * 64}
                with self.assertRaises(Refusal):
                    self.c.adopt(self.scope.subject(), request, frontier)
                self.assertEqual(self.c.db.execute("SELECT COUNT(*) FROM adoptions").fetchone()[0], 0)

    def test_adoption_commit_crash_recovery_idempotence_and_changed_operation_refusal(self):
        cap, result, fidelity, request, frontier = self.ready()
        before = self.c.checkpoint()
        def crash(stage):
            if stage == "before-commit":
                raise RuntimeError("synthetic crash")
        with self.assertRaises(RuntimeError):
            self.c.adopt(self.scope.subject(), request, frontier, fault=crash)
        self.assertEqual(before, self.c.checkpoint())
        def lost_ack(stage):
            if stage == "after-commit":
                raise RuntimeError("lost acknowledgement")
        with self.assertRaises(RuntimeError):
            self.c.adopt(self.scope.subject(), request, frontier, fault=lost_ack)
        first = self.c.adopt(self.scope.subject(), request, frontier)
        self.assertEqual(first, self.c.adopt(self.scope.subject(), request, frontier))
        self.assertEqual(len(self.c.projection()["entries"]), 1)
        other, updated = self.c.request_adoption(
            self.scope.subject(), result["frame"], fidelity, CONTRACT, "operation-one",
            integrity=result["rapp_integrity"], observation=cap["observation"])
        with self.assertRaisesRegex(Refusal, "idempotency-conflict"):
            self.c.adopt(self.scope.subject(), other, updated)

    def test_current_authorization_receipt_is_not_a_reusable_capability(self):
        _, _, result = self.candidate()
        auth = self.c.authorization_receipt(self.scope.subject(), result["frame"], "adoption")
        self.assertEqual(self.c.body(auth)["status"], "verified")
        with self.assertRaisesRegex(Refusal, "external-controller-query"):
            self.c.verify_receipt(auth, "current_authorization", result["frame"], current=True)

    def test_inert_json_materialization_does_not_execute_html_images_or_controls(self):
        raw = b'<img src="https://not-contacted.invalid/x"><script>not executed</script>\x1b[2J'
        cap, _, result = self.candidate(raw)
        self.c.approve_contract(CONTRACT)
        proof = self.c.fidelity(self.scope.subject(), result["frame"], CONTRACT)
        request, frontier = self.c.request_adoption(
            self.scope.subject(), result["frame"], proof, CONTRACT, "inert",
            integrity=result["rapp_integrity"], observation=cap["observation"])
        self.c.adopt(self.scope.subject(), request, frontier)
        path = self.c.materialize(self.scope.subject())
        self.assertEqual(path.name, "view.json")
        content = path.read_bytes()
        self.assertNotIn(b"<img", content)
        self.assertNotIn(b"\x1b", content)
        self.assertFalse((self.c.path / "SKILL.md").exists())
        self.assertFalse(json.loads(content)["native_rebinding"])
        with self.assertRaisesRegex(Refusal, "disabled"):
            self.c.require_effect(self.scope.subject(), "html_materialization")

    def test_exact_evaluator_image_is_consumed_without_reopening_changed_path(self):
        path = self.root / "evaluator-image.py"
        captured = read_file(REFERENCE / "total_eval.py")
        path.write_bytes(captured)
        image = EvaluatorImage(path.read_bytes(), sha(captured))
        path.write_bytes(b"raise RuntimeError('replacement must not execute')")
        self.assertEqual(image.evaluate("identity-octets", b"safe"), b"safe")
        with self.assertRaisesRegex(Refusal, "closure-substitution"):
            EvaluatorImage(path.read_bytes(), sha(captured))

    def test_portability_is_not_native_rebinding_or_redistribution(self):
        with self.assertRaisesRegex(Refusal, "output-scope"):
            self.c.export_frames(self.root / "outside-controller")
        for action in ("native_rebinding", "redistribution", "learned_semantic_capability", "unqualified_runtime"):
            with self.subTest(action=action), self.assertRaisesRegex(Refusal, "disabled"):
                self.c.require_effect(self.scope.subject(), action)

    def test_forged_derivation_cannot_weaken_inherited_restrictions(self):
        restricted = self.c.restrictions()
        restricted["rights"]["adoption"] = False
        cap = self.c.capture_octets(self.scope.subject(), b"restricted source", inherited=[restricted])
        lens = self.c.synthesize(self.scope.subject(), cap["source"])
        result = self.c.execute(self.scope.subject(), lens)
        forged = self.c.body(result["frame"])
        forged["restrictions"]["rights"]["adoption"] = True
        fake = self.c.emit(forged)
        self.c.approve_contract(CONTRACT)
        with self.assertRaisesRegex(Refusal, "restrictions widened"):
            self.c.fidelity(self.scope.subject(), fake, CONTRACT)

    def test_adoption_requires_each_distinct_guarantee_not_only_fidelity(self):
        cap, result, fidelity, request, frontier = self.ready()
        forged = self.c.body(request)
        forged["operation_id"] = "wrong-guarantee"
        forged["observation"] = result["rapp_integrity"]
        forged["frontier"] = self.c.frontier()
        fake = self.c.emit(forged)
        with self.assertRaisesRegex(Refusal, "wrong-validator-or-guarantee"):
            self.c.adopt(self.scope.subject(), fake, self.c.frontier())
        self.assertEqual(self.c.projection()["entries"], [])

    def test_retained_byte_tamper_cannot_reuse_a_previously_verified_receipt(self):
        _, result, _, request, frontier = self.ready()
        frame = self.c.frame(result["frame"])
        frame["payload"]["result_b64"] = "dGFtcGVy"
        self.c.db.execute("UPDATE frames SET raw=? WHERE hash=?",
                          (self.core.octets(frame), result["frame"]["hash"]))
        with self.assertRaisesRegex(Refusal, "tamper|integrity"):
            self.c.adopt(self.scope.subject(), request, frontier)

    def test_root_byte_budget_is_transitive_and_final_stop_is_durable(self):
        self.c.update_policy(replace(self.policy, sequence=2, max_total_octets=8, max_attempts=1))
        cap = self.c.capture_octets(self.scope.subject(), b"123456")
        before = self.c.checkpoint()
        with self.assertRaisesRegex(Refusal, "root-owned-byte-budget"):
            self.c.capture_octets(self.scope.subject(), b"789")
        self.assertEqual(before, self.c.checkpoint())
        lens = self.c.synthesize(self.scope.subject(), cap["source"])
        self.c.execute(self.scope.subject(), lens)
        stopped = self.c.execute(self.scope.subject(), lens)
        snapshot = self.c.checkpoint()
        again = self.c.execute(self.scope.subject(), lens)
        self.assertEqual(again["frame"], stopped["frame"])
        self.assertEqual(snapshot, self.c.checkpoint())

    def test_checkpoint_refuses_suppression_loss_and_same_sequence_frontier_fork(self):
        self.c.suppress(self.scope.subject())
        checkpoint = self.c.checkpoint()
        self.c.db.execute("DELETE FROM suppressions")
        with self.assertRaisesRegex(Refusal, "suppression rollback"):
            self.c.check_checkpoint(checkpoint)

    def test_abrupt_process_crash_recovers_without_partial_adoption(self):
        _, _, _, request, frontier = self.ready()
        before = self.c.checkpoint()
        policy = self.c._policy_value(self.policy)
        policy_file = self.root / "external-policy.json"
        args_file = self.root / "adoption-input.json"
        policy_file.write_bytes(self.core.octets(policy))
        args_file.write_bytes(self.core.octets({"request": request, "frontier": frontier}))
        self.c.close()
        script = """
import json, os, sys
sys.path.insert(0, sys.argv[1])
from common import Parent, read_file
from safe_kernel import Controller, ExternalPolicy, Scope
core = Parent(sys.argv[2])
p = core.parse(read_file(sys.argv[4]))
a = core.parse(read_file(sys.argv[5]))
policy = ExternalPolicy(p['instance_rappid'], p['world_id'], p['spec_sha256'], p['runtime_sha256'],
    frozenset(p['rights']), tuple(Scope(x['subject']['namespace'],x['subject']['native_key'],x['path']) for x in p['scopes']),
    sequence=p['sequence'],expires_utc=p['expires_utc'],audience=tuple(p['audience']),
    max_attempts=p['max_attempts'],max_depth=p['max_depth'],max_frames=p['max_frames'],max_total_octets=p['max_total_octets'])
c = Controller(core, sys.argv[3], policy, now="2026-09-15T03:12:29.000Z")
c.adopt(policy.scopes[0].subject(), a['request'], a['frontier'],
        fault=lambda stage: os._exit(93) if stage == 'before-commit' else None)
"""
        completed = subprocess.run([sys.executable, "-B", "-c", script, str(REFERENCE), str(self.core.path),
                                    str(self.root / "controller"), str(policy_file), str(args_file)],
                                   capture_output=True, timeout=60)
        self.assertEqual(completed.returncode, 93, completed.stderr.decode())
        self.c = Controller(self.core, self.root / "controller", self.policy, now=NOW)
        self.addCleanup(self.c.close)
        self.assertEqual(self.c.checkpoint(), before)
        self.c.adopt(self.scope.subject(), request, frontier)
        self.assertEqual(len(self.c.projection()["entries"]), 1)

    def test_controller_clock_rollback_and_partial_ledger_loss_refuse(self):
        self.c.now = "2026-01-01T00:00:00.000Z"
        with self.assertRaisesRegex(Refusal, "clock-rollback"):
            self.c.capture_octets(self.scope.subject(), b"must not read")
        self.c.now = NOW
        _, _, _, request, frontier = self.ready()
        self.c.adopt(self.scope.subject(), request, frontier)
        self.c.db.execute("DELETE FROM adoptions")
        with self.assertRaisesRegex(Refusal, "recovery-quarantine"):
            self.c.verify_history()

    def test_cli_capture_does_not_implicitly_grant_materialization_or_synthesis(self):
        output = (self.root / "capture-only").relative_to(REPO)
        completed = subprocess.run([
            sys.executable, "-B", str(REPO / "tools/frame_lens.py"), "demo",
            "--rapp1-path", str(self.core.path), "--fixture", str(self.source),
            "--allow-capture", "--allow-retention", "--output", str(output),
        ], cwd=REPO, capture_output=True, text=True, timeout=60)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        report = json.loads((REPO / output / "report.json").read_bytes())
        self.assertEqual(report["synthesis"], "not-authorized")
        self.assertFalse((REPO / output / "controller/evidence").exists())
        self.assertFalse((REPO / output / "controller/view.json").exists())
        self.assertEqual(report["scan_method"], "canonical-parent-in-memory")

    def test_recursive_catalog_refines_outcome_tree_and_withholds_hive_private_entries(self):
        entries = [
            {"id": "repo:a", "kind": "git-repository", "parent": "github:kody-w",
             "labels": ["build-rapp", "workspace"], "metadata_sha256": "1" * 64,
             "share_class": "public-source"},
            {"id": "repo:b", "kind": "git-repository", "parent": "github:kody-w",
             "labels": ["build-rapp", "workspace"], "metadata_sha256": "2" * 64,
             "share_class": "private-source"},
            {"id": "repo:c", "kind": "git-repository", "parent": "github:kody-w",
             "labels": ["publish", "workspace"], "metadata_sha256": "3" * 64,
             "share_class": "public-source"},
            {"id": "repo:d", "kind": "git-repository", "parent": "github:kody-w",
             "labels": ["archive", "workspace"], "metadata_sha256": "4" * 64,
             "share_class": "excluded-source"},
        ]
        snapshot = catalog_snapshot(entries)
        shards = []
        for index in range(2):
            document = {
                "schema": "rapp-workspace/catalog-chunk/1",
                "catalog_id": "github:kody-w",
                "root_id": "github:kody-w",
                "shard_index": index,
                "shard_count": 2,
                "snapshot_sha256": snapshot,
                "branch_scope": "default-branch-only",
                "branch_evidence_status": "external-host-observation-unproven",
                "recursive": True,
                "entries": entries[index * 2:(index + 1) * 2],
            }
            source = self.c.capture_octets(self.scope.subject(), self.core.octets(document))["source"]
            shards.append(self.c.register_catalog_shard(self.scope.subject(), source))

        broad_tree = organization_tiles(
            "github:kody-w",
            [
                {"id": "root", "name": "GitHub", "parent": None},
                {"id": "all-work", "name": "All Work", "parent": "root"},
            ],
            [
                {"entry_id": entry["id"], "group_id": "all-work"} for entry in entries
            ],
        )[0]
        broad_source = self.c.capture_octets(
            self.scope.subject(), self.core.octets(broad_tree))["source"]
        first = self.c.assess_organization(
            self.scope.subject(), shards, broad_source,
            max_bucket=2, allowed_depth=4)
        first_body = self.c.body(first)
        self.assertEqual(first_body["status"], "needs-refinement")
        self.assertEqual(first_body["largest_bucket"], 4)

        refined_tree = organization_tiles(
            "github:kody-w",
            [
                {"id": "root", "name": "GitHub", "parent": None},
                {"id": "build", "name": "Build", "parent": "root"},
                {"id": "publish", "name": "Publish", "parent": "root"},
            ],
            [
                {"entry_id": "repo:a", "group_id": "build"},
                {"entry_id": "repo:b", "group_id": "build"},
                {"entry_id": "repo:c", "group_id": "publish"},
                {"entry_id": "repo:d", "group_id": "publish"},
            ],
        )[0]
        refined_source = self.c.capture_octets(
            self.scope.subject(), self.core.octets(refined_tree))["source"]
        refined = self.c.assess_organization(
            self.scope.subject(), shards, refined_source,
            max_bucket=2, allowed_depth=4, refinement_round=1, previous=first)
        refined_body = self.c.body(refined)
        self.assertEqual(refined_body["status"], "verified")
        self.assertTrue(refined_body["progress"])
        self.assertEqual(refined_body["assigned_count"], 4)

        outcome = self.c.candidate_outcome(
            self.scope.subject(), refined, "publish and improve RAPP", ["repo:a", "repo:c"])
        outcome_body = self.c.body(outcome)
        self.assertEqual(outcome_body["status"], "candidate")
        self.assertEqual(outcome_body["semantic_fidelity"], "unproven")
        self.assertNotIn("publish and improve RAPP", json.dumps(outcome_body))
        self.assertFalse(outcome_body["grants_authority"])

        withheld = self.c.propose_subscription(
            self.scope.subject(), refined, [entry["id"] for entry in entries])
        withheld_body = self.c.body(withheld)
        self.assertEqual(withheld_body["selected_ids"], ["repo:a", "repo:c"])
        self.assertEqual(withheld_body["withheld_private"], 1)
        self.assertEqual(withheld_body["withheld_excluded"], 1)
        self.assertFalse(withheld_body["publication_authorized"])

        approved = self.c.propose_subscription(
            self.scope.subject(), refined, [entry["id"] for entry in entries],
            approved_private_ids=["repo:b"])
        approved_body = self.c.body(approved)
        self.assertEqual(approved_body["selected_ids"], ["repo:a", "repo:b", "repo:c"])
        self.assertEqual(approved_body["externally_approved_private"], 1)
        self.assertFalse(approved_body["publication_authorized"])

        build = self.c.compose_workspace(
            self.scope.subject(), refined, "build-workspace", ["repo:a", "repo:b"])
        publish = self.c.compose_workspace(
            self.scope.subject(), refined, "publish-workspace", ["repo:c", "repo:d"])
        root = self.c.compose_workspace(
            self.scope.subject(), refined, "all-workspaces", [], [build, publish])
        root_body = self.c.body(root)
        self.assertEqual(root_body["member_count"], 4)
        self.assertEqual(root_body["depth"], 1)
        self.assertTrue(root_body["child_identities_preserved"])
        self.assertTrue(root_body["child_worlds_preserved"])
        self.assertFalse(root_body["content_copied"])
        wrapped = self.c.compose_workspace(
            self.scope.subject(), refined, "workspace-of-workspaces", [], [root])
        self.assertEqual(self.c.body(wrapped)["depth"], 2)
        self.assertEqual(self.c.body(wrapped)["member_count"], 4)
        self.assertEqual(
            self.c.compose_workspace(
                self.scope.subject(), refined, "workspace-of-workspaces", [], [root]),
            wrapped,
        )
        with self.assertRaisesRegex(Refusal, "duplicate-member"):
            self.c.compose_workspace(
                self.scope.subject(), refined, "duplicate-member",
                ["repo:a"], [build])
        forged = self.c.body(build)
        forged["composite_id"] = "forged-composite"
        forged_ref = self.c.emit(forged)
        with self.assertRaisesRegex(Refusal, "controller-record-required"):
            self.c.compose_workspace(
                self.scope.subject(), refined, "forged-parent", [], [forged_ref])
        with self.assertRaisesRegex(Refusal, "idempotency-conflict"):
            self.c.compose_workspace(
                self.scope.subject(), refined, "build-workspace", ["repo:a"])

    def test_recursive_catalog_incomplete_no_progress_and_unverified_outcomes_refuse(self):
        entry = {"id": "repo:a", "kind": "git-repository", "parent": "github:kody-w",
                 "labels": [], "metadata_sha256": "1" * 64,
                 "share_class": "public-source"}
        document = {
            "schema": "rapp-workspace/catalog-chunk/1",
            "catalog_id": "github:kody-w",
            "root_id": "github:kody-w",
            "shard_index": 0,
            "shard_count": 2,
            "snapshot_sha256": catalog_snapshot([entry]),
            "branch_scope": "default-branch-only",
            "branch_evidence_status": "external-host-observation-unproven",
            "recursive": True,
            "entries": [entry],
        }
        source = self.c.capture_octets(self.scope.subject(), self.core.octets(document))["source"]
        shard = self.c.register_catalog_shard(self.scope.subject(), source)
        invalid_branch = {**document, "branch_scope": "all-branches", "shard_count": 1}
        invalid_source = self.c.capture_octets(
            self.scope.subject(), self.core.octets(invalid_branch))["source"]
        with self.assertRaisesRegex(Refusal, "unsupported-catalog-scope"):
            self.c.register_catalog_shard(self.scope.subject(), invalid_source)
        for operation in ("repository_clone", "branch_history", "hive_publication"):
            with self.subTest(operation=operation), self.assertRaisesRegex(
                    Refusal, "disabled-workspace1-core"):
                self.c.require_effect(self.scope.subject(), operation)
        tree = organization_tiles(
            "github:kody-w",
            [{"id": "root", "name": "GitHub", "parent": None}],
            [{"entry_id": "repo:a", "group_id": "root"}],
        )[0]
        tree_source = self.c.capture_octets(self.scope.subject(), self.core.octets(tree))["source"]
        with self.assertRaisesRegex(Refusal, "incomplete-catalog-shards"):
            self.c.assess_organization(
                self.scope.subject(), [shard], tree_source,
                max_bucket=1, allowed_depth=2)

        complete_document = {**document, "shard_count": 1}
        complete_source = self.c.capture_octets(
            self.scope.subject(), self.core.octets(complete_document))["source"]
        complete_shard = self.c.register_catalog_shard(self.scope.subject(), complete_source)
        first = self.c.assess_organization(
            self.scope.subject(), [complete_shard], tree_source,
            max_bucket=1, allowed_depth=2)
        self.assertEqual(self.c.body(first)["status"], "verified")
        with self.assertRaisesRegex(Refusal, "outcome-requires-verified"):
            self.c.candidate_outcome(
                self.scope.subject(), shard, "invalid assessment", ["repo:a"])

        broad = organization_tiles(
            "github:kody-w",
            [{"id": "root", "name": "GitHub", "parent": None}],
            [],
        )[0]
        broad_source = self.c.capture_octets(
            self.scope.subject(), self.core.octets(broad))["source"]
        needs = self.c.assess_organization(
            self.scope.subject(), [complete_shard], broad_source,
            max_bucket=1, allowed_depth=2)
        repeated_source = self.c.capture_octets(
            self.scope.subject(), self.core.octets(broad))["source"]
        stopped = self.c.assess_organization(
            self.scope.subject(), [complete_shard], repeated_source,
            max_bucket=1, allowed_depth=2, refinement_round=1, previous=needs)
        self.assertEqual(self.c.body(stopped)["status"], "no-progress")
        self.assertFalse(self.c.body(stopped)["progress"])

        cycle_document = {
            **complete_document,
            "entries": [
                {**entry, "id": "repo:a", "parent": "repo:b"},
                {**entry, "id": "repo:b", "parent": "repo:a",
                 "metadata_sha256": "2" * 64},
            ],
        }
        cycle_document["snapshot_sha256"] = catalog_snapshot(cycle_document["entries"])
        cycle_source = self.c.capture_octets(
            self.scope.subject(), self.core.octets(cycle_document))["source"]
        cycle_shard = self.c.register_catalog_shard(self.scope.subject(), cycle_source)
        with self.assertRaisesRegex(Refusal, "catalog-parent-cycle"):
            self.c.assess_organization(
                self.scope.subject(), [cycle_shard], tree_source,
                max_bucket=2, allowed_depth=2)

    def test_recursive_catalog_authority_snapshot_and_malformed_inputs_fail_closed(self):
        malformed = self.c.capture_octets(self.scope.subject(), b"{")["source"]
        with self.assertRaisesRegex(Refusal, "invalid-catalog-json"):
            self.c.register_catalog_shard(self.scope.subject(), malformed)

        invalid_labels = {
            "schema": "rapp-workspace/catalog-chunk/1",
            "catalog_id": "github:kody-w",
            "root_id": "github:kody-w",
            "shard_index": 0,
            "shard_count": 1,
            "snapshot_sha256": "0" * 64,
            "branch_scope": "default-branch-only",
            "branch_evidence_status": "external-host-observation-unproven",
            "recursive": False,
            "entries": [{
                "id": "repo:a", "kind": "git-repository", "parent": "github:kody-w",
                "labels": [{}], "metadata_sha256": "1" * 64,
                "share_class": "public-source",
            }],
        }
        invalid_source = self.c.capture_octets(
            self.scope.subject(), self.core.octets(invalid_labels))["source"]
        with self.assertRaisesRegex(Refusal, "invalid-catalog-entry-labels"):
            self.c.register_catalog_shard(self.scope.subject(), invalid_source)

        entries = [
            {"id": "repo:a", "kind": "git-repository", "parent": "github:kody-w",
             "labels": [], "metadata_sha256": "1" * 64,
             "share_class": "public-source"},
            {"id": "repo:b", "kind": "git-repository", "parent": "github:kody-w",
             "labels": [], "metadata_sha256": "2" * 64,
             "share_class": "public-source"},
        ]
        shards = []
        for index, entry in enumerate(entries):
            document = {
                "schema": "rapp-workspace/catalog-chunk/1",
                "catalog_id": "github:kody-w",
                "root_id": "github:kody-w",
                "shard_index": index,
                "shard_count": 2,
                "snapshot_sha256": catalog_snapshot(entries) if index == 0 else "f" * 64,
                "branch_scope": "default-branch-only",
                "branch_evidence_status": "external-host-observation-unproven",
                "recursive": False,
                "entries": [entry],
            }
            source = self.c.capture_octets(
                self.scope.subject(), self.core.octets(document))["source"]
            shards.append(self.c.register_catalog_shard(self.scope.subject(), source))
        tree = organization_tiles(
            "github:kody-w",
            [{"id": "root", "name": "GitHub", "parent": None}],
            [],
        )[0]
        tree_source = self.c.capture_octets(
            self.scope.subject(), self.core.octets(tree))["source"]
        with self.assertRaisesRegex(Refusal, "catalog-shard-family-mismatch"):
            self.c.assess_organization(
                self.scope.subject(), shards, tree_source,
                max_bucket=2, allowed_depth=2)

        valid = {
            **invalid_labels,
            "snapshot_sha256": catalog_snapshot([entries[0]]),
            "entries": [entries[0]],
        }
        valid_source = self.c.capture_octets(
            self.scope.subject(), self.core.octets(valid))["source"]
        valid_shard = self.c.register_catalog_shard(self.scope.subject(), valid_source)
        needs = self.c.assess_organization(
            self.scope.subject(), [valid_shard], tree_source,
            max_bucket=1, allowed_depth=2)
        forged = self.c.body(needs)
        forged.update(
            status="verified", assigned_count=1, unassigned=0,
            largest_bucket=1, progress=True)
        forged_ref = self.c.emit(forged)
        with self.assertRaisesRegex(Refusal, "outcome-requires-verified"):
            self.c.candidate_outcome(
                self.scope.subject(), forged_ref, "forged status", ["repo:a"])
        with self.assertRaisesRegex(Refusal, "organization-refinement-round-parent"):
            self.c.assess_organization(
                self.scope.subject(), [valid_shard], tree_source,
                max_bucket=1, allowed_depth=2, refinement_round=1)
        with self.assertRaisesRegex(Refusal, "invalid-outcome-selection"):
            self.c.candidate_outcome(
                self.scope.subject(), needs, "bad selection", [{}])

        foreign = self.c.body(valid_source)
        foreign["world_id"] = "foreign-world"
        foreign_source = self.c.emit(foreign)
        with self.assertRaisesRegex(Refusal, "subject-or-world-substitution"):
            self.c.register_catalog_shard(self.scope.subject(), foreign_source)

    def test_recursive_catalog_subject_and_refinement_restrictions_do_not_widen(self):
        first_scope = Scope("catalog", "first")
        second_scope = Scope("catalog", "second")
        policy = replace(
            self.policy,
            scopes=(first_scope, second_scope),
            audience=("A", "B"),
            max_frames=128,
        )
        controller = Controller(
            self.core, self.root / "recursive-controller", policy, now=NOW)
        self.addCleanup(controller.close)
        controller.seed(first_scope.subject())
        entry = {"id": "repo:a", "kind": "git-repository", "parent": "github:kody-w",
                 "labels": [], "metadata_sha256": "1" * 64,
                 "share_class": "public-source"}
        document = {
            "schema": "rapp-workspace/catalog-chunk/1",
            "catalog_id": "github:kody-w",
            "root_id": "github:kody-w",
            "shard_index": 0,
            "shard_count": 1,
            "snapshot_sha256": catalog_snapshot([entry]),
            "branch_scope": "default-branch-only",
            "branch_evidence_status": "external-host-observation-unproven",
            "recursive": False,
            "entries": [entry],
        }
        source = controller.capture_octets(
            first_scope.subject(), self.core.octets(document))["source"]
        shard = controller.register_catalog_shard(first_scope.subject(), source)
        broad = organization_tiles(
            "github:kody-w",
            [{"id": "root", "name": "GitHub", "parent": None}],
            [],
        )[0]
        foreign_tree = controller.capture_octets(
            second_scope.subject(), self.core.octets(broad))["source"]
        with self.assertRaisesRegex(Refusal, "subject-or-world-substitution"):
            controller.assess_organization(
                second_scope.subject(), [shard], foreign_tree,
                max_bucket=1, allowed_depth=2)

        restricted = controller.restrictions()
        restricted["audience"] = ["A"]
        broad_source = controller.capture_octets(
            first_scope.subject(), self.core.octets(broad),
            inherited=[restricted])["source"]
        needs = controller.assess_organization(
            first_scope.subject(), [shard], broad_source,
            max_bucket=1, allowed_depth=2)
        refined = organization_tiles(
            "github:kody-w",
            [{"id": "root", "name": "GitHub", "parent": None}],
            [{"entry_id": "repo:a", "group_id": "root"}],
        )[0]
        refined_source = controller.capture_octets(
            first_scope.subject(), self.core.octets(refined))["source"]
        verified = controller.assess_organization(
            first_scope.subject(), [shard], refined_source,
            max_bucket=1, allowed_depth=2, refinement_round=1, previous=needs)
        self.assertEqual(controller.body(verified)["status"], "verified")
        self.assertEqual(controller.body(verified)["restrictions"]["audience"], ["A"])

    def test_tiled_organization_scales_without_one_giant_tree_document(self):
        policy = replace(
            self.policy,
            max_frames=512,
            max_total_octets=4 * 1024 * 1024,
        )
        controller = Controller(
            self.core, self.root / "tiled-controller", policy, now=NOW)
        self.addCleanup(controller.close)
        controller.seed(self.scope.subject())
        entries = [
            {
                "id": f"repo:{index:04d}",
                "kind": "git-repository-default-branch",
                "parent": "github:synthetic",
                "labels": [f"group-{index % 16:02d}"],
                "metadata_sha256": sha(str(index).encode("ascii")),
                "share_class": "public-source",
            }
            for index in range(1024)
        ]
        catalog_digest = catalog_snapshot(entries)
        shards = []
        for index in range(4):
            document = {
                "schema": "rapp-workspace/catalog-chunk/1",
                "catalog_id": "github:synthetic",
                "root_id": "github:synthetic",
                "shard_index": index,
                "shard_count": 4,
                "snapshot_sha256": catalog_digest,
                "branch_scope": "default-branch-only",
                "branch_evidence_status": "external-host-observation-unproven",
                "recursive": True,
                "entries": entries[index * 256:(index + 1) * 256],
            }
            raw = self.core.octets(document)
            self.assertLessEqual(len(raw), 65536)
            source = controller.capture_octets(self.scope.subject(), raw)["source"]
            shards.append(controller.register_catalog_shard(self.scope.subject(), source))
        groups = [{"id": "root", "name": "Synthetic", "parent": None}] + [
            {"id": f"group-{index:02d}", "name": f"Outcome {index:02d}", "parent": "root"}
            for index in range(16)
        ]
        assignments = [
            {"entry_id": entry["id"], "group_id": f"group-{index % 16:02d}"}
            for index, entry in enumerate(entries)
        ]
        documents = organization_tiles(
            "github:synthetic", groups, assignments,
            tree_id="github:synthetic:outcomes", tile_count=4)
        tree_sources = []
        for document in documents:
            raw = self.core.octets(document)
            self.assertLessEqual(len(raw), 65536)
            tree_sources.append(
                controller.capture_octets(self.scope.subject(), raw)["source"])
        with self.assertRaisesRegex(Refusal, "incomplete-organization-tiles"):
            controller.assess_organization(
                self.scope.subject(), shards, tree_sources[:-1],
                max_bucket=64, allowed_depth=3)
        mixed_document = {**documents[0], "snapshot_sha256": "f" * 64}
        mixed_source = controller.capture_octets(
            self.scope.subject(), self.core.octets(mixed_document))["source"]
        with self.assertRaisesRegex(Refusal, "organization-tile-family-mismatch"):
            controller.assess_organization(
                self.scope.subject(), shards, [mixed_source, *tree_sources[1:]],
                max_bucket=64, allowed_depth=3)
        assessment = controller.assess_organization(
            self.scope.subject(), shards, tree_sources,
            max_bucket=64, allowed_depth=3)
        body = controller.body(assessment)
        self.assertEqual(body["status"], "verified")
        self.assertEqual(body["entry_count"], 1024)
        self.assertEqual(body["assigned_count"], 1024)
        self.assertEqual(body["largest_bucket"], 64)
        self.assertEqual(len(body["tree_sources"]), 4)

    def test_schemas_are_closed_bounded_and_workspace1_core_only(self):
        for filename, definition in schemas().items():
            self.assertEqual(read_file(REFERENCE.parent / "schemas" / filename), encode(definition))
            def visit(value):
                if isinstance(value, dict):
                    if value.get("type") == "object":
                        self.assertFalse(value["additionalProperties"])
                        self.assertEqual(set(value["properties"]), set(value["required"]))
                    if value.get("type") == "array":
                        self.assertIn("maxItems", value)
                    if value.get("type") == "string":
                        self.assertIn("maxLength", value)
                    for child in value.values():
                        visit(child)
                elif isinstance(value, list):
                    for child in value:
                        visit(child)
            visit(definition)


if __name__ == "__main__":
    unittest.main()
