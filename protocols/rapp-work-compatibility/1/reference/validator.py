"""Pure validation and deterministic static-agent compilation for the profile."""

from __future__ import annotations

import json
from typing import Any

from common import (
    PROFILE,
    Parent,
    SchemaSet,
    canonical_bytes,
    require,
    sha,
    wave,
)

LOSS_ORDER = {
    "lossless-direct": 0,
    "lossless-retained-delta": 1,
    "lossy-source-referenced": 2,
    "lossy-unavailable": 3,
}


def _sorted_unique(values: object, reason: str) -> list[object]:
    require(type(values) is list, reason)
    encoded = [canonical_bytes(value) for value in values]
    require(encoded == sorted(encoded) and len(encoded) == len(set(encoded)), reason)
    return values


def validate_compatibility(value: object, schemas: SchemaSet | None = None) -> dict[str, Any]:
    schemas = SchemaSet() if schemas is None else schemas
    record = schemas.validate(value, "compatibility.schema.json")
    assert isinstance(record, dict)
    source = record["source"]
    require(source["stream_id"].startswith(source["rappid"] + ":"), "source stream/RAPPID mismatch")
    require(
        record["lens"]["passes"] == ["source-lens", "target-finalizer"],
        "double-hotload pass order required",
    )
    _sorted_unique(source["capabilities"], "source capabilities must be sorted and unique")
    _sorted_unique(record["target"]["operations"], "target operations must be sorted and unique")
    _sorted_unique(record["coverage"]["gaps"], "coverage gaps must be sorted and unique")
    _sorted_unique(record["coverage"]["unknowns"], "coverage unknowns must be sorted and unique")
    supported = record["coverage"]["supported"]
    required = record["coverage"]["required"]
    require(supported <= required, "coverage supported exceeds required")
    require(
        record["coverage"]["basis_points"] == supported * 10000 // required,
        "coverage basis points mismatch",
    )
    if record["status"] == "full":
        require(
            supported == required
            and not record["coverage"]["gaps"]
            and not record["coverage"]["unknowns"],
            "full compatibility requires complete known coverage",
        )
    static = record["static_program"]
    static_values = (
        static["bundle"],
        static["entrypoint"],
        static["generation_receipt"],
    )
    require(
        all(item is None for item in static_values)
        or all(item is not None for item in static_values),
        "static program binding must be complete or absent",
    )
    lineage = record["lineage"]
    require(
        (lineage["previous_compatibility"] is None)
        == (lineage["trigger_exhaust"] is None),
        "compatibility successor requires predecessor and exhaust together",
    )
    source_wave = {"space": "rapp/1:wave", "hash": source["head"]["frame_hash"]}
    require(source_wave in lineage["parents"], "source head must be a compatibility parent")
    require(
        record["qualification"]["generated_tests_are_independent_proof"] is False
        and record["grants_authority"] is False,
        "candidate evidence cannot grant authority or self-certify",
    )
    return record


def validate_exhaust(value: object, schemas: SchemaSet | None = None) -> dict[str, Any]:
    schemas = SchemaSet() if schemas is None else schemas
    record = schemas.validate(value, "compatibility-exhaust.schema.json")
    assert isinstance(record, dict)
    _sorted_unique(record["missing_coverage"], "missing coverage must be sorted and unique")
    require(record["privacy_safe"] is True and record["grants_authority"] is False, "unsafe exhaust")
    return record


def validate_causal_manifest(value: object, schemas: SchemaSet | None = None) -> dict[str, Any]:
    schemas = SchemaSet() if schemas is None else schemas
    manifest = schemas.validate(value, "causal-mutation-manifest.schema.json")
    assert isinstance(manifest, dict)
    forward = manifest["forward"]
    reverse = manifest["reverse"]
    source_paths = [entry["source"]["path"] for entry in forward]
    target_paths = [entry["target"]["path"] for entry in reverse]
    require(len(source_paths) == len(set(source_paths)), "duplicate forward source path")
    require(len(target_paths) == len(set(target_paths)), "duplicate reverse target path")
    forward_targets: set[str] = set()
    for entry in forward:
        targets = [target["path"] for target in entry["targets"]]
        require(len(targets) == len(set(targets)), "duplicate forward target path")
        if entry["disposition"] == "removed":
            require(not targets and entry["content_relation"] == "absent", "removed entry has targets")
        else:
            require(targets and entry["content_relation"] != "absent", "nonremoved entry lacks target")
        forward_targets.update(targets)
    require(forward_targets == set(target_paths), "forward and reverse target partitions differ")
    known_sources = set(source_paths)
    for entry in reverse:
        origins = [source["path"] for source in entry["sources"]]
        require(len(origins) == len(set(origins)), "duplicate reverse source path")
        require(set(origins) <= known_sources, "reverse map references unknown source")
        if entry["provenance"] == "new":
            require(not origins, "new target cannot claim source ancestry")
        else:
            require(origins, "inherited or derived target requires source ancestry")
    highest = max(
        [
            LOSS_ORDER[entry["loss_class"]]
            for entry in [*forward, *reverse]
        ],
        default=0,
    )
    require(
        LOSS_ORDER[manifest["aggregate_loss_class"]] == highest,
        "aggregate loss class mismatch",
    )
    _sorted_unique(manifest["selected_traits"], "selected traits must be sorted and unique")
    _sorted_unique(manifest["omitted_traits"], "omitted traits must be sorted and unique")
    return manifest


def validate_learning_trace(
    value: object,
    schemas: SchemaSet | None = None,
    core: Parent | None = None,
) -> dict[str, Any]:
    schemas = SchemaSet() if schemas is None else schemas
    trace = schemas.validate(value, "learning-trace.schema.json")
    assert isinstance(trace, dict)
    previous = None
    for index, event in enumerate(trace["events"]):
        require(event["seq"] == index, "learning trace sequence gap")
        require(event["previous_event"] == previous, "learning trace predecessor mismatch")
        if event["kind"] == "user-correction":
            require(
                event["actor_class"] in {"user-authority", "owner-authority"}
                and event["authority_evidence"] is not None,
                "user correction lacks authority evidence",
            )
        if event["kind"] == "assistant-proposal":
            require(
                event["actor_class"] == "assistant-proposal"
                and event["authority_evidence"] is None,
                "assistant proposal cannot claim user authority",
            )
        previous = (
            core.particle(event)
            if core is not None
            else {"space": "rapp/1:particle", "hash": sha(canonical_bytes(event))}
        )
    require(
        trace["raw_transcript_persisted"] is False
        and trace["hidden_reasoning_persisted"] is False
        and trace["native_paths_persisted"] is False,
        "learning trace privacy boundary violated",
    )
    return trace


def validate_handshake_package(value: object, schemas: SchemaSet | None = None) -> dict[str, Any]:
    schemas = SchemaSet() if schemas is None else schemas
    package = schemas.validate(value, "handshake-package.schema.json")
    assert isinstance(package, dict)
    require(
        package["source_agent"]["sha256"] != package["target_agent"]["sha256"],
        "source and target roles must remain explicit even when implementations later converge",
    )
    require(package["authority"] is False, "handshake package cannot grant authority")
    return package


def validate_capability_manifest(
    value: object,
    schemas: SchemaSet | None = None,
) -> dict[str, Any]:
    schemas = SchemaSet() if schemas is None else schemas
    capability = schemas.validate(value, "capability-manifest.schema.json")
    assert isinstance(capability, dict)
    agent = capability["agent"]
    skill = capability["skill"]
    require(
        agent["role"] == "generic-autobest-agent"
        and skill["role"] == "generic-autobest-skill",
        "generic AutoBest artifact roles are exact",
    )
    require(
        agent["path"].startswith("artifacts/sha256/" + agent["sha256"] + "/")
        and skill["path"].startswith("artifacts/sha256/" + skill["sha256"] + "/"),
        "generic AutoBest artifacts must use hash-addressed paths",
    )
    require(
        capability["profiles"] == ["generic", "microsol-ceo"]
        and capability["authority_from_presence"] is False
        and capability["skill_activates"] is False
        and capability["grants_authority"] is False,
        "generic AutoBest capability cannot activate or grant authority",
    )
    return capability


def validate_seed_capability_binding(
    value: object,
    *,
    capability: dict[str, Any] | None = None,
    core: Parent | None = None,
    schemas: SchemaSet | None = None,
) -> dict[str, Any]:
    schemas = SchemaSet() if schemas is None else schemas
    binding = schemas.validate(value, "seed-capability-binding.schema.json")
    assert isinstance(binding, dict)
    relation = binding["relation"]
    refs = (
        binding["ancestor_binding"],
        binding["parent_binding"],
        binding["previous_binding"],
    )
    if relation == "ancestor-seed":
        require(all(item is None for item in refs), "ancestor seed binding cannot name prior bindings")
    elif relation == "descendant-seed":
        require(
            binding["ancestor_binding"] is not None
            and binding["parent_binding"] is not None
            and binding["previous_binding"] is None,
            "descendant seed binding requires ancestor and parent only",
        )
    else:
        require(
            binding["ancestor_binding"] is not None
            and binding["previous_binding"] is not None,
            "capability successor requires ancestor and previous binding",
        )
    require(
        binding["workspace_spec_sha256"]
        == "80135ae05e532f11810d31a5cf974050a8332c18bd45f16879a7286f213edfab",
        "wrong Workspace/1 seed binding pin",
    )
    require(
        binding["executable"] is False
        and binding["host_activation"] == "external-host-only"
        and binding["grants_authority"] is False,
        "seed capability presence cannot activate execution",
    )
    if capability is not None:
        require(core is not None, "canonical RAPP/1 parent required for capability binding")
        validated = validate_capability_manifest(capability, schemas)
        require(binding["capability"] == core.particle(validated), "capability particle mismatch")
        require(binding["agent"] == validated["agent"]["particle"], "agent particle mismatch")
        require(binding["skill"] == validated["skill"]["particle"], "Skill particle mismatch")
    return binding


def verify_profile_frame(
    core: Parent,
    frame: dict[str, Any],
    *,
    previous: dict[str, Any] | None = None,
) -> dict[str, Any]:
    ok, step, reason = core.r.verify_frame(
        frame,
        head=previous,
        stream_id_of_record=frame["stream_id"],
    )
    require(ok, f"RAPP/1 frame refusal: {step}: {reason}")
    payload = frame["payload"]
    require(
        type(payload) is dict
        and payload.get("profile") == PROFILE
        and payload.get("operation")
        in {
            "compatibility",
            "compatibility-exhaust",
            "seed-capability-binding",
        },
        "wrong compatibility frame payload",
    )
    if payload["operation"] == "compatibility":
        validate_compatibility(payload["record"])
    elif payload["operation"] == "compatibility-exhaust":
        validate_exhaust(payload["record"])
    else:
        validate_seed_capability_binding(payload["record"])
    return payload["record"]


def artifact_descriptor(
    core: Parent,
    path: str,
    raw: bytes,
    *,
    role: str,
    media_type: str,
) -> dict[str, Any]:
    content = {
        "schema": PROFILE + "/artifact-octets",
        "media_type": media_type,
        "octets_sha256": sha(raw),
        "octets_count": len(raw),
    }
    return {
        "path": path,
        "sha256": sha(raw),
        "bytes": len(raw),
        "particle": core.particle(content),
        "role": role,
        "media_type": media_type,
        "executable": False,
    }


def compile_static_agent(frame: dict[str, Any], handshake: dict[str, Any]) -> bytes:
    """Compile one deterministic two-direction Bill fixture agent."""
    validate_compatibility(frame["payload"]["record"])
    source_mapping = json.dumps(
        handshake["source_to_target"],
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    target_mapping = json.dumps(
        handshake["target_to_source"],
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    source_profile = json.dumps(handshake["source_match"]["profile"])
    target_profile = json.dumps(handshake["target"]["profile"])
    frame_hash = json.dumps(frame["frame_hash"])
    frame_keys = sorted(
        [
            "spec",
            "kind",
            "stream_id",
            "seq",
            "utc",
            "payload",
            "payload_hash",
            "frame_hash",
            "prev",
            "prev_wave",
            "sig",
        ]
    )
    source = f'''"""Deterministic RAPP Work compatibility fixture agent."""
from __future__ import annotations

import hashlib
import json
import sys

COMPATIBILITY_FRAME_HASH = {frame_hash}
SOURCE_PROFILE = {source_profile}
TARGET_PROFILE = {target_profile}
SOURCE_MAPPING = json.loads({source_mapping!r})
TARGET_MAPPING = json.loads({target_mapping!r})
FRAME_KEYS = {frame_keys!r}

def pairs(items):
    result = {{}}
    for key, value in items:
        if key in result:
            raise ValueError("REFUSE_JSON_DUPLICATE")
        result[key] = value
    return result

def invalid_number(_value):
    raise ValueError("REFUSE_NUMBER")

def parse(value):
    if isinstance(value, str):
        return json.loads(value, object_pairs_hook=pairs, parse_float=invalid_number,
                          parse_constant=invalid_number)
    return value

def canonical(value):
    return json.dumps(value, ensure_ascii=False, allow_nan=False, sort_keys=True,
                      separators=(",", ":"))

def select(value, path):
    current = value
    for part in path.split("."):
        if not isinstance(current, dict) or part not in current:
            raise ValueError("REFUSE_MAPPING_SELECT")
        current = current[part]
    return current

def render(rule, context):
    if set(rule) == {{"const"}}:
        return rule["const"]
    if set(rule) == {{"select"}}:
        return select(context, rule["select"])
    raise ValueError("REFUSE_MAPPING_RULE")

def particle(value):
    return hashlib.sha256(
        b"rapp/1:particle\\n" + canonical(value).encode("utf-8")
    ).hexdigest()

def source_to_target(frame):
    frame = parse(frame)
    if not isinstance(frame, dict) or set(frame) != set(FRAME_KEYS):
        raise ValueError("REFUSE_FRAME")
    payload = frame.get("payload")
    if (frame.get("spec") != "rapp/1" or frame.get("kind") != "memory.save"
            or not isinstance(payload, dict) or payload.get("profile") != SOURCE_PROFILE):
        raise ValueError("REFUSE_PROFILE")
    operation = payload.get("operation")
    if operation not in SOURCE_MAPPING:
        raise ValueError("REFUSE_TYPED_EXHAUST")
    context = {{"payload": payload, "head": {{
        "stream_id": frame["stream_id"], "seq": frame["seq"],
        "payload_hash": frame["payload_hash"], "frame_hash": frame["frame_hash"]
    }}}}
    candidate = {{key: render(rule, context)
                  for key, rule in SOURCE_MAPPING[operation].items()}}
    output = {{
        "schema": "microsol-hive-observation/1",
        "operation": candidate["local_operation"],
        "subject": candidate["subject"],
        "source": {{
            "profile": candidate["source_profile"],
            "operation": candidate["source_operation"],
            "head": candidate["source_head"],
        }},
        "record": candidate["record"],
        "inventory": candidate["inventory"],
        "compatibility": {{
            "frame_hash": COMPATIBILITY_FRAME_HASH,
            "target_profile": TARGET_PROFILE,
        }},
        "coverage": {{
            "mapped": True,
            "unknown_fields": [],
            "complete_for_operation": True,
        }},
        "restrictions": {{
            "source_authority_inferred": False,
            "membership_inferred": False,
            "effects_authorized": False,
        }},
        "model_calls": 0,
        "authority": False,
    }}
    output["result_particle_hash"] = particle(output)
    return output

def target_to_source(value):
    value = parse(value)
    if not isinstance(value, dict):
        raise TypeError("REFUSE_INPUT")
    operation = "peer-offer"
    if operation not in TARGET_MAPPING:
        raise ValueError("REFUSE_TYPED_EXHAUST")
    output = {{key: render(rule, value)
              for key, rule in TARGET_MAPPING[operation].items()}}
    output["result_particle_hash"] = particle(output)
    return output

def perform(request):
    if not isinstance(request, dict) or set(request) != {{"direction", "value"}}:
        raise ValueError("REFUSE_INPUT")
    if request["direction"] == "source-to-target":
        result = source_to_target(request["value"])
    elif request["direction"] == "target-to-source":
        result = target_to_source(request["value"])
    else:
        raise ValueError("REFUSE_DIRECTION")
    return {{"ok": True, "authority": False, "executed_effects": 0,
             "model_calls": 0, "result": result}}

def main():
    try:
        request = parse(sys.stdin.read())
        print(canonical(perform(request)))
        return 0
    except (ValueError, KeyError, TypeError, json.JSONDecodeError) as error:
        print(canonical({{"ok": False, "authority": False, "executed_effects": 0,
                         "model_calls": 0,
                         "error": {{"code": str(error), "message": "Static agent refused."}}}}))
        return 2

if __name__ == "__main__":
    raise SystemExit(main())
'''
    return source.encode("utf-8")


def generation_receipt(
    core: Parent,
    compatibility_frame: dict[str, Any],
    compiler: dict[str, Any],
    runtime_sha256: str,
    agent_path: str,
    agent: bytes,
    tests: dict[str, str],
) -> dict[str, Any]:
    options = {
        "schema": PROFILE + "/static-agent-options",
        "line_endings": "lf",
        "encoding": "utf-8",
        "entrypoint": "agent.py",
    }
    output = artifact_descriptor(
        core,
        agent_path,
        agent,
        role="locked-static-agent",
        media_type="text/x-python",
    )
    value = {
        "schema": PROFILE + "/static-agent-generation",
        "compatibility": wave(compatibility_frame),
        "compatibility_payload_hash": compatibility_frame["payload_hash"],
        "compiler": compiler,
        "runtime_sha256": runtime_sha256,
        "options": core.particle(options),
        "output": output,
        "deterministic": True,
        "generated_tests_are_independent_proof": False,
        "tests": core.particle(tests),
        "grants_authority": False,
    }
    SchemaSet().validate(value, "static-agent-generation.schema.json")
    return value
