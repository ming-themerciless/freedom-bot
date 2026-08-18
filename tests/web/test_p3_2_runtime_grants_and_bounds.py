"""P3.2's runtime grants under the real restricted role, and the request bounds.

Two unrelated halves, kept together because both are the kind of evidence that is
usually *reviewed* rather than run.

## The runtime role

`infra/postgresql/runtime-grants.sql.tmpl` gained three tables. A template that is
read rather than applied proves nothing, so this file renders the real template for
`freedom_runtime_test` — `NOLOGIN`, non-superuser, and a role the owning login is a
member of — applies it, and then does the work with `SET ROLE`. That exercises the
*privileges* without needing a second connection identity, which is the method
`tests/test_runtime_grants_live.py` established for Phase 2 and which is reused here
rather than re-derived.

What the band has to be, and why: `identity_link_proposals` is **evidence** with a
90-day retention (schema §11), so the runtime role may delete it — and the
authorization a confirmation creates is a `character_access` row plus an audit event,
both outside this band, neither deletable. A purge that has run its course therefore
removes the working papers and leaves the decision. `TRUNCATE` is revoked: a
retention sweep deletes a run and cascades, and a role that could empty the table
outright could erase evidence of a decision nobody had reviewed yet.

## The request bounds

A signed cursor (N-64) that is refused rather than reset, a page size that is clamped
rather than trusted, and a body bound that is refused before the body is read. Each is
a place where a caller supplies a number or a token and the server has to decline to
be helpful about it: a reset cursor hides tampering behind a page that looks like it
worked.
"""
from __future__ import annotations

import base64
from uuid import uuid4

import pytest
from sqlalchemy import text
from sqlalchemy.exc import ProgrammingError

from tests.test_runtime_grants_live import (
    INSUFFICIENT_PRIVILEGE,
    RUNTIME_ROLE,
    grant_statements,
    sqlstate,
)
from tests.web.conftest import link_discord, make_account
from tests.web.portal_fixtures import (
    clean_p3_2_tables,
    csrf_token_for,
    grant_link,
    make_character,
    seed_callers,
    seed_discord_member,
)
from tests.web_fixtures import PUBLIC_ORIGIN

pytestmark = pytest.mark.database

FORM = "application/x-www-form-urlencoded"

#: The three tables migration 0010 adds, children last so an insert order exists.
NEW_TABLES = (
    "identity_migration_runs",
    "identity_link_proposals",
    "identity_link_proposal_candidates",
)

SUBJECT = 700000000000014001
#: A second synthetic member, for the decision-constraint cases below.
SECOND_SUBJECT = 700000000000014002


@pytest.fixture(autouse=True)
def clean_between_cases(request):
    yield
    if "migrated_database" not in request.fixturenames:
        return
    engine = request.getfixturevalue("migrated_database")
    with engine.begin() as connection:
        clean_p3_2_tables(connection)


@pytest.fixture()
def restricted(migrated_database):
    """A connection with the runtime role assumed, and the real template applied.

    The template is applied by the fixture rather than by hand, for the reason the
    Phase 2 file gives: the schema fixture migrates from empty on every run, which
    drops each table and its ACL with it, so grants applied beforehand would not
    survive to be tested — and applying the deployed artifact makes this evidence
    about that artifact.

    Teardown rolls back *before* resetting the role: a denied statement aborts its
    transaction and `RESET ROLE` would fail inside an aborted one, leaving the role
    assumed for whatever ran next.
    """
    with migrated_database.begin() as owner:
        if not owner.execute(
            text("SELECT 1 FROM pg_roles WHERE rolname = :role"), {"role": RUNTIME_ROLE}
        ).scalar():
            pytest.skip(f"{RUNTIME_ROLE} does not exist on this cluster")
        for statement in grant_statements():
            owner.execute(text(statement))

    connection = migrated_database.connect()
    connection.execute(text(f"SET ROLE {RUNTIME_ROLE}"))
    try:
        yield connection
    finally:
        connection.rollback()
        connection.execute(text("RESET ROLE"))
        connection.close()


@pytest.fixture()
def seeded_run(migrated_database, settings):
    """A published run with one confirmed proposal and the link it created.

    Written as the owner, so the restricted-role cases below are about what that role
    may do to rows that already exist rather than about whether it can create them.
    """
    callers = seed_callers(migrated_database, settings, states=("C",))
    with migrated_database.begin() as connection:
        character_id = make_character(connection, display_name="Alia Storm")
        account_id = make_account(connection, label="linked")
        seed_discord_member(connection, subject=SUBJECT, username="linked.one")
        link_discord(connection, account_id, SUBJECT)
        access_id = grant_link(
            connection,
            character_id=character_id,
            account_id=account_id,
            granted_by=callers["C"].account_id,
            access_kind="co_owner",
        )
        run_id, proposal_id = uuid4(), uuid4()
        connection.execute(
            text(
                "INSERT INTO identity_migration_runs (id, source_label, profile_version, "
                "source_characters, source_players, already_linked, proposed, ambiguous, "
                "unresolved, correlation_id) VALUES (:id, 'probe', 'v', 1, 1, 0, "
                "1, 0, 0, :c)"
            ),
            {"id": run_id, "c": uuid4()},
        )
        connection.execute(
            text(
                "INSERT INTO identity_link_proposals (id, run_id, character_id, "
                "sheet_player_name, proposed_subject, resolution, decided_at, "
                "decided_by_account_id, decision_reason, granted_access_id, "
                "audit_correlation_id) VALUES (:id, :run, "
                ":character, 'Ada', :subject, 'confirmed', now(), :council, "
                "'confirmed', :access, :c)"
            ),
            {
                "id": proposal_id,
                "run": run_id,
                "character": character_id,
                "subject": str(SUBJECT),
                "council": callers["C"].account_id,
                "access": access_id,
                "c": uuid4(),
            },
        )
        connection.execute(
            text(
                "INSERT INTO identity_link_proposal_candidates (id, proposal_id, subject, "
                "observed_username) VALUES (:id, :proposal, :subject, 'linked.one')"
            ),
            {"id": uuid4(), "proposal": proposal_id, "subject": str(SUBJECT)},
        )
    return {
        "callers": callers,
        "character_id": character_id,
        "access_id": access_id,
        "run_id": run_id,
        "proposal_id": proposal_id,
    }


# ---------------------------------------------------------------------------
# Runtime grants — what the role may do
# ---------------------------------------------------------------------------


def test_the_runtime_role_can_read_every_new_table(restricted, seeded_run):
    """Denial evidence is only meaningful if the role can do its job.

    R-28 is a read by the application under this role, so a `SELECT` that failed here
    would mean the Council screen could not be rendered in production at all.
    """
    for table in NEW_TABLES:
        assert restricted.execute(text(f"SELECT count(*) FROM {table}")).scalar() >= 1


def test_the_runtime_role_can_write_a_run_its_proposals_and_its_candidates(
    restricted, seeded_run
):
    """Temporary C-04 uses this database role, so all evidence inserts are permitted."""
    run_id, proposal_id = uuid4(), uuid4()
    restricted.execute(
        text(
            "INSERT INTO identity_migration_runs (id, source_label, profile_version, "
            "source_characters, source_players, already_linked, proposed, ambiguous, "
            "unresolved, correlation_id) VALUES (:id, 'runtime', 'v', 1, 0, 0, "
            "0, 1, 0, :c)"
        ),
        {"id": run_id, "c": uuid4()},
    )
    restricted.execute(
        text(
            "INSERT INTO identity_link_proposals (id, run_id, character_id, "
            "sheet_player_name, resolution, audit_correlation_id) VALUES (:id, :run, "
            ":character, 'Bea', 'ambiguous', :c)"
        ),
        {
            "id": proposal_id,
            "run": run_id,
            "character": seeded_run["character_id"],
            "c": uuid4(),
        },
    )
    restricted.execute(
        text(
            "INSERT INTO identity_link_proposal_candidates (id, proposal_id, subject, "
            "observed_username) VALUES (:id, :proposal, '700000000000014999', 'bea.one')"
        ),
        {"id": uuid4(), "proposal": proposal_id},
    )
    # R-29/R-30 update a proposal's resolution in place, so `UPDATE` is needed too.
    restricted.execute(
        text(
            "UPDATE identity_link_proposals SET resolution = 'rejected', "
            "decided_at = now(), decided_by_account_id = :council, "
            "decision_reason = 'nothing here' WHERE id = :id"
        ),
        {"council": seeded_run["callers"]["C"].account_id, "id": proposal_id},
    )


def test_the_runtime_role_can_purge_a_run_and_cascade_to_its_children(
    restricted, seeded_run
):
    """Retention is a `DELETE` on the run, and the cascade does the rest.

    One statement, because the foreign keys cascade run → proposal → candidate: a
    partially purged run is not a state the retention sweep can produce.
    """
    restricted.execute(
        text("DELETE FROM identity_migration_runs WHERE id = :id"),
        {"id": seeded_run["run_id"]},
    )
    for table in NEW_TABLES:
        assert restricted.execute(text(f"SELECT count(*) FROM {table}")).scalar() == 0


def test_purging_a_run_never_removes_the_link_a_confirmation_created(
    restricted, seeded_run
):
    """The band's whole point: the working papers go and the decision stays.

    `granted_access_id` is `RESTRICT`, so this also establishes that the cascade
    deletes the *referencing* row and cannot reach through it to the access row it
    names — a `CASCADE` in the other direction would have made a retention sweep
    silently revoke authorization.
    """
    restricted.execute(
        text("DELETE FROM identity_migration_runs WHERE id = :id"),
        {"id": seeded_run["run_id"]},
    )
    assert (
        restricted.execute(
            text("SELECT count(*) FROM character_access WHERE id = :id"),
            {"id": seeded_run["access_id"]},
        ).scalar()
        == 1
    )


# ---------------------------------------------------------------------------
# Runtime grants — what the role may not do
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("table", NEW_TABLES)
def test_the_runtime_role_cannot_truncate_any_new_table(restricted, table):
    """`TRUNCATE` is revoked on all three, with the SQLSTATE recorded.

    A privilege denial and not any other kind: a syntax error or a missing table would
    also raise and would prove nothing about the grants, so `42501` is asserted.
    """
    with pytest.raises(ProgrammingError) as refusal:
        restricted.execute(text(f"TRUNCATE TABLE {table}"))
    assert sqlstate(refusal.value) == INSUFFICIENT_PRIVILEGE, table


@pytest.mark.parametrize(
    "statement",
    [
        "UPDATE audit_events SET action = 'forged'",
        "DELETE FROM audit_events",
        "TRUNCATE TABLE audit_events",
    ],
)
def test_the_runtime_role_still_cannot_touch_the_audit_history_a_confirmation_wrote(
    restricted, seeded_run, statement
):
    """The band above `identity_link_proposals`, restated where it matters here.

    A confirmation writes an `audit_events` row, and the runtime role can neither
    update, delete nor truncate it. So "the evidence is deletable" never becomes "the
    record of the decision is deletable", which is the only reason the `DELETE` grant
    above is acceptable.

    **One statement per case, deliberately, and `current_user` asserted first.** A
    denied statement aborts its transaction, and `SET ROLE` in PostgreSQL is
    *transactional*: rolling back to retry the next statement silently reverts the
    role to the owning login, and the remaining statements then succeed and the case
    passes for the worst possible reason. Written as a loop with a rollback between
    statements, this test reported that the runtime role could delete and truncate
    audit history — because by then it was no longer the runtime role. The assertion
    on `current_user` is what makes that unable to happen again.
    """
    assert restricted.execute(text("SELECT current_user")).scalar() == RUNTIME_ROLE
    with pytest.raises(Exception) as refusal:
        restricted.execute(text(statement))
    assert refusal.value is not None, statement


def test_the_runtime_role_cannot_bypass_the_balance_constraint(restricted):
    """A constraint is not a privilege, and the role cannot get around it either.

    The point of the case is that an unbalanced run is refused for the *restricted*
    role exactly as for the owner: the balance is a check constraint, so it is not
    something a grant could ever have relaxed, and this is the assertion that says so
    rather than assuming it.
    """
    with pytest.raises(Exception) as refusal:
        restricted.execute(
            text(
                "INSERT INTO identity_migration_runs (id, source_label, profile_version, "
                "source_characters, source_players, already_linked, proposed, ambiguous, "
                "unresolved, correlation_id) VALUES (:id, 'forged', 'v', 9, 0, 0, 1, 0, 0, :c)"
            ),
            {"id": uuid4(), "c": uuid4()},
        )
    assert "buckets_balance_against_source" in str(refusal.value)


def test_the_runtime_role_cannot_give_an_unconfirmed_proposal_a_grant(
    restricted, seeded_run
):
    """The schema's statement of TC-MIG-09, exercised as the runtime role.

    `ck_identity_link_proposals_a_confirmation_is_a_link` is a constraint, so the
    role that runs the application cannot write an authorizing proposal even if
    the service were removed entirely. It admits a grant **exactly** on a
    `confirmed` row, which is a state no C-04 run can write and which a Council
    confirmation reaches only by creating the access row it names, in the same
    statement.
    """
    run_id, proposal_id = uuid4(), uuid4()
    restricted.execute(
        text(
            "INSERT INTO identity_migration_runs (id, source_label, profile_version, "
            "source_characters, source_players, already_linked, proposed, ambiguous, "
            "unresolved, correlation_id) VALUES (:id, 'probe', 'v', 1, 0, 0, 0, 1, 0, :c)"
        ),
        {"id": run_id, "c": uuid4()},
    )
    with pytest.raises(Exception) as refusal:
        restricted.execute(
            text(
                "INSERT INTO identity_link_proposals (id, run_id, character_id, "
                "sheet_player_name, resolution, granted_access_id, audit_correlation_id) "
                "VALUES (:id, :run, :character, 'Bea', 'ambiguous', :access, :c)"
            ),
            {
                "id": proposal_id,
                "run": run_id,
                "character": seeded_run["character_id"],
                "access": seeded_run["access_id"],
                "c": uuid4(),
            },
        )
    assert "a_confirmation_is_a_link" in str(refusal.value)


def test_the_runtime_role_cannot_record_a_confirmation_that_created_nothing(
    restricted, seeded_run
):
    """The other half of the same constraint, in its own transaction.

    A `confirmed` row naming no access row is refused, so "Council decided this
    and nothing was created" is not a storable state — which is what makes the
    withdrawn deferred-apply workflow unrepresentable in this schema rather than
    merely unimplemented.

    Its own case because the first violation aborts the transaction: two
    constraint refusals in one `BEGIN` would leave the second reporting
    `InFailedSqlTransaction` and asserting nothing about the constraint.
    """
    run_id = uuid4()
    restricted.execute(
        text(
            "INSERT INTO identity_migration_runs (id, source_label, profile_version, "
            "source_characters, source_players, already_linked, proposed, ambiguous, "
            "unresolved, correlation_id) VALUES (:id, 'probe', 'v', 1, 0, 0, 1, 0, 0, :c)"
        ),
        {"id": run_id, "c": uuid4()},
    )
    with pytest.raises(Exception) as refusal:
        restricted.execute(
            text(
                "INSERT INTO identity_link_proposals (id, run_id, character_id, "
                "sheet_player_name, proposed_subject, resolution, decided_at, "
                "decided_by_account_id, decision_reason, audit_correlation_id) "
                "VALUES (:id, :run, :character, 'Bea', '700000000000009999', "
                "'confirmed', now(), :council, 'no link', :c)"
            ),
            {
                "id": uuid4(),
                "run": run_id,
                "character": seeded_run["character_id"],
                "council": seeded_run["callers"]["C"].account_id,
                "c": uuid4(),
            },
        )
    assert "a_confirmation_is_a_link" in str(refusal.value)


# ---------------------------------------------------------------------------
# A decision states its reason — the independent review's finding 2
# ---------------------------------------------------------------------------
#
# R-29 and R-30 both require a reason and `IdentityMigrationService` validates
# one, but this role holds `UPDATE` on `identity_link_proposals`. Migration
# 0010's original `decision_reason IS NULL OR length(trim(decision_reason)) > 0`
# therefore admitted a `confirmed` row with no reason at all from one direct
# statement — a half-decided authorization record, which is exactly what the
# service validation was supposed to make impossible. The cases below are the
# database's own answer, taken as the role that runs the application.
#
# Each violation aborts its transaction, so each is its own case: two refusals in
# one `BEGIN` would leave the second reporting `InFailedSqlTransaction` and
# asserting nothing about the constraint it names.


@pytest.fixture()
def decidable(migrated_database, seeded_run):
    """A run with two outstanding proposals, and an access row one could name.

    Written as the owner, like `seeded_run`, so the cases below are about what
    the restricted role may do to a decision rather than about whether it may
    create the evidence. One proposal is `proposed` and carries a snowflake, so a
    valid R-29 confirmation is expressible; the other is `unresolved`, which is a
    row R-30 may reject and R-29 may not touch.
    """
    with migrated_database.begin() as connection:
        confirmable_character = make_character(connection, display_name="Brand Vale")
        rejectable_character = make_character(connection, display_name="Cere Ash")
        account_id = make_account(connection, label="second")
        seed_discord_member(connection, subject=SECOND_SUBJECT, username="second.one")
        link_discord(connection, account_id, SECOND_SUBJECT)
        # A real, active link a confirmation can name.
        # `ck_identity_link_proposals_a_confirmation_is_a_link` requires one, so
        # a case about the *reason* still has to satisfy every other rule.
        access_id = grant_link(
            connection,
            character_id=confirmable_character,
            account_id=account_id,
            granted_by=seeded_run["callers"]["C"].account_id,
            access_kind="co_owner",
        )
        run_id = uuid4()
        connection.execute(
            text(
                "INSERT INTO identity_migration_runs (id, source_label, profile_version, "
                "source_characters, source_players, already_linked, proposed, ambiguous, "
                "unresolved, correlation_id) VALUES (:id, 'probe', 'v', 2, 2, 0, 1, 0, 1, :c)"
            ),
            {"id": run_id, "c": uuid4()},
        )
        confirmable, rejectable = uuid4(), uuid4()
        connection.execute(
            text(
                "INSERT INTO identity_link_proposals (id, run_id, character_id, "
                "sheet_player_name, proposed_subject, resolution, audit_correlation_id) "
                "VALUES (:id, :run, :character, 'Bea', :subject, 'proposed', :c)"
            ),
            {
                "id": confirmable,
                "run": run_id,
                "character": confirmable_character,
                "subject": str(SECOND_SUBJECT),
                "c": uuid4(),
            },
        )
        connection.execute(
            text(
                "INSERT INTO identity_link_proposals (id, run_id, character_id, "
                "sheet_player_name, resolution, audit_correlation_id) "
                "VALUES (:id, :run, :character, 'Cyd', 'unresolved', :c)"
            ),
            {
                "id": rejectable,
                "run": run_id,
                "character": rejectable_character,
                "c": uuid4(),
            },
        )
    return {
        "confirmable": confirmable,
        "rejectable": rejectable,
        "access_id": access_id,
        "council_account_id": seeded_run["callers"]["C"].account_id,
    }


def decide_statement(reason_sql: str) -> str:
    """One R-29-shaped `UPDATE`, with the reason expression left to the caller.

    Written out rather than parameterised over the whole statement so that each
    case below differs in exactly the value under test and in nothing else.
    """
    return (
        "UPDATE identity_link_proposals SET resolution = 'confirmed', "
        "decided_at = now(), decided_by_account_id = :council, "
        f"decision_reason = {reason_sql}, granted_access_id = :access "
        "WHERE id = :id"
    )


def test_the_runtime_role_cannot_confirm_a_proposal_with_no_reason(
    restricted, decidable
):
    """A `confirmed` row with `decision_reason IS NULL` is refused by the database.

    The reviewed defect exactly: every other rule of a confirmation is satisfied
    — the subject resolves, the decision columns agree, a real access row is
    named — and the only thing missing is the reason R-29 requires.
    """
    with pytest.raises(Exception) as refusal:
        restricted.execute(
            text(decide_statement("NULL")),
            {
                "council": decidable["council_account_id"],
                "access": decidable["access_id"],
                "id": decidable["confirmable"],
            },
        )
    assert "a_decision_states_its_reason" in str(refusal.value)


def test_the_runtime_role_cannot_reject_a_proposal_with_no_reason(
    restricted, decidable
):
    """R-30 requires a reason too, and a rejection reaches no grant to hide behind."""
    with pytest.raises(Exception) as refusal:
        restricted.execute(
            text(
                "UPDATE identity_link_proposals SET resolution = 'rejected', "
                "decided_at = now(), decided_by_account_id = :council, "
                "decision_reason = NULL WHERE id = :id"
            ),
            {
                "council": decidable["council_account_id"],
                "id": decidable["rejectable"],
            },
        )
    assert "a_decision_states_its_reason" in str(refusal.value)


def test_the_runtime_role_cannot_decide_with_a_blank_reason(restricted, decidable):
    """Whitespace is not a reason, and the older constraint is what says so.

    Named separately from `a_decision_states_its_reason` on purpose: that one
    answers *"is there a reason at all?"* and this one answers *"is it worth
    reading?"*. A single constraint spelling both would report the wrong fact for
    half the failures it catches.
    """
    with pytest.raises(Exception) as refusal:
        restricted.execute(
            text(decide_statement("'   '")),
            {
                "council": decidable["council_account_id"],
                "access": decidable["access_id"],
                "id": decidable["confirmable"],
            },
        )
    assert "decision_reason_not_blank" in str(refusal.value)


def test_an_outstanding_proposal_cannot_carry_a_decision_reason(
    restricted, decidable
):
    """The other direction, and the reason the rule is an equivalence.

    A reason on a row nobody has decided is a decision that did not happen,
    readable by R-28 as though it had. `proposed`, `ambiguous` and `unresolved`
    carry no reason at all.
    """
    with pytest.raises(Exception) as refusal:
        restricted.execute(
            text(
                "UPDATE identity_link_proposals SET decision_reason = 'looks right' "
                "WHERE id = :id"
            ),
            {"id": decidable["confirmable"]},
        )
    assert "a_decision_states_its_reason" in str(refusal.value)


def test_valid_r29_and_r30_transitions_still_pass_every_constraint(
    restricted, decidable
):
    """Denial evidence proves nothing if the permitted transitions stopped working.

    Both decisions in one case and in one transaction, because both are expected
    to succeed: nothing here aborts, so nothing here needs isolating.
    """
    restricted.execute(
        text(decide_statement("'Council confirmed the Sheet evidence'")),
        {
            "council": decidable["council_account_id"],
            "access": decidable["access_id"],
            "id": decidable["confirmable"],
        },
    )
    restricted.execute(
        text(
            "UPDATE identity_link_proposals SET resolution = 'rejected', "
            "decided_at = now(), decided_by_account_id = :council, "
            "decision_reason = 'No single identity in the evidence' WHERE id = :id"
        ),
        {
            "council": decidable["council_account_id"],
            "id": decidable["rejectable"],
        },
    )
    decided = restricted.execute(
        text(
            "SELECT resolution, decision_reason FROM identity_link_proposals "
            "WHERE id = ANY(:ids) ORDER BY resolution"
        ),
        {"ids": [decidable["confirmable"], decidable["rejectable"]]},
    ).all()
    assert [(row[0], row[1]) for row in decided] == [
        ("confirmed", "Council confirmed the Sheet evidence"),
        ("rejected", "No single identity in the evidence"),
    ]


def test_the_runtime_role_cannot_create_a_table_in_the_schema(restricted):
    """Schema change is a migration's authority, never the application's."""
    with pytest.raises(ProgrammingError) as refusal:
        restricted.execute(text("CREATE TABLE forged_evidence (id uuid PRIMARY KEY)"))
    assert sqlstate(refusal.value) == INSUFFICIENT_PRIVILEGE


def test_public_holds_nothing_on_the_three_new_tables(migrated_database):
    """The template's `REVOKE ... FROM PUBLIC` covers them, and PUBLIC is everybody.

    One `GRANT ALL ... TO PUBLIC` — from a migration, a restore, a recovery session —
    would hand every role in the cluster whatever it granted, without naming any of
    them. The template revokes it; this asserts the revocation reached the new tables.
    """
    with migrated_database.begin() as owner:
        for statement in grant_statements():
            owner.execute(text(statement))
        holdings = owner.execute(
            text(
                "SELECT table_name, privilege_type FROM information_schema.table_privileges "
                "WHERE grantee = 'PUBLIC' AND table_name = ANY(:names)"
            ),
            {"names": list(NEW_TABLES)},
        ).all()
    assert holdings == [], holdings


# ---------------------------------------------------------------------------
# Request bounds: cursors, page sizes, bodies
# ---------------------------------------------------------------------------


@pytest.fixture()
def council(migrated_database, settings):
    return seed_callers(migrated_database, settings, states=("C",))["C"]


@pytest.mark.parametrize(
    ("cursor", "label"),
    [
        ("not-a-cursor", "unsigned garbage"),
        (base64.urlsafe_b64encode(b"forged").decode(), "well-formed base64, no signature"),
        ("", "empty"),
        ("." * 40, "punctuation only"),
    ],
)
async def test_a_tampered_cursor_is_refused_and_never_reset_to_page_one(
    client, settings, council, cursor, label
):
    """N-64. A refused cursor, not a silent reset.

    A reset hides tampering behind a page that looks like it worked, which is the
    failure mode this rule exists to prevent: the caller believes they are seeing the
    page they asked for. The cursor is HMAC-signed and scoped, so an unsigned or
    foreign token is refused outright.

    The empty case is the exception and is deliberately in the list: an absent cursor
    means *"the first page"*, and `?cursor=` is absent rather than tampered.
    """
    response = await client.get(
        f"/v1/council/characters?cursor={cursor}", cookies=council.cookies(settings)
    )
    if cursor == "":
        assert response.status_code == 200, label
    else:
        assert response.status_code in {400, 422}, f"{label}: {response.status_code}"


async def test_a_cursor_from_another_scope_is_refused(client, settings, council):
    """A cursor is scoped, so one screen's token is not another screen's.

    Signing without scoping would let a proposals cursor be replayed against the
    character index, which is a different query over a different table — the signature
    would be valid and the position meaningless.
    """
    from application.web import pagination

    token = pagination.encode(
        settings.cursor_key,
        scope="proposals",
        parts=("00000000-0000-4000-8000-000000000001",),
    )
    response = await client.get(
        f"/v1/council/characters?cursor={token}", cookies=council.cookies(settings)
    )
    assert response.status_code in {400, 422}


@pytest.mark.parametrize(
    ("size", "label"),
    [
        ("0", "zero"),
        ("-5", "negative"),
        ("100000", "far above the maximum"),
        ("abc", "not a number"),
        ("1e9", "scientific notation"),
    ],
)
async def test_a_page_size_outside_the_bounds_is_clamped_not_trusted(
    client, settings, council, size, label
):
    """N-21's page size. Clamped, and the response is still a page.

    A page size is a *hint*, unlike a cursor: a caller asking for a hundred thousand
    rows is asking for something the server declines to do, and the useful answer is
    the largest page it will serve rather than a refusal. `page_size` is the one
    function that decides it, so no route can be persuaded otherwise.
    """
    response = await client.get(
        f"/v1/council/characters?size={size}", cookies=council.cookies(settings)
    )
    assert response.status_code == 200, label


def test_the_page_size_helper_clamps_every_out_of_range_value():
    """The clamp itself, as a unit, so the bound is asserted rather than inferred."""
    from application.web.pagination import page_size
    from application.web.view_models import PAGE_SIZE_DEFAULT, PAGE_SIZE_MAXIMUM

    assert page_size(None) == PAGE_SIZE_DEFAULT
    assert page_size("") == PAGE_SIZE_DEFAULT
    assert page_size("abc") == PAGE_SIZE_DEFAULT
    assert page_size("0") == PAGE_SIZE_DEFAULT
    assert page_size("-1") == PAGE_SIZE_DEFAULT
    assert page_size("1") == 1
    assert page_size(str(PAGE_SIZE_MAXIMUM)) == PAGE_SIZE_MAXIMUM
    assert page_size(str(PAGE_SIZE_MAXIMUM + 1)) == PAGE_SIZE_MAXIMUM
    assert page_size("999999") == PAGE_SIZE_MAXIMUM


async def test_a_body_over_the_bound_is_refused_before_it_is_read(
    client, settings, council, migrated_database
):
    """N-19's body bound, on a P3.2 mutation.

    `413`, and refused at the middleware before routing — so the handler never runs,
    the form is never parsed, and a caller cannot use a large body to make the server
    do work on their behalf. The reason field is bounded at 500 characters by §3.2 and
    refuses rather than truncates, so a body this size is not a long justification: it
    is a request the server declines to read.
    """
    with migrated_database.begin() as connection:
        character_id = make_character(connection, display_name="Bounded")
    # One byte over the **configured** bound rather than an arbitrary large number:
    # N-19 is a policy range (1 KiB…1 MiB) and the deployment picks a value inside it,
    # so a literal here would test a different bound from the one in force.
    oversized = "reason=" + ("x" * (settings.bounds.max_request_bytes + 1))
    response = await client.post(
        f"/v1/council/characters/{character_id}/links",
        cookies=council.cookies(settings),
        headers={"Origin": PUBLIC_ORIGIN, "Content-Type": FORM},
        content=oversized,
    )
    assert response.status_code == 413
    assert (
        count_rows(migrated_database, "SELECT count(*) FROM character_access") == 0
    )


def count_rows(engine, statement):
    with engine.begin() as connection:
        return connection.execute(text(statement)).scalar()


# ---------------------------------------------------------------------------
# Escaping
# ---------------------------------------------------------------------------


async def test_user_controlled_text_is_escaped_in_every_view_that_renders_it(
    client, settings, council, migrated_database
):
    """Actor names and Sheet names come from outside the platform and are escaped.

    Jinja's autoescape is what does it, and this is the assertion that autoescape is
    actually on for these templates: the payload is a script tag inside a character's
    display name and a proposal's Sheet player name, and neither may appear
    unescaped in the response.
    """
    payload = "<script>alert('x')</script>"
    with migrated_database.begin() as connection:
        character_id = make_character(connection, display_name=payload)
        run_id = uuid4()
        connection.execute(
            text(
                "INSERT INTO identity_migration_runs (id, source_label, profile_version, "
                "source_characters, source_players, already_linked, proposed, ambiguous, "
                "unresolved, correlation_id) VALUES (:id, :label, 'v', 1, 1, 0, 0, "
                "0, 1, :c)"
            ),
            {"id": run_id, "label": payload[:120], "c": uuid4()},
        )
        connection.execute(
            text(
                "INSERT INTO identity_link_proposals (id, run_id, character_id, "
                "sheet_player_name, resolution, audit_correlation_id) VALUES (:id, :run, "
                ":character, :name, 'unresolved', :c)"
            ),
            {
                "id": uuid4(),
                "run": run_id,
                "character": character_id,
                "name": payload,
                "c": uuid4(),
            },
        )

    for path in (
        "/v1/council/characters",
        "/v1/council/identity-migration",
        f"/v1/council/characters/{character_id}/links",
    ):
        response = await client.get(path, cookies=council.cookies(settings))
        assert response.status_code == 200, path
        assert "<script>alert" not in response.text, path
        # And the text is *present*, escaped — not silently dropped, which would be a
        # different defect wearing the same passing assertion.
        assert "&lt;script&gt;" in response.text, path
