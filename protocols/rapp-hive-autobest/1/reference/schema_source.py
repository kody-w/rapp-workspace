#!/usr/bin/env python3
"""Generate the closed Draft 2020-12 schemas for rapp-hive-autobest/1."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schema.json"
UINT53_MAX = 2**53 - 1


def ref(name: str) -> dict:
    return {"$ref": f"#/$defs/{name}"}


def array(items: dict, *, minimum: int = 0, maximum: int | None = None) -> dict:
    value = {
        "type": "array",
        "items": items,
        "minItems": minimum,
        "uniqueItems": True,
    }
    if maximum is not None:
        value["maxItems"] = maximum
    return value


def nullable(value: dict) -> dict:
    return {"oneOf": [value, {"type": "null"}]}


def closed(properties: dict, required: list[str] | None = None) -> dict:
    return {
        "type": "object",
        "additionalProperties": False,
        "properties": properties,
        "required": required or list(properties),
    }


def const(value) -> dict:
    return {"const": value}


def enum(*values: str) -> dict:
    return {"enum": list(values)}


def build_schema() -> dict:
    hash_value = {
        "type": "string",
        "pattern": "^[0-9a-f]{64}$(?![\\s\\S])",
    }
    label = {
        "type": "string",
        "minLength": 1,
        "maxLength": 128,
        "pattern": "^[a-z0-9](?:[a-z0-9._-]{0,126}[a-z0-9])?$(?![\\s\\S])",
    }
    text = {
        "type": "string",
        "minLength": 1,
        "maxLength": 512,
        "pattern": "^[^\\u0000-\\u001f\\u007f]*$(?![\\s\\S])",
    }
    relative_path = {
        "type": "string",
        "minLength": 1,
        "maxLength": 1024,
        "pattern": "^(?!/)(?!.*(?:^|/)\\.\\.?(?:/|$))[^/]+(?:/[^/]+)*$(?![\\s\\S])",
        "allOf": [
            {"pattern": "^[^\\\\:\\u0000-\\u001f\\u007f]+$(?![\\s\\S])"},
            {"not": {"pattern": "(?:^|/)[^/]*[ .](?:/|$)"}},
        ],
    }
    rappid = {
        "type": "string",
        "pattern": (
            "^rappid:@(?=[a-z0-9-]{1,39}/)[a-z0-9]+(?:-[a-z0-9]+)*/"
            "(?=[a-z0-9-]{1,100}:)[a-z0-9]+(?:-[a-z0-9]+)*:"
            "[0-9a-f]{64}(?::[a-z0-9]+(?:-[a-z0-9]+)*)?$(?![\\s\\S])"
        ),
    }
    utc = {
        "type": "string",
        "pattern": (
            "^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:"
            "[0-9]{2}:[0-9]{2}\\.[0-9]{3}Z$(?![\\s\\S])"
        ),
        "format": "date-time",
    }
    uint53 = {"type": "integer", "minimum": 0, "maximum": UINT53_MAX}
    bps = {"type": "integer", "minimum": 0, "maximum": 10000}

    address = closed(
        {
            "space": enum("rapp/1:particle", "rapp/1:wave", "rapp/1:egg-manifest"),
            "hash": ref("hash"),
        }
    )
    wave_address = closed({"space": const("rapp/1:wave"), "hash": ref("hash")})
    frame_summary = closed(
        {
            "stream_id": {"type": "string", "minLength": 1, "maxLength": 512},
            "seq": ref("uint53"),
            "utc": ref("utc"),
            "payload_hash": ref("hash"),
            "frame_hash": ref("hash"),
        }
    )
    commit_pin = closed(
        {
            "algorithm": enum("sha1", "sha256"),
            "oid": {
                "type": "string",
                "pattern": "^(?:[0-9a-f]{40}|[0-9a-f]{64})$(?![\\s\\S])",
            },
        }
    )
    repository_pin = closed(
        {
            "repository": {"type": "string", "minLength": 1, "maxLength": 2048},
            "branch": {"type": "string", "minLength": 1, "maxLength": 256},
            "commit": ref("commitPin"),
            "inventory_hash": ref("hash"),
            "file_count": ref("uint53"),
            "total_bytes": ref("uint53"),
        }
    )
    pinned_value = closed(
        {
            "status": enum("verified", "unavailable", "not-applicable"),
            "value": nullable(ref("hash")),
        }
    )
    capability = closed(
        {
            "id": ref("label"),
            "status": enum(
                "verified",
                "partial",
                "unproven",
                "unavailable",
                "revoked",
            ),
            "method": enum(
                "native-protocol",
                "declared-descriptor",
                "signed-stream-inference",
                "deterministic-static-repository-compiler",
                "brainstem-translation-candidate",
            ),
            "coverage_bps": ref("bps"),
            "evidence": array(ref("address"), maximum=64),
            "reason_code": ref("label"),
        }
    )
    endpoint = closed(
        {
            "endpoint_rappid": ref("rappid"),
            "profile": {"type": "string", "minLength": 1, "maxLength": 128},
            "profile_pin": ref("pinnedValue"),
            "head_status": enum("verified", "unavailable", "not-applicable"),
            "head": nullable(ref("frameSummary")),
            "snapshot": nullable(ref("repositoryPin")),
            "capabilities": array(ref("capability"), minimum=1, maximum=256),
        }
    )
    agent_pin = closed(
        {
            "role": enum("source-lens", "target-finalizer", "static-agent", "verifier"),
            "artifact": ref("address"),
            "sha256": ref("hash"),
            "bytes": ref("uint53"),
            "runtime_sha256": ref("hash"),
            "policy_sha256": ref("hash"),
        }
    )
    slot_contract = closed(
        {
            "schema": const("rapp-workspace-autobest/1-hotload-slot"),
            "relative_paths": closed(
                {
                    "source": const("source/agent.py"),
                    "target": const("target/agent.py"),
                    "locked": const("locked/agent.py"),
                }
            ),
            "regular_files_only": const(True),
            "mode": const("0600"),
            "no_symlink": const(True),
            "no_hardlink": const(True),
            "no_overwrite": const(True),
            "captured_bytes_executed": const(True),
            "brainstem_source_modified": const(False),
            "daemon_created": const(False),
            "plugin_registered": const(False),
        }
    )
    runtime_bounds = closed(
        {
            "max_input_bytes": ref("uint53"),
            "max_output_bytes": ref("uint53"),
            "max_depth": ref("uint53"),
            "max_members": ref("uint53"),
            "max_seconds": ref("uint53"),
            "max_model_calls": ref("uint53"),
            "max_tool_calls": ref("uint53"),
        }
    )
    source_vector_entry = closed(
        {
            "dimension_rappid": ref("rappid"),
            "work_group_id": ref("label"),
            "branch_id": ref("label"),
            "branch_kind": enum(
                "shared-trunk",
                "temporary-difference",
                "crossing-parent",
                "crossing-output",
            ),
            "head": ref("frameSummary"),
            "workspace_binding": ref("waveAddress"),
            "observation_receipt": ref("waveAddress"),
            "checkpoint_receipt": ref("waveAddress"),
        }
    )
    hive_checkpoint = closed(
        {
            "registry_seq": ref("uint53"),
            "registry_hash": ref("hash"),
            "declaration_frame_hash": ref("hash"),
            "mother_head_frame_hash": ref("hash"),
            "catalog_hash": ref("hash"),
        }
    )
    verification_set = closed(
        {
            "candidate_tests": ref("address"),
            "host_tests": ref("address"),
            "canonical_tests": ref("address"),
            "controlled_mutants": ref("address"),
            "replay_receipt": ref("address"),
            "privacy_receipt": ref("address"),
            "authority_receipt": ref("address"),
        }
    )
    mapping_contract = closed(
        {
            "directions": array(
                enum("source-to-target", "target-to-source"),
                minimum=1,
                maximum=2,
            ),
            "coverage_bps": ref("bps"),
            "gaps": array(ref("label"), maximum=256),
            "restrictions": array(ref("label"), maximum=256),
            "bounds": ref("runtimeBounds"),
            "loss_class": enum("exact-lossless", "declared-lossy", "unproven"),
            "forward_complete": {"type": "boolean"},
            "reverse_complete": {"type": "boolean"},
        }
    )
    static_agent = closed(
        {
            "package": ref("address"),
            "entrypoint": const("agent.py"),
            "sha256": ref("hash"),
            "bytes": ref("uint53"),
            "compiler_sha256": ref("hash"),
            "runtime_sha256": ref("hash"),
            "generation_receipt": ref("address"),
            "model_calls_per_operation": const(0),
            "directions": array(
                enum("source-to-target", "target-to-source"),
                minimum=1,
                maximum=2,
            ),
            "deterministic": const(True),
            "coverage_bps": ref("bps"),
        }
    )
    trigger = closed(
        {
            "kind": enum(
                "initial-handshake",
                "typed-exhaust",
                "requested-mutation",
                "scheduled-rehearsal",
            ),
            "exhaust": nullable(ref("waveAddress")),
        }
    )
    file_head = closed(
        {
            "path": ref("relativePath"),
            "mode": enum("100644", "100755"),
            "bytes": ref("uint53"),
            "sha256": ref("hash"),
            "content": ref("address"),
        }
    )
    trait = closed(
        {
            "id": ref("label"),
            "status": enum("retained", "replaced", "moved", "removed", "new", "omitted"),
            "source_refs": array(ref("address"), maximum=256),
            "successor_refs": array(ref("address"), maximum=256),
            "reason_code": ref("label"),
        }
    )
    generation = closed(
        {
            "frame": ref("waveAddress"),
            "repository": nullable(ref("repositoryPin")),
            "inventory_hash": ref("hash"),
            "file_count": ref("uint53"),
            "total_bytes": ref("uint53"),
        }
    )
    forward_mutation = closed(
        {
            "source": ref("fileHead"),
            "disposition": enum(
                "retained",
                "replaced",
                "moved",
                "moved-and-replaced",
                "removed",
                "split",
                "composed",
            ),
            "successors": array(ref("fileHead"), maximum=256),
            "receipt": ref("address"),
        }
    )
    reverse_mutation = closed(
        {
            "successor": ref("fileHead"),
            "origin": enum("inherited", "derived", "new", "split", "composed"),
            "sources": array(ref("fileHead"), maximum=256),
            "inverse_method": enum(
                "identity",
                "path-restore",
                "retained-delta",
                "inverse-program",
                "unavailable",
            ),
            "inverse_artifacts": array(ref("address"), maximum=256),
        }
    )
    reconstruction = closed(
        {
            "required": {"type": "boolean"},
            "implementation": nullable(ref("address")),
            "retained_deltas": array(ref("address"), maximum=512),
            "receipt": nullable(ref("address")),
        }
    )
    trace_event = closed(
        {
            "index": ref("uint53"),
            "previous_event_hash": nullable(ref("hash")),
            "event_type": enum(
                "user-intent",
                "assistant-proposal",
                "user-correction",
                "tool-result",
                "agent-result",
                "measured-failure",
                "assumption-superseded",
                "successor-invariant",
            ),
            "actor_class": enum("user", "assistant", "tool", "agent", "host"),
            "authority_class": enum(
                "observed-user-input",
                "user-decision",
                "proposal-only",
                "measured-evidence",
                "host-validation",
            ),
            "source_refs": array(ref("address"), maximum=128),
            "result_code": ref("label"),
            "evidence_refs": array(ref("address"), maximum=128),
            "supersedes_event_ids": array(ref("uint53"), maximum=128),
            "successor_invariant_ids": array(ref("label"), maximum=128),
            "event_hash": ref("hash"),
        }
    )
    search_bounds = closed(
        {
            "max_lenses": {"type": "integer", "minimum": 1, "maximum": 32},
            "max_candidates": {"type": "integer", "minimum": 1, "maximum": 128},
            "max_cross_size": {"type": "integer", "minimum": 2, "maximum": 8},
            "max_depth": {"type": "integer", "minimum": 1, "maximum": 8},
            "max_rounds": {"type": "integer", "minimum": 1, "maximum": 16},
            "max_evaluations": {"type": "integer", "minimum": 1, "maximum": 4096},
            "max_generated_bytes": ref("uint53"),
            "max_tool_calls": ref("uint53"),
            "beam_width": {"type": "integer", "minimum": 1, "maximum": 32},
            "pareto_limit": {"type": "integer", "minimum": 1, "maximum": 32},
            "reserved_stop_frames": {"type": "integer", "minimum": 1, "maximum": 16},
        }
    )
    lens_descriptor = closed(
        {
            "id": ref("label"),
            "agent": ref("agentPin"),
            "prompt_sha256": ref("hash"),
            "policy_sha256": ref("hash"),
            "source_vector": array(ref("sourceVectorEntry"), minimum=1, maximum=256),
            "budget_units": ref("uint53"),
        }
    )
    candidate = closed(
        {
            "id": ref("label"),
            "lens_id": ref("label"),
            "kind": enum("complete-successor", "trait-delta"),
            "artifact": ref("address"),
            "trait_ids": array(ref("label"), maximum=256),
            "parents": array(ref("label"), maximum=256),
            "scenario_evidence": ref("address"),
            "coverage_bps": ref("bps"),
            "unknowns": array(ref("label"), maximum=256),
        }
    )
    cross = closed(
        {
            "id": ref("label"),
            "candidate_ids": array(ref("label"), minimum=2, maximum=8),
            "trait_ids": array(ref("label"), maximum=256),
            "output_candidate_id": ref("label"),
            "crossing_lens": ref("waveAddress"),
        }
    )
    corpus = closed(
        {
            "manifest": ref("address"),
            "case_count": ref("uint53"),
            "bytes": ref("uint53"),
            "private": {"type": "boolean"},
        }
    )
    canary = closed(
        {
            "scope": ref("label"),
            "candidate": ref("address"),
            "result": ref("address"),
            "rollback": ref("address"),
            "passed": {"type": "boolean"},
        }
    )
    assignment = closed(
        {
            "schema": const("rapp-hive-autobest/1-assignment"),
            "hive_rappid": ref("rappid"),
            "world_id": ref("label"),
            "created_utc": ref("utc"),
            "root_compatibility": ref("waveAddress"),
            "assignment_id": ref("label"),
            "revision": ref("uint53"),
            "previous_assignment": nullable(ref("waveAddress")),
            "publisher_rappid": ref("rappid"),
            "worker_dimension_rappid": ref("rappid"),
            "work_group_id": ref("label"),
            "branch_id": ref("label"),
            "branch_kind": enum("shared-trunk", "temporary-difference", "crossing-output"),
            "operation": enum("assign", "tighten", "pause", "resume", "cancel", "complete", "prune"),
            "workspace_assignment": ref("waveAddress"),
            "base_checkpoint": nullable(ref("waveAddress")),
            "source_vector": array(ref("sourceVectorEntry"), minimum=1, maximum=256),
            "constraint_relation": const("equal-or-tighter"),
            "request_only": const(True),
            "authorizes_execution": const(False),
            "grants_authority": const(False),
        }
    )
    checkpoint = closed(
        {
            "schema": const("rapp-hive-autobest/1-checkpoint"),
            "hive_rappid": ref("rappid"),
            "world_id": ref("label"),
            "created_utc": ref("utc"),
            "root_compatibility": ref("waveAddress"),
            "assignment": ref("waveAddress"),
            "previous_checkpoint": nullable(ref("waveAddress")),
            "worker_dimension_rappid": ref("rappid"),
            "checkpoint_seq": ref("uint53"),
            "observation_receipt": ref("waveAddress"),
            "workspace_checkpoint_receipt": ref("waveAddress"),
            "status": enum("running", "completed", "failed", "cancelled", "timed-out", "pruned"),
            "outputs": array(ref("address"), maximum=4096),
            "source_vector": array(ref("sourceVectorEntry"), minimum=1, maximum=256),
            "grants_authority": const(False),
        }
    )
    decision = closed(
        {
            "schema": const("rapp-hive-autobest/1-decision"),
            "hive_rappid": ref("rappid"),
            "world_id": ref("label"),
            "created_utc": ref("utc"),
            "root_compatibility": ref("waveAddress"),
            "work_group_id": ref("label"),
            "autobest_evidence": ref("waveAddress"),
            "crossing_lens": nullable(ref("waveAddress")),
            "parents": array(ref("sourceVectorEntry"), minimum=1, maximum=256),
            "mode": enum("select-one", "compose-compatible", "retain-parallel", "unresolved", "prune-all"),
            "selected_checkpoints": array(ref("waveAddress"), maximum=256),
            "rejected_checkpoints": array(ref("waveAddress"), maximum=256),
            "result_checkpoint": nullable(ref("waveAddress")),
            "coverage_bps": ref("bps"),
            "status": enum("verified", "unproven", "refused"),
            "authorizes_adoption": const(False),
            "grants_authority": const(False),
        }
    )
    topology_node = closed(
        {
            "id": ref("label"),
            "kind": enum("shared-trunk", "temporary-difference", "crossing-rejoin"),
            "parent_ids": array(ref("label"), maximum=256),
            "checkpoint_refs": array(ref("waveAddress"), maximum=256),
            "decision_ref": nullable(ref("waveAddress")),
        }
    )
    view = closed(
        {
            "schema": const("rapp-hive-autobest/1-view"),
            "hive_rappid": ref("rappid"),
            "world_id": ref("label"),
            "created_utc": ref("utc"),
            "compatibility": ref("waveAddress"),
            "view_kind": enum("board", "chat"),
            "basis": ref("hiveCheckpoint"),
            "source_vector": array(ref("sourceVectorEntry"), minimum=1, maximum=256),
            "artifact": ref("address"),
            "topology": array(ref("topologyNode"), maximum=4096),
            "omissions": array(ref("label"), maximum=256),
            "rebuildable": const(True),
            "authoritative": const(False),
            "grants_authority": const(False),
        }
    )

    compatibility = closed(
        {
            "schema": const("rapp-hive-autobest/1-compatibility"),
            "hive_rappid": ref("rappid"),
            "world_id": ref("label"),
            "compatibility_rappid": ref("rappid"),
            "created_utc": ref("utc"),
            "previous_compatibility": nullable(ref("waveAddress")),
            "trigger": ref("trigger"),
            "source": ref("endpoint"),
            "target": ref("endpoint"),
            "source_lens": ref("agentPin"),
            "target_finalizer": ref("agentPin"),
            "hotload_slot": ref("slotContract"),
            "intent_hash": ref("hash"),
            "source_vector": array(ref("sourceVectorEntry"), minimum=1, maximum=256),
            "mapping": ref("mappingContract"),
            "artifact_bundle": ref("address"),
            "mutation_lineage": ref("address"),
            "learning_trace": ref("address"),
            "n_lens_search": nullable(ref("address")),
            "verification": ref("verificationSet"),
            "static_agent": ref("staticAgent"),
            "hive_checkpoint": ref("hiveCheckpoint"),
            "status": enum("candidate", "locked", "superseded", "revoked"),
            "repository_content_is_instructions": const(False),
            "host_constructs_rapp1_envelope": const(True),
            "grants_authority": const(False),
            "shared_brain": const(False),
            "private_state_transfer": const("none"),
            "key_transfer": const("none"),
        }
    )
    exhaust = closed(
        {
            "schema": const("rapp-hive-autobest/1-exhaust"),
            "hive_rappid": ref("rappid"),
            "world_id": ref("label"),
            "created_utc": ref("utc"),
            "compatibility": ref("waveAddress"),
            "source_head": ref("frameSummary"),
            "target_head": nullable(ref("frameSummary")),
            "direction": enum("source-to-target", "target-to-source"),
            "operation": ref("label"),
            "input": ref("address"),
            "output": nullable(ref("address")),
            "failure_code": ref("label"),
            "satisfied_coverage_bps": ref("bps"),
            "missing_capabilities": array(ref("label"), maximum=256),
            "loss_class": enum("none", "bounded", "unavailable-source", "unknown"),
            "restrictions": array(ref("label"), maximum=256),
            "bounds_consumed": ref("runtimeBounds"),
            "retryable": {"type": "boolean"},
            "privacy_safe": const(True),
            "grants_authority": const(False),
        }
    )
    artifact_bundle = closed(
        {
            "schema": const("rapp-hive-autobest/1-artifact-bundle"),
            "bundle_rappid": ref("rappid"),
            "created_utc": ref("utc"),
            "compatibility": ref("waveAddress"),
            "entrypoint": const("agent.py"),
            "files": array(
                closed(
                    {
                        "path": ref("relativePath"),
                        "role": enum(
                            "entrypoint",
                            "code",
                            "schema",
                            "fixture",
                            "candidate-test",
                            "documentation",
                            "migration",
                            "manifest",
                            "data",
                        ),
                        "bytes": ref("uint53"),
                        "sha256": ref("hash"),
                        "content": ref("address"),
                    }
                ),
                minimum=1,
                maximum=4096,
            ),
            "lineage": ref("address"),
            "contracts": array(ref("address"), minimum=1, maximum=256),
            "generated_tests": array(ref("address"), maximum=256),
            "docs_are_instructions": const(False),
            "migrations_auto_execute": const(False),
            "authority": const(False),
        }
    )
    mutation_lineage = closed(
        {
            "schema": const("rapp-hive-autobest/1-mutation-lineage"),
            "source": ref("generation"),
            "successor": ref("generation"),
            "forward": array(ref("forwardMutation"), maximum=10000),
            "reverse": array(ref("reverseMutation"), maximum=10000),
            "selected_traits": array(ref("trait"), maximum=4096),
            "omitted_traits": array(ref("trait"), maximum=4096),
            "loss_class": enum("exact-lossless", "declared-lossy", "unproven"),
            "reconstruction": ref("reconstruction"),
            "coverage": closed(
                {
                    "source_total": ref("uint53"),
                    "source_mapped": ref("uint53"),
                    "successor_total": ref("uint53"),
                    "successor_mapped": ref("uint53"),
                }
            ),
        }
    )
    learning_trace = closed(
        {
            "schema": const("rapp-hive-autobest/1-learning-trace"),
            "trace_id": ref("label"),
            "compatibility_predecessor": nullable(ref("waveAddress")),
            "sanitizer_policy_sha256": ref("hash"),
            "source_commitments": array(ref("address"), minimum=1, maximum=512),
            "events": array(ref("traceEvent"), minimum=1, maximum=4096),
            "correction_coverage_bps": ref("bps"),
            "trace_root_hash": ref("hash"),
            "privacy_status": const("sanitized-sealed-default"),
        }
    )
    n_lens_search = closed(
        {
            "schema": const("rapp-hive-autobest/1-n-lens-search"),
            "root_id": ref("label"),
            "ancestor": ref("waveAddress"),
            "bounds": ref("searchBounds"),
            "lenses": array(ref("lensDescriptor"), minimum=1, maximum=32),
            "candidates": array(ref("candidate"), maximum=128),
            "crosses": array(ref("cross"), maximum=128),
            "selection": closed(
                {
                    "mode": enum(
                        "select-complete",
                        "recombine-traits",
                        "retain-pareto",
                        "unresolved",
                    ),
                    "selected_candidates": array(ref("label"), maximum=32),
                    "selected_traits": array(ref("label"), maximum=4096),
                    "scenario": ref("address"),
                    "coverage_bps": ref("bps"),
                    "unknowns": array(ref("label"), maximum=256),
                }
            ),
            "stop": nullable(
                closed(
                    {
                        "reason_code": ref("label"),
                        "frontier": array(ref("label"), maximum=128),
                        "remaining_unknowns": array(ref("label"), maximum=256),
                    }
                )
            ),
            "grants_authority": const(False),
        }
    )
    mutation_offer = closed(
        {
            "schema": const("rapp-hive-autobest/1-mutation-offer"),
            "offer_rappid": ref("rappid"),
            "created_utc": ref("utc"),
            "source_organization": ref("rappid"),
            "target_organization": ref("rappid"),
            "source_parents": array(ref("waveAddress"), minimum=1, maximum=256),
            "successor_frame": ref("waveAddress"),
            "successor_bundle": ref("address"),
            "mutation_lineage": ref("address"),
            "compatibility": ref("waveAddress"),
            "static_agent": ref("address"),
            "selected_traits": array(ref("label"), maximum=4096),
            "omitted_traits": array(ref("label"), maximum=4096),
            "tests": ref("verificationSet"),
            "pr_projection": closed(
                {
                    "repository": {"type": "string", "minLength": 1, "maxLength": 2048},
                    "base_commit": ref("commitPin"),
                    "head_commit": ref("commitPin"),
                    "base_inventory_hash": ref("hash"),
                    "head_inventory_hash": ref("hash"),
                    "provider_pr_id": ref("label"),
                    "locator": {"type": "string", "minLength": 1, "maxLength": 2048},
                    "projection_receipt": ref("address"),
                }
            ),
            "grants_authority": const(False),
        }
    )
    handshake_catalog = closed(
        {
            "schema": const("rapp-hive-autobest/1-handshake-catalog"),
            "hive_rappid": ref("rappid"),
            "world_id": ref("label"),
            "created_utc": ref("utc"),
            "base_catalog_hash": ref("hash"),
            "entries": array(
                closed(
                    {
                        "id": ref("label"),
                        "version": ref("uint53"),
                        "status": enum("locked", "superseded", "revoked"),
                        "source_profile": {"type": "string", "minLength": 1, "maxLength": 128},
                        "target_profile": {"type": "string", "minLength": 1, "maxLength": 128},
                        "compatibility": ref("waveAddress"),
                        "package": ref("address"),
                        "static_agent_sha256": ref("hash"),
                        "coverage_bps": ref("bps"),
                        "gaps": array(ref("label"), maximum=256),
                    }
                ),
                maximum=4096,
            ),
            "grants_authority": const(False),
        }
    )
    evolution = closed(
        {
            "schema": const("rapp-hive-autobest/1-evolution-proposal"),
            "level": enum(
                "handshake",
                "toolchain",
                "organization-seed-trait",
                "protocol-successor",
            ),
            "created_utc": ref("utc"),
            "parents": array(ref("waveAddress"), minimum=1, maximum=256),
            "candidate": ref("address"),
            "generator": ref("agentPin"),
            "scenario_corpus": ref("corpus"),
            "hidden_holdout": ref("corpus"),
            "controlled_mutants": ref("address"),
            "candidate_tests": ref("address"),
            "independent_tests": ref("address"),
            "verifier": ref("agentPin"),
            "canary": ref("canary"),
            "rollback": ref("address"),
            "promotion_target": ref("label"),
            "status": enum("proposed", "verified", "canary", "accepted", "rejected", "revoked"),
            "adoption_authorized": const(False),
        }
    )
    fixture_binding = closed(
        {
            "schema": const("rapp-hive-autobest/1-fixture-binding"),
            "private_fixture": const(True),
            "contract": closed(
                {
                    "path": const("HIVE-INTEROPERABILITY.md"),
                    "sha256": ref("hash"),
                    "bytes": ref("uint53"),
                }
            ),
            "source": closed(
                {
                    "repository": const(
                        "https://github.com/billwhalenmsft/softwarecoellc-vteam-hive"
                    ),
                    "commit": const("f66da3d879b53a439bc87de764d79f68ceec048a"),
                    "verified_frames": const(2),
                    "verified_artifacts": const(9),
                }
            ),
            "handshake": closed(
                {
                    "path": const("handshake.json"),
                    "sha256": const(
                        "0c52264b81bf88dd8555defa9363a23d8eb8ef85c3c12f66ddcaaabfc85a8882"
                    ),
                    "bytes": const(5351),
                }
            ),
            "source_lens": closed(
                {
                    "path": const("source-agent.py"),
                    "sha256": const(
                        "679fff9531c0c8b13457d594f746c45da28925a7c1be40473e8ca00823db8671"
                    ),
                    "bytes": const(11302),
                }
            ),
            "target_finalizer": closed(
                {
                    "path": const("target-finalizer.py"),
                    "sha256": const(
                        "c056339f90fdd4e604dbefa40291f1b7b22946d26749b36230bb3b29dd8e2296"
                    ),
                    "bytes": const(11461),
                }
            ),
            "static_package": closed(
                {
                    "manifest_sha256": ref("hash"),
                    "agent_sha256": ref("hash"),
                    "compatibility_frame_sha256": ref("hash"),
                    "generation_receipt_sha256": ref("hash"),
                    "public_identity_sha256": ref("hash"),
                }
            ),
            "authority": const(False),
        }
    )

    definitions = {
        "hash": hash_value,
        "label": label,
        "text": text,
        "relativePath": relative_path,
        "rappid": rappid,
        "utc": utc,
        "uint53": uint53,
        "bps": bps,
        "address": address,
        "waveAddress": wave_address,
        "frameSummary": frame_summary,
        "commitPin": commit_pin,
        "repositoryPin": repository_pin,
        "pinnedValue": pinned_value,
        "capability": capability,
        "endpoint": endpoint,
        "agentPin": agent_pin,
        "slotContract": slot_contract,
        "runtimeBounds": runtime_bounds,
        "sourceVectorEntry": source_vector_entry,
        "hiveCheckpoint": hive_checkpoint,
        "verificationSet": verification_set,
        "mappingContract": mapping_contract,
        "staticAgent": static_agent,
        "trigger": trigger,
        "fileHead": file_head,
        "trait": trait,
        "generation": generation,
        "forwardMutation": forward_mutation,
        "reverseMutation": reverse_mutation,
        "reconstruction": reconstruction,
        "traceEvent": trace_event,
        "searchBounds": search_bounds,
        "lensDescriptor": lens_descriptor,
        "candidate": candidate,
        "cross": cross,
        "corpus": corpus,
        "canary": canary,
        "assignment": assignment,
        "checkpoint": checkpoint,
        "decision": decision,
        "topologyNode": topology_node,
        "view": view,
        "compatibility": compatibility,
        "exhaust": exhaust,
        "artifactBundle": artifact_bundle,
        "mutationLineage": mutation_lineage,
        "learningTrace": learning_trace,
        "nLensSearch": n_lens_search,
        "mutationOffer": mutation_offer,
        "handshakeCatalog": handshake_catalog,
        "evolution": evolution,
        "fixtureBinding": fixture_binding,
    }
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": (
            "https://raw.githubusercontent.com/kody-w/rapp-work/main/"
            "protocols/rapp-hive-autobest/1/schema.json"
        ),
        "title": "RAPP Hive AutoBest/1 records",
        "description": (
            "Closed structural schemas for compatibility Frames, typed exhaust, "
            "program bundles, exact mutation lineage, sanitized learning traces, "
            "bounded N-Lens search, mutation offers, handshake catalogs, and "
            "recursive evolution proposals."
        ),
        "$comment": (
            "Schema validity never grants authority, activates an agent, proves "
            "semantic truth, or replaces RAPP/1 signature and registry checks."
        ),
        "oneOf": [
            ref("compatibility"),
            ref("exhaust"),
            ref("assignment"),
            ref("checkpoint"),
            ref("decision"),
            ref("view"),
            ref("artifactBundle"),
            ref("mutationLineage"),
            ref("learningTrace"),
            ref("nLensSearch"),
            ref("mutationOffer"),
            ref("handshakeCatalog"),
            ref("evolution"),
            ref("fixtureBinding"),
        ],
        "$defs": definitions,
    }


def encoded() -> bytes:
    return (
        json.dumps(build_schema(), indent=2, ensure_ascii=True, sort_keys=False) + "\n"
    ).encode("utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    arguments = parser.parse_args(argv)
    expected = encoded()
    if arguments.write:
        SCHEMA_PATH.write_bytes(expected)
    if arguments.check:
        if not SCHEMA_PATH.is_file() or SCHEMA_PATH.read_bytes() != expected:
            raise SystemExit("schema.json differs from schema_source.py")
    if not arguments.write and not arguments.check:
        print(expected.decode("utf-8"), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
