# Proposal 0024: Editable front doors for RAPP Workspace/1

- **Status:** draft, not accepted.
- **Gap:** G24, "RAPP Workspace/1's frozen identity pins its READMEs". This
  proposal is the fix proposed to the owning specification, so the gap's
  health word is `proposed`. The successor identity it defines is a
  `candidate`: a normative draft that no estate has accepted yet.
  Workspace/1 itself is `specified`: normative, pinned, and not yet activated
  by any estate.
- **Home spec and sections:** `rapp-workspace/1`
  ([`SPEC.md`](../../protocols/rapp-workspace/1/SPEC.md) §§1, 2, 3, 4.1, 11
  and 14) and its exact-byte runtime manifest
  ([`manifest.json`](../../protocols/rapp-workspace/1/manifest.json), written
  by `protocols/rapp-workspace/1/reference/pins.py`); for the owner-only
  acceptance step, this repository's copy of `rapp-work-sdk/1`
  ([`SPEC.md`](../../protocols/rapp-work-sdk/1/SPEC.md) §§1, 2, 4 and 8).
- **Branch:** `experimental/gap-g24-successor-candidate`.
- **Intended release:** the next RAPP/1 LTS lock-in scope that includes
  `kody-w/rapp-workspace`. No version number or brand changes.

## Summary

Front doors stay editable. READMEs, badges and start-here links are never
pinned by a frozen identity. Frozen identities pin only normative bytes:
specifications, schemas, reference code, tests and AI instruction files such
as `SKILL.md`.

Today the Workspace/1 runtime manifest pins four READMEs and the root
`SPEC.md`, which describes itself as navigation. So a README edit changes the
frozen Workspace/1 identity. This proposal fixes that **additively**, in three
steps:

| Step | What happens | Frozen bytes and pins | Who |
|---|---|---|---|
| 1. This change | Records a candidate successor manifest, `rapp-workspace-file-manifest/2` (SHA-256 `e99a51d355bd66c71017f4451cdd54bc47ed2b99c4fe0d939e1c494288148814`, 7,484 bytes), that pins no README and no navigation, plus one index entry for it (`status: candidate`, `authority: false`) | None change. The current manifest (`f1165f94…`), its index entry and every consumer pin stay byte-identical | Merges like any proposal; accepts nothing |
| 2. Acceptance | Switches the consumers to the successor: the Workspace/1 runtime itself, the `rapp-workspace/1` index entry and `rapp-work-sdk/1` | The current manifest is retained byte-for-byte as named history | **Owner only** |
| 3. Front door | The README network header (badge and "Start here" link) lands | None; no enforced identity pins a README any more | The network workstream's ordinary header PR |

Step 1 alone does not make the README editable: the current manifest still
pins it until the owner switches. The tests prove both halves.

## Context

Citations are to `kody-w/rapp-workspace` `main` at `52d4f19` unless noted.

1. **The current manifest pins four front doors and the root navigation
   page.** `protocols/rapp-workspace/1/reference/pins.py` lines 35–41 list
   these in `repository_evidence`:
   - `README.md`
   - `protocols/rapp-workspace/1/reference/README.md`
   - `protocols/rapp-workspace/prototypes/README.md`
   - `protocols/README.md`
   - the root `SPEC.md`, which says "This root document is navigation, not a
     second normative specification" (line 12) and otherwise holds a summary
     and links. The normative contract is
     `protocols/rapp-workspace/1/SPEC.md`, pinned under `normative`.

   They sit beside `SKILL.md`, `tools/frame_lens.py`, two core test files and
   two `.github` skill `SKILL.md` files.
2. **That manifest is the runtime identity.**
   - The SPEC makes the exact-byte manifest normative (`SPEC.md` line 11).
   - §3 requires every fresh execution to "requalify the entire pinned
     runtime manifest" (line 107).
   - §4.1 requires a live activation document to bind the "runtime
     **manifest** SHA-256" (line 125).
   - `safe_kernel.py` imports the generator (`from pins import encode,
     manifest`, line 16). `Controller.qualify()` (lines 476–480) refuses
     unless `manifest.json` hashes to the policy's `runtime_sha256` **and**
     equals a fresh `encode(manifest())`. So the kernel re-derives the
     manifest from the generator, README bytes included.
3. **The hash is recorded in many places.**
   - `protocols/index.json` lines 37–38, checked by `pins.py` `check_index()`
     (lines 68–78), which requires the `rapp-workspace/`-named index entries
     to be exactly one, equal to `index_profile()`.
   - The SDK sidecar profile, as `workspace_sibling.manifest_sha256`
     (`protocols/rapp-work-sdk/1/reference/pins.py` lines 128 and 233), its
     two retained history profiles, the `4b4fc213` prior-release fixture and
     the vendored skill copy under `.github/skills/rapp-work-sdk/vendor/`.
   - SDK conformance (`conformance.py` line 18) refuses with "Workspace/1
     manifest bytes changed" when the manifest moves (line 118).
   - The SDK tests pin the hash (`tests/test_rapp_work_sdk.py` line 25) and
     require exactly one `rapp-workspace/` index entry (lines 173–174).
4. **The SDK file manifest pins a README too.** SDK `pins.py` line 223
   selects `reference/*.py` **and** `reference/*.md`, so the SDK's
   `reference/README.md` is pinned.
5. **Consequence.** One added README line changes `README.md`'s hash, the
   manifest's bytes and `f1165f94…`. That breaks qualification, the index
   pin, SDK conformance and the SDK tests, so the repository holds back its
   RAPP/1 network header (badge and "Start here" link).
6. **The pinned AI instruction files call READMEs and docs verified.**
   - `SKILL.md` lines 176–177 (and the identical
     `.github/skills/rapp-workspace/SKILL.md`): "Read the verified reference
     README/API automatically … Additional sibling suites and `py_compile`
     are in README." Line 183: "Inspect their verified help/lock/docs".
   - `.github/skills/autonomous-rapp-estate-manager/SKILL.md` line 63: "see
     the verified README/help from the same checkout."

   Once READMEs are unpinned, those pinned instructions would point an AI at
   unverified text as though it were verified. A correct successor must pin
   corrected, self-contained instruction text.
7. **So the successor needs bytes that cannot exist in place yet.** Making
   READMEs editable requires a new generator (`reference/pins.py`) and
   corrected instructions (three `SKILL.md` files). All four files are pinned
   by the current manifest: changing any of them in place would move
   `f1165f94…` before the owner accepts anything.
8. **SDK generations are keyed by parent commit.** A sidecar generation must
   hold its pin's exact profile bytes (`scaffold.py` `_generation_at`,
   line 1229; "profile bytes changed", line 1252), and the SDK SPEC allows
   replacement only through "a reviewed profile update, an explicit forward
   update plan, retained source profile bytes, and new conformance evidence"
   (§1, lines 19–21). Re-pinning the sibling manifest therefore needs a new
   generation at a real `kody-w/rapp-1` commit. As of 2026-09-26, verified
   through the GitHub API, `kody-w/rapp-1` `main` is
   `bae4e3cacc33e82e7fcf9fe73d2fd043da97801d`; since
   `591e014ad39e223b00ab343ae26e5d9a867ebeee` only `README.md` and
   `.rapp/member.md` changed, and `protocols/rapp-work/1/SPEC.md` is
   byte-identical (SHA-256
   `283359355c3fe2858e28744368255683af3ed28a68e290e56c231e7d4b13c08e`,
   11,427 bytes).
9. **The lock tooling needs one fix before the switch.** `tools/skill_locks.py`
   line 33 sorts `Path` objects component by component, while every lock
   verifier compares path strings (`.github/skills/rapp-work-sdk/scripts/scaffold.py`
   line 62, `prepare_workspace.py` line 116). They disagree as soon as one
   directory name extends another with `-`, such as a new
   `fixtures/prior-release-591e014/` beside `fixtures/prior-release/`: the
   tool writes a lock that the scaffold preflight refuses.
10. **No estate activates Workspace/1.** The index records
    `"signed_activation": false`. As of 2026-09-26 this repository holds no
    live activation document, and the estate kit's unsigned registry drafts
    (a workstream artifact that is not public) pin only the Workspace/1 SPEC
    hash `80135ae0…`, which nothing here changes. As of the same date, a code
    search of the public `kody-w` estate found `f1165f94…` only in this
    repository and its public mirror (`kody-w/rapp-monorepo`, under
    `repos/rapp-workspace/`).

## Design decisions and alternatives rejected

**Decisions.**

1. **Additive now, switch later.** This change adds files and one index
   entry. The current manifest, its index entry and every consumer pin stay
   byte-identical; the tests assert it. Switching consumers is the owner's
   acceptance.
2. **The candidate is the final successor, not a preview.** The four
   post-switch files (point 7) are carried as inert staged bytes, so the
   candidate hash is exactly the hash that becomes current at the switch.
   The owner accepts a concrete identity, and the switch is mechanical.
3. **Everything recorded ahead of the switch is inert.** The candidate
   (`successor/manifest.json.staged`) and the four staged files
   (`successor/staged/*.staged`) carry a `.staged` suffix: no skill loader
   sees a `SKILL.md`, no import or `py_compile` sees a `.py`, and no reader
   or crawler that looks for `manifest.json` finds a second current-looking
   manifest. Nothing reads them at runtime; qualification reads only
   `manifest.json`.
4. **Regenerated with the repository's own tools.** The candidate manifest is
   what the staged generator itself writes after the switch.
   `tools/workspace_successor.py` applies the Workspace side of the switch to
   a scratch copy of the working tree under `.validation/`, runs the staged
   generator there unmodified, and records the result. Nothing is
   hand-edited.
5. **Normative bytes only, by allowlist plus tripwire.** The staged
   generator pins an explicit tuple of repository evidence and refuses to
   build any manifest that lists a front door anywhere. The root `SPEC.md`
   leaves the allowlist because it declares itself navigation; the normative
   SPEC stays pinned under `normative`.
6. **History is retained and never regenerated.** At the switch the current
   bytes move to
   `history/f1165f947cb5d7554906012a174a854b28454403e41e8166925a364a68680370/manifest.json`.
   The generator verifies their SHA-256, length, schema, profile and `core`
   status, so a prototype manifest can never be named as a predecessor
   (SPEC §2).
7. **The Workspace/1 SPEC stays byte-identical.** The contract (SPEC, safety
   matrix, schemas) does not change; only the runtime inventory does.
   Changing the SPEC would move `spec_sha256`, which the estate kit pins, for
   no semantic gain.
8. **One index entry, outside the current namespace.** The candidate entry
   is named by its token, `rapp-workspace-file-manifest/2`, and never
   `rapp-workspace/…`: `check_index()` and the SDK tests require exactly one
   `rapp-workspace/` entry, and that entry must stay the current one. It says
   `status: candidate`, `authority: false`, `acceptance: owner-only`.
9. **The switch retires the candidate entry.** The staged generator's
   `--write-index` drops an entry named after its own schema, and its
   `check_index()` fails while one remains, so the switch cannot leave a
   dangling candidate.
10. **The staged generator also fixes the in-place index writer.** It
    replaces the Workspace entry in place and keeps `generated_utc`. The
    current writer drops the entry, re-appends it and resets
    `generated_utc` (lines 102–103), so running it on `main` changes the
    index. The current writer is pinned and stays as it is until the switch.
11. **The tool never writes through a link.** Two layers keep every write
    in the scratch copy inside it: copying skips every symlink, every special
    or unreadable entry, and scratch or build products, so the copy holds only
    readable regular files and directories; and the two files the staged
    generator writes there (`manifest.json` and the index) must be regular
    files in the copy, or the tool refuses with a precise reason. A skipped
    file the generator needs fails closed as missing, and an untracked
    symlink, socket or unreadable file anywhere in a developer's tree (a
    virtual environment, a convenience link) is simply not copied. Other
    untracked regular files are copied; as with `/1`, an untracked
    `reference/*.py` or `schemas/*.json` therefore enters the regenerated
    manifest. The staged, canonical and
    recorded files are read through the reference's no-follow `read_file`;
    `.DS_Store` and editor swap, backup and lock files in the staged tree are
    skipped. The tool
    refuses a symlinked or non-directory component before it creates,
    replaces or removes anything, and creates each scratch copy owner-only
    (`0o700`), removing it after the run (read-only copied directories
    included) or failing if it cannot. Under `--write` it first checks
    that neither recorded file is a symlink or has another hard link, and
    then replaces each atomically (a temporary file renamed through the
    directory descriptor, keeping the file's mode).

**Alternatives rejected.**

- **Mutate `/1` in place** (drop the READMEs, keep the label, name no
  predecessor). Every `f1165f94` receipt and SDK history profile would point
  at a hash with no retained bytes; recording the lineage needs
  `predecessors`, which changes the key set and so moves the label
  (Art. 2).
- **Switch in the same change** (replace `manifest.json`, repoint the index
  and the SDK). That is the owner's acceptance, not a proposal; it moves
  every consumer before anyone accepts the successor. An earlier draft of
  this proposal did exactly that; it survives only as input to the
  owner-only step (see "Step 2").
- **Record a preview that pins today's `pins.py` and `SKILL.md`.** Its hash
  would change at the switch, and its pinned instructions would still call
  READMEs verified. The owner would be accepting a hash nobody will ever pin.
- **Keep the root `SPEC.md` pinned.** It is navigation by its own words, so
  pinning it contradicts "frozen identities pin only normative bytes", and
  unpinning it later would need a further successor and another SDK
  generation.
- **Keep `/1`.** Front doors stay frozen and the header stays blocked.
- **Pin READMEs in a separate "non-identity" lock.** A red gate on a README
  edit is still a pin (Art. 8), so front doors would still not be editable.
- **Mint `rapp-workspace/2`.** The protocol contract is unchanged; Art. 2
  moves the token of the thing whose shape changes, which is the manifest.
- **A `.github/README.md` beside the root README.** Two READMEs would drift,
  and visitors would see a copy, not the reviewed file.

## Proposed change

### Normative definition of the successor token

Activated at acceptance and enforced by the staged generator; this is not a
SPEC edit.

> **`rapp-workspace-file-manifest/2`.** The Workspace/1 runtime manifest is
> a JSON object with exactly these members, in this order: `schema`,
> `profile`, `brand`, `parent`, `authority`, `status`, `signed_activation`,
> `assurances`, `normative`, `reference`, `repository_evidence`,
> `provenance`, `prototype_catalog`, `authority_boundary`,
> `live_activation`, `production_key_custody`, `synthetic_activation`,
> `predecessors`. `schema` is `"rapp-workspace-file-manifest/2"`. `profile`,
> `brand`, `parent`, `authority`, `status`, `signed_activation`,
> `assurances`, `authority_boundary`, `live_activation`,
> `production_key_custody` and `synthetic_activation` carry the values of
> the retained `rapp-workspace-file-manifest/1` manifest `f1165f94…`.
> `normative`, `reference` and `repository_evidence` are arrays of file
> records, and `provenance` and `prototype_catalog` are single file records,
> all computed over the current bytes. The manifest's bytes are the UTF-8
> JSON text with two-space indentation, non-ASCII characters unescaped,
> members in the orders stated here and one trailing newline (the reference
> `encode`).
>
> A file record is a JSON object with exactly the members `path`, `sha256`
> and `bytes`, in that order: a relative path, the lowercase hex SHA-256 of
> the file's exact bytes and its length. `normative`, `reference` and
> `provenance` paths are relative to the protocol directory;
> `repository_evidence` and `prototype_catalog` paths are relative to the
> repository root. "File-name order" below means ascending Unicode
> code-point order of the file names.
>
> - `normative` pins `SPEC.md`, then `safety-matrix.json`, then every
>   `schemas/*.json` in file-name order.
> - `reference` pins every `reference/*.py` in file-name order.
> - `repository_evidence` pins only normative repository bytes: reference
>   entry points, core tests and AI instruction files, exactly `SKILL.md`,
>   `tools/frame_lens.py`, `tests/test_safe_kernel.py`,
>   `tests/test_p0_hardening.py`, `.github/skills/rapp-workspace/SKILL.md`
>   and `.github/skills/autonomous-rapp-estate-manager/SKILL.md`, in that
>   order. It MUST NOT list a human-facing front door or a navigation page.
> - `provenance` pins `provenance.json`; `prototype_catalog` pins
>   `protocols/rapp-workspace/prototypes/index.json`.
>
> A path whose final component, case-folded, is `readme` or begins with
> `readme.` is a front door. A generator MUST refuse to build a manifest that
> lists a front door anywhere.
>
> `predecessors` lists retained predecessor manifests, oldest first. Each
> entry is a JSON object with exactly the members `schema`, `path`, `sha256`
> and `bytes`, in that order, where `path` is
> `history/<sha256>/manifest.json` relative to the protocol directory.
> Generators and qualification MUST verify the retained bytes' SHA-256 and
> length, and that they declare the entry's `schema`,
> `profile: "rapp-workspace/1"` and `status: "core"`. They MUST NOT
> regenerate the retained bytes.
>
> A predecessor is lineage for inspecting history, never a current runtime.
> Qualification accepts only the current manifest bytes. Receipts and
> activation documents bound to a predecessor remain historical evidence
> (SPEC §11); new execution requires current qualification.

### Step 1: the candidate (this change)

**Added:**

- `protocols/rapp-workspace/1/successor/manifest.json.staged`: the
  candidate,
  `e99a51d355bd66c71017f4451cdd54bc47ed2b99c4fe0d939e1c494288148814`,
  7,484 bytes. Its bytes are exactly the post-switch `manifest.json`, so
  they carry the labels they will have once current (`status: "core"`,
  `authority: true`). Until then the `.staged` suffix and the index entry
  (`status: candidate`, `authority: false`) say it is not current, and no
  runtime reads it (the tests prove that a controller pinned to it refuses).
- `protocols/rapp-workspace/1/successor/staged/` holds the exact post-switch
  bytes of the four pinned files the switch replaces:
  - `protocols/rapp-workspace/1/reference/pins.py.staged`, the `/2`
    generator;
  - `SKILL.md.staged` and `.github/skills/rapp-workspace/SKILL.md.staged`
    (identical, as the live files are);
  - `.github/skills/autonomous-rapp-estate-manager/SKILL.md.staged`.

  `python3 -B tools/workspace_successor.py --diff` prints the exact change.
- `tools/workspace_successor.py`: verifies the candidate (default) or
  regenerates the candidate and its index entry (`--write`).
- `tests/test_front_door.py`: 31 tests (see "Conformance and test
  vectors").
- This proposal.

**Changed:** `protocols/index.json` gains one entry, appended to `profiles`;
no other byte changes:

```json
{
  "name": "rapp-workspace-file-manifest/2",
  "human_name": "RAPP Workspace/1 runtime manifest successor",
  "parent": "rapp/1",
  "profile": "rapp-workspace/1",
  "authority": false,
  "status": "candidate",
  "acceptance": "owner-only",
  "proposal": "docs/proposals/0024-editable-front-door.md",
  "successor_of": {"path": "protocols/rapp-workspace/1/manifest.json", "sha256": "f1165f94…", "bytes": 7990},
  "spec_path": "protocols/rapp-workspace/1/SPEC.md", "spec_sha256": "80135ae0…", "spec_bytes": 31443,
  "manifest_path": "protocols/rapp-workspace/1/successor/manifest.json.staged",
  "manifest_sha256": "e99a51d3…", "manifest_bytes": 7484,
  "staged_path": "protocols/rapp-workspace/1/successor/staged",
  "generator": "tools/workspace_successor.py"
}
```

**Unchanged:** every other file in the repository, verified by diff. The
tests assert the parts that matter for identity: the current manifest
(`f1165f94…`, 7,990 bytes, which fixes every file it pins), its index entry,
and the `rapp-work-sdk/1` sibling pins in the SDK profile, file manifest and
vendored copies. The repository has no CHANGELOG, so none is added.

**Staged instruction text.** In both `SKILL.md` copies (lines 167–186) the
verification block gains `py_compile`, the sibling suites move in from the
README, and the README delegation is replaced:

> ```bash
> python3 -m py_compile tools/*.py protocols/rapp-workspace/1/reference/*.py tests/*.py
> ```
>
> Sibling suites run under their own contracts and keep their documented
> dependencies; they are never Workspace/1 core acceptance:
>
> ```bash
> python3 -B -m unittest discover -s .github/skills/rapp-private-hive/tests -v
> python3 -B protocols/rapp-hive/1/reference/hive_conformance.py
> python3 -B protocols/rapp-federation/1/reference/schema_source.py --check
> python3 -B protocols/rapp-federation/1/reference/conformance.py
> ```
>
> This skill, the normative SPEC, schemas, reference code and core tests are
> manifest-pinned; no second skill install is needed. READMEs and the root
> `SPEC.md` are editable, unpinned navigation: never treat them as verified
> API, commands or authority.

and "Inspect their verified help/lock/docs;" becomes "Inspect their own
specifications, checksum locks and `--help`, never a README;".

In `.github/skills/autonomous-rapp-estate-manager/SKILL.md`, line 63 becomes
"and retention flags; see `tools/frame_lens.py demo --help` from the same
checkout." followed by "READMEs are editable, unpinned navigation: never treat
them as verified instructions or authority." (`demo --help` lists
`--fixture`, `--allow-capture` and `--allow-retention`.)

### Step 2: owner-only acceptance (switching consumers)

The owner accepts `e99a51d3…` by merging one switch pull request, prepared by
the spec-gaps workstream on request, that does all of the following
together. The Workspace part alone would leave SDK conformance red, so the
parts cannot land separately.

a. **Workspace/1 runtime**, applied with the repository's tools:
   1. Copy `protocols/rapp-workspace/1/manifest.json` byte-for-byte to
      `protocols/rapp-workspace/1/history/f1165f947cb5d7554906012a174a854b28454403e41e8166925a364a68680370/manifest.json`.
   2. Copy each `successor/staged/<path>.staged` to `<path>`.
   3. Run `python3 -B protocols/rapp-workspace/1/reference/pins.py --write
      --write-index`. It writes `manifest.json`, which must be byte-identical
      to `successor/manifest.json.staged`; repoints the `rapp-workspace/1`
      index entry's `manifest_sha256` and `manifest_bytes` in place; and
      retires the candidate entry.
   4. Delete `protocols/rapp-workspace/1/successor/` and
      `tools/workspace_successor.py`, and replace `tests/test_front_door.py`
      (which loads that tool and asserts the pre-switch state) with
      post-switch tests of the tree built from its switch vectors.
b. **Lock tooling:** `tools/skill_locks.py` sorts by path string (Context 9),
   with a test, before any lock is regenerated. On `main` this is a byte
   no-op.
c. **`rapp-work-sdk/1`**, under its own replacement rule (SDK SPEC §1): a new
   generation, sequence 3, pinned to the `kody-w/rapp-1` commit current at
   acceptance whose `protocols/rapp-work/1/SPEC.md` is byte-identical
   (`bae4e3cacc33e82e7fcf9fe73d2fd043da97801d` as of 2026-09-26);
   `workspace_sibling` `manifest_sha256` becomes `e99a51d3…` (`spec_sha256`
   unchanged), and SDK SPEC §8's "byte-for-byte stability of the existing
   `rapp-workspace/1` identity" (lines 185–186) is read relative to the
   sibling pin each generation records: generation 3 proves stability of
   `e99a51d3…`, as generations 0–2 do for `f1165f94…`; `591e014…` is retained as `migration-source-only` with its
   exact profile bytes; the SDK file manifest stops pinning
   `reference/README.md` and gains the same front-door tripwire (its
   `rapp-work-sdk-file-manifest/1` label stays: key set, record grammar and
   hash rule are unchanged, and which files it inventories is content, which
   already changes between SDK releases as history profiles and fixtures are
   added); SDK conformance and test constants move to the successor; a real
   `591e014` prior-release fixture, `fixtures/prior-release-591e014/`, is
   produced by the unmodified scaffold; the vendored skill copy is synced;
   both skill locks and the Private Hive constants are regenerated by the
   fixed `tools/skill_locks.py`; and `docs/rapp-work.md` names the new pin.
   Generated artifacts (profiles, parent pin, manifests, index entries,
   vendored copy, locks) go through the SDK's
   `--write-parent-profile/--write/--write-index` path and
   `tools/skill_locks.py`, never by hand; code and constants are reviewed
   edits. As of 2026-09-26, a reference draft of this step exists on
   `experimental/gap-g24-editable-front-door` (commit `780f072`); it predates
   the additive split, uses an earlier successor hash, and must be rebuilt on
   top of the merged candidate before use.
d. **Estate:** nothing needs re-signing; the estate kit pins only the
   Workspace/1 SPEC hash `80135ae0…`. Any draft that records the runtime
   manifest hash must record `e99a51d3…` instead.
e. **This proposal:** its Status becomes "accepted" with the acceptance date,
   and its Summary and Step 1 are recast in the past tense, in the same pull
   request.

### Step 3: the README network header

After the switch is on `main`, the network workstream creates (or rebases)
its header branch for this repository on `main`, adds the header block to
`README.md` only, and runs the repository's own checks
(`tools/frame_lens.py pins`, the core tests, core conformance, and the SDK
pins, conformance and tests). They stay green because no enforced identity
pins a README any more; the archived prototype manifests still record README
hashes as history, and no check verifies them. The network workstream then
removes this repository from its `held` header exceptions and refreshes the
hash its notes quote. Before the switch, that PR would fail: the current
manifest still pins `README.md`.

## Token and compatibility analysis

- **Art. 2 (one label, one shape).** The Workspace manifest's key set
  changes (`+predecessors`), so the successor mints
  `rapp-workspace-file-manifest/2`, whose member list is enumerated above.
  Which files a manifest inventories is content, not shape: that is why the
  SDK file manifest keeps `rapp-work-sdk-file-manifest/1` at the switch
  (Step 2c).
  The `/1` label keeps meaning exactly the current bytes, which stay current
  until the switch and are retained as history after it. (The archived
  `grail-1.0` prototype manifests reuse the `/1` label with other key sets;
  that is pre-existing prototype history, untouched here, and the `/2`
  definition does not refer to them.)
- **The index.** `rapp-estate-protocol-index/1` keeps its shape. Its
  `profiles` entries already differ in their members; one entry is added to
  the array, and no top-level member changes.
- **Art. 3 (no legacy).** At the switch the retained manifest is a published,
  content-addressed artifact, kept bit-exact and never served as current. The
  way out is forward.
- **Art. 4 (growth by registration).** No frame kind, envelope or door
  changes; the change stays inside an application profile's own inventory.
- **Art. 8 (red oracles).** No test is skipped, muted or weakened. Every
  existing oracle still asserts `f1165f94…` and passes unchanged.
- **Art. 9 (claims are computed and dated).** Live-state facts above carry
  their capture date.
- **Art. 10 (one canonicalizer).** No RAPP/1 primitive is copied or
  re-typed; frames are verified only through the byte-pinned RAPP/1 checkout
  `dda32d741c7218f41443a5bd17eebfe0eae82cb7`. The manifests keep their
  inventory encoding. The tool imports the reference's `encode`, file-record
  builder, SHA-256 helper and no-follow file primitives; it restates only the
  one-line front-door rule, which a test holds equal to the staged
  generator's.
- **Art. 18 (the wire is frozen).** Canonicalization, hashes, the RAPPID
  grammar, the eleven-key envelope and eggs are untouched.

## Security and privacy analysis

**Before the switch** nothing changes at runtime. Qualification reads only
`manifest.json`; a controller pinned to the candidate hash refuses with
`runtime-qualification-required` before creating storage. The tool executes
only the staged generator, a repository file under review, inside a scratch
copy; it never executes discovered or received code. The copy holds no
symlink, and the two files the staged generator writes in it are checked to
be regular files first, so every path-based write in it (the tool's and the
generator's) stays inside it. The tool reads the staged, canonical and
recorded files through no-follow paths, refuses a symlinked or
non-directory path component before it creates, replaces or removes
anything, and under `--write` checks both recorded files before atomically
replacing either, refusing a symlink or a file with another hard link. So it
cannot write outside the scratch copy (or, with `--write`, outside the
candidate and the index). The copy includes untracked files, so each scratch
copy is created owner-only (`0o700`) and removed after the run.
It also refuses staged symlinks, front doors, generated files, the candidate
itself, new files, no-op changes and staged files the candidate does not
pin. The test fixture copies the working tree the same way, asserts that its
copy holds no symlink, and resolves a relative RAPP/1 path once, as core
conformance does. So untracked symlinks, special or unreadable files, editor
files in the staged tree, a leftover retained predecessor and a stale scratch
copy from a killed run affect neither the tool nor the tests.

**After the switch**, an unpinned README or navigation page can change
human-facing prose, badges and links. It cannot:

- be read by any runtime (the kernel, qualification, the SDK scaffold, the
  skill wrapper and the Private Hive scripts never load a README);
- grant authority (authority comes only from the external policy and
  activation);
- change qualification, SDK install or update, or any pinned byte;
- instruct an AI through these skills, whose pinned text now calls READMEs
  unverified navigation and carries its own commands.

**What stays pinned:** every normative byte, all reference code, the entry
tool, the core tests, provenance, the prototype catalog and all three AI
instruction files. The tests prove that editing any of 13 such files moves
the identity and makes qualification refuse.

**History integrity:** a tampered retained predecessor refuses with
`retained-predecessor-manifest-changed`, a missing one with
`retained-predecessor-missing`, and only a retained core Workspace/1
manifest, named by an exact `{schema, path, sha256, bytes}` record, can be
listed as a predecessor.

**Residual risk:** humans, and AIs not using these skills, may still follow
README commands. README edits are reviewed through pull requests rather than
detected by pins, and README claims fall under Art. 9.

**Privacy:** all fixtures are synthetic (`rappid:@fixture/…`,
`example.com`). No local paths, secrets or private names are added, and the
repository privacy scan reports 0 findings.

## Migration

- **Until the switch:** nothing migrates. Sidecars, controllers and receipts
  keep using `f1165f94…`. The facts below are as of 2026-09-26
  (Context 10).
- **SDK sidecars at `591e014`** keep verifying after the switch; a
  same-workspace install refuses with "different pin requires an explicit
  update"; the operator runs `scaffold.py plan-update` then `update` with the
  exact plan digest. Sidecars at `4b4fc213` or `1c0e0b7c` update directly.
  No update touches native bytes or uses the network.
- **Workspace/1 controllers bound to `f1165f94…`:** no estate activation
  exists. A store created under `f1165f94…` refuses to reopen under the
  successor, its frames stay inspectable through
  `verify_historical_archive`, and new work uses a fresh controller
  directory, as the SPEC and README already require.
- **Activation documents bound to `f1165f94…`:** none exist. A future one
  needs a new owner-issued document binding `e99a51d3…`; nothing rebinds
  automatically.

## Rollback

- **Before merge:** don't merge; nothing else changes.
- **After merge, before the switch:** revert the merge. It removes only
  added files and the candidate index entry; no consumer depends on them.
- **After the switch, before any sidecar installs or updates to the new
  generation:** revert the switch pull request; `f1165f94…` becomes current
  again.
- **After a sidecar has installed or updated to the new generation:** its pin
  would be unknown to reverted code, and sidecars cannot downgrade (SDK §4),
  so roll forward (Art. 3): mint a further successor that retains both
  manifests as predecessors.

## Conformance and test vectors

`tests/test_front_door.py` runs in CI twice: directly, and inside the core
conformance runner, which refuses skipped tests. It has 31 tests.

1. **The current identity never moves** (`CurrentIdentityTests`, 4 tests).
   - `manifest.json` is `f1165f94…` (7,990 bytes), equals the current
     generator's output, and is the only `rapp-workspace/` index entry.
   - The SDK profile and file manifest, and their vendored copies, still pin
     `f1165f94…`.
   - A controller pinned to the candidate refuses before creating storage.
   - Before the switch a README edit still moves the current identity (pins
     fail, qualification refuses), while the candidate still verifies.
2. **The candidate is recorded exactly** (`CandidateRecordTests`, 6 tests).
   - The candidate is `e99a51d3…`: the `/1` members plus `predecessors`,
     identical normative pins, a `reference` that differs only in
     `reference/pins.py`, no README or navigation page anywhere, and records
     whose members and order match the normative definition.
   - The staged files are exactly the four switched files; each is pinned by
     the candidate, and each live file is exactly what `/1` pins.
   - The staged instructions never call a README or docs verified, never
     delegate to a README, and carry the core and sibling commands.
   - The index holds exactly one candidate entry, not accepted.
   - The tool's check passes, and `--write` reproduces every committed byte,
     from an index without the entry and over a longer, stale candidate and
     entry, keeps non-default file modes, and is idempotent.
   - `--diff` shows only the four switched files.
3. **The switch works** (`SwitchProofTests`, 8 tests), applied independently
   of the tool to a scratch copy.
   - `manifest.json` becomes exactly the candidate; the index bytes equal
     `main`'s with the candidate entry retired and only the
     `rapp-workspace/1` manifest hash and size changed; pins pass.
   - The two pinned core suites (81 tests) pass on the switched tree.
   - Qualification accepts the successor and refuses `f1165f94…`.
   - Editing each of the four READMEs or the root `SPEC.md`, or every README
     in the repository, keeps the identity, the pins and qualification.
   - Editing any of 13 pinned files moves the identity, fails the pins and
     refuses qualification before storage exists.
   - A tampered retained predecessor refuses as changed, and a missing one as
     missing.
   - A leftover candidate entry fails the pins, and `--write-index` retires
     it.
4. **Refusals** (`RefusalTests`, 13 tests).
   - The front-door rule matches exactly the intended names, and a relative
     RAPP/1 path is resolved against the working directory, including by a
     probe run with a relative path.
   - The staged generator refuses a front door in `repository_evidence`,
     `normative`, `reference`, `provenance` and `prototype_catalog`, and a
     predecessor record with a README-named path or an extra key.
   - Only a retained core Workspace/1 manifest can be a predecessor: the
     grail prototype, a non-core status, another profile and another schema
     are refused.
   - The tool refuses unsafe or meaningless staging (nine cases, including a
     staged `provenance.json`, refused for the true reason). It never writes
     through a symlinked directory, a symlinked scratch directory, a
     symlinked index (in check mode and under `--write`), or a symlinked or
     hard-linked candidate under `--write` (the symlinked one also directly
     through its recorded-file writer): the files behind them stay
     byte-identical. A hard-linked index is refused before the candidate is
     touched. It skips untracked symlinks and special files anywhere in the
     tree (virtual environments at the top level, inside `tools/` or inside a
     skill, a convenience link, a FIFO, unreadable files and directories),
     Finder and editor swap, backup and lock files in the staged tree,
     tolerates an untracked checkout, a read-only directory and a leftover
     retained predecessor, and its scratch copy holds no symlink, is
     owner-only and is removed after every run. A copy failure is reported by
     the entry's repository-relative name, never an absolute local path. It
     refuses a candidate or index entry it cannot
     reproduce (tampered candidate, edited staged file, a generator naming no
     predecessor, and authority-claiming, wrong, missing or duplicate
     entries) and a current manifest that is not the named predecessor.

## Mutation table

Each mutation was applied to a disposable scratch copy of this branch. A
mutation of the staged generator was then resealed through
`tools/workspace_successor.py --write`, and the test's successor-hash oracle
was updated to the resealed hash, so only semantic assertions could catch it.
A resealed control with no mutation passed all 17 targeted tests. Symlink
skipping and the write-target pre-check are independent layers: with the
pre-check removed, writes still stay inside the copy (M22); with skipping
removed, the overlay holds the links (M23); with both removed, the staged
generator writes through a symlinked index (M22a, confirmed by hand: the
file behind the link changed).

| ID | Mutation | Targeted test | Result |
|---|---|---|---|
| CTRL | none (resealed; oracle unchanged) | all 17 targeted tests | PASS |
| M1 | staged generator: front-door tripwire removed | `test_staged_generator_refuses_a_front_door_in_every_section` | RED: "Refusal not raised" in every section |
| M2 | staged generator: `README.md` re-listed and tripwire removed | the after-the-switch navigation and README edit tests | RED: a README edit moves the successor identity |
| M2a | staged generator: `README.md` re-listed, tripwire intact | `test_tool_check_passes_and_write_reproduces_every_committed_byte` | RED: the reseal itself is refused (`front-door-not-pinnable`) |
| M2b | staged generator: root `SPEC.md` re-listed | `test_after_the_switch_each_navigation_edit_keeps_the_identity_and_qualification` | RED: a root `SPEC.md` edit moves the successor identity |
| M3 | staged generator: predecessor SHA-256/length check removed | `test_after_the_switch_retained_predecessor_damage_refuses` | RED: tampered history qualifies |
| M4 | staged generator: predecessor `status` check removed | `test_only_a_retained_core_workspace_manifest_can_be_a_predecessor` | RED: a non-core manifest is accepted |
| M4a | staged generator: predecessor `schema` check removed | `test_only_a_retained_core_workspace_manifest_can_be_a_predecessor` | RED: another schema is accepted |
| M4b | staged generator: predecessor `profile` check removed | `test_only_a_retained_core_workspace_manifest_can_be_a_predecessor` | RED: another profile is accepted |
| M5 | staged generator: predecessor record/path rule removed | `test_staged_generator_refuses_a_front_door_in_every_section` | RED: a README-named path and an extra key are not refused by rule |
| M5a | staged generator: predecessor key-set check removed | `test_staged_generator_refuses_a_front_door_in_every_section` | RED: a record with an extra key is accepted |
| M5b | staged generator: missing-predecessor refusal removed | `test_after_the_switch_retained_predecessor_damage_refuses` | RED: a missing predecessor is reported as an unsafe path |
| M6 | staged generator: `--write-index` keeps the candidate entry | `test_switch_makes_exactly_the_candidate_current_and_retires_its_index_entry` | RED: the switch leaves the pins failing |
| M7 | staged generator: `check_index()` tolerates a leftover candidate | `test_after_the_switch_a_leftover_candidate_entry_fails_the_pins` | RED: pins pass with a dangling candidate |
| M8 | staged generator: the current index writer (append, reset `generated_utc`) | `test_switch_makes_exactly_the_candidate_current_and_retires_its_index_entry` | RED: entry order regresses |
| M9 | staged generator: tripwire limited to `repository_evidence` | `test_staged_generator_refuses_a_front_door_in_every_section` | RED: front doors in `normative`, `reference`, `provenance` and `prototype_catalog` pass |
| M10 | tool: staged front-door refusal removed | `test_tool_refuses_unsafe_or_meaningless_staging` | RED: a staged README is not refused as a front door |
| M11 | tool: staged-file-is-pinned check removed | `test_tool_refuses_unsafe_or_meaningless_staging` | RED: a staged unpinned file passes |
| M12 | tool: succession check removed | `test_tool_refuses_a_candidate_it_cannot_reproduce` | RED: a generator naming no predecessor is not refused as such |
| M13 | tool: recorded-candidate comparison removed | `test_tool_refuses_a_candidate_it_cannot_reproduce` | RED: a tampered candidate is not refused |
| M14 | tool: index-entry comparison removed | `test_tool_refuses_a_candidate_it_cannot_reproduce` | RED: authority-claiming, wrong, missing and duplicate entries pass |
| M15 | tool: `--write` appends instead of replacing the entry | `test_tool_check_passes_and_write_reproduces_every_committed_byte` | RED: a second `--write` duplicates the entry |
| M16 | tool: the overlay skips installing the staged files | `test_tool_check_passes_and_write_reproduces_every_committed_byte` | RED: the check fails |
| M17 | tool: the overlay does not retain the current manifest as history | `test_tool_check_passes_and_write_reproduces_every_committed_byte` | RED: the staged generator refuses |
| M18 | tool: the `successor/` staging guard removed | `test_tool_refuses_unsafe_or_meaningless_staging` | RED: staging the candidate itself is not refused as unswitchable |
| M19 | tool: directory-component symlink checks removed | the symlinked-directory and symlinked-scratch-directory tests | RED: the staged-path refusal loses its path, and the overlay is built behind a symlinked `.validation` |
| M20 | tool: `--write` accepts a symlinked recorded file | `test_tool_never_replaces_a_linked_recorded_file` | RED: a symlinked candidate is silently replaced by a regular file |
| M21 | tool: `--write` accepts a hard-linked recorded file | `test_tool_never_replaces_a_linked_recorded_file` | RED: a hard-linked candidate is silently replaced |
| M22 | tool: write-target pre-check removed (symlinks still skipped) | `test_tool_refuses_a_symlinked_index_in_both_modes` | RED: the refusal loses its reason (the index is merely missing from the copy; nothing is written outside it) |
| M22a | tool: symlink skipping and write-target pre-check both removed | `test_tool_refuses_a_symlinked_index_in_both_modes` | RED: the symlinked index is copied as a link and the staged generator writes through it |
| M23 | tool: symlinks copied into the overlay (write-target pre-check intact) | `test_tool_ignores_untracked_local_entries_and_finder_files` | RED: the overlay holds the untracked links |
| M24 | tool: ignored names not skipped in the staged tree | `test_tool_ignores_untracked_local_entries_and_finder_files` | RED: a Finder `.DS_Store` fails the tool |
| M25 | tool: `--write` does not keep the recorded file's mode | `test_tool_check_passes_and_write_reproduces_every_committed_byte` | RED: the recorded files become owner-only |
| M26 | tool: `--write` resets the recorded file's mode to `0o644` | `test_tool_check_passes_and_write_reproduces_every_committed_byte` | RED: non-default modes are lost |
| M27 | tool: `--write` checks each recorded file only when replacing it | `test_tool_never_replaces_a_linked_recorded_file` | RED: the candidate is replaced before a hard-linked index is refused |
| M28 | tool: `provenance` and `prototype_catalog` missing from the pinned map | `test_tool_refuses_unsafe_or_meaningless_staging` | RED: a staged `provenance.json` is refused as unpinned |
| M29 | tool: scratch copy created with the default mode | `test_tool_ignores_untracked_local_entries_and_finder_files` | RED: the scratch copy is not owner-only |
| M30 | tool: scratch copy left behind after the run | `test_tool_check_passes_and_write_reproduces_every_committed_byte` | RED: a new copy of the working tree remains under `.validation/` |
| M31 | tests: a relative RAPP/1 path used as given by the helper | `test_relative_rapp1_paths_resolve_against_the_working_directory` | RED: the path is not resolved |
| M32 | tool: special files not skipped when copying | `test_tool_ignores_untracked_local_entries_and_finder_files` | RED: an untracked FIFO fails the copy |
| M33 | tool: editor swap, backup and lock files not skipped in the staged tree | `test_tool_ignores_untracked_local_entries_and_finder_files` | RED: an editor artifact fails the tool |
| M34 | tool: scratch removal does not make read-only directories writable | `test_tool_ignores_untracked_local_entries_and_finder_files` | RED: a read-only copied directory makes the run fail |
| M35 | tool: copy failure reported without the entry's name | `test_a_copy_failure_names_the_entry_without_local_paths` | RED: the refusal does not name `LICENSE` |
| M36 | tests: the fixture uses `RAPP1_PATH` as given | `test_relative_rapp1_paths_resolve_against_the_working_directory` | RED: a probe run with a relative path refuses |
| M37 | tool: unreadable files not skipped when copying | `test_tool_ignores_untracked_local_entries_and_finder_files` | RED: an unreadable untracked file fails the copy |
| M38 | tool: unreadable directories not skipped when copying | `test_tool_ignores_untracked_local_entries_and_finder_files` | RED: an unreadable untracked directory fails the copy |

## Reference implementation and gating

- **Nothing takes effect until the owner acts.** Merging step 1 changes no
  runtime behavior, identity or consumer pin. Only the owner's switch makes
  the successor current.
- **No semantics change silently.** Step 1 changes no pinned byte: the
  Workspace/1 SPEC, safety matrix, schemas, reference code and instruction
  files are byte-identical. At the switch, the pinned files that change are
  exactly `reference/pins.py` and the three `SKILL.md` files (plus the
  manifest itself, which becomes the successor); the Workspace/1 SPEC, safety
  matrix and schemas stay byte-identical.
- **Defaults stay fail-closed.** The candidate cannot qualify, the tool fails
  closed on any mismatch, and after the switch old runtime pins refuse new
  execution and older sidecars are verified but never auto-updated.
- **Checks.** Every step of `.github/workflows/ci.yml` passes locally under
  Python 3.12, with the `dda32d7` RAPP/1 checkout inside the repository at
  `rapp-1/` as the workflow places it, and `TMPDIR` inside `.validation/`.
  GitHub CI runs the same steps on every push; the pull request cites the
  run for its final commit.

## Open questions for the owner

1. **Should the front-door rule go further?** The tripwire covers
   README-named files; the allowlist already leaves every other unlisted file
   unpinned (for example `LICENSE`, `docs/` and the root `SPEC.md`).
   Recommendation: rely on the allowlist.
2. **Root `SPEC.md`.** The candidate leaves it unpinned because it declares
   itself navigation. If you want it pinned anyway, the candidate changes by
   one allowlist entry and a reseal. Recommendation: leave it unpinned.
3. **SDK re-pin shape.** The switch needs a new SDK generation because
   generations are keyed by parent commit. An alternative is for SDK
   conformance to accept a retained predecessor of the current manifest, but
   that changes SDK semantics. SDK SPEC §8 is read relative to each
   generation's recorded sibling pin (Step 2c); if you prefer to reword §8
   instead, that SDK SPEC edit moves the SDK spec hash, its index entry and
   its file manifest in the same switch. Recommendation: the new generation,
   with §8 read as stated.
4. **Archived README hashes** in prototype catalogs, prototype manifests and
   `provenance.json` are historical evidence that no gate re-verifies.
   Recommendation: leave them.

## Owner actions needed

1. **Merge this pull request.** It records the candidate and its index
   entry; it accepts nothing and moves no identity or pin.
2. **Accept or reject the candidate**
   `rapp-workspace-file-manifest/2`
   `e99a51d355bd66c71017f4451cdd54bc47ed2b99c4fe0d939e1c494288148814`.
   Acceptance happens only by merging the switch pull request (Step 2),
   which the spec-gaps workstream prepares on request. Afterwards the README
   network header can land (Step 3).
3. **Decide the open questions** (a recommendation is given with each).

## References

- RAPP Work organism gap register, `organism/gaps/G24.md`
  (`kody-w/rapp-work`, branch `experimental/rapp-work-constitution`).
- RAPP/1 Protocol Constitution (`kody-w/rapp-1` `CONSTITUTION.md`),
  Articles 2, 3, 4, 8, 9, 10 and 18.
- Workspace/1 SPEC §§1–4.1, 11 and 14; RAPP Work SDK/1 SPEC §§1, 2, 4 and 8.
- `kody-w/rapp-1` commits `591e014ad39e223b00ab343ae26e5d9a867ebeee` and
  `bae4e3cacc33e82e7fcf9fe73d2fd043da97801d`, both with
  `protocols/rapp-work/1/SPEC.md`
  `283359355c3fe2858e28744368255683af3ed28a68e290e56c231e7d4b13c08e`
  (11,427 bytes).
- RAPP/1 inspection checkout `dda32d741c7218f41443a5bd17eebfe0eae82cb7`, used
  by CI and recorded in `provenance.json`.
