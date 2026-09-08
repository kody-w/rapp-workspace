# RAPP Workspace

**The private workspace protocol for the rapp/1 family** — one owner, many
worlds; solo or team (hive); local-first always; and, new in 1.1, **distributed
multi-operator operation** where concurrency is carried by rapp/1 frames
themselves: leases, handoffs, and takeovers are chain events, forks are
detected by hash verification and healed append-only.

- **[SPEC.md](SPEC.md)** — `rapp-workspace/1.1`, the protocol of record.
- **[SKILL.md](SKILL.md)** — operator skill for any AI agent: assumes zero RAPP
  knowledge; setup, the frame commands, refusals, the hive sync loop, fork
  recovery, and a self-test. Drop it into your agent's skills directory.
- **[tools/append_frame.py](tools/append_frame.py)** — reference frame writer
  with lease enforcement (punchin / heartbeat / handoff / takeover / punchout),
  fork detection, and full-chain verification. Requires a checkout of
  [`rapp-1`](https://github.com/kody-w/rapp-1) (set `RAPP1_PATH`).

## What a workspace is, in plain terms

A private folder of Markdown and data for **one owner** and **one world** of
work, which an AI keeps organized as chief of staff. Project progress is not a
status doc that gets overwritten; it is a stream of small JSON **frames**, one
file each, hash-chained so history cannot be silently rewritten. Boards and
status pages are regenerated from the frames. Before an operator (human or AI)
writes frames to a project they **punch in** and hold a time-limited lease;
everyone else is refused until they punch out. A team sharing one workspace
through a private git remote is a **hive**.

## Why

Organically grown work scatters across repos until no one — human or AI — can
hold it. A RAPP Workspace collapses one world of work into one private vault an
AI keeps organized, with project history as append-only, hash-chained rapp/1
frame streams. Hive mode lets a whole team share that vault through a private
store **without stepping on each other's toes**: one stream, one lease; verify
before you trust; append, never rewrite.

## Quick taste

```bash
export RAPP1_PATH=~/src/rapp-1 RAPP_ACTOR=alice RAPP_REQUIRE_LEASE=1

python3 tools/append_frame.py --genesis --project demo --title "Demo" --goal "Try the protocol"
python3 tools/append_frame.py --punchin  --project demo --actor alice --intent "first pass"
python3 tools/append_frame.py --project demo --event work.checkpoint --actor alice --payload '{"step":"s1"}'
python3 tools/append_frame.py --punchout --project demo --actor alice
python3 tools/append_frame.py --verify --all
```

A second actor punching in while alice holds the lease is refused; after the
lease lapses, `--takeover` claims the stream — and every one of those events is
itself a verifiable frame in the chain.

## For AI agents

[`SKILL.md`](SKILL.md) is a self-contained Agent Skill. An agent that has never
heard of RAPP can read it and set up, join, and operate a workspace: vocabulary,
one-time setup, minting a workspace identity, every frame command with a table
of refusals and what to do about them, the conformance rules, the hive sync
loop, append-only fork recovery, the pre-push gate, and a scratch self-test.

Install it wherever your agent loads skills, for example:

```bash
mkdir -p ~/.claude/skills/rapp-workspace
curl -sL https://raw.githubusercontent.com/kody-w/rapp-workspace/main/SKILL.md \
  -o ~/.claude/skills/rapp-workspace/SKILL.md
```

Then ask the agent to "create a RAPP Workspace for <world>" or "punch in to
<project> and log a checkpoint". Every snippet in the skill was run verbatim
before it shipped.

## How the guarantees work

- **Frames are the authority.** Everything else is a derived projection.
- **Append only.** Frames are never edited or deleted; corrections append and
  forks are quarantined into `frames/_forked/`, never removed.
- **Atomic writes.** Temp file, fsync, rename; a crash loses no committed frame.
- **Leases are frames.** Punch-in, heartbeat, handoff, takeover, and punch-out
  all live in the chain, so the concurrency history is auditable.
- **Detection, not prevention, against a non-conforming writer.** Actor ids are
  unauthenticated and local frames are unsigned; among conforming writers the
  lease arbitrates, and any fork is caught deterministically by chain
  verification (two frames can never share a `seq` and both verify).

## Lineage

`rapp-workspace/1.0` defined the private vault, the two-faces data layer, the
world boundary, and solo/hive modes. 1.1 names the shared home the **RAPP
Workspace store** and adds §9 Distributed operation. Instances stay private by
design — this repo carries only the protocol and the reference tool, never a
workspace's content.

MIT. Part of the RAPP foundation (`rapp-1` is the kernel of canon).
