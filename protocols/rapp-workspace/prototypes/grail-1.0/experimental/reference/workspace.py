"""Workspace Grail/1 bounded candidate. No native adapters, network, or code execution."""

import copy
from dataclasses import dataclass
import fcntl
import json
import os
from pathlib import Path
import stat

from common import MAX_BYTES, ROOT, Refusal, address, directory, read_file, require, sha, wave, write_file
from schema_source import CONTROL_DIR, GENERATION, LEGACY_LABELS, NEGATIVES, PROFILE
from pins import encode, legacy_contract, manifest as file_manifest


@dataclass(frozen=True)
class LocalConsent:
    """Trusted caller input, never reconstructed from received frames or a registry cache."""

    owner: str
    decisions: frozenset = frozenset()
    public_reads: frozenset = frozenset()

    def require(self, parent, payload):
        require(payload.get("authorized_by", self.owner) == self.owner, "owner identity substitution")
        require(parent.particle(payload)["hash"] in self.decisions, "independent local consent required")


def get_pointer(value, pointer):
    result = value
    if pointer == "":
        return copy.deepcopy(result)
    require(pointer.startswith("/"), "JSON pointer")
    for encoded in pointer.split("/")[1:]:
        key = encoded.replace("~1", "/").replace("~0", "~")
        if isinstance(result, list):
            require(key.isdigit() and str(int(key)) == key and int(key) < len(result), "read pointer absent")
            result = result[int(key)]
        else:
            require(isinstance(result, dict) and key in result, "read pointer absent")
            result = result[key]
    return copy.deepcopy(result)


def set_pointer(value, pointer, replacement):
    require(pointer.startswith("/") and pointer.count("/") >= 1, "amend pointer")
    parts = pointer.split("/")[1:]
    keys = [part.replace("~1", "/").replace("~0", "~") for part in parts]
    require(keys[0] not in {"schema", "generation", "estate_rappid", "world_id", "seed", "owner_rappid",
                           "proposer_rappid", "synthesis"}, "immutable boundary amendment")
    target = value
    for key in keys[:-1]:
        require(isinstance(target, dict) and key in target, "amend pointer absent")
        target = target[key]
    require(isinstance(target, dict) and keys[-1] in target, "amend pointer absent")
    target[keys[-1]] = copy.deepcopy(replacement)


class Workspace:
    def __init__(self, parent, estate_rappid, world_id, consent, *, legacy=False):
        require(parent.r.rappid_valid(estate_rappid) and parent.r.rappid_valid(consent.owner), "invalid identity")
        require(isinstance(world_id, str) and 0 < len(world_id) <= 128, "world boundary")
        self.core, self.estate, self.world, self.consent = parent, estate_rappid, world_id, consent
        self.legacy = legacy
        self.seed = None
        self._raw, self._streams, self._events, self._faults = {}, {}, [], {}
        self._verified_cache = {}
        self._exhaust_checks = set()
        self._adopted, self._routes, self._suspended = [], {}, set()
        self._adoption_head = self._routing_head = self._migration = None
        self._parents, self._depths = {}, {estate_rappid: 0}

    def payload(self, name, **fields):
        return {"schema": PROFILE + "/" + name, "generation": GENERATION, "estate_rappid": self.estate,
                "world_id": self.world, "seed": copy.deepcopy(self.seed), **fields}

    def frame(self, reference, *, usable=True):
        key = address(reference)
        require(key in self._raw, "missing frame dependency")
        frame = self._verified_frame(key)
        if usable:
            pending, seen = [key], set()
            while pending:
                current = pending.pop()
                if current in seen:
                    continue
                seen.add(current)
                source = self._verified_frame(current)
                floor = self._faults.get(source["stream_id"])
                require(floor is None or source["seq"] < floor, "forked frame or ancestor")
                pending.extend(self._parents.get(current, ()))
        return frame

    def _verified_frame(self, key):
        raw = self._raw[key]
        cached = self._verified_cache.get(key)
        if cached and cached[0] == raw:
            return copy.deepcopy(cached[1])
        frame = self.core.parse(raw)
        require(frame.get("frame_hash") == key, "frame address substitution")
        chain = self._streams.get(frame["stream_id"], [])
        require(type(frame["seq"]) is int and 0 <= frame["seq"] <= len(chain), "cached frame sequence")
        previous = self.core.parse(self._raw[chain[frame["seq"] - 1]]) if frame["seq"] else None
        ok, step, reason = self.core.r.verify_frame(frame, head=previous, stream_id_of_record=frame["stream_id"])
        require(ok, f"retained frame tamper: RAPP/1 {step}: {reason}")
        self._verified_cache[key] = (raw, copy.deepcopy(frame))
        return frame

    def body(self, reference, name=None, *, usable=True):
        payload = self.frame(reference, usable=usable)["payload"]
        if payload.get("schema") == PROFILE + "/derived-frame":
            payload = self.core.parse(payload["value_json"].encode("utf-8"))
        if name:
            require(payload.get("schema") == PROFILE + "/" + name
                    and payload.get("generation") == GENERATION, "wrong dependency schema/generation: " + name)
        return payload

    def ordered(self, references):
        return sorted(copy.deepcopy(references), key=lambda r: (
            self.frame(r)["utc"], self.frame(r)["frame_hash"]))

    def append(self, payload, utc, stream=None):
        stream = stream or self.estate
        chain = self._streams.get(stream, [])
        head = self.frame({"space": "rapp/1:wave", "hash": chain[-1]}) if chain else None
        frame = self.core.r.build_frame(
            "body.pulse", stream, len(chain), utc, copy.deepcopy(payload),
            head["payload_hash"] if head else None)
        return self.ingest(self.core.octets(frame))

    def ingest(self, raw):
        frame = self.core.parse(raw)
        require(isinstance(frame, dict), "frame object required")
        require(frame.get("kind") == "body.pulse" and self.core.r.rappid_valid(frame.get("stream_id")),
                "reference supports registered body.pulse body streams only")
        stream, seq = frame["stream_id"], frame.get("seq")
        require(type(seq) is int and 0 <= seq <= 2**53 - 1, "frame sequence")
        chain = self._streams.get(stream, [])
        require(chain or len(self._streams) < 128, "reference stream budget; never drop existing heads")
        require(seq <= len(chain), "missing predecessor")
        previous = self.frame({"space": "rapp/1:wave", "hash": chain[seq - 1]}, usable=False) if seq else None
        ok, step, reason = self.core.r.verify_frame(frame, head=previous, stream_id_of_record=stream)
        require(ok, f"RAPP/1 {step}: {reason}")
        key, ref = frame["frame_hash"], wave(frame)
        if key in self._raw:
            require(self._raw[key] == raw, "same wave different octets")
            self.frame(ref)
            return ref
        if seq < len(chain):
            self._raw[key] = raw
            self._events.append(key)
            self._parents[key] = {chain[seq - 1]} if seq else set()
            self._faults[stream] = min(seq, self._faults.get(stream, seq))
            raise Refusal("stream-fork: both branches retained and refused")
        require(stream not in self._faults, "stream fork is latched")
        payload = frame["payload"]
        name = payload.get("schema", "")
        is_profile = isinstance(name, str) and name.startswith(PROFILE + "/")
        legacy_prefix = self.legacy and self.seed is None and not (
            name == PROFILE + "/seed-genesis" and payload.get("generation") == GENERATION)
        if legacy_prefix:
            require(payload.get("generation") != GENERATION, "Grail frame cannot be treated as pre-Grail")
            is_profile = False
        dependencies = {chain[-1]} if chain else set()
        if is_profile:
            self.core.schemas.validate(payload)
            require(payload["estate_rappid"] == self.estate and payload["world_id"] == self.world,
                    "estate identity or world substitution")
            if name == PROFILE + "/seed-genesis":
                require(self.seed is None and stream == self.estate, "one seed per estate")
                require(payload["owner_rappid"] == self.consent.owner, "seed owner mismatch")
                require(payload["seed"] is None, "seed cannot name itself")
                require(payload["origin"] == ("migration" if self.legacy else "new"), "birth origin mismatch")
                inherited = [wave(previous)] if previous else []
                require(payload["inherited_heads"] == inherited, "legacy genesis lineage mismatch")
            else:
                require(self.seed is not None and payload["seed"] == self.seed, "foreign or missing seed")
                dependencies.add(address(self.seed))
            self._collect_refs(payload, dependencies)
        else:
            require(self.seed is not None or (self.legacy and stream == self.estate), "seed must be first")
            require(legacy_prefix or not isinstance(name, str) or not name.startswith("rapp-workspace/"),
                    "unsupported Workspace schema")
        if not chain and stream != self.estate:
            require(name == PROFILE + "/dimension-genesis", "child dimension requires its own genesis")
        if is_profile and name != PROFILE + "/seed-genesis":
            self._semantic(payload, ref, stream, seq)
        require(len(self._events) < 8192, "reference frame budget; split verified batches, never truncate")
        self._raw[key] = raw
        self._streams.setdefault(stream, []).append(key)
        self._events.append(key)
        self._parents[key] = dependencies
        if not is_profile:
            return ref
        if name == PROFILE + "/seed-genesis":
            self.seed = ref
        elif name == PROFILE + "/dimension-genesis":
            self._depths[stream] = payload["depth"]
        elif name == PROFILE + "/verification-adoption":
            if payload["decision"] == "adopt":
                self._adopted.append(address(payload["candidate"]))
            self._adoption_head = ref
        elif name == PROFILE + "/routing-decision":
            target = address(payload["target"])
            state = self._routes.setdefault(target, {"selected": False, "suppressed": False})
            if payload["action"] == "select":
                state["selected"] = True
            else:
                state.update(selected=False, suppressed=payload["action"] == "suppress")
            self._routing_head = ref
        elif name == PROFILE + "/lens-drift":
            self._suspended.add(address(payload["lens"]))
        elif name == PROFILE + "/migration-record":
            self._migration = ref
        return ref

    def _collect_refs(self, value, dependencies):
        if isinstance(value, dict):
            if value.get("space") == "rapp/1:wave" and set(value) == {"space", "hash"}:
                self.frame(value)
                dependencies.add(address(value))
            else:
                for child in value.values():
                    self._collect_refs(child, dependencies)
        elif isinstance(value, list):
            for child in value:
                self._collect_refs(child, dependencies)

    def _semantic(self, p, ref, stream, seq):
        name = p["schema"].split("/")[-1]
        if name == "dimension-genesis":
            require(seq == 0 and stream != self.estate, "dimension genesis position")
            parent_stream = self.frame(p["parent"])["stream_id"]
            require(p["depth"] == self._depths[parent_stream] + 1, "recursive dimension depth")
        elif name == "native-shape-observation":
            require(len({f["name"] for f in p["metadata"]}) == len(p["metadata"]), "ambiguous metadata")
            require(p["fingerprint"] == self.core.particle(p["metadata"]), "opaque metadata fingerprint")
            if p["sources"]:
                from native_lens import source_metadata
                require(len(p["sources"]) == 1, "bounded native observation has one complete source")
                source = self.body(p["sources"][0])
                if source.get("schema") == PROFILE + "/opaque-local-object":
                    from framing import object_metadata, validate_object
                    validate_object(self.core, source)
                    expected_metadata, expected_shape = object_metadata(source), "unclassified-local-object"
                else:
                    source = self.body(p["sources"][0], "opaque-native-source")
                    expected_metadata, expected_shape = source_metadata(source), "unclassified-native-layout"
                require(p["subject"] == source["subject"] and p["metadata"] == expected_metadata
                        and p["shape"] == expected_shape, "native observation/source mismatch")
            if p["tile"] is not None:
                require(p["subject"] in self.body(p["tile"], "scan-tile")["targets"], "unrequested scan response")
        elif name == "opaque-native-source":
            from native_lens import validate_source
            validate_source(self.core, p)
        elif name == "opaque-local-object":
            from framing import validate_object
            validate_object(self.core, p)
        elif name in ("workspace-successor", "workspace-unresolved"):
            from framing import validate_outcome
            validate_outcome(self, p)
        elif name == "lens-loop" or name.startswith("iteration-"):
            from iteration import validate_record
            validate_record(self, p)
        elif name == "lens-declaration":
            for source in p["observations"]:
                self.body(source, "native-shape-observation")
            self._descriptors(p)
        elif name == "mutation-receipt":
            self.verify_receipt(p)
        elif name == "derived-frame":
            manifest = self.body(p["declared_reads"], "declared-reads")
            require(p["lens"] == manifest["lens"], "derived lens substitution")
            result = self.execute(manifest)
            require(self.core.octets(result).decode("utf-8") == p["value_json"]
                    and self.core.particle(result) == p["content"], "derived content substitution")
        elif name == "equivalence-evidence":
            require(p == self.evidence_payload(p["receipt"]), "equivalence evidence substitution")
        elif name == "verification-adoption":
            require(stream == self.estate and p["base"] == self._adoption_head, "adoption CAS or stream")
            require(p["authority_scope"] == "local-explicit-consent", "signed owner-policy adapter unavailable")
            self.consent.require(self.core, p)
            evidence = self.body(p["evidence"], "equivalence-evidence")
            require(evidence == self.evidence_payload(evidence["receipt"]), "stale evidence")
            receipt = self.body(evidence["receipt"], "mutation-receipt")
            require(p["candidate"] in (receipt["lens"], receipt["successor"]), "unrelated adoption")
            lens = self.body(receipt["lens"], "lens-declaration")
            if lens["synthesis"] == "model-candidate":
                require(p["authorized_by"] != lens["proposer_rappid"], "model cannot authorize its own candidate")
            if p["decision"] == "adopt":
                candidate = self.body(p["candidate"])
                require(candidate.get("schema") != PROFILE + "/workspace-unresolved",
                        "unresolved successor cannot become an adopted workspace")
                require(len(self._adopted) < 128, "reference adoption budget; never drop prior adoptions")
                require(address(p["candidate"]) not in self._adopted, "duplicate adoption")
                if p["candidate"] != receipt["lens"]:
                    require(address(receipt["lens"]) in self._adopted, "candidate lens is not adopted")
                    from framing import object_lineage, validate_outcome
                    if object_lineage(self, receipt["sources"] + receipt["contexts"]):
                        require(candidate.get("schema") == PROFILE + "/workspace-successor",
                                "universal framing is not workspace adoption evidence")
                        validate_outcome(self, candidate)
        elif name == "routing-decision":
            require(stream == self.estate and p["base"] == self._routing_head, "routing CAS or stream")
            self.consent.require(self.core, p)
            require(address(p["target"]) in self._adopted, "unadopted route")
            self.workspace_content(p["target"])
            require(p["action"] != "select" or not self._routes.get(address(p["target"]), {}).get("suppressed"),
                    "suppression wins; explicit re-add required")
        elif name == "lens-drift":
            self.consent.require(self.core, p)
            self.body(p["lens"], "lens-declaration")
        elif name == "scan-tile":
            expected = self.scan_payload(p["scope"], p["signaled"], p["previous_report"],
                                         p["baseline_every"], p["parent_tile"])
            require(p == expected, "scan scope, delta, tick or baseline substitution")
        elif name == "dream-report":
            require(p == self.report_payload(p["tile"], p["responses"]), "Dream Catcher report substitution")
        elif name == "dimension-merge":
            require(p == self.merge_payload(p["left"], p["right"]), "merge fidelity or retained conflict substitution")
        elif name == "deterministic-reattach":
            require(p == self.reattach_payload(p["stranded"], p["declared_reads"], p["ladder"]),
                    "reattach choice substitution")
        elif name == "migration-record":
            require(self.legacy and self._migration is None and stream == self.estate, "migration boundary")
            self.consent.require(self.core, p)
            legacy_contract(p["source_spec"], p["source_spec_sha256"])
            require(p["prior_rappid"] == self.estate and p["prior_world_id"] == self.world, "migration identity loss")
            require(p["prior_heads"] == self.body(self.seed)["inherited_heads"], "migration history loss")
        elif name == "registry-projection":
            require(p == self.projection(), "registry is a derived projection")
        elif name == "learned-projection":
            require(len({f["name"] for f in p["facts"]}) == len(p["facts"]), "ambiguous learned facts")

    def birth(self, utc):
        require(self.seed is None, "one seed per estate")
        head = self._streams.get(self.estate, [])
        inherited = [{"space": "rapp/1:wave", "hash": head[-1]}] if head else []
        return self.append(self.payload(
            "seed-genesis", owner_rappid=self.consent.owner, origin="migration" if self.legacy else "new",
            inherited_heads=inherited, local_only=True, source_writes=False,
            fixed_taxonomy=False, candidate_self_authorization=False), utc)

    def dimension(self, stream, parent, label, utc):
        depth = self._depths[self.frame(parent)["stream_id"]] + 1
        return self.append(self.payload("dimension-genesis", parent=parent, depth=depth, label=label), utc, stream)

    def observation(self, subject, shape, metadata, utc, *, tile=None, findings=(), stream=None, sources=()):
        return self.append(self.payload(
            "native-shape-observation", tile=tile, subject=subject, shape=shape, sources=list(sources),
            metadata=metadata, fingerprint=self.core.particle(metadata), findings=sorted(set(findings)),
            source_state="opaque", read_scope="approved-metadata-only", native_compliance="unclaimed"), utc, stream)

    @staticmethod
    def runtime_hash():
        raw = read_file(ROOT / "manifest.json")
        require(raw == encode(file_manifest()), "reference manifest drift")
        return sha(raw)

    def lens(self, label, observations, program, proposer, utc, synthesis="local-rule"):
        return self.append(self.payload(
            "lens-declaration", label=label, proposer_rappid=proposer, synthesis=synthesis,
            observations=observations, runtime_sha256=self.runtime_hash(), program=program), utc)

    def _descriptors(self, lens):
        program = lens["program"]
        if program["op"] == "workspace-context-attempt":
            reads = program["reads"]
            require(all(r["pointer"] == "" for r in reads), "context attempt reads complete evidence")
        elif program["op"] == "workspace-attempt":
            reads = [program["read"], program["context_read"]]
            require(all(r["pointer"] == "" for r in reads), "workspace attempt reads complete source/context")
        else:
            reads = [item["read"] for item in program["bindings"]] if program["op"] == "project" else [program["read"]]
        require(len({r["name"] for r in reads}) == len(reads), "ambiguous declared read names")
        if program["op"] in ("identity", "amend"):
            require(program["read"]["pointer"] == "", "identity/amend reads the complete content particle")
        return reads

    def reads_payload(self, lens_ref, sources, contexts=()):
        lens = self.body(lens_ref, "lens-declaration")
        inputs = list(sources) + list(contexts)
        require(len(set(map(address, inputs))) == len(inputs), "duplicate input frames")
        reads, used = [], set()
        for descriptor in self._descriptors(lens):
            require(descriptor["input"] < len(inputs), "missing declared input")
            used.add(descriptor["input"])
            ref = inputs[descriptor["input"]]
            value = get_pointer(self.body(ref), descriptor["pointer"])
            reads.append({"name": descriptor["name"], "frame": ref, "pointer": descriptor["pointer"],
                          "value": self.core.particle(value)})
        require(used == set(range(len(inputs))), "unused or undeclared context")
        return self.payload("declared-reads", lens=lens_ref, sources=list(sources), contexts=list(contexts),
                            complete=True, reads=reads)

    def execute(self, manifest):
        self.core.schemas.validate(manifest)
        expected = self.reads_payload(manifest["lens"], manifest["sources"], manifest["contexts"])
        require(manifest == expected, "incomplete or substituted declared reads")
        lens = self.body(manifest["lens"], "lens-declaration")
        require(lens["runtime_sha256"] == self.runtime_hash(), "runtime drift")
        require(address(manifest["lens"]) not in self._suspended, "lens drift suspended")
        # The interpreter receives only copied declared values, never native handles or callbacks.
        values = {item["name"]: get_pointer(self.body(item["frame"]), item["pointer"]) for item in manifest["reads"]}
        program = lens["program"]
        if program["op"] == "project":
            from framing import object_lineage
            require(not object_lineage(self, manifest["sources"] + manifest["contexts"]),
                    "opaque framing requires workspace-attempt assessment, not unconditional projection")
            result = self.payload("learned-projection", tick=program["tick"],
                                  facts=[{"name": b["name"], "value": values[b["read"]["name"]]}
                                         for b in program["bindings"]], native_compliance="unclaimed")
        elif program["op"] == "workspace-attempt":
            from framing import execute_attempt
            result = execute_attempt(self, manifest, program)
        elif program["op"] == "workspace-context-attempt":
            from framing import execute_context_attempt
            result = execute_context_attempt(self, manifest, program)
        else:
            result = copy.deepcopy(values[program["read"]["name"]])
            require(isinstance(result, dict), "frame payload object required")
            if program["op"] == "amend":
                for change in program["changes"]:
                    set_pointer(result, change["pointer"], change["value"])
        self.core.octets(result)
        if (isinstance(result.get("schema"), str) and result["schema"].startswith(PROFILE + "/")
                and result.get("generation") == GENERATION):
            self.core.schemas.validate(result)
            require(result.get("estate_rappid") == self.estate and result.get("world_id") == self.world
                    and result.get("generation") == GENERATION
                    and (result.get("seed") == self.seed or result["schema"] == PROFILE + "/seed-genesis"),
                    "lens output boundary substitution")
            if result["schema"] in (PROFILE + "/workspace-successor", PROFILE + "/workspace-unresolved"):
                from framing import validate_outcome
                validate_outcome(self, result)
        return result

    def preservation(self, inputs):
        return [{"frame": r, "before_sha256": sha(self._raw[address(r)]),
                 "after_sha256": sha(self._raw[address(r)]), "bytes": len(self._raw[address(r)])}
                for r in {address(value): value for value in inputs}.values()]

    def mutate(self, lens, sources, utc, *, contexts=(), stream=None, declared=None):
        manifest = self.reads_payload(lens, sources, contexts) if declared is None else declared
        self.core.schemas.validate(manifest)
        require((manifest["lens"], manifest["sources"], manifest["contexts"]) ==
                (lens, list(sources), list(contexts)), "mutation arguments differ from declared inputs")
        result = self.execute(manifest)
        before = {address(r): self._raw[address(r)] for r in [lens, *sources, *contexts]}
        reads_ref = self.append(manifest, utc)
        successor = self.append(self.payload(
            "derived-frame", lens=lens, declared_reads=reads_ref, content=self.core.particle(result),
            value_json=self.core.octets(result).decode("utf-8"), native_compliance="unclaimed"), utc, stream)
        require(all(self._raw[k] == v for k, v in before.items()), "source mutation")
        receipt = self.payload(
            "mutation-receipt", lens=lens, sources=list(sources), contexts=list(contexts),
            declared_reads=reads_ref, successor=successor,
            preservation=self.preservation([lens, *sources, *contexts]),
            preservation_scope="retained-frame-octets", native_compliance="unclaimed")
        return self.append(receipt, utc)

    def verify_receipt(self, p):
        manifest = self.body(p["declared_reads"], "declared-reads")
        require((p["lens"], p["sources"], p["contexts"]) ==
                (manifest["lens"], manifest["sources"], manifest["contexts"]), "receipt input substitution")
        require(p["preservation"] == self.preservation([p["lens"], *p["sources"], *p["contexts"]]),
                "source preservation receipt mismatch")
        derived = self.frame(p["successor"])["payload"]
        require(derived.get("schema") == PROFILE + "/derived-frame"
                and (derived["lens"], derived["declared_reads"]) == (p["lens"], p["declared_reads"]),
                "receipt successor substitution")
        require(self.execute(manifest) == self.body(p["successor"]), "lens replay mismatch")
        return manifest

    def evidence_payload(self, receipt_ref):
        receipt = self.body(receipt_ref, "mutation-receipt")
        manifest = self.verify_receipt(receipt)
        results = [self.core.particle(self.execute(manifest)) for _ in range(2)]
        negative = copy.deepcopy(manifest)
        negative["complete"] = False
        self._must_refuse(lambda: self.execute(negative), "incomplete-reads")
        negative = copy.deepcopy(manifest)
        negative["reads"][0]["value"]["hash"] = "0" * 64
        self._must_refuse(lambda: self.execute(negative), "read-substitution")
        original = self.frame(receipt["sources"][0])
        altered = copy.deepcopy(original)
        altered["payload"]["synthetic_tamper"] = True
        predecessor = None
        if original["seq"]:
            key = self._streams[original["stream_id"]][original["seq"] - 1]
            predecessor = self.frame({"space": "rapp/1:wave", "hash": key})
        require(not self.core.r.verify_frame(altered, head=predecessor,
                                            stream_id_of_record=original["stream_id"])[0],
                "source-tamper negative did not refuse")
        negative = copy.deepcopy(manifest)
        negative["contexts"].append(self.seed)
        self._must_refuse(lambda: self.execute(negative), "context-substitution")
        negative = copy.deepcopy(manifest)
        negative["world_id"] += "-foreign"
        self._must_refuse(lambda: self.execute(negative), "world-substitution")
        negative = copy.deepcopy(receipt)
        negative["successor"] = self.seed
        self._must_refuse(lambda: self.verify_receipt(negative), "result-substitution")
        return self.payload("equivalence-evidence", receipt=receipt_ref, replays=results,
                            negatives=NEGATIVES, evaluator="bounded-ir-replay",
                            claim="equivalent-on-declared-inputs-not-universal")

    @staticmethod
    def _must_refuse(action, label):
        try:
            action()
        except (Refusal, ValueError):
            return
        raise Refusal("negative vector accepted: " + label)

    def adoption_payload(self, candidate, evidence, decision="adopt"):
        return self.payload("verification-adoption", candidate=candidate, evidence=evidence,
                            base=self._adoption_head, authorized_by=self.consent.owner,
                            decision=decision, authority_scope="local-explicit-consent")

    def route_payload(self, target, action):
        return self.payload("routing-decision", target=target, action=action,
                            base=self._routing_head, authorized_by=self.consent.owner)

    def scan_payload(self, scope, signaled=(), previous=None, baseline_every=4, parent_tile=None):
        scope, signaled = sorted(set(scope)), sorted(set(signaled))
        require(set(signaled) <= set(scope), "signal outside approved scope")
        tick, last, targets, mode = 0, 0, scope, "baseline"
        if previous:
            report = self.body(previous, "dream-report")
            tile = self.body(report["tile"], "scan-tile")
            tick = tile["tick"] + 1
            last = tile["last_baseline_tick"]
            if scope == tile["scope"] and baseline_every == tile["baseline_every"] and tick - last < baseline_every:
                mode = "delta"
                targets = sorted(set(report["exhaust"]) | set(signaled))
            else:
                last = tick
        return self.payload("scan-tile", parent_tile=parent_tile, previous_report=previous, tick=tick,
                            mode=mode, scope=scope, targets=targets, signaled=signaled,
                            baseline_every=baseline_every, last_baseline_tick=last)

    def report_payload(self, tile_ref, responses):
        tile = self.body(tile_ref, "scan-tile")
        subjects, exhaust = set(), set()
        ordered = self.ordered(responses)
        for ref in ordered:
            observation = self.body(ref, "native-shape-observation")
            require(observation["tile"] == tile_ref and observation["subject"] in tile["targets"],
                    "unbound report response")
            require(observation["subject"] not in subjects, "duplicate subject response")
            subjects.add(observation["subject"])
            if observation["findings"]:
                exhaust.add(observation["subject"])
        missing = sorted(set(tile["targets"]) - subjects)
        return self.payload("dream-report", tile=tile_ref, responses=ordered,
                            exhaust=sorted(exhaust | set(missing)), missing=missing, complete=not missing)

    def merge_payload(self, left, right):
        sides = []
        for refs in (left, right):
            values = {}
            for ref in refs:
                p = self.body(ref, "learned-projection")
                for fact in p["facts"]:
                    values.setdefault(fact["name"], {}).setdefault(p["tick"], set()).add(
                        self.core.particle(fact["value"])["hash"])
            sides.append(values)
        shared = sorted(sides[0].keys() & sides[1].keys())
        conflicts = []
        for name in shared:
            a, b = sides[0][name], sides[1][name]
            if any(len(a[tick] | b[tick]) > 1 for tick in a.keys() & b.keys()):
                conflicts.append(name)
        retained = {address(r): r for r in [*left, *right]}
        return self.payload("dimension-merge", left=self.ordered(left), right=self.ordered(right),
                            shared=shared, mergeable=[name for name in shared if name not in conflicts],
                            conflicts=conflicts, retained=self.ordered(list(retained.values())),
                            numerator=len(shared) - len(conflicts), denominator=len(shared),
                            no_shared_dimensions=not shared)

    def reattach_payload(self, stranded, reads_ref, ladder):
        manifest = self.body(reads_ref, "declared-reads")
        self.execute(manifest)
        require(self.body(stranded) == self.execute(manifest), "stranded frame does not match declared reads")
        require(len({address(r) for r in ladder}) == len(ladder) and ladder, "bounded unique ladder required")
        reads = {r["name"]: r["value"]["hash"] for r in manifest["reads"]}
        comparisons, selected = [], None
        for ref in ladder:
            base = self.body(ref, "learned-projection")
            declarations = {f["name"]: self.core.particle(f["value"])["hash"] for f in base["facts"]}
            conflicts = sorted(name for name in reads.keys() & declarations.keys()
                               if reads[name] != declarations[name])
            comparisons.append({"base": ref, "conflicts": conflicts})
            if not conflicts:
                selected = ref
                break
        return self.payload("deterministic-reattach", stranded=stranded, declared_reads=reads_ref,
                            ladder=list(ladder), comparisons=comparisons, selected=selected,
                            status="candidate" if selected else "dry-hole", grafted_from=stranded,
                            activates_routing=False)

    def membrane(self, source, reference, direction):
        require(direction == "inbound-public" and address(reference) in self.consent.public_reads,
                "one-way membrane refuses private egress or unapproved public input")
        source.frame(reference)
        return source._raw[address(reference)]

    def workspace_content(self, reference):
        p = self.body(reference)
        require(p.get("generation") == GENERATION
                and p.get("schema") in (PROFILE + "/learned-projection", PROFILE + "/workspace-successor"),
                "not an eligible workspace projection")
        if p["schema"] == PROFILE + "/workspace-successor":
            from framing import validate_outcome
            validate_outcome(self, p)
        return p

    def projection(self):
        require(self.seed is not None, "no verified seed")
        entries, adopted = [], []
        for key in sorted(self._adopted):
            ref = {"space": "rapp/1:wave", "hash": key}
            adopted.append(ref)
            p = self.body(ref, usable=False)
            try:
                self.frame(ref)
                eligible = True
            except Refusal:
                eligible = False
            if p.get("schema") in (PROFILE + "/learned-projection", PROFILE + "/workspace-successor") \
                    and p.get("generation") == GENERATION:
                route = self._routes.get(key, {"selected": False, "suppressed": False})
                entries.append({"frame": ref, **route, "selected": route["selected"] and eligible,
                                "eligible": eligible})
        result = self.payload(
            "registry-projection", adopted=adopted,
            heads=[{"stream_id": stream, "seq": len(chain) - 1,
                    "frame": {"space": "rapp/1:wave", "hash": chain[-1]}}
                   for stream, chain in sorted(self._streams.items())],
            entries=entries, migration=self._migration, authority=False)
        self.core.schemas.validate(result)
        return result

    def checkpoint(self):
        return {"estate_rappid": self.estate, "world_id": self.world, "seed": self.seed,
                "heads": self.projection()["heads"], "events": list(self._events),
                "faults": dict(self._faults)}

    def check_checkpoint(self, checkpoint):
        require((checkpoint["estate_rappid"], checkpoint["world_id"], checkpoint["seed"]) ==
                (self.estate, self.world, self.seed), "checkpoint identity substitution")
        require(self._events[:len(checkpoint["events"])] == checkpoint["events"], "rollback or history fork")
        for head in checkpoint["heads"]:
            chain = self._streams.get(head["stream_id"], [])
            require(len(chain) > head["seq"] and chain[head["seq"]] == address(head["frame"]),
                    "rollback or stream fork")
        require(all(self._faults.get(k, 2**53) <= v for k, v in checkpoint["faults"].items()),
                "fork evidence rollback")

    def save(self, destination):
        destination = Path(destination)
        with directory(destination, create=True) as root:
            lock = os.open(".writer-lock", os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600, dir_fd=root)
            try:
                require(os.fstat(lock).st_nlink == 1 and stat.S_ISREG(os.fstat(lock).st_mode), "unsafe lock")
                fcntl.flock(lock, fcntl.LOCK_EX)
                identity = self.core.octets({"schema": "rapp/1", "rappid": self.estate,
                                             "world_id": self.world, "workspace_spec": PROFILE,
                                             "workspace_generation": GENERATION})
                identity_path = destination / "rappid.json"
                if not identity_path.exists():
                    require(set(os.listdir(root)) <= {".writer-lock"}, "unmanaged destination")
                write_file(identity_path, identity, immutable=True)
                history = b"".join(self._raw[k] + b"\n" for k in self._events)
                history_path = destination / "history.jsonl"
                if history_path.exists():
                    prior = read_file(history_path, 16 * MAX_BYTES)
                    require(history.startswith(prior), "history CAS or rollback")
                require(len(history) <= 16 * MAX_BYTES, "history budget")
                for stream, chain in sorted(self._streams.items()):
                    path = destination / "streams" / stream[8:].replace("/", "--").replace(":", "--")
                    write_file(path / "rappid.json", self.core.octets({"schema": "rapp/1", "rappid": stream}), immutable=True)
                    for seq, key in enumerate(chain):
                        write_file(path / "frames" / f"{seq}.json", self._raw[key], immutable=True)
                active = {key for chain in self._streams.values() for key in chain}
                for key in set(self._events) - active:
                    write_file(destination / "quarantine" / f"{key}.json", self._raw[key], immutable=True)
                write_file(history_path, history)
                write_file(destination / "registry.json", self.core.octets(self.projection()))
            finally:
                os.close(lock)

    @classmethod
    def load(cls, parent, destination, consent, checkpoint, *, legacy=False):
        destination = Path(destination)
        require(isinstance(checkpoint, dict), "independently protected checkpoint required")
        identity = parent.parse(read_file(destination / "rappid.json"))
        require(set(identity) == {"schema", "rappid", "world_id", "workspace_spec", "workspace_generation"}
                and identity["schema"] == "rapp/1" and identity["workspace_spec"] == PROFILE
                and identity["workspace_generation"] == GENERATION,
                "stored identity schema substitution")
        require(identity["rappid"] == checkpoint["estate_rappid"]
                and identity["world_id"] == checkpoint["world_id"], "stored identity substitution")
        result = cls(parent, identity["rappid"], identity["world_id"], consent, legacy=legacy)
        for raw in read_file(destination / "history.jsonl", 16 * MAX_BYTES).splitlines():
            try:
                result.ingest(raw)
            except Refusal as exc:
                if not str(exc).startswith("stream-fork:"):
                    raise
        result.check_checkpoint(checkpoint)
        for stream, chain in result._streams.items():
            root = destination / "streams" / stream[8:].replace("/", "--").replace(":", "--")
            require(parent.parse(read_file(root / "rappid.json")) ==
                    {"schema": "rapp/1", "rappid": stream}, "stream identity substitution")
            for seq, key in enumerate(chain):
                require(read_file(root / "frames" / f"{seq}.json") == result._raw[key], "stored frame tamper")
        active = {key for chain in result._streams.values() for key in chain}
        for key in set(result._events) - active:
            require(read_file(destination / "quarantine" / f"{key}.json") == result._raw[key],
                    "fork evidence tamper")
        # Deliberately do not load registry.json: it can be absent, stale, or corrupt.
        return result


def snapshot(root):
    """Full preservation measurements only for an explicitly authorized workspace, never routed roots."""
    root = Path(root)
    entries = []
    total = 0
    with directory(root):
        pending = [root]
        while pending:
            parent = pending.pop()
            with directory(parent) as fd:
                for name in sorted(os.listdir(fd)):
                    path = parent / name
                    relative = path.relative_to(root).as_posix()
                    if relative == CONTROL_DIR:
                        continue
                    info = os.stat(name, dir_fd=fd, follow_symlinks=False)
                    mode = stat.S_IMODE(info.st_mode)
                    if stat.S_ISLNK(info.st_mode):
                        raw, kind = os.readlink(name, dir_fd=fd).encode("utf-8"), "symlink"
                    elif stat.S_ISDIR(info.st_mode):
                        raw, kind = b"", "directory"
                        pending.append(path)
                    else:
                        require(total + info.st_size <= 64 * MAX_BYTES, "migration aggregate read budget")
                        raw, kind = read_file(path, 16 * MAX_BYTES), "file"
                    entries.append({"path": relative, "kind": kind, "sha256": sha(raw),
                                    "bytes": len(raw), "mode": mode})
                    total += len(raw)
                    require(total <= 64 * MAX_BYTES, "migration aggregate read budget")
                    require(len(entries) <= 4096, "migration file budget")
    return sorted(entries, key=lambda e: e["path"])


def _prepare_migration(parent, root, consent, utc, *, source_generation, source_spec,
                       source_spec_sha256, legacy_frames=()):
    root = Path(root)
    legacy_frames = list(legacy_frames)
    require(source_generation == "pre-grail", "explicit pre-Grail source selection required")
    require(source_spec in LEGACY_LABELS, "unsupported pre-Grail source label")
    legacy_contract(source_spec, source_spec_sha256)
    identity_raw = read_file(root / "rappid.json")
    # Legacy documents need not have used canonical whitespace; preserve their octets.
    identity = parent.r._strict_json(identity_raw)
    require(isinstance(identity, dict), "legacy identity object required")
    require(identity.get("workspace_spec", source_spec) == source_spec, "legacy source label mismatch")
    require(identity.get("workspace_generation") in (None, "pre-grail"),
            "Grail or unknown generation cannot enter the pre-Grail migration lane")
    require(identity.get("schema") in (None, "rapp/1"), "legacy identity schema")
    require(parent.r.rappid_valid(identity.get("rappid")), "canonical existing RAPPID required; never remint")
    require(isinstance(identity.get("world_id"), str) and identity["world_id"],
            "existing world_id required; no inferred or replacement world")
    before = snapshot(root)
    frames_path = identity.get("frames", "frames").rstrip("/")
    parent.schemas._check(frames_path, parent.schemas.documents["common.schema.json"]["$defs"]["path"])
    prior_paths = [entry["path"] for entry in before
                   if entry["path"].startswith(frames_path + "/") and entry["kind"] == "file"
                   and entry["path"].endswith(".json")]
    retained_frames = [read_file(root / p) for p in sorted(
        prior_paths, key=lambda p: int(Path(p).stem) if Path(p).stem.isdigit() else -1)]
    require(list(legacy_frames) == retained_frames, "complete explicit legacy stream bytes required")
    result = Workspace(parent, identity["rappid"], identity["world_id"], consent, legacy=True)
    for raw in legacy_frames:
        frame = parent.parse(raw)
        require(frame["stream_id"] == identity["rappid"], "unrelated legacy estate stream")
        result.ingest(raw)
    result.birth(utc)
    registry = next((entry for entry in before if entry["path"] == "registry.json"), None)
    receipt = result.payload(
        "migration-record", source_generation="pre-grail", source_spec=source_spec,
        source_spec_sha256=source_spec_sha256, source_identity_sha256=sha(identity_raw),
        authorized_by=consent.owner,
        prior_rappid=identity["rappid"], prior_world_id=identity["world_id"],
        prior_heads=result.body(result.seed)["inherited_heads"], baseline=before,
        legacy_registry_sha256=registry["sha256"] if registry else None, writes=[CONTROL_DIR])
    parent.schemas.validate(receipt)
    return result, receipt


def plan_migration(parent, root, consent, utc, **selection):
    """Return an exact one-estate review record without writing or granting consent."""
    return _prepare_migration(parent, root, consent, utc, **selection)[1]


def migrate(parent, root, consent, utc, *, checkpoint=None, **selection):
    root = Path(root)
    result, receipt = _prepare_migration(parent, root, consent, utc, **selection)
    before = receipt["baseline"]
    destination = root / CONTROL_DIR
    if destination.exists():
        require(checkpoint is not None, "existing migration requires protected checkpoint")
        existing = Workspace.load(parent, destination, consent, checkpoint, legacy=True)
        previous = existing.body(existing._migration, "migration-record")
        require(previous["baseline"] == before, "legacy baseline changed; never overwrite")
        require(previous == receipt, "migration selection or frozen UTC changed")
        return existing
    consent.require(parent, receipt)
    result.append(receipt, utc)
    require(snapshot(root) == before, "source changed before migration publication")
    result.save(destination)
    require(snapshot(root) == before and sha(read_file(root / "rappid.json")) == receipt["source_identity_sha256"],
            "source changed during migration; sidecar is not accepted")
    return result


def metadata_egg(workspace, identities, utc):
    """Pack inert metadata in existing RAPP/1 organism → neighborhood → estate variants."""
    core = workspace.core
    require(len(identities) == 3 and len(set(identities)) == 3
            and workspace.estate not in identities
            and all(core.r.rappid_valid(r) for r in identities), "fresh artifact identities required")
    organism, neighborhood, estate = identities
    metadata = core.octets(workspace.projection())
    files = {"rappid.json": core.octets({"schema": "rapp/1", "rappid": organism}),
             "soul.md": b"Inert metadata artifact; no code, trust, or routing is inherited.\n",
             "state/registry-projection.json": metadata}
    child = core.r.pack_egg("organism", organism, utc, files=files)
    filename = lambda rid: "--".join(rid[8:].split(":")[0].split("/")) + ".egg"
    middle = core.r.pack_egg("neighborhood", neighborhood, utc, files={filename(organism): child},
                             payload={"members": [organism]})
    egg = core.r.pack_egg("estate", estate, utc, files={filename(neighborhood): middle},
                          payload={"neighborhoods": [neighborhood]})
    ok, step, reason = core.r.verify_egg(egg)
    require(ok, f"canonical egg {step}: {reason}")
    manifest, _ = core.r.read_egg(egg)
    receipt = workspace.payload(
        "metadata-only-estate-egg", egg={"space": "rapp/1:egg-manifest", "hash": core.r.egg_address(manifest)},
        selected=[{"path": "state/registry-projection.json", "kind": "file", "sha256": sha(metadata),
                   "bytes": len(metadata), "mode": 0o600}],
        data_class="godd", publication="not-authorized", native_variant="estate", import_effect="inert-no-routing")
    core.schemas.validate(receipt)
    return egg, receipt
