#!/usr/bin/env python3
"""Self-contained deterministic AutoBest planner/reducer for inert capability Tiles."""

from __future__ import annotations

import base64
import binascii
import hashlib
import itertools
import json
import sys


__manifest__ = {
    "schema": "rapp-agent/1.0",
    "name": "@kody-w/microsol_autobest",
    "version": "3.0.0",
    "display_name": "RAPP AutoBest",
    "description": (
        "Generic deterministic Delegation and Crossing Lens planner plus an inert "
        "microsol-ceo lifecycle and user-takeover reducer for verified caller state."
    ),
    "author": "kody-w",
    "tags": [
        "autobest",
        "brainstem",
        "delegation",
        "crossing",
        "microsol-ceo",
        "user-control",
        "hive-translation",
        "interop",
        "compatibility-frame",
        "planner",
    ],
    "category": "workflow",
    "quality_tier": "private",
    "access": "private",
    "dependencies": [],
    "requires_env": [],
    "single_file": True,
    "stdlib_only": True,
    "deterministic": True,
    "inert": True,
    "runtime": False,
    "record_role": "evidence",
    "manifest_role": "evidence-only",
    "authority": False,
    "authority_source": "external-host",
    "rapp1_role": "core-compatibility-substrate",
    "rapp1_compatibility_required": True,
    "rapp1_application_home": False,
    "rapp1_endpoint_adaptation": "single-compatibility-application-frame",
    "compatibility_learning": "brainstem-double-hotload",
    "dynamic_lens_operation_scope": "universal-framed-application-content",
    "compatibility_runtime": "locked-static-transducer",
    "static_field_map_ir_normative": False,
    "captured_arbitrary_deterministic_code_allowed": True,
    "canonical_rapp1_envelope_owned_by_host": True,
    "artifact_bundle": "content-addressed-successor-program-egg",
    "candidate_tests_are_independent_proof": False,
    "independent_host_canonical_tests_required": True,
    "controlled_mutants_required": True,
    "successor_lineage": "exact-forward-mutation-plus-reverse-ancestry",
    "lossless_requires_byte_reconstruction": True,
    "lossy_requires_exhaust": True,
    "mutation_offer_transport": "pr-projection-only",
    "mutation_offer_grants_authority": False,
    "seed_influence_requires_separate_selection_crossing": True,
    "meta_evolution_ladder": [
        "handshake",
        "agent-compiler",
        "organization-seed-trait",
        "protocol-successor",
    ],
    "automatic_upward_promotion": False,
    "generated_tests_self_certify": False,
    "n_lens_search": "bounded-beam-pareto-recombination",
    "fitness_is_scenario_relative": True,
    "universal_fitness_claimed": False,
    "continuous_ai_translation": False,
    "runtime_topology": "global-brainstem-jit-ephemeral",
    "routing_plane": "verified-regular-file-hotload-slot",
    "durable_output": "deterministic-static-agent.py",
    "durable_output_package": "agent.py+metadata+mutation-tests",
    "durable_output_distribution": "private-hive",
    "durable_output_scope": "declared-coverage-only",
    "learning_trace": "sanitized-hash-chained-correction-evidence",
    "persist_raw_transcripts": False,
    "persist_hidden_reasoning": False,
    "persist_local_paths": False,
    "persist_token_data": False,
    "persist_private_payloads": False,
    "prior_art": {
        "repository": "kody-w/UniversalDataConnectorAI",
        "commit": "f2a978b9f85b65b9815b69d99c67e51c56732251",
        "short_commit": "f2a978b",
        "role": "conceptual-provenance-only",
        "rapp1_conformance_claimed": False,
        "files": [
            {
                "path": "agents/connector_learning_orchestrator.py",
                "blob_sha": "1542986362f27598c224327e1372350d81ead56a",
                "safe_concept": "unknown-source-analysis-and-learning-orchestration",
            },
            {
                "path": "agents/schema_learner_agent.py",
                "blob_sha": "edf4c8bb146c478b77c24f6d1330a07ca79586ba",
                "safe_concept": "schema-learning-and-structural-evidence",
            },
            {
                "path": "agents/cx_format_synthesis_agent.py",
                "blob_sha": "548b88840321de0a56af9d0ea78b36a44dcb49bd",
                "safe_concept": "transform-and-agent-source-synthesis",
            },
            {
                "path": "agents/data_connector_registry_agent.py",
                "blob_sha": "87c99950029ecae3ccc1c5143c9f45efab1f9127",
                "safe_concept": "connector-catalog-and-reuse",
            },
        ],
        "safe_mapping": {
            "unknown_source_analysis": "bounded-snapshot-plus-adapter-resolution",
            "schema_learning": "jit-pass1-plus-typed-evidence",
            "transform_agent_generation": "jit-pass2-plus-static-agent-compiler",
            "test": "real-rehearsal-mutation-and-correction-fixtures",
            "registry": "signed-private-hive-handshake-catalog",
        },
        "excluded_mechanisms": [
            "ambient-azure-storage",
            "network-calls",
            "broad-exception-catches",
            "time-based-identity",
            "random-identity",
            "md5-identity",
            "floating-confidence",
            "auto-approval",
            "simulated-tests",
            "mutable-in-memory-sessions",
            "unqualified-generated-code",
        ],
    },
    "self_hosting_proof": "immutable-ancestor-to-causal-successor-repository",
    "self_hosting_protocol_projections": [
        "workspace",
        "work-organization",
        "hive",
        "federation",
    ],
    "legacy_relabeling_allowed": False,
    "successor_file_mutation_scope": "all-framed-files",
    "additive_sidecar_only": False,
    "unknown_unknown_gates_required": True,
    "normal_traffic_model_calls": 0,
    "persist_native_model_history": False,
    "persisted_interop_state": [
        "frames",
        "pins",
        "rehearsal-corpus",
        "exhaust",
        "static-mapping",
        "portable-agent-metadata-tests",
    ],
    "daemon_required": False,
    "plugin_registry_required": False,
    "permanent_process_required": False,
    "symlink_routing_allowed": False,
    "in_place_overwrite_allowed": False,
    "brainstem_py_modification_required": False,
    "bespoke_endpoint_runtime": False,
    "multi_frame_interop_default": False,
    "rapp1_rules": [
        "envelope",
        "hash",
        "signature",
        "stream",
        "ancestry",
        "registration",
        "refusal",
    ],
    "effects": [],
    "tile_schema": "rapp-work-capability-tile/1",
    "tile_role": "inert-content-addressed-capability",
    "capability_id": "autobest:generic",
    "capability_home": "specific-protocol-and-seed-profiles",
    "implementation_scope": "generic",
    "content_addressed": True,
    "byte_identical_inclusion": True,
    "immutable_implementation": True,
    "implementation_sha256_binding": {
        "algorithm": "sha256",
        "subject": "exact-agent.py-bytes",
        "digest_source": "external-tile-descriptor",
        "binding_api": "bind_implementation_sha256",
        "required_before_activation": True,
        "self_digest_embedded": False,
    },
    "activation": "external-host-only",
    "mutation": "successor-only",
    "ancestor_mutation_permitted": False,
    "authority_from_presence": False,
    "profile_layering": "data-config",
    "profiles": ["microsol-ceo"],
    "generic_operations": [
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
    ],
    "profile_operations": {"microsol-ceo": ["ceo", "microsol-ceo"]},
    "optional_host_adapters": ["agents.basic_agent", "basic_agent"],
}


VERSION = "3.0.0"
SCHEMA_PREFIX = "autobest"
DOMAIN_PREFIX = b"rapp-work/autobest/1\x00"
MAX_INPUT_BYTES = 524_288
MAX_STRING_BYTES = 16_384
MAX_DEPTH = 16
MAX_DICT_ITEMS = 128
MAX_LIST_ITEMS = 2_048
MAX_INTEGER = 1_000_000_000_000_000
MAX_RESOURCE = 1_000_000_000
MAX_SUBJECTS = 16
MAX_CANDIDATES = 8
MAX_COMPONENTS = 16
MAX_GATES = 16
MAX_METRICS = 16
MAX_REFS = 8
MAX_CEO_LINEAGE = 32
MAX_CEO_CRITERIA = 16
MAX_CEO_DIFFERENCES = 16
MAX_CEO_VERIFIERS = 4
MAX_SNAPSHOT_FILES = 32
MAX_SNAPSHOT_BYTES = 262_144
MAX_CONTENT_CHUNKS = 32
MAX_ENDPOINT_CAPABILITIES = 16
MAX_ENDPOINT_OPERATIONS = 16
MAX_COMPATIBILITY_MAPPINGS = 16
MAX_REHEARSAL_FIXTURES = 16
MAX_AGENT_FILE_BYTES = 524_288
MAX_STATIC_MAP_FIELDS = 32
MAX_TRACE_EVENTS = 32
MAX_REPOSITORY_ENTRIES = 256
MAX_BUNDLE_FILES = 64
MAX_EVOLUTION_CASES = 64
MAX_LENSES = 16
MAX_LENS_CANDIDATES = 64

RESOURCE_FIELDS = (
    "task_units",
    "context_bytes",
    "duration_ms",
    "tokens",
    "tool_calls",
    "credits_milli",
    "output_bytes",
    "checkpoints",
)

DIGEST_DOMAINS = {
    "task": "task/v1",
    "root_envelope": "root-envelope/v1",
    "reservation": "reservation/v1",
    "policy": "policy/v1",
    "receipt": "receipt/v1",
    "observation": "observation/v1",
    "deliverable": "deliverable/v1",
    "ceo_command": "ceo-command/v1",
    "ceo_organization": "ceo-organization/v1",
    "ceo_grant": "ceo-grant/v1",
    "ceo_event": "ceo-event/v1",
    "ceo_state": "ceo-state/v2",
    "repository_snapshot": "repository-snapshot/v1",
    "adapter_resolution": "adapter-resolution/v1",
    "hive_translation_policy": "hive-translation-policy/v1",
    "rapp1_endpoint": "rapp1-endpoint/v1",
    "compatibility_lens": "compatibility-lens/v1",
    "compatibility_exhaust": "compatibility-exhaust/v1",
    "double_hotload_result": "double-hotload-result/v1",
    "learning_trace": "learning-trace/v1",
    "repository_frame": "repository-frame/v1",
    "lens_dimension": "lens-dimension/v1",
    "lens_candidate": "lens-candidate/v1",
}

MICROSOL_CEO_PROFILE = {
    "schema": "autobest-profile/1",
    "name": "microsol-ceo",
    "version": "1.0.0",
    "kind": "data-config",
    "host_activation_required": True,
    "authority_from_profile": False,
    "mutation": "successor-state-only",
    "actions": [
        "intake",
        "accept_mission",
        "select_dimensions",
        "delegate",
        "observe_checkpoint",
        "mutate_slice",
        "difference_parallel",
        "cross",
        "verify",
        "decide",
        "handoff",
        "close",
        "user_control",
    ],
    "phases": [
        "mission_acceptance",
        "worker_delegation",
        "checkpoint_observation",
        "control_checkpoint",
        "difference_parallel",
        "independent_verification",
        "decision",
        "handoff",
        "closed",
    ],
    "events": [
        "mission_accepted",
        "worker_observations",
        "checkpoint_observed",
        "differences_completed",
        "verification_completed",
        "decision_recorded",
        "handoff_closed",
        "user_control",
        "control_checkpoint_observed",
    ],
    "control_modes": ["autonomous", "guided", "detail"],
    "hard_gate_policy": "generic-autobest-policy",
}

PROFILE_CONFIGS = {"microsol-ceo": MICROSOL_CEO_PROFILE}
PRIOR_ART_PROVENANCE = __manifest__["prior_art"]
CEO_ACTIONS = frozenset(MICROSOL_CEO_PROFILE["actions"])
CEO_PHASES = frozenset(MICROSOL_CEO_PROFILE["phases"])
CEO_EVENT_TYPES = frozenset(MICROSOL_CEO_PROFILE["events"])
CEO_CONTROL_MODES = frozenset(MICROSOL_CEO_PROFILE["control_modes"])

_FORBIDDEN_AUTHORITY_KEYS = frozenset(
    {
        "adopt",
        "adoption",
        "authority",
        "authorization",
        "authorized",
        "credential",
        "credentials",
        "deploy",
        "effect",
        "effects",
        "execute",
        "execution",
        "grant",
        "grants",
        "launch",
        "private_key",
        "publish",
        "rapp1_frame",
        "rapp1_frames",
        "secret",
        "secrets",
        "signature",
        "signatures",
        "signed",
        "signing_key",
    }
)


class AutoBestRefusal(ValueError):
    """Specific refusal raised by the direct pure-function API."""

    def __init__(self, code, path, detail, evidence=None):
        super().__init__(f"{code} at {path}: {detail}")
        self.code = code
        self.path = path
        self.detail = detail
        self.evidence = evidence


def _refuse(code, path, detail, evidence=None):
    raise AutoBestRefusal(code, path, detail, evidence)


def profile_config(name):
    """Return an inert copy of a named profile configuration."""

    if not isinstance(name, str) or name not in PROFILE_CONFIGS:
        _refuse("unknown_profile", "$.profile", f"unsupported profile: {name!r}")
    return json.loads(
        json.dumps(
            PROFILE_CONFIGS[name],
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
    )


def prior_art_provenance():
    """Return an inert copy of the pinned conceptual prior-art record."""

    return json.loads(
        json.dumps(
            PRIOR_ART_PROVENANCE,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
    )


def _plain_json(value, path="$", depth=0):
    if depth > MAX_DEPTH:
        _refuse("too_deep", path, f"JSON nesting exceeds {MAX_DEPTH}")
    if value is None or isinstance(value, (str, bool)):
        if isinstance(value, str) and len(value.encode("utf-8")) > MAX_STRING_BYTES:
            _refuse("oversize_string", path, f"string exceeds {MAX_STRING_BYTES} UTF-8 bytes")
        return
    if isinstance(value, int):
        if abs(value) > MAX_INTEGER:
            _refuse("oversize_integer", path, f"integer magnitude exceeds {MAX_INTEGER}")
        return
    if isinstance(value, float):
        _refuse("float_forbidden", path, "floats are not accepted; use bounded integers")
    if isinstance(value, list):
        if len(value) > MAX_LIST_ITEMS:
            _refuse("too_many_items", path, f"list exceeds {MAX_LIST_ITEMS} items")
        for index, item in enumerate(value):
            _plain_json(item, f"{path}[{index}]", depth + 1)
        return
    if isinstance(value, dict):
        if len(value) > MAX_DICT_ITEMS:
            _refuse("too_many_fields", path, f"object exceeds {MAX_DICT_ITEMS} fields")
        for key, item in value.items():
            if not isinstance(key, str):
                _refuse("non_string_key", path, "JSON object keys must be strings")
            if len(key.encode("utf-8")) > 128:
                _refuse("oversize_key", f"{path}.{key[:16]}", "object key exceeds 128 UTF-8 bytes")
            _plain_json(item, f"{path}.{key}", depth + 1)
        return
    _refuse("non_json_value", path, f"{type(value).__name__} is not a plain JSON value")


def _canonical_bytes(value):
    _plain_json(value)
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def canonical_digest(domain, value):
    """Return a domain-separated lowercase SHA-256 over canonical JSON."""

    if not isinstance(domain, str) or not domain or len(domain.encode("utf-8")) > 128:
        _refuse("invalid_domain", "$.domain", "digest domain must be a short non-empty string")
    return hashlib.sha256(DOMAIN_PREFIX + domain.encode("utf-8") + b"\x00" + _canonical_bytes(value)).hexdigest()


def head_record(kind, body):
    """Copy a known record body and attach its canonical domain-separated head."""

    if kind not in DIGEST_DOMAINS:
        _refuse("unknown_record_kind", "$.kind", f"unsupported headed record kind: {kind!r}")
    if not isinstance(body, dict):
        _refuse("object_required", "$.body", "record body must be an object")
    if "head" in body:
        _refuse("unexpected_field", "$.body.head", "record body must not already contain head")
    _reject_authority_shaped(body)
    result = dict(body)
    result["head"] = canonical_digest(DIGEST_DOMAINS[kind], body)
    return result


def _duplicate_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            _refuse("duplicate_field", f"$.{key}", f"duplicate JSON field {key!r}")
        result[key] = value
    return result


def _reject_constant(value):
    _refuse("float_forbidden", "$", f"non-integer JSON number {value!r} is forbidden")


def loads_json(text):
    """Parse closed JSON while detecting duplicate fields and non-integer numbers."""

    if not isinstance(text, str):
        _refuse("string_required", "$", "JSON input must be a string")
    if len(text.encode("utf-8")) > MAX_INPUT_BYTES:
        _refuse("oversize_input", "$", f"input exceeds {MAX_INPUT_BYTES} UTF-8 bytes")
    try:
        value = json.loads(
            text,
            object_pairs_hook=_duplicate_object,
            parse_constant=_reject_constant,
        )
    except AutoBestRefusal:
        raise
    except json.JSONDecodeError as error:
        _refuse("malformed_json", "$", str(error))
    _plain_json(value)
    return value


def _prepare_input(value, path):
    _plain_json(value, path)
    if len(_canonical_bytes(value)) > MAX_INPUT_BYTES:
        _refuse("oversize_input", path, f"canonical input exceeds {MAX_INPUT_BYTES} bytes")
    _reject_authority_shaped(value, path)


def _reject_authority_shaped(value, path="$"):
    if isinstance(value, dict):
        for key, item in value.items():
            normalized = key.lower().replace("-", "_")
            if normalized in _FORBIDDEN_AUTHORITY_KEYS:
                _refuse(
                    "authority_shaped_input",
                    f"{path}.{key}",
                    "planner inputs may carry evidence references, never authority, execution, keys, or effects",
                )
            _reject_authority_shaped(item, f"{path}.{key}")
    elif isinstance(value, list):
        for index, item in enumerate(value):
            _reject_authority_shaped(item, f"{path}[{index}]")


def _closed(value, path, fields):
    if not isinstance(value, dict):
        _refuse("object_required", path, "expected an object")
    expected = set(fields)
    actual = set(value)
    missing = sorted(expected - actual)
    unknown = sorted(actual - expected)
    if missing:
        _refuse("missing_field", path, f"missing required fields: {', '.join(missing)}")
    if unknown:
        _refuse("unknown_field", path, f"unknown fields: {', '.join(unknown)}")
    return value


def _text(value, path, *, allow_empty=False, max_bytes=256):
    if not isinstance(value, str):
        _refuse("string_required", path, "expected a string")
    size = len(value.encode("utf-8"))
    if (not allow_empty and not value) or size > max_bytes:
        _refuse("invalid_string", path, f"string must be {'0' if allow_empty else '1'}..{max_bytes} UTF-8 bytes")
    return value


def _identifier(value, path):
    value = _text(value, path, max_bytes=128)
    allowed = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._:/-@"
    if any(character not in allowed for character in value):
        _refuse("invalid_identifier", path, "identifier contains unsupported characters")
    return value


def _sha256(value, path):
    if (
        not isinstance(value, str)
        or len(value) != 64
        or any(character not in "0123456789abcdef" for character in value)
    ):
        _refuse("malformed_sha256", path, "expected exactly 64 lowercase hexadecimal characters")
    return value


def _sha256_content_address(value, digest, path):
    expected = "sha256:" + digest
    if value != expected:
        _refuse("content_address_mismatch", path, f"expected {expected}")
    return value


def _validate_hotload_slot_contract(value, path):
    fields = (
        "slot_id",
        "filename",
        "isolated",
        "regular_file_only",
        "atomic_placement",
        "symlinks_allowed",
        "overwrite_allowed",
        "daemon_allowed",
        "plugin_registry_allowed",
        "permanent_process_allowed",
        "brainstem_py_modification_allowed",
        "unload_required",
    )
    _closed(value, path, fields)
    _identifier(value["slot_id"], f"{path}.slot_id")
    if value["filename"] != "agent.py":
        _refuse("invalid_slot_contract", f"{path}.filename", "hotload slot accepts only agent.py")
    for field in (
        "isolated",
        "regular_file_only",
        "atomic_placement",
        "unload_required",
    ):
        if value[field] is not True:
            _refuse("invalid_slot_contract", f"{path}.{field}", f"{field} must be true")
    for field in (
        "symlinks_allowed",
        "overwrite_allowed",
        "daemon_allowed",
        "plugin_registry_allowed",
        "permanent_process_allowed",
        "brainstem_py_modification_allowed",
    ):
        if value[field] is not False:
            _refuse("forbidden_runtime_mechanism", f"{path}.{field}", f"{field} must be false")
    return value


def bind_implementation_sha256(implementation_sha256):
    """Bind an externally computed digest of the exact single-file implementation bytes."""

    digest = _sha256(implementation_sha256, "$.implementation_sha256")
    body = {
        "schema": "autobest-implementation-binding/1",
        "algorithm": "sha256",
        "implementation_sha256": digest,
        "subject": "exact-agent.py-bytes",
        "manifest_name": __manifest__["name"],
        "manifest_version": __manifest__["version"],
        "tile_schema": __manifest__["tile_schema"],
        "tile_role": __manifest__["tile_role"],
        "capability_home": __manifest__["capability_home"],
        "rapp1_role": __manifest__["rapp1_role"],
        "rapp1_rules": list(__manifest__["rapp1_rules"]),
        "immutable_implementation": True,
        "activation": "external-host-only",
        "mutation": "successor-only",
        "authority_from_presence": False,
        "profiles": sorted(PROFILE_CONFIGS),
        "conceptual_prior_art_commit": PRIOR_ART_PROVENANCE["commit"],
        "prior_art_rapp1_conformance_claimed": False,
    }
    result = dict(body)
    result["binding_head"] = canonical_digest("implementation-binding/v1", body)
    return result


def _integer(value, path, minimum=0, maximum=MAX_RESOURCE):
    if isinstance(value, bool) or not isinstance(value, int):
        _refuse("integer_required", path, "expected an integer, not a boolean or float")
    if value < minimum or value > maximum:
        _refuse("integer_out_of_range", path, f"expected {minimum}..{maximum}")
    return value


def _bp(value, path):
    return _integer(value, path, 0, 10_000)


def _boolean(value, path):
    if not isinstance(value, bool):
        _refuse("boolean_required", path, "expected a JSON boolean")
    return value


def _unique_strings(value, path, *, maximum, allow_empty=True, identifiers=False):
    if not isinstance(value, list):
        _refuse("list_required", path, "expected a list")
    if len(value) > maximum or (not allow_empty and not value):
        lower = 0 if allow_empty else 1
        _refuse("too_many_items", path, f"expected {lower}..{maximum} items")
    result = []
    seen = set()
    for index, item in enumerate(value):
        checked = _identifier(item, f"{path}[{index}]") if identifiers else _text(
            item, f"{path}[{index}]", max_bytes=256
        )
        if checked in seen:
            _refuse("duplicate_item", f"{path}[{index}]", f"duplicate item {checked!r}")
        seen.add(checked)
        result.append(checked)
    return result


def _sha_list(value, path, *, allow_empty=True):
    if not isinstance(value, list):
        _refuse("list_required", path, "expected a list")
    if len(value) > MAX_REFS or (not allow_empty and not value):
        lower = 0 if allow_empty else 1
        _refuse("too_many_items", path, f"expected {lower}..{MAX_REFS} SHA-256 references")
    seen = set()
    for index, item in enumerate(value):
        digest = _sha256(item, f"{path}[{index}]")
        if digest in seen:
            _refuse("duplicate_item", f"{path}[{index}]", "duplicate parent reference")
        seen.add(digest)
    return value


def _bounded_sha_list(value, path, maximum, *, allow_empty=True):
    if not isinstance(value, list):
        _refuse("list_required", path, "expected a list")
    if len(value) > maximum or (not allow_empty and not value):
        lower = 0 if allow_empty else 1
        _refuse("too_many_items", path, f"expected {lower}..{maximum} SHA-256 references")
    seen = set()
    for index, item in enumerate(value):
        digest = _sha256(item, f"{path}[{index}]")
        if digest in seen:
            _refuse("duplicate_item", f"{path}[{index}]", "duplicate SHA-256 reference")
        seen.add(digest)
    return value


def _resource_vector(value, path):
    _closed(value, path, RESOURCE_FIELDS)
    return {field: _integer(value[field], f"{path}.{field}") for field in RESOURCE_FIELDS}


def _zero_resources():
    return {field: 0 for field in RESOURCE_FIELDS}


def _resource_minimum(left, right):
    return {field: min(left[field], right[field]) for field in RESOURCE_FIELDS}


def _resource_leq(left, right):
    return all(left[field] <= right[field] for field in RESOURCE_FIELDS)


def _resource_excess(left, right):
    return [field for field in RESOURCE_FIELDS if left[field] > right[field]]


def _validate_provenance(value, path, *, parents_required=False):
    _closed(value, path, ("source_id", "source_head", "parent_refs"))
    _identifier(value["source_id"], f"{path}.source_id")
    _sha256(value["source_head"], f"{path}.source_head")
    _sha_list(value["parent_refs"], f"{path}.parent_refs", allow_empty=not parents_required)
    return value


def _verify_head(record, path, kind, body_fields):
    _sha256(record["head"], f"{path}.head")
    body = {field: record[field] for field in body_fields}
    expected = canonical_digest(DIGEST_DOMAINS[kind], body)
    if record["head"] != expected:
        _refuse("head_mismatch", f"{path}.head", f"expected canonical {kind} head {expected}")


def _validate_task(value, path):
    body_fields = ("schema", "task_id", "payload", "provenance")
    _closed(value, path, body_fields + ("head",))
    if value["schema"] != "autobest-task/1":
        _refuse("unsupported_schema", f"{path}.schema", "expected autobest-task/1")
    _identifier(value["task_id"], f"{path}.task_id")
    if not isinstance(value["payload"], dict) or not value["payload"]:
        _refuse("object_required", f"{path}.payload", "task payload must be a non-empty JSON object")
    _validate_provenance(value["provenance"], f"{path}.provenance")
    _verify_head(value, path, "task", body_fields)
    return value


def _validate_root(value, path):
    body_fields = ("schema", "envelope_id", "max_subjects", "limits", "provenance")
    _closed(value, path, body_fields + ("head",))
    if value["schema"] != "autobest-root-envelope/1":
        _refuse("unsupported_schema", f"{path}.schema", "expected autobest-root-envelope/1")
    _identifier(value["envelope_id"], f"{path}.envelope_id")
    _integer(value["max_subjects"], f"{path}.max_subjects", 1, MAX_SUBJECTS)
    limits = _resource_vector(value["limits"], f"{path}.limits")
    for field in ("task_units", "context_bytes", "duration_ms", "tokens", "output_bytes", "checkpoints"):
        if limits[field] == 0:
            _refuse("unsafe_zero_limit", f"{path}.limits.{field}", "root planning limit must be non-zero")
    _validate_provenance(value["provenance"], f"{path}.provenance")
    _verify_head(value, path, "root_envelope", body_fields)
    return value


def _validate_reservation(value, path):
    body_fields = (
        "schema",
        "reservation_id",
        "predecessor_plan",
        "resources",
        "checkpoint_every_ms",
        "provenance",
    )
    _closed(value, path, body_fields + ("head",))
    if value["schema"] != "autobest-reservation/1":
        _refuse("unsupported_schema", f"{path}.schema", "expected autobest-reservation/1")
    _identifier(value["reservation_id"], f"{path}.reservation_id")
    predecessor = value["predecessor_plan"]
    if predecessor is not None:
        _sha256(predecessor, f"{path}.predecessor_plan")
    _resource_vector(value["resources"], f"{path}.resources")
    _integer(value["checkpoint_every_ms"], f"{path}.checkpoint_every_ms", 1, MAX_RESOURCE)
    _validate_provenance(value["provenance"], f"{path}.provenance")
    if predecessor is not None and predecessor not in value["provenance"]["parent_refs"]:
        _refuse(
            "missing_predecessor_binding",
            f"{path}.provenance.parent_refs",
            "a successor reservation must retain its predecessor plan reference",
        )
    _verify_head(value, path, "reservation", body_fields)
    return value


def _validate_version(value, path):
    _text(value, path, max_bytes=32)
    parts = value.split(".")
    if len(parts) != 3 or any(not part.isdigit() or int(part) > 999 for part in parts):
        _refuse("invalid_version", path, "policy version must be three bounded decimal components")
    return value


def _weights(value, path):
    if not isinstance(value, dict) or not value or len(value) > MAX_METRICS:
        _refuse("invalid_weights", path, f"weights must contain 1..{MAX_METRICS} metrics")
    total = 0
    for key, weight in value.items():
        _identifier(key, f"{path}.{key}")
        total += _bp(weight, f"{path}.{key}")
    if total != 10_000:
        _refuse("weight_sum", path, f"weights must sum exactly to 10000, got {total}")
    return value


def _validate_policy(value, path):
    body_fields = ("schema", "policy_id", "version", "delegate", "cross", "provenance")
    _closed(value, path, body_fields + ("head",))
    if value["schema"] != "autobest-policy/1":
        _refuse("unsupported_schema", f"{path}.schema", "expected autobest-policy/1")
    _identifier(value["policy_id"], f"{path}.policy_id")
    _validate_version(value["version"], f"{path}.version")
    _validate_provenance(value["provenance"], f"{path}.provenance")

    delegate_fields = (
        "required_gates",
        "weights_bps",
        "minimum_fitness_bps",
        "split_below_bps",
        "reservation_caps",
        "per_subject_caps",
        "minimum_slice",
        "checkpoint_min_ms",
        "checkpoint_max_ms",
        "max_subjects",
    )
    delegate_policy = _closed(value["delegate"], f"{path}.delegate", delegate_fields)
    _unique_strings(
        delegate_policy["required_gates"],
        f"{path}.delegate.required_gates",
        maximum=MAX_GATES,
        allow_empty=False,
        identifiers=True,
    )
    _weights(delegate_policy["weights_bps"], f"{path}.delegate.weights_bps")
    minimum_fitness = _integer(
        delegate_policy["minimum_fitness_bps"],
        f"{path}.delegate.minimum_fitness_bps",
        1,
        10_000,
    )
    split_below = _integer(
        delegate_policy["split_below_bps"],
        f"{path}.delegate.split_below_bps",
        minimum_fitness,
        10_000,
    )
    if split_below < minimum_fitness:
        _refuse("invalid_thresholds", f"{path}.delegate", "split threshold cannot precede minimum fitness")
    reservation_caps = _resource_vector(
        delegate_policy["reservation_caps"], f"{path}.delegate.reservation_caps"
    )
    per_subject_caps = _resource_vector(
        delegate_policy["per_subject_caps"], f"{path}.delegate.per_subject_caps"
    )
    minimum_slice = _resource_vector(
        delegate_policy["minimum_slice"], f"{path}.delegate.minimum_slice"
    )
    for field in RESOURCE_FIELDS:
        if minimum_slice[field] > per_subject_caps[field]:
            _refuse(
                "invalid_policy_cap",
                f"{path}.delegate.minimum_slice.{field}",
                "minimum slice exceeds per-subject cap",
            )
        if minimum_slice[field] > reservation_caps[field]:
            _refuse(
                "invalid_policy_cap",
                f"{path}.delegate.minimum_slice.{field}",
                "minimum slice exceeds reservation cap",
            )
    checkpoint_min = _integer(
        delegate_policy["checkpoint_min_ms"],
        f"{path}.delegate.checkpoint_min_ms",
        1,
        MAX_RESOURCE,
    )
    checkpoint_max = _integer(
        delegate_policy["checkpoint_max_ms"],
        f"{path}.delegate.checkpoint_max_ms",
        checkpoint_min,
        MAX_RESOURCE,
    )
    if checkpoint_max < checkpoint_min:
        _refuse("invalid_thresholds", f"{path}.delegate", "checkpoint maximum precedes minimum")
    _integer(delegate_policy["max_subjects"], f"{path}.delegate.max_subjects", 1, MAX_SUBJECTS)

    cross_fields = (
        "required_gates",
        "weights_bps",
        "minimum_score_bps",
        "minimum_coverage_bps",
        "allow_hash_tiebreak",
        "max_candidates",
        "max_components_per_candidate",
    )
    cross_policy = _closed(value["cross"], f"{path}.cross", cross_fields)
    _unique_strings(
        cross_policy["required_gates"],
        f"{path}.cross.required_gates",
        maximum=MAX_GATES,
        allow_empty=False,
        identifiers=True,
    )
    _weights(cross_policy["weights_bps"], f"{path}.cross.weights_bps")
    _integer(cross_policy["minimum_score_bps"], f"{path}.cross.minimum_score_bps", 1, 10_000)
    _integer(
        cross_policy["minimum_coverage_bps"],
        f"{path}.cross.minimum_coverage_bps",
        1,
        10_000,
    )
    _boolean(cross_policy["allow_hash_tiebreak"], f"{path}.cross.allow_hash_tiebreak")
    _integer(cross_policy["max_candidates"], f"{path}.cross.max_candidates", 1, MAX_CANDIDATES)
    _integer(
        cross_policy["max_components_per_candidate"],
        f"{path}.cross.max_components_per_candidate",
        1,
        MAX_COMPONENTS,
    )
    _verify_head(value, path, "policy", body_fields)
    return value


def _validate_gate_map(value, path, names):
    _closed(value, path, names)
    for name in names:
        _boolean(value[name], f"{path}.{name}")
    return value


def _validate_metric_map(value, path, weights):
    _closed(value, path, tuple(weights))
    for name in weights:
        _bp(value[name], f"{path}.{name}")
    return value


def _validate_receipt(value, path):
    body_fields = ("schema", "receipt_id", "status", "facts_head", "provenance")
    _closed(value, path, body_fields + ("head",))
    if value["schema"] != "autobest-receipt/1":
        _refuse("unsupported_schema", f"{path}.schema", "expected autobest-receipt/1")
    _identifier(value["receipt_id"], f"{path}.receipt_id")
    if value["status"] != "current":
        _refuse("stale_receipt", f"{path}.status", "only current caller-supplied receipts are accepted")
    _sha256(value["facts_head"], f"{path}.facts_head")
    _validate_provenance(value["provenance"], f"{path}.provenance")
    _verify_head(value, path, "receipt", body_fields)
    return value


def _validate_observation(value, path, policy):
    body_fields = (
        "schema",
        "observation_id",
        "subject_kind",
        "subject_id",
        "dimension_id",
        "gates",
        "metrics_bps",
        "remaining",
        "receipt",
        "provenance",
    )
    _closed(value, path, body_fields + ("head",))
    if value["schema"] != "autobest-observation/1":
        _refuse("unsupported_schema", f"{path}.schema", "expected autobest-observation/1")
    _identifier(value["observation_id"], f"{path}.observation_id")
    if value["subject_kind"] not in ("worker", "generation"):
        _refuse("invalid_enum", f"{path}.subject_kind", "expected worker or generation")
    _identifier(value["subject_id"], f"{path}.subject_id")
    _identifier(value["dimension_id"], f"{path}.dimension_id")
    delegate_policy = policy["delegate"]
    _validate_gate_map(
        value["gates"], f"{path}.gates", delegate_policy["required_gates"]
    )
    _validate_metric_map(
        value["metrics_bps"], f"{path}.metrics_bps", delegate_policy["weights_bps"]
    )
    _resource_vector(value["remaining"], f"{path}.remaining")
    _validate_receipt(value["receipt"], f"{path}.receipt")
    _validate_provenance(value["provenance"], f"{path}.provenance", parents_required=True)
    if value["receipt"]["head"] not in value["provenance"]["parent_refs"]:
        _refuse(
            "missing_receipt_binding",
            f"{path}.provenance.parent_refs",
            "observation provenance must retain the exact receipt head",
        )
    _verify_head(value, path, "observation", body_fields)
    return value


def _validate_component(value, path):
    fields = (
        "component_id",
        "content_head",
        "coupling",
        "group_id",
        "compatibility_id",
        "substitutability_id",
        "safety_critical",
        "depends_on",
        "parent_refs",
        "conflicts",
        "unknowns",
    )
    _closed(value, path, fields)
    _identifier(value["component_id"], f"{path}.component_id")
    _sha256(value["content_head"], f"{path}.content_head")
    if value["coupling"] not in ("shared", "independent", "atomic"):
        _refuse("invalid_enum", f"{path}.coupling", "expected shared, independent, or atomic")
    _identifier(value["group_id"], f"{path}.group_id")
    for field in ("compatibility_id", "substitutability_id"):
        if value[field] is not None:
            _identifier(value[field], f"{path}.{field}")
    _boolean(value["safety_critical"], f"{path}.safety_critical")
    _unique_strings(
        value["depends_on"], f"{path}.depends_on", maximum=MAX_COMPONENTS, identifiers=True
    )
    _sha_list(value["parent_refs"], f"{path}.parent_refs", allow_empty=False)
    _unique_strings(value["conflicts"], f"{path}.conflicts", maximum=MAX_REFS)
    _unique_strings(value["unknowns"], f"{path}.unknowns", maximum=MAX_REFS)
    if value["coupling"] == "shared":
        if (
            value["compatibility_id"] is not None
            or value["substitutability_id"] is not None
            or value["depends_on"]
        ):
            _refuse("invalid_component", path, "shared components cannot declare compatibility, substitution, or dependencies")
    elif value["coupling"] == "independent":
        if value["compatibility_id"] is None:
            _refuse("invalid_component", path, "independent components require compatibility_id")
        if value["depends_on"]:
            _refuse("invalid_component", path, "dependency-coupled components must be atomic")
    else:
        if value["compatibility_id"] is not None:
            _refuse("invalid_component", path, "atomic components do not use compatibility_id")
    return value


def _validate_candidate(value, path, policy):
    body_fields = (
        "schema",
        "candidate_id",
        "coverage_bps",
        "comparable",
        "gates",
        "metrics_bps",
        "components",
        "provenance",
    )
    _closed(value, path, body_fields + ("head",))
    if value["schema"] != "autobest-deliverable/1":
        _refuse("unsupported_schema", f"{path}.schema", "expected autobest-deliverable/1")
    _identifier(value["candidate_id"], f"{path}.candidate_id")
    _bp(value["coverage_bps"], f"{path}.coverage_bps")
    _boolean(value["comparable"], f"{path}.comparable")
    cross_policy = policy["cross"]
    _validate_gate_map(value["gates"], f"{path}.gates", cross_policy["required_gates"])
    _validate_metric_map(value["metrics_bps"], f"{path}.metrics_bps", cross_policy["weights_bps"])
    if not isinstance(value["components"], list) or not value["components"]:
        _refuse("list_required", f"{path}.components", "deliverable requires at least one component")
    maximum = cross_policy["max_components_per_candidate"]
    if len(value["components"]) > maximum:
        _refuse("too_many_items", f"{path}.components", f"component count exceeds policy cap {maximum}")
    component_ids = set()
    by_id = {}
    for index, component in enumerate(value["components"]):
        _validate_component(component, f"{path}.components[{index}]")
        component_id = component["component_id"]
        if component_id in component_ids:
            _refuse("duplicate_item", f"{path}.components[{index}].component_id", "component_id must be unique per candidate")
        component_ids.add(component_id)
        by_id[component_id] = component
    for index, component in enumerate(value["components"]):
        for dependency in component["depends_on"]:
            if dependency not in by_id:
                _refuse(
                    "missing_dependency",
                    f"{path}.components[{index}].depends_on",
                    f"unknown component dependency {dependency!r}",
                )
            target = by_id[dependency]
            if target["coupling"] == "independent":
                _refuse(
                    "invalid_dependency",
                    f"{path}.components[{index}].depends_on",
                    "atomic dependencies may target the same atomic group or an exact shared component",
                )
            if target["coupling"] == "atomic" and target["group_id"] != component["group_id"]:
                _refuse(
                    "invalid_dependency",
                    f"{path}.components[{index}].depends_on",
                    "atomic dependency must remain inside one atomic group",
                )
    _validate_provenance(value["provenance"], f"{path}.provenance", parents_required=True)
    _verify_head(value, path, "deliverable", body_fields)
    return value


def _validate_ceo_command(value, path):
    body_fields = ("schema", "command_id", "text", "provenance")
    _closed(value, path, body_fields + ("head",))
    if value["schema"] != "microsol-ceo-command/1":
        _refuse("unsupported_schema", f"{path}.schema", "expected microsol-ceo-command/1")
    _identifier(value["command_id"], f"{path}.command_id")
    _text(value["text"], f"{path}.text", max_bytes=MAX_STRING_BYTES)
    _validate_provenance(value["provenance"], f"{path}.provenance")
    _verify_head(value, path, "ceo_command", body_fields)
    return value


def _validate_ceo_dimension(value, path):
    fields = ("dimension_id", "role", "capabilities", "available", "static")
    _closed(value, path, fields)
    _identifier(value["dimension_id"], f"{path}.dimension_id")
    if value["role"] not in ("management", "worker", "verification"):
        _refuse("invalid_enum", f"{path}.role", "expected management, worker, or verification")
    _unique_strings(
        value["capabilities"],
        f"{path}.capabilities",
        maximum=MAX_COMPONENTS,
        identifiers=True,
    )
    _boolean(value["available"], f"{path}.available")
    if value["static"] is not True:
        _refuse("dynamic_dimension_forbidden", f"{path}.static", "CEO profile selects only static Dimensions")
    return value


def _validate_ceo_organization(value, path):
    body_fields = (
        "schema",
        "organization_id",
        "dimensions",
        "verification_receipt",
        "provenance",
    )
    _closed(value, path, body_fields + ("head",))
    if value["schema"] != "microsol-ceo-organization/1":
        _refuse("unsupported_schema", f"{path}.schema", "expected microsol-ceo-organization/1")
    _identifier(value["organization_id"], f"{path}.organization_id")
    if not isinstance(value["dimensions"], list) or not value["dimensions"]:
        _refuse("list_required", f"{path}.dimensions", "organization requires static Dimensions")
    if len(value["dimensions"]) > MAX_SUBJECTS:
        _refuse("too_many_items", f"{path}.dimensions", f"Dimension count exceeds {MAX_SUBJECTS}")
    seen = set()
    for index, dimension in enumerate(value["dimensions"]):
        _validate_ceo_dimension(dimension, f"{path}.dimensions[{index}]")
        if dimension["dimension_id"] in seen:
            _refuse(
                "duplicate_item",
                f"{path}.dimensions[{index}].dimension_id",
                "duplicate Dimension id",
            )
        seen.add(dimension["dimension_id"])
    _validate_receipt(value["verification_receipt"], f"{path}.verification_receipt")
    _validate_provenance(value["provenance"], f"{path}.provenance", parents_required=True)
    if value["verification_receipt"]["head"] not in value["provenance"]["parent_refs"]:
        _refuse(
            "missing_receipt_binding",
            f"{path}.provenance.parent_refs",
            "organization state must bind its separate verification receipt",
        )
    _verify_head(value, path, "ceo_organization", body_fields)
    return value


def _validate_ceo_grant(value, path):
    body_fields = (
        "schema",
        "grant_id",
        "organization_id",
        "allowed_actions",
        "allowed_dimensions",
        "limits",
        "max_parallel_dimensions",
        "minimum_verifiers",
        "verification_receipt",
        "provenance",
    )
    _closed(value, path, body_fields + ("head",))
    if value["schema"] != "microsol-ceo-grant-envelope/1":
        _refuse("unsupported_schema", f"{path}.schema", "expected microsol-ceo-grant-envelope/1")
    _identifier(value["grant_id"], f"{path}.grant_id")
    _identifier(value["organization_id"], f"{path}.organization_id")
    actions = _unique_strings(
        value["allowed_actions"],
        f"{path}.allowed_actions",
        maximum=len(CEO_ACTIONS),
        identifiers=True,
    )
    unknown_actions = sorted(set(actions) - CEO_ACTIONS)
    if unknown_actions:
        _refuse(
            "unknown_action",
            f"{path}.allowed_actions",
            "unknown CEO actions: " + ", ".join(unknown_actions),
        )
    _unique_strings(
        value["allowed_dimensions"],
        f"{path}.allowed_dimensions",
        maximum=MAX_SUBJECTS,
        identifiers=True,
    )
    _resource_vector(value["limits"], f"{path}.limits")
    _integer(
        value["max_parallel_dimensions"],
        f"{path}.max_parallel_dimensions",
        1,
        MAX_SUBJECTS,
    )
    _integer(
        value["minimum_verifiers"],
        f"{path}.minimum_verifiers",
        1,
        MAX_CEO_VERIFIERS,
    )
    _validate_receipt(value["verification_receipt"], f"{path}.verification_receipt")
    _validate_provenance(value["provenance"], f"{path}.provenance", parents_required=True)
    if value["verification_receipt"]["head"] not in value["provenance"]["parent_refs"]:
        _refuse(
            "missing_receipt_binding",
            f"{path}.provenance.parent_refs",
            "grant envelope must bind its separate verification receipt",
        )
    _verify_head(value, path, "ceo_grant", body_fields)
    return value


def _validate_ceo_mission(value, path):
    _closed(value, path, ("accepted", "acceptance_criteria", "task"))
    _boolean(value["accepted"], f"{path}.accepted")
    _unique_strings(
        value["acceptance_criteria"],
        f"{path}.acceptance_criteria",
        maximum=MAX_CEO_CRITERIA,
    )
    if value["task"] is not None:
        _validate_task(value["task"], f"{path}.task")
    if value["accepted"] and value["task"] is None:
        _refuse("missing_field", f"{path}.task", "accepted mission requires a canonical task")
    return value


def _validate_ceo_budget(value, path):
    _closed(value, path, ("root_limits", "grant_limits", "remaining", "latest_reservation"))
    root_limits = _resource_vector(value["root_limits"], f"{path}.root_limits")
    grant_limits = _resource_vector(value["grant_limits"], f"{path}.grant_limits")
    remaining = _resource_vector(value["remaining"], f"{path}.remaining")
    latest = _resource_vector(value["latest_reservation"], f"{path}.latest_reservation")
    if not _resource_leq(grant_limits, root_limits):
        _refuse("grant_exceeds_root", f"{path}.grant_limits", "grant limits exceed immutable root limits")
    ceiling = _resource_minimum(root_limits, grant_limits)
    if not _resource_leq(remaining, ceiling):
        _refuse("budget_exceeded", f"{path}.remaining", "remaining budget exceeds root/grant ceiling")
    if not _resource_leq(latest, remaining):
        _refuse(
            "budget_exceeded",
            f"{path}.latest_reservation",
            "latest reservation exceeds the externally reported remaining budget",
        )
    return value


def _validate_ceo_artifacts(value, path):
    fields = (
        "delegate_plan_heads",
        "checkpoint_heads",
        "difference_task_heads",
        "candidate_heads",
        "cross_plan_head",
        "verification_event_heads",
        "handoff_head",
    )
    _closed(value, path, fields)
    for field in (
        "delegate_plan_heads",
        "checkpoint_heads",
        "difference_task_heads",
        "candidate_heads",
        "verification_event_heads",
    ):
        _bounded_sha_list(value[field], f"{path}.{field}", MAX_CEO_LINEAGE)
    for field in ("cross_plan_head", "handoff_head"):
        if value[field] is not None:
            _sha256(value[field], f"{path}.{field}")
    return value


def _validate_ceo_verification(value, path):
    if value is None:
        return value
    _closed(value, path, ("passed", "event_head", "verifier_dimensions", "failures"))
    _boolean(value["passed"], f"{path}.passed")
    _sha256(value["event_head"], f"{path}.event_head")
    _unique_strings(
        value["verifier_dimensions"],
        f"{path}.verifier_dimensions",
        maximum=MAX_CEO_VERIFIERS,
        identifiers=True,
    )
    _unique_strings(value["failures"], f"{path}.failures", maximum=MAX_CEO_VERIFIERS)
    return value


def _validate_ceo_decision(value, path):
    if value is None:
        return value
    _closed(value, path, ("kind", "reason", "event_head"))
    if value["kind"] not in ("approve", "refuse"):
        _refuse("invalid_enum", f"{path}.kind", "expected approve or refuse")
    _text(value["reason"], f"{path}.reason", max_bytes=1024)
    if value["event_head"] is not None:
        _sha256(value["event_head"], f"{path}.event_head")
    return value


def _validate_ceo_lineage(value, path):
    _closed(value, path, ("state_heads", "event_heads", "plan_heads"))
    for field in ("state_heads", "event_heads", "plan_heads"):
        _bounded_sha_list(value[field], f"{path}.{field}", MAX_CEO_LINEAGE)
    return value


def _validate_ceo_directive(value, path):
    directive = _closed(value, path, ("kind", "target_refs", "preferences"))
    if directive["kind"] not in ("refine", "compare", "keep", "select"):
        _refuse(
            "invalid_enum",
            f"{path}.kind",
            "expected refine, compare, keep, or select",
        )
    _bounded_sha_list(
        directive["target_refs"],
        f"{path}.target_refs",
        MAX_REFS - 5,
    )
    if not isinstance(directive["preferences"], dict):
        _refuse(
            "object_required",
            f"{path}.preferences",
            "preference overrides must be a JSON object",
        )
    return value


def _validate_ceo_control(value, path):
    fields = (
        "mode",
        "active",
        "takeover_id",
        "return_phase",
        "anchor",
        "affected_dimensions",
        "paused_dimensions",
        "unaffected_dimensions",
        "directive",
        "successor_task",
        "successor_plan_head",
        "preserved_evidence_heads",
        "history",
    )
    _closed(value, path, fields)
    if value["mode"] not in CEO_CONTROL_MODES:
        _refuse("invalid_enum", f"{path}.mode", "expected autonomous, guided, or detail")
    _boolean(value["active"], f"{path}.active")
    if value["takeover_id"] is not None:
        _identifier(value["takeover_id"], f"{path}.takeover_id")
    if value["return_phase"] is not None and value["return_phase"] not in CEO_PHASES:
        _refuse("invalid_enum", f"{path}.return_phase", "unknown return phase")
    if value["anchor"] is not None:
        anchor = _closed(
            value["anchor"],
            f"{path}.anchor",
            ("mission_id", "state_head", "frame_head", "locus", "parent_task_head"),
        )
        _identifier(anchor["mission_id"], f"{path}.anchor.mission_id")
        for field in ("state_head", "frame_head", "parent_task_head"):
            _sha256(anchor[field], f"{path}.anchor.{field}")
        _text(anchor["locus"], f"{path}.anchor.locus", max_bytes=256)
    for field in ("affected_dimensions", "paused_dimensions", "unaffected_dimensions"):
        _unique_strings(
            value[field],
            f"{path}.{field}",
            maximum=MAX_SUBJECTS,
            identifiers=True,
        )
    if value["directive"] is not None:
        _validate_ceo_directive(value["directive"], f"{path}.directive")
    if value["successor_task"] is not None:
        _validate_task(value["successor_task"], f"{path}.successor_task")
    if value["successor_plan_head"] is not None:
        _sha256(value["successor_plan_head"], f"{path}.successor_plan_head")
    _bounded_sha_list(
        value["preserved_evidence_heads"],
        f"{path}.preserved_evidence_heads",
        MAX_CEO_LINEAGE,
    )
    if not isinstance(value["history"], list) or len(value["history"]) > MAX_CEO_LINEAGE:
        _refuse(
            "too_many_items",
            f"{path}.history",
            f"control history exceeds {MAX_CEO_LINEAGE}",
        )
    for index, entry in enumerate(value["history"]):
        entry_path = f"{path}.history[{index}]"
        _closed(
            entry,
            entry_path,
            (
                "takeover_id",
                "mode",
                "command_head",
                "anchor_frame_head",
                "locus",
                "successor_task_head",
                "successor_plan_head",
                "outcome",
            ),
        )
        _identifier(entry["takeover_id"], f"{entry_path}.takeover_id")
        if entry["mode"] not in CEO_CONTROL_MODES - {"autonomous"}:
            _refuse("invalid_enum", f"{entry_path}.mode", "history takeover mode must be guided or detail")
        for field in (
            "command_head",
            "anchor_frame_head",
            "successor_task_head",
            "successor_plan_head",
        ):
            _sha256(entry[field], f"{entry_path}.{field}")
        _text(entry["locus"], f"{entry_path}.locus", max_bytes=256)
        if entry["outcome"] not in ("active", "returned_autonomous", "refused"):
            _refuse("invalid_enum", f"{entry_path}.outcome", "unknown takeover outcome")
    if value["active"]:
        if (
            value["mode"] == "autonomous"
            or value["takeover_id"] is None
            or value["return_phase"] is None
            or value["anchor"] is None
            or value["directive"] is None
            or value["successor_task"] is None
            or value["successor_plan_head"] is None
            or not value["affected_dimensions"]
        ):
            _refuse("invalid_state", path, "active takeover is missing bounded control state")
        if not value["history"]:
            _refuse("invalid_state", f"{path}.history", "active takeover requires history")
        latest = value["history"][-1]
        if (
            latest["takeover_id"] != value["takeover_id"]
            or latest["mode"] != value["mode"]
            or latest["successor_task_head"] != value["successor_task"]["head"]
            or latest["successor_plan_head"] != value["successor_plan_head"]
            or latest["outcome"] != "active"
        ):
            _refuse("invalid_state", f"{path}.history", "active takeover history does not match control state")
    else:
        if value["mode"] != "autonomous":
            _refuse("invalid_state", f"{path}.mode", "inactive control must be autonomous")
    return value


def _validate_ceo_state(value, path):
    body_fields = (
        "schema",
        "profile",
        "mission_id",
        "sequence",
        "phase",
        "status",
        "bindings",
        "mission",
        "active_task",
        "selected_dimensions",
        "budget",
        "artifacts",
        "accepted_evidence_heads",
        "control",
        "verification",
        "decision",
        "lineage",
        "provenance",
    )
    _closed(value, path, body_fields + ("head",))
    if value["schema"] != "microsol-ceo-state/2":
        _refuse("unsupported_schema", f"{path}.schema", "expected microsol-ceo-state/2")
    if value["profile"] != "microsol-ceo":
        _refuse("invalid_profile", f"{path}.profile", "expected microsol-ceo")
    _identifier(value["mission_id"], f"{path}.mission_id")
    _integer(value["sequence"], f"{path}.sequence", 0, MAX_CEO_LINEAGE)
    if value["phase"] not in CEO_PHASES:
        _refuse("invalid_enum", f"{path}.phase", "unknown CEO lifecycle phase")
    if value["status"] not in ("active", "refused", "verified_ready", "closed"):
        _refuse("invalid_enum", f"{path}.status", "unknown CEO lifecycle status")
    bindings = _closed(
        value["bindings"],
        f"{path}.bindings",
        ("command_head", "organization_head", "grant_head", "root_envelope_head", "policy_head"),
    )
    for field in bindings:
        _sha256(bindings[field], f"{path}.bindings.{field}")
    _validate_ceo_mission(value["mission"], f"{path}.mission")
    if value["active_task"] is not None:
        _validate_task(value["active_task"], f"{path}.active_task")
    if value["mission"]["accepted"] and value["active_task"] is None:
        _refuse("invalid_state", f"{path}.active_task", "accepted mission requires an active task")
    if value["active_task"] is not None and value["mission"]["task"] is not None:
        if (
            value["active_task"]["head"] != value["mission"]["task"]["head"]
            and value["mission"]["task"]["head"]
            not in value["active_task"]["provenance"]["parent_refs"]
        ):
            _refuse(
                "evidence_rewrite",
                f"{path}.active_task.provenance.parent_refs",
                "successor objective must retain the original mission task",
            )
    _unique_strings(
        value["selected_dimensions"],
        f"{path}.selected_dimensions",
        maximum=MAX_SUBJECTS,
        identifiers=True,
    )
    _validate_ceo_budget(value["budget"], f"{path}.budget")
    _validate_ceo_artifacts(value["artifacts"], f"{path}.artifacts")
    _bounded_sha_list(
        value["accepted_evidence_heads"],
        f"{path}.accepted_evidence_heads",
        MAX_CEO_LINEAGE,
    )
    if not set(value["artifacts"]["checkpoint_heads"]).issubset(
        set(value["accepted_evidence_heads"])
    ):
        _refuse(
            "evidence_rewrite",
            f"{path}.accepted_evidence_heads",
            "accepted checkpoint evidence cannot be removed from state",
        )
    _validate_ceo_control(value["control"], f"{path}.control")
    if (
        value["active_task"] is not None
        and value["mission"]["task"] is not None
        and value["active_task"]["head"] != value["mission"]["task"]["head"]
    ):
        if (
            not value["control"]["history"]
            or value["control"]["history"][-1]["successor_task_head"]
            != value["active_task"]["head"]
        ):
            _refuse(
                "evidence_rewrite",
                f"{path}.active_task",
                "active successor objective must remain in takeover history",
            )
    _validate_ceo_verification(value["verification"], f"{path}.verification")
    _validate_ceo_decision(value["decision"], f"{path}.decision")
    _validate_ceo_lineage(value["lineage"], f"{path}.lineage")
    _validate_provenance(value["provenance"], f"{path}.provenance")
    if value["phase"] == "closed" and value["status"] != "closed":
        _refuse("invalid_state", path, "closed phase requires closed status")
    if value["status"] == "closed" and value["phase"] != "closed":
        _refuse("invalid_state", path, "closed status requires closed phase")
    if value["phase"] == "handoff" and value["status"] not in ("refused", "verified_ready"):
        _refuse("invalid_state", path, "handoff phase requires refused or verified_ready status")
    if value["phase"] == "control_checkpoint" and not value["control"]["active"]:
        _refuse("invalid_state", path, "control checkpoint phase requires an active takeover")
    if value["phase"] != "control_checkpoint" and value["control"]["active"]:
        _refuse("invalid_state", path, "active takeover must remain in control checkpoint phase")
    if not set(value["control"]["preserved_evidence_heads"]).issubset(
        set(value["accepted_evidence_heads"])
    ):
        _refuse(
            "evidence_rewrite",
            f"{path}.control.preserved_evidence_heads",
            "takeover cannot discard previously accepted evidence",
        )
    _verify_head(value, path, "ceo_state", body_fields)
    return value


def _validate_ceo_event(value, path):
    body_fields = (
        "schema",
        "event_id",
        "event_type",
        "state_head",
        "data",
        "receipt",
        "provenance",
    )
    _closed(value, path, body_fields + ("head",))
    if value["schema"] != "microsol-ceo-event/1":
        _refuse("unsupported_schema", f"{path}.schema", "expected microsol-ceo-event/1")
    _identifier(value["event_id"], f"{path}.event_id")
    if value["event_type"] not in CEO_EVENT_TYPES:
        _refuse("invalid_enum", f"{path}.event_type", "unknown CEO lifecycle event")
    _sha256(value["state_head"], f"{path}.state_head")
    if not isinstance(value["data"], dict):
        _refuse("object_required", f"{path}.data", "event data must be an object")
    _validate_receipt(value["receipt"], f"{path}.receipt")
    _validate_provenance(value["provenance"], f"{path}.provenance", parents_required=True)
    for required_head in (value["state_head"], value["receipt"]["head"]):
        if required_head not in value["provenance"]["parent_refs"]:
            _refuse(
                "missing_receipt_binding",
                f"{path}.provenance.parent_refs",
                "event provenance must bind the prior state and exact event receipt",
            )
    _verify_head(value, path, "ceo_event", body_fields)
    return value


def _relative_repository_path(value, path):
    value = _text(value, path, max_bytes=512)
    if value.startswith("/") or value.endswith("/") or "\\" in value or "\x00" in value:
        _refuse("invalid_repository_path", path, "path must be relative, slash-separated, and normalized")
    segments = value.split("/")
    if any(segment in ("", ".", "..") for segment in segments):
        _refuse("invalid_repository_path", path, "path contains empty, current, or parent segments")
    return value


def _snapshot_content_bytes(value, path):
    _closed(value, path, ("encoding", "chunks"))
    if value["encoding"] not in ("utf-8", "base64"):
        _refuse("invalid_enum", f"{path}.encoding", "expected utf-8 or base64")
    chunks = value["chunks"]
    if not isinstance(chunks, list) or not chunks or len(chunks) > MAX_CONTENT_CHUNKS:
        _refuse(
            "list_required",
            f"{path}.chunks",
            f"expected 1..{MAX_CONTENT_CHUNKS} bounded content chunks",
        )
    checked = [
        _text(chunk, f"{path}.chunks[{index}]", allow_empty=True, max_bytes=MAX_STRING_BYTES)
        for index, chunk in enumerate(chunks)
    ]
    if value["encoding"] == "utf-8":
        data = "".join(checked).encode("utf-8")
    else:
        try:
            data = base64.b64decode("".join(checked).encode("ascii"), validate=True)
        except (UnicodeEncodeError, binascii.Error) as error:
            _refuse("malformed_base64", path, str(error))
    if len(data) > MAX_SNAPSHOT_BYTES:
        _refuse(
            "oversize_content",
            path,
            f"decoded content exceeds {MAX_SNAPSHOT_BYTES} bytes",
        )
    return data


def _validate_snapshot_entry(value, path):
    _closed(value, path, ("path", "kind", "bytes", "sha256", "content"))
    _relative_repository_path(value["path"], f"{path}.path")
    if value["kind"] != "file":
        _refuse("invalid_enum", f"{path}.kind", "repository snapshot inventory supports file entries")
    byte_count = _integer(value["bytes"], f"{path}.bytes", 0, MAX_SNAPSHOT_BYTES)
    digest = _sha256(value["sha256"], f"{path}.sha256")
    data = _snapshot_content_bytes(value["content"], f"{path}.content")
    if len(data) != byte_count:
        _refuse("content_length_mismatch", f"{path}.bytes", "declared byte count differs from content")
    actual = hashlib.sha256(data).hexdigest()
    if actual != digest:
        _refuse("content_hash_mismatch", f"{path}.sha256", f"expected exact content SHA-256 {actual}")
    return value


def _repository_inventory_material(inventory):
    return [
        {
            "path": entry["path"],
            "kind": entry["kind"],
            "bytes": entry["bytes"],
            "sha256": entry["sha256"],
            "encoding": entry["content"]["encoding"],
        }
        for entry in sorted(inventory, key=lambda item: item["path"])
    ]


def _validate_repository_snapshot(value, path):
    body_fields = (
        "schema",
        "snapshot_id",
        "repository_id",
        "scope_head",
        "inventory_head",
        "inventory",
        "scope_receipt",
        "capture_receipt",
        "provenance",
    )
    _closed(value, path, body_fields + ("head",))
    if value["schema"] != "autobest-repository-snapshot/1":
        _refuse("unsupported_schema", f"{path}.schema", "expected autobest-repository-snapshot/1")
    _identifier(value["snapshot_id"], f"{path}.snapshot_id")
    _identifier(value["repository_id"], f"{path}.repository_id")
    _sha256(value["scope_head"], f"{path}.scope_head")
    _sha256(value["inventory_head"], f"{path}.inventory_head")
    inventory = value["inventory"]
    if not isinstance(inventory, list) or not inventory or len(inventory) > MAX_SNAPSHOT_FILES:
        _refuse(
            "list_required",
            f"{path}.inventory",
            f"expected 1..{MAX_SNAPSHOT_FILES} repository files",
        )
    seen_paths = set()
    total_bytes = 0
    for index, entry in enumerate(inventory):
        _validate_snapshot_entry(entry, f"{path}.inventory[{index}]")
        if entry["path"] in seen_paths:
            _refuse(
                "duplicate_item",
                f"{path}.inventory[{index}].path",
                "duplicate repository path",
            )
        seen_paths.add(entry["path"])
        total_bytes += entry["bytes"]
    if total_bytes > MAX_SNAPSHOT_BYTES:
        _refuse(
            "oversize_snapshot",
            f"{path}.inventory",
            f"snapshot exceeds {MAX_SNAPSHOT_BYTES} decoded bytes",
        )
    expected_inventory_head = canonical_digest(
        "repository-inventory/v1",
        _repository_inventory_material(inventory),
    )
    if value["inventory_head"] != expected_inventory_head:
        _refuse(
            "inventory_head_mismatch",
            f"{path}.inventory_head",
            f"expected canonical inventory head {expected_inventory_head}",
        )
    _validate_receipt(value["scope_receipt"], f"{path}.scope_receipt")
    _validate_receipt(value["capture_receipt"], f"{path}.capture_receipt")
    if value["scope_receipt"]["facts_head"] != value["scope_head"]:
        _refuse(
            "receipt_binding_mismatch",
            f"{path}.scope_receipt.facts_head",
            "scope receipt does not bind the supplied bounded scope",
        )
    if value["capture_receipt"]["facts_head"] != value["inventory_head"]:
        _refuse(
            "receipt_binding_mismatch",
            f"{path}.capture_receipt.facts_head",
            "capture receipt does not bind the canonical source inventory",
        )
    _validate_provenance(value["provenance"], f"{path}.provenance", parents_required=True)
    for receipt_head in (
        value["scope_receipt"]["head"],
        value["capture_receipt"]["head"],
    ):
        if receipt_head not in value["provenance"]["parent_refs"]:
            _refuse(
                "missing_receipt_binding",
                f"{path}.provenance.parent_refs",
                "snapshot provenance must retain scope and capture receipts",
            )
    _verify_head(value, path, "repository_snapshot", body_fields)
    return value


def _git_sha1(value, path):
    if (
        not isinstance(value, str)
        or len(value) != 40
        or any(character not in "0123456789abcdef" for character in value)
    ):
        _refuse("malformed_git_oid", path, "expected 40 lowercase hexadecimal characters")
    return value


def _repository_frame_inventory_material(inventory):
    return [
        {
            "path": entry["path"],
            "blob_sha1": entry["blob_sha1"],
            "content_sha256": entry["content_sha256"],
            "bytes": entry["bytes"],
        }
        for entry in sorted(inventory, key=lambda item: item["path"])
    ]


def _validate_repository_frame(value, path):
    body_fields = (
        "schema",
        "repository",
        "commit",
        "inventory_head",
        "inventory",
        "inventory_receipt",
        "provenance",
    )
    _closed(value, path, body_fields + ("head",))
    if value["schema"] != "autobest-repository-frame/1":
        _refuse("unsupported_schema", f"{path}.schema", "expected autobest-repository-frame/1")
    _identifier(value["repository"], f"{path}.repository")
    _git_sha1(value["commit"], f"{path}.commit")
    _sha256(value["inventory_head"], f"{path}.inventory_head")
    inventory = value["inventory"]
    if not isinstance(inventory, list) or not inventory or len(inventory) > MAX_REPOSITORY_ENTRIES:
        _refuse(
            "list_required",
            f"{path}.inventory",
            f"expected 1..{MAX_REPOSITORY_ENTRIES} repository entries",
        )
    seen = set()
    for index, entry in enumerate(inventory):
        entry_path = f"{path}.inventory[{index}]"
        _closed(
            entry,
            entry_path,
            ("path", "blob_sha1", "content_sha256", "bytes"),
        )
        _relative_repository_path(entry["path"], f"{entry_path}.path")
        _git_sha1(entry["blob_sha1"], f"{entry_path}.blob_sha1")
        _sha256(entry["content_sha256"], f"{entry_path}.content_sha256")
        _integer(entry["bytes"], f"{entry_path}.bytes", 0, MAX_INTEGER)
        if entry["path"] in seen:
            _refuse("duplicate_item", f"{entry_path}.path", "duplicate repository path")
        seen.add(entry["path"])
    expected_inventory_head = canonical_digest(
        "repository-frame-inventory/v1",
        _repository_frame_inventory_material(inventory),
    )
    if value["inventory_head"] != expected_inventory_head:
        _refuse(
            "inventory_head_mismatch",
            f"{path}.inventory_head",
            f"expected canonical inventory head {expected_inventory_head}",
        )
    _validate_receipt(value["inventory_receipt"], f"{path}.inventory_receipt")
    if value["inventory_receipt"]["facts_head"] != value["inventory_head"]:
        _refuse(
            "receipt_binding_mismatch",
            f"{path}.inventory_receipt.facts_head",
            "repository receipt does not bind exact inventory",
        )
    _validate_provenance(value["provenance"], f"{path}.provenance", parents_required=True)
    if value["inventory_receipt"]["head"] not in value["provenance"]["parent_refs"]:
        _refuse(
            "missing_receipt_binding",
            f"{path}.provenance.parent_refs",
            "repository Frame must retain inventory receipt",
        )
    _verify_head(value, path, "repository_frame", body_fields)
    return value


def _validate_adapter_resolution(value, path):
    body_fields = (
        "schema",
        "resolution_id",
        "native",
        "declared",
        "inferred",
        "reasons",
        "receipt",
        "provenance",
    )
    _closed(value, path, body_fields + ("head",))
    if value["schema"] != "autobest-adapter-resolution/1":
        _refuse("unsupported_schema", f"{path}.schema", "expected autobest-adapter-resolution/1")
    _identifier(value["resolution_id"], f"{path}.resolution_id")
    for field in ("native", "declared", "inferred"):
        if value[field] not in ("available", "unavailable"):
            _refuse("invalid_enum", f"{path}.{field}", "expected available or unavailable")
    _unique_strings(value["reasons"], f"{path}.reasons", maximum=MAX_REFS, allow_empty=False)
    _validate_receipt(value["receipt"], f"{path}.receipt")
    facts = {
        "native": value["native"],
        "declared": value["declared"],
        "inferred": value["inferred"],
        "reasons": list(value["reasons"]),
    }
    expected_facts_head = canonical_digest("adapter-resolution-facts/v1", facts)
    if value["receipt"]["facts_head"] != expected_facts_head:
        _refuse(
            "receipt_binding_mismatch",
            f"{path}.receipt.facts_head",
            "adapter receipt does not bind exact resolution facts",
        )
    _validate_provenance(value["provenance"], f"{path}.provenance", parents_required=True)
    if value["receipt"]["head"] not in value["provenance"]["parent_refs"]:
        _refuse(
            "missing_receipt_binding",
            f"{path}.provenance.parent_refs",
            "adapter resolution must retain its receipt",
        )
    _verify_head(value, path, "adapter_resolution", body_fields)
    return value


def _validate_hive_translation_policy(value, path):
    body_fields = (
        "schema",
        "policy_id",
        "version",
        "max_files",
        "max_total_bytes",
        "dimension_mode",
        "content_treatment",
        "unknown_treatment",
        "provenance",
    )
    _closed(value, path, body_fields + ("head",))
    if value["schema"] != "autobest-hive-translation-policy/1":
        _refuse(
            "unsupported_schema",
            f"{path}.schema",
            "expected autobest-hive-translation-policy/1",
        )
    _identifier(value["policy_id"], f"{path}.policy_id")
    _validate_version(value["version"], f"{path}.version")
    _integer(value["max_files"], f"{path}.max_files", 1, MAX_SNAPSHOT_FILES)
    _integer(
        value["max_total_bytes"],
        f"{path}.max_total_bytes",
        1,
        MAX_SNAPSHOT_BYTES,
    )
    if value["dimension_mode"] != "one-source-file-per-dimension":
        _refuse(
            "invalid_enum",
            f"{path}.dimension_mode",
            "fallback translation requires one-source-file-per-dimension",
        )
    if value["content_treatment"] != "preserve-exact-data":
        _refuse(
            "invalid_enum",
            f"{path}.content_treatment",
            "fallback translation must preserve exact repository data",
        )
    if value["unknown_treatment"] != "preserve-and-report":
        _refuse(
            "invalid_enum",
            f"{path}.unknown_treatment",
            "fallback translation must preserve and report semantic unknowns",
        )
    _validate_provenance(value["provenance"], f"{path}.provenance")
    _verify_head(value, path, "hive_translation_policy", body_fields)
    return value


def _validate_endpoint_capability(value, path):
    _closed(value, path, ("capability_id", "operations", "restrictions", "bounds"))
    _identifier(value["capability_id"], f"{path}.capability_id")
    _unique_strings(
        value["operations"],
        f"{path}.operations",
        maximum=MAX_ENDPOINT_OPERATIONS,
        allow_empty=False,
        identifiers=True,
    )
    _unique_strings(
        value["restrictions"],
        f"{path}.restrictions",
        maximum=MAX_REFS,
    )
    _resource_vector(value["bounds"], f"{path}.bounds")
    return value


def _validate_endpoint_operation(value, path):
    _closed(
        value,
        path,
        (
            "operation_id",
            "required",
            "input_schema_head",
            "output_schema_head",
            "required_capabilities",
            "restrictions",
            "bounds",
        ),
    )
    _identifier(value["operation_id"], f"{path}.operation_id")
    _boolean(value["required"], f"{path}.required")
    _sha256(value["input_schema_head"], f"{path}.input_schema_head")
    _sha256(value["output_schema_head"], f"{path}.output_schema_head")
    _unique_strings(
        value["required_capabilities"],
        f"{path}.required_capabilities",
        maximum=MAX_ENDPOINT_CAPABILITIES,
        identifiers=True,
    )
    _unique_strings(
        value["restrictions"],
        f"{path}.restrictions",
        maximum=MAX_REFS,
    )
    _resource_vector(value["bounds"], f"{path}.bounds")
    return value


def _validate_rapp1_endpoint(value, path):
    body_fields = (
        "schema",
        "endpoint_id",
        "protocol",
        "profile_id",
        "profile_head",
        "capabilities",
        "operations",
        "provenance",
    )
    _closed(value, path, body_fields + ("head",))
    if value["schema"] != "autobest-rapp1-endpoint/1":
        _refuse("unsupported_schema", f"{path}.schema", "expected autobest-rapp1-endpoint/1")
    _identifier(value["endpoint_id"], f"{path}.endpoint_id")
    if value["protocol"] != "RAPP/1":
        _refuse("protocol_mismatch", f"{path}.protocol", "compatibility Frame requires RAPP/1 endpoints")
    _identifier(value["profile_id"], f"{path}.profile_id")
    _sha256(value["profile_head"], f"{path}.profile_head")
    capabilities = value["capabilities"]
    operations = value["operations"]
    if not isinstance(capabilities, list) or not capabilities:
        _refuse("list_required", f"{path}.capabilities", "endpoint requires capabilities")
    if len(capabilities) > MAX_ENDPOINT_CAPABILITIES:
        _refuse(
            "too_many_items",
            f"{path}.capabilities",
            f"capability count exceeds {MAX_ENDPOINT_CAPABILITIES}",
        )
    if not isinstance(operations, list) or not operations:
        _refuse("list_required", f"{path}.operations", "endpoint requires protocol operations")
    if len(operations) > MAX_ENDPOINT_OPERATIONS:
        _refuse(
            "too_many_items",
            f"{path}.operations",
            f"operation count exceeds {MAX_ENDPOINT_OPERATIONS}",
        )
    capability_ids = set()
    operation_ids = set()
    for index, capability in enumerate(capabilities):
        _validate_endpoint_capability(capability, f"{path}.capabilities[{index}]")
        if capability["capability_id"] in capability_ids:
            _refuse(
                "duplicate_item",
                f"{path}.capabilities[{index}].capability_id",
                "duplicate capability id",
            )
        capability_ids.add(capability["capability_id"])
    for index, operation in enumerate(operations):
        _validate_endpoint_operation(operation, f"{path}.operations[{index}]")
        if operation["operation_id"] in operation_ids:
            _refuse(
                "duplicate_item",
                f"{path}.operations[{index}].operation_id",
                "duplicate operation id",
            )
        operation_ids.add(operation["operation_id"])
    for index, capability in enumerate(capabilities):
        unknown = sorted(set(capability["operations"]) - operation_ids)
        if unknown:
            _refuse(
                "binding_mismatch",
                f"{path}.capabilities[{index}].operations",
                "capability names unknown endpoint operations: " + ", ".join(unknown),
            )
    _validate_provenance(value["provenance"], f"{path}.provenance")
    _verify_head(value, path, "rapp1_endpoint", body_fields)
    return value


def _validate_static_map_spec(value, path):
    _closed(
        value,
        path,
        ("schema", "mode", "field_map", "constants", "preserve_unmapped"),
    )
    if value["schema"] != "autobest-static-field-map/1" or value["mode"] != "field-map":
        _refuse("unsupported_schema", path, "expected autobest-static-field-map/1 field-map")
    if not isinstance(value["field_map"], list) or len(value["field_map"]) > MAX_STATIC_MAP_FIELDS:
        _refuse(
            "too_many_items",
            f"{path}.field_map",
            f"field map exceeds {MAX_STATIC_MAP_FIELDS}",
        )
    source_fields = set()
    target_fields = set()
    for index, item in enumerate(value["field_map"]):
        item_path = f"{path}.field_map[{index}]"
        _closed(item, item_path, ("source", "target", "required"))
        _identifier(item["source"], f"{item_path}.source")
        _identifier(item["target"], f"{item_path}.target")
        _boolean(item["required"], f"{item_path}.required")
        if item["source"] in source_fields or item["target"] in target_fields:
            _refuse("duplicate_item", item_path, "field map sources and targets must be unique")
        source_fields.add(item["source"])
        target_fields.add(item["target"])
    if not isinstance(value["constants"], dict):
        _refuse("object_required", f"{path}.constants", "static map constants must be an object")
    _boolean(value["preserve_unmapped"], f"{path}.preserve_unmapped")
    return value


def _validate_static_transducer(value, path):
    fields = (
        "source_input_schema_head",
        "source_output_schema_head",
        "target_input_schema_head",
        "target_output_schema_head",
        "forward_input_map_head",
        "forward_output_map_head",
        "reverse_input_map_head",
        "reverse_output_map_head",
        "forward_input_spec",
        "forward_output_spec",
        "reverse_input_spec",
        "reverse_output_spec",
    )
    _closed(value, path, fields)
    for field in fields[:8]:
        _sha256(value[field], f"{path}.{field}")
    for field in fields[8:]:
        _validate_static_map_spec(value[field], f"{path}.{field}")
    spec_head_pairs = (
        ("forward_input_map_head", "forward_input_spec"),
        ("forward_output_map_head", "forward_output_spec"),
        ("reverse_input_map_head", "reverse_input_spec"),
        ("reverse_output_map_head", "reverse_output_spec"),
    )
    for head_field, spec_field in spec_head_pairs:
        expected = canonical_digest("static-field-map/v1", value[spec_field])
        if value[head_field] != expected:
            _refuse(
                "head_mismatch",
                f"{path}.{head_field}",
                f"expected static map head {expected}",
            )
    return value


def _validate_compatibility_mapping(value, path):
    _closed(
        value,
        path,
        (
            "mapping_id",
            "source_capability_id",
            "source_operation_id",
            "target_operation_id",
            "transducer",
            "weight_bps",
            "coverage_bps",
            "gaps",
            "restrictions",
            "bounds",
        ),
    )
    _identifier(value["mapping_id"], f"{path}.mapping_id")
    _identifier(value["source_capability_id"], f"{path}.source_capability_id")
    _identifier(value["source_operation_id"], f"{path}.source_operation_id")
    _identifier(value["target_operation_id"], f"{path}.target_operation_id")
    _validate_static_transducer(value["transducer"], f"{path}.transducer")
    _bp(value["weight_bps"], f"{path}.weight_bps")
    _bp(value["coverage_bps"], f"{path}.coverage_bps")
    _unique_strings(value["gaps"], f"{path}.gaps", maximum=MAX_REFS)
    _unique_strings(value["restrictions"], f"{path}.restrictions", maximum=MAX_REFS)
    _resource_vector(value["bounds"], f"{path}.bounds")
    return value


def _validate_portable_agent_artifact(value, path):
    _closed(
        value,
        path,
        (
            "agent_sha256",
            "agent_bytes",
            "content_address",
            "metadata_head",
            "tests_head",
            "private_hive_receipt",
        ),
    )
    agent_sha = _sha256(value["agent_sha256"], f"{path}.agent_sha256")
    _integer(value["agent_bytes"], f"{path}.agent_bytes", 1, MAX_AGENT_FILE_BYTES)
    _sha256_content_address(value["content_address"], agent_sha, f"{path}.content_address")
    _sha256(value["metadata_head"], f"{path}.metadata_head")
    _sha256(value["tests_head"], f"{path}.tests_head")
    _validate_receipt(value["private_hive_receipt"], f"{path}.private_hive_receipt")
    expected_facts_head = canonical_digest(
        "portable-agent-artifact/v1",
        {
            "agent_sha256": agent_sha,
            "agent_bytes": value["agent_bytes"],
            "content_address": value["content_address"],
            "metadata_head": value["metadata_head"],
            "tests_head": value["tests_head"],
        },
    )
    if value["private_hive_receipt"]["facts_head"] != expected_facts_head:
        _refuse(
            "receipt_binding_mismatch",
            f"{path}.private_hive_receipt.facts_head",
            "Private Hive receipt does not bind portable agent.py, metadata, and tests",
        )
    return value


def _validate_compatibility_lens(value, path):
    body_fields = (
        "schema",
        "lens_id",
        "version",
        "artifact_role",
        "hotload_lock_head",
        "portable_artifact",
        "minimum_coverage_bps",
        "allow_partial",
        "mappings",
        "provenance",
    )
    _closed(value, path, body_fields + ("head",))
    if value["schema"] != "autobest-compatibility-lens/1":
        _refuse("unsupported_schema", f"{path}.schema", "expected autobest-compatibility-lens/1")
    _identifier(value["lens_id"], f"{path}.lens_id")
    _validate_version(value["version"], f"{path}.version")
    if value["artifact_role"] != "locked-static-transducer":
        _refuse(
            "invalid_enum",
            f"{path}.artifact_role",
            "compatibility Lens record is the locked static transducer artifact",
        )
    _sha256(value["hotload_lock_head"], f"{path}.hotload_lock_head")
    _validate_portable_agent_artifact(
        value["portable_artifact"],
        f"{path}.portable_artifact",
    )
    _bp(value["minimum_coverage_bps"], f"{path}.minimum_coverage_bps")
    _boolean(value["allow_partial"], f"{path}.allow_partial")
    mappings = value["mappings"]
    if not isinstance(mappings, list) or not mappings:
        _refuse("list_required", f"{path}.mappings", "Lens requires compatibility mappings")
    if len(mappings) > MAX_COMPATIBILITY_MAPPINGS:
        _refuse(
            "too_many_items",
            f"{path}.mappings",
            f"mapping count exceeds {MAX_COMPATIBILITY_MAPPINGS}",
        )
    mapping_ids = set()
    target_operations = set()
    weight_total = 0
    for index, mapping in enumerate(mappings):
        _validate_compatibility_mapping(mapping, f"{path}.mappings[{index}]")
        if mapping["mapping_id"] in mapping_ids:
            _refuse(
                "duplicate_item",
                f"{path}.mappings[{index}].mapping_id",
                "duplicate mapping id",
            )
        if mapping["target_operation_id"] in target_operations:
            _refuse(
                "duplicate_item",
                f"{path}.mappings[{index}].target_operation_id",
                "target operation may appear in only one mapping",
            )
        mapping_ids.add(mapping["mapping_id"])
        target_operations.add(mapping["target_operation_id"])
        weight_total += mapping["weight_bps"]
    if weight_total != 10_000:
        _refuse(
            "weight_sum",
            f"{path}.mappings",
            f"compatibility mapping weights must sum exactly to 10000, got {weight_total}",
        )
    _validate_provenance(value["provenance"], f"{path}.provenance")
    _verify_head(value, path, "compatibility_lens", body_fields)
    return value


def _validate_compatibility_frame(value, path):
    body_fields = (
        "schema",
        "application",
        "protocol",
        "source",
        "target",
        "lens",
        "mappings",
        "coverage",
        "gaps",
        "restrictions",
        "bounds",
        "generic_consumers",
        "frame_count",
        "bespoke_runtime_required",
        "active_lens",
        "runtime_mode",
        "runtime_model_calls",
        "jit_wake_triggers",
        "native_model_history_persisted",
        "learning_evidence",
        "continuous_ai_translation",
        "mapping_exhaust_required_for_mutation",
        "predecessor_frame_head",
        "exhaust_head",
        "mutation_index",
        "activated",
        "adopted",
        "authority_granted",
        "later_mutation_requires_successor_frame",
    )
    _closed(value, path, body_fields + ("head",))
    if value["schema"] != "rapp-application-frame-candidate/1":
        _refuse(
            "unsupported_schema",
            f"{path}.schema",
            "expected rapp-application-frame-candidate/1",
        )
    if value["application"] != "compatibility" or value["protocol"] != "RAPP/1":
        _refuse("invalid_frame", path, "expected a RAPP/1 compatibility application Frame candidate")
    _closed(
        value["source"],
        f"{path}.source",
        ("endpoint_head", "endpoint_id", "profile_id", "profile_head", "capabilities"),
    )
    _closed(
        value["target"],
        f"{path}.target",
        ("endpoint_head", "endpoint_id", "profile_id", "profile_head", "operations"),
    )
    for side in ("source", "target"):
        _sha256(value[side]["endpoint_head"], f"{path}.{side}.endpoint_head")
        _identifier(value[side]["endpoint_id"], f"{path}.{side}.endpoint_id")
        _identifier(value[side]["profile_id"], f"{path}.{side}.profile_id")
        _sha256(value[side]["profile_head"], f"{path}.{side}.profile_head")
    _closed(
        value["lens"],
        f"{path}.lens",
        (
            "lens_head",
            "lens_id",
            "version",
            "artifact_role",
            "hotload_lock_head",
            "portable_artifact",
            "allow_partial",
            "minimum_coverage_bps",
        ),
    )
    _sha256(value["lens"]["lens_head"], f"{path}.lens.lens_head")
    _validate_portable_agent_artifact(
        value["lens"]["portable_artifact"],
        f"{path}.lens.portable_artifact",
    )
    if not isinstance(value["mappings"], list) or not value["mappings"]:
        _refuse("list_required", f"{path}.mappings", "compatibility Frame requires mappings")
    mapping_ids = set()
    for index, mapping in enumerate(value["mappings"]):
        mapping_path = f"{path}.mappings[{index}]"
        _closed(
            mapping,
            mapping_path,
            (
                "mapping_id",
                "source_capability_id",
                "source_operation_id",
                "source_operations",
                "target_operation_id",
                "transducer",
                "target_operation_required",
                "weight_bps",
                "coverage_bps",
                "declared_gaps",
                "structural_gaps",
                "gaps",
                "restrictions",
                "bounds",
            ),
        )
        _identifier(mapping["mapping_id"], f"{mapping_path}.mapping_id")
        if mapping["mapping_id"] in mapping_ids:
            _refuse("duplicate_item", f"{mapping_path}.mapping_id", "duplicate Frame mapping")
        mapping_ids.add(mapping["mapping_id"])
        _validate_static_transducer(mapping["transducer"], f"{mapping_path}.transducer")
        _resource_vector(mapping["bounds"], f"{mapping_path}.bounds")
    _resource_vector(value["bounds"], f"{path}.bounds")
    if value["generic_consumers"] != ["socket", "agent"]:
        _refuse("invalid_frame", f"{path}.generic_consumers", "expected generic socket and agent consumers")
    if value["frame_count"] != 1 or value["bespoke_runtime_required"] is not False:
        _refuse("invalid_frame", path, "compatibility adaptation must remain one Frame with no bespoke runtime")
    if value["active_lens"] != "brainstem-double-hotload":
        _refuse("invalid_frame", f"{path}.active_lens", "active Lens must be Brainstem double hotload")
    if value["runtime_mode"] != "locked-deterministic-agent-hotload":
        _refuse(
            "invalid_frame",
            f"{path}.runtime_mode",
            "expected locked deterministic agent hotload",
        )
    if value["runtime_model_calls"] != 0:
        _refuse("invalid_frame", f"{path}.runtime_model_calls", "normal compatibility traffic must use zero model calls")
    runtime_triggers = ["typed-exhaust"]
    if value["jit_wake_triggers"] != runtime_triggers:
        _refuse("invalid_frame", f"{path}.jit_wake_triggers", "unexpected JIT wake trigger set")
    if value["native_model_history_persisted"] is not False:
        _refuse(
            "privacy_refusal",
            f"{path}.native_model_history_persisted",
            "static Frame cannot persist native model history",
        )
    learning = _closed(
        value["learning_evidence"],
        f"{path}.learning_evidence",
        (
            "hotload_result_head",
            "trigger",
            "fixture_heads",
            "exhaust_heads",
            "transformation_receipt_heads",
            "placement_receipt_heads",
            "unload_receipt_heads",
            "portable_agent_content_address",
            "portable_agent_metadata_head",
            "portable_agent_tests_head",
            "private_hive_receipt_head",
            "learning_trace_head",
            "event_chain_head",
            "correction_fixture_head",
            "correction_fixtures",
        ),
    )
    _sha256(learning["hotload_result_head"], f"{path}.learning_evidence.hotload_result_head")
    if learning["trigger"] not in (
        "unmatched-handshake",
        "typed-exhaust",
        "rehearsal",
        "mapping-mutation",
    ):
        _refuse("invalid_enum", f"{path}.learning_evidence.trigger", "unknown learning trigger")
    for field in (
        "fixture_heads",
        "exhaust_heads",
        "transformation_receipt_heads",
        "placement_receipt_heads",
        "unload_receipt_heads",
    ):
        _bounded_sha_list(
            learning[field],
            f"{path}.learning_evidence.{field}",
            MAX_REHEARSAL_FIXTURES,
            allow_empty=field
            not in (
                "fixture_heads",
                "transformation_receipt_heads",
                "placement_receipt_heads",
                "unload_receipt_heads",
            ),
        )
    artifact = value["lens"]["portable_artifact"]
    _sha256_content_address(
        learning["portable_agent_content_address"],
        artifact["agent_sha256"],
        f"{path}.learning_evidence.portable_agent_content_address",
    )
    for field in (
        "portable_agent_metadata_head",
        "portable_agent_tests_head",
        "private_hive_receipt_head",
        "learning_trace_head",
        "event_chain_head",
        "correction_fixture_head",
    ):
        _sha256(learning[field], f"{path}.learning_evidence.{field}")
    if not isinstance(learning["correction_fixtures"], list):
        _refuse(
            "list_required",
            f"{path}.learning_evidence.correction_fixtures",
            "correction fixtures must be a list",
        )
    for index, fixture in enumerate(learning["correction_fixtures"]):
        _validate_trace_fixture(
            fixture,
            f"{path}.learning_evidence.correction_fixtures[{index}]",
        )
    expected_fixture_head = canonical_digest(
        "learning-trace-correction-fixtures/v1",
        sorted(
            learning["correction_fixtures"],
            key=lambda item: item["fixture_id"],
        ),
    )
    if learning["correction_fixture_head"] != expected_fixture_head:
        _refuse(
            "summary_drift",
            f"{path}.learning_evidence.correction_fixture_head",
            "correction fixture head differs from embedded fixtures",
        )
    if (
        learning["portable_agent_metadata_head"] != artifact["metadata_head"]
        or learning["portable_agent_tests_head"] != artifact["tests_head"]
        or learning["private_hive_receipt_head"]
        != artifact["private_hive_receipt"]["head"]
    ):
        _refuse(
            "binding_mismatch",
            f"{path}.learning_evidence",
            "learning evidence does not match portable agent artifact",
        )
    if value["continuous_ai_translation"] is not False:
        _refuse("invalid_frame", f"{path}.continuous_ai_translation", "continuous AI translation is forbidden")
    if value["mapping_exhaust_required_for_mutation"] is not True:
        _refuse(
            "invalid_frame",
            f"{path}.mapping_exhaust_required_for_mutation",
            "successor mutation requires typed mapping/data exhaust",
        )
    for field in ("predecessor_frame_head", "exhaust_head"):
        if value[field] is not None:
            _sha256(value[field], f"{path}.{field}")
    _integer(value["mutation_index"], f"{path}.mutation_index", 0, MAX_CEO_LINEAGE)
    if value["activated"] is not False or value["adopted"] is not False:
        _refuse("authority_shaped_input", path, "candidate Frame must remain inactive and unadopted")
    if value["authority_granted"] is not False:
        _refuse("authority_shaped_input", path, "candidate Frame grants no authority")
    if value["later_mutation_requires_successor_frame"] is not True:
        _refuse("invalid_frame", path, "later mutation must create a successor Frame")
    _sha256(value["head"], f"{path}.head")
    body = {field: value[field] for field in body_fields}
    expected = canonical_digest("compatibility-application-frame/v1", body)
    if value["head"] != expected:
        _refuse("head_mismatch", f"{path}.head", f"expected compatibility Frame head {expected}")
    return value


def _validate_compatibility_exhaust(value, path):
    body_fields = (
        "schema",
        "exhaust_id",
        "predecessor_frame_head",
        "direction",
        "channel",
        "mapping_id",
        "data_head",
        "expected_schema_head",
        "actual_schema_head",
        "reason",
        "runtime_receipt",
        "provenance",
    )
    _closed(value, path, body_fields + ("head",))
    if value["schema"] != "autobest-compatibility-exhaust/1":
        _refuse(
            "unsupported_schema",
            f"{path}.schema",
            "expected autobest-compatibility-exhaust/1",
        )
    _identifier(value["exhaust_id"], f"{path}.exhaust_id")
    for field in (
        "predecessor_frame_head",
        "data_head",
        "expected_schema_head",
        "actual_schema_head",
    ):
        _sha256(value[field], f"{path}.{field}")
    if value["direction"] not in ("source-to-target", "target-to-source"):
        _refuse("invalid_enum", f"{path}.direction", "unknown transducer direction")
    if value["channel"] not in ("input", "output"):
        _refuse("invalid_enum", f"{path}.channel", "unknown transducer channel")
    _identifier(value["mapping_id"], f"{path}.mapping_id")
    if value["reason"] not in ("typed-mapping-exhausted", "data-domain-exhausted"):
        _refuse("invalid_enum", f"{path}.reason", "unknown compatibility exhaust reason")
    _validate_receipt(value["runtime_receipt"], f"{path}.runtime_receipt")
    facts = {
        "predecessor_frame_head": value["predecessor_frame_head"],
        "direction": value["direction"],
        "channel": value["channel"],
        "mapping_id": value["mapping_id"],
        "data_head": value["data_head"],
        "expected_schema_head": value["expected_schema_head"],
        "actual_schema_head": value["actual_schema_head"],
        "reason": value["reason"],
    }
    expected_facts_head = canonical_digest("compatibility-exhaust-facts/v1", facts)
    if value["runtime_receipt"]["facts_head"] != expected_facts_head:
        _refuse(
            "receipt_binding_mismatch",
            f"{path}.runtime_receipt.facts_head",
            "runtime receipt does not bind exact typed exhaust facts",
        )
    _validate_provenance(value["provenance"], f"{path}.provenance", parents_required=True)
    for parent in (value["predecessor_frame_head"], value["runtime_receipt"]["head"]):
        if parent not in value["provenance"]["parent_refs"]:
            _refuse(
                "missing_receipt_binding",
                f"{path}.provenance.parent_refs",
                "exhaust must retain predecessor Frame and runtime receipt",
            )
    _verify_head(value, path, "compatibility_exhaust", body_fields)
    return value


def _validate_hotload_pass(value, path, pass_name):
    fields = (
        "agent_sha256",
        "agent_bytes",
        "agent_content_address",
        "slot_id",
        "agent_receipt",
        "placement_receipt",
        "prompt_head",
        "prompt_receipt",
        "policy_head",
        "policy_receipt",
        "budget",
        "input_head",
        "output_payload",
        "output_head",
        "output_receipt",
        "unload_receipt",
    )
    _closed(value, path, fields)
    agent_sha = _sha256(value["agent_sha256"], f"{path}.agent_sha256")
    _integer(value["agent_bytes"], f"{path}.agent_bytes", 1, MAX_AGENT_FILE_BYTES)
    _sha256_content_address(
        value["agent_content_address"],
        agent_sha,
        f"{path}.agent_content_address",
    )
    _identifier(value["slot_id"], f"{path}.slot_id")
    _validate_receipt(value["agent_receipt"], f"{path}.agent_receipt")
    if value["agent_receipt"]["facts_head"] != agent_sha:
        _refuse(
            "receipt_binding_mismatch",
            f"{path}.agent_receipt.facts_head",
            f"{pass_name} agent receipt does not bind exact hotloaded bytes",
        )
    _validate_receipt(value["placement_receipt"], f"{path}.placement_receipt")
    placement_facts_head = canonical_digest(
        "double-hotload-placement/v1",
        {
            "slot_id": value["slot_id"],
            "filename": "agent.py",
            "agent_sha256": agent_sha,
            "agent_bytes": value["agent_bytes"],
            "agent_content_address": value["agent_content_address"],
            "placement": "atomic-create-new",
            "regular_file": True,
        },
    )
    if value["placement_receipt"]["facts_head"] != placement_facts_head:
        _refuse(
            "receipt_binding_mismatch",
            f"{path}.placement_receipt.facts_head",
            f"{pass_name} placement receipt does not bind atomic regular-file placement",
        )
    for field in ("prompt_head", "policy_head", "input_head", "output_head"):
        _sha256(value[field], f"{path}.{field}")
    _resource_vector(value["budget"], f"{path}.budget")
    for field, head_field in (
        ("prompt_receipt", "prompt_head"),
        ("policy_receipt", "policy_head"),
        ("output_receipt", "output_head"),
    ):
        _validate_receipt(value[field], f"{path}.{field}")
        if value[field]["facts_head"] != value[head_field]:
            _refuse(
                "receipt_binding_mismatch",
                f"{path}.{field}.facts_head",
                f"{pass_name} {field} does not bind {head_field}",
            )
    if not isinstance(value["output_payload"], dict) or not value["output_payload"]:
        _refuse(
            "object_required",
            f"{path}.output_payload",
            f"{pass_name} output payload must be a non-empty inert object",
        )
    expected_output_head = canonical_digest(
        "double-hotload-output/v1",
        value["output_payload"],
    )
    if value["output_head"] != expected_output_head:
        _refuse(
            "head_mismatch",
            f"{path}.output_head",
            f"expected canonical {pass_name} output head {expected_output_head}",
        )
    _validate_receipt(value["unload_receipt"], f"{path}.unload_receipt")
    unload_facts_head = canonical_digest(
        "double-hotload-unload/v1",
        {
            "slot_id": value["slot_id"],
            "agent_sha256": agent_sha,
            "agent_content_address": value["agent_content_address"],
            "output_head": value["output_head"],
            "unloaded": True,
        },
    )
    if value["unload_receipt"]["facts_head"] != unload_facts_head:
        _refuse(
            "receipt_binding_mismatch",
            f"{path}.unload_receipt.facts_head",
            f"{pass_name} unload receipt does not prove deterministic unload",
        )
    return value


def _validate_double_hotload_result(value, path):
    body_fields = (
        "schema",
        "cycle_id",
        "cycle_index",
        "source_frame_head",
        "source_profile_head",
        "target_profile_head",
        "caller_intent_head",
        "jit_scope",
        "learning_trace",
        "pass1",
        "pass2",
        "rehearsal",
        "gate_audit",
        "locked",
        "provenance",
    )
    _closed(value, path, body_fields + ("head",))
    if value["schema"] != "autobest-double-hotload-result/1":
        _refuse(
            "unsupported_schema",
            f"{path}.schema",
            "expected autobest-double-hotload-result/1",
        )
    _identifier(value["cycle_id"], f"{path}.cycle_id")
    _integer(value["cycle_index"], f"{path}.cycle_index", 0, MAX_CEO_LINEAGE)
    for field in (
        "source_frame_head",
        "source_profile_head",
        "target_profile_head",
        "caller_intent_head",
    ):
        _sha256(value[field], f"{path}.{field}")
    jit_scope = _closed(
        value["jit_scope"],
        f"{path}.jit_scope",
        (
            "trigger",
            "frame_heads",
            "policy_heads",
            "budget",
            "max_passes",
            "persist_native_history",
            "slot_contract",
        ),
    )
    if jit_scope["trigger"] not in (
        "unmatched-handshake",
        "typed-exhaust",
        "rehearsal",
        "mapping-mutation",
    ):
        _refuse("invalid_enum", f"{path}.jit_scope.trigger", "unknown JIT wake trigger")
    _bounded_sha_list(
        jit_scope["frame_heads"],
        f"{path}.jit_scope.frame_heads",
        MAX_REHEARSAL_FIXTURES,
        allow_empty=False,
    )
    _bounded_sha_list(
        jit_scope["policy_heads"],
        f"{path}.jit_scope.policy_heads",
        MAX_REHEARSAL_FIXTURES,
        allow_empty=False,
    )
    _resource_vector(jit_scope["budget"], f"{path}.jit_scope.budget")
    if jit_scope["max_passes"] != 2:
        _refuse("invalid_state", f"{path}.jit_scope.max_passes", "double hotload requires exactly two passes")
    if jit_scope["persist_native_history"] is not False:
        _refuse(
            "privacy_refusal",
            f"{path}.jit_scope.persist_native_history",
            "native model sessions/history must not persist",
        )
    _validate_hotload_slot_contract(
        jit_scope["slot_contract"],
        f"{path}.jit_scope.slot_contract",
    )
    learning_trace = _validate_learning_trace(
        value["learning_trace"],
        f"{path}.learning_trace",
    )
    _validate_hotload_pass(value["pass1"], f"{path}.pass1", "pass1")
    _validate_hotload_pass(value["pass2"], f"{path}.pass2", "pass2")
    if value["pass1"]["input_head"] != value["source_frame_head"]:
        _refuse("binding_mismatch", f"{path}.pass1.input_head", "pass1 must consume immutable source Frame")
    if value["pass2"]["input_head"] != value["pass1"]["output_head"]:
        _refuse("binding_mismatch", f"{path}.pass2.input_head", "pass2 must consume pass1 candidate output")
    for pass_name in ("pass1", "pass2"):
        if value[pass_name]["slot_id"] != jit_scope["slot_contract"]["slot_id"]:
            _refuse(
                "scope_violation",
                f"{path}.{pass_name}.slot_id",
                "hotload pass uses a slot outside the isolated contract",
            )
    if value["source_frame_head"] not in jit_scope["frame_heads"]:
        _refuse("scope_violation", f"{path}.jit_scope.frame_heads", "JIT scope omits source Frame")
    if learning_trace["head"] not in jit_scope["frame_heads"]:
        _refuse("scope_violation", f"{path}.jit_scope.frame_heads", "JIT scope omits learning trace")
    pass_policy_heads = {value["pass1"]["policy_head"], value["pass2"]["policy_head"]}
    if not pass_policy_heads.issubset(set(jit_scope["policy_heads"])):
        _refuse("scope_violation", f"{path}.jit_scope.policy_heads", "JIT scope omits pass policy pins")
    combined_budget = {
        field: value["pass1"]["budget"][field] + value["pass2"]["budget"][field]
        for field in RESOURCE_FIELDS
    }
    if not _resource_leq(combined_budget, jit_scope["budget"]):
        _refuse("over_budget", f"{path}.jit_scope.budget", "two hotload passes exceed scoped budget")
    rehearsal = _closed(
        value["rehearsal"],
        f"{path}.rehearsal",
        (
            "fixture_heads",
            "exhaust_heads",
            "previous_cycle_head",
            "lock_requested",
            "repeat_required",
        ),
    )
    _bounded_sha_list(
        rehearsal["fixture_heads"],
        f"{path}.rehearsal.fixture_heads",
        MAX_REHEARSAL_FIXTURES,
        allow_empty=False,
    )
    _bounded_sha_list(
        rehearsal["exhaust_heads"],
        f"{path}.rehearsal.exhaust_heads",
        MAX_REHEARSAL_FIXTURES,
    )
    if rehearsal["previous_cycle_head"] is not None:
        _sha256(rehearsal["previous_cycle_head"], f"{path}.rehearsal.previous_cycle_head")
    _boolean(rehearsal["lock_requested"], f"{path}.rehearsal.lock_requested")
    _boolean(rehearsal["repeat_required"], f"{path}.rehearsal.repeat_required")
    if not set(rehearsal["exhaust_heads"]).issubset(set(jit_scope["frame_heads"])):
        _refuse("scope_violation", f"{path}.jit_scope.frame_heads", "JIT scope omits exhaust evidence")
    if (
        jit_scope["trigger"] in ("typed-exhaust", "mapping-mutation")
        and not rehearsal["exhaust_heads"]
    ):
        _refuse(
            "invalid_state",
            f"{path}.jit_scope.trigger",
            "post-lock mutation wake requires exhaust evidence",
        )
    _boolean(value["locked"], f"{path}.locked")
    if value["locked"] == rehearsal["repeat_required"]:
        _refuse("invalid_state", path, "locked and repeat_required must be opposites")
    if not isinstance(value["gate_audit"], list):
        _refuse("list_required", f"{path}.gate_audit", "gate audit must be a list")
    for index, item in enumerate(value["gate_audit"]):
        item_path = f"{path}.gate_audit[{index}]"
        _closed(item, item_path, ("gate", "passed", "receipt_head"))
        _identifier(item["gate"], f"{item_path}.gate")
        _boolean(item["passed"], f"{item_path}.passed")
        _sha256(item["receipt_head"], f"{item_path}.receipt_head")
    if value["locked"]:
        required_gates = {"schema", "invariant", "privacy", "authority", "replay", "mutation"}
        observed = {item["gate"] for item in value["gate_audit"]}
        if observed != required_gates or any(item["passed"] is not True for item in value["gate_audit"]):
            _refuse("invalid_state", f"{path}.gate_audit", "locked result requires all six passed gates")
    _validate_provenance(value["provenance"], f"{path}.provenance", parents_required=True)
    _verify_head(value, path, "double_hotload_result", body_fields)
    return value


def _reject_trace_privacy_leakage(value, path):
    forbidden_keys = {
        "raw",
        "raw_transcript",
        "transcript",
        "hidden_reasoning",
        "reasoning",
        "chain_of_thought",
        "local_path",
        "tokens",
        "token_count",
        "private_payload",
        "session_history",
        "native_history",
    }
    if isinstance(value, dict):
        for key, item in value.items():
            normalized = key.lower().replace("-", "_")
            if normalized in forbidden_keys:
                _refuse(
                    "privacy_leakage",
                    f"{path}.{key}",
                    "learning trace may contain only sanitized structured evidence",
                )
            _reject_trace_privacy_leakage(item, f"{path}.{key}")
    elif isinstance(value, list):
        for index, item in enumerate(value):
            _reject_trace_privacy_leakage(item, f"{path}[{index}]")
    elif isinstance(value, str):
        lowered = value.lower()
        if (
            "/users/" in lowered
            or "/home/" in lowered
            or "c:\\" in lowered
            or "bearer " in lowered
            or lowered.startswith("sk-")
        ):
            _refuse(
                "privacy_leakage",
                path,
                "learning trace contains a local path or credential-shaped string",
            )


def _validate_trace_fixture(value, path):
    _closed(
        value,
        path,
        (
            "fixture_id",
            "mapping_id",
            "direction",
            "channel",
            "assertion",
            "schema_head",
            "expected_code",
        ),
    )
    _identifier(value["fixture_id"], f"{path}.fixture_id")
    _identifier(value["mapping_id"], f"{path}.mapping_id")
    if value["direction"] not in ("source-to-target", "target-to-source"):
        _refuse("invalid_enum", f"{path}.direction", "unknown fixture direction")
    if value["channel"] not in ("input", "output"):
        _refuse("invalid_enum", f"{path}.channel", "unknown fixture channel")
    if value["assertion"] not in (
        "bounded-transform",
        "typed-schema-refusal",
        "declared-gap-refusal",
    ):
        _refuse("invalid_enum", f"{path}.assertion", "unknown correction fixture assertion")
    _sha256(value["schema_head"], f"{path}.schema_head")
    _identifier(value["expected_code"], f"{path}.expected_code")
    return value


def _trace_event_head(event_body):
    return canonical_digest("learning-trace-event/v1", event_body)


def _trace_summary(events):
    event_types = (
        "intent",
        "proposal",
        "user_correction",
        "measured_result",
        "superseded_assumption",
        "successor_invariant",
    )
    counts = {event_type: 0 for event_type in event_types}
    correction_ids = []
    invariant_ids = []
    fixtures = []
    for event in events:
        counts[event["event_type"]] += 1
        if event["event_type"] == "user_correction":
            correction_ids.append(event["data"]["correction_id"])
        elif event["event_type"] == "successor_invariant":
            invariant_ids.append(event["data"]["invariant_id"])
            fixtures.append(event["data"]["fixture"])
    return {
        "event_count": len(events),
        "event_type_counts": counts,
        "correction_ids": sorted(correction_ids),
        "successor_invariant_ids": sorted(invariant_ids),
        "correction_fixture_head": canonical_digest(
            "learning-trace-correction-fixtures/v1",
            sorted(fixtures, key=lambda item: item["fixture_id"]),
        ),
    }


def _trace_correction_fixtures(trace):
    return sorted(
        [
            _json_copy(event["data"]["fixture"])
            for event in trace["events"]
            if event["event_type"] == "successor_invariant"
        ],
        key=lambda item: item["fixture_id"],
    )


def _validate_learning_trace_event(value, path, commitments):
    body_fields = (
        "sequence",
        "event_type",
        "actor",
        "source_head",
        "previous_event_head",
        "data",
    )
    _closed(value, path, body_fields + ("event_head",))
    _integer(value["sequence"], f"{path}.sequence", 0, MAX_TRACE_EVENTS - 1)
    if value["event_type"] not in (
        "intent",
        "proposal",
        "user_correction",
        "measured_result",
        "superseded_assumption",
        "successor_invariant",
    ):
        _refuse("invalid_enum", f"{path}.event_type", "unknown learning trace event")
    if value["actor"] not in ("user", "assistant", "tool", "agent", "host"):
        _refuse("invalid_enum", f"{path}.actor", "unknown trace actor")
    _sha256(value["source_head"], f"{path}.source_head")
    if value["source_head"] not in commitments.get(value["actor"], set()):
        _refuse(
            "source_commitment_mismatch",
            f"{path}.source_head",
            "trace event source is not committed for its actor",
        )
    if value["previous_event_head"] is not None:
        _sha256(value["previous_event_head"], f"{path}.previous_event_head")
    if not isinstance(value["data"], dict):
        _refuse("object_required", f"{path}.data", "trace event data must be an object")
    event_type = value["event_type"]
    data_path = f"{path}.data"
    if event_type == "intent":
        _closed(value["data"], data_path, ("intent_id", "goal_head", "scope_heads"))
        if value["actor"] != "user":
            _refuse("forged_user_decision", path, "intent must originate from committed user source")
        _identifier(value["data"]["intent_id"], f"{data_path}.intent_id")
        _sha256(value["data"]["goal_head"], f"{data_path}.goal_head")
        _bounded_sha_list(
            value["data"]["scope_heads"],
            f"{data_path}.scope_heads",
            MAX_REFS,
        )
    elif event_type == "proposal":
        _closed(value["data"], data_path, ("proposal_id", "proposal_head", "assumption_ids"))
        if value["actor"] != "assistant":
            _refuse("invalid_actor", path, "proposal must originate from assistant")
        _identifier(value["data"]["proposal_id"], f"{data_path}.proposal_id")
        _sha256(value["data"]["proposal_head"], f"{data_path}.proposal_head")
        _unique_strings(
            value["data"]["assumption_ids"],
            f"{data_path}.assumption_ids",
            maximum=MAX_REFS,
            identifiers=True,
        )
    elif event_type == "user_correction":
        _closed(
            value["data"],
            data_path,
            (
                "correction_id",
                "decision",
                "proposal_id",
                "superseded_assumption_ids",
                "successor_invariant_ids",
                "decision_receipt",
            ),
        )
        if value["actor"] != "user":
            _refuse("forged_user_decision", path, "correction must originate from committed user source")
        _identifier(value["data"]["correction_id"], f"{data_path}.correction_id")
        if value["data"]["decision"] not in ("accept", "reject", "replace", "constrain"):
            _refuse("invalid_enum", f"{data_path}.decision", "unknown user correction decision")
        _identifier(value["data"]["proposal_id"], f"{data_path}.proposal_id")
        _unique_strings(
            value["data"]["superseded_assumption_ids"],
            f"{data_path}.superseded_assumption_ids",
            maximum=MAX_REFS,
            identifiers=True,
        )
        _unique_strings(
            value["data"]["successor_invariant_ids"],
            f"{data_path}.successor_invariant_ids",
            maximum=MAX_REFS,
            allow_empty=False,
            identifiers=True,
        )
        _validate_receipt(value["data"]["decision_receipt"], f"{data_path}.decision_receipt")
        decision_facts = {
            "correction_id": value["data"]["correction_id"],
            "decision": value["data"]["decision"],
            "proposal_id": value["data"]["proposal_id"],
            "superseded_assumption_ids": list(
                value["data"]["superseded_assumption_ids"]
            ),
            "successor_invariant_ids": list(
                value["data"]["successor_invariant_ids"]
            ),
        }
        expected = canonical_digest("learning-trace-user-decision/v1", decision_facts)
        if value["data"]["decision_receipt"]["facts_head"] != expected:
            _refuse(
                "forged_user_decision",
                f"{data_path}.decision_receipt.facts_head",
                "user correction receipt does not bind exact decision",
            )
    elif event_type == "measured_result":
        _closed(
            value["data"],
            data_path,
            (
                "result_id",
                "operation_id",
                "status",
                "input_head",
                "output_head",
                "error_code",
                "metrics",
                "result_receipt",
            ),
        )
        if value["actor"] not in ("tool", "agent"):
            _refuse("invalid_actor", path, "measured result must originate from tool or agent")
        _identifier(value["data"]["result_id"], f"{data_path}.result_id")
        _identifier(value["data"]["operation_id"], f"{data_path}.operation_id")
        if value["data"]["status"] not in ("success", "failure"):
            _refuse("invalid_enum", f"{data_path}.status", "unknown measured status")
        _sha256(value["data"]["input_head"], f"{data_path}.input_head")
        if value["data"]["output_head"] is not None:
            _sha256(value["data"]["output_head"], f"{data_path}.output_head")
        if value["data"]["error_code"] is not None:
            _identifier(value["data"]["error_code"], f"{data_path}.error_code")
        _closed(
            value["data"]["metrics"],
            f"{data_path}.metrics",
            ("duration_ms", "output_bytes", "tool_calls", "status_code"),
        )
        for metric, metric_value in value["data"]["metrics"].items():
            _integer(metric_value, f"{data_path}.metrics.{metric}", 0, MAX_RESOURCE)
        _validate_receipt(value["data"]["result_receipt"], f"{data_path}.result_receipt")
        result_facts = {
            key: value["data"][key]
            for key in (
                "result_id",
                "operation_id",
                "status",
                "input_head",
                "output_head",
                "error_code",
                "metrics",
            )
        }
        expected = canonical_digest("learning-trace-measured-result/v1", result_facts)
        if value["data"]["result_receipt"]["facts_head"] != expected:
            _refuse(
                "receipt_binding_mismatch",
                f"{data_path}.result_receipt.facts_head",
                "measured result receipt does not bind exact result/failure",
            )
    elif event_type == "superseded_assumption":
        _closed(
            value["data"],
            data_path,
            ("assumption_id", "correction_id", "assumption_head"),
        )
        _identifier(value["data"]["assumption_id"], f"{data_path}.assumption_id")
        _identifier(value["data"]["correction_id"], f"{data_path}.correction_id")
        _sha256(value["data"]["assumption_head"], f"{data_path}.assumption_head")
    else:
        _closed(
            value["data"],
            data_path,
            ("invariant_id", "invariant_head", "correction_id", "fixture"),
        )
        _identifier(value["data"]["invariant_id"], f"{data_path}.invariant_id")
        _sha256(value["data"]["invariant_head"], f"{data_path}.invariant_head")
        _identifier(value["data"]["correction_id"], f"{data_path}.correction_id")
        _validate_trace_fixture(value["data"]["fixture"], f"{data_path}.fixture")
    body = {field: value[field] for field in body_fields}
    expected_event_head = _trace_event_head(body)
    if value["event_head"] != expected_event_head:
        _refuse("head_mismatch", f"{path}.event_head", f"expected event head {expected_event_head}")
    return value


def _validate_learning_trace(value, path):
    body_fields = (
        "schema",
        "trace_id",
        "source_commitments",
        "events",
        "event_chain_head",
        "privacy",
        "summary",
        "provenance",
    )
    _closed(value, path, body_fields + ("head",))
    if value["schema"] != "autobest-sanitized-learning-trace/1":
        _refuse(
            "unsupported_schema",
            f"{path}.schema",
            "expected autobest-sanitized-learning-trace/1",
        )
    _identifier(value["trace_id"], f"{path}.trace_id")
    _reject_trace_privacy_leakage(value, path)
    commitments = {}
    if not isinstance(value["source_commitments"], list) or not value["source_commitments"]:
        _refuse("list_required", f"{path}.source_commitments", "trace requires source commitments")
    for index, commitment in enumerate(value["source_commitments"]):
        commitment_path = f"{path}.source_commitments[{index}]"
        _closed(commitment, commitment_path, ("actor", "source_head"))
        if commitment["actor"] not in ("user", "assistant", "tool", "agent", "host"):
            _refuse("invalid_enum", f"{commitment_path}.actor", "unknown commitment actor")
        _sha256(commitment["source_head"], f"{commitment_path}.source_head")
        commitments.setdefault(commitment["actor"], set()).add(commitment["source_head"])
    events = value["events"]
    if not isinstance(events, list) or not events or len(events) > MAX_TRACE_EVENTS:
        _refuse("list_required", f"{path}.events", f"expected 1..{MAX_TRACE_EVENTS} trace events")
    type_order = {
        "intent": 0,
        "proposal": 1,
        "user_correction": 2,
        "measured_result": 3,
        "superseded_assumption": 4,
        "successor_invariant": 5,
    }
    previous_head = None
    previous_rank = -1
    for index, event in enumerate(events):
        _validate_learning_trace_event(
            event,
            f"{path}.events[{index}]",
            commitments,
        )
        if event["sequence"] != index:
            _refuse("event_order", f"{path}.events[{index}].sequence", "trace sequence must be contiguous")
        if event["previous_event_head"] != previous_head:
            _refuse(
                "event_order",
                f"{path}.events[{index}].previous_event_head",
                "trace previous-event commitment is broken",
            )
        rank = type_order[event["event_type"]]
        if rank < previous_rank:
            _refuse("event_order", f"{path}.events[{index}].event_type", "trace event types are out of order")
        previous_rank = rank
        previous_head = event["event_head"]
    if value["event_chain_head"] != previous_head:
        _refuse("head_mismatch", f"{path}.event_chain_head", "trace chain head differs from final event")
    event_types = {event["event_type"] for event in events}
    required_types = set(type_order)
    if event_types != required_types:
        _refuse(
            "missing_correction",
            f"{path}.events",
            "trace must contain intent, proposal, correction, measured result, supersession, and successor invariant",
        )
    proposals = {
        event["data"]["proposal_id"]: event["data"]
        for event in events
        if event["event_type"] == "proposal"
    }
    corrections = {
        event["data"]["correction_id"]: event["data"]
        for event in events
        if event["event_type"] == "user_correction"
    }
    superseded = {
        (event["data"]["correction_id"], event["data"]["assumption_id"])
        for event in events
        if event["event_type"] == "superseded_assumption"
    }
    invariants = {
        event["data"]["invariant_id"]: event["data"]
        for event in events
        if event["event_type"] == "successor_invariant"
    }
    for correction_id, correction in corrections.items():
        if correction["proposal_id"] not in proposals:
            _refuse("missing_correction", path, "correction references unknown proposal")
        for assumption_id in correction["superseded_assumption_ids"]:
            if (correction_id, assumption_id) not in superseded:
                _refuse(
                    "missing_correction",
                    path,
                    "correction lacks matching superseded-assumption evidence",
                )
        for invariant_id in correction["successor_invariant_ids"]:
            invariant = invariants.get(invariant_id)
            if invariant is None or invariant["correction_id"] != correction_id:
                _refuse(
                    "missing_correction",
                    path,
                    "correction lacks matching successor invariant",
                )
    privacy = _closed(
        value["privacy"],
        f"{path}.privacy",
        (
            "raw_transcript_included",
            "hidden_reasoning_included",
            "local_paths_included",
            "token_data_included",
            "private_payloads_included",
        ),
    )
    if any(privacy.values()):
        _refuse("privacy_leakage", f"{path}.privacy", "all privacy inclusion flags must be false")
    expected_summary = _trace_summary(events)
    if value["summary"] != expected_summary:
        _refuse("summary_drift", f"{path}.summary", "trace summary differs from ordered events")
    _validate_provenance(value["provenance"], f"{path}.provenance")
    _verify_head(value, path, "learning_trace", body_fields)
    return value


def _score(metrics, weights):
    vector = []
    numerator = 0
    for name in sorted(weights):
        product = metrics[name] * weights[name]
        numerator += product
        vector.append(
            {
                "metric": name,
                "value_bps": metrics[name],
                "weight_bps": weights[name],
                "weighted_product": product,
            }
        )
    return numerator // 10_000, vector


def _lineage(records, component_refs=()):
    bound_heads = set()
    source_heads = set()
    parent_refs = set(component_refs)
    for record in records:
        if not isinstance(record, dict):
            continue
        if isinstance(record.get("head"), str):
            bound_heads.add(record["head"])
        provenance = record.get("provenance")
        if isinstance(provenance, dict):
            source_heads.add(provenance["source_head"])
            parent_refs.update(provenance["parent_refs"])
    return {
        "bound_heads": sorted(bound_heads),
        "source_heads": sorted(source_heads),
        "parent_refs": sorted(parent_refs),
    }


def _base_plan(operation):
    return {
        "operation": operation,
        "record_role": "candidate-data",
        "authority_granted": False,
        "authority_source": "external-host",
        "rapp1_role": "core-compatibility-substrate",
        "rapp1_compatibility_required": True,
        "executed": False,
        "workers_launched": 0,
        "frames_emitted": 0,
    }


def _finalize_plan(result, domain):
    result["plan_head"] = canonical_digest(domain, result)
    return result


def _proportional_shares(total, subjects, resource):
    if not subjects or total == 0:
        return {subject["observation"]["head"]: 0 for subject in subjects}
    total_fitness = sum(subject["fitness_bps"] for subject in subjects)
    shares = {}
    remainders = []
    allocated = 0
    for subject in subjects:
        head = subject["observation"]["head"]
        numerator = total * subject["fitness_bps"]
        share = numerator // total_fitness
        shares[head] = share
        allocated += share
        remainders.append(
            (
                -(numerator % total_fitness),
                canonical_digest(
                    "delegate-remainder/v1",
                    {
                        "observation_head": head,
                        "resource": resource,
                    },
                ),
                head,
            )
        )
    remainder = total - allocated
    for _, _, head in sorted(remainders)[:remainder]:
        shares[head] += 1
    return shares


def delegate(request):
    """Apply the Delegation Lens and return inert JIT assignment candidates."""

    _prepare_input(request, "$.request")
    fields = ("schema", "task", "root_envelope", "reservation", "policy", "observations")
    _closed(request, "$.request", fields)
    if request["schema"] != "autobest-delegate-request/1":
        _refuse("unsupported_schema", "$.request.schema", "expected autobest-delegate-request/1")
    task = _validate_task(request["task"], "$.request.task")
    root = _validate_root(request["root_envelope"], "$.request.root_envelope")
    reservation = _validate_reservation(request["reservation"], "$.request.reservation")
    policy = _validate_policy(request["policy"], "$.request.policy")
    observations = request["observations"]
    if not isinstance(observations, list) or not observations:
        _refuse("list_required", "$.request.observations", "at least one current observation is required")
    subject_cap = min(
        root["max_subjects"],
        policy["delegate"]["max_subjects"],
        MAX_SUBJECTS,
    )
    if len(observations) > subject_cap:
        _refuse("too_many_items", "$.request.observations", f"observation count exceeds cap {subject_cap}")
    seen_subjects = set()
    seen_dimensions = set()
    for index, observation in enumerate(observations):
        _validate_observation(observation, f"$.request.observations[{index}]", policy)
        subject_key = (observation["subject_kind"], observation["subject_id"])
        if subject_key in seen_subjects:
            _refuse("duplicate_item", f"$.request.observations[{index}].subject_id", "duplicate subject")
        if observation["dimension_id"] in seen_dimensions:
            _refuse(
                "dimension_not_sovereign",
                f"$.request.observations[{index}].dimension_id",
                "each worker or generation must retain a distinct Dimension",
            )
        seen_subjects.add(subject_key)
        seen_dimensions.add(observation["dimension_id"])

    delegate_policy = policy["delegate"]
    effective_reservation = {}
    reservation_adjustments = []
    for resource in RESOURCE_FIELDS:
        requested = reservation["resources"][resource]
        root_limit = root["limits"][resource]
        if requested > root_limit:
            _refuse(
                "over_budget",
                f"$.request.reservation.resources.{resource}",
                f"requested {requested} exceeds immutable root limit {root_limit}",
            )
        policy_cap = delegate_policy["reservation_caps"][resource]
        effective = min(requested, policy_cap)
        effective_reservation[resource] = effective
        if effective != requested:
            reservation_adjustments.append(
                {
                    "field": resource,
                    "from": requested,
                    "to": effective,
                    "reason": "explicit_policy_reservation_cap",
                }
            )
    requested_cadence = reservation["checkpoint_every_ms"]
    clamped_cadence = min(
        max(requested_cadence, delegate_policy["checkpoint_min_ms"]),
        delegate_policy["checkpoint_max_ms"],
    )
    if clamped_cadence != requested_cadence:
        reservation_adjustments.append(
            {
                "field": "checkpoint_every_ms",
                "from": requested_cadence,
                "to": clamped_cadence,
                "reason": "explicit_policy_checkpoint_range",
            }
        )

    subjects = []
    for observation in sorted(
        observations,
        key=lambda item: (item["dimension_id"], item["subject_kind"], item["subject_id"], item["head"]),
    ):
        gate_failures = [
            gate for gate in delegate_policy["required_gates"] if not observation["gates"][gate]
        ]
        subject = {
            "observation": observation,
            "gate_failures": gate_failures,
            "scored": False,
            "fitness_bps": None,
            "score_vector": None,
            "score_eligible": False,
        }
        if not gate_failures:
            score, vector = _score(observation["metrics_bps"], delegate_policy["weights_bps"])
            subject["scored"] = True
            subject["fitness_bps"] = score
            subject["score_vector"] = vector
            subject["score_eligible"] = score >= delegate_policy["minimum_fitness_bps"]
        subjects.append(subject)

    eligible_for_share = [subject for subject in subjects if subject["score_eligible"]]
    shares = {
        resource: _proportional_shares(
            effective_reservation[resource],
            eligible_for_share,
            resource,
        )
        for resource in RESOURCE_FIELDS
    }

    assignments = []
    used = _zero_resources()
    for subject in subjects:
        observation = subject["observation"]
        assignment = {
            "subject_kind": observation["subject_kind"],
            "subject_id": observation["subject_id"],
            "dimension_id": observation["dimension_id"],
            "observation_head": observation["head"],
            "receipt_head": observation["receipt"]["head"],
            "hard_gates": {
                "passed": not subject["gate_failures"],
                "failures": list(subject["gate_failures"]),
            },
            "scored": subject["scored"],
            "score_vector": subject["score_vector"],
            "fitness_bps": subject["fitness_bps"],
            "eligible": False,
            "disposition": "stop",
            "reason": "",
            "slice": _zero_resources(),
            "timebox_ms": 0,
            "checkpoint_every_ms": 0,
            "bounds": {},
            "adjustments": [],
        }
        if subject["gate_failures"]:
            assignment["reason"] = "hard gates failed; scoring and assignment were not performed"
            assignments.append(assignment)
            continue
        if not subject["score_eligible"]:
            assignment["reason"] = "fitness is below the explicit policy minimum"
            assignments.append(assignment)
            continue

        bounded_slice = {}
        for resource in RESOURCE_FIELDS:
            proportional = shares[resource][observation["head"]]
            remaining = observation["remaining"][resource]
            per_subject_cap = delegate_policy["per_subject_caps"][resource]
            bounded = min(proportional, remaining, per_subject_cap)
            binding_caps = []
            if bounded < proportional:
                if remaining == bounded:
                    binding_caps.append("subject_remaining")
                if per_subject_cap == bounded:
                    binding_caps.append("policy_per_subject_cap")
            bounded_slice[resource] = bounded
            assignment["bounds"][resource] = {
                "immutable_root_limit": root["limits"][resource],
                "current_reservation_total": effective_reservation[resource],
                "proportional_share": proportional,
                "subject_remaining": remaining,
                "policy_per_subject_cap": per_subject_cap,
                "bounded_before_minimum": bounded,
                "effective": bounded,
                "binding_caps": binding_caps,
            }
            if bounded != proportional:
                assignment["adjustments"].append(
                    {
                        "field": resource,
                        "from": proportional,
                        "to": bounded,
                        "reason": "+".join(binding_caps),
                    }
                )

        below_minimum = [
            resource
            for resource in RESOURCE_FIELDS
            if bounded_slice[resource] < delegate_policy["minimum_slice"][resource]
        ]
        if below_minimum:
            assignment["reason"] = (
                "bounded slice is below explicit minimums: " + ", ".join(below_minimum)
            )
            assignment["adjustments"].append(
                {
                    "field": "slice",
                    "from": dict(bounded_slice),
                    "to": _zero_resources(),
                    "reason": "minimum_slice_not_met",
                }
            )
            for resource in RESOURCE_FIELDS:
                assignment["bounds"][resource]["effective"] = 0
            assignments.append(assignment)
            continue

        duration = bounded_slice["duration_ms"]
        checkpoint_budget = bounded_slice["checkpoints"]
        cadence = 0
        checkpoint_infeasible = duration > 0 and checkpoint_budget == 0
        if duration > 0 and checkpoint_budget > 0:
            cadence = min(clamped_cadence, duration)
            if cadence != clamped_cadence:
                assignment["adjustments"].append(
                    {
                        "field": "checkpoint_every_ms",
                        "from": clamped_cadence,
                        "to": cadence,
                        "reason": "timebox_ends_before_next_checkpoint",
                    }
                )
            minimum_cadence_for_budget = (duration + checkpoint_budget - 1) // checkpoint_budget
            if cadence < minimum_cadence_for_budget:
                assignment["adjustments"].append(
                    {
                        "field": "checkpoint_every_ms",
                        "from": cadence,
                        "to": minimum_cadence_for_budget,
                        "reason": "checkpoint_count_budget",
                    }
                )
                cadence = minimum_cadence_for_budget
            if cadence > delegate_policy["checkpoint_max_ms"]:
                checkpoint_infeasible = True
        if checkpoint_infeasible:
            assignment["reason"] = "timebox and checkpoint limits cannot be satisfied together"
            assignment["adjustments"].append(
                {
                    "field": "slice",
                    "from": dict(bounded_slice),
                    "to": _zero_resources(),
                    "reason": "checkpoint_budget_infeasible",
                }
            )
            for resource in RESOURCE_FIELDS:
                assignment["bounds"][resource]["effective"] = 0
            assignments.append(assignment)
            continue

        assignment["eligible"] = True
        assignment["slice"] = bounded_slice
        assignment["timebox_ms"] = duration
        assignment["checkpoint_every_ms"] = cadence
        if subject["fitness_bps"] < delegate_policy["split_below_bps"]:
            assignment["disposition"] = "split"
            assignment["reason"] = "eligible but below the explicit continue threshold; split the task"
        else:
            assignment["disposition"] = "continue"
            assignment["reason"] = "hard gates, fitness, and bounded slice all pass"
        for resource in RESOURCE_FIELDS:
            used[resource] += bounded_slice[resource]
        assignments.append(assignment)

    unallocated = {
        resource: effective_reservation[resource] - used[resource] for resource in RESOURCE_FIELDS
    }
    viable = [assignment for assignment in assignments if assignment["eligible"]]
    result = _base_plan("delegate")
    result.update(
        {
            "schema": "autobest-delegate-candidate/1",
            "ok": bool(viable),
            "task": {"task_id": task["task_id"], "head": task["head"]},
            "bindings": {
                "root_envelope_head": root["head"],
                "reservation_head": reservation["head"],
                "policy_head": policy["head"],
                "observation_heads": sorted(item["head"] for item in observations),
            },
            "root_envelope": {
                "envelope_id": root["envelope_id"],
                "head": root["head"],
                "max_subjects": root["max_subjects"],
                "limits": dict(root["limits"]),
            },
            "current_reservation": {
                "reservation_id": reservation["reservation_id"],
                "head": reservation["head"],
                "predecessor_plan": reservation["predecessor_plan"],
                "requested_resources": dict(reservation["resources"]),
                "effective_resources": effective_reservation,
                "requested_checkpoint_every_ms": requested_cadence,
                "policy_clamped_checkpoint_every_ms": clamped_cadence,
                "adjustments": reservation_adjustments,
            },
            "assignments": assignments,
            "unallocated_resources": unallocated,
            "decision": {
                "mode": "assign" if viable else "refuse",
                "reasons": []
                if viable
                else ["no observation passed gates, score, minimum slice, and checkpoint limits"],
            },
            "successor_resize": {
                "same_root_envelope_required": True,
                "root_envelope_head": root["head"],
                "may_resize_current_reservation_within_root": True,
                "predecessor_plan_must_be_bound_when_present": True,
                "authority_widening_granted": False,
            },
            "lineage": _lineage(
                [task, root, reservation, policy]
                + observations
                + [observation["receipt"] for observation in observations]
            ),
        }
    )
    return _finalize_plan(result, "delegate-plan/v1")


def _candidate_audit(candidate, policy):
    required = policy["cross"]["required_gates"]
    failures = [gate for gate in required if not candidate["gates"][gate]]
    built_in = []
    if candidate["coverage_bps"] < policy["cross"]["minimum_coverage_bps"]:
        built_in.append("low_coverage")
    if not candidate["comparable"]:
        built_in.append("incomparable")
    if any(component["safety_critical"] for component in candidate["components"]):
        built_in.append("safety_critical")
    if any(component["conflicts"] for component in candidate["components"]):
        built_in.append("declared_conflicts")
    if any(component["unknowns"] for component in candidate["components"]):
        built_in.append("declared_unknowns")
    return {
        "candidate_id": candidate["candidate_id"],
        "candidate_head": candidate["head"],
        "parent_refs": list(candidate["provenance"]["parent_refs"]),
        "coverage_bps": candidate["coverage_bps"],
        "comparable": candidate["comparable"],
        "hard_gates": {
            "passed": not failures and not built_in,
            "failures": failures + built_in,
        },
        "metrics_bps": dict(candidate["metrics_bps"]),
        "scored": False,
        "score_vector": None,
        "score_bps": None,
        "eligible": False,
        "reason": "",
    }


def _component_audit_entry(candidate, component, action, reason):
    return {
        "candidate_id": candidate["candidate_id"],
        "candidate_head": candidate["head"],
        "component_id": component["component_id"],
        "content_head": component["content_head"],
        "coupling": component["coupling"],
        "group_id": component["group_id"],
        "compatibility_id": component["compatibility_id"],
        "substitutability_id": component["substitutability_id"],
        "safety_critical": component["safety_critical"],
        "depends_on": list(component["depends_on"]),
        "parent_refs": list(component["parent_refs"]),
        "conflicts": list(component["conflicts"]),
        "unknowns": list(component["unknowns"]),
        "action": action,
        "reason": reason,
    }


def _cross_lineage(task, policy, candidates):
    component_refs = []
    for candidate in candidates:
        for component in candidate["components"]:
            component_refs.extend(component["parent_refs"])
    return _lineage([task, policy] + candidates, component_refs)


def _cross_refusal(task, policy, candidates, audits, reasons, conflicts, unknowns, component_reason):
    component_audit = []
    for candidate in candidates:
        for component in candidate["components"]:
            component_audit.append(
                _component_audit_entry(candidate, component, "not_selected", component_reason)
            )
    result = _base_plan("cross")
    result.update(
        {
            "schema": "autobest-cross-candidate/1",
            "ok": False,
            "task": {"task_id": task["task_id"], "head": task["head"]},
            "bindings": {
                "policy_head": policy["head"],
                "candidate_heads": [candidate["head"] for candidate in candidates],
            },
            "candidate_audit": audits,
            "component_audit": component_audit,
            "decision": {"mode": "refuse", "reasons": reasons},
            "composite": None,
            "conflicts": conflicts,
            "unknowns": unknowns,
            "lineage": _cross_lineage(task, policy, candidates),
        }
    )
    return _finalize_plan(result, "cross-plan/v1")


def _bundle_signature(components):
    signature = []
    for component in components:
        if component["substitutability_id"] is None:
            return None
        signature.append((component["component_id"], component["substitutability_id"]))
    return sorted(signature)


def cross(request):
    """Apply the Crossing Lens to inert deliverable candidates."""

    _prepare_input(request, "$.request")
    fields = ("schema", "task", "policy", "candidates")
    _closed(request, "$.request", fields)
    if request["schema"] != "autobest-cross-request/1":
        _refuse("unsupported_schema", "$.request.schema", "expected autobest-cross-request/1")
    task = _validate_task(request["task"], "$.request.task")
    policy = _validate_policy(request["policy"], "$.request.policy")
    candidates = request["candidates"]
    if not isinstance(candidates, list) or not candidates:
        _refuse("list_required", "$.request.candidates", "at least one deliverable candidate is required")
    maximum = min(policy["cross"]["max_candidates"], MAX_CANDIDATES)
    if len(candidates) > maximum:
        _refuse("too_many_items", "$.request.candidates", f"candidate count exceeds policy cap {maximum}")
    seen_ids = set()
    for index, candidate in enumerate(candidates):
        _validate_candidate(candidate, f"$.request.candidates[{index}]", policy)
        if candidate["candidate_id"] in seen_ids:
            _refuse("duplicate_item", f"$.request.candidates[{index}].candidate_id", "duplicate candidate_id")
        seen_ids.add(candidate["candidate_id"])
    candidates = sorted(candidates, key=lambda item: (item["candidate_id"], item["head"]))
    audits = [_candidate_audit(candidate, policy) for candidate in candidates]
    audit_by_head = {audit["candidate_head"]: audit for audit in audits}

    reasons = []
    conflicts = []
    unknowns = []
    for candidate, audit in zip(candidates, audits):
        failures = audit["hard_gates"]["failures"]
        if "low_coverage" in failures:
            reasons.append(
                {
                    "code": "low_coverage",
                    "candidate_id": candidate["candidate_id"],
                    "detail": "coverage is below the explicit policy threshold",
                }
            )
        if "incomparable" in failures:
            reasons.append(
                {
                    "code": "incomparable",
                    "candidate_id": candidate["candidate_id"],
                    "detail": "candidate declares itself incomparable",
                }
            )
        if "safety_critical" in failures:
            reasons.append(
                {
                    "code": "safety_critical",
                    "candidate_id": candidate["candidate_id"],
                    "detail": "safety-critical deliverables require an external review path, not AutoBest",
                }
            )
        for component in candidate["components"]:
            if component["conflicts"]:
                item = {
                    "candidate_id": candidate["candidate_id"],
                    "component_id": component["component_id"],
                    "items": list(component["conflicts"]),
                }
                conflicts.append(item)
            if component["unknowns"]:
                item = {
                    "candidate_id": candidate["candidate_id"],
                    "component_id": component["component_id"],
                    "items": list(component["unknowns"]),
                }
                unknowns.append(item)
    if conflicts:
        reasons.append({"code": "unresolved_conflicts", "detail": "declared component conflicts remain"})
    if unknowns:
        reasons.append({"code": "unresolved_unknowns", "detail": "declared component unknowns remain"})

    ordinary_gate_pass = {
        candidate["head"]
        for candidate, audit in zip(candidates, audits)
        if not any(
            failure
            in (
                "low_coverage",
                "incomparable",
                "safety_critical",
                "declared_conflicts",
                "declared_unknowns",
            )
            for failure in audit["hard_gates"]["failures"]
        )
        and not [
            failure
            for failure in audit["hard_gates"]["failures"]
            if failure in policy["cross"]["required_gates"]
        ]
    }
    shared_groups = {}
    independent_groups = {}
    for candidate in candidates:
        if candidate["head"] not in ordinary_gate_pass:
            continue
        for component in candidate["components"]:
            if component["coupling"] == "shared":
                shared_groups.setdefault(component["group_id"], []).append((candidate, component))
            elif component["coupling"] == "independent":
                independent_groups.setdefault(component["group_id"], []).append((candidate, component))
    for group_id, instances in sorted(shared_groups.items()):
        signatures = {
            (component["component_id"], component["content_head"])
            for _, component in instances
        }
        if len(signatures) > 1:
            conflict = {
                "group_id": group_id,
                "kind": "shared_content_mismatch",
                "sources": sorted(candidate["candidate_id"] for candidate, _ in instances),
            }
            conflicts.append(conflict)
            reasons.append(
                {
                    "code": "shared_content_mismatch",
                    "group_id": group_id,
                    "detail": "a shared component may be reused only when its identity and content head match",
                }
            )
    for group_id, instances in sorted(independent_groups.items()):
        compatibility = {component["compatibility_id"] for _, component in instances}
        if len(compatibility) > 1:
            conflict = {
                "group_id": group_id,
                "kind": "independent_compatibility_mismatch",
                "compatibility_ids": sorted(compatibility),
            }
            conflicts.append(conflict)
            reasons.append(
                {
                    "code": "independent_compatibility_mismatch",
                    "group_id": group_id,
                    "detail": "independent components combine only under one explicit compatibility id",
                }
            )
    if reasons:
        for audit in audits:
            audit["reason"] = "a hard-gate or structural refusal occurred before scoring"
        return _cross_refusal(
            task,
            policy,
            candidates,
            audits,
            reasons,
            conflicts,
            unknowns,
            "hard-gate refusal occurred before scoring; no partial composite was selected",
        )

    cross_policy = policy["cross"]
    for candidate, audit in zip(candidates, audits):
        gate_failures = [
            gate for gate in cross_policy["required_gates"] if not candidate["gates"][gate]
        ]
        if gate_failures:
            audit["reason"] = "required hard gates failed; candidate was not scored"
            continue
        score, vector = _score(candidate["metrics_bps"], cross_policy["weights_bps"])
        audit["scored"] = True
        audit["score_vector"] = vector
        audit["score_bps"] = score
        audit["eligible"] = score >= cross_policy["minimum_score_bps"]
        audit["reason"] = (
            "eligible after hard gates and score threshold"
            if audit["eligible"]
            else "score is below the explicit policy threshold"
        )
    eligible = [
        candidate for candidate in candidates if audit_by_head[candidate["head"]]["eligible"]
    ]
    if not eligible:
        return _cross_refusal(
            task,
            policy,
            candidates,
            audits,
            [{"code": "no_eligible_candidate", "detail": "no candidate passed gates and score threshold"}],
            [],
            [],
            "candidate was ineligible; no component was selected",
        )

    eligible_independent = {}
    atomic_groups = {}
    for candidate in eligible:
        for component in candidate["components"]:
            if component["coupling"] == "independent":
                eligible_independent.setdefault(component["group_id"], []).append((candidate, component))
            elif component["coupling"] == "atomic":
                atomic_groups.setdefault(component["group_id"], {}).setdefault(candidate["head"], []).append(component)
    post_score_reasons = []
    for group_id, instances in sorted(eligible_independent.items()):
        distinct = {(component["component_id"], component["content_head"]) for _, component in instances}
        if len(distinct) > 1 and any(component["safety_critical"] for _, component in instances):
            post_score_reasons.append(
                {
                    "code": "safety_critical_combination",
                    "group_id": group_id,
                    "detail": "AutoBest will not combine competing safety-critical independent content",
                }
            )

    atomic_winners = {}
    for group_id, bundles in sorted(atomic_groups.items()):
        source_heads = sorted(bundles)
        if len(source_heads) > 1 and any(
            component["safety_critical"]
            for source_head in source_heads
            for component in bundles[source_head]
        ):
            post_score_reasons.append(
                {
                    "code": "safety_critical_competition",
                    "group_id": group_id,
                    "detail": "AutoBest refuses competing safety-critical atomic sources",
                }
            )
            continue
        best_score = max(audit_by_head[source_head]["score_bps"] for source_head in source_heads)
        tied = [
            source_head
            for source_head in source_heads
            if audit_by_head[source_head]["score_bps"] == best_score
        ]
        tie_method = "highest_score"
        if len(tied) > 1:
            signatures = [_bundle_signature(bundles[source_head]) for source_head in tied]
            substitutable = signatures[0] is not None and all(
                signature == signatures[0] for signature in signatures[1:]
            )
            if not cross_policy["allow_hash_tiebreak"] or not substitutable:
                post_score_reasons.append(
                    {
                        "code": "unresolved_atomic_tie",
                        "group_id": group_id,
                        "candidate_heads": tied,
                        "detail": "hash tie-break requires explicit semantic substitutability and non-safety-critical content",
                    }
                )
                continue
            tied = sorted(
                tied,
                key=lambda source_head: canonical_digest(
                    "cross-tie-break/v1",
                    {"group_id": group_id, "candidate_head": source_head},
                ),
            )
            tie_method = "semantic_substitute_hash"
        atomic_winners[group_id] = (tied[0], tie_method)

    if post_score_reasons:
        return _cross_refusal(
            task,
            policy,
            candidates,
            audits,
            post_score_reasons,
            post_score_reasons,
            [],
            "AutoBest refused a safety-critical or unresolved post-score choice; no partial composite was selected",
        )

    composite_components = []
    component_actions = {}
    eligible_shared = {}
    for candidate in eligible:
        for component in candidate["components"]:
            if component["coupling"] == "shared":
                eligible_shared.setdefault(component["group_id"], []).append((candidate, component))
    for group_id, instances in sorted(eligible_shared.items()):
        instances = sorted(instances, key=lambda item: (item[0]["head"], item[1]["component_id"]))
        primary_candidate, primary_component = instances[0]
        parent_refs = sorted(
            {
                parent
                for _, component in instances
                for parent in component["parent_refs"]
            }
        )
        composite_components.append(
            {
                "component_id": primary_component["component_id"],
                "content_head": primary_component["content_head"],
                "coupling": "shared",
                "group_id": group_id,
                "compatibility_id": None,
                "substitutability_id": None,
                "depends_on": [],
                "source_candidates": [candidate["candidate_id"] for candidate, _ in instances],
                "parent_refs": parent_refs,
                "selection_reason": "identical shared component reused once",
            }
        )
        for index, (candidate, component) in enumerate(instances):
            component_actions[(candidate["head"], component["component_id"])] = (
                "selected" if index == 0 else "reused",
                "identical shared content selected once" if index == 0 else "identical shared content already selected",
            )

    for group_id, instances in sorted(eligible_independent.items()):
        by_content = {}
        for candidate, component in instances:
            by_content.setdefault((component["component_id"], component["content_head"]), []).append(
                (candidate, component)
            )
        for _, duplicate_instances in sorted(by_content.items()):
            duplicate_instances = sorted(
                duplicate_instances, key=lambda item: (item[0]["head"], item[1]["component_id"])
            )
            primary_candidate, primary_component = duplicate_instances[0]
            parent_refs = sorted(
                {
                    parent
                    for _, component in duplicate_instances
                    for parent in component["parent_refs"]
                }
            )
            composite_components.append(
                {
                    "component_id": primary_component["component_id"],
                    "content_head": primary_component["content_head"],
                    "coupling": "independent",
                    "group_id": group_id,
                    "compatibility_id": primary_component["compatibility_id"],
                    "substitutability_id": primary_component["substitutability_id"],
                    "depends_on": [],
                    "source_candidates": [
                        candidate["candidate_id"] for candidate, _ in duplicate_instances
                    ],
                    "parent_refs": parent_refs,
                    "selection_reason": "explicitly compatible independent component combined",
                }
            )
            for index, (candidate, component) in enumerate(duplicate_instances):
                component_actions[(candidate["head"], component["component_id"])] = (
                    "combined" if index == 0 else "reused",
                    "explicit compatibility permits combination"
                    if index == 0
                    else "identical compatible content already combined",
                )

    candidate_by_head = {candidate["head"]: candidate for candidate in eligible}
    for group_id, (winner_head, tie_method) in sorted(atomic_winners.items()):
        winner = candidate_by_head[winner_head]
        winner_components = atomic_groups[group_id][winner_head]
        for component in sorted(winner_components, key=lambda item: item["component_id"]):
            composite_components.append(
                {
                    "component_id": component["component_id"],
                    "content_head": component["content_head"],
                    "coupling": "atomic",
                    "group_id": group_id,
                    "compatibility_id": None,
                    "substitutability_id": component["substitutability_id"],
                    "depends_on": list(component["depends_on"]),
                    "source_candidates": [winner["candidate_id"]],
                    "parent_refs": list(component["parent_refs"]),
                    "selection_reason": f"whole atomic source selected by {tie_method}",
                }
            )
            component_actions[(winner_head, component["component_id"])] = (
                "selected",
                f"whole atomic group selected from one source by {tie_method}",
            )
        for source_head, components in atomic_groups[group_id].items():
            if source_head == winner_head:
                continue
            for component in components:
                component_actions[(source_head, component["component_id"])] = (
                    "omitted",
                    f"atomic group selected whole from candidate {winner['candidate_id']}",
                )

    component_audit = []
    for candidate in candidates:
        audit = audit_by_head[candidate["head"]]
        for component in candidate["components"]:
            action = component_actions.get((candidate["head"], component["component_id"]))
            if action is None:
                reason = audit["reason"]
                action = ("omitted", reason)
            component_audit.append(
                _component_audit_entry(candidate, component, action[0], action[1])
            )
    composite_components.sort(
        key=lambda item: (
            {"shared": 0, "independent": 1, "atomic": 2}[item["coupling"]],
            item["group_id"],
            item["component_id"],
            item["content_head"],
        )
    )
    result = _base_plan("cross")
    result.update(
        {
            "schema": "autobest-cross-candidate/1",
            "ok": True,
            "task": {"task_id": task["task_id"], "head": task["head"]},
            "bindings": {
                "policy_head": policy["head"],
                "candidate_heads": [candidate["head"] for candidate in candidates],
            },
            "candidate_audit": audits,
            "component_audit": component_audit,
            "decision": {
                "mode": "autobest",
                "reasons": ["all hard gates passed before scoring and every selection is explicit"],
            },
            "composite": {
                "components": composite_components,
                "adoption_performed": False,
                "caller_must_verify_and_execute": True,
            },
            "conflicts": [],
            "unknowns": [],
            "lineage": _cross_lineage(task, policy, candidates),
        }
    )
    return _finalize_plan(result, "cross-plan/v1")


def run(request):
    """Compose delegate and optional cross without executing workers or adopting output."""

    _prepare_input(request, "$.request")
    _closed(request, "$.request", ("schema", "delegate", "cross"))
    if request["schema"] != "autobest-run-request/1":
        _refuse("unsupported_schema", "$.request.schema", "expected autobest-run-request/1")
    delegate_request = request["delegate"]
    cross_request = request["cross"]
    delegate_result = delegate(delegate_request)
    cross_result = None
    if cross_request is not None:
        if not isinstance(cross_request, dict):
            _refuse("object_required", "$.request.cross", "cross must be an object or explicit null")
        cross_result = cross(cross_request)
        if cross_result["task"]["head"] != delegate_result["task"]["head"]:
            _refuse("binding_mismatch", "$.request.cross.task.head", "run lenses must bind the same task head")
        if cross_result["bindings"]["policy_head"] != delegate_result["bindings"]["policy_head"]:
            _refuse("binding_mismatch", "$.request.cross.policy.head", "run lenses must bind the same policy head")
    result = _base_plan("run")
    result.update(
        {
            "schema": "autobest-run-candidate/1",
            "ok": delegate_result["ok"] and (cross_result is None or cross_result["ok"]),
            "task": dict(delegate_result["task"]),
            "delegate": delegate_result,
            "cross": cross_result,
            "composition": {
                "delegate_plan_head": delegate_result["plan_head"],
                "cross_plan_head": None if cross_result is None else cross_result["plan_head"],
                "worker_execution_performed": False,
                "adoption_performed": False,
            },
        }
    )
    return _finalize_plan(result, "run-plan/v1")


def double_hotload(request):
    """Record a Brainstem two-pass hotload rehearsal and optional locked result."""

    _prepare_input(request, "$.request")
    fields = (
        "schema",
        "cycle_id",
        "cycle_index",
        "source_frame_head",
        "source_profile_head",
        "target_profile_head",
        "caller_intent_head",
        "jit_scope",
        "learning_trace",
        "pass1",
        "pass2",
        "rehearsal",
        "gate_receipts",
    )
    _closed(request, "$.request", fields)
    if request["schema"] != "autobest-double-hotload-request/1":
        _refuse(
            "unsupported_schema",
            "$.request.schema",
            "expected autobest-double-hotload-request/1",
        )
    _identifier(request["cycle_id"], "$.request.cycle_id")
    _integer(request["cycle_index"], "$.request.cycle_index", 0, MAX_CEO_LINEAGE)
    for field in (
        "source_frame_head",
        "source_profile_head",
        "target_profile_head",
        "caller_intent_head",
    ):
        _sha256(request[field], f"$.request.{field}")
    jit_scope = _closed(
        request["jit_scope"],
        "$.request.jit_scope",
        (
            "trigger",
            "frame_heads",
            "policy_heads",
            "budget",
            "max_passes",
            "persist_native_history",
            "slot_contract",
        ),
    )
    if jit_scope["trigger"] not in (
        "unmatched-handshake",
        "typed-exhaust",
        "rehearsal",
        "mapping-mutation",
    ):
        _refuse("invalid_enum", "$.request.jit_scope.trigger", "unknown JIT wake trigger")
    _bounded_sha_list(
        jit_scope["frame_heads"],
        "$.request.jit_scope.frame_heads",
        MAX_REHEARSAL_FIXTURES,
        allow_empty=False,
    )
    _bounded_sha_list(
        jit_scope["policy_heads"],
        "$.request.jit_scope.policy_heads",
        MAX_REHEARSAL_FIXTURES,
        allow_empty=False,
    )
    _resource_vector(jit_scope["budget"], "$.request.jit_scope.budget")
    if jit_scope["max_passes"] != 2:
        _refuse("invalid_state", "$.request.jit_scope.max_passes", "double hotload requires two passes")
    if jit_scope["persist_native_history"] is not False:
        _refuse(
            "privacy_refusal",
            "$.request.jit_scope.persist_native_history",
            "native model sessions/history must not persist",
        )
    _validate_hotload_slot_contract(
        jit_scope["slot_contract"],
        "$.request.jit_scope.slot_contract",
    )
    learning_trace = _validate_learning_trace(
        request["learning_trace"],
        "$.request.learning_trace",
    )
    pass1 = _validate_hotload_pass(request["pass1"], "$.request.pass1", "pass1")
    pass2 = _validate_hotload_pass(request["pass2"], "$.request.pass2", "pass2")
    if pass1["input_head"] != request["source_frame_head"]:
        _refuse("binding_mismatch", "$.request.pass1.input_head", "pass1 must consume source Frame")
    if pass2["input_head"] != pass1["output_head"]:
        _refuse("binding_mismatch", "$.request.pass2.input_head", "pass2 must consume pass1 output")
    for pass_name, pass_value in (("pass1", pass1), ("pass2", pass2)):
        if pass_value["slot_id"] != jit_scope["slot_contract"]["slot_id"]:
            _refuse(
                "scope_violation",
                f"$.request.{pass_name}.slot_id",
                "hotload pass uses a slot outside the isolated contract",
            )
    if request["source_frame_head"] not in jit_scope["frame_heads"]:
        _refuse("scope_violation", "$.request.jit_scope.frame_heads", "JIT scope omits source Frame")
    if learning_trace["head"] not in jit_scope["frame_heads"]:
        _refuse("scope_violation", "$.request.jit_scope.frame_heads", "JIT scope omits learning trace")
    if not {pass1["policy_head"], pass2["policy_head"]}.issubset(
        set(jit_scope["policy_heads"])
    ):
        _refuse("scope_violation", "$.request.jit_scope.policy_heads", "JIT scope omits pass policy pins")
    combined_budget = {
        field: pass1["budget"][field] + pass2["budget"][field]
        for field in RESOURCE_FIELDS
    }
    if not _resource_leq(combined_budget, jit_scope["budget"]):
        _refuse("over_budget", "$.request.jit_scope.budget", "hotload passes exceed scoped budget")
    rehearsal = _closed(
        request["rehearsal"],
        "$.request.rehearsal",
        ("fixture_heads", "exhaust_heads", "previous_cycle_head", "lock_requested"),
    )
    fixture_heads = _bounded_sha_list(
        rehearsal["fixture_heads"],
        "$.request.rehearsal.fixture_heads",
        MAX_REHEARSAL_FIXTURES,
        allow_empty=False,
    )
    exhaust_heads = _bounded_sha_list(
        rehearsal["exhaust_heads"],
        "$.request.rehearsal.exhaust_heads",
        MAX_REHEARSAL_FIXTURES,
    )
    if rehearsal["previous_cycle_head"] is not None:
        _sha256(
            rehearsal["previous_cycle_head"],
            "$.request.rehearsal.previous_cycle_head",
        )
    lock_requested = _boolean(
        rehearsal["lock_requested"],
        "$.request.rehearsal.lock_requested",
    )
    if not set(exhaust_heads).issubset(set(jit_scope["frame_heads"])):
        _refuse("scope_violation", "$.request.jit_scope.frame_heads", "JIT scope omits exhaust evidence")
    if jit_scope["trigger"] in ("typed-exhaust", "mapping-mutation") and not exhaust_heads:
        _refuse(
            "invalid_state",
            "$.request.jit_scope.trigger",
            "post-lock mutation wake requires exhaust",
        )
    lock_proposal = {
        "cycle_id": request["cycle_id"],
        "cycle_index": request["cycle_index"],
        "source_frame_head": request["source_frame_head"],
        "source_profile_head": request["source_profile_head"],
        "target_profile_head": request["target_profile_head"],
        "caller_intent_head": request["caller_intent_head"],
        "jit_scope": _json_copy(jit_scope),
        "learning_trace_head": learning_trace["head"],
        "pass1_output_head": pass1["output_head"],
        "pass2_output_head": pass2["output_head"],
        "fixture_heads": list(fixture_heads),
        "exhaust_heads": list(exhaust_heads),
        "previous_cycle_head": rehearsal["previous_cycle_head"],
    }
    lock_proposal_head = canonical_digest(
        "double-hotload-lock-proposal/v1",
        lock_proposal,
    )
    gate_audit = []
    receipt_records = []
    required_gates = ("schema", "invariant", "privacy", "authority", "replay", "mutation")
    gate_receipts = request["gate_receipts"]
    if lock_requested:
        if not isinstance(gate_receipts, list) or len(gate_receipts) != len(required_gates):
            _refuse(
                "list_required",
                "$.request.gate_receipts",
                "locked rehearsal requires exactly six gate receipts",
            )
        seen = set()
        for index, gate_record in enumerate(gate_receipts):
            gate_path = f"$.request.gate_receipts[{index}]"
            _closed(gate_record, gate_path, ("gate", "passed", "receipt"))
            gate = gate_record["gate"]
            if gate not in required_gates or gate in seen:
                _refuse("invalid_gate", f"{gate_path}.gate", "unknown or duplicate lock gate")
            passed = _boolean(gate_record["passed"], f"{gate_path}.passed")
            gate_receipt = _validate_receipt(gate_record["receipt"], f"{gate_path}.receipt")
            gate_facts_head = canonical_digest(
                "double-hotload-lock-gate/v1",
                {
                    "gate": gate,
                    "passed": passed,
                    "lock_proposal_head": lock_proposal_head,
                },
            )
            if gate_receipt["facts_head"] != gate_facts_head:
                _refuse(
                    "receipt_binding_mismatch",
                    f"{gate_path}.receipt.facts_head",
                    "lock gate receipt does not bind exact double-hotload proposal",
                )
            seen.add(gate)
            receipt_records.append(gate_receipt)
            gate_audit.append(
                {
                    "gate": gate,
                    "passed": passed,
                    "receipt_head": gate_receipt["head"],
                }
            )
        failed = sorted(item["gate"] for item in gate_audit if not item["passed"])
        if failed:
            _refuse(
                "hotload_lock_gate_failed",
                "$.request.gate_receipts",
                "double-hotload lock refused by gates: " + ", ".join(failed),
            )
    else:
        if gate_receipts != []:
            _refuse(
                "unexpected_field",
                "$.request.gate_receipts",
                "unlocked rehearsal cycle must not claim lock gate receipts",
            )
    parent_refs = [
        request["source_frame_head"],
        learning_trace["head"],
        pass1["output_receipt"]["head"],
        pass2["output_receipt"]["head"],
    ]
    if rehearsal["previous_cycle_head"] is not None:
        parent_refs.append(rehearsal["previous_cycle_head"])
    result_record = head_record(
        "double_hotload_result",
        {
            "schema": "autobest-double-hotload-result/1",
            "cycle_id": request["cycle_id"],
            "cycle_index": request["cycle_index"],
            "source_frame_head": request["source_frame_head"],
            "source_profile_head": request["source_profile_head"],
            "target_profile_head": request["target_profile_head"],
            "caller_intent_head": request["caller_intent_head"],
            "jit_scope": _json_copy(jit_scope),
            "learning_trace": _json_copy(learning_trace),
            "pass1": _json_copy(pass1),
            "pass2": _json_copy(pass2),
            "rehearsal": {
                "fixture_heads": list(fixture_heads),
                "exhaust_heads": list(exhaust_heads),
                "previous_cycle_head": rehearsal["previous_cycle_head"],
                "lock_requested": lock_requested,
                "repeat_required": not lock_requested,
            },
            "gate_audit": sorted(gate_audit, key=lambda item: item["gate"]),
            "locked": lock_requested,
            "provenance": {
                "source_id": request["cycle_id"],
                "source_head": pass2["output_receipt"]["head"],
                "parent_refs": parent_refs,
            },
        },
    )
    _validate_double_hotload_result(result_record, "$.generated_hotload_result")
    result = _base_plan("double_hotload")
    result.update(
        {
            "schema": "autobest-double-hotload-candidate/1",
            "ok": True,
            "hotload_result": result_record,
            "pass1": {
                "role": "source-caller-selected-semantic-mutation",
                "agent_sha256": pass1["agent_sha256"],
                "agent_bytes": pass1["agent_bytes"],
                "agent_content_address": pass1["agent_content_address"],
                "placement_receipt_head": pass1["placement_receipt"]["head"],
                "input_head": pass1["input_head"],
                "output_head": pass1["output_head"],
                "transformation_receipt_head": pass1["output_receipt"]["head"],
                "unload_receipt_head": pass1["unload_receipt"]["head"],
            },
            "pass2": {
                "role": "target-finalizer-contract-mutation",
                "agent_sha256": pass2["agent_sha256"],
                "agent_bytes": pass2["agent_bytes"],
                "agent_content_address": pass2["agent_content_address"],
                "placement_receipt_head": pass2["placement_receipt"]["head"],
                "input_head": pass2["input_head"],
                "output_head": pass2["output_head"],
                "transformation_receipt_head": pass2["output_receipt"]["head"],
                "unload_receipt_head": pass2["unload_receipt"]["head"],
            },
            "runtime_topology": {
                "parent": "global-brainstem",
                "routing_plane": "verified-regular-file-hotload-slot",
                "trigger": jit_scope["trigger"],
                "ephemeral": True,
                "max_passes": 2,
                "model_calls_this_cycle": 2,
                "unloaded": True,
                "native_model_history_persisted": False,
                "scoped_frame_heads": list(jit_scope["frame_heads"]),
                "scoped_policy_heads": list(jit_scope["policy_heads"]),
                "scoped_budget": dict(jit_scope["budget"]),
                "slot_contract": _json_copy(jit_scope["slot_contract"]),
                "daemon_used": False,
                "plugin_registry_used": False,
                "permanent_process_used": False,
                "symlink_used": False,
                "overwrite_used": False,
                "brainstem_py_modified": False,
            },
            "locked": lock_requested,
            "repeat_required": not lock_requested,
            "next_action": "compile-static-transducer"
            if lock_requested
            else "repeat-double-hotload-rehearsal",
            "source_frame_mutated": False,
            "operation_universal": True,
            "allowed_successor_shapes": "any-framed-code-data-tree-required-by-caller-intent",
            "canonical_rapp1_envelope_constructed_by_lens": False,
            "host_constructs_and_signs_successor_frames": True,
            "host_signs_successor_frames": True,
            "continuous_ai_translation": False,
            "learning_trace": {
                "trace_head": learning_trace["head"],
                "event_chain_head": learning_trace["event_chain_head"],
                "summary": _json_copy(learning_trace["summary"]),
                "correction_fixtures": _trace_correction_fixtures(learning_trace),
                "raw_transcript_persisted": False,
                "hidden_reasoning_persisted": False,
                "local_paths_persisted": False,
                "token_data_persisted": False,
                "private_payloads_persisted": False,
            },
            "lineage": _lineage(
                [
                    pass1["agent_receipt"],
                    pass1["placement_receipt"],
                    pass1["prompt_receipt"],
                    pass1["policy_receipt"],
                    pass1["output_receipt"],
                    pass1["unload_receipt"],
                    pass2["agent_receipt"],
                    pass2["placement_receipt"],
                    pass2["prompt_receipt"],
                    pass2["policy_receipt"],
                    pass2["output_receipt"],
                    pass2["unload_receipt"],
                    *receipt_records,
                ]
            ),
        }
    )
    return _finalize_plan(result, "double-hotload-plan/v1")


def compatibility(request):
    """Emit one inert compatibility application Frame candidate for RAPP/1 endpoints."""

    _prepare_input(request, "$.request")
    _closed(
        request,
        "$.request",
        ("schema", "source", "target", "lens", "hotload_result"),
    )
    if request["schema"] != "autobest-compatibility-request/1":
        _refuse(
            "unsupported_schema",
            "$.request.schema",
            "expected autobest-compatibility-request/1",
        )
    source = _validate_rapp1_endpoint(request["source"], "$.request.source")
    target = _validate_rapp1_endpoint(request["target"], "$.request.target")
    lens = _validate_compatibility_lens(request["lens"], "$.request.lens")
    hotload_result = _validate_double_hotload_result(
        request["hotload_result"],
        "$.request.hotload_result",
    )
    if not hotload_result["locked"]:
        _refuse(
            "hotload_not_locked",
            "$.request.hotload_result",
            "static compatibility Frame requires a locked double-hotload result",
        )
    if (
        source["profile_head"] != hotload_result["source_profile_head"]
        or target["profile_head"] != hotload_result["target_profile_head"]
    ):
        _refuse(
            "binding_mismatch",
            "$.request",
            "endpoint profile pins do not match the locked double-hotload result",
        )
    if lens["hotload_lock_head"] != hotload_result["head"]:
        _refuse(
            "binding_mismatch",
            "$.request.lens.hotload_lock_head",
            "static transducer does not bind the supplied double-hotload lock",
        )
    if hotload_result["head"] not in lens["provenance"]["parent_refs"]:
        _refuse(
            "missing_provenance",
            "$.request.lens.provenance.parent_refs",
            "static transducer must retain its double-hotload lock",
        )
    source_capabilities = {
        capability["capability_id"]: capability
        for capability in source["capabilities"]
    }
    source_operations = {
        operation["operation_id"]: operation
        for operation in source["operations"]
    }
    target_operations = {
        operation["operation_id"]: operation
        for operation in target["operations"]
    }
    source_capability_ids = set(source_capabilities)
    mapped_target_operations = set()
    mapping_records = []
    aggregate_numerator = 0
    all_restrictions = set()
    overall_bounds = None
    exact_gaps = []
    for mapping in sorted(lens["mappings"], key=lambda item: item["mapping_id"]):
        source_capability = source_capabilities.get(mapping["source_capability_id"])
        if source_capability is None:
            _refuse(
                "binding_mismatch",
                "$.request.lens.mappings",
                f"Lens names unknown source capability {mapping['source_capability_id']!r}",
            )
        target_operation = target_operations.get(mapping["target_operation_id"])
        if target_operation is None:
            _refuse(
                "binding_mismatch",
                "$.request.lens.mappings",
                f"Lens names unknown target operation {mapping['target_operation_id']!r}",
            )
        source_operation = source_operations.get(mapping["source_operation_id"])
        if (
            source_operation is None
            or source_operation["operation_id"] not in source_capability["operations"]
        ):
            _refuse(
                "binding_mismatch",
                "$.request.lens.mappings",
                f"Lens source operation {mapping['source_operation_id']!r} is not provided by capability {source_capability['capability_id']!r}",
            )
        expected_transducer_schemas = {
            "source_input_schema_head": source_operation["input_schema_head"],
            "source_output_schema_head": source_operation["output_schema_head"],
            "target_input_schema_head": target_operation["input_schema_head"],
            "target_output_schema_head": target_operation["output_schema_head"],
        }
        for field, expected_head in expected_transducer_schemas.items():
            if mapping["transducer"][field] != expected_head:
                _refuse(
                    "binding_mismatch",
                    f"$.request.lens.mappings.{mapping['mapping_id']}.transducer.{field}",
                    "static transducer schema pin does not match endpoint operation",
                )
        for ceiling_name, ceiling in (
            ("source capability", source_capability["bounds"]),
            ("target operation", target_operation["bounds"]),
        ):
            excess = _resource_excess(mapping["bounds"], ceiling)
            if excess:
                _refuse(
                    "over_budget",
                    "$.request.lens.mappings",
                    f"mapping {mapping['mapping_id']} exceeds {ceiling_name} bounds: {', '.join(excess)}",
                )
        structural_gaps = [
            "required-capability:" + capability_id
            for capability_id in target_operation["required_capabilities"]
            if capability_id not in source_capability_ids
        ]
        restrictions = sorted(
            set(source_capability["restrictions"])
            | set(target_operation["restrictions"])
            | set(mapping["restrictions"])
        )
        gaps = sorted(set(mapping["gaps"]) | set(structural_gaps))
        mapping_record = {
            "mapping_id": mapping["mapping_id"],
            "source_capability_id": source_capability["capability_id"],
            "source_operation_id": source_operation["operation_id"],
            "source_operations": list(source_capability["operations"]),
            "target_operation_id": target_operation["operation_id"],
            "transducer": _json_copy(mapping["transducer"]),
            "target_operation_required": target_operation["required"],
            "weight_bps": mapping["weight_bps"],
            "coverage_bps": mapping["coverage_bps"],
            "declared_gaps": list(mapping["gaps"]),
            "structural_gaps": structural_gaps,
            "gaps": gaps,
            "restrictions": restrictions,
            "bounds": dict(mapping["bounds"]),
        }
        mapping_records.append(mapping_record)
        mapped_target_operations.add(target_operation["operation_id"])
        aggregate_numerator += mapping["coverage_bps"] * mapping["weight_bps"]
        all_restrictions.update(restrictions)
        exact_gaps.extend(
            {
                "mapping_id": mapping["mapping_id"],
                "target_operation_id": target_operation["operation_id"],
                "gap": gap,
            }
            for gap in gaps
        )
        overall_bounds = (
            dict(mapping["bounds"])
            if overall_bounds is None
            else _resource_minimum(overall_bounds, mapping["bounds"])
        )
    unmapped_operations = []
    for operation in sorted(target["operations"], key=lambda item: item["operation_id"]):
        if operation["operation_id"] not in mapped_target_operations:
            gap = {
                "target_operation_id": operation["operation_id"],
                "required": operation["required"],
                "reason": "target operation has no Lens mapping",
            }
            unmapped_operations.append(gap)
            exact_gaps.append(
                {
                    "mapping_id": None,
                    "target_operation_id": operation["operation_id"],
                    "gap": "unmapped-target-operation",
                }
            )
    aggregate_coverage = aggregate_numerator // 10_000
    required_unmapped = [
        item["target_operation_id"] for item in unmapped_operations if item["required"]
    ]
    has_mapping_gaps = any(record["gaps"] for record in mapping_records)
    coverage_passed = aggregate_coverage >= lens["minimum_coverage_bps"]
    partial_allowed = lens["allow_partial"]
    local_candidate_eligible = (
        coverage_passed
        and not required_unmapped
        and (partial_allowed or not has_mapping_gaps)
    )
    frame_body = {
        "schema": "rapp-application-frame-candidate/1",
        "application": "compatibility",
        "protocol": "RAPP/1",
        "source": {
            "endpoint_head": source["head"],
            "endpoint_id": source["endpoint_id"],
            "profile_id": source["profile_id"],
            "profile_head": source["profile_head"],
            "capabilities": _json_copy(source["capabilities"]),
        },
        "target": {
            "endpoint_head": target["head"],
            "endpoint_id": target["endpoint_id"],
            "profile_id": target["profile_id"],
            "profile_head": target["profile_head"],
            "operations": _json_copy(target["operations"]),
        },
        "lens": {
            "lens_head": lens["head"],
            "lens_id": lens["lens_id"],
            "version": lens["version"],
            "artifact_role": lens["artifact_role"],
            "hotload_lock_head": lens["hotload_lock_head"],
            "portable_artifact": _json_copy(lens["portable_artifact"]),
            "allow_partial": lens["allow_partial"],
            "minimum_coverage_bps": lens["minimum_coverage_bps"],
        },
        "mappings": mapping_records,
        "coverage": {
            "aggregate_bps": aggregate_coverage,
            "minimum_bps": lens["minimum_coverage_bps"],
            "passed": coverage_passed,
        },
        "gaps": {
            "exact": exact_gaps,
            "unmapped_target_operations": unmapped_operations,
            "required_unmapped_operations": required_unmapped,
        },
        "restrictions": sorted(all_restrictions),
        "bounds": overall_bounds or _zero_resources(),
        "generic_consumers": ["socket", "agent"],
        "frame_count": 1,
        "bespoke_runtime_required": False,
        "active_lens": "brainstem-double-hotload",
        "runtime_mode": "locked-deterministic-agent-hotload",
        "runtime_model_calls": 0,
        "jit_wake_triggers": [
            "typed-exhaust",
        ],
        "native_model_history_persisted": False,
        "learning_evidence": {
            "hotload_result_head": hotload_result["head"],
            "trigger": hotload_result["jit_scope"]["trigger"],
            "fixture_heads": list(hotload_result["rehearsal"]["fixture_heads"]),
            "exhaust_heads": list(hotload_result["rehearsal"]["exhaust_heads"]),
            "transformation_receipt_heads": [
                hotload_result["pass1"]["output_receipt"]["head"],
                hotload_result["pass2"]["output_receipt"]["head"],
            ],
            "placement_receipt_heads": [
                hotload_result["pass1"]["placement_receipt"]["head"],
                hotload_result["pass2"]["placement_receipt"]["head"],
            ],
            "unload_receipt_heads": [
                hotload_result["pass1"]["unload_receipt"]["head"],
                hotload_result["pass2"]["unload_receipt"]["head"],
            ],
            "portable_agent_content_address": lens["portable_artifact"][
                "content_address"
            ],
            "portable_agent_metadata_head": lens["portable_artifact"][
                "metadata_head"
            ],
            "portable_agent_tests_head": lens["portable_artifact"]["tests_head"],
            "private_hive_receipt_head": lens["portable_artifact"][
                "private_hive_receipt"
            ]["head"],
            "learning_trace_head": hotload_result["learning_trace"]["head"],
            "event_chain_head": hotload_result["learning_trace"][
                "event_chain_head"
            ],
            "correction_fixture_head": hotload_result["learning_trace"][
                "summary"
            ]["correction_fixture_head"],
            "correction_fixtures": _trace_correction_fixtures(
                hotload_result["learning_trace"]
            ),
        },
        "continuous_ai_translation": False,
        "mapping_exhaust_required_for_mutation": True,
        "predecessor_frame_head": None,
        "exhaust_head": None,
        "mutation_index": 0,
        "activated": False,
        "adopted": False,
        "authority_granted": False,
        "later_mutation_requires_successor_frame": True,
    }
    frame = dict(frame_body)
    frame["head"] = canonical_digest("compatibility-application-frame/v1", frame_body)
    _validate_compatibility_frame(frame, "$.generated_frame")
    result = _base_plan("compatibility")
    result.update(
        {
            "schema": "autobest-compatibility-frame-candidate/1",
            "ok": True,
            "frame": frame,
            "local_validation": {
                "required": True,
                "candidate_eligible": local_candidate_eligible,
                "coverage_passed": coverage_passed,
                "partial_allowed": partial_allowed,
                "required_unmapped_operations": required_unmapped,
                "activation_performed": False,
                "adoption_performed": False,
                "authority_granted": False,
            },
            "lineage": _lineage([source, target, lens, hotload_result]),
        }
    )
    return _finalize_plan(result, "compatibility-plan/v1")


def compatibility_exhaust(request):
    """Create immutable typed exhaust evidence for a static compatibility transducer."""

    _prepare_input(request, "$.request")
    fields = (
        "schema",
        "predecessor_frame",
        "exhaust_id",
        "direction",
        "channel",
        "mapping_id",
        "data_head",
        "expected_schema_head",
        "actual_schema_head",
        "reason",
        "runtime_receipt",
    )
    _closed(request, "$.request", fields)
    if request["schema"] != "autobest-compatibility-exhaust-request/1":
        _refuse(
            "unsupported_schema",
            "$.request.schema",
            "expected autobest-compatibility-exhaust-request/1",
        )
    predecessor = _validate_compatibility_frame(
        request["predecessor_frame"],
        "$.request.predecessor_frame",
    )
    _identifier(request["exhaust_id"], "$.request.exhaust_id")
    if request["direction"] not in ("source-to-target", "target-to-source"):
        _refuse("invalid_enum", "$.request.direction", "unknown transducer direction")
    if request["channel"] not in ("input", "output"):
        _refuse("invalid_enum", "$.request.channel", "unknown transducer channel")
    _identifier(request["mapping_id"], "$.request.mapping_id")
    mapping = next(
        (
            item
            for item in predecessor["mappings"]
            if item["mapping_id"] == request["mapping_id"]
        ),
        None,
    )
    if mapping is None:
        _refuse(
            "binding_mismatch",
            "$.request.mapping_id",
            "exhaust names a mapping absent from the predecessor Frame",
        )
    data_head = _sha256(request["data_head"], "$.request.data_head")
    expected_schema_head = _sha256(
        request["expected_schema_head"],
        "$.request.expected_schema_head",
    )
    actual_schema_head = _sha256(
        request["actual_schema_head"],
        "$.request.actual_schema_head",
    )
    pinned_field = {
        ("source-to-target", "input"): "target_input_schema_head",
        ("source-to-target", "output"): "source_output_schema_head",
        ("target-to-source", "input"): "source_input_schema_head",
        ("target-to-source", "output"): "target_output_schema_head",
    }[(request["direction"], request["channel"])]
    pinned_expected = mapping["transducer"][pinned_field]
    if expected_schema_head != pinned_expected:
        _refuse(
            "binding_mismatch",
            "$.request.expected_schema_head",
            "exhaust expected schema does not match the pinned directional transducer",
        )
    if actual_schema_head == expected_schema_head:
        _refuse(
            "exhaust_not_proven",
            "$.request.actual_schema_head",
            "typed exhaust requires an actual schema outside the pinned mapping",
        )
    if request["reason"] not in ("typed-mapping-exhausted", "data-domain-exhausted"):
        _refuse("invalid_enum", "$.request.reason", "unknown compatibility exhaust reason")
    runtime_receipt = _validate_receipt(
        request["runtime_receipt"],
        "$.request.runtime_receipt",
    )
    facts = {
        "predecessor_frame_head": predecessor["head"],
        "direction": request["direction"],
        "channel": request["channel"],
        "mapping_id": request["mapping_id"],
        "data_head": data_head,
        "expected_schema_head": expected_schema_head,
        "actual_schema_head": actual_schema_head,
        "reason": request["reason"],
    }
    facts_head = canonical_digest("compatibility-exhaust-facts/v1", facts)
    if runtime_receipt["facts_head"] != facts_head:
        _refuse(
            "receipt_binding_mismatch",
            "$.request.runtime_receipt.facts_head",
            "runtime receipt does not bind exact typed exhaust facts",
        )
    exhaust = head_record(
        "compatibility_exhaust",
        {
            "schema": "autobest-compatibility-exhaust/1",
            "exhaust_id": request["exhaust_id"],
            "predecessor_frame_head": predecessor["head"],
            "direction": request["direction"],
            "channel": request["channel"],
            "mapping_id": request["mapping_id"],
            "data_head": data_head,
            "expected_schema_head": expected_schema_head,
            "actual_schema_head": actual_schema_head,
            "reason": request["reason"],
            "runtime_receipt": runtime_receipt,
            "provenance": {
                "source_id": request["exhaust_id"],
                "source_head": runtime_receipt["head"],
                "parent_refs": [predecessor["head"], runtime_receipt["head"]],
            },
        },
    )
    _validate_compatibility_exhaust(exhaust, "$.generated_exhaust")
    result = _base_plan("compatibility_exhaust")
    result.update(
        {
            "schema": "autobest-compatibility-exhaust-candidate/1",
            "ok": True,
            "exhaust": exhaust,
            "predecessor_frame_head": predecessor["head"],
            "immutable_evidence": True,
            "runtime_mapping_changed": False,
            "continuous_ai_translation_used": False,
            "static_runtime_model_calls": 0,
            "jit_wake_required": True,
            "jit_wake_trigger": "typed-exhaust",
            "lineage": {
                "predecessor_frame_head": predecessor["head"],
                "runtime_receipt_head": runtime_receipt["head"],
            },
        }
    )
    return _finalize_plan(result, "compatibility-exhaust-plan/v1")


def compatibility_successor(request):
    """Gate and atomically select one successor compatibility Frame candidate."""

    _prepare_input(request, "$.request")
    fields = (
        "schema",
        "predecessor_frame",
        "exhaust",
        "hotload_result",
        "source",
        "target",
        "lens",
        "proposal_receipt",
        "gate_receipts",
    )
    _closed(request, "$.request", fields)
    if request["schema"] != "autobest-compatibility-successor-request/1":
        _refuse(
            "unsupported_schema",
            "$.request.schema",
            "expected autobest-compatibility-successor-request/1",
        )
    predecessor = _validate_compatibility_frame(
        request["predecessor_frame"],
        "$.request.predecessor_frame",
    )
    exhaust = _validate_compatibility_exhaust(
        request["exhaust"],
        "$.request.exhaust",
    )
    if exhaust["predecessor_frame_head"] != predecessor["head"]:
        _refuse(
            "binding_mismatch",
            "$.request.exhaust.predecessor_frame_head",
            "exhaust does not bind the supplied predecessor Frame",
        )
    hotload_result = _validate_double_hotload_result(
        request["hotload_result"],
        "$.request.hotload_result",
    )
    if not hotload_result["locked"]:
        _refuse(
            "hotload_not_locked",
            "$.request.hotload_result",
            "successor compatibility Frame requires a locked double-hotload result",
        )
    if hotload_result["source_frame_head"] != predecessor["head"]:
        _refuse(
            "binding_mismatch",
            "$.request.hotload_result.source_frame_head",
            "double-hotload result does not bind the predecessor Frame",
        )
    source = _validate_rapp1_endpoint(request["source"], "$.request.source")
    target = _validate_rapp1_endpoint(request["target"], "$.request.target")
    lens = _validate_compatibility_lens(request["lens"], "$.request.lens")
    if (
        source["profile_head"] != hotload_result["source_profile_head"]
        or target["profile_head"] != hotload_result["target_profile_head"]
    ):
        _refuse(
            "binding_mismatch",
            "$.request",
            "new endpoint profile pins do not match the locked double-hotload result",
        )
    if lens["hotload_lock_head"] != hotload_result["head"]:
        _refuse(
            "binding_mismatch",
            "$.request.lens.hotload_lock_head",
            "compiled static transducer does not bind the locked double-hotload result",
        )
    if hotload_result["head"] not in lens["provenance"]["parent_refs"]:
        _refuse(
            "missing_provenance",
            "$.request.lens.provenance.parent_refs",
            "compiled static transducer must retain the hotload lock",
        )
    changed_pins = (
        source["head"] != predecessor["source"]["endpoint_head"]
        or target["head"] != predecessor["target"]["endpoint_head"]
        or lens["head"] != predecessor["lens"]["lens_head"]
    )
    if not changed_pins:
        _refuse(
            "no_successor_mutation",
            "$.request",
            "successor proposal must pin a changed source, target, or Lens",
        )
    proposal_facts = {
        "predecessor_frame_head": predecessor["head"],
        "exhaust_head": exhaust["head"],
        "hotload_result_head": hotload_result["head"],
        "source_head": source["head"],
        "target_head": target["head"],
        "lens_head": lens["head"],
    }
    proposal_facts_head = canonical_digest(
        "compatibility-successor-proposal/v1",
        proposal_facts,
    )
    proposal_receipt = _validate_receipt(
        request["proposal_receipt"],
        "$.request.proposal_receipt",
    )
    if proposal_receipt["facts_head"] != proposal_facts_head:
        _refuse(
            "receipt_binding_mismatch",
            "$.request.proposal_receipt.facts_head",
            "proposal receipt does not bind predecessor, exhaust, and new endpoint/Lens pins",
        )
    required_gates = (
        "schema",
        "invariant",
        "privacy",
        "authority",
        "replay",
        "mutation",
    )
    gate_receipts = request["gate_receipts"]
    if not isinstance(gate_receipts, list) or len(gate_receipts) != len(required_gates):
        _refuse(
            "list_required",
            "$.request.gate_receipts",
            "successor requires exactly six gate receipts",
        )
    gate_audit = []
    seen_gates = set()
    receipt_records = []
    for index, gate_record in enumerate(gate_receipts):
        gate_path = f"$.request.gate_receipts[{index}]"
        _closed(gate_record, gate_path, ("gate", "passed", "receipt"))
        gate = gate_record["gate"]
        if gate not in required_gates or gate in seen_gates:
            _refuse("invalid_gate", f"{gate_path}.gate", "unknown or duplicate successor gate")
        passed = _boolean(gate_record["passed"], f"{gate_path}.passed")
        gate_receipt = _validate_receipt(gate_record["receipt"], f"{gate_path}.receipt")
        gate_facts_head = canonical_digest(
            "compatibility-successor-gate/v1",
            {
                "gate": gate,
                "passed": passed,
                "proposal_facts_head": proposal_facts_head,
            },
        )
        if gate_receipt["facts_head"] != gate_facts_head:
            _refuse(
                "receipt_binding_mismatch",
                f"{gate_path}.receipt.facts_head",
                "gate receipt does not bind the exact proposal and gate result",
            )
        seen_gates.add(gate)
        receipt_records.append(gate_receipt)
        gate_audit.append(
            {
                "gate": gate,
                "passed": passed,
                "receipt_head": gate_receipt["head"],
            }
        )
    if set(seen_gates) != set(required_gates):
        _refuse("missing_gate", "$.request.gate_receipts", "successor gate set is incomplete")
    failed_gates = sorted(item["gate"] for item in gate_audit if not item["passed"])
    if failed_gates:
        _refuse(
            "successor_gate_failed",
            "$.request.gate_receipts",
            "successor refused by gates: " + ", ".join(failed_gates),
        )
    successor_result = compatibility(
        {
            "schema": "autobest-compatibility-request/1",
            "source": source,
            "target": target,
            "lens": lens,
            "hotload_result": hotload_result,
        }
    )
    successor_body = {
        key: _json_copy(value)
        for key, value in successor_result["frame"].items()
        if key != "head"
    }
    successor_body["predecessor_frame_head"] = predecessor["head"]
    successor_body["exhaust_head"] = exhaust["head"]
    successor_body["mutation_index"] = predecessor["mutation_index"] + 1
    successor = dict(successor_body)
    successor["head"] = canonical_digest(
        "compatibility-application-frame/v1",
        successor_body,
    )
    _validate_compatibility_frame(successor, "$.generated_successor_frame")
    result = _base_plan("compatibility_successor")
    result.update(
        {
            "schema": "autobest-compatibility-successor-candidate/1",
            "ok": True,
            "successor_frame": successor,
            "proposal_receipt_head": proposal_receipt["head"],
            "gate_audit": sorted(gate_audit, key=lambda item: item["gate"]),
            "selection": {
                "mode": "atomic-single-successor",
                "selected": True,
                "selection_performed": True,
                "adoption_performed": False,
                "activation_performed": False,
                "host_atomic_commit_required": True,
                "in_place_patch_performed": False,
            },
            "immutable_evidence": {
                "predecessor_frame_head": predecessor["head"],
                "exhaust_head": exhaust["head"],
                "hotload_result_head": hotload_result["head"],
                "rollback_frame_head": predecessor["head"],
                "learning_evidence_head": exhaust["head"],
            },
            "continuous_ai_translation_used": False,
            "lineage": _lineage(
                [
                    source,
                    target,
                    lens,
                    hotload_result,
                    exhaust,
                    exhaust["runtime_receipt"],
                    proposal_receipt,
                    *receipt_records,
                ]
            ),
        }
    )
    return _finalize_plan(result, "compatibility-successor-plan/v1")


def _apply_static_map_spec(spec, payload):
    if not isinstance(payload, dict):
        _refuse("object_required", "$.payload", "static transducer payload must be an object")
    result = dict(payload) if spec["preserve_unmapped"] else {}
    for item in spec["field_map"]:
        if item["source"] not in payload:
            if item["required"]:
                _refuse(
                    "required_field_missing",
                    f"$.payload.{item['source']}",
                    "required static mapping field is missing",
                )
            continue
        result[item["target"]] = _json_copy(payload[item["source"]])
        if spec["preserve_unmapped"] and item["target"] != item["source"]:
            result.pop(item["source"], None)
    for key, value in spec["constants"].items():
        result[key] = _json_copy(value)
    return result


def _static_transform_selection(mapping, direction, channel):
    table = {
        ("source-to-target", "input"): (
            "source_input_schema_head",
            "target_input_schema_head",
            "forward_input_spec",
        ),
        ("source-to-target", "output"): (
            "target_output_schema_head",
            "source_output_schema_head",
            "forward_output_spec",
        ),
        ("target-to-source", "input"): (
            "target_input_schema_head",
            "source_input_schema_head",
            "reverse_input_spec",
        ),
        ("target-to-source", "output"): (
            "source_output_schema_head",
            "target_output_schema_head",
            "reverse_output_spec",
        ),
    }
    selection = table.get((direction, channel))
    if selection is None:
        _refuse("invalid_enum", "$.request", "unknown direction/channel")
    input_field, output_field, spec_field = selection
    transducer = mapping["transducer"]
    return transducer[input_field], transducer[output_field], transducer[spec_field]


def _static_mutation_tests(frame):
    tests = []
    for mapping in sorted(frame["mappings"], key=lambda item: item["mapping_id"]):
        for direction, channel in (
            ("source-to-target", "input"),
            ("source-to-target", "output"),
            ("target-to-source", "input"),
            ("target-to-source", "output"),
        ):
            input_schema, output_schema, spec = _static_transform_selection(
                mapping,
                direction,
                channel,
            )
            payload = {
                item["source"]: f"fixture:{mapping['mapping_id']}:{item['source']}"
                for item in spec["field_map"]
                if item["required"]
            }
            tests.append(
                {
                    "test_id": (
                        f"{mapping['mapping_id']}:{direction}:{channel}"
                    ),
                    "mapping_id": mapping["mapping_id"],
                    "direction": direction,
                    "channel": channel,
                    "input_schema_head": input_schema,
                    "output_schema_head": output_schema,
                    "input_payload": payload,
                    "expected_payload": _apply_static_map_spec(spec, payload),
                    "accept_declared_gaps": bool(mapping["gaps"]),
                    "expectation": "success",
                    "expected_code": None,
                }
            )
    mapping_by_id = {
        mapping["mapping_id"]: mapping for mapping in frame["mappings"]
    }
    for fixture in frame["learning_evidence"]["correction_fixtures"]:
        mapping = mapping_by_id.get(fixture["mapping_id"])
        if mapping is None:
            _refuse(
                "binding_mismatch",
                "$.compatibility_frame.learning_evidence.correction_fixtures",
                f"correction fixture names unknown mapping {fixture['mapping_id']!r}",
            )
        input_schema, output_schema, spec = _static_transform_selection(
            mapping,
            fixture["direction"],
            fixture["channel"],
        )
        payload = {
            item["source"]: f"correction:{fixture['fixture_id']}:{item['source']}"
            for item in spec["field_map"]
            if item["required"]
        }
        if fixture["assertion"] == "bounded-transform":
            test = {
                "test_id": "correction:" + fixture["fixture_id"],
                "mapping_id": mapping["mapping_id"],
                "direction": fixture["direction"],
                "channel": fixture["channel"],
                "input_schema_head": input_schema,
                "output_schema_head": output_schema,
                "input_payload": payload,
                "expected_payload": _apply_static_map_spec(spec, payload),
                "accept_declared_gaps": bool(mapping["gaps"]),
                "expectation": "success",
                "expected_code": None,
            }
        elif fixture["assertion"] == "typed-schema-refusal":
            test = {
                "test_id": "correction:" + fixture["fixture_id"],
                "mapping_id": mapping["mapping_id"],
                "direction": fixture["direction"],
                "channel": fixture["channel"],
                "input_schema_head": fixture["schema_head"],
                "output_schema_head": output_schema,
                "input_payload": payload,
                "expected_payload": None,
                "accept_declared_gaps": True,
                "expectation": "refusal",
                "expected_code": fixture["expected_code"],
            }
        else:
            test = {
                "test_id": "correction:" + fixture["fixture_id"],
                "mapping_id": mapping["mapping_id"],
                "direction": fixture["direction"],
                "channel": fixture["channel"],
                "input_schema_head": input_schema,
                "output_schema_head": output_schema,
                "input_payload": payload,
                "expected_payload": None,
                "accept_declared_gaps": False,
                "expectation": "refusal",
                "expected_code": fixture["expected_code"],
            }
        tests.append(test)
    return tests


def _render_static_agent_source(frame, compiler_sha256, runtime_head, version):
    frame_json = json.dumps(
        frame,
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
    )
    return f'''#!/usr/bin/env python3
"""Deterministic static compatibility agent compiled from one approved Frame."""

from __future__ import annotations

import json

COMPATIBILITY_FRAME = json.loads({frame_json!r})
COMPATIBILITY_FRAME_HEAD = {frame["head"]!r}
COMPILER_SHA256 = {compiler_sha256!r}
RUNTIME_HEAD = {runtime_head!r}
VERSION = {version!r}

__manifest__ = {{
    "schema": "rapp-agent/1.0",
    "name": "static_compatibility_{frame["head"][:16]}",
    "version": VERSION,
    "display_name": "Locked Static Compatibility Agent",
    "description": "Coverage-bounded deterministic compatibility transducer.",
    "dependencies": [],
    "requires_env": [],
    "single_file": True,
    "stdlib_only": True,
    "deterministic": True,
    "inert": True,
    "authority": False,
    "compatibility_frame_head": COMPATIBILITY_FRAME_HEAD,
    "compiler_sha256": COMPILER_SHA256,
    "runtime_head": RUNTIME_HEAD,
    "normal_traffic_model_calls": 0,
    "bidirectional": True,
    "universal_semantic_truth": False,
    "conceptual_prior_art_commit": {PRIOR_ART_PROVENANCE["commit"]!r},
    "conceptual_prior_art_only": True,
    "rapp1_conformance_claimed": False,
}}


class StaticCompatibilityRefusal(ValueError):
    def __init__(self, code, detail):
        super().__init__(code + ": " + detail)
        self.code = code
        self.detail = detail


def _refuse(code, detail):
    raise StaticCompatibilityRefusal(code, detail)


def _canonical_size(value):
    try:
        return len(json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("utf-8"))
    except (TypeError, ValueError) as error:
        _refuse("non_json_value", str(error))


def _mapping(mapping_id):
    for mapping in COMPATIBILITY_FRAME["mappings"]:
        if mapping["mapping_id"] == mapping_id:
            return mapping
    _refuse("unknown_mapping", mapping_id)


def _selection(mapping, direction, channel):
    table = {{
        ("source-to-target", "input"): (
            "source_input_schema_head",
            "target_input_schema_head",
            "forward_input_spec",
        ),
        ("source-to-target", "output"): (
            "target_output_schema_head",
            "source_output_schema_head",
            "forward_output_spec",
        ),
        ("target-to-source", "input"): (
            "target_input_schema_head",
            "source_input_schema_head",
            "reverse_input_spec",
        ),
        ("target-to-source", "output"): (
            "source_output_schema_head",
            "target_output_schema_head",
            "reverse_output_spec",
        ),
    }}
    selected = table.get((direction, channel))
    if selected is None:
        _refuse("invalid_direction_channel", direction + "/" + channel)
    input_field, output_field, spec_field = selected
    transducer = mapping["transducer"]
    return transducer[input_field], transducer[output_field], transducer[spec_field]


def _apply(spec, payload):
    if not isinstance(payload, dict):
        _refuse("object_required", "payload must be an object")
    result = dict(payload) if spec["preserve_unmapped"] else {{}}
    for item in spec["field_map"]:
        if item["source"] not in payload:
            if item["required"]:
                _refuse("required_field_missing", item["source"])
            continue
        result[item["target"]] = payload[item["source"]]
        if spec["preserve_unmapped"] and item["target"] != item["source"]:
            result.pop(item["source"], None)
    for key, value in spec["constants"].items():
        result[key] = value
    return result


def transform(request):
    if not isinstance(request, dict):
        _refuse("object_required", "request must be an object")
    expected = {{
        "mapping_id",
        "direction",
        "channel",
        "input_schema_head",
        "payload",
        "accept_declared_gaps",
    }}
    if set(request) != expected:
        _refuse("closed_request", "request fields differ from the static contract")
    mapping = _mapping(request["mapping_id"])
    input_schema, output_schema, spec = _selection(
        mapping,
        request["direction"],
        request["channel"],
    )
    if request["input_schema_head"] != input_schema:
        _refuse("typed_mapping_exhausted", "input schema is outside the locked mapping")
    if mapping["gaps"] and request["accept_declared_gaps"] is not True:
        _refuse("declared_gap_not_accepted", "caller must explicitly accept declared gaps")
    payload_size = _canonical_size(request["payload"])
    if payload_size > mapping["bounds"]["context_bytes"]:
        _refuse("input_bound_exceeded", "payload exceeds context_bytes bound")
    output = _apply(spec, request["payload"])
    if _canonical_size(output) > mapping["bounds"]["output_bytes"]:
        _refuse("output_bound_exceeded", "output exceeds output_bytes bound")
    return {{
        "schema": "static-compatibility-result/1",
        "ok": True,
        "compatibility_frame_head": COMPATIBILITY_FRAME_HEAD,
        "mapping_id": mapping["mapping_id"],
        "direction": request["direction"],
        "channel": request["channel"],
        "input_schema_head": input_schema,
        "output_schema_head": output_schema,
        "payload": output,
        "coverage_bps": mapping["coverage_bps"],
        "gaps": list(mapping["gaps"]),
        "restrictions": list(mapping["restrictions"]),
        "bounds": dict(mapping["bounds"]),
        "authority_granted": False,
        "model_calls": 0,
        "universal_semantic_truth": False,
    }}


try:
    from agents.basic_agent import BasicAgent
except ImportError:
    try:
        from basic_agent import BasicAgent
    except ImportError:
        class BasicAgent:
            def __init__(self, name=None, metadata=None):
                self.name = name or "BasicAgent"
                self.metadata = metadata or {{}}


class StaticCompatibilityAgent(BasicAgent):
    metadata = {{
        "name": "static_compatibility",
        "description": "Apply one locked compatibility Frame within declared coverage.",
        "parameters": {{
            "type": "object",
            "properties": {{
                "request": {{"type": "object"}},
            }},
            "required": ["request"],
            "additionalProperties": False,
        }},
    }}

    def __init__(self):
        self.name = "static_compatibility"
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs):
        try:
            if set(kwargs) != {{"request"}}:
                _refuse("closed_arguments", "expected only request")
            result = transform(kwargs["request"])
        except StaticCompatibilityRefusal as refusal:
            result = {{
                "schema": "static-compatibility-refusal/1",
                "ok": False,
                "compatibility_frame_head": COMPATIBILITY_FRAME_HEAD,
                "refusal": {{
                    "code": refusal.code,
                    "detail": refusal.detail,
                }},
                "authority_granted": False,
                "model_calls": 0,
            }}
        return json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


if __name__ == "__main__":
    print(json.dumps({{
        "manifest": __manifest__,
        "executed": False,
        "authority_granted": False,
    }}, sort_keys=True, separators=(",", ":")))
'''


def compile_static_agent(request):
    """Compile one approved compatibility Frame into deterministic static agent.py bytes."""

    _prepare_input(request, "$.request")
    fields = (
        "schema",
        "compatibility_frame",
        "compiler_sha256",
        "runtime_head",
        "private_hive_policy_head",
        "compile_mode",
        "captured_agent",
        "captured_mutation_tests",
        "captured_tests_receipt",
        "generation_receipt",
    )
    _closed(request, "$.request", fields)
    if request["schema"] != "autobest-static-agent-compile-request/1":
        _refuse(
            "unsupported_schema",
            "$.request.schema",
            "expected autobest-static-agent-compile-request/1",
        )
    frame = _validate_compatibility_frame(
        request["compatibility_frame"],
        "$.request.compatibility_frame",
    )
    compiler_sha = _sha256(request["compiler_sha256"], "$.request.compiler_sha256")
    runtime_head = _sha256(request["runtime_head"], "$.request.runtime_head")
    private_hive_policy_head = _sha256(
        request["private_hive_policy_head"],
        "$.request.private_hive_policy_head",
    )
    compile_mode = request["compile_mode"]
    if compile_mode not in ("deterministic-field-map", "captured-agent-bytes"):
        _refuse(
            "invalid_enum",
            "$.request.compile_mode",
            "expected deterministic-field-map or captured-agent-bytes",
        )
    if compile_mode == "deterministic-field-map":
        if (
            request["captured_agent"] is not None
            or request["captured_mutation_tests"] is not None
            or request["captured_tests_receipt"] is not None
        ):
            _refuse(
                "unexpected_field",
                "$.request",
                "deterministic field-map compilation cannot carry captured code inputs",
            )
        version = (
            "1.0.0+frame."
            + frame["head"][:12]
            + ".compiler."
            + compiler_sha[:8]
        )
        source = _render_static_agent_source(
            frame,
            compiler_sha,
            runtime_head,
            version,
        )
        source_bytes = source.encode("utf-8")
        mutation_tests = _static_mutation_tests(frame)
        tests_head = canonical_digest(
            "static-agent-mutation-tests/v1",
            mutation_tests,
        )
        captured_tests_receipt_head = None
    else:
        captured_agent = _closed(
            request["captured_agent"],
            "$.request.captured_agent",
            ("encoding", "chunks", "sha256", "bytes", "content_address"),
        )
        if captured_agent["encoding"] != "utf-8":
            _refuse(
                "invalid_enum",
                "$.request.captured_agent.encoding",
                "captured static agent must be UTF-8 Python source",
            )
        source_bytes = _snapshot_content_bytes(
            {
                "encoding": captured_agent["encoding"],
                "chunks": captured_agent["chunks"],
            },
            "$.request.captured_agent",
        )
        declared_sha = _sha256(
            captured_agent["sha256"],
            "$.request.captured_agent.sha256",
        )
        declared_bytes = _integer(
            captured_agent["bytes"],
            "$.request.captured_agent.bytes",
            1,
            MAX_AGENT_FILE_BYTES,
        )
        actual_sha = hashlib.sha256(source_bytes).hexdigest()
        if declared_bytes != len(source_bytes) or declared_sha != actual_sha:
            _refuse(
                "content_hash_mismatch",
                "$.request.captured_agent",
                "captured agent bytes do not match declared length/SHA",
            )
        _sha256_content_address(
            captured_agent["content_address"],
            actual_sha,
            "$.request.captured_agent.content_address",
        )
        artifact = frame["lens"]["portable_artifact"]
        if (
            artifact["agent_sha256"] != actual_sha
            or artifact["agent_bytes"] != len(source_bytes)
            or artifact["content_address"] != captured_agent["content_address"]
        ):
            _refuse(
                "binding_mismatch",
                "$.request.captured_agent",
                "captured bytes do not match the Compatibility Frame portable artifact",
            )
        try:
            source = source_bytes.decode("utf-8")
            compile(source, "<captured-static-agent>", "exec")
        except (UnicodeDecodeError, SyntaxError) as error:
            _refuse(
                "unqualified_generated_code",
                "$.request.captured_agent",
                str(error),
            )
        version = (
            "1.0.0+frame."
            + frame["head"][:12]
            + ".compiler."
            + compiler_sha[:8]
            + ".agent."
            + actual_sha[:8]
        )
        captured_tests = request["captured_mutation_tests"]
        if not isinstance(captured_tests, list) or not captured_tests:
            _refuse(
                "list_required",
                "$.request.captured_mutation_tests",
                "captured arbitrary code requires real passed mutation-test receipts",
            )
        mutation_tests = []
        seen_test_ids = set()
        for index, test in enumerate(captured_tests):
            test_path = f"$.request.captured_mutation_tests[{index}]"
            _closed(test, test_path, ("test_id", "test_head", "status", "receipt"))
            _identifier(test["test_id"], f"{test_path}.test_id")
            if test["test_id"] in seen_test_ids:
                _refuse("duplicate_item", f"{test_path}.test_id", "duplicate captured test")
            seen_test_ids.add(test["test_id"])
            _sha256(test["test_head"], f"{test_path}.test_head")
            if test["status"] != "passed":
                _refuse(
                    "unqualified_generated_code",
                    f"{test_path}.status",
                    "captured mutation test did not pass",
                )
            _validate_receipt(test["receipt"], f"{test_path}.receipt")
            expected_test_facts = canonical_digest(
                "captured-static-agent-test/v1",
                {
                    "test_id": test["test_id"],
                    "test_head": test["test_head"],
                    "status": test["status"],
                    "agent_sha256": actual_sha,
                },
            )
            if test["receipt"]["facts_head"] != expected_test_facts:
                _refuse(
                    "receipt_binding_mismatch",
                    f"{test_path}.receipt.facts_head",
                    "captured test receipt does not bind agent and Frame",
                )
            mutation_tests.append(_json_copy(test))
        tests_head = canonical_digest(
            "static-agent-mutation-tests/v1",
            mutation_tests,
        )
        if tests_head != artifact["tests_head"]:
            _refuse(
                "binding_mismatch",
                "$.request.captured_mutation_tests",
                "captured tests do not match the Frame portable artifact tests head",
            )
        captured_tests_receipt = _validate_receipt(
            request["captured_tests_receipt"],
            "$.request.captured_tests_receipt",
        )
        if captured_tests_receipt["facts_head"] != tests_head:
            _refuse(
                "receipt_binding_mismatch",
                "$.request.captured_tests_receipt.facts_head",
                "captured tests receipt does not bind exact test corpus",
            )
        captured_tests_receipt_head = captured_tests_receipt["head"]
        if request["generation_receipt"] is None:
            _refuse(
                "unqualified_generated_code",
                "$.request.generation_receipt",
                "captured arbitrary code requires an exact generation receipt",
            )
    if len(source_bytes) > MAX_AGENT_FILE_BYTES:
        _refuse(
            "oversize_content",
            "$.generated_agent",
            f"compiled static agent exceeds {MAX_AGENT_FILE_BYTES} bytes",
        )
    agent_sha = hashlib.sha256(source_bytes).hexdigest()
    metadata = {
        "schema": "autobest-static-agent-metadata/1",
        "version": version,
        "agent_sha256": agent_sha,
        "agent_bytes": len(source_bytes),
        "content_address": "sha256:" + agent_sha,
        "compatibility_frame_head": frame["head"],
        "compiler_sha256": compiler_sha,
        "runtime_head": runtime_head,
        "compile_mode": compile_mode,
        "private_hive_policy_head": private_hive_policy_head,
        "coverage": _json_copy(frame["coverage"]),
        "gaps": _json_copy(frame["gaps"]),
        "restrictions": list(frame["restrictions"]),
        "bounds": dict(frame["bounds"]),
        "normal_traffic_model_calls": 0,
        "bidirectional": True,
        "universal_within_declared_coverage": True,
        "universal_semantic_truth": False,
        "arbitrary_deterministic_code": compile_mode == "captured-agent-bytes",
        "mutation_tests_head": tests_head,
        "captured_tests_receipt_head": captured_tests_receipt_head,
        "conceptual_prior_art": {
            "repository": PRIOR_ART_PROVENANCE["repository"],
            "commit": PRIOR_ART_PROVENANCE["commit"],
            "role": PRIOR_ART_PROVENANCE["role"],
            "rapp1_conformance_claimed": False,
        },
    }
    metadata_head = canonical_digest("static-agent-metadata/v1", metadata)
    handshake_id = "handshake:" + canonical_digest(
        "private-hive-handshake-id/v1",
        {
            "compatibility_frame_head": frame["head"],
            "agent_sha256": agent_sha,
            "metadata_head": metadata_head,
            "tests_head": tests_head,
        },
    )[:32]
    generation_facts = {
        "compatibility_frame_head": frame["head"],
        "compiler_sha256": compiler_sha,
        "runtime_head": runtime_head,
        "compile_mode": compile_mode,
        "agent_sha256": agent_sha,
        "version": version,
        "metadata_head": metadata_head,
        "tests_head": tests_head,
    }
    generation_facts_head = canonical_digest(
        "static-agent-generation/v1",
        generation_facts,
    )
    generation_receipt = request["generation_receipt"]
    generation_receipt_head = None
    if generation_receipt is not None:
        _validate_receipt(
            generation_receipt,
            "$.request.generation_receipt",
        )
        if generation_receipt["facts_head"] != generation_facts_head:
            _refuse(
                "receipt_binding_mismatch",
                "$.request.generation_receipt.facts_head",
                "generation receipt does not bind deterministic static agent bytes",
            )
        generation_receipt_head = generation_receipt["head"]
    result = _base_plan("compile_static_agent")
    result.update(
        {
            "schema": "autobest-static-agent-package-candidate/1",
            "ok": True,
            "package": {
                "agent_filename": "agent.py",
                "agent_source": source,
                "agent_sha256": agent_sha,
                "agent_bytes": len(source_bytes),
                "content_address": "sha256:" + agent_sha,
                "version": version,
                "metadata": metadata,
                "metadata_head": metadata_head,
                "mutation_tests": mutation_tests,
                "mutation_tests_head": tests_head,
                "generation_facts_head": generation_facts_head,
                "generation_receipt_head": generation_receipt_head,
                "compile_mode": compile_mode,
                "captured_tests_receipt_head": captured_tests_receipt_head,
                "private_hive_ready": True,
                "private_hive_catalog_candidate": {
                    "schema": "private-hive-handshake-catalog-candidate/1",
                    "handshake_id": handshake_id,
                    "agent_content_address": "sha256:" + agent_sha,
                    "metadata_head": metadata_head,
                    "mutation_tests_head": tests_head,
                    "compatibility_frame_head": frame["head"],
                    "conceptual_prior_art_commit": PRIOR_ART_PROVENANCE["commit"],
                    "conceptual_prior_art_only": True,
                    "rapp1_conformance_claimed": False,
                    "signature_required": True,
                    "signed": False,
                    "registered": False,
                    "authority_granted": False,
                },
                "published": False,
                "activated": False,
                "authority_granted": False,
            },
            "reproducibility": {
                "deterministic_from": [
                    frame["head"],
                    compiler_sha,
                    runtime_head,
                    agent_sha
                    if compile_mode == "captured-agent-bytes"
                    else "field-map-template/v1",
                ],
                "exact_generation_receipt_verified": generation_receipt is not None,
                "changed_frame_changes_version_and_agent_hash": True,
                "static_field_map_ir_normative": False,
            },
            "coverage_boundary": {
                "coverage": _json_copy(frame["coverage"]),
                "gaps": _json_copy(frame["gaps"]),
                "restrictions": list(frame["restrictions"]),
                "universal_semantic_truth_claimed": False,
            },
            "lineage": {
                "compatibility_frame_head": frame["head"],
                "hotload_lock_head": frame["lens"]["hotload_lock_head"],
                "compiler_sha256": compiler_sha,
                "runtime_head": runtime_head,
                "generation_receipt_head": generation_receipt_head,
            },
        }
    )
    return _finalize_plan(result, "static-agent-package-plan/v1")


def self_host_repository(request):
    """Derive an inert causal successor repository from an immutable ancestor Frame."""

    _prepare_input(request, "$.request")
    fields = (
        "schema",
        "source_frame",
        "mutation_intent",
        "lineage_policy",
        "file_mutations",
        "selected_traits",
        "omitted_traits",
        "hotload_result",
        "compatibility_frame",
        "compiler_sha256",
        "runtime_head",
        "private_hive_policy_head",
        "generation_receipt",
        "protocol_projections",
        "unknown_unknown_gates",
    )
    _closed(request, "$.request", fields)
    if request["schema"] != "autobest-self-host-repository-request/1":
        _refuse(
            "unsupported_schema",
            "$.request.schema",
            "expected autobest-self-host-repository-request/1",
        )
    source = _validate_repository_frame(
        request["source_frame"],
        "$.request.source_frame",
    )
    if (
        source["repository"] != PRIOR_ART_PROVENANCE["repository"]
        or source["commit"] != PRIOR_ART_PROVENANCE["commit"]
    ):
        _refuse(
            "binding_mismatch",
            "$.request.source_frame",
            "self-hosting proof must bind the pinned UniversalDataConnectorAI commit",
        )
    inventory_by_path = {
        entry["path"]: entry for entry in source["inventory"]
    }
    for prior_file in PRIOR_ART_PROVENANCE["files"]:
        entry = inventory_by_path.get(prior_file["path"])
        if entry is None or entry["blob_sha1"] != prior_file["blob_sha"]:
            _refuse(
                "prior_art_inventory_mismatch",
                "$.request.source_frame.inventory",
                f"pinned prior-art blob missing or changed: {prior_file['path']}",
            )
    intent = _closed(
        request["mutation_intent"],
        "$.request.mutation_intent",
        (
            "intent_id",
            "mode",
            "preserve_ancestor",
            "target_protocol",
            "intent_head",
        ),
    )
    _identifier(intent["intent_id"], "$.request.mutation_intent.intent_id")
    if intent["mode"] != "derive-successor-repository":
        _refuse(
            "invalid_enum",
            "$.request.mutation_intent.mode",
            "expected derive-successor-repository",
        )
    if intent["preserve_ancestor"] is not True:
        _refuse(
            "source_mutation_forbidden",
            "$.request.mutation_intent.preserve_ancestor",
            "ancestor Frame occurrence must remain immutable and recoverable",
        )
    if intent["target_protocol"] != "RAPP/1":
        _refuse("protocol_mismatch", "$.request.mutation_intent.target_protocol", "target must fit RAPP/1")
    _sha256(intent["intent_head"], "$.request.mutation_intent.intent_head")
    expected_intent_head = canonical_digest(
        "self-host-mutation-intent/v1",
        {
            "intent_id": intent["intent_id"],
            "mode": intent["mode"],
            "preserve_ancestor": intent["preserve_ancestor"],
            "target_protocol": intent["target_protocol"],
        },
    )
    if intent["intent_head"] != expected_intent_head:
        _refuse("head_mismatch", "$.request.mutation_intent.intent_head", "mutation intent head mismatch")

    lineage_policy = _closed(
        request["lineage_policy"],
        "$.request.lineage_policy",
        ("mode", "round_trip_required"),
    )
    if lineage_policy["mode"] not in ("lossless", "lossy"):
        _refuse("invalid_enum", "$.request.lineage_policy.mode", "expected lossless or lossy")
    _boolean(
        lineage_policy["round_trip_required"],
        "$.request.lineage_policy.round_trip_required",
    )
    if (
        lineage_policy["mode"] == "lossless"
        and lineage_policy["round_trip_required"] is not True
    ):
        _refuse(
            "invalid_lineage_policy",
            "$.request.lineage_policy",
            "lossless mode requires round trip",
        )
    if (
        lineage_policy["mode"] == "lossy"
        and lineage_policy["round_trip_required"] is not False
    ):
        _refuse(
            "invalid_lineage_policy",
            "$.request.lineage_policy",
            "lossy mode cannot require round trip",
        )

    mutations = request["file_mutations"]
    if not isinstance(mutations, list) or not mutations:
        _refuse("list_required", "$.request.file_mutations", "causal file mutation evidence is required")
    mutation_ids = set()
    covered_source_paths = set()
    target_paths = set()
    mutation_records = []
    successor_inventory = []
    forward_mutation_map = []
    reverse_ancestry_map = []
    loss_exhaust = []
    reconstructed_bytes = {}
    for index, mutation in enumerate(mutations):
        mutation_path = f"$.request.file_mutations[{index}]"
        _closed(
            mutation,
            mutation_path,
            (
                "mutation_id",
                "action",
                "source_path",
                "source_content_head",
                "target_path",
                "target_content_head",
                "target_bytes",
                "target_content",
                "inverse",
                "parent_refs",
            ),
        )
        _identifier(mutation["mutation_id"], f"{mutation_path}.mutation_id")
        if mutation["mutation_id"] in mutation_ids:
            _refuse("duplicate_item", f"{mutation_path}.mutation_id", "duplicate mutation id")
        mutation_ids.add(mutation["mutation_id"])
        action = mutation["action"]
        if action not in ("retained", "replaced", "moved", "removed", "new"):
            _refuse("invalid_enum", f"{mutation_path}.action", "unknown file mutation action")
        source_entry = None
        if mutation["source_path"] is not None:
            _relative_repository_path(mutation["source_path"], f"{mutation_path}.source_path")
            source_entry = inventory_by_path.get(mutation["source_path"])
            if source_entry is None:
                _refuse("binding_mismatch", f"{mutation_path}.source_path", "mutation source path absent")
            if mutation["source_path"] in covered_source_paths:
                _refuse("duplicate_item", f"{mutation_path}.source_path", "source file mutated more than once")
            covered_source_paths.add(mutation["source_path"])
            _sha256(mutation["source_content_head"], f"{mutation_path}.source_content_head")
            if mutation["source_content_head"] != source_entry["content_sha256"]:
                _refuse(
                    "binding_mismatch",
                    f"{mutation_path}.source_content_head",
                    "mutation does not bind exact ancestor content",
                )
        elif mutation["source_content_head"] is not None:
            _refuse(
                "invalid_mutation",
                f"{mutation_path}.source_content_head",
                "new content cannot claim an ancestor content head",
            )
        target_data = None
        if mutation["target_path"] is not None:
            _relative_repository_path(mutation["target_path"], f"{mutation_path}.target_path")
            if mutation["target_path"] in target_paths:
                _refuse("duplicate_item", f"{mutation_path}.target_path", "duplicate successor path")
            target_paths.add(mutation["target_path"])
            _sha256(mutation["target_content_head"], f"{mutation_path}.target_content_head")
            _integer(mutation["target_bytes"], f"{mutation_path}.target_bytes", 0, MAX_INTEGER)
            target_data = _snapshot_content_bytes(
                mutation["target_content"],
                f"{mutation_path}.target_content",
            )
            if (
                len(target_data) != mutation["target_bytes"]
                or hashlib.sha256(target_data).hexdigest()
                != mutation["target_content_head"]
            ):
                _refuse(
                    "content_hash_mismatch",
                    f"{mutation_path}.target_content",
                    "successor bytes differ from target content head/length",
                )
        elif (
            mutation["target_content_head"] is not None
            or mutation["target_bytes"] is not None
            or mutation["target_content"] is not None
        ):
            _refuse("invalid_mutation", mutation_path, "removed content cannot declare successor bytes")
        inverse = _closed(
            mutation["inverse"],
            f"{mutation_path}.inverse",
            ("mode", "loss_class", "content"),
        )
        if inverse["mode"] not in (
            "successor-content",
            "retained-delta",
            "source-ref-only",
            "not-applicable",
        ):
            _refuse("invalid_enum", f"{mutation_path}.inverse.mode", "unknown inverse mode")
        if inverse["loss_class"] not in (
            "none",
            "content-unavailable",
            "irreversible-transform",
            "external-dependency",
        ):
            _refuse(
                "invalid_enum",
                f"{mutation_path}.inverse.loss_class",
                "unknown inverse loss class",
            )
        inverse_data = None
        if inverse["content"] is not None:
            inverse_data = _snapshot_content_bytes(
                inverse["content"],
                f"{mutation_path}.inverse.content",
            )
        _sha_list(mutation["parent_refs"], f"{mutation_path}.parent_refs", allow_empty=False)
        if source_entry is not None:
            for parent in (source["head"], source_entry["content_sha256"]):
                if parent not in mutation["parent_refs"]:
                    _refuse(
                        "missing_provenance",
                        f"{mutation_path}.parent_refs",
                        "source mutation must retain ancestor Frame and content heads",
                    )
        elif intent["intent_head"] not in mutation["parent_refs"]:
            _refuse(
                "missing_provenance",
                f"{mutation_path}.parent_refs",
                "new content must retain mutation intent head",
            )
        if action == "retained":
            if (
                source_entry is None
                or mutation["target_path"] != mutation["source_path"]
                or mutation["target_content_head"] != source_entry["content_sha256"]
                or mutation["target_bytes"] != source_entry["bytes"]
            ):
                _refuse("invalid_mutation", mutation_path, "retained file must remain byte-identical")
        elif action == "replaced":
            if (
                source_entry is None
                or mutation["target_path"] != mutation["source_path"]
                or mutation["target_content_head"] == source_entry["content_sha256"]
            ):
                _refuse("invalid_mutation", mutation_path, "replacement must change content at same path")
        elif action == "moved":
            if (
                source_entry is None
                or mutation["target_path"] == mutation["source_path"]
                or mutation["target_content_head"] != source_entry["content_sha256"]
                or mutation["target_bytes"] != source_entry["bytes"]
            ):
                _refuse("invalid_mutation", mutation_path, "move must preserve content at a new path")
        elif action == "removed":
            if source_entry is None or mutation["target_path"] is not None:
                _refuse("invalid_mutation", mutation_path, "removed file must have source only")
        else:
            if source_entry is not None or mutation["target_path"] is None:
                _refuse("invalid_mutation", mutation_path, "new file must have target only")
        if action in ("retained", "moved"):
            if (
                inverse["mode"] != "successor-content"
                or inverse["loss_class"] != "none"
                or inverse_data is not None
            ):
                _refuse(
                    "invalid_inverse",
                    f"{mutation_path}.inverse",
                    "retained/moved files reconstruct from successor content",
                )
            reconstructed_bytes[mutation["source_path"]] = target_data
        elif action in ("replaced", "removed"):
            if inverse["mode"] == "retained-delta":
                if (
                    inverse["loss_class"] != "none"
                    or inverse_data is None
                    or len(inverse_data) != source_entry["bytes"]
                    or hashlib.sha256(inverse_data).hexdigest()
                    != source_entry["content_sha256"]
                ):
                    _refuse(
                        "invalid_inverse",
                        f"{mutation_path}.inverse",
                        "retained delta must reproduce exact ancestor bytes",
                    )
                reconstructed_bytes[mutation["source_path"]] = inverse_data
            elif inverse["mode"] == "source-ref-only":
                if inverse["loss_class"] == "none" or inverse_data is not None:
                    _refuse(
                        "invalid_inverse",
                        f"{mutation_path}.inverse",
                        "source-ref-only inverse requires explicit non-none loss class",
                    )
                loss_exhaust.append(
                    {
                        "source_path": mutation["source_path"],
                        "source_content_head": source_entry["content_sha256"],
                        "loss_class": inverse["loss_class"],
                        "mutation_id": mutation["mutation_id"],
                    }
                )
            else:
                _refuse(
                    "invalid_inverse",
                    f"{mutation_path}.inverse",
                    "replaced/removed file requires retained-delta or source-ref-only",
                )
        else:
            if (
                inverse["mode"] != "not-applicable"
                or inverse["loss_class"] != "none"
                or inverse_data is not None
            ):
                _refuse(
                    "invalid_inverse",
                    f"{mutation_path}.inverse",
                    "new content has no ancestor inverse",
                )
        mutation_record = _json_copy(mutation)
        mutation_records.append(mutation_record)
        if source_entry is not None:
            forward_mutation_map.append(
                {
                    "source_path": mutation["source_path"],
                    "source_content_head": source_entry["content_sha256"],
                    "action": action,
                    "target_path": mutation["target_path"],
                    "target_content_head": mutation["target_content_head"],
                    "mutation_id": mutation["mutation_id"],
                }
            )
        if mutation["target_path"] is not None:
            ancestry_class = (
                "new"
                if action == "new"
                else ("inherited" if action in ("retained", "moved") else "derived")
            )
            reverse_ancestry_map.append(
                {
                    "successor_path": mutation["target_path"],
                    "successor_content_head": mutation["target_content_head"],
                    "ancestry_class": ancestry_class,
                    "source_path": mutation["source_path"],
                    "source_content_head": mutation["source_content_head"],
                    "mutation_id": mutation["mutation_id"],
                    "inverse_mode": inverse["mode"],
                    "loss_class": inverse["loss_class"],
                }
            )
            successor_inventory.append(
                {
                    "path": mutation["target_path"],
                    "content_sha256": mutation["target_content_head"],
                    "bytes": mutation["target_bytes"],
                    "caused_by_mutation_id": mutation["mutation_id"],
                    "action": action,
                }
            )
    if covered_source_paths != set(inventory_by_path):
        missing_paths = sorted(set(inventory_by_path) - covered_source_paths)
        _refuse(
            "mutation_coverage",
            "$.request.file_mutations",
            "every framed source file requires one causal mutation record: "
            + ", ".join(missing_paths),
        )
    if lineage_policy["mode"] == "lossless":
        if loss_exhaust or set(reconstructed_bytes) != set(inventory_by_path):
            _refuse(
                "lossless_reconstruction_failed",
                "$.request.file_mutations",
                "lossless successor lacks exact inverse bytes for every ancestor file",
            )
        reconstruction_material = []
        for path_value in sorted(reconstructed_bytes):
            data = reconstructed_bytes[path_value]
            source_entry = inventory_by_path[path_value]
            if (
                len(data) != source_entry["bytes"]
                or hashlib.sha256(data).hexdigest()
                != source_entry["content_sha256"]
            ):
                _refuse(
                    "lossless_reconstruction_failed",
                    "$.request.file_mutations",
                    f"reconstructed ancestor bytes mismatch: {path_value}",
                )
            reconstruction_material.append(
                {
                    "path": path_value,
                    "content_sha256": source_entry["content_sha256"],
                    "bytes": source_entry["bytes"],
                }
            )
        reconstruction_test_head = canonical_digest(
            "ancestor-byte-reconstruction/v1",
            reconstruction_material,
        )
        round_trip_supported = True
        direct_mapping_claimed = True
    else:
        if not loss_exhaust:
            _refuse(
                "loss_class_missing",
                "$.request.file_mutations",
                "lossy successor must declare at least one unavailable source loss",
            )
        reconstruction_test_head = None
        round_trip_supported = False
        direct_mapping_claimed = False
    successor_inventory.sort(key=lambda item: item["path"])
    forward_mutation_map.sort(key=lambda item: item["source_path"])
    reverse_ancestry_map.sort(key=lambda item: item["successor_path"])
    loss_exhaust.sort(key=lambda item: item["source_path"])
    mutation_manifest_head = canonical_digest(
        "self-host-file-mutations/v1",
        sorted(mutation_records, key=lambda item: item["mutation_id"]),
    )
    successor_inventory_head = canonical_digest(
        "self-host-successor-inventory/v1",
        successor_inventory,
    )
    forward_mutation_map_head = canonical_digest(
        "self-host-forward-mutation-map/v1",
        forward_mutation_map,
    )
    reverse_ancestry_map_head = canonical_digest(
        "self-host-reverse-ancestry-map/v1",
        reverse_ancestry_map,
    )
    loss_exhaust_head = canonical_digest(
        "self-host-loss-exhaust/v1",
        loss_exhaust,
    )

    selected = request["selected_traits"]
    omitted = request["omitted_traits"]
    if not isinstance(selected, list) or not isinstance(omitted, list):
        _refuse("list_required", "$.request", "selected and omitted traits must be lists")
    selected_ids = set()
    for index, trait in enumerate(selected):
        trait_path = f"$.request.selected_traits[{index}]"
        _closed(
            trait,
            trait_path,
            ("trait_id", "source_paths", "successor_component", "evidence_head"),
        )
        _identifier(trait["trait_id"], f"{trait_path}.trait_id")
        _unique_strings(
            trait["source_paths"],
            f"{trait_path}.source_paths",
            maximum=MAX_REFS,
            allow_empty=False,
        )
        _identifier(trait["successor_component"], f"{trait_path}.successor_component")
        _sha256(trait["evidence_head"], f"{trait_path}.evidence_head")
        if trait["trait_id"] in selected_ids:
            _refuse("duplicate_item", f"{trait_path}.trait_id", "duplicate selected trait")
        selected_ids.add(trait["trait_id"])
        if not set(trait["source_paths"]).issubset(inventory_by_path):
            _refuse("binding_mismatch", f"{trait_path}.source_paths", "trait references unknown source path")
    required_selected = set(PRIOR_ART_PROVENANCE["safe_mapping"])
    if selected_ids != required_selected:
        _refuse(
            "trait_coverage",
            "$.request.selected_traits",
            "selected traits must exactly cover pinned safe concepts",
        )
    omitted_ids = set()
    for index, trait in enumerate(omitted):
        trait_path = f"$.request.omitted_traits[{index}]"
        _closed(
            trait,
            trait_path,
            ("trait_id", "source_paths", "reason_code", "evidence_head"),
        )
        _identifier(trait["trait_id"], f"{trait_path}.trait_id")
        _unique_strings(
            trait["source_paths"],
            f"{trait_path}.source_paths",
            maximum=MAX_REFS,
        )
        _identifier(trait["reason_code"], f"{trait_path}.reason_code")
        _sha256(trait["evidence_head"], f"{trait_path}.evidence_head")
        if trait["trait_id"] in omitted_ids:
            _refuse("duplicate_item", f"{trait_path}.trait_id", "duplicate omitted trait")
        omitted_ids.add(trait["trait_id"])
        if not set(trait["source_paths"]).issubset(inventory_by_path):
            _refuse("binding_mismatch", f"{trait_path}.source_paths", "omission references unknown source path")
    if omitted_ids != set(PRIOR_ART_PROVENANCE["excluded_mechanisms"]):
        _refuse(
            "unsafe_substrate_not_omitted",
            "$.request.omitted_traits",
            "omitted traits must exactly cover excluded prior-art mechanisms",
        )

    hotload = _validate_double_hotload_result(
        request["hotload_result"],
        "$.request.hotload_result",
    )
    if not hotload["locked"] or hotload["source_frame_head"] != source["head"]:
        _refuse(
            "binding_mismatch",
            "$.request.hotload_result",
            "locked double-hotload result must derive from the repository Frame",
        )
    frame = _validate_compatibility_frame(
        request["compatibility_frame"],
        "$.request.compatibility_frame",
    )
    if frame["lens"]["hotload_lock_head"] != hotload["head"]:
        _refuse(
            "binding_mismatch",
            "$.request.compatibility_frame.lens.hotload_lock_head",
            "compatibility Frame does not bind repository mutation hotload",
        )
    projections = request["protocol_projections"]
    if not isinstance(projections, list) or len(projections) != 4:
        _refuse("list_required", "$.request.protocol_projections", "four protocol projections required")
    projection_records = {}
    for index, projection in enumerate(projections):
        projection_path = f"$.request.protocol_projections[{index}]"
        _closed(
            projection,
            projection_path,
            ("protocol", "profile_head", "restrictions", "bounds"),
        )
        if projection["protocol"] not in (
            "workspace",
            "work-organization",
            "hive",
            "federation",
        ):
            _refuse("invalid_enum", f"{projection_path}.protocol", "unknown protocol projection")
        _sha256(projection["profile_head"], f"{projection_path}.profile_head")
        _unique_strings(
            projection["restrictions"],
            f"{projection_path}.restrictions",
            maximum=MAX_REFS,
        )
        _resource_vector(projection["bounds"], f"{projection_path}.bounds")
        if projection["protocol"] in projection_records:
            _refuse("duplicate_item", f"{projection_path}.protocol", "duplicate protocol projection")
        projection_records[projection["protocol"]] = _json_copy(projection)
    if set(projection_records) != {
        "workspace",
        "work-organization",
        "hive",
        "federation",
    }:
        _refuse("missing_field", "$.request.protocol_projections", "protocol projection set incomplete")

    compiler_sha = _sha256(request["compiler_sha256"], "$.request.compiler_sha256")
    runtime_head = _sha256(request["runtime_head"], "$.request.runtime_head")
    private_hive_policy_head = _sha256(
        request["private_hive_policy_head"],
        "$.request.private_hive_policy_head",
    )
    selected_head = canonical_digest("self-host-selected-traits/v1", selected)
    omitted_head = canonical_digest("self-host-omitted-traits/v1", omitted)
    projections_head = canonical_digest(
        "self-host-protocol-projections/v1",
        [projection_records[key] for key in sorted(projection_records)],
    )
    proposal_facts = {
        "source_frame_head": source["head"],
        "mutation_intent_head": intent["intent_head"],
        "mutation_manifest_head": mutation_manifest_head,
        "successor_inventory_head": successor_inventory_head,
        "forward_mutation_map_head": forward_mutation_map_head,
        "reverse_ancestry_map_head": reverse_ancestry_map_head,
        "loss_exhaust_head": loss_exhaust_head,
        "lineage_mode": lineage_policy["mode"],
        "selected_traits_head": selected_head,
        "omitted_traits_head": omitted_head,
        "hotload_result_head": hotload["head"],
        "compatibility_frame_head": frame["head"],
        "compiler_sha256": compiler_sha,
        "runtime_head": runtime_head,
        "protocol_projections_head": projections_head,
    }
    proposal_head = canonical_digest("self-host-proposal/v1", proposal_facts)
    required_gates = (
        "inventory-closure",
        "unmapped-executable-surface",
        "ambient-dependency",
        "state-migration",
        "privacy",
        "authority",
        "replay",
        "mutation",
    )
    gates = request["unknown_unknown_gates"]
    if not isinstance(gates, list) or len(gates) != len(required_gates):
        _refuse(
            "list_required",
            "$.request.unknown_unknown_gates",
            "exact unknown-unknown gate set required",
        )
    gate_audit = []
    seen = set()
    gate_receipts = []
    for index, gate_record in enumerate(gates):
        gate_path = f"$.request.unknown_unknown_gates[{index}]"
        _closed(gate_record, gate_path, ("gate", "passed", "receipt"))
        gate = gate_record["gate"]
        if gate not in required_gates or gate in seen:
            _refuse("invalid_gate", f"{gate_path}.gate", "unknown or duplicate unknown-unknown gate")
        passed = _boolean(gate_record["passed"], f"{gate_path}.passed")
        receipt = _validate_receipt(gate_record["receipt"], f"{gate_path}.receipt")
        facts_head = canonical_digest(
            "self-host-unknown-gate/v1",
            {
                "gate": gate,
                "passed": passed,
                "proposal_head": proposal_head,
            },
        )
        if receipt["facts_head"] != facts_head:
            _refuse(
                "receipt_binding_mismatch",
                f"{gate_path}.receipt.facts_head",
                "unknown-unknown gate receipt does not bind exact proposal",
            )
        seen.add(gate)
        gate_receipts.append(receipt)
        gate_audit.append({"gate": gate, "passed": passed, "receipt_head": receipt["head"]})
    failed = sorted(item["gate"] for item in gate_audit if not item["passed"])
    if failed:
        _refuse(
            "unknown_unknown_gate_failed",
            "$.request.unknown_unknown_gates",
            "self-host successor refused by gates: " + ", ".join(failed),
        )
    package = compile_static_agent(
        {
            "schema": "autobest-static-agent-compile-request/1",
            "compatibility_frame": frame,
            "compiler_sha256": compiler_sha,
            "runtime_head": runtime_head,
            "private_hive_policy_head": private_hive_policy_head,
            "compile_mode": "deterministic-field-map",
            "captured_agent": None,
            "captured_mutation_tests": None,
            "captured_tests_receipt": None,
            "generation_receipt": request["generation_receipt"],
        }
    )
    if package["package"]["agent_sha256"] not in {
        entry["content_sha256"] for entry in successor_inventory
    }:
        _refuse(
            "compiled_agent_not_in_successor",
            "$.request.file_mutations",
            "successor inventory must contain the exact compiled static agent bytes",
        )
    successor_body = {
        "schema": "autobest-self-hosted-successor/2",
        "successor_id": "successor:" + canonical_digest(
            "self-host-successor-id/v1",
            {
                "source_frame_head": source["head"],
                "agent_sha256": package["package"]["agent_sha256"],
                "proposal_head": proposal_head,
                "successor_inventory_head": successor_inventory_head,
            },
        )[:32],
        "source_repository": source["repository"],
        "source_commit": source["commit"],
        "source_inventory_head": source["inventory_head"],
        "mutation_intent_head": intent["intent_head"],
        "mutation_manifest_head": mutation_manifest_head,
        "file_mutations": sorted(
            mutation_records,
            key=lambda item: item["mutation_id"],
        ),
        "successor_inventory_head": successor_inventory_head,
        "successor_inventory": successor_inventory,
        "lineage_mode": lineage_policy["mode"],
        "forward_mutation_map_head": forward_mutation_map_head,
        "forward_mutation_map": forward_mutation_map,
        "reverse_ancestry_map_head": reverse_ancestry_map_head,
        "reverse_ancestry_map": reverse_ancestry_map,
        "inverse_reconstruction": {
            "round_trip_supported": round_trip_supported,
            "direct_mapping_claimed": direct_mapping_claimed,
            "reconstruction_test_head": reconstruction_test_head,
            "reconstructed_inventory_head": source["inventory_head"]
            if round_trip_supported
            else None,
        },
        "loss_exhaust_head": loss_exhaust_head,
        "loss_exhaust": loss_exhaust,
        "selected_traits": _json_copy(selected),
        "omitted_traits": _json_copy(omitted),
        "compatibility_frame_head": frame["head"],
        "agent_sha256": package["package"]["agent_sha256"],
        "compiler_sha256": compiler_sha,
        "runtime_head": runtime_head,
        "metadata_head": package["package"]["metadata_head"],
        "mutation_tests_head": package["package"]["mutation_tests_head"],
        "protocol_projections": [
            projection_records[key] for key in sorted(projection_records)
        ],
        "unknown_unknown_gate_audit": sorted(gate_audit, key=lambda item: item["gate"]),
        "ancestor_frame_unchanged": True,
        "ancestor_commit_recoverable": True,
        "ancestor_inventory_recoverable": True,
        "legacy_agents_relabelled": False,
        "legacy_rapp1_conformance_claimed": False,
        "successor_only": True,
        "additive_sidecar_only": False,
        "successor_files_may_rewrite_move_remove_add": True,
        "target_compatibility": "RAPP/1",
        "rapp1_conformance_claimed": False,
        "authority_granted": False,
        "adopted": False,
    }
    successor = dict(successor_body)
    successor["head"] = canonical_digest(
        "self-hosted-successor/v2",
        successor_body,
    )
    result = _base_plan("self_host_repository")
    result.update(
        {
            "schema": "autobest-self-hosting-proof-candidate/1",
            "ok": True,
            "source_frame": {
                "head": source["head"],
                "repository": source["repository"],
                "commit": source["commit"],
                "inventory_head": source["inventory_head"],
                "entry_count": len(source["inventory"]),
                "modified": False,
            },
            "successor": successor,
            "static_agent_package": package["package"],
            "proposal_head": proposal_head,
            "unknown_unknown_gate_audit": sorted(gate_audit, key=lambda item: item["gate"]),
            "lineage": _lineage(
                [
                    source,
                    source["inventory_receipt"],
                    hotload,
                    frame["lens"]["portable_artifact"]["private_hive_receipt"],
                    *gate_receipts,
                ]
            ),
        }
    )
    return _finalize_plan(result, "self-hosting-proof-plan/v1")


def artifact_bundle(request):
    """Package a complete generated successor program with independent verification."""

    _prepare_input(request, "$.request")
    fields = (
        "schema",
        "source_frame_head",
        "mutation_manifest_head",
        "compatibility_frame",
        "entrypoint",
        "files",
        "candidate_test_heads",
        "host_tests",
        "canonical_tests",
        "controlled_mutants",
        "selection_receipt",
    )
    _closed(request, "$.request", fields)
    if request["schema"] != "autobest-artifact-bundle-request/1":
        _refuse(
            "unsupported_schema",
            "$.request.schema",
            "expected autobest-artifact-bundle-request/1",
        )
    source_frame_head = _sha256(
        request["source_frame_head"],
        "$.request.source_frame_head",
    )
    mutation_manifest_head = _sha256(
        request["mutation_manifest_head"],
        "$.request.mutation_manifest_head",
    )
    frame = _validate_compatibility_frame(
        request["compatibility_frame"],
        "$.request.compatibility_frame",
    )
    entrypoint = _relative_repository_path(
        request["entrypoint"],
        "$.request.entrypoint",
    )
    files = request["files"]
    if not isinstance(files, list) or not files or len(files) > MAX_BUNDLE_FILES:
        _refuse(
            "list_required",
            "$.request.files",
            f"expected 1..{MAX_BUNDLE_FILES} generated artifact files",
        )
    allowed_kinds = {
        "agent-entrypoint",
        "code",
        "data",
        "schema",
        "fixture",
        "test",
        "documentation",
        "migration",
        "manifest",
    }
    paths = set()
    bundle_files = []
    inventory_material = []
    total_bytes = 0
    for index, file_record in enumerate(files):
        file_path = f"$.request.files[{index}]"
        _closed(
            file_record,
            file_path,
            (
                "path",
                "kind",
                "bytes",
                "sha256",
                "content",
                "caused_by_mutation_id",
                "parent_refs",
            ),
        )
        path_value = _relative_repository_path(
            file_record["path"],
            f"{file_path}.path",
        )
        if path_value in paths:
            _refuse("duplicate_item", f"{file_path}.path", "duplicate artifact path")
        paths.add(path_value)
        if file_record["kind"] not in allowed_kinds:
            _refuse("invalid_enum", f"{file_path}.kind", "unknown artifact file kind")
        _identifier(
            file_record["caused_by_mutation_id"],
            f"{file_path}.caused_by_mutation_id",
        )
        _sha_list(
            file_record["parent_refs"],
            f"{file_path}.parent_refs",
            allow_empty=False,
        )
        if (
            source_frame_head not in file_record["parent_refs"]
            and mutation_manifest_head not in file_record["parent_refs"]
        ):
            _refuse(
                "missing_provenance",
                f"{file_path}.parent_refs",
                "artifact file must bind source Frame or mutation manifest",
            )
        data = _snapshot_content_bytes(
            file_record["content"],
            f"{file_path}.content",
        )
        byte_count = _integer(
            file_record["bytes"],
            f"{file_path}.bytes",
            0,
            MAX_AGENT_FILE_BYTES,
        )
        digest = _sha256(file_record["sha256"], f"{file_path}.sha256")
        if len(data) != byte_count or hashlib.sha256(data).hexdigest() != digest:
            _refuse(
                "content_hash_mismatch",
                file_path,
                "artifact bytes differ from declared length/SHA",
            )
        total_bytes += byte_count
        bundle_files.append(_json_copy(file_record))
        inventory_material.append(
            {
                "path": path_value,
                "kind": file_record["kind"],
                "bytes": byte_count,
                "sha256": digest,
                "caused_by_mutation_id": file_record["caused_by_mutation_id"],
                "parent_refs": list(file_record["parent_refs"]),
            }
        )
    if total_bytes > MAX_INPUT_BYTES:
        _refuse(
            "oversize_content",
            "$.request.files",
            f"artifact bundle exceeds {MAX_INPUT_BYTES} bytes",
        )
    entrypoint_records = [
        item
        for item in bundle_files
        if item["path"] == entrypoint and item["kind"] == "agent-entrypoint"
    ]
    if len(entrypoint_records) != 1:
        _refuse(
            "missing_field",
            "$.request.entrypoint",
            "bundle requires exactly one agent-entrypoint file at the declared path",
        )
    inventory_material.sort(key=lambda item: item["path"])
    inventory_head = canonical_digest(
        "artifact-bundle-inventory/v1",
        inventory_material,
    )
    candidate_test_heads = _bounded_sha_list(
        request["candidate_test_heads"],
        "$.request.candidate_test_heads",
        MAX_BUNDLE_FILES,
    )
    test_file_heads = {
        item["sha256"] for item in bundle_files if item["kind"] == "test"
    }
    if not set(candidate_test_heads).issubset(test_file_heads):
        _refuse(
            "binding_mismatch",
            "$.request.candidate_test_heads",
            "candidate-generated test heads must name bundled test files",
        )

    def validate_independent_tests(records, scope, path):
        if not isinstance(records, list) or not records:
            _refuse(
                "independent_proof_missing",
                path,
                f"at least one passed {scope} test receipt is required",
            )
        validated = []
        seen_ids = set()
        for index, test in enumerate(records):
            test_path = f"{path}[{index}]"
            _closed(test, test_path, ("test_id", "test_head", "status", "receipt"))
            _identifier(test["test_id"], f"{test_path}.test_id")
            if test["test_id"] in seen_ids:
                _refuse("duplicate_item", f"{test_path}.test_id", "duplicate independent test id")
            seen_ids.add(test["test_id"])
            _sha256(test["test_head"], f"{test_path}.test_head")
            if test["status"] != "passed":
                _refuse(
                    "independent_test_failed",
                    f"{test_path}.status",
                    f"{scope} test did not pass",
                )
            _validate_receipt(test["receipt"], f"{test_path}.receipt")
            facts_head = canonical_digest(
                "artifact-bundle-independent-test/v1",
                {
                    "scope": scope,
                    "test_id": test["test_id"],
                    "test_head": test["test_head"],
                    "status": test["status"],
                    "inventory_head": inventory_head,
                    "compatibility_frame_head": frame["head"],
                },
            )
            if test["receipt"]["facts_head"] != facts_head:
                _refuse(
                    "receipt_binding_mismatch",
                    f"{test_path}.receipt.facts_head",
                    "independent test receipt does not bind bundle and Frame",
                )
            validated.append(_json_copy(test))
        return validated

    host_tests = validate_independent_tests(
        request["host_tests"],
        "host",
        "$.request.host_tests",
    )
    canonical_tests = validate_independent_tests(
        request["canonical_tests"],
        "canonical",
        "$.request.canonical_tests",
    )
    independent_test_ids = {
        item["test_id"] for item in host_tests + canonical_tests
    }
    mutants = request["controlled_mutants"]
    if not isinstance(mutants, list) or not mutants:
        _refuse(
            "independent_proof_missing",
            "$.request.controlled_mutants",
            "at least one detected controlled mutant is required",
        )
    mutant_audit = []
    mutant_receipts = []
    seen_mutants = set()
    for index, mutant in enumerate(mutants):
        mutant_path = f"$.request.controlled_mutants[{index}]"
        _closed(
            mutant,
            mutant_path,
            (
                "mutant_id",
                "target_path",
                "mutation_head",
                "expected_test_ids",
                "detected",
                "receipt",
            ),
        )
        _identifier(mutant["mutant_id"], f"{mutant_path}.mutant_id")
        if mutant["mutant_id"] in seen_mutants:
            _refuse("duplicate_item", f"{mutant_path}.mutant_id", "duplicate mutant")
        seen_mutants.add(mutant["mutant_id"])
        target_path = _relative_repository_path(
            mutant["target_path"],
            f"{mutant_path}.target_path",
        )
        if target_path not in paths:
            _refuse("binding_mismatch", f"{mutant_path}.target_path", "mutant target absent")
        _sha256(mutant["mutation_head"], f"{mutant_path}.mutation_head")
        _unique_strings(
            mutant["expected_test_ids"],
            f"{mutant_path}.expected_test_ids",
            maximum=MAX_REFS,
            allow_empty=False,
            identifiers=True,
        )
        if not set(mutant["expected_test_ids"]).issubset(independent_test_ids):
            _refuse(
                "binding_mismatch",
                f"{mutant_path}.expected_test_ids",
                "mutant must be checked by independent host/canonical tests",
            )
        if mutant["detected"] is not True:
            _refuse(
                "mutant_survived",
                f"{mutant_path}.detected",
                "controlled mutant was not detected",
            )
        receipt = _validate_receipt(mutant["receipt"], f"{mutant_path}.receipt")
        facts_head = canonical_digest(
            "artifact-bundle-mutant/v1",
            {
                "mutant_id": mutant["mutant_id"],
                "target_path": target_path,
                "mutation_head": mutant["mutation_head"],
                "expected_test_ids": list(mutant["expected_test_ids"]),
                "detected": True,
                "inventory_head": inventory_head,
            },
        )
        if receipt["facts_head"] != facts_head:
            _refuse(
                "receipt_binding_mismatch",
                f"{mutant_path}.receipt.facts_head",
                "mutant receipt does not bind exact mutation/detection evidence",
            )
        mutant_receipts.append(receipt)
        mutant_audit.append(_json_copy(mutant))
    verification_head = canonical_digest(
        "artifact-bundle-verification/v1",
        {
            "inventory_head": inventory_head,
            "host_test_receipts": sorted(item["receipt"]["head"] for item in host_tests),
            "canonical_test_receipts": sorted(
                item["receipt"]["head"] for item in canonical_tests
            ),
            "mutant_receipts": sorted(receipt["head"] for receipt in mutant_receipts),
        },
    )
    selection_receipt = _validate_receipt(
        request["selection_receipt"],
        "$.request.selection_receipt",
    )
    if selection_receipt["facts_head"] != verification_head:
        _refuse(
            "receipt_binding_mismatch",
            "$.request.selection_receipt.facts_head",
            "selection receipt does not bind independent tests and mutants",
        )
    bundle_body = {
        "schema": "autobest-artifact-bundle/1",
        "bundle_id": "bundle:" + canonical_digest(
            "artifact-bundle-id/v1",
            {
                "inventory_head": inventory_head,
                "compatibility_frame_head": frame["head"],
                "verification_head": verification_head,
            },
        )[:32],
        "source_frame_head": source_frame_head,
        "mutation_manifest_head": mutation_manifest_head,
        "compatibility_frame_head": frame["head"],
        "entrypoint": entrypoint,
        "inventory_head": inventory_head,
        "files": sorted(bundle_files, key=lambda item: item["path"]),
        "candidate_test_heads": list(candidate_test_heads),
        "host_tests": host_tests,
        "canonical_tests": canonical_tests,
        "controlled_mutants": mutant_audit,
        "verification_head": verification_head,
        "selection_receipt_head": selection_receipt["head"],
        "selected": True,
        "selection_mode": "atomic-verified-bundle",
        "adopted": False,
        "activated": False,
        "authority_granted": False,
        "candidate_generated_tests_are_independent_proof": False,
    }
    bundle = dict(bundle_body)
    bundle["head"] = canonical_digest(
        "artifact-bundle/v1",
        bundle_body,
    )
    result = _base_plan("artifact_bundle")
    result.update(
        {
            "schema": "autobest-artifact-bundle-candidate/1",
            "ok": True,
            "bundle": bundle,
            "private_hive_handshake_package": {
                "schema": "private-hive-program-handshake-candidate/1",
                "bundle_head": bundle["head"],
                "inventory_head": inventory_head,
                "entrypoint": entrypoint,
                "entrypoint_sha256": entrypoint_records[0]["sha256"],
                "verification_head": verification_head,
                "signature_required": True,
                "signed": False,
                "registered": False,
                "authority_granted": False,
            },
            "lineage": {
                "source_frame_head": source_frame_head,
                "mutation_manifest_head": mutation_manifest_head,
                "compatibility_frame_head": frame["head"],
                "selection_receipt_head": selection_receipt["head"],
            },
        }
    )
    return _finalize_plan(result, "artifact-bundle-plan/v1")


def _validate_self_hosted_successor(value, path):
    if not isinstance(value, dict) or value.get("schema") != "autobest-self-hosted-successor/2":
        _refuse("unsupported_schema", path, "expected autobest-self-hosted-successor/2")
    required = {
        "head",
        "source_repository",
        "source_commit",
        "source_inventory_head",
        "mutation_manifest_head",
        "forward_mutation_map",
        "reverse_ancestry_map",
        "selected_traits",
        "omitted_traits",
        "compatibility_frame_head",
        "agent_sha256",
        "metadata_head",
        "mutation_tests_head",
    }
    if not required.issubset(value):
        _refuse("missing_field", path, "successor is missing required transport evidence")
    _sha256(value["head"], f"{path}.head")
    body = {key: item for key, item in value.items() if key != "head"}
    expected = canonical_digest("self-hosted-successor/v2", body)
    if value["head"] != expected:
        _refuse("head_mismatch", f"{path}.head", f"expected successor head {expected}")
    return value


def _validate_artifact_bundle_value(value, path):
    if not isinstance(value, dict) or value.get("schema") != "autobest-artifact-bundle/1":
        _refuse("unsupported_schema", path, "expected autobest-artifact-bundle/1")
    for field in (
        "head",
        "source_frame_head",
        "mutation_manifest_head",
        "compatibility_frame_head",
        "inventory_head",
        "entrypoint",
        "files",
        "host_tests",
        "canonical_tests",
        "controlled_mutants",
        "verification_head",
    ):
        if field not in value:
            _refuse("missing_field", path, f"artifact bundle missing {field}")
    _sha256(value["head"], f"{path}.head")
    body = {key: item for key, item in value.items() if key != "head"}
    expected = canonical_digest("artifact-bundle/v1", body)
    if value["head"] != expected:
        _refuse("head_mismatch", f"{path}.head", f"expected artifact bundle head {expected}")
    return value


def _validate_mutation_offer(value, path):
    if not isinstance(value, dict) or value.get("schema") != "autobest-mutation-offer/1":
        _refuse("unsupported_schema", path, "expected autobest-mutation-offer/1")
    _sha256(value.get("head"), f"{path}.head")
    body = {key: item for key, item in value.items() if key != "head"}
    expected = canonical_digest("mutation-offer/v1", body)
    if value["head"] != expected:
        _refuse("head_mismatch", f"{path}.head", f"expected mutation offer head {expected}")
    return value


def mutation_offer(request):
    """Project a complete successor generation as inert PR/transport evidence."""

    _prepare_input(request, "$.request")
    fields = (
        "schema",
        "source_organization_head",
        "source_frame",
        "successor",
        "artifact_bundle",
        "trait_mutations",
        "transport_policy_head",
        "offer_receipt",
    )
    _closed(request, "$.request", fields)
    if request["schema"] != "autobest-mutation-offer-request/1":
        _refuse(
            "unsupported_schema",
            "$.request.schema",
            "expected autobest-mutation-offer-request/1",
        )
    source_organization_head = _sha256(
        request["source_organization_head"],
        "$.request.source_organization_head",
    )
    source = _validate_repository_frame(
        request["source_frame"],
        "$.request.source_frame",
    )
    successor = _validate_self_hosted_successor(
        request["successor"],
        "$.request.successor",
    )
    bundle = _validate_artifact_bundle_value(
        request["artifact_bundle"],
        "$.request.artifact_bundle",
    )
    if (
        successor["source_repository"] != source["repository"]
        or successor["source_commit"] != source["commit"]
        or successor["source_inventory_head"] != source["inventory_head"]
    ):
        _refuse(
            "binding_mismatch",
            "$.request.successor",
            "successor does not bind the exact source repository generation",
        )
    if (
        bundle["source_frame_head"] != source["head"]
        or bundle["mutation_manifest_head"] != successor["mutation_manifest_head"]
        or bundle["compatibility_frame_head"] != successor["compatibility_frame_head"]
    ):
        _refuse(
            "binding_mismatch",
            "$.request.artifact_bundle",
            "artifact bundle does not bind source, mutation manifest, and compatibility Frame",
        )
    trait_mutations = request["trait_mutations"]
    if not isinstance(trait_mutations, list) or not trait_mutations:
        _refuse("list_required", "$.request.trait_mutations", "trait mutation map required")
    expected_traits = {
        item["trait_id"] for item in successor["selected_traits"] + successor["omitted_traits"]
    }
    observed_traits = set()
    forward_traits = []
    reverse_traits = []
    for index, trait in enumerate(trait_mutations):
        trait_path = f"$.request.trait_mutations[{index}]"
        _closed(
            trait,
            trait_path,
            (
                "trait_id",
                "action",
                "source_refs",
                "target_refs",
                "parent_refs",
            ),
        )
        _identifier(trait["trait_id"], f"{trait_path}.trait_id")
        if trait["trait_id"] in observed_traits:
            _refuse("duplicate_item", f"{trait_path}.trait_id", "duplicate trait mutation")
        observed_traits.add(trait["trait_id"])
        if trait["action"] not in ("retained", "replaced", "moved", "removed", "new"):
            _refuse("invalid_enum", f"{trait_path}.action", "unknown trait mutation action")
        _sha_list(trait["source_refs"], f"{trait_path}.source_refs")
        _sha_list(trait["target_refs"], f"{trait_path}.target_refs")
        _sha_list(trait["parent_refs"], f"{trait_path}.parent_refs", allow_empty=False)
        for parent in (source["head"], successor["head"]):
            if parent not in trait["parent_refs"]:
                _refuse(
                    "missing_provenance",
                    f"{trait_path}.parent_refs",
                    "trait mutation must bind source and successor generations",
                )
        if trait["action"] == "removed" and trait["target_refs"]:
            _refuse("invalid_mutation", trait_path, "removed trait cannot have target refs")
        if trait["action"] == "new" and trait["source_refs"]:
            _refuse("invalid_mutation", trait_path, "new trait cannot have source refs")
        forward_traits.append(_json_copy(trait))
        for target_ref in trait["target_refs"]:
            reverse_traits.append(
                {
                    "trait_id": trait["trait_id"],
                    "successor_ref": target_ref,
                    "source_refs": list(trait["source_refs"]),
                    "action": trait["action"],
                }
            )
    if not expected_traits.issubset(observed_traits):
        _refuse(
            "trait_coverage",
            "$.request.trait_mutations",
            "trait mutation map omits selected or omitted source traits",
        )
    forward_traits.sort(key=lambda item: item["trait_id"])
    reverse_traits.sort(key=lambda item: (item["trait_id"], item["successor_ref"]))
    trait_map_head = canonical_digest("mutation-offer-trait-map/v1", forward_traits)
    reverse_trait_map_head = canonical_digest(
        "mutation-offer-reverse-trait-map/v1",
        reverse_traits,
    )
    transport_policy_head = _sha256(
        request["transport_policy_head"],
        "$.request.transport_policy_head",
    )
    offer_facts = {
        "source_organization_head": source_organization_head,
        "source_frame_head": source["head"],
        "successor_head": successor["head"],
        "artifact_bundle_head": bundle["head"],
        "trait_map_head": trait_map_head,
        "reverse_trait_map_head": reverse_trait_map_head,
        "transport_policy_head": transport_policy_head,
    }
    offer_facts_head = canonical_digest("mutation-offer-facts/v1", offer_facts)
    offer_receipt = _validate_receipt(
        request["offer_receipt"],
        "$.request.offer_receipt",
    )
    if offer_receipt["facts_head"] != offer_facts_head:
        _refuse(
            "receipt_binding_mismatch",
            "$.request.offer_receipt.facts_head",
            "offer receipt does not bind complete transport projection",
        )
    offer_body = {
        "schema": "autobest-mutation-offer/1",
        "offer_id": "offer:" + offer_facts_head[:32],
        "transport_kind": "pull-request-projection",
        "source_organization_head": source_organization_head,
        "source_frame_head": source["head"],
        "source_commit": source["commit"],
        "source_inventory_head": source["inventory_head"],
        "successor_head": successor["head"],
        "successor_inventory_head": successor["successor_inventory_head"],
        "artifact_bundle_head": bundle["head"],
        "compatibility_frame_head": successor["compatibility_frame_head"],
        "compatibility_agent_sha256": successor["agent_sha256"],
        "metadata_head": successor["metadata_head"],
        "mutation_tests_head": successor["mutation_tests_head"],
        "forward_file_mutation_map_head": successor["forward_mutation_map_head"],
        "forward_file_mutation_map": _json_copy(successor["forward_mutation_map"]),
        "reverse_file_ancestry_map_head": successor["reverse_ancestry_map_head"],
        "reverse_file_ancestry_map": _json_copy(successor["reverse_ancestry_map"]),
        "trait_map_head": trait_map_head,
        "trait_mutations": forward_traits,
        "reverse_trait_map_head": reverse_trait_map_head,
        "reverse_trait_map": reverse_traits,
        "bundle_verification_head": bundle["verification_head"],
        "offer_receipt_head": offer_receipt["head"],
        "allowed_source_decisions": [
            "merge",
            "reject",
            "cherry-pick-traits",
            "re-lens-successor",
        ],
        "transport_performed": False,
        "merge_performed": False,
        "adoption_performed": False,
        "authority_granted": False,
        "ancestor_rewritten": False,
        "seed_influence": {
            "direct": False,
            "requires_separate_verified_selection_or_crossing": True,
            "current_offer_grants_seed_change": False,
        },
    }
    offer = dict(offer_body)
    offer["head"] = canonical_digest("mutation-offer/v1", offer_body)
    result = _base_plan("mutation_offer")
    result.update(
        {
            "schema": "autobest-mutation-offer-candidate/1",
            "ok": True,
            "offer": offer,
            "lineage": {
                "source_frame_head": source["head"],
                "successor_head": successor["head"],
                "artifact_bundle_head": bundle["head"],
                "offer_receipt_head": offer_receipt["head"],
            },
        }
    )
    return _finalize_plan(result, "mutation-offer-plan/v1")


def mutation_offer_decision(request):
    """Record a source-organization response to a mutation offer without granting authority."""

    _prepare_input(request, "$.request")
    _closed(
        request,
        "$.request",
        ("schema", "offer", "decision", "selected_trait_ids", "decision_receipt"),
    )
    if request["schema"] != "autobest-mutation-offer-decision-request/1":
        _refuse(
            "unsupported_schema",
            "$.request.schema",
            "expected autobest-mutation-offer-decision-request/1",
        )
    offer = _validate_mutation_offer(request["offer"], "$.request.offer")
    decision = request["decision"]
    if decision not in (
        "merge",
        "reject",
        "cherry-pick-traits",
        "re-lens-successor",
    ):
        _refuse("invalid_enum", "$.request.decision", "unknown mutation offer decision")
    selected_trait_ids = _unique_strings(
        request["selected_trait_ids"],
        "$.request.selected_trait_ids",
        maximum=MAX_REPOSITORY_ENTRIES,
        identifiers=True,
    )
    available_traits = {item["trait_id"] for item in offer["trait_mutations"]}
    if not set(selected_trait_ids).issubset(available_traits):
        _refuse("binding_mismatch", "$.request.selected_trait_ids", "selected trait absent from offer")
    if decision == "merge" and set(selected_trait_ids) != available_traits:
        _refuse("decision_mismatch", "$.request.selected_trait_ids", "merge requires all offered traits")
    if decision == "reject" and selected_trait_ids:
        _refuse("decision_mismatch", "$.request.selected_trait_ids", "reject selects no traits")
    if decision == "cherry-pick-traits" and not selected_trait_ids:
        _refuse("decision_mismatch", "$.request.selected_trait_ids", "cherry-pick requires traits")
    decision_facts = {
        "offer_head": offer["head"],
        "decision": decision,
        "selected_trait_ids": list(selected_trait_ids),
    }
    decision_facts_head = canonical_digest(
        "mutation-offer-decision/v1",
        decision_facts,
    )
    receipt = _validate_receipt(
        request["decision_receipt"],
        "$.request.decision_receipt",
    )
    if receipt["facts_head"] != decision_facts_head:
        _refuse(
            "receipt_binding_mismatch",
            "$.request.decision_receipt.facts_head",
            "decision receipt does not bind exact offer response",
        )
    result = _base_plan("mutation_offer_decision")
    result.update(
        {
            "schema": "autobest-mutation-offer-decision-evidence/1",
            "ok": True,
            "offer_head": offer["head"],
            "decision": decision,
            "selected_trait_ids": list(selected_trait_ids),
            "decision_receipt_head": receipt["head"],
            "next_action": (
                "construct-source-organization-successor"
                if decision in ("merge", "cherry-pick-traits")
                else (
                    "run-double-hotload-lens"
                    if decision == "re-lens-successor"
                    else "close-offer"
                )
            ),
            "transport_or_adoption_evidence_only": True,
            "authority_granted": False,
            "ancestor_rewritten": False,
            "seed_influence": {
                "direct": False,
                "requires_separate_verified_selection_or_crossing": True,
            },
        }
    )
    return _finalize_plan(result, "mutation-offer-decision-plan/v1")


def meta_evolution(request):
    """Evaluate one recursive improvement rung without automatic promotion."""

    _prepare_input(request, "$.request")
    fields = (
        "schema",
        "target_level",
        "trigger",
        "predecessor_frame_head",
        "candidate_frame_head",
        "mutation_manifest_head",
        "causal_refs",
        "specific_changes",
        "candidate_test_heads",
        "evidence",
        "metrics_bps",
        "thresholds_bps",
        "guard_receipts",
        "proposal_receipt",
        "adoption_receipt",
    )
    _closed(request, "$.request", fields)
    if request["schema"] != "autobest-meta-evolution-request/1":
        _refuse(
            "unsupported_schema",
            "$.request.schema",
            "expected autobest-meta-evolution-request/1",
        )
    trigger_by_level = {
        "handshake": ("wild-encounter", "typed-exhaust"),
        "agent-compiler": ("accumulated-handshake-outcomes",),
        "organization-seed-trait": ("proven-agent-compiler-mutation",),
        "protocol-successor": ("aggregated-cross-organization-evidence",),
    }
    target_level = request["target_level"]
    if target_level not in trigger_by_level:
        _refuse("invalid_enum", "$.request.target_level", "unknown evolution rung")
    if request["trigger"] not in trigger_by_level[target_level]:
        _refuse(
            "invalid_trigger",
            "$.request.trigger",
            "trigger does not match target evolution rung",
        )
    predecessor = _sha256(
        request["predecessor_frame_head"],
        "$.request.predecessor_frame_head",
    )
    candidate = _sha256(
        request["candidate_frame_head"],
        "$.request.candidate_frame_head",
    )
    mutation_manifest = _sha256(
        request["mutation_manifest_head"],
        "$.request.mutation_manifest_head",
    )
    if candidate == predecessor:
        _refuse(
            "no_successor_mutation",
            "$.request.candidate_frame_head",
            "evolution requires a distinct immutable successor Frame",
        )
    causal_refs = _bounded_sha_list(
        request["causal_refs"],
        "$.request.causal_refs",
        MAX_EVOLUTION_CASES,
        allow_empty=False,
    )
    for required_ref in (predecessor, mutation_manifest):
        if required_ref not in causal_refs:
            _refuse(
                "missing_provenance",
                "$.request.causal_refs",
                "evolution candidate must retain predecessor and mutation manifest",
            )
    specific_changes = request["specific_changes"]
    if not isinstance(specific_changes, list) or not specific_changes:
        _refuse(
            "list_required",
            "$.request.specific_changes",
            "specific proposed changes are required",
        )
    seen_changes = set()
    for index, change in enumerate(specific_changes):
        change_path = f"$.request.specific_changes[{index}]"
        _closed(change, change_path, ("change_id", "target", "change_head"))
        _identifier(change["change_id"], f"{change_path}.change_id")
        _identifier(change["target"], f"{change_path}.target")
        _sha256(change["change_head"], f"{change_path}.change_head")
        if change["change_id"] in seen_changes:
            _refuse("duplicate_item", f"{change_path}.change_id", "duplicate specific change")
        seen_changes.add(change["change_id"])
    candidate_test_heads = _bounded_sha_list(
        request["candidate_test_heads"],
        "$.request.candidate_test_heads",
        MAX_EVOLUTION_CASES,
        allow_empty=False,
    )
    evidence = _closed(
        request["evidence"],
        "$.request.evidence",
        (
            "scenario_case_heads",
            "hidden_holdout_heads",
            "controlled_mutant_heads",
            "canary_head",
            "independent_test_heads",
            "independent_verification_receipts",
            "rollback_frame_head",
            "source_organization_heads",
        ),
    )
    scenario_heads = _bounded_sha_list(
        evidence["scenario_case_heads"],
        "$.request.evidence.scenario_case_heads",
        MAX_EVOLUTION_CASES,
        allow_empty=False,
    )
    holdout_heads = _bounded_sha_list(
        evidence["hidden_holdout_heads"],
        "$.request.evidence.hidden_holdout_heads",
        MAX_EVOLUTION_CASES,
        allow_empty=False,
    )
    mutant_heads = _bounded_sha_list(
        evidence["controlled_mutant_heads"],
        "$.request.evidence.controlled_mutant_heads",
        MAX_EVOLUTION_CASES,
        allow_empty=False,
    )
    independent_heads = _bounded_sha_list(
        evidence["independent_test_heads"],
        "$.request.evidence.independent_test_heads",
        MAX_EVOLUTION_CASES,
        allow_empty=False,
    )
    _sha256(evidence["canary_head"], "$.request.evidence.canary_head")
    rollback_head = _sha256(
        evidence["rollback_frame_head"],
        "$.request.evidence.rollback_frame_head",
    )
    if rollback_head != predecessor:
        _refuse("rollback_mismatch", "$.request.evidence.rollback_frame_head", "rollback must retain predecessor")
    if set(scenario_heads) & set(holdout_heads):
        _refuse(
            "corpus_contamination",
            "$.request.evidence",
            "scenario corpus and hidden holdouts must be disjoint",
        )
    if set(candidate_test_heads) & (
        set(holdout_heads) | set(independent_heads)
    ):
        _refuse(
            "self_certification",
            "$.request",
            "candidate-generated tests cannot overlap holdouts or independent tests",
        )
    verification_receipts = evidence["independent_verification_receipts"]
    if (
        not isinstance(verification_receipts, list)
        or len(verification_receipts) < 2
    ):
        _refuse(
            "independent_proof_missing",
            "$.request.evidence.independent_verification_receipts",
            "at least two independent verification receipts are required",
        )
    verified_heads = set()
    for index, receipt_value in enumerate(verification_receipts):
        receipt = _validate_receipt(
            receipt_value,
            f"$.request.evidence.independent_verification_receipts[{index}]",
        )
        if receipt["facts_head"] not in independent_heads:
            _refuse(
                "receipt_binding_mismatch",
                f"$.request.evidence.independent_verification_receipts[{index}].facts_head",
                "independent verification receipt does not bind an independent test",
            )
        verified_heads.add(receipt["facts_head"])
    if len(verified_heads) < 2:
        _refuse(
            "echo_amplification",
            "$.request.evidence.independent_verification_receipts",
            "independent receipts must bind distinct evidence",
        )
    source_organizations = _bounded_sha_list(
        evidence["source_organization_heads"],
        "$.request.evidence.source_organization_heads",
        MAX_EVOLUTION_CASES,
        allow_empty=False,
    )
    if target_level == "protocol-successor" and len(source_organizations) < 3:
        _refuse(
            "monoculture",
            "$.request.evidence.source_organization_heads",
            "protocol successor requires at least three organizations",
        )
    metric_fields = (
        "scenario_pass",
        "holdout_pass",
        "mutant_detection",
        "canary_pass",
        "independent_verification",
        "diversity",
        "retention",
    )
    metrics = _closed(
        request["metrics_bps"],
        "$.request.metrics_bps",
        metric_fields,
    )
    thresholds = _closed(
        request["thresholds_bps"],
        "$.request.thresholds_bps",
        metric_fields,
    )
    for field in metric_fields:
        _bp(metrics[field], f"$.request.metrics_bps.{field}")
        _bp(thresholds[field], f"$.request.thresholds_bps.{field}")
    proposal_facts = {
        "target_level": target_level,
        "trigger": request["trigger"],
        "predecessor_frame_head": predecessor,
        "candidate_frame_head": candidate,
        "mutation_manifest_head": mutation_manifest,
        "causal_refs": list(causal_refs),
        "specific_changes": _json_copy(specific_changes),
        "candidate_test_heads": list(candidate_test_heads),
        "scenario_case_heads": list(scenario_heads),
        "hidden_holdout_heads": list(holdout_heads),
        "controlled_mutant_heads": list(mutant_heads),
        "canary_head": evidence["canary_head"],
        "independent_test_heads": list(independent_heads),
        "source_organization_heads": list(source_organizations),
        "metrics_bps": dict(metrics),
        "thresholds_bps": dict(thresholds),
    }
    proposal_head = canonical_digest("meta-evolution-proposal/v1", proposal_facts)
    proposal_receipt = _validate_receipt(
        request["proposal_receipt"],
        "$.request.proposal_receipt",
    )
    if proposal_receipt["facts_head"] != proposal_head:
        _refuse(
            "receipt_binding_mismatch",
            "$.request.proposal_receipt.facts_head",
            "proposal receipt does not bind exact evolution evidence",
        )
    guard_names = (
        "reward-hacking",
        "corpus-contamination",
        "echo-amplification",
        "monoculture",
        "catastrophic-forgetting",
        "automatic-promotion",
    )
    guard_receipts = request["guard_receipts"]
    if not isinstance(guard_receipts, list) or len(guard_receipts) != len(guard_names):
        _refuse(
            "list_required",
            "$.request.guard_receipts",
            "exact anti-gaming guard set required",
        )
    guard_audit = []
    seen_guards = set()
    for index, guard_record in enumerate(guard_receipts):
        guard_path = f"$.request.guard_receipts[{index}]"
        _closed(guard_record, guard_path, ("guard", "cleared", "receipt"))
        guard = guard_record["guard"]
        if guard not in guard_names or guard in seen_guards:
            _refuse("invalid_gate", f"{guard_path}.guard", "unknown or duplicate guard")
        cleared = _boolean(guard_record["cleared"], f"{guard_path}.cleared")
        receipt = _validate_receipt(guard_record["receipt"], f"{guard_path}.receipt")
        facts_head = canonical_digest(
            "meta-evolution-guard/v1",
            {
                "guard": guard,
                "cleared": cleared,
                "proposal_head": proposal_head,
            },
        )
        if receipt["facts_head"] != facts_head:
            _refuse(
                "receipt_binding_mismatch",
                f"{guard_path}.receipt.facts_head",
                "guard receipt does not bind exact evolution proposal",
            )
        seen_guards.add(guard)
        guard_audit.append(
            {
                "guard": guard,
                "cleared": cleared,
                "receipt_head": receipt["head"],
            }
        )
    if request["adoption_receipt"] is not None:
        _refuse(
            "automatic_promotion_forbidden",
            "$.request.adoption_receipt",
            "evaluation cannot carry adoption receipt",
        )
    metric_failures = [
        field for field in metric_fields if metrics[field] < thresholds[field]
    ]
    guard_failures = sorted(
        item["guard"] for item in guard_audit if not item["cleared"]
    )
    eligible = not metric_failures and not guard_failures
    result = _base_plan("meta_evolution")
    result.update(
        {
            "schema": "autobest-meta-evolution-candidate/1",
            "ok": True,
            "target_level": target_level,
            "trigger": request["trigger"],
            "predecessor_frame_head": predecessor,
            "candidate_frame_head": candidate,
            "proposal_head": proposal_head,
            "specific_changes": _json_copy(specific_changes),
            "evidence": {
                "scenario_case_heads": list(scenario_heads),
                "hidden_holdout_heads": list(holdout_heads),
                "controlled_mutant_heads": list(mutant_heads),
                "canary_head": evidence["canary_head"],
                "independent_test_heads": list(independent_heads),
                "source_organization_heads": list(source_organizations),
                "rollback_frame_head": rollback_head,
            },
            "metrics_bps": dict(metrics),
            "thresholds_bps": dict(thresholds),
            "guard_audit": sorted(guard_audit, key=lambda item: item["guard"]),
            "evaluation": {
                "eligible_for_separate_adoption": eligible,
                "metric_failures": metric_failures,
                "guard_failures": guard_failures,
                "automatically_promoted": False,
                "adoption_performed": False,
                "rollback_available": True,
            },
            "next_action": (
                "request-separate-adoption"
                if eligible
                else "retain-predecessor-and-revise"
            ),
            "authority_granted": False,
        }
    )
    return _finalize_plan(result, "meta-evolution-plan/v1")


def _validate_lens_dimension(value, path):
    body_fields = (
        "schema",
        "lens_id",
        "dimension_id",
        "agent_sha256",
        "prompt_head",
        "policy_head",
        "budget",
        "provenance",
    )
    _closed(value, path, body_fields + ("head",))
    if value["schema"] != "autobest-lens-dimension/1":
        _refuse("unsupported_schema", f"{path}.schema", "expected autobest-lens-dimension/1")
    _identifier(value["lens_id"], f"{path}.lens_id")
    _identifier(value["dimension_id"], f"{path}.dimension_id")
    for field in ("agent_sha256", "prompt_head", "policy_head"):
        _sha256(value[field], f"{path}.{field}")
    _resource_vector(value["budget"], f"{path}.budget")
    _validate_provenance(value["provenance"], f"{path}.provenance")
    _verify_head(value, path, "lens_dimension", body_fields)
    return value


def _validate_lens_candidate(value, path, metric_names, ancestor_head, lens):
    body_fields = (
        "schema",
        "candidate_id",
        "lens_id",
        "kind",
        "artifact_head",
        "round",
        "depth",
        "metrics_bps",
        "unknowns",
        "traits",
        "shared_work_head",
        "equivalence_key",
        "budget_used",
        "parent_refs",
        "test_receipt",
        "provenance",
    )
    _closed(value, path, body_fields + ("head",))
    if value["schema"] != "autobest-lens-candidate/1":
        _refuse("unsupported_schema", f"{path}.schema", "expected autobest-lens-candidate/1")
    _identifier(value["candidate_id"], f"{path}.candidate_id")
    if value["lens_id"] != lens["lens_id"]:
        _refuse("binding_mismatch", f"{path}.lens_id", "candidate names wrong Lens")
    if value["kind"] not in ("complete", "trait"):
        _refuse("invalid_enum", f"{path}.kind", "expected complete or trait")
    _sha256(value["artifact_head"], f"{path}.artifact_head")
    _integer(value["round"], f"{path}.round", 0, MAX_CEO_LINEAGE)
    _integer(value["depth"], f"{path}.depth", 0, MAX_CEO_LINEAGE)
    _validate_metric_map(value["metrics_bps"], f"{path}.metrics_bps", metric_names)
    _unique_strings(value["unknowns"], f"{path}.unknowns", maximum=MAX_REFS)
    if not isinstance(value["traits"], list):
        _refuse("list_required", f"{path}.traits", "candidate traits must be a list")
    if value["kind"] == "trait" and not value["traits"]:
        _refuse("list_required", f"{path}.traits", "trait candidate requires traits")
    trait_ids = set()
    for index, trait in enumerate(value["traits"]):
        trait_path = f"{path}.traits[{index}]"
        _closed(
            trait,
            trait_path,
            (
                "trait_id",
                "content_head",
                "dependencies",
                "compatibility_tags",
                "parent_refs",
            ),
        )
        _identifier(trait["trait_id"], f"{trait_path}.trait_id")
        if trait["trait_id"] in trait_ids:
            _refuse("duplicate_item", f"{trait_path}.trait_id", "duplicate trait")
        trait_ids.add(trait["trait_id"])
        _sha256(trait["content_head"], f"{trait_path}.content_head")
        _unique_strings(
            trait["dependencies"],
            f"{trait_path}.dependencies",
            maximum=MAX_REFS,
            identifiers=True,
        )
        _unique_strings(
            trait["compatibility_tags"],
            f"{trait_path}.compatibility_tags",
            maximum=MAX_REFS,
        )
        _sha_list(trait["parent_refs"], f"{trait_path}.parent_refs", allow_empty=False)
    if value["shared_work_head"] is not None:
        _sha256(value["shared_work_head"], f"{path}.shared_work_head")
    _identifier(value["equivalence_key"], f"{path}.equivalence_key")
    budget_used = _resource_vector(value["budget_used"], f"{path}.budget_used")
    if not _resource_leq(budget_used, lens["budget"]):
        _refuse("over_budget", f"{path}.budget_used", "candidate exceeds Lens budget")
    _sha_list(value["parent_refs"], f"{path}.parent_refs", allow_empty=False)
    for parent in (ancestor_head, lens["head"]):
        if parent not in value["parent_refs"]:
            _refuse(
                "missing_provenance",
                f"{path}.parent_refs",
                "candidate must retain ancestor and Lens Dimension heads",
            )
    _validate_receipt(value["test_receipt"], f"{path}.test_receipt")
    if value["test_receipt"]["facts_head"] != value["artifact_head"]:
        _refuse(
            "receipt_binding_mismatch",
            f"{path}.test_receipt.facts_head",
            "candidate test receipt does not bind artifact head",
        )
    _validate_provenance(value["provenance"], f"{path}.provenance")
    _verify_head(value, path, "lens_candidate", body_fields)
    return value


def _resource_sum(vectors):
    return {
        field: sum(vector[field] for vector in vectors)
        for field in RESOURCE_FIELDS
    }


def _pareto_front(records):
    front = []
    for candidate in records:
        vector = candidate["pareto_vector"]
        dominated = False
        for other in records:
            if other is candidate:
                continue
            other_vector = other["pareto_vector"]
            if all(
                other_vector[index] >= vector[index]
                for index in range(len(vector))
            ) and any(
                other_vector[index] > vector[index]
                for index in range(len(vector))
            ):
                dominated = True
                break
        if not dominated:
            front.append(candidate)
    return front


def n_lens_search(request):
    """Bounded deterministic N-Lens fanout, recombination, and complete-candidate selection."""

    _prepare_input(request, "$.request")
    fields = (
        "schema",
        "ancestor_frame_head",
        "use_case_head",
        "root_envelope",
        "policy",
        "lenses",
        "candidates",
        "search_state",
    )
    _closed(request, "$.request", fields)
    if request["schema"] != "autobest-n-lens-search-request/1":
        _refuse(
            "unsupported_schema",
            "$.request.schema",
            "expected autobest-n-lens-search-request/1",
        )
    ancestor_head = _sha256(
        request["ancestor_frame_head"],
        "$.request.ancestor_frame_head",
    )
    use_case_head = _sha256(
        request["use_case_head"],
        "$.request.use_case_head",
    )
    root = _validate_root(request["root_envelope"], "$.request.root_envelope")
    policy = _closed(
        request["policy"],
        "$.request.policy",
        (
            "selection_mode",
            "weights_bps",
            "minimums_bps",
            "limits",
        ),
    )
    if policy["selection_mode"] not in (
        "auto",
        "recombine-traits",
        "select-complete",
    ):
        _refuse("invalid_enum", "$.request.policy.selection_mode", "unknown selection mode")
    weights = _weights(policy["weights_bps"], "$.request.policy.weights_bps")
    expected_metrics = {
        "scenario_fit",
        "coverage",
        "holdout",
        "knownness",
        "robustness",
    }
    if set(weights) != expected_metrics:
        _refuse(
            "unknown_field",
            "$.request.policy.weights_bps",
            "N-Lens fitness requires scenario_fit, coverage, holdout, knownness, robustness",
        )
    minimums = _closed(
        policy["minimums_bps"],
        "$.request.policy.minimums_bps",
        ("coverage", "holdout", "knownness"),
    )
    for field in minimums:
        _bp(minimums[field], f"$.request.policy.minimums_bps.{field}")
    limit_fields = (
        "max_lenses",
        "max_candidates",
        "max_combinations",
        "max_cross_size",
        "max_depth",
        "max_rounds",
        "beam_width",
        "pareto_width",
        "no_progress_rounds",
    )
    limits = _closed(
        policy["limits"],
        "$.request.policy.limits",
        limit_fields,
    )
    _integer(limits["max_lenses"], "$.request.policy.limits.max_lenses", 1, MAX_LENSES)
    _integer(
        limits["max_candidates"],
        "$.request.policy.limits.max_candidates",
        1,
        MAX_LENS_CANDIDATES,
    )
    _integer(
        limits["max_combinations"],
        "$.request.policy.limits.max_combinations",
        0,
        MAX_LENS_CANDIDATES,
    )
    _integer(limits["max_cross_size"], "$.request.policy.limits.max_cross_size", 1, 8)
    _integer(limits["max_depth"], "$.request.policy.limits.max_depth", 0, MAX_CEO_LINEAGE)
    _integer(limits["max_rounds"], "$.request.policy.limits.max_rounds", 1, MAX_CEO_LINEAGE)
    _integer(limits["beam_width"], "$.request.policy.limits.beam_width", 1, 16)
    _integer(limits["pareto_width"], "$.request.policy.limits.pareto_width", 1, 16)
    _integer(
        limits["no_progress_rounds"],
        "$.request.policy.limits.no_progress_rounds",
        1,
        MAX_CEO_LINEAGE,
    )
    state = _closed(
        request["search_state"],
        "$.request.search_state",
        ("round", "previous_best_fitness_bps", "no_progress_count"),
    )
    current_round = _integer(
        state["round"],
        "$.request.search_state.round",
        0,
        MAX_CEO_LINEAGE,
    )
    if current_round >= limits["max_rounds"]:
        _refuse("round_limit", "$.request.search_state.round", "search round limit reached")
    if state["previous_best_fitness_bps"] is not None:
        _bp(
            state["previous_best_fitness_bps"],
            "$.request.search_state.previous_best_fitness_bps",
        )
    no_progress_count = _integer(
        state["no_progress_count"],
        "$.request.search_state.no_progress_count",
        0,
        MAX_CEO_LINEAGE,
    )
    lenses = request["lenses"]
    if not isinstance(lenses, list) or not lenses or len(lenses) > limits["max_lenses"]:
        _refuse("too_many_items", "$.request.lenses", "Lens count exceeds explicit bound")
    lens_by_id = {}
    dimensions = set()
    for index, lens in enumerate(lenses):
        _validate_lens_dimension(lens, f"$.request.lenses[{index}]")
        if lens["lens_id"] in lens_by_id or lens["dimension_id"] in dimensions:
            _refuse("duplicate_item", f"$.request.lenses[{index}]", "Lens ids and Dimensions must be unique")
        lens_by_id[lens["lens_id"]] = lens
        dimensions.add(lens["dimension_id"])
    lens_budget_sum = _resource_sum([lens["budget"] for lens in lenses])
    if not _resource_leq(lens_budget_sum, root["limits"]):
        _refuse("over_budget", "$.request.lenses", "Lens fanout exceeds immutable root budget")
    candidates = request["candidates"]
    if (
        not isinstance(candidates, list)
        or not candidates
        or len(candidates) > limits["max_candidates"]
    ):
        _refuse("too_many_items", "$.request.candidates", "candidate count exceeds explicit bound")
    seen_candidate_ids = set()
    candidate_records = []
    branch_audit = []
    for index, candidate in enumerate(candidates):
        lens = lens_by_id.get(candidate.get("lens_id") if isinstance(candidate, dict) else None)
        if lens is None:
            _refuse("binding_mismatch", f"$.request.candidates[{index}].lens_id", "candidate Lens unknown")
        _validate_lens_candidate(
            candidate,
            f"$.request.candidates[{index}]",
            weights,
            ancestor_head,
            lens,
        )
        if candidate["candidate_id"] in seen_candidate_ids:
            _refuse("duplicate_item", f"$.request.candidates[{index}].candidate_id", "duplicate candidate")
        seen_candidate_ids.add(candidate["candidate_id"])
        if candidate["round"] > current_round or candidate["depth"] > limits["max_depth"]:
            branch_audit.append(
                {
                    "candidate_id": candidate["candidate_id"],
                    "candidate_head": candidate["head"],
                    "status": "pruned",
                    "reason": "round-or-depth-limit",
                }
            )
            continue
        fitness, score_vector = _score(candidate["metrics_bps"], weights)
        hard_failures = [
            field
            for field in ("coverage", "holdout", "knownness")
            if candidate["metrics_bps"][field] < minimums[field]
        ]
        record = {
            "candidate": candidate,
            "fitness_bps": fitness,
            "score_vector": score_vector,
            "hard_failures": hard_failures,
        }
        if hard_failures:
            branch_audit.append(
                {
                    "candidate_id": candidate["candidate_id"],
                    "candidate_head": candidate["head"],
                    "status": "pruned",
                    "reason": "minimums:" + ",".join(hard_failures),
                }
            )
        else:
            candidate_records.append(record)
    if not candidate_records:
        result = _base_plan("n_lens_search")
        result.update(
            {
                "schema": "autobest-n-lens-search-candidate/1",
                "ok": False,
                "ancestor_frame_head": ancestor_head,
                "use_case_head": use_case_head,
                "decision": {"mode": "stop", "reason": "no eligible candidates"},
                "branch_audit": branch_audit,
                "universal_fitness_claimed": False,
            }
        )
        return _finalize_plan(result, "n-lens-search-plan/v1")
    deduped = {}
    for record in candidate_records:
        key = record["candidate"]["equivalence_key"]
        current = deduped.get(key)
        if current is None or (
            record["fitness_bps"],
            record["candidate"]["head"],
        ) > (
            current["fitness_bps"],
            current["candidate"]["head"],
        ):
            if current is not None:
                branch_audit.append(
                    {
                        "candidate_id": current["candidate"]["candidate_id"],
                        "candidate_head": current["candidate"]["head"],
                        "status": "deduped",
                        "reason": f"equivalent-to:{record['candidate']['candidate_id']}",
                    }
                )
            deduped[key] = record
        else:
            branch_audit.append(
                {
                    "candidate_id": record["candidate"]["candidate_id"],
                    "candidate_head": record["candidate"]["head"],
                    "status": "deduped",
                    "reason": f"equivalent-to:{current['candidate']['candidate_id']}",
                }
            )
    eligible_records = sorted(
        deduped.values(),
        key=lambda item: (-item["fitness_bps"], item["candidate"]["head"]),
    )
    for record in eligible_records:
        branch_audit.append(
            {
                "candidate_id": record["candidate"]["candidate_id"],
                "candidate_head": record["candidate"]["head"],
                "status": "eligible",
                "reason": "hard-gates-passed",
            }
        )
    trait_beam = [
        record
        for record in eligible_records
        if record["candidate"]["kind"] == "trait"
    ][: limits["beam_width"]]
    combinations = []
    combination_audit = []
    generated_count = 0
    for size in range(2, min(limits["max_cross_size"], len(trait_beam)) + 1):
        for members in itertools.combinations(trait_beam, size):
            if generated_count >= limits["max_combinations"]:
                break
            generated_count += 1
            traits_by_id = {}
            tag_values = {}
            conflicts = []
            for member in members:
                for trait in member["candidate"]["traits"]:
                    existing = traits_by_id.get(trait["trait_id"])
                    if existing and existing["content_head"] != trait["content_head"]:
                        conflicts.append("trait-content:" + trait["trait_id"])
                    else:
                        traits_by_id[trait["trait_id"]] = trait
                    for tag in trait["compatibility_tags"]:
                        key, separator, value = tag.partition("=")
                        if not separator:
                            key, value = tag, "present"
                        if key in tag_values and tag_values[key] != value:
                            conflicts.append("tag:" + key)
                        tag_values[key] = value
            dependencies = {
                dependency
                for trait in traits_by_id.values()
                for dependency in trait["dependencies"]
            }
            missing_dependencies = sorted(dependencies - set(traits_by_id))
            if conflicts or missing_dependencies:
                combination_audit.append(
                    {
                        "member_candidate_ids": [
                            member["candidate"]["candidate_id"] for member in members
                        ],
                        "status": "pruned",
                        "reason": {
                            "compatibility_conflicts": sorted(set(conflicts)),
                            "missing_dependencies": missing_dependencies,
                        },
                    }
                )
                continue
            shared_seen = set()
            cost_vectors = []
            for member in members:
                shared_head = member["candidate"]["shared_work_head"]
                if shared_head is not None and shared_head in shared_seen:
                    continue
                if shared_head is not None:
                    shared_seen.add(shared_head)
                cost_vectors.append(member["candidate"]["budget_used"])
            combined_cost = _resource_sum(cost_vectors)
            if not _resource_leq(combined_cost, root["limits"]):
                combination_audit.append(
                    {
                        "member_candidate_ids": [
                            member["candidate"]["candidate_id"] for member in members
                        ],
                        "status": "pruned",
                        "reason": {"budget": "root-exceeded"},
                    }
                )
                continue
            combined_metrics = {
                metric: min(
                    member["candidate"]["metrics_bps"][metric]
                    for member in members
                )
                for metric in weights
            }
            combined_fitness, score_vector = _score(combined_metrics, weights)
            member_heads = sorted(member["candidate"]["head"] for member in members)
            combined_unknowns = sorted(
                {
                    unknown
                    for member in members
                    for unknown in member["candidate"]["unknowns"]
                }
            )
            traits = [
                _json_copy(traits_by_id[key])
                for key in sorted(traits_by_id)
            ]
            combo_body = {
                "kind": "trait-recombination",
                "ancestor_frame_head": ancestor_head,
                "use_case_head": use_case_head,
                "member_candidate_heads": member_heads,
                "traits": traits,
                "metrics_bps": combined_metrics,
                "unknowns": combined_unknowns,
                "fitness_bps": combined_fitness,
                "budget_used": combined_cost,
                "shared_work_heads_reused": sorted(shared_seen),
            }
            combination_head = canonical_digest(
                "n-lens-trait-combination/v1",
                combo_body,
            )
            combinations.append(
                {
                    **combo_body,
                    "head": combination_head,
                    "score_vector": score_vector,
                    "pareto_vector": [
                        combined_fitness,
                        combined_metrics["coverage"],
                        combined_metrics["holdout"],
                        combined_metrics["knownness"],
                        MAX_RESOURCE - min(
                            combined_cost["credits_milli"],
                            MAX_RESOURCE,
                        ),
                    ],
                }
            )
            combination_audit.append(
                {
                    "member_candidate_ids": [
                        member["candidate"]["candidate_id"] for member in members
                    ],
                    "status": "eligible",
                    "combination_head": combination_head,
                }
            )
        if generated_count >= limits["max_combinations"]:
            break
    complete_records = []
    for record in eligible_records:
        candidate = record["candidate"]
        if candidate["kind"] != "complete":
            continue
        metrics = candidate["metrics_bps"]
        complete_records.append(
            {
                "kind": "complete",
                "head": candidate["head"],
                "candidate_id": candidate["candidate_id"],
                "lens_id": candidate["lens_id"],
                "artifact_head": candidate["artifact_head"],
                "parent_refs": list(candidate["parent_refs"]),
                "metrics_bps": dict(metrics),
                "unknowns": list(candidate["unknowns"]),
                "fitness_bps": record["fitness_bps"],
                "score_vector": record["score_vector"],
                "budget_used": dict(candidate["budget_used"]),
                "pareto_vector": [
                    record["fitness_bps"],
                    metrics["coverage"],
                    metrics["holdout"],
                    metrics["knownness"],
                    MAX_RESOURCE
                    - min(candidate["budget_used"]["credits_milli"], MAX_RESOURCE),
                ],
            }
        )
    search_pool = []
    if policy["selection_mode"] in ("auto", "select-complete"):
        search_pool.extend(complete_records)
    if policy["selection_mode"] in ("auto", "recombine-traits"):
        search_pool.extend(combinations)
    if not search_pool:
        decision_mode = "stop"
        selected = None
        best_fitness = 0
        stop_reason = "no candidate in declared selection mode"
        pareto = []
    else:
        pareto = sorted(
            _pareto_front(search_pool),
            key=lambda item: (-item["fitness_bps"], item["head"]),
        )[: limits["pareto_width"]]
        beam = sorted(
            search_pool,
            key=lambda item: (-item["fitness_bps"], item["head"]),
        )[: limits["beam_width"]]
        bounded_heads = {item["head"] for item in pareto}
        bounded = [item for item in beam if item["head"] in bounded_heads] or pareto
        selected = sorted(
            bounded,
            key=lambda item: (-item["fitness_bps"], item["head"]),
        )[0]
        best_fitness = selected["fitness_bps"]
        decision_mode = (
            "recombine-traits"
            if selected["kind"] == "trait-recombination"
            else "select-complete"
        )
        stop_reason = None
    if state["previous_best_fitness_bps"] is not None and (
        best_fitness <= state["previous_best_fitness_bps"]
    ):
        next_no_progress = no_progress_count + 1
    else:
        next_no_progress = 0
    stop_for_no_progress = next_no_progress >= limits["no_progress_rounds"]
    if stop_for_no_progress:
        decision_mode = "stop"
        stop_reason = "no-progress-limit"
    result = _base_plan("n_lens_search")
    result.update(
        {
            "schema": "autobest-n-lens-search-candidate/1",
            "ok": selected is not None and not stop_for_no_progress,
            "ancestor_frame_head": ancestor_head,
            "use_case_head": use_case_head,
            "lens_heads": sorted(lens["head"] for lens in lenses),
            "branch_audit": sorted(
                branch_audit,
                key=lambda item: (item["candidate_id"], item["candidate_head"]),
            ),
            "combination_audit": combination_audit,
            "equivalence_classes": {
                key: record["candidate"]["head"]
                for key, record in sorted(deduped.items())
            },
            "pareto_front": [
                {
                    "head": item["head"],
                    "kind": item["kind"],
                    "fitness_bps": item["fitness_bps"],
                    "metrics_bps": item["metrics_bps"],
                    "unknowns": item["unknowns"],
                }
                for item in pareto
            ],
            "decision": {
                "mode": decision_mode,
                "selected": None if stop_for_no_progress else selected,
                "reason": stop_reason,
            },
            "bounds": {
                "limits": dict(limits),
                "root_limits": dict(root["limits"]),
                "generated_combinations": generated_count,
                "eligible_combinations": len(combinations),
                "shared_work_reuse_applied": True,
            },
            "next_search_state": {
                "round": current_round + 1,
                "previous_best_fitness_bps": best_fitness,
                "no_progress_count": next_no_progress,
            },
            "all_parent_branches_preserved": True,
            "trait_provenance_preserved": True,
            "fitness_scope": {
                "scenario_relative": True,
                "use_case_head": use_case_head,
                "coverage_explicit": True,
                "holdouts_explicit": True,
                "unknowns_explicit": True,
                "universal_truth_claimed": False,
            },
            "authority_granted": False,
        }
    )
    return _finalize_plan(result, "n-lens-search-plan/v1")


def translate_hive(request):
    """Project a bounded repository snapshot into an inert fallback Hive candidate."""

    _prepare_input(request, "$.request")
    fields = (
        "schema",
        "implementation_sha256",
        "agent_receipt",
        "snapshot",
        "adapter_resolution",
        "translation_policy",
        "policy_receipt",
        "prompt_head",
        "prompt_receipt",
        "model_head",
        "model_receipt",
    )
    _closed(request, "$.request", fields)
    if request["schema"] != "autobest-hive-translation-request/1":
        _refuse(
            "unsupported_schema",
            "$.request.schema",
            "expected autobest-hive-translation-request/1",
        )
    implementation_sha = _sha256(
        request["implementation_sha256"],
        "$.request.implementation_sha256",
    )
    agent_receipt = _validate_receipt(
        request["agent_receipt"],
        "$.request.agent_receipt",
    )
    if agent_receipt["facts_head"] != implementation_sha:
        _refuse(
            "receipt_binding_mismatch",
            "$.request.agent_receipt.facts_head",
            "agent receipt does not bind the externally computed exact implementation SHA",
        )
    snapshot = _validate_repository_snapshot(request["snapshot"], "$.request.snapshot")
    adapter = _validate_adapter_resolution(
        request["adapter_resolution"],
        "$.request.adapter_resolution",
    )
    if any(adapter[field] != "unavailable" for field in ("native", "declared", "inferred")):
        _refuse(
            "adapter_fallback_not_applicable",
            "$.request.adapter_resolution",
            "fallback Hive translation is permitted only when native, declared, and inferred adapters are unavailable",
        )
    policy = _validate_hive_translation_policy(
        request["translation_policy"],
        "$.request.translation_policy",
    )
    policy_receipt = _validate_receipt(
        request["policy_receipt"],
        "$.request.policy_receipt",
    )
    if policy_receipt["facts_head"] != policy["head"]:
        _refuse(
            "receipt_binding_mismatch",
            "$.request.policy_receipt.facts_head",
            "policy receipt does not bind the exact translation policy",
        )
    prompt_head = _sha256(request["prompt_head"], "$.request.prompt_head")
    prompt_receipt = _validate_receipt(
        request["prompt_receipt"],
        "$.request.prompt_receipt",
    )
    if prompt_receipt["facts_head"] != prompt_head:
        _refuse(
            "receipt_binding_mismatch",
            "$.request.prompt_receipt.facts_head",
            "prompt receipt does not bind the exact prompt head",
        )
    model_head = _sha256(request["model_head"], "$.request.model_head")
    model_receipt = _validate_receipt(
        request["model_receipt"],
        "$.request.model_receipt",
    )
    if model_receipt["facts_head"] != model_head:
        _refuse(
            "receipt_binding_mismatch",
            "$.request.model_receipt.facts_head",
            "model receipt does not bind the exact model/output head",
        )

    inventory = sorted(snapshot["inventory"], key=lambda item: item["path"])
    total_bytes = sum(entry["bytes"] for entry in inventory)
    if len(inventory) > policy["max_files"]:
        _refuse(
            "policy_limit_exceeded",
            "$.request.snapshot.inventory",
            "source inventory exceeds translation policy file cap",
        )
    if total_bytes > policy["max_total_bytes"]:
        _refuse(
            "policy_limit_exceeded",
            "$.request.snapshot.inventory",
            "source inventory exceeds translation policy byte cap",
        )

    dimensions = []
    vector = []
    unknowns = []
    for entry in inventory:
        dimension_digest = canonical_digest(
            "hive-source-dimension/v1",
            {
                "snapshot_head": snapshot["head"],
                "path": entry["path"],
                "sha256": entry["sha256"],
            },
        )
        dimension_id = "dimension:" + dimension_digest[:32]
        dimensions.append(
            {
                "dimension_id": dimension_id,
                "kind": "repository-source-data",
                "source_path": entry["path"],
                "source_sha256": entry["sha256"],
                "source_bytes": entry["bytes"],
                "content": _json_copy(entry["content"]),
                "interpretation": "opaque-preserved-data",
                "adapter": None,
                "parent_refs": [snapshot["head"], entry["sha256"]],
            }
        )
        vector.append(
            {
                "dimension_id": dimension_id,
                "source_path": entry["path"],
                "source_sha256": entry["sha256"],
            }
        )
        unknowns.append(
            {
                "dimension_id": dimension_id,
                "source_path": entry["path"],
                "reason": "native, declared, and inferred adapters unavailable; semantics intentionally unresolved",
            }
        )
    hive_body = {
        "schema": "autobest-hive-translation/1",
        "hive_id": "hive:" + canonical_digest(
            "hive-translation-id/v1",
            {
                "snapshot_head": snapshot["head"],
                "policy_head": policy["head"],
                "adapter_head": adapter["head"],
            },
        )[:32],
        "source_snapshot_head": snapshot["head"],
        "source_inventory_head": snapshot["inventory_head"],
        "dimension_mode": policy["dimension_mode"],
        "dimensions": dimensions,
        "vector": vector,
        "unknowns": unknowns,
        "conflicts": [],
        "activated": False,
        "registered": False,
        "authority_granted": False,
    }
    hive = dict(hive_body)
    hive["head"] = canonical_digest("hive-translation/v1", hive_body)
    result = _base_plan("translate_hive")
    result.update(
        {
            "schema": "autobest-hive-translation-candidate/1",
            "ok": True,
            "bindings": {
                "implementation_sha256": implementation_sha,
                "agent_receipt_head": agent_receipt["head"],
                "snapshot_head": snapshot["head"],
                "scope_head": snapshot["scope_head"],
                "inventory_head": snapshot["inventory_head"],
                "adapter_resolution_head": adapter["head"],
                "translation_policy_head": policy["head"],
                "policy_receipt_head": policy_receipt["head"],
                "prompt_head": prompt_head,
                "prompt_receipt_head": prompt_receipt["head"],
                "model_head": model_head,
                "model_receipt_head": model_receipt["head"],
            },
            "source_inventory": _repository_inventory_material(inventory),
            "translation": hive,
            "activation_requirements": {
                "deterministic_host_validation_required": True,
                "checks": [
                    "recompute exact implementation SHA-256 binding",
                    "recompute every source content SHA-256 and inventory head",
                    "verify scope, capture, adapter, policy, prompt, and model receipts",
                    "verify RAPP/1 envelope, hash, signature, stream, ancestry, registration, and refusal compatibility",
                    "register and activate only under separate host authority",
                ],
                "activation_performed": False,
                "registration_performed": False,
                "model_receipt_grants_authority": False,
                "repository_presence_grants_authority": False,
            },
            "lineage": _lineage(
                [
                    snapshot,
                    snapshot["scope_receipt"],
                    snapshot["capture_receipt"],
                    adapter,
                    adapter["receipt"],
                    policy,
                    agent_receipt,
                    policy_receipt,
                    prompt_receipt,
                    model_receipt,
                ]
            ),
        }
    )
    return _finalize_plan(result, "hive-translation-plan/v1")


def _json_copy(value):
    return json.loads(
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    )


def _ceo_dimension_map(organization):
    return {dimension["dimension_id"]: dimension for dimension in organization["dimensions"]}


def _ceo_missing_actions(grant, *actions):
    allowed = set(grant["allowed_actions"])
    return [action for action in actions if action not in allowed]


def _ceo_mission_id(command, organization, grant):
    digest = canonical_digest(
        "ceo-mission-id/v1",
        {
            "command_head": command["head"],
            "organization_head": organization["head"],
            "grant_head": grant["head"],
        },
    )
    return "mission:" + digest[:32]


def _ceo_initial_state(command, organization, grant, root, policy):
    ceiling = _resource_minimum(root["limits"], grant["limits"])
    body = {
        "schema": "microsol-ceo-state/2",
        "profile": "microsol-ceo",
        "mission_id": _ceo_mission_id(command, organization, grant),
        "sequence": 0,
        "phase": "mission_acceptance",
        "status": "active",
        "bindings": {
            "command_head": command["head"],
            "organization_head": organization["head"],
            "grant_head": grant["head"],
            "root_envelope_head": root["head"],
            "policy_head": policy["head"],
        },
        "mission": {
            "accepted": False,
            "acceptance_criteria": [],
            "task": None,
        },
        "active_task": None,
        "selected_dimensions": [],
        "budget": {
            "root_limits": dict(root["limits"]),
            "grant_limits": dict(grant["limits"]),
            "remaining": ceiling,
            "latest_reservation": _zero_resources(),
        },
        "artifacts": {
            "delegate_plan_heads": [],
            "checkpoint_heads": [],
            "difference_task_heads": [],
            "candidate_heads": [],
            "cross_plan_head": None,
            "verification_event_heads": [],
            "handoff_head": None,
        },
        "accepted_evidence_heads": [],
        "control": {
            "mode": "autonomous",
            "active": False,
            "takeover_id": None,
            "return_phase": None,
            "anchor": None,
            "affected_dimensions": [],
            "paused_dimensions": [],
            "unaffected_dimensions": [],
            "directive": None,
            "successor_task": None,
            "successor_plan_head": None,
            "preserved_evidence_heads": [],
            "history": [],
        },
        "verification": None,
        "decision": None,
        "lineage": {
            "state_heads": [],
            "event_heads": [],
            "plan_heads": [],
        },
        "provenance": {
            "source_id": "microsol-autobest:ceo-reducer",
            "source_head": command["head"],
            "parent_refs": [
                command["head"],
                organization["head"],
                grant["head"],
                root["head"],
                policy["head"],
            ],
        },
    }
    state = head_record("ceo_state", body)
    return _validate_ceo_state(state, "$.generated_state")


def _ceo_advance_state(
    state,
    event,
    *,
    phase=None,
    status=None,
    mission=None,
    active_task=None,
    selected_dimensions=None,
    budget=None,
    artifacts=None,
    accepted_evidence_heads=None,
    control=None,
    verification=None,
    decision=None,
    clear_verification=False,
    clear_decision=False,
    plan_heads=(),
):
    body = {
        key: _json_copy(value)
        for key, value in state.items()
        if key != "head"
    }
    body["sequence"] = state["sequence"] + 1
    if body["sequence"] > MAX_CEO_LINEAGE:
        _refuse("lifecycle_limit", "$.request.state.sequence", "CEO lifecycle sequence limit reached")
    if phase is not None:
        body["phase"] = phase
    if status is not None:
        body["status"] = status
    if mission is not None:
        body["mission"] = _json_copy(mission)
    if active_task is not None:
        body["active_task"] = _json_copy(active_task)
    if selected_dimensions is not None:
        body["selected_dimensions"] = list(selected_dimensions)
    if budget is not None:
        body["budget"] = _json_copy(budget)
    if artifacts is not None:
        body["artifacts"] = _json_copy(artifacts)
    if accepted_evidence_heads is not None:
        body["accepted_evidence_heads"] = list(accepted_evidence_heads)
    if control is not None:
        body["control"] = _json_copy(control)
    if clear_verification:
        body["verification"] = None
    if clear_decision:
        body["decision"] = None
    if verification is not None:
        body["verification"] = _json_copy(verification)
    if decision is not None:
        body["decision"] = _json_copy(decision)
    lineage = body["lineage"]
    lineage["state_heads"].append(state["head"])
    lineage["event_heads"].append(event["head"])
    for plan_head in plan_heads:
        if plan_head not in lineage["plan_heads"]:
            lineage["plan_heads"].append(plan_head)
    body["provenance"] = {
        "source_id": "microsol-autobest:ceo-reducer",
        "source_head": state["head"],
        "parent_refs": [state["head"], event["head"]],
    }
    next_state = head_record("ceo_state", body)
    return _validate_ceo_state(next_state, "$.generated_state")


def _ceo_action(state, grant, root, action_type, required_event_type, request_data):
    return {
        "schema": "microsol-ceo-next-action/1",
        "type": action_type,
        "required_event_type": required_event_type,
        "state_head": state["head"],
        "grant_head": grant["head"],
        "root_envelope_head": root["head"],
        "budget_ceiling": dict(state["budget"]["remaining"]),
        "request": request_data,
        "host_executes": True,
        "authority_granted": False,
    }


def _ceo_result(state, next_action, transition, *, emitted_delegate=None, emitted_cross=None):
    result = _base_plan("ceo")
    result.update(
        {
            "schema": "microsol-ceo-candidate/1",
            "profile": "microsol-ceo",
            "ok": state["status"] != "refused"
            and (state["decision"] is None or state["decision"]["kind"] != "refuse"),
            "state": state,
            "transition": transition,
            "next_action": next_action,
            "emitted_plans": {
                "delegate": emitted_delegate,
                "cross": emitted_cross,
            },
            "decision": state["decision"],
            "goal_data_only": True,
            "adoption_performed": False,
            "effects_performed": False,
            "grant_head_unchanged": state["bindings"]["grant_head"],
            "root_envelope_head_unchanged": state["bindings"]["root_envelope_head"],
            "policy_head_unchanged": state["bindings"]["policy_head"],
            "lineage": {
                "state_head": state["head"],
                "state_heads": list(state["lineage"]["state_heads"]),
                "event_heads": list(state["lineage"]["event_heads"]),
                "plan_heads": list(state["lineage"]["plan_heads"]),
            },
        }
    )
    return _finalize_plan(result, "ceo-plan/v1")


def _ceo_handoff_action(state, grant, root):
    kind = "verified_ready" if state["status"] == "verified_ready" else "refusal"
    return _ceo_action(
        state,
        grant,
        root,
        "handoff_" + kind,
        "handoff_closed",
        {
            "mission_id": state["mission_id"],
            "handoff_kind": kind,
            "decision": _json_copy(state["decision"]),
            "artifacts": _json_copy(state["artifacts"]),
            "close_requires_separate_receipt": True,
        },
    )


def _ceo_semantic_refusal(
    state,
    event,
    grant,
    root,
    code,
    detail,
    *,
    artifacts=None,
    budget=None,
    accepted_evidence_heads=None,
    control=None,
    verification=None,
    plan_heads=(),
    emitted_delegate=None,
    emitted_cross=None,
):
    if control is None and state["control"]["active"]:
        history = _json_copy(state["control"]["history"])
        history[-1]["outcome"] = "refused"
        control = {
            "mode": "autonomous",
            "active": False,
            "takeover_id": None,
            "return_phase": None,
            "anchor": None,
            "affected_dimensions": [],
            "paused_dimensions": [],
            "unaffected_dimensions": [],
            "directive": None,
            "successor_task": None,
            "successor_plan_head": None,
            "preserved_evidence_heads": list(state["accepted_evidence_heads"]),
            "history": history,
        }
    decision = {
        "kind": "refuse",
        "reason": f"{code}: {detail}",
        "event_head": event["head"],
    }
    next_state = _ceo_advance_state(
        state,
        event,
        phase="handoff",
        status="refused",
        budget=budget,
        artifacts=artifacts,
        accepted_evidence_heads=accepted_evidence_heads,
        control=control,
        verification=verification,
        decision=decision,
        plan_heads=plan_heads,
    )
    next_action = None
    if not _ceo_missing_actions(grant, "handoff", "close"):
        next_action = _ceo_handoff_action(next_state, grant, root)
    return _ceo_result(
        next_state,
        next_action,
        {
            "from": state["phase"],
            "to": "handoff",
            "event_head": event["head"],
            "code": code,
            "reason": detail,
        },
        emitted_delegate=emitted_delegate,
        emitted_cross=emitted_cross,
    )


def _ceo_require_actions(state, event, grant, root, *actions):
    missing = _ceo_missing_actions(grant, *actions)
    if not missing:
        return None
    return _ceo_semantic_refusal(
        state,
        event,
        grant,
        root,
        "grant_action_missing",
        "grant does not permit: " + ", ".join(missing),
    )


def _ceo_mission_task(state, command, event, criteria):
    return head_record(
        "task",
        {
            "schema": "autobest-task/1",
            "task_id": state["mission_id"],
            "payload": {
                "profile": "microsol-ceo",
                "goal_text": command["text"],
                "acceptance_criteria": list(criteria),
            },
            "provenance": {
                "source_id": command["command_id"],
                "source_head": command["head"],
                "parent_refs": [command["head"], event["head"]],
            },
        },
    )


def _ceo_available_verifiers(organization, grant, selected_dimensions):
    allowed = set(grant["allowed_dimensions"])
    selected = set(selected_dimensions)
    return sorted(
        dimension["dimension_id"]
        for dimension in organization["dimensions"]
        if dimension["role"] == "verification"
        and dimension["available"]
        and dimension["dimension_id"] in allowed
        and dimension["dimension_id"] not in selected
    )


def _ceo_check_reservation(reservation, state):
    ceilings = (
        ("immutable root", state["budget"]["root_limits"]),
        ("verified grant", state["budget"]["grant_limits"]),
        ("reported remaining", state["budget"]["remaining"]),
    )
    violations = []
    for label, ceiling in ceilings:
        excess = _resource_excess(reservation["resources"], ceiling)
        if excess:
            violations.append({"ceiling": label, "fields": excess})
    return violations


def _ceo_validate_difference(value, path, selected_dimensions, checkpoint_heads):
    _closed(value, path, ("difference_id", "dimension_id", "task"))
    _identifier(value["difference_id"], f"{path}.difference_id")
    _identifier(value["dimension_id"], f"{path}.dimension_id")
    if value["dimension_id"] not in selected_dimensions:
        _refuse(
            "dimension_not_selected",
            f"{path}.dimension_id",
            "difference work must stay inside a selected static Dimension",
        )
    _validate_task(value["task"], f"{path}.task")
    if not set(value["task"]["provenance"]["parent_refs"]) & set(checkpoint_heads):
        _refuse(
            "missing_checkpoint_binding",
            f"{path}.task.provenance.parent_refs",
            "difference task must retain a checkpoint parent",
        )
    return value


def _ceo_validate_verification_result(value, path):
    _closed(value, path, ("verifier_dimension_id", "passed", "checks", "receipt_head"))
    _identifier(value["verifier_dimension_id"], f"{path}.verifier_dimension_id")
    _boolean(value["passed"], f"{path}.passed")
    _unique_strings(
        value["checks"],
        f"{path}.checks",
        maximum=MAX_CEO_CRITERIA,
        allow_empty=False,
    )
    _sha256(value["receipt_head"], f"{path}.receipt_head")
    return value


def _ceo_expected_event(phase):
    return {
        "mission_acceptance": "mission_accepted",
        "worker_delegation": "worker_observations",
        "checkpoint_observation": "checkpoint_observed",
        "control_checkpoint": "control_checkpoint_observed",
        "difference_parallel": "differences_completed",
        "independent_verification": "verification_completed",
        "decision": "decision_recorded",
        "handoff": "handoff_closed",
    }.get(phase)


def _ceo_control_task(state, command, event, mode, anchor, directive, criteria):
    takeover_digest = canonical_digest(
        "ceo-takeover-id/v1",
        {
            "state_head": state["head"],
            "command_head": command["head"],
            "frame_head": anchor["frame_head"],
            "locus": anchor["locus"],
        },
    )
    takeover_id = "takeover:" + takeover_digest[:32]
    parent_refs = [
        state["active_task"]["head"],
        anchor["frame_head"],
        command["head"],
        event["head"],
    ]
    if state["mission"]["task"]["head"] not in parent_refs:
        parent_refs.append(state["mission"]["task"]["head"])
    for target_ref in directive["target_refs"]:
        if target_ref not in parent_refs:
            parent_refs.append(target_ref)
    task = head_record(
        "task",
        {
            "schema": "autobest-task/1",
            "task_id": "control:" + takeover_digest[:32],
            "payload": {
                "profile": "microsol-ceo-control",
                "takeover_id": takeover_id,
                "mode": mode,
                "goal_text": command["text"],
                "locus": anchor["locus"],
                "directive": _json_copy(directive),
                "acceptance_criteria": list(criteria),
                "parent_mission_id": state["mission_id"],
            },
            "provenance": {
                "source_id": command["command_id"],
                "source_head": command["head"],
                "parent_refs": parent_refs,
            },
        },
    )
    return takeover_id, task


def _ceo_handle_user_control(state, event, command, organization, grant, root, policy):
    control_phases = {
        "checkpoint_observation",
        "difference_parallel",
        "independent_verification",
        "decision",
    }
    if state["phase"] not in control_phases or state["status"] != "active":
        _refuse(
            "control_not_at_checkpoint",
            "$.request.event",
            "user takeover requires an active mission with accepted checkpoint evidence",
        )
    if state["control"]["active"]:
        _refuse("control_already_active", "$.request.state.control", "takeover is already active")
    missing_action = _ceo_require_actions(
        state,
        event,
        grant,
        root,
        "user_control",
        "mutate_slice",
        "delegate",
    )
    if missing_action is not None:
        return missing_action
    fields = (
        "mode",
        "command",
        "anchor",
        "affected_dimensions",
        "directive",
        "acceptance_criteria",
        "successor_reservation",
        "observations",
    )
    _closed(event["data"], "$.request.event.data", fields)
    mode = event["data"]["mode"]
    if mode not in CEO_CONTROL_MODES - {"autonomous"}:
        _refuse(
            "invalid_enum",
            "$.request.event.data.mode",
            "takeover mode must be guided or detail",
        )
    takeover_command = _validate_ceo_command(
        event["data"]["command"], "$.request.event.data.command"
    )
    if takeover_command["head"] not in event["provenance"]["parent_refs"]:
        _refuse(
            "missing_receipt_binding",
            "$.request.event.provenance.parent_refs",
            "user-control event must retain the exact injected command head",
        )
    anchor = _closed(
        event["data"]["anchor"],
        "$.request.event.data.anchor",
        ("mission_id", "state_head", "frame_head", "locus", "parent_task_head"),
    )
    _identifier(anchor["mission_id"], "$.request.event.data.anchor.mission_id")
    for field in ("state_head", "frame_head", "parent_task_head"):
        _sha256(anchor[field], f"$.request.event.data.anchor.{field}")
    _text(anchor["locus"], "$.request.event.data.anchor.locus", max_bytes=256)
    if (
        anchor["mission_id"] != state["mission_id"]
        or anchor["state_head"] != state["head"]
        or anchor["parent_task_head"] != state["active_task"]["head"]
    ):
        _refuse(
            "binding_mismatch",
            "$.request.event.data.anchor",
            "takeover anchor does not bind the exact active mission, state, and parent task",
        )
    if anchor["frame_head"] not in state["accepted_evidence_heads"]:
        _refuse(
            "unverified_control_anchor",
            "$.request.event.data.anchor.frame_head",
            "takeover must anchor to already accepted checkpoint evidence",
        )
    if (
        not state["accepted_evidence_heads"]
        or anchor["frame_head"] != state["accepted_evidence_heads"][-1]
    ):
        _refuse(
            "stale_control_anchor",
            "$.request.event.data.anchor.frame_head",
            "takeover must bind the latest active accepted mission/frame evidence",
        )
    affected = _unique_strings(
        event["data"]["affected_dimensions"],
        "$.request.event.data.affected_dimensions",
        maximum=MAX_SUBJECTS,
        allow_empty=False,
        identifiers=True,
    )
    if not set(affected).issubset(set(state["selected_dimensions"])):
        _refuse(
            "dimension_not_selected",
            "$.request.event.data.affected_dimensions",
            "takeover may pause only already selected static Dimensions",
        )
    directive = _validate_ceo_directive(
        event["data"]["directive"], "$.request.event.data.directive"
    )
    targets = directive["target_refs"]
    if not set(targets).issubset(set(state["accepted_evidence_heads"])):
        _refuse(
            "evidence_rewrite",
            "$.request.event.data.directive.target_refs",
            "compare/keep/select targets must be previously accepted evidence",
        )
    if directive["kind"] == "compare" and len(targets) < 2:
        _refuse(
            "insufficient_targets",
            "$.request.event.data.directive.target_refs",
            "compare requires at least two accepted evidence heads",
        )
    if directive["kind"] in ("keep", "select") and not targets:
        _refuse(
            "insufficient_targets",
            "$.request.event.data.directive.target_refs",
            f"{directive['kind']} requires accepted evidence targets",
        )
    criteria = _unique_strings(
        event["data"]["acceptance_criteria"],
        "$.request.event.data.acceptance_criteria",
        maximum=MAX_CEO_CRITERIA,
        allow_empty=False,
    )
    latest_delegate_plan = state["artifacts"]["delegate_plan_heads"][-1]
    reservation = _validate_reservation(
        event["data"]["successor_reservation"],
        "$.request.event.data.successor_reservation",
    )
    if reservation["predecessor_plan"] != latest_delegate_plan:
        _refuse(
            "binding_mismatch",
            "$.request.event.data.successor_reservation.predecessor_plan",
            "takeover successor slice must bind the latest delegate plan",
        )
    violations = _ceo_check_reservation(reservation, state)
    if violations:
        return _ceo_semantic_refusal(
            state,
            event,
            grant,
            root,
            "budget_exceeded",
            json.dumps(violations, sort_keys=True, separators=(",", ":")),
        )
    takeover_id, successor_task = _ceo_control_task(
        state,
        takeover_command,
        event,
        mode,
        anchor,
        directive,
        criteria,
    )
    delegate_plan = delegate(
        {
            "schema": "autobest-delegate-request/1",
            "task": successor_task,
            "root_envelope": root,
            "reservation": reservation,
            "policy": policy,
            "observations": event["data"]["observations"],
        }
    )
    observed_dimensions = {
        assignment["dimension_id"] for assignment in delegate_plan["assignments"]
    }
    if observed_dimensions != set(affected):
        artifacts = _json_copy(state["artifacts"])
        artifacts["delegate_plan_heads"].append(delegate_plan["plan_head"])
        return _ceo_semantic_refusal(
            state,
            event,
            grant,
            root,
            "dimension_observation_mismatch",
            "takeover observations must exactly cover affected Dimensions",
            artifacts=artifacts,
            plan_heads=(delegate_plan["plan_head"],),
            emitted_delegate=delegate_plan,
        )
    artifacts = _json_copy(state["artifacts"])
    artifacts["delegate_plan_heads"].append(delegate_plan["plan_head"])
    if not delegate_plan["ok"]:
        return _ceo_semantic_refusal(
            state,
            event,
            grant,
            root,
            "control_hard_gate_refusal",
            "takeover successor failed generic Delegation Lens gates or minimums",
            artifacts=artifacts,
            plan_heads=(delegate_plan["plan_head"],),
            emitted_delegate=delegate_plan,
        )
    budget = _json_copy(state["budget"])
    budget["latest_reservation"] = dict(
        delegate_plan["current_reservation"]["effective_resources"]
    )
    unaffected = sorted(set(state["selected_dimensions"]) - set(affected))
    history = _json_copy(state["control"]["history"])
    history.append(
        {
            "takeover_id": takeover_id,
            "mode": mode,
            "command_head": takeover_command["head"],
            "anchor_frame_head": anchor["frame_head"],
            "locus": anchor["locus"],
            "successor_task_head": successor_task["head"],
            "successor_plan_head": delegate_plan["plan_head"],
            "outcome": "active",
        }
    )
    control = {
        "mode": mode,
        "active": True,
        "takeover_id": takeover_id,
        "return_phase": state["phase"],
        "anchor": _json_copy(anchor),
        "affected_dimensions": sorted(affected),
        "paused_dimensions": sorted(affected),
        "unaffected_dimensions": unaffected,
        "directive": _json_copy(directive),
        "successor_task": successor_task,
        "successor_plan_head": delegate_plan["plan_head"],
        "preserved_evidence_heads": list(state["accepted_evidence_heads"]),
        "history": history,
    }
    next_state = _ceo_advance_state(
        state,
        event,
        phase="control_checkpoint",
        active_task=successor_task,
        budget=budget,
        artifacts=artifacts,
        control=control,
        clear_verification=True,
        clear_decision=True,
        plan_heads=(delegate_plan["plan_head"],),
    )
    unaffected_disposition = (
        "continue"
        if state["phase"] in ("checkpoint_observation", "difference_parallel")
        else "preserve"
    )
    next_action = _ceo_action(
        next_state,
        grant,
        root,
        "execute_user_control_successor",
        "control_checkpoint_observed",
        {
            "mode": mode,
            "takeover_id": takeover_id,
            "anchor": _json_copy(anchor),
            "directive": _json_copy(directive),
            "successor_task": successor_task,
            "successor_plan_head": delegate_plan["plan_head"],
            "assignments": _json_copy(delegate_plan["assignments"]),
            "paused_dimensions": sorted(affected),
            "affected_prior_work_disposition": "pause",
            "unaffected_dimensions": unaffected,
            "unaffected_work_disposition": unaffected_disposition,
            "hard_gates_remain_mandatory": True,
            "parent_frames_rewritten": False,
            "successor_requires_new_cross_and_verification": True,
        },
    )
    return _ceo_result(
        next_state,
        next_action,
        {
            "from": state["phase"],
            "to": "control_checkpoint",
            "event_head": event["head"],
            "code": "user_control_takeover",
            "reason": "bounded successor objective assigned only to affected Dimensions",
        },
        emitted_delegate=delegate_plan,
    )


def _ceo_handle_control_checkpoint(state, event, grant, root):
    _closed(
        event["data"],
        "$.request.event.data",
        ("successor_plan_head", "checkpoint_heads", "remaining_budget", "outcome"),
    )
    missing_action = _ceo_require_actions(
        state,
        event,
        grant,
        root,
        "user_control",
        "observe_checkpoint",
    )
    if missing_action is not None:
        return missing_action
    _sha256(
        event["data"]["successor_plan_head"],
        "$.request.event.data.successor_plan_head",
    )
    if event["data"]["successor_plan_head"] != state["control"]["successor_plan_head"]:
        _refuse(
            "binding_mismatch",
            "$.request.event.data.successor_plan_head",
            "control checkpoint does not bind the active successor plan",
        )
    checkpoint_heads = _bounded_sha_list(
        event["data"]["checkpoint_heads"],
        "$.request.event.data.checkpoint_heads",
        MAX_CEO_DIFFERENCES,
        allow_empty=False,
    )
    if set(checkpoint_heads) & set(state["accepted_evidence_heads"]):
        _refuse(
            "duplicate_item",
            "$.request.event.data.checkpoint_heads",
            "control checkpoint evidence was already accepted",
        )
    remaining = _resource_vector(
        event["data"]["remaining_budget"],
        "$.request.event.data.remaining_budget",
    )
    if not _resource_leq(remaining, state["budget"]["remaining"]):
        return _ceo_semantic_refusal(
            state,
            event,
            grant,
            root,
            "budget_increase_refused",
            "control checkpoint remaining budget cannot increase",
        )
    if event["data"]["outcome"] != "return_autonomous":
        _refuse(
            "invalid_enum",
            "$.request.event.data.outcome",
            "current control completion requires return_autonomous",
        )
    artifacts = _json_copy(state["artifacts"])
    artifacts["checkpoint_heads"].extend(checkpoint_heads)
    accepted_evidence = list(state["accepted_evidence_heads"])
    accepted_evidence.extend(checkpoint_heads)
    budget = _json_copy(state["budget"])
    budget["remaining"] = dict(remaining)
    budget["latest_reservation"] = _zero_resources()
    history = _json_copy(state["control"]["history"])
    history[-1]["outcome"] = "returned_autonomous"
    control = {
        "mode": "autonomous",
        "active": False,
        "takeover_id": None,
        "return_phase": None,
        "anchor": None,
        "affected_dimensions": [],
        "paused_dimensions": [],
        "unaffected_dimensions": [],
        "directive": None,
        "successor_task": None,
        "successor_plan_head": None,
        "preserved_evidence_heads": accepted_evidence,
        "history": history,
    }
    prior_phase = state["control"]["return_phase"]
    next_state = _ceo_advance_state(
        state,
        event,
        phase="checkpoint_observation",
        budget=budget,
        artifacts=artifacts,
        accepted_evidence_heads=accepted_evidence,
        control=control,
    )
    next_action = _ceo_action(
        next_state,
        grant,
        root,
        "resume_autonomous_checkpoint_flow",
        "checkpoint_observed",
        {
            "latest_delegate_plan_head": state["control"]["successor_plan_head"],
            "original_mission_task": state["mission"]["task"],
            "active_successor_task": state["active_task"],
            "accepted_evidence_heads": accepted_evidence,
            "completed_takeover_id": state["control"]["takeover_id"],
            "prior_autonomous_phase": prior_phase,
            "control_mode": "autonomous",
            "history_preserved": True,
        },
    )
    return _ceo_result(
        next_state,
        next_action,
        {
            "from": "control_checkpoint",
            "to": "checkpoint_observation",
            "event_head": event["head"],
            "code": "returned_autonomous",
            "reason": "fine-detail successor checkpoint accepted and autonomous flow restored",
        },
    )


def ceo(request):
    """Advance the inert microsol-ceo profile by at most one verified event."""

    _prepare_input(request, "$.request")
    fields = (
        "schema",
        "profile",
        "command",
        "organization",
        "grant_envelope",
        "root_envelope",
        "policy",
        "state",
        "event",
    )
    _closed(request, "$.request", fields)
    if request["schema"] != "microsol-ceo-request/1":
        _refuse("unsupported_schema", "$.request.schema", "expected microsol-ceo-request/1")
    selected_profile = profile_config(request["profile"])
    if selected_profile["name"] != "microsol-ceo":
        _refuse("invalid_profile", "$.request.profile", "expected microsol-ceo")
    command = _validate_ceo_command(request["command"], "$.request.command")
    organization = _validate_ceo_organization(
        request["organization"], "$.request.organization"
    )
    grant = _validate_ceo_grant(request["grant_envelope"], "$.request.grant_envelope")
    root = _validate_root(request["root_envelope"], "$.request.root_envelope")
    policy = _validate_policy(request["policy"], "$.request.policy")
    if grant["organization_id"] != organization["organization_id"]:
        _refuse(
            "binding_mismatch",
            "$.request.grant_envelope.organization_id",
            "grant and organization ids differ",
        )
    dimensions = _ceo_dimension_map(organization)
    unknown_grant_dimensions = sorted(set(grant["allowed_dimensions"]) - set(dimensions))
    if unknown_grant_dimensions:
        _refuse(
            "binding_mismatch",
            "$.request.grant_envelope.allowed_dimensions",
            "grant names unknown Dimensions: " + ", ".join(unknown_grant_dimensions),
        )
    if not _resource_leq(grant["limits"], root["limits"]):
        _refuse(
            "grant_exceeds_root",
            "$.request.grant_envelope.limits",
            "separately verified grant limits cannot exceed the immutable root envelope",
        )
    if grant["max_parallel_dimensions"] > root["max_subjects"]:
        _refuse(
            "grant_exceeds_root",
            "$.request.grant_envelope.max_parallel_dimensions",
            "grant parallelism exceeds immutable root subject limit",
        )

    state = request["state"]
    event = request["event"]
    if state is None:
        if event is not None:
            _refuse("unexpected_event", "$.request.event", "initial command intake requires explicit null event")
        missing = _ceo_missing_actions(grant, "intake")
        if missing:
            _refuse(
                "grant_action_missing",
                "$.request.grant_envelope.allowed_actions",
                "command intake is not permitted by the supplied grant",
            )
        state = _ceo_initial_state(command, organization, grant, root, policy)
        available_workers = sorted(
            dimension["dimension_id"]
            for dimension in organization["dimensions"]
            if dimension["role"] == "worker"
            and dimension["available"]
            and dimension["dimension_id"] in grant["allowed_dimensions"]
        )
        next_action = _ceo_action(
            state,
            grant,
            root,
            "request_mission_acceptance",
            "mission_accepted",
            {
                "command_id": command["command_id"],
                "command_head": command["head"],
                "goal_text": command["text"],
                "goal_is_authority": False,
                "available_static_dimensions": available_workers,
                "max_selected_dimensions": min(
                    grant["max_parallel_dimensions"],
                    root["max_subjects"],
                    policy["delegate"]["max_subjects"],
                ),
                "acceptance_criteria_required": True,
            },
        )
        return _ceo_result(
            state,
            next_action,
            {
                "from": None,
                "to": "mission_acceptance",
                "event_head": None,
                "code": "command_intake",
                "reason": "arbitrary command retained as inert goal data",
            },
        )

    _validate_ceo_state(state, "$.request.state")
    expected_bindings = {
        "command_head": command["head"],
        "organization_head": organization["head"],
        "grant_head": grant["head"],
        "root_envelope_head": root["head"],
        "policy_head": policy["head"],
    }
    if state["bindings"] != expected_bindings:
        _refuse(
            "binding_mismatch",
            "$.request.state.bindings",
            "CEO state does not bind the exact command, organization, grant, root, and policy",
        )
    if state["budget"]["root_limits"] != root["limits"]:
        _refuse("binding_mismatch", "$.request.state.budget.root_limits", "root budget changed")
    if state["budget"]["grant_limits"] != grant["limits"]:
        _refuse("binding_mismatch", "$.request.state.budget.grant_limits", "grant budget changed")
    if not set(state["selected_dimensions"]).issubset(set(grant["allowed_dimensions"])):
        _refuse(
            "grant_widening",
            "$.request.state.selected_dimensions",
            "state contains a Dimension outside the supplied grant",
        )
    if len(state["selected_dimensions"]) > min(
        grant["max_parallel_dimensions"],
        root["max_subjects"],
        policy["delegate"]["max_subjects"],
    ):
        _refuse(
            "grant_widening",
            "$.request.state.selected_dimensions",
            "state exceeds granted parallel Dimension count",
        )
    for dimension_id in state["selected_dimensions"]:
        dimension = dimensions.get(dimension_id)
        if dimension is None or dimension["role"] != "worker" or not dimension["available"]:
            _refuse(
                "invalid_state",
                "$.request.state.selected_dimensions",
                "selected Dimensions must remain available static workers",
            )
    if state["mission"]["accepted"]:
        mission_task = state["mission"]["task"]
        expected_payload = {
            "profile": "microsol-ceo",
            "goal_text": command["text"],
            "acceptance_criteria": list(state["mission"]["acceptance_criteria"]),
        }
        if mission_task["task_id"] != state["mission_id"] or mission_task["payload"] != expected_payload:
            _refuse(
                "binding_mismatch",
                "$.request.state.mission.task",
                "mission task no longer matches the exact command and acceptance criteria",
            )
        if (
            mission_task["provenance"]["source_head"] != command["head"]
            or command["head"] not in mission_task["provenance"]["parent_refs"]
        ):
            _refuse(
                "binding_mismatch",
                "$.request.state.mission.task.provenance",
                "mission task must retain the exact command head",
            )
    if state["phase"] == "closed":
        if event is not None:
            _refuse("unexpected_event", "$.request.event", "closed mission accepts no further events")
        return _ceo_result(
            state,
            None,
            {
                "from": "closed",
                "to": "closed",
                "event_head": None,
                "code": "already_closed",
                "reason": "exact closed state is stable and inert",
            },
        )
    if event is None:
        _refuse("missing_field", "$.request.event", "active CEO state requires the next exact event")
    _validate_ceo_event(event, "$.request.event")
    if event["state_head"] != state["head"]:
        _refuse(
            "binding_mismatch",
            "$.request.event.state_head",
            "event does not bind the exact prior CEO state",
        )
    if event["event_type"] == "user_control":
        return _ceo_handle_user_control(
            state,
            event,
            command,
            organization,
            grant,
            root,
            policy,
        )
    expected_event = _ceo_expected_event(state["phase"])
    if event["event_type"] != expected_event:
        _refuse(
            "unexpected_event",
            "$.request.event.event_type",
            f"phase {state['phase']} requires {expected_event}",
        )

    if state["phase"] == "control_checkpoint":
        return _ceo_handle_control_checkpoint(state, event, grant, root)

    if state["phase"] == "mission_acceptance":
        _closed(
            event["data"],
            "$.request.event.data",
            ("accepted", "acceptance_criteria", "requested_dimensions"),
        )
        accepted = _boolean(event["data"]["accepted"], "$.request.event.data.accepted")
        criteria = _unique_strings(
            event["data"]["acceptance_criteria"],
            "$.request.event.data.acceptance_criteria",
            maximum=MAX_CEO_CRITERIA,
            allow_empty=not accepted,
        )
        requested_dimensions = _unique_strings(
            event["data"]["requested_dimensions"],
            "$.request.event.data.requested_dimensions",
            maximum=MAX_SUBJECTS,
            allow_empty=not accepted,
            identifiers=True,
        )
        missing_action = _ceo_require_actions(
            state,
            event,
            grant,
            root,
            "accept_mission",
            "select_dimensions",
        )
        if missing_action is not None:
            return missing_action
        if not accepted:
            return _ceo_semantic_refusal(
                state,
                event,
                grant,
                root,
                "mission_not_accepted",
                "separately verified mission acceptance receipt declined the goal",
            )
        selection_errors = []
        for dimension_id in requested_dimensions:
            dimension = dimensions.get(dimension_id)
            if dimension is None:
                selection_errors.append(f"{dimension_id}:unknown")
            elif dimension_id not in grant["allowed_dimensions"]:
                selection_errors.append(f"{dimension_id}:not-granted")
            elif not dimension["available"]:
                selection_errors.append(f"{dimension_id}:unavailable")
            elif dimension["role"] != "worker":
                selection_errors.append(f"{dimension_id}:not-worker")
        maximum_selected = min(
            grant["max_parallel_dimensions"],
            root["max_subjects"],
            policy["delegate"]["max_subjects"],
        )
        if len(requested_dimensions) > maximum_selected:
            selection_errors.append("parallel-dimension-cap-exceeded")
        if selection_errors:
            return _ceo_semantic_refusal(
                state,
                event,
                grant,
                root,
                "dimension_selection_refused",
                "; ".join(selection_errors),
            )
        mission_task = _ceo_mission_task(state, command, event, criteria)
        mission = {
            "accepted": True,
            "acceptance_criteria": list(criteria),
            "task": mission_task,
        }
        selected = sorted(requested_dimensions)
        next_state = _ceo_advance_state(
            state,
            event,
            phase="worker_delegation",
            mission=mission,
            active_task=mission_task,
            selected_dimensions=selected,
        )
        next_action = _ceo_action(
            next_state,
            grant,
            root,
            "request_worker_observations",
            "worker_observations",
            {
                "task": mission_task,
                "selected_static_dimensions": selected,
                "required_current_receipts": True,
                "maximum_observations": len(selected),
                "reservation_must_fit": dict(next_state["budget"]["remaining"]),
            },
        )
        return _ceo_result(
            next_state,
            next_action,
            {
                "from": "mission_acceptance",
                "to": "worker_delegation",
                "event_head": event["head"],
                "code": "mission_accepted",
                "reason": "mission accepted and static granted Dimensions selected",
            },
        )

    if state["phase"] == "worker_delegation":
        _closed(event["data"], "$.request.event.data", ("reservation", "observations"))
        missing_action = _ceo_require_actions(state, event, grant, root, "delegate")
        if missing_action is not None:
            return missing_action
        reservation = _validate_reservation(
            event["data"]["reservation"], "$.request.event.data.reservation"
        )
        if reservation["predecessor_plan"] is not None:
            _refuse(
                "unexpected_predecessor",
                "$.request.event.data.reservation.predecessor_plan",
                "initial worker reservation must not claim a predecessor plan",
            )
        violations = _ceo_check_reservation(reservation, state)
        if violations:
            return _ceo_semantic_refusal(
                state,
                event,
                grant,
                root,
                "budget_exceeded",
                json.dumps(violations, sort_keys=True, separators=(",", ":")),
            )
        delegate_request = {
            "schema": "autobest-delegate-request/1",
            "task": state["active_task"],
            "root_envelope": root,
            "reservation": reservation,
            "policy": policy,
            "observations": event["data"]["observations"],
        }
        delegate_plan = delegate(delegate_request)
        artifacts = _json_copy(state["artifacts"])
        artifacts["delegate_plan_heads"].append(delegate_plan["plan_head"])
        observed_dimensions = {
            assignment["dimension_id"] for assignment in delegate_plan["assignments"]
        }
        if observed_dimensions != set(state["selected_dimensions"]):
            return _ceo_semantic_refusal(
                state,
                event,
                grant,
                root,
                "dimension_observation_mismatch",
                "worker observations must exactly cover the selected static Dimensions",
                artifacts=artifacts,
                emitted_delegate=delegate_plan,
                plan_heads=(delegate_plan["plan_head"],),
            )
        if not delegate_plan["ok"]:
            return _ceo_semantic_refusal(
                state,
                event,
                grant,
                root,
                "delegation_refused",
                "no bounded JIT assignment candidate was eligible",
                artifacts=artifacts,
                plan_heads=(delegate_plan["plan_head"],),
                emitted_delegate=delegate_plan,
            )
        budget = _json_copy(state["budget"])
        budget["latest_reservation"] = dict(
            delegate_plan["current_reservation"]["effective_resources"]
        )
        next_state = _ceo_advance_state(
            state,
            event,
            phase="checkpoint_observation",
            budget=budget,
            artifacts=artifacts,
            plan_heads=(delegate_plan["plan_head"],),
        )
        next_action = _ceo_action(
            next_state,
            grant,
            root,
            "execute_bounded_jit_assignments",
            "checkpoint_observed",
            {
                "delegate_plan_head": delegate_plan["plan_head"],
                "assignments": _json_copy(delegate_plan["assignments"]),
                "host_must_emit_and_verify_checkpoints": True,
                "mutation_must_bind_predecessor_plan": True,
            },
        )
        return _ceo_result(
            next_state,
            next_action,
            {
                "from": "worker_delegation",
                "to": "checkpoint_observation",
                "event_head": event["head"],
                "code": "jit_delegation_candidate",
                "reason": "bounded assignments emitted for host execution",
            },
            emitted_delegate=delegate_plan,
        )

    if state["phase"] == "checkpoint_observation":
        checkpoint_fields = (
            "delegate_plan_head",
            "checkpoint_heads",
            "remaining_budget",
            "disposition",
            "next_reservation",
            "observations",
            "differences",
        )
        _closed(event["data"], "$.request.event.data", checkpoint_fields)
        missing_action = _ceo_require_actions(
            state, event, grant, root, "observe_checkpoint"
        )
        if missing_action is not None:
            return missing_action
        latest_plan = state["artifacts"]["delegate_plan_heads"][-1]
        _sha256(event["data"]["delegate_plan_head"], "$.request.event.data.delegate_plan_head")
        if event["data"]["delegate_plan_head"] != latest_plan:
            _refuse(
                "binding_mismatch",
                "$.request.event.data.delegate_plan_head",
                "checkpoint does not bind the latest delegate plan",
            )
        checkpoint_heads = _bounded_sha_list(
            event["data"]["checkpoint_heads"],
            "$.request.event.data.checkpoint_heads",
            MAX_CEO_DIFFERENCES,
            allow_empty=False,
        )
        if set(checkpoint_heads) & set(state["artifacts"]["checkpoint_heads"]):
            _refuse(
                "duplicate_item",
                "$.request.event.data.checkpoint_heads",
                "checkpoint receipt was already incorporated",
            )
        remaining = _resource_vector(
            event["data"]["remaining_budget"], "$.request.event.data.remaining_budget"
        )
        if not _resource_leq(remaining, state["budget"]["remaining"]):
            return _ceo_semantic_refusal(
                state,
                event,
                grant,
                root,
                "budget_increase_refused",
                "checkpoint-reported remaining budget cannot increase",
            )
        if not _resource_leq(remaining, state["budget"]["grant_limits"]):
            return _ceo_semantic_refusal(
                state,
                event,
                grant,
                root,
                "grant_budget_exceeded",
                "checkpoint remaining budget exceeds verified grant",
            )
        disposition = event["data"]["disposition"]
        if disposition not in ("continue", "split", "stop"):
            _refuse(
                "invalid_enum",
                "$.request.event.data.disposition",
                "expected continue, split, or stop",
            )
        artifacts = _json_copy(state["artifacts"])
        artifacts["checkpoint_heads"].extend(checkpoint_heads)
        accepted_evidence = list(state["accepted_evidence_heads"])
        accepted_evidence.extend(checkpoint_heads)
        budget = _json_copy(state["budget"])
        budget["remaining"] = dict(remaining)

        if disposition in ("continue", "split"):
            missing_action = _ceo_require_actions(
                state,
                event,
                grant,
                root,
                "mutate_slice",
                "delegate",
            )
            if missing_action is not None:
                return missing_action
            if event["data"]["differences"]:
                _refuse(
                    "unexpected_field",
                    "$.request.event.data.differences",
                    "difference tasks are accepted only when the shared checkpoint loop stops",
                )
            if event["data"]["next_reservation"] is None:
                _refuse(
                    "missing_field",
                    "$.request.event.data.next_reservation",
                    "continue/split requires an explicit successor reservation",
                )
            reservation = _validate_reservation(
                event["data"]["next_reservation"],
                "$.request.event.data.next_reservation",
            )
            if reservation["predecessor_plan"] != latest_plan:
                _refuse(
                    "binding_mismatch",
                    "$.request.event.data.next_reservation.predecessor_plan",
                    "slice mutation must bind the latest delegate plan",
                )
            budget_for_check = dict(state)
            budget_for_check["budget"] = dict(budget)
            violations = _ceo_check_reservation(reservation, budget_for_check)
            if violations:
                return _ceo_semantic_refusal(
                    state,
                    event,
                    grant,
                    root,
                    "budget_exceeded",
                    json.dumps(violations, sort_keys=True, separators=(",", ":")),
                    budget=budget,
                    artifacts=artifacts,
                    accepted_evidence_heads=accepted_evidence,
                )
            delegate_plan = delegate(
                {
                    "schema": "autobest-delegate-request/1",
                    "task": state["active_task"],
                    "root_envelope": root,
                    "reservation": reservation,
                    "policy": policy,
                    "observations": event["data"]["observations"],
                }
            )
            artifacts["delegate_plan_heads"].append(delegate_plan["plan_head"])
            observed_dimensions = {
                assignment["dimension_id"] for assignment in delegate_plan["assignments"]
            }
            if observed_dimensions != set(state["selected_dimensions"]):
                return _ceo_semantic_refusal(
                    state,
                    event,
                    grant,
                    root,
                    "dimension_observation_mismatch",
                    "mutated observations must exactly cover selected Dimensions",
                    budget=budget,
                    artifacts=artifacts,
                    accepted_evidence_heads=accepted_evidence,
                    emitted_delegate=delegate_plan,
                    plan_heads=(delegate_plan["plan_head"],),
                )
            if not delegate_plan["ok"]:
                return _ceo_semantic_refusal(
                    state,
                    event,
                    grant,
                    root,
                    "delegation_refused",
                    "mutated JIT slice produced no eligible assignment",
                    budget=budget,
                    artifacts=artifacts,
                    accepted_evidence_heads=accepted_evidence,
                    emitted_delegate=delegate_plan,
                    plan_heads=(delegate_plan["plan_head"],),
                )
            budget["latest_reservation"] = dict(
                delegate_plan["current_reservation"]["effective_resources"]
            )
            next_state = _ceo_advance_state(
                state,
                event,
                phase="checkpoint_observation",
                budget=budget,
                artifacts=artifacts,
                accepted_evidence_heads=accepted_evidence,
                plan_heads=(delegate_plan["plan_head"],),
            )
            next_action = _ceo_action(
                next_state,
                grant,
                root,
                "execute_mutated_jit_assignments",
                "checkpoint_observed",
                {
                    "delegate_plan_head": delegate_plan["plan_head"],
                    "disposition": disposition,
                    "assignments": _json_copy(delegate_plan["assignments"]),
                    "prior_checkpoints": list(artifacts["checkpoint_heads"]),
                },
            )
            return _ceo_result(
                next_state,
                next_action,
                {
                    "from": "checkpoint_observation",
                    "to": "checkpoint_observation",
                    "event_head": event["head"],
                    "code": "slice_mutated",
                    "reason": "successor reservation remained within root, grant, and remaining budget",
                },
                emitted_delegate=delegate_plan,
            )

        if event["data"]["next_reservation"] is not None or event["data"]["observations"]:
            _refuse(
                "unexpected_field",
                "$.request.event.data",
                "stop requires null reservation and an empty observation list",
            )
        missing_action = _ceo_require_actions(
            state, event, grant, root, "difference_parallel"
        )
        if missing_action is not None:
            return missing_action
        differences = event["data"]["differences"]
        if not isinstance(differences, list) or not differences:
            _refuse(
                "list_required",
                "$.request.event.data.differences",
                "stop requires explicit difference-only tasks",
            )
        if len(differences) > MAX_CEO_DIFFERENCES:
            _refuse(
                "too_many_items",
                "$.request.event.data.differences",
                f"difference count exceeds {MAX_CEO_DIFFERENCES}",
            )
        seen_differences = set()
        difference_tasks = []
        for index, difference in enumerate(differences):
            _ceo_validate_difference(
                difference,
                f"$.request.event.data.differences[{index}]",
                set(state["selected_dimensions"]),
                checkpoint_heads,
            )
            if difference["difference_id"] in seen_differences:
                _refuse(
                    "duplicate_item",
                    f"$.request.event.data.differences[{index}].difference_id",
                    "duplicate difference id",
                )
            seen_differences.add(difference["difference_id"])
            difference_tasks.append(_json_copy(difference))
        artifacts["difference_task_heads"] = sorted(
            difference["task"]["head"] for difference in differences
        )
        budget["latest_reservation"] = _zero_resources()
        next_state = _ceo_advance_state(
            state,
            event,
            phase="difference_parallel",
            budget=budget,
            artifacts=artifacts,
            accepted_evidence_heads=accepted_evidence,
        )
        next_action = _ceo_action(
            next_state,
            grant,
            root,
            "execute_difference_only_parallel_work",
            "differences_completed",
            {
                "difference_tasks": difference_tasks,
                "shared_checkpoint_heads": list(checkpoint_heads),
                "shared_work_must_not_repeat": True,
                "maximum_parallel_dimensions": grant["max_parallel_dimensions"],
            },
        )
        return _ceo_result(
            next_state,
            next_action,
            {
                "from": "checkpoint_observation",
                "to": "difference_parallel",
                "event_head": event["head"],
                "code": "difference_only_split",
                "reason": "shared work stopped and only declared differences were emitted",
            },
        )

    if state["phase"] == "difference_parallel":
        _closed(
            event["data"],
            "$.request.event.data",
            ("difference_task_heads", "candidates"),
        )
        missing_action = _ceo_require_actions(state, event, grant, root, "cross")
        if missing_action is not None:
            return missing_action
        difference_heads = _bounded_sha_list(
            event["data"]["difference_task_heads"],
            "$.request.event.data.difference_task_heads",
            MAX_CEO_DIFFERENCES,
            allow_empty=False,
        )
        if set(difference_heads) != set(state["artifacts"]["difference_task_heads"]):
            _refuse(
                "binding_mismatch",
                "$.request.event.data.difference_task_heads",
                "completion must bind every and only emitted difference task",
            )
        candidates = event["data"]["candidates"]
        if not isinstance(candidates, list) or not candidates:
            _refuse(
                "list_required",
                "$.request.event.data.candidates",
                "difference completion requires inert deliverable candidates",
            )
        for index, candidate in enumerate(candidates):
            if not isinstance(candidate, dict):
                _refuse(
                    "object_required",
                    f"$.request.event.data.candidates[{index}]",
                    "candidate must be an object",
                )
            provenance = candidate.get("provenance")
            if not isinstance(provenance, dict) or not set(provenance.get("parent_refs", [])) & set(
                difference_heads
            ):
                _refuse(
                    "missing_provenance",
                    f"$.request.event.data.candidates[{index}].provenance.parent_refs",
                    "candidate must retain at least one difference-task parent",
                )
        cross_plan = cross(
            {
                "schema": "autobest-cross-request/1",
                "task": state["active_task"],
                "policy": policy,
                "candidates": candidates,
            }
        )
        artifacts = _json_copy(state["artifacts"])
        artifacts["candidate_heads"] = sorted(
            candidate["head"] for candidate in candidates
        )
        artifacts["cross_plan_head"] = cross_plan["plan_head"]
        if not cross_plan["ok"]:
            return _ceo_semantic_refusal(
                state,
                event,
                grant,
                root,
                "crossing_refused",
                "Crossing Lens refused AutoBest; no partial composite is handed off",
                artifacts=artifacts,
                plan_heads=(cross_plan["plan_head"],),
                emitted_cross=cross_plan,
            )
        verifiers = _ceo_available_verifiers(
            organization, grant, state["selected_dimensions"]
        )
        if len(verifiers) < grant["minimum_verifiers"]:
            return _ceo_semantic_refusal(
                state,
                event,
                grant,
                root,
                "insufficient_independent_verifiers",
                "verified grant requires more independent verifier Dimensions",
                artifacts=artifacts,
                plan_heads=(cross_plan["plan_head"],),
                emitted_cross=cross_plan,
            )
        next_state = _ceo_advance_state(
            state,
            event,
            phase="independent_verification",
            artifacts=artifacts,
            plan_heads=(cross_plan["plan_head"],),
        )
        next_action = _ceo_action(
            next_state,
            grant,
            root,
            "request_independent_verification",
            "verification_completed",
            {
                "cross_plan": cross_plan,
                "eligible_verifier_dimensions": verifiers,
                "minimum_verifiers": grant["minimum_verifiers"],
                "verifiers_must_be_independent": True,
            },
        )
        return _ceo_result(
            next_state,
            next_action,
            {
                "from": "difference_parallel",
                "to": "independent_verification",
                "event_head": event["head"],
                "code": "crossing_candidate_ready",
                "reason": "AutoBest composite remains inert pending independent verification",
            },
            emitted_cross=cross_plan,
        )

    if state["phase"] == "independent_verification":
        _closed(event["data"], "$.request.event.data", ("cross_plan_head", "results"))
        missing_action = _ceo_require_actions(state, event, grant, root, "verify")
        if missing_action is not None:
            return missing_action
        _sha256(event["data"]["cross_plan_head"], "$.request.event.data.cross_plan_head")
        if event["data"]["cross_plan_head"] != state["artifacts"]["cross_plan_head"]:
            _refuse(
                "binding_mismatch",
                "$.request.event.data.cross_plan_head",
                "verification does not bind the exact Crossing plan",
            )
        results = event["data"]["results"]
        if not isinstance(results, list) or not results or len(results) > MAX_CEO_VERIFIERS:
            _refuse(
                "list_required",
                "$.request.event.data.results",
                f"expected 1..{MAX_CEO_VERIFIERS} verifier results",
            )
        eligible_verifiers = set(
            _ceo_available_verifiers(organization, grant, state["selected_dimensions"])
        )
        seen_verifiers = set()
        failures = []
        for index, result in enumerate(results):
            _ceo_validate_verification_result(
                result, f"$.request.event.data.results[{index}]"
            )
            verifier = result["verifier_dimension_id"]
            if verifier in seen_verifiers:
                _refuse(
                    "duplicate_item",
                    f"$.request.event.data.results[{index}].verifier_dimension_id",
                    "duplicate verifier Dimension",
                )
            if verifier not in eligible_verifiers:
                _refuse(
                    "verifier_not_independent",
                    f"$.request.event.data.results[{index}].verifier_dimension_id",
                    "verifier is not a granted independent verification Dimension",
                )
            if result["receipt_head"] not in event["provenance"]["parent_refs"]:
                _refuse(
                    "missing_receipt_binding",
                    f"$.request.event.data.results[{index}].receipt_head",
                    "verification event must retain every verifier receipt",
                )
            seen_verifiers.add(verifier)
            if not result["passed"]:
                failures.append(verifier + ": " + ", ".join(result["checks"]))
        if len(results) < grant["minimum_verifiers"]:
            failures.append("minimum verifier count not met")
        verification = {
            "passed": not failures,
            "event_head": event["head"],
            "verifier_dimensions": sorted(seen_verifiers),
            "failures": failures,
        }
        artifacts = _json_copy(state["artifacts"])
        artifacts["verification_event_heads"].append(event["head"])
        accepted_evidence = list(state["accepted_evidence_heads"])
        accepted_evidence.append(event["head"])
        if verification["passed"] and state["artifacts"]["cross_plan_head"] not in accepted_evidence:
            accepted_evidence.append(state["artifacts"]["cross_plan_head"])
        next_state = _ceo_advance_state(
            state,
            event,
            phase="decision",
            artifacts=artifacts,
            accepted_evidence_heads=accepted_evidence,
            verification=verification,
        )
        allowed_decisions = ["approve", "refuse"] if verification["passed"] else ["refuse"]
        next_action = _ceo_action(
            next_state,
            grant,
            root,
            "request_external_decision",
            "decision_recorded",
            {
                "verification": verification,
                "allowed_decisions": allowed_decisions,
                "user_command_is_authority": False,
                "decision_requires_separate_receipt": True,
            },
        )
        return _ceo_result(
            next_state,
            next_action,
            {
                "from": "independent_verification",
                "to": "decision",
                "event_head": event["head"],
                "code": "verification_complete",
                "reason": "independent verification result recorded without self-approval",
            },
        )

    if state["phase"] == "decision":
        _closed(
            event["data"],
            "$.request.event.data",
            ("decision", "reason", "verification_event_head"),
        )
        missing_action = _ceo_require_actions(state, event, grant, root, "decide")
        if missing_action is not None:
            return missing_action
        decision_kind = event["data"]["decision"]
        if decision_kind not in ("approve", "refuse"):
            _refuse(
                "invalid_enum",
                "$.request.event.data.decision",
                "expected approve or refuse",
            )
        reason = _text(event["data"]["reason"], "$.request.event.data.reason", max_bytes=1024)
        _sha256(
            event["data"]["verification_event_head"],
            "$.request.event.data.verification_event_head",
        )
        if event["data"]["verification_event_head"] != state["verification"]["event_head"]:
            _refuse(
                "binding_mismatch",
                "$.request.event.data.verification_event_head",
                "decision does not bind the exact verification event",
            )
        if decision_kind == "approve" and not state["verification"]["passed"]:
            return _ceo_semantic_refusal(
                state,
                event,
                grant,
                root,
                "approval_without_verification",
                "CEO cannot approve after failed independent verification",
                verification=state["verification"],
            )
        if _ceo_missing_actions(grant, "handoff", "close"):
            return _ceo_semantic_refusal(
                state,
                event,
                grant,
                root,
                "grant_action_missing",
                "grant does not permit bounded handoff and close",
                verification=state["verification"],
            )
        decision = {
            "kind": decision_kind,
            "reason": reason,
            "event_head": event["head"],
        }
        status = "verified_ready" if decision_kind == "approve" else "refused"
        next_state = _ceo_advance_state(
            state,
            event,
            phase="handoff",
            status=status,
            decision=decision,
        )
        next_action = _ceo_handoff_action(next_state, grant, root)
        return _ceo_result(
            next_state,
            next_action,
            {
                "from": "decision",
                "to": "handoff",
                "event_head": event["head"],
                "code": "verified_ready" if decision_kind == "approve" else "decision_refused",
                "reason": reason,
            },
        )

    if state["phase"] == "handoff":
        _closed(
            event["data"],
            "$.request.event.data",
            ("decision_event_head", "handoff_head", "outcome", "closed"),
        )
        missing_action = _ceo_require_actions(
            state, event, grant, root, "handoff", "close"
        )
        if missing_action is not None:
            return missing_action
        if state["decision"] is None or state["decision"]["event_head"] is None:
            _refuse("invalid_state", "$.request.state.decision", "handoff requires a decision event")
        _sha256(
            event["data"]["decision_event_head"],
            "$.request.event.data.decision_event_head",
        )
        if event["data"]["decision_event_head"] != state["decision"]["event_head"]:
            _refuse(
                "binding_mismatch",
                "$.request.event.data.decision_event_head",
                "handoff close does not bind the exact decision event",
            )
        _sha256(event["data"]["handoff_head"], "$.request.event.data.handoff_head")
        if event["data"]["outcome"] not in ("recorded", "retained"):
            _refuse(
                "invalid_enum",
                "$.request.event.data.outcome",
                "expected recorded or retained",
            )
        if event["data"]["closed"] is not True:
            _refuse(
                "boolean_required",
                "$.request.event.data.closed",
                "close event must explicitly set closed true",
            )
        artifacts = _json_copy(state["artifacts"])
        artifacts["handoff_head"] = event["data"]["handoff_head"]
        next_state = _ceo_advance_state(
            state,
            event,
            phase="closed",
            status="closed",
            artifacts=artifacts,
        )
        return _ceo_result(
            next_state,
            None,
            {
                "from": "handoff",
                "to": "closed",
                "event_head": event["head"],
                "code": "mission_closed",
                "reason": "external handoff receipt recorded; no further action emitted",
            },
        )

    _refuse("invalid_state", "$.request.state.phase", "unsupported CEO lifecycle phase")


def _refusal_result(operation, refusal):
    result = {
        "schema": "autobest-refusal/1",
        "ok": False,
        "operation": operation if isinstance(operation, str) else "invalid",
        "record_role": "candidate-data",
        "authority_granted": False,
        "authority_source": "external-host",
        "rapp1_role": "core-compatibility-substrate",
        "rapp1_compatibility_required": True,
        "executed": False,
        "workers_launched": 0,
        "frames_emitted": 0,
        "refusal": {
            "code": refusal.code,
            "path": refusal.path,
            "detail": refusal.detail,
        },
        "evidence": refusal.evidence,
    }
    result["refusal_head"] = canonical_digest("refusal/v1", result)
    return result


try:
    from agents.basic_agent import BasicAgent
except ImportError:
    try:
        from basic_agent import BasicAgent
    except ImportError:

        class BasicAgent:
            """Minimal local compatibility surface used when Brainstem is absent."""

            def __init__(self, name=None, metadata=None):
                self.name = name or getattr(self, "name", "BasicAgent")
                self.metadata = metadata or getattr(self, "metadata", {})

            def to_tool(self):
                return {
                    "type": "function",
                    "function": {
                        "name": self.name,
                        "description": self.metadata.get("description", ""),
                        "parameters": self.metadata.get(
                            "parameters", {"type": "object", "properties": {}}
                        ),
                    },
                }


class MicrosolAutoBestAgent(BasicAgent):
    """BasicAgent-compatible wrapper around the pure planner/reducer functions."""

    metadata = {
        "name": "microsol_autobest",
        "description": (
            "Return deterministic inert AutoBest or microsol-ceo candidate JSON for a "
            "caller-supplied task and verified state; never launch, sign, adopt, or perform effects."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "enum": [
                        "delegate",
                        "cross",
                        "run",
                        "compatibility",
                        "compatibility-frame",
                        "compatibility_exhaust",
                        "compatibility-exhaust",
                        "compatibility_successor",
                        "compatibility-successor",
                        "double_hotload",
                        "double-hotload",
                        "compile_static_agent",
                        "compile-static-agent",
                        "self_host_repository",
                        "self-host-repository",
                        "artifact_bundle",
                        "artifact-bundle",
                        "mutation_offer",
                        "mutation-offer",
                        "mutation_offer_decision",
                        "mutation-offer-decision",
                        "meta_evolution",
                        "meta-evolution",
                        "n_lens_search",
                        "n-lens-search",
                        "translate_hive",
                        "hive-translate",
                        "ceo",
                        "microsol-ceo",
                    ],
                },
                "request": {"type": "object"},
            },
            "required": ["operation", "request"],
            "additionalProperties": False,
        },
    }

    def __init__(self):
        self.name = "microsol_autobest"
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs):
        operation = kwargs.get("operation")
        try:
            _prepare_input(kwargs, "$.arguments")
            _closed(kwargs, "$.arguments", ("operation", "request"))
            if operation not in (
                "delegate",
                "cross",
                "run",
                "compatibility",
                "compatibility-frame",
                "compatibility_exhaust",
                "compatibility-exhaust",
                "compatibility_successor",
                "compatibility-successor",
                "double_hotload",
                "double-hotload",
                "compile_static_agent",
                "compile-static-agent",
                "self_host_repository",
                "self-host-repository",
                "artifact_bundle",
                "artifact-bundle",
                "mutation_offer",
                "mutation-offer",
                "mutation_offer_decision",
                "mutation-offer-decision",
                "meta_evolution",
                "meta-evolution",
                "n_lens_search",
                "n-lens-search",
                "translate_hive",
                "hive-translate",
                "ceo",
                "microsol-ceo",
            ):
                _refuse(
                    "unsupported_operation",
                    "$.arguments.operation",
                    "expected delegate, cross, run, compatibility, compatibility-frame, compatibility_exhaust, compatibility-exhaust, compatibility_successor, compatibility-successor, double_hotload, double-hotload, compile_static_agent, compile-static-agent, self_host_repository, self-host-repository, artifact_bundle, artifact-bundle, mutation_offer, mutation-offer, mutation_offer_decision, mutation-offer-decision, meta_evolution, meta-evolution, n_lens_search, n-lens-search, translate_hive, hive-translate, ceo, or microsol-ceo",
                )
            function = {
                "delegate": delegate,
                "cross": cross,
                "run": run,
                "compatibility": compatibility,
                "compatibility-frame": compatibility,
                "compatibility_exhaust": compatibility_exhaust,
                "compatibility-exhaust": compatibility_exhaust,
                "compatibility_successor": compatibility_successor,
                "compatibility-successor": compatibility_successor,
                "double_hotload": double_hotload,
                "double-hotload": double_hotload,
                "compile_static_agent": compile_static_agent,
                "compile-static-agent": compile_static_agent,
                "self_host_repository": self_host_repository,
                "self-host-repository": self_host_repository,
                "artifact_bundle": artifact_bundle,
                "artifact-bundle": artifact_bundle,
                "mutation_offer": mutation_offer,
                "mutation-offer": mutation_offer,
                "mutation_offer_decision": mutation_offer_decision,
                "mutation-offer-decision": mutation_offer_decision,
                "meta_evolution": meta_evolution,
                "meta-evolution": meta_evolution,
                "n_lens_search": n_lens_search,
                "n-lens-search": n_lens_search,
                "translate_hive": translate_hive,
                "hive-translate": translate_hive,
                "ceo": ceo,
                "microsol-ceo": ceo,
            }[operation]
            result = function(kwargs["request"])
        except AutoBestRefusal as refusal:
            result = _refusal_result(operation, refusal)
        return json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


AutoBestAgent = MicrosolAutoBestAgent


def main(argv=None):
    """Run one JSON argument shaped as {"operation": ..., "request": ...}."""

    arguments = list(sys.argv[1:] if argv is None else argv)
    if len(arguments) != 1:
        refusal = AutoBestRefusal(
            "invalid_arguments",
            "$",
            "provide exactly one closed JSON object argument; stdin, files, and environment are never read",
        )
        result = _refusal_result("invalid", refusal)
        print(json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(",", ":")))
        return 2
    try:
        payload = loads_json(arguments[0])
        _closed(payload, "$", ("operation", "request"))
        rendered = MicrosolAutoBestAgent().perform(
            operation=payload["operation"],
            request=payload["request"],
        )
    except AutoBestRefusal as refusal:
        rendered = json.dumps(
            _refusal_result("invalid", refusal),
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
    print(rendered)
    return 0 if json.loads(rendered)["ok"] else 2


__all__ = [
    "AutoBestAgent",
    "AutoBestRefusal",
    "CEO_ACTIONS",
    "CEO_CONTROL_MODES",
    "CEO_EVENT_TYPES",
    "CEO_PHASES",
    "DIGEST_DOMAINS",
    "MICROSOL_CEO_PROFILE",
    "MicrosolAutoBestAgent",
    "PROFILE_CONFIGS",
    "PRIOR_ART_PROVENANCE",
    "__manifest__",
    "bind_implementation_sha256",
    "artifact_bundle",
    "canonical_digest",
    "ceo",
    "compile_static_agent",
    "compatibility",
    "compatibility_exhaust",
    "compatibility_successor",
    "cross",
    "delegate",
    "double_hotload",
    "head_record",
    "loads_json",
    "main",
    "meta_evolution",
    "mutation_offer",
    "mutation_offer_decision",
    "n_lens_search",
    "prior_art_provenance",
    "profile_config",
    "run",
    "self_host_repository",
    "translate_hive",
]


if __name__ == "__main__":
    raise SystemExit(main())
