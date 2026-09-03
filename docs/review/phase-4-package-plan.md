# Phase 4 — Shared application services

Package plan, readiness statement and impact assessment.

Date: 2026-08-28

Prepared by: Claude (proposed implementing agent and working Technical Lead)

Acceptance Authority, Product Owner, Data Owner, Operations Owner, Delivery
Lead: Peter Duscha

Authority for the phase: Peter Duscha approved the Phase 3 gate and explicitly
authorized Phase 4 implementation on 2026-08-28 (change-log `C-P3.5-AK`). The
executable brief is `docs/review/Handover information`.

Status: **accepted; gate closed 2026-08-29.** After two remediation cycles,
Codex returned no remaining Blocking or Important findings and Peter Duscha
approved the Phase 4 dependency-direction and domain-correctness gate. P4-R1
through P4-R5 and D-04 are Closed. Phase 5 package planning is released subject
to each package's own readiness, predecessor, review and cutover controls. WP-5
remains removed by final OD-52. Evidence is in `phase-4-submission.md`.

**Decision state, final 2026-08-29. All six decisions are ruled.** Peter Duscha ruled
each on 2026-08-28, recorded canonically in `docs/discovery/open-decisions.md`
as **OD-48** (no ledger table and no migration in Phase 4), **OD-49** (integer
thousandth-days, refuse rather than round, preserve today's rendering),
**OD-50** (integer copper only; the Sheet's denomination counters stay a legacy
representation), **OD-51** (characterize the `/sale` and `/lc` float defects,
defer the fix to packages 5.7 and 5.3) and **OD-52 as finally amended** (Phase 4
creates neither an `/info` rewrite nor a temporary wallet query/Sheet adapter;
package 5.2 introduces the query with its real character-page consumer). P4-D6 is a governance ruling rather
than an OD: **Codex is the Independent Reviewer**, performing the implementation
review, with **no separate security-focused review required**. Change-log
`C-P4-C` through `C-P4-F`.

**Readiness is therefore met**, on the reading that Peter's instruction to
execute the handover designates Claude as the implementing agent and working
Technical Lead. That designation is the one readiness element supplied by
instruction rather than in writing, and is flagged here so it can be corrected
rather than assumed silently. Nothing here approves the Phase 4 gate or closes
D-04.

---

## 1. Outcome

A framework-independent domain and application foundation that both the Discord
bot and the web application can call: typed money and resource quantities,
narrow command boundaries and query conventions, an append-only ledger with balanced
transaction semantics, typed errors, durable idempotent command execution,
optimistic-concurrency detection, characterization of the intended Sheet-era
behavior. The application protocols are exercised by the ledger and durable
idempotent command-execution work. Phase 4 creates no wallet query or temporary
Sheet adapter and does not rewire `/info`; package 5.2 introduces the wallet
read path with the character page as its first production consumer.

The phase gate is **dependency direction and domain correctness**. Test counts
do not close it.

---

## 2. Scope

### 2.1 In scope

| # | Deliverable | Layer |
|---|---|---|
| 1 | `domain/money.py` — integer-copper `Money`, denomination arithmetic, refusal of mixed and unsafe coercion | domain |
| 2 | `domain/resources.py` — `Moradinium` (unit: 1) and `Downtime` (unit: 1/1000 day, per OD-08) as immutable typed quantities that cannot be constructed invalid | domain |
| 3 | `domain/ledger.py` — append-only entry, balanced transaction, compensating-entry semantics | domain |
| 4 | `application/ledger.py` — ledger repository protocol owned by its consumer, plus the transaction-boundary contract | application |
| 5 | `application/commands.py` — command envelope carrying caller authority, idempotency identity, expected version and correlation context; typed results; query convention documented without an unused protocol | application |
| 6 | Durable idempotent command execution on the **existing** `idempotency_keys` table under a Phase-4-owned scope (subject to P4-D1) | application + existing adapter |
| 7 | Optimistic-concurrency precondition handling on the existing `ConcurrencyConflictError` and the existing `characters.version` column | application |
| 8 | Characterization tests for the Sheet-era money/resource behavior listed in §4 | tests |
| 9 | A dependency guard proving `domain/` imports no Discord, Google, SQLAlchemy, FastAPI, `config` or environment module | tests |
| 10 | Falsification evidence: for each important invariant, the exact mutation that breaks it and the assertion that then fails | tests + submission |
| 11 | Package submission, traceability, status, change-log and RAID updates | docs |

### 2.2 Explicitly out of scope

Restated from the handover, and binding on this package:

- **No Phase 5 work.** No Sheet-era field is migrated. No mission reward,
  attendance, approval centre, crafting, trade, sale, lifestyle accrual,
  Bastion or facility behavior is implemented.
- **No authority change.** No read or write authority moves from Sheets to
  PostgreSQL. No dual write. No Sheet, credential, macro, adapter or rollback
  path is retired.
- **No command rewiring.** `ext/commands/info.py` and its renderer remain
  unchanged. Existing characterization remains regression evidence.
- **No wallet query or temporary Sheet adapter.** Package 5.2 introduces both
  with the character page as their first real consumer.
- **No new mutation.** No character
  state mutation is added to the web portal.
- **No security surface change.** Authentication, authorization, session and
  break-glass behavior are untouched.
- **No Foundry write** and no live Foundry connector.
- **No real player or snapshot data**, in fixtures or anywhere else.
- **No deployment.** No service restart, no host configuration, no production
  database contact, no live Discord or Sheets contact.
- **No repair of the legacy float-money mutation paths** identified in §4.4.
  They are characterized, not corrected, and belong to their owning Phase 5
  packages.
- **The Phase 4 gate is not claimed** from implementation or green tests.

---

## 3. Phase-boundary impact assessment (plan §0.2)

The final OD-52 amendment changes one Phase 4 acceptance criterion under plan
§0.2: both real-command wiring and the interim adapter/query compromise are
removed. Application-boundary evidence comes from the ledger and durable
idempotent command-execution work.
It changes no authority, privacy, architecture, data ownership, phase order or
release boundary and therefore requires no new baseline version. Three notes
qualify that:

1. **New `domain/` modules are additive.** `domain/` today holds only Foundry,
   identity, name and snapshot-value concerns. Money, resources and the ledger
   are new files with no existing importer, so nothing changes behavior by being
   added.
2. **The estimate remains within the roadmap range.** §12's Phase 4 target is
   5–10 working days. The most-likely figure in §7 is 9.0 and the PERT
   expectation is 9.6. Under §0.4 that is a planning input, not a commitment, and
   it is stated here rather than compressed out of the review allowance.
3. **The persistence question is a genuine boundary.** P4-D1 in §5 asks whether
   Phase 4 adds a physical ledger table. Option B would be a material schema
   addition and would stop code work until the mandatory logical schema artifact
   is independently reviewed. The recommendation is Option A, which adds none.

---

## 4. Characterization inventory (handover task 1, done before planning)

This is the pre-implementation inventory of every money and resource concept in
the live bot, with the file and line each claim rests on. It is the basis for
the scope and estimates above, and four findings in it are the reason §5 has
open decisions.

### 4.1 Units and representations as they exist today

| Concept | Live representation | Smallest unit | Where |
|---|---|---|---|
| Money (domain-side) | `Money(copper: int)`, frozen dataclass, `Decimal` on the gold boundary with `ROUND_HALF_UP` | 1 cp | `models/money.py:8` |
| Money (character-side) | four independent `int` counters `platinum`/`gold`/`silver`/`copper` | 1 cp, but not normalized | `models/resource.py:8` |
| Money (Sheet-side) | Characters columns **P, Q, R, S** — one column per denomination | as above | `models/actor.py:45-48` |
| Moradinium | `int` counter | 1 | `models/resource.py:14`, Characters **T** |
| Downtime | **Python `float`**, via `safe_number(..., default=0.0)` | register and OD-08 fix the unit at **1/1000 day**; the code enforces nothing | `models/resource.py:18`, `helpers/utils.py:6` |
| Living-cost weeks | `int` | 1 week | `models/lifestyle.py:23`, Characters **J** |
| Debt | `Resource` constructed but never loaded, written or read | — | `models/actor.py:69`; RC-D4, OD-04 |

`models/exchange.py:3` states the conversion table the platform actually uses:
`pp=1000, gp=100, sp=10, cp=1` copper. It agrees with `Money.from_denominations`
(`models/money.py:27`). There is no third rate anywhere.

### 4.2 Reads, writes and visible output

- **Read:** `Actor.load_from_sheet` (`models/actor.py:97`) reads `Characters!A3:AL150`
  once, matches on the lower-cased name, refuses on zero matches and refuses on
  more than one (`AmbiguousActorError`, `models/actor.py:26`).
- **Write:** `Actor.save_to_sheet` (`models/actor.py:223`) diffs against the
  cells loaded at read time, re-verifies the row still holds the same character,
  and writes only changed cells. Phase 4 calls none of this.
- **Visible output:** `Resource.get_summary` (`models/resource.py:41`) prints
  each denomination **only when strictly positive**, then Moradinium
  unconditionally, then downtime when asked. `render_actor_summary`
  (`helpers/renderers.py:72`) assembles name, level, badge, lifestyle,
  optional Bastion and resources. `/info` prints exactly that
  (`ext/commands/info.py:21`). This output is the characterization target: it
  must not change by one character.

### 4.3 Validation and refusal behavior worth preserving

- `Resource.validate_downtime` (`models/resource.py:35`) requires downtime ≥ 5
  and a multiple of 5, then requires availability. Note the comparison is
  `downtime > self.downtime` against a **float** balance.
- `Resource.deduct` (`models/resource.py:66`) refuses negative currency
  deductions, refuses insufficient Moradinium, and otherwise makes change by
  breaking larger coins downward, mutating only after every requirement is met —
  `tests/test_resource.py:89` already pins that a failed deduction mutates
  nothing.
- `Resource.add` (`models/resource.py:104`) refuses any result that would leave
  a denomination negative.
- `calculate_exchange` (`models/exchange.py:18`) refuses non-positive amounts,
  unknown denominations, same-to-same exchange, insufficient funds, and an
  exchange whose net effect is zero. It returns changes and mutates nothing —
  the one existing example of the command/query separation Phase 4 generalizes.
- `safe_int` / `safe_number` (`helpers/utils.py:6,15`) **silently coerce**
  invalid persisted values to a default. `.agents/AGENTS.md` forbids that at a
  boundary ("do not silently coerce invalid persistent data"). Phase 4's domain
  objects must refuse. Package 5.5 owns the eventual Sheet boundary and explicit
  unresolved-value behavior for downtime; Phase 4 creates no read adapter.

### 4.4 Rule fidelity and the float findings

Two live mutation paths compute money in **binary floating point**, against the
product invariant that money is never persisted or calculated as a float:

- `Resource.sale` (`models/resource.py:166-167`): `earnings = crafting_cost *
  earnings_percent`, then `to_currency()` (`helpers/utils.py:29`) converts the
  float through `Decimal(str(...))`. The rule itself (RC-01, RC-03) is recorded
  as **Implemented ✓ / Corrected ✓** and reproduces both PDF worked examples;
  the defect is the arithmetic type, not the rule.
- `Lifestyle.pay_for_weeks` (`models/lifestyle.py:52`): `extra_expenses_sp /
  10.0` through the same converter.

Both are **out of scope** (§2.2) and owned by packages 5.7 and 5.3. They are
characterized here so that the owning package inherits a test that states what
today does, and a named risk rather than a surprise. This is proposed decision
**P4-D4**.

No rule conflict blocks Phase 4. RC-A7 (50 GP per Moradinium, Council-adjustable)
is **Not implemented** and stays that way: Phase 4 adds no conversion rate
between Moradinium and money, because a rate with a Council-adjustable history is
a Phase 5/6 concern and inventing one here would be exactly the silent policy
choice the handover forbids.

### 4.5 The read-only command characterization

`/info` is the **only** read-only command in `ext/commands/`. Everything else
writes: `learn`, `bastion`, `mine`, `lc`, `sale`, `work`, `craft` and `xchange`
call `save_to_sheet` directly, and `trade` writes through `Trade.perform_trade`
(`ext/commands/trade.py:56`). The handover's "one bounded money/resource query"
therefore has exactly one candidate, and it renders more than money — see
**P4-D5**. The characterization remains useful, but the amended OD-52 does not
authorize or require rewiring this transitional command in Phase 4.

### 4.6 Foundations that already exist and must be reused, not rebuilt

`.agents/AGENTS.md` forbids abstractions without a real consumer. These already
exist from Phases 1–3 and Phase 4 consumes them:

| Need | Existing implementation |
|---|---|
| Durable idempotency receipts | `application/idempotency.py`, table `idempotency_keys` (`adapters/database/tables.py:507`), unique on `(scope, key)`, SHA-256 `request_hash`, retry vs. conflicting-reuse already distinguished |
| Typed application errors | `application/errors.py` — `ConcurrencyConflictError`, `UniquenessConflict`, `PersistenceError`, with driver text deliberately dropped |
| Optimistic concurrency | `characters.version` with a non-negative check constraint (`adapters/database/tables.py:80`) |
| Transaction ownership | `UnitOfWork` protocol (`application/repositories.py:197`) and `SqlAlchemyUnitOfWork` (`adapters/database/unit_of_work.py:58`) |
| Repository protocols owned by consumers | `application/repositories.py` |
| Per-actor serialization in the bot process | `application/actor_locks.py` |

Phase 4 adds a ledger and money to this set. It does not add a second
idempotency mechanism, a second error taxonomy or a second unit of work.

---

## 5. Decisions required before implementation

Numbered plan-locally. Each accepted ruling becomes an entry in
`docs/discovery/open-decisions.md` and the decision register.

**P4-D1, P4-D2 and P4-D3 blocked the first production-code edit and were ruled
on 2026-08-28 as OD-48, OD-49 and OD-50.** P4-D4, P4-D5 and P4-D6 remain open
and block the gate, not the start.

### P4-D1 — Does Phase 4 add a physical ledger table? · **RULED 2026-08-28 → OD-48**

**Ruled by Peter Duscha on 2026-08-28: Option A. Phase 4 adds no migration and
no physical ledger table.** Canonical record: **OD-48**. The rest of this
subsection is the recommendation as it stood, retained as the rationale the
ruling accepted.

**Recommendation: Option A — no new migration in Phase 4.**

*Option A (recommended).* The ledger is defined in `domain/` with a repository
protocol in `application/` and an in-memory reference adapter used by contract
tests. Durable idempotency uses the existing `idempotency_keys` table under a
Phase-4-owned scope, giving real PostgreSQL evidence for retry, conflicting
reuse and concurrent callers without a new table. No migration is added, so the
mandatory logical-schema artifact and its independent review are not triggered.

Why: `docs/project-management/data-migration-register.md` assigns
`wallet.balance_copper` (P–S), `wallet.moradinium` (T), `wallet.debt_copper`
(AC) to **5.2**, `downtime.thousandth_days` (I) to **5.5**, and
`lifestyle.living_cost_weeks` (J) to **5.3**. The register states that no row may
have two write-authoritative targets and no row moves to `Database` until its
owning package records typed target, transformation, control totals, unresolved
records and Data Owner acceptance. A Phase 4 balances or wallet table would
pre-empt that ownership, and the handover independently forbids inventing "a
generic character-state store or Phase 5 feature schema".

*Option B.* Add a generic append-only ledger table now. This is a material
schema addition: under `.agents/AGENTS.md` and the handover, **code work stops**
until an ER diagram and schema decision table covering ownership, cardinalities,
keys, constraints, nullability, delete behavior, history/effective dating,
vocabulary sources, unresolved records, access patterns and source-to-target
control totals has received independent review. Add roughly 3–5 days and a
review cycle to §7, and accept the ownership collision with 5.2.

*Consequence of A, stated plainly so the gate is not surprised:* Phase 4 produces
**no new** PostgreSQL constraint, append-only-trigger or runtime-role evidence
for a ledger table, because it creates none. That evidence is owed by package 5.0
or 5.2 when the physical ledger lands. The handover's requirement for it is
conditional on "new persistence", and under Option A there is none.

### P4-D2 — The downtime unit and invalid persisted values · **RULED 2026-08-28 → OD-49**

**Ruled by Peter Duscha on 2026-08-28: integer thousandth-days in the domain,
refuse rather than round, and preserve today's `/info` rendering for an invalid
cell.** Canonical record: **OD-49**.

`Resource.downtime` is a Python float (`models/resource.py:18`) while OD-08 and
the migration register fix the unit at **thousandth-days**.

**Ruling as applied after final OD-52:** the domain `Downtime` value object holds
an **integer count of thousandth-days** and refuses anything else—no rounding or
coercion. Phase 4 leaves `/info` and its legacy loading/rendering unchanged.
Package 5.5 owns the Sheet conversion, explicit invalid-value handling and
character-page representation when downtime receives a real production
consumer.

Confirm: (a) integer thousandth-days as the domain unit; (b) refuse rather than
round in the domain; (c) preserve today's rendering for an invalid cell rather
than surfacing a new error.

### P4-D3 — Denomination counters are a Sheet representation, not a domain concept · **RULED 2026-08-28 → OD-50**

**Ruled by Peter Duscha on 2026-08-28: integer copper only in `domain/`; the
four counters stay a legacy Sheet representation and nothing normalizes a
character's coins on read.** Canonical record: **OD-50**.

The Sheet stores four independent counters. A wallet holding `10 sp` and one
holding `1 gp` are the same 100 cp but **print differently**, so the visible
output is not derivable from a copper total. Normalizing on read would silently
change `/info` for many characters.

**Ruling as applied after final OD-52:** `domain/` models money as integer copper
only. The four counters remain a **legacy Sheet persistence/presentation
detail** and `/info` continues rendering them byte-identically through its
untouched legacy path. Package 5.2 owns their migration and the first typed
wallet read model; Phase 4 creates none.

Confirm that carrying both is acceptable, and that nothing normalizes a
character's coins as a side effect of a read.

### P4-D4 — Defer the float-money defects in `/sale` and `/lc` · **RULED 2026-08-28 → OD-51**

**Ruled by Peter Duscha on 2026-08-28: characterize, do not correct.** Canonical
record: **OD-51**.

**Recommendation:** characterize, do not correct. Add tests recording today's
behavior, raise a risk owned by packages 5.7 and 5.3, and change no line of
`Resource.sale` (`models/resource.py:151`) or `Lifestyle.pay_for_weeks` (`models/lifestyle.py:34`). Correcting
them here would be a Phase 5 behavior change made under a Phase 4 authorization.

### P4-D5 — `/info` and the wallet-query boundary · **FINAL AMENDMENT 2026-08-29 → OD-52**

**Finally amended by Peter Duscha on 2026-08-29: `/info` remains unchanged and
Phase 4 creates no temporary wallet query/Sheet adapter.** The platform needs no
`/info` equivalent because players inspect linked characters on its character
pages. Package 5.2 creates the typed wallet query and production adapter with
that page as its first real consumer. Canonical record: **OD-52**.

`/info` is the only read-only command (§4.5). It renders name, level, badge,
lifestyle, optional Bastion and resources — broader than "one bounded
money/resource query".

Both earlier alternatives—routing `/info` and building an adapter-only query—
are superseded. No replacement Discord command or speculative query is added.

*Observation, not a proposal:* `/info` performs **no authorization** beyond
guild membership. Any guild member can read any character's wallet. Phase 4 is
explicitly forbidden from changing authorization, so this is preserved exactly
and raised as a risk for package **5.1**, whose gate is already
"profile-migration and read-path authorization review".

### P4-D6 — Gate authority and the named Independent Reviewer · **RULED 2026-08-28**

**Ruled by Peter Duscha on 2026-08-28: Codex is the Independent Reviewer for the
Phase 4 gate, performing the implementation review. No separate security-focused
review is required**, on the ground that the package adds no authentication,
authorization, session, network or privacy surface. The reviewer did not and
will not implement the package.

The Phase 4 gate is "dependency direction and domain correctness". The
gate-authority table has no row of that name; it sits between
**Architecture/schema** and **Rules/economy/settlement**.

**Recommendation:** required recommendations from Technical Lead, Product Owner,
Data Owner and an Independent Reviewer; approval by the Acceptance Authority. A
separate security-focused review is **not** proposed as mandatory, because the
package adds no authentication, authorization, session, network or privacy
surface — but §16.4's "trades and multi-actor atomicity" checkpoint is close
enough to the ledger's subject matter that the Acceptance Authority may
reasonably require one.

**Peter must name the Independent Reviewer.** Under
`docs/project-management/README.md` this is a mandatory checkpoint: if no
reviewer who did not implement the work is available, the package remains
`deferred` and the gate is not approved on the implementer's own recommendation.
Codex has held this role for Phases 2 and 3.

---

## 6. Roles

| Role | Assignee | Note |
|---|---|---|
| Product Sponsor / Acceptance Authority | Peter Duscha | records the gate decision |
| Product Owner | Peter Duscha | rules P4-D2…P4-D5 |
| Data Owner | Peter Duscha | rules P4-D1 |
| Technical Lead (working) / implementer | Claude — **proposed, pending Peter's designation** | cannot review its own work |
| Independent Reviewer | **Codex**, named by Peter Duscha on 2026-08-28 | implementation review of the Phase 4 gate package; did not implement it |
| Security Reviewer | **none required**, ruled 2026-08-28 | the package adds no authentication, authorization, session, network or privacy surface |
| Operations Owner | Peter Duscha | no deployment in this package |
| Delivery Lead | Peter Duscha | status, RAID, change control |

---

## 7. Work breakdown and three-point estimate

Units are focused implementer-days for one implementer, excluding blocked time
and excluding the maintainer's own decision and review time (§0.4).

| WP | Deliverables (§2.1) | O | ML | P |
|---|---|---|---|---|
| WP-0 | Characterization completion: pin today's output and refusal behavior for `Resource`, `Lifestyle`, `calculate_exchange` and `/info` before any refactor | 0.5 | 1.0 | 2.0 |
| WP-1 | 1, 2 — money and resource value objects; construction, conversion, arithmetic, refusal; the `domain/` dependency guard (12) | 1.0 | 1.5 | 2.5 |
| WP-2 | 5, 7 — command/query envelope, typed results and errors, expected-version precondition | 0.5 | 1.0 | 2.0 |
| WP-3 | 3, 4 — ledger entries, balanced transactions, compensating entries, append-only enforcement, atomicity under injected mid-transaction failure | 1.0 | 2.0 | 3.5 |
| WP-4 | 6 — durable idempotent execution on `idempotency_keys`: retry, conflicting reuse, concurrent callers, against real PostgreSQL | 1.0 | 1.5 | 3.0 |
| WP-5 | **Removed by final OD-52 amendment** — wallet query and adapter move to package 5.2 with their real consumer | 0.0 | 0.0 | 0.0 |
| WP-6 | 10 — falsification evidence, then the full serial verification in §12 | 0.5 | 1.0 | 2.0 |
| WP-7 | 11 — submission, traceability, status, change log, RAID | 0.5 | 1.0 | 1.5 |
| | **Total** | **5.0** | **9.0** | **16.5** |

PERT expectation `(O + 4ML + P) / 6` = **9.6 days**.

**Separately, and not inside the figures above:**

- Independent review: 0.5–1.0 day of reviewer capacity.
- Remediation allowance: **2.7 days** (30% of ML). Phases 2 and 3 each ran
  several remediation cycles; a zero allowance would be a forecast contradicted
  by this project's own history.
- Contingency: **2.0 days**, matched to R-P4-1 and R-P4-2 in §10.

**Against the roadmap.** §12 targets 5–10 days. ML is 9.0 and PERT is 9.6,
within the range before review and remediation. This is
reported rather than absorbed, per §0.4.

**Confidence: moderate.** Upward drivers: the characterization inventory in §4
is already complete; idempotency, errors, unit of work and version columns
already exist and are proven; the unconsumed query/adapter work is removed.
Downward drivers: P4-D1 could turn into Option B
and add a schema artifact plus a review cycle; the ledger's atomicity and
compensating-entry evidence has no existing shape in this repository to copy;
and the falsification requirement — mutate each invariant, record the failing
assertion — is real work that project history shows is where cycles are spent.

---

## 8. Capacity assumptions

- One implementing agent working the package serially; no parallel package.
- Peter available for six decisions (§5) before implementation starts, and for
  the gate decision after review.
- One Independent Reviewer available for one review plus at least one
  re-review after remediation.
- No calendar dates are proposed. Under §0.4 and the governance README, effort
  is not converted into a promised date until reviewer and maintainer
  availability is known. Peter supplies those windows; this plan does not
  assume them.

---

## 9. Dependencies, environment and unresolved items

### 9.1 Dependencies

| Ref | Item | State |
|---|---|---|
| Phase 3 gate | predecessor | **Approved 2026-08-28** |
| D-04 | shared ledger/idempotency/domain foundations, needed by Phase 5 mutations | **Closed 2026-08-29** when Peter approved the Phase 4 gate; this package produced the evidence for that later decision |
| D-01b | per-vocabulary readiness | **Not required.** Phase 4 migrates no field and introduces no controlled vocabulary |
| OD-03, OD-04, OD-05, OD-09, OD-28, OD-39 | rule decisions blocking Phase 5 packages | **Not required for Phase 4.** None of them governs a value object, a ledger invariant or `/info`'s output. They stay blocking for their own packages |
| OD-08 | downtime recorded to three decimals = thousandth-days | **Closed 2026-07-30**, and is the basis for P4-D2 |

### 9.2 Environment — verified 2026-08-28, not assumed

| Requirement | State |
|---|---|
| Bot test interpreter | `/opt/discord-bots/venv/bin/python`, pytest 8.4.2, Python 3.12.3 — **present** |
| Web test interpreter | `/opt/discord-bots/venv-web/bin/python`, pytest 8.4.2, Python 3.12.3 — **present** |
| Disposable PostgreSQL | `freedom_test` over the local Unix-domain socket — **reachable**, PostgreSQL **16.15**. (Earlier P3.3 evidence cites 16.14 on this host; the server has since taken a patch update. No Phase 3 claim is restated here on that basis.) |
| Node | v24.19.0 — **present**, for the Foundry module suite |
| Formatter / linter / type checker | **None configured.** No `pyproject.toml`, `setup.cfg`, `.ruff.toml` or `.flake8` exists. The submission will state this as "not configured" rather than as "passed" |
| Staging | **Does not exist.** Not required: this package deploys nothing, changes no configuration and adds no persistent state. No staging-class check appears in §11 |

### 9.3 Unresolved rule and authority items

The six decisions in §5. Nothing else. No rule ambiguity in §4 blocks a Phase 4
slice; the two that touch live behavior (RC-A7's Moradinium rate, RC-D4's debt)
are deliberately left unimplemented rather than resolved here.

---

## 10. RAID impact

Proposed rows, to be entered in `docs/project-management/raid-register.md` when
this plan is accepted. They are not entered now, because a register row for a
package that has not started would assert readiness this document is asking for.

| Proposed | Type | Statement | Owner | Trigger / mitigation |
|---|---|---|---|---|
| R-P4-1 | Risk | A ledger with no physical table is judged insufficient at the gate, after the work is done | Technical Lead | Ruled up front by P4-D1. If Option B is chosen, the schema artifact is produced and independently reviewed **before** code, per the handover |
| R-P4-2 | Risk | Characterization tests freeze legacy float-money behavior (§4.4) and are later mistaken for accepted policy | Product Owner | Every such test names the defect and its owning package in its docstring; §4.4 and P4-D4 are quoted in the submission |
| R-P4-3 | Risk | `/info` exposes any character's wallet to any guild member; Phase 4 preserves this exactly | Product Owner | Raised to package **5.1**, whose gate already covers read-path authorization. Not fixed here — changing authorization is an explicit Phase 4 exclusion |
| A-P4-1 | Assumption | No staging environment is required for Phase 4 | Operations Owner | Holds while the package deploys nothing and adds no persistent state. Void the moment P4-D1 resolves to Option B |
| A-P4-2 | Assumption | The established database-enabled web skip count of **80** still holds for an unchanged tree | Technical Lead | Measured at the start of implementation, before any edit, and again at submission. A different figure is explained, not adjusted to |
| D-04 | Dependency | Unchanged and Open | Technical Lead | Closes at the Phase 4 gate, not here |

---

## 11. Requirement-to-evidence traceability

### 11.1 Phase 4 acceptance criteria (implementation-plan §12)

| Criterion | Evidence to be produced |
|---|---|
| Domain imports no infrastructure frameworks | Static dependency guard over every module in `domain/`, asserting no import of `discord`, `google*`, `sqlalchemy`, `fastapi`, `psycopg`, `config` or `os.environ`. Falsified by adding one such import |
| Money uses integer copper | Table-driven construction/conversion/arithmetic tests; a test asserting no `float` reaches a money constructor or crosses the ledger boundary; refusal of mixed resource types |
| Duplicate mutations are safe | Retry returns the original receipt with no second effect; conflicting reuse of one key fails closed; two concurrent callers produce exactly one durable effect — against real PostgreSQL |
| Concurrent stale updates are detected | An expected-version precondition that fails raises `ConcurrencyConflictError` and commits nothing; no partial commit is observable |
| Tests characterize intended current behavior | The §4 inventory turned into tests: `/info` output byte-identical as untouched regression evidence, `Resource` refusal behavior, `calculate_exchange` outcomes, boundary and zero cases |
| Application boundaries have real Phase 4 consumers | WP-2 through WP-4 integrate envelopes, ledger repository/transaction contracts, optimistic concurrency and durable idempotency in concrete command execution tests |

### 11.2 Handover "required tests and falsification"

Every item is mapped, including the two that Option A makes conditional.

| Required | Mapped to |
|---|---|
| value construction, conversion, arithmetic, refusal | WP-1 |
| integer-copper / no-float boundary tables | WP-1 |
| command/query separation | WP-2 defines the boundary and WP-3/WP-4 consume the command side; no unused read query is introduced |
| idempotency: retry, conflicting reuse, concurrent callers | WP-4, real PostgreSQL |
| stale version, no partial commit | WP-2/WP-3 |
| atomicity under injected mid-transaction failure | WP-3 |
| append-only and compensating entries | WP-3 |
| `domain/` dependency guard | WP-1 |
| wallet-query/adapter tests | **Deferred to package 5.2**, where the character page is the first real consumer |
| characterization of unchanged command output and authorization | WP-0; Phase 4 does not touch the command |
| PostgreSQL constraint/concurrency/runtime-role evidence for **new persistence** | **Conditional.** Under P4-D1 Option A no new table exists; the idempotency evidence in WP-4 runs against the existing table and its existing constraints. Under Option B this becomes mandatory and adds a migration, an ER artifact and a review cycle |

**Falsification.** For each invariant above, the submission records the exact
mutation applied (invariant removed or reversed), the assertion that then
failed, and the restoration of the tree by checksum. An invariant whose test
still passes when the invariant is removed is reported as such, not quietly
strengthened.

### 11.3 §13.2 mandatory-scenario matrix

The plan permits `not applicable` only with a written rationale accepted by the
Independent Reviewer, and forbids omitting the row.

| Scenario | Disposition |
|---|---|
| insufficient resources | **Applicable** — ledger and value-object refusal |
| invalid and negative values | **Applicable** — construction refusal, boundary tables |
| duplicate Discord interaction | **Applicable** — idempotency key identity, WP-4 |
| double approval | **Not applicable** — no approval workflow exists in Phase 4; owned by Phase 6 |
| stale optimistic version | **Applicable** — WP-2 |
| concurrent trade/edit | **Applicable in the concurrency sense** (two concurrent callers, one effect); **not applicable as a trade** — `/trade` is a Phase 5.8 mutation this package does not touch |
| partial external failure | **Applicable** — injected mid-transaction failure, WP-3 |
| authorization denied | **Applicable as characterization only** — `/info` is untouched and its existing behavior remains pinned; the new adapter exposes no user-facing authorization surface |
| guild role removed | **Not applicable** — no role-dependent surface is added; Phase 3 owns role evaluation |
| Actor renamed | **Applicable** — the existing ambiguous/missing-name refusals are characterized (`models/actor.py:26`) |
| Foundry duplicate/missing mapping | **Not applicable** — no Foundry surface |
| malformed or tampered Foundry snapshot | **Not applicable** — no Foundry surface |
| migration failure and recovery | **Not applicable under Option A** — no migration is added. Becomes applicable under Option B |
| mission settlement across characters | **Not applicable** — Phase 9 |
| correction after approval | **Applicable in kind** — compensating entries, WP-3 |
| attendance reconnect and late join | **Not applicable** — Phase 8 |
| unsupported Foundry version | **Not applicable** — no Foundry surface |
| pinned catalogue snapshot / checksum | **Not applicable** — Phase 5.6a |
| idempotent catalogue re-import, stale preview | **Not applicable** — Phase 5.6a |
| malformed/duplicate/renamed upstream item records | **Not applicable** — Phase 5.6a |
| source disablement with retained inventory | **Not applicable** — Phase 5.6a |
| unique-item transfer, concurrent consumable use | **Not applicable** — Phase 5.6a |
| stale crafting project | **Not applicable** — Phase 5.6b |
| atomic craft completion across inventory/resources/ledger/audit | **Not applicable as a craft**; the ledger half is exercised generically by WP-3 |

---

## 12. Verification to be run at submission

Narrow tests first, then the suites **serially** — they share one disposable
database (finding F-6), so a parallel run is a different verification, not a
faster one.

```sh
export TEST_DATABASE_URL='postgresql+psycopg:///freedom_test'
/opt/discord-bots/venv/bin/python     -m pytest -q -rs tests/test_*.py
/opt/discord-bots/venv-web/bin/python -m pytest -q -rs tests/web
node --test "foundry-module/tests/"*.test.mjs
```

Plus: focused tests in fresh processes where isolation matters; `compileall`
under both interpreters; `git diff --check`; a secrets, real-data,
generated-artifact and unrelated-edit review of the diff. Alembic
heads/branches and migration upgrade/downgrade/upgrade checks apply **only**
under P4-D1 Option B.

Skips are stated exactly. A database-skipped web run is not evidence: the
established database-enabled skip count is **80** unless this package
deliberately and explainably changes collection, and A-P4-2 requires that figure
to be measured against the unchanged tree before implementation begins.

---

## 13. Deployment, rollback and recovery

- **Deployment effect: none.** No service, unit file, Caddy configuration,
  environment variable or credential changes. Nothing is restarted.
- **Persistence effect under Option A: none.** No migration, no new table, no
  new constraint, no grant change. The existing `idempotency_keys` table is
  read and written under a new `scope` value only.
- **Rollback under Option A:** revert the commit. There is no schema state to
  unwind and no data to reconcile. Rows written under the Phase 4 idempotency
  scope by tests exist only in the disposable database.
- **Rollback under Option B:** the migration must carry upgrade,
  downgrade/recovery, constraints, runtime-role grants and direct PostgreSQL
  tests, and §14.3's roll-forward-over-editing rule applies. Estimated
  separately; not covered by §7's figures.
- **Live-service effect: none.** The bot's implementation and behavior are
  unchanged; no command is touched.

---

## 14. Objective stop conditions

Implementation stops and returns to Peter if any of these occurs:

1. A material schema addition proves necessary — stop before writing it, produce
   the ER diagram and schema decision table, obtain independent review.
2. A rule ambiguity is found that a slice's behavior depends on — stop that
   slice, document the question, do not choose.
3. A wallet query, Sheet wallet adapter, `/info` change or portal wallet view
   appears necessary—stop; all are outside final Phase 4 scope.
4. Any need appears to write to the Sheet, to production PostgreSQL, to Discord
   or to Foundry — stop immediately.
5. The pre-implementation web skip count is not 80 and the cause is not
   understood — stop; the baseline is not what the evidence contract assumes.
6. Effort passes the pessimistic figure in §7 — stop and re-plan under §0.4
   rather than compress review or remediation.
7. An invariant's falsification shows the test still passes with the invariant
   removed — stop treating that invariant as evidenced, and report it.

---

## 15. What this package does not claim

It does not close D-04. It does not approve the Phase 4 gate. It does not
release any Phase 5 mutation, cutover or Sheet retirement. It does not assert
readiness by its own existence: readiness is met when Peter rules the §5
decisions, designates the implementer and names an Independent Reviewer.

---

## 16. Pre-implementation baseline, measured 2026-08-28

Assumption **A-P4-2** and stop condition **5** require this figure to be
measured against the **unchanged** tree before implementation begins, so that a
later count means something. Measured on the tree as it stands, with only the
uncommitted documentation changes present and no production code touched:

| Suite | Command | Result |
|---|---|---|
| Bot | `/opt/discord-bots/venv/bin/python -m pytest -q -rs tests/test_*.py` | **2447 passed, 0 skipped**, 1 warning, 137.88 s |
| Web | `/opt/discord-bots/venv-web/bin/python -m pytest -q -rs tests/web` | **2824 passed, 80 skipped**, 139.01 s |
| Foundry module | `node --test "foundry-module/tests/"*.test.mjs` | **171 pass, 0 fail, 0 skipped**, 203 ms |

`TEST_DATABASE_URL='postgresql+psycopg:///freedom_test'` was exported for both
Python suites, which were run **serially**.

**The web skip count is 80, exactly the established figure**, and `-rs` accounts
for every one of them: 54 in `tests/web/test_p3_2_matrix.py:155` and 26 in
`tests/web/test_p3_3_matrix.py:198`, both reading *"permitted cells are asserted
by the per-route success cases"*. **None is a database skip** — which is the
thing the count exists to detect. A-P4-2 holds and stop condition 5 is not
triggered.

Under `.agents/AGENTS.md` this baseline is evidence about *this* tree only. It
is re-run against the tree actually submitted, and the submitted figures are the
ones the gate reads.

---

## 17. Delivered — actual results against this plan, 2026-08-29

> **Independent-review update, 2026-08-29:** delivery did not pass the gate.
> Codex returned Blocking findings P4-R1 (unsafe concurrent retraction) and
> P4-R2 (service principals bypass application authorization), plus Important
> finding P4-R3 (the idempotency digest omits authoritative occurrence-time and
> caller facts). The gate is deferred, D-04 remains Open, and the remediation
> allowance in §7 is active. See `phase-4-submission.md` and the overwritten
> `Handover information`. No Phase 5 work is released.

Added at the WP-7 handoff. It records what was actually produced and where the
delivery departed from the plan, so a reviewer compares against a statement
rather than reconstructing one. **It closes no gate and claims none.**

### 17.1 Scope §2.1, deliverable by deliverable

| # | Deliverable | State | Where |
|---|---|---|---|
| 1 | `domain/money.py` | **Delivered** (WP-1) | integer-copper `Money`, rate constants pinned against `models/exchange.py`, `sum_money()` |
| 2 | `domain/resources.py` | **Delivered** (WP-1) | `Moradinium` (unit 1), `Downtime` (unit 1/1000 day, OD-08/OD-49) |
| 3 | `domain/ledger.py` | **Delivered** (WP-3) | append-only entries, balanced transactions, compensating entries |
| 4 | `application/ledger.py` | **Delivered** (WP-3) | `LedgerRepository` and `LedgerUnitOfWork` owned by their consumer, plus `LedgerCommandService`, which calls every method on both |
| 5 | `application/commands.py` | **Delivered** (WP-2) | envelope, `ExpectedVersion`, typed results and failures; the query convention documented **without** a protocol, per final OD-52 |
| 6 | Durable idempotent execution on the existing `idempotency_keys` table | **Delivered** (WP-4) | scope `ledger.post_transaction`; no migration, under OD-48 Option A |
| 7 | Optimistic-concurrency precondition handling | **Delivered** (WP-2/WP-3) | on the existing `ConcurrencyConflictError`. **Deviation:** the plan expected the existing `characters.version` column; the Phase 4 aggregate is the ledger book, whose version is its accepted-transaction count in the reference repository. No character row is read or written, which is what OD-48 and the migration register require |
| 8 | Characterization tests | **Delivered** (WP-0) | 36 tests |
| 9 | `domain/` dependency guard | **Delivered** (WP-1), extended (WP-3) | allowlist over every `domain/` module; now covers `ledger.py` |
| 10 | Falsification evidence | **Delivered** (WP-6) | 16 mutations, none surviving; restoration verified by SHA-256 |
| 11 | Submission, traceability, status, change log, RAID | **Delivered** (WP-7) | this section, `phase-4-submission.md`, status update 113, `C-P4-G`, RAID rows R-P4-1…R-P4-4, A-P4-1, A-P4-2 |

### 17.2 Departures from the plan, stated rather than absorbed

1. **WP-5 was removed** by the final OD-52 amendment before implementation
   began (change-log `C-P4-F`). No wallet query, temporary Sheet adapter,
   replacement command, route, template or view-model field exists.
2. **Deliverable 7's aggregate is the ledger book, not `characters.version`.**
   See the table above. The plan named the column as the *existing* concurrency
   mechanism to reuse; the mechanism — a version read before deciding, enforced
   where the write becomes visible, surfacing as `ConcurrencyConflictError` — is
   the one reused. A Phase 4 command that wrote a character row would be a
   Phase 5 mutation.
3. **The precondition is decided at commit, not at read.** The first
   implementation compared the version when the transaction opened, which let two
   concurrent callers who both read version 0 both commit. `append()` now carries
   the expected version into `LedgerBook.publish`, which re-checks it under the
   book's lock in the critical section that appends — the shape of
   `SqlAlchemyCharacterRepository.save`'s conditional update. Mutation 16 in the
   submission is the falsification of the corrected fence.
4. **A structural account distinction was introduced** — `AccountKind.HELD` and
   `AccountKind.COUNTERPARTY`. §11.3 requires the *insufficient resources*
   scenario to be applicable, and without knowing which side of the boundary an
   account sits on, "insufficient" is inexpressible in double-entry. It is
   double-entry's own distinction and **not** a Freedom Blades chart of accounts:
   no named account is enumerated and no economy policy is decided. Flagged for
   the Independent Reviewer.
5. **A transaction may not span two books.** One command therefore has exactly
   one precondition. Character-to-character trade is package 5.8 and the refusal
   names it. Flagged for the Independent Reviewer as a deliberate restriction
   rather than an oversight.
6. **Two existing Phase 3 files were modified**, which §2.2's "no security
   surface change" did not anticipate. `application/web/audit_search.py` gains
   the four Phase 4 ledger payload keys, without which the audit projection would
   silently render them as `(not rendered)`; and
   `tests/web/test_p3_4_static_assets.py` declares the Phase 4 production files,
   following that guard's own rule that an exception is enumerated rather than
   left to erode it. Neither changes a route, a capability check, a session or a
   bound. Both are set out in the submission's WP-6 section, with the finding
   that the second guard had been failing since **WP-1** and was not seen because
   WP-0 and WP-1 ran the bot suite only.

### 17.3 §11.1 acceptance criteria — evidence produced

| Criterion | Evidence |
|---|---|
| Domain imports no infrastructure frameworks | `tests/test_p4_domain_isolation.py`, allowlist over all 11 `domain/` modules including `ledger.py`; falsified by mutation 24 |
| Money uses integer copper | `tests/test_p4_domain_quantities.py`; `float`, `Decimal`, `bool` and bare `int` refused at the ledger boundary too (`kind_of`); falsified by mutations 25, 26 |
| Duplicate mutations are safe | `tests/test_p4_idempotent_execution.py` against real PostgreSQL: retry, conflicting reuse, two concurrent callers, and the unique index asserted directly; falsified by mutations 17, 18, 19 |
| Concurrent stale updates are detected | early refusal and the commit-time fence; falsified by mutations 15 and 16 |
| Tests characterize intended current behavior | WP-0's 36 tests; `/info` and its renderer untouched |
| Application boundaries have real Phase 4 consumers | `LedgerCommandService` calls every method of `LedgerRepository` and every field of `CommandEnvelope`; asserted by `test_every_ledger_repository_method_has_a_phase_4_consumer` |

### 17.4 §11.3 mandatory-scenario matrix — as delivered

Every row keeps its planned disposition. The applicable ones now name tests:

| Scenario | Delivered evidence |
|---|---|
| insufficient resources | `test_a_held_account_may_not_go_below_zero`, `test_spending_one_more_than_is_held_is_refused`, `test_spending_exactly_what_is_held_is_permitted` |
| invalid and negative values | construction refusals across `tests/test_p4_commands.py` and `tests/test_p4_ledger_domain.py` |
| duplicate Discord interaction | `test_a_repeated_key_with_identical_content_executes_the_effect_once` (PostgreSQL) |
| stale optimistic version | `test_a_stale_expected_version_applies_nothing`, `test_a_stale_expected_version_commits_nothing_to_the_database`, `test_a_book_that_moves_on_before_the_commit_refuses_the_posting` |
| concurrent trade/edit (concurrency sense) | `test_two_concurrent_callers_of_one_key_produce_one_durable_winner`, `test_two_concurrent_callers_of_two_keys_produce_one_version_winner` |
| partial external failure | `test_an_injected_idempotency_failure_leaves_no_posted_transaction`, `test_an_injected_audit_failure_…`, `test_an_effect_failure_cannot_publish_success`, `test_a_failed_durable_commit_retracts_the_posting` |
| authorization denied | characterization only for `/info`, unchanged; the new service additionally refuses an ordinary member and a revoked member (`test_an_ordinary_guild_member_is_refused`, `test_a_user_who_is_no_longer_a_guild_member_is_refused`) |
| Actor renamed | WP-0's existing ambiguous/missing-name characterization |
| correction after approval (in kind) | `test_a_correction_is_a_new_transaction_that_reverses_the_original`, `test_the_corrected_transaction_remains_exactly_as_accepted`, `test_a_correction_is_itself_idempotent` |
| every row marked *not applicable* in §11.3 | unchanged, for the reasons given there. Nothing was reclassified to make evidence easier |

### 17.5 Effort

Not converted into a claim. The package was implemented in one continuous
working session rather than measured against the §7 day figures, so no actual is
asserted against the 5.0 / 9.0 / 16.5 estimate. **Stop condition 6 — effort
passing the pessimistic figure — was not reached.**

## 18. Remediation R1 — actual results, 2026-08-29

Independent review returned P4-R1 and P4-R2 Blocking and P4-R3 Important. This
section records the remediation's outcome against this plan. The full record is
`phase-4-submission.md`, *Remediation R1*. **No finding is closed here**; Codex
re-reviews and Peter Duscha records the gate decision.

### 18.1 Stop conditions — none was reached

| Stop condition | Outcome |
|---|---|
| 1 — a material schema addition is proposed | **Not reached.** OD-48 holds: no ledger table, no migration, no wallet/balance store, no credential table. The P4-R1 correction was chosen precisely so that it needs none |
| conflicts with an accepted authorization decision | **Not reached, and deliberately avoided.** `ServicePrincipalScope` was not widened, so the Foundry snapshot credential's grantable authority is unchanged. The ledger scope is consumer-owned. Whether the two vocabularies should eventually merge is recorded as an open question for the maintainer rather than decided |
| changes production authority, bot behaviour, Phase 5 scope, privacy, deployment or rollback | **Not reached.** None of them changes |
| reveals another material atomicity/authorization/data-integrity defect | **Not reached.** Two Phase 3 *guard* failures were caused and are reported (submission, *Two web-suite failures…*); both are controls working, not defects found |
| cannot reproduce the database-enabled environment or the skip count | **Not reached.** `TEST_DATABASE_URL` exported throughout; the web skip count is exactly **80**, both reasons printed by `-rs`, none a database skip |

### 18.2 §12 verification — as actually run

| Check | Planned | Actual |
|---|---|---|
| Narrow Phase 4 tests | run | **178 passed**, 3.43 s |
| Bot suite, serial | run | **2890 passed, 0 skipped**, 1 warning, 144.30 s (was 2840; +50 remediation tests) |
| Web suite, serial | run, skip count 80 | **2824 passed, 80 skipped**, 139.51 s; skip reasons are the two permission-matrix modules' permitted cells |
| Foundry module | run | **171 pass, 0 fail** |
| `compileall`, both interpreters | run | clean |
| `git diff --check` | run | clean |
| Formatter / linter / type checker | run **if configured** | each remains **unconfigured**; none run, none claimed |
| Falsification | required | the handover's **six** mutations, all detected, tree restored by copy and verified with `sha256sum -c` — all eight files match, no mutation survives |

### 18.3 Departures from the plan, stated rather than absorbed

1. **`LedgerBook.publish` and `LedgerBook.retract` are gone**, not corrected.
   §17.2's transaction shape is superseded: the book is now held across the
   durable commit and postings become visible only after it returns. The
   published-then-retracted ordering this plan described is withdrawn as unsafe.
2. **`LedgerCommandService` gained a required constructor dependency**
   (`principals`). §17.1's boundary list grows by one port, and it has a real
   Phase 4 consumer — the service itself — so the "no speculative protocol" rule
   is satisfied for it as for the others.
3. **The §17.4 mandatory-scenario row for partial external failure** cites
   `test_a_failed_durable_commit_retracts_the_posting`, which is renamed
   `test_a_failed_durable_commit_leaves_no_posting`; the property is unchanged
   and the mechanism is not. The row gains the new two-caller regressions.
4. **Two tracked production modules outside §2.1's list changed**, both narrowly
   and both within the remediation brief's "narrowly necessary accepted
   authorization" allowance: `application/idempotency.py` gains
   `canonical_request_hash`, and `application/service_principals.py` has its
   identifier rule extracted, behaviour-preserving. Both are declared in the
   P3.4 scope guard with their reasons.
5. **Effort is again not converted into a claim.** The remediation was one
   continuous working session; stop condition 6 was not reached.

## 19. Independent re-review and Remediation R2 — 2026-08-29

Codex re-reviewed Remediation R1. P4-R1 and P4-R2 are materially remediated,
and P4-R3's requested digest correction is present. The gate remains deferred
for two defects: **P4-R4 Blocking**, requiring authorization before any
`compensate()` lookup with one resolved attribution throughout the operation;
and **P4-R5 Important**, requiring one correlation ID across envelope, ledger,
receipt and audit with mismatch refusal before any unit of work opens.

These corrections change no approved policy, schema, data authority, credential
vocabulary, deployment contract or Phase 5 boundary. Claude may remediate them
without another maintainer ruling. Add direct application and PostgreSQL-backed
no-effect evidence, then repeat narrow and complete serial verification. Restore
the disposable test database's missing grant state before citing the bot suite;
the re-review's 2887/2/1 run is not green evidence.

No finding or gate is closed here. D-04 remains Open and Phase 5 remains blocked
pending Remediation R2 and Codex re-review.

## 20. Remediation R2 — actual results, 2026-08-29

Codex's re-review of Remediation R1 (§19) returned **P4-R4 Blocking** and
**P4-R5 Important**. This section records the remediation's outcome against this
plan. The full record is `phase-4-submission.md`, *Remediation R2*. **No finding
is closed here**; Codex re-reviews and Peter Duscha records the gate decision.

### 20.1 Stop conditions — none was reached

| Stop condition | Outcome |
|---|---|
| 1 — a material schema addition is proposed | **Not reached.** OD-48 holds: no ledger table, no migration, no wallet/balance store, no role grant. Both corrections are inside `application/ledger.py` |
| conflicts with an accepted authorization decision | **Not reached.** No scope, vocabulary or credential changed. `ServicePrincipalScope` and the Foundry credential set are untouched; the R1 open question about merging the vocabularies is left exactly as it was |
| changes production authority, bot behaviour, Phase 5 scope, privacy, deployment or rollback | **Not reached.** None of them changes. `post()`'s behaviour is unchanged by design |
| reveals another material atomicity/authorization/data-integrity defect | **Not reached.** No new defect was found, and no Phase 3 guard failed this time — the P3.4 scope guard needed no new declaration because no tracked production module changed |
| cannot reproduce the database-enabled environment or the skip count | **Not reached.** `TEST_DATABASE_URL` exported throughout; the web skip count is exactly **80**, both reasons printed by `-rs`, none a database skip; the bot suite reports **0** skips |

### 20.2 §12 verification — as actually run

| Check | Planned | Actual |
|---|---|---|
| Narrow Phase 4 tests (the handover's five files) | run | **415 passed**, 4.40 s (was 376; **+39** R2 regressions) |
| Bot suite, serial | run | **2929 passed, 0 skipped**, 1 warning, 145.37 s (was 2890) |
| Web suite, serial | run, skip count 80 | **2824 passed, 80 skipped**, 137.12 s; skip reasons are the two permission-matrix modules' permitted cells |
| Foundry module | run | **171 pass, 0 fail** |
| `compileall`, both interpreters | run | clean |
| `git diff --check` | run | clean |
| Formatter / linter / type checker | run **if configured** | each remains **unconfigured**; none run, none claimed |
| Backup/restore drill | required before citing a bot figure | `tests/test_database_backup_restore.py` **35 passed**; `tests/test_runtime_grants_live.py` passes. The grant state is present in this environment and **no grant was altered** — see §20.3 item 4 |
| Falsification | required | **four** mutations plus one informative weaker variant, all detected; `application/ledger.py` restored by copy and verified `OK` with `sha256sum -c`; no mutation survives |

### 20.3 Departures from the plan, stated rather than absorbed

1. **`LedgerCommandService` gains a private execution path**, `_post_resolved`,
   which accepts an already-resolved `_Attribution`. §17.1's boundary list is
   unchanged — this is not a new port — but the service's internal shape is, and
   the reason is that one compensation must perform exactly one authority
   resolution. The public surface stays two methods, `post` and `compensate`,
   and a reflection test asserts neither accepts an attribution.
2. **A new declared refusal code**, `correlation_mismatch`. `REFUSAL_CODES`
   remains closed; the set grows by one, and an adapter branching on it must
   handle the new member. There is no production adapter.
3. **The §11.2 falsification list grows.** R2 adds four mutations of its own —
   lookup-before-authorization, a second authority resolution, removal of the
   correlation fence, and correlation added to the digest — none of which the
   original handover's six covered, because neither defect existed then.
4. **The bot-suite environment issue the re-review reported could not be
   reproduced, and is reported rather than declared fixed.** The re-review saw
   2887 passed, 2 skipped and 1 failure from the backup/restore drill. Here the
   drill passes and the suite has zero skips, both before and after the R2
   changes. No grant, role or schema was altered by this remediation, and
   `infra/postgresql/runtime-grants.sql.tmpl` is untouched. The submitted figure
   is this session's own 2929/0 run against the finished tree; the earlier
   2890/0 figure is quoted only as the pre-change baseline measured in the same
   session, never carried forward as the result.
5. **A Phase 4 test-fixture change.** Both service test files previously built
   envelopes and transactions with independent `uuid4()` correlation ids, which
   the P4-R5 fence makes a mismatch. The helpers now default both halves to one
   module constant and a test needing a separate attempt passes one fresh id to
   both. Declared because it touched almost every posting in both files, even
   though it weakens no assertion — falsification R2-3 is the evidence.
6. **Effort is again not converted into a claim.** The remediation was one
   continuous working session; stop condition 6 was not reached.

### 20.4 Files changed

One production file — `application/ledger.py`, already declared in the P3.4
scope guard's `PERMITTED_PHASE_4_PRODUCTION` from WP-3 — and two test files,
`tests/test_p4_ledger_service.py` and `tests/test_p4_idempotent_execution.py`.
No tracked production module changed, so the guard needed no new entry.

**No finding or gate is closed here.** P4-R4, P4-R5 and D-04 remain Open, the
Phase 4 gate remains deferred, and no Phase 5 work is released pending Codex's
re-review.
