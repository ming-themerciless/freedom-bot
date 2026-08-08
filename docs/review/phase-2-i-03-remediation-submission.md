# Phase 2 I-03 — remediation submission

Implementer: Claude, implementing agent and working Technical Lead
Date: 2026-08-04
Repository: `/opt/discord-bots/freedom-bot`
Branch: `docs/platform-plan`, `HEAD` at `c8a3da9`, package in the uncommitted
working tree
Remediates: [`phase-2-i-03-codex-review.md`](phase-2-i-03-codex-review.md) (B-1,
I-1, I-2) and
[`phase-2-i-03-codex-security-review.md`](phase-2-i-03-codex-security-review.md)
(S-B-1, S-B-2, S-I-1)

**This is an implementer's submission, not an approval.** No finding is closed
on my authority. It requests the separate Codex implementation re-review and
security re-review named in §11, and it claims no phase gate.

**Amended 2026-08-04 after a second independent re-review**, which found two
findings still open. §§1, 3.3, 3.5 and 12 record what the first attempt got
wrong and what the second one does instead. Nothing in the original text has
been deleted: the difference between the two attempts is the most useful thing
in this document.

**Amended again 2026-08-05 after a third independent re-review.** That review
found the root anchoring in §12.2 materially correct and returned one Blocking
finding and two Important ones: publication could still overwrite an entry it had
never validated, the conservative default in the failure vocabulary made a claim
that defect invalidated, and the submitted test evidence was not reproducible on
the review host. **§13 is the third remediation.** §1 and §6 are corrected;
§§3.3, 3.5, 12 and their figures are left as the historical record of what was
believed at the time. The same rule applies as before — the superseded attempts
are not rewritten, because the sequence of what was missed is itself evidence
about what to check now.

## 1. Finding-by-finding disposition

| # | Finding | Disposition | Where |
|---|---|---|---|
| B-1 / S-I-1 | Browser CORS preflight unanswered, so the supported workflow could not reach the POST | **Remediated by construction and test; not yet observed from a browser** | `adapters/http/cors.py` (new), `adapters/http/wsgi.py`; 41 CORS/preflight/origin tests in `tests/test_http_submission.py` |
| S-B-1 | Reusable bearer in client-readable Foundry world configuration | **Remediated — the credential is no longer in any Foundry state** | `foundry-module/scripts/settings.js`, `main.js`, `transport.js`; `foundry-module/tests/settings.test.mjs` (new) |
| S-B-2 | Existing artifact roots and files accepted without enforcing confidentiality | ~~Remediated~~ ~~reopened, then re-remediated~~ **root anchoring found materially correct by the third re-review; a further Blocking defect was found in publication itself — see §13** | `adapters/artifacts/filesystem.py`, `adapters/http/composition.py`; storage-policy, anchoring, lifecycle and durability tests in `tests/test_artifact_store.py` and `tests/test_submission_composition.py` |
| I-1 | False "nothing was stored" claims | ~~Remediated~~ ~~reopened, then re-remediated~~ **reopened a second time: the conservative default still claimed nothing already held had changed. Corrected in §13, with behaviour tests tied to filesystem state rather than a phrase scan** | `application/artifacts.py`, `application/foundry/submission.py`, `application/errors.py`, `adapters/http/wsgi.py`, `foundry-module/scripts/main.js`, operations §5.6/§5.7/§9; `tests/test_storage_claim_vocabulary.py` |
| I-2 | Directory durability failures suppressed | **Remediated — typed failure, no commit, target preserved, retry completes it**; preserved through the S-B-2 re-remediation and re-asserted | `adapters/artifacts/filesystem.py`, `application/foundry/submission.py`; tests in both suites |

**Two findings were added by the third re-review** and are dispositioned in §13:

| # | Finding | Disposition | Where |
|---|---|---|---|
| Blocking — publication | `os.replace` could remove and overwrite a checksum entry that appeared after the presence check and was never validated | **Re-remediated: publication is `link(2)`, which creates or fails `EEXIST` and never removes an existing entry** | `adapters/artifacts/filesystem.py`; the publication-race group in `tests/test_artifact_store.py` |
| Important — test evidence | 32 storage tests failed at the startup ancestor gate on the review host, so the submitted counts were not independently reproducible | **Re-remediated: the ancestor rule is an injectable policy; the production walk is separately exercised unbounded** | `adapters/artifacts/filesystem.py`, `adapters/http/composition.py`, `tests/test_artifact_store.py`, `tests/test_submission_composition.py` |

Residuals that are **not** closed, and are stated as such throughout: B-1's real
browser observation (§8 R7, §9), S-B-1's real second-client observation, S-B-2's
cross-account observation (§12), and the publication residuals in §13.4. No
finding is closed here.

## 2. What was found about Foundry, before anything was changed

S-B-1 required the actual Foundry 14.365 behaviour to be established from
permitted application source rather than assumed. It was, on this host, and it
is decisive.

| Question | Answer | Source |
|---|---|---|
| Who may create or update a Setting? | a user holding `SETTINGS_MODIFY`; enforced server-side | `common/documents/setting.mjs` — `BaseSetting.canUserCreate`, `#canModify` |
| Which clients receive a world-scoped Setting's **value**? | **every connecting client, whatever its role** | `dist/packages/world.mjs` — the per-user world payload is built with `db.Setting.dump().then(e => f.settings = e)` |
| Does that dump filter by user or permission? | **No.** Its whole signature is `static async dump({sort})` | `dist/database/backend/server-document.mjs` |
| Does the client filter? | No. `game.settings.storage.get("world")` **is** the delivered collection; `getSetting(key, user)` is an in-memory `find` over it | `client/game.mjs:67`, `client/documents/collections/world-settings.mjs` |
| Is there a supported option giving read confidentiality? | **No.** `SETTING_SCOPES` is `client` (browser `localStorage`), `world` and `user`; `world` and `user` are both Setting documents vended by that same unfiltered dump | `common/constants.mjs`, `client/helpers/client-settings.mjs` |

So the reviewer's reading is confirmed and is stronger than "not necessarily":
`config: false` affects the settings *form* only, `SETTINGS_MODIFY` is a
**write** control, and no setting option in this Foundry generation is a read
boundary. The conclusion drives §3.2 — the fix cannot be a different setting.

Recorded permanently in `foundry-module/scripts/settings.js`, the module README
and operations §4.1, so the next person does not have to re-derive it.

## 3. What changed, and why

### 3.1 B-1 / S-I-1 — a bounded, allowlisted CORS policy

**New: `adapters/http/cors.py`.** Transport policy, owning one decision —
whether this exact origin may have the browser make this exact request.

- **Explicit allowlist of exact origins** from `FREEDOM_SNAPSHOT_ALLOWED_ORIGINS`.
  No wildcard, no reflection, no suffix or pattern matching. `*` and `null` are
  refused *by configuration validation*, so they cannot be typed in by accident.
- **Validated at startup.** Scheme and host only; no path, query, fragment or
  userinfo; HTTP only for a loopback host, the same narrow exception
  `transport.js` already makes. Configuration is normalised to the exact form a
  browser sends, so the request-time comparison is a plain string equality with
  nothing clever in it.
- **Empty is the default and is closed.** No browser origin may submit. A
  request with no `Origin` — `curl`, the smoke test, the loopback rehearsal — is
  untouched, which is how the non-browser path stays usable without weakening
  the browser policy.
- **`OPTIONS` answered only for the submission route**, only for `POST`, only
  for exactly the four headers `transport.js` sends. A fifth header, another
  method, or an unlisted origin is `403` with **no** permission header.
- **No authentication on the preflight**, because a browser does not present the
  credential there — it is one of the headers being asked about. The preflight
  reaches no application service and records nothing.
- **`credentials: "omit"` preserved; `Access-Control-Allow-Credentials` never
  emitted.** No cookie authority is added to this endpoint.
- **Permission on every actual response**, including `401`, `400` and the
  unexpected `500` — computed in `__call__` before routing, so the exception
  path carries it too. A response the browser may not read reaches the module as
  an opaque network failure, which would make "your credential is wrong" and
  "the server is down" the same event.
- **`Vary: Origin, Authorization` on every submission response**, whether or not
  permission was granted, so a shared cache cannot serve one origin the
  header-less answer stored for another. Preflights additionally vary on the two
  `Access-Control-Request-*` headers.

`adapters/http/wsgi.py` gained a small `_Response` type so a body-less `204` is
expressible; a `204` carries no `Content-Type`, which `wsgiref.validate` also
requires. The preview route is deliberately given **no** preflight: it is inert
until Phase 3, and a second CORS surface is that phase's decision.

`ADR 0009` records this as a clarification, not a new route: a preflight is the
same route's own contract, required by the browser before the POST the ADR
already authorizes. It adds no resource, capability or caller, and the stdlib
WSGI decision is untouched.

### 3.2 S-B-1 — the credential leaves Foundry entirely

Given §2, no setting is a safe place, so the credential is not configuration at
all.

- **`submissionCredential` is deleted.** `settings.js` registers four settings,
  none secret-shaped; `readSettings` no longer returns a credential.
- **The submitting GM enters it in the dialog**, once per submission, in a
  `type="password"`, `autocomplete="off"` field. It lives in one local variable
  for the duration of one upload; `run()` clears it in a `finally`, and
  `openSubmissionDialog` clears the callback's copy in its own.
- **It is written nowhere**: no setting, no `localStorage`, no flag, no
  document, no notification, no log, no receipt. `transport.js` already took it
  as a parameter and still does.
- **The download fallback needs no credential** and is passed none.

The confidentiality properties, in the terms the review asked for:

| Property | Value |
|---|---|
| Narrowly scoped, revocable, submit-only principal | preserved unchanged — same `ServicePrincipal`, same single `foundry:snapshot:submit` scope, same reload-based revocation |
| No administrator or database credential; no apply or read power added | unchanged; nothing was added to the principal |
| Where the secret lives | the holder's password manager; the server holds a **SHA-256 digest** only |
| Who can retrieve it | the person who holds it. No Foundry user, module or client can read it out of world state, because it is not there |
| Lifetime | one submission in the browser; indefinite in the password manager until rotated |
| Rotation / revocation | server configuration plus reload, and telling the holder. **No longer touches Foundry at all** — there is no setting to update, which is also what makes revocation complete |
| Browser or GM-device compromise | treat as exposed and rotate. Authority is submit-only: unwanted **pending** artifacts and consumed storage; no apply, no Council data, no character mutation, no PostgreSQL |
| Fails closed when unavailable | `missing_credential`, raised before any request is made |
| Still operable | yes — paste from a password manager into the dialog. Submission is a deliberate, occasional GM action |

**Rotation implication.** Any credential ever placed in a world setting must be
treated as exposed and rotated, because it was delivered to every client that
joined while it was set. **None has been**: §5.2 of the operations document has
never been run outside synthetic tests, no credential has been issued, and the
module has never been installed. There is nothing outstanding to rotate today;
the rule is documented and applies from the first credential issued.

**Regression guard.** `foundry-module/tests/settings.test.mjs` fails if any
secret-shaped setting is registered, if `readSettings` returns a credential, if
the settings a client is vended contain one, or if any module source reaches
`settings.register`/`settings.set` with a secret-shaped key, `localStorage`,
`sessionStorage` or `setFlag`. It models Foundry's delivery honestly — whatever
is in the world store is readable by every client — so reading it "as an
ordinary player" reads exactly what a real one would receive.

### 3.3 S-B-2 — restricted storage enforced rather than asserted

`adapters/artifacts/filesystem.py`, with the policy written down in its
docstring:

| Subject | Required | Refusal |
|---|---|---|
| the configured path | no symbolic-link component (`normpath` vs `realpath`) | `ValueError` at construction → `ConfigurationError` at startup |
| the root | directory, `lstat` so a symlink is caught not followed | `root_not_a_directory` |
| the root | owned by the effective uid | `root_not_owned` |
| the root | no bit granted to group or other | `root_permissive` |
| an artifact read, written or reused | opened `O_NOFOLLOW`, regular file | `artifact_untrusted`, `artifact_not_a_regular_file` |
| an artifact | owned by the effective uid | `artifact_not_owned` |
| an artifact | no bit granted to group or other | `artifact_permissive` |
| an artifact | hashes to its own name | `checksum_mismatch` |

- **Startup and per-store.** `ensure_ready()` is called from the composition
  root, so a bad deployment fails startup in front of an operator rather than
  during the first upload of every active character's mechanics. `store()`
  re-checks the root, because a mode can change while the process runs and only
  the second check is in front of a write.
- **Time-of-check to time-of-use.** Artifact checks are made against a *file
  descriptor*: `os.open(..., O_NOFOLLOW)`, then `os.fstat` and a read from that
  same descriptor. The file whose type, owner and mode were checked is exactly
  the file whose bytes were hashed.
- **Refusal, not repair.** Nothing `chmod`s or `chown`s a path the operator
  configured. Operations §5.6 assigns the repair to the operator and gives the
  commands. If that should ever become this process's job, it is a documented
  policy change, not a code decision.
- **Failures name a fixed reason and never a path**, with the cause dropped so
  no `OSError` renders one into a traceback.

**One defect was found by these tests and fixed.** `_path_for` called
`.resolve()`, so a checksum-named **symlink** was resolved and the store then
operated on the link's target — `O_NOFOLLOW` never saw it. The name is a
validated hex digest plus a fixed suffix and is contained by construction, so
resolving bought nothing and cost the symlink refusal. It no longer resolves.

> **Superseded in part — see §12.2.** Every rule in this section still holds and
> is still enforced. What it got wrong is *how*: each check named the configured
> **path**, and so did every later create, open, publication and directory
> `fsync`. That is a check-then-use race, not a control. The root is now an
> anchored directory descriptor.

### 3.4 I-2 — durability is acknowledged or the submission fails

`_fsync_directory()` raised nothing; it now raises
`ArtifactStorageError("durability_unconfirmed")` on a directory-open or
directory-`fsync` failure.

- **No database success can commit.** The store is called inside the unit of
  work before any row is added, so the raise leaves the `with` block without
  committing: no snapshot row, no idempotency receipt, no accepted audit event.
  Asserted directly in `tests/test_snapshot_submission.py`.
- **The published target is not destroyed.** By the time directory sync runs the
  rename has happened and the bytes are correct. The failure path's cleanup only
  ever names the *temporary* file, which no longer exists. Asserted.
- **A retry completes the guarantee.** The already-held branch now `fsync`s the
  directory too, so the retry establishes the durability the first attempt could
  not. Content addressing is what makes it a retry rather than a second
  submission. Asserted, including that the directory is actually synced.
- **A filesystem that cannot support it fails startup.** `ensure_ready()` proves
  directory `fsync` works before the first request, so the narrower guarantee is
  never silently reported as success.

### 3.5 I-1 — every response says only what it knows

| Where | Was | Is |
|---|---|---|
| `wsgi.py` 500 | "Nothing was stored." | "No submission was recorded or confirmed. Retrying with the same Idempotency-Key is safe." |
| `wsgi.py` 503 `database_unavailable` | "could not be recorded and nothing was stored" | "could not be recorded or confirmed. Retry with the same Idempotency-Key: a retry cannot create a second snapshot." |
| `submission.py` `storage_unavailable` | "could not be stored, so nothing was recorded" | "could not be **confirmed as** stored, so nothing was recorded … Retrying with the same request key is safe." |
| `SubmissionRefused` docstring | "Nothing was stored and nothing was recorded" | states which paths can leave bytes, and why the caller is told about recording instead |
| audit payload key | `stored: false` | `recorded: false` — a refusal establishes that nothing was recorded, not that no bytes exist |
| `main.js` failure notice | "Nothing was confirmed." | "Nothing was recorded or confirmed." |
| operations §5.7 | "nothing was stored; retry the same key" | "**nothing was recorded or confirmed**; retry the same key", with a paragraph on why |
| operations §9 | "It stored nothing…" | per-path: which refusals wrote no bytes, and what `durability_unconfirmed` means |

The bounded, no-sensitive-data response policy is unchanged: same closed
vocabulary, same absence of exception text, SQL, paths, artifact bytes and Actor
values.

**Orphan identification** is operations §5.6: a read-only `comm` of the store's
filenames against `SELECT checksum FROM foundry_snapshots`. It states that
nothing deletes them automatically, that this must not become a cron job, that
an unclaimed artifact is evidence of a failure worth understanding, and that a
submission about to be retried needs exactly that file. **No artifact listing or
deletion HTTP route was added**, and the store still has no `list` or `delete`.
The retention decision for unclaimed artifacts is reserved to Peter (§9).

The `stored` → `recorded` rename touches an append-only audit payload. No row
has ever carried the old key: the action is new in this uncommitted package and
has never been written to a real database, so this is not a history rewrite.

> **Superseded in part — see §12.1.** The table above is accurate about the
> messages it lists. It is the word *every* in this section's heading that was
> wrong: the equivalent claims elsewhere in `submission.py` and in
> `application/artifacts.py` were not found, because the search was for the
> messages the review had named rather than for the claim.

## 4. Every changed file

**New.**

| File | Why |
|---|---|
| `adapters/http/cors.py` | the allowlist, the preflight decision and the `Vary` policy (B-1, S-I-1) |
| `foundry-module/tests/settings.test.mjs` | the credential confidentiality boundary and its regression guard (S-B-1) |
| `docs/review/phase-2-i-03-remediation-submission.md` | this record |
| `docs/review/phase-2-i-03-remediation-review-request.md` | the re-review request |

**Changed.**

| File | Why |
|---|---|
| `adapters/artifacts/filesystem.py` | the storage policy, `O_NOFOLLOW` descriptor checks, `ensure_ready()`, the durability raise, and the `_path_for` symlink fix (S-B-2, I-2) |
| `adapters/http/wsgi.py` | preflight routing, per-response CORS and `Vary`, `_Response`, truthful failure messages (B-1, S-I-1, I-1) |
| `adapters/http/composition.py` | build and validate the CORS policy; call `ensure_ready()`; surface both as startup `ConfigurationError` |
| `application/foundry/submission.py` | truthful `storage_unavailable` and docstring; `recorded` audit key; why the raise prevents a commit (I-1, I-2) |
| `application/foundry/audit_policy.py` | `stored` → `recorded`, with the classification argument for it (I-1) |
| `tools/snapshot_api.py` | report configured origins; document the new variable |
| `.env.example` | `FREEDOM_SNAPSHOT_ALLOWED_ORIGINS`; the enforced storage state; the credential is not a Foundry setting |
| `foundry-module/scripts/settings.js` | credential setting removed; the Foundry source findings recorded (S-B-1) |
| `foundry-module/scripts/main.js` | credential field, per-submission lifetime and clearing; truthful failure notice (S-B-1, I-1) |
| `foundry-module/scripts/transport.js` | `missing_credential` message; the CORS and credential-parameter contracts |
| `foundry-module/styles/freedom-blades-export.css` | style for the credential note |
| `foundry-module/README.md` | the credential workflow and why there is no setting |
| `docs/operations/foundry-snapshot-submission.md` | §1, §3, §4, §4.1 (new), §5.1, §5.2, §5.3, §5.4 (new preflight section), §5.5, §5.6 (enforced state + orphan procedure), §5.7, §5.8, §8, §8.1 and §8.2 (new supervised checks), §9 |
| `docs/operations/topology.md` | origin allowlist and the Caddy CORS requirement |
| `docs/adr/0009-snapshot-submission-http-boundary.md` | clarification: the preflight is this route's contract, not a second route |
| `docs/review/phase-2-i-03-package-plan.md` | amendment §7: D2, D5, R1, R2 amended; D8 and R7 added |
| `docs/project-management/change-log.md`, `status.md`, `raid-register.md` | the remediation, its state and R7 |
| `tests/test_http_submission.py` | the CORS/preflight/origin group (41 collected), a real-socket exercise, truthful-response tests |
| `tests/test_artifact_store.py` | the storage-policy and durability group (26 collected) |
| `tests/test_snapshot_submission.py` | three durability tests: no commit, truthful message, safe retry |
| `tests/test_submission_database.py` | the renamed audit key |

**Changed again by the third remediation (2026-08-05).** No file is new.

| File | Why |
|---|---|
| `adapters/artifacts/filesystem.py` | publication by `os.link` with full revalidation of a concurrent winner; `TrustedAncestors` extracted as an injectable policy; `_discard` refuses any name without the temporary prefix; the `link_unsupported` startup probe; `PRESERVED` threaded through `_read_trusted`/`_require_trusted_artifact`; the "Publication never overwrites" docstring section |
| `application/artifacts.py` | `StorageOutcome.PRESERVED` added; `UNRESOLVED` no longer claims anything about durable state; the module docstring records the rule a default sentence must satisfy |
| `adapters/http/composition.py` | the `ancestors` keyword — a test seam with no environment variable, documented as such |
| `.env.example` | the hard-link requirement and `link_unsupported` |
| `docs/operations/foundry-snapshot-submission.md` | §5.6 "Publication never overwrites an entry the service has not validated" and "How the ancestor rule is tested, and what that costs"; the refusal table gains `link_unsupported` and `publication_unsettled`; §5.7 replaces one paragraph with the three-outcome mapping; §9 gains "An unexpected entry under a checksum name" |
| `tests/test_artifact_store.py` | the publication-race group; the ancestor rule tested directly; the bounded-walk fixtures; the `os.replace` injection points became `os.link` ones; 63 → 91 |
| `tests/test_submission_composition.py` | bounded ancestors, plus the assertion that configuration alone produces the unbounded production walk; 3 → 4 |
| `tests/test_http_submission.py` | one docstring that named `os.replace` |
| `docs/review/phase-2-i-03-package-plan.md` | amendment §9: D5, R1, R8 corrected; D10, R9 and R10 added |
| `docs/project-management/change-log.md`, `status.md`, `raid-register.md` | C-6; the third re-review's findings; R-16 and R-17 |

## 5. Architecture and security decisions, and who accepted them

| Decision | Inside whose authority | Basis |
|---|---|---|
| A bounded, allowlisted CORS preflight on the existing route | implementer, inside the accepted boundary | It is the same route's contract, required by the browser before the POST ADR 0009 already accepted. No new route, capability, caller or dependency; stdlib WSGI preserved. Recorded as an ADR clarification under plan §0.2 |
| The credential is entered per submission instead of stored in Foundry | implementer, inside the accepted boundary | Authority, topology and the HTTP boundary are all unchanged: same submit-only principal, same endpoint, same bearer scheme, same rotation mechanism. What changed is the operator workflow and one deleted setting. It is a *removal* of exposure, not a new mechanism |
| Storage state is enforced and never repaired | implementer, with the policy question escalated | Refusal is the conservative choice the review asked for. **Whether this process should ever repair permissions instead is Peter's**, and is stated as such in operations §5.6 and in §9 below |
| `stored` → `recorded` in an append-only payload | implementer | No row has ever carried the old key; the action exists only in this uncommitted package |

**Nothing here required a plan §0.2 baseline change**, and none is claimed. I
considered and rejected two designs that would have:

- **a short-lived token endpoint** (the module exchanges a GM proof for a
  minutes-long credential). It is a genuinely better long-term answer, and it is
  a **second HTTP route**, which ADR 0009 explicitly reserves as a new decision,
  plus an authentication surface Phase 3 owns. Out of scope for a remediation;
  raised in §9 as a decision for Peter to take when Phase 3 arrives.
- **`scope: "client"` storage** (browser `localStorage`, never sent to the
  server, unreadable by other clients). It would satisfy the letter of S-B-1 and
  keep the old convenience. Rejected: it puts a reusable bearer at rest in a
  browser profile indefinitely, which is a worse resting place than a password
  manager for no benefit beyond saving one paste per submission.

## 6. Verification — exact commands and exact results

**Superseded by the figures below.** The block that follows was run on
2026-08-04 after the second remediation and is left in place because §13.3 is
about exactly this: it reported 1912 passing tests, and on the review host 32 of
them failed at the startup ancestor gate. A count that cannot be reproduced by
the reviewer is not evidence, and recording that plainly is more useful than
replacing the number.

### 6.0 Current figures — 2026-08-05, after the third remediation

Run in `/opt/discord-bots/freedom-bot`.

```bash
(cd foundry-module && node --test "tests/*.test.mjs")
```
**81 passed, 0 failed, 0 skipped**, 148 ms. Unchanged: this remediation touched
no module JavaScript.

```bash
TEST_DATABASE_URL=postgresql+psycopg:///freedom_test ./venv/bin/python -m pytest -q \
  tests/test_artifact_store.py tests/test_snapshot_submission.py \
  tests/test_storage_claim_vocabulary.py tests/test_submission_composition.py \
  tests/test_http_submission.py tests/test_snapshot_preview_service.py \
  tests/test_exporter_contract.py tests/test_submission_database.py
```
**373 passed, 0 failed, 0 skipped** in 2.31s. Per file: `test_http_submission.py`
96, `test_artifact_store.py` **91** (was 63), `test_storage_claim_vocabulary.py`
90, `test_snapshot_submission.py` 56, `test_submission_database.py` 16,
`test_snapshot_preview_service.py` 10, `test_exporter_contract.py` 10,
`test_submission_composition.py` **4** (was 3).

```bash
TEST_DATABASE_URL=postgresql+psycopg:///freedom_test ./venv/bin/python -m pytest -q -rs
```
**1941 passed, 0 failed, 0 skipped**, 1 warning, in 10.75s. The warning is
`audioop` deprecation from the vendored `discord` library and is unrelated. `-rs`
reported no skips, so `node` was present and the cross-language contract test
really ran. 1912 → 1941: 28 new storage tests and one new composition test; **no
test was deleted or weakened**, and `git diff` on the test files shows the
`os.replace` monkeypatch signatures that became `os.link` ones and the two
ancestor tests that no longer need to patch `os.lstat` at all.

```bash
./venv/bin/python -m compileall -q application adapters domain tools tests migrations
```
**Clean, exit 0.**

```bash
APP_ENVIRONMENT=test DATABASE_URL='postgresql+psycopg:///freedom_test' ./venv/bin/alembic check
```
**"No new upgrade operations detected."**

```bash
git diff --check
```
**Clean, exit 0.**

```bash
for file in foundry-module/scripts/*.js foundry-module/tests/*.mjs; do node --check "$file"; done
```
**16 files, all ok.**

**Two runs that are not in the standard list**, both requested by the third
review and both reproducible — the exact scripts are in the review request:

- **the suite under the review host's ancestor ownership.** A throwaway harness
  reports `/` and `/tmp` as owned by uid 65534, leaving every other stat real.
  **1941 passed, 0 failed, 0 skipped** — identical to the unpatched run. Before
  this remediation the same harness produced 32 failures in
  `tests/test_artifact_store.py` and 2 in `tests/test_submission_composition.py`;
- **the new tests against the superseded publication.** Publication was
  temporarily reverted to unconditional `os.replace` and
  `tests/test_artifact_store.py` re-run: **10 failed, 81 passed**, including all
  five "appearing in the window" tests and both cleanup tests. The link-based
  implementation was then restored and the suite re-run clean.

### 6.1 Superseded — 2026-08-04, after the second remediation

These figures could not be independently reproduced on the review host. See
§13.3.

```bash
(cd foundry-module && node --test "tests/*.test.mjs")
```
**81 passed, 0 failed, 0 skipped.** `settings.test.mjs` contributes 6 and the
new `claims.test.mjs` contributes 3.

```bash
TEST_DATABASE_URL=postgresql+psycopg:///freedom_test ./venv/bin/python -m pytest -q \
  tests/test_artifact_store.py tests/test_snapshot_submission.py \
  tests/test_http_submission.py tests/test_snapshot_preview_service.py \
  tests/test_exporter_contract.py tests/test_submission_database.py
```
**251 passed, 0 failed, 0 skipped** in 1.95s. Per file:
`test_http_submission.py` 96, `test_artifact_store.py` 63,
`test_snapshot_submission.py` 56, and 36 across the other three. The two suites
added by §12 are run separately and are in the full suite below:
`tests/test_storage_claim_vocabulary.py` 90 (parameterised per file) and
`tests/test_submission_composition.py` 3.

```bash
TEST_DATABASE_URL=postgresql+psycopg:///freedom_test ./venv/bin/python -m pytest -q -rs
```
**1912 passed, 0 failed, 0 skipped**, 1 warning, in 9.98s. The warning is
`audioop` deprecation from the vendored `discord` library and is unrelated.
`-rs` reported no skips, so `node` was present and the cross-language contract
test really ran.

```bash
./venv/bin/python -m compileall -q application adapters domain tools tests migrations
```
**Clean, exit 0.**

```bash
APP_ENVIRONMENT=test DATABASE_URL='postgresql+psycopg:///freedom_test' ./venv/bin/alembic check
```
**"No new upgrade operations detected."** No model changed, and no migration was
added or edited by this remediation.

```bash
git diff --check
```
**Clean, exit 0.**

**Module JavaScript syntax — every file, not a sample.** `node --check` on all
seven `scripts/*.js` and all nine `tests/*.mjs`: **16 files, all ok.**
`module.json` and `package.json` both parse as JSON.

**A real socket exercise** was added:
`test_the_preflight_and_the_post_are_well_formed_over_a_real_connection` serves
the application under `wsgiref.simple_server` on an ephemeral loopback port and
drives a real `OPTIONS` then a real `POST` over one `http.client` connection. It
proves the body-less `204` is framed correctly by an actual server — the class of
bug this package has already had once, when an over-read passed every
`BytesIO`-backed test and hung the first real request. **It is not proof that
browser CORS works**: no client here enforces CORS.

### Formatter, linter, type checker — accurately reported

**None is configured in this repository and none is installed in the
virtualenv.** There is no `pyproject.toml`, `setup.cfg`, `.flake8`, `ruff.toml`,
`mypy.ini`, `tox.ini`, `.pre-commit-config.yaml` or ESLint configuration, and
`ruff`, `mypy` and `black` are all absent from `venv`. I did not install any of
them: the handover forbids installing tooling to make a handoff look complete,
and doing so would also mean reformatting files this package did not touch.

So: **no formatting, lint or type check was run, because none is configured.**
That is a standing gap, not something this remediation introduced.

## 7. Migration, configuration and deployment effects

- **Migrations: none.** No schema change, no new migration, no edited migration.
  `alembic check` is clean and `0004` is untouched.
- **One new configuration variable**,
  `FREEDOM_SNAPSHOT_ALLOWED_ORIGINS`. Optional, defaulting to *no browser origin
  permitted*. **The supported browser workflow does not work until it is set**,
  which is deliberate: unconfigured is closed, and the `403 origin_not_allowed`
  preflight in the log says exactly what is missing.
- **One configuration variable gained enforced preconditions.**
  `FREEDOM_SNAPSHOT_ARTIFACT_ROOT` must now be a real path with no symlinked
  component, a service-owned directory granting nothing to group or other, on a
  filesystem that can `fsync` a directory. **A deployment that was silently
  half-working will now refuse to start.** That is the intended behaviour of
  S-B-2's remediation, and operations §5.6 gives the repair commands.
- **One Foundry setting is removed**, `submissionCredential`. Nothing reads it
  and nothing migrates it. If a value was ever set in a world, it is stale, it is
  exposed, and it should be deleted with
  `game.settings.storage.get("world")` inspection plus a `Setting` delete —
  though no world has ever had one, because the module has never been installed.
- **Caddy:** must pass `OPTIONS` through and add no CORS header of its own. The
  documented block already does both; this is now stated as a requirement rather
  than left implicit.
- **Module version left at `1.0.0`.** It has never been installed anywhere, so
  there is no deployed version to distinguish this from, and `exporterVersion`
  travels in the bundle and into contract fixtures. Bumping it is Peter's call
  at installation time.

## 8. Rollback and recovery

- **Rollback of this remediation** is `git checkout` of the listed files —
  nothing is committed, no schema changed, no data was written.
- **Rollback of the CORS change** is emptying `FREEDOM_SNAPSHOT_ALLOWED_ORIGINS`
  and reloading. That returns to "no browser may submit", which is where B-1
  found us, so it is a diagnostic rather than a fix.
- **Rollback of the storage enforcement** is not offered, and should not be: it
  would be a decision to accept a world-readable store.
- **Orphan artifact recovery** is operations §5.6 and §9. Identify, report, do
  not delete automatically. A retry of the same idempotency key re-uses the file
  rather than duplicating it.
- **Credential rotation** is operations §5.3, and no longer touches Foundry.

## 9. Residual risks, and what is reserved to Peter

| # | Item | State |
|---|---|---|
| R7 | **B-1 is not verified from a real browser.** Automated tests reproduce the preflight and one exercises a real socket; neither is a browser, and `curl` does not enforce CORS | **Open.** Operations §8.2 is the maintainer-supervised check. Not run — it needs Peter and a Foundry instance |
| — | **S-B-1's confidentiality boundary is not verified from a second live client.** The test models Foundry's delivery from its source; it does not observe a real player's browser | **Open.** Operations §8.1 is the maintainer-supervised check. Not run |
| — | The credential is typed into a browser DOM once per submission. A malicious Foundry module or browser extension in the GM's browser can observe it | **Accepted and documented.** It is strictly better than the previous state, where every client was *given* it. Foundry module trust is already load-bearing for this integration |
| — | Per-submission entry is a real operator-workflow change: the GM must hold the secret and paste it each time | **Peter's to accept.** It is the price of there being no confidential storage in Foundry |
| **D-a** | **Should a short-lived token exchange replace the reusable bearer?** It removes the reusable secret from the browser entirely | **Reserved to Peter.** It is a second HTTP route and an authentication surface Phase 3 owns; ADR 0009 makes it a new decision |
| **D-b** | **Should this process ever repair storage permissions instead of refusing?** | **Reserved to Peter.** Implemented as refusal, per the review's stated preference. Changing it is an operations-policy decision |
| **D-c** | **Retention for database-unclaimed artifacts.** | **Reserved to Peter**, once Phase 3 makes the useful lifetime of a pending artifact known. Until then: identify, leave, delete under ordinary retention once the incident is closed |
| — | ADR 0009's textual scope mismatch about the inert preview route, raised in the review's governance section | **Untouched.** It is Peter's to reconcile and was not a finding |

## 10. Confirmations

- **No real credential was used or issued.** Every credential in this work is
  synthetic and invented for a test (`"s" * 32`,
  `foundry-the-guild.0123…`). §5.2 of the operations document was not run.
- **No real player, character or world data was used.** Every fixture is
  synthetic by construction.
- **No prohibited Foundry source was accessed.** I read the installed Foundry
  **application** source, which the handover permits, to establish supported
  setting behaviour: `common/documents/setting.mjs`,
  `client/helpers/client-settings.mjs`, `client/game.mjs`,
  `client/documents/collections/world-settings.mjs`, `common/constants.mjs`,
  `dist/packages/world.mjs`, `dist/database/documents/setting.mjs` and
  `dist/database/backend/server-document.mjs`. **No world storage, LevelDB store
  or compendium pack was opened or read.**
  **One disclosure:** while locating the Foundry installation I ran a directory
  listing that included `/home/foundry/shared/worlds`, returning world *directory
  names* only. No file in it was opened and nothing was read from it. The
  handover names that path as out of bounds, so I am recording it rather than
  leaving it in shell history; I did not return to it.
- **Neither rehearsal was run.** Not Rehearsal A, not Rehearsal B, not the new
  §8.1 or §8.2 supervised checks.
- **The module was not installed** and no Foundry world was touched.
- **Nothing was committed and nothing was pushed.** `git status` shows the same
  working tree, plus this remediation.
- **No finding is marked closed on my authority**, and no phase gate is claimed.

## 11. Requested reviews

Two separate reviews by an agent that did not implement this work, per plan
§0.3 and §16.4. Amended for the second remediation:

1. an **independent implementation re-review** of **I-1** and of the
   preservation of I-2 (B-1 was not reopened); and
2. an **independent security re-review** of **S-B-2** and of the preservation of
   S-B-1 and S-I-1.

The self-contained mapping from each original finding to changed files, named
tests and operational evidence is
[`phase-2-i-03-remediation-review-request.md`](phase-2-i-03-remediation-review-request.md).

Peter Duscha remains the Acceptance Authority and records the decision.

## 12. The second remediation, 2026-08-04 — I-1 and S-B-2

The re-review of the work above found two findings still open. This section is
the record of what was actually wrong and what now stands in its place. Both
findings **remain open**: I close neither.

### 12.1 I-1 — the claims the first attempt did not look for

**What was wrong.** §3.5 corrected the messages the review had named and stopped
there. The claim survived in four more places, and three of them are on paths
that run *after* `_store_and_record` has already published bytes:

| Where | The claim | Why it was false |
|---|---|---|
| `submission.py` unresolved-concurrency refusal | "Nothing was stored." | reached after the artifact store has run — twice, in the checksum-race branch |
| `submission.py` `_replay_stored`'s unresolvable branch | "Nothing was stored." | the store has run, *and* another submission demonstrably recorded something |
| `submission.py` `_replay`'s two refusals | "Nothing was stored." | reachable both before and after the store, and the key was spent by a submission whose record is intact |
| `application/artifacts.py` | "Nothing was stored or served." on **every** `ArtifactStorageError` | false for `durability_unconfirmed`, whose deliberate contract is that a correct target may already be published and must be preserved for the retry |

**What is there now.**

- **The outcome is declared per failure, not inherited.** `StorageOutcome` has
  two values — `UNCHANGED` ("No artifact was published, and nothing already held
  was changed or removed") and `UNRESOLVED` ("Whether an artifact is held under
  that checksum is not established by this failure…"). Each raise in the adapter
  names one. The **default is `UNRESOLVED`**, so a reason nobody classified
  produces a vaguer true statement rather than a stronger false one, and
  `test_every_storage_refusal_declares_what_it_establishes` walks the adapter's
  syntax tree so the default stays a safety net rather than the normal path.
- **Each refusal in `submission.py` says what its own path established.** The
  three post-store refusals say *this attempt* recorded nothing and that a retry
  cannot create a second snapshot; the two replay refusals add that the earlier
  submission's record is unchanged, because denying that would be the mirror
  image of the original defect.
- **The one genuinely pre-storage refusal is specific rather than broad.** The
  claimed-digest mismatch says the artifact store was never asked to hold these
  bytes — useful, because it tells the client the transfer is what to repeat —
  rather than reaching for a phrase that happens to be true in that branch.
- **`application/errors.py` is scoped.** `UniquenessConflict` and
  `PersistenceError` said "Nothing was written". They are database errors, but
  they are raised on a path where an artifact has already been written, so they
  now say "to the database" explicitly.
- **`wsgi.py`'s `incomplete_body`** no longer says it either, although that path
  could truthfully have done so.

**The regression check the handover asked for** is
`tests/test_storage_claim_vocabulary.py`. It is repository-wide and it
distinguishes asserting the claim from discussing it:

| Scanned | Rule |
|---|---|
| Python string literals that are **not** docstrings, in `application/`, `adapters/`, `domain/`, `tools/`, `migrations/` | banned |
| Python docstrings and `#` comments | allowed — the explanation has to be writable |
| `foundry-module/scripts/` with comments stripped | banned |
| `docs/operations/`, `docs/adr/`, `docs/rules/` | allowed only inside quotation marks |
| `tests/`, `foundry-module/tests/`, `docs/review/`, `docs/project-management/` | not scanned: a test that forbids a phrase must name it, and the review record must quote it |

It carries its own proofs that it catches a reintroduction and does not ban the
explanation, because a guard nobody has seen fail is a guard nobody knows works.
`foundry-module/tests/claims.test.mjs` applies the same rule from the module's
own suite.

**Named tests.**

| Required by the handover | Test | File |
|---|---|---|
| unresolved uniqueness/concurrency makes no false claim | `test_an_unresolvable_uniqueness_conflict_makes_no_filesystem_claim`, `test_an_unresolvable_key_race_speaks_only_about_this_attempt` | `test_snapshot_submission.py` |
| `durability_unconfirmed` makes none while the target is present | `test_an_unconfirmed_durability_refusal_leaves_the_correct_target_in_place`, `test_durability_unconfirmed_makes_no_claim_about_the_filesystem` | `test_snapshot_submission.py`, `test_artifact_store.py` |
| replay paths distinguish this attempt from recorded state | `test_a_spent_key_refusal_does_not_deny_the_earlier_submission`, `test_an_unreadable_receipt_refusal_does_not_deny_the_earlier_submission` | `test_snapshot_submission.py` |
| the whole vocabulary, enumerated | `test_no_refusal_this_service_can_raise_claims_the_filesystem_is_unchanged` — raises **every** declared refusal code and fails if one becomes unreachable | `test_snapshot_submission.py` |
| HTTP rendering preserves the wording | `test_every_refusal_reaches_the_wire_with_its_wording_intact`, `test_an_unconfirmed_durability_refusal_reaches_the_wire_truthfully` | `test_http_submission.py` |
| Foundry notification rendering | `no module message tells the GM that nothing was stored`, `a failed submission tells the GM what a retry actually guarantees` | `foundry-module/tests/claims.test.mjs` |
| repository-wide regression check | the whole of `test_storage_claim_vocabulary.py` | — |

The orphan procedure is unchanged and remains read-only: no listing route, no
deletion route, no `list` or `delete` on the store, and the retention decision
still reserved to Peter (D-c).

### 12.2 S-B-2 — the root is a descriptor, not a pathname

**What was wrong.** §3.3's checks were real, and every one of them was made by
**pathname**. `_ensure_root()` `lstat`ed the configured path; then `store()`
created its temporary through that path, opened and verified through it,
`os.replace`d through it, and `_fsync_directory()` re-opened it. An account able
to rename entries in a writable parent could substitute a directory between the
check and any of those uses, and each would follow the name. Adding another
pathname check would have moved the window, not closed it.

**What is there now.**

| Operation | Anchoring |
|---|---|
| creating the temporary | `os.open(name, …, dir_fd=root)` |
| reading, verifying or reusing an artifact | `os.open(name, O_RDONLY \| O_NOFOLLOW, dir_fd=root)` |
| publishing | `os.replace(tmp, name, src_dir_fd=root, dst_dir_fd=root)` |
| removing a failed temporary | `os.unlink(name, dir_fd=root)` |
| presence | `os.stat(name, dir_fd=root, follow_symlinks=False)` |
| directory `fsync` | `os.fsync(root)` — the descriptor itself |

- **The descriptor is the trusted object.** It is opened once with
  `O_DIRECTORY | O_NOFOLLOW`, so the open itself refuses a non-directory and
  refuses a symlinked root rather than following it, and its type, owner and mode
  are proved with `os.fstat` **on the descriptor** — at startup, on every store
  and on every read.
- **Names are resolved relative to it**, and an artifact's name is a validated
  hex digest plus a fixed suffix, so containment is a property of the name's
  shape rather than a comparison somebody has to remember to make. `_path_for`'s
  `Path` arithmetic is gone.
- **Divergence is reported, and is not the mechanism.** Each use compares the
  configured pathname's `(st_dev, st_ino)` with the anchored directory's and
  refuses `root_replaced` if they differ. The anchoring is what makes a
  replacement harmless; this is what stops the service quietly writing into an
  inode no operator can name. **Moving the artifact root now requires a service
  restart**, which is documented in operations §5.6 and `.env.example`.
- **Ancestors are checked once, at startup.** Each parent must be a directory
  owned by `root` or by this account and must not be writable by others without
  the sticky bit — the condition under which the replacement could have been
  staged at all. A descriptor cannot observe its ancestors, and re-walking a
  pathname per request would reintroduce the very window being removed. That
  trade-off is written into the adapter docstring and into operations §5.6.
- **Reads re-check the root as well as writes.** A deliberate decision, which
  the handover asked to be made deliberately and documented: a root that has
  become readable by another account is no longer restricted storage, so a
  preview refuses rather than continuing to serve Actor mechanics out of it.
- **Lifetime is explicit.** `close()` releases the descriptor; the store is a
  context manager; `Composition.dispose()` calls `close()`, and every startup
  refusal after anchoring closes it before the exception leaves
  `build_application`. `__del__` closes too, but it is documented as a backstop
  and nothing depends on it.
- **Refusal, not repair, is unchanged.** No `chmod`, no `chown`, no directory
  created to satisfy a read. D-b remains Peter's.
- **`write_failed` cannot occur after publication.** The `os.replace` is now the
  last statement inside the block that produces it, so the one refusal that
  claims nothing was published is structurally unable to run once something has
  been, and `_discard` is unreachable from beyond it.
- **The platform is probed rather than assumed.** `ensure_ready()` refuses
  `nofollow_unsupported` or `dir_fd_unsupported` where the anchored semantics are
  unavailable, instead of silently degrading to pathname operations. On this
  deployment (Linux, CPython 3.12) all of them are available, so no constraint
  needed to be brought to Peter.

**Named tests** — `tests/test_artifact_store.py` unless stated.

| Required by the handover | Test |
|---|---|
| a store cannot be redirected to the replacement | `test_a_store_cannot_be_redirected_by_replacing_the_root_pathname`, `test_a_swap_after_validation_still_writes_to_the_anchored_directory` |
| a load cannot read from the replacement | `test_a_load_cannot_read_an_artifact_from_a_replacement_directory`, `test_an_artifact_read_is_anchored_even_when_the_root_name_is_swapped` |
| a target cannot be swapped for a symlink between validation and read | `test_an_existing_target_cannot_be_swapped_for_a_symlink_before_the_read` |
| publication and directory `fsync` use the anchored directory | `test_publication_and_directory_fsync_use_the_anchored_directory` (asserts `src_dir_fd`/`dst_dir_fd` are present and that both operations act on the validated inode) |
| unsafe owner/mode/type still fail closed without repair | `test_the_root_state_is_rechecked_through_the_descriptor_on_every_store`, `test_a_read_rechecks_the_root_too`, `test_no_unsafe_state_is_repaired_silently`, and the existing permissive/owner/type group |
| descriptors closed on completion and every injected failure | `test_the_store_holds_exactly_one_descriptor_however_many_operations_run`, `test_no_descriptor_survives_a_refused_operation`, `test_a_refused_startup_leaves_no_descriptor_open`, `test_close_releases_the_descriptor_and_is_idempotent`, `test_the_store_is_a_context_manager`, `test_a_dropped_store_does_not_hold_its_descriptor_forever`, and `tests/test_submission_composition.py` for the composition boundary |
| retry after `durability_unconfirmed` still succeeds | `test_a_retry_after_durability_unconfirmed_neither_duplicates_nor_destroys`, plus the preserved `test_a_retry_after_an_unconfirmed_durability_failure_succeeds` in `test_snapshot_submission.py` |
| the ancestor precondition | `test_an_ancestor_another_account_can_rename_entries_in_is_refused`, `test_a_sticky_shared_ancestor_is_accepted` |

The substitution is performed with controlled renames and replacement
directories that this account owns `0700`, so the owner and mode checks cannot be
what refuses them — the question each test asks is whether the *anchoring* kept
the operation off the replacement. **No test creates a second POSIX account and
none requires privilege**, as the handover directs.

**One behaviour changed, and it is worth the reviewer's attention.** A failure to
*open* the root used to surface as `durability_unconfirmed`, because the only
thing that opened it was the directory `fsync`. It now surfaces as
`root_unavailable`, before anything is written. Both refuse the submission and
both commit nothing, so I-2's guarantee is unchanged; the new code is the more
precise statement, and it is the one that may truthfully say nothing was
published. `test_a_directory_open_failure_refuses_the_store` asserts the new
reason and records why.

### 12.3 What is still not established

- **No cross-account experiment.** The anchoring is proven against pathname
  substitution performed by this process, and against type, owner and mode as
  this process observes them. A real second POSIX account attempting the
  replacement on the deployment host is an observation nobody has made.
- **The ancestor walk is a startup check.** A parent that becomes writable while
  the service runs is not detected. The anchored descriptor is what makes that
  survivable, and the reasoning is written down rather than left implicit — but
  a reviewer who disagrees with that trade-off should say so.
- **`root_replaced` is fail-closed, not tamper-evident.** It tells an operator
  that the configured name no longer refers to the anchored directory. It does
  not tell them who moved it, and it is not an alert.
- **The operational consequence is real.** A deployment whose artifact root has
  an ancestor writable by another account without the sticky bit will now refuse
  to start. That is intended, and it is the kind of change Peter should see
  stated plainly rather than discover during a deployment.

## 13. The third remediation, 2026-08-05 — publication, the I-1 default, test evidence

The third independent re-review reported the S-B-2 remediation in §12.2 as a
material fix: creation, reads, publication, `unlink`, `stat` and directory
`fsync` are all resolved relative to the anchored root, and the
pathname-redirection defect is gone. It then found three things that anchoring
does not address.

I want to state the shape of the mistake before the fix, because it is the third
time it has been the same shape. §12.1 fixed the *messages a reviewer had named*
and missed the class. §12.2 fixed *where* operations resolve and did not ask what
the final operation actually does. Both times the correction was real and both
times it stopped one level short of the rule.

### 13.1 Blocking — publication could overwrite an entry nobody had validated

**The defect.** `store()` was:

1. `_holds()` — open the checksum entry through the anchored descriptor,
   validate it completely, or find it absent;
2. write a temporary file, `fsync` it, read it back and verify its hash;
3. `os.replace(temporary, name, src_dir_fd=root, dst_dir_fd=root)`.

Step 3 is anchored, and step 3 is atomic — about **replacing**. A checksum-named
entry that appeared between 1 and 3 was removed and this process's file put in
its place, with nobody having looked at it. Anchoring proves the operation stayed
inside the approved directory; it says nothing about whether the operation should
have happened.

The window is not theoretical for this design. D5 stores the artifact before
committing the row precisely so that concurrent and retried submissions are
normal, and the store is content-addressed precisely so that two submissions of
identical bytes meet on one name. The race is the ordinary case, not the exotic
one. What it violated, all at once:

- artifacts are immutable and content-addressed;
- an unsafe or mismatched target is refused, not repaired;
- unexpected evidence is preserved for an operator;
- no existing artifact is implicitly deleted;
- publication is safe under concurrency.

**The remediation.** Publication is `os.link`. `linkat(2)` creates the
destination entry or fails `EEXIST`, and it has no mode in which it removes what
is already under the name. The test and the creation are one kernel operation, so
there is no window between them — which is why a pathname existence check
followed by `os.replace` was not an option, and why the review was right to name
it as the same race in a different shape.

| Situation | What happens now |
|---|---|
| the name is free | the link succeeds. Exactly one writer can win; the kernel serialises it |
| another writer won | `EEXIST`. The entry is re-opened through the anchored descriptor with `O_NOFOLLOW` and re-proved from nothing — regular file, service-owned, nothing to group or other, bytes hashing to the name — by the *same* `_holds()` that runs before the write. Valid: their file is the artifact and this submission reuses it. Invalid: refused, and left byte for byte and mode for mode |
| the entry vanishes between `EEXIST` and the open | retried, three times, then `publication_unsettled`. Unreachable in production — nothing here removes an artifact — and bounded so that a filesystem which produces it anyway refuses rather than spins |

Three consequences, all deliberate and all documented in the adapter's
"Publication never overwrites" section:

- **the bytes briefly have two names.** Both are inside the anchored root, both
  are `0600` and service-owned, and the artifact's mode and ownership are the
  *same inode's* — so they cannot drift from what `os.open` created, which a
  rename could not have guaranteed either. `_discard` removes the temporary —
  **best effort; it swallows `OSError`, so a successful store may leave one
  `.incoming-*` link behind, and §14 is the correction of the sentence in the
  third-remediation request that denied it** — and
  `_discard` now **refuses to unlink any name without the temporary prefix**. That
  is not decoration: publication's success path now calls it, and the one thing it
  must never be able to do, however this module is edited later, is remove a
  published checksum entry because a cleanup step went wrong;
- **the temporary's removal is a publication-related directory-entry change**, so
  it happens *before* the directory `fsync`. One sync makes the creation and the
  removal durable together. `write_failed` — the one refusal claiming nothing was
  published — remains structurally unreachable after publication succeeds;
- **hard links must work.** `ensure_ready()` proves it: it links a probe file,
  links it a second time, and requires the second attempt to fail `EEXIST`. A
  filesystem that cannot do either refuses `link_unsupported` at startup. Both
  probe names carry the temporary prefix, so they are removed by the same
  `_discard` that can only remove a temporary.

**`renameat2(RENAME_NOREPLACE)` was considered and not used.** It gives the same
guarantee in one syscall and would remove the extra `unlink`. The standard
library exposes no wrapper, so it would mean a hand-rolled `ctypes` syscall stub
— a raw `syscall(SYS_renameat2, …)` with hand-written argument marshalling — in
the code path that stores every exported Actor's mechanics, plus a silent
narrowing to Linux with a specific kernel. The review named both of those as
things not to do quietly. One extra `unlink` on a path that already does two
`fsync`s is the cheaper trade. It is recorded in the adapter docstring,
operations §5.6 and package-plan item D10 rather than left as an unexplained
choice.

**Named regression tests** (`tests/test_artifact_store.py`, section "publication
never overwrites an unvalidated entry"):

| Test | Proves |
|---|---|
| `test_a_valid_target_appearing_before_publication_is_reused_not_overwritten` | the winner's file is reused; asserted by **inode**, because equal bytes would pass under the old implementation too |
| `test_a_mismatched_target_appearing_before_publication_is_refused_intact` | `checksum_mismatch`, and the planted file's exact bytes, mode and inode are unchanged |
| `test_a_symlinked_target_appearing_before_publication_is_never_followed` | `artifact_untrusted`; the link still exists and its target was not written through |
| `test_a_non_regular_target_appearing_before_publication_is_refused` | `artifact_not_a_regular_file`; the directory is still there |
| `test_a_permissive_target_appearing_before_publication_is_refused_intact` | `artifact_permissive`; the mode is untouched |
| `test_two_writers_of_identical_bytes_converge_on_one_artifact` | a second store object publishes inside the first's window; one file, one reference, the winner's inode, and — with both cleanups allowed to succeed, which is the test's precondition and is now stated in it — no surviving temporary |
| `test_publication_stays_anchored_when_the_root_name_is_taken_over` | the root pathname is replaced inside the publication window; the entry lands in the validated directory and nothing appears in the replacement |
| `test_a_failed_publication_cleans_up_and_publishes_nothing` | injected publication failure removes only the temporary |
| `test_cleanup_can_only_ever_remove_a_temporary` | every `unlink` the store performs names a `.incoming-*` file, on success and on refusal |
| `test_a_failing_cleanup_leaves_the_published_artifact_alone` | a cleanup failure leaves the artifact published |
| `test_a_startup_probe_proves_publication_refuses_to_overwrite` | `link_unsupported` when links fail *and* when a link does not refuse an existing name |
| `test_the_startup_probe_leaves_nothing_behind` | the probe leaves an empty root |
| `test_an_unacknowledged_durability_failure_does_not_destroy_a_correct_target`, `test_a_retry_after_durability_unconfirmed_neither_duplicates_nor_destroys` | I-2 preserved: injected directory-sync failure after successful publication leaves the correct target, and the retry validates and reuses it |

**The tests fail against the superseded implementation, and that was checked
rather than assumed.** The window is entered by hooking the *verification re-read
of the temporary file* — the last thing that happens before the entry is created,
in any implementation of publication — so no test names `os.link`. Publication
was temporarily reverted to unconditional `os.replace` and the suite re-run:
**10 failed, 81 passed**, including all five "appearing in the window" tests and
both cleanup tests. The link-based implementation was then restored.

### 13.2 Important — the failure vocabulary's default made an unproven claim

**The defect.** §12.1 made what a failure claims a declared property per raise,
defaulting to `UNRESOLVED`. `UNRESOLVED`'s sentence still contained "Nothing
already held was changed or removed" — which §13.1 made false, and which is
worse than an ordinary false message because `UNRESOLVED` is the **default**: it
is the sentence attached to every path nobody has classified.

**The remediation**, and it is a rule rather than three edits:

> A conservative default may state what is structurally true of a
> content-addressed store. It may not make a positive claim about what is on the
> filesystem.

`StorageOutcome` now has three values, and each sentence is provable on every
path that raises with it:

| Outcome | Sentence | Raised by |
|---|---|---|
| `UNCHANGED` | "No artifact was published, and no artifact already held was changed or removed." | every pre-publication refusal: root state, platform support, `write_failed`, `publication_unsettled`, the temporary's own verification, `ArtifactNotStored` |
| `PRESERVED` | "No artifact was published. An entry was already present under that checksum and was refused; it has been left exactly as it was found, so that it can be examined." | `checksum_mismatch`, `artifact_untrusted`, `artifact_permissive`, `artifact_not_owned`, `artifact_not_a_regular_file` — from `_holds()` and from `load()`, i.e. exactly where an entry exists under the checksum name |
| `UNRESOLVED` (default) | "Publication under that checksum may or may not have completed, and its durability was not confirmed. Retrying the same content is safe: the store is content-addressed, so a retry resolves to the same artifact and cannot create a second one." | `durability_unconfirmed`, and anything unclassified |

`PRESERVED` exists because the review asked for a failure after detecting a
concurrent target to distinguish a validated existing artifact from an unsafe
entry that was preserved. A validated one is not a failure at all — it is reused
and the submission succeeds — so the distinction that needs making is between
"there was nothing there" and "there was something, it was refused, and it is
still there". Those send an operator to different procedures, and operations §5.7
now carries that mapping as a table and §9 the procedure.

The outcome is chosen by the **caller** rather than by the reason code, because
the same three refusals mean different things depending on what was being
examined: `_read_trusted` takes it as an argument, `_holds()` and `load()` pass
`PRESERVED`, and `_verify_written` — which is reading this attempt's own
temporary file, about to be discarded — passes `UNCHANGED`.

**The repository-wide phrase check is kept as defence in depth and is explicitly
not the proof.** The review was right that it is not evidence of semantic
correctness; it catches a reintroduction of a known wording. What carries the
claim now is behaviour tests tied to filesystem state:
`test_the_conservative_default_claims_nothing_about_durable_state`,
`test_a_preserved_entry_is_distinguished_from_having_found_nothing`,
`test_durability_unconfirmed_makes_no_claim_about_the_filesystem`, and every
`outcome is StorageOutcome.PRESERVED` assertion in the publication-race group
above, each of which also asserts the file it refused is byte-identical
afterwards.

**Nothing in this document, the review request or the project-management records
claims I-1 was closed by a textual scan.** §12.1 said the scan was
repository-wide, which was true and insufficient; the correction is recorded here
and in package-plan §9 rather than by editing §12.1.

### 13.3 Important — the automated evidence was not reproducible

**The defect.** On the review host `/` and `/tmp` are owned by uid 65534.
`_require_trusted_ancestors()` accepts only `root`- or service-owned ancestors,
so it refused, and **32 tests failed before reaching their own assertions** —
tests about publication, durability, anchoring and descriptor lifetime, none of
them about ancestors. `--basetemp` cannot help: every absolute path has host
ancestors. The submitted figure of 1912 was therefore not independently
reproducible, which makes it not evidence.

**The remediation.** The ancestor rule is now an object, `TrustedAncestors`, with
an optional `ceiling` that bounds the walk. It is the only rule in the adapter
whose answer depends on directories the deployment does not own, which is exactly
why it is the one that had to become injectable.

- **the same code, the same real `os.lstat` calls.** Tests about publication,
  durability, anchoring and descriptor lifetime bound the walk at pytest's
  `getbasetemp()`. Below the boundary the production rule runs against real
  directories the test created; above it, the host's business is the host's;
- **nothing is globally monkeypatched.** No test replaces `os.stat` or `os.lstat`
  wholesale, so the root and target checks — which are what those tests are about
  — keep testing real filesystem behaviour. The two ancestor tests that formerly
  patched `os.lstat` for one path no longer need to;
- **the rule is tested directly**, on real directories with real modes, for
  trusted, untrusted (five modes), sticky (three modes), wrong-owner,
  non-directory, symlinked and absent ancestors, plus
  `test_the_walk_stops_at_the_ceiling_and_not_before`, which asserts what the
  bound excludes rather than leaving it to be assumed;
- **the production walk is exercised unbounded**, against the real configured
  path, all the way to `/`:
  `test_the_production_walk_checks_the_real_configured_path` computes the verdict
  independently from `os.lstat` and requires the store to agree, so it is a real
  check on a conventional host *and* correct on a host where `/tmp` is owned by
  `nobody`. `test_the_production_composition_walks_to_the_filesystem_root` does
  the same through `build_application`;
- **the bound is a test seam and cannot become a deployment one.**
  `build_application` accepts it only as a keyword, in the same way it already
  accepts `deployment`; there is no environment variable, and
  `test_an_unbounded_rule_is_the_production_default` and the composition test
  above assert that configuration alone produces the unbounded walk.

**The production owner rule was not changed.** The review said that weakening it
would be a security-policy decision for Peter and the independent reviewer rather
than a drive-by test fix. I agree and did not take it. The prerequisite it
imposes on a deployment is real, is now stated as such in operations §5.6 under
"a genuine environmental prerequisite remains", and is registered as R-17.

**This was verified against the review host's condition, not argued.** A
throwaway harness — not committed — patched `os.lstat` to report uid 65534 for
`/` and `/tmp` only, leaving every other stat real, and the full suite was run
under it: **1941 passed, 0 failed, 0 skipped**, identical to the unpatched run.
The harness is reproduced in the review request so the reviewer can run it.

### 13.4 What is still not established

Everything in §12.3 stands. In addition:

- **convergence is proven deterministically, not by concurrency.** The second
  writer runs *inside* the first's publication window, from a second store object
  with its own descriptor, on the same root. That exercises the exact code path
  two real processes would take, and it is not a multi-process stress test. I
  judge the deterministic form to be the better evidence — a stress test that
  happens not to hit the window proves nothing — but a reviewer who wants a
  concurrent one should say so;
- **the `EEXIST` guarantee is the kernel's.** The store proves at startup that
  the configured filesystem provides it, which is better than citing `linkat(2)`,
  and it is still a property of the platform rather than of this code;
- **the hard-link requirement is new and could refuse to start a deployment**
  whose artifact root is on a filesystem that does not support it. That is
  intended and documented, and it is the kind of change Peter should see stated
  rather than discover;
- **`publication_unsettled` has no natural cause.** It is tested by construction
  only, because nothing in this store can produce the state that reaches it;
- **the bounded ancestor walk is a real reduction in what the storage tests
  observe.** They no longer notice a host with a hostile parent chain. That is
  deliberate, the production walk is exercised separately, and it is the trade
  I would most like a reviewer to disagree with if they are going to.
