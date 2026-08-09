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
third party backwards compatibility, and the Manager pins the exact tuple it
accepts.

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
| Object keys | ECMAScript own-property order at every depth: integer-index keys first, ascending numerically; then all other keys sorted by Unicode code point. See §1.0 |
| Separators | `,` and `:` with no surrounding whitespace |
| Array order | `folders` and `actors` sorted ascending by `id`; every other array keeps the order Foundry reports |
| Numbers | JSON numbers; no `NaN`, no `Infinity`, no `-0` |
| Unicode | text normalised to NFC before encoding |
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

- a key is an **integer index** if it is a canonical decimal integer in
  `[0, 2**53 - 1]` — so `"01"`, `"-1"`, `"1.0"` and `" 1"` are ordinary string
  keys, exactly as JavaScript treats them;
- integer indices come first, ascending numerically;
- every other key follows, sorted by Unicode code point.

The second half is this contract's, not the language's: ECMAScript would use
insertion order there, which is not a property a canonical form may depend on.

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

`coreVersion`, `systemId` and `systemVersion` are validated as a **tuple**
against the configured supported deployment. The configured value today is core
`14.365`, `dnd5e` `5.3.3`, world `the-guild` — held in configuration, not
hard-coded (OD-14).

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
