"""Bounded, effect-free profile tests; canonical cryptographic tests are a separate gate."""

import ast
import copy
from contextlib import closing
import os
import sqlite3
import unittest
from unittest import mock

from support import DatabaseCase, FixtureCase, fixture, pin_for, receipt_double
from common import Refusal, canonical, parse, read_file, sha, validate, write_file
from schema_source import (
    MAX_DB_BYTES, MAX_INT, MAX_MANIFEST_BYTES, MAX_SHARD_BYTES, MAX_TOKEN_BYTES, ROOT,
    check as check_schema, schema,
)
from vectors import FIXTURES, check_local
from work_index import (
    ExactIndex, PinnedGeneration, accept_shard, anti_entropy, bind_checkpoint,
    build_generation, cache_key, candidate_order, check_transition, checkpoint_payload,
    decode_token, encode_token, identity, leaf_hash, make_proofs, node_hash,
    platform_adapters, shard_for, tree_levels, validate_checkpoint_binding,
    validate_manifest, verify_shard,
)


class EncodingTests(FixtureCase):
    def test_exact_generated_schema_and_vectors(self):
        check_schema()
        check_local()

    def test_every_object_schema_is_closed(self):
        def visit(value):
            if isinstance(value, dict):
                if value.get("type") == "object":
                    self.assertIs(value["additionalProperties"], False)
                    self.assertEqual(set(value["properties"]), set(value["required"]))
                for child in value.values():
                    visit(child)
            elif isinstance(value, list):
                for child in value:
                    visit(child)
        visit(schema())
        self.assertEqual(schema()["$schema"], "https://json-schema.org/draft/2020-12/schema")

    def test_safety_matrix_references_existing_tests(self):
        names = set()
        for path in (ROOT / "tests").glob("test_*.py"):
            tree = ast.parse(read_file(path))
            for node in tree.body:
                if isinstance(node, ast.ClassDef):
                    names.update(
                        node.name + "." + method.name for method in node.body
                        if isinstance(method, ast.FunctionDef) and method.name.startswith("test_")
                    )
        matrix = parse(read_file(ROOT / "safety-matrix.json"), exact=False)
        for requirement in matrix["requirements"]:
            self.assertTrue(set(requirement["tests"]) <= names, requirement["id"])

    def test_duplicate_json_members_refused(self):
        with self.assertRaises(Refusal):
            parse(b'{"a":1,"a":2}')

    def test_noncanonical_encodings_refused(self):
        for raw in (b'{"b":1,"a":2}', b'{"a": 1}', b'{"a":1}\n', b'{"a":1.0}',
                    b'{"a":NaN}', b'{"a":9007199254740992}', b'{"a":-0}'):
            with self.subTest(raw=raw), self.assertRaises(Refusal):
                parse(raw)

    def test_application_domain_refuses_cycles_depth_unicode_float(self):
        cycle = []
        cycle.append(cycle)
        deep = []
        for _ in range(18):
            deep = [deep]
        for value in (cycle, deep, {"key": "\u00e9"}, {"key": 1.0}, {"key": MAX_INT + 1}):
            with self.subTest(kind=type(value)), self.assertRaises(Refusal):
                canonical(value)

    def test_bounds_and_types(self):
        for value in (True, -1, MAX_INT + 1):
            changed = copy.deepcopy(self.manifest)
            changed["generation"] = value
            with self.subTest(value=value), self.assertRaises(Refusal):
                validate_manifest(changed)
        with self.assertRaises(Refusal):
            parse(b" " * (MAX_SHARD_BYTES + 1))

    def test_aggregate_escaped_byte_budget_precedes_materialization(self):
        document = {"unexpected": ["\x00" * 4096] * 1024}
        from common import json as common_json

        original = common_json.dumps

        def guarded(value, *args, **kwargs):
            if value is document:
                self.fail("oversized canonical document was materialized")
            return original(value, *args, **kwargs)

        with mock.patch("common.json.dumps", side_effect=guarded), self.assertRaises(Refusal):
            canonical(document, MAX_MANIFEST_BYTES)

    def test_unknown_fields_refuse(self):
        for name, document in (
            ("record", self.inputs["records"][0]), ("generation", self.manifest),
            ("proof", self.proofs[0]), ("binding", self.pin.binding),
            ("frontier", self.current), ("verified-frame", receipt_double(self.manifest)),
        ):
            changed = {**document, "authority_grant": True}
            with self.subTest(name=name), self.assertRaises(Refusal):
                validate(changed, name)

    def test_key_and_rappid_grammar(self):
        for key in ("", "a" * 129, "cedar\n", "\u00e9", " ced ar"):
            with self.subTest(key=key), self.assertRaises(Refusal):
                shard_for("summon", key)
        record = dict(self.inputs["records"][0])
        record["rappid"] = "rappid:@" + "x" * 40 + "/cedar:" + "a" * 64
        with self.assertRaises(Refusal):
            validate(record, "record")
        # A key which happens to resemble an incomplete identity is still an exact key.
        self.assertIsInstance(shard_for("catalog", "rappid:@short"), int)


class MerkleTests(FixtureCase):
    def test_reproduction_independent_of_input_order(self):
        manifest, shards, proofs = build_generation(
            reversed(self.inputs["records"]), 0, self.inputs["context"],
            list(reversed(self.inputs["sources"])),
        )
        self.assertEqual(manifest, self.manifest)
        self.assertEqual(shards, self.shards)
        self.assertEqual(proofs, self.proofs)

    def test_all_sixteen_proofs_and_empty_shards(self):
        for number in range(16):
            shard = verify_shard(self.pin, self.current, self.shards[number], self.proofs[number])
            self.assertEqual(shard["shard"], number)
        self.assertTrue(any(item["items"] == 0 for item in self.manifest["shards"]))

    def test_empty_generation_is_explicit_complete_tree(self):
        manifest, shards, _proofs = build_generation([], 0, self.inputs["context"], [])
        self.assertEqual(len(shards), 16)
        self.assertEqual(manifest["total_items"], 0)
        self.assertEqual(len({entry["leaf_hash"] for entry in manifest["shards"]}), 16)

    def test_tampered_bytes_refused(self):
        number = shard_for("summon", "cedar")
        for raw in (self.shards[number] + b"\n", self.shards[number].replace(b"cedar", b"Cedar", 1)):
            with self.subTest(size=len(raw)), self.assertRaises(Refusal):
                verify_shard(self.pin, self.current, raw, self.proofs[number])

    def test_missing_or_substituted_proof_refused(self):
        for change in (None, {}, {**self.proofs[0], "siblings": self.proofs[0]["siblings"][:-1]},
                       {**self.proofs[0], "shard": 1}, {**self.proofs[0], "leaf_hash": "0" * 64}):
            with self.subTest(proof=change), self.assertRaises(Refusal):
                verify_shard(self.pin, self.current, self.shards[0], change)
        changed = copy.deepcopy(self.proofs[0])
        changed["siblings"][0] = "f" * 64
        with self.assertRaises(Refusal):
            verify_shard(self.pin, self.current, self.shards[0], changed)

    def test_domain_separation(self):
        item = self.manifest["shards"][0]
        self.assertNotEqual(item["sha256"], item["leaf_hash"])
        self.assertNotEqual(item["leaf_hash"], leaf_hash(1, item["sha256"], item["bytes"]))
        self.assertNotEqual(node_hash(item["sha256"], item["sha256"]), item["leaf_hash"])

    def test_manifest_root_totals_and_coverage_refuse(self):
        for field, value in (("root", "0" * 64), ("total_items", 0), ("total_bytes", 0)):
            with self.subTest(field=field), self.assertRaises(Refusal):
                validate_manifest({**self.manifest, field: value})
        changed = copy.deepcopy(self.manifest)
        changed["shards"][1] = changed["shards"][0]
        with self.assertRaises(Refusal):
            validate_manifest(changed)

    def test_duplicate_candidates_never_first_wins(self):
        with self.assertRaises(Refusal):
            build_generation(
                self.inputs["records"] + [self.inputs["records"][0]], 0,
                self.inputs["context"], self.inputs["sources"],
            )

    def test_source_substitution_and_duplicate_sources_refuse(self):
        record = dict(self.inputs["records"][0])
        for field in ("content_sha256", "particle_hash", "occurrence_hash", "rappid"):
            changed = {**record, field: "0" * 64 if field != "rappid" else self.inputs["records"][2]["rappid"]}
            with self.subTest(field=field), self.assertRaises(Refusal):
                build_generation([changed], 0, self.inputs["context"], self.inputs["sources"])
        with self.assertRaises(Refusal):
            build_generation([], 0, self.inputs["context"], self.inputs["sources"] * 2)

    def test_bounded_record_stream_consumption(self):
        consumed = []
        def records():
            for record in self.inputs["records"] * 1000:
                consumed.append(1)
                yield record
        with mock.patch("work_index.MAX_ITEMS", 2), self.assertRaises(Refusal):
            build_generation(records(), 0, self.inputs["context"], self.inputs["sources"])
        self.assertEqual(len(consumed), 3)

    def test_collision_bucket_and_shard_item_ceiling(self):
        records = []
        for index in range(20000):
            key = f"alias-{index}"
            if shard_for("catalog", key) == 0:
                records.append({**self.inputs["records"][0], "domain": "catalog", "key": key})
            if len(records) == 257:
                break
        self.assertEqual(len(records), 257)
        with self.assertRaises(Refusal):
            build_generation(records, 0, self.inputs["context"], self.inputs["sources"])

    def test_signed_root_does_not_excuse_noncanonical_record_order(self):
        number = shard_for("summon", "cedar")
        shard = parse(self.shards[number])
        shard["records"].reverse()
        raw = canonical(shard)
        manifest = copy.deepcopy(self.manifest)
        entry = manifest["shards"][number]
        entry.update(sha256=sha(raw), bytes=len(raw), leaf_hash=leaf_hash(number, sha(raw), len(raw)))
        manifest["root"] = tree_levels([item["leaf_hash"] for item in manifest["shards"]])[-1][0]
        pin = pin_for(manifest)
        with self.assertRaises(Refusal):
            verify_shard(pin, pin.frontier, raw, make_proofs(manifest)[number])


class CheckpointTests(FixtureCase):
    def test_exact_checkpoint_binding(self):
        binding = bind_checkpoint(self.manifest, receipt_double(self.manifest), self.inputs["context"])
        self.assertEqual(binding, fixture("checkpoint-0.binding.json"))
        self.assertEqual(checkpoint_payload(self.manifest), fixture("checkpoint-0.frame.json")["payload"])
        validate_checkpoint_binding(binding, self.manifest, receipt_double(self.manifest), self.inputs["context"])

    def test_stored_binding_cannot_substitute_occurrence(self):
        for field in ("payload_hash", "frame_hash", "frame_sha256"):
            binding = {**self.pin.binding, field: "0" * 64}
            with self.subTest(field=field), self.assertRaises(Refusal):
                validate_checkpoint_binding(binding, self.manifest, receipt_double(self.manifest), self.inputs["context"])

    def test_external_record_required(self):
        for field, value in (
            ("signature_verified", False), ("chain_verified", False), ("kind", "work.done"),
            ("verification", "self-asserted"), ("signer", self.inputs["records"][0]["rappid"]),
            ("spki_sha256", "0" * 64), ("stream", "another-stream"), ("key_epoch", 2),
            ("registry_epoch", 2),
        ):
            record = {**receipt_double(self.manifest), field: value}
            with self.subTest(field=field), self.assertRaises(Refusal):
                bind_checkpoint(self.manifest, record, self.inputs["context"])

    def test_manifest_and_policy_substitution_refused(self):
        for field in ("root", "manifest_sha256", "context_sha256", "source_vector_sha256"):
            record = receipt_double(self.manifest)
            record["payload"][field] = "0" * 64
            with self.subTest(field=field), self.assertRaises(Refusal):
                bind_checkpoint(self.manifest, record, self.inputs["context"])
        with self.assertRaises(Refusal):
            bind_checkpoint(self.manifest, receipt_double(self.manifest),
                            {**self.inputs["context"], "policy_root": "0" * 64})

    def test_pivot_reuses_shards_but_requires_new_signed_wave(self):
        manifest = fixture("generation-1.json")
        successor = pin_for(manifest, 1, self.pin)
        self.assertEqual(manifest["root"], self.manifest["root"])
        self.assertNotEqual(successor.binding["frame_hash"], self.pin.binding["frame_hash"])
        self.assertNotEqual(successor.fingerprint, self.pin.fingerprint)
        first, reused = fixture("source-00.frame.json"), fixture("source-06.frame.json")
        self.assertEqual(first["payload_hash"], reused["payload_hash"])
        self.assertNotEqual(first["frame_hash"], reused["frame_hash"])

    def test_rollback_and_same_sequence_fork_refuse(self):
        newer = pin_for(fixture("generation-1.json"), 1, self.pin)
        with self.assertRaisesRegex(Refusal, "rollback"):
            check_transition(newer.binding, self.pin.binding)
        for field in ("root", "manifest_sha256", "frame_hash", "frame_sha256"):
            with self.subTest(field=field), self.assertRaisesRegex(Refusal, "fork"):
                check_transition(self.pin.binding, {**self.pin.binding, field: "0" * 64})
        check_transition(self.pin.binding, self.pin.binding)

    def test_generation_reuse_key_rollback_stream_change_refuse(self):
        successor = pin_for(fixture("generation-1.json"), 1).binding
        for field, value in (("generation", 0), ("key_epoch", 0), ("registry_epoch", 0),
                             ("stream", "changed"), ("frame_hash", self.pin.binding["frame_hash"])):
            with self.subTest(field=field), self.assertRaises(Refusal):
                check_transition(self.pin.binding, {**successor, field: value})

    def test_pin_is_immutable_and_input_mutation_cannot_change_it(self):
        before = self.pin.fingerprint
        self.manifest["context"]["policy_root"] = "0" * 64
        exported = self.pin.manifest
        exported["generation"] = 4
        self.assertEqual(self.pin.fingerprint, before)
        self.assertEqual(self.pin.manifest["generation"], 0)
        with self.assertRaises(AttributeError):
            self.pin._manifest = b"{}"

    def test_all_cache_context_and_checkpoint_changes_invalidate(self):
        for field, value in self.current["context"].items():
            changed = copy.deepcopy(self.current)
            if isinstance(value, int):
                changed["context"][field] = value + 1
            elif field == "signer":
                changed["context"][field] = self.inputs["records"][0]["rappid"]
            elif field == "stream":
                changed["context"][field] = "changed"
            else:
                changed["context"][field] = "0" * 64
            with self.subTest(field=field), self.assertRaises(Refusal):
                cache_key(b"public", self.pin, changed)
        for field in ("manifest_sha256", "checkpoint_frame_hash", "checkpoint_frame_sha256"):
            with self.subTest(field=field), self.assertRaises(Refusal):
                cache_key(b"public", self.pin, {**self.current, field: "0" * 64})
        changed = copy.deepcopy(self.current)
        changed["source_vector"][0]["raw_sha256"] = "0" * 64
        with self.assertRaises(Refusal):
            cache_key(b"public", self.pin, changed)

    def test_frontier_schema_refuses_before_canonical_materialization(self):
        document = {"unexpected": ["\x00" * 4096] * 1024}
        with mock.patch(
            "common.json.dumps",
            side_effect=AssertionError("invalid frontier reached canonical encoding"),
        ), self.assertRaises(Refusal):
            self.pin.require_current(document)

    def test_raw_bytes_and_signed_pivot_change_cache_identity(self):
        self.assertNotEqual(cache_key(b"a", self.pin, self.current), cache_key(b"b", self.pin, self.current))
        successor = pin_for(fixture("generation-1.json"), 1)
        self.assertNotEqual(cache_key(b"a", self.pin, self.current),
                            cache_key(b"a", successor, successor.frontier))


class PaginationTests(DatabaseCase):
    def setUp(self):
        super().setUp()
        self.build()

    def test_exact_pages_preserve_every_full_candidate(self):
        expected = sorted(
            (item for item in self.inputs["records"] if item["domain"] == "summon"),
            key=candidate_order,
        )
        with self.open() as index:
            for size in (1, 2, 3, 64):
                token, actual = None, []
                while True:
                    page = index.page(self.current, "summon", "cedar", page_size=size, token=token)
                    self.assertIs(page["authority"], False)
                    actual.extend(page["records"])
                    token = page["continuation"]
                    if token is None:
                        break
                self.assertEqual(actual, expected)
                self.assertEqual(len({canonical(identity(item)) for item in actual}), 7)
        self.assertEqual(len({item["rappid"] for item in expected}), 6)

    def test_continuation_matches_golden_bytes(self):
        with self.open() as index:
            first = index.page(self.current, "summon", "cedar", page_size=2)
            self.assertEqual(first["continuation"], fixture("golden.json")["first_continuation"])
            self.assertEqual(first, index.page(self.current, "summon", "cedar", page_size=2))

    def test_case_sensitive_keys_and_domains(self):
        with self.open() as index:
            for domain, key in (("summon", "Cedar"), ("catalog", "cedar"), ("summon", "absent")):
                page = index.page(self.current, domain, key, page_size=2)
                self.assertEqual(page["records"], [])
                self.assertIsNone(page["continuation"])

    def test_token_tampering_and_wrong_binding_refuse(self):
        with self.open() as index:
            token = index.page(self.current, "summon", "cedar", page_size=2)["continuation"]
            for changed in (token + "=", token[:-4], "A" * (MAX_TOKEN_BYTES + 1), "", token[::-1]):
                with self.subTest(size=len(changed)), self.assertRaises(Refusal):
                    index.page(self.current, "summon", "cedar", page_size=2, token=changed)
            for domain, key, size in (("catalog", "cedar", 2), ("summon", "Cedar", 2), ("summon", "cedar", 3)):
                with self.subTest(query=(domain, key, size)), self.assertRaises(Refusal):
                    index.page(self.current, domain, key, page_size=size, token=token)

    def test_new_generation_even_same_root_invalidates_token(self):
        successor = pin_for(fixture("generation-1.json"), 1, self.pin)
        token = fixture("golden.json")["first_continuation"]
        with self.assertRaises(Refusal):
            decode_token(token, successor, "summon", "cedar", 2)

    def test_nonexistent_substituted_or_nonboundary_final_identity_refuses(self):
        expected = sorted(
            (item for item in self.inputs["records"] if item["domain"] == "summon"), key=candidate_order
        )
        invalid = [
            identity(expected[0]),
            {**identity(expected[1]), "occurrence_hash": "0" * 64},
            {**identity(expected[1]), "content_bytes": 0},
        ]
        with self.open() as index:
            for after in invalid:
                token = encode_token(self.pin, "summon", "cedar", after, 2)
                with self.subTest(after=after), self.assertRaises(Refusal):
                    index.page(self.current, "summon", "cedar", page_size=2, token=token)
            terminal = encode_token(self.pin, "summon", "cedar", identity(expected[-1]), 1)
            with self.assertRaises(Refusal):
                index.page(self.current, "summon", "cedar", page_size=1, token=terminal)

    def test_page_size_bounds(self):
        with self.open() as index:
            for size in (0, -1, True, 65, "2"):
                with self.subTest(size=size), self.assertRaises(Refusal):
                    index.page(self.current, "summon", "cedar", page_size=size)

    def test_summon_exact_identity_and_bytes_not_authority(self):
        record = self.inputs["records"][0]
        raw = read_file(FIXTURES / "source-00.content.json")
        with self.open() as index:
            result = index.summon(self.current, "summon", "cedar", identity(record), raw)
            self.assertEqual(result["candidate"], record)
            self.assertEqual(result["status"], "disambiguated-not-authorized")
            self.assertIs(result["authority"], False)
            for selected, content in (
                ({"rappid": record["rappid"]}, raw),
                (identity(record), read_file(FIXTURES / "source-01.content.json")),
                ({**identity(record), "rappid": self.inputs["records"][2]["rappid"]}, raw),
            ):
                with self.subTest(selected=selected), self.assertRaises(Refusal):
                    index.summon(self.current, "summon", "cedar", selected, content)

    def test_current_frontier_required_on_every_use(self):
        with self.open() as index:
            changed = copy.deepcopy(self.current)
            changed["context"]["revocation_root"] = "0" * 64
            with self.assertRaises(Refusal):
                index.page(changed, "summon", "cedar", page_size=2)
            with self.assertRaises(Refusal):
                index.summon(changed, "summon", "cedar", identity(self.inputs["records"][0]), b"")


class SQLiteTests(DatabaseCase):
    def mutate(self, statement, parameters=()):
        with closing(sqlite3.connect(self.path)) as connection:
            with connection:
                connection.execute(statement, parameters)

    def test_without_rowid_and_indexed_exact_query(self):
        self.build()
        with self.open() as index:
            connection = index._connection
            tables = connection.execute("SELECT sql FROM sqlite_master").fetchall()
            self.assertTrue(all("WITHOUT ROWID" in item[0] for item in tables))
            plan = connection.execute(
                "EXPLAIN QUERY PLAN SELECT raw FROM records WHERE domain=? AND key=? "
                "ORDER BY rappid,content_sha256,particle_hash,occurrence_hash LIMIT ?",
                ("summon", "cedar", 2),
            ).fetchall()
            self.assertTrue(any("PRIMARY KEY" in entry[3] and "SEARCH" in entry[3] for entry in plan))

    def test_exact_lookup_retains_all_candidates(self):
        self.build()
        with self.open() as index:
            result = index.lookup(self.current, "summon", "cedar")
            self.assertEqual(len(result["records"]), 7)
            self.assertIs(result["authority"], False)
            self.assertEqual(index.lookup(self.current, "summon", "Cedar")["records"], [])

    def test_missing_database_refuses_no_creation(self):
        with self.assertRaises(Refusal):
            self.open()
        self.assertFalse(self.path.exists())

    def test_deleted_candidate_cannot_silently_win(self):
        self.build()
        self.mutate("DELETE FROM records WHERE raw=(SELECT raw FROM records LIMIT 1)")
        with self.assertRaises(Refusal):
            self.open()

    def test_corrupt_or_substituted_record_refuses(self):
        self.build()
        self.mutate("UPDATE records SET raw=?", (b"{}",))
        with self.assertRaises(Refusal):
            self.open()

    def test_missing_shard_refuses(self):
        self.build()
        self.mutate("DELETE FROM shards WHERE shard=0")
        with self.assertRaises(Refusal):
            self.open()

    def test_corrupt_proof_refuses(self):
        self.build()
        self.mutate("UPDATE shards SET proof=? WHERE shard=0", (b"{}",))
        with self.assertRaises(Refusal):
            self.open()

    def test_metadata_substitution_refuses(self):
        self.build()
        self.mutate("UPDATE metadata SET value=? WHERE key='binding'", (b"{}",))
        with self.assertRaises(Refusal):
            self.open()

    def test_extra_trigger_refuses(self):
        self.build()
        self.mutate("CREATE TRIGGER unexpected AFTER INSERT ON records BEGIN SELECT 1; END")
        with self.assertRaises(Refusal):
            self.open()

    def test_arbitrary_corruption_and_disk_ceiling_refuse(self):
        write_file(self.path, b"not a SQLite database")
        with self.assertRaises(Refusal):
            self.open()
        with self.path.open("wb") as stream:
            stream.truncate(MAX_DB_BYTES + 1)
        with self.assertRaises(Refusal):
            self.open()

    def test_other_generation_cache_refuses_even_same_root(self):
        self.build()
        newer = pin_for(fixture("generation-1.json"), 1)
        with self.assertRaises(Refusal):
            ExactIndex(self.path, newer, newer.frontier)

    def test_existing_database_cannot_be_overwritten(self):
        self.build()
        before = read_file(self.path, MAX_DB_BYTES)
        with self.assertRaises(Refusal):
            self.build()
        self.assertEqual(read_file(self.path, MAX_DB_BYTES), before)

    def test_incomplete_duplicate_or_corrupt_input_creates_no_database(self):
        for pairs in (self.pairs()[:-1], self.pairs() + [self.pairs()[0]],
                      [(b"{}", self.proofs[0])] + self.pairs()[1:]):
            with self.subTest(count=len(pairs)), self.assertRaises(Refusal):
                ExactIndex.build(self.path, self.pin, self.current, pairs)
            self.assertFalse(self.path.exists())

    def test_operation_budget_and_closed_snapshot_refuse(self):
        self.build()
        with self.open(operation_limit=1) as index:
            index.page(self.current, "summon", "cedar", page_size=2)
            with self.assertRaises(Refusal):
                index.page(self.current, "summon", "cedar", page_size=2)
        with self.assertRaises(Refusal):
            index.page(self.current, "summon", "cedar", page_size=2)

    def test_path_escape_symlink_hardlink_fifo_refuse(self):
        for path in (self.path.absolute(), self.owned / ".." / "index.sqlite3"):
            with self.subTest(path=path), self.assertRaises(Refusal):
                ExactIndex.build(path, self.pin, self.current, self.pairs())
        original = self.owned / "public.json"
        write_file(original, b"{}")
        linked = self.owned / "linked.json"
        linked.symlink_to("public.json")
        with self.assertRaises(Refusal):
            read_file(linked)
        linked.unlink()
        os.link(original, linked)
        with self.assertRaises(Refusal):
            read_file(linked)
        fifo = self.owned / "pipe"
        os.mkfifo(fifo)
        with self.assertRaises(Refusal):
            read_file(fifo)

    def test_sidecar_never_automatically_recovers_or_reads(self):
        self.build()
        for suffix in ("-wal", "-shm", "-journal"):
            sidecar = self.path.with_name(self.path.name + suffix)
            write_file(sidecar, b"untrusted")
            with self.subTest(suffix=suffix), self.assertRaises(Refusal):
                self.open()
            sidecar.unlink()


class AntiEntropyTests(FixtureCase):
    def test_equal_manifest_reports_only_untrusted_available_bytes(self):
        result = anti_entropy(self.pin, self.pin, self.current, self.current, self.shards)
        self.assertEqual(result["missing"], [])
        self.assertEqual(result["divergent"], [])
        self.assertEqual(result["changed"], [])
        self.assertEqual(len(result["available_needs_proof"]), 16)
        self.assertIs(result["authority"], False)

    def test_exact_missing_and_corrupt_hash_reports(self):
        supplied = dict(self.shards)
        del supplied[0]
        supplied[1] = b"corrupt"
        result = anti_entropy(self.pin, self.pin, self.current, self.current, supplied)
        self.assertEqual(result["missing"], [{"shard": 0, "target_sha256": sha(self.shards[0])}])
        self.assertEqual(result["divergent"], [{
            "shard": 1, "local_sha256": sha(self.shards[1]),
            "observed_sha256": sha(b"corrupt"), "target_sha256": sha(self.shards[1]),
        }])

    def test_changed_manifest_reports_all_exact_hashes(self):
        records = copy.deepcopy(self.inputs["records"])
        records[0]["key"] = "changed"
        manifest, shards, proofs = build_generation(
            records, 1, self.inputs["pivot_context"], self.inputs["sources"],
        )
        target = pin_for(manifest, 1, self.pin)
        result = anti_entropy(self.pin, target, self.current, target.frontier, self.shards)
        changed = [i for i in range(16) if self.shards[i] != shards[i]]
        self.assertTrue(changed)
        self.assertEqual([item["shard"] for item in result["changed"]], changed)
        self.assertEqual([item["shard"] for item in result["divergent"]], changed)
        for i in changed:
            self.assertEqual(accept_shard(target, target.frontier, shards[i], proofs[i]), shards[i])
            with self.assertRaises(Refusal):
                accept_shard(target, target.frontier, self.shards[i], self.proofs[i])

    def test_reused_shard_requires_proof_for_new_generation(self):
        target = pin_for(fixture("generation-1.json"), 1, self.pin)
        self.assertEqual(anti_entropy(self.pin, target, self.current, target.frontier, {})["changed"], [])
        with self.assertRaises(Refusal):
            accept_shard(target, target.frontier, self.shards[0], self.proofs[0])
        accept_shard(target, target.frontier, self.shards[0], fixture("proofs-1.json")[0])

    def test_rollback_fork_and_unbounded_inventory_refuse(self):
        target = pin_for(fixture("generation-1.json"), 1, self.pin)
        with self.assertRaises(Refusal):
            anti_entropy(target, self.pin, target.frontier, self.current, {})
        changed = copy.deepcopy(self.inputs["records"])
        changed[0]["key"] = "fork"
        manifest, _, _ = build_generation(changed, 0, self.inputs["context"], self.inputs["sources"])
        fork = pin_for(manifest)
        with self.assertRaises(Refusal):
            anti_entropy(self.pin, fork, self.current, fork.frontier, {})
        for inventory in ({16: b""}, {True: b""}, {0: b"x" * (MAX_SHARD_BYTES + 1)}):
            with self.subTest(count=len(inventory)), self.assertRaises(Refusal):
                anti_entropy(self.pin, self.pin, self.current, self.current, inventory)

    def test_platform_descriptors_never_change_verification(self):
        adapters = platform_adapters()
        self.assertEqual([item["name"] for item in adapters], ["posix-sqlite", "windows-sqlite", "browser"])
        for adapter in adapters:
            self.assertEqual(adapter["resident_processes"], 0)
            self.assertFalse(adapter["network"] or adapter["polling"] or adapter["authority"])
            self.assertEqual(adapter["verification"], "identical-canonical-shards-and-external-checkpoint")
        self.assertEqual([item["status"] for item in adapters], ["reference", "mapping-only", "mapping-only"])


if __name__ == "__main__":
    unittest.main()
