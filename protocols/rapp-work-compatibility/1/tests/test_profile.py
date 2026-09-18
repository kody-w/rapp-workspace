from __future__ import annotations

import json
import os
import subprocess
import sys
import unittest
from copy import deepcopy
from pathlib import Path

REFERENCE = Path(__file__).resolve().parents[1] / "reference"
if str(REFERENCE) not in sys.path:
    sys.path.insert(0, str(REFERENCE))

from common import PROFILE, ROOT, Parent, Refusal, SchemaSet, read_file, sha, wave
from schema_source import encoded, schemas
from validator import (
    compile_static_agent,
    validate_capability_manifest,
    validate_causal_manifest,
    validate_compatibility,
    validate_exhaust,
    validate_handshake_package,
    validate_learning_trace,
    validate_seed_capability_binding,
    verify_profile_frame,
)

FIXTURE = ROOT / "fixtures/softwarecoellc-vteam-hive"
AUTOBEST_FIXTURE = ROOT / "fixtures/generic-autobest-capability"


class CompatibilityProfileTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        path = os.environ.get("RAPP1_PATH")
        if not path:
            raise RuntimeError("RAPP1_PATH must name the exact pinned canonical checkout")
        cls.core = Parent(Path(path))
        cls.schemas = SchemaSet()
        cls.frame = cls.core.parse(read_file(FIXTURE / "compatibility-frame.json"))
        cls.handshake = json.loads(read_file(FIXTURE / "handshake.json"))
        cls.package = cls.core.parse(read_file(FIXTURE / "package.json"))
        cls.capability_index = cls.core.parse(read_file(ROOT / "capabilities/index.json"))
        cls.capability_entry = cls.capability_index["entries"][0]
        cls.capability = cls.core.parse(read_file(ROOT / cls.capability_entry["path"]))
        cls.workspace_seed = cls.core.parse(
            read_file(AUTOBEST_FIXTURE / "workspace-seed.json")
        )
        cls.seed_binding_frame = cls.core.parse(
            read_file(AUTOBEST_FIXTURE / "seed-capability-binding.json")
        )

    def test_generated_schemas_match_checked_files(self) -> None:
        self.assertEqual(
            {path.name for path in (ROOT / "schemas").glob("*.json")},
            set(schemas()),
        )
        for name, value in schemas().items():
            self.assertEqual(read_file(ROOT / "schemas" / name), encoded(value))

    def test_bill_fixture_pins_and_package_validate(self) -> None:
        self.assertEqual(
            sha(read_file(FIXTURE / "handshake.json")),
            "0c52264b81bf88dd8555defa9363a23d8eb8ef85c3c12f66ddcaaabfc85a8882",
        )
        self.assertEqual(
            sha(read_file(FIXTURE / "source-agent.py")),
            "679fff9531c0c8b13457d594f746c45da28925a7c1be40473e8ca00823db8671",
        )
        self.assertEqual(
            sha(read_file(FIXTURE / "target-finalizer.py")),
            "c056339f90fdd4e604dbefa40291f1b7b22946d26749b36230bb3b29dd8e2296",
        )
        validated = validate_handshake_package(self.package, self.schemas)
        self.assertEqual(validated["source_profile"], "microsol-project/1")
        self.assertEqual(validated["target_profile"], "microsol-repository-private-hive/1")
        self.assertEqual(
            validated["orchestrator_capability"],
            self.capability_entry["particle"],
        )
        qualification = self.core.parse(read_file(FIXTURE / "source-qualification.json"))
        self.schemas.validate(qualification, "source-qualification.schema.json")
        self.assertEqual(qualification["verified_frames"], 2)
        self.assertEqual(qualification["verified_artifacts"], 9)

    def test_compatibility_frame_is_rapp1_valid_and_non_authorizing(self) -> None:
        record = verify_profile_frame(self.core, self.frame)
        self.assertEqual(record["status"], "read-only")
        self.assertFalse(record["grants_authority"])
        self.assertEqual(record["lens"]["passes"], ["source-lens", "target-finalizer"])
        self.assertEqual(
            record["lens"]["orchestrator_capability"],
            self.capability_entry["particle"],
        )
        self.assertEqual(record["static_program"]["model_calls"], 0)
        self.assertGreater(record["coverage"]["basis_points"], 0)
        self.assertLess(record["coverage"]["basis_points"], 10000)

    def test_static_agent_reproduces_and_runs_with_zero_model_calls(self) -> None:
        generated = compile_static_agent(self.frame, self.handshake)
        checked = read_file(FIXTURE / "static-agent.py")
        self.assertEqual(generated, checked)
        source_frame = self.core.parse(read_file(FIXTURE / "source-frames/00000000.json"))
        request = json.dumps(
            {"direction": "source-to-target", "value": source_frame},
            sort_keys=True,
            separators=(",", ":"),
        ).encode()
        process = subprocess.run(
            [sys.executable, "-I", "-B", str(FIXTURE / "static-agent.py")],
            cwd=FIXTURE,
            env={
                "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
                "PYTHONDONTWRITEBYTECODE": "1",
                "PYTHONHASHSEED": "0",
                "LANG": "C",
                "LC_ALL": "C",
            },
            input=request,
            capture_output=True,
            check=False,
            timeout=30,
        )
        self.assertEqual(process.returncode, 0, process.stderr.decode())
        result = json.loads(process.stdout)
        self.assertTrue(result["ok"])
        self.assertEqual(result["model_calls"], 0)
        self.assertEqual(result["executed_effects"], 0)
        self.assertEqual(result["result"]["schema"], "microsol-hive-observation/1")
        self.assertFalse(result["result"]["authority"])
        unsigned_result = {
            key: value
            for key, value in result["result"].items()
            if key != "result_particle_hash"
        }
        self.assertEqual(
            result["result"]["result_particle_hash"],
            self.core.r.H("rapp/1:particle", unsigned_result),
        )

        reverse = subprocess.run(
            [sys.executable, "-I", "-B", str(FIXTURE / "static-agent.py")],
            cwd=FIXTURE,
            env={"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "PYTHONDONTWRITEBYTECODE": "1"},
            input=json.dumps(
                {
                    "direction": "target-to-source",
                    "value": {"peer": {}, "compatibility": {}, "subscription": {}},
                },
                sort_keys=True,
                separators=(",", ":"),
            ).encode(),
            capture_output=True,
            check=False,
            timeout=30,
        )
        self.assertEqual(reverse.returncode, 0, reverse.stderr.decode())
        self.assertEqual(
            json.loads(reverse.stdout)["result"]["schema"],
            "softwarecoellc-vteam-hive-peer-offer/1",
        )

    def test_frame_and_agent_mutations_fail(self) -> None:
        changed = deepcopy(self.frame)
        changed["payload"]["record"]["lens"]["source_agent"]["sha256"] = "f" * 64
        with self.assertRaises(Refusal):
            verify_profile_frame(self.core, changed)

        record = deepcopy(self.frame["payload"]["record"])
        record["grants_authority"] = True
        with self.assertRaises(Refusal):
            validate_compatibility(record, self.schemas)

        record = deepcopy(self.frame["payload"]["record"])
        record["coverage"]["basis_points"] -= 1
        with self.assertRaisesRegex(Refusal, "basis"):
            validate_compatibility(record, self.schemas)

        record = deepcopy(self.frame["payload"]["record"])
        record["bounds"]["max_lenses"] = 33
        with self.assertRaises(Refusal):
            validate_compatibility(record, self.schemas)

    def test_exhaust_is_typed_private_and_non_authorizing(self) -> None:
        record = self.frame["payload"]["record"]
        exhaust = {
            "schema": PROFILE + "/compatibility-exhaust",
            "instance_rappid": record["instance_rappid"],
            "world_id": record["world_id"],
            "activation_mode": record["activation_mode"],
            "activation": record["activation"],
            "restrictions": record["restrictions"],
            "active_compatibility": wave(self.frame),
            "source_head": record["source"]["head"],
            "target_head": None,
            "direction": "source-to-target",
            "code": "unmapped-operation",
            "locus": "payload.operation",
            "missing_coverage": ["unknown-operation"],
            "loss_class": "lossy-source-referenced",
            "consumed": record["bounds"],
            "retryable": True,
            "privacy_safe": True,
            "grants_authority": False,
        }
        self.assertEqual(validate_exhaust(exhaust)["code"], "unmapped-operation")
        changed = deepcopy(exhaust)
        changed["privacy_safe"] = False
        with self.assertRaises(Refusal):
            validate_exhaust(changed)

    def test_bidirectional_mutation_lineage_is_complete(self) -> None:
        source = {
            "path": "legacy/agent.py",
            "sha256": "1" * 64,
            "bytes": 10,
            "mode": "100644",
        }
        target = {
            "path": "agents/agent.py",
            "sha256": "1" * 64,
            "bytes": 10,
            "mode": "100644",
        }
        evidence = self.core.particle({"fixture": "move"})
        manifest = {
            "schema": PROFILE + "/causal-mutation-manifest",
            "source_parents": [
                {
                    "frame": wave(self.frame),
                    "commit": "a" * 40,
                    "inventory": self.core.particle({"source": [source]}),
                }
            ],
            "target_inventory": self.core.particle({"target": [target]}),
            "forward": [
                {
                    "source": source,
                    "disposition": "moved",
                    "targets": [target],
                    "content_relation": "identical",
                    "receipt": evidence,
                    "traits": ["connector-learning"],
                    "loss_class": "lossless-direct",
                }
            ],
            "reverse": [
                {
                    "target": target,
                    "provenance": "inherited",
                    "sources": [source],
                    "receipt": evidence,
                    "inverse_artifacts": [],
                    "loss_class": "lossless-direct",
                }
            ],
            "aggregate_loss_class": "lossless-direct",
            "inverse_artifacts": [],
            "selected_traits": ["connector-learning"],
            "omitted_traits": ["ambient-azure-storage"],
            "complete": True,
        }
        self.assertEqual(
            validate_causal_manifest(manifest)["aggregate_loss_class"],
            "lossless-direct",
        )
        broken = deepcopy(manifest)
        broken["reverse"] = []
        with self.assertRaisesRegex(Refusal, "partitions"):
            validate_causal_manifest(broken)

    def test_learning_trace_preserves_correction_authority_without_transcript(self) -> None:
        base_restrictions = self.frame["payload"]["record"]["restrictions"]
        scope = self.core.particle({"scope": "fixture"})
        claim = self.core.particle({"proposal": "read-only"})
        first = {
            "seq": 0,
            "previous_event": None,
            "kind": "assistant-proposal",
            "actor_class": "assistant-proposal",
            "source_refs": [self.core.particle({"source": "conversation"})],
            "scope": scope,
            "structured_claim": claim,
            "authority_evidence": None,
            "restrictions": base_restrictions,
        }
        second = {
            "seq": 1,
            "previous_event": self.core.particle(first),
            "kind": "user-correction",
            "actor_class": "user-authority",
            "source_refs": [self.core.particle({"source": "decision"})],
            "scope": scope,
            "structured_claim": self.core.particle({"correction": "no-membership-claim"}),
            "authority_evidence": self.core.particle({"authenticated": True}),
            "restrictions": base_restrictions,
        }
        trace = {
            "schema": PROFILE + "/learning-trace",
            "trigger": self.core.particle({"trigger": "wild-handshake"}),
            "events": [first, second],
            "decision_frontier": self.core.particle({"decisions": 1}),
            "receipt_frontier": self.core.particle({"receipts": 0}),
            "unresolved": 0,
            "raw_transcript_persisted": False,
            "hidden_reasoning_persisted": False,
            "native_paths_persisted": False,
            "restrictions": base_restrictions,
        }
        self.assertEqual(validate_learning_trace(trace, core=self.core)["unresolved"], 0)
        forged = deepcopy(trace)
        forged["events"][1]["actor_class"] = "assistant-proposal"
        with self.assertRaisesRegex(Refusal, "authority"):
            validate_learning_trace(forged, core=self.core)

    def test_exact_autobest_capability_and_seed_binding_are_inert(self) -> None:
        capability = validate_capability_manifest(self.capability, self.schemas)
        self.assertEqual(
            capability["agent"]["sha256"],
            "827f637c024e3fa1229148e5dcd78230a84ea3214283f899d22603741350f23c",
        )
        self.assertEqual(capability["agent"]["bytes"], 430291)
        self.assertEqual(
            capability["skill"]["sha256"],
            "5f8bd5b3c48858329f87ae3812dbc30ee604cb664985dc3d42a79e69d8bdfda8",
        )
        self.assertEqual(capability["skill"]["bytes"], 39139)
        self.assertEqual(self.capability_entry["particle"], self.core.particle(capability))
        self.assertFalse(capability["authority_from_presence"])
        self.assertFalse(capability["skill_activates"])
        self.assertFalse(capability["grants_authority"])
        for role in ("agent", "skill"):
            artifact = capability[role]
            raw = read_file(ROOT / artifact["path"])
            self.assertEqual(sha(raw), artifact["sha256"])
            self.assertEqual(len(raw), artifact["bytes"])

        ok, step, reason = self.core.r.verify_frame(
            self.workspace_seed,
            head=None,
            stream_id_of_record=self.workspace_seed["stream_id"],
        )
        self.assertTrue(ok, f"{step}: {reason}")
        self.assertEqual(self.workspace_seed["payload"]["schema"], "rapp-workspace/1/seed")
        binding = verify_profile_frame(self.core, self.seed_binding_frame)
        validated = validate_seed_capability_binding(
            binding,
            capability=capability,
            core=self.core,
            schemas=self.schemas,
        )
        self.assertEqual(validated["relation"], "ancestor-seed")
        self.assertFalse(validated["executable"])
        self.assertFalse(validated["grants_authority"])

    def test_autobest_agent_import_binds_exact_bytes_without_activation(self) -> None:
        agent_path = ROOT / self.capability["agent"]["path"]
        script = """
import importlib.util
import json
import sys
spec = importlib.util.spec_from_file_location("autobest_fixture", sys.argv[1])
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
binding = module.bind_implementation_sha256(sys.argv[2])
profile = module.profile_config("microsol-ceo")
print(json.dumps({
    "capability_id": module.__manifest__["capability_id"],
    "authority": module.__manifest__["authority"],
    "runtime": module.__manifest__["runtime"],
    "binding": binding,
    "profile_type": type(profile).__name__,
}, sort_keys=True))
"""
        process = subprocess.run(
            [
                sys.executable,
                "-I",
                "-B",
                "-c",
                script,
                str(agent_path),
                self.capability["agent"]["sha256"],
            ],
            cwd=agent_path.parent,
            env={
                "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
                "PYTHONDONTWRITEBYTECODE": "1",
                "PYTHONHASHSEED": "0",
                "LANG": "C",
                "LC_ALL": "C",
            },
            capture_output=True,
            check=False,
            timeout=60,
        )
        self.assertEqual(process.returncode, 0, process.stderr.decode())
        result = json.loads(process.stdout)
        self.assertEqual(result["capability_id"], "autobest:generic")
        self.assertFalse(result["authority"])
        self.assertFalse(result["runtime"])
        self.assertEqual(result["profile_type"], "dict")
        self.assertEqual(
            result["binding"]["implementation_sha256"],
            self.capability["agent"]["sha256"],
        )
        self.assertFalse(result["binding"]["authority_from_presence"])

    def test_autobest_capability_mutations_and_rebinding_refuse(self) -> None:
        changed = deepcopy(self.capability)
        changed["agent"]["sha256"] = "0" * 64
        with self.assertRaisesRegex(Refusal, "hash-addressed"):
            validate_capability_manifest(changed, self.schemas)

        binding = deepcopy(self.seed_binding_frame["payload"]["record"])
        binding["capability"] = {"space": "rapp/1:particle", "hash": "0" * 64}
        with self.assertRaisesRegex(Refusal, "particle mismatch"):
            validate_seed_capability_binding(
                binding,
                capability=self.capability,
                core=self.core,
                schemas=self.schemas,
            )

        descendant = deepcopy(self.seed_binding_frame["payload"]["record"])
        descendant["relation"] = "descendant-seed"
        descendant["ancestor_binding"] = wave(self.seed_binding_frame)
        descendant["parent_binding"] = wave(self.seed_binding_frame)
        self.assertEqual(
            validate_seed_capability_binding(
                descendant,
                capability=self.capability,
                core=self.core,
                schemas=self.schemas,
            )["relation"],
            "descendant-seed",
        )
        widened = deepcopy(descendant)
        widened["executable"] = True
        with self.assertRaises(Refusal):
            validate_seed_capability_binding(widened, schemas=self.schemas)

    def test_profile_does_not_ship_competing_microsol_generic_schema(self) -> None:
        for path in [ROOT / "SPEC.md", *sorted((ROOT / "schemas").glob("*.json"))]:
            content = read_file(path)
            self.assertNotIn(b"microsol-rapp-compatibility/1", content)

    def test_search_evolution_transport_and_promotion_stay_bounded_candidates(self) -> None:
        compatibility = self.frame["payload"]["record"]
        base = {
            "instance_rappid": compatibility["instance_rappid"],
            "world_id": compatibility["world_id"],
            "activation_mode": compatibility["activation_mode"],
            "activation": compatibility["activation"],
            "restrictions": compatibility["restrictions"],
        }
        candidate_bundle = self.core.particle({"bundle": "candidate"})
        evidence = self.core.particle({"evidence": True})
        lens = {
            "schema": PROFILE + "/lens-dimension",
            **base,
            "ancestor": wave(self.frame),
            "intent": self.core.particle({"intent": "whole-repository-mutation"}),
            "source_agent": self.package["source_agent"],
            "target_agent": self.package["target_agent"],
            "scope_traits": ["connector-learning", "schema-learning"],
            "parent_dimension": None,
            "budget": compatibility["bounds"],
            "candidate_limit": 4,
            "grants_authority": False,
        }
        self.schemas.validate(lens, "lens-dimension.schema.json")
        cross = {
            "schema": PROFILE + "/candidate-cross",
            **base,
            "parents": [
                wave(self.frame),
                {"space": "rapp/1:wave", "hash": "f" * 64},
            ],
            "selected_traits": ["connector-learning"],
            "omitted_traits": ["ambient-azure-storage"],
            "dependency_evidence": evidence,
            "result_bundle": candidate_bundle,
            "fitness_evidence": evidence,
            "lineage": evidence,
            "grants_authority": False,
        }
        self.schemas.validate(cross, "candidate-cross.schema.json")
        evolution = {
            "schema": PROFILE + "/evolution-proposal",
            **base,
            "level": "seed",
            "ancestors": [wave(self.frame)],
            "candidate_bundle": candidate_bundle,
            "scenario_corpus": evidence,
            "hidden_holdout": evidence,
            "controlled_mutants": evidence,
            "canary": evidence,
            "independent_verification": evidence,
            "promotion_target": "organization-seed",
            "automatic_promotion": False,
            "status": "candidate",
            "grants_authority": False,
        }
        self.schemas.validate(evolution, "evolution-proposal.schema.json")
        offer = {
            "schema": PROFILE + "/mutation-offer",
            **base,
            "ancestor_refs": [wave(self.frame)],
            "successor_bundle": candidate_bundle,
            "forward_map": evidence,
            "reverse_map": evidence,
            "compatibility": wave(self.frame),
            "tests": evidence,
            "selected_traits": ["connector-learning"],
            "omitted_traits": ["ambient-azure-storage"],
            "transport": {
                "kind": "pull-request",
                "base": "f66da3d879b53a439bc87de764d79f68ceec048a",
                "head": "candidate",
                "evidence": evidence,
            },
            "status": "candidate",
            "grants_authority": False,
        }
        self.schemas.validate(offer, "mutation-offer.schema.json")
        changed = deepcopy(evolution)
        changed["automatic_promotion"] = True
        with self.assertRaises(Refusal):
            self.schemas.validate(changed, "evolution-proposal.schema.json")


if __name__ == "__main__":
    unittest.main()
