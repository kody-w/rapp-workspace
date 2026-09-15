"""Closed Workspace/1 core safety-kernel contracts; no experimental version aliases."""

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROFILE = "rapp-workspace/1"
DRAFT = "https://json-schema.org/draft/2020-12/schema"
URI = "https://github.com/kody-w/rapp-workspace/raw/main/protocols/rapp-workspace/1/schemas/"
GUARANTEES = ("rapp_integrity", "observation", "semantic_fidelity", "current_authorization", "safe_deployment")
RIGHTS = ("capture", "local_synthesis", "model_submission", "retention", "redistribution",
          "adoption", "materialization", "execution")


def obj(**props):
    return {"type": "object", "properties": props, "required": list(props), "additionalProperties": False}


def text(limit=512, minimum=0, pattern=r"^[^\u0000-\u001f\u007f]*$"):
    return {"type": "string", "minLength": minimum, "maxLength": limit, "pattern": pattern + r"(?![\s\S])"}


def integer(maximum=2**53 - 1, minimum=0):
    return {"type": "integer", "minimum": minimum, "maximum": maximum}


def array(items, maximum=128, minimum=0):
    return {"type": "array", "items": items, "minItems": minimum, "maxItems": maximum, "uniqueItems": True}


def ref(name):
    return {"$ref": "common.schema.json#/$defs/" + name}


def fixed(value):
    return {"const": value}


def nullable(schema):
    return {"oneOf": [schema, {"type": "null"}]}


def record(name, **props):
    return obj(schema=fixed(PROFILE + "/" + name), instance_rappid=ref("rappid"), world_id=text(128, 1),
               native_subject=ref("subject"), restrictions=ref("restrictions"), **props)


def schemas():
    hash_value = text(64, 64, r"^[0-9a-f]{64}$")
    address = lambda space: obj(space=fixed(space), hash=hash_value)
    rid = text(213, 76, r"^rappid:@(?=[^/]{1,39}/)[a-z0-9]+(?:-[a-z0-9]+)*/(?=[^:]{1,100}:)[a-z0-9]+(?:-[a-z0-9]+)*:[0-9a-f]{64}$")
    restrictions = obj(
        rights=obj(**{right: {"type": "boolean"} for right in RIGHTS}),
        privacy=fixed("godd"), hashes_sensitive=fixed(True),
        deletion=fixed("no-guaranteed-recall"), retention=fixed("append-only-local"),
        audience=array(text(128, 1), 32, 1))
    b64 = text(87384, 0, r"^(?:[A-Za-z0-9+/]{4})*(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?$")
    read = obj(kind={"enum": ["content", "negative", "enumeration", "environment"]},
               selector=text(512), expected=hash_value)
    common = {
        "$schema": DRAFT, "$id": URI + "common.schema.json",
        "$defs": {
            "hash": hash_value, "rappid": rid, "subject": obj(namespace=text(128, 1), native_key=text(256, 1)),
            "wave": address("rapp/1:wave"), "particle": address("rapp/1:particle"),
            "restrictions": restrictions, "read": read,
            "frontier": obj(instance_rappid=rid, world_id=text(128, 1), policy=address("rapp/1:particle"),
                            graph_head=nullable(address("rapp/1:wave")),
                            adoption_head=nullable(address("rapp/1:wave")), routing_head=nullable(address("rapp/1:wave")),
                            suppressions=address("rapp/1:particle"), source_bindings=address("rapp/1:particle"),
                            runtime_sha256=hash_value, sequence=integer()),
        },
        "type": "object", "properties": {}, "required": [], "additionalProperties": False,
    }
    records = {
        "seed": record("seed", generation=fixed("workspace1-core"), spec_sha256=ref("hash"),
                       immutable_invariants=fixed(True), effect_authority=fixed("external-controller-only")),
        "observation": record(
            "observation", content=ref("particle"), octets_b64=b64, octets_sha256=ref("hash"),
            octets_count=integer(65536), subject_binding=ref("particle"),
            consistency={"enum": ["supplied-immutable-octets", "stable-descriptor-not-coherent"]},
            scope=fixed("captured-octets-only"), complete={"type": "boolean"}, native_rebinding=fixed(False)),
        "lens-request": record(
            "lens-request", source=ref("wave"), operation={"enum": ["identity-octets", "json-field"]},
            field=text(256), runtime_sha256=ref("hash"), synthesis_reads=array(ref("read"), 64),
            necessary_reads=array(ref("read"), 64), grants_authority=fixed(False)),
        "derivation": record(
            "derivation", sources=array(ref("wave"), 64, 1), lens=ref("wave"), result_b64=b64,
            result_sha256=ref("hash"), runtime_sha256=ref("hash"), actual_reads=array(ref("read"), 64),
            necessary_reads=array(ref("read"), 64), synthesis_reads=array(ref("read"), 64),
            negative_reads=array(ref("read"), 64), enumerations=array(ref("read"), 64),
            environment=array(ref("read"), 0), portable=fixed(True), native_rebinding=fixed(False)),
        "refusal": record(
            "refusal", parents=array(ref("wave"), 64), operation=text(128, 1), code=text(128, 1),
            safe_to_retry={"type": "boolean"}, grants_authority=fixed(False)),
        "adoption-request": record(
            "adoption-request", candidate=ref("wave"), integrity=ref("wave"), observation=ref("wave"),
            fidelity=ref("wave"), contract=ref("particle"),
            frontier=ref("frontier"), operation_id=text(128, 1), grants_authority=fixed(False)),
        "adoption-record": record(
            "adoption-record", request=ref("wave"), candidate=ref("wave"), operation_id=text(128, 1),
            controller_epoch=integer(), frontier=ref("frontier"), data_only=fixed(True),
            external_effects=fixed(False)),
        "scheduler-exhaust": record(
            "scheduler-exhaust", parents=array(ref("wave"), 64), work=ref("particle"), root=ref("wave"),
            depth=integer(32), attempts=integer(128), reason=text(128, 1), progress={"type": "boolean"},
            terminal={"type": "boolean"}, remaining_frames=integer(512), reserved_stop=fixed(True)),
        "catalog-shard": record(
            "catalog-shard", source=ref("wave"), catalog_id=text(128, 1), root_id=text(512, 1),
            shard_index=integer(31), shard_count=integer(32, 1),
            snapshot_sha256=ref("hash"), branch_scope=fixed("default-branch-only"),
            branch_evidence_status=fixed("external-host-observation-unproven"),
            recursive={"type": "boolean"},
            entry_ids=array(text(512, 1), 256, 1), entry_count=integer(256, 1),
            source_sha256=ref("hash"), grants_authority=fixed(False)),
        "organization-assessment": record(
            "organization-assessment", tree_sources=array(ref("wave"), 32, 1),
            catalog_shards=array(ref("wave"), 32, 1), catalog_id=text(128, 1),
            snapshot_sha256=ref("hash"), tree_id=text(128, 1),
            tree_snapshot_sha256=ref("hash"), root_group=text(64, 1),
            entry_count=integer(10000),
            assigned_count=integer(10000), group_count=integer(512, 1),
            max_depth=integer(32), largest_bucket=integer(10000),
            max_bucket=integer(10000, 1), allowed_depth=integer(32, 1),
            unassigned=integer(10000), duplicate_assignments=integer(10000),
            unknown_assignments=integer(10000), refinement_round=integer(32),
            previous=nullable(ref("wave")),
            status={"enum": ["verified", "needs-refinement", "no-progress"]},
            progress={"type": "boolean"}, grants_authority=fixed(False)),
        "outcome-resolution": record(
            "outcome-resolution", assessment=ref("wave"), query_sha256=ref("hash"),
            selected_ids=array(text(512, 1), 1024),
            status={"enum": ["candidate", "unresolved"]},
            semantic_fidelity=fixed("unproven"), grants_authority=fixed(False)),
        "subscription-proposal": record(
            "subscription-proposal", assessment=ref("wave"),
            target=fixed("rapp-private-hive"),
            selected_ids=array(text(512, 1), 1024),
            withheld_private=integer(10000), withheld_excluded=integer(10000),
            externally_approved_private=integer(10000),
            external_owner_approval_required=fixed(True),
            publication_authorized=fixed(False), grants_authority=fixed(False)),
    }
    for guarantee in GUARANTEES:
        records[guarantee + "-receipt"] = record(
            guarantee + "-receipt", guarantee=fixed(guarantee), subject=ref("wave"),
            status={"enum": ["verified", "unproven", "refused", "expired", "historical"]},
            scope=text(256, 1), method=text(128, 1), validator_spec=fixed(PROFILE),
            validator_pin=ref("hash"), runtime_sha256=ref("hash"), evidence=ref("particle"),
            authorizes_other_guarantees=fixed(False))
    return {"common.schema.json": common, **{
        name + ".schema.json": {"$schema": DRAFT, "$id": URI + name + ".schema.json", **value}
        for name, value in records.items()}}


def encoded(value):
    return (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    bad = []
    for name, value in schemas().items():
        path = ROOT / "schemas" / name
        raw = encoded(value)
        if args.check:
            if not path.is_file() or path.read_bytes() != raw:
                bad.append(name)
        else:
            path.write_bytes(raw)
    bad += sorted({p.name for p in (ROOT / "schemas").glob("*.json")} - schemas().keys())
    print(f"{len(schemas())} Workspace/1 core schemas | " + ("FAIL " + ", ".join(bad) if bad else "PASS"))
    return bool(bad)


if __name__ == "__main__":
    raise SystemExit(main())
