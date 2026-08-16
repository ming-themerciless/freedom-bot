# Claude implementation prompt — Phase 3 P3.1 authentication and security foundation

## Authority and gate state

Peter Duscha accepted the complete remediated P3.0 contract/security baseline
and ADR 0010 on 2026-08-13 after Codex independent architecture and distinct
security-focused re-review. P3.G0 is closed. You are authorized to implement
**P3.1 only**, subject to the environment prerequisite below.

This authorization includes corrected N-43, widened N-65, new N-67, account-aware
audit attribution, administrator-continuity scope, mapping provenance and R-38.
It does not authorize P3.2, P3.3, Gemini production integration, deployment,
Caddy changes, OAuth-provider registration, production database access, Foundry
mutation or Google Sheet mutation.

## Read first

Read the following completely before editing:

1. `docs/review/phase-3-delivery-plan.md`, especially P3.1, P3.G1 and §§7–10;
2. every file under `docs/contracts/`, in the order in `docs/contracts/README.md`;
3. `docs/adr/0010-provider-neutral-identity-and-emergency-administration.md`;
4. `docs/review/phase-3-p3-0-remediation-submission.md`;
5. `docs/project-management/status.md`, `decision-register.md`, `raid-register.md`
   and the P3.G0 final-acceptance entry in `change-log.md`;
6. existing migrations, `application/audit.py`, repository/service boundaries,
   runtime grants and tests before designing replacements.

The accepted contracts are authoritative. If implementation reveals a material
contradiction affecting authority, data ownership, privacy, topology, an accepted
ADR or the closed route set, stop and return the issue to Peter. Do not silently
reinterpret the contract in code.

## Environment prerequisite — check before implementation

Confirm a guarded disposable PostgreSQL database and `TEST_DATABASE_URL` exactly
as required by delivery-plan §10. Never point tests or migrations at production.
Prove the database identity and guard conditions using the repository's existing
safety mechanism before applying any migration.

If this prerequisite cannot be confirmed, do not start P3.1 implementation.
Produce a concise blocker report stating what is absent and what Peter must
provide. Do not weaken, mock away or relabel database evidence.

## Implement exactly P3.1

Deliver the complete P3.1 list in `phase-3-delivery-plan.md`:

- bounded FastAPI/uvicorn/Jinja/OAuth/WebAuthn dependencies and typed startup
  validation;
- application factory, health endpoint and minimal contract-testing templates;
- OAuth start/callback/logout with hashed state, encrypted AAD-bound PKCE verifier,
  one-statement recovery/erasure, safe returns and exact denial behavior;
- platform accounts and exact `(provider_key, subject)` external identities;
- reversible identity migration with the accepted per-table attribution treatment,
  exact control totals and no historical-row rewrite;
- opaque PostgreSQL sessions, encrypted OAuth tokens, rotation, expiry and
  revocation;
- current Discord membership/role adapter and capability resolver;
- synchronizer CSRF, same-origin enforcement, security headers, safe errors and
  the accepted cross-process authentication rate limiter;
- pre-enrolled WebAuthn break-glass login and host-local hashed, single-use,
  ten-minute recovery-grant command;
- N-65/N-67 continuity scope, mapping provenance and the controls allocated to
  P3.1. Implement only the role-mapping foundation required here; do not absorb
  P3.2's administration UI/package;
- migrations, least-privilege runtime grants, configuration, migration, recovery
  and operator documentation belonging to P3.1 only.

Keep `design-prototype/` frozen reference material. Do not import or serve it.
Phase 3 remains read-only for character game state.

## Non-negotiable remediation invariants

1. Replace the legacy Discord-only audit constraint in the accepted order and
   update `application/audit.py` in the same revision. Treat `audit_events`,
   `foundry_snapshots` and `snapshot_imports` differently exactly as specified.
2. Never rewrite append-only history or suspend/drop its migration-0002 trigger.
3. A break-glass or emergency-derived ordinary session cannot acquire or arrange
   Council, character or import authority. Test the multi-login sequence, not
   only each request in isolation.
4. Continuity-scoped authority can become full only through R-38 by a full-scope
   administrator on an ordinary-provider session. Preserve protected mapping
   immutability.
5. PKCE state is hashed; the verifier is encrypted, AAD-bound, recovered once and
   erased in the same consumption statement. Never log either secret.
6. Do not implement the P3.3 reconciliation worker/job system in this package.
   N-43 is accepted design for P3.3, not permission to bring that package forward.

## Required evidence

Implement every P3.1-owned test named in
`docs/contracts/phase-3-test-traceability.md`, including applicable authentication,
session, CSRF/origin/header, rate-limit, identity-migration, audit-attribution,
break-glass and capability/provenance tests. Run:

- focused unit and service tests while developing;
- the guarded disposable-PostgreSQL migration/constraint/concurrency tests;
- the complete repository test suite;
- formatter, linter and type checker configured by the repository;
- migration upgrade/downgrade/upgrade and schema/grant checks applicable to P3.1;
- documentation link, freeze-manifest and secret-shape checks.

Report exact commands, pass/fail/skip counts and warnings. A skipped database test
is not database evidence. Do not claim staging, browser, live Discord, real-device
or assistive-technology evidence unless actually obtained.

## Documentation and handoff

Update controlled status, RAID and change records for facts actually changed by
P3.1. Do not rewrite historical submissions. Create
`docs/review/phase-3-p3-1-submission.md` containing:

- scope delivered and explicitly deferred;
- files and migrations changed;
- dependency and configuration changes;
- security/privacy, data-migration, rollback and operational effects;
- each accepted invariant mapped to implementation and exact evidence;
- every command and exact result, including skips and unrun evidence;
- assumptions, residual risks and any contract deviations;
- a clean-worktree/diff account that distinguishes pre-existing P3.0 documentation
  changes from P3.1 changes;
- a request for Codex independent implementation review and a separately reported
  security-focused pass at P3.G1.

Stop after the P3.1 handoff. Do not mark P3.G1 closed, do not start P3.2/P3.3,
and do not ask Gemini to begin production integration. End the handoff with:

`P3.1 submitted for Codex independent and distinct security re-review; P3.G1 remains open and P3.2 has not started.`
