# P3.5 remediation — canonical cumulative handoff

**Round 6 (R35-32…R35-36). Updated 2026-08-23.**

**This is the single current handoff for the P3.5 C35/R35 remediation.**
`phase-3-p3-5-r35-remediation-handoff.md` is superseded and now redirects here.

**Date:** 2026-08-23 · **Author:** Claude, P3.5 backend/integration Technical Lead

**Requested:** another independent Codex implementation review and a distinct
security-focused review. **Not requested:** acceptance, or Gemini release.

---

## 1. Blockers first

| # | Blocker | Owner |
|---|---|---|
| ~~B-1~~ | **The shell contract is implemented, and three boundary defects found in review are fixed** (§6). Derived from the **final** context, attached **before** the capability decision, with a server-owned home destination. 28 request-boundary cases added | Claude — done |
| **B-6** | **Gemini remains unreleased**, pending Codex acceptance of the backend contract and the revised prompt | Codex, then Peter |
| **B-7** | **Cloudflare origin ingress is unrestricted.** The `CF-Connecting-IP` rewrite alone does not establish a trusted client address | Peter, deployment gate |
| **B-2** | **The gate password is spent and has never been rotated.** The first two versions of the rotation script could not run at all. It works now, but rotation is a host action | **Peter** |
| **B-3** | **The deployed host still proxies `/healthz` and still holds the inline verifier.** The repository artifact is fixed; the host is not | **Peter** |
| **B-4** | **Both emergency credentials remain unproven.** They were created under `residentKey: preferred`; discoverability is not recorded anywhere and cannot be inferred. Re-enrollment is required before the supervised browser login | **Peter** |
| **B-5** | Origin ingress is not restricted to Cloudflare ranges, so the `CF-Connecting-IP` rewrite **does not** establish a trusted client address | **Peter**, deployment gate |

**Gemini remains unreleased.** Nothing here closes I-06, A-05, A-06, R-23, F-15 or
F-17, and no Phase 3 gate decision is requested.

## 2. Finding map

| Finding | State | Files | Evidence |
|---|---|---|---|
| C35-01 verifier in a repository artifact | Fixed | `infra/caddy/freedom-blades-test.caddy`, `.gate.example`, `infra/staging/rotate-test-gate.sh` | §3.1, falsified |
| C35-02 `/healthz` published by Caddy | Fixed in repository | `infra/caddy/freedom-blades-test.caddy` | §3.2, falsified |
| C35-03 live privilege evidence | Fixed | `tests/test_runtime_grants_live.py` | §3.3, falsified |
| C35-04 health robustness | Fixed | `application/web/startup.py` | §3.4, falsified |
| C35-06 discoverable credentials | Ceremony fixed; existing pair unproven | `infra/ceremony/passkey-registration.html` | §3.5 |
| C35-05 / R35-11 / R35-17 shell contract | **Implemented** | `application/web/shell.py`, `adapters/web/app.py`, both preambles, `includes/header.html` | §6, 21 tests |
| R35-08 script unusable, plaintext in argv | Fixed | `infra/staging/rotate-test-gate.sh` | §4.1, falsified |
| R35-09 hermetic script tests | Added | `tests/test_rotate_test_gate_script.py` | §4.2 |
| R35-10 endpoint-level health evidence | Added | `tests/web/test_health_kill_switch_robustness.py` | §3.4, §5 |
| R35-13 interruption transaction safety | Fixed | `infra/staging/rotate-test-gate.sh` | §4.3, falsified |
| R35-14 bounded verifier backups | Fixed | same | §4.4 |
| R35-15 hermetic failure-path tests | Added | `tests/test_rotate_test_gate_script.py` | §4.2 |
| R35-16 non-skipping ASGI evidence | Explained with exact counts | — | §5 |
| R35-18 one canonical handoff | This document | — | §1 |

## 3. C35 remediations (unchanged, not regressed)

### 3.1 No credential material in the repository

The gate is `import /etc/caddy/freedom-blades-test.gate`, a host-local fragment.
The import **fails closed**: `caddy adapt` on the repository artifact exits
non-zero without it, exit 0 with a stand-in.

**History, verified:** the file is untracked on every branch, but a harness
checkpoint commit (`refs/claude/checkpoint-e3e17315`) snapshotted it, so the
verifier **did** enter Git history. It is on no branch and no remote-tracking ref;
`refs/claude/*` is not pushed. Local-only reach — but it was read during review, so
the password is spent regardless (B-2).

`tests/test_deployment_artifacts.py`: bcrypt, argon2, sha-crypt, private-key blocks
and bearer tokens across every repository Caddy artifact; failure messages name the
artifact and the *class*, never the match.

### 3.2 Health is not publishable

The **first** handle block refuses `/healthz`, `/healthz/` and `/healthz/*` with a
bare `404` — not `403`, which would distinguish "forbidden" from "absent".
**Ordering proved in the adapted configuration:** health at route index **2**,
`reverse_proxy` at **9**. Operational health and TC-PERF-03 read the loopback
endpoint on the host.

### 3.3 `alembic_version` proved by PostgreSQL

Six live cases under `SET ROLE`: the exact S-14 query succeeds;
`has_table_privilege` true for `SELECT`, false for the four write classes; each
write attempted for real and refused with SQLSTATE `42501`; hostile `PUBLIC` grants
removed by applying the template. The table is **not** in the ORM metadata and was
not added to one.

### 3.4 Health degrades rather than breaking

`_kill_switch_absent()` guards `OSError` and returns `False` — **fails closed**. A
process that cannot see its switch cannot report it is off. Ten tests: three
`OSError` classes at the helper, and three ASGI-boundary cases proving `degraded`,
`kill_switch: false`, the exact `{status, checks, version, environment}` shape, and
no path, errno, exception or traceback. The falsification is kept as a test.

### 3.5 Discoverable credentials

`residentKey: 'required'` **and** `requireResidentKey: true`, user verification
`required`, empty `allowCredentials` preserved as the control it is. **The two
enrolled credentials cannot be proven discoverable** — `webauthn_credentials`
records no resident-key state — so B-4 stands.

## 4. R35 remediations

### 4.1 The script could never have run

Reproduced before fixing: `tr -dc … | head -c 20` under `pipefail` exits **141**.
Generation now reads one finite block (665 characters observed) and takes the
substring in the shell. Plaintext is fed on **stdin**, newline-terminated — the
interface was established by running it, not read from help text:

- without a terminator, `Error: EOF`;
- with one, a 60-character `$2a$14$` verifier.

**Round trip verified against a real Caddy** serving `basic_auth` with that
verifier on loopback with `admin off`: exact password **200**; password with a
trailing newline **401**; wrong password **401**; no password **401**. So the
terminator is stripped, not hashed. The probe configuration was deleted; no
password, verifier or hash from it appears anywhere.

### 4.2 The script is executed, not read

`tests/test_rotate_test_gate_script.py` — **24 cases**, running the real script
against a temporary filesystem with controlled `caddy`, `systemctl`, `getent`,
`id` and `chown`. No real `/etc`, service or credential is touched. Assertions
report shapes — lengths, character classes, presence — never values.

Signal tests use a **deterministic synchronization hook**: the fake `caddy
validate` announces that it has been reached and blocks, so the test signals at a
known transaction point rather than guessing a delay. The signal goes to the
process group, as a terminal's Ctrl-C would, because Bash defers its trap until the
foreground child returns.

### 4.3 Interruption is transaction-safe

Three explicit states — `none`, `candidate`, `committed`. Rollback restores the
exact pre-run state from the first two and is a **no-op** once committed. It is
idempotent, captures `$?` first so it cannot mask the failure that triggered it,
and runs on ordinary failure, `EXIT`, `INT` and `TERM`.

The defect: previously a signal after the atomic `mv` left an unvalidated verifier
on disk whose password had never been shown, and a later unrelated reload would
have activated an unknown gate.

**Falsified**, with the mutation asserted before the result was interpreted:
removing the restore block (occurrences 1 → 0, checked) fails 4 interruption tests;
restoring it (0 → 1, checked) passes all 24.

### 4.4 Backups are bounded on every path

The rollback copy is transaction-owned, named distinctly, and always removed —
deliberately **not** the retained recovery generation. A retained generation is
created **only on successful commit**, and exactly one is kept. Failure paths
create none. Tests cover repeated validation failures, repeated reload failures and
interruption, plus proof that a pre-existing retained generation survives a
rollback that still needs the working gate.

## 4a. R35-19 — the post-commit password-loss window

The sequence was: reload succeeds → `STATE=committed` → fallible retention work
(`mv`, `find`, `sort`, `rm`) → print the password. Under `set -e` any failure in
that middle step exited with **the new gate already serving and its plaintext
never shown** — locking the operator out of a door only they were meant to hold.

The password is now displayed immediately after a confirmed reload, before any
housekeeping. Retention runs afterwards with `set -e` suspended for that block
alone, each step reporting for itself, and a failure produces a warning that names
what could not be tidied — never a verifier, and never a second printing of the
password.

**Evidence:** eight new injection cases, one per fallible tool in both directions
(password still shown; warning carries no verifier and the password appears
exactly once), plus proof that a housekeeping failure does not roll back a gate
Caddy has already reloaded. **Falsified**: restoring the old ordering fails six.

## 5. R35-16 — the ASGI skip, explained exactly

Codex saw `35 passed, 4 skipped`. Reproduced precisely:

```
$ ./venv-web/bin/python -m pytest -q -rs tests/web/test_health_kill_switch_robustness.py
SKIPPED [2] …:83: TEST_DATABASE_URL is not configured for a disposable PostgreSQL database.
SKIPPED [1] …:105: …
SKIPPED [1] …:133: …
6 passed, 4 skipped

$ TEST_DATABASE_URL=postgresql+psycopg:///freedom_test ./venv-web/bin/python -m pytest -q -rs …
10 passed
```

**The database boundary is intrinsic, not incidental:** `/healthz` *checks the
database*, so constructing the production app and exercising the real endpoint
requires an engine. Option 2 of R35-16 therefore applies — run against the guarded
disposable database and record exact non-skipped evidence, which is the second run
above: **10 passed, 0 skipped.** The four ASGI cases exercise the real `/healthz`
response boundary, not the helper.

## 6. The shell contract — implemented, then corrected in review

**`application/web/shell.py`** — a typed, immutable `ShellView` with a closed
`ShellNav` vocabulary, built at the request boundary.

### 6.1 Three defects Codex found, and what each was

**R35-20 — it read the wrong authority.** The preamble produces two: `gate.context`,
captured when the session opened, and `context`, returned after a membership
refresh and handed to `authorize()`. The shell read the first. A caller whose
Council role had just been removed would keep Council navigation while the routes
refused them. Now built from the final `context`. **Falsified**, with the mutation
asserted both ways: reverting to `gate.context` fails three refresh cases.

**R35-21 — it was attached too late.** `request.state.shell` was set *after*
`authorize()` succeeded. A valid authenticated caller denied a route gets a
rendered 403, and that page was receiving the **anonymous** frame: "Login" offered
and sign-out hidden, mid-session. Now attached after context resolution and before
the decision. **Falsified**: moving it back fails two denial cases.

**R35-22 — the brand link was a literal.** The header hard-coded `/v1/characters`
for any authenticated caller, which R-20 refuses to an administrator-without-Council
and to continuity scope. `ShellView.home_href` is now server-owned and is always
one of that caller's own offered destinations.

### 6.2 A fourth, found by writing the tests

The navigation rules had been derived from the **prose** matrix — "R-20: `M`, `C`,
`CA`" — and that produced a frame offering `Characters` to an administrator who is
also a guild member. The service rule is `access_control._member_read`: membership
required, and an administrator who is *not* also Council refused. The rules now
mirror the services rather than paraphrase the table, and the request-boundary
tests are what caught the difference — a probe of all seven states against four
routes showed the routes and the frame disagreeing.

### 6.3 Evidence

| Level | Where | Count |
|---|---|---|
| Unit / typed contract | `tests/web/test_shell_navigation_contract.py` | 30 |
| **Request boundary** | `tests/web/test_shell_request_boundary.py` | **28** |
| Template / structural | `tests/web/test_p3_4_shell_and_components.py` | 48 |

The request-boundary module runs the real preamble, session resolution, refresh
branch, `authorize()`, `RequestAuthority.render()`, the template and the logout
route, against the guarded disposable database. It covers anonymous, malformed,
expired and revoked sessions; all seven authenticated states; authenticated 403
rendering for three role combinations; logout with the rendered token; refusal of
missing, empty, wrong and **another session's** token; refresh adding and removing
authority; and the two cases that hold presentation and authorization apart.

**Stated rather than implied:** TC-SHELL-15 drives the refresh at the `_close`
seam, not through a real provider round trip — `_refresh_plan()` returns `None`
without a stored OAuth token grant and the seeded callers have none. An end-to-end
Discord refresh is **not** exercised. And no browser has rendered this frame:
TC-UI-01/02 remain Not Run.

### 6.4 Round 5: the shell lifecycle completed

**R35-26 — public full pages rendered the anonymous frame to everybody.** They run
no protected preamble, so a signed-in caller visiting `/v1/login` or
`/v1/auth/emergency` was offered "Login" and shown no way to sign out. That was the
remaining half of F-17.

`_attach_public_shell()` gives those pages the caller's own frame. **Exactly one
owner per route class:** a protected route's preamble attaches its shell, a public
page attaches its own, and no request resolves its session twice. It authorizes
nothing and refreshes nothing — drawing a header must not make a provider call.

**A correction found while testing it:** the first version keyed "is this authority
current?" off `gate.refresh`, which is `None` whenever no provider token is stored.
It therefore reported a stale Council caller as fresh and handed them the full
frame. It now reads the projection's own freshness. The test caught it; the code
review had not.

**R35-27 — a failed refresh rendered a 503 with the anonymous frame.** A Discord
outage mid-session told a caller with a live session that they were signed out.
The refusal path now attaches the **conservative session-only shell**: sign-out
available, and exactly the one destination that needs no capability. Not the
caller's full frame — the refresh that would have revalidated their capabilities is
precisely what failed, so no privileged link may stand on it.

**R35-28 — housekeeping failures were swallowed.** `find` and `sort` ran inside a
pipeline whose status nobody inspected, so their failures were silently ignored and
superseded verifier generations accumulated while the operator was told nothing.
Each step is now a controlled operation with its own status, and each failure is
named by operation class — never a verifier, never a second printing of the
password, and never reported as a failed rotation.

**Falsified, all three**, with the mutation asserted before the result was read:
removing the public attach fails eight cases; removing the refusal-path shell fails
the degraded case; restoring the swallowing pipeline fails three warning cases.

### 6.5 Round 6: session absence is not infrastructure failure

`_attach_public_shell()` caught every `Exception` and returned, with a comment
asserting that any failure to resolve meant "no session". That was false, and the
consequence was worse than a wrong frame: a database outage, a repository fault or
a plain programming error rendered a **healthy-looking anonymous page**. The portal
would have looked fine while its session store was unreachable, and the signed-in
operator — the one person positioned to notice — would have been silently logged
out rather than told.

The policy is now typed, and catches `SessionAbsent` alone:

| Condition | Result |
|---|---|
| No cookie | anonymous, **no session-store lookup** |
| Unknown, malformed, expired, revoked | anonymous, no logout token |
| `ServiceDegraded` | VM-03 `503`, security headers, `no-store` |
| Database / repository / programming failure | safe-error boundary, `500`, correlation id only |
| Cancellation | never caught; normal propagation |

A public page had no handler for `ServiceDegraded`, so one was added at the app
boundary rendering the **same** view, status and headers as `_refusal_response()`
gives a protected route — one answer to one condition rather than two renderers
disagreeing.

**Falsified** with the mutation verified by AST before the result was read:
restoring `except Exception` fails four cases; the corrected form catches
`['SessionAbsent']` and all 67 boundary cases pass.

### 6.6 Deliberate updates to accepted P3.4 evidence

Each recorded with its prior value or prior intent, never silently applied: the
`includes/header.html` frozen digest (twice, as the frame changed); the "no
`<button>`" assertion narrowed to its intent, since sign-out must be a POST submit;
three read-only-page assertions scoped to the page body; and **seven no-JavaScript
flow expectations** corrected from `/v1/characters` to `/v1/account/identities` —
they had required an administrator's page to link somewhere R-20 refuses them,
which is the same defect as R35-22 expressed as a test expectation.

**Contracts:** VM-23 in the view-model contract and TC-SHELL-01…16 in traceability,
both by addition. No accepted row rewritten.

## 7. Verification

Sequential, because the two suites share `freedom_test`. Exact results in §8 of the
final report accompanying this handoff.

| Check | Result |
|---|---|
| `tests/test_rotate_test_gate_script.py` | 24 passed |
| `tests/test_deployment_artifacts.py` | 7 passed |
| `tests/web/test_health_kill_switch_robustness.py` (with disposable DB) | 10 passed, 0 skipped |
| `tests/test_runtime_grants.py` + `_live.py` | 57 + 53 passed |
| `tests/web/test_shell_navigation_contract.py` | 30 passed |
| `tests/web/test_shell_request_boundary.py` | **67 passed** |
| `tests/test_rotate_test_gate_script.py` | **33 passed** |
| `tests/web/test_health_kill_switch_robustness.py` (with disposable DB) | 10 passed, **0 skipped** |
| focused web package (boundary + contract + health + shell components) | **157 passed** |
| focused script package (rotation + artifacts + grants) | **104 passed** |
| complete web suite | **2277 passed**, 80 skipped |
| complete bot/domain suite | **2346 passed** |
| Foundry module | 155 passed |
| asset + visual-freeze manifests | OK |
| bytecode compilation, both virtualenvs | clean |
| `git diff --check` | clean |

**Skips:** the 80 web skips are the two intentional authorization-matrix
parameterizations (54 + 26) whose permitted cells are asserted by the per-route
success cases; denial cells are not skipped. **No formatter, linter or type checker
is configured in this repository** — recorded as unavailable, never as passed.

Live PostgreSQL tests were run against the guarded disposable `freedom_test`
database. No test touched a real host, service, credential or `/etc`.

## 8. Host actions — what the Operations Owner actually did

**Correcting the earlier rounds, which listed all of these as Not Run:** Peter
performed three of them during this session, and they were verified from the
database and over HTTP rather than assumed.

| # | Action | State |
|---|---|---|
| H-1 | Rotate the spent gate | **Done.** Performed with the R35-08-corrected script |
| H-2 | Install the corrected Caddy configuration and reload | **Done.** `/healthz` verified refused through the public host; all five sites verified still serving |
| H-3 | Re-enroll both emergency credentials | **Done.** Two new credentials enrolled under the corrected `residentKey: required` ceremony; the two unproven ones retired, both retirements in the append-only audit. Verified: exactly two enabled |
| H-4 | Restrict origin ingress to Cloudflare ranges | **Not Run.** Deployment-gate item; the `CF-Connecting-IP` rewrite alone still does not establish a trusted client address |

**These are Peter/Claude attestations, not independently reviewed evidence.** They
were verified from the database and over HTTP by Claude at the time; Codex has not
inspected the live host, and no RAID or gate state changes on the strength of them.

**H-1 carries a caveat.** The rotation ran before R35-19 was found, so it used the
version with the post-commit window. It completed and printed a password, so no
loss occurred — but the window existed while it ran, and the corrected script is
what any future rotation should use.

Nothing in this handoff claims a host action because a hermetic test passed. The
three completed ones were confirmed against the live database and the running
service; H-4 is untouched.
