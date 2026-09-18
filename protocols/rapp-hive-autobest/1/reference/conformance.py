#!/usr/bin/env python3
"""Conformance vectors for rapp-hive-autobest/1."""

from __future__ import annotations

import base64
import copy
import hashlib
import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path
from typing import Any

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
REFERENCE = Path(__file__).resolve().parent
FIXTURE = ROOT / "fixtures" / "softwarecoellc-vteam-hive"
CEO_FIXTURE = ROOT / "fixtures" / "generic-ceo-autobest"
HIVE_REFERENCE = ROOT.parents[1] / "rapp-hive" / "1" / "reference"
for value in (str(REFERENCE), str(HIVE_REFERENCE)):
    if value not in sys.path:
        sys.path.insert(0, value)

import rapp as R  # noqa: E402
import rapp_hive_autobest as A  # noqa: E402
from rapp_profile import particle_hash  # noqa: E402
from schema_source import build_schema  # noqa: E402


def digest(label: str | bytes) -> str:
    value = label if isinstance(label, bytes) else label.encode("utf-8")
    return hashlib.sha256(value).hexdigest()


def rid(owner: str, slug: str, fill: str) -> str:
    return f"rappid:@{owner}/{slug}:{fill * 64}"


def address(label: str, space: str = "rapp/1:particle") -> dict[str, str]:
    return {"space": space, "hash": digest(label)}


def wave(label: str) -> dict[str, str]:
    return address(label, "rapp/1:wave")


def frame_summary(stream_id: str, sequence: int, label: str) -> dict[str, Any]:
    return {
        "stream_id": stream_id,
        "seq": sequence,
        "utc": f"2030-01-01T00:00:{sequence:02d}.000Z",
        "payload_hash": digest(label + "-payload"),
        "frame_hash": digest(label + "-frame"),
    }


HIVE = rid("example", "private-hive", "1")
COMPATIBILITY = rid("example", "compatibility", "2")
TARGET = rid("example", "target-workspace", "3")
DIMENSION = rid("billwhalenmsft", "softwarecoellc-vteam-hive", "4")
WORLD = "bill-interop-private"


def agent_pin(role: str, label: str) -> dict[str, Any]:
    return {
        "role": role,
        "artifact": address(label + "-artifact"),
        "sha256": digest(label + "-bytes"),
        "bytes": 1024,
        "runtime_sha256": digest(label + "-runtime"),
        "policy_sha256": digest(label + "-policy"),
    }


def source_vector() -> list[dict[str, Any]]:
    head = frame_summary(DIMENSION + ":project-softwarecoellc-vteam-hive", 1, "bill")
    return [
        {
            "dimension_rappid": DIMENSION,
            "work_group_id": "bill-read",
            "branch_id": "shared-trunk",
            "branch_kind": "shared-trunk",
            "head": head,
            "workspace_binding": wave("workspace-binding"),
            "observation_receipt": wave("observation-receipt"),
            "checkpoint_receipt": wave("checkpoint-receipt"),
        }
    ]


def source_vector_pair() -> list[dict[str, Any]]:
    first = source_vector()[0]
    second_dimension = rid("example", "alternative-dimension", "6")
    second = {
        "dimension_rappid": second_dimension,
        "work_group_id": "bill-read",
        "branch_id": "difference-b",
        "branch_kind": "crossing-parent",
        "head": frame_summary(second_dimension + ":work", 2, "alternative"),
        "workspace_binding": wave("workspace-binding-b"),
        "observation_receipt": wave("observation-receipt-b"),
        "checkpoint_receipt": wave("checkpoint-receipt-b"),
    }
    first = {**first, "branch_kind": "crossing-parent"}
    return sorted([first, second], key=lambda value: (value["head"]["utc"], value["head"]["frame_hash"]))


def file_head(path: str, label: str, *, mode: str = "100644") -> dict[str, Any]:
    data_hash = digest(label)
    return {
        "path": path,
        "mode": mode,
        "bytes": len(label.encode("utf-8")),
        "sha256": data_hash,
        "content": address(label + "-content"),
    }


def lineage_fixture() -> dict[str, Any]:
    source_a = file_head("agents/old.py", "old-agent")
    source_b = file_head("schemas/old.json", "old-schema")
    successor_a = file_head("agent.py", "new-agent")
    successor_b = file_head("schemas/current.json", "new-schema")
    successor_c = file_head("tests/mutation.json", "new-tests")
    return {
        "schema": A.LINEAGE_SCHEMA,
        "source": {
            "frame": wave("source-generation"),
            "repository": {
                "repository": "https://github.com/example/source",
                "branch": "main",
                "commit": {"algorithm": "sha1", "oid": "1" * 40},
                "inventory_hash": digest("source-inventory"),
                "file_count": 2,
                "total_bytes": 19,
            },
            "inventory_hash": digest("source-inventory"),
            "file_count": 2,
            "total_bytes": 19,
        },
        "successor": {
            "frame": wave("successor-generation"),
            "repository": None,
            "inventory_hash": digest("successor-inventory"),
            "file_count": 3,
            "total_bytes": 28,
        },
        "forward": [
            {
                "source": source_a,
                "disposition": "moved-and-replaced",
                "successors": [successor_a],
                "receipt": address("move-replace-receipt"),
            },
            {
                "source": source_b,
                "disposition": "replaced",
                "successors": [successor_b],
                "receipt": address("replace-receipt"),
            },
        ],
        "reverse": [
            {
                "successor": successor_a,
                "origin": "derived",
                "sources": [source_a],
                "inverse_method": "retained-delta",
                "inverse_artifacts": [address("agent-inverse")],
            },
            {
                "successor": successor_b,
                "origin": "derived",
                "sources": [source_b],
                "inverse_method": "retained-delta",
                "inverse_artifacts": [address("schema-inverse")],
            },
            {
                "successor": successor_c,
                "origin": "new",
                "sources": [],
                "inverse_method": "identity",
                "inverse_artifacts": [],
            },
        ],
        "selected_traits": [
            {
                "id": "schema-learning",
                "status": "replaced",
                "source_refs": [address("old-schema-trait")],
                "successor_refs": [address("new-schema-trait")],
                "reason_code": "qualified-successor",
            }
        ],
        "omitted_traits": [
            {
                "id": "ambient-azure",
                "status": "omitted",
                "source_refs": [address("azure-trait")],
                "successor_refs": [],
                "reason_code": "unsafe-substrate",
            }
        ],
        "loss_class": "exact-lossless",
        "reconstruction": {
            "required": True,
            "implementation": address("inverse-program"),
            "retained_deltas": [address("agent-inverse"), address("schema-inverse")],
            "receipt": address("reconstruction-receipt"),
        },
        "coverage": {
            "source_total": 2,
            "source_mapped": 2,
            "successor_total": 3,
            "successor_mapped": 3,
        },
    }


def trace_fixture() -> dict[str, Any]:
    events = []
    specs = [
        ("user-intent", "user", "observed-user-input", "convert-source", [], ["intent-v1"]),
        ("assistant-proposal", "assistant", "proposal-only", "proposal-v1", [], []),
        ("user-correction", "user", "user-decision", "correction-v1", [1], ["no-auto-authority"]),
        ("assumption-superseded", "host", "host-validation", "superseded-v1", [1], ["no-auto-authority"]),
        ("successor-invariant", "host", "host-validation", "invariant-v1", [2], ["no-auto-authority"]),
    ]
    previous = None
    for index, (event_type, actor, authority, code, supersedes, invariants) in enumerate(specs):
        event = {
            "index": index,
            "previous_event_hash": previous,
            "event_type": event_type,
            "actor_class": actor,
            "authority_class": authority,
            "source_refs": [address(f"trace-source-{index}")],
            "result_code": code,
            "evidence_refs": [address(f"trace-evidence-{index}")],
            "supersedes_event_ids": supersedes,
            "successor_invariant_ids": invariants,
        }
        event["event_hash"] = particle_hash(event)
        events.append(event)
        previous = event["event_hash"]
    return {
        "schema": A.TRACE_SCHEMA,
        "trace_id": "bill-first-handshake",
        "compatibility_predecessor": None,
        "sanitizer_policy_sha256": digest("trace-sanitizer"),
        "source_commitments": [address("trace-source-root")],
        "events": events,
        "correction_coverage_bps": 10000,
        "trace_root_hash": previous,
        "privacy_status": "sanitized-sealed-default",
    }


def search_fixture() -> dict[str, Any]:
    lenses = [
        {
            "id": "lens-a",
            "agent": agent_pin("source-lens", "lens-a"),
            "prompt_sha256": digest("lens-a-prompt"),
            "policy_sha256": digest("lens-a-policy"),
            "source_vector": source_vector(),
            "budget_units": 10,
        },
        {
            "id": "lens-b",
            "agent": agent_pin("source-lens", "lens-b"),
            "prompt_sha256": digest("lens-b-prompt"),
            "policy_sha256": digest("lens-b-policy"),
            "source_vector": source_vector(),
            "budget_units": 10,
        },
    ]
    candidates = [
        {
            "id": "candidate-a",
            "lens_id": "lens-a",
            "kind": "complete-successor",
            "artifact": address("candidate-a"),
            "trait_ids": ["parser-a"],
            "parents": [],
            "scenario_evidence": address("candidate-a-scenarios"),
            "coverage_bps": 8000,
            "unknowns": ["membership"],
        },
        {
            "id": "candidate-b",
            "lens_id": "lens-b",
            "kind": "trait-delta",
            "artifact": address("candidate-b"),
            "trait_ids": ["strict-json"],
            "parents": [],
            "scenario_evidence": address("candidate-b-scenarios"),
            "coverage_bps": 7000,
            "unknowns": ["board"],
        },
        {
            "id": "candidate-cross",
            "lens_id": "lens-a",
            "kind": "complete-successor",
            "artifact": address("candidate-cross"),
            "trait_ids": ["parser-a", "strict-json"],
            "parents": ["candidate-a", "candidate-b"],
            "scenario_evidence": address("candidate-cross-scenarios"),
            "coverage_bps": 9000,
            "unknowns": ["membership"],
        },
    ]
    return {
        "schema": A.SEARCH_SCHEMA,
        "root_id": "bill-search",
        "ancestor": wave("bill-ancestor"),
        "bounds": {
            "max_lenses": 4,
            "max_candidates": 16,
            "max_cross_size": 3,
            "max_depth": 4,
            "max_rounds": 4,
            "max_evaluations": 64,
            "max_generated_bytes": 1048576,
            "max_tool_calls": 32,
            "beam_width": 8,
            "pareto_limit": 8,
            "reserved_stop_frames": 1,
        },
        "lenses": lenses,
        "candidates": candidates,
        "crosses": [
            {
                "id": "cross-a-b",
                "candidate_ids": ["candidate-a", "candidate-b"],
                "trait_ids": ["parser-a", "strict-json"],
                "output_candidate_id": "candidate-cross",
                "crossing_lens": wave("crossing-lens"),
            }
        ],
        "selection": {
            "mode": "select-complete",
            "selected_candidates": ["candidate-cross"],
            "selected_traits": ["parser-a", "strict-json"],
            "scenario": address("declared-use-case"),
            "coverage_bps": 9000,
            "unknowns": ["membership"],
        },
        "stop": None,
        "grants_authority": False,
    }


def bundle_fixture(lineage: dict[str, Any]) -> dict[str, Any]:
    files = [
        {
            "path": "agent.py",
            "role": "entrypoint",
            "bytes": 5003,
            "sha256": "46c981ac9660f24a2e02809ce1957e28b3c9497f85cb60a3f4ff4b06c0455a18",
            "content": address("static-agent-content"),
        },
        {
            "path": "compatibility.json",
            "role": "manifest",
            "bytes": 1024,
            "sha256": digest("compatibility-json"),
            "content": address("compatibility-json-content"),
        },
        {
            "path": "tests/mutation.json",
            "role": "candidate-test",
            "bytes": 512,
            "sha256": digest("mutation-tests"),
            "content": address("mutation-tests-content"),
        },
    ]
    return {
        "schema": A.BUNDLE_SCHEMA,
        "bundle_rappid": rid("example", "handshake-bundle", "5"),
        "created_utc": "2030-01-01T00:00:10.000Z",
        "compatibility": wave("compatibility-frame"),
        "entrypoint": "agent.py",
        "files": files,
        "lineage": address(particle_hash(lineage)),
        "contracts": sorted(
            [address("source-contract"), address("target-contract")],
            key=lambda value: (value["space"], value["hash"]),
        ),
        "generated_tests": [address("candidate-tests")],
        "docs_are_instructions": False,
        "migrations_auto_execute": False,
        "authority": False,
    }


def compatibility_fixture(
    bundle: dict[str, Any],
    lineage: dict[str, Any],
    trace: dict[str, Any],
    search: dict[str, Any],
) -> dict[str, Any]:
    legacy = json.loads((FIXTURE / "static" / "compatibility-frame.json").read_text())
    record = legacy["payload"]["record"]
    source_rappid = record["source"]["rappid"]
    source_head = {
        **record["source"]["qualification_head"],
        "utc": "2026-09-17T21:22:06.877Z",
    }
    capabilities = [
        {
            "id": key.replace("_", "-"),
            "status": (
                "verified"
                if value == "verified"
                else "partial"
                if value in {"partial", "available-on-exhaust"}
                else "unavailable"
            ),
            "method": "signed-stream-inference",
            "coverage_bps": 10000 if value == "verified" else 5000 if value == "partial" else 0,
            "evidence": [wave("legacy-compatibility-frame")],
            "reason_code": value.replace("_", "-"),
        }
        for key, value in sorted(record["capabilities"].items())
    ]
    source_agent = (FIXTURE / "source-agent.py").read_bytes()
    target_agent = (FIXTURE / "target-finalizer.py").read_bytes()
    static_agent = (FIXTURE / "static" / "agent.py").read_bytes()
    ceo_binding = json.loads((CEO_FIXTURE / "binding.json").read_text())
    return {
        "schema": A.COMPATIBILITY_SCHEMA,
        "hive_rappid": HIVE,
        "world_id": WORLD,
        "compatibility_rappid": COMPATIBILITY,
        "created_utc": "2030-01-01T00:00:20.000Z",
        "previous_compatibility": None,
        "trigger": {"kind": "initial-handshake", "exhaust": None},
        "source": {
            "endpoint_rappid": source_rappid,
            "profile": record["source"]["profile"],
            "profile_pin": {"status": "unavailable", "value": None},
            "head_status": "verified",
            "head": source_head,
            "snapshot": {
                "repository": record["source"]["repository"],
                "branch": record["source"]["branch"],
                "commit": {"algorithm": "sha1", "oid": record["source"]["commit"]},
                "inventory_hash": record["source"]["snapshot_hash"],
                "file_count": 9,
                "total_bytes": 0,
            },
            "capabilities": capabilities,
        },
        "target": {
            "endpoint_rappid": TARGET,
            "profile": record["target"]["profile"],
            "profile_pin": {"status": "verified", "value": digest("target-profile")},
            "head_status": "not-applicable",
            "head": None,
            "snapshot": None,
            "capabilities": [
                {
                    "id": "read",
                    "status": "verified",
                    "method": "native-protocol",
                    "coverage_bps": 10000,
                    "evidence": [address("target-read")],
                    "reason_code": "verified",
                },
                {
                    "id": "status",
                    "status": "verified",
                    "method": "native-protocol",
                    "coverage_bps": 10000,
                    "evidence": [address("target-status")],
                    "reason_code": "verified",
                },
            ],
        },
        "source_lens": {
            "role": "source-lens",
            "artifact": address("bill-source-agent"),
            "sha256": hashlib.sha256(source_agent).hexdigest(),
            "bytes": len(source_agent),
            "runtime_sha256": digest("global-brainstem-runtime"),
            "policy_sha256": digest("bill-source-policy"),
        },
        "target_finalizer": {
            "role": "target-finalizer",
            "artifact": address("microsol-target-finalizer"),
            "sha256": hashlib.sha256(target_agent).hexdigest(),
            "bytes": len(target_agent),
            "runtime_sha256": digest("global-brainstem-runtime"),
            "policy_sha256": digest("target-finalizer-policy"),
        },
        "autobest_controller": {
            "capability_id": "autobest:generic",
            "profile": "microsol-ceo",
            "artifact": ceo_binding["profile_artifact"],
            "binding": {
                "space": "rapp/1:particle",
                "hash": particle_hash(ceo_binding),
            },
            "agent_sha256": ceo_binding["agent"]["sha256"],
            "agent_bytes": ceo_binding["agent"]["bytes"],
            "skill_sha256": ceo_binding["skill"]["sha256"],
            "skill_bytes": ceo_binding["skill"]["bytes"],
            "runtime_sha256": digest("global-brainstem-runtime"),
            "policy_sha256": digest("autobest-controller-policy"),
            "activation": "external-host-only",
            "grants_authority": False,
        },
        "hotload_slot": {
            "schema": "rapp-workspace-autobest/1-hotload-slot",
            "relative_paths": {
                "source": "source/agent.py",
                "target": "target/agent.py",
                "locked": "locked/agent.py",
            },
            "regular_files_only": True,
            "mode": "0600",
            "no_symlink": True,
            "no_hardlink": True,
            "no_overwrite": True,
            "captured_bytes_executed": True,
            "brainstem_source_modified": False,
            "daemon_created": False,
            "plugin_registered": False,
        },
        "intent_hash": record["lens"]["intent_hash"],
        "source_vector": [
            {
                **source_vector()[0],
                "dimension_rappid": source_rappid,
                "head": source_head,
            }
        ],
        "mapping": {
            "directions": ["source-to-target", "target-to-source"],
            "coverage_bps": record["coverage"]["basis_points"],
            "gaps": sorted(item["capability"] for item in record["gaps"]),
            "restrictions": sorted(
                key.replace("_", "-") for key, value in record["restrictions"].items() if value is False
            ),
            "bounds": {
                "max_input_bytes": 1048576,
                "max_output_bytes": 2097152,
                "max_depth": 48,
                "max_members": 4096,
                "max_seconds": 30,
                "max_model_calls": 0,
                "max_tool_calls": 0,
            },
            "loss_class": "unproven",
            "forward_complete": True,
            "reverse_complete": False,
        },
        "artifact_bundle": address(particle_hash(bundle)),
        "mutation_lineage": address(particle_hash(lineage)),
        "learning_trace": address(particle_hash(trace)),
        "n_lens_search": address(particle_hash(search)),
        "verification": {
            "candidate_tests": address("candidate-tests"),
            "host_tests": address("host-tests"),
            "canonical_tests": address("canonical-tests"),
            "controlled_mutants": address("controlled-mutants"),
            "replay_receipt": address("replay-receipt"),
            "privacy_receipt": address("privacy-receipt"),
            "authority_receipt": address("authority-receipt"),
        },
        "static_agent": {
            "package": address("bill-static-package"),
            "entrypoint": "agent.py",
            "sha256": hashlib.sha256(static_agent).hexdigest(),
            "bytes": len(static_agent),
            "compiler_sha256": digest("microsol-static-agent-1"),
            "runtime_sha256": digest("global-brainstem-runtime"),
            "generation_receipt": address(
                hashlib.sha256((FIXTURE / "static" / "generation-receipt.json").read_bytes()).hexdigest()
            ),
            "model_calls_per_operation": 0,
            "directions": ["source-to-target"],
            "deterministic": True,
            "coverage_bps": record["coverage"]["basis_points"],
        },
        "hive_checkpoint": {
            "registry_seq": 1,
            "registry_hash": digest("registry"),
            "declaration_frame_hash": digest("declaration"),
            "mother_head_frame_hash": digest("mother-head"),
            "catalog_hash": digest("catalog"),
        },
        "status": "locked",
        "repository_content_is_instructions": False,
        "host_constructs_rapp1_envelope": True,
        "grants_authority": False,
        "shared_brain": False,
        "private_state_transfer": "none",
        "key_transfer": "none",
    }


def assignment_fixture() -> dict[str, Any]:
    return {
        "schema": A.ASSIGNMENT_SCHEMA,
        "hive_rappid": HIVE,
        "world_id": WORLD,
        "created_utc": "2030-01-01T00:00:21.000Z",
        "root_compatibility": wave("compatibility-frame"),
        "assignment_id": "bill-read-shared",
        "revision": 0,
        "previous_assignment": None,
        "publisher_rappid": TARGET,
        "worker_dimension_rappid": DIMENSION,
        "work_group_id": "bill-read",
        "branch_id": "shared-trunk",
        "branch_kind": "shared-trunk",
        "operation": "assign",
        "workspace_assignment": wave("workspace-assignment"),
        "base_checkpoint": None,
        "source_vector": source_vector(),
        "constraint_relation": "equal-or-tighter",
        "request_only": True,
        "authorizes_execution": False,
        "grants_authority": False,
    }


def checkpoint_fixture() -> dict[str, Any]:
    return {
        "schema": A.CHECKPOINT_SCHEMA,
        "hive_rappid": HIVE,
        "world_id": WORLD,
        "created_utc": "2030-01-01T00:00:22.000Z",
        "root_compatibility": wave("compatibility-frame"),
        "assignment": wave("assignment-frame"),
        "previous_checkpoint": None,
        "worker_dimension_rappid": DIMENSION,
        "checkpoint_seq": 0,
        "observation_receipt": wave("observation-receipt"),
        "workspace_checkpoint_receipt": wave("checkpoint-receipt"),
        "status": "completed",
        "outputs": sorted(
            [address("mapped-open"), address("mapped-publish")],
            key=lambda value: (value["space"], value["hash"]),
        ),
        "source_vector": source_vector(),
        "grants_authority": False,
    }


def decision_fixture() -> dict[str, Any]:
    return {
        "schema": A.DECISION_SCHEMA,
        "hive_rappid": HIVE,
        "world_id": WORLD,
        "created_utc": "2030-01-01T00:00:23.000Z",
        "root_compatibility": wave("compatibility-frame"),
        "work_group_id": "bill-read",
        "autobest_evidence": wave("autobest-evidence"),
        "crossing_lens": wave("crossing-lens"),
        "parents": source_vector_pair(),
        "mode": "compose-compatible",
        "selected_checkpoints": sorted(
            [wave("checkpoint-a"), wave("checkpoint-b")],
            key=lambda value: (value["space"], value["hash"]),
        ),
        "rejected_checkpoints": [],
        "result_checkpoint": wave("checkpoint-cross"),
        "coverage_bps": 9000,
        "status": "verified",
        "authorizes_adoption": False,
        "grants_authority": False,
    }


def view_fixture() -> dict[str, Any]:
    return {
        "schema": A.VIEW_SCHEMA,
        "hive_rappid": HIVE,
        "world_id": WORLD,
        "created_utc": "2030-01-01T00:00:24.000Z",
        "compatibility": wave("compatibility-frame"),
        "view_kind": "chat",
        "basis": {
            "registry_seq": 1,
            "registry_hash": digest("registry"),
            "declaration_frame_hash": digest("declaration"),
            "mother_head_frame_hash": digest("mother-head"),
            "catalog_hash": digest("catalog"),
        },
        "source_vector": source_vector_pair(),
        "artifact": address("chat-view"),
        "topology": [
            {
                "id": "branch-a",
                "kind": "temporary-difference",
                "parent_ids": ["trunk"],
                "checkpoint_refs": [wave("checkpoint-a")],
                "decision_ref": None,
            },
            {
                "id": "branch-b",
                "kind": "temporary-difference",
                "parent_ids": ["trunk"],
                "checkpoint_refs": [wave("checkpoint-b")],
                "decision_ref": None,
            },
            {
                "id": "rejoin",
                "kind": "crossing-rejoin",
                "parent_ids": ["branch-a", "branch-b"],
                "checkpoint_refs": [wave("checkpoint-cross")],
                "decision_ref": wave("decision-frame"),
            },
            {
                "id": "trunk",
                "kind": "shared-trunk",
                "parent_ids": [],
                "checkpoint_refs": [wave("checkpoint-root")],
                "decision_ref": None,
            },
        ],
        "omissions": ["membership", "post-write"],
        "rebuildable": True,
        "authoritative": False,
        "grants_authority": False,
    }


def exhaust_fixture(compatibility_hash: str) -> dict[str, Any]:
    return {
        "schema": A.EXHAUST_SCHEMA,
        "hive_rappid": HIVE,
        "world_id": WORLD,
        "created_utc": "2030-01-01T00:00:30.000Z",
        "compatibility": {"space": "rapp/1:wave", "hash": compatibility_hash},
        "source_head": source_vector()[0]["head"],
        "target_head": None,
        "direction": "source-to-target",
        "operation": "unknown-operation",
        "input": address("unknown-input"),
        "output": None,
        "failure_code": "mapping-exhaust",
        "satisfied_coverage_bps": 3076,
        "missing_capabilities": ["unknown-operation"],
        "loss_class": "unknown",
        "restrictions": ["no-authority", "no-private-state"],
        "bounds_consumed": {
            "max_input_bytes": 128,
            "max_output_bytes": 0,
            "max_depth": 1,
            "max_members": 1,
            "max_seconds": 1,
            "max_model_calls": 0,
            "max_tool_calls": 0,
        },
        "retryable": True,
        "privacy_safe": True,
        "grants_authority": False,
    }


def offer_fixture() -> dict[str, Any]:
    return {
        "schema": A.OFFER_SCHEMA,
        "offer_rappid": rid("example", "mutation-offer", "7"),
        "created_utc": "2030-01-01T00:00:50.000Z",
        "source_organization": DIMENSION,
        "target_organization": TARGET,
        "source_parents": [wave("source-parent")],
        "successor_frame": wave("successor-frame"),
        "successor_bundle": address("successor-bundle", "rapp/1:egg-manifest"),
        "mutation_lineage": address("successor-lineage"),
        "compatibility": wave("compatibility-frame"),
        "static_agent": address("static-agent-package", "rapp/1:egg-manifest"),
        "selected_traits": ["schema-learning", "strict-json"],
        "omitted_traits": ["ambient-azure"],
        "tests": {
            "candidate_tests": address("candidate-tests"),
            "host_tests": address("host-tests"),
            "canonical_tests": address("canonical-tests"),
            "controlled_mutants": address("controlled-mutants"),
            "replay_receipt": address("replay-receipt"),
            "privacy_receipt": address("privacy-receipt"),
            "authority_receipt": address("authority-receipt"),
        },
        "pr_projection": {
            "repository": "https://github.com/example/source",
            "base_commit": {"algorithm": "sha1", "oid": "1" * 40},
            "head_commit": {"algorithm": "sha1", "oid": "2" * 40},
            "base_inventory_hash": digest("base-inventory"),
            "head_inventory_hash": digest("head-inventory"),
            "provider_pr_id": "pr-1",
            "locator": "https://github.com/example/source/pull/1",
            "projection_receipt": address("pr-projection"),
        },
        "grants_authority": False,
    }


def catalog_fixture(compatibility_hash: str, static_hash: str) -> dict[str, Any]:
    return {
        "schema": A.CATALOG_SCHEMA,
        "hive_rappid": HIVE,
        "world_id": WORLD,
        "created_utc": "2030-01-01T00:00:40.000Z",
        "base_catalog_hash": digest("base-catalog"),
        "entries": [
            {
                "id": "softwarecoellc-vteam-hive-microsol-project-1",
                "version": 1,
                "status": "locked",
                "source_profile": "microsol-project/1",
                "target_profile": "microsol-repository-private-hive/1",
                "compatibility": {"space": "rapp/1:wave", "hash": compatibility_hash},
                "package": address("bill-static-package"),
                "static_agent_sha256": static_hash,
                "coverage_bps": 3076,
                "gaps": [
                    "board",
                    "canonical-head-pointer",
                    "encryption",
                    "hosted-delivery",
                    "membership-activation",
                    "native-hive-profile",
                    "post-write",
                    "registry-admission",
                    "revocation-key-rotation",
                ],
            }
        ],
        "grants_authority": False,
    }


class SigningFixture:
    def __init__(self) -> None:
        self.private = Ed25519PrivateKey.from_private_bytes(bytes(range(1, 33)))
        self.spki = self.private.public_key().public_bytes(
            serialization.Encoding.DER,
            serialization.PublicFormat.SubjectPublicKeyInfo,
        )
        tail = R.Hb("rapp/1:rappid", self.spki)
        self.rappid = f"rappid:@fixture/hive-autobest:{tail}"
        self.stream = self.rappid + ":compatibility"

    def sign(self, value: dict[str, Any]) -> str:
        header = {"alg": "EdDSA", "b64": False, "crit": ["b64"], "kid": self.rappid}
        protected = base64.urlsafe_b64encode(R.canonical(header).encode()).rstrip(b"=").decode()
        signature = self.private.sign(
            protected.encode("ascii") + b"." + R.canonical(value).encode("utf-8")
        )
        encoded = base64.urlsafe_b64encode(signature).rstrip(b"=").decode()
        return protected + ".." + encoded

    def frame(self, payload: dict[str, Any]) -> dict[str, Any]:
        frame = R.build_frame(
            "hive-autobest.compatibility",
            self.stream,
            0,
            payload["created_utc"],
            payload,
            prev=None,
            sig=None,
        )
        frame["sig"] = self.sign({key: value for key, value in frame.items() if key != "sig"})
        return frame

    def verify(self, unsigned: dict, signature: str):
        return R.verify_detached_jws(unsigned, signature, self.spki, self.rappid)


def run_agent(path: Path, request: dict[str, Any]) -> dict[str, Any]:
    result = subprocess.run(
        [sys.executable, "-B", str(path)],
        input=json.dumps(request, separators=(",", ":"), sort_keys=True).encode(),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
        timeout=30,
    )
    if result.returncode != 0:
        raise AssertionError(result.stderr.decode() or result.stdout.decode())
    return json.loads(result.stdout)


class AutoBestConformance(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.lineage = lineage_fixture()
        cls.trace = trace_fixture()
        cls.search = search_fixture()
        cls.bundle = bundle_fixture(cls.lineage)
        cls.compatibility = compatibility_fixture(cls.bundle, cls.lineage, cls.trace, cls.search)

    def test_schema_source_is_exact_and_valid(self) -> None:
        Draft202012Validator.check_schema(A.SCHEMA)
        self.assertEqual(A.SCHEMA, build_schema())

    def test_bill_fixture_exact_bytes_and_signed_package(self) -> None:
        result = A.validate_bill_fixture(FIXTURE)
        self.assertEqual(result["verified_frames"], 2)
        self.assertEqual(result["verified_artifacts"], 9)
        self.assertEqual(
            result["static_agent_sha256"],
            "46c981ac9660f24a2e02809ce1957e28b3c9497f85cb60a3f4ff4b06c0455a18",
        )

    def test_generic_ceo_exact_bytes_and_external_binding(self) -> None:
        result = A.validate_ceo_fixture(CEO_FIXTURE)
        self.assertEqual(
            result["agent_sha256"],
            "827f637c024e3fa1229148e5dcd78230a84ea3214283f899d22603741350f23c",
        )
        self.assertEqual(
            result["skill_sha256"],
            "5f8bd5b3c48858329f87ae3812dbc30ee604cb664985dc3d42a79e69d8bdfda8",
        )
        self.assertEqual(
            result["profile_artifact_hash"],
            "cadfa00974630cee1ddc614df7790815577e14bc90f035e0e826dffa7a225271",
        )
        self.assertEqual(
            result["binding_hash"],
            "cdba8330dcfad77e9e2804ab1bff573a405424ab94bfd2a512c7a2ac3784cf40",
        )
        specification = importlib.util.spec_from_file_location(
            "rapp_hive_autobest_ceo_fixture",
            CEO_FIXTURE / "agent.py",
        )
        self.assertIsNotNone(specification)
        self.assertIsNotNone(specification.loader)
        module = importlib.util.module_from_spec(specification)
        specification.loader.exec_module(module)
        binding = module.bind_implementation_sha256(result["agent_sha256"])
        self.assertEqual(binding["implementation_sha256"], result["agent_sha256"])
        self.assertEqual(binding["capability_home"], "specific-protocol-and-seed-profiles")
        self.assertFalse(binding["authority_from_presence"])
        profile = module.profile_config("microsol-ceo")
        self.assertEqual(profile["name"], "microsol-ceo")
        self.assertTrue(profile["host_activation_required"])
        self.assertFalse(profile["authority_from_profile"])
        self.assertTrue(module.__manifest__["deterministic"])
        self.assertTrue(module.__manifest__["inert"])
        self.assertFalse(module.__manifest__["authority"])
        self.assertEqual(module.__manifest__["normal_traffic_model_calls"], 0)

    def test_generic_ceo_pin_and_package_substitution_refuse(self) -> None:
        binding = json.loads((CEO_FIXTURE / "binding.json").read_text())
        value = copy.deepcopy(binding)
        value["agent"]["sha256"] = digest("substituted-agent")
        with self.assertRaises(ValueError):
            A.validate(value)
        value = copy.deepcopy(binding)
        value["profile_artifact"]["hash"] = digest("substituted-artifact")
        with self.assertRaises(ValueError):
            A.validate(value)
        original = (CEO_FIXTURE / "agent.py").read_bytes()
        mutated = original[:-1] + bytes([original[-1] ^ 1])
        self.assertNotEqual(
            hashlib.sha256(mutated).hexdigest(),
            binding["agent"]["sha256"],
        )
        compatibility = copy.deepcopy(self.compatibility)
        compatibility["autobest_controller"]["agent_sha256"] = digest("wrong-controller")
        with self.assertRaises(ValueError):
            A.validate(compatibility)

    def test_all_profile_records_validate(self) -> None:
        records = [
            self.lineage,
            self.trace,
            self.search,
            self.bundle,
            self.compatibility,
            assignment_fixture(),
            checkpoint_fixture(),
            decision_fixture(),
            view_fixture(),
            exhaust_fixture(digest("compatibility-wave")),
            offer_fixture(),
            catalog_fixture(
                digest("compatibility-wave"),
                self.compatibility["static_agent"]["sha256"],
            ),
        ]
        for record in records:
            with self.subTest(schema=record["schema"]):
                self.assertEqual(A.validate(record), particle_hash(record))

    def test_double_hotload_fixture_and_static_agent(self) -> None:
        legacy = json.loads((FIXTURE / "static" / "compatibility-frame.json").read_text())
        record = legacy["payload"]["record"]
        payload = {
            "authority": False,
            "inventory": {
                "schema": "microsol-emitted-inventory/1",
                "role": "evidence",
                "authority": False,
                "artifacts": [],
            },
            "operation": "open",
            "profile": "microsol-project/1",
            "project": "wild-hive",
            "record": {"schema": "wild-hive/1", "authority": False},
            "request_hash": digest("request"),
            "request_id": "wild-hive-open-0",
            "sequence": 0,
        }
        frame = R.build_frame(
            "memory.save",
            record["source"]["stream_id"],
            0,
            "2030-01-01T00:00:00.000Z",
            payload,
            prev=None,
            sig=None,
        )
        first = run_agent(
            FIXTURE / "source-agent.py",
            {"direction": "source-to-target", "value": frame},
        )
        self.assertTrue(first["ok"])
        second = run_agent(
            FIXTURE / "target-finalizer.py",
            {
                "candidate": first["result"],
                "context": {
                    "compatibility_intent_hash": record["lens"]["intent_hash"],
                    "handshake_id": record["handshake"]["id"],
                    "handshake_sha256": record["handshake"]["sha256"],
                    "source_agent_sha256": record["lens"]["source_agent"]["sha256"],
                    "target_profile": record["target"]["profile"],
                },
            },
        )
        self.assertTrue(second["ok"])
        self.assertFalse(second["result"]["authority"])
        static = run_agent(
            FIXTURE / "static" / "agent.py",
            {"direction": "source-to-target", "value": frame},
        )
        self.assertTrue(static["ok"])
        self.assertEqual(static["result"]["model_calls"], 0)
        self.assertEqual(static["result"]["compatibility"]["frame_hash"], legacy["frame_hash"])

    def test_signed_compatibility_frame_uses_unchanged_rapp1_envelope(self) -> None:
        fixture = SigningFixture()
        payload = copy.deepcopy(self.compatibility)
        payload["compatibility_rappid"] = fixture.rappid
        frame = fixture.frame(payload)
        accepted = A.authorize_frame(
            frame,
            head=None,
            stream_id=fixture.stream,
            registered_kinds=set(A.KIND_SCHEMAS),
            signature_verifier=fixture.verify,
            authorization_verifier=lambda _frame, _purpose: True,
        )
        self.assertEqual(accepted, payload)
        self.assertEqual(set(frame), R.FRAME_KEYS)

    def test_partial_unknown_capabilities_do_not_block_verified_read(self) -> None:
        self.assertEqual(self.compatibility["source"]["capabilities"][0]["status"], "verified")
        self.assertTrue(any(item["status"] == "unavailable" for item in self.compatibility["source"]["capabilities"]))
        A.validate(self.compatibility)

    def test_initial_compatibility_cannot_smuggle_exhaust(self) -> None:
        value = copy.deepcopy(self.compatibility)
        value["trigger"]["exhaust"] = wave("invented-exhaust")
        with self.assertRaisesRegex(ValueError, "invalid initial trigger"):
            A.validate(value)

    def test_static_agent_cannot_claim_more_coverage_or_directions(self) -> None:
        value = copy.deepcopy(self.compatibility)
        value["static_agent"]["coverage_bps"] = value["mapping"]["coverage_bps"] + 1
        with self.assertRaisesRegex(ValueError, "static coverage"):
            A.validate(value)
        value = copy.deepcopy(self.compatibility)
        value["mapping"]["directions"] = ["source-to-target"]
        value["static_agent"]["directions"] = ["source-to-target", "target-to-source"]
        with self.assertRaisesRegex(ValueError, "static directions"):
            A.validate(value)

    def test_lossless_lineage_requires_inverse_reconstruction(self) -> None:
        value = copy.deepcopy(self.lineage)
        value["reconstruction"]["receipt"] = None
        with self.assertRaisesRegex(ValueError, "reconstruction proof"):
            A.validate(value)
        value = copy.deepcopy(self.lineage)
        value["reverse"][0]["inverse_method"] = "unavailable"
        with self.assertRaisesRegex(ValueError, "unavailable inverse"):
            A.validate(value)

    def test_lossless_reconstruction_materializes_exact_ancestor(self) -> None:
        source_files = {
            "agents/old.py": b"old-agent",
            "schemas/old.json": b"old-schema",
        }
        successor_files = {
            "agent.py": b"new-agent",
            "schemas/current.json": b"new-schema",
            "tests/mutation.json": b"new-tests",
        }
        retained_deltas = {
            "agents/old.py": b"old-agent",
            "schemas/old.json": b"old-schema",
        }
        reconstructed = {}
        reverse_by_path = {
            item["successor"]["path"]: item for item in self.lineage["reverse"]
        }
        for item in self.lineage["forward"]:
            source = item["source"]
            if item["disposition"] == "retained":
                candidate_path = item["successors"][0]["path"]
                reconstructed[source["path"]] = successor_files[candidate_path]
            else:
                reconstructed[source["path"]] = retained_deltas[source["path"]]
        self.assertEqual(reconstructed, source_files)
        self.assertEqual(
            {
                path: hashlib.sha256(data).hexdigest()
                for path, data in sorted(reconstructed.items())
            },
            {
                path: hashlib.sha256(data).hexdigest()
                for path, data in sorted(source_files.items())
            },
        )
        self.assertEqual(set(reverse_by_path), set(successor_files))

    def test_lossy_lineage_must_expose_loss(self) -> None:
        value = copy.deepcopy(self.lineage)
        value["loss_class"] = "declared-lossy"
        with self.assertRaisesRegex(ValueError, "must expose the loss"):
            A.validate(value)

    def test_trace_blocks_summary_drift_and_forged_user_authority(self) -> None:
        value = copy.deepcopy(self.trace)
        value["events"][1]["authority_class"] = "user-decision"
        value["events"][1]["event_hash"] = particle_hash(
            {key: item for key, item in value["events"][1].items() if key != "event_hash"}
        )
        with self.assertRaisesRegex(ValueError, "assistant proposal"):
            A.validate(value)
        value = copy.deepcopy(self.trace)
        value["correction_coverage_bps"] = 9999
        with self.assertRaisesRegex(ValueError, "every correction"):
            A.validate(value)

    def test_n_lens_bounds_prevent_cross_product_runaway(self) -> None:
        value = copy.deepcopy(self.search)
        value["bounds"]["max_lenses"] = 1
        with self.assertRaisesRegex(ValueError, "lens bound"):
            A.validate(value)
        value = copy.deepcopy(self.search)
        value["bounds"]["max_cross_size"] = 2
        value["crosses"][0]["candidate_ids"].append("candidate-cross")
        with self.assertRaisesRegex(ValueError, "cross-size"):
            A.validate(value)

    def test_unresolved_search_cannot_choose_silent_winner(self) -> None:
        value = copy.deepcopy(self.search)
        value["selection"]["mode"] = "unresolved"
        with self.assertRaisesRegex(ValueError, "cannot silently choose"):
            A.validate(value)

    def test_catalog_and_offer_never_grant_authority(self) -> None:
        catalog = catalog_fixture(
            digest("compatibility-wave"),
            self.compatibility["static_agent"]["sha256"],
        )
        catalog["grants_authority"] = True
        with self.assertRaises(ValueError):
            A.validate(catalog)
        offer = offer_fixture()
        offer["grants_authority"] = True
        with self.assertRaises(ValueError):
            A.validate(offer)

    def test_assignment_mutations_cannot_widen_or_self_authorize(self) -> None:
        value = assignment_fixture()
        value["constraint_relation"] = "wider"
        with self.assertRaises(ValueError):
            A.validate(value)
        value = assignment_fixture()
        value["operation"] = "tighten"
        with self.assertRaisesRegex(ValueError, "mutation requires predecessor"):
            A.validate(value)

    def test_crossing_decision_and_view_remain_non_authoritative(self) -> None:
        decision = decision_fixture()
        decision["crossing_lens"] = None
        with self.assertRaisesRegex(ValueError, "requires Crossing Lens"):
            A.validate(decision)
        view = view_fixture()
        view["topology"][0]["parent_ids"] = ["missing"]
        with self.assertRaisesRegex(ValueError, "unknown parent"):
            A.validate(view)

    def test_evolution_requires_independent_verification(self) -> None:
        verifier = agent_pin("verifier", "independent-verifier")
        evolution = {
            "schema": A.EVOLUTION_SCHEMA,
            "level": "handshake",
            "created_utc": "2030-01-01T00:01:00.000Z",
            "parents": [wave("compatibility-parent")],
            "candidate": address("compatibility-successor"),
            "generator": agent_pin("source-lens", "generator"),
            "scenario_corpus": {
                "manifest": address("scenario-corpus"),
                "case_count": 12,
                "bytes": 4096,
                "private": True,
            },
            "hidden_holdout": {
                "manifest": address("hidden-holdout"),
                "case_count": 4,
                "bytes": 1024,
                "private": True,
            },
            "controlled_mutants": address("mutants"),
            "candidate_tests": address("candidate-tests"),
            "independent_tests": address("independent-tests"),
            "verifier": verifier,
            "canary": {
                "scope": "bounded-read",
                "candidate": address("canary-candidate"),
                "result": address("canary-result"),
                "rollback": address("canary-rollback"),
                "passed": True,
            },
            "rollback": address("rollback"),
            "promotion_target": "handshake-catalog",
            "status": "verified",
            "adoption_authorized": False,
        }
        A.validate(evolution)
        value = copy.deepcopy(evolution)
        value["verifier"] = copy.deepcopy(value["generator"])
        value["verifier"]["role"] = "verifier"
        with self.assertRaisesRegex(ValueError, "generator and independent verifier"):
            A.validate(value)
        value = copy.deepcopy(evolution)
        value["independent_tests"] = copy.deepcopy(value["candidate_tests"])
        with self.assertRaisesRegex(ValueError, "cannot self-certify"):
            A.validate(value)

    def test_extra_properties_and_authority_shaped_data_refuse(self) -> None:
        value = copy.deepcopy(self.compatibility)
        value["owner_approved"] = True
        with self.assertRaises(ValueError):
            A.validate(value)
        value = copy.deepcopy(self.compatibility)
        value["grants_authority"] = True
        with self.assertRaises(ValueError):
            A.validate(value)

    def test_tampered_signed_frame_refuses(self) -> None:
        fixture = SigningFixture()
        payload = copy.deepcopy(self.compatibility)
        payload["compatibility_rappid"] = fixture.rappid
        frame = fixture.frame(payload)
        frame["payload"]["intent_hash"] = digest("tampered")
        with self.assertRaisesRegex(ValueError, "RAPP frame refusal"):
            A.authorize_frame(
                frame,
                head=None,
                stream_id=fixture.stream,
                registered_kinds=set(A.KIND_SCHEMAS),
                signature_verifier=fixture.verify,
                authorization_verifier=lambda _frame, _purpose: True,
            )


def run() -> unittest.result.TestResult:
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(AutoBestConformance)
    return unittest.TextTestRunner(verbosity=2).run(suite)


if __name__ == "__main__":
    result = run()
    raise SystemExit(0 if result.wasSuccessful() else 1)
