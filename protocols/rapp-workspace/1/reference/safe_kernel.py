"""Minimal Workspace/1 core kernel. Effects and effective grants never come from the learned graph."""

import base64
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime
import fcntl
import json
import os
from pathlib import Path
import sqlite3
import types

from common import Refusal, ROOT, address, directory, domain, read_file, require, sha, wave, write_file
from pins import encode, manifest
from schema_source import GUARANTEES, PROFILE, RIGHTS

MAX_OCTETS = 65536
DISABLED = frozenset({
    "model_submission", "redistribution", "execution", "network", "loopback", "imports", "host_tool",
    "external_effect", "partitioned_effect", "native_rebinding", "live_migration", "timed_erasure",
    "learned_semantic_capability", "html_materialization", "live_delta", "unqualified_runtime",
    "repository_clone", "branch_history", "hive_publication",
})


def b64(raw):
    return base64.b64encode(raw).decode("ascii")


def unb64(value):
    raw = base64.b64decode(value, validate=True)
    require(b64(raw) == value, "noncanonical base64")
    return raw


def _bounded_text(value, maximum, reason):
    require(type(value) is str and 0 < len(value.encode("utf-8")) <= maximum
            and not any(ord(char) < 32 for char in value), reason)
    return value


def _canonical_sha256(value):
    raw = json.dumps(
        value, sort_keys=True, ensure_ascii=True, allow_nan=False,
        separators=(",", ":"),
    ).encode("ascii")
    return sha(raw)


def catalog_document(core, raw):
    try:
        value = core.r._strict_json(raw)
        domain(value)
    except (ValueError, TypeError, UnicodeError, RecursionError) as error:
        raise Refusal("invalid-catalog-json") from error
    require(type(value) is dict and set(value) == {
        "schema", "catalog_id", "root_id", "shard_index", "shard_count",
        "snapshot_sha256", "branch_scope", "branch_evidence_status",
        "recursive", "entries",
    } and value["schema"] == "rapp-workspace/catalog-chunk/1",
        "closed-catalog-document-required")
    _bounded_text(value["catalog_id"], 128, "invalid-catalog-id")
    _bounded_text(value["root_id"], 512, "invalid-catalog-root")
    require(type(value["shard_index"]) is int and type(value["shard_count"]) is int
            and 1 <= value["shard_count"] <= 32
            and 0 <= value["shard_index"] < value["shard_count"],
            "invalid-catalog-shard")
    require(type(value["snapshot_sha256"]) is str
            and len(value["snapshot_sha256"]) == 64
            and all(char in "0123456789abcdef" for char in value["snapshot_sha256"]),
            "invalid-catalog-snapshot")
    require((value["branch_scope"], value["branch_evidence_status"]) in (
                ("default-branch-only", "external-host-observation-unproven"),
                ("not-applicable", "not-applicable"),
            ) and type(value["recursive"]) is bool,
            "unsupported-catalog-scope")
    entries = value["entries"]
    require(type(entries) is list and 1 <= len(entries) <= 256, "catalog-entry-bound")
    seen = set()
    for entry in entries:
        require(type(entry) is dict and set(entry) == {
            "id", "kind", "parent", "labels", "metadata_sha256", "share_class",
        }, "closed-catalog-entry-required")
        _bounded_text(entry["id"], 512, "invalid-catalog-entry-id")
        _bounded_text(entry["kind"], 64, "invalid-catalog-entry-kind")
        require(entry["parent"] is None or type(entry["parent"]) is str,
                "invalid-catalog-entry-parent")
        if entry["parent"] is not None:
            _bounded_text(entry["parent"], 512, "invalid-catalog-entry-parent")
        require(type(entry["labels"]) is list and len(entry["labels"]) <= 16
                and all(type(label) is str for label in entry["labels"])
                and len(entry["labels"]) == len(set(entry["labels"])),
                "invalid-catalog-entry-labels")
        for label in entry["labels"]:
            _bounded_text(label, 128, "invalid-catalog-entry-label")
        digest = entry["metadata_sha256"]
        require(type(digest) is str and len(digest) == 64
                and all(char in "0123456789abcdef" for char in digest),
                "invalid-catalog-entry-metadata")
        require(entry["share_class"] in (
            "public-source", "private-source", "excluded-source",
        ), "invalid-catalog-share-class")
        require(entry["id"] not in seen, "duplicate-catalog-entry")
        seen.add(entry["id"])
    return value


def organization_tile(core, raw):
    try:
        value = core.r._strict_json(raw)
        domain(value)
    except (ValueError, TypeError, UnicodeError, RecursionError) as error:
        raise Refusal("invalid-organization-json") from error
    require(type(value) is dict and set(value) == {
        "schema", "tree_id", "catalog_id", "root_group", "tile_index",
        "tile_count", "snapshot_sha256", "groups", "assignments",
    } and value["schema"] == "rapp-workspace/organization-tree-tile/1",
        "closed-organization-document-required")
    _bounded_text(value["tree_id"], 128, "invalid-organization-tree-id")
    _bounded_text(value["catalog_id"], 128, "invalid-catalog-id")
    _bounded_text(value["root_group"], 64, "invalid-organization-root")
    require(type(value["tile_index"]) is int and type(value["tile_count"]) is int
            and 1 <= value["tile_count"] <= 32
            and 0 <= value["tile_index"] < value["tile_count"],
            "invalid-organization-tile")
    require(type(value["snapshot_sha256"]) is str
            and len(value["snapshot_sha256"]) == 64
            and all(char in "0123456789abcdef" for char in value["snapshot_sha256"]),
            "invalid-organization-snapshot")
    groups = value["groups"]
    require(type(groups) is list and 1 <= len(groups) <= 512, "organization-group-bound")
    by_id = {}
    for group in groups:
        require(type(group) is dict and set(group) == {"id", "name", "parent"},
                "closed-organization-group-required")
        group_id = _bounded_text(group["id"], 64, "invalid-organization-group-id")
        require(group_id[0].isalpha() and group_id.isascii()
                and all(char.islower() or char.isdigit() or char == "-" for char in group_id),
                "invalid-organization-group-id")
        _bounded_text(group["name"], 128, "invalid-organization-group-name")
        require(group["parent"] is None or type(group["parent"]) is str,
                "invalid-organization-parent")
        if group["parent"] is not None:
            _bounded_text(group["parent"], 64, "invalid-organization-parent")
        require(group_id not in by_id, "duplicate-organization-group")
        by_id[group_id] = group
    require(value["root_group"] in by_id
            and by_id[value["root_group"]]["parent"] is None
            and sum(group["parent"] is None for group in groups) == 1,
            "organization-root-mismatch")
    depths = {}
    for group_id in by_id:
        visited, current, depth = set(), group_id, 0
        while current != value["root_group"]:
            require(current not in visited, "organization-cycle")
            visited.add(current)
            parent = by_id[current]["parent"]
            require(parent in by_id, "organization-orphan-parent")
            current, depth = parent, depth + 1
            require(depth <= 32, "organization-depth-bound")
        depths[group_id] = depth
    assignments = value["assignments"]
    require(type(assignments) is list and len(assignments) <= 10000,
            "organization-assignment-bound")
    for assignment in assignments:
        require(type(assignment) is dict and set(assignment) == {"entry_id", "group_id"},
                "closed-organization-assignment-required")
        _bounded_text(assignment["entry_id"], 512, "invalid-organization-entry")
        _bounded_text(assignment["group_id"], 64, "invalid-organization-group-id")
    return value, by_id, depths


def organization_documents(core, raws):
    require(type(raws) is list and 1 <= len(raws) <= 32,
            "organization-tree-source-bound")
    documents = [organization_tile(core, raw) for raw in raws]
    first, groups, depths = documents[0]
    indexes = set()
    assignments = []
    for document, current_groups, current_depths in documents:
        require((
            document["tree_id"], document["catalog_id"], document["root_group"],
            document["tile_count"], document["snapshot_sha256"],
            document["groups"], current_groups, current_depths,
        ) == (
            first["tree_id"], first["catalog_id"], first["root_group"],
            first["tile_count"], first["snapshot_sha256"],
            first["groups"], groups, depths,
        ), "organization-tile-family-mismatch")
        require(document["tile_index"] not in indexes,
                "duplicate-organization-tile-index")
        indexes.add(document["tile_index"])
        assignments.extend(document["assignments"])
    require(len(documents) == first["tile_count"]
            and indexes == set(range(first["tile_count"])),
            "incomplete-organization-tiles")
    require(len(assignments) <= 10000, "organization-assignment-bound")
    snapshot = {
        "tree_id": first["tree_id"],
        "catalog_id": first["catalog_id"],
        "root_group": first["root_group"],
        "groups": first["groups"],
        "assignments": sorted(
            assignments,
            key=lambda item: (item["entry_id"], item["group_id"]),
        ),
    }
    require(_canonical_sha256(snapshot) == first["snapshot_sha256"],
            "organization-snapshot-commitment-mismatch")
    return {**first, "assignments": assignments}, groups, depths


@dataclass(frozen=True)
class Scope:
    namespace: str
    native_key: str
    path: str | None = None

    def subject(self):
        return {"namespace": self.namespace, "native_key": self.native_key}


@dataclass(frozen=True)
class ExternalPolicy:
    """Trusted host input; never parsed from a source, lens, receipt or projected registry."""

    instance_rappid: str
    world_id: str
    spec_sha256: str
    runtime_sha256: str
    rights: frozenset
    scopes: tuple
    sequence: int = 1
    expires_utc: str = "2026-12-31T00:00:00.000Z"
    audience: tuple = ("local-owner",)
    max_attempts: int = 8
    max_depth: int = 4
    max_frames: int = 256
    max_total_octets: int = 1024 * 1024
    physical_deletion_required: bool = False
    partitioned: bool = False


class EvaluatorImage:
    """Consume the exact verified immutable evaluator bytes, not a re-opened pathname."""

    def __init__(self, octets, expected_sha256):
        require(type(octets) is bytes and sha(octets) == expected_sha256, "executable-closure-substitution")
        require(len(octets) <= 16384, "evaluator closure byte budget")
        allowed = {"type": type, "bytes": bytes, "str": str, "dict": dict, "len": len, "ValueError": ValueError}
        namespace = {"__builtins__": allowed}
        exec(compile(octets, "<verified-effect-free-evaluator>", "exec"), namespace)
        require(set(namespace) == {"__builtins__", "__doc__", "evaluate"}, "unexpected executable closure")
        self._evaluate = namespace["evaluate"]
        self.sha256 = expected_sha256
        self.octets = octets

    def evaluate(self, operation, value, field=""):
        require(operation in ("identity-octets", "json-field"), "effect-or-unknown-operation-disabled")
        return self._evaluate(operation, value, field)


class Controller:
    """One trusted local writer. SQLite commit is the adoption linearization point."""

    def __init__(self, core, directory_path, policy, *, now, checkpoint=None):
        require(type(policy) is ExternalPolicy, "external controller policy required")
        require(core.r.utc_valid(now), "explicit trusted host time required")
        require(core.r.rappid_valid(policy.instance_rappid), "canonical live-instance RAPPID required")
        require(not policy.physical_deletion_required, "timed-erasure-unproven-disabled-before-access")
        require(not policy.partitioned, "partitioned-effects-disabled-before-access")
        require(all(type(v) is int for v in (policy.sequence, policy.max_attempts, policy.max_depth,
                                             policy.max_frames, policy.max_total_octets)) and policy.sequence >= 1,
                "exact integer policy budgets required")
        require(1 <= policy.max_attempts <= 128 and 0 <= policy.max_depth <= 32
                and 8 <= policy.max_frames <= 512 and 1 <= policy.max_total_octets <= 64 * 1024 * 1024,
                "root-owned budget bounds")
        require(set(policy.rights) <= set(RIGHTS), "unknown capability")
        self.core, self.policy, self.path, self.now = core, policy, Path(directory_path), now
        self._scope_map = {self.subject_key(s.subject()): s for s in policy.scopes}
        require(len(self._scope_map) == len(policy.scopes) and self._scope_map, "ambiguous external native subjects")
        self.qualify()
        with directory(self.path, create=True) as fd:
            require(os.fstat(fd).st_mode & 0o077 == 0, "controller directory must be private")
            self._lock = os.open(".controller-lock", os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600, dir_fd=fd)
            try:
                fcntl.flock(self._lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except OSError as exc:
                os.close(self._lock)
                raise Refusal("single-writer-controller-already-active") from exc
        try:
            self._initialize_database(checkpoint)
        except BaseException:
            self.close()
            raise

    def _initialize_database(self, checkpoint):
        policy, now = self.policy, self.now
        database = self.path / "controller.sqlite3"
        if database.exists() or database.is_symlink():
            read_file(database, 64 * 1024 * 1024)
        self.db = sqlite3.connect(database, isolation_level=None)
        self.db.execute("PRAGMA journal_mode=DELETE")
        self.db.execute("PRAGMA synchronous=FULL")
        self.db.executescript("""
            CREATE TABLE IF NOT EXISTS meta(key TEXT PRIMARY KEY, value BLOB NOT NULL);
            CREATE TABLE IF NOT EXISTS frames(seq INTEGER PRIMARY KEY, hash TEXT UNIQUE NOT NULL, raw BLOB NOT NULL);
            CREATE TABLE IF NOT EXISTS receipts(hash TEXT PRIMARY KEY, guarantee TEXT, subject TEXT, scope TEXT);
            CREATE TABLE IF NOT EXISTS subjects(key TEXT PRIMARY KEY, descriptor BLOB, binding BLOB, source TEXT);
            CREATE TABLE IF NOT EXISTS suppressions(key TEXT PRIMARY KEY);
            CREATE TABLE IF NOT EXISTS adoptions(operation TEXT PRIMARY KEY, request TEXT, candidate TEXT, record TEXT);
            CREATE TABLE IF NOT EXISTS requests(work TEXT PRIMARY KEY, result TEXT);
            CREATE TABLE IF NOT EXISTS faults(hash TEXT PRIMARY KEY, raw BLOB);
            CREATE TABLE IF NOT EXISTS assessments(hash TEXT PRIMARY KEY);
            CREATE TABLE IF NOT EXISTS composites(hash TEXT PRIMARY KEY, composite_id TEXT UNIQUE NOT NULL);
        """)
        binding = self._policy_value(policy)
        old = self._get("policy")
        if old is None:
            with self.transaction():
                self._put("policy", binding)
                self._put("sequence", 0)
                self._put("attempts", 0)
                self._put("root", None)
                self._put("adoption_head", None)
                self._put("routing_head", None)
                self._put("no_progress", 0)
                self._put("last_source", None)
                self._put("total_octets", 0)
                self._put("terminal_stop", None)
                self._put("clock_floor", now)
                self._put("contracts", [])
        else:
            require(old == binding, "external-policy/configuration-substitution")
            require(now >= self._get("clock_floor"), "controller-clock-rollback")
        self.verify_history()
        if checkpoint is not None:
            self.check_checkpoint(checkpoint)

    def close(self):
        if getattr(self, "db", None) is not None:
            self.db.close()
            self.db = None
        if getattr(self, "_lock", None) is not None:
            os.close(self._lock)
            self._lock = None

    def subject_key(self, subject):
        return self.core.particle(subject)["hash"]

    def _policy_value(self, policy):
        return {
            "instance_rappid": policy.instance_rappid, "world_id": policy.world_id,
            "spec_id": PROFILE, "spec_sha256": policy.spec_sha256, "runtime_sha256": policy.runtime_sha256,
            "rights": sorted(policy.rights), "sequence": policy.sequence, "expires_utc": policy.expires_utc,
            "audience": list(policy.audience),
            "scopes": [{"subject": s.subject(), "path": s.path} for s in policy.scopes],
            "max_attempts": policy.max_attempts, "max_depth": policy.max_depth, "max_frames": policy.max_frames,
            "max_total_octets": policy.max_total_octets,
        }

    def qualify(self):
        require(self.policy.spec_sha256 == sha(read_file(ROOT / "SPEC.md")), "wrong-validator-or-spec-pin")
        raw = read_file(ROOT / "manifest.json")
        require(sha(raw) == self.policy.runtime_sha256 and raw == encode(manifest()), "runtime-qualification-required")
        evaluator = read_file(ROOT / "reference/total_eval.py")
        entry = next(p for p in json.loads(raw)["reference"] if p["path"] == "reference/total_eval.py")
        return EvaluatorImage(evaluator, entry["sha256"])

    def restrictions(self):
        return {"rights": {name: name in self.policy.rights for name in RIGHTS},
                "privacy": "godd", "hashes_sensitive": True,
                "deletion": "no-guaranteed-recall", "retention": "append-only-local",
                "audience": list(self.policy.audience)}

    def propagate(self, restrictions):
        values = [self.restrictions(), *restrictions]
        rights = {name: all(r["rights"][name] for r in values) for name in RIGHTS}
        audience = sorted(set.intersection(*(set(r["audience"]) for r in values)))
        require(audience, "restriction-audience-intersection-empty")
        return {**self.restrictions(), "rights": rights, "audience": audience}

    def guard(self, subject, action, inherited=None):
        require(action not in DISABLED, "disabled-workspace1-core:" + action)
        require(self.core.r.utc_valid(self.now) and self.core.r.utc_valid(self.policy.expires_utc),
                "trusted-clock-domain-required")
        require(self.now < self.policy.expires_utc, "current-authorization-expired")
        require(action in self.policy.rights, "external-capability-denied:" + action)
        require(self.subject_key(subject) in self._scope_map, "outside-explicit-observation-scope")
        if inherited is not None:
            require(inherited["rights"].get(action) is True, "inherited-restriction-denied:" + action)
            require(set(self.policy.audience) & set(inherited["audience"]), "inherited-audience-denied")
        if getattr(self, "db", None) is not None:
            floor = self._get("clock_floor")
            require(self.now >= floor, "controller-clock-rollback")
            require(not self.db.execute("SELECT 1 FROM faults LIMIT 1").fetchone(), "fork-latched")
            require(self._get("policy") == self._policy_value(self.policy), "stale-external-policy")
            if self.now > floor:
                self._put("clock_floor", self.now)

    @contextmanager
    def transaction(self):
        self.db.execute("BEGIN IMMEDIATE")
        try:
            yield
            self.db.execute("COMMIT")
        except BaseException:
            self.db.execute("ROLLBACK")
            raise

    def _get(self, key):
        row = self.db.execute("SELECT value FROM meta WHERE key=?", (key,)).fetchone()
        return self.core.parse(row[0]) if row else None

    def _put(self, key, value):
        self.db.execute("INSERT OR REPLACE INTO meta VALUES (?,?)", (key, self.core.octets(value)))

    def _payload(self, name, native_subject, restrictions=None, **fields):
        return {"schema": PROFILE + "/" + name, "instance_rappid": self.policy.instance_rappid,
                "world_id": self.policy.world_id, "native_subject": native_subject,
                "restrictions": restrictions or self.restrictions(), **fields}

    def _head(self):
        row = self.db.execute("SELECT raw FROM frames ORDER BY seq DESC LIMIT 1").fetchone()
        return self.core.parse(row[0]) if row else None

    def _emit(self, payload, *, stop=False):
        self.core.schemas.validate(payload)
        require("retention" in self.policy.rights and payload["restrictions"]["rights"]["retention"],
                "retention-denied-before-persistence")
        head = self._head()
        number = 0 if head is None else head["seq"] + 1
        require(number < self.policy.max_frames - (0 if stop else 1), "root-budget-reserved-stop-capacity")
        frame = self.core.r.build_frame("body.pulse", self.policy.instance_rappid, number, self.now,
                                        payload, head["payload_hash"] if head else None)
        ok, step, why = self.core.r.verify_frame(frame, head=head, stream_id_of_record=self.policy.instance_rappid)
        require(ok, f"RAPP/1 refusal {step}: {why}")
        self.db.execute("INSERT INTO frames VALUES (?,?,?)",
                        (number, frame["frame_hash"], self.core.octets(frame)))
        self._put("sequence", self._get("sequence") + 1)
        return wave(frame)

    def emit(self, payload):
        with self.transaction():
            return self._emit(payload)

    def frame(self, ref):
        row = self.db.execute("SELECT raw FROM frames WHERE hash=?", (address(ref),)).fetchone()
        require(row is not None, "missing-frame")
        value = self.core.parse(row[0])
        require(value["frame_hash"] == address(ref), "frame-address-substitution")
        previous = self.db.execute("SELECT raw FROM frames WHERE seq=?", (value["seq"] - 1,)).fetchone()
        ok, step, reason = self.core.r.verify_frame(
            value, head=self.core.parse(previous[0]) if previous else None,
            stream_id_of_record=self.policy.instance_rappid)
        require(ok, f"retained-frame-tamper:{step}:{reason}")
        return value

    def body(self, ref):
        return self.frame(ref)["payload"]

    def seed(self, subject):
        require(self._get("root") is None, "mint-once-seed")
        self.guard(subject, "retention")
        with self.transaction():
            ref = self._emit(self._payload("seed", subject, generation="workspace1-core",
                spec_sha256=self.policy.spec_sha256, immutable_invariants=True,
                effect_authority="external-controller-only"))
            self._put("root", ref)
        return ref

    def _receipt(self, guarantee, subject_frame, status, scope, method, evidence, subject, restrictions):
        require(guarantee in GUARANTEES, "unknown guarantee")
        payload = self._payload(guarantee + "-receipt", subject, restrictions, guarantee=guarantee,
            subject=subject_frame, status=status, scope=scope, method=method, validator_spec=PROFILE,
            validator_pin=self.policy.spec_sha256, runtime_sha256=self.policy.runtime_sha256,
            evidence=self.core.particle(evidence), authorizes_other_guarantees=False)
        reference = self._emit(payload)
        self.db.execute("INSERT INTO receipts VALUES (?,?,?,?)",
                        (address(reference), guarantee, address(subject_frame), scope))
        return reference

    def verify_receipt(self, reference, guarantee, subject_frame, *, scope=None, current=False):
        p = self.body(reference)
        require(p.get("schema") == PROFILE + "/" + guarantee + "-receipt"
                and p.get("guarantee") == guarantee, "wrong-validator-or-guarantee")
        require(p["validator_pin"] == self.policy.spec_sha256 and p["validator_spec"] == PROFILE, "wrong-receipt-pin")
        row = self.db.execute("SELECT guarantee,subject,scope FROM receipts WHERE hash=?",
                              (address(reference),)).fetchone()
        require(row is not None and row[0] == guarantee and row[1] == address(subject_frame),
                "data-shaped-receipt-has-no-controller-authority")
        require(p["subject"] == subject_frame and p["status"] == "verified", "guarantee-not-verified")
        require(scope is None or p["scope"] == scope, "receipt-coverage-scope-mismatch")
        if current:
            require(guarantee != "current_authorization", "fresh-authorization-requires-external-controller-query")
            self.guard(p["native_subject"], "adoption", p["restrictions"])
            require(p["runtime_sha256"] == self.policy.runtime_sha256, "stale-receipt-runtime")
        return p

    def capture_octets(self, subject, octets, *, inherited=(), consistency="supplied-immutable-octets"):
        # These guards precede even inspecting an untrusted input object's type or iterator.
        self.guard(subject, "capture")
        self.guard(subject, "retention")
        restrictions = self.propagate(inherited)
        self.guard(subject, "capture", restrictions)
        self.guard(subject, "retention", restrictions)
        require(self._get("root") is not None, "seed required before observation")
        head = self._head()
        require(head["seq"] + 5 < self.policy.max_frames, "capture-frame-budget-before-access")
        require(type(octets) is bytes and len(octets) <= MAX_OCTETS, "finite-bounded-octets-required")
        require(self._get("total_octets") + len(octets) <= self.policy.max_total_octets, "root-owned-byte-budget")
        content = self.core.particle({"octets_b64": b64(octets)})
        binding = self.core.particle({"subject": subject, "content": content, "consistency": consistency})
        with self.transaction():
            self._put("total_octets", self._get("total_octets") + len(octets))
            source = self._emit(self._payload(
                "observation", subject, restrictions, content=content, octets_b64=b64(octets),
                octets_sha256=sha(octets), octets_count=len(octets), subject_binding=binding,
                consistency=consistency, scope="captured-octets-only", complete=True, native_rebinding=False))
            self.db.execute("INSERT OR REPLACE INTO subjects VALUES (?,?,?,?)",
                (self.subject_key(subject), self.core.octets(subject), self.core.octets(binding), address(source)))
            integrity = self._receipt("rapp_integrity", source, "verified", "RAPP/1-eleven-key-frame",
                "canonical-parent-verifier", {"frame": source}, subject, restrictions)
            observation = self._receipt("observation", source, "verified", "captured-octets-only",
                consistency, {"binding": binding, "bytes": len(octets)}, subject, restrictions)
            deployment = self._receipt("safe_deployment", source, "refused", "external-effects",
                "unproved-deployment-disabled", {"reason": "Workspace/1 core-external-effects-disabled"}, subject, restrictions)
        return {"source": source, "rapp_integrity": integrity, "observation": observation, "safe_deployment": deployment}

    def capture_file(self, subject, path):
        self.guard(subject, "capture")
        self.guard(subject, "retention")
        scope = self._scope_map[self.subject_key(subject)]
        head = self._head()
        require(head is not None and head["seq"] + 5 < self.policy.max_frames,
                "capture-frame-budget-before-access")
        require(scope.path is not None and Path(path).absolute() == Path(scope.path).absolute(),
                "outside-exact-file-scope")
        # Directory/coherent-live observation is deliberately not inferred from stable file reads.
        remaining = self.policy.max_total_octets - self._get("total_octets")
        require(remaining > 0, "root-owned-byte-budget-before-access")
        raw = read_file(path, min(MAX_OCTETS, remaining))
        return self.capture_octets(subject, raw, consistency="stable-descriptor-not-coherent")

    def _observation_octets(self, reference, expected_subject):
        source = self.body(reference)
        require(source["schema"] == PROFILE + "/observation",
                "catalog-or-tree-source-must-be-observation")
        require(source["native_subject"] == expected_subject
                and source["world_id"] == self.policy.world_id
                and source["instance_rappid"] == self.policy.instance_rappid,
                "catalog-source-subject-or-world-substitution")
        self.guard(expected_subject, "local_synthesis", source["restrictions"])
        self.guard(expected_subject, "retention", source["restrictions"])
        return source, self._decode_source(source)

    def register_catalog_shard(self, subject, source):
        self.guard(subject, "local_synthesis")
        self.guard(subject, "retention")
        observed, raw = self._observation_octets(source, subject)
        document = catalog_document(self.core, raw)
        restrictions = self.propagate([observed["restrictions"]])
        with self.transaction():
            return self._emit(self._payload(
                "catalog-shard", subject, restrictions, source=source,
                catalog_id=document["catalog_id"], root_id=document["root_id"],
                shard_index=document["shard_index"], shard_count=document["shard_count"],
                snapshot_sha256=document["snapshot_sha256"],
                branch_scope=document["branch_scope"],
                branch_evidence_status=document["branch_evidence_status"],
                recursive=document["recursive"],
                entry_ids=[entry["id"] for entry in document["entries"]],
                entry_count=len(document["entries"]), source_sha256=sha(raw),
                grants_authority=False))

    def _catalog_entries(self, expected_subject, shard_references):
        require(type(shard_references) is list and 1 <= len(shard_references) <= 32,
                "catalog-shard-reference-bound")
        addresses = [address(reference) for reference in shard_references]
        require(len(addresses) == len(set(addresses)), "catalog-shard-reference-bound")
        documents, restrictions = [], []
        catalog_id, root_id, shard_count = None, None, None
        snapshot_sha256, branch_scope, branch_evidence_status, recursive = None, None, None, None
        entries = {}
        indexes = set()
        for reference in shard_references:
            shard = self.body(reference)
            require(shard["schema"] == PROFILE + "/catalog-shard",
                    "catalog-shard-record-required")
            require(shard["native_subject"] == expected_subject
                    and shard["world_id"] == self.policy.world_id
                    and shard["instance_rappid"] == self.policy.instance_rappid,
                    "catalog-shard-subject-or-world-substitution")
            observed, raw = self._observation_octets(shard["source"], expected_subject)
            document = catalog_document(self.core, raw)
            require(shard["native_subject"] == observed["native_subject"]
                    and shard["catalog_id"] == document["catalog_id"]
                    and shard["root_id"] == document["root_id"]
                    and shard["shard_index"] == document["shard_index"]
                    and shard["shard_count"] == document["shard_count"]
                    and shard["snapshot_sha256"] == document["snapshot_sha256"]
                    and shard["branch_scope"] == document["branch_scope"]
                    and shard["branch_evidence_status"] == document["branch_evidence_status"]
                    and shard["recursive"] == document["recursive"]
                    and shard["entry_ids"] == [entry["id"] for entry in document["entries"]]
                    and shard["entry_count"] == len(document["entries"])
                    and shard["source_sha256"] == sha(raw),
                    "catalog-shard-substitution")
            maximum = self.propagate([observed["restrictions"]])
            require(all(not shard["restrictions"]["rights"][right] or maximum["rights"][right]
                        for right in RIGHTS)
                    and set(shard["restrictions"]["audience"]) <= set(maximum["audience"]),
                    "catalog-shard-restrictions-widened")
            if catalog_id is None:
                catalog_id, root_id, shard_count, snapshot_sha256, branch_scope, branch_evidence_status, recursive = (
                    document["catalog_id"], document["root_id"], document["shard_count"],
                    document["snapshot_sha256"], document["branch_scope"],
                    document["branch_evidence_status"], document["recursive"],
                )
            require((document["catalog_id"], document["root_id"], document["shard_count"],
                     document["snapshot_sha256"], document["branch_scope"],
                     document["branch_evidence_status"], document["recursive"])
                    == (catalog_id, root_id, shard_count, snapshot_sha256, branch_scope,
                        branch_evidence_status, recursive),
                    "catalog-shard-family-mismatch")
            require(document["shard_index"] not in indexes, "duplicate-catalog-shard-index")
            indexes.add(document["shard_index"])
            for entry in document["entries"]:
                require(entry["id"] not in entries, "duplicate-catalog-entry-across-shards")
                entries[entry["id"]] = entry
            documents.append(document)
            restrictions.append(shard["restrictions"])
        require(len(documents) == shard_count and indexes == set(range(shard_count)),
                "incomplete-catalog-shards")
        snapshot = [
            {
                "id": entry["id"], "kind": entry["kind"], "parent": entry["parent"],
                "labels": entry["labels"], "metadata_sha256": entry["metadata_sha256"],
                "share_class": entry["share_class"],
            }
            for entry in sorted(entries.values(), key=lambda item: item["id"])
        ]
        require(_canonical_sha256(snapshot) == snapshot_sha256,
                "catalog-snapshot-commitment-mismatch")
        for entry_id, entry in entries.items():
            parent = entry["parent"]
            require(parent is None or parent == root_id or parent in entries,
                    "catalog-parent-outside-complete-shards")
            visited, current, depth = set(), entry_id, 0
            while entries[current]["parent"] in entries:
                require(current not in visited, "catalog-parent-cycle")
                visited.add(current)
                current = entries[current]["parent"]
                depth += 1
                require(depth <= 128, "catalog-recursion-depth-bound")
            if not recursive:
                require(entry["parent"] in (None, root_id),
                        "nonrecursive-catalog-has-descendants")
        return catalog_id, root_id, snapshot_sha256, entries, restrictions

    def assess_organization(self, subject, catalog_shards, tree_source, *,
                            max_bucket, allowed_depth, refinement_round=0,
                            previous=None):
        self.guard(subject, "local_synthesis")
        self.guard(subject, "retention")
        require(type(max_bucket) is int and 1 <= max_bucket <= 10000
                and type(allowed_depth) is int and 1 <= allowed_depth <= 32
                and type(refinement_round) is int and 0 <= refinement_round <= 32,
                "organization-quality-bound")
        require((previous is None) == (refinement_round == 0),
                "organization-refinement-round-parent-mismatch")
        catalog_id, _, snapshot_sha256, entries, inherited = self._catalog_entries(
            subject, catalog_shards)
        tree_sources = tree_source if type(tree_source) is list else [tree_source]
        require(1 <= len(tree_sources) <= 32
                and len({address(reference) for reference in tree_sources}) == len(tree_sources),
                "organization-tree-source-bound")
        tree_restrictions, tree_raws = [], []
        for reference in tree_sources:
            tree, raw = self._observation_octets(reference, subject)
            tree_restrictions.append(tree["restrictions"])
            tree_raws.append(raw)
        document, groups, depths = organization_documents(self.core, tree_raws)
        require(document["catalog_id"] == catalog_id, "organization-catalog-substitution")
        seen, valid, duplicate_assignments, unknown_assignments = set(), set(), 0, 0
        buckets = {group_id: 0 for group_id in groups}
        for assignment in document["assignments"]:
            entry_id, group_id = assignment["entry_id"], assignment["group_id"]
            if entry_id in seen:
                duplicate_assignments += 1
            seen.add(entry_id)
            if entry_id not in entries or group_id not in groups:
                unknown_assignments += 1
                continue
            valid.add(entry_id)
            buckets[group_id] += 1
        unassigned = len(set(entries) - valid)
        largest_bucket = max(buckets.values(), default=0)
        max_depth = max(depths.values(), default=0)
        quality = (unassigned + duplicate_assignments + unknown_assignments,
                   max(0, largest_bucket - max_bucket),
                   max(0, max_depth - allowed_depth))
        status = "verified" if quality == (0, 0, 0) else "needs-refinement"
        progress = True
        prior_restrictions = []
        if previous is not None:
            prior = self.body(previous)
            require(prior["schema"] == PROFILE + "/organization-assessment"
                    and prior["native_subject"] == subject
                    and self.db.execute(
                        "SELECT 1 FROM assessments WHERE hash=?", (address(previous),)
                    ).fetchone()
                    and prior["catalog_id"] == catalog_id
                    and prior["snapshot_sha256"] == snapshot_sha256
                    and prior["catalog_shards"] == catalog_shards
                    and prior["status"] == "needs-refinement"
                    and prior["max_bucket"] == max_bucket
                    and prior["allowed_depth"] == allowed_depth
                    and refinement_round == prior["refinement_round"] + 1,
                    "invalid-organization-refinement-parent")
            self.guard(subject, "local_synthesis", prior["restrictions"])
            self.guard(subject, "retention", prior["restrictions"])
            prior_restrictions.append(prior["restrictions"])
            prior_quality = (
                prior["unassigned"] + prior["duplicate_assignments"] + prior["unknown_assignments"],
                max(0, prior["largest_bucket"] - max_bucket),
                max(0, prior["max_depth"] - allowed_depth),
            )
            progress = quality < prior_quality
            if status != "verified" and not progress:
                status = "no-progress"
        restrictions = self.propagate([*tree_restrictions, *inherited, *prior_restrictions])
        with self.transaction():
            assessment = self._emit(self._payload(
                "organization-assessment", subject, restrictions,
                tree_sources=tree_sources, catalog_shards=catalog_shards,
                catalog_id=catalog_id, snapshot_sha256=snapshot_sha256,
                tree_id=document["tree_id"],
                tree_snapshot_sha256=document["snapshot_sha256"],
                root_group=document["root_group"],
                entry_count=len(entries), assigned_count=len(valid),
                group_count=len(groups), max_depth=max_depth,
                largest_bucket=largest_bucket, max_bucket=max_bucket,
                allowed_depth=allowed_depth, unassigned=unassigned,
                duplicate_assignments=duplicate_assignments,
                unknown_assignments=unknown_assignments,
                refinement_round=refinement_round, previous=previous,
                status=status, progress=progress, grants_authority=False))
            self.db.execute("INSERT INTO assessments VALUES (?)", (address(assessment),))
            return assessment

    def candidate_outcome(self, subject, assessment, query, selected_ids):
        self.guard(subject, "local_synthesis")
        self.guard(subject, "retention")
        _bounded_text(query, 1024, "invalid-outcome-query")
        require(type(selected_ids) is list and len(selected_ids) <= 1024
                and all(type(value) is str for value in selected_ids),
                "invalid-outcome-selection")
        for value in selected_ids:
            _bounded_text(value, 512, "invalid-outcome-selection")
        require(len(selected_ids) == len(set(selected_ids)), "invalid-outcome-selection")
        evaluated = self.body(assessment)
        require(evaluated["schema"] == PROFILE + "/organization-assessment"
                and evaluated["native_subject"] == subject
                and self.db.execute(
                    "SELECT 1 FROM assessments WHERE hash=?", (address(assessment),)
                ).fetchone()
                and evaluated["status"] == "verified",
                "outcome-requires-verified-organization")
        _, _, snapshot_sha256, entries, inherited = self._catalog_entries(
            subject, evaluated["catalog_shards"])
        require(evaluated["snapshot_sha256"] == snapshot_sha256,
                "outcome-catalog-snapshot-substitution")
        require(set(selected_ids) <= set(entries), "outcome-selection-outside-catalog")
        restrictions = self.propagate([evaluated["restrictions"], *inherited])
        with self.transaction():
            return self._emit(self._payload(
                "outcome-resolution", subject, restrictions, assessment=assessment,
                query_sha256=sha(query.encode("utf-8")), selected_ids=selected_ids,
                status="candidate" if selected_ids else "unresolved",
                semantic_fidelity="unproven", grants_authority=False))

    def propose_subscription(self, subject, assessment, selected_ids, *,
                             approved_private_ids=()):
        self.guard(subject, "local_synthesis")
        self.guard(subject, "retention")
        require(type(selected_ids) is list and len(selected_ids) <= 1024
                and all(type(value) is str for value in selected_ids),
                "invalid-subscription-selection")
        for value in selected_ids:
            _bounded_text(value, 512, "invalid-subscription-selection")
        require(len(selected_ids) == len(set(selected_ids)),
                "invalid-subscription-selection")
        require(isinstance(approved_private_ids, (list, tuple))
                and all(type(value) is str for value in approved_private_ids),
                "invalid-private-subscription-approval")
        approved_values = list(approved_private_ids)
        approved = set(approved_values)
        require(len(approved) == len(approved_values) <= 1024
                and approved <= set(selected_ids),
                "invalid-private-subscription-approval")
        evaluated = self.body(assessment)
        require(evaluated["schema"] == PROFILE + "/organization-assessment"
                and evaluated["native_subject"] == subject
                and self.db.execute(
                    "SELECT 1 FROM assessments WHERE hash=?", (address(assessment),)
                ).fetchone()
                and evaluated["status"] == "verified",
                "subscription-requires-verified-organization")
        _, _, snapshot_sha256, entries, inherited = self._catalog_entries(
            subject, evaluated["catalog_shards"])
        require(evaluated["snapshot_sha256"] == snapshot_sha256,
                "subscription-catalog-snapshot-substitution")
        require(set(selected_ids) <= set(entries), "subscription-selection-outside-catalog")
        require(approved <= {
            entry_id for entry_id, entry in entries.items()
            if entry["share_class"] == "private-source"
        }, "private-approval-must-name-private-source")
        allowed, withheld_private, withheld_excluded, approved_count = [], 0, 0, 0
        for entry_id in selected_ids:
            share_class = entries[entry_id]["share_class"]
            if share_class == "public-source":
                allowed.append(entry_id)
            elif share_class == "private-source" and entry_id in approved:
                allowed.append(entry_id)
                approved_count += 1
            elif share_class == "private-source":
                withheld_private += 1
            else:
                withheld_excluded += 1
        restrictions = self.propagate([evaluated["restrictions"], *inherited])
        with self.transaction():
            return self._emit(self._payload(
                "subscription-proposal", subject, restrictions,
                assessment=assessment, target="rapp-private-hive",
                selected_ids=allowed, withheld_private=withheld_private,
                withheld_excluded=withheld_excluded,
                externally_approved_private=approved_count,
                external_owner_approval_required=True,
                publication_authorized=False, grants_authority=False))

    def _composite_members(self, subject, reference, active=None):
        active = set() if active is None else active
        key = address(reference)
        require(key not in active, "workspace-composite-cycle")
        active.add(key)
        try:
            composite = self.body(reference)
            require(composite["schema"] == PROFILE + "/workspace-composite"
                    and composite["native_subject"] == subject
                    and composite["world_id"] == self.policy.world_id
                    and composite["instance_rappid"] == self.policy.instance_rappid
                    and self.db.execute(
                        "SELECT 1 FROM composites WHERE hash=?", (key,)
                    ).fetchone(),
                    "workspace-composite-controller-record-required")
            self.guard(subject, "local_synthesis", composite["restrictions"])
            self.guard(subject, "retention", composite["restrictions"])
            members = set(composite["selected_ids"])
            composite_ids = {composite["composite_id"]}
            restrictions = [composite["restrictions"]]
            depth = 0
            for child in composite["child_composites"]:
                child_body, child_members, child_ids, child_restrictions, child_depth = (
                    self._composite_members(subject, child, active)
                )
                require(not members & child_members,
                        "workspace-composite-duplicate-member")
                members.update(child_members)
                composite_ids.update(child_ids)
                restrictions.extend(child_restrictions)
                depth = max(depth, child_depth + 1)
            require(composite["member_count"] == len(members)
                    and composite["members_sha256"] == _canonical_sha256(sorted(members))
                    and composite["depth"] == depth,
                    "workspace-composite-member-substitution")
            return composite, members, composite_ids, restrictions, depth
        finally:
            active.remove(key)

    def compose_workspace(self, subject, assessment, composite_id, selected_ids,
                          child_composites=()):
        self.guard(subject, "local_synthesis")
        self.guard(subject, "retention")
        _bounded_text(composite_id, 128, "invalid-workspace-composite-id")
        require(type(selected_ids) is list and len(selected_ids) <= 1024
                and all(type(value) is str for value in selected_ids),
                "invalid-workspace-composite-selection")
        for value in selected_ids:
            _bounded_text(value, 512, "invalid-workspace-composite-selection")
        require(len(selected_ids) == len(set(selected_ids)),
                "invalid-workspace-composite-selection")
        require(isinstance(child_composites, (list, tuple))
                and len(child_composites) <= 128,
                "invalid-workspace-composite-children")
        child_refs = list(child_composites)
        child_addresses = [address(reference) for reference in child_refs]
        require(len(child_addresses) == len(set(child_addresses)),
                "invalid-workspace-composite-children")
        evaluated = self.body(assessment)
        require(evaluated["schema"] == PROFILE + "/organization-assessment"
                and evaluated["native_subject"] == subject
                and self.db.execute(
                    "SELECT 1 FROM assessments WHERE hash=?", (address(assessment),)
                ).fetchone()
                and evaluated["status"] == "verified",
                "workspace-composite-requires-verified-organization")
        _, _, snapshot_sha256, entries, inherited = self._catalog_entries(
            subject, evaluated["catalog_shards"])
        require(evaluated["snapshot_sha256"] == snapshot_sha256
                and set(selected_ids) <= set(entries)
                and all("workspace" in entries[entry_id]["labels"]
                        for entry_id in selected_ids),
                "workspace-composite-selection-outside-catalog")
        selected = sorted(selected_ids)
        children = [
            reference for _, reference in sorted(zip(child_addresses, child_refs))
        ]
        members = set(selected)
        composite_ids = set()
        child_restrictions = []
        depth = 0
        for child in children:
            child_body, child_members, child_ids, restrictions, child_depth = (
                self._composite_members(subject, child)
            )
            require(composite_id not in child_ids, "workspace-composite-cycle")
            require(not members & child_members,
                    "workspace-composite-duplicate-member")
            members.update(child_members)
            composite_ids.update(child_ids)
            child_restrictions.extend(restrictions)
            depth = max(depth, child_depth + 1)
        require(composite_id not in composite_ids and members,
                "workspace-composite-empty-or-cycle")
        require(len(members) <= 10000 and depth <= 32,
                "workspace-composite-bound")
        restrictions = self.propagate([
            evaluated["restrictions"], *inherited, *child_restrictions,
        ])
        with self.transaction():
            existing = self.db.execute(
                "SELECT hash FROM composites WHERE composite_id=?", (composite_id,)
            ).fetchone()
            if existing:
                reference = {"space": "rapp/1:wave", "hash": existing[0]}
                prior = self.body(reference)
                require(prior["assessment"] == assessment
                        and prior["selected_ids"] == selected
                        and prior["child_composites"] == children,
                        "workspace-composite-idempotency-conflict")
                return reference
            composite = self._emit(self._payload(
                "workspace-composite", subject, restrictions,
                assessment=assessment, composite_id=composite_id,
                selected_ids=selected, child_composites=children,
                member_count=len(members),
                members_sha256=_canonical_sha256(sorted(members)),
                depth=depth, recursive=True, routing_only=True,
                child_identities_preserved=True, child_worlds_preserved=True,
                content_copied=False, grants_authority=False))
            self.db.execute(
                "INSERT INTO composites VALUES (?,?)",
                (address(composite), composite_id),
            )
            return composite

    def synthesize(self, subject, source, operation="identity-octets", field=""):
        self.guard(subject, "local_synthesis")
        self.guard(subject, "retention")
        original = self.body(source)
        require(original["native_subject"] == subject, "native-subject-substitution")
        self.guard(subject, "local_synthesis", original["restrictions"])
        require(operation in ("identity-octets", "json-field"), "effect-or-unknown-operation-disabled")
        raw = unb64(original["octets_b64"])
        read = {"kind": "content", "selector": "captured-octets", "expected": sha(raw)}
        return self.emit(self._payload(
            "lens-request", subject, original["restrictions"], source=source, operation=operation,
            field=field, runtime_sha256=self.policy.runtime_sha256, synthesis_reads=[read],
            necessary_reads=[read], grants_authority=False))

    def _read_source_meta(self, subject, lens):
        p = self.body(lens)
        require(p["schema"] == PROFILE + "/lens-request" and p["native_subject"] == subject, "lens subject/schema mismatch")
        source = self.body(p["source"])
        require(source["native_subject"] == subject and source["world_id"] == self.policy.world_id,
                "source subject/world substitution")
        return p, source

    def _decode_source(self, source):
        raw = unb64(source["octets_b64"])
        require(sha(raw) == source["octets_sha256"] and len(raw) == source["octets_count"], "source-byte-substitution")
        return raw

    def _read_source(self, subject, lens):
        p, source = self._read_source_meta(subject, lens)
        raw = self._decode_source(source)
        return p, source, raw

    def verify_derivation(self, reference):
        p = self.body(reference)
        require(p["schema"] == PROFILE + "/derivation", "derivation required")
        lens_meta, source = self._read_source_meta(p["native_subject"], p["lens"])
        require(lens_meta["runtime_sha256"] == self.policy.runtime_sha256, "lens-runtime-pin-mismatch")
        raw = self._decode_source(source)
        lens = lens_meta
        require(p["sources"] == [lens["source"]], "derivation ancestry substitution")
        maximum = self.propagate([source["restrictions"], lens["restrictions"]])
        require(all(not p["restrictions"]["rights"][r] or maximum["rights"][r] for r in RIGHTS)
                and set(p["restrictions"]["audience"]) <= set(maximum["audience"]),
                "derivation restrictions widened")
        actual = [{"kind": "content", "selector": "captured-octets", "expected": sha(raw)}]
        require(p["actual_reads"] == p["necessary_reads"] == p["synthesis_reads"] == actual
                and p["environment"] == [], "derivation read coverage substitution")
        require(p["runtime_sha256"] == self.policy.runtime_sha256, "fresh derivation qualification required")
        require(sha(unb64(p["result_b64"])) == p["result_sha256"], "derivation result substitution")
        return p, lens, source, raw

    def execute(self, subject, lens, *, depth=0, actual_override=None, environment=()):
        self.guard(subject, "local_synthesis")
        self.guard(subject, "retention")
        require(not environment, "ambient-environment-disabled")
        if self._get("terminal_stop") is not None:
            return {"kind": "stopped", "frame": self._get("terminal_stop"), "reason": "durable-root-stop"}
        image = self.qualify()
        p, source = self._read_source_meta(subject, lens)
        require(p["runtime_sha256"] == self.policy.runtime_sha256, "lens-runtime-pin-mismatch")
        restrictions = self.propagate([p["restrictions"], source["restrictions"]])
        self.guard(subject, "local_synthesis", restrictions)
        raw = self._decode_source(source)
        work = self.core.particle({"operation": p["operation"], "field": p["field"],
                                  "source": source["content"], "runtime": self.policy.runtime_sha256,
                                  "subject": subject})
        with self.transaction():
            attempts = self._get("attempts")
            require(type(depth) is int and depth >= 0, "invalid root-owned depth")
            head = self._head()
            remaining = self.policy.max_frames - (head["seq"] + 1 if head else 0)
            if remaining <= 3:
                return self._stop(subject, work, "root-frame-budget", depth, restrictions, [lens])
            if attempts >= self.policy.max_attempts or depth > self.policy.max_depth:
                return self._stop(subject, work, "attempt-or-depth-budget", depth, restrictions, [lens])
            self._put("attempts", attempts + 1)
            duplicate = self.db.execute("SELECT result FROM requests WHERE work=?", (work["hash"],)).fetchone()
            if duplicate:
                return self._stop(subject, work, "repeated-state-fixed-point", depth, restrictions, [lens])
            source_key = source["content"]["hash"]
            no_progress = self._get("no_progress") + 1 if source_key == self._get("last_source") else 0
            self._put("no_progress", no_progress)
            self._put("last_source", source_key)
            if no_progress >= 2:
                return self._stop(subject, work, "no-progress-or-oscillation", depth, restrictions, [lens])
            actual = [{"kind": "content", "selector": "captured-octets", "expected": sha(raw)}]
            require(actual_override is None or actual_override == actual, "actual-read-trace-forgery")
            require(p["necessary_reads"] == actual and p["synthesis_reads"] == actual, "read-coverage-incomplete")
            try:
                parsed = raw
                enumerations, negative = [], []
                if p["operation"] == "json-field":
                    parsed = self.core.r._strict_json(raw)
                    domain(parsed)
                    require(type(parsed) is dict and len(parsed) <= 128, "bounded-structured-document-required")
                    enumerations = [{"kind": "enumeration", "selector": "top-level-keys",
                                     "expected": self.core.particle(sorted(parsed))["hash"]}]
                    if p["field"] not in parsed:
                        negative = [{"kind": "negative", "selector": p["field"],
                                     "expected": self.core.particle({"absent": p["field"]})["hash"]}]
                value = image.evaluate(p["operation"], parsed, p["field"])
                result = value if type(value) is bytes else self.core.octets(value)
                require(len(result) <= MAX_OCTETS, "result byte budget")
            except (ValueError, TypeError, UnicodeError, RecursionError) as exc:
                refusal = self._emit(self._payload(
                    "refusal", subject, restrictions, parents=[lens, p["source"]],
                    operation=p["operation"], code="interpretation-refused", safe_to_retry=False,
                    grants_authority=False))
                fidelity = self._receipt("semantic_fidelity", refusal, "refused", "interpretation",
                    "strict-domain-or-mapping-refusal", {"operation": p["operation"], "negative_reads": negative},
                    subject, restrictions)
                self.db.execute("INSERT INTO requests VALUES (?,?)", (work["hash"], address(refusal)))
                return {"kind": "refused", "frame": refusal, "reason": "interpretation-refused",
                        "negative_reads": negative, "semantic_fidelity": fidelity}
            derived = self._emit(self._payload(
                "derivation", subject, restrictions, sources=[p["source"]], lens=lens, result_b64=b64(result),
                result_sha256=sha(result), runtime_sha256=self.policy.runtime_sha256,
                actual_reads=actual, necessary_reads=actual, synthesis_reads=p["synthesis_reads"],
                negative_reads=negative, enumerations=enumerations, environment=[], portable=True, native_rebinding=False))
            integrity = self._receipt("rapp_integrity", derived, "verified", "RAPP/1-eleven-key-frame",
                "canonical-parent-verifier", {"frame": derived}, subject, restrictions)
            fidelity = self._receipt("semantic_fidelity", derived, "unproven", "replay-is-not-fidelity",
                "mapping-contract-not-yet-verified", {"result": sha(result)}, subject, restrictions)
            self.db.execute("INSERT INTO requests VALUES (?,?)", (work["hash"], address(derived)))
            return {"kind": "candidate", "frame": derived, "rapp_integrity": integrity, "semantic_fidelity": fidelity}

    def authorization_receipt(self, subject, artifact, action):
        """A scoped snapshot of a controller query, never a reusable capability."""
        self.guard(subject, "retention")
        p = self.body(artifact)
        try:
            self.guard(subject, action, p["restrictions"])
            status = "verified"
        except Refusal:
            status = "refused"
        with self.transaction():
            return self._receipt("current_authorization", artifact, status, "action:" + action,
                "external-controller-query-not-a-grant", {"policy": self.core.particle(self._get("policy")),
                                                        "action": action, "now": self.now},
                subject, p["restrictions"])

    def deployment_receipt(self, subject, artifact):
        self.guard(subject, "retention")
        p = self.body(artifact)
        with self.transaction():
            return self._receipt("safe_deployment", artifact, "refused", "external-effects",
                "unqualified-deployment-disabled", {"disabled": True}, subject, p["restrictions"])

    def _stop(self, subject, work, reason, depth, restrictions, parents):
        head = self._head()
        count = 0 if head is None else head["seq"] + 1
        require(count < self.policy.max_frames, "root-budget-exhausted-stop-already-retained")
        ref = self._emit(self._payload(
            "scheduler-exhaust", subject, restrictions, parents=parents, work=work, root=self._get("root"),
            depth=min(depth, 32), attempts=self._get("attempts"), reason=reason, progress=False,
            terminal=True, remaining_frames=max(0, self.policy.max_frames - count - 1), reserved_stop=True), stop=True)
        if reason in ("attempt-or-depth-budget", "root-frame-budget"):
            self._put("terminal_stop", ref)
        return {"kind": "stopped", "frame": ref, "reason": reason}

    def approve_contract(self, contract):
        """Explicit host action. A model/lens cannot call or populate this authority."""
        require(type(contract) is dict and set(contract) == {"operation", "field", "coverage", "inverse"},
                "closed mapping contract required")
        require(contract["operation"] in ("identity-octets", "json-field") and contract["coverage"] in
                ("complete-captured-octets", "selected-field-only"), "unknown fidelity contract")
        commitment = self.core.particle(contract)
        with self.transaction():
            values = self._get("contracts")
            if commitment not in values:
                self._put("contracts", values + [commitment])
                self._put("sequence", self._get("sequence") + 1)
        return commitment

    def fidelity(self, subject, candidate, contract):
        self.guard(subject, "local_synthesis")
        self.guard(subject, "retention")
        pre = self.body(candidate)
        require(pre["schema"] == PROFILE + "/derivation" and pre["native_subject"] == subject,
                "derivation subject/schema mismatch")
        self.guard(subject, "local_synthesis", pre["restrictions"])
        p, lens, source, raw = self.verify_derivation(candidate)
        require(p["native_subject"] == subject, "derivation subject mismatch")
        commitment = self.core.particle(contract)
        require(commitment in self._get("contracts"), "fidelity-contract-not-externally-approved")
        require((contract["operation"], contract["field"]) == (lens["operation"], lens["field"]),
                "wrong correspondence contract")
        output = unb64(p["result_b64"])
        exact = (contract["operation"] == "identity-octets" and contract["coverage"] == "complete-captured-octets"
                 and contract["inverse"] is True and raw == output)
        if contract["operation"] == "json-field":
            value = self.core.r._strict_json(raw)
            domain(value)
            exact = (contract["coverage"] == "selected-field-only" and contract["inverse"] is False
                     and contract["field"] in value and self.core.octets(value[contract["field"]]) == output)
        require(exact, "semantic-fidelity/coverage-not-proven")
        with self.transaction():
            return self._receipt("semantic_fidelity", candidate, "verified", contract["coverage"],
                "independent-coverage-and-inverse-check", {"contract": commitment, "result": sha(output)},
                subject, p["restrictions"])

    def frontier(self):
        subjects = [{"subject": key, "binding": self.core.parse(binding)}
                    for key, binding in self.db.execute("SELECT key,binding FROM subjects ORDER BY key")]
        suppressed = [r[0] for r in self.db.execute("SELECT key FROM suppressions ORDER BY key")]
        head = self._head()
        return {"instance_rappid": self.policy.instance_rappid, "world_id": self.policy.world_id,
                "policy": self.core.particle(self._get("policy")), "graph_head": wave(head) if head else None,
                "adoption_head": self._get("adoption_head"), "routing_head": self._get("routing_head"),
                "suppressions": self.core.particle(suppressed), "source_bindings": self.core.particle(subjects),
                "runtime_sha256": self.policy.runtime_sha256, "sequence": self._get("sequence")}

    def request_adoption(self, subject, candidate, fidelity, contract, operation_id, *, integrity, observation):
        self.guard(subject, "retention")
        p = self.body(candidate)
        restrictions = self.propagate([p["restrictions"]])
        # Request data has no effects; the caller snapshots the complete frontier AFTER this append.
        request = self.emit(self._payload(
            "adoption-request", subject, restrictions, candidate=candidate, fidelity=fidelity,
            integrity=integrity, observation=observation,
            contract=self.core.particle(contract), frontier=self.frontier(), operation_id=operation_id,
            grants_authority=False))
        return request, self.frontier()

    def adopt(self, subject, request_ref, expected_frontier, *, fault=None):
        self.guard(subject, "adoption")
        self.qualify()
        p = self.body(request_ref)
        require(p["schema"] == PROFILE + "/adoption-request" and p["native_subject"] == subject,
                "inert-data-cannot-be-adoption-request")
        self.guard(subject, "adoption", p["restrictions"])
        with self.transaction():
            row = self.db.execute("SELECT request,record FROM adoptions WHERE operation=?", (p["operation_id"],)).fetchone()
            if row:
                require(row[0] == address(request_ref), "idempotency-conflict")
                return {"space": "rapp/1:wave", "hash": row[1]}
            require(self.frontier() == expected_frontier, "complete-frontier-CAS-refused")
            self.verify_history()
            frozen = p["frontier"]
            require(all(frozen[key] == expected_frontier[key] for key in frozen
                        if key not in ("graph_head", "sequence"))
                    and expected_frontier["graph_head"] == request_ref
                    and expected_frontier["sequence"] == frozen["sequence"] + 1,
                    "adoption-request-frontier-substitution")
            require(not self.db.execute("SELECT 1 FROM suppressions WHERE key=?", (self.subject_key(subject),)).fetchone(),
                    "stable-subject-suppression")
            candidate, _, source, _ = self.verify_derivation(p["candidate"])
            require(candidate["native_subject"] == subject and candidate["world_id"] == self.policy.world_id,
                    "subject/world replacement")
            binding = self.db.execute("SELECT binding,source FROM subjects WHERE key=?", (self.subject_key(subject),)).fetchone()
            require(binding and binding[1] == address(candidate["sources"][0])
                    and self.core.parse(binding[0]) == source["subject_binding"], "stale-source-binding")
            require(source["consistency"] == "supplied-immutable-octets", "native-coherent-rebinding-unproven-disabled")
            require(p["contract"] in self._get("contracts"), "contract authority missing")
            self.verify_receipt(p["integrity"], "rapp_integrity", p["candidate"],
                                scope="RAPP/1-eleven-key-frame")
            self.verify_receipt(p["observation"], "observation", candidate["sources"][0],
                                scope="captured-octets-only")
            fidelity = self.verify_receipt(p["fidelity"], "semantic_fidelity", p["candidate"],
                                           scope="complete-captured-octets", current=True)
            require(fidelity["evidence"] == self.core.particle(
                {"contract": p["contract"], "result": candidate["result_sha256"]}),
                "fidelity contract/evidence substitution")
            authorization = self._receipt("current_authorization", p["candidate"], "verified",
                "local-inert-captured-view-only", "external-controller-frontier-CAS",
                expected_frontier, subject, candidate["restrictions"])
            adopted = self._emit(self._payload(
                "adoption-record", subject, candidate["restrictions"], request=request_ref, candidate=p["candidate"],
                operation_id=p["operation_id"], controller_epoch=self.policy.sequence, frontier=expected_frontier,
                data_only=True, external_effects=False))
            self.db.execute("INSERT INTO adoptions VALUES (?,?,?,?)",
                (p["operation_id"], address(request_ref), address(p["candidate"]), address(adopted)))
            self._put("adoption_head", adopted)
            if fault:
                fault("before-commit")
        if fault:
            fault("after-commit")
        return adopted

    def suppress(self, subject):
        self.guard(subject, "adoption")
        with self.transaction():
            self.db.execute("INSERT OR IGNORE INTO suppressions VALUES (?)", (self.subject_key(subject),))
            marker = self._emit(self._payload("refusal", subject, parents=[], operation="routing",
                                             code="subject-suppressed", safe_to_retry=False, grants_authority=False))
            self._put("routing_head", marker)

    def update_policy(self, replacement):
        require(type(replacement) is ExternalPolicy and replacement.sequence > self.policy.sequence,
                "policy rollback or same-sequence fork")
        require(replacement.instance_rappid == self.policy.instance_rappid and replacement.world_id == self.policy.world_id,
                "policy identity/world replacement")
        require(replacement.scopes == self.policy.scopes and replacement.runtime_sha256 == self.policy.runtime_sha256
                and replacement.spec_sha256 == self.policy.spec_sha256,
                "native-rebinding-or-runtime-requalification-required")
        require(not replacement.physical_deletion_required and not replacement.partitioned
                and replacement.max_attempts <= self.policy.max_attempts
                and replacement.max_depth <= self.policy.max_depth
                and replacement.max_frames <= self.policy.max_frames
                and replacement.max_total_octets <= self.policy.max_total_octets,
                "root-budget-reset-or-unsupported-policy")
        with self.transaction():
            self._put("policy", self._policy_value(replacement))
            self._put("sequence", self._get("sequence") + 1)
        self.policy = replacement

    def projection(self):
        for scope in self.policy.scopes:
            self.guard(scope.subject(), "retention")
        values = []
        for operation, candidate, record in self.db.execute("SELECT operation,candidate,record FROM adoptions ORDER BY operation"):
            p = self.body({"space": "rapp/1:wave", "hash": candidate})
            if self.db.execute("SELECT 1 FROM suppressions WHERE key=?", (self.subject_key(p["native_subject"]),)).fetchone():
                continue
            try:
                self.guard(p["native_subject"], "retention", p["restrictions"])
            except Refusal:
                continue
            values.append({"operation": operation, "candidate": candidate, "record": record,
                           "native_subject": p["native_subject"], "result_b64": p["result_b64"]})
        return {"spec_id": PROFILE, "authority": False, "data_only": True, "native_rebinding": False, "entries": values}

    def materialize(self, subject):
        self.guard(subject, "materialization")
        self.guard(subject, "retention")
        for (candidate,) in self.db.execute("SELECT candidate FROM adoptions"):
            p = self.body({"space": "rapp/1:wave", "hash": candidate})
            self.guard(p["native_subject"], "materialization", p["restrictions"])
        # The only output is canonical inert JSON under the controller, never HTML, Markdown, skills or source paths.
        raw = self.core.octets(self.projection())
        write_file(self.path / "view.json", raw)
        return self.path / "view.json"

    def require_effect(self, subject, operation):
        self.guard(subject, operation)
        raise Refusal("unqualified-effect-disabled")

    def verify_history(self):
        head = None
        for seq, key, raw in self.db.execute("SELECT seq,hash,raw FROM frames ORDER BY seq"):
            frame = self.core.parse(raw)
            ok, step, reason = self.core.r.verify_frame(frame, head=head, stream_id_of_record=self.policy.instance_rappid)
            require(ok and frame["seq"] == seq and frame["frame_hash"] == key, f"history integrity refusal: {step}: {reason}")
            require(frame["payload"].get("schema", "").startswith(PROFILE + "/"), "wrong-validator historical frame")
            self.core.schemas.validate(frame["payload"])
            head = frame
        committed = list(self.db.execute("SELECT operation,request,candidate,record FROM adoptions ORDER BY operation"))
        records = []
        for operation, request_hash, candidate_hash, record_hash in committed:
            request = self.body({"space": "rapp/1:wave", "hash": request_hash})
            record = self.body({"space": "rapp/1:wave", "hash": record_hash})
            require(request["schema"] == PROFILE + "/adoption-request"
                    and record["schema"] == PROFILE + "/adoption-record"
                    and record["request"]["hash"] == request_hash
                    and record["candidate"]["hash"] == candidate_hash == request["candidate"]["hash"]
                    and record["operation_id"] == operation == request["operation_id"],
                    "controller-ledger-recovery-quarantine")
            records.append(record_hash)
        adopted_head = self._get("adoption_head")
        require((not records and adopted_head is None)
                or (adopted_head is not None and address(adopted_head) in records),
                "controller-ledger-recovery-quarantine")
        for (assessment_hash,) in self.db.execute("SELECT hash FROM assessments ORDER BY hash"):
            assessment = self.body({"space": "rapp/1:wave", "hash": assessment_hash})
            require(assessment["schema"] == PROFILE + "/organization-assessment",
                    "assessment-ledger-recovery-quarantine")
        for composite_hash, composite_id in self.db.execute(
                "SELECT hash,composite_id FROM composites ORDER BY composite_id"):
            reference = {"space": "rapp/1:wave", "hash": composite_hash}
            composite, _, _, _, _ = self._composite_members(
                self.body(reference)["native_subject"], reference)
            require(composite["composite_id"] == composite_id,
                    "workspace-composite-ledger-recovery-quarantine")
        # Historical receipts remain scoped evidence even if their former evaluator is unavailable.
        return {"rapp_integrity": "verified", "frames": 0 if head is None else head["seq"] + 1,
                "semantic_fidelity": "historical-receipts-only", "current_authorization": "not-inferred",
                "safe_deployment": "disabled"}

    def observe_owned_fork(self, raw):
        frame = self.core.parse(raw)
        prior = self.db.execute("SELECT raw FROM frames WHERE seq=?", (frame["seq"],)).fetchone()
        require(prior is not None, "fork requires an observed owned position")
        previous = self.db.execute("SELECT raw FROM frames WHERE seq=?", (frame["seq"] - 1,)).fetchone()
        ok, _, _ = self.core.r.verify_frame(frame, head=self.core.parse(previous[0]) if previous else None,
                                           stream_id_of_record=self.policy.instance_rappid)
        require(ok and self.core.parse(prior[0])["frame_hash"] != frame["frame_hash"], "unverified fork cannot latch")
        with self.transaction():
            self.db.execute("INSERT OR IGNORE INTO faults VALUES (?,?)", (frame["frame_hash"], raw))
        raise Refusal("owned-store-fork-latched; no external owner-equivocation claim")

    def checkpoint(self):
        return {"instance_rappid": self.policy.instance_rappid, "world_id": self.policy.world_id,
                "frames": [{"seq": row[0], "hash": row[1]} for row in self.db.execute("SELECT seq,hash FROM frames ORDER BY seq")],
                "frontier": self.frontier(), "faults": [r[0] for r in self.db.execute("SELECT hash FROM faults ORDER BY hash")],
                "suppressions": [r[0] for r in self.db.execute("SELECT key FROM suppressions ORDER BY key")],
                "adoptions": [list(r) for r in self.db.execute("SELECT operation,request,candidate,record FROM adoptions ORDER BY operation")]}

    def check_checkpoint(self, checkpoint):
        require(checkpoint["instance_rappid"] == self.policy.instance_rappid
                and checkpoint["world_id"] == self.policy.world_id, "checkpoint identity substitution")
        current = self.checkpoint()
        require(current["frames"][:len(checkpoint["frames"])] == checkpoint["frames"], "history rollback/fork")
        require(current["frontier"]["sequence"] >= checkpoint["frontier"]["sequence"]
                and set(checkpoint["faults"]) <= set(current["faults"]), "controller frontier rollback")
        require(set(checkpoint["suppressions"]) <= set(current["suppressions"]), "suppression rollback")
        require({tuple(r) for r in checkpoint["adoptions"]} <= {tuple(r) for r in current["adoptions"]},
                "adoption-ledger rollback")
        if current["frontier"]["sequence"] == checkpoint["frontier"]["sequence"]:
            require(current["frontier"] == checkpoint["frontier"], "same-sequence controller frontier fork")

    def export_frames(self, destination):
        # This is LOCAL test/inspection carriage. It does not grant redistribution or native rebinding.
        destination = Path(destination)
        require(destination.absolute().is_relative_to(self.path.absolute())
                and destination.absolute() != self.path.absolute(), "local-portability-output-scope")
        for scope in self.policy.scopes:
            self.guard(scope.subject(), "materialization")
            self.guard(scope.subject(), "retention")
        for (raw,) in self.db.execute("SELECT raw FROM frames"):
            p = self.core.parse(raw)["payload"]
            self.guard(p["native_subject"], "materialization", p["restrictions"])
        write_file(destination / "rappid.json", self.core.octets({"schema": "rapp/1", "rappid": self.policy.instance_rappid}),
                   immutable=True)
        for seq, raw in self.db.execute("SELECT seq,raw FROM frames ORDER BY seq"):
            write_file(destination / "frames" / f"{seq}.json", raw, immutable=True)


def verify_historical_archive(core, frames, instance_rappid):
    """Parent integrity survives unavailable application evaluators; no renewed guarantees."""
    head = None
    count = 0
    for raw in frames:
        frame = core.parse(raw)
        ok, step, reason = core.r.verify_frame(frame, head=head, stream_id_of_record=instance_rappid)
        require(ok, f"historical RAPP/1 refusal {step}: {reason}")
        head, count = frame, count + 1
    require(count > 0, "zero-artifact history is not evidence")
    return {"rapp_integrity": "verified", "frames": count, "observation": "historical-receipts-only",
            "semantic_fidelity": "historical-evaluator-unavailable", "current_authorization": "not-inferred",
            "safe_deployment": "disabled"}


def merge_measurement(left, right, correspondence):
    require(correspondence is not None and set(correspondence) == {"pairs"} and len(correspondence["pairs"]) <= 64,
            "merge-correspondence-contract-required")
    pairs = correspondence["pairs"]
    require(type(left) is dict and type(right) is dict and len(left) <= 128 and len(right) <= 128,
            "bounded comparison inputs required")
    require(all(isinstance(p, (list, tuple)) and len(p) == 2 and all(type(k) is str for k in p) for p in pairs)
            and len({p[0] for p in pairs}) == len(pairs) and len({p[1] for p in pairs}) == len(pairs),
            "ambiguous correspondence contract")
    compared = [(a, b) for a, b in pairs if a in left and b in right]
    agreements = sum(left[a] == right[b] for a, b in compared)
    return {"status": "measured" if compared else "unmeasured", "compared": len(compared),
            "required": len(pairs), "coverage_complete": len(compared) == len(pairs) and bool(pairs),
            "numerator": agreements if compared else None, "denominator": len(compared) if compared else None,
            "conflicts": [(a, b) for a, b in compared if left[a] != right[b]], "retained": [left, right]}


def reattach_measurement(necessary_reads, available_context):
    require(type(necessary_reads) is dict and type(available_context) is dict
            and len(necessary_reads) <= 128 and len(available_context) <= 128, "bounded context coverage required")
    missing = sorted(set(necessary_reads) - set(available_context))
    conflicts = sorted(k for k in necessary_reads.keys() & available_context.keys()
                       if necessary_reads[k] != available_context[k])
    return {"status": "unresolved" if missing or conflicts else "candidate-only",
            "missing_coverage": missing, "contradictions": conflicts, "adopted": False}


def delta_plan(scope, baseline_scope, baseline_expires, now, changed, generated):
    require(all(isinstance(v, (list, tuple)) and len(v) <= 128 for v in
                (scope, baseline_scope, changed, generated)), "bounded scan plan required")
    for value in (baseline_expires, now):
        require(type(value) is str and len(value) == 24, "fixed trusted scan clock required")
        try:
            datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%fZ")
        except ValueError as exc:
            raise Refusal("invalid scan clock") from exc
    require(set(scope).isdisjoint(generated), "generated-output-excluded-from-observation")
    if set(scope) != set(baseline_scope) or now >= baseline_expires:
        return {"mode": "baseline-required", "targets": sorted(scope), "current_clean_claim": False}
    require(set(changed) <= set(scope), "delta outside approved scope")
    return {"mode": "delta", "targets": sorted(set(changed)), "current_clean_claim": False}
