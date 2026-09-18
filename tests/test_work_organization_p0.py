"""Adversarial P0 vectors for Work Organization/1."""

from __future__ import annotations

import copy
from pathlib import Path
import sys
import unittest


REPO = Path(__file__).resolve().parents[1]
REFERENCE = REPO / "protocols/rapp-work-organization/1/reference"
sys.path.insert(0, str(REFERENCE))

from atomic_agent import verify_bundle  # noqa: E402
from workorg_common import Refusal  # noqa: E402
from compiler import compile_static_bundle, compiler_pin  # noqa: E402
from protocol import (  # noqa: E402
    validate_activation_document,
    validate_bill_binding,
    validate_learning_trace,
)
from workorg_artifact import (  # noqa: E402
    ARTIFACT_RELATIVE,
    GENERIC_CEO_PROFILE_SHA256,
    GENERIC_CEO_SHA256,
    GENERIC_CEO_SKILL_SHA256,
    validate_generic_ceo_artifact,
)
try:
    from tests.test_work_organization import (  # noqa: E402
        HASH1,
        HASH2,
        HASH3,
        HASH4,
        RAPPID,
        particle_ref,
        trace,
        wave,
    )
except ModuleNotFoundError:
    from test_work_organization import (  # type: ignore[no-redef]  # noqa: E402
        HASH1,
        HASH2,
        HASH3,
        HASH4,
        RAPPID,
        particle_ref,
        trace,
        wave,
    )


class WorkOrganizationP0Tests(unittest.TestCase):
    def bundle(self):
        return compile_static_bundle(
            compatibility_frame=wave(HASH1),
            compatibility_frame_octets_sha256=HASH2,
            locked_profile={
                "coverage": {"forward_bp": 10000, "reverse_bp": 5000},
                "gaps": ["unknown-operation"],
                "restrictions": {"model_calls": 0, "network": False},
            },
            program_source=b"def perform(value):\n    return value\n",
            extra_files={"tests/candidate/test_generated.py": b"assert True\n"},
            bundle_rappid=RAPPID,
            runtime_manifest_sha256=HASH3,
            source_mutation_manifest=particle_ref(HASH4),
            compiler_sha256=compiler_pin(),
        )

    def test_candidate_tests_never_self_certify(self) -> None:
        bundle = self.bundle()
        self.assertFalse(bundle["manifest"]["candidate_tests_are_independent_proof"])
        self.assertFalse(bundle["generation_receipt"]["grants_authority"])

    def test_bundle_byte_substitution_refuses(self) -> None:
        bundle = self.bundle()
        files = dict(bundle["files"])
        files["agent.py"] += b"\n# substituted\n"
        with self.assertRaisesRegex(Refusal, "differ"):
            verify_bundle(bundle["manifest"], files)

    def test_undeclared_file_refuses(self) -> None:
        bundle = self.bundle()
        files = dict(bundle["files"])
        files["ambient.py"] = b"VALUE = 1\n"
        with self.assertRaisesRegex(Refusal, "inventory differ"):
            verify_bundle(bundle["manifest"], files)

    def test_forged_user_authority_refuses(self) -> None:
        value = trace()
        value["events"][0]["authority"] = "host-attested-user-authority"
        with self.assertRaisesRegex(Refusal, "never user authority"):
            validate_learning_trace(value)

    def test_private_path_leak_refuses(self) -> None:
        value = trace()
        value["events"][2]["structured_content"]["source"] = "/Users/private/input.json"
        with self.assertRaisesRegex(Refusal, "private material"):
            validate_learning_trace(value)

    def test_missing_correction_invariant_refuses(self) -> None:
        value = trace()
        value["events"] = value["events"][:2]
        value["ordered_event_hashes"] = value["ordered_event_hashes"][:2]
        with self.assertRaisesRegex(Refusal, "Every correction"):
            validate_learning_trace(value)

    def test_trace_predecessor_mismatch_refuses(self) -> None:
        value = trace()
        value["events"][1]["previous_event"] = wave(HASH4)
        with self.assertRaisesRegex(Refusal, "predecessor"):
            validate_learning_trace(value)

    def test_bill_pin_substitution_refuses(self) -> None:
        binding = __import__("json").loads(
            (
                REPO
                / "protocols/rapp-work-organization/1/fixtures/softwarecoellc-vteam-hive-1.json"
            ).read_text()
        )
        binding["source_lens"]["sha256"] = "f" * 64
        with self.assertRaisesRegex(Refusal, "source_lens pin differs"):
            validate_bill_binding(binding)

    def test_generic_ceo_binding_substitution_refuses(self) -> None:
        binding = __import__("json").loads(
            (
                REPO
                / "protocols/rapp-work-organization/1/fixtures/softwarecoellc-vteam-hive-1.json"
            ).read_text()
        )
        binding["generic_ceo_agent"]["sha256"] = HASH1
        with self.assertRaisesRegex(Refusal, "exact verified"):
            validate_bill_binding(binding)

    def test_generic_ceo_artifact_byte_mutation_refuses(self) -> None:
        root = REPO / "protocols/rapp-work-organization/1" / ARTIFACT_RELATIVE
        profile = __import__("json").loads((root / "profile.json").read_text())
        agent = bytearray((root / "agent.py").read_bytes())
        agent[-1] ^= 1
        with self.assertRaisesRegex(Refusal, "agent bytes differ"):
            validate_generic_ceo_artifact(
                profile,
                bytes(agent),
                (root / "SKILL.md").read_bytes(),
            )

    def test_activation_with_wrong_ceo_pin_refuses(self) -> None:
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
            "generic_ceo_agent_sha256": HASH1,
            "generic_ceo_skill_sha256": GENERIC_CEO_SKILL_SHA256,
            "generic_ceo_artifact_profile_sha256": GENERIC_CEO_PROFILE_SHA256,
        }
        with self.assertRaisesRegex(Refusal, "exact generic CEO"):
            validate_activation_document(document)


if __name__ == "__main__":
    unittest.main()
