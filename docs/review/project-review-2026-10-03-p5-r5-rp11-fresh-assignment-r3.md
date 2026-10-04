# Independent review — fresh R-5 successor assignment R3

Date: 2026-10-03  
Reviewer: Codex  
Drafting assignee: Claude  
Preparation work ID: `C-P5.0-R5-RP11-FRESH-A2`

Reviewed proposal:
[`phase-5-0-p5-r5-rp11-fresh-independent-rebuild-assignment-r3.md`](phase-5-0-p5-r5-rp11-fresh-independent-rebuild-assignment-r3.md)  
SHA-256: `9959d93da7fafb194f942657a3851e83652dc8e1b9ec332b0fa5abd7abb72909`  
Length: `109644` bytes

Preparation handback:
[`phase-5-0-p5-r5-rp11-fresh-independent-rebuild-assignment-r3-handback.md`](phase-5-0-p5-r5-rp11-fresh-independent-rebuild-assignment-r3-handback.md)

## Disposition

**No Blocking, Important or Optional finding.** The R3 proposal satisfies the
preparation task and is suitable for maintainer acceptance and one-run Gemini
activation without remediation.

This review does not activate the assignment and does not authorize host
access. R-5 remains Blocking and unaccepted; RP-11 remains unwired and unmet;
`plan.is_executable=False`; PO-9 and PO-14 remain open; and Package 5.0 remains
not ready.

## Review of the reported open items

Claude's seven notes do not represent seven unresolved blocking decisions.
Their dispositions are:

1. **S1.3 completeness strength — recommend accept as written.** A handback
   that omits or changes required transcript lines lacks the evidence needed
   to establish the run. Treating that as a HARD STOP is proportionate and
   directly prevents recurrence of `FRESH-R5-HS-1`.
2. **Python wrapper — accepted technically.** It invokes Git once, emits Git's
   stdout byte-for-byte, derives count and digest from those same captured
   bytes, propagates Git's status and records stderr. This satisfies the
   requirement for complete actual stdout more reliably than two observations
   of a changing worktree.
3. **Separate S1.4 gate — accepted technically.** S1.3 records the complete
   repository status; S1.4 retains the accepted, mechanically enforced gate
   over the controlled paths. Calling S1.4 “derived repository state” does not
   claim that it is computed from S1.3 bytes.
4. **Per-user quota residual — accepted as disclosed.** The preflight measures
   unprivileged `f_bavail`, requires 4 GiB, records mount options and makes any
   subsequent quota or capacity write failure a HARD STOP. No privilege or
   package change is justified merely to obtain an additional quota report.
5. **AppArmor — no new decision.** The proposal preserves the accepted
   fail-closed behavior: record the setting, then HARD STOP if bubblewrap
   cannot enter. It grants no repair authority.
6. **`/var/tmp` retention — accepted technically.** The handback remains the
   evidence of record, the executor promises no retention period, and cleanup
   remains separately controlled.
7. **Identifiers — maintainer confirmation required at activation.** Codex
   recommends confirming the proposed execution work ID
   `C-P5.0-R5-RP11-FRESH-R5-R3` and handback path
   `docs/review/phase-5-0-p5-r5-rp11-fresh-independent-rebuild-r3-handback.md`.

Consequently the maintainer decision is compact: accept the assignment as
written, including the strict S1.3 evidence rule, confirm the proposed
identifiers, and activate Gemini for exactly one run—or reject/amend it. No
technical remediation is recommended first.

## Independent checks

- Recomputed proposal identity: SHA-256 and byte length match Claude's
  handback.
- Reviewed the proposal against the accepted predecessor and the seven
  required amendments in the preparation task.
- Confirmed outer-host run resources use `/var/tmp/<RUN>-*`; remaining `/tmp`
  references are historical/forbidden context or the sandboxed build root's
  internal paths.
- Reviewed S2.18a–S2.18d: directory identity, filesystem/type output, inode
  output, longest-prefix mount selection and unprivileged available-byte
  threshold are fail-closed before creation.
- Reviewed S1.3: one Git invocation, byte-preserving stdout, same-observation
  line count and digest, status propagation, and explicit handback
  reconstruction requirement.
- Confirmed the resolved Gemini `/goal` appears once and names the R3
  assignment.
- Confirmed the new handback path is used by the handback contract and closing
  block substitution rules.
- Confirmed relative Markdown links resolve.
- `git diff --check`: pass.

No R-5 block, remote command, provisioning, build or test suite was run. No
`oracle-test` access is authorized or performed by this review.

## Recommended acceptance and activation

Peter Duscha may now record all of the following in one decision:

- accept the R3 proposal at the digest and length above;
- accept the strict S1.3 evidence rule;
- confirm work ID `C-P5.0-R5-RP11-FRESH-R5-R3`;
- confirm handback path
  `docs/review/phase-5-0-p5-r5-rp11-fresh-independent-rebuild-r3-handback.md`;
- name Gemini as the independent executor for exactly one run; and
- replace the no-access banner only with the assignment's exact bounded
  authority until PASS, INVALID RUN or HARD STOP and completed handback.

The resolved invocation is:

```text
/goal Execute the active assignment in docs/review/phase-5-0-p5-r5-rp11-fresh-independent-rebuild-assignment-r3.md. Proceed autonomously through every authorized step in order until the defined terminal state (PASS, INVALID RUN, or HARD STOP). Do not post intermediate progress updates, do not yield turns for user confirmation on background tasks, and do not stop until the final handback and closing record are fully written.
```
