"""Canonical synthetic proof: UNKNOWN native bytes → learned lenses → Grail projections."""

import argparse
import copy
from dataclasses import replace
import json
import os
from pathlib import Path
import random
import re
import subprocess
import sys
from unittest.mock import patch
import uuid

from common import Parent, Refusal, ROOT, address, directory, read_file, require, sha, write_file
from native_lens import capture_native, inventory, observe_native, synthesize_program
from pins import encode, index_matches, manifest
from schema_source import NEGATIVES, PROFILE
from workspace import LocalConsent, Workspace

UTC = "2026-09-15T01:05:45.000Z"
SCENARIO = "unknown-native-shapes-to-grail"


def fixture_inputs(seed=7302026):
    """Fixture producer, deliberately separate from the observer/learner.

    The learner receives none of this generator's decisions: only measured
    frames. Changing this seed produces previously unseen names and octets.
    """
    rng = random.Random(seed)
    token = lambda: "".join(rng.choice("abcdefghijklmnopqrstuvwxyz0123456789") for _ in range(9))
    shapes = {}
    for index in range(3):
        subject = "local-" + token()
        files = {}
        for number in range(index + 2):
            path = "/".join([*(token() for _ in range(index)), token() + ".opaque"])
            if index == 0:
                raw = f"!{token()}::{token()}\n[{number}|{token()}]\n".encode()
            elif index == 1:
                raw = json.dumps({token(): {token(): [token(), number, token()]}}).encode()
            else:
                raw = bytes([0, 255, 128, number]) + bytes(rng.randrange(256) for _ in range(29 + number))
            files[path] = raw
        shapes[subject] = files
    return shapes


def _fixture_identity(core, number, slug):
    # Public UUIDv4 test entropy only; the canonical mint, not a name/path hash, produces the RAPPID.
    with patch.object(core.r.uuid, "uuid4", return_value=uuid.UUID(int=number, version=4)):
        return core.r.mint_rappid("fictional", slug)


def _install_inputs(root, shapes):
    for subject, files in shapes.items():
        for path, raw in files.items():
            write_file(root / subject / path, raw, immutable=True)
    require({p.name for p in root.iterdir()} == set(shapes), "unmanaged native fixture root")
    for subject, expected in shapes.items():
        captured = capture_native(root / subject)
        require(inventory(captured["files"]) == [
            {"path": name, "bytes": len(raw), "sha256": sha(raw)} for name, raw in sorted(expected.items())
        ], "existing fixture bytes/layout differ; never replace them")


def _refuse_unchanged(workspace, action):
    before = workspace.checkpoint()
    try:
        action()
    except (Refusal, ValueError) as error:
        require(workspace.checkpoint() == before, "negative vector changed frame history")
        return str(error)
    raise Refusal("negative vector unexpectedly accepted")


def _synthetic_owner_review(workspace, decision, utc=UTC):
    """Test harness's independent exact consent; not called by or passed to synthesis."""
    workspace.consent = replace(workspace.consent, decisions=workspace.consent.decisions |
                                {workspace.core.particle(decision)["hash"]})
    return workspace.append(decision, utc)


def _trial(workspace, lens, sources, utc=UTC):
    receipt = workspace.mutate(lens, sources, utc)
    evidence = workspace.append(workspace.evidence_payload(receipt), utc)
    successor = workspace.body(receipt)["successor"]
    return receipt, evidence, successor


def _ancestry(workspace, descendant):
    pending, seen = [address(descendant)], set()
    while pending:
        key = pending.pop()
        if key not in seen:
            seen.add(key)
            pending.extend(workspace._parents[key])
    return seen


def scan_emitted(core, root, workspace):
    completed = subprocess.run(
        [sys.executable, "-B", str(core.path / "rapp_check.py"), str(root), "--json"],
        capture_output=True, text=True)
    require(completed.returncode == 0, "canonical scan failed: " + completed.stdout + completed.stderr)
    report = json.loads(completed.stdout)
    evidence = [item for item in report["evidence"] if re.match(r"^\d+ frames conform", item["ok"])]
    count = sum(int(item["ok"].split()[0]) for item in evidence)
    emitted = sum(len(chain) for chain in workspace._streams.values())
    require(report["verdict"] == "COMPLIANT" and not report["findings"] and count == emitted and count > 0,
            "zero, incomplete, or non-compliant emitted frame evidence")
    return {"frames_emitted": emitted, "frames_scanned": count, "streams_scanned": len(evidence),
            "scanner_verdict": report["verdict"], "findings": report["findings"], "scan_evidence": evidence}


def run_demo(core, output, *, show=print, fixture_seed=7302026):
    output = Path(output)
    pinned = read_file(ROOT / "manifest.json")
    require(pinned == encode(manifest()) and index_matches(), "unverified candidate bundle")
    shapes = fixture_inputs(fixture_seed)
    fixture_manifest = encode({
        "synthetic": True, "authority": False, "scenario": SCENARIO, "fixture_seed": fixture_seed,
        "roots": {subject: [{"path": name, "bytes": len(raw), "sha256": sha(raw)}
                            for name, raw in sorted(files.items())] for subject, files in shapes.items()},
    })
    with directory(output, create=True) as fd:
        existing = set(os.listdir(fd))
        require(existing <= {"demo-inputs.json", "native-fixtures", "estate", "demo-report.json",
                              "phases.json", "report.json"}, "unmanaged demo output")
        if existing:
            require("demo-inputs.json" in existing and read_file(output / "demo-inputs.json") == fixture_manifest,
                    "unmanaged or different fixture run; use a fresh output")
    write_file(output / "demo-inputs.json", fixture_manifest, immutable=True)
    native_root = output / "native-fixtures"
    _install_inputs(native_root, shapes)
    before = {subject: capture_native(native_root / subject) for subject in shapes}
    owner = _fixture_identity(core, 80001, "demo-owner")
    estate = _fixture_identity(core, 80002, "demo-estate")
    proposer = _fixture_identity(core, 80003, "demo-synthesizer")
    workspace = Workspace(core, estate, "synthetic-unknown-native-world", LocalConsent(owner))
    workspace.birth(UTC)
    tile = workspace.append(workspace.scan_payload(list(shapes)), UTC)
    phases, cases, observations, programs, binding_counts = [], [], [], [], []

    def phase(name, subject, **data):
        entry = {"phase": name, "subject": subject, **data}
        phases.append(entry)
        if show:
            show("[" + name + "] " + json.dumps({k: v for k, v in entry.items() if k != "phase"}, sort_keys=True))

    phase("SEED", "estate", seed=workspace.seed, estate_rappid=estate,
          identity_mint="canonical-RAPP1-with-public-test-entropy", native_identities_assigned=0,
          signed_grail_activation=False)
    for subject in shapes:
        phase("BEFORE", subject, native_format="UNKNOWN", native_rappid=None,
              files=inventory(before[subject]["files"]), taxonomy=None)
        source, observed, measured = observe_native(workspace, native_root / subject, UTC, tile=tile)
        observations.append(observed)
        source_payload = workspace.body(source, "opaque-native-source")
        observation = workspace.body(observed, "native-shape-observation")
        require(measured == before[subject], "native input changed before observation")
        phase("OBSERVATION", subject, source_frame=source, observation_frame=observed,
              entries_scanned=measured["entries_scanned"], bytes_read=measured["bytes_read"],
              source_state="opaque", native_compliance="unclaimed")
        program = synthesize_program(core, observation, source_payload, workspace.body(tile)["tick"])
        require(program == synthesize_program(core, observation, source_payload, 0), "nondeterministic synthesis")
        programs.append(core.particle(program))
        binding_counts.append(len(program["bindings"]))
        lens = workspace.lens("learned:" + subject, [observed], program, proposer, UTC)
        phase("LENS", subject, lens_frame=lens, program=program,
              synthesis="deterministic-evidence-derived-structural-candidate", authority="none")
        receipt, evidence, successor = _trial(workspace, lens, [observed, source])
        result = workspace.body(successor, "learned-projection")
        phase("SUCCESSOR", subject, frame=successor, envelope_spec=workspace.frame(successor)["spec"],
              payload_schema=workspace.frame(successor)["payload"]["schema"], projected_content=result)

        manifest_value = workspace.reads_payload(lens, [observed, source])
        manifest_value["complete"] = False
        tampered_source = copy.deepcopy(source_payload)
        tampered_source["files"][0]["sha256"] = "0" * 64
        unsafe_path = copy.deepcopy(source_payload)
        unsafe_path["files"][0]["path"] = "../outside"
        invented_identity = copy.deepcopy(source_payload)
        invented_identity["native_identity"] = owner
        decision = workspace.adoption_payload(lens, evidence)
        negatives = {
            "incomplete-mutation": _refuse_unchanged(
                workspace, lambda: workspace.mutate(lens, [observed, source], UTC, declared=manifest_value)),
            "source-byte-substitution": _refuse_unchanged(workspace, lambda: workspace.append(tampered_source, UTC)),
            "path-escape": _refuse_unchanged(workspace, lambda: workspace.append(unsafe_path, UTC)),
            "invented-native-identity": _refuse_unchanged(workspace, lambda: workspace.append(invented_identity, UTC)),
            "invented-owner-authority": _refuse_unchanged(workspace, lambda: workspace.append(decision, UTC)),
        }
        require(set(workspace.frame(successor)) == core.r.FRAME_KEYS, "alternative frame envelope")
        required = {address(x) for x in (workspace.seed, source, observed, lens)}
        require(required <= _ancestry(workspace, successor), "missing original ancestry")
        proof = workspace.body(evidence, "equivalence-evidence")
        require(proof["replays"][0] == proof["replays"][1] == core.particle(result), "replay mismatch")
        require(proof["negatives"] == NEGATIVES, "negative replay tests missing")
        _synthetic_owner_review(workspace, decision)
        _synthetic_owner_review(workspace, workspace.adoption_payload(successor, evidence))
        _synthetic_owner_review(workspace, workspace.route_payload(successor, "select"))
        require(capture_native(native_root / subject) == before[subject], "native mutation during adaptation")
        phase("VERIFICATION", subject, receipt=receipt, evidence=evidence, replay_payload=proof["replays"][0],
              core_negative_refusals=proof["negatives"], additional_negative_refusals=negatives,
              source_bytes_unchanged=True, ancestry_complete=True, native_identity_assigned=False,
              adoption="independent-synthetic-owner-consent-not-signed-authority")
        cases.append({"subject": subject, "before": inventory(before[subject]["files"]),
                      "source": source, "observation": observed, "lens": lens, "program": core.particle(program),
                      "receipt": receipt, "evidence": evidence, "successor": successor,
                      "source_bytes_unchanged": True, "ancestry_complete": True,
                      "negative_refusals": negatives, "recursive": []})

    require(len({p["hash"] for p in programs}) == len(shapes), "different native shapes need different learned programs")
    require(len(set(binding_counts)) == len(shapes), "headline recipes must differ structurally, not only by label")
    workspace.append(workspace.report_payload(tile, observations), UTC)
    copier = workspace.lens("generic-recursive-content-lens", [observations[0]],
                            {"op": "identity", "read": {"name": "whole", "input": 0, "pointer": ""}},
                            proposer, UTC)
    for case in cases:
        originals = {address(case[k]): workspace._raw[address(case[k])]
                     for k in ("source", "observation", "lens", "successor")}
        descendants = {}
        for role in ("source", "observation", "lens", "successor"):
            receipt, evidence, child = _trial(workspace, copier, [case[role]])
            require(workspace.body(child) == workspace.body(case[role]), "recursive content loss")
            require(address(case[role]) in _ancestry(workspace, child), "recursive ancestor missing")
            descendants[role] = child
            case["recursive"].append({"role": role, "frame": child, "receipt": receipt, "evidence": evidence})
        # Run a lens which was itself derived through a lens, then recurse on a derived result again.
        _, _, rerun = _trial(workspace, descendants["lens"], [case["observation"], case["source"]])
        _, _, next_result = _trial(workspace, copier, [descendants["successor"]])
        require(workspace.body(rerun) == workspace.body(case["successor"]) == workspace.body(next_result),
                "lens-on-lens or recursive successor replay mismatch")
        require(all(workspace._raw[k] == raw for k, raw in originals.items()), "original frame mutation")
        phase("RECURSIVE", case["subject"], retained_originals=sorted(originals),
              derived_lens=descendants["lens"], rerun_successor=rerun, deeper_successor=next_result,
              all_original_and_derived_frames_retained=True)
        case["derived_lens_rerun"] = rerun
        case["deeper_successor"] = next_result

    projection = workspace.projection()
    require(len(projection["entries"]) == len(shapes)
            and all(e["eligible"] and e["selected"] for e in projection["entries"]), "incomplete adopted projections")
    require(set(workspace._streams) == {estate}, "invented native stream identity")
    require(all(capture_native(native_root / subject) == before[subject] for subject in shapes),
            "native source/layout/identity mutation")
    workspace.save(output / "estate")
    restored = Workspace.load(core, output / "estate", workspace.consent, workspace.checkpoint())
    require(restored.projection() == projection, "projection reconstruction differs")
    scan = scan_emitted(core, output / "estate", workspace)
    require(read_file(ROOT / "manifest.json") == pinned == encode(manifest()), "candidate changed during demo")
    report = {
        "scenario": SCENARIO, "profile": PROFILE, "protocol_family": "rapp-workspace/1",
        "generation": "grail", "status": "first-grail-authority-candidate", "acceptance_gate": "passed",
        "fixture_seed": fixture_seed, "previously_unknown_native_shapes": len(shapes),
        "native_files_observed": sum(len(v["files"]) for v in before.values()),
        "known_provider_adapters_used": 0, "preassigned_taxonomy": False, "native_identities_assigned": 0,
        "source_bytes_and_layout_unchanged": True, "original_and_derived_frames_retained": True,
        "different_candidate_programs": len(programs), "learned_binding_counts": binding_counts,
        "deterministic_replay": True,
        "restart_equivalent": True, "live_native_profiles_observed": 0, "owner_activated": False,
        "signed_grail_activation": False, "signed_estate_authority_verified": False,
        "manifest_sha256": sha(pinned), "rapp1_commit": core.pin["commit"],
        "cases": cases, "projection": projection, **scan,
        "limitations": [
            "synthetic fixture roots only; no live native profiles or remote model calls",
            "structural/opaque byte projection, not universal native-format semantic understanding",
            "independent owner consent is simulated by the harness; no signed authority is manufactured",
            "the reference IR and native observer are bounded, not a production provider adapter",
        ],
    }
    phase("PROJECTION", "estate", registry_schema=projection["schema"], entries=len(projection["entries"]),
          reconstructed=True, canonical_frames=scan["frames_scanned"], streams=scan["streams_scanned"],
          signed_grail_activation=False)
    write_file(output / "demo-report.json", encode(report))
    write_file(output / "phases.json", encode(phases))
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rapp1-path", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path(".validation/unknown-native-grail-demo"))
    parser.add_argument("--fixture-seed", type=int, default=7302026)
    args = parser.parse_args()
    require(not args.output.is_absolute() and ".." not in args.output.parts and args.output != Path("."),
            "demo output must be an owned relative project directory")
    result = run_demo(Parent(args.rapp1_path), args.output, fixture_seed=args.fixture_seed)
    print("[PASS] " + json.dumps({key: result[key] for key in (
        "scenario", "profile", "previously_unknown_native_shapes", "different_candidate_programs",
        "frames_scanned", "streams_scanned", "source_bytes_and_layout_unchanged", "signed_grail_activation")},
        sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (Refusal, OSError, ValueError) as error:
        print("REFUSED: " + str(error), file=sys.stderr)
        raise SystemExit(1)
