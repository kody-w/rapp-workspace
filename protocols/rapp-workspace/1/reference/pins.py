"""Workspace/1 core immutable file inventory: normative bytes only, never front doors."""

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[2]
PROFILE = "rapp-workspace/1"
SCHEMA = "rapp-workspace-file-manifest/2"
# READMEs, badges and start-here links are editable front doors, never runtime evidence.
REPOSITORY_EVIDENCE = (
    "SPEC.md", "SKILL.md", "tools/frame_lens.py",
    "tests/test_safe_kernel.py", "tests/test_p0_hardening.py",
    ".github/skills/rapp-workspace/SKILL.md",
    ".github/skills/autonomous-rapp-estate-manager/SKILL.md",
)
# Retained exact predecessor manifests: verified here, never regenerated.
PREDECESSORS = (
    {
        "schema": "rapp-workspace-file-manifest/1",
        "path": "history/f1165f947cb5d7554906012a174a854b28454403e41e8166925a364a68680370/manifest.json",
        "sha256": "f1165f947cb5d7554906012a174a854b28454403e41e8166925a364a68680370",
        "bytes": 7990,
    },
)


def encode(value):
    return (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode()


def front_door(path):
    name = path.rsplit("/", 1)[-1].casefold()
    return name == "readme" or name.startswith("readme.")


def record(base, name):
    from common import read_file
    raw = read_file(base / name, 16 * 1024 * 1024)
    return {"path": name, "sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw)}


def predecessor(entry):
    from common import read_file, require
    require(set(entry) == {"schema", "path", "sha256", "bytes"}
            and entry["path"] == "history/" + entry["sha256"] + "/manifest.json",
            "retained-predecessor-record-invalid")
    raw = read_file(ROOT / entry["path"], 16 * 1024 * 1024)
    require(len(raw) == entry["bytes"] and hashlib.sha256(raw).hexdigest() == entry["sha256"],
            "retained-predecessor-manifest-changed: " + entry["path"])
    value = json.loads(raw)
    require(type(value) is dict and value.get("schema") == entry["schema"]
            and value.get("profile") == PROFILE and value.get("status") == "core",
            "retained-predecessor-manifest-mismatch: " + entry["path"])
    return dict(entry)


def listed_paths(value):
    if isinstance(value, dict):
        for key, child in value.items():
            if key == "path" and isinstance(child, str):
                yield child
            else:
                yield from listed_paths(child)
    elif isinstance(value, list):
        for child in value:
            yield from listed_paths(child)


def manifest():
    from common import require
    normative = ["SPEC.md", "safety-matrix.json"] + [
        "schemas/" + p.name for p in sorted((ROOT / "schemas").glob("*.json"))]
    reference = ["reference/" + p.name for p in sorted((ROOT / "reference").glob("*.py"))]
    value = {
        "schema": SCHEMA, "profile": PROFILE,
        "brand": "RAPP Workspace/1", "parent": "rapp/1", "authority": True,
        "status": "core", "signed_activation": False,
        "assurances": ["rapp_integrity", "observation", "semantic_fidelity",
                       "current_authorization", "safe_deployment"],
        "normative": [record(ROOT, name) for name in normative],
        "reference": [record(ROOT, name) for name in reference],
        "repository_evidence": [record(REPO, name) for name in REPOSITORY_EVIDENCE],
        "provenance": record(ROOT, "provenance.json"),
        "prototype_catalog": record(REPO, "protocols/rapp-workspace/prototypes/index.json"),
        "authority_boundary": "capability/adoption controller is external to all learned/received data",
        "live_activation": "exact-document-external-verifier-required",
        "production_key_custody": "external-unqualified",
        "synthetic_activation": "explicit-labeled-fixtures-only",
        "predecessors": [predecessor(entry) for entry in PREDECESSORS],
    }
    for path in listed_paths(value):
        require(not front_door(path), "front-door-not-pinnable: " + path)
    return value


def index_profile():
    base = "protocols/rapp-workspace/1/"
    spec, files, provenance = [record(REPO, base + name) for name in ("SPEC.md", "manifest.json", "provenance.json")]
    return {
        "name": PROFILE, "human_name": "RAPP Workspace/1", "parent": "rapp/1",
        "authority": True, "status": "core", "generation": "core", "signed_activation": False,
        "spec_path": spec["path"], "spec_sha256": spec["sha256"], "spec_bytes": spec["bytes"],
        "manifest_path": files["path"], "manifest_sha256": files["sha256"], "manifest_bytes": files["bytes"],
        "provenance_path": provenance["path"], "provenance_sha256": provenance["sha256"],
        "provenance_bytes": provenance["bytes"], "schemas_path": base + "schemas",
        "conformance": base + "reference/conformance.py", "demo": base + "reference/safe_demo.py",
        "learned_semantic_capability": "disabled-unproven", "external_effects": "disabled",
        "live_activation": "exact-document-external-verifier-required",
        "production_key_custody": "external-unqualified",
    }


def check_index():
    index = json.loads((REPO / "protocols/index.json").read_bytes())
    return (
        index.get("authority") is True
        and index.get("workspace_latest") == PROFILE
        and index.get("workspace_brand") == "RAPP Workspace/1"
        and index.get("workspace_prototypes")
        == record(REPO, "protocols/rapp-workspace/prototypes/index.json")
        and [p for p in index["profiles"] if p["name"].startswith("rapp-workspace/")]
        == [index_profile()]
    )


def write_index():
    """Replace only the Workspace entry in place; other entries, order and generated_utc are kept."""
    index_path = REPO / "protocols/index.json"
    index = json.loads(index_path.read_bytes())
    index.update(
        authority=True,
        workspace_latest=PROFILE,
        workspace_brand="RAPP Workspace/1",
        workspace_prototypes=record(REPO, "protocols/rapp-workspace/prototypes/index.json"),
    )
    for key in ("workspace_family", "legacy_workspace_inputs", "prototype_inputs"):
        index.pop(key, None)
    entry, profiles = index_profile(), []
    for item in index["profiles"]:
        if not item["name"].startswith("rapp-workspace/"):
            profiles.append(item)
        elif entry is not None:
            profiles.append(entry)
            entry = None
    index["profiles"] = profiles + ([entry] if entry is not None else [])
    index_path.write_bytes(encode(index))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--write-index", action="store_true")
    args = parser.parse_args()
    from common import Refusal
    try:
        raw = encode(manifest())
    except (OSError, Refusal) as error:
        print("Workspace/1 core spec/schema/runtime/index pins: FAIL (" + str(error) + ")")
        return 1
    path = ROOT / "manifest.json"
    if args.write:
        path.write_bytes(raw)
    if args.write_index:
        write_index()
    good = path.is_file() and path.read_bytes() == raw and check_index()
    print("Workspace/1 core spec/schema/runtime/index pins: " + ("PASS" if good else "FAIL"))
    return int(not good)


if __name__ == "__main__":
    raise SystemExit(main())
