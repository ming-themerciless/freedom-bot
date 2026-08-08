# Re-review request — Phase 2 I-03 remediation

From: Claude, implementing agent and working Technical Lead
To: an Independent Reviewer who did not implement this work (plan §0.3, §16.4)
Date: 2026-08-04
Repository: `/opt/discord-bots/freedom-bot`
State to review: uncommitted working tree on `docs/platform-plan`, `HEAD` at
`c8a3da9`

**Amended 2026-08-05**, after the third independent re-review. That review found
the S-B-2 root anchoring materially correct and returned one Blocking finding
(publication could overwrite an entry it had never validated) and two Important
ones (the failure vocabulary's default made a claim that defect invalidated; the
submitted test evidence was not reproducible on the review host).

**Two separate reviews are requested**, per plan §16.4:

1. an **independent implementation re-review** of the **publication fix**, of
   **I-1**, of the **test evidence**, and of the preservation of **I-2**; and
2. an **independent security re-review** of **final-target publication**, of the
   preservation of the **root anchoring**, and of the preservation of **S-B-1**
   and **S-I-1**.

B-1 was not reopened and its outstanding evidence is unchanged (§8.2 has still
not been run).

Neither review may be performed by me, and I close no finding. Peter Duscha
records the gate decision.

**Start with "Third remediation" at the end of this document.** It is
self-contained: root cause, changed files, the structural guarantee, named tests,
verification, configuration and operational effect, recovery, and residuals, for
each of the three findings. The finding-by-finding sections above it are the
first and second attempts, retained because the sequence of what was missed is
the most useful thing here — three reviews, three corrections, each of which
stopped one level short of the rule.

**Amended 2026-08-04**, after the second independent re-review found two of the
six findings still open. The "second remediation" subsections under §I-1 and
§S-B-2 describe what the first attempt got wrong.

## How to read this

Each finding below names the original text, what changed, the exact files, the
exact named tests, and **what has not been established**. The last column is the
one I would check first: two of the six are remediated by construction and test
rather than by observation, and both need a maintainer-supervised check that has
not been run.

Full narrative: [`phase-2-i-03-remediation-submission.md`](phase-2-i-03-remediation-submission.md).

## Reproducing the verification

```bash
cd /opt/discord-bots/freedom-bot

(cd foundry-module && node --test "tests/*.test.mjs")
# 81 passed, 0 failed, 0 skipped

TEST_DATABASE_URL=postgresql+psycopg:///freedom_test ./venv/bin/python -m pytest -q \
  tests/test_artifact_store.py tests/test_snapshot_submission.py \
  tests/test_storage_claim_vocabulary.py tests/test_submission_composition.py \
  tests/test_http_submission.py tests/test_snapshot_preview_service.py \
  tests/test_exporter_contract.py tests/test_submission_database.py
# 373 passed, 0 failed, 0 skipped

TEST_DATABASE_URL=postgresql+psycopg:///freedom_test ./venv/bin/python -m pytest -q -rs
# 1941 passed, 0 failed, 0 skipped, 1 warning (audioop, from the vendored discord)

./venv/bin/python -m compileall -q application adapters domain tools tests migrations
APP_ENVIRONMENT=test DATABASE_URL='postgresql+psycopg:///freedom_test' ./venv/bin/alembic check
# No new upgrade operations detected.
git diff --check

for f in foundry-module/scripts/*.js foundry-module/tests/*.mjs; do node --check "$f"; done
# 16 files, all clean
```

**No formatter, linter or type checker was run, because none is configured in
this repository and none is installed in `venv`.** There is no `pyproject.toml`,
`setup.cfg`, `.flake8`, `ruff.toml`, `mypy.ini`, `tox.ini`,
`.pre-commit-config.yaml` or ESLint configuration, and `ruff`, `mypy`, `black`,
`flake8`, `pylint` and `isort` are all absent from `venv`. Nothing was installed
to change that: installing tooling to make a handoff look complete is forbidden,
and it would also reformat files this package did not touch. It is a standing
gap, not one this work introduced.

### The two runs that are not in the standard list

Both were asked for by the third review, and both are reproducible.

**1. The suite under the review host's ancestor ownership.** The previous
submission reported 1912 passing tests; the review environment produced 32
failures, because `/` and `/tmp` there are owned by uid 65534. This reproduces
that condition on any host. Write it outside the repository — it is a harness,
not a committed test — and note that only `os.lstat` is patched, and only for two
exact paths: patching `os.stat` as well would remove it from
`os.supports_dir_fd` and make the store refuse `dir_fd_unsupported`, which is a
harness artefact rather than a finding.

```python
# /tmp/fb-harness/nobody_ancestors.py
# Report / and /tmp as owned by uid 65534. Every other stat stays real.
import os
from pathlib import Path

NOBODY, TARGETS, _real = 65534, {"/", "/tmp"}, os.lstat

def lstat(path, *args, **kwargs):
    info = _real(path, *args, **kwargs)
    try:
        matched = str(Path(path)) in TARGETS
    except TypeError:
        return info
    if not matched:
        return info
    fields = list(info)
    fields[4] = NOBODY          # st_uid
    return os.stat_result(tuple(fields))

os.lstat = lstat
```

```bash
PYTHONPATH=/tmp/fb-harness \
TEST_DATABASE_URL=postgresql+psycopg:///freedom_test \
  ./venv/bin/python -m pytest -q -rs -p nobody_ancestors
# 1941 passed, 0 failed, 0 skipped -- identical to the unpatched run.
# Before this remediation: 32 failures in tests/test_artifact_store.py
# and 2 in tests/test_submission_composition.py, all root_ancestor_untrusted.
```

**2. The publication tests against the superseded implementation.** The window is
entered by hooking the verification re-read of the temporary file — the last
thing that happens before the entry is created, in any implementation — so no
test names `os.link`, and the same tests run against any publication primitive.
To see them fail against the one they were written for, keep a copy of
`adapters/artifacts/filesystem.py`, replace the loop body of
`FilesystemArtifactStore._publish` with the superseded call, and re-run:

```python
os.replace(temporary, name, src_dir_fd=root_fd, dst_dir_fd=root_fd)
return
```

```bash
TEST_DATABASE_URL=postgresql+psycopg:///freedom_test \
  ./venv/bin/python -m pytest -q tests/test_artifact_store.py
# 10 failed, 81 passed -- all five "appearing in the window" tests,
# both cleanup tests, both injection tests, and the anchoring assertion.
```

Restore the file afterwards. It is untracked, so `git checkout` will not do it
for you.

---

## B-1 (implementation) / S-I-1 (security) — browser CORS preflight

**Original.** The module submits from a browser with `Authorization`,
`Content-Type: application/json`, `Idempotency-Key` and `X-Snapshot-SHA256`.
`OPTIONS /api/v1/foundry/snapshots` returned `405` and no CORS permission was
emitted, so the supported workflow could not reach its POST cross-origin. The
suite enshrined the absence of CORS; `curl` could not expose it.

**Changed.**

| File | What |
|---|---|
| `adapters/http/cors.py` **(new)** | the whole policy: allowlist parsing and startup validation, `allows`, `preflight`, `response_headers`, `vary_for`, `origin_of` |
| `adapters/http/wsgi.py` | `OPTIONS` routed to `_preflight` **before** authentication; permission and `Vary` applied in `__call__` before routing so the `500` path carries them; `_Response` so a body-less `204` is expressible |
| `adapters/http/composition.py` | `CorsPolicy.from_mapping(environ)` at startup; malformed configuration refuses to start |
| `tools/snapshot_api.py` | reports the configured origins |
| `.env.example`, operations §5.4, topology §6a | the environment contract, the Caddy requirement, the symptom to recognise |

**Named tests** — all in `tests/test_http_submission.py`:

| Required by the handover | Test |
|---|---|
| allowed preflight | `test_an_allowed_preflight_succeeds_and_permits_exactly_what_is_needed` |
| rejected origin | `test_an_unlisted_origin_gets_no_permission` |
| malformed origin | `test_a_malformed_or_near_miss_origin_is_refused` (8 cases: `null`, empty, suffix extension, port drift, scheme swap, mixed case with path, garbage, `*`) |
| wrong requested method | `test_a_preflight_for_the_wrong_method_is_refused` |
| extra requested header | `test_a_preflight_asking_for_an_extra_header_is_refused` |
| allowed-origin POST success | `test_an_allowed_origin_post_succeeds_and_carries_the_permission` |
| allowed-origin authenticated error | `test_an_allowed_origin_error_response_is_still_readable_by_the_browser` (2 cases), `test_an_allowed_origin_refusal_is_still_readable_by_the_browser`, `test_an_unexpected_500_is_still_readable_by_the_browser` |
| no-origin non-browser request | `test_a_non_browser_request_is_untouched_by_any_of_this` |
| correct `Vary`/allow headers | `test_vary_names_origin_on_every_submission_response`, `test_vary_on_a_preflight_names_the_request_headers_too` |

Additionally: `test_the_preflight_needs_no_credential`,
`test_a_preflight_asking_for_fewer_headers_is_allowed`,
`test_a_preflight_header_list_is_matched_case_insensitively`,
`test_an_unlisted_origin_post_is_processed_but_gets_no_permission`,
`test_the_default_composition_permits_no_browser_origin`,
`test_the_preview_route_gets_no_preflight`,
`test_a_preflight_reaches_no_application_service`, and the configuration group
(`test_an_absent_origin_allowlist_is_valid_and_empty`,
`test_configured_origins_are_normalised_to_what_a_browser_sends`,
`test_a_malformed_origin_allowlist_is_refused_at_startup` with 10 cases,
`test_loopback_http_is_permitted_for_a_same_host_rehearsal`).

**Socket-level evidence.**
`test_the_preflight_and_the_post_are_well_formed_over_a_real_connection` serves
the application under `wsgiref.simple_server` on an ephemeral loopback port and
drives a real `OPTIONS` then a real `POST` over one connection.

**What is NOT established.** **No browser was involved.** The handover is
explicit that a fake `fetch` is not evidence, and I extend that: neither is a
socket test, and neither is `curl`. B-1 is remediated by construction and by
tests that reproduce the preflight protocol, and it is **not** verified from a
real Foundry browser origin. Operations §8.2 is the maintainer-supervised check
and **has not been run**. I recommend the re-review record that explicitly.

**Points I would push on if I were reviewing.**

- Is an unlisted origin's POST being *processed* (with no permission header)
  rather than refused acceptable? My reasoning is in
  `test_an_unlisted_origin_post_is_processed_but_gets_no_permission`: the access
  control is the bearer credential, and a server-side origin refusal would be a
  second, weaker control that any non-browser caller bypasses by omitting the
  header. Worth disagreeing with if you see it differently.
- `Access-Control-Max-Age` is 600s. Revoking an origin therefore has up to ten
  minutes of preflight-cache lag in an already-open browser.
- The allowlist is normalised at configuration time. I believe that is safe
  because the request-time comparison is exact string equality on the
  normalised form, but the normaliser is the thing to read carefully
  (`_validated_origin`).

---

## S-B-1 (security) — reusable bearer in client-readable Foundry configuration

**Original.** The full credential was a `scope: "world"`, `config: false`
setting, read through `game.settings.get`. `config: false` hides a form;
`SETTINGS_MODIFY` controls writes. Neither is a confidentiality boundary, and
hiding the button from non-GMs is client-side gating.

**The Foundry facts, established first, from permitted application source.**

| Question | Answer | Source |
|---|---|---|
| Who may create/update a Setting? | a user holding `SETTINGS_MODIFY`; server-enforced | `common/documents/setting.mjs` |
| Which clients receive a world-scoped value? | **every connecting client, whatever its role** | `dist/packages/world.mjs`: `db.Setting.dump().then(e => f.settings = e)` in the per-user world payload |
| Does that dump filter? | **No** — `static async dump({sort})` | `dist/database/backend/server-document.mjs` |
| Does the client filter? | No; `game.settings.storage.get("world")` is the delivered collection | `client/game.mjs:67`, `client/documents/collections/world-settings.mjs` |
| Any option giving read confidentiality? | **No.** `client` = `localStorage`; `world` and `user` are both Setting documents in that same dump | `common/constants.mjs`, `client/helpers/client-settings.mjs` |

So the fix cannot be a different setting. **Please verify these readings
independently** — the entire design rests on them.

**Changed.**

| File | What |
|---|---|
| `foundry-module/scripts/settings.js` | `submissionCredential` **deleted**; four non-secret settings remain; the source findings recorded in the header |
| `foundry-module/scripts/main.js` | a `type="password"`, `autocomplete="off"` field in the dialog; `run(action, folderId, credential, settings)`; cleared in `finally` in both `run` and `openSubmissionDialog` |
| `foundry-module/scripts/transport.js` | `missing_credential` message; the credential-as-parameter contract |
| `foundry-module/README.md`, operations §4.1 | the workflow, the Foundry evidence, lifetime, rotation, compromise consequences |

**Named tests** — `foundry-module/tests/settings.test.mjs`:

| Property | Test |
|---|---|
| no secret-shaped setting is registered | `no setting whose name could hold a secret is registered` |
| the setting set is exactly the four non-secret ones | `the exact set of settings is the four non-secret ones` |
| **what every client is vended holds no credential** | `what every client is vended contains no credential` |
| no credential is retrievable through `readSettings` | `readSettings returns no credential for any caller to pick up` |
| registration writes nothing secret-shaped | `registering settings writes nothing secret-shaped through the settings API` |
| **regression guard** | `no module source persists a credential through any Foundry storage API` — fails on `settings.register`/`settings.set` with a secret-shaped key, `localStorage`, `sessionStorage` or `setFlag`, scanning executable code with comments stripped |

The fake `game` models Foundry's delivery honestly: one world store whose entire
contents reach every client. Reading it "as an ordinary player" reads what a real
one would be vended.

`foundry-module/tests/transport.test.mjs` still proves a missing credential is
refused before any request is made.

**Preserved.** Same submit-only `ServicePrincipal`, same single
`foundry:snapshot:submit` scope, no administrator or database credential, no
apply or read power added, revocation by configuration plus reload. Rotation no
longer touches Foundry at all.

**Rotation implication.** Any credential ever placed in a world setting must be
treated as exposed. **None has been issued** — §5.2 has never been run outside
synthetic tests and the module has never been installed — so there is nothing
outstanding today. The rule is documented and applies from the first credential.

**What is NOT established.** The confidentiality boundary is verified against
Foundry's *source*, not against a live second client. Operations §8.1 is the
maintainer-supervised check — submit as GM, then confirm from an ordinary
player's browser in a different profile that the secret is nowhere in the client
state they were vended — and **has not been run**.

**Points I would push on.**

- The credential is now typed into a browser DOM once per submission. A
  malicious module or extension in the GM's browser can observe it. I judge this
  strictly better than every client being *given* it, and Foundry module trust
  is already load-bearing here — but it is a real residual and it is the main
  thing to disagree with.
- The operator workflow changed: paste per submission. Peter's to accept.
- I rejected `scope: "client"` (`localStorage`) storage, which would satisfy the
  letter of the finding while leaving a reusable bearer at rest in a browser
  profile indefinitely. Reasoning is in §5 of the submission.
- A short-lived token exchange is the better long-term answer and is a **second
  HTTP route**, which ADR 0009 reserves as a new decision. Raised for Peter, not
  implemented.

---

## S-B-2 (security) — existing artifact roots and files

**Original.** `mkdir(mode=0o700, exist_ok=True)` controls only a newly created
root; an existing permissive directory was accepted. An existing checksum-named
target was content-verified but accepted without proving it was a regular,
service-owned `0600` file. The permission test used a fresh root and could catch
neither.

**Changed** — `adapters/artifacts/filesystem.py`, with the policy written into
its docstring; `adapters/http/composition.py` calls `ensure_ready()` at startup.

| Subject | Required | Reason code |
|---|---|---|
| configured path | no symlinked component (`normpath` vs `realpath`) | `ValueError` → `ConfigurationError` |
| root | directory (`lstat`, so a symlink is caught not followed) | `root_not_a_directory` |
| root | owned by the effective uid | `root_not_owned` |
| root | nothing granted to group or other | `root_permissive` |
| artifact | `O_NOFOLLOW`, regular file | `artifact_untrusted`, `artifact_not_a_regular_file` |
| artifact | owned by the effective uid | `artifact_not_owned` |
| artifact | nothing granted to group or other | `artifact_permissive` |
| artifact | hashes to its own name | `checksum_mismatch` |

Checked at **startup** and re-checked on **every store**. Artifact checks use one
file descriptor for `fstat` and the read, so the checked file is the hashed file.
Nothing is repaired: refusal only, with the operator commands in operations §5.6.

**Named tests** — `tests/test_artifact_store.py`:

| Required by the handover | Test |
|---|---|
| fresh safe root | `test_a_fresh_root_is_created_private_and_usable` |
| safe existing root | `test_a_safe_pre_existing_root_is_accepted` |
| permissive root | `test_a_permissive_pre_existing_root_fails_closed` (5 modes; asserts **both** startup and per-store refusal) |
| wrong-owner root, safely | `test_a_root_owned_by_another_account_fails_closed` |
| root symlink | `test_a_symlinked_root_is_refused_at_configuration_time`, `test_a_symlinked_parent_of_the_root_is_refused_too` |
| permissive target | `test_a_permissive_existing_target_is_refused_rather_than_served` (store **and** load) |
| non-regular target | `test_a_non_regular_target_is_refused` |
| target symlink | `test_a_symlinked_target_is_refused_and_never_followed` |
| checksum mismatch | `test_an_existing_target_with_the_wrong_content_is_refused` |
| safe idempotent reuse | `test_a_safe_existing_target_is_reused_idempotently` |

Also `test_a_root_that_is_not_a_directory_fails_closed`,
`test_an_existing_target_owned_by_another_account_is_refused`,
`test_no_unsafe_state_is_repaired_silently`,
`test_a_storage_refusal_names_a_reason_and_never_the_path`,
`test_contains_does_not_follow_a_symlink`.

**Every mode is set explicitly in the test**, so nothing depends on `tmp_path`'s
defaults. The wrong-owner cases move *this process's* effective uid rather than
`chown`ing a directory, because the suite must never require or hold privilege;
that is a deliberate substitution and is worth your judgement.

**A defect these tests found.** `_path_for` called `.resolve()`, so a
checksum-named **symlink** was resolved and the store operated on the link's
target — `O_NOFOLLOW` never saw it. It no longer resolves; the name is a
validated hex digest and is contained by construction.

### Second remediation — the checks were all made by pathname

**What the re-review found.** Everything above is real and is still enforced.
What it got wrong is *how*. `_ensure_root()` `lstat`ed the configured path; then
the temporary file, the artifact opens, the `os.replace` and the directory
`fsync` each named that path again. Between the check and each use, an account
able to rename entries in a writable parent could substitute a different
directory, and every operation would follow the name to it. Another pathname
check would have moved that window, not closed it.

**What is there now.** The root is opened **once**, with
`O_DIRECTORY | O_NOFOLLOW`, and every filesystem operation resolves its name
relative to that descriptor: `os.open(..., dir_fd=root)`,
`os.replace(..., src_dir_fd=root, dst_dir_fd=root)`, `os.unlink(..., dir_fd=root)`,
`os.stat(..., dir_fd=root, follow_symlinks=False)` and `os.fsync(root)`. Type,
owner and mode are proved with `os.fstat` **on the descriptor** at startup, on
every store and on every read. `_path_for`'s `Path` arithmetic is gone; an
artifact's name is a bare validated hex digest plus `.json`.

Four decisions in it are the ones I would question if I were reviewing:

| Decision | My reasoning | Where to disagree |
|---|---|---|
| a `root_replaced` refusal when the configured pathname no longer names the anchored directory | fail-closed, and it stops the service silently writing into an inode nobody can name. It is explicitly **not** the safety mechanism | it makes moving the artifact root a restart-requiring operation. Documented in operations §5.6 and `.env.example`, but it is a real operational change |
| ancestors checked **only** at startup | a descriptor cannot observe its ancestors, and re-walking the pathname per request adds exactly the check-then-use window the anchoring removes | a parent that becomes writable while the service runs is not detected. I judge the anchoring sufficient there; say so if you do not |
| reads re-check the root, not only writes | a root that has become group-readable is no longer restricted storage, and continuing to serve Actor mechanics out of it is the wrong way to fail | it means a permission slip breaks the Council preview as well as submission |
| ancestors must be owned by `root` or the service account, not writable by others unless sticky | that is the precondition under which the replacement could be staged at all | it will refuse to start on a deployment whose `/srv/...` chain is owned by a third account. Intended, and worth Peter seeing before deployment |

**Descriptor lifetime.** `close()`, a context manager, and
`Composition.dispose()` calling `close()`; every startup refusal after anchoring
closes it before the exception leaves `build_application`. `__del__` exists as a
documented backstop and nothing depends on it. Proven by
`tests/test_submission_composition.py` and by six lifetime tests in
`tests/test_artifact_store.py` that count the descriptors held **on this store's
root**, rather than counting the process's fds and hoping nothing else moved.

**One behaviour change worth flagging.** A failure to *open* the root used to
surface as `durability_unconfirmed`, because the directory `fsync` was the only
thing that opened it. It now surfaces as `root_unavailable`, before anything is
written. Both refuse the submission and commit nothing, so I-2's guarantee is
intact — but it is a changed reason code and I would want a reviewer to agree it
is the more precise one rather than a quiet weakening.

**Named tests for the second remediation** — `tests/test_artifact_store.py`:

| Required by the handover | Test |
|---|---|
| a store cannot be redirected | `test_a_store_cannot_be_redirected_by_replacing_the_root_pathname`, `test_a_swap_after_validation_still_writes_to_the_anchored_directory` |
| a load cannot read from the replacement | `test_a_load_cannot_read_an_artifact_from_a_replacement_directory`, `test_an_artifact_read_is_anchored_even_when_the_root_name_is_swapped` |
| symlink swap between validation and read | `test_an_existing_target_cannot_be_swapped_for_a_symlink_before_the_read` |
| publication and `fsync` anchored | `test_publication_and_directory_fsync_use_the_anchored_directory` |
| unsafe state still fails closed, no repair | `test_the_root_state_is_rechecked_through_the_descriptor_on_every_store`, `test_a_read_rechecks_the_root_too`, `test_no_unsafe_state_is_repaired_silently` |
| descriptors closed on completion and every failure | the six lifetime tests plus `tests/test_submission_composition.py` |
| retry after `durability_unconfirmed` | `test_a_retry_after_durability_unconfirmed_neither_duplicates_nor_destroys` |
| the ancestor precondition | `test_an_ancestor_another_account_can_rename_entries_in_is_refused`, `test_a_sticky_shared_ancestor_is_accepted` |

The substitution is staged with controlled renames into replacement directories
this account owns `0700`, so owner and mode cannot be what refuses them — the
question each test asks is whether the anchoring kept the operation off the
replacement. The two "swap after validation" tests inject the rename inside
`os.open`, so it happens **after** every check has passed, which is the window a
pathname store would lose.

**What is NOT established.** A genuine cross-account read or replacement
attempt. No test creates a second POSIX user, and none should. The enforcement
is proven against pathname substitution performed by this process, and against
mode, owner and type as this process sees them. The ancestor walk is a startup
check and does not detect a parent that becomes writable later.

---

## I-1 (implementation) — false "nothing was stored" claims

**Original.** Artifact-before-database ordering permits an orphan. The `503`
`database_unavailable` response, the generic `500` and the operations table all
claimed the filesystem was unchanged, giving operators the wrong incident and
retention model.

**Changed.**

| Where | Now |
|---|---|
| `adapters/http/wsgi.py` `500` | "No submission was recorded or confirmed. Retrying with the same Idempotency-Key is safe." |
| `adapters/http/wsgi.py` `503` | "could not be recorded or confirmed. Retry with the same Idempotency-Key: a retry cannot create a second snapshot." |
| `application/foundry/submission.py` | `storage_unavailable`: "could not be **confirmed as** stored, so nothing was recorded … Retrying … is safe."; `SubmissionRefused` docstring states which path can leave bytes |
| `application/foundry/audit_policy.py` | `stored` → `recorded`, with the classification argument |
| `foundry-module/scripts/main.js` | "Nothing was recorded or confirmed." |
| operations §5.7 | table row corrected, with a paragraph on why |
| operations §5.6 | **orphan identification procedure** |
| operations §9 | per-path recovery: which refusals wrote no bytes; what `durability_unconfirmed` means |

**Named tests**: `test_a_database_failure_says_what_it_knows_and_no_more`,
`test_an_unexpected_exception_makes_no_claim_about_the_filesystem` (both
`tests/test_http_submission.py`, both asserting the phrase "nothing was stored"
is **absent**), `test_an_unconfirmed_durability_failure_reports_only_what_it_knows`
(`tests/test_snapshot_submission.py`), and the existing
`test_a_refusal_writes_one_refused_event_claiming_no_state` updated to
`recorded`.

**Orphan handling.** Operations §5.6 gives a read-only `comm` of the store's
filenames against `SELECT checksum FROM foundry_snapshots`, states that nothing
deletes them automatically and that this must not become a cron job, and
explains that a submission about to be retried needs exactly that file. **No
artifact listing or deletion HTTP route was added**; the store still has no
`list` or `delete`. The retention decision is reserved to Peter.

The bounded, no-sensitive-data response policy is unchanged.

**Note for the reviewer.** The `stored` → `recorded` rename touches an
append-only audit payload. No row has ever carried the old key — the action is
new in this uncommitted package and has never been written to a real database —
so this is not a history rewrite. Please confirm that reading.

### Second remediation — the claims the first attempt did not look for

**What the re-review found.** The table above is accurate about the messages it
lists. What was wrong was the word *every*: I searched for the messages the
review had named rather than for the claim, and four more survived. Three are on
paths that run **after** `_store_and_record` has already published bytes:

| Where | Why it was false |
|---|---|
| `submission.py` unresolved-concurrency refusal | the store has run — twice, in the checksum-race branch |
| `submission.py` `_replay_stored`'s unresolvable branch | the store has run, *and* another submission demonstrably recorded something |
| `submission.py` `_replay`'s two refusals | reachable both before and after the store, and the key was spent by a submission whose record is intact |
| `application/artifacts.py` | built "Nothing was stored or served" into **every** `ArtifactStorageError`, including `durability_unconfirmed`, whose contract is that a correct target may already be published |

**What is there now.**

- **`StorageOutcome`**, declared per raise: `UNCHANGED` ("No artifact was
  published, and nothing already held was changed or removed") or `UNRESOLVED`
  ("Whether an artifact is held under that checksum is not established by this
  failure…"). The **default is the conservative one**, so an unclassified reason
  produces a vaguer true statement rather than a stronger false one — and
  `test_every_storage_refusal_declares_what_it_establishes` walks the adapter's
  syntax tree so the default stays a safety net rather than the normal path.
- **Each `SubmissionRefused` says what its own path established.** The post-store
  refusals say *this attempt* recorded nothing and that a retry cannot create a
  second snapshot. The two replay refusals add that the earlier submission's
  record is unchanged — denying that would be the mirror image of the original
  defect.
- **The one genuinely pre-storage refusal is narrow rather than broad**: the
  claimed-digest mismatch says the artifact store was never asked to hold these
  bytes, which is the fact the client can act on.
- **`application/errors.py`** now says "nothing was written **to the database**".
  Those are database errors, but they are raised on a path where an artifact has
  already been written.
- `wsgi.py`'s `incomplete_body` no longer says it either, although that path
  could truthfully have done so.

**The repository-wide regression check** is
`tests/test_storage_claim_vocabulary.py`. It separates asserting the claim from
discussing it — banned in non-docstring Python literals across
`application/`, `adapters/`, `domain/`, `tools/`, `migrations/` and in
`foundry-module/scripts/` with comments stripped; allowed in docstrings, in
comments, and inside quotation marks in `docs/operations/`, `docs/adr/` and
`docs/rules/`; not applied to `tests/` or the review record, because a test that
forbids a phrase has to name it. It carries its own proofs that it catches a
reintroduction and does not ban the explanation.
`foundry-module/tests/claims.test.mjs` applies the same rule from the module's
own suite.

**Named tests for the second remediation.**

| Required by the handover | Test | File |
|---|---|---|
| unresolved uniqueness/concurrency | `test_an_unresolvable_uniqueness_conflict_makes_no_filesystem_claim`, `test_an_unresolvable_key_race_speaks_only_about_this_attempt` | `test_snapshot_submission.py` |
| `durability_unconfirmed` with the target present | `test_an_unconfirmed_durability_refusal_leaves_the_correct_target_in_place`, `test_durability_unconfirmed_makes_no_claim_about_the_filesystem` | `test_snapshot_submission.py`, `test_artifact_store.py` |
| replay paths distinguish attempt from record | `test_a_spent_key_refusal_does_not_deny_the_earlier_submission`, `test_an_unreadable_receipt_refusal_does_not_deny_the_earlier_submission` | `test_snapshot_submission.py` |
| the whole vocabulary, enumerated | `test_no_refusal_this_service_can_raise_claims_the_filesystem_is_unchanged` — raises **every** declared code and fails if one becomes unreachable | `test_snapshot_submission.py` |
| HTTP rendering | `test_every_refusal_reaches_the_wire_with_its_wording_intact`, `test_an_unconfirmed_durability_refusal_reaches_the_wire_truthfully` | `test_http_submission.py` |
| Foundry notification rendering | `no module message tells the GM that nothing was stored`, `a failed submission tells the GM what a retry actually guarantees` | `foundry-module/tests/claims.test.mjs` |
| repository-wide check | all of `test_storage_claim_vocabulary.py` | — |

**Points I would push on if I were reviewing.**

- The markdown rule treats a quoted occurrence as explanation and an unquoted one
  as an assertion. That is a heuristic. It is deliberately narrow — three doc
  directories, and the review record is excluded entirely — but a reviewer may
  reasonably think a textual rule over prose is not worth having.
- A docstring can still contain a false claim, and this check cannot see that.
  What it does buy is that the *messages* cannot carry the phrase at all.
- `application/errors.py` is shared with the Sheet import path, which has no
  artifact store. Adding "to the database" there is more precise everywhere, but
  it is a change outside the submission package and I would rather you saw it
  named than found it.

**What is NOT established.** I-1 is remediated by construction and test. There is
no operational observation behind it, and none is needed — but the incident model
it produces (a `503` or a `409` does **not** mean the store is empty) is
something operations §5.6, §5.7 and §9 now assert and nobody has yet used in a
real incident.

---

## I-2 (implementation) — directory durability failures suppressed

**Original.** `_fsync_directory()` swallowed both open and `fsync` failures after
`os.replace`, then allowed the transaction to commit, contradicting the claimed
ordering.

**Changed.**

| Requirement from the handover | How |
|---|---|
| a directory-open or -`fsync` failure prevents confirmation and prevents the row/receipt/audit success committing | `_fsync_directory` raises `ArtifactStorageError("durability_unconfirmed")`; the store is called inside the unit of work **before** any row is added, so the raise leaves the `with` without committing |
| typed storage failure without leaking the path | fixed reason code, cause dropped by `_dropped`, no path in the message |
| account for the target already being renamed | the already-held branch now `fsync`s the directory too, so the retry establishes the durability the first attempt could not |
| do not delete a correctly published target | the failure path's cleanup names only the *temporary* file, which no longer exists after `os.replace` |
| a platform that cannot support it fails startup | `ensure_ready()` proves directory `fsync` at startup, from the composition root |

**Named tests.**

| Assertion | Test | File |
|---|---|---|
| directory-open failure refuses | `test_a_directory_open_failure_refuses_the_store` | `test_artifact_store.py` |
| directory-`fsync` failure refuses | `test_a_directory_fsync_failure_refuses_the_store` | `test_artifact_store.py` |
| the correct target is not destroyed | `test_an_unacknowledged_durability_failure_does_not_destroy_a_correct_target` | `test_artifact_store.py` |
| the retry completes the guarantee | `test_a_retry_after_a_durability_failure_completes_the_guarantee` (asserts the directory is actually synced) | `test_artifact_store.py` |
| startup proves support | `test_ensure_ready_proves_directory_fsync_before_any_upload` | `test_artifact_store.py` |
| **no database success state commits** | `test_an_unconfirmed_durability_failure_commits_no_database_state` (asserts no snapshot row, no idempotency record, and only a `SUBMISSION_REFUSED` event) | `test_snapshot_submission.py` |
| the response is truthful | `test_an_unconfirmed_durability_failure_reports_only_what_it_knows` | `test_snapshot_submission.py` |
| retry with the same key completes | `test_a_retry_after_an_unconfirmed_durability_failure_succeeds` (one row, one file) | `test_snapshot_submission.py` |

Injection is by `monkeypatch` on `os.fsync`, failing only for descriptors whose
`fstat` says directory, so file `fsync` keeps working and the test exercises the
real code path.

---

## Cross-cutting requirements — how each was kept

| Requirement | Where to check |
|---|---|
| storage failures classify what they establish, rather than inheriting one sentence | `application/artifacts.py` `StorageOutcome`; every raise in `adapters/artifacts/filesystem.py` names one |
| every filesystem operation is anchored to the validated directory descriptor | `adapters/artifacts/filesystem.py`; `Composition.dispose()` owns its lifetime |
| authentication, CORS transport, artifact storage and application policy in their own layers | `cors.py` holds no game rule and reaches no service; `wsgi.py` decides only *where* the policy applies; the storage policy is in the adapter; refusal vocabulary is unchanged in `submission.py` |
| authentication-before-body-read, declared-size-before-body-read | `_submit` unchanged in order. The preflight is routed before `_submit` and reads no body at all |
| uniform authentication failures; audit not an anonymous write channel | `credentials.py` untouched; `test_every_authentication_failure_gives_the_same_message` still passes; no refusal event is written before a principal is established |
| exact-byte hashing, independent validation, content addressing, idempotency, pending-only, Council-only preview/apply | untouched. The preview route gains no CORS surface and stays inert |
| safe logging: no credential, Actor value, artifact byte, raw request, SQL detail or host path | unchanged; `test_an_error_body_carries_no_secret_path_sql_or_actor_value` and `test_a_storage_refusal_names_a_reason_and_never_the_path` cover both ends |
| no weakening of file modes, HTTPS enforcement, checksum verification, migration constraints, append-only behaviour or runtime grants | modes are now *stricter* and enforced; HTTPS and checksum logic untouched; no migration and no grant changed; `alembic check` clean |
| conclusions-without-findings not implemented unless necessarily touched | none was. The only adjacent change is `stored` → `recorded`, which I-1 required |

## Decisions reserved to Peter, not to the reviewer

| # | Decision |
|---|---|
| D-a | Whether a short-lived token exchange should replace the reusable bearer (a second HTTP route; ADR 0009 makes it a new decision) |
| D-b | Whether this process should ever repair storage permissions rather than refuse |
| D-c | Retention policy for database-unclaimed artifacts |
| — | Acceptance of the per-submission credential workflow as the operator experience |
| — | ADR 0009's textual scope mismatch about the inert preview route, raised in the original review's governance section and untouched here |

## Confirmations

- No real credential was used or issued; every credential in this work is
  synthetic. No real player, character or world data was used.
- The installed Foundry **application** source was read, which the handover
  permits. **No world storage, LevelDB store or compendium pack was opened.**
  One disclosure, recorded in §10 of the submission: a directory listing during
  discovery included `/home/foundry/shared/worlds`, returning world *directory
  names* only; nothing in it was opened, and I did not return to it.
- Neither rehearsal was run, and neither new supervised check (§8.1, §8.2) was
  run. No cross-account experiment was performed for S-B-2, and no second POSIX
  account was created.
- The module was not installed and no Foundry world was touched.
- Nothing was committed and nothing was pushed.
- No finding is marked closed, and no phase gate is claimed.

---

# Third remediation — 2026-08-05

Self-contained. Everything above is the first and second attempts.

## Finding 1 (Blocking, security + implementation) — publication could overwrite an entry that was never validated

### Root cause

`store()` decided whether the checksum entry was already this artifact
(`_holds()`), then wrote a temporary file, then published with
`os.replace(temporary, name, src_dir_fd=root, dst_dir_fd=root)`.

`os.replace` is atomic about **replacing**. Anything appearing under the checksum
name between the check and the rename was removed and overwritten with nobody
having looked at it. The second remediation's anchoring is not a defence here: it
proves the operation stayed inside the approved directory, which was never the
question.

The window is the ordinary case for this design, not an exotic one. Decision D5
stores the artifact before committing the row so that retried and concurrent
submissions are safe, and the store is content-addressed so that two submissions
of identical bytes meet on one name. Concurrency at that name is what the design
is *for*.

Violated simultaneously: artifacts are immutable and content-addressed; an unsafe
or mismatched target is refused rather than repaired; unexpected evidence is
preserved for an operator; no existing artifact is implicitly deleted;
publication is safe under concurrency.

### Changed files

| File | What |
|---|---|
| `adapters/artifacts/filesystem.py` | `_publish()` and `_link()` replace the `os.replace` call; `_discard()` refuses any name without the temporary prefix; `_prove_publication_refuses_to_overwrite()` added to `ensure_ready()`; `_PUBLICATION_ATTEMPTS` and `os.link` added to the `dir_fd` probe; the "Publication never overwrites" docstring section |
| `.env.example` | the hard-link requirement and `link_unsupported` |
| `docs/operations/foundry-snapshot-submission.md` | §5.6 "Publication never overwrites an entry the service has not validated"; the refusal table gains `link_unsupported` and `publication_unsettled`; §9 gains "An unexpected entry under a checksum name" |

### The structural guarantee now provided

Publication is `os.link(temporary, name, src_dir_fd=root, dst_dir_fd=root,
follow_symlinks=False)`. `linkat(2)` **creates the destination entry or fails
`EEXIST`**. There is no mode in which it removes what is already under the name,
and the test and the creation are one kernel operation — which is why a pathname
existence check followed by `os.replace` was not an option and why the review was
right to name it as the same race in a different shape.

| Requirement from the review | How it is met |
|---|---|
| absent target: exactly one writer publishes atomically | the kernel serialises entry creation; the loser gets `EEXIST` |
| existing or concurrently appearing target: opened through the anchored descriptor and fully revalidated for type, owner, mode and checksum | the `EEXIST` branch calls the **same** `_holds()` that runs before the write: `os.open(name, O_RDONLY \| O_NOFOLLOW, dir_fd=root)`, `os.fstat` on that descriptor, read and hash from that descriptor |
| a mismatched, symlinked, non-regular, permissive or wrong-owner winner is refused and preserved unchanged | `_holds()` raises; the caller discards only the temporary; nothing repairs, replaces or removes the entry. `StorageOutcome.PRESERVED` states it |
| two concurrent writers of identical content converge on one valid artifact | the loser revalidates the winner's file and returns its reference |
| no pathname-based fallback | there is none. `os.link` is the only publication call and both ends carry a `dir_fd` |
| ~~no temporary survives success or an ordinary failure~~ **false as written; corrected below** | ~~`_discard` runs on the success path and on both failure paths~~ — running `_discard` is not removal. It swallows `OSError`, so this row claimed a guarantee the implementation never made. Found by the third re-review as **I-3R-1** and corrected in the fourth remediation; see the corrected row beneath this table |
| a cleanup failure cannot delete the published target | `_discard` returns without unlinking unless the name starts with `.incoming-`. Structural, not a convention |
| directory durability after **all** publication-related directory-entry changes | order is: link → discard temporary → `fsync(root_fd)`. One sync covers the creation and the removal |
| `durability_unconfirmed` preserves a correctly published target for retry | unchanged from I-2, and now also true when the target is another writer's |
| retry remains content-idempotent | `_holds()` at the top of `store()` finds it, re-verifies it, re-syncs the directory, returns the same reference |

**The corrected temporary-cleanup row** (I-3R-1, fourth remediation, 2026-08-05):

| What is actually guaranteed | Why |
|---|---|
| publication never removes or overwrites the final checksum entry | `os.link` creates or fails `EEXIST`; `_discard` returns without unlinking unless the name starts with `.incoming-` |
| cleanup can only ever name an internally generated `.incoming-*` entry | the prefix is checked before the `unlink`, and every caller supplies a name this process generated |
| temporary cleanup is **best effort** | `_discard` swallows `OSError` and reports nothing, so `store()` does not know whether the temporary was removed |
| a failed cleanup does not invalidate or delete a correctly published artifact | the checksum entry exists and has been proved before `_discard` runs; a failure there changes nothing about it, and the submission still succeeds |
| a failed cleanup **may leave a private, unservable hard link consuming storage** | proved by `test_a_failing_cleanup_leaves_the_published_artifact_alone`, which asserts exactly one surviving `.incoming-*` file after a *successful* store |
| operator hygiene detects and handles such leftovers | operations §5.6, "Temporary files left by a failed cleanup" — read-only, age-bounded, link-count-aware. Proved against synthetic files by `test_the_hygiene_rule_finds_a_leftover_a_successful_store_left`, `test_the_hygiene_rule_reports_one_link_for_an_unpublished_leftover` and `test_the_hygiene_rule_does_not_match_an_artifact_or_a_submission_in_flight` |

No statement anywhere in this package now promises zero surviving temporaries
unless its preconditions explicitly exclude cleanup failure and a test proves
those preconditions — which is true of exactly two assertions,
`test_two_writers_of_identical_bytes_converge_on_one_artifact` and
`test_the_startup_probe_leaves_nothing_behind`, both of which now say so.

`publication_unsettled` covers `EEXIST` followed by an absent entry, three times.
Nothing in this store removes an artifact, so production cannot reach it; the
bound exists so that a filesystem which reaches it anyway refuses rather than
spins inside a request.

**`renameat2(RENAME_NOREPLACE)` was considered and rejected**, per the review's
instruction to document the trade rather than take it silently. It gives the same
guarantee in one syscall, but the standard library exposes no wrapper, so it
means a hand-rolled `ctypes` `syscall(SYS_renameat2, …)` stub with manual
argument marshalling in the path that stores every exported Actor's mechanics,
plus a silent narrowing to Linux with a specific kernel. One extra `unlink` on a
path that already performs two `fsync`s is the cheaper trade. Recorded in the
adapter docstring, operations §5.6 and package-plan item D10. **If the reviewer
disagrees, this is the decision to send back to Peter.**

### Named regression tests

All in `tests/test_artifact_store.py`, section "publication never overwrites an
unvalidated entry". The review's nine required proofs, mapped:

| Required | Test |
|---|---|
| 1. valid target appearing after `_holds()` is not overwritten and is reused | `test_a_valid_target_appearing_before_publication_is_reused_not_overwritten` — asserted by **inode**, since equal bytes pass under the old implementation too |
| 2. invalid/mismatched target refused, exact bytes and metadata unchanged | `test_a_mismatched_target_appearing_before_publication_is_refused_intact` (bytes, mode and inode), `test_a_permissive_target_appearing_before_publication_is_refused_intact` |
| 3. symlink or non-regular target refused without following or replacing | `test_a_symlinked_target_appearing_before_publication_is_never_followed`, `test_a_non_regular_target_appearing_before_publication_is_refused` |
| 4. two concurrent writers of identical bytes → one artifact, and — with both cleanups succeeding, which the test allows — no surviving temporary | `test_two_writers_of_identical_bytes_converge_on_one_artifact` |
| 5. publication stays anchored if the root pathname is replaced during the operation | `test_publication_stays_anchored_when_the_root_name_is_taken_over`, plus the retained `test_a_swap_after_validation_still_writes_to_the_anchored_directory` and `test_publication_and_directory_fsync_use_the_anchored_directory` |
| 6. injected publication failure removes only the temporary | `test_a_failed_publication_cleans_up_and_publishes_nothing`, `test_cleanup_can_only_ever_remove_a_temporary`, `test_a_failing_cleanup_leaves_the_published_artifact_alone` |
| 7. injected directory-sync failure after successful publication leaves the target present | `test_an_unacknowledged_durability_failure_does_not_destroy_a_correct_target` (retained, I-2) |
| 8. retry after `durability_unconfirmed` validates and reuses without duplication or destruction | `test_a_retry_after_durability_unconfirmed_neither_duplicates_nor_destroys`, `test_a_retry_after_a_durability_failure_completes_the_guarantee` (both retained, I-2) |
| 9. the tests fail against the unconditional-`os.replace` implementation | **checked, not assumed: 10 failed, 81 passed.** Reproduce it with the recipe in "The two runs that are not in the standard list" above |

Plus `test_a_startup_probe_proves_publication_refuses_to_overwrite` and
`test_the_startup_probe_leaves_nothing_behind` for `link_unsupported`.

Synthetic data only. No privilege, no second POSIX account.

**How the window is entered deterministically, and why it is not circular.** The
hook is the *verification re-read of the temporary file* — an `O_RDONLY` open of
a `.incoming-*` name, which is the last thing that happens before the entry is
created, in any implementation of publication. No test names `os.link`. That is
what lets requirement 9 be checked at all: the tests describe the contract, not
the current code.

### Configuration and operational effects

- **the artifact root must be on a filesystem supporting hard links** — ext4,
  XFS, Btrfs, ZFS, tmpfs; not FAT/exFAT or some network mounts. `ensure_ready()`
  links a probe file, links it a second time, and requires the second attempt to
  fail `EEXIST`; otherwise it refuses `link_unsupported` at startup. `.env.example`
  and operations §5.6 state it;
- **two new refusal reasons**: `link_unsupported` (startup) and
  `publication_unsettled` (per store). Both are in the §5.6 table;
- no route, no capability, no schema change, no new environment variable.

### Rollback and recovery behaviour

- **rollback**: the working tree is uncommitted. Reverting
  `adapters/artifacts/filesystem.py` restores the previous behaviour and the
  defect with it; no data migration and no on-disk format change is involved.
  Artifacts written by either implementation are byte-identical files under the
  same names;
- **recovery**: operations §9 gains "An unexpected entry under a checksum name",
  reached by `checksum_mismatch` or any `artifact_*` refusal from a store. It is
  read-only, its first instruction is **do not delete**, and it distinguishes a
  wrong-bytes file (probably a storage fault or partial restore) from a symlink
  or non-regular entry (**treat as a security incident**). The orphan procedure
  in §5.6 is unchanged, still read-only, and D-c is still Peter's.

### Residual risks

- convergence is proven **deterministically**, by running a second store object
  inside the first's publication window on the same root, not by a multi-process
  stress test. The code path is the same one two processes take;
- the `EEXIST` guarantee is the **kernel's**. The store proves at startup that
  the configured filesystem provides it, which is better than citing `linkat(2)`,
  and it is still a platform property rather than a property of this code;
- `publication_unsettled` is unreachable by any state this service can produce
  and is therefore tested by construction only;
- the hard-link requirement can refuse to start a deployment. Intended,
  documented, registered as R-17.

## Finding 2 (Important) — the failure vocabulary's default made an unproven claim

### Root cause

The second remediation made what a failure claims a declared `StorageOutcome`
per raise. `UNRESOLVED` — the **default**, and therefore the sentence every
unclassified path inherits — still asserted "Nothing already held was changed or
removed", which Finding 1 made false. A default is the wrong place for a positive
claim about durable state, because it speaks for paths nobody has examined.

### Changed files

`application/artifacts.py` (the enum and the module docstring),
`adapters/artifacts/filesystem.py` (`PRESERVED` threaded through
`_read_trusted`, `_require_trusted_artifact`, `_holds` and `load`),
`docs/operations/foundry-snapshot-submission.md` §5.7.

### The structural guarantee now provided

The rule, stated in the module docstring: **a conservative default may state what
is structurally true of a content-addressed store; it may not make a positive
claim about what is on the filesystem.**

| Outcome | Sentence | Provable on every path that raises it because |
|---|---|---|
| `UNCHANGED` | "No artifact was published, and no artifact already held was changed or removed." | every such raise is before publication: root state, platform support, `write_failed`, `publication_unsettled`, verification of this attempt's own temporary, `ArtifactNotStored` |
| `PRESERVED` | "No artifact was published. An entry was already present under that checksum and was refused; it has been left exactly as it was found, so that it can be examined." | raised only from `_holds()` and `load()` — the two places an entry exists under the checksum name — and nothing on either path repairs, replaces or removes it |
| `UNRESOLVED` (default) | "Publication under that checksum may or may not have completed, and its durability was not confirmed. Retrying the same content is safe: the store is content-addressed, so a retry resolves to the same artifact and cannot create a second one." | claims nothing positive; the retry-safety clause follows from content addressing, which is structural |

The outcome is chosen by the **caller**, not by the reason code, because the same
three refusals mean different things depending on what was being examined:
`_verify_written` is reading this attempt's own temporary and passes `UNCHANGED`;
`_holds()` and `load()` pass `PRESERVED`.

`PRESERVED` is the review's requirement that a failure after detecting a
concurrent target distinguish a validated existing artifact from an unsafe entry
that was preserved. A validated one is not a failure — it is reused and the
submission succeeds — so the distinction that needed making is between "there was
nothing there" and "there was something, it was refused, and it is still there".
Those send an operator to different procedures.

**The repository-wide phrase check is retained as defence in depth and is
explicitly not offered as proof.** The review is right that it establishes
nothing semantic. Nothing in the submission, this request, the change log, the
status record or the RAID register claims I-1 was closed by a textual scan; the
correction to the earlier claim is in submission §13.2 and package-plan §9 rather
than made by editing the earlier text.

### Named regression tests

- `test_the_conservative_default_claims_nothing_about_durable_state` — the
  finding itself: `UNRESOLVED` contains no "nothing already held", no
  "unchanged", no "changed or removed";
- `test_a_preserved_entry_is_distinguished_from_having_found_nothing`;
- `test_durability_unconfirmed_makes_no_claim_about_the_filesystem` (retained,
  strengthened);
- `test_a_pre_publication_failure_may_say_it_published_nothing`;
- `test_an_unclassified_reason_defaults_to_claiming_nothing`;
- `test_every_storage_refusal_declares_what_it_establishes` — the AST walk,
  retained, with `link_unsupported` and `publication_unsettled` added to the
  reason vocabulary;
- **and the behaviour tests the review asked for, tied to filesystem state**:
  every `outcome is StorageOutcome.PRESERVED` assertion in the publication-race
  group is accompanied by an assertion that the refused file's bytes, mode and
  inode are unchanged. That is what makes the sentence true rather than merely
  present.

### Configuration and operational effects

Message text only. Operations §5.7 now carries the three sentences as a table
mapping what a refusal says to what it means and what to do. No status code, no
reason code and no API shape changed.

### Rollback, recovery, residuals

Rollback is reverting two files; no persisted data carries these sentences.
Recovery is unaffected. Residual: the phrase check remains textual and a
docstring can still contain a false claim — argued, not fixed, in submission
§12.1 §6.1, and unchanged by this remediation.

## Finding 3 (Important) — the automated evidence was not reproducible

### Root cause

`_require_trusted_ancestors()` walks to `/` and accepts only `root`- or
service-owned ancestors. On the review host `/` and `/tmp` are owned by uid
65534, so **32 tests were refused before reaching their own assertions** — tests
about publication, durability, anchoring and descriptor lifetime, none of them
about ancestors. `--basetemp` cannot help: every absolute path has host
ancestors. The submitted figure of 1912 was therefore not independently
reproducible, which makes it not evidence.

### Changed files

`adapters/artifacts/filesystem.py` (`TrustedAncestors` extracted as a class with
an optional `ceiling`; the store takes it through the constructor and exposes it
as a property), `adapters/http/composition.py` (an `ancestors` keyword),
`tests/test_artifact_store.py`, `tests/test_submission_composition.py`,
`docs/operations/foundry-snapshot-submission.md` §5.6.

### The structural guarantee now provided

| Review requirement | How |
|---|---|
| retain explicit integration tests that the real configured path is checked against actual ancestor ownership and mode | `test_the_production_walk_checks_the_real_configured_path` computes the verdict independently from `os.lstat` and requires the store to agree — so it is a real check on a conventional host **and** correct on a host where `/tmp` is owned by `nobody`. `test_the_production_composition_walks_to_the_filesystem_root` does the same through `build_application` |
| isolate ordinary artifact, race, durability and descriptor-lifetime tests from host ancestor ownership | those tests bound the walk at pytest's `getbasetemp()`. Below it the production rule runs against real directories the test created; above it, nothing |
| a focused fixture or injected ancestor-policy boundary | `TrustedAncestors`, injected through the constructor. The `ancestors` and `anchored` fixtures are the only places a test supplies one |
| keep direct tests for trusted, untrusted, sticky, writable, wrong-owner, symlinked and non-directory ancestors | all present in "the ancestor rule, tested directly", on real directories with real modes: trusted, untrusted (5 modes), sticky (3 modes), wrong-owner, non-directory, symlinked, absent, and `root`-owned via `/` |
| tests intended to exercise publication or lifecycle cannot all fail earlier at the ancestor gate | verified by running the whole suite under the review host's ownership: **1941 passed** |
| do not globally monkeypatch `os.stat`/`os.lstat` so broadly that target or root checks stop testing real behaviour | **nothing is monkeypatched at all** for the ancestor rule now. The two tests that previously patched `os.lstat` for one path set real modes instead, and the wrong-owner case moves this process's `geteuid` so the real `st_uid` comparison does the real work |
| document any environmental prerequisite that cannot be isolated | operations §5.6, "a genuine environmental prerequisite remains": the deployment must satisfy the rule, `/srv` and `/srv/freedom` must be `root`- or service-owned, and a host whose `/` or `/tmp` is owned by a third account **will refuse to start, intentionally**. Registered as R-17 |

**The bound is a test seam and cannot become a deployment one.**
`build_application` accepts it only as a keyword, exactly as it already accepts
`deployment`; there is no environment variable; and
`test_an_unbounded_rule_is_the_production_default` plus
`test_the_production_composition_walks_to_the_filesystem_root` assert that
configuration alone produces the unbounded walk.
`test_the_walk_stops_at_the_ceiling_and_not_before` asserts what the bound
excludes, in order, rather than leaving it to be assumed.

**The production owner rule was not changed.** The review said weakening it would
be a security-policy decision for Peter and the independent reviewer rather than
a drive-by test fix. I agree and did not take it, and I am not proposing it.

### Configuration and operational effects

None. No environment variable, no deployment change. The prerequisite the rule
imposes is unchanged and is now stated explicitly rather than implied.

### Rollback, recovery, residuals

Rollback is reverting the policy extraction; the rule's logic is unchanged, so no
deployment behaves differently either way.

Residual, and the one I would most like the reviewer to disagree with if they are
going to: **the bounded walk is a real reduction in what the storage tests
observe.** They no longer notice a host with a hostile parent chain. The
production walk is exercised separately and unbounded, and the alternative —
tests that fail for a reason unrelated to what they assert — is not evidence
either. But it is a judgement call and it is mine, not the reviewer's.

## What the third remediation does not establish

Everything in submission §12.3 stands, and in addition §13.4. Summarising the
evidence still requiring supervised observation, none of which this work
advanced:

| Evidence | State |
|---|---|
| operations §8.1 — the credential is absent from the state a live second Foundry client is vended | **not run.** Needs Peter. `curl` cannot substitute |
| operations §8.2 — a real browser origin passing and failing the preflight | **not run.** Needs Peter. `curl` does not enforce CORS |
| a cross-account experiment against the artifact root | **not run**, and no automated test may create a second POSIX account or require privilege |
| a multi-process concurrency test of publication | **not run.** Convergence is proven deterministically instead |
| rehearsals §6 and §7 | **neither run** |
| formatter, linter, type checker | **none configured, none installed, none run.** Standing gap |

## What I am asking for

**Implementation re-review:**

1. **the publication fix** — is `os.link` plus revalidation actually
   create-if-absent for the final directory entry, is the durability ordering
   right, and is `_discard`'s prefix guard sufficient?
2. **I-1** — is every outcome sentence provable on every path that raises it, and
   is `PRESERVED` the right distinction rather than an extra concept?
3. **the test evidence** — does the suite reproduce for you now, and do the
   publication tests describe the contract rather than the implementation?
4. **I-2** — is the durability behaviour intact through the publication change?

**Security re-review:**

1. **final-target publication** — can any sequence still remove or overwrite an
   entry this process has not validated? The `EEXIST` branch, `_discard`, the
   startup probe and `publication_unsettled` are where I would look;
2. **preservation of the root anchoring** — has any operation regressed to a
   pathname? The ones deliberately left are
   `_require_configured_path_unchanged` (divergence detector, grants nothing),
   `TrustedAncestors` (startup only), `_create_root`'s `Path.mkdir`, and the
   constructor's `normpath`/`realpath` comparison;
3. **preservation of S-B-1 and S-I-1** — the credential is still absent from
   every Foundry-persisted state and the CORS policy is still bounded and exact.
   Neither was touched by this remediation.

Please also say whether the `renameat2` trade in Finding 1 and the bounded
ancestor walk in Finding 3 are acceptable, or whether either should go to Peter
as a decision rather than an implementation choice.

**No finding is closed here, and no gate is claimed.** Peter Duscha records those
decisions after both independent recommendations and the outstanding supervised
checks.
