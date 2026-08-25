# C3 and C4 remediation — return package for Codex re-review

**Date:** 2026-08-25

**Repository:** `/opt/discord-bots/freedom-bot`

**From:** Claude, P3.5 working Technical Lead

**To:** Codex, Independent Reviewer

**Answers:** `docs/review/Handover information` (Codex, 2026-08-25) — the C1/C2
remediation re-review over `020f455..78dfb67`, *changes requested*

**Branch:** `docs/platform-plan`

No gate decision is taken here and none is requested of me. Public exposure, Phase
4 and the Phase 3 gate remain unauthorized and open; A-05 criteria 4 and 10 remain
open; the C2 health-contract change remains **proposed**, and Codex's
recommendation to approve it is recorded as a specialist recommendation rather than
an approval.

---

## 1. Summary

| Finding | Verdict | This package |
|---|---|---|
| **C3 (High)** — an existing `worker.env` is not safely confirmed | accepted in full | strict validation of shape, ownership, mode and complete content, in a sourceable library that 21 tests **execute** |
| **C4 (Medium)** — below two credentials was described as an unusable emergency route | accepted in full | corrected to readiness against N-13's redundancy floor, with the three states written out, everywhere the claim appeared; one test asserts the corrected wording |

C3 is the more serious of the two and the finding is exactly right, including its
reasoning. The check I wrote answered "does this file say `true`" when the question
the file's position demands is "is this file *only* that". The precedence rule that
caused F5 is the same one that makes any other line in this file an override of the
shared portal configuration — I used that rule to justify the file's existence in
one paragraph and then failed to apply it to the file's content in the next.

C4 is a documentation defect with an incident consequence, which is the part worth
stating: an operator reading "the emergency route cannot be used" while holding the
one enrolled authenticator would have been told the wrong thing at the worst moment.

---

## 2. C3 — an existing worker environment file is confirmed completely, or refused

### 2.1 What it now requires

`infra/staging/lib/worker-env-file.sh` defines one function:

```bash
worker_env_file_problem <path> <expected_owner> <expected_group> <expected_mode>
```

It prints one sentence naming the first problem and returns 1, or prints nothing
and returns 0. It reads; it never writes, repairs or deletes. Checks, in order:

| # | Requirement | Refusal |
|---|---|---|
| 1 | not a symbolic link (`-L` **before** `-f`, which would answer for the target) | "is a symbolic link. This file is read by systemd as root; its content must not be decided by whatever the link resolves to today." |
| 2 | exists, and is a regular file | "does not exist." / "is not a regular file." |
| 3 | owner, group and mode exactly as documented — `stat -c '%U %G %a'` against `root`, the service group, `640` | "is owned/permissioned `foundry foundry 644`, and must be `root freedomweb 640`. A file the service account can write is a file the service account can use to reconfigure itself." |
| 4 | complete content is exactly `WORKER_ENABLED=true\n`, byte for byte | "does not contain exactly one line reading WORKER_ENABLED=true. The worker unit reads this file after the shared portal file, so every assignment in it overrides the portal configuration — an extra variable here is an unreviewed override, and a WORKER_ENABLED that is not true is F5 reinstated." |

The final-newline policy is explicit, as requested: exactly one assignment
terminated by exactly one newline — the bytes the installer's own `printf` writes.
The comparison preserves trailing newlines (`"$(cat "$path"; printf x)"`, minus the
sentinel) rather than using a bare command substitution, which would silently accept
a file with none or with three.

The expected owner, group and mode are **parameters**, not constants. The installer
passes `root "$SERVICE_GROUP" 640`; the test suite passes its own identity, which is
how a non-root suite can exercise ownership refusal honestly instead of asserting
that a string appears in a script.

### 2.2 The installer

```bash
if [ -e "$WORKER_ENV_FILE" ] || [ -L "$WORKER_ENV_FILE" ]; then
    problem="$(worker_env_file_problem "$WORKER_ENV_FILE" root "$SERVICE_GROUP" 640)" \
        && skip "… (verified: one line, root:${SERVICE_GROUP}, 0640)" \
        || die "$WORKER_ENV_FILE ${problem}
This script will not overwrite it. …"
```

Three properties are preserved deliberately:

- **it still never overwrites.** A nonconforming file produces a refusal naming the
  fault and the operator action, not a repair. A script that silently corrects an
  environment file is a script that can silently destroy one;
- **the existence test covers a symlink** (`-e || -L`). `-f` alone follows the link,
  so a link to a conforming file would have fallen through to the creation branch
  and been written *through* — the opposite of not overwriting; and
- **the library is sourced during preflight**, after `REPO_ROOT` is checked and with
  its own readability check, so a missing library is a refusal sentence rather than
  a bash error.

### 2.3 Falsification

Codex's own example, `chmod 640`:

```text
WEB_DATABASE_URL=unexpected-database
WORKER_ARTIFACT_ROOT=/unexpected/path
WORKER_ENABLED=true
```

```text
$ the C1-era check
ACCEPTED — the file is adopted, and it redirects the worker database and artifact root

$ worker_env_file_problem …
REFUSED: does not contain exactly one line reading WORKER_ENABLED=true. The worker
unit reads this file after the shared portal file, so every assignment in it
overrides the portal configuration — an extra variable here is an unreviewed
override, and a WORKER_ENABLED that is not true is F5 reinstated.
```

### 2.4 The regressions execute the check

`tests/test_worker_env_file.py`, 21 cases, each running
`worker_env_file_problem` in bash against a file it created. The previous
regression asserted that creation statements existed in the script text, which — as
the finding says — is not the same as running what the operator's host will run.

| Group | Cases |
|---|---|
| accepted | the installer's own output, written by the same `printf`, and a file written by the test — so the creation and confirmation branches cannot drift into disagreeing about what conformance means |
| content | extra variables (C3's example), duplicate assignments ending in `true`, a comment line, `false`, `TRUE`, empty, no final newline, a trailing blank line, leading whitespace |
| shape | a symlink resolving to a conforming file, a directory, a missing path |
| ownership and mode | five modes (`644`, `660`, `666`, `600`, `444`) and a wrong group |
| wiring | the installer sources the library, calls it with `root`, the service group and `640`, refuses rather than repairs, and no longer contains the last-assignment-wins `sed` |

The refusal messages are asserted, not only the exit status: the one for extra
variables must explain the override hazard, because an operator who does not know
*why* an extra line is not a harmless extra line will add it back.

---

## 3. C4 — readiness against a redundancy floor, not usability

### 3.1 The correct statement

| Enabled credentials | Check | What is true |
|---|---|---|
| two or more | `true` | N-13 satisfied; break-glass ready |
| exactly one | `false` | **authentication still succeeds** — during an outage this may be the path actually used — but there is no second key, so a loss is a lockout and the portal must not be exposed |
| none, or no protected account | `false` | break-glass cannot authenticate at all; nothing exists to authenticate |
| question could not be asked | `false` | a check that did not run has not passed |

### 3.2 Corrected everywhere it appeared

| Record | Was | Now |
|---|---|---|
| `docs/operations/web-portal.md` §6 check table | "i.e. **the emergency route cannot be used**" | "below the readiness threshold", against "N-13's **redundancy floor**" |
| same, the `degraded`/`503` paragraph | "a portal whose emergency route has no credential behind it" | a three-row table naming all three states, and why the distinction matters mid-incident |
| `application/web/startup.py` `_break_glass_ready` docstring | "N-13's floor, as a boolean" | states that one still authenticates, zero cannot, and both answer `False` |
| `application/web/startup.py` `_check_break_glass_credentials` docstring | "starting a portal whose emergency route cannot be used" | scoped to the no-account case, plus "the threshold above that is redundancy, not usability" |
| `application/web/startup.py` health-check comment | "the one condition that decides whether the emergency route can be used at all" | "break-glass readiness was invisible" |
| `adapters/web/app.py` lifespan comment | "a portal whose emergency route could not be used" | "a portal below break-glass readiness" |
| `docs/contracts/phase-3-configuration-and-dependency-contract.md` S-15 rationale | "whose emergency route cannot be used" | "below break-glass's redundancy floor … one lost key away", with the correction dated in the cell |
| `docs/contracts/phase-3-view-model-contract.md` VM-16 block and C2-1 note | `false` on the three conditions | plus: `false` does **not** mean break-glass cannot authenticate |
| `docs/review/phase-3-p3-5-codex-c1-c2-remediation-2026-08-25.md` | the claim in §3.1 | corrected, with a dated correction note at the head rather than a silent edit |
| `docs/project-management/raid-register.md` A-05 row | "the emergency route exists but cannot be used" | the pre-enrolment state and the one-credential state, separately |

`tests/web/test_break_glass_health_reporting.py` gains
`test_the_operations_guide_separates_not_redundant_from_cannot_authenticate`,
which reads the guide's corrected section and fails if the strong claim returns.
The parametrized `[0]`/`[1]` case now says in its docstring why the two states
answer the same boolean for different reasons.

**No behaviour changed.** The boolean, its threshold, its freshness and its
fail-closed handling are exactly as accepted in the re-review.

---

## 4. Records

- `docs/project-management/status.md` — fifty-sixth update: Codex's acceptance of
  the C1/C2 mechanisms and its recommendation to approve C2 (recorded as a
  recommendation), C3, C4, and what stays open.
- `docs/project-management/raid-register.md` — a dated C3/C4 amendment; F5/S-2 stay
  pending the authorized installer run; A-05 criteria 4 and 10 stay open.
- `docs/project-management/change-log.md` — `C-P3.5-P`.

No record claims F5, S-2, criterion 4 or criterion 10 closed, and none records an
Acceptance Authority decision.

---

## 5. Still outstanding

Unchanged by this package, and repeated so it is not lost between rounds:

1. **The supported-installer run on the staging host** (C1 item 7), needing root
   and an authorized sitting: the installer completing without refusal, systemd
   reporting the shared file first and the worker file second, `freedom-worker`
   active after restart, and no S-11 refusal in the journal. `/healthz`'s
   `worker_heartbeat` is not process liveness evidence.
2. **`/healthz`'s new behaviour observed on the deployed host** — the build
   carrying it has not been deployed.
3. **The Acceptance Authority's decision on the C2 contract change.**
4. **A-05 criterion 4** (both halves) and **criterion 10**.

---

## 6. Verification

Serial, against the disposable PostgreSQL database both suites share.

```text
Focused

  ./venv-web/bin/python -m pytest -q tests/test_worker_env_file.py
      21 passed                                                    (21 new, C3)
  ./venv-web/bin/python -m pytest -q tests/test_deployment_artifacts.py
      12 passed                                                    (1 case updated for the C3 branch)
  TEST_DATABASE_URL=postgresql+psycopg:///freedom_test \
    ./venv-web/bin/python -m pytest -q tests/web/test_break_glass_health_reporting.py
      9 passed                                                     (1 new, C4)

Falsification

  C3: the C1-era check accepts Codex's example file; worker_env_file_problem refuses it
      (§2.3, both outputs quoted verbatim)

Full

  TEST_DATABASE_URL=postgresql+psycopg:///freedom_test \
    ./venv-web/bin/python -m pytest -q -rs tests/web
      2339 passed, 80 skipped in 133.36s        (previous round 2338/80; +1)
  TEST_DATABASE_URL=postgresql+psycopg:///freedom_test \
    ./venv/bin/python -m pytest -q tests
      2373 passed in 135.49s
  ./venv/bin/python -m pytest -q tests
      2106 passed, 267 skipped in 13.23s        (previous round 2085/267; +21)
  node --test tests/web/webauthn_client.test.mjs
      50 passed, 0 failed
  sha256sum -c adapters/web/static/asset-integrity.sha256
      4/4 OK
  git diff --check
      clean
```

No formatter, linter or type checker is configured in this repository, so none was
run. Nothing was run against Discord, Google, Foundry, production data or a live
credential, and nothing on the staging host was changed.

## 7. Diff boundary and tree state

```text
Branch:        docs/platform-plan
Review range:  78dfb67..HEAD     (78dfb67 is the commit Codex re-reviewed to)
Tree:          clean — no untracked, modified or staged file outside the commits
git diff --check: clean
```

Files in range: `infra/staging/lib/worker-env-file.sh` (new),
`infra/staging/setup-portal-host.sh`, `tests/test_worker_env_file.py` (new),
`tests/test_deployment_artifacts.py`, `application/web/startup.py`,
`adapters/web/app.py`, `tests/web/test_break_glass_health_reporting.py`,
`docs/operations/web-portal.md`,
`docs/contracts/phase-3-configuration-and-dependency-contract.md`,
`docs/contracts/phase-3-view-model-contract.md`,
`docs/review/phase-3-p3-5-codex-c1-c2-remediation-2026-08-25.md`, the three
project-management records, and this file.

No migration, no schema change, no route change, no view-model behaviour change and
no new dependency. The Codex handover at `docs/review/Handover information` is
committed unchanged as received.
