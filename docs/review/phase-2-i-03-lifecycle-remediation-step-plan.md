# Phase 2 I-03 lifecycle remediation — bounded Gemini step plan

Date: 2026-08-07

Run these prompts in order. Do not combine steps. After each Gemini step, give
its walkthrough and resulting workspace to Codex for review before starting the
next step.

| Step | Prompt | Required stopping condition |
|---|---|---|
| 1 | `phase-2-i-03-lifecycle-step-1-restore-tests.md` | The eight removed regressions are restored and pass; production code is unchanged. |
| 2 | `phase-2-i-03-lifecycle-step-2-reproduce-races.md` | Deterministic production-path race tests exist and fail for the expected state-transition reason; production code is unchanged. |
| 3 | `phase-2-i-03-lifecycle-step-3-fix-races.md` | The minimal per-operation concurrency fix passes Steps 1–2 tests and the complete Node suite. |
| 4 | `phase-2-i-03-lifecycle-step-4-harden-classification.md` | Failure-disposition metadata is closed and fail-safe, with focused tests. |
| 5 | `phase-2-i-03-lifecycle-step-5-evidence-handoff.md` | Controlled records match verified reality and a final independent-review handoff exists. |

Global rules for every step:

- Work in `/opt/discord-bots/freedom-bot` on the existing dirty tree.
- Read `AGENTS.md`, `.agents/AGENTS.md`, and the applicable Phase 2 section of
  `docs/implementation-plan.md` before acting.
- Preserve all unrelated work. Never reset, checkout, clean, stage, commit,
  push, install, deploy, or rehearse.
- Use synthetic fixtures only. Never access Foundry, real exports, credentials,
  production services, or player data.
- Do not change module/schema versions unless a later maintainer instruction
  explicitly authorizes it.
- Do not claim I-03 or Phase 2 complete, accepted, approved, or gate-ready.
- Update Gemini's existing walkthrough in place for the current step. Do not
  create competing walkthroughs.
- Stop immediately at the step boundary, even if the next correction looks
  obvious.

Codex review gates:

1. After Step 1, verify all eight restored tests genuinely exercise the named
   behavior and no production file changed.
2. After Step 2, independently reproduce every expected failure. Failing tests
   are the intended deliverable for that step and must not be “fixed” there.
3. After Step 3, inspect concurrency semantics and run the full Node suite plus
   focused interleaving reproductions.
4. After Step 4, review fail-closed classification and error-data safety.
5. After Step 5, review evidence accuracy before authorizing installation or a
   supervised rehearsal rerun.
