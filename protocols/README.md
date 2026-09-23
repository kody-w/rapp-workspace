# RAPP estate protocols

These application profiles extend RAPP/1 by registration rather than changing
the frozen RAPP/1 frame envelope.

They are the protocol layer of [RAPP Work](../docs/rapp-work.md): business
collaboration and compliance while retaining byte-level RAPP/1 conformance.

| Protocol | Purpose | Conformance |
|---|---|---|
| [`rapp-workspace/1`](rapp-workspace/1/SPEC.md) | RAPP Workspace/1 core protocol: recursive default-branch catalogs, outcome-first organization, pointer-only workspace composites and fail-closed Hive proposals/effects | `python3 ../tools/frame_lens.py conformance --rapp1-path "<EXPLICIT_RAPP1_CHECKOUT>"` |
| [`rapp-hive/1`](rapp-hive/1/SPEC.md) | Private Hive workspaces, generic RAPP objects, sealed GODD rooms, PII-free DOGG, Dream Catcher convergence, and multi-channel projection | `python3 rapp-hive/1/reference/hive_conformance.py` |
| [`rapp-federation/1`](rapp-federation/1/SPEC.md) | The universal logical Hive Mind: consent-bound business collaboration among sovereign Private Hives, including delay-tolerant exchange and durable receipts | `python3 rapp-federation/1/reference/conformance.py --report rapp-federation/1/conformance-results.json` |
| [`rapp-hive/2`](rapp-hive/2/SPEC.md) | **Experimental frontier (canary).** Co-equal Hives of sovereign streams: only signed facts are carried, schema lenses map every shape into shared views, members sign agreeing manifests, and [migration paths](rapp-hive/2/MIGRATION.md) bring `rapp-hive/1` and seeded Hives along without breaking them | `cd rapp-hive/2/reference && python3 -B -m rapp_hive2 vectors --check ../conformance/vectors.json` |
| [`rapp-schema/1`](rapp-schema/1/SPEC.md) | **Experimental frontier (canary).** The bare schema of a RAPP/1 frame (names and types, never values): the unit lenses map | covered by the `rapp-hive/2` vectors |

An estate activates a profile through an owner-signed RAPP/1 `protocol`
registry entry pinning this repository, the normative path, and exact SHA-256.
The checked-in federation implementation is a bounded candidate receiver, not
evidence that any estate has activated the profile or deployed a galactic
transport network.

The Workspace/1 core acceptance scenario separates **RAPP integrity, observation,
semantic fidelity, current authorization and safe deployment**:
`python3 ../tools/frame_lens.py demo --rapp1-path "<EXPLICIT_RAPP1_CHECKOUT>"`.
Effective grants are external to learned/received graphs. Unsupported native,
model, network, migration and deployment effects refuse before access.
Live Workspace/1 controllers additionally require independently authenticated
activation of exact spec/runtime-manifest/instance/world/validity/signer/
revocation bindings and fresh trusted clock samples at each authorization
boundary. The reference supplies a host trust hook, not production signing.
The demo explicitly labels synthetic activation; neither local hash
recomputation nor passing conformance creates a signed estate registry entry.
Composite metadata bindings report verified evidence or preserved-by-reference
unverified status, never unconditional child identity/world preservation.
One bounded memoized traversal and checked authority-table/index recovery
cover all composite descendants.
The prior Frame Anything evolution prototype is retained only as opt-in
withdrawn experimental evidence, not current authority or release acceptance.

RAPP Workspace/1 has closed Draft 2020-12 schemas and an exact-byte
[`manifest.json`](rapp-workspace/1/manifest.json). The index pins that
manifest by SHA-256 and byte count. Its RAPP/1 inspection and Frame Chains
orchestration provenance are separate from Workspace policy and neither
activates an estate. The stdlib conformance emits and independently scans
nonzero canonical RAPP/1 frames using an explicitly supplied checkout.

[Prototype workspace materials](rapp-workspace/prototypes/README.md) are
byte-pinned research/migration inputs, not active profiles or normative
predecessors. The sole core protocol ID is `rapp-workspace/1`. Passing gates
never manufactures estate activation or silently rebinds a prototype pin.
