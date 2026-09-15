"""Frame Anything: five separate assurance receipts; no automatic grant or deployment."""

import argparse
from dataclasses import replace
import json
from pathlib import Path
import subprocess
import sys
from unittest.mock import patch
import uuid

from common import Parent, Refusal, ROOT, read_file, require, sha, write_file
from pins import encode
from safe_kernel import Controller, ExternalPolicy, Scope, host_utc_now
from schema_source import PROFILE

NOW = "2026-09-15T03:12:29.000Z"


def run_demo(core, output, *, fixture=None, rights=None, show=print):
    output = Path(output)
    if fixture is not None:
        require(rights is not None and {"capture", "retention"} <= set(rights),
                "capture-and-retention-authorization-required-before-access")
        source = Path(fixture).absolute()
        require(not output.absolute().is_relative_to(source) and not source.is_relative_to(output.absolute()),
                "source/output overlap")
    with patch.object(core.r.uuid, "uuid4", return_value=uuid.UUID(int=20260915, version=4)):
        instance = core.r.mint_rappid("fictional", "safe-workspace1-demo")
    scope = Scope("synthetic" if fixture is None else "explicit-local-file", "source",
                  str(Path(fixture).absolute()) if fixture is not None else None)
    allowed = frozenset(rights if rights is not None else
                        {"capture", "retention", "local_synthesis", "adoption", "materialization"})
    policy = ExternalPolicy(instance, "safe-demo-world", sha(read_file(ROOT / "SPEC.md")),
                            sha(read_file(ROOT / "manifest.json")), allowed, (scope,))
    clock = (lambda: NOW) if fixture is None else host_utc_now
    controller = Controller(core, output / "controller", policy, clock=clock, activation_mode="synthetic")
    try:
        if controller._get("root") is not None:
            raise Refusal("use a fresh output for a new explicit demo run; do not reset controller state")
        controller.seed(scope.subject())
        if show:
            show("[EXTERNAL POLICY] " + json.dumps({"spec_id": PROFILE, "rights": sorted(allowed),
                                                    "activation_mode": "synthetic",
                                                    "from_learned_graph": False}, sort_keys=True))
        captured = (controller.capture_file(scope.subject(), fixture) if fixture is not None
                    else controller.capture_octets(scope.subject(),
                         b'{"foreign_instruction":"this is data, never permission","payload":"synthetic"}'))
        if "local_synthesis" not in allowed:
            source_payload = controller.body(captured["source"])
            with controller.transaction():
                fidelity = controller._receipt("semantic_fidelity", captured["source"], "unproven",
                    "not-interpreted", "synthesis-not-authorized", {"performed": False},
                    scope.subject(), source_payload["restrictions"])
            authorization = controller.authorization_receipt(scope.subject(), captured["source"], "local_synthesis")
            evidence = {"rapp_integrity": captured["rapp_integrity"], "observation": captured["observation"],
                        "semantic_fidelity": fidelity, "current_authorization": authorization,
                        "safe_deployment": captured["safe_deployment"]}
            states = {}
            for guarantee, reference in evidence.items():
                p = controller.body(reference)
                states[guarantee] = {"status": p["status"], "scope": p["scope"], "receipt": reference}
                if show:
                    show("[" + guarantee.upper() + "] " + json.dumps(states[guarantee], sort_keys=True))
            report = {"profile": PROFILE, "framed": True, "synthesis": "not-authorized",
                      "guarantees": states, "adopted": False, "safe_deployment": "disabled",
                      "protocol_authority": True, "signed_activation": False}
            if show:
                show("[REFUSED] synthesis not authorized; framing grants nothing else")
        else:
            lens = controller.synthesize(scope.subject(), captured["source"])
            result = controller.execute(scope.subject(), lens)
            contract = {"operation": "identity-octets", "field": "",
                        "coverage": "complete-captured-octets", "inverse": True}
            controller.approve_contract(contract)
            fidelity = controller.fidelity(scope.subject(), result["frame"], contract)
            authorization = controller.authorization_receipt(scope.subject(), result["frame"], "adoption")
            deployment = controller.deployment_receipt(scope.subject(), result["frame"])
            evidence = {
                "rapp_integrity": captured["rapp_integrity"], "observation": captured["observation"],
                "semantic_fidelity": fidelity, "current_authorization": authorization, "safe_deployment": deployment,
            }
            states = {}
            for guarantee, reference in evidence.items():
                receipt = controller.body(reference)
                states[guarantee] = {"status": receipt["status"], "scope": receipt["scope"], "receipt": reference}
                if show:
                    show("[" + guarantee.upper() + "] " + json.dumps(states[guarantee], sort_keys=True))
            adopted = False
            if fixture is None:
                request, frontier = controller.request_adoption(scope.subject(), result["frame"], fidelity,
                    contract, "synthetic-inert-view", integrity=result["rapp_integrity"],
                    observation=captured["observation"])
                controller.adopt(scope.subject(), request, frontier)
                controller.materialize(scope.subject())
                adopted = True
            report = {"profile": PROFILE, "brand": "RAPP Workspace/1",
                      "status": "core", "protocol_authority": True, "guarantees": states,
                      "adopted_inert_captured_view": adopted, "native_rebinding": False,
                      "learned_semantic_capability": "disabled-unproven", "signed_activation": False}
        verified = controller.verify_history()
        require(verified["frames"] > 0, "zero integrity evidence")
        scan_method = "canonical-parent-in-memory"
        if "materialization" in allowed:
            controller.export_frames(controller.path / "evidence")
            command = [sys.executable, "-B", str(core.path / "rapp_check.py"), str(controller.path / "evidence"), "--json"]
            completed = subprocess.run(command, capture_output=True, text=True)
            require(completed.returncode == 0, "canonical frame integrity scan failed")
            scanned = json.loads(completed.stdout)
            require(scanned["verdict"] == "COMPLIANT" and not scanned["findings"], "invalid integrity evidence")
            scan_method = "canonical-rapp-check-on-authorized-local-export"
        report.update(rapp_frames_verified=verified["frames"], scanner_scope="RAPP-integrity-only",
                      activation_mode="synthetic", activation_authenticated=False,
                      scan_method=scan_method, current_authority_from_graph=False, external_effects="disabled")
        write_file(output / "report.json", encode(report))
        if show:
            show("[RESULT] " + json.dumps(report, sort_keys=True))
        return report
    finally:
        controller.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rapp1-path", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path(".validation/workspace1-core-safe-demo"))
    parser.add_argument("--fixture", type=Path)
    parser.add_argument("--allow-capture", action="store_true")
    parser.add_argument("--allow-retention", action="store_true")
    parser.add_argument("--allow-local-synthesis", action="store_true")
    parser.add_argument("--allow-materialization", action="store_true")
    args = parser.parse_args()
    require(not args.output.is_absolute() and ".." not in args.output.parts and args.output != Path("."),
            "owned relative output required")
    rights = None
    if args.fixture is not None:
        # No filesystem access to fixture occurs before these separate explicit grants.
        require(args.allow_capture and args.allow_retention,
                "explicit --allow-capture and --allow-retention required before source access")
        rights = {"capture", "retention"}
        if args.allow_local_synthesis:
            rights.add("local_synthesis")
        if args.allow_materialization:
            rights.add("materialization")
    run_demo(Parent(args.rapp1_path), args.output, fixture=args.fixture, rights=rights)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (Refusal, ValueError, OSError) as error:
        print("REFUSED: " + json.dumps(str(error), ensure_ascii=True), file=sys.stderr)
        raise SystemExit(1)
