# Claude task — R4-R1 Antigravity wait-contract remediation

Work ID: `C-P5.0-R5-RP11-FRESH-D1-R1`  
Assignee: Claude  
Scope: repository-only remediation and local tests  
No `oracle-test` access or R-5 execution

## Finding to remediate

Read and remediate `R4-D1-1` in:

`docs/review/project-review-2026-10-04-p5-r5-rp11-antigravity-delivery-redesign.md`

R4 currently tells Gemini to stop if Antigravity returns before the runner's
final line. That conflicts with the required autonomous `/goal` terminal state.

## Required change

Amend R4 so that Gemini may use Antigravity's wait facility only to wait for
the same already-started runner task until it completes and prints its final
line. Waiting:

- is not a second runner invocation or operational command;
- must not send input, EOF or signals;
- must not poll or inspect the OS process independently;
- must not yield a user turn or ask for confirmation;
- must not launch another action; and
- ends only when the same task returns, or when the Antigravity wait facility
  itself reports a terminal transport failure.

On a terminal transport failure with unknown runner state, Gemini reports the
condition and stops. It must not reinvoke, retry, repair, poll or signal the
runner. Preserve the runner's autonomous closeout behavior.

Record these maintainer dispositions in the revised proposal:

- U-14: same-task Antigravity waiting as above;
- U-15: a pre-run refusal consumes the activation;
- U-16: no runner timeout; a hung run requires separately authorized recovery;
- U-17: invocation-based attestation accepted.

Do not change the substantive R3 command resources, runner behavior, pins,
identifiers or proposed handback path unless required by the documentation
change. If any controlled file changes, update all affected pins and tests.

## Verification and handback

Run the focused runner tests, relevant syntax checks and `git diff --check`.
Audit R4 for contradictory instructions to stop early, avoid waiting, poll,
send EOF, reinvoke or yield. Write the handback to:

`docs/review/phase-5-0-p5-r5-rp11-antigravity-delivery-redesign-r1-handback.md`

Report exact changed-file identities and unresolved issues. Stop afterward;
R4 remains unaccepted and no host or execution authority exists.
