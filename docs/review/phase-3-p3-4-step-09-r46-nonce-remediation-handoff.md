# P3.4 Step 9 — R-46 apply-nonce boundary remediation

**Date:** 2026-08-21
**Author:** Claude (P3.4 Step 9 implementer)
**Scope:** the single remaining independent-review finding at **R-46 only**.
**Status:** **REMEDIATED.** P3.G4 is **not** marked accepted; the Step 10
template-digest stop condition is unchanged and still red.

This record is new. No historical review or acceptance record was edited. It is
the successor to `phase-3-p3-4-step-09-remediation-handoff.md`, whose §8
*Recommended review focus* item 1 is what this closes.

---

## 1. Finding and disposition

| Finding | Disposition |
|---|---|
| R-46 read its `nonce` as `(form.get("nonce") or "").strip()` and required only non-emptiness, so a direct caller could mint arbitrary, malformed, duplicated, padded, oversized or alternate request identities for one completed preview — even though `job_status_fragment.html` renders exactly one canonical value and the accepted semantic is that every confirmation of one preview converges on one apply | **Fixed.** R-46 now admits exactly one `nonce` field whose text is exactly `str(job_id)` for the preview named by the route path |

**No contract conflict was found.** The route-authorization contract §6.1 R-46
names `csrf_token`, `preview_token` and `nonce` and states that *"double-click,
retry and two-browser concurrency all resolve to one durable effect and one
success audit event"*; the view-model contract's VM-14 `preview_nonce` block
says in as many words that **"R-46's nonce is a separate contract"** and that the
apply form in `job_status_fragment.html` is Step 9's. Neither document permits a
caller-selected R-46 request identity, so the stop condition "an accepted
contract explicitly permits a caller-selected R-46 nonce" did not fire and no new
protocol was invented. The template was not touched.

---

## 2. The final R-46 nonce grammar, multiplicity rule and precedence

### Grammar

Exactly `str(identifier)`, where `identifier` is the `UUID` already parsed from
the R-46 path — the canonical lowercase hyphenated spelling, which is the one
`UUID.__str__` produces and the one the template renders.

**Nothing is normalized or repaired**: no `.strip()`, no case fold, no Unicode
normalization, and deliberately **no `UUID()` re-parse**. Comparing against the
canonical text rather than against a parsed value is what refuses the spellings
Python would otherwise accept as "the same UUID":

| Refused | Because |
|---|---|
| `A1B2…` (uppercase) | not the text the form emits |
| `a1b2c3d4…` (hyphens removed) | not the text the form emits |
| `{a1b2…}`, `urn:uuid:a1b2…` | not the text the form emits |
| ` a1b2… `, `\ta1b2…\n` | a trim would manufacture the match |
| `a1b2…;`, `"a1b2…"`, `a1b2…&x=1` | padding and punctuation |
| `a1b2…\n`, `a1b2…\r`, `a1b2…\x00` | control characters |
| `a1b2‐…` (U+2010), `a1b2…​…`, `a1b2…😀` | Unicode lookalikes and non-ASCII |
| another well-formed UUID, including a **real second preview's** | identity must be *this* job |
| `"a"*7000` inside the 8 KiB body bound | length is not a ceiling to fill |
| a non-`str` value (multipart part, bytes, `UUID` object, `None`) | refused, never coerced |

### Multiplicity

`form.getlist("nonce")` must have length exactly `1`. **Two agreeing values are
refused as well as two conflicting ones**: the rendered form emits one field, so
a body with two did not come from it, and a request with two request identities
has none. `.get()` would have resolved such a body by whichever value the parser
happened to keep.

### Precedence — unchanged in every direction

```text
session  →  origin  →  content type  →  body bound  →  CSRF        (the preamble)
         →  path UUID parse                  → 404 object_not_reachable
         →  preview_token non-empty          → 422 preview_token
         →  ★ the nonce rule ★               → 422 nonce
         →  enqueue_apply(...)               → Council authority, preview state,
                                               N-46 expiry, constant-time token,
                                               checksum/folder/profile/aggregate,
                                               one-live-apply fence, audit
```

The rule sits **after** the guard and **after** path parsing and **before**
`enqueue_apply`. So an unauthorized caller with a perfect nonce is still refused
first, a malformed path is still the non-enumerating `404` rather than a `422`,
and a refused nonce reaches no repository at all.

**The nonce rule is not an existence oracle.** A hostile nonce produces a
byte-identical `422` whether the well-formed UUID in the path names a real
preview or nothing, and the canonical nonce for an absent job reaches the
ordinary `404`. There is no pair of requests whose difference reveals whether a
job exists — the same property §6.3 F-2 states for the capability check, and
`test_r46_path_404_precedes_the_nonce_rule` asserts it in both directions.

### Not a shared grammar with R-42

`application.web.jobs.parse_preview_nonce` was **not** generalized and **not**
called. R-42 and R-46 have opposite idempotency requirements — R-42's nonce is
minted per R-40 render so a Council member can take a *second* preview; R-46's is
the preview job's id so one preview can produce only *one* durable effect — and
folding them into one parser would name a similarity that does not exist.
`application/web/jobs.py` is byte-identical to its pre-remediation state:
`6a934e3418c69ca36c8d1a7de8fc75b5915dcee4ff6ddbe6364c32277acbd7ba`.

### Not constant-time, deliberately

The compared value is the job id from the caller's own request path. There is
nothing secret to leak by timing. The `preview_token`, which *is* compared
against stored state, is still compared in constant time by
`application/web/jobs._constant_time_equal`, unchanged.

---

## 3. Files changed, and why

| File | Why |
|---|---|
| `adapters/web/import_routes.py` | added `_submitted_apply_nonce(form, identifier)` at module scope; R-46 now calls it instead of `.strip()`-ing `form.get("nonce")` |
| `tests/web/test_p3_4_job_status_views.py` | 8 new tests — the hostile-nonce table, no-echo, cross-preview, denial precedence, transport precedence, `404` precedence, the boundary rule without a request, and an executable falsification of the two removed defects |
| `tests/web/test_p3_3_jobs.py` | four hand-built R-46 nonces canonicalized; the two-browser fence case reworked (below) |
| `tests/web/test_p3_3_matrix.py` | two hand-built R-46 nonces canonicalized |
| `tests/web/test_p3_3_success_cells.py` | one hand-built R-46 nonce canonicalized |

`_submitted_apply_nonce` is at **module scope** rather than inside `register`,
unlike its R-42 counterpart, because it closes over nothing and because its
non-`str` branch is otherwise unreachable from an HTTP test: a multipart body is
answered `415` by the content-type guard long before the nonce rule runs, so the
only way to prove that branch is to call the function directly.

### Declared scope note

`tests/web/test_p3_3_matrix.py` and `tests/web/test_p3_3_success_cells.py` are
**not literally in the remediation allowlist**, which names `test_p3_3_jobs.py`,
`test_p3_4_job_status_views.py` and "a narrowly relevant shared P3.3/P3.4 test
helper". They were edited because they are older R-46 cases submitting
`nonce=confirm-C`, `nonce=combined` and `nonce=probe` — hand-built values the
production form never emits — and enforcing the accepted contract necessarily
turns those into refusals. Three of their cases failed on the first full run for
exactly that reason. The edits change only the submitted nonce text.
**Flagged for Peter's explicit ratification.**

### The one test whose *shape* changed, not just its value

`test_p3_3_jobs.py::test_two_browsers_confirming_the_same_preview_resolve_to_one_apply`
proved TC-JOB-08's `uq_reconciliation_jobs_one_live_apply` fence by submitting
`nonce=browser-a` and `nonce=browser-b` from the **same** Council account, so the
two request keys differed only because the two nonces did. Under the canonical
rule neither browser can choose an identity, so that arrangement no longer
exists: two submissions from one account are now one request key and resolve by
idempotency, which would have made the case pass while measuring the wrong fence.

It now uses **two Council accounts** (`C` and `CA`) with the identical canonical
nonce. The request key includes the account, so the keys still differ, and the
one-live-apply fence is still the only thing that can refuse the second — which
is also how two browsers actually reach two request keys in production. The
assertions are unchanged: `303`, then `409`, then exactly one `apply` row.
`test_p3_4_job_status_views.py::test_a_second_council_member_confirming_concurrently_starts_nothing`
already proved the same property this way and was not touched.

No uniqueness, concurrency, authorization, CSRF, non-enumeration, audit, digest,
cleanup or disclosure assertion was weakened or deleted anywhere.

---

## 4. Direct malformed / duplicate / alternate outcomes, with no-effect proof

`test_r46_admits_only_the_canonical_preview_job_nonce` is a direct `POST` to
R-46 that **never fetches R-43 first**, against real disposable PostgreSQL. All
28 refused cases run against **one** preview, deliberately: none may reach
`enqueue_apply`, so none may consume the preview or trip the one-live-apply
fence — and the accepted submission at the end of the table, from that same
still-confirmable preview, is what proves they did not.

| Group | Cases | Outcome |
|---|---|---|
| absent / empty | `absent`, `empty` | `422`, no effect |
| other identity | `other_uuid`, `nil_uuid` | `422`, no effect |
| parseable spellings | `uppercase`, `unhyphenated`, `braced`, `urn_prefixed` | `422`, no effect |
| whitespace a `.strip()` would repair | `leading_space`, `trailing_space`, `surrounding_whitespace`, `internal_space` | `422`, no effect |
| padding / punctuation | `trailing_semicolon`, `quoted`, `query_appended` | `422`, no effect |
| control characters | `newline`, `carriage_return`, `null_byte` | `422`, no effect |
| Unicode | `unicode_hyphen` (U+2010), `zero_width_space`, `emoji_suffix` | `422`, no effect |
| oversized inside the 8 KiB bound | `oversized_in_bound` (7000 ch.), `canonical_then_padding` | `422`, no effect |
| multiplicity | `duplicate_identical`, `duplicate_canonical_first`, `duplicate_canonical_second`, `duplicate_empty_second` | `422`, no effect |
| **accepted** | exactly one `nonce=str(job_id)` + correct `preview_token` | **`303`**, one apply, one `reconciliation.apply_requested` |

Every refused case additionally asserts `data-field="nonce"` (and *not*
`data-field="preview_token"`, so the response names the field that was actually
wrong), and re-reads `reconciliation_jobs` on a fresh connection to prove
`apply_jobs_for(...) == []`.

**No apply job and no success audit effect.** The whole table is bracketed by a
before/after count of `reconciliation.apply_requested` + `reconciliation.job_queued`
and by a total row count of `audit_events`; both deltas are zero. The totals are
deltas rather than absolutes because `audit_events` is append-only — the
migration's trigger refuses `DELETE`, so the table is never truncated between
cases and `audit_events.id` is a UUID rather than a sequence, which is why no
high-water mark is available.

**Nothing is echoed.** `test_a_refused_r46_nonce_is_never_echoed_anywhere`
submits `zz-marker-<script>alert(1)</script>-zz` and asserts the marker appears
in no response body, no response header, no `reconciliation_jobs.request_key`
and no `audit_events` payload, and that no apply row was created.

**A valid nonce for the wrong preview is still refused.**
`test_r46_refuses_a_nonce_naming_a_different_real_preview` seeds a *second* real,
completed, confirmable preview for the same Council caller and confirms preview A
with preview B's id: `422`, and neither snapshot gains an apply. This is the case
that fails if the boundary ever validates "is a UUID" rather than "is *this*
job", and it is why the rule does not re-parse.

---

## 5. Authorization, CSRF and path precedence under every nonce shape

* `test_r46_denial_precedence_is_unchanged_by_the_nonce_shape` — every cell of
  `ACCEPTED_ROUTE_CALLER_MATRIX["R-46"]` (`U N M C A CA BG AC`), each against its
  own fresh preview, submitted with a hostile nonce. Refused callers receive the
  guard's exact status (`401`/`403`) and **never** `422` — a `422` would confirm
  to an unauthorized caller both that the job exists and that only their nonce
  was wrong. Permitted callers (`C`, `CA`) reach the field rule and get `422`.
  Every cell enqueues nothing.
* `test_r46_csrf_and_transport_refusals_precede_the_nonce_rule` — for both a
  canonical and a hostile nonce: missing CSRF `403 csrf_invalid`, wrong CSRF
  `403 csrf_invalid`, multipart `415`, oversized body `413`. No apply enqueued.
* `test_r46_path_404_precedes_the_nonce_rule` — a malformed path is `404
  object_not_reachable` for a canonical-looking, a hostile and an empty nonce; an
  absent job with its own canonical nonce is `404`; and a hostile nonce is
  byte-identical against an absent and an existing job.
* `test_r46_is_not_reachable_for_a_malformed_or_absent_job` (existing) updated to
  confirm each absent job with **its own** canonical nonce, so the two denials are
  still compared on requests that reach the object lookup at all.

---

## 6. Duplicate and concurrent confirmation against PostgreSQL

Unchanged accepted semantics, all re-proved with the canonical nonce:

* **Double-click and retried lost response** —
  `test_a_double_click_and_a_retried_lost_response_converge_on_one_apply` reads
  the nonce out of the **rendered R-43 page** rather than inventing it, asserts
  it equals `str(preview_id)`, submits three times, and gets one location, one
  apply row and exactly one `reconciliation.apply_requested`. A second render
  reproduces the same identity.
* **Two browsers / two accounts** —
  `test_a_second_council_member_confirming_concurrently_starts_nothing` (P3.4) and
  the reworked `test_two_browsers_confirming_the_same_preview_resolve_to_one_apply`
  (P3.3): `303` then `409 duplicate_request`, one apply row, one audit event.
* **Two concurrent inserts at the database** —
  `test_two_concurrent_inserts_of_one_live_apply_leave_one`, two real connections
  and the partial unique index, untouched and green.
* **Stale, expired, changed-scope, wrong-token, blocked and already-running** —
  the existing expired-preview, folder-change, profile-version-change,
  wrong-preview-token, revoked-Council and running-apply cases all retain their
  accepted `409`/`403` semantics and their zero-effect assertions, now with the
  canonical nonce.

No duplicate apply, duplicate audit effect, partial mutation, false success or
constraint bypass was observed at any point.

---

## 7. Verification

Environment: `/opt/discord-bots/venv-web/bin/python` 3.12.3, pytest 8.4.2,
`TEST_DATABASE_URL='postgresql+psycopg:///freedom_test'` — the disposable local
database, present and used. **No dependency was installed.** Nothing was skipped
for want of a database in either prescribed run.

### Focused Step 9 evidence

```bash
TEST_DATABASE_URL='postgresql+psycopg:///freedom_test' \
  /opt/discord-bots/venv-web/bin/python -m pytest -q -rs \
  tests/web/test_p3_3_jobs.py tests/web/test_p3_4_job_status_views.py
```

| | passed | failed | skipped |
|---|---|---|---|
| baseline, before this remediation | 105 | 1 | 0 |
| after | **113** | **1** | **0** |

The one failure is `test_template_digests_match_accepted_corpus` — Finding 3, the
Step 10 stop condition, unchanged. +8 tests, all passing.

### Prior remediation and structural evidence

```bash
TEST_DATABASE_URL='postgresql+psycopg:///freedom_test' \
  /opt/discord-bots/venv-web/bin/python -m pytest -q -rs \
  tests/web/test_account_identity_refusal_audit.py \
  tests/web/test_p3_4_snapshot_views.py tests/web/test_structural_guards.py
```

**1 failed, 141 passed, 0 skipped.** The one failure is again
`test_template_digests_match_accepted_corpus`. `test_structural_guards.py` alone:
**70 passed** — the R-37 dependency-direction guard and the ratchet both hold.

### Complete accepted P3.4 surface through Step 9

```bash
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
| previous remediation's record | 509 | 7 | 0 |
| after | **517** | **7** | **0** |

The same seven digest-preservation tests, failing for the same reason on the same
three templates. **+8 net tests, all passing; no new failure.**

### R-46's other homes

```
tests/web/test_p3_3_matrix.py tests/web/test_p3_3_success_cells.py
  → 90 passed, 26 skipped, 0 failed
```

The 26 skips are the pre-existing by-design `test_p3_3_matrix.py:198`
*"permitted cells are asserted by the per-route success cases"*.

### Whole suites

* **Full `tests/web`** — **25 failed, 1971 passed, 80 skipped.** Identical failure
  *set* to the pre-remediation baseline recorded in
  `phase-3-p3-4-step-09-remediation-handoff.md` §6 (25 failed, 1963 passed, 80
  skipped): the 7 digest failures plus the same 18 that predate this work and
  belong to other owners — 8 × `test_p3_3_disclosure_and_bounds` hostile-name
  cases and `test_security_controls::test_no_view_model_field_reaches_a_script_context`
  (all on the `<script defer src="/static/vendor/htmx-…">` tag in `base.html`),
  5 × `test_identity_migration_command`, 3 × `test_oauth_refusal_audit`, and
  `test_p3_3_audit_search::test_the_cursor_pages_forward_without_repeating_or_dropping_a_row`.
  **No new failure. +8 passing tests.**
  *Interim note:* the first full run after the route change showed **28** failures
  — the 25 plus the three R-46 cases in `test_p3_3_matrix.py` and
  `test_p3_3_success_cells.py` that submitted hand-built nonces. Those three are
  the reason those two modules were edited (§3), and they are green.
* **Bot suite**, `/opt/discord-bots/venv/bin/python -m pytest -q tests` —
  **2034 passed, 260 skipped, 0 failed**, unchanged.

### Formatter, linter, type checker, compileall, whitespace

| Check | Result |
|---|---|
| formatter | **not run — none configured or installed.** No `pyproject.toml`, `setup.cfg`, `.pre-commit-config.yaml`, `.flake8`, `ruff.toml` or `mypy.ini`; `black`/`isort` absent from `requirements*-dev.txt` and from `venv-web` |
| linter | **not run — none configured or installed** (`ruff`, `flake8`, `pylint` all absent) |
| type checker | **not run — none configured or installed** (`mypy`, `pyright` absent) |
| `compileall` | **passed**, exit `0`, over the five changed modules and over `application/` and `adapters/` |
| `git diff --check` | **passed**, exit `0`, clean |
| dependency-direction check | the repository's mechanism is `tests/web/test_structural_guards.py`; **70 passed** |

None of the three uninstalled tools is claimed to have passed.

---

## 8. Falsification

Each defect was reintroduced **alone** into `adapters/web/import_routes.py`, the
focused Step 9 command was run, the file was restored from a byte copy taken
before any mutation, and the restored SHA-256 was compared to the value recorded
first.

Original and restored digest, verified after **every** probe:
**`396a5f173ddc260015df36de32998250a2e4a407eaf62d86436c15d7091f8d4b`**

| # | Defect reintroduced | Mutated SHA-256 | Tests that failed |
|---|---|---|---|
| 1 | `value = value.strip()` before the comparison, so a whitespace-padded nonce is repaired | `3c0f4ce8d1d4aa4b2144893d5944f7d3b66f8e9ba6ddaabac829dda77fe0a7ed` | `test_r46_admits_only_the_canonical_preview_job_nonce`, `test_the_apply_nonce_rule_admits_exactly_one_canonical_text_value`, `test_falsification_a_stripping_or_first_wins_apply_nonce_rule_is_caught` |
| 2 | `if not submitted` + `form.get("nonce")`, so a duplicated key is resolved by precedence | `abfd3a6cbabfe85ff00803a99cd94ca037538f21065474133c0da723391a1071` | the same three |
| 3 | `UUID(value)` parse instead of equality, so any well-formed UUID is accepted for this preview | `23ff51d8b247dad9e37331e6e9fd7a2156065bbfeed1a17bc82db898b7bc02f4` | `test_r46_admits_only_the_canonical_preview_job_nonce`, **`test_r46_refuses_a_nonce_naming_a_different_real_preview`**, `test_the_apply_nonce_rule_admits_exactly_one_canonical_text_value` |
| 4 | the original defect restored verbatim — `(form.get("nonce") or "").strip()` / non-empty — so two direct submissions choose different arbitrary request identities | `911985d66a2776e76485dcc7637af2b88113fd409fef85478579e50871eee0c1` | `test_r46_admits_only_the_canonical_preview_job_nonce`, `test_a_refused_r46_nonce_is_never_echoed_anywhere`, `test_r46_refuses_a_nonce_naming_a_different_real_preview`, `test_r46_denial_precedence_is_unchanged_by_the_nonce_shape`, `test_r46_path_404_precedes_the_nonce_rule` |

(The `test_template_digests_match_accepted_corpus` failure is present in every
run, before and after, and is Finding 3 rather than a probe result.)

Defects 1 and 2 are additionally kept as **executable** probes inside
`test_falsification_a_stripping_or_first_wins_apply_nonce_rule_is_caught`, which
rebuilds a trimming rule and a first-wins rule beside the real one and shows the
two disagree — so the assertions are demonstrably load-bearing without needing a
mutation.

`grep` confirms no probe text (`value.strip()`, `UUID(value)`,
`form.get("nonce")`) remains in `adapters/web/import_routes.py`.
**No falsification mutation remains in the tree.**

---

## 9. Safety confirmation

* **Untouched, byte-identical, verified by SHA-256:**
  `adapters/web/templates/job_status_fragment.html`
  (`81fcd1bb2a80657c979e8c4581657bb0ba0b3940fb689ca7d56483c9d66ee234`) and
  `application/web/jobs.py`
  (`6a934e3418c69ca36c8d1a7de8fc75b5915dcee4ff6ddbe6364c32277acbd7ba`).
* **R-42's separately accepted random nonce contract was not modified** —
  `parse_preview_nonce`, `mint_preview_nonce`, `_PREVIEW_NONCE_GRAMMAR` and
  `_submitted_preview_nonce` are unchanged, and the new rule does not call them.
* **No template, no template digest, no schema, no migration, no route path or
  method, no capability meaning, no session/CSRF design, no audit-disclosure
  policy, no worker state machine, no Phase 3 contract document and no P3.5+
  scope was changed.** `git status --short migrations/ adapters/database/` is
  empty. No expected hash was updated.
* No commit, no push, no deployment. No live service, no Discord, no Google
  Sheets, no Foundry, no production PostgreSQL. `.env`, credentials, secrets,
  real snapshots and player data were never read. All fixtures are the synthetic
  Phase 2 bundles; the only database touched is the disposable local
  `freedom_test`.
* Unrelated user changes in the shared tree — including the entire in-flight
  Step 10 frontend work — are preserved untouched. `git status` gained exactly
  **one** entry relative to the pre-remediation baseline:
  `tests/web/test_p3_3_matrix.py`.

---

## 10. Remaining blockers

1. **Finding 3 / P3.G4 — unchanged and still red.** The seven
   digest-preservation failures stand until Step 10 for `import_result.html`,
   `audit_search.html` and `audit_results.html` is released, implemented,
   independently reviewed and accepted with the exact SHA-256 of the accepted
   bytes recorded in dated evidence. Nothing here updated an expected hash,
   restored those templates or claimed the gate is green. Peter's decision is
   required on how the corpus transition is controlled.
2. **Eighteen further `tests/web` failures predate this work** and belong to
   other owners (§7). Unchanged.
3. **Ratification wanted** for the two out-of-allowlist test modules edited in
   §3, and for the two-account reshaping of the P3.3 two-browser fence case.
4. Still open from the previous handoff and **not** addressed here:
   `application/web/role_mappings.run_mapping_change` and the five other
   pre-existing `application → adapters` imports;
   `tests/web/test_p3_4_static_assets.py::test_no_unrelated_production_files_modified`
   silently passing every modified file because it `.strip()`s before slicing;
   and the seven copied `ACCEPTED_TEMPLATE_DIGESTS` dictionaries.

**P3.G4 is not marked accepted.** Stopping here for independent re-review and
Peter's decision.
