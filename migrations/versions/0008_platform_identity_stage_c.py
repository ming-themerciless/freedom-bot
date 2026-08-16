"""Stage C of the identity migration: the Discord column becomes a shadow.

`docs/contracts/phase-3-identity-migration-contract.md` §3, stage C. From here the
application reads and writes `platform_account_id` exclusively, and
`character_access.discord_user_id` is maintained by a database trigger instead of
by the code that writes the row.

## Why a trigger rather than "the application keeps both current"

Until stage D drops the legacy columns, the Discord-keyed unique indexes from
migration 0001 are still enforcing. If new code wrote only the account column,
those indexes would be enforcing over a column nobody maintains, and the legacy
invariant would quietly stop protecting anything while still appearing to. The
trigger keeps the shadow true, so **both** invariant sets keep meaning what they
say right up to the point of no return.

It is also what makes the stage-C rollback cheap: reverting the application is
sufficient, because the shadow column is current rather than stale.

## The guard for the point of no return

The trigger **refuses** an insert or update whose account has no active Discord
identity, because such a row could not be expressed both ways and would therefore
be unreachable after a downgrade. Break-glass accounts never receive
`character_access` (N-12), so this refuses nothing legitimate; what it refuses is
the row that would make stage D irreversible earlier than the verification period
in §6 intends.

Revision ID: 0008
Revises: 0007
Create Date: 2026-08-14
"""
from __future__ import annotations

from typing import Sequence

from alembic import op

revision: str = "0008"
down_revision: str | None = "0007"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

SHADOW_FUNCTION = """
CREATE OR REPLACE FUNCTION maintain_character_access_discord_shadow() RETURNS trigger AS $$
DECLARE
    owner_subject   BIGINT;
    grantor_subject BIGINT;
BEGIN
    SELECT e.subject::bigint INTO owner_subject
      FROM external_identities e
     WHERE e.platform_account_id = NEW.platform_account_id
       AND e.provider_key = 'discord'
       AND e.state = 'active';

    IF owner_subject IS NULL THEN
        RAISE EXCEPTION
            'character_access requires an account with an active Discord identity '
            'until stage D drops the legacy column: the row could not be expressed '
            'both ways and a downgrade could not recover it'
            USING ERRCODE = 'restrict_violation';
    END IF;

    SELECT e.subject::bigint INTO grantor_subject
      FROM external_identities e
     WHERE e.platform_account_id = NEW.granted_by_account_id
       AND e.provider_key = 'discord'
       AND e.state = 'active';

    IF grantor_subject IS NULL THEN
        RAISE EXCEPTION
            'the granting account has no active Discord identity, so the legacy '
            'grantor column cannot be kept current'
            USING ERRCODE = 'restrict_violation';
    END IF;

    NEW.discord_user_id := owner_subject;
    NEW.granted_by_discord_user_id := grantor_subject;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
"""


def upgrade() -> None:
    op.execute(SHADOW_FUNCTION)
    op.execute(
        """
        CREATE TRIGGER character_access_discord_shadow
        BEFORE INSERT OR UPDATE ON character_access
        FOR EACH ROW EXECUTE FUNCTION maintain_character_access_discord_shadow();
        """
    )


def downgrade() -> None:
    op.execute(
        "DROP TRIGGER IF EXISTS character_access_discord_shadow ON character_access;"
    )
    op.execute("DROP FUNCTION IF EXISTS maintain_character_access_discord_shadow();")
