"""Deterministic arbitrary-program bundle compiler for locked compatibility."""

from __future__ import annotations

import base64
from pathlib import Path
from typing import Any

from workorg_common import (
    canonical_bytes,
    egg,
    hash_value,
    particle_ref,
    require,
    safe_path,
    sha256,
    wave,
)


COMPILER_ID = "rapp-work-organization/1/reference-static-bundle-compiler"
TEMPLATE = b'''"""Generated locked Work Organization agent. Do not edit."""
from __future__ import annotations
import base64
import json

LOCKED_PROFILE_B64 = __LOCKED_PROFILE__
LOCKED_PROGRAM_B64 = __LOCKED_PROGRAM__
LOCKED_PROFILE = json.loads(base64.urlsafe_b64decode(LOCKED_PROFILE_B64))
exec(compile(base64.urlsafe_b64decode(LOCKED_PROGRAM_B64), "<locked-program>", "exec"))
'''


def _encoded_literal(data: bytes) -> bytes:
    return repr(base64.urlsafe_b64encode(data)).encode("ascii")


def _file_entry(
    path: str,
    data: bytes,
    *,
    role: str,
    lineage: list[dict[str, str]],
    generation_receipt: dict[str, str] | None,
) -> dict[str, Any]:
    safe_path(path)
    return {
        "path": path,
        "role": role,
        "sha256": sha256(data),
        "bytes": len(data),
        "mode": "100644",
        "media_type": "text/x-python" if path.endswith(".py") else "application/octet-stream",
        "lineage": lineage,
        "generation_receipt": generation_receipt,
    }


def compile_static_bundle(
    *,
    compatibility_frame: dict[str, str],
    compatibility_frame_octets_sha256: str,
    locked_profile: dict[str, Any],
    program_source: bytes,
    extra_files: dict[str, bytes],
    bundle_rappid: str,
    runtime_manifest_sha256: str,
    source_mutation_manifest: dict[str, str],
    compiler_sha256: str,
) -> dict[str, Any]:
    """Compile arbitrary approved program bytes into one deterministic bundle."""

    wave(compatibility_frame)
    hash_value(compatibility_frame_octets_sha256)
    hash_value(runtime_manifest_sha256)
    hash_value(compiler_sha256)
    particle_ref(source_mutation_manifest)
    require(program_source, "REFUSE_COMPILER", "Approved program bytes are required.")
    require(
        "agent.py" not in extra_files,
        "REFUSE_COMPILER",
        "The compiler owns the hotload entrypoint path.",
    )
    profile = {
        "schema": "rapp-work-organization/1/static-agent-profile",
        "compatibility_frame": compatibility_frame,
        "compatibility_frame_octets_sha256": compatibility_frame_octets_sha256,
        "locked_contract": locked_profile,
        "compiler": COMPILER_ID,
        "compiler_sha256": compiler_sha256,
        "runtime_manifest_sha256": runtime_manifest_sha256,
        "model_calls": 0,
        "grants_authority": False,
    }
    agent = TEMPLATE.replace(
        b"__LOCKED_PROFILE__", _encoded_literal(canonical_bytes(profile))
    ).replace(b"__LOCKED_PROGRAM__", _encoded_literal(program_source))
    files = {"agent.py": agent, **extra_files}
    for path in files:
        safe_path(path)
    generation_version = (
        "compat-"
        + compatibility_frame["hash"][:16]
        + "-compiler-"
        + compiler_sha256[:16]
    )
    generation_receipt = {
        "compatibility_frame": compatibility_frame,
        "compatibility_frame_octets_sha256": compatibility_frame_octets_sha256,
        "compiler_sha256": compiler_sha256,
        "compiler_runtime_manifest_sha256": runtime_manifest_sha256,
        "template_sha256": sha256(TEMPLATE),
        "output_agent_sha256": sha256(agent),
        "output_agent_bytes": len(agent),
        "generation_version": generation_version,
        "model_calls": 0,
        "deterministic": True,
        "grants_authority": False,
    }
    entries = []
    for path, data in sorted(files.items()):
        entries.append(
            _file_entry(
                path,
                data,
                role="hotload-entrypoint" if path == "agent.py" else "code",
                lineage=[compatibility_frame],
                generation_receipt=compatibility_frame if path == "agent.py" else None,
            )
        )
    aggregate = sha256(canonical_bytes(entries))
    manifest = {
        "schema": "rapp-work-organization/1/artifact-bundle",
        "bundle_rappid": bundle_rappid,
        "compatibility_frame": compatibility_frame,
        "entrypoint": "agent.py",
        "files": entries,
        "runtime_manifest_sha256": runtime_manifest_sha256,
        "aggregate_sha256": aggregate,
        "source_mutation_manifest": source_mutation_manifest,
        "generation_receipt": generation_receipt,
        "candidate_tests_are_independent_proof": False,
        "grants_authority": False,
    }
    return {
        "files": files,
        "manifest": manifest,
        "generation_receipt": generation_receipt,
        "artifact_address": {"space": "rapp/1:egg-manifest", "hash": sha256(canonical_bytes(manifest))},
    }


def compiler_pin() -> str:
    return sha256(Path(__file__).read_bytes())
