"""Import and bind the approved SoftwareCo/MicroSOL handshake fixture."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from common import (
    PROFILE,
    ROOT,
    Parent,
    SchemaSet,
    read_file,
    require,
    sha,
    wave,
    write_file,
)
from validator import (
    artifact_descriptor,
    compile_static_agent,
    generation_receipt,
    validate_compatibility,
    validate_handshake_package,
)

EXPECTED = {
    "HIVE-INTEROPERABILITY.md": "4ca6674ee491af0a09b6c333c9f24763face5f22462ce0b454a0ce4c84793932",
    "handshakes/softwarecoellc-vteam-hive/1.json": "0c52264b81bf88dd8555defa9363a23d8eb8ef85c3c12f66ddcaaabfc85a8882",
    "handshakes/softwarecoellc-vteam-hive/agent.py": "679fff9531c0c8b13457d594f746c45da28925a7c1be40473e8ca00823db8671",
    "handshakes/microsol-target-finalizer/agent.py": "c056339f90fdd4e604dbefa40291f1b7b22946d26749b36230bb3b29dd8e2296",
}
FIXTURE = ROOT / "fixtures/softwarecoellc-vteam-hive"
INSTANCE = "rappid:@fixture/rapp-work-compatibility:" + "2" * 64
SOURCE = "rappid:@fixture/softwareco-vteam:" + "3" * 64
WORLD = "softwarecoellc-vteam-hive-fixture"
UTC = ["2030-01-01T00:00:00.000Z", "2030-01-01T00:00:01.000Z", "2030-01-02T00:00:00.000Z"]


def run_agent(path: Path, request: object) -> dict:
    process = subprocess.run(
        [sys.executable, "-I", "-B", str(path)],
        cwd=path.parent,
        input=json.dumps(request, sort_keys=True, separators=(",", ":")).encode("utf-8"),
        capture_output=True,
        check=False,
        timeout=30,
    )
    require(process.returncode == 0, "fixture agent refused")
    value = json.loads(process.stdout)
    require(
        value.get("ok") is True
        and value.get("authority") is False
        and value.get("executed_effects") == 0,
        "fixture agent produced unsafe output",
    )
    return value


def restrictions() -> dict:
    return {
        "rights": {
            "capture": True,
            "local_synthesis": True,
            "model_submission": False,
            "retention": True,
            "redistribution": False,
            "adoption": False,
            "materialization": False,
            "execution": False,
        },
        "privacy": "godd",
        "audience": ["fixture-owner"],
        "hashes_sensitive": True,
        "repository_content_is_instructions": False,
        "grants_authority": False,
        "authorizes_effects": False,
    }


def bounds() -> dict:
    return {
        "max_input_bytes": 1024 * 1024,
        "max_output_bytes": 2 * 1024 * 1024,
        "max_files": 512,
        "max_frames": 256,
        "max_lenses": 8,
        "max_candidates": 32,
        "max_cross_size": 3,
        "max_depth": 4,
        "max_rounds": 4,
        "max_model_calls": 0,
        "max_tool_calls": 16,
    }


def source_payload(operation: str, sequence: int) -> dict:
    record = {
        "schema": "softwarecoellc-vteam-hive-" + operation + "/1",
        "authority": False,
        "value": operation,
    }
    inventory = {
        "schema": "microsol-emitted-inventory/1",
        "role": "evidence",
        "authority": False,
        "artifacts": [
            {
                "path": operation + ".json",
                "bytes": len(operation),
                "sha256": sha(operation.encode("utf-8")),
            }
        ],
    }
    request = {"operation": operation, "sequence": sequence, "record": record}
    return {
        "authority": False,
        "inventory": inventory,
        "operation": operation,
        "profile": "microsol-project/1",
        "project": "softwarecoellc-vteam-hive",
        "record": record,
        "request_hash": sha(json.dumps(request, sort_keys=True).encode("utf-8")),
        "request_id": f"softwarecoellc-{operation}-{sequence}",
        "sequence": sequence,
    }


def receipt(
    core: Parent,
    *,
    pass_role: str,
    agent: dict,
    request: object,
    result: object,
    activation: dict,
    runtime: dict,
) -> dict:
    value = {
        "schema": PROFILE + "/transformation-receipt",
        "instance_rappid": INSTANCE,
        "world_id": WORLD,
        "activation_mode": "synthetic",
        "activation": activation,
        "restrictions": restrictions(),
        "pass_role": pass_role,
        "agent": agent,
        "request": core.particle(request),
        "result": core.particle(result),
        "policy": core.particle({"fixture": True, "effects": False}),
        "runtime": runtime,
        "model_receipt": None,
        "atomic_file_placement": True,
        "captured_bytes_executed": True,
        "model_calls": 0,
        "tool_calls": 0,
        "executed_effects": 0,
        "unloaded": True,
        "grants_authority": False,
    }
    SchemaSet().validate(value, "transformation-receipt.schema.json")
    return value


def generate(source: Path, rapp1_path: Path) -> None:
    for relative, expected in EXPECTED.items():
        require(sha(read_file(source / relative)) == expected, "approved Bill source pin mismatch: " + relative)
    core = Parent(rapp1_path)
    FIXTURE.mkdir(parents=True, exist_ok=True)
    handshake_raw = read_file(source / "handshakes/softwarecoellc-vteam-hive/1.json")
    source_agent_raw = read_file(source / "handshakes/softwarecoellc-vteam-hive/agent.py")
    target_agent_raw = read_file(source / "handshakes/microsol-target-finalizer/agent.py")
    write_file(FIXTURE / "handshake.json", handshake_raw)
    write_file(FIXTURE / "source-agent.py", source_agent_raw)
    write_file(FIXTURE / "target-finalizer.py", target_agent_raw)
    handshake = json.loads(handshake_raw)

    source_agent = artifact_descriptor(
        core,
        "fixtures/softwarecoellc-vteam-hive/source-agent.py",
        source_agent_raw,
        role="source-lens-agent",
        media_type="text/x-python",
    )
    target_agent = artifact_descriptor(
        core,
        "fixtures/softwarecoellc-vteam-hive/target-finalizer.py",
        target_agent_raw,
        role="target-finalizer-agent",
        media_type="text/x-python",
    )
    handshake_artifact = artifact_descriptor(
        core,
        "fixtures/softwarecoellc-vteam-hive/handshake.json",
        handshake_raw,
        role="handshake-metadata",
        media_type="application/json",
    )
    runtime_raw = read_file(ROOT / "runtime-manifest.json")
    runtime = core.particle(json.loads(runtime_raw))
    activation_value = {"fixture": "softwarecoellc-vteam-hive", "mode": "synthetic"}
    activation = core.particle(activation_value)

    stream = SOURCE + ":project-wild-hive"
    opened = core.r.build_frame(
        "memory.save",
        stream,
        0,
        UTC[0],
        source_payload("open", 0),
        None,
    )
    published = core.r.build_frame(
        "memory.save",
        stream,
        1,
        UTC[1],
        source_payload("publish", 1),
        opened["payload_hash"],
    )
    write_file(FIXTURE / "source-frames/00000000.json", core.octets(opened))
    write_file(FIXTURE / "source-frames/00000001.json", core.octets(published))

    source_results = []
    receipts = []
    intent = {
        "schema": PROFILE + "/fixture-intent",
        "handshake_sha256": sha(handshake_raw),
        "source_profile": handshake["source_match"]["profile"],
        "target_profile": handshake["target"]["profile"],
        "mode": "partial-read-only",
    }
    intent_hash = core.particle(intent)["hash"]
    for index, frame in enumerate((opened, published)):
        source_request = {"direction": "source-to-target", "value": frame}
        source_result = run_agent(FIXTURE / "source-agent.py", source_request)
        source_receipt = receipt(
            core,
            pass_role="source-lens",
            agent=source_agent,
            request=source_request,
            result=source_result,
            activation=activation,
            runtime=runtime,
        )
        target_request = {
            "candidate": source_result["result"],
            "context": {
                "compatibility_intent_hash": intent_hash,
                "handshake_id": handshake["id"],
                "handshake_sha256": sha(handshake_raw),
                "source_agent_sha256": sha(source_agent_raw),
                "target_profile": handshake["target"]["profile"],
            },
        }
        target_result = run_agent(FIXTURE / "target-finalizer.py", target_request)
        target_receipt = receipt(
            core,
            pass_role="target-finalizer",
            agent=target_agent,
            request=target_request,
            result=target_result,
            activation=activation,
            runtime=runtime,
        )
        source_results.append(target_result["result"])
        receipts.extend((source_receipt, target_receipt))
        write_file(
            FIXTURE / f"transformation-receipts/{index:08d}-source.json",
            core.octets(source_receipt),
        )
        write_file(
            FIXTURE / f"transformation-receipts/{index:08d}-target.json",
            core.octets(target_receipt),
        )

    qualification = {
        "schema": PROFILE + "/source-qualification",
        "repository": handshake["provenance"]["first_encounter_repository"],
        "commit": handshake["provenance"]["first_encounter_commit"],
        "verified_frames": 2,
        "verified_artifacts": 9,
        "qualification_status": "externally-verified-summary",
        "source_heads_bundled": False,
        "authority": False,
    }
    SchemaSet().validate(qualification, "source-qualification.schema.json")
    write_file(FIXTURE / "source-qualification.json", core.octets(qualification))

    capabilities = sorted(handshake["capabilities"])
    supported = sum(
        handshake["capabilities"][name] in {"verified", "available-on-exhaust"}
        for name in capabilities
    )
    gaps = sorted(
        f"{name}:{handshake['capabilities'][name]}"
        for name in capabilities
        if handshake["capabilities"][name] not in {"verified", "available-on-exhaust"}
    )
    source_inventory = {
        "schema": PROFILE + "/fixture-source-inventory",
        "frames": [wave(opened), wave(published)],
        "qualification": core.particle(qualification),
    }
    host_tests = {
        "suite": "protocols/rapp-work-compatibility/1/tests/test_profile.py",
        "independent": True,
    }
    mutation_tests = {
        "controls": sorted(handshake["rehearsal"]["mutation_controls"]),
        "generated": False,
    }
    record = {
        "schema": PROFILE + "/compatibility",
        "instance_rappid": INSTANCE,
        "world_id": WORLD,
        "activation_mode": "synthetic",
        "activation": activation,
        "restrictions": restrictions(),
        "status": "read-only",
        "source": {
            "rappid": SOURCE,
            "stream_id": stream,
            "head": {
                "stream_id": stream,
                "seq": published["seq"],
                "utc": published["utc"],
                "payload_hash": published["payload_hash"],
                "frame_hash": published["frame_hash"],
            },
            "profile": handshake["source_match"]["profile"],
            "capabilities": capabilities,
            "repository": handshake["provenance"]["first_encounter_repository"],
            "git_commit": handshake["provenance"]["first_encounter_commit"],
            "inventory": core.particle(source_inventory),
        },
        "target": {
            "profile": handshake["target"]["profile"],
            "operations": sorted(handshake["target"]["operations"]),
        },
        "lens": {
            "host": "global-rapp-brainstem",
            "source_agent": source_agent,
            "target_agent": target_agent,
            "passes": ["source-lens", "target-finalizer"],
            "receipts": [core.particle(value) for value in receipts],
            "native_session_persisted": False,
            "brainstem_modified": False,
        },
        "static_program": {
            "bundle": None,
            "entrypoint": None,
            "generation_receipt": None,
            "model_calls": 0,
        },
        "coverage": {
            "supported": supported,
            "required": len(capabilities),
            "basis_points": supported * 10000 // len(capabilities),
            "gaps": gaps,
            "unknowns": [
                "membership and write authority remain unavailable",
                "source heads are represented by synthetic fixture Frames",
            ],
            "scenario": core.particle(qualification),
        },
        "lineage": {
            "parents": [wave(published)],
            "mutation_manifest": None,
            "reverse_ancestry": None,
            "previous_compatibility": None,
            "trigger_exhaust": None,
        },
        "qualification": {
            "rehearsal": core.particle(handshake["rehearsal"]),
            "host_tests": core.particle(host_tests),
            "mutation_tests": core.particle(mutation_tests),
            "canary": None,
            "generated_tests_are_independent_proof": False,
        },
        "bounds": bounds(),
        "grants_authority": False,
    }
    validate_compatibility(record)
    frame = core.r.build_frame(
        "body.pulse",
        INSTANCE,
        0,
        UTC[2],
        {"profile": PROFILE, "operation": "compatibility", "record": record},
        None,
    )
    write_file(FIXTURE / "compatibility-frame.json", core.octets(frame))

    static_agent = compile_static_agent(frame, handshake)
    write_file(FIXTURE / "static-agent.py", static_agent)
    compiler_raw = read_file(ROOT / "reference/validator.py")
    compiler = artifact_descriptor(
        core,
        "reference/validator.py",
        compiler_raw,
        role="static-agent-compiler",
        media_type="text/x-python",
    )
    generation = generation_receipt(
        core,
        frame,
        compiler,
        sha(runtime_raw),
        "fixtures/softwarecoellc-vteam-hive/static-agent.py",
        static_agent,
        host_tests,
    )
    write_file(FIXTURE / "generation-receipt.json", core.octets(generation))
    static_descriptor = artifact_descriptor(
        core,
        "fixtures/softwarecoellc-vteam-hive/static-agent.py",
        static_agent,
        role="locked-static-agent",
        media_type="text/x-python",
    )
    package = {
        "schema": PROFILE + "/handshake-package",
        "handshake_id": "softwarecoellc-vteam-hive-microsol-project-1",
        "version": 1,
        "status": "owner-approved-private",
        "source_profile": handshake["source_match"]["profile"],
        "target_profile": handshake["target"]["profile"],
        "handshake": handshake_artifact,
        "source_agent": source_agent,
        "target_agent": target_agent,
        "static_agent": static_descriptor,
        "generation_receipt": core.particle(generation),
        "compatibility_template": core.particle(record),
        "rehearsal": core.particle(handshake["rehearsal"]),
        "mutation_tests": core.particle(mutation_tests),
        "source_qualification": core.particle(qualification),
        "private_hive_object_kind": "rapp-work-compatibility/1-handshake-program",
        "authority": False,
    }
    validate_handshake_package(package)
    write_file(FIXTURE / "package.json", core.octets(package))
    fixture_index = {
        "schema": PROFILE + "/fixture-index",
        "source": {
            "workspace": source.name,
            "contract_sha256": EXPECTED["HIVE-INTEROPERABILITY.md"],
        },
        "files": [
            {
                "path": path.relative_to(FIXTURE).as_posix(),
                "sha256": sha(read_file(path)),
                "bytes": len(read_file(path)),
            }
            for path in sorted(FIXTURE.rglob("*"))
            if path.is_file() and path.name != "fixture-index.json"
        ],
        "authority": False,
    }
    write_file(FIXTURE / "fixture-index.json", core.octets(fixture_index))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--rapp1-path", type=Path, required=True)
    arguments = parser.parse_args()
    generate(arguments.source, arguments.rapp1_path)
    print("Bill handshake fixture: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
