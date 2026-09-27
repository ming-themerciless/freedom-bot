# Codex independent review — C-P5.0-R5-OP1-R2 operational-evidence prompt

Date: 2026-09-27

Reviewer: Codex, Independent Reviewer

Disposition: **Changes requested — Pass A and Pass B are not authorized**

## Exact reviewed artifacts

- `phase-5-0-p5-r5-operational-evidence-authorization-prompt.md`
  - SHA-256: `308e788cfd4267308f7fc551d53db3a17cdaabebe870d7f4c4b5e2dad7eadc7e`
- `phase-5-0-p5-r5-operational-evidence-prompt-r2-durability-remediation-handback.md`
  - SHA-256: `c191a83cc18d6d922635bbfc965a0dd4b39f5c1593ebfb1af764743401e174c1`

The review compared those exact bytes with the governing agreement, the
implementation-plan controls, the active handover and disposable-host
restriction, the R1 re-review and the R2 remediation assignment. No command
was issued to `oracle-test`.

## Disposition

The R2 correction resolves OP1-R1-1's original durability omissions in
substance. The draft now requires barriers for both completed stream files,
non-replacing atomic publication and a containing-directory barrier for every
per-act record, and a durably created, advanced and finalized immutable index
chain. It remains implementation-neutral and correctly leaves RP-11 absent
and unmet.

Two Blocking internal-consistency defects remain. P5.0-R5 remains
**Blocking**. `plan.is_executable=False` remains controlling; Package 5.0
remains not ready; OD-62 G-A remains conditional. This review creates no
implementation, synchronization, host, database, verifier, evidence-band,
reboot, deployment or production authority.

## Blocking findings

### OP1-R2-1 — one retained capture root cannot admit both passes

Section 4.5 supplies one `MI.capture_root` for every host command in Pass A and
Pass B. C-6 requires that root to be absent before the pass and created
exclusively by the mechanism. Band B0 repeats A0-01 through A0-09, including
A0-08's requirement that the same root not exist. But C-8 requires Pass A's
root and all of its evidence to remain unmodified until post-execution review
and a maintainer disposition; it therefore cannot be removed to admit Pass B.
C-14 also requires one capture index per pass.

Consequently a successful Pass A makes Pass B's B0 admission impossible under
the draft's own requirements. The R2 handback identifies this ambiguity, but
the executable contract does not resolve it.

**Required correction:** make the capture-root input explicitly pass-specific
(or define an equally unambiguous reviewed derivation that yields distinct,
previously absent roots), and reconcile A0-08, B0, C-6, C-12, C-14, the
artifact table and handback template. Pass A's retained root must never be
removed, reused or modified to admit Pass B.

### OP1-R2-2 — finalization is both required and forbidden after a stop

C-10 says the only further act after a capture failure is X-3 finalization.
X-3 requires the mechanism to publish exactly one final state when the pass is
stopped, and §11.2 repeats that requirement unless the mechanism itself was
interrupted. In contrast, §9.5.3 says, without an ordering qualification,
that **after a stop** the capture root is read-only and no file there is
written or moved. Publishing the X-3 final state necessarily writes a
temporary file and renames it under that root.

A future RP-11 implementation cannot obey both rules, and the conflict governs
the final evidence object on capture-failure paths.

**Required correction:** define one precise stop transition. For stops where
the mechanism remains available, make X-3 the sole permitted post-failure
write and make the root read-only after that finalization attempt reaches its
success or failure outcome. Preserve the existing exception for mechanism or
repository-host interruption, the no-retry/no-repair rule, and X-4's rule
that a missing or invalid final state is never reconstructed.

## Confirmed controls

- OP1-R1, OP1-R2 and OP1-R3 remain resolved in substance.
- MD-1 through MD-6, row 40's feasibility classification, the mandatory
  reboot and RR-11/RR-14/RR-16, and JNL-40(b)'s exclusion are preserved.
- RP-11 remains an unmet, independently reviewed implementation prerequisite;
  the draft does not select an API, language or executable command.
- The R2 handback accurately states that no host action, suite, capture trial,
  protected-artifact access, secret scan, commit or push occurred.

## Required next action

Perform a bounded repository-only requirements correction for OP1-R2-1 and
OP1-R2-2, amend the authorization draft, and return a new handback for Codex
review. Only a later explicit maintainer decision may accept or authorize an
operational pass.

## Checks and non-actions

- Re-derived both reviewed-artifact SHA-256 values.
- Read the R2 draft and handback completely and checked the affected admission,
  retention, publication, finalization and stop clauses together.
- Did not run a suite, harness, verifier or database command.
- Did not SSH, synchronize, inspect or otherwise contact `oracle-test`.
- Did not access any protected historical `/tmp` artifact.
- Did not run a secrets scan or alter a guard.
