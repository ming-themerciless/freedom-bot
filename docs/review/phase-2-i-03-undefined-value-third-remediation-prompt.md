# Gemini prompt — third remediation of Foundry boundary projection

Use this prompt from `/opt/discord-bots/freedom-bot`.

---

Perform one narrowly bounded third remediation of the unreleased Phase 2 I-03
module version 1.0.1. A second independent Codex review confirmed the original
path-redaction and depth findings are functionally addressed, but found two new
blocking integrity defects introduced by the remediation plus one unsafe error
message and inaccurate walkthrough claims.

Preserve every existing dirty-tree change. Do not reset, checkout, clean,
reformat unrelated files, commit or push.

Read completely before editing:

- `.agents/AGENTS.md`;
- `docs/implementation-plan.md`;
- `docs/review/phase-2-i-03-undefined-value-second-remediation-prompt.md`;
- `docs/review/phase-2-supervised-rehearsal-2026-08-06.md`;
- `foundry-module/scripts/world-source.js`;
- `foundry-module/scripts/workflow.js`;
- `foundry-module/scripts/main.js`;
- `foundry-module/tests/projection.test.mjs`;
- `foundry-module/tests/workflow.test.mjs`;
- the existing Gemini walkthrough at
  `/home/foundry/.gemini/antigravity-ide/brain/0da55125-bd28-4e88-824f-b33e10805743/walkthrough.md`.

Use synthetic data only. Do not access Foundry world data, Actor/Item documents,
browser storage, credentials, downloaded exports, prior snapshots or the failure
screenshot.

## Finding 1 — blocking: the “closed” safe-key policy is externally mutable

`world-source.js` exports `SAFE_STRUCTURAL_KEYS` as a mutable `Set`. Any importer
can call `.add(dynamicKey)`, after which `safeKeySegment` emits that raw dynamic
key. Reproduction against the current implementation:

```text
before=.{key:0}
after=.PrivateDynamicIdentifier
redaction_defeated=true
```

This makes the walkthrough claim “closed allowlist” false and means path
confidentiality depends on nobody mutating a public object.

### Required correction

- Do not export a mutable allowlist.
- Represent the allowlist as module-private immutable data. Do not use
  `Object.freeze(new Set(...))`: freezing a `Set` does not disable `.add()`.
  A module-private frozen array/lookup record, a switch, or another genuinely
  non-mutable representation is acceptable.
- `safeKeySegment` may remain exported for behavioral testing, but it must not
  expose or accept mutable policy state.
- Tests must prove static keys remain readable and ID-, UUID-, name-like and
  arbitrary dynamic keys remain ordinal placeholders.
- Add a source/API regression proving the mutable policy object is no longer an
  export. Tests must not import internal policy data merely to assert its
  contents.
- Retain the fixed path, depth, omission, cycle and unsupported-type behavior
  already implemented.

## Finding 2 — blocking: `submitOptions` can replace the prepared snapshot

The dispatcher currently calls:

```js
sendSnapshot({ prepared, ...submitOptions })
```

Therefore `submitOptions.prepared` overwrites the genuine prepared object. The
current implementation reproduces `prepared_overridden=true`. This contradicts
the central invariant that both branches consume the one validated, checksummed
prepared snapshot.

### Required correction

Remove `submitOptions` from this pure dispatcher; `main.js` already captures the
endpoint and credential in its submission callback and does not need this
extension point.

Use the smallest API with one invariant:

```text
dispatchWorkflow({prepared, action, downloadPrepared, submitPrepared})
```

Both callbacks receive the exact `prepared` object by reference identity:

- download callback reads `prepared.bytes`, checksum and metadata as needed;
- submit callback passes that same object to `sendSnapshot`;
- the dispatcher never clones, spreads, merges, encodes or prepares it again;
- exactly one callback runs;
- an unsupported action runs neither callback.

Names may differ, but the identity and absence of an override/merge surface are
mandatory. Update `main.js` without changing download bytes, filename,
notification, endpoint, credential lifetime or receipt behavior.

Add tests proving:

- both callbacks receive `strictEqual(received, prepared)`;
- each action invokes exactly one callback;
- extra caller properties cannot replace the prepared object;
- no second preparation or encoding occurs;
- malformed prepared input and unsupported actions still refuse safely.

## Finding 3 — unsafe typed error echoes the unsupported action

`WorkflowError("unsupported_action")` currently interpolates the rejected
`action` string. `notifyFailure` treats `WorkflowError` as safe and displays its
message. A typed operator-visible error must contain only fixed
repository-authored prose.

Change the message so it does not include the rejected value. Add a regression
using a synthetic secret/name-like action and prove the value is absent from the
message while the stable code remains `unsupported_action`.

## Walkthrough corrections

Update the existing walkthrough in place; do not create a new walkthrough.

Correct these claims:

- The allowlist was not closed while an exported mutable `Set` controlled it.
  State how the third remediation makes policy non-mutable from imports.
- The download callback previously received `prepared.bytes`, not the prepared
  object. After the new dispatcher API, state only what tests genuinely prove.
- Record the `submitOptions.prepared` override reproduction and its removal.
- Record the fixed-prose unsupported-action result.
- Preserve the historical rehearsal `FAIL` and all pending checks.

Update the existing rehearsal remediation-status note only with a sanitized
statement that this third remediation was implemented and still awaits
independent review, reinstall and a full rerun. Do not turn any rehearsal item
into a pass.

## Scope and version

- Retain module version `1.0.1`; it remains unreleased and uninstalled.
- Retain on-wire schema version `1`.
- Do not alter the accepted undefined-property semantic, canonical encoder,
  64-level bound, server, database schema or transport contract.
- Do not special-case a real field or identifier.
- Do not edit Caddy, start an endpoint, install/reinstall the module, restart
  Foundry or rerun a supervised rehearsal.

## Required verification

Before database-backed verification, prove `freedom_test` is the disposable
target at Alembic head and record a complete clean table inventory. Refuse
unexplained dirty state. Prove final inventory equals initial inventory
table-for-table and `/srv/freedom/snapshots-rehearsal` remains empty.

Run and report exact commands and totals for:

1. all Foundry module Node tests;
2. `node --check` over every shipped script and test module;
3. the targeted mutable-policy, prepared-identity/override and fixed-message
   regressions;
4. `tests/test_exporter_contract.py`;
5. the complete targeted I-03 Python suite named in the prior remediation plan;
6. the complete Python suite with `-q -rs`;
7. Python `compileall`;
8. `alembic check` against `freedom_test`;
9. `git diff --check` and targeted `git status --short`.

## Required handoff and stop point

The amended walkthrough must report:

- each finding and exact resolution;
- proof that no importer can mutate path-redaction policy;
- the final dispatcher signature and prepared-object identity evidence;
- proof that caller options cannot replace prepared data;
- proof that unsupported action values never enter displayed errors;
- every changed file and exact test totals;
- module/schema version decision;
- initial/final database inventory equality and empty artifact root;
- confirmation that no real data, screenshot, credential or stable real ID was
  accessed or recorded;
- blockers and residual risks.

Stop after implementation, verification and amending the existing walkthrough.
Do not install, restart Foundry, edit Caddy, run the rehearsal, change its
historical `FAIL`, close I-03 or claim Phase 2 completion. The only next action
is another independent Codex implementation/security review.

---
