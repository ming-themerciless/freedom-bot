# Phase 3 P3.G1 — canonical settings-graph remediation

**Date:** 2026-08-16 · **Package:** P3.1 · **Owner:** Claude (implementing
Technical Lead) · **Change record:** C-P3.1-N · **Answers:** the P3.G1
canonical-settings handover in [`Handover information`](Handover%20information) ·
**Continues:** [`phase-3-p3-1-settings-construction-validation-remediation-submission.md`](phase-3-p3-1-settings-construction-validation-remediation-submission.md)
and [`phase-3-p3-1-n-23-exact-lease-remediation-submission.md`](phase-3-p3-1-n-23-exact-lease-remediation-submission.md)

**Status: submitted for fresh independent implementation and security review.
Nothing here is accepted, and this submission closes nothing.** P3.G1 remains
open. **RAID I-09 and I-10 both remain open.** P3.2 and P3.3 have not started —
no route, service or worker behaviour was written. Passing tests are evidence,
not acceptance.

---

## 1. The corrected result, first

A web process now has **one** settings authority at every production
configuration boundary, and the identity provider is one of them.

```python
# adapters/web/composition.py
self.settings = canonical_web_settings(settings)          # the one graph
self.provider = self._build_provider(provider_client, provider_double)
#   … which, for a production process, is:
#   build_provider(self.settings.discord, client=None)
```

```python
# adapters/web/app.py
settings = require_canonical_web_settings(composition.settings, subject="create_app")
_require_provider_from(composition, settings)
```

Three findings, three structural changes:

| # | Finding | What changed |
|---|---|---|
| 1 | An injected provider could reintroduce two authorities | The Discord adapter is **built by the composition** from its own `settings.discord`. It is not an argument. The remaining seam is an explicit test-adapter seam that refuses a real `DiscordIdentityProvider`, plus a transport-only `provider_client`. `create_app` requires the provider the application will use to hold **this** graph's provider settings |
| 2 | The adversarial machinery failed before the seam | The lie is engaged **after** the genuine constructor has validated the accepted value; construction, truthful and lying reads are counted separately, and each refusal case asserts the boundary read the hostile field exactly once in the lying phase. The environment case uses the exact documented variable names, with values actually outside the register |
| 3 | Graph completeness was tested circularly | The expected topology is derived from the dataclasses' own annotations, never from `CANONICAL_SETTINGS_GRAPH`, with a narrow container grammar that fails closed — and an undeclared settings type is now a **runtime** refusal rather than a silent leaf |

---

## 2. Finding 1 — root cause and structural fix

### 2.1 What was constructible

`WebComposition.__init__` canonicalised its `WebSettings` and then accepted a
ready-made `provider`, requiring no relationship between the two:

```python
# before
composition = WebComposition(
    settings=graph_a,
    provider=DiscordIdentityProvider(graph_b.discord),   # valid, and not graph A
)
app = create_app(composition=composition)
```

Both graphs individually valid. Both built through ordinary public constructors —
no private mutation, no `object.__new__`, no unsupported API. The application's
startup checks, middleware, cookies, digests and services then used A, while
R-03's authorization URL and R-04's token exchange were built from B's client id,
client secret, redirect URI, scopes, guild id, endpoints and timeout.

The security consequence is specific rather than theoretical. **S-05 is a
relational check** — the configured redirect URI must share the public origin —
and it is answered at the environment boundary against the graph the process
validated. A provider configured from a second, self-consistent graph satisfies
S-05 *on its own terms* and still sends callers to another origin's callback,
where the authorization code is delivered to whoever owns that host.

### 2.2 The fix, and why it is not a comparison

The split is removed rather than detected:

- `build_provider(settings.discord, client=…)` is the **one** production
  construction of the Discord adapter, and the composition calls it with its own
  canonical `settings.discord`;
- the injection seam is renamed to what it is. `provider_double` accepts a test
  double and **refuses a real `DiscordIdentityProvider`** (`isinstance`, so a
  subclass is refused too). No settings graph is compared, no secret is read, no
  private attribute is inspected — the refusal is a type rule;
- `provider_client` is the transport seam. Supplying it beside a double is a
  caller error rather than a silently ignored argument; and
- `DiscordIdentityProvider` takes its timeout and its no-redirect rule **from its
  settings**, applying both to an injected client, so a client cannot become a
  second place where `WEB_DISCORD_API_TIMEOUT_SECONDS` is decided.

A comparison was rejected deliberately, and the handover requires the reason to
be stated: two independently configured authorities that hold equal values today
are still two authorities, and a field comparison of `DiscordProviderSettings` is
a comparison of the client secret.

### 2.3 The one route left in, and what closes it

A `WebComposition` is an ordinary object; `composition.provider` can be
reassigned after construction. `create_app` therefore *requires* the property
rather than assuming it, by asking the provider a question that exposes nothing:

```python
def is_configured_from(self, settings: DiscordProviderSettings) -> bool:
    return self._settings is settings          # identity, never equality
```

A test double is not a Discord provider, carries no Discord configuration, and is
not asked.

---

## 3. Finding 2 — root cause and correction

`Lie.engaged` was set **before** `lying()` called the genuine subclass
constructor. The inherited `__post_init__` therefore read the hostile value while
the test object was being built, refused there, and ten cases never reached
`canonical_web_settings` or `WebComposition` at all. They proved that a settings
constructor refuses — which C-P3.1-L already proved — while claiming to prove
that the canonicalisation boundary refuses.

The harness now has three phases, recorded per read:

| Phase | Meaning | Asserted |
|---|---|---|
| `construction` | inside the inherited constructor | ≥ 1 read, so the accepted value **was** validated |
| `truthful` | after construction, before `engage()` | exactly 1 read where the boundary canonicalises |
| `lying` | after `engage()` | exactly 1 for a refusal case; **0** for an accepted-value case |

`lying()` asserts the subclass inherited the real `__post_init__` where the base
defines one, refuses to build an already-engaged lie, and never overrides
validation. A control case
(`test_the_accepted_value_survives_when_the_same_object_is_left_truthful`) shows
the same machinery, never engaged, produces a graph canonicalisation **accepts**
— so a refusal elsewhere is the lie being refused and not the harness.

The environment aggregation case used `WEB_RATE_LIMIT_OAUTH_STARTS_PER_IP`, which
no reader recognises (the documented name is `WEB_RATE_LIMIT_OAUTH_STARTS`), and
`WEB_MAX_REQUEST_BYTES=970004`, which is **inside** N-19's accepted range. Two of
its four intended problems were therefore never problems. It now supplies five
variables, spelled exactly as `.env.example` and the production readers spell
them, each with a sentinel value outside its accepted bound, and asserts that the
set of variables named by the aggregated refusal *equals* the set supplied — so
neither a silently accepted value nor an unexpected extra problem can pass.

---

## 4. Finding 3 — root cause and the independent contract

The completeness test iterated `CANONICAL_SETTINGS_GRAPH[WebSettings]`. A
settings-valued field added to a dataclass and omitted from the table removed
both the obligation and the check.

The expected topology is now derived by walking `typing.get_type_hints` from
`WebSettings`, and the supported grammar is written out and narrow:

| Annotation | Classification |
|---|---|
| a plain class | node if it is a dataclass, leaf otherwise |
| `tuple[X, ...]` | tuple-of-nodes if `X` is a dataclass, leaf otherwise |
| `X \| None`, other unions | leaf **only** if no member is a dataclass |
| anything else — `list`, `dict`, fixed-length tuple, optional node | **fails closed** as a reported problem |

`graph_problems(declared, root=…)` takes the mapping as an argument, so the
falsification cases hand it deliberately damaged copies. It reports: a
participating type with no entry (leaves included), an unclassified nested field,
a misclassified field, a declared field that is not a field of its owner, a
declared field that holds no node, and a declared type unreachable from the root.

The runtime half fails closed too. `canonical_settings` and `require_canonical`
looked their type up with `.get(expected, {})`, so an **undeclared** settings type
was canonicalised as though it nested nothing — outer shell rebuilt, any
overridable object left inside it. A missing entry is the absence of a statement,
not the statement that there is nothing to descend into, and
`_declared_nested_settings` now refuses it with `SettingsAuthorityError`. The
declared graph remains the runtime authority: no production code infers structure
from annotations.

---

## 5. The SQLAlchemy engine seam — reviewed, and deliberately left alone

The handover requires either a correction or a demonstration. The demonstration:

- **`settings.database.url` has exactly one reader in the web process** —
  `build_engine`, in `adapters/web/composition.py`. Verified by inspection:
  `grep -rn "settings\.database" adapters application tools main.py` returns four
  lines, all in that one file — `build_engine`'s pool read, its `database.url`
  argument, its own comment, and the class docstring recording this fact. So an injected
  engine cannot disagree with a second consumer of the same configured value,
  because there is no second consumer. That is precisely what was *not* true of
  the provider, whose seven configured values are read per call and are also read
  by S-05 at the environment boundary;
- **production construction is derived from the canonical graph.** `engine=None`
  is the production path: `build_engine(self.settings)` canonicalises
  `settings.database_pool` and passes N-53's four numbers to SQLAlchemy;
- **the checks run against the engine that serves requests.** `run_resource_checks`
  takes `composition.engine`, so S-14's revision comparison and S-15's credential
  query are made on the same connection pool every repository uses; and
- **the injected engine is infrastructure the suite already guards.** Tests supply
  the disposable-PostgreSQL engine that `tests/conftest.py` validates through
  `assert_disposable_target` and `verify_connected_unix_socket_target` before any
  destructive command.

It is recorded as a reviewer decision rather than settled by this submission: if
the review considers a supplied engine a configuration authority in the same
sense, the smallest correction would mirror the provider — an engine seam that
accepts only a connection factory the composition calls with its own
`settings.database` — and that is a change this handover's scope constraints did
not authorise on the strength of analogy alone.

---

## 6. Files changed, and why

| File | Change |
|---|---|
| `application/web/config.py` | `_declared_nested_settings` — the graph lookup now **fails closed** for an undeclared type, and both `canonical_settings` and `_require_canonical` use it. (The descending `canonical_settings`, `CANONICAL_SETTINGS_GRAPH`, `canonical_web_settings`, `require_canonical`, `require_canonical_web_settings` and `SettingsAuthorityError` were introduced by the in-flight work this handover reviews and are unchanged apart from that lookup.) |
| `adapters/web/composition.py` | `build_provider` — the one production construction of the Discord adapter, and a monkeypatchable seam so a test can prove a refusal happened *before* a provider existed. `WebComposition.__init__` takes `provider_client` and `provider_double` in place of `provider`; `_build_provider` refuses a real Discord provider as a double and refuses a transport beside one. Class docstring records why the engine is the one dependency supplied whole |
| `adapters/web/app.py` | `_require_provider_from` — the provider the application will use must hold this graph's `discord` settings, asked by identity |
| `adapters/web/discord_provider.py` | An injected client is transport only: the timeout comes from `api_timeout_seconds` and `follow_redirects` stays `False`. `is_configured_from` answers whether this adapter's authority **is** a given settings object, exposing nothing |
| `tests/web/conftest.py`, `tests/web/test_settings_construction_validation.py`, `tests/web/test_session_policy_numeric_validation.py` | The fixture and three call sites use `provider_double=`; one comment records why passing a double between compositions is not passing a provider |
| `tests/web/test_canonical_settings_graph.py` | Rewritten: the phase-based harness, the provider-authority section, the independent completeness contract with its falsification cases, and the corrected environment case. 46 cases |
| `docs/contracts/phase-3-configuration-and-dependency-contract.md` | Appended section: one canonical settings graph per web process, including the provider. No variable, value or refusal changed |
| `docs/contracts/phase-3-test-traceability.md` | TC-STRUCT-08 added; nothing rewritten or removed |
| `docs/project-management/{status,change-log,raid-register}.md` | Dated appends: status update, change record C-P3.1-N, amendments to I-09 and I-10 — both left **open** |

---

## 7. The exact production construction path after the fix

```text
main / entry point
  └─ WebSettings.from_environment(os.environ)      # S-01…S-11, one ConfigurationError
       └─ create_app(settings)                     # exactly one authority
            └─ WebComposition(settings=settings)
                 ├─ self.settings = canonical_web_settings(settings)
                 │     └─ canonical_settings descends CANONICAL_SETTINGS_GRAPH:
                 │        every field read once, exact base types rebuilt through
                 │        the constructors that hold the accepted register
                 ├─ self.engine   = build_engine(self.settings)          # N-53
                 ├─ self.envelope = Envelope(self.settings.encryption)
                 └─ self.provider = build_provider(self.settings.discord)
                        └─ DiscordIdentityProvider(require_canonical(…))
            ├─ settings = require_canonical_web_settings(composition.settings)
            ├─ _require_provider_from(composition, settings)   # identity, not equality
            ├─ run_resource_checks(settings, composition.engine)   # S-12, S-14, S-15
            └─ middleware, cookies, digests, routes — all from `settings`
                 └─ per request: composition.services(connection)
                      └─ OAuthLoginService / BreakGlassService
                           └─ require_canonical_web_settings(settings)
```

`app.state.settings is app.state.composition.settings`, and every service,
repository, middleware object and the provider read from that one object.

---

## 8. Why the fake provider and the injected engine are not second authorities

| Seam | Second authority? | Why |
|---|---|---|
| `provider_double` | **No** | It is refused if it is a `DiscordIdentityProvider` (or a subclass). `FakeDiscordProvider` holds no client id, secret, redirect URI, scopes, guild id or endpoint — it answers from a script. There is nothing for it to disagree with the graph about, and it cannot be used to smuggle a real adapter in |
| `provider_client` | **No** | An `httpx.AsyncClient` supplies transport. Every URL the adapter uses is absolute and built from settings, so a client `base_url` is never consulted; the timeout and `follow_redirects` are set from the canonical provider settings when the client is accepted |
| `engine` | **No**, and §5 states the demonstration | `settings.database.url` has exactly one reader in this process, so there is no second consumer to disagree with; production derives the engine from the canonical graph, and the startup checks run against the engine that serves requests |

---

## 9. Regression tests, mapped to every required property

All in `tests/web/test_canonical_settings_graph.py` unless noted.

### 9.1 Finding 1 — the five required proofs

| Required property | Test |
|---|---|
| 1. A composition cannot use graph A while a **real** provider uses valid graph B | `test_a_composition_refuses_a_real_provider_built_from_another_graph` — a genuine `DiscordIdentityProvider` from a second complete configuration, through the ordinary public constructor; the refusal is typed, and the removed `provider=` keyword is proved gone |
| 2. The authorization URL and token-exchange inputs use the composition's one graph | `test_the_composition_builds_its_provider_from_its_own_canonical_graph` — hostile `discord.redirect_uri`, engaged after composition; the URL and the posted `redirect_uri`/`client_id`, captured over `MockTransport`, are the canonical ones and the caller's object is never read again. Also `test_the_provider_is_built_from_the_canonical_provider_settings` |
| 3. Redirect-origin startup validation and the OAuth provider cannot see different redirect URIs | `test_startup_validation_and_the_oauth_provider_see_one_redirect_uri` — a second **self-consistent** graph (its own public origin, allowed hosts, redirect URI and relying party, so S-05 accepts it on its own terms) cannot become the application's provider |
| 4. The supported fake-provider seam still works | `test_the_test_adapter_seam_still_works_and_stays_a_double` — the double answers R-03 through the real application; plus the whole 653-test portal suite, which uses it in every fixture |
| 5. Secrets absent from refusals, representations, logs and test output | `test_no_provider_refusal_or_representation_renders_a_secret`, and value-level assertions elsewhere never render a secret-bearing container |
| Client injection cannot become a settings authority | `test_an_injected_client_supplies_transport_and_never_configuration` |

### 9.2 Finding 2 — the harness proves the boundary

| Required property | Test |
|---|---|
| Hostile object genuinely valid at construction; inherited `__post_init__`; truthful reads recorded separately | `lying()` and `Lie` themselves assert it, exercised by every case; `test_the_graph_is_rebuilt_from_exactly_one_read_of_every_field` asserts the construction and truthful counts explicitly |
| Refusal at the intended boundary, read exactly once in the relevant phase | `test_a_wrong_type_or_out_of_register_later_answer_refuses_at_canonicalisation` (8 parametrised register fields), `test_a_member_that_lies_out_of_register_refuses_before_anything_holds_it` |
| …and before the engine, provider, application or other consumer holds it | the same case, with `create_engine` **and** `build_provider` monkeypatched and proved never called |
| Accepted later answers: behaviour and durable state use the validated value, and the caller's object is never read again | OAuth transaction expiry and its stored row; the repository's derived idle bound; the break-glass challenge expiry and relying party; the login-transaction cookie's `Max-Age`; the session cookie name; N-19's body bound; N-34's hop count; the recorded client digest; the sealed verifier's key version — nine cases, each asserting `lie.lying_reads == 0` |
| No settings constructor weakened; a constructor failure never counted as boundary proof | no production constructor changed; `test_the_accepted_value_survives_when_the_same_object_is_left_truthful` is the control |
| Environment aggregation with the exact documented names | `test_the_environment_still_aggregates_every_problem_into_one_redacted_refusal` — five variables, one error, five names, no sentinel values, and the named set proved *equal* to the supplied set |

### 9.3 Finding 3 — completeness, independently

| Required property | Test |
|---|---|
| Every participating type has an entry, leaves included | `test_the_declared_graph_states_the_whole_topology_the_dataclasses_have` |
| Every settings-valued field and supported tuple is classified | same, from the derived topology |
| Every declared field exists on its owner with the expected shape | same, via `graph_problems`' reverse checks |
| No undeclared nested object survives inside an exact-base outer dataclass | `test_canonicalisation_refuses_a_settings_type_the_graph_does_not_declare` (runtime), plus the completeness contract (static) |
| Expected topology independent of the mapping | derived from `typing.get_type_hints`; `graph_problems` never reads the module constant unless it is handed it |
| Falsification / mutation demonstration | `test_deleting_one_nested_classification_makes_the_completeness_check_fail`, `test_deleting_a_whole_type_entry_makes_the_completeness_check_fail`, `test_an_unclassified_nested_field_in_a_synthetic_graph_is_reported`, and the recorded run in §11 |
| Unknown containers fail closed | `test_an_unsupported_container_fails_closed_rather_than_reading_as_a_leaf` |

---

## 10. Verification — fresh results, in the required order

All runs are from after the final edit. Nothing is recycled. Every database run
used the guarded disposable target.

| # | Command | Result |
|---|---|---|
| 1 | `./venv-web/bin/python -m pytest tests/web/test_canonical_settings_graph.py -q` (**no** `TEST_DATABASE_URL`) | **24 passed, 22 skipped**, 0 failed — every non-database case passes and every skip names the missing disposable database |
| 2 | `TEST_DATABASE_URL='postgresql+psycopg:///freedom_test' ./venv-web/bin/python -m pytest tests/web/test_canonical_settings_graph.py -q` | **46 passed, 0 failed, 0 skipped** |
| 3 | `… -m pytest tests/web/test_provider_classification.py tests/web/test_oauth_flow.py tests/web/test_oauth_completion_binding.py tests/web/test_oauth_refusal_audit.py tests/web/test_break_glass_login.py tests/web/test_break_glass_escalation.py tests/web/test_security_controls.py tests/web/test_structural_guards.py tests/web/test_settings_construction_validation.py -q` | **403 passed, 0 failed, 0 skipped**, 13 warnings |
| 4 | `TEST_DATABASE_URL='postgresql+psycopg:///freedom_test' ./venv-web/bin/python -m pytest tests/web -q` | **653 passed, 0 failed, 0 skipped**, 16 warnings, 25.24 s |
| 5 | `TEST_DATABASE_URL='postgresql+psycopg:///freedom_test' ./venv/bin/python -m pytest -q` | **2260 passed, 0 failed, 0 skipped**, 1 warning, 134.92 s |
| 6 | `APP_ENVIRONMENT=test DATABASE_URL='postgresql+psycopg:///freedom_test' ./venv/bin/alembic check` | **`No new upgrade operations detected.`** One pre-existing `SAWarning` from `migrations/env.py:133`, unrelated and unchanged |
| 7 | `./venv/bin/python -m compileall -q application adapters tools tests` and the same under `./venv-web/bin/python` | Both **OK**; both interpreters are CPython 3.12.3 |
| 8 | Formatter / linter / type checker | **None configured** — re-verified, not assumed: no `pyproject.toml`, `setup.cfg`, `.ruff.toml`, `.flake8`, `mypy.ini`, `tox.ini` or pre-commit configuration exists, and neither virtualenv has `ruff`, `mypy`, `flake8` or `black` |
| 9 | `git diff --check` | **Clean**, exit 0 |
| 10 | `sha256sum -c docs/review/phase-3-visual-freeze-manifest.sha256` | **14 `OK`, 0 non-`OK`** |
| 11 | Diff review for secrets, unsafe logs, generated artifacts, unrelated edits, migration/schema changes | No secret, no `.env` read, no generated file, no migration touched, no schema change; the diff is the files in §6 |

**Warnings.** The portal's warnings are the pre-existing `httpx` per-request
cookie `DeprecationWarning`s; the bot suite's single warning is the pre-existing
`audioop` deprecation from `discord.player`. Neither is new.

**Database target.** `postgresql+psycopg:///freedom_test`, the guarded disposable
target: it resolves through `assert_disposable_target`, `current_database()` is
`freedom_test`, and the connection is a Unix-domain socket. **No production
database, live Discord application, guild or Foundry instance was contacted.**

---

## 11. Falsification runs — recorded, not asserted

Each mutation was applied to the worktree, run, and reverted; the four files
touched were checksummed before and after and are **byte-identical** (`sha256sum
-c`: 4 × `OK`).

| # | Mutation | Result |
|---|---|---|
| 1 | The mismatched-provider construction path restored (the `isinstance` refusal neutralised and `_require_provider_from` removed) | **3 failed, 3 passed** of the provider selection: `…refuses_a_real_provider_built_from_another_graph`, `…startup_validation_and_the_oauth_provider_see_one_redirect_uri` and `…no_provider_refusal_or_representation_renders_a_secret` fail. Reported honestly: the three that still pass are the ones about *which settings the built provider uses*, which the mutation does not affect |
| 2 | The premature-engagement harness restored (the lie engaged before the genuine constructor) | **25 failed, 21 passed** of 46. The boundary-proof cases reject that false evidence rather than passing on it |
| 3 | `"discord": DiscordProviderSettings` deleted from `CANONICAL_SETTINGS_GRAPH` | The independent completeness test **fails** (`WebSettings.discord holds a settings node and is not classified in the graph`) — **while the old-style, self-referential assertion in `test_every_member_of_the_canonical_graph_is_the_exact_base_type` still passes**, which is finding 3 demonstrated rather than described |
| 4 | The unrecognised environment-variable name and the in-range sentinel restored | The aggregation case **fails**, naming three problems where five were supplied |

---

## 12. Security and secret handling

- **Strictly a tightening, at startup rather than per request.** Every new refusal
  is a `SettingsAuthorityError` (a `TypeError`) raised while an application is
  being built. No route, authorization decision, audit behaviour, session bound,
  rate limit, cookie attribute or error rendering changed.
- **No secret is rendered, compared, decoded or converted.** Canonicalisation
  moves the same `bytes` object; `SecretKey` and `EncryptionKey` keep the
  `__repr__` that redacts. The new refusals name a **type or a field path** and
  never a configured value; `test_no_provider_refusal_or_representation_renders_a_secret`
  and `test_canonicalisation_renders_no_key_material` assert it with recognisable
  material.
- **The OAuth flow's configuration is now provably the validated one.** The client
  id, client secret, redirect URI, scopes, guild id, endpoints and timeout used by
  the authorization URL and the token exchange are the composition's canonical
  `settings.discord` — the object S-05 and S-06 were answered on.
- **Transport cannot loosen a control.** An injected client cannot lengthen the
  provider timeout, and cannot follow a redirect with the token-exchange body
  (which carries the client secret) attached.
- **No `.env`, credential, token or player data was read, printed or modified.**
  The disposable `freedom_test` database was the only database contacted.

---

## 13. What did not change

- **No accepted numeric value moved.** No `PolicyBound`, ceiling, floor or exact
  value was edited.
- **No environment-variable contract change.** Nothing added, renamed or removed;
  `.env.example` is untouched. Correcting a test's *spelling* of
  `WEB_RATE_LIMIT_OAUTH_STARTS` is not a contract change.
- **No schema, migration or database change.** No migration file was opened for
  editing; `alembic check` reports no new upgrade operations.
- **No deployment topology change.** No systemd unit, dependency, virtualenv or
  runtime grant touched.
- **Visual freeze intact.** 14 manifest entries verified `OK`.
- **Public behaviour unchanged** for every valid configuration: a graph built by
  `WebSettings.from_environment` is already exact-base, so canonicalising it
  removes nothing (`test_a_settings_graph_from_the_environment_is_already_canonical`).

---

## 14. Checks not run, and why

- **No browser, staging, device or live-service check.** None is possible —
  staging does not exist (RAID I-06) — and this change has no rendered surface.
- **No live Discord, Foundry or production-database contact.** Deliberate; the
  provider evidence uses `httpx.MockTransport` and the disposable database.
- **No mutation testing.** No mutation tool is configured; §11 is falsification of
  the previous implementation and of the previous test harness, not mutation
  coverage.
- **No formatter, linter or type checker.** None is configured (§10 row 8).
- **No availability or load testing** of the new startup refusals; they occur
  before the first request and cannot affect steady-state behaviour.

---

## 15. Remaining risks and open maintainer decisions

1. **The engine seam** (§5) is left as a supplied infrastructure dependency with
   its reasoning stated. Reviewers are asked to accept or reject that reasoning
   explicitly.
2. **`WebSettings` and `DiscordProviderSettings` still have no construction-time
   validation.** They are outside the five types I-10 names and outside this
   handover's scope. The canonical graph makes a *lying* instance of either
   harmless at a boundary; it does not make an invalid one unconstructible. This
   was already recorded by C-P3.1-L and is repeated rather than quietly dropped.
3. **The relational refusals (S-02, S-05, S-09) necessarily stay at the
   environment boundary**, because no sub-dataclass carries both sides. What
   changed is that the value they were answered on is now the value every
   consumer uses.
4. **A future settings type must be declared in `CANONICAL_SETTINGS_GRAPH`.** It
   now fails closed at runtime and the completeness test names it, which is the
   intended behaviour rather than a latent breakage — but it is an obligation on
   the next package that adds one.
5. **`provider_double` names a test seam in production code.** The alternative —
   a separate composition subclass for tests — was judged more indirection than
   the property is worth, but it is a design point a reviewer may reasonably
   disagree with.
6. **The residuals recorded by C-P3.1-L and C-P3.1-M are unchanged**: N-09/N-10
   have no P3.1 route consumer, N-21/N-22 have no consumer at all,
   `WEB_WEBAUTHN_USER_VERIFICATION` and `WEB_RECOVERY_GRANT_MINUTES` have no
   runtime consumer, and the worker's consumers are P3.3's.

---

## 16. Statement of status

This remediation is **submitted for fresh independent implementation review and a
distinct security-focused review**. It does not close P3.G1, RAID I-09 or RAID
I-10, and it is not a maintainer acceptance of anything. P3.2 and P3.3 have not
started. No claim in this document should be read as an acceptance; the evidence
is the runs recorded in §10 and §11 and the tests they exercised.
