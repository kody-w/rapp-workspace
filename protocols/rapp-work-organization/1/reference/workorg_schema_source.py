"""Uniquely named auditable source for the closed Work Organization/1 schemas."""

from __future__ import annotations

import argparse
from pathlib import Path

from workorg_common import PROFILE, ROOT, pretty_bytes


SCHEMAS = ROOT / "schemas"
BASE = "https://github.com/kody-w/rapp-workspace/raw/main/protocols/rapp-work-organization/1/schemas/"
MAX_UINT = (1 << 53) - 1


def obj(properties, *, required=None):
    return {
        "type": "object",
        "properties": properties,
        "required": list(properties) if required is None else required,
        "additionalProperties": False,
    }


def array(items, low=0, high=256, *, unique=False):
    value = {"type": "array", "items": items, "minItems": low, "maxItems": high}
    if unique:
        value["uniqueItems"] = True
    return value


def enum(*values):
    return {"type": "string", "enum": list(values)}


def integer(low=0, high=MAX_UINT):
    return {"type": "integer", "minimum": low, "maximum": high}


def nullable(value):
    return {"oneOf": [value, {"type": "null"}]}


def ref(name):
    return {"$ref": "common.schema.json#/$defs/" + name}


def schema(name, body):
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": BASE + name,
        **body,
    }


def common_schema():
    hash_schema = {"type": "string", "pattern": "^[0-9a-f]{64}$"}
    label = {
        "type": "string",
        "minLength": 1,
        "maxLength": 128,
        "pattern": "^[^\\u0000-\\u001f\\u007f]+$",
    }
    address = lambda space: obj({"space": {"const": space}, "hash": hash_schema})
    content_head = obj(
        {
            "entry_id": {"type": "string", "minLength": 1, "maxLength": 256},
            "path": {
                "type": "string",
                "minLength": 1,
                "maxLength": 1024,
                "pattern": "^(?!/)(?!.*(?:^|/)\\.\\.?/)(?!.*\\\\)[^\\u0000]+$",
            },
            "mode": enum("100644", "100755"),
            "sha256": hash_schema,
            "bytes": integer(0, 1 << 30),
            "content": address("rapp/1:particle"),
        }
    )
    return schema(
        "common.schema.json",
        {
            "$defs": {
                "hash": hash_schema,
                "gitHash": {"type": "string", "pattern": "^[0-9a-f]{40}$"},
                "label": label,
                "path": content_head["properties"]["path"],
                "rappid": {
                    "type": "string",
                    "minLength": 76,
                    "maxLength": 213,
                    "pattern": (
                        "^rappid:@(?=[^/]{1,39}/)[a-z0-9]+(?:-[a-z0-9]+)*/"
                        "(?=[^:]{1,100}:)[a-z0-9]+(?:-[a-z0-9]+)*:[0-9a-f]{64}$"
                    ),
                },
                "utc": {
                    "type": "string",
                    "format": "date-time",
                    "pattern": (
                        "^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:"
                        "[0-9]{2}:[0-9]{2}\\.[0-9]{3}Z$"
                    ),
                },
                "wave": address("rapp/1:wave"),
                "particle": address("rapp/1:particle"),
                "egg": address("rapp/1:egg-manifest"),
                "contentHead": content_head,
                "receiptSet": array(address("rapp/1:wave"), 0, 512, unique=True),
                "basisPoints": integer(0, 10000),
                "artifactPin": obj(
                    {
                        "sha256": hash_schema,
                        "bytes": integer(1, 4 * 1024 * 1024),
                        "role": label,
                        "embedded": {"type": "boolean"},
                    }
                ),
                "loss": obj(
                    {
                        "class": enum(
                            "lossless",
                            "content-unavailable",
                            "metadata-unavailable",
                            "semantic-unavailable",
                            "external-dependency-unavailable",
                            "privacy-withheld",
                            "noninvertible-transform",
                        ),
                        "source_refs_preserved": {"type": "boolean"},
                        "round_trip_claimed": {"type": "boolean"},
                    }
                ),
                "bounds": obj(
                    {
                        "max_lenses": integer(1, 64),
                        "max_candidates": integer(1, 256),
                        "max_cross_parents": integer(1, 8),
                        "max_cross_traits": integer(1, 64),
                        "max_depth": integer(1, 32),
                        "max_rounds": integer(1, 16),
                        "max_work_units": integer(1, 1000000),
                        "max_artifact_bytes": integer(1, 1 << 30),
                    }
                ),
            }
        },
    )


def activation_schema():
    return schema(
        "activation-document.schema.json",
        obj(
            {
                "schema": {"const": PROFILE + "/activation-document"},
                "spec_sha256": ref("hash"),
                "manifest_sha256": ref("hash"),
                "brainstem_runtime_sha256": ref("hash"),
                "organization_rappid": ref("rappid"),
                "world_id": ref("label"),
                "policy": ref("particle"),
                "not_before_utc": ref("utc"),
                "expires_utc": ref("utc"),
                "signer_key_id": ref("label"),
                "revocation_status": {"const": "active"},
                "generic_ceo_agent_sha256": nullable(ref("hash")),
            }
        ),
    )


def mutation_schema():
    source_entry = obj(
        {
            "source": ref("contentHead"),
            "disposition": enum("retained", "replaced", "moved", "removed"),
            "relation": enum(
                "retain",
                "metadata-change",
                "move",
                "rewrite",
                "replace",
                "remove",
                "split",
                "combine",
                "reorganize",
            ),
            "targets": array(ref("contentHead"), 0, 64),
            "mutation_receipts": ref("receiptSet"),
            "inverse_material": array(ref("egg"), 0, 16, unique=True),
            "loss": ref("loss"),
        }
    )
    reverse_entry = obj(
        {
            "successor": ref("contentHead"),
            "ancestry": enum("inherited", "derived", "new"),
            "sources": array(ref("contentHead"), 0, 64),
            "derivation_receipts": ref("receiptSet"),
            "inverse_material": array(ref("egg"), 0, 16, unique=True),
            "loss": ref("loss"),
        }
    )
    parent = obj(
        {
            "frame": ref("wave"),
            "inventory": ref("particle"),
            "repository_commit": nullable(ref("gitHash")),
            "repository_tree": nullable(ref("gitHash")),
        }
    )
    trait = obj(
        {
            "trait_id": ref("label"),
            "status": enum("retained", "replaced", "moved", "removed", "new"),
            "source_evidence": array(ref("wave"), 0, 64, unique=True),
            "successor_evidence": array(ref("wave"), 0, 64, unique=True),
            "dependencies": array(ref("label"), 0, 64, unique=True),
        }
    )
    return schema(
        "mutation-lineage.schema.json",
        obj(
            {
                "schema": {"const": PROFILE + "/mutation-lineage"},
                "output_shape": enum("sidecar", "full-successor", "hybrid"),
                "source_parents": array(parent, 1, 8),
                "source_inventory": ref("particle"),
                "successor_inventory": ref("particle"),
                "successor_root": ref("egg"),
                "forward": array(source_entry, 1, 10000),
                "reverse": array(reverse_entry, 1, 10000),
                "traits": array(trait, 0, 4096),
                "directionality": enum(
                    "bidirectional-lossless",
                    "bidirectional-partial",
                    "forward-only-lossy",
                ),
                "reconstruction": obj(
                    {
                        "status": enum(
                            "verified-contained",
                            "verified-external",
                            "unproven",
                        ),
                        "inverse_material": array(ref("egg"), 0, 64, unique=True),
                        "reconstructor_sha256": nullable(ref("hash")),
                        "runtime_manifest_sha256": nullable(ref("hash")),
                    }
                ),
                "grants_authority": {"const": False},
            }
        ),
    )


def artifact_schema():
    entry = obj(
        {
            "path": ref("path"),
            "role": enum(
                "hotload-entrypoint",
                "code",
                "data",
                "schema",
                "fixture",
                "candidate-test",
                "documentation",
                "migration",
                "manifest",
                "compatibility-metadata",
            ),
            "sha256": ref("hash"),
            "bytes": integer(0, 1 << 30),
            "mode": enum("100644", "100755"),
            "media_type": {"type": "string", "minLength": 1, "maxLength": 128},
            "lineage": array(ref("wave"), 0, 64, unique=True),
            "generation_receipt": nullable(ref("wave")),
        }
    )
    receipt = obj(
        {
            "compatibility_frame": ref("wave"),
            "compatibility_frame_octets_sha256": ref("hash"),
            "compiler_sha256": ref("hash"),
            "compiler_runtime_manifest_sha256": ref("hash"),
            "template_sha256": ref("hash"),
            "output_agent_sha256": ref("hash"),
            "output_agent_bytes": integer(1, 4 * 1024 * 1024),
            "generation_version": {"type": "string", "minLength": 1, "maxLength": 128},
            "model_calls": {"const": 0},
            "deterministic": {"const": True},
            "grants_authority": {"const": False},
        }
    )
    return schema(
        "artifact-bundle.schema.json",
        obj(
            {
                "schema": {"const": PROFILE + "/artifact-bundle"},
                "bundle_rappid": ref("rappid"),
                "compatibility_frame": ref("wave"),
                "entrypoint": {"const": "agent.py"},
                "files": array(entry, 1, 4096),
                "runtime_manifest_sha256": ref("hash"),
                "aggregate_sha256": ref("hash"),
                "source_mutation_manifest": ref("particle"),
                "generation_receipt": receipt,
                "candidate_tests_are_independent_proof": {"const": False},
                "grants_authority": {"const": False},
            }
        ),
    )


def trace_schema():
    source_receipt = obj(
        {
            "assurance": enum(
                "user-signed",
                "host-attested-authenticated-user-input",
                "host-measured-tool-result",
                "host-measured-agent-result",
                "withheld-private-source",
            ),
            "receipt": ref("wave"),
        }
    )
    event = obj(
        {
            "event_id": ref("hash"),
            "trace_seq": integer(0, 4096),
            "previous_event": nullable(ref("wave")),
            "event_type": enum(
                "intent",
                "proposal",
                "user-correction",
                "tool-result",
                "tool-failure",
                "agent-result",
                "agent-failure",
                "assumption-superseded",
                "successor-invariant",
                "user-interrupt",
                "trace-closure",
            ),
            "actor_role": enum("user", "assistant", "host", "tool", "agent", "compiler"),
            "authority": enum(
                "user-signed",
                "host-attested-user-authority",
                "proposal-only",
                "measured-evidence",
                "derived-history",
                "derived-from-authoritative-correction",
            ),
            "supersedes": array(ref("hash"), 0, 64, unique=True),
            "source_receipts": array(source_receipt, 0, 64),
            "structured_content": {"type": "object"},
            "raw_content_persisted": {"const": False},
            "hidden_reasoning_present": {"const": False},
        }
    )
    return schema(
        "learning-trace.schema.json",
        obj(
            {
                "schema": {"const": PROFILE + "/learning-trace"},
                "trace_id": ref("hash"),
                "sanitizer_sha256": ref("hash"),
                "reducer_sha256": ref("hash"),
                "events": array(event, 1, 4096),
                "ordered_event_hashes": array(ref("hash"), 1, 4096),
                "active_successor_invariants": array(ref("hash"), 0, 1024, unique=True),
                "unresolved_corrections": array(ref("hash"), 0, 1024, unique=True),
                "correction_fixture_set": ref("particle"),
                "grants_authority": {"const": False},
            }
        ),
    )


def compatibility_schema():
    artifact_pin = ref("artifactPin")
    return schema(
        "compatibility.schema.json",
        obj(
            {
                "schema": {"const": PROFILE + "/compatibility"},
                "organization_rappid": ref("rappid"),
                "world_id": ref("label"),
                "handshake_id": ref("label"),
                "generation": integer(1, MAX_UINT),
                "previous_compatibility": nullable(ref("wave")),
                "source": obj(
                    {
                        "profile": ref("label"),
                        "schema_sha256": ref("hash"),
                        "inventory": ref("particle"),
                        "parents": array(ref("wave"), 1, 64, unique=True),
                    }
                ),
                "target": obj(
                    {
                        "profile": ref("label"),
                        "schema_sha256": ref("hash"),
                        "inventory": ref("particle"),
                    }
                ),
                "lens": obj(
                    {
                        "source_agent": artifact_pin,
                        "target_finalizer": artifact_pin,
                        "receipts": ref("receiptSet"),
                    }
                ),
                "mapping_contract": ref("particle"),
                "forward_map": ref("particle"),
                "reverse_map": ref("particle"),
                "directionality": enum(
                    "bidirectional-lossless",
                    "bidirectional-partial",
                    "forward-only-lossy",
                ),
                "policy": ref("particle"),
                "activation": ref("particle"),
                "trace": ref("wave"),
                "coverage": obj(
                    {
                        "forward_bp": ref("basisPoints"),
                        "reverse_bp": ref("basisPoints"),
                        "source_roundtrip_bp": ref("basisPoints"),
                        "target_roundtrip_bp": ref("basisPoints"),
                        "declared_gaps": integer(0, 10000),
                        "unknowns": integer(0, 10000),
                    }
                ),
                "bounds": ref("bounds"),
                "artifact_bundle": nullable(ref("egg")),
                "runtime": obj(
                    {
                        "mode": {"const": "locked-static-no-model"},
                        "model_calls": {"const": 0},
                        "typed_exhaust_on_gap": {"const": True},
                    }
                ),
                "receipts": ref("receiptSet"),
                "grants_authority": {"const": False},
            }
        ),
    )


def search_schema():
    candidate = obj(
        {
            "candidate_id": ref("hash"),
            "dimension": ref("rappid"),
            "kind": enum(
                "complete-successor",
                "trait-successor",
                "repair",
                "compatibility-agent",
                "compiler",
                "test-or-verifier",
            ),
            "artifact": ref("egg"),
            "parents": array(ref("wave"), 1, 8, unique=True),
            "traits": array(ref("label"), 0, 64, unique=True),
            "status": enum("active", "pareto", "pruned", "selected", "crossed", "refused"),
        }
    )
    return schema(
        "search.schema.json",
        obj(
            {
                "schema": {"const": PROFILE + "/search"},
                "ancestor_frames": array(ref("wave"), 1, 8, unique=True),
                "ancestor_inventory": ref("particle"),
                "declared_use_case": ref("label"),
                "scenario_corpus": ref("particle"),
                "holdout_commitment": ref("particle"),
                "bounds": ref("bounds"),
                "lens_dimensions": array(ref("rappid"), 1, 64, unique=True),
                "candidates": array(candidate, 0, 256),
                "pareto_frontier": array(ref("hash"), 0, 32, unique=True),
                "selected": nullable(ref("hash")),
                "stop_reason": nullable(
                    enum(
                        "budget-exhausted",
                        "candidate-cap",
                        "round-cap",
                        "depth-cap",
                        "all-candidates-pruned",
                        "no-progress",
                        "equivalence-saturation",
                        "critical-invariant-failure",
                        "holdout-exhaustion",
                        "privacy-refusal",
                        "user-interrupt",
                        "authority-expired",
                    )
                ),
                "grants_authority": {"const": False},
            }
        ),
    )


def evolution_schema():
    return schema(
        "evolution.schema.json",
        obj(
            {
                "schema": {"const": PROFILE + "/evolution"},
                "level": enum("handshake", "implementation", "seed-trait", "protocol-successor"),
                "parents": array(ref("wave"), 1, 64, unique=True),
                "candidate": ref("egg"),
                "scenario_corpus": ref("particle"),
                "hidden_holdout": ref("particle"),
                "controlled_mutants": ref("particle"),
                "canonical_evaluation": ref("wave"),
                "canary": ref("wave"),
                "promotion": nullable(ref("wave")),
                "adoption": nullable(ref("wave")),
                "rollback_target": ref("wave"),
                "automatic_promotion": {"const": False},
                "generated_tests_self_certify": {"const": False},
                "grants_authority": {"const": False},
            }
        ),
    )


def offer_schema():
    return schema(
        "mutation-offer.schema.json",
        obj(
            {
                "schema": {"const": PROFILE + "/mutation-offer"},
                "offer_id": ref("hash"),
                "source_organization": ref("rappid"),
                "destination_organization": ref("rappid"),
                "source_parents": array(ref("wave"), 1, 8, unique=True),
                "successor_frame": ref("wave"),
                "successor_inventory": ref("particle"),
                "successor_artifact": ref("egg"),
                "forward_map": ref("particle"),
                "reverse_map": ref("particle"),
                "trait_map": ref("particle"),
                "compatibility": ref("wave"),
                "verification_receipts": ref("receiptSet"),
                "transport": obj(
                    {
                        "kind": enum("git-pr", "rapp-egg", "private-hive", "federation", "offline"),
                        "head_commit": nullable(ref("gitHash")),
                        "head_tree": nullable(ref("gitHash")),
                        "projection_sha256": ref("hash"),
                    }
                ),
                "merge_roots": {"const": False},
                "transfer_keys": {"const": False},
                "transfer_private_state": {"const": False},
                "grants_authority": {"const": False},
            }
        ),
    )


def bill_schema():
    return schema(
        "wild-handshake-binding.schema.json",
        obj(
            {
                "schema": {"const": PROFILE + "/wild-handshake-binding"},
                "id": {"const": "softwarecoellc-vteam-hive"},
                "status": {"const": "owner-approved-private"},
                "embedded_private_content": {"const": False},
                "handshake_profile": ref("artifactPin"),
                "source_lens": ref("artifactPin"),
                "target_finalizer": ref("artifactPin"),
                "contract": ref("artifactPin"),
                "source": obj(
                    {
                        "repository": {
                            "const": "https://github.com/billwhalenmsft/softwarecoellc-vteam-hive"
                        },
                        "commit": ref("gitHash"),
                        "profile": {"const": "microsol-project/1"},
                        "verified_frames": {"const": 2},
                        "verified_artifacts": {"const": 9},
                    }
                ),
                "proof": obj(
                    {
                        "double_hotload": {"const": "verified-local"},
                        "compatibility_frame": {"const": "verified-local-private"},
                        "static_agent": {"const": "verified-local-private"},
                        "model_calls_static_runtime": {"const": 0},
                    }
                ),
                "generic_ceo_agent": obj(
                    {
                        "status": {"const": "pending-pin"},
                        "sha256": {"type": "null"},
                    }
                ),
                "authority": {"const": False},
            }
        ),
    )


def frame_schema():
    kinds = [
        "declaration",
        "agent",
        "placement",
        "lens",
        "mutation",
        "rehearsal",
        "exhaust",
        "compatibility",
        "compilation",
        "artifact",
        "execution",
        "catalog",
        "trace",
        "command",
        "work",
        "search",
        "candidate",
        "cross",
        "selection",
        "evolution",
        "evaluation",
        "promotion",
        "rollback",
        "offer",
        "decision",
        "subscription",
        "control",
        "checkpoint",
    ]
    return schema(
        "frame.schema.json",
        obj(
            {
                "spec": {"const": "rapp/1"},
                "kind": enum(*["organization." + kind for kind in kinds]),
                "stream_id": {"type": "string", "minLength": 1, "maxLength": 278},
                "seq": integer(),
                "utc": ref("utc"),
                "payload": obj(
                    {
                        "schema": {
                            "type": "string",
                            "pattern": "^rapp-work-organization/1/",
                        },
                        "organization_rappid": ref("rappid"),
                        "world_id": ref("label"),
                        "parents": array(ref("wave"), 0, 64, unique=True),
                        "body": {"type": "object"},
                        "grants_authority": {"const": False},
                    }
                ),
                "payload_hash": ref("hash"),
                "frame_hash": ref("hash"),
                "prev": nullable(ref("hash")),
                "prev_wave": {"type": "null"},
                "sig": {"type": "string", "minLength": 1, "maxLength": 2048},
            }
        ),
    )


def documents():
    return {
        "common.schema.json": common_schema(),
        "activation-document.schema.json": activation_schema(),
        "mutation-lineage.schema.json": mutation_schema(),
        "artifact-bundle.schema.json": artifact_schema(),
        "learning-trace.schema.json": trace_schema(),
        "compatibility.schema.json": compatibility_schema(),
        "search.schema.json": search_schema(),
        "evolution.schema.json": evolution_schema(),
        "mutation-offer.schema.json": offer_schema(),
        "wild-handshake-binding.schema.json": bill_schema(),
        "frame.schema.json": frame_schema(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    expected = {name: pretty_bytes(value) for name, value in documents().items()}
    if args.write:
        SCHEMAS.mkdir(parents=True, exist_ok=True)
        for name, data in expected.items():
            (SCHEMAS / name).write_bytes(data)
    good = all((SCHEMAS / name).is_file() and (SCHEMAS / name).read_bytes() == data
               for name, data in expected.items())
    if args.check or not args.write:
        print("RAPP Work Organization/1 schemas: " + ("PASS" if good else "FAIL"))
    return int(not good)


if __name__ == "__main__":
    raise SystemExit(main())
