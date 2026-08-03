# Project status

Status date: 2026-08-02

Baseline: v1.5; accepted by Peter Duscha on 2026-08-02

Overall health: Amber — the management baseline and technical foundations are
accepted, and the Phase 2 mapped-name normalization correction was independently
reviewed and accepted on 2026-08-02. The milestone itself remains incomplete.

## Milestone status

| Milestone | State | Gate | Evidence / next condition |
|---|---|---|---|
| Phase 0 — Discovery and architecture | Accepted | Closed 2026-07-30 | `docs/discovery/phase-0-handoff.md`, `docs/review/phase-0-submission.md` |
| Phase 1 — Database foundation | Accepted | Closed 2026-07-31 | Maintainer acceptance is recorded at the head of `docs/review/phase-1-submission.md` |
| Phase 2 — Import and reconciliation | In remediation — replacement plan **accepted 2026-08-02**; packages R1–R3 released to start, R4 not ready | Deferred | The prior package plan is superseded. The accepted plan is [`../review/phase-2-v1.5-remediation-plan.md`](../review/phase-2-v1.5-remediation-plan.md): I-02 is reduced to snapshot, identity, mapping, `legacy_authority_deferred`, reconciliation, provenance and audit scope. Outstanding: implementation of R1–R4, implementation re-review, the §9.4 windows, supervised real-export rehearsal, restricted-role grant/denial evidence and backup/restore |
| Phase 3 and later | Not ready | Not opened | Phase 2 gate and applicable decisions/dependencies must close first |
| Frontend visual prototype | Status to be recorded by Product Owner | Separate visual gate | May proceed only within §12.1 constraints |

## Current critical path

1. ~~**Draft the replacement Phase 2 remediation plan**~~ — done 2026-08-02:
   [`../review/phase-2-v1.5-remediation-plan.md`](../review/phase-2-v1.5-remediation-plan.md).
2. ~~**Readiness check of that plan**~~ — done 2026-08-02. Independent review of
   the plan was not separately commissioned; the mandatory independent review at
   the §16.4 import/reconciliation checkpoint applies to the **implementation**
   and remains required at step 5.
3. ~~**Acceptance Authority approval**~~ — recorded 2026-08-02, together with
   the OD-42/I-05 ruling and the three delivery rulings in change-log C-2.
4. **Implementation** of the four approved remediation packages. R1–R3 are
   released to start; R4 is blocked until the §9.4 windows are set.
5. **Independent re-review of the implementation**, closing every blocking
   security, identity, atomicity, migration and recovery finding.
6. **Operational evidence**: upgrade/downgrade/upgrade, backup/restore/rerun and
   direct `freedom_runtime_test` denial of `UPDATE`, `DELETE` and `TRUNCATE`
   against the final retained schema.
7. **Maintainer-supervised real-export rehearsal** and the Data Owner
   attestation defined by implementation plan §12 Phase 2.
8. **Close the Phase 2 data-integrity, identity and migration-safety gate.**

Phase 3 is baselined only after that gate, and then only once named owners,
accepted frontend contracts and security-review capacity are available. Steps 4
onward do not start before step 3 is recorded.

## Current decisions and blockers

- Peter Duscha holds the solo-maintainer accountable roles defined in the
  governance record. Package-specific implementing and reviewing agents are
  assigned when each package is prepared.
- No calendar forecast is committed; maintainer availability and package-level
  agent capacity are established during readiness planning.
- OD-16 and OD-17 block Phase 3 planning; OD-39 blocks the affected Phase 5
  economy cutovers. See `decision-register.md`.
- The normalization correction of 2026-08-02 implements the accepted identity
  policy and does not amend the baseline, so it carries no change-log entry.
- **OD-41 closed 2026-08-02:** ADR 0008 was rejected; the controlled baseline
  assigns every Sheet-era field in the migration register to one typed owning
  package and defines legacy comparison as deferred.
- **Restricted-role evidence is no longer blocked on role creation.** The
  temporary role `freedom_runtime_test` exists and can be assumed: it is
  `NOLOGIN`, non-superuser, cannot create roles or databases, cannot replicate
  and cannot bypass RLS, and the owner/test login `foundry` is a member able to
  `SET ROLE freedom_runtime_test`. What remains is **applying the runtime grants
  for the final retained schema and testing denial directly under that role** —
  not creating a role, and not template review alone. The current
  `infra/postgresql/runtime-grants.sql.tmpl` must not be applied as it stands,
  because it still grants the rejected ADR 0008 tables. A-02 is updated
  accordingly.
- **The example exports are available; the rehearsal is not performed.** Two
  maintainer-authorized exports exist outside the repository at
  `/opt/discord-bots/foundry-actor-exports`. None was read during package
  planning. The supervised real-export preview, its reconciliation report and
  the Data Owner attestation remain outstanding maintainer actions. A-03 is
  updated accordingly.
- **I-05 closed 2026-08-02 by OD-42:** display names are not unique identities,
  multiple characters may share one, stable character IDs and external Actor IDs
  provide identity, and any legacy name-based candidate lookup fails closed when
  more than one candidate exists. No unique display-name constraint is added;
  application enforcement is accepted deliberately.
- **Three delivery rulings recorded with the plan acceptance** (change-log C-2):
  `tools/import_sheet_characters.py` reverts to its committed state and is
  dormant with its disposition owned by package 5.1; Codex performs both the
  independent review and a distinct security-focused pass; and the §9.4 windows
  are required before R4 rather than before any work.
- **Outstanding maintainer inputs, all blocking R4 only:** the supervised
  real-export rehearsal window, the post-rehearsal observation period, and the
  preview/apply wall-clock runtime budget for a 500-Actor artifact.
- **D-01 was split** into D-01a (the only register dependency Phase 2 has) and
  D-01b (per-package vocabulary readiness). Future vocabulary readiness no
  longer reads as a Phase 2 blocker.
- No additional people or standing team are required by the baseline.

## Next status update

Update when the Acceptance Authority records a decision on the replacement Phase
2 remediation plan and OD-42, or another critical-path condition changes,
whichever occurs first.
