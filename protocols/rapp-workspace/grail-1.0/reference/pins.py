"""First-Grail immutable file inventory; neither discovery nor a manifest grants authority."""

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[2]
PROFILE = "rapp-workspace/grail-1.0"


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
        "brand": "RAPP Workspace/1 Grail", "parent": "rapp/1", "authority": False,
        "status": "minimal-safe-kernel-candidate", "signed_grail_activation": False,
        "assurances": ["rapp_integrity", "observation", "semantic_fidelity",
                       "current_authorization", "safe_deployment"],
        "normative": [record(ROOT, name) for name in normative],
        "reference": [record(ROOT, name) for name in reference],
        "repository_evidence": [record(REPO, name) for name in [
            "README.md", "SPEC.md", "SKILL.md", "tools/frame_lens.py", "tests/test_safe_kernel.py",
            "protocols/rapp-workspace/historical/pre-grail/README.md",
            "protocols/README.md", ".github/skills/rapp-workspace/SKILL.md",
            ".github/skills/autonomous-rapp-estate-manager/SKILL.md"]],
        "provenance": record(ROOT, "provenance.json"),
        "historical_catalog": record(REPO, "protocols/rapp-workspace/historical/pre-grail/index.json"),
        "withdrawn_experiment": "experimental/README.md; not normative, not imported by the safe kernel",
        "authority_boundary": "capability/adoption controller is external to all learned/received data",
    }


def index_profile():
    base = "protocols/rapp-workspace/grail-1.0/"
    spec, files, provenance = [record(REPO, base + name) for name in ("SPEC.md", "manifest.json", "provenance.json")]
    return {
        "name": PROFILE, "human_name": "RAPP Workspace/1 Grail", "parent": "rapp/1",
        "status": "minimal-safe-kernel-candidate", "generation": "first-grail", "signed_grail_activation": False,
        "spec_path": spec["path"], "spec_sha256": spec["sha256"], "spec_bytes": spec["bytes"],
        "manifest_path": files["path"], "manifest_sha256": files["sha256"], "manifest_bytes": files["bytes"],
        "provenance_path": provenance["path"], "provenance_sha256": provenance["sha256"],
        "provenance_bytes": provenance["bytes"], "schemas_path": base + "schemas",
        "conformance": base + "reference/conformance.py", "demo": base + "reference/safe_demo.py",
        "learned_semantic_capability": "disabled-unproven", "external_effects": "disabled",
    }


def check_index():
    index = json.loads((REPO / "protocols/index.json").read_bytes())
    return index.get("workspace_latest") == PROFILE and [
        p for p in index["profiles"] if p["name"].startswith("rapp-workspace/")] == [index_profile()]


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
        index.update(authority=False, workspace_latest=PROFILE, workspace_brand="RAPP Workspace/1 Grail")
        index.pop("workspace_family", None)
        index["profiles"] = [p for p in index["profiles"] if not p["name"].startswith("rapp-workspace/")] + [index_profile()]
        index["legacy_workspace_inputs"] = [
            {**item, "authority": False, "current_validator_accepted": False}
            for item in index.get("legacy_workspace_inputs", [])]
        index["generated_utc"] = "2026-09-15T03:12:29.169Z"
        index_path.write_bytes(encode(index))
    good = path.is_file() and path.read_bytes() == raw and check_index()
    print("First-Grail spec/schema/runtime/index pins: " + ("PASS" if good else "FAIL"))
    return int(not good)


if __name__ == "__main__":
    raise SystemExit(main())
