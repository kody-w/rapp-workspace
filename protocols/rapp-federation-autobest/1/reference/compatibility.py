"""Strict compatibility-frame validation and deterministic static-agent compilation."""

from __future__ import annotations

import base64
import hashlib
import json
import os
import re
import subprocess
import unicodedata
from pathlib import Path
from typing import Any

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)
from jsonschema import Draft202012Validator

from schema_source import PROFILE


ROOT = Path(__file__).resolve().parents[1]
SCHEMA = json.loads((ROOT / "schema.json").read_text(encoding="utf-8"))
VALIDATORS = {
    name: Draft202012Validator({"$ref": "#/$defs/" + name, "$defs": SCHEMA["$defs"]})
    for name in (
        "frame",
        "compatibilityRecord",
        "exhaustRecord",
        "artifactBundle",
        "learningTrace",
        "lensSearch",
        "mutationOffer",
        "generationReceipt",
    )
}
HASH = re.compile(r"[0-9a-f]{64}\Z")
FRAME_KEYS = {
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
}
POLICY = {
    "schema": PROFILE + "/runtime-policy",
    "regular_files_only": True,
    "create_only": True,
    "overwrite": False,
    "symlinks": False,
    "hardlinks": False,
    "path_traversal": False,
    "brainstem_modified": False,
    "plugin_registry": False,
    "daemon": False,
}


class Refusal(ValueError):
    def __init__(self, code: str, detail: str = ""):
        super().__init__(detail or code)
        self.code = code


def require(condition: bool, code: str, detail: str = "") -> None:
    if not condition:
        raise Refusal(code, detail)


def _utf16(value: str) -> bytes:
    return value.encode("utf-16be", "surrogatepass")


def _check(value: Any, depth: int = 0) -> None:
    require(depth <= 64, "depth")
    if value is None or type(value) in (bool, str):
        if type(value) is str:
            require(unicodedata.normalize("NFC", value) == value, "nfc")
        return
    if type(value) is int:
        require(abs(value) <= (1 << 53) - 1, "number")
        return
    if type(value) is list:
        require(len(value) <= 65536, "members")
        for child in value:
            _check(child, depth + 1)
        return
    if type(value) is dict:
        require(len(value) <= 65536 and all(type(key) is str for key in value), "object")
        for key, child in value.items():
            _check(key, depth + 1)
            _check(child, depth + 1)
        return
    raise Refusal("type")


def canonical(value: Any) -> bytes:
    _check(value)

    def render(item: Any) -> str:
        if item is None:
            return "null"
        if item is True:
            return "true"
        if item is False:
            return "false"
        if type(item) is int:
            return str(item)
        if type(item) is str:
            return json.dumps(item, ensure_ascii=False, allow_nan=False)
        if type(item) is list:
            return "[" + ",".join(render(child) for child in item) + "]"
        if type(item) is dict:
            return "{" + ",".join(
                render(key) + ":" + render(item[key])
                for key in sorted(item, key=_utf16)
            ) + "}"
        raise Refusal("type")

    return render(value).encode("utf-8")


def _pairs(entries):
    result = {}
    for key, value in entries:
        require(key not in result, "duplicate-json-key")
        result[key] = value
    return result


def _noninteger(_value):
    raise Refusal("number")


def loads(raw: bytes):
    require(type(raw) is bytes and 0 < len(raw) <= (1 << 24), "size")
    try:
        value = json.loads(
            raw.decode("utf-8"),
            object_pairs_hook=_pairs,
            parse_float=_noninteger,
            parse_constant=_noninteger,
        )
    except (UnicodeError, json.JSONDecodeError, RecursionError) as error:
        raise Refusal("json") from error
    _check(value)
    return value


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def H(space: str, value: Any) -> str:
    return digest(space.encode("utf-8") + b"\n" + canonical(value))


def b64(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")


def unb64(text: str) -> bytes:
    require(type(text) is str, "base64")
    try:
        return base64.urlsafe_b64decode(text + "=" * (-len(text) % 4))
    except ValueError as error:
        raise Refusal("base64") from error


def spki_bytes(key: Ed25519PublicKey) -> bytes:
    return key.public_bytes(
        serialization.Encoding.DER,
        serialization.PublicFormat.SubjectPublicKeyInfo,
    )


def keyed_rappid(owner: str, slug: str, public_key: Ed25519PublicKey) -> str:
    return f"rappid:@{owner}/{slug}:{digest(b'rapp/1:rappid\\n' + spki_bytes(public_key))}"


def sign(value: dict[str, Any], identity: str, private_key: Ed25519PrivateKey) -> str:
    header = {"alg": "EdDSA", "b64": False, "crit": ["b64"], "kid": identity}
    encoded = b64(canonical(header))
    signature = private_key.sign(encoded.encode("ascii") + b"." + canonical(value))
    return encoded + ".." + b64(signature)


def verify_signature(value: dict[str, Any], signature: str, public_key: Ed25519PublicKey, identity: str) -> None:
    parts = signature.split(".")
    require(len(parts) == 3 and parts[1] == "", "signature")
    header = loads(unb64(parts[0]))
    require(header == {"alg": "EdDSA", "b64": False, "crit": ["b64"], "kid": identity}, "signature-header")
    try:
        public_key.verify(unb64(parts[2]), parts[0].encode("ascii") + b"." + canonical(value))
    except (InvalidSignature, ValueError) as error:
        raise Refusal("signature") from error


def unsigned(frame: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in frame.items() if key != "sig"}


def build_frame(
    payload: dict[str, Any],
    *,
    identity: str,
    private_key: Ed25519PrivateKey,
    stream: str,
    seq: int,
    utc: str,
    previous: dict[str, Any] | None = None,
) -> dict[str, Any]:
    frame = {
        "spec": "rapp/1",
        "kind": "memory.save",
        "stream_id": stream,
        "seq": seq,
        "utc": utc,
        "payload": payload,
        "payload_hash": H("rapp/1:particle", payload),
        "frame_hash": "",
        "prev": None if previous is None else previous["payload_hash"],
        "prev_wave": None,
        "sig": None,
    }
    wave = {key: value for key, value in frame.items() if key not in {"frame_hash", "sig"}}
    frame["frame_hash"] = H("rapp/1:wave", wave)
    frame["sig"] = sign(unsigned(frame), identity, private_key)
    return frame


def validate(value: Any, definition: str = "frame") -> Any:
    canonical(value)
    error = next(VALIDATORS[definition].iter_errors(value), None)
    require(error is None, "schema", str(error.message)[:300] if error else "")
    return value


def verify_frame(
    frame: dict[str, Any],
    *,
    public_key: Ed25519PublicKey,
    identity: str,
    previous: dict[str, Any] | None = None,
    profile: bool = True,
) -> None:
    if profile:
        validate(frame)
    else:
        canonical(frame)
        require(set(frame) == FRAME_KEYS, "frame-shape")
    require(set(frame) == FRAME_KEYS, "frame-shape")
    require(frame["payload_hash"] == H("rapp/1:particle", frame["payload"]), "payload-hash")
    wave = {key: value for key, value in frame.items() if key not in {"frame_hash", "sig"}}
    require(frame["frame_hash"] == H("rapp/1:wave", wave), "frame-hash")
    verify_signature(unsigned(frame), frame["sig"], public_key, identity)
    if previous is None:
        require(frame["seq"] == 0 and frame["prev"] is None, "genesis")
    else:
        require(
            frame["stream_id"] == previous["stream_id"]
            and frame["seq"] == previous["seq"] + 1
            and frame["prev"] == previous["payload_hash"]
            and frame["utc"] >= previous["utc"],
            "chain",
        )


def strict_file(path: Path) -> bytes:
    require(path.is_file() and not path.is_symlink(), "regular-file", str(path))
    raw = path.read_bytes()
    require(0 < len(raw) <= (1 << 24), "file-size", str(path))
    return raw


def check_relative(path: str) -> None:
    require(
        path
        and not path.startswith("/")
        and "\\" not in path
        and "//" not in path
        and all(part not in {"", ".", ".."} for part in path.split("/")),
        "path",
        path,
    )


def validate_artifact_bundle(bundle: dict[str, Any], files: dict[str, bytes]) -> None:
    validate(bundle, "artifactBundle")
    entries = bundle["entries"]
    require(entries == sorted(entries, key=lambda item: item["path"]), "entry-order")
    require(len({item["path"] for item in entries}) == len(entries), "entry-duplicate")
    require(set(files) == {item["path"] for item in entries}, "entry-inventory")
    for item in entries:
        check_relative(item["path"])
        raw = files[item["path"]]
        require(item["regular_file"] is True and len(raw) == item["bytes"] and digest(raw) == item["sha256"], "entry-bytes")
    lineage = bundle["lineage"]
    source_paths = [item["source_path"] for item in lineage["forward"]]
    successor_paths = [item["successor_path"] for item in lineage["reverse"]]
    require(len(source_paths) == len(set(source_paths)), "lineage-source-duplicate")
    require(len(successor_paths) == len(set(successor_paths)), "lineage-successor-duplicate")
    require(set(successor_paths) == set(files), "lineage-successor-coverage")
    require(
        lineage["roundtrip_claim"] is (lineage["ancestor_reconstruction"] == "lossless"),
        "lineage-roundtrip",
    )


def validate_learning_trace(trace: dict[str, Any]) -> None:
    validate(trace, "learningTrace")
    previous = None
    corrections = set()
    invariants = set()
    for index, event in enumerate(trace["events"]):
        body = {key: value for key, value in event.items() if key != "event_hash"}
        require(event["seq"] == index and event["prev_event_hash"] == previous, "trace-order")
        require(event["event_hash"] == H(PROFILE + ":trace-event", body), "trace-hash")
        if event["type"] == "user-correction":
            require(event["authority_class"] == "user-authoritative", "trace-authority")
            corrections.add(event["event_hash"])
        if event["type"] == "assistant-proposal":
            require(event["authority_class"] == "assistant-proposal", "trace-authority")
        if event["type"] == "successor-invariant":
            require(corrections <= set(event["references"]), "trace-correction-missing")
            invariants.add(event["event_hash"])
        previous = event["event_hash"]
    require(bool(corrections) and bool(invariants), "trace-closure")
    require(trace["correction_frontier_hash"] == H(PROFILE + ":correction-frontier", sorted(corrections)), "trace-frontier")


def validate_compatibility_record(
    record: dict[str, Any],
    bindings: dict[str, Any],
    handshake: dict[str, Any] | None = None,
) -> None:
    validate(record, "compatibilityRecord")
    require(record["handshake"]["sha256"] == bindings["wild_handshake"]["profile_sha256"], "handshake-pin")
    require(record["handshake"]["status"] == "owner-approved-private", "handshake-revoked")
    require(record["lens"]["source_agent"]["sha256"] == bindings["wild_handshake"]["source_agent_sha256"], "source-agent-pin")
    require(record["lens"]["target_agent"]["sha256"] == bindings["wild_handshake"]["target_finalizer_sha256"], "target-agent-pin")
    require(
        record["lens"]["generic_ceo_agent"]
        == {"role": "generic-ceo", "sha256": None, "bytes": None, "status": "pending"},
        "ceo-pending",
    )
    if handshake is not None:
        require(
            record["mapping_sha256"]
            == digest(
                canonical(
                    {
                        "source_to_target": handshake["source_to_target"],
                        "target_to_source": handshake["target_to_source"],
                    }
                )
            ),
            "mapping-pin",
        )
    supported = sum(item["status"] in {"verified", "available-on-exhaust"} for item in record["capabilities"])
    require(
        record["coverage"]["supported"] == supported
        and record["coverage"]["required"] == len(record["capabilities"])
        and record["coverage"]["basis_points"] == supported * 10000 // len(record["capabilities"]),
        "coverage",
    )
    receipts = record["lens"]["hotload_receipts"]
    require(
        [item["role"] for item in receipts].count("source-lens")
        == [item["role"] for item in receipts].count("target-finalizer")
        and all(
            item["model_calls"] == item["network_calls"] == item["executed_effects"] == 0
            and item["unloaded"]
            and not item["authority"]
            for item in receipts
        ),
        "hotload-receipts",
    )
    require(
        (record["previous_compatibility"] is None) == (record["trigger_exhaust"] is None),
        "successor-causality",
    )
    require(record["grants_authority"] is False, "authority")


def require_ceo_for_mutation(bindings: dict[str, Any]) -> None:
    candidate = bindings["generic_ceo_agent"]
    require(candidate["status"] == "verified" and candidate["sha256"] is not None, "ceo-agent-pending")


def run_agent(path: Path, request: dict[str, Any]) -> dict[str, Any]:
    raw = strict_file(path)
    environment = {
        "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
        "PYTHONDONTWRITEBYTECODE": "1",
        "PYTHONHASHSEED": "0",
        "LANG": "C",
        "LC_ALL": "C",
    }
    result = subprocess.run(
        [os.environ.get("PYTHON", "python3"), "-B", str(path)],
        input=canonical(request),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=environment,
        check=False,
        timeout=10,
    )
    require(result.returncode == 0, "agent-refusal", result.stderr.decode("utf-8", "replace")[:200])
    response = loads(result.stdout)
    require(response.get("ok") is True and response.get("executed_effects") == 0 and response.get("authority") is False, "agent-result")
    require(digest(raw) == digest(strict_file(path)), "agent-substitution")
    return response


def _static_mapping(handshake: dict[str, Any]) -> dict[str, Any]:
    return {
        "source_to_target": handshake["source_to_target"],
        "target_to_source": handshake["target_to_source"],
        "source_profile": handshake["source_match"]["profile"],
        "source_operations": sorted(handshake["source_match"]["required_operations"]),
        "target_profile": handshake["target"]["profile"],
    }


def compiler_bytes() -> bytes:
    return strict_file(Path(__file__))


def generate_static_agent(frame: dict[str, Any], handshake: dict[str, Any]) -> bytes:
    validate(frame)
    mapping = json.dumps(
        _static_mapping(handshake),
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    source = f'''"""Deterministic static RAPP compatibility agent. Generated; do not edit."""
from __future__ import annotations
import hashlib, json, sys

COMPATIBILITY_FRAME_HASH = {frame["frame_hash"]!r}
HANDSHAKE_SHA256 = {digest(canonical(handshake))!r}
MAPPING = json.loads({mapping!r})
FRAME_KEYS = {sorted(FRAME_KEYS)!r}
MAX_INPUT_BYTES = {1 << 20}

def pairs(items):
    out = {{}}
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
    return hashlib.sha256(b"rapp/1:particle\\n" + canonical(value).encode("utf-8")).hexdigest()

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
    head = {{"stream_id": frame["stream_id"], "seq": frame["seq"],
             "payload_hash": frame["payload_hash"], "frame_hash": frame["frame_hash"]}}
    context = {{"payload": payload, "head": head}}
    rules = MAPPING["source_to_target"][payload["operation"]]
    candidate = {{key: render(rule, context) for key, rule in rules.items()}}
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
            "handshake_sha256": HANDSHAKE_SHA256,
            "target_profile": MAPPING["target_profile"],
        }},
        "coverage": {{"mapped": True, "unknown_fields": [], "complete_for_operation": True}},
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
    if not isinstance(value, dict) or set(value) != {{"peer", "compatibility", "subscription"}}:
        raise ValueError("REFUSE_PEER_OFFER")
    output = {{
        "schema": "softwarecoellc-vteam-hive-peer-offer/1",
        "operation": "peer-offer",
        "peer": value["peer"],
        "compatibility": value["compatibility"],
        "subscription": value["subscription"],
        "authority": False,
    }}
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
    raw = sys.stdin.read(MAX_INPUT_BYTES + 1)
    try:
        if not raw or len(raw.encode("utf-8")) > MAX_INPUT_BYTES:
            raise ValueError("REFUSE_SIZE")
        print(canonical(perform(parse(raw))))
        return 0
    except Exception as error:
        print(canonical({{"ok": False, "authority": False, "executed_effects": 0,
                         "model_calls": 0,
                         "error": {{"code": str(error), "message": "Static compatibility refused."}}}}))
        return 2

if __name__ == "__main__":
    raise SystemExit(main())
'''
    return source.encode("utf-8")
