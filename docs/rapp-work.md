# RAPP Work

RAPP Work is the business collaboration and compliance layer built on RAPP/1.
It does not fork or weaken RAPP/1. Identity, frames, canonicalization, content
addressing, eggs, signatures, registries, and trust remain governed by the
canonical RAPP/1 specification.

RAPP Work adds subordinate operational profiles for business requirements such
as:

- organizational and world boundaries;
- human, AI, agent, and service collaboration through equal RAPPID membership;
- role-, room-, and audience-scoped access;
- DOGG/GODD data classification;
- PII-free public projections;
- encrypted GODD sharing and scoped key release;
- provenance, audit history, and attributable approval;
- portable storage and multi-channel projection; and
- deterministic reconciliation of parallel work.

## Additive Workspace SDK integration

[`rapp-work-sdk/1`](../protocols/rapp-work-sdk/1/SPEC.md) is the additive
Workspace integration profile. It pins the accepted exact `rapp-work/1` bytes
at canonical `kody-w/rapp-1` commit
`591e014ad39e223b00ab343ae26e5d9a867ebeee`, then installs an atomic,
offline-first `.rapp-work/` sidecar beside an existing workspace. Earlier
`kody-w/rapp-work` pins are retained only as verified migration sources.

The sidecar preserves the native workspace RAPPID, world, workspace spec, and
content. It does not copy native workspace files and it does not alter or
relabel the normative `rapp-workspace/1` protocol. Organization entries point
to existing Workspace/1 composite wave addresses. Hive endpoint/vector
receipts, plugins, skills, and static APIs are discovery evidence only and
grant no publication, activation, or execution authority.

Same-pin installation is idempotent only after complete verification. Updates
require explicit known `from_pin` and `to_pin` values plus the exact
deterministic plan digest. Known historical pins retain their exact old profile
artifacts, and each sidecar generation retains its profile and discovery bytes.
The plan binds both source and target profile hashes; activation uses
directory-fd no-follow reads, no-replace generation activation, and an atomic
pointer compare-and-swap. Symlinks, races, conflicts, partial state,
downgrades, unsupported filesystem primitives, and unknown pins fail closed.
No branch, tag, latest-release, or network lookup is used by the scaffold.

An installed sidecar can recover its recorded world for inspection and update
when native identity omits it, while an explicit world must match. Native
content is never changed. Private Hive inventory and selection also reserve
case-fold aliases of both control sidecars on case-insensitive filesystems.

Private Hive preparation now invokes this scaffold by default before creating
or accepting `.rapp-hive/`. The historical Private Hive migration remains an
explicit `legacy-migrate` lane.

[`rapp-hive/1`](../protocols/rapp-hive/1/SPEC.md) is the first RAPP Work
profile. It defines the RAPP Private Hive: an access-restricted workspace that
can hold any verified RAPP/1 object, share explicitly selected GODD safely,
carry DOGG without changing its classification, and converge distributed
dimensions into one Mother Hive through Dream Catcher.

[`rapp-federation/1`](../protocols/rapp-federation/1/SPEC.md) defines the Hive
Mind: the one universal logical federation and interoperable graph formed by
many sovereign Private Hives. Each Hive retains its own owner, registry,
policies, keys, worlds, and Mother Hive head. Federation adds signed DOGG-safe
discovery, explicit peer consent, recipient-scoped sealed exchange, bilateral
business agreements, durable idempotency, phased receipts, revocation and
moderation, and delay-tolerant operation across long partitions.

Universal and galactic do not mean centralized or globally visible. The Hive
Mind has no universal owner, signing key, writable head, complete database,
mandatory relay, or public GODD graph. ActivityPub, AT Protocol, Git, HTTP,
Matrix, and delay-tolerant transports are replaceable adapters; none confers
RAPP authority.

The checked-in federation reference is a bounded, offline receiver and
conformance candidate. It does not claim that an estate has activated the
profile, that a live federation exists, or that unsupported transport and
native ECDH key-acquisition services have been deployed.

The invariant is simple:

> RAPP Work may add business policy around a RAPP/1 object. It never changes
> what makes that object RAPP/1 conformant.
