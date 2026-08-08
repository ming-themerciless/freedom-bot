# Claude prompt — independent review of Phase 2 I-03 lifecycle Steps 3–4

Use this prompt from `/opt/discord-bots/freedom-bot` in a fresh Claude Code
session.

---

Perform a read-only independent implementation and security review of the
prepared-snapshot lifecycle Steps 3–4. Codex implemented the final correction;
you are the reviewer, not an implementing agent.

Do not edit, create, delete, stage, commit, push, install, deploy, start a
service, access Foundry, read a real export, use a credential, mutate a database,
or update a walkthrough or controlled record. If you find an issue, report it
with evidence; do not fix it.

## Required context

Read completely before reviewing:

1. `AGENTS.md` and `.agents/AGENTS.md`;
2. `docs/implementation-plan.md`, especially §§6.4–6.5 and Phase 2;
3. `docs/review/phase-2-i-03-lifecycle-remediation-step-plan.md`;
4. `docs/review/phase-2-i-03-lifecycle-step-3-fix-races.md`;
5. `docs/review/phase-2-i-03-lifecycle-step-4-harden-classification.md`;
6. `foundry-module/scripts/workflow.js`;
7. `foundry-module/scripts/transport.js`;
8. `foundry-module/scripts/main.js`;
9. `foundry-module/tests/workflow.test.mjs` and
   `foundry-module/tests/transport.test.mjs`; and
10. current targeted `git status`. The module is untracked, so ordinary
    `git diff` cannot establish its history; inspect the files directly.

## Changes under review

Codex changed the lifecycle implementation to:

- use a fresh opaque `Symbol` as the authority for every workflow or standalone
  preparation operation;
- retain only the current operation identity, so memory remains constant and
  operation identities never wrap or collide;
- establish operation authority before asynchronous validation;
- keep prepared-payload identity separate from operation identity;
- preserve strict cached object/bytes/checksum/timestamp/idempotency-key reuse;
- make explicit discard invalidate older operations while retaining authority
  for its own fresh workflow;
- prevent an older completion from confirming, pinning, clearing or
  resurrecting state after a newer operation or discard;
- drive discard race tests through `executeWorkflow(discardPinned: true)`, the
  same coordinator used by `main.js`;
- gate fresh preparation deterministically so an old request completes while
  preparation is genuinely in flight;
- define one frozen four-value `FailureDisposition` vocabulary in
  `workflow.js`;
- make transport errors carry only bounded facts (`code`, `stage`, `status`),
  not authoritative disposition strings;
- classify failures in one workflow policy;
- ignore arbitrary or mutated `error.disposition` metadata;
- clear only established local or definitive refusals; and
- conservatively pin unknown post-dispatch and non-4xx/5xx response outcomes.

## Review questions

Report findings ordered by severity, with exact file and line references.
Review at least:

1. Can any stale same-payload or different-payload operation become current or
   mutate current state?
2. Can operation identity collide, wrap, leak, accumulate, or enter snapshot
   bytes, HTTP requests, receipts, logs or credentials?
3. Does the production discard-and-submit path retain its own authority while
   invalidating every older operation?
4. If fresh preparation fails after discard, can any older completion restore
   the discarded payload?
5. Does latest-operation-wins have deterministic invocation-order semantics,
   independent of completion order and wall-clock time?
6. Does standalone `prepareSnapshot()` remain safe and compatible with the
   coordinated `executeWorkflow()` path?
7. Are unchanged content, changed Actor/Item content, changed folder scope,
   folder switching, download/submission reuse, one-entry bounds and credential
   isolation preserved?
8. Is failure classification defined in exactly one authoritative place?
9. Can invalid/missing/mutated metadata make a post-dispatch uncertainty clear
   state?
10. Are local endpoint/credential failures, definitive 4xx responses,
    `request_key_conflict`, documented same-key codes, HTTP 5xx, timeout,
    network failure, malformed responses and unknown post-dispatch outcomes
    correctly classified?
11. Do tests drive production orchestration rather than merely calling private
    mutators, and are their deferred promises always settled?
12. Do any messages overclaim what was or was not recorded, expose raw server or
    exception content, or weaken credential confidentiality?

Treat security, duplicate submission, stale-operation mutation, lost pinned
retry, false delivery certainty, credential retention and evidence overstatement
as blocking or important according to impact.

## Independent verification

Run each command once with a hard timeout. Do not poll or retry.

```bash
cd /opt/discord-bots/freedom-bot/foundry-module

timeout 10s node --test \
  --test-name-pattern='failure classification|disposition metadata|unknown post-dispatch|executeWorkflow race|state operation identity' \
  tests/workflow.test.mjs

timeout 30s node --test tests/*.test.mjs

for file in scripts/*.js tests/*.mjs; do
  timeout 5s node --check "$file" || exit 1
done

cd /opt/discord-bots/freedom-bot
git diff --check
git status --short -- foundry-module docs/review docs/project-management/status.md
```

Expected current evidence, which you must independently verify rather than
trust:

- focused lifecycle/classification selection: 10 passed;
- complete module suite: 123 passed;
- zero failures, skips, cancellations, hangs or timeouts;
- syntax checks and `git diff --check`: clean; and
- version 1.0.2 remains uninstalled and unrehearsed.

## Required response

Lead with findings. If there are no findings, state `No blocking, important or
minor findings.` explicitly, then list residual risks and verification. Distinguish
implementation correctness from pending Step 5 evidence reconciliation and the
later supervised rehearsal. Do not claim Phase 2 accepted or gate-ready.

End with exactly one of:

- `Steps 3–4 accepted for Step 5 evidence reconciliation.`
- `Steps 3–4 not accepted; findings require remediation and independent re-review.`

---
