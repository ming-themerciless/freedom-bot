# Claude implementation prompt — Package 5.0 evidence harness, pre-execution stage

Work in `/opt/freedom-blades/platform`.

## Authority and outcome

Peter Duscha approved the bounded Package 5.0 pre-implementation evidence
harness on 2026-09-02. Implement the minimum synthetic/disposable harness and
prepare its exact privileged execution plan for Codex review.

**This prompt authorizes implementation of evidence scaffolding only. It does
not authorize privileged execution yet.** Stop after producing the tested
harness, exact command/run plan, cleanup plan and handback. Codex must approve
those concrete artifacts before any `sudo`, identity creation, PostgreSQL
configuration change, `systemd-run`, `chattr`, capability construction or
other mutation-bearing evidence step is run.

Package 5.0 remains `not ready`. Do not implement migration `0014`, production
application behavior, production schema, deployment, authority transition,
cutover, OD-62, or Package 5.1+.

Claude is the implementer and working Technical Lead. Codex is the Security
Reviewer and Independent Reviewer. Peter Duscha is Operations Owner and
Acceptance Authority.

## Required reading

Read completely, in this order, before planning or editing:

1. `.agents/AGENTS.md`;
2. `docs/implementation-plan.md`;
3. `docs/project-management/README.md`;
4. `docs/project-management/status.md`;
5. `docs/review/Handover information`;
6. `docs/review/phase-5-0-evidence-harness-authorization-draft.md`;
7. `docs/review/phase-5-0-read-only-evidence-preflight.md`;
8. `docs/review/phase-5-0-gemini-operational-evidence-runbook.md`;
9. `docs/review/phase-5-0-package-plan.md`, especially §§2.10–2.13, 6, 8 and 9;
10. `docs/review/phase-5-0-logical-schema.md`, especially the authority,
    journal, grants and evidence sections;
11. `docs/review/phase-5-0-security-rereview-revision-12.md`;
12. `docs/project-management/raid-register.md`, focusing on P5.0-R4/R5,
    A-5.0-3/4/5 and R-5.0-12 through R-5.0-16; and
13. `docs/discovery/open-decisions.md`, OD-62 through OD-66.

Check `git status` first. The tree is intentionally dirty and contains work
belonging to the maintainer and other agents. Do not reset, revert, overwrite,
stage, commit or reformat unrelated work.

If any controlling documents conflict after the 2026-09-02 current-state
overrides, stop and report the exact conflict. Historical sections explicitly
marked superseded are history, not current authority.

## Preflight facts to preserve

- The current non-elevated session is `foundry`, has an empty capability
  bounding set and `no-new-privs=1`.
- `/etc/sudoers.d`, `pg_hba.conf` and `pg_ident.conf` were unreadable without
  elevation. Do not attempt to bypass those permissions in this stage.
- `/var/lib` is read-only in the current sandbox view.
- `freedomcoord`, `freedomsheet`, `fbprobe` and `freedomjournal` do not exist.
- The proposed coordinator, journal and provenance paths do not exist.
- The live bot unit lacks the four OD-65 hardening properties. Do not modify or
  restart it.
- A-5.0-3 means a disposable Google Sheet and service account for WP-13. It is
  not a prerequisite for C-3/C-4 and remains separately unconfirmed.
- A-5.0-4 is the disposable OS identity/HBA environment. A-5.0-5 is the
  filesystem, capability, sandbox and journal evidence environment.

## Required deliverable: minimum evidence harness

Implement only reusable, synthetic probes required to produce objective
evidence for:

- C-1 capture and validation of `sudoers` file metadata/content supplied by an
  authorized reader;
- pre-change and post-change `pg_hba.conf`/`pg_ident.conf` ordering analysis;
- the OD-64 peer-authentication positive/negative identity matrix;
- C-3 `FS_APPEND_FL` positive control and `O_TRUNC` refusal attribution;
- C-4/JNL-52 canonical identity, group and filesystem-access checks;
- JNL-49/JNL-50 E1–E8 capability-mask, securebit, positive-control and exact
  `errno` evidence;
- JNL-46 manifest-function equivalence;
- JNL-51 reviewed-source provenance, especially missing-provenance refusal;
- JNL-53 W11a deployed-source/provenance self-check;
- journal creation, sealing, generation registration, missing/corrupt/reset/
  stale/cross-generation refusal and recovery evidence needed for P5.0-R5; and
- deterministic cleanup/residue reporting.

Keep the harness isolated from product modules. Prefer a dedicated
`tools/phase_5_0_evidence/` package and focused tests under
`tests/phase_5_0_evidence/`, unless an existing test-only location clearly owns
the behavior. It may model the proposed schema with a disposable synthetic
facsimile, but must not create or invoke migration `0014`.

The harness must:

- default to dry-run or refusal when the target is not explicitly marked
  disposable;
- require explicit absolute target paths and database names;
- reject `/`, `/opt/freedom-blades/platform`, `/var/lib`, production database
  names and unresolved environment variables as mutation targets;
- never read or print secrets, environment-file contents, private keys,
  credentials, tokens, player data or unrelated host configuration;
- use structured evidence records with case ID, target identity, preconditions,
  observed UID/GID/groups, complete capability masks, securebits, operation,
  exact result/`errno`, cleanup state and pass/fail/inconclusive status;
- classify a failed positive control or identity mismatch as `inconclusive` or
  failed, never passed;
- make cleanup explicit, bounded and idempotent; never recursively delete a
  broad or unresolved path;
- refuse to run mutation-bearing cases unless a generated plan names the
  disposable target and every intended mutation;
- emit no claim that P5.0-R4/R5 or an assumption is closed; and
- make no network call.

Use deterministic inputs and synthetic fixtures. Do not use shell-string
construction for privileged commands where an argument-vector representation
can be emitted and reviewed. Do not execute generated privileged commands in
this stage.

## Exact execution-plan artifact

Create `docs/review/phase-5-0-evidence-harness-execution-plan.md` containing:

- the named proposed disposable host/context, filesystem path and PostgreSQL
  instance; if no suitable target is currently available, mark it `UNASSIGNED`
  and stop before execution;
- every command as an argument vector or exact shell command, grouped by
  identity and evidence case;
- why each command is within the approved authorization;
- before-state capture, expected safe result, expected refusal and stop result;
- all temporary accounts, groups, files, paths, roles, databases, HBA/identity
  lines and transient units it would create;
- exact cleanup in reverse dependency order;
- the evidence artifact produced by each command;
- confirmation that no production service, credential, data or external system
  is touched; and
- a clear **NOT EXECUTED — CODEX PRE-EXECUTION REVIEW REQUIRED** banner.

Do not invent a disposable target. `UNASSIGNED` is the correct result when the
maintainer has not named one.

## Tests required before handback

Add and run unprivileged automated tests covering at least:

- target allowlist/refusal, including every broad/path/database guard;
- dry-run behavior and absence of subprocess execution;
- safe argument handling for paths, identities and case IDs;
- exact evidence schema and deterministic serialization;
- positive-control failure classification;
- unexpected `errno`, capability mask, securebit, UID/GID or group handling;
- partial-step failure and cleanup-plan generation;
- idempotent cleanup planning with no broad deletion;
- HBA/identity-map parser ordering, wildcard and broad-rule detection;
- `sudoers` validation for wildcards, `NOPASSWD`, executable path and
  `log_output` without logging unrelated file contents;
- provenance-present, provenance-missing, mismatch and unaccounted-file cases;
- malformed/corrupt/stale/cross-generation journal evidence; and
- proof that no test contacts PostgreSQL, systemd, Google, Discord, Foundry or
  the network and no test needs root.

Run the focused harness suite and applicable repository static checks. Do not
run privileged cases merely to increase test coverage. Report exact commands,
passes, skips and checks not configured.

## Forbidden in this stage

Do not run `sudo`, `su`, `systemd-run`, `chattr`, `setcap`, `setpriv`, capability-
bearing `capsh`, `useradd`, `groupadd`, `usermod`, `install` outside the
workspace, `chmod`/`chown` outside the workspace, PostgreSQL DDL/DML, config
reloads, service changes, network calls or destructive cleanup. Do not read
`/etc/sudoers.d` or PostgreSQL configuration through elevated or alternative
identities. Do not request production credentials.

Do not change controlled roadmap, decision, RAID, status or change-log records.
If implementation reveals a governance change, stop and report it rather than
editing the approved decision.

## Stop conditions

Stop and hand back without privileged execution if:

- a representative disposable target cannot be named;
- the evidence requires product code or migration `0014` rather than a minimal
  synthetic probe;
- a command cannot be bounded to an explicit disposable target;
- cleanup cannot be proved narrow and reversible;
- the package-plan evidence contract is internally inconsistent;
- a positive and negative case cannot isolate one intended control;
- a proposed command could expose a secret or unrelated host data; or
- any required action falls outside the approved authorization.

## Handback

Create `docs/review/phase-5-0-evidence-harness-implementation-handback.md` with:

- scope and authority;
- files changed and why;
- architecture of the isolated harness;
- requirement/evidence-case traceability;
- target safety and cleanup guarantees;
- exact tests and results;
- all skipped/blocked evidence;
- every discrepancy found in the package plan, schema or runbook;
- secrets, privacy, external-state and unrelated-diff review;
- the execution-plan path and its `NOT EXECUTED` state;
- explicit confirmation that no privileged or mutation-bearing evidence command
  ran; and
- a request for Codex pre-execution review.

Then stop. Do not execute the plan until Codex returns an explicit approval for
the exact target, commands and cleanup.
