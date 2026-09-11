# RAPP Workspace

**A local-first workspace that carries its own AI capabilities and can grow into
a sovereign Private Hive without losing local data.**

RAPP Workspace is the workspace layer of the RAPP/1 family. Clone or share the
repository and GitHub Copilot CLI discovers its project skills automatically
from `.github/skills/`.

## The model

- **Local workspace:** the complete on-device workspace. Everything is
  local-only unless its owner explicitly selects it for sharing.
- **Private Hive:** the access-restricted, off-device portion of a workspace.
  Members—humans, AIs, agents, and services—organize their own areas and shared
  projects under the same RAPPID-based rules.
- **DOGG:** globally safe data. DOGG never contains PII.
- **GODD:** private data. Selected GODD may be shared inside sealed Hive rooms;
  the most sensitive GODD remains local.
- **Mother Hive:** one Private Hive's signed authority and canonical head.
- **Hive dimensions:** local devices, branches, and storage projections that
  converge back into their Mother Hive through Dream Catcher.
- **Hive Mind:** the universal singleton logical federation of sovereign
  Private Hives. It is one interoperable graph, not one owner, key, server,
  database, or globally writable head.

## Capabilities included with the workspace

| Project skill | Purpose |
|---|---|
| `.github/skills/rapp-workspace` | Operate append-only project frames, leases, handoffs, verification, and fork recovery. |
| `.github/skills/rapp-private-hive` | Migrate older workspaces without data loss, prepare selections, create signed authority, publish to qualified filesystems/NAS or private GitHub, and independently verify/pull the Hive. |

Copilot CLI loads project skills after the repository is trusted. In an
already-running session, use `/skills reload`.

## Update an older workspace

Run the migration script from a trusted clone of this repository:

```bash
python3 /path/to/rapp-workspace/.github/skills/rapp-private-hive/scripts/prepare_workspace.py migrate \
  --workspace /path/to/existing-workspace \
  --member-rappid 'rappid:@owner/member:<64hex>' \
  --hive-name my-private-hive \
  --world-id my-world
```

Migration is additive and identity-preserving. It snapshots and rechecks every
existing file and symlink, adds `.rapp-hive/`, and embeds the exact
checksum-locked Private Hive project skill at
`.github/skills/rapp-private-hive`. It refuses conflicting or unsafe existing
skill content rather than overwriting it.

## Local workspace manager

Create a private manager outside this public protocol repository, scan local
Git roots, and use its generated dashboard or CLI:

```bash
python3 tools/workspace_manager.py init \
  --workspace ~/RAPP-Workspace-Manager \
  --owner <owner-handle> \
  --rapp1-path ~/src/rapp-1
python3 tools/workspace_manager.py scan \
  --workspace ~/RAPP-Workspace-Manager \
  --root ~/Documents/GitHub \
  --rapp1-path ~/src/rapp-1
python3 tools/workspace_manager.py list \
  --workspace ~/RAPP-Workspace-Manager
```

The registry contains paths and RAPP identity metadata only. It does not copy
source, notes, or other content out of the routed workspaces. Discovered RAPP
identities are accepted only after canonical validation; symlinked identity
files are ignored.

## Deploy a Private Hive

After migration:

```bash
cd /path/to/existing-workspace
python3 .github/skills/rapp-private-hive/scripts/deploy_hive.py --preflight
```

Follow
[`DEPLOYMENT.md`](.github/skills/rapp-private-hive/DEPLOYMENT.md) for explicit
owner-key creation, authority initialization, approval, private filesystem/NAS
or private GitHub publication, and independent client verification.

The current deployment MVP intentionally refuses SharePoint, automatic GODD
sealing/key release, federation activation, owner rotation, and topology
mutation until those capabilities have separate verified adapters.

## Protocols

- [`SPEC.md`](SPEC.md) — `rapp-workspace/2.0`
- [`protocols/rapp-hive/1`](protocols/rapp-hive/1/SPEC.md) — sovereign Private
  Hive authority and Dream Catcher convergence
- [`protocols/rapp-federation/1`](protocols/rapp-federation/1/SPEC.md) — bounded
  galactic Hive Mind federation candidate
- [`docs/rapp-work.md`](docs/rapp-work.md) — RAPP Work business/compliance layer
- [`tools/append_frame.py`](tools/append_frame.py) — project-frame lease writer
- [`tools/workspace_manager.py`](tools/workspace_manager.py) — pointer-only
  manager for local Git and RAPP workspaces

RAPP/1 remains authoritative for identity, canonicalization, frames, hashes,
signatures, eggs, and registries. RAPP Workspace and RAPP Work add policy
without changing the eleven-key RAPP/1 frame envelope.

MIT.
