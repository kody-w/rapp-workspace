# RAPP Workspace/1 Grail — minimal safe kernel candidate

**Unique subordinate identifier:** `rapp-workspace/grail-1.0`

**Product/Grail brand:** RAPP Workspace/1 Grail

**Parent:** current canonical RAPP/1, unchanged.

**Status:** candidate. No signed Grail activation or safe external deployment
is asserted. The [blocking matrix](safety-matrix.json), [schemas](schemas/)
and [exact-byte manifest](manifest.json) are normative.

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

First Grail emits `safe_deployment:refused` for external effects. There is no
“all green therefore deploy” shortcut. An integrity scanner's COMPLIANT
verdict MUST be reported as integrity only.

## 2. Version collision and parent authority

Old `rapp-workspace/1.0`, `/1.1` and `/2.0` identifiers retain their published
meaning and exact pins as experimental migration inputs. They MUST NOT be
reused for this contract, relabeled current, or selected by a current
validator. Product numbering does not change protocol history.

The unique current ID is `rapp-workspace/grail-1.0`; “Workspace/1” is branding,
not an alternative validator name. Every receipt MUST bind this ID and its
exact normative SHA-256. Wrong-ID and wrong-pin inputs MUST refuse, never be
repaired or silently passed to a convenient older validator.

The [historical archive](../historical/pre-grail/README.md) preserves available
published bytes. Absence of an original historical 1.0 SPEC in this checkout
does not erase its meaning or justify inventing bytes. The withdrawn
[unpublished experiment](experimental/README.md) is not normative or safe
first-Grail authority; its opt-in regression results MUST NOT count as
first-Grail acceptance.

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

First Grail consists of:

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
fallback. In particular, first Grail disables remote model submission,
network/loopback access, arbitrary imports/host tools/code, external effects,
partitioned execution, live native rebinding/migration, timed physical
erasure, unqualified runtimes and claims of learned semantic capability.

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

Rights for capture, local synthesis, model submission, retention,
redistribution, adoption, materialization and execution MUST be separate.
Authorization for capture is not authorization for model submission; private
storage is not permission to redistribute; a retained artifact is not a grant.
All relevant current rights and inherited restrictions MUST be checked before
the first source access, decoding/synthesis action, output write or egress.
The controller MUST receive trusted current time explicitly and enforce its
durable clock floor and policy expiry. Candidate timestamps or a frozen
fixture clock MUST NOT supply live authorization freshness.

A denied/expired capture MUST NOT stat, enumerate, open, hash or parse the
source. A denied synthesis MUST NOT decode source content. An unsupported
model/network/host operation MUST fail before credentials or transport are
touched. First-Grail demos use explicit external synthetic policies; they
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
stats and is disabled in first Grail. A producer requiring a stronger
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
plaintext was omitted. First Grail has no public redistribution path.

Retention and deletion semantics MUST be honest. Immutable history and
backups do not provide guaranteed recall or physical erasure. First Grail
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
reads are empty in first Grail; adding one cannot silently broaden the sandbox.

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

First Grail permits one trusted local writer. A private controller directory,
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

## 10. Inert projections, portability and materialization

Projections are deterministic data views of controller-accepted history,
never sources of capability authority. Rebuilding data MUST NOT rebuild
permissions from learned adoption records. The only first-Grail materializer
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
reserved before work begins. Exhaustion, no-op/repeated state, oscillation
or ping-pong MUST terminate with retained evidence, not recurse unboundedly.
Continuation state and idempotency MUST survive restart.

The reference defaults to eight attempts, depth four, 256 frame slots and
1 MiB aggregate captured octets; hard ceilings are 128 attempts, depth 32,
512 frames and 64 MiB aggregate capture. Policy updates MUST NOT reset or
increase an existing root's budget. Final budget stops are durable and exact
retries reuse the stop rather than consume unbounded new stop frames.

Historical RAPP integrity and scoped historical receipts MUST remain
inspectable even when the old application evaluator is unavailable.
Unavailable historical replay MUST be labeled unavailable, not false and not
freshly verified. New execution requires current qualification and rights;
an old pass or a valid chain cannot satisfy those gates.

## 12. Higher mechanisms: explicit gates or refusal

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
First-Grail live migration is disabled before source access. Missing original
spec bytes or native mapping cannot be guessed or solved by re-labeling.

## 13. Blocking conformance and honest completion

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
unproven learned-capability refusal.

Completion MUST report each guarantee separately and scan nonzero emitted
canonical RAPP/1 frames. No single conformance verdict authorizes deployment.
Owner publication, independent anchors/signed registry adoption, genuine
snapshot/native adapters, protected monotonic hosting and production
execution/key-custody qualification remain distinct owner/engineering gates.
