# RAPP Hive AutoBest/1
## Wild-Hive compatibility, bounded Lens search, and portable successor programs

**Protocol identifier:** `rapp-hive-autobest/1`
**Status:** additive RAPP/1 application profile
**Parent:** canonical `rapp/1`, unchanged
**Required profiles:** `rapp-hive/1` and the locally activated Workspace
capability/controller that qualifies Brainstem hotloading and adoption
**Schema:** [`schema.json`](schema.json)

This profile binds generic Brainstem-invoked AutoBest capability to sovereign
Private Hive collaboration without changing the frozen RAPP/1 envelope or the
existing `rapp-hive/1` contract.

The existing Hive profile remains byte-exact:

```text
rapp-hive/1 SPEC SHA-256
79aeef7bc5000f4a7b09483844b035c66adf817475540e583138f2e6b432c822

rapp-hive/1 schema SHA-256
9b383535d6a2ad379e8c70b1a1cb3ab6ed3f9ca71114c37695e24fd8560415e0
```

An estate adopts this profile through a separate signed RAPP/1 protocol
registry entry. It MUST NOT reinterpret old Hive frames as AutoBest records or
silently replace the Hive/1 profile pin.

The key words **MUST**, **MUST NOT**, **REQUIRED**, **SHOULD**, and **MAY** are
normative.

## 1. RAPP/1 and Hive/1 boundaries

RAPP/1 exclusively owns:

- identity and keyed RAPPIDs;
- canonicalization and hash domains;
- the eleven-key Frame envelope;
- stream sequence, `prev`, and `prev_wave`;
- signatures, eggs, registries, revocation, and migration.

A Lens receives approved application content. It MUST NOT choose or mutate
`spec`, `kind`, `stream_id`, `seq`, `utc`, `payload_hash`, `frame_hash`,
`prev`, `prev_wave`, or `sig`. The host validates a candidate, constructs the
RAPP/1 successor, computes hashes, chooses the predecessor, and signs.

This profile registers four exact application kinds:

| Kind | Payload schema |
|---|---|
| `hive-autobest.compatibility` | `rapp-hive-autobest/1-compatibility` |
| `hive-autobest.exhaust` | `rapp-hive-autobest/1-exhaust` |
| `hive-autobest.mutation-offer` | `rapp-hive-autobest/1-mutation-offer` |
| `hive-autobest.evolution` | `rapp-hive-autobest/1-evolution-proposal` |

These frames live on independently registered body streams. A Private Hive
advertises or converges them through an ordinary `rapp-hive/1-object` whose
typed address is the application Frame wave. No new Mother Hive kind,
convergence rule, signature format, transport endpoint, or authority path is
created.

Shape validation, a package hash, a passing test, a PR merge, a model result, a
catalog entry, or a signed compatibility Frame does not activate code or grant
authority.

## 2. Partial compatibility is valid

When source and target both speak RAPP/1, incomplete application compatibility
is preferable to blanket refusal. Trust failures remain terminal; application
gaps remain explicit.

For each requested capability, negotiation proceeds only as far as necessary:

1. native protocol;
2. declared descriptor;
3. authenticated signed-stream inference;
4. deterministic static repository compiler;
5. bounded Brainstem translation candidate.

Each capability records its method, exact evidence, coverage, and one of:
`verified`, `partial`, `unproven`, `unavailable`, or `revoked`.

Invalid signatures, key substitution, rollback, same-position stream forks,
current revocation, cross-world input, denied capture/model rights, or privacy
failure MUST NOT fall through to a weaker negotiation level. Unknown semantics
remain partial or unproven.

## 3. One Compatibility Frame

Endpoint adaptation is one immutable `compatibility` application Frame. It
binds:

- exact source and target identities, profile pins, heads, snapshots, and
  capability evidence;
- source Lens and target-finalizer `agent.py` bytes;
- the isolated hotload slot contract;
- exact intent and source vector;
- directions, coverage, gaps, restrictions, finite bounds, and loss class;
- the successor program bundle, mutation lineage, sanitized learning trace,
  optional N-Lens search, and independent verification receipts;
- the deterministic static `agent.py` package and generation receipt;
- the exact Hive registry/Mother/catalog checkpoint;
- predecessor and trigger exhaust for a successor;
- `grants_authority:false`, `shared_brain:false`, and no state/key transfer.

An initial Frame has no predecessor or exhaust. A typed-exhaust successor binds
both. Requested mutation and scheduled rehearsal successors bind the exact
predecessor. No field is patched in place.

The selected Frame is an external local-controller pointer. Atomic selection
MUST compare-and-swap the expected active predecessor. A stale candidate
remains inert evidence. Rollback creates a successor selecting a previously
verified mapping; history is not rewound.

## 4. Active Lens: Brainstem plus double hotload

The dynamic Lens is the global Brainstem with two exact hotloaded agents.

### 4.1 Source pass

The source/caller-selected agent consumes the immutable source application
Frame/content, caller intent, target contract, current policy, one inherited
root budget, and exact fixtures or exhaust. It may generate any authorized
successor application shape, including:

- changed records or schemas;
- arbitrary code and data;
- a complete replacement repository tree;
- a new `agent.py`;
- tests, documentation, migrations, and manifests;
- retained, moved, replaced, removed, split, composed, and new material.

The pass emits an inert candidate. It cannot sign, select a predecessor, widen
policy, modify the source Frame, or treat repository text as host instructions.

### 4.2 Target pass

The target-finalizer consumes the exact source-pass candidate and pinned target
contract. It fills and normalizes required fields, retains source refs and
restrictions, rejects unsupported material, and emits a target-shaped inert
candidate.

The target request receipt MUST commit the exact source-pass output. A
different candidate, changed agent, changed prompt/policy, or missing receipt
refuses.

### 4.3 Ephemeral topology

JIT intelligence wakes only for:

- an unmatched handshake;
- typed mapping or data exhaust;
- explicit mapping mutation;
- source/target profile mutation; or
- bounded scheduled rehearsal.

It inherits only exact Frames, policies, tools, and budgets. Native model
sessions, hidden reasoning, caches, provider history, tokens, and local paths
are not protocol state. The agents unload after receipts are recorded.

The protocol records no physical-deletion guarantee. It records that future
operation does not depend on a retained native session.

## 5. File routing and hotload slot

File manipulation is the routing plane. The generic Workspace controller
creates a fresh operation namespace with:

```text
source/agent.py
target/agent.py
locked/agent.py
```

For each placement the host MUST:

1. resolve exact content-addressed bytes;
2. create an absent regular mode-0600 file atomically;
3. reject symlinks, hardlinks, devices, sockets, FIFOs, traversal, and
   overwrite;
4. reopen without following links and verify type, bytes, and SHA-256;
5. capture and hotload those verified bytes rather than later rereading an
   unchecked path;
6. record file/input/output/prompt/policy/runtime/tool receipts;
7. unload and close the slot.

No daemon, permanent per-Hive process, mutable plugin registry, symlink route,
or `brainstem.py` modification is defined.

Repository presence, a filename, an egg signature, or Hive convergence never
authorizes hotloading. Local controller validation and adoption are required.

## 6. Durable successor program

Successful rehearsal emits a self-contained static output `agent.py` inside a
content-addressed RAPP/1 egg or equivalent typed bundle. The bundle may contain
arbitrary new code, schemas, fixtures, candidate tests, documentation,
migrations, data, and manifests.

The hotload entrypoint is exactly `agent.py`. Documentation remains data.
Migrations remain inert until separately authorized.

The static agent embeds or pins:

- the Compatibility Frame hash;
- source and target profiles/contracts;
- forward and reverse behavior;
- coverage, gaps, restrictions, and bounds;
- compiler/runtime pins;
- deterministic refusal and typed-exhaust behavior.

Normal covered traffic hotloads the static agent with zero model calls. Its
implementation is not restricted to a small mapping IR, but every code and
dependency byte MUST be captured and qualified. It returns an application
candidate; the host still owns RAPP/1 construction and signing.

Changed Compatibility Frame, compiler, runtime, code, contract, or test result
creates a new agent hash/version. Deterministic generation SHOULD reproduce
exact bytes. Otherwise an exact generation receipt MUST bind every input and
the output bytes without claiming reproduction it did not prove.

## 7. Independent verification

Candidate-generated tests cannot certify their generator. Before selection,
the exact bundle MUST pass:

1. candidate tests;
2. separately selected host tests;
3. exact canonical protocol conformance;
4. host-controlled mutants;
5. deterministic replay where claimed;
6. privacy and authority checks;
7. current revocation/fork/rollback checks.

Mutation evidence records exact integer counts. Mandatory surviving or untested
mutants refuse. Controlled mutants cover schema changes, swapped directions,
boundary errors, changed pins, gap suppression, false authority, privacy
leakage, envelope injection, path escape, nondeterminism, and success-shaped
fallback.

## 8. Bidirectional mutation lineage

Immutability protects every ancestor occurrence, not the successor file
layout. A successor may replace every input path and byte.

The `mutation-lineage` particle carries:

- source and successor generation/frame/inventory refs;
- one forward disposition for every source path/content head;
- one reverse origin for every successor path/content head;
- selected and omitted traits;
- exact coverage counts;
- `exact-lossless`, `declared-lossy`, or `unproven`;
- inverse implementation/deltas and independent reconstruction receipt.

Forward dispositions are `retained`, `replaced`, `moved`,
`moved-and-replaced`, `removed`, `split`, or `composed`. Reverse origins are
`inherited`, `derived`, `new`, `split`, or `composed`.

No source or successor entry may be silently unmapped. Moves are explicit, not
heuristic rename detection.

An exact-lossless claim requires reconstruction of every ancestor path, mode,
byte, content address, and inventory from the successor plus retained deltas.
Private inverse bytes remain sealed GODD and require retention rights. If
required inverse data cannot be retained, the mapping is lossy or unproven.
Unavailable reverse material emits typed exhaust and cannot claim round-trip
compatibility.

## 9. Sanitized learning trace

Conversation/tool/agent history is protocol data exhaust only after
sanitization. The trace stores ordered structured events:

```text
intent
proposal
user correction
measured tool/agent result or failure
superseded assumption
successor invariant
```

Events bind order, source/evidence refs, actor class, and authority class.
Assistant proposals never become user decisions. Text asserting that the user
approved is not an approval receipt.

The trace has no raw transcript, prompt, hidden reasoning, tool body, token
count, local path, credential, key, or private payload field. It defaults to
sealed GODD.

Every correction identifies the superseded event and successor invariant and
enters the regression/mutation corpus. A locked successor requires complete
correction coverage. Summaries are non-normative and bind the canonical trace
root; omission, reorder, duplication, or contradiction is summary drift.

## 10. Bounded N-Lens search

One immutable ancestor may fan into independently pinned Lens Dimensions.
Each Lens may emit a complete successor, trait delta, refusal, or unknown.
Compatible candidates may cross; the controller may select one complete
candidate, recombine traits, retain a bounded Pareto set, or stop unresolved.

The root owns all maxima: Lens count, candidate count, cross width, depth,
rounds, evaluations, generated bytes, tools, beam width, Pareto width, and
reserved stop Frames. Children, renamed agents, crosses, and retries cannot
reset them.

Before crossing, prune missing/cyclic dependencies, incompatible contracts,
worlds, audiences, rights, loss requirements, and mutation conflicts.
Byte-identical equivalent outputs are evaluated once while all occurrences
retain provenance. Shared immutable observation, parsing, fixtures, and tests
execute once; hidden model state is never shared.

Fitness is relative to one declared scenario/corpus/holdout and exact coverage.
No score establishes universal truth. Incomparable coverage is not silently
collapsed into one winner.

Repeated state, no new non-equivalent candidate, no measured improvement,
incompatibility, holdout/mutant failure, or any exhausted root bound emits a
stop/unresolved record.

### 10.1 JIT assignments, checkpoints, AutoBest decisions, and views

The immutable Compatibility Frame is the root envelope. JIT work changes only
through successor `assignment` records. An initial assignment has revision
zero and no predecessor; every mutation binds the prior assignment and a
positive revision. `assign`, `tighten`, `pause`, `resume`, `cancel`, `complete`
and `prune` are requests to the external Workspace controller.

Every assignment binds one worker Dimension, work group, branch, exact
Workspace assignment wave and source vector. `constraint_relation` is
`equal-or-tighter`; Hive data cannot widen root scope, rights or budgets.
Assignments carry `request_only:true`, `authorizes_execution:false` and
`grants_authority:false`.

Worker `checkpoint` records bind the exact assignment, predecessor checkpoint,
Workspace observation/checkpoint receipts, outputs and source vector. They are
historical evidence, not reusable authorization.

An AutoBest `decision` binds independent evidence, complete parent vectors,
selected/rejected checkpoint waves, coverage, optional Crossing Lens and
result checkpoint. Composed results require at least two exact parents and a
Crossing Lens. `unresolved` cannot silently choose a winner. Every decision
records `authorizes_adoption:false`.

Board and chat `view` particles bind the current Hive checkpoint, exact source
vector, artifact and reference-only trunk/difference/rejoin topology. They
store omissions and remain `rebuildable:true`, `authoritative:false` and
`grants_authority:false`. Raw private chat content is not required by the view
contract and remains sealed when retained.

## 11. Mutation-offer PR projection

A complete successor may be projected into Git as a mutation offer carrying:

- exact source parent Frames/commit/tree/inventory;
- complete successor Frame/tree/bundle;
- forward and reverse lineage;
- selected/omitted traits;
- static compatibility agent;
- generated and independent verification.

The PR projection binds exact base/head commits and inventories. PR IDs and
URLs are transport metadata, not identity. Force-push or changed head
invalidates the projection receipt.

The receiving organization may merge the complete candidate, reject it,
select exact traits, or run another Lens. Git merge/cherry-pick is transport
and review evidence only. It does not authorize adoption, rewrite RAPP
ancestry, or mutate an ancestor seed.

A wild trait influences a seed only through a separate verified selection or
Crossing Lens with new identity, tests, canary, and adoption.

## 12. Recursive evolution

Evolution is explicitly layered:

1. exhaust evolves a handshake;
2. accumulated outcomes may evolve source/target Lens agents or the static
   compiler;
3. proven toolchain mutations may become organization-seed trait candidates;
4. deduplicated cross-organization evidence may propose a versioned protocol
   successor.

Every level uses immutable parents, exact causal evidence, a scenario corpus,
protected hidden holdout, host-controlled mutants, prior-version regression,
bounded canary, independent verifier, rollback, and separate adoption.

Generated tests cannot self-certify. Generator and independent verifier pins
must differ. Passing one level cannot automatically promote upward.

Metrics and invariants are fixed before generation. The profile preserves
evidence diversity and blocks reward hacking, holdout contamination, repeated
self-evidence, echo amplification, monoculture, catastrophic forgetting, and
aggregate scores that hide invariant regressions.

Protocol evolution creates a new immutable profile/version and migration rule;
it never patches an adopted profile in place.

## 13. Hive carriage, privacy, and authority

Worker Dimensions remain sovereign streams with exact source vectors. Shared
work grouping deduplicates identical work; temporary difference branches retain
their own identities and histories. Crossing Lens results reference every
parent.

Hive stores only approved Frames, packages, receipts, catalogs, projections,
and sealed evidence. It is not a shared model, memory, planner, authority, or
key store.

The following MUST NOT transfer:

- private/signing keys or DEKs;
- credentials or environment;
- native model sessions, hidden reasoning, or caches;
- unrelated local state;
- raw private rehearsal corpus;
- unapproved prompts or endpoint secrets.

Hashes and lineage are sensitive GODD by default. Live packages and traces use
sealed-room protection unless independently sanitized and approved.

Registry tombstones stop future signed use at their effective time. Historical
evidence remains historical. A same-stream fork is quarantined by Hive/1 and
cannot be cleared by an ordinary reconciliation or AutoBest decision.

Catalog, board, and chat views are deterministic non-authoritative projections.
They expose exact source vectors, branches, gaps, omissions, and stale/forked/
revoked states. Rebuilding a projection never rebuilds permission.

## 14. First wild-handshake fixture

The checked fixture pins the private SoftwareCo V-team Hive encounter:

```text
handshake
0c52264b81bf88dd8555defa9363a23d8eb8ef85c3c12f66ddcaaabfc85a8882

source Lens agent.py
679fff9531c0c8b13457d594f746c45da28925a7c1be40473e8ca00823db8671

target finalizer agent.py
c056339f90fdd4e604dbefa40291f1b7b22946d26749b36230bb3b29dd8e2296
```

The source qualification observed two signed RAPP/1 Frames and nine verified
artifacts. The fixture also retains the locally generated signed compatibility
Frame and static-agent proof. It is private conformance evidence, not estate
activation, membership, publication authority, or a claim that the source
implements native Hive/1.

The upstream `UniversalDataConnectorAI@f2a978b9f85b65b9815b69d99c67e51c56732251`
is conceptual provenance only. Its learning pipeline is retained; its ambient
storage/network, mutable sessions, time/MD5 identity, floating confidence,
auto-approval, simulated tests, broad success-shaped fallback, and unqualified
generated code are excluded.

## 15. Compatibility and migration

Existing Hive/1 implementations remain conformant and may retain these
application waves as generic objects without understanding AutoBest semantics.
Extension-aware consumers validate the exact profile pin and records.

An old handshake remains historical. A changed matcher, Frame, agent, package,
compiler, runtime, coverage, or policy produces a new immutable version. It
MUST NOT reuse an ID with changed bytes.

Missing historical evaluator bytes may leave integrity inspectable while fresh
semantic replay is unavailable. That state is explicit, not false and not a
renewed grant.

The generic CEO agent is outside this profile and remains independently pinned
by the Workspace/Work-Organization layer. Its absence does not weaken or
silently populate any Hive capability.

## 16. Conformance

Conformance requires:

```sh
PYTHONDONTWRITEBYTECODE=1 \
  python3 protocols/rapp-hive-autobest/1/reference/schema_source.py --check

PYTHONDONTWRITEBYTECODE=1 \
  python3 protocols/rapp-hive-autobest/1/reference/conformance.py

PYTHONDONTWRITEBYTECODE=1 \
  python3 protocols/rapp-hive/1/reference/hive_conformance.py
```

The profile suite validates all closed schemas, exact pins, the signed Bill
fixture, double-hotload chaining, zero-model static reuse, unchanged RAPP/1
envelope semantics, partial capability operation, exact lineage, correction
coverage, N-Lens bounds, independent evolution verification, and controlled
negative mutations.

Passing conformance does not create an estate registry entry, current owner
approval, production key custody, a qualified model/runtime, or deployment.
