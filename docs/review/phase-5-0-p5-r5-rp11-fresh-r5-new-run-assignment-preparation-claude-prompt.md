# Claude task — prepare the post-cleanup fresh R-5 assignment

Work ID: `C-P5.0-R5-RP11-FRESH-A2`  
Assignee: Claude  
Scope: repository documentation only  
Output: `docs/review/phase-5-0-p5-r5-rp11-fresh-independent-rebuild-assignment-r3-handback.md`

## Objective

Prepare a complete, standalone, mechanically executable successor to:

`docs/review/phase-5-0-p5-r5-rp11-fresh-independent-rebuild-assignment.md`

for one wholly new Gemini run. Write the proposed assignment to:

`docs/review/phase-5-0-p5-r5-rp11-fresh-independent-rebuild-assignment-r3.md`

Do not execute any R-5 command and do not access `oracle-test`.

## Required inputs

Read the canonical instructions and current-state documents, then read:

- the accepted predecessor assignment;
- Gemini's closed HARD STOP handback;
- Codex's independent HARD STOP review;
- Peter's acceptance and cleanup authority; and
- the cleanup result.

Do not read or reuse any disposable artifacts from Gemini's stopped run.

## Required amendments

Preserve the accepted procedure, pinned inputs, comparisons, ordering,
single-invocation limits and terminal-state rules except for these explicit
changes:

1. Allocate all outer-host run resources under `/var/tmp/<RUN>-*`, including
   checkout, index, package cache, provisioned root, work, evidence and pytest
   paths. Do not perform a blind global substitution: references to the
   sandboxed build root's own `/tmp` and `/var/tmp` must retain their original
   meaning.
2. Change the fresh-prefix absence check to inspect `oracle-test:/var/tmp` and
   record `df`, filesystem type, mount options, available bytes and inodes for
   `/var/tmp` before creation. A missing directory, unexpected link/non-directory,
   or less than 4 GiB available is a HARD STOP. The 4 GiB threshold is a
   preflight floor, not permission to consume that amount deliberately.
3. Make every creation, synchronization, build, evidence, accounting,
   retention and cleanup-state statement consistently name `/var/tmp` for the
   outer-host run resources.
4. Close `FRESH-R5-HS-1` prospectively: Step 1 must print the complete actual
   stdout of `git status --short --untracked-files=all` before printing and
   gating its derived repository-state result. The handback must reproduce
   that output. Do not edit the closed predecessor handback.
5. Use a new run identifier and a new final handback path:
   `docs/review/phase-5-0-p5-r5-rp11-fresh-independent-rebuild-r3-handback.md`.
   The run remains wholly fresh and may not resume or reuse the stopped run.
6. Preserve the rule that no remediation, retry, cleanup, package change,
   privilege escalation, service/database action, secret access, commit or
   push is authorized. At PASS, INVALID RUN or HARD STOP Gemini must write the
   complete handback and closing record and stop.
7. Include this resolved invocation in the assignment and your handback:

```text
/goal Execute the active assignment in docs/review/phase-5-0-p5-r5-rp11-fresh-independent-rebuild-assignment-r3.md. Proceed autonomously through every authorized step in order until the defined terminal state (PASS, INVALID RUN, or HARD STOP). Do not post intermediate progress updates, do not yield turns for user confirmation on background tasks, and do not stop until the final handback and closing record are fully written.
```

## Verification and handback

Mechanically audit every command and prose reference affected by the location
change. Verify that no outer-host run output remains directed to `/tmp`, while
the build root's internal `/tmp` and `/var/tmp` checks remain intact. Report
the proposed assignment's SHA-256 and byte length, files changed, checks run,
checks not run and unresolved issues. Stop after writing the proposal and
handback; it is not active until Codex independently reviews it and Peter's
acceptance/activation is recorded.
