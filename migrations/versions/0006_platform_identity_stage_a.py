"""Stage A of the identity migration: platform accounts, credentials, sessions.

This is the additive stage of M-1 in
`docs/contracts/phase-3-identity-migration-contract.md` §3, and the schema it
creates is `docs/contracts/phase-3-logical-schema.md` §4, §5, §8 and §9. It does
four things, in this order, and the order is load-bearing:

1. creates the identity, credential, session and rate-limit tables;
2. adds nullable account columns to `character_access` and to the three
   append-only tables, and performs the **`audit_events` constraint swap**;
3. backfills one platform account and one active Discord external identity per
   existing `discord_users` row, and resolves `character_access`; and
4. checks control totals T1–T8 inside its own transaction and **aborts** if any
   disagrees.

## The constraint swap, and why it does not touch history

Migration 0001 created

    CHECK (actor_discord_user_id IS NOT NULL
           OR actor_capability IN ('service_principal', 'system'))

Check constraints are conjunctive, so a Discord-independent human event — the
break-glass administrator repairing a capability mapping during a Discord
outage, which is the entire purpose of ADR 0010 D8 — is **illegal today**: it
carries `platform_administrator`, an account id and a null Discord id. Because
SM-03 commits an emergency session and its audit event in one transaction, that
constraint refuses the emergency login itself.

So the rule is replaced rather than supplemented, and the wider rule is added
**before** the narrower one is dropped. Between the two statements both are in
force; at no instant is an unattributed human row insertable. The replacement is
implied by what it replaces — `A ⟹ (X ∨ A)` for any `X` — so no existing row can
be invalidated by it and none has to be read to know that.

`ADD COLUMN` with no default, `ADD CONSTRAINT … NOT VALID` and `DROP CONSTRAINT`
are catalogue changes. **Row triggers do not fire for DDL**, so the
`audit_events_append_only` trigger from migration 0002 is neither dropped,
disabled nor evaded — it is never reached, which is a materially different
statement from "it is worked around".

The three append-only tables are **not** treated alike, because they are not
alike (schema §6.2.1). `foundry_snapshots` carries no attribution constraint and
gains none: a supervised-bootstrap row that names no human is legitimate, and
migration 0004 records why. `snapshot_imports` carries none either, and gains a
new `NOT VALID` check that binds future rows only.

`application/audit.py`'s `UNATTENDED_CAPABILITIES` guard is a Python copy of the
same rule and changes in the same revision. A guard that refused in Python what
the database now permits would produce the same outage with a different
traceback.

## What a downgrade costs, where an operator will read it

The downgrade restores `ck_audit_events_human_action_has_an_actor` **`NOT
VALID`**, deliberately: by then the table may hold account-attributed rows, and
a validating `ADD CONSTRAINT` would scan, find them and fail, leaving the
downgrade half-applied. `NOT VALID` restores the *rule* without asserting a
*history* that is no longer true.

**Dropping `actor_platform_account_id` discards the attribution of every audit
event written by a break-glass session after this upgrade.** The events survive
with their capability, action, payload and correlation id; their actor becomes
unresolvable. That is a data consequence of the downgrade, not a defect in it,
and it is why §5 of the migration contract requires a restore-tested dump before
each stage runs against a database whose history matters.

## Bootstrap configuration

The protected administrator mapping is inserted **by this migration**, not by the
application, and cannot afterwards be revoked, edited, demoted or shadowed
(OD-24, ADR 0010 D10). It needs the guild and role snowflakes, which are read
from `WEB_DISCORD_GUILD_ID` and `WEB_BOOTSTRAP_ADMIN_ROLE_ID`. Both are
**required**: there is no default, because a default would be a production
identifier compiled into source, and a skipped insert would be a portal with no
anchor for administrator capability.

Revision ID: 0006
Revises: 0005
Create Date: 2026-08-14
"""
from __future__ import annotations

import os
from typing import Sequence
from uuid import uuid4

import sqlalchemy as sa
from alembic import context, op
from sqlalchemy.dialects import postgresql

revision: str = "0006"
down_revision: str | None = "0005"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

#: Added to the append-only set by this revision. `role_capability_mappings`
#: itself is mutable — a mapping is revoked, not deleted — but the *record of
#: every attempt to change one*, refusals included, must not be editable by the
#: service whose behaviour it records.
NEW_APPEND_ONLY_TABLES = ("role_capability_mapping_events",)

#: The capabilities a Discord role may map to: `ActorCapability` minus the two
#: machine capabilities. A Discord role can never map to `system` or
#: `service_principal`, because a human holding a role is not a service.
MAPPABLE_CAPABILITIES = (
    "guild_member",
    "character_owner",
    "dm",
    "guild_council",
    "platform_administrator",
)

_AUTH_METHODS = ("discord_oauth", "webauthn", "recovery_grant")
_ADMIN_SCOPES = ("full", "emergency_continuity")

#: A migration takes brief ACCESS EXCLUSIVE locks for its catalogue changes. A
#: bounded `lock_timeout` makes a long-running reader defer the revision rather
#: than let the revision queue ahead of every other session behind it.
LOCK_TIMEOUT = "5s"


def _bootstrap_identifiers() -> tuple[int, int]:
    """The guild and protected administrator role, from the environment.

    Required rather than defaulted. `.agents/AGENTS.md` forbids production
    identifiers in source, and a migration that silently skipped the insert
    would leave the platform with no mapping anchoring administrator capability —
    the one row §8.1's ratification path depends on being `ordinary` by
    construction.
    """
    missing = [
        name
        for name in ("WEB_DISCORD_GUILD_ID", "WEB_BOOTSTRAP_ADMIN_ROLE_ID")
        if not (os.environ.get(name) or "").strip()
    ]
    if missing:
        raise RuntimeError(
            "Revision 0006 inserts the protected administrator role-capability "
            "mapping and requires " + " and ".join(missing) + ". Set them for "
            "this migration run. There is no default: a default would be a "
            "production identifier in source, and skipping the insert would "
            "leave the portal with no anchor for administrator capability."
        )
    guild = int(os.environ["WEB_DISCORD_GUILD_ID"].strip())
    role = int(os.environ["WEB_BOOTSTRAP_ADMIN_ROLE_ID"].strip())
    if guild <= 0 or role <= 0:
        raise RuntimeError(
            "WEB_DISCORD_GUILD_ID and WEB_BOOTSTRAP_ADMIN_ROLE_ID must be "
            "positive Discord snowflakes."
        )
    return guild, role


#: Prepended to this revision's contribution to an offline (`--sql`) script.
#: Offline mode never connects, so a backfill that has to read `discord_users`
#: and control totals that have to count rows cannot be part of it. Saying so in
#: the script is the whole point: an operator who applies the DDL alone and stops
#: has a schema whose account columns are null, and **stage B refuses loudly**
#: rather than proceeding — which is the safe direction for this to fail in.
OFFLINE_DATA_STEP_NOTICE = """
-- ---------------------------------------------------------------------------
-- REVISION 0006 -- OFFLINE MODE OMITS ITS DATA STEPS
--
-- The DDL below is complete. The following are NOT in this script, because
-- offline mode never opens a connection and each of them has to read rows:
--
--   1. the backfill that creates one platform account and one active Discord
--      external identity per existing `discord_users` row, and resolves
--      `character_access.platform_account_id` / `granted_by_account_id`; and
--   2. control totals T1-T8, which are checked inside the migration's own
--      transaction and abort it on disagreement.
--
-- Applying this script alone therefore leaves `character_access` with null
-- account columns. That state is not silently wrong: revision 0007 counts those
-- rows first and refuses to continue.
--
-- Run `alembic upgrade 0006` ONLINE against the same database to perform the
-- backfill and its control totals. Online mode also verifies which server and
-- database it reached, which this script cannot.
-- ---------------------------------------------------------------------------
"""


def upgrade() -> None:
    guild_id, admin_role_id = _bootstrap_identifiers()
    offline = context.is_offline_mode()

    audit_rows_before: sa.engine.Row | None = None
    connection: sa.Connection | None = None
    if offline:
        op.execute(sa.text(OFFLINE_DATA_STEP_NOTICE))
    else:
        connection = op.get_bind()
        connection.execute(sa.text(f"SET LOCAL lock_timeout = '{LOCK_TIMEOUT}'"))
        # Captured before any statement in this revision runs, so T7 compares the
        # table to itself across the whole swap rather than across part of it.
        audit_rows_before = connection.execute(
            sa.text("SELECT count(*), max(occurred_at) FROM audit_events")
        ).one()

    _create_platform_accounts()
    _create_external_identities()
    _create_oauth_token_grants()
    _create_sessions()
    _create_oauth_transactions()
    _create_webauthn_credentials()
    _create_webauthn_challenges()
    _create_recovery_grants()
    _create_auth_rate_limits()
    _create_role_capability_mappings()
    _create_role_capability_mapping_events()

    _add_character_access_columns()
    _swap_audit_attribution_constraint()
    _add_snapshot_imports_attribution()
    _add_foundry_snapshots_attribution()

    # The protected mapping is emitted in both modes: it is an insert of literal
    # values that reads nothing, and a schema without it has no anchor for
    # administrator capability at all.
    _insert_protected_mapping(guild_id=guild_id, role_id=admin_role_id)

    if connection is not None:
        _backfill_accounts(connection)
        _check_control_totals(connection, audit_rows_before=audit_rows_before)


def downgrade() -> None:
    if not context.is_offline_mode():
        op.get_bind().execute(sa.text(f"SET LOCAL lock_timeout = '{LOCK_TIMEOUT}'"))

    for table in NEW_APPEND_ONLY_TABLES:
        op.execute(f"DROP TRIGGER IF EXISTS {table}_append_only ON {table};")

    # `foundry_snapshots`: column and FK only — no check was added, so none is
    # dropped, and the existing `received_via` pairing is untouched throughout.
    op.drop_constraint(
        op.f("fk_foundry_snapshots_received_by_account_id_platform_accounts"),
        "foundry_snapshots",
        type_="foreignkey",
    )
    op.drop_column("foundry_snapshots", "received_by_account_id")

    op.drop_constraint(
        op.f("ck_snapshot_imports_import_has_an_attribution"),
        "snapshot_imports",
        type_="check",
    )
    op.drop_constraint(
        op.f("fk_snapshot_imports_actor_account_id_platform_accounts"),
        "snapshot_imports",
        type_="foreignkey",
    )
    op.drop_column("snapshot_imports", "actor_account_id")

    op.drop_index("ix_audit_events_occurred_at_desc", table_name="audit_events")

    # The legacy rule comes back NOT VALID. See the module docstring: by now the
    # table may hold account-attributed rows, and a validating ADD CONSTRAINT
    # would scan, find them, and fail — leaving the downgrade half-applied.
    op.execute(
        """
        ALTER TABLE audit_events
            ADD CONSTRAINT ck_audit_events_human_action_has_an_actor CHECK (
                actor_discord_user_id IS NOT NULL
                OR actor_capability IN ('service_principal', 'system')
            ) NOT VALID;
        """
    )
    op.drop_constraint(
        op.f("ck_audit_events_human_action_has_an_attribution"),
        "audit_events",
        type_="check",
    )
    op.drop_constraint(
        op.f("fk_audit_events_actor_platform_account_id_platform_accounts"),
        "audit_events",
        type_="foreignkey",
    )
    op.drop_column("audit_events", "actor_platform_account_id")

    op.drop_constraint(
        op.f("fk_character_access_granted_by_account_id_platform_accounts"),
        "character_access",
        type_="foreignkey",
    )
    op.drop_constraint(
        op.f("fk_character_access_platform_account_id_platform_accounts"),
        "character_access",
        type_="foreignkey",
    )
    op.drop_column("character_access", "granted_by_account_id")
    op.drop_column("character_access", "platform_account_id")

    op.drop_table("role_capability_mapping_events")
    op.execute("DROP TRIGGER IF EXISTS role_capability_mappings_protected ON role_capability_mappings;")
    op.execute("DROP TRIGGER IF EXISTS role_capability_mappings_one_protected ON role_capability_mappings;")
    op.execute("DROP TRIGGER IF EXISTS role_capability_mappings_provenance ON role_capability_mappings;")
    op.execute("DROP FUNCTION IF EXISTS reject_protected_mapping_change();")
    op.execute("DROP FUNCTION IF EXISTS reject_second_protected_mapping();")
    op.execute("DROP FUNCTION IF EXISTS enforce_mapping_provenance_transition();")
    op.drop_table("role_capability_mappings")

    op.drop_table("auth_rate_limits")
    op.drop_table("recovery_grants")
    op.drop_table("webauthn_challenges")
    op.drop_table("webauthn_credentials")
    op.drop_table("oauth_transactions")
    op.drop_table("sessions")
    op.drop_table("oauth_token_grants")
    op.drop_table("external_identities")
    op.execute("DROP TRIGGER IF EXISTS platform_accounts_protected ON platform_accounts;")
    op.execute("DROP FUNCTION IF EXISTS protect_platform_admin_account();")
    op.drop_table("platform_accounts")


# ---------------------------------------------------------------------------
# Table creation
# ---------------------------------------------------------------------------


def _create_platform_accounts() -> None:
    """The identity of a person on this platform (ADR 0010 D1).

    Deletion policy: **none**. An account is `closed`, never deleted, because
    audit attribution references it with `ON DELETE RESTRICT`. A privacy-driven
    erasure is a separate documented Data Owner procedure outside the
    application.
    """
    op.create_table(
        "platform_accounts",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="active"),
        sa.Column(
            "is_protected_admin", sa.Boolean(), nullable=False, server_default="false"
        ),
        # Operator-facing only. **Never** used for matching (N-16): a label that
        # could match would be the name-based linking ADR 0010 D3 forbids.
        sa.Column("display_label", sa.String(80)),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column("version", sa.Integer(), nullable=False, server_default="0"),
        sa.CheckConstraint(
            "status IN ('active', 'suspended', 'closed')",
            name=op.f("ck_platform_accounts_status"),
        ),
        sa.CheckConstraint("version >= 0", name=op.f("ck_platform_accounts_version_non_negative")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_platform_accounts")),
    )
    # Exactly one protected administrator account can exist. A second is both a
    # lockout hazard and a privilege-escalation surface.
    op.create_index(
        "uq_platform_accounts_one_protected_admin",
        "platform_accounts",
        ["is_protected_admin"],
        unique=True,
        postgresql_where=sa.text("is_protected_admin"),
    )
    # Losing the protected account through an ordinary administrative mistake is
    # the failure OD-24 exists to prevent, so the database refuses the mistake
    # rather than the application remembering not to make it.
    op.execute(
        """
        CREATE OR REPLACE FUNCTION protect_platform_admin_account() RETURNS trigger AS $$
        BEGIN
            IF OLD.is_protected_admin AND NOT NEW.is_protected_admin THEN
                RAISE EXCEPTION
                    'the protected administrator flag cannot be cleared through '
                    'the application; it is the anchor of emergency access (OD-24)'
                    USING ERRCODE = 'restrict_violation';
            END IF;
            IF OLD.is_protected_admin AND NEW.status <> 'active' THEN
                RAISE EXCEPTION
                    'the protected administrator account cannot be suspended or '
                    'closed; doing so would disable the emergency route it exists for'
                    USING ERRCODE = 'restrict_violation';
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """
    )
    op.execute(
        """
        CREATE TRIGGER platform_accounts_protected
        BEFORE UPDATE ON platform_accounts
        FOR EACH ROW EXECUTE FUNCTION protect_platform_admin_account();
        """
    )


def _create_external_identities() -> None:
    """One provider identity, unique on `(provider_key, subject)` (ADR 0010 D2).

    **There is no display-name, username or email column, and that absence is
    the control** (N-16, OD-42): a column that does not exist cannot become a
    matching key. `TC-ID-05` asserts the absence structurally so a later
    migration cannot add one without a test failing.
    """
    op.create_table(
        "external_identities",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("platform_account_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("provider_key", sa.String(120), nullable=False),
        sa.Column("subject", sa.String(255), nullable=False),
        sa.Column("state", sa.String(20), nullable=False, server_default="active"),
        sa.Column(
            "linked_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column("linked_by_account_id", postgresql.UUID(as_uuid=True)),
        sa.Column("last_authenticated_at", sa.DateTime(timezone=True)),
        sa.Column("retired_at", sa.DateTime(timezone=True)),
        sa.Column("retired_reason", sa.Text()),
        sa.Column("audit_correlation_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.CheckConstraint(
            "state IN ('active', 'retired')", name=op.f("ck_external_identities_state")
        ),
        sa.CheckConstraint(
            "(state = 'retired') = (retired_at IS NOT NULL)",
            name=op.f("ck_external_identities_retirement_is_dated"),
        ),
        sa.CheckConstraint(
            r"provider_key ~ '^[a-z0-9]+(:[\x21-\x7e]+)?$'",
            name=op.f("ck_external_identities_provider_key_shape"),
        ),
        sa.CheckConstraint(
            "length(trim(subject)) > 0", name=op.f("ck_external_identities_subject_not_blank")
        ),
        sa.ForeignKeyConstraint(
            ["platform_account_id"],
            ["platform_accounts.id"],
            ondelete="RESTRICT",
            name=op.f("fk_external_identities_platform_account_id_platform_accounts"),
        ),
        sa.ForeignKeyConstraint(
            ["linked_by_account_id"],
            ["platform_accounts.id"],
            ondelete="RESTRICT",
            name=op.f("fk_external_identities_linked_by_account_id_platform_accounts"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_external_identities")),
        # Covers retired rows as well. That is the exactness requirement of
        # delivery plan §9.2, and it additionally prevents a retired subject
        # being re-linked to a *different* account — the subject-reuse takeover
        # in threat model T-06.
        sa.UniqueConstraint(
            "provider_key", "subject", name=op.f("uq_external_identities_provider_key_subject")
        ),
    )
    op.create_index(
        "ix_external_identities_active",
        "external_identities",
        ["platform_account_id"],
        postgresql_where=sa.text("state = 'active'"),
    )


def _create_oauth_token_grants() -> None:
    op.create_table(
        "oauth_token_grants",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("external_identity_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("access_token_ciphertext", sa.LargeBinary(), nullable=False),
        sa.Column("refresh_token_ciphertext", sa.LargeBinary()),
        sa.Column("nonce", sa.LargeBinary(), nullable=False),
        sa.Column("refresh_nonce", sa.LargeBinary()),
        sa.Column("key_version", sa.SmallInteger(), nullable=False),
        sa.Column("scopes", sa.String(120), nullable=False),
        sa.Column("access_expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column("deleted_at", sa.DateTime(timezone=True)),
        sa.CheckConstraint("length(nonce) = 12", name=op.f("ck_oauth_token_grants_nonce_length")),
        sa.CheckConstraint(
            "refresh_nonce IS NULL OR length(refresh_nonce) = 12",
            name=op.f("ck_oauth_token_grants_refresh_nonce_length"),
        ),
        sa.CheckConstraint(
            "(refresh_token_ciphertext IS NULL) = (refresh_nonce IS NULL)",
            name=op.f("ck_oauth_token_grants_refresh_pairing"),
        ),
        sa.ForeignKeyConstraint(
            ["external_identity_id"],
            ["external_identities.id"],
            ondelete="CASCADE",
            name=op.f("fk_oauth_token_grants_external_identity_id_external_identities"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_oauth_token_grants")),
    )
    op.create_index(
        "uq_oauth_token_grants_one_live",
        "oauth_token_grants",
        ["external_identity_id"],
        unique=True,
        postgresql_where=sa.text("deleted_at IS NULL"),
    )


def _create_sessions() -> None:
    """Opaque server-side sessions (ADR 0004, ADR 0010; schema §9.1).

    The cookie holds a 256-bit random token; the table holds its SHA-256. The
    session id is **never** the cookie value, so a database read yields nothing
    a browser could present. Rotation is insert + revoke rather than an in-place
    id change, so a stolen cookie is dead the instant rotation happens and the
    chain stays auditable through `rotated_from_session_id`.
    """
    op.create_table(
        "sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("token_hash", sa.LargeBinary(), nullable=False),
        sa.Column("platform_account_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("auth_method", sa.String(20), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "last_seen_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column("idle_expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("absolute_expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True)),
        sa.Column("revocation_reason", sa.String(40)),
        sa.Column("rotated_from_session_id", postgresql.UUID(as_uuid=True)),
        sa.Column("privilege_fingerprint", sa.LargeBinary(), nullable=False),
        sa.Column("client_ip_hash", sa.LargeBinary()),
        sa.Column("user_agent_digest", sa.LargeBinary()),
        sa.CheckConstraint(
            "auth_method IN " + _sql_tuple(_AUTH_METHODS), name=op.f("ck_sessions_auth_method")
        ),
        sa.CheckConstraint(
            "revocation_reason IS NULL OR revocation_reason IN "
            "('logout', 'rotation', 'privilege_change', 'operator', 'expired', 'session_limit')",
            name=op.f("ck_sessions_revocation_reason"),
        ),
        sa.CheckConstraint(
            "absolute_expires_at > created_at", name=op.f("ck_sessions_absolute_after_creation")
        ),
        # The absolute bound is a bound: an idle refresh clamps to it in the
        # update statement, and this constraint is what makes a mistake there
        # fail loudly instead of quietly extending a session past its policy.
        sa.CheckConstraint(
            "idle_expires_at <= absolute_expires_at",
            name=op.f("ck_sessions_idle_within_absolute"),
        ),
        sa.CheckConstraint(
            "(revoked_at IS NULL) = (revocation_reason IS NULL)",
            name=op.f("ck_sessions_revocation_state"),
        ),
        sa.CheckConstraint("length(token_hash) = 32", name=op.f("ck_sessions_token_hash_length")),
        sa.CheckConstraint(
            "length(privilege_fingerprint) = 32",
            name=op.f("ck_sessions_privilege_fingerprint_length"),
        ),
        sa.ForeignKeyConstraint(
            ["platform_account_id"],
            ["platform_accounts.id"],
            ondelete="RESTRICT",
            name=op.f("fk_sessions_platform_account_id_platform_accounts"),
        ),
        sa.ForeignKeyConstraint(
            ["rotated_from_session_id"],
            ["sessions.id"],
            ondelete="RESTRICT",
            name=op.f("fk_sessions_rotated_from_session_id_sessions"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_sessions")),
        sa.UniqueConstraint("token_hash", name=op.f("uq_sessions_token_hash")),
    )
    # `now()` is not immutable, so the "currently live" predicate cannot be in
    # the index. The index carries the columns and the query carries the
    # predicate (schema §9.1).
    op.create_index(
        "ix_sessions_account_expiry", "sessions", ["platform_account_id", "absolute_expires_at"]
    )


def _create_oauth_transactions() -> None:
    """One in-flight OAuth attempt (SM-01; schema §9.2).

    `state` is **hashed**: it is only ever compared, so a plaintext copy would
    be a stealable value with no use for it. The PKCE `code_verifier` is
    **encrypted**: it must be *presented* to the provider at the code exchange,
    so it has to be recoverable, and a hash cannot be sent to Discord. An earlier
    revision of the route contract said both were hashed, which described a flow
    that cannot complete.
    """
    op.create_table(
        "oauth_transactions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("state_hash", sa.LargeBinary(), nullable=False),
        sa.Column("pkce_verifier_ciphertext", sa.LargeBinary()),
        sa.Column("nonce", sa.LargeBinary()),
        sa.Column("key_version", sa.SmallInteger(), nullable=False),
        sa.Column("return_path", sa.String(255), nullable=False),
        sa.Column("provider_key", sa.String(120), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("consumed_at", sa.DateTime(timezone=True)),
        sa.Column("client_ip_hash", sa.LargeBinary()),
        sa.CheckConstraint(
            "expires_at > created_at", name=op.f("ck_oauth_transactions_expiry_after_creation")
        ),
        sa.CheckConstraint(
            "length(state_hash) = 32", name=op.f("ck_oauth_transactions_state_hash_length")
        ),
        # The second half is what stops a protocol-relative `//evil.example`
        # ever being *stored*, let alone redirected to.
        sa.CheckConstraint(
            "return_path LIKE '/%' AND return_path NOT LIKE '//%'",
            name=op.f("ck_oauth_transactions_return_path_is_a_path"),
        ),
        sa.CheckConstraint(
            "(pkce_verifier_ciphertext IS NULL) = (nonce IS NULL)",
            name=op.f("ck_oauth_transactions_verifier_pairing"),
        ),
        # A consumed transaction has no verifier left, and the database says so
        # rather than the application remembering to.
        sa.CheckConstraint(
            "consumed_at IS NULL OR pkce_verifier_ciphertext IS NULL",
            name=op.f("ck_oauth_transactions_consumed_has_no_verifier"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_oauth_transactions")),
        sa.UniqueConstraint("state_hash", name=op.f("uq_oauth_transactions_state_hash")),
    )
    op.create_index("ix_oauth_transactions_expires_at", "oauth_transactions", ["expires_at"])


def _create_webauthn_credentials() -> None:
    """Pre-enrolled break-glass credentials (N-13; schema §9.3).

    No attestation object, no private key, no PIN and no biometric material is
    stored — none of it ever leaves the authenticator. **Enrollment is host-local
    only** (C-03): there is no web enrollment route, so a stolen break-glass
    session cannot enroll an attacker's key.
    """
    op.create_table(
        "webauthn_credentials",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("platform_account_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("credential_id", sa.LargeBinary(), nullable=False),
        sa.Column("public_key", sa.LargeBinary(), nullable=False),
        sa.Column("sign_count", sa.BIGINT(), nullable=False, server_default="0"),
        sa.Column("aaguid", postgresql.UUID(as_uuid=True)),
        sa.Column("transports", sa.String(60)),
        sa.Column("nickname", sa.String(60)),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column("created_by_operator", sa.String(120), nullable=False),
        sa.Column("last_used_at", sa.DateTime(timezone=True)),
        sa.Column("disabled_at", sa.DateTime(timezone=True)),
        sa.CheckConstraint("sign_count >= 0", name=op.f("ck_webauthn_credentials_sign_count")),
        sa.CheckConstraint(
            "length(trim(created_by_operator)) > 0",
            name=op.f("ck_webauthn_credentials_operator_named"),
        ),
        sa.ForeignKeyConstraint(
            ["platform_account_id"],
            ["platform_accounts.id"],
            ondelete="RESTRICT",
            name=op.f("fk_webauthn_credentials_platform_account_id_platform_accounts"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_webauthn_credentials")),
        sa.UniqueConstraint("credential_id", name=op.f("uq_webauthn_credentials_credential_id")),
    )


def _create_webauthn_challenges() -> None:
    """The server-side challenge R-07 mints and R-08 consumes (SM-03).

    **Added by P3.1, and recorded as such.** SM-03 requires "a challenge row with
    an N-04 lifetime", but schema §9 lists no table for it; this is that table.
    The challenge is stored in the clear because a WebAuthn challenge is a public
    nonce that must be handed to the browser and then compared byte-for-byte
    against the authenticator's response — there is nothing here a hash would
    protect, and a hash could not be presented as `expected_challenge`.
    """
    op.create_table(
        "webauthn_challenges",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("challenge", sa.LargeBinary(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("consumed_at", sa.DateTime(timezone=True)),
        sa.Column("client_ip_hash", sa.LargeBinary()),
        sa.CheckConstraint(
            "expires_at > created_at", name=op.f("ck_webauthn_challenges_expiry_after_creation")
        ),
        sa.CheckConstraint(
            "length(challenge) >= 32", name=op.f("ck_webauthn_challenges_length")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_webauthn_challenges")),
        sa.UniqueConstraint("challenge", name=op.f("uq_webauthn_challenges_challenge")),
    )


def _create_recovery_grants() -> None:
    """The host-issued last resort (N-14, N-61; schema §9.4).

    `token_hash` is a plain SHA-256 and that is **correct, not a shortcut**: the
    token is 256 bits of entropy printed once by C-01, so there is no low-entropy
    guess for a slow hash to slow down. Argon2 here would be cargo cult.
    """
    op.create_table(
        "recovery_grants",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("platform_account_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("token_hash", sa.LargeBinary(), nullable=False),
        sa.Column("purpose", sa.String(40), nullable=False, server_default="emergency_login"),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_by_operator", sa.String(120), nullable=False),
        sa.Column("consumed_at", sa.DateTime(timezone=True)),
        sa.Column("consumed_session_id", postgresql.UUID(as_uuid=True)),
        sa.Column("invalidated_at", sa.DateTime(timezone=True)),
        sa.Column("invalidated_reason", sa.String(60)),
        sa.Column("attempt_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("audit_correlation_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.CheckConstraint(
            "expires_at > created_at", name=op.f("ck_recovery_grants_expiry_after_creation")
        ),
        sa.CheckConstraint(
            "(consumed_at IS NULL) = (consumed_session_id IS NULL)",
            name=op.f("ck_recovery_grants_consumption_names_its_session"),
        ),
        # Purpose-bound (N-14): a grant is for emergency login and for nothing
        # else, so a future purpose is a deliberate schema change rather than a
        # string somebody passed.
        sa.CheckConstraint("purpose = 'emergency_login'", name=op.f("ck_recovery_grants_purpose")),
        sa.CheckConstraint(
            "length(token_hash) = 32", name=op.f("ck_recovery_grants_token_hash_length")
        ),
        sa.CheckConstraint("attempt_count >= 0", name=op.f("ck_recovery_grants_attempt_count")),
        sa.CheckConstraint(
            "(invalidated_at IS NULL) = (invalidated_reason IS NULL)",
            name=op.f("ck_recovery_grants_invalidation_state"),
        ),
        sa.CheckConstraint(
            "length(trim(created_by_operator)) > 0",
            name=op.f("ck_recovery_grants_operator_named"),
        ),
        sa.ForeignKeyConstraint(
            ["platform_account_id"],
            ["platform_accounts.id"],
            ondelete="RESTRICT",
            name=op.f("fk_recovery_grants_platform_account_id_platform_accounts"),
        ),
        sa.ForeignKeyConstraint(
            ["consumed_session_id"],
            ["sessions.id"],
            ondelete="RESTRICT",
            name=op.f("fk_recovery_grants_consumed_session_id_sessions"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_recovery_grants")),
        sa.UniqueConstraint("token_hash", name=op.f("uq_recovery_grants_token_hash")),
    )
    # N-61: at most one unconsumed, unexpired grant per account. Two live grants
    # double the window with no operational benefit.
    op.create_index(
        "uq_recovery_grants_one_live",
        "recovery_grants",
        ["platform_account_id"],
        unique=True,
        postgresql_where=sa.text("consumed_at IS NULL AND invalidated_at IS NULL"),
    )


def _create_auth_rate_limits() -> None:
    """The cross-process limiter §7 of the delivery plan required (N-30).

    PostgreSQL is already a required, shared, transactional dependency; adding
    Redis for one counter would not be the smallest justified dependency set.
    The known cost of a fixed window is a 2x burst at the boundary, recorded as
    residual risk RR-03.
    """
    op.create_table(
        "auth_rate_limits",
        sa.Column("bucket", sa.String(120), nullable=False),
        sa.Column("window_start", sa.DateTime(timezone=True), nullable=False),
        sa.Column("count", sa.Integer(), nullable=False, server_default="0"),
        sa.CheckConstraint("count >= 0", name=op.f("ck_auth_rate_limits_count_non_negative")),
        sa.PrimaryKeyConstraint("bucket", "window_start", name=op.f("pk_auth_rate_limits")),
    )
    op.create_index("ix_auth_rate_limits_window_start", "auth_rate_limits", ["window_start"])


def _create_role_capability_mappings() -> None:
    """Stable Discord role snowflake -> platform capability (OD-18; schema §8).

    Three constraints here carry the N-67 administrator-continuity allowlist,
    and the middle one is the whole point of §8.1: **it does not depend on the
    session at all**. It depends on what is being written, so it holds even if
    the application service is wrong, bypassed, or replaced by a future one that
    forgets.
    """
    op.create_table(
        "role_capability_mappings",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("guild_id", sa.BIGINT(), nullable=False),
        sa.Column("role_id", sa.BIGINT(), nullable=False),
        sa.Column("capability", sa.String(30), nullable=False),
        sa.Column("protected", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("active", sa.Boolean(), nullable=False, server_default="true"),
        # Nullable **only** for the protected bootstrap row, which is inserted by
        # this migration at a moment when no platform account exists yet — the
        # accounts table is created empty in the same revision. The check below
        # is what keeps that from becoming a general licence. Recorded as a
        # deviation from schema §8's "Null: no" in the P3.1 submission.
        sa.Column("created_by_account_id", postgresql.UUID(as_uuid=True)),
        sa.Column("created_under_auth_method", sa.String(20), nullable=False),
        sa.Column("created_under_scope", sa.String(24), nullable=False),
        sa.Column("provenance", sa.String(24), nullable=False),
        sa.Column("ratified_at", sa.DateTime(timezone=True)),
        sa.Column("ratified_by_account_id", postgresql.UUID(as_uuid=True)),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column("revoked_at", sa.DateTime(timezone=True)),
        sa.Column("revoked_by_account_id", postgresql.UUID(as_uuid=True)),
        sa.Column("revoked_under_auth_method", sa.String(20)),
        sa.Column("revoked_under_scope", sa.String(24)),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("audit_correlation_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False, server_default="0"),
        sa.CheckConstraint("guild_id > 0", name=op.f("ck_role_capability_mappings_guild_id")),
        sa.CheckConstraint("role_id > 0", name=op.f("ck_role_capability_mappings_role_id")),
        sa.CheckConstraint(
            "capability IN " + _sql_tuple(MAPPABLE_CAPABILITIES),
            name=op.f("ck_role_capability_mappings_capability"),
        ),
        sa.CheckConstraint(
            "created_under_scope IN " + _sql_tuple(_ADMIN_SCOPES),
            name=op.f("ck_role_capability_mappings_created_under_scope"),
        ),
        sa.CheckConstraint(
            "provenance IN ('ordinary', 'emergency_continuity')",
            name=op.f("ck_role_capability_mappings_provenance"),
        ),
        sa.CheckConstraint(
            "created_under_auth_method IN " + _sql_tuple(_AUTH_METHODS),
            name=op.f("ck_role_capability_mappings_created_under_auth_method"),
        ),
        # -------------------------------------------------------------------
        # N-67, in the database. A continuity-scoped caller cannot insert a
        # `guild_council`, `dm`, `character_owner` or `guild_member` mapping,
        # whatever the application believes about its own capability set.
        # -------------------------------------------------------------------
        sa.CheckConstraint(
            "created_under_scope = 'full' OR capability = 'platform_administrator'",
            name=op.f("ck_role_capability_mappings_continuity_create_allowlist"),
        ),
        sa.CheckConstraint(
            "revoked_under_scope IS NULL OR revoked_under_scope = 'full' "
            "OR capability = 'platform_administrator'",
            name=op.f("ck_role_capability_mappings_continuity_revoke_allowlist"),
        ),
        # Provenance is not an independent fact an application may set as it
        # likes; it is exactly "created under a continuity scope and not yet
        # ratified", and this constraint is what makes that definitional.
        sa.CheckConstraint(
            "(created_under_scope = 'emergency_continuity' AND ratified_at IS NULL) "
            "= (provenance = 'emergency_continuity')",
            name=op.f("ck_role_capability_mappings_provenance_is_derived"),
        ),
        sa.CheckConstraint(
            "(ratified_at IS NULL) = (ratified_by_account_id IS NULL)",
            name=op.f("ck_role_capability_mappings_ratification_names_its_actor"),
        ),
        sa.CheckConstraint(
            "ratified_at IS NULL OR ratified_at >= created_at",
            name=op.f("ck_role_capability_mappings_ratified_after_creation"),
        ),
        sa.CheckConstraint(
            "(revoked_at IS NULL) = (revoked_under_scope IS NULL)",
            name=op.f("ck_role_capability_mappings_revocation_names_its_scope"),
        ),
        sa.CheckConstraint(
            "(revoked_at IS NULL) = (revoked_by_account_id IS NULL)",
            name=op.f("ck_role_capability_mappings_revocation_names_its_actor"),
        ),
        sa.CheckConstraint(
            "(active AND revoked_at IS NULL) OR (NOT active AND revoked_at IS NOT NULL)",
            name=op.f("ck_role_capability_mappings_revocation_state"),
        ),
        sa.CheckConstraint(
            "length(trim(reason)) > 0", name=op.f("ck_role_capability_mappings_reason_not_blank")
        ),
        sa.CheckConstraint(
            "created_by_account_id IS NOT NULL OR protected",
            name=op.f("ck_role_capability_mappings_creator_named_unless_bootstrap"),
        ),
        sa.CheckConstraint("version >= 0", name=op.f("ck_role_capability_mappings_version")),
        sa.ForeignKeyConstraint(
            ["created_by_account_id"],
            ["platform_accounts.id"],
            ondelete="RESTRICT",
            name=op.f("fk_role_capability_mappings_created_by_account_id_platform_accounts"),
        ),
        sa.ForeignKeyConstraint(
            ["ratified_by_account_id"],
            ["platform_accounts.id"],
            ondelete="RESTRICT",
            name=op.f("fk_role_capability_mappings_ratified_by_account_id_platform_accounts"),
        ),
        sa.ForeignKeyConstraint(
            ["revoked_by_account_id"],
            ["platform_accounts.id"],
            ondelete="RESTRICT",
            name=op.f("fk_role_capability_mappings_revoked_by_account_id_platform_accounts"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_role_capability_mappings")),
    )
    # Partial, so a revoked mapping stays as history and re-mapping inserts a new
    # row — exactly as `character_access` already does.
    op.create_index(
        "uq_role_capability_mappings_active",
        "role_capability_mappings",
        ["guild_id", "role_id", "capability"],
        unique=True,
        postgresql_where=sa.text("active"),
    )
    op.create_index(
        "ix_role_capability_mappings_resolution",
        "role_capability_mappings",
        ["guild_id", "role_id"],
        postgresql_where=sa.text("active"),
    )

    op.execute(
        """
        CREATE OR REPLACE FUNCTION reject_protected_mapping_change() RETURNS trigger AS $$
        BEGIN
            IF TG_OP = 'DELETE' THEN
                IF OLD.protected THEN
                    RAISE EXCEPTION
                        'the protected administrator mapping cannot be deleted (OD-24)'
                        USING ERRCODE = 'restrict_violation';
                END IF;
                RETURN OLD;
            END IF;
            IF OLD.protected THEN
                RAISE EXCEPTION
                    'the protected administrator mapping cannot be revoked, edited, '
                    'demoted or shadowed by any caller, ordinary administrators '
                    'included (OD-24, ADR 0010 D10)'
                    USING ERRCODE = 'restrict_violation';
            END IF;
            IF NEW.protected AND NOT OLD.protected THEN
                RAISE EXCEPTION
                    'a mapping cannot be promoted to protected after creation; the '
                    'protected row is inserted by migration and by nothing else'
                    USING ERRCODE = 'restrict_violation';
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """
    )
    op.execute(
        """
        CREATE TRIGGER role_capability_mappings_protected
        BEFORE UPDATE OR DELETE ON role_capability_mappings
        FOR EACH ROW EXECUTE FUNCTION reject_protected_mapping_change();
        """
    )
    op.execute(
        """
        CREATE OR REPLACE FUNCTION reject_second_protected_mapping() RETURNS trigger AS $$
        BEGIN
            IF NEW.protected AND EXISTS (
                SELECT 1 FROM role_capability_mappings WHERE protected AND id <> NEW.id
            ) THEN
                RAISE EXCEPTION
                    'exactly one protected administrator mapping may exist; a second '
                    'would give lockout recovery two anchors and no defined winner'
                    USING ERRCODE = 'unique_violation';
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """
    )
    op.execute(
        """
        CREATE TRIGGER role_capability_mappings_one_protected
        BEFORE INSERT ON role_capability_mappings
        FOR EACH ROW EXECUTE FUNCTION reject_second_protected_mapping();
        """
    )
    # Ratification is a one-way door (SM-07). A mapping cannot be pushed back
    # across the boundary to disguise where it came from, and it cannot be
    # ratified twice.
    op.execute(
        """
        CREATE OR REPLACE FUNCTION enforce_mapping_provenance_transition() RETURNS trigger AS $$
        BEGIN
            IF OLD.provenance = 'ordinary' AND NEW.provenance = 'emergency_continuity' THEN
                RAISE EXCEPTION
                    'a mapping cannot move from ordinary back to emergency_continuity; '
                    'provenance records where authority came from and is not editable'
                    USING ERRCODE = 'restrict_violation';
            END IF;
            IF OLD.provenance = 'emergency_continuity' AND NEW.provenance = 'ordinary' THEN
                IF NEW.ratified_at IS NULL OR NEW.ratified_by_account_id IS NULL THEN
                    RAISE EXCEPTION
                        'provenance becomes ordinary only through ratification, which '
                        'must name its time and its full-scope administrator in the '
                        'same statement (R-38)'
                        USING ERRCODE = 'restrict_violation';
                END IF;
            END IF;
            IF OLD.ratified_at IS NOT NULL AND NEW.ratified_at IS DISTINCT FROM OLD.ratified_at THEN
                RAISE EXCEPTION
                    'a mapping is ratified once; a second ratification would let the '
                    'record of who adopted it be rewritten'
                    USING ERRCODE = 'restrict_violation';
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """
    )
    op.execute(
        """
        CREATE TRIGGER role_capability_mappings_provenance
        BEFORE UPDATE ON role_capability_mappings
        FOR EACH ROW EXECUTE FUNCTION enforce_mapping_provenance_transition();
        """
    )


def _create_role_capability_mapping_events() -> None:
    """Every attempt to change a mapping, **including every refusal** (§8.1).

    Recording the attempted `capability` on a refusal is deliberate: "a
    break-glass session tried to map a role to Council" is precisely the sentence
    an incident review needs, and it exists nowhere else if the refusal writes
    only a counter.
    """
    op.create_table(
        "role_capability_mapping_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "occurred_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        # Null for a create that was refused before a row existed.
        sa.Column("mapping_id", postgresql.UUID(as_uuid=True)),
        sa.Column("operation", sa.String(20), nullable=False),
        sa.Column("outcome", sa.String(12), nullable=False),
        sa.Column("refusal_code", sa.String(40)),
        sa.Column("guild_id", sa.BIGINT(), nullable=False),
        sa.Column("role_id", sa.BIGINT(), nullable=False),
        sa.Column("capability", sa.String(30), nullable=False),
        sa.Column("actor_account_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("auth_method", sa.String(20), nullable=False),
        sa.Column("scope", sa.String(24), nullable=False),
        sa.Column("reason", sa.Text()),
        sa.Column("correlation_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.CheckConstraint(
            "operation IN ('create', 'revoke', 'ratify')",
            name=op.f("ck_role_capability_mapping_events_operation"),
        ),
        sa.CheckConstraint(
            "outcome IN ('applied', 'refused')",
            name=op.f("ck_role_capability_mapping_events_outcome"),
        ),
        sa.CheckConstraint(
            "(outcome = 'refused') = (refusal_code IS NOT NULL)",
            name=op.f("ck_role_capability_mapping_events_refusal_is_coded"),
        ),
        sa.CheckConstraint(
            "auth_method IN " + _sql_tuple(_AUTH_METHODS),
            name=op.f("ck_role_capability_mapping_events_auth_method"),
        ),
        sa.CheckConstraint(
            "scope IN " + _sql_tuple(_ADMIN_SCOPES),
            name=op.f("ck_role_capability_mapping_events_scope"),
        ),
        sa.ForeignKeyConstraint(
            ["actor_account_id"],
            ["platform_accounts.id"],
            ondelete="RESTRICT",
            name=op.f("fk_role_capability_mapping_events_actor_account_id_platform_accounts"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_role_capability_mapping_events")),
    )
    op.create_index(
        "ix_role_capability_mapping_events_mapping",
        "role_capability_mapping_events",
        ["mapping_id", "occurred_at"],
    )
    for table in NEW_APPEND_ONLY_TABLES:
        op.execute(
            f"""
            CREATE TRIGGER {table}_append_only
            BEFORE UPDATE OR DELETE ON {table}
            FOR EACH ROW EXECUTE FUNCTION reject_history_mutation();
            """
        )


# ---------------------------------------------------------------------------
# Column additions on existing tables
# ---------------------------------------------------------------------------


def _add_character_access_columns() -> None:
    """Nullable in stage A; `NOT NULL` in stage B once the backfill has run."""
    op.add_column(
        "character_access",
        sa.Column("platform_account_id", postgresql.UUID(as_uuid=True)),
    )
    op.add_column(
        "character_access",
        sa.Column("granted_by_account_id", postgresql.UUID(as_uuid=True)),
    )
    op.create_foreign_key(
        op.f("fk_character_access_platform_account_id_platform_accounts"),
        "character_access",
        "platform_accounts",
        ["platform_account_id"],
        ["id"],
        ondelete="RESTRICT",
    )
    op.create_foreign_key(
        op.f("fk_character_access_granted_by_account_id_platform_accounts"),
        "character_access",
        "platform_accounts",
        ["granted_by_account_id"],
        ["id"],
        ondelete="RESTRICT",
    )


def _swap_audit_attribution_constraint() -> None:
    """The swap. Statement order is the argument; see the module docstring."""
    op.add_column(
        "audit_events",
        sa.Column("actor_platform_account_id", postgresql.UUID(as_uuid=True)),
    )
    op.execute(
        """
        ALTER TABLE audit_events
            ADD CONSTRAINT fk_audit_events_actor_platform_account_id_platform_accounts
            FOREIGN KEY (actor_platform_account_id) REFERENCES platform_accounts (id)
            ON DELETE RESTRICT
            NOT VALID;
        """
    )
    # 1. The wider rule goes in FIRST, so the table is never less constrained
    #    than it is today, not even for the duration of one statement.
    op.execute(
        """
        ALTER TABLE audit_events
            ADD CONSTRAINT ck_audit_events_human_action_has_an_attribution CHECK (
                actor_platform_account_id IS NOT NULL
                OR actor_discord_user_id IS NOT NULL
                OR actor_capability IN ('service_principal', 'system')
            ) NOT VALID;
        """
    )
    # 2. Only then is the narrower rule withdrawn. Between the two statements
    #    both are in force; at no instant is an unattributed human row
    #    insertable.
    op.execute(
        "ALTER TABLE audit_events DROP CONSTRAINT ck_audit_events_human_action_has_an_actor;"
    )
    # The default cursor order for the bounded audit page (N-21, N-64). An
    # append-only table with a descending time index costs an extra write per
    # event; that is the price of "no unbounded offset scan" and it is accepted
    # deliberately (schema §11.1).
    op.create_index(
        "ix_audit_events_occurred_at_desc",
        "audit_events",
        [sa.text("occurred_at DESC"), sa.text("id DESC")],
    )


def _add_snapshot_imports_attribution() -> None:
    """A **strengthening**, not a replacement: no rule exists here to drop.

    It must never be `VALIDATE`d, and the reason differs from the `audit_events`
    case: there is no old constraint whose truth implies the new one, so nothing
    can prove from the schema alone that every historical row satisfies it, and
    P3.0 did not inspect production data. `NOT VALID` binds new writes; the past
    is left exactly as it was found.
    """
    op.add_column(
        "snapshot_imports", sa.Column("actor_account_id", postgresql.UUID(as_uuid=True))
    )
    op.execute(
        """
        ALTER TABLE snapshot_imports
            ADD CONSTRAINT fk_snapshot_imports_actor_account_id_platform_accounts
            FOREIGN KEY (actor_account_id) REFERENCES platform_accounts (id)
            ON DELETE RESTRICT
            NOT VALID;
        """
    )
    op.execute(
        """
        ALTER TABLE snapshot_imports
            ADD CONSTRAINT ck_snapshot_imports_import_has_an_attribution CHECK (
                actor_account_id IS NOT NULL
                OR actor_discord_user_id IS NOT NULL
                OR actor_capability = 'system'
            ) NOT VALID;
        """
    )


def _add_foundry_snapshots_attribution() -> None:
    """Column and foreign key only. **No check constraint is added.**

    `foundry_snapshots` has no attribution rule today, and a "must name
    somebody" rule would be false of legitimate rows: migration 0004 records
    that the supervised bootstrap has no interactive user. This is the table the
    naive symmetric fix would have broken.
    """
    op.add_column(
        "foundry_snapshots", sa.Column("received_by_account_id", postgresql.UUID(as_uuid=True))
    )
    op.execute(
        """
        ALTER TABLE foundry_snapshots
            ADD CONSTRAINT fk_foundry_snapshots_received_by_account_id_platform_accounts
            FOREIGN KEY (received_by_account_id) REFERENCES platform_accounts (id)
            ON DELETE RESTRICT
            NOT VALID;
        """
    )


# ---------------------------------------------------------------------------
# Backfill and control totals
# ---------------------------------------------------------------------------


def _backfill_accounts(connection: sa.Connection) -> None:
    """One account and one active Discord identity per existing Discord user.

    Idempotent by construction: the insert selects `discord_users` that have no
    `external_identities` row for `('discord', id)`, so re-running inserts
    nothing and a re-run after a partial failure completes the remainder. That is
    ADR 0003's "idempotency from mapping constraints", not a flag somebody
    remembered to check.
    """
    # The pairing is materialised **first**, so the account a Discord user gets
    # is written down before either insert runs. Deriving it instead from the
    # row order of an `INSERT … RETURNING` would be wrong: PostgreSQL does not
    # promise that `RETURNING` yields rows in the order the source produced
    # them, and a mismatch here would silently attach every identity to somebody
    # else's account — the one failure T6 exists to catch and the one nobody
    # should be relying on a control total to catch.
    connection.execute(
        sa.text(
            """
            CREATE TEMPORARY TABLE _identity_backfill ON COMMIT DROP AS
            SELECT u.id                AS discord_id,
                   u.created_at        AS linked_at,
                   gen_random_uuid()   AS account_id,
                   gen_random_uuid()   AS identity_id,
                   gen_random_uuid()   AS correlation_id
              FROM discord_users u
             WHERE NOT EXISTS (
                    SELECT 1 FROM external_identities e
                     WHERE e.provider_key = 'discord'
                       AND e.subject = u.id::text
                   );
            """
        )
    )
    connection.execute(
        sa.text(
            """
            INSERT INTO platform_accounts (
                id, status, is_protected_admin, created_at, updated_at, version
            )
            SELECT account_id, 'active', false, now(), now(), 0
              FROM _identity_backfill;
            """
        )
    )
    connection.execute(
        sa.text(
            """
            INSERT INTO external_identities (
                id, platform_account_id, provider_key, subject, state,
                linked_at, audit_correlation_id
            )
            SELECT identity_id, account_id, 'discord', discord_id::text, 'active',
                   linked_at, correlation_id
              FROM _identity_backfill;
            """
        )
    )
    connection.execute(sa.text("DROP TABLE _identity_backfill"))
    # Authorization-bearing rows are resolved through the identity table, never
    # by matching anything name-like. A row whose Discord user has no identity
    # would stay null and be caught by T4/T5 below.
    connection.execute(
        sa.text(
            """
            UPDATE character_access ca
               SET platform_account_id = owner_identity.platform_account_id,
                   granted_by_account_id = grantor_identity.platform_account_id
              FROM external_identities owner_identity,
                   external_identities grantor_identity
             WHERE owner_identity.provider_key = 'discord'
               AND owner_identity.subject = ca.discord_user_id::text
               AND grantor_identity.provider_key = 'discord'
               AND grantor_identity.subject = ca.granted_by_discord_user_id::text;
            """
        )
    )


def _insert_protected_mapping(*, guild_id: int, role_id: int) -> None:
    """The one mapping whose authority does not derive from an emergency action.

    Inserted with `created_under_scope = 'full'` and `provenance = 'ordinary'`,
    which is what makes §8.1's ratification path terminate: there is always
    exactly one mapping in the database that is `ordinary` by construction and
    cannot be edited.
    """
    # Literal values rather than bound parameters, so the statement renders
    # identically in an offline (`--sql`) script and online. The identifiers are
    # generated here, which means two runs of `--sql` produce two different
    # mapping ids — that is correct: they are two different proposed inserts, and
    # applying both would be refused by the one-protected-row trigger.
    op.execute(
        sa.text(
            f"""
            INSERT INTO role_capability_mappings (
                id, guild_id, role_id, capability, protected, active,
                created_by_account_id, created_under_auth_method,
                created_under_scope, provenance, created_at, reason,
                audit_correlation_id, version
            ) VALUES (
                '{uuid4()}', {guild_id:d}, {role_id:d}, 'platform_administrator',
                true, true, NULL, 'discord_oauth', 'full', 'ordinary', now(),
                'Protected Server Administrator bootstrap mapping, inserted by '
                'migration 0006 under OD-24 and ADR 0010 D10. It cannot be '
                'revoked, edited, demoted or shadowed by the application.',
                '{uuid4()}', 0
            );
            """
        )
    )


def _check_control_totals(
    connection: sa.Connection, *, audit_rows_before: sa.engine.Row
) -> None:
    """T1–T8, checked in the migration's own transaction, refusing on disagreement.

    A control total that is computed and then ignored is a comment. These run
    before the transaction commits, so a disagreement rolls the whole stage back
    and the database is left exactly where it started.
    """
    failures: list[str] = []

    def scalar(sql: str) -> int:
        return int(connection.execute(sa.text(sql)).scalar_one())

    discord_users = scalar("SELECT count(*) FROM discord_users")
    discord_identities = scalar(
        "SELECT count(*) FROM external_identities WHERE provider_key = 'discord'"
    )
    distinct_subjects = scalar(
        "SELECT count(DISTINCT subject) FROM external_identities WHERE provider_key = 'discord'"
    )
    accounts = scalar("SELECT count(*) FROM platform_accounts")

    # T1 — every Discord user has an account. `>=` rather than `=` because a
    # re-run over a database that already has accounts must not fail; T2 and T6
    # are what actually pin the mapping.
    if accounts < discord_users:
        failures.append(
            f"T1: {accounts} platform accounts for {discord_users} Discord users."
        )
    # T2
    if discord_identities != discord_users:
        failures.append(
            f"T2: {discord_identities} Discord identities for {discord_users} Discord users."
        )
    # T3
    if distinct_subjects != discord_identities:
        failures.append(
            f"T3: {distinct_subjects} distinct subjects among {discord_identities} "
            "Discord identities; a subject is duplicated."
        )
    # T4 / T5
    unresolved = scalar(
        "SELECT count(*) FROM character_access WHERE platform_account_id IS NULL"
    )
    if unresolved:
        failures.append(f"T4: {unresolved} character_access rows have no account.")
    unresolved_grantor = scalar(
        "SELECT count(*) FROM character_access WHERE granted_by_account_id IS NULL"
    )
    if unresolved_grantor:
        failures.append(
            f"T5: {unresolved_grantor} character_access rows have no granting account."
        )
    # T6 — the one that matters for the mapping: a full-table equality between
    # the old key and the new key. This is the evidence that the migration
    # *mapped* rather than guessed.
    mismatched = scalar(
        """
        SELECT count(*)
          FROM character_access ca
         WHERE NOT EXISTS (
                SELECT 1 FROM external_identities e
                 WHERE e.platform_account_id = ca.platform_account_id
                   AND e.provider_key = 'discord'
                   AND e.state = 'active'
                   AND e.subject = ca.discord_user_id::text
               )
        """
    )
    if mismatched:
        failures.append(
            f"T6: {mismatched} character_access rows resolve to an account whose "
            "active Discord identity is not the row's own Discord user."
        )
    # T7 — history is the same size it was, and ends at the same moment.
    after = connection.execute(
        sa.text("SELECT count(*), max(occurred_at) FROM audit_events")
    ).one()
    if after[0] != audit_rows_before[0] or after[1] != audit_rows_before[1]:
        failures.append(
            "T7: the audit_events row count or latest timestamp changed during a "
            "revision that must not touch history."
        )
    # T8 — the rule set is exactly the one that was reviewed.
    inventory_problem = _check_constraint_inventory(connection)
    if inventory_problem:
        failures.append(f"T8: {inventory_problem}")

    if failures:
        raise RuntimeError(
            "Revision 0006 refused: control totals disagree.\n  - "
            + "\n  - ".join(failures)
        )


#: What T8 asserts. Every check constraint each append-only table must have
#: after this revision, and no other. Named so a later migration that quietly
#: reintroduced a Discord-only attribution rule would fail T8 and TC-MIG-15
#: rather than pass unnoticed.
EXPECTED_CHECK_CONSTRAINTS: dict[str, frozenset[str]] = {
    "audit_events": frozenset(
        {
            "ck_audit_events_actor_capability",
            "ck_audit_events_human_action_has_an_attribution",
            "ck_audit_events_source",
            "ck_audit_events_action_not_blank",
            "ck_audit_events_entity_type_not_blank",
        }
    ),
    "snapshot_imports": frozenset(
        {
            "ck_snapshot_imports_status",
            "ck_snapshot_imports_mode",
            "ck_snapshot_imports_actor_capability",
            "ck_snapshot_imports_counts_non_negative",
            "ck_snapshot_imports_operation_digest_sha256_hex",
            "ck_snapshot_imports_import_has_an_attribution",
        }
    ),
    "foundry_snapshots": frozenset(
        {
            "ck_foundry_snapshots_checksum_sha256_hex",
            "ck_foundry_snapshots_size_positive",
            "ck_foundry_snapshots_actor_count_non_negative",
            "ck_foundry_snapshots_schema_version_positive",
            "ck_foundry_snapshots_received_via",
            "ck_foundry_snapshots_module_submission_names_its_principal",
        }
    ),
}

CONSTRAINT_INVENTORY_QUERY = """
SELECT c.conname
  FROM pg_constraint c
  JOIN pg_class t ON t.oid = c.conrelid
  JOIN pg_namespace n ON n.oid = t.relnamespace
 WHERE c.contype = 'c'
   AND n.nspname = current_schema()
   AND t.relname = :table
   AND c.conname NOT LIKE '%_not_null'
"""


def _check_constraint_inventory(connection: sa.Connection) -> str | None:
    problems: list[str] = []
    for table, expected in EXPECTED_CHECK_CONSTRAINTS.items():
        found = {
            row[0]
            for row in connection.execute(
                sa.text(CONSTRAINT_INVENTORY_QUERY), {"table": table}
            )
        }
        missing = expected - found
        extra = found - expected
        if missing:
            problems.append(f"{table} is missing {sorted(missing)}")
        if extra:
            problems.append(f"{table} carries unexpected {sorted(extra)}")
    return "; ".join(problems) if problems else None


def _sql_tuple(values: Sequence[str]) -> str:
    return "(" + ", ".join(f"'{value}'" for value in values) + ")"
