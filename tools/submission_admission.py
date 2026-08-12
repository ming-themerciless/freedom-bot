"""Open and close the submission admission generation. The settlement operation.

This is the operator half of the fence described in `application/admissions.py`.
Recovery no longer settles a lost-pin episode by stopping the endpoint and
terminating the proxy in front of it; it settles it by **closing the admission
generation the submitting credential writes under**, which is a transaction
rather than an outage.

## Why closure takes `FOR UPDATE` before it updates anything

Because a plain `UPDATE` of a non-key column is not a fence, and looks exactly
like one.

An acceptance's foreign key into `submission_admissions` takes a `KEY SHARE` lock
on the admission row. `UPDATE … SET state = 'closed'` takes `FOR NO KEY UPDATE`,
which does **not** conflict with `KEY SHARE` — so a closure written the obvious
way would sail straight past an acceptance that was already waiting, and both
would commit. `SELECT … FOR UPDATE` does conflict. This was measured against this
host's PostgreSQL 16.14, not reasoned about; the measurement lives in
`tests/test_submission_admission_postgresql.py` and fails if it ever stops
holding.

The exclusive advisory lock is taken first, for the paths that write nothing: a
same-key retry returns a stored receipt without inserting a row, so it takes no
foreign-key lock, and only the advisory lock puts it on one side of a closure.

## Why closing is not the same as revoking the credential

Revoking the credential (operations §5.3) stops *new* requests being
authenticated by the running process. It does nothing to a request that
authenticated before the reload and is paused somewhere — which is the entire
class of failure finding B-1 is open against. Closing the admission reaches that
request, because the check happens inside its own transaction, at the moment it
tries to make something durable, against the admission its own credential names.

Both are worth doing, in this order: close the admission (which is decisive and
takes effect for work already accepted), then rotate the credential (which is
what a new generation is opened for).

## What this tool will not do

There is no `reopen`. A trigger in migration 0005 refuses it, and this tool does
not pretend to offer it: a generation that could be reopened would be
indistinguishable afterwards from one that was never closed, and every settlement
record written against it would become unfalsifiable. After a closure, recovery
issues a **new** credential (operations §5.2) and opens a **new** generation
naming it. The old request cannot present a credential it was never sent with.

## Safety

Reads `DATABASE_URL` through `adapters.database.config.DatabaseSettings`, which
resolves the ambient libpq environment and refuses a named remote host.
`APP_ENVIRONMENT` selects which database name is permitted and **defaults to
`development`**, exactly as it does for Alembic, so a command that omits it can
only ever reach `freedom_dev`. Settling production is therefore a deliberate act
that names both:

    APP_ENVIRONMENT=production \\
    DATABASE_URL='postgresql+psycopg://__OWNER_ROLE__@/freedom_production' \\
    ./venv/bin/python -m tools.submission_admission show

`__OWNER_ROLE__` is the role that **owns** `submission_admissions` — the
migration/schema owner named in `docs/operations/database-development.md`, not
the environment's restricted runtime login role (`freedom_production_app` and
its siblings). The runtime role holds `SELECT` on this table and nothing else;
that asymmetry is the point, not an inconvenience, and `open` and `close` run as
the owner because of it. Substitute the real role through the deployment's
secret-safe templating, the way `infra/postgresql/runtime-grants.sql.tmpl` does;
it is not written down here.

    APP_ENVIRONMENT=production \\
    DATABASE_URL='postgresql+psycopg://__OWNER_ROLE__@/freedom_production' \\
    ./venv/bin/python -m tools.submission_admission open \\
        --principal foundry-the-guild-r1 \\
        --operator 'A. Operator' \\
        --reason 'Recovery generation after episode 2026-08-12-a.'
    APP_ENVIRONMENT=production \\
    DATABASE_URL='postgresql+psycopg://__OWNER_ROLE__@/freedom_production' \\
    ./venv/bin/python -m tools.submission_admission close \\
        --principal foundry-the-guild \\
        --operator 'A. Operator' \\
        --reason 'Settling lost-pin episode 2026-08-12-a.'

## Exit codes

Every failure is a distinct, documented code, because an operator settling an
episode has to be able to tell "nothing was closed, retry" from "nothing was
closed, escalate" without reading a traceback:

| Code | Meaning |
|---|---|
| 0 | The command succeeded. |
| 1 | Refused before touching the database. Nothing was written. |
| 2 | The connection target was refused by configuration validation. |
| 3 | The database could not be reached. Nothing was read or written. |
| 4 | The database refused the operation for lack of privilege. |
| 5 | `lock_timeout`. **Unsettled**, and safe to retry. |
| 6 | Another database failure. The transaction did not commit. |
| 7 | Lost connection after the transaction began. **Outcome unknown — Unsettled.** Verify with `show`. |

Codes 1 to 6 accompany a statement that nothing was opened or closed, and each
of them is reached only with the transaction rolled back. **Code 7 makes no such
claim**, and that is the whole reason it exists.

## Why an absent SQLSTATE is not proof that nothing committed

A `DBAPIError` with no SQLSTATE means the client never received a server
response. Until this correction the tool read that as "could not connect" and
told the operator, for `close`, that no generation was closed and the fence was
unchanged. **That conclusion is not sound.** A connection can be lost while
PostgreSQL is processing or acknowledging `COMMIT`; the server may have
committed while the client sees only a driver error. No amount of client-side
observation distinguishes the two — which is the same lesson the fence itself
rests on, arriving at the operator surface instead of the acceptance boundary.

So the phase is **recorded rather than inferred**. `CommandProgress` is marked
the moment a transaction has been established, and a failure with no SQLSTATE is
classified by that mark:

- unmarked — the connection was never established, the transaction never began,
  and nothing was written. Exit 3, and it is sound to say so;
- marked — the failure happened after the transaction began, possibly at the
  commit. Exit 7, **Outcome unknown**, and nothing is claimed about the fence.

The second bucket deliberately includes failures during an ordinary statement,
where in truth no `COMMIT` was ever sent. Separating those would mean trusting
the client's account of how far it got, and a lost connection is exactly the
event that makes that account unreliable. False uncertainty costs one `show`;
a false assertion that settlement did not occur costs a duplicate accepted
export, which is the failure this whole mechanism exists to prevent.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from uuid import UUID, uuid4

from sqlalchemy import Engine, create_engine, text
from sqlalchemy.exc import DBAPIError

from adapters.database.config import DatabaseSettings
from adapters.database.safety import ConnectionPolicy, UnsafeDatabaseTargetError
from application.admissions import ADMISSION_LOCK_KEY, PRE_FENCE_PRINCIPAL
from application.audit import ActorCapability, AuditEvent, AuditSource
from application.foundry.audit_policy import (
    ADMISSION_CLOSED,
    ADMISSION_OPENED,
    enforced,
)
from application.service_principals import ServicePrincipal, ServicePrincipalScope

#: How long a closure waits for an acceptance that is already in flight before
#: giving up. A closure that waits is a closure doing its job — the acceptance
#: ahead of it commits, and settlement then reads a database that contains it —
#: but an unbounded wait would leave an operator with no defined outcome. On
#: timeout nothing is closed and the episode is Unsettled, which is the
#: fail-closed direction.
LOCK_TIMEOUT = "15s"

#: Bounds operator-authored text before it reaches append-only history. Not
#: validation of meaning: it is what stops a paste accident becoming a permanent
#: row nobody can shorten.
REASON_MAX_LENGTH = 500
OPERATOR_MAX_LENGTH = 120

#: See the module docstring. Named rather than spelled inline so the runbook,
#: the tests and the code cannot drift apart.
EXIT_OK = 0
EXIT_REFUSED = 1
EXIT_UNSAFE_TARGET = 2
EXIT_CANNOT_CONNECT = 3
EXIT_INSUFFICIENT_PRIVILEGE = 4
EXIT_LOCK_TIMEOUT = 5
EXIT_DATABASE_FAILURE = 6
EXIT_OUTCOME_UNKNOWN = 7

#: The two commands that change the fence. Only these can have an ambiguous
#: outcome: `show` writes nothing, so a failure during it settles nothing either
#: way and has nothing to verify afterwards.
TRANSITIONS = frozenset({"open", "close"})

#: The two SQLSTATEs this tool can say something specific and *operational*
#: about. Everything else is a database failure with its code reported verbatim.
SQLSTATE_LOCK_NOT_AVAILABLE = "55P03"
SQLSTATE_INSUFFICIENT_PRIVILEGE = "42501"


class AdmissionToolError(RuntimeError):
    """The operation was refused. Nothing was written."""


class CommandProgress:
    """How far this command got. **Recorded as it happens, never inferred.**

    One fact, and it is the one that decides whether "nothing was written" is a
    sound thing to print: has a database transaction been established? Marked
    inside the `with engine.begin()` block, so it is set if and only if a
    connection was checked out and a transaction opened — which means the
    failure that follows could be anywhere from the first statement to the
    commit acknowledgement, and the client cannot tell which.

    Deliberately not a phase enum. A finer record — "in a statement" versus "at
    the commit" — is available in principle, since statements run inside the
    block and the commit runs as it exits, but acting on it would mean asserting
    "the transaction did not commit" on the strength of the client's own account
    of how far it got. A lost connection is precisely the event that makes that
    account unreliable, and the fail-safe direction is to leave the outcome
    unknown. See the module docstring.
    """

    __slots__ = ("_began",)

    def __init__(self) -> None:
        self._began = False

    @property
    def began(self) -> bool:
        """Whether a transaction was established before the failure."""
        return self._began

    def transaction_began(self) -> None:
        self._began = True


@dataclass(frozen=True, slots=True)
class DatabaseFailure:
    """A database error rendered as an operator outcome, with nothing extra.

    `message` is written for someone settling an episode at 2 a.m., so it says
    what state the database is in first and what to do second. It carries no
    traceback, no connection string, no credential and no SQL: `str()` of a
    SQLAlchemy `DBAPIError` includes the statement and its parameters, which is
    why nothing here is built from it.
    """

    exit_code: int
    message: str


def _sqlstate(error: DBAPIError) -> str | None:
    """The server's SQLSTATE, when the failure reached a server at all.

    psycopg 3 puts it on the driver exception; a connection failure never got a
    response, so it has none. That absence is itself the classification, and it
    is the only thing distinguishing "could not connect" from a refusal the
    server issued.
    """
    return getattr(error.orig, "sqlstate", None)


def _server_detail(error: DBAPIError) -> str:
    """The server's own primary message, or nothing.

    Deliberately `diag.message_primary` rather than any rendering of the
    exception: the primary message is the one line PostgreSQL wrote about the
    condition, without the statement SQLAlchemy appends and without the
    parameters bound to it.
    """
    diagnostic = getattr(error.orig, "diag", None)
    primary = getattr(diagnostic, "message_primary", None)
    return f" PostgreSQL said: {primary}." if primary else ""


def _outcome_unknown(command: str) -> DatabaseFailure:
    """The connection was lost after the transaction began. Claim nothing.

    Every word here is chosen against the two failures an operator can make with
    an ambiguous settlement: treating it as done, and treating it as not done.
    So it names the state as unknown, sends them to `show` and to the
    append-only event before anything else, and says what each verified answer
    then means. It never says the fence is unchanged, never says the transition
    did not commit, and never suggests a blind retry.
    """
    verify = (
        "Reconnect and run `show` before doing anything else, and confirm the "
        "transition against its append-only audit event — "
        "`submission_admissions.correlation_id` and `closed_correlation_id` "
        "each name one `snapshot_submission.admission_opened` or "
        "`.admission_closed` row."
    )
    if command == "close":
        return DatabaseFailure(
            EXIT_OUTCOME_UNKNOWN,
            "Outcome unknown. The connection was lost after this closure's "
            "transaction had begun, so PostgreSQL may have committed it without "
            "this command ever hearing that it did. Client observation cannot "
            "tell those apart, so nothing here says whether the generation is "
            "closed. Treat the episode as **Unsettled**. "
            f"{verify} If it reads closed, the settlement happened and needs no "
            "retry. If it reads open, run this same close command again: "
            "closing is idempotent once you have verified. Do not authorize a "
            "fresh export until a closure has been verified.",
        )
    return DatabaseFailure(
        EXIT_OUTCOME_UNKNOWN,
        "Outcome unknown. The connection was lost after this open's transaction "
        "had begun, so a generation may have been created for this credential "
        "without this command ever hearing that it was. Treat the outcome as "
        f"**Unsettled**. {verify} An ambiguous open must be verified before you "
        "attempt another principal or generation: a credential holds at most "
        "one admission for all time, so opening a second one for it is refused "
        "permanently, and a credential that already has an open generation "
        "needs no second command.",
    )


def classify_database_failure(
    error: DBAPIError, *, command: str, progress: CommandProgress
) -> DatabaseFailure:
    """Turn a database error into one documented outcome. It never guesses open.

    Every branch below states that nothing was written **except** the ambiguous
    one, and the distinction is the point of `progress`. A server SQLSTATE means
    the server answered, so the transaction did not commit; no SQLSTATE means
    the client never heard anything, and only whether a transaction had been
    established says which of the two unheard outcomes is possible.
    """
    nothing = {
        "open": "No generation was opened",
        "close": "No generation was closed and the fence is unchanged",
        "show": "Nothing was read",
    }[command]
    sqlstate = _sqlstate(error)

    if sqlstate is None:
        if progress.began and command in TRANSITIONS:
            return _outcome_unknown(command)
        return DatabaseFailure(
            EXIT_CANNOT_CONNECT,
            f"Could not reach the database. {nothing}. Check that PostgreSQL is "
            "running, that APP_ENVIRONMENT and DATABASE_URL name this "
            "environment's database, and that the operator role may connect "
            "over the local socket.",
        )

    if sqlstate == SQLSTATE_LOCK_NOT_AVAILABLE:
        if command == "close":
            return DatabaseFailure(
                EXIT_LOCK_TIMEOUT,
                f"The closure waited {LOCK_TIMEOUT} for a submission that was "
                f"already committing and gave up. {nothing}. This is the "
                "Unsettled outcome in the runbook's lost-pin step 3, and it is "
                "safe to retry: run this same command again, and only then the "
                "acceptance-event query. Do not authorize a fresh export until "
                "a closure has succeeded. A timeout here usually means the "
                "episode will settle as a hit, because the thing that blocked "
                "the closure is the acceptance the query looks for. "
                f"(SQLSTATE {sqlstate}.)",
            )
        return DatabaseFailure(
            EXIT_LOCK_TIMEOUT,
            f"Waited {LOCK_TIMEOUT} for the admission lock and gave up. "
            f"{nothing}. A closure is probably in progress; wait for it to "
            f"finish and retry. (SQLSTATE {sqlstate}.)",
        )

    if sqlstate == SQLSTATE_INSUFFICIENT_PRIVILEGE:
        return DatabaseFailure(
            EXIT_INSUFFICIENT_PRIVILEGE,
            f"The database refused this for lack of privilege. {nothing}. "
            "`open` and `close` must run as the role that owns "
            "`submission_admissions` — the migration/schema owner — and not as "
            "the restricted runtime login role, which holds SELECT on that "
            f"table and nothing else by design. (SQLSTATE {sqlstate}.)"
            + _server_detail(error),
        )

    return DatabaseFailure(
        EXIT_DATABASE_FAILURE,
        "The database refused this and the transaction did not commit. "
        f"{nothing}. (SQLSTATE {sqlstate}.)" + _server_detail(error),
    )


def build_engine(environ: Mapping[str, str]) -> Engine:
    settings = DatabaseSettings.from_mapping(
        environ,
        environment=environ.get("APP_ENVIRONMENT", "development"),
        environ=environ,
        policy=ConnectionPolicy.SOCKET_OR_LOOPBACK,
    )
    return create_engine(settings.url)


def _checked_text(value: str, *, field: str, limit: int) -> str:
    stripped = value.strip()
    if not stripped:
        raise AdmissionToolError(f"--{field} is required and may not be blank.")
    if len(stripped) > limit:
        raise AdmissionToolError(
            f"--{field} may be at most {limit} characters; this one is "
            f"{len(stripped)}. It is written into append-only history."
        )
    if any(character < " " or character == "\x7f" for character in stripped):
        raise AdmissionToolError(
            f"--{field} must be printable text. It is recorded verbatim in "
            "append-only history, so a control character in it would corrupt "
            "every later rendering of that row."
        )
    return stripped


def _checked_principal(principal_id: str) -> str:
    """Refuse anything that is not a credential id the endpoint could present.

    Constructed rather than pattern-matched, so this tool and the authentication
    path agree by sharing one rule. It also refuses `PRE_FENCE_PRINCIPAL`, which
    migration 0005 owns: generation 0 stands for receipts written before the
    fence existed and must stay closed forever.
    """
    if principal_id == PRE_FENCE_PRINCIPAL:
        raise AdmissionToolError(
            f"{PRE_FENCE_PRINCIPAL!r} is the reserved pre-fence generation "
            "created by migration 0005. It is closed permanently and is not an "
            "admission an operator may manage."
        )
    try:
        ServicePrincipal(
            principal_id=principal_id,
            scopes=frozenset({ServicePrincipalScope.SUBMIT_SNAPSHOT}),
        )
    except ValueError as error:
        raise AdmissionToolError(f"--principal is not a usable id: {error}") from None
    return principal_id


def _audit(
    connection,
    action: str,
    payload: Mapping[str, object],
    *,
    correlation_id: UUID,
) -> None:
    """One append-only row per open and per close, inside the same transaction.

    Written through `enforced`, so the payload policy decides what may enter
    permanent history here exactly as it does on the submission path.

    **`correlation_id` is the caller's, and that is the whole point of the
    parameter.** An earlier revision generated one here while the admission row
    generated its own with `gen_random_uuid()`, so the row's `correlation_id` and
    `closed_correlation_id` columns named events that did not exist and the audit
    event named a transition nothing recorded. Two identifiers for one transition
    is the same as none. The caller mints one per transition and writes it to
    both, in this transaction, so the column is a join key rather than a
    decoration.

    `SYSTEM`, not `PLATFORM_ADMINISTRATOR`: the `human_action_has_an_actor`
    check constraint requires an identified Discord user for every attended
    capability, and an operator at a shell has none. The named human is carried
    in the payload as `operator`, which is the arrangement the supervised
    bootstrap already uses for `supervisor`.
    """
    event = AuditEvent(
        action=action,
        entity_type="submission_admission",
        entity_id=str(payload["service_principal_id"]),
        source=AuditSource.SYSTEM,
        actor_capability=ActorCapability.SYSTEM,
        correlation_id=correlation_id,
        payload=enforced(action, payload),
    )
    connection.execute(
        text(
            """
            INSERT INTO audit_events (
                id, actor_discord_user_id, actor_capability, action,
                entity_type, entity_id, source, correlation_id, payload
            ) VALUES (
                :id, NULL, :capability, :action,
                :entity_type, :entity_id, :source, :correlation_id,
                CAST(:payload AS jsonb)
            )
            """
        ),
        {
            "id": event.id,
            "capability": event.actor_capability.value,
            "action": event.action,
            "entity_type": event.entity_type,
            "entity_id": event.entity_id,
            "source": event.source.value,
            "correlation_id": event.correlation_id,
            "payload": json.dumps(event.json_payload()),
        },
    )


def open_admission(
    engine: Engine,
    *,
    principal_id: str,
    operator: str,
    reason: str,
    progress: CommandProgress | None = None,
) -> int:
    """Open a new generation for `principal_id`, or refuse.

    Refuses if that credential has *ever* held one. `principal_id` is unique in
    the table for all time, and this is where an operator meets that rule: after
    a closure, recovery issues a **new** credential and opens a generation naming
    it, so that no request holding the old one can be silently upgraded.

    `progress` records that a transaction was established, which is what lets a
    lost connection afterwards be reported as an unknown outcome rather than as
    a failure to connect. See `CommandProgress`.
    """
    progress = progress or CommandProgress()
    principal_id = _checked_principal(principal_id)
    operator = _checked_text(operator, field="operator", limit=OPERATOR_MAX_LENGTH)
    reason = _checked_text(reason, field="reason", limit=REASON_MAX_LENGTH)

    # One identifier for this transition, minted here and written to both the
    # admission row and its audit event below. See `_audit`.
    correlation_id = uuid4()

    with engine.begin() as connection:
        # A connection is checked out and a transaction is open. From here on,
        # a failure with no SQLSTATE could be anywhere up to and including the
        # commit acknowledgement, so nothing may claim this wrote nothing.
        progress.transaction_began()
        connection.execute(text(f"SET LOCAL lock_timeout = '{LOCK_TIMEOUT}'"))
        connection.execute(
            text("SELECT pg_advisory_xact_lock(:key)"), {"key": ADMISSION_LOCK_KEY}
        )
        existing = connection.execute(
            text(
                "SELECT generation, state FROM submission_admissions "
                "WHERE principal_id = :principal"
            ),
            {"principal": principal_id},
        ).one_or_none()
        if existing is not None:
            raise AdmissionToolError(
                f"{principal_id!r} already holds generation {existing[0]} "
                f"({existing[1]}). A credential holds at most one admission, "
                "ever — that is what stops a closed generation being replaced by "
                "an open one for the same credential. Issue a new credential "
                "(operations §5.2) and open a generation for that."
            )
        generation = (
            connection.execute(
                text("SELECT coalesce(max(generation), 0) + 1 FROM submission_admissions")
            ).scalar_one()
        )
        connection.execute(
            text(
                """
                INSERT INTO submission_admissions (
                    id, generation, principal_id, state,
                    opened_by, open_reason, correlation_id
                ) VALUES (
                    gen_random_uuid(), :generation, :principal, 'open',
                    :operator, :reason, :correlation_id
                )
                """
            ),
            {
                "generation": generation,
                "principal": principal_id,
                "operator": operator,
                "reason": reason,
                "correlation_id": correlation_id,
            },
        )
        _audit(
            connection,
            ADMISSION_OPENED,
            {
                "admission_generation": generation,
                "service_principal_id": principal_id,
                "operator": operator,
                "reason": reason,
            },
            correlation_id=correlation_id,
        )
    return generation


def close_admission(
    engine: Engine,
    *,
    principal_id: str,
    operator: str,
    reason: str,
    progress: CommandProgress | None = None,
) -> tuple[int, bool]:
    """Close `principal_id`'s generation. Returns `(generation, changed)`.

    `changed` is `False` when the generation was already closed, which is not an
    error: two operators settling the same episode, or one repeating the command
    after a lost connection, must both reach the same state rather than one of
    them reporting a failure over a database that is already correct.

    **The lock order below is the fence, and it is not interchangeable.** The
    exclusive advisory lock first, so a transaction that only replays a receipt
    cannot slip past; then `FOR UPDATE`, so an acceptance holding the row's `KEY
    SHARE` through its foreign key blocks this until it commits — and, in the
    other order, so an acceptance that arrives while this is held waits, and then
    reads `closed`. A bare `UPDATE` would conflict with neither.

    `progress` records that a transaction was established, which is what lets a
    lost connection afterwards be reported as an unknown outcome rather than as
    a false assurance that the fence is unchanged. See `CommandProgress`.
    """
    progress = progress or CommandProgress()
    principal_id = _checked_principal(principal_id)
    operator = _checked_text(operator, field="operator", limit=OPERATOR_MAX_LENGTH)
    reason = _checked_text(reason, field="reason", limit=REASON_MAX_LENGTH)

    # Minted per *transition*, not per call: a second close of an already-closed
    # generation returns below without using it, so no second identifier is
    # written for a transition that did not happen. See `_audit`.
    correlation_id = uuid4()

    with engine.begin() as connection:
        # See `open_admission`: from here on the outcome of a lost connection is
        # not knowable from this side, so nothing may claim the fence is
        # unchanged.
        progress.transaction_began()
        connection.execute(text(f"SET LOCAL lock_timeout = '{LOCK_TIMEOUT}'"))
        connection.execute(
            text("SELECT pg_advisory_xact_lock(:key)"), {"key": ADMISSION_LOCK_KEY}
        )
        row = connection.execute(
            text(
                "SELECT id, generation, state FROM submission_admissions "
                "WHERE principal_id = :principal FOR UPDATE"
            ),
            {"principal": principal_id},
        ).one_or_none()
        if row is None:
            raise AdmissionToolError(
                f"{principal_id!r} holds no admission, so there is nothing to "
                "close. Nothing was written. Check the principal id against "
                "FREEDOM_SNAPSHOT_PRINCIPALS and against `show`."
            )
        admission_id, generation, state = row
        if state == "closed":
            return generation, False

        connection.execute(
            text(
                """
                UPDATE submission_admissions
                SET state = 'closed',
                    closed_at = now(),
                    closed_by = :operator,
                    close_reason = :reason,
                    closed_correlation_id = :correlation_id
                WHERE id = :id
                """
            ),
            {
                "operator": operator,
                "reason": reason,
                "id": admission_id,
                "correlation_id": correlation_id,
            },
        )
        _audit(
            connection,
            ADMISSION_CLOSED,
            {
                "admission_generation": generation,
                "service_principal_id": principal_id,
                "operator": operator,
                "reason": reason,
            },
            correlation_id=correlation_id,
        )
    return generation, True


def show(engine: Engine) -> list[tuple]:
    with engine.connect() as connection:
        return list(
            connection.execute(
                text(
                    "SELECT generation, principal_id, state, opened_at, opened_by, "
                    "closed_at, closed_by FROM submission_admissions "
                    "ORDER BY generation"
                )
            )
        )


def parse_arguments(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    commands = parser.add_subparsers(dest="command", required=True)

    commands.add_parser("show", help="List every admission generation.")

    for name, help_text in (
        ("open", "Open a new generation for a credential that has never held one."),
        ("close", "Close a generation. This is the settlement operation."),
    ):
        sub = commands.add_parser(name, help=help_text)
        sub.add_argument("--principal", required=True)
        sub.add_argument("--operator", required=True, help="The named human running this.")
        sub.add_argument("--reason", required=True)

    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    """Run one command and return its documented exit code.

    The two `except` clauses are narrow on purpose. `AdmissionToolError` is this
    tool's own refusal and `DBAPIError` is every failure the database driver
    reports — a lock timeout, a lost connection, a missing privilege. A
    `TypeError` or an `AttributeError` is a defect in this file, and it keeps its
    traceback rather than being dressed up as an operational refusal an operator
    would then act on.
    """
    arguments = parse_arguments(argv)
    try:
        engine = build_engine(os.environ)
    except (UnsafeDatabaseTargetError, ValueError) as error:
        print(f"Refusing to connect: {error}", file=sys.stderr)
        return EXIT_UNSAFE_TARGET

    # Passed into the transition commands and read by the failure classifier, so
    # that "did this get far enough to have committed?" is a fact this run
    # recorded rather than a guess made from an exception. See `CommandProgress`.
    progress = CommandProgress()

    try:
        if arguments.command == "show":
            rows = show(engine)
            if not rows:
                print(
                    "No admission generation exists. The endpoint refuses every "
                    "submission until one is opened."
                )
            for row in rows:
                print(
                    f"generation {row[0]}  {row[2]:<6}  {row[1]}\n"
                    f"    opened {row[3]:%Y-%m-%d %H:%M:%S%z} by {row[4]}"
                    + (
                        f"\n    closed {row[5]:%Y-%m-%d %H:%M:%S%z} by {row[6]}"
                        if row[5] is not None
                        else ""
                    )
                )
        elif arguments.command == "open":
            generation = open_admission(
                engine,
                principal_id=arguments.principal,
                operator=arguments.operator,
                reason=arguments.reason,
                progress=progress,
            )
            print(
                f"Opened generation {generation} for {arguments.principal!r}. "
                "Submissions presenting that credential are now accepted."
            )
        else:
            generation, changed = close_admission(
                engine,
                principal_id=arguments.principal,
                operator=arguments.operator,
                reason=arguments.reason,
                progress=progress,
            )
            if changed:
                print(
                    f"Closed generation {generation} for {arguments.principal!r}. "
                    "No submission presenting that credential can be recorded "
                    "from here on, wherever it was paused. Run the "
                    "acceptance-event query now."
                )
            else:
                print(
                    f"Generation {generation} for {arguments.principal!r} was "
                    "already closed. Nothing changed; the fence is in force."
                )
    except AdmissionToolError as error:
        print(f"Refused: {error}", file=sys.stderr)
        return EXIT_REFUSED
    except DBAPIError as error:
        failure = classify_database_failure(
            error, command=arguments.command, progress=progress
        )
        print(failure.message, file=sys.stderr)
        return failure.exit_code
    finally:
        engine.dispose()
    return EXIT_OK


if __name__ == "__main__":  # pragma: no cover - console entry point
    raise SystemExit(main())
