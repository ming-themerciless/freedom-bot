# Independent re-review — fresh R-5 assignment R2

Date: 2026-10-02

Reviewer: Codex

Reviewed inputs:

- [`phase-5-0-p5-r5-rp11-fresh-independent-rebuild-assignment-r2-claude-prompt.md`](phase-5-0-p5-r5-rp11-fresh-independent-rebuild-assignment-r2-claude-prompt.md), SHA-256 `0efbf17ef0144b884faa7972d84429dc92dc0ec9abc13f82147ee855a1dda57c`;
- [`phase-5-0-p5-r5-rp11-fresh-independent-rebuild-assignment.md`](phase-5-0-p5-r5-rp11-fresh-independent-rebuild-assignment.md), SHA-256 `f5b4c4e935817e7a68df3c8d1b6f8cc78617e0db6622a86a45ea38c1f0c18f94`; and
- [`phase-5-0-p5-r5-rp11-fresh-independent-rebuild-assignment-r2-handback.md`](phase-5-0-p5-r5-rp11-fresh-independent-rebuild-assignment-r2-handback.md), SHA-256 `897c71c07aefedf64820d161196f6f31878e690425c0f22551b912637a6f1b8a`.

## Disposition

**No Blocking, Important or Optional finding.** `FRESH-A1-R2-1` is Closed as remediated on Codex's recommendation, subject to Peter Duscha's decision.

The revised assignment is decision-ready. Peter may accept, amend or reject it and, if accepting it for execution, must name the independent executor. This review does not accept the assignment, appoint an executor or authorize any host action.

R-5 remains stopped, Blocking, unaccepted and unauthorized until that explicit acceptance exists. RP-11 remains unwired and unmet, `plan.is_executable=False`, PO-9 and PO-14 remain open, and Package 5.0 remains not ready.

## Finding verification

The assignment keeps the required timestamp evidence and makes it executable within the bounded command set:

- §6.0 defines fifteen timed scopes: the whole run; steps 1, 2, 3, 4a, 4b, 4c, 4d and 5; combined steps 6/7; steps 8, 9, 10, 11 and 12.
- Each scope has an explicit start and end producer. The twelve ordinary step blocks install a written `EXIT` handler, take the start timestamp before substantive work and take the end timestamp on success, INVALID RUN or HARD STOP.
- The handler captures the exiting status before any other action. A prior nonzero status remains governing; after an otherwise successful block, an end-timestamp failure governs. An isolated shell-semantics check independently confirmed that an `EXIT` handler using this pattern preserves status 20.
- Step 4b retains the exact standalone, guard-safe `rsync` command. Separate written timestamp blocks bracket it without wrapping, redirecting, chaining or changing its bytes. The end block is the only permitted follow-up after a nonzero synchronization status.
- Step 12 has a written start block and a written closing block. The latter checks the handback body, appends the step-12 and whole-run end values from one clock reading, records the timestamp status inside the closing record and then requires immediate stop.
- §7 expressly authorizes these timestamp commands and retains the rule that any other command or block-text change is unexpected and a HARD STOP.
- §8 makes complete successful timestamp evidence a PASS condition and missing, failed or malformed timestamp evidence a HARD STOP.
- §10 now maps the handback timestamp table to the exact §6.0 scopes and identifies the two values written by the closing record.

The assignment therefore no longer requires evidence that its authorized procedure cannot produce.

## Preserved controls

The R2 edit preserves the earlier remediations and controlling boundaries: checked statuses remain fail-closed; expected absences have explicit success semantics; the secret-excluding transport remains unchanged; HA-3 cannot qualify through a bubblewrap version-only difference; exact-byte equality is the only `cc1check.py` PASS route; the same-invocation R-1/R-2 gate and 12-test/zero-skip requirement remain; and the run remains single-attempt with no retry, remediation, privilege escalation or prerequisite repair.

The accepted inputs remain manifest version 30, aggregate digest `28a4f4c2b7596e9042f6b12a34f5684b3499a3fafd997e306fe25f6798e8a526`, and the 5,120-byte diagnostic fixture with SHA-256 `b77f92dcdcf899c5459fec606f16dc325ed5329516cbab5faea86b479992905b`.

## Checks performed

- Read the R2 handback and revised assignment, including every timestamp convention, modified execution block, step-12 closing mechanism, authorization rule, verdict rule and handback requirement.
- Recomputed the three reviewed-file digests above and the R1-review digest cited by the handback; all matched their records.
- Verified all relative links in the assignment and R2 handback resolve.
- Verified both files have no trailing whitespace and `git diff --check` reports no issue.
- Confirmed repository manifest constant `MANIFEST_VERSION = 30`.
- Ran one repository-local, generic shell-semantics check of `EXIT`-trap status preservation; it returned status 20 as intended. No proposed R-5 block or command was executed.

No SSH, `rsync`, remote access, provisioning, build, pytest, verifier, B1, IC-1 or R-5 action occurred. No implementation, test, fixture, manifest, current-state or governance file was modified. No staging, commit or push occurred.
