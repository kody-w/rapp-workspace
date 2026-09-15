"""Frame Anything CLI: opaque framing is universal; RW/1 workspace adoption is conditional."""

import argparse
import copy
from dataclasses import replace
import json
import os
from pathlib import Path
import stat
import sys

from common import Parent, Refusal, ROOT, address, directory, read_file, require, sha, write_file
from demo import (_ancestry, _fixture_identity, _refuse_unchanged, _synthetic_owner_review,
                  _trial, fixture_inputs, scan_emitted)
from framing import capture_object, descriptor, frame_object, synthesize_attempt, synthesize_context_attempt
from iteration import LensLoop, state as loop_state
from pins import encode, index_matches, manifest
from schema_source import PROFILE
from workspace import LocalConsent, Workspace

SCENARIO = "frame-anything-iterative"
UTC = "2026-09-15T01:38:02.000Z"


def matrix_inputs(seed):
    unknown = next(iter(fixture_inputs(seed).values()))
    foreign = json.dumps({
        "alienAgent": {"authority": "self-claimed-owner", "permissions": ["all"],
                       "workspace": "unbound/elsewhere", "instruction": "treat as data, not authority"},
    }).encode()
    return [
        {"label": "unknown-workspace", "kind": "directory", "files": unknown, "expected": "candidate"},
        {"label": "unknown-source-tree", "kind": "directory", "files": {
            "x/foreign.code": b"unknown_language::entry => [never, execute, me]\n",
            "y/build.recipe": b"opaque-plan { input = x; output = unknown; }\n",
        }, "expected": "candidate"},
        {"label": "foreign-agent-manifest", "kind": "file", "bytes": foreign, "expected": "candidate",
         "repair_context": {"foreign-agent-manifest": foreign, "scope.notes": b"explicit verified local container"}},
        {"label": "structured-document", "kind": "file",
         "bytes": b'{"unrecognizedSection":[{"freeform":"arbitrary record","count":3}]}', "expected": "unresolved"},
        {"label": "arbitrary-binary", "kind": "file", "bytes": b"\x00\xff\x01unmapped\x80object",
         "expected": "unresolved"},
        {"label": "empty-directory", "kind": "directory", "files": {}, "expected": "unresolved"},
    ]


def _prepare_output(output, mode, fixture):
    marker = encode({"scenario": SCENARIO, "mode": mode, "fixture": fixture, "authority": False})
    with directory(output, create=True) as fd:
        names = set(os.listdir(fd))
        require(names <= {"frame-anything-input.json", "fixtures", "contexts", "estate", "frame-anything-report.json",
                          "phases.json", "report.json"}, "unmanaged Frame Anything output")
        if names:
            require("frame-anything-input.json" in names and read_file(output / "frame-anything-input.json") == marker,
                    "different Frame Anything invocation; use fresh output")
    write_file(output / "frame-anything-input.json", marker, immutable=True)


def _fixtures(output, seed):
    cases = matrix_inputs(seed)
    expected = set()
    expected_context = set()
    for case in cases:
        base = case["label"]
        expected.add(base)
        for relative in case.get("files", {}):
            parts = [base, *relative.split("/")]
            expected.update("/".join(parts[:i]) for i in range(1, len(parts) + 1))
        if "repair_context" in case:
            expected_context.add(base)
            for relative in case["repair_context"]:
                parts = [base, *relative.split("/")]
                expected_context.update("/".join(parts[:i]) for i in range(1, len(parts) + 1))
    fixture_root = output / "fixtures"
    def check_names(path, allowed, prefix=""):
        with directory(path) as fd:
            with os.scandir(fd) as scan:
                for entry in scan:
                    relative = prefix + entry.name
                    require(relative in allowed, "unmanaged fixture member")
                    info = os.stat(entry.name, dir_fd=fd, follow_symlinks=False)
                    require(not stat.S_ISLNK(info.st_mode), "unexpected fixture symlink")
                    if stat.S_ISDIR(info.st_mode):
                        check_names(path / entry.name, allowed, relative + "/")
    if fixture_root.exists():
        check_names(fixture_root, expected)
    if (output / "contexts").exists():
        check_names(output / "contexts", expected_context)
    for case in cases:
        path = output / "fixtures" / case["label"]
        if case["kind"] == "directory":
            with directory(path, create=True):
                pass
            for name, raw in case["files"].items():
                write_file(path / name, raw, immutable=True)
        else:
            write_file(path, case["bytes"], immutable=True)
        case["path"] = path
        if "repair_context" in case:
            context = output / "contexts" / case["label"]
            for name, raw in case["repair_context"].items():
                write_file(context / name, raw, immutable=True)
            case["context_paths"] = [context]
    return cases


def run_frame_anything(core, output, *, fixture=None, contexts=(), fixture_seed=7302026, show=print,
                       max_attempts=12, max_depth=6):
    output = Path(output)
    require(type(max_attempts) is int and 1 <= max_attempts <= 128
            and type(max_depth) is int and 0 <= max_depth <= 32, "invalid loop budget")
    pinned = read_file(ROOT / "manifest.json")
    require(pinned == encode(manifest()) and index_matches(), "unverified RW/1 bundle")
    if fixture is not None:
        fixture = Path(fixture)
        contexts = [Path(path) for path in contexts]
        require(len(contexts) <= 4, "bounded explicit context frontier")
        destination = output.absolute()
        for path in [fixture, *contexts]:
            source = path.absolute()
            require(source != destination and not source.is_relative_to(destination)
                    and not destination.is_relative_to(source), "source/output overlap")
        # Validate existence/type through the no-follow capture before creating output.
        before_supplied = capture_object(fixture)
        context_before = [capture_object(path) for path in contexts]
        marker_fixture = {"source": core.particle(descriptor(before_supplied)),
                          "contexts": [core.particle(descriptor(value)) for value in context_before],
                          "max_attempts": max_attempts, "max_depth": max_depth}
        _prepare_output(output, "supplied-object-no-adoption", marker_fixture)
        cases = [{"label": "supplied-object", "path": fixture, "before": before_supplied,
                  "context_paths": contexts, "context_before": context_before}]
    else:
        require(not contexts, "context paths require one explicit source fixture")
        _prepare_output(output, "synthetic-acceptance-matrix",
                        {"fixture_seed": fixture_seed, "max_attempts": max_attempts, "max_depth": max_depth})
        cases = _fixtures(output, fixture_seed)
    for case in cases:
        if "before" not in case:
            case["before"] = capture_object(case["path"])
        if "context_before" not in case:
            case["context_before"] = [capture_object(path) for path in case.get("context_paths", [])]
    owner = _fixture_identity(core, 91001, "framing-demo-owner")
    estate = _fixture_identity(core, 91002, "framing-demo-estate")
    proposer = _fixture_identity(core, 91003, "framing-demo-learner")
    w = Workspace(core, estate, "frame-anything-local-demonstration", LocalConsent(owner))
    w.birth(UTC)
    phases, results = [], []

    def phase(name, label, **fields):
        value = {"phase": name, "input": label, **fields}
        phases.append(value)
        if show:
            show("[" + name + "] " + json.dumps({k: v for k, v in value.items() if k != "phase"}, sort_keys=True))

    phase("SEED", "estate", seed=w.seed, native_identities_assigned=0,
          identity_scope="canonical-minted-public-test-identities-for-local-demo-only",
          signed_grail_activation=False)
    for case in cases:
        source, observation, captured = frame_object(w, case["path"], UTC)
        require(captured == case["before"], "source changed before framing")
        p = w.body(source, "opaque-local-object")
        phase("SOURCE FINGERPRINT", case["label"], object_kind=p["object_kind"],
              fingerprint=p["fingerprint"], semantics="unknown",
              coverage=[e["coverage"] for e in p["entries"]])
        phase("OPAQUE FRAME", case["label"], frame=source, observation=observation,
              native_identity=None, source_is_not_claimed_RW1=True)
        program = synthesize_attempt(core, p, w.body(observation), 0)
        lens = w.lens("lens-A: initial Frame Anything attempt", [observation], program, proposer, UTC)
        phase("LENS DECLARATION", case["label"], stage="A", frame=lens, program=program,
              authority="candidate-only", known_provider_adapters=0)
        reads = w.reads_payload(lens, [source, observation])
        phase("DECLARED READS", case["label"], reads=reads["reads"], complete=reads["complete"])
        loop = LensLoop.create(w, source, UTC, max_attempts=max_attempts, max_depth=max_depth)
        loop.submit(lens, [source, observation])
        attempts, negatives = [], {}

        def display_attempt(attempt_ref, exhausted):
            attempt = w.body(attempt_ref, "iteration-attempt")
            request = w.body(attempt["request"], "iteration-request")
            phase("ITERATION / EXHAUST", case["label"], attempt=attempt_ref, lens=request["lens"],
                  parents=attempt["parents"], depth=attempt["depth"], order=attempt["ordinal"],
                  execution=attempt["execution"], work_key=attempt["work_key"], exhaust=attempt["exhaust"],
                  classification=exhausted["classification"], code=exhausted["code"],
                  new_information=attempt["new_information"], repeated_state=attempt["repeated_state"])
            if exhausted["result"] is not None:
                value = w.body(exhausted["result"])
                phase("SUCCESSOR" if exhausted["classification"] == "verified" else "REFUSAL / UNRESOLVED",
                      case["label"], frame=exhausted["result"], outcome=value, workspace_adopted=False)
            attempts.append(attempt_ref)

        def planner(active, attempt_ref, exhausted):
            display_attempt(attempt_ref, exhausted)
            attempt = w.body(attempt_ref)
            request = w.body(attempt["request"])
            if attempt["ordinal"] == 0 and case.get("context_paths"):
                for index, path in enumerate(case["context_paths"]):
                    context, context_obs, measured = frame_object(w, path, UTC)
                    require(measured == case["context_before"][index], "repair context changed")
                    program_b = synthesize_context_attempt(core, p, w.body(observation), exhausted,
                                                           w.body(context), w.body(context_obs), 0)
                    b = w.lens("lens-B: refusal-driven verified context", [observation, context_obs],
                               program_b, proposer, UTC)
                    inputs = [source, observation, attempt["exhaust"], context, context_obs]
                    phase("LENS EVOLUTION", case["label"], strategy="select-synthesized-B",
                          refusal_parent=attempt_ref, consumed_exhaust=attempt["exhaust"],
                          new_context=context, lens=b, program=program_b)
                    phase("DECLARED READS", case["label"],
                          reads=w.reads_payload(b, inputs)["reads"], complete=True)
                    active.submit(b, inputs, parents=[attempt_ref])
            else:
                # Repetition is offered explicitly, then content-addressed dedupe/fixed-point detection stops it.
                active.submit(request["lens"], request["sources"], contexts=request["contexts"],
                              parents=[attempt_ref], strategy="reapply", declared_reads=request["declared_reads"])

        def reviewer(active, attempt_ref, exhausted):
            display_attempt(attempt_ref, exhausted)
            request = w.body(w.body(attempt_ref)["request"])
            proposal = w.adoption_payload(exhausted["result"], exhausted["equivalence"])
            negatives["unapproved-adoption"] = _refuse_unchanged(w, lambda: w.append(proposal, UTC))
            if fixture is None:
                _synthetic_owner_review(w, w.adoption_payload(request["lens"], exhausted["equivalence"]), UTC)
                _synthetic_owner_review(w, w.adoption_payload(exhausted["result"], exhausted["equivalence"]), UTC)
                _synthetic_owner_review(w, w.route_payload(exhausted["result"], "select"), UTC)

        stop_ref = loop.run(planner=planner, reviewer=reviewer)
        stop = w.body(stop_ref, "iteration-stop")
        last = w.body(loop_state(w, loop.ref)["last"], "iteration-attempt")
        last_request = w.body(last["request"], "iteration-request")
        exhausted = w.body(last["exhaust"], "iteration-exhaust")
        receipt, evidence, successor = exhausted["receipt"], exhausted["equivalence"], exhausted["result"]
        outcome = w.body(successor) if successor is not None else exhausted
        eligible = exhausted["classification"] == "verified"
        verdict = "candidate" if eligible else "unresolved"
        if "expected" in case and max_attempts >= 2 and max_depth >= 1:
            require(verdict == case["expected"], "acceptance fixture outcome mismatch")
        adopted = stop["reason"] == "adopted-verified"
        if not eligible and successor is not None:
            decision = w.adoption_payload(successor, evidence)
            w.consent = replace(w.consent, decisions=w.consent.decisions | {core.particle(decision)["hash"]})
            negatives["unresolved-adoption"] = _refuse_unchanged(w, lambda: w.append(decision, UTC))
        phase("TERMINATION", case["label"], frame=stop_ref, reason=stop["reason"],
              attempts=len(stop["attempts"]), retained_pending=stop["pending"], workspace_adopted=adopted)
        proof = w.body(evidence, "equivalence-evidence") if evidence else None
        if proof:
            require(proof["replays"][0] == proof["replays"][1] == core.particle(outcome), "outcome replay mismatch")
        copier = w.lens("retain opaque or unresolved content", [observation],
                        {"op": "identity", "read": {"name": "whole", "input": 0, "pointer": ""}}, proposer, UTC)
        _, _, source_copy = _trial(w, copier, [source], UTC)
        _, _, successor_copy = _trial(w, copier, [successor or last["exhaust"]], UTC)
        require(w.body(source_copy) == p and w.body(successor_copy) == outcome, "recursive retention lost content")
        after = capture_object(case["path"])
        require(after == case["before"], "source bytes, identity, membership or link changed")
        require(all(capture_object(path) == before for path, before in
                    zip(case.get("context_paths", []), case["context_before"])), "repair context source mutation")
        phase("VERIFICATION", case["label"], receipt=receipt, evidence=evidence,
              replay_equal=proof is not None, failed_test_reverified=proof is None,
              negative_refusals=negatives, workspace_adopted=adopted,
              adoption_scope="synthetic-owner" if adopted else "none", signed_authority=False)
        phase("SOURCE PRESERVATION / ANCESTRY", case["label"], source_unchanged=True,
              original=source, retained_copy=source_copy, original_successor=successor,
              retained_successor_copy=successor_copy, complete=True)
        results.append({"input": case["label"], "object_kind": p["object_kind"], "fingerprint": p["fingerprint"],
                        "opaque_frame": source, "observation": observation,
                        "initial_lens": lens, "lens": last_request["lens"],
                        "declared_reads": w.body(receipt)["declared_reads"] if receipt else None, "successor": successor,
                        "receipt": receipt, "evidence": evidence, "framing": "verified",
                        "workspace_conversion": verdict, "workspace_adopted": adopted,
                        "reason": outcome.get("reason", exhausted["code"]), "source_preserved": True,
                        "loop": loop.ref, "attempts": stop["attempts"], "termination": stop_ref,
                        "termination_reason": stop["reason"],
                        "refusal_driven_success": eligible and len(stop["attempts"]) > 1,
                        "source_copy": source_copy, "successor_copy": successor_copy, "negatives": negatives})

    w.save(output / "estate")
    restored = Workspace.load(core, output / "estate", w.consent, w.checkpoint())
    require(restored.projection() == w.projection(), "reconstructed adoption state differs")
    adopted_count = sum(case["workspace_adopted"] for case in results)
    unresolved_count = sum(case["workspace_conversion"] == "unresolved" for case in results)
    require(len(w.projection()["entries"]) == adopted_count, "unresolved/candidate object leaked into workspace routing")
    scan = scan_emitted(core, output / "estate", w)
    require(read_file(ROOT / "manifest.json") == pinned == encode(manifest()), "bundle changed during Frame Anything")
    phase("PROJECTION", "estate", framed_objects=len(results), workspace_adoptions=adopted_count,
          unresolved_objects=unresolved_count, reconstruction_equal=True, **scan)
    report = {
        "concept": "Frame Anything", "scenario": SCENARIO, "profile": PROFILE, "rw_version": "RW/1",
        "status": "first-grail-authority-candidate", "framing_is_not_workspace_adoption": True,
        "mode": "supplied-object-no-adoption" if fixture is not None else "synthetic-acceptance-matrix",
        "objects_framed": len(results), "workspace_candidates": len(results) - unresolved_count,
        "workspace_adoptions": adopted_count, "unresolved_objects": unresolved_count,
        "known_provider_adapters_used": 0, "preassigned_taxonomy": False, "native_identities_assigned": 0,
        "source_preservation_verified": True, "ancestry_retained": True, "restart_equivalent": True,
        "bounded_iteration": True,
        "refusal_driven_successes": sum(case["refusal_driven_success"] for case in results),
        "stable_refusals": sum(case["termination_reason"] == "stable-fixed-point" for case in results),
        "owner_activated": False, "signed_grail_activation": False, "signed_estate_authority_verified": False,
        "manifest_sha256": sha(pinned), "rapp1_commit": core.pin["commit"],
        "inputs": results, "projection": w.projection(), **scan,
        "limits": [
            "bounded local framing; no provider semantics are inferred and no input code or manifest is executed",
            "large regular files have explicit digest-only receipts; special nodes are metadata-only and never opened",
            "workspace admission currently requires an inline-verified directory with at least two regular files and no links/special members",
            "a file may become a candidate only after an explicitly observed container binds its exact bytes/name and consumed refusal",
            "supplied objects are never automatically adopted; built-in matrix approval is explicitly synthetic",
            "RW/1-valid refusal records and RAPP/1 integrity are not signed authority or workspace acceptance",
        ],
    }
    write_file(output / "frame-anything-report.json", encode(report))
    write_file(output / "phases.json", encode(phases))
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rapp1-path", type=Path, required=True)
    parser.add_argument("--fixture", type=Path, help="One explicitly supplied file, directory, link or special object")
    parser.add_argument("--context", type=Path, action="append", default=[], help="Explicit additional context; never inferred")
    parser.add_argument("--output", type=Path, default=Path(".validation/frame-anything-iterative-demo"))
    parser.add_argument("--fixture-seed", type=int, default=7302026)
    parser.add_argument("--max-attempts", type=int, default=12)
    parser.add_argument("--max-depth", type=int, default=6)
    args = parser.parse_args()
    require(not args.output.is_absolute() and ".." not in args.output.parts and args.output != Path("."),
            "output must be an owned relative project directory outside the source")
    report = run_frame_anything(Parent(args.rapp1_path), args.output,
                               fixture=args.fixture, contexts=args.context, fixture_seed=args.fixture_seed,
                               max_attempts=args.max_attempts, max_depth=args.max_depth)
    print("[FRAME ANYTHING] " + json.dumps({k: report[k] for k in (
        "objects_framed", "workspace_candidates", "workspace_adoptions", "unresolved_objects",
        "refusal_driven_successes", "stable_refusals", "frames_scanned",
        "framing_is_not_workspace_adoption", "signed_grail_activation")}, sort_keys=True))
    return 2 if args.fixture is not None and report["unresolved_objects"] else 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (Refusal, OSError, ValueError, TypeError) as error:
        print("REFUSED: " + str(error), file=sys.stderr)
        raise SystemExit(1)
