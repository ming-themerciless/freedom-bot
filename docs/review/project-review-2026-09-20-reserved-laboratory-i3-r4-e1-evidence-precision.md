# Independent review — I3 R4 E1 evidence-precision correction — 2026-09-20

## Recommendation

Acceptance recommended with **no Blocking, Important or Optional finding**.
C-P5.0-LAB-I3-R4-E1 correctly narrows the operational evidence claim without
changing the accepted R4 result: the verifier refused admission with
`target-mismatch` at exit `4`, before a controlled write or verifier-object
creation; the `ubuntu` invocation was not run; and I3 remains unconfirmed and
unperformed.

This recommendation does not accept the correction on Peter Duscha's behalf,
close LAB-I3-TARGET-1, choose a target identity, approve a digest, advance a
gate or authorize host access, deletion of the two `/tmp` evidence artifacts,
an I3 retry, V7, V8, V10, a participant, the evidence harness, a generated
vector, database access or `--execute`.

## Review result

The corrected records consistently distinguish the three relevant scopes:

1. the I3 verifier performed no controlled write and created no verifier
   object;
2. the authorized §3.2 synchronization updated the remote repository worktree;
   and
3. the shell-level evidence-capture wrapper created
   `/tmp/fb-i3-root.out` and `/tmp/fb-i3-root.err` outside canonical `R` and
   the four publication directories.

Calling the two `/tmp` files operator evidence artifacts rather than verifier
residue is accurate. They were created by shell redirection, are outside the
verifier's controlled topology and do not bear on its cleanup contract. Their
continued presence is disclosed and the current restriction forbids deleting
them.

The argv/wrapper correction is also accurate. The verifier argv is the
reviewed invocation, unchanged in arguments; `ssh`, `cd`, timestamps,
redirection, status capture and `cat` form a distinct shell-level wrapper. The
recorded command is 434 characters as claimed, and its quoting preserves the
verifier's exit status for the remote `echo "EXIT=$?"` immediately following
the invocation.

The correction is confined to repository documentation. It leaves the open
target-identity decision, consumed R4 authority, excluded V7, unperformed
V8/V10, `plan.is_executable=False` and Package 5.0's not-ready state intact.
The append-only C-P5.0-LAB-I3-R4-E1 change-log entry is the appropriate way to
correct the historical R4 and R4-H1 summaries without rewriting those entries.

## Disposition of the transfer-count discrepancy

The accepted R4 handback's “52 paths transferred” figure is not independently
reproducible from the recorded output, which contains 54 entries: 45 files and
9 directories. E1 does not present 52 as newly verified evidence: it places an
inline correction note immediately beside the historical figure and records
the reproducible count in the correction handback.

This is **not a review finding**. The count has no bearing on the exact
exclusion policy, byte totals, tree identity, admission refusal or I3 status,
and the discrepancy is neither hidden nor used to support a conclusion. A
future separately authorized clerical correction may replace the historical
figure with 54, but it is not required for acceptance of this evidence-
precision correction.

## Evidence reviewed

- the C-P5.0-LAB-I3-R4-E1 correction handback and the corrected R4 handback;
- the active handover and current runbook restriction;
- implementation-plan §20 and the current status, RAID, decision and change
  records;
- the exact shell command, its quoting and its claimed 434-character length;
- searches for the superseded broad wording in the reconciled current records;
  and
- `git diff --check`, which completed cleanly.

No test suite was run. This correction changes documentation only, cites no
new suite result, and the active restriction forbids `oracle-test` access.
No host action, secret access, source change, artifact regeneration or digest
change was performed during this review.

## Required next action

Peter Duscha may accept or reject this recommendation. Independently of that
clerical decision, LAB-I3-TARGET-1 remains Open and Blocking: Peter must choose
the approved target-identity treatment before any source or artifact change,
fresh independent review and separately authorized operational retry can be
considered.
