"""Blocking actual canonical RAPP/1 emission, signature, occurrence, and refusal tests."""

import copy
import os
import unittest
from unittest import mock

from support import fixture
from canonical_fixture import CanonicalRapp, public_test_key, sign_fixture
from common import REPO, Refusal, read_file, sha
from schema_source import GENERATED_UTC
from vectors import FIXTURES, check_exact, generate
from work_index import PinnedGeneration, build_generation, checkpoint_payload


class CanonicalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        checkout = os.environ.get("RAPP_WORK_INDEX_RAPP1_PATH")
        if not checkout:
            raise Refusal("canonical tests require explicit RAPP_WORK_INDEX_RAPP1_PATH; no skip/fallback")
        cls.checkout = checkout
        cls.core = CanonicalRapp(checkout)
        cls.inputs = fixture("inputs.json")
        cls.key, cls.spki, cls.signer = public_test_key(cls.core, "checkpoint", "index")

    def verify_zero(self, raw=None, **changes):
        return self.core.verify(
            read_file(FIXTURES / "checkpoint-0.frame.json") if raw is None else raw,
            **{"signer": self.signer, "spki": self.spki, "stream": self.signer, **changes},
        )

    def test_full_deterministic_emission_uses_canonical_checkout(self):
        before = self.core.frames_verified
        check_exact(generate(self.core))
        self.assertEqual(self.core.frames_verified - before, 9)

    def test_actual_signed_checkpoint_and_canonical_envelope(self):
        record, frame = self.core.verified_checkpoint(
            read_file(FIXTURES / "checkpoint-0.frame.json"),
            context=self.inputs["context"], spki=self.spki,
        )
        self.assertEqual(set(frame), self.core.r.FRAME_KEYS)
        self.assertEqual(len(frame), 11)
        self.assertIsNotNone(frame["sig"])
        pin = PinnedGeneration(fixture("generation-0.json"), record, self.inputs["context"])
        self.assertEqual(pin.binding, fixture("checkpoint-0.binding.json"))

    def test_real_signature_tampering_refuses(self):
        frame = fixture("checkpoint-0.frame.json")
        protected, _, signature = frame["sig"].split(".")
        signature = ("A" if signature[0] != "A" else "B") + signature[1:]
        frame["sig"] = protected + ".." + signature
        with self.assertRaises(Refusal):
            self.verify_zero(self.core.octets(frame))

    def test_unsigned_checkpoint_refuses(self):
        frame = fixture("checkpoint-0.frame.json")
        frame["sig"] = None
        with self.assertRaises(Refusal):
            self.verify_zero(self.core.octets(frame))

    def test_payload_and_hash_substitution_refuse(self):
        original = fixture("checkpoint-0.frame.json")
        for field in ("root", "manifest_sha256", "context_sha256", "source_vector_sha256"):
            frame = copy.deepcopy(original)
            frame["payload"][field] = "0" * 64
            with self.subTest(field=field), self.assertRaises(Refusal):
                self.verify_zero(self.core.octets(frame))
        frame = copy.deepcopy(original)
        frame["frame_hash"] = "0" * 64
        with self.assertRaises(Refusal):
            self.verify_zero(self.core.octets(frame))

    def test_wrong_spki_or_expected_signer_refuses(self):
        _, other_spki, other_signer = public_test_key(self.core, "other", "index")
        with self.assertRaises(Refusal):
            self.verify_zero(spki=other_spki)
        with self.assertRaises(Refusal):
            self.verify_zero(signer=other_signer)

    def test_noncanonical_bytes_and_cross_stream_replay_refuse(self):
        raw = read_file(FIXTURES / "checkpoint-0.frame.json")
        with self.assertRaises(Refusal):
            self.verify_zero(raw + b"\n")
        with self.assertRaises(Refusal):
            self.verify_zero(stream="unrelated-stream")

    def test_missing_chain_predecessor_refuses(self):
        with self.assertRaises(Refusal):
            self.verify_zero(read_file(FIXTURES / "checkpoint-1.frame.json"))
        first = self.verify_zero()
        second = self.verify_zero(read_file(FIXTURES / "checkpoint-1.frame.json"), head=first)
        self.assertEqual(second["seq"], 1)

    def test_real_fork_is_not_excused_by_valid_signature(self):
        record, _ = self.core.verified_checkpoint(
            read_file(FIXTURES / "checkpoint-0.frame.json"),
            context=self.inputs["context"], spki=self.spki,
        )
        pin = PinnedGeneration(fixture("generation-0.json"), record, self.inputs["context"])
        records = copy.deepcopy(self.inputs["records"])
        records[0]["key"] = "fork"
        manifest, _, _ = build_generation(records, 0, self.inputs["context"], self.inputs["sources"])
        frame = sign_fixture(self.core, self.core.r.build_frame(
            "memory.save", self.signer, 0, GENERATED_UTC, checkpoint_payload(manifest), None,
        ), self.key, self.signer)
        verified, _ = self.core.verified_checkpoint(
            self.core.octets(frame), context=self.inputs["context"], spki=self.spki,
        )
        with self.assertRaisesRegex(Refusal, "fork"):
            PinnedGeneration(manifest, verified, self.inputs["context"], pin)

    def test_actual_rotation_requires_new_external_context(self):
        verified, previous = self.core.verified_checkpoint(
            read_file(FIXTURES / "checkpoint-0.frame.json"),
            context=self.inputs["context"], spki=self.spki,
        )
        pin = PinnedGeneration(fixture("generation-0.json"), verified, self.inputs["context"])
        key, spki, signer = public_test_key(self.core, "rotated", "index")
        context = {
            **self.inputs["context"], "signer": signer, "spki_sha256": sha(spki),
            "key_epoch": 2, "registry_epoch": 2,
            "registry_root": sha(b"PUBLIC SYNTHETIC externally authenticated rotation"),
        }
        manifest, _, _ = build_generation(self.inputs["records"], 1, context, self.inputs["sources"])
        frame = sign_fixture(self.core, self.core.r.build_frame(
            "memory.save", context["stream"], 1, GENERATED_UTC,
            checkpoint_payload(manifest), previous["payload_hash"],
        ), key, signer)
        record, _ = self.core.verified_checkpoint(
            self.core.octets(frame), context=context, spki=spki, head=previous,
        )
        successor = PinnedGeneration(manifest, record, context, pin)
        self.assertNotEqual(successor.fingerprint, pin.fingerprint)
        with self.assertRaises(Refusal):
            successor.require_current(pin.frontier)
        with self.assertRaises(Refusal):
            PinnedGeneration(manifest, record, self.inputs["context"], pin)

    def test_particle_reuse_does_not_collapse_signed_occurrences(self):
        source = self.inputs["sources"][0]
        _, spki, signer = public_test_key(self.core, "source-00", "cedar")
        first = self.core.verify(
            read_file(FIXTURES / "source-00.frame.json"),
            signer=signer, spki=spki, stream=source["stream"],
        )
        second = self.core.verify(
            read_file(FIXTURES / "source-06.frame.json"),
            signer=signer, spki=spki, stream=source["stream"], head=first,
        )
        self.assertEqual(first["payload_hash"], second["payload_hash"])
        self.assertNotEqual(first["frame_hash"], second["frame_hash"])

    def test_wrong_checkout_and_missing_checkout_refuse(self):
        with self.assertRaises(Refusal):
            CanonicalRapp(None)
        with self.assertRaises(Refusal):
            CanonicalRapp(REPO)

    def test_canonical_source_tampering_refuses_before_execution(self):
        original_read = read_file
        def substituted(path, *args, **kwargs):
            raw = original_read(path, *args, **kwargs)
            return raw + b"\n" if path.name == "rapp.py" else raw
        with mock.patch("canonical_fixture.read_file", side_effect=substituted), self.assertRaises(Refusal):
            CanonicalRapp(self.checkout)


if __name__ == "__main__":
    unittest.main()
