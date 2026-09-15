# RAPP Workspace/1 — core protocol

**Protocol identifier:** `rapp-workspace/1`

**Name:** RAPP Workspace/1

**Parent:** current canonical RAPP/1, unchanged.

**Status:** core authority. Estate activation and safe external deployment are
separate states and are not implied. The [blocking matrix](safety-matrix.json),
[schemas](schemas/) and [exact-byte manifest](manifest.json) are normative.

MUST, MUST NOT, REQUIRED, SHOULD and MAY are normative requirements.

## 1. Five guarantees, never one compliance Boolean

**RAPP-valid != accurately observed != semantically faithful != currently
authorized != safely deployable.**

These guarantees MUST have separate scoped receipts:

| Guarantee | What its receipt can establish | What it cannot establish |
|---|---|---|
| `rapp_integrity` | Exact canonical RAPP/1 frame/content/chain integrity under the stated verifier | Native truth, semantics, permission or safe execution |
| `observation` | The exact captured octets and stated observation consistency/coverage | A coherent live snapshot merely because reads were stable |
| `semantic_fidelity` | The exact externally selected mapping/coverage/inverse contract was checked | Universal domain semantics, native compatibility or authority |
| `current_authorization` | The external controller authorized one scoped action against a current frontier | A reusable capability, transitive grant or future permission |
| `safe_deployment` | Only the explicitly qualified deployment class, when implemented | A consequence of any other receipt |

Receipts MUST bind subject, native subject, instance/world, exact validator
identifier and pin, runtime commitment, scope, method, evidence and inherited
restrictions. Status MUST distinguish verified, unproven, refused, expired
and historical. A receipt for one guarantee MUST NOT satisfy another gate.
A syntactically valid, forged or stale receipt MUST NOT become authority.

Workspace/1 core emits `safe_deployment:refused` for external effects. There is no
“all green therefore deploy” shortcut. An integrity scanner's COMPLIANT
verdict MUST be reported as integrity only.

## 2. Core authority, prototypes and parent authority

`rapp-workspace/1` is the sole current RAPP Workspace core protocol. Every
earlier workspace protocol line—including `rapp-workspace/1.0`, `/1.1`, `/2.0`
and the previously named candidate—is prototype history. Prototype identifiers and
bytes MUST NOT be relabeled current, selected by the core validator or treated
as normative predecessors.

Every receipt MUST bind `rapp-workspace/1` and its exact normative SHA-256.
Wrong-ID and wrong-pin inputs MUST refuse, never be repaired or silently passed
to a convenient prototype validator.

The [prototype archive](../prototypes/README.md) preserves the earlier
candidate and available published snapshots without changing their bytes.
Absence of an original `rapp-workspace/1.0` SPEC in this checkout does not
justify inventing one. Prototype regression results MUST NOT count as
RAPP Workspace/1 core acceptance.

RAPP/1 exclusively defines canonicalization, identity, hashes, the eleven-key
frame, signatures, stream order, eggs and its signed registry. The envelope
MUST remain exactly:

```text
spec kind stream_id seq utc payload payload_hash frame_hash prev prev_wave sig
```

`spec` remains `rapp/1`. Reference records use registered `body.pulse` body
streams and canonical primitives from an explicitly supplied, byte-pinned
RAPP/1 checkout. No new identity/hash domain/registry is defined. The current
inspection commit is `dda32d741c7218f41443a5bd17eebfe0eae82cb7`,
revision wave `83ca275f35cca96e43d75c99d338326c1a39b2240eabf57eb7c29ac96cc90818`.
Frame Chains at `0aeb8332f4bb20bc689aba217a704b463ba20105` is orchestration
provenance only, not substrate or authority.

## 3. Minimal kernel and closed effect boundary

Workspace/1 core consists of:

1. unchanged RAPP/1;
2. scoped observation records;
3. immutable derivation relations with propagated restrictions;
4. one small total, effect-free, bounded evaluator;
5. scoped verification receipts;
6. an **external** adoption/capability controller;
7. deterministic inert materialization; and
8. a root-owned bounded scheduler with durable continuation.

Frame Chains mechanisms grow above this kernel. A mechanism lacking its
necessary proof MUST be disabled/refused, not implemented through a weaker
fallback. In particular, Workspace/1 core disables remote model submission,
network/loopback access, arbitrary imports/host tools/code, external effects,
partitioned execution, live native rebinding/migration, timed physical
erasure, unqualified runtimes, repository cloning, non-default branch history,
Hive publication and claims of learned semantic capability.

The evaluator accepts a closed data instruction, never Python, shell,
templates, imports or callbacks. Supported operations are bounded byte
identity and exact JSON-field projection. Unknown effects MUST refuse before
access/egress. Loopback, a private URL, local credentials, a transport session
or a model-supplied `local:true` flag MUST NOT prove locality or permission.
No ambient credential, environment, network, import or tool surface is
available to candidate programs.

The exact `total_eval.py` closure has no imports. The host verifies its bytes,
captures them in an immutable byte object, compiles those same captured
bytes with an explicit minimal builtins set, and invokes only that evaluator.
It MUST NOT hash a pathname then later launch different bytes through it.
Every fresh execution MUST requalify the entire pinned runtime manifest.
Alternate bytecode, generated code, plugins or dependencies are disabled.
This scoped evaluator proof is NOT full production interpreter/OS/key-custody
qualification; safe external deployment remains disabled.

## 4. Authority before observation or synthesis

Effective capabilities MUST stay outside all learned, received or derived
graphs. The controller is initialized from independently selected host policy,
scopes, validator/runtime pins and protected instance/world identity.
A source, lens, failure, adoption-shaped value, receipt or projection MUST
NOT create, widen, renew or replace that policy.

### 4.1 Authenticated live activation, explicit synthetic operation

A controller MUST distinguish `live` from `synthetic` activation. The reference
defaults to `live` and MUST refuse before creating controller storage without
an independently authenticated, closed `activation-document`. That document
binds the exact Workspace/1 spec SHA-256, runtime **manifest** SHA-256,
instance RAPPID, world, not-before and exclusive expiry times, signer key ID
and revocation status. Local hash recomputation, a matching manifest, an
approval-shaped frame or a signer-name string is insufficient.

The trusted host MUST install `verify_activation(document, now)` independently
of candidate data. It MUST authenticate the entire exact document against an
independent trust anchor or protected allowlist, including signer eligibility
and current revocation state. The reference rechecks that hook at every
authorization boundary and requires the literal Boolean `True`; missing hooks,
exceptions, truthy approval-shaped values, inactive documents and mismatched
bindings refuse. A document's `revocation_status:active` is not its own proof.
This is an explicit verification/trust interface, **not** a new signature scheme.
Production signature verification, key custody, trust-anchor distribution and
revocation-service qualification remain external obligations.

Tests and demos MAY explicitly select `activation_mode="synthetic"`. All their
records, receipts, frontiers and projections MUST carry that label and bind the
synthetic activation commitment. Synthetic status is never authenticated live
activation, including a demo reading an explicitly permitted local file.
The stored activation binding is immutable for this controller lifetime and
on reopen. Silent synthetic/live promotion, downgrade, activation substitution
and renewal refuse. An authenticated rotation/renewal transition is not
implemented in this wave; deleting/resetting state is not such a transition.
No activation mode enables the otherwise disabled external effects.

### 4.2 Fresh trusted time at each boundary

Rights for capture, local synthesis, model submission, retention,
redistribution, adoption, materialization and execution MUST be separate.
Authorization for capture is not authorization for model submission; private
storage is not permission to redistribute; a retained artifact is not a grant.
All relevant current rights and inherited restrictions MUST be checked before
the first source access, decoding/synthesis action, output write or egress.
The controller MUST sample a trusted host clock at **every** authorization
boundary, including direct persistence, contract/policy updates, adoption
commit and each output write. A constructor timestamp MUST NOT authorize
later work. The reference defaults to the host UTC clock; deterministic
fixtures use an explicitly installed `clock()` callback returning canonical
UTC milliseconds. `now` is only the last sampled value, not a writable clock
or a constructor authorization argument.

Time MUST be valid and nondecreasing relative to both the in-process high-water
mark and durable clock floor. Current policy expiry and activation validity
MUST be checked on fresh samples. Read-only-looking authorized operations
advance the floor; rolling back work MUST NOT roll back already observed time.
Candidate timestamps, cached receipts or data-supplied callbacks cannot supply
freshness. An injected host callback is a trust obligation, not proof that a
frozen or malicious host clock is correct. Protected monotonic hosting and
external checkpoints are still required against whole-store/host rollback.

A denied/expired capture MUST NOT stat, enumerate, open, hash or parse the
source. A denied synthesis MUST NOT decode source content. An unsupported
model/network/host operation MUST fail before credentials or transport are
touched. Workspace/1 core demos use explicit external synthetic policies; they
MUST NOT represent those as real owner signatures.

## 5. Observation forms and consistency

Opaque observation accepts **finite octets**, not arbitrary live iterators,
streams, cyclic Python objects or unbounded containers. Invalid UTF-8,
duplicate JSON names and huge integer tokens may be captured opaquely as
bytes but MUST refuse interpretation under the parent's strict domain.
The reference caps captured octets at 64 KiB and parsed depth at 64.

`supplied-immutable-octets` means exactly the byte object supplied by the
trusted caller, not an asserted native snapshot. `stable-descriptor-not-coherent`
means bounded no-follow regular-file reads passed before/after object checks;
it MUST NOT claim a coherent multi-file/live state. The frame binds exact
captured buffers, byte count, content measurement and source binding.

Directory/live-profile/coherent-native capture is not proved by stable file
stats and is disabled in Workspace/1 core. A producer requiring a stronger
consistency class must supply an independently qualified snapshot mechanism,
not a Boolean payload flag. Native rebinding and native-backed adoption
remain disabled. Captured-view adoption is restricted to supplied immutable
octets and does not select a native route.

## 6. Restrictions survive every derivation

All sources, lenses, synthesis inputs, results, refusals, exhaust and receipts
MUST carry propagated restrictions. Effective child rights are the
intersection of all ancestors and current external policy; audiences also
intersect. No output may loosen a restriction or erase a restrictive parent.

Content addresses, filenames, source relationships and low-entropy raw hashes
are sensitive GODD by default. A hash is not sanitization. A public receipt
cannot safely expose a private dictionary-testable commitment merely because
plaintext was omitted. Workspace/1 core has no public redistribution path.

Retention and deletion semantics MUST be honest. Immutable history and
backups do not provide guaranteed recall or physical erasure. Workspace/1 core
refuses capture under a policy requiring timed physical deletion that it
cannot prove. Retention revocation stops new authorized persistence/use;
historical integrity is not renewed retention/access authority. Never claim
that deleting a projection erased retained source, derived or replica bytes.

## 7. Identity and source occurrence are different concepts

Implementations MUST distinguish:

- content address: the canonical RAPP particle of captured content;
- occurrence: the RAPP frame wave/stream position recording one observation;
- native subject: the externally bound opaque namespace/native-key pair;
- live instance: the mint-once canonical workspace RAPPID;
- display name: presentation only, never an identity or grant.

Native subjects MUST NOT be invented from filenames or content hashes.
The controller's explicit subject binding is a routing/provenance descriptor,
not another RAPP identity namespace. Reobserving or reencoding a subject MUST
NOT clear suppression. Suppression is keyed to the stable external subject,
not a rendition's content/wave hash. Native/path rebinding requires a distinct
verified owner transition and is disabled in this first class.

## 8. Replay, reads, coverage and fidelity

Replay equality is execution evidence, not semantic fidelity. Every
interpretation MUST bind actual reads, necessary reads and synthesis reads
separately. Negative reads, membership enumerations and environment inputs
MUST be explicit. Required unknown/undeclared reads MUST refuse. Environment
reads are empty in Workspace/1 core; adding one cannot silently broaden the sandbox.

Fidelity requires an independently selected exact mapping/correspondence
contract, explicit covered and uncovered source scope, and a verified result.
Byte identity can prove complete captured-octet coverage with an exact inverse.
JSON-field projection can prove only selected-field coverage; it MUST NOT
claim full-source behavior preservation. Missing fields and unknown native
semantics remain scoped refusals/unproven states.

The reference cannot prove general learned capability, semantic synthesis
quality or unseen native transfer from its synthetic fixtures. Those claims
are explicitly disabled. A future learned-capability claim requires actual
synthesis, independent evaluation and unseen transfer evidence bound to the
exact artifact; canned fixtures, names or replay alone are insufficient.

## 9. External adoption transaction and first-writer rule

Lens/adoption-shaped data is a request only. Effective adoption is one
controller transaction that validates all of:

- fixed instance/world;
- independently authenticated live activation (or explicitly labeled
  synthetic activation), never inferred from the graph;
- current external policy and action-specific rights;
- exact source/occurrence/native-subject binding;
- graph, adoption and routing heads;
- complete suppression frontier;
- approved fidelity contract and matching scoped receipt;
- separately verified integrity and observation receipts for their exact
  candidate/source subjects (neither substitutes for fidelity);
- exact runtime qualification; and
- operation idempotency commitment.

The request's frozen frontier and the externally supplied current frontier
MUST agree. A stale source, policy, routing/adoption head, suppression set,
runtime or world refuses the whole operation. A fresh approval cannot repair
missing source/fidelity evidence or widen inherited restrictions.

Workspace/1 core permits one trusted local writer. A private controller directory,
exclusive process lock and serialized SQLite transaction enforce this local
class. The COMMIT is the linearization point. Frames/receipts/decision ledger
and heads commit or roll back together. An interrupted transaction MUST not
leave a partial adoption. A lost acknowledgement MUST return the existing
committed result on exact retry; changed operation content MUST refuse.

External/partitioned side effects and distributed controller merge are
disabled. No last-writer-wins merge may erase suppression, policy or competing
heads. Verified owned-store forks MUST latch refusal and preserve both proofs;
an unsigned local fault MUST NOT be described as signed owner equivocation.
A whole-store rollback needs an independently protected checkpoint; the
rolled-back store cannot authenticate itself.

`verify_history` and startup recovery MUST compare the stored activation to
the independently installed host binding and validate the clock floor.
Controller-owned workspace-binding, assessment and composite rows MUST agree
with their atomically maintained authority indexes and retained frames.
Missing, extra, substituted or dangling rows/index entries quarantine the
store; matching data-shaped records do not restore authority. Independently
retained checkpoints also bind activation, time and these record sets.
These consistency checks are not protection against an adversary rewriting
the entire store and its local indexes together.

## 10. Inert projections, portability and materialization

Projections are deterministic data views of controller-accepted history,
never sources of capability authority. Rebuilding data MUST NOT rebuild
permissions from learned adoption records. The only Workspace/1 core materializer
output is fixed-path canonical JSON under the controller-owned directory.

HTML, scripts, Markdown instructions, skill files, hooks, active URLs/remote
images, terminal controls and executable permissions MUST NOT be materialized
or rendered as behavior. Untrusted strings in diagnostics MUST be safely
escaped. Opening/downloading/compiling objects because they claim a capability
is disabled. Materialization must check current and inherited rights.

Portable verified bytes are not native rebinding. Local inspection export is
limited to the controller-owned output scope and does not grant
redistribution, native path selection, ownership, source writes or execution.

## 11. Root-owned scheduling, continuation and historical verification

Attempts, depth, bytes/frame work and all descendants/fanout MUST share one
external root-owned budget. Children cannot reset budgets by renaming a lens,
creating a subloop or presenting a new frame. One stop-record slot MUST be
reserved before work begins. Evaluator exhaustion, no-op/repeated state, oscillation
or ping-pong MUST terminate with retained evidence, not recurse unboundedly.
Continuation state and idempotency MUST survive restart.

The reference defaults to eight attempts, depth four, 256 frame slots and
1 MiB aggregate captured octets; hard ceilings are 128 attempts, depth 32,
512 frames and 64 MiB aggregate capture. Policy updates MUST NOT reset or
increase an existing root's budget. Final budget stops are durable and exact
retries reuse the stop rather than consume unbounded new stop frames.

Composite validation has a separate **shared per-request traversal budget**
selected by the external root policy, not by any child. One context covers
the proposed root and all descendants, or all recorded composites during one
recovery pass. Defaults and hard ceilings are 512 unique composite nodes,
4,096 child edges, 16 MiB of referenced/produced serialized frame and controller
index bytes, 1,000,000 deterministic work units, and depth 32. Policies may
lower these limits but cannot raise/reset them on an existing controller.
Nodes/edges/depth are reserved before descent; frame byte lengths are checked
before fetching SQLite blobs. Work is charged before catalog walks, member
merges and sorting/hashing. Shared children are validated once per wave hash
within the context, with separate active-path cycle detection; memoization
never survives a request, policy change or recovery pass.

Recovery first verifies a separately bounded full history (512 frames, 64 MiB),
then uses that verified frame cache and one aggregate composite context.
These bounds are deterministic validation limits, not wall-clock performance
promises. A composite validation refusal leaves frames/authority ledgers
unchanged; it does not produce a candidate or reset evaluator counters.
Unlike evaluator scheduler stops, those validation diagnostics are not
claimed to be durable stop receipts.

Historical RAPP integrity and scoped historical receipts MUST remain
inspectable even when the old application evaluator is unavailable.
Unavailable historical replay MUST be labeled unavailable, not false and not
freshly verified. New execution requires current qualification and rights;
an old pass or a valid chain cannot satisfy those gates.

## 12. Recursive catalogs, outcome routing and Hive proposals

A unified workspace MAY catalog an explicitly authorized repository estate
without cloning it or opening every folder. Provider access occurs outside the
core effect boundary. Workspace/1 receives only finite captured catalog shards
whose exact bytes, indexes, count and source restrictions are bound to RAPP/1
frames.

Repository catalogs are **default-branch-only**. A selected default branch is
the repository's main working branch regardless of its literal name. Branch
history, other refs, automatic checkout and repository cloning are separate
effects and remain disabled. The core verifies the closed branch-scope field,
catalog snapshot and captured tree commitments; it does **not** independently
prove that an external provider reported the selected ref as default. Current
records therefore carry `external-host-observation-unproven`. A future
qualified provider adapter/receipt is required before claiming provider truth.
A recursive file map MAY remain in manager-owned private storage while the
framed catalog entry binds its digest, completeness, labels and source
classification.

Non-Git local workspace catalogs MUST use
`branch_scope:not-applicable` together with
`branch_evidence_status:not-applicable`. They MUST NOT fabricate a repository,
branch or commit merely to enter a workspace composite.

Every complete catalog MUST:

- use one catalog/root identity and contiguous shard indexes;
- refuse missing, duplicate or substituted shards and duplicate entry IDs;
- retain parent links without cycles or references outside the complete
  catalog;
- distinguish public, private and excluded source classifications without
  treating any classification as publication authority; and
- propagate restrictions across every shard, tree, outcome and proposal.

An organization tree is a candidate lens output, not authority. The controller
MUST accept it as one to 32 contiguous content-addressed tiles sharing one
complete tree commitment. This avoids one giant organization payload. The
controller MUST assess the combined assignments, unknown/duplicate entries,
group graph, depth and largest direct bucket against externally selected
bounds. Missing, duplicate, mixed-snapshot or substituted tiles refuse. An
ineffective but valid tree emits `needs-refinement`. A successor assessment
MUST bind the previous assessment and demonstrate measurable improvement.
Repeated non-improvement emits `no-progress`; it MUST NOT be called organized
or loop forever. Every attempted shape remains in history.

Large local sources such as Downloads, Documents or Desktop are **scan
boundaries**, not one editor folder per file. Recursive file/path metadata
belongs in bounded, resumable, no-follow external indexes whose exact digests
are bound by catalog entries. Content is fetched only after an outcome selects
an authorized object. Generated outputs, credentials, native stores, symlinks,
device-boundary escapes and the manager itself MUST be excluded. The UI or
editor MUST open focused outcome subsets, never the whole recursive file tree.

A verified organization MAY be wrapped into a `workspace-composite`.
Composites contain catalog entry IDs and/or controller-verified child
composites. They are routing-only pointer structures: the wrapper neither
changes nor acquires child identity/world authority and copies no child
content. This absence of a write is **not proof** that an unknown child's
identity or world has been observed or preserved. A composite may itself
become a child of another composite.

Each directly selected entry MUST have a closed `workspace_bindings` descriptor
binding its entry ID, source metadata digest, optional child RAPPID/world,
verification status and optional evidence reference. Without independently
verified metadata, the status MUST be `preserved-by-reference-unverified`,
with null identity/world/evidence fields. The original metadata remains
external and digest-bound; labels, filenames and asserted identity-shaped
metadata MUST NOT be promoted to proof.

The host-only `register_workspace_binding` path verifies exact finite metadata
bytes against the catalog digest and invokes an independently installed
`verify_workspace_binding(claim, metadata)` hook. Only the literal `True` permits
a controller-owned `workspace-binding` record with
`verification_status:verified-external-binding`. The hook must independently
establish the exact entry/metadata/RAPPID/world association; no native metadata
adapter or signature implementation is manufactured by the reference.
The recorded evidence commits that exact claim, and all source restrictions
remain inherited. Controller ledger membership, schema, assessment, metadata
digest and claim commitment are checked when using or recovering the evidence.
A data-shaped binding frame without that controller record MUST refuse.

Composites MUST commit the complete transitive binding descriptors, count
verified and unverified members, and compute `child_identity_status` and
`child_world_status`. They may report `verified-external-bindings` only when
every member has the matching controller evidence; any unknown member keeps
the aggregate `preserved-by-reference-unverified`. Unconditional preservation
Booleans are not defined. Verified status proves only the scoped metadata
association at verification, not ongoing native preservation, current owner
authorization, migration safety or capability inheritance. Previously emitted
unverified composites remain unverified even if new evidence later arrives;
a new composite ID is needed to express stronger evidence.

Composite IDs are immutable within one controller. Children must already exist
as controller-produced records, so append order plus transitive validation
forms a DAG. Duplicate leaf membership, reused IDs with changed content,
data-shaped composite frames, cycles, depth beyond 32 and more than 10,000
transitive members MUST refuse. Every wrapper propagates all child/catalog
and binding-evidence restrictions and obeys the aggregate traversal budget
in §11. Neither cached validation nor a binding grants source access,
adoption, native rebinding, execution or any other authority.

The intended user experience is outcome-first. A user may ask for an outcome
without naming a repository or path. An outcome-resolution frame binds the
query digest and selected catalog IDs, but its semantic fidelity remains
`unproven` until independently evaluated. It cannot grant source access,
checkout, execution, adoption or any other capability.

A Private Hive subscription is a separate proposal over a verified
organization. Public-source entries may be proposed. Private-source entries
MUST be withheld unless the external owner explicitly approves their exact IDs;
excluded entries remain withheld. The proposal always records
`publication_authorized:false`. Actual NAS/network publication, signing,
catalog mutation and subscriber authorization remain the responsibility of a
separately qualified RAPP Private Hive authority and are disabled in this core.

## 13. Higher mechanisms: explicit gates or refusal

Merge fidelity MUST have a correspondence contract and report comparison
coverage. No shared/compared dimensions means **unmeasured**, with no numeric
perfect-fidelity score. Contradictions and all inputs remain retained.
Invariant-preserving authoritative merge is not implemented; it is disabled.

Reattachment requires complete necessary-context coverage as well as
noncontradiction. Missing reads MUST remain unresolved. It is only a candidate
relationship, never automatic adoption or permission.

O(delta) claims require an unexpired baseline, complete approved scope/
coverage, trustworthy change signals and exclusion of generated outputs.
Expired/missing/incomplete baselines require baseline work, not clean delta
claims. Live monitoring/freshness/anti-entropy proof is unavailable here and
disabled; synthetic planner checks do not certify a live estate.

Migration requires behavior coverage, a coherent complete legacy frontier,
world/identity/path/source/suppression preservation and interruption/recovery
proof. The earlier byte-only migrator does not satisfy those requirements.
Workspace/1 core live migration is disabled before source access. Missing original
spec bytes or native mapping cannot be guessed or solved by re-labeling.

## 14. Blocking conformance and honest completion

The [safety matrix](safety-matrix.json) maps every P0/P1 obligation to an
implemented gate or explicit disabled capability and deterministic negative
vectors. Unproven features MUST remain disabled, not watered down to make a
test green. All tests use synthetic data; no private estate, credential, chat
or live native profile is part of the acceptance run.

Conformance MUST include wrong-validator/pin refusal; cross-guarantee
substitution; authority-shaped data; pre-access authorization; ambient
network/import/credential refusal; propagated rights/restrictions; exact
frontier races/crashes/retries; domain/coverage/negative-read failures;
subject suppression across renditions; zero-overlap merge; context coverage;
root budgets/stop capacity; historical unavailability; stale delta;
partition/fork refusal; disabled migration; inert output; executable
verification-through-consumption; portability/rebinding separation; and
unproven learned-capability refusal. Recursive vectors MUST also cover
default-branch-only catalogs, incomplete/duplicate shards, parent cycles,
incomplete/mixed organization tiles, bucket refinement, no-progress
termination, outcome non-authority, large external indexes, recursive
workspace composition, duplicate/cycle refusal and private Hive withholding.
The P0 hardening vectors additionally block frozen-constructor authorization,
mid-operation expiry, clock rollback after failed transactions, unauthenticated
or revoked activation, synthetic/live substitution, false child identity/world
claims, binding/index/table corruption, and aggregate wide/deep/shared-DAG
work-limit bypasses. They are included in the core conformance runner, not
optional prototype tests.

Completion MUST report each guarantee separately and scan nonzero emitted
canonical RAPP/1 frames. No single conformance verdict authorizes deployment.
The reference provides the authenticated activation gate and synthetic trust
hooks, not a production signer or live estate activation. Independent anchors,
authenticated renewal/rotation, genuine snapshot/native adapters, protected
monotonic hosting and production execution/key-custody qualification remain
distinct deployment gates.
