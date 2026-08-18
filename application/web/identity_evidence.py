"""M-2: Sheet-era identity evidence, and the Council confirmation that activates it.

## The pipeline this module implements, in the order the contract states it

Migration contract §7.2 has **two** steps, and the second is the one that
authorizes:

```text
C-04 --dry-run                          Council (R-28/R-29/R-30)
──────────────────                      ────────────────────────
read-only Sheet boundary          ──▶   review one proposal at a time
writes identity_link_proposals          confirm: creates the character_access row
writes NO character_access               and both audit events in one transaction,
                                         through the same service R-25 uses
                                        reject: decision + audit, and no link
```

`IdentityEvidenceRunService` is step 1 and `IdentityMigrationService` is the R-28
read and step 2.

**Corrected on the maintainer's ruling of 2026-08-17 (change-log entry
C-P3.2-A, OD-46).** An earlier delivery of P3.2 read §7.2 as having a third step —
`C-05 --apply`, materializing confirmed proposals into `character_access` later —
and built an apply service, an apply state, a recorded-decision authority object
and a superseded-run rule to manage the gap between deciding and linking. Three
other accepted passages placed the write at the confirmation, and the maintainer
resolved the contradiction in their favour. **A confirmation is the activation.**
Every part of the deferred-apply architecture is gone rather than retained
because it existed: an unused apply phase is a second, untested way for an
authorization to come into being.

So `confirm()` below writes the link, and it writes it through
`CharacterAccessService.grant()` — the one R-25 uses — inside the route's one
transaction, attributed to the confirming Council member's **live** authorization
context. There is no second grant implementation anywhere in M-2, and therefore no
second place for the one-active-owner invariant, the reason requirement, the
optimistic version, the audit event and the atomicity to be got right.

The original M-2 rationale follows, unchanged.


The migration contract keeps M-1 and M-2 apart deliberately, and this module is
the whole of M-2's application logic. M-1 asked *"which platform account does
this existing Discord-keyed row belong to?"* and was total, computed and done by
P3.1's migration. M-2 asks *"which Discord human does this Sheet row's Player
Name refer to?"*, and the honest answer for many rows is **nobody the platform
can determine**. Building the two together would let a name-derived guess flow
into an authorization-bearing column under cover of a deterministic backfill.

## What the evidence is worth

`Characters C` gives a *player name*; the player tab's column B gives that
player's *Discord name*. The chain character → player → Discord therefore exists
in the spreadsheet, and two facts limit it to evidence, both already recorded:
it is a **username and not a snowflake**, and usernames change; and it is **one
Discord name per player**, while the product invariant allows several authorized
users per character. `Players D` (*Active DM*) is reconciliation evidence and
never grants capability (OD-18).

So: a resolution is a *proposal*. The only identity in the pipeline is a Discord
snowflake resolved from the membership projection, and the only thing that ever
confers reach over a character is a `character_access` row written after a named
Council member confirmed that specific proposal.

## The resolver refuses to choose, twice

`resolve()` below returns `ambiguous` when more than one guild member's username
matches, lists every candidate, and picks none. That is the same rule
`application/foundry/reconciliation.py` already applies to Actor mapping — *an
ambiguous candidate lookup fails closed* — applied to people instead of Actors.
An ambiguous proposal is **not confirmable**, and the server refuses the
confirmation regardless of what the browser submits, because `proposed_subject`
is null and there is nothing to link to.

It refuses a second time, **upstream**, and that refusal is the remediation of a
reproduced identity-integrity defect (§7.3.1, C-P3.2-A). The player join used to
be a dict comprehension keyed by the normalized player name, so two Sheet rows
called `Ada` and `ADA` collided silently and whichever came later in the Sheet
decided the confirmable Discord identity of every character that named that
player. Sheet order is not a tie-break; it is a layout accident deciding who gets
access. `resolve()` now refuses the **whole run** when two player rows share one
normalized key, so there is no partial run for a duplicate to hide in and no
control total that could report the collision as an ordinary ambiguity.

Comparison goes through `domain.names.DisplayName`, the platform's one answer to
*"are these the same name?"* — for the match, and for the duplicate check, which
is why the duplicate check lives here and not in the Sheets adapter. A second
copy of a name-comparison rule is a second place for it to be wrong, and this one
would be wrong in the direction of linking two people.

## Nothing is written to Google Sheets, ever

C-04 reads through the existing read-only boundary. There is no write path in
this module, in the tool that drives it, or in the adapter either of them uses,
so rolling back to the legacy linkage workflow requires nothing to be undone in
the Sheet — because nothing was ever done to it. Google is legacy **migration
input** with an end date (§7.7); the portal and the PostgreSQL-backed runtime
need neither the libraries nor the credential.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from application.audit import ActorCapability, AuditEvent, AuditSource
from application.web.capabilities import WebAuthorizationContext
from application.web.character_access import BlankReason, REASON_BOUND
from application.web.errors import (
    ObjectNotReachable,
    RefusalCode,
    WebRefusal,
)
from application.web.pagination import Page
from application.web.view_models import (
    ACTOR_NAME_BOUND,
    DISCORD_NAME_BOUND,
    PAGE_SIZE_DEFAULT,
    SMALL_LIST_BOUND,
    IdentityMigrationView,
    Instant,
    LinkProposal,
    MigrationRun,
    MigrationTotals,
    SafeText,
    bounded_tuple,
)
from domain.names import DisplayName

#: The four resolutions a dry run can produce. `confirmed` and `rejected` are
#: transitions a Council member makes; a run never writes one.
PROPOSED = "proposed"
AMBIGUOUS = "ambiguous"
UNRESOLVED = "unresolved"
ALREADY_LINKED = "already_linked"

#: The access kind a confirmed identity proposal creates. `owner` is deliberately
#: **not** it: the Sheet says who plays a character, and OD-37's one-active-owner
#: invariant makes ownership a decision a Council member takes explicitly through
#: R-25 rather than one a migration takes for them from a spreadsheet column.
#:
#: It is a constant rather than a parameter, and R-29 has no field for it, so the
#: kind a confirmation creates is not something a browser can substitute. VM-10
#: renders it on the form, because a Council member is entitled to see what the
#: confirmation is about to create before creating it.
CONFIRMED_ACCESS_KIND = "co_owner"


@dataclass(frozen=True, slots=True)
class SheetCharacter:
    """One `Characters` row's identity-linkage evidence. No game state."""

    character_id: UUID
    display_name: str
    #: `Characters C`.
    player_name: str


@dataclass(frozen=True, slots=True)
class SheetPlayer:
    """One `Players` row: `A` (name), `B` (Discord name), `D` (Active DM)."""

    player_name: str
    discord_name: str | None
    active_dm: bool


@dataclass(frozen=True, slots=True)
class GuildMember:
    """One member of the membership projection, as evidence to match against."""

    subject: str
    username: str
    global_name: str | None


@dataclass(frozen=True, slots=True)
class Resolution:
    """One character's outcome. `subject` is set only for `proposed`."""

    character: SheetCharacter
    player: SheetPlayer | None
    resolution: str
    subject: str | None
    candidates: tuple[tuple[str, str], ...]


@dataclass(frozen=True, slots=True)
class RunTotals:
    """§7.4's arithmetic, computed rather than asserted."""

    source_characters: int
    source_players: int
    already_linked: int
    proposed: int
    ambiguous: int
    unresolved: int

    def balances(self) -> bool:
        return (
            self.already_linked + self.proposed + self.ambiguous + self.unresolved
            == self.source_characters
        )


class UnbalancedRun(Exception):
    """A dry run whose buckets do not account for every source row.

    A refusal to proceed, not a warning: the plan's success measure is *"no
    identity discrepancy is silently accepted"* (§0.5). PostgreSQL refuses the
    run row for the same reason, so this exception is the *legible* half of a
    control that holds even if this check were removed.
    """


class DuplicatePlayerNames(Exception):
    """Two player-tab rows share one normalized *Player Name* key.

    Migration contract §7.3.1, and the remediation of a reproduced defect. The
    join from `Characters C` to a Discord name is only meaningful if the player
    tab names each player once; two rows claiming one key mean the platform
    cannot tell which person a character's *Player Name* refers to, and the one
    thing it must never do is decide that by which row came later in the Sheet.

    A refusal of the **whole run**, for the same reason `UnmappedSourceRows` is
    one: any per-character treatment would let a source-integrity defect be
    reported as an ordinary ambiguity inside a balance computed over a player set
    the run had already decided was self-consistent. Refusing writes no run row,
    no proposal and no candidate, so there is nothing partial for the duplicate to
    hide in.

    The message carries **counts only** — no player name, no Discord name, no
    snowflake and no cell. An operator's terminal, shell history and CI log are
    not the place for the personal data the player tab holds, and the remedy does
    not need one: resolve the duplicate in the legacy Sheet, then re-run. Nothing
    in this workflow writes to Google, so the platform does not resolve it for
    them.
    """

    def __init__(self, *, duplicate_keys: int, rows_involved: int) -> None:
        super().__init__(
            f"{duplicate_keys} player name(s) appear on more than one player-tab "
            f"row, across {rows_involved} rows, comparing names the same way the "
            "resolver does (NFC-normalised and case-folded). A character's Player "
            "Name cannot be resolved to one person while that is true, and this "
            "run will not choose one by row order. Resolve the duplicates in the "
            "source spreadsheet and re-run. Nothing was written."
        )
        self.duplicate_keys = duplicate_keys
        self.rows_involved = rows_involved


def _index_players(player_rows) -> dict[str, SheetPlayer]:
    """`{normalized player name: player}`, or a refusal if that is not a function.

    The dict comprehension this replaces was the defect: a later row silently
    overwrote an earlier one under the same key, so `Ada` and `ADA` resolved to
    whichever the Sheet happened to list second. Collisions are collected first
    and counted, so the refusal reports the size of the problem rather than the
    first instance of it — an operator fixing one duplicate at a time and
    re-running is an operator making several passes over a spreadsheet.

    Blank player names are not rows in this index and cannot collide: the player
    tab's parser already refuses a row that carries data without a name, and a
    wholly blank spacer row is skipped there.
    """
    grouped: dict[str, list[SheetPlayer]] = {}
    for player in player_rows:
        if not player.player_name.strip():
            continue
        grouped.setdefault(DisplayName(player.player_name).identity_key, []).append(
            player
        )

    collisions = {key: rows for key, rows in grouped.items() if len(rows) > 1}
    if collisions:
        raise DuplicatePlayerNames(
            duplicate_keys=len(collisions),
            rows_involved=sum(len(rows) for rows in collisions.values()),
        )
    return {key: rows[0] for key, rows in grouped.items()}


def resolve(
    *,
    sheet_characters,
    sheet_players,
    guild_members,
    already_linked,
) -> tuple[tuple[Resolution, ...], RunTotals]:
    """The one deterministic resolver. C-04 is its only caller.

    Matching is over the **NFC-normalised, case-folded** username, through
    `DisplayName.identity_key`. A player row whose Discord name is blank, and a
    character row whose player name matches no player row, both land in
    `unresolved` — the same bucket, because the platform can determine nothing
    in either case and inventing a distinction would suggest one of them is
    closer to an answer.

    ## The player index is a function, or the run refuses

    `_index_players` raises `DuplicatePlayerNames` when two player rows share one
    normalized key (§7.3.1). It is called **before** any character is examined and
    before anything is written, so a duplicate refuses the whole run rather than
    deciding one character's Discord identity by Sheet order. The refusal is
    therefore independent of the order of `sheet_characters` and of
    `sheet_players`: it depends only on the *set* of keys.

    ## Every input is materialised once, at the boundary

    The four parameters are *iterables*, and a caller is entitled to hand over a
    generator: `tools/identity_migration.py` shapes Sheet rows lazily, and a
    repository cursor is not a list either. This function used to traverse them
    where it needed them and then ask `len(tuple(sheet_characters))` for the
    control totals, which is correct for a list and silently wrong for a
    generator — the second traversal of an exhausted iterator yields nothing, so
    `source_characters` came out `0` and §7.4's balance was asserted against a
    denominator that had been consumed. The three lines below are the fix and the
    whole of it: each input becomes a stable collection exactly once, and every
    resolution and every total is derived from *those* rather than from the
    parameter. `already_linked` is materialised for the same reason, since a
    one-shot iterable of pairs would answer the first `in` test and then answer
    nothing.

    ## `already_linked` is a pair, not a character

    §7.3's fifth row is *"the character already has an active access row **for
    that account**"*. So the bucket is a property of the (character, person) pair
    and not of the character: a character owned by one person is still a proposal
    for a second authorized user, which is the whole point of the product
    invariant that a character may have several explicitly authorized users. The
    parameter is therefore a set of `(character_id, discord subject)` pairs, and
    the test happens **after** the subject resolves, because before that there is
    no person to ask the question about.
    """
    characters = tuple(sheet_characters)
    player_rows = tuple(sheet_players)
    members = tuple(guild_members)
    linked = frozenset(already_linked)

    players = _index_players(player_rows)
    by_username: dict[str, list[GuildMember]] = {}
    for member in members:
        by_username.setdefault(
            DisplayName(member.username).identity_key, []
        ).append(member)

    resolutions: list[Resolution] = []
    already = 0
    counts = {PROPOSED: 0, AMBIGUOUS: 0, UNRESOLVED: 0}

    for character in characters:
        player = players.get(DisplayName(character.player_name).identity_key)
        discord_name = (player.discord_name or "").strip() if player else ""
        if not discord_name:
            resolutions.append(
                Resolution(
                    character=character,
                    player=player,
                    resolution=UNRESOLVED,
                    subject=None,
                    candidates=(),
                )
            )
            counts[UNRESOLVED] += 1
            continue

        matches = by_username.get(DisplayName(discord_name).identity_key, [])
        if len(matches) == 1:
            if (character.character_id, matches[0].subject) in linked:
                # Counted, not proposed: there is nothing to propose when this
                # character already carries an active link for **this** person.
                # A rerun of C-04 after a Council confirmation lands here, which
                # is what makes the pipeline idempotent across runs without any
                # run having to know what an earlier one decided.
                already += 1
                continue
            resolutions.append(
                Resolution(
                    character=character,
                    player=player,
                    resolution=PROPOSED,
                    subject=matches[0].subject,
                    candidates=((matches[0].subject, matches[0].username),),
                )
            )
            counts[PROPOSED] += 1
        elif len(matches) > 1:
            # **Every** candidate is listed; none is chosen. A Council member
            # resolves it to one snowflake before anything can be confirmed.
            #
            # No `[:SMALL_LIST_BOUND]` here, deliberately. That slice used to be
            # applied at this line, which made the *durable* record of an
            # ambiguity depend on a **rendering** bound: an eleventh member whose
            # username matched was dropped before
            # `identity_link_proposal_candidates` ever saw it, so the evidence a
            # Council member reviewed said the ambiguity was between ten people
            # when it was between more, and the dropped candidate was
            # unrecoverable from the run. §7.6 requires ambiguity to persist as an
            # explicit record naming every candidate, so the bound belongs where
            # the list is *shown* (`_proposal_view`, which reports its truncation
            # and the true count) and nowhere near where it is stored.
            resolutions.append(
                Resolution(
                    character=character,
                    player=player,
                    resolution=AMBIGUOUS,
                    subject=None,
                    candidates=tuple(
                        sorted((member.subject, member.username) for member in matches)
                    ),
                )
            )
            counts[AMBIGUOUS] += 1
        else:
            resolutions.append(
                Resolution(
                    character=character,
                    player=player,
                    resolution=UNRESOLVED,
                    subject=None,
                    candidates=(),
                )
            )
            counts[UNRESOLVED] += 1

    totals = RunTotals(
        # From the materialised collections, never from the parameters: see the
        # docstring. A generator input would have made both of these `0`.
        source_characters=len(characters),
        source_players=len(player_rows),
        already_linked=already,
        proposed=counts[PROPOSED],
        ambiguous=counts[AMBIGUOUS],
        unresolved=counts[UNRESOLVED],
    )
    if not totals.balances():
        raise UnbalancedRun(
            "the run's buckets do not account for every source character: "
            f"{totals.already_linked} already linked + {totals.proposed} proposed "
            f"+ {totals.ambiguous} ambiguous + {totals.unresolved} unresolved "
            f"!= {totals.source_characters} source rows"
        )
    return tuple(resolutions), totals


@dataclass(frozen=True, slots=True)
class SheetCharacterRow:
    """One `Characters` row as the Sheet gives it: a position and column C.

    The **position** is the identity here. `sheet_row_mappings` turns it into a
    stable character id, which is the mapping the Phase 2 importer retained for
    exactly this purpose. Resolving a character *name* to a character would be a
    second name-comparison rule deciding identity, and the one thing M-2 must
    never do is let a name establish equivalence (OD-42, N-16).
    """

    row_number: int
    #: `Characters C`. Blank rows are not source rows and never reach here.
    player_name: str


@dataclass(frozen=True, slots=True)
class RunOutcome:
    """What one C-04 run produced. Counts and identifiers only.

    Deliberately carries no name, no snowflake and no Sheet cell: it is what the
    operator's terminal prints, and an operator's terminal, shell history and CI
    log are not the right place for the personal data a proposal holds. The
    evidence itself is in the database, behind R-28's Council authorization.
    """

    run_id: UUID
    correlation_id: UUID
    totals: RunTotals
    #: How many proposals this run persisted — `proposed + ambiguous + unresolved`.
    proposals_written: int
    #: How many candidate rows it persisted across every ambiguous proposal.
    candidates_written: int


class UnmappedSourceRows(Exception):
    """Source rows whose Sheet position has no stable character mapping.

    A refusal, not a warning, and for the same reason `UnbalancedRun` is one:
    §7.4 requires **every** source row to land in exactly one bucket, and a row
    the platform cannot name a character for can land in none of them durably —
    `identity_link_proposals.character_id` is `NOT NULL` and foreign-keyed, so
    there is nowhere to put it. Counting it into `source_characters` and writing
    no proposal for it would make the balance a lie; leaving it out of
    `source_characters` would make the report silently narrower than the Sheet.
    The third option is to refuse the run and name the count, and it is the one
    the plan's *"no identity discrepancy is silently accepted"* requires.

    The remedy is an operational one the operator can carry out: run the Phase 2
    character import so the missing rows acquire their mapping, then re-run.
    """

    def __init__(self, count: int, sheet_tab: str) -> None:
        super().__init__(
            f"{count} source row(s) in {sheet_tab!r} have no stable character "
            "mapping, so this run cannot account for every source row. Run the "
            "Phase 2 character import first, then re-run. Nothing was written."
        )
        self.count = count


#: How many membership rows one keyset page of the projection scan reads.
#:
#: **Not a numeric policy, and deliberately not an `N-nn`.** It replaced
#: `GUILD_POPULATION_BOUND = 5000`, which the second review found to be a policy
#: number that appears in no row of the accepted numeric register — a guild
#: larger than it made the whole run *refuse*, which is product behaviour nobody
#: accepted. The deviation is removed rather than legitimised with an invented
#: identifier: the scan is bounded per statement instead of bounded in total, so
#: every active member is considered whatever the guild's size, and this value
#: changes only how many round trips that takes. No refusal, no truncation and no
#: resolution depends on it, and `test_the_scan_batch_changes_no_outcome` is the
#: assertion of that rather than this sentence.
MEMBERSHIP_SCAN_BATCH = 500


class IdentityEvidenceRunService:
    """C-04: the only reader of the Sheet, and the only writer of a run.

    The tool is a command-line adapter — it parses arguments, reads two Sheet
    ranges through the read-only boundary, prints counts and chooses an exit code.
    Everything that decides anything is here, which is what makes C-04's behaviour
    testable without Google credentials.

    ## One run, and it authorizes nothing

    `python -m tools.identity_migration --dry-run --player-tab Players` produces
    **the** durable proposal set Council decides. It writes
    `identity_migration_runs`, `identity_link_proposals` and
    `identity_link_proposal_candidates`, and it can write nothing else: this
    service holds no `CharacterAccessService`, no access repository and no audit
    repository, so "C-04 creates no authorization" is a fact about what it can
    reach rather than a promise about what it calls. The database says the same
    thing independently — `identity_link_proposals.granted_access_id` is
    `CHECK`-ed null on every row this service can write.

    ## It is temporary

    C-04 is a migration/import utility with an end date (§7.7). It is the only
    thing in Phase 3 that reads Google, it reads only the identity-evidence
    columns, it never writes Google, and it runs from a separate operator
    environment that holds the Google client libraries and a read-only
    credential — not from the portal runtime, which has neither and needs
    neither.
    """

    __slots__ = ("_sources", "_proposals", "_guild_id", "_scan_batch")

    def __init__(
        self,
        *,
        sources,
        proposals,
        guild_id: int,
        scan_batch: int = MEMBERSHIP_SCAN_BATCH,
    ) -> None:
        self._sources = sources
        self._proposals = proposals
        self._guild_id = guild_id
        self._scan_batch = scan_batch

    def run(
        self,
        *,
        sheet_character_rows,
        sheet_players,
        sheet_tab: str,
        source_label: str,
        profile_version: str,
        correlation_id: UUID,
        now: datetime,
    ) -> RunOutcome:
        """Resolve the Sheet's evidence and persist the run. One transaction.

        The transaction is the **caller's** — the tool opens it — so the run row,
        every proposal and every candidate commit together or not at all. An
        injected failure part-way through therefore leaves no run at all rather
        than a run whose totals describe proposals that were never written, which
        is what makes a rerun after a crash produce a whole run rather than a
        second half of one. A `DuplicatePlayerNames` or `UnmappedSourceRows`
        refusal reaches the caller the same way and with the same consequence:
        the transaction has written nothing it will not roll back.
        """
        source_rows = tuple(sheet_character_rows)
        players = tuple(sheet_players)

        mapped = self._sources.character_ids_for_sheet_rows(
            sheet_tab=sheet_tab,
            row_indexes=(row.row_number for row in source_rows),
        )
        unmapped = sum(1 for row in source_rows if row.row_number not in mapped)
        if unmapped:
            raise UnmappedSourceRows(unmapped, sheet_tab)

        characters = tuple(
            SheetCharacter(
                character_id=mapped[row.row_number][0],
                display_name=mapped[row.row_number][1],
                player_name=row.player_name,
            )
            for row in source_rows
        )

        resolutions, totals = resolve(
            sheet_characters=characters,
            sheet_players=players,
            guild_members=self._matching_members(players),
            already_linked=self._sources.active_links(
                character.character_id for character in characters
            ),
        )

        run_id = self._proposals.create_run(
            source_label=source_label,
            profile_version=profile_version,
            source_characters=totals.source_characters,
            source_players=totals.source_players,
            already_linked=totals.already_linked,
            proposed=totals.proposed,
            ambiguous=totals.ambiguous,
            unresolved=totals.unresolved,
            correlation_id=correlation_id,
            at=now,
        )

        candidates_written = 0
        for resolution in resolutions:
            self._proposals.add_proposal(
                run_id=run_id,
                character_id=resolution.character.character_id,
                sheet_player_name=resolution.character.player_name,
                sheet_discord_name=(
                    resolution.player.discord_name if resolution.player else None
                ),
                # Evidence, recorded because §7.1 says it is reconciliation
                # evidence, and consulted by nothing: no capability anywhere in
                # this package reads it (OD-18).
                active_dm=bool(resolution.player.active_dm if resolution.player else False),
                proposed_subject=resolution.subject,
                resolution=resolution.resolution,
                candidates=resolution.candidates,
                correlation_id=correlation_id,
            )
            candidates_written += len(resolution.candidates)

        return RunOutcome(
            run_id=run_id,
            correlation_id=correlation_id,
            totals=totals,
            proposals_written=len(resolutions),
            candidates_written=candidates_written,
        )

    def _matching_members(self, players) -> tuple[GuildMember, ...]:
        """Every active member whose username could match a Sheet Discord name.

        The projection is streamed in keyset batches and filtered here, so no
        statement reads an unbounded row set and nothing in memory grows with the
        guild — only with the number of members the Sheet's names actually reach.

        The filter cannot change a resolution. `resolve()` indexes members by
        `DisplayName.identity_key` and looks each Sheet Discord name up in that
        index, so a member whose key is not one of the keys being looked up is
        unreachable by construction; dropping it here removes a row the resolver
        would never have consulted. Crucially the comparison is *still*
        `domain.names.DisplayName` and nothing else — pushing the match into SQL
        would have meant a second, subtly different implementation of "are these
        the same name?", which §7.3 forbids for exactly the reason it matters
        here: the second copy would be wrong in the direction of linking two
        people.
        """
        wanted = frozenset(
            DisplayName(player.discord_name).identity_key
            for player in players
            if (player.discord_name or "").strip()
        )
        if not wanted:
            return ()
        return tuple(
            GuildMember(
                subject=str(member["id"]),
                username=member["username"] or "",
                global_name=member["global_name"],
            )
            for member in self._sources.iter_active_guild_members(
                guild_id=self._guild_id, batch=self._scan_batch
            )
            if DisplayName(member["username"] or "").identity_key in wanted
        )


class NotConfirmable(WebRefusal):
    """An `ambiguous`, `unresolved` or already-decided proposal cannot be confirmed.

    `409` rather than `422`: the caller submitted a well-formed request against a
    proposal whose state does not admit it, and the answer is the current state
    (VM-19) rather than a field-level correction.
    """

    def __init__(self, correlation_id: UUID | None = None) -> None:
        super().__init__(
            RefusalCode.STALE_VERSION, status=409, correlation_id=correlation_id
        )


class AlreadyLinked(WebRefusal):
    """The proposal's account already holds an active link to its character.

    `409` with the current state, and never an overwrite. Reached when a link
    appears between the C-04 run that proposed it and the Council member
    confirming it — through R-25, through another proposal for the same pair, or
    through a concurrent confirmation of this one. The desired end state already
    holds, so refusing costs nothing and *not* refusing would mean either a
    duplicate active link — which
    `uq_character_access_one_active_link_account` refuses anyway, as an integrity
    error rather than a sentence a Council member can act on — or a silent
    widening of an existing grant.

    Distinct from `NotConfirmable` because it is a different fact about a
    different row, and a Council member reading VM-19 should be able to tell
    "somebody decided this" from "this person already has access".
    """

    def __init__(self, correlation_id: UUID | None = None) -> None:
        super().__init__(
            RefusalCode.DUPLICATE_ACTIVE_MAPPING,
            status=409,
            correlation_id=correlation_id,
        )


class IdentityMigrationService:
    """R-28, R-29 and R-30. A confirmation **is** the activation.

    Council-only at the route; the service takes the resolved context and calls
    `require_council()` itself, because a service that trusts its caller to have
    checked is a service with one caller that forgot. The context is a *live*
    resolution of the confirming member's current Discord roles, taken on this
    request — never a durable claim recorded earlier and never anything the
    browser supplied.

    ## What `confirm()` does, in one transaction

    1. resolves the target platform account **server-side** from the snowflake
       C-04 recorded — nothing about the target arrives in the request;
    2. takes the character's optimistic version, refusing `409` if it moved;
    3. writes the `character_access` row and the `character_access.granted`
       audit event through `CharacterAccessService.grant()`, the one R-25 uses;
    4. moves the proposal to `confirmed`, conditionally on it still being
       outstanding, recording the decider, the reason and the access row it
       produced; and
    5. writes the `identity_migration.confirmed` audit event.

    All five are in the caller's transaction. Nothing here catches anything, so a
    failure in any of them rolls back all of them: no link, no decision, no
    version bump, no audit. `reject()` does 4 and 5 only, and can reach no grant
    at all.

    ## Three independent controls stop a second durable effect

    Two Council members confirming the same proposal at the same moment, or one
    double-submitting, meet all of: the conditional version bump inside `grant()`
    (the loser matches zero rows and is refused before writing anything),
    `uq_character_access_one_active_link_account`, and `decide()`'s conditional
    update on the proposal still being outstanding. None of them is the only one.
    """

    __slots__ = (
        "_proposals",
        "_access_service",
        "_access",
        "_accounts",
        "_audit",
        "_cursor_key",
    )

    def __init__(
        self, *, proposals, access_service, access, accounts, audit, cursor_key
    ) -> None:
        self._proposals = proposals
        self._access_service = access_service
        self._access = access
        self._accounts = accounts
        self._audit = audit
        self._cursor_key = cursor_key

    # -- R-28 -------------------------------------------------------------
    def overview(
        self,
        context: WebAuthorizationContext,
        *,
        cursor_token: str | None,
        csrf_token: str,
        size: int = PAGE_SIZE_DEFAULT,
    ) -> IdentityMigrationView:
        """The latest run, its proposals and §7.4's control totals.

        The totals are shown to the person doing the confirming rather than only
        in a report they may not read, and `MigrationTotals.balances()` is
        arithmetic the view can be asked about rather than a claim in prose.

        Four **decision** states and no fifth (VM-10): outstanding proposed
        evidence, ambiguous/unresolved evidence, confirmed proposals, and
        rejected proposals. There is nothing between a confirmation and the
        access row it creates, so there is no "confirmed but not applied" row to
        render and no apply total to report.

        A confirmed proposal additionally reports whether the access row **it**
        created is active now (C-P3.2-C). That is not a fifth decision state: the
        decision is immutable and stays `confirmed`, while R-26 revocation is a
        compensating action on a different row (§7.5). Reading it takes two
        bounded queries — one for the page, one for the run's totals — and it is
        read from the exact `granted_access_id`, so no other link on the same
        character or account can make a revoked confirmation read as active.
        """
        from application.web import pagination

        context.require_council()
        run = self._proposals.latest_run()
        if run is None:
            return IdentityMigrationView(
                state="empty",
                run=None,
                proposals=(),
                cursor=pagination.Page.of(
                    (), size=size, key=self._cursor_key, scope="proposals",
                    position=lambda row: (),
                ).cursor,
                # Named rather than nine zeroes in a row: a positional empty
                # state is exactly the constructor that goes wrong silently the
                # next time a field is added in the middle.
                totals=MigrationTotals(
                    source_characters=0,
                    source_players=0,
                    proposed=0,
                    ambiguous=0,
                    unresolved=0,
                    confirmed=0,
                    confirmed_revoked=0,
                    rejected=0,
                    already_linked=0,
                    outstanding=0,
                ),
                csrf_token=csrf_token,
            )

        after = pagination.decode(
            self._cursor_key, cursor_token, scope="proposals", arity=1
        )
        rows = self._proposals.proposals(
            run_id=run["id"],
            after=UUID(after[0]) if after else None,
            limit=size + 1,
        )
        page = Page.of(
            rows,
            size=size,
            key=self._cursor_key,
            scope="proposals",
            position=lambda row: (str(row["id"]),),
        )
        candidates = self._proposals.candidates_for(
            [row["id"] for row in page.rows], limit=SMALL_LIST_BOUND
        )
        character_ids = [row["character_id"] for row in page.rows]
        summary = self._access.link_summary(character_ids)
        named = self._access.characters_by_id(character_ids)
        labels = self._accounts.labels_for(
            entry["owner_account_id"] for entry in summary.values()
        )
        decided = self._proposals.decision_counts(run["id"])
        # The current state of the exact access row each confirmation on **this
        # page** created, and the same question aggregated over the whole run.
        # Two queries rather than one because they answer different questions
        # about different row sets, and both are bounded: the first by the page,
        # the second by being an aggregate.
        link_states = self._proposals.granted_link_state(
            [row["id"] for row in page.rows]
        )
        links = self._proposals.confirmed_link_counts(run["id"])

        return IdentityMigrationView(
            state="ready" if page.rows else "empty",
            run=MigrationRun(
                run_id=run["id"],
                produced_at=Instant.of(run["produced_at"]),
                source_snapshot=run["source_label"],
                dry_run=run["dry_run"],
                profile_version=run["profile_version"],
            ),
            proposals=tuple(
                self._proposal_view(
                    row, candidates, summary, labels, named, link_states
                )
                for row in page.rows
            ),
            cursor=page.cursor,
            totals=MigrationTotals(
                source_characters=run["source_characters"],
                source_players=run["source_players"],
                proposed=run["proposed"],
                ambiguous=run["ambiguous"],
                unresolved=run["unresolved"],
                # §7.4's sentence, unchanged: `confirmed` counts proposals that
                # are **active links**. A confirmation Council has since revoked
                # is counted beside it rather than inside it, so the total a
                # Council member reads as "links this run produced" is the
                # number of links that exist.
                confirmed=links["active"],
                confirmed_revoked=links["revoked"],
                rejected=decided.get("rejected", 0),
                already_linked=run["already_linked"],
                outstanding=sum(
                    decided.get(state, 0)
                    for state in (PROPOSED, AMBIGUOUS, UNRESOLVED)
                ),
            ),
            csrf_token=csrf_token,
        )

    # -- R-29 -------------------------------------------------------------
    def confirm(
        self,
        *,
        context: WebAuthorizationContext,
        proposal_id: UUID,
        reason: str,
        expected_version: int,
        correlation_id: UUID,
        now: datetime,
    ) -> UUID:
        """Create the link this proposal names. One transaction, or nothing.

        Migration contract §7.2 as the maintainer ruled it (OD-46): the
        confirmation is the activation. The `character_access` row is written
        here, through `CharacterAccessService.grant()` — R-25's own service, not
        a second implementation — under the confirming member's live Council
        authority, together with the proposal's `confirmed` transition and both
        audit events.

        Every fact the write depends on is resolved **server-side**: the subject
        is the snowflake C-04 recorded on the proposal, the platform account is
        resolved from that snowflake, the access kind is
        `CONFIRMED_ACCESS_KIND`, and the granting authority is `context`. The
        request supplies a proposal id, a reason and the character's version, and
        nothing else has a parameter here to arrive through.

        An `ambiguous` or `unresolved` proposal is refused here **and** cannot be
        expressed: `proposed_subject` is null on both, so there is no snowflake
        to link even if this check were removed (TC-MIG-10). A proposal already
        decided is refused too, twice — once by the state check and once by
        `decide()`'s conditional update, which is the control that holds when two
        Council members act in the same instant.

        `expected_version` is the character's optimistic version, exactly as
        R-25's grant takes it. A confirmation now changes the character, so a
        page rendered before somebody else's change must not be applied on top of
        it: the bump is conditional and its loser is refused `409` with the
        current state, before it has written anything at all.
        """
        context.require_council()
        text = (reason or "").strip()
        if not text or len(text) > REASON_BOUND:
            raise BlankReason(correlation_id)

        row = self._decidable(proposal_id, correlation_id)
        if row["resolution"] != PROPOSED or row["proposed_subject"] is None:
            raise NotConfirmable(correlation_id)

        subject = row["proposed_subject"]
        character_id = row["character_id"]
        # Resolved here as well as inside `grant()`, and deliberately: the
        # already-linked question below is about a *person*, and there is no
        # person to ask it about until the snowflake resolves to an account. A
        # snowflake with no account, or with no active identity, is refused as
        # unreachable — byte-identically to an unknown character, so a Council
        # member learns that this combination cannot be linked and not which half
        # of it the platform has never heard of.
        account_id = self._accounts.account_for_active_identity("discord", subject)
        if account_id is None:
            raise ObjectNotReachable(correlation_id)

        if self._access.access_for(
            character_id=character_id, account_id=account_id
        ) is not None:
            # The link appeared between the run and this confirmation. The end
            # state already holds; nothing is overwritten and nothing is widened.
            raise AlreadyLinked(correlation_id)

        change = self._access_service.grant(
            context=context,
            character_id=character_id,
            subject=subject,
            access_kind=CONFIRMED_ACCESS_KIND,
            reason=text,
            expected_version=expected_version,
            correlation_id=correlation_id,
            now=now,
        )

        if not self._proposals.decide(
            proposal_id=proposal_id,
            resolution="confirmed",
            account_id=context.account_id,
            reason=text,
            at=now,
            granted_access_id=change.access_id,
        ):
            # Somebody decided it between the read and the write. Raising rolls
            # the grant above back with everything else in this transaction,
            # which is why the conditional update is allowed to be the last
            # control rather than having to be the first.
            raise NotConfirmable(correlation_id)

        self._audit.record(
            self._event(
                "identity_migration.confirmed",
                proposal_id,
                context,
                correlation_id,
                {
                    "character_id": str(character_id),
                    "proposed_subject": subject,
                    "reason": text,
                    "run_id": str(row["run_id"]),
                    "access_kind": CONFIRMED_ACCESS_KIND,
                    # The row this confirmation created, named in the decision's
                    # own event so an audit reader does not have to correlate two
                    # events to answer "what did this confirmation authorize?".
                    "granted_access_id": str(change.access_id),
                    "platform_account_id": str(change.account_id),
                    "character_version": change.character_version,
                },
            )
        )
        return proposal_id

    # -- R-30 -------------------------------------------------------------
    def reject(
        self,
        *,
        context: WebAuthorizationContext,
        proposal_id: UUID,
        reason: str,
        correlation_id: UUID,
        now: datetime,
    ) -> UUID:
        """Record that this proposal will not become a link. Durable and audited.

        A rejection only, and it never creates a link: it passes no
        `granted_access_id` to `decide()`, and
        `ck_identity_link_proposals_a_confirmation_is_a_link` refuses a rejected
        row that carries one, so the property holds against an edit here as well
        as against this code.

        Any outstanding resolution may be rejected, including `ambiguous` and
        `unresolved`: rejecting one is how a Council member says *"there is
        nothing here"* and stops it appearing in the outstanding count for ever.
        It changes no character, so it takes no version.
        """
        context.require_council()
        text = (reason or "").strip()
        if not text or len(text) > REASON_BOUND:
            raise BlankReason(correlation_id)

        row = self._decidable(proposal_id, correlation_id)
        if not self._proposals.decide(
            proposal_id=proposal_id,
            resolution="rejected",
            account_id=context.account_id,
            reason=text,
            at=now,
            granted_access_id=None,
        ):
            raise NotConfirmable(correlation_id)

        self._audit.record(
            self._event(
                "identity_migration.rejected",
                proposal_id,
                context,
                correlation_id,
                {
                    "character_id": str(row["character_id"]),
                    "previous_resolution": row["resolution"],
                    "reason": text,
                    "run_id": str(row["run_id"]),
                    "granted_access_id": None,
                },
            )
        )
        return proposal_id

    # -- helpers ----------------------------------------------------------
    def _decidable(self, proposal_id: UUID, correlation_id: UUID):
        """The proposal, if it exists and belongs to a run.

        The refusal is `409` rather than `404` where the *state* is wrong: the
        proposal exists and the caller is entitled to know its state, which is
        what VM-19 answers with. A proposal that does not exist, or whose run
        does not, is `404` — the same answer an unreachable object gets
        everywhere else on this surface.
        """
        row = self._proposals.proposal(proposal_id)
        if row is None:
            raise ObjectNotReachable(correlation_id)
        if self._proposals.run(row["run_id"]) is None:
            raise ObjectNotReachable(correlation_id)
        if not self._proposals.is_latest_run(row["run_id"]):
            # Old runs remain durable evidence, but a newer C-04 run supersedes
            # their authority to create a link. The repository repeats this in
            # the conditional decision update so a run committed after this read
            # still rolls back the entire confirmation.
            raise NotConfirmable(correlation_id)
        return row

    def _proposal_view(
        self, row, candidates, summary, labels, named, link_states
    ) -> LinkProposal:
        from application.web.characters import _actor
        from application.web.view_models import CouncilCharacterRow

        entry = summary.get(
            row["character_id"], {"active_links": 0, "owner_account_id": None}
        )
        owner_id = entry["owner_account_id"]
        character_row = named.get(row["character_id"])
        character = CouncilCharacterRow(
            character_id=row["character_id"],
            display_name=SafeText.bounded(
                character_row["display_name"] if character_row else "",
                ACTOR_NAME_BOUND,
            ),
            level=character_row["level"] if character_row else None,
            active=bool(character_row["active"]) if character_row else False,
            active_owner=_actor(owner_id, labels) if owner_id else None,
            active_link_count=entry["active_links"],
            unresolved_owner=owner_id is None,
            links_path=f"/v1/council/characters/{row['character_id']}/links",
        )
        # `candidates` maps a proposal to `(bounded subjects, true total)`. The
        # bound is applied twice — once in SQL so the query cannot read an
        # unbounded child set, and once here so the view type's own limit is this
        # module's statement rather than the repository's — and the count comes
        # from the database, so it is the number of rows that exist rather than
        # the number this page received.
        listed_subjects, candidate_count = candidates.get(row["id"], ((), 0))
        listed, truncated = bounded_tuple(listed_subjects, SMALL_LIST_BOUND)
        return LinkProposal(
            proposal_id=row["id"],
            character=character,
            # The version the confirm form submits, so a character that moved
            # under the page is refused rather than linked on top of somebody
            # else's change. `0` only when the character row is missing, in which
            # case the proposal is unconfirmable anyway and the grant would
            # refuse the character as unreachable.
            character_version=character_row["version"] if character_row else 0,
            sheet_player_name=SafeText.bounded(
                row["sheet_player_name"], DISCORD_NAME_BOUND
            ),
            sheet_discord_name=(
                SafeText.bounded(row["sheet_discord_name"], DISCORD_NAME_BOUND)
                if row["sheet_discord_name"]
                else None
            ),
            active_dm_flag=row["active_dm"],
            proposed_subject=row["proposed_subject"],
            resolution=row["resolution"],
            candidate_subjects=listed,
            # True when either half of the bound bit: the SQL returned more than
            # it shows, or this tuple was longer than `SMALL_LIST_BOUND`.
            candidate_subjects_truncated=truncated or candidate_count > len(listed),
            candidate_count=candidate_count,
            # What a confirmation would create, shown before it is created. Fixed
            # by the service, and the form carries no field for it.
            resulting_access_kind=CONFIRMED_ACCESS_KIND,
            # `false` for every ambiguous and unresolved row and for every row
            # already decided. The server refuses each of those regardless of
            # what the browser submits; this is the honest rendering, not the
            # control.
            confirmable=row["resolution"] == PROPOSED,
            decided=row["decided_at"] is not None,
            # The current state of **this** proposal's own access row. Keyed by
            # the proposal, so the lookup cannot reach another link: a proposal
            # that created none is absent from the map and stays `None`, and the
            # page therefore never claims a link is active because some other
            # link on the same character is.
            link_state=(
                None
                if row["id"] not in link_states
                else ("active" if link_states[row["id"]] else "revoked")
            ),
        )

    @staticmethod
    def _event(
        action: str,
        proposal_id: UUID,
        context: WebAuthorizationContext,
        correlation_id: UUID,
        payload: dict,
    ) -> AuditEvent:
        return AuditEvent(
            action=action,
            entity_type="identity_link_proposal",
            entity_id=str(proposal_id),
            source=AuditSource.WEB,
            actor_capability=ActorCapability.GUILD_COUNCIL,
            correlation_id=correlation_id,
            actor_platform_account_id=context.account_id,
            payload=payload,
        )


__all__ = [
    "ALREADY_LINKED",
    "AMBIGUOUS",
    "AlreadyLinked",
    "CONFIRMED_ACCESS_KIND",
    "DuplicatePlayerNames",
    "GuildMember",
    "IdentityEvidenceRunService",
    "IdentityMigrationService",
    "MEMBERSHIP_SCAN_BATCH",
    "NotConfirmable",
    "PROPOSED",
    "Resolution",
    "RunOutcome",
    "RunTotals",
    "SheetCharacter",
    "SheetCharacterRow",
    "SheetPlayer",
    "UNRESOLVED",
    "UnbalancedRun",
    "UnmappedSourceRows",
    "resolve",
]
