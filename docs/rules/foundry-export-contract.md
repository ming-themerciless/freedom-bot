# Freedom Blades offline Foundry export bundle — contract v1

Status: **Phase 2 contract.** Required by implementation plan §6.4 and by the
maintainer ruling that the Manager never reads live Foundry and never reads
Foundry LevelDB. Supersedes the part of
[ADR 0006](../adr/0006-foundry-integration-boundary.md) that rejected offline
snapshot import; see that ADR's *Amendment 2026-08-02*.

This document defines the artifact a Guild Council member deliberately produces
inside Foundry and hands to the Manager. It is the **only** Foundry input Phase 2
accepts.

## 0. What produces it

A Council member runs an explicit action in the Foundry client — a macro or a
small Freedom Blades module — using **supported Foundry document APIs**
(`game.actors`, `game.folders`, `Document#toObject()`). It is a deliberate
export, not a background job, and not a read of `worlds/<id>/data/`.

Reading LevelDB is forbidden for this artifact exactly as it is for the Phase 7
connector. The world stores are held open by a running server, and the storage
format is a Foundry internal.

The exporter is **not distributed**. It serves one deployment, so it owes no
third-party backwards compatibility. Under OD-14 as superseded by controlled
baseline v1.6, the Manager requires exact world/system identities, numeric
Foundry `14.x`, numeric dnd5e `5.3.x`, and fails closed outside those ranges.

### 0.1 The implementation, and how it reaches the Manager

The exporter is [`foundry-module/`](../../foundry-module/README.md), a Foundry
v14 module. Its canonical encoder and bundle builder are pure and are tested
without a running Foundry instance; `tests/test_exporter_contract.py` feeds
their real output to the Manager's real parser, so the two implementations of
this contract cannot drift apart unnoticed.

**Transport is not part of this contract, and this contract does not change
because of it.** The bundle below is identical whether it is carried as a file
or POSTed. Two routes exist:

| Route | Status | Where |
|---|---|---|
| direct HTTPS submission from the module | **the supported workflow** | [operations](../operations/foundry-snapshot-submission.md) |
| browser download, then an operator command | fallback and diagnosis | [import operations](../operations/foundry-snapshot-import.md) |

A submitted artifact is validated by the server against every rule below,
independently of anything the client claimed, and becomes a **pending** record.
Submission applies nothing; §4 is unchanged.

## 1. Encoding and canonicalisation

Comparison and content-addressing require that the same world state produces the
same bytes, so the encoding is part of the contract rather than a convention:

| Rule | Value |
|---|---|
| Container | one JSON document |
| Encoding | UTF-8, no byte-order mark |
| Line ending | `\n` |
| Object keys | ECMAScript own-property order at every depth: **array-index** keys — canonical decimals in `[0, 2**32 - 2]` — first, ascending numerically; then all other keys sorted by Unicode code point. See §1.0 |
| Separators | `,` and `:` with no surrounding whitespace |
| Array order | `folders` and `actors` sorted ascending by `id`; every other array keeps the order Foundry reports |
| Numbers | IEEE-754 doubles, written as ECMAScript's `Number::toString` writes them; no `NaN`, no `Infinity`, no `-0`. See §1.3 |
| Unicode | every string normalised to NFC before encoding, keys included; two keys of one object that share an NFC form are a **refusal**, never a merge. See §1.2 |
| Trailing newline | exactly one, at end of file |

The Manager **preserves the original bytes** and identifies the artifact by the
SHA-256 of those bytes, computed before parsing. It never re-serialises an
artifact and calls the result the same snapshot. Canonicalisation is the
exporter's obligation: it makes two exports of an unchanged world compare equal,
and it is not something the Manager may apply retroactively.

### 1.0 Why key order is ECMAScript's and not plain code-point order

Changed 2026-08-09 after finding
[RA-2](../review/phase-2-rehearsal-a-findings-2026-08-09.md). Until then this
row read "sorted by Unicode code point, at every depth", and **no conforming
exporter could satisfy it.**

dnd5e keys scale-value advancements by class level, so a real Actor carries
objects like `{"1": …, "4": …, "10": …}`. ECMAScript defines own-property order
as integer-index keys first in ascending numeric order, then string keys; a
browser exporter therefore emits `"1","4","10"` no matter how it sorts, because
`Object.keys` has already reordered them. Code-point order wants `"1","10","4"`.
The consequence was that `canonical_encoding` was reported false for every real
world and true only for synthetic fixtures, which have no integer-like keys —
so the flag was structurally unable to mean anything.

The rule now matches what the only supported exporter can produce:

- a key is an **array index** if it is a canonical decimal integer in
  `[0, 2**32 - 2]` — so `"01"`, `"-1"`, `"1.0"` and `" 1"` are ordinary string
  keys, exactly as JavaScript treats them, and so is every canonical decimal
  from `"4294967295"` upwards;
- array indices come first, ascending numerically;
- every other key follows, sorted by Unicode code point.

The second half is this contract's, not the language's: ECMAScript would use
insertion order there, which is not a property a canonical form may depend on.

#### The upper bound is `2**32 - 2`, and it was wrong here until 2026-08-10

Corrected as change-log **C-12**, on the independent review's finding I-1. The
first version of this section said `[0, 2**53 - 1]` and called such keys
"integer indices". Both were wrong, and not merely as terminology:

`OrdinaryOwnPropertyKeys` — the operation behind `Object.keys` and every
enumeration of an ordinary object — gives numeric precedence to **array
indices**, which ECMAScript defines as the property keys `P` where
`ToString(ToUint32(P))` is `P` and `ToUint32(P)` is not `2**32 - 1`. That range
ends at `4294967294`. An *integer index* — the `[0, 2**53 - 1]` concept — is a
`String.prototype` and typed-array notion that ordinary object enumeration never
consults.

The difference is observable, and it disagreed across the two implementations.
From the repository root:

```bash
node --input-type=module -e "import {canonicalBytes} from './foundry-module/scripts/canonical.js'; process.stdout.write(new TextDecoder().decode(canonicalBytes({'5000000000':'five','10000000000':'ten'})))"

./venv/bin/python -c "from application.foundry.parser import canonical_bytes; print(canonical_bytes({'5000000000':'five','10000000000':'ten'}).decode(), end='')"
```

Under the `2**53 - 1` rule the exporter emitted
`{"10000000000":"ten","5000000000":"five"}` — both keys are ordinary string keys
to it, so they sorted by code point — while the Python verifier sorted them
numerically and produced the other order. Every real artifact containing a
canonical decimal key of ten digits or more would have been reported
non-canonical against an exporter that was in fact conforming.

**Only the verifier and this document changed.** The exporter always implemented
the corrected rule, because it never implemented the wrong one: `canonical.js`
sorts the key array by code point and then rebuilds an object, and the engine
hoists exactly the array indices on insertion. The rule stated here is what that
produces. Module `1.0.5` is therefore unchanged, byte for byte, and remains the
installed, rehearsed build of record.

`canonical.js`'s own header comment said "keys sorted by code point at every
depth", which describes the sort it performs rather than the order it emits. It
was **deliberately not edited** at the time: correcting a comment would have
changed the bytes of an installed and rehearsed build, and the version/build
identity control forbids doing that silently under the same version. It was
carried against the next version bump and **corrected in `1.0.6`** (§1.2), which
is that bump.

Cross-language agreement over the whole boundary — `"0"`, `"4294967294"`,
`"4294967295"`, numeric-looking strings whose numeric and code-point orders
differ, the noncanonical forms, and recursion through nested objects and arrays
— is now asserted by `tests/test_exporter_contract.py`, which feeds the real
module output through the real verifier, and mirrored in
`foundry-module/tests/canonical.test.mjs`.

What did **not** change: the Manager still preserves the original bytes and
identifies an artifact by their SHA-256. Duplicate detection never depended on
canonicalisation, because an exporter's output is deterministic — re-exporting
an unchanged world yields identical bytes whatever the key order. What
canonicalisation buys is comparability *between* exporters, which is why a
non-canonical artifact is a warning naming the exporter and version, and never a
refusal.

### 1.1 Boundary projection of undefined

Foundry `Document#toObject()` passes through schema defaults such as dnd5e's
`initial: undefined` for optional properties. To map these cleanly into JSON:

- At the Foundry source boundary (`world-source.js`), a plain object's own
  enumerable property whose value is `undefined` is **skipped while constructing a new projected result**; the source object and its property are unchanged.
- An `undefined` element inside an **array** is **refused** (`undefined_array_element`).
- Any `undefined` value reaching the canonical encoder (`canonical.js`) remains an
  exporter defect and is **refused** (`undefined_value`).

Nesting depth may not exceed **64**. An artifact may not exceed **64 MiB** — a
real Actor is 1.1–3.3 MB of JSON ([foundry-mapping.md](../discovery/foundry-mapping.md)
F-F5), so this bounds a plausible active folder with headroom while keeping the
refusal well below anything that could exhaust memory.

### 1.2 Two keys that share one NFC form are a refusal

Added 2026-08-10 as change-log **C-16**, on a defect recorded in
[`../review/phase-2-canonical-nfc-key-collision.md`](../review/phase-2-canonical-nfc-key-collision.md).
Exporter **`1.0.6`**; `1.0.5` and earlier do not implement this section.

NFC normalisation applies to keys, so `é` written as U+00E9 and as
U+0065 U+0301 are two properties of a Foundry document and one key of the
canonical form. The canonical form cannot hold both, and **the resolution is a
refusal, not a choice**:

- the exporter refuses the export (`nfc_key_collision`), naming the path and
  never a value, before any bytes exist to hash or send;
- the Manager refuses the artifact with the same code. This is the one place
  canonicalisation is *enforced* rather than reported: a non-canonical artifact
  is a warning because a conforming exporter's bytes are simply ordered
  differently, whereas a colliding document has **no** canonical form and cannot
  have come from a conforming exporter at all.

Merging is not available: the two keys are different properties, and nothing in
this repository says which one an operator meant. Dropping one is what the
defect did — until `1.0.6` the exporter inserted both under the shared form, so
the second write silently discarded the first value, and the Manager emitted the
same key twice. Both are exactly the "a value quietly disappears from an Actor
export" outcome §1 exists to prevent.

A **single** non-NFC key is not a collision: it has one NFC form, is normalised
like any other string, and the artifact is accepted. Because the emitted bytes
then differ from a document written in the decomposed form, an artifact that
carries one and was not produced by this exporter is reported non-canonical,
which is a warning as always.

The operator remedy is to rename one of the two properties in Foundry and export
again.

### 1.3 How a number is written, and the two that cannot be

Added 2026-08-10 as change-log **C-17**, on a blocking finding of the
independent Phase 2 gate review. Until then this row read "JSON numbers", which
is not a serialisation rule at all: `1e20` is `1e+20`, `100000000000000000000`
and `1.0E20` in JSON, and a canonical form must name one of them.

The number is the **double**, and it is written as ECMAScript's
`Number::toString` writes it — which is what `JSON.stringify` emits, so the
exporter obeys this rule by construction. In full, for a value that is not zero
(zero, including `-0`, is `0`), with `s` the shortest digit string that reads
back as the value, `k` its length, and the value equal to `0.s × 10**n`:

| Condition | Written as |
|---|---|
| `k ≤ n ≤ 21` | `s` followed by `n − k` zeros — `100000000000000000000` |
| `0 < n ≤ 21` | `s` with a point after `n` digits — `123.456` |
| `−6 < n ≤ 0` | `0.` then `−n` zeros then `s` — `0.000001` |
| otherwise | `s` in exponent form, `e+`/`e-`, exponent **not** zero-padded — `1e-7`, `1.7976931348623157e+308` |

The thresholds are the whole point. Python's `json.dumps` switches to exponent
notation at `1e16` and below `1e-4`, and pads the exponent to two digits, so the
verifier wrote `1e+20` and `1e-07` where the exporter writes
`100000000000000000000` and `1e-7`. Both implementations were self-consistent
and disagreed, exactly as at the array-index boundary (§1.0) and the NFC
boundary (§1.2), and the consequence was the same: `canonical_encoding` reported
false for a conforming export. From the repository root:

```bash
node --input-type=module -e "import {canonicalBytes} from './foundry-module/scripts/canonical.js'; process.stdout.write(new TextDecoder().decode(canonicalBytes({'a':1e20,'b':1e-7})))"

./venv/bin/python -c "from application.foundry.parser import canonical_bytes; print(canonical_bytes({'a':1e20,'b':1e-7}).decode(), end='')"
```

**Only the verifier changed.** `canonical.js` has always delegated numbers to
`JSON.stringify`, which is `Number::toString` exactly. The module bytes change
only because §1.3's refusal code is added to the client's bounded
`SERVER_ARTIFACT_CODES` list, which is a version bump to **`1.0.7`** and no
change to what the exporter emits.

Because the contract's numbers are doubles, an integer literal is read as the
double a browser would have read it as. `9007199254740993` is not a double, so
an artifact containing it is reported non-canonical against
`9007199254740992` — which is honest, since no exporter could have written the
first.

Two values have **no** canonical form, and are the numeric counterpart of §1.2:

- **A literal outside the double range** — `1e999`, or an integer of 400
  digits — reads as an infinity in both languages. JSON cannot express one, and
  `null`, a clamp to the largest double and the digits written back again are
  three different values, none of them the one the artifact held. The exporter
  refuses (`non_finite_number`) and **the Manager refuses with the same code.**
- **`-0`** is refused by the *exporter* (`negative_zero`) and **encoded by the
  Manager as `0`.** This is the one deliberate asymmetry in this contract.
  Producing a `-0` and reading one are different acts: the exporter reads live
  Foundry objects, where `-0` is a value its own output would not read back as,
  so emitting it would produce a document that no longer matches its source. The
  Manager reads a document that has already been through JSON, where the sign is
  gone; `-0` has the canonical form `0`, the artifact's bytes differ from it, and
  that is the ordinary non-canonical warning.

Cross-language agreement over the thresholds, the precision boundaries, the
subnormals, both ends of the double range, integer literals past `2**53`, and
recursion through nested objects and arrays is asserted by
`tests/test_exporter_contract.py`, which feeds the real module output through the
real verifier, and mirrored in `foundry-module/tests/canonical.test.mjs`.

## 2. Top-level shape

Exactly these keys, all required. **Any unknown top-level key is a refusal**, not
a warning: an artifact carrying something the Manager does not understand has not
been validated by anyone.

```json
{
  "schema": "freedom-blades.foundry-export",
  "schemaVersion": 1,
  "exporter": { "id": "freedom-blades-export", "version": "1.0.2" },
  "exportedAt": "2026-08-02T09:15:00Z",
  "world": {
    "id": "the-guild",
    "title": "The Guild",
    "coreVersion": "14.365",
    "systemId": "dnd5e",
    "systemVersion": "5.3.3"
  },
  "selectedFolderIds": ["actvQwErTyUiOpAs"],
  "folders": [
    { "id": "actvQwErTyUiOpAs", "name": "Characters (active)", "parentId": null }
  ],
  "actors": [
    {
      "id": "5tYuIoPaSdFgHj6K",
      "folderId": "actvQwErTyUiOpAs",
      "name": "Synthetic Testcharacter",
      "system": { "…": "…" },
      "items": [ { "…": "…" } ]
    }
  ]
}
```

### 2.1 `schema` and `schemaVersion`

`schema` is the fixed string `freedom-blades.foundry-export`. `schemaVersion` is
an integer. The Manager accepts **exactly** the versions it was built for and
fails closed on anything else, naming both the observed and the expected value.
A newer exporter is a deliberate, visible checkpoint, not a degraded import.

### 2.2 `exporter`

`id` and `version` identify the macro/module that produced the artifact. The
version is recorded on every preview, import, comparison and snapshot-based
correction, alongside the field-profile version.

### 2.3 `exportedAt`

RFC 3339 UTC instant with a `Z` offset. It is provenance, not identity: two
exports of an unchanged world differ in this field and are therefore two
snapshots. That is intended — the checksum is the identity, and it changes.

### 2.4 `world`

The world **is** the identity; the instance is a transport endpoint (ADR 0006,
unchanged). There is deliberately no instance, host, port or URL in the bundle:
`/home/foundry/shared/worlds` is bind-mounted into all three Foundry instances,
so composing an instance into the identity would split one world into three.

`coreVersion`, `systemId` and `systemVersion` are validated together against the
configured supported deployment. The observed reference today is core `14.367`,
`dnd5e` `5.3.3`, world `the-guild`. World and system identities match exactly;
compatible versions are numeric Foundry `14.x` and dnd5e `5.3.x`; malformed or
out-of-range versions fail closed (OD-14, controlled baseline v1.6).

### 2.5 `folders` and `selectedFolderIds` — a bounded set, not a single folder

**Decision: the bundle carries a bounded set of Actor folders, and the Manager
selects one of them.**

The alternative — one folder chosen inside Foundry at export time — was
rejected because plan §12 Phase 3 requires a Platform Administrator to *select*
the import folder **from the artifact**, with a Council member then confirming
the exact preview. A single-folder bundle would move that selection into the
Foundry macro, where neither the administrator's authorization nor the
confirmation the plan requires can be enforced or audited.

The set is bounded so that "select from the artifact" cannot become "export the
whole world":

| Bound | Limit |
|---|---|
| `selectedFolderIds` entries | 1–8 |
| `folders` entries | ≤ 64 |
| `actors` entries | ≤ 500 |

`selectedFolderIds` lists the folders the Council member deliberately exported.
Every Actor's `folderId` **must** be one of them. `folders` must additionally
contain every ancestor of every selected folder, so the Manager can present a
full path such as `/actors/Characters (active)` without asking Foundry anything.

Folder identity is the **stable Foundry folder ID together with its displayed
path**, never the name alone. Two folders may legitimately share a name under
different parents; a name is a display value in exactly the way an Actor name is.

Refused: a duplicate folder `id`; a `parentId` naming a folder not present; a
parent cycle; a `selectedFolderIds` entry not present in `folders`; an empty
`selectedFolderIds`.

The initial selected folder is `Characters (active)`, folder ID
`actvQwErTyUiOpAs` in the live world, with no sub-folders
([foundry-mapping.md §7](../discovery/foundry-mapping.md#7-what-a-maintainer-had-to-supply--all-five-answered-2026-07-30)).

### 2.6 `actors`

Every entry carries:

| Key | Meaning |
|---|---|
| `id` | the Actor's **real** Foundry `_id`: 16 alphanumeric characters |
| `folderId` | the containing folder, which must be in `selectedFolderIds` |
| `name` | display name — provenance and reconciliation evidence, never identity |
| `system` | the `dnd5e` system document, as exported |
| `items` | the Actor's embedded items, as exported |

**`id` is the correction that made this contract possible.** An ordinary Foundry
*Actor export* writes `"_id": null` and leaves the real ID only in the filename
([foundry-mapping.md](../discovery/foundry-mapping.md) F-F1), which is why
ADR 0006 concluded mappings could not come from an export. A bundle built through
`Document#toObject()` over `game.actors` carries the real `_id`, so that
conclusion no longer holds for *this* artifact. It still holds for a hand-saved
per-Actor export, and such a file is refused: a missing or malformed `id` is a
blocking issue, never a name-matched guess.

Refused: a duplicate `id`; a missing, null or malformed `id`; a `folderId` not in
`selectedFolderIds`; an Actor appearing in more than one folder.

## 3. What the bundle must not contain

The exporter includes **only** the collections above. It must not carry:

- credentials, API keys, or any secret;
- Foundry `User` documents, user IDs, or `ownership` grants;
- chat messages, journals, scenes, playlists, macros, tables, combats, cards,
  effects, fog or settings;
- any world collection other than `actors` and `folders`;
- file paths outside the world's own asset references;
- embedded binary image data.

An unknown top-level key is refused, so an exporter that adds a collection fails
closed rather than smuggling it in.

## 4. What the Manager does with it

1. Reads the bytes under a size bound.
2. Computes SHA-256 **before parsing**. That checksum is the snapshot identity.
3. Refuses archive, executable and path-bearing input, and any nesting beyond
   the depth bound.
4. Parses and validates: schema, exporter version, world identity, the
   (core, system) version tuple, the folder graph, and Actor identity.
5. Binds every preview, import, mapping, reconciliation, correction and audit
   record to that checksum.
6. Never writes to Foundry, in this phase or any other before Phase 7's gate.

Changing one byte produces a different snapshot with a different identity. An
imported artifact and its audit record are never edited or overwritten.

## 5. Fixtures

Automated tests use small **synthetic** bundles built by
`tests/foundry_fixtures.py` on the Python side and
`foundry-module/tests/fixtures.mjs` on the JavaScript side, both shaped like this
contract and both holding invented Actors. Real Council snapshots are operational
inputs and are never committed — `.gitignore` already excludes
`fvtt-Actor-*.json`, and this contract adds no route by which a real bundle could
enter the repository.

There is deliberately **no committed golden artifact**. A checked-in expected
bundle is a third implementation of this contract: correct on the day it is
written and silently stale afterwards, because nothing regenerates it.
`tests/test_exporter_contract.py` executes the exporter's real serialization
path instead and hands the result to the real parser.

## 6. Selection: what a single exporter run carries

§2.5 permits 1–8 selected folders, and the Manager supports that range. The
shipped module exports **exactly one** folder per run, and the Actors it
includes are the **direct children** of that folder.

Direct membership is not a simplification, it is the only reading §2.6 admits:
every Actor's `folderId` must be in `selectedFolderIds`, so an Actor sitting in a
sub-folder of the selection would carry a `folderId` that is not selected, and
the Manager refuses exactly that with `actor_outside_selection`. Rather than let
an operator discover this from a count that looks low, the module shows the
selected folder's sub-folder count before confirmation and states that their
Actors are not included.
