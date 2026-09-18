# RAPP Work SDK/1 reference

`scaffold.py` is the stdlib-only reference installer and updater for the
additive `.rapp-work/` sidecar.

## Install and verify

The workspace must already contain a regular, non-symlinked `rappid.json` with
a valid RAPPID and a world either in that file or supplied explicitly:

```bash
python3 -B protocols/rapp-work-sdk/1/reference/scaffold.py install \
  --workspace /explicit/workspace

python3 -B protocols/rapp-work-sdk/1/reference/scaffold.py verify \
  --workspace /explicit/workspace
```

The command performs no network access and writes only `.rapp-work/`. It does
not copy native files, install discovered capabilities, or authorize Hive
publication.

Mutable sidecar operations require POSIX directory-descriptor reads with
`O_NOFOLLOW`, pre/post-`fstat`, atomic no-replace rename, and atomic exchange.
Unsupported platforms fail closed instead of using a path-based or overwrite
fallback. If native identity omits its world after installation, verify and
update recover the exact world recorded by the sidecar without changing native
bytes.

An optional discovery JSON document must match
`schemas/discovery.schema.json`. Organization entries point to existing
Workspace/1 composite wave addresses. Hive receipts, plugins, skills, and
static APIs remain inert discovery metadata.

## Explicit update

Updates are two-step and require exact pins plus the exact plan digest:

```bash
python3 -B protocols/rapp-work-sdk/1/reference/scaffold.py plan-update \
  --workspace /explicit/workspace \
  --from-pin <installed-known-pin> \
  --to-pin <newer-known-pin>

python3 -B protocols/rapp-work-sdk/1/reference/scaffold.py update \
  --workspace /explicit/workspace \
  --from-pin <installed-known-pin> \
  --to-pin <newer-known-pin> \
  --plan-digest <exact-plan-sha256>
```

There is no branch, tag, latest-release, or network resolution. Unknown pins,
downgrades, changed plans, partial generations, symlinks, unsafe file types,
and conflicting state refuse.

The checked-in prior-release fixture carries a real older profile and discovery
generation. Conformance verifies those old bytes and source-profile hash,
retains them, activates the target profile bytes, and updates the active
`install.json` profile hash.

## Profile and conformance

```bash
python3 -B protocols/rapp-work-sdk/1/reference/scaffold.py profile
python3 -B protocols/rapp-work-sdk/1/reference/schema_source.py --check
python3 -B protocols/rapp-work-sdk/1/reference/pins.py
python3 -B protocols/rapp-work-sdk/1/reference/conformance.py
```

`parent-pin.json` binds the accepted canonical `kody-w/rapp-1` commit and
`protocols/rapp-work/1/SPEC.md` bytes. The former `kody-w/rapp-work` pins remain
available only as exact migration sources. Any later dependency change must
repeat the reviewed forward-profile process and retain the displaced profile
bytes.

Maintainers reseal an accepted parent and its derived artifacts only through
the checked-in generators:

```bash
python3 -B protocols/rapp-work-sdk/1/reference/schema_source.py
python3 -B protocols/rapp-work-sdk/1/reference/pins.py \
  --write-parent-profile --canonical-spec /explicit/canonical/SPEC.md \
  --write --write-index
python3 -B tools/skill_locks.py --sync-work-sdk-vendor \
  --write rapp-work-sdk
python3 -B tools/skill_locks.py --bind-private-hive \
  --write rapp-private-hive
```
