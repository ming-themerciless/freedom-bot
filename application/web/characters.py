"""Member and Council read paths: R-20, R-21, R-22, R-23, R-24 and R-31.

Queries, not commands. Nothing here writes, and the naming rule from
`.agents/AGENTS.md` is load-bearing rather than stylistic: a method named `for_`,
`detail` or `search` must not persist state, so a reviewer can tell from a call
site whether a request could have changed anything.

## Object authorization is below the route, and inside the read

R-21 is the single most substituted identifier in the product. Its authorization
is therefore not a check the handler performs before calling a loader — it is a
predicate **inside** the statement that reads the character:
`CharacterAccessRepository.access_for()` answers `None` for a character this
account may not reach and `None` for a character that does not exist, and the
service cannot tell those apart either. That is what makes the two `404`s
byte-identical rather than merely similar (route contract §2.3, TC-OBJ-07), and
it is why nothing below loads a character and then decides.

Council reach is the one exception, and it is role-derived: a Council member
reads any character with **no** `character_access` row existing for them (OD-37,
TC-OBJ-04). The view says so by leaving `viewer_access_kind` as `None`, which is
"not through an access row" and not "no access".

## Names are search and display facts, never identity

R-22's query and R-24's search both match on display names and both answer with
**stable ids** — a character UUID, a Discord snowflake. No caller downstream is
keyed by the string that matched, and there is no method here that turns a name
into an authorization. That is ADR 0006's *never by name matching* at the read
boundary (OD-42).

## Character detail is deliberately thin

Only Phase 2 identity/snapshot facts and fields whose typed database package is
already authoritative. Every other profile field renders `migration deferred`
with the package named in the controlled register — and cannot render a value,
because `MigrationDeferred` has no field to put one in. There is no generic state
representation here and no correction control anywhere, which is the acceptance
criterion *"no Phase 3 route or form mutates character game state"* seen from the
read side.
"""
from __future__ import annotations

from uuid import UUID

from application.audit import ActorCapability
from application.web.capabilities import WebAuthorizationContext
from application.web.errors import ObjectNotReachable
from application.web.pagination import Page
from application.web.view_models import (
    ACCESS_FACT_BOUND,
    ACTOR_NAME_BOUND,
    CHARACTER_LONG_NAME_BOUND,
    DISCORD_NAME_BOUND,
    FIELD_BOUND,
    HISTORICAL_ACCESS_BOUND,
    IDENTITY_CANDIDATE_BOUND,
    MY_CHARACTERS_BOUND,
    PROFILE_ROW_BOUND,
    REASON_BOUND,
    SMALL_LIST_BOUND,
    AccessFact,
    Actor,
    CharacterDetailView,
    CharacterFilters,
    CharacterLinksView,
    CharacterPortrait,
    CharacterSummary,
    CouncilCharacterIndexView,
    CouncilCharacterRow,
    Correlation,
    Cursor,
    FieldProfileView,
    IdentityCandidate,
    IdentitySearchResultsView,
    Instant,
    LinkInvariants,
    MigrationDeferred,
    MyCharactersView,
    ProfileFieldRow,
    ProfilePathRow,
    Provenance,
    SafeText,
    SnapshotField,
    SnapshotStamp,
    bounded_tuple,
)

#: R-24 returns the empty state rather than the whole guild for a query this
#: short. Two characters is not a search; it is a keystroke.
MINIMUM_SEARCH_LENGTH = 2
#: §3.2's bound on the search term, matching VM-09's `query_echo`.
SEARCH_QUERY_BOUND = 120


class CharacterQueryService:
    """Read-side use cases for the member and Council character screens."""

    __slots__ = ("_access", "_accounts", "_candidates", "_profile", "_cursor_key")

    def __init__(self, *, access, accounts, candidates, profile, cursor_key) -> None:
        self._access = access
        self._accounts = accounts
        self._candidates = candidates
        self._profile = profile
        self._cursor_key = cursor_key

    # -- R-20 -------------------------------------------------------------
    def my_characters(self, context: WebAuthorizationContext) -> MyCharactersView:
        """Exactly the caller's own active links, and their caller-specific default.

        `default_character_id` is read from *this account's* rows, so two people
        linked to one character each see their own default. The empty state is a
        fact rather than an error, and it offers no self-service control because
        ordinary users are read-only (OD-31).
        """
        rows = self._access.characters_for_account(
            context.account_id, limit=MY_CHARACTERS_BOUND + 1
        )
        visible, truncated = bounded_tuple(rows, MY_CHARACTERS_BOUND)
        summaries = tuple(self._summary(row) for row in visible)
        default_id = next(
            (row["id"] for row in visible if row["default_character"]), None
        )
        return MyCharactersView(
            state="ready" if summaries else "empty",
            characters=summaries,
            truncated=truncated,
            default_character_id=default_id,
        )

    # -- R-21 -------------------------------------------------------------
    def character_detail(
        self, context: WebAuthorizationContext, character_id: UUID
    ) -> CharacterDetailView:
        """One character, or `404` — and the `404` carries nothing about which.

        The authorization is resolved **before** the character row is read for
        anyone who is not Council, so an inaccessible identifier never causes the
        character to be loaded at all. A reader checking this can follow one
        path: no access row and no Council capability means the method raises
        before `character()` is called.
        """
        viewer_access = None
        if not context.guild_council:
            viewer_access = self._access.access_for(
                character_id=character_id, account_id=context.account_id
            )
            if viewer_access is None:
                raise ObjectNotReachable()

        character = self._access.character(character_id)
        if character is None:
            raise ObjectNotReachable()

        access_rows = self._access.active_links(character_id, limit=ACCESS_FACT_BOUND)
        labels = self._accounts.labels_for(
            [row["platform_account_id"] for row in access_rows]
            + [row["granted_by_account_id"] for row in access_rows]
        )
        access_facts, _ = bounded_tuple(
            (self._access_fact(row, labels, council=context.guild_council)
             for row in access_rows),
            ACCESS_FACT_BOUND,
        )

        provenance_row = self._access.provenance(character_id)
        snapshot_fields, deferred_fields = self._field_rows(character)

        return CharacterDetailView(
            state="ready",
            character_id=character["id"],
            display_name=SafeText.bounded(character["display_name"], ACTOR_NAME_BOUND),
            long_name=(
                SafeText.bounded(character["long_name"], CHARACTER_LONG_NAME_BOUND)
                if character["long_name"]
                else None
            ),
            level=character["level"],
            active=character["active"],
            version=character["version"],
            portrait=CharacterPortrait.for_name(character["display_name"]),
            access=access_facts,
            viewer_access_kind=(
                viewer_access["access_kind"] if viewer_access is not None else None
            ),
            snapshot_fields=snapshot_fields,
            deferred_fields=deferred_fields,
            provenance=self._provenance(provenance_row),
        )

    # -- R-22 -------------------------------------------------------------
    def council_index(
        self,
        context: WebAuthorizationContext,
        *,
        query: str | None,
        cursor_token: str | None,
        size: int,
        include_inactive: bool = False,
    ) -> CouncilCharacterIndexView:
        from application.web import pagination

        after = pagination.decode(
            self._cursor_key, cursor_token, scope="council-characters", arity=2
        )
        position = None
        if after is not None:
            position = (after[0], UUID(after[1]))

        term = (query or "").strip()[:SEARCH_QUERY_BOUND] or None
        rows = self._access.council_index(
            query=term,
            include_inactive=include_inactive,
            after=position,
            limit=size + 1,
        )
        page = Page.of(
            rows,
            size=size,
            key=self._cursor_key,
            scope="council-characters",
            position=lambda row: (row["display_name"], str(row["id"])),
        )
        summary = self._access.link_summary([row["id"] for row in page.rows])
        labels = self._accounts.labels_for(
            entry["owner_account_id"] for entry in summary.values()
        )
        return CouncilCharacterIndexView(
            state="ready" if page.rows else "empty",
            rows=tuple(self._council_row(row, summary, labels) for row in page.rows),
            cursor=page.cursor,
            filters=CharacterFilters(
                query=SafeText.bounded(term, SEARCH_QUERY_BOUND) if term else None,
                include_inactive=include_inactive,
            ),
        )

    # -- R-23 -------------------------------------------------------------
    def character_links(
        self,
        context: WebAuthorizationContext,
        character_id: UUID,
        *,
        cursor_token: str | None,
        csrf_token: str,
    ) -> CharacterLinksView:
        """One character's links, active and historical, with the invariants stated.

        `LinkInvariants` is why the confirmation copy can say what will happen
        before the Council member commits. The database still enforces every one
        of them; this explains one rather than replacing it.
        """
        from application.web import pagination

        character = self._access.character(character_id)
        if character is None:
            raise ObjectNotReachable()

        active_rows = self._access.active_links(character_id, limit=ACCESS_FACT_BOUND)
        after = pagination.decode(
            self._cursor_key, cursor_token, scope="character-links", arity=2
        )
        position = None
        if after is not None:
            from datetime import datetime

            position = (datetime.fromisoformat(after[0]), UUID(after[1]))
        historical_rows = self._access.historical_links(
            character_id, after=position, limit=HISTORICAL_ACCESS_BOUND + 1
        )
        page = Page.of(
            historical_rows,
            size=HISTORICAL_ACCESS_BOUND,
            key=self._cursor_key,
            scope="character-links",
            position=lambda row: (row["revoked_at"].isoformat(), str(row["id"])),
        )

        labels = self._accounts.labels_for(
            [row["platform_account_id"] for row in active_rows]
            + [row["granted_by_account_id"] for row in active_rows]
            + [row["platform_account_id"] for row in page.rows]
            + [row["granted_by_account_id"] for row in page.rows]
        )
        owner = self._access.active_owner(character_id)
        defaults_elsewhere = tuple(
            sorted(
                {
                    held["character_id"]
                    for held in (
                        self._access.active_default_for_account(
                            row["platform_account_id"]
                        )
                        for row in active_rows
                    )
                    if held is not None and held["character_id"] != character_id
                },
                key=str,
            )
        )[:SMALL_LIST_BOUND]

        summary = self._access.link_summary([character_id])
        return CharacterLinksView(
            state="ready",
            character=self._council_row(character, summary, labels),
            character_version=character["version"],
            active_links=tuple(
                self._access_fact(row, labels, council=True) for row in active_rows
            ),
            historical_links=tuple(
                self._access_fact(row, labels, council=True) for row in page.rows
            ),
            cursor=page.cursor,
            csrf_token=csrf_token,
            invariants=LinkInvariants(
                one_active_owner=owner is not None,
                # OD-37 §2, stated before the click rather than after it.
                revoking_last_owner_leaves_unresolved=owner is not None,
                default_character_held_elsewhere=defaults_elsewhere,
            ),
        )

    # -- R-24 -------------------------------------------------------------
    def identity_search(
        self, context: WebAuthorizationContext, *, guild_id: int, query: str | None,
        character_id: UUID | None = None,
    ) -> IdentitySearchResultsView:
        """At most 25 candidates from the membership projection, by snowflake.

        A query shorter than two characters returns the **empty** state rather
        than the whole guild: an unbounded render is an availability defect on a
        co-located host, and "everything" is not a search result.
        """
        term = (query or "").strip()[:SEARCH_QUERY_BOUND]
        echo = SafeText.bounded(term, SEARCH_QUERY_BOUND)
        if len(term) < MINIMUM_SEARCH_LENGTH:
            return IdentitySearchResultsView(
                state="empty" if not term else "invalid",
                query_echo=echo,
                candidates=(),
                truncated=False,
            )
        rows = self._candidates.search(
            guild_id=guild_id, query=term, limit=IDENTITY_CANDIDATE_BOUND + 1
        )
        visible, truncated = bounded_tuple(rows, IDENTITY_CANDIDATE_BOUND)
        linked_here = (
            self._candidates.linked_character_accounts(character_id)
            if character_id is not None
            else set()
        )
        candidates = tuple(
            IdentityCandidate(
                # The snowflake as a canonical decimal string. This is what the
                # grant form carries, and it is the only identity here.
                discord_subject=str(row["id"]),
                username=SafeText.bounded(row["username"], DISCORD_NAME_BOUND),
                global_name=(
                    SafeText.bounded(row["global_name"], DISCORD_NAME_BOUND)
                    if row["global_name"]
                    else None
                ),
                membership_observed_at=Instant.of(row["observed_at"]),
                already_linked_to_account=row["platform_account_id"] is not None,
                existing_link_here=row["platform_account_id"] in linked_here,
            )
            for row in visible
        )
        return IdentitySearchResultsView(
            state="ready" if candidates else "empty",
            query_echo=echo,
            candidates=candidates,
            truncated=truncated,
        )

    # -- R-31 -------------------------------------------------------------
    def field_profile(self, context: WebAuthorizationContext) -> FieldProfileView:
        """The versioned field profile, rendered. There is no write route.

        `owning_package` appears exactly when a field is
        `legacy_authority_deferred`, mirroring the invariant
        `domain/field_profile.py` already enforces — so the page cannot claim an
        authority the profile refuses to.
        """
        profile = self._profile
        paths, _ = bounded_tuple(
            (
                ProfilePathRow(
                    path=rule.path,
                    snapshot_mode=rule.mode.value,
                    reports_field=rule.profile_field,
                )
                for rule in profile.snapshot_fields
            ),
            PROFILE_ROW_BOUND,
        )
        fields, _ = bounded_tuple(
            (
                ProfileFieldRow(
                    field_key=field.key,
                    authority=field.authority.value,
                    difference_direction=_direction(field),
                    owning_package=field.owning_package,
                )
                for field in profile.reported_fields()
            ),
            PROFILE_ROW_BOUND,
        )
        return FieldProfileView(
            state="ready",
            profile_version=profile.version,
            paths=paths,
            fields=fields,
        )

    # -- helpers ----------------------------------------------------------
    def _summary(self, row) -> CharacterSummary:
        return CharacterSummary(
            character_id=row["id"],
            display_name=SafeText.bounded(row["display_name"], ACTOR_NAME_BOUND),
            level=row["level"],
            active=row["active"],
            access_kind=row["access_kind"],
            is_default=row["default_character"],
            portrait=CharacterPortrait.for_name(row["display_name"]),
            detail_path=f"/v1/characters/{row['id']}",
            last_snapshot=_stamp(
                row["checksum"], row["snapshot_world_id"], row["exported_at"]
            ),
        )

    def _council_row(self, row, summary, labels) -> CouncilCharacterRow:
        entry = summary.get(row["id"], {"active_links": 0, "owner_account_id": None})
        owner_id = entry["owner_account_id"]
        return CouncilCharacterRow(
            character_id=row["id"],
            display_name=SafeText.bounded(row["display_name"], ACTOR_NAME_BOUND),
            level=row["level"],
            active=row["active"],
            active_owner=_actor(owner_id, labels) if owner_id else None,
            active_link_count=entry["active_links"],
            # The OD-37 exception, made visible rather than treated as an error.
            unresolved_owner=owner_id is None,
            links_path=f"/v1/council/characters/{row['id']}/links",
        )

    def _access_fact(self, row, labels, *, council: bool) -> AccessFact:
        return AccessFact(
            access_id=row["id"],
            account=_actor(row["platform_account_id"], labels),
            # Council-visible evidence only, and absent from every member-facing
            # view. `Actor` above is the identity; this is a label beside it.
            discord_subject_display=(
                str(row["discord_user_id"]) if council and row["discord_user_id"] else None
            ),
            access_kind=row["access_kind"],
            active=row["active"],
            is_default=row["default_character"],
            granted_by=_actor(row["granted_by_account_id"], labels),
            granted_at=Instant.of(row["granted_at"]),
            revoked_at=Instant.of(row["revoked_at"]) if row["revoked_at"] else None,
            expires_at=Instant.of(row["expires_at"]) if row["expires_at"] else None,
            reason=SafeText.bounded(row["reason"], REASON_BOUND),
            correlation=Correlation(row["audit_correlation_id"]),
        )

    def _field_rows(self, character):
        """The two lists of VM-06, from the one versioned profile.

        A field with `database_authority` is rendered with the platform's own
        typed value; every other field is rendered as `migration deferred` with
        its owning package and **no value**, because `MigrationDeferred` has
        nowhere to put one.
        """
        profile = self._profile
        available = {"character.display_name": character["display_name"]}
        snapshot_fields = []
        deferred = []
        for field in profile.reported_fields():
            if field.is_deferred:
                deferred.append(
                    MigrationDeferred(
                        field_key=field.key,
                        owning_package=field.owning_package or "",
                    )
                )
                continue
            value = available.get(field.key)
            snapshot_fields.append(
                SnapshotField(
                    field_key=field.key,
                    label=field.label,
                    value=(
                        SafeText.bounded(value, ACTOR_NAME_BOUND)
                        if value is not None
                        else None
                    ),
                    authority="database_authority",
                    # Explicit, never a zero and never a blank: an absent value
                    # says it is absent (plan §6.5).
                    unavailable_reason=None if value is not None else "absent_in_snapshot",
                )
            )
        bounded_snapshot, _ = bounded_tuple(snapshot_fields, FIELD_BOUND)
        bounded_deferred, _ = bounded_tuple(deferred, FIELD_BOUND)
        return bounded_snapshot, bounded_deferred

    def _provenance(self, row) -> Provenance:
        if row is None:
            return Provenance(
                snapshot=None,
                profile_version=self._profile.version,
                world_id="",
            )
        return Provenance(
            snapshot=_stamp(row["checksum"], row["world_id"], row["exported_at"]),
            profile_version=self._profile.version,
            world_id=row["world_id"],
            external_actor_id=row["external_actor_id"],
            mapped_at=Instant.of(row["created_at"]),
        )


def _actor(account_id: UUID, labels) -> Actor:
    """An `Actor` for a Council view. **Never** a Discord snowflake.

    A missing operator label falls back to the account id's first segment, which
    is a platform identifier rather than a Discord one — the fallback must not
    quietly become the thing the type exists to keep out.
    """
    label = labels.get(account_id)
    return Actor(
        account_id=account_id,
        label=SafeText.bounded(label or f"Account {str(account_id)[:8]}", DISCORD_NAME_BOUND),
        capability=ActorCapability.GUILD_MEMBER,
    )


def _stamp(checksum, world_id, exported_at) -> SnapshotStamp | None:
    if not checksum or not exported_at:
        return None
    return SnapshotStamp(
        # First twelve hex characters, for display. Anything that must *identify*
        # a snapshot uses the full value server-side.
        checksum_short=checksum[:12],
        world_id=world_id or "",
        exported_at=Instant.of(exported_at),
    )


def _direction(field):
    direction = field.difference_direction
    if direction is None:
        return None
    # VM-11's vocabulary is the reader's, not the domain enum's: the profile
    # names the *record* a difference makes stale, and the view says which side.
    return (
        "platform_stale"
        if direction.value == "platform_display_name_stale"
        else "foundry_stale"
    )


__all__ = [
    "MINIMUM_SEARCH_LENGTH",
    "SEARCH_QUERY_BOUND",
    "CharacterQueryService",
]
