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
    #: scheme the delivery plan rejected. Recorded in the P3.2 submission.
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
    "VM-16": HealthView,
    "VM-19": ConflictView,
    "VM-20": SafeErrorView,
    "VM-21": ValidationView,
}

#: Documented in `vm-1` and owned by a later package. Named rather than merely
#: absent, so "not implemented yet" is a recorded fact with an owner instead of
#: something a reader has to infer from a gap.
DEFERRED_VIEW_MODELS: dict[str, str] = {
    "VM-14": "P3.3",
    "VM-15": "P3.3",
    "VM-17": "P3.3",
    "VM-18": "P3.3",
}
