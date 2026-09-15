# RAPP Workspace/1 Grail

**RAPP-valid ≠ accurately observed ≠ semantically faithful ≠ currently
authorized ≠ safely deployable.**

The unique subordinate protocol identifier is
[`rapp-workspace/grail-1.0`](protocols/rapp-workspace/grail-1.0/SPEC.md).
“Workspace/1 Grail” is the product name, not permission to reuse historical
`rapp-workspace/1.0` or `/1.1` identifiers with different bytes. RAPP/1 still
owns the unchanged eleven-key frame, identities, hashes, signatures, eggs and
signed estate registry.

## First Grail: the minimal safe kernel candidate

The first-Grail reference deliberately narrows the previous experiments:

- Scoped capture is authorized **before** access.
- Immutable observations and derivations propagate separate capture,
  synthesis, model-submission, retention, redistribution and action rights.
- A small total evaluator consumes exact verified immutable code bytes.
  It has no imports, network, credentials, host tools or executable input.
- Integrity, observation, fidelity, authorization and deployment have
  separate pinned, scoped receipts; none silently satisfies another.
- Effective capability grants and adoption live in an **external single-writer
  controller**, not the learned graph.
- Adoption checks the complete policy/source/routing/adoption/suppression/
  runtime frontier and commits atomically with crash recovery/idempotence.
- A root-owned bounded scheduler reserves stop capacity and persists its
  counters and repeated-state/no-progress evidence.
- The only materializer writes deterministic inert `view.json` under the
  controller. No HTML, remote images, terminal controls, instructions or code
  are activated.

[Normative safety matrix](protocols/rapp-workspace/grail-1.0/safety-matrix.json)
maps every red-team P0/P1 requirement to an implemented gate or an explicit
refusal. Passing fixtures cannot turn an unproven capability on.

## One-command five-guarantee demo

From this checkout, with the explicitly supplied canonical RAPP/1 checkout:

```bash
python3 -B tools/frame_lens.py demo --rapp1-path "<EXPLICIT_RAPP1_CHECKOUT>"
```

The demo prints each guarantee separately. It can adopt an **inert captured
view** after an independent synthetic controller approves an exact complete
byte-coverage/inverse contract. It still reports **safe deployment refused**
and **signed Grail activation false**.

To observe a supplied regular file, capture and retention are separate explicit
grants; local synthesis is another:

```bash
python3 -B tools/frame_lens.py demo --rapp1-path "<EXPLICIT_RAPP1_CHECKOUT>" \
  --fixture "<EXPLICIT_FILE>" --allow-capture --allow-retention \
  --allow-local-synthesis --output .validation/scoped-file-observation
```

Missing grants refuse before source access. Stable file-descriptor reads are
not called coherent native snapshots. Supplied files are never automatically
adopted or rebound to native applications. Output must be outside the source.
Local frame export/materialization additionally needs `--allow-materialization`;
capture/retention flags do not grant it implicitly.
Use a fresh output directory; controller state is never reset to rerun a demo.

## Explicitly disabled in first Grail

Remote model submission, loopback/network access, ambient imports/host tools,
arbitrary code, external or partitioned effects, public redistribution,
native rebinding, live migration, live O(delta) monitoring, authoritative
merge, timed physical erasure and learned semantic-capability claims are
**disabled** until their required proofs exist.

Replay proves reproducibility, not semantics. A selected JSON field is partial
coverage, not full behavior preservation. Zero-overlap merge is unmeasured,
not perfect. Reattachment without complete context remains unresolved.
Low-entropy hashes and lineage are sensitive GODD. Deleting a view cannot
erase immutable history or prior copies.

The exact effect-free evaluator image is verified through consumption.
Full production interpreter/OS/key-custody/deployment qualification is not
claimed; the deployment receipt stays refused.

## Experimental history is not first-Grail authority

The prior unpublished seed/lens/iteration implementation is isolated under
[`experimental/`](protocols/rapp-workspace/grail-1.0/experimental/README.md).
It is not imported by the safe kernel or CLI, and requires
`RAPP_ALLOW_UNQUALIFIED_EXPERIMENTS=1` to run its separate regression suite.
Those tests preserve research evidence; they are **not** first-Grail release
acceptance and cannot authorize its old in-graph adoption or migration.

The [pre-Grail public archive](protocols/rapp-workspace/historical/pre-grail/README.md)
preserves eight byte-exact files, including both published 1.1 and both 2.0
SPEC snapshots. Old IDs and pins retain their meaning. No missing historical
1.0 bytes are fabricated, and the new validator refuses old IDs/wrong pins.

Existing [`rapp-hive/1`](protocols/rapp-hive/1/SPEC.md),
[`rapp-federation/1`](protocols/rapp-federation/1/SPEC.md) and their locked
Private Hive capability remain unchanged independent profiles. They are not
a workaround for disabled first-Grail effects.

## One shareable skill and checks

[`SKILL.md`](SKILL.md) is the single-file operating entry; normative
specifications/schemas remain separate. Repository skills under `.github/skills`
carry the same safety boundary.

```bash
mkdir -p .validation/test-artifacts
export TMPDIR="$PWD/.validation/test-artifacts"
export RAPP1_PATH="<EXPLICIT_RAPP1_CHECKOUT>"
python3 -B tools/frame_lens.py schemas
python3 -B tools/frame_lens.py pins
python3 -B -m unittest discover -s tests -v
python3 -B tools/frame_lens.py conformance --rapp1-path "$RAPP1_PATH"
python3 -B -m unittest discover -s .github/skills/rapp-private-hive/tests -v
python3 -B protocols/rapp-hive/1/reference/hive_conformance.py
python3 -B protocols/rapp-federation/1/reference/schema_source.py --check
python3 -B protocols/rapp-federation/1/reference/conformance.py
RAPP_ALLOW_UNQUALIFIED_EXPERIMENTS=1 python3 -B -m unittest discover -s tests/experimental -v
python3 -m py_compile tools/*.py protocols/rapp-workspace/grail-1.0/reference/*.py tests/*.py
```

The first-Grail kernel/conformance is stdlib-only. Existing signed sibling
tests retain their documented dependencies. Tests use public/synthetic data
and scan nonzero actual RAPP/1 frames; a zero-artifact pass is insufficient.

Owner publication/ratification, independent anchors and signed profile/genesis
registration, protected monotonic hosting, qualified native snapshot/migration
adapters and safe production execution remain separate blockers.

MIT. External source provenance does not relicense papers or confer authority.
