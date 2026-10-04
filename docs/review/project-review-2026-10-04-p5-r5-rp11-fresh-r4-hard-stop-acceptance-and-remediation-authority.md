# R4 HARD STOP acceptance and `cc1.v` determinism-remediation authority

Date: 2026-10-04  
Decision owner: Peter Duscha, Maintainer and Acceptance Authority  
Recorded by: Codex

## Decision

Peter Duscha accepts Codex's independent review and Gemini's R4 terminal state
as a valid consumed **HARD STOP**. The run is not an R-5 PASS and may not be
resumed, retried, reclassified or continued. Peter accepts Important finding
`FRESH-R4-HS-1` as open against the immutable handback.

- [Gemini handback](phase-5-0-p5-r5-rp11-fresh-independent-rebuild-r4-handback.md)
- [Independent review](project-review-2026-10-04-p5-r5-rp11-fresh-r4-hard-stop.md)

## Staged authority

Peter accepts Codex's recommended sequence and authorizes stages 2–4 subject
to their stated gates:

1. **Claude remediation — active now.** Claude is assigned the repository-only
   determinism audit and remediation in
   [`phase-5-0-p5-r5-rp11-fresh-r4-cc1-determinism-remediation-claude-prompt.md`](phase-5-0-p5-r5-rp11-fresh-r4-cc1-determinism-remediation-claude-prompt.md).
2. **Codex independent review — authorized after return.** Codex will review
   Claude's exact changes and evidence. Claude cannot close the finding or
   approve a successor run.
3. **Successor Gemini run — conditionally authorized as the next stage only if
   Codex finds the contract closed.** This is approval of the staged sequence,
   not current host activation. Before execution, Codex must prepare or review
   a complete digest-pinned successor assignment and record the exact Gemini
   activation prompt. Gemini receives host authority only when that exact
   assignment and activation record exist; no old assignment may be reused.

This staging preserves the mandatory independent-review gate. It does not
authorize Claude or Codex to access `oracle-test`, clean retained evidence,
execute R-5, install packages, change configuration or services, read secrets,
commit or push. The retained
`/var/tmp/p5-r5-fresh-20261003T234834Z-4fc93046-*` paths remain untouched.

R-5 remains Blocking and unaccepted; D9-3 remains incomplete; RP-11 remains
unwired and unmet; `plan.is_executable=False`; PO-9 and PO-14 remain open; and
Package 5.0 remains not ready.
