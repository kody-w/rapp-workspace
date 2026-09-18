# RAPP Work SDK/1

**Profile ID:** `rapp-work-sdk/1`

**Status:** additive reference integration profile.

RAPP Work SDK/1 installs a local, offline-first `.rapp-work/` control sidecar
beside an existing workspace. It does not replace, rename, migrate, copy, or
reinterpret the workspace, its RAPPID, its world, its native files, or the
normative `rapp-workspace/1` protocol.

## 1. Parent and sibling pins

This profile is subordinate to `rapp-work/1`, which remains subordinate to
RAPP/1. The exact parent repository, commit, path, SHA-256, byte count, and
vendored inspection bytes are pinned by `parent-pin.json`.

The checked-in parent is the accepted canonical `kody-w/rapp-1` commit and
exact `protocols/rapp-work/1/SPEC.md` bytes. Any future replacement requires a
reviewed profile update, an explicit forward update plan, retained source
profile bytes, and new conformance evidence. A runtime MUST NOT resolve a
branch, tag, latest release, network response, or compatible-looking profile
in place of the exact known pin.

`rapp-workspace/1` is a sibling product protocol. This profile records its
existing core spec and manifest hashes only to prove non-interference. It does
not inherit Workspace/1 authority or alter any Workspace/1 identity, spec,
schema, manifest, reference, or prototype byte.

## 2. Sidecar boundary

The only default installation target is `.rapp-work/` under an explicitly
selected existing workspace root. A conforming install:

- reads `rappid.json` without following symlinks;
- preserves its exact bytes, RAPPID, declared world, and workspace spec;
- uses directory descriptors, `O_NOFOLLOW`, and pre/post-`fstat` checks for
  native identity, sidecar, generation, profile, discovery, and pointer reads;
- writes no native workspace content;
- copies no native workspace content into the sidecar;
- creates a complete private temporary generation before activation;
- activates the initial sidecar and each new generation with an atomic
  no-replace rename that refuses a raced destination;
- uses an atomic compare-and-swap exchange for `install.json` updates; and
- performs no network access.

Platforms without the required no-follow directory-descriptor reads and atomic
no-replace/exchange rename primitives fail closed before activation. A
path-check-then-open or overwrite fallback is not conforming.

The sidecar contains only profile metadata, discovery metadata, install state,
and update receipts. It is not a workspace snapshot, package cache, authority
store, publication queue, or native application binding.

The installed layout is:

```text
.rapp-work/
  install.json
  generations/
    <exact-rapp-work-commit-pin>/
      profile.json
      discovery.json
      update.json              # forward updates only
```

Files are canonical JSON except `profile.json`, whose exact checked-in bytes
are copied and pinned per release. Every historical generation retains its
original profile and discovery bytes. The current profile retains the exact
path, byte count, and SHA-256 of every known historical source profile, so an
older sidecar is verified against its own release bytes rather than the
updater's current profile. On POSIX, the sidecar is owner-only. Unexpected files,
unsafe file types, hard links, symlinks, unknown generations, incomplete
generations, inconsistent pointers, and conflicting bytes are refusals.

## 3. Installation and idempotency

Fresh installation selects only the profile's current installable pin.
Installing the same exact pin again is idempotent only after the complete
existing sidecar, workspace identity bytes, world, profile, discovery
document, generation digest, and history have been verified.

A changed discovery document, changed world, changed identity bytes, different
pin, incomplete state, or conflicting file is not repaired or overwritten.
The operator must use an explicit supported update or resolve the conflict
outside this protocol.

## 4. Updates

An update requires all of:

1. an existing completely verified sidecar;
2. an explicit known `from_pin` equal to the active pin;
3. an explicit known `to_pin` with a strictly greater profile sequence;
4. a deterministic update plan binding the current generation, target profile,
   known source profile, target discovery document, identity, world, and exact
   operations; and
5. the exact SHA-256 of that canonical plan supplied independently to apply.

The implementation prepares the complete target generation, activates it
without replacement, then compare-and-swaps `install.json` from the exact
verified old bytes. A raced generation or pointer is never overwritten. A
complete inactive forward generation left before pointer activation is inert
and may be resumed only with the same exact plan digest. A partial generation,
changed plan, fork, downgrade, unknown pin, or ambiguous recovery fails closed.

No update deletes history or native workspace bytes. No update may use a
network lookup to discover a newer pin.

If native `rappid.json` omits `world_id`, an installed sidecar may recover its
recorded world for inspection, verification, planning, and update. An explicit
world must match that recorded world. The binding is checked against the exact
native identity bytes and never writes the world into native content.

## 5. Discovery contract

Discovery is inert metadata. It may describe:

- organization pointers to existing `rapp-workspace/1` workspace-composite
  RAPP/1 wave addresses;
- Private Hive endpoint verification receipts;
- Private Hive vector verification receipts;
- plugins;
- skills; and
- static APIs.

Organization pointers are routing-only references. They copy no composite or
workspace content and grant no child capability.

Hive endpoint and vector receipts describe claimed or independently verified
observations. They never authorize publication, mutation, membership, key
release, transport use, or Hive authority.

Plugin, skill, and static API entries are discovery-only. Their presence does
not install, load, import, execute, activate, trust, or authorize them. A
locator and digest are evidence for a separate consumer, not an instruction.

Every discovery document fixes:

- `network_default: "disabled"`;
- `discovery_only: true`;
- `native_workspace_copied: false`;
- `publication_authorized: false`; and
- `grants_authority: false`.

## 6. Closed schemas

The four closed Draft 2020-12 schemas are:

- `schemas/profile.schema.json`;
- `schemas/install.schema.json`;
- `schemas/update.schema.json`; and
- `schemas/discovery.schema.json`.

Unknown members are refused. The reference additionally enforces
cross-document identity, pin order, digest, history, authority, and filesystem
invariants that JSON Schema alone cannot express.

## 7. Private Hive integration

Private Hive preparation calls the checked-in scaffold by default before
creating or accepting `.rapp-hive/`. The `.rapp-work/` and `.rapp-hive/`
sidecars remain independent. Neither grants publication authority.

The historical Private Hive migration command remains an explicit legacy
lane. It may preserve historical receipts and names, but it cannot relabel the
native workspace or any Workspace/1 protocol byte. Migrated project skills
include checksum-locked `rapp-work-sdk` and `rapp-private-hive` entries.

## 8. Conformance

A conforming implementation MUST prove:

- exact parent, profile, schema, and manifest pins;
- same-pin idempotency;
- atomic install and pointer update behavior;
- no default network access;
- no native workspace copying or identity mutation;
- exact forward-plan digest enforcement;
- actual prior-release profile/discovery fixtures and source-profile hashes;
- directory-fd no-follow reads, no-replace activation, and pointer
  compare-and-swap race refusal;
- refusal of symlinks, conflicts, partial state, downgrades, and unknown pins;
- discovery-only and no-authority semantics; and
- byte-for-byte stability of the existing `rapp-workspace/1` identity,
  normative manifest, spec, safety matrix, schemas, and reference pins.

Passing this profile's tests does not activate an estate, publish a Hive,
authorize a plugin, or qualify production key custody.
