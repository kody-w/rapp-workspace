"""Generate and verify exact RAPP Work SDK/1 parent, profile, and file pins."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[2]
PROFILE = "rapp-work-sdk/1"
CANONICAL_PARENT_REPOSITORY = "https://github.com/kody-w/rapp-1"
CANONICAL_PARENT_COMMIT = "591e014ad39e223b00ab343ae26e5d9a867ebeee"
CANONICAL_PARENT_PATH = "protocols/rapp-work/1/SPEC.md"
CANONICAL_PARENT_SPEC_SHA256 = (
    "283359355c3fe2858e28744368255683af3ed28a68e290e56c231e7d4b13c08e"
)
CANONICAL_PARENT_SPEC_BYTES = 11427
LEGACY_PIN = "4b4fc213c352de9157858041e57ab72bb5e17551"
PREVIOUS_PIN = "1c0e0b7c33a857e3f5e99c64355a8b8f970a83bc"
PREVIOUS_PROFILE_SHA256 = (
    "0add0b6c4adedcc569d137d6c6e243d47bc383cc29d955805dee13fbd048e21a"
)
PREVIOUS_PROFILE_BYTES = 1880
LEGACY_PROFILE_SHA256 = (
    "84b5afe5171b91202c96213de6767815ef1e22d743cdef97bd4ac9b4f5a66591"
)
LEGACY_PROFILE_BYTES = 1372
HISTORICAL_SPEC_SHA256 = (
    "861920ed31dd31412cc67064532ca855e3d9f842f1f63fa7f3daeab605fddf7e"
)
HISTORICAL_PROFILES = {
    LEGACY_PIN: (LEGACY_PROFILE_SHA256, LEGACY_PROFILE_BYTES),
    PREVIOUS_PIN: (PREVIOUS_PROFILE_SHA256, PREVIOUS_PROFILE_BYTES),
}
VENDORED_PARENT_SPEC = "vendor/rapp-work/1/SPEC.md"


def encoded(value: object) -> bytes:
    return (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


def record(base: Path, relative: str) -> dict:
    raw = (base / relative).read_bytes()
    return {
        "path": relative,
        "sha256": hashlib.sha256(raw).hexdigest(),
        "bytes": len(raw),
    }


def decoded(raw: bytes, label: str) -> dict:
    try:
        value = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ValueError(f"{label} is not valid UTF-8 JSON") from error
    if not isinstance(value, dict):
        raise ValueError(f"{label} is not a JSON object")
    return value


def historical_pin(pin: str, sequence: int) -> dict:
    relative = f"history/{pin}/profile.json"
    artifact = record(ROOT, relative)
    expected_sha256, expected_bytes = HISTORICAL_PROFILES[pin]
    value = decoded((ROOT / relative).read_bytes(), relative)
    parent = value.get("parent")
    pins = value.get("pins")
    if (
        artifact["sha256"] != expected_sha256
        or artifact["bytes"] != expected_bytes
        or value.get("schema") != PROFILE + "/profile"
        or value.get("profile") != PROFILE
        or value.get("current_pin") != pin
        or not isinstance(parent, dict)
        or parent.get("commit") != pin
        or parent.get("spec_sha256") != HISTORICAL_SPEC_SHA256
        or not isinstance(pins, list)
        or not any(
            isinstance(item, dict)
            and item.get("pin") == pin
            and item.get("spec_sha256") == parent["spec_sha256"]
            and item.get("fresh_install") is True
            for item in pins
        )
    ):
        raise ValueError(f"{relative} does not retain the exact source profile")
    return {
        "pin": pin,
        "sequence": sequence,
        "spec_sha256": parent["spec_sha256"],
        "status": "migration-source-only",
        "fresh_install": False,
        "profile_artifact": artifact,
    }


def parent_pin() -> dict:
    return {
        "schema": PROFILE + "/parent-pin",
        "profile": "rapp-work/1",
        "repository": CANONICAL_PARENT_REPOSITORY,
        "commit": CANONICAL_PARENT_COMMIT,
        "path": CANONICAL_PARENT_PATH,
        "spec_sha256": CANONICAL_PARENT_SPEC_SHA256,
        "spec_bytes": CANONICAL_PARENT_SPEC_BYTES,
        "vendored_path": VENDORED_PARENT_SPEC,
        "replacement_rule": "reviewed-forward-profile-update-only",
    }


def profile() -> dict:
    return {
        "schema": PROFILE + "/profile",
        "profile": PROFILE,
        "parent": {
            "profile": "rapp-work/1",
            "repository": CANONICAL_PARENT_REPOSITORY,
            "commit": CANONICAL_PARENT_COMMIT,
            "path": CANONICAL_PARENT_PATH,
            "spec_sha256": CANONICAL_PARENT_SPEC_SHA256,
        },
        "workspace_sibling": {
            "profile": "rapp-workspace/1",
            "spec_sha256": "80135ae05e532f11810d31a5cf974050a8332c18bd45f16879a7286f213edfab",
            "manifest_sha256": "f1165f947cb5d7554906012a174a854b28454403e41e8166925a364a68680370",
            "identity_unchanged": True,
            "normative_bytes_unchanged": True,
        },
        "sidecar": {
            "path": ".rapp-work",
            "mode": "offline-first",
            "network_default": "disabled",
            "atomic_generation_pointer": True,
            "native_workspace_copy": False,
        },
        "pins": [
            historical_pin(LEGACY_PIN, 0),
            historical_pin(PREVIOUS_PIN, 1),
            {
                "pin": CANONICAL_PARENT_COMMIT,
                "sequence": 2,
                "spec_sha256": CANONICAL_PARENT_SPEC_SHA256,
                "status": "current",
                "fresh_install": True,
                "profile_artifact": None,
            },
        ],
        "current_pin": CANONICAL_PARENT_COMMIT,
        "authority": {
            "discovery_only": True,
            "hive_publication": False,
            "plugin_activation": False,
            "native_workspace_mutation": False,
            "grants_authority": False,
        },
    }


def preserve_previous_profile() -> None:
    destination = ROOT / "history" / PREVIOUS_PIN / "profile.json"
    if destination.is_file() and not destination.is_symlink():
        raw = destination.read_bytes()
    else:
        if destination.exists() or destination.is_symlink():
            raise ValueError("previous profile artifact path is unsafe")
        raw = (ROOT / "profile.json").read_bytes()
        if (
            len(raw) != PREVIOUS_PROFILE_BYTES
            or hashlib.sha256(raw).hexdigest() != PREVIOUS_PROFILE_SHA256
        ):
            raise ValueError("current profile is not the accepted previous profile")
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(raw)
    if (
        len(raw) != PREVIOUS_PROFILE_BYTES
        or hashlib.sha256(raw).hexdigest() != PREVIOUS_PROFILE_SHA256
    ):
        raise ValueError("retained previous profile bytes changed")
    historical_pin(PREVIOUS_PIN, 1)


def install_parent_spec(source: Path | None) -> None:
    target = ROOT / VENDORED_PARENT_SPEC
    candidate = target if source is None else source.expanduser()
    if candidate.is_symlink() or not candidate.is_file():
        raise ValueError("canonical parent SPEC path is missing or unsafe")
    raw = candidate.read_bytes()
    if (
        len(raw) != CANONICAL_PARENT_SPEC_BYTES
        or hashlib.sha256(raw).hexdigest() != CANONICAL_PARENT_SPEC_SHA256
    ):
        raise ValueError("canonical parent SPEC bytes do not match the accepted pin")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(raw)


def manifest() -> dict:
    normative = [
        "SPEC.md",
        "parent-pin.json",
        "profile.json",
        *[
            "schemas/" + path.name
            for path in sorted((ROOT / "schemas").glob("*.json"))
        ],
    ]
    historical_profiles = [
        path.relative_to(ROOT).as_posix()
        for path in sorted((ROOT / "history").rglob("*"))
        if path.is_file()
    ]
    fixtures = [
        path.relative_to(ROOT).as_posix()
        for path in sorted((ROOT / "fixtures").rglob("*"))
        if path.is_file()
    ]
    reference = [
        "reference/" + path.name
        for path in sorted((ROOT / "reference").iterdir())
        if path.is_file() and path.suffix in {".py", ".md"}
    ]
    return {
        "schema": "rapp-work-sdk-file-manifest/1",
        "profile": PROFILE,
        "parent": "rapp-work/1",
        "parent_pin": record(ROOT, "parent-pin.json"),
        "workspace_sibling": {
            "profile": "rapp-workspace/1",
            "spec_sha256": "80135ae05e532f11810d31a5cf974050a8332c18bd45f16879a7286f213edfab",
            "manifest_sha256": "f1165f947cb5d7554906012a174a854b28454403e41e8166925a364a68680370",
            "identity_unchanged": True,
            "normative_bytes_unchanged": True,
        },
        "normative": [record(ROOT, name) for name in normative],
        "historical_profiles": [
            record(ROOT, name) for name in historical_profiles
        ],
        "dependencies": [record(ROOT, "vendor/rapp-work/1/SPEC.md")],
        "reference": [record(ROOT, name) for name in reference],
        "fixtures": [record(ROOT, name) for name in fixtures],
        "sidecar": ".rapp-work",
        "network_default": "disabled",
        "native_workspace_copy": False,
        "publication_authority": False,
    }


def index_profile() -> dict:
    base = "protocols/rapp-work-sdk/1/"
    spec = record(REPO, base + "SPEC.md")
    files = record(REPO, base + "manifest.json")
    parent = json.loads((ROOT / "parent-pin.json").read_text(encoding="utf-8"))
    profile = json.loads((ROOT / "profile.json").read_text(encoding="utf-8"))
    return {
        "name": PROFILE,
        "human_name": "RAPP Work SDK/1",
        "parent": "rapp-work/1",
        "authority": False,
        "status": "additive-reference",
        "spec_path": spec["path"],
        "spec_sha256": spec["sha256"],
        "spec_bytes": spec["bytes"],
        "manifest_path": files["path"],
        "manifest_sha256": files["sha256"],
        "manifest_bytes": files["bytes"],
        "schemas_path": base + "schemas",
        "conformance": base + "reference/conformance.py",
        "scaffold": base + "reference/scaffold.py",
        "sidecar": ".rapp-work",
        "network_default": "disabled",
        "native_workspace_copy": False,
        "publication_authority": False,
        "rapp_work_commit": parent["commit"],
        "rapp_work_repository": parent["repository"],
        "rapp_work_path": parent["path"],
        "rapp_work_spec_sha256": parent["spec_sha256"],
        "rapp_work_spec_bytes": parent["spec_bytes"],
        "current_pin": profile["current_pin"],
    }


def check_index() -> bool:
    index = json.loads((REPO / "protocols" / "index.json").read_text(encoding="utf-8"))
    matches = [entry for entry in index.get("profiles", []) if entry.get("name") == PROFILE]
    return matches == [index_profile()]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--write-index", action="store_true")
    parser.add_argument("--write-parent-profile", action="store_true")
    parser.add_argument("--canonical-spec", type=Path)
    args = parser.parse_args(argv)
    if args.canonical_spec is not None and not args.write_parent_profile:
        parser.error("--canonical-spec requires --write-parent-profile")
    if args.write_parent_profile:
        preserve_previous_profile()
        install_parent_spec(args.canonical_spec)
        (ROOT / "parent-pin.json").write_bytes(encoded(parent_pin()))
        (ROOT / "profile.json").write_bytes(encoded(profile()))
    raw = encoded(manifest())
    path = ROOT / "manifest.json"
    if args.write:
        path.write_bytes(raw)
    if args.write_index:
        index_path = REPO / "protocols" / "index.json"
        index = decoded(index_path.read_bytes(), "protocols/index.json")
        profiles = index.get("profiles")
        if not isinstance(profiles, list):
            raise ValueError("protocols/index.json profiles are invalid")
        index["profiles"] = [
            entry
            for entry in profiles
            if not isinstance(entry, dict) or entry.get("name") != PROFILE
        ] + [index_profile()]
        index_path.write_bytes(encoded(index))
    vendored = ROOT / VENDORED_PARENT_SPEC
    good = (
        (ROOT / "parent-pin.json").read_bytes() == encoded(parent_pin())
        and (ROOT / "profile.json").read_bytes() == encoded(profile())
        and vendored.is_file()
        and len(vendored.read_bytes()) == CANONICAL_PARENT_SPEC_BYTES
        and hashlib.sha256(vendored.read_bytes()).hexdigest()
        == CANONICAL_PARENT_SPEC_SHA256
        and path.is_file()
        and path.read_bytes() == raw
        and check_index()
    )
    print(
        "RAPP Work SDK/1 parent/profile/manifest/index pins: "
        + ("PASS" if good else "FAIL")
    )
    return int(not good)


if __name__ == "__main__":
    raise SystemExit(main())
