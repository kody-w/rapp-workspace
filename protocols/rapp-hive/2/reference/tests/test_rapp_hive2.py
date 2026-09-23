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

from rapp_hive2 import crossing, hive, lens as lensmod, migrate, model, rapp1, schema as schemas, sign, store, vectors  # noqa: E402
from rapp_hive2.rapp1 import Refusal  # noqa: E402

BUILT = model.build()


def written(files: dict[str, bytes]) -> tuple[tempfile.TemporaryDirectory, Path]:
    scratch = tempfile.TemporaryDirectory()
    folder = Path(scratch.name) / "hive"
    store.write_new_tree(folder, files)
    return scratch, folder


def evaluated(files: dict[str, bytes]) -> tuple[hive.Evaluation, dict]:
    scratch, folder = written(files)
    with scratch:
        _carried, _records, evaluation, verdict = hive.evaluate_folder(folder)
    return evaluation, verdict


def slug_of(slug: str) -> str:
    return model.signer(slug).rappid


def frames_of(files: dict[str, bytes]) -> list[dict]:
    return [json.loads(data) for path, data in sorted(files.items()) if path.startswith("streams/")]


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
        self.assertEqual([item["code"] for item in verdict["refusals"]], ["REFUSE_NOT_DECIDER", "REFUSE_STALE", "REFUSE_LENS_LAW"])
        self.assertEqual(evaluation.members[slug_of("emery-kiosk")]["grants"], [slug_of("avery-laptop")])
        self.assertEqual([evaluation.lens_objects[p]["version"] for p in evaluation.derived], [2])
        self.assertEqual({key: evaluation.lens_objects[value]["version"] for key, value in evaluation.active.items()}, {"contoso-tasks": 3, "phone-tasks": 1})
        self.assertEqual([(item["code"], len(item["waiting"])) for item in verdict["exhausts"]], [("no-lens", 1)])
        self.assertEqual(len(verdict["quarantined"]), 1)
        self.assertEqual(sorted(item["position"] for item in verdict["manifests"]), ["agrees", "agrees", "agrees", "behind"])
        self.assertTrue(all(item["verdict"] == "consistent" for item in verdict["manifests"]))

    def test_quarantined_messages_never_teach_or_veto_lenses(self) -> None:
        evaluation, verdict = evaluated(BUILT["hive"])
        (quarantined,) = [record for record in evaluation.quarantine]
        self.assertEqual(quarantined.owner, slug_of("frankie-laptop"))
        self.assertEqual(verdict["quarantined"], [quarantined.wave])
        laptop_v1 = next(value for value in evaluation.schemas.values() if value["payload"].keys() == {"due", "operation", "owner", "profile", "task_id", "title"})
        outsider = schemas.schema_of(quarantined.frame)
        self.assertTrue(schemas.is_additive(outsider, laptop_v1), "the outsider's shape would qualify if it were a member's")
        accepted = {particle for lens in (evaluation.lens_objects[p] for p in evaluation.history) for mapping in lens["mappings"] for particle in mapping["accepts"]}
        self.assertNotIn(schemas.particle(outsider), accepted)
        self.assertEqual([evaluation.lens_objects[p]["version"] for p in evaluation.derived], [2])
        self.assertNotIn(quarantined.wave, {record.wave for record in evaluation.content})

    def test_the_steward_alone_decides_until_the_peers_take_over(self) -> None:
        files = {path: data for path, data in BUILT["hive"].items() if not path.startswith("streams/") or json.loads(data)["utc"] < "2026-09-22"}
        anchor = json.loads(BUILT["hive"]["HIVE.json"])["anchor"]
        policies = {rapp1.particle(value): value for value in (json.loads(data) for path, data in files.items() if path.startswith("objects/")) if value.get("schema") == hive.POLICY}
        steward = next(key for key, value in policies.items() if value["version"] == 1)
        peers = next(key for key, value in policies.items() if value["version"] == 2)
        self.assertEqual(policies[steward]["deciders"], [slug_of("avery-laptop")])
        blake = model.signer("blake-phone")
        head = max((frame for frame in frames_of(files) if frame["stream_id"] == blake.stream("hive")), key=lambda frame: frame["seq"])
        grab = blake.frame("hive2.adopt", "hive", {"schema": "rapp-hive/2-adopt", "anchor": anchor, "object": peers, "predecessor": steward}, "2026-09-21T12:00:00.000Z", head)
        files[sign.frame_path(grab)] = rapp1.canonical(grab)
        evaluation, verdict = evaluated(files)
        self.assertEqual(evaluation.policy_chain, [steward])
        self.assertIn({"wave": grab["frame_hash"], "code": "REFUSE_NOT_DECIDER"}, verdict["refusals"])

    def test_the_newest_manifest_counts_across_streams(self) -> None:
        variant = model.build(divergent_manifest=True)
        evaluation, _verdict = evaluated(variant["hive"])
        scratch, folder = written(variant["hive"])
        with scratch:
            carried = hive.load(folder)
            records = hive.verify_frames(carried)
        drew = next(item for item in hive.manifests(carried, records, evaluation) if item["by"] == slug_of("drew-desktop"))
        self.assertEqual(drew["verdict"], "divergent")
        self.assertEqual(next(record for record in records if record.wave == drew["wave"]).stream, model.signer("drew-desktop").stream("manifest-backup"))

    def test_signed_but_malformed_governance_is_refused_without_effect(self) -> None:
        _evaluation, verdict = evaluated(model.build(adversarial=True)["hive"])
        _main, main = evaluated(BUILT["hive"])
        self.assertEqual(verdict["state"], main["state"])
        self.assertEqual([item["code"] for item in verdict["refusals"][len(main["refusals"]):]], ["REFUSE_STALE", "REFUSE_GOVERNANCE_SHAPE", "REFUSE_GOVERNANCE_SHAPE", "REFUSE_LEGACY_STREAM"])
        self.assertIn("unverifiable", [item["verdict"] for item in verdict["manifests"]])

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
        with self.assertRaises(Refusal) as refused:
            crossing.cross_to_member(evaluation, evaluation.quarantine[0].wave, "avery-laptop")
        self.assertEqual(refused.exception.code, "REFUSE_CROSSING")

    def test_crossings_report_what_the_forward_lens_actually_read(self) -> None:
        view = lensmod.check_view({"schema": lensmod.VIEW, "id": "note", "version": 1, "fields": {"title": "string"}})
        payload = {"profile": "notes/1", "operation": "note", "title": "keep", "alternate": "LOST", "meta": {"a": 1, "b": 2}}
        particle = schemas.particle(schemas.schema_of({"spec": "rapp/1", "kind": "memory.save", "payload": payload}))
        lens = lensmod.check_lens({"schema": lensmod.LENS, "id": "notes", "version": 1, "predecessor": None, "view": rapp1.particle(view), "mappings": [
            {"accepts": [particle], "forward": {"title": {"first": [{"select": "payload.title"}, {"select": "payload.alternate"}]}}, "reverse": None}]})
        trace = lensmod.new_trace()
        lensmod.forward(lens, 0, {"payload": payload}, view, trace)
        self.assertEqual(crossing.dropped_fields(payload, trace["used"]), ["alternate", "meta.a", "meta.b"])


class LegacyAndMigrationTests(unittest.TestCase):
    def test_the_legacy_declaration_is_valid_under_rapp_hive_1s_own_rules(self) -> None:
        import base64

        import rapp  # the rapp-hive/1 reference frame checks, unchanged
        import rapp_hive  # the rapp-hive/1 reference profile, unchanged

        declaration = next(frame for frame in frames_of(BUILT["before"]) if frame["kind"] == "hive.declaration")
        payload = declaration["payload"]
        owner = next(item["rappid"] for item in payload["members"] if item["role"] == "owner")
        identity = next(json.loads(data) for path, data in BUILT["before"].items() if path.startswith("identities/") and json.loads(data)["rappid"] == owner)
        spki = base64.b64decode(identity["spki_der_b64"])
        verifier = lambda value, sig: rapp.verify_detached_jws(value, sig, spki, expected_kid=owner)  # noqa: E731
        self.assertEqual(rapp.verify_frame(declaration, head=None, stream_id_of_record=payload["hive_rappid"], signature_verifier=verifier), (True, None, "ok"))
        self.assertEqual(declaration["stream_id"], payload["hive_rappid"])
        self.assertEqual(rapp.parse_detached_jws(declaration["sig"])[0]["kid"], owner)
        self.assertEqual(rapp_hive.validate_declaration(payload), rapp1.particle(payload))

    def test_a_rapp_hive_1_legacy_names_its_declaration(self) -> None:
        anchor = json.loads(next(data for path, data in BUILT["hive"].items() if path.startswith("objects/") and json.loads(data).get("schema") == hive.ANCHOR))
        for legacy in ({"from": "rapp-hive/1", "declaration": None, "join": None}, {"from": "seeded", "declaration": "0" * 64, "join": None}):
            with self.assertRaises(Refusal) as refused:
                hive.check_anchor({**anchor, "legacy": legacy})
            self.assertEqual(refused.exception.code, "REFUSE_SCHEMA")

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
            body = {key: value for key, value in plan.items() if key != "plan_particle"}
            body["steps"] = [{**plan["steps"][0], "drafts": [{"kind": "memory.save", "instance": "hive", "payload": {"anchor": plan["anchor"], "operation": "anything"}}]}]
            with self.assertRaises(Refusal) as refused:
                migrate.apply({**body, "plan_particle": rapp1.particle(body)}, folder, model.signer("avery-laptop"), phase=1, utc="2026-09-21T09:00:00.000Z")
            self.assertEqual(refused.exception.code, "REFUSE_TAMPER")
            migrate.apply(plan, folder, model.signer("avery-laptop"), phase=1, utc="2026-09-21T09:00:00.000Z")
            with self.assertRaises(Refusal) as refused:
                migrate.apply(plan, folder, model.signer("avery-laptop"), phase=1, utc="2026-09-21T09:01:00.000Z")
            self.assertEqual(refused.exception.code, "REFUSE_ALREADY_APPLIED")

    def test_path_b_carries_old_join_requests_without_an_override(self) -> None:
        scratch, folder = written(BUILT["before"])
        with scratch:
            carried = hive.load(folder)
            records = hive.verify_frames(carried)
            request = next(item for item in records if item.frame["payload"].get("operation") == "join-request")
            founders = [model.signer("avery-laptop").rappid, model.signer("blake-phone").rappid]
            plan = migrate.plan_from_join_requests(records, name="Seeded model", world_id="seeded-model", founders=founders, requests=[request.wave], quorum=2, source="repository-seeded-private-hive")
            with self.assertRaises(Refusal) as refused:
                migrate.apply(plan, folder, model.signer("avery-laptop"), phase=2, utc="2026-09-21T08:59:00.000Z")
            self.assertEqual(refused.exception.code, "REFUSE_ORDER")
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

    @unittest.skipIf(os.name == "nt" or not hasattr(os, "mkfifo"), "needs POSIX FIFOs")
    def test_special_files_are_refused_before_anything_reads_them(self) -> None:
        scratch, folder = written(BUILT["before"])
        with scratch:
            (folder / "objects").mkdir()
            os.mkfifo(folder / "objects" / ("0" * 64 + ".json"))
            with self.assertRaises(Refusal) as refused:
                hive.load(folder)
            self.assertEqual(refused.exception.code, "REFUSE_UNSAFE_PATH")

    def test_the_command_line_answers_in_plain_language(self) -> None:
        with tempfile.TemporaryDirectory() as scratch:
            run = lambda *args: subprocess.run([sys.executable, "-B", "-m", "rapp_hive2", *args], cwd=REFERENCE, capture_output=True, text=True, timeout=300)  # noqa: E731
            built = run("model", str(Path(scratch) / "m"))
            self.assertEqual(built.returncode, 0, built.stderr)
            status = json.loads(run("status", str(Path(scratch) / "m" / "hive")).stdout)
            self.assertTrue(any("Waiting: frankie-laptop" in line for line in status["summary"]))
            verify = json.loads(run("verify", str(Path(scratch) / "m" / "before")).stdout)
            self.assertEqual(verify["refusal"]["code"], "REFUSE_ANCHOR")


class FoundationTests(unittest.TestCase):
    def test_frames_obey_the_parent_rapp_1_grammar(self) -> None:
        avery = model.signer("avery-laptop")
        frame = next(frame for frame in frames_of(BUILT["hive"]) if frame["stream_id"] == avery.stream("hive") and frame["seq"] == 1)
        good = {"utc": "2028-02-29T23:59:59.999Z"}
        self.assertEqual(rapp1.frame_integrity(vectors._resigned(frame, avery, **good))["seq"], 1)
        cases = {
            "REFUSE_FRAME_TIME": [{"utc": "2026-02-29T09:00:00.000Z"}, {"utc": "2100-02-29T09:00:00.000Z"}, {"utc": "2026-09-22T24:00:00.000Z"}, {"utc": "2026-09-22T09:60:00.000Z"}, {"utc": "2026-09-22T09:00:60.000Z"}, {"utc": "0000-01-01T00:00:00.000Z"}],
            "REFUSE_FRAME_SHAPE": [{"kind": "Hive2.grant"}, {"kind": "hive2"}, {"kind": "a" * 65 + ".b"}, {"prev_wave": frame["frame_hash"]}, {"stream_id": "net:swarm"}, {"stream_id": avery.rappid + ":"}, {"stream_id": avery.rappid + ":Tasks"}, {"stream_id": avery.rappid + ":" + "x" * 65}],
        }
        for code, changes in cases.items():
            for change in changes:
                with self.assertRaises(Refusal, msg=change) as refused:
                    rapp1.frame_integrity(vectors._resigned(frame, avery, **change))
                self.assertEqual(refused.exception.code, code, change)

    def test_additive_schemas_compare_under_the_schema_bound(self) -> None:
        payload = {"blob": {str(i): {str(j): "" for j in range(10000)} for i in range(10)}}
        old = schemas.schema_of({"spec": "rapp/1", "kind": "memory.save", "payload": payload})
        new = schemas.schema_of({"spec": "rapp/1", "kind": "memory.save", "payload": {**payload, "extra": True}})
        self.assertGreater(len(rapp1.canonical(old, limit=schemas.SCHEMA_MAX_BYTES)), rapp1.MAX_JSON_BYTES)
        self.assertTrue(schemas.is_additive(new, old))

    def test_malformed_objects_are_refused_never_crash(self) -> None:
        anchor = json.loads(next(data for path, data in BUILT["hive"].items() if path.startswith("objects/") and json.loads(data).get("schema") == hive.ANCHOR))
        policy = next(value for value in (json.loads(data) for path, data in BUILT["hive"].items() if path.startswith("objects/")) if value.get("schema") == hive.POLICY and value["version"] == 1)
        lens = next(value for value in (json.loads(data) for path, data in BUILT["hive"].items() if path.startswith("objects/")) if value.get("schema") == lensmod.LENS and value["version"] == 3)
        checks = [
            (hive.check_anchor, {**anchor, "founders": [[1]]}, "REFUSE_SCHEMA"),
            (hive.check_anchor, {**anchor, "legacy": {**anchor["legacy"], "join": {"requests": [{}]}}}, "REFUSE_SCHEMA"),
            (hive.check_policy, {**policy, "deciders": [[]]}, "REFUSE_SCHEMA"),
            (hive.check_policy, {**policy, "deciders": [slug_of("avery-laptop")], "admit": {"quorum": 2, "attested": False}}, "REFUSE_SCHEMA"),
            (lensmod.check_view, {"schema": lensmod.VIEW, "id": "v", "version": 1, "fields": {"a": [["x"], "y"]}}, "REFUSE_LENS"),
            (lensmod.check_lens, {**lens, "predecessor": {**lens["predecessor"], "version": True}}, "REFUSE_LENS"),
        ]
        for check, value, code in checks:
            with self.assertRaises(Refusal) as refused:
                check(value)
            self.assertEqual(refused.exception.code, code, value)


if __name__ == "__main__":
    unittest.main()
