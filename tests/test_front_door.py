"""G24 vectors: an additive successor keeps front doors editable after the owner's switch.

The current Workspace/1 identity never moves here. Public synthetic data only.
"""

from contextlib import contextmanager
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import stat
import subprocess
import sys
import unittest
from unittest.mock import patch
import uuid

REPO = Path(__file__).resolve().parents[1]
WORKSPACE = REPO / "protocols" / "rapp-workspace" / "1"
REFERENCE = WORKSPACE / "reference"
SUCCESSOR = WORKSPACE / "successor"
CANDIDATE_FILE = SUCCESSOR / "manifest.json.staged"
SDK_ROOT = REPO / "protocols" / "rapp-work-sdk" / "1"
sys.path.insert(0, str(REFERENCE))
from common import Parent, Refusal, read_file, sha
import pins
from safe_kernel import Controller, ExternalPolicy, Scope


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


TOOL = load_module("workspace_successor_front_door", REPO / "tools" / "workspace_successor.py")

SPEC_SHA256 = "80135ae05e532f11810d31a5cf974050a8332c18bd45f16879a7286f213edfab"
CURRENT = {"path": "protocols/rapp-workspace/1/manifest.json",
            "sha256": "f1165f947cb5d7554906012a174a854b28454403e41e8166925a364a68680370", "bytes": 7990}
SUCCESSOR_SHA256 = "e99a51d355bd66c71017f4451cdd54bc47ed2b99c4fe0d939e1c494288148814"
PREDECESSOR = {
    "schema": "rapp-workspace-file-manifest/1",
    "path": "history/" + CURRENT["sha256"] + "/manifest.json",
    "sha256": CURRENT["sha256"],
    "bytes": CURRENT["bytes"],
}
SWITCHED = (
    ".github/skills/autonomous-rapp-estate-manager/SKILL.md",
    ".github/skills/rapp-workspace/SKILL.md",
    "SKILL.md",
    "protocols/rapp-workspace/1/reference/pins.py",
)
WORKSPACE_FRONT_DOORS = (
    "README.md",
    "protocols/README.md",
    "protocols/rapp-workspace/1/reference/README.md",
    "protocols/rapp-workspace/prototypes/README.md",
)
# The root SPEC.md declares itself navigation, not a second normative specification.
NAVIGATION = (*WORKSPACE_FRONT_DOORS, "SPEC.md")
REPOSITORY_EVIDENCE = (
    "SKILL.md", "tools/frame_lens.py", "tests/test_safe_kernel.py",
    "tests/test_p0_hardening.py", ".github/skills/rapp-workspace/SKILL.md",
    ".github/skills/autonomous-rapp-estate-manager/SKILL.md",
)
INSTANCE = "rappid:@fixture/front-door:" + "b" * 64
NOW = "2026-09-25T12:00:00.000Z"
HEADER = (
    b"<!-- synthetic network header -->\n"
    b"[![RAPP/1](https://example.com/badge.svg)](https://example.com/rapp-1) "
    b"[Start here](https://example.com/start-here)\n\n"
)
PROBE = r"""
import contextlib, io, json, sys
from pathlib import Path
repo, rapp1, controller, instance, spec_sha256, runtime_sha256, now = sys.argv[1:8]
repo, controller = Path(repo), Path(controller)
sys.path.insert(0, str(repo / "protocols/rapp-workspace/1/reference"))
from common import Parent, Refusal, read_file, sha
import pins
from safe_kernel import Controller, ExternalPolicy, Scope
result = {"committed": sha(read_file(repo / "protocols/rapp-workspace/1/manifest.json"))}
try:
    result["regenerated"] = sha(pins.encode(pins.manifest()))
except Refusal as error:
    result["regenerated"] = "refused: " + str(error)
output = io.StringIO()
sys.argv = ["pins.py"]
try:
    with contextlib.redirect_stdout(output):
        code = pins.main()
except (OSError, Refusal) as error:
    code = "raised: " + str(error)
result["pins"] = [code, output.getvalue().strip()]
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


def copied_files(base, tops):
    """Relative paths of the files the tool's copy holds under tops: no symlinks, no scratch or build products."""
    found = []
    for top in tops:
        source = base / top
        if source.is_symlink():
            continue
        if source.is_file():
            found.append(top)
            continue
        for current, directories, files in os.walk(source):
            skipped = TOOL.skip_links(current, directories + files)
            directories[:] = [name for name in directories if name not in skipped]
            found += [Path(current, name).relative_to(base).as_posix() for name in files if name not in skipped]
    return sorted(found)


def absolute_path(value):
    return None if value is None else str(Path(value).absolute())


def rapp1_environment(environ):
    """Probes run inside scratch copies, so a relative RAPP/1 path is resolved once, as conformance.py does."""
    rapp1 = absolute_path(environ.get("RAPP1_PATH"))
    environment = {**environ, "PYTHONDONTWRITEBYTECODE": "1"}
    if rapp1 is not None:
        environment["RAPP1_PATH"] = rapp1
    return rapp1, environment


def append_marker(path):
    marker = b"\n# synthetic normative edit\n" if path.suffix == ".py" else b"\n"
    path.write_bytes(path.read_bytes() + marker)


def staged_path(root, canonical):
    return root / "protocols/rapp-workspace/1/successor/staged" / (canonical + ".staged")


def candidate():
    return json.loads(read_file(CANDIDATE_FILE))


def total_eval_sha256():
    return next(item["sha256"] for item in candidate()["reference"] if item["path"] == "reference/total_eval.py")


class FrontDoorFixture(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rapp1, cls.environment = rapp1_environment(os.environ)
        cls.core = Parent(cls.rapp1)
        cls.base = REPO / ".validation" / "test-artifacts" / ("front-door-" + uuid.uuid4().hex)
        cls.base.mkdir(parents=True, mode=0o700)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.base, ignore_errors=True)

    def scratch(self, name):
        """Copy the working tree as the tool does, skipping every symlink so no test write can leave the copy."""
        root = self.base / (name + "-" + uuid.uuid4().hex) / "repo"
        shutil.copytree(REPO, root, symlinks=True, ignore=TOOL.skip_links, copy_function=shutil.copyfile)
        links = [os.path.join(current, entry) for current, directories, files in os.walk(root)
                 for entry in directories + files if os.path.islink(os.path.join(current, entry))]
        self.assertEqual(links, [], "the scratch tree must not contain symlinks")
        return root

    def switched(self, name):
        """Apply the owner's Workspace-side switch to a scratch copy, independently of the tool."""
        root = self.scratch(name)
        workspace = root / "protocols/rapp-workspace/1"
        retained = workspace / PREDECESSOR["path"]
        current = (workspace / "manifest.json").read_bytes()
        retained.parent.mkdir(parents=True, exist_ok=True)
        if retained.exists():
            self.assertEqual(retained.read_bytes(), current)
        else:
            retained.write_bytes(current)
        for canonical in SWITCHED:
            (root / canonical).write_bytes(staged_path(root, canonical).read_bytes())
        shutil.rmtree(workspace / "successor")
        completed = self.run_tool(root, workspace / "reference/pins.py", "--write", "--write-index")
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        self.assertTrue(completed.stdout.strip().endswith("PASS"), completed.stdout)
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
                              capture_output=True, text=True, timeout=300, env=self.environment)

    def probe(self, root, runtime_sha256=SUCCESSOR_SHA256):
        controller = root.parent / ("controller-" + uuid.uuid4().hex)
        completed = self.run_tool(root, "-c", PROBE, root, self.rapp1, controller, INSTANCE,
                                  SPEC_SHA256, runtime_sha256, NOW)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        return json.loads(completed.stdout)

    def policy(self, runtime_sha256):
        return ExternalPolicy(INSTANCE, "fixture-world", SPEC_SHA256, runtime_sha256,
                              frozenset({"capture"}), (Scope("fixture", "front-door"),))

    def tool(self, root, *arguments):
        leftovers = root / ".validation/workspace-successor"
        before = set(os.listdir(leftovers)) if leftovers.is_dir() else set()
        completed = self.run_tool(root, root / "tools/workspace_successor.py", *arguments)
        after = set(os.listdir(leftovers)) if leftovers.is_dir() else set()
        self.assertEqual(after - before, set(), "every scratch copy is removed after the run")
        return completed.returncode, completed.stdout.strip()


class CurrentIdentityTests(FrontDoorFixture):
    """Property 1: the candidate is additive; the current identity never moves and no consumer switches."""

    def test_current_manifest_and_its_index_entry_are_the_frozen_identity(self):
        raw = read_file(WORKSPACE / "manifest.json")
        self.assertEqual((sha(raw), len(raw)), (CURRENT["sha256"], CURRENT["bytes"]))
        self.assertEqual(raw, pins.encode(pins.manifest()))
        self.assertEqual(json.loads(raw)["schema"], "rapp-workspace-file-manifest/1")
        self.assertTrue(pins.check_index())
        index = json.loads((REPO / "protocols/index.json").read_bytes())
        core = [item for item in index["profiles"] if item["name"].startswith("rapp-workspace/")]
        self.assertEqual(core, [pins.index_profile()])
        self.assertEqual(core[0]["manifest_sha256"], CURRENT["sha256"])
        self.assertEqual(index["workspace_latest"], "rapp-workspace/1")

    def test_consumers_still_pin_the_current_manifest(self):
        vendor = REPO / ".github/skills/rapp-work-sdk/vendor/rapp-work-sdk/1"
        for root in (SDK_ROOT, vendor):
            for name in ("profile.json", "manifest.json"):
                with self.subTest(root=root.name, name=name):
                    sibling = json.loads((root / name).read_bytes())["workspace_sibling"]
                    self.assertEqual((sibling["spec_sha256"], sibling["manifest_sha256"]),
                                     (SPEC_SHA256, CURRENT["sha256"]))

    def test_the_candidate_grants_nothing_before_the_switch(self):
        target = self.base / ("candidate-" + uuid.uuid4().hex)
        with self.assertRaisesRegex(Refusal, "runtime-qualification-required"):
            Controller(self.core, target, self.policy(SUCCESSOR_SHA256), clock=lambda: NOW,
                       activation_mode="synthetic")
        self.assertFalse(target.exists())

    def test_until_the_switch_a_readme_edit_still_moves_the_frozen_identity(self):
        root = self.scratch("before-switch")
        path = root / "README.md"
        path.write_bytes(HEADER + path.read_bytes())
        result = self.probe(root, CURRENT["sha256"])
        self.assertEqual(result["committed"], CURRENT["sha256"])
        self.assertNotEqual(result["regenerated"], CURRENT["sha256"])
        self.assertTrue(result["pins"][1].endswith("FAIL"), result["pins"])
        self.assertEqual(result["qualification"], "refused: runtime-qualification-required")
        code, output = self.tool(root)
        self.assertEqual((code, output), (0, "Workspace/1 successor candidate (proposal 0024): PASS"))


class CandidateRecordTests(FrontDoorFixture):
    """Property 2: the candidate is recorded exactly and regenerates through the repository's tool."""

    def test_candidate_manifest_is_the_successor_and_pins_no_navigation(self):
        raw = read_file(CANDIDATE_FILE)
        self.assertEqual(sha(raw), SUCCESSOR_SHA256)
        value, old = json.loads(raw), json.loads(read_file(WORKSPACE / "manifest.json"))
        self.assertEqual(value["schema"], "rapp-workspace-file-manifest/2")
        self.assertEqual(list(value), [*old, "predecessors"])
        self.assertEqual(value["predecessors"], [PREDECESSOR])
        self.assertEqual(value["normative"], old["normative"])
        for key in old:
            if key not in {"schema", "reference", "repository_evidence"}:
                self.assertEqual(value[key], old[key], key)
        before = {item["path"]: item for item in old["reference"]}
        after = {item["path"]: item for item in value["reference"]}
        self.assertEqual(list(before), list(after))
        self.assertEqual({path for path in before if before[path] != after[path]}, {"reference/pins.py"})
        self.assertEqual([item["path"] for item in value["repository_evidence"]], list(REPOSITORY_EVIDENCE))
        old_paths = [item["path"] for item in old["repository_evidence"]]
        self.assertEqual({path for path in old_paths if TOOL.front_door(path)}, set(WORKSPACE_FRONT_DOORS))
        self.assertEqual([path for path in old_paths if path not in NAVIGATION], list(REPOSITORY_EVIDENCE))
        self.assertNotIn("README", json.dumps(value).upper())
        records = [*value["normative"], *value["reference"], *value["repository_evidence"],
                   value["provenance"], value["prototype_catalog"]]
        self.assertEqual({tuple(item) for item in records}, {("path", "sha256", "bytes")})
        self.assertEqual([list(item) for item in value["predecessors"]], [["schema", "path", "sha256", "bytes"]])
        self.assertEqual([item["path"] for item in value["normative"]][:2], ["SPEC.md", "safety-matrix.json"])
        schemas = [item["path"] for item in value["normative"]][2:]
        self.assertEqual(schemas, sorted(schemas))
        self.assertEqual([item["path"] for item in value["reference"]], sorted(item["path"] for item in value["reference"]))
        self.assertEqual(raw, pins.encode(value))

    def test_staged_bytes_are_exactly_the_switched_pinned_files(self):
        staged = TOOL.staged_files()
        self.assertEqual(sorted(staged), sorted(SWITCHED))
        value, old = candidate(), json.loads(read_file(WORKSPACE / "manifest.json"))

        def pinned(manifest):
            records = {"protocols/rapp-workspace/1/" + item["path"]: item
                       for key in ("normative", "reference") for item in manifest[key]}
            records.update({item["path"]: item for item in manifest["repository_evidence"]})
            return records

        new, current = pinned(value), pinned(old)
        for canonical, raw in staged.items():
            with self.subTest(canonical=canonical):
                self.assertEqual((new[canonical]["sha256"], new[canonical]["bytes"]), (sha(raw), len(raw)))
                live = read_file(REPO / canonical)
                self.assertEqual((current[canonical]["sha256"], current[canonical]["bytes"]), (sha(live), len(live)))
                self.assertNotEqual(raw, live)
        for canonical in (path for path in new if path not in staged):
            live = read_file(REPO / canonical)
            self.assertEqual((new[canonical]["sha256"], new[canonical]["bytes"]), (sha(live), len(live)), canonical)
        self.assertEqual(staged["SKILL.md"], staged[".github/skills/rapp-workspace/SKILL.md"])
        self.assertEqual(read_file(REPO / "SKILL.md"), read_file(REPO / ".github/skills/rapp-workspace/SKILL.md"))

    def test_staged_instructions_never_call_navigation_verified(self):
        staged = TOOL.staged_files()
        delegation = re.compile(r"(?i)verified\W+(?:[\w/-]+\W+){0,3}?(?:readme|docs)")
        for canonical in SWITCHED[:3]:
            with self.subTest(canonical=canonical):
                live = " ".join(read_file(REPO / canonical).decode().split())
                text = " ".join(staged[canonical].decode().split())
                self.assertRegex(live, delegation)
                self.assertNotRegex(text, delegation)
                self.assertNotIn(" in README", text)
                self.assertIn("READMEs", text)
                self.assertRegex(text, r"READMEs (and the root `SPEC.md` )?are editable, unpinned navigation")
        text = staged["SKILL.md"].decode()
        for command in (
            "python3 -m py_compile tools/*.py protocols/rapp-workspace/1/reference/*.py tests/*.py",
            "python3 -B -m unittest discover -s .github/skills/rapp-private-hive/tests -v",
            "python3 -B protocols/rapp-hive/1/reference/hive_conformance.py",
            "python3 -B protocols/rapp-federation/1/reference/schema_source.py --check",
            "python3 -B protocols/rapp-federation/1/reference/conformance.py",
        ):
            self.assertIn(command, text)

    def test_index_records_exactly_one_candidate_that_is_not_accepted(self):
        index = json.loads((REPO / "protocols/index.json").read_bytes())
        entries = [item for item in index["profiles"] if item["name"] == "rapp-workspace-file-manifest/2"]
        self.assertEqual(entries, [TOOL.candidate_entry()])
        entry = entries[0]
        self.assertEqual((entry["status"], entry["authority"], entry["acceptance"]), ("candidate", False, "owner-only"))
        self.assertEqual(entry["successor_of"], CURRENT)
        self.assertEqual(entry["manifest_path"], "protocols/rapp-workspace/1/successor/manifest.json.staged")
        self.assertEqual((entry["manifest_sha256"], entry["manifest_bytes"]),
                         (SUCCESSOR_SHA256, len(read_file(CANDIDATE_FILE))))
        self.assertEqual(entry["spec_sha256"], SPEC_SHA256)
        self.assertFalse(entry["name"].startswith("rapp-workspace/"))
        self.assertTrue((REPO / entry["proposal"]).is_file())

    def test_tool_check_passes_and_write_reproduces_every_committed_byte(self):
        code, output = self.tool(REPO)
        self.assertEqual((code, output), (0, "Workspace/1 successor candidate (proposal 0024): PASS"))
        root = self.scratch("regenerate")
        index_path = root / "protocols/index.json"
        index = json.loads(index_path.read_bytes())
        index["profiles"] = [item for item in index["profiles"] if item["name"] != "rapp-workspace-file-manifest/2"]
        index_path.write_bytes(pins.encode(index))
        (root / "protocols/rapp-workspace/1/successor/manifest.json.staged").unlink()
        self.assertNotEqual(self.tool(root)[0], 0)
        code, output = self.tool(root, "--write")
        self.assertEqual((code, output), (0, "Workspace/1 successor candidate (proposal 0024): PASS"))
        for relative in ("protocols/index.json", "protocols/rapp-workspace/1/successor/manifest.json.staged"):
            self.assertEqual((root / relative).read_bytes(), (REPO / relative).read_bytes(), relative)
        self.assertEqual(self.tool(root, "--write"), (0, output))
        self.assertEqual(index_path.read_bytes(), (REPO / "protocols/index.json").read_bytes())
        stale_candidate = root / "protocols/rapp-workspace/1/successor/manifest.json.staged"
        stale_candidate.write_bytes(stale_candidate.read_bytes() + b"stale tail\n" * 64)
        stale_candidate.chmod(0o640)
        index_path.chmod(0o755)
        index = json.loads(index_path.read_bytes())
        entry = next(item for item in index["profiles"] if item["name"] == "rapp-workspace-file-manifest/2")
        entry["human_name"] += " (stale)" * 64
        index_path.write_bytes(pins.encode(index))
        self.assertNotEqual(self.tool(root)[0], 0)
        self.assertEqual(self.tool(root, "--write"), (0, output))
        for relative, mode in (("protocols/index.json", 0o755),
                               ("protocols/rapp-workspace/1/successor/manifest.json.staged", 0o640)):
            self.assertEqual((root / relative).read_bytes(), (REPO / relative).read_bytes(), relative)
            self.assertEqual(stat.S_IMODE((root / relative).stat().st_mode), mode, relative)
        for relative in copied_files(REPO, ("protocols", ".github", "SKILL.md", "SPEC.md", "README.md", "tools", "tests")):
            self.assertEqual((root / relative).read_bytes(), (REPO / relative).read_bytes(), relative)

    def test_diff_shows_only_the_switched_files(self):
        code, output = self.tool(REPO, "--diff")
        self.assertEqual(code, 0)
        self.assertEqual(sorted(re.findall(r"^\+\+\+ b/(.+)$", output, re.M)), sorted(SWITCHED))


class SwitchProofTests(FrontDoorFixture):
    """Property 3: after the owner's switch the candidate is current and front doors are editable."""

    def test_switch_makes_exactly_the_candidate_current_and_retires_its_index_entry(self):
        root = self.switched("switch")
        raw = (root / "protocols/rapp-workspace/1/manifest.json").read_bytes()
        self.assertEqual(raw, read_file(CANDIDATE_FILE))
        self.assertEqual(sha(raw), SUCCESSOR_SHA256)
        before = json.loads((REPO / "protocols/index.json").read_bytes())
        after = json.loads((root / "protocols/index.json").read_bytes())
        kept = [item for item in before["profiles"] if item["name"] != "rapp-workspace-file-manifest/2"]
        self.assertEqual([item["name"] for item in after["profiles"]], [item["name"] for item in kept])
        for old, new in zip(kept, after["profiles"]):
            if old["name"] != "rapp-workspace/1":
                self.assertEqual(new, old, old["name"])
            else:
                changed = {key for key in old if old[key] != new[key]}
                self.assertEqual(changed, {"manifest_sha256", "manifest_bytes"})
                self.assertEqual((new["manifest_sha256"], new["manifest_bytes"]), (SUCCESSOR_SHA256, len(raw)))
        self.assertEqual({key: value for key, value in after.items() if key != "profiles"},
                         {key: value for key, value in before.items() if key != "profiles"})
        expected = json.loads((REPO / "protocols/index.json").read_bytes())
        expected["profiles"] = [item for item in expected["profiles"] if item["name"] != "rapp-workspace-file-manifest/2"]
        core = next(item for item in expected["profiles"] if item["name"] == "rapp-workspace/1")
        core.update(manifest_sha256=SUCCESSOR_SHA256, manifest_bytes=len(raw))
        self.assertEqual((root / "protocols/index.json").read_bytes(), pins.encode(expected))
        pins_run = self.run_tool(root, root / "tools/frame_lens.py", "pins")
        self.assertEqual(pins_run.returncode, 0, pins_run.stdout + pins_run.stderr)
        self.assertEqual(pins_run.stdout.strip(), "Workspace/1 core spec/schema/runtime/index pins: PASS")

    def test_the_pinned_core_suites_pass_on_the_switched_tree(self):
        root = self.switched("core-suites")
        completed = subprocess.run([sys.executable, "-B", "-m", "unittest", "test_safe_kernel", "test_p0_hardening"],
                                   cwd=root / "tests", capture_output=True, text=True, timeout=600,
                                   env=self.environment)
        self.assertEqual(completed.returncode, 0, completed.stderr[-2000:])
        self.assertRegex(completed.stderr, r"Ran (\d{2,}) tests")
        self.assertIn("\nOK", completed.stderr)
        ran = int(re.search(r"Ran (\d+) tests", completed.stderr).group(1))
        self.assertEqual(ran, 81)

    def test_qualification_after_the_switch_accepts_only_the_successor(self):
        root = self.switched("qualify")
        result = self.probe(root)
        self.assertEqual(result["qualification"], "qualified: " + total_eval_sha256())
        self.assertEqual((result["committed"], result["regenerated"]), (SUCCESSOR_SHA256, SUCCESSOR_SHA256))
        old = self.probe(root, CURRENT["sha256"])
        self.assertEqual(old["qualification"], "refused: runtime-qualification-required")
        self.assertFalse(old["controller_created"])

    def assert_identity_kept(self, result):
        self.assertEqual((result["committed"], result["regenerated"]), (SUCCESSOR_SHA256, SUCCESSOR_SHA256))
        self.assertEqual(result["pins"][0], 0, result["pins"])
        self.assertEqual(result["qualification"], "qualified: " + total_eval_sha256())
        self.assertTrue(result["controller_created"])

    def test_after_the_switch_each_navigation_edit_keeps_the_identity_and_qualification(self):
        root = self.switched("edit-each-front-door")
        for relative in NAVIGATION:
            with self.subTest(navigation=relative):
                path = root / relative
                original = path.read_bytes()
                edit = lambda item: item.write_bytes(HEADER + original + b"\nSynthetic editable front-door line.\n")
                with self.damaged(path, edit):
                    self.assertNotEqual(path.read_bytes(), original)
                    self.assert_identity_kept(self.probe(root))

    def test_after_the_switch_no_readme_anywhere_is_part_of_the_identity(self):
        root = self.switched("edit-every-readme")
        edited = sorted(path for path in root.rglob("*") if path.is_file() and TOOL.front_door(path.name))
        self.assertLessEqual({root / item for item in WORKSPACE_FRONT_DOORS}, set(edited))
        for path in edited:
            path.write_bytes(HEADER + b"Rewritten synthetic front door.\n")
        self.assert_identity_kept(self.probe(root))

    PINNED_EDITS = (
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
        ("protocols/rapp-workspace/1/reference/pins.py", "runtime-qualification-required"),
        ("protocols/rapp-workspace/1/provenance.json", "runtime-qualification-required"),
        ("protocols/rapp-workspace/prototypes/index.json", "runtime-qualification-required"),
    )

    def test_after_the_switch_normative_and_instruction_edits_move_the_identity(self):
        root = self.switched("normative-edits")
        for relative, reason in self.PINNED_EDITS:
            with self.subTest(pinned=relative), self.damaged(root / relative, append_marker):
                result = self.probe(root)
                self.assertNotEqual(result["regenerated"], SUCCESSOR_SHA256)
                self.assertRegex(result["regenerated"], r"^[0-9a-f]{64}$")
                self.assertEqual(result["committed"], SUCCESSOR_SHA256)
                self.assertTrue(result["pins"][1].endswith("FAIL"), result["pins"])
                self.assertEqual(result["qualification"], "refused: " + reason)
                self.assertFalse(result["controller_created"])

    def test_after_the_switch_retained_predecessor_damage_refuses(self):
        root = self.switched("predecessor-damage")
        retained = root / "protocols/rapp-workspace/1" / PREDECESSOR["path"]
        for name, damage in (("tamper", append_marker), ("loss", lambda path: path.unlink())):
            with self.subTest(damage=name), self.damaged(retained, damage):
                result = self.probe(root)
                expected = ("retained-predecessor-manifest-changed" if name == "tamper"
                            else "retained-predecessor-missing")
                self.assertTrue(result["regenerated"].startswith("refused: " + expected), result)
                self.assertTrue(result["qualification"].startswith("refused: " + expected), result)
                self.assertFalse(result["controller_created"])
                self.assertIn("FAIL", result["pins"][1])

    def test_after_the_switch_a_leftover_candidate_entry_fails_the_pins(self):
        root = self.switched("leftover-candidate")
        index_path = root / "protocols/index.json"
        index = json.loads(index_path.read_bytes())
        index["profiles"].append(json.loads((REPO / "protocols/index.json").read_bytes())["profiles"][-1])
        self.assertEqual(index["profiles"][-1]["name"], "rapp-workspace-file-manifest/2")
        index_path.write_bytes(pins.encode(index))
        result = self.probe(root)
        self.assertEqual(result["pins"][0], 1, result["pins"])
        rewritten = self.run_tool(root, root / "protocols/rapp-workspace/1/reference/pins.py", "--write-index")
        self.assertEqual(rewritten.returncode, 0, rewritten.stdout)
        self.assertNotIn("rapp-workspace-file-manifest/2", index_path.read_text(encoding="utf-8"))


class RefusalTests(FrontDoorFixture):
    """The staged generator never pins a front door; the tool records nothing it cannot prove."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.switched_root = None

    def staged_generator(self):
        if type(self).switched_root is None:
            type(self).switched_root = self.switched("staged-generator")
        root = type(self).switched_root
        return root, load_module("staged_pins_" + uuid.uuid4().hex, root / "protocols/rapp-workspace/1/reference/pins.py")

    def test_front_door_rule_is_exact(self):
        _, generator = self.staged_generator()
        for rule in (TOOL.front_door, generator.front_door):
            for path in ("README.md", "readme.md", "protocols/ReadMe.MD", "README", "docs/README.rst", "README.json"):
                self.assertTrue(rule(path), path)
            for path in ("SPEC.md", "SKILL.md", "reference/pins.py", "readme_parser.py", "READMEFIRST.md"):
                self.assertFalse(rule(path), path)

    def test_staged_generator_refuses_a_front_door_in_every_section(self):
        root, generator = self.staged_generator()
        for front_door in WORKSPACE_FRONT_DOORS:
            with self.subTest(section="repository_evidence", front_door=front_door):
                with patch.object(generator, "REPOSITORY_EVIDENCE", (*generator.REPOSITORY_EVIDENCE, front_door)):
                    with self.assertRaisesRegex(Refusal, "front-door-not-pinnable: " + re.escape(front_door)):
                        generator.manifest()
        schema = root / "protocols/rapp-workspace/1/schemas/README.json"
        with self.subTest(section="normative"), self.damaged(schema, lambda path: path.write_bytes(b"{}\n")):
            with self.assertRaisesRegex(Refusal, "front-door-not-pinnable: schemas/README.json"):
                generator.manifest()
        module = root / "protocols/rapp-workspace/1/reference/README.py"
        with self.subTest(section="reference"), self.damaged(module, lambda path: path.write_bytes(b"# synthetic\n")):
            with self.assertRaisesRegex(Refusal, "front-door-not-pinnable: reference/README.py"):
                generator.manifest()
        original = generator.record
        for section, name in (("provenance", "provenance.json"),
                              ("prototype_catalog", "protocols/rapp-workspace/prototypes/index.json")):
            def renamed(base, relative, target=name):
                value = original(base, relative)
                return {**value, "path": "README.md"} if relative == target else value
            with self.subTest(section=section), patch.object(generator, "record", renamed):
                with self.assertRaisesRegex(Refusal, "front-door-not-pinnable: README.md"):
                    generator.manifest()
        readme = {**PREDECESSOR, "path": "history/" + PREDECESSOR["sha256"] + "/README.md"}
        for name, entry in (("README path", readme), ("extra key", {**PREDECESSOR, "note": "synthetic"})):
            with self.subTest(predecessor=name), patch.object(generator, "PREDECESSORS", (entry,)):
                with self.assertRaisesRegex(Refusal, "retained-predecessor-record-invalid"):
                    generator.manifest()

    def retained(self, root, value):
        raw = pins.encode(value)
        digest = sha(raw)
        path = root / "protocols/rapp-workspace/1/history" / digest / "manifest.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
        self.addCleanup(shutil.rmtree, path.parent, True)
        return {"schema": "rapp-workspace-file-manifest/1", "path": f"history/{digest}/manifest.json",
                "sha256": digest, "bytes": len(raw)}

    def test_only_a_retained_core_workspace_manifest_can_be_a_predecessor(self):
        root, generator = self.staged_generator()
        current = json.loads(read_file(root / "protocols/rapp-workspace/1" / PREDECESSOR["path"]))
        prototype = json.loads((root / "protocols/rapp-workspace/prototypes/grail-1.0/manifest.json").read_bytes())
        self.assertEqual(prototype["schema"], "rapp-workspace-file-manifest/1")
        cases = {
            "grail prototype": prototype,
            "not core": {**current, "status": "candidate"},
            "other profile": {**current, "profile": "rapp-workspace/grail-1.0"},
            "other schema": {**current, "schema": "rapp-workspace-file-manifest/0"},
        }
        for name, value in cases.items():
            with self.subTest(case=name):
                entry = self.retained(root, value)
                with patch.object(generator, "PREDECESSORS", (*generator.PREDECESSORS, entry)):
                    with self.assertRaisesRegex(Refusal, "retained-predecessor-manifest-mismatch"):
                        generator.manifest()

    def refused(self, root, reason):
        self.refused_with(root, (), reason)

    def refused_with(self, root, arguments, reason):
        code, output = self.tool(root, *arguments)
        self.assertEqual(code, 1, output)
        self.assertTrue(output.startswith("Workspace/1 successor candidate (proposal 0024): FAIL ("), output)
        self.assertIn(reason, output)

    def test_tool_refuses_unsafe_or_meaningless_staging(self):
        root = self.scratch("staging")
        staged = root / "protocols/rapp-workspace/1/successor/staged"
        cases = (
            ("no suffix", staged / "SKILL.md", lambda path: path.write_bytes(b"x\n"), "lacks the .staged suffix"),
            ("front door", staged / "README.md.staged", lambda path: path.write_bytes(b"x\n"),
             "front doors are never staged: README.md"),
            ("generated", staged / "protocols/index.json.staged", lambda path: path.write_bytes(b"{}\n"),
             "staged path is not switchable: protocols/index.json"),
            ("candidate itself", staged / "protocols/rapp-workspace/1/successor/manifest.json.staged.staged",
             lambda path: path.write_bytes(b"{}\n"),
             "staged path is not switchable: protocols/rapp-workspace/1/successor/manifest.json.staged"),
            ("new file", staged / "tools/new_tool.py.staged", lambda path: path.write_bytes(b"x\n"),
             "staged file replaces no regular file: tools/new_tool.py"),
            ("no-op", staged / "LICENSE.staged", lambda path: path.write_bytes((root / "LICENSE").read_bytes()),
             "staged file changes nothing: LICENSE"),
            ("symlink", staged / "tests/test_safe_kernel.py.staged",
             lambda path: path.symlink_to(root / "tests/test_safe_kernel.py"), "unsafe staged entry"),
            ("unpinned", staged / "LICENSE.staged",
             lambda path: path.write_bytes((root / "LICENSE").read_bytes() + b"\n"),
             "staged file is not pinned by the candidate: LICENSE"),
            ("pinned provenance", staged / "protocols/rapp-workspace/1/provenance.json.staged",
             lambda path: path.write_bytes((root / "protocols/rapp-workspace/1/provenance.json").read_bytes() + b"\n"),
             "the recorded candidate is not the staged generator's output"),
        )
        for name, path, damage, reason in cases:
            with self.subTest(case=name):
                path.parent.mkdir(parents=True, exist_ok=True)
                try:
                    damage(path)
                    self.refused(root, reason)
                finally:
                    path.unlink()

    def test_tool_refuses_a_symlinked_directory_on_a_staged_path(self):
        root = self.scratch("symlinked-parent")
        outside = root.parent / "outside"
        skill = root / ".github/skills/rapp-workspace"
        shutil.move(str(skill), str(outside))
        skill.symlink_to(outside, target_is_directory=True)
        before = {path.name: path.read_bytes() for path in outside.iterdir()}
        self.refused(root, "unsafe directory or symlink: .github/skills/rapp-workspace")
        self.assertEqual({path.name: path.read_bytes() for path in outside.iterdir()}, before)

    def test_tool_refuses_a_symlinked_scratch_directory(self):
        root = self.scratch("symlinked-validation")
        elsewhere = root.parent / "elsewhere"
        elsewhere.mkdir()
        (root / ".validation").symlink_to(elsewhere, target_is_directory=True)
        self.refused(root, "unsafe directory or symlink: .validation/workspace-successor")
        self.assertEqual(list(elsewhere.iterdir()), [])

    def test_tool_refuses_a_symlinked_index_in_both_modes(self):
        root = self.scratch("symlinked-index")
        index = root / "protocols/index.json"
        moved = root.parent / "index-target"
        shutil.move(str(index), str(moved))
        index.symlink_to(moved)
        saved = moved.read_bytes()
        for arguments in ((), ("--write",)):
            with self.subTest(arguments=arguments):
                self.refused_with(root, arguments, "not a regular file in the working tree: protocols/index.json")
                self.assertEqual(moved.read_bytes(), saved)

    def test_tool_never_replaces_a_linked_recorded_file(self):
        root = self.scratch("linked-recorded")
        relative = CANDIDATE_FILE.relative_to(REPO).as_posix()
        recorded = root / relative
        target = root.parent / "recorded-target"
        saved = b"synthetic file outside the repository\n"
        target.write_bytes(saved)
        recorded.unlink()
        recorded.symlink_to(target)
        self.refused_with(root, ("--write",), "unsafe recorded file: " + relative)
        with patch.object(TOOL, "REPO", root):
            with self.assertRaisesRegex(TOOL.SuccessorError, "unsafe recorded file: " + re.escape(relative)):
                TOOL.write_recorded(relative, b"synthetic\n")
        self.assertTrue(recorded.is_symlink())
        self.assertEqual(target.read_bytes(), saved)
        recorded.unlink()
        os.link(target, recorded)
        self.refused_with(root, ("--write",), "unsafe recorded file: " + relative)
        self.assertEqual(target.read_bytes(), saved)
        self.assertEqual(recorded.read_bytes(), saved)
        recorded.unlink()
        stale = CANDIDATE_FILE.read_bytes() + b"stale tail\n"
        recorded.write_bytes(stale)
        index = root / "protocols/index.json"
        outside_index = root.parent / "index-link"
        os.link(index, outside_index)
        self.refused_with(root, ("--write",), "unsafe recorded file: protocols/index.json")
        self.assertEqual(recorded.read_bytes(), stale)

    def test_relative_rapp1_paths_resolve_against_the_working_directory(self):
        self.assertEqual(absolute_path("rapp-1"), str(Path.cwd() / "rapp-1"))
        self.assertIsNone(absolute_path(None))
        rapp1, environment = rapp1_environment({"RAPP1_PATH": "rapp-1"})
        self.assertEqual((rapp1, environment["RAPP1_PATH"]), (str(Path.cwd() / "rapp-1"), str(Path.cwd() / "rapp-1")))
        checkout = Path(self.rapp1)
        completed = subprocess.run(
            [sys.executable, "-B", "-m", "unittest", "discover", "-s", str(REPO / "tests"),
             "-p", "test_front_door.py", "-k", "test_qualification_after_the_switch_accepts_only_the_successor"],
            cwd=checkout.parent, capture_output=True, text=True, timeout=600,
            env={**self.environment, "RAPP1_PATH": checkout.name})
        self.assertEqual(completed.returncode, 0, completed.stderr[-2000:])
        self.assertIn("Ran 1 test", completed.stderr)

    def test_tool_ignores_untracked_local_entries_and_finder_files(self):
        root = self.scratch("local-entries")
        tag = uuid.uuid4().hex[:8]
        fifo = root / f"tools/fifo-{tag}"
        os.mkfifo(fifo)
        retained = root / "protocols/rapp-workspace/1" / PREDECESSOR["path"]
        current = (root / "protocols/rapp-workspace/1/manifest.json").read_bytes()
        retained.parent.mkdir(parents=True, exist_ok=True)
        if retained.exists():
            self.assertEqual(retained.read_bytes(), current)
        else:
            retained.write_bytes(current)
        staged = root / "protocols/rapp-workspace/1/successor/staged"
        (staged / ".SKILL.md.staged.swp").write_bytes(b"\0synthetic swap file")
        (staged / "SKILL.md.staged~").write_bytes(b"synthetic backup\n")
        (staged / ".#SKILL.md.staged").symlink_to("synthetic-lock")
        read_only = root / f"tools/read-only-{tag}"
        read_only.mkdir()
        (read_only / "file").write_bytes(b"synthetic\n")
        read_only.chmod(0o555)
        self.addCleanup(read_only.chmod, 0o755)
        unreadable = root / f"tools/unreadable-{tag}"
        unreadable.write_bytes(b"synthetic\n")
        unreadable.chmod(0o000)
        self.addCleanup(unreadable.chmod, 0o644)
        closed = root / f"tools/closed-{tag}"
        closed.mkdir()
        closed.chmod(0o000)
        self.addCleanup(closed.chmod, 0o755)
        links = []
        for folder in (f".venv-{tag}/bin", f"tools/.venv-{tag}/bin", f".github/skills/rapp-private-hive/.venv-{tag}/bin"):
            (root / folder).mkdir(parents=True)
            (root / folder / "python").symlink_to(sys.executable)
            links.append(folder + "/python")
        checkout = root / f"rapp-1-{tag}"
        (checkout / "protocols").mkdir(parents=True)
        (checkout / "README.md").write_bytes(b"synthetic untracked checkout\n")
        (checkout / "protocols/link").symlink_to(root.parent, target_is_directory=True)
        links.append(f"rapp-1-{tag}/protocols/link")
        (root / f"rapp-1-link-{tag}").symlink_to(root.parent, target_is_directory=True)
        links.append(f"rapp-1-link-{tag}")
        (root / "protocols/rapp-workspace/1/successor/staged/.DS_Store").write_bytes(b"\0synthetic finder file")
        (root / "protocols/rapp-workspace/1/successor/staged/.github/.DS_Store").write_bytes(b"\0synthetic")
        self.assertEqual(self.tool(root), (0, "Workspace/1 successor candidate (proposal 0024): PASS"))
        code, output = self.tool(root, "--diff")
        self.assertEqual(code, 0)
        self.assertEqual(sorted(re.findall(r"^\+\+\+ b/(.+)$", output, re.M)), sorted(SWITCHED))
        base = root.parent / ("overlay-" + tag)
        base.mkdir()
        with patch.object(TOOL, "REPO", root):
            overlay = TOOL.switched_overlay(base, TOOL.staged_files())
        found = [os.path.join(current, entry) for current, directories, files in os.walk(overlay)
                 for entry in directories + files if os.path.islink(os.path.join(current, entry))]
        self.assertEqual(found, [])
        self.assertFalse(os.path.lexists(overlay / f"tools/fifo-{tag}"))
        self.assertTrue((overlay / f"tools/read-only-{tag}/file").is_file())
        if os.geteuid() != 0:
            self.assertFalse(os.path.lexists(overlay / f"tools/unreadable-{tag}"))
            self.assertFalse(os.path.lexists(overlay / f"tools/closed-{tag}"))
        for link in links:
            self.assertFalse(os.path.lexists(overlay / link), link)
        self.assertTrue((overlay / f"rapp-1-{tag}/README.md").is_file())
        self.assertEqual(read_file(overlay / "protocols/rapp-workspace/1/manifest.json"), read_file(CANDIDATE_FILE))
        TOOL.remove_scratch(base, strict=True)
        self.assertFalse(base.exists())
        modes, original = [], TOOL.switched_overlay

        def watched(scratch_base, staged):
            modes.append(stat.S_IMODE(scratch_base.stat().st_mode))
            return original(scratch_base, staged)

        with patch.object(TOOL, "REPO", root), patch.object(TOOL, "switched_overlay", watched):
            self.assertEqual(TOOL.generate(), read_file(CANDIDATE_FILE))
        self.assertEqual(modes, [0o700])

    def test_a_copy_failure_names_the_entry_without_local_paths(self):
        root = self.scratch("copy-failure")
        original = shutil.copyfile

        def failing(source, destination, *arguments, **options):
            if os.path.basename(source) == "LICENSE":
                raise PermissionError(13, "synthetic refusal", source)
            return original(source, destination, *arguments, **options)

        with patch.object(TOOL, "REPO", root), patch.object(shutil, "copyfile", failing):
            with self.assertRaises(TOOL.SuccessorError) as refusal:
                TOOL.generate()
        self.assertEqual(str(refusal.exception), "cannot copy the working tree: LICENSE")
        self.assertEqual(os.listdir(root / ".validation/workspace-successor"), [])

    def test_tool_refuses_a_candidate_it_cannot_reproduce(self):
        root = self.scratch("tampered")
        with self.damaged(root / "protocols/rapp-workspace/1/successor/manifest.json.staged", append_marker):
            self.refused(root, "the recorded candidate is not the staged generator's output")
        with self.damaged(staged_path(root, "SKILL.md"), append_marker):
            self.refused(root, "the recorded candidate is not the staged generator's output")
        generator = staged_path(root, "protocols/rapp-workspace/1/reference/pins.py")
        source = generator.read_text(encoding="utf-8")
        start = source.index("PREDECESSORS = (")
        end = source.index("\n)\n", start) + 3
        orphan = source[:start] + "PREDECESSORS = ()\n" + source[end:]
        with self.damaged(generator, lambda path: path.write_text(orphan, encoding="utf-8")):
            self.refused(root, "the candidate does not succeed the current manifest")
        index_path = root / "protocols/index.json"
        original = json.loads(index_path.read_bytes())
        variants = {
            "claims authority": lambda entry: entry.update(status="core", authority=True),
            "wrong hash": lambda entry: entry.update(manifest_sha256="0" * 64),
            "missing": None,
            "duplicate": "duplicate",
        }
        for name, change in variants.items():
            with self.subTest(index=name):
                index = json.loads(json.dumps(original))
                entries = [item for item in index["profiles"] if item["name"] == "rapp-workspace-file-manifest/2"]
                if change is None:
                    index["profiles"].remove(entries[0])
                elif change == "duplicate":
                    index["profiles"].append(dict(entries[0]))
                else:
                    change(entries[0])
                with self.damaged(index_path, lambda path: path.write_bytes(pins.encode(index))):
                    self.refused(root, "protocols/index.json does not record exactly this candidate")

    def test_tool_refuses_when_the_current_manifest_is_not_the_named_predecessor(self):
        root = self.scratch("predecessor-moved")
        shutil.rmtree(root / "protocols/rapp-workspace/1/history", ignore_errors=True)
        with self.damaged(root / "protocols/rapp-workspace/1/manifest.json", append_marker):
            self.refused(root, "staged generator failed after the switch")


if __name__ == "__main__":
    unittest.main()
