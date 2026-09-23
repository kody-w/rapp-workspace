# rapp-hive/2 reference (experimental frontier)

A small, pure reference implementation: Python 3.11+ and `cryptography`, no
network, no operating-system dependency in verification.

| Module | Does |
|---|---|
| `rapp1` | RAPP/1 canonical JSON, particles and waves, the frame checklist, RAPPIDs, detached EdDSA JWS, memory and body streams |
| `schema` | `rapp-schema/1` and additive schemas |
| `lens` | views, lenses, expressions, loss, additive successors |
| `hive` | carrier loading, frame verification, deterministic evaluation, manifests, the verdict |
| `crossing` | one member's message in another member's schema (unsigned proposals) |
| `migrate` | Path A (`rapp-hive/1`) and Path B (seeded join requests) plans, and signing one's own steps in phase order |
| `store` | portable, link-free, never-overwriting folder carriers |
| `sign` | frame signing, carrier layout, public test keys for models and tests |
| `model` | the synthetic Contoso model Hive and its conformance variants |
| `vectors` | generating and checking the conformance vectors |

```sh
cd protocols/rapp-hive/2/reference
python3 -B -m rapp_hive2 model /tmp/contoso            # build the model Hive
python3 -B -m rapp_hive2 status /tmp/contoso/hive      # plain-language summary
python3 -B -m rapp_hive2 vectors --check ../conformance/vectors.json
python3 -B -m unittest discover -s tests
```

The model is synthetic: fictional people and devices, signed with public test
keys that anyone can re-derive. Never use test keys for real data.

To walk through the model instead of building it, see
[kody-w/rapp-model-hive](https://github.com/kody-w/rapp-model-hive).
