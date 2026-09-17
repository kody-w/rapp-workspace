#!/usr/bin/env python3
"""RAPP Work Organization/1 candidate schema, pin, and conformance entry."""

from __future__ import annotations

from pathlib import Path
import subprocess
import sys


REFERENCE = (
    Path(__file__).resolve().parents[1]
    / "protocols"
    / "rapp-work-organization"
    / "1"
    / "reference"
)


def main() -> int:
    commands = {
        "artifact": ("workorg_artifact.py", ["--check"]),
        "schemas": ("workorg_schema_source.py", ["--check"]),
        "pins": ("pins.py", []),
        "conformance": ("conformance.py", []),
    }
    if len(sys.argv) < 2 or sys.argv[1] not in commands:
        print(
            "usage: work_organization.py {artifact|schemas|pins|conformance} [args...]",
            file=sys.stderr,
        )
        return 2
    script, defaults = commands[sys.argv[1]]
    rest = sys.argv[2:] or defaults
    return subprocess.run(
        [sys.executable, "-B", str(REFERENCE / script), *rest],
        check=False,
    ).returncode


if __name__ == "__main__":
    raise SystemExit(main())
