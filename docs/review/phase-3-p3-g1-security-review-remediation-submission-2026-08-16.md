# P3.G1 — both break-glass attempt budgets now survive the refusal they count

**Date:** 2026-08-16 (sixth P3.G1 remediation of the day) · **Package:** P3.G1 ·
**Author:** working Technical Lead (Claude) · **Corrects:**
`docs/review/phase-3-p3-g1-security-review-2026-08-16.md` — the distinct
security-focused review, which returned *changes requested* on two `[Blocking]`
findings.

**Status: submitted for fresh independent security re-review. Nothing here is
accepted. P3.G1, RAID I-09 and RAID I-10 remain open. P3.2 and P3.3 have not been
started.**

Scope is four production files and two test modules. **No accepted numeric value,
environment variable, route, view model, schema, migration, dependency, deployment
value, runtime grant, provider/engine authority or visual asset changed.**
`.env.example` is unchanged. N-32 and N-33 are enforced as the numeric register
already accepted them; nothing here proposes a new number.

---

## 1. The findings

Quoted in full, because the correction is judged against them rather than a
paraphrase.

> **[Blocking] N-32's per-account WebAuthn assertion budget has no production
> consumer.** … `RateLimiter.check_account()` implements the latter … but no
> production call site invokes it. … Consequently, attempts distributed across
> source addresses are bounded only per address; the accepted ten-attempt,
> sixty-minute account budget is inoperative.

> **[Blocking] N-33's per-grant recovery-attempt counter rolls back on every
> refused matched grant.** … R-09 runs that whole service call inside
> `_in_transaction()` … The increment therefore does not survive the refused
> attempt it is meant to count. … Repeating it from multiple source addresses
> bypasses the per-grant cap; only the separate per-IP counter advances.

Both are accepted without qualification, including the review's judgement that
`test_the_per_grant_attempt_cap_refuses_the_sixth_attempt` overstated what it
proved. That test presented `"wrong-" + token`, which matches no grant row, and
asserted the stored count stayed **zero** — an assertion the defect satisfies
perfectly. It has been renamed and re-scoped rather than deleted, because the
property it really held is worth keeping (§4.1).

### 1.1 One shape, twice

Both findings are the same mistake in two places, and it is the RAID I-09 shape
again: **the control exists, and the path does not reach it.** N-32's second
budget was written, validated, unit-tested and never called. N-33's second budget
was written, called, and then rolled back by the refusal it was counting. In both
cases a green suite was reporting on a mechanism rather than on a request, and in
both cases the per-address budget — which does work — masked the absence, because
the only attacker who notices is one who changes address.

The rule this remediation applies, stated once so a later edit can be checked
against it:

> **An attempt counter must be spent in a transaction that commits whether or not
> the attempt succeeds.** Any counter inside the unit of work it bounds counts
> only the successes, and successes are not what a budget is for.

That rule was already written down and already obeyed for the per-address
counters — `_consume_rate_limit()`'s docstring states it exactly — which is what
made the two second budgets look handled.

---

## 2. Finding 1 — the per-account assertion budget now has a caller

### 2.1 Where the consumption had to go

The budget cannot be spent before the credential is resolved (there is nothing to
spend it against) and must not be spent after verification (a refused assertion
must spend it). So it is spent **between**: after the presented credential id has
been looked up, before any signature is verified.

`BreakGlassService.assertion_subject()` is that lookup and nothing else. It reads
one row, verifies nothing, consumes no challenge, writes nothing and **raises
nothing** — a malformed payload yields an empty subject rather than an exception,
so a caller who sends rubbish takes the ordinary refusal path rather than a
distinguishable one.

`_consume_assertion_account_budget()` in `adapters/web/app.py` runs that lookup
and the resulting `check_account()` in **one short transaction of its own**,
exactly as `_consume_rate_limit()` has always done for the per-address budgets,
and R-08 calls it after the per-address check and before the verification
transaction.

### 2.2 Why an unknown credential also spends a budget

The review requires that unknown credentials stay indistinguishable and that the
fix not create an account-existence oracle. Those two requirements pull against
each other the moment only *known* credentials have a budget: the eleventh attempt
against an enrolled credential would answer `429 rate_limited` while the eleventh
against an invented one still answered `403 invalid`, and that difference is
precisely the fact `begin_assertion()` refuses to disclose by sending an empty
`allow_credentials`.

`RateLimiter.check_credential()` closes it: a credential id that resolves to no
account spends an equivalent budget — the **same** configured limit, the **same**
configured window — in a bucket named by a keyed digest of the credential id.
Both cases therefore refuse at the same attempt with the same externally
meaningful outcome: the same status and coarse error code under the same
configured window. Correlation identifiers intentionally differ between
requests, and literal `Retry-After` values can differ with request timing; neither
is evidence of credential existence.

Three properties of that bucket are stated deliberately:

* **It is keyed.** A credential id is an authenticator's public handle, and
  `auth_rate_limits` is not a place to accumulate a list of them, for the same
  reason N-30 keys the address digest.
* **It is bounded.** Rows are created only by attempts that already passed the
  five-per-address budget, and N-31's sweep removes them after 60 minutes. An
  attacker cannot grow the table faster than five rows per address per ten
  minutes.
* **It is not a second policy.** It reads `webauthn_assertions_per_account` and
  `webauthn_account_window_minutes` — the accepted N-32 numbers — rather than
  introducing any number of its own.

### 2.3 One incidental hardening, disclosed

`complete_assertion()` and `assertion_subject()` now share one credential-id
reader, so the bytes the budget is spent against are the bytes the lookup uses; a
divergence there would have bounded nothing. The shared reader also tolerates a
non-`dict` JSON body, which the old inline parse did not: `[]` posted to R-08 used
to raise `AttributeError` and reach the generic 500 handler, and now takes the
ordinary `403 invalid` path with `no_credential_id` in the audit. The distinct
audit reasons (`no_credential_id` / `malformed_credential_id`) are preserved and
still never reach the browser.

---

## 3. Finding 2 — the per-grant counter is spent outside the redemption

`BreakGlassService.note_recovery_attempt()` increments the grant's counter and
**returns** the refusal rather than raising it. That is the whole correction:
raising inside the transaction that holds the increment is what destroyed it.
`_consume_grant_attempt()` runs it in its own transaction, and R-09 calls it after
the per-address check and before the redemption unit; on refusal the route records
the authentication failure exactly as it does for every other emergency refusal
and redirects with the coarse `rate_limited` code.

Three consequences, stated so a reviewer can check them:

* **No `Retry-After` accompanies this refusal.** N-33's per-grant budget is *for
  all time*, not a window; a retry hint would promise a recovery that does not
  exist. The per-address half keeps its hint, because that one is a window.
* **A successful redemption spends an attempt too.** The counter counts attempts,
  the grant is single-use, and five remains the accepted cap. Proved rather than
  assumed by TC-BG-17's last case.
* **`redeem_recovery_grant()` keeps a read-only check of the same counter.** It no
  longer writes, but it still refuses above the cap, so a caller that reaches the
  service without spending an attempt cannot redeem past it. That read is
  `attempts_for()`'s only production consumer and is why it was kept.

`RecoveryGrantRepository.note_attempt()` is now one statement — `UPDATE … RETURNING
attempt_count` — instead of an update followed by a separate read. Two concurrent
attempts could previously read the same number back; the increment and the reading
of it are now the same operation, which is the property N-30's `INSERT … ON
CONFLICT … RETURNING` has always had. A token matching no grant still updates no
row, creates no row, and returns zero.

---

## 4. Evidence

Two new traceability rows, added to `docs/contracts/phase-3-test-traceability.md`
**by addition only**. TC-BG-11 is unchanged: its scope was always the per-address
halves, and it remains accurate for them.

| Row | What it proves | Level |
|---|---|---|
| TC-BG-16 | Ten refused assertions for one enrolled credential from **ten different source addresses** are all `403 invalid`; the eleventh is `429 rate_limited` with `Retry-After`; `auth_rate_limits` holds exactly **one** account bucket carrying all eleven; no session exists. The same sequence against an invented credential id returns the same statuses and coarse error codes at the same attempts, from a bucket that contains no credential id. Correlation identifiers are intentionally per-request and literal retry-hint equality is not claimed | direct HTTP, real PostgreSQL |
| TC-BG-17 | Five attempts against a **matched but invalidated** grant, from five different source addresses, each advance the stored `attempt_count` durably *after* the refusal rolled its transaction back (1, 2, 3, 4, 5, asserted between requests); the sixth is refused `rate_limited`, `attempt_count` is 6, no session exists, and `auth.emergency.refused` with `grant_attempt_cap` is committed. A separate case proves a successful redemption spends attempt one and still consumes the grant | direct HTTP, real PostgreSQL |

Every source address is supplied by `X-Forwarded-For` over the loopback transport
peer, which is exactly N-34's one trusted hop, so the addresses the limiter sees
are the addresses the tests intend.

### 4.1 The overstated test, corrected rather than deleted

`test_the_per_grant_attempt_cap_refuses_the_sixth_attempt` is renamed
`test_a_token_matching_no_grant_counts_against_no_grant_record`, and its docstring
now says what it does: a token matching no grant spends nobody's per-grant budget,
so an attacker holding no token cannot exhaust a real grant's cap. Its body now
drives **both** boundaries the route uses — the committed attempt counter and the
redemption that rolls back — because after this change the redemption alone no
longer touches the counter at all, and a test that reached only it would have
proved nothing about either.

### 4.2 A consumer case for the new budget path

`tests/web/test_settings_construction_validation.py` gains one TC-LIM-06 case: an
unresolved credential spends the same *configured* limit and window as an account
does. The existing account-budget case is unchanged and now names TC-BG-16 as its
route-consumer evidence — which is the thing the security review correctly said it
did not have.

---

## 5. Falsification

Four mutations, each applied alone to the restored file, each reverted and the
file verified byte-for-byte with `sha256sum -c` afterwards. Suite:
`tests/web/test_break_glass_login.py` (17 cases).

| # | Mutation | Result |
|---|---|---|
| M1 | `_consume_assertion_account_budget()` returns `None` immediately — the reported defect, exactly | **2 failed**: `..._one_credential_shares_one_assertion_budget_across_addresses`, `..._an_unknown_credential_is_refused_exactly_as_an_enrolled_one_is` |
| M2 | `_consume_grant_attempt()` returns `None` immediately | **2 failed**: `..._the_sixth_attempt_against_one_grant_is_refused_across_addresses`, `..._a_successful_redemption_spends_one_of_the_grant_attempts` |
| M3 | The attempt is spent, but the refusal is **raised inside** its transaction — the reported defect's mechanism, reintroduced at the new boundary | **1 failed**: `..._the_sixth_attempt_against_one_grant_is_refused_across_addresses` |
| M4 | An unresolved credential spends no budget — the oracle the design exists to avoid | **1 failed**: `..._an_unknown_credential_is_refused_exactly_as_an_enrolled_one_is` |

M3 is the important one: it proves the new tests fail against the *original*
defect and not merely against a missing call.

---

## 6. Verification

All commands were run from `/opt/discord-bots/freedom-bot` against the guarded
disposable PostgreSQL database `freedom_test` over its local Unix-domain socket.
The two suites share that database, so they were run **serially**; running them
concurrently produces dozens of false failures.

| Command | Result |
|---|---|
| `TEST_DATABASE_URL=postgresql+psycopg:///freedom_test ./venv-web/bin/python -m pytest -q -rs tests/web` | **712 passed**, 20 deprecation warnings, **0 skipped** |
| `TEST_DATABASE_URL=postgresql+psycopg:///freedom_test ./venv-web/bin/python -m pytest -q -rs tests/web/test_break_glass_login.py` | **17 passed**, 0 skipped |
| `TEST_DATABASE_URL=postgresql+psycopg:///freedom_test ./venv/bin/python -m pytest -q -rs` | **2260 passed**, 1 warning, **0 skipped** |
| `git diff --check` | clean |
| `sha256sum -c` after each of the four mutations | both files OK, byte-for-byte |

The web suite is 707 + 5, and the five are the cases described in §4. The 20 and 1
warnings are the pre-existing dependency deprecations (`httpx` per-request cookies;
`audioop` through Discord).

### 6.1 Not run, and not claimed

* **`alembic check`** — no schema, migration, table or model was touched. The
  `recovery_grants.attempt_count` column is unchanged; only the statement that
  writes it changed.
* **Formatter, linter, type checker** — none is configured in this repository.
* **Staging-class checks** — no staging environment exists.
* **Concurrency evidence for the new counters** — see §8.1.

---

## 7. Diff audit

Production:

* `application/web/rate_limit.py` — `check_credential()` added. `check_ip()`,
  `check_account()`, `_budget_for()`, `_check()`, `_digest()` and `sweep()` are
  unchanged.
* `application/web/breakglass.py` — `AssertionSubject`, `assertion_subject()`,
  `note_recovery_attempt()`, the shared `_credential_id_from()` reader, and
  `redeem_recovery_grant()`'s increment becoming a read. No lifetime, capability,
  scope, audit action or refusal code changed; every refusal a caller can see is
  the code it was before.
* `adapters/web/app.py` — two helpers beside `_consume_rate_limit()` and one call
  to each from R-08 and R-09. No route added, removed or renamed; no cookie,
  header, digest, origin check or middleware touched. `ROUTE_INVENTORY` is
  unchanged.
* `adapters/web/repositories.py` — `note_attempt()` returns the count it wrote in
  one statement; a docstring on `attempts_for()`. No other repository touched.

Tests: `tests/web/test_break_glass_login.py` (four new cases, one renamed and
re-scoped), `tests/web/test_settings_construction_validation.py` (one new
TC-LIM-06 case, one docstring).

Documentation: `docs/contracts/phase-3-test-traceability.md` (amended by
addition), `docs/project-management/change-log.md` (C-P3.1-X),
`docs/project-management/status.md` (tenth update, appended),
`docs/project-management/raid-register.md` (I-09 amended), and this file.

No secret, credential, real player datum, production identifier or `.env` value
appears in any changed file. No production data was read or written.

---

## 8. Honest remaining gaps, and where a reviewer should push

1. **The account budget is spent by a lookup the assertion then repeats.** R-08
   now resolves the credential twice: once to charge the budget, once inside the
   verification transaction. That is deliberate — the first read must commit and
   the second must be inside the unit of work — but it is two reads of one row,
   and a reviewer may reasonably ask whether the resolved account should be
   carried into the second transaction instead. It is not, because passing a
   resolved identity across a transaction boundary is how a stale read becomes an
   authorization decision, and the second read is the one that authorizes.
2. **`redeem_recovery_grant()` now depends on a caller having spent an attempt.**
   The read-only check keeps it fail-closed, but the *counting* is the route's
   job. Direct service callers — every other test in the module — no longer
   advance the counter, and that is visible rather than hidden: `note_attempt()`
   has exactly one production caller and it is named for what it does.
3. **No concurrency case for either new counter.** `UPDATE … RETURNING` makes the
   per-grant increment atomic and `INSERT … ON CONFLICT … RETURNING` already made
   the rate-limit bucket atomic, so the 2× fixed-window burst of RR-03 remains the
   known and accepted cost — now on the per-account budget as well as the
   per-address ones. Two simultaneous attempts at a window boundary can therefore
   total twenty in a second against one account. That is RR-03's existing shape,
   not a new risk, and it is not separately tested here.
4. **The per-credential bucket is a new row shape in `auth_rate_limits`.** It is
   bounded and swept (§2.2), but it is genuinely new storage, and a reviewer who
   disagrees that the oracle is worth it should say so — the alternative is to
   spend nothing for unknown credentials and accept the distinguishable eleventh
   attempt.
5. **Nothing here re-examines TC-BG-11.** Its per-address halves were correct and
   remain untouched.

**Requested of the security review:** confirm that consuming the account budget
after credential resolution and before verification is the right boundary; that
the per-credential fallback removes the oracle rather than moving it; that
returning a refusal instead of raising it is the right way to keep an increment
committed; that no refusal code, audit payload or response shape now discloses
more than it did; and that the per-grant read-only check left in the service is a
safeguard rather than a second authority.

---

## 9. Status

**Submitted, not accepted.** P3.G1, RAID I-09 and RAID I-10 remain open. P3.2 and
P3.3 have not been started. No deployment, OAuth registration, production database
change, Foundry mutation or Google Sheet mutation is authorized by this document.
