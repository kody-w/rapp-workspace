---
name: rapp-work-sdk
description: Install, verify, or explicitly update the additive offline-first RAPP Work SDK/1 sidecar for an existing RAPP Workspace without changing its identity, world, protocol bytes, or native content.
---

# RAPP Work SDK/1

Use this skill only for the additive `rapp-work-sdk/1` integration profile.
The normative profile lives at `protocols/rapp-work-sdk/1/SPEC.md`.

## Boundary

- The workspace already exists and owns its `rappid.json`, RAPPID, world,
  native files, and any Workspace/1 composite addresses.
- Installation writes only `.rapp-work/`.
- No native workspace file is copied into the sidecar.
- Network access is disabled by default and the reference performs none.
- Organization pointers are references to existing `rapp-workspace/1`
  composite wave addresses.
- Hive endpoint/vector receipts describe verification only. They do not
  authorize publication.
- Plugin, skill, and static API entries are discovery-only. Never import,
  install, execute, activate, or trust them because they appear in discovery.
- This profile does not alter or relabel `rapp-workspace/1`.

## Preflight

From this skill directory:

```bash
python3 -B scripts/scaffold.py --preflight
python3 -B scripts/scaffold.py profile
```

The checked-in `rapp-work/1` parent is the accepted exact canonical
`kody-w/rapp-1` commit and spec path. Report it exactly and do not resolve a
branch, tag, latest release, or network response in its place.

## Install and verify

Use an explicit workspace path:

```bash
python3 -B scripts/scaffold.py install --workspace /explicit/workspace
python3 -B scripts/scaffold.py verify --workspace /explicit/workspace
```

If native `rappid.json` has no `world_id`, supply `--world-id` for a fresh
install. Later inspection, verification, planning, and update may recover the
exact world recorded by the installed sidecar; an explicitly supplied world
must match it. The scaffold never writes that value into native content.

An optional `--discovery` file must satisfy the closed discovery schema and
all cross-document authority checks. Repeating a same-pin installation is
idempotent only if the complete sidecar and discovery bytes verify. Conflicts,
partial state, and symlinks refuse rather than being repaired.

## Explicit forward update

Never update implicitly. First produce the exact plan:

```bash
python3 -B scripts/scaffold.py plan-update \
  --workspace /explicit/workspace \
  --from-pin <exact-active-pin> \
  --to-pin <exact-known-newer-pin>
```

Then apply that exact plan digest:

```bash
python3 -B scripts/scaffold.py update \
  --workspace /explicit/workspace \
  --from-pin <exact-active-pin> \
  --to-pin <exact-known-newer-pin> \
  --plan-digest <exact-plan-sha256>
```

Unknown pins, wrong source pins, no-op transitions, downgrades, changed
discovery, changed plan digests, partial generations, and ambiguous recovery
fail closed.

Known older pins are verified against retained prior-release profile bytes and
their own retained discovery generation. The target generation uses the target
profile bytes, and activation refuses raced destinations instead of replacing
them.

## Handoff

Report the profile pin, canonical parent repository/commit/path/spec digest,
sidecar status, exact plan digest for any update, preserved workspace
RAPPID/world, no-network result, no-copy result, and every refused or
unresolved authority dependency.
