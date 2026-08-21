# P3.4 Step 9 — remediation handoff for the 2026-08-21 independent Codex review

**Date:** 2026-08-21
**Author:** Claude (P3.4 Step 9 implementer)
**Status:** REMEDIATION COMPLETE FOR FINDINGS 1 AND 2 · **FINDING 3 IS A STOP
CONDITION** · P3.G4 remains open and is **not** marked accepted.

This record is new. No historical review or acceptance record was edited.

---

## 1. Findings and dispositions

| # | Finding | Disposition |
|---|---|---|
| 1 | `application/web/account_identities.py` owned `run_identity_unlink`, imported `adapters.web.repositories.WebAuditRepository` inside it, and drove `engine.begin()` — reversing the required dependency direction | **Fixed.** Runner moved to the adapter boundary; a structural regression guard now fails if it comes back |
| 2 | R-42 stripped the submitted `nonce` and only checked it was non-empty, so a direct caller could submit arbitrary or oversized text to the idempotency-key path | **Fixed.** One shared rule, enforced at the request boundary, with 28 new direct-HTTP and unit cases |
| 3 | Seven digest-preservation failures: the changed `audit_results.html`, `audit_search.html` and `import_result.html` bytes contradict the accepted immutable corpus | **NOT fixed — stop condition.** The current bytes have no dated acceptance and belong to another implementer's in-flight Step 10 work. Neither blessing them nor restoring the accepted bytes is authorized |

---

## 2. Finding 1 — dependency direction and the R-37 transaction boundary

### What changed

`run_identity_unlink(engine, change)` moved from `application/web/account_identities.py`
to module scope in `adapters/web/portal_routes.py`. Nothing about its behaviour
changed; only its side of the boundary did.

The split of responsibility is now:

* **`application/web/account_identities.py`** states the *rule*.
  `AccountIdentityService.unlink` decides that the last-usable-identity refusal
  is the one that must be durable, constructs the `identity.link_refused`
  `AuditEvent`, and raises `UnlinkRefusedPendingAudit` carrying it. The module
  imports no `adapters.*`, no SQLAlchemy, no engine and no concrete repository —
  at any nesting depth, including function-local and `TYPE_CHECKING`.
* **`adapters/web/portal_routes.py`** provides the *machinery*. It owns the
  engine, the two transactions and the `WebAuditRepository` write.

### Final dependency direction and transaction boundary for R-37

```text
adapters/web/portal_routes.py
    run_identity_unlink(engine, change)
        txn 1: change(connection) -> AccountIdentityService.unlink(...)
                 success  -> retire identity + identity.unlinked, committed together
                 refusal  -> rolled back; nothing retired
        txn 2 (only on UnlinkRefusedPendingAudit):
                 WebAuditRepository(connection).record(event)
                 -> then re-raise the plain UnlinkRefused, which the route renders as 409
```

Accepted R-37 behaviour preserved exactly and re-proved by
`tests/web/test_account_identity_refusal_audit.py` (30 cases, all against real
disposable PostgreSQL, reading `audit_events` on a **separate** connection after
the work committed):

* successful unlink retires the identity and records `identity.unlinked` in the
  same transaction;
* the last-usable-identity refusal changes no identity state;
* it records exactly one durable `identity.link_refused` event, in a separate
  transaction;
* a failing refusal-audit transaction propagates, so the route never answers
  `409` claiming a durable record that does not exist
  (`test_a_failed_refusal_audit_renders_a_safe_error_not_a_conflict`);
* correlation, actor, subject, capability, reason and safe facts are unchanged
  (`test_the_durable_refusal_carries_exactly_the_accepted_attribution`);
* retries and the other refusal branches create no duplicate or spurious audit
  effect — the other branches raise plain `UnlinkRefused` and write nothing;
* status, safe body, CSRF and authorization behaviour are unchanged.

None of the prohibited escapes were used: no suppressed import check, no
`TYPE_CHECKING` import, no service locator, no weakened refusal audit.

### The structural regression assertion

Added to `tests/web/test_structural_guards.py`, next to the existing TC-STRUCT-05
module-graph guard and built the same way — `ast.walk` over the whole tree, so a
function-local import (the exact shape of the defect) is counted like any other:

1. `test_the_r37_unlink_use_case_never_imports_an_adapter_or_an_engine` — hard
   assertion that `application/web/account_identities.py` imports neither
   `adapters` nor `sqlalchemy`. This is the regression guard the review asked for.
2. `test_no_new_application_web_module_starts_importing_an_adapter` — a **ratchet**
   over the rest of the layer. It fails if the set of offending modules changes in
   either direction.

### Pre-existing violations found while building the guard (not remediated)

Six `application/web/` modules already invert the dependency direction, all from
packages accepted before P3.4 and all outside this remediation's allowlist:

| Module | Reaches outward to |
|---|---|
| `application/web/config.py` | `adapters.database.config`, `adapters.database.safety` |
| `application/web/errors.py` | `adapters.web.repositories`, `engine.begin()` |
| `application/web/rate_limit.py` | `adapters.web.repositories` |
| `application/web/refusals.py` | `adapters.web.repositories`, `engine.begin()` |
| `application/web/role_mappings.py` | `adapters.web.repositories`, `engine.begin()` |
| `application/web/startup.py` | `adapters.artifacts.filesystem`, `adapters.database.tables`, `sqlalchemy` |

`application/web/role_mappings.run_mapping_change` is the same two-transaction
pattern the review flagged, on the same wrong side of the boundary — the Step 9
runner was written to match it. It is named here rather than fixed: it is
committed, accepted, serves five call sites, and changing it is outside the
allowlist. **Recommended for a separately authorized remediation.**

---

## 3. Finding 2 — the R-42 preview-nonce boundary

### The one shared rule

`application/web/jobs.parse_preview_nonce(submitted: object) -> str | None`,
beside `mint_preview_nonce` and `request_key`. The width and alphabet are stated
once, from `PREVIEW_NONCE_BOUND`:

```python
_PREVIEW_NONCE_GRAMMAR = re.compile(f"[A-Za-z0-9_-]{{{PREVIEW_NONCE_BOUND}}}")
```

No literal `43` appears in the route, the service or the tests. Accepts only:

* type — `str` (anything else, including a multipart upload object, is refused
  rather than coerced);
* length — exactly `PREVIEW_NONCE_BOUND == 43` characters, tested **first** so an
  oversized body is refused by a comparison rather than by a quantified pattern;
* grammar — ASCII `[A-Za-z0-9_-]{43}`, which is exactly the unpadded base64url
  alphabet `secrets.token_urlsafe` emits.

**No normalization at all** — no strip, no case fold, no Unicode normalization,
no percent-decoding. The previous `.strip()` was removed: trimming turns an
invalid submitted value into a valid one, which is the thing VM-14 forbids.

### The request boundary

`adapters/web/import_routes._submitted_preview_nonce(form)` adds the one thing
only the boundary can see — **how many `nonce` fields arrived**:

```python
submitted = form.getlist("nonce")
if len(submitted) != 1:
    return None
return parse_preview_nonce(submitted[0])
```

A body repeating the key has no single request identity, so it is refused rather
than resolved by whichever value the parser happened to keep.

Refusal is the accepted `422` `ValidationView` response, emitted **before**
`enqueue_preview` is called: no job, no repository call, no queued audit effect.
The refusal is also **after** the guard, so authorization and CSRF denial
precedence is unchanged.

### Idempotency semantics — unchanged

* two submissions of one rendered form → one durable job, one
  `reconciliation.job_queued` event
  (`test_rendered_r42_nonce_is_server_minted_per_render`, steps 5–6);
* a separately rendered R-40 page carries a fresh nonce and creates a second
  deliberate preview (same test, steps 7–8);
* the raw nonce is not persisted, logged, echoed or exposed — `request_key`
  hashes it, and the test asserts neither raw value appears in either
  `request_key`;
* nonce possession grants nothing: Council authorization, snapshot, folder,
  profile and server-owned scope are all still re-resolved by
  `enqueue_preview`, unchanged.

### Direct R-42 malformed / oversized outcomes

`tests/web/test_p3_4_snapshot_views.py`, four new tests (28 cases), every one a
direct `POST` that **never fetches R-40 first**. Every case asserts `422` **and**
then reads `reconciliation_jobs` and `audit_events` on a fresh connection to
prove no job and no success audit effect.

| Case | Submitted | Outcome |
|---|---|---|
| accepted | a real `mint_preview_nonce()` (43 chars) | `303`, one job |
| `absent` | no `nonce` field at all | `422`, no effect |
| `empty` | `nonce=` | `422`, no effect |
| `one_short` | 42 chars | `422`, no effect |
| `one_long` | 44 chars | `422`, no effect |
| `far_too_long` | 172 chars | `422`, no effect |
| `padding` / `solidus` / `plus` / `dot` / `colon` | 43 chars ending `=` `/` `+` `.` `:` | `422`, no effect |
| `inner_space` | 43 chars ending in a space | `422`, no effect |
| `leading_space_padded` / `trailing_space_padded` / `surrounding_whitespace_padded` | 43 valid chars **plus** surrounding whitespace — would become valid if trimmed | `422`, no effect |
| `newline` / `carriage_return` / `null_byte` | control characters at accepted width | `422`, no effect |
| `unicode` / `homoglyph` (Cyrillic А) / `emoji` | non-ASCII at accepted character width | `422`, no effect |
| `hand_shaped` | `nonce_12345` | `422`, no effect |
| oversized-in-bound | 4000-byte body, inside R-42's accepted 4 KiB bound, so the size middleware does **not** answer first | `422`, no effect |
| duplicate keys | `nonce=<minted>&nonce=<hostile>` and both other orderings | `422`, no effect |
| denial precedence | every non-`303` caller-matrix cell × {minted nonce, malformed nonce} | guard's status, never `422` |
| CSRF precedence | wrong `csrf_token` × {minted nonce, malformed nonce} | `403 csrf_invalid` |

### Existing tests corrected because they submitted values R-42 never minted

These were passing only because the validation was missing:

* `tests/web/test_p3_4_snapshot_views.py` — `test_nonce` was
  `f"{snap_id}:nonce_12345"`; now `mint_preview_nonce()`.
* `tests/web/test_p3_3_jobs.py` — `nonce=tc-job-01`, `nonce=double-click`,
  `nonce=n{index}`, `nonce=one-too-many`.
* `tests/web/test_p3_3_success_cells.py` — `nonce=success-{state}`.

A shared helper `tests/web/p3_3_fixtures.preview_nonce(label)` folds a readable
label into the accepted alphabet and width, so a double-click stays one identity
and two labels stay two deliberate previews.

`tests/web/test_p3_3_disclosure_and_bounds.py` still submits `nonce=x`; those
cases assert `413`, `411`, `415` and `503`, all of which precede the nonce rule.
They are unaffected and were left alone.

### Out of scope, flagged

**R-46's `nonce` is not validated either.** `adapters/web/import_routes.py`
applies the same `(form.get("nonce") or "").strip()` / non-empty test at the
apply boundary, where the rendered value is the preview job's UUID
(`job_status_fragment.html`). The same class of defect, a different accepted
grammar, and outside this remediation's allowlist and findings. **Recommended
for the independent re-review's attention.**

---

## 4. Finding 3 — STOP CONDITION, gate stays red

### The controlled status of the three changed templates

| Template | Accepted bytes (`HEAD`, baseline §4, all 7 digest owners) | Working-tree bytes |
|---|---|---|
| `audit_results.html` | `11ee0efcba8892970dee0870b5612d0fbf9c5091d5cf954ddf77e4af4f98291e` | `d74dc0a0f4409dd0f6954002c810f9c1be4b01264f1962448e13ffb9f7877642` |
| `audit_search.html` | `c54db1a4cc1779a52921269641330f79d295a843086eb198916a2f07c6e61c15` | `6453c99cd068918be029d7f592b8a934654b11f05e324400ef080d83e878ec23` |
| `import_result.html` | `152b84f766211b886ddd67ca1ce03c53cb37ceefc9ea5678cd22f7f2b7f3fff6` | `15735d60fdb5a5b3c8435a7ee389af7e6ec027c2f386cdee55f3d109bd42c86e` |

**Before and after this remediation these three files are byte-identical.** None
was read into, written, restored or blessed.

### Why this is case 3 of the finding's decision procedure

1. **The working-tree bytes have no dated acceptance.** Each of the three current
   digests appears in **zero** files anywhere in the repository — no acceptance
   record, no review record, no manifest, no test.
2. **The accepted bytes are the `HEAD` bytes**, recorded in
   `docs/review/phase-3-p3-4-gemini-baseline.md` §4 and enforced identically by
   all seven digest owners.
3. **These are exactly the Step 10 allowlist.** Execution plan §Step 10 names
   `import_result.html`, `audit_search.html` and `audit_results.html`; baseline
   rows 22–24 and the transition table assign all three to **Step 10**.
4. **Step 10 has not been released, let alone accepted.** The baseline's status
   line reads `STEPS 1–6 ACCEPTED · STEP 7 RELEASED · STEP 8 NOT RELEASED`;
   §"Step 8 and every later step remain unreleased". There is no
   `phase-3-p3-4-gemini-step-08/09/10-*-prompt.md`, no Step 10
   `*-review-and-acceptance.md`, and the Step 10 test module the baseline plans
   (`tests/web/test_p3_4_import_and_audit_views.py`) does not exist.

So the tree holds another implementer's **in-flight, unreviewed, uncommitted**
Step 10 frontend work.

### Why neither available action was taken

* **Updating the seven digest dictionaries would self-approve those bytes.** They
  have passed no Step 10 semantic, security, accessibility or route/view-model
  review; there is no dated evidence recording their SHA-256; and the finding
  forbids blessing unreviewed bytes.
* **Restoring the accepted bytes would destroy user work.** The Step 10 changes
  are uncommitted (`git status` shows ` M`), so `git checkout` on them is
  irreversible. The remediation prompt requires preserving all current changes
  and permits restoration only if Peter's existing authorization explicitly
  allows it without destroying user work. It does not.

Consolidating the seven copied digest dictionaries into one canonical source is
listed in the prompt's *conditional* allowlist, available only with existing
explicit acceptance authority. There is none, so it was not done. It remains the
right cleanup once the corpus transition is decided.

### The precise unresolved acceptance dependency

> The seven digest-preservation failures cannot close until Step 10 for
> `import_result.html`, `audit_search.html` and `audit_results.html` is released,
> implemented, independently reviewed and accepted with the exact SHA-256 of the
> accepted bytes recorded in dated evidence — after which the canonical digest
> source is updated **once** and the seven suites are made to consume it.

**This gate is red and must stay red until then.** It is not a Step 9 defect.

---

## 5. Files changed, and why

| File | Why |
|---|---|
| `application/web/account_identities.py` | removed `run_identity_unlink` and its `adapters` import; docstrings now point at the adapter that owns the transaction (F1) |
| `adapters/web/portal_routes.py` | received `run_identity_unlink` at module scope with the `WebAuditRepository` import; the R-37 handler is otherwise unchanged (F1) |
| `application/web/jobs.py` | added `_PREVIEW_NONCE_GRAMMAR` and `parse_preview_nonce`; exported it and `mint_preview_nonce` (F2) |
| `adapters/web/import_routes.py` | added `_submitted_preview_nonce`; R-42 now admits only the exact contract (F2) |
| `tests/web/test_structural_guards.py` | the two dependency-direction guards (F1) |
| `tests/web/test_account_identity_refusal_audit.py` | import follows the runner to the adapter; assertions unchanged (F1) |
| `tests/web/test_p3_4_snapshot_views.py` | 28 new direct-HTTP/unit nonce cases; the hand-built fixture nonce replaced with a minted one (F2) |
| `tests/web/p3_3_fixtures.py` | shared `preview_nonce(label)` helper (F2) |
| `tests/web/test_p3_3_jobs.py` | five submitted nonces now of the accepted shape (F2) |
| `tests/web/test_p3_3_success_cells.py` | one submitted nonce now of the accepted shape (F2) |

**No** schema, migration, capability meaning, route path/method, session/CSRF
design, audit disclosure policy, worker state machine, Foundry parsing, shared
shell/asset, template, Phase 3 contract or P3.5+ scope was changed. No file was
added or deleted. `git status` gained exactly four entries relative to the
pre-remediation baseline, all of them tests.

### Declared scope note

`tests/web/p3_3_fixtures.py`, `tests/web/test_p3_3_jobs.py` and
`tests/web/test_p3_3_success_cells.py` are **not literally in the remediation
allowlist**, though the prompt names "existing R-42 P3.3 route and idempotency
tests" among Finding 2's primary files to inspect. They were edited because
enforcing the accepted VM-14 contract necessarily turns their hand-built nonces
into refusals; the edits change only the submitted nonce values and add one
shared helper. **Flagged for Peter's explicit ratification.**

---

## 6. Verification

Environment: `/opt/discord-bots/venv-web/bin/python` 3.12.3, pytest 8.4.2,
`TEST_DATABASE_URL='postgresql+psycopg:///freedom_test'` (present and used — the
disposable local database, no live or production service). No dependency was
installed.

### Focused remediation evidence

```
TEST_DATABASE_URL='postgresql+psycopg:///freedom_test' \
  /opt/discord-bots/venv-web/bin/python -m pytest -q -rs \
  tests/web/test_account_identity_refusal_audit.py \
  tests/web/test_p3_4_snapshot_views.py \
  tests/web/test_p3_4_job_status_views.py
```

**2 failed, 149 passed, 0 skipped.** Both failures are
`test_template_digests_match_accepted_corpus` (Finding 3).

### Combined accepted P3.4 surface

```
TEST_DATABASE_URL='postgresql+psycopg:///freedom_test' \
  /opt/discord-bots/venv-web/bin/python -m pytest -q -rs \
  tests/web/test_p3_4_static_assets.py tests/web/test_static_asset_surface.py \
  tests/web/test_p3_4_shell_and_components.py tests/web/test_p3_4_auth_and_system_views.py \
  tests/web/test_p3_4_member_views.py tests/web/test_p3_4_council_character_views.py \
  tests/web/test_p3_4_identity_and_role_views.py tests/web/test_p3_4_snapshot_views.py \
  tests/web/test_p3_4_job_status_views.py tests/web/test_account_identity_refusal_audit.py
```

| | passed | failed | skipped |
|---|---|---|---|
| before this remediation | 484 | 7 | 0 |
| after | **509** | **7** | **0** |

The same seven digest-preservation tests, failing for the same reason, on the
same three templates. +25 net tests, all passing; no new failure introduced.

Step 10 is not within the accepted or current review scope, so no Step 10 module
was added to the run — there is none to add.

### Other suites

* `tests/web/test_structural_guards.py` — **70 passed**.
* Full `tests/web` — 25 failed, 1963 passed, 80 skipped. The 25 are the 7 digest
  failures plus 18 that are unrelated to R-37 and R-42 and predate this work:
  8 × `test_p3_3_disclosure_and_bounds` hostile-name cases and
  `test_security_controls::test_no_view_model_field_reaches_a_script_context`
  (all failing on `<script defer src="/static/vendor/htmx-…">` newly present in
  `base.html`, a frontend-track change), 5 × `test_identity_migration_command`,
  3 × `test_oauth_refusal_audit`, and
  `test_p3_3_audit_search::test_the_cursor_pages_forward_without_repeating_or_dropping_a_row`.
  None of those modules exercises R-42 or the R-37 unlink path; the three that
  did (`test_p3_3_jobs`, `test_p3_3_success_cells`, `test_p3_3_matrix`) are green.
* Bot suite, `/opt/discord-bots/venv/bin/python -m pytest -q tests` — **2034
  passed, 260 skipped, 0 failed.**

### PostgreSQL evidence actually exercised

`TEST_DATABASE_URL` was configured throughout; **nothing was skipped for want of
a database** in either prescribed run. Real-PostgreSQL evidence covers:

* R-37's two-transaction behaviour — the durable refusal read back on a
  **separate** connection after the rolled-back mutation, the unretired identity,
  the absent `identity.unlinked`, the failure-injection cases in both directions,
  and a concurrent two-thread case;
* R-42's no-effect refusals — every one of the 28 nonce cases re-reads
  `reconciliation_jobs` and `audit_events` after the response.

No partial mutation, false success, missing audit, duplicate effect or
runtime-role bypass was observed.

### Formatter, linter, type checker, compileall, whitespace

| Check | Result |
|---|---|
| formatter | **not run — none configured or installed.** No `pyproject.toml`, `setup.cfg`, `.pre-commit-config.yaml`; `black`/`isort` absent from `requirements*-dev.txt` and from `venv-web` |
| linter | **not run — none configured or installed** (`ruff`, `flake8` absent) |
| type checker | **not run — none configured or installed** (`mypy`, `pyright` absent) |
| `compileall` | **passed**, exit `0`, over the ten changed modules and over `application/` and `adapters/` |
| `git diff --check` | **passed**, exit `0`, clean |
| dependency-direction check | the repository's mechanism is `tests/web/test_structural_guards.py`; **70 passed**, including the two guards added here |

None of the three uninstalled tools is claimed to have passed.

### Falsification

Each mutation was applied alone, run, reverted, and the restored SHA-256 verified
against the value recorded before mutation.

**1 — an `application` import of the concrete web repository.** Added a
function-local `from adapters.web.repositories import WebAuditRepository` to
`application/web/account_identities.py`.
`application/web/account_identities.py` `8ea4b17a…` → `e716f021…`.
Both guards failed:
`test_the_r37_unlink_use_case_never_imports_an_adapter_or_an_engine` and
`test_no_new_application_web_module_starts_importing_an_adapter`.
Restored to **`8ea4b17a060f8345403b44da50faefce435c0b418d97b37b2997377fe90dd5af`**; both pass.

**2 — acceptance of a 44-character or non-URL-safe nonce.** Widened
`_PREVIEW_NONCE_GRAMMAR` to `.+` and the width test to `43..44`.
`application/web/jobs.py` `6a934e34…` → `ee8990f2…`.
**15 tests failed**, including `one_long` (44 chars), `padding`, `solidus`,
`plus`, `dot`, `colon`, `inner_space`, `leading_space_padded`,
`trailing_space_padded`, `null_byte`, `carriage_return`, `unicode`, `homoglyph`,
`emoji` and `test_r42_accepts_exactly_the_shape_r40_mints`.
Restored to **`6a934e3418c69ca36c8d1a7de8fc75b5915dcee4ff6ddbe6364c32277acbd7ba`**; 25 pass.

**3 — a changed accepted template byte with no controlled corpus transition.**
Appended a comment to `adapters/web/templates/login.html` — an accepted template
whose digest currently matches.
`login.html` `eafd7635…` → `72aa1fa6…`. Detected: measured against the digest
owners' own `ACCEPTED_TEMPLATE_DIGESTS`, `login.html` mismatched. (The suite-level
assertion reports only the first mismatch in sorted order, which is
`audit_results.html`, so the check was isolated to `login.html` to make the
detection unambiguous.)
Restored to **`eafd7635be0b6b8dfb7d60df7a827a49863b5b12bb1cdc0e49ddbd4c0f7d5e3b`**.

All five files whose hashes were recorded before falsification are bit-for-bit
identical afterwards. **No falsification mutation remains in the tree.**

---

## 7. Safety confirmation

No commit, no push, no deployment, no live service, no Discord, no Google
Sheets, no Foundry, no production PostgreSQL. `.env`, credentials, secrets, real
snapshots and player data were never read. All fixtures are the synthetic Phase 2
bundles. The only database touched is the disposable local `freedom_test`.
Unrelated user changes in the shared tree — including the entire in-flight
Step 10 frontend work — are preserved untouched.

---

## 8. Remaining blockers and recommended independent-review focus

**Blockers**

1. **Finding 3 / P3.G4.** Seven digest-preservation failures stand until Step 10
   is released, implemented, reviewed and accepted with recorded SHA-256 values.
   Peter's decision is required on how the corpus transition is controlled.
2. **Eighteen further `tests/web` failures predate this work** and belong to other
   owners — most visibly the `<script defer src="/static/vendor/htmx-…">` tag now
   in `base.html`, which breaks the accepted P3.2/P3.3 "no script context"
   controls. Whether that is an accepted Step 3 shell change or a defect is a
   frontend-track question, not a Step 9 one.

**Recommended review focus**

1. **R-46's `nonce`** — the same missing-validation shape as Finding 2, at the
   apply boundary, where the accepted value is a job UUID.
2. **`application/web/role_mappings.run_mapping_change`** and the five other
   pre-existing `application → adapters` imports (§2). The new ratchet guard
   stops the set growing; it does not shrink it.
3. **`tests/web/test_p3_4_static_assets.py::test_no_unrelated_production_files_modified`
   does not check what it claims.** It `.strip()`s each `git status --short` line
   before slicing `line[3:]`, which shifts every ` M` entry by one character, so
   the path never starts with `adapters/` or `application/` and **every modified
   file passes silently**. Only untracked (`??`) entries are actually checked. The
   currently-modified `portal_routes.py`, `import_routes.py` and the three Step 10
   templates all go undetected. Not in this remediation's allowlist; reported here.
4. **The seven copied `ACCEPTED_TEMPLATE_DIGESTS` dictionaries** should become one
   canonical source as part of resolving Finding 3.

**The P3.G4 review gate is not marked accepted.** Stopping here for independent
re-review and Peter's decision.
