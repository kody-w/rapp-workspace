# RAPP Federation AutoBest / 1
## Wild-handshake compatibility, double-hotload learning, and static fallback

**Protocol identifier:** `rapp-federation-autobest/1`
**Status:** Optional normative candidate; not estate-activated
**Parent:** canonical RAPP/1
**Carrier:** signed RAPP/1 `memory.save` Frames
**Schema:** [`schema.json`](schema.json)
**Bindings:** [`bindings.json`](bindings.json)
**Reference:** [`reference/`](reference/)

This profile adds an optional compatibility layer for sovereign RAPP/1
applications that do not share the same Hive, Workspace, organization, schema,
endpoint, or implementation profile. It does not amend RAPP/1,
`rapp-workspace/1`, `rapp-hive/1`, or `rapp-federation/1`.

The existing closed profile bytes remain independently pinned. An estate
registers this profile separately or treats its records as inert application
data.

The checked-in first wild-handshake package is approved private fixture
material. The generic CEO agent remains unpinned, so dynamic successor mutation
is disabled. Static validation, double-hotload reproduction, partial
compatibility, deterministic static-agent generation, exhaust schemas, package
lineage, mutation offers, and conformance are implemented.

## 1. RAPP/1 boundary

Every normative compatibility or exhaust record is carried by one exact
eleven-key RAPP/1 Frame:

```text
spec kind stream_id seq utc payload payload_hash frame_hash prev prev_wave sig
```

The carrier kind is `memory.save`. The payload is closed:

```json
{
  "profile": "rapp-federation-autobest/1",
  "operation": "compatibility | compatibility-exhaust",
  "record": {}
}
```

RAPP/1 owns canonicalization, particle and wave hashing, signatures, stream
identity, predecessor semantics, registry authority, eggs, and `/chat`.
Compatibility Lenses never mutate those envelope fields.

The host:

1. verifies the immutable source Frame and current authority;
2. supplies only approved application content to a Lens;
3. validates the candidate against the target contract;
4. constructs and signs a fresh successor Frame.

A Lens cannot choose the signer, stream, sequence, predecessor, hashes,
signature, registry, or authority.

## 2. No in-place Federation/1 extension

`rapp-federation/1` is a closed thirteen-kind profile with exact SPEC and schema
pins. This profile therefore does not add fields or kinds to Federation/1.

Federation/1 may carry a compatibility package as an exact sealed resource
through existing `proposal.submit`, `godd.exchange`, or separately authorized
`task.execute` operations. Receipt or completion authorizes only the scoped
federation operation. It does not adopt or activate a compatibility mapping.

Different Hive endpoints are transport locators, not identity. Compatibility
binds exact RAPPIDs, worlds, heads, profile pins, capabilities, and artifact
addresses. Endpoint changes do not rewrite those identities.

## 3. Capability negotiation ladder

For each required capability, consumers attempt:

1. native registered protocol support;
2. an exact declared descriptor;
3. deterministic inference from verified signed-stream coverage;
4. a pinned static repository compiler over an authorized immutable snapshot;
5. a bounded Brainstem translation candidate.

The first sufficient tier may be used for that capability. Different
capabilities may resolve at different tiers. Unknowns remain `partial`,
`unavailable`, or `unproven`; they never become implicit support.

Invalid signatures, key substitution, rollback, stream forks, revocation,
privacy denial, or scope violations are terminal. Those failures cannot be
laundered through a lower tier.

## 4. Compatibility Frame

One compatibility Frame binds:

- exact source repository cut, RAPPID, stream, qualification head, profile, and
  capability evidence;
- exact target profile and operations;
- Workspace, Hive, and Federation pins;
- source-Lens and target-finalizer `agent.py` bytes;
- generic CEO agent status;
- double-hotload receipts;
- mapping commitment;
- per-capability tier, status, and integer coverage;
- known gaps and unknowns;
- privacy, authority, access, and effect restrictions;
- finite runtime and N-Lens search bounds;
- deterministic static-output contract;
- sanitized learning-trace and search artifacts;
- predecessor and triggering exhaust for a successor;
- `grants_authority:false`.

The current first fixture has a pending generic CEO agent. A pending pin cannot
generate, select, or activate a dynamic successor. It does not block the
already qualified static handshake.

## 5. Double-hotload Lens

The active semantic Lens is global Brainstem plus two ephemeral hotloads.

### 5.1 Pass one: source mutation

Brainstem hotloads exact source/caller-selected `agent.py` bytes. It receives
the immutable framed application content, caller intent, source evidence,
target contract, policy, budget, and approved fixtures or exhaust.

The Lens is operation-universal. It may propose any authorized successor code,
data, repository tree, schema, agent, test, documentation, migration, or
organization shape. It does not edit or resign the source Frame.

### 5.2 Pass two: target finalization

A fresh hotload receives the exact pass-one candidate and the pinned target
contract. It may normalize fields, reorganize content, fill required target
data, or refuse. The candidate is still inert.

The pass-one candidate is the only cross-pass state. Native model sessions,
hidden reasoning, provider history, ambient memory, and credentials are not
protocol state.

### 5.3 File routing

Verified regular files are the routing plane. The host uses fresh isolated
slots, create-only atomic placement, no-follow verification, exact byte-count
and SHA-256 checks, bounded execution, and mandatory unload.

The host refuses:

- overwrite;
- symlink or hardlink;
- device, socket, or FIFO;
- path traversal;
- byte substitution between verification and load;
- permanent daemons or plugin registries;
- `brainstem.py` modification.

Repository and Frame content is data, never higher-priority instructions.

## 6. Rehearsal and static output

Double-hotload rehearsal runs approved fixtures and typed exhaust through both
passes under one root budget. Candidate-generated tests are not independent
proof.

Selection requires:

- candidate tests;
- independently maintained host tests;
- canonical RAPP/1 checks;
- controlled mutants;
- privacy and authority gates;
- declared scenario and coverage thresholds;
- no critical surviving mutant;
- owner and host activation.

The successful compiler deterministically emits a self-contained static
`agent.py`. It embeds or pins:

- Compatibility Frame hash;
- source and target profiles and schemas;
- bidirectional implementation;
- coverage, gaps, restrictions, and bounds;
- compiler and runtime commitments;
- stable refusal behavior;
- zero model calls;
- zero authority and effect grants.

The Compatibility Frame contains the output contract, not the final file hash,
avoiding a hash cycle. A generation receipt binds exact Frame, compiler,
runtime, generated bytes, tests, and controlled mutants.

Changed Frame, compiler, runtime, or generation configuration creates a new
agent version and content address. No generated file is overwritten in place.

## 7. Static runtime and typed exhaust

Normal traffic may hotload the locked deterministic agent. Hotloading the
static file is not JIT semantic intelligence:

- no model call;
- no native model session;
- no ambient discovery;
- no authority;
- no external effect.

Unsupported operation, field, enum, schema, locus, or capability emits a typed,
privacy-safe exhaust. Runtime does not improvise.

A successor mapping requires:

```text
previous Compatibility Frame
+ exact exhaust
+ current source and target pins
+ approved evidence
+ source and target agents
+ Brainstem/prompt/policy/model receipts
```

Selection is an atomic compare-and-swap against the active compatibility head.
A stale or failed candidate remains inert. Rollback is a new successor
selecting previously verified material; history is not rewound.

## 8. Artifact bundles and mutation lineage

A Lens may emit a complete content-addressed artifact bundle or egg containing
arbitrary bounded regular files:

- `agent.py`;
- code and data;
- schemas;
- fixtures;
- candidate and host tests;
- documentation;
- migration assets;
- manifests and receipts.

The manifest lists every byte. It rejects path escape, duplicate or
case-colliding paths, symlinks, hardlinks, and special files.

Immutability protects ancestor occurrences, not successor file contents. A
successor may replace every file. Exact forward and reverse lineage is
mandatory:

- every source occurrence is `retained`, `replaced`, `moved`, or `removed`;
- every successor occurrence is `inherited`, `derived`, or `new`;
- one-to-many and many-to-one ancestry lists every source;
- selected and omitted traits are explicit;
- every mapping declares a loss class.

Lossless claims require exact ancestor reconstruction from successor plus
retained inverse material. Lossy or partial mappings preserve unavailable
source references and refuse unsupported reverse operations.

## 9. Learning trace

Live conversation, tools, agents, and failures produce sanitized structured
protocol evidence, not raw transcripts.

Trace events are contiguous and hash-chained:

```text
intent
assistant-proposal
user-correction
measured-result
measured-failure
assumption-superseded
successor-invariant
```

Authority classes distinguish user direction, host policy, assistant proposal,
measured evidence, and derived invariant. Assistant proposals, silence, or
successful output cannot become user decisions.

The trace excludes raw prompts, hidden reasoning, native model history, local
paths, credentials, tokens, and private payloads. Correction cases become
regression and mutation fixtures. A successor invariant must close every
relevant user correction and superseded assumption.

## 10. N-Lens bounded search

One immutable ancestor may fan out through independently pinned Lens
Dimensions. Each may emit a complete successor, trait candidate, alternative
interpretation, refusal, or unknown.

Compatible candidates may be crossed only after dependency, authority,
privacy, and incompatibility pruning. Equivalent results are content-deduped
without losing occurrence provenance. Identical safe work may be reused.

The profile hard ceilings are:

| Bound | Ceiling |
|---|---:|
| Lenses | 32 |
| Candidates | 256 |
| Traits per cross | 8 |
| Cross depth | 8 |
| Rounds | 16 |
| Beam width | 32 |
| Pareto frontier | 32 |

Root budgets are transitive and cannot be reset by children. Repeated-state,
no-progress, budget exhaustion, user stop, or no-compatible-cross terminates
the search.

Fitness is a scenario-relative integer vector containing coverage, holdouts,
mutants, regressions, unknowns, restrictions, reversibility, cost, and canary
outcomes. It is not universal truth.

## 11. Mutation offers and pull requests

A complete successor may be projected through a pull request or other
transport as a mutation offer. The offer binds exact parents, successor bundle,
lineage, tests, Compatibility Frame, static agent, and limitations.

The source organization may:

- merge the complete candidate;
- reject it;
- cherry-pick exact traits into a new successor;
- run another Lens;
- combine it with another parent.

PR and merge metadata is transport or adoption evidence. It never rewrites the
ancestor, signs a successor, advances an active root, or establishes semantic
acceptance.

A wild descendant may influence an organization seed or protocol only through
a separate verified selection/crossing and separate adoption.

## 12. Meta-evolution

Verified evidence may propose, but never automatically perform:

```text
wild exhaust
-> handshake successor
-> source/target agent or compiler successor
-> organization-seed trait candidate
-> versioned protocol-successor proposal
```

Every level retains immutable predecessors, causal evidence, scenario corpus,
hidden holdouts, controlled mutants, canary, rollback target, and a separate
adopter.

Controls prevent reward hacking, corpus contamination, echo amplification,
monoculture, catastrophic forgetting, and automatic upward promotion.
Generated tests cannot self-certify.

## 13. Private Hive and Federation use

Private Hives may catalog compatibility packages as inert content-addressed
objects or sealed GODD. Receiving a package does not install or activate it.

Each subscriber independently verifies catalog authority, package bytes,
matcher specificity, profile pins, agents, rehearsal, mutation evidence,
current policy, and privacy.

Federation exchange remains bilateral and nondelegable. A reverse response
requires its own exact authorization. No central shared brain, global owner,
global head, or transitive Hive access is created.

## 14. Replay, fork, rollback, and revocation

Compatibility streams remain normal RAPP/1 streams:

- identical replay is idempotent;
- changed bytes at the same sequence are a fork;
- lower sequence or predecessor substitution is rollback;
- same profile ID with changed bytes is substitution;
- revoked agent, profile, key, source, or package cannot authorize new use;
- accepted history remains evidence;
- revocation cannot recall already disclosed plaintext or undo external
  effects.

Dynamic attempts record intent before execution. A crash or uncertainty leaves
the attempt in doubt and the predecessor active. It does not authorize an
automatic retry.

## 15. First wild-handshake fixture

The checked-in fixture binds:

```text
handshake profile SHA-256:
  0c52264b81bf88dd8555defa9363a23d8eb8ef85c3c12f66ddcaaabfc85a8882
source Lens agent.py:
  679fff9531c0c8b13457d594f746c45da28925a7c1be40473e8ca00823db8671
target finalizer agent.py:
  c056339f90fdd4e604dbefa40291f1b7b22946d26749b36230bb3b29dd8e2296
source commit:
  f66da3d879b53a439bc87de764d79f68ceec048a
```

Parent-supplied live qualification reports two verified signed Frames, nine
verified artifacts, and a passing fresh compatibility/static-agent proof. Raw
private source bytes are not included. The checked-in conformance fixture uses
public synthetic keys and data and independently proves the profile mechanics.

The safe result is partial read-only compatibility. Membership, board, post,
revocation, key rotation, encryption, and hosted delivery remain unavailable.

## 16. Conceptual prior art

`kody-w/UniversalDataConnectorAI` at
`f2a978b9f85b65b9815b69d99c67e51c56732251` is conceptual provenance only.

The profile preserves its high-level unknown-source analysis, schema learning,
transformation synthesis, generated connector, testing, and catalog pipeline.
It does not import or trust its Azure storage/network coupling, mutable
sessions, broad catches, time/MD5 identity, floating confidence,
auto-approval, simulated tests, or unqualified generated code.

The upstream repository is not RAPP/1 conformance evidence.

## 17. Conformance and blockers

Run:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 reference/schema_source.py --check
PYTHONDONTWRITEBYTECODE=1 python3 reference/vectors.py --check
PYTHONDONTWRITEBYTECODE=1 python3 reference/conformance.py \
  --report conformance-results.json
```

The suite verifies nonzero signed RAPP/1 Frames, exact supplied pins,
double-hotload reproduction, partial capability reporting, static-agent
generation and bidirectional use, artifact lineage, sanitized corrections,
bounded N-Lens search, mutation offers, privacy, replay/fork/rollback
refusals, and unchanged closed sibling profiles.

Passing conformance does not activate an estate, prove universal semantics,
grant Hive membership, authorize effects, or qualify the missing generic CEO
agent. Dynamic successor mutation remains blocked until that exact agent and
its policy/runtime pins are installed.
