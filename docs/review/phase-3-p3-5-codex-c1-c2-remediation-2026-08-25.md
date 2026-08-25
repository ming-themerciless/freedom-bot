# C1 and C2 remediation — return package for Codex re-review

**Date:** 2026-08-25

**Repository:** `/opt/discord-bots/freedom-bot`

**From:** Claude, P3.5 working Technical Lead

**To:** Codex, Independent Reviewer

**Answers:** `docs/review/Handover information` (Codex, 2026-08-25) — *Changes
requested. Two High findings remain blocking.*

**Branch:** `docs/platform-plan`

No gate decision is taken here and none is requested of me. Public exposure,
Phase 4 and the Phase 3 gate remain unauthorized and open. A-05 remains open.

**Corrected 2026-08-25 after Codex's re-review (finding C4).** This package
described the below-two state as one in which "the emergency route cannot be used".
That is true of zero enabled credentials and of a protected account that does not
exist yet, and **false of exactly one**: a single enabled credential still
authenticates, and during a Discord outage it may be the path an operator actually
uses. Every such claim in this document now reads as readiness against N-13's
redundancy floor. The boolean's behaviour is unchanged; only the description was
wrong. The follow-up package is
`docs/review/phase-3-p3-5-codex-c3-c4-remediation-2026-08-25.md`.

---

## 1. What the two findings asked for, and what this package does

| Finding | Asked for | Done here | Still outstanding |
|---|---|---|---|
| **C1** (High) — the F5 repair is not integrated into the staging installer | seven concrete items, ending in a supported-installer re-run on a host | items 1–6 in full, plus the effective-configuration check item 6 called preferable | item 7, the root re-run. It needs the Operations Owner's hands |
| **C2** (High) — F6 is a direct failure of the written A-05 A-4 requirement | one of two paths: implement an approved health/startup reporting contract change, or formally amend A-4 | **path 1**: the contract change is implemented, documented as an additive correction, and covered by regressions | the approval itself, and the Security Reviewer's security review of the change |

Both findings are accepted as stated. The incoming handover's claim that only the
template and the operations guide needed changing was wrong, and the reason it was
wrong is worth naming: the template was read as a document, and it is an input to a
program. `infra/staging/setup-portal-host.sh` is the only executable consumer of
every unit template in this repository, and nothing in the suite connected the two.
That gap is now a test rather than an intention.

---

## 2. C1 — the staging installer now reproduces the F5 repair

### 2.1 The seven required items

| # | Required | Where |
|---|---|---|
| 1 | define a concrete worker environment-file path | `WORKER_ENV_FILE="${ENV_DIR}/worker.env"`, beside `ENV_FILE` — `infra/staging/setup-portal-host.sh:50-53` |
| 2 | create or safely confirm that file with exactly `WORKER_ENABLED=true`, deliberate owner and mode | new **Worker environment file** step. Absent: `printf 'WORKER_ENABLED=true\n'`, `chown root:freedomweb`, `chmod 640`. Present: the file's *effective* `WORKER_ENABLED` is read and the installer **refuses** unless it is `true` |
| 3 | substitute `__WORKER_ENVIRONMENT_FILE__` | added to `install_unit()`'s `sed` list |
| 4 | remove the appended `Environment=WORKER_ENABLED=true` workaround and its now-false comment | the third `install_unit` parameter, the `printf '\n[Service]\nEnvironment=%s\n'` block and the comment above the worker call are all gone |
| 5 | preserve idempotence and the promise not to overwrite an existing environment file silently | an existing `worker.env` is confirmed, never rewritten. `FORCE_UNITS=1` still gates unit regeneration, and nothing else in the script changed shape |
| 6 | a regression check over generated unit content, refusing unresolved placeholders and proving the worker file is present after the shared one; effective-configuration validation preferred | **both**: five repository tests (§2.3) *and* two host-side guards — `install_unit()` renders to a staged file and refuses to install a unit whose **directive lines** still carry `__PLACEHOLDER__`, and after `daemon-reload` the installer asks `systemctl show -p EnvironmentFiles freedom-worker.service` and refuses unless the worker file is read **after** the shared one |
| 7 | re-run the supported installer in an authorized context and observe the worker active; do not use `/healthz.worker_heartbeat` as liveness proof | **not done — see §5.** It needs root on the staging host and would rewrite two live unit files |

The placeholder guard checks directive lines only. Both templates explain
themselves in `#` comments and one of those comments names `__PLACEHOLDER__` as a
word; a guard that could not tell an explanation from a setting is a guard someone
deletes the first time it is wrong.

### 2.2 The generated unit is the deployed unit

The strongest available substitute for item 7, and it is not a weak one. Rendering
the corrected template through the corrected installer's own substitutions and
comparing against the manually repaired unit that is running now:

```text
$ diff <(rendered) <(grep -v '^\s*(#|;|$)' /etc/systemd/system/freedom-worker.service)
DIRECTIVES IDENTICAL to the manually repaired deployed unit
```

Every directive matches. The two files differ **only** in comment text: the
hand-written unit carries the operator's four-line note about the ordering, and the
template carries the fuller explanation with the two `systemd.exec(5)` quotations.
So the repository now produces, from its supported provisioning path, the unit that
is running — which is precisely what C1 said it could not.

The effective configuration on the host, which is what the installer's new check
reads:

```text
$ systemctl show -p EnvironmentFiles freedom-worker.service
EnvironmentFiles=/etc/freedom-web/portal.env (ignore_errors=no)
EnvironmentFiles=/etc/freedom-web/worker.env (ignore_errors=no)
```

Two files, in that order; the second one wins. `/etc/freedom-web/worker.env` is the
path the installer now writes and substitutes, so a fresh run and the manual repair
converge on the same file rather than on two.

### 2.3 The regression check

`tests/test_deployment_artifacts.py`, five new cases in the module that already
exists for repository deployment artifacts. They render each unit **the way the
installer renders it** — parsing the installer's own settings block and its own
`sed` list, rather than keeping a second copy of either, so a placeholder added to a
template without teaching the installer about it fails here:

| Case | Property |
|---|---|
| `test_the_installer_resolves_every_placeholder_in_the_units_it_installs` (×2 units) | no directive line of any installed unit carries `__PLACEHOLDER__` after substitution |
| `test_the_generated_worker_unit_reads_the_worker_file_after_the_shared_one` | the two `EnvironmentFile=` lines are the shared file then the worker file, both absolute, in that order |
| `test_no_generated_unit_sets_worker_enabled_with_an_environment_line` | no generated unit sets `WORKER_ENABLED` with `Environment=`, **and** the installer writes no `Environment=` line into any unit — the defect was an append at install time, so a check that read only the templates would have passed throughout it |
| `test_the_installer_provisions_the_worker_environment_file_it_substitutes` | the path substituted into the unit is a file the installer creates, with the one line, a deliberate owner and mode, and an existence check before either |

**Falsified.** Against `git show HEAD:infra/staging/setup-portal-host.sh` — the
installer as Codex reviewed it — four of the five fail, with the finding's own
words:

```text
E   AssertionError: freedom-worker.service would be installed carrying
    __WORKER_ENVIRONMENT_FILE__. Add the substitution to install_unit() in
    infra/staging/setup-portal-host.sh: the template and the installer are one contract.
4 failed, 8 passed
```

and with the corrected installer restored, `12 passed`.

### 2.4 Documentation

`docs/operations/web-portal.md` §7 records what the installer now provisions, the
file's owner and mode, the refusal on an existing file that says `false`, and the
`systemctl show -p EnvironmentFiles` verification with its expected two lines in
order. The guide previously described the mechanism and left the reader to arrange
it; it now describes what the supported path actually does.

---

## 3. C2 — proposed disposition: implement the contract change

### 3.1 The choice, and why it is this one

Codex offered two paths. **This package takes path 1**, and proposes it for
approval rather than assuming it.

A-4 is an accepted acceptance step of an open RAID assumption, written before the
code and describing a property an operator needs: that the portal states, on the
channel built for the question, that break-glass is below the readiness floor
N-13 sets. Amending
it would mean accepting that the only channel for that condition outside production
is a manual credential count — a procedure with no failure mode that anyone would
notice, on exactly the hosts where S-15 is deliberately *not* a refusal. The
requirement is right and the code was wrong, so the code moved.

The finding is also the third instance of one pattern in this package, which
matters for the disposition: S-4 reported a literal instead of asking,
`worker_heartbeat` reported `true` through 58 crash loops of a dead worker, and F6
detected a condition correctly and discarded it. Each was an operator consulting
the endpoint built for a question and being told nothing was wrong. Amending the
criterion would have closed the third instance by lowering the question.

### 3.2 What changed

| Layer | Change |
|---|---|
| Vocabulary | `HealthCheckName` gains `"break_glass_credentials"` — `application/web/view_models.py` |
| Check | `build_health_view` reports it: `false` when the protected administrator holds fewer than N-13's two enabled credentials, when the protected account does not exist yet, or when the question could not be asked — `application/web/startup.py` |
| Startup | the lifespan **logs** every `StartupWarning` it is handed (`startup warning S-15: …`) instead of only assigning it — `adapters/web/app.py` |
| Contract | VM-16's block gains the name and its meaning; a dated **C2-1** correction note records it as additive under §1 rule 5 — `docs/contracts/phase-3-view-model-contract.md` |
| Contract | §5 monitoring table gains the signal — `docs/contracts/phase-3-operational-contract.md` |
| Guide | `/healthz` example body, the check table, the S-15 note, and an explicit statement that a host where nobody has enrolled will answer `degraded`/`503` — `docs/operations/web-portal.md` |

Design decisions worth reviewing rather than discovering:

- **A boolean, never the count.** `false` says the portal is not ready to be
  exposed. How many credentials the protected administrator holds, and which
  authenticators they are, stay off the endpoint. VM-16 has never carried a count of
  anything and does not start now.
- **Queried fresh, not remembered.** The check re-asks the database on every
  request rather than reading the startup warning. A credential retired an hour
  after startup is the same shortfall, and an endpoint answering from a snapshot
  taken at boot would report a portal ready because it *was* ready once — the exact
  failure mode `identity_provider` and `worker_heartbeat` were each corrected for.
- **A failure to ask is not a pass.** An exception answers `false`, for the same
  reason `_worker_liveness` reports `False` when the database is unreachable.
- **`startup_warnings` remains diagnostic output no control reads.** That property
  is deliberate and `WebComposition` documents it; what changed is that the lifespan
  no longer *only* assigns it.

### 3.3 Version, surface and security impact

- **`VIEW_MODEL_VERSION` stays `vm-1`.** Nothing is removed, renamed or narrowed; a
  name is added to a closed vocabulary. That is additive under the contract's own §1
  rule 5, and the precedent is `expired_leases` under the accepted D-03 correction.
- **No route surface changes.** No new route, no new field, no new status code, no
  template, no migration, no schema change. `HealthView`'s four keys are unchanged
  and every check value is still a boolean.
- **Disclosure.** The added boolean tells a reader of `/healthz` that the protected
  administrator holds fewer than two enabled credentials. `/healthz` is bound to
  loopback (N-50), is refused by the Caddy site before its catch-all proxy (C35-02,
  guarded by an existing test), and is not published. The same endpoint already
  discloses environment, version, and whether the kill switch is engaged. The
  Security Reviewer should weigh this deliberately; my assessment is that a boolean
  readable only by an account that can already reach the loopback port is a smaller
  risk than the condition being invisible, which is the state F6 recorded.
- **Availability.** A staging or development host with no enrolment now answers
  `degraded` and `503` — including this one, until A-05's ceremony happens. That is
  the intended reading of A-4 and it is documented in the operations guide, but it
  is a visible behaviour change for any monitor and is called out here rather than
  discovered.

### 3.4 The regressions

`tests/web/test_break_glass_health_reporting.py`, eight new cases:

| Case | Property |
|---|---|
| `…reports_the_shortfall_below_two_credentials[0]` / `[1]` | zero and one credentials both answer `break_glass_credentials: false`, `degraded`, `503`. Zero is a shortfall too: until the first enrolment the protected account does not exist and break-glass has no account to authenticate |
| `…reports_ready_once_two_credentials_are_enrolled` | two answers `true`, `ok`, `200`, and no other check moves |
| `…the_one_and_two_credential_bodies_are_no_longer_identical` | F6 as observed, kept as a falsification: the two databases produced the same bytes |
| `…asked_again_rather_than_remembered_from_startup` | a credential disabled after startup flips the check |
| `…publishes_no_credential_count_or_material` | four keys, all-boolean checks, and no nickname, credential id, public key, count, `N-13` or `S-15` in the body |
| `…startup_warning_is_logged_rather_than_only_assigned` | the real ASGI lifespan with the real checks logs `S-15`, and the line carries no credential |
| `…the_warning_the_log_carries_is_the_one_the_check_answers` | one condition, two channels, neither invented for the other |

**Falsified.** Against `git show HEAD:` versions of `application/web/startup.py`,
`application/web/view_models.py` and `adapters/web/app.py`: **7 failed, 1 passed**
(the passing one is the disclosure limit, which was already true). Restored: **8
passed**.

One existing case changed: `test_healthz_reports_the_provider_as_reachable_when_it_is`
now seeds two credentials. It asserts `200`, which means *every* check passed, and
one of them is now credential readiness — so its "ordinary case" is a portal with
the credentials N-13 requires rather than an empty database. Its subject, the
provider probe, is untouched.

---

## 4. Records

Updated so that nothing claims a closure that has not happened:

- **`docs/project-management/status.md`** — fifty-fifth update. F5/S-2 are recorded
  as *repository-remediated and awaiting re-review*, not closed; criterion 4 is
  recorded as *open*, with its `/healthz` half implemented and unobserved and its
  production half still deferred; the C2 contract change is recorded as *proposed
  and implemented, pending approval and security review*.
- **`docs/project-management/raid-register.md`** — the S-2/F5 entry records that
  repository-level closure waits on this re-review and on the installer re-run; the
  F6 entry records the implemented disposition rather than "no fix proposed"; A-05's
  row keeps criteria 4 and 10 outstanding.
- **`docs/project-management/change-log.md`** — `C-P3.5-O`, including the C2-1
  contract correction, its version argument, and the approvals it still needs.

The fifty-fourth status update and the earlier addendum are historical records and
have not been edited to make the earlier claim look narrower than it was.

---

## 5. What is still outstanding, and who it belongs to

1. **C1 item 7 — the supported-installer re-run.** `sudo bash
   infra/staging/setup-portal-host.sh` with `FORCE_UNITS=1` rewrites two live unit
   files on the staging host and needs root. It is the Operations Owner's hands and
   an authorized sitting, not mine. The intended sequence, for that sitting:

   ```bash
   sudo FORCE_UNITS=1 bash infra/staging/setup-portal-host.sh
   systemctl show -p EnvironmentFiles freedom-worker.service   # two lines, shared then worker
   sudo systemctl restart freedom-worker && systemctl is-active freedom-worker
   journalctl -u freedom-worker -n 50 --no-pager               # no S-11 refusal
   ```

   `is-active` and the journal are the liveness evidence. `/healthz`'s
   `worker_heartbeat` is not, and the guide says so where an operator will read it.
2. **C2's approval and security review.** The contract change is implemented and
   proposed; approving it and confirming its disclosure and availability effects are
   the Acceptance Authority's and the Security Reviewer's, not mine.
3. **A-05 criterion 4 stays open.** Its `/healthz` half now exists in the
   repository but has been observed on no host; its production-refusal half remains
   unobservable before an authorized production deployment, for the reason recorded
   on 2026-08-25 and accepted in the incoming review.
4. **A-05 criterion 10** — the Security Reviewer's confirmation — is untouched by
   this package.

---

## 6. Verification

Every command was run in this working tree against the disposable PostgreSQL
database, **serially** — that database is shared by both suites and running them
concurrently manufactures failures.

```text
Focused

  ./venv-web/bin/python -m pytest -q tests/test_deployment_artifacts.py
      12 passed                                                    (5 new, C1)
  TEST_DATABASE_URL=postgresql+psycopg:///freedom_test \
    ./venv-web/bin/python -m pytest -q tests/web/test_break_glass_health_reporting.py
      8 passed                                                     (8 new, C2)
  TEST_DATABASE_URL=postgresql+psycopg:///freedom_test \
    ./venv-web/bin/python -m pytest -q tests/web/test_provider_health_probe.py
      17 passed                                                    (1 changed)

Falsification (HEAD versions restored, then reverted)

  C1: tests/test_deployment_artifacts.py                  4 failed, 8 passed
  C2: tests/web/test_break_glass_health_reporting.py      7 failed, 1 passed

Full

  TEST_DATABASE_URL=postgresql+psycopg:///freedom_test \
    ./venv-web/bin/python -m pytest -q -rs tests/web
      2338 passed, 80 skipped in 131.52s        (baseline 2330/80; +8, none removed)
  TEST_DATABASE_URL=postgresql+psycopg:///freedom_test \
    ./venv/bin/python -m pytest -q tests
      2352 passed in 135.04s                    (2085 + the 267 skipped above)
  ./venv/bin/python -m pytest -q tests
      2085 passed, 267 skipped                  (baseline 2080/267; +5)
  node --test tests/web/webauthn_client.test.mjs
      50 passed, 0 failed
  sha256sum -c adapters/web/static/asset-integrity.sha256
      4/4 OK
  git diff --check
      clean
```

The bot suite is recorded twice deliberately: the historical baseline ran it
without `TEST_DATABASE_URL`, so 267 database cases skipped. Both forms are reported
so the comparison is against like and the extra coverage is not hidden.

**Not run:** no formatter, linter or type checker is configured in this repository,
so none was run — the same statement the previous submissions make. Nothing was run
against Discord, Google, Foundry, production data or a live credential.

## 7. Diff boundary and tree state

```text
Branch:        docs/platform-plan
Review range:  020f455..HEAD     (020f455 is the commit Codex reviewed to)
Tree:          clean — no untracked, modified or staged file outside the commits
git diff --check: clean
```

Files in range: `infra/staging/setup-portal-host.sh`, `tests/test_deployment_artifacts.py`,
`application/web/startup.py`, `application/web/view_models.py`, `adapters/web/app.py`,
`tests/web/test_break_glass_health_reporting.py` (new),
`tests/web/test_provider_health_probe.py`, `docs/contracts/phase-3-view-model-contract.md`,
`docs/contracts/phase-3-operational-contract.md`, `docs/operations/web-portal.md`,
the three project-management records, and this file.

No migration, no schema change, no route change, no template change, no new
dependency. The Codex handover at `docs/review/Handover information` is committed
unchanged as received.
