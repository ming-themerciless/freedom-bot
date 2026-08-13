# Claude prompt — Phase 3 P3.0 contract and security design baseline

Use this prompt from `/opt/discord-bots/freedom-bot` in a fresh Claude Code
session.

---

Implement **Phase 3 package P3.0 only**: the contract and security design
baseline for the Freedom Blades production web portal.

Peter Duscha accepted the Phase 3 delivery plan on 2026-08-13. You are the
Working Technical Lead and backend implementer for this package. Codex will
perform the independent architecture/security review; Peter alone accepts
P3.G0.

This package is documentation and design. Do not implement P3.1, add a web
framework scaffold, add dependencies, create migrations, add protected routes,
alter runtime code, deploy, start services, contact Discord, access production
data, inspect secrets, or proceed past P3.G0. Do not ask Gemini to begin
production integration.

## Required context

Read completely before editing:

1. `AGENTS.md`, `.agents/AGENTS.md` and `CLAUDE.md`;
2. `docs/implementation-plan.md`, especially §§0, 3, 5, 6, 7, 12.0, 12.1 and
   the complete Phase 3 section;
3. `docs/review/phase-3-delivery-plan.md`;
4. `docs/discovery/open-decisions.md`, especially OD-16, OD-17, OD-18, OD-24,
   OD-42 and OD-43;
5. `docs/adr/README.md` and ADRs 0001–0009 under `docs/adr/`, noting the
   rejected/superseded status recorded for ADR 0008;
6. `docs/discovery/command-inventory.md`, `docs/discovery/sheet-inventory.md`,
   `docs/rules/field-ownership.md` and
   `docs/project-management/data-migration-register.md`;
7. Phase 2 schema, migration, repository, audit, import and reconciliation code
   and tests relevant to the proposed contracts;
8. `.env.example`, current dependency declarations and operations/topology
   documentation; and
9. the accepted visual handoff and freeze manifest only to identify required
   screens and view-model states—not to edit frozen prototype files.

Check `git status` before editing. Preserve unrelated work and never read or
print `.env`, credentials, tokens, database URLs, real snapshots or player data.

## Fixed decisions and boundaries

Treat the accepted plan as authoritative. In particular:

- Discord OAuth2 is the first ordinary-user authentication adapter.
- Platform accounts use stable internal IDs. Discord IDs are external identity
  facts and must not key sessions, `character_access`, or human audit identity.
- External identities are exact, unique `(provider, subject)` links. For OIDC,
  the provider key must unambiguously bind the configured issuer. Never merge
  accounts by name, username, display name or email.
- Authentication providers are replaceable adapters. Authorization, session
  integrity, CSRF, origin/host validation, rate limiting, input bounds, audit,
  and safe failure are provider-independent core controls.
- Emergency authentication is for the protected Server Administrator account.
  It grants Platform Administrator capability only and never implies Council,
  character ownership, game-policy authority or import-apply authority.
- There is no permanent local password and no ordinary-user alternative
  provider in Phase 3. Design the adapter boundary; do not select a hypothetical
  replacement provider.
- The proposed normal emergency mechanism is at least two pre-enrolled
  WebAuthn credentials. Last-resort recovery is a host-local command issuing a
  hashed, purpose-bound, single-use 10-minute grant.
- Public exposure terminates at Caddy. The design must reject unknown hosts,
  keep application/PostgreSQL ports private, bound connections and timeouts,
  and provide an operator kill switch that disables the portal without stopping
  the Discord bot or Foundry.
- Administrator does not imply Council. Council does not imply administrator.
- Phase 3 ordinary-member views are read-only. No character game-state edit
  endpoint may exist.
- The 9.57-second measured 32-Actor reconciliation preview requires a durable
  asynchronous job. It cannot be modelled as a synchronous handler or an
  in-memory-only queue.
- No contract may expose raw snapshot bytes, OAuth tokens, authenticator
  secrets, recovery tokens, internal exceptions or other players' private data.

If repository evidence conflicts with these decisions, document the conflict
and stop on that point. Do not silently change authority, privacy, data
ownership, topology, migration strategy or an accepted ADR.

## Required deliverables

Create a coherent P3.0 package under `docs/` with clear links between artifacts.
Choose descriptive filenames and update the management indexes that must point
to them. At minimum deliver all of the following.

### 1. Route and authorization contract

Define every planned P3.1–P3.3 endpoint with:

- stable route name and versioned path;
- HTTP method and response/content type;
- authentication state and exact capability/object-level authorization;
- CSRF and origin requirements;
- request bounds and validation;
- success, empty, loading/polling, stale, denied and safe-error outcomes;
- session, role-cache and audit effects;
- whether it is browser navigation, form submission, HTMX partial, polling or
  operator-only CLI; and
- explicit proof that UI hiding is not authorization.

Include unauthenticated, non-member, member, Council, Platform Administrator,
Council+Administrator and break-glass matrices. Cover login/callback/logout,
health, My Characters, character detail, link administration, role-capability
mapping, reconciliation job lifecycle, import confirmation and audit search.

### 2. Versioned view-model contracts

Specify typed, bounded view models for every accepted screen and partial:

- login/session and degraded-provider states;
- character summaries and detail, including portrait metadata and safe
  fallback;
- character-link administration and identity-resolution states;
- field-profile classifications and `migration deferred` ownership;
- reconciliation job status/progress/result/stale states;
- confirmation checksum, world, folder, Actor count, mappings and warnings;
- immutable paginated audit search; and
- standard empty/loading/denied/validation/error states.

Define escaping and safe-display rules. Browser-provided IDs, roles, prices,
counts and calculated results are never authoritative. Keep contracts compatible
with server-rendered Jinja and modest HTMX; do not introduce an SPA/API redesign.

### 3. Logical schema and migration contract

Provide a logical schema artifact and decision table covering at least:

- platform accounts and lifecycle/status;
- external identities and issuer/provider namespace;
- WebAuthn credential metadata without secrets;
- hashed recovery grants and replay/expiry state;
- opaque server-side sessions and rotation/revocation;
- encrypted OAuth-token records and deletion rules;
- Discord membership/role projections and cache timestamps;
- role-to-capability mappings and protected bootstrap mapping;
- `character_access` and its migration to platform-account identity;
- append-only human attribution/audit compatibility;
- durable reconciliation jobs, leases, attempts, idempotency and bounded result
  references; and
- optimistic concurrency and timestamps.

For every table/relationship record IDs, types, foreign keys, uniqueness,
checks, indexes, retention, encryption/hashing boundary, writer, reader and
deletion policy. Preserve PostgreSQL semantics and reversible Alembic staging.

Design the existing-Discord-reference migration as dry-runnable, idempotent,
transactional and reversible before cutover. Define exact source/target control
totals, unresolved handling, historical audit readability, downgrade limits,
backup/restore rehearsal and the point after which rollback becomes recovery.
Do not write the migration in P3.0.

### 4. State machines

Define explicit state machines and forbidden transitions for:

- OAuth attempt and callback;
- authenticated session, rotation, expiry and revocation;
- WebAuthn and host-recovery login;
- external-identity link/unlink/provider retirement; and
- reconciliation job queue, lease, preview, confirmation, apply, failure,
  expiry and cancellation.

No job may be called completed before its domain commit and audit effect are
durable. Specify restart, retry, lost-response, expired-lease, concurrent apply,
provider outage and audit-failure behaviour.

### 5. ADR and threat model

Add a proposed ADR for provider-neutral identity and Discord-independent
emergency administration. It must record context, decision, alternatives,
security consequences, provider-adapter interface, stable-account model,
account-link/unlink rules, recovery boundary, privilege separation, migration
strategy and rollback/recovery implications.

Create a threat model with assets, trust boundaries, entry points, attackers,
abuse cases, controls, residual risks and verification mapping. Cover at least:

- OAuth state/PKCE/callback and return-target attacks;
- account linking, issuer/subject collision and provider retirement;
- session fixation/theft/replay and privilege changes;
- CSRF, host-header, origin, CORS and clickjacking issues;
- object substitution and confused deputy;
- stale Discord membership/roles and Discord outage;
- WebAuthn enrollment/recovery abuse and emergency-account escalation;
- credential stuffing, scanning, bot traffic and resource exhaustion;
- malicious uploads, filenames, Actor/warning text and oversized snapshots;
- job retry, lease theft, duplicate/concurrent apply and audit failure;
- unsafe rendering, exception/log leakage and raw-snapshot disclosure; and
- co-located host impact on the bot, Foundry and PostgreSQL.

The design must remain safe if Discord is unavailable and must fail closed for
ordinary protected access when the accepted grace bound is exhausted.

### 6. Configuration, dependency and operational contracts

Propose—do not install—the smallest justified production and test dependency
set. Record exact purposes, version/pinning strategy and rejected alternatives.

Define typed configuration without secret values for Discord OAuth, provider
registry, WebAuthn RP ID/origins, encryption keys, cookie/session limits,
membership cache, rate limiter, request bounds, database pools, job worker,
proxy trust, allowed hosts, health, kill switch and environment separation.
Specify startup refusal for unsafe or cross-environment combinations.

Define development, disposable-PostgreSQL, staging and production topology,
Caddy/firewall boundaries, private ports, timeouts/connection limits,
monitoring without personal data, recovery operations and rollback. Do not
claim the current firewall or staging environment is configured unless verified
by separately authorized evidence.

### 7. Exact acceptance and test traceability

Expand every acceptance and mandatory-test row in the accepted plan into named
test cases or parametrized test groups owned by P3.1, P3.2, P3.3 or P3.5.
Include unit, service, direct-HTTP, real-PostgreSQL migration/constraint,
concurrency/restart, browser/accessibility and operational checks.

Every endpoint needs the full role matrix where applicable. Include negative
tests for forged direct requests, cross-character substitution, name/email
collisions, stale roles, Discord outage, recovery replay/expiry, CSRF,
host/origin rejection, raw-data leakage, audit immutability, double apply and
unsafe startup. Clearly label checks that require later staging, real-device or
assistive-technology evidence.

## Quality and reconciliation requirements

- Use stable terminology consistently across routes, view models, schema,
  states, threats and tests.
- Give every numeric policy one authoritative definition and reference it
  elsewhere; do not create conflicting copies.
- Trace each design element to the accepted plan, implementation-plan
  acceptance criterion, OD/ADR and owning future package.
- Identify assumptions and residual risks candidly. Do not invent evidence.
- Update `docs/project-management/status.md`, decision/ADR indexes, RAID and
  change log only where P3.0 artifacts genuinely change their recorded state.
- Do not mark P3.G0 accepted, P3.1 authorized, Phase 3 implemented or the
  production portal secure.

## Verification

Run repository-local documentation and consistency checks that already exist.
At minimum run:

```bash
git diff --check
git status --short
```

Also run any existing Markdown-link, ADR-index, policy-reference or documentation
checks you discover. Do not install tooling merely to satisfy this package.
Review the complete diff for secrets, real identities, production data,
contradictory policies, implementation changes and scope creep.

## Required handoff

Write a P3.0 handoff document that:

- inventories every created/changed artifact;
- maps each required deliverable to its exact section;
- lists decisions made versus decisions still requiring Peter;
- lists assumptions, residual risks and any conflicts;
- reports commands actually run and their exact outcomes;
- confirms that no runtime implementation, migration, dependency, service or
  deployment was added; and
- requests Codex independent architecture/security review at P3.G0.

Lead your final response with blockers or findings. If none, summarize the
artifacts and verification. End with exactly:

`P3.0 submitted for Codex review and Peter's P3.G0 decision; P3.1 has not started.`

---
