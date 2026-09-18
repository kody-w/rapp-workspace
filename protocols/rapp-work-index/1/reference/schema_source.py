"""Closed Draft 2020-12 application schemas; this is not a RAPP/1 wire schema."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

PROFILE = "rapp-work-index/1"
GENERATED_UTC = "2026-09-17T21:36:39.234Z"
SHARDS = 16
PROOF_DEPTH = 4
MAX_SHARD_ITEMS = 256
MAX_ITEMS = SHARDS * MAX_SHARD_ITEMS
MAX_SHARD_BYTES = 256 * 1024
MAX_TOTAL_BYTES = SHARDS * MAX_SHARD_BYTES
MAX_CONTENT_BYTES = 1024 * 1024
MAX_MANIFEST_BYTES = 128 * 1024
MAX_SOURCES = 64
MAX_PAGE_SIZE = 64
MAX_TOKEN_BYTES = 4096
MAX_DB_BYTES = 16 * 1024 * 1024
MAX_OPERATIONS = 256
MAX_SQL_STEPS = 5_000_000
MAX_JSON_NODES = 100_000
MAX_JSON_DEPTH = 16
MAX_INT = 2**53 - 1
ROOT = Path(__file__).resolve().parents[1]


def obj(**properties):
    return {
        "type": "object",
        "additionalProperties": False,
        "required": list(properties),
        "properties": properties,
    }


def fixed(value):
    return {"const": value}


def text(pattern=r"^[ -~]+$", minimum=1, maximum=128):
    # JSON Schema regex '$' alone can match before a final newline.
    if pattern.endswith("$"):
        pattern += r"(?![\s\S])"
    return {"type": "string", "minLength": minimum, "maxLength": maximum, "pattern": pattern}


def uint(maximum=MAX_INT, minimum=0):
    return {"type": "integer", "minimum": minimum, "maximum": maximum}


def array(items, maximum, minimum=0):
    return {"type": "array", "items": items, "minItems": minimum, "maxItems": maximum}


def ref(name):
    return {"$ref": "#/$defs/" + name}


HEX = text(r"^[0-9a-f]{64}$", 64, 64)
LABEL = text(r"^[a-z][a-z0-9.-]*$", 1, 64)
KEY = text(r"^[!-~]+$", 1, 128)
RAPPID = text(
    r"^rappid:@(?=[a-z0-9-]{1,39}/)[a-z0-9]+(?:-[a-z0-9]+)*/"
    r"(?=[a-z0-9-]{1,100}:)[a-z0-9]+(?:-[a-z0-9]+)*:[0-9a-f]{64}$",
    76,
    213,
)
STREAM = text(r"^[!-~]+$", 1, 256)


def schema():
    identity = {
        "rappid": RAPPID,
        "content_sha256": HEX,
        "content_bytes": uint(MAX_CONTENT_BYTES),
        "particle_hash": HEX,
        "occurrence_hash": HEX,
    }
    context = obj(
        signer=RAPPID,
        spki_sha256=HEX,
        stream=STREAM,
        key_epoch=uint(),
        registry_epoch=uint(),
        registry_root=HEX,
        policy_root=HEX,
        grant_root=HEX,
        revocation_root=HEX,
        subscription_root=HEX,
        context_root=HEX,
    )
    source = obj(
        source=LABEL,
        subject=RAPPID,
        raw_sha256=HEX,
        raw_bytes=uint(MAX_CONTENT_BYTES),
        signer=RAPPID,
        spki_sha256=HEX,
        stream=STREAM,
        seq=uint(),
        key_epoch=uint(),
        registry_epoch=uint(),
        payload_hash=HEX,
        frame_hash=HEX,
        frame_sha256=HEX,
        policy_root=HEX,
        registry_root=HEX,
    )
    payload = obj(
        schema=fixed(PROFILE + "/checkpoint"),
        generation=uint(),
        manifest_sha256=HEX,
        root=HEX,
        context_sha256=HEX,
        source_vector_sha256=HEX,
        authority=fixed(False),
    )
    occurrence = {
        "signer": RAPPID,
        "spki_sha256": HEX,
        "stream": STREAM,
        "key_epoch": uint(),
        "registry_epoch": uint(),
        "seq": uint(),
        "payload_hash": HEX,
        "frame_hash": HEX,
        "frame_sha256": HEX,
    }
    definitions = {
        "identity": obj(**identity),
        "query": obj(domain=LABEL, key=KEY),
        "record": obj(
            schema=fixed(PROFILE + "/record"), domain=LABEL, key=KEY, **identity
        ),
        "context": context,
        "source": source,
        "source-vector": array(ref("source"), MAX_SOURCES),
        "shard": obj(
            schema=fixed(PROFILE + "/shard"),
            shard=uint(SHARDS - 1),
            records=array(ref("record"), MAX_SHARD_ITEMS),
        ),
        "descriptor": obj(
            shard=uint(SHARDS - 1),
            sha256=HEX,
            bytes=uint(MAX_SHARD_BYTES, 1),
            items=uint(MAX_SHARD_ITEMS),
            leaf_hash=HEX,
        ),
        "generation": obj(
            schema=fixed(PROFILE + "/generation"),
            generation=uint(),
            root=HEX,
            context=ref("context"),
            source_vector=ref("source-vector"),
            shards=array(ref("descriptor"), SHARDS, SHARDS),
            total_items=uint(MAX_ITEMS),
            total_bytes=uint(MAX_TOTAL_BYTES),
            authority=fixed(False),
        ),
        "proof": obj(
            schema=fixed(PROFILE + "/proof"),
            manifest_sha256=HEX,
            root=HEX,
            shard=uint(SHARDS - 1),
            leaf_hash=HEX,
            siblings=array(HEX, PROOF_DEPTH, PROOF_DEPTH),
        ),
        "checkpoint": payload,
        "verified-frame": obj(
            schema=fixed(PROFILE + "/verified-frame"),
            verification=fixed("external-canonical-rapp/1"),
            kind=fixed("memory.save"),
            signature_verified=fixed(True),
            chain_verified=fixed(True),
            context=ref("context"),
            payload=ref("checkpoint"),
            **occurrence,
        ),
        "binding": obj(
            schema=fixed(PROFILE + "/binding"),
            generation=uint(),
            manifest_sha256=HEX,
            root=HEX,
            context_sha256=HEX,
            source_vector_sha256=HEX,
            authority=fixed(False),
            **occurrence,
        ),
        "frontier": obj(
            schema=fixed(PROFILE + "/frontier"),
            context=ref("context"),
            source_vector=ref("source-vector"),
            manifest_sha256=HEX,
            checkpoint_frame_hash=HEX,
            checkpoint_frame_sha256=HEX,
        ),
        "cursor": obj(
            schema=fixed(PROFILE + "/cursor"),
            generation=uint(),
            manifest_sha256=HEX,
            root=HEX,
            binding_sha256=HEX,
            checkpoint_frame_hash=HEX,
            domain=LABEL,
            key=KEY,
            shard=uint(SHARDS - 1),
            after=ref("identity"),
            page_size=uint(MAX_PAGE_SIZE, 1),
        ),
        "token": obj(cursor=ref("cursor"), checksum=HEX),
        "anti-entropy": obj(
            schema=fixed(PROFILE + "/anti-entropy"),
            local_manifest_sha256=HEX,
            target_manifest_sha256=HEX,
            target_generation=uint(),
            target_root=HEX,
            changed=array(
                obj(shard=uint(SHARDS - 1), local_sha256=HEX, target_sha256=HEX), SHARDS
            ),
            missing=array(obj(shard=uint(SHARDS - 1), target_sha256=HEX), SHARDS),
            divergent=array(
                obj(
                    shard=uint(SHARDS - 1),
                    local_sha256=HEX,
                    observed_sha256=HEX,
                    target_sha256=HEX,
                ),
                SHARDS,
            ),
            available_needs_proof=array(
                obj(shard=uint(SHARDS - 1), sha256=HEX), SHARDS
            ),
            authority=fixed(False),
        ),
        "adapter": obj(
            name=LABEL,
            status={"enum": ["reference", "mapping-only"]},
            platforms=array(LABEL, 4, 1),
            stores=array(KEY, 4, 1),
            optimizations=array(KEY, 4),
            verification=fixed("identical-canonical-shards-and-external-checkpoint"),
            authority=fixed(False),
            resident_processes=fixed(0),
            polling=fixed(False),
            network=fixed(False),
        ),
    }
    tagged = (
        "record", "shard", "generation", "proof", "checkpoint", "verified-frame",
        "binding", "frontier", "cursor", "anti-entropy",
    )
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "urn:rapp-work-index:1:schema",
        "title": "RAPP Work Index/1 (non-authoritative application data)",
        "oneOf": [ref(name) for name in tagged],
        "$defs": definitions,
    }


def encoded():
    return (json.dumps(schema(), indent=2, ensure_ascii=True) + "\n").encode("ascii")


def check():
    if not (ROOT / "schema.json").is_file() or (ROOT / "schema.json").read_bytes() != encoded():
        raise ValueError("schema.json differs from its closed generated source")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.write:
        (ROOT / "schema.json").write_bytes(encoded())
    check()
    print("rapp-work-index/1 schema: exact generated match")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
