"""Create Phase 1 identity and transaction foundation.

Revision ID: 0001
Revises:
Create Date: 2026-07-30
"""
from typing import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "discord_users",
        sa.Column("id", sa.BIGINT(), autoincrement=False, nullable=False),
        sa.Column("username", sa.String(80), nullable=False),
        sa.Column("global_name", sa.String(80)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("id > 0", name=op.f("ck_discord_users_positive_id")),
        sa.CheckConstraint("length(trim(username)) > 0", name=op.f("ck_discord_users_username_not_blank")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_discord_users")),
    )
    op.create_table(
        "characters",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("display_name", sa.String(120), nullable=False),
        sa.Column("long_name", sa.String(240)),
        # Nullable while an imported identity awaits Council reconciliation.
        sa.Column("level", sa.Integer()),
        sa.Column("active", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("version", sa.Integer(), server_default="0", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("length(trim(display_name)) > 0", name=op.f("ck_characters_display_name_not_blank")),
        sa.CheckConstraint("level IS NULL OR level BETWEEN 1 AND 20", name=op.f("ck_characters_level_range")),
        sa.CheckConstraint("version >= 0", name=op.f("ck_characters_version_non_negative")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_characters")),
    )
    op.create_table(
        "discord_guild_memberships",
        sa.Column("discord_user_id", sa.BIGINT(), nullable=False),
        sa.Column("guild_id", sa.BIGINT(), nullable=False),
        sa.Column("active", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("observed_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("guild_id > 0", name=op.f("ck_discord_guild_memberships_positive_guild_id")),
        sa.ForeignKeyConstraint(["discord_user_id"], ["discord_users.id"], ondelete="CASCADE", name=op.f("fk_discord_guild_memberships_discord_user_id_discord_users")),
        sa.PrimaryKeyConstraint("discord_user_id", "guild_id", name=op.f("pk_discord_guild_memberships")),
    )
    op.create_table(
        "discord_membership_roles",
        sa.Column("discord_user_id", sa.BIGINT(), nullable=False),
        sa.Column("guild_id", sa.BIGINT(), nullable=False),
        sa.Column("role_id", sa.BIGINT(), nullable=False),
        sa.CheckConstraint("role_id > 0", name=op.f("ck_discord_membership_roles_positive_role_id")),
        sa.ForeignKeyConstraint(
            ["discord_user_id", "guild_id"],
            ["discord_guild_memberships.discord_user_id", "discord_guild_memberships.guild_id"],
            ondelete="CASCADE",
            name=op.f("fk_discord_membership_roles_discord_user_id_guild_id_discord_guild_memberships"),
        ),
        sa.PrimaryKeyConstraint("discord_user_id", "guild_id", "role_id", name=op.f("pk_discord_membership_roles")),
    )
    op.create_table(
        "character_access",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("character_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("discord_user_id", sa.BIGINT(), nullable=False),
        sa.Column("access_kind", sa.String(20), nullable=False),
        sa.Column("active", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("default_character", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("granted_by_discord_user_id", sa.BIGINT(), nullable=False),
        sa.Column("granted_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True)),
        sa.Column("expires_at", sa.DateTime(timezone=True)),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("audit_correlation_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.CheckConstraint("access_kind IN ('owner', 'co_owner', 'delegate', 'viewer')", name=op.f("ck_character_access_access_kind")),
        sa.CheckConstraint("length(trim(reason)) > 0", name=op.f("ck_character_access_reason_not_blank")),
        sa.CheckConstraint("(active AND revoked_at IS NULL) OR (NOT active AND revoked_at IS NOT NULL)", name=op.f("ck_character_access_revocation_state")),
        sa.CheckConstraint("revoked_at IS NULL OR revoked_at >= granted_at", name=op.f("ck_character_access_revoked_after_grant")),
        sa.CheckConstraint("expires_at IS NULL OR expires_at > granted_at", name=op.f("ck_character_access_expiry_after_grant")),
        sa.ForeignKeyConstraint(["character_id"], ["characters.id"], ondelete="CASCADE", name=op.f("fk_character_access_character_id_characters")),
        sa.ForeignKeyConstraint(["discord_user_id"], ["discord_users.id"], ondelete="RESTRICT", name=op.f("fk_character_access_discord_user_id_discord_users")),
        sa.ForeignKeyConstraint(["granted_by_discord_user_id"], ["discord_users.id"], ondelete="RESTRICT", name=op.f("fk_character_access_granted_by_discord_user_id_discord_users")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_character_access")),
    )
    # Active links are unique; revoked rows remain as history and may repeat.
    op.create_index(
        "uq_character_access_one_active_link",
        "character_access",
        ["character_id", "discord_user_id"],
        unique=True,
        postgresql_where=sa.text("active"),
    )
    # OD-37: at most one active owner per character. Requiring at least one is an
    # application invariant — the Phase 2 importer creates a character before
    # Council has resolved ownership.
    op.create_index(
        "uq_character_access_one_active_owner",
        "character_access",
        ["character_id"],
        unique=True,
        postgresql_where=sa.text("active AND access_kind = 'owner'"),
    )
    op.create_index(
        "uq_character_access_one_active_default_per_user",
        "character_access",
        ["discord_user_id"],
        unique=True,
        postgresql_where=sa.text("active AND default_character"),
    )
    op.create_table(
        "external_actor_mappings",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("character_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("world_id", sa.String(120), nullable=False),
        sa.Column("external_actor_id", sa.String(64), nullable=False),
        sa.Column("last_instance", sa.String(255)),
        sa.Column("relink_fingerprint", sa.String(255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("length(trim(world_id)) > 0", name=op.f("ck_external_actor_mappings_world_id_not_blank")),
        sa.CheckConstraint("external_actor_id ~ '^[A-Za-z0-9]{16}$'", name=op.f("ck_external_actor_mappings_actor_id_shape")),
        sa.CheckConstraint("length(trim(relink_fingerprint)) > 0", name=op.f("ck_external_actor_mappings_fingerprint_not_blank")),
        sa.ForeignKeyConstraint(["character_id"], ["characters.id"], ondelete="CASCADE", name=op.f("fk_external_actor_mappings_character_id_characters")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_external_actor_mappings")),
        sa.UniqueConstraint("world_id", "external_actor_id", name=op.f("uq_external_actor_mappings_world_id_external_actor_id")),
        sa.UniqueConstraint("character_id", "world_id", name=op.f("uq_external_actor_mappings_character_id_world_id")),
    )
    op.create_table(
        "sheet_row_mappings",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("character_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("sheet_tab", sa.String(120), nullable=False),
        sa.Column("row_index", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("length(trim(sheet_tab)) > 0", name=op.f("ck_sheet_row_mappings_sheet_tab_not_blank")),
        sa.CheckConstraint("row_index > 0", name=op.f("ck_sheet_row_mappings_row_index_positive")),
        sa.ForeignKeyConstraint(["character_id"], ["characters.id"], ondelete="CASCADE", name=op.f("fk_sheet_row_mappings_character_id_characters")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_sheet_row_mappings")),
        sa.UniqueConstraint("sheet_tab", "row_index", name=op.f("uq_sheet_row_mappings_sheet_tab_row_index")),
        sa.UniqueConstraint("character_id", "sheet_tab", name=op.f("uq_sheet_row_mappings_character_id_sheet_tab")),
    )
    op.create_table(
        "audit_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("occurred_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        # Nullable for import, scheduled and system actions; RESTRICT so a user
        # carrying audit history cannot be deleted without an explicit decision.
        sa.Column("actor_discord_user_id", sa.BIGINT()),
        # The authority the action was taken under (plan §4.1/§4.3, OD-37).
        sa.Column("actor_capability", sa.String(30), nullable=False),
        sa.Column("action", sa.String(120), nullable=False),
        sa.Column("entity_type", sa.String(80), nullable=False),
        sa.Column("entity_id", sa.String(120), nullable=False),
        sa.Column("source", sa.String(20), nullable=False),
        sa.Column("correlation_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.CheckConstraint(
            "actor_capability IN ('guild_member', 'character_owner', 'dm', "
            "'guild_council', 'platform_administrator', 'service_principal', 'system')",
            name=op.f("ck_audit_events_actor_capability"),
        ),
        sa.CheckConstraint(
            "actor_discord_user_id IS NOT NULL "
            "OR actor_capability IN ('service_principal', 'system')",
            name=op.f("ck_audit_events_human_action_has_an_actor"),
        ),
        sa.CheckConstraint("source IN ('discord', 'web', 'foundry', 'import', 'system')", name=op.f("ck_audit_events_source")),
        sa.CheckConstraint("length(trim(action)) > 0", name=op.f("ck_audit_events_action_not_blank")),
        sa.CheckConstraint("length(trim(entity_type)) > 0", name=op.f("ck_audit_events_entity_type_not_blank")),
        sa.ForeignKeyConstraint(["actor_discord_user_id"], ["discord_users.id"], ondelete="RESTRICT", name=op.f("fk_audit_events_actor_discord_user_id_discord_users")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_audit_events")),
    )
    op.create_index("ix_audit_events_correlation_id", "audit_events", ["correlation_id"])
    op.create_index("ix_audit_events_entity", "audit_events", ["entity_type", "entity_id", "occurred_at"])
    op.create_table(
        "idempotency_keys",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("scope", sa.String(120), nullable=False),
        sa.Column("key", sa.String(255), nullable=False),
        sa.Column("request_hash", sa.LargeBinary(32), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("response", postgresql.JSONB(astext_type=sa.Text())),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True)),
        sa.CheckConstraint("status IN ('started', 'completed', 'failed')", name=op.f("ck_idempotency_keys_status")),
        sa.CheckConstraint("length(request_hash) = 32", name=op.f("ck_idempotency_keys_request_hash_sha256")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_idempotency_keys")),
        sa.UniqueConstraint("scope", "key", name=op.f("uq_idempotency_keys_scope_key")),
    )


def downgrade() -> None:
    # DROP TABLE removes the table's own indexes, so they are not dropped
    # separately: naming them here would make the downgrade fail against any
    # database whose index set differs.
    op.drop_table("idempotency_keys")
    op.drop_table("audit_events")
    op.drop_table("sheet_row_mappings")
    op.drop_table("external_actor_mappings")
    op.drop_table("character_access")
    op.drop_table("discord_membership_roles")
    op.drop_table("discord_guild_memberships")
    op.drop_table("characters")
    op.drop_table("discord_users")
