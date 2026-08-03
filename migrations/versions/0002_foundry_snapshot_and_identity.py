"""Create the Phase 2 snapshot, import and provenance schema.

Adds, in one migration because they are one contract:

- `foundry_snapshots` — the immutable, content-addressed artifact record;
- `snapshot_imports` — one row per apply attempt, keyed twice: by request key
  (the attempt) and, for applied rows only, by (snapshot, folder, profile
  version) (the input);
- `platform_initialization` — the one-row record that disables the supervised
  first-import bootstrap after its first success;
- provenance columns on `external_actor_mappings`; and
- `reject_history_mutation()` triggers making the append-only tables
  append-only **in the database**, not only in the application.

## Why this revision replaced an earlier `0002`

An earlier `0002_foundry_snapshot_and_character_state` also created
`character_state_values`, `character_balances` and `character_transactions` —
the profile-driven store proposed by ADR 0008. The Acceptance Authority
**rejected** ADR 0008 on 2026-08-02 (OD-41, controlled baseline v1.1): Phase 2
does not migrate Sheet-era state, and each field group migrates once into the
typed model introduced by its owning package.

That earlier revision was **never committed and never applied to a durable
environment** — only to the disposable `freedom_test` database — so it was
replaced in place rather than corrected by a follow-on migration. Plan §14.3's
"applied migrations are never edited" protects migrations that exist in
committed history or in a real environment; this one was in neither. The
replacement is recorded in the Phase 2 submission so the substitution is visible
rather than inferred from a diff.

`TRUNCATE` is deliberately **not** trigger-blocked: the runtime role is denied it
by grant (`infra/postgresql/runtime-grants.sql.tmpl`), while the owner keeps it
so that a disposable test database can be reset. The triggers apply to the
schema owner too, so exceptional recovery is `ALTER TABLE … DISABLE TRIGGER`,
executed deliberately by the owner outside the application and recorded in the
operations log — which is what plan §6.5 means by "exceptional database-owner
recovery is outside the application, follows a documented procedure and cannot
be presented as ordinary history".

Revision ID: 0002
Revises: 0001
Create Date: 2026-08-03
"""
from typing import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0002"
down_revision: str | None = "0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

APPEND_ONLY_TABLES = (
    "audit_events",
    "foundry_snapshots",
    "snapshot_imports",
)


def upgrade() -> None:
    op.create_table(
        "foundry_snapshots",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("checksum", sa.String(64), nullable=False),
        sa.Column("size_bytes", sa.Integer(), nullable=False),
        sa.Column("schema_version", sa.Integer(), nullable=False),
        sa.Column("exporter_id", sa.String(120), nullable=False),
        sa.Column("exporter_version", sa.String(32), nullable=False),
        sa.Column("exported_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("world_id", sa.String(120), nullable=False),
        sa.Column("world_title", sa.String(200), nullable=False),
        sa.Column("core_version", sa.String(32), nullable=False),
        sa.Column("system_id", sa.String(64), nullable=False),
        sa.Column("system_version", sa.String(32), nullable=False),
        sa.Column("actor_count", sa.Integer(), nullable=False),
        sa.Column("selected_folder_ids", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        # A reference into the restricted artifact store, never the bytes.
        sa.Column("artifact_location", sa.Text()),
        sa.Column("received_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("received_by_discord_user_id", sa.BIGINT()),
        sa.Column("correlation_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.CheckConstraint("checksum ~ '^[0-9a-f]{64}$'", name=op.f("ck_foundry_snapshots_checksum_sha256_hex")),
        sa.CheckConstraint("size_bytes > 0", name=op.f("ck_foundry_snapshots_size_positive")),
        sa.CheckConstraint("actor_count >= 0", name=op.f("ck_foundry_snapshots_actor_count_non_negative")),
        sa.CheckConstraint("schema_version > 0", name=op.f("ck_foundry_snapshots_schema_version_positive")),
        sa.ForeignKeyConstraint(
            ["received_by_discord_user_id"],
            ["discord_users.id"],
            ondelete="RESTRICT",
            name=op.f("fk_foundry_snapshots_received_by_discord_user_id_discord_users"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_foundry_snapshots")),
        sa.UniqueConstraint("checksum", name=op.f("uq_foundry_snapshots_checksum")),
    )

    op.create_table(
        "snapshot_imports",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("snapshot_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("folder_id", sa.String(64), nullable=False),
        sa.Column("folder_path", sa.Text(), nullable=False),
        sa.Column("profile_version", sa.String(64), nullable=False),
        sa.Column("request_key", sa.String(255), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("mode", sa.String(20), nullable=False),
        sa.Column("actor_discord_user_id", sa.BIGINT()),
        sa.Column("actor_capability", sa.String(30), nullable=False),
        sa.Column("supervisor", sa.String(120)),
        sa.Column("created_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("updated_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("warning_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("summary", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("occurred_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("correlation_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.CheckConstraint("status IN ('applied', 'refused')", name=op.f("ck_snapshot_imports_status")),
        sa.CheckConstraint("mode IN ('bootstrap', 'council')", name=op.f("ck_snapshot_imports_mode")),
        sa.CheckConstraint(
            "actor_capability IN ('guild_council', 'platform_administrator', 'system')",
            name=op.f("ck_snapshot_imports_actor_capability"),
        ),
        sa.CheckConstraint(
            "created_count >= 0 AND updated_count >= 0 AND warning_count >= 0",
            name=op.f("ck_snapshot_imports_counts_non_negative"),
        ),
        sa.ForeignKeyConstraint(
            ["snapshot_id"],
            ["foundry_snapshots.id"],
            ondelete="RESTRICT",
            name=op.f("fk_snapshot_imports_snapshot_id_foundry_snapshots"),
        ),
        sa.ForeignKeyConstraint(
            ["actor_discord_user_id"],
            ["discord_users.id"],
            ondelete="RESTRICT",
            name=op.f("fk_snapshot_imports_actor_discord_user_id_discord_users"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_snapshot_imports")),
        sa.UniqueConstraint("request_key", name=op.f("uq_snapshot_imports_request_key")),
    )
    # Only an *applied* row claims the input identity, so a refusal never blocks
    # the corrected retry, and two applies of the same input cannot both win.
    op.create_index(
        "uq_snapshot_imports_applied_input",
        "snapshot_imports",
        ["snapshot_id", "folder_id", "profile_version"],
        unique=True,
        postgresql_where=sa.text("status = 'applied'"),
    )
    op.create_index(
        "ix_snapshot_imports_correlation_id", "snapshot_imports", ["correlation_id"]
    )

    op.add_column(
        "external_actor_mappings",
        sa.Column("established_by_snapshot_id", postgresql.UUID(as_uuid=True)),
    )
    op.add_column("external_actor_mappings", sa.Column("folder_id", sa.String(64)))
    op.create_foreign_key(
        op.f("fk_external_actor_mappings_established_by_snapshot_id_foundry_snapshots"),
        "external_actor_mappings",
        "foundry_snapshots",
        ["established_by_snapshot_id"],
        ["id"],
        ondelete="RESTRICT",
    )

    op.create_table(
        "platform_initialization",
        sa.Column("singleton", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("initialized_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("supervisor", sa.String(120), nullable=False),
        sa.Column("snapshot_checksum", sa.String(64)),
        sa.Column("profile_version", sa.String(64), nullable=False),
        sa.Column("correlation_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.CheckConstraint("singleton", name=op.f("ck_platform_initialization_single_row")),
        sa.CheckConstraint("length(trim(supervisor)) > 0", name=op.f("ck_platform_initialization_supervisor_not_blank")),
        sa.PrimaryKeyConstraint("singleton", name=op.f("pk_platform_initialization")),
    )

    op.execute(
        """
        CREATE OR REPLACE FUNCTION reject_history_mutation() RETURNS trigger AS $$
        BEGIN
            RAISE EXCEPTION
                'append-only table %: % is refused. History is corrected by '
                'appending a compensating record, never by editing it.',
                TG_TABLE_NAME, TG_OP
                USING ERRCODE = 'restrict_violation';
        END;
        $$ LANGUAGE plpgsql;
        """
    )
    for table in APPEND_ONLY_TABLES:
        op.execute(
            f"""
            CREATE TRIGGER {table}_append_only
            BEFORE UPDATE OR DELETE ON {table}
            FOR EACH ROW EXECUTE FUNCTION reject_history_mutation();
            """
        )


def downgrade() -> None:
    for table in APPEND_ONLY_TABLES:
        op.execute(f"DROP TRIGGER IF EXISTS {table}_append_only ON {table};")
    op.execute("DROP FUNCTION IF EXISTS reject_history_mutation();")

    op.drop_table("platform_initialization")
    op.drop_constraint(
        op.f("fk_external_actor_mappings_established_by_snapshot_id_foundry_snapshots"),
        "external_actor_mappings",
        type_="foreignkey",
    )
    op.drop_column("external_actor_mappings", "folder_id")
    op.drop_column("external_actor_mappings", "established_by_snapshot_id")
    op.drop_index("ix_snapshot_imports_correlation_id", table_name="snapshot_imports")
    op.drop_index("uq_snapshot_imports_applied_input", table_name="snapshot_imports")
    op.drop_table("snapshot_imports")
    op.drop_table("foundry_snapshots")
