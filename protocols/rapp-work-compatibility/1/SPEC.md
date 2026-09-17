# RAPP Work Compatibility/1

**Protocol identifier:** `rapp-work-compatibility/1`

**Parent:** `rapp-workspace/1`

**Substrate:** canonical `rapp/1`, unchanged.

**Status:** optional application profile and candidate reference. Estate
activation, Brainstem execution, owner adoption, signing infrastructure and
external effects remain separate.

MUST, MUST NOT, REQUIRED, SHOULD and MAY are normative.

## 1. Purpose and authority boundary

This profile carries one compatibility relationship between independently
versioned RAPP application endpoints. It defines inert candidates, signed
Compatibility and Exhaust Frames, content-addressed learned handshake
programs, repository mutation lineage, bounded Lens search and evidence for
later evolution.

The exact eleven-key RAPP/1 envelope, canonicalization, particles, waves,
RAPPIDs, signatures, registries and eggs remain exclusively RAPP/1. This
profile creates no envelope, hash, identity, signature, transport or registry
system.

A Compatibility Frame grants no authority, membership or effects. Local
validation and external controller adoption are mandatory. Repository
content, generated code, tests, summaries, model output and compatibility-
shaped data cannot supply policy, signing keys, activation or permission.

`rapp-workspace/1` remains byte-for-byte unchanged. Its external capability
controller, fresh trusted-clock checks, current activation, privacy,
restriction propagation, fork/rollback quarantine and disabled core effects
remain mandatory.

## 2. Generic AutoBest/CEO ancestor capability

The profile carries one exact inert `autobest:generic` capability:

- `agent.py` SHA-256
  `827f637c024e3fa1229148e5dcd78230a84ea3214283f899d22603741350f23c`,
  430291 bytes;
- `SKILL.md` SHA-256
  `5f8bd5b3c48858329f87ae3812dbc30ee604cb664985dc3d42a79e69d8bdfda8`,
  39139 bytes; and
- Tile schema `rapp-work-capability-tile/1`, subject
  `exact-agent.py-bytes`.

Both files are stored under SHA-256-addressed profile paths. A closed
capability manifest binds their RAPP/1 particle addresses, generic and
`microsol-ceo` profiles, external-global-Brainstem invocation, external-host
activation, successor-only mutation and `authority_from_presence:false`.

A `seed-capability-binding` Frame references an immutable Workspace/1 seed and
the exact capability/agent/Skill particles. An ancestor binding has no prior
binding. Descendants reference their parent and root ancestor. An implementation
change creates a capability successor that references the previous binding.
No binding overwrites the Workspace seed or grants execution.

File presence, importability, a Skill catalog entry or a valid content address
does not activate the capability. Current host authority, policy, scope,
budgets, runtime qualification and action-specific rights remain external.

## 3. One Compatibility Frame

When both endpoints speak RAPP/1, endpoint adaptation is represented by one
application Frame. Its payload binds:

- exact source identity, stream, qualification head, application profile,
  capabilities, repository commit and inventory;
- exact target profile and required operations;
- source Lens and target-finalizer `agent.py` artifacts;
- double-hotload receipts and global Brainstem host commitment;
- optional locked static program and generation receipt;
- scenario-relative coverage, gaps and unknowns;
- privacy restrictions and finite budgets;
- immutable source parents, mutation/reverse-lineage evidence, predecessor
  Compatibility Frame and triggering Exhaust;
- independent rehearsal, host, mutation and optional canary evidence; and
- `grants_authority:false`.

An initial Compatibility Frame has null predecessor and trigger. A successor
MUST bind both its predecessor and the exact Exhaust that justified reopening
the Lens. There is no hidden in-place mapping patch.

Missing or incomplete capabilities MAY produce honest partial compatibility.
Invalid signatures, key substitution, revocation, rollback, same-sequence
forks, privacy denial or source-scope violations are terminal for that source
and MUST NOT be laundered through a lower-quality fallback.

## 4. Operation-universal double-hotload Lens

The dynamic Lens is global Brainstem plus exact hotloaded `agent.py` bytes.
It is operation-universal over authorized framed application content.

Pass 1 hotloads the source/caller-selected agent. It may propose any successor
payload, code, data or repository tree shape required by caller intent,
including conversion, editing, addition, removal, movement, reorganization,
composition and complete program generation.

Pass 2 starts from a fresh isolated context, hotloads the target/finalizer
agent, consumes the exact Pass-1 candidate, fills and normalizes the target
contract and emits a target-shaped successor candidate.

Neither pass edits a signed source Frame or canonical envelope. Agents receive
application data only. The trusted host alone selects kind/stream/sequence/
UTC/predecessor, canonicalizes the output, computes hashes, accesses signing
keys and constructs/signs the RAPP/1 successor.

Each pass binds exact agent, Skill, prompt, policy, runtime, model receipt,
input, output, declared reads, restrictions and root budget. Native model
sessions, hidden reasoning, provider history, caches and temporary slot paths
are not protocol state.

## 5. File routing and isolated slots

File placement is the routing plane. There is no daemon, permanent per-Hive
process, mutable plugin registry or `brainstem.py` modification.

Every hotload uses a fresh private slot and exact regular files. The host MUST:

1. resolve content-addressed bytes;
2. publish into an absent slot without overwrite;
3. reject symlinks, hardlinks, devices, sockets, FIFOs and traversal;
4. verify type, mode, byte count and SHA-256 before and after placement;
5. hotload the captured verified bytes rather than an unchecked later read;
6. enforce inherited policy and budgets;
7. record file/input/output/policy/runtime receipts; and
8. unload and retire the slot.

Cleanup is best effort. No physical-erasure claim follows from unload.

## 6. Rehearsal, trace and typed Exhaust

Data sloshing is bounded rehearsal over exact fixtures and Exhaust evidence.
Every round performs both hotloads, target validation, applicable reverse
checks, controlled mutations and independent tests.

The sanitized learning trace records ordered:

`intent -> assistant proposal -> user correction -> measured result/failure
-> superseded assumption -> successor invariant`.

It stores no transcript, hidden reasoning, credentials, tokens, local paths,
native model sessions or raw private payloads. User corrections require
independent user/owner authority evidence; assistant proposals cannot be
relabeled user decisions. Normative state is the structured trace, never a
prose summary.

Typed Exhaust records the active Compatibility Frame, direction, exact source/
target heads, failed locus, missing coverage, information-loss class, consumed
bounds and privacy-safe diagnostics. It grants no patch or authority.

## 7. Static output program

Successful rehearsal MAY compile a deterministic, self-contained program
bundle whose `agent.py` is the hotload entrypoint. The bundle may contain
arbitrary code, data, schemas, fixtures, producer tests, documentation,
migration candidates and manifests.

The static program is not restricted to a declarative mapping IR. Arbitrary
deterministic code is permitted only with captured bytes, a pinned dependency
closure/runtime, independent tests, controlled mutants, target invariants and
host qualification.

Normal covered traffic hotloads the locked static agent with zero model calls.
The agent returns application output or typed Exhaust; it never constructs or
signs a RAPP/1 envelope and never self-modifies.

The Compatibility Frame cannot contain an agent hash while that agent embeds
the final Frame hash without a cryptographic cycle. A separate exact generation
receipt binds the approved Compatibility Frame, compiler/runtime/options,
output artifact and tests. The external controller atomically selects that
tuple.

Changed Compatibility Frame, compiler, runtime, schema or output creates a new
content address and version. Existing bytes are never overwritten.

## 8. Artifact bundles and Private Hive

Portable learned handshakes use an existing RAPP/1 egg manifest or a
`rapp-hive/1-object` whose kind is
`rapp-work-compatibility/1-handshake-program`.

The package binds exact agents, Compatibility Frame, static program, generation
receipt, schemas, fixtures, mutation evidence, coverage/gaps, restrictions and
provenance. Candidate-generated tests are producer evidence only. Independent
host/canonical tests and controlled mutants are required before selection.

GODD packages use sealed-room protection. Receiving or verifying a Hive object
does not install, activate, execute or grant authority.

MicroSOL ships only its concrete live subscription profile. It MUST NOT publish
a competing generic compatibility schema. It references this profile by exact
spec and Frame pins.

## 9. Repository mutation and bidirectional lineage

Immutability protects each ancestor occurrence, not descendant file contents.
A Lens MAY replace the complete successor repository.

Every source path/content head is exactly one of retained, replaced, moved or
removed. Every target path/content head is inherited, derived or new. Forward
and reverse maps bind all parents, transformation/generation receipts, selected
and omitted traits, file modes and loss classes.

Moves are explicit causal declarations. Splits and merges require exact
one-to-many or many-to-one references. Every source and target entry appears
exactly once in its directional partition.

Loss classes are:

- `lossless-direct`;
- `lossless-retained-delta`;
- `lossy-source-referenced`; and
- `lossy-unavailable`.

A lossless claim requires independent exact reconstruction of ancestor paths,
modes, bytes and inventory from the successor plus retained inverse artifacts.
A lossy reverse request emits Exhaust and preserves unavailable source refs; it
never fabricates data or claims round-trip compatibility.

The static output agent supports both directions within separately declared
coverage.

## 10. Mutation offers and transport

A complete successor MAY be projected through a pull request, Private Hive,
Federation or local transport. The offer binds exact parent refs, full successor
tree/egg, trait mutations, reverse ancestry, tests and compatibility agent.

Provider merge/close status is transport evidence, not RAPP authority or
ancestor rewrite. The receiving organization may adopt the complete result,
reject it, select traits or run another Lens. Trait selection produces a new
successor with fresh lineage and independent tests.

Wild adaptation can influence an organization seed only through a separately
verified crossing and atomic selection. No PR or local success automatically
mutates the seed.

## 11. N-Lens bounded search

One ancestor MAY fan out into independently pinned Lens Dimensions. Each may
emit a complete successor, trait candidate, alternative interpretation,
program/test bundle, refusal or unknown.

Compatible candidates MAY be crossed. Parents and rejected/pruned branches
remain immutable. A selected successor records exact contributing traits and
parents.

Default search limits are eight Lenses, four candidates per Lens, 32 total
candidates, cross width three, depth three, four rounds, beam width eight and
Pareto frontier 16. Hard ceilings are respectively 32, 16, 128, eight, eight,
16, 32 and 64. Existing roots may only lower them.

Dependency/incompatibility pruning, exact equivalence dedupe, root-scoped
shared-work reuse, beam/Pareto bounds, repeated-state and no-progress stops are
mandatory. Fitness is an integer evidence vector for one declared scenario,
never universal truth.

## 12. Recursive meta-evolution

The improvement ladder is:

`encounter/exhaust -> handshake successor -> Lens-agent/compiler successor
-> organization-seed trait candidate -> protocol-successor proposal`.

Every level retains immutable ancestors and exact causal refs. Rehearsal corpus,
hidden holdouts, controlled mutants, bounded canary, independent verification,
rollback and adoption are separate.

Generated tests cannot self-certify. Hidden holdouts are committed before
candidate generation and unavailable to candidate agents. Duplicate/derived
evidence counts once by root lineage. Competing implementations and minority
failures are retained.

No scalar confidence or automatic upward promotion is normative. Reward
hacking, corpus contamination, echo amplification, monoculture and catastrophic
forgetting are blocking failures.

Protocol evolution requires a new exact version/pin and separate registry
authority. Existing protocol bytes are never relabeled.

## 13. Bill SoftwareCo fixture

The first bound concrete fixture is the owner-approved private handshake:

- repository: `https://github.com/billwhalenmsft/softwarecoellc-vteam-hive`;
- inspected commit: `f66da3d879b53a439bc87de764d79f68ceec048a`;
- handshake SHA-256:
  `0c52264b81bf88dd8555defa9363a23d8eb8ef85c3c12f66ddcaaabfc85a8882`;
- source Lens SHA-256:
  `679fff9531c0c8b13457d594f746c45da28925a7c1be40473e8ca00823db8671`;
- target finalizer SHA-256:
  `c056339f90fdd4e604dbefa40291f1b7b22946d26749b36230bb3b29dd8e2296`;
- live qualification summary: two signed Frames and nine artifacts; and
- capability: partial read-only evidence/handoff, not membership or write
  authority.

The checked-in fixture uses synthetic Frames and no live private source bytes.
It proves exact package pins, two-pass captured-byte execution, deterministic
static generation, zero-model static use and mutation/refusal behavior. It is
evidence, not estate activation.

## 14. Prior art and non-authority

`UniversalDataConnectorAI@f2a978b` is conceptual provenance for staged unknown
source analysis, schema learning, synthesis, testing and registry. Its ambient
Azure storage/network, broad catches, time/random/MD5 identity, floating
confidence, auto-approval, simulated tests, mutable sessions and unqualified
generated code are explicitly excluded.

The preserved local generic one-Frame prototype and seven tests are candidate
source material only. Their MicroSOL schema identifiers and custom authority
implementation are not adopted.

Neither prior-art source is RAPP/1 conformance evidence.

## 15. Completion and conformance

Conformance MUST:

- validate every checked-in schema and manifest pin;
- verify nonzero actual canonical RAPP/1 Frames;
- verify exact Bill fixture/package pins;
- reproduce the fixture static agent byte-for-byte;
- execute covered static fixture traffic with zero model/effect calls;
- prove signature/head/history, coverage, restriction, budget and authority
  mutations fail;
- prove candidate/generated tests do not self-certify; and
- rerun the unchanged Workspace/1 core conformance.

Passing local conformance does not activate an estate, Brainstem, Hive
subscription, signer, model, tool, deployment or the checked-in generic
AutoBest/CEO seed capability.
