# Claude task — redesign fresh R-5 delivery for Antigravity

Work ID: `C-P5.0-R5-RP11-FRESH-D1`  
Assignee: Claude  
Scope: repository-only design, implementation and local tests  
No `oracle-test` access or R-5 execution

## Objective

Replace the failed interactive heredoc/background-terminal delivery mechanism
with a deterministic, non-interactive runner and prepare a complete successor
R-5 assignment that Gemini can invoke through Antigravity without manually
sending EOF or managing individual background tasks.

Write the handback to:

`docs/review/phase-5-0-p5-r5-rp11-antigravity-delivery-redesign-handback.md`

## Required inputs

Read the canonical instructions and current-state documents, then read in full:

- the accepted R3 assignment;
- the R3 handback;
- Codex's R3 HARD STOP review; and
- Peter's R3 HARD STOP acceptance and redesign authority.

Do not read or reuse any disposable artifact from an earlier run.

## Required deliverables

1. A repository-owned, non-interactive runner with exact reviewable source
   bytes. Prefer a small Python orchestrator plus static command resources over
   terminal-fed heredocs. It must not require interactive stdin or an EOF.
2. Focused local tests that simulate command execution. They must not contact
   `oracle-test`, download packages or execute R-5. Cover at least:
   - Step 1 success and progression;
   - Step 1 missing output despite exit 0;
   - nonzero first-step failure;
   - first-failure stop with no later operational step;
   - unconditional S12.start, handback-body and S12.end closeout;
   - closing-record immutability; and
   - rejection of altered command resources or runner identity.
3. A complete standalone successor assignment derived from R3. Preserve its
   substantive commands, pinned inputs, `/var/tmp` resource model, comparisons,
   first-failure semantics and terminal verdicts. Replace only the delivery and
   closeout orchestration needed to solve `FRESH-R3-HS-1` and
   `FRESH-R3-HS-2`.
4. Pin the runner, every static command resource and every focused test by
   SHA-256 and byte length in the proposed assignment. The run must verify
   those identities before any remote access.
5. Define one short, non-interactive Gemini invocation path. Gemini must not
   paste multiline scripts, operate an interactive terminal, send EOF, poll a
   background terminal job, or decide manually which step follows.
6. Ensure the runner itself enforces: exact order; exactly-once step attempts;
   no continuation after the first terminal condition; capture of stdout,
   stderr and true process status; mandatory closeout; one immutable handback;
   and no cleanup, retry or remediation.
7. Preserve the standard resolved `/goal` instruction in the proposed
   assignment, pointing to that successor assignment's final path.

## Constraints

- Do not execute any R-5 step or remote command.
- Do not access `oracle-test`.
- Do not install dependencies or change host configuration.
- Do not read secrets or protected files.
- Do not alter accepted launcher inputs or normative baselines.
- Do not activate Gemini or claim R-5 readiness.
- Do not commit or push.

If exact preservation of R3's command semantics is incompatible with the
runner design, stop and document the conflict rather than silently changing a
gate or command.

## Verification and handback

Run focused local unit tests, syntax/type checks appropriate to the new runner,
all existing directly affected tests, and `git diff --check`. Audit the final
proposal for interactive stdin, heredoc, background-task, retry and cleanup
paths. Report files changed, exact results, checks not run, SHA-256/length of
every proposed controlled file, unresolved decisions and reviewer focus.

Stop after writing the proposal and handback. The successor is not executable
until Codex independently reviews it and Peter records a separate acceptance
and Gemini activation.
