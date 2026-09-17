#!/usr/bin/env python3
"""Structural and cross-record validation for rapp-hive-autobest/1."""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[1]
HIVE_REFERENCE = ROOT.parents[1] / "rapp-hive" / "1" / "reference"
if str(HIVE_REFERENCE) not in sys.path:
    sys.path.insert(0, str(HIVE_REFERENCE))

import rapp as R  # noqa: E402
from rapp_profile import (  # noqa: E402
    authoritative_frame_payload,
    canonical_object,
    particle_hash,
    require,
)


PROFILE = "rapp-hive-autobest/1"
COMPATIBILITY_SCHEMA = f"{PROFILE}-compatibility"
EXHAUST_SCHEMA = f"{PROFILE}-exhaust"
ASSIGNMENT_SCHEMA = f"{PROFILE}-assignment"
CHECKPOINT_SCHEMA = f"{PROFILE}-checkpoint"
DECISION_SCHEMA = f"{PROFILE}-decision"
VIEW_SCHEMA = f"{PROFILE}-view"
BUNDLE_SCHEMA = f"{PROFILE}-artifact-bundle"
LINEAGE_SCHEMA = f"{PROFILE}-mutation-lineage"
TRACE_SCHEMA = f"{PROFILE}-learning-trace"
SEARCH_SCHEMA = f"{PROFILE}-n-lens-search"
OFFER_SCHEMA = f"{PROFILE}-mutation-offer"
CATALOG_SCHEMA = f"{PROFILE}-handshake-catalog"
EVOLUTION_SCHEMA = f"{PROFILE}-evolution-proposal"
FIXTURE_SCHEMA = f"{PROFILE}-fixture-binding"
CEO_BINDING_SCHEMA = f"{PROFILE}-ceo-binding"

KIND_SCHEMAS = {
    "hive-autobest.compatibility": COMPATIBILITY_SCHEMA,
    "hive-autobest.exhaust": EXHAUST_SCHEMA,
    "hive-autobest.mutation-offer": OFFER_SCHEMA,
    "hive-autobest.evolution": EVOLUTION_SCHEMA,
}

SCHEMA = json.loads((ROOT / "schema.json").read_text(encoding="utf-8"))
VALIDATOR = Draft202012Validator(SCHEMA, format_checker=FormatChecker())


def _hash_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _address_key(value: dict[str, Any]) -> tuple[str, str]:
    return value["space"], value["hash"]


def _sorted_unique(values: list[Any], key, where: str) -> None:
    keys = [key(value) for value in values]
    require(keys == sorted(set(keys)), f"{where}: must be unique and sorted")


def _schema_validate(document: dict[str, Any]) -> None:
    errors = sorted(
        VALIDATOR.iter_errors(document),
        key=lambda error: (list(error.absolute_path), error.message),
    )
    if errors:
        first = errors[0]
        location = ".".join(str(item) for item in first.absolute_path) or "<root>"
        raise ValueError(f"schema {location}: {first.message}")


def _validate_endpoint(endpoint: dict[str, Any], where: str) -> None:
    capabilities = endpoint["capabilities"]
    _sorted_unique(capabilities, lambda value: value["id"], f"{where}.capabilities")
    head = endpoint["head"]
    if endpoint["head_status"] == "verified":
        require(head is not None, f"{where}: verified head is missing")
        require(
            head["stream_id"] == endpoint["endpoint_rappid"]
            or head["stream_id"].startswith(endpoint["endpoint_rappid"] + ":"),
            f"{where}: head stream is outside endpoint identity",
        )
    else:
        require(head is None, f"{where}: unavailable head must be null")
    pin = endpoint["profile_pin"]
    require(
        (pin["status"] == "verified") == (pin["value"] is not None),
        f"{where}: profile pin status/value mismatch",
    )


def _validate_source_vector(values: list[dict[str, Any]], where: str) -> None:
    _sorted_unique(
        values,
        lambda value: (value["head"]["utc"], value["head"]["frame_hash"]),
        where,
    )
    dimensions = [value["dimension_rappid"] for value in values]
    require(len(dimensions) == len(set(dimensions)), f"{where}: duplicate dimension")
    for entry in values:
        stream = entry["head"]["stream_id"]
        dimension = entry["dimension_rappid"]
        require(
            stream == dimension or stream.startswith(dimension + ":"),
            f"{where}: head stream is outside dimension identity",
        )


def validate_compatibility(document: dict[str, Any]) -> str:
    _validate_endpoint(document["source"], "compatibility.source")
    _validate_endpoint(document["target"], "compatibility.target")
    _validate_source_vector(document["source_vector"], "compatibility.source_vector")
    mapping = document["mapping"]
    _sorted_unique(mapping["directions"], lambda value: value, "compatibility.mapping.directions")
    _sorted_unique(mapping["gaps"], lambda value: value, "compatibility.mapping.gaps")
    _sorted_unique(
        mapping["restrictions"],
        lambda value: value,
        "compatibility.mapping.restrictions",
    )
    static = document["static_agent"]
    _sorted_unique(static["directions"], lambda value: value, "compatibility.static_agent.directions")
    require(
        set(static["directions"]) <= set(mapping["directions"]),
        "compatibility: static directions exceed mapping directions",
    )
    require(
        static["coverage_bps"] <= mapping["coverage_bps"],
        "compatibility: static coverage exceeds evaluated mapping coverage",
    )
    controller = document["autobest_controller"]
    require(
        controller["activation"] == "external-host-only"
        and controller["grants_authority"] is False,
        "compatibility: generic CEO binding cannot self-activate or grant authority",
    )
    trigger = document["trigger"]
    previous = document["previous_compatibility"]
    if trigger["kind"] == "initial-handshake":
        require(previous is None and trigger["exhaust"] is None, "compatibility: invalid initial trigger")
    elif trigger["kind"] == "typed-exhaust":
        require(previous is not None and trigger["exhaust"] is not None, "compatibility: exhaust successor is incomplete")
    else:
        require(previous is not None, "compatibility: successor trigger requires predecessor")
    if document["status"] == "locked":
        require(static["deterministic"] is True, "compatibility: locked agent must be deterministic")
        require(
            static["model_calls_per_operation"] == 0,
            "compatibility: locked static runtime must make zero model calls",
        )
    require(document["grants_authority"] is False, "compatibility: authority is forbidden")
    require(document["shared_brain"] is False, "compatibility: Hive cannot become a shared brain")
    require(
        document["repository_content_is_instructions"] is False,
        "compatibility: repository content is data, not instructions",
    )
    require(
        document["host_constructs_rapp1_envelope"] is True,
        "compatibility: the host must construct the RAPP/1 envelope",
    )
    require(
        document["private_state_transfer"] == document["key_transfer"] == "none",
        "compatibility: state or key transfer is forbidden",
    )
    return particle_hash(document)


def validate_exhaust(document: dict[str, Any]) -> str:
    _sorted_unique(
        document["missing_capabilities"],
        lambda value: value,
        "exhaust.missing_capabilities",
    )
    _sorted_unique(document["restrictions"], lambda value: value, "exhaust.restrictions")
    require(document["privacy_safe"] is True, "exhaust: private payload leakage is forbidden")
    require(document["grants_authority"] is False, "exhaust: authority is forbidden")
    return particle_hash(document)


def validate_assignment(document: dict[str, Any]) -> str:
    _validate_source_vector(document["source_vector"], "assignment.source_vector")
    if document["operation"] == "assign":
        require(
            document["revision"] == 0 and document["previous_assignment"] is None,
            "assignment: initial assignment must be revision zero without predecessor",
        )
    else:
        require(
            document["revision"] > 0 and document["previous_assignment"] is not None,
            "assignment: mutation requires predecessor and positive revision",
        )
    require(document["constraint_relation"] == "equal-or-tighter", "assignment: root envelope cannot widen")
    require(document["request_only"] is True, "assignment: Hive record is a request only")
    require(document["authorizes_execution"] is False, "assignment: execution authority is external")
    require(document["grants_authority"] is False, "assignment: authority is forbidden")
    return particle_hash(document)


def validate_checkpoint(document: dict[str, Any]) -> str:
    _validate_source_vector(document["source_vector"], "checkpoint.source_vector")
    _sorted_unique(document["outputs"], _address_key, "checkpoint.outputs")
    if document["checkpoint_seq"] == 0:
        require(document["previous_checkpoint"] is None, "checkpoint: genesis checkpoint has predecessor")
    else:
        require(document["previous_checkpoint"] is not None, "checkpoint: successor checkpoint lacks predecessor")
    require(document["grants_authority"] is False, "checkpoint: evidence is not authority")
    return particle_hash(document)


def validate_decision(document: dict[str, Any]) -> str:
    _validate_source_vector(document["parents"], "decision.parents")
    _sorted_unique(document["selected_checkpoints"], _address_key, "decision.selected_checkpoints")
    _sorted_unique(document["rejected_checkpoints"], _address_key, "decision.rejected_checkpoints")
    selected = {_address_key(value) for value in document["selected_checkpoints"]}
    rejected = {_address_key(value) for value in document["rejected_checkpoints"]}
    require(not selected & rejected, "decision: one checkpoint cannot be selected and rejected")
    if document["mode"] == "unresolved":
        require(
            not selected and document["result_checkpoint"] is None,
            "decision: unresolved result cannot silently select a winner",
        )
    if document["mode"] == "compose-compatible":
        require(
            document["crossing_lens"] is not None
            and len(document["parents"]) >= 2
            and document["result_checkpoint"] is not None,
            "decision: composed result requires Crossing Lens and complete parents",
        )
    require(document["authorizes_adoption"] is False, "decision: AutoBest evidence cannot adopt")
    require(document["grants_authority"] is False, "decision: authority is forbidden")
    return particle_hash(document)


def validate_view(document: dict[str, Any]) -> str:
    _validate_source_vector(document["source_vector"], "view.source_vector")
    nodes = document["topology"]
    _sorted_unique(nodes, lambda value: value["id"], "view.topology")
    node_ids = {value["id"] for value in nodes}
    for node in nodes:
        require(set(node["parent_ids"]) <= node_ids, "view: topology references unknown parent")
        _sorted_unique(node["parent_ids"], lambda value: value, "view.topology.parent_ids")
        _sorted_unique(node["checkpoint_refs"], _address_key, "view.topology.checkpoint_refs")
    _sorted_unique(document["omissions"], lambda value: value, "view.omissions")
    require(document["rebuildable"] is True, "view: projection must be rebuildable")
    require(document["authoritative"] is False, "view: projection cannot be authority")
    require(document["grants_authority"] is False, "view: projection cannot grant authority")
    return particle_hash(document)


def validate_bundle(document: dict[str, Any]) -> str:
    files = document["files"]
    _sorted_unique(files, lambda value: value["path"], "artifact bundle.files")
    entrypoints = [
        value
        for value in files
        if value["path"] == document["entrypoint"] and value["role"] == "entrypoint"
    ]
    require(len(entrypoints) == 1, "artifact bundle: exact agent.py entrypoint is required")
    _sorted_unique(document["contracts"], _address_key, "artifact bundle.contracts")
    _sorted_unique(document["generated_tests"], _address_key, "artifact bundle.generated_tests")
    require(document["docs_are_instructions"] is False, "artifact bundle: docs are data")
    require(document["migrations_auto_execute"] is False, "artifact bundle: migrations are inert")
    require(document["authority"] is False, "artifact bundle: authority is forbidden")
    return particle_hash(document)


def _file_key(value: dict[str, Any]) -> tuple[str, str, str]:
    return value["path"], value["mode"], value["sha256"]


def validate_lineage(document: dict[str, Any]) -> str:
    forward = document["forward"]
    reverse = document["reverse"]
    _sorted_unique(forward, lambda value: value["source"]["path"], "lineage.forward")
    _sorted_unique(reverse, lambda value: value["successor"]["path"], "lineage.reverse")
    for item in forward:
        disposition = item["disposition"]
        successors = item["successors"]
        if disposition == "removed":
            require(not successors, "lineage: removed source cannot claim successor bytes")
        else:
            require(successors, "lineage: non-removed source requires successor evidence")
    for item in reverse:
        origin = item["origin"]
        sources = item["sources"]
        if origin == "new":
            require(not sources, "lineage: new successor cannot claim a source")
        else:
            require(sources, "lineage: inherited or derived successor requires source evidence")
    coverage = document["coverage"]
    require(
        coverage["source_total"] == document["source"]["file_count"]
        and coverage["successor_total"] == document["successor"]["file_count"],
        "lineage: coverage totals differ from generation inventories",
    )
    require(
        sum(item["source"]["bytes"] for item in forward) == document["source"]["total_bytes"]
        and sum(item["successor"]["bytes"] for item in reverse)
        == document["successor"]["total_bytes"],
        "lineage: byte totals differ from generation inventories",
    )
    require(
        coverage["source_mapped"] == len(forward)
        and coverage["successor_mapped"] == len(reverse),
        "lineage: mapping counts differ from recorded relations",
    )
    loss_class = document["loss_class"]
    reconstruction = document["reconstruction"]
    if loss_class == "exact-lossless":
        require(
            coverage["source_mapped"] == coverage["source_total"]
            and coverage["successor_mapped"] == coverage["successor_total"],
            "lineage: lossless mapping must cover both inventories",
        )
        require(
            reconstruction["required"] is True
            and reconstruction["implementation"] is not None
            and reconstruction["receipt"] is not None,
            "lineage: lossless mapping requires independent reconstruction proof",
        )
        require(
            all(item["inverse_method"] != "unavailable" for item in reverse),
            "lineage: lossless mapping cannot contain unavailable inverse material",
        )
    if loss_class == "declared-lossy":
        require(
            any(item["inverse_method"] == "unavailable" for item in reverse)
            or coverage["source_mapped"] < coverage["source_total"],
            "lineage: lossy mapping must expose the loss",
        )
    _sorted_unique(document["selected_traits"], lambda value: value["id"], "lineage.selected_traits")
    _sorted_unique(document["omitted_traits"], lambda value: value["id"], "lineage.omitted_traits")
    return particle_hash(document)


def _event_hash(event: dict[str, Any]) -> str:
    return particle_hash({key: value for key, value in event.items() if key != "event_hash"})


def validate_trace(document: dict[str, Any]) -> str:
    events = document["events"]
    require(
        [event["index"] for event in events] == list(range(len(events))),
        "learning trace: event indexes must be contiguous",
    )
    previous = None
    corrections = []
    for event in events:
        require(
            event["previous_event_hash"] == previous,
            "learning trace: event order commitment mismatch",
        )
        require(event["event_hash"] == _event_hash(event), "learning trace: event hash mismatch")
        if event["actor_class"] == "assistant":
            require(
                event["authority_class"] == "proposal-only",
                "learning trace: assistant proposal cannot become user authority",
            )
        if event["event_type"] == "user-correction":
            corrections.append(event)
            require(
                event["actor_class"] == "user"
                and event["authority_class"] in {"observed-user-input", "user-decision"}
                and event["supersedes_event_ids"]
                and event["successor_invariant_ids"],
                "learning trace: correction lacks authority class or successor invariant",
            )
        previous = event["event_hash"]
    require(document["trace_root_hash"] == previous, "learning trace: root differs from final event")
    if corrections:
        require(
            document["correction_coverage_bps"] == 10000,
            "learning trace: every correction must enter regression evidence",
        )
    return particle_hash(document)


def validate_search(document: dict[str, Any]) -> str:
    bounds = document["bounds"]
    lenses = document["lenses"]
    candidates = document["candidates"]
    crosses = document["crosses"]
    require(len(lenses) <= bounds["max_lenses"], "N-Lens search: lens bound exceeded")
    require(len(candidates) <= bounds["max_candidates"], "N-Lens search: candidate bound exceeded")
    _sorted_unique(lenses, lambda value: value["id"], "N-Lens search.lenses")
    _sorted_unique(candidates, lambda value: value["id"], "N-Lens search.candidates")
    _sorted_unique(crosses, lambda value: value["id"], "N-Lens search.crosses")
    lens_ids = {value["id"] for value in lenses}
    candidate_ids = {value["id"] for value in candidates}
    for value in candidates:
        require(value["lens_id"] in lens_ids, "N-Lens search: candidate references unknown lens")
        require(set(value["parents"]) <= candidate_ids, "N-Lens search: unknown candidate parent")
    for value in crosses:
        require(
            len(value["candidate_ids"]) <= bounds["max_cross_size"],
            "N-Lens search: cross-size bound exceeded",
        )
        require(
            set(value["candidate_ids"]) <= candidate_ids
            and value["output_candidate_id"] in candidate_ids,
            "N-Lens search: cross references unknown candidate",
        )
    selection = document["selection"]
    require(
        set(selection["selected_candidates"]) <= candidate_ids,
        "N-Lens search: selection references unknown candidate",
    )
    if selection["mode"] == "unresolved":
        require(
            not selection["selected_candidates"] and not selection["selected_traits"],
            "N-Lens search: unresolved selection cannot silently choose a winner",
        )
    require(document["grants_authority"] is False, "N-Lens search: authority is forbidden")
    return particle_hash(document)


def validate_offer(document: dict[str, Any]) -> str:
    _sorted_unique(document["source_parents"], _address_key, "mutation offer.source_parents")
    _sorted_unique(document["selected_traits"], lambda value: value, "mutation offer.selected_traits")
    _sorted_unique(document["omitted_traits"], lambda value: value, "mutation offer.omitted_traits")
    require(document["grants_authority"] is False, "mutation offer: PR transport is not authority")
    return particle_hash(document)


def validate_catalog(document: dict[str, Any]) -> str:
    entries = document["entries"]
    _sorted_unique(entries, lambda value: (value["id"], value["version"]), "handshake catalog.entries")
    for entry in entries:
        _sorted_unique(entry["gaps"], lambda value: value, "handshake catalog.entry.gaps")
    require(document["grants_authority"] is False, "handshake catalog: inclusion is not activation")
    return particle_hash(document)


def validate_evolution(document: dict[str, Any]) -> str:
    _sorted_unique(document["parents"], _address_key, "evolution.parents")
    generator = document["generator"]
    verifier = document["verifier"]
    require(
        (generator["sha256"], generator["runtime_sha256"], generator["policy_sha256"])
        != (verifier["sha256"], verifier["runtime_sha256"], verifier["policy_sha256"]),
        "evolution: generator and independent verifier must not collapse",
    )
    require(
        _address_key(document["candidate_tests"]) != _address_key(document["independent_tests"]),
        "evolution: candidate tests cannot self-certify",
    )
    require(document["adoption_authorized"] is False, "evolution: promotion is never automatic")
    return particle_hash(document)


def validate_fixture_binding(document: dict[str, Any]) -> str:
    require(document["authority"] is False, "fixture binding: provenance is not authority")
    return particle_hash(document)


def validate_ceo_binding(document: dict[str, Any]) -> str:
    require(document["grants_authority"] is False, "CEO binding: authority is forbidden")
    require(
        document["authority_from_presence"] is False,
        "CEO binding: presence cannot become authority",
    )
    require(document["shared_brain"] is False, "CEO binding: Hive cannot become a shared brain")
    require(
        document["private_state_transfer"] == document["key_transfer"] == "none",
        "CEO binding: private state or keys cannot transfer",
    )
    return particle_hash(document)


VALIDATORS = {
    COMPATIBILITY_SCHEMA: validate_compatibility,
    EXHAUST_SCHEMA: validate_exhaust,
    ASSIGNMENT_SCHEMA: validate_assignment,
    CHECKPOINT_SCHEMA: validate_checkpoint,
    DECISION_SCHEMA: validate_decision,
    VIEW_SCHEMA: validate_view,
    BUNDLE_SCHEMA: validate_bundle,
    LINEAGE_SCHEMA: validate_lineage,
    TRACE_SCHEMA: validate_trace,
    SEARCH_SCHEMA: validate_search,
    OFFER_SCHEMA: validate_offer,
    CATALOG_SCHEMA: validate_catalog,
    EVOLUTION_SCHEMA: validate_evolution,
    FIXTURE_SCHEMA: validate_fixture_binding,
    CEO_BINDING_SCHEMA: validate_ceo_binding,
}


def validate(document: dict[str, Any]) -> str:
    canonical_object(document, "rapp-hive-autobest/1 record")
    _schema_validate(document)
    schema = document.get("schema")
    require(schema in VALIDATORS, "rapp-hive-autobest/1: unknown schema")
    return VALIDATORS[schema](document)


def authorize_frame(
    frame: dict[str, Any],
    *,
    head: dict[str, Any] | None,
    stream_id: str,
    registered_kinds: set[str],
    signature_verifier,
    authorization_verifier,
) -> dict[str, Any]:
    schema = KIND_SCHEMAS.get(frame.get("kind"))
    require(schema is not None, "rapp-hive-autobest/1: unsupported frame kind")
    payload = authoritative_frame_payload(
        frame,
        expected_schema=schema,
        purpose="rapp-hive-autobest/1",
        head=head,
        stream_id=stream_id,
        registered_kinds=registered_kinds,
        signature_verifier=signature_verifier,
        authorization_verifier=authorization_verifier,
    )
    validate(payload)
    return payload


def validate_bill_fixture(fixture_root: Path) -> dict[str, Any]:
    binding = json.loads((fixture_root / "binding.json").read_text(encoding="utf-8"))
    validate(binding)
    for section in ("handshake", "source_lens", "target_finalizer"):
        record = binding[section]
        raw = (fixture_root / record["path"]).read_bytes()
        require(len(raw) == record["bytes"], f"Bill fixture: {section} byte count mismatch")
        require(_hash_bytes(raw) == record["sha256"], f"Bill fixture: {section} hash mismatch")
    package = fixture_root / "static"
    static = binding["static_package"]
    expected = {
        "manifest.json": static["manifest_sha256"],
        "agent.py": static["agent_sha256"],
        "compatibility-frame.json": static["compatibility_frame_sha256"],
        "generation-receipt.json": static["generation_receipt_sha256"],
        "public-identity.json": static["public_identity_sha256"],
    }
    for path, digest in expected.items():
        require(_hash_bytes((package / path).read_bytes()) == digest, f"Bill fixture: {path} hash mismatch")
    manifest = json.loads((package / "manifest.json").read_text(encoding="utf-8"))
    require(manifest["private_keys_included"] is False, "Bill fixture: private key included")
    require(manifest["native_session_included"] is False, "Bill fixture: native session included")
    require(manifest["model_calls_per_translation"] == 0, "Bill fixture: static model calls")
    files = {entry["path"]: entry for entry in manifest["files"]}
    require(set(files) == {"agent.py", "compatibility-frame.json", "generation-receipt.json", "public-identity.json"},
            "Bill fixture: incomplete static package")
    for path, record in files.items():
        raw = (package / path).read_bytes()
        require(len(raw) == record["bytes"] and _hash_bytes(raw) == record["sha256"],
                f"Bill fixture: manifest differs for {path}")
    require(not (package / "private-key.pem").exists(), "Bill fixture: private key file present")
    identity = json.loads((package / "public-identity.json").read_text(encoding="utf-8"))
    frame = json.loads((package / "compatibility-frame.json").read_text(encoding="utf-8"))
    spki = base64.b64decode(identity["spki_der_b64"], validate=True)
    ok, step, why = R.verify_frame(
        frame,
        stream_id_of_record=frame["stream_id"],
        signature_verifier=lambda unsigned, signature: R.verify_detached_jws(
            unsigned,
            signature,
            spki,
            identity["rappid"],
        ),
    )
    require(ok, f"Bill fixture: signed compatibility frame refused at {step}: {why}")
    receipt = json.loads((package / "generation-receipt.json").read_text(encoding="utf-8"))
    agent = (package / "agent.py").read_bytes()
    require(receipt["compatibility"]["frame_hash"] == frame["frame_hash"],
            "Bill fixture: generation receipt points to another frame")
    require(receipt["agent_sha256"] == _hash_bytes(agent) and receipt["agent_bytes"] == len(agent),
            "Bill fixture: generation receipt differs from static agent")
    return {
        "binding_hash": particle_hash(binding),
        "compatibility_frame_hash": frame["frame_hash"],
        "static_agent_sha256": _hash_bytes(agent),
        "verified_frames": binding["source"]["verified_frames"],
        "verified_artifacts": binding["source"]["verified_artifacts"],
    }


def validate_ceo_fixture(fixture_root: Path) -> dict[str, Any]:
    binding = json.loads((fixture_root / "binding.json").read_text(encoding="utf-8"))
    validate(binding)
    manifest_raw = (fixture_root / "manifest.json").read_bytes()
    manifest = json.loads(manifest_raw)
    require(
        _hash_bytes(manifest_raw) == binding["manifest"]["sha256"]
        and len(manifest_raw) == binding["manifest"]["bytes"],
        "CEO fixture: manifest bytes differ",
    )
    require(
        particle_hash(manifest) == binding["profile_artifact"]["hash"],
        "CEO fixture: profile artifact address differs",
    )
    require(
        manifest["schema"] == "rapp-hive-autobest/1-ceo-profile-artifact"
        and manifest["capability_id"] == binding["capability_id"]
        and manifest["profile"] == binding["profile"]
        and manifest["authority"] is False,
        "CEO fixture: invalid profile artifact",
    )
    files = {record["path"]: record for record in manifest["files"]}
    require(set(files) == {"agent.py", "SKILL.md"}, "CEO fixture: incomplete exact-byte package")
    for section, path in (("agent", "agent.py"), ("skill", "SKILL.md")):
        record = binding[section]
        raw = (fixture_root / path).read_bytes()
        require(
            record["path"] == path
            and len(raw) == record["bytes"] == files[path]["bytes"]
            and _hash_bytes(raw) == record["sha256"] == files[path]["sha256"],
            f"CEO fixture: {path} bytes differ",
        )
    properties = manifest["properties"]
    require(
        properties["deterministic"] is True
        and properties["inert"] is True
        and properties["authority"] is False
        and properties["activation"] == "external-host-only"
        and properties["authority_from_presence"] is False
        and properties["normal_traffic_model_calls"] == 0
        and properties["shared_brain"] is False
        and properties["private_state_transfer"] == "none"
        and properties["key_transfer"] == "none",
        "CEO fixture: unsafe capability property",
    )
    return {
        "binding_hash": particle_hash(binding),
        "profile_artifact_hash": particle_hash(manifest),
        "agent_sha256": binding["agent"]["sha256"],
        "skill_sha256": binding["skill"]["sha256"],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("document")
    arguments = parser.parse_args(argv)
    document = json.loads(Path(arguments.document).read_text(encoding="utf-8"))
    print(
        json.dumps(
            {
                "status": "payload-conformant",
                "authenticated": False,
                "payload_hash": validate(document),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError) as error:
        print(json.dumps({"status": "refused", "error": str(error)}, sort_keys=True), file=sys.stderr)
        raise SystemExit(1)
