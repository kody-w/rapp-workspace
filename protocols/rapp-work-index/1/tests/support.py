"""Public fixture test doubles. Reading these files is NOT external Frame verification."""

import copy
import shutil
import sys
import unittest
import uuid
from pathlib import Path

REFERENCE = Path(__file__).resolve().parents[1] / "reference"
sys.path.insert(0, str(REFERENCE))

from common import REPO, directory, parse, read_file, sha
from schema_source import MAX_MANIFEST_BYTES, PROFILE
from vectors import FIXTURES
from work_index import ExactIndex, PinnedGeneration


def fixture(name):
    return parse(read_file(FIXTURES / name), MAX_MANIFEST_BYTES)


def receipt_double(manifest, number=0):
    """Only unit tests simulate the protected caller; conformance separately uses RAPP/1."""
    frame_raw = read_file(FIXTURES / f"checkpoint-{number}.frame.json")
    frame = parse(frame_raw)
    context = manifest["context"]
    from work_index import checkpoint_payload

    return {
        "schema": PROFILE + "/verified-frame",
        "verification": "external-canonical-rapp/1",
        "kind": "memory.save", "signature_verified": True, "chain_verified": True,
        "context": copy.deepcopy(context),
        "payload": checkpoint_payload(manifest),
        "signer": context["signer"], "spki_sha256": context["spki_sha256"],
        "stream": context["stream"], "key_epoch": context["key_epoch"],
        "registry_epoch": context["registry_epoch"], "seq": frame["seq"],
        "payload_hash": frame["payload_hash"], "frame_hash": frame["frame_hash"],
        "frame_sha256": sha(frame_raw),
    }


def pin_for(manifest, number=0, previous=None):
    return PinnedGeneration(manifest, receipt_double(manifest, number), manifest["context"], previous)


class FixtureCase(unittest.TestCase):
    def setUp(self):
        self.inputs = fixture("inputs.json")
        self.manifest = fixture("generation-0.json")
        self.pin = pin_for(self.manifest)
        self.current = self.pin.frontier
        self.shards = {i: read_file(FIXTURES / f"shard-{i:02d}.json") for i in range(16)}
        self.proofs = fixture("proofs-0.json")

    def pairs(self):
        return [(self.shards[i], self.proofs[i]) for i in range(16)]


class DatabaseCase(FixtureCase):
    def setUp(self):
        super().setUp()
        self.assertEqual(Path.cwd(), REPO, "run the profile tests from the repository root")
        self.owned = Path(".validation/work-index-tests") / uuid.uuid4().hex
        with directory(self.owned, create=True):
            pass
        self.path = self.owned / "index.sqlite3"

    def build(self):
        ExactIndex.build(self.path, self.pin, self.current, self.pairs())

    def open(self, **kwargs):
        return ExactIndex(self.path, self.pin, self.current, **kwargs)

    def tearDown(self):
        shutil.rmtree(self.owned)
