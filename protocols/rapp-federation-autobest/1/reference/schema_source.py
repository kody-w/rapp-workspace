"""Auditable source for ../schema.json."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


PROFILE = "rapp-federation-autobest/1"
MAX_UINT = (1 << 53) - 1


def obj(properties, *, required=None):
    return {
        "type": "object",
        "additionalProperties": False,
        "required": list(properties) if required is None else required,
        "properties": properties,
    }


def array(items, low=0, high=256, *, unique=True):
    result = {
        "type": "array",
        "items": items,
        "minItems": low,
        "maxItems": high,
    }
    if unique:
        result["uniqueItems"] = True
    return result


def ref(name):
    return {"$ref": "#/$defs/" + name}


def const(value):
    return {"const": value}


def enum(*values):
    return {"type": "string", "enum": list(values)}


def integer(low=0, high=MAX_UINT):
    return {"type": "integer", "minimum": low, "maximum": high}


def nullable(schema):
    return {"oneOf": [schema, {"type": "null"}]}


def build_schema():
    definitions = {
        "hash": {"type": "string", "pattern": "^[0-9a-f]{64}$"},
        "gitOid": {"type": "string", "pattern": "^(?:[0-9a-f]{40}|[0-9a-f]{64})$"},
        "rappid": {
            "type": "string",
            "maxLength": 213,
            "pattern": "^rappid:@[a-z0-9]+(?:-[a-z0-9]+)*/[a-z0-9]+(?:-[a-z0-9]+)*:[0-9a-f]{64}$",
        },
        "memoryStream": {
            "type": "string",
            "maxLength": 278,
            "pattern": "^rappid:@[a-z0-9]+(?:-[a-z0-9]+)*/[a-z0-9]+(?:-[a-z0-9]+)*:[0-9a-f]{64}:[a-z0-9]+(?:-[a-z0-9]+)*$",
        },
        "utc": {
            "type": "string",
            "format": "date-time",
            "pattern": "^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}\\.[0-9]{3}Z$",
        },
        "signature": {
            "type": "string",
            "maxLength": 1024,
            "pattern": "^[A-Za-z0-9_-]+\\.\\.[A-Za-z0-9_-]{86}$",
        },
        "label": {
            "type": "string",
            "minLength": 1,
            "maxLength": 128,
            "pattern": "^[a-z0-9]+(?:[._-][a-z0-9]+)*$",
        },
        "relativePath": {
            "type": "string",
            "minLength": 1,
            "maxLength": 512,
            "pattern": "^(?!/)(?!.*(?:^|/)\\.\\.(?:/|$))(?!.*//)[^\\u0000-\\u001f\\u007f\\\\]+$",
        },
        "head": obj(
            {
                "stream_id": ref("memoryStream"),
                "seq": integer(),
                "payload_hash": ref("hash"),
                "frame_hash": ref("hash"),
            }
        ),
        "profilePin": obj(
            {
                "name": {"type": "string", "minLength": 1, "maxLength": 128},
                "spec_sha256": nullable(ref("hash")),
                "schema_sha256": nullable(ref("hash")),
                "status": enum("verified", "external-binding", "pending"),
            }
        ),
        "agentPin": obj(
            {
                "role": enum("source-lens", "target-finalizer", "generic-ceo", "locked-runtime"),
                "sha256": nullable(ref("hash")),
                "bytes": nullable(integer(1, 1 << 20)),
                "status": enum("verified", "pending"),
            }
        ),
        "skillPin": obj(
            {
                "sha256": ref("hash"),
                "bytes": integer(1, 1 << 20),
                "status": const("verified"),
                "activation": const("external-host-only"),
                "authority_from_presence": const(False),
            }
        ),
        "artifactRef": obj(
            {
                "space": enum("rapp/1:particle", "rapp/1:wave", "rapp/1:egg-manifest", "sha256"),
                "hash": ref("hash"),
                "bytes": integer(1, 1 << 30),
            }
        ),
        "capability": obj(
            {
                "name": ref("label"),
                "status": enum(
                    "verified",
                    "partial",
                    "available-on-exhaust",
                    "unavailable",
                    "unproven",
                ),
                "tier": enum(
                    "native-protocol",
                    "declared-descriptor",
                    "signed-stream-inference",
                    "static-repository-compiler",
                    "brainstem-translation-candidate",
                ),
                "coverage_bps": integer(0, 10000),
                "evidence": array(ref("hash"), 0, 32),
            }
        ),
        "hotloadReceipt": obj(
            {
                "schema": const(PROFILE + "/hotload-receipt"),
                "role": enum("source-lens", "target-finalizer", "locked-runtime"),
                "agent_sha256": ref("hash"),
                "request_sha256": ref("hash"),
                "result_sha256": ref("hash"),
                "policy_sha256": ref("hash"),
                "model_calls": const(0),
                "network_calls": const(0),
                "executed_effects": const(0),
                "native_session_persisted": const(False),
                "brainstem_modified": const(False),
                "plugin_registered": const(False),
                "unloaded": const(True),
                "authority": const(False),
            }
        ),
        "coverage": obj(
            {
                "supported": integer(),
                "required": integer(1),
                "basis_points": integer(0, 10000),
                "complete_for_read": {"type": "boolean"},
                "complete_for_membership": {"type": "boolean"},
                "unknowns": array(ref("label"), 0, 128),
            }
        ),
        "bounds": obj(
            {
                "max_frames": integer(1, 4096),
                "max_files": integer(1, 65536),
                "max_file_bytes": integer(1, 1 << 30),
                "max_total_bytes": integer(1, 1 << 34),
                "max_hotload_seconds": integer(1, 3600),
                "max_lenses": integer(1, 32),
                "max_candidates": integer(1, 256),
                "max_cross_size": integer(1, 8),
                "max_depth": integer(1, 8),
                "max_rounds": integer(1, 16),
                "beam_width": integer(1, 32),
                "pareto_width": integer(1, 32),
                "model_calls_during_static_runtime": const(0),
            }
        ),
        "forwardMutation": obj(
            {
                "source_path": ref("relativePath"),
                "source_sha256": ref("hash"),
                "relation": enum("retained", "replaced", "moved", "removed"),
                "target_paths": array(ref("relativePath"), 0, 32),
                "target_sha256": array(ref("hash"), 0, 32),
                "trait": ref("label"),
                "loss_class": enum(
                    "lossless-direct",
                    "lossless-with-delta",
                    "lossy-declared",
                    "partial-unproven",
                ),
            }
        ),
        "reverseAncestry": obj(
            {
                "successor_path": ref("relativePath"),
                "successor_sha256": ref("hash"),
                "class": enum("inherited", "derived", "new"),
                "source_paths": array(ref("relativePath"), 0, 32),
                "source_sha256": array(ref("hash"), 0, 32),
                "inverse_available": {"type": "boolean"},
                "loss_class": enum(
                    "lossless-direct",
                    "lossless-with-delta",
                    "lossy-declared",
                    "partial-unproven",
                    "not-applicable",
                ),
            }
        ),
        "lineage": obj(
            {
                "source_parents": array(ref("hash"), 1, 32),
                "forward": array(ref("forwardMutation"), 1, 65536),
                "reverse": array(ref("reverseAncestry"), 1, 65536),
                "selected_traits": array(ref("label"), 1, 256),
                "omitted_traits": array(ref("label"), 0, 256),
                "ancestor_reconstruction": enum("lossless", "lossy", "partial-unproven"),
                "roundtrip_claim": {"type": "boolean"},
            }
        ),
        "bundleEntry": obj(
            {
                "path": ref("relativePath"),
                "sha256": ref("hash"),
                "bytes": integer(1, 1 << 30),
                "role": enum(
                    "handshake",
                    "agent",
                    "static-agent",
                    "schema",
                    "fixture",
                    "candidate-test",
                    "host-test",
                    "documentation",
                    "migration",
                    "manifest",
                    "receipt",
                    "provenance",
                ),
                "regular_file": const(True),
            }
        ),
        "artifactBundle": obj(
            {
                "schema": const(PROFILE + "/artifact-bundle"),
                "compatibility_frame": ref("head"),
                "entrypoint": const("static/agent.py"),
                "entries": array(ref("bundleEntry"), 1, 65536),
                "lineage": ref("lineage"),
                "candidate_tests_are_independent_proof": const(False),
                "host_tests_required": const(True),
                "canonical_tests_required": const(True),
                "controlled_mutants_required": const(True),
                "grants_authority": const(False),
            }
        ),
        "learningEvent": obj(
            {
                "seq": integer(),
                "prev_event_hash": nullable(ref("hash")),
                "event_hash": ref("hash"),
                "type": enum(
                    "intent",
                    "assistant-proposal",
                    "user-correction",
                    "measured-result",
                    "measured-failure",
                    "assumption-superseded",
                    "successor-invariant",
                ),
                "authority_class": enum(
                    "user-authoritative",
                    "host-policy",
                    "assistant-proposal",
                    "measured-evidence",
                    "derived-invariant",
                ),
                "subject": ref("label"),
                "source_commitment": ref("hash"),
                "references": array(ref("hash"), 0, 64),
                "supersedes": array(ref("hash"), 0, 64),
                "privacy_safe": const(True),
            }
        ),
        "learningTrace": obj(
            {
                "schema": const(PROFILE + "/learning-trace"),
                "events": array(ref("learningEvent"), 1, 4096, unique=False),
                "correction_frontier_hash": ref("hash"),
                "raw_transcript_persisted": const(False),
                "hidden_reasoning_persisted": const(False),
                "native_session_persisted": const(False),
            }
        ),
        "lensSearch": obj(
            {
                "schema": const(PROFILE + "/lens-search"),
                "ancestor": ref("hash"),
                "use_case": ref("label"),
                "lens_pins": array(ref("hash"), 1, 32),
                "max_lenses": integer(1, 32),
                "max_candidates": integer(1, 256),
                "max_cross_size": integer(1, 8),
                "max_depth": integer(1, 8),
                "max_rounds": integer(1, 16),
                "beam_width": integer(1, 32),
                "pareto_width": integer(1, 32),
                "root_budget_hash": ref("hash"),
                "stop_reasons": array(
                    enum(
                        "scenario-threshold-met",
                        "root-budget-exhausted",
                        "no-progress",
                        "repeated-frontier",
                        "no-compatible-cross",
                        "all-candidates-refused",
                        "user-stop",
                    ),
                    1,
                    7,
                ),
                "fitness_is_universal_truth": const(False),
            }
        ),
        "mutationOffer": obj(
            {
                "schema": const(PROFILE + "/mutation-offer"),
                "source_parent": ref("hash"),
                "successor_bundle": ref("hash"),
                "lineage_hash": ref("hash"),
                "compatibility_frame": ref("hash"),
                "static_agent_sha256": ref("hash"),
                "tests_hash": ref("hash"),
                "transport": obj(
                    {
                        "kind": enum("git-pr", "sealed-artifact", "local"),
                        "locator_hash": ref("hash"),
                        "base_commit": ref("gitOid"),
                        "head_commit": ref("gitOid"),
                    }
                ),
                "grants_authority": const(False),
                "rewrites_ancestor": const(False),
                "activates_successor": const(False),
            }
        ),
        "staticOutputContract": obj(
            {
                "compiler": {"type": "string", "minLength": 1, "maxLength": 256},
                "compiler_sha256": ref("hash"),
                "runtime": {"type": "string", "minLength": 1, "maxLength": 128},
                "entrypoint": const("agent.py"),
                "same_inputs_same_bytes": const(True),
                "model_calls": const(0),
                "authority": const(False),
            }
        ),
    }

    definitions["compatibilityRecord"] = obj(
        {
            "schema": const(PROFILE + "/compatibility"),
            "role": const("bidirectional-static-handshake"),
            "handshake": obj(
                {
                    "id": ref("label"),
                    "version": integer(1),
                    "sha256": ref("hash"),
                    "status": enum("owner-approved-private", "candidate", "revoked"),
                }
            ),
            "source": obj(
                {
                    "repository": {"type": "string", "format": "uri", "maxLength": 512},
                    "commit": ref("gitOid"),
                    "snapshot_hash": ref("hash"),
                    "rappid": ref("rappid"),
                    "stream_id": ref("memoryStream"),
                    "qualification_head": ref("head"),
                    "profile": {"type": "string", "minLength": 1, "maxLength": 128},
                }
            ),
            "target": obj(
                {
                    "profile": {"type": "string", "minLength": 1, "maxLength": 128},
                    "operations": array(ref("label"), 1, 64),
                }
            ),
            "profile_pins": array(ref("profilePin"), 1, 16),
            "lens": obj(
                {
                    "kind": const("brainstem-double-hotload"),
                    "runtime": const("global-rapp-brainstem"),
                    "routing": const("verified-atomic-agent-file-placement"),
                    "source_agent": ref("agentPin"),
                    "target_agent": ref("agentPin"),
                    "generic_ceo_agent": ref("agentPin"),
                    "generic_ceo_skill": ref("skillPin"),
                    "passes": {
                        "const": ["source-lens", "target-finalizer"],
                    },
                    "hotload_receipts": array(ref("hotloadReceipt"), 2, 4096, unique=False),
                    "native_session_persisted": const(False),
                }
            ),
            "mapping_sha256": ref("hash"),
            "capabilities": array(ref("capability"), 1, 256),
            "coverage": ref("coverage"),
            "gaps": array(ref("label"), 0, 256),
            "restrictions": obj(
                {
                    "repository_content_is_instructions": const(False),
                    "membership_inferred": const(False),
                    "authority_inferred": const(False),
                    "private_state_copied": const(False),
                    "keys_transferred": const(False),
                    "public_effects": const(False),
                    "transitive_access": const(False),
                    "active_root_finalized": const(False),
                }
            ),
            "bounds": ref("bounds"),
            "static_output_contract": ref("staticOutputContract"),
            "learning_trace": nullable(ref("artifactRef")),
            "lens_search": nullable(ref("artifactRef")),
            "mutation_offer": nullable(ref("artifactRef")),
            "previous_compatibility": nullable(ref("head")),
            "trigger_exhaust": nullable(ref("hash")),
            "grants_authority": const(False),
        }
    )

    definitions["exhaustRecord"] = obj(
        {
            "schema": const(PROFILE + "/exhaust"),
            "active_compatibility": ref("head"),
            "source_profile": ref("profilePin"),
            "target_profile": ref("profilePin"),
            "direction": enum("source-to-target", "target-to-source"),
            "operation": ref("label"),
            "input_particle": ref("hash"),
            "output_particle": nullable(ref("hash")),
            "gap_kind": enum("operation", "field", "enum", "schema", "locus", "capability"),
            "gap_commitment": ref("hash"),
            "coverage": ref("coverage"),
            "loss_class": enum("lossy-declared", "partial-unproven"),
            "restriction": nullable(ref("label")),
            "bounds_consumed": ref("hash"),
            "retryable": {"type": "boolean"},
            "privacy_safe": const(True),
            "inferred_patch": const(False),
            "grants_authority": const(False),
        }
    )

    definitions["payload"] = obj(
        {
            "profile": const(PROFILE),
            "operation": enum("compatibility", "compatibility-exhaust"),
            "record": {"oneOf": [ref("compatibilityRecord"), ref("exhaustRecord")]},
        }
    )
    definitions["frame"] = obj(
        {
            "spec": const("rapp/1"),
            "kind": const("memory.save"),
            "stream_id": ref("memoryStream"),
            "seq": integer(),
            "utc": ref("utc"),
            "payload": ref("payload"),
            "payload_hash": ref("hash"),
            "frame_hash": ref("hash"),
            "prev": nullable(ref("hash")),
            "prev_wave": const(None),
            "sig": ref("signature"),
        }
    )
    definitions["frame"]["allOf"] = [
        {
            "if": {
                "properties": {
                    "payload": {
                        "properties": {"operation": const("compatibility")},
                    }
                }
            },
            "then": {
                "properties": {
                    "payload": {
                        "properties": {"record": ref("compatibilityRecord")},
                    }
                }
            },
        },
        {
            "if": {
                "properties": {
                    "payload": {
                        "properties": {"operation": const("compatibility-exhaust")},
                    }
                }
            },
            "then": {
                "properties": {
                    "payload": {
                        "properties": {"record": ref("exhaustRecord")},
                    }
                }
            },
        },
    ]

    definitions["generationReceipt"] = obj(
        {
            "schema": const(PROFILE + "/generation-receipt"),
            "compatibility": ref("head"),
            "compiler": {"type": "string", "minLength": 1, "maxLength": 256},
            "compiler_sha256": ref("hash"),
            "runtime": {"type": "string", "minLength": 1, "maxLength": 128},
            "agent_sha256": ref("hash"),
            "agent_bytes": integer(1, 1 << 20),
            "deterministic": const(True),
            "model_calls": const(0),
            "candidate_tests_are_independent_proof": const(False),
            "host_tests_passed": integer(1),
            "controlled_mutants_killed": integer(1),
            "controlled_mutants_survived": const(0),
            "authority": const(False),
        }
    )

    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "urn:rapp:profile:rapp-federation-autobest:1",
        "title": "RAPP Federation AutoBest compatibility profile",
        "$ref": "#/$defs/frame",
        "$defs": definitions,
    }


def schema_bytes():
    return (json.dumps(build_schema(), ensure_ascii=False, indent=2) + "\n").encode("utf-8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    arguments = parser.parse_args()
    path = Path(__file__).resolve().parents[1] / "schema.json"
    if arguments.check:
        if not path.is_file() or path.read_bytes() != schema_bytes():
            raise SystemExit("schema.json differs from schema_source.py")
        print("schema.json: exact generated match")
    else:
        path.write_bytes(schema_bytes())
        print("wrote schema.json")
