# RAPP Hive AutoBest/1 reference

The reference validates closed application records and signed RAPP/1
application Frames. It does not activate a Hive, hotload an unapproved agent,
or grant authority.

Run from the repository root:

```sh
PYTHONDONTWRITEBYTECODE=1 \
  python3 protocols/rapp-hive-autobest/1/reference/schema_source.py --check

PYTHONDONTWRITEBYTECODE=1 \
  python3 protocols/rapp-hive-autobest/1/reference/conformance.py
```

`rapp_hive_autobest.py` provides:

- `validate(document)` for structural and cross-record validation;
- `authorize_frame(...)` for exact kind/schema binding through trusted RAPP/1
  signature and authorization verifiers;
- `validate_bill_fixture(path)` for the pinned first wild-handshake package.

Closed derived records cover JIT assignments, exact worker checkpoints,
Crossing Lens/AutoBest decisions, board/chat views, complete program bundles,
forward/reverse mutation lineage, sanitized learning traces, bounded N-Lens
search, mutation offers, handshake catalogs and recursive evolution.

The reference imports canonical RAPP primitives from the unchanged sibling
`rapp-hive/1` reference. Compatibility and exhaust Frames remain separate from
the Mother Hive stream and enter Hive catalogs through ordinary
`rapp-hive/1-object` typed wave addresses.

The Bill fixture is private conformance evidence. It contains no private key,
native model session, customer payload, or activation grant.
