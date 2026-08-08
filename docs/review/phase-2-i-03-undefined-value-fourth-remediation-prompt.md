# Gemini prompt — fourth remediation: genuinely immutable path policy

Use this prompt from `/opt/discord-bots/freedom-bot`.

---

Perform one minimal fourth remediation of the unreleased Phase 2 I-03 module
version 1.0.1. The latest independent Codex review confirms the dispatcher
override, fixed-prose error, dynamic-key redaction and depth-limit defects are
resolved. One specification mismatch remains: the walkthrough and tests claim
the safe-key policy is immutable, but the implementation is still a mutable
JavaScript `Set`.

Preserve every existing dirty-tree change. Do not reset, checkout, clean,
reformat unrelated files, commit or push.

Read completely before editing:

- `.agents/AGENTS.md`;
- `docs/implementation-plan.md`;
- `docs/review/phase-2-i-03-undefined-value-third-remediation-prompt.md`;
- `docs/review/phase-2-supervised-rehearsal-2026-08-06.md`;
- `foundry-module/scripts/world-source.js`;
- `foundry-module/tests/projection.test.mjs`;
- the existing Gemini walkthrough at
  `/home/foundry/.gemini/antigravity-ide/brain/0da55125-bd28-4e88-824f-b33e10805743/walkthrough.md`.

Use synthetic data only. Do not access Foundry world data, Actor/Item documents,
browser storage, credentials, downloaded exports, prior snapshots or the
failure screenshot.

## Remaining finding

Current code:

```js
const SAFE_STRUCTURAL_KEYS = new Set([...]);
```

The `Set` is module-private, so the prior import-time `.add()` exploit is closed.
However, a `Set` remains mutable, and the approved implementation plan required
genuinely immutable module-private policy data. The walkthrough incorrectly
calls it an “immutable Set.” The test named `world-source.js does not export
SAFE_STRUCTURAL_KEYS or any mutable policy object` proves only that one named
binding is absent from the module namespace; it does not prove the internal
`Set` is immutable or that no mutable policy export exists.

## Required correction

In `foundry-module/scripts/world-source.js`:

1. Replace the `Set` with genuinely immutable module-private representation.
   Preferred minimal form:

   ```js
   const SAFE_STRUCTURAL_KEYS = Object.freeze([
     // existing exact vocabulary, unchanged
   ]);
   ```

   Query it with `.includes(key)`. A fixed `switch` or genuinely frozen lookup
   record is also acceptable.
2. Do not use `Object.freeze(new Set(...))`; freezing a Set does not disable
   `.add()`.
3. Keep the policy unexported. `safeKeySegment(key, ordinal)` may remain the only
   behavioral test seam.
4. Preserve the exact current static-key vocabulary. Do not add or remove keys
   in this task.
5. Preserve every current redaction, ordinal, projection, depth, cycle,
   canonical and dispatcher behavior.

## Required tests

In `foundry-module/tests/projection.test.mjs`:

- Keep behavioral tests proving static keys render literally and ID-, UUID-,
  name-like and arbitrary dynamic keys render only ordinal placeholders.
- Keep the ESM namespace assertion that `SAFE_STRUCTURAL_KEYS` is not exported.
- Rename the current overclaiming test so it says exactly what it proves, for
  example: `world-source.js does not export the safe-key policy`.
- Add a source/API guard proving the implementation does not reintroduce a
  `Set`/`Map` policy or export a mutable policy container. The guard must not
  expose private policy contents or couple tests to array ordering beyond the
  existing behavior tests.
- Run the previously added dispatcher, depth and confidentiality regressions
  unchanged.

Do not invent a runtime mutation hook merely to test private data. The point is
to make the representation immutable by construction and keep policy private.

## Documentation and walkthrough

Update the existing Gemini walkthrough in place; do not create another
walkthrough.

- Correct “module-private immutable Set” to the actual immutable representation.
- State honestly that the third remediation closed external mutation by making
  policy private, while this fourth remediation satisfies immutability by
  construction.
- Correct the proof statement so it distinguishes namespace privacy,
  representation immutability and behavioral redaction tests.
- Preserve the verified dispatcher, fixed-prose action, depth and redaction
  results.

Update only the existing sanitized remediation-status note in
`docs/review/phase-2-supervised-rehearsal-2026-08-06.md` if it currently calls
the Set immutable. Preserve the historical rehearsal `FAIL` and every pending
checkbox.

## Scope and version

- Retain module version `1.0.1` and schema version `1`.
- Do not alter the wire format or accepted undefined-property semantics.
- Do not modify workflow/dispatcher code unless a verification failure proves
  an actual regression; report that blocker instead of expanding scope.
- Do not edit Caddy, start an endpoint, install/reinstall the module, restart
  Foundry or rerun the supervised rehearsal.

## Required verification

Run and report exact commands and totals for:

1. all Foundry module Node tests;
2. `node --check` over every shipped script and test module;
3. targeted safe-policy privacy, immutability and redaction tests;
4. `tests/test_exporter_contract.py`;
5. the complete targeted I-03 Python suite from the prior plan;
6. the full Python suite with `-q -rs`;
7. Python `compileall`;
8. `alembic check` against `freedom_test`;
9. `git diff --check` and targeted `git status --short`.

Before database-backed verification, prove `freedom_test` is the disposable
target at Alembic head and record its complete clean table inventory. Refuse
unexplained dirty state. At the end, prove final inventory equals initial
inventory table-for-table and `/srv/freedom/snapshots-rehearsal` remains empty.

## Required handoff and stop point

The amended walkthrough must report:

- the precise remaining finding and correction;
- the final immutable, private representation;
- distinct privacy, immutability and behavioral evidence;
- every changed file and exact verification totals;
- unchanged module/schema versions;
- initial/final database inventory equality and empty artifact root;
- confirmation that no real data, screenshot, credential or stable real ID was
  accessed or recorded;
- blockers and residual risks.

Stop after implementation, verification and amending the existing walkthrough.
Do not install, restart Foundry, edit Caddy, run the rehearsal, change its
historical `FAIL`, close I-03 or claim Phase 2 completion. The only next action
is another independent Codex implementation/security review.

---
