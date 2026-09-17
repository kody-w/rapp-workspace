---
name: microsol-autobest
description: Plan bounded just-in-time delegation and inert AutoBest crossing for any caller task, or advance the receipt-bound microsol-ceo lifecycle from verified organization state, grants, and budgets. The agent never launches, signs, adopts, or performs effects.
metadata:
  agent-sha256: "827f637c024e3fa1229148e5dcd78230a84ea3214283f899d22603741350f23c"
  tile-schema: "rapp-work-capability-tile/1"
  tile-subject: "exact-agent.py-bytes"
---

# MicroSOL AutoBest

Use this Skill when Brainstem already has a caller-supplied task and needs a
deterministic candidate plan for bounded delegation, when it has inert
deliverable candidates and needs a conservative AutoBest reduction, or when it
must advance the closed `microsol-ceo` organization lifecycle. The core lenses
remain generic: Sol may call them, but they are not Sol managers and contain no
domain, model, organization, or task-specific behavior.

Brainstem supplies all facts:

- a canonical task object and head;
- an immutable root envelope;
- the current reservation requested from that envelope;
- a versioned policy whose integer-basis-point weights sum to `10000`;
- exact current worker or generation observations and receipts;
- optional inert deliverable candidates and their complete provenance.

Use **current observations and receipts only**. Never provide native model
history, private transcripts, personal data, credentials, keys, secret state,
or inferred authority.

## What the agent is

`.github/skills/microsol-autobest/agent.py` is a single-file, standard-library
planner/reducer. Import it directly or let Brainstem expose
`MicrosolAutoBestAgent` / `AutoBestAgent` through `BasicAgent`.

Pure import API:

```python
delegate(request)  # Delegation Lens
cross(request)     # Crossing Lens
run(request)       # delegate plus optional cross
compatibility(request)  # one RAPP/1 compatibility application Frame candidate
compatibility_exhaust(request)  # immutable typed mapping/data exhaust
compatibility_successor(request)  # gated atomic successor Frame candidate
double_hotload(request)  # two-pass Brainstem rehearsal/lock candidate
compile_static_agent(request)  # deterministic durable agent.py package candidate
self_host_repository(request)  # immutable ancestor -> causal successor repository
artifact_bundle(request)  # content-addressed successor program egg
mutation_offer(request)  # complete successor PR/transport projection
mutation_offer_decision(request)  # merge/reject/cherry-pick/re-Lens evidence
meta_evolution(request)  # evaluate one recursive improvement rung
n_lens_search(request)  # bounded fanout/recombination/selection search
translate_hive(request)  # inert repository-snapshot fallback projection
ceo(request)       # microsol-ceo state-machine profile
profile_config(name)
bind_implementation_sha256(exact_file_sha256)
```

The BasicAgent/CLI operation accepts either `ceo` or `microsol-ceo` for that
profile.

The helper `head_record(kind, body)` creates canonical headed records for
`task`, `root_envelope`, `reservation`, `policy`, `receipt`, `observation`, and
`deliverable`, plus the CEO command, organization, grant, event, and state
records and the repository snapshot, adapter resolution, and Hive translation
policy, plus RAPP/1 endpoint and compatibility Lens records.
The same helper heads sanitized learning traces and immutable repository Frames.
`canonical_digest(domain, value)` uses domain-separated SHA-256 over canonical
JSON. `loads_json(text)` additionally detects duplicate fields.

## Ancestor-seed capability Tile contract

`agent.py` is suitable for byte-identical inclusion as an inert
`rapp-work-capability-tile/1` implementation in a canonical RAPP Work ancestor
seed profile:

- it is one standard-library file with no MicroSOL imports, repository lookup,
  filesystem read, environment dependency, clock, network, subprocess, or
  runtime-service requirement;
- optional `agents.basic_agent` / `basic_agent` imports are host adapters only;
  the in-file fallback keeps the capability executable/importable without them;
- the immutable implementation subject is the **exact `agent.py` bytes**;
- an external Tile descriptor/host computes SHA-256 over those bytes and calls
  `bind_implementation_sha256(digest)` or records the equivalent binding;
- the full-file digest is intentionally not embedded inside the file it hashes,
  because that would change the subject bytes. `__manifest__` instead declares
  the required external exact-byte binding contract;
- file presence, import, cataloging, content addressing, or profile availability
  grants no authority and activates nothing;
- only an external host with separately verified authority may activate an
  operation; the authority evidence must fit the RAPP/1 compatibility rules;
- the ancestor implementation is immutable. Changes produce a newly addressed
  successor Tile; state/profile evolution produces successor records and never
  mutates the ancestor bytes.

RAPP/1 is the core compatibility substrate, not the application home for this
capability. AutoBest lives in specific protocol/seed profiles and must fit the
canonical RAPP/1 envelope, hash, signature, stream, ancestry, registration, and
refusal rules. Those rules make profile/seed records interoperable and
verifiable; they do not move AutoBest behavior into `rapp-1`.

`__manifest__` records `capability_id: autobest:generic`,
`capability_home: specific-protocol-and-seed-profiles`, generic implementation
scope, exact-byte SHA-256 binding, external-host-only activation,
successor-only mutation, `rapp1_role: core-compatibility-substrate`, and
`authority_from_presence: false`.

The `microsol-ceo` behavior is the inert `MICROSOL_CEO_PROFILE` /
`PROFILE_CONFIGS` data layer on the same generic `delegate`, `cross`, and `run`
implementation. Selecting or carrying that profile is not activation or a
grant. Parent integration should copy the verified `agent.py` bytes unchanged
and bind their external SHA-256 in the ancestor Tile descriptor.

The exact `agent.py` bytes in this package bind to:

`sha256:827f637c024e3fa1229148e5dcd78230a84ea3214283f899d22603741350f23c`

### Conceptual prior art pin

Conceptual provenance is pinned to
`kody-w/UniversalDataConnectorAI@f2a978b9f85b65b9815b69d99c67e51c56732251`
(`f2a978b`) and these exact blobs:

- `agents/connector_learning_orchestrator.py`
  — `1542986362f27598c224327e1372350d81ead56a`
- `agents/schema_learner_agent.py`
  — `edf4c8bb146c478b77c24f6d1330a07ca79586ba`
- `agents/cx_format_synthesis_agent.py`
  — `548b88840321de0a56af9d0ea78b36a44dcb49bd`
- `agents/data_connector_registry_agent.py`
  — `87c99950029ecae3ccc1c5143c9f45efab1f9127`

Safe concepts map as follows:

- unknown-source analysis -> bounded snapshot and adapter resolution;
- schema learning -> JIT Pass 1 plus typed evidence;
- transform / `agent.py` synthesis -> JIT Pass 2 plus the deterministic static
  compiler;
- testing -> real rehearsal, mutation tests, and correction fixtures;
- registry/reuse -> a signature-required Private Hive handshake catalog
  candidate.

This is conceptual provenance only, **not** a RAPP/1 conformance claim. The
implementation deliberately does not inherit ambient Azure storage/network,
broad exception catches, time/random/MD5 identity, floating confidence,
auto-approval, simulated tests, mutable in-memory sessions, or unqualified
generated code.

### Self-hosting prior-art proof

`self_host_repository` treats the pinned UniversalDataConnectorAI repository as
an immutable `autobest-repository-frame/1` input organism. Brainstem supplies
the exact commit, complete inventory head, Git blob ids/byte counts, and
inventory receipt.

The mutation:

- verifies the four pinned conceptual source blobs exactly;
- keeps the ancestor Frame/commit occurrence immutable and fully recoverable;
- never edits or relabels old agents as RAPP/1-compliant in that ancestor;
- allows the successor to retain, replace, move, remove, add, and reorganize
  every framed code/data file;
- requires one causal mutation record for every ancestor file plus every new
  file, with exact source/target content heads, byte counts, parent refs, and a
  canonical successor inventory;
- selects exactly the safe orchestration/schema/synthesis/test/catalog traits;
- omits every declared mutable or unsafe substrate trait;
- binds mutation intent, locked double-hotload result, Compatibility Frame,
  generated static agent/compiler/runtime pins, metadata, mutation tests, and
  complete lineage;
- emits a new causal successor repository/capability candidate rather than an
  additive-only sidecar.

The successor carries bounded projections for Workspace, Work Organization,
Hive, and Federation profiles. It also requires passed unknown-unknown gates for
inventory closure, unmapped executable surfaces, ambient dependencies, state
migration, privacy, authority boundary, replay, and mutation. A failed or
missing gate refuses.

Every successor also carries two exact lineage views:

- a **forward mutation map** from every ancestor path/content head to
  retained/replaced/moved/removed disposition and any successor path/head;
- a **reverse ancestry map** from every successor path/head to
  inherited/derived/new ancestry, source refs, mutation id, inverse mode, and
  loss class.

In `lossless` mode, retained/moved bytes come from successor content and
replaced/removed bytes require retained inverse deltas. The reducer reconstructs
every ancestor byte hash/length and emits a deterministic reconstruction test
head plus the original inventory head.

In `lossy` mode, unavailable ancestor content remains pinned by source path/head
and explicit loss class. The successor emits loss exhaust, sets round-trip and
direct-mapping claims false, and never pretends missing bytes are recoverable.

The compiled static compatibility agent remains bidirectional within declared
coverage, supporting both source-to-successor and successor-to-source channels.

The successor targets RAPP/1 compatibility, but neither it nor the legacy
repository claims signed conformance or authority before separate local
validation, signing, registration, and adoption.

### Mutation offer / PR transport

`mutation_offer` projects the complete successor generation as inert
pull-request-style transport evidence. The offer pins:

- source organization, ancestor Frame/commit/inventory, and exact parent refs;
- the complete successor inventory/tree and artifact bundle;
- compatibility Frame and generated compatibility-agent pins;
- forward file mutation and reverse ancestry maps;
- trait-level retained/replaced/moved/removed/new map and reverse trait refs;
- independent test, mutant, metadata, and mutation-test heads.

The source organization may explicitly merge the complete offer, reject it,
cherry-pick named traits, or run another double-hotload Lens to construct its
own successor.

`mutation_offer_decision` records that choice under an exact decision receipt.
PR transport and merge/cherry-pick records are adoption evidence only. They do
not grant authority, rewrite the ancestor occurrence, or mutate the source
organization automatically.

Wild adaptations may influence a seed ancestor only through a later, separate,
verified selection or Crossing operation. The mutation offer itself explicitly
grants no direct seed change.

### Recursive meta-evolution ladder

`meta_evolution` evaluates one adjacent improvement rung:

1. wild encounter or typed exhaust -> handshake successor;
2. accumulated handshake outcomes -> source/target Lens agent or static-agent
   compiler successor;
3. proven agent/compiler mutation -> candidate organization-seed trait;
4. aggregated cross-organization evidence -> specific protocol successor.

Every rung requires a distinct immutable candidate Frame, predecessor and
mutation refs, specific proposed changes, scenario corpus, disjoint hidden
holdouts, controlled mutants, canary evidence, at least two distinct independent
verification receipts, rollback to the predecessor, and separate adoption.

Candidate-generated tests never self-certify. Candidate tests must be disjoint
from hidden holdouts and independent tests. Protocol successors additionally
require evidence from at least three source organizations.

Receipt-bound guards cover reward hacking, corpus contamination, echo
amplification, monoculture, catastrophic forgetting, and automatic promotion.
Integer basis-point retention/diversity/holdout/mutant/canary/verification
thresholds must pass. A cleared evaluation only becomes eligible to request a
separate adoption; it is never promoted automatically.

### Bounded N-Lens search

`n_lens_search` fans one immutable ancestor Frame/tree into independently pinned
Lens Dimensions. Each Lens may emit a complete successor candidate or
trait-level candidate with exact parents, receipts, budgets, dependencies,
compatibility tags, unknowns, coverage, holdout, and scenario-relative metrics.

The search can:

- select one complete fittest candidate for the declared use case;
- test compatible trait combinations and recombine selected traits;
- preserve every parent branch and exact trait provenance.

Runaway prevention is explicit: maximum Lenses, input candidates, generated
combinations, cross size, depth, rounds, beam width, Pareto width, and
no-progress rounds; immutable root budgets; compatibility/dependency pruning;
equivalence dedupe; shared-work cost reuse; and stop rules.

Fitness uses integer basis points and is relative to the exact use-case head.
Coverage, hidden holdout performance, knownness/unknowns, robustness, and cost
remain visible. No winner claims universal semantic truth.

Connector mutation traits such as schema learning, transform/agent generation,
registry, and tests can compete or recombine under the same rules. Antifragility
tests retain rejected branches, incompatibility evidence, missing dependencies,
equivalence classes, Pareto front, and no-progress history.

The executable surface accepts exactly one JSON argument and never reads files,
stdin, environment variables, clocks, randomness, network, or subprocesses:

```sh
python3 .github/skills/microsol-autobest/agent.py \
  '{"operation":"delegate","request":{...}}'
```

Every control record is closed and fully explicit. The task `payload` alone is
caller-defined JSON so this can plan any domain. Floats, booleans in integer
fields, malformed heads, missing provenance, unknown control fields, authority-
shaped inputs, oversized collections, stale receipts, unsafe counts, and
over-root reservations refuse.

## Delegation Lens

`delegate` evaluates each worker or generation as its own sovereign Dimension:

1. Verify task, immutable root, reservation, policy, observation, and receipt
   heads and provenance.
2. Apply every hard gate. A failed gate prevents scoring.
3. Compute fitness only from the policy's explicit integer metrics and weights.
4. Proportion the current reservation deterministically, then cap every field
   by the immutable root, current reservation, subject remaining resources, and
   explicit policy caps.
5. Emit a JIT candidate containing task granularity, context bytes, timebox,
   tokens, tool calls, milli-credits, output bytes, checkpoint budget/cadence,
   and `continue`, `split`, or `stop`.
6. Retain exact policy, observation, receipt, reservation, and root bindings.
   Every clamp or stop includes its bound and reason.

The root envelope and current reservation are separate. A successor may bind
the prior candidate and request a larger or smaller reservation under the same
root head. That resizes a preauthorized slice; it never widens the root or
grants authority.

### JIT host loop

Brainstem/host owns the real loop:

`observe -> call delegate -> execute chosen assignment -> emit/verify checkpoint -> observe again -> mutate within root or stop`

The agent performs only the middle calculation. It does not launch a model,
worker, tool, or generation. The same pattern applies to generation branches:
represent each branch as `subject_kind: "generation"` with its own Dimension,
current receipt, remaining resources, and explicit metrics.

## Crossing Lens

`cross` reduces inert deliverable candidates only:

1. Verify complete candidate/component provenance and canonical heads.
2. Apply comparability, coverage, declared conflict/unknown, structural, and
   caller-policy hard gates before any score.
3. Score eligible candidates with integer basis points only.
4. Reuse an identical shared component once.
5. Combine independent components only when they declare the same explicit
   compatibility group.
6. Select atomic or dependency-coupled components from one eligible source as
   a whole.
7. Refuse safety-critical cases, low coverage, incomparability, unresolved
   conflicts/unknowns, and non-substitutable ties.
8. Use deterministic hash tie-break only for explicitly semantically
   substitutable, non-safety-critical atomic candidates.

The result retains every candidate head, parent reference, metric/weight vector,
component selection or omission reason, conflict, and unknown. A refusal never
returns a partial composite that looks adopted.

## `run`

`run` accepts a closed `autobest-run-request/1` object with a required
`delegate` request and an explicit `cross` request or `null`. Both lenses must
bind the same task and policy heads. It returns the two candidate plans and
their heads without executing workers between them.

## RAPP/1 endpoint compatibility Frame

When source and target endpoints both speak RAPP/1, use `compatibility` /
BasicAgent operation `compatibility-frame`. Do not create a bespoke Hive runtime
or a multi-Frame handshake.

Brainstem supplies:

- exact headed source and target endpoint records;
- each endpoint's profile head, capabilities, protocol operations,
  restrictions, and bounds;
- one locked static-transducer artifact recorded as
  `autobest-compatibility-lens/1`, whose mapping weights sum to `10000` and
  whose `hotload_lock_head` binds the rehearsal that produced it.

The active Lens is **Brainstem with a hotloaded `agent.py`**, not the static
mapping artifact. The legacy `...-lens/1` record name identifies the compiled,
locked runtime artifact only.

The dynamic Lens is operation-universal over framed application content. It may
derive any successor code, data, directory/tree shape, composition, deletion,
or reorganization required by caller intent. The declarative field-map format
used by one cheap static compiler is optional output IR, not a normative limit
on Lens mutation.

Canonical RAPP/1 envelope construction, identity, signing, stream placement,
registration, and authority remain host-owned outside Lens mutation.

The reducer emits exactly one inert `compatibility` application Frame candidate.
It binds:

- source endpoint head, profile, capabilities, and source operations;
- target endpoint head, profile, and protocol operations;
- the exact compiled artifact id, version, head, and double-hotload lock;
- per-mapping integer coverage, declared and structural gaps, merged
  restrictions, and bounds;
- aggregate weighted coverage, unmapped target operations, and the conservative
  overall bound.

Mapping bounds must already fit both the source capability and target operation;
the reducer refuses widening instead of silently clamping it. Unknown
capabilities/operations, duplicate target mappings, or weights not totaling
`10000` also refuse.

The Frame candidate has `frame_count: 1`, names generic `socket` and `agent`
consumers, and explicitly says no bespoke runtime is required. Presence or
transport grants no authority. Local deterministic validation and explicit
adoption are required before activation. If adaptation later changes, emit a
successor compatibility Frame; do not turn initial interoperability into a
multi-Frame ceremony.

### Static transducer and successor lifecycle

Handshake learning uses `double_hotload`:

1. **Pass 1 — source/caller-selected hotload.** Brainstem hotloads the selected
   source `agent.py`, binds agent/prompt/policy/input/output receipts, and
   semantically mutates the immutable source Frame into an inert candidate
   payload according to caller intent (`convert`, `edit`, `add`, `compose`, and
   similar intent remain data).
2. **Pass 2 — target/finalizer hotload.** Brainstem hotloads the target
   `agent.py`, consumes the exact Pass-1 output head, performs the final
   target-shaped mutation, and fills/normalizes required contract fields.

The portable reducer does not import or run either hotloaded file. Brainstem
performs both passes and supplies their exact agent, prompt, policy, input,
output, and receipt pins. The signed source remains immutable; the host alone
creates/signs successor Frames.

The two hotloaded agents are **JIT ephemeral intelligence hanging off the
global Brainstem**. A cycle may wake only for:

- an unmatched handshake;
- typed exhaust;
- explicit rehearsal;
- a requested mapping mutation.

After a mapping has locked, a mapping-mutation wake must carry new typed exhaust;
it cannot regenerate the learned agent merely because a caller asks.

Each cycle carries a closed `jit_scope`: exact Frame/exhaust heads, exact policy
heads, one finite shared budget, exactly two passes, and
`persist_native_history: false`. Each pass has its own bounded slice,
transformation receipt, and unload receipt. Missing scope, budget widening,
unload failure, or any request to persist native model session/history refuses.

**File manipulation is the routing plane.** The scope contains one isolated
hotload slot contract. Brainstem atomically places verified regular bytes at the
single filename `agent.py`, hotloads the pass, records placement/input/output/
policy receipts, and unloads before the next placement. Exact byte length,
SHA-256, and `sha256:...` content address are pinned for each pass.

The slot contract requires isolation, regular files, atomic create-new
placement, and unload. It explicitly forbids:

- daemons or permanent processes;
- bespoke plugin registries;
- symlinks;
- overwrite/in-place replacement;
- modification of `brainstem.py`.

Rehearsal/data sloshing repeats the same two passes against bounded fixture and
exhaust heads. Unlocked cycles point to `repeat-double-hotload-rehearsal`.
Locking requires passed schema, invariant, privacy, authority-boundary, replay,
and mutation receipts. A locked result may then compile to the cheap static
transducer below.

### Sanitized learning trace

The live conversation/tool/agent trace is protocol data exhaust and rehearsal
evidence, but raw interaction content is never durable state. Brainstem supplies
an `autobest-sanitized-learning-trace/1` containing a hash-chained sequence:

`intent -> assistant proposal -> user correction -> measured tool/agent result or failure -> superseded assumption -> successor invariant`

Events carry only structured ids, heads, bounded metrics, receipts, and
synthetic correction fixtures. Source commitments distinguish user authority
from assistant proposal and tool/agent measurement. User corrections require a
receipt binding the exact decision; measured outcomes require exact result
receipts.

The trace persists:

- event order and previous-event commitments;
- source commitments;
- proposals, correction decisions, measured status/failure codes;
- superseded assumptions and successor invariants;
- sanitized regression/mutation fixture descriptors.

It never persists raw transcripts, hidden reasoning, local paths, token data,
credentials, native model history, or private payloads. Deterministic validation
refuses summary drift, broken ordering, missing correction/invariant links,
forged user decisions, and privacy-shaped content.

Correction fixtures are embedded in the Compatibility Frame and added to the
generated static agent's mutation suite. They use synthetic data and assert
bounded success or exact refusal behavior, so learned corrections cannot
silently disappear in later compilations.

Each mapping is a pinned **bidirectional static input/output transducer**. It
binds source/target input and output schema heads plus forward and reverse input
and output map heads. Generic socket/agent runtime applies those static pins
deterministically. Normal traffic makes **zero model calls**. JIT intelligence
unloads after learning and stays asleep until a listed trigger reopens the loop.
It does not invoke continuous AI translation.

Approved learned handshakes are portable `agent.py` bytes plus metadata/tests,
bound by a Private Hive receipt. Persist only Frames, exact file/input/output/
policy pins, placement/transformation/unload receipts, rehearsal fixture corpus,
exhaust evidence, and the locked deterministic agent/static mapping. Never
persist native model sessions, private histories, or hidden conversational
context.

Normal translation may hotload the locked deterministic `agent.py` through the
same isolated regular-file slot. It still makes zero model calls. Only new typed
exhaust reopens JIT mutation/regeneration after a mapping has locked.

Runtime continues using the immutable Frame until a typed mapping or data-domain
exhaust is proven. `compatibility_exhaust` requires:

- the exact predecessor Frame and mapping id;
- direction (`source-to-target` or `target-to-source`) and channel
  (`input` or `output`);
- the pinned expected schema, differing actual schema, and data head;
- a runtime receipt binding all exhaust facts.

The resulting exhaust and predecessor remain immutable evidence. No mapping is
changed in place.

Exhaust reopens the double-hotload loop. `compatibility_successor` then takes
the predecessor, exhaust, locked double-hotload result, new source and target
endpoint pins, the newly compiled static-transducer artifact, and one proposal
receipt. It requires exact passed receipts for all six gates:

`schema`, `invariant`, `privacy`, `authority`, `replay`, and `mutation`.

The `authority` gate is validation evidence about the external boundary; it
does not grant authority to the Frame or reducer.

Only then does it deterministically select one successor Frame candidate. The
selection is atomic and singular, but adoption/activation still require the
host's atomic commit. The successor binds predecessor and exhaust heads and
increments its mutation index. Rollback points to the predecessor; learning
points to the immutable exhaust. Failed gates, unchanged pins, unproven exhaust,
or widened bounds refuse. Hidden patches and continuous translation are
forbidden.

### Durable static output compiler

After approval, `compile_static_agent` deterministically emits a complete static
`agent.py` source string from the exact Compatibility Frame plus compiler and
runtime pins. The generated agent embeds:

- the complete locked bidirectional field-map specifications and schema heads;
- coverage, exact gaps, restrictions, and bounds;
- the Compatibility Frame head;
- compiler SHA-256 and runtime head;
- deterministic refusal behavior for unknown mappings, typed exhaust,
  unacknowledged gaps, missing required fields, and input/output bounds.

The source is standard-library-only, self-contained, and performs normal
translation with zero model calls. Its generated manifest explicitly refuses
authority and universal semantic truth beyond declared coverage.

The package candidate also contains:

- exact source bytes, SHA-256, byte count, content address, and Frame-derived
  version;
- compatibility metadata and metadata head;
- deterministic bidirectional mutation vectors and tests head;
- an optional exact generation receipt;
- Private Hive packaging intent without publication or activation.

Recompiling the same Frame/compiler/runtime pins reproduces byte-identical
source. An exact generation receipt may independently verify those bytes.
Changing the Frame changes the generated version and agent hash. Another
Brainstem can reuse the packaged `agent.py` universally only within its declared
coverage; gaps and restrictions remain visible and enforceable.

The compiler supports two qualified modes:

- `deterministic-field-map` compiles the captured static mapping template;
- `captured-agent-bytes` packages arbitrary deterministic Python generated by
  the double-hotload finalizer.

Captured code is not interpreted as trusted merely because it was generated. Its
exact UTF-8 bytes, SHA-256/content address, Compatibility Frame portable-artifact
pin, passed mutation-test receipts, aggregate test receipt, and exact generation
receipt must all match. Syntax is checked but never executed by the portable
compiler. Arbitrary code remains coverage-bounded and makes no universal
semantic truth claim.

### Content-addressed artifact bundle / egg

`artifact_bundle` packages a complete generated successor program, not only one
payload, mapping, or `agent.py`. The bundle may contain arbitrary code, data,
the hotload-entrypoint `agent.py`, schemas, fixtures, tests, documentation,
migrations, and manifests.

Every file binds exact bytes/SHA-256, kind, mutation cause, source Frame or
mutation-manifest parents, and the canonical bundle inventory. The declared
entrypoint must be exactly one regular `agent-entrypoint` file.

Candidate-generated tests are useful artifacts but are explicitly **not**
independent proof. Atomic bundle selection requires:

- separately receipted host tests;
- separately receipted canonical contract tests;
- one or more controlled mutants targeting bundle files;
- proof that independent tests detected every mutant;
- a final selection receipt binding the inventory, independent tests, and
  mutant evidence.

Only then is one bundle candidate selected. Adoption, activation, registration,
and signing remain external. The Private Hive handshake package identifies the
complete bundle and hotload entrypoint; another Brainstem may reuse the
generated program only after local verification and signature.

## Hive translation fallback

If source and target already speak RAPP/1, do **not** use this fallback; use the
single compatibility application Frame above.

Use `translate_hive` / BasicAgent operation `hive-translate` only when
Brainstem has already captured a bounded repository snapshot under separate
host authority and exact native, declared, and inferred adapter resolution
receipts all say `unavailable`.

The portable agent never opens a repository. Brainstem supplies a closed
`autobest-repository-snapshot/1` value containing:

- normalized relative paths;
- exact decoded byte counts and SHA-256 values;
- bounded UTF-8 or base64 content chunks treated only as data;
- a canonical source inventory head;
- separately supplied scope and capture receipts.

The request also pins:

- the externally computed exact `agent.py` SHA and agent receipt;
- an `autobest-hive-translation-policy/1` plus policy receipt;
- exact prompt and model/output heads plus their receipts;
- an `autobest-adapter-resolution/1` receipt proving the fallback condition.

The reducer recomputes content hashes, inventory, bounds, and every receipt
binding, then emits an inert `autobest-hive-translation-candidate/1`. The
fallback creates one opaque source-data Dimension per file, preserves the exact
captured content, reports semantics as unknown, and retains every binding. It
does not infer application meaning, execute repository code, manufacture an
adapter, register a Hive, activate anything, or grant authority.

Before activation, the host must deterministically revalidate exact
implementation bytes, every source hash and inventory entry, all receipts, and
the applicable RAPP/1 envelope/hash/signature/stream/ancestry/registration/
refusal compatibility rules. Registration and activation remain separate host
actions under separate authority.

## `microsol-ceo` profile

Use `ceo` only when Brainstem supplies all of these closed records:

- an arbitrary user command as `microsol-ceo-command/1`;
- separately verified `microsol-ceo-organization/1` static Dimension state;
- a separately verified `microsol-ceo-grant-envelope/1`;
- the immutable AutoBest root envelope and versioned policy;
- the exact prior CEO state and the next exact event/receipt, or `null`/`null`
  for first command intake.

The command text is always **goal data, never authority**. It may contain an
unknown request or words such as “launch,” “deploy,” “grant,” or “unlimited.”
The reducer does not interpret those words as permissions. Only the supplied
grant head, allowed actions, allowed static Dimensions, root limits, grant
limits, current remaining budget, and verified event receipts constrain the
candidate next action.

### Lifecycle

Each call advances at most one receipt-bound transition:

1. **Command intake:** retain the arbitrary text and request mission acceptance.
2. **Mission/acceptance:** require explicit acceptance criteria; select only
   requested, available, static worker Dimensions already named by the grant.
3. **Worker JIT delegation:** consume current observations/receipts and an
   explicit reservation through the generic Delegation Lens.
4. **Checkpoint observation and mutation:** bind the latest delegate plan and
   checkpoints. A successor slice must name its predecessor and remain within
   immutable root, grant, and monotonically non-increasing remaining budgets.
5. **Difference-only parallel work:** stop the shared trunk, retain checkpoint
   parents, and emit only declared differing tasks. Shared work must not repeat.
6. **Crossing Lens / AutoBest:** reduce inert deliverables with the same hard
   gates, complete lineage, and refusal rules as generic `cross`.
7. **Independent verification:** require granted verification Dimensions that
   are distinct from worker Dimensions and bind every verifier receipt.
8. **Decision/refusal:** request a separately receipted `approve` or `refuse`.
   Failed verification permits refusal only; the CEO cannot self-approve.
9. **Handoff/close:** emit verified-ready or refusal handoff request data, then
   close only after a separate handoff receipt.

The phases carried in `microsol-ceo-state/2` are:

`mission_acceptance -> worker_delegation -> checkpoint_observation -> difference_parallel -> independent_verification -> decision -> handoff -> closed`

Checkpoint calls may remain in `checkpoint_observation` while a bounded
successor reservation is mutated. Exact state/event replay is deterministic.
Every successor state preserves prior state heads, event heads, plan heads,
artifact heads, immutable bindings, budget ceilings, and an explicit decision.

### User takeover and fine finishing

The CEO is also the user's verified takeover channel. Its explicit control
modes are:

- **`autonomous`** — normal receipt-driven organization flow;
- **`guided`** — the user supplies direction or preference overrides while the
  reducer keeps assignment detail bounded;
- **`detail`** — the user directly steers a named fine-grained locus.

Brainstem may submit a `user_control` event from any active pre-handoff phase
that carries accepted checkpoint/frame evidence. The event must bind:

- the exact mission id, CEO state head, latest active accepted checkpoint/frame
  head, parent task head, and named locus;
- a new headed user command, which remains goal data;
- only affected already-selected Dimensions;
- `refine`, `compare`, `keep`, or `select`, with target references restricted to
  already accepted evidence;
- explicit successor acceptance criteria, a predecessor-bound reservation, and
  current observations for affected Dimensions.

The reducer creates a new parent-linked successor task, runs the normal
Delegation Lens, enters transient `control_checkpoint`, and emits assignments
only for affected Dimensions. Those Dimensions are marked paused/replaced;
unaffected work is explicitly left to continue. The original mission task,
parent Frames, accepted evidence heads, and complete takeover history remain
unchanged. The new successor becomes `active_task` for later autonomous
delegation/crossing while the original mission remains its immutable ancestor.
If takeover occurs after an earlier crossing or verification, that evidence is
preserved as history but the successor must cross and verify again before a new
decision.

`control_checkpoint_observed` then returns the state deterministically to
`autonomous` `checkpoint_observation`, where affected differences can be
recomputed before any new crossing or decision. The new checkpoint is appended
to accepted evidence; no earlier evidence can be removed. Invalid anchors,
ungranted Dimensions/actions, budget increases, failed hard gates, or attempts
to compare/select unknown evidence refuse rather than weakening the mission.

### Host boundary

Every CEO response contains a `microsol-ceo-next-action/1` request or `null`.
It is bounded request data for Brainstem, not execution. Brainstem/host decides
whether its separately verified authority permits the request, executes
workers/tools elsewhere, emits and verifies receipts/Frames that conform to
RAPP/1 compatibility rules, and returns the next exact event. A missing grant
action, ungranted Dimension, budget
increase, failed verification, crossing refusal, or lineage mismatch remains an
explicit refusal and never becomes a success-shaped fallback.

## Authority boundary and final checks

`__manifest__` follows the repository's private single-file agent conventions,
but it is evidence only. Authority is external; RAPP/1 supplies the core
compatibility substrate. The caller/host:

- chooses whether to execute an assignment;
- enforces the immutable root at execution time;
- emits and verifies actual Frames and receipts under RAPP/1 envelope, hash,
  signature, stream, ancestry, registration, and refusal rules;
- resolves any human or safety review;
- decides adoption through a separately authorized route.

This agent emits candidate JSON data only. It does not read or write a
filesystem, inspect environment state, contact services, use keys, sign Frames,
launch models, spend credits, adopt results, publish, deploy, or perform effects.

Before using a candidate, the host must verify:

- every bound head still matches the exact current object;
- observations/receipts are current and belong to their stated Dimensions;
- no assignment or successor reservation exceeds root, remaining, or policy
  limits;
- hard gates preceded scoring;
- every Crossing selection has complete lineage and no unresolved case;
- every CEO transition binds the exact prior state and current event receipt;
- the CEO grant head and immutable root head are unchanged, selected Dimensions
  are static/granted, and remaining budget never increases;
- every takeover binds an accepted frame/locus, preserves parent tasks and all
  accepted evidence, and changes only explicitly affected Dimensions;
- approval has independent verification plus a separate decision receipt;
- an external host authority check explicitly permits the intended execution or
  adoption, with its evidence conforming to RAPP/1 compatibility rules.
