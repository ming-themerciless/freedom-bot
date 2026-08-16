# Phase 3 P3.G1 — provider and engine authority remediation

**Date:** 2026-08-16 · **Package:** P3.G1 (stop gate) · **Author:** working
Technical Lead (Claude) · **Status:** *submitted for fresh independent
implementation review and a distinct security-focused pass. Not accepted.*

**P3.G1, RAID I-09 and RAID I-10 remain OPEN.** Nothing below closes a review
gate. P3.2 and P3.3 have not started and no route, service, worker or provider
was added. Passing tests are evidence offered to a reviewer; they are not an
acceptance.

This corrects
[`phase-3-p3-g1-canonical-settings-graph-remediation-submission.md`](phase-3-p3-g1-canonical-settings-graph-remediation-submission.md),
whose three blocking findings are the subject of the handover in
`docs/review/Handover information`. The canonical settings graph that submission
introduced is intact and unweakened; what is corrected is the two **dependencies
derived from it**, and the mutability of all three.

---

## 1. The corrected result, first

```python
# adapters/web/composition.py — before
class WebComposition:
    def __init__(
        self,
        *,
        settings: WebSettings,
        engine: Engine | None = None,
        provider_client: httpx.AsyncClient | None = None,
        provider_double: IdentityProvider | None = None,
    ) -> None: ...
    # settings, engine, provider, envelope: public, assignable attributes

# adapters/web/composition.py — after
class WebComposition:
    def __init__(
        self,
        *,
        settings: WebSettings,
        provider_client: "httpx.AsyncClient | None" = None,
    ) -> None: ...

    # read-only properties over private, write-once slots
    @property
    def settings(self) -> WebSettings: ...
    @property
    def engine(self) -> Engine: ...
    @property
    def provider(self) -> IdentityProvider: ...
    @property
    def envelope(self) -> Envelope: ...

    # the two protected construction hooks, called once each from __init__
    def _build_engine(self) -> EngineHandle:
        return EngineHandle(build_engine(self._settings), owned=True)

    def _build_provider(self, client) -> IdentityProvider:
        return build_provider(self._settings.discord, client=client)


@dataclass(frozen=True, slots=True)
class EngineHandle:
    engine: Engine
    owned: bool
```

```python
# adapters/web/app.py — before
def create_app(settings=None, *, composition=None, run_startup_checks=True) -> FastAPI
def _require_provider_from(composition, settings) -> None   # called once, at startup
def _register_routes(app) -> None                           # routes read app.state per request

# adapters/web/app.py — after
def create_app(settings=None, *, composition=None, run_startup_checks=True) -> FastAPI
#   _require_provider_from: REMOVED
def _register_routes(app, composition: WebComposition) -> None   # routes close over both
```

```python
# tests/web/composition_harness.py — new, and the suite's only substitution path
def substituted_composition(*, settings, engine, provider=None, provider_client=None) -> WebComposition
class SubstitutedComposition(WebComposition):   # overrides _build_engine and _build_provider
def require_disposable_engine(engine: Engine) -> Engine
```

The statement this submission makes, and proves: **an ordinary production caller
can construct a web application from a settings graph and nothing else. It cannot
supply an identity provider, cannot supply a database engine, and cannot replace
either — or the graph — after the application that validated them exists.**

---

## 2. Finding 1 — `provider_double` was an unrestricted provider seam

### 2.1 Root cause

`WebComposition.__init__` accepted `provider_double: IdentityProvider` and
refused only `isinstance(double, DiscordIdentityProvider)`. `IdentityProvider` is
a `typing.Protocol` — a **structural** contract, satisfied by any object with
`provider_key`, `authorization_url`, `exchange` and `verify`. A wrapper, a
delegating adapter, a caching or metrics decorator, a retry adapter or an
alternate implementation therefore:

- may hold a second, complete, individually valid settings graph's client id,
  client secret, redirect URI, scopes, guild id, endpoints and timeout;
- is not a `DiscordIdentityProvider`, so it passed the exclusion; and
- was then used for R-03's authorization URL and R-04's token exchange.

The parameter's **name** was the only thing making it test-only, and the previous
submission's own prose ("a test double — which is not a Discord provider and
holds no Discord configuration") described an intention the type system did not
carry.

### 2.2 The structural fix

The parameter is removed. `WebComposition.__init__` takes `settings` and an
optional HTTP transport. The provider is built inside the constructor from
`self._settings.discord` — the object `canonical_web_settings` produced from one
read of every field — through the single module-level `build_provider`.

No concrete-class blacklist, type-name test, private-field inspection, equality
comparison, secret comparison, environment-mode flag, call-stack inspection or
`assert` is used to establish this. It is established by the **absence of a
parameter**.

One requirement remains inside the constructor,
`_require_no_second_discord_authority`, and this submission is explicit about
what it is and is not. It is **defence in depth**, not the boundary. The supported
state it detects is exactly one: a `WebComposition` **subclass** whose
`_build_provider` override returns a real `DiscordIdentityProvider` configured
from a graph other than this composition's — asked by identity
(`provider.is_configured_from(self._settings.discord)`), never by comparing
fields, which would be a comparison of the client secret. It cannot classify a
wrapper, and does not pretend to; a structural protocol makes that undecidable,
which is precisely why the boundary is the missing parameter.

### 2.3 The separate test construction path

`tests/web/composition_harness.py` defines `SubstitutedComposition`, a
`WebComposition` subclass overriding `_build_engine` and `_build_provider`, and
`substituted_composition(...)`, the function every fixture and test calls.

**Why it is not a supported production authority seam:**

- reaching it requires *writing a subclass*. There is no parameter, keyword,
  environment flag, registry or configuration value that selects it, so no
  production caller arrives here by mistake, by copy-paste, or by renaming an
  argument;
- it is centralised. Four test modules and one fixture use it; no test constructs
  a composition subclass of its own, and the single case that needs one further
  deviation extends `SubstitutedComposition` rather than writing a second one;
- it is visually distinct at every call site: `substituted_composition(...)` never
  reads as production construction; and
- it is proved to be imported by **no** module under `adapters/`, `application/`,
  `domain/`, `tools/` or `helpers/`
  (`test_the_harness_is_never_imported_by_production_code`, which also asserts its
  own detector finds this module's import, so the check is not vacuous).

Deterministic real-provider tests still inject an `httpx` transport through the
production `provider_client` parameter. Transport injection cannot choose the
provider's URLs, credentials, redirect URI, guild, scopes, timeout or
redirect-following policy: `DiscordIdentityProvider.__init__` overwrites
`client.timeout` and `client.follow_redirects` from its canonical settings, and
every other value is read from that settings object alone
(`test_an_injected_client_supplies_transport_and_never_configuration`).

The `IdentityProvider` protocol is unchanged and no provider result-binding check
was weakened.

---

## 3. Finding 2 — the provider remained mutable after the startup check

### 3.1 Root cause

`create_app()` called `_require_provider_from()` once. `WebComposition.provider`
was a public attribute in `__slots__`, and R-03, R-04 and `aclose()` dereferenced
it **per request**. So the sequence "build the application, replace the provider,
make requests" ran entirely through supported API. The regression offered as
proof replaced the provider and then called `create_app` **again**, which tests
that the factory refuses a composition it has never accepted — a different, and
much weaker, statement.

Reproduced before the fix, against an already-built application (§9, run R1):

```
assignment accepted: True
status: 303
original.authorization_calls: 0
intruder.authorization_calls: 1
```

### 3.2 The structural fix

`settings`, `engine` and `provider` are read-only properties over private slots
`_settings`, `_engine`, `_provider`. `WebComposition.__setattr__` refuses to
rebind any of those slots — plus `_owns_engine` and `_envelope` — once written, so
the private name behind each property is write-once as well as the public one.
There is no setter, no mutable container and no supported replacement method.
`frozen=True` is deliberately **not** relied on: `WebComposition` is not a
dataclass, and a frozen wrapper would still have permitted nested mutation.

`aclose()` closes `self._provider` and disposes `self._engine`, which cannot be
anything other than the objects requests used.

The application no longer exposes a second route either. `_register_routes(app,
composition)` closes over the composition the factory accepted, so a route reads
neither `request.app.state.composition` nor a per-request attribute lookup.
`app.state.composition` and `app.state.settings` remain as the diagnostic
references an operator and the suite read; replacing one changes what is
*reported* and cannot change which provider answers an OAuth start or which
engine a transaction opens on. This is asserted, not argued
(`test_the_live_provider_cannot_be_replaced_after_create_app` replaces
`app.state.composition` with a composition holding a different provider and then
drives R-03 **and** R-04).

### 3.3 `_require_provider_from()` is removed, not kept

With the provider derived from `self._settings.discord` and write-once, the
startup comparison could detect no state a supported caller can produce. Keeping
it would be exactly the "one-time startup check described as a structural
security boundary" the handover forbids, so it is deleted.

What survives in `create_app` is `require_canonical_web_settings(composition.settings)`,
and this submission states precisely what supported state *it* detects: a
`WebComposition` **subclass** whose `settings` property answers something other
than the canonical exact-base graph. That is not hypothetical — the portal suite
ships a subclass — and it is proved by
`test_create_app_still_requires_a_canonical_graph_from_a_composition_subclass`,
which builds such a subclass through the ordinary harness constructor with no
`object.__new__`, no private mutation and no skipped validation.

---

## 4. Finding 3 — an injected engine could ignore canonical database settings

### 4.1 Root cause

`WebComposition.__init__(settings=A, engine=B)` accepted any SQLAlchemy engine.
The previous submission's §5 justified this by observing that
`settings.database.url` has exactly one reader, so an injected engine "cannot
disagree with a second consumer of the same value, because there is no second
consumer". That argument is wrong in the direction that matters: with one reader
**and** an injected engine, the configured database selection is not
singly-authoritative — it is *ignored*. Running the S-14/S-15 resource checks
against B then proves B is reachable and at the expected migration revision, not
that B is the database the canonical graph names.

Reproduced before the fix (§9, run R2):

```
accepted.
  canonical graph names  : postgresql+psycopg:///freedom_test
  engine actually serving: postgresql+psycopg:///freedom_dev
  same database?         : False
```

### 4.2 The structural fix

Whole-engine injection is removed from the production constructor. The serving
engine comes from `_build_engine()`, which production implements as
`EngineHandle(build_engine(self._settings), owned=True)` — `build_engine` reads
the four N-53 pool numbers once through `canonical_settings` and hands SQLAlchemy
the url `self._settings.database` selected.

**No rendered database URL is compared with anything.** A comparison would admit
two authorities that happen to agree, would be a comparison of a string that may
carry credentials, and would be unreliable across dialect spellings
(`postgresql:///x` and `postgresql+psycopg:///x` are the same database). The
property is established by there being one construction, from one graph.

`EngineHandle` makes **ownership explicit**. A production composition owns the
engine it built, and `aclose()` disposes it. A lent engine is `owned=False` and is
never disposed, because the suite's `migrated_database` is session-scoped and
shared by hundreds of tests — an application disposing it would silently replace
a pool the next test is holding connections from.

### 4.3 The guarded disposable engine, still guarded

`require_disposable_engine()` in the harness re-runs both layers
`tests/conftest.py` documents, against the engine actually handed over:

1. `assert_disposable_target(engine.url…, expected_database="freedom_test",
   runtime_url=DATABASE_URL, policy=UNIX_SOCKET_ONLY)` — the static identity
   check, including the ambient libpq environment. The URL is rendered with the
   password **hidden**: the identity resolved is backend, host, port and database
   name, so passing key material would only put it into whatever a refusal or a
   test failure renders; and
2. `verify_connected_unix_socket_target(connection, expected_database=…)` — the
   live "which database did this connection land in, and is it a Unix-domain
   socket?" question.

Neither is re-implemented: these are the same two functions the session fixture
calls, so there is one copy of the reasoning. What is added is that they are asked
about *this* engine. Checks, repositories, transactions and cleanup all use the
exact engine handed over — there is only one, held write-once.

No schema change was made and no applied migration was edited.

---

## 5. Canonical graph work retained and regression-tested

Every sound part of the previous remediation is intact and still proved:

| Property | Case |
|---|---|
| Recursive canonicalisation of the declared graph | `test_every_member_of_the_canonical_graph_is_the_exact_base_type` |
| Exact base types at every declared node | same, plus the depth assertions on `SecretKey`, `EncryptionKey`, `ConnectionIdentity` |
| One read per supplied field before reconstruction | `test_the_graph_is_rebuilt_from_exactly_one_read_of_every_field` |
| Fail-closed for an undeclared settings type | `test_canonicalisation_refuses_a_settings_type_the_graph_does_not_declare` |
| Annotation-derived completeness contract, narrow container grammar, falsification cases | `test_the_declared_graph_states_the_whole_topology_the_dataclasses_have`, `test_deleting_one_nested_classification_makes_the_completeness_check_fail`, `test_deleting_a_whole_type_entry_makes_the_completeness_check_fail`, `test_an_unclassified_nested_field_in_a_synthetic_graph_is_reported`, `test_an_unsupported_container_fails_closed_rather_than_reading_as_a_leaf` |
| Phase-aware hostile-subclass tests engaging only after genuine construction | the `Lie`/`lying()` machinery and every case asserting `construction_reads`, `truthful_reads`, `lying_reads` |

`CANONICAL_SETTINGS_GRAPH`, `canonical_settings`, `canonical_web_settings`,
`require_canonical`, `require_canonical_web_settings`, `SettingsAuthorityError`,
`DiscordIdentityProvider`, `OAuthLoginService` and `BreakGlassService` are
**unchanged by this remediation**. The expected topology is still derived from the
dataclasses' annotations and never from the mapping it verifies.

---

## 6. Files changed, and why

| File | Change |
|---|---|
| `adapters/web/composition.py` | `engine` and `provider_double` parameters removed; `_build_engine`/`_build_provider` protected hooks added; `EngineHandle` added; `settings`/`engine`/`provider`/`envelope` become read-only properties over write-once private slots; `__setattr__` states the write-once rule once; `_require_no_second_discord_authority` added as documented defence in depth; `aclose()` documented as closing exactly what requests used |
| `adapters/web/app.py` | `_require_provider_from()` removed; `_composition(request)` helper removed; `_register_routes(app, composition)` closes over the composition the factory accepted; the docstrings state what the surviving graph requirement detects |
| `tests/web/composition_harness.py` | **New.** `SubstitutedComposition`, `substituted_composition()`, `require_disposable_engine()` — the suite's single substitution path |
| `tests/web/conftest.py` | the `composition` fixture builds through the harness |
| `tests/web/test_canonical_settings_graph.py` | section 7 rewritten (provider authority, findings 1 and 2), section 7b added (engine authority, finding 3), the replaced-graph case rewritten as an immutability case, a subclass case added for what `create_app` still detects, and every call site moved to the harness |
| `tests/web/test_settings_construction_validation.py` | two composition call sites moved to the harness; stale comments corrected |
| `tests/web/test_session_policy_numeric_validation.py` | one composition call site moved to the harness |
| `tests/web_fixtures.py` | `FakeDiscordProvider`'s docstring corrected: it no longer describes a `provider_double` parameter that does not exist |
| `docs/contracts/phase-3-configuration-and-dependency-contract.md` | new dated subsection; the two superseded statements named and corrected, by addition |
| `docs/contracts/phase-3-test-traceability.md` | TC-STRUCT-09 added; TC-STRUCT-08 amended where it claimed the superseded properties |
| `docs/project-management/change-log.md` | C-P3.1-O appended (corrects C-P3.1-N) |
| `docs/project-management/raid-register.md` | I-09 and I-10 amended; both left **OPEN** |
| `docs/project-management/status.md` | second 2026-08-16 update appended, correcting three claims in the first |

No other file was edited. No migration, schema, environment variable, `.env`,
credential, visual asset, dependency, systemd unit or runtime grant was touched.

---

## 7. The exact production construction and lifecycle path

```
os.environ
  └─ WebSettings.from_environment(environ)
       · every reader validates and collects; one redacted ConfigurationError
         aggregates every problem; the result is exact-base already
  └─ create_app(settings)
       └─ WebComposition(settings=settings)
            1. self._settings = canonical_web_settings(settings)
                 · descends CANONICAL_SETTINGS_GRAPH, one read per field,
                   exact base types rebuilt through the register's constructors
            2. handle = self._build_engine()
                 = EngineHandle(build_engine(self._settings), owned=True)
                     └─ canonical_settings(settings.database_pool, DatabasePoolSettings)
                     └─ create_engine(self._settings.database.url,
                                      pool_size, max_overflow, pool_timeout,
                                      pool_pre_ping, statement_timeout)   [N-53]
               self._engine, self._owns_engine = handle.engine, handle.owned
            3. self._envelope = Envelope(self._settings.encryption)
            4. self._provider = _require_no_second_discord_authority(
                                    self._build_provider(provider_client))
                 = build_provider(self._settings.discord, client=…)
                     └─ DiscordIdentityProvider(settings.discord)
                          └─ require_canonical(…, DiscordProviderSettings)
                          └─ timeout and follow_redirects taken from those settings
            5. self.startup_warnings = ()          # diagnostic only
            · steps 1–4 write slots that __setattr__ will not let anything rebind
       └─ settings = require_canonical_web_settings(composition.settings)
       └─ run_resource_checks(settings, composition.engine)      [S-12, S-14, S-15]
       └─ app.state.composition / app.state.settings              (diagnostic refs)
       └─ middleware from settings.bounds, settings.session, settings.allowed_hosts
       └─ _register_routes(app, composition)   ← the routes bind here, once

per request
  · composition.engine.begin() → composition.services(connection) → repositories
  · composition.provider.authorization_url / exchange / verify      (R-03, R-04)
  · no route dereferences app.state.composition

shutdown
  └─ composition.aclose()
       · await provider.aclose()      — exactly the provider requests used
       · engine.dispose() if _owns_engine — never an engine lent to it
```

**Honest note on the entry point.** P3.1 commits no ASGI entry module; the
operational contract's topology describes `uvicorn` behind Caddy, and wiring it is
a later action. `create_app(settings)` is therefore the documented production
construction path and the one this submission's claims are about.

### The separate test construction path

```
tests/web/composition_harness.py
  substituted_composition(settings=…, engine=…, provider=…, provider_client=…)
    └─ SubstitutedComposition(WebComposition)
         · __init__ guards the engine (require_disposable_engine: both layers)
         · _build_engine  → EngineHandle(lent_engine, owned=False)
         · _build_provider → the suite's fake, or super() for the real adapter
         · everything else — canonicalisation, envelope, services, repositories,
           lifecycle, and the no-second-Discord-authority requirement — is
           production's, unmodified
```

It is not a supported production authority seam because it is not reachable by
passing anything: it requires defining a subclass, it lives under `tests/`, and no
production module imports it (asserted).

---

## 8. Regression tests mapped to every required property

`tests/web/test_canonical_settings_graph.py`, 56 cases. The handover's numbered
requirements:

| Required property | Case(s) |
|---|---|
| 1 — graph A cannot be combined with a real provider built from valid graph B | `test_a_real_provider_from_another_graph_is_refused_even_by_the_test_seam` (through the only path that can attempt it), `test_production_construction_admits_no_provider_and_no_engine` |
| 2 — graph A cannot be combined with a wrapper/delegating `IdentityProvider` that is not a `DiscordIdentityProvider` but uses graph B | `test_a_wrapper_provider_holding_another_graph_cannot_reach_production` — the wrapper is built, shown to satisfy the protocol structurally, shown **not** to be a `DiscordIdentityProvider`, and shown to answer graph B's endpoint with graph B's client id and redirect URI; every production entry point then refuses it |
| 3 — production `WebComposition` has no arbitrary provider/double parameter | `test_production_construction_admits_no_provider_and_no_engine` — pinned parameter sets for `WebComposition.__init__` and `create_app`, no annotation naming `IdentityProvider` or `Engine`, and interpreter refusals of `provider=`, `provider_double=`, `engine=` on both |
| 4 — after `create_app()`, supported replacement of the live provider is refused and OAuth still uses the original graph-A provider | `test_the_live_provider_cannot_be_replaced_after_create_app` — refuses the property, refuses the private slot, proves the held object unchanged, replaces `app.state.composition`, then drives R-03 and R-04 and shows the startup provider answered both |
| 5 — the authorization URL and token exchange use the client id, redirect URI, endpoint and timeout from the canonical graph | `test_the_composition_builds_its_provider_from_its_own_canonical_graph`, `test_the_provider_is_built_from_the_canonical_provider_settings` |
| 6 — S-05 redirect-origin validation and the live provider cannot observe different redirect URIs | `test_startup_validation_and_the_oauth_provider_see_one_redirect_uri` — graph B is individually valid and S-05-consistent on its own terms; every route to it is closed and the provider is proved to answer the same URL afterwards |
| 7 — the centralised test-only fake-provider path still supports the portal suite without becoming production construction | `test_the_centralised_test_only_provider_path_still_serves_the_suite`, `test_the_harness_is_never_imported_by_production_code`, and the 663-test suite itself |
| Engine — production API cannot accept an arbitrary engine | `test_production_construction_admits_no_provider_and_no_engine` |
| Engine — the default builder receives the canonical graph and its canonical pool settings exactly once | `test_the_default_engine_builder_receives_the_canonical_graph_and_pool_once` |
| Engine — application, resource checks, repositories and lifecycle use the same instance | `test_the_application_checks_repositories_and_lifecycle_use_one_engine` (identity assertions on the checks' arguments, plus a request's row read back from that engine), `test_the_engine_a_composition_serves_from_cannot_be_replaced` |
| Engine — the test-only factory accepts only the guarded disposable engine | `test_the_test_only_factory_accepts_only_the_guarded_disposable_target` (another database; a TCP target) |
| Engine — ownership and cleanup correct for production-owned and fixture-owned | `test_the_default_engine_builder_receives_the_canonical_graph_and_pool_once` (disposed exactly once), `test_a_lent_engine_is_never_disposed_by_the_application` (never disposed) |
| No configured value or secret is compared, rendered, logged or included in a refusal | `test_no_provider_refusal_or_representation_renders_a_secret`, `test_canonicalisation_renders_no_key_material`, and the value-absence assertions inside the two refusal cases |

Every mismatch case uses a **second complete, individually valid graph** built by
`foreign_graph()` from the synthetic environment. No case uses `object.__new__`,
invalid settings, private mutation as its principal proof, or a subclass that
bypasses constructor validation. Where a private attribute is read
(`composition._provider`, `composition._owns_engine`) it is to confirm that state
was unchanged *after* the supported operation was refused, beside a behavioural
assertion, never instead of one.

---

## 9. Verification — fresh results, in the required order

Every run below is from after the final edit. Nothing is recycled. Every
database run used the guarded disposable target
`postgresql+psycopg:///freedom_test`.

| # | Command | Result |
|---|---|---|
| 1 | `./venv-web/bin/python -m pytest tests/web/test_canonical_settings_graph.py -q` (**no** `TEST_DATABASE_URL`) | **27 passed, 29 skipped**, 0 failed — every skip names the missing disposable database |
| 2 | `TEST_DATABASE_URL=… ./venv-web/bin/python -m pytest tests/web/test_canonical_settings_graph.py -q` | **56 passed, 0 failed, 0 skipped** |
| 3 | `… -m pytest tests/web/test_provider_classification.py tests/web/test_oauth_flow.py tests/web/test_oauth_completion_binding.py tests/web/test_oauth_refusal_audit.py tests/web/test_break_glass_login.py tests/web/test_break_glass_escalation.py tests/web/test_security_controls.py tests/web/test_structural_guards.py tests/web/test_settings_construction_validation.py tests/web/test_session_policy_numeric_validation.py -q` | **431 passed, 0 failed, 0 skipped**, 13 warnings |
| 4 | `TEST_DATABASE_URL=… ./venv-web/bin/python -m pytest tests/web -q` | **663 passed, 0 failed, 0 skipped**, 16 warnings |
| 5 | `TEST_DATABASE_URL=… ./venv/bin/python -m pytest -q` | **2260 passed, 0 failed, 0 skipped**, 1 warning |
| 6 | `APP_ENVIRONMENT=test DATABASE_URL=… ./venv/bin/alembic check` | **`No new upgrade operations detected.`** One pre-existing `SAWarning` from `migrations/env.py:133`, unrelated and unchanged |
| 7 | `python -m compileall -q application adapters tools tests` under **both** interpreters | Both **OK** (CPython 3.12.3) |
| 8 | Formatter / linter / type checker | **None configured** — re-verified, not assumed: no `pyproject.toml`, `setup.cfg`, `.ruff.toml`, `.flake8`, `mypy.ini`, `tox.ini` or pre-commit configuration exists, and neither virtualenv has `ruff`, `mypy`, `flake8` or `black` |
| 9 | `git diff --check` | **Clean**, exit 0 |
| 10 | `sha256sum -c docs/review/phase-3-visual-freeze-manifest.sha256` | **14 `OK`**, 0 non-`OK` |
| 11 | Diff/status review for secrets, unrelated edits, generated artifacts, schema/migration changes, stale claims | No secret, no `.env` read, no generated file, no migration touched, no schema change; the diff is the files in §6 |

**The portal suite's environment is complete.** `fastapi 0.115.14`,
`httpx 0.28.1`, Jinja2, SQLAlchemy and `py_webauthn` are installed in
`./venv-web`, and nothing was installed globally. No run reports a missing
dependency, and no test in this package is skipped when the disposable database
is configured.

**Warnings.** The portal's are the pre-existing `httpx` per-request cookie
`DeprecationWarning`s; the bot suite's single warning is the pre-existing
`audioop` deprecation from `discord.player`. Neither is new.

**No production database, live Discord application, guild or Foundry instance was
contacted.** The provider evidence uses `httpx.MockTransport`.

---

## 10. Falsification and reproduction — recorded, not asserted

Each mutation was applied to the worktree, run, and reverted; `adapters/web/composition.py`
and `application/web/config.py` were checksummed before and after every cycle and
are **byte-identical** (`sha256sum -c`: `OK` after each restoration).

| # | Mutation | Result |
|---|---|---|
| F1 | An arbitrary non-Discord provider seam restored — a `provider_double` parameter accepted whenever the object is not a `DiscordIdentityProvider`, exactly the reviewed design | **2 failed, 54 passed**: `test_production_construction_admits_no_provider_and_no_engine` and `test_a_wrapper_provider_holding_another_graph_cannot_reach_production` |
| F2 | Post-`create_app()` provider replacement restored — `_provider` removed from the write-once set and a `provider` setter added | **3 failed, 53 passed**: `test_the_live_provider_cannot_be_replaced_after_create_app`, `test_startup_validation_and_the_oauth_provider_see_one_redirect_uri`, `test_no_provider_refusal_or_representation_renders_a_secret` |
| F3 | Production whole-engine injection restored — `engine: Engine \| None = None` accepted and used | **1 failed, 55 passed**: `test_production_construction_admits_no_provider_and_no_engine`. Reported honestly: exactly one case fails, because the property removed is the *existence of the parameter*. The consequence is shown by reproduction R2 rather than claimed by a count |
| F4 | `"discord": DiscordProviderSettings` deleted from `CANONICAL_SETTINGS_GRAPH` | **4 failed, 52 passed**, including `test_the_declared_graph_states_the_whole_topology_the_dataclasses_have` — the independent completeness contract reports the omission |

Two **before/after reproductions** were run as scripts against the disposable
database, because a failing assertion states that a property is missing while a
reproduction states what an attacker gets:

| # | Reproduction | Under the mutation | After restoration |
|---|---|---|---|
| R1 | Build the application, then assign `composition.provider = intruder`, then `GET /v1/auth/discord/start` | `assignment accepted: True`; `original.authorization_calls: 0`; **`intruder.authorization_calls: 1`** — an already-built application authenticated through a provider assigned after startup | `assignment refused: AttributeError`; **`original.authorization_calls: 1`**; `intruder.authorization_calls: 0` |
| R2 | `WebComposition(settings=A, engine=B)` where A names `freedom_test` and B names another database (never connected) | `accepted.` — engine serving `postgresql+psycopg:///freedom_dev`, `same database?: False` | `refused at construction: WebComposition.__init__() got an unexpected keyword argument 'engine'` |

After every mutation and reproduction the full portal suite was re-run: **663
passed, 0 failed, 0 skipped.**

**Mutation testing was not run and is not claimed**; no mutation tool is
configured. No destructive Git command was used and no unrelated work was
discarded.

---

## 11. Security and secret handling

- **Strictly a tightening, moved one step earlier.** Every refusal added here
  happens while a composition or an application is being constructed, or at an
  attribute assignment. No route, authorization decision, audit behaviour, session
  bound, rate limit, cookie attribute, redaction or error rendering changed.
- **No secret is rendered, compared, decoded or converted.** The one provider
  requirement asks object identity (`is`), never field equality — a field
  comparison of provider settings is a comparison of the client secret. Refusals
  name a type, a boundary or a field path and never a configured value;
  `test_no_provider_refusal_or_representation_renders_a_secret` asserts it against
  recognisable material from both graphs.
- **No rendered database URL is compared or logged.** The engine's authority is
  established by single construction, not by string equality on a value that may
  carry credentials.
- **The OAuth flow's configuration is provably the validated one.** The client id,
  secret, redirect URI, scopes, guild id, endpoints and timeout used by R-03 and
  R-04 are the composition's canonical `settings.discord` — the object S-05 and
  S-06 were answered on — and cannot be replaced for the life of the process.
- **The blast radius of a compromised test path is smaller.** Substitution now
  requires a subclass under `tests/`, so an accidental production call cannot
  reach it, and the engine that path lends is re-checked against the disposable
  target contract.
- **No `.env`, credential, token, player data or production identifier was read,
  printed, copied or modified.** `freedom_test` was the only database contacted.

---

## 12. What did not change

- **No accepted numeric value moved.** No `PolicyBound`, ceiling, floor or exact
  value was edited; no accepted policy value changed.
- **No environment-variable contract change.** Nothing added, renamed or removed;
  `.env.example` is untouched.
- **No schema, migration or database change.** No migration file was opened for
  editing; `alembic check` reports no new upgrade operations.
- **Route inventory unchanged.** The same ten routes (`R-01`…`R-10`);
  `TC-STRUCT-01` still asserts set equality against the parsed contract, and the
  deferred P3.2/P3.3 routes are still absent.
- **Authorization, audit and safe-failure behaviour unchanged.** No capability,
  scope, refusal code, audit action or view model was touched.
- **Deployment topology unchanged.** No systemd unit, dependency, lock file,
  virtualenv or runtime grant touched.
- **Visual freeze intact.** 14 manifest entries verified `OK`.
- **Public behaviour unchanged** for every valid configuration: production already
  passed no engine and no provider, so the removed parameters had no production
  caller to break.

---

## 13. Checks not run, and why

- **No browser, staging, device or live-service check.** None is possible —
  staging does not exist (RAID I-06) — and this change has no rendered surface.
- **No live Discord, Foundry or production-database contact.** Deliberate.
- **No mutation testing.** No mutation tool is configured; §10 is falsification
  and reproduction, not mutation coverage.
- **No formatter, linter or type checker.** None is configured (§9 row 8). This is
  reported as an environment fact, re-verified, not as a passing check.
- **No availability or load testing** of the new refusals; they occur before the
  first request.

---

## 14. Remaining risks and open maintainer decisions

1. **`_require_no_second_discord_authority` is defence in depth and is described
   as such.** It cannot classify a wrapper. If a reviewer prefers no residual
   check at all — on the ground that a check which cannot decide the general case
   invites being mistaken for one that can — it can be removed without weakening
   the boundary, which is the missing parameter. A decision either way is
   welcome; silence would leave the ambiguity this remediation exists to remove.
2. **Protected hooks versus a constructor capability token.** The handover offered
   both shapes. The protected-hook subclass was chosen as the smaller design:
   nothing is threaded through the entry point and no production type exists
   solely to be held by tests. The cost is that `_build_engine` and
   `_build_provider` are overridable by anything that subclasses
   `WebComposition`. Today only `tests/` does, and that is asserted; a reviewer who
   wants the stronger property should say so, and a token would then be the
   change.
3. **`app.state.composition` remains a diagnostic reference.** Replacing it now
   changes what an operator or a test *reads* without changing behaviour. That
   divergence is deliberate and asserted, but it is a divergence; a reviewer may
   prefer the attribute be removed entirely, at the cost of the introspection the
   suite and a future health surface use.
4. **`EngineHandle.owned` is always `True` in production.** The field exists for
   the test path. It is retained because ownership is a genuine lifecycle
   statement that `aclose()` must answer, and because inferring it from "was an
   engine supplied" is precisely what the removed parameter did.
5. **No production ASGI entry point exists yet** (§7). When one is added it must
   call `create_app(settings)` and must not grow a dependency parameter of its
   own; that obligation is recorded in the change-log entry.

---

## 15. Statement of status

- **P3.G1 is OPEN.** This is a remediation submission, not an acceptance.
- **RAID I-09 is OPEN.** Amended in the register; nothing here closes it.
- **RAID I-10 is OPEN.** Amended in the register; nothing here closes it.
- **P3.2 and P3.3 have not started** and must not start on this submission.
- A **fresh independent implementation review** and a **distinct security-focused
  pass** are required before dependent work continues. Passing tests are not a
  gate outcome, and this submission does not claim one.
