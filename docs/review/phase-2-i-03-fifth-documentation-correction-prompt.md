# Gemini prompt — final documentation correction for I-03 projection remediation

Use this prompt from `/opt/discord-bots/freedom-bot`.

---

Perform a documentation-only correction after the independent review of the
fourth remediation. Do not change functional behavior.

The frozen-array implementation and dispatcher behavior passed review, and the
Foundry module suite independently reports `101 passed, 0 failed`. Two stale
statements remain:

1. `foundry-module/scripts/world-source.js` now defines
   `SAFE_STRUCTURAL_KEYS` as a frozen array, but its preceding comment still
   says “Keys in this set”.
2. `docs/review/phase-2-supervised-rehearsal-2026-08-06.md` still records only
   the third-remediation encapsulation result. The walkthrough claims this file
   was updated with the fourth-remediation frozen-array result, but it was not.

## Required edits

### `foundry-module/scripts/world-source.js`

Change only the stale comment from “Keys in this set” to precise array-neutral
wording such as “Keys in this allowlist”. Do not change the frozen array,
vocabulary, `safeKeySegment`, projection, depth, canonicalisation or dispatcher
code.

### `docs/review/phase-2-supervised-rehearsal-2026-08-06.md`

Amend only the existing sanitized remediation-status paragraph under Section B:

- preserve the original rehearsal `FAIL` and every pending checkbox;
- preserve the first through third remediation history in concise form;
- state that the fourth remediation replaced the private mutable Set with a
  private `Object.freeze([...])` string array while preserving redaction
  behavior;
- state the current verified Node total accurately;
- keep independent review, atomic reinstall and complete rehearsal rerun marked
  pending;
- include no real Actor/Item/advancement ID, name, mechanic, credential or raw
  value.

### Existing Gemini walkthrough

Amend the existing walkthrough in place at:

`/home/foundry/.gemini/antigravity-ide/brain/0da55125-bd28-4e88-824f-b33e10805743/walkthrough.md`

Do not create another walkthrough. Add a short review-correction note stating
that independent review found and corrected the stale source comment and the
omitted rehearsal-record update. Keep its functional verification claims
unchanged unless rerun results differ.

## Verification

Run and report:

1. `node --test "tests/*.test.mjs"` from `foundry-module`;
2. `node --check` for shipped scripts and test modules;
3. `tests/test_exporter_contract.py` against `freedom_test`;
4. `git diff --check`;
5. targeted `git diff` and `git status --short` proving no functional code or
   unrelated dirty work changed.

Before the database-backed golden test, prove the target is exactly the clean
disposable `freedom_test`; afterward prove its complete table inventory is
unchanged and `/srv/freedom/snapshots-rehearsal` remains empty.

## Scope and stop point

- Use no real world data, screenshot, credential, downloaded export or prior
  snapshot.
- Preserve module version `1.0.1`, schema version `1`, and all current behavior.
- Do not install/reinstall the module, restart Foundry, edit Caddy, start the
  endpoint or rerun a supervised rehearsal.
- Do not change the historical rehearsal `FAIL`, close I-03 or claim Phase 2
  completion.

Stop after these documentation corrections and verification. The next action
is independent Codex confirmation, followed—only if accepted—by the separately
authorized atomic reinstall and complete supervised rehearsal rerun.

---
