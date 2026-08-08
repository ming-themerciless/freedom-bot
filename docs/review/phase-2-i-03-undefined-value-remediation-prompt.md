# Gemini prompt — remediate real Foundry `undefined_value` rehearsal blocker

Use this prompt from `/opt/discord-bots/freedom-bot`.

---

You are remediating one narrowly bounded Phase 2 I-03 defect discovered by the
maintainer-supervised Foundry rehearsal on 2026-08-06. Work in the existing
dirty working tree. Preserve every pre-existing change. Do not reset, checkout,
clean, reformat unrelated files, commit or push.

Read completely before editing:

- `.agents/AGENTS.md`;
- `docs/implementation-plan.md`;
- `docs/rules/foundry-export-contract.md`;
- `docs/operations/foundry-snapshot-submission.md`;
- `docs/operations/phase-2-maintainer-closeout.md`;
- `docs/review/phase-2-supervised-rehearsal-2026-08-06.md`;
- `foundry-module/README.md`;
- all files and tests under `foundry-module/` relevant to source extraction,
  canonicalisation, bundle construction and workflow.

## Observed failure

The local module version 1.0.0 was installed and enabled on Foundry 14.365 with
dnd5e 5.3.3. The maintainer selected the explicitly non-live Actor folder and
clicked **Download JSON (fallback)** with no credential. Export failed closed
before download with `undefined_value`.

A real embedded dnd5e Item contained an optional schema property whose
JavaScript value was `undefined`. The dnd5e 5.3.3 installed source declares
several advancement fields, including `classRestriction`, with
`initial: undefined`. Foundry `Document#toObject()` passes through
`Document.shimData`, so a supported public serialization call can yield these
undefined-valued object properties even though JSON cannot represent them.

No download or submission occurred. The endpoint was stopped, its synthetic
credential revoked, the artifact root is empty, and all relevant
`freedom_test` counts are zero. Do not use or request any real Actor name,
mechanic, raw export, credential, Item ID or Actor ID to implement the fix.

## Required semantic decision

Do not special-case `classRestriction`, advancement records, a particular Item
type, Actor, folder or stable ID. Do not weaken the canonical encoder's general
rule that receiving `undefined` is an error.

Instead, introduce an explicit, pure projection at the Foundry source boundary
between `Document#toObject()` and bundle construction:

1. Recursively copy supported JSON values without mutating the Foundry object.
2. For a plain object's **own enumerable property** whose value is
   `undefined`, omit that property. This gives an explicit meaning to the
   absence marker dnd5e uses for optional schema fields; it is not silent
   `JSON.stringify` coercion.
3. Do not silently convert an `undefined` array element to `null` or remove it.
   Refuse it with a typed, path-only error because either conversion changes
   array meaning or indexes.
4. Continue to refuse functions, symbols, bigint, non-finite numbers, negative
   zero, cycles, non-plain class instances and every other value the canonical
   contract currently rejects.
5. Preserve NFC normalisation, key ordering, stable array ordering, size/depth
   bounds and exact-byte checksum behavior.
6. The canonical encoder must remain a second fail-closed boundary. Its current
   direct test proving `{a: undefined}` is refused must continue to pass.
7. Errors and tests must use synthetic paths and values. Do not log or report
   real content or real stable document IDs.

Name and document the projection so a future maintainer can distinguish:

- `undefined` as an absent optional **object property** at the Foundry API
  boundary; from
- `undefined` anywhere after that boundary, which remains an exporter defect
  and refusal.

If code inspection proves that this semantic decision conflicts with a
load-bearing accepted contract, stop without editing and report the exact
conflict. Do not invent a different policy.

## Required implementation and tests

Implement the smallest cohesive change. At minimum add regression tests proving:

- a synthetic nested object matching the structural category of an embedded
  Item advancement may contain optional undefined-valued properties and those
  properties are explicitly absent from the projected result;
- siblings with `null`, `false`, `0` and `""` are retained exactly;
- nested objects and objects inside arrays are handled;
- an undefined array element refuses with a stable typed code and path but no
  value;
- input objects are not mutated;
- cycles and unsupported types still refuse;
- canonicalisation still independently refuses an undefined value;
- two projections/exports of unchanged synthetic input produce identical
  bytes and checksum;
- the download and submit workflows consume the same projected bytes;
- the Node-to-Python golden contract still parses through the Manager's real
  parser;
- no Foundry mutation API or credential persistence is introduced.

Do not make a fixture pass by using `JSON.parse(JSON.stringify(value))`: that
silently converts undefined array elements to `null`, loses typed refusal
information, and obscures the policy being reviewed.

Inspect the installed Foundry 14.365 and dnd5e 5.3.3 application source only as
read-only product code evidence. Do not inspect world databases, world JSON,
Actor documents, browser storage, logs containing player data, or any prior
real export.

## Version and documentation

This changes exporter behavior after an observed real-world refusal. Bump the
module patch version from `1.0.0` to `1.0.1` and update version-coupled tests and
examples deliberately. Do not change schema version 1 unless the existing
Manager contract actually requires it; explain why omission of a JavaScript
non-value does or does not alter the on-wire schema.

Update the export contract and module documentation to state the boundary rule
precisely. Update the supervised rehearsal record only with a sanitized note
that remediation was implemented and awaits independent review/reinstallation;
do not change its failed result to passed. Do not claim the rehearsal was
rerun.

## Verification

Run and report exact commands and totals for:

1. all Foundry module Node tests;
2. syntax checks for every shipped module script and relevant test module;
3. the Python exporter golden-contract test;
4. the complete snapshot/database/reconciliation group used by the I-03
   package;
5. the full Python suite;
6. `python -m compileall` over project Python sources;
7. `alembic check` against the documented disposable database configuration;
8. `git diff --check`;
9. a targeted diff and `git status --short` demonstrating that unrelated dirty
   changes were preserved.

Never point a test at production or staging. Database verification may use only
`freedom_test` and must restore its exact empty baseline. Do not start Caddy,
the rehearsal endpoint or Foundry, and do not install/reinstall the module in
this task.

## Required handoff

Report:

- root cause in plain language;
- exact semantic rule implemented;
- files changed;
- module version;
- exact verification commands and totals;
- database/artifact cleanup result;
- confirmation that no real world data or credential was accessed;
- any blocker or residual risk;
- the exact source path that should later be atomically reinstalled on Foundry
  1, but do not perform installation;
- one next action: independent Codex implementation/security re-review.

Do not claim the inactive-folder rehearsal passed, the active-folder gate
passed, I-03 is closed or Phase 2 is complete.

---
