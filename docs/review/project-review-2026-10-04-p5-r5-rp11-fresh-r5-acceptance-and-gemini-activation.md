# Fresh R-5 successor R5 — remediation acceptance and Gemini activation

Date: 2026-10-04  
Decision owner: Peter Duscha, Maintainer and Acceptance Authority  
Executor: Gemini

## Acceptance

Peter Duscha accepts Codex's independent review of Claude's determinism
remediation and its recommendations:

- `FRESH-R4-HS-1` is **Closed as remediated**;
- the two fixed compiler inputs are accepted:
  `--param=ggc-min-expand=100` and
  `--param=ggc-min-heapsize=131072`;
- the dated amendment in the accepted D2 design is accepted as the current
  compiler-vector and byte-drift clarification;
- R5 work ID `C-P5.0-R5-RP11-FRESH-R5-R5` and handback path
  `docs/review/phase-5-0-p5-r5-rp11-fresh-independent-rebuild-r5-handback.md`
  are confirmed;
- the R4 remote paths remain retained and forbidden as inputs; no cleanup is
  authorized; and
- S10 remains the accepted 12-test contract.

The exact R5 assignment is accepted at SHA-256
`4073360b0894c212e5b5507249c011d1d4197c09af2094e877829fcb9b00a1e1`
and 140,080 bytes.

- [Claude handback](phase-5-0-p5-r5-rp11-fresh-r4-cc1-determinism-remediation-handback.md)
- [Independent review](project-review-2026-10-04-p5-r5-rp11-fresh-r4-cc1-determinism-remediation.md)
- [Accepted R5 assignment](phase-5-0-p5-r5-rp11-fresh-independent-rebuild-assignment-r5.md)

## Commit precondition satisfied

Codex created focused commit
`4cbdf0b6ecabad7484e64ff0485587a17f55dcaf`, containing exactly the 17
reviewed remediation, contract, runner and test files under `infra/`, `tests/`
and `tools/`. No governance or unrelated workspace change was staged or
committed.

After the commit:

- `git status --short --untracked-files=all -- infra tests tools pytest.ini`
  produced no output;
- runner SHA-256 is
  `5626a9ecfa8486b058cfe9ab1c45f163671827d77a7f4adb34a1e8b9145a9142`;
- runner-test SHA-256 is
  `95647bb82646550ffd09e4a693136a6ff1dac20bbfd137cde017ed4544a3154f`;
- every R5 Appendix C identity passed `sha256sum --check`; and
- `git diff --check` passes.

The independent review reproduced 4,159 focused passes and 16 explicit
root-dependent skips because no pinned local root was available in Codex's
session. Claude's reviewed evidence reports all 4,175 focused cases passing
with two R-1-verified roots. R5 is the independent different-host confirmation.

## One-run activation

Gemini is activated for exactly one invocation of the accepted R5 assignment.
Gemini may issue only the assignment's single digest-pinned runner command and
wait on that same Antigravity task under the accepted waiting contract. The
runner alone performs the exact ordered actions, first-terminal-condition
handling and immutable closeout.

There is no retry, remediation, cleanup, package, privilege, configuration,
service/database, operational, secrets, additional commit or push authority.
Authority ends at PASS, INVALID RUN, HARD STOP, incomplete closeout, terminal
transport failure or pre-run refusal. A further invocation requires a new
maintainer decision.

R-5 remains Blocking and unaccepted until the resulting handback is
independently reviewed and Peter records its disposition. RP-11 remains
unwired and unmet; `plan.is_executable=False`; PO-9 and PO-14 remain open; and
Package 5.0 remains not ready.

## Gemini invocation

```text
/goal Execute the active assignment in docs/review/phase-5-0-p5-r5-rp11-fresh-independent-rebuild-assignment-r5.md. Proceed autonomously through every authorized step in order until the defined terminal state (PASS, INVALID RUN, or HARD STOP). Do not post intermediate progress updates, do not yield turns for user confirmation on background tasks, and do not stop until the final handback and closing record are fully written.
```
