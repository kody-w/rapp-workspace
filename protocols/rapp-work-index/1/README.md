# RAPP Work Index/1

An optional **non-authoritative** application profile. Exact-key SQLite
acceleration, collision-preserving summon buckets, deterministic Merkle
shards, checkpoint-bound pagination and explicit-byte anti-entropy do not
change the closed RAPP wire/workspace/hive/federation profiles or activate
an estate. See [SPEC.md](SPEC.md), [schema.json](schema.json),
[safety-matrix.json](safety-matrix.json) and [provenance.json](provenance.json).

## Check from the repository root

Python 3.11+ and SQLite are sufficient for the index runtime and pure tests.
The signed evidence additionally uses an explicitly supplied canonical
`rapp-1` checkout at `dda32d741c7218f41443a5bd17eebfe0eae82cb7` and its
`cryptography` verification dependency. No checkout discovery or network
download occurs.

```bash
python3 -B tools/work_index.py schemas --check
python3 -B tools/work_index.py vectors --check
python3 -B tools/work_index.py pins --check
python3 -B tools/work_index.py tests
python3 -B tools/work_index.py vectors --check --rapp1-path "<EXPLICIT_RAPP1_CHECKOUT>"
python3 -B tools/work_index.py conformance --rapp1-path "<EXPLICIT_RAPP1_CHECKOUT>" \
  --output .validation/rapp-work-index-1
python3 -m py_compile tools/work_index.py protocols/rapp-work-index/1/reference/*.py \
  protocols/rapp-work-index/1/tests/*.py
git diff --check
```

If the signed gate reports the missing verification dependency, explicitly
install `protocols/rapp-work-index/1/requirements-conformance.txt`. It is not
a runtime dependency. Without a canonical checkout, run the first four
commands but report **conformance blocked**; zero-Frame checks are not passes.
Conformance emits and independently verifies nine actual signed Frames
(seven sources, two checkpoints), runs all pure and canonical refusal tests,
checks pins again, and persists `conformance-results.json`.
An existing valid output index can be checked again; a corrupt/stale one
refuses and must be explicitly discarded/rebuilt. Source/high-water authority
is never stored exclusively in that disposable database.

### Closed-profile integration boundary

Workspace/1 pins the repository's root `README.md`, root `SKILL.md` and
`protocols/README.md` as frozen evidence. This additive profile therefore
registers itself only through its own exact files, `protocols/index.json` and
the independent CI job. Those sealed shared documents remain byte-identical;
discoverability never repins or bypasses the closed Workspace/1 acceptance
surface.

## Intentional generation, then exact checking

```bash
python3 -B tools/work_index.py schemas --write
python3 -B tools/work_index.py vectors --write --rapp1-path "<EXPLICIT_RAPP1_CHECKOUT>"
python3 -B tools/work_index.py pins --write
python3 -B tools/work_index.py schemas --check
python3 -B tools/work_index.py vectors --check --rapp1-path "<EXPLICIT_RAPP1_CHECKOUT>"
python3 -B tools/work_index.py pins --check
```

The final writer inventories all profile files and updates only this profile's
entry in `protocols/index.json`; its fixed timestamp follows the branch's
existing convention. Manifest/schema/index drift is blocking. Fixtures contain
only synthetic payloads and explicitly public, reproducible test-key identities;
there are no private paths, credentials or downloaded executable artifacts.

## Reference API and host obligations

`reference/work_index.py` exposes:

- `build_generation(records, generation, context, sources)` → canonical
  manifest, sixteen exact shard byte strings, sixteen inclusion proofs.
- `bind_checkpoint` / `validate_checkpoint_binding` → strict binding to a
  **protected caller-supplied canonical verification record**, not a
  self-asserted JSON approval. `check_transition` refuses forks/rollback.
- `PinnedGeneration(manifest, verified_frame, expected_context, previous)` →
  immutable comparison state. A host must retain the previous high-water
  binding separately and independently refresh the full current frontier.
- `verify_shard` / `accept_shard` → exact-byte, canonical and proof checks
  against the pin, never automatic trust or authority merge.
- `ExactIndex.build(path, pin, current_frontier, [(bytes, proof), ...])`,
  then context-managed `ExactIndex(path, pin, current_frontier)` →
  a verified read-only SQLite snapshot. Paths must be explicit, relative,
  caller-owned `.sqlite3` paths; no symlinks or automatic fallback.
- `index.page(current_frontier, domain, key, page_size=..., token=...)` →
  candidate records and an opaque deterministic continuation, or explicit refusal.
- `index.lookup(current_frontier, domain, key)` → the complete bounded exact
  collision bucket in full identity order, never a selected winner.
- `index.summon(current_frontier, domain, key, full_identity, raw_content)` →
  `disambiguated-not-authorized`. Every collision is retained; no first repo wins.
- `anti_entropy(local, target, local_frontier, target_frontier, supplied_bytes)`
  → exact changed/missing/divergent hash reports; it never fetches.
- `cache_key(raw, pin, current_frontier)` and `platform_adapters()` →
  fully contextual cache identities and optional adapter mappings.

`pin.frontier` is not fresh host policy. Do not feed received JSON or a stale
cache back into the external trust API. The pure tests use clearly named
`receipt_double` fixtures; signed conformance separately checks actual Frames
through the pinned canonical implementation.

SQLite B-tree lookup is indexed O(log n + results) **after O(n + bytes) snapshot
verification**; process-local hash lookup is only expected O(1). All work has
explicit count/byte ceilings, not a potato-class latency promise. POSIX SQLite
is implemented; Windows SQLite/safe-copy/ReFS and browser IndexedDB/OPFS/
WebCrypto are mappings requiring equivalent verification, not deployment
certifications. Sleeping organisms require no resident process, polling or
network. All rights, revocation, activation and live-source use stay external.
