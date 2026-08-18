"""C-04: the Sheet-era identity-evidence migration (migration contract M-2).

    python -m tools.identity_migration --dry-run --player-tab 'Players'

One mode, and it is named explicitly. `--dry-run` is not a default and is not
optional: a command whose destructiveness depends on a flag being remembered is a
command an operator runs the wrong way once. This one is never destructive — it
writes evidence and no authorization — and saying so on every invocation is worth
one argument.

## What this command is, and what it is not

Migration contract §7.2 has **two** steps, and this module is the operator half of
the first:

```text
C-04 --dry-run                     R-28 / R-29 / R-30
read Sheet evidence           ->   review one proposal at a time
write proposals                    confirm: creates the link + audits atomically
write NO character_access          reject: decision + audit, and no link
```

**Command C-05 is withdrawn** (change-log entry C-P3.2-A, OD-46, 2026-08-17). It
was a `--apply --run-id` mode that materialized confirmed proposals into
`character_access` afterwards, written under a reading of §7.2 that three other
accepted passages contradicted. The maintainer ruled that a Guild Council
confirmation activates the link immediately, so there is nothing left to
materialize. The mode, its report, its refusals and its apply state are removed
rather than left in place unused: a second way for an authorization to come into
being is a second way for it to be wrong.

## A temporary utility, run outside the platform runtime

C-04 exists because some current character/player data still lives in the legacy
Google Sheet. Google is **migration input**, not a platform component: it is not
an operational database, not a portal dependency and not a participant in the
Council decision (§7.7).

`adapters/sheets/read_only.py` imports the Google client libraries lazily and
refuses with a typed, operator-facing message when they are absent, and they are
deliberately **not** in `requirements-web.txt` or its lock file. The operator runs
this command from a separate, temporary environment provisioned for the migration
window with those libraries and a read-only service-account credential. That
environment is not deployed and is destroyed when the legacy access is retired
after the approved verification window.

Consequence, stated plainly rather than discovered: **C-04 cannot be run from
`venv-web`.** That is the design, not a gap.

## Nothing is ever written to Google

The reader this command obtains has one method, which reads one A1 range; there is
no `batch_update` in this module, in `adapters/sheets/identity_evidence.py`, or in
`adapters/sheets/read_only.py`. Rolling back to the legacy linkage workflow
therefore requires nothing to be undone in the spreadsheet, because nothing was
ever done to it (§7.5).

## The player tab is named by the operator

Peter Duscha confirmed the one-time legacy tab name as `Players` on 2026-08-17
(`C-P3.2-B`). `--player-tab` remains **required**: keeping the temporary input
explicit prevents it from becoming an enduring portal or command default. The
character tab keeps its default because that range is already part of the Phase 2
importer's established contract.

## Output is bounded and carries no personal data

The report is counts, identifiers and a mode. No player name, no Discord name, no
snowflake, no Sheet cell and no credential appears in it, and the expected
operational failures are fixed strings with a stable exit code rather than a
traceback — an operator's terminal, shell history and CI log are the wrong place
for the personal data a proposal holds, and `adapters/safe_logging.py` keeps the
same rule at every logging level. The evidence itself is reviewed at R-28, behind
Council authorization, which is where it belongs.
"""
from __future__ import annotations

import argparse
import logging
import os
import sys
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from adapters.safe_logging import log_expected_failure
from adapters.sheets.identity_evidence import (
    CHARACTER_RANGE,
    CHARACTER_TAB,
    PLAYER_RANGE,
    SheetLayoutError,
    character_rows,
    player_rows,
)
from adapters.sheets.read_only import (
    ReaderSelection,
    SheetCredentialError,
    build_values_reader,
)
from application.web.identity_evidence import (
    DuplicatePlayerNames,
    IdentityEvidenceRunService,
    RunOutcome,
    SheetCharacterRow,
    SheetPlayer,
    UnbalancedRun,
    UnmappedSourceRows,
)
from domain.foundry_profile import PROFILE as FIELD_PROFILE

if TYPE_CHECKING:  # imported for typing only; the runtime import stays lazy
    from adapters.database.config import DatabaseSettings

logger = logging.getLogger(__name__)

EXIT_OK = 0
#: The work refused before changing anything: an unbalanced report, unmapped
#: source rows, or duplicate player names. Nothing was written.
EXIT_REFUSED = 1
#: Configuration was refused before anything was read: the database target, the
#: Sheet credential, the Sheet layout or the command line itself.
EXIT_MISCONFIGURED = 2
#: The Sheet could not be read: network, credential, quota or permission.
EXIT_SHEET_UNAVAILABLE = 3
#: The database could not be reached or refused the work.
EXIT_DATABASE_UNAVAILABLE = 4
#: Another writer conflicted with this run.
EXIT_CONFLICT = 5

SHEET_UNAVAILABLE_MESSAGE = (
    "The Sheet could not be read. Check network access, the service account's "
    "permission on the spreadsheet, and the configured spreadsheet id, then "
    "re-run. Nothing was written."
)
DATABASE_UNAVAILABLE_MESSAGE = (
    "The database could not be reached or refused the work. Check that "
    "PostgreSQL is running and that WEB_DATABASE_URL names the intended "
    "database, then re-run. Nothing was written."
)
CONFLICT_MESSAGE = (
    "The work conflicted with another change: a second run or a Council "
    "decision made while this one was in progress. Nothing was written; re-run "
    "once the other change has finished."
)

#: PostgreSQL's two "you lost a race, retry" states: `serialization_failure` and
#: `deadlock_detected`. Both mean the same thing to an operator — nothing was
#: written and re-running is the remedy — and neither is a defect to report.
CONCURRENCY_SQLSTATES = frozenset({"40001", "40P01"})


@dataclass(frozen=True, slots=True)
class IdentityMigrationSettings:
    """The three portal-owned values C-04 actually consumes.

    C-04 is a temporary operator command, not a web process. Requiring the
    complete ``WebSettings`` graph made an operator provide OAuth, WebAuthn,
    cookie and encryption secrets that this command neither reads nor should
    possess. The database member remains the canonical validated
    ``DatabaseSettings`` value; only the command-specific graph is narrow.
    """

    database: DatabaseSettings
    guild_id: int

    @classmethod
    def from_environment(cls, values: Mapping[str, str]) -> IdentityMigrationSettings:
        from adapters.database.config import (
            ConnectionPolicy,
            DatabaseSettings,
        )

        environment = (values.get("WEB_ENVIRONMENT") or "").strip()
        if not environment:
            raise ValueError("WEB_ENVIRONMENT is required and was not set.")

        database = DatabaseSettings.from_mapping(
            values,
            environment=environment,
            variable="WEB_DATABASE_URL",
            environ=values,
            policy=ConnectionPolicy.SOCKET_OR_LOOPBACK,
        )

        raw_guild_id = (values.get("WEB_DISCORD_GUILD_ID") or "").strip()
        if not raw_guild_id or not raw_guild_id.isdigit() or int(raw_guild_id) <= 0:
            raise ValueError(
                "WEB_DISCORD_GUILD_ID must be a positive Discord snowflake."
            )
        guild_id = int(raw_guild_id)

        # S-07, kept rather than dropped with the rest of the portal graph. This
        # command scopes its membership scan and every proposal row it writes by
        # this snowflake, so an environment/guild mismatch does not merely start
        # the wrong process — it writes a whole evidence run attributed to the
        # wrong community. The constant is imported rather than repeated: a
        # production identifier does not belong in this module's source.
        from application.web.config import PRODUCTION_GUILD_ID

        if environment == "production":
            if guild_id != PRODUCTION_GUILD_ID:
                raise ValueError(
                    "WEB_DISCORD_GUILD_ID is not the production guild, but "
                    "WEB_ENVIRONMENT is production. A production run pointed at "
                    "another guild would write evidence for the wrong community."
                )
        elif guild_id == PRODUCTION_GUILD_ID:
            raise ValueError(
                "WEB_DISCORD_GUILD_ID is the production guild, but WEB_ENVIRONMENT "
                f"is {environment!r}. No non-production run may read or write "
                "evidence for the production guild (delivery plan §10)."
            )
        return cls(database=database, guild_id=guild_id)


class MigrationCommandError(RuntimeError):
    """An expected operational failure, already translated for the operator."""

    def __init__(self, message: str, exit_code: int) -> None:
        super().__init__(message)
        self.exit_code = exit_code


def parse_arguments(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """One required mode and one explicit, maintainer-confirmed migration input.

    `--dry-run` is required rather than defaulted so every invocation says what
    it is. `--player-tab` remains required even though the one-time input is now
    confirmed as `Players` (§7.7, C-P3.2-B): a default here would turn temporary
    migration input into enduring command behavior.
    """
    parser = argparse.ArgumentParser(
        prog="python -m tools.identity_migration",
        description=(
            "C-04 resolves Sheet-era identity evidence into Council-confirmable "
            "link proposals. It writes no character_access row, creates no "
            "authorization, and never writes to Google. Guild Council confirms "
            "each proposal at /v1/council/identity-migration, and a confirmation "
            "creates the link immediately. Temporary migration utility: run it "
            "from the separate operator environment that carries the Google "
            "client libraries and a read-only credential, not from the portal "
            "runtime."
        ),
    )
    parser.add_argument(
        "--dry-run",
        dest="dry_run",
        action="store_true",
        required=True,
        help=(
            "Required. Read the Sheet evidence and write one durable evidence "
            "run with its proposals and ambiguity candidates. Writes no link."
        ),
    )
    parser.add_argument(
        "--character-tab", default=CHARACTER_TAB, help="Tab holding Characters."
    )
    parser.add_argument(
        "--character-range",
        default=CHARACTER_RANGE,
        help="A1 range within the character tab, starting at the header row.",
    )
    parser.add_argument(
        "--player-tab",
        required=True,
        help=(
            "Required. The exact one-time legacy player tab confirmed by the "
            "maintainer as 'Players'; it remains explicit rather than defaulted."
        ),
    )
    parser.add_argument(
        "--player-range",
        default=PLAYER_RANGE,
        help="A1 range within the player tab, starting at the header row.",
    )
    arguments = parser.parse_args(argv)
    if not str(arguments.player_tab).strip():
        parser.error("--player-tab must name the tab; a blank name reads nothing.")
    return arguments


def build_run_context():
    """Build C-04's narrow settings graph and database engine.

    Database target validation is still delegated to the project's canonical
    database validator. OAuth, WebAuthn, session and browser settings are not
    accepted dependencies of this non-HTTP command.
    """
    from sqlalchemy import create_engine

    settings = IdentityMigrationSettings.from_environment(os.environ)
    return create_engine(settings.database.url, pool_pre_ping=True), settings


def sheet_failure_types() -> tuple[type[BaseException], ...]:
    """Exception types that mean "the Sheet could not be read".

    Resolved at call time and tolerant of a missing Google library, so `--help`,
    a configuration error and the test suite never require the dependency.
    """
    types: list[type[BaseException]] = [OSError, TimeoutError]
    try:  # pragma: no cover - depends on the installed Google libraries
        from googleapiclient.errors import Error as GoogleApiError

        types.append(GoogleApiError)
    except ImportError:  # pragma: no cover
        pass
    try:  # pragma: no cover
        from google.auth.exceptions import GoogleAuthError

        types.append(GoogleAuthError)
    except ImportError:  # pragma: no cover
        pass
    return tuple(types)


def is_concurrency_conflict(error: BaseException) -> bool:
    """Did PostgreSQL refuse this because another transaction won a race?

    Asked of the SQLSTATE rather than of the message, so it does not depend on a
    locale, a driver version or a string nobody controls.
    """
    original = getattr(error, "orig", None)
    for candidate in (original, error):
        state = getattr(candidate, "sqlstate", None) or getattr(
            candidate, "pgcode", None
        )
        if state in CONCURRENCY_SQLSTATES:
            return True
    return False


def select_reader() -> ReaderSelection:
    """The read-only Sheet boundary, or a translated refusal."""
    try:
        return build_values_reader(os.environ)
    except SheetCredentialError as error:
        # A fixed, operator-facing string; `read_only.py` never renders the
        # underlying Google error, which can quote credential material.
        raise MigrationCommandError(
            f"Sheet credential refused: {error}", EXIT_MISCONFIGURED
        ) from error
    except sheet_failure_types() as error:
        log_expected_failure(logger, "sheets_client_unreachable", error)
        raise MigrationCommandError(
            SHEET_UNAVAILABLE_MESSAGE, EXIT_SHEET_UNAVAILABLE
        ) from error


def read_sources(
    selection: ReaderSelection,
    *,
    character_tab: str,
    character_range: str,
    player_tab: str,
    player_range: str,
):
    """Read the two ranges and shape them. Two `values.get` calls, no writes."""
    try:
        character_values = selection.read_values(f"{character_tab}!{character_range}")
        player_values = selection.read_values(f"{player_tab}!{player_range}")
    except sheet_failure_types() as error:
        log_expected_failure(logger, "sheet_read_failed", error)
        raise MigrationCommandError(
            SHEET_UNAVAILABLE_MESSAGE, EXIT_SHEET_UNAVAILABLE
        ) from error
    try:
        # A layout refusal is this repository's own message and names only
        # columns and row numbers, never a cell's contents.
        return character_rows(character_values), player_rows(player_values)
    except SheetLayoutError as error:
        raise MigrationCommandError(
            f"Sheet layout refused: {error}", EXIT_MISCONFIGURED
        ) from error


def execute_run(
    engine,
    settings,
    *,
    characters,
    players,
    character_tab: str,
    player_tab: str,
) -> RunOutcome:
    """One transaction: the run row, every proposal and every candidate.

    All of it commits or none of it does. A failure part-way leaves no run at all
    rather than a run whose totals describe proposals that were never written, so
    a re-run after a crash produces a whole run instead of the second half of one.
    The three refusals below reach the operator the same way and with the same
    consequence: the transaction is abandoned before it commits, so no partial run
    survives a refusal.
    """
    from adapters.web.repositories import (
        IdentityEvidenceSourceRepository,
        IdentityProposalRepository,
    )

    source_label = f"{character_tab}!C + {player_tab}!A/B/D"
    correlation_id = uuid4()
    try:
        with engine.begin() as connection:
            service = IdentityEvidenceRunService(
                sources=IdentityEvidenceSourceRepository(connection),
                proposals=IdentityProposalRepository(connection),
                guild_id=settings.guild_id,
            )
            return service.run(
                sheet_character_rows=(
                    SheetCharacterRow(
                        row_number=row.row_number, player_name=row.player_name
                    )
                    for row in characters
                ),
                sheet_players=(
                    SheetPlayer(
                        player_name=row.player_name,
                        discord_name=row.discord_name,
                        active_dm=row.active_dm,
                    )
                    for row in players
                ),
                sheet_tab=character_tab,
                source_label=source_label,
                profile_version=FIELD_PROFILE.version,
                correlation_id=correlation_id,
                now=_utcnow(),
            )
    except (UnbalancedRun, UnmappedSourceRows, DuplicatePlayerNames) as error:
        # Each is a refusal to proceed rather than a warning, and each already
        # carries an operator-facing message naming counts and a remedy and no
        # personal data. Nothing was written: the transaction had not committed.
        raise MigrationCommandError(f"Run refused: {error}", EXIT_REFUSED) from error
    except IntegrityError as error:
        # The run row's own balance constraint lands here when the arithmetic
        # disagrees with itself, as does a concurrent write on a row this run
        # touched. Both mean the same thing to an operator: nothing was written.
        log_expected_failure(logger, "identity_migration_conflict", error)
        raise MigrationCommandError(CONFLICT_MESSAGE, EXIT_CONFLICT) from error
    except SQLAlchemyError as error:
        if is_concurrency_conflict(error):
            log_expected_failure(logger, "identity_migration_conflict", error)
            raise MigrationCommandError(CONFLICT_MESSAGE, EXIT_CONFLICT) from error
        log_expected_failure(logger, "database_unavailable", error)
        raise MigrationCommandError(
            DATABASE_UNAVAILABLE_MESSAGE, EXIT_DATABASE_UNAVAILABLE
        ) from error


def render_evidence_run(outcome: RunOutcome) -> str:
    """§7.4's control totals, and the balance, as arithmetic on the page.

    An operator can check the report by reading it, which is the point: the
    balance is not asserted in prose, it is shown with both sides.

    The report prints **no** `character_access rows written` figure. This command
    cannot write one, so a line reporting zero of them would be a constant
    dressed as a measurement — which is exactly the misleading line the withdrawn
    C-05 mode printed.
    """
    totals = outcome.totals
    buckets = (
        totals.already_linked + totals.proposed + totals.ambiguous + totals.unresolved
    )
    return "\n".join(
        [
            "Mode:           C-04 evidence run (--dry-run)",
            f"Run id:         {outcome.run_id}",
            f"Correlation id: {outcome.correlation_id}",
            "",
            "Control totals (migration contract §7.4):",
            f"  source characters   {totals.source_characters}",
            f"  source players      {totals.source_players}",
            f"  already linked      {totals.already_linked}",
            f"  proposed            {totals.proposed}",
            f"  ambiguous           {totals.ambiguous}",
            f"  unresolved          {totals.unresolved}",
            "",
            f"  {totals.already_linked} + {totals.proposed} + {totals.ambiguous} + "
            f"{totals.unresolved} = {buckets}, source characters "
            f"{totals.source_characters} — "
            f"{'balanced' if buckets == totals.source_characters else 'UNBALANCED'}",
            "",
            f"Proposals written:  {outcome.proposals_written}",
            f"Candidates written: {outcome.candidates_written}",
            "",
            "This run created no character_access row and cannot: only a Guild "
            "Council confirmation does.",
            "",
            "Next: Guild Council reviews each proposal at "
            "/v1/council/identity-migration. Confirming one creates that "
            "character's access row immediately, in the same transaction as the "
            "decision and its audit events; rejecting one creates nothing.",
        ]
    )


def _utcnow():
    from datetime import datetime, timezone

    return datetime.now(timezone.utc)


def run_evidence_command(engine, settings, arguments) -> str:
    """C-04, end to end. The only thing in Phase 3 that touches Google."""
    selection = select_reader()
    # stderr, so a pipeline capturing the report does not capture the note.
    print(selection.note, file=sys.stderr)
    characters, players = read_sources(
        selection,
        character_tab=arguments.character_tab,
        character_range=arguments.character_range,
        player_tab=arguments.player_tab,
        player_range=arguments.player_range,
    )
    return render_evidence_run(
        execute_run(
            engine,
            settings,
            characters=characters,
            players=players,
            character_tab=arguments.character_tab,
            player_tab=arguments.player_tab,
        )
    )


def main(argv: Sequence[str] | None = None) -> int:
    arguments = parse_arguments(argv)

    try:
        engine, settings = build_run_context()
    except Exception as error:  # noqa: BLE001 - every startup refusal is one answer
        # The narrow C-04 settings boundary raises operator-facing refusals that
        # name variables and never their values. The remedy is the same for each:
        # correct the temporary environment before any Sheet read begins.
        print(f"Configuration refused: {error}", file=sys.stderr)
        return EXIT_MISCONFIGURED

    try:
        report = run_evidence_command(engine, settings, arguments)
    except MigrationCommandError as error:
        print(str(error), file=sys.stderr)
        return error.exit_code
    finally:
        engine.dispose()

    print(report)
    return EXIT_OK


if __name__ == "__main__":  # pragma: no cover - process entry point
    raise SystemExit(main())
