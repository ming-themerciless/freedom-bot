"""One canonical settings graph per web process — validated once, used everywhere.

The defect these cases exist for is the fifth form of one shape: **validate one
value or graph, then use another** (RAID I-09/I-10). The previous correction made
each settings type valid by construction and made selected consumers rebuild the
*one* nested object they used. It stopped one level too early:

1. `WebComposition.__init__()` stored the caller's outer `WebSettings` unchanged;
2. `services()` read `settings.session` for `SessionRepository`, whose derivation
   validated the five lifetime numbers it read;
3. the same method handed the **whole** caller object to `OAuthLoginService` and
   `BreakGlassService`;
4. those services kept it and later re-read
   `self._settings.session.oauth_transaction_minutes` while creating OAuth
   transactions and WebAuthn challenges, and `self._settings.encryption
   .active_version` while sealing a PKCE verifier; and
5. `create_app()` kept its own `settings` argument in `app.state.settings` and
   read it for startup checks, cookies, middleware, digests and every request
   helper, while separately accepting a `composition` built from something else.

So a genuine subclass — of `WebSettings`, or of any settings object below it —
could answer the accepted value to every construction gate and a different value
to the read that was actually used; and a caller could pass `settings_a` beside a
composition built from `settings_b` and get an application whose middleware,
cookies and digests used A while every service used B. Neither needs private
mutation, `object.__new__`, raw SQL or an unsupported API.

**And it stopped one boundary short of the provider** (2026-08-16, re-review
finding 1). `WebComposition` canonicalised its graph and then accepted a
ready-made `provider` beside it, requiring no relationship between the two: a
genuine `DiscordIdentityProvider` built from a valid graph B — B's client id,
client secret, redirect URI, scopes, guild id, endpoints and timeout — could be
handed to a composition built from graph A, and R-03's authorization URL and
R-04's token exchange would then use configuration the process never validated.
Section 7 is that finding; the seam is now a test-adapter seam that refuses a
real Discord provider, and the production adapter is built from the composition's
own `settings.discord`.

## How the cases are written

Every subclass here is **genuine**: it inherits the real `__post_init__` and is
built through the ordinary constructor, so the object exists only because the
accepted register let it. None of them overrides validation — a subclass that
skipped the gate would demonstrate a weaker defect than the one recorded.

They lie by **phase**, and the phase is recorded on every read (corrected
2026-08-16, re-review finding 2). A hostile object is constructed while it still
answers the accepted stored value — the earlier version of this module engaged
the lie *before* calling the genuine constructor, so the inherited
`__post_init__` saw the hostile value and refused during test-object
construction, and ten cases never reached `canonical_web_settings` or
`WebComposition` at all. What they proved was that a settings constructor
refuses, which was already proved elsewhere; what they claimed to prove was that
the *canonicalisation boundary* refuses. So construction reads, truthful reads
and lying reads are counted separately here, and a case asserts which phase the
production boundary read in — the question is not "how many times was this read"
but "was the value that reached a control the value that was checked".

Assertions are behavioural. Where a private attribute is inspected it is to
establish identity or base type *beside* a behaviour assertion, never instead of
one.
"""
from __future__ import annotations

import ast
import inspect
import re
import types
from contextlib import contextmanager
from dataclasses import dataclass, field, fields, is_dataclass, replace
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Union, get_args, get_origin, get_type_hints
from urllib.parse import parse_qsl, quote, urlsplit

import httpx
import pytest
from sqlalchemy import create_engine as sqlalchemy_create_engine, func, select
from sqlalchemy.exc import IntegrityError

from adapters.database.safety import UnsafeDatabaseTargetError
from adapters.database.tables import oauth_transactions, webauthn_challenges
from adapters.web import app as app_module
from adapters.web import composition as composition_module
from adapters.web import repositories as repositories_module
from adapters.web.app import create_app
from adapters.web.composition import WebComposition
from adapters.web.discord_provider import DiscordIdentityProvider
from adapters.web.middleware import ClientAddressPolicy
from application.web.breakglass import BreakGlassService
from application.web.config import (
    CANONICAL_SETTINGS_GRAPH,
    ConfigurationError,
    DiscordProviderSettings,
    EncryptionKey,
    SecretKey,
    SessionSettings,
    SettingsAuthorityError,
    WebSettings,
    canonical_settings,
    canonical_web_settings,
    require_canonical_web_settings,
)
from application.web.crypto import keyed_digest
from application.web.oauth import OAuthLoginService
from tests.web.composition_harness import (
    SubstitutedComposition,
    substituted_composition,
)
from tests.web.lifespan import application_lifespan
from tests.web_fixtures import (
    PUBLIC_ORIGIN,
    FakeDiscordProvider,
    web_environment,
    web_settings,
)

pytestmark = pytest.mark.database

# ---------------------------------------------------------------------------
# 0. One clock per operation, because the rows carry two authorities
# ---------------------------------------------------------------------------
#
# (2026-08-16, P3.G1 clock re-review.) Two constants have stood here and both
# were the same mistake. `datetime(2026, 8, 16, 12, 0, …)` made every case that
# wrote a row fail from noon on the day it was written. Replacing it with
# `datetime.now(timezone.utc)` evaluated at **module import** only postponed that
# failure: it is still an instant captured somewhere the operation is not, and
# collection, an earlier case, a debugger pause or a slow worker are all it takes
# to put it further in the past than the lifetime being tested.
#
# The rows these cases write stamp `created_at` from two authorities, and neither
# of them is this module:
#
# * `oauth_transactions.created_at` is **supplied by the repository**, from
#   `adapters.web.repositories.utcnow()`, read while the INSERT is built; and
# * `webauthn_challenges.created_at` is not supplied at all, so its
#   `server_default=func.now()` is stamped by **PostgreSQL**, from the database
#   server's clock, at the transaction's timestamp.
#
# `expires_at` is derived by the service from the `now` its caller injects, and
# `ck_oauth_transactions_expiry_after_creation` and
# `ck_webauthn_challenges_expiry_after_creation` compare the two. So a case that
# injects an instant captured anywhere but inside the operation has **two
# clocks**, and whether its row is legal depends on how much wall time passed
# between the two readings. That is not a slow test; it is a test whose subject
# is settings authority and whose result is a stopwatch.
#
# `OperationClock` removes the second clock rather than widening the gap between
# them. It reads `now()` from inside the operation's own transaction — where it
# is, by definition, the exact instant PostgreSQL will stamp `created_at` with,
# because `now()` is the transaction timestamp and is fixed for the transaction —
# and binds the repository's `utcnow` to that same reading. Every timestamp the
# operation persists and every expiry it derives then come from one reading;
# `expires_at - created_at` is exactly the configured lifetime; and no quantity
# of elapsed wall time before the test changes either.
#
# Nothing sleeps, no lifetime is extended, no constraint is relaxed or mocked,
# PostgreSQL still stamps the WebAuthn row itself, and no instant is captured at
# module or session scope — the fixture below is function-scoped and the reading
# happens inside the transaction under test.


class OperationClock:
    """The one clock authority for an operation and every row it writes.

    `begin()` yields the operation's transaction and its instant. Inject that
    instant as `now`, and `created_at` **is** it: for the repository-stamped row
    because `utcnow` is bound to it, and for the database-stamped row because
    `now()` does not move within a transaction.
    """

    __slots__ = ("_engine", "_monkeypatch", "_readings")

    def __init__(self, engine, monkeypatch) -> None:
        self._engine = engine
        self._monkeypatch = monkeypatch
        self._readings: list[datetime] = []

    @contextmanager
    def begin(self):
        """Open the operation's transaction and answer `(connection, now)`."""
        with self._engine.begin() as connection:
            reading = connection.execute(select(func.now())).scalar_one()
            now = reading.astimezone(timezone.utc)
            # Bound, not read: calling `utcnow()` here would produce a *third*
            # instant, which is the defect in miniature. Undone by `monkeypatch`
            # when the test ends.
            self._monkeypatch.setattr(repositories_module, "utcnow", lambda: now)
            self._readings.append(now)
            yield connection, now

    @property
    def readings(self) -> tuple[datetime, ...]:
        """Every instant this clock has issued, in order."""
        return tuple(self._readings)


@pytest.fixture()
def operation_clock(migrated_database, monkeypatch) -> OperationClock:
    """Function-scoped, deliberately: an operation's clock is not a module's."""
    return OperationClock(migrated_database, monkeypatch)


def test_persisted_rows_carry_one_clock_from_creation_to_expiry(
    settings, composition, migrated_database, operation_clock
):
    """The two-clock defect, discriminated at the rows themselves.

    Both affected tables are written in one operation and each row is then asked
    the only question that tells one clock from two: **is `expires_at` exactly
    the configured lifetime after this row's own `created_at`?**

    Under the import-time model it is not, and cannot be. `created_at` is stamped
    when the INSERT runs; `expires_at` was derived from an instant captured when
    the module was imported; so the two are `lifetime - elapsed` apart for
    whatever elapsed in between. That quantity is never zero — import, collection
    and every earlier case happen in the gap — so this case fails against that
    model for the defect's own reason and not for a timing accident, and it does
    so without asserting anything about how fast the suite runs.
    """
    accepted = settings.session.oauth_transaction_minutes
    assert accepted == 10, "N-04's accepted lifetime, carried exactly and unchanged"
    lifetime = timedelta(minutes=accepted)

    with operation_clock.begin() as (connection, now):
        services = composition.services(connection)
        started, _state = services.oauth.start(
            provider=composition.provider,
            return_path=None,
            now=now,
            client_ip_hash=None,
        )
        options = services.break_glass.begin_assertion(now=now, client_ip_hash=None)

    # Read back on a second connection, so what is examined is durable state and
    # not the values the services happened to return.
    with migrated_database.connect() as connection:
        transaction_row = connection.execute(
            select(
                oauth_transactions.c.created_at, oauth_transactions.c.expires_at
            ).where(oauth_transactions.c.id == started.transaction_id)
        ).one()
        # `.one()` rather than a filter: the operation above wrote exactly one
        # challenge, and a second row would be a test polluting this one.
        challenge_row = connection.execute(
            select(webauthn_challenges.c.created_at, webauthn_challenges.c.expires_at)
        ).one()

    for table, (created_at, expires_at) in (
        ("oauth_transactions", transaction_row),
        ("webauthn_challenges", challenge_row),
    ):
        assert created_at == now, (
            f"{table}.created_at must be the operation's own instant. It is "
            f"{created_at} and the operation's clock read {now}, so the row was "
            "stamped by a clock the expiry was not derived from"
        )
        assert expires_at - created_at == lifetime, (
            f"{table} carries two clocks: `expires_at` is {expires_at - created_at} "
            f"after this row's own `created_at`, and N-04's lifetime is {lifetime}. "
            "An expiry derived from an instant captured outside the operation is "
            "short by however long elapsed in between, and at some elapsed time "
            "that row stops satisfying `expiry_after_creation` altogether"
        )
    assert started.expires_at == now + lifetime
    assert options.expires_at == now + lifetime


def test_an_instant_captured_before_the_operation_is_refused_by_the_database(
    composition, migrated_database
):
    """The same defect from the other side: the constraint is live, and it bites.

    An import-time clock is only ever *older* than the row it stamps, and by how
    much is wall time nobody controls. This case stands in for an arbitrarily
    long delay — a year — because `expiry_after_creation` cannot tell "a year
    late" from "eleven minutes late", and eleven minutes is one minute past
    N-04's lifetime. No sleep is needed to demonstrate what elapsed time does;
    injecting the stale instant is what elapsed time *is*.

    Nothing here is mocked, dropped or extended: this is the real check
    constraint on the guarded disposable database, which is what makes the
    coherent-clock case above a result rather than a convention. Note that
    `utcnow` is deliberately **not** bound here — the two clocks are the point.
    """
    with migrated_database.connect() as connection:
        now = connection.execute(select(func.now())).scalar_one()
    stale = now.astimezone(timezone.utc) - timedelta(days=365)

    with pytest.raises(IntegrityError, match="expiry_after_creation"):
        with migrated_database.begin() as connection:
            composition.services(connection).oauth.start(
                provider=composition.provider,
                return_path=None,
                now=stale,
                client_ip_hash=None,
            )

    with pytest.raises(IntegrityError, match="expiry_after_creation"):
        with migrated_database.begin() as connection:
            composition.services(connection).break_glass.begin_assertion(
                now=stale, client_ip_hash=None
            )


# ---------------------------------------------------------------------------
# 0.1 The guard: this module reads no clock while it is being imported
# ---------------------------------------------------------------------------
#
# (Added 2026-08-16, by the independent re-review of the correction above.) Two
# module-level constants have stood here and both were deleted by hand. Nothing
# stopped a third: a diff that restores `NOW = datetime.now(timezone.utc)` at the
# top of this file fails no case, and the reader is left to remember why it is
# wrong. The clock submission asserted that the absence was already "asked of the
# AST". It was not — this module did not import `ast` and no case parsed it — so
# this section is that assertion, written rather than the claim repeated.
#
# The invariant is about **when**, not about what. Inside a function, `datetime`,
# `timedelta` and `timezone` are read during the operation they belong to and are
# exactly what `OperationClock` and the five injected cases use. What the module
# may not do is read or construct an instant while it is being *imported*, since
# such a value is already as stale by the time any case runs as `NOW` was, and
# staleness is the defect. Import-time is wider than the module's own statement
# list: class bodies, decorator expressions, and the default arguments of the
# functions declared here all run at import too, and a constant captured in any
# of them is the same defect wearing a different hat. A lambda invoked where it is
# written — `NOW = (lambda: datetime.now(timezone.utc))()` — is one more of those
# hats, and was one this guard first missed; the finding and the correction are
# recorded in §12 of the clock-authority submission. So is that same lambda wearing
# a walrus — `NOW = (reader := lambda: datetime.now(timezone.utc))()`, whose body
# runs in that expression exactly as the unnamed one's does, and which this guard
# missed a second time; §14 records that finding and its correction. And so is that
# lambda behind a literal choice — `NOW = ((lambda: datetime.now(timezone.utc)) if
# True else (lambda: None))()`, where the source names the branch that runs and the
# guard missed it a third time; §16 records that one. What stays outside is a choice
# the source does not settle: `if flag` selects a body this module cannot know
# without resolving a name, and that is declared a limit rather than guessed at.
#
# `timedelta` and `timezone` are deliberately **not** findings. A duration and a
# fixed UTC offset are not instants, and a guard that rejected them would say
# something other than what it means.

#: Names that read or construct an instant. Matched as a bare name or as the last
#: component of a dotted reference, so `datetime.now(...)`, `dt.datetime.utcnow()`,
#: `func.now()` (PostgreSQL's clock) and a bare `utcnow()` imported from the
#: repositories module are all the same finding.
INSTANT_SOURCES = frozenset(
    {
        "clock",
        "combine",
        "date",
        "datetime",
        "fromisoformat",
        "fromtimestamp",
        "monotonic",
        "monotonic_ns",
        "now",
        "perf_counter",
        "time",
        "time_ns",
        "today",
        "utcfromtimestamp",
        "utcnow",
    }
)


def _literal_selection(conditional: ast.IfExp) -> ast.expr | None:
    """The branch a conditional expression runs, when its test is a boolean literal.

    `A if True else B` evaluates `A` and never evaluates `B`; `A if False else B`
    does the reverse. Nothing has to be resolved to know that — the test *is* the
    answer, written where it stands — so the selection is decidable from this one
    node exactly as `(lambda: ...)()` is (added 2026-08-16 by independent
    re-review; §16 of the clock-authority submission).

    The test must be an **exact** boolean literal. `test.value is True` is identity
    and not equality on purpose: `1`, `1.0`, `"yes"`, a non-empty tuple and `None`
    are all constants with a settled truth value, and none of them is answered
    here. Deciding those is constant folding, and a name, a comparison or a boolean
    operator is the data-flow analysis this guard does not attempt. Every one of
    them answers `None`, which leaves the conditional exactly where it was.
    """
    test = conditional.test
    if not isinstance(test, ast.Constant):
        return None
    if test.value is True:
        return conditional.body
    if test.value is False:
        return conditional.orelse
    return None


def _invoked_lambda(callable_expression: ast.expr) -> ast.Lambda | None:
    """The lambda a call in this callable position runs, when the source says so.

    Parentheses leave no trace in the AST, so `(lambda: ...)()` is simply a `Call`
    whose callable **is** the `Lambda`: the lambda is invoked where it is written,
    and its body therefore runs whenever the call does. Currying is the same fact
    once more — in `(lambda: lambda: ...)()()` the outer call yields the inner
    lambda and the second call runs it, both while the enclosing expression is
    being evaluated.

    A named expression is looked **through** (added 2026-08-16 by independent
    re-review, which found `NOW = (reader := lambda: datetime.now(timezone.utc))()`
    reported clean). `(reader := L)` evaluates `L`, binds it, and answers *that
    same object* to the call in the very same expression, so the lambda is still
    invoked where it is written and recognising it needs no knowledge of where the
    name went. The walrus is the only wrapper unwrapped here, and the boundary is
    exact rather than a first instance of a class: it is the only expression in the
    grammar that yields its single operand, evaluated at that point, with no
    selection and no lookup. A **selection** — `(f if flag else g)()` — is read only
    when its test is an exact boolean literal (corrected 2026-08-16 by the next
    independent re-review, which found `((lambda: datetime.now(timezone.utc)) if
    True else (lambda: None))()` reported clean; §16). `if True` and `if False` name
    the branch that runs in the source itself, so the selection is decidable from
    this one node and neither data flow nor a set of possible bodies is involved.
    Any other test — a name, a comparison, a boolean operator, or a constant that is
    merely truthy — is **not** unwrapped, because then the source genuinely does not
    say which body runs and answering would mean reporting a body that may not
    execute. `ast.BoolOp` is not unwrapped at all, for that same reason. A name, an
    attribute, a subscript, a container or an argument is not unwrapped either,
    because reaching the lambda through one means resolving where a *separately
    stored* value came from. That is the interprocedural analysis this guard
    deliberately does not attempt. Both limits are recorded in §10.6/§12.7/§14.7 of
    the clock-authority submission rather than implied.

    Unwrapping decides only *whether a body runs*. The named expression's target is
    ordinary import-time code and is still walked by the visitor, so a target that
    is itself one of `INSTANT_SOURCES` remains a finding.
    """
    if isinstance(callable_expression, ast.NamedExpr):
        return _invoked_lambda(callable_expression.value)
    if isinstance(callable_expression, ast.IfExp):
        selected = _literal_selection(callable_expression)
        return None if selected is None else _invoked_lambda(selected)
    if isinstance(callable_expression, ast.Lambda):
        return callable_expression
    if isinstance(callable_expression, ast.Call):
        inner = _invoked_lambda(callable_expression.func)
        if inner is not None and isinstance(inner.body, ast.Lambda):
            return inner.body
    return None


class _ImportTimeClocks(ast.NodeVisitor):
    """Every reference to an instant in code that runs when the module is imported.

    What it descends into is the whole definition of the invariant, so it is
    listed rather than left to the reader:

    * **imports** are skipped — importing `datetime` is not reading a clock, and
      this module must go on importing it;
    * **function and method bodies** are skipped, because they run when a case
      calls them; but their **decorators** and **default arguments** are visited,
      because those run at import;
    * **class bodies** are visited in full — a class body is import-time code, so
      a field default or a class attribute that captures an instant is a finding
      exactly as a module-level assignment is; and
    * **annotations** are skipped. `from __future__ import annotations` is in
      force at the top of this module, so an annotation is a string and evaluates
      nothing. Their absence from this walk is a decision, not an oversight.

    A `lambda` is treated as a function, and by **when its body runs** rather than
    by what it is (corrected 2026-08-16 by independent re-review, which found
    `NOW = (lambda: datetime.now(timezone.utc))()` reported as clean while its
    body plainly runs during the import). Its defaults always run at import and
    are always visited. Its body is visited exactly when the source shows the
    lambda being invoked where it stands — see `_invoked_lambda`, which looks
    through a named expression to see it, because `(reader := lambda: ...)()`
    invokes the lambda in the same expression that names it (corrected again
    2026-08-16 by the next independent re-review; §14 of the submission), and
    through the selected branch of a conditional whose test is an exact boolean
    literal, because `if True` and `if False` name the branch that runs in the
    source itself (corrected again 2026-08-16 by the re-review after that; §16). A
    lambda that is stored, returned or passed as an argument keeps its body
    excluded, because that body runs when something later calls it.

    A **conditional expression** is walked the way Python evaluates it — see
    `visit_IfExp`. Its test always runs and is always visited; its branches are both
    visited when the test is not a literal, and only the selected one is when it is,
    because the unselected expression is never evaluated and so captures nothing.
    """

    def __init__(self) -> None:
        self.found: list[tuple[int, str]] = []

    # -- positions that do not run at import --------------------------------

    def visit_Import(self, node: ast.Import) -> None:  # noqa: N802
        return

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:  # noqa: N802
        return

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:  # noqa: N802
        for decorator in node.decorator_list:
            self.visit(decorator)
        self._defaults(node.args)

    visit_AsyncFunctionDef = visit_FunctionDef  # noqa: N815 - the ast API's name

    def visit_Lambda(self, node: ast.Lambda) -> None:  # noqa: N802
        # Reached only where the lambda is *not* being invoked in place: stored,
        # returned, or passed. Its defaults ran during the import; its body did
        # not. The invoked case is handled by `visit_Call`, which does not route
        # back through here, so no position is visited twice.
        self._defaults(node.args)

    def visit_Call(self, node: ast.Call) -> None:  # noqa: N802
        invoked = _invoked_lambda(node.func)
        if isinstance(node.func, ast.Lambda):
            # `(lambda: datetime.now(timezone.utc))()`. The callable itself is the
            # lambda, so its defaults are visited here instead of by `visit_Lambda`.
            self._defaults(node.func.args)
        else:
            # Every other callable expression — a name, an attribute, the inner
            # call of a curried invocation, or a named expression — is import-time
            # code and is walked as such. `datetime.now(...)` is still found here,
            # by `visit_Attribute`; and a walrus is walked in full, so its target
            # is evaluated as a `Name` and the lambda it binds still reaches
            # `visit_Lambda` for its defaults. Unwrapping in `_invoked_lambda`
            # answers only *whether the body runs*; it removes nothing from this
            # walk, and the body it answers is visited exactly once, below.
            self.visit(node.func)
        if invoked is not None:
            self.visit(invoked.body)
        for child in (*node.args, *node.keywords):
            self.visit(child)

    def visit_IfExp(self, node: ast.IfExp) -> None:  # noqa: N802
        # The test always runs, so it is always walked. The branches are walked as
        # Python evaluates them: both when the test is not an exact boolean literal,
        # because either may run and the guard errs towards reporting; the selected
        # one alone when it is, because the unselected expression is not evaluated
        # at all — no lambda object is built from it and no default of one runs, so
        # a capture written there is never made. Reporting it would be a finding for
        # code that does not execute. The order is unchanged for every conditional
        # that was already walked: test, then body, then orelse.
        self.visit(node.test)
        selected = _literal_selection(node)
        for branch in (node.body, node.orelse) if selected is None else (selected,):
            self.visit(branch)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:  # noqa: N802
        for child in (*node.decorator_list, *node.bases, *node.keywords, *node.body):
            self.visit(child)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:  # noqa: N802
        self.visit(node.target)
        if node.value is not None:
            self.visit(node.value)

    def _defaults(self, arguments: ast.arguments) -> None:
        for default in (*arguments.defaults, *arguments.kw_defaults):
            if default is not None:
                self.visit(default)

    # -- the finding ---------------------------------------------------------

    def visit_Name(self, node: ast.Name) -> None:  # noqa: N802
        if node.id in INSTANT_SOURCES:
            self.found.append((node.lineno, node.id))

    def visit_Attribute(self, node: ast.Attribute) -> None:  # noqa: N802
        if node.attr in INSTANT_SOURCES:
            # Reported once: the dotted reference is one thing, and descending
            # would report `datetime.now` a second time as bare `datetime`.
            self.found.append((node.lineno, ast.unparse(node)))
            return
        self.generic_visit(node)


def import_time_clock_offenders(source: str, *, where: str) -> list[str]:
    """Every instant this source would read or construct while being imported."""
    visitor = _ImportTimeClocks()
    visitor.visit(ast.parse(source))
    return [f"{where}:{line} {reference}" for line, reference in visitor.found]


def test_this_module_captures_no_instant_while_it_is_imported():
    """TC-STRUCT-08. The deleted `NOW` cannot come back without failing a case.

    Asserted over the AST rather than by a text search, deliberately: the comments
    and docstrings in this very section discuss `datetime.now(timezone.utc)` at
    length, and a `grep` guard would be satisfied or broken by prose. What is
    parsed here is the module's own structure, so a mention costs nothing and an
    executed capture costs a failure.
    """
    module = Path(__file__).resolve()
    offenders = import_time_clock_offenders(
        module.read_text(encoding="utf-8"), where=module.name
    )
    assert offenders == [], (
        "an instant is captured while this module is imported, which is the "
        f"defect the clock remediation removed: {offenders}"
    )


def test_the_import_time_clock_guard_reports_both_forms_and_no_others():
    """The guard has teeth, and knows which side of the line each reference is on.

    Without this, the case above would pass just as happily against a detector
    that found nothing at all. Both forms the invariant claims to prohibit are
    proved detected, and everything this module legitimately does is proved
    accepted — including the fixture the correction is built on.
    """
    # 1. The form that was actually here, and the form that preceded it.
    captured = (
        "import pytest\n"
        "from datetime import datetime, timedelta, timezone\n"
        "\n"
        "NOW = datetime.now(timezone.utc).replace(microsecond=0)\n"
    )
    assert import_time_clock_offenders(captured, where="synthetic.py") == [
        "synthetic.py:4 datetime.now"
    ]

    fixed = (
        "from datetime import datetime, timezone\n"
        "\n"
        "NOW = datetime(2026, 8, 16, 12, 0, tzinfo=timezone.utc)\n"
    )
    assert import_time_clock_offenders(fixed, where="synthetic.py") == [
        "synthetic.py:3 datetime"
    ]

    # 2. Import-time is not only the module's own statements. A capture hidden in
    #    a default argument, a decorator or a class body is the same staleness.
    hidden = (
        "from datetime import datetime, timedelta, timezone\n"
        "import pytest\n"
        "\n"
        "def helper(now=datetime.now(timezone.utc)):\n"
        "    return now\n"
        "\n"
        "@pytest.mark.parametrize('instant', [datetime.utcnow()])\n"
        "def test_case(instant):\n"
        "    assert instant\n"
        "\n"
        "class Row:\n"
        "    created_at = datetime.now(timezone.utc)\n"
    )
    assert import_time_clock_offenders(hidden, where="synthetic.py") == [
        "synthetic.py:4 datetime.now",
        "synthetic.py:7 datetime.utcnow",
        "synthetic.py:12 datetime.now",
    ]

    # 3. An alias captures the function rather than the instant, and the call that
    #    makes it one is a line away. Still a finding.
    aliased = "from datetime import datetime\n\n_clock = datetime.now\n"
    assert import_time_clock_offenders(aliased, where="synthetic.py") == [
        "synthetic.py:3 datetime.now"
    ]

    # 4. What this module actually does, and must go on doing: imports, the
    #    `pytestmark` assignment, ordinary declarations, a module-level constant
    #    that is a duration rather than an instant, function-scoped datetime
    #    arithmetic, and the `OperationClock` fixture itself.
    accepted = (
        "from __future__ import annotations\n"
        "\n"
        "from contextlib import contextmanager\n"
        "from datetime import datetime, timedelta, timezone\n"
        "\n"
        "import pytest\n"
        "from sqlalchemy import func, select\n"
        "\n"
        "pytestmark = pytest.mark.database\n"
        "LIFETIME = timedelta(minutes=10)\n"
        "\n"
        "\n"
        "class OperationClock:\n"
        "    __slots__ = ('_engine', '_readings')\n"
        "\n"
        "    def __init__(self, engine) -> None:\n"
        "        self._engine = engine\n"
        "        self._readings: list[datetime] = []\n"
        "\n"
        "    @contextmanager\n"
        "    def begin(self):\n"
        "        with self._engine.begin() as connection:\n"
        "            reading = connection.execute(select(func.now())).scalar_one()\n"
        "            now = reading.astimezone(timezone.utc)\n"
        "            self._readings.append(now)\n"
        "            yield connection, now\n"
        "\n"
        "\n"
        "@pytest.fixture()\n"
        "def operation_clock(migrated_database) -> OperationClock:\n"
        "    return OperationClock(migrated_database)\n"
        "\n"
        "\n"
        "def test_expiry(operation_clock):\n"
        "    with operation_clock.begin() as (connection, now):\n"
        "        assert now + LIFETIME > datetime.now(timezone.utc)\n"
    )
    assert import_time_clock_offenders(accepted, where="synthetic.py") == []


def test_the_import_time_clock_guard_reads_an_invoked_lambda_body():
    """A lambda invoked where it is written runs at import, and is reported.

    Added 2026-08-16 by independent re-review, which read the detector rather than
    the claim and found that `visit_Lambda()` skipped every lambda body — so the
    reproducer below was reported clean while its `datetime.now` plainly executes
    during the import. The invariant said "any code that runs at import"; the
    detector said "any code that runs at import, unless a lambda is spelled around
    it". The detector was corrected to the invariant rather than the invariant
    narrowed to the detector, and this case is the proof.

    The distinction is *when the body runs*, which the source states for these
    forms: an invoked lambda's body runs now, a stored or passed lambda's body
    runs when its holder calls it, and defaults run at import either way.
    """
    # 1. The reproducer from the finding, verbatim.
    invoked = (
        "from datetime import datetime, timezone\n"
        "\n"
        "NOW = (lambda: datetime.now(timezone.utc))()\n"
    )
    assert import_time_clock_offenders(invoked, where="synthetic.py") == [
        "synthetic.py:3 datetime.now"
    ]

    # 2. Curried, and still evaluated in place: both calls happen at import, so the
    #    body the second one runs is import-time code as well.
    curried = (
        "from datetime import datetime, timezone\n"
        "\n"
        "NOW = (lambda: lambda: datetime.utcnow())()()\n"
    )
    assert import_time_clock_offenders(curried, where="synthetic.py") == [
        "synthetic.py:3 datetime.utcnow"
    ]

    # 3. One call short of the above, the inner body is *not* import-time code: the
    #    module stores a callable and something else decides when to read a clock.
    #    This is the line the correction had to keep, not move.
    returned = (
        "from datetime import datetime, timezone\n"
        "\n"
        "make_clock = (lambda: lambda: datetime.now(timezone.utc))()\n"
    )
    assert import_time_clock_offenders(returned, where="synthetic.py") == []

    # 4. Stored and passed lambdas keep their bodies excluded, exactly as before.
    #    A fixture that reads the clock when a case calls it is what this module
    #    legitimately does, and `OperationClock` is built on it.
    ordinary = (
        "import pytest\n"
        "from datetime import datetime, timezone\n"
        "\n"
        "read_now = lambda: datetime.now(timezone.utc)\n"
        "sorted_rows = sorted([], key=lambda row: datetime.now(timezone.utc))\n"
    )
    assert import_time_clock_offenders(ordinary, where="synthetic.py") == []

    # 5. Defaults are unchanged by the correction: they run at import whether the
    #    lambda is invoked in place or merely stored, and both are reported once.
    defaults = (
        "from datetime import datetime, timezone\n"
        "\n"
        "held = lambda _at=datetime.now(timezone.utc): _at\n"
        "NOW = (lambda _at=datetime.utcnow(): _at)()\n"
    )
    assert import_time_clock_offenders(defaults, where="synthetic.py") == [
        "synthetic.py:3 datetime.now",
        "synthetic.py:4 datetime.utcnow",
    ]

    # 6. An ordinary call is still walked as it was: the callable, the arguments
    #    and the keywords, each reported once and in source order.
    ordinary_call = (
        "from datetime import datetime, timezone\n"
        "\n"
        "STAMPED = str(datetime.now(timezone.utc), errors=datetime.utcnow())\n"
    )
    assert import_time_clock_offenders(ordinary_call, where="synthetic.py") == [
        "synthetic.py:3 datetime.now",
        "synthetic.py:3 datetime.utcnow",
    ]


def test_the_import_time_clock_guard_sees_through_a_named_expression():
    """A walrus around an invoked lambda does not hide its body from the guard.

    Added 2026-08-16 by the independent re-review of the correction above, which
    took that correction's own rule — *a lambda is decided by when its body runs,
    and a lambda invoked where it is written is recognisable without resolving a
    name* — and found two spellings the detector did not recognise:

        NOW = (reader := lambda: datetime.now(timezone.utc))()
        NOW = (factory := lambda: lambda: datetime.now(timezone.utc))()()

    Both bodies execute during the import. Both lambdas are invoked in the same
    expression that names them, so neither needs anything looked up: `(reader := L)`
    evaluates `L` and answers that object straight to the call beside it. The
    detector nevertheless reported both clean, because `_invoked_lambda()` knew only
    `ast.Lambda` and `ast.Call`. That is the sixth correction's gap in the seventh
    correction's clothing — a control narrower than the claim made for it — and it
    is **not** the declared limit `f = lambda: ...` then `NOW = f()`, which is two
    statements joined by a name and is still outside the guard (case 6 below).

    The helper now looks through `ast.NamedExpr` and nothing else. §14 of the
    clock-authority submission records why that boundary is exact and not merely
    the first member of an open class.
    """
    # 1. Both reproducers from the finding, verbatim, asserted together so that a
    #    regression reports both rather than stopping at the first.
    direct = (
        "from datetime import datetime, timezone\n"
        "\n"
        "NOW = (reader := lambda: datetime.now(timezone.utc))()\n"
    )
    curried = (
        "from datetime import datetime, timezone\n"
        "\n"
        "NOW = (factory := lambda: lambda: datetime.now(timezone.utc))()()\n"
    )
    assert {
        "direct": import_time_clock_offenders(direct, where="synthetic.py"),
        "curried": import_time_clock_offenders(curried, where="synthetic.py"),
    } == {
        "direct": ["synthetic.py:3 datetime.now"],
        "curried": ["synthetic.py:3 datetime.now"],
    }

    # 2. Unwrapping decides *whether the body runs* and takes nothing out of the
    #    walk. The named expression's target is import-time code like any other, so
    #    a target that is itself one of `INSTANT_SOURCES` is still reported — first,
    #    because it is evaluated first — beside the body's finding.
    named_target = (
        "from datetime import datetime, timezone\n"
        "\n"
        "NOW = (now := lambda: datetime.utcnow())()\n"
    )
    assert import_time_clock_offenders(named_target, where="synthetic.py") == [
        "synthetic.py:3 now",
        "synthetic.py:3 datetime.utcnow",
    ]

    # 3. A walrus whose value is not a lambda at all is walked exactly as before:
    #    no body is invented, and both the alias and the aliased attribute report.
    aliased_through_walrus = (
        "from datetime import datetime\n"
        "\n"
        "NOW = (clock := datetime.now)()\n"
    )
    assert import_time_clock_offenders(aliased_through_walrus, where="synthetic.py") == [
        "synthetic.py:3 clock",
        "synthetic.py:3 datetime.now",
    ]

    # 4. Defaults are unaffected: they run when the lambda object is created, which
    #    is at import whether the walrus's lambda is then invoked or merely bound.
    #    Reported once each, in source order, exactly as without the walrus.
    defaults = (
        "from datetime import datetime, timezone\n"
        "\n"
        "held = (keep := lambda _at=datetime.now(timezone.utc): _at)\n"
        "NOW = (run := lambda _at=datetime.utcnow(): _at)()\n"
    )
    assert import_time_clock_offenders(defaults, where="synthetic.py") == [
        "synthetic.py:3 datetime.now",
        "synthetic.py:4 datetime.utcnow",
    ]

    # 5. The other side of the line, unmoved. One call short of case 1 the module
    #    stores a callable, and a walrus that is never called stores one too; in
    #    both, something else decides when a clock is read.
    applied_once = (
        "from datetime import datetime, timezone\n"
        "\n"
        "make_clock = (factory := lambda: lambda: datetime.now(timezone.utc))()\n"
    )
    bound_only = (
        "from datetime import datetime, timezone\n"
        "\n"
        "read_now = (reader := lambda: datetime.now(timezone.utc))\n"
    )
    assert import_time_clock_offenders(applied_once, where="synthetic.py") == []
    assert import_time_clock_offenders(bound_only, where="synthetic.py") == []

    # 6. The negative control that says what this correction is *not*. A lambda
    #    stored in one statement and called through its name in a later one does
    #    capture an instant at import, and the guard does not see it — knowing that
    #    `read_now` still holds that lambda two statements later is name resolution,
    #    which this guard deliberately does not do. Declared as a limit (§14.7),
    #    asserted here so the limit is where the code says it is and not wherever a
    #    later reader assumes. Case 1 is decidable from one expression; this is not.
    stored_then_called = (
        "from datetime import datetime, timezone\n"
        "\n"
        "read_now = lambda: datetime.now(timezone.utc)\n"
        "NOW = read_now()\n"
    )
    assert import_time_clock_offenders(stored_then_called, where="synthetic.py") == []

    # 7. The boundary of the unwrapping, stated as a case, and **narrowed by §16**:
    #    a selection whose test is not an exact boolean literal is not unwrapped,
    #    because then the source does not say which of the two lambdas the call
    #    runs and reporting either would report a body that may not execute. A
    #    name is such a test, so this case is unchanged and still reports nothing.
    #    What it must **not** be read as saying — and did say until §16 corrected
    #    it — is that every selection is undecidable: `if True` and `if False` name
    #    their branch in the source, and those are reported. See
    #    `test_the_import_time_clock_guard_selects_a_literal_conditional_branch`.
    selected = (
        "from datetime import datetime, timezone\n"
        "\n"
        "PREFER_UTC = True\n"
        "NOW = ((lambda: datetime.now(timezone.utc))"
        " if PREFER_UTC else (lambda: None))()\n"
    )
    assert import_time_clock_offenders(selected, where="synthetic.py") == []

    # 8. A named expression outside a callable position is untouched by any of
    #    this: it is walked, and the instant inside it is found, as it always was.
    non_callable = (
        "from datetime import datetime, timezone\n"
        "\n"
        "if (stamp := datetime.now(timezone.utc)) is not None:\n"
        "    STAMPED = stamp\n"
    )
    assert import_time_clock_offenders(non_callable, where="synthetic.py") == [
        "synthetic.py:3 datetime.now"
    ]


def test_the_import_time_clock_guard_selects_a_literal_conditional_branch():
    """`if True` and `if False` say which lambda runs, so the guard reads it.

    Added 2026-08-16 by the independent re-review of the correction above. That
    correction looked through `ast.NamedExpr` correctly, but the boundary it
    claimed for conditional expressions was false: it said a selection in callable
    position *cannot* be unwrapped because the source does not say which lambda
    runs, and that closing it would need data flow or a set-valued analysis. That
    is true of `if flag`. It is not true of `if True`:

        NOW = ((lambda: datetime.now(timezone.utc)) if True else (lambda: None))()

    This captures an instant at import — confirmed by executing it, not by reading
    the grammar — and the AST says exactly which lambda runs. No name is resolved,
    no value is looked up, and no set of possible bodies is needed. The detector
    returned `[]`, because `_invoked_lambda()` did not handle `ast.IfExp` at all;
    and the existing control used a *name* as its test, so it never exercised the
    broader claim made for every selection. §16 of the clock-authority submission
    records the finding, the correction, and the limit that genuinely remains.
    """
    # 1. Both reproducers, asserted together so a regression reports both rather
    #    than stopping at the first. `True` selects the body, `False` the orelse;
    #    the clock is in the selected branch in each.
    literal_true = (
        "from datetime import datetime, timezone\n"
        "\n"
        "NOW = ((lambda: datetime.now(timezone.utc)) if True else (lambda: None))()\n"
    )
    literal_false = (
        "from datetime import datetime, timezone\n"
        "\n"
        "NOW = ((lambda: None) if False else (lambda: datetime.utcnow()))()\n"
    )
    assert {
        "true": import_time_clock_offenders(literal_true, where="synthetic.py"),
        "false": import_time_clock_offenders(literal_false, where="synthetic.py"),
    } == {
        "true": ["synthetic.py:3 datetime.now"],
        "false": ["synthetic.py:3 datetime.utcnow"],
    }

    # 2. A clock in *each* selectable branch. Exactly one of them runs, and it is
    #    the one reported — the dead branch is not evaluated by Python and is not
    #    walked here, so it is neither reported nor silently swept in beside it.
    both_branches = (
        "from datetime import datetime, timezone\n"
        "\n"
        "NOW = ((lambda: datetime.now(timezone.utc))"
        " if {test} else (lambda: datetime.utcnow()))()\n"
    )
    assert import_time_clock_offenders(
        both_branches.format(test="True"), where="synthetic.py"
    ) == ["synthetic.py:3 datetime.now"]
    assert import_time_clock_offenders(
        both_branches.format(test="False"), where="synthetic.py"
    ) == ["synthetic.py:3 datetime.utcnow"]

    # 3. The dead branch proved dead, at the one position where it would otherwise
    #    still report: a lambda's **defaults** run when the lambda object is built,
    #    and the unselected expression never builds one. The selected branch's
    #    defaults do run, and are reported exactly as they always were.
    dead_defaults = (
        "from datetime import datetime, timezone\n"
        "\n"
        "NOW = ((lambda _at=datetime.now(timezone.utc): _at)"
        " if False else (lambda: None))()\n"
    )
    live_defaults = (
        "from datetime import datetime, timezone\n"
        "\n"
        "NOW = ((lambda _at=datetime.utcnow(): _at) if True else (lambda: None))()\n"
    )
    assert import_time_clock_offenders(dead_defaults, where="synthetic.py") == []
    assert import_time_clock_offenders(live_defaults, where="synthetic.py") == [
        "synthetic.py:3 datetime.utcnow"
    ]

    # 4. The test itself is ordinary import-time code and is walked as such — it
    #    runs whichever branch is selected. A clock in the condition is therefore a
    #    finding, and here it is the *only* one: the test is not a boolean literal,
    #    so nothing is unwrapped and the stored lambdas keep their bodies excluded.
    clock_in_condition = (
        "from datetime import datetime, timezone\n"
        "\n"
        "NOW = ((lambda: datetime.now(timezone.utc))"
        " if datetime.utcnow() else (lambda: None))()\n"
    )
    assert import_time_clock_offenders(clock_in_condition, where="synthetic.py") == [
        "synthetic.py:3 datetime.utcnow"
    ]

    # 5. The selection composes with both earlier corrections rather than being a
    #    special case beside them: curried through a literal branch, and a walrus
    #    inside one. Same recursion, same single report.
    curried = (
        "from datetime import datetime, timezone\n"
        "\n"
        "NOW = ((lambda: lambda: datetime.now(timezone.utc))"
        " if True else (lambda: None))()()\n"
    )
    walrus_inside = (
        "from datetime import datetime, timezone\n"
        "\n"
        "NOW = ((reader := lambda: datetime.now(timezone.utc))"
        " if True else (lambda: None))()\n"
    )
    assert import_time_clock_offenders(curried, where="synthetic.py") == [
        "synthetic.py:3 datetime.now"
    ]
    assert import_time_clock_offenders(walrus_inside, where="synthetic.py") == [
        "synthetic.py:3 datetime.now"
    ]

    # 6. The limit, and it is identity rather than truthiness. Every test below has
    #    a settled value that a constant folder or an evaluator would resolve, and
    #    none of them is an exact boolean literal, so none is unwrapped. Deciding
    #    them is the constant folding, symbol resolution and control-flow analysis
    #    this guard deliberately does not do. `1 == 1` and `or` are here for the
    #    same reason: they are decidable to a reader and not to this detector.
    for test in ("1", "1.0", "'yes'", "(0,)", "None", "1 == 1", "not False"):
        truthy = (
            "from datetime import datetime, timezone\n"
            "\n"
            f"NOW = ((lambda: datetime.now(timezone.utc)) if {test} else (lambda: None))()\n"
        )
        assert import_time_clock_offenders(truthy, where="synthetic.py") == [], (
            f"`if {test}` is not an exact boolean literal and must not be unwrapped"
        )
    boolop = (
        "from datetime import datetime, timezone\n"
        "\n"
        "NOW = ((lambda: datetime.now(timezone.utc)) or (lambda: None))()\n"
    )
    assert import_time_clock_offenders(boolop, where="synthetic.py") == []

    # 7. A literal selection outside a callable position is walked by the same
    #    rule, because it is the same fact about evaluation: the selected
    #    expression runs and the other does not. This removes a report the previous
    #    detector made for code that never executes; it narrows no invariant,
    #    because no instant is captured by an expression Python does not evaluate.
    selected_value = (
        "from datetime import datetime, timezone\n"
        "\n"
        "NOW = datetime.now(timezone.utc) if True else None\n"
    )
    dead_value = (
        "from datetime import datetime, timezone\n"
        "\n"
        "NOW = None if True else datetime.now(timezone.utc)\n"
    )
    assert import_time_clock_offenders(selected_value, where="synthetic.py") == [
        "synthetic.py:3 datetime.now"
    ]
    assert import_time_clock_offenders(dead_value, where="synthetic.py") == []


# ---------------------------------------------------------------------------
# The lying-subclass machinery
# ---------------------------------------------------------------------------


@dataclass
class Lie:
    """One field that answers the accepted value until the lie is engaged.

    `reads` records the **phase** of every read:

    * `"construction"` — inside the genuine inherited constructor, which is where
      the accepted value is validated and where the object earns the right to
      exist at all;
    * `"truthful"` — after construction and before `engage()`, which is the phase
      a production boundary canonicalises in; and
    * `"lying"` — after `engage()`, which is every read a consumer makes of the
      caller's object once composition is over.

    Counting them separately is what lets a case assert that a consumer stopped
    consulting the caller's object entirely rather than merely happening to get
    the right number out of it, and what stops a case from mistaking a refusal
    during *its own* fixture construction for a refusal at the boundary under
    test.
    """

    field_name: str
    later_value: object
    phase: str = "construction"
    reads: list[str] = field(default_factory=list)

    def reads_in(self, phase: str) -> int:
        return self.reads.count(phase)

    @property
    def construction_reads(self) -> int:
        return self.reads_in("construction")

    @property
    def truthful_reads(self) -> int:
        return self.reads_in("truthful")

    @property
    def lying_reads(self) -> int:
        return self.reads_in("lying")

    def engage(self) -> "Lie":
        """Start lying. Called after construction, immediately before the boundary."""
        assert self.phase == "truthful", (
            "a lie is engaged once, after the hostile object has been "
            f"constructed truthfully. Phase: {self.phase!r}"
        )
        self.phase = "lying"
        return self


def lying(instance, lie: Lie):
    """A genuine subclass of `type(instance)` that answers `lie` for one field.

    Inherited construction runs **while the object still tells the truth**, so it
    observes the stored, accepted value and the returned object is one the
    register let exist. `__post_init__` is deliberately not overridden, and where
    the base defines one this asserts the subclass inherited it rather than
    shadowing it. `WebSettings` has none — it is a plain frozen dataclass whose
    members validate themselves — so its absence is accepted rather than asserted
    away.

    The lie is *not* engaged here. The caller engages it immediately before
    invoking the production boundary under test, which is the boundary the
    finding is about.
    """
    assert lie.phase == "construction", (
        "build the hostile object before engaging its lie, so the inherited "
        f"constructor validates the accepted value. Phase: {lie.phase!r}"
    )
    base = type(instance)

    class Lying(base):  # type: ignore[misc, valid-type]
        __slots__ = ()

        def __getattribute__(self, name: str):
            if name == lie.field_name:
                lie.reads.append(lie.phase)
                if lie.phase == "lying":
                    return lie.later_value
            return super().__getattribute__(name)

    built = Lying(**{f.name: getattr(instance, f.name) for f in fields(base)})
    inherited = getattr(base, "__post_init__", None)
    if inherited is not None:
        assert type(built).__post_init__ is inherited, (
            "the subclass must inherit construction validation, not bypass it"
        )
    lie.phase = "truthful"
    return built


def graph_with(settings: WebSettings, **members) -> WebSettings:
    """The caller's graph with one member replaced by a lying subclass of it.

    `dataclasses.replace` is used **only here**, on a base `WebSettings`, to build
    the hostile input. Production code never uses it to canonicalise: `replace()`
    preserves the type it is given, so on a subclass it would return the subclass
    and canonicalise nothing.
    """
    return replace(settings, **members)


def foreign_graph(tmp_path: Path, **overrides: str) -> WebSettings:
    """A second, complete, individually valid settings graph.

    Every case that needs "two authorities" needs both of them to be
    configurations a process would accept — a refusal that only catches an
    invalid second graph would catch nothing the register does not already.
    """
    return web_settings(tmp_path, **overrides)


# ---------------------------------------------------------------------------
# 1. The graph itself: exact base types, one read per field
# ---------------------------------------------------------------------------


def test_every_member_of_the_canonical_graph_is_the_exact_base_type(settings):
    """Requirement 7. Not a subclass, at any depth, and equal to what was read.

    Parameterised from `CANONICAL_SETTINGS_GRAPH` rather than from a list written
    here. That the table itself is complete is section 2's question, answered
    from the dataclasses rather than from the table.
    """
    canonical = canonical_web_settings(settings)

    assert type(canonical) is WebSettings
    for name, expected in CANONICAL_SETTINGS_GRAPH[WebSettings].items():
        held = getattr(canonical, name)
        assert type(held) is expected, (
            f"{name} must be exactly {expected.__name__}, not {type(held).__name__}"
        )
        source = getattr(settings, name)
        for member in fields(expected):
            assert getattr(held, member.name) == getattr(source, member.name), (
                f"{name}.{member.name} must equal the value that was read"
            )

    # And one level further down, where the earlier correction never reached.
    assert type(canonical.discord.client_secret) is SecretKey
    assert all(type(key) is EncryptionKey for key in canonical.encryption.keys)
    assert type(canonical.encryption.keys) is tuple
    assert type(canonical.database.identity) is type(settings.database.identity)


def test_the_graph_is_rebuilt_from_exactly_one_read_of_every_field(settings):
    """Requirement 7's other half: one read, so there is one value to validate."""
    lie = Lie("max_sessions_per_account", 3)
    hostile = graph_with(settings, session=lying(settings.session, lie))
    construction_reads = lie.construction_reads
    assert construction_reads >= 1, (
        "the inherited constructor must have read and validated the field"
    )

    canonical = canonical_web_settings(hostile)

    assert lie.truthful_reads == 1, (
        f"canonicalisation must read each field exactly once. Reads: {lie.reads}"
    )
    assert lie.construction_reads == construction_reads, (
        "and must not have re-entered the constructor's phase"
    )
    assert lie.lying_reads == 0
    assert canonical.session.max_sessions_per_account == (
        settings.session.max_sessions_per_account
    )


def test_a_member_that_lies_out_of_register_refuses_before_anything_holds_it(
    settings, monkeypatch
):
    """Requirement 8. The refusal precedes the engine, the provider and the app.

    A pool size of 500 is what SQLAlchemy would have been given. The assertions
    that neither `create_engine` nor `build_provider` was called are the ones
    that matter: a refusal that happened *after* either would still have left a
    process holding a pool or an OAuth adapter nobody accepted.
    """
    engines: list = []
    providers: list = []
    monkeypatch.setattr(
        composition_module,
        "create_engine",
        lambda *args, **kwargs: engines.append((args, kwargs)),
    )
    monkeypatch.setattr(
        composition_module,
        "build_provider",
        lambda *args, **kwargs: providers.append((args, kwargs)),
    )
    lie = Lie("pool_size", 500)
    hostile = graph_with(settings, database_pool=lying(settings.database_pool, lie))
    assert lie.construction_reads >= 1, (
        "the accepted pool size was validated while the object was built"
    )
    lie.engage()

    with pytest.raises(ValueError, match="pool_size"):
        WebComposition(settings=hostile)

    assert lie.lying_reads == 1, (
        f"canonicalisation must read the hostile field exactly once: {lie.reads}"
    )
    assert engines == [], "an out-of-register pool must never reach SQLAlchemy"
    assert providers == [], "and no provider may be built from a refused graph"


@pytest.mark.parametrize(
    ("member", "field_name", "later_value"),
    [
        ("session", "idle_minutes", 1.0),
        ("session", "max_sessions_per_account", True),
        ("rate_limits", "oauth_starts_per_ip", 10_000),
        ("bounds", "max_request_bytes", 64 * 1024 * 1024),
        ("bounds", "trusted_proxy_hops", 2),
        ("worker", "lease_seconds", 1),
        ("webauthn", "recovery_grant_minutes", 1_000),
        ("database_pool", "statement_timeout_ms", 3_600_000),
    ],
)
def test_a_wrong_type_or_out_of_register_later_answer_refuses_at_canonicalisation(
    settings, member, field_name, later_value
):
    """Requirement 8, across the register. Every one of these is a control.

    The two `session` cases are the type rule rather than the range rule: an
    integral-looking `float` and a `bool` are both refused by `type(value) is
    int`, which is the accepted statement of "integer" and stays so here.

    Each hostile object is **valid at construction** — the accepted value is what
    the inherited `__post_init__` saw — so the refusal asserted below is the
    canonicalisation boundary's and not that constructor's.
    """
    lie = Lie(field_name, later_value)
    hostile = graph_with(settings, **{member: lying(getattr(settings, member), lie)})
    assert lie.construction_reads >= 1
    lie.engage()

    with pytest.raises(ValueError, match=field_name):
        canonical_web_settings(hostile)

    assert lie.lying_reads == 1, (
        f"the boundary must read the hostile field exactly once: {lie.reads}"
    )


def test_the_accepted_value_survives_when_the_same_object_is_left_truthful(settings):
    """The control for the parametrised cases above.

    The same machinery, never engaged, produces a graph canonicalisation accepts
    — so a refusal above is the lie being refused, not the harness being refused.
    """
    lie = Lie("idle_minutes", 5)
    hostile = graph_with(settings, session=lying(settings.session, lie))

    canonical = canonical_web_settings(hostile)

    assert canonical.session.idle_minutes == settings.session.idle_minutes
    assert lie.lying_reads == 0
    assert type(canonical.session) is SessionSettings


# ---------------------------------------------------------------------------
# 2. The graph declaration is complete — proved independently of itself
# ---------------------------------------------------------------------------
#
# (2026-08-16, re-review finding 3.) The completeness test this replaces
# iterated `CANONICAL_SETTINGS_GRAPH` and checked the entries it found, so a
# settings-valued field added to a dataclass and omitted from the table passed:
# the omission removed both the obligation and the check. The expected topology
# below is derived from the dataclasses' own annotations and never from the
# mapping it verifies, so an omission now fails.
#
# The declared graph remains the **runtime** authority — nothing in production
# infers structure from annotations. What is proved here is that the declaration
# says everything the dataclasses do.


class UnsupportedAnnotation(Exception):
    """An annotation outside the supported container grammar. Fails closed.

    Raised rather than guessed at: an unrecognised container holding a settings
    object would otherwise be derived as a leaf, and a leaf is exactly what an
    unclassified nested node looks like.
    """


def _holds_dataclass(annotation: object) -> bool:
    if isinstance(annotation, type):
        return is_dataclass(annotation)
    return any(_holds_dataclass(argument) for argument in get_args(annotation))


def classify_annotation(annotation: object, where: str):
    """`None` for a leaf, a type for a node, `(type,)` for a tuple of nodes.

    The whole supported grammar, written out:

    * a plain class — a node if it is a dataclass, a leaf otherwise;
    * `tuple[X, ...]` — a tuple of nodes if `X` is a dataclass, a leaf otherwise;
    * `X | None` and other unions — a leaf **only** if no member is a dataclass.

    Anything else fails closed, including a fixed-length tuple, a `list`, a
    `dict`, and an optional or unioned settings node. Those are not refusals of
    ideas that might one day be needed; they are the statement that adding one
    requires deciding what canonicalising it means, in the graph and in
    `canonical_settings`, rather than having it silently treated as a leaf here.
    """
    origin = get_origin(annotation)
    arguments = get_args(annotation)
    if origin is None:
        if not isinstance(annotation, type):
            raise UnsupportedAnnotation(
                f"{where}: {annotation!r} is not a class, so what it holds cannot "
                "be classified"
            )
        return annotation if is_dataclass(annotation) else None
    if origin in (Union, types.UnionType):
        if any(_holds_dataclass(argument) for argument in arguments):
            raise UnsupportedAnnotation(
                f"{where}: an optional or unioned settings node is not in the "
                "supported grammar — a node that may be absent has no single "
                "canonical rebuild"
            )
        return None
    if origin is tuple:
        if len(arguments) == 2 and arguments[1] is Ellipsis:
            element = arguments[0]
            if not isinstance(element, type):
                raise UnsupportedAnnotation(
                    f"{where}: tuple element {element!r} is not a class"
                )
            return (element,) if is_dataclass(element) else None
        raise UnsupportedAnnotation(
            f"{where}: only tuple[X, ...] is supported, not a fixed-length tuple"
        )
    raise UnsupportedAnnotation(
        f"{where}: {origin!r} is not a supported container"
    )


def derive_expected_graph(root: type) -> tuple[dict[type, dict[str, object]], list[str]]:
    """The graph the dataclasses themselves describe, reachable from `root`.

    Derived from `typing.get_type_hints`, which is independent of
    `CANONICAL_SETTINGS_GRAPH` in both directions: a type missing from the table
    is still walked here, and a field missing from the table is still classified.
    """
    expected: dict[type, dict[str, object]] = {}
    problems: list[str] = []
    pending = [root]
    while pending:
        node = pending.pop()
        if node in expected:
            continue
        hints = get_type_hints(node)
        nested: dict[str, object] = {}
        for member in fields(node):
            where = f"{node.__name__}.{member.name}"
            try:
                classification = classify_annotation(hints[member.name], where)
            except UnsupportedAnnotation as error:
                problems.append(str(error))
                continue
            if classification is None:
                continue
            nested[member.name] = classification
            pending.append(
                classification[0]
                if isinstance(classification, tuple)
                else classification
            )
        expected[node] = nested
    return expected, problems


def graph_problems(declared: object, *, root: type = WebSettings) -> list[str]:
    """Every way `declared` fails to state the topology `root`'s dataclasses have.

    Takes the mapping as an argument rather than reading the module constant, so
    a falsification case can hand it a deliberately damaged copy and show this
    reports the damage.
    """
    expected, problems = derive_expected_graph(root)
    for node, nested in expected.items():
        if node not in declared:  # type: ignore[operator]
            problems.append(
                f"{node.__name__} participates in the settings graph and has no "
                "entry, so nothing states which of its fields hold other "
                "settings objects"
            )
            continue
        entry = declared[node]  # type: ignore[index]
        for name, classification in nested.items():
            if name not in entry:
                problems.append(
                    f"{node.__name__}.{name} holds a settings node and is not "
                    "classified in the graph"
                )
            elif entry[name] != classification:
                problems.append(
                    f"{node.__name__}.{name} is classified as {entry[name]!r}, "
                    f"but the dataclass declares {classification!r}"
                )
        owned = {member.name for member in fields(node)}
        for name in entry:
            if name not in owned:
                problems.append(
                    f"{node.__name__}.{name} is declared in the graph and is not "
                    "a field of that dataclass"
                )
            elif name not in nested:
                problems.append(
                    f"{node.__name__}.{name} is declared as a nested settings "
                    "node and does not hold one"
                )
    for node in declared:  # type: ignore[union-attr]
        if node not in expected:
            problems.append(
                f"{node.__name__} is declared in the graph and is not reachable "
                f"from {root.__name__}"
            )
    return problems


#: A synthetic equivalent of the real graph, used only by the falsification
#: cases below. Defined at module level because `get_type_hints` resolves a
#: dataclass's annotations against its module's globals.
@dataclass(frozen=True, slots=True)
class SyntheticLeaf:
    value: int


@dataclass(frozen=True, slots=True)
class SyntheticNode:
    leaf: SyntheticLeaf
    label: str


@dataclass(frozen=True, slots=True)
class SyntheticUnsupportedContainer:
    leaves: list[SyntheticLeaf]


def test_the_declared_graph_states_the_whole_topology_the_dataclasses_have():
    """Requirement: every participating type and every nested field is declared.

    The expected topology comes from the annotations; the mapping is only ever
    the thing being checked. A settings-valued field added to a settings
    dataclass and forgotten here fails this, which is the property the previous
    version of this test did not have.
    """
    assert graph_problems(CANONICAL_SETTINGS_GRAPH) == []

    # And the derivation is not vacuous: it found the leaves as well as the
    # branches, and it found them without consulting the mapping.
    expected, unsupported = derive_expected_graph(WebSettings)
    assert unsupported == []
    assert set(expected) == set(CANONICAL_SETTINGS_GRAPH)
    assert SecretKey in expected and expected[SecretKey] == {}
    assert expected[WebSettings]["discord"] is DiscordProviderSettings


def test_deleting_one_nested_classification_makes_the_completeness_check_fail():
    """Falsification, by mutation of a copy: the check has teeth.

    `discord` is removed from `WebSettings`'s entry — the exact omission the
    previous, self-referential test could not see, because it iterated the
    entries that remained.
    """
    damaged = {
        node: dict(entry) for node, entry in CANONICAL_SETTINGS_GRAPH.items()
    }
    del damaged[WebSettings]["discord"]

    problems = graph_problems(damaged)

    assert any("WebSettings.discord" in problem for problem in problems), problems
    # The module constant itself is untouched by the falsification.
    assert graph_problems(CANONICAL_SETTINGS_GRAPH) == []


def test_deleting_a_whole_type_entry_makes_the_completeness_check_fail():
    """The other omission: a participating type with no entry at all."""
    damaged = {
        node: dict(entry)
        for node, entry in CANONICAL_SETTINGS_GRAPH.items()
        if node is not SecretKey
    }

    problems = graph_problems(damaged)

    assert any("SecretKey" in problem for problem in problems), problems


def test_an_unclassified_nested_field_in_a_synthetic_graph_is_reported():
    """The same omission in a synthetic equivalent, to prove it is not incidental."""
    complete = {SyntheticNode: {"leaf": SyntheticLeaf}, SyntheticLeaf: {}}
    assert graph_problems(complete, root=SyntheticNode) == []

    unclassified = {SyntheticNode: {}, SyntheticLeaf: {}}
    problems = graph_problems(unclassified, root=SyntheticNode)
    assert any("SyntheticNode.leaf" in problem for problem in problems), problems

    misdeclared = {
        SyntheticNode: {"leaf": SyntheticLeaf, "label": SyntheticLeaf},
        SyntheticLeaf: {},
    }
    problems = graph_problems(misdeclared, root=SyntheticNode)
    assert any("SyntheticNode.label" in problem for problem in problems), problems


def test_an_unsupported_container_fails_closed_rather_than_reading_as_a_leaf():
    """Requirement: an unknown container is a problem, never a silent leaf."""
    problems = graph_problems(
        {SyntheticUnsupportedContainer: {}, SyntheticLeaf: {}},
        root=SyntheticUnsupportedContainer,
    )
    assert any("not a supported container" in problem for problem in problems), problems

    with pytest.raises(UnsupportedAnnotation, match="fixed-length tuple"):
        classify_annotation(tuple[SyntheticLeaf, SyntheticLeaf], "synthetic")
    with pytest.raises(UnsupportedAnnotation, match="optional or unioned"):
        classify_annotation(Union[SyntheticLeaf, None], "synthetic")


def test_canonicalisation_refuses_a_settings_type_the_graph_does_not_declare():
    """The runtime half of the same rule: an unknown type fails closed.

    `canonical_settings` looked its type up with `.get(expected, {})`, so an
    undeclared settings type was canonicalised as though it nested nothing — its
    outer shell rebuilt and any overridable object left inside it. A missing
    entry is the absence of a statement, not the statement that there is nothing
    to descend into, and the two must not answer the same.
    """
    with pytest.raises(SettingsAuthorityError, match="SyntheticNode"):
        canonical_settings(SyntheticNode(leaf=SyntheticLeaf(1), label="x"), SyntheticNode)


# ---------------------------------------------------------------------------
# 3. The OAuth transaction lifetime (requirement 1)
# ---------------------------------------------------------------------------


def test_an_oauth_transaction_expires_on_the_canonical_lifetime_not_a_later_answer(
    settings, provider, migrated_database, operation_clock
):
    """Requirement 1. N-04's window, at the service that applies it.

    `SessionSettings` validates `oauth_transaction_minutes` at construction, and
    `SessionPolicy.derive()` — the repository's derivation — reads the five
    numbers that govern a *session's* lifetime and never this one. So this field
    had exactly one reader, `OAuthLoginService`, and that reader held the caller's
    graph: the value the constructor validated and the value the transaction
    expired on were two different reads of a subclass, and nothing required them
    to agree.
    """
    accepted = settings.session.oauth_transaction_minutes
    lie = Lie("oauth_transaction_minutes", 3)
    assert lie.later_value != accepted, "the case needs a value that is not N-04's"

    composition = substituted_composition(
        settings=graph_with(settings, session=lying(settings.session, lie)),
        engine=migrated_database,
        provider=provider,
    )
    assert lie.truthful_reads == 1, (
        f"composition must read the caller's field exactly once: {lie.reads}"
    )
    lie.engage()

    with operation_clock.begin() as (connection, now):
        started, _state = composition.services(connection).oauth.start(
            provider=composition.provider,
            return_path=None,
            now=now,
            client_ip_hash=None,
        )

    assert started.expires_at == now + timedelta(minutes=accepted), (
        "the transaction must expire on the value canonicalisation validated"
    )
    assert lie.lying_reads == 0, (
        "the service must not consult the caller's graph at all after "
        f"composition. Reads: {lie.reads}"
    )
    assert lie.truthful_reads == 1, "and must not have read it again"

    # Durable state, not only the returned value: the row a callback will be
    # matched against carries the same expiry.
    with migrated_database.connect() as connection:
        stored = connection.execute(
            select(oauth_transactions.c.expires_at).where(
                oauth_transactions.c.id == started.transaction_id
            )
        ).scalar_one()
    assert stored == now + timedelta(minutes=accepted)


def test_the_repository_derivation_uses_the_canonical_session_bounds(
    settings, provider, migrated_database
):
    """Requirement 1's derivation half, on a field the derivation does read.

    `idle_minutes` is N-06, compiled into the refresh statement at repository
    construction. A later answer of five minutes would be a *tighter* window and
    therefore not obviously wrong — which is the point: what is asserted is that
    the number in force is the one that was validated, whichever direction the
    lie went.
    """
    accepted = settings.session.idle_minutes
    lie = Lie("idle_minutes", 5)
    assert lie.later_value != accepted

    composition = substituted_composition(
        settings=graph_with(settings, session=lying(settings.session, lie)),
        engine=migrated_database,
        provider=provider,
    )
    lie.engage()

    with migrated_database.connect() as connection:
        services = composition.services(connection)
        policy = services.sessions_repository.policy
        assert policy.ordinary_idle == timedelta(minutes=accepted)
        # The service takes its bounds from the repository, so one authority
        # here is one authority there.
        assert services.session_service.policy is policy

    assert lie.lying_reads == 0, lie.reads


# ---------------------------------------------------------------------------
# 4. The break-glass challenge lifetime (requirement 2)
# ---------------------------------------------------------------------------


def test_a_webauthn_challenge_expires_on_the_canonical_lifetime(
    settings, provider, migrated_database, operation_clock
):
    """Requirement 2. The same field, the other service, the emergency route.

    A challenge that outlives its accepted window is a replayable assertion on
    the one authentication path that exists because Discord is down.
    """
    accepted = settings.session.oauth_transaction_minutes
    lie = Lie("oauth_transaction_minutes", 240)

    composition = substituted_composition(
        settings=graph_with(settings, session=lying(settings.session, lie)),
        engine=migrated_database,
        provider=provider,
    )
    lie.engage()

    with operation_clock.begin() as (connection, now):
        options = composition.services(connection).break_glass.begin_assertion(
            now=now, client_ip_hash=None
        )

    assert options.expires_at == now + timedelta(minutes=accepted)
    assert lie.lying_reads == 0, lie.reads


def test_the_relying_party_a_challenge_is_scoped_to_is_the_canonical_one(
    settings, provider, migrated_database, operation_clock
):
    """Requirement 2, at the value that decides which credentials may answer."""
    lie = Lie("rp_id", "elsewhere.test")
    composition = substituted_composition(
        settings=graph_with(settings, webauthn=lying(settings.webauthn, lie)),
        engine=migrated_database,
        provider=provider,
    )
    lie.engage()

    with operation_clock.begin() as (connection, now):
        options = composition.services(connection).break_glass.begin_assertion(
            now=now, client_ip_hash=None
        )

    assert options.payload["rpId"] == settings.webauthn.rp_id
    assert lie.lying_reads == 0, lie.reads


# ---------------------------------------------------------------------------
# 5. An outer subclass that swaps which nested object it returns (requirement 3)
# ---------------------------------------------------------------------------


def test_the_composition_snapshots_the_nested_settings_object_exactly_once(
    settings, provider, migrated_database, operation_clock
):
    """Requirement 3. The outer graph answers a **different object** per read.

    This is the shape a per-field lie cannot express: every `SessionSettings` in
    play is a genuine, in-register, fully valid instance, and the subclass simply
    hands out a different one after the first read. Under retain-and-re-read that
    made the repository's derivation and the OAuth service's expiry come from two
    unrelated objects, both individually valid.
    """
    other = replace(settings.session, idle_minutes=5, oauth_transaction_minutes=2)
    assert other != settings.session
    reads: list[str] = []

    class SwappingSettings(WebSettings):
        __slots__ = ()

        def __getattribute__(self, name: str):
            if name == "session":
                reads.append(name)
                if len(reads) > 1:
                    return other
            return super().__getattribute__(name)

    hostile = SwappingSettings(
        **{f.name: getattr(settings, f.name) for f in fields(WebSettings)}
    )
    composition = substituted_composition(
        settings=hostile, engine=migrated_database, provider=provider
    )

    assert len(reads) == 1, f"the graph must be read once, not per consumer: {reads}"
    held = composition.settings.session
    assert type(held) is SessionSettings
    assert held == settings.session, "the first — and only — read is what is used"

    with operation_clock.begin() as (connection, now):
        services = composition.services(connection)
        assert services.sessions_repository.policy.ordinary_idle == timedelta(
            minutes=settings.session.idle_minutes
        )
        started, _state = services.oauth.start(
            provider=composition.provider,
            return_path=None,
            now=now,
            client_ip_hash=None,
        )
        # Every consumer holds the same exact-base object, asserted by identity
        # beside the two behaviours above rather than instead of them.
        assert services.oauth._settings.session is held  # noqa: SLF001
        assert services.break_glass._settings.session is held  # noqa: SLF001

    assert started.expires_at == now + timedelta(
        minutes=settings.session.oauth_transaction_minutes
    )
    assert len(reads) == 1, f"and never read again: {reads}"


# ---------------------------------------------------------------------------
# 6. `create_app` has exactly one authority (requirements 4 and 5)
# ---------------------------------------------------------------------------


def test_create_app_refuses_two_configuration_authorities(
    settings, composition, tmp_path
):
    """Requirement 4. Materially different, safe, synthetic settings.

    The two graphs differ in the session idle window, the body bound and the
    Discord client id — every one of which is a control the factory installs from
    `settings` while the services come from `composition`. The refusal is typed
    and names no configured value.
    """
    other = foreign_graph(
        tmp_path,
        WEB_MAX_REQUEST_BYTES="4096",
        WEB_SESSION_IDLE_MINUTES="7",
        WEB_DISCORD_CLIENT_ID="9990000001",
    )
    assert other.session.idle_minutes != composition.settings.session.idle_minutes
    assert (
        other.bounds.max_request_bytes != composition.settings.bounds.max_request_bytes
    )
    assert other.discord.client_id != composition.settings.discord.client_id

    with pytest.raises(SettingsAuthorityError) as refusal:
        create_app(other, composition=composition, run_startup_checks=False)

    rendered = str(refusal.value)
    assert "exactly one configuration authority" in rendered
    for secret in (
        other.session.cookie_name,
        str(other.bounds.max_request_bytes),
        other.public_origin,
        other.database.url,
        other.discord.client_id,
    ):
        assert secret not in rendered, "the refusal must echo no configured value"


def test_create_app_refuses_no_configuration_authority_at_all():
    """Requirement 4's other half: neither is not a configuration."""
    with pytest.raises(SettingsAuthorityError, match="exactly one"):
        create_app()


def test_create_app_exposes_one_settings_object_through_both_state_attributes(
    settings, monkeypatch
):
    """Requirement 5. `app.state.settings` **is** `app.state.composition.settings`.

    Built without a supplied composition, which is the production path. The
    engine and the provider are stubbed because this case is about which object
    the application holds, not about reaching PostgreSQL or Discord.
    """
    monkeypatch.setattr(
        composition_module, "create_engine", lambda *args, **kwargs: object()
    )
    monkeypatch.setattr(
        composition_module,
        "build_provider",
        lambda provider_settings, **kwargs: FakeDiscordProvider(),
    )
    app = create_app(settings, run_startup_checks=False)

    assert app.state.settings is app.state.composition.settings
    assert type(app.state.settings) is WebSettings
    assert app.state.settings is not settings, (
        "and it is the canonical rebuild, not the caller's object"
    )
    assert app.state.settings == settings, "which is equal to it in every field"


def test_a_compositions_canonical_graph_cannot_be_replaced_after_construction(
    composition
):
    """The reassignment this used to demonstrate is now refused at the assignment.

    The earlier version of this case replaced `composition.settings` with a lying
    graph and asserted that `create_app` refused *the next time it was called*.
    That was a real property and the wrong one: an application already built from
    this composition would have gone on serving requests, and nothing in the
    factory runs again per request. `settings` is now a read-only property over a
    write-once slot, so the swap itself fails and there is no window to check.
    """
    canonical = composition.settings
    hostile = graph_with(
        canonical, session=lying(canonical.session, Lie("idle_minutes", 5))
    )

    with pytest.raises(AttributeError):
        composition.settings = hostile
    with pytest.raises(SettingsAuthorityError, match="written once"):
        composition._settings = hostile  # noqa: SLF001 - the next reach a caller has

    assert composition.settings is canonical
    app = create_app(composition=composition, run_startup_checks=False)
    assert app.state.settings is canonical


def test_create_app_still_requires_a_canonical_graph_from_a_composition_subclass(
    settings, provider, migrated_database
):
    """What the factory's remaining requirement detects, stated exactly.

    `WebComposition` canonicalises its own graph and holds it write-once, so an
    ordinary composition cannot fail this. A **subclass** can: `settings` is a
    property, and a subclass may answer it with anything. The portal suite ships
    one such subclass, so the requirement is not hypothetical — it is the reason
    `create_app` states the property rather than inheriting it from how the
    object it was handed happened to be built.

    Built through the ordinary harness constructor, with the engine guard intact
    and no `object.__new__`, no private mutation and no skipped validation: the
    subclass is genuine and its canonical graph is real. Only the *property* the
    factory reads answers something else.
    """
    lie = Lie("idle_minutes", 5)

    class CompositionAnsweringAnotherGraph(SubstitutedComposition):
        __slots__ = ()

        @property
        def settings(self):
            canonical = self._settings  # noqa: SLF001 - the genuine one, untouched
            return graph_with(canonical, session=lying(canonical.session, lie))

    forged = CompositionAnsweringAnotherGraph(
        settings=settings,
        engine=migrated_database,
        provider=provider,
        provider_client=None,
    )

    with pytest.raises(SettingsAuthorityError, match="WebSettings.session"):
        create_app(composition=forged, run_startup_checks=False)


@pytest.mark.parametrize(
    "service",
    [OAuthLoginService, BreakGlassService],
)
def test_a_service_refuses_anything_that_is_not_the_canonical_graph(
    settings, composition, migrated_database, service
):
    """The services state the requirement rather than trusting their one caller.

    Both retain the graph and read it again per operation, so both are consumers
    in the sense the finding means. Requiring the canonical object here is what
    keeps the property true for a construction site that does not exist yet.
    """
    lie = Lie("oauth_transaction_minutes", 240)
    hostile = graph_with(
        composition.settings, session=lying(composition.settings.session, lie)
    )
    with migrated_database.connect() as connection:
        services = composition.services(connection)
        common = {
            "session_service": services.session_service,
            "audit": services.audit,
            "accounts": services.accounts,
            "settings": hostile,
        }
        arguments = (
            {
                "transactions": services.transactions,
                "token_grants": services.tokens,
                "role_mappings": services.mappings,
                "membership": services.membership,
                "envelope": composition.envelope,
            }
            if service is OAuthLoginService
            else {
                "webauthn_repository": services.credentials,
                "recovery_grants": services.grants,
            }
        )
        with pytest.raises(SettingsAuthorityError, match=service.__name__):
            service(**common, **arguments)


# ---------------------------------------------------------------------------
# 7. The identity provider is not a second authority (blocking findings 1 and 2)
# ---------------------------------------------------------------------------
#
# The previous correction built the production provider from `settings.discord`
# and kept a `provider_double: IdentityProvider` parameter beside it, refusing
# only a concrete `DiscordIdentityProvider`. Two things were wrong with that:
#
# 1. `IdentityProvider` is a *structural* protocol. A wrapper, a delegating
#    adapter, an alternate implementation or an ordinary fake can hold graph B's
#    client id, secret, redirect URI, scopes, guild and endpoints, satisfy the
#    protocol, fail the `isinstance` exclusion, and then serve R-03's
#    authorization URL and R-04's token exchange. Calling the parameter "double"
#    described an intention, not a type.
# 2. `WebComposition.provider` was publicly assignable, and both routes
#    dereference it per request. `create_app` checked it once; a caller could
#    build the application, replace the provider, and make requests through a
#    graph nothing had validated. The regression offered as proof replaced the
#    provider and called `create_app` **again**, so it never tested that.
#
# Both parameters are gone and the three process-lifetime objects are write-once.
# The cases below prove what a production caller can and cannot construct.


def _mock_token_client(recorder: list[httpx.Request]) -> httpx.AsyncClient:
    """A transport that records requests and answers a valid token body.

    Deterministic HTTP, no socket. Only the *transport* is supplied — the timeout
    and the no-redirect rule come from the provider's settings.
    """

    def handler(request: httpx.Request) -> httpx.Response:
        recorder.append(request)
        return httpx.Response(
            200,
            json={
                "access_token": "synthetic-access-token",
                "expires_in": 604800,
                "scope": "identify guilds.members.read",
            },
        )

    return httpx.AsyncClient(transport=httpx.MockTransport(handler))


class DelegatingIdentityProvider:
    """An `IdentityProvider` that is not a `DiscordIdentityProvider`, and lies.

    It satisfies the protocol structurally — `provider_key`, `authorization_url`,
    `exchange`, `verify` — and forwards every one of them to a **real** Discord
    adapter configured from a second graph. This is the object blocking finding 1
    is about: the removed `provider_double` parameter's `isinstance` exclusion
    admitted it, and everything it answers carries graph B's configuration.

    Nothing here is exotic. A caching decorator, a metrics wrapper or a
    retry-on-outage adapter would have exactly this shape.
    """

    provider_key = "discord"

    def __init__(self, inner) -> None:
        self._inner = inner

    def authorization_url(self, *, state: str, code_challenge: str) -> str:
        return self._inner.authorization_url(state=state, code_challenge=code_challenge)

    async def exchange(self, *, code: str, code_verifier: str):
        return await self._inner.exchange(code=code, code_verifier=code_verifier)

    async def verify(self, tokens):
        return await self._inner.verify(tokens)


def _annotations(function) -> list[str]:
    """Every annotation of `function`, as written, without resolving it.

    Written rather than resolved because `provider_client` is annotated with a
    string naming a `TYPE_CHECKING`-only import; resolving would need `httpx` in
    the production module's namespace, which is the thing the adapter boundary
    keeps out of it.
    """
    return [str(value) for value in function.__annotations__.values()]


def test_production_construction_admits_no_provider_and_no_engine(
    settings, migrated_database
):
    """Findings 1.3 and 3.1. The boundary is the absence of a parameter.

    Asserted twice over, because a signature that merely *happens* not to mention
    a provider today is a comment: the parameter names are pinned as a set, no
    annotation on either public constructor names `IdentityProvider` or `Engine`,
    and the four keywords a caller would actually reach for are rejected by the
    interpreter before any object is built.
    """
    assert set(inspect.signature(WebComposition.__init__).parameters) == {
        "self",
        "settings",
        "provider_client",
    }
    assert set(inspect.signature(create_app).parameters) == {
        "settings",
        "composition",
        "run_startup_checks",
    }
    for annotation in _annotations(WebComposition.__init__) + _annotations(create_app):
        assert "IdentityProvider" not in annotation, annotation
        assert "Engine" not in annotation, annotation

    for keyword, value in (
        ("provider", object()),
        ("provider_double", object()),
        ("engine", migrated_database),
    ):
        with pytest.raises(TypeError, match=keyword):
            WebComposition(settings=settings, **{keyword: value})
        with pytest.raises(TypeError, match=keyword):
            create_app(settings, **{keyword: value})


async def test_a_wrapper_provider_holding_another_graph_cannot_reach_production(
    settings, migrated_database, tmp_path
):
    """Finding 1.2, and the reason a concrete-class exclusion was never enough.

    The wrapper is a genuine `IdentityProvider` by structure, is **not** a
    `DiscordIdentityProvider`, and demonstrably carries graph B: the URL it
    answers is graph B's authorization endpoint with graph B's client id and
    redirect URI in it. Under the removed seam that object was accepted.

    What is asserted now is that no supported production construction takes it —
    and that the composition built from graph A holds a provider derived from
    graph A's own `discord` object, which is the positive half of the same fact.
    """
    foreign = foreign_graph(
        tmp_path,
        WEB_PUBLIC_ORIGIN="https://elsewhere.test",
        WEB_ALLOWED_HOSTS="elsewhere.test",
        WEB_DISCORD_CLIENT_ID="9990000001",
        WEB_DISCORD_REDIRECT_URI="https://elsewhere.test/auth/discord/callback",
        WEB_WEBAUTHN_RP_ID="elsewhere.test",
    )
    real = DiscordIdentityProvider(foreign.discord)
    wrapper = DelegatingIdentityProvider(real)
    try:
        assert not isinstance(wrapper, DiscordIdentityProvider), (
            "the removed exclusion tested exactly this and would have admitted it"
        )
        for member in ("provider_key", "authorization_url", "exchange", "verify"):
            assert hasattr(wrapper, member), member
        forwarded = wrapper.authorization_url(state="s", code_challenge="c")
        assert quote(foreign.discord.redirect_uri, safe="") in forwarded
        assert foreign.discord.client_id in forwarded

        for keyword in ("provider", "provider_double"):
            with pytest.raises(TypeError, match=keyword):
                WebComposition(settings=settings, **{keyword: wrapper})
            with pytest.raises(TypeError, match=keyword):
                create_app(settings, **{keyword: wrapper})

        composition = substituted_composition(
            settings=settings, engine=migrated_database
        )
        try:
            assert composition.provider.is_configured_from(
                composition.settings.discord
            )
            url = composition.provider.authorization_url(state="s", code_challenge="c")
            assert quote(settings.discord.redirect_uri, safe="") in url
            assert "elsewhere.test" not in url
        finally:
            await composition.aclose()
    finally:
        await real.aclose()


async def test_a_real_provider_from_another_graph_is_refused_even_by_the_test_seam(
    settings, migrated_database, tmp_path
):
    """Finding 1.1. Two complete, individually valid graphs; no way to combine them.

    Production offers no parameter at all, so the only construction that can even
    attempt this is the suite's own harness — and the composition refuses it
    there too, at construction, by asking whether the provider's configuration
    object **is** this graph's `discord`. Identity, never equality: two
    independently built graphs that happen to agree today are still two
    authorities, and comparing their fields would be comparing the client secret.
    """
    foreign = foreign_graph(
        tmp_path,
        WEB_DISCORD_CLIENT_ID="9990000001",
        WEB_DISCORD_GUILD_ID="900000000000000009",
    )
    real = DiscordIdentityProvider(foreign.discord)
    try:
        with pytest.raises(SettingsAuthorityError) as refusal:
            substituted_composition(
                settings=settings, engine=migrated_database, provider=real
            )
    finally:
        await real.aclose()

    rendered = str(refusal.value)
    secret = foreign.discord.client_secret.material.decode("utf-8")
    for value in (
        foreign.discord.client_id,
        str(foreign.discord.guild_id),
        foreign.discord.redirect_uri,
        secret,
    ):
        assert value not in rendered, "the refusal must echo no provider value"


async def test_the_composition_builds_its_provider_from_its_own_canonical_graph(
    settings, migrated_database
):
    """Requirement 5. Authorization URL, exchange body, endpoint and timeout.

    The caller's `discord` settings answer a different redirect URI once
    composition is over. Everything the provider sends is the canonical value —
    the one S-05 checked against the public origin — and the caller's object is
    never consulted again. The timeout is asserted on the injected client because
    that is where a transport could have carried one of its own.
    """
    requests: list[httpx.Request] = []
    client = _mock_token_client(requests)
    lie = Lie("redirect_uri", "https://elsewhere.test/auth/discord/callback")
    hostile = graph_with(settings, discord=lying(settings.discord, lie))

    composition = substituted_composition(
        settings=hostile, engine=migrated_database, provider_client=client
    )
    lie.engage()

    try:
        provider = composition.provider
        assert isinstance(provider, DiscordIdentityProvider)
        assert provider.is_configured_from(composition.settings.discord), (
            "the provider's authority must be the composition's own object"
        )

        url = provider.authorization_url(
            state="the-state", code_challenge="the-challenge"
        )
        tokens = await provider.exchange(code="the-code", code_verifier="the-verifier")
    finally:
        await composition.aclose()

    assert quote(settings.discord.redirect_uri, safe="") in url
    assert "elsewhere.test" not in url
    assert tokens.provider_key == "discord"

    sent = dict(parse_qsl(requests[-1].content.decode("utf-8")))
    assert sent["redirect_uri"] == settings.discord.redirect_uri
    assert sent["client_id"] == settings.discord.client_id
    assert str(requests[-1].url) == settings.discord.token_url
    assert client.timeout == httpx.Timeout(settings.discord.api_timeout_seconds)
    assert lie.lying_reads == 0, lie.reads


async def test_the_live_provider_cannot_be_replaced_after_create_app(
    settings, migrated_database
):
    """Finding 2, requirement 4. The post-construction bypass, tested for real.

    The earlier regression replaced `composition.provider` and called
    `create_app` a *second* time, which proved the factory refuses a composition
    it has never accepted. It said nothing about the application already serving
    requests — and R-03 and R-04 read `composition.provider` per request, so that
    was the whole defect.

    Here the application is built first. Then every supported route to a
    different provider is attempted: the public attribute, the private slot
    behind it, and `app.state.composition`, which the routes deliberately no
    longer dereference. Afterwards R-03 **and** R-04 are driven and the original
    graph-A double is shown to be the object that answered both.
    """
    original = FakeDiscordProvider(role_ids=frozenset())
    intruder = FakeDiscordProvider(subject="700000000000000002")
    composition = substituted_composition(
        settings=settings, engine=migrated_database, provider=original
    )
    app = create_app(composition=composition, run_startup_checks=False)

    with pytest.raises(AttributeError):
        composition.provider = intruder
    with pytest.raises(SettingsAuthorityError, match="written once"):
        composition._provider = intruder  # noqa: SLF001 - the next reach a caller has
    # State, not only the refusal: the object behind the property is untouched.
    assert composition._provider is original  # noqa: SLF001
    assert composition.provider is original

    # The one indirection left: replacing the whole composition on `app.state`.
    # The routes closed over the composition the factory validated, so this
    # changes what is *reported* and nothing that serves a request.
    app.state.composition = substituted_composition(
        settings=settings, engine=migrated_database, provider=intruder
    )

    async with await _app_client(app) as client:
        started = await client.get("/v1/auth/discord/start")
        assert started.status_code == 303
        state, _challenge = original.authorization_calls[-1]
        await client.get(f"/auth/discord/callback?state={state}&code=the-code")

    assert original.authorization_calls, "R-03 used the provider built at startup"
    assert original.exchange_calls, "and R-04 exchanged through the same object"
    assert intruder.authorization_calls == []
    assert intruder.exchange_calls == []


async def test_startup_validation_and_the_oauth_provider_see_one_redirect_uri(
    settings, migrated_database, tmp_path
):
    """Requirement 6. S-05's check and R-03's URL cannot observe different values.

    S-05 refuses a redirect URI that does not share the public origin, at the
    environment boundary, on the graph the process validated. A provider
    configured from a *second* self-consistent graph would satisfy S-05 on its
    own terms and still send callers to another origin's callback — graph B
    below is exactly that: individually valid, and pointing somewhere else.

    The two cannot diverge because they are the same object. `is_configured_from`
    asks identity, and every route into a different one is closed: there is no
    parameter, the attribute is read-only, the slot behind it is write-once, and
    the harness refuses a foreign Discord adapter.
    """
    elsewhere = foreign_graph(
        tmp_path,
        WEB_PUBLIC_ORIGIN="https://elsewhere.test",
        WEB_ALLOWED_HOSTS="elsewhere.test",
        WEB_DISCORD_REDIRECT_URI="https://elsewhere.test/auth/discord/callback",
        WEB_WEBAUTHN_RP_ID="elsewhere.test",
    )
    # Graph B is individually valid — S-05 accepted it — and its redirect URI is
    # not graph A's.
    assert urlsplit(elsewhere.discord.redirect_uri).netloc == urlsplit(
        elsewhere.public_origin
    ).netloc
    assert elsewhere.discord.redirect_uri != settings.discord.redirect_uri

    composition = substituted_composition(settings=settings, engine=migrated_database)
    foreign_provider = DiscordIdentityProvider(elsewhere.discord)
    try:
        app = create_app(composition=composition, run_startup_checks=False)
        provider = app.state.composition.provider
        assert provider.is_configured_from(app.state.settings.discord)
        url = provider.authorization_url(state="s", code_challenge="c")
        assert quote(settings.discord.redirect_uri, safe="") in url
        assert "elsewhere.test" not in url

        with pytest.raises(AttributeError):
            composition.provider = foreign_provider
        with pytest.raises(SettingsAuthorityError, match="written once"):
            composition._provider = foreign_provider  # noqa: SLF001
        with pytest.raises(SettingsAuthorityError):
            substituted_composition(
                settings=settings,
                engine=migrated_database,
                provider=foreign_provider,
            )
        assert composition.provider is provider
        assert provider.authorization_url(state="s", code_challenge="c") == url
    finally:
        await foreign_provider.aclose()
        await composition.aclose()


async def test_the_centralised_test_only_provider_path_still_serves_the_suite(
    settings, migrated_database
):
    """Requirement 7. The harness works, and is not production construction.

    The double answers R-03, which is what the seam exists for. The two facts
    that keep it out of production are asserted beside it: reaching the seam
    needs a `WebComposition` **subclass**, and the module holding that subclass
    lives under `tests/`.
    """
    double = FakeDiscordProvider(role_ids=frozenset())
    composition = substituted_composition(
        settings=settings, engine=migrated_database, provider=double
    )
    assert composition.provider is double
    assert isinstance(composition, WebComposition)
    assert type(composition) is not WebComposition, (
        "substitution is a subclass, not an argument"
    )
    assert Path(inspect.getfile(type(composition))).parts[-3:-1] == ("tests", "web")

    app = create_app(composition=composition, run_startup_checks=False)
    async with await _app_client(app) as client:
        response = await client.get("/v1/auth/discord/start")

    assert response.status_code == 303
    assert double.authorization_calls, "the double answered the route"

    # A transport for an adapter this composition does not build is a caller
    # error, not a silently ignored argument.
    with pytest.raises(TypeError, match="provider_client"):
        substituted_composition(
            settings=settings,
            engine=migrated_database,
            provider=double,
            provider_client=httpx.AsyncClient(),
        )


async def test_an_injected_client_supplies_transport_and_never_configuration(
    settings, migrated_database
):
    """Finding 1's client half. Injection is a transport seam, not a second graph.

    A client carrying its own timeout would have made
    `WEB_DISCORD_API_TIMEOUT_SECONDS` inoperative for every provider call while
    the settings graph still reported it, and a client that followed redirects
    would send the token exchange — client secret included — wherever a redirect
    pointed. Both are taken from the canonical provider settings instead.
    """
    requests: list[httpx.Request] = []
    client = _mock_token_client(requests)
    client.timeout = httpx.Timeout(600.0)
    client.follow_redirects = True

    composition = substituted_composition(
        settings=settings, engine=migrated_database, provider_client=client
    )
    try:
        assert client.timeout == httpx.Timeout(settings.discord.api_timeout_seconds)
        assert client.follow_redirects is False
        await composition.provider.exchange(code="c", code_verifier="v")
    finally:
        await composition.aclose()

    assert requests, "the injected transport is still the one that answered"
    assert client.is_closed, "aclose() closed exactly the provider requests used"


async def test_no_provider_refusal_or_representation_renders_a_secret(
    settings, migrated_database, tmp_path
):
    """Finding 1.5. Nothing here converts, compares or renders key material."""
    foreign = foreign_graph(tmp_path, WEB_DISCORD_CLIENT_ID="9990000002")
    secrets = (
        settings.discord.client_secret.material.decode("utf-8"),
        foreign.discord.client_secret.material.decode("utf-8"),
        settings.csrf_key.material.decode("latin-1"),
    )
    real = DiscordIdentityProvider(foreign.discord)
    composition = substituted_composition(settings=settings, engine=migrated_database)
    try:
        with pytest.raises(SettingsAuthorityError) as substituted:
            substituted_composition(
                settings=settings, engine=migrated_database, provider=real
            )
        with pytest.raises(SettingsAuthorityError) as replaced:
            composition._provider = real  # noqa: SLF001
        with pytest.raises(TypeError) as parameter:
            WebComposition(settings=settings, provider=real)

        rendered = [
            str(substituted.value),
            str(replaced.value),
            str(parameter.value),
            repr(composition.settings.discord),
            repr(composition.settings.csrf_key),
            repr(composition.provider),
        ]
    finally:
        await real.aclose()
        await composition.aclose()

    for text in rendered:
        assert "redacted" in text or "SecretKey" not in text
        for secret in secrets:
            assert secret not in text


# ---------------------------------------------------------------------------
# 7b. The engine is derived from the canonical graph too (blocking finding 3)
# ---------------------------------------------------------------------------
#
# `WebComposition(settings=A, engine=B)` accepted any SQLAlchemy engine. The
# argument recorded for it — that `settings.database.url` has exactly one reader,
# so an injected engine cannot disagree with a second consumer — proved the wrong
# thing: with one reader and an injected engine, the configured database
# selection is simply *ignored*. Running S-14 and S-15 against B then proves B is
# usable and at the expected revision, not that B is the database graph A names.
#
# There is no whole-engine parameter now. The construction dependency is
# `_build_engine`, which production implements by calling `build_engine` with its
# own canonical graph, and which the harness overrides to lend the suite's
# guarded disposable engine — with ownership stated, so a lent engine is never
# disposed by an application.


class RecordingEngine:
    """Stands in for a SQLAlchemy engine where only disposal is observed."""

    def __init__(self) -> None:
        self.disposals = 0

    def dispose(self) -> None:
        self.disposals += 1


async def test_the_default_engine_builder_receives_the_canonical_graph_and_pool_once(
    settings, monkeypatch
):
    """Finding 3's positive half, on the production construction path.

    Three properties, none of which involves comparing a rendered database URL —
    a comparison would admit two authorities that happen to agree, would be
    unreliable across dialect spellings, and would be a comparison of a string
    that may carry credentials:

    1. `build_engine` is called exactly once, and the graph it is handed **is**
       the composition's canonical one — not the caller's object;
    2. the url and the four N-53 pool numbers SQLAlchemy receives are the ones
       that graph carries, read once; and
    3. the engine the composition serves from is the one that call returned.
    """
    engines: list[RecordingEngine] = []
    created: list[tuple] = []
    graphs: list[object] = []
    real_build_engine = composition_module.build_engine

    def create_engine_spy(url, **kwargs):
        created.append((url, kwargs))
        engines.append(RecordingEngine())
        return engines[-1]

    def build_engine_spy(graph):
        graphs.append(graph)
        return real_build_engine(graph)

    monkeypatch.setattr(composition_module, "create_engine", create_engine_spy)
    monkeypatch.setattr(composition_module, "build_engine", build_engine_spy)
    monkeypatch.setattr(
        composition_module,
        "build_provider",
        lambda provider_settings, **kwargs: FakeDiscordProvider(),
    )

    composition = WebComposition(settings=settings)

    assert len(graphs) == 1, f"the engine is built once: {graphs}"
    assert graphs[0] is composition.settings, (
        "and from the canonical graph, not the caller's object"
    )
    assert graphs[0] is not settings

    assert len(created) == 1
    url, kwargs = created[0]
    pool = composition.settings.database_pool
    assert url == composition.settings.database.url
    assert kwargs["pool_size"] == pool.pool_size
    assert kwargs["max_overflow"] == pool.max_overflow
    assert kwargs["pool_timeout"] == pool.pool_timeout_seconds
    assert kwargs["pool_pre_ping"] is True
    assert kwargs["connect_args"]["options"] == (
        f"-c statement_timeout={pool.statement_timeout_ms}"
    )
    assert composition.engine is engines[0]

    # And a production composition owns what it built, so cleanup disposes it.
    await composition.aclose()
    assert engines[0].disposals == 1


def test_the_engine_a_composition_serves_from_cannot_be_replaced(composition):
    """Finding 3's other half of finding 2's shape.

    A replaceable engine is the same defect as a replaceable provider: every
    transaction below opens on `composition.engine`, and the startup checks ran
    against whatever it was at the time.
    """
    original = composition.engine
    with pytest.raises(AttributeError):
        composition.engine = object()
    with pytest.raises(SettingsAuthorityError, match="written once"):
        composition._engine = object()  # noqa: SLF001
    assert composition.engine is original


async def test_the_application_checks_repositories_and_lifecycle_use_one_engine(
    settings, provider, migrated_database, monkeypatch
):
    """Finding 3's "what is checked is what serves" requirement, asserted by identity.

    The resource checks receive the composition's canonical graph and the
    composition's engine — the same objects, not equal ones — and a request's
    transaction then writes a row that is visible on that engine. `aclose()`
    leaves it alone, because a lent engine is not owned.

    **The checks run in the lifespan, not in the factory** (2026-08-16, P3.G1
    lifecycle re-review). They used to run inside `create_app()`, which meant a
    refusal escaped with the provider and the owned engine already built and no
    application in existence to release them. What is asserted here is unchanged —
    which graph and which engine the checks are handed — but it is asserted where
    they now happen, and the factory is shown to have run none of them.
    """
    seen: list[tuple] = []

    def resource_check_spy(graph, engine):
        seen.append((graph, engine))
        return ()

    monkeypatch.setattr(app_module, "run_resource_checks", resource_check_spy)
    composition = substituted_composition(
        settings=settings, engine=migrated_database, provider=provider
    )
    app = create_app(composition=composition)

    assert seen == [], "returning from the factory is not a passed resource check"

    async with application_lifespan(app) as messages:
        assert messages[-1]["type"] == "lifespan.startup.complete"
        assert len(seen) == 1
        checked_settings, checked_engine = seen[0]
        assert checked_settings is composition.settings
        assert checked_engine is migrated_database
        assert app.state.composition.engine is migrated_database

        async with await _app_client(app) as client:
            response = await client.get("/v1/auth/discord/start")
        assert response.status_code == 303

    with migrated_database.connect() as connection:
        stored = connection.execute(select(oauth_transactions.c.id)).scalars().all()
    assert len(stored) == 1, "the request's transaction opened on that same engine"


async def test_a_lent_engine_is_never_disposed_by_the_application(
    settings, provider, migrated_database
):
    """Ownership is explicit, so a shared fixture engine survives an `aclose()`.

    `dispose()` is replaced on the instance rather than asserted around, because
    disposing a SQLAlchemy engine does not make it unusable — it silently
    replaces the pool, which is exactly the kind of damage a later test would
    report as something else entirely.
    """
    disposals: list[int] = []
    migrated_database.dispose = lambda *args, **kwargs: disposals.append(1)
    try:
        composition = substituted_composition(
            settings=settings, engine=migrated_database, provider=provider
        )
        assert composition._owns_engine is False  # noqa: SLF001 - beside the behaviour
        await composition.aclose()
        assert disposals == [], (
            "an engine this composition did not build is not its to dispose"
        )
    finally:
        del migrated_database.dispose


def test_the_test_only_factory_accepts_only_the_guarded_disposable_target(settings):
    """The harness re-asks the suite's safety contract about **this** engine.

    Both layers, both refused: a PostgreSQL engine naming another database, and
    one that would dial TCP — which `tests/conftest.py` documents as
    indistinguishable from a forwarded port to a server on another machine.
    Neither engine is ever connected; the static layer refuses first.
    """
    for url, expected in (
        ("postgresql+psycopg:///freedom_dev", "disposable database"),
        ("postgresql+psycopg://localhost/freedom_test", "socket"),
    ):
        engine = sqlalchemy_create_engine(url)
        try:
            with pytest.raises(UnsafeDatabaseTargetError, match=expected):
                substituted_composition(settings=settings, engine=engine)
        finally:
            engine.dispose()


def test_the_harness_is_never_imported_by_production_code():
    """TC-STRUCT-09. The substitution path is in `tests/`, and stays there.

    Asserted rather than reviewed: a production module importing the harness
    would restore, by the back door, exactly the arbitrary-dependency seam this
    remediation removed.

    An *import* is what is refused, not a mention: `adapters/web/composition.py`
    names the harness in the docstring of each protected hook, so a reader
    arriving at `_build_provider` learns immediately where its only override
    lives. A pointer in prose is the opposite of a dependency.
    """
    root = Path(__file__).resolve().parents[2]
    importing = re.compile(
        r"^\s*(?:from\s+\S*composition_harness|import\s+\S*composition_harness)",
        re.MULTILINE,
    )
    offenders = [
        path.relative_to(root)
        for directory in ("adapters", "application", "domain", "tools", "helpers")
        for path in (root / directory).rglob("*.py")
        if importing.search(path.read_text(encoding="utf-8"))
    ]
    assert offenders == [], offenders

    # The check has teeth: the same pattern finds this module's own import.
    assert importing.search(Path(__file__).read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# 8. The controls, exercised where they run (requirement 6)
# ---------------------------------------------------------------------------


async def _app_client(app):
    transport = httpx.ASGITransport(app=app)
    return httpx.AsyncClient(
        transport=transport, base_url=PUBLIC_ORIGIN, follow_redirects=False
    )


def _compose(hostile, migrated_database, provider) -> WebComposition:
    return substituted_composition(
        settings=hostile, engine=migrated_database, provider=provider
    )


async def test_the_login_transaction_cookie_carries_the_canonical_lifetime(
    settings, provider, migrated_database
):
    """Requirement 6, cookie attributes, through the route that sets them.

    `R-03` sets the login-transaction cookie with `max_age =
    oauth_transaction_minutes * 60` and `secure = cookie_secure`, both read from
    the settings the factory holds. A cookie outliving its transaction is a
    replayable login attempt.
    """
    accepted = settings.session.oauth_transaction_minutes
    lie = Lie("oauth_transaction_minutes", 240)
    composition = _compose(
        graph_with(settings, session=lying(settings.session, lie)),
        migrated_database,
        provider,
    )
    app = create_app(composition=composition, run_startup_checks=False)
    lie.engage()

    async with await _app_client(app) as client:
        response = await client.get("/v1/auth/discord/start")

    cookie = response.headers["set-cookie"]
    assert f"Max-Age={accepted * 60}" in cookie, cookie
    assert "Secure" in cookie and "HttpOnly" in cookie, cookie
    assert lie.lying_reads == 0, lie.reads


async def test_the_session_cookie_name_the_routes_answer_to_is_the_canonical_one(
    settings, provider, migrated_database
):
    """Requirement 6, cookie **name**, through `R-01`'s behaviour.

    The root route branches on the presence of the session cookie, so the name
    the application answers to is observable without creating a session. A name
    that changed after composition would be a session cookie the portal stopped
    recognising — every authenticated caller silently logged out.
    """
    lie = Lie("cookie_name", "__Host-elsewhere")
    composition = _compose(
        graph_with(settings, session=lying(settings.session, lie)),
        migrated_database,
        provider,
    )
    app = create_app(composition=composition, run_startup_checks=False)
    lie.engage()

    async with await _app_client(app) as client:
        recognised = await client.get(
            "/", cookies={settings.session.cookie_name: "opaque"}
        )
        ignored = await client.get("/", cookies={"__Host-elsewhere": "opaque"})

    assert recognised.headers["location"] == "/v1/characters"
    assert ignored.headers["location"] == "/v1/login"
    assert lie.lying_reads == 0, lie.reads


async def test_the_body_bound_is_the_canonical_one_at_the_middleware(
    settings, provider, migrated_database
):
    """Requirement 6, N-19, before the body is read."""
    lie = Lie("max_request_bytes", 64 * 1024 * 1024)
    composition = _compose(
        graph_with(settings, bounds=lying(settings.bounds, lie)),
        migrated_database,
        provider,
    )
    app = create_app(composition=composition, run_startup_checks=False)
    lie.engage()
    bound = settings.bounds.max_request_bytes

    async with await _app_client(app) as client:
        over = await client.post("/v1/anything", content=b"x" * (bound + 1))
        under = await client.post("/v1/anything", content=b"x" * 16)

    assert over.status_code == 413
    assert under.status_code != 413
    assert lie.lying_reads == 0, lie.reads


async def test_the_trusted_proxy_hop_count_is_the_canonical_one(
    settings, provider, migrated_database
):
    """Requirement 6, N-34, at the object that interprets `X-Forwarded-For`."""
    lie = Lie("trusted_proxy_hops", 2)
    composition = _compose(
        graph_with(settings, bounds=lying(settings.bounds, lie)),
        migrated_database,
        provider,
    )
    app = create_app(composition=composition, run_startup_checks=False)
    lie.engage()

    policy: ClientAddressPolicy = app.state.address_policy
    assert policy.trusted_hops == settings.bounds.trusted_proxy_hops == 1
    assert lie.lying_reads == 0, lie.reads


async def test_the_client_digest_recorded_by_a_route_uses_the_canonical_key(
    settings, provider, migrated_database
):
    """Requirement 6, the keyed digest, read from durable state.

    `client_digest_key` is what every audited client identity and every
    rate-limit bucket is keyed by. A key that changed after startup would make
    the digests written before and after uncorrelatable, which is the same as not
    recording them.
    """
    substitute = SecretKey(name="WEB_SECRET_KEY_CLIENT_DIGEST", material=b"z" * 32)
    lie = Lie("client_digest_key", substitute)
    composition = _compose(lying(settings, lie), migrated_database, provider)
    app = create_app(composition=composition, run_startup_checks=False)
    lie.engage()

    async with await _app_client(app) as client:
        response = await client.get("/v1/auth/discord/start")
    assert response.status_code == 303

    with migrated_database.connect() as connection:
        recorded = connection.execute(
            select(oauth_transactions.c.client_ip_hash)
        ).scalars().all()

    expected = keyed_digest(settings.client_digest_key, "127.0.0.1")
    assert recorded == [expected]
    assert recorded != [keyed_digest(substitute, "127.0.0.1")]
    assert lie.lying_reads == 0, lie.reads


async def test_the_provider_is_built_from_the_canonical_provider_settings(
    settings, migrated_database
):
    """Requirement 6, the redirect URI, at the real adapter that sends callers to it.

    S-05 checks at startup that the configured redirect URI shares the public
    origin. A provider that answered a different one afterwards would deliver the
    authorization code to whoever owned that host.
    """
    lie = Lie("redirect_uri", "https://elsewhere.test/auth/discord/callback")
    composition = substituted_composition(
        settings=graph_with(settings, discord=lying(settings.discord, lie)),
        engine=migrated_database,
    )
    lie.engage()
    try:
        assert isinstance(composition.provider, DiscordIdentityProvider)
        url = composition.provider.authorization_url(state="s", code_challenge="c")
    finally:
        await composition.aclose()

    assert quote(settings.discord.redirect_uri, safe="") in url
    assert "elsewhere.test" not in url
    assert lie.lying_reads == 0, lie.reads


def test_a_sealed_verifier_uses_the_canonical_active_encryption_version(
    settings, provider, migrated_database, operation_clock
):
    """Requirement 6, the encryption key selection, proved by a round trip.

    `OAuthLoginService` reads `encryption.active_version` twice per login — once
    into the AAD a ciphertext is bound to, once when that ciphertext is read back
    — and `Envelope` selects the key from the same keyring. A version that
    changed between those reads binds a verifier to a key nobody can name, and the
    consumption below is what proves it did not: the callback recovers the exact
    verifier the start sealed.
    """
    lie = Lie("active_version", 7)
    composition = substituted_composition(
        settings=graph_with(settings, encryption=lying(settings.encryption, lie)),
        engine=migrated_database,
        provider=provider,
    )
    lie.engage()

    with operation_clock.begin() as (connection, now):
        started, state = composition.services(connection).oauth.start(
            provider=composition.provider,
            return_path=None,
            now=now,
            client_ip_hash=None,
        )
    # The consumption writes no row of its own, so it needs no second reading —
    # only an instant inside the transaction's accepted window.
    with migrated_database.begin() as connection:
        recovered = composition.services(connection).oauth.consume(
            transaction_id=started.transaction_id,
            state=state,
            now=now + timedelta(seconds=1),
            correlation_id=started.transaction_id,
        )

    assert recovered.code_verifier, "the verifier must decrypt under the canonical key"
    with migrated_database.connect() as connection:
        version = connection.execute(
            select(oauth_transactions.c.key_version).where(
                oauth_transactions.c.id == started.transaction_id
            )
        ).scalar_one()
    assert version == settings.encryption.active_version
    assert lie.lying_reads == 0, lie.reads


# ---------------------------------------------------------------------------
# 9. The environment boundary is unchanged (requirement 9)
# ---------------------------------------------------------------------------


def test_the_environment_still_aggregates_every_problem_into_one_redacted_refusal(
    tmp_path,
):
    """Requirement 9. Five bad variables, one error, five names, no values.

    Canonicalisation happens *after* `from_environment`, so it must not have
    turned a collected list of problems into the first one raised. The variable
    names are the exact ones `.env.example` documents and the production readers
    accept — the earlier version of this case used a name the reader does not
    recognise and a value that was inside its accepted range, so two of the four
    "problems" were never problems and the aggregation it claimed to prove was
    proved for two variables (corrected 2026-08-16, re-review finding 2).

    The sentinels are recognisable strings **outside** every accepted bound, so
    the assertion is that none of them appears anywhere in the rendered refusal,
    not merely that the message looks careful.
    """
    sentinels = {
        # N-06: a ceiling of 60 minutes.
        "WEB_SESSION_IDLE_MINUTES": "970001",
        # N-66: a ceiling of 10 live sessions.
        "WEB_MAX_SESSIONS_PER_ACCOUNT": "970002",
        # N-18: a ceiling of 10 starts per IP per window.
        "WEB_RATE_LIMIT_OAUTH_STARTS": "970003",
        # N-19: a ceiling of 1 MiB.
        "WEB_MAX_REQUEST_BYTES": "97000400",
        # N-34: exactly one trusted hop, either side of which is a loosening.
        "WEB_TRUSTED_PROXY_HOPS": "970005",
    }
    with pytest.raises(ConfigurationError) as refusal:
        WebSettings.from_environment(web_environment(tmp_path, **sentinels))

    rendered = refusal.value.render()
    for variable, value in sentinels.items():
        assert variable in rendered, f"{variable} must be named\n{rendered}"
        assert value not in rendered, f"{variable}'s value must not be echoed"
    named = {
        variable
        for problem in refusal.value.problems
        for variable in problem.variables
    }
    assert named == set(sentinels), (
        f"every supplied problem is reported, and nothing else is: {named}"
    )
    assert "S-10" in refusal.value.refusals(), (
        "and each is still classified as the loosening refusal it is"
    )


def test_a_settings_graph_from_the_environment_is_already_canonical(tmp_path):
    """The ordinary path builds an object canonicalisation only has to confirm.

    Stated as a test because it is the reason canonicalisation is a boundary and
    not a coercion: production configuration is exact-base already, so what the
    boundary removes is only ever something a caller introduced.
    """
    settings = web_settings(tmp_path)
    assert require_canonical_web_settings(settings, subject="test") is settings
    canonical = canonical_web_settings(settings)
    assert canonical == settings
    for name in CANONICAL_SETTINGS_GRAPH[WebSettings]:
        assert type(getattr(settings, name)) is type(getattr(canonical, name))


def test_the_kill_switch_path_survives_canonicalisation(tmp_path):
    """A `Path` is carried through unchanged, so S-13's file still governs."""
    settings = web_settings(tmp_path)
    canonical = canonical_web_settings(settings)
    assert canonical.kill_switch_file == settings.kill_switch_file
    assert isinstance(canonical.kill_switch_file, Path)


def test_canonicalisation_renders_no_key_material(tmp_path):
    """Secrets are moved, never converted, compared, decoded or rendered."""
    settings = web_settings(tmp_path)
    canonical = canonical_web_settings(settings)

    assert canonical.csrf_key.material is settings.csrf_key.material
    assert canonical.discord.client_secret.material is (
        settings.discord.client_secret.material
    )
    for rendered in (repr(canonical.csrf_key), str(canonical.encryption.keys[0])):
        assert "redacted" in rendered
        assert canonical.csrf_key.material.decode("latin-1") not in rendered
