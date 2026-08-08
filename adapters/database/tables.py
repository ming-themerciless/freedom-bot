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
    String,
    Table,
    Text,
    UniqueConstraint,
    func,
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
    Column("discord_user_id", BIGINT, ForeignKey("discord_users.id", ondelete="RESTRICT"), nullable=False),
    Column("access_kind", String(20), nullable=False),
    Column("active", Boolean, nullable=False, server_default="true"),
    Column("default_character", Boolean, nullable=False, server_default="false"),
    Column("granted_by_discord_user_id", BIGINT, ForeignKey("discord_users.id", ondelete="RESTRICT"), nullable=False),
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
    CheckConstraint(
        "actor_discord_user_id IS NOT NULL "
        "OR actor_capability IN ('service_principal', 'system')",
        name="human_action_has_an_actor",
    ),
    CheckConstraint("source IN ('discord', 'web', 'foundry', 'import', 'system')", name="source"),
    CheckConstraint("length(trim(action)) > 0", name="action_not_blank"),
    CheckConstraint("length(trim(entity_type)) > 0", name="entity_type_not_blank"),
)
Index("ix_audit_events_entity", audit_events.c.entity_type, audit_events.c.entity_id, audit_events.c.occurred_at)
Index("ix_audit_events_correlation_id", audit_events.c.correlation_id)

#: Tables the application may only append to. The runtime role holds
#: `SELECT, INSERT` on each, and a database trigger rejects `UPDATE`/`DELETE`
#: even for the schema owner, so an accidental repair is a visible act of DDL
#: rather than a quiet row edit.
APPEND_ONLY_TABLES = (
    "audit_events",
    "foundry_snapshots",
    "snapshot_imports",
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

idempotency_keys = Table(
    "idempotency_keys",
    metadata,
    Column("id", UUID(as_uuid=True), primary_key=True),
    Column("scope", String(120), nullable=False),
    Column("key", String(255), nullable=False),
    Column("request_hash", LargeBinary(32), nullable=False),
    Column("status", String(20), nullable=False),
    Column("response", json_type),
    Column("created_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
    Column("expires_at", DateTime(timezone=True)),
    UniqueConstraint("scope", "key"),
    CheckConstraint("status IN ('started', 'completed', 'failed')", name="status"),
    CheckConstraint("length(request_hash) = 32", name="request_hash_sha256"),
)
