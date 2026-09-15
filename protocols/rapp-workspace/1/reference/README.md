# Workspace/1 core safe reference

Normative ID: `rapp-workspace/1`. Brand: **RAPP Workspace/1**.
The parent RAPP/1 checkout is explicit and byte-pinned; no home search or
legacy validator fallback occurs.

```bash
python3 -B tools/frame_lens.py demo --rapp1-path "<EXPLICIT_RAPP1_CHECKOUT>"
python3 -B tools/frame_lens.py conformance --rapp1-path "<EXPLICIT_RAPP1_CHECKOUT>"
```

The demo exposes five separate receipts. It does not claim safe external
deployment, signed authority or learned semantic capability. The canonical
scanner's nonzero frame result is labeled **RAPP integrity only**.
Supplied-file capture, retention, local synthesis and materialization have
separate CLI flags. Without materialization, the controller verifies retained
frames in memory rather than silently exporting them. All five assurance
states remain explicit when synthesis is not authorized.

## Kernel boundary

`safe_kernel.Controller` receives a typed `ExternalPolicy` and `Scope` values
from the trusted host, not from captured/learned data. `Scope` binds an opaque
native subject and optional exact local file path. Rights are independent;
capture/retention/synthesis are checked before access. The controller's
private SQLite state and process lock form one local serialization domain.
`Controller(..., now=<trusted-host-UTC>)` requires time explicitly; no candidate
timestamp or historical demo clock supplies live authorization freshness.
Only the synthetic built-in demo uses a frozen fixture clock.

`capture_octets` accepts finite immutable byte objects and records only that
scope. `capture_file` uses no-follow stable-descriptor reads, never claiming
coherent native snapshot semantics. Workspace/1 core adoption of native-backed
records/rebinding is disabled. `synthesize` produces a bounded **request** for
`identity-octets` or `json-field`; it never grants anything.

`EvaluatorImage` verifies and consumes the exact captured `total_eval.py`
octets, with a minimal builtins set and no imports/host operations. Source
path replacement after capture cannot change the consumed image. Each new
execution must freshly qualify the pinned runtime bundle. That scoped
evaluator proof is not full production interpreter/OS/key-custody qualification.

Actual, necessary and synthesis reads are distinct. JSON-field interpretation
also records membership enumeration and negative reads. Invalid UTF-8,
duplicate keys, huge integers, cyclic objects, streams and oversize inputs
cannot be repaired into valid interpretations.

## External contracts and adoption

`approve_contract` is an explicit host action. `fidelity` checks the exact
selected coverage/inverse contract independently; a replay receipt is not
fidelity. Byte identity may cover all captured octets. JSON-field projection
covers only that selected field and cannot authorize complete behavior
preservation.

`request_adoption` requires explicit integrity, observation and fidelity
receipt references, emits inert request data and returns the complete frontier.
`adopt` independently checks current policy/rights, source binding, instance/
world, graph/routing/adoption heads, suppression, contract/receipt and runtime.
SQLite COMMIT is its linearization point. Before-commit interruption rolls
back the entire decision; after-commit lost acknowledgement returns the same
result on exact retry. Changed operation content refuses.

Suppression keys use the stable external native subject, not a content hash
or occurrence wave. Reobservation cannot clear it. No distributed merge or
partitioned effects are implemented.

## Inert output, continuation and history

`materialize` writes only `view.json` under the controller. It never creates
HTML, skills, executable files or native routes. Local `export_frames` is
restricted to the controller directory and does not authorize redistribution.

Root-owned attempt/depth/frame counters and state keys persist in SQLite;
one final stop slot is reserved. Repeated requests, oscillation and fanout
cannot reset limits. `verify_historical_archive` checks parent integrity
without requiring an old application evaluator; its other guarantees remain
historical/unavailable, never freshly authorized.

`merge_measurement` requires correspondence and reports coverage; zero
comparison is unmeasured. `reattach_measurement` requires all necessary
context. `delta_plan` requires unexpired complete baselines and excludes
generated outputs. These pure measurements do not grant authority; their
unqualified live/effectful counterparts are disabled.

`register_catalog_shard` validates finite default-branch-only catalog shards
and their shared snapshot commitment. Provider-default truth remains marked
external-host-observation-unproven.
`assess_organization` requires the complete shard set and records broad
buckets, missing assignments, refinement progress or durable no-progress.
Organization input may be one source or up to 32 same-snapshot tiles; missing
or mixed tiles refuse before assessment.
`candidate_outcome` stores only a query digest and selected IDs with semantic
fidelity still unproven. `propose_subscription` withholds private/excluded
entries by default and always leaves actual Private Hive publication disabled.

The blocking matrix covers every P0/P1 requirement. Earlier candidate and
experimental implementations are isolated under `../prototypes/` and are never
imported by the safe entry point. Their regression passes are not Workspace/1
core acceptance.
