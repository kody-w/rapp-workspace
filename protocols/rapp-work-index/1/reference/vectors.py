"""Generate public deterministic application vectors through an explicit canonical checkout."""

from __future__ import annotations

import argparse
from pathlib import Path

from common import canonical, parse, read_file, require, sha, write_file
from schema_source import GENERATED_UTC, MAX_MANIFEST_BYTES, PROFILE, ROOT, SHARDS
from work_index import (
    PinnedGeneration, build_generation, candidate_order, checkpoint_payload,
    encode_token, identity, platform_adapters,
)

FIXTURES = ROOT / "fixtures" / "synthetic"


def application_outputs(inputs, core, checkpoint_key, checkpoint_spki):
    from canonical_fixture import sign_fixture

    output, previous_frame, previous_pin = {}, None, None
    for number, context in enumerate((inputs["context"], inputs["pivot_context"])):
        manifest, shards, proofs = build_generation(
            inputs["records"], number, context, inputs["sources"],
        )
        frame = core.r.build_frame(
            "memory.save", context["stream"], number, GENERATED_UTC,
            checkpoint_payload(manifest),
            None if previous_frame is None else previous_frame["payload_hash"],
        )
        frame = sign_fixture(core, frame, checkpoint_key, context["signer"])
        raw = core.octets(frame)
        verified, frame = core.verified_checkpoint(
            raw, context=context, spki=checkpoint_spki, head=previous_frame,
        )
        pin = PinnedGeneration(manifest, verified, context, previous_pin)
        output[f"generation-{number}.json"] = canonical(manifest, MAX_MANIFEST_BYTES)
        output[f"checkpoint-{number}.frame.json"] = raw
        output[f"checkpoint-{number}.binding.json"] = canonical(pin.binding)
        output[f"proofs-{number}.json"] = canonical(proofs)
        for index, shard_raw in shards.items():
            output[f"shard-{index:02d}.json"] = shard_raw
        if number == 0:
            candidates = sorted(
                (record for record in inputs["records"] if record["domain"] == "summon"),
                key=candidate_order,
            )
            output["golden.json"] = canonical({
                "classification": "public-synthetic-not-authority",
                "root": manifest["root"],
                "manifest_sha256": pin.binding["manifest_sha256"],
                "binding_sha256": sha(canonical(pin.binding)),
                "first_page_size": 2,
                "first_continuation": encode_token(pin, "summon", "cedar", identity(candidates[1]), 2),
                "adapters": platform_adapters(),
            })
        previous_frame, previous_pin = frame, pin
    return output


def generate(core):
    from canonical_fixture import public_test_key, sign_fixture

    checkpoint_key, checkpoint_spki, checkpoint_signer = public_test_key(core, "checkpoint", "index")
    context = {
        "signer": checkpoint_signer, "spki_sha256": sha(checkpoint_spki),
        "stream": checkpoint_signer, "key_epoch": 1, "registry_epoch": 1,
        **{name: sha(("PUBLIC SYNTHETIC " + name).encode("ascii")) for name in (
            "registry_root", "policy_root", "grant_root", "revocation_root",
            "subscription_root", "context_root",
        )},
    }
    sources, records, output, keys, saved = [], [], {}, {}, []
    keys[checkpoint_signer] = checkpoint_spki.hex()
    for number in range(7):
        if number < 6:
            key, spki, signer = public_test_key(core, f"source-{number:02d}", "cedar")
            payload = {"classification": "public-synthetic", "sample": number, "text": "cedar"}
            prior, sequence = None, 0
        else:
            key, spki, signer, payload, prior = saved[0]
            sequence = 1
        keys[signer] = spki.hex()
        frame = core.r.build_frame(
            "memory.save", signer, sequence, GENERATED_UTC, payload,
            None if prior is None else prior["payload_hash"],
        )
        frame = sign_fixture(core, frame, key, signer)
        frame_raw = core.octets(frame)
        core.verify(frame_raw, signer=signer, spki=spki, stream=signer, head=prior)
        saved.append((key, spki, signer, payload, frame))
        content = core.octets(payload)
        label = f"source-{number:02d}"
        output[label + ".frame.json"] = frame_raw
        output[label + ".content.json"] = content
        source = {
            "source": label, "subject": signer,
            "raw_sha256": sha(content), "raw_bytes": len(content),
            "signer": signer, "spki_sha256": sha(spki), "stream": signer,
            "seq": sequence, "key_epoch": 1, "registry_epoch": 1,
            "payload_hash": frame["payload_hash"], "frame_hash": frame["frame_hash"],
            "frame_sha256": sha(frame_raw),
            "policy_root": context["policy_root"], "registry_root": context["registry_root"],
        }
        sources.append(source)
        for domain, lookup_key in (("summon", "cedar"), ("catalog", label)):
            records.append({
                "schema": PROFILE + "/record", "domain": domain, "key": lookup_key,
                "rappid": signer, "content_sha256": sha(content), "content_bytes": len(content),
                "particle_hash": frame["payload_hash"], "occurrence_hash": frame["frame_hash"],
            })
    inputs = {
        "records": records, "sources": sources, "context": context,
        "pivot_context": {**context, "context_root": sha(b"PUBLIC SYNTHETIC contextual pivot")},
    }
    output["inputs.json"] = canonical(inputs, MAX_MANIFEST_BYTES)
    output["public-keys.json"] = canonical({
        "classification": "public-synthetic-not-a-trust-store",
        "keys": [{"signer": signer, "spki_der_hex": value} for signer, value in sorted(keys.items())],
    })
    output.update(application_outputs(inputs, core, checkpoint_key, checkpoint_spki))
    require(core.frames_verified >= 9, "zero/insufficient actual RAPP/1 fixture evidence")
    return output


def check_local():
    """Reproduce application bytes only; this does not verify RAPP/1 signatures."""
    inputs = parse(read_file(FIXTURES / "inputs.json"), MAX_MANIFEST_BYTES)
    for number, context in enumerate((inputs["context"], inputs["pivot_context"])):
        manifest, shards, proofs = build_generation(
            inputs["records"], number, context, inputs["sources"],
        )
        require(read_file(FIXTURES / f"generation-{number}.json") == canonical(manifest, MAX_MANIFEST_BYTES),
                "generation vector drift")
        require(read_file(FIXTURES / f"proofs-{number}.json") == canonical(proofs), "proof vector drift")
        for index in range(SHARDS):
            require(read_file(FIXTURES / f"shard-{index:02d}.json") == shards[index],
                    "shard vector drift")
    return inputs


def check_exact(output):
    paths = set()
    for path in FIXTURES.iterdir():
        require(path.is_file() and len(paths) < len(output), "unexpected fixture entry/expansion")
        paths.add(path.name)
    require(paths == set(output), "fixture file set differs from deterministic generator")
    for name, raw in output.items():
        require(read_file(FIXTURES / name) == raw, "fixture exact-byte drift: " + name)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    parser.add_argument("--rapp1-path", type=Path)
    args = parser.parse_args()
    if args.rapp1_path is None:
        require(not args.write, "fixture generation requires explicit --rapp1-path")
        check_local()
        print("application vectors: exact match; RAPP/1 Frames verified: 0 (not conformance)")
        return 0
    from canonical_fixture import CanonicalRapp

    core = CanonicalRapp(args.rapp1_path)
    output = generate(core)
    if args.write:
        for name, raw in output.items():
            write_file(FIXTURES / name, raw)
    check_exact(output)
    print(f"exact public vectors: {len(output)} files; canonical signed Frames verified: {core.frames_verified}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
