"""rapp-schema/1: the bare schema of a RAPP/1 frame (field names and types, never values).

Frozen. Any change to this function is a new schema version with a new version
string inside the schema object, so a schema particle can never silently change.
"""

from __future__ import annotations

from typing import Any

from . import rapp1
from .rapp1 import Refusal

VERSION = "rapp-schema/1"
TAG_KEYS = ("schema", "profile", "operation")
SCHEMA_MAX_BYTES = 8 * 1024 * 1024


def shape(value: Any) -> Any:
    """Objects stay objects; arrays list the distinct shapes of their elements; scalars become type names."""
    if type(value) is dict:
        return {key: shape(item) for key, item in value.items()}
    if type(value) is list:
        unique = {rapp1.canonical(item, limit=SCHEMA_MAX_BYTES): item for item in (shape(element) for element in value)}
        return [unique[key] for key in sorted(unique)]
    if value is None:
        return "null"
    if type(value) is bool:
        return "boolean"
    if type(value) is int:
        return "integer"
    if type(value) is str:
        return "string"
    raise Refusal("REFUSE_SCHEMA", "Only JSON values have a schema.")


def schema_of(frame: dict[str, Any]) -> dict[str, Any]:
    """Envelope spec and kind, the payload's string-valued discriminator tags, and the payload's shape."""
    payload = frame["payload"]
    if type(payload) is not dict:
        raise Refusal("REFUSE_FRAME_SHAPE", "Frame payloads are JSON objects.")
    return {
        "schema": VERSION,
        "spec": frame["spec"],
        "kind": frame["kind"],
        "tags": {key: payload[key] for key in TAG_KEYS if type(payload.get(key)) is str},
        "payload": shape(payload),
    }


def particle(schema: dict[str, Any]) -> str:
    return rapp1.particle(schema, limit=SCHEMA_MAX_BYTES)


def is_additive(new: dict[str, Any], old: dict[str, Any]) -> bool:
    """True when ``new`` only adds payload fields to ``old``: same envelope and tags, every old field unchanged."""
    if (new["schema"], new["spec"], new["kind"]) != (old["schema"], old["spec"], old["kind"]):
        return False
    if not rapp1.json_equal(new["tags"], old["tags"]):
        return False
    old_fields, new_fields = old["payload"], new["payload"]
    if not set(old_fields) < set(new_fields):
        return False
    return all(rapp1.json_equal(new_fields[key], old_fields[key]) for key in old_fields)
