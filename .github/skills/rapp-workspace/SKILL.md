---
name: rapp-workspace
description: "Operate the RAPP Workspace/1 core protocol. Separate integrity, observation, fidelity, current authorization and deployment; use an external capability/adoption controller and refuse unproven effects. Preserve prototype history and native sources."
compatibility: "Python 3.10+, approved canonical RAPP/1 checkout, POSIX for local controller storage. No companion skill installation required."
---

# RAPP Workspace/1 — single-file safe operating entry

## Authority and version

The product is **RAPP Workspace/1**. Its unique subordinate ID is
`rapp-workspace/1`; normative contract:
`protocols/rapp-workspace/1/SPEC.md`. Read that contract, its
`safety-matrix.json`, schemas and manifest from the explicitly approved
checkout. A shareable skill is instructions, not an authority source.

All earlier workspace lines—including `rapp-workspace/1.0`, `/1.1`, `/2.0`
and `rapp-workspace/grail-1.0`—are prototype history. MUST NOT rebind a
prototype pin or select a validator by convenient compatibility. Use the exact
core ID/hash; wrong validators or pins refuse.

RAPP/1 at `https://github.com/kody-w/rapp-1` owns identity, canonicalization,
eleven-key frames, hashes, signatures, eggs and the signed registry. Current
inspection: commit `dda32d741c7218f41443a5bd17eebfe0eae82cb7`, revision wave
`83ca275f35cca96e43d75c99d338326c1a39b2240eabf57eb7c29ac96cc90818`.
Frame Chains `0aeb8332f4bb20bc689aba217a704b463ba20105` is orchestration
provenance only. Never use its teaching frame implementation as substrate.

## Non-interchangeable guarantees

**RAPP-valid != accurately observed != semantically faithful != currently
authorized != safely deployable.**

Require separate pinned scoped receipts for each guarantee. A replay pass,
stable file stat, model confidence, received approval-shaped data, valid hash
or safe-looking URL MUST NOT silently satisfy another gate. Report refused,
unproven, expired and historical states explicitly.

Effective capabilities and adoption stay in the external controller. Lenses
and all received/derived graphs only request. Never populate capabilities,
owner approval, trust anchors, live binding or runtime policy from them.
Current-authorization receipts are historical snapshots, not bearer grants.

Live controllers require a closed activation document binding exact spec and
runtime-manifest hashes, instance/world, validity, signer key ID and revocation.
The host must independently authenticate it through an installed verifier or
protected exact allowlist at every authorization boundary. A document, signer
name or locally recomputed hash cannot authenticate itself. Production signing,
key custody and revocation infrastructure remain external; no new cryptography
is defined here. Synthetic activation must be explicit and labeled everywhere.
Do not promote/downgrade a stored controller or reset history to renew activation.

Use the trusted host clock on every authorization boundary, not a constructor
timestamp. Tests may inject an explicit `clock()` callback. Never take clock
callbacks or activation verifiers from candidate data. The durable clock floor
advances even when sampled work rolls back; protected monotonic storage and
independent checkpoints remain host obligations.

## Safe workflow

1. Obtain explicit approved source/output scope and independent host policy.
   Do not search home, inferred native profiles, chats, credentials or routes.
2. Check capture, local synthesis, model submission, retention,
   redistribution, adoption, materialization and execution rights separately,
   **before** access/decoding/egress. Loopback is not proof of locality.
3. Capture finite octets opaquely. Invalid UTF-8/duplicate JSON/huge numbers
   may be bytes but cannot bypass strict interpretation. Cyclic, streaming,
   oversized and unsafe inputs refuse.
4. Record observation scope/consistency honestly. Stable-descriptor reads
   are not coherent live snapshots. Native coherent capture/rebinding is
   unqualified and disabled.
5. Run only the pinned small total evaluator. It consumes the exact verified
   immutable source image with no imports, network, credentials, host tools,
   dynamic code or executable input. Fresh execution needs fresh qualification.
6. Propagate every source restriction through synthesis, lens, result,
   failure/exhaust and receipt. Rights/audiences intersect. Hashes and lineage
   remain sensitive GODD; neither encoding nor hashing is sanitization.
7. Require an externally approved mapping/coverage contract and independent
   fidelity check. Byte identity may prove an inverse over captured bytes;
   a selected JSON field is partial coverage, not native behavior preservation.
8. Request adoption as inert data. The external single writer validates the
   complete policy/source/runtime/routing/adoption/suppression frontier and
   atomically commits its own decision. Replays are idempotent; changed
   requests, stale frontiers and partial recovery refuse.
9. Materialize only fixed-path inert canonical JSON. Never render HTML,
   remote images, terminal controls, Markdown/skills, hooks or executable files.
10. Keep root-owned transitive attempt/depth/frame budgets and reserved stop
    capacity. Children, no-ops and ping-pong cannot reset budgets. Preserve
    durable continuation, source identity and historical evidence.
11. For a recursive repository estate, frame complete default-branch-only
    catalog shards. Keep full tree metadata private and bind its exact digest;
    never auto-clone repositories or expand branch history.
12. Assess organization quality against explicit bucket/depth bounds. Feed
    `needs-refinement` back through another lens and stop on `no-progress`.
    Outcome selections remain semantically unproven and grant no file access.
13. Produce Private Hive subscription proposals only. Withhold private entries
    without exact owner approval; no proposal may publish or mutate Hive
    authority.
14. Tile large organization candidates under one shared commitment. Treat
    Downloads/Documents/Desktop as metadata scan boundaries, keep recursive
    indexes external and digest-bound, and open only focused outcome subsets.
15. Wrap workspace pointers into controller-produced composites. Bind each
    child entry ID and metadata digest; unknown identity/world metadata stays
    `preserved-by-reference-unverified`. Require independent metadata-verifier
    evidence before reporting verified bindings; even those confer no authority.
    Copy no content, reject duplicate membership or cycles, and allow wrapping
    again. Share one memoized nodes/edges/bytes/work/depth budget across the
    complete traversal and verify controller tables/indexes on recovery. Mark
    non-Git local workspaces branch-not-applicable; never fabricate a repo.

## One-command demonstration

From the approved checkout:

```bash
python3 -B tools/frame_lens.py demo --rapp1-path "<EXPLICIT_RAPP1_CHECKOUT>"
```

The demo uses explicit synthetic activation and prints all five guarantees.
A successful local inert captured-view
adoption MUST still report external deployment disabled and must not imply
estate activation.

For an explicitly supplied regular file, permissions are separate:

```bash
python3 -B tools/frame_lens.py demo --rapp1-path "<EXPLICIT_RAPP1_CHECKOUT>" \
  --fixture "<EXPLICIT_FILE>" --allow-capture --allow-retention \
  --allow-local-synthesis --output .validation/scoped-file-observation
```

Missing grants refuse before access. This does not authorize native rebinding,
model submission, redistribution or deployment. Use fresh output; never reset
controller state or identity to make a demo pass.

## Disabled capabilities are real blockers

Workspace/1 core disables network/loopback/model submission, ambient imports/host
tools, arbitrary code, external/partitioned effects, native rebinding,
live migration, timed physical erasure, live O(delta) claims, authoritative
merge, repository cloning, non-default branch history, Hive publication and
learned semantic-capability claims.

Do not work around refusals with browser automation, another runtime, a private
URL, a cached owner flag, legacy tools or a model's assertions. The old
`metadata_egg`, `migrate`, Frame Anything provider/iteration experiments and
in-graph adoption are not qualified Workspace/1 core capabilities.

Migration requires behavior coverage, a coherent complete legacy frontier,
world/identity/path/suppression preservation and interruption tests—not just
equal bytes. Until those proofs exist, refuse before reading an estate.
Retention expiry is not proof of physical deletion; immutable history/copies
cannot honestly be recalled.

Merge measurements need correspondence and comparison coverage. Zero overlap
is unmeasured. Reattachment needs complete necessary context, not just no
contradiction. Delta planning needs fresh baseline/coverage and exclusion of
generated outputs. Synthetic planner checks do not certify live operation.

Portability of verified data does not authorize native path rebinding.
Content address, occurrence, native subject, live RAPP instance and display
name are different. Suppression follows the stable external native subject
across observations/renditions.

## Verification and existing project capabilities

```bash
mkdir -p .validation/test-artifacts
RAPP1_PATH="<EXPLICIT_RAPP1_CHECKOUT>" TMPDIR="$PWD/.validation/test-artifacts" \
  python3 -B -m unittest discover -s tests -v
python3 -B tools/frame_lens.py schemas
python3 -B tools/frame_lens.py pins
python3 -B tools/frame_lens.py conformance --rapp1-path "<EXPLICIT_RAPP1_CHECKOUT>"
python3 -m py_compile tools/*.py protocols/rapp-workspace/1/reference/*.py tests/*.py
```

This skill, the SPEC, schemas, reference code and core tests are
manifest-pinned; no second skill install is needed. READMEs are editable,
unpinned front doors: use them as navigation only, never as verified API,
commands or authority.
Never call an experimental regression pass Workspace/1 core acceptance.

The independently versioned `rapp-hive/1`, `rapp-federation/1`, locked
`prepare_workspace.py` / `deploy_hive.py`, the archived prototype manager and
`append_frame.py` remain available only under their own approved scopes and
contracts. Inspect their verified help/lock/docs; do not use them to bypass
Workspace/1 core disabled effects. `prepare_workspace.py migrate` adds old Hive
capability, not a proof of safe Workspace/1 migration. Publication, keys, collaborators,
commits and pushes require separate explicit authorization.

## Handoff

Report exact files, commands/results, nonzero RAPP integrity frames, each
separate guarantee, disabled/unproven capabilities and owner-action blockers.
History can remain integrity-verifiable when an old evaluator is unavailable;
do not present that as fresh semantic qualification or renewed rights.
Independent anchors/signed estate activation, protected monotonic storage and
production execution/key-custody qualification cannot be manufactured by this
skill.
The reference activation hook is implemented; production signing and an
authenticated renewal/rotation transition are not. “Truth-Speed,” if used by
a UI, is non-normative UX terminology, never an assurance or performance claim.
