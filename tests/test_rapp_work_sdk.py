"""Adversarial RAPP Work SDK/1 integration and Workspace/1 immutability tests."""

from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import unittest
from unittest.mock import patch
import uuid


REPO = Path(__file__).resolve().parents[1]
REFERENCE = REPO / "protocols" / "rapp-work-sdk" / "1" / "reference"
PRIOR_RELEASE = REPO / "protocols" / "rapp-work-sdk" / "1" / "fixtures" / "prior-release"
PRIOR_RELEASE_DISPLACED = (
    REPO / "protocols" / "rapp-work-sdk" / "1" / "fixtures" / "prior-release-591e014"
)
SPEC = importlib.util.spec_from_file_location("rapp_work_sdk_scaffold_tests", REFERENCE / "scaffold.py")
SDK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(SDK)
WORKSPACE_MANIFEST_SHA256 = "3c59224a8641a827403779382abb70114ff53f3f884e2a0e738ed042b51582d3"
WORKSPACE_PREDECESSOR_MANIFEST_SHA256 = "f1165f947cb5d7554906012a174a854b28454403e41e8166925a364a68680370"
WORKSPACE_SPEC_SHA256 = "80135ae05e532f11810d31a5cf974050a8332c18bd45f16879a7286f213edfab"
WORKSPACE_SAFETY_SHA256 = "838b25dc46d881671d84a5d9f5cb10350fab3070f0e326e606dd420755f0beb9"
LEGACY_PIN = "4b4fc213c352de9157858041e57ab72bb5e17551"
PREVIOUS_PIN = "1c0e0b7c33a857e3f5e99c64355a8b8f970a83bc"
CURRENT_PIN = "e657140bf583e7caacea096af2f653cc8621f1a2"
DISPLACED_PIN = "591e014ad39e223b00ab343ae26e5d9a867ebeee"
DISPLACED_PROFILE_SHA256 = "f9a1b773ce4f4b61da6087b53a87f36495e73794821670d9ae371b9ef21299dc"
CANONICAL_SPEC_SHA256 = "283359355c3fe2858e28744368255683af3ed28a68e290e56c231e7d4b13c08e"
PREVIOUS_PROFILE_SHA256 = "0add0b6c4adedcc569d137d6c6e243d47bc383cc29d955805dee13fbd048e21a"
NOW = "2026-09-18T15:00:00.000Z"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class WorkSdkTests(unittest.TestCase):
    def setUp(self):
        base = REPO / ".validation" / "test-artifacts"
        base.mkdir(parents=True, exist_ok=True)
        self.temporary = base / f"work-sdk-{uuid.uuid4().hex}"
        self.temporary.mkdir()
        self.addCleanup(shutil.rmtree, self.temporary, True)

    def workspace(self, name: str = "workspace", *, world: str | None = "test-world") -> Path:
        root = self.temporary / name
        root.mkdir()
        identity = {
            "schema": "rapp/1",
            "rappid": "rappid:@fixture/workspace:" + hashlib.sha256(name.encode()).hexdigest(),
            "workspace_spec": "legacy-local/1",
        }
        if world is not None:
            identity["world_id"] = world
        (root / "rappid.json").write_text(json.dumps(identity, indent=2) + "\n", encoding="utf-8")
        (root / "native").mkdir()
        (root / "native" / "secret.txt").write_bytes(b"native-secret-never-copy")
        return root

    @staticmethod
    def native_snapshot(root: Path) -> dict[str, bytes]:
        return {
            path.relative_to(root).as_posix(): path.read_bytes()
            for path in root.rglob("*")
            if path.is_file() and ".rapp-work" not in path.parts
        }

    def discovery(self, root: Path, pin: str) -> dict:
        identity = SDK.workspace_identity(root)
        value = SDK.default_discovery(identity, pin)
        value["organization_pointers"] = [
            {
                "workspace_profile": "rapp-workspace/1",
                "composite": {"space": "rapp/1:wave", "hash": "1" * 64},
                "verification_status": "verified-local-receipt",
                "verification_receipt": {"space": "rapp/1:wave", "hash": "2" * 64},
                "routing_only": True,
                "content_copied": False,
                "grants_authority": False,
            }
        ]
        hive = "rappid:@fixture/hive:" + "3" * 64
        value["hive_endpoints"] = [
            {
                "id": "local-hive",
                "hive_rappid": hive,
                "world_id": identity["world_id"],
                "transport": "local-filesystem",
                "locator_sha256": "4" * 64,
                "verification_status": "verified",
                "verification_receipt": {"space": "rapp/1:wave", "hash": "5" * 64},
                "publication_authorized": False,
                "grants_authority": False,
            }
        ]
        value["hive_vectors"] = [
            {
                "hive_rappid": hive,
                "vector_sha256": "6" * 64,
                "verification_status": "verified",
                "verification_receipt": {"space": "rapp/1:wave", "hash": "7" * 64},
                "publication_authorized": False,
                "grants_authority": False,
            }
        ]
        capability = {
            "id": "example",
            "version": "1",
            "locator": "discovery:example",
            "sha256": None,
            "discovery_only": True,
            "activation_authorized": False,
            "execution_authorized": False,
            "grants_authority": False,
        }
        value["plugins"] = [capability]
        value["skills"] = [{**capability, "id": "example-skill"}]
        value["static_apis"] = [{**capability, "id": "example-static-api"}]
        SDK.validate_discovery(value, identity=identity, pin=pin)
        return value

    def prior_release_workspace(self, name: str = "prior-release", source: Path = PRIOR_RELEASE) -> Path:
        root = self.temporary / name
        shutil.copytree(source, root)
        root.chmod(0o700)
        sidecar = root / ".rapp-work"
        for directory in [sidecar, *[path for path in sidecar.rglob("*") if path.is_dir()]]:
            directory.chmod(0o700)
        for path in sidecar.rglob("*"):
            if path.is_file():
                path.chmod(0o600)
        return root

    def retained_profile_workspace(self, pin: str, name: str) -> Path:
        root = self.workspace(name)
        identity = SDK.workspace_identity(root)
        discovery = SDK.default_discovery(identity, pin)
        files = SDK._generation_files(pin, discovery)
        install = SDK._install_state(identity, pin, discovery, NOW)
        sidecar = root / ".rapp-work"
        generation = sidecar / "generations" / pin
        generation.mkdir(parents=True, mode=0o700)
        sidecar.chmod(0o700)
        (sidecar / "generations").chmod(0o700)
        generation.chmod(0o700)
        for filename, raw in files.items():
            path = generation / filename
            path.write_bytes(raw)
            path.chmod(0o600)
        install_path = sidecar / "install.json"
        install_path.write_bytes(SDK.canonical_bytes(install))
        install_path.chmod(0o600)
        return root

    def test_workspace1_identity_and_normative_bytes_are_frozen(self):
        root = REPO / "protocols" / "rapp-workspace" / "1"
        manifest_path = root / "manifest.json"
        self.assertEqual(digest(manifest_path), WORKSPACE_MANIFEST_SHA256)
        self.assertEqual(digest(root / "SPEC.md"), WORKSPACE_SPEC_SHA256)
        self.assertEqual(digest(root / "safety-matrix.json"), WORKSPACE_SAFETY_SHA256)
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        self.assertEqual(manifest["profile"], "rapp-workspace/1")
        self.assertEqual(manifest["brand"], "RAPP Workspace/1")
        for entry in manifest["normative"]:
            path = root / entry["path"]
            self.assertEqual(path.stat().st_size, entry["bytes"], entry["path"])
            self.assertEqual(digest(path), entry["sha256"], entry["path"])
        index = json.loads((REPO / "protocols" / "index.json").read_text(encoding="utf-8"))
        self.assertEqual(index["workspace_latest"], "rapp-workspace/1")
        entries = [item for item in index["profiles"] if item["name"].startswith("rapp-workspace/")]
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]["name"], "rapp-workspace/1")
        self.assertEqual(entries[0]["spec_sha256"], WORKSPACE_SPEC_SHA256)
        self.assertEqual(entries[0]["manifest_sha256"], WORKSPACE_MANIFEST_SHA256)
        retained = [
            {
                "schema": "rapp-workspace-file-manifest/1",
                "path": f"history/{WORKSPACE_PREDECESSOR_MANIFEST_SHA256}/manifest.json",
                "sha256": WORKSPACE_PREDECESSOR_MANIFEST_SHA256,
                "bytes": 7990,
            }
        ]
        self.assertEqual(manifest["predecessors"], retained)
        self.assertEqual(digest(root / retained[0]["path"]), WORKSPACE_PREDECESSOR_MANIFEST_SHA256)

    def test_parent_pin_and_vendored_rapp_work_bytes_match(self):
        pin = SDK.PARENT_PIN
        vendored = REPO / "protocols" / "rapp-work-sdk" / "1" / pin["vendored_path"]
        self.assertNotIn("temporary", pin)
        self.assertEqual(pin["repository"], "https://github.com/kody-w/rapp-1")
        self.assertEqual(pin["commit"], CURRENT_PIN)
        self.assertEqual(pin["path"], "protocols/rapp-work/1/SPEC.md")
        self.assertEqual(pin["spec_sha256"], CANONICAL_SPEC_SHA256)
        self.assertEqual(pin["spec_bytes"], 11427)
        self.assertEqual(vendored.stat().st_size, pin["spec_bytes"])
        self.assertEqual(digest(vendored), pin["spec_sha256"])
        self.assertEqual(SDK.CURRENT_PIN, pin["commit"])
        self.assertEqual(SDK.PINS[PREVIOUS_PIN]["status"], "migration-source-only")
        self.assertFalse(SDK.PINS[PREVIOUS_PIN]["fresh_install"])
        self.assertEqual(
            SDK.PINS[PREVIOUS_PIN]["profile_artifact"]["sha256"],
            PREVIOUS_PROFILE_SHA256,
        )
        self.assertEqual(SDK.PINS[SDK.CURRENT_PIN]["status"], "current")
        self.assertEqual(SDK.PINS[SDK.CURRENT_PIN]["sequence"], 3)
        self.assertEqual(SDK.PINS[DISPLACED_PIN]["status"], "migration-source-only")
        self.assertFalse(SDK.PINS[DISPLACED_PIN]["fresh_install"])
        self.assertEqual(SDK.PINS[DISPLACED_PIN]["sequence"], 2)
        self.assertEqual(SDK.PINS[DISPLACED_PIN]["spec_sha256"], CANONICAL_SPEC_SHA256)
        self.assertEqual(
            SDK.PINS[DISPLACED_PIN]["profile_artifact"],
            {
                "path": f"history/{DISPLACED_PIN}/profile.json",
                "sha256": DISPLACED_PROFILE_SHA256,
                "bytes": 2342,
            },
        )
        self.assertEqual(SDK.PROFILE["workspace_sibling"]["manifest_sha256"], WORKSPACE_MANIFEST_SHA256)

    def test_active_pin_metadata_has_no_temporary_markers(self):
        protocol = REPO / "protocols" / "rapp-work-sdk" / "1"
        profile = json.loads((protocol / "profile.json").read_text(encoding="utf-8"))
        index = json.loads((REPO / "protocols" / "index.json").read_text(encoding="utf-8"))
        index_profile = next(
            entry for entry in index["profiles"] if entry["name"] == "rapp-work-sdk/1"
        )
        lock = json.loads(
            (
                REPO
                / ".github"
                / "skills"
                / "rapp-work-sdk"
                / "rapp"
                / "agent.lock.json"
            ).read_text(encoding="utf-8")
        )
        self.assertNotIn("temporary", profile["parent"])
        self.assertNotIn("temporary_parent_pin", index_profile)
        self.assertNotIn("temporary_parent_pin", lock["protocol"])
        self.assertNotIn("current-temporary", (protocol / "profile.json").read_text())

    def test_install_is_atomic_offline_idempotent_and_does_not_copy_native_bytes(self):
        root = self.workspace()
        before = self.native_snapshot(root)
        requested = self.discovery(root, SDK.CURRENT_PIN)
        with patch("socket.socket", side_effect=AssertionError("network attempted")):
            first = SDK.install_workspace(root, discovery=requested, now=NOW)
            second = SDK.install_workspace(root, discovery=requested, now=NOW)
            verified = SDK.verify_workspace(root)
        self.assertEqual(first["status"], "installed")
        self.assertEqual(second["status"], "already-installed")
        self.assertEqual(first["generation_sha256"], second["generation_sha256"])
        self.assertEqual(before, self.native_snapshot(root))
        self.assertFalse(verified["native_workspace_copied"])
        self.assertFalse(verified["publication_authorized"])
        sidecar_bytes = b"".join(
            path.read_bytes() for path in (root / ".rapp-work").rglob("*") if path.is_file()
        )
        self.assertNotIn(b"native-secret-never-copy", sidecar_bytes)

    def test_discovery_entries_cannot_grant_authority(self):
        root = self.workspace()
        requested = self.discovery(root, SDK.CURRENT_PIN)
        requested["hive_endpoints"][0]["publication_authorized"] = True
        with self.assertRaisesRegex(SDK.Refusal, "authorize publication"):
            SDK.install_workspace(root, discovery=requested, now=NOW)
        self.assertFalse((root / ".rapp-work").exists())
        requested = self.discovery(root, SDK.CURRENT_PIN)
        requested["skills"][0]["execution_authorized"] = True
        with self.assertRaisesRegex(SDK.Refusal, "grant authority"):
            SDK.install_workspace(root, discovery=requested, now=NOW)
        self.assertFalse((root / ".rapp-work").exists())

    def test_symlink_conflict_partial_and_world_relabel_fail_closed(self):
        outside = self.temporary / "outside"
        outside.mkdir()
        symlinked = self.workspace("symlinked")
        (symlinked / ".rapp-work").symlink_to(outside, target_is_directory=True)
        with self.assertRaisesRegex(SDK.Refusal, "symlink|unsafe"):
            SDK.install_workspace(symlinked)
        partial = self.workspace("partial")
        (partial / ".rapp-work").mkdir(mode=0o700)
        (partial / ".rapp-work" / "partial.json").write_text("{}", encoding="utf-8")
        with self.assertRaisesRegex(SDK.Refusal, "partial|unmanaged"):
            SDK.install_workspace(partial)
        conflict = self.workspace("world-conflict")
        with self.assertRaisesRegex(SDK.Refusal, "world"):
            SDK.install_workspace(conflict, world_id="other-world")
        self.assertFalse((conflict / ".rapp-work").exists())

    def test_missing_atomic_backend_fails_closed_without_activation(self):
        root = self.workspace("unsupported-atomic-backend")
        with patch.object(SDK.sys, "platform", "unsupported-platform"):
            with self.assertRaisesRegex(SDK.Refusal, "unavailable"):
                SDK.install_workspace(root, now=NOW)
        self.assertFalse((root / ".rapp-work").exists())
        self.assertEqual(
            [
                path.name
                for path in root.iterdir()
                if path.name.casefold().startswith(".rapp-work.tmp-")
            ],
            [],
        )

    def test_failed_initial_activation_leaves_no_partial_sidecar(self):
        root = self.workspace()
        original_activate = SDK._rename_noreplace_at

        def fail_activation(source_parent, source, destination_parent, destination):
            if destination == ".rapp-work":
                raise OSError("simulated activation failure")
            return original_activate(
                source_parent,
                source,
                destination_parent,
                destination,
            )

        with patch.object(SDK, "_rename_noreplace_at", side_effect=fail_activation):
            with self.assertRaisesRegex(OSError, "activation failure"):
                SDK.install_workspace(root, now=NOW)
        self.assertFalse((root / ".rapp-work").exists())
        self.assertEqual(
            [path.name for path in root.iterdir() if path.name.startswith(".rapp-work.tmp-")],
            [],
        )

    def test_update_requires_exact_forward_pins_and_plan_digest(self):
        root = self.prior_release_workspace("update")
        before = self.native_snapshot(root)
        old_profile = (
            root / ".rapp-work" / "generations" / LEGACY_PIN / "profile.json"
        ).read_bytes()
        old_discovery = (
            root / ".rapp-work" / "generations" / LEGACY_PIN / "discovery.json"
        ).read_bytes()
        verified_old = SDK.verify_workspace(root)
        self.assertEqual(verified_old["current_pin"], LEGACY_PIN)
        self.assertEqual(hashlib.sha256(old_profile).hexdigest(), "84b5afe5171b91202c96213de6767815ef1e22d743cdef97bd4ac9b4f5a66591")
        self.assertNotEqual(old_profile, SDK.PROFILE_RAW)
        plan = SDK.plan_update(root, from_pin=LEGACY_PIN, to_pin=SDK.CURRENT_PIN)
        self.assertEqual(
            plan["plan"]["from_profile_sha256"],
            hashlib.sha256(old_profile).hexdigest(),
        )
        self.assertEqual(plan["plan"]["target_profile_sha256"], SDK.PROFILE_SHA256)
        with self.assertRaisesRegex(SDK.Refusal, "exact update plan"):
            SDK.update_workspace(
                root,
                from_pin=LEGACY_PIN,
                to_pin=SDK.CURRENT_PIN,
                plan_digest="0" * 64,
                now=NOW,
            )
        result = SDK.update_workspace(
            root,
            from_pin=LEGACY_PIN,
            to_pin=SDK.CURRENT_PIN,
            plan_digest=plan["plan_digest"],
            now=NOW,
        )
        self.assertEqual(result["status"], "updated")
        self.assertEqual(before, self.native_snapshot(root))
        install = json.loads((root / ".rapp-work" / "install.json").read_bytes())
        self.assertEqual(install["profile_sha256"], SDK.PROFILE_SHA256)
        self.assertEqual(
            (
                root / ".rapp-work" / "generations" / LEGACY_PIN / "profile.json"
            ).read_bytes(),
            old_profile,
        )
        self.assertEqual(
            (
                root / ".rapp-work" / "generations" / LEGACY_PIN / "discovery.json"
            ).read_bytes(),
            old_discovery,
        )
        self.assertEqual(
            (
                root
                / ".rapp-work"
                / "generations"
                / SDK.CURRENT_PIN
                / "profile.json"
            ).read_bytes(),
            SDK.PROFILE_RAW,
        )
        with self.assertRaisesRegex(SDK.Refusal, "downgrade"):
            SDK.plan_update(root, from_pin=SDK.CURRENT_PIN, to_pin=LEGACY_PIN)
        with self.assertRaisesRegex(SDK.Refusal, "unknown"):
            SDK.plan_update(root, from_pin=SDK.CURRENT_PIN, to_pin="f" * 40)

    def test_immediate_previous_pin_updates_from_retained_profile_bytes(self):
        root = self.retained_profile_workspace(PREVIOUS_PIN, "previous-pin-update")
        before = self.native_snapshot(root)
        retained = (
            REPO
            / "protocols"
            / "rapp-work-sdk"
            / "1"
            / "history"
            / PREVIOUS_PIN
            / "profile.json"
        ).read_bytes()
        self.assertEqual(hashlib.sha256(retained).hexdigest(), PREVIOUS_PROFILE_SHA256)
        self.assertEqual(SDK.verify_workspace(root)["current_pin"], PREVIOUS_PIN)
        plan = SDK.plan_update(
            root,
            from_pin=PREVIOUS_PIN,
            to_pin=SDK.CURRENT_PIN,
        )
        self.assertEqual(
            plan["plan"]["from_profile_sha256"],
            PREVIOUS_PROFILE_SHA256,
        )
        result = SDK.update_workspace(
            root,
            from_pin=PREVIOUS_PIN,
            to_pin=SDK.CURRENT_PIN,
            plan_digest=plan["plan_digest"],
            now=NOW,
        )
        self.assertEqual(result["status"], "updated")
        self.assertEqual(before, self.native_snapshot(root))
        self.assertEqual(
            (
                root
                / ".rapp-work"
                / "generations"
                / PREVIOUS_PIN
                / "profile.json"
            ).read_bytes(),
            retained,
        )

    def test_actual_591e014_release_fixture_updates_only_by_exact_plan_digest(self):
        record = json.loads((PRIOR_RELEASE_DISPLACED / "fixture.json").read_bytes())
        self.assertEqual(record["pin"], DISPLACED_PIN)
        self.assertEqual(record["profile_sha256"], DISPLACED_PROFILE_SHA256)
        root = self.prior_release_workspace("displaced-update", PRIOR_RELEASE_DISPLACED)
        before = self.native_snapshot(root)
        generation = root / ".rapp-work" / "generations"
        old_profile = (generation / DISPLACED_PIN / "profile.json").read_bytes()
        old_discovery = (generation / DISPLACED_PIN / "discovery.json").read_bytes()
        install_path = root / ".rapp-work" / "install.json"
        old_install = install_path.read_bytes()
        self.assertEqual(hashlib.sha256(old_profile).hexdigest(), DISPLACED_PROFILE_SHA256)
        self.assertEqual(hashlib.sha256(old_install).hexdigest(), record["install_sha256"])
        self.assertEqual(old_profile, SDK._pin_profile_raw(DISPLACED_PIN))
        self.assertNotEqual(old_profile, SDK.PROFILE_RAW)
        self.assertEqual(
            json.loads(old_profile)["workspace_sibling"]["manifest_sha256"],
            WORKSPACE_PREDECESSOR_MANIFEST_SHA256,
        )
        verified = SDK.verify_workspace(root)
        self.assertEqual(verified["current_pin"], DISPLACED_PIN)
        self.assertEqual(verified["generation_sha256"], record["generation_sha256"])
        plan = SDK.plan_update(root, from_pin=DISPLACED_PIN, to_pin=SDK.CURRENT_PIN)
        self.assertEqual(plan["plan"]["from_profile_sha256"], DISPLACED_PROFILE_SHA256)
        self.assertEqual(plan["plan"]["target_profile_sha256"], SDK.PROFILE_SHA256)
        legacy_plan = SDK.plan_update(
            self.prior_release_workspace("legacy-plan"),
            from_pin=LEGACY_PIN,
            to_pin=SDK.CURRENT_PIN,
        )
        for wrong in ("0" * 64, legacy_plan["plan_digest"]):
            with self.subTest(wrong=wrong), self.assertRaisesRegex(SDK.Refusal, "exact update plan"):
                SDK.update_workspace(
                    root,
                    from_pin=DISPLACED_PIN,
                    to_pin=SDK.CURRENT_PIN,
                    plan_digest=wrong,
                    now=NOW,
                )
            self.assertEqual(install_path.read_bytes(), old_install)
            self.assertFalse((generation / SDK.CURRENT_PIN).exists())
        result = SDK.update_workspace(
            root,
            from_pin=DISPLACED_PIN,
            to_pin=SDK.CURRENT_PIN,
            plan_digest=plan["plan_digest"],
            now=NOW,
        )
        self.assertEqual(result["status"], "updated")
        self.assertEqual(before, self.native_snapshot(root))
        self.assertEqual((generation / DISPLACED_PIN / "profile.json").read_bytes(), old_profile)
        self.assertEqual((generation / DISPLACED_PIN / "discovery.json").read_bytes(), old_discovery)
        self.assertEqual((generation / SDK.CURRENT_PIN / "profile.json").read_bytes(), SDK.PROFILE_RAW)
        install = json.loads(install_path.read_bytes())
        self.assertEqual(install["profile_sha256"], SDK.PROFILE_SHA256)
        self.assertEqual(install["installed_pin"], DISPLACED_PIN)
        self.assertEqual(install["last_update_plan_digest"], plan["plan_digest"])
        self.assertEqual(SDK.verify_workspace(root)["current_pin"], SDK.CURRENT_PIN)
        with self.assertRaisesRegex(SDK.Refusal, "downgrade"):
            SDK.plan_update(root, from_pin=SDK.CURRENT_PIN, to_pin=DISPLACED_PIN)

    def test_reference_conformance_runs_every_prior_release_vector(self):
        output = (self.temporary / "conformance").relative_to(REPO)
        completed = subprocess.run(
            [sys.executable, "-B", str(REFERENCE / "conformance.py"), "--output", str(output)],
            cwd=REPO,
            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=180,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        report = json.loads((REPO / output / "conformance-results.json").read_bytes())
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(report["checks"], 18)
        self.assertEqual(report["current_pin"], CURRENT_PIN)
        self.assertEqual(report["workspace_manifest_sha256"], WORKSPACE_MANIFEST_SHA256)
        self.assertEqual(report["workspace_spec_sha256"], WORKSPACE_SPEC_SHA256)

    def test_pointer_failure_keeps_old_pin_and_exact_retry_completes(self):
        root = self.prior_release_workspace("pointer-failure")
        plan = SDK.plan_update(root, from_pin=LEGACY_PIN, to_pin=SDK.CURRENT_PIN)
        original_cas = SDK._atomic_compare_swap_at

        def fail_pointer(parent, name, expected, replacement):
            if name == "install.json":
                raise OSError("simulated pointer failure")
            return original_cas(parent, name, expected, replacement)

        with patch.object(SDK, "_atomic_compare_swap_at", side_effect=fail_pointer):
            with self.assertRaisesRegex(OSError, "pointer failure"):
                SDK.update_workspace(
                    root,
                    from_pin=LEGACY_PIN,
                    to_pin=SDK.CURRENT_PIN,
                    plan_digest=plan["plan_digest"],
                    now=NOW,
                )
        pending = SDK.verify_workspace(root)
        self.assertEqual(pending["current_pin"], LEGACY_PIN)
        self.assertEqual(pending["pending_updates"][0]["plan_digest"], plan["plan_digest"])
        result = SDK.update_workspace(
            root,
            from_pin=LEGACY_PIN,
            to_pin=SDK.CURRENT_PIN,
            plan_digest=plan["plan_digest"],
            now="2026-09-18T16:00:00.000Z",
        )
        self.assertEqual(result["status"], "updated")

    def test_raced_sidecar_and_generation_destinations_are_never_overwritten(self):
        root = self.workspace("sidecar-race")
        original_activate = SDK._rename_noreplace_at

        def race_sidecar(source_parent, source, destination_parent, destination):
            if destination == ".rapp-work":
                raced = root / ".rapp-work"
                raced.mkdir(mode=0o700)
                (raced / "attacker").write_bytes(b"preserve-me")
            return original_activate(
                source_parent,
                source,
                destination_parent,
                destination,
            )

        with patch.object(SDK, "_rename_noreplace_at", side_effect=race_sidecar):
            with self.assertRaisesRegex(SDK.Refusal, "raced activation"):
                SDK.install_workspace(root, now=NOW)
        self.assertEqual((root / ".rapp-work" / "attacker").read_bytes(), b"preserve-me")

        historical = self.prior_release_workspace("generation-race")
        plan = SDK.plan_update(
            historical,
            from_pin=LEGACY_PIN,
            to_pin=SDK.CURRENT_PIN,
        )

        def race_generation(source_parent, source, destination_parent, destination):
            if destination == SDK.CURRENT_PIN:
                raced = (
                    historical
                    / ".rapp-work"
                    / "generations"
                    / SDK.CURRENT_PIN
                )
                raced.mkdir(mode=0o700)
                (raced / "attacker").write_bytes(b"preserve-generation")
            return original_activate(
                source_parent,
                source,
                destination_parent,
                destination,
            )

        with patch.object(SDK, "_rename_noreplace_at", side_effect=race_generation):
            with self.assertRaisesRegex(SDK.Refusal, "raced activation"):
                SDK.update_workspace(
                    historical,
                    from_pin=LEGACY_PIN,
                    to_pin=SDK.CURRENT_PIN,
                    plan_digest=plan["plan_digest"],
                    now=NOW,
                )
        self.assertEqual(
            (
                historical
                / ".rapp-work"
                / "generations"
                / SDK.CURRENT_PIN
                / "attacker"
            ).read_bytes(),
            b"preserve-generation",
        )
        install = json.loads(
            (historical / ".rapp-work" / "install.json").read_bytes()
        )
        self.assertEqual(install["current_pin"], LEGACY_PIN)

    def test_install_pointer_compare_and_swap_restores_raced_destination(self):
        root = self.prior_release_workspace("pointer-cas-race")
        plan = SDK.plan_update(root, from_pin=LEGACY_PIN, to_pin=SDK.CURRENT_PIN)
        install_path = root / ".rapp-work" / "install.json"
        original = install_path.read_bytes()
        raced_value = json.loads(original)
        raced_value["installed_utc"] = "2026-09-17T12:00:01.000Z"
        raced = SDK.canonical_bytes(raced_value)
        original_exchange = SDK._rename_exchange_at
        calls = 0

        def race_exchange(source_parent, source, destination_parent, destination):
            nonlocal calls
            calls += 1
            if calls == 1:
                install_path.write_bytes(raced)
                install_path.chmod(0o600)
            return original_exchange(
                source_parent,
                source,
                destination_parent,
                destination,
            )

        with patch.object(SDK, "_rename_exchange_at", side_effect=race_exchange):
            with self.assertRaisesRegex(SDK.Refusal, "changed during compare-and-swap"):
                SDK.update_workspace(
                    root,
                    from_pin=LEGACY_PIN,
                    to_pin=SDK.CURRENT_PIN,
                    plan_digest=plan["plan_digest"],
                    now=NOW,
                )
        self.assertEqual(install_path.read_bytes(), raced)
        self.assertEqual(
            json.loads(install_path.read_bytes())["current_pin"],
            LEGACY_PIN,
        )

    def test_recorded_world_recovers_without_native_mutation(self):
        root = self.prior_release_workspace("recorded-world")
        native = (root / "rappid.json").read_bytes()
        verified = SDK.verify_workspace(root)
        self.assertEqual(verified["world_id"], "fixture-world")
        self.assertEqual((root / "rappid.json").read_bytes(), native)
        with self.assertRaisesRegex(SDK.Refusal, "installed sidecar world"):
            SDK.verify_workspace(root, world_id="other-world")
        self.assertEqual((root / "rappid.json").read_bytes(), native)

    def test_tampered_vendored_implementation_has_zero_import_side_effects(self):
        source = REPO / ".github" / "skills" / "rapp-work-sdk"
        skill = self.temporary / "tampered-skill"
        shutil.copytree(source, skill)
        marker = self.temporary / "vendored-import-side-effect"
        implementation = (
            skill
            / "vendor"
            / "rapp-work-sdk"
            / "1"
            / "reference"
            / "scaffold.py"
        )
        source_text = implementation.read_text(encoding="utf-8")
        future = "from __future__ import annotations\n"
        self.assertIn(future, source_text)
        implementation.write_text(
            source_text.replace(
                future,
                future
                + "from pathlib import Path as _TamperPath\n"
                + f"_TamperPath({str(marker)!r}).write_text("
                "'executed', encoding='utf-8')\n",
                1,
            ),
            encoding="utf-8",
        )
        environment = {
            "PATH": os.environ.get("PATH", ""),
            "PYTHONDONTWRITEBYTECODE": "1",
            "TMPDIR": str(REPO / ".validation" / "test-artifacts"),
        }
        completed = subprocess.run(
            [
                sys.executable,
                "-B",
                str(skill / "scripts" / "scaffold.py"),
                "profile",
            ],
            cwd=skill,
            env=environment,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("checksum mismatch", completed.stderr)
        self.assertFalse(marker.exists())

    def test_partial_or_conflicting_generation_is_never_repaired(self):
        root = self.workspace("generation-conflict")
        SDK.install_workspace(root, now=NOW)
        generation = root / ".rapp-work" / "generations" / SDK.CURRENT_PIN
        discovery = generation / "discovery.json"
        discovery.chmod(0o644)
        with self.assertRaisesRegex(SDK.Refusal, "owner-only"):
            SDK.verify_workspace(root)
        discovery.chmod(0o600)
        (generation / "discovery.json").unlink()
        before = (root / "rappid.json").read_bytes()
        with self.assertRaisesRegex(SDK.Refusal, "partial"):
            SDK.install_workspace(root)
        self.assertEqual((root / "rappid.json").read_bytes(), before)
        self.assertFalse((generation / "discovery.json").exists())

    def test_checksum_locked_skill_matches_canonical_profile_and_scaffold(self):
        skill = REPO / ".github" / "skills" / "rapp-work-sdk"
        lock = json.loads((skill / "rapp" / "agent.lock.json").read_text(encoding="utf-8"))
        self.assertEqual(lock["schema"], "rapp-skill-lock/1")
        self.assertEqual(lock["name"], "rapp-work-sdk")
        paths = [entry["path"] for entry in lock["files"]]
        self.assertEqual(paths, sorted(paths))
        self.assertEqual(len(paths), len(set(paths)))
        for entry in lock["files"]:
            self.assertEqual(digest(skill / entry["path"]), entry["sha256"], entry["path"])
        profile = REPO / "protocols" / "rapp-work-sdk" / "1"
        vendored = skill / "vendor" / "rapp-work-sdk" / "1"
        for relative in (
            "SPEC.md",
            "manifest.json",
            "parent-pin.json",
            "profile.json",
            "history/4b4fc213c352de9157858041e57ab72bb5e17551/profile.json",
            "history/1c0e0b7c33a857e3f5e99c64355a8b8f970a83bc/profile.json",
            f"history/{DISPLACED_PIN}/profile.json",
            "reference/scaffold.py",
            "schemas/discovery.schema.json",
            "schemas/install.schema.json",
            "schemas/profile.schema.json",
            "schemas/update.schema.json",
            "vendor/rapp-work/1/SPEC.md",
            "fixtures/prior-release/fixture.json",
            "fixtures/prior-release/rappid.json",
            "fixtures/prior-release/native/secret.txt",
            "fixtures/prior-release/.rapp-work/install.json",
            "fixtures/prior-release/.rapp-work/generations/"
            "4b4fc213c352de9157858041e57ab72bb5e17551/profile.json",
            "fixtures/prior-release/.rapp-work/generations/"
            "4b4fc213c352de9157858041e57ab72bb5e17551/discovery.json",
            "fixtures/prior-release-591e014/fixture.json",
            "fixtures/prior-release-591e014/rappid.json",
            "fixtures/prior-release-591e014/native/secret.txt",
            "fixtures/prior-release-591e014/.rapp-work/install.json",
            f"fixtures/prior-release-591e014/.rapp-work/generations/{DISPLACED_PIN}/profile.json",
            f"fixtures/prior-release-591e014/.rapp-work/generations/{DISPLACED_PIN}/discovery.json",
        ):
            self.assertEqual((profile / relative).read_bytes(), (vendored / relative).read_bytes(), relative)


if __name__ == "__main__":
    unittest.main()
