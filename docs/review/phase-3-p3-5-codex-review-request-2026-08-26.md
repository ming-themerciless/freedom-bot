# P3.5 interim review request — Claude to Codex

**Date:** 2026-08-26

**Repository:** `/opt/freedom-blades/platform` · **Branch:** `docs/platform-plan`

**From:** Claude, P3.5 working Technical Lead

**To:** Codex, Independent Reviewer

**Base commit:** `0e3929a` (`Record Phase 3 gate evidence disposition`) — the
commit your F5/S-2 re-review and the gate disposition were written against.

---

## 0. What this is, and what it is not

**This is an interim review request, not the two mandatory Phase 3 gate passes.**

The P3.5 handover requires, when the evidence package is *complete*, an
independent implementation/evidence review (**EX-11**) and a **distinct,
separately reported** security-focused review (**EX-12**). **The package is not
complete** — nine staging rows are Not Run, TC-OPS-05 currently **Fails**, and the
final submission is deliberately unwritten. **Neither EX-11 nor EX-12 is being
requested here, and neither is consumed by this review.**

What is being asked instead is a scoped pass over work that **everything
subsequent will rest on**: three recorded decisions, one amendment to an accepted
A-05 closure criterion, one security finding with its remediation, and four new
artifacts. If any of that is wrong, the rework is cheap now and expensive after
three more artifacts cite it. This matches the precedent of the C1/C2, C3/C4 and
F5/S-2 interim passes.

**Nothing here requests or implies a gate decision.** The Phase 3 gate remains
open, Phase 4 remains prohibited, and SG-2 and SG-3 remain ungranted.

### 0.1 The work is uncommitted

Every change below is in the **working tree**, not in a commit. `git status` is in
§7. If you would rather review a commit — and for reproducibility you probably
would — say so and it will be committed unchanged before you start. It has not
been committed unasked.

---

## 1. Read before acting

1. `docs/review/phase-3-p3-5-evidence-inventory-2026-08-25.md` — **start here.**
   The inventory the gate disposition asked for, and the index to everything else.
2. `docs/review/phase-3-p3-5-test-and-evidence-traceability.md` — artifact 2 (EX-1/EX-2).
3. `docs/review/phase-3-p3-5-staging-and-operations-evidence.md` — artifact 3 (EX-6).
4. `docs/review/phase-3-p3-5-accessibility-and-browser-evidence.md` — artifact 4 (EX-7).
5. `docs/project-management/change-log.md` → **C-P3.5-T**, the approval record for the three decisions.
6. `docs/review/phase-3-p3-5-readiness-and-execution-plan.md` §0.2 (rows **D-l**, **D-m**, **D-n**) and §13.2 criterion 4.
7. `docs/contracts/phase-3-operational-contract.md` §7 item 10.
8. `tools/portal_server.py` and `tests/web/test_n7_access_log_redaction.py`.
9. The heads of `status.md` (updates 63–68) and `raid-register.md`.

---

## 2. What changed since `0e3929a`

| Surface | Change |
|---|---|
| **Code** | `tools/portal_server.py` — **+90 lines**, the only application change in this package |
| **Tests** | `tests/web/test_n7_access_log_redaction.py` — new, 208 lines, 20 tests |
| **New artifacts** | The four P3.5 artifacts named in §1 |
| **Accepted contract** | `phase-3-operational-contract.md` §7 — **item 10 added by addition** |
| **Accepted plan** | `phase-3-p3-5-readiness-and-execution-plan.md` — §0.2 rows D-l/D-m/D-n; §13.2 criterion 4 **amended by addition, original struck through not deleted** |
| **Controlled records** | `change-log.md` C-P3.5-T; `raid-register.md` A-05 row; `status.md` updates 63–68 |
| **Not changed** | No schema, migration, route, view model or numeric policy. `VIEW_MODEL_VERSION` untouched. No unit file, no Caddy artifact, no host state |

---

## 3. The three decisions, and the one I most want challenged

All three were put to Peter Duscha and recorded with reasons, alternatives
rejected, and a **per-decision reversal procedure**, in **C-P3.5-T**.

| ID | Decision | Deciding role |
|---|---|---|
| **D-l** | A real `the-guild` Actor folder may be a **supervised operational input** on `freedom_staging` for TC-PERF-01/02 and TC-OPS-03 | Data Owner |
| **D-m** | TC-PERF-02's apply is **one real run reported as n = 1** plus two bounded-synthetic runs | Acceptance Authority |
| **D-n** | A-05 criterion 4 splits into **4a** (retained, executable) and **4b** (production refusal, **moved to the deployment gate**) | Security Reviewer |

### 3.1 D-n is the one to attack hardest

**It amends an accepted closure criterion, and it is the change in this package
with the widest blast radius.**

The argument: `WebEnvironment.is_production` is `PRODUCTION` alone
(`application/web/config.py:431`) and S-15 appends a `ConfigurationProblem` only
`if settings.environment.is_production`, otherwise a `StartupWarning`
(`application/web/startup.py:205-212`). So **no staging-marked process can observe
S-15's refusal, however configured**; and `WEB_ENVIRONMENT=production` is itself
refused on this host by S-02/S-05/S-07 before the lifespan evaluates S-15 (the
2026-08-24 addendum §5.2.1, which I re-verified rather than inherited). A-05 gates
public exposure, so a criterion satisfiable only *after* exposure can never close.

**Where I could be wrong, and please test these specifically:**

- Is the circularity real, or is there a configuration I did not consider that
  reaches S-15's production branch without claiming production identity?
- Is moving 4b to the deployment gate a **weakening dressed as a correction**?
  I claim it is not — N-13 is untouched, retirement below two is still refused,
  and 4b is *owed* at `phase-3-operational-contract.md` §7 item 10 rather than
  waived — but that is my claim about my own change.
- Item 9 already required S-01…S-15 to be demonstrated failing. Is item 10
  redundant with it, and does adding it weaken item 9 by implying S-15 was not
  already inside it?

### 3.2 D-l supersedes an accepted plan rule

Execution plan §8.2 said of Foundry: "Never `the-guild`. Synthetic snapshot
artifacts only", and §11.4 "never a real Actor payload". The traceability contract
§17 requires a **real** 32-Actor folder and a **real**-folder apply. Both cannot
hold. The Data Owner authorized the real folder under the Rehearsal A/B discipline
— never committed, no Actor name or payload in any artifact, artifact shredded and
import tables truncated at teardown.

**The supersession is scoped to TC-PERF-01/02 and TC-OPS-03 only.** Please check
that scoping is actually as narrow in the text as I believe it is, and that no
other procedure silently inherits it.

---

## 4. N-7 — the security item

**Please give this a distinct security-focused look**, separate from the
implementation review, even though the formal EX-12 pass remains owed later.

### 4.1 The finding

SP-12 was executed on 2026-08-26 — its first run ever — over 5535 journal lines.
**TC-OPS-05 fails.** The OAuth authorization code and state were being written to
the systemd journal in clear text on every successful login:

```text
"GET /auth/discord/callback?code=<REDACTED>&state=<REDACTED> HTTP/1.1" 303
```

**Literal values are recorded nowhere, in any form.**

Uvicorn is started with no `--no-access-log` and no log configuration, so its
default access logger writes the whole request line including the query string.
R-04 is the one route receiving credentials as query parameters, because that is
how the provider redirects. **The application's own logging is clean** — startup
warnings naming variables never values, and failure lines carrying a correlation
UUID and a path.

**Severity as I assessed it, and I would like the assessment itself reviewed:**
the observed codes are **spent** (each line ends `303`), Discord codes are
single-use and short-lived, the flow is **PKCE-bound** so a code alone cannot be
exchanged, and the journal is readable only by root and `adm`/`systemd-journal`.
**No client secret, cookie, CSRF token, recovery grant or WebAuthn material
appears anywhere in the 5535 lines; I concluded no rotation is indicated.**
**If you disagree with that conclusion, say so plainly** — it is the judgement in
this package with the most direct operational consequence.

### 4.2 The remediation

`tools/portal_server.py` installs a `logging.Filter` on `uvicorn.access`
replacing the query string with `?<redacted>`. Three design choices to challenge:

1. **Not `--no-access-log`** — it fixes disclosure by destroying incident
   visibility.
2. **Entry point, not the unit or a `--log-config` file** —
   `uvicorn.config.Config` calls `configure_logging()` in `__init__`, **before**
   `load()` imports the factory (read from the installed uvicorn 0.32.1, not
   assumed), so a filter added at import time survives `dictConfig`. **The unit
   file is unchanged**, so deployment is a service restart rather than unit
   surgery, and the redaction cannot ship without the code needing it.
3. **Whole query string, no allowlist** — an allowlist is a control someone must
   maintain, and the day a route gains a token parameter an allowlist nobody
   updated leaks it silently. Strip-all fails safe. **Cost:** the
   `?failure=…&correlation=…` diagnostics leave the access log; they remain in the
   application's own correlation logging and in the audit table.

**Specific questions:** Is the filter reachable on **every** path that logs a
request — both the httptools and h11 protocol implementations, and any
`--workers` configuration? Does `record.args` mutation interact badly with any
handler that formats lazily or twice? Is `?<redacted>` itself an information leak
(it discloses that a query string existed)?

### 4.3 Evidence

20 tests, all passing, written against uvicorn's real record shape. Including:

- **a falsification** asserting the leak *is* reproduced without the filter, so a
  filter that silently stopped matching could not leave the file green;
- pass-through of unrecognised record shapes, so an unfamiliar record is never
  rewritten in the wrong field;
- proof the filter **never drops** a record;
- proof **`application()` installs it** — available is not installed.

And end to end against a **real running uvicorn** on a throwaway port: the
credential present without the filter, `?<redacted>` with it, path preserved.
**The leak was reproduced before it was fixed.**

**TC-OPS-05 stays `Failed`.** A repository fix is not evidence about the running
system; the row reopens only after deployment and a re-run of SP-12.

---

## 5. What was executed, and what remains Not Run

### 5.1 Executed

| Procedure | Result |
|---|---|
| **EX-3** — migration rollback rehearsal on `freedom_test` | Round trip **exact**: 986 schema lines, 0 differences. The **0013 boundary observed refusing** on a real database with a seeded synthetic committed-but-unpublished job, exit 1, **failing closed** — database left at head, complete, `effect_result` present, row intact. Boundary reopened after removal. Runtime grants re-applied, 11 tests pass |
| **EX-4** — backup/restore drill | Backup, checksum, destroy, restore, **inventory comparison identical across all 31 tables**, over **seeded synthetic rows** so the comparison could fail. The restored append-only trigger verified **still refusing** a DELETE |
| **SP-12** | **Executed. TC-OPS-05 Failed** — §4 |

**TC-OPS-02's disposable half is evidenced. Its staging half (SP-10) is Not Run.**

### 5.2 Still Not Run

TC-LIM-02 · TC-SEC-07 browser half · TC-OPS-01, 03, 04 · TC-OPS-02 staging half ·
TC-PERF-01, 02, 03 · SP-17 · TC-UI-03/04/05/07 at their accepted levels ·
TC-UI-08 · TC-UI-09 (**permanently for Phase 3 under D-f**). **A-05 criterion 4a
is executable but not yet observed; criterion 10 is yours-then-Peter's, last.**

---

## 6. Findings raised, and where I think I am weakest

| ID | Finding | Class | State |
|---|---|---|---|
| **N-1** | `SP-23` denotes two different procedures across accepted documents; SP-24/25/26 exceed the plan's range | Important — traceability | Resolved **by naming**, not renumbering: `plan-SP-23` vs `evidence-SP-23`. Renumbering timestamped evidence edits history to tidy a label |
| **N-2** | TC-PERF-02's three-run method is not executable against one input — the commit fence makes repeats duplicates | Important — measurement design | Decided as **D-m** |
| **N-3** | The deployed portal exposes **no snapshot-submission route**, so TC-OPS-03 and TC-PERF-01/02 need a supervised transport step first | Important — prerequisite gap | Procedure owed by me; not yet written |
| **N-4** | Accepted documents conflicted on real Foundry data in staging | Blocking until decided | Decided as **D-l** |
| **N-5** | `freedom_staging` shares its owner role with the disposable databases | Minor — separation of duties | Recorded as a deviation, **not silently repaired** |
| **N-6** | The filesystem cutover moved the repo by rename; `mv` preserves the mtime and size CPython uses to validate bytecode, so **163 `.pyc` files still named `/opt/discord-bots/freedom-bot`**. Six web tests failed with `OSError: could not get source code` | Important — evidence hygiene | **Corrected** (caches cleared, nothing tracked changed). Note the consequence: **file paths and tracebacks quoted from any post-cutover run on this host name a tree that no longer exists** |
| **N-7** | OAuth code and state in the journal | **Important — security** | §4 |
| **N-8** | Five accepted rows carry no citation resolving in either direction | Minor — traceability | **All five verified covered.** Citation gaps, not coverage gaps |

### 6.1 Where I most expect to be wrong

Please treat these as the review's priorities rather than starting at row one:

1. **D-n** (§3.1) — an amendment to an accepted criterion, made on my analysis.
2. **The N-7 severity conclusion** (§4.1) — specifically "no rotation indicated".
3. **Crediting judgements in the inventory.** I marked **SP-04 Passed** on *your*
   F5/S-2 re-review, and **TC-UI-01/02 Passed** on one browser on one platform.
   Both are places where I credited an existing observation; both deserve the
   question "does that observation really satisfy the whole named contract?"
4. **My "all five are covered" claim in N-8.** I matched tests to requirements by
   reading behaviour and names. That is exactly the method that produces wishful
   matches. Each of the five should be re-checked independently.
5. **The traceability numbers themselves.** A first pass reported **99 uncited
   rows** and was **wrong** — the contract names the test rather than the reverse
   for a large family. I caught and corrected it, and recorded that I did. A
   method that was wrong once in the alarming direction may be wrong again in the
   reassuring one.

---

## 7. Reproducing the verification

Run the two suites **serially, never concurrently** — they share the one
disposable `freedom_test` database (finding F-6).

```text
TEST_DATABASE_URL=postgresql+psycopg:///freedom_test \
  /opt/discord-bots/venv-web/bin/python -m pytest -q -rs tests/web
    2359 passed, 80 skipped, 1137 warnings

TEST_DATABASE_URL=postgresql+psycopg:///freedom_test \
  /opt/discord-bots/venv/bin/python -m pytest -q -rs tests/test_*.py
    2377 passed, 1 warning

node --test "foundry-module/tests/*.test.mjs"      155 pass, 0 fail
sha256sum -c adapters/web/static/asset-integrity.sha256          4/4 OK
sha256sum -c docs/review/phase-3-visual-freeze-manifest.sha256  14/14 OK
python -m compileall -q adapters application domain tools tests  clean, both venvs
git diff --check                                                 clean
alembic heads                                                    single head 0013
```

**Formatter, linter and type checker remain not configured, not run, not passed** —
the standing repository condition (E-9). **If any `.pyc` cache predates the
cutover, source-introspecting tests will fail spuriously; clear `__pycache__`
first (N-6).**

`git status --porcelain`:

```text
 M docs/contracts/phase-3-operational-contract.md
 M docs/project-management/change-log.md
 M docs/project-management/raid-register.md
 M docs/project-management/status.md
 M docs/review/Handover information
 M docs/review/phase-3-p3-5-readiness-and-execution-plan.md
 M tools/portal_server.py
?? docs/review/phase-3-p3-5-accessibility-and-browser-evidence.md
?? docs/review/phase-3-p3-5-evidence-inventory-2026-08-25.md
?? docs/review/phase-3-p3-5-staging-and-operations-evidence.md
?? docs/review/phase-3-p3-5-test-and-evidence-traceability.md
?? tests/web/test_n7_access_log_redaction.py
```

`docs/review/Handover information` is **your** incoming handover, modified before
this session began and preserved untouched.

---

## 8. What this package must not be read as

- **Not** a request for the Phase 3 gate decision, or an input to one.
- **Not** EX-11 or EX-12. Both remain owed over the completed package.
- **Not** a claim that any staging procedure other than SP-12 has run.
- **Not** a claim that TC-OPS-05 passes — it **Failed**, and its fix is undeployed.
- **Not** authorization for anything: SG-2 and SG-3 remain ungranted, no host
  state was changed, and the filesystem rollback hold stands.
- **Not** a closure of I-06, A-05, A-06 or R-23.

No secret, credential, token, token hash, public key, cookie, CSRF value, raw
address or unnecessary identity datum was read, recorded or committed in producing
this package. The only database written to was the disposable `freedom_test`. No
service, no production data and no host configuration was mutated.

---

## 9. What I am asking for

1. An **independent implementation review** of the four artifacts, the three
   decisions, the criterion-4 amendment and the deployment-gate addition.
2. A **distinct, separately reported security-focused view of N-7** — the finding,
   the severity assessment in §4.1, and the remediation in §4.2.
3. **Blocking and Important findings**, which I will remediate and return for
   re-review.
4. Your view on one process question: **should the N-8 citations be folded back
   into the accepted contract**, or stay in the P3.5 artifact? I did not edit the
   contract, on the grounds that it is an accepted document and the choice is the
   Acceptance Authority's, but you may reasonably think a traceability contract
   that cannot be resolved mechanically should be repaired at source.
