#!/usr/bin/env python3
"""Candidate successor of the Workspace/1 runtime manifest (proposal 0024, not accepted).

The current `rapp-workspace-file-manifest/1`, its index entry and every consumer pin stay
byte-identical. The candidate is exactly what the staged post-switch generator writes once
the owner switches: this tool applies the Workspace side of that switch to a scratch copy
of the repository, runs the staged generator there, and records the result additively.
The scratch copy never contains a symlink: copying skips every symlink (and scratch or build
products), so every path-based write in the copy stays inside it, and a skipped file the
staged generator needs fails closed as missing. Staged, canonical and recorded files are read
through no-follow paths. The tool never writes outside the scratch copy or, with --write,
outside the two files it records, which it checks first and then replaces atomically.
"""

import argparse
import difflib
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import stat
import subprocess
import sys
import uuid

REPO = Path(__file__).resolve().parents[1]
BASE = "protocols/rapp-workspace/1/"
sys.path.insert(0, str(REPO / BASE / "reference"))
from common import Refusal, directory, read_file, sha, write_file  # noqa: E402
from pins import encode, record as pinned_record  # noqa: E402

STAGED = BASE + "successor/staged"
SUFFIX = ".staged"
CANDIDATE_PATH = BASE + "successor/manifest.json" + SUFFIX
INDEX = "protocols/index.json"
CANDIDATE = "rapp-workspace-file-manifest/2"
PROPOSAL = "docs/proposals/0024-editable-front-door.md"
SCRATCH = ".validation/workspace-successor"
LIMIT = 16 * 1024 * 1024
IGNORED = shutil.ignore_patterns(".git", ".validation", ".hive-test-work", "__pycache__", "*.pyc", ".DS_Store")
# Editor swap, backup and lock files are never staged content.
STAGED_IGNORED = shutil.ignore_patterns(".git", "__pycache__", "*.pyc", ".DS_Store", "*.swp", "*.swo", "*~", ".#*",
                                        "#*#")
# Written by the generators themselves at the switch, never staged.
GENERATED = {BASE + "manifest.json", INDEX}


class SuccessorError(Exception):
    pass


def front_door(path):
    name = path.rsplit("/", 1)[-1].casefold()
    return name == "readme" or name.startswith("readme.")


def relative_parts(relative):
    parts = PurePosixPath(relative).parts
    if not parts or PurePosixPath(relative).is_absolute() or any(part in {"", ".", ".."} for part in parts):
        raise SuccessorError("unsafe relative path: " + relative)
    return parts


def real_directory(root, relative):
    """root/relative after proving that no component below root is a symlink or a non-directory."""
    path = root
    for part in relative_parts(relative):
        path = path / part
        if path.is_symlink() or (path.exists() and not path.is_dir()):
            raise SuccessorError("unsafe directory or symlink: " + relative)
    return path


def read(root, relative):
    relative_parts(relative)
    try:
        return read_file(root / relative, LIMIT)
    except Refusal as error:
        raise SuccessorError(relative + ": " + str(error)) from error


def record(relative):
    relative_parts(relative)
    return pinned_record(REPO, relative)


def staged_files():
    """Canonical repository path -> the exact bytes the switch installs there."""
    top = real_directory(REPO, STAGED)
    if not top.is_dir():
        raise SuccessorError("staged directory is missing")
    names = []
    for current, directories, files in os.walk(top, followlinks=False):
        skipped = STAGED_IGNORED(current, directories + files)
        directories[:] = [name for name in directories if name not in skipped]
        files = [name for name in files if name not in skipped]
        for name in sorted(directories + files):
            entry = Path(current) / name
            if entry.is_symlink() or not (entry.is_dir() or entry.is_file()):
                raise SuccessorError("unsafe staged entry: " + entry.relative_to(top).as_posix())
        names.extend(Path(current, name).relative_to(top).as_posix() for name in files)
    result = {}
    for relative in sorted(names):
        if not relative.endswith(SUFFIX):
            raise SuccessorError("staged file lacks the " + SUFFIX + " suffix: " + relative)
        canonical = relative[: -len(SUFFIX)]
        relative_parts(canonical)
        if canonical.startswith(BASE + "successor/") or canonical in GENERATED:
            raise SuccessorError("staged path is not switchable: " + canonical)
        if front_door(canonical):
            raise SuccessorError("front doors are never staged: " + canonical)
        if "/" in canonical:
            real_directory(REPO, canonical.rsplit("/", 1)[0])
        target = REPO / canonical
        if target.is_symlink() or not target.is_file():
            raise SuccessorError("staged file replaces no regular file: " + canonical)
        raw = read(REPO, STAGED + "/" + relative)
        if raw == read(REPO, canonical):
            raise SuccessorError("staged file changes nothing: " + canonical)
        result[canonical] = raw
    if not result:
        raise SuccessorError("no staged post-switch files")
    return result


def skip_links(folder, names):
    """copytree filter: skip scratch and build products, every symlink, and special or unreadable entries.

    The copy therefore holds only readable regular files and directories and never a link.
    """
    skipped = IGNORED(folder, names)
    for name in names:
        path = os.path.join(folder, name)
        try:
            mode = os.lstat(path).st_mode
        except OSError:
            skipped.add(name)
            continue
        if stat.S_ISREG(mode):
            readable = os.access(path, os.R_OK)
        elif stat.S_ISDIR(mode):
            readable = os.access(path, os.R_OK | os.X_OK)
        else:
            readable = False
        if not readable:
            skipped.add(name)
    return skipped


def switched_overlay(base, staged):
    """Copy the repository, apply the Workspace side of the switch, and run the staged generator."""
    root = base / "repo"
    try:
        shutil.copytree(REPO, root, symlinks=True, ignore=skip_links, copy_function=shutil.copyfile)
    except shutil.Error as error:
        source = error.args[0][0][0] if error.args and error.args[0] else ""
        raise SuccessorError("cannot copy the working tree: " + relative_name(source)) from None
    except OSError as error:
        raise SuccessorError("cannot copy the working tree: " + relative_name(error.filename or "")) from None
    for relative in (INDEX, BASE + "manifest.json"):
        written = root / relative
        if written.is_symlink() or not written.is_file():
            raise SuccessorError("not a regular file in the working tree: " + relative)
    current = read(root, BASE + "manifest.json")
    retained = BASE + "history/" + sha(current) + "/manifest.json"
    real_directory(root, BASE + "history")
    write_file(root / retained, current, immutable=True)
    for canonical, raw in staged.items():
        write_file(root / canonical, raw)
    shutil.rmtree(real_directory(root, BASE + "successor"))
    completed = subprocess.run(
        [sys.executable, "-B", str(root / BASE / "reference" / "pins.py"), "--write", "--write-index"],
        cwd=root, capture_output=True, text=True, timeout=300,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
    lines = completed.stdout.strip().splitlines()
    if completed.returncode != 0 or not lines or not lines[-1].endswith("PASS"):
        raise SuccessorError("staged generator failed after the switch: "
                             + (completed.stdout + completed.stderr).strip())
    return root


def relative_name(path):
    """A repository- or scratch-relative name for messages; never an absolute local path."""
    for anchor in (REPO / SCRATCH, REPO):
        try:
            relative = Path(path).relative_to(anchor).as_posix()
        except ValueError:
            continue
        return relative.split("/", 2)[-1] if anchor != REPO else relative
    return Path(path).name or "(unknown entry)"


def remove_scratch(base, strict):
    """Remove one scratch copy, making copied read-only directories writable first."""
    try:
        for current, _, _ in os.walk(base):
            os.chmod(current, 0o700)
        shutil.rmtree(base)
    except OSError:
        if strict:
            raise SuccessorError("could not remove the scratch copy under " + SCRATCH) from None


def generate():
    staged = staged_files()
    scratch = real_directory(REPO, SCRATCH)
    scratch.mkdir(parents=True, exist_ok=True)
    base = scratch / uuid.uuid4().hex
    base.mkdir(mode=0o700)
    try:
        root = switched_overlay(base, staged)
        raw = read(root, BASE + "manifest.json")
    except BaseException:
        remove_scratch(base, strict=False)
        raise
    remove_scratch(base, strict=True)
    value = json.loads(raw)
    pinned = {}
    for key, prefix in (("normative", BASE), ("reference", BASE), ("repository_evidence", "")):
        for item in value[key]:
            pinned[prefix + item["path"]] = (item["sha256"], item["bytes"])
    for key, prefix in (("provenance", BASE), ("prototype_catalog", "")):
        pinned[prefix + value[key]["path"]] = (value[key]["sha256"], value[key]["bytes"])
    for canonical, staged_raw in staged.items():
        if pinned.get(canonical) != (sha(staged_raw), len(staged_raw)):
            raise SuccessorError("staged file is not pinned by the candidate: " + canonical)
    current = record(BASE + "manifest.json")
    if [item["sha256"] for item in value.get("predecessors", [])] != [current["sha256"]]:
        raise SuccessorError("the candidate does not succeed the current manifest")
    return raw


def candidate_entry():
    spec = record(BASE + "SPEC.md")
    successor = record(CANDIDATE_PATH)
    return {
        "name": CANDIDATE,
        "human_name": "RAPP Workspace/1 runtime manifest successor",
        "parent": "rapp/1",
        "profile": "rapp-workspace/1",
        "authority": False,
        "status": "candidate",
        "acceptance": "owner-only",
        "proposal": PROPOSAL,
        "successor_of": record(BASE + "manifest.json"),
        "spec_path": spec["path"], "spec_sha256": spec["sha256"], "spec_bytes": spec["bytes"],
        "manifest_path": successor["path"], "manifest_sha256": successor["sha256"],
        "manifest_bytes": successor["bytes"],
        "staged_path": STAGED,
        "generator": "tools/workspace_successor.py",
    }


def recorded_mode(relative, parent=None):
    """The mode to keep for a recorded file; an existing entry must be a regular, singly linked file."""
    folder, name = relative.rsplit("/", 1)
    if parent is None:
        real_directory(REPO, folder)
        with directory(REPO / folder) as descriptor:
            return recorded_mode(relative, descriptor)
    try:
        status = os.stat(name, dir_fd=parent, follow_symlinks=False)
    except FileNotFoundError:
        return 0o644
    if not stat.S_ISREG(status.st_mode) or status.st_nlink != 1:
        raise SuccessorError("unsafe recorded file: " + relative)
    return stat.S_IMODE(status.st_mode)


def write_recorded(relative, raw):
    """Atomically replace one recorded working-tree file through its directory descriptor, keeping its mode."""
    folder, name = relative.rsplit("/", 1)
    real_directory(REPO, folder)
    with directory(REPO / folder) as parent:
        mode = recorded_mode(relative, parent)
        pending = ".pending-" + uuid.uuid4().hex
        fd = os.open(pending, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600, dir_fd=parent)
        try:
            with os.fdopen(fd, "wb") as stream:
                stream.write(raw)
                stream.flush()
                os.fchmod(stream.fileno(), mode)
                os.fsync(stream.fileno())
            os.replace(pending, name, src_dir_fd=parent, dst_dir_fd=parent)
            os.fsync(parent)
        finally:
            try:
                os.unlink(pending, dir_fd=parent)
            except FileNotFoundError:
                pass


def write_index():
    """Replace or append only the candidate entry; every other byte of the index is kept."""
    index = json.loads(read(REPO, INDEX))
    entry, profiles = candidate_entry(), []
    for item in index["profiles"]:
        if item.get("name") != CANDIDATE:
            profiles.append(item)
        elif entry is not None:
            profiles.append(entry)
            entry = None
    index["profiles"] = profiles + ([entry] if entry is not None else [])
    write_recorded(INDEX, encode(index))


def check():
    raw = generate()
    if read(REPO, CANDIDATE_PATH) != raw:
        raise SuccessorError("the recorded candidate is not the staged generator's output")
    index = json.loads(read(REPO, INDEX))
    if [item for item in index["profiles"] if item.get("name") == CANDIDATE] != [candidate_entry()]:
        raise SuccessorError("protocols/index.json does not record exactly this candidate")


def show_diff():
    for canonical, raw in staged_files().items():
        before = read(REPO, canonical).decode().splitlines(keepends=True)
        after = raw.decode().splitlines(keepends=True)
        sys.stdout.writelines(difflib.unified_diff(before, after, "a/" + canonical, "b/" + canonical))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true",
                        help="regenerate the recorded candidate and its index entry")
    parser.add_argument("--diff", action="store_true", help="print what the switch changes in pinned files")
    args = parser.parse_args(argv)
    label = "Workspace/1 successor candidate (proposal 0024): "
    try:
        if args.diff:
            show_diff()
            return 0
        if args.write:
            raw = generate()
            for relative in (CANDIDATE_PATH, INDEX):
                recorded_mode(relative)
            write_recorded(CANDIDATE_PATH, raw)
            write_index()
        check()
    except (OSError, ValueError, KeyError, TypeError, Refusal, SuccessorError, subprocess.SubprocessError) as error:
        print(label + "FAIL (" + str(error) + ")")
        return 1
    print(label + "PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
