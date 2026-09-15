# RAPP Workspace Grail/1 — seed-born adaptive frame lenses

**Protocol family:** `rapp-workspace/1`
**Normative spec ID:** `rapp-workspace/1.0`
**Generation:** `grail`
**Brand:** RAPP Workspace Grail/1
**Status:** first Grail authority candidate; not signed or estate-activated
**Parent:** current canonical [RAPP/1](https://github.com/kody-w/rapp-1)
**Payload contracts:** [schemas/](schemas/) (JSON Schema Draft 2020-12)
**Byte inventory:** [manifest.json](manifest.json)
**Inspected sources:** [provenance.json](provenance.json), explicitly non-authorizing

**Headline acceptance concept: Frame Anything.** Any explicitly supplied
local object may become opaque RAPP evidence. RW/1 workspace adoption is
conditional, never implied by framing. Frame Anything is a **bounded
iterative/branching lens evolution loop**, not one-shot transformation.
Refusals and other verified exhaust can drive the next lens/context attempt.
Run from the repository root:

```bash
python3 -B tools/frame_lens.py demo --rapp1-path "<EXPLICIT_RAPP1_CHECKOUT>"
```

This runs the owner's diverse synthetic matrix with expected refusals (§13.2).
Add `--fixture "<EXPLICIT_LOCAL_OBJECT>" --output <fresh-relative-directory>`
to frame one supplied object. RW/1 abbreviates `rapp-workspace/1.0`; it is not
an alternative wire version or signed activation.

The words MUST, MUST NOT, REQUIRED, SHOULD, and MAY are normative.
This specification defines the first Grail Workspace policy contract.
Schema validity,
a successful test, a Git branch, a source pin, or a model's assertion MUST NOT
be represented as owner acceptance, signed authority, or deployment.

## 1. Authority, versioning, and unchanged substrate

RAPP/1 exclusively governs identity, minting, canonicalization, address spaces,
the eleven-key frame, stream linkage, signatures, eggs, and the signed estate
registry. On any conflict, an implementation MUST refuse in favor of current
canonical RAPP/1. It MUST NOT fork or modify a parent primitive.

Every frame MUST retain exactly:

```text
spec kind stream_id seq utc payload payload_hash frame_hash prev prev_wave sig
```

`spec` MUST be `rapp/1`. `prev` MUST name the preceding **particle**, not wave.
`seq`, monotonic stream-local `utc`, `prev_wave`, and signatures MUST satisfy
RAPP/1 §7. All Workspace records in this reference use the already registered
`body.pulse` kind on body streams. Payload schema names are not new frame kinds.
A production estate MUST register its creation geneses and exact profile pin
through the existing authenticated RAPP/1 §13 registry. This document creates
no alternate registry, identity, hash domain, egg variant, or wire endpoint.

The parent inspection is current canonical-main commit
`dda32d741c7218f41443a5bd17eebfe0eae82cb7`, selected revision wave
`83ca275f35cca96e43d75c99d338326c1a39b2240eabf57eb7c29ac96cc90818`
(rev-15). The parent chain's integrity and owner-selected canonical publication
MUST be distinguished from an estate's own activation and independent trust.

The owner designates this architecture as the **first Grail** Workspace
contract, not a successor major version imposed by pre-Grail experiments.
Published workspace 1.x/2.0 materials are historical experimental/migration
inputs, not normative Grail predecessors. The original labels and content
MUST remain byte-exact; archival classification MUST NOT rewrite history.

The latest pre-Grail `rapp-workspace/2.0` text is retained at
[`../historical/pre-grail/2.0/SPEC.md`](../historical/pre-grail/2.0/SPEC.md),
exactly **10,596 bytes**, raw SHA-256
`86fe0ec4085e4f7bf33fe622519342bfed9f754ee4bdf45f41288129bf6e256c`.
Its original relative links were rooted at the repository root. Archival
relocation MUST NOT be used to change those historical bytes. Root `SPEC.md`
is a latest-entry document. Both 1.1 and both 2.0 published specification
snapshots, plus their entry documents, are byte-pinned in the
[historical index](../historical/pre-grail/index.json). No historical 1.0
SPEC was found here; implementations MUST NOT fabricate missing source bytes.

Historical use of the string `rapp-workspace/1.0` MUST NOT be treated as Grail
adoption. Every current Workspace payload MUST carry `generation:"grail"`,
and Grail identity metadata MUST carry `workspace_generation:"grail"`.
These are policy discriminators, not new identities or cryptographic
authority. The exact new spec hash, not a label or discriminator alone,
selects this contract. Old signed registry pins MUST NOT be silently rebound
to new bytes. Any existing label collision requires an explicit
parent-authorized adoption transition naming old and new commitments;
if that transition is unavailable, activation MUST remain blocked.

Legacy payloads whose names resemble current schemas MUST remain inert
pre-Grail data. They MAY pass through lenses as retained content, but MUST
NOT execute current schema effects or qualify as current lens/route/control
records without the Grail discriminator and verified current contract.

“Grail” here designates the owner's first Workspace authority candidate.
It MUST NOT imply an activated RAPP/1 §13.3 `grail-kernel`, invent a
`grail_id`, or waive the parent's immutable-kernel rules. Release-gate success
is qualification evidence, not a signature or owner ratification.

A pre-Grail workspace MUST NOT be relabeled Grail merely because its tooling
updated. A change to this normative contract after publication MUST receive
a new version/pin; these identifiers MUST NOT denote
different published shapes.

## 2. Birth: one local seed and one genesis lineage

An estate MUST originate in one locally instantiated workspace seed. The seed
is the `seed-genesis` **particle carried by a normal RAPP/1 frame**; the
enclosing wave anchors its Workspace lineage. It is not a new identity.
The workspace's existing RAPPID MUST be reused, or minted once by RAPP/1 when
the workspace is genuinely new. Names, paths, providers, machine labels,
content hashes, and template addresses MUST NOT be substituted for that mint.

For a new estate the seed MUST be the root stream's genesis. An estate MUST
accept exactly one seed. Each descendant MUST reference that seed wave and
the same estate RAPPID and hard `world_id`. A different seed at the same
identity is not an update; it MUST be refused and retained as conflict
evidence where applicable. Copying a workspace is a replica of that lineage,
not permission for another independent writer to extend its stream.

Only generic invariants are predefined: local-only by default, immutable
history, native sovereignty, explicit observation scope, verified derivation,
independent authorization, world isolation, preserved conflicts, and resource
bounds. A seed MUST NOT prescribe providers, folder anatomy, organization
labels, taxonomies, adapters, model vendors, or default lenses.

Shapes and capabilities MUST grow from approved local observations. Two
machines MAY grow different shapes from the same generic seed policy; equal
software versions MUST NOT force equal estates. Labels are opaque local
vocabulary, not identities or authority. Reusing a template MUST NOT copy its
live identity or confer its trust; RAPP/1 §9.4 governs actual hatching.

For a pre-Grail migration, a seed is an additive adoption point, not a claim
that experimental history was born under this policy. If the estate RAPPID
already has a stream, the seed MUST extend its verified existing head and name that head in
`inherited_heads`. Its original creation genesis MUST remain the one genesis
lineage. It MUST NOT reset sequence, re-genesis, or mint another RAPPID.

## 3. Native sovereignty and opaque observation

Observation authorization MUST be explicit and bounded. A locator discovered
inside metadata MUST NOT authorize traversal. Private estate files,
credentials, chats, mail, histories, or native profiles MUST NOT be read
merely to organize a workspace. Production adapters MUST use separately
approved metadata surfaces, bounded no-follow reads, stable filesystem-object
checks, and last-good state on incomplete or unsafe reads.

Unknown AI-local patterns MUST first produce a `native-shape-observation`.
Its `shape` is an opaque locally observed label; its bounded metadata is only
the authorized observation, not an inferred provider parser or transcript.
The `fingerprint` MUST be the RAPP particle of the exact metadata list.
`source_state:"opaque"` and `native_compliance:"unclaimed"` are REQUIRED.
Unknown or changed patterns MUST NOT automatically select routes, execute
code, grant rights, or masquerade as a known adapter.

For the synthetic acceptance class, `opaque-native-source` MUST retain each
observed regular file's exact octets as canonical base64, safe relative path,
raw SHA-256 and length. Its inventory MUST be the RAPP particle of the
ordered `{path, bytes, sha256}` list. Every decoded byte count, digest, path
and encoding MUST be independently checked. `native_identity:null` MUST NOT
be replaced with a minted identity for the source folder.

A `native-shape-observation` MUST carry its source-wave list. This list may
be empty for other scoped metadata observations; in the supporting native-directory
scenario it MUST contain the one complete `opaque-native-source` frame.
Metadata MUST exactly match the retained source's observed paths/digests and
subject, not a model-supplied summary. Both source and observation frames
are projections; neither claims native RAPP compliance.

Sources remain sovereign. No observation, lens, merge, projection, migration,
forget action, import, or reattachment may write, move, rename, flatten, delete,
repair, or reinterpret the native source. A derived projection MAY be
RAPP-compliant without the source being natively RAPP-compliant. Implementations
MUST state which object was verified; “the native estate is compliant” is not
a consequence of wrapping its metadata in a frame.

## 4. Immutable mutation and recursive lenses

A historical frame MUST NOT change. “Mutating a frame” means deriving a
**successor object at a new wave address** from source/context frames through
an exact content-addressed lens. Implementations MUST retain the source,
lens, declared reads, result, receipts, alternatives, and all ancestors.
Superseded is not deleted. The RAPP envelope's predecessor MUST NOT be edited
to express a semantic source or graft.

A lens MUST itself be a verified frame whose content is a `lens-declaration`.
Its exact wave selects the declaration; its particle commits the recipe.
The declaration MUST name its observation evidence, proposer, candidate
synthesis mode, exact runtime bytes, and bounded deterministic program.
For the reference, `runtime_sha256` measures the exact file-manifest bytes,
which pin the complete reference/spec/schema bundle and parent provenance.
Every execution MUST recheck that manifest, not only an interpreter file.
Changes to either recipe or runtime require new evidence and a new candidate;
the old lens MUST remain available.

**Closure:** every verified frame, including a seed, a lens, a receipt, and a
previous derived frame, MAY be input to another lens. There is no terminal
frame type or protocol lifetime depth. A bounded implementation MAY defer a
batch at a resource ceiling; it MUST NOT discard ancestry or declare further
mutation semantically impossible. Derived lenses MUST pass the same trial and
adoption gates; self-modification grants no exceptional privilege.

The reference's `derived-frame` is an ordinary payload, NOT another frame
envelope. It commits a result particle plus its exact canonical JSON text in
`value_json`, and names its lens and declared-read frame. That bounded string
lets closed payload schemas carry arbitrary **inert** result objects without
open extension bags or interpreting copied control records as new commands.
The decoded text MUST be a canonical RAPP object; its particle MUST match
`content`; deterministic replay MUST reproduce its exact bytes.
Copying a seed/adoption record this way MUST NOT create a seed or adoption.

## 5. Complete reads and deterministic trials

`declared-reads` MUST bind the exact lens, ordered source frames, ordered
context frames, and every input read as name, frame wave, JSON pointer, and
value particle. Source/context arrays are ordered function arguments, not
sets to reorder. Read names MUST be unambiguous. Every input MUST be used.
The read trace MUST be independently recomputed, with no omitted, extra,
substituted, or undeclared dependency. `complete:false` MUST refuse mutation.

In the bounded IR, pointers address the input's content particle: an ordinary
frame's payload, or the verified decoded content of a derived frame. This is
an explicit data projection, never an altered RAPP envelope. The empty
pointer denotes the whole particle. Original envelope bytes remain retained
and verified. The IR supports:

- `identity`: read the whole content object without alteration;
- `project`: copy declared scalar reads into locally named facts at a declared
  logical tick; names are learned vocabulary, not protocol taxonomy;
- `workspace-attempt`: read complete opaque-object and observation particles,
  check the synthesized member map against evidence, and deterministically
  emit a workspace candidate or unresolved successor under §13.2;
- `workspace-context-attempt`: consume a verified source-bound refusal's code
  and missing fields, plus explicitly supplied verified container context;
  produce a new successor, partial mapping or contradiction under §13.3;
- `amend`: copy a whole object and replace explicitly named existing scalar
  fields. Estate/world/seed/schema/owner/proposer/synthesis boundaries MUST
  NOT be amended by this instruction.

A reference trial MUST NOT run Python, shell, native adapters, model calls,
network requests, environment reads, filesystem reads, or clocks supplied by
candidate code. It consumes only copied declared values and a trusted pinned
interpreter. It MUST refuse unknown operations, missing pointers, ambiguous
names, boundary changes, oversized output, and changed runtime bytes.
General programs outside this bounded class require separately verified
isolation and a complete read monitor; they MUST NOT be silently approximated.

## 6. Receipts, equivalence, and independent adoption

`mutation-receipt` MUST link lens, sources, contexts, declared-read frame, and
successor. Every preservation entry MUST bind retained source/lens octets
before and after by raw SHA-256 and byte count. The result's links and content
MUST agree with the receipt. Raw octet digests are measurements, not new
RAPP addresses. The reference measures retained frame octets ONLY.
It MUST NOT claim unobserved native bytes were measured. Full native
preservation/canary proofs in this repository use synthetic fixtures only.

`equivalence-evidence` MUST be derived by replay, not trusted as a Boolean.
At least two independent deterministic executions MUST reproduce the result
particle. The verifier MUST run the specified incomplete-read,
read-substitution, source-tamper, context-substitution, world-substitution,
and result-substitution negative tests and observe actual refusal. A consumer
MUST recompute this evidence, not accept claimed check names. Equivalence
means **on the declared inputs under this evaluator**, not universal semantic
equivalence, privacy clearance, or proof of model quality.

Model assistance MAY synthesize a candidate lens. It MUST NOT authorize
itself, alter the evaluator, select trust inputs, or convert test success into
permission. A model-derived result remains a candidate until verification
and a distinct authorized decision both succeed.

`verification-adoption` MUST bind the exact candidate, evidence, owner/policy
authority and prior adoption head. Acceptance MUST compare-and-swap that
head. An output cannot be adopted through a lens that is not itself adopted;
bootstrapping a lens permits sandbox trials but only independent adoption of
that exact lens. A model proposer's identity MUST NOT authorize its own trial.

The local reference takes an explicit `LocalConsent` from its trusted caller:
owner RAPPID and an allowlist of exact decision **particle hashes**. This
object is a local capability boundary, not a protocol registry or portable
credential. The interpreter never receives it. Restarts MUST receive it
independently again; history/cache content MUST NOT populate it. Local
unsigned decisions demonstrate integrity and explicit caller consent, not
cryptographic authorship. Signed/off-device policy use MUST wait for a real
RAPP/1 registry/signature adapter; the reference refuses that mode.

Verified drift MUST block affected future use without erasing historical
evidence. `lens-drift` binds lens, trial, reason and optional candidate
replacement. The bounded reference requires independent exact consent to
suspend a lens; untrusted observations cannot poison unrelated lenses.
A replacement MUST be verified and adopted separately. No “repair in place.”

## 7. Scan tiles, exhaust, and recursive dimensions

A `scan-tile` is one immutable observation intent anchored to the estate seed,
not another estate genesis. It MUST state scope, exact targets, logical tick,
previous report, optional parent tile, local-change signals, and periodic
baseline policy. A child dimension MUST have its own canonical RAPPID and
creation genesis linking the parent wave and same seed/world. Recursion MUST
preserve the parent, sibling histories, and scope; a drill is not permission
to observe anything named by an untrusted finding.

Responses MUST be bound to that tile and to one requested subject. The
deterministic `dream-report` MUST use verified responses in unchanged RAPP/1
`(utc, frame_hash)` order, refuse duplicate/foreign responses, and explicitly
retain missing subjects. Missing MUST NOT be represented as healthy.

The first scan, a scope/policy change, and each periodic baseline deadline
MUST scan the entire approved scope. Otherwise the exact follow-up target
set MUST be previous exhaust union approved local-change signals. Exhaust
includes findings and missing responses. An unimplicated, unchanged subject
MUST have zero follow-up invocation cost. O(delta) refers to these **subject
invocations**, not zero metadata, replay, or verification cost. Baselines
remain O(scope). Untrusted/absent signals or a stale baseline MUST NOT support
a whole-estate clean claim. Partial reports preserve last-good state.

A deeper drill MAY create child dimensions under the implicated parent and
return an additional report. Late children MAY reference a frozen earlier
tick; they MUST NOT change its bytes. “Chain as clock” means causal lineage
and logical ticks govern dependency readiness. It MUST NOT replace the
parent's timestamp validation, cross-stream ordering, or lease authority.
No global wall-clock synchronization or universal heartbeat is required.

## 8. Merge fidelity and conflict preservation

Merge MUST verify complete input history and declared context first. For
the bounded learned-fact class, join histories by locally named dimension
and logical tick. A shared dimension is mergeable iff every overlapping tick
has a single agreeing value particle. The integer numerator is mergeable
shared dimensions; the denominator is all shared dimensions. Zero shared
dimensions MUST be reported explicitly, not divided or labeled a perfect
semantic score.

`dimension-merge` MUST retain the full union of both sides' waves and their
ancestry, including one-sided facts and every contradictory alternative.
It MUST NOT select a winner by arrival, timestamp, hash order, or fidelity.
An explicit reconciliation MUST name all conflicting parents and pass its
own lens/evidence/authority gates; merge alone never authorizes it.

A semantic conflict across independent dimension streams is not a
same-stream/sequence fork. A RAPP/1 fork MUST latch refusal of both branches
and dependent results, retain exact evidence, and survive restart. Only the
parent's owner-authorized recovery mechanism can resolve a stream fork.

## 9. Deterministic reattachment and the one-way membrane

A stranded result MUST provide complete verified declared reads. An explicit
bounded candidate ladder MUST be searched in declared order: approved local
head, other approved local dimensions, then independently approved public
contexts if supported. Candidate enumeration MUST NOT traverse implied
locations. A base conflicts exactly when its declarations disagree with a
declared read name on their intersection.

`deterministic-reattach` MUST record the comparisons through the first
contradiction-free base. It MUST preserve `grafted_from` and the original
source. Missing non-overlapping declarations are not proof of semantic
agreement or permission to omit actual read dependencies. All original
dependencies MUST still resolve. If no base qualifies, `dry-hole` is a no-op
for routing and source history; retaining a diagnostic is permitted.

A reattachment record is a candidate relation, not an envelope repair or
authorization. Actual adopted enrichment MUST undergo a new lens trial with
the chosen context, fresh equivalence evidence, and independent adoption.
The reference emits candidate/no-op records; it does not implement automatic
federated graft execution.

The private-estate membrane permits only independently authorized verified
public input and refuses private-frame egress. A `dogg` label MUST NOT grant
export permission. Imported public frames remain foreign evidence, never
local geneses, owners, or native dimensions. GODD stays private by default.
Publication outside this membrane is a separate explicit owner action under
the Hive/DOGG policies, exact-byte clearance and required sealing; it is not
implemented by the lens interpreter. This gate is not protection against
unmediated egress, malicious host code, or side channels.

## 10. Rebuildable manager projections and restart

`registry-projection`, `registry.json`, dashboards, editor layouts and current
workspace-manager state MUST be deterministic rebuildable projections from
verified **adopted** history and separately verified migration evidence.
They MUST retain historical adoption addresses even when a fork makes their
current entries ineligible. Ineligible entries MUST NOT route.
They MUST NOT authorize themselves, introduce a competing RAPP registry,
mint identities, or become authority because they are newer or available.

Discovery and candidate execution MUST NOT select routes. Exact independently
authorized `routing-decision` frames establish selection/suppression intent.
Suppression MUST win over selection. Re-add MUST be explicit and MUST NOT
recreate native data; re-add alone does not select a route. Restart, cache
loss, rescan, rollback, and import MUST NOT erase suppression.

Restore MUST verify original frame bytes, stream identities, complete
dependencies, receipt replays, independent consent, and protected high-water
checkpoints. Stale/corrupt/missing registry caches MUST be rebuilt, not trusted.
A lower checkpoint, changed same-sequence head, lost fork evidence, path
escape, unsafe link, identity substitution, or missing historical byte MUST
refuse. A whole-store rollback cannot be detected using only that store;
an independently protected monotonic frontier is REQUIRED for that threat.

## 11. Explicit bounded pre-Grail migration

Migration MUST preserve original RAPPIDs, `world_id`, paths, all original
frame/file octets, symlink targets, native references, suppressions, and
selection evidence. It MUST NOT move sources, rewrite a legacy registry, or
retrospectively claim that old records used Grail schemas.

The reference migrates **one explicitly selected existing estate per call**.
It MUST NOT discover or migrate an estate inventory automatically. Supported
source labels are pre-Grail `rapp-workspace/1.0`, `/1.1`, and `/2.0`;
this is a bounded migration lane, not perpetual universal compatibility.

`source_generation:"pre-grail"` and the source label MUST be supplied
explicitly. A present identity version must agree; an omitted historical
version may be bound only through the independently approved migration plan.
Existing RAPPID and `world_id` MUST be present and valid; missing worlds,
provisional identities, or unknown generation markers MUST refuse. An already
Grail identity/seed MUST NOT enter the pre-Grail lane.

For 1.1/2.0, `source_spec_sha256` MUST match one archived source SPEC for
that label. For pre-Grail 1.0, it MUST be null because no original SPEC bytes
are available here; null explicitly limits the claim to byte-preserving
metadata migration, not verification of an absent historical contract.
The new Grail 1.0 hash MUST NOT be substituted for the absent legacy hash.

`plan_migration` MUST perform a read-only preflight and produce the exact
`migration-record`: source generation/label/pin, original identity SHA-256,
RAPPID/world, complete baseline, original registry commitment, inherited
heads, seed and authorized owner. The owner MUST independently approve that
record's RAPP particle before `migrate` writes anything. The frozen UTC and
input bytes MUST reproduce the same seed/plan; model or source metadata
cannot populate approval. Restore MUST recheck this independent consent.

The reference writes only `.workspace-grail/`, containing an additive seed,
`migration-record`, normal RAPP frames and a new projection. The old manager,
paths, registry, source bytes and history remain in place. The migration
record MUST bind the complete authorized baseline by safe relative paths,
type, mode, raw SHA-256 and size; link targets are measured without following
them. The original registry commitment retains even unrecognized provider
shapes and suppression forms without silently translating them.

The reference bounds each pass to 4,096 entries, 16 MiB per file, and 64 MiB
aggregate baseline bytes. Exceeding a bound MUST defer without pruning.
Full-byte baseline reads require explicit workspace authorization and MUST
NOT traverse routed sources or native stores. Existing root-stream frames
MUST be supplied explicitly for verification and continuation, not discovered
by scanning private profiles. Unsupported/ambiguous old state MUST remain
opaque and unselected until a verified migration lens exists.

Repeated migration with the same protected checkpoint and unchanged baseline
MUST be idempotent. Conflicting sidecars, identity changes, truncated legacy
history, unsafe paths, changed baseline or newer suppression MUST refuse,
never overwrite. A manager adapter that cannot reconstruct a legacy feature
MUST preserve the original and report that feature blocked. Keeping opaque
evidence is not a claim that its UI/adapter was migrated.

## 12. Metadata-only estate eggs

`metadata-only-estate-egg` is an export **receipt**, not a new egg variant.
Packing MUST use and verify native RAPP/1 §9 container/variant rules. A
nonempty native estate nests neighborhoods and organisms; required inert
identity/soul metadata MUST NOT be bypassed with an invented ZIP format.
Artifact identities MUST be distinct from the live estate and minted by
RAPP/1; import MUST NOT transfer live instance identity or owner authority.

Selection MUST be an exact allowlist of inert manager metadata. Sources,
native databases, chats, memories, credentials, keys, executable agents,
provider caches, pending stages, backups, Git internals, and unrelated logs
MUST NOT enter it. The bounded reference constructs only inert identity,
fixed non-executable soul text, and the verified registry projection in
memory; it does not recursively pack a directory.

The egg and its topology metadata remain GODD. No file name, hash, schema,
or lack of plaintext sources proves global privacy clearance. Import MUST
remain inert; destination routing requires fresh local bindings and adoption.
Exact-byte round-trip and canonical egg verification are REQUIRED. Export
does not publish and does not authorize sealed key release.

## 13. Conformance, portability, and honest limits

All schemas MUST be closed, Draft 2020-12, bounded, and used with the parent's
I-JSON domain checks. Required unknown semantics MUST fail closed. Portable
paths use a deliberately narrower safe relative alphabet; no private absolute
paths belong in portable records. Profile-created strings MUST be NFC.
The `value_json` encoding of an existing result particle preserves its original
code points under the parent's no-normalization rule; it is not a new label
and MUST NOT be normalized to manufacture equivalence.
The stdlib validator implements only the schema vocabulary shipped here,
not arbitrary JSON Schema. The offline IR uses exact integers, not floats.

The manifest MUST enumerate every normative spec/schema with raw SHA-256 and
byte count, separately from reference code, historical bytes and source
provenance. `protocols/index.json` pins the manifest; the manifest does not
hash itself. Neither file is the signed RAPP/1 registry. Skill prose is an
execution entry point and MUST NOT replace the normative contracts.

The reference MUST receive an explicit canonical checkout and verify its
inspection commit, source bytes and selected parent chain. It MUST NOT use
the simplified Frame Chains teaching implementation. Frame Chains provenance
is pinned at current-main commit
`0aeb8332f4bb20bc689aba217a704b463ba20105`; its orchestration ideas are
adapted under RAPP/1, not copied as substrate or protocol authority.

Conformance MUST exercise synthetic positive and adversarial cases for birth,
divergent local growth, unknown observation, replay/read closure, model
non-self-authorization, preservation, lens-on-lens recursion, branches,
scan/delta/baseline, drills, reattachment/dry holes, membrane, reconstruction,
restart, tamper/path/identity/rollback/fork refusal, migration and native eggs.
It MUST emit and independently scan **nonzero** RAPP frames/streams. A
zero-artifact CLEAN result MUST NOT count as conformance evidence.

This release does **not** implement live native providers, AI model synthesis,
signed estate activation/owner succession, distributed CAS/consensus,
automatic semantic reconciliation, deployed federation, native key release,
live editor routing for opaque pre-Grail providers, or automatic graft execution.
The local storage reference is bounded POSIX tooling, not a hardened
multi-tenant service. Its migration checks cannot prevent a separately
authorized external process from modifying source files after measurement.
Equivalence/read completeness apply only to the monitored IR. Resource
ceilings are refusal/defer points, not pruning rules.

Frame Chains field observations are not reproduced by these synthetic tests.
Scale beyond the local fixtures is unmeasured. Sparse follow-up assumes
trustworthy exhaust/signals and periodic baselines; an oracle's stable floor
is not absolute health. Reattachment depends on complete declared reads and
the stated ladder. Fidelity equally weights dimensions, not business
criticality. Partitions can create competing writers; the chain is not
Byzantine consensus. A membrane controls only traffic that traverses it.
Owner ratification, independent anchors, protected monotonic storage, exact
profile/genesis registration, reviewed native adapters and explicit deployment
consent remain owner-authority/production blockers.

### 13.1 Supporting UNKNOWN-native directory scenario

The supporting directory scenario MUST begin with at least three distinct,
previously unclassified **non-RAPP native workspace shapes**. The reference
creates synthetic opaque files with different layouts, arities and octets
before the seed observes them. A fixture producer MUST be separate from the
learner: the learner MUST NOT receive fixture recipes, provider names,
preassigned categories or a catalog of recognized native patterns.

The supporting scenario MUST expose these stages:

| Stage | Required evidence |
|---|---|
| BEFORE | Actual native file inventory; source has no assigned RAPPID; no preassigned taxonomy. |
| OBSERVATION | Bounded real file reads, an opaque source frame, and a source-bound observation frame. |
| LENS | A different content-addressed candidate program derived from each observation's measured structure, not merely a renamed identical recipe. |
| SUCCESSOR | Real verified eleven-key RAPP/1 frames carrying `rapp-workspace/1.0` derived content and complete lens/read/source ancestry. |
| VERIFICATION | Replayed result particles, actual negative refusals, unchanged native bytes/layout, independent adoption boundary, and retained originals. |
| RECURSIVE | Original source, observation, lens and successor each pass another lens; a derived lens runs again and a derived successor can continue. |
| PROJECTION | Compliant adopted workspace projections rebuilt after restart and independently scanned nonzero emitted frames. |

The reference observer is bounded per root: 32 directory entries, 16 regular
files, depth 4, 4,096 bytes/file, 16,384 total file bytes and two seconds.
It MUST use descriptor-relative no-follow reads and stable before/after file
identity checks. Symlinks, hardlinks, unsafe/non-regular inputs, changing
membership and budget exhaustion MUST refuse, not produce a partial clean
observation. This supporting generator MUST NOT accept live native-profile roots; it reads
only its explicitly created synthetic fixture roots.

The bounded structural learner MUST derive IR binding names and pointer
positions from the observed file paths/arity, with the retained source
inventory as context. It MUST NOT decode a provider format, infer a semantic
taxonomy, mint a native identity, or receive an owner-consent capability.
The default fixture produces genuinely different binding arities; arbitrary
fresh fixture seeds and held-out layouts MUST work without changing the
learner. Native bytes remain opaque even where they happen to resemble JSON,
instructions or executable code.

Each candidate MUST pass the normal complete-read/replay/equivalence gate.
The proof MUST additionally refuse source-byte substitution, path escape,
invented native identity and invented owner authority. Refused mutations
MUST NOT advance history. The synthetic harness may independently approve
exact local decision particles **after** verification; it MUST identify that
consent as simulated and MUST NOT fabricate signatures, registries or Grail
activation. The same estate stream MUST retain all original and derived
frames; no RAPPID is assigned to native folders merely to make them comply.

Original file bytes, inventory and filesystem identity MUST compare unchanged
before/after the pipeline. Supporting frame octets MUST remain immutable.
The demo MUST run the canonical RAPP/1 checker from the explicitly supplied
checkout and report actual nonzero emitted/scanned counts. Reported projection
validity means a source-bound opaque/structural workspace view—not native-app
semantic understanding, a production adapter, or automatic source migration.
Passing the demo qualifies the candidate; it does not activate signed authority.

### 13.2 Frame Anything: universal framing, conditional RW/1 adoption

**Frame Anything** is the headline demo and acceptance gate. Any explicitly
supplied local object MAY first be represented as an opaque content-addressed
RAPP source frame/receipt: a directory, arbitrary file, source tree, foreign
agent/skill manifest, structured document, or unknown workspace. Framing
MUST NOT claim native semantics, identity, authority, or RW/1 workspace
compliance. Universal means no provider/domain whitelist; it does not waive
resource limits, observation authorization or safe I/O.

`opaque-local-object` MUST record kind, original root-name/path octets as
canonical base64, retained entries, exact content coverage, and a fingerprint
which is the RAPP particle of `{object_kind, root_name_b64, entries}`.
Encoded relative names are **opaque provenance**, not authorized extraction
paths. They MUST NOT be normalized, executed, or used to follow references
embedded in a foreign manifest. No native RAPPID is assigned.

Capture MUST use bounded no-follow descriptor-relative reads. The reference
supports up to 128 entries, 64 regular files, depth 16, 16 MiB/file, 64 MiB
aggregate and five seconds. Hardlinks, changing identity/membership, unsafe
scope and exhausted budgets MUST refuse before a clean framing claim.
Regular files up to 4 KiB retain exact octets inline. Larger files retain an
explicit digest-only measurement receipt; the frame alone MUST NOT claim
those original bytes are available. Symlinks retain link-target bytes without
following the target. Special nodes are metadata-only and MUST NOT be opened
or given a fabricated content hash. Directory membership is metadata, not
raw directory-file content.

Source-bound observations and evidence-derived `workspace-attempt` lens
declarations MUST precede conversion. The lens MUST declare complete reads of
the source and observation. Its member mapping MUST match measured entries;
a candidate-supplied mapping cannot weaken eligibility policy.

For this bounded class, `workspace-successor` is eligible only for an
inline-verified directory with at least two regular files and no unresolved
links/special members. This establishes a **structural workspace candidate**,
not native application semantics. All other observed cases MUST emit
`workspace-unresolved` with the deterministic applicable reason:

1. non-directory object: `incompatible-object-kind`;
2. link/special membership: `unresolved-links-or-special-members`;
3. missing inline content evidence: `external-content-evidence-required`;
4. insufficient container membership: `insufficient-workspace-evidence`.

Each unresolved successor MUST retain its source/observation ancestry,
`adoption_eligible:false` and the need for additional verified workspace
context. A valid RAPP/1 envelope or valid RW/1 unresolved payload MUST NOT be
reported as a compliant or adopted workspace.

Verification MUST independently replay the decision, validate exact outcome
semantics and negatively test substitution. Even exact caller consent MUST
NOT adopt an unresolved successor. Copying it through another lens MUST NOT
clear that refusal. The unconditional `project` operation MUST NOT bypass
assessment for opaque-local-object data dependencies, including derived
copies and source-bound observations. Eligible candidates still require
separate independent adoption; source framing and selection are not consent.

The CLI MUST accept an explicit fixture/object path and visibly show source
fingerprint, opaque frame, lens declaration, declared reads, successor or
refusal, verification, preservation and retained ancestry. Output MUST be
outside a supplied source. Supplied objects MUST NOT be automatically adopted.
The built-in matrix MUST include at least three radically different unknown
inputs and at least one expected unresolved result. Synthetic owner approval
MAY demonstrate eligible adoption but MUST be identified as simulated.

The reference matrix includes an unknown workspace, source tree, foreign agent
manifest, structured document, binary file and empty directory. The foreign
manifest MUST first fail lens A, then use that refusal and explicitly supplied
new context in lens B to succeed. The matrix expects three candidates and
three stable unresolved outcomes. Both success and
refusal histories MUST reconstruct after restart and remain available for
further lenses. The gate MUST independently scan nonzero emitted RAPP frames
and separately report framing counts, candidate counts, adopted workspaces
and unresolved objects.

CLI status 0 means a supplied candidate was framed (not adopted), or the
built-in expected-outcome matrix passed. Status 2 means framing succeeded but
a supplied object remains unresolved. Status 1 means a capture/verification
failure. Neither status 0 nor an integrity scanner's COMPLIANT verdict grants
workspace semantics, signed authority, execution rights or publication.

### 13.3 Bounded iterative/branching lens evolution

A refusal, partial mapping, contradiction set, failed test, or unresolved
field MUST be a valid retained successor/exhaust frame, not an instruction to
discard the input or pretend the goal succeeded. The scheduler MAY reapply
the same content-addressed lens with new context/evidence, consume a lens
descendant produced by a verified mutation, or select/synthesize another
candidate lens. Every actual attempt and its complete explicit parent set
MUST remain in history, including failures, duplicates and losing branches.
No loop record is an alternative RAPP/1 envelope, registry or authority.

The closed records are:

- `lens-loop`: fixed root and maximum attempts, maximum depth and no-progress
  window. Defaults are 12 attempts, depth 6 and two no-information attempts;
  hard ceilings are 128 attempts, depth 32 and 128 admitted requests.
- `iteration-request`: exact lens/source/context/read-declaration references,
  strategy, parent-attempt set, derived depth and content-addressed work key.
- `iteration-exhaust`: exact executed outcome/receipt/equivalence references,
  or a deterministically reproduced failed-test code; classification, missing
  fields, contradictions and normalized semantic result.
- `iteration-attempt`: execution or dedupe decision, duplicate ancestor,
  ordinal/depth, retained exhaust, computed information frontier/delta,
  semantic state commitment and no-progress/repetition evidence.
- `iteration-stop`: explicit reason, all attempt references, all remaining
  pending requests, verified information frontier and any candidate.

All references MUST resolve and remain seed/world-bound. Parent sets MUST be
sorted, unique, from the same loop and complete for consumed same-loop exhaust.
Depth MUST be zero for a root request, otherwise one plus the greatest parent
depth. A claimed descendant MUST have actual declared-read mutation ancestry
from the named lens parent; mere stream-clock ancestry or a changed name is
insufficient. Reapply MUST name the same lens as a parent attempt.

Eligible requests MUST be executed in ascending `(depth, work_key.hash,
request.frame_hash)` order over the explicit candidate set. This is scheduling
policy, not a replacement for RAPP/1 timestamps or canonical merge order.
Cross-stream record presentation remains `(utc, frame_hash)`.

`iteration-work-key` and `iteration-state` are closed **RAPP particle
commitments**, not frame kinds or new hash domains. The work key binds the
fixed root, exact runtime pin, program without its decorative logical tick,
normalized source/context content and any explicit declared-read content.
Lens labels, envelope sequence/UTC, wave rewrapping and parent bookkeeping
MUST NOT manufacture new work. Identical keys MUST reuse previously verified
exhaust rather than execute again; a new request/attempt still preserves its
own parent set and the dedupe reference.

Information MUST be independently derived from verified retained source
content and replay-checked diagnostics. Arbitrary progress messages, proposed
code, labels, renamed roots and copied frames MUST NOT count as new evidence.
Normalized source content excludes cosmetic root labels and modes while
retaining relevant entry names, kinds, coverage and exact content commitments.
Normalized workspace outcomes exclude chronology/provenance wrappers while
binding their original root, actual context, members or refusal/contradiction.
The state commitment binds that root, the cumulative information frontier
and semantic result. A repeated state MUST be detected even when lenses
alternate or outputs arrive in new envelopes.

`new_information`, `repeated_state`, counters and work/state hashes MUST be
recomputed, not trusted as model claims. A generic changed message or an
unrelated new root MUST NOT establish mission progress or successful adoption.
The verifier MUST reproduce failed-test evidence through the pinned pure
executor. Shape validation alone MUST NOT authenticate an exhaust record.

Termination MUST be explicit:

1. `adopted-verified`: an exact verified RW/1 result for the loop's fixed root
   was independently adopted. A Boolean callback or payload flag is not
   evidence of that adoption.
2. `missing-owner-authorization`: a verified candidate exists but actual
   adoption authority is missing. The scheduler MUST NOT busy-loop, invent
   consent, or discard the candidate.
3. `attempt-budget` / `depth-budget`: the fixed configured bound is reached.
   Pending requests MUST remain named in the stop record.
4. `stable-fixed-point`: repeated semantic state, exhausted candidate frontier
   or the configured no-new-information horizon. Newly supplied verified
   information in pending work MAY continue exploration; renamed lenses or
   arbitrary messages MUST NOT bypass convergence.
5. `explicit-contradiction` / `explicit-refusal`: the retained evidence
   explicitly blocks the current bounded search, with no actionable pending
   branch. Contradictions MUST NOT be overwritten by timestamp/hash ranking.

A fixed point is relative to the supplied evidence, candidate frontier and
declared no-progress horizon, not a universal proof that future repair is
impossible. New externally supplied evidence MAY support another authorized
bounded run, but MUST NOT erase the earlier stop, counters or ancestry.
Trusted planner/reviewer code is outside the candidate IR; untrusted frames
MUST NOT provide executable callbacks. The scheduler does not sandbox
arbitrary host code or bound external model/network latency.

The implemented context-repair lens MUST read five complete inputs: original
source, original observation, source-bound refusal exhaust, verified context
container and its observation. Its `repair_code` MUST equal the actual
refusal code. The refusal's missing fields MUST justify requesting workspace
context. Context MUST be explicitly approved for observation, never inferred
by following an input's path or manifest instruction.

For this bounded repair class, a standalone inline file may acquire verified
workspace context only when the context passes the structural-container
gate and has one unambiguous member with the same original basename, exact
bytes, size and digest. The new successor MUST bind original source, context
and consumed exhaust. A matching name with different bytes produces retained
`context-source-contradiction`; missing/ambiguous membership produces a partial
`source-not-bound-to-context`; unsupported repairs remain refusals. The
earlier unresolved frame is never edited or retroactively adopted.

The headline demo/conformance MUST visibly prove A-refusal → exhaust/new
context → A′ or B → verified successor, and another input reaching a stable
honest refusal. Adversarial vectors MUST cover lens cycles, same-content
rewrapping, identical outputs, ping-pong, fabricated progress, missing parents,
false lens ancestry, root switching, bounded depth/attempt exhaustion,
missing authority and restart reconstruction of dedupe/iteration history.
