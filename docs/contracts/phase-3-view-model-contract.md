# Phase 3 view-model contract, version `vm-1`

Status: **Accepted 2026-08-13 at P3.G0.** The version identifier stays `vm-1`;
the later P3.G2/P3.G3 gates still control its production-frontend freeze.

Remediated in this revision: VM-12 gains `administrator_scope`, per-row
`provenance`, `ratifiable`, `ratified_*` and `unratified_count`, so the
role-capability screen can show which mappings arrived through the emergency
path; VM-16 gains an `expired_leases` health check, which is the reaper's
liveness signal under the corrected N-43.

Package: P3.0 · Owner: Claude · Implemented by P3.1–P3.3 · **Frozen for Gemini's
P3.4 integration at stop gates P3.G2 and P3.G3.**

Routes cited as `R-nn` are defined in
[`phase-3-route-authorization-contract.md`](phase-3-route-authorization-contract.md).
Numbers cited as `N-nn` are defined in
[`phase-3-numeric-policy-register.md`](phase-3-numeric-policy-register.md).

## 1. What a view model is here, and what it is not

A view model is a **frozen, typed, bounded dataclass** produced by an application
query and handed to a Jinja template. It is the entire contract between backend
and frontend.

Rules that hold for every view model in this document:

1. **Typed and frozen.** `@dataclass(frozen=True, slots=True)`, with enums for
   closed vocabularies and `tuple` for sequences — never a bare `dict`, never a
   mutable list handed to a template (`.agents/AGENTS.md`, *Do not expose internal
   mutable lists or dictionaries*).
2. **Bounded.** Every sequence has a stated maximum. A template must never be able
   to render an unbounded collection, because an unbounded render is an
   availability defect on a co-located host (RAID R-24).
3. **Pre-authorized.** A view model contains only what its caller is already
   entitled to see. Templates perform no authorization and receive no data they
   must remember to hide.
4. **Presentation-safe.** No raw snapshot bytes, no OAuth tokens, no authenticator
   secrets, no recovery tokens, no exception text, no SQL, no file paths, no other
   player's private data — in any field, of any view model, ever (delivery plan
   §8.9, plan §6.5).
5. **Versioned.** The whole set carries the version `vm-1`. A change that removes a
   field, renames one, or narrows an enum is a **breaking** change requiring a new
   version and a return through P3.G2/P3.G3. Adding an optional field is additive
   and does not.
6. **Server-authoritative.** Any identifier, count, checksum, price, version or
   capability that came from the browser was re-resolved server-side before it
   entered a view model (route contract §2.4).

### 1.1 Version identifier

`vm-1` appears as a constant in the code (`application/web/view_models.py`,
`VIEW_MODEL_VERSION`) and in a test that asserts the documented set of view-model
names equals the implemented set (TC-STRUCT-02). The prototype's frozen visual
baseline is `design-prototype/`, which is **reference only**: no production module
imports or serves it (plan §12.1, and `tests/test_rejected_scope_absent.py`
establishes the precedent for asserting an absence).

## 2. Shared value objects

These appear inside several view models and are defined once.

| Type | Fields | Rules |
|---|---|---|
| `PageState` | `state: Literal["ready","empty","loading","stale","denied","invalid","error"]` | Every page-level view model carries exactly one. The seven values are the component inventory the accepted §12.1 prototype already renders |
| `SafeText` | `value: str`, `truncated: bool` | Any string that originated outside the platform — Actor names, reasons, usernames, filenames. Bounded (see §3.2) and escaped at render |
| `Actor` | `account_id: UUID`, `label: SafeText`, `capability: Capability` | Who did something. **Never** a Discord snowflake in a member-facing view |
| `Instant` | `iso_utc: str`, `display: str` | Always UTC, always ISO-8601 in the machine field. Templates never compute a timezone |
| `Correlation` | `id: UUID` | The one identifier a user may quote to an operator (N-25) |
| `Cursor` | `token: str`, `has_more: bool` | Opaque, HMAC-signed (N-64). Never an offset |
| `DeniedReason` | `category: Literal["not_authenticated","not_a_member","insufficient_capability","not_available","emergency_session_restricted","service_degraded"]` | A closed vocabulary. Free-text denial reasons leak |
| `MigrationDeferred` | `field_key: str`, `owning_package: str` | Rendered wherever a legacy field would otherwise appear (plan §12 Phase 3). `owning_package` is read from the controlled `data-migration-manifest.json`, never typed by hand |

`Capability` is the existing `application.audit.ActorCapability` enum. The web
layer adds no second vocabulary for the same concept.

## 3. Escaping and safe-display rules

### 3.1 The escaping contract

- Jinja2 autoescaping is **on** for every template extension in use
  (`.html`, `.html.j2`), configured at environment construction, and a test
  asserts it (TC-SEC-11). No template calls `|safe` on any value that can carry
  external content. The whole application permits `|safe` on **zero** values in
  Phase 3; a future exception requires a security review.
- `Markup` / `markupsafe` is not used to pre-render user-influenced content.
- Attribute interpolation uses quoted attributes only. URLs built from identifiers
  use `url_for`-style route construction from typed values (UUIDs, enums), never
  string concatenation of user input.
- No view model field is ever placed inside a `<script>` block. There is no
  server-rendered JSON island in Phase 3.
- HTMX attributes are static template text. `hx-on:` is forbidden (route contract
  §6.4), so no user value can reach a script context through an attribute.

### 3.2 Bounds on external text

| Source | Bound | On exceeding |
|---|---|---|
| Actor display name (snapshot) | 120 chars | Truncated with `truncated = true`; the untruncated value is never sent |
| Character long name | 240 chars | Truncated |
| Discord username / global name | 80 chars | Truncated (matches the `discord_users` columns) |
| Grant/revoke reason | 500 chars on input; 500 rendered | Rejected at input validation (`422`), not silently cut |
| Audit payload string value | 200 chars per value, 40 values per record | Truncated per value, then the record is marked `payload_truncated` |
| Issue/warning text | **not rendered at all** | Only closed-vocabulary issue **codes** are rendered; see §3.3 |

### 3.3 Warnings are codes, not prose

`application/foundry/reconciliation.py` already defines `ISSUE_CODES` as a closed
vocabulary, explicitly *"because `issue_codes` goes into an append-only audit
payload: a caller filters on it, and an unlisted value would be a free-text field
arriving under a vocabulary's name"*. The web layer inherits that discipline:

> A reconciliation warning reaches the browser as a **code plus a count**, and the
> human sentence is a template-side lookup table owned by the platform. Text from
> the artifact is never forwarded.

That closes the mandatory test *"escaped Actor, warning and user-controlled text"*
at the design level rather than at the escaping level — the dangerous string is
never in the response to begin with. Where an Actor name genuinely must be shown
(a blocked create-candidate a Council member has to resolve), it is a `SafeText`
under the §3.2 bound, and it is shown only to Council.

### 3.4 Portraits

Phase 3 renders **no character image**. Foundry image proxying is deferred
(visual handoff §6.4), and no route serves an artifact-derived byte (route
contract §6.1). `CharacterPortrait` therefore carries metadata and a fallback
only:

```text
CharacterPortrait(
    state: Literal["unavailable_in_phase_3", "absent"],
    initials: str,          # at most 2 characters, derived from display name
    accessible_label: str,  # "Portrait unavailable for {name}"
)
```

The accepted prototype's `onerror` fallback, `role="status"` announcement and
initials treatment are the visual target; the production difference is that the
fallback is the *only* path in Phase 3. Recorded so Gemini does not read the
prototype's local portrait assets as a contract to serve images.

## 4. Authentication and session view models

### VM-01 `LoginPageView` — R-02

```text
LoginPageView(
    state: PageState,                       # ready | error
    providers: tuple[ProviderOption, ...],  # exactly one in Phase 3
    emergency_access_available: bool,
    degraded: DegradedProvider | None,
    failure: LoginFailure | None,
)
ProviderOption(key: str, display_name: str, start_path: str, enabled: bool)
DegradedProvider(provider_key: str, since: Instant, message_code: str)
LoginFailure(code: Literal["transaction_expired","transaction_unknown",
    "state_mismatch","provider_error","rate_limited","not_available"],
    correlation: Correlation)
```

`ProviderOption.key` is `"discord"`. `start_path` is R-03's path — a **path**, so
a template cannot be tricked into rendering an off-site login button.
`LoginFailure` carries a code and a correlation ID and never the provider's error
string (N-25). The degraded banner is what a member sees when Discord is
unreachable; it names the emergency route only when `emergency_access_available`,
which is a configuration fact, not an account fact — the page must not reveal
whether a credential is enrolled.

### VM-02 `NonMemberView` — the R-04 rejection, and any protected route in caller state `N`

```text
NonMemberView(
    state: PageState,                # denied
    reason: DeniedReason,            # not_a_member
    guild_display_name: str,         # configuration, not fetched
    checked_at: Instant,
    correlation: Correlation,
)
```

The distinction from "not logged in" is the whole content of this view: the person
authenticated successfully and is not in the guild. It names no roles, no
characters and no other members.

It is rendered in two situations, and carries no session in the first: as the
`403` body of R-04 when a non-member completes the OAuth flow (ADR 0004's
rejection step), and on any protected route when an existing session's membership
has since been revoked.

### VM-03 `ServiceDegradedView` — any protected route when N-10 is exhausted

```text
ServiceDegradedView(
    state: PageState,                # error
    reason: DeniedReason,            # service_degraded
    subsystem: Literal["identity_provider","database"],
    grace_expired: bool,
    correlation: Correlation,
)
```

Rendered with `503`. It states that authorization cannot currently be confirmed
and that the platform is therefore refusing — the visible face of *fail closed*.
It carries no cached role data and no character data, because the point at which
this view appears is exactly the point at which cached authorization stopped being
trustworthy.

### VM-04 `EmergencyLoginView` — R-06

```text
EmergencyLoginView(
    state: PageState,                # ready
    webauthn_supported_hint: bool,   # static; feature detection is client-side
    recovery_form_available: bool,   # static configuration
    failure: EmergencyFailure | None,
)
EmergencyFailure(code: Literal["invalid","expired","consumed","rate_limited",
    "not_available"], correlation: Correlation)
```

Every failure code is deliberately coarse. `invalid`, `expired` and `consumed`
are distinguishable to the operator through the audit record, **not** through the
response — the browser learns only that it failed. The view discloses no account
identifier, no credential nickname and no grant state.

### VM-13 `AccountIdentitiesView` — R-35

```text
AccountIdentitiesView(
    state: PageState,
    account_id: UUID,
    identities: tuple[LinkedIdentity, ...],       # max 10
    additional_provider: Literal["no_additional_provider"] | ProviderOption,
    unlink_blocked_reason: Literal["last_usable_identity","emergency_session"] | None,
)
LinkedIdentity(
    identity_id: UUID,
    provider_key: str,
    provider_display_name: str,
    subject_display: str,        # abbreviated; see below
    linked_at: Instant,
    last_authenticated_at: Instant | None,
    state: Literal["active","retired"],
    is_current_session_identity: bool,
)
```

`subject_display` shows the caller their **own** Discord snowflake in full — it is
their own identifier — and is never rendered in any view another member can see.
`retired` identities remain listed because historical audit attribution depends on
them (schema contract §6.3); they carry no re-authentication control.

## 5. Member read view models

### VM-05 `MyCharactersView` — R-20

```text
MyCharactersView(
    state: PageState,                      # ready | empty
    characters: tuple[CharacterSummary, ...],   # max 50
    truncated: bool,
    default_character_id: UUID | None,
)
CharacterSummary(
    character_id: UUID,
    display_name: SafeText,
    level: int | None,                     # None renders "not recorded", not "0"
    active: bool,
    access_kind: Literal["owner","co_owner","delegate","viewer"],
    is_default: bool,
    portrait: CharacterPortrait,
    detail_path: str,
    last_snapshot: SnapshotStamp | None,
)
SnapshotStamp(checksum_short: str, world_id: str, exported_at: Instant)
```

`level` is nullable because `characters.level` is nullable *by design* — an
imported identity awaits Council reconciliation (schema comment, OD-37). Rendering
a null level as `0` would fabricate a game fact; the view model forbids it by
type. `checksum_short` is the first 12 hex characters, for display only; anything
that must identify a snapshot uses the full value server-side.

The empty state is a designed screen (the prototype's *No Linked Characters
Found*), and it says that Guild Council manages links — it offers no self-service
control, because ordinary users are read-only (OD-31).

### VM-06 `CharacterDetailView` — R-21

```text
CharacterDetailView(
    state: PageState,
    character_id: UUID,
    display_name: SafeText,
    long_name: SafeText | None,
    level: int | None,
    active: bool,
    version: int,                              # optimistic-concurrency value, display-only here
    portrait: CharacterPortrait,
    access: tuple[AccessFact, ...],            # max 25; who may reach this character
    viewer_access_kind: Literal[...] | None,   # None when the viewer is Council-by-role
    snapshot_fields: tuple[SnapshotField, ...],       # max 200
    deferred_fields: tuple[MigrationDeferred, ...],   # max 200
    provenance: Provenance,
)
SnapshotField(
    field_key: str,
    label: str,
    value: SafeText | None,
    authority: Literal["snapshot_only","database_authority"],
    unavailable_reason: Literal["absent_in_snapshot","unsupported_type"] | None,
)
Provenance(
    snapshot: SnapshotStamp | None,
    profile_version: str,
    world_id: str,
    external_actor_id: str | None,
    mapped_at: Instant | None,
)
```

Three properties are enforced by the shape rather than by discipline:

- **A deferred field cannot carry a value.** `MigrationDeferred` has no value
  field. It is impossible to render a legacy field as if the platform knew it —
  which is the mandatory test *"every legacy field renders `migration deferred`
  plus the package named in the controlled migration register, with no editable
  control"*. `domain/field_profile.py` already raises rather than answering for
  deferred fields; this is the same rule at the presentation boundary.
- **A missing snapshot value is explicit.** `value = None` with an
  `unavailable_reason` — never a zero, never a blank, never a stale older value
  (plan §6.5, *snapshot-backed calculations*).
- **There is no mutation affordance anywhere in this type.** No form token, no
  editable field, no action list. A template cannot invent one that the server
  would honour, because no route accepts one (route contract §1).

### VM-07 `CouncilCharacterIndexView` — R-22

```text
CouncilCharacterIndexView(
    state: PageState,
    rows: tuple[CouncilCharacterRow, ...],   # page size N-21 default 50, max 100
    cursor: Cursor,
    filters: CharacterFilters,
)
CouncilCharacterRow(
    character_id: UUID, display_name: SafeText, level: int | None, active: bool,
    active_owner: Actor | None, active_link_count: int,
    unresolved_owner: bool, links_path: str,
)
```

`unresolved_owner` is the OD-37 exception made visible: the database enforces *at
most* one active owner and the application invariant *at least one* cannot be a
constraint, so a character with no active owner is a reportable state, not an
error.

## 6. Council administration view models

### VM-08 `CharacterLinksView` — R-23

```text
CharacterLinksView(
    state: PageState,
    character: CouncilCharacterRow,
    character_version: int,                    # submitted back with every mutation
    active_links: tuple[AccessFact, ...],      # max 25
    historical_links: tuple[AccessFact, ...],  # max 100, newest first, cursor beyond that
    cursor: Cursor,
    csrf_token: str,
    invariants: LinkInvariants,
)
AccessFact(
    access_id: UUID,
    account: Actor,
    discord_subject_display: str | None,   # Council-visible, evidence only
    access_kind: Literal["owner","co_owner","delegate","viewer"],
    active: bool,
    is_default: bool,
    granted_by: Actor,
    granted_at: Instant,
    revoked_at: Instant | None,
    expires_at: Instant | None,
    reason: SafeText,
    correlation: Correlation,
)
LinkInvariants(
    one_active_owner: bool,
    revoking_last_owner_leaves_unresolved: bool,
    default_character_held_elsewhere: tuple[UUID, ...],   # max 10
)
```

`LinkInvariants` exists so the confirmation copy states the consequence *before*
the Council member commits, rather than reporting a constraint violation
afterwards. The database still enforces every one of them; the view model does not
replace the constraint, it explains it.

### VM-09 `IdentitySearchResultsView` — R-24 (HTMX fragment)

```text
IdentitySearchResultsView(
    state: PageState,                 # ready | empty | invalid
    query_echo: SafeText,             # echoed for context, escaped, bounded 120
    candidates: tuple[IdentityCandidate, ...],   # max 25
    truncated: bool,
    evidence_notice_code: Literal["names_are_not_identity"],
)
IdentityCandidate(
    discord_subject: str,             # the snowflake, canonical string
    username: SafeText,
    global_name: SafeText | None,
    membership_observed_at: Instant,
    already_linked_to_account: bool,
    existing_link_here: bool,
)
```

The candidate the operator picks is identified by **snowflake**. `username` and
`global_name` are labels; `evidence_notice_code` renders the standing warning that
names are evidence and never identity (OD-42, ADR 0006 *never by name matching*).
`already_linked_to_account` prevents the silent creation of a second platform
account for a person who has one.

### VM-10 `IdentityMigrationView` — R-28

```text
IdentityMigrationView(
    state: PageState,
    run: MigrationRun | None,
    proposals: tuple[LinkProposal, ...],   # page size 50, max 100
    cursor: Cursor,
    totals: MigrationTotals,
    csrf_token: str,
)
MigrationRun(run_id: UUID, produced_at: Instant, source_snapshot: str,
    dry_run: bool, profile_version: str)
LinkProposal(
    proposal_id: UUID,
    character: CouncilCharacterRow,
    sheet_player_name: SafeText,          # Characters C — evidence
    sheet_discord_name: SafeText | None,  # Players B — evidence
    active_dm_flag: bool,                 # Players D — evidence, never authorization
    proposed_subject: str | None,         # a snowflake, or None when unresolved
    resolution: Literal["proposed","ambiguous","unresolved","confirmed","rejected"],
    candidate_subjects: tuple[str, ...],  # max 10, populated when ambiguous
    evidence_notice_code: Literal["names_are_not_identity"],
    confirmable: bool,
)
MigrationTotals(
    source_characters: int, source_players: int,
    proposed: int, ambiguous: int, unresolved: int,
    confirmed: int, rejected: int, already_linked: int,
)
```

`confirmable` is `false` for every `ambiguous` and `unresolved` row and the server
refuses the confirmation regardless of what the browser submits. `MigrationTotals`
is the source-to-target control total the migration contract requires, shown to
the person doing the confirming rather than only in a report they may not read.

### VM-11 `FieldProfileView` — R-31

```text
FieldProfileView(
    state: PageState,
    profile_version: str,
    paths: tuple[ProfilePathRow, ...],     # max 500
    fields: tuple[ProfileFieldRow, ...],   # max 500
    unknown_path_policy_code: Literal["reported_never_writable"],
)
ProfilePathRow(path: str, snapshot_mode: Literal["snapshot-only","reported","ignored"],
    reports_field: str | None)
ProfileFieldRow(field_key: str,
    authority: Literal["database_authority","legacy_authority_deferred"],
    difference_direction: Literal["platform_stale","foundry_stale"] | None,
    owning_package: str | None)
```

Read-only by construction: there is no write route (route contract §5.1) and the
profile is code under change control. `owning_package` is present exactly when
`authority` is `legacy_authority_deferred`, mirroring the invariant
`domain/field_profile.py` already enforces.

### VM-12 `RoleCapabilityView` — R-32

```text
RoleCapabilityView(
    state: PageState,
    guild_id: str,
    administrator_scope: Literal["full","emergency_continuity"],
    mappings: tuple[RoleMappingRow, ...],   # max N-62 (50)
    available_capabilities: tuple[Capability, ...],   # N-67-filtered; see below
    csrf_token: str,
    lockout_guard_notice_code: Literal["protected_bootstrap_mapping"],
    scope_notice_code: Literal["emergency_continuity_allowlist"] | None,
    unratified_count: int,
)
RoleMappingRow(
    mapping_id: UUID,
    role_snowflake: str,
    role_label: SafeText | None,     # cached Discord label; presentation only
    capability: Capability,
    protected: bool,
    provenance: Literal["ordinary","emergency_continuity"],
    revocable: bool,                 # false whenever protected, or outside N-67
    ratifiable: bool,                # emergency provenance AND caller scope is full
    ratified_at: Instant | None,
    ratified_by: Actor | None,
    created_by: Actor,
    created_under_auth_method: Literal["discord_oauth","webauthn","recovery_grant"],
    created_at: Instant,
)
```

`role_label` is explicitly presentation (`.agents/AGENTS.md`: *"Use stable Discord
role IDs for authorization; role names are presentation"*). The protected
bootstrap row renders with `revocable = false`, and the database refuses the
mutation independently — the flag is an explanation, not the control.

The remediation fields are the same kind of thing, and the same caveat applies to
all of them. When `administrator_scope` is `emergency_continuity`,
`available_capabilities` contains exactly `platform_administrator`, `revocable`
is false on every row whose capability is something else, `ratifiable` is false
everywhere, and `scope_notice_code` explains why the page looks smaller than the
operator remembers. **None of that is the control**: R-33, R-34 and R-38 refuse
regardless of what was rendered, the check constraint refuses regardless of what
the service decided, and TC-BG-05b issues the requests without ever fetching this
page (route contract §2.2).

`provenance` and `created_under_auth_method` are shown because an administrator
looking at this table during an incident needs to see which rows arrived through
the emergency path. `unratified_count` gives the same fact a place in the page
header, so a mapping created during an outage cannot sit unnoticed at position 34
of a 50-row table.

## 7. Import, job and audit view models

### VM-14 `SnapshotListView` — R-40

```text
SnapshotListView(
    state: PageState,
    snapshots: tuple[SnapshotRow, ...],   # max 50, newest first
    cursor: Cursor,
    can_select_folder: bool,     # administrator
    can_preview: bool,           # Council
    csrf_token: str,
)
SnapshotRow(
    snapshot_id: UUID,
    checksum_short: str, checksum_full: str,
    world_id: str, world_title: SafeText,
    core_version: str, system_id: str, system_version: str,
    actor_count: int, size_bytes: int,
    exported_at: Instant, received_at: Instant,
    received_via: Literal["operator","foundry_module"],
    selected_folder: FolderChoice | None,
    selectable_folders: tuple[FolderChoice, ...],   # max 50
    applied: bool, latest_job: JobStamp | None,
)
FolderChoice(folder_id: str, folder_path: SafeText, actor_count: int, is_default: bool)
JobStamp(job_id: UUID, kind: Literal["preview","apply"], state: JobState, updated_at: Instant)
```

`can_select_folder` and `can_preview` are **rendering hints computed from the same
resolution the server will perform again**. They exist so the page is honest, not
so it is safe: R-41 and R-42 refuse regardless (route contract §2.2).

### VM-15 `JobStatusView` — R-43 and R-44

```text
JobStatusView(
    state: PageState,
    job_id: UUID,
    kind: Literal["preview","apply"],
    job_state: JobState,          # queued|running|completed|stale|failed|cancelled (N-27)
    progress: JobProgress | None,
    requested_by: Actor,
    requested_at: Instant,
    attempts: int,
    poll_after_seconds: int,      # >= N-22
    result: ReconciliationSummary | None,
    stale_reason: StaleReason | None,
    failure: JobFailure | None,
    cancel_available: bool,
    confirm: ConfirmScope | None,
    csrf_token: str,
    correlation: Correlation,
)
JobProgress(step: Literal["queued","reading","parsing","reconciling","committing"],
    percent: int | None, updated_at: Instant)
StaleReason(code: Literal["snapshot_changed","folder_changed","profile_version_changed",
    "aggregate_version_changed","preview_expired","authorization_changed"])
JobFailure(code: Literal["parse_refused","artifact_unavailable","attempts_exhausted",
    "timeout","internal"], correlation: Correlation)
ReconciliationSummary(
    actor_count: int, mapped: int, unmapped: int, blocked: int, absent: int,
    would_create: int, would_update: int,
    issue_counts: tuple[IssueCount, ...],       # max 30, one per ISSUE_CODES entry
    blocked_entries: tuple[BlockedEntry, ...],  # max 50, Council-only
)
IssueCount(code: str, severity: Literal["error","warning"], count: int)
BlockedEntry(external_actor_id: str, display_name: SafeText,
    issue_code: str, candidate_character_ids: tuple[UUID, ...])   # max 10
```

`attempts` is the **number of claims made against the job**, the single meaning
N-43 now fixes, and it is at most 3. It is shown rather than hidden because a
Council member watching a job retry twice is watching something worth knowing
about; `failure.code = "attempts_exhausted"` is what the third expiry produces
(SM-05).

`percent` is `None` unless the worker can report a real fraction; a fabricated
progress bar is worse than an indeterminate one. `issue_counts` uses the closed
`ISSUE_CODES` vocabulary (§3.3). `blocked_entries` is the one place an Actor name
crosses the boundary — it is the minimum a Council member needs to resolve a
blocked create-candidate, it is Council-only, it is bounded at 50, and it carries
no other Actor field. Everything else about the artifact stays server-side.

`stale_reason` matching the delivery plan's invalidation triggers is what makes
the mandatory test *"an administrator folder/profile change invalidates an
existing Council preview, and Council confirmation displays the exact changed
scope"* observable in the response rather than only in the database.

### VM-16 `HealthView` — R-10 (JSON, not HTML)

```text
HealthView(
    status: Literal["ok","degraded"],
    checks: tuple[HealthCheck, ...],
    version: str,               # application version string
    environment: Literal["development","test","staging","production"],
)
HealthCheck(name: Literal["database","migrations","artifact_store","worker_heartbeat",
    "expired_leases","identity_provider","kill_switch"], ok: bool)
```

No connection string, no host, no credential, no counts of players, no identity,
no queue contents. `environment` is included deliberately: the single most useful
thing a monitor can tell you is that production is running production
configuration (RAID R-25).

### VM-17 `ImportResultView` — R-47

```text
ImportResultView(
    state: PageState,
    import_id: UUID,
    status: Literal["applied","refused"],
    mode: Literal["bootstrap","council"],
    actor: Actor, capability: Capability,
    snapshot: SnapshotStamp, checksum_full: str,
    folder: FolderChoice, profile_version: str,
    created_count: int, updated_count: int, warning_count: int,
    issue_counts: tuple[IssueCount, ...],
    occurred_at: Instant, correlation: Correlation,
    duplicate_of: UUID | None,
)
```

Mirrors the existing `snapshot_imports` row, which is append-only. `duplicate_of`
is how a retry presents itself: the second request returns the original receipt
(plan §6.5, *idempotency and concurrency*), and the view says so rather than
implying a second import happened.

### VM-18 `AuditSearchView` — R-48 and R-49

```text
AuditSearchView(
    state: PageState,
    filters: AuditFilters,
    rows: tuple[AuditRow, ...],     # N-21: default 50, max 100
    cursor: Cursor,
    total_is_unbounded: bool,       # always true; no COUNT(*) over an append-only log
    immutability_notice_code: Literal["append_only_no_correction_here"],
)
AuditFilters(
    action_prefix: SafeText | None, entity_type: str | None, entity_id: SafeText | None,
    capability: Capability | None, source: Literal["discord","web","foundry","import","system"] | None,
    occurred_from: Instant | None, occurred_to: Instant | None,
    correlation_id: UUID | None,
)
AuditRow(
    event_id: UUID, occurred_at: Instant,
    actor: Actor | None,                 # None for system/service actions
    actor_capability: Capability,
    action: str, entity_type: str, entity_id: SafeText,
    source: str, correlation: Correlation,
    facts: tuple[AuditFact, ...],        # max 40
    payload_truncated: bool,
)
AuditFact(key: str, before: SafeText | None, after: SafeText | None)
```

`facts` is the flattened, bounded, structured projection of the JSON payload —
**not** the payload. `application/audit.py` already restricts payloads to JSON
scalars, mappings and sequences and rejects bytes; the view model narrows further
to key/before/after triples with per-value bounds (§3.2). A payload key the
projection does not recognize is rendered as a key with a redacted marker rather
than as its value, so a future writer cannot widen the response by writing a new
key.

`total_is_unbounded` is `true` permanently: there is no `COUNT(*)` over
`audit_events`, because that is the unbounded scan N-21 forbids.

## 8. Cross-cutting state view models

### VM-19 `ConflictView` — any `409`

```text
ConflictView(
    state: PageState,               # stale
    conflict: Literal["stale_version","stale_preview","already_applied",
                      "already_cancelled","duplicate_request"],
    current: object,                # the current VM for the same screen
    correlation: Correlation,
)
```

A conflict always carries the **current** state, so the user's next action is
informed rather than a blind retry. `already_applied` returns the original
receipt (VM-17), which is what makes a double-click indistinguishable from a
single click at the user's level while remaining one durable effect.

### VM-20 `SafeErrorView` — any `500`

```text
SafeErrorView(
    state: PageState,               # error
    correlation: Correlation,
    message_code: Literal["unexpected_error"],
)
```

One code, one UUID, nothing else (N-25). The operator correlates through the log;
the user quotes the UUID. There is no `detail` field, and adding one is a security
change.

### VM-21 `ValidationView` — any `422`

```text
ValidationView(
    state: PageState,               # invalid
    form: object,                   # the re-rendered form view model, values echoed safely
    errors: tuple[FieldError, ...], # max 20
)
FieldError(field: str, code: Literal["required","too_long","not_a_choice",
    "not_found","not_permitted","malformed"], limit: int | None)
```

Error codes are closed. `not_found` and `not_permitted` are both returned as
`not_found` on object-scoped fields, matching the route contract's `404` rule
(§2.3) so validation cannot become the enumeration oracle the status code refuses
to be.

## 9. HTMX and Jinja compatibility constraints

These are contract terms for P3.4, not suggestions:

1. **Every HTMX partial is also reachable as a full page.** R-44 and R-49 are
   fragments of R-43 and R-48; a caller with no JavaScript gets the full page and
   a working, if manual, flow. Progressive enhancement is a delivery-plan
   requirement (§5 P3.4).
2. **A fragment is authorized exactly like a page.** No fragment route relies on
   having been reached from its parent page.
3. **No SPA, no JSON API for the browser.** The only `application/json` browser
   routes are R-07/R-08, which exist because the WebAuthn API requires script, and
   R-10, which is not a browser route at all. Everything else is HTML.
4. **No client-side computation of an authoritative value.** Counts, totals,
   checksums and capabilities are rendered as received. HTMX swaps content; it
   does not calculate.
5. **`hx-post` targets carry the CSRF token** from the view model's `csrf_token`
   field, in a hidden input or `hx-headers` rendered server-side — never read from
   a cookie by script (N-17 is a synchronizer token, not a double-submit cookie).
6. **Polling honours `poll_after_seconds`** and stops on a terminal `job_state`.

## 10. Traceability

| View model | Screen (accepted §12.1 baseline) | Route | Owning package |
|---|---|---|---|
| VM-01, VM-04 | `login.html` | R-02, R-06 | P3.1 |
| VM-02, VM-03, VM-19, VM-20, VM-21 | `components.html` state inventory | all | P3.1 |
| VM-05 | `my-characters.html` | R-20 | P3.2 |
| VM-06 | `character-detail.html` | R-21 | P3.2 |
| VM-07, VM-08, VM-09 | `council-approval.html` (link/diff patterns) | R-22–R-27 | P3.2 |
| VM-10 | new screen; no frozen prototype page | R-28 | P3.2 |
| VM-11 | `reconciliation.html` deferred-fields section | R-31 | P3.2 |
| VM-12 | new screen; no frozen prototype page | R-32 (and the R-33/R-34/R-38 controls it carries) | P3.2 |
| VM-13 | new screen; no frozen prototype page | R-35 | P3.2 |
| VM-14, VM-15, VM-17 | `reconciliation.html` (job states `queued/running/completed/failed/stale` already prototyped) | R-40–R-47 | P3.3 |
| VM-16 | none (JSON) | R-10 | P3.1 |
| VM-18 | new screen; audit table patterns exist in `council-approval.html` | R-48 | P3.3 |

**Gap recorded, not silently absorbed.** Four screens in this contract have no
frozen prototype page: identity migration (VM-10), role-capability administration
(VM-12), account identities (VM-13) and audit search (VM-18). The frozen baseline
contains a `council-approval.html` that is a **Phase 6** approval-centre concept,
explicitly excluded from Phase 3 (delivery plan §4). P3.4 must therefore build four
screens by extending the accepted visual language rather than by adapting an
accepted page, and Peter's visual acceptance at P3.G4 covers new work in those four
cases. This is a scope observation for the P3.G0 decision, not a request to change
the accepted visual baseline.
