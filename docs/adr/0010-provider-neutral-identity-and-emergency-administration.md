# ADR 0010 — Provider-neutral platform identity and Discord-independent emergency administration

Status: **Accepted by Peter Duscha on 2026-08-13 at P3.G0**, after Codex
independent architecture and security-focused re-review. Acceptance includes the
remediated account-based audit attribution (D5), administrator-continuity scope,
mapping provenance, N-67 and ratification boundary (D9.1/R-38). P3.1 may begin
subject to its recorded environment prerequisite; acceptance does not claim that
the prospective migration or PostgreSQL tests have run.

Date: 2026-08-13

Relationship to existing ADRs: this ADR **extends** [ADR 0004](0004-discord-oauth2-authentication.md)
and supersedes none of it. Every decision in 0004 — OAuth2 with PKCE, scopes
`identify` and `guilds.members.read`, rejection of non-members at callback,
capabilities from role snowflakes, cached roles are never proof, `character_access`
separate from role, opaque server-side sessions, encrypted server-side tokens,
synchronizer CSRF, service principals — is carried forward unchanged. What 0004
did not decide, and what this ADR decides, is **what a session, an access grant and
an audit attribution point at**.

## Context

### What forced the question

OD-24 (2026-07-31) established that the Server Administrator mapping is protected
bootstrap configuration and that Discord server ownership is an external
emergency-recovery path, *"not the normal authorization mechanism"*.

OD-43 (ruled 2026-08-13) went further and made two product requirements binding:

1. **Availability.** The Server Administrator must retain an independent access
   route if Discord authentication is unavailable.
2. **Portability.** The account and authorization model must permit a controlled
   replacement of Discord as the community login provider. Discord *"must not
   become the permanent identity key for sessions, character ownership or audit
   attribution"*.

The ruling deliberately split decided product requirements from security
architecture, and assigned the architecture to P3.0: *"P3.0 must turn that proposal
into an accepted ADR, schema and tested migration contract before P3.1
authentication implementation starts."* This is that ADR.

### What the codebase currently assumes

Phases 1 and 2 key authorization-bearing and attribution rows by Discord
snowflake: `character_access.discord_user_id`, `character_access.granted_by_discord_user_id`,
`audit_events.actor_discord_user_id`, `snapshot_imports.actor_discord_user_id`,
`foundry_snapshots.received_by_discord_user_id`. Nothing is wrong with that as
Phase 1 work — it matched plan §7.1. It does mean that a Discord replacement
today would be a rewrite of character ownership and audit attribution, which is
precisely the outcome delivery plan §1 forbids.

### The constraint that shapes the answer

`audit_events`, `foundry_snapshots` and `snapshot_imports` are append-only, with a
trigger installed in **migration 0002** that refuses `UPDATE` and `DELETE` **even
for the schema owner**. Any identity design that requires rewriting historical
attribution is therefore not merely awkward; it is incompatible with an accepted
integrity control that Phase 2 passed its gate on.

A second, sharper constraint was missed in the first revision of this ADR and is
recorded here because it changes D5: migration 0001's
`ck_audit_events_human_action_has_an_actor` requires *a Discord user id* for every
human capability. An emergency administrator acting without Discord is a human
capability with no Discord user id, so the constraint refuses the very audit event
that D8's recovery path must write — and, since a login and its audit event share
one transaction, refuses the emergency login itself. Discord-independence is not
achievable by adding a column; it requires replacing that constraint.

## Decision

### D1 — A platform account is the identity of a person on this platform

`platform_accounts.id` is a UUID assigned at row creation. **Sessions,
`character_access`, human audit attribution and every authorization decision refer
to it.** No provider identifier appears in any of those positions again.

### D2 — An external identity is an exact, unique `(provider_key, subject)` link

`external_identities` holds one row per provider identity, unique on
`(provider_key, subject)` and pointing at exactly one account. A Discord snowflake
remains a typed Discord fact; it is not, and never becomes, a platform account id.

`provider_key` binds the issuer unambiguously: the fixed token `discord` for
Discord, and `oidc:<exact issuer>` for any future OIDC provider, compared
byte-for-byte at every authentication. A changed issuer is a different provider
key and therefore a different identity — never a silently migrated one.

### D3 — No name, username or email ever establishes identity equivalence

`external_identities` carries no display-name, username or email column. The
absence is the control: a column that does not exist cannot become a matching key.
Linking an additional identity to an existing account requires strong
reauthentication and an audited confirmation; automatic merging does not exist as
an operation anywhere in the design.

### D4 — Identities are retired, never deleted

Unlink and provider retirement set `state = 'retired'` and keep the row, including
its uniqueness. Two consequences, both intended: historical audit attribution
stays readable after a provider is retired, and a retired subject cannot be
re-linked to a *different* account.

### D5 — History is never rewritten; the attribution *rule* is replaced, and reads resolve

Historical rows keep their Discord column and are never touched. New rows carry
`actor_platform_account_id`.

The legacy constraint `ck_audit_events_human_action_has_an_actor` is **replaced**,
by explicit DDL in a committed migration, with
`ck_audit_events_human_action_has_an_attribution`, which accepts an account id, a
Discord id, or a machine capability. The wider rule is added `NOT VALID` before
the narrower one is dropped, so the table is never less constrained than it is
today; the replacement is logically implied by what it replaces, so no existing
row can be invalidated and none needs to be read to know it; and `ADD COLUMN`,
`ADD CONSTRAINT … NOT VALID` and `DROP CONSTRAINT` are catalogue operations for
which row triggers never fire. The append-only trigger is therefore **not
weakened, suspended, dropped or worked around — it is never reached.** Reads
resolve the historical form through `external_identities`.

`snapshot_imports` and `foundry_snapshots` are handled on their own evidence
rather than by symmetry: neither carries an attribution constraint today, so
neither needs a replacement; `snapshot_imports` gains a new `NOT VALID`
attribution check that binds future rows only, and `foundry_snapshots` gains
none, because a supervised-bootstrap row that names no human is legitimate.
The exact DDL, the locking, the downgrade and the nine named PostgreSQL tests are
in [`../contracts/phase-3-logical-schema.md`](../contracts/phase-3-logical-schema.md)
§6.

The application-level copy of the same rule — `UNATTENDED_CAPABILITIES` in
`application/audit.py` — changes in the same revision. A guard that refuses in
Python what the database now permits would produce the same outage with a
different traceback.

### D6 — Authentication providers are replaceable adapters; the security core is not

A provider adapter is responsible for exactly one thing: turning a completed
authentication into a verified `(provider_key, subject)` plus, where the provider
supplies it, a membership and role projection. Session integrity, authorization,
CSRF, origin and host validation, request and concurrency bounds, rate limiting,
audit and safe failure are **provider-independent core controls** and cannot be
weakened by replacing Discord (delivery plan §9.10).

The adapter interface P3.1 implements:

```text
class IdentityProvider(Protocol):
    provider_key: str
    def begin(self, return_path: str) -> ProviderRedirect: ...
    def complete(self, callback: ProviderCallback) -> VerifiedIdentity: ...

VerifiedIdentity(provider_key, subject, projection: MembershipProjection | None)
```

`VerifiedIdentity` carries **no capability**. Capability is resolved by the
platform from role-capability mappings, exactly as ADR 0004 requires. A provider
that claimed a capability would be believed by nothing.

### D7 — Phase 3 delivers the boundary, not a second provider

There is no second ordinary-member provider, no local password database, and no
selection of a Discord replacement in Phase 3. Adding one later requires its own
accepted provider, privacy, account-linking and migration package (delivery plan
§9.9). The interface makes that bounded; it does not pre-approve an unknown
provider.

### D8 — Emergency administration is phishing-resistant, host-anchored and narrow

- **Normal emergency credential:** at least two pre-enrolled WebAuthn credentials
  for the accountable Server Administrator. **No permanent local password exists**
  anywhere in the design.
- **Last-resort recovery:** a host-local operator command issues a random,
  purpose-bound, single-use grant, stored only as a SHA-256 hash, valid for 10
  minutes, fully audited without storing the token. **There is no HTTP route that
  issues a grant**, so the recovery path requires existing host authority and
  cannot be reached from the internet.
- **Enrollment is host-local too**, so a stolen emergency session cannot enroll an
  attacker's authenticator.
- **Sessions are short:** 15-minute idle, 60-minute absolute, no extension.

### D9 — Emergency authentication grants Platform Administrator capability only

Capability resolution short-circuits on the session's authentication method: a
session whose method is not the ordinary provider resolves to exactly
`{platform_administrator}`, whatever Discord roles the same human holds. It never
implies Council, never implies character ownership, and never makes an import or a
game-policy change legal (OD-24, OD-43, delivery plan §9.6).

P3.0 additionally proposes a **route-level restriction** (N-65): a
continuity-scoped session may reach only the identity/capability administration
and audit-read surface. Emergency access exists to restore administrative
continuity, not to operate imports. This is a tightening beyond the accepted
contract and is one of the decisions listed for Peter at P3.G0.

**D9.1 — capability resolution is not enough, and the first revision of this ADR
said it was.** Short-circuiting on `auth_method` bounds what the emergency
session may do *while it exists*. It says nothing about what the emergency
session may **arrange**: a break-glass caller that can write an arbitrary
role-capability mapping can map a role it controls to `guild_council`, log in
through Discord as an ordinary member holding that role, and reach every import
route with no short-circuit in sight. Nor is a narrower allowlist sufficient on
its own, because a mapping to `platform_administrator` yields an ordinary
administrator who may then map anything, as administrators legitimately may.

The remediation is therefore twofold, and both halves are required:

1. **N-67, the administrator-continuity allowlist.** A continuity-scoped caller
   may create a mapping naming `platform_administrator` and revoke a
   non-protected mapping naming `platform_administrator`. Nothing else. Enforced
   by the application service, by
   `CHECK (created_under_scope = 'full' OR capability = 'platform_administrator')`,
   and by the N-65 route surface — three controls, none of which is the only one,
   and none of which is the session's own short-circuited capability set.
2. **Provenance.** A mapping records the administrator scope it was created
   under. Administrator capability conferred only by emergency-provenance
   mappings is itself continuity-scoped, so the restriction survives an ordinary
   login instead of being laundered by one. It ends when a full-scope
   administrator — in practice the holder of the migration-inserted protected
   mapping, which is `ordinary` by construction and cannot be edited — ratifies
   the mapping through R-38 on an ordinary-provider session.

The testable statement is a property of *sequences*, not of sessions: no series
of mapping changes beginning in a break-glass session and passing through any
number of ordinary logins yields Council, character or import authority before
ratification. TC-BG-05a…05e prove it at the service and HTTP boundaries and
directly against the constraint. The mechanism is specified in
[`../contracts/phase-3-logical-schema.md`](../contracts/phase-3-logical-schema.md)
§8.1–§8.2 and [`../contracts/phase-3-state-machines.md`](../contracts/phase-3-state-machines.md)
SM-07.

### D10 — The protected administrator mapping cannot be lost through the application

Exactly one account may carry `is_protected_admin`, enforced by a partial unique
index. The protected role-capability mapping is inserted by migration, not by the
application, and a trigger refuses to update or delete it — including refusing to
clear its own `protected` flag. Capability resolution is a union over active
mappings, so adding mappings can never subtract the administrator capability.
Between the trigger and the union there is no application path to lockout
(OD-24, delivery plan §9.6).

## Security consequences

**Improved.**

- Losing Discord — as a provider, as a company relationship, or for an afternoon —
  no longer implies losing administrative access to the platform.
- Character ownership, audit attribution and sessions survive a provider change
  without a data rewrite, which is the outcome that makes a future migration a
  bounded project rather than a rebuild.
- Emergency access is phishing-resistant by default and cannot be brute-forced,
  because there is no password to guess.
- The most dangerous operations in the emergency path — issuing a grant, enrolling
  a credential — are not reachable over the network at all.

**Worsened, and accepted deliberately.**

- **A second authentication path is a second attack surface.** It is mitigated by
  being narrow (one account, N-12/N-65), short-lived (N-15), rate-limited (N-32,
  N-33), fully audited, and unreachable for issuance without host access. It is
  not eliminated, and the threat model gives it three entries (T-09, T-10, T-11).
- **A recovery grant is a bearer token for ten minutes.** If the operator's
  terminal or clipboard is compromised in that window, the grant is usable. The
  compensating controls are the 10-minute expiry, single use, the N-61 one-live
  rule, and an audit record the operator can compare against their own action.
- **Losing every passkey plus host access is unrecoverable through the
  application.** That is deliberate: the alternative is a permanent backdoor. The
  documented last resort is database-owner recovery outside the application, which
  is an explicit, visible, audited act of operations — the same posture plan §6.5
  already takes for append-only tables.
- **A break-glass session can leave durable administrator continuity behind it.**
  Under N-67 it may map a Discord role to `platform_administrator`, and that
  mapping outlives the emergency session. This is not an escalation — the
  capability reaches no Council, character or import route, and provenance keeps
  it continuity-scoped until ratified — but it is persistence, and it is exactly
  what the recovery case requires. Recorded as residual risk RR-13 rather than
  argued away. The compensating controls are the allowlist, the provenance
  guard, the append-only record of every attempt including refusals, and the fact
  that only a full-scope administrator can make the authority ordinary.
- **An extra join on every authenticated request** (session → account →
  identities), and a second one to resolve mapping provenance for administrator
  capability. Both are indexed lookups; noted so they are decisions rather than
  discoveries.

**Unchanged.**

Every ADR 0004 control. In particular, cached roles remain non-proof, capability
still comes from role snowflakes, and character access still comes exclusively
from `character_access`.

## Migration strategy

Four staged Alembic revisions, each independently reversible, detailed in
[`../contracts/phase-3-identity-migration-contract.md`](../contracts/phase-3-identity-migration-contract.md):

| Stage | Content | Reversal |
|---|---|---|
| A | Create the identity tables; backfill an account and a Discord identity per `discord_users`; add nullable account columns; six control totals checked in-transaction | Downgrade; the Discord keys were never removed |
| B | `NOT NULL`, foreign keys and account-keyed unique indexes **alongside** the Discord-keyed ones | Downgrade; the old invariants never stopped enforcing |
| C | Application cutover; the Discord column becomes a trigger-maintained read-only shadow | Revert the application; the shadow is current |
| D | Drop the legacy columns — **a separate later decision** after a 30-day verification period | **Not a rollback.** Restore from a restore-tested backup and replay |

The Sheet-era identity-evidence migration (`Characters C`, `Players A/B/D`) is a
**separate** pipeline: an operator dry run writes proposals, a Council member
confirms each one individually, and confirmation is what creates a
`character_access` row. Names are evidence; ambiguity stays unresolved and grants
nothing.

## Rollback and recovery implications

- Stages A–C are ordinary rollbacks with no data loss beyond post-cutover
  sessions.
- Stage D is the point of no return and is gated on evidence, not on a calendar.
- If the emergency path itself must be withdrawn after deployment, the withdrawal
  is a configuration change plus a credential retirement, not a schema change: the
  routes refuse when no protected account exists.
- If a recovery grant is suspected compromised, C-02 invalidates it, C-07 revokes
  sessions, and the audit record shows whether it was consumed.

## Alternatives considered

**Keep Discord snowflakes as the platform key and add a separate admin login.**
Simplest, and it satisfies the availability half of OD-43 alone. Rejected because
it fails the portability half: character ownership and audit attribution would
still be Discord-keyed, so replacing Discord would be the rewrite the delivery
plan explicitly rules out. The migration is cheapest now, when `character_access`
is empty or small, and gets monotonically more expensive.

**A permanent local administrator password.** Rejected. It is a standing
credential with no expiry, guessable, phishable, and reusable — the *"permanent
backdoor or overpowered emergency account"* risk the delivery plan names (§12).
Two pre-enrolled passkeys plus a host-issued 10-minute grant covers the same
outages without a credential that exists when nobody is using it.

**A remote API for issuing recovery grants**, protected by an API key. Rejected:
it converts "an attacker needs host access" into "an attacker needs one secret",
and that secret would live in a configuration file on the same host anyway.

**Merging accounts by verified email.** Rejected outright. Email verification
proves control of a mailbox at one moment; it does not prove identity continuity,
and the platform never collects email (scopes are `identify` and
`guilds.members.read` only). OD-42 and ADR 0006 already forbid identity by name;
this is the same rule for a different string.

**Rewriting historical audit rows to carry the new account id.** Rejected because
it requires disabling the append-only trigger installed in migration 0002 — the
control the Phase 2 gate accepted. The resolution join costs one indexed lookup per
displayed row, bounded by N-21's page size, which is a smaller price than a
suspended integrity guarantee.

**Keeping the legacy audit constraint and giving the emergency administrator a
placeholder Discord id.** Rejected, and worth recording because it is the
tempting shortcut. A synthetic snowflake would satisfy the old constraint by
lying: the audit trail would name a Discord user who did not act, the FK to
`discord_users` would need a fabricated row, and every later reader — including
an incident investigation — would have to know which ids are real. Replacing the
constraint is more DDL and less deceit.

**Emergency capability including Council.** Rejected: OD-24 and OD-43 both
prohibit it, and an emergency route that can approve game policy is a governance
bypass rather than a recovery mechanism.

## Open questions this ADR does not close

- Which provider, if any, eventually replaces Discord (D7 — a later package).
- Whether the N-65 route restriction is accepted as written — now with its subject
  widened to any continuity-scoped session — or whether Peter prefers the broader
  N-12 boundary alone.
- Whether N-67's allowlist is the right two operations. It is deliberately the
  smallest set that restores administrator continuity without database-owner
  access; a reviewer who can name a recovery case it does not cover is naming a
  gap worth closing before P3.1.
- Whether ratification (R-38) should require two full-scope administrators rather
  than one. P3.0 proposes one, because the community has one accountable Server
  Administrator and a two-person rule that cannot be satisfied is a control that
  will be worked around.
- Peak memory and latency of the resolution join under real audit volume, which
  P3.5's staging evidence measures.
- Whether OIDC subject reuse by a future provider needs a stronger control than
  refusal-on-collision (residual risk RR-04).

## Consequences for other records

If accepted, this ADR:

- closes the design half of **OD-43** (its requirement half was ruled 2026-08-13);
- answers ADR 0004's open question about break-glass administration, which OD-24
  answered for policy and this ADR answers for mechanism;
- adds `platform_accounts`, `external_identities`, and the identity/credential
  tables to the plan §7.1 logical model, which currently lists `discord_users`,
  `sessions` and `character_access` without an account concept; and
- requires a change-log entry recording the schema and topology effect, per plan
  §0.2.

None of those updates is made by this ADR. They are made when it is accepted.
