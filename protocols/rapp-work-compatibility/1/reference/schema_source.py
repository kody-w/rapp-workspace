"""Generate the closed RAPP Work Compatibility/1 schemas."""

from __future__ import annotations

import argparse
import json

from common import PROFILE, ROOT

DRAFT = "https://json-schema.org/draft/2020-12/schema"
URI = "https://github.com/kody-w/rapp-work/raw/main/protocols/rapp-work-compatibility/1/schemas/"
MAX_SAFE = 2**53 - 1


def obj(**properties):
    return {
        "type": "object",
        "properties": properties,
        "required": list(properties),
        "additionalProperties": False,
    }


def text(maximum=512, minimum=0, pattern=r"^[^\u0000-\u001f\u007f]*$"):
    return {
        "type": "string",
        "minLength": minimum,
        "maxLength": maximum,
        "pattern": pattern + r"(?![\s\S])",
    }


def integer(maximum=MAX_SAFE, minimum=0):
    return {"type": "integer", "minimum": minimum, "maximum": maximum}


def array(items, maximum=128, minimum=0):
    return {
        "type": "array",
        "items": items,
        "minItems": minimum,
        "maxItems": maximum,
        "uniqueItems": True,
    }


def ref(name):
    return {"$ref": "common.schema.json#/$defs/" + name}


def fixed(value):
    return {"const": value}


def nullable(value):
    return {"oneOf": [value, {"type": "null"}]}


def record(name, **properties):
    return obj(
        schema=fixed(PROFILE + "/" + name),
        instance_rappid=ref("rappid"),
        world_id=text(128, 1),
        activation_mode={"enum": ["live", "synthetic"]},
        activation=ref("particle"),
        restrictions=ref("restrictions"),
        **properties,
    )


def schemas():
    hash_value = text(64, 64, r"^[0-9a-f]{64}$")
    token = text(128, 1, r"^[a-z0-9]+(?:[._/-][a-z0-9]+)*$")
    rid = text(
        213,
        76,
        r"^rappid:@(?=[^/]{1,39}/)[a-z0-9]+(?:-[a-z0-9]+)*/"
        r"(?=[^:]{1,100}:)[a-z0-9]+(?:-[a-z0-9]+)*:[0-9a-f]{64}$",
    )
    address = lambda space: obj(space=fixed(space), hash=hash_value)
    utc = text(
        24,
        24,
        r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:"
        r"[0-9]{2}:[0-9]{2}\.[0-9]{3}Z$",
    )
    rights = obj(
        capture={"type": "boolean"},
        local_synthesis={"type": "boolean"},
        model_submission={"type": "boolean"},
        retention={"type": "boolean"},
        redistribution={"type": "boolean"},
        adoption={"type": "boolean"},
        materialization={"type": "boolean"},
        execution={"type": "boolean"},
    )
    restrictions = obj(
        rights=rights,
        privacy={"enum": ["godd", "dogg", "neutral"]},
        audience=array(text(128, 1), 32, 1),
        hashes_sensitive=fixed(True),
        repository_content_is_instructions=fixed(False),
        grants_authority=fixed(False),
        authorizes_effects=fixed(False),
    )
    head = obj(
        stream_id=text(512, 1),
        seq=integer(),
        utc=utc,
        payload_hash=hash_value,
        frame_hash=hash_value,
    )
    artifact = obj(
        path=text(1024, 1),
        sha256=hash_value,
        bytes=integer(16 * 1024 * 1024),
        particle=address("rapp/1:particle"),
        role=token,
        media_type=text(128, 1),
        executable=fixed(False),
    )
    bounds = obj(
        max_input_bytes=integer(64 * 1024 * 1024, 1),
        max_output_bytes=integer(64 * 1024 * 1024, 1),
        max_files=integer(10000, 1),
        max_frames=integer(512, 1),
        max_lenses=integer(32, 1),
        max_candidates=integer(128, 1),
        max_cross_size=integer(8, 1),
        max_depth=integer(32, 1),
        max_rounds=integer(16, 1),
        max_model_calls=integer(128),
        max_tool_calls=integer(4096),
    )
    file_ref = obj(
        path=text(1024, 1),
        sha256=hash_value,
        bytes=integer(16 * 1024 * 1024),
        mode={"enum": ["100644", "100755"]},
    )
    common = {
        "$schema": DRAFT,
        "$id": URI + "common.schema.json",
        "$defs": {
            "hash": hash_value,
            "token": token,
            "rappid": rid,
            "wave": address("rapp/1:wave"),
            "particle": address("rapp/1:particle"),
            "head": head,
            "artifact": artifact,
            "restrictions": restrictions,
            "bounds": bounds,
            "file_ref": file_ref,
            "loss_class": {
                "enum": [
                    "lossless-direct",
                    "lossless-retained-delta",
                    "lossy-source-referenced",
                    "lossy-unavailable",
                ]
            },
        },
        "type": "object",
        "properties": {},
        "required": [],
        "additionalProperties": False,
    }
    compatibility = record(
        "compatibility",
        status={"enum": ["candidate", "partial", "read-only", "full"]},
        source=obj(
            rappid=rid,
            stream_id=text(512, 1),
            head=head,
            profile=token,
            capabilities=array(token, 256),
            repository=text(512, 1),
            git_commit=text(64, 40, r"^[0-9a-f]{40,64}$"),
            inventory=ref("particle"),
        ),
        target=obj(profile=token, operations=array(token, 256, 1)),
        lens=obj(
            host=fixed("global-rapp-brainstem"),
            orchestrator_capability=ref("particle"),
            source_agent=artifact,
            target_agent=artifact,
            passes={
                "type": "array",
                "items": {"enum": ["source-lens", "target-finalizer"]},
                "minItems": 2,
                "maxItems": 2,
                "uniqueItems": True,
            },
            receipts=array(ref("particle"), 512),
            native_session_persisted=fixed(False),
            brainstem_modified=fixed(False),
        ),
        static_program=obj(
            bundle=nullable(ref("particle")),
            entrypoint=nullable(artifact),
            generation_receipt=nullable(ref("particle")),
            model_calls=fixed(0),
        ),
        coverage=obj(
            supported=integer(10000),
            required=integer(10000, 1),
            basis_points=integer(10000),
            gaps=array(text(512, 1), 1024),
            unknowns=array(text(512, 1), 1024),
            scenario=ref("particle"),
        ),
        lineage=obj(
            parents=array(ref("wave"), 128, 1),
            mutation_manifest=nullable(ref("particle")),
            reverse_ancestry=nullable(ref("particle")),
            previous_compatibility=nullable(ref("wave")),
            trigger_exhaust=nullable(ref("wave")),
        ),
        qualification=obj(
            rehearsal=ref("particle"),
            host_tests=ref("particle"),
            mutation_tests=ref("particle"),
            canary=nullable(ref("particle")),
            generated_tests_are_independent_proof=fixed(False),
        ),
        bounds=bounds,
        grants_authority=fixed(False),
    )
    exhaust = record(
        "compatibility-exhaust",
        active_compatibility=ref("wave"),
        source_head=head,
        target_head=nullable(head),
        direction={"enum": ["source-to-target", "target-to-source"]},
        code=token,
        locus=text(512, 1),
        missing_coverage=array(text(512, 1), 256),
        loss_class=ref("loss_class"),
        consumed=bounds,
        retryable={"type": "boolean"},
        privacy_safe=fixed(True),
        grants_authority=fixed(False),
    )
    transformation = record(
        "transformation-receipt",
        pass_role={"enum": ["source-lens", "target-finalizer", "static-agent"]},
        agent=artifact,
        request=ref("particle"),
        result=ref("particle"),
        policy=ref("particle"),
        runtime=ref("particle"),
        model_receipt=nullable(ref("particle")),
        atomic_file_placement=fixed(True),
        captured_bytes_executed=fixed(True),
        model_calls=integer(128),
        tool_calls=integer(4096),
        executed_effects=fixed(0),
        unloaded=fixed(True),
        grants_authority=fixed(False),
    )
    generation = {
        "$schema": DRAFT,
        "$id": URI + "static-agent-generation.schema.json",
        **obj(
            schema=fixed(PROFILE + "/static-agent-generation"),
            compatibility=ref("wave"),
            compatibility_payload_hash=ref("hash"),
            compiler=artifact,
            runtime_sha256=ref("hash"),
            options=ref("particle"),
            output=artifact,
            deterministic=fixed(True),
            generated_tests_are_independent_proof=fixed(False),
            tests=ref("particle"),
            grants_authority=fixed(False),
        ),
    }
    artifact_bundle = {
        "$schema": DRAFT,
        "$id": URI + "artifact-bundle.schema.json",
        **obj(
            schema=fixed(PROFILE + "/artifact-bundle"),
            egg_manifest=ref("particle"),
            entrypoint=artifact,
            files=array(artifact, 10000, 1),
            compatibility=ref("wave"),
            generation_receipt=ref("particle"),
            mutation_manifest=ref("particle"),
            reverse_ancestry=ref("particle"),
            producer_tests=ref("particle"),
            host_tests=ref("particle"),
            mutation_tests=ref("particle"),
            migrations=array(artifact, 1024),
            authority=fixed(False),
        ),
    }
    forward_entry = obj(
        source=file_ref,
        disposition={"enum": ["retained", "replaced", "moved", "removed"]},
        targets=array(file_ref, 128),
        content_relation={"enum": ["identical", "derived", "absent"]},
        receipt=ref("particle"),
        traits=array(token, 256),
        loss_class=ref("loss_class"),
    )
    reverse_entry = obj(
        target=file_ref,
        provenance={"enum": ["inherited", "derived", "new"]},
        sources=array(file_ref, 128),
        receipt=ref("particle"),
        inverse_artifacts=array(ref("particle"), 128),
        loss_class=ref("loss_class"),
    )
    mutation_manifest = {
        "$schema": DRAFT,
        "$id": URI + "causal-mutation-manifest.schema.json",
        **obj(
            schema=fixed(PROFILE + "/causal-mutation-manifest"),
            source_parents=array(
                obj(frame=ref("wave"), commit=text(64, 40, r"^[0-9a-f]{40,64}$"), inventory=ref("particle")),
                32,
                1,
            ),
            target_inventory=ref("particle"),
            forward=array(forward_entry, 10000),
            reverse=array(reverse_entry, 10000),
            aggregate_loss_class=ref("loss_class"),
            inverse_artifacts=array(ref("particle"), 10000),
            selected_traits=array(token, 1024),
            omitted_traits=array(token, 1024),
            complete=fixed(True),
        ),
    }
    trace_event = obj(
        seq=integer(),
        previous_event=nullable(ref("particle")),
        kind={
            "enum": [
                "intent",
                "assistant-proposal",
                "user-correction",
                "measured-result",
                "superseded-assumption",
                "successor-invariant",
            ]
        },
        actor_class={
            "enum": [
                "user-authority",
                "owner-authority",
                "assistant-proposal",
                "tool-observation",
                "agent-observation",
                "host-policy",
            ]
        },
        source_refs=array(ref("particle"), 128),
        scope=ref("particle"),
        structured_claim=ref("particle"),
        authority_evidence=nullable(ref("particle")),
        restrictions=restrictions,
    )
    learning_trace = {
        "$schema": DRAFT,
        "$id": URI + "learning-trace.schema.json",
        **obj(
            schema=fixed(PROFILE + "/learning-trace"),
            trigger=ref("particle"),
            events=array(trace_event, 4096, 1),
            decision_frontier=ref("particle"),
            receipt_frontier=ref("particle"),
            unresolved=integer(4096),
            raw_transcript_persisted=fixed(False),
            hidden_reasoning_persisted=fixed(False),
            native_paths_persisted=fixed(False),
            restrictions=restrictions,
        ),
    }
    mutation_offer = record(
        "mutation-offer",
        ancestor_refs=array(ref("wave"), 128, 1),
        successor_bundle=ref("particle"),
        forward_map=ref("particle"),
        reverse_map=ref("particle"),
        compatibility=ref("wave"),
        tests=ref("particle"),
        selected_traits=array(token, 1024),
        omitted_traits=array(token, 1024),
        transport=obj(
            kind={"enum": ["pull-request", "private-hive", "federation", "local"]},
            base=text(512, 1),
            head=text(512, 1),
            evidence=ref("particle"),
        ),
        status=fixed("candidate"),
        grants_authority=fixed(False),
    )
    lens_dimension = record(
        "lens-dimension",
        ancestor=ref("wave"),
        intent=ref("particle"),
        source_agent=artifact,
        target_agent=artifact,
        scope_traits=array(token, 1024),
        parent_dimension=nullable(ref("wave")),
        budget=bounds,
        candidate_limit=integer(16, 1),
        grants_authority=fixed(False),
    )
    candidate_cross = record(
        "candidate-cross",
        parents=array(ref("wave"), 8, 2),
        selected_traits=array(token, 1024),
        omitted_traits=array(token, 1024),
        dependency_evidence=ref("particle"),
        result_bundle=ref("particle"),
        fitness_evidence=ref("particle"),
        lineage=ref("particle"),
        grants_authority=fixed(False),
    )
    evolution = record(
        "evolution-proposal",
        level={"enum": ["handshake", "agent", "compiler", "seed", "protocol"]},
        ancestors=array(ref("wave"), 128, 1),
        candidate_bundle=ref("particle"),
        scenario_corpus=ref("particle"),
        hidden_holdout=ref("particle"),
        controlled_mutants=ref("particle"),
        canary=ref("particle"),
        independent_verification=ref("particle"),
        promotion_target=token,
        automatic_promotion=fixed(False),
        status=fixed("candidate"),
        grants_authority=fixed(False),
    )
    metrics = obj(
        scenarios_total=integer(),
        scenarios_passed=integer(),
        scenarios_failed=integer(),
        holdouts_total=integer(),
        holdouts_passed=integer(),
        holdouts_failed=integer(),
        mutants_total=integer(),
        mutants_killed=integer(),
        mutants_survived=integer(),
        prior_regressions_total=integer(),
        prior_regressions_preserved=integer(),
        prior_regressions_lost=integer(),
        coverage_items=integer(),
        coverage_gaps=integer(),
        distinct_source_roots=integer(),
        distinct_target_roots=integer(),
        distinct_organization_roots=integer(),
        privacy_violations=integer(),
        authority_violations=integer(),
        canary_successes=integer(),
        canary_failures=integer(),
    )
    evaluation = record(
        "evaluation-receipt",
        candidate=ref("wave"),
        corpus=ref("particle"),
        holdout=ref("particle"),
        mutants=ref("particle"),
        canary=ref("particle"),
        verifier=artifact,
        metrics=metrics,
        generated_tests_are_independent_proof=fixed(False),
        passed={"type": "boolean"},
        grants_authority=fixed(False),
    )
    promotion = record(
        "promotion-decision",
        proposal=ref("wave"),
        decision={"enum": ["adopted", "rejected", "canary", "rollback"]},
        authority_rappid=rid,
        authority_evidence=ref("particle"),
        previous_selection=nullable(ref("wave")),
        new_selection=nullable(ref("wave")),
        automatic=fixed(False),
        grants_authority=fixed(False),
    )
    source_qualification = {
        "$schema": DRAFT,
        "$id": URI + "source-qualification.schema.json",
        **obj(
            schema=fixed(PROFILE + "/source-qualification"),
            repository=text(512, 1),
            commit=text(64, 40, r"^[0-9a-f]{40,64}$"),
            verified_frames=integer(512),
            verified_artifacts=integer(10000),
            qualification_status={"enum": ["synthetic", "externally-verified-summary"]},
            source_heads_bundled={"type": "boolean"},
            authority=fixed(False),
        ),
    }
    capability_manifest = {
        "$schema": DRAFT,
        "$id": URI + "capability-manifest.schema.json",
        **obj(
            schema=fixed(PROFILE + "/capability-manifest"),
            capability_id=fixed("autobest:generic"),
            version=fixed(1),
            tile_schema=fixed("rapp-work-capability-tile/1"),
            tile_subject=fixed("exact-agent.py-bytes"),
            agent=artifact,
            skill=artifact,
            profiles={
                "type": "array",
                "items": {"enum": ["generic", "microsol-ceo"]},
                "minItems": 2,
                "maxItems": 2,
                "uniqueItems": True,
            },
            invoker=fixed("external-global-brainstem"),
            activation=fixed("external-host-only"),
            mutation=fixed("successor-only"),
            rapp1_role=fixed("core-compatibility-substrate"),
            authority_from_presence=fixed(False),
            skill_activates=fixed(False),
            grants_authority=fixed(False),
        ),
    }
    seed_capability_binding = record(
        "seed-capability-binding",
        workspace_seed=ref("wave"),
        workspace_profile=fixed("rapp-workspace/1"),
        workspace_spec_sha256=ref("hash"),
        capability=ref("particle"),
        agent=ref("particle"),
        skill=ref("particle"),
        relation={
            "enum": [
                "ancestor-seed",
                "descendant-seed",
                "capability-successor",
            ]
        },
        ancestor_binding=nullable(ref("wave")),
        parent_binding=nullable(ref("wave")),
        previous_binding=nullable(ref("wave")),
        inheritance=fixed("reference-only"),
        executable=fixed(False),
        host_activation=fixed("external-host-only"),
        mutation=fixed("successor-only"),
        grants_authority=fixed(False),
    )
    handshake_package = {
        "$schema": DRAFT,
        "$id": URI + "handshake-package.schema.json",
        **obj(
            schema=fixed(PROFILE + "/handshake-package"),
            handshake_id=token,
            version=integer(1024, 1),
            status={"enum": ["candidate", "owner-approved-private", "retired"]},
            source_profile=token,
            target_profile=token,
            orchestrator_capability=ref("particle"),
            handshake=artifact,
            source_agent=artifact,
            target_agent=artifact,
            static_agent=nullable(artifact),
            generation_receipt=nullable(ref("particle")),
            compatibility_template=ref("particle"),
            rehearsal=ref("particle"),
            mutation_tests=ref("particle"),
            source_qualification=ref("particle"),
            private_hive_object_kind=fixed("rapp-work-compatibility/1-handshake-program"),
            authority=fixed(False),
        ),
    }
    documents = {
        "common.schema.json": common,
        "compatibility.schema.json": compatibility,
        "compatibility-exhaust.schema.json": exhaust,
        "transformation-receipt.schema.json": transformation,
        "static-agent-generation.schema.json": generation,
        "artifact-bundle.schema.json": artifact_bundle,
        "causal-mutation-manifest.schema.json": mutation_manifest,
        "learning-trace.schema.json": learning_trace,
        "mutation-offer.schema.json": mutation_offer,
        "lens-dimension.schema.json": lens_dimension,
        "candidate-cross.schema.json": candidate_cross,
        "evolution-proposal.schema.json": evolution,
        "evaluation-receipt.schema.json": evaluation,
        "promotion-decision.schema.json": promotion,
        "source-qualification.schema.json": source_qualification,
        "capability-manifest.schema.json": capability_manifest,
        "seed-capability-binding.schema.json": seed_capability_binding,
        "handshake-package.schema.json": handshake_package,
    }
    return {
        name: {
            "$schema": DRAFT,
            "$id": URI + name,
            **value,
        }
        if name != "common.schema.json" and "$schema" not in value
        else value
        for name, value in documents.items()
    }


def encoded(value):
    return (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--write", action="store_true")
    arguments = parser.parse_args()
    bad = []
    for name, value in schemas().items():
        path = ROOT / "schemas" / name
        raw = encoded(value)
        if arguments.write:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(raw)
        elif not path.is_file() or path.read_bytes() != raw:
            bad.append(name)
    existing = {path.name for path in (ROOT / "schemas").glob("*.json")}
    bad += sorted(existing - schemas().keys())
    print(f"{len(schemas())} RAPP Work Compatibility/1 schemas | " + ("FAIL " + ", ".join(bad) if bad else "PASS"))
    return int(bool(bad))


if __name__ == "__main__":
    raise SystemExit(main())
