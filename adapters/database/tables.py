from __future__ import annotations

from sqlalchemy import (
    BIGINT,
    JSON,
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    Index,
    Integer,
    LargeBinary,
    SmallInteger,
    String,
    Table,
    Text,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID

from .metadata import metadata

json_type = JSON().with_variant(JSONB(), "postgresql")

discord_users = Table(
    "discord_users",
    metadata,
    Column("id", BIGINT, primary_key=True, autoincrement=False),
    Column("username", String(80), nullable=False),
    Column("global_name", String(80)),
    Column("created_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
    Column(
        "updated_at",
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    ),
    CheckConstraint("id > 0", name="positive_id"),
    CheckConstraint("length(trim(username)) > 0", name="username_not_blank"),
)

discord_guild_memberships = Table(
    "discord_guild_memberships",
    metadata,
    Column("discord_user_id", BIGINT, ForeignKey("discord_users.id", ondelete="CASCADE"), primary_key=True),
    Column("guild_id", BIGINT, primary_key=True),
    Column("active", Boolean, nullable=False, server_default="true"),
    Column("observed_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
    CheckConstraint("guild_id > 0", name="positive_guild_id"),
)

discord_membership_roles = Table(
    "discord_membership_roles",
    metadata,
    Column("discord_user_id", BIGINT, primary_key=True),
    Column("guild_id", BIGINT, primary_key=True),
    Column("role_id", BIGINT, primary_key=True),
    ForeignKeyConstraint(
        ["discord_user_id", "guild_id"],
        ["discord_guild_memberships.discord_user_id", "discord_guild_memberships.guild_id"],
        ondelete="CASCADE",
    ),
    CheckConstraint("role_id > 0", name="positive_role_id"),
)

characters = Table(
    "characters",
    metadata,
    Column("id", UUID(as_uuid=True), primary_key=True),
    Column("display_name", String(120), nullable=False),
    Column("long_name", String(240)),
    # Nullable while an imported identity awaits Council reconciliation.
    Column("level", Integer),
    Column("active", Boolean, nullable=False, server_default="true"),
    Column("version", Integer, nullable=False, server_default="0"),
    Column("created_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
    Column(
        "updated_at",
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    ),
    CheckConstraint("length(trim(display_name)) > 0", name="display_name_not_blank"),
    CheckConstraint("level IS NULL OR level BETWEEN 1 AND 20", name="level_range"),
    CheckConstraint("version >= 0", name="version_non_negative"),
)

character_access = Table(
    "character_access",
    metadata,
    Column("id", UUID(as_uuid=True), primary_key=True),
    Column("character_id", UUID(as_uuid=True), ForeignKey("characters.id", ondelete="CASCADE"), nullable=False),
    # Retained through stage C as a trigger-maintained read-only shadow, and
    # dropped in stage D — a separate, later decision after the verification
    # period in the migration contract §6. Until then both key sets are enforced
    # simultaneously, which is what makes the cutover reversible.
    Column("discord_user_id", BIGINT, ForeignKey("discord_users.id", ondelete="RESTRICT"), nullable=False),
    # The authorization-bearing key from stage B onward (ADR 0010 D1). Only an
    # account id may answer "who may do this here?".
    Column(
        "platform_account_id",
        UUID(as_uuid=True),
        ForeignKey("platform_accounts.id", ondelete="RESTRICT"),
        nullable=False,
    ),
    Column("access_kind", String(20), nullable=False),
    Column("active", Boolean, nullable=False, server_default="true"),
    Column("default_character", Boolean, nullable=False, server_default="false"),
    Column("granted_by_discord_user_id", BIGINT, ForeignKey("discord_users.id", ondelete="RESTRICT"), nullable=False),
    Column(
        "granted_by_account_id",
        UUID(as_uuid=True),
        ForeignKey("platform_accounts.id", ondelete="RESTRICT"),
        nullable=False,
    ),
    Column("granted_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
    Column("revoked_at", DateTime(timezone=True)),
    Column("expires_at", DateTime(timezone=True)),
    Column("reason", Text, nullable=False),
    Column("audit_correlation_id", UUID(as_uuid=True), nullable=False),
    CheckConstraint(
        "access_kind IN ('owner', 'co_owner', 'delegate', 'viewer')",
        name="access_kind",
    ),
    CheckConstraint("length(trim(reason)) > 0", name="reason_not_blank"),
    CheckConstraint(
        "(active AND revoked_at IS NULL) OR (NOT active AND revoked_at IS NOT NULL)",
        name="revocation_state",
    ),
    CheckConstraint("revoked_at IS NULL OR revoked_at >= granted_at", name="revoked_after_grant"),
    CheckConstraint("expires_at IS NULL OR expires_at > granted_at", name="expiry_after_grant"),
)
# Uniqueness covers *active* links only. A revoked grant stays as a historical row
# carrying its own revoked_at, reason and audit_correlation_id, so re-granting the
# same user inserts a new row instead of overwriting the revocation.
Index(
    "uq_character_access_one_active_link",
    character_access.c.character_id,
    character_access.c.discord_user_id,
    unique=True,
    postgresql_where=character_access.c.active,
)
# OD-37: a character has exactly one owner. The database enforces *at most* one;
# requiring at least one is an application invariant, because the Phase 2 importer
# creates a character before Council has resolved who owns it.
# Guild Council reach over every character is role-derived and is deliberately not
# modelled as an access row — that is why 'guild_council' is not an access_kind.
Index(
    "uq_character_access_one_active_owner",
    character_access.c.character_id,
    unique=True,
    postgresql_where=character_access.c.active
    & (character_access.c.access_kind == "owner"),
)
Index(
    "uq_character_access_one_active_default_per_user",
    character_access.c.discord_user_id,
    unique=True,
    postgresql_where=character_access.c.active & character_access.c.default_character,
)
# The account-keyed counterparts, created by migration 0007 **alongside** the
# Discord-keyed ones above. Both sets enforce at once until stage D, so a wrong
# mapping is rejected by one of them rather than discovered by a user holding
# authorization they should not have. `uq_character_access_one_active_owner` has
# no counterpart here because it never referenced the user column (OD-37).
Index(
    "uq_character_access_one_active_link_account",
    character_access.c.character_id,
    character_access.c.platform_account_id,
    unique=True,
    postgresql_where=character_access.c.active,
)
Index(
    "uq_character_access_one_active_default_per_account",
    character_access.c.platform_account_id,
    unique=True,
    postgresql_where=character_access.c.active & character_access.c.default_character,
)
Index(
    "ix_character_access_account_active",
    character_access.c.platform_account_id,
    postgresql_where=character_access.c.active,
)

external_actor_mappings = Table(
    "external_actor_mappings",
    metadata,
    Column("id", UUID(as_uuid=True), primary_key=True),
    Column("character_id", UUID(as_uuid=True), ForeignKey("characters.id", ondelete="CASCADE"), nullable=False),
    Column("world_id", String(120), nullable=False),
    Column("external_actor_id", String(64), nullable=False),
    Column("last_instance", String(255)),
    Column("relink_fingerprint", String(255), nullable=False),
    # Which snapshot established this mapping, and which folder the Actor sat
    # in. Provenance for plan §12 Phase 2: "every applied character and mapping
    # is traceable to the immutable snapshot checksum and triggering actor".
    # Nullable because a mapping may also be created by a deliberate Council
    # link that no snapshot proposed.
    Column("established_by_snapshot_id", UUID(as_uuid=True), ForeignKey("foundry_snapshots.id", ondelete="RESTRICT")),
    Column("folder_id", String(64)),
    Column("created_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
    UniqueConstraint("world_id", "external_actor_id"),
    UniqueConstraint("character_id", "world_id"),
    CheckConstraint("length(trim(world_id)) > 0", name="world_id_not_blank"),
    CheckConstraint("external_actor_id ~ '^[A-Za-z0-9]{16}$'", name="actor_id_shape"),
    CheckConstraint("length(trim(relink_fingerprint)) > 0", name="fingerprint_not_blank"),
)

sheet_row_mappings = Table(
    "sheet_row_mappings",
    metadata,
    Column("id", UUID(as_uuid=True), primary_key=True),
    Column("character_id", UUID(as_uuid=True), ForeignKey("characters.id", ondelete="CASCADE"), nullable=False),
    Column("sheet_tab", String(120), nullable=False),
    Column("row_index", Integer, nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
    UniqueConstraint("sheet_tab", "row_index"),
    UniqueConstraint("character_id", "sheet_tab"),
    CheckConstraint("length(trim(sheet_tab)) > 0", name="sheet_tab_not_blank"),
    CheckConstraint("row_index > 0", name="row_index_positive"),
)

audit_events = Table(
    "audit_events",
    metadata,
    Column("id", UUID(as_uuid=True), primary_key=True),
    Column("occurred_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
    # Nullable: import, scheduled and system actions have no acting Discord user.
    # RESTRICT keeps attribution intact — a user with audit history cannot be
    # deleted silently; removing one is an explicit, separately designed action.
    Column(
        "actor_discord_user_id",
        BIGINT,
        ForeignKey("discord_users.id", ondelete="RESTRICT"),
    ),
    # Added by migration 0006. Historical rows keep their Discord column and are
    # never rewritten (ADR 0010 D5); new rows carry the account. A read resolves
    # the older form through `external_identities`, which is why an identity is
    # retired rather than deleted.
    Column(
        "actor_platform_account_id",
        UUID(as_uuid=True),
        ForeignKey("platform_accounts.id", ondelete="RESTRICT"),
    ),
    # The authority the action was taken under (plan §4.1/§4.3). A Council member
    # modifying a character they do not own must be distinguishable in the audit
    # from the owner editing it, so this is required rather than inferred.
    Column("actor_capability", String(30), nullable=False),
    Column("action", String(120), nullable=False),
    Column("entity_type", String(80), nullable=False),
    Column("entity_id", String(120), nullable=False),
    Column("source", String(20), nullable=False),
    Column("correlation_id", UUID(as_uuid=True), nullable=False),
    Column("payload", json_type, nullable=False),
    CheckConstraint(
        "actor_capability IN ('guild_member', 'character_owner', 'dm', "
        "'guild_council', 'platform_administrator', 'service_principal', 'system')",
        name="actor_capability",
    ),
    # Replaced by migration 0006. The rule was not relaxed; its subject was
    # widened from *a Discord user* to *an identified person*, because a
    # break-glass administrator acting during a Discord outage is a human
    # capability with no Discord user id, and the legacy constraint refused the
    # very audit event ADR 0010 D8's recovery path must write.
    CheckConstraint(
        "actor_platform_account_id IS NOT NULL "
        "OR actor_discord_user_id IS NOT NULL "
        "OR actor_capability IN ('service_principal', 'system')",
        name="human_action_has_an_attribution",
    ),
    CheckConstraint("source IN ('discord', 'web', 'foundry', 'import', 'system')", name="source"),
    CheckConstraint("length(trim(action)) > 0", name="action_not_blank"),
    CheckConstraint("length(trim(entity_type)) > 0", name="entity_type_not_blank"),
)
Index("ix_audit_events_entity", audit_events.c.entity_type, audit_events.c.entity_id, audit_events.c.occurred_at)
Index("ix_audit_events_correlation_id", audit_events.c.correlation_id)
# The cursor order for the bounded audit page (N-21, N-64). An append-only table
# with a descending time index costs an extra write per event; that is the price
# of "no unbounded offset scan" and it is accepted deliberately.
Index(
    "ix_audit_events_occurred_at_desc",
    audit_events.c.occurred_at.desc(),
    audit_events.c.id.desc(),
)

#: Tables the application may only append to. The runtime role holds
#: `SELECT, INSERT` on each, and a database trigger rejects `UPDATE`/`DELETE`
#: even for the schema owner, so an accidental repair is a visible act of DDL
#: rather than a quiet row edit.
APPEND_ONLY_TABLES = (
    "audit_events",
    "foundry_snapshots",
    "snapshot_imports",
    # Added by migration 0006. `role_capability_mappings` itself is mutable — a
    # mapping is revoked, not deleted — but the record of every attempt to change
    # one, refusals included, must not be editable by the service whose
    # behaviour it records.
    "role_capability_mapping_events",
)

foundry_snapshots = Table(
    "foundry_snapshots",
    metadata,
    Column("id", UUID(as_uuid=True), primary_key=True),
    # The identity: SHA-256 of the artifact's original bytes, computed before
    # parsing. One changed byte is a different snapshot, which is why this is
    # unique rather than merely indexed.
    Column("checksum", String(64), nullable=False, unique=True),
    Column("size_bytes", Integer, nullable=False),
    Column("schema_version", Integer, nullable=False),
    Column("exporter_id", String(120), nullable=False),
    Column("exporter_version", String(32), nullable=False),
    Column("exported_at", DateTime(timezone=True), nullable=False),
    Column("world_id", String(120), nullable=False),
    Column("world_title", String(200), nullable=False),
    Column("core_version", String(32), nullable=False),
    Column("system_id", String(64), nullable=False),
    Column("system_version", String(32), nullable=False),
    Column("actor_count", Integer, nullable=False),
    Column("selected_folder_ids", json_type, nullable=False),
    # A reference into the restricted artifact store, never the bytes. Audit
    # visibility does not by itself grant permission to download the artifact.
    Column("artifact_location", Text),
    Column("received_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
    Column("received_by_discord_user_id", BIGINT, ForeignKey("discord_users.id", ondelete="RESTRICT")),
    # Added by migration 0006. **No attribution check accompanies it**, unlike
    # `audit_events` and `snapshot_imports`: this table has never required a
    # human, and migration 0004 records why — the supervised bootstrap has no
    # interactive user. A "must name somebody" rule here would be false of
    # legitimate rows, which is why the three append-only tables are treated on
    # their own evidence rather than symmetrically.
    Column(
        "received_by_account_id",
        UUID(as_uuid=True),
        ForeignKey("platform_accounts.id", ondelete="RESTRICT"),
    ),
    # How the artifact arrived, and who presented it. An operator ran a command
    # as themselves; a module presented a submit-only service credential and no
    # human at all. `received_by_discord_user_id` cannot express the second, so
    # a record written on that path would otherwise name nobody.
    Column("received_via", String(20), nullable=False, server_default="operator"),
    Column("submitted_by_principal", String(64)),
    Column("correlation_id", UUID(as_uuid=True), nullable=False),
    CheckConstraint("checksum ~ '^[0-9a-f]{64}$'", name="checksum_sha256_hex"),
    CheckConstraint(
        "received_via IN ('operator', 'foundry_module')", name="received_via"
    ),
    # Attribution is required on the module path and forbidden on the operator
    # path, so a row can never claim a chain of custody it did not have.
    CheckConstraint(
        "(received_via = 'foundry_module') = (submitted_by_principal IS NOT NULL)",
        name="module_submission_names_its_principal",
    ),
    CheckConstraint("size_bytes > 0", name="size_positive"),
    CheckConstraint("actor_count >= 0", name="actor_count_non_negative"),
    CheckConstraint("schema_version > 0", name="schema_version_positive"),
)

snapshot_imports = Table(
    "snapshot_imports",
    metadata,
    Column("id", UUID(as_uuid=True), primary_key=True),
    Column("snapshot_id", UUID(as_uuid=True), ForeignKey("foundry_snapshots.id", ondelete="RESTRICT"), nullable=False),
    Column("folder_id", String(64), nullable=False),
    Column("folder_path", Text, nullable=False),
    Column("profile_version", String(64), nullable=False),
    # The apply attempt's own key: a retry of the same request returns the
    # original result instead of applying a second time.
    #
    # The only column that holds the caller's key verbatim, and it holds it
    # because an exact match is what the idempotency lookup does. Audit rows
    # carry a one-way `request_key_digest` instead (finding S-1), and a refused
    # attempt is keyed by that digest too, so the text is written once per
    # applied attempt and nowhere else.
    Column("request_key", String(255), nullable=False, unique=True),
    # …and what that key was spent on. The key alone identifies the attempt; it
    # does not identify the *operation*, so on its own it let a different
    # artifact, folder or profile be presented under an old key and receive the
    # original receipt (finding B-1). Stored immutably beside the key so a retry
    # can be told from a reuse without trusting anything the caller passes.
    Column("operation_digest", String(64), nullable=False),
    Column("status", String(20), nullable=False),
    Column("mode", String(20), nullable=False),
    Column("actor_discord_user_id", BIGINT, ForeignKey("discord_users.id", ondelete="RESTRICT")),
    Column(
        "actor_account_id",
        UUID(as_uuid=True),
        ForeignKey("platform_accounts.id", ondelete="RESTRICT"),
    ),
    Column("actor_capability", String(30), nullable=False),
    Column("supervisor", String(120)),
    Column("created_count", Integer, nullable=False, server_default="0"),
    Column("updated_count", Integer, nullable=False, server_default="0"),
    Column("warning_count", Integer, nullable=False, server_default="0"),
    Column("summary", json_type, nullable=False),
    Column("occurred_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
    Column("correlation_id", UUID(as_uuid=True), nullable=False),
    CheckConstraint("status IN ('applied', 'refused')", name="status"),
    CheckConstraint("mode IN ('bootstrap', 'council')", name="mode"),
    CheckConstraint(
        "actor_capability IN ('guild_council', 'platform_administrator', 'system')",
        name="actor_capability",
    ),
    CheckConstraint("created_count >= 0 AND updated_count >= 0 AND warning_count >= 0", name="counts_non_negative"),
    CheckConstraint("operation_digest ~ '^[0-9a-f]{64}$'", name="operation_digest_sha256_hex"),
    # Added by migration 0006 as a **strengthening**: no attribution rule existed
    # on this table, so a `guild_council` import row could name nobody at all.
    # It binds new writes only and is never validated against history, because
    # nothing here implies it was true of the past.
    CheckConstraint(
        "actor_account_id IS NOT NULL "
        "OR actor_discord_user_id IS NOT NULL "
        "OR actor_capability = 'system'",
        name="import_has_an_attribution",
    ),
)
# The *input* identity of an import is (snapshot, folder, profile version).
# Only an applied row claims it, so a refusal never blocks the retry that fixes
# it, and a second apply of the same input cannot succeed twice.
Index(
    "uq_snapshot_imports_applied_input",
    snapshot_imports.c.snapshot_id,
    snapshot_imports.c.folder_id,
    snapshot_imports.c.profile_version,
    unique=True,
    postgresql_where=snapshot_imports.c.status == "applied",
)
Index("ix_snapshot_imports_correlation_id", snapshot_imports.c.correlation_id)

platform_initialization = Table(
    "platform_initialization",
    metadata,
    # Exactly one row can ever exist: the primary key is a boolean constrained
    # to true. The bootstrap disables itself by inserting it, and the
    # constraint — not the application — is what makes that irreversible.
    Column("singleton", Boolean, primary_key=True, server_default="true"),
    Column("initialized_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
    Column("supervisor", String(120), nullable=False),
    Column("snapshot_checksum", String(64)),
    Column("profile_version", String(64), nullable=False),
    Column("correlation_id", UUID(as_uuid=True), nullable=False),
    CheckConstraint("singleton", name="single_row"),
    CheckConstraint("length(trim(supervisor)) > 0", name="supervisor_not_blank"),
)

#: The admission generation a submission credential may currently write under.
#:
#: This is the **fence** finding B-1 asked for, and its shape is the argument.
#:
#: `principal_id` is unique across the whole table, for all time. A principal
#: therefore holds at most one admission that ever existed, so an admission that
#: has been closed cannot be replaced by an open one for the same credential —
#: which is what stops a request that was accepted long ago, and paused
#: somewhere, from waking up and finding itself admitted again. Recovery issues a
#: *new* credential (§5.2) and opens a *new* admission naming it; the old request
#: cannot present it, because the id it carries is fixed in the bytes it was sent
#: with.
#:
#: `state` moves `open` → `closed` once and never back. Migration 0005 enforces
#: that with a trigger, and refuses `DELETE` outright, because a reopened
#: admission would be indistinguishable from one that was never closed.
submission_admissions = Table(
    "submission_admissions",
    metadata,
    Column("id", UUID(as_uuid=True), primary_key=True),
    #: Ordering an operator can read and cite. Unique so two concurrent opens
    #: cannot both claim to be the same generation.
    Column("generation", BIGINT, nullable=False, autoincrement=False),
    Column("principal_id", String(64), nullable=False),
    Column("state", String(16), nullable=False),
    Column("opened_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
    Column("opened_by", String(120), nullable=False),
    Column("open_reason", Text, nullable=False),
    Column("correlation_id", UUID(as_uuid=True), nullable=False),
    Column("closed_at", DateTime(timezone=True)),
    Column("closed_by", String(120)),
    Column("close_reason", Text),
    Column("closed_correlation_id", UUID(as_uuid=True)),
    UniqueConstraint("generation", name="uq_submission_admissions_generation"),
    UniqueConstraint("principal_id", name="uq_submission_admissions_principal_id"),
    CheckConstraint("state IN ('open', 'closed')", name="state"),
    CheckConstraint("generation >= 0", name="generation_not_negative"),
    # Both directions. A `closed` row that names no closure would be a fence
    # nobody can account for, and an `open` row carrying one would be a closure
    # that did not take effect.
    CheckConstraint(
        "(state = 'closed') = (closed_at IS NOT NULL)", name="closed_state_is_dated"
    ),
    CheckConstraint(
        "(state = 'closed') = (closed_by IS NOT NULL)", name="closed_state_names_its_operator"
    ),
    CheckConstraint(
        "(state = 'closed') = (close_reason IS NOT NULL)", name="closed_state_gives_a_reason"
    ),
    CheckConstraint(
        "(state = 'closed') = (closed_correlation_id IS NOT NULL)",
        name="closed_state_is_correlated",
    ),
)

idempotency_keys = Table(
    "idempotency_keys",
    metadata,
    Column("id", UUID(as_uuid=True), primary_key=True),
    Column("scope", String(120), nullable=False),
    Column("key", String(255), nullable=False),
    Column("request_hash", LargeBinary(32), nullable=False),
    Column("status", String(20), nullable=False),
    Column("response", json_type),
    #: The admission this receipt was earned under — and the reason the fence
    #: works. Writing this row is what makes an acceptance durable, on the
    #: new-bytes path *and* on the duplicate-bytes path where no
    #: `foundry_snapshots` row is created, so it is the one choke point every
    #: successful submission passes through.
    #:
    #: The foreign key is not decoration. PostgreSQL takes a row-level `KEY
    #: SHARE` lock on the referenced admission to check it, which conflicts with
    #: the `FOR UPDATE` that closure takes — so a closure and an acceptance can
    #: never interleave, and the submission's own state re-read afterwards sees
    #: a closure that got in first. That was established against this host's
    #: PostgreSQL 16.14 rather than assumed; see
    #: `tests/test_submission_admission_postgresql.py`.
    Column(
        "admission_id",
        UUID(as_uuid=True),
        # `RESTRICT`, stated rather than defaulted: a receipt is the evidence
        # that an acceptance happened under a named generation, and an
        # admission that could be deleted out from under it would erase that.
        # The trigger in 0005 refuses `DELETE` on the parent outright; this is
        # the same rule said where a reader of the schema looks for it.
        ForeignKey(
            "submission_admissions.id",
            name="fk_idempotency_keys_admission_id",
            ondelete="RESTRICT",
        ),
    ),
    Column("created_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
    Column("expires_at", DateTime(timezone=True)),
    UniqueConstraint("scope", "key"),
    CheckConstraint("status IN ('started', 'completed', 'failed')", name="status"),
    CheckConstraint("length(request_hash) = 32", name="request_hash_sha256"),
    # Nullable in general — other scopes are not fenced — but never null for a
    # snapshot submission. A receipt in that scope that named no admission would
    # be an acceptance nobody can attribute to a generation, which is the state
    # the fence exists to make impossible.
    CheckConstraint(
        "scope <> 'foundry.snapshot.submission' OR admission_id IS NOT NULL",
        name="submission_names_its_admission",
    ),
)


# ---------------------------------------------------------------------------
# Phase 3 identity, session and credential tables (migration 0006).
#
# The one structural decision, stated where a reader of the schema meets it:
#
#   A snowflake may answer "who is this on Discord?".
#   Only an account id may answer "who may do this here?".
#
# `discord_users`, `discord_guild_memberships` and `discord_membership_roles`
# above remain **Discord facts**, keyed by snowflake and projected by an adapter.
# They join to an account only through `external_identities`.
# ---------------------------------------------------------------------------

platform_accounts = Table(
    "platform_accounts",
    metadata,
    Column("id", UUID(as_uuid=True), primary_key=True),
    Column("status", String(20), nullable=False, server_default="active"),
    # OD-24's anchor. A partial unique index below allows exactly one, and a
    # trigger refuses to clear the flag or to suspend the account: losing the
    # protected account through an ordinary administrative mistake is precisely
    # the failure that decision exists to prevent.
    Column("is_protected_admin", Boolean, nullable=False, server_default="false"),
    # Operator-facing label only, and **never** a matching key (N-16, ADR 0010
    # D3). Identity equivalence is established by an exact provider subject or
    # not at all.
    Column("display_label", String(80)),
    Column("created_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
    Column(
        "updated_at",
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    ),
    Column("version", Integer, nullable=False, server_default="0"),
    CheckConstraint("status IN ('active', 'suspended', 'closed')", name="status"),
    CheckConstraint("version >= 0", name="version_non_negative"),
)
Index(
    "uq_platform_accounts_one_protected_admin",
    platform_accounts.c.is_protected_admin,
    unique=True,
    postgresql_where=platform_accounts.c.is_protected_admin,
)

external_identities = Table(
    "external_identities",
    metadata,
    Column("id", UUID(as_uuid=True), primary_key=True),
    Column(
        "platform_account_id",
        UUID(as_uuid=True),
        ForeignKey("platform_accounts.id", ondelete="RESTRICT"),
        nullable=False,
    ),
    # `discord`, or `oidc:<exact issuer>` for a future reviewed provider. A
    # changed issuer is a *different* provider key and therefore a different
    # identity, never a silently migrated one (ADR 0010 D2).
    Column("provider_key", String(120), nullable=False),
    # The provider's immutable subject. For Discord, the snowflake as a canonical
    # decimal string.
    Column("subject", String(255), nullable=False),
    Column("state", String(20), nullable=False, server_default="active"),
    Column("linked_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
    # Null when self-linked at first login.
    Column(
        "linked_by_account_id",
        UUID(as_uuid=True),
        ForeignKey("platform_accounts.id", ondelete="RESTRICT"),
    ),
    Column("last_authenticated_at", DateTime(timezone=True)),
    Column("retired_at", DateTime(timezone=True)),
    Column("retired_reason", Text),
    Column("audit_correlation_id", UUID(as_uuid=True), nullable=False),
    CheckConstraint("state IN ('active', 'retired')", name="state"),
    CheckConstraint(
        "(state = 'retired') = (retired_at IS NOT NULL)", name="retirement_is_dated"
    ),
    CheckConstraint(
        r"provider_key ~ '^[a-z0-9]+(:[\x21-\x7e]+)?$'", name="provider_key_shape"
    ),
    CheckConstraint("length(trim(subject)) > 0", name="subject_not_blank"),
    # Covering retired rows as well is the exactness requirement of delivery plan
    # §9.2, and it additionally prevents a retired subject being re-linked to a
    # *different* account — the subject-reuse takeover in threat model T-06.
    UniqueConstraint("provider_key", "subject"),
)
# **There is deliberately no display-name, username or email column here.** The
# absence is the control: a column that does not exist cannot become a matching
# key (N-16, OD-42). `tests/test_web_identity_structure.py` asserts it.
Index(
    "ix_external_identities_active",
    external_identities.c.platform_account_id,
    postgresql_where=external_identities.c.state == "active",
)

oauth_token_grants = Table(
    "oauth_token_grants",
    metadata,
    Column("id", UUID(as_uuid=True), primary_key=True),
    Column(
        "external_identity_id",
        UUID(as_uuid=True),
        ForeignKey("external_identities.id", ondelete="CASCADE"),
        nullable=False,
    ),
    Column("access_token_ciphertext", LargeBinary, nullable=False),
    Column("refresh_token_ciphertext", LargeBinary),
    Column("nonce", LargeBinary, nullable=False),
    Column("refresh_nonce", LargeBinary),
    # Versioned so a key rotation is add-key, switch-active, re-encrypt,
    # remove-old — with no moment at which a stored token cannot be read.
    Column("key_version", SmallInteger, nullable=False),
    # Recorded so a scope widening at the provider is detectable rather than
    # inferred from behaviour.
    Column("scopes", String(120), nullable=False),
    Column("access_expires_at", DateTime(timezone=True), nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
    Column("deleted_at", DateTime(timezone=True)),
    CheckConstraint("length(nonce) = 12", name="nonce_length"),
    CheckConstraint("refresh_nonce IS NULL OR length(refresh_nonce) = 12", name="refresh_nonce_length"),
    CheckConstraint(
        "(refresh_token_ciphertext IS NULL) = (refresh_nonce IS NULL)",
        name="refresh_pairing",
    ),
)
Index(
    "uq_oauth_token_grants_one_live",
    oauth_token_grants.c.external_identity_id,
    unique=True,
    postgresql_where=oauth_token_grants.c.deleted_at.is_(None),
)

sessions = Table(
    "sessions",
    metadata,
    # Never the cookie value. The cookie holds a 256-bit random token; this table
    # holds its SHA-256, so a database read yields nothing a browser could
    # present.
    Column("id", UUID(as_uuid=True), primary_key=True),
    Column("token_hash", LargeBinary, nullable=False, unique=True),
    Column(
        "platform_account_id",
        UUID(as_uuid=True),
        ForeignKey("platform_accounts.id", ondelete="RESTRICT"),
        nullable=False,
    ),
    Column("auth_method", String(20), nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
    Column("last_seen_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
    Column("idle_expires_at", DateTime(timezone=True), nullable=False),
    Column("absolute_expires_at", DateTime(timezone=True), nullable=False),
    Column("revoked_at", DateTime(timezone=True)),
    Column("revocation_reason", String(40)),
    # Rotation is insert + revoke, never an in-place id change, so a stolen
    # cookie value is dead the instant rotation happens and the chain stays
    # auditable through this column.
    Column("rotated_from_session_id", UUID(as_uuid=True), ForeignKey("sessions.id", ondelete="RESTRICT")),
    # SHA-256 over the sorted capability set plus guild membership. A change
    # forces rotation (N-08). It is recomputed from a fresh resolution, never
    # read back as proof of anything.
    Column("privilege_fingerprint", LargeBinary, nullable=False),
    # Salted digests, for abuse investigation without storing addresses (plan
    # §9.4). The salt is a configured key, because an unkeyed digest of an IPv4
    # address is the address with extra steps.
    Column("client_ip_hash", LargeBinary),
    Column("user_agent_digest", LargeBinary),
    # OD-44. The authoritative relationship between a Discord OAuth session and
    # the one consumed transaction that produced it. `RESTRICT`, so N-04's expiry
    # reaper cannot delete a transaction a live session still names. There is
    # deliberately no reverse `oauth_transactions.session_id`: Peter's refinement
    # rejected a cyclic pair whose two halves could disagree.
    Column(
        "oauth_transaction_id",
        UUID(as_uuid=True),
        ForeignKey("oauth_transactions.id", ondelete="RESTRICT"),
    ),
    CheckConstraint(
        "auth_method IN ('discord_oauth', 'webauthn', 'recovery_grant')", name="auth_method"
    ),
    # The forbidden state as a database property: no Discord OAuth session
    # without a transaction behind it, and no break-glass session pretending to
    # have one.
    CheckConstraint(
        "(auth_method = 'discord_oauth') = (oauth_transaction_id IS NOT NULL)",
        name="oauth_transaction_binding",
    ),
    CheckConstraint(
        "revocation_reason IS NULL OR revocation_reason IN "
        "('logout', 'rotation', 'privilege_change', 'operator', 'expired', 'session_limit')",
        name="revocation_reason",
    ),
    CheckConstraint("absolute_expires_at > created_at", name="absolute_after_creation"),
    CheckConstraint("idle_expires_at <= absolute_expires_at", name="idle_within_absolute"),
    CheckConstraint("(revoked_at IS NULL) = (revocation_reason IS NULL)", name="revocation_state"),
    CheckConstraint("length(token_hash) = 32", name="token_hash_length"),
    CheckConstraint("length(privilege_fingerprint) = 32", name="privilege_fingerprint_length"),
    # OD-44 condition 2. These two composite keys exist only to be the targets of
    # the rotation foreign keys below them. `id` is already the primary key, so
    # each is trivially unique; PostgreSQL nonetheless requires a declared unique
    # constraint over the exact referenced column list.
    UniqueConstraint(
        "id", "platform_account_id", "auth_method", name="uq_sessions_rotation_identity"
    ),
    UniqueConstraint("id", "oauth_transaction_id", name="uq_sessions_rotation_binding"),
    # A rotation's account and authentication method equal its predecessor's.
    ForeignKeyConstraint(
        ["rotated_from_session_id", "platform_account_id", "auth_method"],
        ["sessions.id", "sessions.platform_account_id", "sessions.auth_method"],
        name="fk_sessions_rotation_account_method",
        ondelete="RESTRICT",
    ),
    # A rotation's OAuth binding equals its predecessor's.
    ForeignKeyConstraint(
        ["rotated_from_session_id", "oauth_transaction_id"],
        ["sessions.id", "sessions.oauth_transaction_id"],
        name="fk_sessions_rotation_oauth_binding",
        ondelete="RESTRICT",
    ),
)
# OD-44 condition 2 — a rotation chain is linear, and the database says so.
#
# Three declarative facts, none of which depends on the application:
#
# 1. **One successor per predecessor.** A partial unique index over
#    `rotated_from_session_id`, so a session cannot acquire two successors and a
#    chain cannot branch. Partial because the *root* of every chain has no
#    predecessor, and there are many roots.
# 2. **A rotation does not cross accounts or authentication methods.** The
#    successor's `(platform_account_id, auth_method)` must equal its
#    predecessor's, expressed as a composite foreign key into the row it names.
# 3. **A rotation does not cross OAuth bindings.** The successor's
#    `oauth_transaction_id` must equal its predecessor's.
#
# Both foreign keys are `MATCH SIMPLE` (the default), which means they are
# satisfied without a lookup when *any* referencing column is null. That is
# exactly the behaviour wanted here rather than a gap tolerated:
#
# - a root session has `rotated_from_session_id IS NULL`, so neither key applies
#   to it — correct, it has no predecessor to agree with;
# - a break-glass rotation has `oauth_transaction_id IS NULL`, so (3) does not
#   apply — correct, and (2) still binds it to its predecessor's account and
#   method, while `ck_sessions_oauth_transaction_binding` independently refuses a
#   non-`discord_oauth` session that names a transaction. A `discord_oauth`
#   rotation cannot escape (3) by nulling the column, because then the check
#   constraint would demand a different `auth_method` and (2) refuses that.
#
# `MATCH FULL` was rejected: it would require all-null-or-all-non-null and would
# therefore make break-glass rotation impossible, which is a working control
# turned into an outage.
Index(
    "uq_sessions_rotated_from_session_id",
    sessions.c.rotated_from_session_id,
    unique=True,
    postgresql_where=sessions.c.rotated_from_session_id.isnot(None),
)
# `now()` is not immutable, so "currently live" cannot be an index predicate.
# The index carries the columns; the query carries the predicate.
Index("ix_sessions_account_expiry", sessions.c.platform_account_id, sessions.c.absolute_expires_at)
# OD-44. Scoped to the rows a *completion* creates, so one transaction can never
# yield a second session, while N-08 rotation — which mints a new row for the
# same login and therefore carries the same transaction id forward — stays
# possible. Migration 0009's docstring records why the predicate is the one place
# that revision reads the ruling rather than transcribing it.
Index(
    "uq_sessions_oauth_transaction_id",
    sessions.c.oauth_transaction_id,
    unique=True,
    postgresql_where=text("rotated_from_session_id IS NULL"),
)

oauth_transactions = Table(
    "oauth_transactions",
    metadata,
    Column("id", UUID(as_uuid=True), primary_key=True),
    # The state is only ever *compared*, so a hash is sufficient and a plaintext
    # copy would be a stealable value with no use for it.
    Column("state_hash", LargeBinary, nullable=False, unique=True),
    # The PKCE verifier must be *presented* to the provider at the code
    # exchange, so it has to be recoverable: it is encrypted, not hashed. A hash
    # cannot be sent to Discord, and a flow built on one cannot complete.
    Column("pkce_verifier_ciphertext", LargeBinary),
    Column("nonce", LargeBinary),
    Column("key_version", SmallInteger, nullable=False),
    Column("return_path", String(255), nullable=False),
    Column("provider_key", String(120), nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
    Column("expires_at", DateTime(timezone=True), nullable=False),
    Column("consumed_at", DateTime(timezone=True)),
    # OD-44. The second, one-way step after `consumed`. Claimed atomically inside
    # the provider-I/O-free transaction that creates the session and its success
    # audit, and never cleared: a consumed-and-claimed row is terminal.
    Column("completion_claimed_at", DateTime(timezone=True)),
    Column("client_ip_hash", LargeBinary),
    CheckConstraint("expires_at > created_at", name="expiry_after_creation"),
    # A claim without a consumption would be a completion for a transaction whose
    # verifier was never recovered, and so one that cannot have reached the
    # provider. The claim statement requires it too; this is the same rule where
    # a future statement cannot forget it.
    CheckConstraint(
        "completion_claimed_at IS NULL OR consumed_at IS NOT NULL",
        name="completion_requires_consumption",
    ),
    CheckConstraint("length(state_hash) = 32", name="state_hash_length"),
    # The second half is what stops a protocol-relative `//evil.example` ever
    # being stored, let alone reaching a Location header.
    CheckConstraint(
        "return_path LIKE '/%' AND return_path NOT LIKE '//%'", name="return_path_is_a_path"
    ),
    CheckConstraint("(pkce_verifier_ciphertext IS NULL) = (nonce IS NULL)", name="verifier_pairing"),
    # A consumed transaction has no verifier left, and the database says so
    # rather than the application remembering to.
    CheckConstraint(
        "consumed_at IS NULL OR pkce_verifier_ciphertext IS NULL",
        name="consumed_has_no_verifier",
    ),
)
Index("ix_oauth_transactions_expires_at", oauth_transactions.c.expires_at)

webauthn_credentials = Table(
    "webauthn_credentials",
    metadata,
    # The identifier that appears in audit records. The public key never does.
    Column("id", UUID(as_uuid=True), primary_key=True),
    Column(
        "platform_account_id",
        UUID(as_uuid=True),
        ForeignKey("platform_accounts.id", ondelete="RESTRICT"),
        nullable=False,
    ),
    Column("credential_id", LargeBinary, nullable=False, unique=True),
    # A public key is not a secret; it is nonetheless restricted, because it is a
    # fingerprint of a specific authenticator. No attestation object, no private
    # key, no PIN and no biometric material is stored — none of it ever leaves
    # the authenticator.
    Column("public_key", LargeBinary, nullable=False),
    # A decrease is a cloned-authenticator signal and refuses the login.
    Column("sign_count", BIGINT, nullable=False, server_default="0"),
    Column("aaguid", UUID(as_uuid=True)),
    Column("transports", String(60)),
    Column("nickname", String(60)),
    Column("created_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
    # Enrollment is host-local only (C-03): there is no web enrollment route, so
    # a stolen break-glass session cannot enroll an attacker's key.
    Column("created_by_operator", String(120), nullable=False),
    Column("last_used_at", DateTime(timezone=True)),
    Column("disabled_at", DateTime(timezone=True)),
    CheckConstraint("sign_count >= 0", name="sign_count"),
    CheckConstraint("length(trim(created_by_operator)) > 0", name="operator_named"),
)

webauthn_challenges = Table(
    "webauthn_challenges",
    metadata,
    Column("id", UUID(as_uuid=True), primary_key=True),
    # Stored in the clear, deliberately: a WebAuthn challenge is a public nonce
    # that is handed to the browser and then compared byte-for-byte against the
    # authenticator's response. A hash could not be presented as
    # `expected_challenge`, and there is nothing here a hash would protect.
    Column("challenge", LargeBinary, nullable=False, unique=True),
    Column("created_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
    Column("expires_at", DateTime(timezone=True), nullable=False),
    Column("consumed_at", DateTime(timezone=True)),
    Column("client_ip_hash", LargeBinary),
    CheckConstraint("expires_at > created_at", name="expiry_after_creation"),
    CheckConstraint("length(challenge) >= 32", name="length"),
)

recovery_grants = Table(
    "recovery_grants",
    metadata,
    # Named in the audit record. The token never is, and is never stored.
    Column("id", UUID(as_uuid=True), primary_key=True),
    Column(
        "platform_account_id",
        UUID(as_uuid=True),
        ForeignKey("platform_accounts.id", ondelete="RESTRICT"),
        nullable=False,
    ),
    # SHA-256 of a 256-bit random token, and a plain SHA-256 is **correct** here
    # rather than a shortcut: there is no low-entropy guess for a slow hash to
    # slow down, so Argon2 would be cargo cult.
    Column("token_hash", LargeBinary, nullable=False, unique=True),
    Column("purpose", String(40), nullable=False, server_default="emergency_login"),
    Column("created_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
    Column("expires_at", DateTime(timezone=True), nullable=False),
    Column("created_by_operator", String(120), nullable=False),
    Column("consumed_at", DateTime(timezone=True)),
    Column("consumed_session_id", UUID(as_uuid=True), ForeignKey("sessions.id", ondelete="RESTRICT")),
    Column("invalidated_at", DateTime(timezone=True)),
    Column("invalidated_reason", String(60)),
    Column("attempt_count", Integer, nullable=False, server_default="0"),
    Column("audit_correlation_id", UUID(as_uuid=True), nullable=False),
    CheckConstraint("expires_at > created_at", name="expiry_after_creation"),
    CheckConstraint(
        "(consumed_at IS NULL) = (consumed_session_id IS NULL)",
        name="consumption_names_its_session",
    ),
    CheckConstraint("purpose = 'emergency_login'", name="purpose"),
    CheckConstraint("length(token_hash) = 32", name="token_hash_length"),
    CheckConstraint("attempt_count >= 0", name="attempt_count"),
    CheckConstraint(
        "(invalidated_at IS NULL) = (invalidated_reason IS NULL)", name="invalidation_state"
    ),
    CheckConstraint("length(trim(created_by_operator)) > 0", name="operator_named"),
)
# N-61: at most one unconsumed, unexpired grant per account. Two live grants
# double the window with no operational benefit.
Index(
    "uq_recovery_grants_one_live",
    recovery_grants.c.platform_account_id,
    unique=True,
    postgresql_where=recovery_grants.c.consumed_at.is_(None)
    & recovery_grants.c.invalidated_at.is_(None),
)

auth_rate_limits = Table(
    "auth_rate_limits",
    metadata,
    # e.g. `oauth_start:ip:<keyed digest>`. The address is hashed, not stored.
    Column("bucket", String(120), primary_key=True),
    Column("window_start", DateTime(timezone=True), primary_key=True),
    Column("count", Integer, nullable=False, server_default="0"),
    CheckConstraint("count >= 0", name="count_non_negative"),
)
Index("ix_auth_rate_limits_window_start", auth_rate_limits.c.window_start)

role_capability_mappings = Table(
    "role_capability_mappings",
    metadata,
    Column("id", UUID(as_uuid=True), primary_key=True),
    Column("guild_id", BIGINT, nullable=False),
    Column("role_id", BIGINT, nullable=False),
    Column("capability", String(30), nullable=False),
    Column("protected", Boolean, nullable=False, server_default="false"),
    Column("active", Boolean, nullable=False, server_default="true"),
    # Nullable **only** for the protected bootstrap row, which migration 0006
    # inserts at a moment when no platform account exists. The
    # `creator_named_unless_bootstrap` check keeps that from becoming a general
    # licence.
    Column(
        "created_by_account_id",
        UUID(as_uuid=True),
        ForeignKey("platform_accounts.id", ondelete="RESTRICT"),
    ),
    Column("created_under_auth_method", String(20), nullable=False),
    # The creating session's **administrator scope**. This is the column the
    # escalation guard of schema §8.1 keys on, and the one that makes the guard
    # travel with the mapping rather than with the session that wrote it.
    Column("created_under_scope", String(24), nullable=False),
    Column("provenance", String(24), nullable=False),
    Column("ratified_at", DateTime(timezone=True)),
    Column(
        "ratified_by_account_id",
        UUID(as_uuid=True),
        ForeignKey("platform_accounts.id", ondelete="RESTRICT"),
    ),
    Column("created_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
    Column("revoked_at", DateTime(timezone=True)),
    Column(
        "revoked_by_account_id",
        UUID(as_uuid=True),
        ForeignKey("platform_accounts.id", ondelete="RESTRICT"),
    ),
    Column("revoked_under_auth_method", String(20)),
    Column("revoked_under_scope", String(24)),
    Column("reason", Text, nullable=False),
    Column("audit_correlation_id", UUID(as_uuid=True), nullable=False),
    Column("version", Integer, nullable=False, server_default="0"),
    CheckConstraint("guild_id > 0", name="guild_id"),
    CheckConstraint("role_id > 0", name="role_id"),
    # `ActorCapability` minus the two machine capabilities. A Discord role can
    # never map to `system` or `service_principal`: a human holding a role is not
    # a service.
    CheckConstraint(
        "capability IN ('guild_member', 'character_owner', 'dm', 'guild_council', "
        "'platform_administrator')",
        name="capability",
    ),
    CheckConstraint(
        "created_under_scope IN ('full', 'emergency_continuity')", name="created_under_scope"
    ),
    CheckConstraint("provenance IN ('ordinary', 'emergency_continuity')", name="provenance"),
    CheckConstraint(
        "created_under_auth_method IN ('discord_oauth', 'webauthn', 'recovery_grant')",
        name="created_under_auth_method",
    ),
    # ------------------------------------------------------------------
    # N-67, in the database, and the reason it is here rather than only in the
    # service: **this check does not depend on the session at all.** It depends
    # on what is being written, so it holds when the application is wrong,
    # bypassed, or replaced by a future service that forgets.
    # ------------------------------------------------------------------
    CheckConstraint(
        "created_under_scope = 'full' OR capability = 'platform_administrator'",
        name="continuity_create_allowlist",
    ),
    CheckConstraint(
        "revoked_under_scope IS NULL OR revoked_under_scope = 'full' "
        "OR capability = 'platform_administrator'",
        name="continuity_revoke_allowlist",
    ),
    # Provenance is not an independent fact an application may set as it likes;
    # it is exactly "created under a continuity scope and not yet ratified".
    CheckConstraint(
        "(created_under_scope = 'emergency_continuity' AND ratified_at IS NULL) "
        "= (provenance = 'emergency_continuity')",
        name="provenance_is_derived",
    ),
    CheckConstraint(
        "(ratified_at IS NULL) = (ratified_by_account_id IS NULL)",
        name="ratification_names_its_actor",
    ),
    CheckConstraint("ratified_at IS NULL OR ratified_at >= created_at", name="ratified_after_creation"),
    CheckConstraint(
        "(revoked_at IS NULL) = (revoked_under_scope IS NULL)", name="revocation_names_its_scope"
    ),
    CheckConstraint(
        "(revoked_at IS NULL) = (revoked_by_account_id IS NULL)", name="revocation_names_its_actor"
    ),
    CheckConstraint(
        "(active AND revoked_at IS NULL) OR (NOT active AND revoked_at IS NOT NULL)",
        name="revocation_state",
    ),
    CheckConstraint("length(trim(reason)) > 0", name="reason_not_blank"),
    CheckConstraint(
        "created_by_account_id IS NOT NULL OR protected", name="creator_named_unless_bootstrap"
    ),
    CheckConstraint("version >= 0", name="version"),
)
# Partial, so a revoked mapping stays as history and re-mapping inserts a new
# row — exactly as `character_access` already does.
Index(
    "uq_role_capability_mappings_active",
    role_capability_mappings.c.guild_id,
    role_capability_mappings.c.role_id,
    role_capability_mappings.c.capability,
    unique=True,
    postgresql_where=role_capability_mappings.c.active,
)
Index(
    "ix_role_capability_mappings_resolution",
    role_capability_mappings.c.guild_id,
    role_capability_mappings.c.role_id,
    postgresql_where=role_capability_mappings.c.active,
)

role_capability_mapping_events = Table(
    "role_capability_mapping_events",
    metadata,
    Column("id", UUID(as_uuid=True), primary_key=True),
    Column("occurred_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
    # Null for a create that was refused before a row existed.
    Column("mapping_id", UUID(as_uuid=True)),
    Column("operation", String(20), nullable=False),
    Column("outcome", String(12), nullable=False),
    Column("refusal_code", String(40)),
    Column("guild_id", BIGINT, nullable=False),
    Column("role_id", BIGINT, nullable=False),
    # Recorded even for a refusal, deliberately: "a break-glass session tried to
    # map a role to Council" is precisely the sentence an incident review needs,
    # and it exists nowhere else if the refusal writes only a counter.
    Column("capability", String(30), nullable=False),
    Column(
        "actor_account_id",
        UUID(as_uuid=True),
        ForeignKey("platform_accounts.id", ondelete="RESTRICT"),
        nullable=False,
    ),
    Column("auth_method", String(20), nullable=False),
    Column("scope", String(24), nullable=False),
    Column("reason", Text),
    Column("correlation_id", UUID(as_uuid=True), nullable=False),
    CheckConstraint("operation IN ('create', 'revoke', 'ratify')", name="operation"),
    CheckConstraint("outcome IN ('applied', 'refused')", name="outcome"),
    CheckConstraint("(outcome = 'refused') = (refusal_code IS NOT NULL)", name="refusal_is_coded"),
    CheckConstraint(
        "auth_method IN ('discord_oauth', 'webauthn', 'recovery_grant')", name="auth_method"
    ),
    CheckConstraint("scope IN ('full', 'emergency_continuity')", name="scope"),
)
Index(
    "ix_role_capability_mapping_events_mapping",
    role_capability_mapping_events.c.mapping_id,
    role_capability_mapping_events.c.occurred_at,
)

# ---------------------------------------------------------------------------
# P3.2 — Sheet-era identity-evidence proposals (M-2)
# ---------------------------------------------------------------------------
#
# Three tables where the accepted schema decision table (§11) names one. The
# addition is deliberate and is recorded in the P3.2 submission rather than made
# quietly, because §11 gave `identity_link_proposals` a one-line row — primary
# key, character foreign key, `(run_id, character_id)` uniqueness, writer,
# reader, retention — and left its columns to the owning package, while the
# migration contract §7.4 and §7.6 require two things that one flat row cannot
# hold without a prohibited container:
#
# 1. **Source-side control totals.** `source_characters` and `source_players`
#    are facts about the *run*, and `source_players` cannot hang off a proposal
#    at all: a player with no character produces no proposal row. They therefore
#    live on a run, which is what `identity_migration_runs` is.
# 2. **Every candidate of an ambiguous proposal, durably.** §7.6 requires the
#    ambiguity to persist as an explicit record. Plan §7.3.1 prohibits delimited
#    text, JSON/JSONB collections and PostgreSQL arrays for multi-valued facts
#    and prescribes "typed foreign-keyed child rows" instead, and TC-STRUCT-03
#    asserts that no third JSONB column appears in this schema. A child table is
#    therefore the only compliant representation, not a preference.
#
# Nothing here is authorization-bearing by itself. A proposal is evidence; the
# only row that ever confers reach over a character is a `character_access` row
# written by the one service R-25 and R-29 share, and `granted_access_id` below
# records which one a confirmation produced rather than producing it.

identity_migration_runs = Table(
    "identity_migration_runs",
    metadata,
    Column("id", UUID(as_uuid=True), primary_key=True),
    Column("produced_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
    # Always `true`, and `CHECK`-ed rather than merely defaulted. Every row in
    # this table is a **C-04 evidence run**: it read `Characters C` and
    # `Players A/B/D` through the read-only boundary and wrote no
    # `character_access` row. Stating it as a constraint makes "this table holds
    # evidence runs" a fact about the table rather than about which code path
    # inserted the row. VM-10 renders it.
    Column("dry_run", Boolean, nullable=False, server_default="true"),
    # A **label** for the source ranges, never the spreadsheet id and never a
    # credential. "Characters!C + Players!A,B,D" is the whole of what a reader
    # needs, and it is the whole of what is stored.
    Column("source_label", String(120), nullable=False),
    Column("profile_version", String(64), nullable=False),
    # §7.4's source side. Counted at run time, never assumed.
    Column("source_characters", Integer, nullable=False),
    Column("source_players", Integer, nullable=False),
    # The run's own bucket counts, immutable once written. They are the
    # *right-hand* side of §7.4's second balance, and they have to be stored
    # rather than counted from the proposal rows because a Council confirmation
    # changes a row's `resolution` in place: counting live would make
    # `confirmed + rejected + outstanding = proposed + ambiguous + unresolved`
    # true by construction and therefore worth nothing.
    #
    # `already_linked` is a count and never a proposal row. The character already
    # has an active access row for that account, so there is nothing to propose
    # and VM-10's closed `resolution` vocabulary has no member for it (migration
    # contract §7.3: "counted, not proposed").
    Column("already_linked", Integer, nullable=False),
    Column("proposed", Integer, nullable=False),
    Column("ambiguous", Integer, nullable=False),
    Column("unresolved", Integer, nullable=False),
    Column("correlation_id", UUID(as_uuid=True), nullable=False),
    # **No apply state.** A Guild Council confirmation activates the link
    # immediately (migration contract §7.2 as amended by change-log entry
    # C-P3.2-A), so there is no gap between deciding and linking for a run-level
    # `applied_at` to describe. The columns an earlier draft carried for the
    # withdrawn C-05 command are removed rather than left nullable and unused.
    CheckConstraint("dry_run", name="run_is_a_c04_evidence_run"),
    CheckConstraint("length(trim(source_label)) > 0", name="source_label_not_blank"),
    CheckConstraint("length(trim(profile_version)) > 0", name="profile_version_not_blank"),
    CheckConstraint("source_characters >= 0", name="source_characters_non_negative"),
    CheckConstraint("source_players >= 0", name="source_players_non_negative"),
    CheckConstraint(
        "already_linked >= 0 AND proposed >= 0 AND ambiguous >= 0 AND unresolved >= 0",
        name="buckets_non_negative",
    ),
    # §7.4's first balance, as a constraint. "Every source row lands in exactly
    # one bucket" is the plan's *"no identity discrepancy is silently accepted"*
    # (§0.5), and an unbalanced run is refused by PostgreSQL rather than reported
    # as a warning a reader may skip.
    CheckConstraint(
        "already_linked + proposed + ambiguous + unresolved = source_characters",
        name="buckets_balance_against_source",
    ),
)

identity_link_proposals = Table(
    "identity_link_proposals",
    metadata,
    Column("id", UUID(as_uuid=True), primary_key=True),
    Column(
        "run_id",
        UUID(as_uuid=True),
        ForeignKey("identity_migration_runs.id", ondelete="CASCADE"),
        nullable=False,
    ),
    Column(
        "character_id",
        UUID(as_uuid=True),
        ForeignKey("characters.id", ondelete="CASCADE"),
        nullable=False,
    ),
    # -- evidence, and nothing but evidence ---------------------------------
    # `Characters C`, `Players B` and `Players D`. A username changes and one
    # Discord name is recorded per player, so none of the three can be an
    # identity (migration contract §7.1) and `active_dm` confers no capability
    # whatever (OD-18). They are stored so a Council member can see what the
    # proposal was derived from, and for no other purpose.
    Column("sheet_player_name", Text, nullable=False),
    Column("sheet_discord_name", Text),
    Column("active_dm", Boolean, nullable=False, server_default="false"),
    # The only identity in this table: a Discord snowflake as a canonical
    # decimal string, resolved from the membership projection. Null whenever the
    # evidence resolved to no single member.
    Column("proposed_subject", String(255)),
    Column("resolution", String(20), nullable=False),
    # -- Council decision ----------------------------------------------------
    Column("decided_at", DateTime(timezone=True)),
    Column(
        "decided_by_account_id",
        UUID(as_uuid=True),
        ForeignKey("platform_accounts.id", ondelete="RESTRICT"),
    ),
    Column("decision_reason", Text),
    # The `character_access` row this confirmation created. Non-null exactly on a
    # `confirmed` row, and written in the same statement as the decision, so a
    # confirmation and its authorization cannot come apart. `RESTRICT` because
    # the access row may not be removed out from under the decision that created
    # it.
    Column(
        "granted_access_id",
        UUID(as_uuid=True),
        ForeignKey("character_access.id", ondelete="RESTRICT"),
    ),
    Column("audit_correlation_id", UUID(as_uuid=True), nullable=False),
    UniqueConstraint("run_id", "character_id", name="uq_identity_link_proposals_run_character"),
    # Exactly VM-10's closed vocabulary. `already_linked` is deliberately not a
    # member: it is a run-level count, because there is no proposal to make.
    CheckConstraint(
        "resolution IN ('proposed', 'ambiguous', 'unresolved', 'confirmed', 'rejected')",
        name="resolution",
    ),
    CheckConstraint("length(trim(sheet_player_name)) > 0", name="player_name_not_blank"),
    # A resolved subject is exactly what `proposed` and `confirmed` mean, and a
    # decision is exactly what `confirmed` and `rejected` mean. Both are stated
    # as constraints so a service cannot write a half-decided row.
    CheckConstraint(
        "(resolution IN ('proposed', 'confirmed')) = (proposed_subject IS NOT NULL)",
        name="resolved_subject_matches_resolution",
    ),
    CheckConstraint(
        "(resolution IN ('confirmed', 'rejected')) = (decided_at IS NOT NULL)",
        name="decision_state",
    ),
    CheckConstraint("(decided_at IS NULL) = (decided_by_account_id IS NULL)", name="decider"),
    # §7.2's whole pipeline, as one constraint: a confirmation **is** a link and
    # nothing else is. A `proposed`, `ambiguous`, `unresolved` or `rejected` row
    # carrying a grant is refused, and so is a `confirmed` row naming none — so
    # neither "C-04 authorized something" nor "a confirmation was recorded
    # without its access row" is a state this table can hold. The database says
    # it rather than the service remembering to.
    CheckConstraint(
        "(granted_access_id IS NOT NULL) = (resolution = 'confirmed')",
        name="a_confirmation_is_a_link",
    ),
    CheckConstraint(
        "decision_reason IS NULL OR length(trim(decision_reason)) > 0",
        name="decision_reason_not_blank",
    ),
    # R-29 and R-30 both **require** a reason, and the restricted runtime role
    # holds `UPDATE` on this table — so a rule the service checks is a rule the
    # database has to state as well, or a half-decided row is one direct
    # statement away. Paired with the constraint above, which bans a blank one
    # everywhere: together they make `confirmed` and `rejected` carry a non-null,
    # non-blank trimmed reason, and `proposed`, `ambiguous` and `unresolved`
    # carry none at all. An outstanding row with a reason would be a decision
    # nobody made.
    CheckConstraint(
        "(resolution IN ('confirmed', 'rejected')) = (decision_reason IS NOT NULL)",
        name="a_decision_states_its_reason",
    ),
)
Index(
    "ix_identity_link_proposals_run",
    identity_link_proposals.c.run_id,
    identity_link_proposals.c.resolution,
    identity_link_proposals.c.id,
)
Index(
    "ix_identity_link_proposals_character",
    identity_link_proposals.c.character_id,
)

identity_link_proposal_candidates = Table(
    "identity_link_proposal_candidates",
    metadata,
    Column("id", UUID(as_uuid=True), primary_key=True),
    Column(
        "proposal_id",
        UUID(as_uuid=True),
        ForeignKey("identity_link_proposals.id", ondelete="CASCADE"),
        nullable=False,
    ),
    # One row per member whose username matched. Typed child rows rather than a
    # delimited column or an array (plan §7.3.1), so "which candidates were
    # there?" is a query rather than a parse.
    Column("subject", String(255), nullable=False),
    Column("observed_username", Text, nullable=False),
    UniqueConstraint(
        "proposal_id", "subject", name="uq_identity_link_proposal_candidates_subject"
    ),
    CheckConstraint("length(trim(subject)) > 0", name="subject_not_blank"),
)
