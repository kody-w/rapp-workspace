"""Blocking nonzero tests plus emitted, persisted, independently verified signed RAPP/1 Frames."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import unittest

from canonical_fixture import CanonicalRapp
from common import REPO, parse, pretty, read_file, require, sha, write_file
from pins import check as check_pins
from schema_source import GENERATED_UTC, MAX_MANIFEST_BYTES, PROFILE, ROOT, check as check_schema
from vectors import check_exact, generate
from work_index import ExactIndex, PinnedGeneration, identity


def scan_emitted(core, output, inputs, public_keys):
    keys = {entry["signer"]: bytes.fromhex(entry["spki_der_hex"]) for entry in public_keys["keys"]}
    heads, names = {}, []
    for source in inputs["sources"]:
        name = source["source"] + ".frame.json"
        raw = read_file(output / name)
        spki = keys[source["signer"]]
        require(sha(spki) == source["spki_sha256"], "source SPKI substitution")
        frame = core.verify(
            raw, signer=source["signer"], spki=spki, stream=source["stream"],
            head=heads.get(source["stream"]),
        )
        require(
            frame["seq"] == source["seq"] and frame["payload_hash"] == source["payload_hash"]
            and frame["frame_hash"] == source["frame_hash"] and sha(raw) == source["frame_sha256"],
            "source vector occurrence mismatch",
        )
        content = core.octets(frame["payload"])
        require(sha(content) == source["raw_sha256"] and len(content) == source["raw_bytes"],
                "source vector content substitution")
        heads[source["stream"]] = frame
        names.append(name)
    previous_frame, previous_pin, pins = None, None, []
    for number, context in enumerate((inputs["context"], inputs["pivot_context"])):
        name = f"checkpoint-{number}.frame.json"
        raw = read_file(output / name)
        record, previous_frame = core.verified_checkpoint(
            raw, context=context, spki=keys[context["signer"]], head=previous_frame,
        )
        manifest = parse(read_file(output.parent / f"generation-{number}.json"), MAX_MANIFEST_BYTES)
        previous_pin = PinnedGeneration(manifest, record, context, previous_pin)
        pins.append(previous_pin)
        names.append(name)
    emitted = []
    for path in output.iterdir():
        require(path.is_file() and len(emitted) < len(names), "emitted artifact file budget")
        emitted.append(path.name)
    require(sorted(emitted) == sorted(names),
            "unexpected/missing emitted frame artifacts")
    require(core.frames_verified == len(names) > 0, "zero-artifact RAPP/1 pass refused")
    return pins, names


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rapp1-path", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path(".validation/rapp-work-index-1"))
    args = parser.parse_args()
    require(not args.output.is_absolute() and ".." not in args.output.parts
            and len(args.output.parts) >= 2 and args.output.parts[0] == ".validation",
            "explicit owned relative .validation output required")
    require(Path.cwd() == REPO, "run conformance from the approved repository root")
    manifest_before = check_pins()
    check_schema()
    emitter = CanonicalRapp(args.rapp1_path)
    generated = generate(emitter)
    check_exact(generated)
    output = args.output
    frame_names = sorted(name for name in generated if name.endswith(".frame.json"))
    for name in frame_names:
        write_file(output / "emitted" / name, generated[name])
    for number in range(2):
        name = f"generation-{number}.json"
        write_file(output / name, generated[name])
    scanner = CanonicalRapp(args.rapp1_path)
    pins, scanned_names = scan_emitted(
        scanner, output / "emitted",
        parse(generated["inputs.json"], MAX_MANIFEST_BYTES), parse(generated["public-keys.json"]),
    )
    require(frame_names == sorted(scanned_names), "emitted/scanned artifact mismatch")
    pin = pins[0]
    proofs = parse(generated["proofs-0.json"])
    database = output / "exact-index.sqlite3"
    if not os.path.lexists(database):
        ExactIndex.build(
            database, pin, pin.frontier,
            ((generated[f"shard-{i:02d}.json"], proofs[i]) for i in range(16)),
        )
    with ExactIndex(database, pin, pin.frontier) as index:
        page = index.page(pin.frontier, "summon", "cedar", page_size=2)
        require(len(page["records"]) == 2 and page["continuation"] is not None,
                "nonzero collision pagination evidence required")
        record = next(
            item for item in parse(generated["inputs.json"], MAX_MANIFEST_BYTES)["records"]
            if item["domain"] == "summon"
        )
        result = index.summon(
            pin.frontier, "summon", "cedar", identity(record), generated["source-00.content.json"],
        )
        require(result["authority"] is False, "index must never grant authority")
    old_path = os.environ.get("RAPP_WORK_INDEX_RAPP1_PATH")
    os.environ["RAPP_WORK_INDEX_RAPP1_PATH"] = str(args.rapp1_path.absolute())
    try:
        suite = unittest.defaultTestLoader.discover(str(ROOT / "tests"), pattern="test_*.py")
        result = unittest.TextTestRunner(verbosity=2).run(suite)
    finally:
        if old_path is None:
            os.environ.pop("RAPP_WORK_INDEX_RAPP1_PATH", None)
        else:
            os.environ["RAPP_WORK_INDEX_RAPP1_PATH"] = old_path
    require(result.wasSuccessful() and result.testsRun > 0 and not result.skipped,
            "blocking profile tests failed/empty/skipped")
    require(check_pins() == manifest_before, "profile inputs changed during conformance")
    report = {
        "profile": PROFILE,
        "generated_utc": GENERATED_UTC,
        "tests_run": result.testsRun, "failures": len(result.failures),
        "errors": len(result.errors), "skipped": len(result.skipped),
        "rapp_frames_emitted": len(frame_names),
        "rapp_frames_verified": scanner.frames_verified,
        "signed_checkpoint_frames_verified": 2,
        "signed_source_frames_verified": 7,
        "canonical_rapp1_commit": scanner.pin["commit"],
        "canonical_anchor_frames_verified_separately": scanner.anchor_frames_verified,
        "manifest_sha256": sha(manifest_before),
        "generation_roots": [item.binding["root"] for item in pins],
        "checkpoint_waves": [item.binding["frame_hash"] for item in pins],
        "emitted_frames": ["emitted/" + name for name in frame_names],
        "sqlite_snapshot": "exact-index.sqlite3",
        "guarantees": {
            "rapp_integrity": "nonzero-signed-canonical-frames-verified",
            "observation": "public-synthetic-fixtures-only",
            "semantic_fidelity": "not-inferred",
            "current_authorization": "not-inferred",
            "safe_deployment": "not-qualified",
        },
        "authority": False, "estate_activation": False,
        "network_access": False, "resident_processes_required": 0,
    }
    write_file(output / "conformance-results.json", pretty(report))
    print(json.dumps(report, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
