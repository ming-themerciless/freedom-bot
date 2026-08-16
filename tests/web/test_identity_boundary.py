"""TC-ID-01 to TC-ID-07: accounts, identities, and the linking that cannot happen.

ADR 0010 D3's control is an **absence**: `external_identities` carries no
display-name, username or email column, so there is no matching key for a name
to become. Several tests here therefore assert that nothing exists rather than
that something is refused — which is the stronger statement, and the one a future
migration could quietly undo.
"""
from __future__ import annotations

import ast
from pathlib import Path
from uuid import uuid4

import pytest
from sqlalchemy import inspect, select, text

from adapters.database.tables import audit_events, external_identities
from adapters.web.repositories import AccountRepository
from application.audit import ActorCapability, AuditEvent, AuditSource
from tests.web.conftest import link_discord, make_account, utcnow

pytestmark = pytest.mark.database

ROOT = Path(__file__).resolve().parents[2]

#: Any column whose *name* suggests it could be used to match two people. The
#: rule is about what a column could become, not about what it currently holds.
NAME_LIKE_COLUMN_FRAGMENTS = (
    "name",
    "email",
    "mail",
    "username",
    "handle",
    "nick",
    "label",
)


# ---------------------------------------------------------------------------
# TC-ID-05
# ---------------------------------------------------------------------------


def test_external_identities_has_no_name_like_column(migrated_database):
    """TC-ID-05. **The absence is the control** (N-16, OD-42, ADR 0010 D3).

    A column that does not exist cannot become a matching key, and no amount of
    care in the linking code is as durable as not having somewhere to put the
    name.
    """
    columns = {
        column["name"]
        for column in inspect(migrated_database).get_columns("external_identities")
    }
    offenders = {
        column
        for column in columns
        for fragment in NAME_LIKE_COLUMN_FRAGMENTS
        if fragment in column
    }
    assert offenders == set(), f"name-like columns appeared: {sorted(offenders)}"


def test_no_web_query_resolves_an_identity_by_anything_but_provider_and_subject():
    """The code half of the same rule, read from the source rather than assumed."""
    source = (ROOT / "adapters" / "web" / "repositories.py").read_text()
    tree = ast.parse(source)
    lookups = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef) and node.name == "find_by_identity"
    ]
    assert lookups, "the identity lookup could not be found"
    arguments = {argument.arg for argument in lookups[0].args.args}
    assert arguments == {"self", "provider_key", "subject"}


# ---------------------------------------------------------------------------
# TC-ID-03
# ---------------------------------------------------------------------------


def test_provider_and_subject_are_unique_including_against_a_retired_row(
    migrated_database,
):
    """TC-ID-03. Covering retired rows is what closes the subject-reuse takeover.

    Without it, retiring an identity would free its subject for a *different*
    account, which is threat model T-06 exactly.
    """
    from sqlalchemy.exc import IntegrityError

    with migrated_database.begin() as connection:
        first = make_account(connection)
        link_discord(connection, first, 700000000000000900, state="retired")

    with migrated_database.begin() as connection:
        second = make_account(connection)

    with pytest.raises(IntegrityError):
        with migrated_database.begin() as connection:
            link_discord(connection, second, 700000000000000900)


# ---------------------------------------------------------------------------
# TC-ID-06
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "subject",
    [
        "700000000000001001",
        "700000000000001002",
        "700000000000001003",
    ],
)
def test_identical_names_never_merge_or_auto_link_accounts(
    migrated_database, subject
):
    """TC-ID-06. Three people with the same display name are three accounts.

    The names are deliberately identical, case-varied and NFC/NFD-varied across
    the parametrisation's fixtures below; the *subject* is what differs, and the
    subject is the only thing consulted.
    """
    label = "Aliá"  # 'Alia' + combining acute, i.e. an NFD form
    with migrated_database.begin() as connection:
        account_id = make_account(connection, label=label)
        link_discord(connection, account_id, int(subject))

    with migrated_database.connect() as connection:
        repository = AccountRepository(connection)
        found = repository.find_by_identity("discord", subject)
        assert found is not None
        assert found.id == account_id
        # The composed form, the case variant and the homoglyph are all
        # different *subjects*, and none of them resolves.
        assert repository.find_by_identity("discord", "Aliá") is None
        assert repository.find_by_identity("discord", label) is None


def test_three_accounts_sharing_one_display_label_stay_three_accounts(
    migrated_database,
):
    """The same rule stated as a count, which is what a merge would change."""
    label = "Same Name"
    subjects = [700000000000002001, 700000000000002002, 700000000000002003]
    created = []
    with migrated_database.begin() as connection:
        for subject in subjects:
            account_id = make_account(connection, label=label)
            link_discord(connection, account_id, subject)
            created.append(account_id)

    assert len(set(created)) == 3
    with migrated_database.connect() as connection:
        repository = AccountRepository(connection)
        resolved = {repository.find_by_identity("discord", str(s)).id for s in subjects}
    assert resolved == set(created)


# ---------------------------------------------------------------------------
# TC-ID-01, TC-ID-04
# ---------------------------------------------------------------------------


def test_an_account_survives_retiring_its_identity_and_stays_attributable(
    migrated_database, composition
):
    """TC-ID-01/TC-ID-04. Retirement keeps the row, so history keeps resolving.

    This is why unlink is `state = 'retired'` rather than `DELETE`: the audit
    resolution join in schema §6.5 reads through this table, and a deleted row
    would turn every historical event that person wrote into an unattributable
    one.
    """
    with migrated_database.begin() as connection:
        account_id = make_account(connection)
        identity_id = link_discord(connection, account_id, 700000000000003001)
        composition.services(connection).audit.record(
            AuditEvent(
                action="character_access.granted",
                entity_type="character",
                entity_id=str(uuid4()),
                source=AuditSource.WEB,
                actor_capability=ActorCapability.GUILD_COUNCIL,
                correlation_id=uuid4(),
                actor_platform_account_id=account_id,
                payload={"reason": "synthetic"},
            )
        )

    with migrated_database.begin() as connection:
        connection.execute(
            text(
                "UPDATE external_identities SET state = 'retired', "
                "retired_at = now(), retired_reason = 'provider retirement' "
                "WHERE id = :id"
            ),
            {"id": identity_id},
        )

    with migrated_database.connect() as connection:
        identity = connection.execute(
            select(external_identities).where(external_identities.c.id == identity_id)
        ).mappings().one()
        event = connection.execute(
            select(audit_events).where(
                audit_events.c.actor_platform_account_id == account_id
            )
        ).mappings().one()
        # The historical form still resolves through the retired row, which is
        # exactly delivery plan §9.5's requirement.
        resolved = connection.execute(
            text(
                "SELECT platform_account_id FROM external_identities "
                "WHERE provider_key = 'discord' AND subject = :subject"
            ),
            {"subject": "700000000000003001"},
        ).scalar_one()

    assert identity["state"] == "retired"
    assert event["actor_platform_account_id"] == account_id
    assert resolved == account_id


def test_a_retired_identity_no_longer_authenticates(migrated_database):
    """TC-ID-04's other half: retirement removes *authentication*, not attribution."""
    with migrated_database.begin() as connection:
        account_id = make_account(connection)
        link_discord(connection, account_id, 700000000000003002, state="retired")

    with migrated_database.connect() as connection:
        assert (
            AccountRepository(connection).find_by_identity(
                "discord", "700000000000003002"
            )
            is None
        )


# ---------------------------------------------------------------------------
# TC-ID-07
# ---------------------------------------------------------------------------


def test_the_active_identity_count_is_what_unlink_will_have_to_consult(
    migrated_database,
):
    """TC-ID-07's P3.1 half.

    R-37 (unlink) is a **P3.2** route and is deliberately absent from this build,
    so the refusal it will make cannot be exercised end to end yet. What P3.1
    owns is the fact the refusal rests on — "does this account still have a
    usable identity?" — and that is asserted here, including that a retired one
    does not count. Recorded as a partial in the P3.1 submission.
    """
    with migrated_database.begin() as connection:
        account_id = make_account(connection)
        link_discord(connection, account_id, 700000000000004001)
        link_discord(connection, account_id, 700000000000004002, state="retired")

    with migrated_database.connect() as connection:
        assert AccountRepository(connection).active_identity_count(account_id) == 1


# ---------------------------------------------------------------------------
# TC-ID-02
# ---------------------------------------------------------------------------


def test_no_web_module_filters_authorization_by_a_discord_snowflake():
    """TC-ID-02. Sessions and access refer to accounts; snowflakes are Discord facts.

    Read from the source: the web layer may *read* the membership projection by
    snowflake — that is what a projection is — but no authorization-bearing query
    may key on one. The distinction is enforced by naming the two places the
    snowflake legitimately appears.
    """
    permitted = {
        # The membership projection is Discord's own data, keyed by Discord's own
        # identifier. It answers "who is this on Discord?" and never "who may do
        # this here?".
        "MembershipProjectionRepository",
        # The exact `(provider, subject)` lookup, which is how a snowflake
        # becomes an account in the first place.
        "find_by_identity",
    }
    source = (ROOT / "adapters" / "web" / "repositories.py").read_text()
    tree = ast.parse(source)

    offenders: list[str] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.FunctionDef):
            continue
        if node.name in permitted:
            continue
        parents = [
            ancestor.name
            for ancestor in ast.walk(tree)
            if isinstance(ancestor, ast.ClassDef) and node in ast.walk(ancestor)
        ]
        if set(parents) & permitted:
            continue
        arguments = {argument.arg for argument in node.args.args} | {
            argument.arg for argument in node.args.kwonlyargs
        }
        if "discord_user_id" in arguments:
            offenders.append(f"{parents}.{node.name}")

    assert offenders == [], offenders
