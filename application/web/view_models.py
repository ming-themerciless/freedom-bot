"""Version `vm-1` view models: the whole contract between backend and template.

Every type here is a frozen, slotted dataclass holding tuples and enums. That is
not a style preference — it is four rules from the accepted view-model contract,
stated where they are enforced:

1. **Typed and frozen.** A template cannot mutate what it was given, and a
   service cannot hand a template a `dict` whose keys nobody agreed to.
2. **Bounded.** Every sequence has a stated maximum and a `truncated` flag. An
   unbounded render is an availability defect on a host shared with three Foundry
   instances and the live bot (RAID R-24).
3. **Pre-authorized.** A view model contains only what its caller is already
   entitled to see. Templates perform no authorization and receive no data they
   must remember to hide.
4. **Presentation-safe.** No token, no authenticator secret, no recovery token,
   no exception text, no SQL, no path, no raw artifact byte reaches any field of
   any view model, ever.

**This module implements the P3.1 and P3.2 subsets**: VM-01 to VM-13, VM-16 and
the cross-cutting VM-19, VM-20 and VM-21. VM-14, VM-15, VM-17 and VM-18 belong
to P3.3 and are deliberately absent rather than stubbed — a stub would be a
contract the frontend could start depending on before its authorization was
written.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Literal
from uuid import UUID

from application.audit import ActorCapability

#: The version identifier the whole set carries. A change that removes a field,
#: renames one or narrows an enum is **breaking** and returns through P3.G2/G3.
#: Adding an optional field is additive and does not.
VIEW_MODEL_VERSION = "vm-1"

PageState = Literal["ready", "empty", "loading", "stale", "denied", "invalid", "error"]

#: §3.2's bounds on text that originated outside the platform. A value longer
#: than its bound is truncated **and says so**; the untruncated value is never
#: sent.
DISCORD_NAME_BOUND = 80
ACTOR_NAME_BOUND = 120
CHARACTER_LONG_NAME_BOUND = 240
REASON_BOUND = 500


@dataclass(frozen=True, slots=True)
class SafeText:
    """External text, bounded at construction and escaped at render.

    Bounding here rather than in the template is what makes the bound a property
    of the response instead of a property of one Jinja filter somebody remembered
    to apply.
    """

    value: str
    truncated: bool = False

    @classmethod
    def bounded(cls, raw: str | None, limit: int) -> "SafeText":
        text = raw or ""
        if len(text) <= limit:
            return cls(value=text, truncated=False)
        return cls(value=text[:limit], truncated=True)


@dataclass(frozen=True, slots=True)
class Instant:
    """Always UTC, always ISO-8601 in the machine field.

    Templates never compute a timezone: a template that formatted a time would be
    a second place for "what time is it here" to be answered differently.
    """

    iso_utc: str
    display: str

    @classmethod
    def of(cls, moment: datetime) -> "Instant":
        utc = moment.astimezone(tz=None) if moment.tzinfo is None else moment
        return cls(
            iso_utc=utc.isoformat(),
            display=utc.strftime("%Y-%m-%d %H:%M UTC"),
        )


@dataclass(frozen=True, slots=True)
class Correlation:
    """The one identifier a user may quote to an operator (N-25)."""

    id: UUID


@dataclass(frozen=True, slots=True)
class Actor:
    """Who did something. **Never** a Discord snowflake in a member-facing view."""

    account_id: UUID
    label: SafeText
    capability: ActorCapability


@dataclass(frozen=True, slots=True)
class Cursor:
    """Opaque and HMAC-signed (N-64). Never an offset."""

    token: str
    has_more: bool


class DenialCategory(Enum):
    """A closed vocabulary. Free-text denial reasons leak."""

    NOT_AUTHENTICATED = "not_authenticated"
    NOT_A_MEMBER = "not_a_member"
    INSUFFICIENT_CAPABILITY = "insufficient_capability"
    NOT_AVAILABLE = "not_available"
    EMERGENCY_SESSION_RESTRICTED = "emergency_session_restricted"
    SERVICE_DEGRADED = "service_degraded"


@dataclass(frozen=True, slots=True)
class DeniedReason:
    category: DenialCategory


@dataclass(frozen=True, slots=True)
class MigrationDeferred:
    """Rendered wherever a legacy field would otherwise appear.

    `owning_package` is read from the controlled migration manifest, never typed
    by hand, and this type deliberately has **no value field**: a deferred field
    cannot carry a value, so the type makes that unrepresentable rather than
    relying on a template not to print one.
    """

    field_key: str
    owning_package: str


# ---------------------------------------------------------------------------
# VM-01 `LoginPageView` — R-02
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class ProviderOption:
    key: str
    display_name: str
    #: A **path**, so a template cannot be tricked into rendering an off-site
    #: login button.
    start_path: str
    enabled: bool


@dataclass(frozen=True, slots=True)
class DegradedProvider:
    provider_key: str
    since: Instant
    message_code: str


LoginFailureCode = Literal[
    "transaction_expired",
    "transaction_unknown",
    "state_mismatch",
    "provider_error",
    "rate_limited",
    "not_available",
]


@dataclass(frozen=True, slots=True)
class LoginFailure:
    """A code and a correlation id — **never** the provider's error string (N-25)."""

    code: LoginFailureCode
    correlation: Correlation


@dataclass(frozen=True, slots=True)
class LoginPageView:
    state: PageState
    providers: tuple[ProviderOption, ...]
    #: A **configuration** fact, not an account fact. The page must not reveal
    #: whether a credential is enrolled for anyone.
    emergency_access_available: bool
    degraded: DegradedProvider | None = None
    failure: LoginFailure | None = None


# ---------------------------------------------------------------------------
# VM-02 `NonMemberView` — R-04's rejection, and caller state `N`
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class NonMemberView:
    """The person authenticated successfully and is not in the guild.

    That distinction from "not logged in" is the entire content of this view: it
    is what a user needs in order to recover. It names no roles, no characters
    and no other members.
    """

    state: PageState
    reason: DeniedReason
    #: Configuration, not fetched. Asking the provider here would make the
    #: rejection path depend on the provider being reachable.
    guild_display_name: str
    checked_at: Instant
    correlation: Correlation


# ---------------------------------------------------------------------------
# VM-03 `ServiceDegradedView` — any protected route once N-10's grace is spent
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class ServiceDegradedView:
    """The visible face of *fail closed*, rendered with `503`.

    It carries no cached role data and no character data, because the point at
    which this view appears is exactly the point at which cached authorization
    stopped being trustworthy.
    """

    state: PageState
    reason: DeniedReason
    subsystem: Literal["identity_provider", "database"]
    grace_expired: bool
    correlation: Correlation


# ---------------------------------------------------------------------------
# VM-04 `EmergencyLoginView` — R-06
# ---------------------------------------------------------------------------

EmergencyFailureCode = Literal[
    "invalid", "expired", "consumed", "rate_limited", "not_available"
]


@dataclass(frozen=True, slots=True)
class EmergencyFailure:
    """Deliberately coarse.

    `invalid`, `expired` and `consumed` are distinguishable to the operator
    through the audit record and **not** through the response: the browser learns
    only that it failed.
    """

    code: EmergencyFailureCode
    correlation: Correlation


@dataclass(frozen=True, slots=True)
class EmergencyLoginView:
    """Discloses no account identifier, no credential nickname and no grant state.

    The page is byte-identical whether or not a credential is enrolled, which is
    why both flags below are static configuration rather than lookups.
    """

    state: PageState
    webauthn_supported_hint: bool
    recovery_form_available: bool
    failure: EmergencyFailure | None = None


# ---------------------------------------------------------------------------
# P3.2 shared shapes
# ---------------------------------------------------------------------------

AccessKind = Literal["owner", "co_owner", "delegate", "viewer"]

#: §5.1 of the route contract: R-20 does not paginate, because the bound is how
#: many characters one person may be linked to. Past this the view truncates and
#: says so rather than growing without limit (RAID R-24).
MY_CHARACTERS_BOUND = 50
#: VM-06 and VM-08: who may reach one character.
ACCESS_FACT_BOUND = 25
HISTORICAL_ACCESS_BOUND = 100
#: VM-09.
IDENTITY_CANDIDATE_BOUND = 25
#: VM-06's two field lists.
FIELD_BOUND = 200
#: VM-11.
PROFILE_ROW_BOUND = 500
#: VM-12, N-62.
ROLE_MAPPING_BOUND = 50
#: VM-13.
LINKED_IDENTITY_BOUND = 10
#: VM-08's `default_character_held_elsewhere`, and VM-10's candidate list.
SMALL_LIST_BOUND = 10
#: N-21's default page size, reused for every cursor-paginated P3.2 view.
PAGE_SIZE_DEFAULT = 50
PAGE_SIZE_MAXIMUM = 100


def bounded_tuple(items, limit: int) -> tuple[tuple, bool]:
    """`(first `limit` items, whether anything was dropped)`.

    Every bounded sequence in this module is built through this, so "bounded"
    is one implementation rather than a rule each construction site remembers.
    The dropped remainder is never sent, and the flag is what says so — a view
    that silently truncated would be indistinguishable from a short list.
    """
    materialised = tuple(items)
    if len(materialised) <= limit:
        return materialised, False
    return materialised[:limit], True


@dataclass(frozen=True, slots=True)
class CharacterPortrait:
    """§3.4. Phase 3 renders **no** character image.

    Foundry image proxying is deferred and no route serves an artifact-derived
    byte, so the fallback is the only path. The type carries metadata and an
    accessible label; there is no URL field for a template to fill in.
    """

    state: Literal["unavailable_in_phase_3", "absent"]
    #: At most two characters, derived from the display name.
    initials: str
    accessible_label: str

    @classmethod
    def for_name(cls, display_name: str) -> "CharacterPortrait":
        parts = [part for part in display_name.split() if part]
        initials = "".join(part[0] for part in parts[:2]).upper()
        return cls(
            state="unavailable_in_phase_3" if initials else "absent",
            initials=initials[:2],
            accessible_label=f"Portrait unavailable for {display_name}",
        )


@dataclass(frozen=True, slots=True)
class SnapshotStamp:
    """`checksum_short` is the first 12 hex characters, **for display only**.

    Anything that must *identify* a snapshot uses the full value server-side.
    """

    checksum_short: str
    world_id: str
    exported_at: Instant


@dataclass(frozen=True, slots=True)
class AccessFact:
    """One `character_access` row as a Council member needs to read it.

    `discord_subject_display` is Council-visible evidence and appears in no
    member-facing view. The rule it carries is OD-42's: a snowflake answers
    *who is this on Discord*, and only an account id answers *who may do this
    here* — which is why `account` is an `Actor` and the snowflake is a string
    beside it rather than the identifier anything is keyed by.
    """

    access_id: UUID
    account: Actor
    access_kind: AccessKind
    active: bool
    is_default: bool
    granted_by: Actor
    granted_at: Instant
    reason: SafeText
    correlation: Correlation
    discord_subject_display: str | None = None
    revoked_at: Instant | None = None
    expires_at: Instant | None = None


# ---------------------------------------------------------------------------
# VM-05 `MyCharactersView` — R-20
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class CharacterSummary:
    #: `None` renders "not recorded", never `0`. `characters.level` is nullable
    #: *by design* — an imported identity awaits Council reconciliation — and
    #: rendering a null level as zero would fabricate a game fact. The view model
    #: forbids it by type rather than by template discipline (TC-VM-05).
    level: int | None
    character_id: UUID
    display_name: SafeText
    active: bool
    access_kind: AccessKind
    is_default: bool
    portrait: CharacterPortrait
    detail_path: str
    last_snapshot: SnapshotStamp | None = None


@dataclass(frozen=True, slots=True)
class MyCharactersView:
    """Exactly the caller's own active links, in a stable order.

    The empty state is a designed screen and a first-class outcome, not an
    error: a member with no links is told that Guild Council manages them. It
    offers no self-service control, because ordinary users are read-only
    (OD-31).
    """

    state: PageState
    characters: tuple[CharacterSummary, ...]
    truncated: bool
    default_character_id: UUID | None = None


# ---------------------------------------------------------------------------
# VM-06 `CharacterDetailView` — R-21
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class SnapshotField:
    """One field whose typed database package is already authoritative.

    A missing value is **explicit**: `value = None` with an
    `unavailable_reason`, never a zero, never a blank and never a stale older
    value. There is no branch in which this type can present an absence as a
    fact.
    """

    field_key: str
    label: str
    value: SafeText | None
    authority: Literal["snapshot_only", "database_authority"]
    unavailable_reason: Literal["absent_in_snapshot", "unsupported_type"] | None = None


@dataclass(frozen=True, slots=True)
class Provenance:
    snapshot: SnapshotStamp | None
    profile_version: str
    world_id: str
    external_actor_id: str | None = None
    mapped_at: Instant | None = None


@dataclass(frozen=True, slots=True)
class CharacterDetailView:
    """Three properties are enforced by the shape rather than by discipline.

    * **A deferred field cannot carry a value.** `MigrationDeferred` has no
      value field, so a legacy field cannot be rendered as though the platform
      knew it — which is the mandatory test *"every legacy field renders
      `migration deferred` plus the package named in the controlled migration
      register, with no editable control"*.
    * **A missing snapshot value is explicit**, per `SnapshotField` above.
    * **There is no mutation affordance anywhere in this type.** No form token,
      no editable field, no action list. A template cannot invent one the server
      would honour, because no route accepts one (route contract §1).

    `version` is the character's optimistic-concurrency value and is
    **display-only here**: R-21 is a read, and the routes that consume a version
    are R-25 to R-27, which take it from the Council screen.
    """

    state: PageState
    character_id: UUID
    display_name: SafeText
    long_name: SafeText | None
    level: int | None
    active: bool
    version: int
    portrait: CharacterPortrait
    access: tuple[AccessFact, ...]
    #: `None` when the viewer reaches this character by Council role rather than
    #: by an access row (OD-37). It is not "no access"; it is "not through one".
    viewer_access_kind: AccessKind | None
    snapshot_fields: tuple[SnapshotField, ...]
    deferred_fields: tuple[MigrationDeferred, ...]
    provenance: Provenance


# ---------------------------------------------------------------------------
# VM-07 `CouncilCharacterIndexView` — R-22
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class CharacterFilters:
    """Bounded, and echoed back escaped. `query` never searches by anything that
    establishes identity — a display name is a search fact and nothing more."""

    query: SafeText | None = None
    include_inactive: bool = False


@dataclass(frozen=True, slots=True)
class CouncilCharacterRow:
    character_id: UUID
    display_name: SafeText
    level: int | None
    active: bool
    active_owner: Actor | None
    active_link_count: int
    #: OD-37's exception made visible. The database enforces *at most* one
    #: active owner, and the application invariant *at least one* cannot be a
    #: constraint — so a character with no active owner is a reportable state
    #: rather than an error, and revoking the last owner is permitted.
    unresolved_owner: bool
    links_path: str


@dataclass(frozen=True, slots=True)
class CouncilCharacterIndexView:
    state: PageState
    rows: tuple[CouncilCharacterRow, ...]
    cursor: Cursor
    filters: CharacterFilters


# ---------------------------------------------------------------------------
# VM-08 `CharacterLinksView` — R-23
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class LinkInvariants:
    """States the consequence *before* the Council member commits.

    The database still enforces every one of these. This type does not replace
    a constraint; it explains one, so a confirmation reads as a decision rather
    than as a constraint violation reported afterwards.
    """

    one_active_owner: bool
    revoking_last_owner_leaves_unresolved: bool
    default_character_held_elsewhere: tuple[UUID, ...]


@dataclass(frozen=True, slots=True)
class CharacterLinksView:
    state: PageState
    character: CouncilCharacterRow
    #: Submitted back with every mutation, and re-checked server-side. A stale
    #: value is refused `409` and applied on top of nothing.
    character_version: int
    active_links: tuple[AccessFact, ...]
    historical_links: tuple[AccessFact, ...]
    cursor: Cursor
    csrf_token: str
    invariants: LinkInvariants


# ---------------------------------------------------------------------------
# VM-09 `IdentitySearchResultsView` — R-24 (HTMX fragment)
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class IdentityCandidate:
    """The operator picks a **snowflake**; the names beside it are labels.

    `already_linked_to_account` prevents the silent creation of a second
    platform account for a person who has one.
    """

    discord_subject: str
    username: SafeText
    global_name: SafeText | None
    membership_observed_at: Instant
    already_linked_to_account: bool
    existing_link_here: bool


@dataclass(frozen=True, slots=True)
class IdentitySearchResultsView:
    state: PageState
    query_echo: SafeText
    candidates: tuple[IdentityCandidate, ...]
    truncated: bool
    evidence_notice_code: Literal["names_are_not_identity"] = "names_are_not_identity"


# ---------------------------------------------------------------------------
# VM-10 `IdentityMigrationView` — R-28
# ---------------------------------------------------------------------------

ProposalResolution = Literal[
    "proposed", "ambiguous", "unresolved", "confirmed", "rejected"
]

#: The access kind a confirmed identity proposal creates, as a closed
#: single-member vocabulary. `owner` is deliberately not in it (migration
#: contract §7.2): ownership is a decision R-25 takes explicitly under OD-37's
#: one-active-owner invariant, not one a spreadsheet column takes on Council's
#: behalf. Rendered on the confirm form so the Council member sees what the
#: confirmation will create; there is no form field for it.
ConfirmedAccessKind = Literal["co_owner"]


@dataclass(frozen=True, slots=True)
class MigrationRun:
    """The C-04 evidence run R-28 is showing.

    `dry_run` is always `true` and is rendered rather than hidden: every row of
    `identity_migration_runs` is a C-04 evidence run, `CHECK`-ed so by the
    schema.

    There is **no apply state on a run** (change-log entry C-P3.2-A, OD-46). A
    confirmation is the activation, so "Council decided this run" and "the links
    exist" are the same fact and a second field for the second reading of it
    would be a field that can disagree with the first.
    """

    run_id: UUID
    produced_at: Instant
    source_snapshot: str
    dry_run: bool
    profile_version: str


@dataclass(frozen=True, slots=True)
class LinkProposal:
    """Sheet evidence, and one snowflake when the evidence resolved to one.

    The three Sheet fields are evidence and nothing else: a player name and a
    Discord *name* both change, one Discord name is recorded per player while
    the product invariant allows several authorized users per character, and
    `Active DM` confers no capability whatever (OD-18). `confirmable` is `false`
    for every `ambiguous` and `unresolved` row, and the server refuses the
    confirmation regardless of what the browser submits.
    """

    proposal_id: UUID
    character: CouncilCharacterRow
    #: The character's optimistic version, which the confirm form submits — the
    #: same field R-25's grant form carries. A confirmation now changes the
    #: character, so a page rendered before somebody else's change must not be
    #: applied on top of it: the conditional bump refuses `409` with the current
    #: state instead.
    character_version: int
    sheet_player_name: SafeText
    sheet_discord_name: SafeText | None
    active_dm_flag: bool
    proposed_subject: str | None
    resolution: ProposalResolution
    #: At most `SMALL_LIST_BOUND`, as VM-10 states. The **durable** candidate set
    #: is not bounded: `resolve()` returns every matching member and
    #: `identity_link_proposal_candidates` stores every one of them, because §7.6
    #: requires an ambiguity to persist as a record naming all of them. This field
    #: is the rendering, and the two below are what stop a bounded rendering from
    #: reading as a complete one.
    candidate_subjects: tuple[str, ...]
    #: **Addition to VM-10**, recorded as a contract deviation in the P3.2
    #: submission rather than made quietly. Without it a proposal ambiguous
    #: between fifteen people and one ambiguous between ten render identically,
    #: and a Council member cannot tell that they are choosing from a partial
    #: list — which is exactly the confusion §7.6 exists to prevent.
    candidate_subjects_truncated: bool
    #: How many candidates the run actually persisted, whatever this page shows.
    candidate_count: int
    #: What confirming this proposal **will create**, shown before it is created.
    #: Fixed by the service; the form carries no field for it, so it is a
    #: statement of what the server will do rather than a value the browser
    #: chooses.
    resulting_access_kind: ConfirmedAccessKind = "co_owner"
    confirmable: bool = True
    #: **Decision state**: a Council member confirmed or rejected this proposal.
    #: `resolution` already says which, and this says that the transition
    #: happened at all, so a template does not have to know the vocabulary. A
    #: confirmation **is** the activation, not an instruction awaiting an apply:
    #: there is no apply state on this type, because there is no such state
    #: (change-log entry C-P3.2-A, OD-46).
    decided: bool = False
    #: **Whether the access row this confirmation created is active now**, read
    #: from the exact `granted_access_id` and nothing else (change-log entry
    #: C-P3.2-C). `None` on every proposal that created no link — outstanding,
    #: ambiguous, unresolved and rejected — so "no link was ever created" and
    #: "the link was created and has since been revoked" are different values
    #: rather than the same falsy one.
    #:
    #: This is **not** a fifth decision state. The decision vocabulary is
    #: untouched and a revoked confirmation stays `confirmed` for ever: R-26 is a
    #: compensating action on the `character_access` row (migration contract
    #: §7.5), and this field reports that row's current state beside the
    #: immutable historical fact that Council confirmed it. Never inferred from
    #: another active link on the same character or account.
    link_state: Literal["active", "revoked"] | None = None
    evidence_notice_code: Literal["names_are_not_identity"] = "names_are_not_identity"


@dataclass(frozen=True, slots=True)
class MigrationTotals:
    """§7.4's control totals, shown to the person doing the confirming.

    `balances()` is the report's own arithmetic rather than a comment about it:
    every source row lands in exactly one bucket, and every proposal is
    outstanding, confirmed or rejected.

    `confirmed` counts proposals that are **active links** (§7.4 as amended by
    C-P3.2-A). There is no apply count beside it and no third equation, because
    there is nothing between a confirmation and the `character_access` row it
    creates.

    `confirmed_revoked` counts the confirmations whose access row was later
    revoked through R-26 (change-log entry C-P3.2-C). It exists so that
    `confirmed` can keep meaning *active link* — §7.4's sentence, unchanged —
    without the second balance quietly losing a proposal every time Council
    corrects one. A revoked confirmation is still a confirmation: it is counted
    here, never moved to `rejected` and never returned to `outstanding`.
    """

    source_characters: int
    source_players: int
    proposed: int
    ambiguous: int
    unresolved: int
    confirmed: int
    rejected: int
    already_linked: int
    outstanding: int
    #: Confirmations whose own `character_access` row is no longer active. A
    #: default of `0` because the overwhelmingly common run has none, and because
    #: a positional argument added in the middle of nine integers is exactly the
    #: constructor that goes wrong silently.
    confirmed_revoked: int = 0

    def balances(self) -> bool:
        first = (
            self.already_linked + self.proposed + self.ambiguous + self.unresolved
            == self.source_characters
        )
        second = (
            self.confirmed + self.confirmed_revoked + self.rejected + self.outstanding
            == self.proposed + self.ambiguous + self.unresolved
        )
        return first and second


@dataclass(frozen=True, slots=True)
class IdentityMigrationView:
    state: PageState
    run: MigrationRun | None
    proposals: tuple[LinkProposal, ...]
    cursor: Cursor
    totals: MigrationTotals
    csrf_token: str


# ---------------------------------------------------------------------------
# VM-11 `FieldProfileView` — R-31
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class ProfilePathRow:
    path: str
    snapshot_mode: Literal["snapshot-only", "reported", "ignored"]
    reports_field: str | None = None


@dataclass(frozen=True, slots=True)
class ProfileFieldRow:
    """`owning_package` is present exactly when the field is deferred.

    That mirrors the invariant `domain/field_profile.py` already enforces, so
    the presentation cannot claim an authority the profile refuses to.
    """

    field_key: str
    authority: Literal["database_authority", "legacy_authority_deferred"]
    difference_direction: Literal["platform_stale", "foundry_stale"] | None = None
    owning_package: str | None = None


@dataclass(frozen=True, slots=True)
class FieldProfileView:
    """Read-only by construction: there is no write route, and the profile is
    code under change control."""

    state: PageState
    profile_version: str
    paths: tuple[ProfilePathRow, ...]
    fields: tuple[ProfileFieldRow, ...]
    unknown_path_policy_code: Literal["reported_never_writable"] = (
        "reported_never_writable"
    )


# ---------------------------------------------------------------------------
# VM-12 `RoleCapabilityView` — R-32
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class RoleMappingRow:
    """`role_label` is explicitly presentation.

    *"Use stable Discord role IDs for authorization; role names are
    presentation"* — so `role_snowflake` is what every control submits and
    `role_label` is what a human reads. The protected bootstrap row renders with
    `revocable = false`, and the database refuses the mutation independently: the
    flag is an explanation, not the control.
    """

    mapping_id: UUID
    role_snowflake: str
    capability: ActorCapability
    protected: bool
    provenance: Literal["ordinary", "emergency_continuity"]
    revocable: bool
    ratifiable: bool
    created_by: Actor
    created_under_auth_method: Literal["discord_oauth", "webauthn", "recovery_grant"]
    created_at: Instant
    #: **Additive to the documented `vm-1` shape**, for the same reason and under
    #: the same rule as VM-13's `csrf_token`. R-34 and R-38 both require "the
    #: mapping's optimistic `version`" (route contract §5.1), and a form cannot
    #: submit a value the row it renders does not carry. Recorded in the P3.2
    #: submission.
    version: int
    role_label: SafeText | None = None
    ratified_at: Instant | None = None
    ratified_by: Actor | None = None


@dataclass(frozen=True, slots=True)
class RoleCapabilityView:
    """The administration screen, and **none of it is the control**.

    When `administrator_scope` is `emergency_continuity`,
    `available_capabilities` holds exactly `platform_administrator`, `revocable`
    is false on every row whose capability is something else, `ratifiable` is
    false everywhere, and `scope_notice_code` explains why the page looks
    smaller than the operator remembers. R-33, R-34 and R-38 refuse regardless of
    what was rendered, the check constraint refuses regardless of what the
    service decided, and TC-BG-05b issues the requests without ever fetching
    this page.

    `unratified_count` gives the same fact a place in the header, so a mapping
    created during an outage cannot sit unnoticed at position 34 of a 50-row
    table.
    """

    state: PageState
    guild_id: str
    administrator_scope: Literal["full", "emergency_continuity"]
    mappings: tuple[RoleMappingRow, ...]
    available_capabilities: tuple[ActorCapability, ...]
    csrf_token: str
    unratified_count: int
    scope_notice_code: Literal["emergency_continuity_allowlist"] | None = None
    lockout_guard_notice_code: Literal["protected_bootstrap_mapping"] = (
        "protected_bootstrap_mapping"
    )


# ---------------------------------------------------------------------------
# VM-13 `AccountIdentitiesView` — R-35
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class LinkedIdentity:
    """`subject_display` shows the caller their **own** subject in full.

    It is their own identifier. It is never rendered in any view another member
    can see. `retired` identities remain listed because historical audit
    attribution depends on them, and they carry no re-authentication control.
    """

    identity_id: UUID
    provider_key: str
    provider_display_name: str
    subject_display: str
    linked_at: Instant
    state: Literal["active", "retired"]
    is_current_session_identity: bool
    last_authenticated_at: Instant | None = None


@dataclass(frozen=True, slots=True)
class AccountIdentitiesView:
    state: PageState
    account_id: UUID
    identities: tuple[LinkedIdentity, ...]
    #: Phase 3 has exactly one ordinary provider. R-36 exists to make the
    #: boundary real and answers `no_additional_provider` until a later approved
    #: provider package — rather than a second provider being invented here.
    additional_provider: Literal["no_additional_provider"] | ProviderOption
    unlink_blocked_reason: (
        Literal["last_usable_identity", "emergency_session"] | None
    ) = None
    #: **Additive to the documented `vm-1` shape**, and permitted by §1 rule 5:
    #: adding an optional field does not break the version. R-37 is a
    #: cookie-authenticated mutation, so N-17 requires a synchronizer token to be
    #: rendered server-side into its form — and the accepted VM-13 block, alone
    #: among the view models carrying a mutation control, does not list one.
    #: Reading the token from a cookie by script instead is the double-submit
    #: scheme the delivery plan rejected.
    #:
    #: **Provenance corrected 2026-08-19** (accepted D-03 correction `C-P3.4-A`,
    #: item D-03-4). This comment previously read "Recorded in the P3.2
    #: submission", and it was not: `docs/review/phase-3-p3-2-submission.md`
    #: contains no occurrence of `csrf_token`. The accepted P3.2 submission is a
    #: historical record and has not been edited to manufacture the provenance
    #: after the fact. The field is now recorded where a frozen shape belongs —
    #: in the VM-13 block of `docs/contracts/phase-3-view-model-contract.md` — and
    #: that record, not this docstring, is the contract statement.
    csrf_token: str = ""


# ---------------------------------------------------------------------------
# VM-16 `HealthView` — R-10 (JSON, not HTML)
# ---------------------------------------------------------------------------

HealthCheckName = Literal[
    "database",
    "migrations",
    "artifact_store",
    "worker_heartbeat",
    "expired_leases",
    "identity_provider",
    "kill_switch",
]


@dataclass(frozen=True, slots=True)
class HealthCheck:
    name: HealthCheckName
    ok: bool


@dataclass(frozen=True, slots=True)
class HealthView:
    """No connection string, no host, no credential, no identity, no counts.

    `environment` is included deliberately: the single most useful thing a
    monitor can tell you is that production is running production configuration
    (RAID R-25).
    """

    status: Literal["ok", "degraded"]
    checks: tuple[HealthCheck, ...]
    version: str
    environment: Literal["development", "test", "staging", "production"]

    def as_payload(self) -> dict[str, object]:
        return {
            "status": self.status,
            "checks": {check.name: check.ok for check in self.checks},
            "version": self.version,
            "environment": self.environment,
        }


# ---------------------------------------------------------------------------
# VM-19 / VM-20 / VM-21 — the cross-cutting states
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class ConflictView:
    """Any `409`. Always carries the **current** state, so the next action is informed."""

    state: PageState
    conflict: Literal[
        "stale_version",
        "stale_preview",
        "already_applied",
        "already_cancelled",
        "duplicate_request",
    ]
    current: object
    correlation: Correlation


@dataclass(frozen=True, slots=True)
class SafeErrorView:
    """Any `500`: one code, one UUID, nothing else (N-25).

    There is deliberately no `detail` field. Adding one is a security change, not
    a usability improvement — the operator correlates through the log, and the
    user quotes the UUID.
    """

    state: PageState
    correlation: Correlation
    message_code: Literal["unexpected_error"] = "unexpected_error"


FieldErrorCode = Literal[
    "required", "too_long", "not_a_choice", "not_found", "not_permitted", "malformed"
]


@dataclass(frozen=True, slots=True)
class FieldError:
    field: str
    code: FieldErrorCode
    limit: int | None = None


@dataclass(frozen=True, slots=True)
class ValidationView:
    """Any `422`, with the form re-rendered so the user can correct it.

    `not_found` and `not_permitted` are both returned as `not_found` on
    object-scoped fields, matching the route contract's `404` rule so validation
    cannot become the enumeration oracle the status code refuses to be.
    """

    state: PageState
    form: object
    errors: tuple[FieldError, ...]


# ---------------------------------------------------------------------------
# VM-22 `DeniedView` — the safe denial body, every closed category
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class DeniedView:
    """Two fields, and the second one is a closed vocabulary. That is the point.

    **Added 2026-08-19 by the accepted D-03 correction (`C-P3.4-A`, item D-03-6).**
    Until then every generic denial — `401`, `403` and `404` alike — was rendered
    from a `NonMemberView` (VM-02) whose `guild_display_name` was `""`, whose
    `checked_at` was `Instant("", "")` and whose `correlation` was the nil UUID.
    The placeholders were deliberate and the rendered bytes were correct, because
    route contract §2.3 requires the `404` for an unreachable object and the `404`
    for an absent one to be **byte-identical** and a correlation id differs per
    request. But correctness rested on `denied.html` never printing three fields
    it was handed, and P3.4 writes that template. A production template that
    rendered `view.correlation.id` on a denial page would print
    `00000000-0000-0000-0000-000000000000` on every denial and break TC-OBJ-07 by
    exactly the amount a real correlation id varies.

    The correction is the type, not another rule for a template author to
    remember: there is nothing here to print. No correlation id, no guild name,
    no timestamp, no object identifier, no exception text and no free-form
    reason — the fields do not exist, so a template cannot render one by
    accident and a service cannot supply one by mistake. This is the same
    technique `MigrationDeferred` uses for deferred field values.

    **VM-02 keeps its own page.** `non_member.html` is a different response with
    a different purpose: the person authenticated successfully and is not in the
    guild, and the guild name, the check time and the correlation id are what
    they need in order to recover. That page is *intentionally* distinguishable
    and stays on VM-02 (view-model contract §4, VM-02).

    Additive under §1 rule 5: a view model is added, none is removed, renamed or
    narrowed, and `VIEW_MODEL_VERSION` stays `vm-1`.
    """

    state: PageState
    reason: DeniedReason


# ---------------------------------------------------------------------------
# VM-14 / VM-15 / VM-17 / VM-18 — import, job and audit views (P3.3)
# ---------------------------------------------------------------------------

#: VM-14: at most 50 snapshots, newest first, and at most 50 selectable folders
#: on each. Both are bounds on a page a co-located host has to render (R-24).
SNAPSHOT_ROW_BOUND = 50
FOLDER_CHOICE_BOUND = 50
#: VM-14: the exact length of `SnapshotListView.preview_nonce`. 32 random bytes
#: rendered by `secrets.token_urlsafe` are always 43 URL/form-safe characters, so
#: this is a fixed width rather than a ceiling, and a rendered value of any other
#: length was not minted by this platform.
PREVIEW_NONCE_BYTES = 32
PREVIEW_NONCE_BOUND = 43
#: VM-15. `issue_counts` is one entry per `ISSUE_CODES` member, and 30 is the
#: headroom over the nine that exist; `blocked_entries` is the one place an Actor
#: name crosses the boundary and it is Council-only.
ISSUE_COUNT_BOUND = 30
BLOCKED_ENTRY_BOUND = 50
CANDIDATE_CHARACTER_BOUND = 10
#: VM-18. §3.2: 40 values per record, 200 characters per value.
AUDIT_FACT_BOUND = 40
AUDIT_VALUE_BOUND = 200

#: N-27's six states, as the one vocabulary the schema, the state machine and the
#: view share. There is no seventh, and cancellation is a request rather than a
#: state.
JobState = Literal["queued", "running", "completed", "stale", "failed", "cancelled"]
JobKind = Literal["preview", "apply"]


@dataclass(frozen=True, slots=True)
class FolderChoice:
    """A folder's identity: the stable id **and** the displayed path (ADR 0006).

    Both, because a folder renamed or moved between preview and apply is a
    different confirmation from the one a Council member read, and an id alone
    cannot express that.

    ## `path_observed`, and the honest gap it names

    **Additive to the documented `vm-1` shape**, and permitted by §1 rule 5.

    `foundry_snapshots` records which folder **ids** a snapshot exports
    (`selected_folder_ids`) and nothing about their paths or per-folder Actor
    counts — those live only inside the artifact, and reading them costs the
    ~9.6 seconds of `json.loads` that R-40 must not spend in a page load.

    So a folder's path is known only once something has parsed the artifact: a
    completed preview stores the reconciled folder's path in its bounded summary.
    Before that, `folder_path` repeats the id and `actor_count` is the snapshot's
    own total when it exports exactly one folder — which is then exactly right,
    and is the same case `SnapshotImportService._default_folder()` already treats
    as unambiguous — and `0` otherwise.

    `path_observed` is what stops that from being a quiet lie. A template renders
    an unobserved folder as an identifier awaiting its first preview rather than
    as a path, and `is_default` is decided on an observed path or on the
    exactly-one-folder rule, never on a guess. Recorded in the P3.3 submission.
    """

    folder_id: str
    folder_path: SafeText
    actor_count: int
    is_default: bool
    path_observed: bool = True


@dataclass(frozen=True, slots=True)
class JobStamp:
    """The latest job against a snapshot, as R-40's row needs to show it."""

    job_id: UUID
    kind: JobKind
    state: JobState
    updated_at: Instant


@dataclass(frozen=True, slots=True)
class SnapshotRow:
    """One submitted snapshot. `checksum_full` is shown; the **artifact** is not.

    No route in the accepted inventory serves an artifact-derived byte, so this
    row identifies a document a Council member cannot download — deliberately
    (route contract §6.1, *audit visibility does not by itself grant permission
    to download the raw artifact*).
    """

    snapshot_id: UUID
    checksum_short: str
    checksum_full: str
    world_id: str
    world_title: SafeText
    core_version: str
    system_id: str
    system_version: str
    actor_count: int
    size_bytes: int
    exported_at: Instant
    received_at: Instant
    received_via: Literal["operator", "foundry_module"]
    selected_folder: FolderChoice | None
    selectable_folders: tuple[FolderChoice, ...]
    applied: bool
    latest_job: JobStamp | None


@dataclass(frozen=True, slots=True)
class SnapshotListView:
    """VM-14 — R-40.

    `can_select_folder` and `can_preview` are **rendering hints computed from the
    same resolution the server will perform again**. They exist so the page is
    honest, not so it is safe: R-41 and R-42 refuse regardless of what was
    rendered, and the matrix tests prove it by never fetching this page.

    ## `preview_nonce`, and why the page has to carry one

    `preview_nonce` is the **request identity every R-42 form on this response
    submits**. It is minted by the server for one R-40 render
    (`PREVIEW_NONCE_BOUND` URL/form-safe characters from
    `application.web.jobs.mint_preview_nonce`), it is the same value in every
    preview form of that response, and a separately rendered response carries a
    different one.

    That pair of properties is the whole contract, and each half is load-bearing:

    * **stable within one response**, so two submissions of the same rendered
      form — a double-click, a browser retry, a back-and-resubmit — produce the
      identical R-42 request key and therefore one durable job and one
      `reconciliation.job_queued` event; and
    * **distinct across renders**, so a Council member who deliberately loads the
      page again and previews again gets a *second* job rather than the first
      one's redirect.

    A value derived from the row — the snapshot and folder ids, say — satisfies
    the first half and silently breaks the second: it never changes while the
    snapshot and folder do not, so every later deliberate preview collapses onto
    the first job. That is the defect this field exists to close.

    **It is not authorization, and it is not a credential.** It carries no
    account, capability, snapshot, folder, timestamp or CSRF material, and
    holding it permits nothing: R-42 re-resolves Council capability and every
    server-owned snapshot, folder and profile fact on its own. Nor is the raw
    text durable — `jobs.request_key` hashes it with the server-read checksum,
    folder, profile version and account into the fixed-width digest that is the
    persisted identity.
    """

    state: PageState
    snapshots: tuple[SnapshotRow, ...]
    cursor: Cursor
    can_select_folder: bool
    can_preview: bool
    csrf_token: str
    preview_nonce: str


@dataclass(frozen=True, slots=True)
class JobProgress:
    """`percent` is `None` unless the worker can report a real fraction.

    A fabricated progress bar is worse than an indeterminate one: it tells a
    Council member watching a ten-second parse something the platform does not
    know.
    """

    step: Literal["queued", "reading", "parsing", "reconciling", "committing"]
    percent: int | None
    updated_at: Instant


@dataclass(frozen=True, slots=True)
class StaleReason:
    """Why an outstanding preview stopped being confirmable. A closed vocabulary."""

    code: Literal[
        "snapshot_changed",
        "folder_changed",
        "profile_version_changed",
        "aggregate_version_changed",
        "preview_expired",
        "authorization_changed",
    ]


@dataclass(frozen=True, slots=True)
class JobFailure:
    code: Literal[
        "parse_refused",
        "artifact_unavailable",
        "attempts_exhausted",
        "timeout",
        "internal",
    ]
    correlation: Correlation


@dataclass(frozen=True, slots=True)
class IssueCount:
    """A closed-vocabulary code and a count. **Never** the issue's message.

    `application/foundry/reconciliation.py` already keeps `ISSUE_CODES` closed
    because the codes go into an append-only audit payload. The web layer
    inherits the discipline: a reconciliation warning reaches the browser as a
    code plus a count, and the human sentence is a template-side lookup table
    owned by the platform. Text from the artifact is never forwarded, which
    closes the escaping question at the design level rather than at the filter.
    """

    code: str
    severity: Literal["error", "warning"]
    count: int


@dataclass(frozen=True, slots=True)
class BlockedEntry:
    """The one place an Actor name crosses the boundary.

    It is the minimum a Council member needs to resolve a blocked
    create-candidate, it is Council-only, it is bounded at 50 entries, the name
    is a `SafeText` under §3.2's 120-character bound, and it carries no other
    Actor field. Everything else about the artifact stays server-side.
    """

    external_actor_id: str
    display_name: SafeText
    issue_code: str
    candidate_character_ids: tuple[UUID, ...]


@dataclass(frozen=True, slots=True)
class ReconciliationSummary:
    actor_count: int
    mapped: int
    unmapped: int
    blocked: int
    absent: int
    would_create: int
    would_update: int
    issue_counts: tuple[IssueCount, ...]
    blocked_entries: tuple[BlockedEntry, ...]


@dataclass(frozen=True, slots=True)
class ConfirmScope:
    """Exactly what an apply would commit, and the token that names *this* preview.

    `preview_token` is the Phase 2 `PreviewBinding.token()` digest, reused
    unchanged. Presenting it back is what lets R-46 refer to the preview a
    Council member actually read rather than to whatever the database looks like
    when the button is pressed — and R-46 re-resolves authority, re-checks the
    checksum, folder, profile version and aggregate versions, and re-computes the
    scope fingerprint anyway, so the token is one control among four rather than
    the only one.
    """

    preview_token: str
    checksum_full: str
    folder: FolderChoice
    profile_version: str
    expires_at: Instant
    would_create: int
    would_update: int
    blocked: bool


@dataclass(frozen=True, slots=True)
class JobStatusView:
    """VM-15 — R-43 and R-44.

    `attempts` is the **number of claims made against the job**, the single
    meaning N-43 fixes, and it is at most 3. It is shown rather than hidden
    because a Council member watching a job retry twice is watching something
    worth knowing about, and `failure.code = "attempts_exhausted"` is what the
    third expiry produces.

    The response carries the bounded summary only — counts, issue codes, folder
    identity, checksum, profile version. Never Actor names outside
    `blocked_entries`, never warning text drawn from the artifact, never raw
    bytes.
    """

    state: PageState
    job_id: UUID
    kind: JobKind
    job_state: JobState
    progress: JobProgress | None
    requested_by: Actor
    requested_at: Instant
    attempts: int
    poll_after_seconds: int
    result: ReconciliationSummary | None
    stale_reason: StaleReason | None
    failure: JobFailure | None
    cancel_available: bool
    confirm: ConfirmScope | None
    csrf_token: str
    correlation: Correlation


@dataclass(frozen=True, slots=True)
class ImportResultView:
    """VM-17 — R-47. Mirrors the append-only `snapshot_imports` row.

    `duplicate_of` is how a retry presents itself: the second request returns the
    original receipt, and the view **says so** rather than implying a second
    import happened.
    """

    state: PageState
    import_id: UUID
    status: Literal["applied", "refused"]
    mode: Literal["bootstrap", "council"]
    actor: Actor
    capability: ActorCapability
    snapshot: SnapshotStamp
    checksum_full: str
    folder: FolderChoice
    profile_version: str
    created_count: int
    updated_count: int
    warning_count: int
    issue_counts: tuple[IssueCount, ...]
    occurred_at: Instant
    correlation: Correlation
    duplicate_of: UUID | None


@dataclass(frozen=True, slots=True)
class AuditFilters:
    """The accepted bounded filters (N-63), and nothing else is queryable.

    There is no free-text payload search and no action *substring*: an action
    filter is a **prefix**, which an index can serve and which cannot be turned
    into a scan of every row's JSON.
    """

    action_prefix: SafeText | None = None
    entity_type: str | None = None
    entity_id: SafeText | None = None
    capability: ActorCapability | None = None
    source: Literal["discord", "web", "foundry", "import", "system"] | None = None
    occurred_from: Instant | None = None
    occurred_to: Instant | None = None
    correlation_id: UUID | None = None


@dataclass(frozen=True, slots=True)
class AuditFact:
    """One flattened before/after pair. **Not** the payload.

    A payload key the projection does not recognize is rendered as a key with a
    redacted marker rather than as its value, so a future writer cannot widen the
    response by writing a new key.
    """

    key: str
    before: SafeText | None
    after: SafeText | None
    redacted: bool = False


@dataclass(frozen=True, slots=True)
class AuditRow:
    event_id: UUID
    occurred_at: Instant
    #: `None` for system and service-principal actions, which have no person.
    actor: Actor | None
    actor_capability: ActorCapability
    action: str
    entity_type: str
    entity_id: SafeText
    source: str
    correlation: Correlation
    facts: tuple[AuditFact, ...]
    payload_truncated: bool


@dataclass(frozen=True, slots=True)
class AuditSearchView:
    """VM-18 — R-48 and R-49.

    `total_is_unbounded` is `true` permanently: there is no `COUNT(*)` over
    `audit_events`, because that is the unbounded scan N-21 forbids. The
    immutability notice is a code rather than a sentence for the same reason
    every other vocabulary here is closed.
    """

    state: PageState
    filters: AuditFilters
    rows: tuple[AuditRow, ...]
    cursor: Cursor
    total_is_unbounded: bool = True
    immutability_notice_code: Literal["append_only_no_correction_here"] = (
        "append_only_no_correction_here"
    )


#: The view models this package implements, by contract identifier. Asserted
#: against the parsed contract document by the structural tests, so a name that
#: drifts fails a test rather than a review.
IMPLEMENTED_VIEW_MODELS: dict[str, type] = {
    "VM-01": LoginPageView,
    "VM-02": NonMemberView,
    "VM-03": ServiceDegradedView,
    "VM-04": EmergencyLoginView,
    "VM-05": MyCharactersView,
    "VM-06": CharacterDetailView,
    "VM-07": CouncilCharacterIndexView,
    "VM-08": CharacterLinksView,
    "VM-09": IdentitySearchResultsView,
    "VM-10": IdentityMigrationView,
    "VM-11": FieldProfileView,
    "VM-12": RoleCapabilityView,
    "VM-13": AccountIdentitiesView,
    "VM-14": SnapshotListView,
    "VM-15": JobStatusView,
    "VM-16": HealthView,
    "VM-17": ImportResultView,
    "VM-18": AuditSearchView,
    "VM-19": ConflictView,
    "VM-20": SafeErrorView,
    "VM-21": ValidationView,
    "VM-22": DeniedView,
}

#: Documented in `vm-1` and owned by a later package. Named rather than merely
#: absent, so "not implemented yet" is a recorded fact with an owner instead of
#: something a reader has to infer from a gap.
#:
#: **Empty from P3.3 onward.** The four import, job and audit view models this
#: mapping named are implemented above, so `vm-1` is now complete and the
#: structural guard asserts equality with the documented set rather than
#: equality-minus-a-deferral.
DEFERRED_VIEW_MODELS: dict[str, str] = {}
