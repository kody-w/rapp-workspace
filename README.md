# RAPP Workspace/1

**RAPP-valid ≠ accurately observed ≠ semantically faithful ≠ currently
authorized ≠ safely deployable.**

The core protocol identifier is
[`rapp-workspace/1`](protocols/rapp-workspace/1/SPEC.md).
All earlier workspace protocol lines are prototypes. RAPP/1 still owns the
unchanged eleven-key frame, identities, hashes, signatures, eggs and signed
estate registry.

## Workspace/1 core protocol

The Workspace/1 core reference deliberately narrows the previous experiments:

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

[Normative safety matrix](protocols/rapp-workspace/1/safety-matrix.json)
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
and does not imply estate activation.

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

## Explicitly disabled in Workspace/1 core

Remote model submission, loopback/network access, ambient imports/host tools,
arbitrary code, external or partitioned effects, public redistribution,
native rebinding, live migration, live O(delta) monitoring, authoritative
merge, timed physical erasure, repository cloning, non-default branch history,
actual Hive publication and learned semantic-capability claims are **disabled**
until their required proofs exist.

Replay proves reproducibility, not semantics. A selected JSON field is partial
coverage, not full behavior preservation. Zero-overlap merge is unmeasured,
not perfect. Reattachment without complete context remains unresolved.
Low-entropy hashes and lineage are sensitive GODD. Deleting a view cannot
erase immutable history or prior copies.

The exact effect-free evaluator image is verified through consumption.
Full production interpreter/OS/key-custody/deployment qualification is not
claimed; the deployment receipt stays refused.

## Recursive estates without folder management

Workspace/1 can frame complete, bounded catalog shards for an authorized
repository estate while retaining recursive default-branch maps in private
manager-owned storage. It refuses missing shards, duplicate entries, parent
cycles and branch-history expansion. The provider-default claim remains
explicitly unproven until a separately qualified provider receipt exists.

Organization is iterative: the controller measures unassigned/duplicate
entries, depth and largest bucket. Broad trees produce `needs-refinement`;
repeated non-improvement produces `no-progress`. Outcome queries resolve to
candidate catalog IDs without granting file access or claiming semantic
fidelity.

Private Hive output is proposal-only. Public-source entries may be proposed;
private entries remain withheld without exact external owner approval, and
even an approved proposal cannot publish or mutate the signed NAS authority.

## Prototype history is not Workspace/1 core authority

The [prototype archive](protocols/rapp-workspace/prototypes/README.md) preserves
the complete previously named candidate, its earlier experiments, and
byte-exact published 1.1/2.0 snapshots. Prototype code is never imported by the
core CLI. Its archived tests are research evidence, not Workspace/1 acceptance,
and cannot authorize old in-graph adoption or migration.

Existing [`rapp-hive/1`](protocols/rapp-hive/1/SPEC.md),
[`rapp-federation/1`](protocols/rapp-federation/1/SPEC.md) and their locked
Private Hive capability remain unchanged independent profiles. They are not
a workaround for disabled Workspace/1 core effects.

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
python3 -m py_compile tools/*.py protocols/rapp-workspace/1/reference/*.py tests/*.py
```

The Workspace/1 core kernel/conformance is stdlib-only. Existing signed sibling
tests retain their documented dependencies. Tests use public/synthetic data
and scan nonzero actual RAPP/1 frames; a zero-artifact pass is insufficient.

Independent anchors and signed estate activation, protected monotonic hosting,
qualified native snapshot/migration adapters and safe production execution
remain separate deployment blockers.

MIT. External source provenance does not relicense papers or confer authority.
