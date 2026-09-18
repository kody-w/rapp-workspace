"""Generate and verify the exact generic CEO/AutoBest artifact profile."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from workorg_common import (
    ROOT,
    canonical_bytes,
    exact_object,
    hash_value,
    pretty_bytes,
    read_bytes,
    require,
    sha256,
)


GENERIC_CEO_SHA256 = "827f637c024e3fa1229148e5dcd78230a84ea3214283f899d22603741350f23c"
GENERIC_CEO_BYTES = 430291
GENERIC_CEO_SKILL_SHA256 = "5f8bd5b3c48858329f87ae3812dbc30ee604cb664985dc3d42a79e69d8bdfda8"
GENERIC_CEO_SKILL_BYTES = 39139
GENERIC_CEO_PROFILE_SHA256 = "568bb863d3c3f01109f6a4a40a56833127c6d6e509ef09b5433a40d92a83065a"
GENERIC_CEO_PROFILE_BYTES = 1819
GENERIC_CEO_VERSION = "3.0.0"
ARTIFACT_RELATIVE = (
    "artifacts/generic-ceo/"
    + GENERIC_CEO_SHA256
)
ARTIFACT = ROOT / ARTIFACT_RELATIVE
PROFILE_PATH = ARTIFACT / "profile.json"

OPERATIONS = [
    "delegate",
    "cross",
    "run",
    "compatibility",
    "compatibility_exhaust",
    "compatibility_successor",
    "double_hotload",
    "compile_static_agent",
    "self_host_repository",
    "artifact_bundle",
    "mutation_offer",
    "mutation_offer_decision",
    "meta_evolution",
    "n_lens_search",
    "translate_hive",
    "ceo",
    "microsol-ceo",
]


def _entry(path: str, data: bytes, role: str) -> dict[str, Any]:
    return {
        "path": path,
        "role": role,
        "sha256": sha256(data),
        "bytes": len(data),
    }


def profile(agent: bytes, skill: bytes) -> dict[str, Any]:
    require(
        sha256(agent) == GENERIC_CEO_SHA256 and len(agent) == GENERIC_CEO_BYTES,
        "REFUSE_GENERIC_CEO",
        "Generic CEO agent bytes differ from the approved pin.",
    )
    require(
        sha256(skill) == GENERIC_CEO_SKILL_SHA256
        and len(skill) == GENERIC_CEO_SKILL_BYTES,
        "REFUSE_GENERIC_CEO",
        "Generic CEO skill bytes differ from the approved pin.",
    )
    files = [
        _entry("agent.py", agent, "brainstem-hotload-entrypoint"),
        _entry("SKILL.md", skill, "human-and-agent-operating-guide"),
    ]
    return {
        "schema": "rapp-work-organization/1/generic-ceo-artifact",
        "id": "autobest:generic",
        "name": "@kody-w/microsol_autobest",
        "version": GENERIC_CEO_VERSION,
        "status": "verified",
        "content_address": {
            "algorithm": "sha256",
            "subject": "exact-agent.py-bytes",
            "hash": GENERIC_CEO_SHA256,
        },
        "entrypoint": "agent.py",
        "files": files,
        "aggregate_sha256": sha256(canonical_bytes(files)),
        "runtime": {
            "stdlib_only": True,
            "deterministic": True,
            "single_file_entrypoint": True,
            "requires_environment": False,
            "reads_files": False,
            "reads_stdin": False,
            "uses_clock": False,
            "uses_randomness": False,
            "uses_network": False,
            "uses_subprocess": False,
        },
        "binding": {
            "api": "bind_implementation_sha256",
            "required_before_activation": True,
            "external_host_only": True,
        },
        "operations": OPERATIONS,
        "authority": False,
        "authority_from_presence": False,
        "brainstem_modified": False,
        "estate_activation": False,
    }


def validate_generic_ceo_artifact(
    value: Any,
    agent: bytes,
    skill: bytes,
) -> dict[str, Any]:
    expected = profile(agent, skill)
    require(value == expected, "REFUSE_GENERIC_CEO", "Generic CEO artifact profile drift.")
    encoded = pretty_bytes(value)
    require(
        sha256(encoded) == GENERIC_CEO_PROFILE_SHA256
        and len(encoded) == GENERIC_CEO_PROFILE_BYTES,
        "REFUSE_GENERIC_CEO",
        "Generic CEO artifact profile pin differs.",
    )
    exact_object(
        value,
        {
            "schema",
            "id",
            "name",
            "version",
            "status",
            "content_address",
            "entrypoint",
            "files",
            "aggregate_sha256",
            "runtime",
            "binding",
            "operations",
            "authority",
            "authority_from_presence",
            "brainstem_modified",
            "estate_activation",
        },
        "REFUSE_GENERIC_CEO",
    )
    hash_value(value["content_address"]["hash"], "REFUSE_GENERIC_CEO")
    require(
        value["authority"] is False
        and value["authority_from_presence"] is False
        and value["brainstem_modified"] is False
        and value["estate_activation"] is False,
        "REFUSE_GENERIC_CEO",
        "Artifact presence cannot grant or claim authority.",
    )
    return value


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    agent = read_bytes(ARTIFACT / "agent.py", GENERIC_CEO_BYTES)
    skill = read_bytes(ARTIFACT / "SKILL.md", GENERIC_CEO_SKILL_BYTES)
    expected = pretty_bytes(profile(agent, skill))
    if args.write:
        PROFILE_PATH.write_bytes(expected)
    good = (
        PROFILE_PATH.is_file()
        and PROFILE_PATH.read_bytes() == expected
        and sha256(expected) == GENERIC_CEO_PROFILE_SHA256
        and len(expected) == GENERIC_CEO_PROFILE_BYTES
    )
    if args.check or not args.write:
        print("RAPP Work Organization/1 generic CEO artifact: " + ("PASS" if good else "FAIL"))
    return int(not good)


if __name__ == "__main__":
    raise SystemExit(main())
