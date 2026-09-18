"""Non-authoritative, bounded exact indexes over caller-pinned application data."""

from __future__ import annotations

import base64
from dataclasses import dataclass
import os
from pathlib import Path
import sqlite3
from types import MappingProxyType

from common import Refusal, canonical, directory, parse, read_file, require, sha, validate
from schema_source import (
    MAX_CONTENT_BYTES, MAX_DB_BYTES, MAX_ITEMS, MAX_MANIFEST_BYTES, MAX_OPERATIONS,
    MAX_PAGE_SIZE, MAX_SHARD_BYTES, MAX_SHARD_ITEMS, MAX_SQL_STEPS, MAX_TOKEN_BYTES,
    MAX_TOTAL_BYTES, PROFILE, SHARDS,
)

IDENTITY_FIELDS = ("rappid", "content_sha256", "content_bytes", "particle_hash", "occurrence_hash")
ORDER_FIELDS = ("rappid", "content_sha256", "particle_hash", "occurrence_hash")
OCCURRENCE_FIELDS = (
    "signer", "spki_sha256", "stream", "key_epoch", "registry_epoch", "seq",
    "payload_hash", "frame_hash", "frame_sha256",
)


def identity(record):
    return {key: record[key] for key in IDENTITY_FIELDS}


def candidate_order(record):
    return tuple(record[key] for key in ORDER_FIELDS)


def record_order(record):
    return (record["domain"], record["key"], *candidate_order(record))


def shard_for(domain, key):
    query = validate({"domain": domain, "key": key}, "query")
    digest = sha(b"rapp-work-index/1:key\x00" + canonical(query))
    return int(digest[:2], 16) % SHARDS


def leaf_hash(shard, content_hash, size):
    return sha(
        b"rapp-work-index/1:leaf\x00" + shard.to_bytes(2, "big")
        + size.to_bytes(8, "big") + bytes.fromhex(content_hash)
    )


def node_hash(left, right):
    return sha(b"rapp-work-index/1:node\x00" + bytes.fromhex(left) + bytes.fromhex(right))


def tree_levels(leaves):
    require(type(leaves) is list and len(leaves) == SHARDS, "fixed sixteen-leaf tree required")
    levels = [leaves]
    while len(levels[-1]) > 1:
        layer = levels[-1]
        levels.append([node_hash(layer[i], layer[i + 1]) for i in range(0, len(layer), 2)])
    return levels


def source_map(vector):
    validate(vector, "source-vector")
    require([entry["source"] for entry in vector] == sorted(entry["source"] for entry in vector),
            "source vector must be sorted")
    require(len({entry["source"] for entry in vector}) == len(vector), "duplicate source label")
    result = {}
    for entry in vector:
        key = (entry["subject"], entry["frame_hash"])
        require(key not in result, "duplicate source occurrence")
        result[key] = (entry["raw_sha256"], entry["raw_bytes"], entry["payload_hash"])
    return result


def validate_record(record, sources):
    validate(record, "record")
    require(len(canonical(record)) <= 2048, "record byte budget")
    source = sources.get((record["rappid"], record["occurrence_hash"]))
    require(source is not None, "candidate occurrence absent from pinned source vector")
    require(
        (record["content_sha256"], record["content_bytes"], record["particle_hash"])
        == source,
        "candidate bytes/particle substitution",
    )
    return record


def validate_manifest(manifest):
    validate(manifest, "generation")
    canonical(manifest, MAX_MANIFEST_BYTES)
    source_map(manifest["source_vector"])
    require([item["shard"] for item in manifest["shards"]] == list(range(SHARDS)),
            "manifest shard coverage/order")
    for item in manifest["shards"]:
        require(item["leaf_hash"] == leaf_hash(item["shard"], item["sha256"], item["bytes"]),
                "manifest leaf mismatch")
    root = tree_levels([item["leaf_hash"] for item in manifest["shards"]])[-1][0]
    require(root == manifest["root"], "manifest Merkle root mismatch")
    require(sum(item["items"] for item in manifest["shards"]) == manifest["total_items"],
            "manifest item total mismatch")
    require(sum(item["bytes"] for item in manifest["shards"]) == manifest["total_bytes"],
            "manifest byte total mismatch")
    return manifest


def build_generation(records, generation, context, sources):
    """Consume at most 4,097 input records; all retained buffers have hard ceilings."""
    validate(context, "context")
    require(type(sources) is list, "explicit bounded source vector required")
    validate(sources, "source-vector")
    sources = sorted(sources, key=lambda item: item["source"])
    by_source = source_map(sources)
    buckets = [[] for _ in range(SHARDS)]
    seen, count = set(), 0
    for record in records:
        count += 1
        require(count <= MAX_ITEMS, "record input expansion budget")
        validate_record(record, by_source)
        key = record_order(record)
        require(key not in seen, "duplicate candidate identity; never first-wins")
        seen.add(key)
        bucket = buckets[shard_for(record["domain"], record["key"])]
        require(len(bucket) < MAX_SHARD_ITEMS, "shard item/collision bucket budget")
        bucket.append(parse(canonical(record)))
    raw_shards, descriptors, total_bytes = {}, [], 0
    for number, records_in_shard in enumerate(buckets):
        raw = canonical({
            "schema": PROFILE + "/shard",
            "shard": number,
            "records": sorted(records_in_shard, key=record_order),
        })
        total_bytes += len(raw)
        require(total_bytes <= MAX_TOTAL_BYTES, "generation byte budget")
        raw_shards[number] = raw
        digest = sha(raw)
        descriptors.append({
            "shard": number, "sha256": digest, "bytes": len(raw),
            "items": len(records_in_shard), "leaf_hash": leaf_hash(number, digest, len(raw)),
        })
    manifest = {
        "schema": PROFILE + "/generation",
        "generation": generation,
        "root": tree_levels([item["leaf_hash"] for item in descriptors])[-1][0],
        "context": parse(canonical(context)),
        "source_vector": parse(canonical(sources, MAX_MANIFEST_BYTES), MAX_MANIFEST_BYTES),
        "shards": descriptors,
        "total_items": count,
        "total_bytes": total_bytes,
        "authority": False,
    }
    validate_manifest(manifest)
    return manifest, raw_shards, make_proofs(manifest)


def make_proofs(manifest):
    validate_manifest(manifest)
    levels = tree_levels([item["leaf_hash"] for item in manifest["shards"]])
    manifest_hash = sha(canonical(manifest, MAX_MANIFEST_BYTES))
    proofs = []
    for number in range(SHARDS):
        index, siblings = number, []
        for level in levels[:-1]:
            siblings.append(level[index ^ 1])
            index //= 2
        proofs.append({
            "schema": PROFILE + "/proof", "manifest_sha256": manifest_hash,
            "root": manifest["root"], "shard": number,
            "leaf_hash": levels[0][number], "siblings": siblings,
        })
    return proofs


def checkpoint_payload(manifest):
    validate_manifest(manifest)
    return {
        "schema": PROFILE + "/checkpoint",
        "generation": manifest["generation"],
        "manifest_sha256": sha(canonical(manifest, MAX_MANIFEST_BYTES)),
        "root": manifest["root"],
        "context_sha256": sha(canonical(manifest["context"])),
        "source_vector_sha256": sha(canonical(manifest["source_vector"], MAX_MANIFEST_BYTES)),
        "authority": False,
    }


def check_transition(previous, candidate):
    validate(previous, "binding")
    validate(candidate, "binding")
    require(candidate["stream"] == previous["stream"],
            "stream change requires a separate externally authenticated lineage")
    require(candidate["seq"] >= previous["seq"], "checkpoint rollback")
    if candidate["seq"] == previous["seq"]:
        require(candidate["root"] == previous["root"], "same-sequence root fork")
        require(candidate == previous, "same-sequence occurrence/generation fork")
        return
    require(candidate["generation"] > previous["generation"], "generation rollback/reuse")
    require(candidate["frame_hash"] != previous["frame_hash"], "context pivot needs a new signed wave")
    require(candidate["key_epoch"] >= previous["key_epoch"], "key epoch rollback")
    require(candidate["registry_epoch"] >= previous["registry_epoch"], "registry epoch rollback")


def bind_checkpoint(manifest, verified_frame, expected_context, previous=None):
    """The verified record is a protected caller input, NEVER a self-authenticating receipt."""
    validate_manifest(manifest)
    validate(verified_frame, "verified-frame")
    validate(expected_context, "context")
    require(manifest["context"] == expected_context == verified_frame["context"],
            "externally current context differs")
    require(verified_frame["payload"] == checkpoint_payload(manifest),
            "checkpoint does not bind this exact generation")
    for name in ("signer", "spki_sha256", "stream", "key_epoch", "registry_epoch"):
        require(verified_frame[name] == expected_context[name], "checkpoint signer/epoch/stream mismatch")
    result = {
        **checkpoint_payload(manifest),
        "schema": PROFILE + "/binding",
        **{key: verified_frame[key] for key in OCCURRENCE_FIELDS},
    }
    validate(result, "binding")
    if previous is not None:
        check_transition(previous, result)
    return result


def validate_checkpoint_binding(binding, manifest, verified_frame, expected_context, previous=None):
    validate(binding, "binding")
    require(binding == bind_checkpoint(manifest, verified_frame, expected_context, previous),
            "stored checkpoint binding substitution")
    return binding


@dataclass(frozen=True, init=False)
class PinnedGeneration:
    _manifest: bytes
    _binding: bytes
    _frontier: bytes
    _descriptors: tuple
    _sources: MappingProxyType
    _manifest_hash: str
    _root: str
    _generation: int
    _frame_hash: str

    def __init__(self, manifest, verified_frame, expected_context, previous=None):
        binding = bind_checkpoint(
            manifest, verified_frame, expected_context,
            None if previous is None else previous.binding,
        )
        frontier = {
            "schema": PROFILE + "/frontier",
            "context": expected_context,
            "source_vector": manifest["source_vector"],
            "manifest_sha256": binding["manifest_sha256"],
            "checkpoint_frame_hash": binding["frame_hash"],
            "checkpoint_frame_sha256": binding["frame_sha256"],
        }
        validate(frontier, "frontier")
        object.__setattr__(self, "_manifest", canonical(manifest, MAX_MANIFEST_BYTES))
        object.__setattr__(self, "_binding", canonical(binding))
        object.__setattr__(self, "_frontier", canonical(frontier, MAX_MANIFEST_BYTES))
        object.__setattr__(self, "_descriptors", tuple(
            (item["sha256"], item["bytes"], item["items"], item["leaf_hash"])
            for item in manifest["shards"]
        ))
        object.__setattr__(self, "_sources", MappingProxyType(source_map(manifest["source_vector"])))
        object.__setattr__(self, "_manifest_hash", binding["manifest_sha256"])
        object.__setattr__(self, "_root", manifest["root"])
        object.__setattr__(self, "_generation", manifest["generation"])
        object.__setattr__(self, "_frame_hash", binding["frame_hash"])

    @property
    def manifest(self):
        return parse(self._manifest, MAX_MANIFEST_BYTES)

    @property
    def binding(self):
        return parse(self._binding)

    @property
    def frontier(self):
        """A comparison value, NOT a source of present authorization/freshness."""
        return parse(self._frontier, MAX_MANIFEST_BYTES)

    @property
    def fingerprint(self):
        return sha(b"rapp-work-index/1:generation\x00" + self._manifest + self._binding)

    def require_current(self, current_frontier):
        validate(current_frontier, "frontier")
        require(canonical(current_frontier, MAX_MANIFEST_BYTES) == self._frontier,
                "stale cache: checkpoint/policy/key/registry/grant/revocation/subscription/source changed")


def verify_shard(pin, current_frontier, raw, proof):
    pin.require_current(current_frontier)
    require(type(raw) is bytes and len(raw) <= MAX_SHARD_BYTES, "shard byte budget")
    validate(proof, "proof")
    content_hash, size, count, leaf = pin._descriptors[proof["shard"]]
    require(proof["manifest_sha256"] == pin._manifest_hash
            and proof["root"] == pin._root, "proof belongs to another generation/root")
    require(len(raw) == size and sha(raw) == content_hash,
            "shard exact-byte hash/size mismatch")
    require(proof["leaf_hash"] == leaf, "proof leaf substitution")
    node, position = proof["leaf_hash"], proof["shard"]
    for sibling in proof["siblings"]:
        node = node_hash(sibling, node) if position & 1 else node_hash(node, sibling)
        position //= 2
    require(node == pin._root, "Merkle inclusion failure")
    shard = validate(parse(raw), "shard")
    require(shard["shard"] == proof["shard"], "shard position substitution")
    require(len(shard["records"]) == count, "shard item count mismatch")
    keys = []
    for record in shard["records"]:
        validate_record(record, pin._sources)
        require(shard_for(record["domain"], record["key"]) == shard["shard"],
                "candidate assigned to wrong shard")
        keys.append(record_order(record))
    require(keys == sorted(keys) and len(set(keys)) == len(keys),
            "shard order/duplicate collision; never first-wins")
    return shard


def accept_shard(pin, current_frontier, raw, proof):
    verify_shard(pin, current_frontier, raw, proof)
    return raw


def anti_entropy(local, target, local_frontier, target_frontier, supplied_bytes):
    """Compare only explicit pins and at most sixteen supplied byte strings; no fetch."""
    local.require_current(local_frontier)
    target.require_current(target_frontier)
    check_transition(local.binding, target.binding)
    require(type(supplied_bytes) is dict and len(supplied_bytes) <= SHARDS,
            "anti-entropy inventory budget")
    total = 0
    for number, raw in supplied_bytes.items():
        require(type(number) is int and 0 <= number < SHARDS, "inventory shard number")
        require(type(raw) is bytes and len(raw) <= MAX_SHARD_BYTES, "inventory shard byte budget")
        total += len(raw)
        require(total <= MAX_TOTAL_BYTES, "inventory total byte budget")
    result = {
        "schema": PROFILE + "/anti-entropy",
        "local_manifest_sha256": local.binding["manifest_sha256"],
        "target_manifest_sha256": target.binding["manifest_sha256"],
        "target_generation": target.binding["generation"],
        "target_root": target.binding["root"],
        "changed": [], "missing": [], "divergent": [], "available_needs_proof": [],
        "authority": False,
    }
    for old, new in zip(local.manifest["shards"], target.manifest["shards"]):
        number = new["shard"]
        if old["sha256"] != new["sha256"]:
            result["changed"].append({
                "shard": number, "local_sha256": old["sha256"], "target_sha256": new["sha256"],
            })
        if number not in supplied_bytes:
            result["missing"].append({"shard": number, "target_sha256": new["sha256"]})
        else:
            observed = sha(supplied_bytes[number])
            if observed != new["sha256"]:
                result["divergent"].append({
                    "shard": number, "local_sha256": old["sha256"],
                    "observed_sha256": observed, "target_sha256": new["sha256"],
                })
            else:
                result["available_needs_proof"].append({"shard": number, "sha256": observed})
    return validate(result, "anti-entropy")


def cache_key(raw, pin, current_frontier):
    pin.require_current(current_frontier)
    require(type(raw) is bytes and len(raw) <= MAX_CONTENT_BYTES, "cache raw byte budget")
    return sha(
        b"rapp-work-index/1:cache\x00" + bytes.fromhex(sha(raw))
        + len(raw).to_bytes(8, "big") + bytes.fromhex(pin.fingerprint)
    )


def encode_token(pin, domain, key, after, page_size):
    cursor = {
        "schema": PROFILE + "/cursor",
        "generation": pin._generation,
        "manifest_sha256": pin._manifest_hash,
        "root": pin._root,
        "binding_sha256": sha(pin._binding),
        "checkpoint_frame_hash": pin._frame_hash,
        "domain": domain, "key": key, "shard": shard_for(domain, key),
        "after": after, "page_size": page_size,
    }
    validate(cursor, "cursor")
    raw = canonical({
        "cursor": cursor,
        "checksum": sha(b"rapp-work-index/1:cursor\x00" + canonical(cursor)),
    }, MAX_TOKEN_BYTES)
    token = base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")
    require(len(token) <= MAX_TOKEN_BYTES, "token byte budget")
    return token


def decode_token(token, pin, domain, key, page_size):
    require(type(token) is str and 0 < len(token) <= MAX_TOKEN_BYTES and token.isascii(),
            "bounded opaque cursor required")
    require(all(char.isalnum() or char in "-_" for char in token), "noncanonical base64url")
    try:
        raw = base64.b64decode(token + "=" * (-len(token) % 4), altchars=b"-_", validate=True)
    except ValueError as error:
        raise Refusal("invalid cursor encoding") from error
    require(base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii") == token,
            "noncanonical cursor bits")
    document = validate(parse(raw, MAX_TOKEN_BYTES), "token")
    cursor = document["cursor"]
    require(token == encode_token(pin, domain, key, cursor["after"], page_size),
            "cursor checksum/generation/root/domain/key/shard/size mismatch")
    return cursor["after"]


TABLES = {
    "metadata": "CREATE TABLE metadata (key TEXT PRIMARY KEY, value BLOB NOT NULL) WITHOUT ROWID",
    "shards": (
        "CREATE TABLE shards (shard INTEGER PRIMARY KEY, raw BLOB NOT NULL, "
        "proof BLOB NOT NULL) WITHOUT ROWID"
    ),
    "records": (
        "CREATE TABLE records (domain TEXT COLLATE BINARY NOT NULL, "
        "key TEXT COLLATE BINARY NOT NULL, rappid TEXT COLLATE BINARY NOT NULL, "
        "content_sha256 TEXT COLLATE BINARY NOT NULL, particle_hash TEXT COLLATE BINARY NOT NULL, "
        "occurrence_hash TEXT COLLATE BINARY NOT NULL, content_bytes INTEGER NOT NULL, "
        "shard INTEGER NOT NULL, raw BLOB NOT NULL, "
        "PRIMARY KEY (domain,key,rappid,content_sha256,particle_hash,occurrence_hash)) WITHOUT ROWID"
    ),
}
APPLICATION_ID = 0x52574931


def row(record, number):
    return (*record_order(record), record["content_bytes"], number, canonical(record))


def configure(connection):
    if hasattr(connection, "enable_load_extension"):
        connection.enable_load_extension(False)
    connection.setlimit(sqlite3.SQLITE_LIMIT_LENGTH, MAX_SHARD_BYTES + MAX_MANIFEST_BYTES)
    connection.setlimit(sqlite3.SQLITE_LIMIT_SQL_LENGTH, 8192)
    connection.setlimit(sqlite3.SQLITE_LIMIT_COLUMN, 32)
    connection.setlimit(sqlite3.SQLITE_LIMIT_ATTACHED, 0)
    connection.setlimit(sqlite3.SQLITE_LIMIT_EXPR_DEPTH, 64)
    connection.setlimit(sqlite3.SQLITE_LIMIT_VARIABLE_NUMBER, 32)
    connection.execute("PRAGMA trusted_schema=OFF")
    connection.execute("PRAGMA temp_store=MEMORY")
    connection.execute("PRAGMA cache_size=-2048")
    connection.execute("PRAGMA mmap_size=0")
    steps = 0

    def progress():
        nonlocal steps
        steps += 1000
        return int(steps >= MAX_SQL_STEPS)

    connection.set_progress_handler(progress, 1000)


def owned_database_path(path, *, create=False):
    path = Path(path)
    require(not path.is_absolute() and ".." not in path.parts and path.name.endswith(".sqlite3"),
            "explicit relative .sqlite3 path required")
    with directory(path.parent, create=create) as parent:
        info = os.fstat(parent)
        require(info.st_uid == os.getuid() and not info.st_mode & 0o022,
                "database parent must be caller-owned and not group/world writable")
        for suffix in ("-journal", "-wal", "-shm"):
            require(not os.path.lexists(str(path) + suffix),
                    "unrecovered SQLite sidecar; explicit discard/rebuild required")
    return path


class ExactIndex:
    """One bounded, verified, read-only SQLite snapshot; it grants no source authority."""

    @classmethod
    def build(cls, path, pin, current_frontier, supplied_shards):
        pin.require_current(current_frontier)
        seen, verified, total = set(), [], 0
        for position, pair in enumerate(supplied_shards):
            require(position < SHARDS, "shard input/queue budget")
            require(type(pair) in (tuple, list) and len(pair) == 2, "bytes plus proof required")
            raw, proof = pair
            shard = verify_shard(pin, current_frontier, raw, proof)
            number = shard["shard"]
            require(number not in seen, "duplicate shard; never first-wins")
            seen.add(number)
            total += len(raw)
            require(total <= MAX_TOTAL_BYTES, "database input byte budget")
            verified.append((number, raw, canonical(proof), shard["records"]))
        require(seen == set(range(SHARDS)), "missing shard/proof; incomplete generation refused")
        path = owned_database_path(path, create=True)
        with directory(path.parent) as parent:
            try:
                fd = os.open(
                    path.name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                    0o600, dir_fd=parent,
                )
                os.close(fd)
            except OSError as error:
                raise Refusal("database already exists or cannot be exclusively created") from error
        connection = None
        try:
            connection = sqlite3.connect(path.absolute().as_uri() + "?mode=rw", uri=True, timeout=0)
            configure(connection)
            connection.execute("PRAGMA page_size=4096")
            connection.execute("PRAGMA journal_mode=DELETE")
            connection.execute("PRAGMA synchronous=FULL")
            connection.execute(f"PRAGMA max_page_count={MAX_DB_BYTES // 4096}")
            connection.execute(f"PRAGMA application_id={APPLICATION_ID}")
            with connection:
                for statement in TABLES.values():
                    connection.execute(statement)
                connection.executemany("INSERT INTO metadata VALUES (?,?)", [
                    ("manifest", pin._manifest), ("binding", pin._binding),
                    ("fingerprint", pin.fingerprint.encode("ascii")),
                ])
                for number, raw, proof_raw, records in sorted(verified):
                    connection.execute("INSERT INTO shards VALUES (?,?,?)", (number, raw, proof_raw))
                    connection.executemany(
                        "INSERT INTO records VALUES (?,?,?,?,?,?,?,?,?)",
                        (row(record, number) for record in records),
                    )
            require(path.stat().st_size <= MAX_DB_BYTES, "database disk budget")
        except (sqlite3.Error, OSError) as error:
            raise Refusal("index build failed; explicit discard/rebuild required") from error
        finally:
            if connection is not None:
                connection.close()

    def __init__(self, path, pin, current_frontier, *, operation_limit=MAX_OPERATIONS):
        pin.require_current(current_frontier)
        require(type(operation_limit) is int and 1 <= operation_limit <= MAX_OPERATIONS,
                "operation ceiling")
        self.pin, self._operations, self._operation_limit = pin, 0, operation_limit
        self._connection = None
        self._closed = True
        path = owned_database_path(path)
        read_file(path, MAX_DB_BYTES)
        try:
            self._connection = sqlite3.connect(
                path.absolute().as_uri() + "?mode=ro", uri=True, timeout=0,
            )
            configure(self._connection)
            self._connection.execute("PRAGMA query_only=ON")
            self._connection.execute("BEGIN")
            self._verify_snapshot(current_frontier)
            self._closed = False
        except (sqlite3.Error, OSError, Refusal) as error:
            self.close()
            raise Refusal("index unavailable/corrupt/stale; explicit rebuild only") from error

    def _verify_snapshot(self, current_frontier):
        connection = self._connection
        require(connection.execute("PRAGMA application_id").fetchone() == (APPLICATION_ID,),
                "unknown SQLite application")
        require(connection.execute("PRAGMA page_size").fetchone() == (4096,), "SQLite page size")
        require(connection.execute("PRAGMA page_count").fetchone()[0] * 4096 <= MAX_DB_BYTES,
                "SQLite page budget")
        require(connection.execute("PRAGMA quick_check(1)").fetchone() == ("ok",), "SQLite corruption")
        definitions = connection.execute(
            "SELECT name,sql FROM sqlite_master WHERE type='table' ORDER BY name LIMIT 4"
        ).fetchall()
        require(definitions == sorted(TABLES.items()), "SQLite table/schema substitution")
        extras = connection.execute(
            "SELECT type FROM sqlite_master WHERE type!='table' LIMIT 1"
        ).fetchone()
        require(extras is None, "SQLite views/triggers/indexes not in the closed layout")
        metadata = connection.execute("SELECT key,value FROM metadata ORDER BY key LIMIT 4").fetchall()
        require(metadata == sorted([
            ("manifest", self.pin._manifest), ("binding", self.pin._binding),
            ("fingerprint", self.pin.fingerprint.encode("ascii")),
        ]), "SQLite generation/checkpoint substitution")
        shards = connection.execute("SELECT shard,raw,proof FROM shards ORDER BY shard LIMIT 17")
        expected, shard_count, byte_count = [], 0, 0
        for number, raw, proof_raw in shards:
            require(type(number) is int and number == shard_count < SHARDS, "SQLite shard coverage/order")
            shard_count += 1
            require(type(raw) is bytes and type(proof_raw) is bytes, "SQLite byte types")
            require(len(proof_raw) <= MAX_TOKEN_BYTES, "SQLite proof byte budget")
            byte_count += len(raw)
            require(byte_count <= MAX_TOTAL_BYTES, "SQLite shard byte budget")
            shard = verify_shard(self.pin, current_frontier, raw, parse(proof_raw, MAX_TOKEN_BYTES))
            require(number == shard["shard"], "SQLite shard alias")
            expected.extend(row(record, number) for record in shard["records"])
        require(shard_count == SHARDS, "SQLite missing shards")
        expected.sort(key=lambda record: record[:6])
        actual = connection.execute(
            "SELECT domain,key,rappid,content_sha256,particle_hash,occurrence_hash,"
            "content_bytes,shard,raw FROM records "
            "ORDER BY domain,key,rappid,content_sha256,particle_hash,occurrence_hash LIMIT 4097"
        )
        count = 0
        for count, record in enumerate(actual, 1):
            require(count <= len(expected) and record == expected[count - 1],
                    "SQLite row corruption/omission/substitution")
        require(count == len(expected), "SQLite omitted candidates; no first-wins")

    def _begin_operation(self, current_frontier):
        require(not self._closed, "index snapshot closed")
        self.pin.require_current(current_frontier)
        self._operations += 1
        require(self._operations <= self._operation_limit, "index operation budget exhausted")

    def lookup(self, current_frontier, domain, key):
        self._begin_operation(current_frontier)
        shard_for(domain, key)
        try:
            rows = self._connection.execute(
                "SELECT raw FROM records WHERE domain=? AND key=? "
                "ORDER BY rappid,content_sha256,particle_hash,occurrence_hash LIMIT 257",
                (domain, key),
            ).fetchall()
            require(len(rows) <= MAX_SHARD_ITEMS, "exact collision bucket budget")
            return {
                "records": [validate(parse(item[0]), "record") for item in rows],
                "authority": False,
            }
        except sqlite3.Error as error:
            raise Refusal("SQLite exact lookup refused; no fallback") from error

    def page(self, current_frontier, domain, key, *, page_size, token=None):
        self._begin_operation(current_frontier)
        shard_for(domain, key)
        require(type(page_size) is int and 1 <= page_size <= MAX_PAGE_SIZE, "page size budget")
        after = None if token is None else decode_token(token, self.pin, domain, key, page_size)
        try:
            if after is not None:
                found = self._connection.execute(
                    "SELECT raw FROM records WHERE domain=? AND key=? AND "
                    "(rappid,content_sha256,particle_hash,occurrence_hash)=(?,?,?,?)",
                    (domain, key, *candidate_order(after)),
                ).fetchone()
                require(found is not None and identity(parse(found[0])) == after,
                        "cursor final full identity absent/substituted")
                rank = self._connection.execute(
                    "SELECT COUNT(*) FROM records WHERE domain=? AND key=? AND "
                    "(rappid,content_sha256,particle_hash,occurrence_hash)<=(?,?,?,?)",
                    (domain, key, *candidate_order(after)),
                ).fetchone()[0]
                require(rank % page_size == 0, "cursor not at a complete page boundary")
            condition = "" if after is None else (
                " AND (rappid,content_sha256,particle_hash,occurrence_hash)>(?,?,?,?)"
            )
            parameters = (domain, key, *(() if after is None else candidate_order(after)), page_size + 1)
            rows = self._connection.execute(
                "SELECT raw FROM records WHERE domain=? AND key=?" + condition
                + " ORDER BY rappid,content_sha256,particle_hash,occurrence_hash LIMIT ?",
                parameters,
            ).fetchall()
            require(after is None or rows, "cursor is terminal, not a continuation")
            records = [validate(parse(item[0]), "record") for item in rows[:page_size]]
            continuation = (
                encode_token(self.pin, domain, key, identity(records[-1]), page_size)
                if len(rows) > page_size else None
            )
            return {"records": records, "continuation": continuation, "authority": False}
        except sqlite3.Error as error:
            raise Refusal("SQLite lookup refused; no fallback") from error

    def summon(self, current_frontier, domain, key, full_identity, raw_content):
        self._begin_operation(current_frontier)
        shard_for(domain, key)
        validate(full_identity, "identity")
        require(type(raw_content) is bytes and len(raw_content) <= MAX_CONTENT_BYTES,
                "bounded explicitly supplied content required")
        require(sha(raw_content) == full_identity["content_sha256"]
                and len(raw_content) == full_identity["content_bytes"], "summon content substitution")
        try:
            found = self._connection.execute(
                "SELECT raw FROM records WHERE domain=? AND key=? AND "
                "(rappid,content_sha256,particle_hash,occurrence_hash)=(?,?,?,?)",
                (domain, key, *candidate_order(full_identity)),
            ).fetchone()
        except sqlite3.Error as error:
            raise Refusal("SQLite summon refused") from error
        require(found is not None, "full summon identity is not a candidate")
        record = validate(parse(found[0]), "record")
        require(identity(record) == full_identity, "summon identity/byte-count substitution")
        return {"candidate": record, "status": "disambiguated-not-authorized", "authority": False}

    def close(self):
        if self._connection is not None:
            self._connection.close()
            self._connection = None
        self._closed = True

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        self.close()


def platform_adapters():
    configurations = [
        ("posix-sqlite", "reference", ["posix", "macos", "linux"],
         ["sqlite-without-rowid", "explicit-filesystem"],
         ["safe-copy", "optional-reflink", "optional-apfs-clone"]),
        ("windows-sqlite", "mapping-only", ["windows"],
         ["sqlite-without-rowid", "explicit-filesystem"],
         ["safe-copy", "optional-refs-block-clone"]),
        ("browser", "mapping-only", ["browser"],
         ["indexeddb", "opfs", "webcrypto"], []),
    ]
    return [
        validate({
            "name": name, "status": status, "platforms": platforms, "stores": stores,
            "optimizations": optimizations,
            "verification": "identical-canonical-shards-and-external-checkpoint",
            "authority": False, "resident_processes": 0, "polling": False, "network": False,
        }, "adapter")
        for name, status, platforms, stores, optimizations in configurations
    ]
