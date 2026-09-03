# Gemini handover — Package 5.0 pre-implementation readiness work

Work in `/opt/freedom-blades/platform`.

## Purpose and authority

Claude is temporarily unavailable. Use this time to advance every safe,
documentation- and review-level prerequisite for Package 5.0 that can be
completed without implementing the package or changing external state.

This is a **read-only technical review plus documentation-preparation task**.
Package 5.0 remains `not ready`. This prompt does **not** authorize production
code, migration `0014`, database objects, host accounts or groups, filesystem
objects or permissions, `sudoers`, PostgreSQL configuration, credentials,
services, deployment, cutover, Package 5.1+, or any mutation of Discord,
Google Sheets, Foundry, PostgreSQL, or the host environment.

Codex remains the named Package 5.0 Security Reviewer, Independent Reviewer and
logical-schema reviewer. You are assisting those reviews as an adversarial
readiness analyst. You may identify and classify findings and recommend a
disposition, but you may not close P5.0-SR1/P5.0-SR2, issue the official
security-readiness recommendation, approve a decision, accept a residual risk,
confirm an operational assumption, or approve the package gate. Those actions
remain with the roles named in the controlled documents.

## Required reading before planning or changing a document

Read these files completely, in this order:

1. `.agents/AGENTS.md`;
2. `docs/implementation-plan.md`;
3. `docs/project-management/README.md`;
4. `docs/project-management/status.md`;
5. `docs/review/phase-5-0-security-review-brief.md`;
6. `docs/review/phase-5-0-security-review.md`;
7. `docs/review/phase-5-0-remediation-r11-handback.md`;
8. `docs/review/phase-5-0-package-plan.md`;
9. `docs/review/phase-5-0-logical-schema.md`;
10. `docs/discovery/open-decisions.md`, concentrating on OD-62 through OD-66;
11. `docs/project-management/decision-register.md`, `raid-register.md`,
    `change-log.md`, and the Phase 5.0 portions of the data-migration register;
12. `docs/review/phase-5-0-od-63-ruling-draft.md`; and
13. `docs/review/phase-4-post-gate-remediation-r3-handback.md` for boundary
    context only.

Check `git status` before work. The tree is intentionally dirty and contains
uncommitted work belonging to the maintainer and other agents. Do not reset,
revert, reformat, stage, commit, or overwrite it. Do not edit controlled status,
roadmap, RAID, decision, change-log, package-plan, schema, security-review, or
handover documents. New review/preparation artifacts are permitted only at the
paths named below.

If two governing documents conflict, stop and report the conflict. Do not pick
the interpretation that makes implementation easier.

## Current state that must remain true

- Phase 4 remains approved. Codex's R3 review found no Blocking or Important
  finding in P4-PG4/P4-PG5, but do not edit controlled records to memorialize
  that outcome under this prompt.
- Package 5.0 revision 12 is design documentation, not implemented behavior.
- P5.0-SR1 and P5.0-SR2 are remediated on paper but remain open pending the
  named Security Reviewer's disposition.
- P5.0-R5 remains Blocking. P5.0-R1 and P5.0-R4 remain open; P5.0-R2 is closed.
- OD-62 through OD-66 remain Open. Do not select or approve an option.
- A-5.0-3, A-5.0-4, and A-5.0-5 remain unconfirmed.
- C-1 is incomplete; C-2 is an inventory; C-3 and C-4 have not run.
- R-5.0-12 through R-5.0-16 are proposed/unaccepted residuals.
- No Package 5.0 host object or schema object exists.
- Implementation, migration, deployment, cutover, production changes and
  Package 5.1+ remain unauthorized.

## Workstream A — adversarial revision-12 security analysis

Independently analyze all twelve surfaces in package-plan §9.2. Do not merely
summarize the implementer's argument. Attempt to falsify it.

At minimum:

1. Re-review P5.0-SR1's remediation end to end: approval record, root-owned bare
   object store, object-id-only lookup, SHA-256 source manifest, deployment map,
   closed source/dependency partition, Algorithm D ordering and rollback,
   provenance record, `init-generation` C0, writer W11a, and the database
   provenance foreign keys.
2. Re-review P5.0-SR2: prove §2.12.2 is the sole live membership authority and
   that provisioning, E1–E8, holder tables, permission matrices, `JNL-52`,
   `sudoers`, `pg_ident`, and every identity-dependent argument cite it without
   contradicting it.
3. Trace every trusted input and writer. Look specifically for mutable Git refs,
   alternates, replace/graft mechanisms, hooks, submodules, unsafe checkout or
   path handling, symlink/hard-link races, ownership/mode gaps, unaccounted
   deployed files, TOCTOU windows, and rollback states that could leave live
   bytes without current provenance.
4. Test the claimed SHA-1/SHA-256 reasoning on paper: establish exactly which
   object bytes are independently hashed, which paths and modes are bound, and
   whether any extraction decision remains controlled only by a Git object ID.
5. Trace the `approved_source_revisions` and generation foreign-key fence under
   direct SQL, schema-owner access, constraint timing, restore, trigger disable,
   `session_replication_role`, and `TRUNCATE` scenarios. Distinguish ordinary
   runtime refusal from powers intentionally retained by PostgreSQL superuser or
   host root; do not claim a database constraint restrains a superuser if it
   does not.
6. Recheck `pg_hba.conf`/`pg_ident.conf` first-match ordering, Unix-socket reach,
   `PASSWORD NULL`, role grants, and whether later broad rules or inherited role
   membership can expose either privileged database principal.
7. Recheck the eleven-authority model against Linux DAC, supplementary groups,
   `FS_IOC_SETFLAGS`, `CAP_FOWNER`, `CAP_LINUX_IMMUTABLE`, bounding/permitted/
   effective/inheritable/ambient sets, securebits, `capsh` ordering, and the
   actual holder table.
8. Analyze the two privileged tools, their exact `sudoers` argument boundaries,
   environment handling, executable/library provenance, path resolution,
   descriptor use, temporary paths, cleanup states, and opportunities for a
   constrained identity to make evidence disappear.
9. Re-evaluate all five residuals R-5.0-12 through R-5.0-16. Determine whether
   each is accurately bounded and whether the design omits a sixth residual.
10. Check every stop condition, refusal code and evidence case for an assertion
    that cannot actually distinguish the safe and unsafe state it claims to
    distinguish.

Classify each concrete issue as Blocking, Important or Optional using
implementation-plan §16.4. A disagreement with an unaccepted policy option is
not itself a finding; an internally inconsistent, bypassable or untestable
control is.

## Workstream B — cross-document consistency and traceability

Perform a mechanical and semantic consistency review across the revision-12
package plan, logical schema, security brief, R11 handback, open decisions and
management registers.

Verify at least:

- revision number, table count, column/foreign-key/trigger count, evidence IDs
  and case count, authority count, residual count, work-package count, estimate,
  remediation allowance and security-review effort;
- every live group-membership statement and every superseded quotation;
- every reference to six versus seven tables, four versus five append-only
  histories/triggers, eleven versus twelve surfaces, and three versus five
  residuals;
- that no controlled document accidentally says P5.0-SR1/SR2, P5.0-R5,
  OD-62–OD-66, A-5.0-3/4/5, C-1/C-3/C-4, or Package 5.0 readiness is closed;
- schema diagram/table/constraint/delete/grant/evidence consistency;
- source-to-target and package-readiness traceability required by the
  implementation plan; and
- that the proposed decision order remains executable: security recommendation
  before OD-64/65/66, OD-63 when its owners are ready, and OD-62 last.

Do not repair controlled documents. Record exact file and line references for
each discrepancy so the maintainer can assign a bounded correction.

## Workstream C — prepare, but do not decide, the remaining owner actions

Prepare concise decision/evidence aids that reduce the maintainer's work without
pre-empting it:

1. For OD-63, review the existing ruling draft for completeness, internal
   consistency, required recommendations, change-control effects and signature
   fields. Propose exact corrections in your report; do not edit or sign it.
2. For OD-64, OD-65 and OD-66, create an option-neutral decision matrix stating
   each option, security/availability/operations trade-off, affected residuals,
   prerequisites, reversibility and which named owner must recommend/approve.
3. For OD-62, create a final risk-acceptance checklist that consumes the other
   four rulings and makes every accepted residual explicit. Do not recommend
   accepting a residual unless your security analysis supports that statement;
   never mark it accepted.
4. Create an operational-evidence runbook for P5.0-R5 and checks C-1, C-3 and
   C-4. Separate:
   - safe read-only host discovery;
   - disposable-environment mutations requiring explicit authorization;
   - privileged production-like evidence;
   - database migration/constraint evidence; and
   - evidence that cannot exist before implementation.

For every command in the runbook, state intended identity, prerequisites,
expected safe result, refusal result, cleanup/recovery, evidence captured and
whether explicit elevation or external-state authorization is required. Do not
run commands that require elevation or create/change host or database state.
Do not read secrets, environment files, credentials, tokens or private keys.

## Permitted read-only checks

You may use repository searches, parsers and local read-only commands to verify
documents and already-public host facts. Prefer `rg`. You may inspect tool
manuals and version output already available on the host. Do not use `sudo`,
`su`, `systemd-run`, `setpriv`, `capsh` to construct an identity, `chattr`,
`setcap`, `usermod`, `groupadd`, `useradd`, `install`, `chmod`, `chown`, `git
init`, `git fetch`, database DDL/DML, service commands, or network calls.

Do not attempt to work around a permission denial. Record C-1 as not run if the
current identity cannot read `/etc/sudoers.d/`. C-3 and C-4 necessarily remain
operational evidence unless a separately authorized disposable environment is
provided.

## Deliverables

Create exactly these new files:

1. `docs/review/phase-5-0-gemini-readiness-analysis.md`
   - executive outcome;
   - scope and authority limitations;
   - twelve-surface review matrix;
   - P5.0-SR1 and P5.0-SR2 recommended dispositions for Codex's consideration;
   - findings with severity, evidence, consequence and smallest remediation;
   - residual-risk completeness analysis;
   - cross-document consistency results;
   - checks run and checks not run; and
   - an explicit statement that no implementation or external mutation occurred.
2. `docs/review/phase-5-0-gemini-decision-matrix.md`
   - option-neutral preparation for OD-62 through OD-66;
   - dependencies, accountable roles and required signatures;
   - no selected option, approval, signature or effective ruling.
3. `docs/review/phase-5-0-gemini-operational-evidence-runbook.md`
   - ordered evidence plan for P5.0-R5 and C-1/C-3/C-4;
   - authorization, identity, safety, cleanup and capture requirements;
   - no claim that an unexecuted check passed.

Do not create or change any other file. If completing a deliverable would
require a controlled-document correction, record the proposed patch in prose
with exact locations; do not apply it.

## Verification and handback

Before handing back:

```sh
git status --short
git diff --check -- \
  docs/review/phase-5-0-gemini-readiness-analysis.md \
  docs/review/phase-5-0-gemini-decision-matrix.md \
  docs/review/phase-5-0-gemini-operational-evidence-runbook.md
```

Also report:

- every file read and created;
- every command run and its result;
- all checks not run and why;
- whether any permission denial occurred;
- confirmation that no secret or real player data was read or written;
- confirmation that no Git write, host/database mutation, network call,
  implementation, migration, deployment, cutover or Package 5.1+ work occurred;
  and
- the exact next action for Codex, each accountable owner and the Acceptance
  Authority.

Stop immediately if you discover a secret, real player data, an instruction to
retire Discord, an authorization to implement Package 5.0, or a conflict between
the controlled baseline and this prompt. Report it without attempting a fix.
