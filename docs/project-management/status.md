# Project status

This file is the current operational status entry point. Historical status
updates through 2026-09-24 are preserved verbatim in
[`status-through-2026-09-24.md`](status-through-2026-09-24.md).
The decision register, RAID register, change log and dedicated review records
remain the authoritative durable records for their respective subjects.

## Current status — RP-11 repository implementation assigned — 2026-09-27

Peter Duscha has decided P5.0-R5 MD-1 through MD-6. In particular, he accepts
`R-5.0-13` without requiring JNL-40(b)'s second-host or
`/etc/machine-id`-rewrite case for P5.0-R5 closure. The residual and its
external-evidence controls remain active.

P5.0-R5 remains **Blocking**. OD-62 G-A remains a conditional direction rather
than a binding ruling. `plan.is_executable=False`, Package 5.0 remains not
ready, and no implementation, migration, host, database, reboot, deployment or
production authority has been granted.

**R5 accepted, 2026-09-27.** Codex independently reviewed the exact
R5-amended draft and reported no findings. Peter Duscha accepted that review
and C-P5.0-R5-OP1-R5; **OP1-R4-1 is Closed, remediated**. This accepts the
requirements correction only. RP-11 remains absent and unmet, neither pass is
accepted or authorized, and no operational authority is created.
[Codex R5 review](../review/project-review-2026-09-27-p5-r5-operational-evidence-prompt-r5.md);
[maintainer acceptance](../review/project-review-2026-09-27-p5-r5-operational-evidence-prompt-r5-acceptance.md).

**RP-11 implementation assigned, 2026-09-27.** Peter Duscha assigned
C-P5.0-R5-RP11-I1: a bounded repository implementation of the crash-consistent
client-side capture mechanism and read-only B0-RA retention verification, with
focused local tests and an implementation handback for independent Codex
review. The assignment creates no host or operational authority and does not
mark RP-11 satisfied.
[Claude prompt](../review/phase-5-0-p5-r5-rp11-capture-mechanism-implementation-claude-prompt.md).

Codex's [R4 review](../review/project-review-2026-09-27-p5-r5-operational-evidence-prompt-r4.md)
confirmed that R4 resolves retention verification for the root, final index,
chain, admitted records and bound streams, then found one Blocking gap: B0-RA
does not detect deletion of an unadmitted file named by Pass A's final state.
The bounded repository-only
[R5 assignment](../review/phase-5-0-p5-r5-operational-evidence-prompt-r5-unadmitted-retention-remediation-claude-prompt.md)
was performed. It authorized documentation edits only and created no host or
operational authority.

**R5 returned for Codex review, 2026-09-27.** Claude completed
C-P5.0-R5-OP1-R5 repository-only. The
[R5-amended draft](../review/phase-5-0-p5-r5-operational-evidence-authorization-prompt.md)
(SHA-256 `5e06a38811462613244ee258524461eb23b5598862ce43efa3ec77365040acb3`)
adds B0-RA condition 5. One complete recursive enumeration of Pass A's
retained root must agree in both directions with the names Pass A's final state
accounts for, each at its exact relative name and expected object type. An
absent unadmitted file therefore stops Pass B, as does an unexpected name, a
type mismatch, a duplicate or ambiguous name, a path alias, an escape from the
root or an incomplete comparison. Each such stop is fail-closed before B0-08,
so no `MI.capture_root_B` is created and no Pass B host command is issued. The
final state now records unadmitted files and mechanism-created subdirectories
by relative name and type. For unadmitted files the check verifies presence,
name and type only, never unchanged content. It is requirements-only: RP-11
remains absent and unmet. Neither pass is executable or authorized, and no
host action occurred.
[R5 handback](../review/phase-5-0-p5-r5-operational-evidence-prompt-r5-unadmitted-retention-remediation-handback.md).

Codex's [R3 review](../review/project-review-2026-09-27-p5-r5-operational-evidence-prompt-r3.md)
confirmed that R3 resolved the distinct-root and ordered-stop defects in
substance, then found one Blocking evidence-integrity defect: Pass B can be
admitted without verifying that Pass A's required retained root and final
index still exist and match the Pass A handback. The bounded repository-only
[R4 assignment](../review/phase-5-0-p5-r5-operational-evidence-prompt-r4-retention-verification-remediation-claude-prompt.md)
was performed. It authorized documentation edits only and created no host or
operational authority.

**R4 returned for Codex review, 2026-09-27.** Claude completed
C-P5.0-R5-OP1-R4 repository-only. The
[R4-amended draft](../review/phase-5-0-p5-r5-operational-evidence-authorization-prompt.md)
(SHA-256 `20fa2ce07b391d430569df0e513d687859a1032cfc37bc4c6c0e4dda883b486b`)
adds a new Pass B admission step, **B0-RA**, that runs before B0-08. It is a
reviewed, non-mutating check. It binds `MI.capture_root_A`, the final index
state's name and the capture index SHA-256 to a digest-pinned Pass A handback
(new input `MI.pass_a_handback`). It also re-derives the final state's digest
and re-applies X-4 to Pass A's retained chain, records and bound stream files.
Every retained name must be accounted for by Pass A's final state. Absence,
mismatch, invalidity or inability to check is a fail-closed B0 stop: no
`MI.capture_root_B` is created and no Pass B host command is issued. Pass A's
root stays retained, unmodified and never used as Pass B evidence. The check
establishes retention at that moment only. It is requirements-only, and RP-11
remains absent and unmet. Neither pass is executable or authorized, and no
host action occurred.
[R4 handback](../review/phase-5-0-p5-r5-operational-evidence-prompt-r4-retention-verification-remediation-handback.md).

Codex independently reviewed the exact returned draft and issued
[changes requested](../review/project-review-2026-09-27-p5-r5-operational-evidence-prompt.md).
Neither Pass A nor Pass B is authorized. The review found three Blocking
defects:

- RP-1 makes Pass A observations the source of E7 expectations, contrary to
  the reviewed harness contract;
- reconciliation row 40's `fsync` failure-injection feasibility work is
  improperly deferred; and
- the per-act separate stdout/stderr digest contract has no executable capture
  method.

**Returned for Codex re-review, 2026-09-27.** Claude completed the
repository-only remediation under
[C-P5.0-R5-OP1-R1](../review/phase-5-0-p5-r5-operational-evidence-prompt-remediation-claude-prompt.md).
It amended the
[authorization draft](../review/phase-5-0-p5-r5-operational-evidence-authorization-prompt.md)
in place and returned a
[remediation handback](../review/phase-5-0-p5-r5-operational-evidence-prompt-remediation-handback.md).
The draft remains unaccepted and unauthorized, and **neither pass is
executable as amended**:

- RP-1's E7 and interpreter expectations must be owner-stated and
  independently verified. Pass A observations are corroborative only. The
  missing provenance and verification method is new blocker RP-10.
- Row 40's `fsync` injection is P5.0-R5 feasibility work, blocked by new
  RP-12.
- Every host command needs new RP-11, a reviewed client-side capture
  mechanism. None exists.
- MD-5 stays unmet until an independent acceptance record exists.

Codex completed that independent
[R1 re-review](../review/project-review-2026-09-27-p5-r5-operational-evidence-prompt-r1.md).
It confirmed that the three original findings are resolved in substance and
requested one further change, **OP1-R1-1**: RP-11 does not yet require durable
publication of the captured stream files, per-act record directory entries or
the pass-level capture index.

**Returned for Codex review, 2026-09-27.** Claude completed the
repository-only
[C-P5.0-R5-OP1-R2 assignment](../review/phase-5-0-p5-r5-operational-evidence-prompt-r2-durability-remediation-claude-prompt.md).
It amended the
[authorization draft](../review/phase-5-0-p5-r5-operational-evidence-authorization-prompt.md)
in place (SHA-256 `308e788c…`) and returned an
[R2 durability-remediation handback](../review/phase-5-0-p5-r5-operational-evidence-prompt-r2-durability-remediation-handback.md).

RP-11's requirements now make three things crash-consistent, and any failed
barrier is an `inconclusive` stop that is never retried or repaired:

- **Stream files.** Both are completed, closed and file-synchronized, with
  durable directory entries, before a record publishes their digests.
- **Per-act records.** Each is written under a temporary name,
  file-synchronized, published by a non-replacing atomic rename and followed
  by a containing-directory synchronization.
- **The capture index.** It is a chain of immutable index states with one
  defined finalization point.

RP-11 remains absent and unmet, the draft remains unaccepted and
unauthorized, and neither pass is executable. Codex's
[R2 review](../review/project-review-2026-09-27-p5-r5-operational-evidence-prompt-r2.md)
confirmed that the original durability omission is resolved in substance but
requested two Blocking corrections: distinct retained capture roots for Pass A
and Pass B, and one consistent ordering between stop, X-3 finalization and the
capture root becoming read-only. The bounded repository-only
[R3 assignment](../review/phase-5-0-p5-r5-operational-evidence-prompt-r3-contract-consistency-remediation-claude-prompt.md)
is now active. Claude must amend documentation only, return the named R3
handback and stop for another independent review. No action on `oracle-test`
occurred or is authorized.

**Returned for Codex review, 2026-09-27.** Claude completed the
repository-only R3 assignment. It amended the
[authorization draft](../review/phase-5-0-p5-r5-operational-evidence-authorization-prompt.md)
in place (SHA-256 `026edf43…`) and returned an
[R3 contract-consistency handback](../review/phase-5-0-p5-r5-operational-evidence-prompt-r3-contract-consistency-remediation-handback.md):

- **Distinct capture roots.** Pass A uses only `MI.capture_root_A` and Pass B
  only `MI.capture_root_B`. The two are distinct, and each has its own
  exclusive creation, genesis state, index chain and final state. Pass A's
  root stays retained, unmodified and unused while Pass B is admitted and run.
- **One stop transition.** Commands stop at once. Where possible, one X-3
  finalization attempt is the only later write. The capture root is then
  read-only, whether the attempt succeeds or fails. After an interruption no
  attempt is made, and nothing is retried or reconstructed.

RP-11 remains absent and unmet, the draft remains unaccepted and
unauthorized, and neither pass is executable. Codex's independent review of
the exact R3-amended bytes is next.

The controlling assignment and restrictions are in
[`../review/Handover information`](../review/Handover%20information).

**Historical update, 2026-09-24 — original draft returned.** Claude drafted
[C-P5.0-R5-OP1](../review/phase-5-0-p5-r5-operational-evidence-authorization-prompt.md)
repository-only and returned it with a
[drafting handback](../review/phase-5-0-p5-r5-operational-evidence-prompt-drafting-handback.md).
The draft authorizes nothing. Codex's 2026-09-27 review supersedes the drafting
handback's proposal that Pass A is structurally admissible. Pass B remains
inadmissible until its prerequisites are met and an amended draft is
independently accepted. No host action occurred.

## Current decision state

- **MD-1:** independently reviewed harness-facsimile feasibility evidence may
  close P5.0-R5; production-code evidence remains mandatory at the later
  implementation/release gate.
- **MD-2:** `oracle-test` supplies the target-specific feasibility host facts;
  development-host observations are historical context only.
- **MD-3:** the supervised reboot durability case is mandatory for feasibility
  closure and cannot be replaced by a Not Run result or accepted residual.
- **MD-4:** `R-5.0-10` through `R-5.0-16` are accepted on their recorded terms;
  the required recovery rehearsals remain mandatory.
- **MD-5:** the classifier contradictions must be corrected and independently
  reviewed before any evidence band is executable.
- **MD-6:** JNL-40(b) is not required for P5.0-R5 closure; `R-5.0-13` remains
  active with external-evidence controls.

## Next gate sequence

1. Claude performs C-P5.0-R5-OP1-R5 repository-only unadmitted-retention
   remediation (returned 2026-09-27).
2. Codex independently reviews the exact R5-amended prompt (accepted with no
   findings 2026-09-27).
3. Peter Duscha accepts the requirements remediation (completed 2026-09-27).
4. Claude performs C-P5.0-R5-RP11-I1 repository-only and returns its
   implementation handback.
5. Codex independently reviews the exact RP-11 implementation and evidence.
6. After every prerequisite is satisfied and independently reviewed, Peter
   Duscha decides whether to accept and authorize an exact operational pass.
7. If authorized, the assigned operator performs the bounded pass and returns
   its evidence.
8. Codex independently reviews that evidence.
9. Peter Duscha decides P5.0-R5 closure and, only after its prerequisite is
   satisfied, the binding disposition of OD-62 G-A.

No step authorizes a later step implicitly.

## Historical status

The archived snapshot retains every prior Current, Superseded and Historical
status block exactly as it stood when archived:

- [Status history through 2026-09-24](status-through-2026-09-24.md)

Future historical batches should be moved to dated files beside this file and
indexed in `status-archive/`; this entry point should contain only controlling
current state, the immediate gate sequence and archive links. Keeping snapshots
in this directory preserves the relative-link base of the original text.
