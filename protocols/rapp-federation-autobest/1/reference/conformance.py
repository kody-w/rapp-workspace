"""Conformance suite for the optional RAPP Federation AutoBest profile."""

from __future__ import annotations

import argparse
import base64
import copy
import hashlib
import json
import os
import subprocess
import sys
import unittest
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

from compatibility import (
    H,
    PROFILE,
    Refusal,
    canonical,
    digest,
    generate_static_agent,
    loads,
    require,
    require_ceo_for_mutation,
    run_agent,
    validate,
    validate_artifact_bundle,
    validate_compatibility_record,
    validate_learning_trace,
    verify_frame,
)
from schema_source import schema_bytes
from manifest_source import manifest_bytes
from vectors import (
    BINDINGS_PATH,
    COMPATIBILITY_PATH,
    DOCUMENT_PATH,
    EXHAUST_PATH,
    FIXTURE,
    GENERATION_PATH,
    HANDSHAKE_PATH,
    MUTATIONS_PATH,
    OFFER_PATH,
    PACKAGE_PATH,
    SCHEMA_COPY_PATH,
    SEARCH_PATH,
    SOURCE_AGENT_PATH,
    STATIC_PATH,
    TARGET_AGENT_PATH,
    TRACE_PATH,
    check as check_vectors,
)


ROOT = Path(__file__).resolve().parents[1]
REPOSITORY = ROOT.parents[2]
NEGATIVE_RESULTS: list[dict[str, str]] = []
VERIFIED_FIXTURE_FRAMES = 0


def object_file(path: Path):
    return loads(path.read_bytes())


def public_key(encoded: str) -> Ed25519PublicKey:
    value = serialization.load_der_public_key(base64.b64decode(encoded))
    if not isinstance(value, Ed25519PublicKey):
        raise AssertionError("fixture key is not Ed25519")
    return value


def source_tree():
    paths = [
        ROOT / "SPEC.md",
        ROOT / "schema.json",
        ROOT / "bindings.json",
        ROOT / "safety-matrix.json",
        ROOT / "provenance.json",
        ROOT / "manifest.json",
        ROOT / "parent-wire-results.json",
        ROOT / "reference" / "schema_source.py",
        ROOT / "reference" / "manifest_source.py",
        ROOT / "reference" / "compatibility.py",
        ROOT / "reference" / "vectors.py",
        ROOT / "reference" / "conformance.py",
        ROOT / "reference" / "README.md",
        HANDSHAKE_PATH,
        SOURCE_AGENT_PATH,
        TARGET_AGENT_PATH,
        DOCUMENT_PATH,
        EXHAUST_PATH,
        COMPATIBILITY_PATH,
        SCHEMA_COPY_PATH,
        FIXTURE / "qualification.json",
        STATIC_PATH,
        GENERATION_PATH,
        TRACE_PATH,
        SEARCH_PATH,
        MUTATIONS_PATH,
        PACKAGE_PATH,
        OFFER_PATH,
    ]
    return {
        str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in paths
        if path.is_file()
    }


class ProfileCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bindings = object_file(BINDINGS_PATH)
        cls.handshake = object_file(HANDSHAKE_PATH)
        cls.fixture = object_file(DOCUMENT_PATH)
        cls.frame = cls.fixture["compatibility"]["frame"]
        cls.exhaust = cls.fixture["exhaust"]["frame"]
        cls.record = cls.frame["payload"]["record"]
        cls.package = object_file(PACKAGE_PATH)
        cls.trace = object_file(TRACE_PATH)
        cls.search = object_file(SEARCH_PATH)
        cls.offer = object_file(OFFER_PATH)
        cls.generation = object_file(GENERATION_PATH)

    def reject(self, code, function, *args, **kwargs):
        with self.assertRaises(Refusal) as caught:
            function(*args, **kwargs)
        self.assertEqual(caught.exception.code, code)
        NEGATIVE_RESULTS.append({"test": self._testMethodName, "refusal": code})

    def test_schema_is_closed_and_generated_exactly(self):
        self.assertEqual((ROOT / "schema.json").read_bytes(), schema_bytes())
        changed = copy.deepcopy(self.frame)
        changed["payload"]["record"]["unknown"] = True
        self.reject("schema", validate, changed)

    def test_manifest_is_exact_and_excludes_generated_report_cycle(self):
        self.assertEqual((ROOT / "manifest.json").read_bytes(), manifest_bytes())
        manifest = object_file(ROOT / "manifest.json")
        paths = {item["path"] for item in manifest["files"]}
        self.assertNotIn("manifest.json", paths)
        self.assertNotIn("conformance-results.json", paths)

    def test_checked_in_fixture_is_reproducible(self):
        check_vectors()

    def test_supplied_handshake_and_agents_match_exact_pins(self):
        self.assertEqual(digest(HANDSHAKE_PATH.read_bytes()), self.bindings["wild_handshake"]["profile_sha256"])
        self.assertEqual(digest(SOURCE_AGENT_PATH.read_bytes()), self.bindings["wild_handshake"]["source_agent_sha256"])
        self.assertEqual(digest(TARGET_AGENT_PATH.read_bytes()), self.bindings["wild_handshake"]["target_finalizer_sha256"])
        self.assertEqual(self.bindings["wild_handshake"]["verified_frames"], 2)
        self.assertEqual(self.bindings["wild_handshake"]["verified_artifacts"], 9)

    def test_source_and_compatibility_frames_are_real_signed_rapp1_frames(self):
        global VERIFIED_FIXTURE_FRAMES
        source = self.fixture["source"]
        key = public_key(source["public_spki_der_b64"])
        previous = None
        for frame in source["frames"]:
            verify_frame(
                frame,
                public_key=key,
                identity=source["identity"],
                previous=previous,
                profile=False,
            )
            previous = frame
            VERIFIED_FIXTURE_FRAMES += 1
        compatibility = self.fixture["compatibility"]
        verify_frame(
            compatibility["frame"],
            public_key=public_key(compatibility["public_spki_der_b64"]),
            identity=compatibility["identity"],
        )
        VERIFIED_FIXTURE_FRAMES += 1
        verify_frame(
            self.exhaust,
            public_key=public_key(compatibility["public_spki_der_b64"]),
            identity=compatibility["identity"],
            previous=compatibility["frame"],
        )
        VERIFIED_FIXTURE_FRAMES += 1

    def test_double_hotload_reproduces_exact_candidate_chain(self):
        outputs = []
        receipts = []
        for source_frame in self.fixture["source"]["frames"]:
            source_request = {"direction": "source-to-target", "value": source_frame}
            source_response = run_agent(SOURCE_AGENT_PATH, source_request)
            context = {
                "compatibility_intent_hash": self.fixture["double_hotload"]["intent_hash"],
                "handshake_id": self.handshake["id"],
                "handshake_sha256": self.bindings["wild_handshake"]["profile_sha256"],
                "source_agent_sha256": self.bindings["wild_handshake"]["source_agent_sha256"],
                "target_profile": self.handshake["target"]["profile"],
            }
            target_request = {"candidate": source_response["result"], "context": context}
            target_response = run_agent(TARGET_AGENT_PATH, target_request)
            outputs.append({"source": source_response["result"], "target": target_response["result"]})
            receipts.extend(
                [
                    (digest(canonical(source_request)), digest(canonical(source_response))),
                    (digest(canonical(target_request)), digest(canonical(target_response))),
                ]
            )
        self.assertEqual(outputs, self.fixture["double_hotload"]["outputs"])
        expected = [
            (item["request_sha256"], item["result_sha256"])
            for item in self.fixture["double_hotload"]["receipts"]
        ]
        self.assertEqual(receipts, expected)

    def test_compatibility_record_is_partial_non_authorizing_and_ceo_pending(self):
        validate_compatibility_record(self.record, self.bindings, self.handshake)
        self.assertFalse(self.record["grants_authority"])
        self.assertFalse(self.record["coverage"]["complete_for_membership"])
        self.assertGreater(len(self.record["gaps"]), 0)
        self.reject("ceo-agent-pending", require_ceo_for_mutation, self.bindings)

    def test_static_agent_reproduces_exactly_from_frame_and_compiler(self):
        generated = generate_static_agent(self.frame, self.handshake)
        self.assertEqual(generated, STATIC_PATH.read_bytes())
        self.assertEqual(digest(generated), self.generation["agent_sha256"])
        validate(self.generation, "generationReceipt")
        self.assertEqual(self.generation["compiler_sha256"], self.record["static_output_contract"]["compiler_sha256"])
        self.assertFalse(self.generation["candidate_tests_are_independent_proof"])

    def test_static_agent_maps_both_directions_without_model_calls(self):
        for frame, expected in zip(
            self.fixture["source"]["frames"],
            self.fixture["double_hotload"]["outputs"],
            strict=True,
        ):
            response = run_agent(STATIC_PATH, {"direction": "source-to-target", "value": frame})
            self.assertEqual(response["model_calls"], 0)
            self.assertEqual(response["result"]["schema"], "microsol-hive-observation/1")
            self.assertEqual(
                response["result"]["source"]["head"],
                expected["target"]["source"]["head"],
            )
        reverse = run_agent(
            STATIC_PATH,
            {
                "direction": "target-to-source",
                "value": {
                    "peer": {"id": "peer-a"},
                    "compatibility": {"frame": self.frame["frame_hash"]},
                    "subscription": {"mode": "partial-read-only"},
                },
            },
        )
        self.assertEqual(reverse["result"]["operation"], "peer-offer")
        self.assertFalse(reverse["result"]["authority"])

    def test_unknown_operation_refuses_without_jit_improvisation(self):
        changed = copy.deepcopy(self.fixture["source"]["frames"][-1])
        changed["payload"]["operation"] = "unknown-operation"
        process = subprocess.run(
            [sys.executable, "-B", str(STATIC_PATH)],
            input=canonical({"direction": "source-to-target", "value": changed}),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env={"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "PYTHONDONTWRITEBYTECODE": "1"},
            check=False,
            timeout=10,
        )
        self.assertEqual(process.returncode, 2)
        response = loads(process.stdout)
        self.assertFalse(response["ok"])
        self.assertEqual(response["model_calls"], 0)

    def test_typed_exhaust_is_signed_privacy_safe_and_non_authorizing(self):
        validate(self.exhaust["payload"]["record"], "exhaustRecord")
        record = self.exhaust["payload"]["record"]
        self.assertEqual(record["active_compatibility"], {
            key: self.frame[key]
            for key in ("stream_id", "seq", "payload_hash", "frame_hash")
        })
        self.assertTrue(record["privacy_safe"])
        self.assertFalse(record["inferred_patch"])
        self.assertFalse(record["grants_authority"])
        self.assertIsNone(record["output_particle"])

    def test_artifact_bundle_binds_every_byte_and_complete_lineage(self):
        files = {}
        for entry in self.package["entries"]:
            path = FIXTURE / entry["path"]
            self.assertTrue(path.is_file(), entry["path"])
            files[entry["path"]] = path.read_bytes()
        validate_artifact_bundle(self.package, files)
        self.assertEqual(self.package["entrypoint"], "static/agent.py")
        self.assertFalse(self.package["candidate_tests_are_independent_proof"])
        self.assertFalse(self.package["lineage"]["roundtrip_claim"])

    def test_learning_trace_preserves_corrections_without_raw_history(self):
        validate_learning_trace(self.trace)
        self.assertFalse(self.trace["raw_transcript_persisted"])
        self.assertFalse(self.trace["hidden_reasoning_persisted"])
        changed = copy.deepcopy(self.trace)
        changed["events"][-1]["references"] = []
        body = {
            key: value
            for key, value in changed["events"][-1].items()
            if key != "event_hash"
        }
        changed["events"][-1]["event_hash"] = H(PROFILE + ":trace-event", body)
        self.reject("trace-correction-missing", validate_learning_trace, changed)

    def test_forged_user_authority_is_refused(self):
        changed = copy.deepcopy(self.trace)
        correction = next(item for item in changed["events"] if item["type"] == "user-correction")
        correction["authority_class"] = "assistant-proposal"
        body = {key: value for key, value in correction.items() if key != "event_hash"}
        correction["event_hash"] = H(PROFILE + ":trace-event", body)
        self.reject("trace-authority", validate_learning_trace, changed)

    def test_lens_search_is_explicitly_bounded_and_not_universal_truth(self):
        validate(self.search, "lensSearch")
        self.assertLessEqual(self.search["max_lenses"], 32)
        self.assertLessEqual(self.search["max_candidates"], 256)
        self.assertFalse(self.search["fitness_is_universal_truth"])
        changed = copy.deepcopy(self.search)
        changed["max_lenses"] = 33
        self.reject("schema", validate, changed, "lensSearch")

    def test_mutation_offer_is_transport_only(self):
        validate(self.offer, "mutationOffer")
        self.assertFalse(self.offer["grants_authority"])
        self.assertFalse(self.offer["rewrites_ancestor"])
        self.assertFalse(self.offer["activates_successor"])
        changed = copy.deepcopy(self.offer)
        changed["grants_authority"] = True
        self.reject("schema", validate, changed, "mutationOffer")

    def test_live_bill_binding_is_external_evidence_not_local_reverification(self):
        qualification = object_file(FIXTURE / "qualification.json")
        self.assertEqual(qualification["assurance"], "parent-supplied-live-qualification")
        self.assertEqual(qualification["signed_frames_verified"], 2)
        self.assertEqual(qualification["artifacts_verified"], 9)
        self.assertFalse(qualification["authority"])
        self.assertFalse(qualification["raw_private_repository_content_included"])

    def test_prior_art_is_provenance_only(self):
        provenance = object_file(ROOT / "provenance.json")
        prior = provenance["conceptual_prior_art"]
        self.assertEqual(prior["commit"], "f2a978b9f85b65b9815b69d99c67e51c56732251")
        self.assertFalse(prior["code_imported"])
        self.assertFalse(prior["runtime_dependency"])
        self.assertFalse(prior["rapp1_conformance_claim"])
        trusted = "\n".join(
            (ROOT / "reference" / name).read_text(encoding="utf-8")
            for name in ("compatibility.py", "schema_source.py", "vectors.py")
        )
        self.assertNotIn("AzureFileStorage", trusted)
        self.assertNotIn("hashlib.md5", trusted)

    def test_fixture_contains_no_local_paths_tokens_or_native_sessions(self):
        for path in FIXTURE.rglob("*"):
            if not path.is_file() or path.suffix not in {".json", ".py"}:
                continue
            text = path.read_text(encoding="utf-8")
            self.assertNotIn("/Users/", text)
            self.assertNotIn("ghp_", text)
            self.assertNotIn("sk-", text)
            self.assertNotIn("BEGIN PRIVATE KEY", text)
            self.assertNotIn("native_session_id", text)

    def test_duplicate_json_keys_and_floats_refuse(self):
        self.reject("duplicate-json-key", loads, b'{"a":1,"a":2}')
        self.reject("number", loads, b'{"a":1.5}')

    def test_signature_tamper_rollback_and_same_sequence_fork_refuse(self):
        source = self.fixture["source"]
        key = public_key(source["public_spki_der_b64"])
        tampered = copy.deepcopy(source["frames"][0])
        tampered["sig"] = tampered["sig"][:-1] + ("A" if tampered["sig"][-1] != "A" else "B")
        self.reject(
            "signature",
            verify_frame,
            tampered,
            public_key=key,
            identity=source["identity"],
            profile=False,
        )
        self.reject(
            "chain",
            verify_frame,
            source["frames"][0],
            public_key=key,
            identity=source["identity"],
            previous=source["frames"][1],
            profile=False,
        )
        rival = copy.deepcopy(source["frames"][1])
        rival["frame_hash"] = "0" * 64
        self.reject(
            "stream-fork",
            require,
            not (
                rival["stream_id"] == source["frames"][1]["stream_id"]
                and rival["seq"] == source["frames"][1]["seq"]
                and rival["frame_hash"] != source["frames"][1]["frame_hash"]
            ),
            "stream-fork",
        )

    def test_revoked_handshake_and_changed_mapping_refuse(self):
        revoked = copy.deepcopy(self.record)
        revoked["handshake"]["status"] = "revoked"
        self.reject("handshake-revoked", validate_compatibility_record, revoked, self.bindings, self.handshake)
        changed = copy.deepcopy(self.record)
        changed["mapping_sha256"] = "0" * 64
        self.reject("mapping-pin", validate_compatibility_record, changed, self.bindings, self.handshake)

    def test_successor_requires_previous_and_exhaust_together(self):
        changed = copy.deepcopy(self.record)
        changed["previous_compatibility"] = {
            "stream_id": self.frame["stream_id"],
            "seq": 0,
            "payload_hash": self.frame["payload_hash"],
            "frame_hash": self.frame["frame_hash"],
        }
        self.reject("successor-causality", validate_compatibility_record, changed, self.bindings, self.handshake)

    def test_path_escape_and_lineage_gap_refuse(self):
        files = {entry["path"]: (FIXTURE / entry["path"]).read_bytes() for entry in self.package["entries"]}
        escaped = copy.deepcopy(self.package)
        escaped["entries"][0]["path"] = "../escape"
        self.reject("schema", validate_artifact_bundle, escaped, files)
        gap = copy.deepcopy(self.package)
        gap["lineage"]["reverse"].pop()
        self.reject("lineage-successor-coverage", validate_artifact_bundle, gap, files)

    def test_candidate_tests_cannot_self_certify(self):
        changed = copy.deepcopy(self.package)
        changed["candidate_tests_are_independent_proof"] = True
        self.reject("schema", validate, changed, "artifactBundle")
        mutations = object_file(MUTATIONS_PATH)
        self.assertFalse(mutations["candidate_tests_are_independent_proof"])
        self.assertGreater(len(mutations["host_tests"]), 0)
        self.assertGreater(len(mutations["controlled_mutants"]), 0)

    def test_existing_closed_profiles_remain_byte_identical(self):
        federation_spec = REPOSITORY / "protocols" / "rapp-federation" / "1" / "SPEC.md"
        federation_schema = REPOSITORY / "protocols" / "rapp-federation" / "1" / "schema.json"
        hive_spec = REPOSITORY / "protocols" / "rapp-hive" / "1" / "SPEC.md"
        workspace_spec = REPOSITORY / "protocols" / "rapp-workspace" / "1" / "SPEC.md"
        self.assertEqual(digest(federation_spec.read_bytes()), self.bindings["federation"]["spec_sha256"])
        self.assertEqual(digest(federation_schema.read_bytes()), self.bindings["federation"]["schema_sha256"])
        self.assertEqual(digest(hive_spec.read_bytes()), self.bindings["hive"]["spec_sha256"])
        self.assertEqual(digest(workspace_spec.read_bytes()), self.bindings["workspace"]["spec_sha256"])


def run():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report")
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("tests", nargs="*")
    arguments = parser.parse_args()
    before = source_tree()
    suite = (
        unittest.defaultTestLoader.loadTestsFromNames(arguments.tests)
        if arguments.tests
        else unittest.defaultTestLoader.loadTestsFromTestCase(ProfileCase)
    )
    result = unittest.TextTestRunner(verbosity=2 if arguments.verbose else 1).run(suite)
    after = source_tree()
    report = {
        "profile": PROFILE,
        "activation": "candidate-not-activated-ceo-agent-pending",
        "tests_run": result.testsRun,
        "failures": len(result.failures),
        "errors": len(result.errors),
        "skipped": len(result.skipped),
        "verified_fixture_frames": VERIFIED_FIXTURE_FRAMES,
        "negative_checks": len(NEGATIVE_RESULTS),
        "negative_vectors": NEGATIVE_RESULTS,
        "input_tree_stable": before == after,
        "changed_inputs": sorted(key for key in set(before) | set(after) if before.get(key) != after.get(key)),
        "source_sha256": after,
    }
    if arguments.report:
        path = Path(arguments.report)
        raw = json.dumps(report, indent=2, sort_keys=True).encode("utf-8") + b"\n"
        if not path.is_file() or path.read_bytes() != raw:
            path.write_bytes(raw)
    if not result.wasSuccessful() or before != after:
        raise SystemExit(1)


if __name__ == "__main__":
    run()
