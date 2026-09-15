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
`Controller` defaults to **live activation** and the host UTC clock. Every
authorization boundary samples that clock anew; `now` is read-only last-sample
diagnostics, not a constructor parameter. The clock floor advances on
authorized reads and survives transaction rollback. A host may inject
`clock()` returning canonical UTC milliseconds; a callback sourced from
candidate data is not trusted. Host-clock correctness and whole-store rollback
protection remain external obligations.

Live construction requires the closed `activation-document.schema.json` and
an independently installed `verify_activation(document, now)` callback:

```python
controller = Controller(
    core, owned_directory, external_policy,
    activation=host_selected_activation,
    verify_activation=host_verify_activation,
)
```

The callback must authenticate the **entire exact** document against a protected
allowlist/trust anchor, including the signer key ID and fresh revocation state.
The document binds `spec_id`, `spec_sha256`, `runtime_sha256` (the manifest
hash), `instance_rappid`, `world_id`, `not_before_utc`, `expires_utc`,
`signer_key_id` and `revocation_status`. The reference checks exact bindings and
validity and requires a literal `True` from the callback on every boundary.
Neither `revocation_status:active` nor recomputing the local hashes authenticates
anything. Exceptions and truthy data-shaped results refuse before source IO.
An always-true production callback is not an implementation of this contract.
The reference provides no signature scheme, signer, key storage or qualified
revocation client; those belong to the trusted host integration.

Synthetic use must be explicit:

```python
controller = Controller(
    core, owned_directory, external_policy,
    activation_mode="synthetic", clock=lambda: "2026-09-15T03:12:29.000Z",
)
```

All frames/receipts, frontiers, projections and demo reports carry
`activation_mode`. A supplied-file demo also uses labeled synthetic activation
but samples the actual host clock. The exact activation is persisted and must
match on reopen; mode changes and activation substitution refuse. Authenticated
renewal/rotation and migration from the old record shapes are not implemented.
Do not remove controller state or silently rewrite pins to get around this.

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
`compose_workspace` creates controller-owned routing DAG nodes from catalog
entries and verified child composites. Its closed `workspace_bindings`
descriptors bind entry IDs and metadata digests. Unknown metadata has null
RAPPID/world/evidence and stays `preserved-by-reference-unverified`; absence
of a native write is not evidence that an identity/world was observed.

To establish a stronger **metadata association**, install
`verify_workspace_binding(claim, metadata)` on the controller, independently
of candidate data, then call:

```python
binding = controller.register_workspace_binding(
    subject, assessment, entry_id,
    child_rappid=observed_child_rappid, child_world_id=observed_child_world,
    metadata=exact_metadata_bytes,
)
```

The closed claim contains `entry_id`, `child_rappid`, `child_world_id` and
`source_metadata_sha256`. The bytes must match the selected catalog entry's
digest; capture/synthesis/retention restrictions apply. Only an independent
verifier's literal `True` creates an indexed `workspace-binding` evidence
record. Future composites may reference it; existing composites are immutable.
Composite fields expose verified/unverified counts, complete transitive binding
commitments and `child_identity_status`/`child_world_status`. Only fully
evidenced membership reports `verified-external-bindings`. This proves no
ongoing native state, current child rights or migration safety. Verified and
unverified pointers alike confer **no authority**.

`CompositeWork` is one ephemeral context per complete request/recovery pass.
It memoizes validated wave hashes, catalog data and evidence; checks active
paths for cycles; and reserves aggregate nodes, edges, depth, serialized
frame/index bytes and deterministic work units before further work. The limits
in `ExternalPolicy` default to hard ceilings of 512 nodes, 4,096 edges, 16 MiB,
1,000,000 work units and depth 32. Work includes catalog walks and member
aggregation/sorting; bytes include newly emitted composite/binding frames.
Policy updates cannot increase those limits. A too-small limit can quarantine
recovery of an existing larger estate; never reset state to bypass it.
Wide, deep and shared DAGs must either verify within the budget or refuse
without creating a wrapper. This is bounded validation, not a latency promise.

`verify_history` verifies bounded RAPP history, then checks one shared composite
context, exact host activation, clock floor, workspace-binding/assessment/
composite tables and their atomic indexes. Missing, extra or substituted rows
quarantine the controller. Historical checks do not query current activation
or infer renewed permissions; current work still reauthenticates. External
checkpoints cover the new record sets as well. Complete malicious store
rewrites require independent protected anchors, not self-authentication.

The blocking matrix covers every P0/P1 requirement. Earlier candidate and
experimental implementations are isolated under `../prototypes/` and are never
imported by the safe entry point. Their regression passes are not Workspace/1
core acceptance.
