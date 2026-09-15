#!/usr/bin/env python3
"""RAPP Workspace/1 safe entry: distinct guarantees, no implicit authority."""

import argparse
from pathlib import Path
import subprocess
import sys

REFERENCE = Path(__file__).resolve().parents[1] / "protocols/rapp-workspace/1/reference"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["demo", "conformance", "schemas", "pins"])
    if len(sys.argv) > 1 and sys.argv[1] in {"demo", "conformance", "schemas", "pins"}:
        args, rest = argparse.Namespace(command=sys.argv[1]), sys.argv[2:]
    else:
        args, rest = parser.parse_known_args()
    script = {"demo": "safe_demo.py", "conformance": "conformance.py", "schemas": "schema_source.py", "pins": "pins.py"}[args.command]
    if args.command == "schemas" and not rest:
        rest = ["--check"]
    return subprocess.run([sys.executable, "-B", str(REFERENCE / script), *rest]).returncode


if __name__ == "__main__":
    raise SystemExit(main())
