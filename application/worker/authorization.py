"""The authority an apply commits under, resolved **at the moment it commits**.

`SnapshotImportService.apply` re-resolves through an `AuthorizationPort` — that
is the module's documented reason for existing, and SM-05 names it as the
mechanism that refuses an apply whose Council role was revoked between the
preview and the commit. This is that port, for the worker.

## Why the worker's port is stricter than the web request's, deliberately

The web request path resolves capability from the membership projection and, when
the projection is older than N-09, refreshes it at Discord before deciding.
The worker performs **no provider I/O at all**: it has no event loop, holds no
OAuth transport, and a database transaction held open across a network call to
Discord is exactly what the engineering rules forbid.

So this port answers from the projection alone, and refuses when the projection
is not **fresh** within N-09. That is stricter than the web path and it is the
correct direction:

- N-10 gives a **mutation** no grace whatsoever — it is refused the moment the
  provider cannot confirm the caller's current roles — and an apply is the most
  consequential mutation in Phase 3;
- the projection was refreshed by the R-46 request itself moments earlier, since
  the request preamble refreshes anything staler than N-09, so a job claimed
  within the poll interval finds a fresh projection as a matter of course;
- and a job that waits out N-09 in the queue is a job the platform has not
  confirmed authority for, which must fail closed rather than commit on a
  five-minute-old reading of somebody's roles.

A refusal here is `NotAuthorizedError`, which `SnapshotImportService.apply`
already turns into a refused import row and one audit event under the same
correlation id, claiming no partial state.
"""
from __future__ import annotations

from datetime import datetime

from application.authorization import AuthorizationContext, NotAuthorizedError
from application.web.capabilities import AuthMethod, resolve_capabilities


class WorkerAuthorizationPort:
    """Resolves current effective privilege from the membership projection.

    ## Why it opens its own connection

    `SnapshotImportService.apply` resolves authority as its **first** action,
    before it opens the unit of work that commits — that ordering is Phase 2's
    and is not changed here, because changing an accepted, gate-passed atomic
    boundary to make a new caller's composition tidier is exactly the kind of
    edit the package contract forbids.

    So this port reads on a connection of its own, taken from the worker's pool
    for the duration of one lookup. The window between that read and the commit
    is the same window the accepted design already has, and it is bounded by the
    apply's own re-checks: the scope fingerprint is compared inside the attempt,
    and the import's uniqueness constraints fence the durable effect regardless.
    """

    __slots__ = ("_engine", "_services", "_guild_id", "_clock", "_cache_seconds")

    def __init__(
        self,
        *,
        engine,
        services,
        guild_id: int,
        clock,
        cache_seconds: int,
    ) -> None:
        self._engine = engine
        #: `services(connection)` — the worker composition's factory, so the port
        #: builds the same repositories the rest of the process uses rather than
        #: a second construction of them.
        self._services = services
        self._guild_id = guild_id
        self._clock = clock
        self._cache_seconds = cache_seconds

    def context_for(self, discord_user_id: int) -> AuthorizationContext:
        with self._engine.connect() as connection:
            services = self._services(connection)
            return self._resolve(services, discord_user_id, self._clock())

    def _resolve(self, services, discord_user_id: int, now: datetime):
        projection = services.membership.load(
            discord_user_id=discord_user_id, guild_id=self._guild_id
        )
        if projection is None:
            raise NotAuthorizedError(
                "The platform holds no membership observation for this account, "
                "so current Guild Council authority cannot be confirmed and "
                "nothing was applied.",
                code="membership_unknown",
            )
        if not projection.is_fresh(now=now, cache_seconds=self._cache_seconds):
            # N-10's mutation rule, applied where the mutation happens. A stale
            # role is a display inaccuracy on a read and an unauthorized write
            # here, and the worker cannot ask Discord — so it fails closed.
            raise NotAuthorizedError(
                "The membership observation behind this apply is older than the "
                "accepted cache bound, so current Guild Council authority cannot "
                "be confirmed. Nothing was applied; produce a new preview and "
                "confirm it.",
                code="membership_observation_stale",
            )
        web_context = resolve_capabilities(
            account_id=self._account_id_for(services, discord_user_id),
            auth_method=AuthMethod.DISCORD_OAUTH,
            membership=projection,
            mappings=services.mappings.active_mappings(self._guild_id),
        )
        return AuthorizationContext(
            discord_user_id=discord_user_id,
            guild_member=web_context.guild_member,
            guild_council=web_context.guild_council,
            platform_administrator=web_context.platform_administrator,
        )

    def _account_id_for(self, services, discord_user_id: int):
        """The account this subject belongs to.

        `resolve_capabilities` needs one and the capability decision does not
        depend on it, but passing a fabricated identifier would put a value in a
        context that names nobody. If the identity is gone the apply is refused:
        an import committed under an account the platform cannot name is an
        import with no attribution, which the audit constraint would refuse
        anyway — better here, with a sentence, than at the driver.
        """
        account_id = services.accounts.account_for_active_identity(
            "discord", str(discord_user_id)
        )
        if account_id is None:
            raise NotAuthorizedError(
                "No platform account holds this Discord identity, so the apply "
                "would have no attribution. Nothing was applied.",
                code="identity_absent",
            )
        return account_id


__all__ = ["WorkerAuthorizationPort"]
