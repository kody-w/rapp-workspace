"""Import the exact generic AutoBest/CEO capability and seed binding fixture."""

from __future__ import annotations

import argparse
from pathlib import Path

from common import (
    PROFILE,
    ROOT,
    Parent,
    read_file,
    require,
    sha,
    wave,
    write_file,
)
from validator import (
    artifact_descriptor,
    validate_capability_manifest,
    validate_seed_capability_binding,
)

AGENT_SHA256 = "827f637c024e3fa1229148e5dcd78230a84ea3214283f899d22603741350f23c"
AGENT_BYTES = 430291
SKILL_SHA256 = "5f8bd5b3c48858329f87ae3812dbc30ee604cb664985dc3d42a79e69d8bdfda8"
SKILL_BYTES = 39139
WORKSPACE = "rappid:@fixture/autobest-workspace:" + "4" * 64
CAPABILITY_INSTANCE = "rappid:@fixture/autobest-capability:" + "5" * 64
WORLD = "generic-autobest-capability-fixture"
WORKSPACE_SPEC_SHA256 = "80135ae05e532f11810d31a5cf974050a8332c18bd45f16879a7286f213edfab"
FIXTURE = ROOT / "fixtures/generic-autobest-capability"


def profile_restrictions() -> dict:
    return {
        "rights": {
            "capture": False,
            "local_synthesis": False,
            "model_submission": False,
            "retention": True,
            "redistribution": False,
            "adoption": False,
            "materialization": False,
            "execution": False,
        },
        "privacy": "godd",
        "audience": ["fixture-owner"],
        "hashes_sensitive": True,
        "repository_content_is_instructions": False,
        "grants_authority": False,
        "authorizes_effects": False,
    }


def workspace_restrictions() -> dict:
    return {
        "rights": {
            "capture": False,
            "local_synthesis": False,
            "model_submission": False,
            "retention": True,
            "redistribution": False,
            "adoption": False,
            "materialization": False,
            "execution": False,
        },
        "privacy": "godd",
        "hashes_sensitive": True,
        "deletion": "no-guaranteed-recall",
        "retention": "append-only-local",
        "audience": ["fixture-owner"],
    }


def generate(source: Path, rapp1_path: Path) -> None:
    agent_source = source / "agent.py"
    skill_source = source / "SKILL.md"
    agent_raw = read_file(agent_source)
    skill_raw = read_file(skill_source)
    require(
        sha(agent_raw) == AGENT_SHA256 and len(agent_raw) == AGENT_BYTES,
        "generic AutoBest agent pin mismatch",
    )
    require(
        sha(skill_raw) == SKILL_SHA256 and len(skill_raw) == SKILL_BYTES,
        "generic AutoBest Skill pin mismatch",
    )
    core = Parent(rapp1_path)
    agent_path = f"artifacts/sha256/{AGENT_SHA256}/agent.py"
    skill_path = f"artifacts/sha256/{SKILL_SHA256}/SKILL.md"
    write_file(ROOT / agent_path, agent_raw)
    write_file(ROOT / skill_path, skill_raw)
    agent = artifact_descriptor(
        core,
        agent_path,
        agent_raw,
        role="generic-autobest-agent",
        media_type="text/x-python",
    )
    skill = artifact_descriptor(
        core,
        skill_path,
        skill_raw,
        role="generic-autobest-skill",
        media_type="text/markdown",
    )
    capability = {
        "schema": PROFILE + "/capability-manifest",
        "capability_id": "autobest:generic",
        "version": 1,
        "tile_schema": "rapp-work-capability-tile/1",
        "tile_subject": "exact-agent.py-bytes",
        "agent": agent,
        "skill": skill,
        "profiles": ["generic", "microsol-ceo"],
        "invoker": "external-global-brainstem",
        "activation": "external-host-only",
        "mutation": "successor-only",
        "rapp1_role": "core-compatibility-substrate",
        "authority_from_presence": False,
        "skill_activates": False,
        "grants_authority": False,
    }
    validate_capability_manifest(capability)
    capability_particle = core.particle(capability)
    capability_path = (
        "capabilities/rapp-particle/"
        + capability_particle["hash"]
        + "/capability.json"
    )
    write_file(ROOT / capability_path, core.octets(capability))
    capability_index = {
        "schema": PROFILE + "/capability-index",
        "entries": [
            {
                "capability_id": "autobest:generic",
                "version": 1,
                "path": capability_path,
                "particle": capability_particle,
                "agent": {
                    "path": agent_path,
                    "sha256": AGENT_SHA256,
                    "bytes": AGENT_BYTES,
                },
                "skill": {
                    "path": skill_path,
                    "sha256": SKILL_SHA256,
                    "bytes": SKILL_BYTES,
                },
                "status": "verified-inert-capability",
            }
        ],
        "authority": False,
    }
    write_file(ROOT / "capabilities/index.json", core.octets(capability_index))

    activation_value = {"fixture": "generic-autobest", "mode": "synthetic"}
    activation = core.particle(activation_value)
    workspace_seed_payload = {
        "schema": "rapp-workspace/1/seed",
        "instance_rappid": WORKSPACE,
        "world_id": WORLD,
        "activation_mode": "synthetic",
        "activation": activation,
        "native_subject": {
            "namespace": "fixture",
            "native_key": "generic-autobest-workspace",
        },
        "restrictions": workspace_restrictions(),
        "generation": "workspace1-core",
        "spec_sha256": WORKSPACE_SPEC_SHA256,
        "immutable_invariants": True,
        "effect_authority": "external-controller-only",
    }
    workspace_seed = core.r.build_frame(
        "body.pulse",
        WORKSPACE,
        0,
        "2030-01-03T00:00:00.000Z",
        workspace_seed_payload,
        None,
    )
    binding = {
        "schema": PROFILE + "/seed-capability-binding",
        "instance_rappid": CAPABILITY_INSTANCE,
        "world_id": WORLD,
        "activation_mode": "synthetic",
        "activation": activation,
        "restrictions": profile_restrictions(),
        "workspace_seed": wave(workspace_seed),
        "workspace_profile": "rapp-workspace/1",
        "workspace_spec_sha256": WORKSPACE_SPEC_SHA256,
        "capability": capability_particle,
        "agent": agent["particle"],
        "skill": skill["particle"],
        "relation": "ancestor-seed",
        "ancestor_binding": None,
        "parent_binding": None,
        "previous_binding": None,
        "inheritance": "reference-only",
        "executable": False,
        "host_activation": "external-host-only",
        "mutation": "successor-only",
        "grants_authority": False,
    }
    validate_seed_capability_binding(binding, capability=capability, core=core)
    binding_frame = core.r.build_frame(
        "body.pulse",
        CAPABILITY_INSTANCE,
        0,
        "2030-01-03T00:00:01.000Z",
        {
            "profile": PROFILE,
            "operation": "seed-capability-binding",
            "record": binding,
        },
        None,
    )
    write_file(FIXTURE / "workspace-seed.json", core.octets(workspace_seed))
    write_file(FIXTURE / "seed-capability-binding.json", core.octets(binding_frame))
    fixture_index = {
        "schema": PROFILE + "/autobest-capability-fixture-index",
        "source_workspace": source.parents[2].name,
        "capability": capability_particle,
        "capability_path": capability_path,
        "agent_sha256": AGENT_SHA256,
        "agent_bytes": AGENT_BYTES,
        "skill_sha256": SKILL_SHA256,
        "skill_bytes": SKILL_BYTES,
        "workspace_seed": wave(workspace_seed),
        "seed_binding": wave(binding_frame),
        "authority": False,
    }
    write_file(FIXTURE / "fixture-index.json", core.octets(fixture_index))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--rapp1-path", type=Path, required=True)
    arguments = parser.parse_args()
    generate(arguments.source, arguments.rapp1_path)
    print("Generic AutoBest capability: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
