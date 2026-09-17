"""State-independent Work Organization/1 protocol validators."""

from __future__ import annotations

import json
from typing import Any

from workorg_common import (
    HASH_RE,
    Refusal,
    bounded_int,
    content_head,
    egg,
    exact_object,
    hash_value,
    particle_ref,
    require,
    safe_path,
    validate_plain_json,
    wave,
)
from workorg_artifact import (
    GENERIC_CEO_BYTES,
    GENERIC_CEO_PROFILE_SHA256,
    GENERIC_CEO_SHA256,
    GENERIC_CEO_SKILL_BYTES,
    GENERIC_CEO_SKILL_SHA256,
)


BILL_PROFILE_SHA256 = "0c52264b81bf88dd8555defa9363a23d8eb8ef85c3c12f66ddcaaabfc85a8882"
BILL_SOURCE_LENS_SHA256 = "679fff9531c0c8b13457d594f746c45da28925a7c1be40473e8ca00823db8671"
BILL_TARGET_FINALIZER_SHA256 = "c056339f90fdd4e604dbefa40291f1b7b22946d26749b36230bb3b29dd8e2296"
BILL_CONTRACT_SHA256 = "4ca6674ee491af0a09b6c333c9f24763face5f22462ce0b454a0ce4c84793932"


def validate_activation_document(value: Any) -> dict[str, Any]:
    document = exact_object(
        value,
        {
            "schema",
            "spec_sha256",
            "manifest_sha256",
            "brainstem_runtime_sha256",
            "organization_rappid",
            "world_id",
            "policy",
            "not_before_utc",
            "expires_utc",
            "signer_key_id",
            "revocation_status",
            "generic_ceo_agent_sha256",
            "generic_ceo_skill_sha256",
            "generic_ceo_artifact_profile_sha256",
        },
        "REFUSE_ACTIVATION",
    )
    require(
        document["schema"] == "rapp-work-organization/1/activation-document"
        and document["revocation_status"] == "active",
        "REFUSE_ACTIVATION",
        "Invalid activation identity or revocation state.",
    )
    for name in ("spec_sha256", "manifest_sha256", "brainstem_runtime_sha256"):
        hash_value(document[name], "REFUSE_ACTIVATION")
    particle_ref(document["policy"])
    require(
        document["generic_ceo_agent_sha256"] == GENERIC_CEO_SHA256
        and document["generic_ceo_skill_sha256"] == GENERIC_CEO_SKILL_SHA256
        and document["generic_ceo_artifact_profile_sha256"]
        == GENERIC_CEO_PROFILE_SHA256,
        "REFUSE_ACTIVATION",
        "Activation does not bind the exact generic CEO artifact.",
    )
    return document


def _ids(items: list[dict[str, Any]], key: str, code: str) -> set[str]:
    values = [content_head(item[key])["entry_id"] for item in items]
    require(len(values) == len(set(values)), code, "Duplicate inventory entry accounting.")
    return set(values)


def validate_mutation_lineage(value: Any) -> dict[str, Any]:
    item = exact_object(
        value,
        {
            "schema",
            "output_shape",
            "source_parents",
            "source_inventory",
            "successor_inventory",
            "successor_root",
            "forward",
            "reverse",
            "traits",
            "directionality",
            "reconstruction",
            "grants_authority",
        },
        "REFUSE_LINEAGE",
    )
    require(
        item["schema"] == "rapp-work-organization/1/mutation-lineage"
        and item["output_shape"] in {"sidecar", "full-successor", "hybrid"}
        and item["grants_authority"] is False,
        "REFUSE_LINEAGE",
        "Invalid lineage identity or authority.",
    )
    require(
        type(item["source_parents"]) is list and 1 <= len(item["source_parents"]) <= 8,
        "REFUSE_LINEAGE",
        "One to eight immutable source parents are required.",
    )
    for parent in item["source_parents"]:
        exact_object(
            parent,
            {"frame", "inventory", "repository_commit", "repository_tree"},
            "REFUSE_LINEAGE",
        )
        wave(parent["frame"])
        particle_ref(parent["inventory"])
    particle_ref(item["source_inventory"])
    particle_ref(item["successor_inventory"])
    egg(item["successor_root"])
    require(
        type(item["forward"]) is list
        and type(item["reverse"]) is list
        and item["forward"]
        and item["reverse"],
        "REFUSE_LINEAGE",
        "Complete forward and reverse maps are required.",
    )
    source_ids = _ids(item["forward"], "source", "REFUSE_FORWARD_MAP")
    successor_ids = _ids(item["reverse"], "successor", "REFUSE_REVERSE_MAP")
    forward_targets: list[str] = []
    reverse_sources: list[str] = []
    loss_classes: list[str] = []
    round_trip_claims: list[bool] = []
    for entry in item["forward"]:
        exact_object(
            entry,
            {
                "source",
                "disposition",
                "relation",
                "targets",
                "mutation_receipts",
                "inverse_material",
                "loss",
            },
            "REFUSE_FORWARD_MAP",
        )
        content_head(entry["source"])
        require(
            entry["disposition"] in {"retained", "replaced", "moved", "removed"},
            "REFUSE_FORWARD_MAP",
            "Invalid source disposition.",
        )
        require(type(entry["targets"]) is list, "REFUSE_FORWARD_MAP", "Target list required.")
        targets = [content_head(target) for target in entry["targets"]]
        if entry["disposition"] == "removed":
            require(not targets, "REFUSE_FORWARD_MAP", "Removed source cannot have a target.")
        else:
            require(targets, "REFUSE_FORWARD_MAP", "Nonremoved source requires a target.")
        forward_targets.extend(target["entry_id"] for target in targets)
        loss = exact_object(
            entry["loss"],
            {"class", "source_refs_preserved", "round_trip_claimed"},
            "REFUSE_LOSS",
        )
        require(loss["source_refs_preserved"] is True, "REFUSE_LOSS", "Source refs must survive.")
        loss_classes.append(loss["class"])
        round_trip_claims.append(loss["round_trip_claimed"])
        if loss["class"] != "lossless":
            require(
                loss["round_trip_claimed"] is False,
                "REFUSE_LOSS",
                "A lossy relation cannot claim round trip.",
            )
    for entry in item["reverse"]:
        exact_object(
            entry,
            {
                "successor",
                "ancestry",
                "sources",
                "derivation_receipts",
                "inverse_material",
                "loss",
            },
            "REFUSE_REVERSE_MAP",
        )
        content_head(entry["successor"])
        require(
            entry["ancestry"] in {"inherited", "derived", "new"},
            "REFUSE_REVERSE_MAP",
            "Invalid successor ancestry.",
        )
        require(type(entry["sources"]) is list, "REFUSE_REVERSE_MAP", "Source list required.")
        sources = [content_head(source) for source in entry["sources"]]
        if entry["ancestry"] == "new":
            require(not sources, "REFUSE_REVERSE_MAP", "New content cannot fabricate ancestry.")
        else:
            require(sources, "REFUSE_REVERSE_MAP", "Inherited or derived content needs ancestry.")
        reverse_sources.extend(source["entry_id"] for source in sources)
        loss = exact_object(
            entry["loss"],
            {"class", "source_refs_preserved", "round_trip_claimed"},
            "REFUSE_LOSS",
        )
        require(loss["source_refs_preserved"] is True, "REFUSE_LOSS", "Source refs must survive.")
        loss_classes.append(loss["class"])
        round_trip_claims.append(loss["round_trip_claimed"])
        if loss["class"] != "lossless":
            require(
                loss["round_trip_claimed"] is False,
                "REFUSE_LOSS",
                "A lossy relation cannot claim round trip.",
            )
    require(
        set(forward_targets) == successor_ids,
        "REFUSE_LINEAGE_COVERAGE",
        "Forward targets and reverse successor inventory differ.",
    )
    require(
        set(reverse_sources) <= source_ids,
        "REFUSE_LINEAGE_COVERAGE",
        "Reverse ancestry references an unknown source entry.",
    )
    reconstruction = exact_object(
        item["reconstruction"],
        {"status", "inverse_material", "reconstructor_sha256", "runtime_manifest_sha256"},
        "REFUSE_RECONSTRUCTION",
    )
    direction = item["directionality"]
    require(
        direction
        in {"bidirectional-lossless", "bidirectional-partial", "forward-only-lossy"},
        "REFUSE_LINEAGE",
        "Invalid directionality.",
    )
    if direction == "bidirectional-lossless":
        require(
            all(loss == "lossless" for loss in loss_classes)
            and all(round_trip_claims)
            and reconstruction["status"] in {"verified-contained", "verified-external"}
            and type(reconstruction["reconstructor_sha256"]) is str
            and type(reconstruction["runtime_manifest_sha256"]) is str,
            "REFUSE_LOSSLESS",
            "Lossless lineage requires complete verified reconstruction.",
        )
        hash_value(reconstruction["reconstructor_sha256"], "REFUSE_LOSSLESS")
        hash_value(reconstruction["runtime_manifest_sha256"], "REFUSE_LOSSLESS")
    else:
        require(
            any(loss != "lossless" for loss in loss_classes),
            "REFUSE_LOSS",
            "Lossy or partial directionality must declare an exact loss.",
        )
    validate_plain_json(item["traits"])
    return item


def validate_learning_trace(value: Any, *, require_closed: bool = True) -> dict[str, Any]:
    trace = exact_object(
        value,
        {
            "schema",
            "trace_id",
            "sanitizer_sha256",
            "reducer_sha256",
            "events",
            "ordered_event_hashes",
            "active_successor_invariants",
            "unresolved_corrections",
            "correction_fixture_set",
            "grants_authority",
        },
        "REFUSE_TRACE",
    )
    require(
        trace["schema"] == "rapp-work-organization/1/learning-trace"
        and trace["grants_authority"] is False,
        "REFUSE_TRACE",
        "Invalid trace identity or authority.",
    )
    hash_value(trace["trace_id"], "REFUSE_TRACE")
    hash_value(trace["sanitizer_sha256"], "REFUSE_TRACE")
    hash_value(trace["reducer_sha256"], "REFUSE_TRACE")
    particle_ref(trace["correction_fixture_set"])
    require(type(trace["events"]) is list and trace["events"], "REFUSE_TRACE", "Trace is empty.")
    event_ids: list[str] = []
    corrections: set[str] = set()
    invariants_by_correction: set[str] = set()
    invariant_events: set[str] = set()
    for sequence, event in enumerate(trace["events"]):
        exact_object(
            event,
            {
                "event_id",
                "trace_seq",
                "previous_event",
                "event_type",
                "actor_role",
                "authority",
                "supersedes",
                "source_receipts",
                "structured_content",
                "raw_content_persisted",
                "hidden_reasoning_present",
            },
            "REFUSE_TRACE_EVENT",
        )
        event_id = hash_value(event["event_id"], "REFUSE_TRACE_EVENT")
        bounded_int(event["trace_seq"], sequence, sequence, "REFUSE_TRACE_ORDER")
        if sequence == 0:
            require(
                event["previous_event"] is None,
                "REFUSE_TRACE_ORDER",
                "Trace genesis cannot name a predecessor.",
            )
        else:
            previous = wave(event["previous_event"])
            require(
                previous["hash"] == event_ids[-1],
                "REFUSE_TRACE_ORDER",
                "Trace predecessor does not match the prior event.",
            )
        require(
            type(event["supersedes"]) is list
            and all(
                type(reference) is str
                and HASH_RE.fullmatch(reference) is not None
                and reference in event_ids
                for reference in event["supersedes"]
            ),
            "REFUSE_TRACE_ORDER",
            "Superseded events must be earlier exact trace events.",
        )
        require(
            type(event["source_receipts"]) is list,
            "REFUSE_TRACE_SOURCE",
            "Source receipts must be an array.",
        )
        for receipt in event["source_receipts"]:
            exact_object(receipt, {"assurance", "receipt"}, "REFUSE_TRACE_SOURCE")
            require(
                receipt["assurance"]
                in {
                    "user-signed",
                    "host-attested-authenticated-user-input",
                    "host-measured-tool-result",
                    "host-measured-agent-result",
                    "withheld-private-source",
                },
                "REFUSE_TRACE_SOURCE",
                "Unknown source assurance.",
            )
            wave(receipt["receipt"])
        require(
            event["raw_content_persisted"] is False
            and event["hidden_reasoning_present"] is False,
            "REFUSE_TRACE_PRIVACY",
            "Raw content or hidden reasoning cannot enter the trace.",
        )
        event_ids.append(event_id)
        content = event["structured_content"]
        validate_plain_json(content)
        serialized = json.dumps(content, ensure_ascii=False, sort_keys=True)
        forbidden = (
            "/Users/",
            "Bearer ",
            "chain_of_thought",
            "hidden_reasoning",
            "raw_transcript",
            "access_token",
            "api_key",
        )
        require(
            not any(token in serialized for token in forbidden),
            "REFUSE_TRACE_PRIVACY",
            "Trace content contains prohibited private material.",
        )
        if event["event_type"] == "proposal":
            require(
                event["authority"] == "proposal-only",
                "REFUSE_TRACE_AUTHORITY",
                "Assistant proposals are never user authority.",
            )
        if event["event_type"] == "user-correction":
            require(
                event["actor_role"] == "user"
                and event["authority"] in {"user-signed", "host-attested-user-authority"}
                and type(event["supersedes"]) is list
                and bool(event["supersedes"]),
                "REFUSE_TRACE_AUTHORITY",
                "Correction requires authenticated user authority and an exact predecessor.",
            )
            corrections.add(event_id)
        if event["event_type"] == "successor-invariant":
            require(
                event["authority"] == "derived-from-authoritative-correction"
                and type(content) is dict
                and type(content.get("correction_event")) is str,
                "REFUSE_TRACE_INVARIANT",
                "Successor invariant requires correction ancestry.",
            )
            invariants_by_correction.add(content["correction_event"])
            invariant_events.add(event_id)
    require(
        trace["ordered_event_hashes"] == event_ids,
        "REFUSE_TRACE_ORDER",
        "Trace summary drift or event omission detected.",
    )
    require(
        corrections <= invariants_by_correction,
        "REFUSE_TRACE_INVARIANT",
        "Every correction requires a successor invariant.",
    )
    require(
        set(trace["active_successor_invariants"]) <= invariant_events,
        "REFUSE_TRACE_INVARIANT",
        "Active invariant commitments must name invariant events.",
    )
    if require_closed:
        require(
            trace["unresolved_corrections"] == [],
            "REFUSE_TRACE_OPEN",
            "Compatibility cannot lock with unresolved corrections.",
        )
    return trace


def validate_search(value: Any) -> dict[str, Any]:
    search = exact_object(
        value,
        {
            "schema",
            "ancestor_frames",
            "ancestor_inventory",
            "declared_use_case",
            "scenario_corpus",
            "holdout_commitment",
            "bounds",
            "lens_dimensions",
            "candidates",
            "pareto_frontier",
            "selected",
            "stop_reason",
            "grants_authority",
        },
        "REFUSE_SEARCH",
    )
    require(
        search["schema"] == "rapp-work-organization/1/search"
        and search["grants_authority"] is False,
        "REFUSE_SEARCH",
        "Invalid search identity or authority.",
    )
    for parent in search["ancestor_frames"]:
        wave(parent)
    particle_ref(search["ancestor_inventory"])
    particle_ref(search["scenario_corpus"])
    particle_ref(search["holdout_commitment"])
    bounds = search["bounds"]
    exact_object(
        bounds,
        {
            "max_lenses",
            "max_candidates",
            "max_cross_parents",
            "max_cross_traits",
            "max_depth",
            "max_rounds",
            "max_work_units",
            "max_artifact_bytes",
        },
        "REFUSE_SEARCH_BOUNDS",
    )
    require(
        bounded_int(bounds["max_lenses"], 1, 64) == bounds["max_lenses"]
        and bounded_int(bounds["max_candidates"], 1, 256) == bounds["max_candidates"]
        and bounded_int(bounds["max_cross_parents"], 1, 8) == bounds["max_cross_parents"]
        and bounded_int(bounds["max_cross_traits"], 1, 64) == bounds["max_cross_traits"]
        and bounded_int(bounds["max_depth"], 1, 32) == bounds["max_depth"]
        and bounded_int(bounds["max_rounds"], 1, 16) == bounds["max_rounds"]
        and bounded_int(bounds["max_work_units"], 1, 1000000)
        == bounds["max_work_units"]
        and bounded_int(bounds["max_artifact_bytes"], 1, 1 << 30)
        == bounds["max_artifact_bytes"],
        "REFUSE_SEARCH_BOUNDS",
        "Search root bounds exceed the protocol ceiling.",
    )
    require(
        len(search["lens_dimensions"]) <= bounds["max_lenses"]
        and len(search["candidates"]) <= bounds["max_candidates"]
        and len(search["pareto_frontier"]) <= 32,
        "REFUSE_SEARCH_BOUNDS",
        "Search exceeded its frozen root bounds.",
    )
    candidate_ids = {candidate["candidate_id"] for candidate in search["candidates"]}
    for candidate_id in candidate_ids:
        hash_value(candidate_id, "REFUSE_SEARCH")
    require(
        len(candidate_ids) == len(search["candidates"]),
        "REFUSE_SEARCH",
        "Duplicate candidate identifiers.",
    )
    require(
        search["selected"] is None or search["selected"] in candidate_ids,
        "REFUSE_SEARCH",
        "Selected candidate is not part of the retained search.",
    )
    return search


def validate_evolution(value: Any) -> dict[str, Any]:
    record = exact_object(
        value,
        {
            "schema",
            "level",
            "parents",
            "candidate",
            "scenario_corpus",
            "hidden_holdout",
            "controlled_mutants",
            "canonical_evaluation",
            "canary",
            "promotion",
            "adoption",
            "rollback_target",
            "automatic_promotion",
            "generated_tests_self_certify",
            "grants_authority",
        },
        "REFUSE_EVOLUTION",
    )
    require(
        record["schema"] == "rapp-work-organization/1/evolution"
        and record["level"]
        in {"handshake", "implementation", "seed-trait", "protocol-successor"}
        and record["automatic_promotion"] is False
        and record["generated_tests_self_certify"] is False
        and record["grants_authority"] is False,
        "REFUSE_EVOLUTION",
        "Evolution evidence cannot self-promote or self-certify.",
    )
    for parent in record["parents"]:
        wave(parent)
    egg(record["candidate"])
    particle_ref(record["scenario_corpus"])
    particle_ref(record["hidden_holdout"])
    particle_ref(record["controlled_mutants"])
    wave(record["canonical_evaluation"])
    wave(record["canary"])
    wave(record["rollback_target"])
    return record


def validate_bill_binding(value: Any) -> dict[str, Any]:
    binding = exact_object(
        value,
        {
            "schema",
            "id",
            "status",
            "embedded_private_content",
            "handshake_profile",
            "source_lens",
            "target_finalizer",
            "contract",
            "source",
            "proof",
            "generic_ceo_agent",
            "authority",
        },
        "REFUSE_BILL_BINDING",
    )
    require(
        binding["schema"] == "rapp-work-organization/1/wild-handshake-binding"
        and binding["id"] == "softwarecoellc-vteam-hive"
        and binding["status"] == "owner-approved-private"
        and binding["embedded_private_content"] is False
        and binding["authority"] is False,
        "REFUSE_BILL_BINDING",
        "Invalid Bill handshake binding.",
    )
    expected = {
        "handshake_profile": (BILL_PROFILE_SHA256, 5351),
        "source_lens": (BILL_SOURCE_LENS_SHA256, 11302),
        "target_finalizer": (BILL_TARGET_FINALIZER_SHA256, 11461),
        "contract": (BILL_CONTRACT_SHA256, 34226),
    }
    for name, (digest, size) in expected.items():
        pin = exact_object(
            binding[name],
            {"sha256", "bytes", "role", "embedded"},
            "REFUSE_BILL_BINDING",
        )
        require(
            pin["sha256"] == digest
            and pin["bytes"] == size
            and pin["embedded"] is False,
            "REFUSE_BILL_BINDING",
            f"Bill {name} pin differs from the approved private source.",
        )
    source = binding["source"]
    require(
        source["commit"] == "f66da3d879b53a439bc87de764d79f68ceec048a"
        and source["verified_frames"] == 2
        and source["verified_artifacts"] == 9,
        "REFUSE_BILL_BINDING",
        "Bill source qualification evidence changed.",
    )
    require(
        binding["proof"]["double_hotload"] == "verified-local"
        and binding["proof"]["model_calls_static_runtime"] == 0
        and binding["generic_ceo_agent"]
        == {
            "status": "verified",
            "sha256": GENERIC_CEO_SHA256,
            "bytes": GENERIC_CEO_BYTES,
            "skill_sha256": GENERIC_CEO_SKILL_SHA256,
            "skill_bytes": GENERIC_CEO_SKILL_BYTES,
            "artifact_profile_sha256": GENERIC_CEO_PROFILE_SHA256,
        },
        "REFUSE_BILL_BINDING",
        "The fixture must bind the exact verified generic CEO artifact.",
    )
    return binding
