"""Seeding helpers for the P3.2 suites: callers, characters, links and proposals.

One place where "a caller in state `M`" becomes rows, because every P3.2 suite
needs the same eight caller states and building them per module would be eight
chances to build one slightly wrong — a `C` that is accidentally also an
administrator would make a Council test pass for the wrong reason.

The states are route contract §3.1's, and `caller()` below is the only thing that
constructs them:

| Code | What it is here |
|---|---|
| `U` | No cookie at all |
| `N` | A live session whose guild membership row is `active = false` |
| `M` | Member, no mapped role |
| `C` | Member holding the role mapped to `guild_council` |
| `A` | Member holding the role mapped to `platform_administrator` |
| `CA` | Both roles |
| `BG` | A `webauthn` session — break-glass, and never a Discord role |
| `AC` | A **`discord_oauth`** session holding a role whose administrator mapping has `provenance = 'emergency_continuity'` |

`AC` is the one that has to be built rather than described. It is an ordinary
login: `auth_method` is `discord_oauth`, the membership projection is real, and
the only thing making it continuity-scoped is that every mapping conferring
`platform_administrator` on it was created under an emergency scope. That is
exactly the state schema §8.1's guard exists for, and a test double would prove
nothing about it.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4

from sqlalchemy import insert, text, update

from adapters.database.tables import (
    character_access,
    characters,
    discord_guild_memberships,
    external_actor_mappings,
    sheet_row_mappings,
)
from application.audit import ActorCapability
from application.web.capabilities import (
    AdministratorScope,
    AuthMethod,
    WebAuthorizationContext,
)
from tests.web.conftest import (
    add_mapping,
    link_discord,
    make_account,
    seed_membership,
    seed_oauth_transaction,
)
from tests.web_fixtures import BOOTSTRAP_ADMIN_ROLE_ID, COUNCIL_ROLE_ID, TEST_GUILD_ID

#: Synthetic, and outside the range Discord has issued. No real player, guild or
#: credential appears anywhere in this suite (delivery plan §10).
MEMBER_SUBJECT = 700000000000001001
COUNCIL_SUBJECT = 700000000000001002
ADMIN_SUBJECT = 700000000000001003
COUNCIL_ADMIN_SUBJECT = 700000000000001004
NON_MEMBER_SUBJECT = 700000000000001005
CONTINUITY_SUBJECT = 700000000000001006
OTHER_MEMBER_SUBJECT = 700000000000001007

#: A role nobody maps by default, used to make an `AC` caller: the emergency
#: mapping is attached to it so an ordinary login through it resolves to
#: administrator authority with `emergency_continuity` provenance.
CONTINUITY_ROLE_ID = 900000000000000009


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Caller:
    """One seeded caller: its account, its subject, and its session cookie."""

    __slots__ = ("state", "account_id", "subject", "cookie", "session_id")

    def __init__(self, *, state, account_id, subject, cookie, session_id) -> None:
        self.state = state
        self.account_id = account_id
        self.subject = subject
        self.cookie = cookie
        self.session_id = session_id

    def cookies(self, settings) -> dict[str, str]:
        if self.cookie is None:
            return {}
        return {settings.session.cookie_name: self.cookie}


def bootstrap_council_mapping(connection, *, created_by: UUID) -> UUID:
    """Map the Council role to `guild_council`, as an administrator would.

    Written directly rather than through R-33 because the tests that *use*
    Council are not the tests that prove how a mapping is made. The ones that
    prove it — TC-CAP and TC-BG-05 — go through the route.
    """
    return add_mapping(
        connection,
        role_id=COUNCIL_ROLE_ID,
        capability=ActorCapability.GUILD_COUNCIL.value,
        created_by=created_by,
    )


def seed_callers(engine, settings, *, states=None):
    """Build every requested caller state and return them by code.

    One transaction, so a suite's fixture cannot leave half a matrix behind.
    """
    from adapters.web.composition import WebComposition  # noqa: F401 - typing only

    wanted = set(states or ("U", "N", "M", "C", "A", "CA", "BG", "AC"))
    callers: dict[str, Caller] = {}
    with engine.begin() as connection:
        seeder_account = make_account(connection, label="seeder")
        link_discord(connection, seeder_account, 700000000000000999)
        bootstrap_council_mapping(connection, created_by=seeder_account)
        # The emergency-provenance administrator mapping that makes `AC`
        # continuity-scoped. Created under `emergency_continuity`, exactly as a
        # break-glass session's R-33 would have created it.
        add_mapping(
            connection,
            role_id=CONTINUITY_ROLE_ID,
            capability=ActorCapability.PLATFORM_ADMINISTRATOR.value,
            created_by=seeder_account,
            scope="emergency_continuity",
            auth_method="webauthn",
        )

    plan = {
        "N": (NON_MEMBER_SUBJECT, frozenset(), AuthMethod.DISCORD_OAUTH),
        "M": (MEMBER_SUBJECT, frozenset(), AuthMethod.DISCORD_OAUTH),
        "C": (COUNCIL_SUBJECT, frozenset({COUNCIL_ROLE_ID}), AuthMethod.DISCORD_OAUTH),
        "A": (
            ADMIN_SUBJECT,
            frozenset({BOOTSTRAP_ADMIN_ROLE_ID}),
            AuthMethod.DISCORD_OAUTH,
        ),
        "CA": (
            COUNCIL_ADMIN_SUBJECT,
            frozenset({COUNCIL_ROLE_ID, BOOTSTRAP_ADMIN_ROLE_ID}),
            AuthMethod.DISCORD_OAUTH,
        ),
        "BG": (None, frozenset(), AuthMethod.WEBAUTHN),
        "AC": (
            CONTINUITY_SUBJECT,
            frozenset({CONTINUITY_ROLE_ID}),
            AuthMethod.DISCORD_OAUTH,
        ),
    }

    if "U" in wanted:
        callers["U"] = Caller(
            state="U", account_id=None, subject=None, cookie=None, session_id=None
        )

    for state in sorted(wanted - {"U"}):
        subject, roles, method = plan[state]
        callers[state] = _build(engine, settings, state, subject, roles, method)
    return callers


def _build(engine, settings, state, subject, roles, method) -> Caller:
    from adapters.web.composition import WebComposition  # noqa: F401

    with engine.begin() as connection:
        account_id = make_account(
            connection,
            protected=(state == "BG"),
            label=f"caller-{state}",
        )
        transaction_id = None
        if subject is not None:
            link_discord(connection, account_id, subject)
            seed_membership(connection, discord_user_id=subject, role_ids=roles)
            if state == "N":
                # Membership revoked *during* an existing session. Login itself
                # never produces this state (route contract §4.1), so it is
                # produced the way production produces it: the session exists,
                # and the projection then says the person is no longer a member.
                connection.execute(
                    update(discord_guild_memberships)
                    .where(
                        discord_guild_memberships.c.discord_user_id == subject,
                        discord_guild_memberships.c.guild_id == TEST_GUILD_ID,
                    )
                    .values(active=False)
                )
        if method is AuthMethod.DISCORD_OAUTH:
            # OD-44: every `discord_oauth` session names the transaction it is
            # the durable product of, and the check constraint refuses one that
            # does not.
            transaction_id = seed_oauth_transaction(connection)

    from adapters.web.repositories import SessionRepository
    from application.web.sessions import SessionService

    with engine.begin() as connection:
        repository = SessionRepository(connection, settings=settings.session)
        from adapters.web.repositories import TokenGrantRepository, WebAuditRepository

        service = SessionService(
            sessions=repository,
            token_grants=TokenGrantRepository(connection),
            audit=WebAuditRepository(connection),
        )
        context = WebAuthorizationContext(
            account_id=account_id,
            auth_method=method,
            capabilities=frozenset({ActorCapability.GUILD_MEMBER}),
            administrator_scope=AdministratorScope.FULL,
            membership=None,
        )
        issued = service.begin(
            context=context,
            now=utcnow(),
            correlation_id=uuid4(),
            oauth_transaction_id=transaction_id,
        )
    return Caller(
        state=state,
        account_id=account_id,
        subject=None if subject is None else str(subject),
        cookie=issued.token,
        session_id=issued.session_id,
    )


# ---------------------------------------------------------------------------
# Characters, links and snapshots
# ---------------------------------------------------------------------------


def make_character(connection, *, display_name: str, level: int | None = 3) -> UUID:
    character_id = uuid4()
    connection.execute(
        insert(characters).values(
            id=character_id,
            display_name=display_name,
            long_name=f"{display_name} of the Free Blades",
            level=level,
            active=True,
            version=0,
        )
    )
    return character_id


def grant_link(
    connection,
    *,
    character_id: UUID,
    account_id: UUID,
    granted_by: UUID,
    access_kind: str = "owner",
    default_character: bool = False,
    reason: str = "seeded for a test",
) -> UUID:
    """Insert an active link directly.

    The legacy Discord columns are left to migration 0008's shadow trigger, which
    also refuses an account with no active Discord identity — so a caller seeded
    without one cannot be given a link here either, which is the guard doing its
    job rather than a limitation of this helper.
    """
    access_id = uuid4()
    connection.execute(
        insert(character_access).values(
            id=access_id,
            character_id=character_id,
            platform_account_id=account_id,
            access_kind=access_kind,
            active=True,
            default_character=default_character,
            granted_by_account_id=granted_by,
            reason=reason,
            audit_correlation_id=uuid4(),
        )
    )
    return access_id


def map_sheet_row(connection, *, character_id: UUID, row_index: int, sheet_tab: str = "Characters") -> UUID:
    """The Phase 2 importer's Sheet-row → character-id mapping, seeded directly.

    This is the *stable* key M-2 resolves a `Characters` row through, and the
    reason the resolver never has to compare a character name to anything: the
    row's position is the identity, and `sheet_row_mappings` is where the Phase 2
    import recorded it.
    """
    mapping_id = uuid4()
    connection.execute(
        insert(sheet_row_mappings).values(
            id=mapping_id,
            character_id=character_id,
            sheet_tab=sheet_tab,
            row_index=row_index,
        )
    )
    return mapping_id


def seed_discord_member(connection, *, subject: int, username: str) -> None:
    """One active guild member in the projection, with a chosen username.

    `seed_membership` names members `member-<snowflake>`, which is right for the
    caller states and useless for M-2: the whole resolver is a comparison against
    the *username*, so a case needs to choose it.
    """
    connection.execute(
        text(
            "INSERT INTO discord_users (id, username) VALUES (:id, :name) "
            "ON CONFLICT (id) DO UPDATE SET username = :name"
        ),
        {"id": subject, "name": username},
    )
    connection.execute(
        text(
            "INSERT INTO discord_guild_memberships (discord_user_id, guild_id, active) "
            "VALUES (:user, :guild, true) "
            "ON CONFLICT (discord_user_id, guild_id) DO UPDATE SET active = true"
        ),
        {"user": subject, "guild": TEST_GUILD_ID},
    )


def stale_membership(connection, *, subject: int, minutes: int = 60) -> None:
    """Backdate a member's projection so the next request must ask the provider.

    N-09 gives a projection five minutes; past that, `open_request()` plans a
    refresh. A case about *"what happens before the provider is asked"* has to be
    able to produce a request that would otherwise ask, or it proves nothing.
    """
    connection.execute(
        text(
            "UPDATE discord_guild_memberships SET observed_at = :at "
            "WHERE discord_user_id = :user AND guild_id = :guild"
        ),
        {
            "at": utcnow() - timedelta(minutes=minutes),
            "user": subject,
            "guild": TEST_GUILD_ID,
        },
    )


def seed_token_grant(composition, connection, *, identity_id: UUID) -> UUID:
    """A live, correctly bound token grant, so a refresh plan can be formed.

    `_refresh_plan` returns `None` when there is no stored grant — there is then no
    way to ask the provider anything — so a case that wants to prove *"the
    provider was not called"* must first arrange a request for which calling it was
    possible. The ciphertext is sealed with the composition's own envelope under
    the real AAD, because a grant the platform cannot open produces `None` from
    `_observe_membership` and would again mean "no call" for the wrong reason.
    """
    from adapters.web.repositories import TokenGrantRepository
    from application.web.crypto import token_grant_aad

    grant_id = uuid4()
    key_version = composition.envelope.seal(b"probe", aad=b"probe").key_version
    sealed = composition.envelope.seal(
        b"synthetic-access-token",
        aad=token_grant_aad(grant_id, identity_id, key_version),
    )
    TokenGrantRepository(connection).replace(
        external_identity_id=identity_id,
        access=sealed,
        refresh=None,
        scopes="identify guilds.members.read",
        access_expires_at=utcnow() + timedelta(hours=1),
        grant_id=grant_id,
    )
    return grant_id


def csrf_token_for(settings, caller: "Caller") -> str:
    """The synchronizer token this caller's session would be issued (N-17).

    Derived, never rendered: `csrf.issue` is what `open_request()` calls, so a
    matrix case can hold a **valid** token without fetching the page that carries
    one. That is the difference between a matrix cell that measures authorization
    and one that measures whether a form was rendered first — the reason the
    authenticated mutation cells supply this instead of omitting the field.
    """
    from application.web import csrf

    return csrf.issue(settings.csrf_key, caller.session_id)


def map_external_actor(connection, *, character_id: UUID, world_id: str = "the-guild") -> UUID:
    mapping_id = uuid4()
    connection.execute(
        insert(external_actor_mappings).values(
            id=mapping_id,
            character_id=character_id,
            world_id=world_id,
            external_actor_id="A" * 16,
            relink_fingerprint="synthetic-fingerprint",
        )
    )
    return mapping_id


def character_version(connection, character_id: UUID) -> int:
    return connection.execute(
        text("SELECT version FROM characters WHERE id = :id"), {"id": character_id}
    ).scalar_one()


def clean_p3_2_tables(connection) -> None:
    """Children first; `character_access` before `characters`.

    `identity_migration_runs` cascades to proposals and candidates, and
    `identity_link_proposals.granted_access_id` is `RESTRICT`, so the proposals
    have to go before the access rows they name.
    """
    connection.execute(text("DELETE FROM identity_migration_runs"))
    connection.execute(text("DELETE FROM character_access"))
    connection.execute(text("DELETE FROM external_actor_mappings"))
    connection.execute(text("DELETE FROM sheet_row_mappings"))
    connection.execute(text("DELETE FROM characters"))


__all__ = [
    "ADMIN_SUBJECT",
    "CONTINUITY_ROLE_ID",
    "CONTINUITY_SUBJECT",
    "COUNCIL_ADMIN_SUBJECT",
    "COUNCIL_SUBJECT",
    "Caller",
    "MEMBER_SUBJECT",
    "NON_MEMBER_SUBJECT",
    "OTHER_MEMBER_SUBJECT",
    "bootstrap_council_mapping",
    "character_version",
    "clean_p3_2_tables",
    "csrf_token_for",
    "grant_link",
    "make_character",
    "map_external_actor",
    "map_sheet_row",
    "seed_callers",
    "seed_discord_member",
    "seed_token_grant",
    "stale_membership",
    "utcnow",
]
