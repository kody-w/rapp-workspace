"""Generate the first Workspace Grail/1 payload schemas; not a RAPP primitive."""

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROFILE = "rapp-workspace/1.0"
GENERATION = "grail"
CONTROL_DIR = ".workspace-grail"
LEGACY_LABELS = ["rapp-workspace/1.0", "rapp-workspace/1.1", "rapp-workspace/2.0"]
DRAFT = "https://json-schema.org/draft/2020-12/schema"
URI = "https://github.com/kody-w/rapp-workspace/raw/main/protocols/rapp-workspace/1.0/schemas/"
NEGATIVES = [
    "incomplete-reads", "read-substitution", "source-tamper",
    "context-substitution", "world-substitution", "result-substitution",
]


def obj(**properties):
    return {"type": "object", "properties": properties,
            "required": list(properties), "additionalProperties": False}


def text(limit=256, minimum=1, pattern=r"^[^\u0000-\u001f\u007f]*$"):
    return {"type": "string", "minLength": minimum, "maxLength": limit,
            "pattern": pattern + r"(?![\s\S])"}


def array(items, maximum=128, minimum=0, unique=True):
    return {"type": "array", "items": items, "minItems": minimum,
            "maxItems": maximum, "uniqueItems": unique}


def integer(maximum=2**53 - 1, minimum=0):
    return {"type": "integer", "minimum": minimum, "maximum": maximum}


def ref(name):
    return {"$ref": "common.schema.json#/$defs/" + name}


def nullable(schema):
    return {"oneOf": [schema, {"type": "null"}]}


def fixed(value):
    return {"const": value}


def record(name, **properties):
    return obj(schema=fixed(PROFILE + "/" + name), generation=fixed(GENERATION), estate_rappid=ref("rappid"),
               world_id=text(128), seed=ref("wave"), **properties)


def schemas():
    hexadecimal = text(64, 64, r"^[0-9a-f]{64}$")
    rappid = text(212, 76, r"^rappid:@(?=[^/]{1,39}/)[a-z0-9]+(?:-[a-z0-9]+)*/(?=[^:]{1,100}:)[a-z0-9]+(?:-[a-z0-9]+)*:[0-9a-f]{64}$")
    # This deliberately narrower portable path alphabet is not a new RAPP path grammar.
    path = text(512, 1, r"^(?!.*(?:^|/)(?:\.{1,2}|[Cc][Oo][Nn](?:\.[^/]*)?|[Pp][Rr][Nn](?:\.[^/]*)?|[Aa][Uu][Xx](?:\.[^/]*)?|[Nn][Uu][Ll](?:\.[^/]*)?|[Cc][Oo][Mm][1-9](?:\.[^/]*)?|[Ll][Pp][Tt][1-9](?:\.[^/]*)?)(?:/|$))(?!.*[. ](?:/|$))[A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.-]+)*$")
    atom = {"oneOf": [text(1024, 0), integer(minimum=-(2**53 - 1)),
                       {"type": "boolean"}, {"type": "null"}]}
    address = lambda space: obj(space=fixed(space), hash=hexadecimal)
    read = obj(name=text(), input=integer(127), pointer=text(512, 0, r"^(?:/(?:[^~/\u0000-\u001f\u007f]|~[01])*)*$"))
    file_entry = obj(path=path, kind={"enum": ["file", "symlink", "directory"]},
                     sha256=hexadecimal, bytes=integer(16 * 1024 * 1024),
                     mode=integer(4095))
    fact = obj(name=text(), value=atom)
    b64 = text(5464, 0, r"^(?:[A-Za-z0-9+/]{4})*(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?$")
    local_entry = obj(
        path_b64=b64, kind={"enum": ["file", "directory", "symlink", "special"]},
        mode=integer(65535), bytes=nullable(integer(16 * 1024 * 1024)),
        sha256=nullable(hexadecimal), octets_b64=nullable(b64),
        coverage={"enum": ["inline", "digest-only", "metadata-only"]})
    programs = [
        obj(op=fixed("identity"), read=read),
        obj(op=fixed("project"), tick=integer(), bindings=array(obj(name=text(), read=read), 64, 1)),
        obj(op=fixed("amend"), read=read,
            changes=array(obj(pointer=read["properties"]["pointer"], value=atom), 64, 1)),
        obj(op=fixed("workspace-attempt"), read=read, context_read=read, tick=integer(),
            members=array(integer(127), 64)),
        obj(op=fixed("workspace-context-attempt"), reads=array(read, 5, 5), tick=integer(),
            repair_code=text(128), members=array(integer(127), 64)),
    ]
    common = {
        "$schema": DRAFT, "$id": URI + "common.schema.json",
        "$defs": {
            "hash": hexadecimal, "rappid": rappid, "path": path, "atom": atom,
            "wave": address("rapp/1:wave"), "particle": address("rapp/1:particle"),
            "egg": address("rapp/1:egg-manifest"), "fact": fact,
            "read": read, "file": file_entry,
            "program": {"oneOf": programs},
            "head": obj(stream_id=rappid, seq=integer(), frame=address("rapp/1:wave")),
            "comparison": obj(base=address("rapp/1:wave"), conflicts=array(text(), 64)),
        },
        "description": "Definitions only; address spaces and identities are exclusively RAPP/1.",
        "type": "object", "properties": {}, "required": [], "additionalProperties": False,
    }
    wave = ref("wave")
    particle = ref("particle")
    waves = lambda minimum=0: array(wave, 128, minimum)
    records = {
        "seed-genesis": record(
            "seed-genesis", owner_rappid=ref("rappid"), origin={"enum": ["new", "migration"]},
            inherited_heads=waves(), local_only=fixed(True), source_writes=fixed(False),
            fixed_taxonomy=fixed(False), candidate_self_authorization=fixed(False)),
        "scan-tile": record(
            "scan-tile", parent_tile=nullable(wave), previous_report=nullable(wave),
            tick=integer(), mode={"enum": ["baseline", "delta"]},
            scope=array(text(), 128, 1), targets=array(text()),
            signaled=array(text()), baseline_every=integer(1024, 1),
            last_baseline_tick=integer()),
        "native-shape-observation": record(
            "native-shape-observation", tile=nullable(wave), subject=text(), shape=text(),
            sources=waves(), metadata=array(ref("fact"), 64), fingerprint=particle,
            findings=array(text()), source_state=fixed("opaque"),
            read_scope=fixed("approved-metadata-only"), native_compliance=fixed("unclaimed")),
        "opaque-native-source": record(
            "opaque-native-source", subject=text(128),
            files=array(obj(path=ref("path"), bytes=integer(4096), sha256=ref("hash"),
                            octets_b64=text(5464, 0, r"^(?:[A-Za-z0-9+/]{4})*(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?$")), 16, 1),
            inventory=particle, native_identity={"type": "null"},
            read_scope=fixed("explicit-synthetic-fixture-files"), native_compliance=fixed("unclaimed")),
        "opaque-local-object": record(
            "opaque-local-object", subject=text(128), root_name_b64=b64,
            object_kind={"enum": ["file", "directory", "symlink", "special"]},
            entries=array(local_entry, 128), fingerprint=particle,
            read_scope=fixed("explicit-local-object"), native_identity={"type": "null"},
            semantics=fixed("unknown"), native_compliance=fixed("unclaimed")),
        "lens-declaration": record(
            "lens-declaration", label=text(), proposer_rappid=ref("rappid"),
            synthesis={"enum": ["local-rule", "model-candidate"]}, observations=waves(1),
            runtime_sha256=ref("hash"), program=ref("program")),
        "declared-reads": record(
            "declared-reads", lens=wave, sources=waves(1), contexts=waves(),
            complete={"type": "boolean"},
            reads=array(obj(name=text(), frame=wave, pointer=read["properties"]["pointer"],
                            value=particle), 64, 1)),
        "derived-frame": record(
            "derived-frame", lens=wave, declared_reads=wave, content=particle,
            value_json=text(512 * 1024, 2, r"^[^\u0000-\u001f\u007f]*$"),
            native_compliance=fixed("unclaimed")),
        "mutation-receipt": record(
            "mutation-receipt", lens=wave, sources=waves(1), contexts=waves(),
            declared_reads=wave, successor=wave,
            preservation=array(obj(frame=wave, before_sha256=ref("hash"),
                                   after_sha256=ref("hash"), bytes=integer(1024 * 1024)), 128, 1),
            preservation_scope=fixed("retained-frame-octets"),
            native_compliance=fixed("unclaimed")),
        "equivalence-evidence": record(
            "equivalence-evidence", receipt=wave, replays=array(particle, 2, 2, False),
            negatives={"const": NEGATIVES}, evaluator=fixed("bounded-ir-replay"),
            claim=fixed("equivalent-on-declared-inputs-not-universal")),
        "verification-adoption": record(
            "verification-adoption", candidate=wave, evidence=wave,
            base=nullable(wave), authorized_by=ref("rappid"),
            decision={"enum": ["adopt", "reject"]},
            authority_scope={"enum": ["local-explicit-consent", "rapp1-owner-policy"]}),
        "lens-drift": record(
            "lens-drift", lens=wave, trial=wave, replacement=nullable(wave),
            reason={"enum": ["replay-mismatch", "input-changed", "runtime-changed", "invariant-refusal"]}),
        "dimension-genesis": record(
            "dimension-genesis", parent=wave, depth=integer(32, 1), label=text()),
        "dream-report": record(
            "dream-report", tile=wave, responses=waves(), exhaust=array(text()),
            missing=array(text()), complete={"type": "boolean"}),
        "learned-projection": record(
            "learned-projection", tick=integer(), facts=array(ref("fact"), 64, 1),
            native_compliance=fixed("unclaimed")),
        "workspace-successor": record(
            "workspace-successor", source=wave, observation=wave, tick=integer(),
            context=nullable(wave), context_observation=nullable(wave), feedback=nullable(wave),
            members=array(obj(entry=integer(127), path_b64=b64, sha256=hexadecimal,
                              bytes=integer(4096)), 64, 2),
            admission_class=fixed("verified-structural-container"), adoption_eligible=fixed(True),
            native_compliance=fixed("unclaimed")),
        "workspace-unresolved": record(
            "workspace-unresolved", source=wave, observation=wave, tick=integer(),
            context=nullable(wave), context_observation=nullable(wave), feedback=nullable(wave),
            reason={"enum": ["incompatible-object-kind", "unresolved-links-or-special-members",
                             "external-content-evidence-required", "insufficient-workspace-evidence",
                             "context-source-contradiction", "source-not-bound-to-context", "unsupported-context-repair"]},
            missing_fields=array(text(), 16),
            contradictions=array(obj(source_sha256=ref("hash"), context_sha256=ref("hash")), 64),
            retry_requirement=fixed("additional-verified-workspace-context"),
            adoption_eligible=fixed(False), native_compliance=fixed("unclaimed")),
        "lens-loop": record(
            "lens-loop", root=wave, max_attempts=integer(128, 1), max_depth=integer(32),
            no_progress_window=integer(8, 1)),
        "iteration-request": record(
            "iteration-request", loop=wave, root=wave, lens=wave, sources=waves(1), contexts=waves(),
            parents=waves(), depth=integer(33), declared_reads=nullable(wave),
            strategy={"enum": ["select", "reapply", "descendant"]}, lens_parent=nullable(wave),
            work_key=particle),
        "iteration-exhaust": record(
            "iteration-exhaust", loop=wave, root=wave, request=wave, parents=waves(),
            result=nullable(wave), receipt=nullable(wave), equivalence=nullable(wave),
            classification={"enum": ["verified", "unresolved", "partial", "contradiction", "failed-test", "refusal"]},
            code=text(128), missing_fields=array(text(), 16),
            contradictions=array(obj(source_sha256=ref("hash"), context_sha256=ref("hash")), 64),
            semantic_result=particle),
        "iteration-attempt": record(
            "iteration-attempt", loop=wave, root=wave, request=wave, parents=waves(),
            ordinal=integer(127), depth=integer(33), work_key=particle, exhaust=wave,
            execution={"enum": ["executed", "deduplicated"]}, duplicate_of=nullable(wave),
            information=array(particle, 512), new_information=array(particle, 512),
            state=particle, repeated_state={"type": "boolean"}, no_progress=integer(128)),
        "iteration-stop": record(
            "iteration-stop", loop=wave, root=wave, attempts=waves(),
            pending=waves(), information=array(particle, 512), candidate=nullable(wave),
            reason={"enum": ["adopted-verified", "stable-fixed-point", "explicit-contradiction",
                             "explicit-refusal", "attempt-budget", "depth-budget", "missing-owner-authorization"]}),
        "iteration-work-key": obj(
            schema=fixed(PROFILE + "/iteration-work-key"), root=particle, lens_program=particle,
            runtime_sha256=ref("hash"), inputs=array(particle, 128, 1), declaration=nullable(particle)),
        "iteration-state": obj(
            schema=fixed(PROFILE + "/iteration-state"), root=particle,
            information=array(particle, 512), result=particle),
        "dimension-merge": record(
            "dimension-merge", left=waves(1), right=waves(1),
            shared=array(text()), mergeable=array(text()), conflicts=array(text()),
            retained=waves(1), numerator=integer(128), denominator=integer(128),
            no_shared_dimensions={"type": "boolean"}),
        "deterministic-reattach": record(
            "deterministic-reattach", stranded=wave, declared_reads=wave,
            ladder=waves(1), comparisons=array(ref("comparison"), 128, 1),
            selected=nullable(wave), status={"enum": ["candidate", "dry-hole"]},
            grafted_from=wave, activates_routing=fixed(False)),
        "routing-decision": record(
            "routing-decision", target=wave, action={"enum": ["select", "suppress", "re-add"]},
            base=nullable(wave), authorized_by=ref("rappid")),
        "registry-projection": record(
            "registry-projection", adopted=waves(), heads=array(ref("head"), 128, 1),
            entries=array(obj(frame=wave, selected={"type": "boolean"},
                              suppressed={"type": "boolean"}, eligible={"type": "boolean"}), 128),
            migration=nullable(wave), authority=fixed(False)),
        "migration-record": record(
            "migration-record", source_generation=fixed("pre-grail"),
            source_spec={"enum": LEGACY_LABELS}, source_spec_sha256=nullable(ref("hash")),
            source_identity_sha256=ref("hash"), authorized_by=ref("rappid"),
            prior_rappid=ref("rappid"), prior_world_id=text(128), prior_heads=waves(),
            baseline=array(ref("file"), 4096, 1),
            legacy_registry_sha256=nullable(ref("hash")),
            writes={"const": [CONTROL_DIR]}),
        "metadata-only-estate-egg": record(
            "metadata-only-estate-egg", egg=ref("egg"), selected=array(ref("file"), 128, 1),
            data_class=fixed("godd"), publication=fixed("not-authorized"),
            native_variant=fixed("estate"), import_effect=fixed("inert-no-routing")),
    }
    records["seed-genesis"]["properties"]["seed"] = {"type": "null"}
    return {"common.schema.json": common, **{
        name + ".schema.json": {"$schema": DRAFT, "$id": URI + name + ".schema.json", **value}
        for name, value in records.items()
    }}


def encoded(value):
    return (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    mismatches = []
    for name, value in schemas().items():
        path = ROOT / "schemas" / name
        raw = encoded(value)
        if args.check:
            if not path.is_file() or path.read_bytes() != raw:
                mismatches.append(name)
        else:
            path.write_bytes(raw)
    extras = {p.name for p in (ROOT / "schemas").glob("*.json")} - schemas().keys()
    mismatches.extend(sorted(extras))
    print(f"{len(schemas())} schemas | " + ("FAIL " + ", ".join(mismatches) if mismatches else "PASS"))
    return int(bool(mismatches))


if __name__ == "__main__":
    raise SystemExit(main())
