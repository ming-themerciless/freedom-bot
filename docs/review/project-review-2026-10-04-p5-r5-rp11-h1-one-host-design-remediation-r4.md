# Independent re-review — `oracle-test` one-host H-1 design remediation R4

Date: 2026-10-04

Reviewer: Codex

Design author: Claude

Work ID: `C-P5.0-R5-RP11-H1-D3-R4`

Reviewed return: [D3-R4 remediation and handback](phase-5-0-p5-r5-rp11-h1-oracle-test-one-host-design-amendment-proposal.md#15-d3-r4-remediation-and-handback-d3-r4-2026-10-04).

## Outcome

Claude's **DESIGN REMEDIATION READY FOR RE-REVIEW** return is structurally
complete, but I find one Blocking defect, `OH-H1-D3-R4-1`. The proposal does
not yet establish its claimed one-shot start boundary after every failed
consume attempt.

`OH-H1-D3-R2-1`, `OH-H1-D3-R1-1` and `OH-H1-D3-2` remain open. Nothing in
this review accepts or activates H-1.

## Finding

### `OH-H1-D3-R4-1` — Blocking — early CP failures do not create the one-shot barrier

The proposal says that CP is one-shot and that, after any CP failure, a second
start finds CP-3's consume-evidence directory and refuses. That is not true for
failures before CP-4:

* CP-0 can fail before the activation lock is acquired;
* CP-1 can return `consume-busy`; and
* CP-2 can return `consume-precondition`.

None of those paths creates `/var/tmp/⟨activation_id⟩-consume-evidence/`.
CP-3 only checks whether that name already exists; CP-4 creates it. A later
`start` in the same activation can therefore pass CP-3 and, if the earlier
condition was transient or the first failure raced cleanup, proceed through
CP-7 and run `ExecStart=`.

This contradicts all of the following D3-R4 claims:

* §4.2.5-R4 (c), CP-3: “A second start of this activation ... never runs the
  pass”;
* §4.2.5-R4 (d), the CP-failure row: “A second start finds CP-3's directory
  and refuses”;
* §4.2.5-R4 (i), proof item 7: “CP-3 prevents any later start of this
  activation from running the pass”;
* §4.2.5-R4 (k), CX-2: “No pass has run, and none can run in this activation”; and
* the R4 prompt's requirement that the consume step be one-shot and serialized
  with cleanup.

The defect is Blocking because the proposal relies on the false claim for its
activation authorization and lifetime state machine. It also leaves an
unanalysed race between HL/CL reacting to the first failed start and a repeated
start entering CP. The grant-removal-before-`ExecStart=` argument still holds
for a later successful CP, but that narrower property does not satisfy the
complete accepted one-pass/one-activation contract.

## Required remediation

Revise the design so that every start attempt which enters CP durably and
atomically consumes the activation's single attempt before any fallible
precondition can return, while remaining serialized with CL. The revised
procedure must specify crash recovery and cleanup classification for every
boundary around that consumption, and must reconcile the terminal-cause table,
states, proof, residuals, tests and successor drill. Alternatively, explicitly
return for a maintainer decision if meeting that contract requires changing
the accepted OH-D-10 design rather than refining it.

## Review notes

The requested OH-D-10 changes are otherwise represented consistently: the
rule grants `start` only; the fixed privileged `ExecStartPre=` consumes and
PK-verifies the grant before `ExecStart=`; route (iii-a) is the executor's
A-2-authorized root stop; polling is not used as a grant boundary; GP-R3,
ST-1.ur, boot clearing, automatic cleanup and separately authorized RB-1 are
retained; and PO-21 (n) through (r) plus PO-11 (g) remain proposed fail-closed
obligations rather than host facts.

## Checks and authority boundary

I read the canonical current-state documents, the R4 authority and prompt,
the D3-R3 review, and the relevant D3-R4 proposal sections and reconciliations.
I performed repository-local, read-only consistency inspection before writing
this review record. No host, network/Git retrieval, credential, retained-path
inspection, upstream research, implementation, build, installation,
H-0/H-1/H-2, activation, evidence, rollback, cleanup, test-suite, commit or
push action occurred.
