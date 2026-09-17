# RAPP Work Organization/1

**Protocol identifier:** `rapp-work-organization/1`

**Status:** normative candidate; profile-independent reference implemented;
generic CEO agent pin and estate activation pending.

**Parent:** canonical RAPP/1, unchanged.

**Conformance class:** `single-host-locked-handshake`.

MUST, MUST NOT, REQUIRED, SHOULD, and MAY are normative.

## 1. Boundary

RAPP Work Organization/1 defines host-mediated organization behavior above
RAPP/1. It does not redefine identity, canonicalization, particles, waves,
signatures, streams, eggs, registries, or the exact eleven-key Frame:

```text
spec kind stream_id seq utc payload payload_hash frame_hash prev prev_wave sig
```

The global RAPP Brainstem is the runtime host. Global describes a shared host
substrate, not a universal owner, signing key, organization root, or consensus
authority. Brainstem itself is not modified.

The host owns current authority, trusted time, budgets, model/tool access,
interrupts, atomic placement, successor construction, hashing, and signing.
Agents, Lenses, mappings, traces, tests, receipts, catalogs, and offers are
requests or evidence. They MUST carry `grants_authority:false`.

## 2. Registered records

An adopting estate registers these exact kinds:

```text
organization.declaration
organization.agent
organization.placement
organization.lens
organization.mutation
organization.rehearsal
organization.exhaust
organization.compatibility
organization.compilation
organization.artifact
organization.execution
organization.catalog
organization.trace
organization.command
organization.work
organization.search
organization.candidate
organization.cross
organization.selection
organization.evolution
organization.evaluation
organization.promotion
organization.rollback
organization.offer
organization.decision
organization.subscription
organization.control
organization.checkpoint
```

Every record remains a normal signed RAPP/1 Frame. Multi-parent ancestry lives
in payload references and never changes `prev` or `prev_wave`.

## 3. Operation-universal double-hotload Lens

The dynamic Lens is operation-universal over authorized framed application
content. It may generate any successor code, data, repository tree, schema,
fixture, test, documentation, migration, or application payload required by
caller intent.

The two hotload phases are structural:

1. A source Lens consumes exact immutable source Frames/content and emits an
   inert candidate successor plus causal mutation evidence.
2. A target/finalizer Lens consumes that exact candidate and emits the target
   contract candidate.

The Lens MUST NOT edit accepted source Frames, choose canonical envelope
fields, sign a Frame, obtain a signing key, widen policy, or treat
envelope-shaped output as authority. The host validates candidate content and
alone constructs/signs the successor Frame.

Safety comes from immutable ancestor references, exact input/model/tool/agent/
policy receipts, current authority, finite budgets, target contracts,
privacy, independent tests, typed exhaust, and host-owned construction. It
does not come from a closed rename/select/convert instruction language.

## 4. Verified atomic artifact placement

The host resolves exact content-addressed bytes, stages a complete bundle in a
new host-owned directory, rejects path escape/symlink/special-file/overwrite
conditions, verifies every SHA-256 and byte count, fsyncs content, atomically
installs the digest-addressed directory, reopens the files, and hotloads the
captured `agent.py` entrypoint.

A path hash followed by a later unchecked read is insufficient. Bundle
substitution, partial placement, ambient module lookup, and route races MUST
refuse. Existing identical placements MAY replay idempotently.

## 5. Ancestor immutability and arbitrary successors

Immutability protects the ancestor occurrence, not successor file contents.
A successor may retain, rewrite, replace, move, remove, split, combine,
reorganize, or add every application file.

Every source entry is classified as retained, replaced, moved, or removed.
Every successor entry is inherited, derived, or new. The forward mutation map
and reverse ancestry map MUST account for the complete source and successor
inventories with no duplicate or orphan entries.

The ancestor bytes and Frame remain independently recoverable. In-place
mutation of the only recoverable ancestor copy MUST refuse.

## 6. Bidirectional lineage and loss

Each generation declares:

```text
bidirectional-lossless
bidirectional-partial
forward-only-lossy
```

Lossless claims require exact reconstruction of the ancestor inventory and
bytes from the successor plus retained inverse material. Paths, modes, byte
counts, SHA-256 values, and aggregate inventory commitments MUST reproduce.

Lossy mappings preserve exact unavailable source references and classify the
loss as content, metadata, semantic, dependency, privacy, or noninvertible
loss. They MUST emit typed exhaust outside reverse coverage and MUST NOT claim
direct round trip.

Static runtime exposes both `source_to_successor` and `successor_to_source`
within the declared coverage.

## 7. Compatibility Frame and rehearsal

The locked handshake is one `organization.compatibility` Frame binding:

- exact source and target profile/schema/inventory/parent pins;
- source and finalizer agent pins and hotload receipts;
- static bidirectional contract;
- forward and reverse lineage commitments;
- policy and activation;
- learning-trace closure;
- coverage, gaps, unknowns, restrictions, and bounds;
- canonical, holdout, mutation, reconstruction, and canary receipts;
- predecessor compatibility and triggering exhaust; and
- zero-model locked runtime.

Rehearsal performs bounded source mutation, target finalization, target
validation, reverse checks, controlled mutants, and stable cold replays.
Passing a corpus proves only the declared coverage.

Typed exhaust records exact active pins, direction, operation, input/output
references, coverage, loss, invariant failure, restrictions, consumed bounds,
and retryability without raw private payloads or inferred patches.

## 8. Static artifact bundle

A successful lock MUST deterministically produce a content-addressed RAPP/1
egg containing a complete successor program. The bundle MAY contain arbitrary
code, `agent.py`, modules, schemas, fixtures, candidate tests, documentation,
migrations, manifests, and compatibility metadata.

`agent.py` is the exact Brainstem hotload entrypoint. It embeds or pins the
Compatibility Frame, bundle manifest, contracts, coverage/gaps, restrictions,
bounds, compiler/runtime, and refusal behavior. It MAY implement arbitrary
deterministic code and import only exact files in the verified bundle.

Changed Compatibility Frame, program, compiler, runtime, template, or bundle
creates a new hash and generation.

The receiving host either reproduces exact bytes from the pinned compiler or
authenticates the exact generation receipt. Claimed equivalence cannot replace
byte identity.

## 9. Independent proof

Candidate-generated tests are supplemental evidence and MUST NOT certify their
generator. Selection requires externally selected canonical tests, evaluator
holdouts, controlled mutants, privacy/security negatives, reconstruction
tests, and host-signed verification receipts.

Critical mutants MUST have zero survivors. Tests, runner, thresholds, and
critical classifications freeze independently of the candidate. A generated
success summary, confidence score, test count, or popularity signal grants no
authority.

## 10. Sanitized learning trace

The live intent/proposal/correction/result history is protocol rehearsal
evidence only after sanitization. It contains structured intent, assistant
proposal, authenticated user correction, measured tool/agent result or
failure, superseded assumption, and successor invariant.

Raw transcripts, prompts, completions, hidden reasoning, local paths, tokens,
credentials, and private payloads MUST NOT enter protocol Frames or portable
packages. User decisions are user-signed or distinctly host-attested.
Assistant proposals remain proposal-only.

The deterministic reducer commits the ordered event set. Missing/reordered
events, summary drift, forged decisions, unresolved corrections, or correction
without a successor invariant MUST refuse compatibility lock.

## 11. Known-handshake catalog

Discovery order is:

1. verify source RAPP/1 identity/history;
2. try approved Private Hive entries by deterministic matcher specificity;
3. run a current canary/rehearsal;
4. instantiate a local Compatibility Frame;
5. wake JIT generation only when no approved entry passes and model submission
   is currently authorized.

Equal-specificity incompatible matches refuse. No latest-wins or mutable
success-rate selection is permitted.

Catalog entries bind matcher, artifact bundle, Compatibility template,
fixtures, exhaust history, provenance, approval, revocation, and privacy.
Hive storage does not activate code.

## 12. First wild handshake

`softwarecoellc-vteam-hive` is the first owner-approved private wild
handshake. The checked-in fixture binds only public-safe hashes, byte counts,
source qualification counts, and private proof status:

```text
handshake profile:
  0c52264b81bf88dd8555defa9363a23d8eb8ef85c3c12f66ddcaaabfc85a8882
source Lens:
  679fff9531c0c8b13457d594f746c45da28925a7c1be40473e8ca00823db8671
target finalizer:
  c056339f90fdd4e604dbefa40291f1b7b22946d26749b36230bb3b29dd8e2296
```

The private source qualified two signed Frames and nine artifacts. Local
double-hotload, Compatibility Frame, and static-agent proof succeeded. Raw
private source bytes and local runtime state are not embedded here.

The generic CEO agent pin remains pending and therefore live organization
activation remains blocked.

## 13. N-Lens bounded search

One ancestor may fan out into independently pinned Lens Dimensions. Each may
produce a complete successor, trait successor, repair, compatibility agent,
compiler, or verifier.

The root freezes use case, corpus, holdout, authority, and limits. Dependency
and incompatibility pruning occurs before crossing. Exact equivalent work is
deduplicated without losing occurrence provenance. Beam/Pareto bounds,
candidate/cross/depth/round/work/byte limits, and durable no-progress stops
prevent exponential runaway.

Fitness is a scenario-relative vector containing mandatory passes, coverage,
holdouts, mutants, unknowns, privacy, loss, work, regressions, and canary
outcomes. It is never universal truth.

A selected complete candidate or crossed trait set creates another candidate
with exact parent/trait provenance and independent interaction tests. Selection
and adoption remain separate.

## 14. Recursive meta-evolution

The improvement ladder is:

```text
wild exhaust -> handshake successor
handshake outcomes -> Lens/compiler successor
proven implementation -> organization-seed trait candidate
cross-organization evidence -> protocol-successor proposal
```

Every level uses immutable parents, frozen scenario corpus, hidden holdouts,
controlled mutants, bounded canary, independent verification, rollback, and
separate promotion/adoption. Evidence may motivate the next level but cannot
authorize it.

Corpus provenance, lineage clustering, diversity slots, legacy regression,
and promotion firewalls address reward hacking, contamination, echo
amplification, monoculture, catastrophic forgetting, and automatic promotion.

## 15. Mutation offers and PR projection

A complete successor may be projected as a signed mutation offer through Git
PR, RAPP egg, Private Hive, Federation, or offline transport. The projection
binds exact source parents, successor Frame/tree, forward/reverse maps, traits,
artifact bundle, tests, receipts, and compatibility program.

The source organization may accept exactly, reject, select traits, relens, or
defer. Git merge/rebase/squash/cherry-pick is transport evidence only. Local
RAPP adoption requires a new local decision and successor Frame.

Wild adaptations influence an organization seed or protocol only through a
separate verified selection/crossing and successor adoption. Ancestors are
never edited.

## 16. CEO agent

The generic Brainstem-invoked CEO agent coordinates command scoping, plans,
worker assignments, crossing, verification, and handoff in autonomous, guided,
or fine-detail modes. It has no root keys or unilateral authority.

This release intentionally does not supply or invent its bytes. Activation
documents use a nullable placeholder only while the candidate remains
inactive. Live activation MUST refuse until the exact approved CEO agent pin
is supplied.

## 17. Profile relationships

RAPP Workspace/1 may provide authorized observations, catalogs, and pointer
composites. Its closed evaluator and disabled arbitrary-code boundary remain
unchanged.

RAPP Hive/1 may store approved packages as generic objects or sealed GODD.
Hive convergence does not activate them.

RAPP Federation/1 may transport sealed sovereign offers under bilateral
consent. Peers publish only their own additions and do not merge roots, keys,
native histories, or private state.

No sibling closed `/1` profile bytes are amended by this profile.

## 18. Prior art

`kody-w/UniversalDataConnectorAI` commit
`f2a978b9f85b65b9815b69d99c67e51c56732251` is conceptual provenance only.
Its unknown-source analysis, schema learning, transform synthesis, generated
connector, testing lifecycle, and registry informed this profile.

Ambient Azure/model access, broad catches, time/random/MD5 identity, floating
confidence, auto-approval, simulated tests, mutable sessions, popularity
ranking, and unqualified generated code are expressly rejected.

The prior repository is an immutable input organism, not RAPP/1 authority.
Its successor may rewrite the complete tree while preserving the ancestor
inventory and causal maps.

## 19. Unknown-unknown gates

Conformance and deployment account for matcher collisions, poisoned catalog
entries, stale compiled mappings, rehearsal overfit, agent substitution,
prompt/policy drift, file-routing races, recursive handshakes, catalog
rollback/forks, peer-mesh amplification, revocation, source privacy, semantic
loss, user interruption, submodules, LFS, path normalization, prompt
injection, dependency drift, compiler bootstrap, test-runner compromise,
holdout leakage, Sybil evidence, and whole-store rollback.

Unknown or unsupported conditions fail closed with retained evidence. The
reference cannot prove host honesty, universal semantic truth, secure
production key custody, or real-world effect correctness.

## 20. Conformance and completion

Profile-independent conformance checks schema closure, immutable pins,
mutation/reverse accounting, deterministic compilation, atomic bundle
placement, trace authority/privacy, bounded search, promotion firewall, and
the private-safe Bill binding.

Passing conformance does not activate an estate. Completion reports the
generic CEO pin as pending, Brainstem unchanged, live activation false, and
safe external deployment unproven.
