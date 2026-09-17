"""Generated static Hive compatibility agent. Do not edit."""
from __future__ import annotations
import hashlib, json, sys

COMPATIBILITY_FRAME_HASH = "80bf903340d3cc7f36864807682a6c0cf2229e010e5823019a03a8f92326f488"
SOURCE_PROFILE = "microsol-project/1"
TARGET_PROFILE = "microsol-repository-private-hive/1"
OPERATIONS = set(json.loads('["open","publish"]'))
MAPPING = json.loads('{"open":{"authority":{"const":false},"inventory":{"select":"payload.inventory"},"local_operation":{"const":"evidence"},"record":{"select":"payload.record"},"schema":{"const":"microsol-hive-compatible-observation/1"},"source_head":{"select":"head"},"source_operation":{"select":"payload.operation"},"source_profile":{"select":"payload.profile"},"subject":{"select":"payload.project"}},"publish":{"authority":{"const":false},"inventory":{"select":"payload.inventory"},"local_operation":{"const":"handoff"},"record":{"select":"payload.record"},"schema":{"const":"microsol-hive-compatible-observation/1"},"source_head":{"select":"head"},"source_operation":{"select":"payload.operation"},"source_profile":{"select":"payload.profile"},"subject":{"select":"payload.project"}}}')
FRAME_KEYS = ['frame_hash', 'kind', 'payload', 'payload_hash', 'prev', 'prev_wave', 'seq', 'sig', 'spec', 'stream_id', 'utc']

def pairs(items):
    out = {}
    for key, value in items:
        if key in out:
            raise ValueError("REFUSE_JSON_DUPLICATE")
        out[key] = value
    return out

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
    if set(rule) == {"const"}:
        return rule["const"]
    if set(rule) == {"select"}:
        return select(context, rule["select"])
    raise ValueError("REFUSE_MAPPING_RULE")

def transform(frame):
    frame = parse(frame)
    if not isinstance(frame, dict) or set(frame) != set(FRAME_KEYS):
        raise ValueError("REFUSE_FRAME")
    payload = frame.get("payload")
    if (frame.get("spec") != "rapp/1" or frame.get("kind") != "memory.save"
            or not isinstance(payload, dict)
            or payload.get("profile") != SOURCE_PROFILE
            or payload.get("operation") not in OPERATIONS):
        raise ValueError("REFUSE_PROFILE")
    operation = payload["operation"]
    context = {"payload": payload, "head": {
        "stream_id": frame["stream_id"], "seq": frame["seq"],
        "payload_hash": frame["payload_hash"], "frame_hash": frame["frame_hash"]
    }}
    candidate = {key: render(rule, context) for key, rule in MAPPING[operation].items()}
    output = {
        "schema": "microsol-hive-observation/1",
        "operation": candidate["local_operation"],
        "subject": candidate["subject"],
        "source": {
            "profile": candidate["source_profile"],
            "operation": candidate["source_operation"],
            "head": candidate["source_head"],
        },
        "record": candidate["record"],
        "inventory": candidate["inventory"],
        "compatibility": {
            "frame_hash": COMPATIBILITY_FRAME_HASH,
            "target_profile": TARGET_PROFILE,
        },
        "coverage": {
            "mapped": True,
            "unknown_fields": [],
            "complete_for_operation": True,
        },
        "restrictions": {
            "source_authority_inferred": False,
            "membership_inferred": False,
            "effects_authorized": False,
        },
        "model_calls": 0,
        "authority": False,
    }
    body = canonical(output)
    output["result_particle_hash"] = hashlib.sha256(
        b"rapp/1:particle\n" + body.encode("utf-8")
    ).hexdigest()
    return output

def perform(request):
    if not isinstance(request, dict) or set(request) != {"direction", "value"}:
        raise ValueError("REFUSE_INPUT")
    if request["direction"] != "source-to-target":
        raise ValueError("REFUSE_DIRECTION")
    return {"ok": True, "authority": False, "executed_effects": 0,
             "result": transform(request["value"])}

def main():
    try:
        request = parse(sys.stdin.read())
        print(canonical(perform(request)))
        return 0
    except Exception as error:
        print(canonical({"ok": False, "authority": False, "executed_effects": 0,
                         "error": {"code": str(error), "message": "Static mapping refused."}}))
        return 2

if __name__ == "__main__":
    raise SystemExit(main())
