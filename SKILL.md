---
name: rapp-workspace
description: Operate a RAPP Workspace — a private, local-first vault of Markdown + data that an AI keeps organized for one owner, with project history recorded as append-only, hash-chained rapp/1 frame streams and lease-based multi-operator concurrency. Use when asked to create, organize, join, or work inside a RAPP Workspace, to log project progress as frames, to punch in / heartbeat / hand off / punch out / take over a project stream, to verify or repair a frame chain, or to run the hive sync loop. Assumes no prior knowledge of RAPP.
---

# RAPP Workspace — operator skill

You are being asked to work inside (or set up) a **RAPP Workspace**. You do not
need to know anything about RAPP beforehand. Everything you need is here; the
protocol of record is `SPEC.md` in this repo and the reference tool is
`tools/append_frame.py`. When this skill and `SPEC.md` disagree, `SPEC.md` wins.

## 1. The idea in five sentences

1. A workspace is a **private folder** of Markdown and data for **one owner**
   and **one world** (one domain of work). It is never published.
2. An AI (you) acts as **chief of staff**: it keeps the folder organized, answers
   questions from it, and proposes; the owner decides.
3. **Project state is not a status doc.** It is a stream of small JSON
   **frames**, one file each, hash-chained so history cannot be silently
   rewritten. Boards, indexes, and status pages are regenerated from frames.
4. Before writing frames to a project you **punch in** (take a time-limited
   lease). Others are refused while you hold it. You **punch out** when done.
   Those lease events are themselves frames, so the concurrency history is part
   of the record.
5. A team ("**hive**") shares one workspace through a private git remote. The
   sync loop is: pull, verify every chain, punch in, work, punch out, gate, push.

## 2. Vocabulary

| Term | Meaning |
| --- | --- |
| **rapp/1** | The base protocol: 11-key JSON frames, canonical (RFC 8785) hashing, chains linked by `prev`. Reference implementation: `rapp.py` in the `rapp-1` repo. |
| **rappid** | A stable identity string, `rappid:@<owner>/<slug>:<64 hex>`. Minted once, stored in `rappid.json`, never re-minted. |
| **frame** | One JSON file under `frames/`, named `<seq padded to 20>-<frame_hash>.json`. Keys: `spec, kind, stream_id, seq, utc, payload, payload_hash, frame_hash, prev, prev_wave, sig`. |
| **stream** | One project's ordered chain of frames. Different projects are independent chains and never contend. |
| **payload.event** | What the frame records. Kinds: `project.genesis`, `work.punchin`, `work.heartbeat`, `work.checkpoint`, `work.status`, `work.handoff`, `work.takeover`, `work.punchout`, `project.verify`. |
| **actor** | Free-text operator id (`RAPP_ACTOR`), human or AI. Unauthenticated: the lease arbitrates among honest writers; forks by dishonest writers are detected, not prevented. |
| **lease** | Opened by `work.punchin` or `work.takeover` with `lease_expires_utc`; extended by `work.heartbeat`; released by `work.handoff` or `work.punchout`. Default 60 minutes. |
| **solo / hive** | `mode` in the workspace `rappid.json`. Hive adds a `members` list and forces strict lease mode. |
| **world_id** | The hard isolation boundary. Never read or write across it. |
| **store** | A hive's private, access-controlled git remote (plus optional artifact store), inside the world's boundary. |
| **two faces** | Private face: real data, local only. Public face: a PII-free static app shell that the owner loads private data into client-side. |

## 3. Setup (once per machine)

The reference writer is pure Python 3 standard library plus `rapp.py` from the
`rapp-1` repo. No pip installs.

```bash
git clone https://github.com/kody-w/rapp-1 ~/src/rapp-1          # the kernel
git clone https://github.com/kody-w/rapp-workspace ~/src/rapp-workspace  # this repo
export RAPP1_PATH=~/src/rapp-1        # where rapp.py lives (default ~/rapp-1)
export RAPP_ACTOR=<your-actor-id>     # e.g. alice, or claude-session-7
```

Where the tool finds projects: it uses `<dir containing tools/>/projects/<slug>/`.
Inside a workspace, copy it to `<workspace>/rapp-projects/tools/append_frame.py`
so projects live at `<workspace>/rapp-projects/projects/<slug>/` and hive
detection reads `<workspace>/rappid.json`. Or set `RAPP_PROJECTS_ROOT` to the
`rapp-projects/` directory explicitly.

## 4. Create a workspace from nothing

Required files (spec §3). Create them all; keep the README guard loud.

```
<workspace>/
  CLAUDE.md                 # or your AI's operating file: owner, behavior rules,
                            #   question→doc routing table, world rules, privacy guard
  HOME.md                   # command-center dashboard
  <PERSONA>.md              # the owner's profile
  where-everything-lives.md # map of the world's machinery
  README.md                 # "PRIVATE / NEVER PUBLISH" guard
  rappid.json               # workspace identity (below)
  strategy/ portfolio/ projects/ reference/ people/ meetings/   # as needed
  rapp-projects/            # the frame authority (required for hive)
    tools/append_frame.py
    projects/<slug>/rappid.json
    projects/<slug>/frames/*.json
```

Mint the workspace identity once (never re-run on an existing file):

```bash
cd <workspace> && test -f rappid.json && echo "exists — do not re-mint" || \
RAPP1_PATH=${RAPP1_PATH:-~/rapp-1} python3 - <<'EOF'
import json, os, sys
sys.path.insert(0, os.path.expanduser(os.environ["RAPP1_PATH"])); import rapp
owner, slug = "<owner-handle>", "<workspace-slug>"
rid = rapp.mint_rappid(owner, slug); assert rapp.rappid_valid(rid)
json.dump({"schema": "rapp/1", "rappid": rid, "kind": "workspace", "name": slug,
           "mode": "solo", "world_id": "<world-id>"}, open("rappid.json", "w"), indent=2)
print(rid)
EOF
```

For a hive, set `"mode": "hive"` and add
`"members": [{"rappid": "...", "alias": "alice", "role": "owner"}, ...]` with
roles `owner` / `member` / `viewer`. The owner stays sovereign.

Do **not** add a git remote to a workspace holding personal data unless it is
private, inside the world, and guarded by the pre-push gate (§8 below).

## 5. Daily operation: the frame commands

All commands: `python3 rapp-projects/tools/append_frame.py ...` from the
workspace root (or anywhere, with `RAPP_PROJECTS_ROOT` set).

```bash
# Start a project stream (once per project; refuses if it already exists)
--genesis --project <slug> --title "<title>" --goal "<goal>" [--owner "<who>"]

# Take the lease before doing work on that project
--punchin --project <slug> --actor $RAPP_ACTOR --intent "<what you are about to do>" [--lease-minutes 60]

# Record progress at every phase boundary (any non-lease event; payload is free JSON)
--project <slug> --event work.checkpoint --actor $RAPP_ACTOR --payload '{"step":"drafted spec","files":["spec.md"]}'
--project <slug> --event work.status     --actor $RAPP_ACTOR --payload '{"state":"blocked","on":"owner decision"}'

# Long session: extend the lease (default +60 min from now)
--heartbeat --project <slug> --actor $RAPP_ACTOR

# Release the lease
--punchout --project <slug> --actor $RAPP_ACTOR          # done for now
--handoff  --project <slug> --actor $RAPP_ACTOR          # releasing for someone else

# Claim a stream whose lease expired or was handed off
--takeover --project <slug> --actor $RAPP_ACTOR --reason "<why>"

# Read-only
--lease  --project <slug>     # FREE / LEASED <actor> until <utc> / EXPIRED — takeover allowed
--verify --project <slug>     # full chain verify
--verify --all                # every project; exit 1 if any chain fails
```

What the tool guarantees on every append: it re-verifies the whole chain, checks
the lease rules, builds the frame with `rapp.build_frame`, verifies it against
the head, and writes it atomically (temp file, fsync, rename). It refuses rather
than write anything that would not verify.

Refusals you will see, and what to do:

| Message starts with | Meaning | Do |
| --- | --- | --- |
| `REFUSED: <x> holds an active lease` | Someone else is working this stream. | Wait, ask for a handoff, or work another project. Never delete frames to get past it. |
| `REFUSED: cannot take over an ACTIVE lease` | Takeover only after expiry or handoff. | Check `--lease`; wait for expiry. |
| `REFUSED: no active lease to punchout` | You never punched in (or it lapsed). | `--punchin` first. |
| `REFUSED: strict lease mode` | Hive or `RAPP_REQUIRE_LEASE=1`: every append needs a lease. | `--punchin` first. |
| `CHAIN FORKED at seq N` | Two writers appended the same seq. | Stop pushing. Recover per §7. |
| `CHAIN BROKEN at seq N` | A frame was edited or the file is corrupt. | Restore from git; never hand-edit frames. |
| `CHAIN UNREADABLE` | Partial or corrupt frame file. | Restore from git or quarantine it. |

## 6. Rules you must keep (conformance)

- **Frames are the authority.** Regenerate boards/indexes/status docs from
  frames. Never hand-merge a projection back into history.
- **Append only.** Never edit, rename, or delete a frame file. Corrections are
  new frames. Forks are quarantined (moved), never deleted.
- **Lease before write.** Punch in before working frames; punch out or hand off
  when done. In a hive this is enforced; solo, do it anyway.
- **Verify before trust.** Run `--verify --all` after every pull and before
  every push.
- **World boundary.** One workspace, one `world_id`. Content from another world
  never enters this workspace, its public face, or its store. Slosh freely
  within the world; contain across.
- **Owner sovereign.** Organize and propose; do not take irreversible or
  outward-facing actions (publish, push to a new remote, delete) without the
  owner's consent.
- **PII stays local.** Anything leaving the machine is stripped of names and
  identifiers. The vault itself is never published; only PII-free projections.
- **Mint once.** Never regenerate an existing `rappid.json`.

## 7. Hive sync loop and fork recovery

Every working session in a hive:

```bash
git pull --rebase
python3 rapp-projects/tools/append_frame.py --verify --all      # must be all OK
python3 rapp-projects/tools/append_frame.py --punchin --project <slug> --actor $RAPP_ACTOR --intent "..."
git add rapp-projects && git commit -m "punchin <slug>" && git push   # push the lease EARLY
# ... work; append checkpoint frames at each phase boundary ...
python3 rapp-projects/tools/append_frame.py --punchout --project <slug> --actor $RAPP_ACTOR
<pre-push gate>                                                   # §8
git add -A && git commit -m "..." && git push
```

An unpushed lease protects nobody, so push right after punching in.

**Fork** (two frames share one `seq`, detected by `--verify`): this is the one
race the lease cannot prevent (both pulled the same head offline, both punched
in, both pushed). Recovery is append-only:

1. Do not push further.
2. Decide the winner: the older *pushed* punchin; then the earlier `utc`; then
   the owner's ruling.
3. Move (never delete) the losing frame(s) into `projects/<slug>/frames/_forked/`.
4. `--verify --project <slug>` must now pass.
5. The losing operator re-appends their work on the healed chain, adding
   `"recovered_from": "<quarantined frame_hash>"` to the payload.
6. Commit the quarantine move and the new frames together; push.

## 8. Pre-push gate (hive stores)

Before every push to a hive store, run a fail-closed check that blocks the push
on any failure:

- no secret values in tracked files (keys, tokens, passwords; record pointers,
  never values),
- remote URLs carry no credentials,
- local-state paths are excluded,
- `append_frame.py --verify --all` exits 0,
- warn on oversized files and on anything that smells like another world.

If this repo's owner has not supplied a gate script, write one for the
workspace before adding a remote. A push that skips the gate is a protocol
violation.

## 9. Quick self-test (proves your setup works, touches nothing real)

```bash
export RAPP1_PATH=~/src/rapp-1 RAPP_ACTOR=alice RAPP_REQUIRE_LEASE=1
export RAPP_PROJECTS_ROOT=$(mktemp -d)/rapp-projects; mkdir -p $RAPP_PROJECTS_ROOT
T=~/src/rapp-workspace/tools/append_frame.py
python3 $T --genesis --project demo --title "Demo" --goal "Try the protocol"
python3 $T --punchin  --project demo --actor alice --intent "first pass"
python3 $T --project demo --event work.checkpoint --actor alice --payload '{"step":"s1"}'
python3 $T --punchin  --project demo --actor bob     # expect: REFUSED, alice holds the lease
python3 $T --punchout --project demo --actor alice
python3 $T --verify --all                            # expect: OK   demo: 4 frames
```

Expected: four frame files under `$RAPP_PROJECTS_ROOT/projects/demo/frames/`,
bob refused, verify green. Unset `RAPP_PROJECTS_ROOT` afterwards.

## 10. What this skill does not cover

- Signing frames for hive members (future work; local frames are unsigned).
- The workspace **manager** that routes an owner across several workspaces: it
  holds only a registry of pointers (name, mode, world, path, rappid, tags),
  never content (spec §7).
- Nested "matrix" workspaces, one cell per `world_id` (spec §5a): same rules,
  applied per cell.
