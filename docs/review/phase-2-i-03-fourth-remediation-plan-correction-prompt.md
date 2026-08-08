# Gemini prompt — correct the fourth-remediation implementation plan

Use this prompt from `/opt/discord-bots/freedom-bot`.

---

Amend your existing implementation plan in place at:

`/home/foundry/.gemini/antigravity-ide/brain/0da55125-bd28-4e88-824f-b33e10805743/implementation_plan.md`

Do not create a new implementation plan and do not implement code yet.

The proposed `Object.freeze([...])` representation, unchanged vocabulary,
`.includes(key)` lookup, namespace privacy test and walkthrough update are
appropriate. Preserve them. Add the following missing binding requirements.

## 1. Make the representation guard precise

The planned source/API test must prove the actual chosen invariant rather than
only searching vaguely for `new Set(` or `new Map(`.

Require all of these:

- ESM namespace does not expose `SAFE_STRUCTURAL_KEYS` or another policy
  container;
- source declares the policy through `Object.freeze([ ... ])` (allow harmless
  formatting differences);
- source does not declare that policy as a `Set` or `Map`;
- behavioral tests remain the authority for the exact static/dynamic rendering
  outcomes;
- tests do not export or add a runtime mutation hook for private policy data.

Do not claim that a generic source scan proves all possible mutable objects are
absent. It proves only the deliberately chosen representation and public API.

## 2. Add database baseline refusal and cleanup proof

Before any database-backed command, require Gemini to:

1. prove the configured target is exactly the disposable `freedom_test`;
2. prove it is at Alembic head;
3. record the complete table-count inventory;
4. refuse unexplained nonzero business state instead of truncating it.

After verification, require proof that:

- final inventory equals initial inventory table-for-table;
- `/srv/freedom/snapshots-rehearsal` remains empty;
- no broad guessed truncation or cleanup touched pre-existing state.

## 3. Add binding scope and privacy constraints

The plan must state:

- use synthetic data only;
- do not access a Foundry world database, Actor/Item document, browser storage,
  credential, downloaded export, prior snapshot or failure screenshot;
- do not copy any real Actor, Item or advancement ID into tests, logs, examples
  or Markdown;
- preserve all unrelated dirty-tree changes;
- do not reset, checkout, clean, commit, push or reformat unrelated files;
- preserve the accepted projection, redaction, depth, canonical, dispatcher and
  transport behavior;
- retain module version `1.0.1` and schema version `1`.

## 4. Add the required handoff and hard stop

Require the existing walkthrough—not a new walkthrough—to report:

- the exact remaining finding and correction;
- the final private frozen-array representation;
- separate namespace-privacy, representation and behavioral evidence;
- every changed file and exact verification totals;
- initial/final database inventory equality and empty artifact root;
- confirmation that no real data, screenshot, credential or stable real ID was
  accessed or recorded;
- blockers and residual risks.

The plan must end with this stop condition:

> Stop after implementation, verification and updating the existing
> walkthrough. Do not install/reinstall the module, restart Foundry, edit Caddy,
> start the endpoint, run either supervised rehearsal, change the historical
> rehearsal FAIL, close I-03 or claim Phase 2 completion. The only next action
> is another independent Codex implementation/security review.

After amending the plan, report only the exact sections changed and wait for
maintainer approval before implementing.

---
