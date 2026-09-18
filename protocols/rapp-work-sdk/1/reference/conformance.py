#!/usr/bin/env python3
"""Run offline RAPP Work SDK/1 reference conformance."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
import shutil

from pins import ROOT, REPO, encoded, manifest
import scaffold
import schema_source


WORKSPACE_MANIFEST_SHA256 = "f1165f947cb5d7554906012a174a854b28454403e41e8166925a364a68680370"
WORKSPACE_SPEC_SHA256 = "80135ae05e532f11810d31a5cf974050a8332c18bd45f16879a7286f213edfab"
LEGACY_PIN = "4b4fc213c352de9157858041e57ab72bb5e17551"
PREVIOUS_PIN = "1c0e0b7c33a857e3f5e99c64355a8b8f970a83bc"
RAPPID = "rappid:@fixture/workspace:" + "1" * 64
HIVE_RAPPID = "rappid:@fixture/hive:" + "2" * 64
NOW = "2026-09-18T15:00:00.000Z"
PRIOR_RELEASE = ROOT / "fixtures" / "prior-release"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise scaffold.Refusal(message)


def write_workspace(path: Path, suffix: str) -> dict[str, bytes]:
    path.mkdir(parents=True)
    files = {
        "rappid.json": encoded(
            {
                "schema": "rapp/1",
                "rappid": RAPPID[:-64] + suffix * 64,
                "world_id": "fixture-world",
                "workspace_spec": "legacy-local/1",
            }
        ),
        "native.txt": ("native-" + suffix).encode("utf-8"),
    }
    for name, raw in files.items():
        (path / name).write_bytes(raw)
    return files


def assert_native(path: Path, expected: dict[str, bytes]) -> None:
    for name, raw in expected.items():
        require((path / name).read_bytes() == raw, f"native workspace byte changed: {name}")


def discovery(identity: dict, pin: str) -> dict:
    value = scaffold.default_discovery(identity, pin)
    value["organization_pointers"] = [
        {
            "workspace_profile": "rapp-workspace/1",
            "composite": {"space": "rapp/1:wave", "hash": "3" * 64},
            "verification_status": "address-reference-only",
            "verification_receipt": None,
            "routing_only": True,
            "content_copied": False,
            "grants_authority": False,
        }
    ]
    value["hive_endpoints"] = [
        {
            "id": "local-hive",
            "hive_rappid": HIVE_RAPPID,
            "world_id": "fixture-world",
            "transport": "local-filesystem",
            "locator_sha256": "4" * 64,
            "verification_status": "verified",
            "verification_receipt": {"space": "rapp/1:wave", "hash": "5" * 64},
            "publication_authorized": False,
            "grants_authority": False,
        }
    ]
    value["hive_vectors"] = [
        {
            "hive_rappid": HIVE_RAPPID,
            "vector_sha256": "6" * 64,
            "verification_status": "verified",
            "verification_receipt": {"space": "rapp/1:wave", "hash": "7" * 64},
            "publication_authorized": False,
            "grants_authority": False,
        }
    ]
    entry = {
        "id": "fixture-entry",
        "version": "1",
        "locator": "discovery:fixture",
        "sha256": None,
        "discovery_only": True,
        "activation_authorized": False,
        "execution_authorized": False,
        "grants_authority": False,
    }
    value["plugins"] = [entry]
    value["skills"] = [{**entry, "id": "fixture-skill"}]
    value["static_apis"] = [{**entry, "id": "fixture-static-api"}]
    scaffold.validate_discovery(value, identity=identity, pin=pin)
    return value


def run(output: Path) -> dict:
    require(not output.is_absolute() and ".." not in output.parts, "conformance output must be relative")
    destination = REPO / output
    if destination.exists() or destination.is_symlink():
        require(not destination.is_symlink() and destination.is_dir(), "conformance output is unsafe")
        shutil.rmtree(destination)
    destination.mkdir(parents=True)
    workspace_manifest = REPO / "protocols" / "rapp-workspace" / "1" / "manifest.json"
    workspace_spec = REPO / "protocols" / "rapp-workspace" / "1" / "SPEC.md"
    require(hashlib.sha256(workspace_manifest.read_bytes()).hexdigest() == WORKSPACE_MANIFEST_SHA256,
            "Workspace/1 manifest bytes changed")
    require(hashlib.sha256(workspace_spec.read_bytes()).hexdigest() == WORKSPACE_SPEC_SHA256,
            "Workspace/1 SPEC bytes changed")
    require((ROOT / "manifest.json").read_bytes() == encoded(manifest()), "SDK manifest drift")
    require(not schema_source.main(["--check"]), "SDK schema drift")

    checks = 0
    current = destination / "current"
    expected = write_workspace(current, "1")
    identity = scaffold.workspace_identity(current)
    requested = discovery(identity, scaffold.CURRENT_PIN)
    first = scaffold.install_workspace(current, discovery=requested, now=NOW)
    checks += 1
    second = scaffold.install_workspace(current, discovery=requested, now=NOW)
    require(first["status"] == "installed" and second["status"] == "already-installed",
            "same-pin installation is not idempotent")
    checks += 1
    verified = scaffold.verify_workspace(current)
    require(
        verified["current_pin"] == scaffold.CURRENT_PIN
        and verified["network_default"] == "disabled"
        and verified["publication_authorized"] is False,
        "installed sidecar violates offline/no-authority invariants",
    )
    assert_native(current, expected)
    require(b"native-1" not in b"".join(
        path.read_bytes() for path in (current / ".rapp-work").rglob("*") if path.is_file()
    ), "native content was copied into the sidecar")
    checks += 1

    historical = destination / "historical"
    shutil.copytree(PRIOR_RELEASE, historical)
    historical.chmod(0o700)
    historical_sidecar = historical / ".rapp-work"
    for directory in [
        historical_sidecar,
        *[path for path in historical_sidecar.rglob("*") if path.is_dir()],
    ]:
        directory.chmod(0o700)
    for path in historical_sidecar.rglob("*"):
        if path.is_file():
            path.chmod(0o600)
    historical_expected = {
        path.relative_to(historical).as_posix(): path.read_bytes()
        for path in historical.rglob("*")
        if path.is_file() and ".rapp-work" not in path.parts
    }
    old_profile_path = (
        historical / ".rapp-work" / "generations" / LEGACY_PIN / "profile.json"
    )
    old_discovery_path = (
        historical / ".rapp-work" / "generations" / LEGACY_PIN / "discovery.json"
    )
    old_profile = old_profile_path.read_bytes()
    old_discovery = old_discovery_path.read_bytes()
    old_state = scaffold.verify_workspace(historical)
    require(
        old_state["current_pin"] == LEGACY_PIN
        and hashlib.sha256(old_profile).hexdigest()
        == scaffold._pin_profile_sha256(LEGACY_PIN)
        and old_profile != scaffold.PROFILE_RAW,
        "retained prior-release sidecar is not an actual older profile",
    )
    checks += 1
    previous_profile = scaffold.strict_json(
        scaffold._pin_profile_raw(PREVIOUS_PIN),
        "retained previous profile",
    )
    require(
        scaffold.PINS[PREVIOUS_PIN]["status"] == "migration-source-only"
        and scaffold.PINS[PREVIOUS_PIN]["fresh_install"] is False
        and previous_profile["current_pin"] == PREVIOUS_PIN
        and previous_profile["parent"]["repository"]
        == "https://github.com/kody-w/rapp-work",
        "immediate previous parent pin is not retained as a migration source",
    )
    checks += 1
    plan = scaffold.plan_update(
        historical,
        from_pin=LEGACY_PIN,
        to_pin=scaffold.CURRENT_PIN,
    )
    require(
        plan["plan"]["from_profile_sha256"]
        == scaffold._pin_profile_sha256(LEGACY_PIN)
        and
        plan["plan"]["target_profile_sha256"] == scaffold.PROFILE_SHA256,
        "forward plan does not bind source and target profile bytes",
    )
    try:
        scaffold.update_workspace(
            historical,
            from_pin=LEGACY_PIN,
            to_pin=scaffold.CURRENT_PIN,
            plan_digest="0" * 64,
            now=NOW,
        )
    except scaffold.Refusal:
        pass
    else:
        raise scaffold.Refusal("wrong update plan digest was accepted")
    checks += 1
    updated = scaffold.update_workspace(
        historical,
        from_pin=LEGACY_PIN,
        to_pin=scaffold.CURRENT_PIN,
        plan_digest=plan["plan_digest"],
        now=NOW,
    )
    require(updated["status"] == "updated", "forward update did not activate")
    assert_native(historical, historical_expected)
    active_install = scaffold.strict_json(
        (historical / ".rapp-work" / "install.json").read_bytes(),
        "updated fixture install",
    )
    require(
        active_install["profile_sha256"] == scaffold.PROFILE_SHA256
        and old_profile_path.read_bytes() == old_profile
        and old_discovery_path.read_bytes() == old_discovery
        and (
            historical
            / ".rapp-work"
            / "generations"
            / scaffold.CURRENT_PIN
            / "profile.json"
        ).read_bytes()
        == scaffold.PROFILE_RAW,
        "forward update did not preserve source artifacts and activate target profile bytes",
    )
    checks += 1
    try:
        scaffold.plan_update(
            historical,
            from_pin=scaffold.CURRENT_PIN,
            to_pin=LEGACY_PIN,
        )
    except scaffold.Refusal:
        pass
    else:
        raise scaffold.Refusal("downgrade plan was accepted")
    checks += 1

    conflict = destination / "conflict"
    write_workspace(conflict, "9")
    (conflict / ".rapp-work").mkdir()
    (conflict / ".rapp-work" / "partial").write_text("partial", encoding="utf-8")
    try:
        scaffold.install_workspace(conflict)
    except scaffold.Refusal:
        pass
    else:
        raise scaffold.Refusal("partial sidecar was repaired or overwritten")
    checks += 1

    unsafe = destination / "unsafe"
    write_workspace(unsafe, "7")
    outside = destination / "outside"
    outside.mkdir()
    (unsafe / ".rapp-work").symlink_to(outside, target_is_directory=True)
    try:
        scaffold.install_workspace(unsafe)
    except scaffold.Refusal:
        pass
    else:
        raise scaffold.Refusal("symlinked sidecar was accepted")
    checks += 1

    report = {
        "schema": "rapp-work-sdk-conformance/1",
        "profile": "rapp-work-sdk/1",
        "checks": checks,
        "current_pin": scaffold.CURRENT_PIN,
        "canonical_rapp_work_pin": True,
        "rapp_work_commit": scaffold.PARENT_PIN["commit"],
        "rapp_work_spec_sha256": scaffold.PARENT_PIN["spec_sha256"],
        "rapp_work_spec_bytes": scaffold.PARENT_PIN["spec_bytes"],
        "previous_pin_migration_source_only": True,
        "workspace_profile": "rapp-workspace/1",
        "workspace_manifest_sha256": WORKSPACE_MANIFEST_SHA256,
        "workspace_spec_sha256": WORKSPACE_SPEC_SHA256,
        "workspace_bytes_unchanged": True,
        "same_pin_idempotent": True,
        "true_prior_release_fixture": True,
        "per_pin_profile_and_discovery_history": True,
        "exact_update_plan_digest": True,
        "atomic_no_replace_and_pointer_cas": True,
        "offline_default": True,
        "native_workspace_copy": False,
        "publication_authority": False,
        "status": "PASS",
    }
    (destination / "conformance-results.json").write_bytes(encoded(report))
    print(json.dumps(report, sort_keys=True))
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(".validation/rapp-work-sdk-conformance"),
    )
    args = parser.parse_args(argv)
    run(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
