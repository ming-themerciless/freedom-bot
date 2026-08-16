# Phase 3 logical schema and schema decision table

Status: **Accepted 2026-08-13 at P3.G0.** **No migration was written in P3.0.**
Every table below is accepted design; the Alembic revisions belong to
P3.1 (§4–§9) and P3.2 (§10–§11).

Remediated in this revision: §6 (the legacy audit constraint must be replaced,
not merely supplemented, and the three append-only tables do not have the same
shape); §8.1–§8.2 (the administrator-continuity allowlist and mapping
provenance); §9.2.1 (the PKCE verifier is encrypted, transaction-bound and erased
on consumption); §10.1 (the job attempt semantics, the claim predicate, the
`queued`-implies-attempt-remaining constraint and the two-branch reaper). The
append-only trigger is from **migration 0002**, not 0005, throughout.

Package: P3.0 · Owner: Claude · Reviewed against implementation plan §7, §7.3.1,
§9.3, ADR 0003, ADR 0005 and the existing `adapters/database/tables.py`.

This artifact satisfies plan §7.3.1's requirement that a package introducing
normalized data has *"an independently reviewed logical schema artifact (ER diagram
plus schema decision table) naming table ownership, cardinalities, primary and
foreign keys, unique/check constraints, nullability, delete behavior,
effective-dating/history behavior, vocabulary sources, unresolved-record handling,
expected access patterns and source-to-target control totals"* before coding.

The migration of existing Discord references is in
[`phase-3-identity-migration-contract.md`](phase-3-identity-migration-contract.md).
Numbers are `N-nn` from
[`phase-3-numeric-policy-register.md`](phase-3-numeric-policy-register.md).

## 1. The one structural decision

Today, authorization-bearing relationships are keyed by Discord snowflake:

```text
discord_users.id (BIGINT snowflake)
   ├── discord_guild_memberships.discord_user_id
   ├── character_access.discord_user_id            ← authorization-bearing
   ├── character_access.granted_by_discord_user_id ← authorization-bearing
   ├── audit_events.actor_discord_user_id          ← human attribution
   ├── snapshot_imports.actor_discord_user_id      ← human attribution
   └── foundry_snapshots.received_by_discord_user_id
```

OD-43 and delivery plan §9.1 require that sessions, `character_access`, acting-user
audit attribution and human authorization refer instead to a **stable internal
platform account**, with Discord demoted to one external identity among possible
others. The target:

```text
platform_accounts.id (UUID)  ─── the identity of a person on this platform
   │
   ├─1:N─ external_identities (provider_key, subject)  ─── Discord is one row
   │         └─0:1─ oauth_token_grants                 ─── encrypted, short-lived
   ├─1:N─ webauthn_credentials        ─── break-glass, public keys only
   ├─1:N─ recovery_grants             ─── hashed, single use, 10 minutes
   ├─1:N─ sessions                    ─── opaque, server-side
   ├─1:N─ character_access            ─── authorization-bearing (migrated)
   └─1:N─ audit_events.actor_platform_account_id  ─── new rows; history keeps its
                                                     Discord column (see §6.3)

discord_users / discord_guild_memberships / discord_membership_roles
   remain **Discord facts**, keyed by snowflake, projected by an adapter,
   and joined to an account only through external_identities.
```

The rule that makes this reviewable in one sentence:

> A snowflake may answer *"who is this on Discord?"*. Only an account id may
> answer *"who may do this here?"*.

## 2. Entity-relationship diagram

```text
                      ┌───────────────────────┐
                      │  platform_accounts    │
                      │  id UUID PK           │
                      │  status               │
                      │  is_protected_admin   │
                      └───────────┬───────────┘
        ┌─────────────────┬───────┴────────┬──────────────────┬─────────────┐
        │                 │                │                  │             │
┌───────▼────────┐ ┌──────▼───────┐ ┌──────▼────────┐ ┌───────▼──────┐ ┌────▼─────────┐
│external_       │ │ sessions     │ │ webauthn_     │ │recovery_     │ │character_    │
│identities      │ │ id UUID PK   │ │ credentials   │ │grants        │ │access        │
│id UUID PK      │ │ token_hash U │ │ id UUID PK    │ │id UUID PK    │ │(migrated)    │
│provider_key    │ │ auth_method  │ │ credential_id │ │token_hash U  │ │platform_     │
│subject         │ │ idle_exp     │ │ public_key    │ │expires_at    │ │ account_id FK│
│UQ(provider,    │ │ absolute_exp │ │ sign_count    │ │consumed_at   │ │character_id  │
│   subject)     │ │ revoked_at   │ │ UQ credential │ │purpose       │ │access_kind   │
│state           │ └──────────────┘ └───────────────┘ └──────────────┘ └──────┬───────┘
└───┬────────────┘                                                            │
    │1:0..1                                                            ┌──────▼───────┐
┌───▼───────────────┐                                                  │  characters  │
│ oauth_token_grants│                                                  │  (existing)  │
│ ciphertext, nonce │                                                  └──────┬───────┘
│ key_version       │                                                         │
│ expires_at        │                                             ┌───────────▼──────────┐
└───────────────────┘                                             │ external_actor_      │
                                                                  │ mappings (existing)  │
  ┌─────────────────────┐   ┌────────────────────────┐            └──────────────────────┘
  │ discord_users       │   │ role_capability_       │
  │ (existing, Discord  │   │ mappings               │      ┌───────────────────────────┐
  │  facts only)        │   │ guild_id, role_id,     │      │ reconciliation_jobs       │
  ├─────────────────────┤   │ capability, protected  │      │ id UUID PK                │
  │ discord_guild_      │   │ UQ(guild,role,cap)     │      │ kind, state, attempts     │
  │ memberships         │   └────────────┬───────────┘      │ lease_owner, lease_exp    │
  │ observed_at ← N-09  │                │                  │ request_key U             │
  ├─────────────────────┤   ┌────────────▼───────────┐      │ snapshot_id FK            │
  │ discord_membership_ │   │ role_capability_       │      │ scope_fingerprint         │
  │ roles               │   │ mapping_events         │      └────────────┬──────────────┘
  └─────────────────────┘   │ (append-only)          │                   │
                            └────────────────────────┘      ┌────────────▼──────────────┐
  ┌─────────────────────┐   ┌────────────────────────┐      │ reconciliation_job_results│
  │ oauth_transactions  │   │ auth_rate_limits       │      │ bounded summary           │
  │ state_hash, pkce    │   │ (bucket, window_start) │      └───────────────────────────┘
  │ expires_at, consumed│   └────────────────────────┘
  └─────────────────────┘
```

Existing Phase 2 tables not redrawn: `foundry_snapshots`, `snapshot_imports`,
`sheet_row_mappings`, `platform_initialization`, `submission_admissions`,
`idempotency_keys`, `audit_events`. Phase 3 adds columns to two of them and
changes none of their semantics.

## 3. Conventions inherited, not reinvented

From ADR 0003, ADR 0005 and the existing tables:

- UUID primary keys assigned at row creation; idempotency comes from mapping and
  unique constraints, never from a client-chosen id.
- `TIMESTAMPTZ` everywhere, UTC, `server_default=now()` where the row's creation
  is the event.
- Discord snowflakes as `BIGINT` with `> 0` check constraints.
- Explicit `ON DELETE` on every foreign key: `RESTRICT` where history references
  the row, `CASCADE` only where the child is meaningless without its parent.
- `version` integer columns for optimistic concurrency on mutable aggregates.
- Check constraints for closed vocabularies, matching the Python enum exactly.
- Partial unique indexes for "at most one active X" rules — the pattern
  `character_access` already uses.
- Append-only tables are listed in `APPEND_ONLY_TABLES` and protected by the
  trigger introduced in **migration 0002**, plus a runtime role holding only
  `SELECT, INSERT`.

## 4. `platform_accounts`

**Owner:** P3.1. **Writer:** the authentication service and the identity-migration
command. **Reader:** every authorization decision.

| Column | Type | Null | Rule |
|---|---|---|---|
| `id` | UUID | no | PK, assigned at creation |
| `status` | VARCHAR(20) | no | `active` \| `suspended` \| `closed`. Check-constrained |
| `is_protected_admin` | BOOLEAN | no | default `false`. Marks the Server Administrator account (OD-24) |
| `display_label` | VARCHAR(80) | yes | Operator-facing label only. **Never** used for matching (N-16) |
| `created_at` / `updated_at` | TIMESTAMPTZ | no | |
| `version` | INTEGER | no | default 0, `>= 0` |

Constraints:

- `CHECK (status IN ('active','suspended','closed'))`
- Partial unique index `uq_platform_accounts_one_protected_admin` on
  `(is_protected_admin)` `WHERE is_protected_admin` — **exactly one** protected
  administrator account can exist. A second one is a lockout hazard and a
  privilege-escalation surface.
- A `BEFORE UPDATE` trigger refuses clearing `is_protected_admin` and refuses
  setting `status <> 'active'` on the protected account. Losing the protected
  account through an ordinary administrative mistake is the failure OD-24 exists
  to prevent.

Deletion policy: **none**. Accounts are `closed`, never deleted, because audit
attribution references them (`RESTRICT`). A privacy-driven erasure is a separate,
documented Data Owner procedure outside the application (plan §9.4).

Access patterns: by `id` (session resolution, every request); by
`is_protected_admin` (break-glass, rare).

## 5. `external_identities`

**Owner:** P3.1. This is the table OD-43 turns on.

| Column | Type | Null | Rule |
|---|---|---|---|
| `id` | UUID | no | PK |
| `platform_account_id` | UUID | no | FK → `platform_accounts.id` `ON DELETE RESTRICT` |
| `provider_key` | VARCHAR(120) | no | See §5.1 |
| `subject` | VARCHAR(255) | no | The provider's immutable subject. For Discord, the snowflake as a canonical decimal string |
| `state` | VARCHAR(20) | no | `active` \| `retired` |
| `linked_at` | TIMESTAMPTZ | no | |
| `linked_by_account_id` | UUID | yes | FK → `platform_accounts.id` `RESTRICT`. Null when self-linked at first login |
| `last_authenticated_at` | TIMESTAMPTZ | yes | |
| `retired_at` | TIMESTAMPTZ | yes | |
| `retired_reason` | TEXT | yes | |
| `audit_correlation_id` | UUID | no | |

Constraints:

- **`UNIQUE (provider_key, subject)` covering retired rows as well.** This is the
  exactness requirement of delivery plan §9.2. Covering retired rows additionally
  prevents a retired subject from being re-linked to a *different* account, which
  is the subject-reuse takeover in threat model T-06.
- `CHECK (state IN ('active','retired'))`,
  `CHECK ((state = 'retired') = (retired_at IS NOT NULL))`.
- `CHECK (provider_key ~ '^[a-z0-9]+(:[\x21-\x7e]+)?$')`.
- `CHECK (length(trim(subject)) > 0)`.
- Partial index `ix_external_identities_active` on `(platform_account_id)`
  `WHERE state = 'active'` for the "does this account still have a usable
  identity?" check that unlink performs (§9.5 of the delivery plan).

**No unique constraint on any display name, username or email**, and no such
column exists on this table at all. The absence is the control: a column that does
not exist cannot become a matching key (N-16, OD-42).

Deletion policy: **never deleted**, only retired. Historical audit attribution
resolves through this table after a provider is retired (§6.3).

### 5.1 The provider key

`provider_key` must unambiguously bind the configured issuer:

| Provider kind | `provider_key` | Binding rule |
|---|---|---|
| Discord | `discord` | The subject namespace is Discord's global snowflake space. Configuration additionally pins the client id; a mismatch is a startup refusal, not a runtime fallback |
| OIDC (future, requires its own approved package) | `oidc:<issuer>` where `<issuer>` is the exact `iss` value from the provider's discovery document | Compared byte-for-byte at every authentication. A changed issuer is a **different** provider key and therefore a different identity, never a silently migrated one |

Startup refuses to run if a configured provider's key is not in the accepted set,
so a typo cannot create a shadow namespace in which two subjects collide.

## 6. Attribution, and the append-only problem

### 6.1 The finding

`audit_events`, `foundry_snapshots` and `snapshot_imports` are in
`APPEND_ONLY_TABLES`. **Migration 0002** installs the `reject_history_mutation()`
trigger function and a `<table>_append_only` `BEFORE UPDATE OR DELETE` trigger on
each of the three, refusing both **even for the schema owner**, so an accidental
repair is *"a visible act of DDL rather than a quiet row edit"*. (Migration 0005
is the submission-admission fence and installs a different trigger. Earlier
revisions of this package attributed the append-only trigger to 0005; that was
wrong and is corrected throughout.)

A naive identity migration would add `actor_platform_account_id` and backfill it.
**That backfill is an `UPDATE` on an append-only table and the database will refuse
it.** Dropping the trigger to run it would be the single most damaging thing this
package could do to the platform's integrity story.

### 6.1.1 The second half of the finding, which the first revision of this
document missed

Adding a permissive new check is not sufficient, because a **restrictive old one
is still standing**. Migration 0001 created:

```sql
CONSTRAINT ck_audit_events_human_action_has_an_actor CHECK (
    actor_discord_user_id IS NOT NULL
    OR actor_capability IN ('service_principal', 'system')
)
```

Check constraints are conjunctive. A Discord-independent human event — the
break-glass administrator repairing a capability mapping during a Discord outage,
which is the entire purpose of ADR 0010 D8 — carries `actor_capability =
'platform_administrator'`, a non-null `actor_platform_account_id` and a **null**
`actor_discord_user_id`. It satisfies the new constraint and violates the old one,
so the insert fails and the emergency action cannot be recorded. Because
SM-03 puts the session insert and its audit event in one transaction, *the
emergency login itself would fail*. The design as first written did not deliver
the availability half of OD-43 at all.

There is an **application-level copy of the same rule**, and it would raise first:
`application/audit.py` defines `UNATTENDED_CAPABILITIES = {SERVICE_PRINCIPAL,
SYSTEM}` and `AuditEvent.__post_init__` refuses any other capability without an
`actor_discord_user_id`, with the comment *"They match the
`human_action_has_an_actor` check constraint."* Changing the database without
changing that guard would leave the platform refusing in Python instead of in SQL.
P3.1 changes both in the same revision, or neither.

### 6.2 The decisions

1. **Historical audit rows are not rewritten.** Ever. No `UPDATE`, no backfill, no
   trigger suspension, at any stage.
2. **The legacy constraint is replaced by an account-aware one**, by explicit,
   visible DDL in a committed migration — the same class of deliberate act as
   migration 0004's `ADD COLUMN`, and the opposite of a quiet row edit.
3. **The replacement is strictly weaker than what it replaces**, so no existing
   row can be invalidated by it and no row needs to be read to know that.
4. **Each of the three tables is treated on its own evidence.** They do not have
   the same shape and are not given the same treatment.

### 6.2.1 The three tables, as they actually are

Read from migrations 0001, 0002 and 0004 rather than assumed.

| Table | Legacy attribution constraint | Effect on account attribution | P3.1 action |
|---|---|---|---|
| `audit_events` | `ck_audit_events_human_action_has_an_actor` (0001): `actor_discord_user_id IS NOT NULL OR actor_capability IN ('service_principal','system')` | **Blocking.** A Discord-independent human event is illegal today | **Replace** (§6.3), plus the `application/audit.py` guard |
| `foundry_snapshots` | **None.** `received_by_discord_user_id` is nullable with an `ON DELETE RESTRICT` FK and no attribution check whatever. The constraints that exist — `ck_foundry_snapshots_received_via` and `ck_foundry_snapshots_module_submission_names_its_principal`, `(received_via = 'foundry_module') = (submitted_by_principal IS NOT NULL)` — are about the **channel of custody**, not about a human | Not blocking. A row that names no Discord user is already legal, and 0004 explains why: *"the supervised bootstrap has no interactive user"* | Add the nullable column and its FK. **Change no constraint.** A "must name someone" rule would be false of legitimate supervised-bootstrap rows |
| `snapshot_imports` | **None.** `actor_discord_user_id` is nullable; `ck_snapshot_imports_actor_capability` limits capability to `guild_council`, `platform_administrator`, `system` and says nothing about attribution | Not blocking, and **weaker than `audit_events`**: a human-capability import row with no actor at all is legal today | Add the nullable column and its FK, **and add** a new `NOT VALID` attribution check that binds new rows only (§6.4) |

The `foundry_snapshots` row is the reason the prompt's instruction not to assume a
common shape matters: the naive symmetric fix — one constraint applied to all
three — would have introduced an invariant that the platform's own supervised
bootstrap path violates.

### 6.3 The design — `audit_events`

New column, unchanged history, replaced constraint. Ordering inside the revision
is load-bearing and is stated as such.

```sql
-- P3.1 stage A, one transaction, schema owner, no row is read or written.

ALTER TABLE audit_events
    ADD COLUMN actor_platform_account_id UUID;                     -- all-null, no rewrite

ALTER TABLE audit_events
    ADD CONSTRAINT fk_audit_events_actor_platform_account_id_platform_accounts
    FOREIGN KEY (actor_platform_account_id) REFERENCES platform_accounts (id)
    ON DELETE RESTRICT
    NOT VALID;

-- 1. The wider rule goes in FIRST, so the table is never less constrained than
--    it is today, not even for the duration of one statement.
ALTER TABLE audit_events
    ADD CONSTRAINT ck_audit_events_human_action_has_an_attribution CHECK (
        actor_platform_account_id IS NOT NULL
        OR actor_discord_user_id IS NOT NULL
        OR actor_capability IN ('service_principal', 'system')
    ) NOT VALID;

-- 2. Only then is the narrower rule withdrawn. Between the two statements both
--    are in force; at no instant is an unattributed human row insertable.
ALTER TABLE audit_events
    DROP CONSTRAINT ck_audit_events_human_action_has_an_actor;
```

Four properties, each stated so a reviewer can check it rather than trust it:

- **No existing row is read, locked for write, updated or deleted.** `ADD COLUMN`
  with no default is a catalogue change in PostgreSQL 11 and later;
  `ADD CONSTRAINT … NOT VALID` and `DROP CONSTRAINT` are catalogue changes. Row
  triggers do not fire for DDL, so `audit_events_append_only` is neither
  suspended, dropped nor evaded — **it is simply never reached**, which is a
  materially different statement from "it is worked around".
- **The replacement is implied by what it replaces.** `A ⟹ (X ∨ A)` for any `X`.
  Every row that satisfied `ck_audit_events_human_action_has_an_actor` satisfies
  `ck_audit_events_human_action_has_an_attribution`. This is a proof, not a
  measurement, and it is why the swap is safe on a database P3.0 has never
  inspected.
- **Both machine cases survive.** `service_principal` (the Foundry module's
  submissions) and `system` (bootstrap, importers, scheduled work) remain legal
  with both attribution columns null, exactly as today.
- **An unattributed human action is still refused.** `guild_council`,
  `platform_administrator`, `character_owner`, `dm` and `guild_member` all require
  one of the two attribution columns. The rule was not relaxed; its subject was
  widened from *a Discord user* to *an identified person*.

Locks: both `ALTER TABLE` statements take a brief `ACCESS EXCLUSIVE` lock for a
catalogue update and no scan. P3.1 sets `lock_timeout` on the migration session so
a long-running reader defers the revision rather than queueing behind it.

**Validation is a separate, optional, later revision.** `NOT VALID` is enough for
correctness — PostgreSQL enforces a `NOT VALID` check on every insert and update
regardless — so nothing depends on it. When it is run:

```sql
ALTER TABLE audit_events VALIDATE CONSTRAINT ck_audit_events_human_action_has_an_attribution;
ALTER TABLE audit_events VALIDATE CONSTRAINT fk_audit_events_actor_platform_account_id_platform_accounts;
```

Both are guaranteed to succeed by the implication above and by the new column
being all-null in history, and both are **read-only**: `VALIDATE CONSTRAINT` takes
`SHARE UPDATE EXCLUSIVE`, scans, and modifies no row, so it fires no row trigger
and cannot violate the append-only guarantee. This corrects the previous
revision's claim that validation was impossible; it is possible and safe, it is
merely not required.

**Downgrade**, stated honestly. The revision reverses as:

```sql
ALTER TABLE audit_events
    ADD CONSTRAINT ck_audit_events_human_action_has_an_actor CHECK (
        actor_discord_user_id IS NOT NULL
        OR actor_capability IN ('service_principal', 'system')
    ) NOT VALID;                          -- NOT VALID is required, see below
ALTER TABLE audit_events DROP CONSTRAINT ck_audit_events_human_action_has_an_attribution;
ALTER TABLE audit_events DROP CONSTRAINT fk_audit_events_actor_platform_account_id_platform_accounts;
ALTER TABLE audit_events DROP COLUMN actor_platform_account_id;
```

The legacy constraint is restored `NOT VALID` because by then the table may
contain account-attributed rows written after the upgrade, and a validating `ADD
CONSTRAINT` would scan, find them, and fail — leaving the downgrade half-applied.
`NOT VALID` restores the *rule* without asserting a *history* that is no longer
true. Dropping the column discards the account attribution of any row written
after the upgrade; those rows keep their capability, action, payload and
correlation id, and the audit trail loses attribution rather than losing the
event. A downgrade after production break-glass use is therefore a decision with a
data consequence, and P3.1's revision docstring must say so where an operator will
read it.

### 6.4 The design — `snapshot_imports` and `foundry_snapshots`

| Table | Change |
|---|---|
| `snapshot_imports` | add nullable `actor_account_id` UUID FK → `platform_accounts` `RESTRICT` (`NOT VALID`), **and** the new check below |
| `foundry_snapshots` | add nullable `received_by_account_id` UUID FK → `platform_accounts` `RESTRICT` (`NOT VALID`). No check constraint is added, changed or dropped |

```sql
ALTER TABLE snapshot_imports
    ADD CONSTRAINT ck_snapshot_imports_import_has_an_attribution CHECK (
        actor_account_id IS NOT NULL
        OR actor_discord_user_id IS NOT NULL
        OR actor_capability = 'system'
    ) NOT VALID;
```

This one is a **strengthening**, not a replacement: there is nothing to drop,
because no attribution rule exists on this table today. It closes the gap that a
`guild_council` import row may currently name nobody.

It must **never** be `VALIDATE`d, and the reason is different from the
`audit_events` case and worth keeping separate in a reader's mind: there is no
old constraint whose truth implies the new one, so P3.0 cannot prove from the
schema alone that every historical row satisfies it, and P3.0 has not inspected
production data and must not. `NOT VALID` binds new writes; the past is left
exactly as it was found. If a later package wants the guarantee for history, it
measures first and decides then.

`foundry_snapshots` gets no attribution check for the reason in §6.2.1: a
supervised-bootstrap row that names no human is a legitimate row, and migration
0004 already records why. The existing `received_via` / `submitted_by_principal`
pairing is untouched.

**Runtime grants are unchanged.** `GRANT SELECT, INSERT ON audit_events,
foundry_snapshots, snapshot_imports` is table-level and covers columns added
later, and `infra/postgresql/runtime-grants.sql.tmpl` keeps its `REVOKE UPDATE,
DELETE, TRUNCATE` on all three. No new grant is required by this section, and none
is given.

### 6.5 Reading historical attribution

**Reading historical attribution** is a resolved join, not a rewrite:

```sql
COALESCE(
  ae.actor_platform_account_id,
  (SELECT ei.platform_account_id FROM external_identities ei
    WHERE ei.provider_key = 'discord'
      AND ei.subject = ae.actor_discord_user_id::text)
)
```

This is why external identities are retired rather than deleted (§5): the join
must keep working after a provider is retired, which is delivery plan §9.5's
*"historical audit attribution remains readable after provider retirement"*.

Cost, stated honestly: the correlated subquery is a per-row lookup on a unique
index. For a page of at most 100 audit rows (N-21) that is at most 100 index
probes, which is acceptable. It is bounded because the pagination is bounded.

### 6.6 What must be proved, against a real PostgreSQL

The constraint swap is the one place in this package where a design error would
be discovered in production as *"the emergency login does not work"*. It
therefore carries named tests rather than a general assurance. All are
`automated (database)` and are specified in
[`phase-3-test-traceability.md`](phase-3-test-traceability.md) §11.

| Test | Proves |
|---|---|
| TC-AUD-09 | **Old Discord-attributed history remains readable and unchanged.** Rows seeded before the revision are byte-identical after it — same count, same ids, same `actor_discord_user_id`, `actor_capability`, `payload`, `occurred_at` — and `xmin` is unchanged, which is the strongest available evidence that no row was rewritten |
| TC-AUD-10 | **New account attribution inserts succeed**, in both forms: an ordinary-provider event (`guild_council`, account set, Discord null) and a **break-glass** event (`platform_administrator`, account set, Discord null) |
| TC-AUD-11 | **An unattributed human action is rejected** — both columns null with a human capability — by the database constraint, and separately by `application/audit.py`'s account-aware guard |
| TC-AUD-12 | **System and service-principal actions remain valid** with both attribution columns null |
| TC-AUD-13 | **Append-only denial still holds after the swap:** `UPDATE` and `DELETE` on `audit_events` are refused for the restricted runtime role (no grant) and for the owner role (the 0002 trigger), including an `UPDATE` that only sets the new column |
| TC-AUD-14 | `VALIDATE CONSTRAINT` succeeds on a database seeded with legacy-shaped rows and modifies nothing |
| TC-MIG-14 | `upgrade → downgrade → upgrade` of the constraint-swap revision leaves an identical schema and identical data, and the downgrade restores the legacy constraint `NOT VALID` |
| TC-MIG-15 | The **constraint inventory** of all three append-only tables equals the inventory documented in §6.2.1, so a later migration cannot quietly reintroduce a Discord-only attribution rule |
| TC-BG-15 | End to end: a break-glass session performs an allowed mapping repair with Discord entirely unavailable, and **both** the session row and its audit event commit |

## 7. `character_access` — the authorization-bearing migration

**Owner:** P3.2. Existing table; the mechanics of moving it are in the migration
contract. The **target shape**:

| Column | Change |
|---|---|
| `platform_account_id` | **new**, UUID, FK → `platform_accounts` `ON DELETE RESTRICT`, `NOT NULL` after stage B |
| `granted_by_account_id` | **new**, UUID, FK → `platform_accounts` `RESTRICT`, `NOT NULL` after stage B |
| `discord_user_id` | retained through stage C as a read-only shadow; dropped in stage D |
| `granted_by_discord_user_id` | same |

Indexes rebuilt on the account column, preserving every existing invariant:

| Existing index | Target |
|---|---|
| `uq_character_access_one_active_link (character_id, discord_user_id) WHERE active` | `(character_id, platform_account_id) WHERE active` |
| `uq_character_access_one_active_owner (character_id) WHERE active AND access_kind='owner'` | unchanged — it never referenced the user column (OD-37) |
| `uq_character_access_one_active_default_per_user (discord_user_id) WHERE active AND default_character` | `(platform_account_id) WHERE active AND default_character` |

Both index sets exist simultaneously during stages B–C, which is what makes the
cutover reversible: the old invariant is still enforced while the new one is.

Everything else about the table — the `revocation_state` pairing, the
`revoked_after_grant` and `expiry_after_grant` checks, the non-blank reason, the
required `audit_correlation_id`, the deliberate absence of a `guild_council`
access kind (OD-37 §3) — is carried forward **verbatim**.

## 8. `role_capability_mappings` and the lockout guard

**Owner:** P3.2. Stores the mapping from stable Discord role snowflakes to platform
capabilities (OD-18: *"the website stores only the mapping from stable Discord role
IDs to platform capabilities"*).

| Column | Type | Null | Rule |
|---|---|---|---|
| `id` | UUID | no | PK |
| `guild_id` | BIGINT | no | `> 0` |
| `role_id` | BIGINT | no | `> 0` |
| `capability` | VARCHAR(30) | no | Same closed vocabulary as `audit_events.actor_capability` |
| `protected` | BOOLEAN | no | default `false` |
| `active` | BOOLEAN | no | default `true` |
| `created_by_account_id` | UUID | no | FK `RESTRICT` |
| `created_under_auth_method` | VARCHAR(20) | no | The creating session's `sessions.auth_method`. Recorded for audit |
| `created_under_scope` | VARCHAR(24) | no | `full` \| `emergency_continuity` — the creating session's **administrator scope** (§8.1). This is the column the escalation guard keys on |
| `provenance` | VARCHAR(24) | no | `ordinary` \| `emergency_continuity`. Derived, and enforced by check to be derived, from `created_under_scope` and `ratified_at` |
| `ratified_at` | TIMESTAMPTZ | yes | Set once, by R-38, when a full-scope administrator on an ordinary-provider session adopts an emergency-created mapping |
| `ratified_by_account_id` | UUID | yes | FK `RESTRICT` |
| `created_at` / `revoked_at` | TIMESTAMPTZ | | |
| `revoked_by_account_id` | UUID | yes | FK `RESTRICT` |
| `revoked_under_auth_method` | VARCHAR(20) | yes | |
| `revoked_under_scope` | VARCHAR(24) | yes | `full` \| `emergency_continuity` |
| `reason` | TEXT | no | non-blank |
| `audit_correlation_id` | UUID | no | |

Constraints:

- `UNIQUE (guild_id, role_id, capability) WHERE active` — partial, so a revoked
  mapping stays as history and re-mapping inserts a new row, exactly as
  `character_access` does.
- `CHECK (capability IN (…))`, matching `ActorCapability` minus `system` and
  `service_principal` — a Discord role can never map to a machine capability.
- `CHECK (created_under_scope IN ('full','emergency_continuity'))`,
  `CHECK (provenance IN ('ordinary','emergency_continuity'))`,
  `CHECK (created_under_auth_method IN ('discord_oauth','webauthn','recovery_grant'))`.
- **`CHECK (created_under_scope = 'full' OR capability = 'platform_administrator')`**
  — the N-67 allowlist, in the database. A continuity-scoped caller cannot insert
  a `guild_council`, `dm`, `character_owner` or `guild_member` mapping, whatever
  the application believes about its own capability set.
- **`CHECK (revoked_under_scope IS NULL OR revoked_under_scope = 'full' OR
  capability = 'platform_administrator')`** — the same allowlist on the
  subtractive operation.
- `CHECK ((revoked_at IS NULL) = (revoked_under_scope IS NULL))`,
  `CHECK ((revoked_at IS NULL) = (revoked_by_account_id IS NULL))`.
- **`CHECK ((created_under_scope = 'emergency_continuity' AND ratified_at IS NULL)
  = (provenance = 'emergency_continuity'))`** — provenance is not an independent
  fact an application can set as it likes; it is exactly *"created under a
  continuity scope and not yet ratified"*.
- `CHECK ((ratified_at IS NULL) = (ratified_by_account_id IS NULL))`,
  `CHECK (ratified_at IS NULL OR ratified_at >= created_at)`.
- **`BEFORE UPDATE OR DELETE` trigger refusing any change to a row where
  `protected` is true**, and refusing `UPDATE` that sets `protected` on or off.
- **`BEFORE INSERT` trigger refusing a second protected row.**
- **`BEFORE UPDATE` trigger permitting exactly one `provenance` transition**,
  `emergency_continuity → ordinary`, only when `ratified_at` and
  `ratified_by_account_id` are set in the same statement, and refusing the
  reverse direction and any re-ratification. Ratification is a one-way door, so
  a mapping cannot be laundered back and forth to obscure where it came from.

### 8.1 The escalation the first revision left open, and the guard that closes it

**The finding.** R-33 as first written let a break-glass session create *any*
role-capability mapping, and TC-BG-05 treated that success as expected on the
argument that the emergency session's own capability set stays
`{platform_administrator}`. That argument answers the wrong question. The attack
does not need the emergency session to hold Council; it needs the emergency
session to **arrange** for a later ordinary session to hold it:

```text
compromised BG session
  └─ R-33: map role X (which the attacker holds) → guild_council
       └─ log in through Discord as an ordinary member holding role X
            └─ capability resolution returns {guild_council}: no short-circuit
               applies, because auth_method is now discord_oauth
                 └─ R-46: apply an import
```

Every individual control held. The emergency session never held Council, the
capability short-circuit never fired incorrectly, N-65 never let a break-glass
session near R-46. The authority was laundered through a durable row instead.

**A narrower allowlist alone does not close it either**, and this is the part
worth stating carefully. Confining a break-glass session to creating
`platform_administrator` mappings still permits:

```text
BG ─ maps role X → platform_administrator ─▶ ordinary login as administrator
                                              └─ R-33 again, this time as a
                                                 fully-privileged `A`, mapping
                                                 role X → guild_council
```

The second hop is an ordinary administrator doing an ordinary administrator's
job (threat model T-53), so no rule about *break-glass sessions* can see it. The
guard therefore has to travel with the mapping rather than with the session.

**The guard: continuity scope is provenance-carrying.**

1. Every mapping records the **administrator scope** of the session that created
   it. A session's administrator scope is `emergency_continuity` when its
   `auth_method` is not `discord_oauth`, **or** when every active mapping
   conferring `platform_administrator` on it has `provenance =
   'emergency_continuity'`. Otherwise it is `full`.
2. A mapping created under `emergency_continuity` has `provenance =
   'emergency_continuity'` and may name only `platform_administrator` (N-67,
   enforced by check constraint above).
3. Administrator capability held *only* through emergency-provenance mappings is
   itself continuity-scoped. The property is transitive by construction, so the
   second hop above resolves to `emergency_continuity` too and R-33 refuses the
   `guild_council` mapping exactly as it did for the break-glass session.
4. The way out is **ratification (R-38)**: an administrator whose authority does
   not derive from an emergency mapping — in practice the holder of the protected
   bootstrap mapping, which is inserted by migration and is `full` by definition —
   adopts the emergency-created mapping on an ordinary-provider session. Only then
   does it become `ordinary`, and only then does the authority it confers become
   full-scope.

The invariant, in one sentence a reviewer can test:

> No sequence of mapping changes that begins in a break-glass session and passes
> through any number of ordinary logins yields Council, character or import
> authority, until a full-scope administrator ratifies.

**Three independent controls, deliberately redundant**, because the prompt's
instruction not to rely on the short-circuited capability set is exactly right:

| # | Control | Where | Fails safe if |
|---|---|---|---|
| 1 | The application service resolves the caller's administrator scope and refuses a disallowed capability before any write | `application/authorization.py` + the mapping service | The route layer is bypassed |
| 2 | `CHECK (created_under_scope = 'full' OR capability = 'platform_administrator')` | PostgreSQL | The application is wrong, or a future service forgets |
| 3 | N-65's route surface refuses a continuity-scoped session everywhere outside identity/capability administration and audit reads | Route layer | Either of the above is bypassed |

Control 2 is the one that does not depend on the session at all: it depends on
what is being written. That is why it exists.

**Every attempt is recorded**, permitted or refused, in
`role_capability_mapping_events` with `auth_method`, `scope`, `outcome`
(`applied` \| `refused`), refusal code and correlation id. A refusal that leaves
no trace is indistinguishable afterwards from an attack that never happened.

### 8.2 Exactly which mapping operations a continuity-scoped caller may perform

Stated exhaustively, with the continuity need each one serves. Anything not in
this table is refused `403` with the typed code `emergency_scope_refused`.

| Operation | Permitted | Why administrator continuity needs it |
|---|---|---|
| Create `(guild, role, platform_administrator)` | **Yes** | The failure this exists for: the Discord role carrying administrator authority has been deleted and recreated with a new snowflake, or the guild was rebuilt, so the protected bootstrap mapping points at a role nobody can hold. Without this, restoring administrator access requires database-owner action outside the application |
| Revoke a **non-protected** mapping whose capability is `platform_administrator` | **Yes** | Administrator authority was granted to a role that is compromised or mis-assigned, and no ordinary-provider administrator can log in to withdraw it. Revocation is subtractive and can confer nothing |
| Create or revoke a mapping naming `guild_council` | No | It is the escalation in §8.1. Council authority is game-governance authority (OD-24, OD-43); emergency access exists to restore administration, not to change who governs |
| Create or revoke a mapping naming `dm`, `character_owner` or `guild_member` | No | Character and game authority, for the same reason. `dm` grants no Phase 3 web capability today, which makes it a quiet way to pre-position one for Phase 8 |
| Any change to the protected bootstrap mapping | No | Refused by the 0002-style trigger for **every** caller, ordinary administrators included (OD-24). Continuity does not need it: the protected row is what continuity is anchored to |
| Ratify an emergency-created mapping (R-38) | No | Ratification is the boundary between emergency and ordinary authority. A continuity-scoped caller ratifying its own mapping would be the whole guard, self-cancelled |
| Any `character_access` grant, revoke or default change (R-25–R-27) | No | Already refused by N-65 and the route matrix; restated here so the set is complete |
| Any identity link or unlink (R-36, R-37) | No | Already refused; converting a temporary authentication into a permanent one is the same class of laundering |
| Any import, preview, apply or folder selection (R-41…R-46) | No | Already refused by N-65 |

The honest residual: a break-glass session **can** cause a role it controls to
carry continuity-scoped administrator capability after an ordinary login. That is
not an escalation — `platform_administrator` reaches no Council, character or
import route, and the continuity scope confines it further — but it is a
*persistence* gain, and it is recorded as residual risk RR-13 rather than
described away. The compensating controls are that the emergency session is the
only way to reach it, every step is in the append-only mapping-event table, and
ratification by a full-scope administrator is required before that authority
becomes ordinary.

The protected bootstrap row — guild `1052698198180892733`, role
`1124405581298552933`, capability `platform_administrator` — is inserted by the
migration itself, not by the application, and cannot be revoked, replaced, demoted
or shadowed (OD-24, delivery plan §9.6). Capability resolution is a **union** over
active mappings, so adding rows can never subtract the administrator capability;
the trigger covers removal; between them there is no application path to lockout.

The migration inserts it with `created_under_scope = 'full'`, `provenance =
'ordinary'` and `created_under_auth_method = 'discord_oauth'`. It is the anchor
of §8.1's ratification path: because it is `ordinary` by construction and cannot
be edited, there is always exactly one mapping in the database whose authority
does not derive from an emergency action.

`role_capability_mapping_events` is an append-only companion (added to
`APPEND_ONLY_TABLES`) recording every attempted change including refusals, so the
audit of capability administration does not depend on the mutable table. Its
columns:

| Column | Rule |
|---|---|
| `id` UUID PK, `occurred_at` TIMESTAMPTZ | |
| `mapping_id` UUID | The row the attempt concerned; null for a create that was refused before a row existed |
| `operation` VARCHAR(20) | `create` \| `revoke` \| `ratify`, check-constrained |
| `outcome` VARCHAR(12) | `applied` \| `refused`, check-constrained |
| `refusal_code` VARCHAR(40) | `emergency_scope_refused`, `protected_mapping`, `duplicate_active_mapping`, `unknown_capability`, `mapping_limit` (N-62). Non-null exactly when `outcome = 'refused'` |
| `guild_id`, `role_id` BIGINT, `capability` VARCHAR(30) | The attempted subject, recorded even for a refusal |
| `actor_account_id` UUID | FK `RESTRICT` |
| `auth_method` VARCHAR(20), `scope` VARCHAR(24) | The acting session's method and administrator scope (§8.1) |
| `reason` TEXT, `correlation_id` UUID | |

`CHECK ((outcome = 'refused') = (refusal_code IS NOT NULL))`. Recording the
attempted `capability` on a refusal is deliberate: *"a break-glass session tried
to map a role to Council"* is precisely the sentence an incident review needs,
and it exists nowhere else if the refusal writes only a counter.

**Bootstrap ordering hazard, stated:** the protected mapping is inserted by
migration, but the protected *account* is created the first time the Server
Administrator authenticates or by C-03 enrollment. Until then, `is_protected_admin`
is unset and break-glass has no account to authenticate. P3.1's operator
documentation must therefore establish the protected account and enroll two
credentials (N-13) **before** the portal is exposed. Recorded as RAID assumption
A-05, and checked at startup by S-15.

## 9. Session, credential and provider tables

### 9.1 `sessions`

| Column | Type | Null | Rule |
|---|---|---|---|
| `id` | UUID | no | PK. **Never** the cookie value |
| `token_hash` | BYTEA(32) | no | `UNIQUE`. SHA-256 of a 256-bit random token; the token itself is in the cookie and nowhere else |
| `platform_account_id` | UUID | no | FK `RESTRICT` |
| `auth_method` | VARCHAR(20) | no | `discord_oauth` \| `webauthn` \| `recovery_grant` |
| `created_at` | TIMESTAMPTZ | no | |
| `last_seen_at` | TIMESTAMPTZ | no | |
| `idle_expires_at` | TIMESTAMPTZ | no | N-06 / N-15 |
| `absolute_expires_at` | TIMESTAMPTZ | no | N-07 / N-15 |
| `revoked_at` | TIMESTAMPTZ | yes | |
| `revocation_reason` | VARCHAR(40) | yes | `logout` \| `rotation` \| `privilege_change` \| `operator` \| `expired` \| `session_limit` |
| `rotated_from_session_id` | UUID | yes | FK → `sessions.id` `RESTRICT`; **unique where not null** (one successor per predecessor), and composite-foreign-keyed with `platform_account_id`, `auth_method` and `oauth_transaction_id` so a rotation cannot cross an account, a method or a login (added 2026-08-14, OD-44 §8) |
| `oauth_transaction_id` | UUID | yes | FK → `oauth_transactions.id` `RESTRICT`; required for `discord_oauth`, null for other methods; unique among the sessions a completion creates. N-08 rotation **carries it forward** unchanged |
| `privilege_fingerprint` | BYTEA(32) | no | SHA-256 over the sorted capability set + guild membership. A change forces rotation (N-08) |
| `client_ip_hash` | BYTEA(32) | yes | Salted hash; for abuse investigation without storing addresses (plan §9.4) |
| `user_agent_digest` | BYTEA(32) | yes | Same |

Constraints: `CHECK (absolute_expires_at > created_at)`,
`CHECK (idle_expires_at <= absolute_expires_at)`,
`CHECK ((revoked_at IS NULL) = (revocation_reason IS NULL))`,
`CHECK (auth_method IN (…))`,
`CHECK ((auth_method = 'discord_oauth') = (oauth_transaction_id IS NOT NULL))`,
and `UNIQUE (oauth_transaction_id) WHERE rotated_from_session_id IS NULL`. Index
on `(platform_account_id)` `WHERE revoked_at
IS NULL AND absolute_expires_at > now()` is not possible (`now()` is not immutable),
so the index is on `(platform_account_id, absolute_expires_at)` and the predicate
is applied in the query.

**Rotation is insert + revoke, never an in-place id change**, so a stolen cookie
value is dead the instant rotation happens and the chain remains auditable through
`rotated_from_session_id`.

#### Liveness is enforced by the statement, not by the constraints (added 2026-08-15)

Liveness is a comparison against `now()`, so PostgreSQL cannot express it
declaratively: `now()` is not immutable, which is the same reason the partial
index above is not possible. **No constraint on this table establishes that a
session has not expired.** `CHECK (idle_expires_at <= absolute_expires_at)`
relates the two bounds to each other and says nothing about either against the
current time, and `revoked_at IS NULL` establishes only that nobody has *ended*
the session — an expired row stays unrevoked until some read observes it and
marks it.

Each of the two operations that continues a session therefore carries liveness in
the single conditional statement that performs its write. Both were corrected
after review found them describing a liveness they did not test:

| Operation | Enforcing statement | Corrected |
|---|---|---|
| Rotation (`SessionRepository.rotate()`) | `SELECT … FROM sessions WHERE id = :id AND revoked_at IS NULL AND idle_expires_at > :now AND absolute_expires_at > :now AND NOT EXISTS (successor) FOR UPDATE` — the locked read; the successor insert and predecessor revocation follow in the same transaction | 2026-08-14 |
| Idle refresh (`SessionRepository.touch()`) | `UPDATE sessions SET last_seen_at = :now, idle_expires_at = LEAST(:now + make_interval(secs => CASE auth_method WHEN … THEN … END), absolute_expires_at) WHERE id = :id AND auth_method IN (…) AND revoked_at IS NULL AND idle_expires_at > :now AND absolute_expires_at > :now RETURNING id, last_seen_at, idle_expires_at, absolute_expires_at` — the `CASE` and the `IN` list are generated by walking `AuthMethod` and classifying each member with `session_class_of()`, so the durations are bind parameters from configuration and never literals in the adapter, and the two configured numbers come from a `SessionPolicy` the repository **derived** from its `SessionSettings` rather than from anything a caller supplied | 2026-08-15 (amended 2026-08-15, second and third session-lifetime reviews and the idle-policy-construction review) |

Three properties of those statements are load-bearing:

1. **Both comparisons are strict.** Equality at either bound is expired, matching
   resolution's `<=` refusal. An inclusive comparison would grant a session whose
   window ends exactly now one further window.
2. **The chain-wide absolute lifetime.** `absolute_expires_at` appears in neither
   `SET` clause. A rotation inherits the predecessor's value under the row lock,
   and an idle refresh clamps to it without writing it. One login therefore has
   one absolute bound, however many times it is refreshed or rotated — N-07 for an
   ordinary session, N-15's "no extension beyond the absolute bound" for a
   break-glass one.
3. **The idle duration follows the row's own `auth_method`** — N-06 for
   `discord_oauth`, N-15 for `webauthn` and `recovery_grant`.

   *Amended 2026-08-15 (second session-lifetime review).* This paragraph
   previously read "the application selects it from the persisted method and the
   statement verifies that method, so the duration and the row cannot be paired
   incorrectly by either layer." **That was false**, and the falsehood is the
   reason for this amendment: the statement's `auth_method = :expected_auth_method`
   predicate compared a *method* against the row and had no view of the `idle`
   duration passed beside it. Supplying a break-glass row's **correct** method
   together with N-06's sixty minutes matched the row and extended its idle window
   to the emergency absolute bound. An equality predicate on one argument does not
   validate a second, independent argument.

   The duration is no longer an argument at any layer. `SessionIdlePolicy` is what
   the repository is constructed with, and the `CASE auth_method` inside the
   conditional write selects from it using the column on the row being written.

   *Amended again 2026-08-15 (third session-lifetime review).* The paragraph
   above previously continued "— a complete, validated method-to-window mapping
   built from `SessionSettings` and injected once at the composition root — …
   There is therefore no supported call shape in which a method and a duration
   can be paired at all, correctly or otherwise." **The conclusion was false as
   written**, because it reasoned about *calls* and the pairing had moved into
   *construction*: `SessionIdlePolicy` was a frozen dataclass whose generated
   constructor took `tuple[tuple[AuthMethod, timedelta], ...]`, and
   `SessionIdlePolicy(tuple((m, timedelta(minutes=60)) for m in AuthMethod))` is
   complete, duplicate-free and positive. A repository constructed with it
   selected sixty minutes for a persisted WebAuthn or recovery-grant row, and
   N-15's fifteen-minute idle limit was bypassed again, up to the sixty-minute
   emergency absolute bound.

   The policy now has **no public constructor**: `__init__` refuses every call,
   the only supported factory is `from_settings(SessionSettings)`, and the
   method-to-window mapping is derived inside the class from
   `AuthMethod.is_break_glass`. `SessionSettings` remains the sole source of the
   two numbers — validated at load against N-06's and N-15's ceilings — and the
   policy owns only the *classification*: Discord OAuth derives the configured
   ordinary value and both break-glass methods derive the configured emergency
   value, for every pair of values the configuration contract accepts, including
   an ordinary window shorter than the emergency one. There is no supported shape
   at any layer, call or construction, in which an `AuthMethod` and a `timedelta`
   are named together. One policy instance is built at the composition root and
   injected into both `SessionRepository` and `SessionService`; the service
   previously derived a second one from settings, which production happened to
   make equivalent.

   *Amended a fourth time 2026-08-15 (idle-policy-construction review).* The
   paragraph above is retained as history and its central claim — "there is no
   supported shape at any layer, call or construction, in which an `AuthMethod`
   and a `timedelta` are named together" — **was false in two ways it did not
   consider.** (F1) `from_settings()` validated only positivity, and
   `SessionSettings` was a public frozen dataclass with no construction-time
   validation, so `SessionSettings(..., emergency_idle_minutes=60, ...)` was an
   accepted object and the policy built from it gave both break-glass methods
   sixty minutes. Closing the policy's constructor was beside the point while the
   numbers it read were unconstrained. (F2) The refresh statement was generated by
   iterating the policy's public, overridable `__iter__`, so a subclass inheriting
   the supported factory replaced the SQL's mapping while `for_method()` went on
   reporting fifteen minutes. Alongside them, (F3) `SessionService` accepted a
   policy beside the repository and required no relationship between them, so
   correct wiring at the two production sites was a convention rather than an
   invariant.

   The correction is a change of shape, not a further guard.
   **`SessionIdlePolicy` is deleted.** `SessionSettings` enforces the accepted
   register (N-04, N-06, N-07, N-15, N-66) in `__post_init__`, so an
   out-of-register instance cannot exist however it was built.
   `SessionRepository(connection, settings=…)` **derives** a `SessionPolicy` — five
   numbers with fixed roles, no mapping, no `__iter__` — reading each configured
   value exactly once, and owns it; nothing accepts a pre-built policy, so a
   subclass has nowhere to go. The `CASE` branches are generated by walking
   `AuthMethod` and asking `session_class_of()`, an explicit table in
   `application/web/capabilities.py`, so an authentication method nobody
   classified refuses at import and at repository construction rather than
   inheriting a window by inference. `SessionService(sessions=…, …)` reads its
   bounds from that repository and has no policy argument, so a graph with two
   independently configured bounds sources is not constructible. Neither the SQL
   nor the lifetime guarantees above change.

   **Corrected again 2026-08-15 (session-policy numeric-validation remediation).**
   "Reading each configured value exactly once" is worth something only if the one
   read is validated *completely*, and it was not. The two gates shared the
   `SESSION_CEILINGS` bounds and each stated independently what a value may **be**:
   `SessionSettings.__post_init__` required an actual `int`, never a `bool`, while
   the derivation gate restated the rule as `value < 1` and `value > ceiling`.
   `float("nan")` makes both comparisons false, so a non-finite
   `max_sessions_per_account` survived derivation and `len(live) >= maximum`
   became false for every live-session count — **N-66 revoked nothing.** Both gates
   now call one definition, `session_policy_problem`/`session_policy_problems` in
   `application/web/config.py`, which lives beside the ceilings table: the accepted
   type is an `int` and never a `bool`, which refuses floats as a class —
   integral-looking, fractional, infinite and NaN alike. There is deliberately no
   second copy of the rule, because the restatement is what drifted.

   The `auth_method IN (…)` predicate beside it refuses a row whose
   method the policy does not govern; no reachable row has one, because
   `ck_sessions_auth_method` admits exactly the three the policy covers, and it is
   present because the alternative failure is silent (an unmatched `CASE` yields
   `NULL`, and `LEAST` discards `NULL`).

A zero-row result from either statement is a **refusal** — `SessionRotationRefused`
or `SessionTouchRefused` — and writes nothing at all. Distinguish the three
layers when reading this section: the **database** enforces liveness in the
conditional statement itself, and enforces the bounds' relation to each other and
the rotation-chain shape by constraint; **trusted configuration** owns the
numeric policy, which reaches the statement as bind parameters derived from
validated settings and is applied by the persisted method rather than by any
caller; the **application service**
raises the typed refusals; and no **P3.1 HTTP route** calls `touch()` yet, so the
refusal handling described here is a contract the P3.2 request path must meet, not
behaviour P3.1 exercises in production. Note in particular that no check
constraint establishes liveness — `idle_expires_at <= absolute_expires_at` relates
the two bounds to each other and neither of them to `now`.

**Why the uniqueness is scoped to non-rotated rows** (implementation detail of
OD-44, migration 0009). A rotation creates a **new** session row for the same
login. An unscoped `UNIQUE (oauth_transaction_id)` would make that row impossible:
the check constraint requires a transaction id for `discord_oauth`, and the only
correct one is already taken by the row being rotated away from. Rotating a
Discord OAuth session would then be impossible and N-08 would silently stop
protecting the platform's main authentication method. Scoping the index to
`rotated_from_session_id IS NULL` restricts uniqueness to exactly the rows a
*completion* can create, which is the set OD-44's guarantee is about: one
consumed transaction can still never yield a second session from a second
completion, and the check constraint still refuses any unbound `discord_oauth`
row, rotated or not.

**Added 2026-08-14 (OD-44 §8 condition, migration 0009): the rotation chain is
linear, and that is what makes the scoping above safe.** The predicate permits
rotated rows to share a transaction id, so the set allowed to share it must be
exactly one linear chain per login. Three further declarations in `sessions`
establish that, and none of them depends on the application:

| Object | Rule it makes a database property |
|---|---|
| `UNIQUE (rotated_from_session_id) WHERE rotated_from_session_id IS NOT NULL` | At most one successor per predecessor: a chain cannot branch, so one login can never have two live descendants |
| `FOREIGN KEY (rotated_from_session_id, platform_account_id, auth_method) REFERENCES sessions (id, platform_account_id, auth_method)` | A rotation's account and authentication method are its predecessor's |
| `FOREIGN KEY (rotated_from_session_id, oauth_transaction_id) REFERENCES sessions (id, oauth_transaction_id)` | A rotation's OAuth binding is its predecessor's, so a row cannot be *labelled* a rotation in order to carry another login's transaction id past the root-session index |

Both keys are `MATCH SIMPLE`, so each is satisfied without a lookup when any
referencing column is null. That is the wanted behaviour rather than a tolerated
gap: a root session (`rotated_from_session_id IS NULL`) has no predecessor to
agree with, and a break-glass rotation (`oauth_transaction_id IS NULL`) is exempt
from the binding key while the account-and-method key still holds it to its
predecessor and the check constraint still refuses it a transaction id. A
`discord_oauth` rotation cannot shed its binding by nulling the column, because
the check constraint would then demand a different `auth_method` and the
account-and-method key refuses that. `MATCH FULL` was rejected: it would require
all-null-or-all-non-null and would make break-glass rotation impossible.

Two composite `UNIQUE` keys — `(id, platform_account_id, auth_method)` and
`(id, oauth_transaction_id)` — exist solely as the targets those foreign keys
require. `id` is the primary key, so both are trivially unique.

**"Only a live, unrotated predecessor may be rotated" is not declarative**, because
liveness is a `now()` comparison. It is enforced in the single transactional
repository operation `SessionRepository.rotate()`: the predecessor is read
`FOR UPDATE` with `revoked_at IS NULL`, the successor is inserted from that locked
row's own account, method and binding, and the predecessor is revoked — in one
transaction. Two concurrent rotations meet at the row lock; the loser
re-evaluates after the winner commits, matches zero rows and receives a typed
refusal. No trigger is used.

**CSRF token derivation (N-17), and why nothing is stored:** the synchronizer token
is `base64url(HMAC-SHA256(csrf_signing_key, session_id))`, recomputed for each
render and compared in constant time. It is session-bound and rotates with the
session because the session id changes on rotation. It is one-way, so a database
read never yields a usable token, and there is no second column to keep in sync.

Retention: revoked and expired rows are deleted after 30 days by the same
opportunistic cleanup as N-31. Sessions are not audit records; the audit events
`auth.login.*` and `auth.logout` are. That distinction is what makes the OD-44
rollback affordable: a schema change that has to remove `discord_oauth` session
rows ends logins and loses no history.

**Rollback consequence of the binding** (migration 0009). The binding cannot be
reconstructed for a session created while the column did not exist, so revision
0009 refuses to apply while any `discord_oauth` session row exists, and states
the remedy — `DELETE FROM sessions WHERE auth_method = 'discord_oauth'` — in the
refusal. Revoking those rows is **not** sufficient: the check constraint is
evaluated over every row, and a revoked row is still a row. Downgrading past 0009
and re-upgrading therefore costs every Discord OAuth login in progress, and
nothing else.

### 9.2 `oauth_transactions`

| Column | Rule |
|---|---|
| `id` UUID PK | Referenced by the `__Host-fb_login_txn` cookie |
| `state_hash` BYTEA(32) `UNIQUE` | SHA-256 of the state; **the state itself is never stored** |
| `pkce_verifier_ciphertext` BYTEA, `nonce` BYTEA(12), `key_version` SMALLINT | The verifier must be *recoverable* to complete the exchange, so it is **encrypted**, not hashed (§9.2.1) |
| `return_path` VARCHAR(255) | A path from the server-side allowlist; checked again on use |
| `provider_key` VARCHAR(120) | The provider the browser was sent to. **Compared inside the completion claim** from 2026-08-14 (OD-44 §8.1): the claim matches only when the provider being completed is the one recorded here, so a consumed transaction cannot be spent by another provider's verified result |
| `created_at`, `expires_at` | N-04 |
| `consumed_at` TIMESTAMPTZ | Single use |
| `completion_claimed_at` TIMESTAMPTZ | Set once, after provider verification, in the same transaction as the unique bound session and success audit. The claiming statement is `UPDATE … SET completion_claimed_at = :now WHERE id = :id AND consumed_at IS NOT NULL AND completion_claimed_at IS NULL AND provider_key = :provider_key RETURNING id`; zero rows is a refusal |
| `client_ip_hash` BYTEA(32) | For N-18 attribution |

`CHECK (expires_at > created_at)`, `CHECK (return_path LIKE '/%' AND return_path
NOT LIKE '//%')` — the second half of that check is what stops a
protocol-relative `//evil.example` from ever being stored, let alone redirected to.
Rows are deleted 24 hours after expiry — **except** a row a session still names.
`sessions.oauth_transaction_id` is `RESTRICT`, and a session outlives its
transaction by design (N-07's twelve hours against N-04's ten minutes), so the
purge meets referenced rows in *ordinary* operation. It therefore skips them by
predicate rather than attempting and failing, and they become deletable once the
sessions naming them are cleaned up under §9.1's 30-day retention. `RESTRICT`
remains the backstop for any deletion written without that predicate: a session
whose origin row had been removed would be a session nobody could trace back to a
login, and that is refused rather than merely avoided.

`CHECK ((pkce_verifier_ciphertext IS NULL) = (nonce IS NULL))` and
`CHECK (consumed_at IS NULL OR pkce_verifier_ciphertext IS NULL)` — a consumed
transaction has no verifier left, and the database says so rather than the
application remembering to. Also
`CHECK (completion_claimed_at IS NULL OR consumed_at IS NOT NULL)`. There is no
reverse session-id column on this table; `sessions.oauth_transaction_id` is the
single authoritative relationship.

### 9.2.1 The verifier: encrypted, transaction-bound, and gone after one use

Stated in full because an earlier revision of the route contract said the
verifier was hashed, which contradicted this table and describes a flow that
cannot complete: a hash cannot be sent to Discord, and PKCE requires sending the
original verifier at the code exchange. Every contract in this package now says
the same thing:

| Value | Storage | Why |
|---|---|---|
| `state` | **Hashed** (SHA-256), compared in constant time | It is only ever compared. Storing it in the clear would add a stealable value with no use for it |
| PKCE `code_verifier` | **Encrypted** (AES-256-GCM, versioned key, §9.5's boundary), decrypted once at the callback | It must be *presented* to the provider. Encryption is the weakest protection that still permits that, and it is the same approved authenticated-encryption boundary the OAuth tokens use — one key-management story, not two |

The GCM **additional authenticated data** binds `(oauth_transactions.id,
key_version, provider_key)`. A ciphertext copied from one transaction row into
another therefore fails to authenticate and raises, rather than decrypting into a
verifier that would complete somebody else's exchange. Key material is
`WEB_TOKEN_ENCRYPTION_KEYS` (configuration contract §2), versioned so a rotation
does not invalidate in-flight logins.

**Recovery and erasure are one statement**, which is what makes "exactly once"
a database property rather than a coding convention:

```sql
WITH claimed AS (
    SELECT id, pkce_verifier_ciphertext, nonce, key_version, return_path, provider_key
      FROM oauth_transactions
     WHERE id = $1 AND consumed_at IS NULL AND expires_at > now()
       FOR UPDATE
)
UPDATE oauth_transactions t
   SET consumed_at = now(),
       pkce_verifier_ciphertext = NULL,
       nonce = NULL
  FROM claimed c
 WHERE t.id = c.id
RETURNING c.pkce_verifier_ciphertext, c.nonce, c.key_version, c.return_path, c.provider_key;
```

The CTE returns the values as they were *before* the update, so the callback gets
the verifier it needs while the row is emptied of it in the same statement. Under
`READ COMMITTED`, a second concurrent callback blocks on `FOR UPDATE`, re-checks
`consumed_at IS NULL` when the lock is released, matches zero rows, and is
refused. Replay, race and retry all end in the same place, and after any of them
the ciphertext is gone.

Retention: the ciphertext is erased **at consumption**; the row is deleted 24
hours after expiry; an unconsumed transaction's ciphertext therefore lives at most
N-04 + 24 hours, and only in encrypted form. The verifier is never written to a
log, an audit payload, a response body, a redirect URL or an error message —
audit records carry the transaction id and nothing from inside it (N-25).

### 9.3 `webauthn_credentials`

| Column | Rule |
|---|---|
| `id` UUID PK | The identifier that appears in audit records |
| `platform_account_id` UUID FK `RESTRICT` | |
| `credential_id` BYTEA `UNIQUE` | The authenticator's credential id |
| `public_key` BYTEA | COSE public key. **A public key is not a secret**; it is nonetheless restricted, because it is a fingerprint of a specific authenticator |
| `sign_count` BIGINT | Updated on each successful assertion; a decrease is a cloned-authenticator signal and refuses the login |
| `aaguid` UUID, `transports` VARCHAR(60) | Metadata |
| `nickname` VARCHAR(60) | Operator label |
| `created_at`, `created_by_operator` VARCHAR(120), `last_used_at`, `disabled_at` | |

`CHECK (sign_count >= 0)`. No attestation object, no private key, no PIN, no
biometric material is stored — none of it ever leaves the authenticator.
**Enrollment is host-local only** (C-03): there is no web enrollment route, so a
stolen break-glass session cannot enroll an attacker's key.

An application-level invariant, tested rather than constrained: the protected
account must have **at least two** enabled credentials (N-13). It cannot be a
database constraint for the same reason OD-37's *at least one owner* cannot be —
PostgreSQL cannot require a row in another table without a deferred trigger, and
the account must exist before the first credential is enrolled. C-03 refuses to
retire a credential that would leave fewer than two, and the health check (VM-16)
reports the shortfall.

### 9.4 `recovery_grants`

| Column | Rule |
|---|---|
| `id` UUID PK | Named in the audit record |
| `platform_account_id` UUID FK `RESTRICT` | |
| `token_hash` BYTEA(32) `UNIQUE` | SHA-256 of a 256-bit random token. **Not** a password: there is no low-entropy guess to slow down, so a plain SHA-256 over 256 bits of entropy is correct and Argon2 would be cargo cult. The token is printed once by C-01 and stored nowhere |
| `purpose` VARCHAR(40) | `emergency_login` only, check-constrained. Purpose-bound per N-14 |
| `created_at`, `expires_at` | N-14: 10 minutes |
| `created_by_operator` VARCHAR(120) | The host operator, named |
| `consumed_at`, `consumed_session_id` UUID FK `RESTRICT` | |
| `invalidated_at`, `invalidated_reason` | Issuing a new grant invalidates the old (N-61) |
| `attempt_count` INTEGER | N-33's per-grant bound |
| `audit_correlation_id` UUID | |

Constraints: `CHECK (expires_at > created_at)`,
`CHECK ((consumed_at IS NULL) = (consumed_session_id IS NULL))`,
`CHECK (purpose = 'emergency_login')`, and the partial unique index
`uq_recovery_grants_one_live (platform_account_id) WHERE consumed_at IS NULL AND
invalidated_at IS NULL` implementing N-61.

Consumption is one statement:
`UPDATE recovery_grants SET consumed_at = now(), consumed_session_id = $1 WHERE
token_hash = $2 AND consumed_at IS NULL AND invalidated_at IS NULL AND expires_at
> now() RETURNING id`. Replay, expiry and concurrency all resolve to zero rows.

Retention: consumed and expired grants are retained 90 days for investigation,
then deleted. The audit event is permanent; the grant row is not the record.

### 9.5 `oauth_token_grants`

| Column | Rule |
|---|---|
| `id` UUID PK | |
| `external_identity_id` UUID FK `CASCADE` | One live grant per identity |
| `access_token_ciphertext`, `refresh_token_ciphertext` BYTEA | AES-256-GCM |
| `nonce` BYTEA(12), `key_version` SMALLINT | Versioned keys permit rotation without downtime |
| `scopes` VARCHAR(120) | Recorded so a scope widening at the provider is detectable |
| `access_expires_at`, `created_at`, `deleted_at` | N-11 |

The GCM additional authenticated data binds `(id, external_identity_id,
key_version)`, so a ciphertext moved to another row fails to decrypt rather than
decrypting into the wrong identity. Partial unique index on
`(external_identity_id) WHERE deleted_at IS NULL`.

Deletion policy per N-11: deleted on logout, on revocation, and no later than the
session's absolute expiry. A row surviving past that is a defect and the health
check counts them.

Why store them at all: membership and role verification (N-09) requires
`guilds.members.read` on the member's own token, so the platform needs it for as
long as the session lives and no longer.

### 9.6 `auth_rate_limits`

| Column | Rule |
|---|---|
| `bucket` VARCHAR(120) | e.g. `oauth_start:ip:<hash>`; the address is hashed, not stored |
| `window_start` TIMESTAMPTZ | Truncated to the 10-minute window |
| `count` INTEGER | |
| PK `(bucket, window_start)` | One statement increments: `INSERT … ON CONFLICT (bucket, window_start) DO UPDATE SET count = auth_rate_limits.count + 1 RETURNING count` |

N-30 storage, N-31 cleanup. This is the shared-state limiter §7 of the delivery
plan required; it works across `freedom-web` and `freedom-worker` because
PostgreSQL is the shared state both already have.

## 10. Durable reconciliation jobs

**Owner:** P3.3. Implements delivery plan §8 invariants 1–9.

### 10.1 `reconciliation_jobs`

| Column | Type | Rule |
|---|---|---|
| `id` | UUID | PK |
| `kind` | VARCHAR(10) | `preview` \| `apply` (route contract §6.3 finding F-1) |
| `state` | VARCHAR(12) | Exactly N-27's six values |
| `snapshot_id` | UUID | FK → `foundry_snapshots` `RESTRICT` |
| `folder_id` | VARCHAR(64) | |
| `profile_version` | VARCHAR(64) | |
| `scope_fingerprint` | BYTEA(32) | SHA-256 over checksum ‖ folder ‖ profile version ‖ aggregate versions. **The staleness test is one equality comparison**, not a list of separate checks that can drift |
| `requested_by_account_id` | UUID | FK `RESTRICT` |
| `requested_capability` | VARCHAR(30) | The authority claimed at request time; re-resolved at execution |
| `request_key` | VARCHAR(255) | `UNIQUE`. The idempotency key (delivery plan §8.6) |
| `parent_job_id` | UUID | FK → `reconciliation_jobs.id` `RESTRICT`. An `apply` names the `preview` it was confirmed from |
| `attempts` | INTEGER | **The number of claims made against this job.** Incremented by the claim statement and by nothing else. N-43 caps it at 3 |
| `lease_owner` | VARCHAR(120) | Worker instance identity |
| `lease_expires_at` | TIMESTAMPTZ | N-23 |
| `heartbeat_at` | TIMESTAMPTZ | N-23 |
| `queued_at`, `started_at`, `finished_at` | TIMESTAMPTZ | |
| `cancel_requested_at` | TIMESTAMPTZ | Cancellation is a **request**, not a state (N-27 has six states and gains no seventh) |
| `stale_reason`, `failure_code` | VARCHAR(40) | Closed vocabularies matching VM-15 |
| `result_id` | UUID | FK → `reconciliation_job_results.id` `RESTRICT` |
| `correlation_id` | UUID | |
| `version` | INTEGER | Optimistic concurrency |

Constraints and indexes:

- `CHECK (state IN ('queued','running','completed','stale','failed','cancelled'))`
- `CHECK ((state = 'running') = (lease_owner IS NOT NULL))`
- `CHECK ((state IN ('completed','stale','failed','cancelled')) = (finished_at IS NOT NULL))`
- `CHECK ((state = 'completed') = (result_id IS NOT NULL))` — **a job cannot be
  `completed` without a durable result**, which is delivery plan §8.7's *"no state
  named `completed` precedes durable commit"* expressed as a constraint rather
  than as a code review comment.
- `CHECK ((state = 'failed') = (failure_code IS NOT NULL))`
- `CHECK ((state = 'stale') = (stale_reason IS NOT NULL))`
- `CHECK (attempts >= 0 AND attempts <= 3)` (N-43)
- **`CHECK (state <> 'queued' OR attempts < 3)`** — *a queued job always has a
  remaining attempt.* This is the constraint the first revision of this contract
  lacked, and its absence is what let a job strand: the reaper requeued only
  while `attempts < 3`, so a job whose third lease expired stayed `running`
  forever, and a fourth claim would have violated the cap anyway. With this
  constraint the stranded state is not merely avoided by careful code — it is
  unrepresentable, and any statement that would produce it fails loudly
- Partial index `ix_reconciliation_jobs_claimable (queued_at) WHERE state = 'queued'`
  for `FOR UPDATE SKIP LOCKED` claiming.
- Partial unique index
  `uq_reconciliation_jobs_one_live_apply (snapshot_id, folder_id, profile_version)
  WHERE kind = 'apply' AND state IN ('queued','running')` — two concurrent applies
  of the same input cannot both be in flight. The durable
  `uq_snapshot_imports_applied_input` already prevents two from both succeeding;
  this prevents the second from starting and doing 10 seconds of work to discover
  it.

**Claim statement** (the lease of delivery plan §8.3):

```sql
UPDATE reconciliation_jobs SET
    state = 'running', lease_owner = $1, attempts = attempts + 1,
    started_at = COALESCE(started_at, now()),
    lease_expires_at = now() + interval '60 seconds',
    heartbeat_at = now(), version = version + 1
WHERE id = (
    SELECT id FROM reconciliation_jobs
    WHERE state = 'queued'
      AND cancel_requested_at IS NULL
      AND attempts < 3                      -- N-43; redundant with the check
    ORDER BY queued_at                      -- constraint, and kept for that reason
    FOR UPDATE SKIP LOCKED LIMIT 1
) RETURNING *;
```

`SKIP LOCKED` is what makes two workers unable to claim the same attempt. The
platform runs one worker (N-41); the statement is correct for more, which is the
point of using the database as the queue.

`attempts < 3` in the claim predicate is deliberately redundant with
`CHECK (state <> 'queued' OR attempts < 3)`. The constraint makes an exhausted
queued job impossible; the predicate makes the claim *refuse* rather than
*violate* if the constraint is ever dropped or a future revision widens N-43. A
claim that fails a check constraint aborts the worker's transaction; a claim that
matches no row simply moves on.

**Reaper statement** (N-44, every 15 seconds), and the correction at the centre
of this section:

```sql
UPDATE reconciliation_jobs SET
    state         = CASE WHEN attempts < 3 THEN 'queued' ELSE 'failed' END,
    lease_owner   = NULL,
    lease_expires_at = NULL,
    heartbeat_at  = NULL,
    failure_code  = CASE WHEN attempts >= 3 THEN 'attempts_exhausted' END,
    finished_at   = CASE WHEN attempts >= 3 THEN now() END,
    version       = version + 1
WHERE id IN (
    SELECT id FROM reconciliation_jobs
    WHERE state = 'running' AND lease_expires_at < now()
    ORDER BY lease_expires_at
    FOR UPDATE SKIP LOCKED LIMIT 20
) RETURNING id, state, attempts, correlation_id;
```

One statement, two outcomes, no gap between them:

- **`attempts < 3`** — the lease is recoverable, exactly as N-23 requires. The job
  returns to `queued` with a remaining attempt, satisfying the new check
  constraint by construction.
- **`attempts = 3`** — the attempt budget is spent. The job goes **directly** to
  `failed` with `attempts_exhausted`. It does not wait for a fourth claim, which
  the cap forbids; it does not sit in `queued` waiting for a claim that would be
  refused; it does not sit in `running` with nobody running it.

The `CASE` expressions with no `ELSE` yield `NULL` on the requeue branch, which
is what `failure_code` and `finished_at` must be for a non-terminal job — so the
terminal-state check constraints (`(state = 'failed') = (failure_code IS NOT
NULL)` and the `finished_at` pairing) hold on both branches of the same
statement. That is not a coincidence to be preserved by care; if a future edit
breaks it, the constraint rejects the statement.

`FOR UPDATE SKIP LOCKED` in the sub-select is what makes **two concurrent reapers
safe**: each row is transitioned by exactly one of them, and the other skips it
rather than blocking or double-counting. `LIMIT 20` bounds a single reaper pass
so a backlog cannot turn one tick into a long transaction.

The terminal branch writes its audit event — `reconciliation.job_failed`, with the
job id, `attempts_exhausted`, the last lease owner and the job's correlation id —
in the **same transaction**, satisfying delivery plan §8.2's requirement that
append-only audit facts record every terminal outcome. A job may therefore be
failed by a process that never executed it; the event names the job's lease
history rather than pretending the reaper did the work (residual risk RR-14).

**Worker self-abandon.** When a worker hits N-45's 300-second hard cap, or
observes the kill switch, it applies the *same* two-branch logic under its own
lease:

```sql
UPDATE reconciliation_jobs SET
    state = CASE WHEN attempts < 3 THEN 'queued' ELSE 'failed' END,
    lease_owner = NULL, lease_expires_at = NULL, heartbeat_at = NULL,
    failure_code = CASE WHEN attempts >= 3 THEN 'attempts_exhausted' END,
    finished_at  = CASE WHEN attempts >= 3 THEN now() END,
    version = version + 1
WHERE id = $1 AND lease_owner = $2 AND state = 'running';
```

`AND lease_owner = $2` is the whole safety argument: if the reaper has already
acted — because this worker was slow enough to lose its lease — the statement
matches zero rows and the worker exits quietly rather than stamping a stale
verdict on a job somebody else now owns.

**Deterministic failure is not a retry.** A refusal that would recur on every
attempt (`parse_refused`, `artifact_unavailable`) sets `state = 'failed'` with
its own `failure_code` immediately, under the lease-owner predicate, whatever
`attempts` says. Retrying a deterministic refusal three times is 30 seconds of
work to reach the conclusion the first attempt already had.

**Bounded lease-expiry recovery**, stated so the invariant is checkable rather
than asserted: assuming the reaper remains live, an unresponsive worker's expired
claim is recovered within `N-23 + N-44` (60 s lease + 15 s reaper interval), so
three expired claims consume at most 3 × 75 s ≈ 225 s of lease-expiry recovery.
That figure excludes queue waiting, successful execution time and N-45's separate
runtime cap; it is not an unconditional end-to-end job-duration promise. Under
the stated liveness assumption no job remains `running` indefinitely, and
TC-JOB-13 measures the property rather than trusting this paragraph.

### 10.2 `reconciliation_job_results`

| Column | Rule |
|---|---|
| `id` UUID PK | |
| `job_id` UUID FK `CASCADE` | |
| `summary` JSONB | The bounded summary — counts, issue codes, folder identity, checksum, profile version |
| `blocked_entries` JSONB | At most 50 entries, each `{external_actor_id, display_name, issue_code, candidate_character_ids}` |
| `produced_at` TIMESTAMPTZ | |
| `expires_at` TIMESTAMPTZ | N-24: 30 days |

**JSONB justification, because plan §7.3.1 forbids it for authoritative
multi-valued facts.** These two columns fall under the explicit §7.3.1 exceptions:
*"bounded diagnostic or parser metadata used only to explain an import"* and
*"presentation-only caches that are disposable and never authoritative"*. They are
disposable (N-24 deletes them), never read by a calculation, never a source of
authority, and reproducible by re-running the job against the immutable snapshot.
The precedent is `snapshot_imports.summary`, which is already JSON for the same
reason and passed the Phase 2 gate. Every searchable fact — job identity, state,
checksum, folder, profile version, actor, correlation, timestamps — is a typed
column, satisfying §7.3.1's closing requirement.

**Raw bytes are never here.** Delivery plan §8.9: results are bounded summaries and
references. The artifact stays in the restricted store the Phase 2 package built,
reachable by no route.

## 11. Schema decision table

Reading key: *Writer* is the only component permitted to insert or update.
*Retention* is the deletion rule. *PII* marks rows holding personal data under
plan §9.4.

| Table | Owner pkg | PK | Key FKs | Uniqueness | Writer | Reader | Delete policy | Retention | PII | Encrypted / hashed |
|---|---|---|---|---|---|---|---|---|---|---|
| `platform_accounts` | P3.1 | UUID | — | one protected admin (partial) | auth service, C-04/05 | every authz decision | never (status `closed`) | indefinite | label only | — |
| `external_identities` | P3.1 | UUID | account `RESTRICT` | `(provider_key, subject)` incl. retired | auth service, C-04/05 | authz, audit resolution | never (state `retired`) | indefinite | subject | — |
| `oauth_token_grants` | P3.1 | UUID | identity `CASCADE` | one live per identity | auth service | membership refresh | on logout/revocation/absolute expiry | ≤ session absolute expiry (N-11) | yes | AES-256-GCM, versioned key |
| `sessions` | P3.1 | UUID | account `RESTRICT`, self `RESTRICT` | `token_hash` | auth service | every request | 30 days after revoke/expiry | 30 days | ip/ua digests | token hashed (SHA-256) |
| `oauth_transactions` | P3.1 | UUID | — | `state_hash` | auth service | callback | 24 h after expiry; **verifier erased at consumption** | 24 h | ip hash | state hashed (SHA-256); verifier encrypted (AES-256-GCM, AAD-bound to the row) |
| `webauthn_credentials` | P3.1 | UUID | account `RESTRICT` | `credential_id` | C-03 (host-local only) | break-glass login | never (disable instead) | indefinite | no | public key only |
| `recovery_grants` | P3.1 | UUID | account `RESTRICT`, session `RESTRICT` | `token_hash`; one live per account | C-01/C-02 (host-local only) | break-glass login | 90 days after consumption/expiry | 90 days | no | token hashed (SHA-256) |
| `auth_rate_limits` | P3.1 | `(bucket, window_start)` | — | PK | rate limiter | rate limiter | windows > 60 min | 60 min | address hashed | yes |
| `role_capability_mappings` | P3.2 | UUID | accounts `RESTRICT` | `(guild, role, capability) WHERE active` | admin service | capability resolution | never (revoke instead) | indefinite | no | — |
| `role_capability_mapping_events` | P3.2 | UUID | — | — | admin service | audit views | **append-only** | indefinite | actor account | — |
| `character_access` (migrated) | P3.2 | UUID | account `RESTRICT`, character `CASCADE` | 3 partial indexes (§7) | Council service, C-05 | authz, member reads | never (revoke instead) | indefinite | no | — |
| `identity_link_proposals` | P3.2 | UUID | character `CASCADE` | `(run_id, character_id)` | C-04 | R-28 | 90 days after run | 90 days | sheet names | — |
| `reconciliation_jobs` | P3.3 | UUID | snapshot `RESTRICT`, account `RESTRICT`, self `RESTRICT` | `request_key`; one live apply per input | job service, worker | Council views | 30 days after terminal (N-24) | 30 days | requester | — |
| `reconciliation_job_results` | P3.3 | UUID | job `CASCADE` | — | worker | Council views | with the job | 30 days | Actor names in blocked entries | — |
| `audit_events` (+column) | P3.1 | existing | +account `RESTRICT` | existing | every service | Council/admin | **append-only, never** | indefinite (OD-23) | actor | — |
| `foundry_snapshots` (+column) | P3.1 | existing | +account `RESTRICT` | existing | submission | Council/admin | **append-only** | indefinite | submitter | — |
| `snapshot_imports` (+column) | P3.1 | existing | +account `RESTRICT` | existing | import service | Council/admin | **append-only** | indefinite | actor | — |

### 11.1 Expected access patterns

| Query | Frequency | Index |
|---|---|---|
| Session by token hash | every request | `sessions.token_hash` unique |
| Account's active identities | every login, every unlink | `ix_external_identities_active` |
| Identity by `(provider, subject)` | every login | the unique constraint |
| Membership + roles for a Discord user | at most every N-09 per active session | existing PKs |
| Capability resolution from role snowflakes | with every membership refresh | `(guild, role, capability) WHERE active` |
| Characters for an account | R-20 | new index `(platform_account_id) WHERE active` |
| Access rows for a character | R-23 | existing `(character_id, …)` partial indexes |
| Claimable job | worker, every N-44 | `ix_reconciliation_jobs_claimable` |
| Audit page | R-49 | existing `ix_audit_events_entity`, plus a new `(occurred_at DESC, id DESC)` for the default cursor order |

The audit ordering index is the one genuinely new cost: an append-only table with
a descending time index takes an extra write per event. It is the price of N-21's
"no unbounded offset scan" and is accepted deliberately.

### 11.2 Runtime role grants

Extending the pattern migrations 0002 and 0005 established, and preserving
`infra/postgresql/runtime-grants.sql.tmpl`'s `REVOKE ALL … FROM PUBLIC`
normalisation for every table added here:

| Grant | Tables |
|---|---|
| `SELECT, INSERT` only | `audit_events`, `foundry_snapshots`, `snapshot_imports`, `role_capability_mapping_events` |
| `SELECT, INSERT, UPDATE` | `sessions`, `oauth_transactions`, `reconciliation_jobs`, `webauthn_credentials`, `recovery_grants`, `character_access`, `role_capability_mappings`, `platform_accounts`, `external_identities` |
| `SELECT, INSERT, UPDATE, DELETE` | `auth_rate_limits`, `oauth_token_grants`, `reconciliation_job_results`, `identity_link_proposals` |
| No grant at all | every Alembic version table; schema ownership stays with the migration role (ADR 0003) |

`DELETE` on `oauth_token_grants` is required by N-11 and is the reason it is not in
the append-only set. That is a deliberate trade: token deletion is a privacy
control that outranks the forensic value of keeping the row.

## 12. Traceability

| Design element | Source | Test |
|---|---|---|
| Stable internal account | OD-43; delivery plan §9.1 | TC-ID-01 |
| `(provider, subject)` uniqueness incl. retired | delivery plan §9.2; §9.5 | TC-ID-03, TC-ID-04 |
| No name/email matching column exists | N-16; OD-42 | TC-ID-05 (structural) |
| Append-only history is never rewritten | plan §6.5; migration 0002 | TC-AUD-04, TC-AUD-09, TC-AUD-13 |
| Account-attributed human events are legal without rewriting history | OD-43; ADR 0010 D5; §6.3 | TC-AUD-10…TC-AUD-14, TC-MIG-14, TC-MIG-15 |
| Break-glass mapping repair cannot confer Council/import authority | OD-24; OD-43; D-3; §8.1 | TC-BG-05a…05e, TC-CAP-08, TC-CAP-09 |
| A job always reaches a terminal state | delivery plan §8.3, §8.7; N-43 | TC-JOB-05, TC-JOB-13, TC-JOB-15, TC-JOB-16 |
| Protected admin mapping cannot be lost | OD-24; delivery plan §9.6 | TC-CAP-03, TC-CAP-04 |
| One active owner / one active default | OD-37 | TC-ACC-02, TC-ACC-03 |
| No `completed` before durable result | delivery plan §8.7 | TC-JOB-06 |
| One durable effect under concurrency | plan §6.5; delivery plan §8.6 | TC-JOB-08 |
| JSONB confined to §7.3.1 exceptions | plan §7.3.1 | TC-STRUCT-03 |
| PostgreSQL semantics preserved; reversible staging | ADR 0003; plan §14 | TC-MIG-06 |
