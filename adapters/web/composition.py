"""The composition root: one place where the portal's objects are wired together.

Everything the application layer needs is constructed here and injected, so no
service reaches for a global, reads an environment variable, or opens its own
transaction. That is what makes the services testable against fakes and what
makes the transaction rule — a state change and its audit event share one
transaction — expressible at all.

**One engine, bounded** (N-53). `pool_size=5`, `max_overflow=5`, a five-second
pool timeout and a ten-second `statement_timeout`, because this process is
co-located with three Foundry instances, the live bot and PostgreSQL. A web
request that needs more than ten seconds of SQL is a defect, and letting it hold
a connection while it proves that is an availability problem for everything else
on the host.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import Engine, create_engine

from adapters.web.repositories import (
    AccountRepository,
    MembershipProjectionRepository,
    OAuthTransactionRepository,
    RateLimitRepository,
    RecoveryGrantRepository,
    RoleMappingRepository,
    SessionRepository,
    TokenGrantRepository,
    WebAuditRepository,
    WebAuthnRepository,
)
from application.web.breakglass import BreakGlassService
from application.web.config import (
    DatabasePoolSettings,
    WebSettings,
    canonical_settings,
)
from application.web.crypto import Envelope
from application.web.oauth import OAuthLoginService
from application.web.rate_limit import RateLimiter
from application.web.role_mappings import RoleMappingService
from application.web.sessions import SessionService

TEMPLATE_ROOT = Path(__file__).resolve().parent / "templates"


def build_engine(settings: WebSettings) -> Engine:
    """N-53's pool, from four numbers read once and validated before they are used.

    `canonical_settings` is what makes "validated" mean the values *these* four
    arguments carry (2026-08-15, I-10). `settings.database_pool` may be a
    subclass whose attributes answer differently on a second read, so reading it
    into an ordinary `DatabasePoolSettings` first — one read per field, checked
    by that constructor — is what stops an out-of-register pool size or
    statement timeout reaching SQLAlchemy at all.
    """
    pool = canonical_settings(settings.database_pool, DatabasePoolSettings)
    return create_engine(
        settings.database.url,
        pool_size=pool.pool_size,
        max_overflow=pool.max_overflow,
        pool_timeout=pool.pool_timeout_seconds,
        pool_pre_ping=True,
        connect_args={
            # Bounded at the server, not only in the client's intention: a query
            # that outlives this is cancelled by PostgreSQL whatever the
            # application is doing.
            "options": f"-c statement_timeout={pool.statement_timeout_ms}"
        },
    )


@dataclass(frozen=True, slots=True)
class RequestServices:
    """Every service, bound to one connection and therefore to one transaction."""

    accounts: AccountRepository
    sessions_repository: SessionRepository
    transactions: OAuthTransactionRepository
    tokens: TokenGrantRepository
    credentials: WebAuthnRepository
    grants: RecoveryGrantRepository
    mappings: RoleMappingRepository
    membership: MembershipProjectionRepository
    audit: WebAuditRepository
    rate_limiter: RateLimiter
    session_service: SessionService
    oauth: OAuthLoginService
    break_glass: BreakGlassService
    role_mappings: RoleMappingService


class WebComposition:
    """Holds the process-lifetime objects and builds the per-request ones."""

    __slots__ = (
        "settings",
        "engine",
        "provider",
        "envelope",
        "startup_warnings",
        "_owns_engine",
    )

    def __init__(
        self,
        *,
        settings: WebSettings,
        engine: Engine | None = None,
        provider=None,
    ) -> None:
        self.settings = settings
        self._owns_engine = engine is None
        self.engine = engine or build_engine(settings)
        self.envelope = Envelope(settings.encryption)
        # There is deliberately **no session policy held here** (2026-08-15,
        # idle-policy-construction remediation). A composition-level policy was
        # this root's answer to "the repository and the service must agree", and
        # it worked only because both construction sites remembered to pass the
        # same object. `SessionRepository` now derives the bounds itself and
        # `SessionService` reads them from it, so agreement is structural and a
        # copy held here would be a second authority with nothing to enforce it.
        # The configuration those bounds come from is `settings.session`, which
        # `WebSettings.from_environment` has already validated against the
        # accepted register — so an out-of-register value still refuses at
        # startup, one layer earlier than before.
        self.provider = provider if provider is not None else self._default_provider()
        #: Conditions that are refusals in production and warnings elsewhere
        #: (S-15). Held so an operator can see them and a test can assert
        #: that a development host reports rather than swallows them.
        self.startup_warnings: tuple = ()

    def _default_provider(self):
        from adapters.web.discord_provider import DiscordIdentityProvider

        return DiscordIdentityProvider(self.settings.discord)

    def services(self, connection) -> RequestServices:
        settings = self.settings
        accounts = AccountRepository(connection)
        #: The **one** owner of session bounds in this graph. It derives them
        #: from `settings.session` — N-06's, N-07's, N-15's and N-66's numbers
        #: stay in configuration, the adapter holds no duration of its own, and
        #: which window a method gets is the explicit classification table in
        #: `application/web/capabilities.py`. The session service below takes its
        #: bounds from this object rather than being given a second set.
        session_repository = SessionRepository(connection, settings=settings.session)
        transactions = OAuthTransactionRepository(connection)
        tokens = TokenGrantRepository(connection)
        credentials = WebAuthnRepository(connection)
        grants = RecoveryGrantRepository(connection)
        mappings = RoleMappingRepository(connection)
        membership = MembershipProjectionRepository(connection)
        audit = WebAuditRepository(connection)
        rate_limiter = RateLimiter(
            RateLimitRepository(connection),
            settings.rate_limits,
            settings.client_digest_key,
        )
        session_service = SessionService(
            sessions=session_repository, token_grants=tokens, audit=audit
        )
        return RequestServices(
            accounts=accounts,
            sessions_repository=session_repository,
            transactions=transactions,
            tokens=tokens,
            credentials=credentials,
            grants=grants,
            mappings=mappings,
            membership=membership,
            audit=audit,
            rate_limiter=rate_limiter,
            session_service=session_service,
            oauth=OAuthLoginService(
                transactions=transactions,
                accounts=accounts,
                token_grants=tokens,
                role_mappings=mappings,
                membership=membership,
                session_service=session_service,
                audit=audit,
                envelope=self.envelope,
                settings=settings,
            ),
            break_glass=BreakGlassService(
                accounts=accounts,
                webauthn_repository=credentials,
                recovery_grants=grants,
                session_service=session_service,
                audit=audit,
                settings=settings,
            ),
            role_mappings=RoleMappingService(role_mappings=mappings, audit=audit),
        )

    async def aclose(self) -> None:
        closer = getattr(self.provider, "aclose", None)
        if closer is not None:
            await closer()
        if self._owns_engine:
            self.engine.dispose()


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


__all__ = [
    "RequestServices",
    "TEMPLATE_ROOT",
    "WebComposition",
    "build_engine",
    "utcnow",
]
