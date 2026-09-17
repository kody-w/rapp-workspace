"""Deterministic static RAPP compatibility agent. Generated; do not edit."""
from __future__ import annotations
import hashlib, json, sys

COMPATIBILITY_FRAME_HASH = 'f266537ad8c2bc0509ee3e976adc09e7128f0fce587cf2b54a3af6538c6cee49'
HANDSHAKE_SHA256 = 'b606b5e9e051857c813fbb0fecaefebaa177c4fa81ece4d6f66fed42e9676440'
MAPPING = json.loads('{"source_operations":["open","publish"],"source_profile":"microsol-project/1","source_to_target":{"open":{"authority":{"const":false},"inventory":{"select":"payload.inventory"},"local_operation":{"const":"evidence"},"record":{"select":"payload.record"},"schema":{"const":"microsol-hive-compatible-observation/1"},"source_head":{"select":"head"},"source_operation":{"select":"payload.operation"},"source_profile":{"select":"payload.profile"},"subject":{"select":"payload.project"}},"publish":{"authority":{"const":false},"inventory":{"select":"payload.inventory"},"local_operation":{"const":"handoff"},"record":{"select":"payload.record"},"schema":{"const":"microsol-hive-compatible-observation/1"},"source_head":{"select":"head"},"source_operation":{"select":"payload.operation"},"source_profile":{"select":"payload.profile"},"subject":{"select":"payload.project"}}},"target_profile":"microsol-repository-private-hive/1","target_to_source":{"peer-offer":{"authority":{"const":false},"compatibility":{"select":"compatibility"},"operation":{"const":"peer-offer"},"peer":{"select":"peer"},"schema":{"const":"softwarecoellc-vteam-hive-peer-offer/1"},"subscription":{"select":"subscription"}}}}')
FRAME_KEYS = ['frame_hash', 'kind', 'payload', 'payload_hash', 'prev', 'prev_wave', 'seq', 'sig', 'spec', 'stream_id', 'utc']
MAX_INPUT_BYTES = 1048576

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

def particle(value):
    return hashlib.sha256(b"rapp/1:particle\n" + canonical(value).encode("utf-8")).hexdigest()

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

def source_to_target(frame):
    frame = parse(frame)
    if not isinstance(frame, dict) or set(frame) != set(FRAME_KEYS):
        raise ValueError("REFUSE_FRAME")
    payload = frame.get("payload")
    if (frame.get("spec") != "rapp/1" or frame.get("kind") != "memory.save"
            or not isinstance(payload, dict)
            or payload.get("profile") != MAPPING["source_profile"]
            or payload.get("operation") not in MAPPING["source_operations"]):
        raise ValueError("REFUSE_PROFILE")
    head = {"stream_id": frame["stream_id"], "seq": frame["seq"],
             "payload_hash": frame["payload_hash"], "frame_hash": frame["frame_hash"]}
    context = {"payload": payload, "head": head}
    rules = MAPPING["source_to_target"][payload["operation"]]
    candidate = {key: render(rule, context) for key, rule in rules.items()}
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
            "handshake_sha256": HANDSHAKE_SHA256,
            "target_profile": MAPPING["target_profile"],
        },
        "coverage": {"mapped": True, "unknown_fields": [], "complete_for_operation": True},
        "restrictions": {
            "source_authority_inferred": False,
            "membership_inferred": False,
            "effects_authorized": False,
        },
        "model_calls": 0,
        "authority": False,
    }
    output["result_particle_hash"] = particle(output)
    return output

def target_to_source(value):
    value = parse(value)
    if not isinstance(value, dict) or set(value) != {"peer", "compatibility", "subscription"}:
        raise ValueError("REFUSE_PEER_OFFER")
    output = {
        "schema": "softwarecoellc-vteam-hive-peer-offer/1",
        "operation": "peer-offer",
        "peer": value["peer"],
        "compatibility": value["compatibility"],
        "subscription": value["subscription"],
        "authority": False,
    }
    output["result_particle_hash"] = particle(output)
    return output

def perform(request):
    if not isinstance(request, dict) or set(request) != {"direction", "value"}:
        raise ValueError("REFUSE_INPUT")
    if request["direction"] == "source-to-target":
        result = source_to_target(request["value"])
    elif request["direction"] == "target-to-source":
        result = target_to_source(request["value"])
    else:
        raise ValueError("REFUSE_DIRECTION")
    return {"ok": True, "authority": False, "executed_effects": 0,
             "model_calls": 0, "result": result}

def main():
    raw = sys.stdin.read(MAX_INPUT_BYTES + 1)
    try:
        if not raw or len(raw.encode("utf-8")) > MAX_INPUT_BYTES:
            raise ValueError("REFUSE_SIZE")
        print(canonical(perform(parse(raw))))
        return 0
    except Exception as error:
        print(canonical({"ok": False, "authority": False, "executed_effects": 0,
                         "model_calls": 0,
                         "error": {"code": str(error), "message": "Static compatibility refused."}}))
        return 2

if __name__ == "__main__":
    raise SystemExit(main())
