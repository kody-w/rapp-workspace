"""Deterministic bounded lens evolution; requests, exhaust and attempts are immutable frames."""

import copy

from common import Refusal, address, require
from schema_source import PROFILE

RECORDS = {"iteration-request", "iteration-exhaust", "iteration-attempt", "iteration-stop"}


def _set(values):
    return [dict(space="rapp/1:particle", hash=h) for h in sorted({v["hash"] for v in values})]


def semantic_value(w, value):
    """Stable content projection. Envelope chronology and cosmetic labels are never progress."""
    name = value.get("schema", "") if isinstance(value, dict) else ""
    if name == PROFILE + "/opaque-local-object":
        return {"object_kind": value["object_kind"], "entries": [
            {k: e[k] for k in ("path_b64", "kind", "bytes", "sha256", "octets_b64", "coverage")}
            for e in value["entries"]]}
    if name == PROFILE + "/opaque-native-source":
        return {"files": value["files"]}
    if name == PROFILE + "/native-shape-observation":
        return {"observations": [semantic(w, r) for r in value["sources"]],
                "metadata": value["metadata"] if not value["sources"] else []}
    if name == PROFILE + "/iteration-exhaust":
        return {"classification": value["classification"], "code": value["code"],
                "missing_fields": value["missing_fields"], "contradictions": value["contradictions"],
                "result": value["semantic_result"]}
    if name == PROFILE + "/lens-declaration":
        return {"program": {k: v for k, v in value["program"].items() if k != "tick"},
                "runtime_sha256": value["runtime_sha256"]}
    if name in (PROFILE + "/workspace-successor", PROFILE + "/workspace-unresolved"):
        result = {"schema": name, "source": semantic(w, value["source"]),
                  "context": semantic(w, value["context"]) if value["context"] else None}
        for key in ("members", "reason", "missing_fields", "contradictions", "adoption_eligible"):
            if key in value:
                result[key] = value[key]
        return result
    return value


def semantic(w, reference):
    return w.core.particle(semantic_value(w, w.body(reference)))


def information(w, references):
    """Only verified source evidence and replay-checked diagnostics add information."""
    pending, seen, tokens = list(references), set(), []
    while pending:
        ref = pending.pop()
        if address(ref) in seen:
            continue
        seen.add(address(ref))
        frame, body = w.frame(ref), w.body(ref)
        name = body.get("schema", "")
        if name in (PROFILE + "/opaque-local-object", PROFILE + "/opaque-native-source"):
            tokens.append(semantic(w, ref))
        elif name == PROFILE + "/native-shape-observation":
            pending.extend(body["sources"])
        elif name == PROFILE + "/iteration-exhaust":
            body = verified_exhaust(w, ref)
            tokens.append(w.core.particle({
                "classification": body["classification"], "code": body["code"],
                "missing_fields": body["missing_fields"], "contradictions": body["contradictions"]}))
            request = w.body(body["request"], "iteration-request")
            pending.extend(request["sources"] + request["contexts"])
        elif name in (PROFILE + "/workspace-successor", PROFILE + "/workspace-unresolved"):
            pending.extend(r for r in (body["source"], body["context"]) if r)
        if frame["payload"].get("schema") == PROFILE + "/derived-frame":
            reads = w.body(frame["payload"]["declared_reads"], "declared-reads")
            pending.extend(reads["sources"] + reads["contexts"])
    return _set(tokens)


def work_key(w, request):
    lens = w.body(request["lens"], "lens-declaration")
    declared = w.body(request["declared_reads"], "declared-reads") if request["declared_reads"] else None
    if declared:
        declared = {"complete": declared["complete"], "reads": [
            {k: item[k] for k in ("name", "pointer", "value")} for item in declared["reads"]]}
    value = {
        "schema": PROFILE + "/iteration-work-key", "root": semantic(w, request["root"]),
        "lens_program": w.core.particle({k: v for k, v in lens["program"].items() if k != "tick"}),
        "runtime_sha256": lens["runtime_sha256"],
        "inputs": [semantic(w, r) for r in request["sources"] + request["contexts"]],
        "declaration": w.core.particle(declared) if declared is not None else None,
    }
    w.core.schemas.validate(value)
    return w.core.particle(value)


def state(w, loop_ref):
    policy = w.body(loop_ref, "lens-loop")
    result = {"policy": policy, "requests": {}, "attempts": {}, "done": set(), "seen_work": {},
              "information": information(w, [policy["root"]]), "states": set(), "no_progress": 0,
              "last": None, "stopped": None}
    for key in w._events:
        frame = w.core.parse(w._raw[key])
        p = frame["payload"]
        if p.get("loop") != loop_ref:
            continue
        name = p.get("schema", "").split("/")[-1]
        ref = {"space": "rapp/1:wave", "hash": key}
        if name == "iteration-request":
            result["requests"][key] = p
        elif name == "iteration-attempt":
            result["attempts"][key] = p
            result["done"].add(address(p["request"]))
            result["seen_work"].setdefault(p["work_key"]["hash"], ref)
            result["information"] = p["information"]
            result["states"].add(p["state"]["hash"])
            result["no_progress"], result["last"] = p["no_progress"], ref
        elif name == "iteration-stop":
            result["stopped"] = ref
    return result


def pending(s):
    values = [(key, p) for key, p in s["requests"].items() if key not in s["done"]]
    values.sort(key=lambda item: (item[1]["depth"], item[1]["work_key"]["hash"], item[0]))
    return [{"space": "rapp/1:wave", "hash": key} for key, _ in values]


def _data_ancestor(w, child, parent):
    queue, seen = [child], set()
    while queue:
        ref = queue.pop()
        if ref == parent:
            return True
        if address(ref) in seen:
            continue
        seen.add(address(ref))
        p = w.frame(ref)["payload"]
        if p.get("schema") == PROFILE + "/derived-frame":
            reads = w.body(p["declared_reads"], "declared-reads")
            queue.extend(reads["sources"] + reads["contexts"])
    return False


def _failure_code(error):
    message = str(error)
    for needle, code in (
        ("runtime", "runtime-refusal"), ("suspended", "lens-suspended"),
        ("mapping", "mapping-not-entailed"), ("declared", "incomplete-reads"),
        ("input", "incomplete-reads"), ("context", "context-refusal"),
        ("pointer", "read-pointer-refusal"), ("schema", "schema-refusal"),
    ):
        if needle in message:
            return code
    return "verification-refusal"


def evaluation(w, request):
    try:
        reads = (w.body(request["declared_reads"], "declared-reads") if request["declared_reads"]
                 else w.reads_payload(request["lens"], request["sources"], request["contexts"]))
        require((reads["lens"], reads["sources"], reads["contexts"]) ==
                (request["lens"], request["sources"], request["contexts"]), "declared request mismatch")
        value = w.execute(reads)
    except (Refusal, ValueError) as error:
        code = _failure_code(error)
        return {"value": None, "classification": "failed-test", "code": code,
                "missing_fields": [code], "contradictions": [],
                "semantic_result": w.core.particle({"failed_test": code})}
    kind = value.get("schema")
    if kind in (PROFILE + "/workspace-successor", PROFILE + "/workspace-unresolved") \
            and value["source"] != request["root"]:
        classification, code = "refusal", "foreign-root-result"
    elif kind == PROFILE + "/workspace-successor":
        classification, code = "verified", "verified-workspace-candidate"
    elif kind == PROFILE + "/workspace-unresolved":
        code = value["reason"]
        classification = ("contradiction" if value["contradictions"] else
                          "partial" if code == "source-not-bound-to-context" else
                          "refusal" if code == "unsupported-context-repair" else "unresolved")
    else:
        classification, code = "refusal", "non-workspace-result"
    return {"value": value, "classification": classification, "code": code,
            "missing_fields": value.get("missing_fields", []), "contradictions": value.get("contradictions", []),
            "semantic_result": w.core.particle(semantic_value(w, value))}


def exhaust_payload(w, loop_ref, request_ref, result=None, receipt=None, equivalence=None):
    request = w.body(request_ref, "iteration-request")
    evaluated = evaluation(w, request)
    if evaluated["value"] is None:
        require(result is receipt is equivalence is None, "failed trial cannot claim a verified successor")
    else:
        require(all(r is not None for r in (result, receipt, equivalence)), "verified trial evidence missing")
        actual = w.body(receipt, "mutation-receipt")
        require((actual["lens"], actual["sources"], actual["contexts"], actual["successor"]) ==
                (request["lens"], request["sources"], request["contexts"], result), "trial/receipt substitution")
        if request["declared_reads"] is not None:
            require(actual["declared_reads"] == request["declared_reads"]
                    or w.body(actual["declared_reads"]) == w.body(request["declared_reads"]),
                    "declared reads changed between trial and receipt")
        proof = w.body(equivalence, "equivalence-evidence")
        require(proof["receipt"] == receipt and proof == w.evidence_payload(receipt), "trial proof substitution")
        require(w.body(result) == evaluated["value"], "trial output substitution")
    return w.payload("iteration-exhaust", loop=loop_ref, root=request["root"], request=request_ref,
                     parents=request["parents"], result=result, receipt=receipt, equivalence=equivalence,
                     **{k: v for k, v in evaluated.items() if k != "value"})


def verified_exhaust(w, reference):
    p = w.body(reference, "iteration-exhaust")
    # frame() above rechecks retained bytes and all faulted ancestry on every use.
    key = (address(reference), w.runtime_hash(), tuple(sorted(w._suspended)))
    if key in w._exhaust_checks:
        return p
    require(p == exhaust_payload(w, p["loop"], p["request"], p["result"], p["receipt"], p["equivalence"]),
            "fabricated diagnostic cannot become progress or repair authority")
    w._exhaust_checks.add(key)
    return p


def attempt_payload(w, loop_ref, request_ref, exhaust_ref):
    s = state(w, loop_ref)
    request = w.body(request_ref, "iteration-request")
    exhausted = w.body(exhaust_ref, "iteration-exhaust")
    duplicate = s["seen_work"].get(request["work_key"]["hash"])
    if duplicate:
        prior = s["attempts"][address(duplicate)]
        require(exhaust_ref == prior["exhaust"], "dedupe cannot substitute retained exhaust")
    else:
        require(exhausted["request"] == request_ref, "attempt/exhaust mismatch")
    info = _set(s["information"] + information(w, [request["root"], *request["sources"],
                                                  *request["contexts"], exhaust_ref]))
    known = {r["hash"] for r in s["information"]}
    added = [r for r in info if r["hash"] not in known]
    state_value = {"schema": PROFILE + "/iteration-state", "root": semantic(w, request["root"]),
                   "information": info, "result": exhausted["semantic_result"]}
    w.core.schemas.validate(state_value)
    commitment = w.core.particle(state_value)
    return w.payload(
        "iteration-attempt", loop=loop_ref, root=request["root"], request=request_ref,
        parents=request["parents"], ordinal=len(s["attempts"]), depth=request["depth"],
        work_key=request["work_key"], exhaust=exhaust_ref,
        execution="deduplicated" if duplicate else "executed", duplicate_of=duplicate,
        information=info, new_information=added, state=commitment,
        repeated_state=commitment["hash"] in s["states"], no_progress=0 if added else s["no_progress"] + 1)


def terminal(w, s, *, include_empty=False):
    queue = pending(s)
    candidate = None
    last = s["attempts"].get(address(s["last"])) if s["last"] else None
    exhausted = w.body(last["exhaust"], "iteration-exhaust") if last else None
    if exhausted and exhausted["classification"] == "verified":
        candidate = exhausted["result"]
        reason = "adopted-verified" if address(candidate) in w._adopted else "missing-owner-authorization"
        return reason, candidate
    if len(s["attempts"]) >= s["policy"]["max_attempts"]:
        return "attempt-budget", None
    if queue and s["requests"][address(queue[0])]["depth"] > s["policy"]["max_depth"]:
        return "depth-budget", None
    fresh_input = any(
        {r["hash"] for r in information(w, s["requests"][address(q)]["sources"] +
                                       s["requests"][address(q)]["contexts"])} -
        {r["hash"] for r in s["information"]} for q in queue)
    if last and not fresh_input and (last["repeated_state"] or
                                    s["no_progress"] >= s["policy"]["no_progress_window"]):
        return "stable-fixed-point", None
    if include_empty and not queue:
        if exhausted and exhausted["classification"] == "contradiction":
            return "explicit-contradiction", None
        if exhausted and exhausted["classification"] in ("refusal", "failed-test"):
            return "explicit-refusal", None
        return "stable-fixed-point", None
    return None, None


def stop_payload(w, loop_ref):
    s = state(w, loop_ref)
    reason, candidate = terminal(w, s, include_empty=True)
    require(reason is not None, "loop still has bounded actionable work")
    return w.payload("iteration-stop", loop=loop_ref, root=s["policy"]["root"],
                     attempts=[{"space": "rapp/1:wave", "hash": key} for key in s["attempts"]],
                     pending=pending(s), information=s["information"], candidate=candidate, reason=reason)


def validate_record(w, p):
    name = p["schema"].split("/")[-1]
    if name == "lens-loop":
        w.frame(p["root"])
        return
    require(name in RECORDS, "work/state particles are commitments, not loop frames")
    s = state(w, p["loop"])
    require(s["stopped"] is None and p["root"] == s["policy"]["root"], "stopped or foreign loop")
    if name == "iteration-request":
        require(len(s["requests"]) < 128, "bounded request frontier")
        require(p["parents"] == sorted(p["parents"], key=address), "parent set must be ordered")
        parents = [w.body(r, "iteration-attempt") for r in p["parents"]]
        require(all(v["loop"] == p["loop"] for v in parents), "foreign attempt parent")
        depth = max((v["depth"] for v in parents), default=-1) + 1
        require(p["depth"] == depth and p["work_key"] == work_key(w, p), "fabricated depth or work key")
        for r in p["sources"] + p["contexts"]:
            w.frame(r)
            data = w.body(r)
            if data.get("schema") == PROFILE + "/iteration-exhaust":
                verified_exhaust(w, r)
                if data["loop"] == p["loop"]:
                    require(any(v["exhaust"] == r or _data_ancestor(w, r, v["exhaust"]) for v in parents),
                            "consumed exhaust parent omitted")
        w.body(p["lens"], "lens-declaration")
        if p["strategy"] == "reapply":
            require(p["lens_parent"] is None and any(
                w.body(v["request"], "iteration-request")["lens"] == p["lens"] for v in parents),
                "reapply must name the same parent lens")
        elif p["strategy"] == "descendant":
            require(p["lens_parent"] is not None and p["lens"] != p["lens_parent"]
                    and _data_ancestor(w, p["lens"], p["lens_parent"])
                    and any(w.body(v["request"], "iteration-request")["lens"] == p["lens_parent"] for v in parents),
                    "fabricated lens descendant")
        else:
            require(p["lens_parent"] is None, "selected lens cannot claim a descendant parent")
    elif name == "iteration-exhaust":
        require(p == exhaust_payload(w, p["loop"], p["request"], p["result"], p["receipt"], p["equivalence"]),
                "fabricated exhaust or failed-test claim")
    elif name == "iteration-attempt":
        require(terminal(w, s)[0] is None, "attempt after termination condition")
        require(pending(s) and p["request"] == pending(s)[0], "non-deterministic iteration order")
        require(p == attempt_payload(w, p["loop"], p["request"], p["exhaust"]), "fabricated progress or state")
    else:
        require(p == stop_payload(w, p["loop"]), "fabricated termination")


class LensLoop:
    def __init__(self, workspace, loop_ref, utc):
        self.w, self.ref, self.utc = workspace, loop_ref, utc
        workspace.body(loop_ref, "lens-loop")

    @classmethod
    def create(cls, workspace, root, utc, max_attempts=12, max_depth=6, no_progress_window=2):
        ref = workspace.append(workspace.payload(
            "lens-loop", root=root, max_attempts=max_attempts, max_depth=max_depth,
            no_progress_window=no_progress_window), utc)
        return cls(workspace, ref, utc)

    def submit(self, lens, sources, *, contexts=(), parents=(), declared_reads=None,
               strategy="select", lens_parent=None):
        parents = sorted(copy.deepcopy(list(parents)), key=address)
        depth = max((self.w.body(r, "iteration-attempt")["depth"] for r in parents), default=-1) + 1
        p = self.w.payload(
            "iteration-request", loop=self.ref, root=self.w.body(self.ref)["root"], lens=lens,
            sources=list(sources), contexts=list(contexts), parents=parents, depth=depth,
            declared_reads=declared_reads, strategy=strategy, lens_parent=lens_parent, work_key={})
        p["work_key"] = work_key(self.w, p)
        return self.w.append(p, self.utc)

    def step(self):
        s = state(self.w, self.ref)
        require(s["stopped"] is None, "loop already stopped")
        if terminal(self.w, s)[0] is not None or not pending(s):
            return None
        request_ref = pending(s)[0]
        request = self.w.body(request_ref, "iteration-request")
        duplicate = s["seen_work"].get(request["work_key"]["hash"])
        if duplicate:
            exhaust = s["attempts"][address(duplicate)]["exhaust"]
        else:
            result = receipt = proof = None
            evaluated = evaluation(self.w, request)
            if evaluated["value"] is not None:
                declared = self.w.body(request["declared_reads"]) if request["declared_reads"] else None
                receipt = self.w.mutate(request["lens"], request["sources"], self.utc,
                                        contexts=request["contexts"], declared=declared)
                proof = self.w.append(self.w.evidence_payload(receipt), self.utc)
                result = self.w.body(receipt)["successor"]
            exhaust = self.w.append(exhaust_payload(self.w, self.ref, request_ref, result, receipt, proof), self.utc)
        return self.w.append(attempt_payload(self.w, self.ref, request_ref, exhaust), self.utc)

    def finish(self):
        current = state(self.w, self.ref)
        if current["stopped"]:
            return current["stopped"]
        return self.w.append(stop_payload(self.w, self.ref), self.utc)

    def run(self, planner=None, reviewer=None):
        while True:
            attempt = self.step()
            if attempt is None:
                return self.finish()
            exhausted = self.w.body(self.w.body(attempt)["exhaust"], "iteration-exhaust")
            if reviewer and exhausted["classification"] == "verified":
                reviewer(self, attempt, exhausted)
            if planner and exhausted["classification"] != "verified":
                planner(self, attempt, exhausted)
            s = state(self.w, self.ref)
            if terminal(self.w, s, include_empty=True)[0] is not None:
                return self.finish()
