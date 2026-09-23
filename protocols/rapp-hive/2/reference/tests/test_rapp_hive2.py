"""rapp-hive/2 reference tests (experimental frontier). Run: python3 -B -m unittest discover -s protocols/rapp-hive/2/reference/tests"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
REFERENCE = HERE.parent
PROTOCOL = REFERENCE.parent
sys.path.insert(0, str(REFERENCE))
sys.path.insert(0, str(PROTOCOL.parent / "1" / "reference"))

from rapp_hive2 import crossing, hive, migrate, model, rapp1, sign, store, vectors  # noqa: E402
from rapp_hive2.rapp1 import Refusal  # noqa: E402

BUILT = model.build()


def written(files: dict[str, bytes]) -> tuple[tempfile.TemporaryDirectory, Path]:
    scratch = tempfile.TemporaryDirectory()
    folder = Path(scratch.name) / "hive"
    store.write_new_tree(folder, files)
    return scratch, folder


class ConformanceTests(unittest.TestCase):
    def test_committed_vectors_are_current_and_pass(self) -> None:
        committed = (PROTOCOL / "conformance" / "vectors.json").read_bytes()
        self.assertEqual(vectors.encode(vectors.generate()), committed, "regenerate: python3 -B -m rapp_hive2 vectors --write ../conformance/vectors.json")
        outcome = vectors.check(json.loads(committed))
        self.assertEqual(outcome["failed"], [])
        self.assertGreaterEqual(outcome["passed"], 60)

    def test_the_model_is_deterministic(self) -> None:
        self.assertEqual(model.build()["hive"], BUILT["hive"])

    def test_the_model_tells_the_whole_story(self) -> None:
        scratch, folder = written(BUILT["hive"])
        with scratch:
            _carried, _records, evaluation, verdict = hive.evaluate_folder(folder)
        slugs = {rappid: info["slug"] for rappid, info in BUILT["people"].items()}
        self.assertEqual([slugs[item] for item in verdict["state"]["members"]], ["avery-laptop", "blake-phone", "casey-tablet", "drew-desktop", "emery-kiosk"])
        self.assertTrue(evaluation.members[next(r for r, s in slugs.items() if s == "emery-kiosk")]["legacy"])
        self.assertEqual([slugs[request["requester"]] for request in evaluation.pending.values()], ["frankie-laptop"])
        self.assertEqual({item["code"] for item in verdict["refusals"]}, {"REFUSE_STALE", "REFUSE_LENS_LAW"})
        self.assertEqual([evaluation.lens_objects[p]["version"] for p in evaluation.derived], [2])
        self.assertEqual({key: evaluation.lens_objects[value]["version"] for key, value in evaluation.active.items()}, {"contoso-tasks": 3, "phone-tasks": 1})
        self.assertEqual([(item["code"], len(item["waiting"])) for item in verdict["exhausts"]], [("no-lens", 1)])
        self.assertEqual(len(verdict["quarantined"]), 1)
        self.assertEqual(sorted(item["position"] for item in verdict["manifests"]), ["agrees", "agrees", "agrees", "behind"])
        self.assertTrue(all(item["verdict"] == "consistent" for item in verdict["manifests"]))

    def test_crossings_never_invent_and_name_what_stays_behind(self) -> None:
        scratch, folder = written(BUILT["hive"])
        with scratch:
            _carried, _records, evaluation, _verdict = hive.evaluate_folder(folder)
        phone, laptop, tablet = (item["source"] for item in BUILT["crossings"])
        with self.assertRaises(Refusal) as refused:
            crossing.cross_to_member(evaluation, phone, "avery-laptop")
        self.assertEqual(refused.exception.code, "REFUSE_CROSSING")
        to_phone = crossing.cross_to_member(evaluation, laptop, "blake-phone")
        self.assertEqual((to_phone["not_expressible_in_target"], to_phone["signed"], to_phone["authority"]), (["due"], False, False))
        self.assertEqual(set(to_phone["payload"]), {"assignee", "id", "operation", "profile", "text"})
        self.assertTrue(crossing.cross_to_member(evaluation, tablet, "avery-laptop")["lossless"])


class LegacyAndMigrationTests(unittest.TestCase):
    def test_the_legacy_declaration_is_valid_under_rapp_hive_1s_own_rules(self) -> None:
        import rapp_hive  # the rapp-hive/1 reference, unchanged

        declaration = next(json.loads(data) for path, data in BUILT["before"].items() if path.startswith("streams/contoso-hive.mother."))
        self.assertEqual(declaration["kind"], "hive.declaration")
        self.assertEqual(rapp_hive.validate_declaration(declaration["payload"]), rapp1.particle(declaration["payload"]))

    def test_migration_is_reproducible_from_the_before_snapshot(self) -> None:
        scratch, folder = written(BUILT["before"])
        with scratch:
            carried = hive.load(folder)
            records = hive.verify_frames(carried)
            declaration = next(item.wave for item in records if item.kind == "hive.declaration")
            request = next(item.wave for item in records if item.frame["payload"].get("operation") == "join-request")
            plan = migrate.plan_from_rapp_hive_1(carried, records, declaration, name=model.NAME, legacy_requests=[request])
            self.assertEqual(plan, BUILT["plan"])
            for slug, phase, utc in (("avery-laptop", 1, "2026-09-21T09:00:00.000Z"), ("blake-phone", 1, "2026-09-21T09:05:00.000Z"), ("casey-tablet", 1, "2026-09-21T09:10:00.000Z"), ("avery-laptop", 2, "2026-09-21T09:20:00.000Z")):
                migrate.apply(plan, folder, model.signer(slug), phase=phase, utc=utc)
            for path in hive._files(folder):
                if path.startswith("streams/"):
                    self.assertEqual((folder / path).read_bytes(), BUILT["hive"][path], path)

    def test_a_signer_can_only_apply_its_own_steps_in_order(self) -> None:
        scratch, folder = written(BUILT["before"])
        with scratch:
            carried = hive.load(folder)
            records = hive.verify_frames(carried)
            declaration = next(item.wave for item in records if item.kind == "hive.declaration")
            plan = migrate.plan_from_rapp_hive_1(carried, records, declaration, name=model.NAME)
            with self.assertRaises(Refusal) as refused:
                migrate.apply(plan, folder, model.signer("drew-desktop"), phase=1, utc="2026-09-21T09:00:00.000Z")
            self.assertEqual(refused.exception.code, "REFUSE_NOT_YOURS")
            with self.assertRaises(Refusal) as refused:
                migrate.apply(plan, folder, model.signer("avery-laptop"), phase=2, utc="2026-09-21T09:00:00.000Z")
            self.assertEqual(refused.exception.code, "REFUSE_ORDER")
            tampered = {**plan, "notes": ["trust me"]}
            with self.assertRaises(Refusal) as refused:
                migrate.apply(tampered, folder, model.signer("avery-laptop"), phase=1, utc="2026-09-21T09:00:00.000Z")
            self.assertEqual(refused.exception.code, "REFUSE_TAMPER")

    def test_path_b_carries_old_join_requests_without_an_override(self) -> None:
        scratch, folder = written(BUILT["before"])
        with scratch:
            carried = hive.load(folder)
            records = hive.verify_frames(carried)
            request = next(item for item in records if item.frame["payload"].get("operation") == "join-request")
            founders = [model.signer("avery-laptop").rappid, model.signer("blake-phone").rappid]
            plan = migrate.plan_from_join_requests(records, name="Seeded model", world_id="seeded-model", founders=founders, requests=[request.wave], quorum=2, source="repository-seeded-private-hive")
            for slug, utc in (("avery-laptop", "2026-09-21T09:00:00.000Z"), ("blake-phone", "2026-09-21T09:01:00.000Z")):
                migrate.apply(plan, folder, model.signer(slug), phase=1, utc=utc)
            migrate.apply(plan, folder, model.signer("avery-laptop"), phase=2, utc="2026-09-21T09:02:00.000Z")
            _c, _r, evaluation, _v = hive.evaluate_folder(folder)
            self.assertIn(request.wave, evaluation.pending)
            migrate.apply(plan, folder, model.signer("blake-phone"), phase=2, utc="2026-09-21T09:03:00.000Z")
            _c, _r, evaluation, _v = hive.evaluate_folder(folder)
            self.assertEqual(evaluation.members[request.owner]["legacy"], True)


class IndexTests(unittest.TestCase):
    def test_the_protocol_index_pins_these_exact_documents(self) -> None:
        import hashlib

        repo = PROTOCOL.parent.parent.parent
        index = json.loads((repo / "protocols" / "index.json").read_text(encoding="utf-8"))
        entries = {entry["name"]: entry for entry in index["profiles"]}
        for name in ("rapp-hive/2", "rapp-schema/1"):
            entry = entries[name]
            self.assertEqual((entry["status"], entry["ring"], entry["authority"]), ("experimental-frontier", "canary", False))
            for key in ("spec", "migration", "conformance_vectors"):
                if f"{key}_path" in entry:
                    data = (repo / entry[f"{key}_path"]).read_bytes()
                    self.assertEqual((hashlib.sha256(data).hexdigest(), len(data)), (entry[f"{key}_sha256"], entry[f"{key}_bytes"]), f"{name} {key}")


class CarrierTests(unittest.TestCase):
    def test_links_and_renamed_objects_are_refused(self) -> None:
        scratch, folder = written(BUILT["hive"])
        with scratch:
            if os.name != "nt":
                target = next((folder / "objects").iterdir())
                (folder / "objects" / "link.json").symlink_to(target)
                with self.assertRaises(Refusal) as refused:
                    hive.load(folder)
                self.assertEqual(refused.exception.code, "REFUSE_UNSAFE_PATH")
                (folder / "objects" / "link.json").unlink()
            name = next((folder / "objects").iterdir())
            name.rename(name.with_name("0" * 64 + ".json"))
            with self.assertRaises(Refusal) as refused:
                hive.load(folder)
            self.assertEqual(refused.exception.code, "REFUSE_TAMPER")

    def test_the_command_line_answers_in_plain_language(self) -> None:
        with tempfile.TemporaryDirectory() as scratch:
            run = lambda *args: subprocess.run([sys.executable, "-B", "-m", "rapp_hive2", *args], cwd=REFERENCE, capture_output=True, text=True, timeout=300)  # noqa: E731
            built = run("model", str(Path(scratch) / "m"))
            self.assertEqual(built.returncode, 0, built.stderr)
            status = json.loads(run("status", str(Path(scratch) / "m" / "hive")).stdout)
            self.assertTrue(any("Waiting: frankie-laptop" in line for line in status["summary"]))
            verify = json.loads(run("verify", str(Path(scratch) / "m" / "before")).stdout)
            self.assertEqual(verify["refusal"]["code"], "REFUSE_ANCHOR")


if __name__ == "__main__":
    unittest.main()
