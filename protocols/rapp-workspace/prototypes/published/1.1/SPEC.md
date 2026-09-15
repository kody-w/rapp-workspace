# rapp-workspace/1.1 — the private workspace protocol for the rapp/1 family

> One owner, many worlds. A **RAPP Workspace** is a private, local-first vault
> that an AI keeps organized on the owner's behalf — so chaotic, organically
> grown work scattered across repos and files collapses into one place that
> never disorganizes again. Each workspace is scoped to **one world** (one
> use-case domain); an owner may run several, routed by use-case and timeframe.
> A workspace may be operated **solo** or by a **team (hive)** — including a
> distributed team sharing one private remote — without ever losing the
> append-only, hash-verified history that makes it rapp/1.

`spec_id: rapp-workspace/1.1`

This is a rapp/1-family protocol. It builds on `rapp/1` (frames, §6 identity,
canonical hashing — see the `rapp-1` reference repo) and the one-brain ruling:
one knowledge, a public face and a private face.

**1.1 over 1.0:** names the shared home the **RAPP Workspace store** (generic —
any private, access-controlled remote inside the world's boundary), and adds §9
**Distributed operation**: multi-operator concurrency carried by the frame
protocol's own lease model, with deterministic fork detection and append-only
recovery. 1.0 instances are conformant 1.1 instances.

---

## 1. What a workspace is

A **private, local-first** organizing vault (a folder of Markdown + data) that
an AI operates as chief-of-staff. It holds strategy, planning, portfolio,
projects, reference, and real (PII-bearing) data. It is **never published**;
its public projections are separate, PII-free artifacts.

Every workspace has a **mode**:
- **`solo`** — one owner.
- **`hive`** — a team. Same protocol, plus membership, roles, and a
  shared-vs-personal data split (§4a).

## 2. Identity

Each workspace has a keyless rappid (`rapp/1 §6`):
`rappid:@<owner>/<workspace-slug>:<64hex>`, minted once and stored in
`rappid.json` at the workspace root (mint-once: on read of an existing
`rappid.json`, reuse the stored value — never re-mint). Major workspace events
(creation, a big reorg, a world-boundary change) MAY be sealed as `rapp/1`
frames; day-to-day note edits need not be.

## 3. Anatomy

**Required:**
- `CLAUDE.md` (or your AI's operating file) — who the owner is, how the AI
  behaves, a question→doc routing table, the world's rules, the privacy guard.
- `HOME.md` — the command-center dashboard.
- `<PERSONA>.md` — the owner/principal profile.
- `where-everything-lives.md` — the map of the world's machinery.
- `README.md` — a loud **PRIVATE / NEVER PUBLISH** guard.
- `rappid.json` — the workspace identity (§2).

**Standard sections as the world needs:** `strategy/`, `portfolio/`,
`projects/`, `reference/`, `people/`, `meetings/`, plus world-specific ones.

**The frame authority:** a `rapp-projects/` directory (§8) when the workspace
tracks project state as rapp/1 streams — required for hive/distributed mode.

## 4. The two-faces data layer

Data with PII follows the one-brain ruling — one truth, two faces:
- **The private face**: the owner's full, real data, kept inside the workspace,
  local-only, ideally generated from workspace content so it stays in sync.
- **The public face**: a PII-free static application (the "bones"). The owner
  injects the private data locally, client-side; the data never leaves the
  machine; only the empty shell is public.

A workspace that surfaces data through an app MUST use this pattern — never
paste private data into a hosted form, never commit it anywhere public.

## 4a. Hive mode — team workspaces

A **hive** is the same protocol operated by a team. It adds:
- **Membership** — a `members` list in `rappid.json`, each
  `{rappid, alias, role}` with role `owner` / `member` / `viewer`. The owner
  stays sovereign (§6).
- **Shared vs personal data** — the private face splits into **shared** (the
  team's common data) and **personal** (per-member). The public face stays
  PII-free for both.
- **The workspace store** — the hive shares through a **private,
  access-controlled store scoped to its own world**: a private git remote
  inside the world's boundary (and optionally a private artifact/cubby store).
  A hive never shares through a store belonging to a different world.
- **Still private.** A hive is shared among its members privately; it is not
  public.

Solo is the default; a workspace becomes a hive by declaring `mode: hive` and a
`members` list. Everything else is unchanged.

## 5. The world boundary

Each workspace is scoped to **one world** and never bleeds into another:
content from world A never enters world B's workspace, its public surfaces, or
its store. Every workspace (and nested cell) declares a **`world_id`** — the
hard isolation domain — and optionally finer **`axes`** for routing. The rule:
**slosh within, contain across** — pre-enrich the AI freely with context from
inside the world; never read or write across a `world_id`.

### 5a. Nested workspaces (matrix projects)
A project needing isolation along several axes at once is a **matrix**: a
parent workspace with one nested cell per axis-combination, each its own
`world_id`, so content never sloshes between cells.

## 6. Privacy & sovereignty (conformance)

- **Local-only by default.** No git remote for a workspace holding PII. If a
  remote is added it MUST be private, access-controlled, **inside the
  workspace's own world**, and gated by a fail-closed pre-push scan (§9.5).
- **Owner sovereign.** The AI organizes and proposes; the owner decides. No
  irreversible or outward action without owner consent.
- **PII stays local.** Any output leaving the machine strips names/PII.
- **Never publish the vault.** Public projections only.

A workspace that keeps §3, §4, §5, and §6 is conformant. A hive additionally
keeps §9.

## 7. The workspace manager

An owner runs several workspaces; a **manager** routes to the right one by
use-case, timeframe, and mode. The manager holds only a **registry of
pointers** (name, mode, world, path, rappid, use-case tags) — never content —
so routing never crosses a boundary.

## 8. RAPP Projects — the frame authority

Project state lives as **rapp/1 frame streams**: one directory per project,
`projects/<slug>/rappid.json` + `projects/<slug>/frames/*.json`, where each
frame is an 11-key rapp/1 frame (see the rapp-1 reference implementation)
hash-chained by `prev` and content-addressed by RFC 8785 canonical hashing.

- **Frames are the authority; everything else is a projection.** Boards,
  indexes, status docs are derived and regenerated, never hand-merged.
- **Append-only.** Historical frames are never rewritten. Corrections append.
- **Atomic writes.** A frame is written to a temp file and renamed into place;
  a crash after the rename loses no committed work.
- **Frame kinds** (payload `event`): `project.genesis`, `work.punchin`,
  `work.heartbeat`, `work.checkpoint`, `work.status`, `work.handoff`,
  `work.takeover`, `work.punchout`, `project.verify`.

The reference writer (`tools/append_frame.py` in this repo) builds and verifies
every frame with the rapp-1 reference implementation and refuses to write a
frame that does not verify against the head.

## 9. Distributed operation (new in 1.1)

Multiple operators — humans and AIs — share one workspace through the store.
Concurrency rides the frame protocol itself; there are no side-channel locks.

### 9.1 Actors and leases
Every operator has an actor id (`RAPP_ACTOR`). Before appending working frames
to a project stream, an actor **punches in** (`work.punchin` with
`lease_expires_utc`). Heartbeats extend the lease; `work.handoff` and
`work.punchout` release it. While another actor holds an unexpired lease, every
mutating append to that stream is refused. `work.takeover` claims a stream only
after expiry or an explicit handoff. In distributed use, strict mode
(`RAPP_REQUIRE_LEASE=1`) makes the lease mandatory for all appends. A hive
workspace (`mode: hive` in `rappid.json`) forces strict mode. Actor ids are
unauthenticated free text and local frames are unsigned (rapp/1 mandates
signatures only on `net:` swarm streams): among conforming writers the lease
arbitrates; against a non-conforming writer the protocol guarantees
deterministic detection (§9.4 and the §9.5 append-only tripwire), not
prevention. Frame-signing for hive members is future work.

### 9.2 Partition by stream
Different projects are independent chains — operators on different streams
never contend. The lease arbitrates only same-stream writers.

### 9.3 The sync loop
pull (rebase) → verify all chains → punchin → work (frames at every phase
boundary) → punchout → pre-push gate → commit → push. Push soon after punchin:
an unpushed lease protects nobody.

### 9.4 Fork detection and recovery
Offline-first git allows the one race the lease cannot prevent: two operators
pull the same head, both punch in locally, both push. The collision lands as
two frame files sharing a `seq` — and chain verification detects it
deterministically (duplicate seq can never both verify against one head). A
forked chain MUST NOT be pushed further. Recovery is append-only: the frame
whose writer held the valid claim wins (older pushed punchin; then earlier
`utc`; then owner's ruling); losing frames are **quarantined** into
`frames/_forked/` (moved, never deleted — the collision is itself history);
the losing operator re-appends on the healed chain with a `recovered_from`
field naming the quarantined frame hash.

### 9.5 The pre-push gate
A hive's store is guarded by a fail-closed script run before every push:
secret-value scan over tracked files, credential-free remote URLs, local-state
exclusions honored, **every stream chain-verifies**, oversized-file and
world-boundary warnings. A failing gate blocks the push.

### 9.6 Compliance invariants (checkable)
- Every frame is built and verified by the rapp/1 reference implementation.
- Every stream chain-verifies end to end at any time.
- History is append-only; forks are quarantined, never rewritten.
- Leases, handoffs, and takeovers are themselves frames — the concurrency
  history is part of the auditable record.

---

*Reference implementation of the frame writer with lease enforcement:
[`tools/append_frame.py`](tools/append_frame.py). It depends on the rapp-1
reference implementation (`rapp.py`) — point `RAPP1_PATH` at your rapp-1
checkout.*
