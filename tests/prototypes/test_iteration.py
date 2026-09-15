"""Adversarial bounded iteration, dedupe, branching and refusal-driven lens repair."""

import copy
import os
from pathlib import Path
import shutil
import sys
import unittest
import uuid

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "protocols/rapp-workspace/prototypes/grail-1.0/experimental/reference"))
from common import Parent, Refusal, address, write_file
from framing import capture_object, frame_object, synthesize_attempt, synthesize_context_attempt
from iteration import LensLoop, attempt_payload, information, pending, state, work_key
from test_frame_lens import Fixture, UTC
from workspace import Workspace


class IterationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.core = Parent(os.environ.get("RAPP1_PATH"))

    def setUp(self):
        self.root = REPO / ".validation/test-artifacts" / ("iteration-" + uuid.uuid4().hex)
        self.root.mkdir(parents=True)
        self.addCleanup(shutil.rmtree, self.root)
        self.fx = Fixture(self.core, 120000)
        self.w = self.fx.w
        self.context_path = self.root / "container"
        write_file(self.context_path / "unknown.manifest", b'{"foreign":"opaque"}')
        write_file(self.context_path / "companion.info", b"explicit additional context")
        self.source, self.observation, _ = frame_object(self.w, self.context_path / "unknown.manifest", UTC)
        program = synthesize_attempt(self.core, self.w.body(self.source), self.w.body(self.observation))
        self.lens = self.w.lens("lens-A", [self.observation], program, self.fx.owner, UTC)

    def context_lens(self, exhaust, path=None):
        context, observed, _ = frame_object(self.w, path or self.context_path, UTC)
        program = synthesize_context_attempt(self.core, self.w.body(self.source), self.w.body(self.observation),
                                             self.w.body(exhaust), self.w.body(context), self.w.body(observed))
        lens = self.w.lens("lens-B", [self.observation, observed], program, self.fx.owner, UTC)
        return lens, [self.source, self.observation, exhaust, context, observed]

    def first(self, **limits):
        loop = LensLoop.create(self.w, self.source, UTC, **limits)
        request = loop.submit(self.lens, [self.source, self.observation])
        attempt = loop.step()
        return loop, request, attempt, self.w.body(attempt)["exhaust"]

    def review(self, loop, attempt, exhaust):
        request = self.w.body(self.w.body(attempt)["request"])
        self.fx.approve(self.w.adoption_payload(request["lens"], exhaust["equivalence"]))
        self.fx.approve(self.w.adoption_payload(exhaust["result"], exhaust["equivalence"]))

    def test_refusal_exhaust_drives_new_lens_context_to_verified_adoption(self):
        before = capture_object(self.context_path)
        loop, _, first, exhausted = self.first()
        self.assertEqual(self.w.body(exhausted)["classification"], "unresolved")
        lens, inputs = self.context_lens(exhausted)
        second_request = loop.submit(lens, inputs, parents=[first])
        stop = loop.run(reviewer=self.review)
        s = state(self.w, loop.ref)
        self.assertEqual(len(s["attempts"]), 2)
        self.assertEqual(self.w.body(stop)["reason"], "adopted-verified")
        second = list(s["attempts"].values())[-1]
        self.assertEqual(second["parents"], [first])
        self.assertEqual(second["request"], second_request)
        result = self.w.body(self.w.body(second["exhaust"])["result"])
        self.assertEqual(result["feedback"], exhausted)
        self.assertTrue(result["adoption_eligible"])
        self.assertTrue(second["new_information"])
        self.assertEqual(before, capture_object(self.context_path))

    def test_same_lens_reapplication_dedupes_to_stable_honest_refusal(self):
        loop, _, first, exhausted = self.first()
        retry = loop.submit(self.lens, [self.source, self.observation], parents=[first], strategy="reapply")
        attempt = loop.step()
        value = self.w.body(attempt)
        self.assertEqual(value["request"], retry)
        self.assertEqual(value["execution"], "deduplicated")
        self.assertEqual(value["duplicate_of"], first)
        self.assertEqual(value["exhaust"], exhausted)
        self.assertTrue(value["repeated_state"])
        self.assertEqual(value["new_information"], [])
        self.assertEqual(self.w.body(loop.finish())["reason"], "stable-fixed-point")

    def test_cycling_lenses_and_tick_only_changes_do_not_create_progress(self):
        loop, _, first, _ = self.first()
        program = copy.deepcopy(self.w.body(self.lens)["program"])
        program["tick"] = 777
        renamed = self.w.lens("new-label-is-not-information", [self.observation], program, self.fx.owner, UTC)
        loop.submit(renamed, [self.source, self.observation], parents=[first])
        attempt = loop.step()
        self.assertEqual(self.w.body(attempt)["execution"], "deduplicated")
        self.assertEqual(self.w.body(loop.finish())["reason"], "stable-fixed-point")
        with self.assertRaisesRegex(Refusal, "stopped"):
            loop.submit(self.lens, [self.source, self.observation], parents=[attempt], strategy="reapply")

    def test_ping_pong_and_different_programs_with_identical_semantic_output_stop(self):
        a = self.w.lens("A", [self.observation],
                        {"op": "identity", "read": {"name": "whole", "input": 0, "pointer": ""}}, self.fx.owner, UTC)
        b = self.w.lens("B", [self.observation],
                        {"op": "amend", "read": {"name": "whole", "input": 0, "pointer": ""},
                         "changes": [{"pointer": "/subject", "value": "cosmetic-change"}]}, self.fx.owner, UTC)
        loop = LensLoop.create(self.w, self.source, UTC)
        loop.submit(a, [self.source])
        first = loop.step()
        loop.submit(b, [self.source], parents=[first])
        second = loop.step()
        p = self.w.body(second)
        self.assertEqual(p["execution"], "executed")
        self.assertTrue(p["repeated_state"])
        self.assertEqual(p["new_information"], [])
        loop.submit(a, [self.source], parents=[second])
        stop = loop.run()
        self.assertEqual(self.w.body(stop)["reason"], "stable-fixed-point")
        self.assertEqual(len(self.w.body(stop)["attempts"]), 2)
        self.assertEqual(len(self.w.body(stop)["pending"]), 1)

    def test_fabricated_progress_and_depth_are_refused_without_history_change(self):
        loop, _, first, exhausted = self.first()
        request = loop.submit(self.lens, [self.source, self.observation], parents=[first], strategy="reapply")
        candidate = attempt_payload(self.w, loop.ref, request, exhausted)
        candidate["new_information"] = [{"space": "rapp/1:particle", "hash": "f" * 64}]
        candidate["no_progress"] = 0
        before = self.w.checkpoint()
        with self.assertRaisesRegex(Refusal, "fabricated progress"):
            self.w.append(candidate, UTC)
        self.assertEqual(before, self.w.checkpoint())
        candidate = copy.deepcopy(self.w.body(request))
        candidate["depth"] = 0
        with self.assertRaisesRegex(Refusal, "fabricated depth"):
            self.w.append(candidate, UTC)

    def test_failed_test_is_exhaust_and_same_lens_can_retry_corrected_reads(self):
        context, observation, _ = frame_object(self.w, self.context_path, UTC)
        program = synthesize_attempt(self.core, self.w.body(context), self.w.body(observation))
        lens = self.w.lens("correctable", [observation], program, self.fx.owner, UTC)
        wrong = self.w.reads_payload(lens, [context, observation])
        wrong["complete"] = False
        wrong_ref = self.w.append(wrong, UTC)
        loop = LensLoop.create(self.w, context, UTC)
        loop.submit(lens, [context, observation], declared_reads=wrong_ref)
        failed = loop.step()
        exhausted = self.w.body(self.w.body(failed)["exhaust"])
        self.assertEqual(exhausted["classification"], "failed-test")
        self.assertIsNone(exhausted["result"])
        loop.submit(lens, [context, observation], parents=[failed], strategy="reapply")
        stop = loop.run(reviewer=self.review)
        self.assertEqual(self.w.body(stop)["reason"], "adopted-verified")

    def test_descendant_lens_requires_actual_mutation_lineage_and_cannot_reset_work(self):
        loop, _, first, _ = self.first()
        modifier = self.w.lens("modifier", [self.observation],
            {"op": "amend", "read": {"name": "whole", "input": 0, "pointer": ""},
             "changes": [{"pointer": "/label", "value": "A-prime"}]}, self.fx.owner, UTC)
        _, _, descendant = self.fx.trial(modifier, [self.lens])
        loop.submit(descendant, [self.source, self.observation], parents=[first],
                    strategy="descendant", lens_parent=self.lens)
        attempt = loop.step()
        self.assertEqual(self.w.body(attempt)["execution"], "deduplicated")
        unrelated = self.w.lens("unrelated", [self.observation], self.w.body(self.lens)["program"], self.fx.owner, UTC)
        with self.assertRaisesRegex(Refusal, "fabricated lens descendant"):
            loop.submit(unrelated, [self.source, self.observation], parents=[first],
                        strategy="descendant", lens_parent=self.lens)

    def test_branches_keep_parent_sets_and_use_deterministic_work_key_order(self):
        loop, _, first, exhausted = self.first()
        wrong = self.root / "wrong-context"
        write_file(wrong / "unknown.manifest", b"contradictory bytes")
        write_file(wrong / "other", b"x")
        absent = self.root / "absent-context"
        write_file(absent / "one", b"x")
        write_file(absent / "two", b"y")
        requests = []
        for path in (wrong, absent):
            lens, inputs = self.context_lens(exhausted, path)
            requests.append(loop.submit(lens, inputs, parents=[first]))
        expected = pending(state(self.w, loop.ref))
        self.assertEqual(set(map(address, expected)), set(map(address, requests)))
        seen = []
        for _ in range(2):
            ref = loop.step()
            p = self.w.body(ref)
            seen.append(p["request"])
            self.assertEqual(p["parents"], [first])
        self.assertEqual(seen, expected)
        classes = {self.w.body(p["exhaust"])["classification"] for p in state(self.w, loop.ref)["attempts"].values()}
        self.assertTrue({"partial", "contradiction"} <= classes)
        self.assertTrue(all(address(r) in self.w._raw for r in requests))

    def test_attempt_depth_and_missing_authority_terminate_explicitly(self):
        for limit, reason in (({"max_attempts": 1}, "attempt-budget"), ({"max_depth": 0}, "depth-budget")):
            loop, _, first, exhausted = self.first(**limit)
            lens, inputs = self.context_lens(exhausted)
            loop.submit(lens, inputs, parents=[first])
            self.assertEqual(self.w.body(loop.run())["reason"], reason)
        loop, _, first, exhausted = self.first()
        lens, inputs = self.context_lens(exhausted)
        loop.submit(lens, inputs, parents=[first])
        stop = loop.run(reviewer=lambda *args: True)
        self.assertEqual(self.w.body(stop)["reason"], "missing-owner-authorization")
        self.assertIsNotNone(self.w.body(stop)["candidate"])

    def test_loop_history_and_dedupe_state_reconstruct_on_restart(self):
        loop, _, first, exhausted = self.first()
        retry = loop.submit(self.lens, [self.source, self.observation], parents=[first], strategy="reapply")
        store = self.root / "saved"
        self.w.save(store)
        restored = Workspace.load(self.core, store, self.w.consent, self.w.checkpoint())
        resumed = LensLoop(restored, loop.ref, UTC)
        attempt = resumed.step()
        self.assertEqual(restored.body(attempt)["request"], retry)
        self.assertEqual(restored.body(attempt)["execution"], "deduplicated")
        self.assertEqual(restored.body(resumed.finish())["reason"], "stable-fixed-point")
        self.assertEqual(restored._raw[address(exhausted)], self.w._raw[address(exhausted)])

    def test_same_content_addressed_lens_retries_when_missing_context_arrives(self):
        loop, _, first, exhausted = self.first()
        lens, complete_inputs = self.context_lens(exhausted)
        loop.submit(lens, complete_inputs[:3], parents=[first])
        failed = loop.step()
        self.assertEqual(self.w.body(self.w.body(failed)["exhaust"])["classification"], "failed-test")
        loop.submit(lens, complete_inputs, parents=[first, failed], strategy="reapply")
        stop = loop.run(reviewer=self.review)
        self.assertEqual(self.w.body(stop)["reason"], "adopted-verified")
        last = list(state(self.w, loop.ref)["attempts"].values())[-1]
        self.assertEqual(self.w.body(last["request"])["lens"], lens)
        self.assertEqual(last["execution"], "executed")

    def test_consumed_exhaust_cannot_omit_its_attempt_parent(self):
        loop, _, first, exhausted = self.first()
        lens, inputs = self.context_lens(exhausted)
        before = self.w.checkpoint()
        with self.assertRaisesRegex(Refusal, "parent omitted"):
            loop.submit(lens, inputs)
        self.assertEqual(before, self.w.checkpoint())
        loop.submit(lens, inputs, parents=[first])

    def test_switching_to_an_unrelated_root_cannot_fake_mission_success(self):
        loop, _, first, _ = self.first()
        other, obs, _ = frame_object(self.w, self.context_path, UTC)
        program = synthesize_attempt(self.core, self.w.body(other), self.w.body(obs))
        lens = self.w.lens("unrelated-source-success", [obs], program, self.fx.owner, UTC)
        loop.submit(lens, [other, obs], parents=[first])
        attempted = loop.step()
        exhausted = self.w.body(self.w.body(attempted)["exhaust"])
        self.assertEqual(exhausted["classification"], "refusal")
        self.assertEqual(exhausted["code"], "foreign-root-result")
        self.assertEqual(self.w.body(loop.finish())["reason"], "explicit-refusal")

    def test_rewritten_diagnostic_is_inert_data_not_fabricated_progress(self):
        loop, _, first, exhausted = self.first()
        modifier = self.w.lens("rewrite-diagnostic-candidate", [self.observation],
            {"op": "amend", "read": {"name": "whole", "input": 0, "pointer": ""},
             "changes": [{"pointer": "/code", "value": "source-not-bound-to-context"}]}, self.fx.owner, UTC)
        _, _, rewritten = self.fx.trial(modifier, [exhausted])
        with self.assertRaisesRegex(Refusal, "fabricated diagnostic"):
            information(self.w, [rewritten])
        lens, inputs = self.context_lens(exhausted)
        inputs[2] = rewritten
        with self.assertRaisesRegex(Refusal, "fabricated diagnostic"):
            loop.submit(lens, inputs, parents=[first])

    def test_arbitrary_new_labels_are_not_new_information(self):
        loop = LensLoop.create(self.w, self.source, UTC)
        fake1 = self.w.append({"claimed_progress": "new information", "nonce": 1}, UTC)
        fake2 = self.w.append({"claimed_progress": "even more", "nonce": 2}, UTC)
        loop.submit(self.lens, [self.source, self.observation], contexts=[fake1])
        first = loop.step()
        loop.submit(self.lens, [self.source, self.observation], contexts=[fake2], parents=[first], strategy="reapply")
        second = loop.step()
        self.assertEqual(self.w.body(second)["new_information"], [])
        self.assertEqual(self.w.body(loop.finish())["reason"], "stable-fixed-point")


if __name__ == "__main__":
    unittest.main()
