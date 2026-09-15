"""One bounded, ephemeral validation context for a whole composite DAG or recovery pass."""

from common import address, require


class CompositeWork:
    def __init__(self, controller, *, historical=False, verified_frames=None):
        self.controller = controller
        self.policy = controller.policy
        self.historical = historical
        self.verified_frames = verified_frames
        self.memo, self.catalogs, self.assessments, self.bindings, self.ledgers = {}, {}, {}, {}, {}
        self.active, self.nodes = set(), set()
        self.raw_frames, self.frames = {}, {}
        self.edges = self.serialized_bytes = self.work_units = 0
        self.depth = 0

    def charge(self, units):
        require(self.work_units + units <= self.policy.max_composite_work,
                "workspace-composite-work-budget")
        self.work_units += units

    def charge_bytes(self, size):
        require(type(size) is int and size >= 0
                and self.serialized_bytes + size <= self.policy.max_composite_bytes,
                "workspace-composite-byte-budget")
        self.serialized_bytes += size

    def reserve(self, keys, level):
        require(level <= self.policy.max_composite_depth, "workspace-composite-depth-budget")
        self.charge(len(keys) + 1)
        require(len(self.nodes | set(keys)) <= self.policy.max_composite_nodes,
                "workspace-composite-node-budget")
        self.nodes.update(keys)
        self.depth = max(self.depth, level)

    def children(self, references, level):
        require(self.edges + len(references) <= self.policy.max_composite_edges,
                "workspace-composite-edge-budget")
        if references:
            self.reserve([address(ref) for ref in references], level + 1)
        self.edges += len(references)

    def _raw_frame(self, *, key=None, seq=None):
        lookup = ("hash", key) if key is not None else ("seq", seq)
        if lookup in self.raw_frames:
            return self.raw_frames[lookup]
        self.charge(1)
        if self.verified_frames is not None:
            entry = self.verified_frames.get(lookup)
            require(entry is not None, "missing-frame")
            frame, size = entry
            self.charge_bytes(size)
        else:
            row = self.controller.db.execute(
                "SELECT seq,hash,length(raw) FROM frames WHERE " + lookup[0] + "=?", (lookup[1],)
            ).fetchone()
            require(row is not None, "missing-frame")
            number, digest, size = row
            self.charge_bytes(size)
            raw = self.controller.db.execute("SELECT raw FROM frames WHERE hash=?", (digest,)).fetchone()[0]
            require(len(raw) == size, "workspace-composite-frame-substitution")
            frame = self.controller.core.parse(raw)
            require(frame["seq"] == number and frame["frame_hash"] == digest,
                    "workspace-composite-frame-substitution")
        self.raw_frames[("hash", frame["frame_hash"])] = frame
        self.raw_frames[("seq", frame["seq"])] = frame
        return frame

    def body(self, reference):
        key = address(reference)
        if key not in self.frames:
            frame = self._raw_frame(key=key)
            if self.verified_frames is None:
                previous = self._raw_frame(seq=frame["seq"] - 1) if frame["seq"] else None
                ok, step, reason = self.controller.core.r.verify_frame(
                    frame, head=previous, stream_id_of_record=self.policy.instance_rappid)
                require(ok, f"retained-frame-tamper:{step}:{reason}")
                self.controller.core.schemas.validate(frame["payload"])
            self.frames[key] = frame["payload"]
        return self.frames[key]

    def stats(self):
        return {"nodes": len(self.nodes), "edges": self.edges, "serialized_bytes": self.serialized_bytes,
                "work_units": self.work_units, "depth": self.depth}
