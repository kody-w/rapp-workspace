"""Blocking synthetic regressions for trusted time, activation, binding truth and bounded DAG work."""

from contextlib import contextmanager
import copy
from dataclasses import replace
import unittest
from unittest.mock import Mock, patch
import uuid

from test_safe_kernel import CONTRACT, NOW, FixtureClock, KernelFixture, catalog_snapshot, organization_tiles
from common import Refusal, address, sha
from composite_work import CompositeWork
from safe_kernel import COMPOSITE_LIMITS, Controller
from schema_source import PROFILE


class ActivationTrust:
    """An independently installed exact allowlist, not reference cryptography."""

    def __init__(self, document):
        self.allowed = copy.deepcopy(document)
        self.revoked = False
        self.calls = []

    def __call__(self, document, now):
        self.calls.append((copy.deepcopy(document), now))
        return document == self.allowed and not self.revoked


class P0HardeningTests(KernelFixture):
    def activation_document(self):
        return {
            "schema": PROFILE + "/activation-document", "spec_id": PROFILE,
            "spec_sha256": self.policy.spec_sha256, "runtime_sha256": self.policy.runtime_sha256,
            "instance_rappid": self.policy.instance_rappid, "world_id": self.policy.world_id,
            "not_before_utc": "2026-09-15T00:00:00.000Z",
            "expires_utc": "2026-10-01T00:00:00.000Z",
            "signer_key_id": "synthetic-independent-host-key", "revocation_status": "active",
        }

    def controller(self, name, **options):
        options.setdefault("clock", self.clock)
        options.setdefault("activation_mode", "synthetic")
        controller = Controller(self.core, self.root / name, self.policy, **options)
        self.addCleanup(controller.close)
        return controller

    def live_controller(self, name="live"):
        document = self.activation_document()
        trust = ActivationTrust(document)
        controller = self.controller(name, activation_mode="live", activation=document, verify_activation=trust)
        return controller, trust

    def organization(self, count=4, *, metadata=None, inherited=()):
        entries = [{
            "id": f"workspace:{index:03d}", "kind": "local-workspace", "parent": "synthetic-root",
            "labels": ["workspace"], "metadata_sha256": sha(metadata[index] if metadata else str(index).encode()),
            "share_class": "private-source",
        } for index in range(count)]
        document = {
            "schema": "rapp-workspace/catalog-chunk/1", "catalog_id": "synthetic-catalog",
            "root_id": "synthetic-root", "shard_index": 0, "shard_count": 1,
            "snapshot_sha256": catalog_snapshot(entries), "branch_scope": "not-applicable",
            "branch_evidence_status": "not-applicable", "recursive": True, "entries": entries,
        }
        source = self.c.capture_octets(
            self.scope.subject(), self.core.octets(document), inherited=inherited)["source"]
        shard = self.c.register_catalog_shard(self.scope.subject(), source)
        tree = organization_tiles(
            "synthetic-catalog", [{"id": "root", "name": "Synthetic", "parent": None}],
            [{"entry_id": entry["id"], "group_id": "root"} for entry in entries])[0]
        tree_source = self.c.capture_octets(self.scope.subject(), self.core.octets(tree))["source"]
        assessment = self.c.assess_organization(
            self.scope.subject(), [shard], tree_source, max_bucket=count, allowed_depth=4)
        return assessment, entries

    def wrap(self, assessment, name, selected=(), children=()):
        return self.c.compose_workspace(self.scope.subject(), assessment, name, list(selected), children)

    def binding_fixture(self):
        with patch.object(self.core.r.uuid, "uuid4", return_value=uuid.UUID(int=191002, version=4)):
            child = self.core.r.mint_rappid("fictional", "child-instance")
        metadata = self.core.octets({
            "entry_id": "workspace:000", "rappid": child, "world_id": "child-world",
            "source": "synthetic-metadata-only",
        })
        claim = {"entry_id": "workspace:000", "child_rappid": child, "child_world_id": "child-world",
                 "source_metadata_sha256": sha(metadata)}
        verifier = Mock(side_effect=lambda proposed, raw: proposed == claim and raw == metadata)
        self.c = self.controller("binding-controller", verify_workspace_binding=verifier)
        self.c.seed(self.scope.subject())
        assessment, entries = self.organization(2, metadata=[metadata, b"unknown-metadata"])
        return assessment, entries, metadata, claim, verifier

    def register_binding(self, assessment, metadata, claim):
        return self.c.register_workspace_binding(
            self.scope.subject(), assessment, claim["entry_id"],
            child_rappid=claim["child_rappid"], child_world_id=claim["child_world_id"], metadata=metadata)

    @contextmanager
    def corrupt_store(self):
        self.c.db.execute("SAVEPOINT synthetic_corruption")
        try:
            yield
        finally:
            self.c.db.execute("ROLLBACK TO synthetic_corruption")
            self.c.db.execute("RELEASE synthetic_corruption")

    def test_long_lived_controller_samples_clock_at_every_authorization_boundary(self):
        cap, result, fidelity, request, frontier = self.ready()
        lens = self.c.body(result["frame"])["lens"]
        subject = self.scope.subject()
        frames = self.c.checkpoint()["frames"]
        methods = {
            "capture_file": lambda: self.c.capture_file(subject, self.source),
            "capture_octets": lambda: self.c.capture_octets(subject, object()),
            "synthesize": lambda: self.c.synthesize(subject, cap["source"]),
            "execute": lambda: self.c.execute(subject, lens),
            "fidelity": lambda: self.c.fidelity(subject, result["frame"], CONTRACT),
            "verify_derivation": lambda: self.c.verify_derivation(result["frame"]),
            "verify_current_receipt": lambda: self.c.verify_receipt(
                fidelity, "semantic_fidelity", result["frame"], current=True),
            "request_adoption": lambda: self.c.request_adoption(
                subject, result["frame"], fidelity, CONTRACT, "expired",
                integrity=result["rapp_integrity"], observation=cap["observation"]),
            "adopt": lambda: self.c.adopt(subject, request, frontier),
            "materialize": lambda: self.c.materialize(subject),
            "export": lambda: self.c.export_frames(self.c.path / "expired-export"),
            "projection": self.c.projection,
            "approve_contract": lambda: self.c.approve_contract(CONTRACT),
            "update_policy": lambda: self.c.update_policy(replace(self.policy, sequence=2)),
            "emit": lambda: self.c.emit(self.c.body(result["frame"])),
            "authorization_receipt": lambda: self.c.authorization_receipt(subject, result["frame"], "adoption"),
            "deployment_receipt": lambda: self.c.deployment_receipt(subject, result["frame"]),
            "suppress": lambda: self.c.suppress(subject),
            "qualify": self.c.qualify,
            "catalog": lambda: self.c.register_catalog_shard(subject, cap["source"]),
            "organization": lambda: self.c.assess_organization(subject, [], cap["source"], max_bucket=1, allowed_depth=1),
            "compose": lambda: self.c.compose_workspace(subject, result["frame"], "expired", []),
            "binding": lambda: self.c.register_workspace_binding(
                subject, result["frame"], "unknown", child_rappid=None, child_world_id=None, metadata=object()),
        }
        self.clock.value = self.policy.expires_utc
        for name, method in methods.items():
            calls = self.clock.calls
            with self.subTest(boundary=name), patch("safe_kernel.read_file", side_effect=AssertionError("source IO")), \
                    patch("safe_kernel.unb64", side_effect=AssertionError("source decoding")):
                with self.assertRaisesRegex(Refusal, "current-authorization-expired"):
                    method()
            self.assertGreater(self.clock.calls, calls)
        self.assertEqual(self.c.checkpoint()["frames"], frames)
        self.assertFalse((self.c.path / "view.json").exists())

    def test_default_host_clock_is_resampled_and_fixture_time_is_not_settable(self):
        clock = FixtureClock()
        with patch("safe_kernel.host_utc_now", clock):
            controller = Controller(self.core, self.root / "default-clock", self.policy, activation_mode="synthetic")
        self.addCleanup(controller.close)
        controller.seed(self.scope.subject())
        calls = clock.calls
        clock.value = self.policy.expires_utc
        with self.assertRaisesRegex(Refusal, "expired"):
            controller.capture_file(self.scope.subject(), self.source)
        self.assertGreater(clock.calls, calls)
        with self.assertRaises(AttributeError):
            controller.now = NOW
        with self.assertRaisesRegex(Refusal, "clock-callback-required"):
            self.controller("scalar-clock", clock=NOW)
        self.assertFalse((self.root / "scalar-clock").exists())

    def test_clock_domain_and_callback_failures_refuse(self):
        for value in (None, 1, {}, "2026-99-15T03:12:29.000Z", "2026-09-15T03:12:29+00:00"):
            self.clock.value = value
            with self.subTest(value=value), self.assertRaisesRegex(Refusal, "clock-domain"):
                self.c.guard(self.scope.subject(), "capture")
        with patch.object(self.c, "_clock", side_effect=RuntimeError("clock failed")):
            with self.assertRaisesRegex(Refusal, "clock-unavailable"):
                self.c.guard(self.scope.subject(), "capture")

    def test_read_only_clock_floor_is_durable_and_reopen_cannot_rewind(self):
        _, _, _, request, frontier = self.ready()
        self.c.adopt(self.scope.subject(), request, frontier)
        self.clock.value = "2026-09-15T03:12:30.000Z"
        self.c.materialize(self.scope.subject())
        checkpoint = self.c.checkpoint()
        self.assertEqual(checkpoint["clock_floor"], self.clock.value)
        self.c.close()
        with self.assertRaisesRegex(Refusal, "clock-rollback"):
            Controller(self.core, self.root / "controller", self.policy,
                       clock=lambda: NOW, activation_mode="synthetic")
        self.c = self.controller("controller", checkpoint=checkpoint)
        self.assertEqual(self.c.checkpoint(), checkpoint)

    def test_clock_storage_failure_cannot_rewind_in_process_high_water_mark(self):
        self.clock.value = "2026-09-15T03:12:30.000Z"
        with patch.object(self.c, "_put", side_effect=OSError("synthetic storage failure")), \
                self.assertRaises(OSError):
            self.c.guard(self.scope.subject(), "capture")
        self.clock.value = NOW
        with self.assertRaisesRegex(Refusal, "clock-rollback"):
            self.c.guard(self.scope.subject(), "capture")

    def test_expiry_before_adoption_commit_rolls_back_work_but_not_time(self):
        _, _, _, request, frontier = self.ready()
        before = self.c.checkpoint()
        def expire(stage):
            if stage == "before-commit":
                self.clock.value = self.policy.expires_utc
        with self.assertRaisesRegex(Refusal, "expired"):
            self.c.adopt(self.scope.subject(), request, frontier, fault=expire)
        after = self.c.checkpoint()
        self.assertEqual(after["frames"], before["frames"])
        self.assertEqual(after["adoptions"], [])
        self.assertEqual(after["clock_floor"], self.policy.expires_utc)
        self.assertEqual(self.c.verify_history()["current_authorization"], "not-inferred")
        self.c.close()
        with self.assertRaisesRegex(Refusal, "clock-rollback"):
            Controller(self.core, self.root / "controller", self.policy,
                       clock=lambda: NOW, activation_mode="synthetic")

    def test_materialization_rechecks_time_after_projection_before_write(self):
        _, _, _, request, frontier = self.ready()
        self.c.adopt(self.scope.subject(), request, frontier)
        projection = self.c.projection()
        def expire():
            self.clock.value = self.policy.expires_utc
            return projection
        with patch.object(self.c, "projection", side_effect=expire), \
                patch("safe_kernel.write_file", side_effect=AssertionError("expired output")):
            with self.assertRaisesRegex(Refusal, "expired"):
                self.c.materialize(self.scope.subject())

    def test_export_rechecks_time_before_each_output_file(self):
        self.candidate()
        from safe_kernel import write_file
        def expire_after_identity(path, raw, **options):
            self.assertEqual(path.name, "rappid.json")
            write_file(path, raw, **options)
            self.clock.value = self.policy.expires_utc
        with patch("safe_kernel.write_file", side_effect=expire_after_identity), \
                self.assertRaisesRegex(Refusal, "expired"):
            self.c.export_frames(self.c.path / "expiring-export")
        self.assertTrue((self.c.path / "expiring-export/rappid.json").exists())
        self.assertFalse((self.c.path / "expiring-export/frames").exists())

    def test_live_controller_refuses_recomputed_local_hashes_without_external_activation(self):
        for options in ({}, {"activation": self.activation_document()},
                        {"activation": self.activation_document(), "verify_activation": True}):
            with self.subTest(options=options), self.assertRaisesRegex(Refusal, "requires-authenticated-activation"):
                Controller(self.core, self.root / "no-activation", self.policy, clock=self.clock, **options)
        self.assertFalse((self.root / "no-activation").exists())
        for verdict in (False, None, 1, {"verified": True}):
            with self.subTest(verdict=verdict), self.assertRaisesRegex(Refusal, "not-independently-authenticated"):
                self.controller("untrusted", activation_mode="live", activation=self.activation_document(),
                                verify_activation=lambda doc, now: verdict)
        self.assertFalse((self.root / "untrusted").exists())

    def test_activation_binds_exact_pins_identity_world_validity_signer_and_revocation(self):
        document = self.activation_document()
        trust = ActivationTrust(document)
        changes = {
            "spec_sha256": "0" * 64, "runtime_sha256": "0" * 64,
            "instance_rappid": self.policy.instance_rappid.replace("/safe-instance:", "/another-instance:"),
            "world_id": "another-world", "not_before_utc": "2027-01-01T00:00:00.000Z",
            "expires_utc": NOW, "signer_key_id": "unknown-key", "revocation_status": "revoked",
        }
        for field, value in changes.items():
            with self.subTest(field=field), self.assertRaises(Refusal):
                self.controller("wrong-activation", activation_mode="live",
                                activation={**document, field: value}, verify_activation=trust)
            self.assertFalse((self.root / "wrong-activation").exists())
        for change in ({"spec_id": "rapp-workspace/grail-1.0"}, {"owner": True},
                       {"not_before_utc": "2026-02-30T00:00:00.000Z"}):
            with self.subTest(change=change), self.assertRaises(Refusal):
                self.controller("malformed-activation", activation_mode="live",
                                activation={**document, **change}, verify_activation=lambda doc, now: True)

    def test_live_activation_is_reauthenticated_at_each_boundary_and_revocation_refuses(self):
        self.c, trust = self.live_controller()
        self.c.seed(self.scope.subject())
        _, _, _, request, frontier = self.ready()
        self.c.adopt(self.scope.subject(), request, frontier)
        self.assertEqual(self.c._head()["payload"]["activation_mode"], "live")
        self.assertGreater(len(trust.calls), 20)
        self.assertTrue(all(document == trust.allowed and now == NOW for document, now in trust.calls))
        trust.revoked = True
        frames = self.c.checkpoint()["frames"]
        for method in (lambda: self.c.capture_file(self.scope.subject(), self.source),
                       lambda: self.c.adopt(self.scope.subject(), request, frontier),
                       lambda: self.c.approve_contract(CONTRACT),
                       lambda: self.c.update_policy(replace(self.policy, sequence=2)),
                       lambda: self.c.materialize(self.scope.subject())):
            with patch("safe_kernel.read_file", side_effect=AssertionError("revoked IO")), \
                    self.assertRaisesRegex(Refusal, "not-independently-authenticated"):
                method()
        self.assertEqual(self.c.checkpoint()["frames"], frames)
        self.assertEqual(self.c.verify_history()["activation"], "historical-host-binding-only")

    def test_activation_expiry_is_independent_of_policy_expiry(self):
        self.c, trust = self.live_controller()
        self.c.seed(self.scope.subject())
        self.clock.value = trust.allowed["expires_utc"]
        self.assertLess(self.clock.value, self.policy.expires_utc)
        with patch("safe_kernel.read_file", side_effect=AssertionError("expired IO")), \
                self.assertRaisesRegex(Refusal, "activation-not-current"):
            self.c.capture_file(self.scope.subject(), self.source)

    def test_activation_hook_errors_and_mutation_cannot_supply_data_authority(self):
        document = self.activation_document()
        with self.assertRaisesRegex(Refusal, "activation-verifier-refused"):
            self.controller("hook-error", activation_mode="live", activation=document,
                            verify_activation=Mock(side_effect=RuntimeError("external verifier unavailable")))
        trust = ActivationTrust(document)
        controller = self.controller("immutable-activation", activation_mode="live",
                                     activation=document, verify_activation=trust)
        document["world_id"] = "mutated-caller-object"
        controller.seed(self.scope.subject())
        self.assertEqual(controller._get("activation")["document"], trust.allowed)
        with self.assertRaisesRegex(Refusal, "must-not-ignore-live-document"):
            self.controller("ignored-live-document", activation=document)

    def test_synthetic_live_reopen_cannot_silently_promote_or_downgrade(self):
        self.c.close()
        document = self.activation_document()
        with self.assertRaisesRegex(Refusal, "activation-recovery-quarantine"):
            self.controller("controller", activation_mode="live", activation=document,
                            verify_activation=ActivationTrust(document))
        live, _ = self.live_controller()
        live.seed(self.scope.subject())
        live.close()
        with self.assertRaisesRegex(Refusal, "activation-recovery-quarantine"):
            self.controller("live")

    def test_synthetic_labels_survive_receipts_and_data_cannot_claim_live_activation(self):
        cap, _, result = self.candidate(self.core.octets(self.activation_document()))
        for reference in (cap["source"], cap["observation"], result["frame"], result["rapp_integrity"]):
            self.assertEqual(self.c.body(reference)["activation_mode"], "synthetic")
        self.assertEqual(self.c.frontier()["activation_mode"], "synthetic")
        self.assertEqual(self.c.projection()["activation_mode"], "synthetic")
        forged = self.c.body(result["frame"])
        forged["activation_mode"] = "live"
        with self.assertRaisesRegex(Refusal, "activation-substitution"):
            self.c.emit(forged)

    def test_activation_and_clock_authority_state_recovery_is_fail_closed(self):
        for key, replacement in (("activation", None), ("activation", {"mode": "live", "document": None}),
                                 ("clock_floor", None), ("clock_floor", "2026-01-01T00:00:00.000Z")):
            with self.subTest(key=key, replacement=replacement), self.corrupt_store():
                if replacement is None:
                    self.c.db.execute("DELETE FROM meta WHERE key=?", (key,))
                else:
                    self.c._put(key, replacement)
                with self.assertRaisesRegex(Refusal, "recovery-quarantine"):
                    self.c.verify_history()
        self.c.db.execute("DELETE FROM meta WHERE key='activation'")
        self.c.close()
        with self.assertRaisesRegex(Refusal, "activation-recovery-quarantine"):
            self.controller("controller")

    def test_unknown_child_metadata_is_reference_only_not_identity_or_world_proof(self):
        raw = b'{"owner":true,"rappid":"unverified","world_id":"unverified","activation_mode":"live"}'
        assessment, entries = self.organization(2, metadata=[raw, b"unknown"])
        leaf = self.wrap(assessment, "leaf", [entry["id"] for entry in entries])
        wrapper = self.wrap(assessment, "wrapper", children=[leaf])
        for reference in (leaf, wrapper):
            payload = self.c.body(reference)
            self.assertNotIn("child_identities_preserved", payload)
            self.assertNotIn("child_worlds_preserved", payload)
            self.assertEqual(payload["child_identity_status"], "preserved-by-reference-unverified")
            self.assertEqual(payload["child_world_status"], "preserved-by-reference-unverified")
            self.assertEqual(payload["verified_binding_count"], 0)
            self.assertEqual(payload["unverified_binding_count"], 2)
            self.assertFalse(payload["content_copied"])
            self.assertFalse(payload["grants_authority"])
        for value, entry in zip(self.c.body(leaf)["workspace_bindings"], entries):
            self.assertEqual(value["entry_id"], entry["id"])
            self.assertEqual(value["source_metadata_sha256"], entry["metadata_sha256"])
            self.assertIsNone(value["child_rappid"])
            self.assertIsNone(value["child_world_id"])
            self.assertIsNone(value["evidence"])
        self.assertEqual(self.source.read_bytes(), b"PUBLIC SYNTHETIC INPUT")

    def test_verified_workspace_binding_has_exact_metadata_evidence_but_no_capabilities(self):
        assessment, entries, metadata, claim, verifier = self.binding_fixture()
        reference = self.register_binding(assessment, metadata, claim)
        self.assertEqual(self.register_binding(assessment, metadata, claim), reference)
        leaf = self.wrap(assessment, "verified", [entries[0]["id"]])
        parent = self.wrap(assessment, "verified-parent", children=[leaf])
        mixed = self.wrap(assessment, "mixed", [entries[1]["id"]], [parent])
        value = self.c.body(leaf)["workspace_bindings"][0]
        self.assertEqual(value["evidence"], reference)
        self.assertEqual(value["child_rappid"], claim["child_rappid"])
        self.assertEqual(value["child_world_id"], claim["child_world_id"])
        self.assertEqual(self.c.body(parent)["child_identity_status"], "verified-external-bindings")
        self.assertEqual(self.c.body(parent)["child_world_status"], "verified-external-bindings")
        self.assertEqual(self.c.body(parent)["bindings_sha256"], self.c.body(leaf)["bindings_sha256"])
        self.assertEqual(self.c.body(mixed)["child_identity_status"], "preserved-by-reference-unverified")
        self.assertEqual(self.c.body(mixed)["verified_binding_count"], 1)
        self.assertEqual(self.c.body(mixed)["unverified_binding_count"], 1)
        self.assertEqual(self.c.policy.instance_rappid, self.policy.instance_rappid)
        self.assertEqual(self.c.policy.world_id, self.policy.world_id)
        self.assertEqual(self.c.projection()["entries"], [])
        with self.assertRaisesRegex(Refusal, "outside-explicit"):
            self.c.guard({"namespace": "child", "native_key": claim["child_rappid"]}, "capture")
        with self.assertRaisesRegex(Refusal, "disabled"):
            self.c.require_effect(self.scope.subject(), "execution")
        self.assertGreaterEqual(verifier.call_count, 2)
        self.assertEqual(self.c.verify_history()["workspace_bindings"], "historical-evidence-only")

    def test_binding_verification_requires_exact_bytes_independent_hook_and_complete_claim(self):
        assessment, _, metadata, claim, verifier = self.binding_fixture()
        before = self.c.checkpoint()
        with self.assertRaisesRegex(Refusal, "metadata-mismatch"):
            self.register_binding(assessment, metadata + b"changed", claim)
        verifier.assert_not_called()
        for verdict in (False, 1, {"verified": True}):
            verifier.side_effect = None
            verifier.return_value = verdict
            with self.subTest(verdict=verdict), self.assertRaisesRegex(Refusal, "not-independently-verified"):
                self.register_binding(assessment, metadata, claim)
        for field in ("child_rappid", "child_world_id"):
            with self.subTest(field=field), self.assertRaises(Refusal):
                self.register_binding(assessment, metadata, {**claim, field: None})
        self.assertEqual(self.c.checkpoint(), before)

    def test_data_shaped_binding_and_claim_status_cannot_become_controller_evidence(self):
        assessment, entries, metadata, claim, _ = self.binding_fixture()
        reference = self.register_binding(assessment, metadata, claim)
        forged = self.c.body(reference)
        forged["child_world_id"] = "forged-world"
        forged["evidence"] = self.core.particle({**claim, "child_world_id": "forged-world"})
        fake = self.c.emit(forged)
        with self.assertRaisesRegex(Refusal, "controller-record-required"):
            self.c._binding_record(self.scope.subject(), fake, CompositeWork(self.c))
        leaf = self.wrap(assessment, "real-binding", [entries[0]["id"]])
        proposed = self.c.body(leaf)
        proposed["composite_id"] = "data-composite"
        proposed["workspace_bindings"][0].update(child_world_id="forged-world", evidence=fake)
        data = self.c.emit(proposed)
        with self.assertRaisesRegex(Refusal, "controller-record-required"):
            self.wrap(assessment, "cannot-promote", children=[data])
        closed = self.c.body(leaf)
        closed["workspace_bindings"][0]["owner"] = True
        with self.assertRaisesRegex(Refusal, "closed schema"):
            self.core.schemas.validate(closed)

    def test_binding_expiry_and_inherited_capture_denial_precede_persistence_or_hashing(self):
        assessment, _, metadata, claim, verifier = self.binding_fixture()
        before = self.c.checkpoint()["frames"]
        def expire(proposed, raw):
            self.clock.value = self.policy.expires_utc
            return True
        verifier.side_effect = expire
        with self.assertRaisesRegex(Refusal, "expired"):
            self.register_binding(assessment, metadata, claim)
        self.assertEqual(self.c.checkpoint()["frames"], before)
        self.assertEqual(self.c.db.execute("SELECT COUNT(*) FROM workspace_bindings").fetchone()[0], 0)

    def test_binding_metadata_is_not_hashed_without_inherited_capture_right(self):
        metadata = b"must-not-hash-new-metadata"
        self.c = self.controller("restricted-binding", verify_workspace_binding=lambda proposed, raw: True)
        self.c.seed(self.scope.subject())
        assessment, _ = self.organization(1, metadata=[metadata])
        self.c.update_policy(replace(self.policy, sequence=2, rights=self.policy.rights - {"capture"}))
        with patch("safe_kernel.sha", side_effect=AssertionError("unauthorized metadata hash")), \
                self.assertRaisesRegex(Refusal, "capability-denied:capture"):
            self.c.register_workspace_binding(
                self.scope.subject(), assessment, "workspace:000", child_rappid=self.policy.instance_rappid,
                child_world_id="world", metadata=metadata)

    def test_workspace_binding_requires_host_hook_and_changed_identity_conflicts(self):
        assessment, entries = self.organization(1)
        with self.assertRaisesRegex(Refusal, "verifier-required"):
            self.c.register_workspace_binding(
                self.scope.subject(), assessment, entries[0]["id"], child_rappid=self.policy.instance_rappid,
                child_world_id="world", metadata=b"0")
        assessment, _, metadata, claim, verifier = self.binding_fixture()
        self.register_binding(assessment, metadata, claim)
        verifier.side_effect = lambda proposed, raw: True
        with self.assertRaisesRegex(Refusal, "idempotency-conflict"):
            self.register_binding(assessment, metadata, {**claim, "child_world_id": "changed"})

    def test_new_controller_owned_record_tables_and_registries_recover_together(self):
        assessment, entries, metadata, claim, _ = self.binding_fixture()
        binding = self.register_binding(assessment, metadata, claim)
        self.wrap(assessment, "owned", [entries[0]["id"]])
        changes = [
            ("DELETE FROM workspace_bindings", ()),
            ("UPDATE workspace_bindings SET metadata_sha256=?", ("0" * 64,)),
            ("UPDATE workspace_bindings SET entry_id=?", ("workspace:other",)),
            ("UPDATE workspace_bindings SET assessment=?", (address(binding),)),
            ("DELETE FROM meta WHERE key='binding_records'", ()),
            ("DELETE FROM composites", ()),
            ("UPDATE composites SET composite_id='changed'", ()),
            ("DELETE FROM meta WHERE key='composite_records'", ()),
            ("DELETE FROM assessments", ()),
            ("DELETE FROM meta WHERE key='assessment_records'", ()),
            ("INSERT INTO workspace_bindings VALUES (?,?,?,?)",
             ("f" * 64, address(assessment), "workspace:injected", "f" * 64)),
        ]
        for sql, parameters in changes:
            with self.subTest(sql=sql), self.corrupt_store():
                self.c.db.execute(sql, parameters)
                with self.assertRaises(Refusal):
                    self.c.verify_history()
        self.c.db.execute("DELETE FROM workspace_bindings")
        self.c.close()
        with self.assertRaisesRegex(Refusal, "recovery-quarantine"):
            self.controller("binding-controller")

    def test_checkpoint_detects_binding_composite_and_assessment_rollback(self):
        assessment, entries, metadata, claim, _ = self.binding_fixture()
        self.register_binding(assessment, metadata, claim)
        self.wrap(assessment, "checkpointed", [entries[0]["id"]])
        checkpoint = self.c.checkpoint()
        for table in ("workspace_bindings", "composites", "assessments"):
            with self.subTest(table=table), self.corrupt_store():
                self.c.db.execute("DELETE FROM " + table)
                with self.assertRaisesRegex(Refusal, "checkpoint-rollback"):
                    self.c.check_checkpoint(checkpoint)

    def test_wide_composite_preflights_aggregate_nodes_before_reading_children(self):
        assessment, entries = self.organization(12)
        children = [self.wrap(assessment, f"leaf-{index}", [entry["id"]]) for index, entry in enumerate(entries)]
        self.c.update_policy(replace(self.policy, sequence=2, max_composite_nodes=5))
        before = self.c.checkpoint()
        with patch.object(CompositeWork, "body", side_effect=AssertionError("descended before node budget")), \
                self.assertRaisesRegex(Refusal, "node-budget"):
            self.wrap(assessment, "too-wide", children=children)
        self.assertEqual(self.c.checkpoint(), before)

    def test_edge_budget_is_shared_across_sibling_subtrees(self):
        assessment, entries = self.organization(8)
        leaves = [self.wrap(assessment, f"leaf-{index}", [entry["id"]]) for index, entry in enumerate(entries)]
        branches = [self.wrap(assessment, f"branch-{index}", children=leaves[index:index + 2])
                    for index in range(0, 8, 2)]
        self.c.update_policy(replace(self.policy, sequence=2, max_composite_edges=6))
        before = self.c.checkpoint()
        for _ in range(2):
            with self.assertRaisesRegex(Refusal, "edge-budget"):
                self.wrap(assessment, "over-edges", children=branches)
        self.assertEqual(self.c.checkpoint(), before)

    def test_depth_budget_refuses_before_descending_and_depth_32_remains_valid(self):
        assessment, entries = self.organization(1)
        child = self.wrap(assessment, "depth-0", [entries[0]["id"]])
        for depth in range(1, 33):
            child = self.wrap(assessment, f"depth-{depth}", children=[child])
        self.assertEqual(self.c.body(child)["depth"], 32)
        before = self.c.checkpoint()
        with self.assertRaisesRegex(Refusal, "depth-budget"):
            self.wrap(assessment, "depth-33", children=[child])
        self.assertEqual(self.c.checkpoint(), before)
        self.assertEqual(self.c.verify_history()["composite_work"]["depth"], 32)

    def test_byte_budget_is_checked_before_sqlite_returns_frame_blobs(self):
        assessment, entries = self.organization(1)
        child = self.wrap(assessment, "byte-leaf", [entries[0]["id"]])
        self.c.update_policy(replace(self.policy, sequence=2, max_composite_bytes=512))
        statements = []
        self.c.db.set_trace_callback(statements.append)
        try:
            with self.assertRaisesRegex(Refusal, "byte-budget"):
                self.wrap(assessment, "byte-leaf", [entries[0]["id"]])
        finally:
            self.c.db.set_trace_callback(None)
        self.assertFalse(any(sql.startswith("SELECT raw FROM frames") for sql in statements))
        self.assertEqual(self.c.body(child)["composite_id"], "byte-leaf")

    def test_serialized_byte_budget_is_aggregate_across_child_composites(self):
        first_assessment, entries = self.organization(2)
        first = self.wrap(first_assessment, "first-catalog", [entries[0]["id"]])
        second_assessment, _ = self.organization(2)
        second = self.wrap(second_assessment, "second-catalog", [entries[1]["id"]])
        sizes = []
        for child in (first, second):
            work = CompositeWork(self.c)
            self.c._composite_members(self.scope.subject(), child, work=work)
            sizes.append(work.serialized_bytes)
        combined = CompositeWork(self.c)
        for child in (first, second):
            self.c._composite_members(self.scope.subject(), child, work=combined)
        self.assertGreater(combined.serialized_bytes, max(sizes))
        limit = (max(sizes) + combined.serialized_bytes) // 2
        self.c.update_policy(replace(self.policy, sequence=2, max_composite_bytes=limit))
        before = self.c.checkpoint()
        with self.assertRaisesRegex(Refusal, "byte-budget"):
            self.wrap(first_assessment, "both-catalogs", children=[first, second])
        self.assertEqual(self.c.checkpoint(), before)

    def test_work_units_include_catalog_validation_and_member_aggregation(self):
        assessment, entries = self.organization(128)
        self.c.update_policy(replace(self.policy, sequence=2, max_composite_work=64))
        before = self.c.checkpoint()
        with self.assertRaisesRegex(Refusal, "work-budget"):
            self.wrap(assessment, "work-bound", [entry["id"] for entry in entries])
        self.assertEqual(self.c.checkpoint(), before)

    def test_shared_dag_history_uses_one_memo_and_bounded_sqlite_work(self):
        assessment, entries = self.organization(1)
        leaf = self.wrap(assessment, "shared", [entries[0]["id"]])
        for index in range(32):
            self.wrap(assessment, f"wrapper-{index}", children=[leaf])
        frame_count = len(self.c.checkpoint()["frames"])
        statements = []
        self.c.db.set_trace_callback(statements.append)
        try:
            with patch.object(self.core.r, "verify_frame", wraps=self.core.r.verify_frame) as verify:
                history = self.c.verify_history()
                self.assertEqual(verify.call_count, frame_count)
        finally:
            self.c.db.set_trace_callback(None)
        self.assertEqual(history["composite_work"]["nodes"], 33)
        self.assertEqual(history["composite_work"]["edges"], 32)
        self.assertLess(len(statements), 50)
        self.assertLess(history["composite_work"]["work_units"], 10000)

    def test_shared_dag_duplicate_members_fail_deterministically_without_reexpansion(self):
        assessment, entries = self.organization(1)
        leaf = self.wrap(assessment, "shared", [entries[0]["id"]])
        children = [self.wrap(assessment, f"shared-{index}", children=[leaf]) for index in range(16)]
        before = self.c.checkpoint()
        for _ in range(2):
            with self.assertRaisesRegex(Refusal, "duplicate-member"):
                self.wrap(assessment, "invalid-shared-parent", children=children)
        self.assertEqual(self.c.checkpoint(), before)

    def test_memo_is_per_request_and_does_not_mask_later_authority_table_corruption(self):
        assessment, entries = self.organization(1)
        leaf = self.wrap(assessment, "memo-leaf", [entries[0]["id"]])
        self.wrap(assessment, "first-parent", children=[leaf])
        self.c.db.execute("UPDATE composites SET composite_id='changed' WHERE hash=?", (address(leaf),))
        with self.assertRaisesRegex(Refusal, "recovery-quarantine"):
            self.wrap(assessment, "second-parent", children=[leaf])

    def test_composite_cycle_refuses_without_reentering_an_active_node(self):
        assessment, entries = self.organization(1)
        leaf = self.wrap(assessment, "cycle-leaf", [entries[0]["id"]])
        root = self.wrap(assessment, "cycle-root", children=[leaf])
        work = CompositeWork(self.c)
        corrupted = work.body(root)
        corrupted["child_composites"] = [root]
        with self.assertRaisesRegex(Refusal, "workspace-composite-cycle"):
            self.c._composite_members(self.scope.subject(), root, work=work)
        self.assertEqual(work.edges, 1)
        self.assertEqual(work.active, set())

    def test_composite_budget_policy_is_exact_bounded_and_cannot_be_reset(self):
        for name, ceiling in COMPOSITE_LIMITS.items():
            with self.subTest(name=name):
                for invalid in (True, ceiling + 1, -1):
                    with self.assertRaisesRegex(Refusal, "composite-policy-budget"):
                        Controller(self.core, self.root / "invalid-budget", replace(self.policy, **{name: invalid}),
                                   clock=self.clock, activation_mode="synthetic")
        self.c.update_policy(replace(self.policy, sequence=2, max_composite_nodes=64, max_composite_edges=64))
        with self.assertRaisesRegex(Refusal, "budget-reset"):
            self.c.update_policy(replace(self.c.policy, sequence=3, max_composite_edges=65))


if __name__ == "__main__":
    unittest.main()
