# Claude prompt — V6 provisioning remediation — 2026-09-16

Authorization: **C-P5.0-LAB-V6-R1**, one bounded repository-local remediation
of the incomplete provisioning contract exposed by the released V6 survey.

Peter Duscha approves the prerequisite provisioning needed to create
`freedomlab` and the exact directories with reviewed owners and modes. That
approval does **not** waive the independent-review checkpoint and does not make
an unspecified target safe to create. This pass produces the complete,
executable provisioning delta and its evidence for independent Codex technical
and security review. **Do not apply it to `oracle-test` in this pass.**

## Governing context

Before changing anything, read completely:

1. `.agents/AGENTS.md`;
2. the reading map and §§0, 12 (Package 5.0), 13, 14, 16 and 20 of
   `docs/implementation-plan.md`;
3. the active `docs/review/Handover information`;
4. the restriction banner in
   `docs/operations/disposable-test-server.md`;
5. [the accepted D12-R1 and V6 record](project-review-2026-09-16-reserved-laboratory-d12-r1-acceptance-and-v6-preflight.md);
6. runner contract r6, especially §§1.3–1.5, 5.2–5.11, 6.2, 7 and 9;
7. `tools/phase_5_0_evidence/provisioning.py`, its tests and every caller; and
8. the current review manifest and concrete plan, without executing either.

The accepted V6 observation is authoritative input: both future location
families are on the same ext4 root mount; `fs.protected_hardlinks=1`; the
observed SSH process ran as `ubuntu` with no inheritable, permitted, effective
or ambient capabilities; `/opt/freedom-blades/evidence`,
`/var/lib/freedom-blades`, its `laboratory` and `laboratory/runs` children and
`recovery` are absent; and `freedomlab` is absent.

## Defect to remediate

r6 §7 and `provisioning.PROVISIONING_ITEMS` define V1–V5, V7 and V9, but V6
also requires the exact publication directory `/opt/freedom-blades/evidence`.
That path is absent. The contract calls it “root-only [A]” without defining an
owner, group, numeric mode, creation mechanism, persistence/reboot behavior or
provisioning item. Therefore the approved provisioning cannot yet be applied as
one exact, reviewable delta, and V6 cannot confirm every required owner/mode
assumption.

Do not silently interpret “root-only” as a particular mode. Establish the
smallest exact contract consistent with the descriptor and execution model. If
the intended execution identity cannot traverse or create `R` under the chosen
ownership/mode, report the contradiction rather than weakening the boundary.
Do not use the unresolved V10 assumption as evidence.

## Required work

1. Trace who opens D1, under which real/effective/filesystem identity, and who
   creates each per-run `R`. Reconcile that with the root-only parent claim,
   `fs.protected_hardlinks=1`, and the observed absence of `CAP_FOWNER`.
2. Add one explicit provisioning item for `/opt/freedom-blades/evidence`, with
   exact owner, group, numeric mode, creation mechanism, persistence behavior,
   rationale, verification and rollback. Update the count everywhere it is
   stated. Do not broaden access merely to make a test pass.
3. Preserve the accepted definitions of V1, V2, V3, V4, V5 and V9 unless the
   trace proves a contradiction. Peter's approval covers those prerequisite
   objects and the new evidence-root item once independently accepted.
4. Keep **V7 excluded from this provisioning release**. Do not initialize
   `lifecycle.json`: first-use publication reaches `linkat`, and I3 remains
   unconfirmed. Specify the stop condition that leaves an absent lifecycle
   record fail-closed until V7 receives its own release.
5. Provide an idempotent, fail-closed provisioning procedure or repository
   artifact for the approved prerequisite subset. Existing objects with wrong
   type, owner, group, mode, link count or unexpected content must refuse; do
   not repair or replace an unexplained object automatically.
6. Provide a read-only post-provision verification procedure covering exact
   types, owners, groups and modes; group membership; mount/filesystem identity;
   `fs.protected_hardlinks`; and relevant process/file capabilities. This is the
   V6 re-observation. It must create no link and must not claim to close I3.
7. Add public tests for clean creation in a disposable local model/root,
   idempotent re-run, every wrong-object refusal, partial-failure recovery,
   rollback boundaries, and the V7/I3 stop. Tests must not touch real `/run`,
   `/var/lib`, `/etc`, users or groups.
8. Update runner contract r6, provisioning code, tests, RAID/status-facing
   review records and operations instructions consistently. Regenerate covered
   review artifacts only through the non-executing CLI if covered source bytes
   change; prove deterministic regeneration and report the digest as review
   input only.

## Restrictions

This is a **repository-local contract and implementation remediation**, not the
application of provisioning.

- Do not use SSH, synchronize to the target, inspect the target again, invoke
  `sudo`, create users or groups, edit `/etc`, create anything under `/run` or
  `/var/lib`, or run `systemd-tmpfiles`.
- Do not create a hard link or run a controlled write verification.
- Do not initialize `lifecycle.json` or perform V7.
- Do not perform V8 or V10, wire any participant, access a database, execute a
  generated vector, invoke a real boundary/materializer, or use `--execute`.
- Do not choose or implement LAB-X1's execution route.
- Keep `plan.is_executable` false and
  `reservation.REAL_EXECUTION_REFUSAL` unconditional.

C-7, EH-R16-1, LAB-R6, LAB-X1, I3, P5.0-R5 and OD-62 remain Open; Package 5.0
remains not ready. V6 remains performed-but-not-closed until accepted
provisioning is applied and the read-only survey is repeated successfully.

## Evidence and handback

Run narrow affected tests first, then the complete
`tests/phase_5_0_evidence` suite locally with `TEST_DATABASE_URL` unset. Run
configured structural guards, `compileall` and `git diff --check`. Report exact
pass/fail/skip/warning counts and all checks not run.

Return a remediation handback for independent Codex technical and security
review. Include:

- the identity/descriptor trace and resolution of the root-only-parent issue;
- the exact new provisioning item and revised total;
- the complete approved prerequisite subset and explicit V7 exclusion;
- preconditions, refusal behavior, idempotency, rollback and reboot behavior;
- the post-provision V6 verification procedure;
- tests, reversals where appropriate and generated-artifact evidence; and
- an explicit statement that no target mutation occurred.

The implementer closes no finding, marks no V6/I3 fact confirmed, approves no
digest and advances no gate. Stop after the handback.
