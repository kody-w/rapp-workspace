# Reference compatibility validator

This directory validates the optional `rapp-federation-autobest/1` profile. It
does not start a daemon, contact a network, modify Brainstem, install a plugin,
or activate a compatibility package.

## Release gate

```sh
PYTHONDONTWRITEBYTECODE=1 python3 reference/schema_source.py --check
PYTHONDONTWRITEBYTECODE=1 python3 reference/vectors.py --check
PYTHONDONTWRITEBYTECODE=1 python3 reference/conformance.py \
  --report conformance-results.json
```

The public synthetic fixture contains three signed RAPP/1 Frames: two source
`microsol-project/1` Frames and one local compatibility Frame. It runs the
exact pinned SoftwareCo source Lens and target finalizer, then reproduces a
self-contained static `agent.py`.

The live Bill qualification counts in `qualification.json` are externally
supplied evidence. Raw private repository content is not checked in and the
reference does not claim to reverify it.

## Modules

| Module | Purpose |
|---|---|
| `schema_source.py` | Auditable generator for the closed Draft 2020-12 schema |
| `compatibility.py` | Strict JSON/canonicalization, RAPP frame checks, semantic gates, deterministic compiler |
| `vectors.py` | Reproducible fixture, learning trace, package, mutation offer, and static agent |
| `conformance.py` | Positive and controlled-negative acceptance suite |

## Verified generic CEO binding

`fixtures/generic-ceo/agent.py` and `SKILL.md` are byte-identical approved
inputs. `implementation-binding.json` is deterministically reproduced by the
agent's pure `bind_implementation_sha256()` API.

The binding is external-host-only and grants no authority from presence.
`require_ceo_for_mutation()` confirms pin eligibility only; every dynamic
successor still requires current authority, policy, bounded execution,
independent verification, and separate host activation.

Known static compatibility continues to work under its declared partial
coverage with zero model calls.
