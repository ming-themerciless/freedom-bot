"""The M-2 pipeline end to end: TC-MIG-08 to TC-MIG-13 and TC-MIG-17, real PostgreSQL.

```text
C-04 --dry-run --player-tab   ->  R-28    ->  R-29 / R-30           ->  R-28
read Sheet evidence               review      confirm: link + audits    see it
write proposals                               reject: decision only     linked
write NO character_access                     one transaction, or none
```

**Two** stages, and this module is organised as those two plus the reads that
bracket them.

## What this rewrite answers

The maintainer's ruling of 2026-08-17 (change-log entry C-P3.2-A, OD-46) resolved
a contradiction between four accepted passages: a confirmation **is** the
activation, and the withdrawn `C-05 --apply` step that used to materialize
confirmed proposals afterwards is gone. Every case in this module that asserted
the deferred apply certified a workflow that is no longer the accepted one, so
those cases are removed rather than adjusted, and the confirmation cases assert
the link.

It also answers the independent review's reproduced identity-integrity defect: two
player-tab rows whose names differ only by case silently collided, and the later
one decided the confirmable Discord identity. The duplicate cases below are
TC-MIG-17.

## What is substituted, and what is not

Exactly two things: the Sheet reader and the settings/engine pair. Everything
between them is production code — `read_sources`, the layout guards in
`adapters/sheets/identity_evidence.py`, `IdentityEvidenceRunService`, the
resolver, `IdentityMigrationService`, `CharacterAccessService`, every repository,
the migration-0010 schema and every constraint on it.

The Sheet reader is a closure over canned **raw values** rather than a fake
returning typed rows, so the header/position guards run for real. It has one
method, and it reads: there is no `batch_update` on it, because there is no
`batch_update` anywhere in the boundary the tool uses.

No real player, Sheet, Discord, Foundry or production data appears here. Every
snowflake is outside the range Discord has issued and every name is invented.
"""
from __future__ import annotations

import threading
from uuid import UUID, uuid4

import pytest
from sqlalchemy import create_engine, text

import tools.identity_migration as command
from adapters.sheets.identity_evidence import (
    PLAYER_FIRST_DATA_ROW,
    SheetLayoutError,
)
from adapters.sheets.read_only import ReaderSelection
from adapters.web.repositories import (
    AccountRepository,
    CharacterAccessRepository,
    IdentityEvidenceSourceRepository,
    IdentityProposalRepository,
    WebAuditRepository,
)
from application.audit import ActorCapability
from application.web.capabilities import (
    AdministratorScope,
    AuthMethod,
    WebAuthorizationContext,
)
from application.web.character_access import CharacterAccessService, StaleVersion
from application.web.identity_evidence import (
    AMBIGUOUS,
    CONFIRMED_ACCESS_KIND,
    PROPOSED,
    UNRESOLVED,
    AlreadyLinked,
    IdentityEvidenceRunService,
    IdentityMigrationService,
    NotConfirmable,
    SheetCharacterRow,
    SheetPlayer,
    UnmappedSourceRows,
)
from application.web.view_models import SMALL_LIST_BOUND
from tests.conftest import TEST_ENVIRONMENT, resolve_test_database_url
from tests.web.conftest import link_discord, make_account, utcnow
from tests.web.portal_fixtures import (
    character_version,
    clean_p3_2_tables,
    csrf_token_for,
    grant_link,
    make_character,
    map_sheet_row,
    seed_callers,
    seed_discord_member,
)
from tests.web_fixtures import PUBLIC_ORIGIN, TEST_GUILD_ID

pytestmark = pytest.mark.database

#: Synthetic, outside the range Discord has issued.
ADA_SUBJECT = 700000000000003001
TWIN_A_SUBJECT = 700000000000003003
TWIN_B_SUBJECT = 700000000000003004
CYD_SUBJECT = 700000000000003005

CHARACTER_TAB = "Characters"
#: The name a *test* supplies on the command line, and deliberately **not**
#: `Players`. The maintainer-confirmed one-time tab is `Players` (`C-P3.2-B`), and
#: the adapter still carries no `PLAYER_TAB` constant (migration contract §7.7):
#: `--player-tab` is required so that one-time migration input stays an explicit
#: argument rather than enduring command configuration. Driving the command with a
#: different name is what proves the run reads the tab the operator supplied and
#: not one the code remembers.
PLAYER_TAB = "Player Register"


# ---------------------------------------------------------------------------
# Raw Sheet values, shaped exactly as Google returns them
# ---------------------------------------------------------------------------
def character_values(rows_):
    """`[header, second header, *data]` with A/B/C/F/AL in their real positions.

    Built positionally on purpose: the layout guard checks the *position* as well
    as the name, and a fixture that built the header dict directly would skip the
    guard the production reader depends on.
    """
    headers = [""] * 38
    headers[0] = "Character Name (short)"
    headers[1] = "Character Name (long)"
    headers[2] = "Player Name"
    headers[5] = "Character Level"
    headers[37] = "Active"

    values = [headers, [""] * 38]
    for display_name, player_name in rows_:
        row = [""] * 38
        row[0] = display_name
        row[1] = f"{display_name} of the Free Blades"
        row[2] = player_name
        row[5] = "3"
        row[37] = "1"
        values.append(row)
    return values


def player_values(rows_):
    """The player tab: A, B and D at their inventory positions, data from row 2."""
    headers = ["Player Name", "Discord Name", "Last date played", "Active DM"]
    values = [headers]
    for player_name, discord_name, active_dm in rows_:
        values.append([player_name, discord_name or "", "", "1" if active_dm else "0"])
    return values


class ReaderProbe:
    """Stands in for `build_values_reader`, and records whether it was asked.

    Constructed with `characters=None` it **refuses to build a reader at all**,
    which is how a case asserts that a path never reaches Google: the assertion is
    that the command never gets here, not that a fake returned canned data.
    """

    __slots__ = ("_characters", "_players", "builds", "ranges")

    def __init__(self, characters=None, players=None) -> None:
        self._characters = characters
        self._players = players
        self.builds = 0
        self.ranges: list[str] = []

    def build(self, _environ) -> ReaderSelection:
        self.builds += 1
        if self._characters is None:
            raise AssertionError("a Sheet reader was constructed unexpectedly")

        def read_values(a1_range: str, value_render_option: str = "UNFORMATTED_VALUE"):
            self.ranges.append(a1_range)
            tab = a1_range.split("!", 1)[0]
            if tab == CHARACTER_TAB:
                return self._characters
            if tab == PLAYER_TAB:
                return self._players
            raise AssertionError(f"the run read an unexpected range: {a1_range}")

        return ReaderSelection(
            read_values=read_values,
            read_only_credential=True,
            note="Using the read-only Sheets credential.",
        )

    @property
    def tabs_read(self) -> list[str]:
        return [entry.split("!", 1)[0] for entry in self.ranges]


#: The whole accepted C-04 invocation, in one place. `--player-tab` is required,
#: so every case that drives the command states the tab the way an operator has
#: to (§7.7) — a default here would let a case pass without the argument the
#: operator cannot omit.
C04_ARGV = ["--dry-run", "--player-tab", PLAYER_TAB]


def c04_settings(settings):
    """The production settings shape, built by the production validator.

    Deliberately not a stand-in carrying a `guild_id` attribute. The narrow
    `IdentityMigrationSettings` is what `build_run_context` returns, so a case
    driven by a substitute object would keep passing if the command began
    reading a member the real settings type does not carry — which is the drift
    this helper exists to catch. The values are the suite's own disposable ones,
    and they are validated by `from_environment`, so the canonical database
    checks run here exactly as they do for an operator.
    """
    return command.IdentityMigrationSettings.from_environment(
        {
            "WEB_ENVIRONMENT": TEST_ENVIRONMENT,
            "WEB_DATABASE_URL": resolve_test_database_url(),
            "WEB_DISCORD_GUILD_ID": str(settings.discord.guild_id),
        }
    )


def run_command(monkeypatch, engine, settings, *, argv=None, characters=None, players=None):
    """Drive the real entry point. Returns `(exit_code, probe)`."""
    probe = ReaderProbe(characters, players)
    command_settings = c04_settings(settings)
    monkeypatch.setattr(
        command, "build_run_context", lambda: (engine, command_settings)
    )
    monkeypatch.setattr(command, "build_values_reader", probe.build)
    # The engine is the suite's; disposing it would break every later case.
    monkeypatch.setattr(engine, "dispose", lambda: None)
    return command.main(list(C04_ARGV if argv is None else argv)), probe


def rows(engine, statement, **parameters):
    with engine.begin() as connection:
        return connection.execute(text(statement), parameters).mappings().all()


def scalar(engine, statement, **parameters):
    with engine.begin() as connection:
        return connection.execute(text(statement), parameters).scalar()


def access_rows(engine) -> int:
    return scalar(engine, "SELECT count(*) FROM character_access")


def audit_actions(engine) -> list[str]:
    return [
        row["action"]
        for row in rows(engine, "SELECT action FROM audit_events ORDER BY occurred_at, action")
    ]


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def clean_between_cases(request):
    """Empty the P3.2 tables after **every** case in this module.

    `tests/web/conftest.py`'s autouse cleanup covers the identity tables and stops
    at `platform_accounts`; characters, their links, their Sheet-row mappings and
    the runs are this package's and are cleaned here. It has to run *before* that
    one, because `character_access` references `platform_accounts` `RESTRICT` —
    which fixture finalisation order gives, since the conftest fixture is set up
    first and therefore torn down last.

    Module-wide rather than per-fixture: several cases seed characters and Sheet
    rows without going through `sheet_world`, and `sheet_row_mappings` is unique on
    `(sheet_tab, row_index)`, so one case's row 3 collides with the next one's.
    """
    yield
    if "migrated_database" not in request.fixturenames:
        return
    engine = request.getfixturevalue("migrated_database")
    with engine.begin() as connection:
        clean_p3_2_tables(connection)


@pytest.fixture()
def council(migrated_database, settings):
    """The seven caller states, and a Council session cookie among them."""
    return seed_callers(migrated_database, settings)


@pytest.fixture()
def sheet_world(migrated_database):
    """Four characters, four players and three guild members, all synthetic.

    One character resolves to exactly one member; one is ambiguous between two
    same-named members; one names a player nobody in the guild matches; one names a
    player whose Discord cell is blank.

    Returns the ids and the canned Sheet values, so a case can drive the command
    and then assert against the database.
    """
    with migrated_database.begin() as connection:
        alia = make_character(connection, display_name="Alia Storm")
        brand = make_character(connection, display_name="Brand Vale")
        cere = make_character(connection, display_name="Cere Ash")
        dain = make_character(connection, display_name="Dain Rell")
        # Sheet rows 3..6, in order.
        for offset, character_id in enumerate((alia, brand, cere, dain)):
            map_sheet_row(connection, character_id=character_id, row_index=3 + offset)

        seed_discord_member(connection, subject=ADA_SUBJECT, username="ada.one")
        seed_discord_member(connection, subject=TWIN_A_SUBJECT, username="shared.name")
        seed_discord_member(connection, subject=TWIN_B_SUBJECT, username="SHARED.NAME")

    characters = character_values(
        [
            ("Alia Storm", "Ada"),
            ("Brand Vale", "Bea"),
            ("Cere Ash", "Cyd"),
            ("Dain Rell", "Dot"),
        ]
    )
    players = player_values(
        [
            ("Ada", "ada.one", False),
            ("Bea", "shared.name", True),
            ("Cyd", "nobody.in.guild", False),
            ("Dot", None, False),
        ]
    )
    return {
        "alia": alia,
        "brand": brand,
        "cere": cere,
        "dain": dain,
        "characters": characters,
        "players": players,
    }


def council_context(account_id: UUID) -> WebAuthorizationContext:
    return WebAuthorizationContext(
        account_id=account_id,
        auth_method=AuthMethod.DISCORD_OAUTH,
        capabilities=frozenset(
            {ActorCapability.GUILD_MEMBER, ActorCapability.GUILD_COUNCIL}
        ),
        administrator_scope=AdministratorScope.FULL,
        membership=None,
    )


def migration_service(
    connection, settings, *, audit=None, proposals=None, access_service=None
):
    """R-28/R-29/R-30's service, built exactly as request composition builds it.

    `access_service` is the **same** `CharacterAccessService` R-25 grants through
    — the confirmation is not a second grant implementation. The three optional
    arguments exist so a case can inject one failure into one collaborator; every
    other collaborator is production code on the caller's connection, which is
    what makes the transaction boundary real.
    """
    accounts = AccountRepository(connection)
    access = CharacterAccessRepository(connection)
    audit = audit if audit is not None else WebAuditRepository(connection)
    return IdentityMigrationService(
        proposals=proposals or IdentityProposalRepository(connection),
        access_service=access_service
        or CharacterAccessService(access=access, accounts=accounts, audit=audit),
        access=access,
        accounts=accounts,
        audit=audit,
        cursor_key=settings.cursor_key,
    )


def confirm(
    engine,
    settings,
    *,
    proposal_id,
    account_id,
    expected_version=0,
    reason="Council confirmed it",
):
    """One R-29 confirmation, through the service, in its own transaction."""
    correlation_id = uuid4()
    with engine.begin() as connection:
        migration_service(connection, settings).confirm(
            context=council_context(account_id),
            proposal_id=proposal_id,
            reason=reason,
            expected_version=expected_version,
            correlation_id=correlation_id,
            now=utcnow(),
        )
    return correlation_id


def revoke(
    engine,
    settings,
    *,
    character_id,
    access_id,
    account_id,
    reason="Council revoked the link",
):
    """One R-26 revocation of an existing link, through R-25/R-26's own service.

    The version is read inside the same transaction rather than passed in: a
    confirmation has already bumped it, and a case that had to track that number
    would be asserting arithmetic about the fixture instead of about the
    revocation.
    """
    correlation_id = uuid4()
    with engine.begin() as connection:
        accounts = AccountRepository(connection)
        access = CharacterAccessRepository(connection)
        audit = WebAuditRepository(connection)
        CharacterAccessService(
            access=access, accounts=accounts, audit=audit
        ).revoke(
            context=council_context(account_id),
            character_id=character_id,
            access_id=access_id,
            reason=reason,
            expected_version=character_version(connection, character_id),
            correlation_id=correlation_id,
            now=utcnow(),
        )
    return correlation_id


def proposal_id_for(engine, resolution):
    return scalar(
        engine,
        "SELECT id FROM identity_link_proposals WHERE resolution = :resolution "
        "ORDER BY id LIMIT 1",
        resolution=resolution,
    )


def latest_run_id(engine):
    return scalar(
        engine,
        "SELECT id FROM identity_migration_runs ORDER BY produced_at DESC, id DESC "
        "LIMIT 1",
    )


@pytest.fixture()
def proposed_run(monkeypatch, migrated_database, settings, council, sheet_world):
    """C-04, plus the platform account the one confirmable proposal names.

    The state every confirmation case starts from: one reviewed run with one
    confirmable proposal, an account for the Discord identity it proposes, and
    **no** `character_access` row yet.
    """
    exit_code, _probe = run_command(
        monkeypatch,
        migrated_database,
        settings,
        characters=sheet_world["characters"],
        players=sheet_world["players"],
    )
    assert exit_code == command.EXIT_OK

    with migrated_database.begin() as connection:
        ada_account = make_account(connection, label="ada")
        link_discord(connection, ada_account, ADA_SUBJECT)
        version = character_version(connection, sheet_world["alia"])

    assert access_rows(migrated_database) == 0
    return {
        "run_id": latest_run_id(migrated_database),
        "proposal_id": proposal_id_for(migrated_database, PROPOSED),
        "account_id": ada_account,
        "character_id": sheet_world["alia"],
        "character_version": version,
        "council_account_id": council["C"].account_id,
    }


# ===========================================================================
# Stage 1 — C-04 writes evidence and nothing else
# ===========================================================================


def test_c04_writes_balanced_evidence_and_not_one_access_row(
    monkeypatch, migrated_database, settings, sheet_world
):
    """TC-MIG-08's first half and TC-MIG-09's. The real `main()`, real argv.

    Argument parsing, the Sheet layout guards, `IdentityEvidenceRunService`, the
    resolver, both repositories and every migration-0010 constraint are on the
    path. What the run produces is one evidence run, one proposal per source row,
    every ambiguity candidate — and zero `character_access` rows, which is the
    property the whole pipeline rests on.
    """
    exit_code, probe = run_command(
        monkeypatch,
        migrated_database,
        settings,
        characters=sheet_world["characters"],
        players=sheet_world["players"],
    )
    assert exit_code == command.EXIT_OK

    # Two ranges, and only two: `Characters` and the player tab the operator
    # named (§7.1, §7.7).
    assert probe.tabs_read == [CHARACTER_TAB, PLAYER_TAB]

    run = rows(migrated_database, "SELECT * FROM identity_migration_runs")
    assert len(run) == 1
    # Every run is a C-04 evidence run, and the column is `CHECK`-ed so.
    assert run[0]["dry_run"] is True
    assert run[0]["source_characters"] == 4
    assert run[0]["source_players"] == 4
    assert (run[0]["proposed"], run[0]["ambiguous"], run[0]["unresolved"]) == (1, 1, 2)
    assert run[0]["already_linked"] == 0
    assert run[0]["profile_version"]
    # The label names the ranges and nothing worth stealing: no spreadsheet id.
    assert run[0]["source_label"] == f"{CHARACTER_TAB}!C + {PLAYER_TAB}!A/B/D"
    # §7.4's first balance, on the row PostgreSQL accepted.
    assert (
        run[0]["already_linked"] + run[0]["proposed"] + run[0]["ambiguous"]
        + run[0]["unresolved"]
        == run[0]["source_characters"]
    )

    proposals = rows(
        migrated_database,
        "SELECT character_id, resolution, proposed_subject, sheet_player_name, "
        "sheet_discord_name, active_dm, decided_at, granted_access_id "
        "FROM identity_link_proposals ORDER BY sheet_player_name",
    )
    assert [(row["sheet_player_name"], row["resolution"]) for row in proposals] == [
        ("Ada", PROPOSED),
        ("Bea", AMBIGUOUS),
        ("Cyd", UNRESOLVED),
        ("Dot", UNRESOLVED),
    ]
    assert proposals[0]["proposed_subject"] == str(ADA_SUBJECT)
    assert proposals[0]["character_id"] == sheet_world["alia"]
    # `Active DM` is recorded as evidence (§7.1) and read by no capability.
    assert proposals[1]["active_dm"] is True
    # No decision, and — the property that matters — no grant on any row.
    for row in proposals:
        assert row["decided_at"] is None
        assert row["granted_access_id"] is None

    # Every ambiguous candidate is a row of its own — typed child rows, never a
    # delimited string, a JSON collection or an array (plan §7.3.1).
    candidates = rows(
        migrated_database,
        "SELECT subject FROM identity_link_proposal_candidates ORDER BY subject",
    )
    assert [row["subject"] for row in candidates] == sorted(
        [str(ADA_SUBJECT), str(TWIN_A_SUBJECT), str(TWIN_B_SUBJECT)]
    )
    assert access_rows(migrated_database) == 0
    assert audit_actions(migrated_database) == []


def test_the_evidence_run_service_can_reach_no_grant_at_all(
    migrated_database, settings
):
    """TC-MIG-09's structural half: C-04 has nothing on it that could authorize.

    `IdentityEvidenceRunService` holds a source repository, a proposal repository,
    a guild id and a scan batch. No `CharacterAccessService`, no access repository
    and no audit repository, so "C-04 creates no authorization" is a fact about
    what the object *has* rather than a promise about what it calls.
    """
    with migrated_database.begin() as connection:
        service = IdentityEvidenceRunService(
            sources=IdentityEvidenceSourceRepository(connection),
            proposals=IdentityProposalRepository(connection),
            guild_id=TEST_GUILD_ID,
        )
        held = [getattr(service, name) for name in IdentityEvidenceRunService.__slots__]
    assert not any(isinstance(value, CharacterAccessService) for value in held)
    assert not any(isinstance(value, CharacterAccessRepository) for value in held)
    assert not any(isinstance(value, WebAuditRepository) for value in held)


def test_the_database_refuses_a_grant_on_anything_but_a_confirmation(
    migrated_database, monkeypatch, settings, sheet_world, council
):
    """The same property, with the application bypassed entirely.

    `ck_identity_link_proposals_a_confirmation_is_a_link` is what makes "C-04
    wrote no authorization" and "a rejection creates no link" properties of the
    table. The insert path is bypassed and the column set directly; PostgreSQL
    refuses it on a `proposed` row.
    """
    run_command(
        monkeypatch,
        migrated_database,
        settings,
        characters=sheet_world["characters"],
        players=sheet_world["players"],
    )
    with migrated_database.begin() as connection:
        # The shadow trigger from migration 0008 refuses an access row whose
        # account has no active Discord identity, so the member exists first.
        seed_discord_member(connection, subject=CYD_SUBJECT, username="cyd.two")
        account = make_account(connection, label="stray")
        link_discord(connection, account, CYD_SUBJECT)
        access_id = grant_link(
            connection,
            character_id=sheet_world["brand"],
            account_id=account,
            granted_by=council["C"].account_id,
        )
    proposal_id = proposal_id_for(migrated_database, PROPOSED)

    with pytest.raises(Exception) as refusal:
        with migrated_database.begin() as connection:
            connection.execute(
                text(
                    "UPDATE identity_link_proposals SET granted_access_id = :access "
                    "WHERE id = :id"
                ),
                {"access": access_id, "id": proposal_id},
            )
    assert "a_confirmation_is_a_link" in str(refusal.value)


@pytest.mark.parametrize("batch", [1, 2, 3, 500])
def test_c04_considers_every_member_whatever_the_keyset_batch(
    migrated_database, batch, sheet_world
):
    """The scan is bounded per statement, never bounded in total.

    `MEMBERSHIP_SCAN_BATCH` replaced `GUILD_POPULATION_BOUND = 5000`, which made a
    guild larger than an invented policy number a **refusal**. This is the
    assertion that the replacement decides nothing: three members are scanned in
    pages of one, two, three and five hundred, and the resolution, the candidate
    set and the totals are byte-identical every time. A batch that dropped the
    tail would show up as `Bea` resolving to one twin instead of staying
    ambiguous — which is the direction that failure would go.
    """
    with migrated_database.begin() as connection:
        service = IdentityEvidenceRunService(
            sources=IdentityEvidenceSourceRepository(connection),
            proposals=IdentityProposalRepository(connection),
            guild_id=TEST_GUILD_ID,
            scan_batch=batch,
        )
        outcome = service.run(
            sheet_character_rows=[
                SheetCharacterRow(row_number=3, player_name="Ada"),
                SheetCharacterRow(row_number=4, player_name="Bea"),
            ],
            sheet_players=[
                SheetPlayer("Ada", "ada.one", False),
                SheetPlayer("Bea", "shared.name", True),
            ],
            sheet_tab=CHARACTER_TAB,
            source_label="probe",
            profile_version="v",
            correlation_id=uuid4(),
            now=utcnow(),
        )
    resolutions = tuple(
        (row["resolution"], row["proposed_subject"])
        for row in rows(
            migrated_database,
            "SELECT resolution, proposed_subject FROM identity_link_proposals "
            "WHERE run_id = :run ORDER BY sheet_player_name",
            run=outcome.run_id,
        )
    )
    # Stated as the same expected value for **every** batch rather than as "the
    # batches agreed with each other", so a batch that was wrong the same way
    # twice could not pass.
    totals = outcome.totals
    assert (totals.proposed, totals.ambiguous, totals.unresolved) == (1, 1, 0)
    assert (outcome.proposals_written, outcome.candidates_written) == (2, 3)
    assert resolutions == ((PROPOSED, str(ADA_SUBJECT)), (AMBIGUOUS, None))


def test_a_source_row_with_no_stable_character_mapping_refuses_the_whole_run(
    monkeypatch, migrated_database, settings
):
    """A row no bucket can hold is a refusal, not a silently narrower report.

    `identity_link_proposals.character_id` is `NOT NULL` and foreign-keyed, so a
    `Characters` row the Phase 2 import never mapped cannot be recorded in any
    bucket. Counting it into `source_characters` would make §7.4's balance a lie;
    dropping it would make the report quietly narrower than the Sheet. The run
    refuses, names the count, and writes nothing.
    """
    with migrated_database.begin() as connection:
        mapped = make_character(connection, display_name="Mapped")
        map_sheet_row(connection, character_id=mapped, row_index=3)
        seed_discord_member(connection, subject=ADA_SUBJECT, username="ada.one")

    exit_code, _probe = run_command(
        monkeypatch,
        migrated_database,
        settings,
        characters=character_values([("Mapped", "Ada"), ("Unmapped", "Bea")]),
        players=player_values([("Ada", "ada.one", False), ("Bea", "ada.one", False)]),
    )
    assert exit_code == command.EXIT_REFUSED
    assert scalar(migrated_database, "SELECT count(*) FROM identity_migration_runs") == 0
    assert scalar(migrated_database, "SELECT count(*) FROM identity_link_proposals") == 0


def test_the_service_refuses_unmapped_rows_before_writing_anything(migrated_database):
    """The same refusal at the service, so the type and the count are assertable."""
    with migrated_database.begin() as connection:
        service = IdentityEvidenceRunService(
            sources=IdentityEvidenceSourceRepository(connection),
            proposals=IdentityProposalRepository(connection),
            guild_id=TEST_GUILD_ID,
        )
        with pytest.raises(UnmappedSourceRows) as refusal:
            service.run(
                sheet_character_rows=[
                    SheetCharacterRow(row_number=3, player_name="Ada"),
                    SheetCharacterRow(row_number=4, player_name="Bea"),
                ],
                sheet_players=[SheetPlayer("Ada", "ada.one", False)],
                sheet_tab=CHARACTER_TAB,
                source_label="probe",
                profile_version="v",
                correlation_id=uuid4(),
                now=utcnow(),
            )
    assert refusal.value.count == 2
    assert scalar(migrated_database, "SELECT count(*) FROM identity_migration_runs") == 0


def test_the_database_refuses_an_unbalanced_run_with_the_application_bypassed(
    migrated_database,
):
    """TC-MIG-08's second half: the balance holds for every writer, not just ours.

    `RunTotals.balances()` is the legible control; this is the one that survives
    the application being removed.
    """
    with pytest.raises(Exception) as refusal:
        with migrated_database.begin() as connection:
            connection.execute(
                text(
                    "INSERT INTO identity_migration_runs (id, source_label, "
                    "profile_version, source_characters, source_players, "
                    "already_linked, proposed, ambiguous, unresolved, correlation_id) "
                    "VALUES (:id, 'forged', 'v', 9, 0, 0, 1, 0, 0, :correlation)"
                ),
                {"id": uuid4(), "correlation": uuid4()},
            )
    assert "buckets_balance_against_source" in str(refusal.value)


def test_an_ambiguity_wider_than_the_render_bound_persists_every_candidate_once(
    monkeypatch, migrated_database, settings
):
    """F4's regression, against the database.

    `SMALL_LIST_BOUND + 5` guild members share one username. The proposal is
    ambiguous, chooses nobody, persists every candidate exactly once, remains
    unconfirmable, and grants no access. Before the fix the resolver truncated the
    list to ten *before* the repository saw it, so five candidates were
    unrecoverable from the run and the evidence understated the ambiguity.
    """
    width = SMALL_LIST_BOUND + 5
    subjects = [str(700000000000004000 + index) for index in range(width)]
    with migrated_database.begin() as connection:
        wide = make_character(connection, display_name="Wide Vale")
        map_sheet_row(connection, character_id=wide, row_index=3)
        for subject in subjects:
            seed_discord_member(connection, subject=int(subject), username="shared.name")

    exit_code, _probe = run_command(
        monkeypatch,
        migrated_database,
        settings,
        characters=character_values([("Wide Vale", "Ada")]),
        players=player_values([("Ada", "shared.name", False)]),
    )
    assert exit_code == command.EXIT_OK

    proposal = rows(migrated_database, "SELECT * FROM identity_link_proposals")[0]
    assert proposal["resolution"] == AMBIGUOUS
    assert proposal["proposed_subject"] is None

    persisted = rows(
        migrated_database,
        "SELECT subject, count(*) AS occurrences FROM "
        "identity_link_proposal_candidates WHERE proposal_id = :id "
        "GROUP BY subject ORDER BY subject",
        id=proposal["id"],
    )
    assert len(persisted) == width
    assert {row["subject"] for row in persisted} == set(subjects)
    # Exactly once each: `uq_identity_link_proposal_candidates_subject` would
    # refuse a duplicate, and this asserts the writer did not need it to.
    assert {row["occurrences"] for row in persisted} == {1}

    # The complete durable set is queryable, which is what licenses the bounded
    # rendering (F4). `candidates_for` is the *view's* read and is bounded; this is
    # the review read and is not.
    with migrated_database.begin() as connection:
        repository = IdentityProposalRepository(connection)
        assert len(repository.candidate_subjects(proposal["id"])) == width
        bounded = repository.candidates_for([proposal["id"]], limit=SMALL_LIST_BOUND)
        listed, total = bounded[proposal["id"]]
        # `limit + 1` rows come back so the view can tell "exactly ten" from
        # "more than ten"; the count is the true number of rows.
        assert len(listed) == SMALL_LIST_BOUND + 1
        assert total == width

    assert access_rows(migrated_database) == 0


def test_a_run_that_fails_part_way_leaves_no_run_at_all(migrated_database):
    """Atomicity under injected failure: a whole run, or none of one.

    A run half-written would be worse than no run: its totals would describe
    proposals nobody wrote, and §7.4's balance would be true of the row and false of
    the database. The failure is injected at the third `add_proposal`, after the run
    row and two proposals are already in the transaction.
    """
    with migrated_database.begin() as connection:
        for offset in range(4):
            character_id = make_character(connection, display_name=f"Row {offset}")
            map_sheet_row(connection, character_id=character_id, row_index=3 + offset)
        seed_discord_member(connection, subject=ADA_SUBJECT, username="ada.one")

    class FailsOnTheThirdProposal(IdentityProposalRepository):
        def __init__(self, connection) -> None:
            super().__init__(connection)
            self.written = 0

        def add_proposal(self, **keywords):
            self.written += 1
            if self.written == 3:
                raise RuntimeError("injected proposal failure")
            return super().add_proposal(**keywords)

    with pytest.raises(RuntimeError, match="injected proposal failure"):
        with migrated_database.begin() as connection:
            service = IdentityEvidenceRunService(
                sources=IdentityEvidenceSourceRepository(connection),
                proposals=FailsOnTheThirdProposal(connection),
                guild_id=TEST_GUILD_ID,
            )
            service.run(
                sheet_character_rows=[
                    SheetCharacterRow(row_number=3 + offset, player_name="Ada")
                    for offset in range(4)
                ],
                sheet_players=[SheetPlayer("Ada", "ada.one", False)],
                sheet_tab=CHARACTER_TAB,
                source_label="probe",
                profile_version="v",
                correlation_id=uuid4(),
                now=utcnow(),
            )

    assert scalar(migrated_database, "SELECT count(*) FROM identity_migration_runs") == 0
    assert scalar(migrated_database, "SELECT count(*) FROM identity_link_proposals") == 0


def test_undecided_proposals_persist_across_runs(
    monkeypatch, migrated_database, settings, sheet_world
):
    """§7.6. They are not deleted at the end of a run and not retried away.

    A second run over unchanged sources produces its own run row and its own
    proposals — keyed `(run_id, character_id)` — and leaves the first run's rows
    exactly where they were, with their evidence and their resolutions.
    """
    for _ in range(2):
        run_command(
            monkeypatch,
            migrated_database,
            settings,
            characters=sheet_world["characters"],
            players=sheet_world["players"],
        )

    runs = rows(migrated_database, "SELECT id FROM identity_migration_runs")
    assert len(runs) == 2
    per_run = rows(
        migrated_database,
        "SELECT run_id, count(*) AS proposals FROM identity_link_proposals "
        "GROUP BY run_id",
    )
    assert sorted(row["proposals"] for row in per_run) == [4, 4]
    # The resolutions are identical run to run: one resolver, no state carried.
    shapes = rows(
        migrated_database,
        "SELECT run_id, resolution, count(*) AS n FROM identity_link_proposals "
        "GROUP BY run_id, resolution ORDER BY run_id, resolution",
    )
    by_run: dict[UUID, dict[str, int]] = {}
    for row in shapes:
        by_run.setdefault(row["run_id"], {})[row["resolution"]] = row["n"]
    assert len(by_run) == 2
    assert len({tuple(sorted(counts.items())) for counts in by_run.values()}) == 1


def test_a_rerun_after_a_confirmed_link_counts_it_and_proposes_nothing_for_it(
    monkeypatch, migrated_database, settings, council, proposed_run, sheet_world
):
    """§7.5's idempotency, as an operator experiences it.

    A confirmation creates the link, so the next run finds the (character,
    account) pair already linked, counts it `already_linked` and proposes nothing
    for it. No run has to know what an earlier one decided; the database is asked.
    """
    confirm(
        migrated_database,
        settings,
        proposal_id=proposed_run["proposal_id"],
        account_id=proposed_run["council_account_id"],
        expected_version=proposed_run["character_version"],
    )
    assert access_rows(migrated_database) == 1

    run_command(
        monkeypatch,
        migrated_database,
        settings,
        characters=sheet_world["characters"],
        players=sheet_world["players"],
    )
    run = rows(
        migrated_database,
        "SELECT * FROM identity_migration_runs ORDER BY produced_at DESC, id DESC "
        "LIMIT 1",
    )[0]
    assert run["already_linked"] == 1
    assert run["proposed"] == 0
    assert (
        run["already_linked"] + run["proposed"] + run["ambiguous"] + run["unresolved"]
        == run["source_characters"]
    )
    assert (
        scalar(
            migrated_database,
            "SELECT count(*) FROM identity_link_proposals WHERE character_id = :id "
            "AND run_id = :run",
            id=sheet_world["alia"],
            run=run["id"],
        )
        == 0
    )


# ===========================================================================
# TC-MIG-17 — duplicate player names fail closed
# ===========================================================================


DUPLICATE_CASES = {
    # Exactly equal, and case-folded-equal. Both are one key under
    # `DisplayName.identity_key`, which is the comparison the resolver uses, and
    # neither may be settled by which row came second.
    "exact": ("Ada", "Ada"),
    "case_folded": ("Ada", "ADA"),
}


@pytest.mark.parametrize("case", sorted(DUPLICATE_CASES))
@pytest.mark.parametrize("reversed_order", [False, True])
def test_duplicate_player_names_refuse_the_run_whatever_the_row_order(
    monkeypatch, migrated_database, settings, case, reversed_order
):
    """TC-MIG-17, the whole of it, through the real command.

    The reproduced defect: the player index was a dict comprehension keyed by the
    normalized player name, so `Ada` and `ADA` collided and **the later row**
    decided which Discord identity the character's proposal would name. Sheet
    order is not a tie-break.

    Four cases — exact and case-folded duplicates, each in both row orders — and
    all four refuse identically. The two orders are the point: under the defect
    they produced *different* confirmable identities from the same source data,
    and that difference is what an assertion has to be able to see.
    """
    first, second = DUPLICATE_CASES[case]
    with migrated_database.begin() as connection:
        alia = make_character(connection, display_name="Alia Storm")
        map_sheet_row(connection, character_id=alia, row_index=3)
        seed_discord_member(connection, subject=ADA_SUBJECT, username="ada.one")
        seed_discord_member(connection, subject=CYD_SUBJECT, username="cyd.two")

    players = [(first, "ada.one", False), (second, "cyd.two", False)]
    if reversed_order:
        players.reverse()

    exit_code, _probe = run_command(
        monkeypatch,
        migrated_database,
        settings,
        characters=character_values([("Alia Storm", first)]),
        players=player_values(players),
    )
    assert exit_code == command.EXIT_REFUSED

    # No confirmable proposal, because no proposal and no run at all: the refusal
    # happens before the run row is written, so the command-level transaction
    # leaves nothing partial behind.
    assert scalar(migrated_database, "SELECT count(*) FROM identity_migration_runs") == 0
    assert scalar(migrated_database, "SELECT count(*) FROM identity_link_proposals") == 0
    assert (
        scalar(
            migrated_database,
            "SELECT count(*) FROM identity_link_proposal_candidates",
        )
        == 0
    )
    assert access_rows(migrated_database) == 0
    assert audit_actions(migrated_database) == []


def test_the_duplicate_refusal_names_no_player_and_no_discord_identity(
    monkeypatch, migrated_database, settings, capsys
):
    """The operator-facing surface of TC-MIG-17: counts, and nothing personal.

    A terminal, a shell history and a CI log are the wrong place for the player
    tab's contents, and the remedy — resolve the duplicate in the source
    spreadsheet — does not need them.
    """
    with migrated_database.begin() as connection:
        alia = make_character(connection, display_name="Alia Storm")
        map_sheet_row(connection, character_id=alia, row_index=3)
        seed_discord_member(connection, subject=ADA_SUBJECT, username="ada.one")

    run_command(
        monkeypatch,
        migrated_database,
        settings,
        characters=character_values([("Alia Storm", "Ada")]),
        players=player_values(
            [("Ada", "ada.one", False), ("ADA", "shared.name", False)]
        ),
    )
    captured = capsys.readouterr()
    printed = captured.out + captured.err
    assert "Run refused" in printed
    assert "1 player name(s) appear on more than one player-tab row" in printed
    assert "Nothing was written." in printed
    for secret in ("Ada", "ADA", "ada.one", "shared.name", "Alia Storm", str(ADA_SUBJECT)):
        assert secret not in printed, secret


def test_a_duplicate_is_not_reported_as_an_ordinary_ambiguity(
    monkeypatch, migrated_database, settings
):
    """The refusal is not a bucket, so no control total can absorb it.

    The alternative design — persisting each affected character as non-confirmable
    evidence — would let a source-integrity defect be counted as an ordinary
    `ambiguous` row inside a balance computed over a player set the run had
    already decided was self-consistent. Nothing is written, so there is no total
    to hide it in.
    """
    with migrated_database.begin() as connection:
        alia = make_character(connection, display_name="Alia Storm")
        brand = make_character(connection, display_name="Brand Vale")
        map_sheet_row(connection, character_id=alia, row_index=3)
        map_sheet_row(connection, character_id=brand, row_index=4)
        seed_discord_member(connection, subject=ADA_SUBJECT, username="ada.one")
        seed_discord_member(connection, subject=CYD_SUBJECT, username="cyd.two")

    exit_code, _probe = run_command(
        monkeypatch,
        migrated_database,
        settings,
        characters=character_values([("Alia Storm", "Ada"), ("Brand Vale", "Cyd")]),
        players=player_values(
            [
                ("Ada", "ada.one", False),
                ("ADA", "cyd.two", False),
                ("Cyd", "cyd.two", False),
            ]
        ),
    )
    assert exit_code == command.EXIT_REFUSED
    # Not even the character whose player name is unambiguous gets a proposal:
    # the run is the unit that refuses, because the player tab is the unit whose
    # integrity failed.
    assert scalar(migrated_database, "SELECT count(*) FROM identity_migration_runs") == 0
    assert scalar(migrated_database, "SELECT count(*) FROM identity_link_proposals") == 0


# ===========================================================================
# Stage 2 — R-28 shows four states, and no apply state
# ===========================================================================


async def test_r28_renders_outstanding_confirmed_and_rejected_states(
    client, migrated_database, settings, council, proposed_run
):
    """The page a Council member reads before and after a confirmation.

    Before, the confirmable row is outstanding and carries a confirm control that
    states what it will create. After, it is confirmed **and linked** — one state,
    not two — and the control is gone because the proposal cannot be decided
    again.
    """
    caller = council["C"]
    before = await client.get(
        "/v1/council/identity-migration", cookies=caller.cookies(settings)
    )
    assert before.status_code == 200
    assert 'data-status="outstanding"' in before.text
    assert 'data-notice="confirmation-creates-the-link"' in before.text
    assert '<dd data-total="confirmed">0</dd>' in before.text
    # The confirm form states the character, the identity, the access kind and
    # the version before anything is created (VM-10).
    assert f'data-subject="{ADA_SUBJECT}"' in before.text
    assert f'data-access-kind="{CONFIRMED_ACCESS_KIND}"' in before.text
    assert f'data-character-id="{proposed_run["character_id"]}"' in before.text
    assert 'name="version"' in before.text
    # No apply state anywhere on the page: there is no such state.
    for absent in ("data-run-applied", "confirmed-not-applied", "apply-totals"):
        assert absent not in before.text, absent

    confirm(
        migrated_database,
        settings,
        proposal_id=proposed_run["proposal_id"],
        account_id=caller.account_id,
        expected_version=proposed_run["character_version"],
    )

    after = await client.get(
        "/v1/council/identity-migration", cookies=caller.cookies(settings)
    )
    assert after.status_code == 200
    assert 'data-status="confirmed-and-active"' in after.text
    assert 'data-stage="decided"' in after.text
    assert '<dd data-total="confirmed">1</dd>' in after.text
    # The decided row's controls are gone; the three still-outstanding rows keep
    # their own reject control, one form per proposal, and no bulk control exists.
    assert after.text.count("/confirm") == 0
    assert after.text.count("/reject") == 3
    assert "confirm-all" not in after.text
    assert 'data-status="outstanding"' in after.text


async def test_r28_totals_balance_and_report_no_apply_count(
    client, settings, council, proposed_run
):
    """§7.4's two equations, shown to the person doing the confirming.

    `balances()` is arithmetic the page can be asked about rather than a claim in
    prose, and there is no third equation and no apply total beside it.
    """
    response = await client.get(
        "/v1/council/identity-migration", cookies=council["C"].cookies(settings)
    )
    assert response.status_code == 200
    assert 'data-balances="true"' in response.text
    assert '<dd data-total="source_characters">4</dd>' in response.text
    assert '<dd data-total="outstanding">4</dd>' in response.text
    for absent in ('data-total="granted"', 'data-total="adopted"'):
        assert absent not in response.text, absent


async def test_r28_never_calls_a_revoked_confirmation_active(
    client, migrated_database, settings, council, proposed_run
):
    """The independent review's finding 1, reproduced and then closed.

    `C-04 → R-29 confirm → R-26 revoke → R-28`. Before the fix this page read the
    proposal's historical `confirmed` resolution and rendered it
    `confirmed-and-active`, saying the link *"is active now"* about an access row
    Council had already revoked — and counted it in the active-confirmed total
    that migration contract §7.4 defines as active links.

    The current state is read from the **exact** `granted_access_id`, so what the
    page says is a fact about the row that confirmation created. The historical
    decision is untouched by all of it: `resolution` is still `confirmed`, the
    decider, the reason and the access id it named are all still there, and both
    audit events the confirmation wrote are still in the log. A revocation is a
    compensating action (§7.5), not an erasure.
    """
    caller = council["C"]
    confirm(
        migrated_database,
        settings,
        proposal_id=proposed_run["proposal_id"],
        account_id=caller.account_id,
        expected_version=proposed_run["character_version"],
        reason="Council confirmed the Sheet evidence",
    )
    decided = rows(
        migrated_database,
        "SELECT * FROM identity_link_proposals WHERE id = :id",
        id=proposed_run["proposal_id"],
    )[0]
    access_id = decided["granted_access_id"]

    # Still true while the link is active: the retained half of this evidence.
    active_page = await client.get(
        "/v1/council/identity-migration", cookies=caller.cookies(settings)
    )
    assert 'data-status="confirmed-and-active"' in active_page.text
    assert '<dd data-total="confirmed">1</dd>' in active_page.text
    assert '<dd data-total="confirmed_revoked">0</dd>' in active_page.text

    revoke(
        migrated_database,
        settings,
        character_id=proposed_run["character_id"],
        access_id=access_id,
        account_id=caller.account_id,
    )

    page = await client.get(
        "/v1/council/identity-migration", cookies=caller.cookies(settings)
    )
    assert page.status_code == 200
    # 1. The page does not label it active, and does not say it is active now.
    assert 'data-status="confirmed-and-active"' not in page.text
    assert "is active now" not in page.text
    assert 'data-status="confirmed-and-revoked"' in page.text
    assert 'data-link-state="revoked"' in page.text
    # 2. The active-confirmed total excludes it, and the balance still closes
    #    over every proposal — the revoked confirmation is counted, not dropped.
    assert '<dd data-total="confirmed">0</dd>' in page.text
    assert '<dd data-total="confirmed_revoked">1</dd>' in page.text
    assert '<dd data-total="outstanding">3</dd>' in page.text
    assert 'data-balances="true"' in page.text
    # 3. The decision itself is intact, and is not rewritten to `rejected` and
    #    not returned to `proposed`.
    after = rows(
        migrated_database,
        "SELECT * FROM identity_link_proposals WHERE id = :id",
        id=proposed_run["proposal_id"],
    )[0]
    assert after["resolution"] == "confirmed"
    assert after["decided_by_account_id"] == caller.account_id
    assert after["decision_reason"] == "Council confirmed the Sheet evidence"
    assert after["decided_at"] == decided["decided_at"]
    assert after["granted_access_id"] == access_id
    # And the row it named is still there, revoked rather than deleted, keeping
    # the reason it was *granted* for.
    link = rows(
        migrated_database, "SELECT * FROM character_access WHERE id = :id", id=access_id
    )[0]
    assert link["active"] is False
    assert link["revoked_at"] is not None
    assert link["reason"] == "Council confirmed the Sheet evidence"
    # 4. Both audit events the confirmation wrote are still in the log, beside
    #    the revocation's own.
    assert audit_actions(migrated_database).count("identity_migration.confirmed") == 1
    assert audit_actions(migrated_database).count("character_access.granted") == 1
    assert audit_actions(migrated_database).count("character_access.revoked") == 1
    # 5. The proposal cannot be decided again: it is decided, and its controls
    #    are gone. A revocation does not re-open a decision.
    assert page.text.count("/confirm") == 0
    assert page.text.count("/reject") == 3


async def test_another_active_link_cannot_make_a_revoked_confirmation_look_active(
    client, migrated_database, settings, council, proposed_run
):
    """Activation is read from the exact grant, never from the character.

    The obvious wrong implementation of the fix above is "does this character
    have an active link?", which is one join away from the right one and passes
    every case where the revoked confirmation is the only link. Here the same
    character carries a second, unrelated active link — a different account,
    granted through R-25 and never touched by this run — and the revoked
    confirmation must still read revoked.

    The account-side version of the same mistake is covered too: the second link
    is on the character the proposal names, which is the join a `character_id`
    lookup would follow.
    """
    caller = council["C"]
    confirm(
        migrated_database,
        settings,
        proposal_id=proposed_run["proposal_id"],
        account_id=caller.account_id,
        expected_version=proposed_run["character_version"],
    )
    access_id = scalar(
        migrated_database,
        "SELECT granted_access_id FROM identity_link_proposals WHERE id = :id",
        id=proposed_run["proposal_id"],
    )
    revoke(
        migrated_database,
        settings,
        character_id=proposed_run["character_id"],
        access_id=access_id,
        account_id=caller.account_id,
    )

    other_subject = 700000000000003099
    with migrated_database.begin() as connection:
        other = make_account(connection, label="other")
        seed_discord_member(connection, subject=other_subject, username="other.one")
        link_discord(connection, other, other_subject)
        grant_link(
            connection,
            character_id=proposed_run["character_id"],
            account_id=other,
            granted_by=caller.account_id,
            access_kind="co_owner",
        )

    page = await client.get(
        "/v1/council/identity-migration", cookies=caller.cookies(settings)
    )
    assert page.status_code == 200
    assert 'data-status="confirmed-and-revoked"' in page.text
    assert 'data-status="confirmed-and-active"' not in page.text
    assert "is active now" not in page.text
    assert '<dd data-total="confirmed">0</dd>' in page.text
    assert '<dd data-total="confirmed_revoked">1</dd>' in page.text
    assert 'data-balances="true"' in page.text


async def test_a_rejected_proposal_carries_no_link_state_at_all(
    client, migrated_database, settings, council, proposed_run
):
    """"No link was ever created" and "the link was revoked" are not one state.

    A rejection creates nothing, so it has no access row whose state could be
    reported, and the attribute that reports one is absent rather than present
    and false. Without this, the honest rendering of a revoked confirmation could
    be reached by rendering *every* non-active row the same way, which would tell
    a Council member that a rejection had once been a link.
    """
    caller = council["C"]
    ambiguous_id = proposal_id_for(migrated_database, AMBIGUOUS)
    with migrated_database.begin() as connection:
        migration_service(connection, settings).reject(
            context=council_context(caller.account_id),
            proposal_id=ambiguous_id,
            reason="No single identity in the evidence",
            correlation_id=uuid4(),
            now=utcnow(),
        )

    page = await client.get(
        "/v1/council/identity-migration", cookies=caller.cookies(settings)
    )
    assert page.status_code == 200
    assert 'data-status="rejected"' in page.text
    assert "data-link-state" not in page.text
    assert '<dd data-total="rejected">1</dd>' in page.text
    assert '<dd data-total="confirmed">0</dd>' in page.text
    assert '<dd data-total="confirmed_revoked">0</dd>' in page.text
    assert 'data-balances="true"' in page.text


# ===========================================================================
# Stage 3 — R-29 creates the link; R-30 creates nothing
# ===========================================================================


def test_r29_creates_the_link_its_audits_and_the_decision_atomically(
    migrated_database, settings, council, proposed_run
):
    """TC-MIG-11. One confirmation, one link, one decision, two audit events.

    The link is written through `CharacterAccessService` — R-25's own service —
    under the confirming member's live context, and the proposal names the access
    row it produced. All of it in one transaction.
    """
    correlation_id = confirm(
        migrated_database,
        settings,
        proposal_id=proposed_run["proposal_id"],
        account_id=council["C"].account_id,
        expected_version=proposed_run["character_version"],
        reason="Council confirmed the Sheet evidence",
    )

    decided = rows(
        migrated_database,
        "SELECT * FROM identity_link_proposals WHERE id = :id",
        id=proposed_run["proposal_id"],
    )[0]
    assert decided["resolution"] == "confirmed"
    assert decided["decided_by_account_id"] == council["C"].account_id
    assert decided["decision_reason"] == "Council confirmed the Sheet evidence"
    assert decided["decided_at"] is not None
    assert decided["granted_access_id"] is not None

    link = rows(
        migrated_database,
        "SELECT * FROM character_access WHERE id = :id",
        id=decided["granted_access_id"],
    )[0]
    assert link["character_id"] == proposed_run["character_id"]
    assert link["platform_account_id"] == proposed_run["account_id"]
    assert link["access_kind"] == CONFIRMED_ACCESS_KIND
    assert link["active"] is True
    # Attributed to the confirming Council member's live context, not to an
    # operator and not to the account being linked.
    assert link["granted_by_account_id"] == council["C"].account_id
    assert link["reason"] == "Council confirmed the Sheet evidence"
    # Exactly one link, and exactly one row moved.
    assert access_rows(migrated_database) == 1
    assert (
        scalar(
            migrated_database,
            "SELECT count(*) FROM identity_link_proposals WHERE resolution = 'confirmed'",
        )
        == 1
    )

    # The character's optimistic version was taken, once.
    with migrated_database.begin() as connection:
        assert character_version(connection, proposed_run["character_id"]) == (
            proposed_run["character_version"] + 1
        )

    events = rows(
        migrated_database,
        "SELECT action, actor_platform_account_id, correlation_id, payload, source "
        "FROM audit_events ORDER BY action",
    )
    assert [row["action"] for row in events] == [
        "character_access.granted",
        "identity_migration.confirmed",
    ]
    for event in events:
        assert event["actor_platform_account_id"] == council["C"].account_id
        assert event["correlation_id"] == correlation_id
        assert event["source"] == "web"
    confirmed = events[1]
    assert confirmed["payload"]["granted_access_id"] == str(decided["granted_access_id"])
    assert confirmed["payload"]["access_kind"] == CONFIRMED_ACCESS_KIND
    assert confirmed["payload"]["reason"] == "Council confirmed the Sheet evidence"


def test_r29_grants_through_the_one_shared_service(migrated_database, settings):
    """R-29 is not a second grant implementation, structurally.

    `IdentityMigrationService` holds a `CharacterAccessService`, and request
    composition hands it the **same object** it hands R-25 rather than a second
    construction of the class — so the one-active-owner invariant, the reason
    requirement, the optimistic version and the audit event are the ones already
    under test.
    """
    from adapters.web.composition import WebComposition  # noqa: F401 - documented below

    with migrated_database.begin() as connection:
        service = migration_service(connection, settings)
        held = {
            name: getattr(service, name, None)
            for name in IdentityMigrationService.__slots__
        }
    assert isinstance(held["_access_service"], CharacterAccessService)

    # And the composition passes one object to both, which is the property that
    # stops them drifting: asserted over the source rather than by building a
    # request, because the claim is about wiring.
    import ast
    import inspect

    source = inspect.getsource(WebComposition.services)
    tree = ast.parse(source.lstrip())
    assigned = {
        node.func.id if isinstance(node.func, ast.Name) else ""
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
    }
    assert "CharacterAccessService" in assigned
    # Constructed once in that method, so `character_access=` and
    # `access_service=` cannot be two different objects.
    assert (
        sum(
            1
            for node in ast.walk(tree)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "CharacterAccessService"
        )
        == 1
    )


def test_r30_rejects_an_outstanding_proposal_and_creates_no_link(
    migrated_database, settings, council, monkeypatch, sheet_world
):
    """A rejection is durable, audited, and creates nothing.

    Any outstanding resolution may be rejected, including `ambiguous` and
    `unresolved`: rejecting one is how a Council member says *"there is nothing
    here"* and stops it standing outstanding for ever (§7.6).
    """
    run_command(
        monkeypatch,
        migrated_database,
        settings,
        characters=sheet_world["characters"],
        players=sheet_world["players"],
    )
    proposal_id = proposal_id_for(migrated_database, AMBIGUOUS)
    with migrated_database.begin() as connection:
        migration_service(connection, settings).reject(
            context=council_context(council["C"].account_id),
            proposal_id=proposal_id,
            reason="two people share that name; neither is this character's",
            correlation_id=uuid4(),
            now=utcnow(),
        )

    rejected = rows(
        migrated_database,
        "SELECT * FROM identity_link_proposals WHERE id = :id",
        id=proposal_id,
    )[0]
    assert rejected["resolution"] == "rejected"
    assert rejected["decided_by_account_id"] == council["C"].account_id
    assert rejected["granted_access_id"] is None
    assert access_rows(migrated_database) == 0
    assert audit_actions(migrated_database) == ["identity_migration.rejected"]


def test_a_superseded_run_cannot_create_authorization(
    proposed_run, migrated_database, settings, monkeypatch, sheet_world
):
    """A stale R-28 page cannot confirm evidence superseded by a newer C-04 run.

    Older evidence remains durable for review, but durability is not authority.
    Once C-04 has recorded a newer view of the source, only that latest run may
    create or reject decisions; otherwise a corrected rerun would leave the
    earlier, potentially wrong subject one stale browser submission away from a
    real ``character_access`` row.
    """
    old_proposal = proposed_run["proposal_id"]
    old_run = proposed_run["run_id"]
    run_command(
        monkeypatch,
        migrated_database,
        settings,
        characters=sheet_world["characters"],
        players=sheet_world["players"],
    )
    assert latest_run_id(migrated_database) != old_run

    with pytest.raises(NotConfirmable):
        confirm(
            migrated_database,
            settings,
            proposal_id=old_proposal,
            account_id=proposed_run["council_account_id"],
            expected_version=proposed_run["character_version"],
        )

    assert access_rows(migrated_database) == 0
    assert audit_actions(migrated_database) == []


@pytest.mark.parametrize("resolution", [AMBIGUOUS, UNRESOLVED])
def test_an_undecidable_proposal_cannot_be_confirmed_by_the_service(
    migrated_database, settings, council, monkeypatch, sheet_world, resolution
):
    """TC-MIG-10, at the service. `proposed_subject` is null on both."""
    run_command(
        monkeypatch,
        migrated_database,
        settings,
        characters=sheet_world["characters"],
        players=sheet_world["players"],
    )
    proposal_id = proposal_id_for(migrated_database, resolution)
    with pytest.raises(NotConfirmable):
        with migrated_database.begin() as connection:
            migration_service(connection, settings).confirm(
                context=council_context(council["C"].account_id),
                proposal_id=proposal_id,
                reason="confirmed anyway",
                expected_version=0,
                correlation_id=uuid4(),
                now=utcnow(),
            )
    assert access_rows(migrated_database) == 0
    assert audit_actions(migrated_database) == []


@pytest.mark.parametrize("resolution", [AMBIGUOUS, UNRESOLVED])
async def test_an_undecidable_proposal_grants_no_access_even_when_submitted(
    client, migrated_database, settings, council, sheet_world, monkeypatch, resolution
):
    """TC-MIG-10, by direct HTTP: the browser submits anyway, and is refused.

    The request is built and sent without ever rendering R-28, so the refusal
    cannot be an artefact of the confirm control having been hidden — route
    contract §2.2.
    """
    run_command(
        monkeypatch,
        migrated_database,
        settings,
        characters=sheet_world["characters"],
        players=sheet_world["players"],
    )
    proposal_id = proposal_id_for(migrated_database, resolution)
    caller = council["C"]

    response = await client.post(
        f"/v1/council/identity-migration/{proposal_id}/confirm",
        cookies=caller.cookies(settings),
        headers={
            "Origin": PUBLIC_ORIGIN,
            "Content-Type": "application/x-www-form-urlencoded",
        },
        content=(
            f"csrf_token={csrf_token_for(settings, caller)}"
            "&version=0&reason=submitted+anyway"
        ),
    )
    assert response.status_code == 409
    assert access_rows(migrated_database) == 0
    assert (
        scalar(
            migrated_database,
            "SELECT resolution FROM identity_link_proposals WHERE id = :id",
            id=proposal_id,
        )
        == resolution
    )
    assert audit_actions(migrated_database) == []


async def test_a_confirmation_by_http_creates_the_link(
    client, migrated_database, settings, council, proposed_run
):
    """R-29's success cell, end to end through the real route.

    `303` back to R-28, one link, one decision naming it, two audit events. The
    request carries the proposal id, the reason and the version, and nothing else
    it needs.
    """
    caller = council["C"]
    response = await client.post(
        f"/v1/council/identity-migration/{proposed_run['proposal_id']}/confirm",
        cookies=caller.cookies(settings),
        headers={
            "Origin": PUBLIC_ORIGIN,
            "Content-Type": "application/x-www-form-urlencoded",
        },
        content=(
            f"csrf_token={csrf_token_for(settings, caller)}"
            f"&version={proposed_run['character_version']}"
            "&reason=Council+confirmed+the+Sheet+evidence"
        ),
        follow_redirects=False,
    )
    assert response.status_code == 303
    assert response.headers["location"] == "/v1/council/identity-migration"
    assert access_rows(migrated_database) == 1
    assert audit_actions(migrated_database) == [
        "character_access.granted",
        "identity_migration.confirmed",
    ]
    decided = rows(
        migrated_database,
        "SELECT resolution, granted_access_id FROM identity_link_proposals "
        "WHERE id = :id",
        id=proposed_run["proposal_id"],
    )[0]
    assert decided["resolution"] == "confirmed"
    assert decided["granted_access_id"] is not None


async def test_a_confirmation_cannot_substitute_any_authorization_bearing_value(
    client, migrated_database, settings, council, proposed_run
):
    """Extra body fields are read by nothing, and change nothing.

    A subject, an account, an actor, an access kind and an authority are all
    submitted. Every one of them is resolved server-side, and none of them has a
    parameter to arrive through — so the link that results is the one the
    proposal named, granted by the caller's own account, with the service's
    access kind.
    """
    caller = council["C"]
    other = council["M"]
    response = await client.post(
        f"/v1/council/identity-migration/{proposed_run['proposal_id']}/confirm",
        cookies=caller.cookies(settings),
        headers={
            "Origin": PUBLIC_ORIGIN,
            "Content-Type": "application/x-www-form-urlencoded",
        },
        content=(
            f"csrf_token={csrf_token_for(settings, caller)}"
            f"&version={proposed_run['character_version']}"
            "&reason=substitution+attempt"
            f"&subject={CYD_SUBJECT}"
            f"&platform_account_id={other.account_id}"
            f"&account_id={other.account_id}"
            f"&granted_by_account_id={other.account_id}"
            f"&actor={other.account_id}"
            "&access_kind=owner"
            "&capability=platform_administrator"
        ),
        follow_redirects=False,
    )
    assert response.status_code == 303
    link = rows(migrated_database, "SELECT * FROM character_access")[0]
    assert link["platform_account_id"] == proposed_run["account_id"]
    assert link["granted_by_account_id"] == caller.account_id
    assert link["access_kind"] == CONFIRMED_ACCESS_KIND
    assert link["character_id"] == proposed_run["character_id"]


def test_a_second_confirmation_of_one_proposal_changes_nothing_twice(
    migrated_database, settings, council, proposed_run
):
    """Repeated submissions produce one durable effect.

    A decided proposal is refused on its **state**, before the version is even
    consulted — so a double submission is refused for the right reason rather
    than incidentally by the optimistic version having moved. Both the stale
    resubmission and one carrying the *current* version are refused identically,
    which is what shows the version is not what is doing the work here; and a
    rejection of the decided row is refused by `decide()`'s conditional update.
    """
    confirm(
        migrated_database,
        settings,
        proposal_id=proposed_run["proposal_id"],
        account_id=council["C"].account_id,
        expected_version=proposed_run["character_version"],
    )

    with migrated_database.begin() as connection:
        current = character_version(connection, proposed_run["character_id"])
    for version in (proposed_run["character_version"], current):
        with pytest.raises(NotConfirmable):
            confirm(
                migrated_database,
                settings,
                proposal_id=proposed_run["proposal_id"],
                account_id=council["C"].account_id,
                expected_version=version,
            )

    # A rejection of the decided row is refused too.
    with pytest.raises(NotConfirmable):
        with migrated_database.begin() as connection:
            migration_service(connection, settings).reject(
                context=council_context(council["C"].account_id),
                proposal_id=proposed_run["proposal_id"],
                reason="second attempt",
                correlation_id=uuid4(),
                now=utcnow(),
            )

    assert access_rows(migrated_database) == 1
    assert audit_actions(migrated_database) == [
        "character_access.granted",
        "identity_migration.confirmed",
    ]


def test_two_concurrent_confirmations_produce_one_durable_effect(
    migrated_database, settings, council, proposed_run
):
    """TC-MIG-11's concurrency half, with two real connections.

    Both threads read an outstanding proposal and an unbumped character, and both
    attempt the confirmation. Exactly one commits: the conditional version bump,
    `uq_character_access_one_active_link_account` and `decide()`'s conditional
    update are three independent reasons the loser cannot also succeed, and the
    assertion is on the durable result rather than on which of them fired.
    """
    url = str(migrated_database.url)
    started = threading.Barrier(2)
    outcomes: list[str] = []
    lock = threading.Lock()

    def work():
        engine = create_engine(url)
        try:
            started.wait(timeout=10)
            confirm(
                engine,
                settings,
                proposal_id=proposed_run["proposal_id"],
                account_id=council["C"].account_id,
                expected_version=proposed_run["character_version"],
            )
            result = "committed"
        except Exception as error:  # noqa: BLE001 - the class is the assertion below
            result = type(error).__name__
        finally:
            engine.dispose()
        with lock:
            outcomes.append(result)

    threads = [threading.Thread(target=work) for _ in range(2)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=30)

    assert outcomes.count("committed") == 1, outcomes
    assert access_rows(migrated_database) == 1
    assert audit_actions(migrated_database) == [
        "character_access.granted",
        "identity_migration.confirmed",
    ]
    assert (
        scalar(
            migrated_database,
            "SELECT count(*) FROM identity_link_proposals WHERE resolution = 'confirmed'",
        )
        == 1
    )


# ===========================================================================
# TC-MIG-13 — every injected failure leaves nothing behind
# ===========================================================================


class _FailingAudit(WebAuditRepository):
    """`record()` raises on the nth call. Everything else is production code."""

    def __init__(self, connection, *, fail_on: int) -> None:
        super().__init__(connection)
        self._fail_on = fail_on
        self.calls = 0

    def record(self, event):
        self.calls += 1
        if self.calls == self._fail_on:
            raise RuntimeError("injected audit failure")
        return super().record(event)


@pytest.mark.parametrize(
    "fail_on, which",
    [(1, "the grant's audit event"), (2, "the confirmation's audit event")],
)
def test_an_injected_audit_failure_rolls_the_whole_confirmation_back(
    migrated_database, settings, council, proposed_run, fail_on, which
):
    """TC-MIG-13. Either audit event failing takes everything with it.

    Not because anything catches the failure — nothing does — but because the
    grant, the version bump, the decision and both events are in one transaction
    and the exception leaves it. `which` names the event for the report; the
    assertions are identical, which is the point.
    """
    with pytest.raises(RuntimeError, match="injected audit failure"):
        with migrated_database.begin() as connection:
            migration_service(
                connection,
                settings,
                audit=_FailingAudit(connection, fail_on=fail_on),
            ).confirm(
                context=council_context(council["C"].account_id),
                proposal_id=proposed_run["proposal_id"],
                reason=f"rolled back by {which}",
                expected_version=proposed_run["character_version"],
                correlation_id=uuid4(),
                now=utcnow(),
            )

    assert access_rows(migrated_database) == 0
    assert audit_actions(migrated_database) == []
    assert (
        scalar(
            migrated_database,
            "SELECT resolution FROM identity_link_proposals WHERE id = :id",
            id=proposed_run["proposal_id"],
        )
        == PROPOSED
    )
    with migrated_database.begin() as connection:
        assert (
            character_version(connection, proposed_run["character_id"])
            == proposed_run["character_version"]
        )


def test_an_injected_grant_failure_leaves_no_decision_and_no_version_bump(
    migrated_database, settings, council, proposed_run
):
    """TC-MIG-13's grant half. The decision never happens if the link cannot."""

    class RefusingGrant(CharacterAccessService):
        def grant(self, **keywords):
            raise RuntimeError("injected grant failure")

    with pytest.raises(RuntimeError, match="injected grant failure"):
        with migrated_database.begin() as connection:
            accounts = AccountRepository(connection)
            access = CharacterAccessRepository(connection)
            audit = WebAuditRepository(connection)
            migration_service(
                connection,
                settings,
                audit=audit,
                access_service=RefusingGrant(
                    access=access, accounts=accounts, audit=audit
                ),
            ).confirm(
                context=council_context(council["C"].account_id),
                proposal_id=proposed_run["proposal_id"],
                reason="never recorded",
                expected_version=proposed_run["character_version"],
                correlation_id=uuid4(),
                now=utcnow(),
            )

    assert access_rows(migrated_database) == 0
    assert audit_actions(migrated_database) == []
    assert (
        scalar(
            migrated_database,
            "SELECT decided_at FROM identity_link_proposals WHERE id = :id",
            id=proposed_run["proposal_id"],
        )
        is None
    )


def test_a_failed_proposal_transition_rolls_the_grant_back_with_it(
    migrated_database, settings, council, proposed_run
):
    """TC-MIG-13's transition half.

    `decide()` is conditional, so it can answer `False` after the grant has been
    written — somebody decided the row in between. The service raises rather than
    returning a success, and the grant it had already written goes with the
    transaction.
    """

    class LosesTheRace(IdentityProposalRepository):
        def decide(self, **keywords) -> bool:
            return False

    with pytest.raises(NotConfirmable):
        with migrated_database.begin() as connection:
            migration_service(
                connection, settings, proposals=LosesTheRace(connection)
            ).confirm(
                context=council_context(council["C"].account_id),
                proposal_id=proposed_run["proposal_id"],
                reason="lost the race",
                expected_version=proposed_run["character_version"],
                correlation_id=uuid4(),
                now=utcnow(),
            )

    assert access_rows(migrated_database) == 0
    assert audit_actions(migrated_database) == []
    with migrated_database.begin() as connection:
        assert (
            character_version(connection, proposed_run["character_id"])
            == proposed_run["character_version"]
        )


def test_a_commit_failure_leaves_no_partial_confirmation(
    migrated_database, settings, council, proposed_run
):
    """The transaction is abandoned after every write has been issued.

    Nothing in the service is trusted to undo anything; the assertion is that a
    failure between the last write and the commit leaves the database exactly as
    it was, which is what makes "one transaction" a fact rather than a claim.
    """
    with pytest.raises(RuntimeError, match="injected commit failure"):
        with migrated_database.connect() as connection:
            with connection.begin():
                migration_service(connection, settings).confirm(
                    context=council_context(council["C"].account_id),
                    proposal_id=proposed_run["proposal_id"],
                    reason="never committed",
                    expected_version=proposed_run["character_version"],
                    correlation_id=uuid4(),
                    now=utcnow(),
                )
                raise RuntimeError("injected commit failure")

    assert access_rows(migrated_database) == 0
    assert audit_actions(migrated_database) == []
    assert (
        scalar(
            migrated_database,
            "SELECT resolution FROM identity_link_proposals WHERE id = :id",
            id=proposed_run["proposal_id"],
        )
        == PROPOSED
    )


def test_a_stale_character_version_refuses_before_writing_anything(
    migrated_database, settings, council, proposed_run
):
    """Stale state is refused safely, and refused first.

    The character moves under the page — a rename, another Council action — and
    the confirmation submitted from the stale page is refused `409` before the
    grant, the decision or either audit event.
    """
    with migrated_database.begin() as connection:
        connection.execute(
            text("UPDATE characters SET version = version + 1 WHERE id = :id"),
            {"id": proposed_run["character_id"]},
        )

    with pytest.raises(StaleVersion):
        confirm(
            migrated_database,
            settings,
            proposal_id=proposed_run["proposal_id"],
            account_id=council["C"].account_id,
            expected_version=proposed_run["character_version"],
        )
    assert access_rows(migrated_database) == 0
    assert audit_actions(migrated_database) == []
    assert (
        scalar(
            migrated_database,
            "SELECT resolution FROM identity_link_proposals WHERE id = :id",
            id=proposed_run["proposal_id"],
        )
        == PROPOSED
    )


def test_a_proposal_whose_subject_has_no_account_is_unreachable(
    migrated_database, settings, council, monkeypatch, sheet_world
):
    """A snowflake the platform has never heard of cannot be linked.

    Refused as unreachable rather than causing an account to be minted from a
    Council form, and byte-identically to an unknown character so the refusal
    does not say which half of the pair is missing.
    """
    from application.web.errors import ObjectNotReachable

    run_command(
        monkeypatch,
        migrated_database,
        settings,
        characters=sheet_world["characters"],
        players=sheet_world["players"],
    )
    # No `link_discord` for `ADA_SUBJECT`: the proposal names a snowflake with no
    # platform account.
    proposal_id = proposal_id_for(migrated_database, PROPOSED)
    with pytest.raises(ObjectNotReachable):
        confirm(
            migrated_database,
            settings,
            proposal_id=proposal_id,
            account_id=council["C"].account_id,
        )
    assert access_rows(migrated_database) == 0
    assert audit_actions(migrated_database) == []


def test_a_link_created_between_the_run_and_the_confirmation_is_refused(
    migrated_database, settings, council, proposed_run
):
    """`AlreadyLinked`: the end state holds, and nothing is widened.

    Reached when R-25 grants the same pair between C-04 and the confirmation.
    Refusing costs nothing — the person already has access — and not refusing
    would mean either a duplicate active link, which the unique index refuses as
    an integrity error, or a silent widening of the existing grant.
    """
    with migrated_database.begin() as connection:
        grant_link(
            connection,
            character_id=proposed_run["character_id"],
            account_id=proposed_run["account_id"],
            granted_by=council["C"].account_id,
            access_kind="viewer",
        )

    with pytest.raises(AlreadyLinked):
        confirm(
            migrated_database,
            settings,
            proposal_id=proposed_run["proposal_id"],
            account_id=council["C"].account_id,
            expected_version=proposed_run["character_version"],
        )
    # Unchanged: not widened to `co_owner`, not duplicated, not revoked.
    link = rows(migrated_database, "SELECT * FROM character_access")[0]
    assert link["access_kind"] == "viewer"
    assert access_rows(migrated_database) == 1
    assert audit_actions(migrated_database) == []


def test_a_missing_proposal_is_a_404_shaped_refusal(
    migrated_database, settings, council
):
    """A proposal that does not exist is unreachable, not a conflict."""
    from application.web.errors import ObjectNotReachable

    with pytest.raises(ObjectNotReachable):
        confirm(
            migrated_database,
            settings,
            proposal_id=uuid4(),
            account_id=council["C"].account_id,
        )


# ===========================================================================
# The command line, the Sheet boundary and the operator's terminal
# ===========================================================================


def test_the_command_line_requires_the_mode_and_the_player_tab():
    """§7.7's parsing half.

    `--player-tab` is required even though the one-time tab is now confirmed as
    `Players` (`C-P3.2-B`): a default would turn temporary migration input into
    enduring command configuration and remove the explicit wrong-tab guard.
    `--dry-run` is required so every invocation says what it is. And the withdrawn
    C-05 surface is *gone*, not merely undocumented: an operator who types the old
    command gets a parse error rather than a silent reinterpretation.
    """
    parsed = command.parse_arguments(["--dry-run", "--player-tab", PLAYER_TAB])
    assert parsed.dry_run is True
    assert parsed.player_tab == PLAYER_TAB
    assert parsed.character_tab == CHARACTER_TAB

    for argv in (
        [],  # no mode, no tab
        ["--dry-run"],  # no tab
        ["--player-tab", PLAYER_TAB],  # no mode
        ["--dry-run", "--player-tab", "   "],  # a blank tab reads nothing
        ["--apply", "--run-id", str(uuid4())],  # the withdrawn C-05 invocation
        ["--dry-run", "--player-tab", PLAYER_TAB, "--run-id", str(uuid4())],
    ):
        with pytest.raises(SystemExit):
            command.parse_arguments(argv)


def test_the_command_help_describes_the_two_stage_pipeline():
    """The help text is where an operator learns what the command does.

    It has to say that a confirmation creates the link — an operator who believes
    a second command is still needed will wait for a step that no longer exists —
    and it must not describe an apply.
    """
    import contextlib
    import io

    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        with pytest.raises(SystemExit):
            command.parse_arguments(["--help"])
    # `argparse` re-wraps the description to the terminal width, so a phrase is
    # matched against whitespace-normalised text rather than against wherever the
    # wrap happened to fall.
    help_text = " ".join(buffer.getvalue().split())
    assert "C-04" in help_text
    assert "creates the link immediately" in help_text
    assert "never writes to Google" in help_text
    # The withdrawn mode is not described, offered or hinted at.
    for absent in ("C-05", "--apply", "--run-id", "materialize"):
        assert absent not in help_text, absent
    # And the module documents Google as temporary migration input.
    assert "withdrawn" in (command.__doc__ or "")


def test_no_apply_surface_survives_anywhere_in_the_command(monkeypatch):
    """C-05 is removed, not hidden behind a flag nobody documents.

    An undocumented mode is still a mode. The module is asked for the attributes
    the apply path was built from, and none of them exists.
    """
    for attribute in (
        "execute_apply",
        "run_apply_command",
        "render_apply",
        "IdentityMigrationApplyService",
        "ApplyRefused",
    ):
        assert not hasattr(command, attribute), attribute

    import application.web.identity_evidence as evidence

    for attribute in (
        "IdentityMigrationApplyService",
        "ApplyOutcome",
        "ApplyRefused",
        "APPLY_GRANTED",
    ):
        assert not hasattr(evidence, attribute), attribute

    import application.web.character_access as access

    for attribute in ("RecordedCouncilDecision", "LinkAuthority", "NotAConfirmedDecision"):
        assert not hasattr(access, attribute), attribute


def test_the_sheet_boundary_offers_no_write_at_all():
    """TC-MIG-12. The reader has one capability, and the modules have no other.

    Two assertions, because "we do not write" is only worth stating if it cannot be
    done: the selected reader is a *callable that reads one range* and carries no
    update method under any spelling, and no module on the tool's Sheet path
    mentions any Sheets write API.
    """
    import ast
    from pathlib import Path

    selection = ReaderProbe(character_values([]), player_values([])).build({})
    for spelling in ("update", "batch_update", "batchUpdate", "append", "clear", "write"):
        assert not hasattr(selection.read_values, spelling), spelling
    assert not hasattr(selection, "write_values")

    # Over the **AST**, not the text: a grep would match this module's own prose
    # explaining what is absent, which is how an absence guard ends up asserting
    # that nobody documented the rule.
    #
    # Two different questions, asked separately, because `list.append` and
    # `spreadsheets().values().append` are the same attribute name and only one of
    # them is a Sheets write:
    #
    # 1. `read_only.py` is the **only** module that touches a Google client. The
    #    methods it reaches on that client are asserted as an exact allowlist, so
    #    `values().update` or `values().append` would fail here even though
    #    `list.append` elsewhere does not.
    # 2. The other three modules import nothing from Google that can *act* — only
    #    its exception types, for classifying a failed read. A client or a
    #    credential is what a write would need, and neither is reachable there.
    root = Path(__file__).resolve().parents[2]

    reader = ast.parse((root / "adapters/sheets/read_only.py").read_text())
    builder = next(
        node
        for node in ast.walk(reader)
        if isinstance(node, ast.FunctionDef) and node.name == "_build_read_only_reader"
    )
    google_calls = {
        node.func.attr
        for node in ast.walk(builder)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
    }
    # `service.spreadsheets().values().get(...).execute()`, plus the dict access on
    # the result. Nothing else, and in particular nothing that writes.
    assert google_calls == {"spreadsheets", "values", "get", "execute"}, google_calls

    for module in (
        "adapters/sheets/identity_evidence.py",
        "adapters/sheets/columns.py",
        "tools/identity_migration.py",
    ):
        tree = ast.parse((root / module).read_text())
        imported = {
            name
            for node in ast.walk(tree)
            for name in (
                [node.module or ""]
                if isinstance(node, ast.ImportFrom)
                else [alias.name for alias in node.names]
                if isinstance(node, ast.Import)
                else []
            )
        }
        google = {
            name for name in imported if name.split(".")[0] in {"google", "googleapiclient"}
        }
        # Exception types only. `googleapiclient.discovery` builds a client and
        # `google.oauth2` builds a credential; either appearing here would be a
        # second place a Sheets call could originate, and only `read_only.py` — whose
        # reachable methods are asserted above — is allowed to be that place.
        assert google <= {
            "googleapiclient.errors",
            "google.auth.exceptions",
        }, f"{module} imports Google beyond its exception types: {sorted(google)}"

    # And the narrow scope is the one the credential asks for.
    from adapters.sheets.read_only import READ_ONLY_SCOPES

    assert READ_ONLY_SCOPES == (
        "https://www.googleapis.com/auth/spreadsheets.readonly",
    )


def test_the_portal_runtime_needs_no_google_package():
    """TC-MIG-18. Google is legacy migration input, not a platform dependency.

    Three assertions: the portal's requirement files name no Google package; the
    portal application imports none on any startup or request path; and C-04's own
    Google import is lazy, so `--help` and a configuration refusal work without
    the libraries.

    The import check runs in a **subprocess** with a clean interpreter. Reloading
    or un-importing modules inside this process would answer the question and
    leave every later case holding a stale class object, which is a worse bargain
    than one process start; and a fresh interpreter is also the only way to know
    that nothing *this* suite imported is what made the answer come out right.
    """
    import subprocess
    import sys
    from pathlib import Path

    root = Path(__file__).resolve().parents[2]
    for name in ("requirements-web.txt", "requirements-web.lock"):
        path = root / name
        if not path.exists():
            continue
        text_ = path.read_text().lower()
        for package in (
            "google-api-python-client",
            "google-auth",
            "google-api-core",
            "googleapis-common-protos",
        ):
            assert package not in text_, f"{name} names {package}"

    probe = (
        "import sys;"
        "import adapters.web.composition, adapters.web.portal_routes;"
        "leaked=[m for m in sys.modules "
        "if m.split('.')[0] in {'google','googleapiclient'}];"
        "print(','.join(sorted(leaked)))"
    )
    result = subprocess.run(
        [sys.executable, "-c", probe],
        cwd=root,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "", result.stdout

    # And `--help` works here, where the Google libraries are equally absent,
    # because C-04 imports them lazily and only when it actually reads.
    import contextlib
    import io

    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        with pytest.raises(SystemExit):
            command.parse_arguments(["--help"])
    assert buffer.getvalue()


def test_a_shifted_character_layout_refuses_before_any_database_work(
    monkeypatch, migrated_database, settings
):
    """A moved column is a refusal naming the column, not a run that guesses.

    Reading column C from a shifted Sheet would attribute one player's name to
    another character, which is the failure the positional guard exists for. The
    guard is the Phase 2 importer's, reused rather than re-derived.
    """
    shifted = character_values([("Alia Storm", "Ada")])
    shifted[0][2] = "Something Else"
    exit_code, _probe = run_command(
        monkeypatch,
        migrated_database,
        settings,
        characters=shifted,
        players=player_values([("Ada", "ada.one", False)]),
    )
    assert exit_code == command.EXIT_MISCONFIGURED
    assert scalar(migrated_database, "SELECT count(*) FROM identity_migration_runs") == 0


def test_a_shifted_player_layout_refuses_too(monkeypatch, migrated_database, settings):
    shifted = player_values([("Ada", "ada.one", False)])
    shifted[0][3] = "Not Active DM"
    exit_code, _probe = run_command(
        monkeypatch,
        migrated_database,
        settings,
        characters=character_values([("Alia Storm", "Ada")]),
        players=shifted,
    )
    assert exit_code == command.EXIT_MISCONFIGURED


def test_an_uninterpretable_active_dm_cell_names_its_row():
    """Evidence is still validated at the boundary, and the message names a row.

    Never the cell's contents in an operator-facing string beyond the offending
    token itself, which is what the operator has to go and look at.
    """
    from adapters.sheets.identity_evidence import player_rows

    values = player_values([("Ada", "ada.one", False)])
    values[1][3] = "perhaps"
    with pytest.raises(SheetLayoutError, match=f"row {PLAYER_FIRST_DATA_ROW}"):
        player_rows(values)


def test_the_c04_report_carries_counts_and_no_personal_data(
    monkeypatch, migrated_database, settings, sheet_world, capsys
):
    """The report is what lands in a terminal, a shell history and a CI log.

    The evidence itself is reviewed at R-28, behind Council authorization, which
    is where the personal data belongs. It names the run and says what happens
    next, and what happens next is a Council confirmation — not a second command.
    """
    run_command(
        monkeypatch,
        migrated_database,
        settings,
        characters=sheet_world["characters"],
        players=sheet_world["players"],
    )
    printed = capsys.readouterr().out
    assert "C-04 evidence run" in printed
    assert "balanced" in printed
    assert str(latest_run_id(migrated_database)) in printed
    assert "/v1/council/identity-migration" in printed
    assert "creates that character's access row immediately" in printed
    # It prints no `character_access rows written` figure at all: this command
    # cannot make one non-zero, so reporting it would be a constant dressed as a
    # measurement. And it offers no withdrawn next command.
    assert "character_access rows written" not in printed
    for absent in ("--apply", "--run-id", "C-05"):
        assert absent not in printed, absent
    for secret in (
        "Ada",
        "Bea",
        "ada.one",
        "shared.name",
        "Alia Storm",
        str(ADA_SUBJECT),
        str(TWIN_A_SUBJECT),
    ):
        assert secret not in printed, secret
