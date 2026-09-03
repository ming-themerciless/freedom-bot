# Phase 4 — Shared application services · submission record

## Post-gate constructor remediation — final disposition, 2026-09-02

Phase 4 remains approved. A later broad repository review found malformed-input
paths in Phase 4's command boundary. Claude supplied two bounded corrections and
Codex independently reviewed them.

- **P4-PG1 Closed:** Discord-user IDs require positive non-boolean integers.
- **P4-PG2 Closed:** expected-version aggregate types require text.
- **P4-PG3 Closed:** service-principal IDs require text; resolution and authority
  remain the execution-time answer of `LedgerPrincipalPort`.
- **P4-PG4 Closed:** `validate_key()` establishes text before value rules and
  preserves `invalid_request_key` at every caller without coercion.
- **P4-PG5 Closed:** malformed stored receipt command names become
  `StoredReceiptUnreadable`; a spent key is never re-executed or answered with
  an invented receipt.

The authoritative final review is
[`phase-4-post-gate-r3-independent-review.md`](phase-4-post-gate-r3-independent-review.md).
Peter Duscha accepted that disposition on 2026-09-02. Phase 4 is approved and
closed, and Package 5 preparation may proceed subject to Package 5's own
readiness and authorization controls. This closure authorizes no Package 5
implementation, migration, deployment or cutover.

## Acceptance Authority decision — 2026-08-29

**Approved.** Peter Duscha accepted the Phase 4 dependency-direction and domain-
correctness gate after Codex's second independent re-review returned no Blocking
or Important findings. P4-R4 and P4-R5 are Closed; the earlier P4-R1, P4-R2 and
P4-R3 remediations remain accepted review evidence. D-04 is Closed.

This decision accepts the shared money/resource, ledger, authorization,
idempotency, concurrency and audit/correlation foundation as safe to build on.
It releases Phase 5 package planning subject to every package's own definition
of ready, predecessor decisions, independent review and cutover gate. It does
**not** migrate character data, make PostgreSQL authoritative for a Phase 5
field, change `/info`, deploy a mutation, retire Sheets, or authorize permanent
character-data mutation through Discord. During migration the Freedom bot may
temporarily consume shared services; after the platform is fully functional and
the separately gated bot retirement completes, Discord remains the identity,
membership, role, event, notification and attendance integration, not a
character-mutation interface.

Independent verification against the accepted tree: focused Phase 4 **415
passed**; bot **2929 passed, 0 skipped**; web **2824 passed, 80 expected skips**;
Foundry **171 passed**; `compileall` under both interpreters and `git diff
--check` clean. No formatter, linter or type checker is configured.

## Independent re-review disposition — 2026-08-29

**Changes requested. The Phase 4 gate remains deferred; D-04 remains Open and
no Phase 5 work is released.** Codex re-reviewed Remediation R1 and found that
the original transaction-visibility and service-principal mechanisms are
materially corrected, and that occurrence time and resolved caller identity are
now bound into the idempotency digest. Two defects remain:

1. **P4-R4 — Blocking, authorization boundary.**
   `LedgerCommandService.compensate()` reads `ledger.get(transaction_id)` and
   returns a distinguishable missing-transaction refusal before resolving the
   caller's current authority. Authority must be resolved before the lookup,
   without introducing a second resolution whose answer could change between
   lookup and posting.
2. **P4-R5 — Important, audit/correlation correctness.** A
   `CommandEnvelope` and supplied `LedgerTransaction` may carry different
   correlation IDs. Receipt and audit use the envelope ID while ledger history
   retains the transaction ID; the digest excludes both as attempt metadata, so
   the contradiction is neither refused nor detected on retry.

P4-R1 and P4-R2 are remediated. P4-R3's requested time/caller digest correction
is remediated; P4-R5 is a separate residual correlation-contract defect found
during re-review.

Independent evidence: focused Phase 4 **376 passed**; web **2824 passed, 80
expected skips**; Foundry **171 passed**; `compileall` under both interpreters
and `git diff --check` clean. The bot suite completed with **2887 passed, 2
skipped and 1 failure**: the backup/restore drill detected missing disposable-
test-database schema/role grants. That is environment evidence, not a Phase 4
behavior failure, and must be restored and rerun rather than reported as green.

No maintainer policy or architecture decision is needed for P4-R4 or P4-R5.
Remediation R2 and independent re-review are required before a gate
recommendation.

## Independent review disposition — 2026-08-29

**Changes requested. The Phase 4 gate is deferred; D-04 remains Open and no
Phase 5 work is released.** Codex reviewed the submitted tree and returned:

1. **P4-R1 — Blocking, atomicity/concurrency.** The composite unit of work
   publishes the in-memory ledger, releases its lock, and then commits the
   durable receipt/audit transaction. A concurrent posting can become visible
   before that durable commit finishes. If the first commit then fails,
   `retract(published)` deletes the last N transactions rather than the exact
   failed transaction, so it can delete the concurrent winner and retain the
   failed posting. The submission's claim that another caller cannot observe
   the intermediate publish is false.
2. **P4-R2 — Blocking, authorization.** `LedgerCommandService._attribute()`
   accepts every `CommandCaller` carrying a nonblank `principal_id` as an
   authorized service principal. No application-layer port verifies that the
   principal exists, is current, or holds the ledger-command scope. A direct
   service caller can therefore manufacture authority.
3. **P4-R3 — Important, idempotency/audit correctness.** `_digest()` omits
   command-defining facts including `occurred_at` and caller identity. Reuse
   with a different historical time or by another principal can consequently be
   treated as an identical retry rather than conflicting reuse.

Independent verification run:

```sh
export TEST_DATABASE_URL='postgresql+psycopg:///freedom_test'
/opt/discord-bots/venv/bin/python -m pytest -q \
  tests/test_p4_domain_quantities.py tests/test_p4_commands.py \
  tests/test_p4_ledger_domain.py tests/test_p4_ledger_service.py \
  tests/test_p4_idempotent_execution.py
# 326 passed in 2.81s
git diff --check
# clean
```

The passing run is retained as evidence but does not cover the counterexamples.
The remediation instructions are in `docs/review/Handover information`. All
three findings require remediation and independent re-review before Peter is
asked to decide the gate.

**Remediation R1 was delivered on 2026-08-29 and is recorded at the end of this
document** — see *Remediation R1 — P4-R1, P4-R2, P4-R3*. It closes no finding.
The three findings remain Open pending Codex's re-review, D-04 remains Open, the
gate remains deferred, and no Phase 5 work is released. The record above and
below this note is the original review history and is unchanged.

Running submission for the Phase 4 package. Built incrementally as each work
package completes; the handback statement the gate reads is assembled here.

Package plan: [`phase-4-package-plan.md`](phase-4-package-plan.md)
Implementing agent and working Technical Lead: Claude
Independent Reviewer: **Codex** (named 2026-08-28; has not implemented this package)

Status: **Independent review completed with changes requested: P4-R1 and P4-R2
Blocking; P4-R3 Important. Remediation and re-review are required. The Phase 4
gate is deferred, D-04 remains Open, and no Phase 5 work is released.**

Decisions this package implements: **OD-48** (no ledger table, no migration),
**OD-49** (integer thousandth-days, refuse rather than round, preserve
rendering), **OD-50** (integer copper only; denomination counters stay a legacy
representation), **OD-51** (characterize the `/sale` and `/lc` float defects,
defer the fix), **OD-52 as finally amended** (Phase 4 creates neither an
`/info` rewrite nor a temporary wallet query/Sheet adapter; package 5.2
introduces the query with its real character-page consumer).

---

## Pre-implementation baseline — 2026-08-28

Measured against the unchanged tree before any edit, as assumption **A-P4-2**
and stop condition 5 require. Recorded in full in the package plan §16.

| Suite | Result |
|---|---|
| Bot | 2447 passed, 0 skipped |
| Web | 2824 passed, **80 skipped** — the established figure; all 80 are the two permission-matrix modules' permitted cells, **none a database skip** |
| Foundry module | 171 pass, 0 fail |

---

## WP-0 — Characterization of Sheet-era money and resource behaviour

**Complete.** One new file, `tests/test_p4_characterization.py`, **36 tests**.
No production file was modified. Bot suite after WP-0: **2483 passed, 0
skipped** — the baseline's 2447 plus these 36, with no other movement.

### What it pins

| Area | Pinned |
|---|---|
| Visible output | `Resource.get_summary` exact text; positive-only denominations; Moradinium unconditional; downtime opt-in; the empty-wallet sentinel; `render_actor_summary` composition and the conditional Bastion block |
| OD-50 | Two wallets holding the same 100 cp print differently (`10sp` vs `1gp`), so the rendering is **not derivable** from a copper total; plus the copper totals themselves, so the new typed value is checkable against today's counters |
| OD-49 | Downtime loads as a Python `float` and renders as `5.0 days`; a four-decimal value finer than the accepted thousandth-day is accepted silently; an unparseable cell becomes `0.0` with no report; `safe_int` truncates rather than rounds |
| OD-52 | `/info` defers, sends exactly one **non-ephemeral** follow-up whose body is `render_actor_summary`, matches names case-insensitively, reports an unknown character ephemerally, refuses an ambiguous name naming the rows, and writes nothing |
| Refusals | Downtime five-day increments and availability; insufficient Moradinium; a negative result on `add` — each with no mutation on the failing path |

### Deliberately pinned defects

These tests record behaviour that contradicts an accepted invariant. Each names
its decision record and owning package in its own docstring so it cannot later
be read as accepted policy — risk **R-P4-2**.

- Downtime as a float, sub-unit precision accepted, unparseable values coerced
  to defaults (**OD-49**; column I is package **5.5**).
- A **negative** denomination is silently suppressed from the summary rather
  than shown or refused — the player sees a wallet that omits it.
- `Resource.sale` and `Lifestyle.pay_for_weeks` compute in binary floating point
  (**OD-51**; packages **5.7** and **5.3**). Their existing coverage in
  `tests/test_resource.py` is their characterization; Phase 4 changes neither.

### Falsification

Each mutation was applied to the production tree, the named test run, and the
tree restored and **verified by SHA-256** against the pre-mutation checksums.
No mutation survives in the submitted tree.

| # | Mutation | Result |
|---|---|---|
| 1 | `Resource.get_summary` normalizes coins to canonical denominations before rendering (reverses OD-50) | **Failed as required** — `test_equal_value_wallets_print_differently`: `assert '**Money:** 1gp' == '**Money:** 10sp'` |
| 2 | `/info` sends its summary with `ephemeral=True` | **Failed as required** — `test_info_defers_then_sends_the_summary_non_ephemerally`: `assert True is False` |
| 3 | `/info` calls `actor.save_to_sheet()` before responding | **PASSED — the test did not detect it.** See below |
| 4 | `Resource.load_from_sheet_data` loads downtime with `safe_int` (reverses OD-49's unit) | **Failed as required** — two tests: `assert False is isinstance(5, float)` and `assert 12 == 12.3456` |

**Mutation 3 is reported as a finding against my own test, not omitted.** Stop
condition 7 of the package plan requires exactly this disclosure. The original
`test_info_writes_nothing` watched only `connectors.sheets.batch_update`.
`Actor.save_to_sheet` diffs against the cells it loaded and **returns before
calling `batch_update` when nothing changed**, so an injected `save_to_sheet()`
in a read-only command reaches no Sheets API and the assertion held. The test
was measuring a weaker property than it claimed.

It now watches every write path on the model — `save_to_sheet`, `sheet_updates`,
`verify_sheet_row` — **and** the Sheets API, and fails if any is touched. The
identical mutation was re-injected against the corrected test and failed as
required: `assert ['save_to_sheet'] == []`. The corrected test also asserts that
exactly one follow-up was sent.

### Commands run

```sh
export TEST_DATABASE_URL='postgresql+psycopg:///freedom_test'
/opt/discord-bots/venv/bin/python -m pytest -q tests/test_p4_characterization.py   # 36 passed
/opt/discord-bots/venv/bin/python -m pytest -q -rs tests/test_*.py                 # 2483 passed
```

The web and Foundry suites were not re-run for WP-0: it adds one bot-suite test
file and modifies no production code, so neither can be affected. Both are re-run
against the tree actually submitted, and those figures — not these — are the ones
the gate reads.

### Not done in WP-0

No production code changed. No domain object, protocol, ledger, idempotency
path exists yet; those are WP-1 to WP-4. Both command routing and the temporary
Sheet query/adapter are outside Phase 4 under final OD-52.

---

## WP-1 — Framework-free money and resource value objects

**Complete.** Three new `domain/` modules and two new test modules. **144 new
tests**; bot suite **2627 passed, 0 skipped** (2483 after WP-0, plus 144).

### Files added

| File | Contents |
|---|---|
| `domain/quantities.py` | `QuantityError` and `whole_number()` — the single definition of what counts as a valid quantity |
| `domain/money.py` | `Money` (signed integer copper), the platform's rate constants, `sum_money()` |
| `domain/resources.py` | `Moradinium` (unit: one piece), `Downtime` (unit: one thousandth-day), `DOWNTIME_UNITS_PER_DAY` |
| `tests/test_p4_domain_quantities.py` | 120 tests — construction, conversion, arithmetic, refusal, immutability |
| `tests/test_p4_domain_isolation.py` | 21 tests — the dependency guard |

No existing file was modified.

### Design decisions a reviewer should check

**`bool` is refused explicitly.** `isinstance(True, int)` is `True`, so
`Money(True)` would otherwise mean one copper piece. A flag arriving where an
amount belongs is a programming error and reading it as `1` hides it.

**`float` is refused unconditionally, including integral values**, and `Decimal`
with it. A rule that accepts `5.0` but not `0.1 + 0.2` holds exactly for the
values a developer tries by hand. Conversion from an external decimal is an
adapter's job, where the rounding policy is visible.

**`Money` has `from_denominations` but deliberately no decomposition back.**
That asymmetry *is* OD-50: coin counts go in because the Sheet stores four
counters, and nothing comes back out, because rendering a canonical
decomposition would silently rewrite what many players' wallets look like.
Rendering belongs to the adapter holding the stored counters.

**Quantities may be negative.** A ledger entry is signed and debt is a real game
concept (RC-D4); the no-negative-*balance* rule belongs to whatever holds a
balance. Enforcing it in the number would make the debit half of a transfer
inexpressible. WP-3 owns that rule.

**`Money * fraction` is refused.** A percentage of a price needs a stated
rounding policy, and that policy belongs with the rule — which is exactly the
defect OD-51 records in `Resource.sale`.

**The dependency guard is an allowlist, not a denylist.** Every top-level import
in `domain/` must be the standard library or `domain` itself, so a framework
nobody thought to ban still fails. It reads source with `ast` rather than
importing, because an import inside a function or a `TYPE_CHECKING` block is
still a dependency. A second check bans environment reads, which the allowlist
would let through since `os` is standard library. A third asserts the guard
still matches the Phase 4 modules, so it cannot pass vacuously by matching
nothing.

**The rate constants are pinned against `models/exchange.py`**, so the new
domain cannot drift from the conversion the live bot performs.

### Falsification

Six mutations, each applied to the production tree and reverted.

| # | Mutation | Result |
|---|---|---|
| 5 | `whole_number` accepts integral floats | **Failed as required** — 21 tests |
| 6 | the `bool` guard is removed | **Failed as required** — 14 tests |
| 7 | `Money.__add__` absorbs a `Moradinium` | **Failed as required** — `test_mixing_resource_types_is_refused` |
| 8 | `DOWNTIME_UNITS_PER_DAY` becomes 100 (reverses OD-08) | **Failed as required** — 8 tests |
| 9 | `domain/money.py` imports `sqlalchemy` | **Failed as required** — *"money.py imports ['sqlalchemy'], which is neither the standard library nor `domain`"* |
| 10 | `domain/money.py` reads `os.environ` for a rate | **Failed as required** — *"money.py reads the environment (['environ'])"* |

**A process failure in the restore path, reported rather than omitted.** These
three `domain/` modules are new and **untracked**, so the `git checkout` used to
revert each mutation could not restore them and silently failed — leaving the
mutations on disk after the run. They were reversed explicitly and the tree
verified byte-identical to its pre-mutation state by **SHA-256 against
checksums taken before the first mutation**. All three match. The three files
are now copied to the scratchpad so later mutations have a real restore path.
The mutation results above stand — each ran against the intended tree — but the
verification that matters is the checksum comparison, not the `git checkout`.

### Commands run

```sh
/opt/discord-bots/venv/bin/python -m pytest -q tests/test_p4_domain_quantities.py tests/test_p4_domain_isolation.py   # 141 passed
/opt/discord-bots/venv/bin/python -m pytest -q -rs tests/test_*.py                                                   # 2627 passed, 0 skipped
/opt/discord-bots/venv/bin/python     -m compileall -q domain …                                                      # OK
/opt/discord-bots/venv-web/bin/python -m compileall -q domain                                                        # OK
```

`domain/` compiles under **both** interpreters, which is the practical form of
the claim that it depends on neither runtime's packages.

### Not done in WP-1

No command protocol, ledger or idempotent executor yet—WP-2 to WP-4. Nothing
consumes these value objects yet, which is why the guard test
asserts they exist rather than inferring it from a caller.

---

## WP-2 — Application command boundaries and typed failures

**Complete.** One new module, `application/commands.py`, and **61 tests** in
`tests/test_p4_commands.py`. No existing file was modified.

### What it defines

| Type | Carries |
|---|---|
| `CommandCaller` | The caller's **identity** and the surface it arrived on: exactly one of a Discord snowflake or a service-principal id, plus an `AuditSource` |
| `ExpectedVersion` | The aggregate type, the aggregate id and the version the caller read before deciding |
| `CommandEnvelope` | Caller, idempotency key, correlation id, optional expected version — and `require_expected_version`, which refuses a command whose precondition is missing or is a version of something else |
| `CommandReceipt` | The stable result: command name, correlation id, resulting aggregate version, flat JSON-safe facts, and a `duplicate` flag that is **not** stored |
| `InvalidEnvelopeError`, `StoredReceiptUnreadable` | The two typed failures, each carrying a stable code |

Reuse rather than parallel mechanisms: the key is validated by
`application.idempotency.validate_key` and its published `invalid_request_key`
code is preserved; the expected-version failure at execution is the existing
`application.errors.ConcurrencyConflictError`; the transaction boundary is the
existing `UnitOfWork` shape.

### Design decisions a reviewer should check

**The envelope carries authority as an identity, never as a privilege.** There
is no `guild_council` field and a test asserts there never becomes one.
`application/authorization.py` rule 2 is that permission is re-resolved when the
work is done; an envelope field carrying a resolved capability would let a
caller present a privilege it held a minute ago, or never held, since the
envelope is built from the request. The service asks the port instead.

**`ExpectedVersion` names its aggregate.** A bare integer precondition can be
checked against the wrong thing and still pass, and the failure mode is a stale
write that reported success. `require_expected_version("ledger_book", book_id)`
refuses a version of another aggregate and refuses a missing one.

**A receipt round-trips through its stored payload.** `as_payload()` is exactly
what is written to `idempotency_keys.response`; `from_payload()` is exactly what
a retry is answered from. `duplicate` is excluded from the payload because it
describes *this call* rather than the operation — storing it would make the
first caller's own receipt claim to be a replay of itself.

**A receipt fact may not hold a `float`, a nested structure, bytes or a UUID
object.** A receipt is the last place a binary float should be able to enter the
platform, and a value that would not survive the JSON round trip unchanged is
refused at the call site rather than at the driver.

**No query protocol is defined.** The convention is recorded in the module
docstring — a query takes the caller and its own inputs, spends no key, has no
expected version, writes no receipt, and is authorized when it runs. Under the
final OD-52 amendment package 5.2 introduces the typed wallet query with its
production adapter and character-page consumer; an interface written here to
satisfy the word "query" would have exactly one caller, its own test.

### Not done in WP-2

No adapter is wired to this envelope. Its Phase 4 consumers are WP-3 and WP-4.

---

## WP-3 — Ledger domain and concrete transaction execution

**Complete.** Two new modules and one new adapter package: `domain/ledger.py`,
`application/ledger.py` and `adapters/ledger/`. **78 tests** in
`tests/test_p4_ledger_domain.py` and **50** in `tests/test_p4_ledger_service.py`.
`tests/test_p4_domain_isolation.py` gains `ledger.py` (21 → 23 tests); no other
existing file was modified.

### Files added

| File | Contents |
|---|---|
| `domain/ledger.py` | `ResourceKind`, `AccountKind`, `AccountRef`, `LedgerEntry`, `LedgerTransaction`, `LedgerError`, `compensate()` |
| `application/ledger.py` | `LedgerRepository` and `LedgerUnitOfWork` protocols, `LedgerCommandService`, `LedgerRefused` and its closed refusal-code set, the Phase-4-owned scope |
| `adapters/ledger/in_memory.py` | `LedgerBook` (the reference authority), `InMemoryLedgerRepository`, the composite `LedgerUnitOfWork` |

### The invariants, and where each is enforced

| Invariant | Where |
|---|---|
| Signed integer amounts of one named smallest unit; no float, `Decimal` or bare int | `LedgerEntry`, via `domain/quantities.py` |
| At least two entries, summing to zero | `LedgerTransaction.__post_init__` |
| Exactly one resource type per transaction | same |
| Exactly one book per transaction, so one command has one precondition | same |
| No zero entry; bounded, printable reason and account names; timezone-aware timestamp | same |
| A held balance may not go below zero | `LedgerCommandService`, read inside the transaction |
| The expected version | `LedgerCommandService` (early) **and** `LedgerBook.publish` (decisive) |
| Append-only | structural: no `update`, no `delete`, frozen dataclasses, immutable entry tuple |

### Design decisions a reviewer should check

**The aggregate is the ledger book, and a transaction may not span two.** That
gives one command exactly one optimistic-concurrency precondition. A movement
between two books needs both books' preconditions checked together and is
refused with `cross_book_transaction`; character-to-character trade is package
5.8 and is named in the refusal.

**`AccountKind` is double-entry's own distinction, not a Freedom Blades chart of
accounts.** A `HELD` account is a balance the platform tracks and may not go
negative — the rule `Resource.deduct` enforces in the live bot today. A
`COUNTERPARTY` account is where value crosses the boundary and is unbounded,
because bounding it would mean the platform claimed to know the world's balance.
Which named accounts a character has is a Phase 5 decision and none is
enumerated here.

**A correction is a compensating transaction and there is nothing else.**
`compensate()` negates every entry and names the original by id; the original is
untouched, and a compensation of a compensation is permitted because refusing it
would leave editing history as the only way out. `LedgerCommandService.compensate`
reads the original back rather than letting the caller rebuild it, so a
correction cannot quietly reverse something other than what was accepted.

**`kind_of` uses `type(...)`, not `isinstance`.** A subclass of `Money` that
redefined addition would pass an `isinstance` check and then be summed by rules
the ledger cannot see.

**The version precondition is decided where the write becomes visible, not where
it is read.** This is the substantive correction made during implementation: an
early comparison alone would let two callers who both read version 0 both
commit, and the first draft did exactly that — the failing test is recorded
below as mutation 16's target. `append()` therefore takes `expected_version` and
carries it into the commit, where `LedgerBook.publish` re-checks it under the
book's lock in the same critical section that appends. That is the shape of
`SqlAlchemyCharacterRepository.save`'s conditional `UPDATE … WHERE version =
:expected`, which is one atomic statement rather than a read followed by a write.

**The receipt is written before the effect, and the order decides what a
concurrent caller is told.** A duplicate submission of one command is a retry and
must be answered with the original receipt. If the effect's own precondition were
reached first, the loser of an identical double-submit would be told its version
was stale — true of the book, false of the question the caller asked.

**The in-memory ledger is a reference, not an alternative production authority.**
It models three properties exactly, because the service's guarantees rest on
them: uncommitted work disappears; a duplicate identity raises the same
`UniquenessConflict("ledger_transaction.id")` rule name the database adapter
would; and the version precondition is decided under a lock at publish time.

**The composite unit of work publishes before it commits, and retracts if the
commit fails.** The order is stated in full in `adapters/ledger/in_memory.py`.
Committing the database first would leave a durable receipt behind for a posting
the version fence then refused, and nothing could take it back. Publishing first
means an idempotency-record failure retracts the posting, and an effect failure
never reaches the database commit at all.

### The honest limit of this package, stated rather than discovered at review

**OD-48 rules that Phase 4 adds no ledger table**, so the posting's own
durability is exactly as durable as process memory. What is proved against
PostgreSQL is the receipt: the retry, the conflicting reuse and the concurrent
callers in WP-4 all turn on the real unique index on `(scope, key)`. When package
5.0 or 5.2 gives the ledger a table, both halves belong in **one** database
transaction, and the publish/commit ordering above becomes a single commit. The
service is written so that is a change of adapter rather than of use case. This
is recorded as risk **R-P4-4**.

### Not done in WP-3

No Discord command, web route or Foundry path calls this service. No ledger
table, migration, wallet table or character-state store is added. No account
vocabulary is defined.

---

## WP-4 — Durable idempotent command execution

**Complete.** **17 tests** in `tests/test_p4_idempotent_execution.py`, all
`@pytest.mark.database` and all against the disposable `freedom_test` PostgreSQL
database over the Unix-domain socket. No production module was added: WP-4 is the
WP-2 envelope and the WP-3 service integrated with the **existing**
`idempotency_keys` table under the Phase-4-owned scope `ledger.post_transaction`.

**No migration is added.** The rows written are inserts into an existing table
under a scope value nothing else uses. `admission_id` is null, which the table's
`submission_names_its_admission` check permits for every scope except the Foundry
submission's — asserted rather than assumed.

### What the database proves

| Requirement | Evidence |
|---|---|
| A repeated key with identical content returns the stable original result without executing the effect twice | `test_a_repeated_key_with_identical_content_executes_the_effect_once` — three calls, one receipt row, one audit row, one posting |
| The original result, not a recomputation | `test_a_retry_returns_the_original_result_after_the_book_has_moved_on` — the book advances between the call and the retry; the retry still answers with the original's version and transaction id |
| Reuse of a key with different content fails closed | `test_reuse_of_a_key_with_different_content_fails_closed` — `idempotency_key_conflict`, one receipt, the balance unchanged |
| Two concurrent callers produce one durable winner and one stable duplicate | `test_two_concurrent_callers_of_one_key_produce_one_durable_winner` — two threads, two engines, two real connections, one barrier; one receipt row, one audit row, one posting, and the loser's receipt equals the winner's |
| The loser is typed | `test_a_concurrent_loser_never_escapes_as_a_driver_exception` — never an `IntegrityError` or `DBAPIError` |
| Two concurrent callers against one version produce one effect | `test_two_concurrent_callers_of_two_keys_produce_one_version_winner` — different keys, same expected version; one commits, one is refused as stale |
| A stale version commits nothing | `test_a_stale_expected_version_commits_nothing_to_the_database` |
| The constraint itself, not the service's own early read | `test_the_database_refuses_a_second_receipt_for_one_key` — a direct insert of a second row for one `(scope, key)` raises `IntegrityError`. Without this assertion, dropping the index would leave every other test passing |
| Nothing unsafe reaches a caller or history | a refusal carries no SQL, no parameters, no driver name and no table name; the audit payload carries the reason and the resource and no amounts |

Transaction ownership stays at the application-service boundary: one unit of work
per attempt, repositories join it, nothing else commits.

### Not done in WP-4

No new persistence. No schema change. The `idempotency_keys` retention,
expiry and operator surface are untouched.

---

## WP-5 — Removed

Removed by the final OD-52 amendment (change-log `C-P4-F`). No wallet query, no
temporary Sheet adapter, no replacement bot command, web route, template or
view-model field was created. `ext/commands/info.py` and `helpers/renderers.py`
are byte-identical to the committed tree.

---

## WP-6 — Falsification and complete verification

### Falsification

**Sixteen mutations. All sixteen failed as required. None survived.** Numbering
continues from WP-0's and WP-1's mutations 1–10.

Each mutation was applied to the production tree, the smallest test expected to
fail was run, and the tree was restored **by copying from a byte-exact backup
and then verifying every file's SHA-256** against checksums taken before the
first mutation. No mutation survives in the submitted tree; the checksum
comparison after the final restoration passes for all eight production files.

**The WP-1 restore defect is closed.** WP-1 reported that `git checkout` had
silently done nothing for untracked files, leaving mutations on disk. This
harness never uses `git checkout`: it restores by copy and refuses to continue
unless every checksum matches, so a silent restoration failure is not
expressible.

| # | Mutation | Failing assertion |
|---|---|---|
| 11 | The balance-to-zero check is removed from `LedgerTransaction` | `test_an_unbalanced_transaction_is_refused[entries0..2]` — `DID NOT RAISE <class 'domain.ledger.LedgerError'>`, all three cases |
| 12 | An accepted transaction becomes mutable (`frozen=False`) | `test_an_accepted_transaction_cannot_be_mutated` — `DID NOT RAISE <class 'dataclasses.FrozenInstanceError'>` |
| 13 | A `delete` operation is added to ledger history | `test_history_offers_no_update_or_delete` — `assert not ({'amend', 'delete', 'edit', 'remove', …} & {…})` |
| 14 | The mixed-resource refusal is removed | `test_a_transaction_mixing_resources_is_refused` — `TypeError: unsupported operand type(s) for +: 'Money' and 'Moradinium'`, raised at `domain/ledger.py:303`. **Reported as it happened rather than tidied:** the test fails, but on the value objects' own refusal to add across types rather than on the transaction's typed `mixed_resources` message. That is defence in depth working — WP-1's arithmetic refusal catches what WP-3's check was removed from — and it is also the reason the transaction-level check is not redundant: it produces a typed, translatable refusal instead of a `TypeError` |
| 15 | The early stale-version refusal is removed from the service | `test_a_stale_expected_version_applies_nothing` and `test_a_stale_expected_version_commits_nothing_to_the_database` — both `DID NOT RAISE <class 'application.errors.ConcurrencyConflictError'>`; the second against PostgreSQL |
| 16 | The commit-time version fence is removed from the reference book | `test_a_book_that_moves_on_before_the_commit_refuses_the_posting` — `DID NOT RAISE … ConcurrencyConflictError`; and `test_two_concurrent_callers_of_two_keys_produce_one_version_winner` — two `CommandReceipt`s where one was expected. **This is the falsification of the design defect corrected during implementation** |
| 17 | The early idempotency read is removed, so a retry executes again | `test_a_retry_of_the_same_command_returns_the_original_receipt` and `test_a_repeated_key_with_identical_content_executes_the_effect_once` — both raise `ConcurrencyConflictError: … is at version 1; this command was decided against version 0`, which is the retry being executed a second time instead of replayed |
| 18 | The request-hash comparison is removed, so a conflicting reuse is accepted | `test_reusing_a_key_for_different_content_fails_closed` and `test_reuse_of_a_key_with_different_content_fails_closed` — both `DID NOT RAISE <class 'application.ledger.LedgerRefused'>` |
| 19 | The idempotency key is made unique per attempt | `test_two_concurrent_callers_of_one_key_produce_one_durable_winner` — a `CommandReceipt` beside a `ConcurrencyConflictError`, instead of one winner and one stable duplicate |
| 20 | A failed durable commit no longer retracts the published posting | `test_a_failed_durable_commit_retracts_the_posting` — `assert (LedgerTransaction(…),) == ()`: the posting survived a commit that never happened |
| 21 | The held-balance rule is removed | `test_a_held_account_may_not_go_below_zero` and `test_spending_one_more_than_is_held_is_refused` — both `DID NOT RAISE <class 'application.ledger.LedgerRefused'>` |
| 22 | The authorization port is no longer consulted | `test_an_ordinary_guild_member_is_refused` — `DID NOT RAISE <class 'application.ledger.LedgerRefused'>` |
| 23 | The transaction id is folded into the canonical digest | `test_a_retry_with_a_freshly_built_transaction_is_still_a_retry` — a rebuilt but identical retry is refused as `idempotency_key_conflict` |
| 24 | `domain/ledger.py` imports `sqlalchemy` | `test_domain_module_imports_only_stdlib_or_domain[ledger.py]` — *"ledger.py imports ['sqlalchemy'], which is neither the standard library nor `domain`"* |
| 25 | `whole_number` accepts integral floats (WP-1 mutation 5, re-run against **this** tree) | 7 failures, `DID NOT RAISE <class 'domain.quantities.QuantityError'>` across `Money`, `from_denominations`, `Moradinium` and `Downtime` |
| 26 | The `bool` guard is removed from `whole_number` (WP-1 mutation 6, re-run) | 14 failures, same assertion |

### The handover's minimum falsification list, item by item

| Required | Covered by |
|---|---|
| float or Boolean admission into a quantity | 25, 26 (re-run against this tree; originally WP-1's 5, 6) |
| cross-resource arithmetic | 14 at the ledger boundary; WP-1's mutation 7 on the value objects |
| an unbalanced ledger transaction | 11 |
| mutation or deletion of an accepted ledger entry | 12, 13 |
| stale-version acceptance | 15 (early refusal) and 16 (the decisive commit-time fence) |
| duplicate execution after a same-content retry | 17, and 23 for the rebuilt-command form of a retry |
| acceptance of conflicting idempotency-key reuse | 18 |
| two concurrent successful effects for one key | 19 |
| partial state after injected transaction failure | 20; the injected-failure tests demonstrate the property without needing a mutation |
| an infrastructure import into `domain/` | 24 (originally WP-1's 9, 10) |

### Complete verification — the tree actually submitted

Narrow tests first, then the suites **serially**, because they share one
disposable database (finding F-6).

```sh
export TEST_DATABASE_URL='postgresql+psycopg:///freedom_test'
/opt/discord-bots/venv/bin/python     -m pytest -q -rs tests/test_*.py
/opt/discord-bots/venv-web/bin/python -m pytest -q -rs tests/web
node --test "foundry-module/tests/"*.test.mjs
```

| Suite | Result |
|---|---|
| Bot | **2840 passed, 0 skipped**, 1 warning, 146.10 s |
| Web | **2824 passed, 80 skipped**, 135.89 s |
| Foundry module | **171 pass, 0 fail, 0 skipped** |

**The web skip count is 80, exactly the established figure**, and `-rs` accounts
for every one: 54 in `tests/web/test_p3_2_matrix.py:155` and 26 in
`tests/web/test_p3_3_matrix.py:198`, both reading *"permitted cells are asserted
by the per-route success cases"*. **None is a database skip.** Assumption
**A-P4-2** holds and package-plan stop condition 5 is not triggered.

The bot suite's single warning is the pre-existing `audioop` deprecation from
`discord/player.py` under Python 3.12. It is not this package's.

Bot suite arithmetic: the pre-implementation baseline was 2447; WP-0 added 36
(2483); WP-1 added 141 (2624 by its own commands, reported as 2627 including the
two files together); this package adds 61 + 78 + 50 + 17 = **206**, plus 2 from
the `domain/` guard now covering `ledger.py`. Every new test is named in the WP
sections above.

### Concurrency in fresh processes

Each run in its own interpreter, cache provider disabled, so nothing carries
over from a shared session:

```sh
/opt/discord-bots/venv/bin/python -m pytest -q -p no:cacheprovider \
  "tests/test_p4_idempotent_execution.py::<test>"
```

| Test | Result |
|---|---|
| `test_two_concurrent_callers_of_one_key_produce_one_durable_winner` | 1 passed in 1.22 s |
| `test_two_concurrent_callers_of_two_keys_produce_one_version_winner` | 1 passed in 1.26 s |
| `test_a_concurrent_loser_never_escapes_as_a_driver_exception` | 1 passed in 1.38 s |

### Other checks

| Check | Result |
|---|---|
| `compileall` under `/opt/discord-bots/venv` over `domain application adapters` | **OK** |
| `compileall` under `/opt/discord-bots/venv-web` over `domain application adapters` | **OK** — `domain/` and the ledger adapter depend on neither runtime's packages |
| `git diff --check` | **clean** |
| Formatter | **Not configured.** No `pyproject.toml`, `setup.cfg`, `.ruff.toml`, `.flake8`, `mypy.ini` or `tox.ini` exists in the repository |
| Linter | **Not configured**, same evidence |
| Type checker | **Not configured**, same evidence |
| Alembic heads/branches, migration upgrade/downgrade | **Not applicable.** No migration is added (OD-48) |
| Staging | **Does not exist and is not required** (assumption A-P4-1). Nothing is deployed |

Nothing was skipped, mocked or stubbed to produce a figure above. No test in
this package contacts live Discord, Sheets, Foundry or production PostgreSQL,
and no real player data or credential appears in any fixture.

### Two web-suite failures this package caused, found and fixed

Both were real, both are reported rather than quietly repaired, and one of them
had been failing since **WP-1**.

**1. `test_p3_3_audit_search.py::test_every_payload_key_this_repository_writes_is_classified`.**
That regression parses every `AuditEvent(payload={...})` literal in the
repository and requires each key to be in `RENDERED_PAYLOAD_KEYS`. WP-3's audit
event writes four new keys — `book_id`, `entry_count`, `resource`, `version` —
and none was classified. As the allowlist's own docstring says, a missing entry
is not a disclosure but a **silent loss**: a Council member reading history would
see `(not rendered)` where the platform meant to show them a fact. The four keys
are now classified in `application/web/audit_search.py`, each in one of the four
categories the list permits — a UUID identifier, a closed vocabulary value and
two integers. **The posting's amounts are deliberately not in the payload at
all**, so nothing here can carry one character's holdings into another Council
member's view. `docs/contracts/phase-3-view-model-contract.md` needs no change:
it specifies the *mechanism* — an unrecognised key is rendered redacted — and
that mechanism is unchanged.

**2. `test_p3_4_static_assets.py::test_no_unrelated_production_files_modified`,
and this one is a finding about the WP-1 evidence, not only about WP-2–WP-4.**
That guard reads `git status --short` and rejects any undeclared change under
`adapters/`, `application/` or `domain/`. **`domain/` has been watched since
2026-08-27 (N-27)**, so WP-1's three untracked `domain/` modules were tripping it
from the moment they were written. Nobody saw it because WP-0 and WP-1 ran the
**bot suite only**, on the stated reasoning that a package adding no web code
cannot affect the web suite. That reasoning is wrong for this guard specifically:
it reads the working tree, not the web application. The submitted figures are
therefore the first complete evidence Phase 4 has produced, and WP-1's
"the web and Foundry suites cannot be affected" note should be read with this
correction beside it.

The fix follows the guard's own design — *"the exception is enumerated here
rather than left to erode the guard"*: a new `PERMITTED_PHASE_4_PRODUCTION` set
in `tests/web/test_p3_4_static_assets.py` names every Phase 4 production file,
with the authority and the package plan cited. It also declares
`adapters/ledger/` in the trailing-slash form, because `git status --short`
collapses a wholly untracked directory to one entry and the files inside it never
appear in the output the guard reads.

**Two Phase 3 files were therefore modified by this package**, which the package
plan did not anticipate and which a reviewer should look at directly:

| File | Change | Why it is not a security-surface change |
|---|---|---|
| `application/web/audit_search.py` | four keys added to `RENDERED_PAYLOAD_KEYS` | The list governs what the audit projection **renders**, not who may read it. No route, capability check, session, CSRF or bound is touched; rendering still fails closed for anything unlisted |
| `tests/web/test_p3_4_static_assets.py` | `PERMITTED_PHASE_4_PRODUCTION` added and consulted | Test code. The guard's coverage is unchanged for every path not enumerated, and the synthetic-path test that proves the guard can still fail is untouched and passes |

---

## WP-7 — Documentation and independent-review handoff

### Requirements satisfied

| Handover requirement | Where |
|---|---|
| Integer-copper money and explicitly unitized resources | `domain/money.py`, `domain/resources.py` (WP-1) |
| Narrow application command/query conventions and typed errors | `application/commands.py` (WP-2); the query convention documented without a protocol, per final OD-52 |
| Balanced, append-only ledger semantics with compensating entries | `domain/ledger.py` (WP-3) |
| A concrete Phase 4 command-execution path consuming the application and repository boundaries | `LedgerCommandService` in `application/ledger.py` (WP-3) |
| Durable idempotent command execution using existing persistence | `idempotency_keys` under scope `ledger.post_transaction` (WP-4) |
| Optimistic-concurrency handling | `ExpectedVersion` + the commit-time fence (WP-2/WP-3) |
| Characterization of intended Sheet-era behavior | `tests/test_p4_characterization.py` (WP-0) |

### Files changed

**Added — production:**

- `domain/quantities.py`, `domain/money.py`, `domain/resources.py` (WP-1)
- `domain/ledger.py` (WP-3)
- `application/commands.py` (WP-2)
- `application/ledger.py` (WP-3)
- `adapters/ledger/__init__.py`, `adapters/ledger/in_memory.py` (WP-3)

**Added — tests:**

- `tests/test_p4_characterization.py` (36), `tests/test_p4_domain_quantities.py` (120),
  `tests/test_p4_domain_isolation.py` (23), `tests/test_p4_commands.py` (61),
  `tests/test_p4_ledger_domain.py` (78), `tests/test_p4_ledger_service.py` (50),
  `tests/test_p4_idempotent_execution.py` (17)

**Modified — existing:**

- `application/web/audit_search.py` — four payload keys classified (see WP-6)
- `tests/web/test_p3_4_static_assets.py` — Phase 4 production files declared (see WP-6)

**Unchanged, and verified so:** `ext/commands/info.py`, `helpers/renderers.py`,
`models/`, `connectors/`, every migration, every Alembic revision, every
`infra/` artefact, every `adapters/web` route and template.

**Documentation:** this submission, package plan §17, status update 113,
change-log `C-P4-G`, RAID rows R-P4-1…R-P4-4, A-P4-1, A-P4-2.

### Migrations

**None.** OD-48. No new table, column, constraint, index, trigger or grant. The
`idempotency_keys` rows this package writes are inserts into an existing table
under a scope value nothing else uses, with `admission_id` null — permitted by
the table's `submission_names_its_admission` check for every scope but the
Foundry submission's, asserted directly in `test_the_receipt_is_stored_in_the_existing_idempotency_table`.

### Security and authority effects

- **No authentication, session, CSRF, OAuth, break-glass or rate-limit change.**
- **No authorization *policy* change.** `LedgerCommandService` requires current
  Guild Council authority through the existing `AuthorizationPort`, resolved at
  execution rather than carried in the request. That is the existing rule (plan
  §4.3, `application/authorization.py`) applied to a new service, not a new one.
- **No new route, command, endpoint or user-facing surface.** Nothing calls this
  service outside its tests.
- **No authority moves.** No read or write authority leaves Google Sheets. The
  ledger holds no migrated Sheet field.
- `/info`'s existing lack of read authorization (risk **R-P4-3**) is untouched
  and remains package 5.1's.
- Refusals carry no SQL, no bound parameters, no driver name, no table name and
  no other player's holdings; audit payloads carry identifiers, a closed
  vocabulary, counts and the transaction's bounded reason, and no amounts.

### Deployment and rollback effects

- **Deployment: none.** No service, unit file, Caddy configuration, environment
  variable, credential or dependency changes. Nothing was restarted; no host was
  touched; no production database, live Discord, live Sheets or Foundry instance
  was contacted.
- **Persistence: none beyond existing rows.** Rows written under the Phase 4
  idempotency scope exist only in the disposable test database.
- **Rollback:** revert the commit. There is no schema state to unwind and no data
  to reconcile.
- **Recovery:** not applicable; this package introduces no persistent mutation
  outside the disposable database.

### Unresolved items

1. **D-04 remains Open.** It closes only when the Acceptance Authority approves
   the Phase 4 gate.
2. **The ledger has no physical persistence** (OD-48), so a posted transaction is
   durable only as far as process memory — risk **R-P4-4**. Package 5.0 or 5.2
   owns the table, its constraints, its append-only enforcement and its
   runtime-role evidence, and must commit the posting and its receipt in one
   database transaction.
3. **Two Phase 4 design choices are flagged for the reviewer rather than
   assumed**: `AccountKind.HELD`/`COUNTERPARTY`, and the one-book-per-transaction
   restriction. Package-plan §17.2 items 4 and 5 state the reasoning.
4. **No account vocabulary exists.** The ledger takes opaque `(book, name)`
   identities. Which accounts a character has is a Phase 5 decision.
5. **The float-money defects in `/sale` and `/lc` remain**, characterized and
   deferred to packages 5.7 and 5.3 under OD-51.
6. **The implementer designation** remains supplied by instruction rather than in
   writing (package plan, readiness statement).

### Proposed reviewer focus areas

For **Codex**, as the named Independent Reviewer:

1. **The commit-time version fence.** `LedgerBook.publish` and
   `LedgerUnitOfWork.commit` in `adapters/ledger/in_memory.py`, and the
   publish-before-commit-with-retraction ordering. This is where the one design
   defect was found, and the reasoning about what a future real table changes is
   the thing most worth disagreeing with.
2. **The write order in `LedgerCommandService._execute`** — receipt before
   effect — and whether the argument for it (an identical double-submit must be
   told "retry", not "stale") holds under every interleaving.
3. **Dependency direction.** Whether the allowlist guard is strong enough, and
   whether `application/ledger.py` leaks anything infrastructural.
4. **`AccountKind`** — whether a structural held/counterparty distinction is
   within Phase 4's authority or is game-economy policy that should have been an
   OD.
5. **The one-book restriction**, and whether refusing a cross-book transaction
   now will cost package 5.8 more than it saves.
6. **The canonical idempotency digest** in `_digest` — whether excluding the
   transaction id is right, and whether anything that makes a command *what it
   is* is missing from it.
7. **The two modified Phase 3 files**, and whether either constitutes a change
   this package was not authorized to make.
8. **What the falsification does not cover.** Mutation 14's failure came from the
   value objects rather than the transaction check, and no mutation exercises the
   `LedgerBook.retract` path under real concurrency.

### What this package does not claim

It does not close **D-04**. It does not approve the Phase 4 gate. It authorizes
no Phase 5 work, no migration, no cutover, no deployment and no Sheet
retirement. The suites passing is evidence for the gate, not the gate.

**The package is submitted for Codex independent review of dependency direction,
domain correctness, atomicity, concurrency, idempotency and regression safety.
Peter's gate decision follows the review.**

---

## Remediation R1 — P4-R1, P4-R2, P4-R3 · 2026-08-29

**Status: remediation complete and submitted for independent re-review. No
finding is closed here.** Claude does not close P4-R1, P4-R2, P4-R3 or D-04 and
does not decide the Phase 4 gate. Codex re-reviews all three findings; Peter
Duscha alone records the gate decision. Everything above this line is the
original review history and is unchanged.

Authority: `docs/review/Handover information` (remediation-only brief), the
independent-review disposition at the head of this document, status update 114,
RAID rows P4-R1…P4-R3 and change-log C-P4-H.

### What was in scope, and what was not

Remediated: exactly the three findings. **OD-48 is untouched** — no ledger
table, no migration, no wallet/balance store, no new database authority and no
runtime ledger deployment. No route, Discord command, Foundry endpoint,
deployment unit, environment variable or credential was added; no Sheet-era
field was migrated; `/info` is untouched; the Freedom bot's production behaviour
is unchanged; no Phase 5 work began. No authorization, idempotency, audit,
concurrency, append-only or failure-handling rule was weakened to make a test
pass — the falsification below is the evidence for that claim rather than the
claim itself.

---

### P4-R1 — the transaction boundary is now one the adapter can enforce

**The defect.** `LedgerUnitOfWork.commit()` published the postings, released the
book's lock, committed the durable half, and on failure called
`LedgerBook.retract(N)` to delete the last *N* transactions. Two things were
wrong and the second is the serious one: the posting was externally visible
before anything had committed, and the rollback was **positional**, so a
concurrent caller that appended in that window could be deleted by the failing
caller's rollback while the failing caller's own posting was kept.

**The correction — a different transaction shape, not a better retraction.**
`retract` is gone and nothing replaces it. `LedgerBook.committing(pending)` is a
context manager that holds the book's writer lock across the durable commit:

1. under the lock, every pending posting is validated against committed history
   — transaction identity, then the optimistic version precondition;
2. the durable half commits inside the `with` block; and
3. only if it returned do the postings become visible, by rebinding an immutable
   tuple, still under the same lock.

A durable commit that fails appends nothing, so there is nothing to take back.
**Rollback of a published posting is not an operation this class can be asked to
perform**, which is a stronger guarantee than a correct implementation of one.

Readers deliberately do **not** take the writer's lock: committed history is an
immutable tuple read without blocking. That is what makes "an in-flight posting
is invisible" an assertion a test can *fail* rather than hang on.

The handover's seven properties, and where each now holds:

| Property | How |
|---|---|
| no uncommitted posting is externally visible | the tuple is rebound only after the durable commit returns; readers see committed history or the history before it |
| a failed durable commit leaves none of that caller's effects | the append never happens; the receipt and audit row roll back with the inner unit of work |
| a successful concurrent caller remains intact | writers serialize on the book, and nothing removes an accepted transaction |
| versions and balances describe surviving committed history | both are derived from that tuple; no running total is stored beside it |
| rollback never removes another unit of work's transaction | no rollback removes anything at all |
| receipt, audit and effect cannot disagree | no posting exists without its receipt; the residual direction is stated below |
| stale-version and duplicate-identity outcomes remain typed | `ConcurrencyConflictError` and `UniquenessConflict("ledger_transaction.id")`, both decided inside the critical section that appends |

**The honest limit, stated rather than left to be discovered.** A process dying
between the durable commit returning and the tuple being rebound would leave a
receipt with no posting. For this adapter that window is unobservable — the book
is process memory and dies with the process. It becomes real the moment the
ledger has a table, and at that point both halves belong in one database
transaction, which is exactly what OD-48 defers to package 5.0 or 5.2. **The
in-memory adapter no longer claims cross-store atomicity anywhere**; what it
claims and enforces is written at the head of `adapters/ledger/in_memory.py`.

**Code:** `adapters/ledger/in_memory.py` — `LedgerBook.committing`,
`LedgerBook._require_acceptable`, `LedgerUnitOfWork.commit`; `publish` and
`retract` removed.

**Tests** (`tests/test_p4_ledger_service.py`, fakes; and
`tests/test_p4_idempotent_execution.py`, real PostgreSQL). Synchronization is by
`threading.Event` set at named points inside the units of work — **no sleeps**,
so the interleaving is decided by the test rather than by how long anything
takes.

| Test | What it pins |
|---|---|
| `test_an_in_flight_posting_is_not_visible_before_its_durable_commit` | property 1 alone, in the direction that succeeds: a reader looking mid-commit sees nothing, and sees the posting once the commit returns |
| `test_a_failed_durable_commit_cannot_remove_a_concurrent_callers_posting` | the handover's mandatory regression, steps 1–7: A stops inside its durable commit, B posts validly with a distinct key, A fails; only B survives, with B-only version and balances, and a following command succeeds against the surviving version |
| `test_a_failed_durable_commit_keeps_the_concurrent_winners_database_rows` | the same ordering against real PostgreSQL: one receipt row, keyed `winner`, and one audit row |
| `test_the_inverse_ordering_leaves_the_earlier_posting_alone` | B first, then A fails: A's failure does not reach back |
| `test_a_failed_commit_leaves_its_idempotency_key_free_for_the_same_key` | the same-key ordering, which fails differently: A's receipt never became durable, so the key was never spent and a retry posts exactly once |
| `test_the_book_offers_no_way_to_remove_an_accepted_transaction` | structural: `retract`, `publish`, `remove`, `delete` and `update` are all absent |
| `test_a_failed_durable_commit_leaves_no_posting`, `test_a_failed_durable_commit_leaves_the_book_free_for_the_next_command` | the previous retraction-era tests, renamed and retained: the property is unchanged, the mechanism is not |

---

### P4-R2 — service-principal authority is resolved inside the application boundary

**The defect.** `LedgerCommandService._attribute()` returned
`SERVICE_PRINCIPAL` authority for any `CommandCaller` carrying a non-blank
`principal_id`. The envelope is built out of the request, so a direct caller
could manufacture authority by choosing a string. The rule "every non-human
caller is automatically authorized" is removed.

**The correction.** A narrow, consumer-owned port in `application/ledger.py`:

- `LedgerScope` — an enum with one member, `POST_TRANSACTION`;
- `LedgerPrincipal` — a resolved principal: an operator-chosen identifier and
  the scopes it currently holds. Its identifier obeys the accepted rule, now
  extracted as `application.service_principals.validate_principal_id` and called
  rather than copied; and
- `LedgerPrincipalPort.current_principal(principal_id) -> LedgerPrincipal | None`
  — asked at execution, on every command.

At execution the service asks the port, refuses when the port returns nothing,
refuses when the resolved principal does not hold `POST_TRANSACTION`, and
attributes the audit row to the **resolved** principal
(`payload.service_principal_id`) rather than to request text. `principal_id` is a
*lookup*, never a grant, and `application/commands.py` now says so where the
field is defined. Human Council authority is unchanged: still resolved at
execution through `AuthorizationPort`.

Unknown, revoked, deactivated and out-of-scope produce **one** refusal with one
message naming neither the principal nor which cause applied — the same posture
`adapters/http/credentials.py` already takes, and the reason is the same.

**Why a consumer-owned port rather than `ServicePrincipalScope`.** That enum is
the accepted authority vocabulary of the Foundry snapshot credential set, whose
secrets are configured in `FREEDOM_SNAPSHOT_PRINCIPALS`. Adding a ledger scope to
it would widen what an operator could grant to a snapshot-submission credential
— a change to an accepted authorization decision, and not Phase 4's to make.
Phase 4 has no production caller for this service, so the handover's stated
alternative applies. **No implementation of `LedgerPrincipalPort` exists outside
the tests, and the fake proves authorization, not authentication.** Proving that
a presented credential belongs to a principal is an adapter's job, owned by the
package that gives this service a caller. No credential table was invented and
`.env.example` is unchanged.

**Code:** `application/ledger.py` (`LedgerScope`, `LedgerPrincipal`,
`LedgerPrincipalPort`, `_attribute`, `_attribute_person`,
`_attribute_principal`, the audit payload); `application/service_principals.py`
(`validate_principal_id`, extracted, behaviour-preserving);
`application/commands.py` (docstring only); `tests/fakes.py`
(`FakeLedgerPrincipals`).

**Tests** — all through **direct service calls**, which is the level the defect
lived at:

| Test | What it pins |
|---|---|
| `test_a_currently_authorized_and_correctly_scoped_principal_succeeds` | the valid case, and that the port was asked |
| `test_an_unknown_principal_is_refused` | an id nobody configured |
| `test_a_revoked_principal_is_refused` | authorized for one command, refused for the next |
| `test_a_deactivated_principal_is_refused` | a distinct operator action, one answer |
| `test_a_principal_without_the_posting_scope_is_refused` | the scope branch, through a stand-in principal — `LedgerScope` has one member today, so a principal holding only *another* scope cannot be constructed |
| `test_a_caller_constructed_principal_name_cannot_bypass_the_port` (×4) | `guild-council`, `system`, `admin` and a near-miss all resolve to nothing |
| `test_a_principal_refusal_says_which_of_its_causes_applies_to_none_of_them` | one message, naming no principal |
| `test_principal_authority_is_re_resolved_on_every_execution` | asked per command, not per session |
| `test_a_refused_principal_leaves_history_receipts_and_audit_untouched` | no transaction, no receipt, no audit row on refusal |
| `test_a_successful_principal_command_is_attributed_to_the_resolved_principal`, `test_a_human_command_records_no_service_principal` | safe attribution, both ways |
| `test_a_ledger_principal_holding_no_scope_cannot_be_constructed`, `…refuses_a_scope_that_is_merely_text`, `…refuses_an_identifier_history_cannot_render` | the resolved principal's own invariants |
| `test_an_unresolved_principal_writes_nothing_to_the_database` (×3), `test_a_principal_authorized_now_may_be_refused_on_the_next_command`, `test_an_authorized_principal_is_recorded_as_the_resolved_principal` | the same properties against real PostgreSQL: zero receipt rows, zero audit rows, and the resolved id in the stored payload |

---

### P4-R3 — idempotency is bound to the complete command identity

**The defect.** `_digest()` covered the book, the resource, the expected
version, the reason, the compensation target and the entries. It omitted the
authoritative occurrence time and the caller identity, so a key reused for
materially different history — or by a different principal — hashed identically
and was answered as a retry. It also joined its fields with `"\n"`, which
collides as soon as a field can contain a newline.

**The rule, stated field by field.** `application/ledger.py`'s module docstring
carries the contract; this is its summary.

*Command-defining* — change any and the same key **conflicts**: the digest
schema; the command name and idempotency scope; the caller's source; the
**authenticated caller identity**; the book; the resource; the expected version;
the **authoritative occurrence time**; the reason; the compensation target; the
entry count; and every entry in order — account book, name, kind, unit and
signed amount.

*Attempt metadata* — may differ between attempts under one key:

- **`correlation_id` is attempt metadata**, in both the envelope and the
  transaction, and the handover requires this to be unambiguous. It ties one
  *attempt*'s receipt, audit row and log line together. Only the first attempt's
  transaction is ever accepted, so only its correlation id is ever recorded, and
  a retry is answered from the stored receipt and therefore returns the
  **original** attempt's correlation id. Stored receipt, audit correlation and
  retry behaviour all agree on that. Were it command-defining, a genuine retry
  that generated a fresh one would be refused as a conflict.
- **`LedgerTransaction.id`** — excluded under the handover's stated condition: a
  rebuilt true retry is intentionally equivalent, and the accepted id is always
  returned from stored state (`facts.transaction_id` is read back from the
  receipt, never recomputed).
- **The idempotency key itself**, which is the identity the digest is stored
  under.

**Canonicalization.** `canonical_request_hash(schema, fields)` in
`application/idempotency.py` replaces delimiter joining with a **typed,
length-delimited, schema-versioned** encoding: every name and value is written as
an 8-byte big-endian length followed by its bytes, with no separator anywhere;
each value carries a one-byte type tag so text, a whole number and an absent
field are three different digests; the field count is bound in; and
`DIGEST_SCHEMA = "ledger.post_transaction.identity/1"` is hashed first, so a
stored key can only ever be compared against the field list that produced it.
The occurrence time is bound as exact integer microseconds since the epoch, by
integer `timedelta` arithmetic rather than `timestamp()` — one instant has one
canonical form, and no binary float decides an identity. The existing
`request_hash` is retained unchanged for its one fixed-shape caller, with its
ambiguity now documented.

**Compatibility.** No stored key changes meaning: the Phase 4 scope has never
run outside the disposable test database, so there are no production digests to
reinterpret, and the schema version exists so that a future change cannot
silently reinterpret the ones there will be.

**Code:** `application/idempotency.py` (`canonical_request_hash`,
`CanonicalValue`, the type tags); `application/ledger.py` (`DIGEST_SCHEMA`,
`_digest`, `_epoch_microseconds`, `_amount_units` now returning an integer,
`_Attribution.identity`).

**Tests** — the handover's mandatory list, item by item:

| Required | Test |
|---|---|
| an identical retry returns the original receipt | `test_a_retry_of_the_same_command_returns_the_original_receipt`, `test_a_repeated_key_with_identical_content_executes_the_effect_once` (PostgreSQL) |
| different `occurred_at` under the same key conflicts | `test_a_different_occurrence_time_under_one_key_conflicts`, `test_one_microsecond_of_difference_is_a_different_command`, `test_a_different_occurrence_time_conflicts_against_the_stored_digest` (PostgreSQL); and `test_the_same_instant_in_another_timezone_is_the_same_command` for the other direction |
| another human or service principal under the same key conflicts | `test_another_human_reusing_one_key_conflicts`, `test_another_service_principal_reusing_one_key_conflicts`, `test_a_principal_cannot_replay_a_persons_command_or_the_reverse`, `test_another_caller_cannot_replay_a_stored_receipt` (PostgreSQL) |
| a rebuilt genuine retry with a fresh transaction object executes once | `test_a_rebuilt_true_retry_executes_once_and_returns_the_accepted_identifiers`, `test_a_retry_with_a_freshly_built_transaction_is_still_a_retry` |
| changing every other command-defining field conflicts | `test_the_canonical_digest_covers_what_makes_the_command_what_it_is` — reason, amount, direction, account, **entry order**, entry count, account kind; plus `test_a_different_expected_version_under_one_key_conflicts`, `test_the_same_principal_on_another_surface_conflicts`, `test_a_compensation_target_is_part_of_the_command_identity` |
| corrupted stored receipts fail closed without re-execution | `test_a_corrupted_stored_receipt_fails_closed_without_re_executing` (PostgreSQL, by corrupting the stored row), `test_a_spent_key_whose_receipt_is_unreadable_is_never_re_executed`, `test_a_spent_key_with_no_stored_receipt_is_never_re_executed` |
| the `correlation_id` rule agrees with stored receipt, audit and retry | `test_a_correlation_id_is_attempt_metadata_and_not_command_identity` |
| the canonicalization itself | `test_the_canonical_encoding_cannot_be_collided_by_resplitting_a_field`, `…distinguishes_a_number_text_and_nothing`, `…is_bound_to_its_schema_version`, `…refuses_a_boolean` |

---

### Falsification — the handover's six mutations

Each mutation was applied to the tree, the tests were run, and the tree was
restored **by copying from a byte-exact backup** — never by `git checkout`,
which does nothing for these untracked files — and then verified with
`sha256sum -c` against checksums taken before the first mutation. **All eight
files matched after the final restoration; no mutation survives in the submitted
tree.**

One file changed *after* that verification and is recorded here rather than left
for a checksum comparison to raise: an unused `LedgerScope` import was removed
from `tests/test_p4_idempotent_execution.py`. **No production file changed after
falsification** — the five production files still verify `OK` against the
pre-mutation checksums — and the complete suite set was run again afterwards.

| # | Mutation | Exact failing test and assertion |
|---|---|---|
| R1-1 | Positional cross-caller retraction returns: `committing` appends before the durable commit, releases the lock, and truncates the last *N* on failure | `test_an_in_flight_posting_is_not_visible_before_its_durable_commit` and `test_a_failed_durable_commit_cannot_remove_a_concurrent_callers_posting` — both `AssertionError: assert (LedgerTransaction(…),) == ()`, at `tests/test_p4_ledger_service.py:1294` and `:1339`; and against PostgreSQL, `test_a_failed_durable_commit_keeps_the_concurrent_winners_database_rows`, same assertion. **Deterministic**: the failure is the visibility assertion made while A is inside its durable commit, not a race between B's append and A's rollback |
| R1-2 | Service principals bypass the authorization port: `_attribute` returns `SERVICE_PRINCIPAL` from the request without asking | **16 failures.** `test_an_unknown_principal_is_refused` — `Failed: DID NOT RAISE <class 'application.ledger.LedgerRefused'>`; also the revoked, deactivated, wrong-scope, four caller-constructed-name, undifferentiated-message, re-resolution and untouched-history tests, and all four PostgreSQL principal tests |
| R1-3 | The port is asked but its answer is not enforced: the `None`/scope refusal is disabled | **14 failures**, same assertion. `test_a_principal_without_the_posting_scope_is_refused` and `test_a_revoked_principal_is_refused` are the two the handover names |
| R1-4 | `occurred_at` is removed from request identity | `test_a_different_occurrence_time_under_one_key_conflicts`, `test_one_microsecond_of_difference_is_a_different_command`, and `test_a_different_occurrence_time_conflicts_against_the_stored_digest` (PostgreSQL) — all three `Failed: DID NOT RAISE … LedgerRefused` |
| R1-5 | Authenticated caller identity is removed from request identity | `test_another_human_reusing_one_key_conflicts`, `test_another_service_principal_reusing_one_key_conflicts`, `test_another_caller_cannot_replay_a_stored_receipt` (PostgreSQL) — all `Failed: DID NOT RAISE … LedgerRefused`. **Reported as it happened rather than tidied:** `test_a_principal_cannot_replay_a_persons_command_or_the_reverse` did *not* fail, because that pair also differs in `caller.source`, which the digest still covers. That is defence in depth working, and it is the reason the source field is not redundant |
| R1-6 | True retries execute a second effect: the early idempotency read is removed | **25 failures.** `test_a_rebuilt_true_retry_executes_once_and_returns_the_accepted_identifiers` — `application.errors.ConcurrencyConflictError: Ledger book … is at version 1; this command was decided against version 0`, which is the retry being executed a second time instead of replayed; and `test_the_stored_receipt_survives_a_json_round_trip_unchanged` against PostgreSQL |

---

### Complete verification — the tree actually submitted

Narrow tests first, then the suites **serially**, because they share one
disposable database (finding F-6). Run under the correct interpreters: `./venv`
and `./venv-web` are the *runtime* environments and have no pytest.

```sh
export TEST_DATABASE_URL='postgresql+psycopg:///freedom_test'

/opt/discord-bots/venv/bin/python -m pytest -q \
  tests/test_p4_commands.py tests/test_p4_ledger_service.py \
  tests/test_p4_idempotent_execution.py

/opt/discord-bots/venv/bin/python     -m pytest -q -rs tests/test_*.py
/opt/discord-bots/venv-web/bin/python -m pytest -q -rs tests/web
node --test "foundry-module/tests/"*.test.mjs

/opt/discord-bots/venv/bin/python     -m compileall -q domain application adapters
/opt/discord-bots/venv-web/bin/python -m compileall -q domain application adapters
git diff --check
```

| Check | Result |
|---|---|
| Narrow — commands, ledger service, PostgreSQL idempotency | **178 passed**, 0 failed, 0 skipped, 3.43 s |
| Bot suite | **2890 passed, 0 skipped**, 0 failed, 1 warning, 144.30 s |
| Web suite | **2824 passed, 80 skipped**, 0 failed, 1137 warnings, 139.51 s |
| Foundry module | **171 pass, 0 fail**, 0 skipped, 237.9 ms |
| `compileall`, bot interpreter | clean |
| `compileall`, web interpreter | clean |
| `git diff --check` | clean |

**The web skip count is exactly 80 and none of them is a database skip.** `-rs`
reports both reasons: 54 from `tests/web/test_p3_2_matrix.py:155` and 26 from
`tests/web/test_p3_3_matrix.py:198`, both *"permitted cells are asserted by the
per-route success cases"*. `TEST_DATABASE_URL` was exported for every run, which
is what makes the figure meaningful — without it the web suite reports roughly
1141 passed and 1362 skipped and still exits 0.

The bot suite is **2890** against the pre-remediation **2840**: the 50 new tests
are the regressions above. The web figure is unchanged at 2824/80.

**Formatter, linter and type checker: each remains unconfigured** in this
repository. None was run and none is claimed.

**Diff review.** The complete diff was read for secrets, credentials, tokens,
real player data, unsafe logging, unrelated changes and accidental Phase 5
scope. There are none: no `.env`, service-account JSON, Discord token, OAuth
secret, database URL or Foundry credential is read, printed or committed; every
identifier in the tests is synthetic; no refusal message carries SQL, bound
parameters, a driver name or a filesystem path; and nothing outside the three
findings' code and tests, the two declared Phase 3 guard files and this
documentation was touched.

**The complete set was run three times**: against the finished code, again after
this documentation was written, and again after the one post-falsification test
edit noted above — so the figures describe the tree actually submitted rather
than an earlier one. All three runs returned identical counts. The five
production files verify `OK` against the pre-falsification SHA-256 checksums in
the last of them.

---

### Two web-suite failures this remediation caused, found and fixed

Reported rather than quietly corrected, because both are Phase 3 controls doing
exactly what they exist for, and both would have been invisible to a bot-suite-
only run.

1. **`test_every_payload_key_this_repository_writes_is_classified`.** The new
   `service_principal_id` audit payload key was unclassified, so the audit view
   would have rendered `(not rendered)` where the platform meant to name the
   principal. Fixed by classifying it in `RENDERED_PAYLOAD_KEYS` with its bound
   and its reason. It is an operator-chosen token from a closed configured set,
   never the credential and never the request's claimed text.
2. **`test_no_unrelated_production_files_modified`** — *"Unpermitted application
   modification detected in working tree: application/idempotency.py"*. The
   remediation touches two tracked production modules the Phase 4 declaration
   did not list. Both are now declared in `PERMITTED_PHASE_4_PRODUCTION` with
   their reasons, which is the guard's own mechanism rather than a way around
   it.

---

### Changed contracts a re-reviewer should read as changes

1. **`LedgerCommandService.__init__` requires `principals`.** No default: one
   would have to be "authorize every principal", which is the defect, or "refuse
   every principal", which would let a deployment that forgot to wire a port look
   like one that deliberately has no service callers. Every construction site
   must now say which it is. There are no production construction sites.
2. **Transaction semantics.** `LedgerBook.publish` and `LedgerBook.retract` are
   gone, replaced by `LedgerBook.committing`. Any future adapter implements the
   ordering, not the retraction.
3. **Audit payload.** `ledger.transaction_posted` gains
   `service_principal_id`, always present and `null` for a person.
4. **Idempotency identity.** The digest covers more fields and is computed by a
   different, versioned encoding. Digests are not comparable across the change —
   which is why the schema version exists, and why it matters that no digest has
   ever been stored outside the disposable test database.
5. **`application/service_principals.py`** exports `validate_principal_id`. The
   rule is unchanged; only its call site moved. **No scope was added to
   `ServicePrincipalScope`, and the Foundry credential vocabulary is untouched.**

### Migrations, deployment, configuration, rollback

- **Migrations: none, and none expected.** OD-48 is unchanged; no table, no
  column, no constraint, no trigger, no role grant.
- **Deployment: none.** No service, unit file, Caddy configuration, environment
  variable, credential or dependency changes. No host was touched and no live
  Discord, Sheets, Foundry or production database was contacted.
- **Configuration: none.** `.env.example` is unchanged.
- **Rollback:** revert the commit. There is no schema state to unwind and no data
  to reconcile. Rows written under the Phase 4 idempotency scope exist only in
  the disposable test database.

### Checks not run, and open questions

- **Formatter, linter and type checker remain unconfigured** in this repository.
  Each was checked for and none is present; none was run, and none is claimed.
- **`LedgerPrincipalPort` has no production implementation.** The fake proves
  authorization. Authentication of a presented credential is owed by the package
  that gives this service a caller, and is called out for the reviewer rather
  than assumed to be somebody's problem later.
- **Open question for the maintainer and the reviewer:** whether a ledger scope
  should eventually join `ServicePrincipalScope` — one vocabulary — or stay
  consumer-owned as it is here. This remediation deliberately did not decide it,
  because deciding it would widen an accepted credential's grantable authority.
- The unresolved items recorded before the review (D-04, R-P4-4, `AccountKind`,
  the one-book restriction, the absent account vocabulary, the deferred `/sale`
  and `/lc` float defects, the implementer designation) are unchanged.

### Proposed re-review focus

1. `LedgerBook.committing` — whether holding the writer lock across the durable
   commit is the right shape for a reference adapter, and whether the residual
   crash window is stated honestly enough.
2. Whether the P4-R1 regression is genuinely deterministic, and whether the
   visibility assertion is the right thing to be asserting.
3. `LedgerPrincipalPort` — whether a consumer-owned port was the right call
   against reusing `ServicePrincipalScope`, and whether the port's contract is
   narrow enough to implement safely later.
4. The command-defining/attempt-metadata split, field by field, and in
   particular the `correlation_id` ruling and the exclusion of the transaction
   id.
5. `canonical_request_hash` — whether the encoding is unambiguous, and whether
   the schema version is placed where it can do its job.

**Submitted for Codex independent re-review of P4-R1, P4-R2 and P4-R3. No
finding is closed, D-04 remains Open, the Phase 4 gate remains deferred, and no
Phase 5 work is released.**

---

## Remediation R2 — P4-R4, P4-R5 · 2026-08-29

**Status: remediation complete and submitted for independent re-review. No
finding is closed here.** Claude does not close P4-R4, P4-R5 or D-04 and does
not decide the Phase 4 gate. Codex re-reviews both findings; Peter Duscha alone
records the gate decision. Everything above this line — the original review, the
re-review disposition and the Remediation R1 record — is unchanged.

Authority: `docs/review/Handover information` (Remediation-R2-only brief), the
independent re-review disposition at the head of this document, package plan
§19, status update 116, RAID rows P4-R4/P4-R5 and change log C-P4-J.

### What was in scope, and what was not

Remediated: exactly the two findings. **OD-48 is untouched** — no ledger table,
no migration, no wallet/balance store, no new database authority. No route,
Discord command, Foundry endpoint, deployment unit, environment variable,
credential or configuration changed; no Sheet-era field was migrated; `/info` is
untouched; the Freedom bot's production behaviour is unchanged; no Phase 5 work
began. No stop condition was reached.

**One production file changed**: `application/ledger.py`. Two test files
changed: `tests/test_p4_ledger_service.py` and
`tests/test_p4_idempotent_execution.py`. No *tracked* production module changed,
so the P3.4 scope guard needed no new declaration — `application/ledger.py` was
already declared in `PERMITTED_PHASE_4_PRODUCTION` from WP-3.

---

### P4-R4 — authority is resolved before the lookup, and exactly once

**The defect, precisely.** `compensate()` opened a unit of work, called
`ledger.get(transaction_id)`, and refused an unknown id with `concurrent_posting`
*before* any authority was resolved. An id that did exist went on to `post()`,
which resolved authority and refused with `not_authorized`. Two different
refusals to two different questions, both reachable by a caller holding no
authority at all. Nothing was written on either path — no posting, no receipt,
no audit row — so the defect was never an effect. It was an **existence
oracle**: an ordinary guild member, a member whose Council role had been
withdrawn, an unknown principal, a revoked or deactivated one, or one holding
some other scope could all ask this method whether a given transaction id is in
the ledger and read the answer off which refusal came back.

**The correction.**

1. `compensate()` resolves the caller's current authority through the same
   `_attribute` path `post()` uses, **before** it opens a unit of work. An
   unauthorized caller is refused with the identical `not_authorized` code and
   the identical fixed prose whether the transaction exists or not, and the
   ledger is never read — so there is no answer to leak rather than an answer
   that is withheld.
2. That resolution happens **once**. A new private `_post_resolved()` carries the
   already-resolved `_Attribution` through the correlation fence, the
   expected-version precondition, the digest and `_execute`. Resolving before
   the lookup and then calling `post()` would resolve a *second* time, and a
   resolution is a reading with a time: a credential revoked between the two
   readings would leave the lookup authorized under one identity and the posting
   recorded under another.
3. The carried attribution is what the canonical digest binds, what the audit
   row is attributed to, and what the receipt describes. One operation, one
   answer, used consistently.
4. **`post()` is unchanged in behaviour.** It resolves authority first as
   before and then calls the same private path, so every existing posting,
   refusal, retry, conflict and concurrency property is the property it was.

**The private path is private, and that is load-bearing.** `_post_resolved` is
not exposed and `LedgerCommandService` still offers exactly two public methods,
`post` and `compensate`, neither of which accepts an attribution. An
`_Attribution` exists only as a port's answer; a public entry point that
accepted one would let an adapter present a *conclusion* where the design
requires it to present an *identity* — which is defect P4-R2 in a new place.
`test_the_service_offers_no_public_way_to_supply_an_attribution` asserts this
structurally, by reflection, rather than in prose. No authorization is cached
between requests.

**Tests added — 20, of which 9 run against real PostgreSQL.**

| Property | Test |
|---|---|
| Unauthorized caller cannot distinguish existing from unknown | `test_no_unauthorized_caller_can_tell_an_existing_transaction_from_an_unknown_one`, parametrized over **six** caller shapes: ordinary member, revoked member, unknown principal, revoked principal, deactivated principal, wrong-scope principal. Asserts the two refusals are the *same pair* — same code and same prose — and that the target id does not appear in the message |
| …and the ledger was never consulted at all | The same test counts the units of work the service asked its factory for and asserts the count is unchanged across both attempts. This is the stronger claim: not that the answers match, but that the question was never asked |
| No posting, receipt or audit on any refusal | `test_an_unauthorized_correction_of_an_existing_transaction_writes_nothing`, same six shapes; and against PostgreSQL, `test_an_unauthorized_correction_writes_nothing_durable_either_way`, same six shapes, asserting `idempotency_keys` and `audit_events` hold only the first posting's rows |
| One resolution per compensation | `test_a_human_correction_resolves_the_authorization_port_exactly_once` and `test_a_principal_correction_resolves_the_principal_port_exactly_once` — each asserts its port's `asked` list has exactly one entry **and** that the port the caller does not need was not consulted at all; against PostgreSQL, `test_a_correction_resolves_its_authority_port_exactly_once` |
| The refusing path resolves once too | `test_a_refused_correction_resolves_authority_once_and_stops` |
| Authorized compensation still works, and records the resolved actor | `test_an_authorized_correction_still_appends_and_records_the_resolved_actor` (human) and `test_a_principal_correction_is_attributed_to_the_resolved_principal` (service principal); against PostgreSQL, `test_an_authorized_correction_commits_one_posting_receipt_and_audit_row` and `test_a_correction_by_a_principal_records_the_resolved_principal_durably`, the latter selecting the audit row by the correction's own entity id rather than by timestamp order |
| A true retry creates no second effect | `test_a_rebuilt_true_retry_of_a_correction_creates_no_second_effect` — the retry regenerates both the compensating transaction and its correlation id; and against PostgreSQL, `test_a_true_retry_of_a_correction_creates_no_second_durable_effect` |
| No public way to supply an attribution | `test_the_service_offers_no_public_way_to_supply_an_attribution` |

---

### P4-R5 — one correlation identity per attempt

**The defect.** `CommandEnvelope.correlation_id` and
`LedgerTransaction.correlation_id` were independent, and nothing required them
to agree. When they differed, the receipt and the audit row recorded the
envelope's while append-only ledger history kept the transaction's: one attempt
with two correlation identities, and an operator tracing an audit row into
ledger history finding nothing. Neither the digest nor a retry could detect it,
because correlation is attempt metadata and deliberately excluded from the
digest.

**The correction.** `post()` refuses a mismatch with the new typed refusal code
`correlation_mismatch`, raised **before** the expected-version precondition is
read, before the digest is computed and before the unit-of-work factory is
called. The prose is fixed and names neither identity. An accepted command then
records one id in all three places: `_execute` takes the fenced
`correlation_id` as a parameter and uses it for the receipt and the audit row,
while the transaction carries the same value into ledger history — so the three
cannot drift apart through a later edit to one of them.

**It is a fence, not a new digest field.** The handover is explicit that
correlation must not be added to the command-defining digest to mask the
mismatch, and it is not: making it command-defining would refuse a genuine retry
that regenerated one, which is the opposite of what a retry needs. What is
fenced is a single attempt's *internal* disagreement. A true retry may carry a
fresh correlation id in **both** halves, is still the same command, and is
answered from the stored receipt — which returns the accepted attempt's id,
exactly as the P4-R3 ruling says it must.

**Refused rather than silently resolved.** Preferring the envelope's id would
quietly discard the one the domain object was built with; preferring the
transaction's would make the caller's own correlation a suggestion. Both
directions are the same refusal, and
`test_a_mismatch_is_refused_whichever_side_carries_the_stray_identity` asserts
it.

**Tests added — 19, of which 4 run against real PostgreSQL.**

| Property | Test |
|---|---|
| Mismatch refused before the unit-of-work factory is called, leaving ledger, receipt and audit empty | `test_a_mismatched_correlation_is_refused_before_a_unit_of_work_opens` — counts factory calls, then asserts `assert_nothing_happened()`; against PostgreSQL, `test_a_mismatched_correlation_leaves_the_database_empty` |
| The refusal is typed, declared and safe | `test_the_correlation_refusal_is_declared_and_names_neither_identity` — the code is in `REFUSAL_CODES` and neither id appears in the prose |
| Refused in both directions | `test_a_mismatch_is_refused_whichever_side_carries_the_stray_identity` |
| One accepted command records one id in ledger history, receipt and audit | `test_an_accepted_command_records_one_correlation_id_in_all_three_places`; and `test_an_accepted_correction_records_one_correlation_id_in_all_three_places` for the compensation path, using a correlation id distinct from the original posting's so the assertion is not trivially true. Against PostgreSQL, `test_one_accepted_command_stores_one_correlation_id_in_every_record` reads the audit `correlation_id` column and the stored `response` JSON back out of the database |
| A rebuilt true retry with new attempt metadata returns the original receipt and creates no second effect | `test_a_retry_carrying_new_attempt_metadata_in_both_halves_is_still_a_retry`; against PostgreSQL, `test_a_retry_with_fresh_attempt_metadata_returns_the_stored_correlation` |
| Correlation is still not command-defining | `test_correlation_is_not_in_the_command_defining_digest` — reads the digest directly for two attempts differing only in their (internally consistent) correlation id and asserts the two digests are equal |
| Correlation remains attempt metadata across a retry | `test_a_correlation_id_is_attempt_metadata_and_not_command_identity`, updated so the second attempt regenerates the id on **both** halves |

**A test-fixture consequence, stated rather than absorbed.** Both Phase 4
service test files previously built envelopes and transactions with independent
`uuid4()` correlation ids, so essentially every posting in them was a mismatch
under the new rule. The helpers now default both halves to one fixed module
constant (`ATTEMPT`), and a test that needs a genuinely separate attempt passes
one fresh id to both. This is a fixture change, not a weakening: the fence's own
tests supply mismatches explicitly, and the falsification below shows the tests
fail when the fence is removed.

---

### Falsification — four mutations, all detected, tree restored

`application/ledger.py` was copied to a byte-exact backup and its SHA-256
recorded before the first mutation. Each mutation was applied, the two Phase 4
service test files were run, and the tree was restored **by copying from that
backup** — never by `git checkout`, which does nothing for these untracked
files. After the final restoration `sha256sum -c` reported
`application/ledger.py: OK`, and the narrow set was re-run green. **No mutation
survives in the submitted tree.** No test file was mutated, so no test file
needed restoring.

| # | Mutation | Exact failing tests and assertion |
|---|---|---|
| R2-1 | **The exact P4-R4 defect restored**: `compensate()` opens a unit of work, calls `ledger.get()`, refuses an unknown id with `concurrent_posting`, and only then delegates to `self.post()` for authorization | **12 failures.** All six parametrizations of `test_no_unauthorized_caller_can_tell_an_existing_transaction_from_an_unknown_one` — `AssertionError: assert 2 == 1`, the two distinct answers being `('concurrent_posting', 'The transaction to be corrected is not in the ledger…')` and `('not_authorized', '…requires a currently authorized service principal…')` — and all six parametrizations of the PostgreSQL `test_an_unauthorized_correction_writes_nothing_durable_either_way`, same assertion at `tests/test_p4_idempotent_execution.py:918` |
| R2-1a | **A weaker variant, run first and reported because it is informative**: the lookup happens first but authority is resolved before the missing-transaction refusal, so both callers still receive `not_authorized` | **6 failures**, all six parametrizations of the same application test, but on the *other* assertion: `assert 3 == 1` on the count of units of work opened, at `tests/test_p4_ledger_service.py:1636`. The refusal-equality assertion passes under this mutation and the unit-of-work count catches it — which is why the test asserts both, and why "the question was never asked" is the property worth asserting rather than "the answers matched" |
| R2-2 | **A second authorization resolution**: authority is resolved before the lookup, then the operation delegates to `self.post()`, which resolves again | **3 failures.** `test_a_human_correction_resolves_the_authorization_port_exactly_once`, `test_a_principal_correction_resolves_the_principal_port_exactly_once`, and the PostgreSQL `test_a_correction_resolves_its_authority_port_exactly_once` — `AssertionError: assert ['ledger-worker', 'ledger-worker'] == ['ledger-worker']`, *"Left contains one more item"* |
| R2-3 | **The correlation equality fence removed** (`if envelope.correlation_id != transaction.correlation_id` → `if False`) | **4 failures.** `test_a_mismatched_correlation_is_refused_before_a_unit_of_work_opens`, `test_the_correlation_refusal_is_declared_and_names_neither_identity`, `test_a_mismatch_is_refused_whichever_side_carries_the_stray_identity`, and the PostgreSQL `test_a_mismatched_correlation_leaves_the_database_empty` — all `Failed: DID NOT RAISE <class 'application.ledger.LedgerRefused'>` |
| R2-4 | **Correlation made command-defining**, added to the canonical digest — the masking the handover forbids | **6 failures.** `test_correlation_is_not_in_the_command_defining_digest`; and the retry regressions it would break: `test_a_correlation_id_is_attempt_metadata_and_not_command_identity`, `test_a_rebuilt_true_retry_of_a_correction_creates_no_second_effect`, `test_a_retry_carrying_new_attempt_metadata_in_both_halves_is_still_a_retry`, and against PostgreSQL `test_a_true_retry_of_a_correction_creates_no_second_durable_effect` and `test_a_retry_with_fresh_attempt_metadata_returns_the_stored_correlation` — each `LedgerRefused: This idempotency key has already been spent on a different command`, which is a genuine retry being refused as a conflict |

---

### Complete verification — the tree actually submitted

Narrow tests first, then the suites **serially**, because they share one
disposable database (finding F-6). Run under the correct interpreters: `./venv`
and `./venv-web` are the *runtime* environments and have no pytest.

```sh
export TEST_DATABASE_URL='postgresql+psycopg:///freedom_test'

/opt/discord-bots/venv/bin/python -m pytest -q \
  tests/test_p4_domain_quantities.py tests/test_p4_commands.py \
  tests/test_p4_ledger_domain.py tests/test_p4_ledger_service.py \
  tests/test_p4_idempotent_execution.py

/opt/discord-bots/venv/bin/python     -m pytest -q -rs tests/test_*.py
/opt/discord-bots/venv-web/bin/python -m pytest -q -rs tests/web
node --test "foundry-module/tests/"*.test.mjs

/opt/discord-bots/venv/bin/python     -m compileall -q domain application adapters
/opt/discord-bots/venv-web/bin/python -m compileall -q domain application adapters
git diff --check
```

| Check | Result |
|---|---|
| Narrow — the five Phase 4 files named in the handover | **415 passed**, 0 failed, 0 skipped, 4.40 s (was 376: **+39** R2 regressions) |
| Bot suite, serial | **2929 passed, 0 skipped**, 0 failed, 1 warning, 145.37 s (was 2890) |
| Web suite, serial | **2824 passed, 80 skipped**, 0 failed, 1137 warnings, 137.12 s — unchanged |
| Foundry module | **171 pass, 0 fail**, 0 skipped, 213.2 ms |
| `compileall`, bot interpreter | clean |
| `compileall`, web interpreter | clean |
| `git diff --check` | clean |

**The web skip count is exactly 80 and none of them is a database skip.** `-rs`
reports both reasons: 54 from `tests/web/test_p3_2_matrix.py:155` and 26 from
`tests/web/test_p3_3_matrix.py:198`, both *"permitted cells are asserted by the
per-route success cases"*. `TEST_DATABASE_URL` was exported for every run, which
is what makes the figure meaningful — without it the web suite reports roughly
1141 passed and 1362 skipped and still exits 0.

**The bot suite's zero skips is the load-bearing number here**, given the
re-review's 2887/2/1. See the environment note below.

**Formatter, linter and type checker: each remains unconfigured** in this
repository. The repository was checked again for `ruff`, `black`, `flake8`,
`mypy`, `pyproject.toml`, `setup.cfg` and `tox.ini`; none is present. None was
run and none is claimed.

**Diff review.** The complete diff was read for secrets, credentials, tokens,
real player data, unsafe logging, unrelated changes and accidental Phase 5
scope. There are none: no `.env`, service-account JSON, Discord token, OAuth
secret, database URL or Foundry credential is read, printed or committed; every
identifier in the tests is synthetic; no refusal message carries SQL, bound
parameters, a driver name or a filesystem path; and nothing outside
`application/ledger.py`, the two Phase 4 service test files and this
documentation was touched.

### The disposable test database and the re-review's 2887/2/1 — reported, not assumed fixed

The handover requires the documented disposable-test grant state to be restored
and the drill rerun before any bot-suite figure is cited, and forbids carrying
the earlier 2890/0 figure forward.

What was actually observed, stated plainly:

- The bot suite was run **before any R2 code change** as a baseline and returned
  **2890 passed, 0 skipped, 0 failed** in 142.57 s.
- `tests/test_database_backup_restore.py` was run on its own: **35 passed, 0
  failed, 0 skipped**. `tests/test_runtime_grants_live.py` also passes.
- The final post-remediation run returned **2929 passed, 0 skipped, 0 failed**.

So in this environment the drill passes, there are no skips, and the grant state
the drill requires is present. **No grant was altered by this remediation** — no
`GRANT`, `REVOKE`, role or schema change was executed, and
`infra/postgresql/runtime-grants.sql.tmpl` is untouched. The honest reading is
that the re-review's 2887/2/1 reflects the reviewer's own disposable database
rather than a defect in the tree, and that the restoration the handover asks for
was not needed here because nothing here was missing. **Nothing above claims the
reviewer's environment is fixed**; a re-reviewer seeing 2887/2/1 again should
apply `infra/postgresql/runtime-grants.sql.tmpl` to their `freedom_test`
database and rerun the drill before reading the figure as a Phase 4 result. The
2890/0 baseline is quoted only as this session's own pre-change measurement, and
the submitted figure is the 2929/0 run against the finished tree.

### Changed contracts a re-reviewer should read as changes

1. **`LedgerCommandService` has a new declared refusal code**,
   `correlation_mismatch`, added to `REFUSAL_CODES`. An adapter branching on the
   closed set must handle it. It is raised only by `post()`/`compensate()`
   before any unit of work opens.
2. **A `post()` that previously succeeded with disagreeing correlation ids now
   refuses.** No production caller exists — Phase 4 has no route, command or
   deployment unit for this service — so the change has no production surface,
   but it is a real narrowing of the accepted input and is recorded as one.
3. **`compensate()` resolves authority before reading the ledger.** An
   unauthorized caller now receives `not_authorized` where it previously could
   receive `concurrent_posting`. The missing-transaction refusal is unchanged
   for an *authorized* caller.
4. **`post()`'s behaviour is unchanged**, deliberately and as the handover
   requires. Its authorization, digest, retry, conflict, balance and concurrency
   properties are the ones Remediation R1 delivered.

### Migrations, deployment, configuration, rollback

- **Migrations: none, and none expected.** OD-48 is unchanged; no table, no
  column, no constraint, no trigger, no role grant.
- **Deployment: none.** No service, unit file, Caddy configuration, environment
  variable, credential or dependency changes. No host was touched and no live
  Discord, Sheets, Foundry or production database was contacted.
- **Configuration: none.** `.env.example` is unchanged.
- **Rollback:** revert the commit. There is no schema state to unwind and no
  data to reconcile. Rows written under the Phase 4 idempotency scope exist only
  in the disposable test database.

### Checks not run, and open questions

- **Formatter, linter and type checker remain unconfigured.** Checked for,
  absent, not run, not claimed.
- **`LedgerPrincipalPort` still has no production implementation.** The fake
  proves authorization; authentication of a presented credential is owed by the
  package that gives this service a caller.
- **The open question from Remediation R1 is unchanged and undecided**: whether
  a ledger scope should eventually join `ServicePrincipalScope`. R2 did not
  touch it.
- **No staging-class check was run**, because no staging environment exists.
- The unresolved items recorded before the review (D-04, R-P4-4, `AccountKind`,
  the one-book restriction, the absent account vocabulary, the deferred `/sale`
  and `/lc` float defects, the implementer designation) are unchanged.

### Proposed re-review focus

1. Whether resolving authority before the lookup and carrying one
   `_Attribution` through a private path is the right shape, and whether
   `_post_resolved` is genuinely unreachable from outside the class.
2. Whether counting units of work is a fair proxy for "the ledger was never
   read" — falsification R2-1a is the argument that it catches more than the
   refusal-equality assertion does.
3. Whether the six unauthorized caller shapes are the right six, and whether any
   further shape could reach `compensate()` with an authority the parametrization
   does not model.
4. Whether refusing a correlation mismatch is preferable to normalizing one, and
   whether `correlation_mismatch` belongs in the closed refusal vocabulary or is
   better modelled as an `InvalidEnvelopeError` — the choice made here is that it
   is a *relationship* between two objects rather than a malformed envelope, so
   it is a refusal rather than a construction error.
5. Whether the test-helper change to paired correlation ids has weakened any
   existing assertion.

**Submitted for Codex independent re-review of P4-R4 and P4-R5. No finding is
closed, D-04 remains Open, the Phase 4 gate remains deferred, and no Phase 5
work is released.**
