"""SQLAlchemy Core access to the Phase 3 identity, session and credential tables.

Written against Core rather than the ORM for the same reason the rest of this
repository is: the statements below *are* the design. Three of them in particular
are single statements because being single statements is what makes the property
they carry a database guarantee instead of a coding convention, and an ORM
session flushing them in two would quietly withdraw that guarantee:

- **`consume_oauth_transaction`** returns the PKCE verifier as it was *before*
  the update and erases it in the same pass. A replay finds neither a live
  transaction nor a verifier (schema §9.2.1).
- **`consume_recovery_grant`** matches on unconsumed, uninvalidated and unexpired
  in the `WHERE`, so replay, expiry and concurrency all resolve to zero rows.
- **`increment_rate_limit`** is one `INSERT … ON CONFLICT DO UPDATE … RETURNING`,
  which is what lets the counter be shared across `freedom-web` and
  `freedom-worker` without a second datastore (N-30).

Every method takes an explicit `Connection`. Transaction boundaries belong to the
caller, because the rule that a state change and its audit event share one
transaction (SM-01, SM-03, SM-07) cannot be expressed by a repository that opens
its own.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Iterable
from uuid import UUID, uuid4

from sqlalchemy import (
    Connection,
    TextClause,
    and_,
    delete,
    func,
    insert,
    String,
    or_,
    select,
    text,
    update,
)
from sqlalchemy.dialects.postgresql import insert as pg_insert

from application.audit import ActorCapability
from application.web.capabilities import (
    AdministratorScope,
    AuthMethod,
    MappingProvenance,
    MembershipProjection,
    RoleCapabilityMapping,
)
from application.web.config import SessionSettings
from application.web.errors import AmbiguousProviderIdentity
from application.web.crypto import Sealed
from application.web.sessions import SessionPolicy
from adapters.database.tables import (
    audit_events,
    auth_rate_limits,
    character_access,
    characters,
    discord_guild_memberships,
    discord_users,
    discord_membership_roles,
    external_actor_mappings,
    external_identities,
    foundry_snapshots,
    identity_link_proposal_candidates,
    identity_link_proposals,
    identity_migration_runs,
    oauth_token_grants,
    oauth_transactions,
    platform_accounts,
    recovery_grants,
    reconciliation_job_results,
    reconciliation_jobs,
    role_capability_mapping_events,
    role_capability_mappings,
    sessions,
    sheet_row_mappings,
    snapshot_folder_selections,
    snapshot_imports,
    webauthn_challenges,
    webauthn_credentials,
)

DISCORD_PROVIDER_KEY = "discord"


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


# ---------------------------------------------------------------------------
# Accounts and external identities
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class AccountRecord:
    id: UUID
    status: str
    is_protected_admin: bool
    display_label: str | None


class AccountRepository:
    """Platform accounts and their external identities (ADR 0010 D1, D2)."""

    __slots__ = ("_connection",)

    def __init__(self, connection: Connection) -> None:
        self._connection = connection

    def get(self, account_id: UUID) -> AccountRecord | None:
        row = (
            self._connection.execute(
                select(platform_accounts).where(platform_accounts.c.id == account_id)
            )
            .mappings()
            .one_or_none()
        )
        return None if row is None else _account(row)

    def protected_administrator(self) -> AccountRecord | None:
        row = (
            self._connection.execute(
                select(platform_accounts).where(platform_accounts.c.is_protected_admin)
            )
            .mappings()
            .one_or_none()
        )
        return None if row is None else _account(row)

    def find_by_identity(self, provider_key: str, subject: str) -> AccountRecord | None:
        """Resolve `(provider, subject)` to an account, **exactly**.

        There is no fallback lookup by name, username or email, here or anywhere
        else: `external_identities` has no such column, so there is nothing to
        fall back to. That absence is the control (N-16, ADR 0010 D3).
        """
        row = (
            self._connection.execute(
                select(platform_accounts)
                .join(
                    external_identities,
                    external_identities.c.platform_account_id == platform_accounts.c.id,
                )
                .where(
                    external_identities.c.provider_key == provider_key,
                    external_identities.c.subject == subject,
                    external_identities.c.state == "active",
                )
            )
            .mappings()
            .one_or_none()
        )
        return None if row is None else _account(row)

    def create_with_identity(
        self,
        *,
        provider_key: str,
        subject: str,
        correlation_id: UUID,
        display_label: str | None = None,
    ) -> AccountRecord:
        """First login on a provider with no existing identity (SM-04).

        `display_label` is operator-facing only. It is stored because an operator
        looking at an account list needs something to read; it is never compared,
        and no query in this module filters on it.
        """
        account_id = uuid4()
        self._connection.execute(
            insert(platform_accounts).values(
                id=account_id,
                status="active",
                is_protected_admin=False,
                display_label=display_label,
            )
        )
        self._connection.execute(
            insert(external_identities).values(
                id=uuid4(),
                platform_account_id=account_id,
                provider_key=provider_key,
                subject=subject,
                state="active",
                linked_at=utcnow(),
                audit_correlation_id=correlation_id,
            )
        )
        return AccountRecord(
            id=account_id,
            status="active",
            is_protected_admin=False,
            display_label=display_label,
        )

    def identity_id(self, provider_key: str, subject: str) -> UUID | None:
        return self._connection.execute(
            select(external_identities.c.id).where(
                external_identities.c.provider_key == provider_key,
                external_identities.c.subject == subject,
            )
        ).scalar_one_or_none()

    def note_authentication(self, identity_id: UUID, *, at: datetime) -> None:
        self._connection.execute(
            update(external_identities)
            .where(external_identities.c.id == identity_id)
            .values(last_authenticated_at=at)
        )

    def active_identity_count(self, account_id: UUID) -> int:
        return int(
            self._connection.execute(
                select(text("count(*)"))
                .select_from(external_identities)
                .where(
                    external_identities.c.platform_account_id == account_id,
                    external_identities.c.state == "active",
                )
            ).scalar_one()
        )

    def lock_identity_changes(self, account_id: UUID) -> bool:
        """Serialize decisions that can change this account's usable identities.

        Locking one ``external_identities`` row is insufficient for R-37: two
        requests can target two different rows, both observe a count of two and
        retire both. The stable parent account is the common lock key. Callers
        must acquire it before re-reading identity state or counting active
        identities, and every future existing-account link path must use the
        same lock before adding a usable identity.
        """
        return (
            self._connection.execute(
                select(platform_accounts.c.id)
                .where(platform_accounts.c.id == account_id)
                .with_for_update()
            ).scalar_one_or_none()
            is not None
        )

    # -- P3.2 -------------------------------------------------------------
    def discord_subject(self, account_id: UUID) -> str | None:
        """This account's **active** Discord subject, for the projection lookup.

        The projection is keyed by snowflake because it holds Discord facts; the
        authorization built on top of it is keyed by account. This method is the
        one crossing between the two, and it is a *read* — nothing here decides
        anything, it only says which Discord rows describe this person.

        ## Two active Discord identities is an ambiguity, and it fails closed

        `external_identities` is unique on `(provider_key, subject)` and carries no
        constraint against one account holding **two** active identities for the
        same provider (schema §5), so the state is expressible. This method used to
        answer it with `scalar_one_or_none()`, which raises `MultipleResultsFound` —
        an unhandled exception inside `open_request()`, so every protected request by
        such an account became a `500` naming an internal error.

        It is answered as an ambiguity instead. `AmbiguousProviderIdentity` reaches
        the boundary as a refusal rather than a crash, and it is deliberately not
        resolved by ordering the rows and taking the first: which Discord account's
        roles decide a person's capability is exactly the question that must not be
        settled by an arbitrary tiebreak. The same rule the identity resolver
        applies to candidate people, applied to one person's provider identities.

        No constraint is added here to make the state unexpressible. Whether one
        human may link two Discord accounts to one platform account is a product
        decision that ADR 0010 does not settle, and forbidding it in a migration
        would settle it as a side effect of fixing a `500`. The P3.2 submission
        records it as an open question for the maintainer.
        """
        subjects = (
            self._connection.execute(
                select(external_identities.c.subject).where(
                    external_identities.c.platform_account_id == account_id,
                    external_identities.c.provider_key == DISCORD_PROVIDER_KEY,
                    external_identities.c.state == "active",
                )
            )
            .scalars()
            .all()
        )
        if not subjects:
            return None
        if len(subjects) > 1:
            raise AmbiguousProviderIdentity(account_id, DISCORD_PROVIDER_KEY)
        return subjects[0]

    def account_for_active_identity(self, provider_key: str, subject: str) -> UUID | None:
        """`(provider, subject)` to an account id, or `None`. **Never creates one.**

        R-25 resolves its target through this: the Council member selects a
        snowflake and the platform account is looked up server-side (TC-ID-08).
        A snowflake nobody has authenticated with resolves to nothing, and the
        grant is refused as unreachable — minting an account from a Council form
        would create a platform identity nobody ever proved they hold.
        """
        return self._connection.execute(
            select(external_identities.c.platform_account_id).where(
                external_identities.c.provider_key == provider_key,
                external_identities.c.subject == subject,
                external_identities.c.state == "active",
            )
        ).scalar_one_or_none()

    def labels_for(self, account_ids) -> dict[UUID, str | None]:
        """Operator-facing labels for a bounded set of accounts, in one query.

        Bounded because every caller is rendering a bounded view model. One
        statement rather than one per row: N+1 queries in a web endpoint are
        forbidden by `.agents/AGENTS.md`, and a Council links page can name
        twenty-five accounts.
        """
        wanted = {account_id for account_id in account_ids if account_id is not None}
        if not wanted:
            return {}
        rows = self._connection.execute(
            select(platform_accounts.c.id, platform_accounts.c.display_label).where(
                platform_accounts.c.id.in_(wanted)
            )
        ).all()
        return {row[0]: row[1] for row in rows}

    def identities_for(self, account_id: UUID) -> list:
        """R-35. The caller's own identities, active and retired, newest first.

        Retired rows stay listed because historical audit attribution resolves
        through them (schema §6.3). They carry no control: an identity that has
        been retired is history, not an option.
        """
        return list(
            self._connection.execute(
                select(external_identities)
                .where(external_identities.c.platform_account_id == account_id)
                .order_by(
                    external_identities.c.linked_at.desc(),
                    external_identities.c.id.desc(),
                )
            )
            .mappings()
            .all()
        )

    def identity(self, identity_id: UUID):
        return (
            self._connection.execute(
                select(external_identities).where(external_identities.c.id == identity_id)
            )
            .mappings()
            .one_or_none()
        )

    def retire_identity(self, identity_id: UUID, *, reason: str, at: datetime) -> bool:
        """R-37. Marks `retired`; **never deletes the row**.

        Conditional on the row still being active, so two concurrent unlinks
        resolve to one: the loser matches zero rows and is told the state moved
        rather than writing a second retirement over the first.
        """
        result = self._connection.execute(
            update(external_identities)
            .where(
                external_identities.c.id == identity_id,
                external_identities.c.state == "active",
            )
            .values(state="retired", retired_at=at, retired_reason=reason)
        )
        return (result.rowcount or 0) == 1


def _account(row) -> AccountRecord:
    return AccountRecord(
        id=row["id"],
        status=row["status"],
        is_protected_admin=row["is_protected_admin"],
        display_label=row["display_label"],
    )


# ---------------------------------------------------------------------------
# Sessions
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class SessionRecord:
    id: UUID
    platform_account_id: UUID
    auth_method: AuthMethod
    created_at: datetime
    idle_expires_at: datetime
    absolute_expires_at: datetime
    privilege_fingerprint: bytes
    revoked_at: datetime | None
    #: OD-44. Non-null for every `discord_oauth` session, and carried forward
    #: unchanged by N-08 rotation so a rotated session still names the login it
    #: descends from. `None` for WebAuthn and recovery-grant sessions, which the
    #: check constraint requires.
    oauth_transaction_id: UUID | None = None


@dataclass(frozen=True, slots=True)
class RotatedSession:
    """The successor a rotation actually persisted, with the bounds it was given.

    Rotation returns the bounds rather than letting the caller re-derive them,
    because after the 2026-08-14 lifetime correction the caller cannot: the
    absolute expiration is the **predecessor's**, read under the row lock, and
    the idle expiration is clamped to it. A caller that reported
    `now + bounds.absolute` would be reporting an expiry the row does not have.
    """

    id: UUID
    idle_expires_at: datetime
    absolute_expires_at: datetime


@dataclass(frozen=True, slots=True)
class TouchedSession:
    """The bounds an accepted idle refresh actually persisted.

    Touch returns the row's own timestamps for the same reason rotation does:
    the new idle expiration is `LEAST(now + idle, absolute_expires_at)`, decided
    by PostgreSQL inside the conditional write, so a caller that reported
    `now + idle` would be reporting an expiry the row does not have whenever the
    clamp bites. `absolute_expires_at` is returned unchanged — touch never writes
    it — so a caller can assert that rather than assume it.
    """

    id: UUID
    last_seen_at: datetime
    idle_expires_at: datetime
    absolute_expires_at: datetime


def _touch_statement(
    policy: SessionPolicy,
) -> tuple[TextClause, dict[str, object]]:
    """Build the conditional refresh from the derived policy. No literals here.

    **The mapping is generated, never supplied** (corrected 2026-08-15,
    idle-policy-construction remediation, finding F2). This function previously
    iterated its argument — `for method, idle in idle_policy` — over a
    `SessionIdlePolicy` whose `__iter__` was public and overridable. A subclass
    inheriting the supported factory could therefore replace what the SQL was
    built from while `for_method()` went on reporting the correct window:

        class ForgedPolicy(SessionIdlePolicy):
            def __iter__(self):
                return iter((m, timedelta(minutes=60)) for m in AuthMethod)

    gave persisted WebAuthn and recovery-grant rows a sixty-minute refresh.
    Nothing is iterated now. The set of methods is `AuthMethod` itself, and each
    one's window is `policy.idle_for(method)` — `session_class_of()`, an explicit
    table, applied to two validated numbers. There is no argument in the shape of
    a mapping, so there is no mapping to override.

    Ordered by `method.value` so the generated statement is stable across
    processes, which makes a diff of the SQL readable.

    Every value is a bind parameter. The only thing interpolated is the generated
    parameter *names* (`:method_0`, `:idle_seconds_0`, …), which come from
    `enumerate` and never from data.

    Two clauses carry the correction:

    - `CASE auth_method WHEN … THEN …` chooses the window from the column, so the
      duration is a function of the persisted row and of nothing a caller says.
    - `auth_method IN (…)` refuses a row the policy does not govern. Today the
      policy covers every `AuthMethod` and `ck_sessions_auth_method` allows
      exactly those three values, so no reachable row fails it. It is here
      because the failure it prevents is silent: an ungoverned method makes the
      `CASE` yield `NULL`, `make_interval` yield `NULL`, and `LEAST` — which
      ignores `NULL` — return `absolute_expires_at`, handing the row the longest
      window there is. A refusal is the safe outcome; a default is not.
    """
    branches: list[str] = []
    method_placeholders: list[str] = []
    parameters: dict[str, object] = {}
    methods = sorted(AuthMethod, key=lambda member: member.value)
    for index, method in enumerate(methods):
        # Raises `UnclassifiedAuthMethod` for a method nobody classified, so a
        # future one refuses **here**, at repository construction, rather than
        # silently acquiring a window in a generated `CASE` branch.
        idle = policy.idle_for(method)
        method_name = f"method_{index}"
        seconds_name = f"idle_seconds_{index}"
        branches.append(
            f"WHEN :{method_name} "
            f"THEN CAST(:{seconds_name} AS double precision)"
        )
        method_placeholders.append(f":{method_name}")
        parameters[method_name] = method.value
        parameters[seconds_name] = idle.total_seconds()
    indented = "\n                                   ".join(branches)
    statement = text(
        f"""
        UPDATE sessions
           SET last_seen_at = CAST(:now AS timestamptz),
               idle_expires_at = LEAST(
                   CAST(:now AS timestamptz)
                       + make_interval(secs => CASE auth_method
                                   {indented}
                               END),
                   absolute_expires_at
               )
         WHERE id = :id
           AND auth_method IN ({", ".join(method_placeholders)})
           AND revoked_at IS NULL
           AND idle_expires_at > CAST(:now AS timestamptz)
           AND absolute_expires_at > CAST(:now AS timestamptz)
     RETURNING id, last_seen_at, idle_expires_at, absolute_expires_at
        """
    )
    return statement, parameters


class SessionRepository:
    """Opaque server-side sessions (schema §9.1, SM-02).

    **This is the one owner of session bounds in a composition graph** (corrected
    2026-08-15, idle-policy-construction remediation). It takes `SessionSettings`
    — validated at its own construction, so the numbers are in-register whatever
    built it — and derives a `SessionPolicy` from it once. `SessionService` then
    reads that policy from here rather than accepting one, so the bounds a login
    is created with and the window a refresh applies come from the same
    derivation of the same configuration and cannot be made to disagree.

    Why here and not in the service: this layer is the one that must have the
    numbers, because they are compiled into the refresh statement below at
    construction time. Deriving them anywhere else would mean passing them here
    anyway, and a value passed is a value that can be a different one.
    """

    __slots__ = ("_connection", "_policy", "_touch_sql", "_touch_parameters")

    def __init__(self, connection: Connection, *, settings: SessionSettings) -> None:
        self._connection = connection
        #: Required, not defaulted. A default here would be the 60/15 literals
        #: living in the adapter, which is what the numeric-policy register
        #: exists to prevent — and it would let a construction site silently
        #: acquire bounds nobody configured.
        #:
        #: Derived, not accepted: `SessionPolicy.derive` is the only way in, and
        #: it reads each configured number exactly once before validating it. A
        #: caller therefore cannot hand over a pre-built policy that skipped
        #: validation, nor settings whose values differ between the read that was
        #: checked and the read that reaches the SQL.
        self._policy = SessionPolicy.derive(settings)
        self._touch_sql, self._touch_parameters = _touch_statement(self._policy)

    @property
    def policy(self) -> SessionPolicy:
        """The derived bounds. `SessionService` takes its own from here.

        Exposed because "the service and the refresh statement use the same
        bounds" is the property F3 was about, and it is worth being able to
        assert with `is` rather than through a private attribute. `SessionPolicy`
        is frozen and holds numbers with fixed roles rather than a method-to-
        duration mapping, so returning it widens nothing.
        """
        return self._policy

    def create(
        self,
        *,
        account_id: UUID,
        auth_method: AuthMethod,
        token_hash: bytes,
        idle_expires_at: datetime,
        absolute_expires_at: datetime,
        privilege_fingerprint: bytes,
        client_ip_hash: bytes | None = None,
        user_agent_digest: bytes | None = None,
        oauth_transaction_id: UUID | None = None,
    ) -> UUID:
        """Insert a **root** session. A rotation is `rotate()` and cannot be this.

        There is deliberately no `rotated_from` parameter (OD-44 condition 2).
        Labelling a row as a rotation is what carries an OAuth binding forward
        past the root-session unique index, so it is not something a caller may
        assert while inserting; it is the outcome of the locked predecessor read
        in `rotate()`, which takes the binding from the predecessor rather than
        from an argument.
        """
        session_id = uuid4()
        now = utcnow()
        self._connection.execute(
            insert(sessions).values(
                id=session_id,
                token_hash=token_hash,
                platform_account_id=account_id,
                auth_method=auth_method.value,
                created_at=now,
                last_seen_at=now,
                # Clamped, not merely intended: the check constraint
                # `idle_expires_at <= absolute_expires_at` makes a mistake here
                # fail loudly instead of quietly extending a session.
                idle_expires_at=min(idle_expires_at, absolute_expires_at),
                absolute_expires_at=absolute_expires_at,
                privilege_fingerprint=privilege_fingerprint,
                rotated_from_session_id=None,
                client_ip_hash=client_ip_hash,
                user_agent_digest=user_agent_digest,
                # OD-44. Passed straight through and never defaulted: a caller
                # that omits it for a `discord_oauth` session is refused by
                # `ck_sessions_oauth_transaction_binding`, which is the point.
                oauth_transaction_id=oauth_transaction_id,
            )
        )
        return session_id

    def rotate(
        self,
        *,
        predecessor_id: UUID,
        expected_account_id: UUID,
        expected_auth_method: AuthMethod,
        token_hash: bytes,
        idle_expires_at: datetime,
        privilege_fingerprint: bytes,
        now: datetime,
        revocation_reason: str,
        client_ip_hash: bytes | None = None,
        user_agent_digest: bytes | None = None,
    ) -> RotatedSession | None:
        """One transactional operation: lock, verify, insert the successor, revoke.

        OD-44 condition 2. Rotation is the one place `rotated_from_session_id` is
        ever written, and everything the successor inherits — account,
        authentication method, OAuth binding, **absolute expiration** — is read
        from the **locked predecessor row**, not from an argument. A caller
        therefore cannot rotate a session into another account, into another
        authentication method, onto another login's OAuth transaction, or into a
        longer life than the login it descends from, because it has nothing to
        say about those values.

        The order is deliberate and the lock is the whole mechanism:

        1. `SELECT … FOR UPDATE` the predecessor, requiring it to be **live** —
           `revoked_at IS NULL` **and** `idle_expires_at > :now` **and**
           `absolute_expires_at > :now` — and **unrotated** (no row already names
           it). Liveness is the one fact PostgreSQL cannot express declaratively
           — it is a `now()` comparison — so it is enforced here, under the lock;
        2. insert the successor from the locked row's own values;
        3. revoke the predecessor with the same `revoked_at IS NULL` predicate.

        **Both expiry predicates are part of liveness, and the correction on
        2026-08-14 is that they were missing.** `revoked_at IS NULL` alone
        establishes only that nobody has *ended* the session; an idle- or
        absolute-expired row is still unrevoked until some read observes it. A
        caller holding a `SessionRecord` resolved while the session was valid
        could therefore rotate it afterwards and receive a live successor — the
        expired session revived, with the same account, capabilities and OAuth
        binding. `resolve()` refusing the record first is not the control: the
        record is a value the caller already holds, and this operation is the
        serialization boundary, so the comparison has to be in the locked
        statement where nothing can pass it a stale answer.

        **The successor inherits the predecessor's `absolute_expires_at`
        exactly**, and its idle expiration is clamped to that inheritance. A
        fresh `now + bounds.absolute` would let repeated privilege-change
        rotations extend one login without limit, which defeats N-07 for ordinary
        sessions and directly violates N-15's "60-minute absolute expiry […] no
        extension beyond the absolute bound" for break-glass ones. So the whole
        chain from one login carries one absolute bound, set by that login, and
        the caller supplies no absolute expiration at all.

        Two concurrent rotations of one session meet at step 1. The loser blocks
        on the winner's row lock, re-evaluates the predicate under `READ
        COMMITTED` once the winner commits, sees a revoked predecessor, matches
        zero rows and returns `None`. There is no sleep and no retry: the outcome
        is decided by PostgreSQL. The partial unique index
        `uq_sessions_rotated_from_session_id` refuses a second successor from a
        different direction, and the two composite rotation foreign keys refuse a
        crossing one, so none of this rests on the statements below being the only
        writer.

        Returns the successor and the bounds it was persisted with, or `None`
        when the predecessor cannot be rotated — unknown, revoked, idle-expired,
        absolute-expired, already rotated, or belonging to another account or
        authentication method. `None` is a refusal, not a retry signal, and the
        caller's transaction is what makes any of it durable.
        """
        predecessor = (
            self._connection.execute(
                text(
                    """
                    SELECT id, platform_account_id, auth_method,
                           oauth_transaction_id, absolute_expires_at
                      FROM sessions predecessor
                     WHERE id = :id
                       AND revoked_at IS NULL
                       AND idle_expires_at > CAST(:now AS timestamptz)
                       AND absolute_expires_at > CAST(:now AS timestamptz)
                       AND NOT EXISTS (
                           SELECT 1
                             FROM sessions successor
                            WHERE successor.rotated_from_session_id = predecessor.id
                       )
                       FOR UPDATE
                    """
                ),
                {"id": predecessor_id, "now": now},
            )
            .mappings()
            .one_or_none()
        )
        if predecessor is None:
            return None
        if (
            predecessor["platform_account_id"] != expected_account_id
            or predecessor["auth_method"] != expected_auth_method.value
        ):
            # The caller believes it is rotating a session it is not. Refused
            # rather than silently rotating the row that actually exists: the
            # composite foreign keys would refuse the insert anyway, and an
            # `IntegrityError` at that point would surface as a `500` where a
            # typed refusal belongs.
            return None

        # The login's absolute bound, not this rotation's. Read from the locked
        # row, so the chain's lifetime is decided once, by the login at its root.
        absolute_expires_at = predecessor["absolute_expires_at"]
        successor_idle_expires_at = min(idle_expires_at, absolute_expires_at)

        session_id = uuid4()
        self._connection.execute(
            insert(sessions).values(
                id=session_id,
                token_hash=token_hash,
                # The predecessor's own values, from the row this transaction
                # holds locked. Not the caller's, which is the point.
                platform_account_id=predecessor["platform_account_id"],
                auth_method=predecessor["auth_method"],
                created_at=now,
                last_seen_at=now,
                idle_expires_at=successor_idle_expires_at,
                absolute_expires_at=absolute_expires_at,
                privilege_fingerprint=privilege_fingerprint,
                rotated_from_session_id=predecessor["id"],
                client_ip_hash=client_ip_hash,
                user_agent_digest=user_agent_digest,
                oauth_transaction_id=predecessor["oauth_transaction_id"],
            )
        )
        revoked = self._connection.execute(
            update(sessions)
            .where(sessions.c.id == predecessor_id, sessions.c.revoked_at.is_(None))
            .values(revoked_at=now, revocation_reason=revocation_reason)
        )
        if not revoked.rowcount:
            # Unreachable while the lock is held — nothing else can revoke a row
            # this transaction has locked — and asserted rather than assumed,
            # because "the predecessor survived its own rotation" would leave two
            # live sessions for one login, which is the state this method exists
            # to make impossible.
            raise RuntimeError(
                "rotation could not revoke the predecessor it holds locked"
            )
        return RotatedSession(
            id=session_id,
            idle_expires_at=successor_idle_expires_at,
            absolute_expires_at=absolute_expires_at,
        )

    def resolve(self, token_hash: bytes, *, now: datetime) -> SessionRecord | None:
        """Look up a live session, and mark an expired one revoked as we pass.

        Expiry is evaluated **server-side on every request**. There is no cache
        of "this session was valid": that cache is exactly what would let a
        revoked session serve one more request.
        """
        row = (
            self._connection.execute(
                select(sessions).where(sessions.c.token_hash == token_hash)
            )
            .mappings()
            .one_or_none()
        )
        if row is None:
            return None
        if row["revoked_at"] is not None:
            return None
        if row["idle_expires_at"] <= now or row["absolute_expires_at"] <= now:
            self.revoke(row["id"], reason="expired", at=now)
            return None
        return SessionRecord(
            id=row["id"],
            platform_account_id=row["platform_account_id"],
            auth_method=AuthMethod(row["auth_method"]),
            created_at=row["created_at"],
            idle_expires_at=row["idle_expires_at"],
            absolute_expires_at=row["absolute_expires_at"],
            privilege_fingerprint=row["privilege_fingerprint"],
            revoked_at=None,
            oauth_transaction_id=row["oauth_transaction_id"],
        )

    def touch(self, session_id: UUID, *, now: datetime) -> TouchedSession | None:
        """Extend the idle window of a **live** session, never past its bound.

        **The caller supplies an id and an instant, and nothing else** (corrected
        2026-08-15, second session-lifetime review). This method previously took
        `idle` and `expected_auth_method` as independent arguments and verified
        only that the method matched the row. That predicate refuses a *false
        method*; it cannot see a false **duration** beside a true one. So
        `touch(break_glass_id, idle=60 minutes, expected_auth_method=WEBAUTHN)`
        matched the row and pushed its idle window out to the emergency absolute
        bound — N-15's fifteen minutes bypassed while every stated check passed.
        The service had already been corrected to select the right duration; this
        API sat below it and did not require anyone to.

        There is now no duration to pass. The window comes from the
        `SessionPolicy` this repository derived from its configuration, and the
        `CASE` in the statement selects from it by the `auth_method` **the row
        itself carries** — inside the same write, so the choice cannot be made
        from a value that has gone stale, and outside the reach of every caller.

        One conditional `UPDATE`. Every condition on which the refresh depends is
        in that statement, because the write is the serialization boundary and
        anything checked before it is a value the caller already holds:

        1. `revoked_at IS NULL` — nobody has ended the session;
        2. `idle_expires_at > :now` **and** `absolute_expires_at > :now` — it is
           strictly inside both bounds. **Corrected 2026-08-15: these were
           missing**, and they are the same stale-record class corrected in
           `rotate()` on 2026-08-14. `revoked_at IS NULL` alone establishes only
           that nobody *ended* the session; an idle-expired row stays unrevoked
           until some read observes it, so a caller holding a `SessionRecord`
           resolved while the session was valid could touch it after its idle
           bound and push `idle_expires_at` back into the future — reviving an
           expired session between its idle and absolute bounds. Calling
           `resolve()` first is not the control: time advances after resolution;
        3. `auth_method IN (…)` — the row's method is one the configured policy
           governs, so the `CASE` beside it always chooses a window. This is not
           an authorization check and no caller can influence it; it exists so an
           ungoverned method is refused rather than silently given the row's
           absolute bound through a `NULL` interval.

        Both expiry comparisons are strict. Equality at either bound is expired —
        a session whose idle window ends exactly now cannot refresh itself —
        which matches `resolve()`'s `<=` refusal and the rotation predicates.

        The clamp is in the statement rather than in Python so a caller cannot
        pass a later value and have it taken, and `absolute_expires_at` appears
        in no `SET` clause: touch never moves the bound the login set.

        Returns the persisted bounds, or `None` when no row matched — unknown,
        revoked, idle-expired or absolute-expired. `None` is a refusal, not a
        retry signal: a refused touch writes nothing at all, because the single
        statement that would have written `last_seen_at` and `idle_expires_at`
        matched zero rows.
        """
        row = (
            self._connection.execute(
                self._touch_sql,
                {**self._touch_parameters, "now": now, "id": session_id},
            )
            .mappings()
            .one_or_none()
        )
        if row is None:
            return None
        return TouchedSession(
            id=row["id"],
            last_seen_at=row["last_seen_at"],
            idle_expires_at=row["idle_expires_at"],
            absolute_expires_at=row["absolute_expires_at"],
        )

    def revoke(self, session_id: UUID, *, reason: str, at: datetime) -> None:
        self._connection.execute(
            update(sessions)
            .where(sessions.c.id == session_id, sessions.c.revoked_at.is_(None))
            .values(revoked_at=at, revocation_reason=reason)
        )

    def revoke_all_for_account(
        self, account_id: UUID, *, reason: str, at: datetime
    ) -> int:
        result = self._connection.execute(
            update(sessions)
            .where(
                sessions.c.platform_account_id == account_id,
                sessions.c.revoked_at.is_(None),
            )
            .values(revoked_at=at, revocation_reason=reason)
        )
        return result.rowcount or 0

    def live_sessions(self, account_id: UUID, *, now: datetime) -> list[SessionRecord]:
        rows = (
            self._connection.execute(
                select(sessions)
                .where(
                    sessions.c.platform_account_id == account_id,
                    sessions.c.revoked_at.is_(None),
                    sessions.c.absolute_expires_at > now,
                    sessions.c.idle_expires_at > now,
                )
                .order_by(sessions.c.created_at)
            )
            .mappings()
            .all()
        )
        return [
            SessionRecord(
                id=row["id"],
                platform_account_id=row["platform_account_id"],
                auth_method=AuthMethod(row["auth_method"]),
                created_at=row["created_at"],
                idle_expires_at=row["idle_expires_at"],
                absolute_expires_at=row["absolute_expires_at"],
                privilege_fingerprint=row["privilege_fingerprint"],
                revoked_at=None,
                oauth_transaction_id=row["oauth_transaction_id"],
            )
            for row in rows
        ]


# ---------------------------------------------------------------------------
# OAuth transactions
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class ConsumedTransaction:
    """What a callback recovers, once, from a transaction it just consumed."""

    verifier: Sealed
    return_path: str
    provider_key: str


class OAuthTransactionRepository:
    """`oauth_transactions`: one in-flight login attempt (SM-01)."""

    __slots__ = ("_connection",)

    def __init__(self, connection: Connection) -> None:
        self._connection = connection

    def create(
        self,
        *,
        state_hash: bytes,
        verifier: Sealed,
        return_path: str,
        provider_key: str,
        expires_at: datetime,
        client_ip_hash: bytes | None,
        transaction_id: UUID | None = None,
    ) -> UUID:
        # The caller may supply the id, and the OAuth service does: the id is
        # part of the ciphertext's additional authenticated data, so it has to
        # exist before the row does. A repository that minted its own would make
        # the binding impossible to compute.
        transaction_id = transaction_id or uuid4()
        self._connection.execute(
            insert(oauth_transactions).values(
                id=transaction_id,
                state_hash=state_hash,
                pkce_verifier_ciphertext=verifier.ciphertext,
                nonce=verifier.nonce,
                key_version=verifier.key_version,
                return_path=return_path,
                provider_key=provider_key,
                created_at=utcnow(),
                expires_at=expires_at,
                client_ip_hash=client_ip_hash,
            )
        )
        return transaction_id

    def consume(
        self, *, transaction_id: UUID, state_hash: bytes, now: datetime
    ) -> ConsumedTransaction | None:
        """Recover the verifier and erase it, in one statement.

        The CTE returns the values as they were *before* the update, so the
        callback gets the verifier it needs while the row is emptied of it in the
        same pass. Under `READ COMMITTED` a second concurrent callback blocks on
        `FOR UPDATE`, re-checks `consumed_at IS NULL` when the lock is released,
        matches zero rows, and is refused. Replay, race and retry all end in the
        same place, and after any of them the ciphertext is gone.

        The `state_hash` is compared **inside** the statement rather than by the
        caller. A caller-side comparison would be a second place to get constant
        time wrong, and would leave a window between checking and consuming.
        """
        row = (
            self._connection.execute(
                text(
                    """
                    WITH claimed AS (
                        SELECT id, pkce_verifier_ciphertext, nonce, key_version,
                               return_path, provider_key
                          FROM oauth_transactions
                         WHERE id = :id
                           AND state_hash = :state_hash
                           AND consumed_at IS NULL
                           AND expires_at > :now
                           FOR UPDATE
                    )
                    UPDATE oauth_transactions t
                       SET consumed_at = :now,
                           pkce_verifier_ciphertext = NULL,
                           nonce = NULL
                      FROM claimed c
                     WHERE t.id = c.id
                    RETURNING c.pkce_verifier_ciphertext AS ciphertext,
                              c.nonce AS nonce,
                              c.key_version AS key_version,
                              c.return_path AS return_path,
                              c.provider_key AS provider_key
                    """
                ),
                {"id": transaction_id, "state_hash": state_hash, "now": now},
            )
            .mappings()
            .one_or_none()
        )
        if row is None or row["ciphertext"] is None:
            return None
        return ConsumedTransaction(
            verifier=Sealed(
                ciphertext=bytes(row["ciphertext"]),
                nonce=bytes(row["nonce"]),
                key_version=row["key_version"],
            ),
            return_path=row["return_path"],
            provider_key=row["provider_key"],
        )

    def claim_completion(
        self, *, transaction_id: UUID, provider_key: str, now: datetime
    ) -> bool:
        """OD-44. Take the one completion this transaction will ever have.

        The second serialization point of SM-01, and the one that survives the
        provider round trip. `consume()` proves a live, browser-bound transaction
        existed *before* Discord was contacted; this proves that the completion
        being performed *after* Discord answered is the only one that transaction
        will ever produce, **and that it is being performed by the provider the
        transaction was started with**.

        Four predicates, and each refuses a different thing:

        - `id = :id` — an unknown id. A caller that invented one is refused from
          durable state rather than by an argument nobody checked.
        - `consumed_at IS NOT NULL` — a transaction that never gave up its
          verifier, so no provider exchange can have happened for it.
        - `completion_claimed_at IS NULL` — a second completion. Under `READ
          COMMITTED` a concurrent claim blocks on the row lock, re-evaluates when
          it is released, and matches zero rows.
        - `provider_key = :provider_key` — a completion carrying a *different*
          provider's verified result. The row records which provider the browser
          was sent to at `start()`; the argument is derived from the verified
          result that is being completed. A caller holding provider B's identity
          and tokens cannot spend a transaction issued for provider A, and the
          refusal is durable rather than a route-ordering accident.

        The provider predicate is in **this** statement rather than in a separate
        read for the same reason the `state_hash` comparison is inside `consume()`:
        a check that is not part of the claiming update is a check with a window
        between it and the claim.

        Returns whether the claim was taken. **Zero rows is a refusal, not a
        warning**: the caller must not create a session, and the whole completion
        transaction rolls back with it.
        """
        result = self._connection.execute(
            text(
                """
                UPDATE oauth_transactions
                   SET completion_claimed_at = :now
                 WHERE id = :id
                   AND consumed_at IS NOT NULL
                   AND completion_claimed_at IS NULL
                   AND provider_key = :provider_key
                RETURNING id
                """
            ),
            {"id": transaction_id, "now": now, "provider_key": provider_key},
        )
        return result.one_or_none() is not None

    def purge_expired(self, *, before: datetime) -> int:
        """N-04's reaper, which now has to step around a live session's origin row.

        A session outlives its transaction by design — twelve hours against ten
        minutes — so from OD-44 onward the purge meets referenced rows in
        *ordinary* operation, not only in a contrived case. `RESTRICT` would make
        that an error and take the whole cleanup down with it.

        So the referenced rows are skipped rather than attempted. `RESTRICT`
        remains the backstop for anything that deletes without this predicate: a
        session whose origin row had been removed would be a session nobody could
        trace back to a login, and that must be impossible rather than merely
        avoided here. The skipped rows become deletable when the sessions naming
        them are cleaned up under the 30-day session retention (schema §9.1).
        """
        result = self._connection.execute(
            delete(oauth_transactions).where(
                oauth_transactions.c.expires_at < before,
                ~select(sessions.c.id)
                .where(sessions.c.oauth_transaction_id == oauth_transactions.c.id)
                .exists(),
            )
        )
        return result.rowcount or 0


# ---------------------------------------------------------------------------
# Provider token storage
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class StoredGrant:
    """One live `oauth_token_grants` row, still encrypted.

    The ciphertext is handed out rather than the token: opening it needs the
    envelope and the AAD that binds it to *this* grant and *this* identity, so a
    ciphertext lifted from another row fails to authenticate instead of
    decrypting into somebody else's access token (schema §9.5).
    """

    grant_id: UUID
    external_identity_id: UUID
    access: Sealed
    scopes: str
    access_expires_at: datetime


class TokenGrantRepository:
    """Encrypted provider tokens, kept only while the session needs them (N-11)."""

    __slots__ = ("_connection",)

    def __init__(self, connection: Connection) -> None:
        self._connection = connection

    def replace(
        self,
        *,
        external_identity_id: UUID,
        access: Sealed,
        refresh: Sealed | None,
        scopes: str,
        access_expires_at: datetime,
        grant_id: UUID | None = None,
    ) -> UUID:
        # One live grant per identity: the previous one is deleted rather than
        # marked, because N-11 is a deletion rule and a soft-deleted token is
        # still a token.
        self._connection.execute(
            delete(oauth_token_grants).where(
                oauth_token_grants.c.external_identity_id == external_identity_id
            )
        )
        grant_id = grant_id or uuid4()
        self._connection.execute(
            insert(oauth_token_grants).values(
                id=grant_id,
                external_identity_id=external_identity_id,
                access_token_ciphertext=access.ciphertext,
                nonce=access.nonce,
                refresh_token_ciphertext=None if refresh is None else refresh.ciphertext,
                refresh_nonce=None if refresh is None else refresh.nonce,
                key_version=access.key_version,
                scopes=scopes,
                access_expires_at=access_expires_at,
            )
        )
        return grant_id

    def delete_for_account(self, account_id: UUID) -> int:
        result = self._connection.execute(
            delete(oauth_token_grants).where(
                oauth_token_grants.c.external_identity_id.in_(
                    select(external_identities.c.id).where(
                        external_identities.c.platform_account_id == account_id
                    )
                )
            )
        )
        return result.rowcount or 0

    def load(self, external_identity_id: UUID) -> "StoredGrant | None":
        """The live grant for one identity, as it was stored.

        Returns a record rather than a tuple because P3.2's membership refresh
        (N-09) has to rebuild a `ProviderTokens` to hand back to
        `IdentityProvider.verify()`, and every field of that object must be a
        value this platform actually persisted. A refresh that invented a scope
        string or an expiry to fill the shape would be presenting a token result
        the platform never received — and the provider binding exists precisely
        so that a token result cannot say something nobody observed.
        """
        row = (
            self._connection.execute(
                select(oauth_token_grants).where(
                    oauth_token_grants.c.external_identity_id == external_identity_id,
                    oauth_token_grants.c.deleted_at.is_(None),
                )
            )
            .mappings()
            .one_or_none()
        )
        if row is None:
            return None
        return StoredGrant(
            grant_id=row["id"],
            external_identity_id=external_identity_id,
            access=Sealed(
                ciphertext=bytes(row["access_token_ciphertext"]),
                nonce=bytes(row["nonce"]),
                key_version=row["key_version"],
            ),
            scopes=row["scopes"],
            access_expires_at=row["access_expires_at"],
        )


# ---------------------------------------------------------------------------
# Break-glass credentials and grants
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class CredentialRecord:
    id: UUID
    platform_account_id: UUID
    credential_id: bytes
    public_key: bytes
    sign_count: int
    nickname: str | None


class WebAuthnRepository:
    """Pre-enrolled credentials and the challenges they answer (schema §9.3)."""

    __slots__ = ("_connection",)

    def __init__(self, connection: Connection) -> None:
        self._connection = connection

    def enabled_credentials(self, account_id: UUID) -> list[CredentialRecord]:
        rows = (
            self._connection.execute(
                select(webauthn_credentials).where(
                    webauthn_credentials.c.platform_account_id == account_id,
                    webauthn_credentials.c.disabled_at.is_(None),
                )
            )
            .mappings()
            .all()
        )
        return [
            CredentialRecord(
                id=row["id"],
                platform_account_id=row["platform_account_id"],
                credential_id=bytes(row["credential_id"]),
                public_key=bytes(row["public_key"]),
                sign_count=row["sign_count"],
                nickname=row["nickname"],
            )
            for row in rows
        ]

    def find_by_credential_id(self, credential_id: bytes) -> CredentialRecord | None:
        row = (
            self._connection.execute(
                select(webauthn_credentials).where(
                    webauthn_credentials.c.credential_id == credential_id,
                    webauthn_credentials.c.disabled_at.is_(None),
                )
            )
            .mappings()
            .one_or_none()
        )
        if row is None:
            return None
        return CredentialRecord(
            id=row["id"],
            platform_account_id=row["platform_account_id"],
            credential_id=bytes(row["credential_id"]),
            public_key=bytes(row["public_key"]),
            sign_count=row["sign_count"],
            nickname=row["nickname"],
        )

    def enroll(
        self,
        *,
        account_id: UUID,
        credential_id: bytes,
        public_key: bytes,
        sign_count: int,
        operator: str,
        nickname: str | None,
        transports: str | None,
        aaguid: UUID | None,
    ) -> UUID:
        record_id = uuid4()
        self._connection.execute(
            insert(webauthn_credentials).values(
                id=record_id,
                platform_account_id=account_id,
                credential_id=credential_id,
                public_key=public_key,
                sign_count=sign_count,
                aaguid=aaguid,
                transports=transports,
                nickname=nickname,
                created_by_operator=operator,
            )
        )
        return record_id

    def advance_sign_count(
        self, credential_record_id: UUID, *, sign_count: int, at: datetime
    ) -> None:
        self._connection.execute(
            update(webauthn_credentials)
            .where(webauthn_credentials.c.id == credential_record_id)
            .values(sign_count=sign_count, last_used_at=at)
        )

    def disable(self, credential_record_id: UUID, *, at: datetime) -> None:
        self._connection.execute(
            update(webauthn_credentials)
            .where(webauthn_credentials.c.id == credential_record_id)
            .values(disabled_at=at)
        )

    def issue_challenge(
        self, *, challenge: bytes, expires_at: datetime, client_ip_hash: bytes | None
    ) -> UUID:
        challenge_id = uuid4()
        self._connection.execute(
            insert(webauthn_challenges).values(
                id=challenge_id,
                challenge=challenge,
                expires_at=expires_at,
                client_ip_hash=client_ip_hash,
            )
        )
        return challenge_id

    def consume_challenge(self, *, challenge: bytes, now: datetime) -> bool:
        """Single use, by the same conditional-update pattern as everything else."""
        result = self._connection.execute(
            update(webauthn_challenges)
            .where(
                webauthn_challenges.c.challenge == challenge,
                webauthn_challenges.c.consumed_at.is_(None),
                webauthn_challenges.c.expires_at > now,
            )
            .values(consumed_at=now)
        )
        return (result.rowcount or 0) == 1

    def purge_expired_challenges(self, *, before: datetime) -> int:
        result = self._connection.execute(
            delete(webauthn_challenges).where(webauthn_challenges.c.expires_at < before)
        )
        return result.rowcount or 0


@dataclass(frozen=True, slots=True)
class GrantRecord:
    id: UUID
    platform_account_id: UUID


class RecoveryGrantRepository:
    """Host-issued, hashed, single-use, ten-minute grants (N-14, N-61)."""

    __slots__ = ("_connection",)

    def __init__(self, connection: Connection) -> None:
        self._connection = connection

    def issue(
        self,
        *,
        account_id: UUID,
        token_hash: bytes,
        expires_at: datetime,
        operator: str,
        correlation_id: UUID,
    ) -> UUID:
        """Issuing invalidates any prior live grant **in the same transaction**.

        N-61: two live grants double the window with no operational benefit. The
        partial unique index would refuse the second insert anyway; doing the
        invalidation explicitly is what makes the outcome an invalidated grant
        with a reason rather than an error the operator has to interpret.
        """
        now = utcnow()
        self._connection.execute(
            update(recovery_grants)
            .where(
                recovery_grants.c.platform_account_id == account_id,
                recovery_grants.c.consumed_at.is_(None),
                recovery_grants.c.invalidated_at.is_(None),
            )
            .values(invalidated_at=now, invalidated_reason="superseded_by_new_grant")
        )
        grant_id = uuid4()
        self._connection.execute(
            insert(recovery_grants).values(
                id=grant_id,
                platform_account_id=account_id,
                token_hash=token_hash,
                purpose="emergency_login",
                created_at=now,
                expires_at=expires_at,
                created_by_operator=operator,
                audit_correlation_id=correlation_id,
            )
        )
        return grant_id

    def invalidate_all(self, *, account_id: UUID, reason: str) -> int:
        result = self._connection.execute(
            update(recovery_grants)
            .where(
                recovery_grants.c.platform_account_id == account_id,
                recovery_grants.c.consumed_at.is_(None),
                recovery_grants.c.invalidated_at.is_(None),
            )
            .values(invalidated_at=utcnow(), invalidated_reason=reason)
        )
        return result.rowcount or 0

    def note_attempt(self, *, token_hash: bytes) -> int:
        """Count an attempt against the grant record itself (N-33's per-grant bound).

        Deliberately not conditional on the grant being live: an attempt against
        an expired or already-consumed grant is exactly the attempt worth
        counting.

        **One statement, and it returns the count it wrote** (2026-08-16, P3.G1
        security review). Incrementing and then reading in a second statement
        left two concurrent attempts able to read the same number, which is the
        `check_ip` mistake N-30 avoided by construction; `RETURNING` makes the
        increment and the reading of it the same operation. A token matching no
        grant updates no row and returns zero — no row is created, so an
        attacker cannot grow this table with invented tokens.
        """
        value = self._connection.execute(
            update(recovery_grants)
            .where(recovery_grants.c.token_hash == token_hash)
            .values(attempt_count=recovery_grants.c.attempt_count + 1)
            .returning(recovery_grants.c.attempt_count)
        ).scalar_one_or_none()
        return int(value or 0)

    def attempts_for(self, *, token_hash: bytes) -> int:
        """The durable count, read without spending one. Zero for no such grant."""
        value = self._connection.execute(
            select(recovery_grants.c.attempt_count).where(
                recovery_grants.c.token_hash == token_hash
            )
        ).scalar_one_or_none()
        return int(value or 0)

    def consume(
        self, *, token_hash: bytes, session_id: UUID, now: datetime
    ) -> GrantRecord | None:
        """One statement. Replay, expiry and concurrency all yield zero rows."""
        row = (
            self._connection.execute(
                text(
                    """
                    UPDATE recovery_grants
                       SET consumed_at = :now, consumed_session_id = :session
                     WHERE token_hash = :token_hash
                       AND purpose = 'emergency_login'
                       AND consumed_at IS NULL
                       AND invalidated_at IS NULL
                       AND expires_at > :now
                    RETURNING id, platform_account_id
                    """
                ),
                {"now": now, "session": session_id, "token_hash": token_hash},
            )
            .mappings()
            .one_or_none()
        )
        if row is None:
            return None
        return GrantRecord(id=row["id"], platform_account_id=row["platform_account_id"])


# ---------------------------------------------------------------------------
# Rate limiting
# ---------------------------------------------------------------------------


class RateLimitRepository:
    """The shared fixed-window counter of N-30."""

    __slots__ = ("_connection",)

    def __init__(self, connection: Connection) -> None:
        self._connection = connection

    def increment(self, *, bucket: str, window_start: datetime) -> int:
        """One statement, so two processes cannot both read 9 and both write 10."""
        statement = (
            pg_insert(auth_rate_limits)
            .values(bucket=bucket, window_start=window_start, count=1)
            .on_conflict_do_update(
                index_elements=[auth_rate_limits.c.bucket, auth_rate_limits.c.window_start],
                set_={"count": auth_rate_limits.c.count + 1},
            )
            .returning(auth_rate_limits.c.count)
        )
        return int(self._connection.execute(statement).scalar_one())

    def purge(self, *, before: datetime) -> int:
        result = self._connection.execute(
            delete(auth_rate_limits).where(auth_rate_limits.c.window_start < before)
        )
        return result.rowcount or 0


# ---------------------------------------------------------------------------
# Role-capability mappings and the membership projection
# ---------------------------------------------------------------------------


class RoleMappingRepository:
    """`role_capability_mappings` and its append-only event log (schema §8)."""

    __slots__ = ("_connection",)

    def __init__(self, connection: Connection) -> None:
        self._connection = connection

    def active_mappings(self, guild_id: int) -> list[RoleCapabilityMapping]:
        rows = (
            self._connection.execute(
                select(role_capability_mappings).where(
                    role_capability_mappings.c.guild_id == guild_id,
                    role_capability_mappings.c.active,
                )
            )
            .mappings()
            .all()
        )
        return [
            RoleCapabilityMapping(
                id=row["id"],
                guild_id=row["guild_id"],
                role_id=row["role_id"],
                capability=ActorCapability(row["capability"]),
                provenance=MappingProvenance(row["provenance"]),
                protected=row["protected"],
            )
            for row in rows
        ]

    def rows_for_guild(self, guild_id: int, *, limit: int):
        """Every **active** mapping for one guild, in full, for R-32's screen.

        `active_mappings()` above answers capability resolution and returns only
        what a decision needs. This returns the whole row, because the
        administration screen has to show provenance, the creating session's
        authentication method, the optimistic version each control submits back,
        and who ratified what — none of which an authorization decision may ever
        consult.

        Ordered by capability then role so the page is stable, and bounded by
        N-62's fifty: an unbounded render is an availability defect, and a guild
        cannot hold more than that many active mappings anyway.
        """
        return list(
            self._connection.execute(
                select(role_capability_mappings)
                .where(
                    role_capability_mappings.c.guild_id == guild_id,
                    role_capability_mappings.c.active.is_(True),
                )
                .order_by(
                    role_capability_mappings.c.capability,
                    role_capability_mappings.c.role_id,
                )
                .limit(limit)
            )
            .mappings()
            .all()
        )

    def get(self, mapping_id: UUID):
        return (
            self._connection.execute(
                select(role_capability_mappings).where(
                    role_capability_mappings.c.id == mapping_id
                )
            )
            .mappings()
            .one_or_none()
        )

    def active_count(self, guild_id: int) -> int:
        return int(
            self._connection.execute(
                select(text("count(*)"))
                .select_from(role_capability_mappings)
                .where(
                    role_capability_mappings.c.guild_id == guild_id,
                    role_capability_mappings.c.active,
                )
            ).scalar_one()
        )

    def create(
        self,
        *,
        guild_id: int,
        role_id: int,
        capability: ActorCapability,
        created_by: UUID,
        auth_method: AuthMethod,
        scope: AdministratorScope,
        reason: str,
        correlation_id: UUID,
    ) -> UUID:
        """Writes the creating session's scope, so provenance travels with the row.

        `provenance` is derived here and constrained to be derived by the
        database: it is exactly "created under a continuity scope and not yet
        ratified". The application does not get to decide it independently.
        """
        provenance = (
            MappingProvenance.EMERGENCY_CONTINUITY
            if scope is AdministratorScope.EMERGENCY_CONTINUITY
            else MappingProvenance.ORDINARY
        )
        mapping_id = uuid4()
        self._connection.execute(
            insert(role_capability_mappings).values(
                id=mapping_id,
                guild_id=guild_id,
                role_id=role_id,
                capability=capability.value,
                protected=False,
                active=True,
                created_by_account_id=created_by,
                created_under_auth_method=auth_method.value,
                created_under_scope=scope.value,
                provenance=provenance.value,
                reason=reason,
                audit_correlation_id=correlation_id,
            )
        )
        return mapping_id

    def revoke(
        self,
        *,
        mapping_id: UUID,
        revoked_by: UUID,
        auth_method: AuthMethod,
        scope: AdministratorScope,
        expected_version: int,
        at: datetime,
    ) -> bool:
        result = self._connection.execute(
            update(role_capability_mappings)
            .where(
                role_capability_mappings.c.id == mapping_id,
                role_capability_mappings.c.active,
                role_capability_mappings.c.version == expected_version,
            )
            .values(
                active=False,
                revoked_at=at,
                revoked_by_account_id=revoked_by,
                revoked_under_auth_method=auth_method.value,
                revoked_under_scope=scope.value,
                version=role_capability_mappings.c.version + 1,
            )
        )
        return (result.rowcount or 0) == 1

    def ratify(
        self, *, mapping_id: UUID, ratified_by: UUID, expected_version: int, at: datetime
    ) -> bool:
        """R-38. One-way, and the trigger enforces that independently."""
        result = self._connection.execute(
            update(role_capability_mappings)
            .where(
                role_capability_mappings.c.id == mapping_id,
                role_capability_mappings.c.active,
                role_capability_mappings.c.provenance == "emergency_continuity",
                role_capability_mappings.c.version == expected_version,
            )
            .values(
                provenance="ordinary",
                ratified_at=at,
                ratified_by_account_id=ratified_by,
                version=role_capability_mappings.c.version + 1,
            )
        )
        return (result.rowcount or 0) == 1

    def record_event(
        self,
        *,
        mapping_id: UUID | None,
        operation: str,
        outcome: str,
        refusal_code: str | None,
        guild_id: int,
        role_id: int,
        capability: ActorCapability,
        actor_account_id: UUID,
        auth_method: AuthMethod,
        scope: AdministratorScope,
        reason: str | None,
        correlation_id: UUID,
    ) -> UUID:
        """Every attempt, permitted or refused.

        A refusal that leaves no trace is indistinguishable afterwards from an
        attack that never happened.
        """
        event_id = uuid4()
        self._connection.execute(
            insert(role_capability_mapping_events).values(
                id=event_id,
                mapping_id=mapping_id,
                operation=operation,
                outcome=outcome,
                refusal_code=refusal_code,
                guild_id=guild_id,
                role_id=role_id,
                capability=capability.value,
                actor_account_id=actor_account_id,
                auth_method=auth_method.value,
                scope=scope.value,
                reason=reason,
                correlation_id=correlation_id,
            )
        )
        return event_id


class MembershipProjectionRepository:
    """The Discord facts an adapter writes and authorization reads (SM-06).

    These rows stay keyed by snowflake, deliberately. A snowflake answers "who is
    this on Discord?"; it never answers "who may do this here?".
    """

    __slots__ = ("_connection",)

    def __init__(self, connection: Connection) -> None:
        self._connection = connection

    def load(self, *, discord_user_id: int, guild_id: int) -> MembershipProjection | None:
        row = (
            self._connection.execute(
                select(discord_guild_memberships).where(
                    discord_guild_memberships.c.discord_user_id == discord_user_id,
                    discord_guild_memberships.c.guild_id == guild_id,
                )
            )
            .mappings()
            .one_or_none()
        )
        if row is None:
            return None
        role_ids = set(
            self._connection.execute(
                select(discord_membership_roles.c.role_id).where(
                    discord_membership_roles.c.discord_user_id == discord_user_id,
                    discord_membership_roles.c.guild_id == guild_id,
                )
            ).scalars()
        )
        return MembershipProjection(
            guild_id=guild_id,
            is_member=row["active"],
            role_ids=frozenset(role_ids),
            observed_at=row["observed_at"],
        )

    def record(
        self,
        *,
        discord_user_id: int,
        username: str,
        global_name: str | None,
        guild_id: int,
        is_member: bool,
        role_ids: Iterable[int],
        observed_at: datetime,
    ) -> MembershipProjection:
        """Upsert what the provider just said. **A failure never writes an absence.**

        A refresh that could not reach the provider does not call this at all —
        "refresh failed" and "membership absent" are different facts, and a 429
        storm that wrote `is_member = false` would revoke a guild.
        """
        self._connection.execute(
            pg_insert(discord_users)
            .values(id=discord_user_id, username=username, global_name=global_name)
            .on_conflict_do_update(
                index_elements=["id"],
                set_={"username": username, "global_name": global_name},
            )
        )
        self._connection.execute(
            pg_insert(discord_guild_memberships)
            .values(
                discord_user_id=discord_user_id,
                guild_id=guild_id,
                active=is_member,
                observed_at=observed_at,
            )
            .on_conflict_do_update(
                index_elements=["discord_user_id", "guild_id"],
                set_={"active": is_member, "observed_at": observed_at},
            )
        )
        self._connection.execute(
            delete(discord_membership_roles).where(
                discord_membership_roles.c.discord_user_id == discord_user_id,
                discord_membership_roles.c.guild_id == guild_id,
            )
        )
        materialised = frozenset(role_ids)
        for role_id in sorted(materialised):
            self._connection.execute(
                insert(discord_membership_roles).values(
                    discord_user_id=discord_user_id, guild_id=guild_id, role_id=role_id
                )
            )
        return MembershipProjection(
            guild_id=guild_id,
            is_member=is_member,
            role_ids=materialised,
            observed_at=observed_at,
        )


def window_start(now: datetime, *, minutes: int) -> datetime:
    """Truncate `now` to the start of its fixed window (N-30)."""
    epoch_minutes = int(now.timestamp() // 60)
    aligned = epoch_minutes - (epoch_minutes % minutes)
    return datetime.fromtimestamp(aligned * 60, tz=timezone.utc)


__all__ = [
    "AccountRecord",
    "AccountRepository",
    "ConsumedTransaction",
    "CredentialRecord",
    "DISCORD_PROVIDER_KEY",
    "GrantRecord",
    "MembershipProjectionRepository",
    "OAuthTransactionRepository",
    "RateLimitRepository",
    "RecoveryGrantRepository",
    "RoleMappingRepository",
    "RotatedSession",
    "SessionRecord",
    "SessionRepository",
    "TokenGrantRepository",
    "WebAuditRepository",
    "WebAuthnRepository",
    "utcnow",
    "window_start",
]


class WebAuditRepository:
    """Append-only audit writes on the portal's own connection.

    Separate from `adapters.database.repositories.SqlAlchemyAuditRepository`
    because that one takes an ORM `Session` and this layer works in Core on an
    explicit `Connection`. The **rule** they share is the one that matters: the
    event is written in the same transaction as the change it describes, so a
    committed mutation always carries its trail and a rolled-back one leaves
    none. An emergency login that cannot be recorded does not happen (SM-03).
    """

    __slots__ = ("_connection",)

    def __init__(self, connection: Connection) -> None:
        self._connection = connection

    def record(self, event) -> None:
        from adapters.database.tables import audit_events

        self._connection.execute(
            insert(audit_events).values(
                id=event.id,
                actor_discord_user_id=event.actor_discord_user_id,
                actor_platform_account_id=event.actor_platform_account_id,
                actor_capability=event.actor_capability.value,
                action=event.action,
                entity_type=event.entity_type,
                entity_id=event.entity_id,
                source=event.source.value,
                correlation_id=event.correlation_id,
                payload=event.json_payload(),
            )
        )


# ---------------------------------------------------------------------------
# P3.2 — characters, character access, identity candidates and proposals
# ---------------------------------------------------------------------------


class CharacterAccessRepository:
    """Every read and write of `character_access`, and the character rows behind it.

    One repository for both tables because every operation here spans them: a
    grant bumps the character's optimistic version, a member's character list is
    an access-row join, and the Council index counts links per character. Two
    repositories would have meant a caller holding both and being trusted to use
    them in the right order.

    **Two invariant sets are enforced at once** until the identity migration's
    stage D (migration contract §3): the Discord-keyed indexes from migration
    0001 and the account-keyed ones from 0007. Nothing here writes
    `discord_user_id` — the stage C trigger maintains it, and it refuses a row
    whose account has no active Discord identity, which is the guard that keeps
    every authorization-bearing row expressible both ways until the legacy
    columns are dropped.
    """

    __slots__ = ("_connection",)

    def __init__(self, connection: Connection) -> None:
        self._connection = connection

    # -- characters --------------------------------------------------------
    def character(self, character_id: UUID):
        return (
            self._connection.execute(
                select(characters).where(characters.c.id == character_id)
            )
            .mappings()
            .one_or_none()
        )

    def characters_by_id(self, character_ids):
        """A bounded set of characters in one query, keyed by id.

        The identity-migration page renders one character per proposal. Reading
        them one at a time would be the N+1 the engineering rules forbid in a web
        endpoint, and it would grow with the page size the caller chooses.
        """
        wanted = list(character_ids)
        if not wanted:
            return {}
        rows = (
            self._connection.execute(
                select(characters).where(characters.c.id.in_(wanted))
            )
            .mappings()
            .all()
        )
        return {row["id"]: row for row in rows}

    def bump_character_version(
        self, *, character_id: UUID, expected_version: int, at: datetime
    ) -> int | None:
        """Take the character's optimistic version, or answer `None`.

        One conditional statement, and it is the **first** write of every
        mutation. Two Council members editing the same character meet here: the
        `WHERE version = :expected` matches for one of them and matches zero rows
        for the other, so the loser is refused before it has written anything at
        all rather than after inserting a row somebody has to remember to undo.
        """
        row = (
            self._connection.execute(
                update(characters)
                .where(
                    characters.c.id == character_id,
                    characters.c.version == expected_version,
                )
                .values(version=characters.c.version + 1, updated_at=at)
                .returning(characters.c.version)
            )
            .mappings()
            .one_or_none()
        )
        return None if row is None else row["version"]

    # -- one character's access rows ---------------------------------------
    def get(self, access_id: UUID):
        return (
            self._connection.execute(
                select(character_access).where(character_access.c.id == access_id)
            )
            .mappings()
            .one_or_none()
        )

    def access_for(self, *, character_id: UUID, account_id: UUID):
        """The caller's own **active** link to this character, or `None`.

        This is R-21's object-level authorization in one statement. It answers
        `None` both for a character this account may not reach and for a
        character that does not exist, which is what makes the two `404`s
        byte-identical (route contract §2.3).
        """
        return (
            self._connection.execute(
                select(character_access).where(
                    character_access.c.character_id == character_id,
                    character_access.c.platform_account_id == account_id,
                    character_access.c.active.is_(True),
                )
            )
            .mappings()
            .one_or_none()
        )

    def active_owner(self, character_id: UUID):
        return (
            self._connection.execute(
                select(character_access).where(
                    character_access.c.character_id == character_id,
                    character_access.c.active.is_(True),
                    character_access.c.access_kind == "owner",
                )
            )
            .mappings()
            .one_or_none()
        )

    def active_default_for_account(self, account_id: UUID):
        return (
            self._connection.execute(
                select(character_access).where(
                    character_access.c.platform_account_id == account_id,
                    character_access.c.active.is_(True),
                    character_access.c.default_character.is_(True),
                )
            )
            .mappings()
            .one_or_none()
        )

    def active_links(self, character_id: UUID, *, limit: int):
        return list(
            self._connection.execute(
                select(character_access)
                .where(
                    character_access.c.character_id == character_id,
                    character_access.c.active.is_(True),
                )
                .order_by(character_access.c.granted_at, character_access.c.id)
                .limit(limit)
            )
            .mappings()
            .all()
        )

    def historical_links(
        self, character_id: UUID, *, after: tuple[str, str] | None, limit: int
    ):
        """Revoked rows, newest first, cursor-paginated.

        The order is `(revoked_at DESC, id DESC)` and the cursor carries both,
        so it is total: two revocations in the same microsecond still have a
        strict order and neither is skipped at a page boundary.
        """
        statement = select(character_access).where(
            character_access.c.character_id == character_id,
            character_access.c.active.is_(False),
        )
        if after is not None:
            moment, identifier = after
            # `(revoked_at, id) < (:at, :id)` written out rather than as a row
            # comparison, because the descending order above pairs with a strict
            # "everything after this position" and a row constructor would need
            # the same two branches anyway. `id` breaks the tie, so the order is
            # total and no row is skipped when two revocations share an instant.
            statement = statement.where(
                or_(
                    character_access.c.revoked_at < moment,
                    and_(
                        character_access.c.revoked_at == moment,
                        character_access.c.id < identifier,
                    ),
                )
            )
        return list(
            self._connection.execute(
                statement.order_by(
                    character_access.c.revoked_at.desc(), character_access.c.id.desc()
                ).limit(limit)
            )
            .mappings()
            .all()
        )

    def active_link_count(self, character_id: UUID) -> int:
        return int(
            self._connection.execute(
                select(func.count())
                .select_from(character_access)
                .where(
                    character_access.c.character_id == character_id,
                    character_access.c.active.is_(True),
                )
            ).scalar_one()
        )

    # -- R-20 --------------------------------------------------------------
    def characters_for_account(self, account_id: UUID, *, limit: int):
        """R-20's whole query: the caller's active links and their characters.

        One statement with the snapshot provenance joined in, rather than a
        lookup per row. Ordered default-first, then display name, then id, so
        the page is stable across reloads and the truncation bound cuts the same
        rows every time.
        """
        latest = (
            select(
                external_actor_mappings.c.character_id.label("character_id"),
                foundry_snapshots.c.checksum.label("checksum"),
                foundry_snapshots.c.world_id.label("snapshot_world_id"),
                foundry_snapshots.c.exported_at.label("exported_at"),
            )
            .select_from(
                external_actor_mappings.outerjoin(
                    foundry_snapshots,
                    foundry_snapshots.c.id
                    == external_actor_mappings.c.established_by_snapshot_id,
                )
            )
            .subquery()
        )
        return list(
            self._connection.execute(
                select(
                    characters.c.id,
                    characters.c.display_name,
                    characters.c.level,
                    characters.c.active,
                    character_access.c.access_kind,
                    character_access.c.default_character,
                    latest.c.checksum,
                    latest.c.snapshot_world_id,
                    latest.c.exported_at,
                )
                .select_from(
                    character_access.join(
                        characters, characters.c.id == character_access.c.character_id
                    ).outerjoin(latest, latest.c.character_id == characters.c.id)
                )
                .where(
                    character_access.c.platform_account_id == account_id,
                    character_access.c.active.is_(True),
                )
                .order_by(
                    character_access.c.default_character.desc(),
                    characters.c.display_name,
                    characters.c.id,
                )
                .limit(limit)
            )
            .mappings()
            .all()
        )

    # -- R-22 --------------------------------------------------------------
    def council_index(
        self,
        *,
        query: str | None,
        include_inactive: bool,
        after: tuple[str, str] | None,
        limit: int,
    ):
        """A bounded, cursor-paginated character index for Council.

        `query` is a **display-name** search and is a search fact only: the row
        it finds is identified by its stable id, and nothing downstream is keyed
        by the name that matched. Matching is case-insensitive containment over
        the same NFC-normalised text `domain/names.py` defines as the identity
        key, so a search behaves the way the platform's own comparison does
        rather than the way one `LIKE` happens to.

        Ordering is `(display_name, id)`, which is total because `id` is a
        primary key.
        """
        statement = select(
            characters.c.id,
            characters.c.display_name,
            characters.c.level,
            characters.c.active,
        )
        if not include_inactive:
            statement = statement.where(characters.c.active.is_(True))
        if query:
            statement = statement.where(
                func.lower(characters.c.display_name).contains(query.casefold())
            )
        if after is not None:
            name, identifier = after
            statement = statement.where(
                or_(
                    characters.c.display_name > name,
                    and_(
                        characters.c.display_name == name,
                        characters.c.id > identifier,
                    ),
                )
            )
        return list(
            self._connection.execute(
                statement.order_by(characters.c.display_name, characters.c.id).limit(limit)
            )
            .mappings()
            .all()
        )

    def link_summary(self, character_ids):
        """Active link count and active owner per character, in **one** query.

        The Council index renders both for every row on the page. Asking per row
        would be the N+1 the engineering rules forbid in a web endpoint, and it
        would grow with the page size the caller chooses.
        """
        wanted = list(character_ids)
        if not wanted:
            return {}
        rows = self._connection.execute(
            select(
                character_access.c.character_id,
                func.count().label("active_links"),
                func.max(
                    text("CASE WHEN access_kind = 'owner' THEN platform_account_id::text END")
                ).label("owner_account_id"),
            )
            .where(
                character_access.c.character_id.in_(wanted),
                character_access.c.active.is_(True),
            )
            .group_by(character_access.c.character_id)
        ).all()
        return {
            row[0]: {
                "active_links": int(row[1]),
                "owner_account_id": UUID(row[2]) if row[2] else None,
            }
            for row in rows
        }

    # -- writes ------------------------------------------------------------
    def grant(
        self,
        *,
        character_id: UUID,
        platform_account_id: UUID,
        access_kind: str,
        granted_by_account_id: UUID,
        default_character: bool,
        reason: str,
        correlation_id: UUID,
        at: datetime,
    ) -> UUID:
        """Insert one active link. The legacy columns are the trigger's business.

        `discord_user_id` and `granted_by_discord_user_id` are **not** set here:
        migration 0008's `character_access_discord_shadow` trigger derives both
        from the accounts named above and refuses the insert if either account
        has no active Discord identity. Writing them here as well would be a
        second author for a column with one.
        """
        access_id = uuid4()
        self._connection.execute(
            insert(character_access).values(
                id=access_id,
                character_id=character_id,
                platform_account_id=platform_account_id,
                access_kind=access_kind,
                active=True,
                default_character=default_character,
                granted_by_account_id=granted_by_account_id,
                granted_at=at,
                reason=reason,
                audit_correlation_id=correlation_id,
            )
        )
        return access_id

    def revoke(self, *, access_id: UUID, at: datetime) -> bool:
        """Deactivate, keeping the row, its grant reason and its correlation id.

        The **revocation's** reason and actor are not written here, and there is
        no column for them: `character_access.reason` is the reason the link was
        granted, and overwriting it would erase why somebody was given access in
        order to record why they lost it. The revoker, the reason and the time
        go into the append-only `character_access.revoked` audit event, which is
        the record (route contract §5.1, schema §7).
        """
        result = self._connection.execute(
            update(character_access)
            .where(
                character_access.c.id == access_id,
                character_access.c.active.is_(True),
            )
            .values(active=False, revoked_at=at, default_character=False)
        )
        return (result.rowcount or 0) == 1

    def clear_default_for_account(self, account_id: UUID, *, at: datetime) -> None:
        self._connection.execute(
            update(character_access)
            .where(
                character_access.c.platform_account_id == account_id,
                character_access.c.active.is_(True),
                character_access.c.default_character.is_(True),
            )
            .values(default_character=False)
        )

    def set_default(self, *, access_id: UUID, at: datetime) -> bool:
        result = self._connection.execute(
            update(character_access)
            .where(
                character_access.c.id == access_id,
                character_access.c.active.is_(True),
            )
            .values(default_character=True)
        )
        return (result.rowcount or 0) == 1

    # -- provenance --------------------------------------------------------
    def provenance(self, character_id: UUID):
        """The Foundry mapping and the snapshot that established it, if any."""
        return (
            self._connection.execute(
                select(
                    external_actor_mappings.c.world_id,
                    external_actor_mappings.c.external_actor_id,
                    external_actor_mappings.c.created_at,
                    foundry_snapshots.c.checksum,
                    foundry_snapshots.c.exported_at,
                )
                .select_from(
                    external_actor_mappings.outerjoin(
                        foundry_snapshots,
                        foundry_snapshots.c.id
                        == external_actor_mappings.c.established_by_snapshot_id,
                    )
                )
                .where(external_actor_mappings.c.character_id == character_id)
            )
            .mappings()
            .one_or_none()
        )


class IdentityCandidateRepository:
    """R-24's bounded search over the **membership projection**.

    It searches Discord facts — the snowflake, the username, the global name —
    because that is what a Council member has to recognise when choosing whom to
    link. What it returns as the answer is the **snowflake**: the names are
    labels beside it, and OD-42's rule that a display name is evidence and never
    identity is the reason there is no method here that resolves a name to
    anything.
    """

    __slots__ = ("_connection",)

    def __init__(self, connection: Connection) -> None:
        self._connection = connection

    def search(self, *, guild_id: int, query: str, limit: int):
        pattern = f"%{query.casefold()}%"
        return list(
            self._connection.execute(
                select(
                    discord_users.c.id,
                    discord_users.c.username,
                    discord_users.c.global_name,
                    discord_guild_memberships.c.observed_at,
                    external_identities.c.platform_account_id,
                )
                .select_from(
                    discord_users.join(
                        discord_guild_memberships,
                        discord_guild_memberships.c.discord_user_id == discord_users.c.id,
                    ).outerjoin(
                        external_identities,
                        and_(
                            external_identities.c.provider_key == DISCORD_PROVIDER_KEY,
                            external_identities.c.subject
                            == func.cast(discord_users.c.id, String()),
                            external_identities.c.state == "active",
                        ),
                    )
                )
                .where(
                    discord_guild_memberships.c.guild_id == guild_id,
                    discord_guild_memberships.c.active.is_(True),
                    or_(
                        func.lower(discord_users.c.username).like(pattern),
                        func.lower(func.coalesce(discord_users.c.global_name, "")).like(
                            pattern
                        ),
                    ),
                )
                # Stable, and by the **id** rather than by the name that matched:
                # a mutable label must not decide which twenty-five candidates a
                # Council member is shown.
                .order_by(discord_users.c.id)
                .limit(limit)
            )
            .mappings()
            .all()
        )

    def linked_character_accounts(self, character_id: UUID) -> set:
        return set(
            self._connection.execute(
                select(character_access.c.platform_account_id).where(
                    character_access.c.character_id == character_id,
                    character_access.c.active.is_(True),
                )
            ).scalars()
        )


class IdentityEvidenceSourceRepository:
    """The three database facts M-2's resolver needs, and no fourth.

    C-04 reads two things from Google — `Characters C` and `Players A/B/D` — and
    three things from PostgreSQL, which are exactly these methods:

    1. **which stable character a Sheet row is**, from `sheet_row_mappings`, the
       mapping the Phase 2 importer retained for precisely this purpose. The Sheet
       row's *position* is the key, never its character name: resolving a name to
       a character here would be a second name-comparison rule deciding identity,
       which is the failure OD-42 and ADR 0006 forbid;
    2. **who is in the guild**, from the membership projection, as the population
       a Sheet's Discord *name* is matched against; and
    3. **which (character, Discord subject) pairs already hold an active link**,
       so §7.3's `already_linked` bucket is counted from the database rather than
       guessed.

    None of the three can authorize anything. They are reads, they are bounded,
    and the resolver they feed refuses to choose whenever they are ambiguous.
    """

    __slots__ = ("_connection",)

    def __init__(self, connection: Connection) -> None:
        self._connection = connection

    def character_ids_for_sheet_rows(self, *, sheet_tab: str, row_indexes):
        """`{row_index: character_id}` for the rows that have a stable mapping.

        A Sheet row with no mapping is **absent from the result**, not defaulted
        to anything. The caller refuses the whole run when that happens, because a
        source row the platform cannot name a character for is a source row no
        bucket of §7.4 can durably account for.
        """
        wanted = sorted({int(index) for index in row_indexes})
        if not wanted:
            return {}
        rows = self._connection.execute(
            select(
                sheet_row_mappings.c.row_index,
                sheet_row_mappings.c.character_id,
                characters.c.display_name,
            )
            .select_from(
                sheet_row_mappings.join(
                    characters, characters.c.id == sheet_row_mappings.c.character_id
                )
            )
            .where(
                sheet_row_mappings.c.sheet_tab == sheet_tab,
                sheet_row_mappings.c.row_index.in_(wanted),
            )
        ).all()
        return {
            int(row_index): (character_id, display_name)
            for row_index, character_id, display_name in rows
        }

    def iter_active_guild_members(self, *, guild_id: int, batch: int):
        """Every active member of the projection, streamed in keyset batches.

        Ordered by the **id**, for the reason `search()` above states: a mutable
        label must never decide which members a run considers. Paged by that same
        id rather than by `OFFSET`, so a member is neither skipped nor seen twice
        if the projection is refreshed mid-scan, and so no single statement reads
        an unbounded row set (`.agents/AGENTS.md`).

        This replaced `active_guild_members(limit=…)`, which took a
        `GUILD_POPULATION_BOUND` and made a guild larger than it a **refusal**.
        That bound was a numeric policy nobody accepted — it appears in no `N-nn`
        row of the numeric register — and inventing one to keep a read bounded is
        the wrong half of the trade. Streaming keeps the read bounded without
        deciding anything: every member is considered, whatever the guild's size,
        and `batch` changes only how many round trips it takes.

        `batch` is therefore **not** a policy and no run's outcome depends on it:
        it produces no refusal, no truncation and no ordering difference, and any
        value yields byte-identical resolutions.
        """
        if batch < 1:
            raise ValueError("a keyset batch must read at least one row")
        after: int | None = None
        while True:
            statement = (
                select(
                    discord_users.c.id,
                    discord_users.c.username,
                    discord_users.c.global_name,
                )
                .select_from(
                    discord_users.join(
                        discord_guild_memberships,
                        discord_guild_memberships.c.discord_user_id
                        == discord_users.c.id,
                    )
                )
                .where(
                    discord_guild_memberships.c.guild_id == guild_id,
                    discord_guild_memberships.c.active.is_(True),
                )
                .order_by(discord_users.c.id)
                .limit(batch)
            )
            if after is not None:
                statement = statement.where(discord_users.c.id > after)
            rows = self._connection.execute(statement).mappings().all()
            if not rows:
                return
            yield from rows
            if len(rows) < batch:
                return
            after = rows[-1]["id"]

    def active_links(self, character_ids):
        """`{(character_id, discord subject)}` for every active link on these characters.

        The subject is resolved through `external_identities`, not through
        `character_access.discord_user_id`: the account key is the
        authorization-bearing one from stage B onward, and the shadow column is on
        its way out (migration contract §3, stage D). A link whose account has no
        active Discord identity contributes no pair, which is correct — the Sheet's
        evidence is a Discord name, so a pair it could never match is not one this
        set exists to hold.
        """
        wanted = list(character_ids)
        if not wanted:
            return set()
        rows = self._connection.execute(
            select(
                character_access.c.character_id,
                external_identities.c.subject,
            )
            .select_from(
                character_access.join(
                    external_identities,
                    and_(
                        external_identities.c.platform_account_id
                        == character_access.c.platform_account_id,
                        external_identities.c.provider_key == DISCORD_PROVIDER_KEY,
                        external_identities.c.state == "active",
                    ),
                )
            )
            .where(
                character_access.c.character_id.in_(wanted),
                character_access.c.active.is_(True),
            )
        ).all()
        return {(character_id, subject) for character_id, subject in rows}


class IdentityProposalRepository:
    """The M-2 evidence pipeline's durable state (migration contract §7).

    Two lifecycle positions (§7.2): C-04 writes the run, its proposals and its
    candidates; R-29/R-30 write one decision at a time, and a confirmation names
    the `character_access` row it created in the same statement.

    Nothing here can authorize anything. `granted_access_id` is the only column
    that touches authorization, it is written only by `decide()`, and
    `ck_identity_link_proposals_a_confirmation_is_a_link` permits it to be
    non-null exactly on a `confirmed` row — so "C-04 writes no `character_access`
    row" and "a rejection creates no link" are properties of the schema rather
    than of this class being careful. The row itself is written by
    `CharacterAccessService`, which this class has no reference to.
    """

    __slots__ = ("_connection",)

    def __init__(self, connection: Connection) -> None:
        self._connection = connection

    def create_run(
        self,
        *,
        source_label: str,
        profile_version: str,
        source_characters: int,
        source_players: int,
        already_linked: int,
        proposed: int,
        ambiguous: int,
        unresolved: int,
        correlation_id: UUID,
        at: datetime,
    ) -> UUID:
        """Insert the C-04 evidence run, with §7.4's first balance checked by SQL.

        An unbalanced report does not reach a reader: the check constraint
        refuses the row, the transaction aborts, and the tool reports a refusal.
        That is the plan's *"no identity discrepancy is silently accepted"*
        expressed as something that cannot be overridden by a caller who decides
        the difference is small.

        `dry_run` is written `true` and is not a parameter. Every run is a C-04
        evidence run; Council decisions consume its proposals directly, and
        `ck_identity_migration_runs_run_is_a_c04_evidence_run` is what makes that
        a property of the table rather than of this method.
        """
        run_id = uuid4()
        self._connection.execute(
            insert(identity_migration_runs).values(
                id=run_id,
                produced_at=at,
                dry_run=True,
                source_label=source_label,
                profile_version=profile_version,
                source_characters=source_characters,
                source_players=source_players,
                already_linked=already_linked,
                proposed=proposed,
                ambiguous=ambiguous,
                unresolved=unresolved,
                correlation_id=correlation_id,
            )
        )
        return run_id

    def add_proposal(
        self,
        *,
        run_id: UUID,
        character_id: UUID,
        sheet_player_name: str,
        sheet_discord_name: str | None,
        active_dm: bool,
        proposed_subject: str | None,
        resolution: str,
        candidates,
        correlation_id: UUID,
    ) -> UUID:
        proposal_id = uuid4()
        self._connection.execute(
            insert(identity_link_proposals).values(
                id=proposal_id,
                run_id=run_id,
                character_id=character_id,
                sheet_player_name=sheet_player_name,
                sheet_discord_name=sheet_discord_name,
                active_dm=active_dm,
                proposed_subject=proposed_subject,
                resolution=resolution,
                audit_correlation_id=correlation_id,
            )
        )
        for subject, username in candidates:
            self._connection.execute(
                insert(identity_link_proposal_candidates).values(
                    id=uuid4(),
                    proposal_id=proposal_id,
                    subject=subject,
                    observed_username=username,
                )
            )
        return proposal_id

    def latest_run(self):
        return (
            self._connection.execute(
                select(identity_migration_runs).order_by(
                    identity_migration_runs.c.produced_at.desc(),
                    identity_migration_runs.c.id.desc(),
                )
            )
            .mappings()
            .first()
        )

    def run(self, run_id: UUID):
        return (
            self._connection.execute(
                select(identity_migration_runs).where(
                    identity_migration_runs.c.id == run_id
                )
            )
            .mappings()
            .one_or_none()
        )

    def is_latest_run(self, run_id: UUID) -> bool:
        latest_id = (
            select(identity_migration_runs.c.id)
            .order_by(
                identity_migration_runs.c.produced_at.desc(),
                identity_migration_runs.c.id.desc(),
            )
            .limit(1)
            .scalar_subquery()
        )
        return bool(
            self._connection.execute(select(run_id == latest_id)).scalar_one()
        )

    def proposals(self, *, run_id: UUID, after: str | None, limit: int):
        statement = select(identity_link_proposals).where(
            identity_link_proposals.c.run_id == run_id
        )
        if after is not None:
            statement = statement.where(identity_link_proposals.c.id > after)
        return list(
            self._connection.execute(
                statement.order_by(identity_link_proposals.c.id).limit(limit)
            )
            .mappings()
            .all()
        )

    def proposal(self, proposal_id: UUID):
        return (
            self._connection.execute(
                select(identity_link_proposals).where(
                    identity_link_proposals.c.id == proposal_id
                )
            )
            .mappings()
            .one_or_none()
        )

    def candidates_for(self, proposal_ids, *, limit: int):
        """`{proposal_id: (at most `limit` subjects, how many rows exist)}`.

        Two facts, because the view needs both and they are not the same fact.
        The candidate set is **not** bounded on the way in — §7.6 requires every
        matching member of an ambiguity to persist, and `resolve()` returns every
        one — so a read that selected all children of a hundred proposals would be
        the unbounded query `.agents/AGENTS.md` forbids. The bound is applied in
        SQL by `row_number()`, and the count is a separate aggregate over the same
        rows, so what the view reports as the total is the number of rows that
        exist rather than the number this query chose to return.
        """
        wanted = list(proposal_ids)
        if not wanted:
            return {}

        ranked = (
            select(
                identity_link_proposal_candidates.c.proposal_id,
                identity_link_proposal_candidates.c.subject,
                func.row_number()
                .over(
                    partition_by=identity_link_proposal_candidates.c.proposal_id,
                    order_by=identity_link_proposal_candidates.c.subject,
                )
                .label("rank"),
            )
            .where(identity_link_proposal_candidates.c.proposal_id.in_(wanted))
            .subquery()
        )
        # `limit + 1` so the caller can tell "exactly `limit`" from "more than
        # `limit`" without trusting the count query to have run against the same
        # snapshot. Inside one transaction it has, and the redundancy costs a row.
        listed = self._connection.execute(
            select(ranked.c.proposal_id, ranked.c.subject)
            .where(ranked.c.rank <= limit + 1)
            .order_by(ranked.c.proposal_id, ranked.c.subject)
        ).all()
        totals = dict(
            self._connection.execute(
                select(
                    identity_link_proposal_candidates.c.proposal_id, func.count()
                )
                .where(identity_link_proposal_candidates.c.proposal_id.in_(wanted))
                .group_by(identity_link_proposal_candidates.c.proposal_id)
            ).all()
        )

        grouped: dict[UUID, list[str]] = {}
        for proposal_id, subject in listed:
            grouped.setdefault(proposal_id, []).append(subject)
        return {
            proposal_id: (tuple(subjects), int(totals.get(proposal_id, len(subjects))))
            for proposal_id, subjects in grouped.items()
        }

    def candidate_subjects(self, proposal_id: UUID) -> tuple[str, ...]:
        """Every candidate of one proposal, for the durability evidence.

        Bounded by the proposal rather than by a page size: this answers *"what
        did the run actually record?"*, which is the question §7.6 makes a Council
        member entitled to ask and the question a rendering bound must not be able
        to change the answer to.
        """
        return tuple(
            self._connection.execute(
                select(identity_link_proposal_candidates.c.subject)
                .where(identity_link_proposal_candidates.c.proposal_id == proposal_id)
                .order_by(identity_link_proposal_candidates.c.subject)
            ).scalars()
        )

    def decision_counts(self, run_id: UUID) -> dict[str, int]:
        """How many of this run's proposals sit in each `resolution`.

        The **historical** decision, which is the only thing this column records.
        `confirmed` here counts confirmations that happened, not links that are
        still active; `confirmed_link_counts()` below is the question about the
        access rows, and the two are deliberately separate queries because they
        are separate facts.
        """
        rows = self._connection.execute(
            select(identity_link_proposals.c.resolution, func.count())
            .where(identity_link_proposals.c.run_id == run_id)
            .group_by(identity_link_proposals.c.resolution)
        ).all()
        return {row[0]: int(row[1]) for row in rows}

    def confirmed_link_counts(self, run_id: UUID) -> dict[str, int]:
        """`{"active": n, "revoked": m}` over this run's confirmed proposals.

        §7.4's `confirmed` counts proposals that are **active links**, and after
        an R-26 revocation a confirmation is no longer one. The join is from
        `granted_access_id` to the **exact** `character_access` row that
        confirmation created — never to another active link on the same
        character or the same account, which would let somebody else's grant
        make a revoked one read as active.

        Total by construction: `ck_identity_link_proposals_a_confirmation_is_a_link`
        makes `granted_access_id` non-null exactly on a `confirmed` row, and the
        foreign key is `RESTRICT`, so every confirmed proposal has exactly one
        access row and it cannot be deleted out from under the decision. The
        inner join therefore loses nothing and
        `active + revoked == decision_counts()["confirmed"]`, which is what keeps
        §7.4's second balance closed rather than merely plausible.

        One grouped query for the whole run, not one per row.
        """
        rows = self._connection.execute(
            select(character_access.c.active, func.count())
            .select_from(
                identity_link_proposals.join(
                    character_access,
                    character_access.c.id
                    == identity_link_proposals.c.granted_access_id,
                )
            )
            .where(
                identity_link_proposals.c.run_id == run_id,
                identity_link_proposals.c.resolution == "confirmed",
            )
            .group_by(character_access.c.active)
        ).all()
        counts = {"active": 0, "revoked": 0}
        for active, count in rows:
            counts["active" if active else "revoked"] += int(count)
        return counts

    def granted_link_state(self, proposal_ids) -> dict[UUID, bool]:
        """`{proposal_id: is its own granted access row active now}`.

        One bounded query for the rendered page — the proposals are already
        limited to a page size, and this reads at most one row for each — rather
        than a lookup per proposal, which is the N+1 the engineering rules forbid
        in a web endpoint.

        Absent from the result for every proposal that created no link:
        `granted_access_id` is null on everything but a `confirmed` row, so a
        missing key means "this confirmation does not exist", never "its link is
        gone". The caller distinguishes the two rather than defaulting.
        """
        wanted = list(proposal_ids)
        if not wanted:
            return {}
        rows = self._connection.execute(
            select(identity_link_proposals.c.id, character_access.c.active)
            .select_from(
                identity_link_proposals.join(
                    character_access,
                    character_access.c.id
                    == identity_link_proposals.c.granted_access_id,
                )
            )
            .where(identity_link_proposals.c.id.in_(wanted))
        ).all()
        return {row[0]: bool(row[1]) for row in rows}

    def decide(
        self,
        *,
        proposal_id: UUID,
        resolution: str,
        account_id: UUID,
        reason: str,
        at: datetime,
        granted_access_id: UUID | None,
    ) -> bool:
        """Move one proposal to `confirmed` or `rejected`, once.

        Conditional on it still being outstanding and belonging to the latest
        evidence run, so a double submission decides nothing twice and stale
        evidence cannot authorize after a newer C-04 run. The caller is told the
        state moved. Idempotency here is the `WHERE`, not a check the caller
        performs first and then hopes still holds. That same `WHERE` is
        what makes two concurrent R-29/R-30 decisions resolve to one: both read
        an outstanding row, both attempt the update, and exactly one of them
        matches.

        `granted_access_id` is the `character_access` row the confirmation
        created, and it is written in **this** statement rather than in a later
        one because `ck_identity_link_proposals_a_confirmation_is_a_link`
        requires a confirmed row to name its access row and a rejected row not
        to. A separate update would have to pass through a state the constraint
        forbids, so there is no way to write half of a confirmation. R-30 passes
        `None` and cannot pass anything else — it has no access id to pass.
        """
        latest_run_id = (
            select(identity_migration_runs.c.id)
            .order_by(
                identity_migration_runs.c.produced_at.desc(),
                identity_migration_runs.c.id.desc(),
            )
            .limit(1)
            .scalar_subquery()
        )
        result = self._connection.execute(
            update(identity_link_proposals)
            .where(
                identity_link_proposals.c.id == proposal_id,
                identity_link_proposals.c.run_id == latest_run_id,
                identity_link_proposals.c.resolution.in_(
                    ("proposed", "ambiguous", "unresolved")
                ),
            )
            .values(
                resolution=resolution,
                decided_at=at,
                decided_by_account_id=account_id,
                decision_reason=reason,
                granted_access_id=granted_access_id,
            )
        )
        return (result.rowcount or 0) == 1

    def purge_runs_older_than(self, *, before: datetime) -> int:
        """The 90-day retention of schema §11, applied to the run.

        One statement: the foreign keys cascade run to proposal to candidate, so
        a partially purged run is not a state this can produce.
        """
        result = self._connection.execute(
            delete(identity_migration_runs).where(
                identity_migration_runs.c.produced_at < before
            )
        )
        return result.rowcount or 0


# ---------------------------------------------------------------------------
# P3.3 — snapshots, folder selection, durable jobs and audit search
# ---------------------------------------------------------------------------


class SnapshotReadRepository:
    """`foundry_snapshots`, its folder selection, and what has been applied.

    Read-mostly. The one thing it writes is the folder selection, and that write
    is an upsert rather than a delete-and-insert so the row's identity — and the
    foreign key an audit trail could one day hang off — survives a change of
    mind.

    **Nothing here touches `foundry_snapshots`.** That table is append-only, and
    the reason the selection lives in its own table at all is that it has to be
    changeable (migration 0011's docstring).
    """

    __slots__ = ("_connection", "_profile_version")

    def __init__(self, connection: Connection, *, profile_version: str) -> None:
        self._connection = connection
        self._profile_version = profile_version

    def profile_version(self) -> str:
        """The versioned field profile the platform is running.

        Read from the profile object the composition injected, never from
        configuration: there is no write route for it, and a profile an operator
        could point at something else would be a profile nobody reviewed.
        """
        return self._profile_version

    def snapshot(self, snapshot_id: UUID):
        return (
            self._connection.execute(
                select(foundry_snapshots).where(foundry_snapshots.c.id == snapshot_id)
            )
            .mappings()
            .one_or_none()
        )

    def snapshot_by_checksum(self, checksum: str):
        return (
            self._connection.execute(
                select(foundry_snapshots).where(
                    foundry_snapshots.c.checksum == checksum
                )
            )
            .mappings()
            .one_or_none()
        )

    def unapplied_page(self, *, position, size: int):
        """R-40's page: snapshots with no applied import, newest first.

        `NOT EXISTS` rather than a left join with a null test, because the
        question is existential and the planner can stop at the first matching
        import row. Over-reads by one so `Page.of` can observe `has_more`
        instead of asking `COUNT(*)` for it.

        The cursor is `(received_at, id)` descending — total, because the
        trailing primary key breaks every tie.
        """
        applied = (
            select(snapshot_imports.c.id)
            .where(
                snapshot_imports.c.snapshot_id == foundry_snapshots.c.id,
                snapshot_imports.c.status == "applied",
            )
            .exists()
        )
        statement = select(foundry_snapshots).where(~applied)
        if position is not None:
            received_at, identifier = position
            statement = statement.where(
                or_(
                    foundry_snapshots.c.received_at < datetime.fromisoformat(received_at),
                    and_(
                        foundry_snapshots.c.received_at
                        == datetime.fromisoformat(received_at),
                        foundry_snapshots.c.id < UUID(identifier),
                    ),
                )
            )
        return list(
            self._connection.execute(
                statement.order_by(
                    foundry_snapshots.c.received_at.desc(),
                    foundry_snapshots.c.id.desc(),
                ).limit(size + 1)
            )
            .mappings()
            .all()
        )

    def applied_snapshot_ids(self, snapshot_ids) -> set:
        wanted = [identifier for identifier in snapshot_ids if identifier is not None]
        if not wanted:
            return set()
        rows = self._connection.execute(
            select(snapshot_imports.c.snapshot_id).where(
                snapshot_imports.c.snapshot_id.in_(wanted),
                snapshot_imports.c.status == "applied",
            )
        ).all()
        return {row[0] for row in rows}

    def import_record(self, import_id: UUID):
        """R-47's receipt: one row of the append-only `snapshot_imports` table.

        There is no update and no delete anywhere in this class for this table,
        and there is no route that offers one. A correction is a compensating
        import, which is the plan's rule for the whole platform.
        """
        return (
            self._connection.execute(
                select(snapshot_imports).where(snapshot_imports.c.id == import_id)
            )
            .mappings()
            .one_or_none()
        )

    def import_by_request_key(self, request_key: str):
        return (
            self._connection.execute(
                select(snapshot_imports).where(
                    snapshot_imports.c.request_key == request_key
                )
            )
            .mappings()
            .one_or_none()
        )

    def folder_selection(self, snapshot_id: UUID):
        return (
            self._connection.execute(
                select(snapshot_folder_selections).where(
                    snapshot_folder_selections.c.snapshot_id == snapshot_id
                )
            )
            .mappings()
            .one_or_none()
        )

    def folder_selections(self, snapshot_ids) -> dict:
        """A bounded set of selections in one query, keyed by snapshot.

        One statement rather than one per row: an N+1 in a web endpoint is
        forbidden, and this one would grow with the page size the caller chooses.
        """
        wanted = [identifier for identifier in snapshot_ids if identifier is not None]
        if not wanted:
            return {}
        rows = (
            self._connection.execute(
                select(snapshot_folder_selections).where(
                    snapshot_folder_selections.c.snapshot_id.in_(wanted)
                )
            )
            .mappings()
            .all()
        )
        return {row["snapshot_id"]: row for row in rows}

    def observed_folder_paths(self, snapshot_ids) -> dict:
        """`{snapshot_id: {folder_id: folder_path}}`, from completed previews.

        The **only** place a folder's displayed path can come from without
        parsing the artifact: a completed preview stored the path it reconciled
        against, in its bounded summary. A snapshot nothing has previewed yet has
        no entry here, and `FolderChoice.path_observed` says so rather than a
        path being invented (view-model contract, `FolderChoice`).
        """
        wanted = [identifier for identifier in snapshot_ids if identifier is not None]
        if not wanted:
            return {}
        rows = self._connection.execute(
            select(
                reconciliation_jobs.c.snapshot_id,
                reconciliation_jobs.c.folder_id,
                reconciliation_job_results.c.summary,
            )
            .select_from(
                reconciliation_jobs.join(
                    reconciliation_job_results,
                    reconciliation_jobs.c.result_id == reconciliation_job_results.c.id,
                )
            )
            .where(
                reconciliation_jobs.c.snapshot_id.in_(wanted),
                reconciliation_jobs.c.state == "completed",
            )
            .order_by(reconciliation_jobs.c.queued_at.asc())
        ).all()
        observed: dict = {}
        for snapshot_id, folder_id, summary in rows:
            path = (summary or {}).get("folder_path")
            if path:
                # Later rows win: the newest completed preview of a folder is the
                # most recent observation of its path, and a folder that was
                # renamed in Foundry should read as its current name.
                observed.setdefault(snapshot_id, {})[folder_id] = path
        return observed

    def set_folder_selection(
        self,
        *,
        snapshot_id: UUID,
        folder_id: str,
        folder_path: str,
        account_id: UUID,
        correlation_id: UUID,
        now: datetime,
    ) -> UUID:
        """Upsert, in one statement, on the snapshot's unique constraint.

        One statement rather than read-then-write: two administrators selecting
        different folders at the same moment must produce one selection, not a
        lost update or a uniqueness violation the caller has to interpret. The
        `version` increment is what makes which one won observable.
        """
        statement = (
            pg_insert(snapshot_folder_selections)
            .values(
                id=uuid4(),
                snapshot_id=snapshot_id,
                folder_id=folder_id,
                folder_path=folder_path,
                selected_by_account_id=account_id,
                selected_at=now,
                correlation_id=correlation_id,
                version=1,
            )
            .on_conflict_do_update(
                constraint="uq_snapshot_folder_selections_snapshot",
                set_={
                    "folder_id": folder_id,
                    "folder_path": folder_path,
                    "selected_by_account_id": account_id,
                    "selected_at": now,
                    "correlation_id": correlation_id,
                    "version": snapshot_folder_selections.c.version + 1,
                },
            )
            .returning(snapshot_folder_selections.c.id)
        )
        return self._connection.execute(statement).scalar_one()


class ReconciliationJobRepository:
    """The queue, as statements. SM-05 lives here and nowhere else.

    Every write below carries the predicate that makes it safe against a
    concurrent one, and the predicates are the design:

    - the **claim** matches `state = 'queued' AND cancel_requested_at IS NULL AND
      attempts < 3` under `FOR UPDATE SKIP LOCKED`, so two workers cannot claim
      one attempt;
    - every worker write carries `AND lease_owner = :owner`, so a worker that has
      lost its lease matches zero rows and exits quietly rather than stamping a
      verdict on a job somebody else now owns;
    - the **reaper** is one statement with two branches, so an expired lease is
      requeued or exhausted with no gap between deciding and doing — and it takes
      only expiries with `effect_committed_at IS NULL`, because an expired lease
      over a committed effect is a **publication** rather than an expiry;
    - **`lock_unpublished_effect`** takes those, under `FOR UPDATE SKIP LOCKED`,
      and **`complete_recovered_effect`** publishes them in the same transaction;
    - **both** branches of the **cancel** filter `effect_committed_at IS NULL`, so
      an apply whose effect has committed — including one committing *right now*,
      because the predicate blocks on the commit fence's row lock — matches zero
      rows;
    - the **self-abandon** carries the same `effect_committed_at IS NULL`, so a
      worker cannot requeue or fail a job whose import already committed;
    - so do **`fail`**, **`mark_stale_under_lease`** and **`cancel_under_lease`**,
      the three statements that write a terminal verdict under a live lease;
    - and so do **`mark_stale`** and **`invalidate_for_snapshot`**, so R-41's
      folder change and R-46's N-46 expiry cannot rewrite an apply whose effect
      is durable into a state that means "nothing was applied".

    None of them is a rule the caller has to remember. A caller that forgot one
    would be issuing a different statement, which is visible in the diff — and
    migration 0013's `committed_effect_is_never_denied` refuses the row anyway, so
    a forgotten predicate is a loud abort rather than a quiet lie.
    """

    __slots__ = ("_connection", "_lease_seconds", "_max_attempts")

    def __init__(
        self, connection: Connection, *, lease_seconds: int, max_attempts: int
    ) -> None:
        self._connection = connection
        # Both from the validated `WorkerSettings` graph — N-23's exact 60 and
        # N-43's 3 — rather than literals here. A repository holding its own copy
        # of an accepted number is a second place for it to be wrong.
        self._lease_seconds = lease_seconds
        self._max_attempts = max_attempts

    # -- reads -------------------------------------------------------------
    def job(self, job_id: UUID):
        return (
            self._connection.execute(
                select(reconciliation_jobs).where(reconciliation_jobs.c.id == job_id)
            )
            .mappings()
            .one_or_none()
        )

    def by_request_key(self, key: str):
        return (
            self._connection.execute(
                select(reconciliation_jobs).where(
                    reconciliation_jobs.c.request_key == key
                )
            )
            .mappings()
            .one_or_none()
        )

    def result(self, result_id: UUID):
        if result_id is None:
            return None
        return (
            self._connection.execute(
                select(reconciliation_job_results).where(
                    reconciliation_job_results.c.id == result_id
                )
            )
            .mappings()
            .one_or_none()
        )

    def result_for_job(self, job_id: UUID):
        """The result a job produced, found from the **result** side.

        `reconciliation_jobs.result_id` is not the only link: the result row
        names its job, and `CHECK ((state = 'completed') = (result_id IS NOT
        NULL))` means the job's own pointer exists exactly while the job is
        `completed`.

        A preview that goes `stale` therefore stops naming its result, because
        the constraint requires it to — and the result itself is untouched.
        Reading from this side is what lets a Council member still see the
        bounded summary of the preview that just became unconfirmable, which is
        the difference between "this is stale, and here is what it said" and a
        blank screen with a code on it.
        """
        return (
            self._connection.execute(
                select(reconciliation_job_results)
                .where(reconciliation_job_results.c.job_id == job_id)
                .order_by(reconciliation_job_results.c.produced_at.desc())
                .limit(1)
            )
            .mappings()
            .one_or_none()
        )

    def queued_count(self) -> int:
        """N-42's admission bound: how many jobs are `queued` platform-wide.

        Counted over the partial index's predicate, so the count is a scan of the
        at-most-five rows the bound permits rather than of the table.
        """
        return int(
            self._connection.execute(
                select(func.count())
                .select_from(reconciliation_jobs)
                .where(reconciliation_jobs.c.state == "queued")
            ).scalar_one()
        )

    def live_apply_exists(
        self, *, snapshot_id: UUID, folder_id: str, profile_version: str
    ) -> bool:
        return (
            self._connection.execute(
                select(reconciliation_jobs.c.id).where(
                    reconciliation_jobs.c.kind == "apply",
                    reconciliation_jobs.c.state.in_(("queued", "running")),
                    reconciliation_jobs.c.snapshot_id == snapshot_id,
                    reconciliation_jobs.c.folder_id == folder_id,
                    reconciliation_jobs.c.profile_version == profile_version,
                )
            ).first()
            is not None
        )

    def latest_stamps(self, snapshot_ids) -> dict:
        """The newest job per snapshot, in one statement (`DISTINCT ON`).

        PostgreSQL-specific and deliberately so: the alternative is a window
        function or a correlated subquery per row, and the second is the N+1 this
        method exists to avoid.
        """
        wanted = [identifier for identifier in snapshot_ids if identifier is not None]
        if not wanted:
            return {}
        rows = (
            self._connection.execute(
                select(
                    reconciliation_jobs.c.id,
                    reconciliation_jobs.c.snapshot_id,
                    reconciliation_jobs.c.kind,
                    reconciliation_jobs.c.state,
                    func.coalesce(
                        reconciliation_jobs.c.finished_at,
                        reconciliation_jobs.c.heartbeat_at,
                        reconciliation_jobs.c.queued_at,
                    ).label("updated_at"),
                )
                .distinct(reconciliation_jobs.c.snapshot_id)
                .where(reconciliation_jobs.c.snapshot_id.in_(wanted))
                .order_by(
                    reconciliation_jobs.c.snapshot_id,
                    reconciliation_jobs.c.queued_at.desc(),
                    reconciliation_jobs.c.id.desc(),
                )
            )
            .mappings()
            .all()
        )
        return {row["snapshot_id"]: row for row in rows}

    def expired_lease_age_seconds(self) -> float | None:
        """The reaper's liveness signal (VM-16, operational contract §5).

        `max(now() - lease_expires_at)` over running jobs whose lease has
        expired. It should never exceed `N-23 + N-44`; a value that does means
        the reaper is not running, which is the one way a job can sit
        unterminated under the corrected N-43.
        """
        value = self._connection.execute(
            text(
                "SELECT EXTRACT(EPOCH FROM max(now() - lease_expires_at)) "
                "FROM reconciliation_jobs "
                "WHERE state = 'running' AND lease_expires_at < now()"
            )
        ).scalar_one_or_none()
        return None if value is None else float(value)

    # -- enqueue -----------------------------------------------------------
    def insert(
        self,
        *,
        kind,
        snapshot_id: UUID,
        folder_id: str,
        profile_version: str,
        fingerprint: bytes,
        requested_by_account_id: UUID,
        requested_capability: ActorCapability,
        request_key: str,
        parent_job_id: UUID | None,
        correlation_id: UUID,
        now: datetime,
    ) -> UUID:
        return self._connection.execute(
            insert(reconciliation_jobs)
            .values(
                id=uuid4(),
                kind=kind.value,
                state="queued",
                snapshot_id=snapshot_id,
                folder_id=folder_id,
                profile_version=profile_version,
                scope_fingerprint=fingerprint,
                requested_by_account_id=requested_by_account_id,
                requested_capability=requested_capability.value,
                request_key=request_key,
                parent_job_id=parent_job_id,
                attempts=0,
                queued_at=now,
                correlation_id=correlation_id,
                version=1,
            )
            .returning(reconciliation_jobs.c.id)
        ).scalar_one()

    # -- claim, heartbeat, complete ---------------------------------------
    def claim(self, *, owner: str, now: datetime):
        """Schema §10.1's claim statement, verbatim in shape.

        `FOR UPDATE SKIP LOCKED` is what makes two workers unable to claim one
        attempt. The platform runs one worker (N-41); the statement is correct
        for more, which is the point of using the database as the queue.

        `attempts < :max` in the predicate is deliberately redundant with
        `CHECK (state <> 'queued' OR attempts < 3)`. The constraint makes an
        exhausted queued job impossible; the predicate makes the claim **refuse**
        rather than **violate** if the constraint is ever dropped or a future
        revision widens N-43 — a claim that fails a check constraint aborts the
        worker's transaction, and a claim that matches no row simply moves on.
        """
        return (
            self._connection.execute(
                text(
                    """
                    UPDATE reconciliation_jobs SET
                        state = 'running',
                        lease_owner = :owner,
                        attempts = attempts + 1,
                        started_at = COALESCE(started_at, :now),
                        lease_expires_at = :now + make_interval(secs => :lease),
                        heartbeat_at = :now,
                        version = version + 1
                    WHERE id = (
                        SELECT id FROM reconciliation_jobs
                        WHERE state = 'queued'
                          AND cancel_requested_at IS NULL
                          AND attempts < :max_attempts
                        ORDER BY queued_at
                        FOR UPDATE SKIP LOCKED
                        LIMIT 1
                    )
                    RETURNING *
                    """
                ),
                {
                    "owner": owner,
                    "now": now,
                    "lease": self._lease_seconds,
                    "max_attempts": self._max_attempts,
                },
            )
            .mappings()
            .one_or_none()
        )

    def heartbeat(self, *, job_id: UUID, owner: str, now: datetime):
        """Extend the lease, and report whether cancellation was requested.

        Returns `None` when this worker no longer owns the job — the reaper acted
        while it was working — which is the signal to abandon rather than to keep
        going and publish a result nobody is waiting for.
        """
        return (
            self._connection.execute(
                text(
                    """
                    UPDATE reconciliation_jobs SET
                        heartbeat_at = :now,
                        lease_expires_at = :now + make_interval(secs => :lease),
                        version = version + 1
                    WHERE id = :job_id AND lease_owner = :owner AND state = 'running'
                    RETURNING id, cancel_requested_at, attempts
                    """
                ),
                {
                    "job_id": job_id,
                    "owner": owner,
                    "now": now,
                    "lease": self._lease_seconds,
                },
            )
            .mappings()
            .one_or_none()
        )

    def store_result(
        self,
        *,
        job_id: UUID,
        summary: dict,
        blocked_entries: list,
        now: datetime,
        expires_at: datetime,
    ) -> UUID:
        return self._connection.execute(
            insert(reconciliation_job_results)
            .values(
                id=uuid4(),
                job_id=job_id,
                summary=summary,
                blocked_entries=blocked_entries,
                produced_at=now,
                expires_at=expires_at,
            )
            .returning(reconciliation_job_results.c.id)
        ).scalar_one()

    def complete(
        self,
        *,
        job_id: UUID,
        owner: str,
        result_id: UUID,
        fingerprint: bytes | None,
        now: datetime,
    ) -> bool:
        """`running -> completed`, under the lease, with the result already committed.

        The result row is inserted first and named here, in the **same
        transaction**, which is what `CHECK ((state = 'completed') = (result_id IS
        NOT NULL))` turns from an ordering convention into a fact.

        `fingerprint` is the preview's completed scope — the aggregate versions
        the run actually read, folded in. It is written here rather than at
        enqueue because it is not knowable until the artifact has been parsed,
        and it is written in this statement rather than a second one so a
        `completed` preview can never carry the `unobserved` scope.
        """
        values = {
            "job_id": job_id,
            "owner": owner,
            "result_id": result_id,
            "now": now,
        }
        fingerprint_clause = ""
        if fingerprint is not None:
            fingerprint_clause = "scope_fingerprint = :fingerprint,"
            values["fingerprint"] = fingerprint
        return (
            self._connection.execute(
                text(
                    f"""
                    UPDATE reconciliation_jobs SET
                        state = 'completed',
                        {fingerprint_clause}
                        result_id = :result_id,
                        finished_at = :now,
                        lease_owner = NULL,
                        lease_expires_at = NULL,
                        heartbeat_at = NULL,
                        version = version + 1
                    WHERE id = :job_id AND lease_owner = :owner AND state = 'running'
                    """
                ),
                values,
            ).rowcount
            == 1
        )

    def fail(
        self, *, job_id: UUID, owner: str, code, now: datetime
    ) -> bool:
        """`running -> failed`, under the lease, with a closed-vocabulary code.

        Used for a **deterministic** refusal — one that would recur on every
        attempt — which is failed immediately whatever `attempts` says. An
        exhausted-attempts failure is not written here: that one belongs to the
        reaper, which is the hand that observes the expiry.

        `AND effect_committed_at IS NULL` (2026-08-18 effect-publication
        remediation) because `failed` asserts that nothing was applied. Migration
        0013's `committed_effect_is_never_denied` makes the row impossible either
        way; the predicate is what makes this statement **refuse** rather than
        **violate**, which is the difference between a worker exiting quietly and
        a worker whose transaction aborts.
        """
        return (
            self._connection.execute(
                text(
                    """
                    UPDATE reconciliation_jobs SET
                        state = 'failed',
                        failure_code = :code,
                        finished_at = :now,
                        lease_owner = NULL,
                        lease_expires_at = NULL,
                        heartbeat_at = NULL,
                        version = version + 1
                    WHERE id = :job_id AND lease_owner = :owner AND state = 'running'
                      AND effect_committed_at IS NULL
                    """
                ),
                {"job_id": job_id, "owner": owner, "code": code.value, "now": now},
            ).rowcount
            == 1
        )

    def mark_stale_under_lease(
        self, *, job_id: UUID, owner: str, reason, now: datetime
    ) -> bool:
        """`running -> stale`, under the lease, when the scope moved.

        `AND effect_committed_at IS NULL` for the same reason `fail` carries it
        (2026-08-18 effect-publication remediation): `stale` asserts that nothing
        was applied, and an apply whose import is durable applied something. The
        constraint forbids the row; the predicate makes the statement refuse
        rather than abort the transaction that issued it.
        """
        return (
            self._connection.execute(
                text(
                    """
                    UPDATE reconciliation_jobs SET
                        state = 'stale',
                        stale_reason = :reason,
                        finished_at = :now,
                        lease_owner = NULL,
                        lease_expires_at = NULL,
                        heartbeat_at = NULL,
                        version = version + 1
                    WHERE id = :job_id AND lease_owner = :owner AND state = 'running'
                      AND effect_committed_at IS NULL
                    """
                ),
                {"job_id": job_id, "owner": owner, "reason": reason.value, "now": now},
            ).rowcount
            == 1
        )

    def cancel_under_lease(self, *, job_id: UUID, owner: str, now: datetime) -> bool:
        """A `running` job observing its cancellation at the next heartbeat.

        `AND effect_committed_at IS NULL` completes the set (2026-08-18
        effect-publication remediation). Observing a recorded cancellation is
        already proof that no effect committed — `request_cancel` cannot record
        one over a committed effect — so this predicate is the belt to that
        braces: the statement that *writes* `cancelled` carries the same refusal
        as the statement that requests it, and neither depends on the other having
        been correct.
        """
        return (
            self._connection.execute(
                text(
                    """
                    UPDATE reconciliation_jobs SET
                        state = 'cancelled',
                        finished_at = :now,
                        lease_owner = NULL,
                        lease_expires_at = NULL,
                        heartbeat_at = NULL,
                        version = version + 1
                    WHERE id = :job_id AND lease_owner = :owner AND state = 'running'
                      AND effect_committed_at IS NULL
                    """
                ),
                {"job_id": job_id, "owner": owner, "now": now},
            ).rowcount
            == 1
        )

    def abandon(self, *, job_id: UUID, owner: str, now: datetime):
        """Worker self-abandon at N-45's hard cap or on the kill switch.

        The **same** two-branch logic the reaper uses, under this worker's own
        lease. `AND lease_owner = :owner` is the whole safety argument: if the
        reaper has already acted — because this worker was slow enough to lose
        its lease — the statement matches zero rows and the worker exits quietly
        rather than stamping a stale verdict on a job somebody else now owns.

        `AND effect_committed_at IS NULL` is the second half of that argument,
        added by the 2026-08-18 remediation. Abandoning a job whose import
        already committed would requeue or fail a job the database has already
        changed — a `queued` or `failed` job over a real import. The predicate
        also blocks on the fence's row lock while the effect is committing, so
        the abandon and the commit cannot both win.

        Returns an `Abandonment`, which distinguishes "the reaper got there
        first" from "the effect committed" — two outcomes that were both `None`
        before and need opposite responses from the worker.
        """
        from application.web.jobs import Abandonment

        row = (
            self._connection.execute(
                text(
                    """
                    UPDATE reconciliation_jobs SET
                        state = CASE WHEN attempts < :max_attempts
                                     THEN 'queued' ELSE 'failed' END,
                        lease_owner = NULL,
                        lease_expires_at = NULL,
                        heartbeat_at = NULL,
                        failure_code = CASE WHEN attempts >= :max_attempts
                                            THEN 'attempts_exhausted' END,
                        finished_at = CASE WHEN attempts >= :max_attempts
                                           THEN :now END,
                        version = version + 1
                    WHERE id = :job_id AND lease_owner = :owner
                      AND state = 'running'
                      AND effect_committed_at IS NULL
                    RETURNING state, attempts
                    """
                ),
                {
                    "job_id": job_id,
                    "owner": owner,
                    "now": now,
                    "max_attempts": self._max_attempts,
                },
            )
            .mappings()
            .one_or_none()
        )
        if row is not None:
            return Abandonment(state=row["state"], effect_committed=False)
        # Zero rows. Which of the two reasons it was is a fact about the row, so
        # it is read from the row rather than inferred — in this same
        # transaction, immediately after the statement that lost.
        probe = (
            self._connection.execute(
                text(
                    """
                    SELECT lease_owner, state, effect_committed_at
                    FROM reconciliation_jobs WHERE id = :job_id
                    """
                ),
                {"job_id": job_id},
            )
            .mappings()
            .one_or_none()
        )
        committed = (
            probe is not None
            and probe["effect_committed_at"] is not None
            and probe["lease_owner"] == owner
            and probe["state"] == "running"
        )
        return Abandonment(state=None, effect_committed=committed)

    def reap(self, *, limit: int = 20):
        """Schema §10.1's reaper: one statement, two outcomes, no gap between them.

        **Ordinary expiries only.** `AND effect_committed_at IS NULL` in the
        locking sub-select is the 2026-08-18 effect-publication remediation: an
        expired lease over a job whose import already committed is not an attempt
        to retry or exhaust, it is a **publication the platform owes**, and it is
        taken by `lock_unpublished_effect` instead. Before that predicate the
        reaper chose from `attempts` alone, so an apply whose effect committed on
        attempt three and whose process died before publishing became `failed`
        with `attempts_exhausted` over a durable import — the second of the two
        blocking findings this remediation exists for.

        - `attempts < 3` — the lease is recoverable, exactly as N-23 requires.
          The job returns to `queued` with a remaining attempt, satisfying
          `CHECK (state <> 'queued' OR attempts < 3)` by construction.
        - `attempts = 3` — the budget is spent. The job goes **directly** to
          `failed` with `attempts_exhausted`. It does not wait for a fourth
          claim, which the cap forbids; it does not sit in `queued` waiting for a
          claim that would be refused; it does not sit in `running` with nobody
          running it.

        The `CASE` expressions with no `ELSE` yield `NULL` on the requeue branch,
        which is what `failure_code` and `finished_at` **must** be for a
        non-terminal job — so both terminal-state check constraints hold on both
        branches of the same statement. That is not a coincidence to be preserved
        by care: if a future edit breaks it, the constraint rejects the statement.

        `FOR UPDATE SKIP LOCKED` in the sub-select is what makes two concurrent
        reapers safe: each row is transitioned by exactly one of them, and the
        other skips it rather than blocking or double-counting. `LIMIT` bounds a
        single pass so a backlog cannot turn one tick into a long transaction.
        """
        # One statement, in three CTEs, and the shape is forced by one fact:
        # `RETURNING` yields the row **after** the update, so the lease this pass
        # cleared is `NULL` by the time it could be returned. The audit event the
        # terminal branch owes has to name the worker that stopped answering — it
        # is the only thing an operator has to find the process with — so the
        # owner is captured in the locking select and joined back.
        #
        # `FOR UPDATE SKIP LOCKED` still lives in `expired`, which is what makes
        # two concurrent reapers safe: each row is transitioned by exactly one of
        # them, and the other skips it rather than blocking or double-counting.
        return (
            self._connection.execute(
                text(
                    """
                    WITH expired AS (
                        SELECT id, lease_owner AS previous_owner
                        FROM reconciliation_jobs
                        WHERE state = 'running' AND lease_expires_at < now()
                          -- An expired lease over a committed effect is a
                          -- publication this statement must not turn into a
                          -- retry or an exhaustion. `lock_unpublished_effect`
                          -- takes those.
                          AND effect_committed_at IS NULL
                        ORDER BY lease_expires_at
                        FOR UPDATE SKIP LOCKED
                        LIMIT :limit
                    ), reaped AS (
                        UPDATE reconciliation_jobs SET
                            state = CASE WHEN attempts < :max_attempts
                                         THEN 'queued' ELSE 'failed' END,
                            lease_owner = NULL,
                            lease_expires_at = NULL,
                            heartbeat_at = NULL,
                            failure_code = CASE WHEN attempts >= :max_attempts
                                                THEN 'attempts_exhausted' END,
                            finished_at = CASE WHEN attempts >= :max_attempts
                                               THEN now() END,
                            version = version + 1
                        FROM expired
                        WHERE reconciliation_jobs.id = expired.id
                        RETURNING reconciliation_jobs.id, reconciliation_jobs.state,
                                  reconciliation_jobs.attempts,
                                  reconciliation_jobs.correlation_id,
                                  reconciliation_jobs.kind,
                                  reconciliation_jobs.requested_by_account_id
                    )
                    SELECT reaped.id, reaped.state, reaped.attempts,
                           reaped.correlation_id, reaped.kind,
                           reaped.requested_by_account_id,
                           expired.previous_owner AS lease_owner
                    FROM reaped JOIN expired ON expired.id = reaped.id
                    """
                ),
                {"limit": limit, "max_attempts": self._max_attempts},
            )
            .mappings()
            .all()
        )

    # -- publishing an effect whose process died ---------------------------
    def lock_unpublished_effect(self):
        """One expired job whose effect committed and whose result never did.

        The counterpart of `reap`'s locking sub-select, and deliberately a
        separate statement rather than a third branch of it: reaping is one
        `UPDATE` over up to twenty rows, and publishing a result is a read of two
        durable rows followed by an insert, an update and an audit event. Folding
        the second into the first would make one bad publication roll back
        nineteen good reaps.

        **`FOR UPDATE` without a following `UPDATE` here is the point.** The row
        lock is taken now and held for the rest of the caller's transaction, which
        is the transaction that inserts the result, completes the job and records
        the completion event. That is what makes two concurrent recoveries
        serialize: the second `SKIP LOCKED`s the row, sees nothing to do, and
        writes nothing — rather than blocking and then inserting a second result.

        `lease_expires_at < now()` is what keeps this out of the live worker's
        way. While the lease is alive the process that ran the attempt may still
        publish — that is what `EFFECT_PUBLICATION_GRACE_HEARTBEATS` is for — and
        the platform only publishes on its behalf once the lease it was holding
        has lapsed. Both writers carry predicates the other invalidates, so
        whichever reaches the row first, the second matches nothing.

        Returns `None` when there is nothing to publish, which is the ordinary
        case on every pass.
        """
        return (
            self._connection.execute(
                text(
                    """
                    SELECT * FROM reconciliation_jobs
                    WHERE state = 'running'
                      AND effect_committed_at IS NOT NULL
                      AND lease_expires_at < now()
                    ORDER BY effect_committed_at
                    FOR UPDATE SKIP LOCKED
                    LIMIT 1
                    """
                )
            )
            .mappings()
            .one_or_none()
        )

    def complete_recovered_effect(
        self, *, job_id: UUID, result_id: UUID, now: datetime
    ) -> bool:
        """`running -> completed` for an effect the platform published itself.

        Deliberately **not** `complete`: that statement carries `AND lease_owner =
        :owner`, and the whole premise here is that the owner of that lease is
        gone. What replaces the lease as the entitlement is
        `effect_committed_at IS NOT NULL` — the durable fact that this job's
        import committed — plus the row lock `lock_unpublished_effect` is still
        holding in this same transaction.

        `attempts` is untouched, no lease is minted and nothing is claimed, so
        N-43's cap is neither spent nor disguised: this is a publication, not a
        fourth execution.

        Returns `False` if the row moved underneath the caller, which under the
        held lock cannot happen and is therefore treated as a fault rather than as
        a race: the caller raises and the whole transaction — result row included
        — rolls back.
        """
        return (
            self._connection.execute(
                text(
                    """
                    UPDATE reconciliation_jobs SET
                        state = 'completed',
                        result_id = :result_id,
                        finished_at = :now,
                        lease_owner = NULL,
                        lease_expires_at = NULL,
                        heartbeat_at = NULL,
                        version = version + 1
                    WHERE id = :job_id
                      AND state = 'running'
                      AND effect_committed_at IS NOT NULL
                    """
                ),
                {"job_id": job_id, "result_id": result_id, "now": now},
            ).rowcount
            == 1
        )

    # -- cancellation and invalidation, from a request --------------------
    def request_cancel(self, *, job_id: UUID, now: datetime):
        """R-45. A `queued` job cancels immediately; a `running` one is asked.

        Two statements, and the first one's `RETURNING` decides whether the
        second runs — rather than a read followed by a write, which would let the
        job change state in between and be cancelled from `completed`.

        `AND effect_committed_at IS NULL` on the `running` statement is what
        makes SM-05's "a committed apply can never be cancelled" true **during**
        the commit rather than only after it (2026-08-18 remediation). Before it,
        the apply's effect and the job's `completed` state were two transactions,
        and a cancellation arriving between them matched a still-`running` job
        and cancelled a job whose import had already committed.

        The predicate is enforced by PostgreSQL's row lock, not by ordering: the
        commit fence takes this row's write lock as the last statement before the
        effect commits, so this statement blocks and then re-evaluates under
        `READ COMMITTED`. If the effect won, this matches zero rows and the
        caller answers `409` with the receipt. If this won, the fence matches
        zero rows and the effect is rolled back entirely.

        ## Both branches carry it, from 2026-08-18

        The first remediation put the predicate on the `running` branch only,
        because the `queued` branch was believed unreachable for a committed
        effect. It was not. The reaper deliberately requeued a job whose effect
        had committed but whose result had not been published, so this ordering
        existed and produced a `cancelled` job over a durable import:

        ```text
            apply commits import + effect_committed_at        COMMIT
            the process dies before publishing its result
            the lease expires; the reaper writes state = 'queued'
            R-45 arrives and matches `state = 'queued'`        → cancelled
        ```

        The reaper no longer requeues a committed effect — it publishes it — so
        the ordering above is gone at its source as well. The predicate is here
        anyway, on both branches, because *"every cancellation statement capable of
        touching a live job refuses a committed effect"* is a property a reader can
        check in one place, and *"no other statement can put such a job in that
        state"* is a property they would have to reconstruct from four.
        """
        from application.web.jobs import Cancellation, JobState

        cancelled = self._connection.execute(
            text(
                """
                UPDATE reconciliation_jobs SET
                    state = 'cancelled',
                    cancel_requested_at = COALESCE(cancel_requested_at, :now),
                    finished_at = :now,
                    version = version + 1
                WHERE id = :job_id AND state = 'queued'
                  AND effect_committed_at IS NULL
                RETURNING id
                """
            ),
            {"job_id": job_id, "now": now},
        ).first()
        if cancelled is not None:
            return Cancellation(
                state=JobState.CANCELLED,
                effect_committed=False,
                observed_state=JobState.CANCELLED,
            )
        # `running`: record the request and let the worker observe it at its next
        # heartbeat. A committed apply matches neither statement.
        requested = self._connection.execute(
            text(
                """
                UPDATE reconciliation_jobs SET
                    cancel_requested_at = COALESCE(cancel_requested_at, :now),
                    version = version + 1
                WHERE id = :job_id AND state = 'running'
                  AND effect_committed_at IS NULL
                RETURNING id
                """
            ),
            {"job_id": job_id, "now": now},
        ).first()
        if requested is not None:
            return Cancellation(
                state=JobState.RUNNING,
                effect_committed=False,
                observed_state=JobState.RUNNING,
            )
        # Refused. **Which** refusal it was is a fact about the row, so it is read
        # from the row — in this same transaction, immediately after the two
        # statements that matched nothing, exactly as `abandon` does. This read
        # decides the word in the response; it decides nothing about the
        # invariant, which both statements above already enforced at the write
        # boundary.
        probe = (
            self._connection.execute(
                text(
                    """
                    SELECT state, effect_committed_at
                    FROM reconciliation_jobs WHERE id = :job_id
                    """
                ),
                {"job_id": job_id},
            )
            .mappings()
            .one_or_none()
        )
        return Cancellation(
            state=None,
            effect_committed=probe is not None
            and probe["effect_committed_at"] is not None,
            observed_state=None if probe is None else JobState(probe["state"]),
        )

    def mark_stale(self, *, job_id: UUID, reason, now: datetime) -> bool:
        """One job to `stale`, from a request.

        ## Why `completed` is in the predicate, and why that is not a
        ## terminal-state rewrite

        SM-05's forbidden-transition table says *any terminal state to any other
        state*, and names its mechanism as "the application's single-statement
        guards on `state IN ('queued','running')`". Route contract §6.1 requires
        the opposite for one case, in as many words: R-41 must transition **every
        completed-but-unconfirmed preview** to `stale`.

        Both cannot be read literally, and the specific requirement is the one
        that governs — with the boundary drawn exactly where the two agree:

        - a **`completed` preview that no apply names** is not a record of
          anything that happened. It is an offer to confirm, and `stale` is what
          withdrawing that offer is called. Nothing durable is rewritten,
          because a preview writes only its own result row;
        - a **`completed` apply**, and a preview an apply already names, are
          never touched. An apply that completed has committed an import, and
          rewriting its state would be rewriting the record of something that
          did happen.

        The `parent_job_id` clause is what expresses "unconfirmed". It is the
        same predicate `invalidate_for_snapshot` uses, and it is one
        implementation rather than two that agree: R-41's folder change and
        R-46's N-46 expiry withdraw the same kind of offer for different reasons.
        """
        return (
            self._connection.execute(
                text(
                    """
                    UPDATE reconciliation_jobs SET
                        state = 'stale',
                        stale_reason = :reason,
                        finished_at = COALESCE(finished_at, :now),
                        lease_owner = NULL,
                        lease_expires_at = NULL,
                        heartbeat_at = NULL,
                        -- Required by `CHECK ((state = 'completed') = (result_id
                        -- IS NOT NULL))`: only a `completed` job names a result.
                        -- The result row itself is **not** deleted — it is still
                        -- reachable from its own `job_id`, which is how a stale
                        -- preview still shows what it said.
                        result_id = NULL,
                        version = version + 1
                    WHERE id = :job_id
                      -- Added 2026-08-18 with the commit fence. An apply whose
                      -- import has committed is a record of something that
                      -- happened, and `stale` means "nothing was applied" — so
                      -- the same argument that excludes a `completed` apply
                      -- excludes a `running` or requeued one whose effect is
                      -- already durable. A preview can never carry this column
                      -- (migration 0012's check constraint), so this narrows
                      -- nothing R-41 or R-46 was for.
                      AND effect_committed_at IS NULL
                      AND (
                            state IN ('queued', 'running')
                            OR (
                                state = 'completed'
                                AND kind = 'preview'
                                AND NOT EXISTS (
                                    SELECT 1 FROM reconciliation_jobs child
                                    WHERE child.parent_job_id = reconciliation_jobs.id
                                )
                            )
                          )
                    """
                ),
                {"job_id": job_id, "reason": reason.value, "now": now},
            ).rowcount
            == 1
        )

    def invalidate_for_snapshot(
        self, *, snapshot_id: UUID, reason, now: datetime
    ) -> tuple:
        """R-41's atomic invalidation: **every** non-terminal job **and** every
        completed-but-unconfirmed preview for this snapshot.

        One statement, so there is no instant at which the folder has changed and
        an outstanding preview is still confirmable.

        A `completed` preview is included and a `completed` **apply** is not: an
        apply that completed has already committed its import, and rewriting its
        state would be rewriting the record of something that happened. The
        `parent_job_id` clause is what expresses "unconfirmed" — a preview an
        apply already names has been confirmed, and its outcome is that apply's.
        """
        rows = self._connection.execute(
            text(
                """
                UPDATE reconciliation_jobs SET
                    state = 'stale',
                    stale_reason = :reason,
                    finished_at = COALESCE(finished_at, :now),
                    lease_owner = NULL,
                    lease_expires_at = NULL,
                    heartbeat_at = NULL,
                    -- See `mark_stale`: the constraint reserves `result_id` for
                    -- `completed`, and the result row survives regardless.
                    result_id = NULL,
                    version = version + 1
                WHERE snapshot_id = :snapshot_id
                  -- See `mark_stale`: an apply whose effect has committed is
                  -- never rewritten to `stale`, because `stale` means nothing
                  -- was applied and something was.
                  AND effect_committed_at IS NULL
                  AND (
                        state IN ('queued', 'running')
                        OR (
                            state = 'completed'
                            AND kind = 'preview'
                            AND NOT EXISTS (
                                SELECT 1 FROM reconciliation_jobs child
                                WHERE child.parent_job_id = reconciliation_jobs.id
                            )
                        )
                      )
                RETURNING id
                """
            ),
            {"snapshot_id": snapshot_id, "reason": reason.value, "now": now},
        ).all()
        return tuple(row[0] for row in rows)

    # -- N-24 retention ----------------------------------------------------
    def expired_results(self, *, now: datetime, limit: int = 200) -> tuple:
        """Result rows past N-24, for the operator's retention sweep.

        Read here and deleted by the operator command, not by the web process:
        the runtime role holds no `DELETE` on `reconciliation_jobs` (grants
        template), so the sweep runs as the schema owner and this method exists
        so it can be *reported* before it is run.
        """
        rows = self._connection.execute(
            select(reconciliation_job_results.c.id, reconciliation_job_results.c.job_id)
            .where(reconciliation_job_results.c.expires_at < now)
            .limit(limit)
        ).all()
        return tuple((row[0], row[1]) for row in rows)


class AuditSearchRepository:
    """R-48/R-49's bounded read over `audit_events`. **There is no write here.**

    Not "no write is called": no method exists. The append-only guarantee is the
    runtime role's grant and migration 0002's trigger; this class is the
    application-level half of the same statement, and TC-AUD-04 asserts it by
    introspection rather than by reading the file.
    """

    __slots__ = ("_connection",)

    def __init__(self, connection: Connection) -> None:
        self._connection = connection

    def search(self, *, filters, position, size: int):
        """`(occurred_at DESC, id DESC)`, cursor-positioned, over-read by one.

        Every filter is an equality, a prefix or a range — all index-usable, and
        none of them a scan of the payload. There is deliberately no free-text
        payload search: an append-only table that grows forever cannot serve one
        within N-21's bound, and offering it would be offering a query that gets
        slower every day until it stops working.
        """
        statement = select(audit_events)
        if filters.action_prefix is not None:
            # A prefix, not a substring: `reconciliation.` is an index range and
            # `%council%` is a scan of every row ever written.
            statement = statement.where(
                audit_events.c.action.startswith(
                    filters.action_prefix.value, autoescape=True
                )
            )
        if filters.entity_type is not None:
            statement = statement.where(
                audit_events.c.entity_type == filters.entity_type
            )
        if filters.entity_id is not None:
            statement = statement.where(
                audit_events.c.entity_id == filters.entity_id.value
            )
        if filters.capability is not None:
            statement = statement.where(
                audit_events.c.actor_capability == filters.capability.value
            )
        if filters.source is not None:
            statement = statement.where(audit_events.c.source == filters.source)
        if filters.correlation_id is not None:
            statement = statement.where(
                audit_events.c.correlation_id == filters.correlation_id
            )
        if filters.occurred_from is not None:
            statement = statement.where(
                audit_events.c.occurred_at
                >= datetime.fromisoformat(filters.occurred_from.iso_utc)
            )
        if filters.occurred_to is not None:
            statement = statement.where(
                audit_events.c.occurred_at
                <= datetime.fromisoformat(filters.occurred_to.iso_utc)
            )
        if position is not None:
            occurred_at, identifier = position
            statement = statement.where(
                or_(
                    audit_events.c.occurred_at < datetime.fromisoformat(occurred_at),
                    and_(
                        audit_events.c.occurred_at
                        == datetime.fromisoformat(occurred_at),
                        audit_events.c.id < UUID(identifier),
                    ),
                )
            )
        return list(
            self._connection.execute(
                statement.order_by(
                    audit_events.c.occurred_at.desc(), audit_events.c.id.desc()
                ).limit(size + 1)
            )
            .mappings()
            .all()
        )

    def labels_for_discord_actors(self, discord_user_ids) -> dict:
        """Historical attribution, resolved through `external_identities`.

        Rows written before migration 0006 carry only a Discord user id and are
        never rewritten (ADR 0010 D5). This resolves one to the account it now
        belongs to — **including when that identity has been retired**, which is
        the reason an identity is retired rather than deleted.
        """
        wanted = {
            identifier for identifier in discord_user_ids if identifier is not None
        }
        if not wanted:
            return {}
        rows = self._connection.execute(
            select(
                external_identities.c.subject,
                external_identities.c.platform_account_id,
                platform_accounts.c.display_label,
            )
            .select_from(
                external_identities.join(
                    platform_accounts,
                    external_identities.c.platform_account_id
                    == platform_accounts.c.id,
                )
            )
            .where(
                external_identities.c.provider_key == DISCORD_PROVIDER_KEY,
                external_identities.c.subject.in_(
                    [str(identifier) for identifier in wanted]
                ),
            )
        ).all()
        return {
            int(subject): {"account_id": account_id, "label": label or f"Account {str(account_id)[:8]}"}
            for subject, account_id, label in rows
        }
