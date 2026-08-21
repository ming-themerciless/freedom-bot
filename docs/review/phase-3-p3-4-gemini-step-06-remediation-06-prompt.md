# Prompt for Gemini — P3.4 Step 6 remediation 06

Date: 2026-08-20 · Status: **RELEASED BY PETER / ACCEPTANCE AUTHORITY**

Peter's instruction to update documentation and write this fully contextualized
prompt is the single authorization and release. Do not request another
approval. Make this one-file test correction, report the checkpoint, and stop.
Step 7 and every later step remain unreleased.

## Complete context

Step 6 implements Council character views R-22–R-27. Production templates and
their contracts are now correct and frozen. Remediations 01–05 progressively
closed rendering, HTMX, URL encoding, authorization matrix, CSRF/stale writes,
cleanup validation, access-state snapshots, and exact denial headers. The only
remaining issue is the fidelity of R-25 audit no-write evidence and the
structural validator that must protect it.

Production behavior is authoritative:

- `CharacterAccessService.grant()` creates a new `access_id` only after version
  validation and the access-row insert.
- It records action `character_access.granted` with
  `entity_type = "character_access"` and `entity_id = str(access_id)`.
- Its audit JSON payload contains `character_id`, `platform_account_id`,
  `access_kind`, `default_character`, before/after facts, version and reason.
- Consequently, a refused R-25 request has no known access ID with which to
  query `audit_events.entity_id`.
- The current test incorrectly executes
  `WHERE entity_id = :cid` with `str(character_id)`. That can never match a
  correctly shaped R-25 grant audit event and therefore cannot detect an
  erroneous audit-only partial write.
- R-26 and R-27 already know `access_id`; their production events use that ID
  as `entity_id`, so an exact entity/action predicate is available.

## Sole write and starting hash

Edit only:

`tests/web/test_p3_4_council_character_views.py`

Required starting SHA-256:

`e470181392dd6af6a96f315a14cdf3708c7eac7139dcb1d2330519572cfc5c36`

Read `.agents/AGENTS.md`, `docs/implementation-plan.md`, all Step 6 prompts and
reviews, `application/web/character_access.py` grant/revoke/default event
creation, the `audit_events` table definition, and existing audit-query tests.
Preserve all other work. Stop on mismatch or any need to edit production,
shared helpers, contracts, configuration, dependencies, documentation, assets,
manifests, or other tests.

## Correction 1 — production-faithful audit snapshots

Change `snapshot_r25_state` so its audit component counts or returns immutable
IDs for exactly the relevant potential grant events using stable production
facts, not `entity_id = character_id`. Its SQL must require:

- `action = 'character_access.granted'`;
- `entity_type = 'character_access'`; and
- JSON payload `character_id` equal to `str(character_id)`.

Also bind the target account payload if the stored JSON representation and
existing audit-query conventions make that exact and portable. Use PostgreSQL's
accepted JSON extraction syntax for the actual `json_type`; do not cast the
entire payload to text or use substring/`LIKE` matching.

For `snapshot_r26_state`, require the audit predicate to use
`entity_id = str(access_id)`, `entity_type = 'character_access'`, and action
`character_access.revoked`.

For `snapshot_r27_state`, require `entity_id = str(access_id)`,
`entity_type = 'character_access'`, and action
`character_access.default_changed`.

Continue returning immutable snapshots containing character version and all
operation-owned access state. All nine refused requests must compare exact
before/after snapshots.

## Correction 2 — validator must prove actual attribution and data flow

Strengthen the same positive validator used on the real module. For each
snapshot helper, validate the exact literal SQL shape (normalized whitespace is
fine), table, closed action, entity type, JSON payload/entity predicate,
parameter keys, and parameter values bound from the correct function arguments.
Validate that query scalar/ID results flow into the returned tuple alongside
the exact character-version result and required access state.

It must reject:

- R-25 `entity_id = character_id`;
- an unfiltered/global audit count;
- payload text casting, `LIKE`, or substring matching;
- wrong/missing action or entity type;
- R-26/R-27 using character ID instead of access ID;
- wrong parameter key/value, literal ID, unused correct query beside a returned
  unrelated value, constants/aliases without data flow, and omitted tuple field.

## Correction 3 — exact refusal request and uninterrupted ordering

For each of the nine refusal sequences, the validator must additionally prove:

1. the before snapshot occurs in a bound connection;
2. the next relevant operation is `await client.post(...)` to the exact R-25,
   R-26 or R-27 path expression for that case;
3. the request uses the expected body class: missing CSRF, invalid CSRF, or
   valid CSRF with stale version;
4. the expected `403` or `409` status assertion immediately follows;
5. no other awaited request, mutation helper, database write context, or
   assignment to the tracked character/access identifiers occurs between the
   before and after snapshots;
6. the after snapshot uses a distinct bound connection, identical helper and
   identifiers; and
7. exact equality immediately follows that snapshot.

Reject wrong HTTP method, wrong route/action/access ID, swapped/literal helper
arguments, wrong refusal body, intervening mutation/request, reordered status,
or equality before/away from the after snapshot.

Every negative probe must change one semantic property and call the same
positive validator. Include direct falsifications for the original R-25
character-ID `entity_id` bug and for an intervening mutation. Comments,
docstrings and unused correct-looking SQL must not satisfy the validator.

If `TEST_DATABASE_URL` is absent, the database case may skip but every
structural/falsification test must run. Do not read `.env`, discover/provision a
database, or claim skipped PostgreSQL evidence.

## Verification

Run and report:

```bash
sha256sum -c docs/review/phase-3-visual-freeze-manifest.sha256
sha256sum -c adapters/web/static/asset-integrity.sha256
./venv-web/bin/python -m pytest -q tests/web/test_p3_4_council_character_views.py
./venv-web/bin/python -m pytest -q tests/web/test_p3_4_council_character_views.py tests/web/test_p3_4_member_views.py tests/web/test_p3_4_auth_and_system_views.py tests/web/test_p3_4_shell_and_components.py tests/web/test_p3_4_static_assets.py tests/web/test_static_asset_surface.py tests/web/test_structural_guards.py -m "not database"
./venv-web/bin/python -m pytest -q tests/web/test_p3_4_council_character_views.py tests/web/test_p3_4_member_views.py tests/web/test_p3_4_auth_and_system_views.py tests/web/test_p3_4_shell_and_components.py tests/web/test_p3_4_static_assets.py tests/web/test_static_asset_surface.py tests/web/test_structural_guards.py
./venv-web/bin/python -m compileall -q tests/web/test_p3_4_council_character_views.py
git diff --check
git status --short
```

Report the final test-file hash, confirmation that every other file stayed at
its checkpoint hash, exact pass/skip counts, whether PostgreSQL ran, and every
unrun check. A skip is not database evidence.

## Stop

Report `READY FOR INDEPENDENT STEP 6 REMEDIATION 06 REVIEW`, then stop. Do not
begin Step 7, update documentation, commit, push, deploy, access secrets/real
data, contact live services, or claim Step 6 acceptance.
