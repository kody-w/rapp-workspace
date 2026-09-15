# Workspace Grail/1.0 candidate reference

The normative contract is [../SPEC.md](../SPEC.md), not this guide. All new
code is stdlib-only. The canonical RAPP/1 checkout must be explicitly
supplied; its current-main inspection commit, core files, authority chain and
selected materialization are verified before fixture execution.

## Frame Anything: iterative/branching evolution and conditional acceptance

```bash
python3 -B tools/frame_lens.py demo \
  --rapp1-path "<EXPLICIT_RAPP1_CHECKOUT>" \
  --fixture "<EXPLICIT_LOCAL_OBJECT>" \
  --context "<EXPLICIT_CONTEXT_DIRECTORY>" \
  --max-attempts 12 --max-depth 6 \
  --output .validation/framed-object
```

Omit `--fixture` to create the built-in six-input matrix: unknown workspace,
source tree, foreign agent manifest, structured document, binary file and
empty directory. The foreign manifest must first fail lens A, then consume
that refusal and independently observed container evidence in lens B to
succeed. Three inputs become candidates and three reach stable honest
refusals. The learner is not given fixture categories. `--context` is optional
and repeatable up to four explicitly supplied paths for branching; no context
path is inferred or traversed from source content.

`framing.py` captures only explicitly supplied local objects through bounded
no-follow reads. It does not decode native schemas or execute file/manifest
contents. Names remain opaque base64 octets; the source fingerprint is a
normal RAPP particle, not a new identity/hash domain. Small files are retained
inline, large files produce honest digest-only receipts, links are not
followed and special nodes are metadata-only.

`workspace-attempt` reads complete source/observation particles and checks its
member map. RW/1 workspace admission in this class requires an inline-verified
directory with at least two regular files and no links/special members.
Other cases yield a deterministic `workspace-unresolved` successor with a
reason. This valid refusal frame is not a compliant workspace. Even caller
approval cannot adopt it, and an unconditional project/copy cannot launder it.
`workspace-context-attempt` consumes complete source, observation, verified
refusal exhaust, context container and context observation. It binds
`repair_code` to the refusal and checks exact original-name/bytes membership.
Mismatch yields a retained contradiction; missing/ambiguous binding is a
partial unresolved mapping. It never edits an older refusal.

The command visibly prints source fingerprint, opaque frame, lens declaration,
declared reads, successor or refusal, verification, source preservation and
retained ancestry. `frame-anything-report.json` and `phases.json` retain the
proof. Source/outcome copies remain available for further lenses.

`iteration.py` retains loop declarations, candidate requests, each attempted
execution/dedupe decision, data exhaust and explicit stops. Request order is
`(depth, work_key.hash, request.frame_hash)`. Work keys ignore cosmetic lens
labels, logical ticks and envelope rewrapping. State commitments combine
normalized results with independently derived information. Repeated states,
lens ping-pong and repeated no-information attempts converge rather than run
forever. New claimed-progress messages or rewritten diagnostics cannot create
progress. Genuine new verified inputs may reopen bounded exploration.

Limits default to 12 attempts/depth 6/two no-progress attempts, with hard
ceilings of 128 attempts, 128 admitted requests and depth 32. Termination
distinguishes adopted verification, missing owner authorization, attempt/
depth budgets, stable fixed point and explicit contradiction/refusal.
All attempted and remaining pending parent sets survive restart. A stop is
relative to the supplied frontier/horizon, not proof that future repair is
impossible. Trusted planner/reviewer callbacks are not executable model data.

Supplied objects are never automatically adopted; candidates need separate
consent. Only the built-in fixture harness simulates independent owner review.
Exit 0 means a supplied candidate was framed or the matrix passed; exit 2 is
successful framing with an unresolved supplied object; exit 1 is a failure.
RAPP/1 scanner COMPLIANT means frame integrity, not workspace adoption.

Limits: 128 entries, 64 regular files, depth 16, 16 MiB/file, 64 MiB aggregate,
five seconds and 4 KiB inline retention per file. Output cannot overlap the
source. No native identity, authority, semantics, taxonomy or provider adapter
is inferred. `demo.py`/`native_lens.py` remain supporting synthetic
directory-only regression helpers, not the headline CLI.

## Full conformance

```bash
python3 -B tools/frame_lens.py conformance \
  --rapp1-path "<EXPLICIT_RAPP1_CHECKOUT>" \
  --output .validation/workspace-grail-conformance
```

Run from the repository root. Conformance runs Frame Anything, including
expected refusals, as its headline proof alongside all prior regression tests.
The report gives actual test/scan counts,
nonzero emitted frames and streams, restart equivalence, manifest commitment
and explicit non-activation status. A repeated unchanged run is byte-identical.
`schemas` and `pins` check generated contracts. Regeneration is explicit:

```bash
python3 -B protocols/rapp-workspace/1.0/reference/schema_source.py
python3 -B protocols/rapp-workspace/1.0/reference/pins.py --write --write-index
```

The second command updates `protocols/index.json` from the new manifest.
Do not regenerate pins while verification is running. `--capture-provenance`
is an explicit maintainer action requiring both public source checkouts, not
a conformance step or automatic moving-main update.

## API

Import `common.Parent`, `workspace.Workspace`, `workspace.LocalConsent` from
this directory. The constructor is:

```text
core = Parent(explicit_canonical_checkout)
workspace = Workspace(core, existing_or_newly_minted_rappid, world_id, consent)
```

Only a genuinely new workspace may mint a new identity using
`core.r.mint_rappid`. UUID entropy substitution in the test `Fixture` is
**test-only**, never a production mint, key, or deterministic identity scheme.

| Method | Meaning |
|---|---|
| `birth(utc)` | Append the sole local seed; a migration extends verified old root history. |
| `framing.frame_object(workspace, path, utc)` | Frame one explicitly supplied local object opaquely and emit a linked observation; never change its identity or bytes. |
| `framing.synthesize_attempt(core, source, observation, tick)` | Produce an evidence-bound workspace-attempt program, not an unconditional workspace projection. |
| `framing.synthesize_context_attempt(core, source, observation, exhaust, context, context_observation, tick)` | Synthesize a candidate lens using verified refusal information and new explicit context. |
| `frame_anything.run_frame_anything(core, output, fixture=...)` | Run the visible supplied-object flow (no automatic adoption), or the synthetic acceptance matrix when no fixture is supplied. |
| `iteration.LensLoop.create(workspace, root, utc, max_attempts=12, max_depth=6, no_progress_window=2)` | Start one fixed-root bounded iteration lineage. |
| `loop.submit(lens, sources, contexts=..., parents=..., strategy=...)` | Retain a candidate request for select/reapply/verified-descendant execution. |
| `loop.step()` / `loop.run(planner=..., reviewer=...)` | Deterministically execute or dedupe; failures become replay-verified exhaust rather than disappearing. |
| `loop.finish()` | Append the truthful stop reason and retain all attempts/pending branches. |
| `observation(subject, shape, metadata, utc, ...)` | Record already-authorized opaque metadata; does not read a native store. |
| `native_lens.observe_native(workspace, fixture_root, utc, ...)` | Boundedly capture explicitly supplied synthetic files, then emit opaque source and linked observation frames; no source writes. |
| `native_lens.synthesize_program(core, observation, source, tick)` | Pure evidence-derived structural IR compiler; no file I/O, provider parser, identity mint or consent. |
| `lens(label, observations, program, proposer, utc, synthesis=...)` | Store a candidate declaration with the exact runtime-manifest pin. |
| `reads_payload(lens, sources, contexts)` | Recompute every declared content-particle read; reject unused contexts. |
| `execute(manifest)` | Pure sandbox IR trial; no frames, native I/O, shell or model calls. |
| `mutate(lens, sources, utc, ...)` | Emit reads, an inert derived successor, and preservation receipt. |
| `evidence_payload(receipt)` | Repeat execution and actual negative refusals; claims no universal equivalence. |
| `adoption_payload(candidate, evidence)` | Propose an exact CAS-bound decision, not grant it. |
| `route_payload(target, action)` | Propose selection, suppression, or explicit re-add. |
| `append(payload, utc, stream=...)` | Verify the parent frame and profile semantics before appending. |
| `dimension(stream, parent, label, utc)` | Child genesis under a retained parent; each dimension is its own RAPP stream. |
| `scan_payload`, `report_payload` | Deterministic sparse/baseline intent and report generation. |
| `merge_payload` | Conflict-preserving fidelity report, never winner selection. |
| `reattach_payload` | First noncontradicting candidate or dry hole; no automatic activation. |
| `membrane(source_workspace, ref, direction)` | Modeled exact-allowlist public read; private egress always refuses. |
| `projection()` | Rebuild cache from retained adoption/routing history, retaining historical adoptions. |
| `checkpoint()` | Host frontier to protect independently, not portable authority. |
| `save(relative_destination)` | Locked local immutable frames, append-only history and disposable registry cache. |
| `Workspace.load(core, destination, consent, checkpoint, ...)` | Reverify history, receipts, consent, bytes and frontier; ignore registry cache. |

`LocalConsent(owner, decisions, public_reads)` is a trusted **caller** input.
The owner must independently approve the exact `core.particle(decision)["hash"]`
before it enters `decisions`. Never populate it by reading a candidate,
history's `authorized_by`, the generated registry, or model output. The
fixture intentionally simulates this external owner action; there is no
remote authorization claim. `rapp1-owner-policy` mode refuses because this
reference does not implement that signed adapter.

Content reads refer to the frame payload, or the verified canonical result
particle inside `derived-frame`. The whole object uses pointer `""`; arbitrary
candidate programs cannot access the filesystem. A lens can consume another
lens's content and produce an inert candidate lens, which needs its own
qualification and adoption before use in accepted projections.

## Explicit one-estate pre-Grail migration

```text
selection = dict(source_generation="pre-grail",
                 source_spec="rapp-workspace/2.0",
                 source_spec_sha256="<EXACT_ARCHIVED_SOURCE_SPEC_SHA256>",
                 legacy_frames=exact_retained_root_frame_octets)
plan = plan_migration(core, explicitly_authorized_workspace, consent, frozen_utc, **selection)
# Independent owner review/approval of core.particle(plan)["hash"] occurs here.
migrate(core, explicitly_authorized_workspace, independently_updated_consent, frozen_utc,
        checkpoint=protected_checkpoint_for_repeat_or_restart, **selection)
```

Supported source labels are pre-Grail 1.0, 1.1 and 2.0; they are experimental
migration inputs, not normative Grail predecessors. This function does not
scan for estates. The source generation and label are explicit. For 1.1/2.0,
the source hash must match an archived SPEC variant. No historical 1.0 SPEC
was found in this repository, so its source hash must be `None`—never the new
Grail 1.0 hash. This honestly limits that claim to metadata/byte preservation.

The existing identity must contain a canonical RAPPID and `world_id`.
A missing version/schema marker may be bound by the exact owner-approved
plan; it is not added to or rewritten in the source. A missing world cannot
be inferred. Existing Grail identity/seed markers refuse this lane.
New payloads carry `generation:"grail"` and saved identity metadata carries
`workspace_generation:"grail"`; neither is a signature.

The source's declared
root `frames` directory (default `frames/`) must match the complete supplied
frame list. Other project histories and unknown provider data remain
unchanged baseline evidence. The function snapshots the authorized workspace
without following symlinks, adds only `.workspace-grail`, continues the original
estate stream, and checks unchanged bytes, modes, paths and symlink targets.
It does not traverse pointers in the old registry. Full baseline reads are
not authorized by merely knowing the workspace path.

The old registry remains in place with its exact commitment in the migration
record. This preserves path/identity/suppression evidence without pretending
to understand every legacy schema. The Grail projection references that
migration; unknown legacy routes remain unselected. It does not implement a
live replacement UI for all previous providers. Each call is bounded to
one estate, 4,096 entries, 16 MiB per file and 64 MiB aggregate baseline.
The plan is read-only, and migration fails before writes without independent
exact consent. Repeating needs the original frozen UTC/selection and protected
checkpoint, not a new inferred seed.

## Native metadata-only eggs

`metadata_egg(workspace, [organism_id, neighborhood_id, estate_id], utc)` creates
and verifies native RAPP/1 nested containers in memory. It includes only
inert artifact identity, fixed soul text and the current registry projection.
The three artifact identities must be distinct from the live estate.
The receipt is separate from the native manifest; no new variant or egg
identity exists. Round-trip is tested; extraction never runs code or binds
routes. Metadata and its graph remain GODD and are not published.

## Storage and threat boundary

Frames are stored under `streams/<safe-RAPPID-locator>/frames/<seq>.json`;
locators are reversible routing names, not alternate identities. Exact
fork evidence is separately retained. History is the append-only selection
log; immutable supporting objects are written first and a locked prefix CAS
updates history, then the registry cache. Interruption can leave unselected
supporting objects; they must not silently become selected history.

Readers refuse unsafe links, hardlinks, path escape, changed observed file
identity, byte tamper and unavailable dependencies. This POSIX reference is
bounded to 8,192 frames/16 MiB history, 128 entries per projection and 32
simultaneous dimension levels; these are explicit resource deferrals, not
permission to trim ancestors. It is not distributed storage, Byzantine
consensus, full rollback-resistant hosting, or a hostile-process sandbox.

The canonical scanner proves emitted local frame integrity—not signed owner
authorization. There are no live provider adapters, network endpoints,
model-assisted synthesis, publication, key custody or live estate mutations
in the conformance path.
