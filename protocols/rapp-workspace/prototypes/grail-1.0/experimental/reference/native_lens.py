"""Bounded opaque observation and evidence-derived structural lens synthesis.

No provider adapters, native-format decoders, taxonomy, model calls, or owner
consent live here. The demo supplies only roots it created as synthetic data.
"""

import base64
import os
from pathlib import Path
import stat
import time

from common import directory, require, sha

MAX_ENTRIES = 32
MAX_FILES = 16
MAX_FILE_BYTES = 4096
MAX_TOTAL_BYTES = 16384
MAX_DEPTH = 4
MAX_SECONDS = 2


def _identity(info):
    return (info.st_dev, info.st_ino, info.st_mode, info.st_nlink,
            info.st_size, info.st_mtime_ns, info.st_ctime_ns)


def capture_native(root):
    """Read one explicitly supplied fixture root, opaquely, through no-follow descriptors."""
    files, identities = [], {}
    entries = total = 0
    deadline = time.monotonic() + MAX_SECONDS

    def bounded():
        require(time.monotonic() <= deadline, "native observation time budget")

    def walk(fd, prefix, depth):
        nonlocal entries, total
        bounded()
        require(depth <= MAX_DEPTH, "native observation depth budget")
        before_dir = os.fstat(fd)
        names = []
        with os.scandir(fd) as scan:
            for entry in scan:
                entries += 1
                require(entries <= MAX_ENTRIES, "native observation entry budget")
                bounded()
                names.append(entry.name)
        for name in sorted(names):
            bounded()
            relative = "/".join([*prefix, name])
            expected = os.stat(name, dir_fd=fd, follow_symlinks=False)
            require(not stat.S_ISLNK(expected.st_mode), "native observation symlink refusal")
            if stat.S_ISDIR(expected.st_mode):
                child = os.open(name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
                try:
                    require(_identity(os.fstat(child)) == _identity(expected), "native directory replacement")
                    walk(child, [*prefix, name], depth + 1)
                    require(_identity(os.fstat(child)) == _identity(
                        os.stat(name, dir_fd=fd, follow_symlinks=False)), "native directory replacement")
                finally:
                    os.close(child)
                continue
            require(stat.S_ISREG(expected.st_mode) and expected.st_nlink == 1,
                    "native observation non-regular file or hardlink")
            require(name != "rappid.json", "demo requires unknown non-RAPP roots, not native RAPP identities")
            require(len(files) < MAX_FILES, "native observation file budget")
            require(expected.st_size <= MAX_FILE_BYTES and total + expected.st_size <= MAX_TOTAL_BYTES,
                    "native observation byte budget")
            child = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=fd)
            try:
                before = os.fstat(child)
                require(_identity(before) == _identity(expected), "native file replacement")
                chunks, read = [], 0
                while True:
                    bounded()
                    chunk = os.read(child, min(1024, MAX_FILE_BYTES + 1 - read))
                    if not chunk:
                        break
                    chunks.append(chunk)
                    read += len(chunk)
                    require(read <= MAX_FILE_BYTES and total + read <= MAX_TOTAL_BYTES,
                            "native observation byte budget")
                raw = b"".join(chunks)
                require(_identity(before) == _identity(os.fstat(child)) == _identity(
                    os.stat(name, dir_fd=fd, follow_symlinks=False)), "native source changed during observation")
            finally:
                os.close(child)
            total += len(raw)
            identities[relative] = _identity(before)
            files.append({"path": relative, "bytes": len(raw), "sha256": sha(raw),
                          "octets_b64": base64.b64encode(raw).decode("ascii")})
        require(_identity(before_dir) == _identity(os.fstat(fd)), "native directory changed during observation")
        identities["/" + "/".join(prefix)] = _identity(before_dir)

    root = Path(root)
    with directory(root) as fd:
        walk(fd, [], 0)
    require(files, "empty native shape is not acceptance evidence")
    return {"files": sorted(files, key=lambda f: f["path"]), "identities": identities,
            "entries_scanned": entries, "bytes_read": total}


def inventory(files):
    return [{key: item[key] for key in ("path", "bytes", "sha256")} for item in files]


def validate_source(core, payload):
    core.schemas.validate(payload)
    require([f["path"] for f in payload["files"]] == sorted({f["path"] for f in payload["files"]}),
            "opaque source paths must be unique and ordered")
    total = 0
    for item in payload["files"]:
        raw = base64.b64decode(item["octets_b64"], validate=True)
        require(base64.b64encode(raw).decode("ascii") == item["octets_b64"], "noncanonical opaque encoding")
        require(len(raw) == item["bytes"] and sha(raw) == item["sha256"], "opaque source byte substitution")
        total += len(raw)
    require(total <= MAX_TOTAL_BYTES, "opaque source aggregate byte budget")
    require(core.particle(inventory(payload["files"])) == payload["inventory"], "opaque inventory substitution")


def source_metadata(source):
    return [{"name": item["path"], "value": item["sha256"]} for item in source["files"]]


def observe_native(workspace, root, utc, *, tile=None):
    """Capture first, then emit source and bound observation; never write into root."""
    captured = capture_native(root)
    source = workspace.payload(
        "opaque-native-source", subject=Path(root).name, files=captured["files"],
        inventory=workspace.core.particle(inventory(captured["files"])),
        native_identity=None, read_scope="explicit-synthetic-fixture-files", native_compliance="unclaimed")
    validate_source(workspace.core, source)
    source_ref = workspace.append(source, utc)
    observation_ref = workspace.observation(
        source["subject"], "unclassified-native-layout", source_metadata(source), utc,
        tile=tile, findings=["unknown-native-shape"], sources=[source_ref])
    return source_ref, observation_ref, captured


def synthesize_program(core, observation, source, tick):
    """Learn a closed IR read-map from observed paths; no fixture catalog or consent input."""
    validate_source(core, source)
    core.schemas.validate(observation)
    require(observation["subject"] == source["subject"]
            and observation["metadata"] == source_metadata(source)
            and observation["fingerprint"] == core.particle(observation["metadata"]),
            "synthesis requires source-bound measured evidence")
    bindings = [
        {"name": item["name"],
         "read": {"name": item["name"], "input": 0, "pointer": f"/metadata/{i}/value"}}
        for i, item in enumerate(observation["metadata"])
    ]
    bindings.append({"name": "source:" + source["subject"],
                     "read": {"name": "source:" + source["subject"], "input": 1, "pointer": "/inventory/hash"}})
    return {"op": "project", "tick": tick, "bindings": bindings}
