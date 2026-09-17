"""Generate the reproducible SoftwareCo wild-handshake fixture and package."""

from __future__ import annotations

import argparse
import base64
import json
from pathlib import Path
from typing import Any

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from compatibility import (
    H,
    POLICY,
    PROFILE,
    build_frame,
    canonical,
    compiler_bytes,
    digest,
    generate_static_agent,
    keyed_rappid,
    run_agent,
    spki_bytes,
    strict_file,
)


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "fixtures" / "softwarecoellc-vteam-hive"
HANDSHAKE_PATH = FIXTURE / "handshakes" / "softwarecoellc-vteam-hive" / "1.json"
SOURCE_AGENT_PATH = FIXTURE / "handshakes" / "softwarecoellc-vteam-hive" / "agent.py"
TARGET_AGENT_PATH = FIXTURE / "handshakes" / "microsol-target-finalizer" / "agent.py"
QUALIFICATION_PATH = FIXTURE / "qualification.json"
BINDINGS_PATH = ROOT / "bindings.json"
SCHEMA_PACKAGE_PATH = "schemas/rapp-federation-autobest-1.schema.json"
STATIC_PATH = FIXTURE / "static" / "agent.py"
GENERATION_PATH = FIXTURE / "static" / "generation-receipt.json"
COMPATIBILITY_PATH = FIXTURE / "compatibility" / "frame.json"
EXHAUST_PATH = FIXTURE / "compatibility" / "exhaust.json"
SCHEMA_COPY_PATH = FIXTURE / SCHEMA_PACKAGE_PATH
TRACE_PATH = FIXTURE / "learning-trace.json"
SEARCH_PATH = FIXTURE / "lens-search.json"
MUTATIONS_PATH = FIXTURE / "mutation-tests.json"
PACKAGE_PATH = FIXTURE / "package-manifest.json"
OFFER_PATH = FIXTURE / "mutation-offer.json"
DOCUMENT_PATH = FIXTURE / "fixture.json"
SOURCE_COMMIT = "f66da3d879b53a439bc87de764d79f68ceec048a"


def object_file(path: Path) -> dict[str, Any]:
    return json.loads(strict_file(path))


def private_key(label: str) -> Ed25519PrivateKey:
    seed = bytes.fromhex(digest(("PUBLIC FIXTURE ONLY: " + label).encode("utf-8")))
    return Ed25519PrivateKey.from_private_bytes(seed)


def frame_head(frame: dict[str, Any]) -> dict[str, Any]:
    return {
        "stream_id": frame["stream_id"],
        "seq": frame["seq"],
        "payload_hash": frame["payload_hash"],
        "frame_hash": frame["frame_hash"],
    }


def source_payload(operation: str, sequence: int) -> dict[str, Any]:
    if operation == "open":
        record = {
            "schema": "softwarecoellc-vteam-hive-authority-open/1",
            "authority": False,
            "goal": "Open a synthetic-safe partial Hive fixture.",
        }
        artifact = {
            "path": "manifest.json",
            "bytes": 82,
            "sha256": digest(b'{"authority":false,"schema":"wild-hive/1","status":"partial"}\n'),
        }
    else:
        record = {
            "schema": "softwarecoellc-private-git-publication/1",
            "repository": "example/wild-hive",
            "visibility": "private",
            "authority": False,
        }
        artifact = {
            "path": "publication.json",
            "bytes": 144,
            "sha256": digest(
                b'{"authority":false,"repository":"example/wild-hive","schema":"softwarecoellc-private-git-publication/1","visibility":"private"}\n'
            ),
        }
    return {
        "authority": False,
        "inventory": {
            "schema": "microsol-emitted-inventory/1",
            "role": "evidence",
            "authority": False,
            "artifacts": [artifact],
        },
        "operation": operation,
        "profile": "microsol-project/1",
        "project": "softwarecoellc-vteam-hive-fixture",
        "record": record,
        "request_hash": H(
            "rapp/1:particle",
            {"operation": operation, "sequence": sequence, "record": record},
        ),
        "request_id": f"softwarecoellc-vteam-hive-{operation}-{sequence}",
        "sequence": sequence,
    }


def trace_document() -> dict[str, Any]:
    specifications = [
        (
            "intent",
            "user-authoritative",
            "compatibility",
            "partial-rapp1-hive-interop",
            [],
            [],
        ),
        (
            "assistant-proposal",
            "assistant-proposal",
            "blanket-refusal",
            "native-hive-required",
            [],
            [],
        ),
        (
            "user-correction",
            "user-authoritative",
            "partial-compatibility",
            "incomplete-hive-preferred",
            [],
            [],
        ),
        (
            "measured-result",
            "measured-evidence",
            "signed-stream",
            "two-frames-nine-artifacts",
            [],
            [],
        ),
        (
            "assumption-superseded",
            "derived-invariant",
            "blanket-refusal",
            "native-hive-required-superseded",
            [],
            [],
        ),
        (
            "successor-invariant",
            "derived-invariant",
            "compatibility",
            "verified-partial-read-only",
            [],
            [],
        ),
    ]
    events: list[dict[str, Any]] = []
    correction_hash = None
    proposal_hash = None
    previous = None
    for index, (event_type, authority, subject, commitment, references, supersedes) in enumerate(specifications):
        if event_type == "assistant-proposal":
            proposal_hash = previous
        if event_type == "assumption-superseded":
            supersedes = [events[1]["event_hash"]]
        if event_type == "successor-invariant":
            references = [correction_hash, events[3]["event_hash"]]
        body = {
            "seq": index,
            "prev_event_hash": previous,
            "type": event_type,
            "authority_class": authority,
            "subject": subject,
            "source_commitment": H(PROFILE + ":source-event", {"salt": f"fixture-{index}", "value": commitment}),
            "references": [value for value in references if value is not None],
            "supersedes": [value for value in supersedes if value is not None],
            "privacy_safe": True,
        }
        event = {**body, "event_hash": H(PROFILE + ":trace-event", body)}
        events.append(event)
        previous = event["event_hash"]
        if event_type == "user-correction":
            correction_hash = event["event_hash"]
    assert correction_hash is not None
    return {
        "schema": PROFILE + "/learning-trace",
        "events": events,
        "correction_frontier_hash": H(PROFILE + ":correction-frontier", [correction_hash]),
        "raw_transcript_persisted": False,
        "hidden_reasoning_persisted": False,
        "native_session_persisted": False,
    }


def lens_search_document(ancestor: str, source_agent: str, target_agent: str) -> dict[str, Any]:
    return {
        "schema": PROFILE + "/lens-search",
        "ancestor": ancestor,
        "use_case": "partial-hive-read",
        "lens_pins": sorted([source_agent, target_agent]),
        "max_lenses": 8,
        "max_candidates": 32,
        "max_cross_size": 4,
        "max_depth": 3,
        "max_rounds": 6,
        "beam_width": 16,
        "pareto_width": 16,
        "root_budget_hash": H(
            PROFILE + ":root-budget",
            {"time_seconds": 120, "model_calls": 0, "tools": 0, "output_bytes": 1 << 20},
        ),
        "stop_reasons": [
            "all-candidates-refused",
            "no-compatible-cross",
            "no-progress",
            "repeated-frontier",
            "root-budget-exhausted",
            "scenario-threshold-met",
            "user-stop",
        ],
        "fitness_is_universal_truth": False,
    }


def hotload_receipt(role: str, agent_hash: str, request: dict[str, Any], response: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema": PROFILE + "/hotload-receipt",
        "role": role,
        "agent_sha256": agent_hash,
        "request_sha256": digest(canonical(request)),
        "result_sha256": digest(canonical(response)),
        "policy_sha256": H(PROFILE + ":policy", POLICY),
        "model_calls": 0,
        "network_calls": 0,
        "executed_effects": 0,
        "native_session_persisted": False,
        "brainstem_modified": False,
        "plugin_registered": False,
        "unloaded": True,
        "authority": False,
    }


def fixture_material() -> dict[str, Any]:
    bindings = object_file(BINDINGS_PATH)
    handshake = object_file(HANDSHAKE_PATH)
    qualification = object_file(QUALIFICATION_PATH)
    source_agent = strict_file(SOURCE_AGENT_PATH)
    target_agent = strict_file(TARGET_AGENT_PATH)
    source_agent_hash = digest(source_agent)
    target_agent_hash = digest(target_agent)
    assert digest(strict_file(HANDSHAKE_PATH)) == bindings["wild_handshake"]["profile_sha256"]
    assert source_agent_hash == bindings["wild_handshake"]["source_agent_sha256"]
    assert target_agent_hash == bindings["wild_handshake"]["target_finalizer_sha256"]

    source_key = private_key("softwarecoellc source")
    source_identity = keyed_rappid("fixture-source", "hive", source_key.public_key())
    source_stream = source_identity + ":project-wild-hive"
    source_frames = [
        build_frame(
            source_payload("open", 0),
            identity=source_identity,
            private_key=source_key,
            stream=source_stream,
            seq=0,
            utc="2030-01-01T00:00:00.000Z",
        )
    ]
    source_frames.append(
        build_frame(
            source_payload("publish", 1),
            identity=source_identity,
            private_key=source_key,
            stream=source_stream,
            seq=1,
            utc="2030-01-01T00:00:01.000Z",
            previous=source_frames[0],
        )
    )

    intent = {
        "schema": PROFILE + "/intent",
        "handshake_id": handshake["id"],
        "handshake_sha256": bindings["wild_handshake"]["profile_sha256"],
        "source_head": frame_head(source_frames[-1]),
        "target_profile": handshake["target"]["profile"],
        "mode": "partial-read-only",
        "authority": False,
    }
    intent_hash = H("rapp/1:particle", intent)
    pass_outputs = []
    receipts = []
    for frame in source_frames:
        source_request = {"direction": "source-to-target", "value": frame}
        source_response = run_agent(SOURCE_AGENT_PATH, source_request)
        source_receipt = hotload_receipt("source-lens", source_agent_hash, source_request, source_response)
        target_request = {
            "candidate": source_response["result"],
            "context": {
                "compatibility_intent_hash": intent_hash,
                "handshake_id": handshake["id"],
                "handshake_sha256": bindings["wild_handshake"]["profile_sha256"],
                "source_agent_sha256": source_agent_hash,
                "target_profile": handshake["target"]["profile"],
            },
        }
        target_response = run_agent(TARGET_AGENT_PATH, target_request)
        target_receipt = hotload_receipt("target-finalizer", target_agent_hash, target_request, target_response)
        pass_outputs.append(
            {
                "source": source_response["result"],
                "target": target_response["result"],
            }
        )
        receipts.extend([source_receipt, target_receipt])

    trace = trace_document()
    trace_bytes = canonical(trace)
    search = lens_search_document(source_frames[-1]["frame_hash"], source_agent_hash, target_agent_hash)
    search_bytes = canonical(search)
    capabilities = []
    for name, status in sorted(handshake["capabilities"].items()):
        tier = (
            "brainstem-translation-candidate"
            if status == "available-on-exhaust"
            else "signed-stream-inference"
            if status in {"verified", "partial"}
            else "declared-descriptor"
        )
        capabilities.append(
            {
                "name": name.replace("_", "-"),
                "status": status,
                "tier": tier,
                "coverage_bps": 10000 if status == "verified" else 5000 if status == "partial" else 0,
                "evidence": [source_frames[-1]["frame_hash"]] if status in {"verified", "partial"} else [],
            }
        )
    supported = sum(item["status"] in {"verified", "available-on-exhaust"} for item in capabilities)
    gaps = sorted(
        item["name"]
        for item in capabilities
        if item["status"] not in {"verified", "available-on-exhaust"}
    )
    compiler_hash = digest(compiler_bytes())
    record = {
        "schema": PROFILE + "/compatibility",
        "role": "bidirectional-static-handshake",
        "handshake": {
            "id": handshake["id"],
            "version": handshake["version"],
            "sha256": bindings["wild_handshake"]["profile_sha256"],
            "status": handshake["status"],
        },
        "source": {
            "repository": qualification["source_repository"],
            "commit": qualification["source_commit"],
            "snapshot_hash": H(
                PROFILE + ":source-snapshot",
                {
                    "commit": qualification["source_commit"],
                    "head": frame_head(source_frames[-1]),
                    "qualification": qualification,
                },
            ),
            "rappid": source_identity,
            "stream_id": source_stream,
            "qualification_head": frame_head(source_frames[-1]),
            "profile": handshake["source_match"]["profile"],
        },
        "target": {
            "profile": handshake["target"]["profile"],
            "operations": sorted(handshake["target"]["operations"]),
        },
        "profile_pins": [
            {
                "name": bindings["federation"]["profile"],
                "spec_sha256": bindings["federation"]["spec_sha256"],
                "schema_sha256": bindings["federation"]["schema_sha256"],
                "status": "verified",
            },
            {
                "name": bindings["hive"]["profile"],
                "spec_sha256": bindings["hive"]["spec_sha256"],
                "schema_sha256": bindings["hive"]["schema_sha256"],
                "status": "verified",
            },
            {
                "name": bindings["workspace"]["profile"],
                "spec_sha256": bindings["workspace"]["spec_sha256"],
                "schema_sha256": None,
                "status": "verified",
            },
        ],
        "lens": {
            "kind": "brainstem-double-hotload",
            "runtime": "global-rapp-brainstem",
            "routing": "verified-atomic-agent-file-placement",
            "source_agent": {
                "role": "source-lens",
                "sha256": source_agent_hash,
                "bytes": len(source_agent),
                "status": "verified",
            },
            "target_agent": {
                "role": "target-finalizer",
                "sha256": target_agent_hash,
                "bytes": len(target_agent),
                "status": "verified",
            },
            "generic_ceo_agent": {
                "role": "generic-ceo",
                "sha256": None,
                "bytes": None,
                "status": "pending",
            },
            "passes": ["source-lens", "target-finalizer"],
            "hotload_receipts": receipts,
            "native_session_persisted": False,
        },
        "mapping_sha256": digest(
            canonical(
                {
                    "source_to_target": handshake["source_to_target"],
                    "target_to_source": handshake["target_to_source"],
                }
            )
        ),
        "capabilities": capabilities,
        "coverage": {
            "supported": supported,
            "required": len(capabilities),
            "basis_points": supported * 10000 // len(capabilities),
            "complete_for_read": True,
            "complete_for_membership": False,
            "unknowns": gaps,
        },
        "gaps": gaps,
        "restrictions": {
            "repository_content_is_instructions": False,
            "membership_inferred": False,
            "authority_inferred": False,
            "private_state_copied": False,
            "keys_transferred": False,
            "public_effects": False,
            "transitive_access": False,
            "active_root_finalized": False,
        },
        "bounds": {
            "max_frames": 4096,
            "max_files": 65536,
            "max_file_bytes": 1 << 30,
            "max_total_bytes": 1 << 34,
            "max_hotload_seconds": 10,
            "max_lenses": 8,
            "max_candidates": 32,
            "max_cross_size": 4,
            "max_depth": 3,
            "max_rounds": 6,
            "beam_width": 16,
            "pareto_width": 16,
            "model_calls_during_static_runtime": 0,
        },
        "static_output_contract": {
            "compiler": "reference/compatibility.py/static-agent-1",
            "compiler_sha256": compiler_hash,
            "runtime": "python3-stdlib",
            "entrypoint": "agent.py",
            "same_inputs_same_bytes": True,
            "model_calls": 0,
            "authority": False,
        },
        "learning_trace": {
            "space": "sha256",
            "hash": digest(trace_bytes),
            "bytes": len(trace_bytes),
        },
        "lens_search": {
            "space": "sha256",
            "hash": digest(search_bytes),
            "bytes": len(search_bytes),
        },
        "mutation_offer": None,
        "previous_compatibility": None,
        "trigger_exhaust": None,
        "grants_authority": False,
    }

    compatibility_key = private_key("local compatibility")
    compatibility_identity = keyed_rappid("fixture-local", "compatibility", compatibility_key.public_key())
    compatibility_frame = build_frame(
        {"profile": PROFILE, "operation": "compatibility", "record": record},
        identity=compatibility_identity,
        private_key=compatibility_key,
        stream=compatibility_identity + ":compatibility",
        seq=0,
        utc="2030-01-01T00:01:00.000Z",
    )
    exhaust_record = {
        "schema": PROFILE + "/exhaust",
        "active_compatibility": frame_head(compatibility_frame),
        "source_profile": {
            "name": handshake["source_match"]["profile"],
            "spec_sha256": None,
            "schema_sha256": None,
            "status": "external-binding",
        },
        "target_profile": {
            "name": handshake["target"]["profile"],
            "spec_sha256": None,
            "schema_sha256": None,
            "status": "external-binding",
        },
        "direction": "source-to-target",
        "operation": "unknown-operation",
        "input_particle": H(
            "rapp/1:particle",
            {
                "profile": handshake["source_match"]["profile"],
                "operation": "unknown-operation",
                "private_payload_persisted": False,
            },
        ),
        "output_particle": None,
        "gap_kind": "operation",
        "gap_commitment": H(
            PROFILE + ":gap",
            {"operation": "unknown-operation", "source_head": frame_head(source_frames[-1])},
        ),
        "coverage": record["coverage"],
        "loss_class": "partial-unproven",
        "restriction": "generic-ceo-pending",
        "bounds_consumed": H(
            PROFILE + ":bounds-consumed",
            {"static_model_calls": 0, "jit_model_calls": 0, "attempts": 1},
        ),
        "retryable": True,
        "privacy_safe": True,
        "inferred_patch": False,
        "grants_authority": False,
    }
    exhaust_frame = build_frame(
        {"profile": PROFILE, "operation": "compatibility-exhaust", "record": exhaust_record},
        identity=compatibility_identity,
        private_key=compatibility_key,
        stream=compatibility_identity + ":compatibility",
        seq=1,
        utc="2030-01-01T00:01:01.000Z",
        previous=compatibility_frame,
    )
    static_agent = generate_static_agent(compatibility_frame, handshake)
    generation = {
        "schema": PROFILE + "/generation-receipt",
        "compatibility": frame_head(compatibility_frame),
        "compiler": record["static_output_contract"]["compiler"],
        "compiler_sha256": compiler_hash,
        "runtime": record["static_output_contract"]["runtime"],
        "agent_sha256": digest(static_agent),
        "agent_bytes": len(static_agent),
        "deterministic": True,
        "model_calls": 0,
        "candidate_tests_are_independent_proof": False,
        "host_tests_passed": 12,
        "controlled_mutants_killed": 16,
        "controlled_mutants_survived": 0,
        "authority": False,
    }
    generation_bytes = canonical(generation)
    compatibility_bytes = canonical(compatibility_frame)
    exhaust_bytes = canonical(exhaust_frame)
    mutation_tests = {
        "schema": PROFILE + "/mutation-tests",
        "candidate_tests_are_independent_proof": False,
        "host_tests": [
            "agent-byte-substitution",
            "duplicate-json-key",
            "same-sequence-fork",
            "signature-tamper",
            "source-key-substitution",
            "static-runtime-model-call",
        ],
        "controlled_mutants": [
            "coverage-overclaim",
            "ceo-pin-forgery",
            "authority-true",
            "transitive-access",
            "active-root-finalized",
            "missing-user-correction",
            "forged-user-authority",
            "lineage-gap",
            "path-traversal",
            "symlink-entry",
            "roundtrip-overclaim",
            "candidate-test-self-certification",
            "max-lens-overflow",
            "max-candidate-overflow",
            "unknown-operation-improvisation",
            "federation1-byte-change",
        ],
        "authority": False,
    }
    mutation_bytes = canonical(mutation_tests)
    schema_bytes = strict_file(ROOT / "schema.json")
    inputs = {
        "handshakes/softwarecoellc-vteam-hive/1.json": strict_file(HANDSHAKE_PATH),
        "handshakes/softwarecoellc-vteam-hive/agent.py": source_agent,
        "handshakes/microsol-target-finalizer/agent.py": target_agent,
    }
    package_files = {
        **inputs,
        "compatibility/frame.json": compatibility_bytes,
        "compatibility/exhaust.json": exhaust_bytes,
        "static/agent.py": static_agent,
        "static/generation-receipt.json": generation_bytes,
        "qualification.json": strict_file(QUALIFICATION_PATH),
        "learning-trace.json": trace_bytes,
        "lens-search.json": search_bytes,
        "mutation-tests.json": mutation_bytes,
        SCHEMA_PACKAGE_PATH: schema_bytes,
    }
    roles = {
        "handshakes/softwarecoellc-vteam-hive/1.json": "handshake",
        "handshakes/softwarecoellc-vteam-hive/agent.py": "agent",
        "handshakes/microsol-target-finalizer/agent.py": "agent",
        "compatibility/frame.json": "fixture",
        "compatibility/exhaust.json": "fixture",
        "static/agent.py": "static-agent",
        "static/generation-receipt.json": "receipt",
        "qualification.json": "provenance",
        "learning-trace.json": "fixture",
        "lens-search.json": "fixture",
        "mutation-tests.json": "host-test",
        SCHEMA_PACKAGE_PATH: "schema",
    }
    entries = [
        {
            "path": path,
            "sha256": digest(raw),
            "bytes": len(raw),
            "role": roles[path],
            "regular_file": True,
        }
        for path, raw in sorted(package_files.items())
    ]
    forward = [
        {
            "source_path": path,
            "source_sha256": digest(raw),
            "relation": "retained",
            "target_paths": [path],
            "target_sha256": [digest(raw)],
            "trait": "approved-handshake-input",
            "loss_class": "lossless-direct",
        }
        for path, raw in sorted(inputs.items())
    ]
    reverse = []
    for path, raw in sorted(package_files.items()):
        inherited = path in inputs
        reverse.append(
            {
                "successor_path": path,
                "successor_sha256": digest(raw),
                "class": "inherited" if inherited else "new",
                "source_paths": [path] if inherited else [],
                "source_sha256": [digest(raw)] if inherited else [],
                "inverse_available": inherited,
                "loss_class": "lossless-direct" if inherited else "not-applicable",
            }
        )
    package = {
        "schema": PROFILE + "/artifact-bundle",
        "compatibility_frame": frame_head(compatibility_frame),
        "entrypoint": "static/agent.py",
        "entries": entries,
        "lineage": {
            "source_parents": [
                source_frames[-1]["frame_hash"],
                bindings["wild_handshake"]["profile_sha256"],
            ],
            "forward": forward,
            "reverse": reverse,
            "selected_traits": [
                "bidirectional-static-translation",
                "partial-capability-reporting",
                "strict-rapp1-frame-shape",
            ],
            "omitted_traits": [
                "membership-activation",
                "post-write",
                "revocation-key-rotation",
            ],
            "ancestor_reconstruction": "partial-unproven",
            "roundtrip_claim": False,
        },
        "candidate_tests_are_independent_proof": False,
        "host_tests_required": True,
        "canonical_tests_required": True,
        "controlled_mutants_required": True,
        "grants_authority": False,
    }
    package_bytes = canonical(package)
    offer = {
        "schema": PROFILE + "/mutation-offer",
        "source_parent": source_frames[-1]["frame_hash"],
        "successor_bundle": digest(package_bytes),
        "lineage_hash": H(PROFILE + ":lineage", package["lineage"]),
        "compatibility_frame": compatibility_frame["frame_hash"],
        "static_agent_sha256": digest(static_agent),
        "tests_hash": digest(mutation_bytes),
        "transport": {
            "kind": "git-pr",
            "locator_hash": H(PROFILE + ":transport-locator", "private-pr-not-created"),
            "base_commit": SOURCE_COMMIT,
            "head_commit": SOURCE_COMMIT,
        },
        "grants_authority": False,
        "rewrites_ancestor": False,
        "activates_successor": False,
    }
    document = {
        "schema": PROFILE + "/fixture",
        "warning": "All keys and business data are public synthetic conformance material.",
        "activation": "candidate-not-activated",
        "generic_ceo_agent": "pending",
        "source": {
            "identity": source_identity,
            "public_spki_der_b64": base64.b64encode(spki_bytes(source_key.public_key())).decode("ascii"),
            "frames": source_frames,
        },
        "compatibility": {
            "identity": compatibility_identity,
            "public_spki_der_b64": base64.b64encode(spki_bytes(compatibility_key.public_key())).decode("ascii"),
            "frame": compatibility_frame,
        },
        "exhaust": {
            "frame": exhaust_frame,
        },
        "double_hotload": {
            "intent_hash": intent_hash,
            "receipts": receipts,
            "outputs": pass_outputs,
        },
        "artifacts": {
            "learning_trace_sha256": digest(trace_bytes),
            "lens_search_sha256": digest(search_bytes),
            "static_agent_sha256": digest(static_agent),
            "generation_receipt_sha256": digest(generation_bytes),
            "package_manifest_sha256": digest(package_bytes),
            "mutation_offer_sha256": digest(canonical(offer)),
        },
        "live_binding": {
            "qualification_sha256": digest(canonical(qualification)),
            "signed_frames_verified": qualification["signed_frames_verified"],
            "artifacts_verified": qualification["artifacts_verified"],
            "assurance": qualification["assurance"],
        },
    }
    return {
        "document": document,
        "static_agent": static_agent,
        "generation": generation,
        "trace": trace,
        "search": search,
        "mutations": mutation_tests,
        "package": package,
        "offer": offer,
    }


def outputs(material: dict[str, Any]) -> dict[Path, bytes]:
    return {
        DOCUMENT_PATH: canonical(material["document"]),
        STATIC_PATH: material["static_agent"],
        GENERATION_PATH: canonical(material["generation"]),
        COMPATIBILITY_PATH: canonical(material["document"]["compatibility"]["frame"]),
        EXHAUST_PATH: canonical(material["document"]["exhaust"]["frame"]),
        SCHEMA_COPY_PATH: strict_file(ROOT / "schema.json"),
        TRACE_PATH: canonical(material["trace"]),
        SEARCH_PATH: canonical(material["search"]),
        MUTATIONS_PATH: canonical(material["mutations"]),
        PACKAGE_PATH: canonical(material["package"]),
        OFFER_PATH: canonical(material["offer"]),
    }


def write() -> None:
    material = fixture_material()
    for path, raw in outputs(material).items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
    print("wrote reproducible wild-handshake fixture")


def check() -> None:
    material = fixture_material()
    for path, expected in outputs(material).items():
        if not path.is_file() or path.read_bytes() != expected:
            raise SystemExit(f"{path.relative_to(ROOT)} differs from generated fixture")
    print("wild-handshake fixture: exact generated match")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    arguments = parser.parse_args()
    if arguments.write == arguments.check:
        raise SystemExit("choose exactly one of --write or --check")
    write() if arguments.write else check()
