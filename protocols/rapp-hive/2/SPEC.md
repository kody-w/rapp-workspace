# RAPP Hive/2

## Co-equal Hives of sovereign streams, schema lenses and portable manifests

**Protocol identifier:** `rapp-hive/2`
**Status:** Frozen research record (2026-09-23): kept for its lessons; never activate. See [`FROZEN.md`](FROZEN.md).
**Parent:** [`rapp/1`](https://github.com/kody-w/rapp-1/blob/main/SPEC.md)
**Predecessor:** [`rapp-hive/1`](../1/SPEC.md), which remains valid and unchanged
**Companion:** [`rapp-schema/1`](../../rapp-schema/1/SPEC.md)
**Migration:** [`MIGRATION.md`](MIGRATION.md)
**Conformance:** [`conformance/vectors.json`](conformance/vectors.json), reference in [`reference/`](reference/README.md)

A Hive is one portable organism made of sovereign streams. Each member (a
person, device, agent or team) writes only its own signed RAPP/1 streams. The
Hive's state is not stored anywhere: every device derives it from the signed
frames it holds, the same way, and members sign manifests that say what they
derived. Messages of different shapes meet through versioned lenses that map
schemas into shared views and back.

The key words **MUST**, **MUST NOT**, **REQUIRED**, **SHOULD** and **MAY** are
used as defined by RAPP/1 section 2.

## 0. Why a successor

`rapp-hive/2` keeps the `rapp-hive/1` data boundaries and changes what hurt in
practice:

| What hurt | Rule in this profile |
|---|---|
| Derived data (views, catalogs, receipts) travelled next to signed data, so every engine had to copy the producer exactly or be fooled | Only signed frames, identity records and content-addressed objects are carried; everything else is derived (section 3) |
| One authority stream and one owner; changing governance stranded older requests | Co-equal members, quorum policies, and policy successors that say how pending requests migrate (section 6) |
| Checks of who may write a stream lived in applications | The stream owner is part of frame validity (section 2) |
| Observations were carried as unsigned claims | Observations are signed attestation frames (section 6.5) |
| Engines drifted apart | Normative conformance vectors every engine must pass (section 12) |
| Verifiers depended on one operating system | A pure core: bytes in, verdict out (section 3) |

## 1. RAPP/1 foundation

An implementation:

1. **MUST** use the exact eleven-key `rapp/1` frame envelope, RAPP/1 canonical
   JSON, particles `H("rapp/1:particle", payload)` and waves, and apply the whole
   RAPP/1 section 7.5 checklist: the `kind` grammar (`lclabel "." lclabel`), a
   calendar-valid `utc` (no second 60), and `prev_wave` null, since this profile
   carries no swarm streams.
2. **MUST** require a valid detached EdDSA JWS on every frame it accepts.
3. **MUST** register the kinds below in the adopting estate's signed RAPP/1
   section 13 registry and pin this specification's exact SHA-256, as for
   `rapp-hive/1`. While this profile is experimental, an estate **MUST NOT**
   activate it for production data.
4. **MUST** order frames across streams by ascending `utc`, then ascending
   `frame_hash` (the RAPP/1 Dream Catcher order). Signers **SHOULD** give each
   frame of a stream its own `utc`.
5. **MUST NOT** repair, reparent, mutate or discard a received frame.
6. **MUST** refuse in favor of RAPP/1 whenever this profile conflicts with it.

Registered kinds, each bound to exactly one payload schema:

| Kind | Payload schema | Keys |
|---|---|---|
| `hive2.accept` | `rapp-hive/2-accept` | `schema`, `anchor` |
| `hive2.join` | `rapp-hive/2-join` | `schema`, `anchor`, `policy` |
| `hive2.grant` | `rapp-hive/2-grant` | `schema`, `anchor`, `member`, `request` |
| `hive2.adopt` | `rapp-hive/2-adopt` | `schema`, `anchor`, `object`, `predecessor` |
| `hive2.attest` | `rapp-hive/2-attest` | `schema`, `anchor`, `subject`, `claim`, `method` |
| `hive2.manifest` | `rapp-hive/2-manifest` | `schema`, `anchor`, `heads`, `state` |

Every other frame (for example `memory.save` work items, or `rapp-hive/1`
`hive.object` records) is **content**.

## 2. Stream ownership

A carrier holds RAPP/1 memory streams and body streams only (RAPP/1 section
6.1.1); any other `stream_id` refuses the carrier.

- **Memory streams** (`stream_id = <rappid> ":" <instance>`) are sovereign. The
  signer is the keyed RAPPID that prefixes the stream: the JWS protected header
  `kid` **MUST** equal it, and the signature **MUST** verify with the public key
  bound to it (RAPPID suffix = `H("rapp/1:rappid", SPKI DER)`). A frame on
  another identity's memory stream is invalid, whatever it says, and so is every
  carrier that holds it. Every `rapp-hive/2` governance frame is written on its
  signer's own memory stream.
- **Body streams** (`stream_id = <rappid>`) are how `rapp-hive/1` writes its
  Mother Hive: the owner signs frames on the `hive_rappid` stream. The signer of
  a body-stream frame is its JWS `kid`, whose signature **MUST** verify. Such a
  frame is legacy evidence: it counts only as content of its signer, and a
  governance kind on a body stream is refused without effect
  (`REFUSE_LEGACY_STREAM`).

A carrier supplies public keys as self-verifying identity records:

```json
{"schema": "rapp-hive/2-identity", "rappid": "rappid:@owner/slug:<hex>", "spki_der_b64": "<base64>"}
```

Streams **MUST** be carried whole from `seq` 0 and form a RAPP/1 chain (no gap,
fork, replay or UTC rollback).

## 3. What is carried and what is derived

Carried (authority): signed frames, identity records, and content-addressed
objects (anchors, policies, views, lenses, schemas) named by their particle.
Derived (never trusted from a carrier): members, the active policy and lenses,
views, exhausts, agreement, liveness, documents and user interfaces.

A folder carrier holds `HIVE.json` (a pointer to the anchor particle),
`identities/*.json`, `objects/<particle>.json` and `streams/**/<seq>.json`, all
canonical JSON. File names are transport, never identity: an object whose bytes
do not hash to its name is refused, links and special files are refused, and paths obey the
strictest common rules of macOS, Linux and Windows. Git, NAS, LAN, archives or QR
chunks are equally valid carriers of the same bytes. Every carried file, and so
every carried object, is at most 1 MiB of canonical JSON; a larger schema is
derived from its frames and never carried. A carried object whose `schema` is
`rapp-schema/1` **MUST** be a schema that `rapp-schema/1` could produce
(`REFUSE_SCHEMA`).

The verifier is pure: given the same bytes, every engine on every platform
reaches the same verdict (section 12). Integrity failures refuse the whole
carrier. Governance frames that do not meet the rules are recorded as refusals
and have no effect.

## 4. Objects

### 4.1 Anchor

```json
{"schema": "rapp-hive/2-anchor", "name": "…", "world_id": "<label>",
 "founders": ["<sorted unique rappids>"], "policy": "<policy particle>",
 "legacy": null}
```

The Hive's identity is the anchor particle. `world_id` is a lowercase label of
at most 128 characters, as in RAPP Workspace/1. `policy` names version 1 of the
policy. `legacy` is `null` or `{"from", "declaration", "join"}` (section 7);
`declaration` is a frame hash exactly when `from` is `"rapp-hive/1"`, and `null`
otherwise.

### 4.2 Policy

```json
{"schema": "rapp-hive/2-policy", "version": 1, "predecessor": null,
 "deciders": "members",
 "admit": {"quorum": 2, "attested": true},
 "change_policy": {"quorum": 2},
 "adopt_lens": {"new": {"quorum": 1}, "additive": "automatic", "successor": {"quorum": 2}},
 "migrate_pending": "keep-pinned",
 "data": {}}
```

`deciders` is `"members"` (every member decides) or a sorted list of RAPPIDs
(only they decide, and no quorum may exceed their number). A quorum counts
distinct current members who decide under the governing policy: the pinned
policy for a join request, the active policy for adoptions. A grant or adoption
by a member who does not decide is refused (`REFUSE_NOT_DECIDER`); attesting is
not deciding. `migrate_pending` is `keep-pinned`
(requests already pending keep the rules they were made under) or `re-decide`
(they move to the new rules). `data` carries settings that other profiles
define, such as the `rapp-hive/1` privacy policy.

### 4.3 View and lens

A view declares the fields every lens into it must produce:

```json
{"schema": "rapp-hive/2-view", "id": "…", "version": 1,
 "fields": {"title": "string", "due": ["null", "string"]}}
```

A lens maps exact schemas into one view:

```json
{"schema": "rapp-hive/2-lens", "id": "…", "version": 1, "predecessor": null,
 "view": "<view particle>",
 "mappings": [{"accepts": ["<sorted schema particles>"],
               "forward": {"title": {"select": "payload.text"}},
               "reverse": {"text": {"select": "title"}, "operation": {"const": "task"}}}]}
```

Expressions are data: `{"select": "a.b"}`, `{"const": v}`, `{"first": [e, …]}`,
or objects and arrays of expressions; object keys are rendered in canonical
order. `forward` reads only `payload.*` and **MUST** produce an object that
conforms to the view. `reverse` (optional) reads the view and rebuilds a payload.
A schema is accepted by at most one mapping of a lens. A successor pins its exact
predecessor `{id, version, particle}` and keeps the same view.

## 5. Schemas

Every content frame has a `rapp-schema/1` schema. Mapping is decided per schema:
the frame is mapped by the one active lens mapping that accepts its schema
particle. None is an exhaust (`no-lens`); more than one is an exhaust
(`ambiguous`); an output that does not conform to the view is an exhaust
(`view-shape`). Exhausts are recorded once per schema with every waiting message,
and a new lens later maps them all.

## 6. Deterministic evaluation

An engine processes the verified frames of the carrier in section 1 order,
starting with no members and the anchor's version 1 policy, and applies the
rules below. Membership never depends on content or lenses, so an engine can
decide it first; content is then weighed only if its signer is a member at the
end (section 6.6). A governance frame whose keys, schema or value types are
wrong is refused (`REFUSE_GOVERNANCE_SHAPE`): anchors, policies, requests,
objects and predecessors are 64-hex particles (a predecessor may be `null`),
members and subjects are keyed RAPPIDs.

### 6.1 Founding

`hive2.accept` by a founder makes it a member. Others are refused
(`REFUSE_NOT_FOUNDER`).

### 6.2 Admission

`hive2.join` by a non-member creates a pending request pinned to the policy
named in the frame, which **MUST** be the active policy (`REFUSE_STALE`).
`hive2.grant` by a member who decides under the request's pinned policy counts
toward a pending request of the named identity. A request is admitted when its
distinct granting deciders reach the pinned policy's `admit.quorum` and, if
`admit.attested`, a member other than the requester has attested
`key-confirmed` for the requester's RAPPID. Admission closes every other pending
request of the new member, and a request whose requester is already a member
closes without effect. Membership only grows.

### 6.3 Policy change

`hive2.adopt` of a policy by a member counts only if the policy's `predecessor`
and the frame's `predecessor` both equal the active policy and its version is
one higher (compare-and-swap; `REFUSE_STALE`). The policy becomes active when its
distinct adopting deciders reach the active policy's `change_policy.quorum`.
Pending requests then keep or change their pinned policy per `migrate_pending`.

### 6.4 Lenses and their laws

`hive2.adopt` of a lens with `predecessor: null` introduces a new lens id
(quorum `adopt_lens.new`). With a predecessor, the frame's `predecessor` **MUST**
be the active lens particle and the lens's own `predecessor` **MUST** equal the
active version's exact `{id, version, particle}`, so its version is one higher
(`REFUSE_STALE`); it needs quorum `adopt_lens.successor`. Before a
successor becomes active its **laws** **MUST** hold, whatever signatures it has:

1. it keeps its predecessor's view;
2. it accepts every schema its predecessor accepted;
3. every content frame the predecessor already mapped maps to the identical
   view particle under the successor.

A violation is recorded as `REFUSE_LENS_LAW` and the successor stays inactive.

**Additive successors.** When a content frame's schema is not accepted, but is
additive (`rapp-schema/1` section 3) over a schema accepted by exactly one active
mapping whose forward expression renders on it, the engine derives the successor
that adds the new schema to that mapping (same id, version + 1, predecessor
pinned). Every engine derives the same bytes. It is active immediately when
`adopt_lens.additive` is `automatic`; otherwise it waits for adoption. Derived
successors are not carried.

### 6.5 Attestations

`hive2.attest` by a member records a signed observation about another identity,
such as `key-confirmed` after confirming a key fingerprint by voice, video or in
person. People prove who holds a key; the Hive keeps their signed word.

### 6.6 Content and quarantine

Content frames count once their signer is a member at the end of evaluation.
Frames of other identities are quarantined, never deleted. Quarantined frames
are set aside before any lens processing: they never teach an additive
successor, never become exhausts and are never weighed by the lens laws.
Governance frames naming another anchor belong to another Hive and are ignored.

### 6.7 State

The derived state is:

```json
{"schema": "rapp-hive/2-state", "anchor": "…", "policy": "<active policy particle>",
 "members": ["<sorted>"], "lenses": {"<id>": "<active lens particle>"}, "pending": ["<sorted request frame hashes>"]}
```

## 7. Legacy and migration

An anchor with `legacy.from = "rapp-hive/1"` names the frame hash of the
`rapp-hive/1` declaration it succeeds. That frame **MUST** be carried and
**MUST** be exactly what `rapp-hive/1` accepts: its payload passes every
`rapp-hive/1` declaration rule (section 3 of that profile, as its reference
`validate_declaration` checks), and it is the genesis (`seq` 0) of its Mother
Hive body stream, whose `stream_id` equals the declaration's `hive_rappid`,
signed by the one owner it declares. Its `world_id` **MUST** equal
the anchor's, and every founder **MUST** be a declared owner or member
(`REFUSE_LEGACY`). `legacy.join.requests` lists the exact frame hashes of requests
made on an older system; each **MUST** be a carried content frame, never a
governance frame or the declaration. Each is a pending request of its signer,
pinned to the anchor's version 1 policy, so it is decided by the rules of the
Hive's first policy and is never stranded. The list is fixed by the anchor, so no
new request can pose as an old one. See [`MIGRATION.md`](MIGRATION.md).

## 8. Manifests and agreement

`hive2.manifest` names `heads` (per stream: `seq` and `frame_hash` of the newest
frame the signer holds, excluding manifests) and the particle of the state it
derived at those heads. A head that names a manifest makes the manifest
unverifiable. An engine re-derives the state from exactly those heads.
A manifest is `consistent` or `divergent`; a consistent manifest either `agrees`
with the carrier's heads or is `behind` them. A manifest whose keys, schema or state
particle are wrong is `malformed`; one whose heads are malformed or name frames the carrier does not
hold is `unverifiable` (`REFUSE_MANIFEST`). Only each member's newest manifest
counts: the last in section 1 order, across all of its streams. There is no
master copy: the Hive's current state is what members' manifests agree on. Under
a steward policy (one decider) the steward's manifest plays the role of the
`rapp-hive/1` Mother Hive head.

## 9. Crossing dimensions

To show one member's message in another member's schema, an engine maps it
forward through its own lens into the view, then back through the newest lens
version whose reverse reproduces the target schema exactly. The result is an
unsigned proposal:

- it **MUST** name the view fields the target cannot express, and the source
  fields the forward lens did not actually read (string-valued `schema`,
  `profile` and `operation` tags are matched by the schema itself);
- it **MUST NOT** invent a field: if the target schema cannot be reproduced
  exactly, it refuses (`REFUSE_CROSSING`);
- if more than one lens id could answer, it refuses (`REFUSE_LENS_COLLISION`);
- only the receiving member can sign it into its own stream.

## 10. Liveness, privacy and data classes

Every verified frame is a tick of existence. A Hive is awake while new verified
ticks arrive and asleep when none do; the viewer judges this against its own
clock.

The `rapp-hive/1` boundaries are unchanged: local workspace, Private Hive and
DOGG; GODD, DOGG and neutral data classes; sealed rooms, sealed eggs, GODD slices
and assimilation (`rapp-hive/1` sections 2, 3.1, 4, 5 and 6), carried as content.
Schemas, views and lenses hold no message values and form the Hive's **public
layer**: they are DOGG-eligible only when their field names, tags and constants
are free of personal data, and only an explicit owner decision promotes them to a
public projection. Content is never public by default.

## 11. Versioning and compatibility

1. Every change is a successor (policy, lens, schema version, profile version);
   nothing is edited in place, and old versions stay verifiable forever.
2. Additive changes apply automatically; changes that could alter meaning wait
   for the policy's quorum and the lens laws.
3. Unknown kinds and schemas are opaque evidence, never guessed.
4. A `rapp-hive/2` engine keeps verifying `rapp-hive/1` frames (on their body
   streams) as content; a
   `rapp-hive/1` engine treats `hive2.*` frames as unregistered application
   data. Neither breaks the other.

## 12. Conformance

[`conformance/vectors.json`](conformance/vectors.json) holds canonical-JSON and
limit cases, schema particles, the synthetic model Hive and its variants with
their full expected verdicts, tampered carriers with their exact refusal codes,
and crossings. An engine conforms when it reproduces every expectation byte for
byte. The reference runs them with
`python3 -B -m rapp_hive2 vectors --check ../conformance/vectors.json` from
`reference/`.

## 13. Refusal codes

`REFUSE_CANONICAL_JSON`, `REFUSE_JSON_SIZE`, `REFUSE_FRAME_SHAPE`,
`REFUSE_FRAME_HASH`, `REFUSE_FRAME_TIME`, `REFUSE_HISTORY_ORDER`,
`REFUSE_SIGNATURE`, `REFUSE_IDENTITY`, `REFUSE_TAMPER`, `REFUSE_UNSAFE_PATH`,
`REFUSE_PORTABLE_PATH`, `REFUSE_SCHEMA`, `REFUSE_ANCHOR`, `REFUSE_POLICY`,
`REFUSE_LEGACY`, `REFUSE_LENS` (carrier level); `REFUSE_GOVERNANCE_SHAPE`,
`REFUSE_NOT_FOUNDER`, `REFUSE_NOT_MEMBER`, `REFUSE_ALREADY_MEMBER`,
`REFUSE_DUPLICATE`, `REFUSE_UNKNOWN_REQUEST`, `REFUSE_UNKNOWN_OBJECT`,
`REFUSE_STALE`, `REFUSE_NOT_DECIDER`, `REFUSE_LEGACY_STREAM`, `REFUSE_LENS_LAW`
(recorded, no effect); `REFUSE_MANIFEST` (a manifest is unverifiable);
`REFUSE_CROSSING`, `REFUSE_LENS_COLLISION` (crossing); `REFUSE_NOT_YOURS`,
`REFUSE_ORDER`, `REFUSE_ALREADY_APPLIED`, `REFUSE_CONFLICT` (migration tooling).

## 14. Experimental frontier

This profile starts in the experimental frontier track, canary ring. It moves
through nightly, alpha and beta to that track's grail only with passing
conformance, review, and at least one migrated Hive; later tracks start only
from that grail. Until then `rapp-hive/1` is the current version, and nothing
here changes it.
