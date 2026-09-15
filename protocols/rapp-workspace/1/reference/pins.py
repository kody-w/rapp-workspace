"""Workspace/1 core immutable file inventory."""

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[2]
PROFILE = "rapp-workspace/1"


def encode(value):
    return (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode()


def record(base, name):
    from common import read_file
    raw = read_file(base / name, 16 * 1024 * 1024)
    return {"path": name, "sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw)}


def manifest():
    normative = ["SPEC.md", "safety-matrix.json"] + [
        "schemas/" + p.name for p in sorted((ROOT / "schemas").glob("*.json"))]
    reference = ["reference/" + p.name for p in sorted((ROOT / "reference").glob("*.py"))]
    return {
        "schema": "rapp-workspace-file-manifest/1", "profile": PROFILE,
        "brand": "RAPP Workspace/1", "parent": "rapp/1", "authority": True,
        "status": "core", "signed_activation": False,
        "assurances": ["rapp_integrity", "observation", "semantic_fidelity",
                       "current_authorization", "safe_deployment"],
        "normative": [record(ROOT, name) for name in normative],
        "reference": [record(ROOT, name) for name in reference],
        "repository_evidence": [record(REPO, name) for name in [
            "README.md", "SPEC.md", "SKILL.md", "tools/frame_lens.py", "tests/test_safe_kernel.py",
            "protocols/rapp-workspace/prototypes/README.md",
            "protocols/README.md", ".github/skills/rapp-workspace/SKILL.md",
            ".github/skills/autonomous-rapp-estate-manager/SKILL.md"]],
        "provenance": record(ROOT, "provenance.json"),
        "prototype_catalog": record(REPO, "protocols/rapp-workspace/prototypes/index.json"),
        "authority_boundary": "capability/adoption controller is external to all learned/received data",
    }


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


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--write-index", action="store_true")
    args = parser.parse_args()
    raw = encode(manifest())
    path = ROOT / "manifest.json"
    if args.write:
        path.write_bytes(raw)
    if args.write_index:
        index_path = REPO / "protocols/index.json"
        index = json.loads(index_path.read_bytes())
        index.update(
            authority=True,
            workspace_latest=PROFILE,
            workspace_brand="RAPP Workspace/1",
            workspace_prototypes=record(REPO, "protocols/rapp-workspace/prototypes/index.json"),
        )
        index.pop("workspace_family", None)
        index.pop("legacy_workspace_inputs", None)
        index.pop("prototype_inputs", None)
        index["profiles"] = [p for p in index["profiles"] if not p["name"].startswith("rapp-workspace/")] + [index_profile()]
        index["generated_utc"] = "2026-09-15T16:19:18.852Z"
        index_path.write_bytes(encode(index))
    good = path.is_file() and path.read_bytes() == raw and check_index()
    print("Workspace/1 core spec/schema/runtime/index pins: " + ("PASS" if good else "FAIL"))
    return int(not good)


if __name__ == "__main__":
    raise SystemExit(main())
