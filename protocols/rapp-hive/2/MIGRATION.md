# Migrating to rapp-hive/2 (experimental frontier)

`rapp-hive/2` is an experimental frontier draft. Joining it is a choice: nothing
here changes `rapp-hive/1`, and every Hive that stays on the current version
keeps working exactly as it does today. This document is for people who want to
try the frontier with the Hive they already have.

## Principles

1. **Nothing is rewritten.** Every existing frame stays byte for byte as it is,
   and keeps verifying with the engine that made it.
2. **Everyone signs for themselves.** A migration is a plan anyone can review
   plus new frames that each identity signs with its own key. The migrator can
   only apply the signer's own steps (`REFUSE_NOT_YOURS`).
3. **Same people, same rules first.** The first `rapp-hive/2` policy reproduces
   how the Hive already decides. Changing how it decides is a separate, later
   step, and it never strands a request that is already waiting.
4. **Reversible.** To go back, stop writing `rapp-hive/2` frames. Legacy engines
   treat them as unregistered application data and ignore them.
5. **Private stays private.** Rooms, sealed eggs, GODD slices and the
   `rapp-hive/1` privacy policy are unchanged; the new policy carries the
   privacy settings in its `data`.

## Which path

| You run today | Path |
|---|---|
| A `rapp-hive/1` Private Hive (a declaration with one owner and members) | A |
| A repository-seeded Private Hive whose newcomers file signed join requests | B |
| Nothing yet | C |

## Path A: rapp-hive/1 to rapp-hive/2

1. **Plan.** From a folder holding the Hive's verified frames:

   ```sh
   python3 -B -m rapp_hive2 migrate plan-hive1 <folder> \
     --declaration <frame hash of the current hive.declaration> \
     --name "<Hive name>" --out plan.json
   ```

   The declaration must be exactly what `rapp-hive/1` accepts: a payload that
   passes every `rapp-hive/1` declaration rule, as the first frame of the Mother
   Hive stream (`stream_id` = `hive_rappid`), signed by the one owner it
   declares. The plan's anchor keeps its `world_id`, names that owner as
   the steward founder, and pins a version 1 **steward policy** whose only
   decider is the steward (`"deciders": [<owner>]`): the steward alone admits,
   adopts lenses and changes policy, just as the owner did in `rapp-hive/1`.
   Members (role `member`) keep their place by joining and being granted by the
   steward; their own grants and adoptions do not count until a co-equal policy
   makes them deciders. Viewers are not admitted as members; they can still read
   carried copies.

2. **Review.** Everyone can check the plan: its particle, anchor, policy and
   each person's steps. It holds no private data beyond what the declaration
   already names.

3. **Apply, each with their own key.** The owner applies phase 1 (accept), each
   member applies phase 1 (join), then the owner applies phase 2 (grants). The
   migrator refuses a phase before every earlier phase is carried and in effect
   (`REFUSE_ORDER`), a time that would sort before the steps it depends on
   (`REFUSE_FRAME_TIME`), a step that is already carried and in effect
   (`REFUSE_ALREADY_APPLIED`), and any plan that asks for more than accept, join
   and grant frames for its own anchor (`REFUSE_TAMPER`):

   ```sh
   python3 -B -m rapp_hive2 migrate apply <folder> plan.json \
     --key <own-ed25519-key.pem> --owner <rappid owner> --slug <rappid slug> --phase 1
   ```

4. **Verify.** `python3 -B -m rapp_hive2 status <folder>` shows the same people
   with the same roles, now on `rapp-hive/2`.

5. **When ready, go co-equal.** The steward adopts a version 2 policy with
   `"deciders": "members"`, a peer quorum and `migrate_pending: "keep-pinned"`.
   Requests already waiting keep the rules they were made under (a request made
   under the steward policy is still decided by the steward alone); new requests
   use the new rules.

## Path B: repository-seeded Hives with signed join requests

Some Private Hives are seeded from a repository: an owner anchor, signed join
requests committed by newcomers, and an admission policy that may have changed
since the requests were made (for example from owner admission to peer approval,
which leaves older requests with no way in).

1. **Choose the founders** (the peers who will decide together) and the exact
   join-request frames that exist today.
2. **Plan:**

   ```sh
   python3 -B -m rapp_hive2 migrate plan-joins <folder> --name "<Hive name>" \
     --world <world_id> --founder <rappid> --founder <rappid> \
     --request <frame hash> --quorum 2 --attested --from repository-seeded-private-hive --out plan.json
   ```

   The anchor keeps the Hive's existing `world_id` (up to 128 characters) and
   lists those request frame hashes under `legacy.join.requests`. Each becomes a
   pending request of its own signer, decided under the Hive's first policy.
   Because the list is fixed in the anchor, no new request can pose as an old
   one. A founder may be someone whose old request is still waiting: that
   request closes when the founder accepts, so no grant is drafted for it. The
   quorum cannot exceed the number of founders (a peer policy with too few
   members could never admit anyone), and `--attested` also requires a key
   another member has confirmed, for Hives that already check fingerprints:
   each founder's optional phase 2 step then includes a `key-confirmed`
   attestation, to sign only after confirming that requester's fingerprint with
   its holder by voice, video or in person.
3. **Apply.** Each founder accepts (phase 1). After every founder has accepted,
   each founder signs only the approvals they vouch for (phase 2, optional per
   request). The first policy's deciders are all members, so there is no
   one-owner override; when the quorum is reached, the requester is a member,
   without re-enrolling. A request may be any signed content frame of its
   requester, including one on an old body stream; governance frames and the
   declaration cannot be listed.

## Path C: a new Hive on the frontier

Write an anchor and a version 1 policy, have each founder sign `hive2.accept`,
and adopt your first lenses. The synthetic model Hive shows every step.

## What each version sees

| | A `rapp-hive/1` engine | A `rapp-hive/2` engine |
|---|---|---|
| `rapp-hive/1` frames | verified as always | verified on their body streams and carried as content of their signer; the pinned declaration is legacy evidence |
| `hive2.*` frames | unregistered application data, ignored | governance, but only on the signer's own memory stream |
| Old join requests | unchanged | pending requests when listed in the anchor |

## Try it on the model first

The synthetic Contoso model Hive (`python3 -B -m rapp_hive2 model <new-folder>`)
contains a `before/` folder (a `rapp-hive/1` declaration on its Mother Hive
stream, which `rapp-hive/1`'s own reference verifies, plus work items and an old
join request) and the migrated `hive/`. Running Path A on `before/` with the
model's public test keys reproduces the migrated frames byte for byte; the
reference tests check this. The model also shows the steward deciding alone: a
member's grant under the steward policy is refused (`REFUSE_NOT_DECIDER`) until
the peers take over.

A published, walkable copy lives at
[kody-w/rapp-model-hive](https://github.com/kody-w/rapp-model-hive): a room-by-room
tour, a single offline page that verifies the Hive in your browser, and a
Brainstem agent that replays this migration and compares every frame.
