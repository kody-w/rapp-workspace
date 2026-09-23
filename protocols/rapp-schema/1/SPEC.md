# RAPP Schema/1

## The bare schema of a RAPP/1 frame

**Protocol identifier:** `rapp-schema/1`
**Status:** Experimental frontier draft (canary ring). Frozen once promoted.
**Parent:** [`rapp/1`](https://github.com/kody-w/rapp-1/blob/main/SPEC.md)
**Used by:** [`rapp-hive/2`](../../rapp-hive/2/SPEC.md)

A schema says what shape a message has and nothing about what it says. Lenses
map schemas, not individual messages, so one mapping serves every message of a
schema, and two Hives can compare schemas without sharing any content.

The key words **MUST**, **MUST NOT**, **SHOULD** and **MAY** are used as defined
by RAPP/1 section 2.

## 1. Definition

For a RAPP/1 frame `f` whose `payload` is a JSON object, `schema(f)` is:

```json
{
  "schema": "rapp-schema/1",
  "spec": "<f.spec>",
  "kind": "<f.kind>",
  "tags": { "<k>": "<f.payload[k]>" },
  "payload": "<shape(f.payload)>"
}
```

- `tags` holds exactly the keys `schema`, `profile` and `operation` of the
  payload whose values are strings. They are discriminators, not content.
- `shape(v)` is: for an object, an object with the same keys whose values are
  `shape` of each value; for an array, the distinct `shape`s of its elements,
  ordered by their canonical bytes; for `null`, `true`/`false`, integers and
  strings, the type names `"null"`, `"boolean"`, `"integer"` and `"string"`.
- A schema is exactly as deep as its message, so every valid frame has one.

The schema's identity is its particle, `H("rapp/1:particle", schema(f))`,
computed over RAPP/1 canonical JSON with a byte bound of 8 MiB.

## 2. Rules

1. Implementations **MUST** produce byte-identical schema particles for the
   same frame. The conformance vectors of `rapp-hive/2` include schema cases.
2. Any change to this function **MUST** be a new version with a new version
   string inside the schema object (`rapp-schema/2`, ...). A schema particle can
   therefore never silently change meaning.
3. A schema reveals field names, types and the tag values. Field names and tag
   values **MUST NOT** carry personal data; if they could, the schema is private
   data under `rapp-hive/1` section 2 and is not published.
4. Equal schemas mean equal shape, not equal meaning. Meaning is decided by a
   lens and its laws (`rapp-hive/2` section 6.4), never by a schema match alone.

## 3. Additive schemas

Schema `N` is **additive** over schema `O` when they have equal `schema`,
`spec`, `kind` and `tags`, every payload field of `O` appears in `N` with an
identical shape, and `N` has at least one more field. Shapes are compared as
canonical JSON under the same 8 MiB bound as the particle, so every pair of valid
schemas can be compared. An additive schema can be mapped by `O`'s mapping
unchanged; its extra fields are reported as dropped.
