"""Exact-byte file manifest and additive protocol-index entry; no estate activation."""

from __future__ import annotations

import argparse
import json

from common import REPO, pretty, read_file, require, sha, write_file
from schema_source import GENERATED_UTC, PROFILE, ROOT

INDEX = REPO / "protocols/index.json"


def inventory():
    result = []
    total = 0
    for visited, path in enumerate(ROOT.rglob("*"), 1):
        require(visited <= 512, "profile directory-entry budget")
        if "__pycache__" in path.parts or path.suffix in (".pyc", ".pyo"):
            continue
        require(not path.is_symlink(), "symlink in profile inventory")
        if not path.is_file() or path == ROOT / "manifest.json":
            continue
        raw = read_file(path)
        total += len(raw)
        require(len(result) < 128 and total <= 8 * 1024 * 1024, "profile inventory budget")
        result.append({
            "path": path.relative_to(ROOT).as_posix(), "sha256": sha(raw), "bytes": len(raw),
        })
    return sorted(result, key=lambda item: item["path"])


def manifest():
    return {
        "schema": "rapp-work-index-file-manifest/1",
        "profile": PROFILE,
        "parent": "rapp-workspace/1",
        "substrate": "rapp/1",
        "generated_utc": GENERATED_UTC,
        "status": "optional-application-profile",
        "authority": False,
        "grants_authority": False,
        "activation": "not-activated",
        "activation_authority": "external-host-only",
        "signed_activation": False,
        "carrier": "rapp/1 memory.save",
        "closed_sibling_profiles_modified": False,
        "files": inventory(),
    }


def index_entry(manifest_raw):
    entry = {
        "name": PROFILE,
        "human_name": "RAPP Work Index/1",
        "parent": "rapp-workspace/1",
        "substrate": "rapp/1",
        "status": "optional-application-profile",
        "authority": False,
        "grants_authority": False,
        "activation": "not-activated",
        "activation_authority": "external-host-only",
        "signed_activation": False,
        "closed_sibling_profiles_modified": False,
    }
    for label, name in (
        ("spec", "SPEC.md"), ("schema", "schema.json"),
        ("manifest", "manifest.json"), ("provenance", "provenance.json"),
        ("safety_matrix", "safety-matrix.json"),
    ):
        raw = manifest_raw if label == "manifest" else read_file(ROOT / name)
        entry[label + "_path"] = "protocols/" + PROFILE + "/" + name
        entry[label + "_sha256"] = sha(raw)
        entry[label + "_bytes"] = len(raw)
    entry.update({
        "conformance": "protocols/" + PROFILE + "/reference/conformance.py",
        "fixtures": "public-synthetic-only",
        "canonical_checkpoint": "explicit-canonical-rapp1-checkout-required",
        "durable_lookup": "indexed-O(log-n)-plus-results-after-bounded-snapshot-verification",
        "network_access": False,
        "background_workers": 0,
    })
    return entry


def updated_index(entry):
    index = json.loads(read_file(INDEX))
    names = [item["name"] for item in index["profiles"]]
    require(len(names) == len(set(names)), "duplicate profile index entries")
    profiles = [item for item in index["profiles"] if item["name"] != PROFILE]
    position = next(
        (i + 1 for i, item in enumerate(profiles) if item["name"] == "rapp-work-compatibility/1"),
        len(profiles),
    )
    profiles.insert(position, entry)
    return {**index, "generated_utc": GENERATED_UTC, "profiles": profiles}


def check():
    expected = pretty(manifest())
    require(read_file(ROOT / "manifest.json") == expected, "profile exact-byte manifest drift")
    require(read_file(INDEX) == pretty(updated_index(index_entry(expected))),
            "profile index exact bytes/counts/order drift")
    return expected


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.write:
        raw = pretty(manifest())
        write_file(ROOT / "manifest.json", raw)
        write_file(INDEX, pretty(updated_index(index_entry(raw))))
    check()
    print("rapp-work-index/1 manifest/index: exact generated match")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
