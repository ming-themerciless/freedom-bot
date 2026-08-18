"""TC-ID-01…08: accounts, external identities, and the rule that a name links nothing.

The whole of ADR 0010's D1 is that authorization is keyed by **account**, and the
whole of OD-42/N-16 is that no name-like value ever establishes that two identities
are one person. Both are absences, and an absence needs a test that would fail if the
absence stopped holding — so several cases here are structural sweeps over the schema
and over the web module's own source, not behavioural cases at all.

`external_identities` covers **retired** rows in its uniqueness (delivery plan §9.2),
which is not an implementation detail: it prevents a retired subject being re-linked
to a *different* account, which is the subject-reuse takeover of threat model T-06.
TC-ID-03 is where that is asserted against the database rather than read in a
docstring.
"""
from __future__ import annotations

import ast
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import Barrier, BrokenBarrierError
from uuid import UUID, uuid4

import pytest
from sqlalchemy import text

from adapters.web.repositories import (
    AccountRepository,
    CharacterAccessRepository,
    WebAuditRepository,
    WebAuthnRepository,
)
from application.web.account_identities import AccountIdentityService, UnlinkRefused
from application.web.capabilities import (
    AdministratorScope,
    AuthMethod,
    WebAuthorizationContext,
)
from application.audit import ActorCapability
from tests.web.conftest import link_discord, make_account, utcnow
from tests.web.portal_fixtures import (
    clean_p3_2_tables,
    grant_link,
    make_character,
    seed_callers,
    seed_discord_member,
)

pytestmark = pytest.mark.database

ROOT = Path(__file__).resolve().parents[2]

#: Synthetic. The names below are chosen to collide in every way a name can.
BASE = 700000000000012000


@pytest.fixture(autouse=True)
def clean_between_cases(request):
    yield
    if "migrated_database" not in request.fixturenames:
        return
    engine = request.getfixturevalue("migrated_database")
    with engine.begin() as connection:
        clean_p3_2_tables(connection)


def member_context(account_id: UUID) -> WebAuthorizationContext:
    return WebAuthorizationContext(
        account_id=account_id,
        auth_method=AuthMethod.DISCORD_OAUTH,
        capabilities=frozenset({ActorCapability.GUILD_MEMBER}),
        administrator_scope=AdministratorScope.FULL,
        membership=None,
    )


def count(engine, statement, **parameters):
    with engine.begin() as connection:
        return connection.execute(text(statement), parameters).scalar()


def rows(engine, statement, **parameters):
    with engine.begin() as connection:
        return connection.execute(text(statement), parameters).mappings().all()


# ---------------------------------------------------------------------------
# TC-ID-01 — an account survives unlinking a provider
# ---------------------------------------------------------------------------


def test_an_account_survives_retiring_its_provider_identity(
    migrated_database, settings
):
    """TC-ID-01. Sessions, `character_access` and audit attribution all still resolve.

    Retirement keeps the row (`state = 'retired'`, `retired_at` set), and every
    foreign key into it is `RESTRICT`, so the identity cannot be removed out from
    under the history that names it. That is what makes the account — not the Discord
    snowflake — the durable identity ADR 0010 D1 requires.
    """
    callers = seed_callers(migrated_database, settings, states=("C",))
    with migrated_database.begin() as connection:
        character_id = make_character(connection, display_name="Alia Storm")
        account_id = make_account(connection, label="retiring")
        seed_discord_member(connection, subject=BASE + 1, username="retiring.one")
        identity_id = link_discord(connection, account_id, BASE + 1)
        access_id = grant_link(
            connection,
            character_id=character_id,
            account_id=account_id,
            granted_by=callers["C"].account_id,
            access_kind="co_owner",
        )

    with migrated_database.begin() as connection:
        assert AccountRepository(connection).retire_identity(
            identity_id, reason="the person changed Discord accounts", at=utcnow()
        )

    identity = rows(
        migrated_database,
        "SELECT state, retired_at, platform_account_id FROM external_identities "
        "WHERE id = :id",
        id=identity_id,
    )
    assert len(identity) == 1, "retirement must keep the row"
    assert identity[0]["state"] == "retired"
    assert identity[0]["retired_at"] is not None
    assert identity[0]["platform_account_id"] == account_id

    # The account is untouched and its link still resolves by account key.
    assert (
        count(
            migrated_database,
            "SELECT status FROM platform_accounts WHERE id = :id",
            id=account_id,
        )
        == "active"
    )
    with migrated_database.begin() as connection:
        access = CharacterAccessRepository(connection).access_for(
            character_id=character_id, account_id=account_id
        )
    assert access is not None
    assert access["id"] == access_id


def test_concurrent_unlinks_cannot_retire_an_accounts_last_two_identities(
    migrated_database,
):
    """TC-ID-07. The last-identity decision is atomic across different rows.

    A conditional update on one identity only serializes two requests aimed at
    that same row. Two requests aimed at the account's two different active
    identities must also serialize the count-and-retire decision, or each can
    observe two identities and retire one, leaving the account with no way back
    in. The barrier forces that vulnerable interleaving when no account lock is
    held; after the lock is present, the first waiter times out and completes,
    then the second observes the remaining identity and refuses it.
    """

    with migrated_database.begin() as connection:
        account_id = make_account(connection, label="concurrent-unlink")
        first_id = link_discord(connection, account_id, BASE + 90)
        second_id = link_discord(connection, account_id, BASE + 91)

    rendezvous = Barrier(2)

    class CoordinatedAccounts(AccountRepository):
        def active_identity_count(self, candidate: UUID) -> int:
            count = super().active_identity_count(candidate)
            try:
                rendezvous.wait(timeout=0.5)
            except BrokenBarrierError:
                pass
            return count

    def unlink(identity_id: UUID):
        try:
            with migrated_database.begin() as connection:
                service = AccountIdentityService(
                    accounts=CoordinatedAccounts(connection),
                    credentials=WebAuthnRepository(connection),
                    audit=WebAuditRepository(connection),
                )
                service.unlink(
                    context=member_context(account_id),
                    identity_id=identity_id,
                    correlation_id=uuid4(),
                    now=utcnow(),
                )
            return "unlinked"
        except UnlinkRefused:
            return "refused"

    with ThreadPoolExecutor(max_workers=2) as executor:
        outcomes = sorted(executor.map(unlink, (first_id, second_id)))

    assert outcomes == ["refused", "unlinked"]
    assert count(
        migrated_database,
        "SELECT count(*) FROM external_identities "
        "WHERE platform_account_id = :account AND state = 'active'",
        account=account_id,
    ) == 1


def test_a_retired_identity_cannot_be_deleted_out_from_under_history(
    migrated_database, settings
):
    """The `RESTRICT` half of TC-ID-04, asserted by attempting the deletion.

    Deleting the row is what would break historical audit attribution (§8 property
    1), and it is refused by the foreign key rather than by a convention nobody
    enforces.
    """
    with migrated_database.begin() as connection:
        account_id = make_account(connection, label="restricted")
        seed_discord_member(connection, subject=BASE + 2, username="restricted.one")
        link_discord(connection, account_id, BASE + 2)
    with pytest.raises(Exception) as refusal:
        with migrated_database.begin() as connection:
            connection.execute(
                text("DELETE FROM platform_accounts WHERE id = :id"), {"id": account_id}
            )
    assert "external_identities" in str(refusal.value)


# ---------------------------------------------------------------------------
# TC-ID-03 — uniqueness covers retired rows
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("state", ["active", "retired"])
def test_provider_subject_uniqueness_holds_including_against_a_retired_row(
    migrated_database, state
):
    """TC-ID-03, and threat model T-06 with it.

    A subject that has been retired must not become linkable to a **different**
    account: the person who held that snowflake would then be impersonable by whoever
    acquired it next. The unique constraint deliberately covers retired rows, which is
    exactly the case a `WHERE state = 'active'` index would have missed.
    """
    with migrated_database.begin() as connection:
        first = make_account(connection, label="first")
        second = make_account(connection, label="second")
        seed_discord_member(connection, subject=BASE + 3, username="reused.one")
        link_discord(connection, first, BASE + 3, state=state)

    with pytest.raises(Exception) as refusal:
        with migrated_database.begin() as connection:
            link_discord(connection, second, BASE + 3)
    assert "provider_key_subject" in str(refusal.value)


# ---------------------------------------------------------------------------
# TC-ID-06 — no name-like value ever merges or auto-links accounts
# ---------------------------------------------------------------------------


#: Every way two people's names can collide. Each pair is (username A, username B),
#: chosen so that a name-based linker would treat them as one person.
COLLIDING_NAMES = [
    ("identical.name", "identical.name"),
    ("CaseVariant", "casevariant"),
    # NFC vs NFD: the same grapheme, two byte sequences.
    ("Renée", "Renée"),
    # Homoglyphs: Latin 'a' against Cyrillic 'а'.
    ("marka", "markа"),
    ("trailing.space ", "trailing.space"),
]


@pytest.mark.parametrize(("first_name", "second_name"), COLLIDING_NAMES)
def test_colliding_names_never_merge_or_auto_link_accounts(
    migrated_database, first_name, second_name
):
    """TC-ID-06. Two accounts, two subjects, two names that collide. Still two accounts.

    The reason this holds is not that a linker is careful: it is that
    `external_identities` has **no name column at all** and every resolution is by
    `(provider_key, subject)`. So the parametrization above cannot influence anything,
    and this case is the demonstration of that rather than a check on a heuristic.
    """
    first_subject, second_subject = BASE + 10, BASE + 11
    with migrated_database.begin() as connection:
        first_account = make_account(connection, label="collision-first")
        second_account = make_account(connection, label="collision-second")
        seed_discord_member(connection, subject=first_subject, username=first_name)
        seed_discord_member(connection, subject=second_subject, username=second_name)
        link_discord(connection, first_account, first_subject)
        link_discord(connection, second_account, second_subject)

    assert first_account != second_account
    with migrated_database.begin() as connection:
        accounts = AccountRepository(connection)
        assert accounts.account_for_active_identity("discord", str(first_subject)) == (
            first_account
        )
        assert accounts.account_for_active_identity("discord", str(second_subject)) == (
            second_account
        )
        # Each account holds exactly one identity: nothing merged them.
        assert accounts.active_identity_count(first_account) == 1
        assert accounts.active_identity_count(second_account) == 1


def test_a_colliding_name_is_still_shown_as_two_candidates_never_resolved_to_one(
    migrated_database, settings
):
    """R-24's search returns candidates; it never answers "this name is that person".

    Two members whose usernames are identical are two rows in the result, each with
    its own snowflake. A search that collapsed them would be a name deciding an
    identity at the moment a Council member is choosing whom to authorize — the worst
    available place for it.
    """
    from adapters.web.repositories import IdentityCandidateRepository

    with migrated_database.begin() as connection:
        for offset in range(2):
            seed_discord_member(
                connection, subject=BASE + 20 + offset, username="the.same.name"
            )
    with migrated_database.begin() as connection:
        found = IdentityCandidateRepository(connection).search(
            guild_id=settings.discord.guild_id, query="the.same.name", limit=25
        )
    assert len({row["id"] for row in found}) == 2


# ---------------------------------------------------------------------------
# TC-ID-02 / TC-ID-05 — structural absences
# ---------------------------------------------------------------------------


def test_external_identities_carries_no_name_like_column(migrated_database):
    """TC-ID-05, first half: read from `information_schema`, not from the model.

    The absence of a display-name, username or email column is *why* no code path can
    link by one. Asserted against the live database so a migration that added one
    fails here rather than being noticed later by a reviewer.
    """
    columns = {
        row["column_name"]
        for row in rows(
            migrated_database,
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_schema = 'public' AND table_name = 'external_identities'",
        )
    }
    forbidden = {
        name
        for name in columns
        if any(
            token in name
            for token in ("name", "email", "mail", "nick", "handle", "label", "display")
        )
    }
    assert forbidden == set(), sorted(forbidden)
    # And the identity **is** the pair, so both halves are present.
    assert {"provider_key", "subject"} <= columns


def test_no_web_module_resolves_an_account_from_a_name_like_value():
    """TC-ID-05, second half: an AST sweep over the web application layer.

    The rule is that the *only* lookup that answers "which account is this?" is one
    keyed on a provider subject. This walks every call in `application/web/` and
    `adapters/web/` and asserts that no `account_for_*` or `find_by_*` helper takes a
    keyword that names a name-like value. It is crude, and crude is the right shape
    for a rule about what must never appear.
    """
    suspect_keywords = {"username", "display_name", "email", "global_name", "nickname"}
    offences: list[str] = []
    for module in sorted(
        list((ROOT / "application" / "web").glob("*.py"))
        + list((ROOT / "adapters" / "web").glob("*.py"))
    ):
        tree = ast.parse(module.read_text())
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Attribute):
                continue
            name = node.func.attr
            if not (name.startswith("account_for") or name.startswith("find_by")):
                continue
            supplied = {keyword.arg for keyword in node.keywords if keyword.arg}
            if supplied & suspect_keywords:
                offences.append(f"{module.name}:{node.lineno} {name}({sorted(supplied)})")
    assert offences == [], offences


def test_no_web_query_filters_character_access_or_sessions_by_a_discord_snowflake():
    """TC-ID-02. Authorization-bearing reads are keyed by account, not by snowflake.

    The Discord columns still exist as a trigger-maintained shadow until stage D, so
    the guard cannot be "the column is gone". It is "no web query mentions it": an
    AST sweep for `discord_user_id` used as a column reference on `character_access`
    or `sessions` inside `adapters/web/repositories.py`.
    """
    source = (ROOT / "adapters" / "web" / "repositories.py").read_text()
    tree = ast.parse(source)
    offences: list[str] = []
    for node in ast.walk(tree):
        # `character_access.c.discord_user_id` and `sessions.c.discord_user_id`.
        if (
            isinstance(node, ast.Attribute)
            and node.attr in {"discord_user_id", "granted_by_discord_user_id"}
            and isinstance(node.value, ast.Attribute)
            and node.value.attr == "c"
            and isinstance(node.value.value, ast.Name)
            and node.value.value.id in {"character_access", "sessions"}
        ):
            offences.append(f"line {node.lineno}: {node.value.value.id}.c.{node.attr}")
    assert offences == [], offences


def test_the_grant_path_takes_a_subject_and_resolves_the_account_itself():
    """TC-ID-08, from the signature. There is nowhere to put a forged account id.

    The strongest statement of "a forged `platform_account_id` is ignored" is that the
    parameter does not exist. Asserted over the signature rather than by submitting one
    and observing that nothing happened, because the second reads as a coincidence.
    """
    import inspect

    from application.web.character_access import CharacterAccessService

    parameters = set(inspect.signature(CharacterAccessService.grant).parameters)
    assert "subject" in parameters
    assert not parameters & {
        "platform_account_id",
        "account_id",
        "target_account_id",
        "username",
        "display_name",
        "email",
    }


def test_the_identity_overview_takes_no_account_argument():
    """R-35's scope is `context.account_id`, so there is no id to substitute."""
    import inspect

    from application.web.account_identities import AccountIdentityService

    parameters = set(inspect.signature(AccountIdentityService.overview).parameters)
    assert "account_id" not in parameters
    assert "context" in parameters
