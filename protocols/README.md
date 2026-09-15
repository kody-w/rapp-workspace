# RAPP estate protocols

These application profiles extend RAPP/1 by registration rather than changing
the frozen RAPP/1 frame envelope.

They are the protocol layer of [RAPP Work](../docs/rapp-work.md): business
collaboration and compliance while retaining byte-level RAPP/1 conformance.

| Protocol | Purpose | Conformance |
|---|---|---|
| [`rapp-workspace/grail-1.0`](rapp-workspace/grail-1.0/SPEC.md) | RAPP Workspace/1 Grail minimal safe kernel candidate: five distinct guarantees, external capabilities/adoption and fail-closed effects | `python3 ../tools/frame_lens.py conformance --rapp1-path "<EXPLICIT_RAPP1_CHECKOUT>"` |
| [`rapp-hive/1`](rapp-hive/1/SPEC.md) | Private Hive workspaces, generic RAPP objects, sealed GODD rooms, PII-free DOGG, Dream Catcher convergence, and multi-channel projection | `python3 rapp-hive/1/reference/hive_conformance.py` |
| [`rapp-federation/1`](rapp-federation/1/SPEC.md) | The universal logical Hive Mind: consent-bound business collaboration among sovereign Private Hives, including delay-tolerant exchange and durable receipts | `python3 rapp-federation/1/reference/conformance.py --report rapp-federation/1/conformance-results.json` |

An estate activates a profile through an owner-signed RAPP/1 `protocol`
registry entry pinning this repository, the normative path, and exact SHA-256.
The checked-in federation implementation is a bounded candidate receiver, not
evidence that any estate has activated the profile or deployed a galactic
transport network.

The first-Grail acceptance scenario separates **RAPP integrity, observation,
semantic fidelity, current authorization and safe deployment**:
`python3 ../tools/frame_lens.py demo --rapp1-path "<EXPLICIT_RAPP1_CHECKOUT>"`.
Effective grants are external to learned/received graphs. Unsupported native,
model, network, migration and deployment effects refuse before access.
The prior Frame Anything evolution prototype is retained only as opt-in
withdrawn experimental evidence, not current authority or release acceptance.

Workspace Grail has closed Draft 2020-12 schemas and an exact-byte
[`manifest.json`](rapp-workspace/grail-1.0/manifest.json). The index pins that
manifest by SHA-256 and byte count. Its RAPP/1 inspection and Frame Chains
orchestration provenance are separate from Workspace policy and neither
activates an estate. The stdlib conformance emits and independently scans
nonzero canonical RAPP/1 frames using an explicitly supplied checkout.

[Historical pre-Grail 1.x/2.0 materials](rapp-workspace/historical/pre-grail/README.md)
are byte-pinned experimental/migration inputs, not active profiles or
normative predecessors forcing v2. The unique first-Grail protocol ID is
`rapp-workspace/grail-1.0`; it MUST NOT reuse old 1.0/1.1 IDs with different
bytes. The product is branded “RAPP Workspace/1 Grail.” Passing gates never manufactures signed
Grail activation or silently rebinds an older registry pin.
