# RAPP Workspace

**The private workspace protocol for the rapp/1 family** — one owner, many
worlds; solo or team (hive); local-first always; and, new in 1.1, **distributed
multi-operator operation** where concurrency is carried by rapp/1 frames
themselves: leases, handoffs, and takeovers are chain events, forks are
detected by hash verification and healed append-only.

- **[SPEC.md](SPEC.md)** — `rapp-workspace/1.1`, the protocol of record.
- **[tools/append_frame.py](tools/append_frame.py)** — reference frame writer
  with lease enforcement (punchin / heartbeat / handoff / takeover / punchout),
  fork detection, and full-chain verification. Requires a checkout of
  [`rapp-1`](https://github.com/kody-w/rapp-1) (set `RAPP1_PATH`).

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

## Lineage

`rapp-workspace/1.0` defined the private vault, the two-faces data layer, the
world boundary, and solo/hive modes. 1.1 names the shared home the **RAPP
Workspace store** and adds §9 Distributed operation. Instances stay private by
design — this repo carries only the protocol and the reference tool, never a
workspace's content.

MIT. Part of the RAPP foundation (`rapp-1` is the kernel of canon).
