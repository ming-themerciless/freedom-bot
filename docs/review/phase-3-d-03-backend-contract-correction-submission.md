# D-03 backend-contract correction — submission

**Work date:** 2026-08-19 · **Handoff completed:** 2026-08-20 (the session ran
past midnight; the contract annotations are dated 2026-08-19 because that is the
date `C-P3.4-A` was accepted and the date the edits were made) · **Package:**
bounded D-03 correction under change-log `C-P3.4-A` · **Owner:** Claude, backend
contract owner and working Technical Lead

**Status: submitted for review. Not accepted, not self-accepted.**

> **D-03 remains OPEN. Gemini remains BLOCKED.**
> `docs/review/phase-3-p3-4-gemini-implementation-prompt.md` remains **held** and
> is **not** marked released. P3.G4, I-06 and A-05 remain open. No staging
> exposure, deployment, production use, live-service contact or real-player-data
> use is authorized or claimed by this submission.

Peter/Acceptance Authority accepted `C-P3.4-A` as written on 2026-08-19,
authorizing a bounded backend-contract correction for D-03-1 through D-03-6. This
is that correction, delivered for an independent Codex implementation review and a
distinct Codex security-focused review, after which the corrected contract returns
to Peter for acceptance and an explicit release decision on the Gemini prompt.

---

## 1. The six accepted decisions and how each was implemented

| # | Accepted decision | Kind | Where it landed |
|---|---|---|---|
| D-03-1 | Application-served `/static/` with `GET`/`HEAD`, no authentication, trusted-host enforcement, kill-switch availability, fingerprint-aware cache headers, and structural inventory of mounts | **New surface + new guard** | Route contract §1.2 (new), operational contract §4.1/§4.3/§4.4, threat model §2 + T-54/T-55, `adapters/web/static_assets.py` (new), `adapters/web/static/` (new), `adapters/web/app.py`, `adapters/web/composition.py`, `adapters/web/middleware.py`, `tests/web/test_structural_guards.py`, `tests/web/test_static_asset_surface.py` (new), `tests/web/test_security_controls.py` |
| D-03-2 | Define `ConfirmScope` with its eight implemented fields | **Record** (definition) | View-model contract §7, VM-15 block |
| D-03-3 | Define `CharacterFilters` with `query` and `include_inactive` | **Record** (definition) | View-model contract §5, VM-07 block |
| D-03-4 | Record VM-13's additive `csrf_token`; correct its inaccurate P3.2 provenance statement | **Record** (+ retraction) | View-model contract §4 VM-13 block; `application/web/view_models.py` docstring |
| D-03-5 | Record R-36 as `200` HTML rendering VM-13 denied, not `303` | **Record** (correction) | Route contract §5 table and §5.1 prose |
| D-03-6 | Dedicated typed `DeniedView` with only `state` and a closed-vocabulary `reason`, preserving byte-identical denial `404`s | **New type + carrier swap** | View-model contract §8 (VM-22, new), `application/web/view_models.py`, `adapters/web/portal_routes.py`, `adapters/web/import_routes.py` |

**Four of the six changed no runtime behaviour at all.** D-03-2, D-03-3, D-03-4
and D-03-5 are definitions and record corrections: the implementation they
describe is exactly what P3.2 and P3.3 delivered and what P3.G2/P3.G3 accepted.
D-03-1 adds a new URL surface. D-03-6 changes which typed object is handed to an
unmodified template, and the rendered bytes are unchanged (§5, byte-identity).

### 1.1 The decisions in detail

**D-03-1.** `/static` is a single Starlette `Mount`, identifier **M-01**, served
by `freedom-web` out of `adapters/web/static/`.

- **Methods:** `GET` and `HEAD`; everything else is `405`, uniformly for present
  and absent paths so the refusal cannot enumerate filenames.
- **Caller:** public — all eight caller states, no session, capability, CSRF token
  or `Origin` requirement.
- **Host:** the existing `HostGuard` is the outermost middleware and the mount is
  registered inside it, so an unknown `Host` is `400` on an asset exactly as on a
  page.
- **Kill switch:** exempt, by a named closed rule (`KillSwitch.exempt`) that now
  admits `/healthz` and `/static/` and nothing else.
- **Cache:** `<stem>.<16 lowercase hex>.<ext>` → `public, max-age=31536000,
  immutable`; anything else → `public, max-age=0, must-revalidate`. The
  conservative branch is the default.
- **Grammar:** `/static/<segment>[/<segment>…]`, `segment := [A-Za-z0-9][A-Za-z0-9._-]*`,
  checked before the filesystem is touched. A violation is `404`, byte-identical
  to a missing file.
- **Cookies:** none set, none refreshed. `SecurityHeaders` is scoped out of its
  `no-store` rule for this prefix only; all six security headers still apply.
- **Mounts in the inventory:** `MOUNT_INVENTORY` in `adapters/web/app.py`, route
  contract §1.2's table, and a new half of TC-STRUCT-01 asserting them against
  each other in both directions plus the count.

**Why the application and not Caddy** — operational contract §4.1 gives Caddy
exactly two jobs, TLS and HSTS, and assigns every other header to the application
so each header has one authority. A `file_server` would have broken that rule for
precisely the responses whose headers matter most to N-26: the CSP and `nosniff`
on an asset would come from the application's middleware only if the request
reached the application, which by construction it would not. It also keeps the
surface inside an inventory a test can assert, and keeps development and
production identical. The cost is stated honestly in §4.4: asset requests occupy
`freedom-web` workers.

**D-03-6.** `DeniedView(state, reason)` replaces `NonMemberView` at both `_denied`
helpers. `denied.html` is **not modified** — it already rendered only
`view.reason.category.value`, which is why the rendered bytes are identical and
why no production template needed to change. VM-02 keeps `non_member.html` with
its guild name, check time and correlation id, which is intentionally permitted
membership-recovery context and is asserted as preserved.

---

## 2. Exact files and edited regions

Line counts are **this package's** diff against the pre-edit state, not the diff
against `HEAD` — the working tree carried substantial pre-existing user changes
before this package began, and reporting those as mine would be a false claim.

### 2.1 Modified

| File | Edited regions | +/− |
|---|---|---|
| `docs/contracts/phase-3-route-authorization-contract.md` | Status block (dated correction note); §1 exhaustiveness claim; §1's TC-STRUCT-01 paragraph; **§1.2 new**; §2.1 step 2; §2.3 denial-body paragraph; §5 table R-36 *Response* cell; §5.1 R-36 prose; §7.1 *Denied* row | +131 / −7 |
| `docs/contracts/phase-3-view-model-contract.md` | Status block; VM-13 block + `csrf_token` prose; VM-07 block + `CharacterFilters` definition; VM-15 block + `ConfirmScope` definition; **§8 VM-22 new**; §10 traceability row | +145 / −0 |
| `docs/contracts/phase-3-operational-contract.md` | Revision note; §4.1 `/static/*` row; §4.3 exemption paragraph; **§4.4 new** | +49 / −0 |
| `docs/contracts/phase-3-threat-model.md` | Status note; §2 entry-point row; §4 T-54 and T-55; §6 verification-mapping row | +11 / −0 |
| `docs/contracts/phase-3-test-traceability.md` | TC-STRUCT-01 amended by addition; TC-SEC-14, TC-VM-06, TC-STATIC-01…07 rows; **§22 new** | +35 / −1 |
| `docs/operations/web-portal.md` | §5 kill-switch exemption; **§9 new** | +37 / −3 |
| `adapters/web/app.py` | Module docstring; two imports; `MOUNT_INVENTORY`; the `app.mount(...)` call; `__all__` | +37 / −1 |
| `adapters/web/composition.py` | `STATIC_ROOT` and its rationale; `__all__` | +16 / −0 |
| `adapters/web/middleware.py` | Chain docstring; `STATIC_PREFIX`; `KillSwitch.exempt` + dispatch; `SecurityHeaders` scoping + docstring; `__all__` | +49 / −4 |
| `adapters/web/portal_routes.py` | Module docstring; `DeniedView` import; `_denied` body and docstring | +18 / −5 |
| `adapters/web/import_routes.py` | `DeniedView` import; `_denied` body and docstring | +8 / −5 |
| `application/web/view_models.py` | `DeniedView` (VM-22); VM-13 `csrf_token` docstring retraction; `IMPLEMENTED_VIEW_MODELS` entry | +45 / −1 |
| `tests/web/test_structural_guards.py` | `Mount` import, `MOUNT_INVENTORY` import; `_MOUNT_ROW` + `parsed_contract_mounts()`; two mount cases; TC-STRUCT-01 docstring; two denial-view cases | +102 / −1 |
| `tests/web/test_security_controls.py` | TC-SEC-14: three cases and the marker table | +89 / −0 |

### 2.2 Created

| File | Purpose |
|---|---|
| `adapters/web/static_assets.py` | `StaticAssets`, the URL grammar, the cache policy |
| `adapters/web/static/.gitkeep` | Zero-byte placeholder; makes the root exist for `StaticFiles(check_dir=True)` |
| `tests/web/test_static_asset_surface.py` | TC-STATIC-01…07 (54 cases) |
| `tests/web/test_d03_contract_correction.py` | D-03-2…D-03-6 (25 cases) |
| `docs/review/phase-3-d-03-backend-contract-correction-submission.md` | This document |

### 2.3 Deliberately **not** modified

`adapters/web/templates/denied.html` and every other production template;
`design-prototype/` and its freeze manifest; any authentication, capability,
persistence, migration, runtime-grant or use-case module; any route path or
method other than the added `/static/` surface; `.env.example`;
`requirements-web*.txt`; the accepted P3.2 submission; and every historical gate
record. `denied.html`'s digest is unchanged and is reported as such in §3.

---

## 3. Before/after SHA-256

`absent` means the file did not exist before this package.

| File | Before | After |
|---|---|---|
| `docs/contracts/phase-3-route-authorization-contract.md` | `5b1f7348ec22a3e0793bfcddd5f51606320efa42ffd46abd109082a83b0212ae` | `b6dee35fbd8ef357deec12cd10936b01eec7c589170f3ccdb591794c10178dac` |
| `docs/contracts/phase-3-view-model-contract.md` | `9536061854d3a3eccd19126d366f97140d3f9211b3a24e5f2354634e86146879` | `55901f3cfdd0ca3e755fe0770c86e2f0c6b2cebe38387666311e5708baa16eba` |
| `docs/contracts/phase-3-operational-contract.md` | `185f43f82e8c244a7891277afc6d174fe1b818629d6f21e4b58ab913cd974b23` | `1e95c89e796bbfda43b8b718e191f59c177f94d29f9feb11ae09cfbc05886dd9` |
| `docs/contracts/phase-3-threat-model.md` | `c225c884ac4312cf66d194775a27e2effc6267d327ba89f63e4b0365ecc1caae` | `308c136dc9297296b99f4624e69ab8cf1d6b455d05e56a0dd00a48bfff54a327` |
| `docs/contracts/phase-3-test-traceability.md` | `c5442287a8646e2645899260124f2f53cc7c843be56cf73668bf2ad577162fa0` | `ade915c6438e9666840ce670c3de2967168b1cad6921bb426657a27480b8798d` |
| `docs/operations/web-portal.md` | `713bc3c3a580a244d968a3783035c92861634370a12904767d110b867ca36626` | `76b136de4064b14ca060f83a80e58f1a74617972138f68623b949e622f855e70` |
| `adapters/web/app.py` | `3ee4e19640aec6a050034108f747479105d0995113785db6d95a3a4df2f1f11f` | `f4153bc422baa5d6ffd5da792de65c643096205fe08622d52ae2df31ab10f388` |
| `adapters/web/composition.py` | `2f53d9331cf24aa6a3018c9bd325a0e9ac5aed972802ae447c49804c9152a209` | `06894e3d2b223920cbfe6463af96dccaa5f0f760eb98f93f5963cedd89ce26a0` |
| `adapters/web/middleware.py` | `f508647a3488487d881115f287a1bc954928a262e6c51dbed54e953fcc5eadd5` | `60a3a1cc2086ed03f17f9afc8ea092bcc5164f7e8ad3f848736882ec7e5eab6b` |
| `adapters/web/portal_routes.py` | `082a556a3127206767757483a1ee4f366a53f07200442437e9c1711c60077aa4` | `d24ce0d37313e9bb5209751d0a7dded1616f4054c457eb55f24282ae6902db4b` |
| `adapters/web/import_routes.py` | `e4abbd74e98eff5d670e48a13196ca843188696cf6a9af201181d311b934f409` | `0589a02b50f0ac2e48f14422f8f40704b43852f6de9526c36c2d0185e36883a1` |
| `application/web/view_models.py` | `5026b95077d557cb9f7a99ff3c35cf6a268f319638577332495a94cd9ae46f3c` | `8a8069c53aa2d09e23dccf4315ca4f0378c73a483503bf9ae57d6e27244f4f65` |
| `tests/web/test_structural_guards.py` | `45a993cd3a7ded7d5c2f913b6c32a26fa2b51a334b6a1868601ade195d50d7db` | `861d91d83c245598bacdc672e6ef4b5a8c405dc80cd3970227aa0ad954065b9e` |
| `tests/web/test_security_controls.py` | `67509f7acddf162f09570681e73c26f2e674ad3974292b9a188996dfb9d20265` | `1cb728b880a245713b7785b721700fbc13cbfa20f5d8f33f7b98cd0e9260678f` |
| `adapters/web/static_assets.py` | `absent` | `98cf16170f6e80524f6c877c8b1a7265fe2fd903ac43658dde2bcc6500d477a2` |
| `adapters/web/static/.gitkeep` | `absent` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `tests/web/test_static_asset_surface.py` | `absent` | `d4c00b54303028466e905e9db6e3bc6cd30eb9e64eada73d8a869d8bfb75d855` |
| `tests/web/test_d03_contract_correction.py` | `absent` | `b6e3a757f7244f62e83eb555f48fbc8b39de312b55b9e050d6be41fc92af06d0` |

**Unchanged and verified unchanged**, because the correction was expected to touch
them and did not:

| File | Digest, before and after |
|---|---|
| `adapters/web/templates/denied.html` | `5f29922f6b48739d03874b3afb3a41953dc0bd0185b25d982800e860dd0c5305` |

`.gitkeep`'s digest is the SHA-256 of the empty string, which is the assertion
that it is a zero-byte placeholder and not an asset.

**Controlled records** updated by this package to record the submission (§11):

| File | Before | After |
|---|---|---|
| `docs/project-management/status.md` | `654c54428c2d3489955c4f5038fe130c0288057bed816a3d3b345250b1975f07` | `eede292a9f235ed639311138764c4b388a55bcea3b43f1b787879d1ad66106ad` |
| `docs/project-management/raid-register.md` | `d9181620019b9e34c673d88fb4898cf761c2a29c580575669ffc59feb62e5fc4` | `0e55edee0ac23c40acb42837121932315b57c84356c3e75a91bc80e05cf8b00a` |
| `docs/project-management/change-log.md` | `a90f0855c31adeb3485e27769aa51d5f5f6b62ce6be66a4def62b734655027b1` | `c830fda988c25e1ba7459c2797e0a06af41ab3b246b2463dab7c2a10bb15059f` |

This submission's own digest is not listed: it would change on writing the line
that carried it. Its path is
`docs/review/phase-3-d-03-backend-contract-correction-submission.md`.

---

## 4. Contract and version effects

| Contract | Effect |
|---|---|
| Route authorization | **Extended.** One mount added to a previously route-only closed set, with §1.2 defining it and the exhaustiveness claim widened to cover mounts. R-36's *Response* cell corrected to match §5.1's prose and the accepted implementation. No route path, method, caller state, matrix cell, denial code, CSRF, origin or body rule changed |
| View model | **Additive only.** `VIEW_MODEL_VERSION` remains **`vm-1`**. VM-22 added; `ConfirmScope`, `CharacterFilters` and VM-13's `csrf_token` documented from the accepted implementation. **No field removed, renamed or narrowed, and no enum narrowed** — the three conditions §1 rule 5 makes breaking |
| Operational | **Extended.** §4.4 records the static surface's deployment, configuration, backup and monitoring position; §4.1 gains a `/static/*` row stating Caddy does nothing; §4.3 records the second kill-switch exemption. No topology, service, port or signal changed |
| Threat model | **Extended by addition.** T-54 and T-55 added, continuing after the existing T-53; §2 gains the M-01 entry point; §6 gains a verification row. No existing threat, control, residual or attacker profile rewritten |
| Test traceability | **Extended by addition.** TC-STRUCT-01 amended by an addition clause; TC-SEC-14, TC-VM-06 and TC-STATIC-01…07 added; §22 maps the six items to their evidence |
| Numeric policy register | **Untouched.** The cache values are a route-contract policy, not an `N-nn` number, and were not smuggled into the register |
| Logical schema, state machines, identity migration, configuration/dependency | **Untouched by this package** |

**§1 rule 5 assessment.** The correction is additive throughout, so no new version
identifier is required and none was created. The one place where a stop-and-return
was possible — D-03-6's new view model — is additive by the same rule: a view
model is added and none is removed, renamed or narrowed. No conflict with the
accepted versioning rules arose, so nothing was returned to Peter on that ground.

---

## 5. Tests and literal results

### 5.1 What was added

| Module | Cases | Covers |
|---|---|---|
| `tests/web/test_static_asset_surface.py` | 54 | TC-STATIC-01…07 |
| `tests/web/test_d03_contract_correction.py` | 25 | D-03-2…D-03-6 |
| `tests/web/test_structural_guards.py` (added cases) | 4 | TC-STRUCT-01 mount half ×2, TC-VM-06 ×2 |
| `tests/web/test_security_controls.py` (added cases) | 3 | TC-SEC-14 |

Mapping to the handover's fourteen required proofs:

| # | Required proof | Where |
|---|---|---|
| 1 | Route-and-mount surface equals the contract; a new undeclared `Route` or `Mount` fails the guard | `test_the_registered_route_set_equals_the_contract_exactly`, `test_the_registered_mount_set_equals_the_contract_exactly`, `test_the_only_mount_is_the_static_surface`; falsified in §6 |
| 2 | `/static/` permits `GET`/`HEAD`, refuses mutation methods, serves only the approved root | TC-STATIC-01, TC-STATIC-02 |
| 3 | Traversal, encoded traversal, missing files and directories expose nothing | TC-STATIC-03 |
| 4 | Untrusted hosts refused on static requests | TC-STATIC-04 |
| 5 | Assets reachable during the kill switch while protected routes keep their behaviour | TC-STATIC-04 (both halves in one case) |
| 6 | Cache policy correct; no session/CSRF cookie set or refreshed | TC-STATIC-05, TC-STATIC-06 |
| 7 | `ConfirmScope` and `CharacterFilters` match the corrected contract exactly | `test_confirm_scope_matches_the_corrected_contract_exactly`, `test_character_filters_matches_the_corrected_contract_exactly` (field **and order** equality, parsed from the contract) |
| 8 | VM-13 carries server-rendered CSRF; R-37 still rejects missing or invalid tokens | `test_vm_13_carries_a_csrf_token_and_the_contract_now_lists_it`, `test_r_37_still_refuses_a_missing_or_invalid_csrf_token` (absent, forged, and another caller's genuine token) |
| 9 | R-36 returns `200` denied VM-13 and never redirects | `test_r_36_answers_200_with_a_denied_vm_13_and_never_redirects`, `test_the_route_contract_table_and_prose_now_agree_about_r_36` |
| 10 | Every generic denial uses `DeniedView`; the non-member page keeps VM-02 | `test_no_generic_denial_is_constructed_from_the_non_member_view` (source-level, both modules), `test_the_non_member_page_keeps_vm_02_and_its_recovery_context` |
| 11 | Denied and absent `404` bodies byte-identical, with no correlation, UUID, guild name, timestamp or object detail | `test_denied_and_absent_404_bodies_remain_byte_identical`, `test_a_denied_response_body_contains_only_the_category`, `test_the_import_surface_denies_a_member_with_the_same_bytes` |
| 12 | Direct unauthorized calls denied before object lookup | `test_an_unauthorized_call_is_denied_before_the_object_is_looked_up`; the pre-existing TC-OBJ-05 is unchanged and still green |
| 13 | Zero unsafe `\|safe`, `hx-on:`, inline script, CDN, remote font, `design-prototype/` | TC-SEC-08/10/11 (pre-existing, still green) plus **TC-SEC-14** (new: remote origins and `design-prototype/`, over the template corpus **and** the new static root) |
| 14 | The complete existing portal and bot suites remain green | §5.2 |

### 5.2 Literal command output

Every command below was run from `/opt/discord-bots/freedom-bot` after the final
edit. Exit codes are reported as observed.

```bash
$ sha256sum -c docs/review/phase-3-visual-freeze-manifest.sha256
design-prototype/assets/freedom-blades-token.png: OK
design-prototype/assets/portraits/lyra.png: OK
design-prototype/assets/portraits/thorin.png: OK
design-prototype/assets/portraits/valerius.png: OK
design-prototype/character-detail.html: OK
design-prototype/components.html: OK
design-prototype/council-approval.html: OK
design-prototype/css/styles.css: OK
design-prototype/css/tokens.css: OK
design-prototype/index.html: OK
design-prototype/js/portrait-preview.js: OK
design-prototype/login.html: OK
design-prototype/my-characters.html: OK
design-prototype/reconciliation.html: OK
# exit status 0 — 14/14
```

```bash
$ TEST_DATABASE_URL='postgresql+psycopg:///freedom_test' \
    ./venv-web/bin/python -m pytest tests/web -q
SKIPPED [54] tests/web/test_p3_2_matrix.py:155: permitted cells are asserted by the per-route success cases
SKIPPED [26] tests/web/test_p3_3_matrix.py:198: permitted cells are asserted by the per-route success cases
1524 passed, 80 skipped, 491 warnings in 98.85s (0:01:38)
# exit status 0
```

```bash
$ TEST_DATABASE_URL='postgresql+psycopg:///freedom_test' \
    ./venv/bin/python -m pytest -q
2294 passed, 1 warning in 134.09s (0:02:14)
# exit status 0
```

```bash
$ ./venv-web/bin/python -m compileall application adapters tests/web
# exit status 0
```

```bash
$ git diff --check
# no output; exit status 0
```

```bash
$ git status --short
# reported in full in §9; every pre-existing user change is preserved and the
# only additions are this package's four new paths.
```

**Both suites were run serially, never concurrently.** They share the one
disposable `freedom_test` database, and running them at the same time produces
dozens of fabricated failures.

**Skip accounting.** The 80 skips are two pre-existing parametrized cases that
skip the *permitted* matrix cells because those are asserted by the per-route
success modules instead. They are unchanged by this package and skipped for the
same documented reason as before it. **No test in this package skips.**

**Migrations.** The portal suite's `migrated_database` fixture runs Alembic
against the already-approved disposable `freedom_test` database, exactly as every
prior package's evidence did. No migration was run against any other database, no
migration was added, edited or removed by this package, and nothing was pointed at
production.

---

## 6. Falsification and restoration evidence

Two guards were falsified, as the handover requires. Each mutation was applied to
the real tree, observed to fail the guard, reverted, and the revert verified by
SHA-256 against a digest captured **before** the mutation.

### 6.1 The mount inventory guard

**Mutation.** Two lines in `adapters/web/app.py`, immediately before route
registration:

```python
from starlette.staticfiles import StaticFiles as _F  # FALSIFICATION
app.mount("/undeclared", _F(directory=str(TEMPLATE_ROOT)), name="undeclared")  # FALSIFICATION
```

**Result — the new guard fails:**

```text
FAILED tests/web/test_structural_guards.py::test_the_registered_mount_set_equals_the_contract_exactly
FAILED tests/web/test_structural_guards.py::test_the_only_mount_is_the_static_surface
2 failed, 66 deselected in 1.30s

E       AssertionError: assert 2 == 1
E        +  where 2 = len([Mount(path='/static', name='static', …),
E                          Mount(path='/undeclared', name='undeclared', …)])
```

**And the second result, which is the point of D-03-1's second half — the
pre-existing route guard passes against the same mutation:**

```bash
$ … -m pytest tests/web/test_structural_guards.py -q -k "registered_route_set"
1 passed, 67 deselected in 1.28s
```

An undeclared mount claiming a whole URL subtree — here, the entire Jinja template
directory — was invisible to the only machine check protecting the closed
inventory. That is exactly the blindness the readiness report identified, observed
rather than argued, and it is now closed.

**Restoration.**

```bash
$ grep -rn "FALSIFICATION" adapters/ application/ tests/    # → none
$ sha256sum -c PRE-MUTATION.sha256
adapters/web/app.py: OK
adapters/web/portal_routes.py: OK
```

### 6.2 The denial leakage guard

**Mutation.** The exact defect D-03-6 exists to make impossible, in three places:
a `correlation: Correlation | None = None` field added to `DeniedView`; the portal
`_denied` helper populating it with the refusal's real correlation id; and
`denied.html` printing `{{ view.correlation.id }}`.

**Result — twelve cases fail across three modules, including the pre-existing
TC-OBJ-07 case that P3.2 delivered:**

```text
FAILED tests/web/test_structural_guards.py::test_the_denial_view_cannot_carry_anything_that_would_break_byte_identity
FAILED tests/web/test_d03_contract_correction.py::test_no_generic_denial_is_constructed_from_the_non_member_view
FAILED tests/web/test_d03_contract_correction.py::test_a_denied_response_body_contains_only_the_category
FAILED tests/web/test_d03_contract_correction.py::test_denied_and_absent_404_bodies_remain_byte_identical
FAILED tests/web/test_d03_contract_correction.py::test_an_unauthorized_call_is_denied_before_the_object_is_looked_up
FAILED tests/web/test_d03_contract_correction.py::test_every_denial_category_is_representable_and_carries_nothing_else[…6 params…]
FAILED tests/web/test_p3_2_success_cells.py::test_cross_character_substitution_is_indistinguishable_from_absence
12 failed, 129 passed, 67 warnings in 5.81s
```

**Honestly reported gap in this mutation.** `test_the_import_surface_denies_a_member_with_the_same_bytes`
did **not** fail, because the mutation was applied only to `portal_routes.py`'s
`_denied` and not to `import_routes.py`'s. That is a limit of the mutation, not of
the test: the two helpers are independent, and the source-level case
(`test_no_generic_denial_is_constructed_from_the_non_member_view`) checks **both**
modules and did fail.

**Restoration.**

```bash
$ grep -rn "FALSIFICATION" adapters/ application/ tests/    # → none
$ sha256sum -c PRE-MUTATION.sha256 PRE-MUTATION-2.sha256
adapters/web/app.py: OK
adapters/web/portal_routes.py: OK
adapters/web/templates/denied.html: OK
application/web/view_models.py: OK
```

### 6.3 The traversal guard, proved load-bearing rather than decorative

Not required, but recorded because a layered control deserves evidence that each
layer does something.

```text
route '/../templates/base.html'   normpath -> '../templates/base.html'   grammar=False  starlette_lookup -> '' exists=False
route '/../composition.py'        normpath -> '../composition.py'        grammar=False  starlette_lookup -> '' exists=False
route '/.gitkeep'                 normpath -> '.gitkeep'                 grammar=False  starlette_lookup -> '/opt/discord-bots/freedom-bot/adapters/web/static/.gitkeep' exists=True
target exists on disk: True
```

Two readings. The traversal rows are refused **twice**, independently — by the
grammar and by Starlette's `realpath`/`commonpath` containment — against a target
that genuinely exists on disk, so the `404` is a refusal and not an absence. The
`.gitkeep` row is refused **only** by the grammar: Starlette's own check resolves
it happily inside the root. The grammar is therefore a real control, and dotfiles
are unreachable because of it.

Separately, the six traversal encodings used by TC-STATIC-03 were checked against
a recording ASGI application to establish which ones actually reach the
application rather than being normalised away by the client. Five arrive as
`/static/../templates/base.html`; the plain unencoded form is normalised by httpx
into `/templates/base.html` before it is sent. That is recorded in the test's own
comment so the case is not read as stronger than it is.

**No mutation remains in the tree.** Every `FALSIFICATION` marker is gone, all six
touched files verify against their pre-mutation digests, and the full suites in
§5.2 were run **after** restoration.

---

## 7. Security analysis

### 7.1 Static serving

The static surface is the first deliberately public URL surface in Phase 3.
Everything else in the closed inventory refuses somebody, so what makes this one
safe is not an authorization chain but a small set of structural properties.

| Concern | Analysis |
|---|---|
| **Path traversal** | Four layers, and the first two are independent: a URL grammar refusing any segment that does not begin alphanumeric, checked before the filesystem is touched; Starlette's `os.path.realpath` + `os.path.commonpath` containment against the one root; `follow_symlink=False` (the default), so a symlink planted in the root cannot escape it; and a root that is **not configurable**, so there is no operator-supplied path to point elsewhere. Evidence in §6.3 and TC-STATIC-02/03 |
| **Directory disclosure** | `html=False`: a directory request is `404` with no listing and no implicit `index.html`. `/static` (bare) redirects to `/static/`, which is `404` |
| **Dotfile disclosure** | Refused by grammar. Proved load-bearing (§6.3): Starlette alone would serve `.gitkeep` |
| **Error disclosure** | A missing file, a grammar violation, a traversal attempt and a directory all produce the **same** safe `404` with no exception text, filesystem path, stack frame or requested filename. A grammar refusal is byte-identical to a missing file, so the grammar is not enumerable |
| **Method surface** | `GET`/`HEAD` only. `405` is returned identically for present and absent paths, so a mutation method cannot be used as a one-request-at-a-time directory listing |
| **Host confusion** | The mount is registered **inside** `HostGuard`, so N-01 applies to an asset exactly as to a page — including while the kill switch is engaged, which is asserted |
| **CSP** | N-26 is **unweakened**. The whole point of this surface is that CSS, script and images can be `'self'`. TC-SEC-14 asserts that no template and no file in the root references a remote origin, a CDN, a Google Font or an `@import url(...)` |
| **Session interaction** | The mount reaches no handler that issues a cookie, so no session, login-transaction or CSRF cookie is set or refreshed. Asserted **with** a cookie presented, which is the case that would catch an asset fetch silently extending an N-06 idle timeout |
| **Caching** | Decided by the filename's fingerprint, never by who is asking. A shared cache therefore never holds a caller-varying body under a cacheable header — the mistake that scoping `no-store` away would otherwise invite. `no-store` remains on every `/v1/*` and every authenticated response |
| **Kill switch** | The exemption is a named closed rule admitting two prefixes. The static mount reads no database, opens no transaction and reaches no application service, so nothing the switch exists to stop is reachable through it. Asserted together with every `/v1/*` route still answering `503` |
| **Availability** | Asset requests occupy `freedom-web` workers, stated as an accepted trade in operational contract §4.4. On a single-guild co-located host this is not the measured constraint; the measured one is the artifact parse, already on a separate worker |

Recorded as **T-54** and **T-55** in the threat model.

### 7.2 Denial non-enumeration

The `404` for an unreachable object and the `404` for an absent one must be
byte-identical (route contract §2.3, TC-OBJ-07). Before this correction that held
because `denied.html` declined to print three fields it was handed. It now holds
because there is nothing to print.

- **The type is the control.** `DeniedView` has `state` and `reason` and no other
  field. TC-VM-06 asserts **equality**, not containment — an added field is the
  defect, and the failure message says so, because the next person to hit it will
  be adding one for a plausible reason.
- **The vocabulary stays closed.** `DenialCategory`'s six members are asserted
  exactly. A closed view model carrying an open reason would leak precisely what
  the two fields were narrowed to prevent.
- **Both surfaces.** The source-level case reads both `_denied` helpers and fails
  if either constructs a `NonMemberView` or passes `correlation=`,
  `guild_display_name=` or `checked_at=`.
- **The response is asserted, not only the type.** The denied body is checked for
  the object's UUID, the character's display name, the nil UUID, **any** UUID of
  any shape, and any ISO-8601 timestamp — so a leak nobody predicted still fails.
- **Status behaviour is unweakened.** `401`, `403` and `404` are unchanged; the
  full matrix suites (`test_p3_2_matrix.py`, `test_p3_3_matrix.py`) are green.
- **Authorization still precedes lookup.** A real character id and an invented one
  produce identical status **and** identical bytes for a caller without Council
  capability, which is only possible if the refusal happened before the row was
  read.
- **The permitted exception is preserved.** `non_member.html` keeps VM-02 with its
  guild name, check time and correlation id. That page is *meant* to be
  distinguishable from "not signed in", and narrowing it would have been a
  regression dressed as consistency. Asserted positively: the test requires a
  correlation id to be present there.

### 7.3 What the record corrections could have gone wrong and did not

D-03-4 is a correction to a **claim**. The risk in "record the CSRF field
properly" is quietly relaxing the check it feeds, so R-37 is re-proved to refuse a
missing token, a forged token, and another caller's genuine token. The risk in
correcting a false provenance statement is editing the accepted P3.2 submission
until the statement becomes true, so a test asserts that `csrf_token` is **still
absent** from `docs/review/phase-3-p3-2-submission.md`. The correction was made by
retracting the claim, not by manufacturing its support.

---

## 8. Checks not run, and why

| Check | Status | Why |
|---|---|---|
| Browser, real-device, screen-reader evidence | **Not run, not claimed** | No browser is installed and installing one requires Peter's explicit authorization. TC-UI-01…09 are untouched; TC-UI-08 and TC-UI-09 remain Peter-only and are not schedulable by this package |
| Staging evidence (TC-OPS-01…05, TC-LIM-02, TC-PERF-01…03, TC-SEC-07 browser half) | **Not run** | Staging does not exist; I-06 is open |
| Deployment, live services, network calls | **Not run** | Forbidden by the handover and unnecessary. No Discord, Google, Foundry or production PostgreSQL contact; no `.env`, credential or secret file read |
| Package installation | **None** | No dependency added, removed or upgraded. `requirements-web.txt` and `requirements-web.lock` are untouched — the static mount uses Starlette's `StaticFiles`, which FastAPI already vendors |
| Formatter / linter / type checker | **Not run** | The repository configures none for this package; `compileall` is the configured mechanical check and was run (exit 0). Reported as a gap rather than implied to have passed |
| `alembic check` / migration tests | **Run as part of the two suites**, unchanged | This package adds no migration and touches no schema |
| TC-UI-06 | **Not delivered** | TC-SEC-14 asserts the backend half — the current corpus and the new static root. The delivery-plan row belongs to P3.4 and to a production corpus that does not exist. Recorded in traceability §22.1 |
| The pre-existing stash | **Not inspected, not applied, not modified** | `stash@{0}: On main: temp before rebase` is untouched and still present |

---

## 9. Working tree

`git status --short` before and after this package differs by exactly four new
paths and the modification of files listed in §2. Every pre-existing user change
— the uncommitted P3.3 work, the worker package, the new migrations, the modified
`.env.example`, `repositories.py`, `config.py`, `startup.py` and the rest — is
**preserved**. Nothing was committed, pushed, stashed or reverted.

New paths added by this package:

```text
?? adapters/web/static/
?? adapters/web/static_assets.py
?? tests/web/test_static_asset_surface.py
?? tests/web/test_d03_contract_correction.py
?? docs/review/phase-3-d-03-backend-contract-correction-submission.md
```

Overlap analysis: `application/web/view_models.py`, `adapters/web/app.py`,
`adapters/web/portal_routes.py`, `adapters/web/middleware.py`,
`adapters/web/composition.py`, `tests/web/test_structural_guards.py`,
`tests/web/test_security_controls.py` and five contract documents already carried
uncommitted user changes before this package began. Each edit here is a distinct
region — a new constant, a new class, a new section, a replaced helper body — and
none overwrites or reverts pre-existing work. The before/after digests in §3 are
taken against the **working tree as found**, not against `HEAD`, precisely so this
package's effect can be separated from what was already there.

The prototype freeze is **14/14**, verified before and after (§5.2).

---

## 10. Residual risks

| # | Risk | Assessment |
|---|---|---|
| 1 | **The static root is empty, so every asset-shaped rule is unexercised against a real asset.** The cache policy, the CSP interaction and the same-origin guard are proved against probe files this package writes and removes | Accepted and deliberate: filling the root is P3.4's work and this package is forbidden to add visual assets. TC-SEC-14 and TC-STATIC-07 will hold against the real corpus when it lands, and P3.4 must re-run them |
| 2 | **Serving assets from `freedom-web` occupies application workers.** No measurement supports the judgement that this is acceptable | Stated as a design trade in operational contract §4.4, not as a measurement. The alternative — a Caddy `file_server` — was rejected for a header-authority reason, not a performance one, and revisiting it is a deployment-gate decision with real traffic in view |
| 3 | **`.gitkeep` is a placeholder in a contract surface.** A future contributor could read the directory as a scratch space | Bounded three ways: the grammar makes dotfiles unreachable, TC-STATIC-07 asserts the root holds only `.gitkeep`, and TC-SEC-14 scans the root for remote origins |
| 4 | **Containment beyond the grammar is Starlette's.** The second traversal layer is third-party code | Stated in T-54's residual column rather than implied to be ours. Both layers are asserted independently (§6.3), and the grammar alone refuses every traversal form tested |
| 5 | **TC-SEC-14's remote-origin check is substring-based.** An obfuscated remote reference could pass | Accepted: a template has no legitimate reason to contain any of the markers, so a coarse check has no false positives to trade against, and P3.4's review is the second line |
| 6 | **The mount inventory is asserted by count as well as by set.** A legitimate second mount will fail a test | Deliberate. Widening the application's URL surface should be a visible, deliberate edit to a test rather than a silent addition |
| 7 | **`ConfirmScope` and `CharacterFilters` are documented from the implementation.** If the implementation was wrong, the contract now records the wrong shape | This is the accepted disposition — `C-P3.4-A` authorizes documenting the *implemented* shape "without renaming, removing or inventing fields". Both shapes were reviewed and accepted at P3.G2/P3.G3 as part of their packages. Flagged for the independent review as the one place where "matches the implementation" is the weaker of the two possible claims |
| 8 | **RR-17, RR-18, RR-19, RR-24 unchanged.** No existing residual is closed, reduced or re-argued by this package | — |

---

## 11. Controlled-record updates made by this package

| Record | Change |
|---|---|
| `docs/project-management/status.md` | Records the correction submission and that both reviews are pending |
| `docs/project-management/raid-register.md` | D-03 amended by addition: implementation delivered, reviews pending, D-03 still **partly closed**, Gemini still blocked |
| `docs/project-management/change-log.md` | New entry `C-P3.4-B` recording the correction submission. **Not marked accepted** |

**Not done, deliberately:** no review is marked complete; nothing is
self-accepted; D-03 is not closed; P3.G4 is not closed; the Gemini prompt is not
marked released; no historical gate record is rewritten.

---

## 12. Review requests

### 12.1 Independent Codex implementation review — requested

Please review this package as an implementation against the accepted decisions in
`C-P3.4-A`, independently of its author. Suggested focus:

1. **Is the mount inventory guard actually closed?** `MOUNT_INVENTORY`, route
   contract §1.2's table, `parsed_contract_mounts()` and the two cases — is there
   a shape of registered sub-application that still evades all of them?
2. **Is the URL grammar right?** Segment rule, the `404`-not-`400` choice, the
   ordering of the grammar check against Starlette's own containment, and the
   interaction with `get_path`'s normalisation.
3. **Is the cache policy's fingerprint grammar sound**, and is the conservative
   default the right way round?
4. **Is `DeniedView`'s carrier swap complete?** Every generic denial boundary on
   both route modules, with VM-02 correctly retained for the non-member page.
5. **Do the recorded shapes match the implementation exactly** for `ConfirmScope`,
   `CharacterFilters` and VM-13 — including field order, defaults and optionality?
6. **Are the contract edits additive as claimed**, with `vm-1` genuinely intact
   and no identifier reused? (T-54/T-55 and TC-SEC-14 were both renumbered during
   this package after collisions were found; please re-check for others.)
7. **Is the evidence honestly classified** in §5.2, §6 and §8 — in particular the
   declared gap in the §6.2 mutation and the normalisation note in §6.3?

### 12.2 Distinct security-focused review — requested

Please review this package as a security change, in a **separate** pass. Suggested
focus:

1. **The static surface as a new public attack surface.** Traversal, encoded
   traversal, symlinks, dotfiles, directory disclosure, error disclosure, method
   surface, and anything the four layers in §7.1 do not cover.
2. **Cache correctness.** Is scoping `/static/` out of `no-store` safe under every
   caller state, and is there any path by which a caller-varying body could be
   served under the immutable header?
3. **The kill-switch exemption.** Is it genuinely narrow, and is there any way to
   reach an application service, a database read or a session through it?
4. **Denial non-enumeration under the new carrier.** Is byte-identity preserved
   across every denial category, both route surfaces, and every status code — and
   is there any remaining path by which a correlation id, timestamp or object
   detail could reach a denial body?
5. **CSP.** Is N-26 genuinely unweakened, and does anything in this package make a
   future weakening easier or more likely?
6. **Whether the record corrections weakened anything**, especially R-37's CSRF
   verification and R-36's refusal.

---

## 13. The decision Peter must make after both reviews pass

> **Accept the corrected D-03 backend route/view-model contract, and explicitly
> release `docs/review/phase-3-p3-4-gemini-implementation-prompt.md`.**

That single decision is what unblocks Gemini's P3.4 production frontend
integration. It does **not** close P3.G4, and it authorizes no staging exposure,
deployment, production use, live-service contact or real-player-data use — I-06
and A-05 remain open and continue to prohibit public exposure.

Until Peter records that decision:

- **D-03 remains open** (partly closed: visual half accepted 2026-08-13, backend
  half corrected and under review);
- **Gemini may not change a production frontend file**; and
- **the implementation prompt remains held.**

**This package stops here.** No P3.4 frontend implementation has begun, no
production template, CSS, HTMX file, image or visual asset has been created or
modified, and no review has been marked complete.
