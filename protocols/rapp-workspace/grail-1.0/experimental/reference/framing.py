"""Frame Anything: opaque local capture and conditional RW/1 structural admission."""

import base64
import hashlib
import os
from pathlib import Path
import stat
import time

from common import address, directory, require, sha
from schema_source import GENERATION, PROFILE

MAX_ENTRIES = 128
MAX_FILES = 64
MAX_FILE_BYTES = 16 * 1024 * 1024
MAX_TOTAL_BYTES = 64 * 1024 * 1024
INLINE_BYTES = 4096
MAX_DEPTH = 16
MAX_SECONDS = 5


def b64(raw):
    return base64.b64encode(raw).decode("ascii")


def unb64(value):
    require(isinstance(value, str), "opaque octets must use base64 text")
    raw = base64.b64decode(value, validate=True)
    require(b64(raw) == value, "noncanonical opaque octets")
    return raw


def _identity(s):
    return (s.st_dev, s.st_ino, s.st_mode, s.st_nlink, s.st_size, s.st_mtime_ns, s.st_ctime_ns)


def _kind(s):
    return ("file" if stat.S_ISREG(s.st_mode) else "directory" if stat.S_ISDIR(s.st_mode)
            else "symlink" if stat.S_ISLNK(s.st_mode) else "special")


def capture_object(path):
    """Capture only the named object. Never follow a symlink or open a special node."""
    path = Path(path)
    require(".." not in path.parts, "explicit object path required")
    path = path.absolute()
    require(path.name not in ("", ".", ".."), "filesystem root is outside bounded object framing")
    entries, identities = [], {}
    total = regular_files = 0
    deadline = time.monotonic() + MAX_SECONDS

    def budget():
        require(time.monotonic() <= deadline, "Frame Anything observation time budget")

    def node(parent, name, parts, depth, root=False):
        nonlocal total, regular_files
        budget()
        require(depth <= MAX_DEPTH, "Frame Anything depth budget")
        expected = os.stat(name, dir_fd=parent, follow_symlinks=False)
        kind = _kind(expected)
        relative = b"/".join(os.fsencode(p) for p in parts)
        identities[("root:" if root else "entry:") + b64(relative)] = _identity(expected)
        item = {"path_b64": b64(relative), "kind": kind, "mode": expected.st_mode,
                "bytes": None, "sha256": None, "octets_b64": None, "coverage": "metadata-only"}
        if not (root and kind == "directory"):
            require(len(entries) < MAX_ENTRIES, "Frame Anything entry budget")
            entries.append(item)
        if kind == "directory":
            child = os.open(name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=parent)
            try:
                require(_identity(os.fstat(child)) == _identity(expected), "directory identity replacement")
                names = []
                with os.scandir(child) as scan:
                    for entry in scan:
                        budget()
                        require(len(names) + len(entries) < MAX_ENTRIES, "Frame Anything entry budget")
                        names.append(entry.name)
                for entry in sorted(names, key=os.fsencode):
                    node(child, entry, ([] if root else parts) + [entry], depth + 1)
                require(_identity(expected) == _identity(os.fstat(child)) == _identity(
                    os.stat(name, dir_fd=parent, follow_symlinks=False)), "directory changed during capture")
            finally:
                os.close(child)
        elif kind == "file":
            regular_files += 1
            require(regular_files <= MAX_FILES and expected.st_nlink == 1, "file budget or unsafe hardlink")
            require(expected.st_size <= MAX_FILE_BYTES and total + expected.st_size <= MAX_TOTAL_BYTES,
                    "Frame Anything byte budget")
            child = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=parent)
            try:
                require(_identity(os.fstat(child)) == _identity(expected), "file identity replacement")
                digest, chunks, size = hashlib.sha256(), [], 0
                while True:
                    budget()
                    raw = os.read(child, min(65536, MAX_FILE_BYTES + 1 - size))
                    if not raw:
                        break
                    size += len(raw)
                    require(size <= MAX_FILE_BYTES and total + size <= MAX_TOTAL_BYTES, "Frame Anything byte budget")
                    digest.update(raw)
                    if size <= INLINE_BYTES:
                        chunks.append(raw)
                require(_identity(expected) == _identity(os.fstat(child)) == _identity(
                    os.stat(name, dir_fd=parent, follow_symlinks=False)), "source changed during capture")
            finally:
                os.close(child)
            total += size
            item.update(bytes=size, sha256=digest.hexdigest(),
                        octets_b64=b64(b"".join(chunks)) if size <= INLINE_BYTES else None,
                        coverage="inline" if size <= INLINE_BYTES else "digest-only")
        elif kind == "symlink":
            raw = os.fsencode(os.readlink(name, dir_fd=parent))
            require(len(raw) <= INLINE_BYTES and total + len(raw) <= MAX_TOTAL_BYTES, "link-target metadata budget")
            total += len(raw)
            item.update(bytes=len(raw), sha256=sha(raw), octets_b64=b64(raw), coverage="inline")
        require(_identity(expected) == _identity(os.stat(name, dir_fd=parent, follow_symlinks=False)),
                "object identity changed during capture")
        return kind

    with directory(path.parent) as fd:
        root_kind = node(fd, path.name, [path.name], 0, root=True)
    entries.sort(key=lambda e: unb64(e["path_b64"]))
    return {"object_kind": root_kind, "root_name_b64": b64(os.fsencode(path.name)),
            "entries": entries, "identities": identities, "bytes_read": total}


def descriptor(source):
    return {key: source[key] for key in ("object_kind", "root_name_b64", "entries")}


def validate_object(core, source):
    core.schemas.validate(source)
    names = []
    kinds = {}
    root_name = unb64(source["root_name_b64"])
    require(root_name and b"/" not in root_name and root_name not in (b".", b".."), "opaque root name")
    total = 0
    for entry in source["entries"]:
        name = unb64(entry["path_b64"])
        require(name and b"\x00" not in name and all(p not in (b"", b".", b"..") for p in name.split(b"/")),
                "opaque path traversal")
        names.append(name)
        kinds[name] = entry["kind"]
        mode = entry["mode"]
        actual_kind = ("file" if stat.S_ISREG(mode) else "directory" if stat.S_ISDIR(mode)
                       else "symlink" if stat.S_ISLNK(mode) else "special")
        require(actual_kind == entry["kind"], "object kind/mode contradiction")
        if entry["kind"] in ("directory", "special"):
            require(entry["coverage"] == "metadata-only"
                    and entry["bytes"] is entry["sha256"] is entry["octets_b64"] is None,
                    "metadata-only framing cannot claim content bytes")
        elif entry["coverage"] == "inline":
            raw = unb64(entry["octets_b64"])
            require(len(raw) == entry["bytes"] and len(raw) <= INLINE_BYTES and sha(raw) == entry["sha256"],
                    "opaque object byte substitution")
        else:
            require(entry["kind"] == "file" and entry["coverage"] == "digest-only"
                    and type(entry["bytes"]) is int and entry["bytes"] > INLINE_BYTES
                    and isinstance(entry["sha256"], str) and entry["octets_b64"] is None,
                    "digest-only receipt coverage mismatch")
        total += entry["bytes"] or 0
    require(names == sorted(set(names)) and total <= MAX_TOTAL_BYTES, "object inventory bounds/order")
    require(sum(e["kind"] == "file" for e in source["entries"]) <= MAX_FILES, "object file budget")
    for name in names:
        parts = name.split(b"/")
        require(all(kinds.get(b"/".join(parts[:i])) == "directory" for i in range(1, len(parts))),
                "incomplete directory ancestry")
    if source["object_kind"] != "directory":
        require(len(source["entries"]) == 1 and names == [root_name]
                and source["entries"][0]["kind"] == source["object_kind"], "standalone object binding")
    require(source["fingerprint"] == core.particle(descriptor(source)), "object fingerprint substitution")


def object_metadata(source):
    return [{"name": "object-kind", "value": source["object_kind"]},
            {"name": "entry-count", "value": len(source["entries"])},
            {"name": "source-fingerprint", "value": source["fingerprint"]["hash"]}]


def frame_object(workspace, path, utc):
    captured = capture_object(path)
    source = workspace.payload(
        "opaque-local-object", subject="explicit-local-object", **descriptor(captured),
        fingerprint=workspace.core.particle(descriptor(captured)), read_scope="explicit-local-object",
        native_identity=None, semantics="unknown", native_compliance="unclaimed")
    validate_object(workspace.core, source)
    source_ref = workspace.append(source, utc)
    observation = workspace.observation(
        source["subject"], "unclassified-local-object", object_metadata(source), utc, sources=[source_ref])
    return source_ref, observation, captured


def synthesize_attempt(core, source, observation, tick=0):
    validate_object(core, source)
    core.schemas.validate(observation)
    require(observation["metadata"] == object_metadata(source)
            and observation["fingerprint"] == core.particle(observation["metadata"]),
            "workspace attempt requires bound evidence")
    return {
        "op": "workspace-attempt", "tick": tick,
        "read": {"name": "opaque-object", "input": 0, "pointer": ""},
        "context_read": {"name": "object-observation", "input": 1, "pointer": ""},
        "members": [i for i, e in enumerate(source["entries"]) if e["kind"] == "file"],
    }


def admission(source):
    """Necessary conditions for this bounded structural workspace class, not native semantics."""
    if source["object_kind"] != "directory":
        return "incompatible-object-kind"
    if any(e["kind"] in ("symlink", "special") for e in source["entries"]):
        return "unresolved-links-or-special-members"
    files = [e for e in source["entries"] if e["kind"] == "file"]
    if any(e["coverage"] != "inline" for e in files):
        return "external-content-evidence-required"
    if len(files) < 2:
        return "insufficient-workspace-evidence"
    return None


def outcome(workspace, source_ref, observation_ref, tick, context=None, context_observation=None, feedback=None):
    source = workspace.body(source_ref, "opaque-local-object")
    observation = workspace.body(observation_ref, "native-shape-observation")
    validate_object(workspace.core, source)
    require(observation["sources"] == [source_ref] and observation["metadata"] == object_metadata(source),
            "unbound workspace observation")
    basis = source
    reason = admission(source)
    contradictions = []
    if any(ref is not None for ref in (context, context_observation, feedback)):
        require(all(ref is not None for ref in (context, context_observation, feedback)), "complete repair context required")
        from iteration import verified_exhaust
        exhaust = verified_exhaust(workspace, feedback)
        require(exhaust["root"] == source_ref and exhaust["classification"] in
                ("unresolved", "partial", "contradiction", "refusal"), "repair requires source-bound refusal exhaust")
        require(exhaust["code"] in {
            "incompatible-object-kind", "insufficient-workspace-evidence", "external-content-evidence-required",
            "source-not-bound-to-context", "context-source-contradiction",
        } and bool(exhaust["missing_fields"]), "refusal does not justify this context repair")
        basis = workspace.body(context, "opaque-local-object")
        context_obs = workspace.body(context_observation, "native-shape-observation")
        validate_object(workspace.core, basis)
        require(context_obs["sources"] == [context] and context_obs["metadata"] == object_metadata(basis),
                "unbound repair context observation")
        reason = admission(basis)
        if source["object_kind"] != "file" or source["entries"][0]["coverage"] != "inline":
            reason = "unsupported-context-repair"
        elif reason is None:
            original = source["entries"][0]
            name = unb64(source["root_name_b64"])
            matching = [e for e in basis["entries"] if e["kind"] == "file"
                        and unb64(e["path_b64"]).split(b"/")[-1] == name]
            contradictions = [{"source_sha256": original["sha256"], "context_sha256": e["sha256"]}
                              for e in matching if (e["sha256"], e["bytes"], e["octets_b64"]) !=
                              (original["sha256"], original["bytes"], original["octets_b64"])]
            contradictions = sorted({(c["source_sha256"], c["context_sha256"]) for c in contradictions})
            contradictions = [{"source_sha256": a, "context_sha256": b} for a, b in contradictions]
            if contradictions:
                reason = "context-source-contradiction"
            elif len(matching) != 1:
                reason = "source-not-bound-to-context"
    fields = dict(source=source_ref, observation=observation_ref, tick=tick,
                  context=context, context_observation=context_observation, feedback=feedback)
    if reason:
        return workspace.payload(
            "workspace-unresolved", **fields,
            reason=reason, retry_requirement="additional-verified-workspace-context",
            missing_fields=["unique-context-member" if reason == "source-not-bound-to-context" else
                            "contradiction-resolution" if contradictions else "verified-workspace-context"],
            contradictions=contradictions,
            adoption_eligible=False, native_compliance="unclaimed")
    return workspace.payload(
        "workspace-successor", **fields,
        members=[{"entry": i, "path_b64": e["path_b64"], "sha256": e["sha256"], "bytes": e["bytes"]}
                 for i, e in enumerate(basis["entries"]) if e["kind"] == "file"],
        admission_class="verified-structural-container", adoption_eligible=True, native_compliance="unclaimed")


def validate_outcome(workspace, payload):
    expected = outcome(workspace, payload["source"], payload["observation"], payload["tick"],
                       payload["context"], payload["context_observation"], payload["feedback"])
    require(payload == expected, "workspace outcome is not justified by source evidence")


def synthesize_context_attempt(core, source, observation, feedback, context, context_observation, tick=0):
    synthesize_attempt(core, source, observation, tick)
    synthesize_attempt(core, context, context_observation, tick)
    core.schemas.validate(feedback)
    require(feedback["schema"] == PROFILE + "/iteration-exhaust"
            and feedback["classification"] in ("unresolved", "partial", "contradiction", "refusal"),
            "context lens synthesis requires refusal information")
    names = ("opaque-object", "object-observation", "refusal-exhaust", "workspace-context", "context-observation")
    return {"op": "workspace-context-attempt", "tick": tick,
            "repair_code": feedback["code"],
            "reads": [{"name": name, "input": i, "pointer": ""} for i, name in enumerate(names)],
            "members": [i for i, e in enumerate(context["entries"]) if e["kind"] == "file"]}


def execute_attempt(workspace, manifest, program):
    inputs = manifest["sources"] + manifest["contexts"]
    source_ref = inputs[program["read"]["input"]]
    observation_ref = inputs[program["context_read"]["input"]]
    source = workspace.body(source_ref, "opaque-local-object")
    observation = workspace.body(observation_ref, "native-shape-observation")
    require(program == synthesize_attempt(workspace.core, source, observation, program["tick"]),
            "candidate mapping not justified by evidence")
    return outcome(workspace, source_ref, observation_ref, program["tick"])


def execute_context_attempt(workspace, manifest, program):
    inputs = manifest["sources"] + manifest["contexts"]
    require(len(inputs) == 5, "context lens needs all five declared inputs")
    source, obs, feedback, context, context_obs = [workspace.body(ref) for ref in inputs]
    require(program == synthesize_context_attempt(workspace.core, source, obs, feedback, context,
                                                  context_obs, program["tick"]),
            "context mapping not justified by exhaust/evidence")
    return outcome(workspace, inputs[0], inputs[1], program["tick"], inputs[3], inputs[4], inputs[2])

def object_lineage(workspace, references):
    """Follow declared data dependencies, not unrelated stream-clock predecessors."""
    pending, seen = list(references), set()
    while pending:
        ref = pending.pop()
        key = address(ref)
        if key in seen:
            continue
        seen.add(key)
        frame = workspace.frame(ref)
        body = workspace.body(ref)
        if body.get("generation") == GENERATION and body.get("schema") in {
            PROFILE + "/opaque-local-object", PROFILE + "/workspace-successor", PROFILE + "/workspace-unresolved",
        }:
            return True
        if body.get("generation") == GENERATION and body.get("schema") == PROFILE + "/native-shape-observation":
            pending.extend(body["sources"])
        if frame["payload"].get("schema") == PROFILE + "/derived-frame":
            reads = workspace.body(frame["payload"]["declared_reads"], "declared-reads")
            pending.extend(reads["sources"] + reads["contexts"])
    return False
