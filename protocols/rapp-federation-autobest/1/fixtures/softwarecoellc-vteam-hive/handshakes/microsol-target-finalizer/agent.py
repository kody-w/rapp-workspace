"""Static MicroSOL Hive target-finalizer Lens.

Brainstem hotloads these exact bytes after a source handshake Lens. The agent
accepts only the source pass candidate and a pinned compatibility context, then
emits a target-shaped inert observation. Authority and successor signing remain
outside this file.
"""

from __future__ import annotations

import hashlib
import json
import re
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
MAX_SAFE_INTEGER = 2**53 - 1
MAX_DEPTH = 48
MAX_MEMBERS = 4096
HASH = re.compile(r"[0-9a-f]{64}\Z")
HEAD_KEYS = {"stream_id", "seq", "payload_hash", "frame_hash"}
CANDIDATE_KEYS = {
    "schema",
    "local_operation",
    "source_operation",
    "source_profile",
    "subject",
    "record",
    "inventory",
    "source_head",
    "source_occurrence",
    "authority",
    "result_particle_hash",
}

__manifest__ = {
    "schema": "rapp-agent/1.0",
    "name": "@kody-w/microsol-hive-target-finalizer",
    "version": "1.0.0",
    "display_name": "MicroSOL Hive target finalizer",
    "description": (
        "Finalize a source handshake candidate into a bounded MicroSOL Hive "
        "observation without effects or authority."
    ),
    "author": "kody-w",
    "tags": ["private-hive", "compatibility", "target-finalizer", "rapp1"],
    "category": "protocol",
    "quality_tier": "private",
    "access": "private",
    "dependencies": ["@rapp/basic_agent"],
    "requires_env": [],
    "record_role": "candidate",
    "authority": False,
    "runtime": "global-brainstem-jit-hotload",
    "target_profile": "microsol-repository-private-hive/1",
    "mutates_signed_source_in_place": False,
    "grants_authority": False,
}


class FinalizerRefusal(ValueError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


def _require(condition: bool, code: str, message: str) -> None:
    if not condition:
        raise FinalizerRefusal(code, message)


def _copy(value: Any, depth: int = 0) -> Any:
    _require(depth <= MAX_DEPTH, "REFUSE_DEPTH", "Input nesting exceeds the finalizer bound.")
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
            "Input arrays exceed the finalizer bound.",
        )
        return [_copy(item, depth + 1) for item in value]
    if type(value) is dict:
        _require(
            len(value) <= MAX_MEMBERS and all(type(key) is str for key in value),
            "REFUSE_OBJECT",
            "Bounded string-keyed JSON objects are required.",
        )
        return {key: _copy(item, depth + 1) for key, item in value.items()}
    raise FinalizerRefusal("REFUSE_TYPE", "Only plain JSON data is supported.")


def _pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        _require(key not in result, "REFUSE_JSON", "Duplicate JSON keys are forbidden.")
        result[key] = value
    return result


def _invalid_number(_value: str) -> Any:
    raise FinalizerRefusal("REFUSE_NUMBER", "Floats and nonfinite numbers are forbidden.")


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
        raise FinalizerRefusal("REFUSE_JSON", "Expected bounded unique-key UTF-8 JSON.") from error


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


def _head(value: Any) -> dict[str, Any]:
    _require(type(value) is dict and set(value) == HEAD_KEYS, "REFUSE_HEAD", "Exact head required.")
    _require(
        type(value["stream_id"]) is str
        and type(value["seq"]) is int
        and not isinstance(value["seq"], bool)
        and value["seq"] >= 0
        and all(type(value[key]) is str and HASH.fullmatch(value[key]) for key in HEAD_KEYS - {"stream_id", "seq"}),
        "REFUSE_HEAD",
        "Invalid source head.",
    )
    return value


def finalize(candidate_value: Any, context_value: Any) -> dict[str, Any]:
    candidate = parse(candidate_value)
    context = parse(context_value)
    _require(
        type(candidate) is dict and set(candidate) == CANDIDATE_KEYS,
        "REFUSE_CANDIDATE",
        "The exact source-Lens candidate is required.",
    )
    unsigned_candidate = {
        key: value for key, value in candidate.items() if key != "result_particle_hash"
    }
    _require(
        candidate["schema"] == "microsol-hive-compatible-observation/1"
        and candidate["authority"] is False
        and candidate["local_operation"] in {"evidence", "handoff"}
        and candidate["result_particle_hash"] == particle(unsigned_candidate),
        "REFUSE_CANDIDATE",
        "The source candidate does not reproduce.",
    )
    _head(candidate["source_head"])
    _require(
        type(context) is dict
        and set(context)
        == {
            "compatibility_intent_hash",
            "handshake_id",
            "handshake_sha256",
            "source_agent_sha256",
            "target_profile",
        }
        and type(context["compatibility_intent_hash"]) is str
        and HASH.fullmatch(context["compatibility_intent_hash"]) is not None
        and type(context["handshake_id"]) is str
        and type(context["handshake_sha256"]) is str
        and HASH.fullmatch(context["handshake_sha256"]) is not None
        and type(context["source_agent_sha256"]) is str
        and HASH.fullmatch(context["source_agent_sha256"]) is not None
        and context["target_profile"] == "microsol-repository-private-hive/1",
        "REFUSE_CONTEXT",
        "A pinned compatibility and target context is required.",
    )
    result = {
        "schema": "microsol-hive-observation/1",
        "operation": candidate["local_operation"],
        "subject": candidate["subject"],
        "source": {
            "profile": candidate["source_profile"],
            "operation": candidate["source_operation"],
            "head": candidate["source_head"],
            "occurrence": candidate["source_occurrence"],
        },
        "record": candidate["record"],
        "inventory": candidate["inventory"],
        "compatibility": context,
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
        "authority": False,
    }
    return {**result, "result_particle_hash": particle(result)}


class MicrosolHiveTargetFinalizerAgent(BasicAgent):
    metadata = {
        "name": "MicrosolHiveTargetFinalizer",
        "description": "Finalize a source Hive candidate into inert MicroSOL Hive observation data.",
        "parameters": {
            "type": "object",
            "properties": {
                "candidate": {"description": "Source-Lens candidate object or JSON."},
                "context": {"description": "Pinned compatibility context object or JSON."},
            },
            "required": ["candidate", "context"],
            "additionalProperties": False,
        },
    }

    def __init__(self) -> None:
        self.name = "MicrosolHiveTargetFinalizer"
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs: Any) -> str:
        try:
            _require(
                set(kwargs) == {"candidate", "context"},
                "REFUSE_INPUT",
                "Only candidate and context are accepted.",
            )
            result = finalize(kwargs["candidate"], kwargs["context"])
            return canonical(
                {
                    "ok": True,
                    "authority": False,
                    "executed_effects": 0,
                    "result": result,
                }
            )
        except (FinalizerRefusal, KeyError, TypeError, ValueError) as error:
            code = error.code if isinstance(error, FinalizerRefusal) else "REFUSE_INPUT"
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
        output = MicrosolHiveTargetFinalizerAgent().perform(**request)
        print(output)
        return 0 if parse(output).get("ok") is True else 2
    except (FinalizerRefusal, TypeError, ValueError) as error:
        code = error.code if isinstance(error, FinalizerRefusal) else "REFUSE_INPUT"
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
