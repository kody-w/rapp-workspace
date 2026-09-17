# RAPP Work Organization/1 reference

This directory implements the profile-independent candidate gates for
`rapp-work-organization/1`. It does not modify Brainstem, activate an estate,
or supply the still-pending generic CEO `agent.py`.

The reference provides:

- generated closed Draft 2020-12 schemas;
- exact mutation-lineage, learning-trace, search, and evolution validators;
- a deterministic arbitrary-program artifact-bundle compiler;
- verified atomic placement of a complete generated bundle;
- exact private-safe bindings for the first wild handshake;
- manifest/index pin verification; and
- a stdlib-only conformance suite.

The deterministic compiler is one reference construction, not a restriction
on Lens behavior. A dynamic Lens remains operation-universal over framed
application content. The host alone constructs and signs canonical RAPP/1
successor Frames.

The Bill fixture contains hashes, byte counts, source qualification counts,
and proof status only. It intentionally excludes private source bytes, keys,
runtime state, compatibility Frame bytes, and the generated static agent.

Run from the repository root:

```sh
python3 -B tools/work_organization.py schemas
python3 -B tools/work_organization.py pins
python3 -B tools/work_organization.py conformance
```

Passing these checks establishes the checked-in candidate structure and
synthetic profile-independent reference behavior. Live activation remains
blocked until the generic CEO agent, Brainstem runtime, policy, signer, and
revocation bindings are independently supplied and authenticated.
