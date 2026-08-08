# Gemini prompt — second remediation of Foundry boundary projection

Use this prompt from `/opt/discord-bots/freedom-bot`.

---

You are performing a narrowly bounded second remediation of the Phase 2 I-03
Foundry `undefined_value` fix. An independent Codex review found two blocking
defects and two review gaps in module version 1.0.1. Preserve the existing dirty
working tree exactly: do not reset, checkout, clean, reformat unrelated files,
commit or push.

Read completely before editing:

- `.agents/AGENTS.md`;
- `docs/implementation-plan.md`;
- `docs/review/phase-2-i-03-undefined-value-remediation-prompt.md`;
- `docs/review/phase-2-supervised-rehearsal-2026-08-06.md`;
- `docs/rules/foundry-export-contract.md`;
- `foundry-module/README.md`;
- `foundry-module/scripts/world-source.js`;
- `foundry-module/scripts/canonical.js`;
- `foundry-module/scripts/main.js`;
- `foundry-module/scripts/workflow.js`;
- all Foundry module tests, especially `projection.test.mjs`,
  `world-source.test.mjs`, `workflow.test.mjs` and `main.test.mjs` if present;
- the Gemini walkthrough at
  `/home/foundry/.gemini/antigravity-ide/brain/0da55125-bd28-4e88-824f-b33e10805743/walkthrough.md`.

Do not access a Foundry world database, Actor or Item document, browser storage,
credential, downloaded export, prior real snapshot or the failure screenshot.
Use synthetic data only.

## Finding 1 — blocking: error paths disclose dynamic stable IDs

`projectFoundryData` starts with an ordinal Actor path but appends each raw
object key:

```js
const keyPath = `${path}.${key}`;
```

dnd5e uses stable document/advancement IDs as object keys. A synthetic
reproduction currently produces an error like:

```text
$actors[0].system.advancement.AbCdEf1234567890.items[0]
```

The stable ID therefore enters the operator-visible error. This contradicts the
accepted path-confidentiality rule and the 1.0.1 walkthrough.

### Required correction

Design one deterministic path-rendering helper and use it for every object-key
path segment produced by the Foundry boundary projector. It must:

1. Never include a raw dynamic key that could be an Actor ID, Item ID,
   advancement ID, UUID, name, mechanic or user-controlled value.
2. Preserve useful safe structural context where it can be proven static.
3. Represent unsafe/dynamic keys with a deterministic ordinal placeholder such
   as `{key:2}` or an equally non-identifying form. Do not hash the key: a hash
   remains a persistent identifier and is unnecessary.
4. Keep array indexes, because they identify structure rather than content.
5. Produce only a path and fixed repository-authored prose—never the rejected
   value.

Do not solve this with a narrow 16-character-ID regex alone. Arbitrary object
keys may contain names or identifiers of other lengths. A denylist cannot prove
confidentiality. Prefer an explicit allowlist of repository-defined structural
keys, or redact all object keys at this boundary if that is the only defensible
generic rule. Explain the chosen rule and why it cannot leak a dynamic key.

Add regression tests proving:

- an ID-shaped synthetic key is absent from an
  `undefined_array_element` message;
- a synthetic name-like and UUID-like key are also absent;
- the message retains the Actor ordinal and array index;
- unsupported-type and cycle errors use the same safe path policy;
- no test assertion depends on the real rehearsal ID or screenshot.

## Finding 2 — blocking: unbounded projection recursion precedes validation

`projectFoundryData` recursively copies the complete contract payload before
`canonical.js` enforces the accepted maximum nesting depth of 64. A 10,000-level
synthetic object currently fails with an untyped JavaScript `RangeError`, not a
controlled exporter refusal.

### Required correction

Enforce the same accepted maximum depth at the projector boundary before
recursing beyond it:

1. Use the single existing `MAX_DEPTH` definition from `canonical.js`, or move
   the shared constant to a dependency-neutral module if importing it would
   create a cycle. Do not copy a second magic number.
2. Match the canonical encoder's exact depth semantics at levels 64 and 65.
3. Refuse excessive nesting with a stable typed `SourceError` code and a safe
   redacted path.
4. Ensure a very deeply nested synthetic input cannot escape as `RangeError`.
5. Preserve cycle detection and do not turn repeated non-ancestor references
   into false cycle findings.

Add regression tests proving:

- the exact accepted boundary succeeds;
- one level beyond it refuses with the typed depth code;
- a 10,000-level synthetic input produces that typed code, never `RangeError`;
- arrays and objects count depth consistently with canonical validation;
- repeated sibling references remain accepted while ancestor cycles refuse.

## Finding 3 — test overclaim: download/submit equivalence

The test named `download and submit workflows consume identical projected
bytes` calls `prepareSnapshot()` twice. It proves deterministic preparation,
not that both UI branches consume the same prepared bytes.

### Required correction

Choose one of these evidence-backed outcomes:

- Preferred: extract the smallest pure/testable dispatch helper from
  `main.js` so a test proves the download branch passes `prepared.bytes` to
  `saveDataToFile` and the submit branch passes those exact same bytes to
  `sendSnapshot`, without duplicating preparation or touching Foundry; or
- if extraction would unreasonably enlarge the production surface, rename the
  existing test to its truthful deterministic-preparation claim and add a
  focused source/invariant test that directly proves both branches consume the
  one `prepared` object created by `run`.

Do not claim branch equivalence from two calls to the same preparation function.
Do not introduce a second serializer, re-encode for one branch, or weaken the
existing checksum test.

## Finding 4 — contradictory documentation

The source comment and export contract say an undefined-valued property is
“deleted/skipped.” The implementation does not and must not delete anything.

Replace this everywhere in live documentation with precise wording such as:

> The property is skipped while constructing a new projected result; the
> source object and its property are unchanged.

Check the module README, contract, source comments, walkthrough and live
rehearsal remediation note for related overclaims. Preserve the historical
rehearsal `FAIL`; implementation does not convert it to a pass.

## Scope and versioning

- Keep the semantic policy introduced in 1.0.1: undefined-valued own enumerable
  object properties are omitted only while constructing the new boundary
  result; undefined array elements refuse; canonical undefined still refuses.
- Do not special-case `classRestriction`, advancement, one Item type or one ID.
- Do not use `JSON.parse(JSON.stringify(...))`.
- Keep on-wire schema version `1` unless a proven conflict requires stopping
  for review.
- Because 1.0.1 has not been reinstalled and this task corrects its unreleased
  remediation before deployment, retain module version `1.0.1` unless project
  policy demonstrably requires another patch bump. State the decision and
  evidence in the handoff.
- Do not change server, database, Caddy, module settings, Foundry installation
  or world state.

## Required verification

Before database-backed verification, prove `freedom_test` is the configured
disposable database, is at Alembic head and has a clean table-count baseline.
Refuse unexplained dirty state. At the end, prove the complete table inventory
equals the initial inventory table-for-table and the rehearsal artifact root is
empty.

Run and report exact commands and totals for:

1. all Foundry module Node tests;
2. `node --check` for every shipped script and test module;
3. targeted new path-confidentiality, depth and branch-equivalence tests;
4. `tests/test_exporter_contract.py`;
5. the complete targeted I-03 suite:

   ```text
   tests/test_artifact_store.py
   tests/test_audit_payload_policy.py
   tests/test_http_submission.py
   tests/test_snapshot_preview_service.py
   tests/test_snapshot_submission.py
   tests/test_snapshot_import_service.py
   tests/test_snapshot_database.py
   tests/test_snapshot_reconciliation.py
   tests/test_storage_claim_vocabulary.py
   tests/test_submission_composition.py
   tests/test_submission_database.py
   tests/test_submission_traceability.py
   ```

6. the full Python suite with `-q -rs`;
7. Python `compileall` over application, adapters, domain, tools, tests and
   migrations;
8. `alembic check` against `freedom_test`;
9. `git diff --check`;
10. a targeted diff and `git status --short` proving unrelated dirty changes
    were preserved.

## Required handoff and stop point

Update the existing Gemini walkthrough in place; do not create another
walkthrough. Its final report must include:

- each independent-review finding and exact resolution;
- the safe path-rendering rule and proof that dynamic keys cannot appear;
- exact depth semantics and the typed excessive-depth code;
- honest description of the download/submit evidence;
- all changed files;
- module/schema version decision;
- exact test commands and totals;
- initial/final database inventory equality and empty artifact-root result;
- confirmation that no real data, screenshot, credential or stable real ID was
  accessed or recorded;
- blockers and residual risks.

Stop after implementation, verification and walkthrough update. Do not install
or reinstall the module, restart Foundry, edit Caddy, start the rehearsal
endpoint, rerun either supervised rehearsal, change the historical `FAIL`,
close I-03 or claim Phase 2 completion.

The only next action is a second independent Codex implementation/security
review.

---
