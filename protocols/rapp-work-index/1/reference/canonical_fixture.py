"""Explicit canonical RAPP/1 integration and PUBLIC SYNTHETIC signing, not wire code."""

from __future__ import annotations

import base64
import hashlib
import json
from pathlib import Path
import subprocess
import types

from common import Refusal, read_file, require, sha, validate
from schema_source import MAX_CONTENT_BYTES, ROOT
from work_index import OCCURRENCE_FIELDS


class CanonicalRapp:
    def __init__(self, checkout):
        require(checkout is not None, "explicit --rapp1-path required; discovery/fallback forbidden")
        self.path = Path(checkout)
        provenance = json.loads(read_file(ROOT / "provenance.json"))
        self.pin = provenance["rapp1"]
        try:
            commit = subprocess.run(
                ["git", "-C", str(self.path), "rev-parse", "HEAD"],
                check=True, capture_output=True, text=True, timeout=10,
            ).stdout.strip()
        except (OSError, subprocess.SubprocessError) as error:
            raise Refusal("explicit canonical checkout unavailable") from error
        require(commit == self.pin["commit"], "canonical checkout commit mismatch")
        sources = {}
        for entry in self.pin["files"]:
            raw = read_file(self.path / entry["path"])
            require(len(raw) == entry["bytes"] and sha(raw) == entry["sha256"],
                    "canonical source byte substitution: " + entry["path"])
            sources[entry["path"]] = raw
        self.r = types.ModuleType("work_index_explicit_canonical_rapp")
        self.r.__file__ = str(self.path / "rapp.py")
        # Only caller-approved local source whose exact bytes were checked above is executed.
        exec(compile(sources["rapp.py"], self.r.__file__, "exec"), self.r.__dict__)
        previous, self.anchor_frames_verified = None, 0
        for line in sources["anchor/chain.jsonl"].splitlines():
            frame = self.r._strict_json(line)
            ok, step, reason = self.r.verify_frame(
                frame, head=previous, stream_id_of_record=self.pin["anchor_stream"],
            )
            require(ok, f"canonical anchor refusal: {step}: {reason}")
            previous = frame
            self.anchor_frames_verified += 1
        require(previous is not None and previous["frame_hash"] == self.pin["selected_head"],
                "canonical anchor head mismatch")
        require(previous["payload"]["normative"]["text"].encode("utf-8") == sources["SPEC.md"],
                "canonical normative text mismatch")
        self.frames_verified = 0

    def octets(self, value):
        raw = self.r.canonical(value).encode("utf-8")
        require(len(raw) <= MAX_CONTENT_BYTES, "canonical RAPP/1 byte ceiling")
        return raw

    def verify(self, raw, *, signer, spki, stream, head=None):
        require(type(raw) is bytes and len(raw) <= MAX_CONTENT_BYTES, "RAPP/1 input byte ceiling")
        try:
            frame = self.r._strict_json(raw)
            require(self.octets(frame) == raw, "noncanonical RAPP/1 fixture")
            require(frame["sig"] is not None, "index evidence must be genuinely signed")
            ok, step, reason = self.r.verify_frame(
                frame, head=head, stream_id_of_record=stream,
                signature_verifier=lambda unsigned, signature: self.r.verify_detached_jws(
                    unsigned, signature, spki, expected_kid=signer,
                ),
            )
            require(ok, f"canonical signed frame refusal: {step}: {reason}")
        except (ValueError, KeyError, TypeError, UnicodeError) as error:
            raise Refusal("canonical frame refused: " + str(error)) from error
        self.frames_verified += 1
        return frame

    def verified_checkpoint(self, raw, *, context, spki, head=None):
        validate(context, "context")
        require(sha(spki) == context["spki_sha256"], "external signer SPKI differs")
        frame = self.verify(
            raw, signer=context["signer"], spki=spki, stream=context["stream"], head=head,
        )
        record = {
            "schema": "rapp-work-index/1/verified-frame",
            "verification": "external-canonical-rapp/1",
            "kind": frame["kind"], "signature_verified": True, "chain_verified": True,
            "context": context, "payload": frame["payload"],
            "signer": context["signer"], "spki_sha256": sha(spki),
            "stream": frame["stream_id"], "key_epoch": context["key_epoch"],
            "registry_epoch": context["registry_epoch"],
            "seq": frame["seq"], "payload_hash": frame["payload_hash"],
            "frame_hash": frame["frame_hash"], "frame_sha256": sha(raw),
        }
        validate(record, "verified-frame")
        require(all(key in record for key in OCCURRENCE_FIELDS), "incomplete external record")
        return record, frame


def public_test_key(core, label, slug):
    """Deliberately public deterministic test material; NEVER a production credential."""
    try:
        from cryptography.hazmat.primitives import serialization
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    except ImportError as error:
        raise Refusal("canonical signed conformance requires requirements-conformance.txt") from error
    seed = hashlib.sha256(
        ("rapp-work-index/1 PUBLIC SYNTHETIC TEST KEY -- " + label).encode("ascii")
    ).digest()
    key = Ed25519PrivateKey.from_private_bytes(seed)
    spki = key.public_key().public_bytes(
        serialization.Encoding.DER, serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    signer = core.r.mint_rappid("public-fixture", slug, spki_der=spki)
    return key, spki, signer


def sign_fixture(core, frame, key, signer):
    """Standard detached JWS test signing; canonical RAPP/1 constructs/checks every Frame."""
    header = {"alg": "EdDSA", "b64": False, "crit": ["b64"], "kid": signer}
    protected = base64.urlsafe_b64encode(core.octets(header)).rstrip(b"=")
    unsigned = {name: value for name, value in frame.items() if name != "sig"}
    signature = key.sign(protected + b"." + core.octets(unsigned))
    result = dict(frame)
    result["sig"] = protected.decode("ascii") + ".." + base64.urlsafe_b64encode(
        signature
    ).rstrip(b"=").decode("ascii")
    return result
