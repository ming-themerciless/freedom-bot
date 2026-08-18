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
    role_capability_mapping_events,
    role_capability_mappings,
    sessions,
    sheet_row_mappings,
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
