"""G24 vectors: editable front doors never move a frozen identity. Public synthetic data only."""

from contextlib import contextmanager
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import unittest
from unittest.mock import patch
import uuid

REPO = Path(__file__).resolve().parents[1]
WORKSPACE = REPO / "protocols" / "rapp-workspace" / "1"
REFERENCE = WORKSPACE / "reference"
SDK_ROOT = REPO / "protocols" / "rapp-work-sdk" / "1"
# Receipts exported by the unmodified f1165f94 runtime's own demo (`frame_lens.py demo`).
PRIOR_RUNTIME_RECEIPTS = REPO / "tests" / "fixtures" / "prior-runtime-f1165f94"
sys.path.insert(0, str(REFERENCE))
from common import Parent, Refusal, read_file, sha
import pins
from safe_kernel import Controller, ExternalPolicy, Scope, verify_historical_archive


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


SDK = load_module("rapp_work_sdk_scaffold_front_door", SDK_ROOT / "reference" / "scaffold.py")
SDK_PINS = load_module("rapp_work_sdk_pins_front_door", SDK_ROOT / "reference" / "pins.py")

SPEC_SHA256 = "80135ae05e532f11810d31a5cf974050a8332c18bd45f16879a7286f213edfab"
SUCCESSOR_SHA256 = "3c59224a8641a827403779382abb70114ff53f3f884e2a0e738ed042b51582d3"
PREDECESSOR = {
    "schema": "rapp-workspace-file-manifest/1",
    "path": "history/f1165f947cb5d7554906012a174a854b28454403e41e8166925a364a68680370/manifest.json",
    "sha256": "f1165f947cb5d7554906012a174a854b28454403e41e8166925a364a68680370",
    "bytes": 7990,
}
WORKSPACE_FRONT_DOORS = (
    "README.md",
    "protocols/README.md",
    "protocols/rapp-workspace/1/reference/README.md",
    "protocols/rapp-workspace/prototypes/README.md",
)
SDK_FRONT_DOOR = "protocols/rapp-work-sdk/1/reference/README.md"
REPOSITORY_EVIDENCE = (
    "SPEC.md", "SKILL.md", "tools/frame_lens.py", "tests/test_safe_kernel.py",
    "tests/test_p0_hardening.py", ".github/skills/rapp-workspace/SKILL.md",
    ".github/skills/autonomous-rapp-estate-manager/SKILL.md",
)
DISPLACED_PIN = "591e014ad39e223b00ab343ae26e5d9a867ebeee"
CURRENT_PIN = "e657140bf583e7caacea096af2f653cc8621f1a2"
DISPLACED_PROFILE_SHA256 = "f9a1b773ce4f4b61da6087b53a87f36495e73794821670d9ae371b9ef21299dc"
INSTANCE = "rappid:@fixture/front-door:" + "b" * 64
NOW = "2026-09-25T12:00:00.000Z"
HEADER = (
    b"<!-- synthetic network header -->\n"
    b"[![RAPP/1](https://example.com/badge.svg)](https://example.com/rapp-1) "
    b"[Start here](https://example.com/start-here)\n\n"
)
REPOSITORY_ROOTS = (
    ".github", "docs", "protocols", "tests", "tools",
    ".gitignore", "LICENSE", "README.md", "SKILL.md", "SPEC.md",
)
PROBE = r"""
import contextlib, importlib.util, io, json, sys
from pathlib import Path
repo, rapp1, controller, instance, spec_sha256, runtime_sha256, now = sys.argv[1:8]
repo, controller = Path(repo), Path(controller)
sys.path.insert(0, str(repo / "protocols/rapp-workspace/1/reference"))
from common import Parent, Refusal, read_file, sha
import pins
from safe_kernel import Controller, ExternalPolicy, Scope
result = {"workspace_committed": sha(read_file(repo / "protocols/rapp-workspace/1/manifest.json"))}
try:
    result["workspace_manifest"] = sha(pins.encode(pins.manifest()))
except Refusal as error:
    result["workspace_manifest"] = "refused: " + str(error)
spec = importlib.util.spec_from_file_location("probe_sdk_pins", repo / "protocols/rapp-work-sdk/1/reference/pins.py")
sdk = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sdk)
result["sdk_committed"] = sha((repo / "protocols/rapp-work-sdk/1/manifest.json").read_bytes())
try:
    result["sdk_manifest"] = sha(sdk.encoded(sdk.manifest()))
except ValueError as error:
    result["sdk_manifest"] = "refused: " + str(error)
def verdict(function):
    output = io.StringIO()
    with contextlib.redirect_stdout(output):
        code = function()
    return [code, output.getvalue().strip()]
sys.argv = ["pins.py"]
result["workspace_pins"] = verdict(pins.main)
result["sdk_pins"] = verdict(lambda: sdk.main([]))
policy = ExternalPolicy(instance, "fixture-world", spec_sha256, runtime_sha256,
                        frozenset({"capture"}), (Scope("fixture", "front-door"),))
try:
    kernel = Controller(Parent(rapp1), controller, policy, clock=lambda: now, activation_mode="synthetic")
except Refusal as error:
    result["qualification"] = "refused: " + str(error)
else:
    try:
        result["qualification"] = "qualified: " + kernel.qualify().sha256
    finally:
        kernel.close()
result["controller_created"] = controller.exists()
print(json.dumps(result, sort_keys=True))
"""


def append_marker(path):
    marker = b"\n# synthetic normative edit\n" if path.suffix == ".py" else b"\n"
    path.write_bytes(path.read_bytes() + marker)


def reference_sha256(name):
    return next(item["sha256"] for item in pins.manifest()["reference"] if item["path"] == name)


class FrontDoorFixture(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rapp1 = os.environ.get("RAPP1_PATH")
        cls.core = Parent(cls.rapp1)
        cls.base = REPO / ".validation" / "test-artifacts" / ("front-door-" + uuid.uuid4().hex)
        cls.base.mkdir(parents=True, mode=0o700)
        cls.environment = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.base, ignore_errors=True)

    def scratch(self, name):
        root = self.base / (name + "-" + uuid.uuid4().hex) / "repo"
        root.mkdir(parents=True)
        for entry in REPOSITORY_ROOTS:
            source = REPO / entry
            if source.is_dir():
                shutil.copytree(source, root / entry, copy_function=shutil.copyfile,
                                ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".DS_Store"))
            else:
                shutil.copyfile(source, root / entry)
        return root

    @contextmanager
    def damaged(self, path, damage):
        """Apply one controlled edit to a scratch file, then restore its exact bytes."""
        original = path.read_bytes() if path.exists() else None
        try:
            damage(path)
            yield
        finally:
            if original is None:
                path.unlink(missing_ok=True)
            else:
                path.write_bytes(original)
            self.assertEqual(path.read_bytes() if path.exists() else None, original)

    def run_tool(self, root, *arguments):
        return subprocess.run([sys.executable, "-B", *[str(item) for item in arguments]], cwd=root,
                              capture_output=True, text=True, timeout=180, env=self.environment)

    def probe(self, root, runtime_sha256=SUCCESSOR_SHA256):
        controller = root.parent / ("controller-" + uuid.uuid4().hex)
        completed = self.run_tool(root, "-c", PROBE, root, self.rapp1, controller, INSTANCE,
                                  SPEC_SHA256, runtime_sha256, NOW)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        return json.loads(completed.stdout)

    def policy(self, runtime_sha256):
        return ExternalPolicy(INSTANCE, "fixture-world", SPEC_SHA256, runtime_sha256,
                              frozenset({"capture"}), (Scope("fixture", "front-door"),))


class PredecessorHistoryTests(FrontDoorFixture):
    """Property 1: the old pin f1165f94 still verifies as history."""

    def setUp(self):
        self.successor = json.loads(read_file(WORKSPACE / "manifest.json"))
        self.raw = read_file(WORKSPACE / PREDECESSOR["path"])
        self.predecessor = json.loads(self.raw)

    def test_retained_predecessor_bytes_hash_to_the_old_pin_and_are_named(self):
        self.assertEqual(sha(self.raw), PREDECESSOR["sha256"])
        self.assertEqual(len(self.raw), PREDECESSOR["bytes"])
        self.assertEqual(self.raw, pins.encode(self.predecessor))
        self.assertEqual(self.predecessor["schema"], PREDECESSOR["schema"])
        self.assertEqual((self.predecessor["profile"], self.predecessor["status"]), ("rapp-workspace/1", "core"))
        self.assertEqual(self.successor["predecessors"], [PREDECESSOR])
        self.assertEqual(pins.PREDECESSORS, (PREDECESSOR,))

    def test_normative_and_runtime_sections_carry_forward_unchanged(self):
        self.assertEqual(list(self.successor), [*self.predecessor, "predecessors"])
        self.assertEqual(self.predecessor["normative"], self.successor["normative"])
        old = {item["path"]: item for item in self.predecessor["reference"]}
        new = {item["path"]: item for item in self.successor["reference"]}
        self.assertEqual(list(old), list(new))
        self.assertEqual({path for path in old if old[path] != new[path]}, {"reference/pins.py"})
        for key in self.predecessor:
            if key not in {"schema", "reference", "repository_evidence"}:
                self.assertEqual(self.predecessor[key], self.successor[key], key)
        for item in self.predecessor["normative"]:
            raw = read_file(WORKSPACE / item["path"])
            self.assertEqual((sha(raw), len(raw)), (item["sha256"], item["bytes"]), item["path"])
        old_paths = [item["path"] for item in self.predecessor["repository_evidence"]]
        self.assertEqual({path for path in old_paths if pins.front_door(path)}, set(WORKSPACE_FRONT_DOORS))
        self.assertEqual([path for path in old_paths if not pins.front_door(path)], list(REPOSITORY_EVIDENCE))

    def test_retained_591e014_profile_names_predecessor_and_verifies_as_history(self):
        record = SDK.PINS[DISPLACED_PIN]
        self.assertEqual((record["status"], record["fresh_install"], record["sequence"]),
                         ("migration-source-only", False, 2))
        self.assertEqual(record["profile_artifact"]["sha256"], DISPLACED_PROFILE_SHA256)
        raw = SDK._pin_profile_raw(DISPLACED_PIN)
        self.assertEqual(hashlib.sha256(raw).hexdigest(), DISPLACED_PROFILE_SHA256)
        self.assertEqual(raw, (SDK_ROOT / record["profile_artifact"]["path"]).read_bytes())
        sibling = json.loads(raw)["workspace_sibling"]
        self.assertEqual((sibling["spec_sha256"], sibling["manifest_sha256"]),
                         (SPEC_SHA256, PREDECESSOR["sha256"]))
        fixture = SDK_ROOT / "fixtures" / "prior-release-591e014"
        root = self.base / ("history-" + uuid.uuid4().hex)
        shutil.copytree(fixture, root)
        root.chmod(0o700)
        for path in [root / ".rapp-work", *(root / ".rapp-work").rglob("*")]:
            path.chmod(0o700 if path.is_dir() else 0o600)
        verified = SDK.verify_workspace(root)
        self.assertEqual((verified["installed_pin"], verified["current_pin"]), (DISPLACED_PIN, DISPLACED_PIN))
        generation = root / ".rapp-work" / "generations" / DISPLACED_PIN / "profile.json"
        self.assertEqual(generation.read_bytes(), raw)

    def test_every_retained_sdk_profile_names_a_retained_workspace_manifest(self):
        retained = {item["sha256"] for item in self.successor["predecessors"]}
        for pin, record in SDK.PINS.items():
            with self.subTest(pin=pin):
                sibling = json.loads(SDK._pin_profile_raw(pin))["workspace_sibling"]
                expected = SUCCESSOR_SHA256 if pin == CURRENT_PIN else PREDECESSOR["sha256"]
                self.assertEqual(sibling["manifest_sha256"], expected)
                self.assertIn(sibling["manifest_sha256"], retained | {SUCCESSOR_SHA256})
                self.assertEqual(sibling["spec_sha256"], SPEC_SHA256)

    def test_old_runtime_pin_is_history_and_cannot_qualify_new_execution(self):
        target = self.base / ("old-runtime-" + uuid.uuid4().hex)
        with self.assertRaisesRegex(Refusal, "runtime-qualification-required"):
            Controller(self.core, target, self.policy(PREDECESSOR["sha256"]),
                       clock=lambda: NOW, activation_mode="synthetic")
        self.assertFalse(target.exists())

    def test_receipts_emitted_by_the_old_runtime_remain_inspectable_history(self):
        identity = json.loads(read_file(PRIOR_RUNTIME_RECEIPTS / "rappid.json"))
        names = sorted((path.name for path in (PRIOR_RUNTIME_RECEIPTS / "frames").iterdir()),
                       key=lambda name: int(name.removesuffix(".json")))
        self.assertEqual(names, [f"{seq}.json" for seq in range(len(names))])
        frames = [read_file(PRIOR_RUNTIME_RECEIPTS / "frames" / name) for name in names]
        with patch("safe_kernel.read_file", side_effect=AssertionError("history consulted the current runtime")):
            proof = verify_historical_archive(self.core, frames, identity["rappid"])
        self.assertEqual(proof, {
            "rapp_integrity": "verified", "frames": 15, "observation": "historical-receipts-only",
            "semantic_fidelity": "historical-evaluator-unavailable", "current_authorization": "not-inferred",
            "safe_deployment": "disabled",
        })
        payloads = [self.core.parse(raw)["payload"] for raw in frames]
        runtimes = [payload["runtime_sha256"] for payload in payloads if "runtime_sha256" in payload]
        self.assertEqual((len(runtimes), set(runtimes)), (11, {PREDECESSOR["sha256"]}))
        self.assertEqual({payload["activation_mode"] for payload in payloads}, {"synthetic"})
        receipts = [payload for payload in payloads if payload["schema"].endswith("-receipt")]
        self.assertTrue(receipts)
        self.assertEqual({payload["validator_pin"] for payload in receipts}, {SPEC_SHA256})
        target = self.base / ("replay-" + uuid.uuid4().hex)
        with self.assertRaisesRegex(Refusal, "runtime-qualification-required"):
            Controller(self.core, target, self.policy(runtimes[0]), clock=lambda: NOW, activation_mode="synthetic")
        self.assertFalse(target.exists())


class SuccessorPinTests(FrontDoorFixture):
    """Property 2: the new pin verifies everywhere it is recorded."""

    def test_successor_manifest_is_the_exact_regeneration_and_lists_no_front_door(self):
        raw = read_file(WORKSPACE / "manifest.json")
        self.assertEqual(sha(raw), SUCCESSOR_SHA256)
        self.assertEqual(raw, pins.encode(pins.manifest()))
        value = json.loads(raw)
        self.assertEqual(value["schema"], "rapp-workspace-file-manifest/2")
        self.assertEqual([item["path"] for item in value["repository_evidence"]], list(REPOSITORY_EVIDENCE))
        self.assertFalse([path for path in pins.listed_paths(value) if pins.front_door(path)])
        sdk = json.loads((SDK_ROOT / "manifest.json").read_bytes())
        self.assertEqual(sdk["schema"], "rapp-work-sdk-file-manifest/1")
        self.assertFalse([path for path in SDK_PINS.listed_paths(sdk) if SDK_PINS.front_door(path)])
        self.assertNotIn("reference/README.md", [item["path"] for item in sdk["reference"]])

    def test_pins_pass_for_both_identities(self):
        workspace = self.run_tool(REPO, REPO / "tools/frame_lens.py", "pins")
        sdk = self.run_tool(REPO, SDK_ROOT / "reference/pins.py")
        self.assertEqual(workspace.returncode, 0, workspace.stdout + workspace.stderr)
        self.assertEqual(sdk.returncode, 0, sdk.stdout + sdk.stderr)
        self.assertTrue(workspace.stdout.strip().endswith("PASS"))
        self.assertTrue(sdk.stdout.strip().endswith("PASS"))

    def test_index_and_current_sdk_profile_agree_with_the_successor(self):
        index = json.loads((REPO / "protocols/index.json").read_bytes())
        self.assertEqual([item["name"] for item in index["profiles"]],
                         ["rapp-hive/1", "rapp-federation/1", "rapp-workspace/1", "rapp-work-sdk/1"])
        self.assertGreaterEqual(index["generated_utc"], "2026-09-18T15:00:00.000Z")
        workspace = next(item for item in index["profiles"] if item["name"] == "rapp-workspace/1")
        raw = read_file(WORKSPACE / "manifest.json")
        self.assertEqual((workspace["manifest_sha256"], workspace["manifest_bytes"]), (SUCCESSOR_SHA256, len(raw)))
        self.assertEqual(workspace["spec_sha256"], SPEC_SHA256)
        self.assertEqual(workspace, pins.index_profile())
        sdk = next(item for item in index["profiles"] if item["name"] == "rapp-work-sdk/1")
        self.assertEqual((sdk["current_pin"], sdk["rapp_work_commit"]), (CURRENT_PIN, CURRENT_PIN))
        self.assertEqual(sdk["manifest_sha256"], hashlib.sha256((SDK_ROOT / "manifest.json").read_bytes()).hexdigest())
        expected = {
            "profile": "rapp-workspace/1", "spec_sha256": SPEC_SHA256, "manifest_sha256": SUCCESSOR_SHA256,
            "identity_unchanged": True, "normative_bytes_unchanged": True,
        }
        vendor = REPO / ".github/skills/rapp-work-sdk/vendor/rapp-work-sdk/1"
        for root in (SDK_ROOT, vendor):
            for name in ("profile.json", "manifest.json"):
                with self.subTest(root=root.name, name=name):
                    self.assertEqual(json.loads((root / name).read_bytes())["workspace_sibling"], expected)
        self.assertEqual(SDK.PROFILE["current_pin"], CURRENT_PIN)
        self.assertEqual(SDK.PARENT_PIN["commit"], CURRENT_PIN)

    def test_qualification_succeeds_with_the_successor_runtime(self):
        target = self.base / ("successor-" + uuid.uuid4().hex)
        controller = Controller(self.core, target, self.policy(SUCCESSOR_SHA256),
                                clock=lambda: NOW, activation_mode="synthetic")
        self.addCleanup(controller.close)
        image = controller.qualify()
        self.assertEqual(image.sha256, reference_sha256("reference/total_eval.py"))

    def test_generators_reproduce_every_committed_pin_through_their_own_write_paths(self):
        root = self.scratch("regenerate")
        commands = (
            (root / "protocols/rapp-workspace/1/reference/pins.py", "--write", "--write-index"),
            (root / "protocols/rapp-work-sdk/1/reference/pins.py", "--write-parent-profile", "--write", "--write-index"),
            (root / "tools/skill_locks.py", "--sync-work-sdk-vendor", "--write", "rapp-work-sdk"),
            (root / "tools/skill_locks.py", "--bind-private-hive", "--write", "rapp-private-hive"),
        )
        for command in commands:
            completed = self.run_tool(root, *command)
            self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        for top in ("protocols", ".github"):
            for path in sorted((REPO / top).rglob("*")):
                if path.is_file() and "__pycache__" not in path.parts and path.suffix != ".pyc" \
                        and path.name != ".DS_Store":
                    relative = path.relative_to(REPO)
                    self.assertEqual((root / relative).read_bytes(), path.read_bytes(), relative.as_posix())


class EditableFrontDoorTests(FrontDoorFixture):
    """Property 3: README edits leave both identities byte-identical and qualification succeeding."""

    def assert_identities_unchanged(self, result):
        committed_sdk = hashlib.sha256((SDK_ROOT / "manifest.json").read_bytes()).hexdigest()
        self.assertEqual(result["workspace_manifest"], SUCCESSOR_SHA256)
        self.assertEqual(result["workspace_committed"], SUCCESSOR_SHA256)
        self.assertEqual(result["sdk_manifest"], committed_sdk)
        self.assertEqual(result["sdk_committed"], committed_sdk)
        self.assertEqual(result["workspace_pins"][0], 0, result["workspace_pins"])
        self.assertEqual(result["sdk_pins"][0], 0, result["sdk_pins"])
        self.assertEqual(result["qualification"], "qualified: " + reference_sha256("reference/total_eval.py"))
        self.assertTrue(result["controller_created"])

    def test_editing_each_front_door_keeps_both_identities_and_qualification(self):
        root = self.scratch("edit-each-front-door")
        for relative in (*WORKSPACE_FRONT_DOORS, SDK_FRONT_DOOR):
            with self.subTest(front_door=relative):
                path = root / relative
                original = path.read_bytes()
                edit = lambda item: item.write_bytes(HEADER + original + b"\nSynthetic editable front-door line.\n")
                with self.damaged(path, edit):
                    self.assertNotEqual(path.read_bytes(), original)
                    self.assert_identities_unchanged(self.probe(root))

    def test_no_readme_anywhere_in_the_repository_is_part_of_either_identity(self):
        root = self.scratch("edit-every-readme")
        edited = sorted(path for path in root.rglob("*") if path.is_file() and pins.front_door(path.name))
        self.assertLessEqual({root / item for item in (*WORKSPACE_FRONT_DOORS, SDK_FRONT_DOOR)}, set(edited))
        for path in edited:
            path.write_bytes(HEADER + b"Rewritten synthetic front door.\n")
        self.assert_identities_unchanged(self.probe(root))


class NormativeEditTests(FrontDoorFixture):
    """Property 4: normative and AI-instruction edits move the identity and qualification refuses."""

    WORKSPACE_EDITS = (
        ("SPEC.md", "runtime-qualification-required"),
        ("SKILL.md", "runtime-qualification-required"),
        ("protocols/rapp-workspace/1/SPEC.md", "wrong-validator-or-spec-pin"),
        (".github/skills/rapp-workspace/SKILL.md", "runtime-qualification-required"),
        (".github/skills/autonomous-rapp-estate-manager/SKILL.md", "runtime-qualification-required"),
        ("tools/frame_lens.py", "runtime-qualification-required"),
        ("tests/test_safe_kernel.py", "runtime-qualification-required"),
        ("tests/test_p0_hardening.py", "runtime-qualification-required"),
        ("protocols/rapp-workspace/1/safety-matrix.json", "runtime-qualification-required"),
        ("protocols/rapp-workspace/1/schemas/common.schema.json", "runtime-qualification-required"),
        ("protocols/rapp-workspace/1/reference/total_eval.py", "runtime-qualification-required"),
    )

    def test_normative_and_instruction_edits_move_the_identity_and_refuse_qualification(self):
        committed_sdk = hashlib.sha256((SDK_ROOT / "manifest.json").read_bytes()).hexdigest()
        root = self.scratch("normative-edits")
        for relative, reason in self.WORKSPACE_EDITS:
            with self.subTest(normative=relative), self.damaged(root / relative, append_marker):
                result = self.probe(root)
                self.assertNotEqual(result["workspace_manifest"], SUCCESSOR_SHA256)
                self.assertRegex(result["workspace_manifest"], r"^[0-9a-f]{64}$")
                self.assertEqual(result["workspace_committed"], SUCCESSOR_SHA256)
                self.assertNotEqual(result["workspace_pins"][0], 0)
                self.assertTrue(result["workspace_pins"][1].endswith("FAIL"), result["workspace_pins"])
                self.assertEqual(result["qualification"], "refused: " + reason)
                self.assertFalse(result["controller_created"])
                self.assertEqual(result["sdk_manifest"], committed_sdk)

    def test_retained_predecessor_tamper_or_loss_refuses_pins_and_qualification(self):
        root = self.scratch("predecessor-damage")
        retained = root / "protocols/rapp-workspace/1" / PREDECESSOR["path"]
        for name, damage in (("tamper", append_marker), ("loss", lambda path: path.unlink())):
            with self.subTest(damage=name), self.damaged(retained, damage):
                result = self.probe(root)
                expected = ("retained-predecessor-manifest-changed" if name == "tamper"
                            else "unsafe directory or symlink")
                self.assertTrue(result["workspace_manifest"].startswith("refused: " + expected), result)
                self.assertTrue(result["qualification"].startswith("refused: " + expected), result)
                self.assertFalse(result["controller_created"])
                self.assertNotEqual(result["workspace_pins"][0], 0)
                self.assertIn("FAIL", result["workspace_pins"][1])

    def test_sdk_normative_edits_move_only_the_sdk_identity(self):
        root = self.scratch("sdk-normative-edits")
        for relative in ("protocols/rapp-work-sdk/1/SPEC.md", "protocols/rapp-work-sdk/1/reference/scaffold.py"):
            with self.subTest(normative=relative), self.damaged(root / relative, append_marker):
                result = self.probe(root)
                self.assertNotEqual(result["sdk_manifest"], result["sdk_committed"])
                self.assertNotEqual(result["sdk_pins"][0], 0)
                self.assertEqual(result["workspace_manifest"], SUCCESSOR_SHA256)
                self.assertEqual(result["qualification"], "qualified: " + reference_sha256("reference/total_eval.py"))


class FrontDoorRefusalTests(FrontDoorFixture):
    """Both generators refuse to list a front door; retained history is never regenerated."""

    def test_front_door_rule_is_exact(self):
        for module in (pins, SDK_PINS):
            for path in ("README.md", "readme.md", "protocols/ReadMe.MD", "README", "docs/README.rst"):
                self.assertTrue(module.front_door(path), path)
            for path in ("SPEC.md", "SKILL.md", "reference/pins.py", "readme_parser.py", "READMEFIRST.md"):
                self.assertFalse(module.front_door(path), path)

    def test_workspace_generator_refuses_to_list_any_front_door(self):
        for candidate in (*WORKSPACE_FRONT_DOORS, SDK_FRONT_DOOR):
            with self.subTest(candidate=candidate):
                with patch.object(pins, "REPOSITORY_EVIDENCE", (*pins.REPOSITORY_EVIDENCE, candidate)):
                    with self.assertRaisesRegex(Refusal, "front-door-not-pinnable: " + re.escape(candidate)):
                        pins.manifest()
        readme = {**PREDECESSOR, "path": "history/" + PREDECESSOR["sha256"] + "/README.md"}
        with patch.object(pins, "PREDECESSORS", (readme,)):
            with self.assertRaisesRegex(Refusal, "retained-predecessor-record-invalid"):
                pins.manifest()

    def test_prototype_manifest_can_never_be_listed_as_a_predecessor(self):
        root = self.scratch("prototype-predecessor")
        workspace = root / "protocols/rapp-workspace/1"
        raw = (root / "protocols/rapp-workspace/prototypes/grail-1.0/manifest.json").read_bytes()
        digest = hashlib.sha256(raw).hexdigest()
        retained = workspace / "history" / digest / "manifest.json"
        retained.parent.mkdir(parents=True)
        retained.write_bytes(raw)
        entry = {"schema": "rapp-workspace-file-manifest/1", "path": f"history/{digest}/manifest.json",
                 "sha256": digest, "bytes": len(raw)}
        self.assertEqual(json.loads(raw)["schema"], entry["schema"])
        with patch.object(pins, "ROOT", workspace), patch.object(pins, "REPO", root), \
                patch.object(pins, "PREDECESSORS", (*pins.PREDECESSORS, entry)):
            with self.assertRaisesRegex(Refusal, "retained-predecessor-manifest-mismatch"):
                pins.manifest()

    def test_sdk_generator_refuses_to_list_any_front_door(self):
        root = self.scratch("sdk-readme")
        for directory in ("fixtures", "history", "reference"):
            readme = root / "protocols/rapp-work-sdk/1" / directory / "README.md"
            with self.subTest(directory=directory), \
                    self.damaged(readme, lambda path: path.write_bytes(b"synthetic\n")):
                result = self.probe(root)
                if directory == "reference":
                    self.assertEqual(result["sdk_manifest"], result["sdk_committed"])
                    self.assertEqual(result["sdk_pins"][0], 0, result["sdk_pins"])
                else:
                    self.assertEqual(result["sdk_manifest"],
                                     f"refused: front-door bytes are never pinned: {directory}/README.md")
                    self.assertNotEqual(result["sdk_pins"][0], 0)
                    self.assertIn("front-door bytes are never pinned", result["sdk_pins"][1])

    def test_sdk_generator_never_manufactures_displaced_history_from_other_bytes(self):
        root = self.scratch("sdk-displaced-history")
        retained = root / "protocols/rapp-work-sdk/1/history" / DISPLACED_PIN / "profile.json"
        retained.unlink()
        retained.parent.rmdir()
        completed = self.run_tool(root, root / "protocols/rapp-work-sdk/1/reference/pins.py",
                                  "--write-parent-profile", "--write", "--write-index")
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("current profile is not the accepted displaced profile", completed.stdout)
        self.assertFalse(retained.parent.exists())

    def test_sdk_generator_refuses_to_reseal_over_tampered_retained_profiles(self):
        root = self.scratch("sdk-history")
        for pin in SDK_PINS.HISTORICAL_PROFILES:
            retained = root / "protocols/rapp-work-sdk/1/history" / pin / "profile.json"
            with self.subTest(pin=pin), self.damaged(retained, append_marker):
                sealed = ("protocols/rapp-work-sdk/1/profile.json", "protocols/rapp-work-sdk/1/parent-pin.json",
                          "protocols/rapp-work-sdk/1/manifest.json", "protocols/index.json")
                before = {name: (root / name).read_bytes() for name in sealed}
                completed = self.run_tool(root, root / "protocols/rapp-work-sdk/1/reference/pins.py",
                                          "--write-parent-profile", "--write", "--write-index")
                self.assertNotEqual(completed.returncode, 0)
                self.assertRegex(completed.stdout, "does not retain the exact source profile"
                                 "|retained displaced profile bytes changed")
                self.assertEqual({name: (root / name).read_bytes() for name in sealed}, before)


if __name__ == "__main__":
    unittest.main()
