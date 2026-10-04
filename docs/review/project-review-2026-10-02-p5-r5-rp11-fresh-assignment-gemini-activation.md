# Fresh R-5 Gemini activation — 2026-10-02

Decision ID: `C-P5.0-R5-RP11-FRESH-R5-A1`

Acceptance Authority: Peter Duscha

## Decision

Peter Duscha names **Gemini** as the independent executor for execution work
ID `C-P5.0-R5-RP11-FRESH-R5` under the accepted fresh R-5 procedure.

The exact reviewed procedure is preserved at
[`phase-5-0-p5-r5-rp11-fresh-independent-rebuild-reviewed-proposal.md`](phase-5-0-p5-r5-rp11-fresh-independent-rebuild-reviewed-proposal.md),
SHA-256 `f5b4c4e935817e7a68df3c8d1b6f8cc78617e0db6622a86a45ea38c1f0c18f94`.
Its acceptance record is
[`project-review-2026-10-02-p5-r5-rp11-fresh-assignment-r2-acceptance.md`](project-review-2026-10-02-p5-r5-rp11-fresh-assignment-r2-acceptance.md).
The active assignment adds acceptance and activation metadata only.

The confirmed handback path and `<HANDBACK>` substitution are:
`docs/review/phase-5-0-p5-r5-rp11-fresh-independent-rebuild-handback.md`.

Invoke the assignment in Gemini with:

```text
/goal Execute the active assignment in docs/review/phase-5-0-p5-r5-rp11-fresh-independent-rebuild-assignment.md. Proceed autonomously through every authorized step in order until the defined terminal state (PASS, INVALID RUN, or HARD STOP). Do not post intermediate progress updates, do not yield turns for user confirmation on background tasks, and do not stop until the final handback and closing record are fully written.
```

This invocation prevents conversational pauses but does not expand Gemini's
authority or override any tool-permission prompt or assignment stop condition.

## Independence and freshness

Gemini did not implement Claude's I-7/I-7-R1 work and is eligible under the
party-independence rule. Because Gemini performed the earlier stopped R-5 and
B1 work, the assignment's Gemini-specific clause is mandatory: Gemini must not
read, reuse, copy, compare against or inherit any resource or artifact from
those earlier runs. The new run must use wholly fresh roots, caches, checkout,
work directory, build output, trace, evidence and pytest tree.

Before any host action Gemini must write and sign the complete independence
attestation required by assignment §2.

## Bounded authority

Gemini is authorized to perform the accepted assignment once, in its exact
order, with only the substitutions permitted by §6.0. This activates only:

- the repository-host and `oracle-test` blocks written in assignment §6;
- the single exact secret-guard-safe `rsync` command in step 4b;
- fresh `/tmp/<RUN>-*` resources on `oracle-test`;
- the pinned snapshot download, provisioning, unprivileged build, comparisons,
  verifier and one 12-test corroborating pytest invocation written there; and
- the confirmed handback file, its closing record and immediate stop.

Every prerequisite failure, guard refusal, unexplained difference, unexpected
command or nonzero status follows the assignment's INVALID RUN or HARD STOP
rules. There is no retry, partial rerun or remediation authority. The earlier
`bubblewrap` installation authority is exhausted and is not renewed.

This activation does not authorize `sudo`, package or host changes, reboot,
services or databases, launcher installation, H-1/H-2, D9-4/D9-5, PO-14
discharge, RP-11 wiring, controlled writes, an evidence band, harness
`--execute`, an operational pass, secrets scanning, commit or push.

## Result gate

The run's result is not accepted in advance. Gemini must write the prescribed
handback and stop. R-5 remains Blocking and unaccepted as evidence until Codex
independently reviews that handback and Peter Duscha records a separate result
decision. RP-11 remains unwired and unmet; `plan.is_executable=False`; PO-9
and PO-14 remain open; OD-62 G-A remains conditional; and Package 5.0 remains
not ready.
