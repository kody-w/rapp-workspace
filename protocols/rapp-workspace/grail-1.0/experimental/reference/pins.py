"""Check exact profile bytes. A file manifest is not a signed RAPP/1 registry."""

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[3]
HISTORY = REPO / "protocols/rapp-workspace/historical/pre-grail"


def file_record(root, name):
    from common import read_file
    raw = read_file(root / name, 16 * 1024 * 1024)
    return {"path": name, "sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw)}


def encode(value):
    return (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


def historical_catalog():
    from common import read_file, require
    value = json.loads(read_file(HISTORY / "index.json"))
    require(value.get("authority") is False, "historical catalog is not authority")
    for entry in value["files"]:
        require(entry["path"].startswith("protocols/rapp-workspace/historical/pre-grail/")
                and ".." not in Path(entry["path"]).parts, "historical path escape")
        measured = file_record(REPO, entry["path"])
        require((measured["sha256"], measured["bytes"]) == (entry["sha256"], entry["bytes"]),
                "historical byte substitution")
    return value


def legacy_contract(label, digest):
    from common import require
    catalog = historical_catalog()
    if label == "rapp-workspace/1.0":
        require(digest is None, "pre-Grail 1.0 specification unavailable; MUST NOT fabricate a pin")
        return
    require(any(entry["label"] == label and entry["source_path"] == "SPEC.md"
                and entry["sha256"] == digest for entry in catalog["files"]),
            "unrecognized pre-Grail source specification pin")


def legacy_inputs():
    catalog = historical_catalog()
    return [{"source_generation": "pre-grail", "source_spec": entry["label"],
             "spec_path": entry["path"], "spec_sha256": entry["sha256"],
             "spec_bytes": entry["bytes"], "authority": False}
            for entry in catalog["files"] if entry["source_path"] == "SPEC.md"] + [{
                "source_generation": "pre-grail", "source_spec": "rapp-workspace/1.0",
                "spec_path": None, "spec_sha256": None, "spec_bytes": None, "authority": False,
                "status": "unavailable-spec-explicit-owner-approved-baseline-only",
            }]


def provenance(rapp1, chains):
    commit = lambda path: subprocess.check_output(
        ["git", "-C", str(path), "rev-parse", "HEAD"], text=True).strip()
    frames = [json.loads(line) for line in (rapp1 / "anchor/chain.jsonl").read_bytes().splitlines()]
    return {
        "schema": "rapp-workspace-source-provenance/1",
        "authority": False,
        "inspected_utc": datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z"),
        "workspace_versioning": {
            "selection": "owner-directed-first-grail-numbering",
            "requested_utc": "2026-09-15T00:35:23.808Z",
            "protocol_family": "rapp-workspace/1", "spec_id": "rapp-workspace/1.0",
            "generation": "grail", "status": "first-grail-authority-candidate",
            "pre_grail_materials": "experimental-migration-inputs-not-normative-predecessors",
            "signed_grail_activation": False,
        },
        "rapp1": {
            "role": "canonical-parent-authority-inspection-not-estate-activation",
            "repository": "https://github.com/kody-w/rapp-1",
            "observed_ref": "refs/heads/main", "commit": commit(rapp1),
            "anchor_stream": frames[-1]["stream_id"],
            "selected_head": {"space": "rapp/1:wave", "hash": frames[-1]["frame_hash"]},
            "authority_selection": "owner-accepted-canonical-main-per-RAPP1-12.2",
            "authenticated_estate_registry": None,
            "files": [file_record(rapp1, p) for p in [
                "SPEC.md", "rapp.py", "rapp_check.py", "anchor/chain.jsonl",
                "anchor/bootstrap/index.json", "anchor/bootstrap_verify.py"]],
        },
        "frame_chains": {
            "role": "non-authority-orchestration-provenance",
            "repository": "https://github.com/kody-w/frame-chains",
            "observed_ref": "refs/heads/main", "commit": commit(chains),
            "files": [file_record(chains, p) for p in [
                "README.md", "paper.html", "evidence/README.md", "evidence/verify.mjs",
                "evidence/v1/data/scan-heal.json", "evidence/v1/data/reattach.json",
                "evidence/v1/data/membrane.json", "evidence/v1/data/merge-fidelity.json"]],
            "mechanisms": {
                "scan_tiles": "paper section 3.1",
                "exhaust_delta_and_baseline": "paper section 3.2",
                "stable_ticks": "paper section 3.3",
                "recursive_dimensions": "paper section 3.4",
                "resume_and_one_way_membrane": "paper section 3.6",
                "deterministic_reattach": "paper section 3.7",
                "chain_as_clock": "paper section 3.8",
                "merge_fidelity": "paper section 3.9",
                "limitations": "paper section 6",
            },
            "copied_production_substrate": False,
            "teaching_sample": "samples/frame_chain.py is not imported, vendored, or used for RAPP conformance",
        },
    }


def manifest():
    normative = ["SPEC.md"] + ["schemas/" + p.name for p in sorted((ROOT / "schemas").glob("*.json"))]
    reference = ["reference/" + p.name for p in sorted((ROOT / "reference").glob("*.py"))]
    return {
        "schema": "rapp-workspace-file-manifest/1", "profile": "rapp-workspace/1.0",
        "protocol_family": "rapp-workspace/1", "generation": "grail",
        "brand": "RAPP Workspace Grail/1", "parent": "rapp/1", "authority": False,
        "policy_status": "first-grail-authority-candidate", "signed_grail_activation": False,
        "headline_acceptance": {"concept": "Frame Anything", "scenario": "frame-anything-iterative",
                                "entry": "reference/frame_anything.py", "learner": "reference/framing.py",
                                "scheduler": "reference/iteration.py", "bounded_iteration": True,
                                "workspace_adoption": "conditional-not-implied-by-framing"},
        "normative": [file_record(ROOT, p) for p in normative],
        "reference": [file_record(ROOT, p) for p in reference],
        "repository_evidence": [file_record(REPO, p) for p in [
            "tests/experimental/test_frame_lens.py", "tests/experimental/test_unknown_native.py",
            "tests/experimental/test_frame_anything.py", "tests/experimental/test_iteration.py",
            "tools/frame_lens.py", "SKILL.md", "SPEC.md",
            "README.md", "protocols/README.md", "protocols/rapp-workspace/grail-1.0/experimental/reference/README.md",
            ".github/skills/rapp-workspace/SKILL.md",
            ".github/skills/autonomous-rapp-estate-manager/SKILL.md"]],
        "provenance": file_record(ROOT, "provenance.json"),
        "historical": {
            "status": "pre-grail-experimental-migration-inputs-not-normative-predecessors",
            "index": file_record(REPO, "protocols/rapp-workspace/historical/pre-grail/index.json"),
            "guide": file_record(REPO, "protocols/rapp-workspace/historical/pre-grail/README.md"),
            "files": [file_record(REPO, e["path"]) for e in historical_catalog()["files"]],
        },
        "authority_boundary": {
            "rapp1": "canonical identities, addresses, eleven-key envelope, signatures, eggs and estate registry",
            "frame_chains": "orchestration inspiration only; no protocol or estate authority",
            "workspace_grail": "first Grail workspace authority candidate; subordinate to RAPP/1; no kernel activation",
            "this_manifest": "raw file integrity inventory; cannot adopt itself or grant rights",
        },
    }


def index_profiles():
    base = "protocols/rapp-workspace/grail-1.0/experimental/"
    spec = file_record(REPO, base + "SPEC.md")
    profile = {
        "name": "rapp-workspace/1.0", "protocol_family": "rapp-workspace/1",
        "human_name": "RAPP Workspace Grail/1", "generation": "grail", "parent": "rapp/1",
        "status": "first-grail-authority-candidate", "signed_grail_activation": False,
        "spec_path": spec["path"], "spec_sha256": spec["sha256"], "spec_bytes": spec["bytes"],
    }
    for key, name in (("manifest", "manifest.json"), ("provenance", "provenance.json")):
        item = file_record(REPO, base + name)
        profile.update({key + "_path": item["path"], key + "_sha256": item["sha256"],
                        key + "_bytes": item["bytes"]})
    profile.update(schemas_path=base + "schemas", conformance=base + "reference/conformance.py")
    profile.update(demo=base + "reference/frame_anything.py", headline_scenario="frame-anything-iterative",
                   concept="Frame Anything", workspace_adoption="conditional", bounded_iteration=True,
                   scheduler=base + "reference/iteration.py")
    return [profile]


def index_matches():
    index = json.loads((ROOT / "experimental-index.json").read_bytes())
    return (index.get("authority") is False and index.get("workspace_latest") == "rapp-workspace/1.0"
            and [p for p in index["profiles"] if p["name"].startswith("rapp-workspace/")] == index_profiles()
            and index.get("legacy_workspace_inputs") == legacy_inputs())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--capture-provenance", action="store_true")
    parser.add_argument("--write-index", action="store_true")
    parser.add_argument("--rapp1-path", type=Path)
    parser.add_argument("--frame-chains-path", type=Path)
    args = parser.parse_args()
    if args.capture_provenance:
        if not args.rapp1_path or not args.frame_chains_path:
            parser.error("both explicit source checkouts required")
        (ROOT / "provenance.json").write_bytes(encode(provenance(args.rapp1_path, args.frame_chains_path)))
    raw = encode(manifest())
    path = ROOT / "manifest.json"
    if args.write:
        path.write_bytes(raw)
    if args.write_index:
        index_path = ROOT / "experimental-index.json"
        index = {"profiles": []}
        index.update(authority=False, workspace_latest="rapp-workspace/1.0",
                     workspace_family="rapp-workspace/1", legacy_workspace_inputs=legacy_inputs())
        index["profiles"] = [p for p in index["profiles"] if not p["name"].startswith("rapp-workspace/")] + index_profiles()
        index["generated_utc"] = json.loads((ROOT / "provenance.json").read_bytes())["inspected_utc"]
        index_path.write_bytes(encode(index))
    good = path.is_file() and path.read_bytes() == raw
    indexed = index_matches() if path.is_file() else False
    print(f"Workspace Grail/1 manifest {'PASS' if good else 'FAIL'}; protocol index {'PASS' if indexed else 'FAIL'}")
    return int(not (good and indexed))


if __name__ == "__main__":
    raise SystemExit(main())
