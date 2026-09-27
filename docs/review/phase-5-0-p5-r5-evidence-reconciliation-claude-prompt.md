# Draft Claude prompt — C-P5.0-R5-E1 evidence reconciliation

**Draft only. This document does not assign Claude or authorize work. Peter
Duscha must explicitly accept and assign it. Codex remains the Independent
Reviewer and must not implement this pass.**

## Objective

Perform one bounded, repository-only reconciliation of the evidence relevant to
**P5.0-R5**, the Blocking dispatch-journal durability and integrity finding.
Determine, without closing the finding, exactly which acceptance claims are:

1. supported by accepted operational evidence;
2. supported only by repository implementation or automated tests;
3. specified by design but not implemented;
4. implemented but not operationally verified;
5. contradicted, stale or superseded; or
6. still dependent on a maintainer decision or fresh authorization.

The result must let Codex independently decide whether P5.0-R5 is ready for a
closure review and whether any additional disposable-host evidence is genuinely
necessary.

## Governing context

Before analysing anything, read completely:

1. `.agents/AGENTS.md`;
2. the reading map and §§0, 12 (Package 5.0), 13, 15.1, 16, 17 and 20 of
   `docs/implementation-plan.md`;
3. `docs/review/Handover information`;
4. the restriction banner in `docs/operations/disposable-test-server.md`;
5. `docs/review/phase-5-0-package-plan.md`, especially §§2.10, 2.12, 2.13,
   5.3, 6, 8, 9.2, 9.4 and the `TC-5.0-JNL` evidence catalogue;
6. the current status, RAID, decision and change registers and OD-62 in
   `docs/discovery/open-decisions.md`;
7. the accepted V6/I12 provisioning evidence and its independent reviews;
8. the complete I3 R6–R8 operational and remediation chain, including the R8
   handback, R8-R1 through R8-R6, their independent reviews and dispositions;
9. the current laboratory contract, concrete plan, review manifest, generated
   artifacts, implementation modules and tests relevant to journal storage,
   lifecycle, capabilities, identities, admission, cleanup and controlled
   writes; and
10. the Package 5.0 logical schema and every current P5.0-R5, A-5.0-5,
    D5.0-13/OD-66 and `JNL-*` trace.

Inspect `git status` first. Preserve every unrelated, earlier-pass and
reviewer-authored change. Do not treat an uncommitted file as absent merely
because it is not in `HEAD`.

## Required reconciliation

Build one authoritative matrix with one row for every distinct P5.0-R5
acceptance proposition. At minimum cover:

- durable, block-backed journal storage and exact hierarchy ownership/modes;
- writer inability to create, replace, unlink, rename, rotate or dispose of its
  own evidence;
- `FS_APPEND_FL` capability probing, its positive controls and refusal
  attribution;
- systemd sandbox attribution and the exact S4-0/S4-2 target relationship;
- construction order C0–C13 and every value-consumption invariant;
- deployment-source provenance and unaccounted-file refusal;
- seal, genesis, inode, digest and registered-generation agreement;
- journal hash chain, sequence, startup record and typed refusal conditions;
- missing, empty, corrupt, replaced, unreadable, stale, cross-generation and
  incomplete evidence;
- disk-full, `fsync`, append and outcome-record failure behavior;
- transient-directory cleanup success, cleanup failure, residue reporting and
  next-invocation refusal;
- restart, process-kill, rotation, archive, restore, rollback and reboot
  behavior;
- identity and group-membership evidence for `freedomsheet`, `freedomcoord`,
  `discordbot`, `freedomweb` and `freedomjournal`;
- the E1–E8 capability identities and every required capability combination;
- PostgreSQL generation registration and activation-trigger refusals;
- privileged lifecycle commands and their authorization boundary;
- archive verification, retention and disposal control N5.0-23;
- the full `TC-5.0-JNL`/`JNL-*` catalogue, including C-1, C-3 and C-4;
- every component of A-5.0-5; and
- the exact relationship between I3's accepted R8 controlled-write evidence
  and the broader P5.0-R5 finding.

For each row record:

- stable requirement/test identifier and exact source citation;
- the proposition in falsifiable terms;
- required evidence type: design review, repository test, PostgreSQL test,
  disposable-host observation, controlled mutation, reboot, or maintainer
  decision;
- implementation location, if any;
- test location and exact case, if any;
- evidence artifact and independent disposition, if any;
- current state: `accepted`, `implemented_not_verified`, `test_only`,
  `design_only`, `missing`, `contradicted`, `decision_pending`, or
  `not_applicable`;
- whether V6/I12/I3/R8 actually supports it, with the measured scope stated
  narrowly;
- the smallest remaining action needed; and
- whether that action requires new host authority.

Do not infer that one passing syscall experiment proves the entire journal
lifecycle. Do not count source code, a generated vector, a test definition or a
prior suite count as operational evidence. Do not count R6 as gate evidence;
Peter retained it as historical evidence only. R8 is accepted for I3 at its
measured scope, not automatically for P5.0-R5 in full.

## Required conclusions

Return a dated reconciliation handback containing:

1. an executive conclusion: `ready_for_independent_closure_review`,
   `additional_repository_work_required`, or
   `additional_authorized_operational_evidence_required`;
2. the complete matrix and totals by state;
3. a precise disposition of every A-5.0-5 component;
4. a list of every stale or superseded P5.0-R5 claim found in controlled
   documents;
5. the minimum remaining work, grouped into repository-only work, database
   evidence, disposable-host read-only evidence, controlled host mutation,
   reboot evidence and maintainer decisions;
6. a recommendation on whether the supervised reboot may remain Not Run under
   the accepted contract or is required for closure;
7. a statement of what the accepted I3/R8 evidence proves and does not prove;
8. the effect on conditional OD-62 G-A—analysis only; do not make it binding;
9. exact files inspected and any files changed;
10. exact checks run, with pass/fail/skip/warning counts, and checks not run;
11. security, data-authority, rollback and deployment implications; and
12. proposed Codex independent-review focus.

If the evidence is insufficient, do not draft an operational execution prompt.
List the smallest missing facts and stop. Codex will review the reconciliation
before Peter decides whether any new prompt or host authorization is warranted.

## Permitted work

- Read repository files that are not prohibited secrets.
- Perform repository-only textual, structural and static consistency checks.
- Run focused local tests only when they do not access a database, network,
  credential, live service or protected artifact and when their result answers
  a specific matrix row. Keep `TEST_DATABASE_URL` unset.
- Add only the reconciliation handback and the minimum controlled-document
  pointers necessary to return it for review.

## Prohibited work and stop conditions

**No action on `oracle-test` is authorized.** Do not SSH, synchronize, inspect
the host, invoke a verifier or provisioning command, use `sudo`, access a
database, start a service, create an identity or group, change permissions,
touch `/run`, `/var/lib` or `/opt/freedom-blades`, perform a controlled write,
exercise a reboot, or access, inspect, `stat`, modify, move, delete or reuse any
protected `/tmp` artifact.

Do not run a secrets scan or any command expected to engage a secrets guard. If
any guard or tool refuses a call, stop immediately, do not reformulate or retry
it, and report the refusal.

Do not change application source, tests, hooks, manifests, generated artifacts,
migrations, schema, configuration, the Package 5.0 design or any evidence
artifact. Do not implement a missing requirement. Do not regenerate artifacts.
Do not authorize a later pass.

Do not close P5.0-R5, confirm A-5.0-5 beyond accepted evidence, make G-A
binding, close OD-62, change `plan.is_executable=False`, declare Package 5.0
ready, authorize implementation or migration `0014`, approve a digest, or use
`--execute`.

Run `git diff --check` and focused consistency checks. Stop after returning the
handback for Codex independent technical, security and evidence review.
