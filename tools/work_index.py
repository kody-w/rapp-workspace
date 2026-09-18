#!/usr/bin/env python3
"""Exact RAPP Work Index/1 gates; no implicit checkout discovery or activation."""

import argparse
from pathlib import Path
import subprocess
import sys

REPO = Path(__file__).resolve().parents[1]
REFERENCE = REPO / "protocols/rapp-work-index/1/reference"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["schemas", "vectors", "pins", "tests", "conformance"])
    args, rest = parser.parse_known_args()
    if args.command == "tests":
        command = [
            "-m", "unittest", "discover", "-s", "protocols/rapp-work-index/1/tests",
            "-p", "test_profile.py", *(rest or ["-v"]),
        ]
    else:
        script = {
            "schemas": "schema_source.py", "vectors": "vectors.py", "pins": "pins.py",
            "conformance": "conformance.py",
        }[args.command]
        command = [str(REFERENCE / script), *(rest or ([] if args.command == "conformance" else ["--check"]))]
    return subprocess.run([sys.executable, "-B", *command], cwd=REPO).returncode


if __name__ == "__main__":
    raise SystemExit(main())
