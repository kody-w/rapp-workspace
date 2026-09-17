"""Static SoftwareCo V-team Hive handshake Lens.

The global Brainstem may hotload these exact pinned bytes as one pass in a
compatibility crossing. This file transforms inert application data only. It
does not read files, verify authority, launch tools, or mutate a signed source
Frame in place.
"""

from __future__ import annotations

import hashlib
import json
import sys
from typing import Any

try:
    from agents.basic_agent import BasicAgent
except ImportError:
    try:
        from basic_agent import BasicAgent
    except ImportError:
        class BasicAgent:  # type: ignore[no-redef]
            def __init__(self, name: str | None = None, metadata: dict[str, Any] | None = None):
                if name is not None:
                    self.name = name
                if metadata is not None:
                    self.metadata = metadata


MAX_INPUT_BYTES = 1024 * 1024
MAX_DEPTH = 48
MAX_MEMBERS = 4096
MAX_SAFE_INTEGER = 2**53 - 1
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
PAYLOAD_KEYS = {
    "authority",
    "inventory",
    "operation",
    "profile",
    "project",
    "record",
    "request_hash",
    "request_id",
    "sequence",
}

__manifest__ = {
    "schema": "rapp-agent/1.0",
    "name": "@kody-w/softwarecoellc-vteam-hive-handshake",
    "version": "1.0.0",
    "display_name": "SoftwareCo V-team Hive handshake",
    "description": (
        "Static bidirectional data Lens for the first learned wild-Hive "
        "microsol-project/1 handshake."
    ),
    "author": "kody-w",
    "tags": ["private-hive", "handshake", "compatibility", "rapp1", "static-lens"],
    "category": "protocol",
    "quality_tier": "private",
    "access": "private",
    "dependencies": ["@rapp/basic_agent"],
    "requires_env": [],
    "record_role": "candidate",
    "authority": False,
    "runtime": "global-brainstem-jit-hotload",
    "source_profile": "microsol-project/1",
    "target_profile": "microsol-repository-private-hive/1",
    "mutates_signed_source_in_place": False,
    "grants_authority": False,
}


class HandshakeRefusal(ValueError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


def _require(condition: bool, code: str, message: str) -> None:
    if not condition:
        raise HandshakeRefusal(code, message)


def _copy(value: Any, depth: int = 0) -> Any:
    _require(depth <= MAX_DEPTH, "REFUSE_DEPTH", "Input nesting exceeds the Lens bound.")
    if value is None or type(value) in (bool, str):
        return value
    if type(value) is int:
        _require(
            abs(value) <= MAX_SAFE_INTEGER,
            "REFUSE_NUMBER",
            "Only finite IEEE-754-safe integers are supported.",
        )
        return value
    if type(value) is list:
        _require(
            len(value) <= MAX_MEMBERS,
            "REFUSE_MEMBERS",
            "Input arrays exceed the Lens bound.",
        )
        return [_copy(item, depth + 1) for item in value]
    if type(value) is dict:
        _require(
            len(value) <= MAX_MEMBERS and all(type(key) is str for key in value),
            "REFUSE_OBJECT",
            "Bounded string-keyed JSON objects are required.",
        )
        return {key: _copy(item, depth + 1) for key, item in value.items()}
    raise HandshakeRefusal(
        "REFUSE_TYPE",
        "Only plain JSON strings, integers, booleans, null, arrays, and objects are supported.",
    )


def _pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        _require(key not in result, "REFUSE_JSON", "Duplicate JSON keys are forbidden.")
        result[key] = value
    return result


def _invalid_number(_value: str) -> Any:
    raise HandshakeRefusal("REFUSE_NUMBER", "Floats and nonfinite numbers are forbidden.")


def parse(value: Any) -> Any:
    if type(value) is not str:
        return _copy(value)
    raw = value.encode("utf-8")
    _require(0 < len(raw) <= MAX_INPUT_BYTES, "REFUSE_SIZE", "Input JSON is empty or oversized.")
    try:
        return _copy(
            json.loads(
                value,
                object_pairs_hook=_pairs,
                parse_float=_invalid_number,
                parse_constant=_invalid_number,
            )
        )
    except (UnicodeError, json.JSONDecodeError, RecursionError) as error:
        raise HandshakeRefusal("REFUSE_JSON", "Expected bounded unique-key UTF-8 JSON.") from error


def canonical(value: Any) -> str:
    return json.dumps(
        _copy(value),
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def particle(value: Any) -> str:
    return hashlib.sha256(
        b"rapp/1:particle\n" + canonical(value).encode("utf-8")
    ).hexdigest()


def head(frame: dict[str, Any]) -> dict[str, Any]:
    return {
        "stream_id": frame["stream_id"],
        "seq": frame["seq"],
        "payload_hash": frame["payload_hash"],
        "frame_hash": frame["frame_hash"],
    }


def source_to_target(value: Any) -> dict[str, Any]:
    frame = parse(value)
    _require(
        type(frame) is dict and set(frame) == FRAME_KEYS,
        "REFUSE_FRAME",
        "An exact RAPP/1 Frame object is required.",
    )
    payload = frame["payload"]
    _require(
        frame["spec"] == "rapp/1"
        and frame["kind"] == "memory.save"
        and type(payload) is dict
        and set(payload) == PAYLOAD_KEYS
        and payload["profile"] == "microsol-project/1"
        and payload["operation"] in {"open", "publish"}
        and payload["sequence"] == frame["seq"],
        "REFUSE_PROFILE",
        "The Frame does not match the learned SoftwareCo V-team Hive profile.",
    )
    local_operation = "evidence" if payload["operation"] == "open" else "handoff"
    result = {
        "schema": "microsol-hive-compatible-observation/1",
        "local_operation": local_operation,
        "source_operation": payload["operation"],
        "source_profile": payload["profile"],
        "subject": payload["project"],
        "record": payload["record"],
        "inventory": payload["inventory"],
        "source_head": head(frame),
        "source_occurrence": {
            "stream_id": frame["stream_id"],
            "seq": frame["seq"],
            "frame_hash": frame["frame_hash"],
        },
        "authority": False,
    }
    return {**result, "result_particle_hash": particle(result)}


def target_to_source(value: Any) -> dict[str, Any]:
    record = parse(value)
    _require(
        type(record) is dict
        and set(record) == {"peer", "compatibility", "subscription"}
        and all(type(record[key]) is dict for key in record),
        "REFUSE_PEER_OFFER",
        "A peer, compatibility, and subscription object are required.",
    )
    result = {
        "schema": "softwarecoellc-vteam-hive-peer-offer/1",
        "operation": "peer-offer",
        "peer": record["peer"],
        "compatibility": record["compatibility"],
        "subscription": record["subscription"],
        "authority": False,
    }
    return {**result, "result_particle_hash": particle(result)}


def transform(direction: str, value: Any) -> dict[str, Any]:
    if direction == "source-to-target":
        return source_to_target(value)
    if direction == "target-to-source":
        return target_to_source(value)
    raise HandshakeRefusal(
        "REFUSE_DIRECTION",
        "Direction must be source-to-target or target-to-source.",
    )


class SoftwareCoVTeamHiveHandshakeAgent(BasicAgent):
    metadata = {
        "name": "SoftwareCoVTeamHiveHandshake",
        "description": (
            "Transform inert data between the learned SoftwareCo V-team Hive "
            "microsol-project/1 shape and a MicroSOL compatibility observation."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "direction": {
                    "type": "string",
                    "enum": ["source-to-target", "target-to-source"],
                },
                "value": {
                    "description": "Plain JSON object or encoded JSON text.",
                },
            },
            "required": ["direction", "value"],
            "additionalProperties": False,
        },
    }

    def __init__(self) -> None:
        self.name = "SoftwareCoVTeamHiveHandshake"
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs: Any) -> str:
        try:
            _require(
                set(kwargs) == {"direction", "value"},
                "REFUSE_INPUT",
                "Only direction and value are accepted.",
            )
            result = transform(kwargs["direction"], kwargs["value"])
            return canonical(
                {
                    "ok": True,
                    "authority": False,
                    "executed_effects": 0,
                    "result": result,
                }
            )
        except (HandshakeRefusal, KeyError, TypeError, ValueError) as error:
            code = error.code if isinstance(error, HandshakeRefusal) else "REFUSE_INPUT"
            return canonical(
                {
                    "ok": False,
                    "authority": False,
                    "executed_effects": 0,
                    "error": {
                        "code": code,
                        "message": str(error),
                    },
                }
            )


def main() -> int:
    raw = sys.stdin.read(MAX_INPUT_BYTES + 1)
    if not raw:
        print(
            canonical(
                {
                    "manifest": __manifest__,
                    "authority": False,
                    "hotloaded": False,
                    "executed_effects": 0,
                }
            )
        )
        return 0
    if len(raw.encode("utf-8")) > MAX_INPUT_BYTES:
        print(
            canonical(
                {
                    "ok": False,
                    "authority": False,
                    "executed_effects": 0,
                    "error": {
                        "code": "REFUSE_SIZE",
                        "message": "Input JSON is oversized.",
                    },
                }
            )
        )
        return 2
    try:
        request = parse(raw)
        _require(type(request) is dict, "REFUSE_INPUT", "A request object is required.")
        output = SoftwareCoVTeamHiveHandshakeAgent().perform(**request)
        print(output)
        return 0 if parse(output).get("ok") is True else 2
    except (HandshakeRefusal, TypeError, ValueError) as error:
        code = error.code if isinstance(error, HandshakeRefusal) else "REFUSE_INPUT"
        print(
            canonical(
                {
                    "ok": False,
                    "authority": False,
                    "executed_effects": 0,
                    "error": {
                        "code": code,
                        "message": str(error),
                    },
                }
            )
        )
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
