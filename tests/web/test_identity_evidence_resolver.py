"""The M-2 resolver, in isolation: determinism, totals, and durable ambiguity.

No database and no Sheet. `resolve()` is a pure function of four iterables, which
is what lets these cases be exhaustive about the two defects the P3.2 review found
and about the rules §7.3 states:

- **F5, traversal.** The function used to consume its iterables and then ask
  `len(tuple(...))` for the control totals. That is right for a list and silently
  wrong for a generator: the second traversal of an exhausted iterator yields
  nothing, so `source_characters` came out `0`, §7.4's balance was asserted against
  a consumed denominator, and the run either refused for the wrong reason or
  recorded a total nobody could reconcile. Every case below runs three times — over
  lists, over tuples, and over one-shot generators — and asserts the three produce
  **identical** resolutions and identical totals.
- **F4, ambiguity.** The ambiguous branch used to slice its candidate list to
  `SMALL_LIST_BOUND` before returning it, so the *durable* record of an ambiguity
  depended on a rendering bound and an eleventh matching member was dropped where
  nothing could recover it. §7.6 requires every candidate to persist.
- **The duplicate player name.** The player index was a dict comprehension keyed
  by the normalized player name, so two Sheet rows called `Ada` and `ADA`
  collided silently and **the later row** decided the confirmable Discord
  identity of every character naming that player. Sheet order is not a tie-break
  — it is a layout accident deciding who gets access. §7.3.1 now refuses the
  whole run, and the cases at the end of this module are where that is exhaustive
  about order, about case folding and about what the refusal is allowed to say.

`already_linked` is a set of `(character_id, subject)` **pairs**, because §7.3's
fifth row is "the character already has an active access row *for that account*" —
a property of the pair. A character owned by one person is still a proposal for a
second authorized user, which is the product invariant.
"""
from __future__ import annotations

from uuid import UUID, uuid4

import pytest

from application.web.identity_evidence import (
    AMBIGUOUS,
    PROPOSED,
    UNRESOLVED,
    DuplicatePlayerNames,
    GuildMember,
    RunTotals,
    SheetCharacter,
    SheetPlayer,
    UnbalancedRun,
    resolve,
)
from application.web.view_models import SMALL_LIST_BOUND

#: Synthetic and outside the range Discord has issued (delivery plan §10).
BASE_SUBJECT = 700000000000002000


def character(name: str, player: str, identifier: UUID | None = None) -> SheetCharacter:
    return SheetCharacter(
        character_id=identifier or uuid4(), display_name=name, player_name=player
    )


def player(name: str, discord_name: str | None, *, active_dm: bool = False) -> SheetPlayer:
    return SheetPlayer(player_name=name, discord_name=discord_name, active_dm=active_dm)


def member(offset: int, username: str) -> GuildMember:
    return GuildMember(
        subject=str(BASE_SUBJECT + offset), username=username, global_name=None
    )


# ---------------------------------------------------------------------------
# F5 — one traversal, three input shapes, identical answers
# ---------------------------------------------------------------------------

#: The shapes a caller may legitimately hand over. `iter(...)` is the one that
#: broke the totals, and it is deliberately a *one-shot* iterator rather than a
#: re-iterable object: the defect was a second traversal, so the fixture has to be
#: something a second traversal cannot succeed against.
SHAPES = {
    "list": list,
    "tuple": tuple,
    "generator": lambda items: (item for item in items),
}


def resolve_with(shape, *, characters, players, members, already_linked=()):
    build = SHAPES[shape]
    return resolve(
        sheet_characters=build(characters),
        sheet_players=build(players),
        guild_members=build(members),
        already_linked=build(already_linked),
    )


#: One scenario touching every bucket at once, so the equivalence cases below are
#: not equivalent about an empty problem.
def mixed_scenario():
    ids = [UUID(int=index + 1) for index in range(5)]
    characters = [
        character("Alia Storm", "Ada", ids[0]),          # proposed
        character("Brand Vale", "Bea", ids[1]),          # ambiguous: two matches
        character("Cere Ash", "Cyd", ids[2]),            # unresolved: no member
        character("Dain Rell", "Dot", ids[3]),           # unresolved: blank Discord name
        character("Esk Mire", "Ada", ids[4]),            # already linked to Ada's member
    ]
    players = [
        player("Ada", "ada.one"),
        player("Bea", "shared.name"),
        player("Cyd", "nobody.here"),
        player("Dot", None),
    ]
    members = [
        member(1, "ada.one"),
        member(2, "shared.name"),
        member(3, "shared.name"),
        member(4, "unrelated"),
    ]
    already = [(ids[4], str(BASE_SUBJECT + 1))]
    return characters, players, members, already, ids


@pytest.mark.parametrize("shape", sorted(SHAPES))
def test_every_input_shape_produces_the_same_resolutions_and_totals(shape):
    """F5. Lists, tuples and a one-shot generator are one answer, not three.

    The generator column is the regression: before the fix its `source_characters`
    was `0`, because the totals re-traversed an iterator the loop had already
    exhausted. The balance then failed and the run refused — with an arithmetic
    message about a denominator that had nothing to do with the Sheet.
    """
    characters, players, members, already, ids = mixed_scenario()
    resolutions, totals = resolve_with(
        shape,
        characters=characters,
        players=players,
        members=members,
        already_linked=already,
    )

    assert totals == RunTotals(
        source_characters=5,
        source_players=4,
        already_linked=1,
        proposed=1,
        ambiguous=1,
        unresolved=2,
    )
    assert totals.balances()
    assert [(row.character.character_id, row.resolution) for row in resolutions] == [
        (ids[0], PROPOSED),
        (ids[1], AMBIGUOUS),
        (ids[2], UNRESOLVED),
        (ids[3], UNRESOLVED),
    ]


def test_the_three_shapes_agree_with_each_other_exactly():
    """Stated as an equality between the shapes, not only against a literal.

    The case above pins each shape to the expected answer; this one pins the shapes
    to *each other*, so a change that altered all three consistently — a genuine
    behaviour change rather than a traversal defect — fails there and not here, and
    a change that altered only the lazy path fails here.
    """
    characters, players, members, already, _ids = mixed_scenario()
    answers = {
        shape: resolve_with(
            shape,
            characters=characters,
            players=players,
            members=members,
            already_linked=already,
        )
        for shape in SHAPES
    }
    reference = answers["list"]
    for shape, answer in answers.items():
        assert answer == reference, shape


@pytest.mark.parametrize("shape", sorted(SHAPES))
def test_empty_inputs_balance_at_zero(shape):
    """The trivially correct case, which the traversal defect also got wrong.

    An empty generator and an empty list must both give `source_characters = 0` and
    a balanced run. This one passed before the fix by coincidence — nothing to
    consume — and it is kept because it is the case an operator hits on a fresh
    database, and a run that refuses there would refuse for its whole first day.
    """
    resolutions, totals = resolve_with(
        shape, characters=[], players=[], members=[], already_linked=[]
    )
    assert resolutions == ()
    assert totals == RunTotals(0, 0, 0, 0, 0, 0)
    assert totals.balances()


@pytest.mark.parametrize("shape", sorted(SHAPES))
def test_source_players_counts_the_player_tab_and_not_the_join(shape):
    """`source_players` is "rows in the player tab" (§7.4), joined or not.

    A player nobody plays a character for still counts, and a player row counted
    only when it matched would make the source side of the report a function of the
    join — which is precisely the number the report exists to check.
    """
    identifier = UUID(int=9)
    _resolutions, totals = resolve_with(
        shape,
        characters=[character("Solo", "Ada", identifier)],
        players=[player("Ada", "ada.one"), player("Unused", "nobody"), player("Also", None)],
        members=[member(1, "ada.one")],
    )
    assert totals.source_players == 3
    assert totals.source_characters == 1
    assert totals.proposed == 1
    assert totals.balances()


# ---------------------------------------------------------------------------
# F4 — every ambiguous candidate persists
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("shape", sorted(SHAPES))
def test_an_ambiguity_wider_than_the_render_bound_returns_every_candidate(shape):
    """F4. `SMALL_LIST_BOUND + 5` matches, and the resolver returns all of them.

    The bound is a *rendering* bound. Applying it here truncated the durable record
    of an ambiguity: a Council member reviewing the proposal was shown ten
    candidates and told nothing about the rest, and the dropped ones were not
    recoverable from the run at all. §7.6 requires the ambiguity to persist as a
    record naming every candidate, and the number that must appear here is
    therefore the true one.
    """
    identifier = UUID(int=11)
    width = SMALL_LIST_BOUND + 5
    members = [member(offset, "shared.name") for offset in range(width)]
    resolutions, totals = resolve_with(
        shape,
        characters=[character("Wide", "Ada", identifier)],
        players=[player("Ada", "shared.name")],
        members=members,
    )

    (row,) = resolutions
    assert row.resolution == AMBIGUOUS
    # Nothing is chosen, and there is nothing for a confirmation to link to.
    assert row.subject is None
    assert len(row.candidates) == width
    assert len(set(row.candidates)) == width
    assert {subject for subject, _username in row.candidates} == {
        member.subject for member in members
    }
    # Sorted, so two runs over the same evidence write the same rows in the same
    # order — the deterministic half of §7.5's idempotency.
    assert list(row.candidates) == sorted(row.candidates)
    assert totals.ambiguous == 1
    assert totals.proposed == 0


def test_a_two_way_ambiguity_chooses_neither_and_lists_both():
    identifier = UUID(int=12)
    resolutions, _totals = resolve(
        sheet_characters=[character("Pair", "Ada", identifier)],
        sheet_players=[player("Ada", "shared.name")],
        guild_members=[member(1, "shared.name"), member(2, "SHARED.NAME")],
        already_linked=(),
    )
    (row,) = resolutions
    # Case-folded comparison is the point: two members whose usernames differ only
    # in case are the *same* claim about a name, so they are an ambiguity rather
    # than one match and one miss.
    assert row.resolution == AMBIGUOUS
    assert row.subject is None
    assert len(row.candidates) == 2


# ---------------------------------------------------------------------------
# §7.3's resolution table, row by row
# ---------------------------------------------------------------------------


def test_one_match_proposes_that_snowflake_and_nothing_else():
    identifier = UUID(int=21)
    resolutions, _totals = resolve(
        sheet_characters=[character("Alia", "Ada", identifier)],
        sheet_players=[player("Ada", "Ada.One")],
        # NFC-normalised, case-folded comparison through `domain.names`, so the
        # Sheet's capitalisation is not a second identity.
        guild_members=[member(1, "ada.one"), member(2, "someone.else")],
        already_linked=(),
    )
    (row,) = resolutions
    assert row.resolution == PROPOSED
    assert row.subject == str(BASE_SUBJECT + 1)
    assert row.candidates == ((str(BASE_SUBJECT + 1), "ada.one"),)


@pytest.mark.parametrize(
    ("players_", "members_", "why"),
    [
        ([], [member(1, "ada.one")], "no player row joins this character"),
        ([("Ada", None)], [member(1, "ada.one")], "the player's Discord cell is blank"),
        ([("Ada", "   ")], [member(1, "ada.one")], "the cell holds only whitespace"),
        ([("Ada", "ada.one")], [], "the guild holds nobody at all"),
        ([("Ada", "ada.one")], [member(1, "someone.else")], "no member's username matches"),
    ],
)
def test_every_way_of_determining_nothing_lands_in_unresolved(players_, members_, why):
    """One bucket for "the platform can determine nothing", deliberately.

    Inventing a distinction between *"no player row"*, *"a blank cell"* and *"no
    matching member"* would suggest one of them is closer to an answer than the
    others. None of them is: each is a row a Council member must resolve by hand.
    """
    identifier = UUID(int=22)
    resolutions, totals = resolve(
        sheet_characters=[character("Alia", "Ada", identifier)],
        sheet_players=[player(name, discord) for name, discord in players_],
        guild_members=members_,
        already_linked=(),
    )
    (row,) = resolutions
    assert row.resolution == UNRESOLVED, why
    assert row.subject is None
    assert row.candidates == ()
    assert totals.unresolved == 1


def test_already_linked_is_a_pair_and_not_a_character():
    """§7.3's fifth row: *for that account*.

    The same character is `already_linked` for the person who holds the link and
    still `proposed` for a second person the Sheet names — which is the product
    invariant that a character may have several explicitly authorized users. Keying
    the bucket on the character alone would have silently refused to propose the
    second one, and a Council member would never have seen the row.
    """
    identifier = UUID(int=23)
    first, second = str(BASE_SUBJECT + 1), str(BASE_SUBJECT + 2)

    _resolutions, totals = resolve(
        sheet_characters=[character("Alia", "Ada", identifier)],
        sheet_players=[player("Ada", "ada.one")],
        guild_members=[member(1, "ada.one")],
        already_linked=[(identifier, first)],
    )
    assert totals.already_linked == 1
    assert totals.proposed == 0
    assert totals.balances()

    # Same character, same evidence, but the existing link belongs to somebody the
    # Sheet does not name. The Sheet's person is still a proposal.
    resolutions, totals = resolve(
        sheet_characters=[character("Alia", "Ada", identifier)],
        sheet_players=[player("Ada", "ada.one")],
        guild_members=[member(1, "ada.one")],
        already_linked=[(identifier, second)],
    )
    assert totals.already_linked == 0
    assert totals.proposed == 1
    assert resolutions[0].subject == first


def test_an_already_linked_character_writes_no_proposal_row():
    """Counted, not proposed. The distinction is what makes a rerun idempotent."""
    identifier = UUID(int=24)
    resolutions, totals = resolve(
        sheet_characters=[character("Alia", "Ada", identifier)],
        sheet_players=[player("Ada", "ada.one")],
        guild_members=[member(1, "ada.one")],
        already_linked=[(identifier, str(BASE_SUBJECT + 1))],
    )
    assert resolutions == ()
    assert totals.already_linked == 1
    assert totals.balances()


def test_an_ambiguous_row_is_never_silently_narrowed_by_an_existing_link():
    """An existing link does not resolve an ambiguity; it is not a vote.

    A character already linked to one of several same-named candidates stays
    ambiguous for a *different* Sheet claim, because the pair test only fires when
    the resolver produced exactly one match. There is no branch in which an
    existing link picks a candidate.
    """
    identifier = UUID(int=25)
    resolutions, totals = resolve(
        sheet_characters=[character("Alia", "Ada", identifier)],
        sheet_players=[player("Ada", "shared.name")],
        guild_members=[member(1, "shared.name"), member(2, "shared.name")],
        already_linked=[(identifier, str(BASE_SUBJECT + 1))],
    )
    (row,) = resolutions
    assert row.resolution == AMBIGUOUS
    assert row.subject is None
    assert totals.already_linked == 0


def test_a_blank_player_name_row_cannot_reach_the_resolver_balanced_or_not():
    """A `Characters` row with a blank column C is not a source row (§7.4).

    The Sheet adapter filters it out, and this case states what the resolver does
    if one arrives anyway: it matches no player row, so it is `unresolved` and the
    balance still holds. Neither layer can turn it into a proposed link.
    """
    identifier = UUID(int=26)
    resolutions, totals = resolve(
        sheet_characters=[character("Nameless", "", identifier)],
        sheet_players=[player("Ada", "ada.one")],
        guild_members=[member(1, "ada.one")],
        already_linked=(),
    )
    assert resolutions[0].resolution == UNRESOLVED
    assert totals.balances()


def test_a_blank_player_row_is_not_a_join_target():
    """A player row with no name in column A joins nothing.

    It is excluded from the join index — a blank key would otherwise match every
    character whose column C is also blank, linking people by the absence of a
    name, which is the worst available form of "linking by name".
    """
    identifier = UUID(int=27)
    resolutions, _totals = resolve(
        sheet_characters=[character("Nameless", "", identifier)],
        sheet_players=[player("   ", "ada.one")],
        guild_members=[member(1, "ada.one")],
        already_linked=(),
    )
    assert resolutions[0].resolution == UNRESOLVED


def test_an_unbalanced_run_is_a_refusal_and_not_a_warning():
    """`RunTotals.balances()` is arithmetic, and the resolver refuses when it fails.

    The resolver's own totals cannot disagree — it counts what it produced — so the
    check is exercised through `RunTotals` directly, and the database enforces the
    same rule for every writer through
    `ck_identity_migration_runs_buckets_balance_against_source`. Two controls, and
    this is the legible one.
    """
    assert not RunTotals(5, 2, 1, 1, 1, 1).balances()
    assert RunTotals(4, 2, 1, 1, 1, 1).balances()
    assert issubclass(UnbalancedRun, Exception)


# ---------------------------------------------------------------------------
# §7.3.1 — a duplicate player name refuses the whole run (TC-MIG-17)
# ---------------------------------------------------------------------------

#: Pairs that are one key under `DisplayName.identity_key`, which is the
#: comparison the resolver matches with — so anything that treats them as two
#: people is using a different rule than the one that decides identity.
#:
#: Surrounding whitespace is deliberately **not** one of these pairs.
#: `identity_key` normalizes and case-folds but does not trim, and the duplicate
#: check uses that one shared policy rather than a second, slightly different
#: answer to "are these the same name?" (§7.3). It does not matter in practice:
#: `adapters/sheets/identity_evidence.py` strips every cell it reads, on both
#: sides of the join, so a padded name never reaches here from C-04.
DUPLICATE_PAIRS = {
    "exact": ("Ada", "Ada"),
    "case_folded": ("Ada", "ADA"),
    "upper_and_lower": ("ADA", "ada"),
}


@pytest.mark.parametrize("case", sorted(DUPLICATE_PAIRS))
@pytest.mark.parametrize("reversed_order", [False, True])
def test_a_duplicate_player_name_refuses_the_run_in_either_row_order(
    case, reversed_order
):
    """The defect, and the whole shape of its fix.

    Two player rows share one key and carry **different** Discord names, so under
    the old dict comprehension the answer depended on which came second. Both
    orders are run and both refuse identically — the assertion is not "it refuses"
    but "the two orders agree", because disagreement was the defect.
    """
    first, second = DUPLICATE_PAIRS[case]
    identifier = uuid4()
    players = [player(first, "ada.one"), player(second, "cyd.two")]
    if reversed_order:
        players.reverse()

    with pytest.raises(DuplicatePlayerNames) as refusal:
        resolve(
            sheet_characters=[character("Alia", first, identifier)],
            sheet_players=players,
            guild_members=[member(1, "ada.one"), member(2, "cyd.two")],
            already_linked=(),
        )
    assert refusal.value.duplicate_keys == 1
    assert refusal.value.rows_involved == 2


def test_duplicates_carrying_the_same_discord_name_refuse_too():
    """Order-independence is not the only reason to refuse.

    Two rows naming one player with the same Discord name resolve the same way
    whichever is second, so the ordering argument alone would let them through.
    They are still two claims to one key: the platform cannot tell whether that
    is one person entered twice or two people the spreadsheet cannot distinguish,
    and a run that guessed would be guessing about a person.
    """
    with pytest.raises(DuplicatePlayerNames):
        resolve(
            sheet_characters=[character("Alia", "Ada", uuid4())],
            sheet_players=[player("Ada", "ada.one"), player("ADA", "ada.one")],
            guild_members=[member(1, "ada.one")],
            already_linked=(),
        )


def test_the_refusal_is_raised_before_any_character_is_examined():
    """It depends on the player set, and on nothing else.

    No character names the duplicated player here — one names nobody at all — and
    the run still refuses. A check that ran per character would pass this case and
    then fail the next spreadsheet, which is the difference between refusing a
    source-integrity defect and refusing the rows that happen to trip over it.
    """
    with pytest.raises(DuplicatePlayerNames):
        resolve(
            sheet_characters=[],
            sheet_players=[player("Ada", "ada.one"), player("ADA", "cyd.two")],
            guild_members=[],
            already_linked=(),
        )


def test_the_refusal_counts_every_colliding_key_not_only_the_first():
    """An operator fixing one duplicate per run is an operator making many passes.

    Two colliding keys across four rows, plus one row that collides with nothing,
    and the counts describe the whole problem.
    """
    with pytest.raises(DuplicatePlayerNames) as refusal:
        resolve(
            sheet_characters=[],
            sheet_players=[
                player("Ada", "ada.one"),
                player("ADA", "cyd.two"),
                player("Bea", "bea.three"),
                player("bea", "bea.four"),
                player("Cyd", "cyd.five"),
            ],
            guild_members=[],
            already_linked=(),
        )
    assert refusal.value.duplicate_keys == 2
    assert refusal.value.rows_involved == 4


def test_the_refusal_names_counts_and_no_personal_data():
    """Its message reaches an operator's terminal, shell history and CI log.

    The remedy — resolve the duplicate in the source spreadsheet — needs a count
    and not a name, and the player tab's contents are personal data that belongs
    behind Council authorization at R-28.
    """
    with pytest.raises(DuplicatePlayerNames) as refusal:
        resolve(
            sheet_characters=[],
            sheet_players=[player("Ada", "ada.one"), player("ADA", "cyd.two")],
            guild_members=[],
            already_linked=(),
        )
    message = str(refusal.value)
    assert "1 player name(s) appear on more than one player-tab row" in message
    assert "Nothing was written." in message
    for secret in ("Ada", "ADA", "ada.one", "cyd.two"):
        assert secret not in message, secret


def test_distinct_player_names_are_not_a_duplicate():
    """The refusal is narrow: it fires on one key held twice, and not otherwise.

    A guard that refused a working spreadsheet would be replaced by whoever had to
    run the migration, so the negative case is asserted beside the positives.
    """
    identifier = uuid4()
    resolutions, totals = resolve(
        sheet_characters=[character("Alia", "Ada", identifier)],
        sheet_players=[player("Ada", "ada.one"), player("Adam", "cyd.two")],
        guild_members=[member(1, "ada.one"), member(2, "cyd.two")],
        already_linked=(),
    )
    assert resolutions[0].resolution == PROPOSED
    assert resolutions[0].subject == str(BASE_SUBJECT + 1)
    assert totals.source_players == 2


def test_blank_player_names_are_not_keys_and_cannot_collide():
    """A blank name names nobody, so two of them are not two claims to one key.

    The player-tab parser already refuses a row with data and no name and skips a
    wholly blank spacer; this is the resolver's own belt, and it is why the
    duplicate check cannot make a spacer row into a refusal.
    """
    resolutions, totals = resolve(
        sheet_characters=[],
        sheet_players=[player("   ", "ada.one"), player("", "cyd.two")],
        guild_members=[],
        already_linked=(),
    )
    assert resolutions == ()
    assert totals.source_players == 2
