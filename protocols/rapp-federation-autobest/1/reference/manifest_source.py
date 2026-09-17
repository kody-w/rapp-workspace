"""Generate the exact-byte profile manifest."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXCLUDED = {
    "manifest.json",
    "conformance-results.json",
}


def files():
    result = []
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(ROOT).as_posix()
        if relative in EXCLUDED or "__pycache__" in path.parts or path.suffix == ".pyc":
            continue
        raw = path.read_bytes()
        result.append(
            {
                "path": relative,
                "sha256": hashlib.sha256(raw).hexdigest(),
                "bytes": len(raw),
            }
        )
    return result


def manifest():
    return {
        "schema": "rapp-federation-autobest-file-manifest/1",
        "profile": "rapp-federation-autobest/1",
        "parent": "rapp/1",
        "status": "candidate",
        "activation": "not-activated",
        "generic_ceo_agent": {
            "status": "verified",
            "sha256": "827f637c024e3fa1229148e5dcd78230a84ea3214283f899d22603741350f23c",
            "skill_sha256": "5f8bd5b3c48858329f87ae3812dbc30ee604cb664985dc3d42a79e69d8bdfda8",
            "activation": "external-host-only",
        },
        "carrier": "rapp/1 memory.save",
        "closed_sibling_profiles_modified": False,
        "files": files(),
    }


def manifest_bytes():
    return (json.dumps(manifest(), ensure_ascii=False, indent=2) + "\n").encode("utf-8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    arguments = parser.parse_args()
    path = ROOT / "manifest.json"
    if arguments.check:
        if not path.is_file() or path.read_bytes() != manifest_bytes():
            raise SystemExit("manifest.json differs from profile files")
        print("manifest.json: exact generated match")
    else:
        path.write_bytes(manifest_bytes())
        print("wrote manifest.json")
