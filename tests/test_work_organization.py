"""Profile-independent positive and refusal vectors for Work Organization/1."""

from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest


REPO = Path(__file__).resolve().parents[1]
REFERENCE = REPO / "protocols/rapp-work-organization/1/reference"
sys.path.insert(0, str(REFERENCE))

from atomic_agent import place_bundle, verify_bundle  # noqa: E402
from workorg_common import Refusal, canonical_bytes, particle, read_json, sha256  # noqa: E402
from compiler import compile_static_bundle, compiler_pin  # noqa: E402
from protocol import (  # noqa: E402
    validate_activation_document,
    validate_bill_binding,
    validate_evolution,
    validate_learning_trace,
    validate_mutation_lineage,
    validate_search,
)
from workorg_schema_source import documents  # noqa: E402
from workorg_artifact import (  # noqa: E402
    ARTIFACT_RELATIVE,
    GENERIC_CEO_BYTES,
    GENERIC_CEO_PROFILE_SHA256,
    GENERIC_CEO_SHA256,
    GENERIC_CEO_SKILL_BYTES,
    GENERIC_CEO_SKILL_SHA256,
    validate_generic_ceo_artifact,
)


HASH0 = "0" * 64
HASH1 = "1" * 64
HASH2 = "2" * 64
HASH3 = "3" * 64
HASH4 = "4" * 64
RAPPID = "rappid:@test/work-org:" + HASH0


def wave(value: str) -> dict[str, str]:
    return {"space": "rapp/1:wave", "hash": value}


def particle_ref(value: str) -> dict[str, str]:
    return {"space": "rapp/1:particle", "hash": value}


def egg(value: str) -> dict[str, str]:
    return {"space": "rapp/1:egg-manifest", "hash": value}


def head(entry_id: str, path: str, digest: str) -> dict[str, object]:
    return {
        "entry_id": entry_id,
        "path": path,
        "mode": "100644",
        "sha256": digest,
        "bytes": 3,
        "content": particle_ref(digest),
    }


def loss(name: str = "lossless") -> dict[str, object]:
    return {
        "class": name,
        "source_refs_preserved": True,
        "round_trip_claimed": name == "lossless",
    }


def lineage() -> dict[str, object]:
    source = head("source-a", "old/a.py", HASH1)
    target = head("target-a", "src/a.py", HASH2)
    return {
        "schema": "rapp-work-organization/1/mutation-lineage",
        "output_shape": "full-successor",
        "source_parents": [
            {
                "frame": wave(HASH1),
                "inventory": particle_ref(HASH1),
                "repository_commit": "a" * 40,
                "repository_tree": "b" * 40,
            }
        ],
        "source_inventory": particle_ref(HASH1),
        "successor_inventory": particle_ref(HASH2),
        "successor_root": egg(HASH2),
        "forward": [
            {
                "source": source,
                "disposition": "replaced",
                "relation": "rewrite",
                "targets": [target],
                "mutation_receipts": [wave(HASH3)],
                "inverse_material": [egg(HASH3)],
                "loss": loss(),
            }
        ],
        "reverse": [
            {
                "successor": target,
                "ancestry": "derived",
                "sources": [source],
                "derivation_receipts": [wave(HASH4)],
                "inverse_material": [egg(HASH3)],
                "loss": loss(),
            }
        ],
        "traits": [],
        "directionality": "bidirectional-lossless",
        "reconstruction": {
            "status": "verified-contained",
            "inverse_material": [egg(HASH3)],
            "reconstructor_sha256": HASH3,
            "runtime_manifest_sha256": HASH4,
        },
        "grants_authority": False,
    }


def trace() -> dict[str, object]:
    correction = HASH2
    events = [
        {
            "event_id": HASH1,
            "trace_seq": 0,
            "previous_event": None,
            "event_type": "proposal",
            "actor_role": "assistant",
            "authority": "proposal-only",
            "supersedes": [],
            "source_receipts": [],
            "structured_content": {"proposal_code": "sidecar-only"},
            "raw_content_persisted": False,
            "hidden_reasoning_present": False,
        },
        {
            "event_id": correction,
            "trace_seq": 1,
            "previous_event": wave(HASH1),
            "event_type": "user-correction",
            "actor_role": "user",
            "authority": "host-attested-user-authority",
            "supersedes": [HASH1],
            "source_receipts": [],
            "structured_content": {"correction_code": "full-successor-allowed"},
            "raw_content_persisted": False,
            "hidden_reasoning_present": False,
        },
        {
            "event_id": HASH3,
            "trace_seq": 2,
            "previous_event": wave(HASH2),
            "event_type": "successor-invariant",
            "actor_role": "host",
            "authority": "derived-from-authoritative-correction",
            "supersedes": [],
            "source_receipts": [],
            "structured_content": {
                "invariant_id": "ancestor-immutable-successor-mutable",
                "correction_event": correction,
                "predicate": "complete-causal-accounting",
            },
            "raw_content_persisted": False,
            "hidden_reasoning_present": False,
        },
    ]
    return {
        "schema": "rapp-work-organization/1/learning-trace",
        "trace_id": HASH4,
        "sanitizer_sha256": HASH3,
        "reducer_sha256": HASH4,
        "events": events,
        "ordered_event_hashes": [HASH1, HASH2, HASH3],
        "active_successor_invariants": [HASH3],
        "unresolved_corrections": [],
        "correction_fixture_set": particle_ref(HASH4),
        "grants_authority": False,
    }


class WorkOrganizationTests(unittest.TestCase):
    def test_checked_in_schemas_match_source(self) -> None:
        for name, value in documents().items():
            actual = read_json(REPO / "protocols/rapp-work-organization/1/schemas" / name)
            self.assertEqual(actual, value)

    def test_bill_binding_exact_and_private_safe(self) -> None:
        binding = read_json(
            REPO
            / "protocols/rapp-work-organization/1/fixtures/softwarecoellc-vteam-hive-1.json"
        )
        validate_bill_binding(binding)
        self.assertFalse(binding["embedded_private_content"])
        self.assertEqual(binding["generic_ceo_agent"]["status"], "verified")
        self.assertEqual(binding["generic_ceo_agent"]["sha256"], GENERIC_CEO_SHA256)

    def test_generic_ceo_artifact_exact_bytes_and_binding_api(self) -> None:
        root = REPO / "protocols/rapp-work-organization/1" / ARTIFACT_RELATIVE
        agent = (root / "agent.py").read_bytes()
        skill = (root / "SKILL.md").read_bytes()
        profile = json.loads((root / "profile.json").read_text())
        validate_generic_ceo_artifact(profile, agent, skill)
        self.assertEqual((sha256(agent), len(agent)), (GENERIC_CEO_SHA256, GENERIC_CEO_BYTES))
        self.assertEqual(
            (sha256(skill), len(skill)),
            (GENERIC_CEO_SKILL_SHA256, GENERIC_CEO_SKILL_BYTES),
        )
        self.assertEqual(sha256((root / "profile.json").read_bytes()), GENERIC_CEO_PROFILE_SHA256)
        spec = importlib.util.spec_from_file_location("workorg_generic_ceo_fixture", root / "agent.py")
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        binding = module.bind_implementation_sha256(GENERIC_CEO_SHA256)
        self.assertEqual(binding["implementation_sha256"], GENERIC_CEO_SHA256)
        self.assertFalse(binding["authority_from_presence"])
        self.assertEqual(module.__manifest__["capability_id"], "autobest:generic")
        self.assertFalse(module.__manifest__["authority"])

    def test_activation_document_binds_exact_generic_ceo(self) -> None:
        document = {
            "schema": "rapp-work-organization/1/activation-document",
            "spec_sha256": HASH1,
            "manifest_sha256": HASH2,
            "brainstem_runtime_sha256": HASH3,
            "organization_rappid": RAPPID,
            "world_id": "test-world",
            "policy": particle_ref(HASH4),
            "not_before_utc": "2030-01-01T00:00:00.000Z",
            "expires_utc": "2030-01-01T01:00:00.000Z",
            "signer_key_id": "test-signer",
            "revocation_status": "active",
            "generic_ceo_agent_sha256": GENERIC_CEO_SHA256,
            "generic_ceo_skill_sha256": GENERIC_CEO_SKILL_SHA256,
            "generic_ceo_artifact_profile_sha256": GENERIC_CEO_PROFILE_SHA256,
        }
        validate_activation_document(document)

    def test_complete_bidirectional_lineage(self) -> None:
        self.assertEqual(
            validate_mutation_lineage(lineage())["directionality"],
            "bidirectional-lossless",
        )

    def test_orphan_successor_refuses(self) -> None:
        value = lineage()
        value["reverse"][0]["successor"] = dict(value["reverse"][0]["successor"])
        value["reverse"][0]["successor"]["entry_id"] = "orphan"
        with self.assertRaisesRegex(Refusal, "Forward targets"):
            validate_mutation_lineage(value)

    def test_lossless_claim_requires_exact_reconstruction(self) -> None:
        value = lineage()
        value["reconstruction"]["status"] = "unproven"
        with self.assertRaisesRegex(Refusal, "Lossless lineage"):
            validate_mutation_lineage(value)

    def test_lossy_relation_cannot_claim_round_trip(self) -> None:
        value = lineage()
        value["directionality"] = "forward-only-lossy"
        value["reconstruction"] = {
            "status": "unproven",
            "inverse_material": [],
            "reconstructor_sha256": None,
            "runtime_manifest_sha256": None,
        }
        for entry in value["forward"] + value["reverse"]:
            entry["loss"] = {
                "class": "privacy-withheld",
                "source_refs_preserved": True,
                "round_trip_claimed": True,
            }
        with self.assertRaisesRegex(Refusal, "cannot claim round trip"):
            validate_mutation_lineage(value)

    def test_learning_trace_binds_correction_and_invariant(self) -> None:
        self.assertEqual(len(validate_learning_trace(trace())["events"]), 3)

    def test_trace_summary_drift_refuses(self) -> None:
        value = trace()
        value["ordered_event_hashes"] = [HASH1, HASH3]
        with self.assertRaisesRegex(Refusal, "summary drift"):
            validate_learning_trace(value)

    def test_static_bundle_is_deterministic_and_frame_bound(self) -> None:
        program = b"VALUE = 7\n\ndef perform(value):\n    return VALUE + value\n"
        arguments = {
            "compatibility_frame": wave(HASH1),
            "compatibility_frame_octets_sha256": HASH2,
            "locked_profile": {
                "coverage": {"forward_bp": 10000, "reverse_bp": 10000},
                "gaps": [],
                "restrictions": {"model_calls": 0},
            },
            "program_source": program,
            "extra_files": {"schemas/input.json": b"{}"},
            "bundle_rappid": RAPPID,
            "runtime_manifest_sha256": HASH3,
            "source_mutation_manifest": particle_ref(HASH4),
            "compiler_sha256": compiler_pin(),
        }
        first = compile_static_bundle(**arguments)
        second = compile_static_bundle(**arguments)
        self.assertEqual(first["files"], second["files"])
        self.assertEqual(first["manifest"], second["manifest"])
        changed = dict(arguments)
        changed["compatibility_frame"] = wave(HASH2)
        third = compile_static_bundle(**changed)
        self.assertNotEqual(
            first["generation_receipt"]["output_agent_sha256"],
            third["generation_receipt"]["output_agent_sha256"],
        )
        compile(first["files"]["agent.py"], "<generated-agent>", "exec")

    def test_atomic_bundle_placement_and_replay(self) -> None:
        bundle = compile_static_bundle(
            compatibility_frame=wave(HASH1),
            compatibility_frame_octets_sha256=HASH2,
            locked_profile={"coverage": {}, "gaps": [], "restrictions": {}},
            program_source=b"VALUE = 1\n",
            extra_files={},
            bundle_rappid=RAPPID,
            runtime_manifest_sha256=HASH3,
            source_mutation_manifest=particle_ref(HASH4),
            compiler_sha256=compiler_pin(),
        )
        with tempfile.TemporaryDirectory() as directory:
            first = place_bundle(Path(directory), bundle["manifest"], bundle["files"])
            second = place_bundle(Path(directory), bundle["manifest"], bundle["files"])
            self.assertFalse(first["replayed"])
            self.assertTrue(second["replayed"])

    def test_search_bounds_and_selection(self) -> None:
        value = {
            "schema": "rapp-work-organization/1/search",
            "ancestor_frames": [wave(HASH1)],
            "ancestor_inventory": particle_ref(HASH1),
            "declared_use_case": "connector-rewrite",
            "scenario_corpus": particle_ref(HASH2),
            "holdout_commitment": particle_ref(HASH3),
            "bounds": {
                "max_lenses": 2,
                "max_candidates": 2,
                "max_cross_parents": 2,
                "max_cross_traits": 4,
                "max_depth": 2,
                "max_rounds": 2,
                "max_work_units": 100,
                "max_artifact_bytes": 1024,
            },
            "lens_dimensions": [RAPPID],
            "candidates": [
                {
                    "candidate_id": HASH2,
                    "dimension": RAPPID,
                    "kind": "complete-successor",
                    "artifact": egg(HASH2),
                    "parents": [wave(HASH1)],
                    "traits": [],
                    "status": "selected",
                }
            ],
            "pareto_frontier": [HASH2],
            "selected": HASH2,
            "stop_reason": None,
            "grants_authority": False,
        }
        validate_search(value)
        value["lens_dimensions"] = [RAPPID, RAPPID, RAPPID]
        with self.assertRaisesRegex(Refusal, "bounds"):
            validate_search(value)

    def test_evolution_cannot_self_promote(self) -> None:
        value = {
            "schema": "rapp-work-organization/1/evolution",
            "level": "handshake",
            "parents": [wave(HASH1)],
            "candidate": egg(HASH2),
            "scenario_corpus": particle_ref(HASH1),
            "hidden_holdout": particle_ref(HASH2),
            "controlled_mutants": particle_ref(HASH3),
            "canonical_evaluation": wave(HASH3),
            "canary": wave(HASH4),
            "promotion": None,
            "adoption": None,
            "rollback_target": wave(HASH1),
            "automatic_promotion": False,
            "generated_tests_self_certify": False,
            "grants_authority": False,
        }
        validate_evolution(value)
        value["automatic_promotion"] = True
        with self.assertRaisesRegex(Refusal, "self-promote"):
            validate_evolution(value)


if __name__ == "__main__":
    unittest.main()
