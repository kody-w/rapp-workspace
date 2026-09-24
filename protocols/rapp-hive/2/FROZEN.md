# rapp-hive/2: frozen research record

**Status:** frozen on 2026-09-23. Never activate. Apart from this note and the status line of `SPEC.md`, every file in this folder is kept byte for byte, so that its specification, reference and vectors, and the lessons they hold, stay checkable.

## Why it was frozen

- **It worked, and it was too much to run.** Deriving membership, rules and meaning from signed streams took several governance kinds, dozens of refusal codes, a large reference implementation with a byte-exact browser port, and a large vector suite. Each review round found real defects, and every fix added another rule.
- **Real data did not fit.**
  - The one real repository-seeded Hive matched neither `rapp-hive/1` nor this draft.
  - Replaying its history left no members and stranded its pending requests.
  - The last commit here records the four generic gaps that dry run found.

## What replaced it (experimental)

- **The Hive folder convention.** A Hive is a folder of markdown files with git underneath. Every change is an SSH-signed commit, judged by the Hive as it stood just before the change. One Brainstem agent proposes, confirms, applies and undoes changes.
  - Model and reference agent: [`kody-w/rapp-model-hive`](https://github.com/kody-w/rapp-model-hive), branch `experimental/hive-md`.
- **The lessons.** They are written up in the draft RAPP Work Constitution: [`kody-w/rapp-work`](https://github.com/kody-w/rapp-work), branch `experimental/rapp-work-constitution`.

## What stays true

- `rapp-hive/1` is unchanged and remains the normative Private Hive profile.
- Nothing here migrates anything automatically.
- Old records stay valid under the rules they were signed under.
