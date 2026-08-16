# Phase 3 P3.0 remediation submission — after Codex review and the P3.G0 decision

**Date:** 2026-08-13

**Package:** P3.0 remediation, prepared from
`docs/review/phase-3-p3-0-remediation-claude-prompt.md` after the Codex
architecture/security review and Peter Duscha's P3.G0 remediation decision of the
same date.

**Author:** Claude, operating as Working Technical Lead under Peter's designation.

> **Superseding acceptance note, 2026-08-13:** Codex completed the requested
> architecture and distinct security-focused re-review. Peter Duscha accepted
> the complete remediated P3.0 baseline, corrected N-43 (with its recovery-bound
> wording clarified), widened N-65, new N-67 and ADR 0010. P3.G0 is closed and
> P3.1 is authorized subject to confirmation of its disposable-PostgreSQL
> prerequisite. The dated submission below is preserved as the pre-decision
> record; its statements that acceptance was pending are historical.

**Status at submission:** **Submitted for re-review. Nothing here was then
accepted.** This package is
documentation and design only. No route, dependency, migration, framework
scaffold, service, template or runtime module was added; nothing was deployed or
started; no external service was contacted, no secret inspected, no production
data read, and no file under `design-prototype/` altered.

**Requested next step:** Codex independent architecture re-review and a
**distinct** security-focused re-review, then Peter's P3.G0 decision.

---

## 1. What the decision required, and what was done

| # | Finding | Severity | Disposition |
|---|---|---|---|
| 1 | Account attribution versus the legacy audit constraint | Blocking | **Remediated.** The constraint is replaced, not supplemented; the three append-only tables are treated on their own evidence; nine named PostgreSQL tests |
| 2 | Indirect Council escalation from break-glass | Blocking | **Remediated.** N-67 allowlist plus mapping provenance plus ratification route R-38; three independent enforcement points; TC-BG-05 withdrawn and replaced by five tests |
| 3 | Unreachable job attempt exhaustion | Blocking | **Remediated.** One meaning for `attempts`; a two-branch atomic reaper; a constraint that makes the stranded state unrepresentable |
| 4 | PKCE verifier contradiction | Important | **Remediated.** State is hashed, verifier is encrypted, AAD-bound and erased at consumption; said identically in every contract |

Peter's five decisions are preserved exactly as recorded. D-1 (`freedom-worker`)
and D-2 (apply as a durable job) are untouched. D-3's approved narrow surface is
kept and made enforceable. D-4's provisionally approved values are unchanged
except N-43, which was withheld and is now redefined. D-5's ADR keeps its
**conditionally accepted** status.

## 2. Finding 1 — account attribution versus the legacy audit constraint

### 2.1 What was actually wrong

The first revision added a permissive `NOT VALID` check and left migration 0001's
`ck_audit_events_human_action_has_an_actor` standing. Check constraints are
conjunctive, so a break-glass audit event — `actor_capability =
'platform_administrator'`, account set, `actor_discord_user_id` **null** —
satisfies the new rule and violates the old one. Because SM-03 commits an
emergency session and its audit event in one transaction, **the emergency login
itself would have failed**. The design did not deliver the availability half of
OD-43 at all.

Two further facts were found while remediating, neither of which the review named:

- **There is an application-level copy of the same rule.**
  `application/audit.py` defines `UNATTENDED_CAPABILITIES = {SERVICE_PRINCIPAL,
  SYSTEM}` and `AuditEvent.__post_init__` refuses any other capability without a
  Discord user id — with the comment *"They match the `human_action_has_an_actor`
  check constraint."* It would raise before SQL was reached. P3.1 changes both in
  one revision or neither.
- **The append-only trigger is from migration 0002, not 0005.** Ten statements
  across the package said 0005. Migration 0005 is the submission-admission fence.
  Corrected everywhere.

### 2.2 The three tables do not have the same shape

Read from the migrations rather than assumed, because the prompt was right to
warn against symmetry:

| Table | Legacy attribution constraint | Action |
|---|---|---|
| `audit_events` | `ck_audit_events_human_action_has_an_actor` — Discord id or a machine capability | **Replaced** |
| `foundry_snapshots` | **None.** `received_by_discord_user_id` is nullable; the constraints that exist govern the *channel* (`received_via` / `submitted_by_principal`) | Column and FK only. **No constraint added** — a supervised-bootstrap row that names no human is legitimate, and migration 0004 says why |
| `snapshot_imports` | **None**, and weaker than `audit_events`: a `guild_council` import row may name nobody today | Column and FK, **plus** a new `NOT VALID` attribution check binding new rows only |

The symmetric fix would have introduced an invariant that the platform's own
bootstrap path violates.

### 2.3 The DDL, and why it is safe

Wider rule added `NOT VALID` **first**, narrower rule dropped **second**, in one
transaction, so the table is never less constrained than it is today. Four
properties, each checkable:

1. **No row is read, locked for write, updated or deleted.** `ADD COLUMN` without
   a default, `ADD CONSTRAINT … NOT VALID` and `DROP CONSTRAINT` are catalogue
   operations. Row triggers do not fire for DDL, so `audit_events_append_only` is
   not suspended, dropped or evaded — it is never reached, which is a different
   claim and a better one.
2. **The replacement is implied by what it replaces** (`A ⟹ X ∨ A`), so no
   existing row can be invalidated. That is a proof, not a measurement, which
   matters because P3.0 has not inspected the production database and must not.
3. **Both machine cases survive** unchanged.
4. **An unattributed human action is still refused.** The rule was not relaxed;
   its subject widened from *a Discord user* to *an identified person*.

Validation is a separate optional revision and is **possible and safe** — it takes
`SHARE UPDATE EXCLUSIVE`, reads, and modifies nothing — correcting the first
revision's claim that it was impossible. Nothing depends on it, because
PostgreSQL enforces a `NOT VALID` check on every insert regardless.

The downgrade restores the legacy constraint **`NOT VALID`**, because by then the
table may hold account-attributed rows that a validating restore would choke on,
and it names what it costs: dropping the column discards the attribution of any
event a break-glass session wrote.

### 2.4 Where and what to test

| Where | Change |
|---|---|
| `docs/contracts/phase-3-logical-schema.md` §6 | Rewritten: the finding, the two decisions, the three-table inventory, the exact DDL, locking, validation stance, downgrade, and §6.6's test list |
| `docs/contracts/phase-3-identity-migration-contract.md` §3 stage A, §8 | The swap, the per-table table, the guard-changes-with-it rule, control totals **T7** and **T8**, the downgrade cost, and the fourth attribution property |
| `docs/adr/0010-…md` D5, context, alternatives | Rewritten; a new rejected alternative (a placeholder Discord id, rejected as putting a lie in the audit trail) |

Named tests, all `automated (database)`: **TC-AUD-09** (history byte-identical,
`xmin` unchanged), **TC-AUD-10** (ordinary and break-glass account attribution
both insert, and both are refused at the previous revision), **TC-AUD-11**
(unattributed human action refused by the constraint *and* by the application
guard), **TC-AUD-12** (`system`/`service_principal` still valid),
**TC-AUD-13** (`UPDATE`/`DELETE` still denied for runtime and owner roles,
including an update touching only the new column), **TC-AUD-14** (validation
succeeds and changes nothing), **TC-MIG-14** (upgrade→downgrade→upgrade, with the
downgrade exercised against a database that already holds account-attributed
rows), **TC-MIG-15** (constraint inventory equality, so a later migration cannot
reintroduce a Discord-only rule), **TC-BG-15** (end to end with Discord faulted:
session and audit event commit together).

## 3. Finding 2 — indirect Council escalation from break-glass

### 3.1 Why the allowlist alone is not the answer

The review's attack is one hop: break-glass maps a role to `guild_council`, then
an ordinary Discord login collects it. But confining break-glass to
`platform_administrator` mappings only moves the hop:

```text
BG ─ maps role X → platform_administrator ─▶ ordinary login as administrator
                                              └─ maps role X → guild_council,
                                                 as administrators legitimately may
```

The second step is an ordinary administrator doing an administrator's job
(threat model T-53), so no rule *about break-glass sessions* can see it. The
guard has to travel with the mapping.

### 3.2 The guard

1. Every mapping records the **administrator scope** of the session that created
   it: `emergency_continuity` when `auth_method` is not `discord_oauth`, **or**
   when every active mapping conferring `platform_administrator` on that session
   is itself emergency-provenance. Otherwise `full`.
2. A mapping created under continuity scope may name only
   `platform_administrator` — **N-67**.
3. Administrator capability held *only* through emergency-provenance mappings is
   itself continuity-scoped. Transitive by construction, so the second hop above
   is refused exactly as the first was.
4. The exit is **ratification (R-38)**: a full-scope administrator on an
   ordinary-provider session adopts the mapping. The protected bootstrap mapping
   is inserted by migration and is `full` by construction, so a full-scope anchor
   always exists.

The invariant a reviewer can test is a property of *sequences*:

> No series of mapping changes beginning in a break-glass session and passing
> through any number of ordinary logins yields Council, character or import
> authority before ratification.

**Three independent controls**, in line with the instruction not to rely on the
short-circuited capability set: the application service's scope check; the check
constraint `created_under_scope = 'full' OR capability = 'platform_administrator'`
(which depends on **what is written**, not on who is writing); and N-65's route
surface. Every attempt, permitted or refused, is recorded in the append-only
`role_capability_mapping_events` table with the attempted capability and a refusal
code.

### 3.3 Exactly what a continuity-scoped caller may do

| Operation | Permitted | Continuity need |
|---|---|---|
| Create `(guild, role, platform_administrator)` | **Yes** | The Discord role carrying administrator authority was deleted and recreated with a new snowflake, or the guild was rebuilt, so the protected mapping points at a role nobody can hold. Without this, recovery requires database-owner action |
| Revoke a non-protected `platform_administrator` mapping | **Yes** | Administrator authority sits on a compromised or mis-assigned role and no ordinary administrator can log in to withdraw it. Subtractive; confers nothing |
| Anything naming `guild_council`, `dm`, `character_owner`, `guild_member` | No | Game and governance authority — the escalation itself |
| Any change to the protected mapping | No | Refused for every caller by trigger (OD-24). Continuity is anchored to it |
| Ratify (R-38) | No | A continuity-scoped caller ratifying its own mapping is the guard, self-cancelled |
| `character_access`, identity link/unlink, any import route | No | Already refused by N-65; restated so the set is exhaustive |

**Honest residual, RR-13:** a break-glass session can leave durable
*continuity-scoped* administrator capability behind. That is persistence, not
escalation — the capability reaches no Council, character or import route — and it
is exactly what the recovery case needs. It is recorded rather than argued away.

### 3.4 Where

| Artifact | Change |
|---|---|
| Logical schema §8, **§8.1, §8.2** | Provenance/scope/ratification columns, six new check constraints, the one-way provenance trigger, the finding and the guard, the exhaustive operation table, the `role_capability_mapping_events` column list |
| Route contract §2.3, §3.1, **§3.3**, §5, §5.1, §5.2, §9 | Caller state `AC`; the rule binding it to the `BG` column; **R-38**; N-67 enforcement on R-33/R-34; `✓ N-67` legend; the `403 emergency_scope_refused` denial row |
| State machines SM-02, SM-03, **SM-07** | The forbidden "arranging" transition; SM-07 for mapping provenance with its own failure behaviour |
| ADR 0010 **D9.1** | Why capability resolution is not enough and why the allowlist alone is not either |
| Threat model **T-10b**, T-53, RR-13 | The indirect path as its own entry |
| View model VM-12 | `administrator_scope`, `provenance`, `ratifiable`, `ratified_*`, `unratified_count`, `scope_notice_code` — all explicitly *not* the control |
| Numeric register | **N-67** new; **N-65's subject widened** (see §6) |
| Operational contract §5, §6 | Unratified-mapping and mapping-refusal signals; the ratify-or-revoke recovery step |

Tests: **TC-BG-05 withdrawn** — it asserted that the mapping change *succeeds* and
checked only the emergency session's own capability set, so it would have passed
while the platform was escalatable. Replaced by **TC-BG-05a** (direct service,
parametrized over every forbidden capability, with the refusal record asserted),
**TC-BG-05b** (direct HTTP, never rendering R-32), **TC-BG-05c** (the full
sequence through an ordinary login, asserting no Council and no import),
**TC-BG-05d** (the constraint alone, application bypassed, runtime *and* owner
roles), **TC-BG-05e** (ratification is the only exit and is one-way). Plus
**TC-CAP-08…11** for scope resolution, the `AC` matrix mirror, rotation on
ratification, and the mapping-event record.

## 4. Finding 3 — unreachable job attempt exhaustion

### 4.1 Why it could not work

The reaper requeued `WHERE … attempts < 3`; `running → failed` was described as
happening on "the 4th claim". Both cannot hold. After the third lease expired with
`attempts = 3` the reaper's predicate excluded the row, so it stayed **`running`
with no worker and no lease, permanently** — and had it been requeued, the fourth
claim would have set `attempts = 4` and violated `CHECK (attempts <= 3)`, aborting
the worker's transaction rather than failing the job. The job was unreachable from
every terminal state, which is the opposite of what a retry cap is for.

### 4.2 The redesign

**One meaning:** `attempts` is the number of **claims**. The claim statement
increments it; nothing else writes it. Cap 3.

**One new constraint** makes the stranded state unrepresentable rather than merely
avoided:

```sql
CHECK (state <> 'queued' OR attempts < 3)   -- a queued job always has an attempt left
```

**One reaper statement, two branches**, so exhaustion is detected by the same
statement that would otherwise retry:

```sql
UPDATE reconciliation_jobs SET
    state        = CASE WHEN attempts < 3 THEN 'queued' ELSE 'failed' END,
    lease_owner  = NULL, lease_expires_at = NULL, heartbeat_at = NULL,
    failure_code = CASE WHEN attempts >= 3 THEN 'attempts_exhausted' END,
    finished_at  = CASE WHEN attempts >= 3 THEN now() END,
    version      = version + 1
WHERE id IN (
    SELECT id FROM reconciliation_jobs
    WHERE state = 'running' AND lease_expires_at < now()
    ORDER BY lease_expires_at
    FOR UPDATE SKIP LOCKED LIMIT 20
) RETURNING id, state, attempts, correlation_id;
```

The `CASE … END` expressions yield `NULL` on the requeue branch, so the existing
terminal-state check constraints hold on **both** branches of one statement — if a
later edit breaks that, the constraint rejects the statement rather than a
reviewer having to notice.

- **Concurrent reapers:** `FOR UPDATE SKIP LOCKED` means each row is transitioned
  by exactly one; the other skips. `LIMIT 20` bounds a pass.
- **Lost worker:** nothing in recovery asks the worker anything. Three lease
  expiries later the job is `failed` with `attempts_exhausted`.
- **Worker self-abandon** (N-45 hard cap, kill switch) applies the same two
  branches under `AND lease_owner = $2`; if the reaper already acted it matches
  zero rows and the worker exits quietly.
- **Deterministic refusal** (`parse_refused`, `artifact_unavailable`) fails
  immediately whatever `attempts` says. Retrying a refusal that will recur is 30
  seconds of work to reach a conclusion already in hand.
- **Claim predicate** carries a redundant `attempts < 3`: a claim that matches no
  row moves on, where a claim that violates a constraint aborts a transaction.
- **Bounded time to terminal:** `N-23 + N-44` per remaining attempt — at most
  3 × 75 s ≈ 225 s of lease-expiry time. **No job remains `running`
  indefinitely.**
- **Audit:** the terminal branch writes `reconciliation.job_failed` in the same
  transaction, satisfying delivery plan §8.2. A job may therefore be failed by a
  process that never executed it; recorded as residual **RR-14**.
- **Liveness is now a monitored dependency:** the reaper is the only writer of the
  expiry transition, so the operational contract adds an *oldest expired lease*
  signal and a `expired_leases` health check, and the recovery table says a stuck
  job means a stopped reaper — never a manual `UPDATE`.

Where: numeric register **N-43** (redefined), logical schema §10.1, state machines
SM-05 (states, transitions, a *why the first revision could not work* section, six
new forbidden transitions, lost-worker and concurrent-reaper behaviour),
operational contract §5–§6, view model VM-16.

Tests: **TC-JOB-05** rewritten to walk attempts one through exhaustion on real
PostgreSQL, asserting `queued` after expiries 1 and 2 and `failed` with
`attempts_exhausted` after expiry 3, with no claim ever raising a constraint
violation. **TC-JOB-13** rewritten for **two concurrent reapers** across jobs at
`attempts` 1, 2 and 3, asserting exactly one transition each and that **no job is
`running` after the pass**. New **TC-JOB-15** (the stranded state is refused by
the constraint) and **TC-JOB-16** (worker self-abandon racing the reaper, in both
orders).

## 5. Finding 4 — PKCE verifier contradiction

The route contract said the transaction row holds *"hashes of state and verifier"*;
the schema said the verifier is encrypted because it must be recovered. The schema
was right, and the route contract described a flow that cannot complete: PKCE
requires presenting the original verifier at the code exchange, and a hash cannot
be presented.

Every contract now says the same thing:

- **`state` is hashed** (SHA-256), compared in constant time. It is only ever
  compared, so a plaintext copy would be a liability with no use.
- **The verifier is encrypted** under the approved authenticated-encryption
  boundary — AES-256-GCM with versioned keys from `WEB_TOKEN_ENCRYPTION_KEYS`, the
  same key-management story as the OAuth tokens rather than a second one. The GCM
  **additional authenticated data binds `(transaction id, key_version,
  provider_key)`**, so a ciphertext moved to another transaction row fails to
  authenticate instead of completing somebody else's exchange.
- **Recovery and erasure are one statement.** A CTE selects the row `FOR UPDATE`
  under `consumed_at IS NULL AND expires_at > now()`, the `UPDATE` sets
  `consumed_at` and nulls the ciphertext, and `RETURNING` yields the *pre-update*
  values. The callback gets the verifier exactly once; a second callback blocks,
  re-checks, matches zero rows and is refused. Two new check constraints keep it
  true afterwards, including `CHECK (consumed_at IS NULL OR
  pkce_verifier_ciphertext IS NULL)`.
- **Retention:** erased at consumption; row deleted 24 hours after expiry; never
  in a log, audit payload, response, redirect or error message.

Where: route contract §4.1 R-03 and R-04, logical schema §9.2 and new **§9.2.1**,
schema §11 decision table, state machines SM-01 forbidden transitions.

Tests: **TC-AUTH-07** strengthened — no column holds the plaintext *or its
SHA-256*, which is the assertion that would have caught the contradicted contract.
New **TC-AUTH-12**: the callback recovers the original verifier and completes;
the ciphertext moved to another row fails to decrypt; after consumption the
columns are null and a second callback recovers nothing; two concurrent callbacks
yield exactly one exchange.

## 6. Decisions preserved, and the three that need Peter

**Preserved unchanged:** D-1 (`freedom-worker`), D-2 (apply as a durable job),
every provisionally accepted numeric value N-30–N-42 and N-44–N-64 and N-66, the
closed route set and its exhaustiveness claim, the `403`/`404` denial split, the
seven caller states and every existing matrix cell, the `vm-1` view-model set, the
four-stage migration and its rollback boundary, the dependency proposal, the CSP
conclusion, the operational topology and the worker finding. ADR 0010 stays
**conditionally accepted**; P3.G0 stays **open**; P3.1 is **not** authorized.

**Requiring Peter's decision at the re-review, beyond the original five:**

| # | Item | Why it is Peter's |
|---|---|---|
| 1 | **N-43, redefined.** The withheld definition is replaced by claim-counting semantics, the `queued`-implies-attempt-remaining constraint, and the two-branch reaper | He withheld it explicitly and asked for a coherent atomic transition |
| 2 | **N-65's subject widened**, value and surface unchanged: from "a break-glass session" to "a continuity-scoped session", which additionally covers an ordinary-provider session whose administrator capability descends only from emergency mappings | It widens the subject of a provisionally accepted policy. Without it the restriction is shed by logging in through Discord, so the remediation does not hold — but it is still a change, and it is not made silently |
| 3 | **N-67, new**, with route R-38 and the mapping provenance columns | D-3's conditional approval required a defined and tested allowlist; this is that definition, plus the provenance the allowlist needs to work |

Two smaller judgements, made inside P3.0's authority and flagged so they can be
disagreed with specifically: the eighth caller state `AC` has **no matrix column**
and is bound to the `BG` column by a stated rule plus a test that re-runs the whole
inventory (TC-CAP-09); and R-38 requires **one** full-scope administrator rather
than two, because the community has one accountable Server Administrator and a
two-person rule that cannot be satisfied is a control that will be worked around.

## 7. Files changed

Nothing outside documentation was touched.

| Path | Change |
|---|---|
| `docs/contracts/phase-3-logical-schema.md` | §6 rewritten (constraint swap, three-table inventory, DDL, tests); §8 extended with provenance columns and constraints; **§8.1, §8.2** new; **§9.2.1** new; §10.1 rewritten (attempts, claim predicate, new constraint, reaper, self-abandon, bounds); §3, §11.2 and §12 corrected |
| `docs/contracts/phase-3-route-authorization-contract.md` | §2.3 denial rows; §3.1 caller state `AC`; §3.2 legend; **§3.3** new; R-03/R-04 PKCE; R-32–R-34 detail and **R-38**; §5 route table and §5.2 matrix; §9 traceability; migration-0002 correction |
| `docs/contracts/phase-3-state-machines.md` | SM-01 forbidden transitions; SM-02 and SM-03 forbidden transitions; **SM-05 rewritten**; **SM-07 new**; §7 traceability |
| `docs/contracts/phase-3-numeric-policy-register.md` | Header change table; **N-43 redefined**; **N-65 subject widened**; **N-67 new**; N-44 rationale |
| `docs/contracts/phase-3-identity-migration-contract.md` | Stage A constraint swap and per-table treatment; downgrade and its cost; control totals **T7, T8**; §8 fourth property |
| `docs/contracts/phase-3-threat-model.md` | **T-10b new**; T-10, T-52, T-53 corrected; **RR-13, RR-14** new; verification mapping; migration-0002 correction |
| `docs/contracts/phase-3-test-traceability.md` | **TC-BG-05 withdrawn**; TC-BG-05a…05e, TC-BG-15, TC-AUTH-12, TC-AUD-09…14, TC-MIG-14…16, TC-CAP-08…11, TC-JOB-15, TC-JOB-16 added; TC-JOB-05 and TC-JOB-13 rewritten; TC-AUTH-07 strengthened; `[MATRIX]` note; §18 coverage rows |
| `docs/contracts/phase-3-view-model-contract.md` | VM-12 scope/provenance/ratification fields; VM-16 `expired_leases` check; §10 row |
| `docs/contracts/phase-3-operational-contract.md` | §5 three signals; §6 three recovery rows |
| `docs/contracts/README.md` | Status, reading-order descriptions, threat count |
| `docs/adr/0010-…md` | Status; context; **D5 rewritten**; **D9.1 new**; security consequences; a new rejected alternative; open questions |
| `docs/adr/README.md` | 0010 status row |
| `docs/project-management/change-log.md` | New dated entry, decision **Not yet decided** |
| `docs/project-management/status.md` | Status date, milestone row, critical path item 2, next-update trigger |
| `docs/project-management/decision-register.md` | OD-43 row |
| `docs/project-management/raid-register.md` | R-26 widened; **R-29** added |
| `docs/review/phase-3-p3-0-submission.md` | A superseding note at the head. The body is left as the dated record of what was first submitted |
| `docs/review/phase-3-p3-0-remediation-submission.md` | This document |

## 8. Commands run, and their exact outcomes

All from `/opt/discord-bots/freedom-bot` on 2026-08-13.

| Command | Outcome |
|---|---|
| `git status --short` (before) | 5 modified, 2 untracked paths — the P3.0 package plus the remediation prompt. No unrelated work to preserve |
| `git diff --check` | **No output; exit status 0.** No whitespace or conflict-marker defects |
| `sha256sum --check docs/review/phase-3-visual-freeze-manifest.sha256` | **14 of 14 `OK`, zero failures.** The frozen visual baseline is untouched |
| `./venv/bin/python -m pytest -q` | See §8.1 |
| Relative-link check over every created and changed Markdown file (ad-hoc Python, existence of each non-URL link target) | **Zero broken links** after this file was written. Before it existed, the two links pointing at it were reported and are now resolved |
| Secret-shape scan (`grep -E` for DSNs, PEM headers, `client_secret=`, `password=`, bearer tokens, Slack-shaped tokens) over the contracts, ADR, management records and review documents | **One match, a false positive:** the previous submission's own sentence describing its secret scan. No secret-shaped value |

### 8.1 Test run, stated precisely

`./venv/bin/python -m pytest -q` — **1968 passed, 253 skipped, 1 warning**.
No failures.

- **All 253 skips are `TEST_DATABASE_URL is not configured`**, the disposable
  PostgreSQL condition the delivery plan §10 records as *"must be re-confirmed
  before P3.1"*. This package changed no code, so the skip set is identical to the
  one the first submission reported. **No database evidence is claimed by this
  package.**
- The single warning is the pre-existing `audioop` deprecation from Pycord,
  unrelated to this work.
- The two repository-local documentation checks that exist both pass:
  `tests/test_field_ownership_document.py` (field-ownership matrix against the
  profile and the controlled migration manifest) and
  `tests/test_rejected_scope_absent.py` (the rejected ADR 0008 scope stays absent).
- No tooling was installed. The design-prototype tools (`check_css_tokens.py`,
  `calc_contrast.py`) were **not** re-run: no prototype file changed, and the
  freeze manifest proves it.

### 8.2 Checks that were not run, and why

| Check | Why not |
|---|---|
| Every test named in this package | **None has been written.** They are a specification for P3.1–P3.3, and no evidence from them is claimed anywhere |
| Any real-PostgreSQL execution of the DDL in §2.3, the reaper in §4.2 or the consumption statement in §5 | P3.0 writes no migration and no code. The SQL is reviewed as design; TC-MIG-14/15, TC-AUD-09…14 and TC-JOB-05/13/15/16 are where it becomes evidence |
| `alembic check` / migration consistency | No migration was added or edited |
| Formatter, linter, type checker | No Python file was changed. Running them would report only the pre-existing state of code this package did not touch |
| Staging, browser, real-device and assistive-technology evidence | Staging does not exist; the other three are recorded in the traceability §20 as requiring evidence Phase 3 does not yet have. Unchanged by this package |

## 9. What this remediation does **not** claim

- It does not claim the four findings are closed. **Codex closes them, or does
  not.**
- It does not claim the escalation analysis is complete. It claims one attack
  class, one guard with three enforcement points, one honest residual (RR-13), and
  a test that exercises the *sequence* rather than the hops. A reviewer who can
  name a fourth hop is naming a gap worth closing before P3.1.
- It does not claim the DDL has ever been executed. It has not.
- It does not claim P3.G0 may close, that ADR 0010 is accepted, that any numeric
  value is accepted, or that P3.1 may begin.
- It does not claim the portal is secure.

## 10. Re-review request

**To Codex, as Independent Reviewer** (architecture):

1. the constraint swap in schema §6.3 — is the ordering argument sound, is the
   implication argument sound, and is there any path by which the DDL touches a
   row;
2. whether treating the three append-only tables differently is right, or whether
   `snapshot_imports`' new check and `foundry_snapshots`' absence of one are the
   wrong way round;
3. SM-05 and schema §10.1 — does the two-branch reaper leave **any** reachable
   state in which a job neither terminates nor becomes claimable, under
   concurrency, restart, kill switch and a stopped reaper;
4. whether R-38 and the `AC` caller state are the smallest addition that closes
   finding 2, or whether the provenance model carries complexity that will be
   implemented wrongly;
5. whether the remediation broke anything it did not touch — particularly the
   route-set closure claim, the `vm-1` boundedness and the migration's rollback
   boundary.

**To Codex, in a distinct security-focused pass:**

1. **Finding 2 above all:** construct a sequence of mapping changes, logins,
   ratifications and revocations that yields Council, character or import
   authority from a break-glass start. If one exists, the guard is wrong;
2. whether the check constraint is genuinely independent of the application's
   scope resolution, or whether both ultimately trust the same computed value;
3. whether continuity scope can be *lost* incorrectly — a legitimate full-scope
   administrator wrongly confined during an incident is also a failure;
4. the PKCE consumption statement under `READ COMMITTED`: does the CTE plus
   `FOR UPDATE` genuinely yield exactly one recovery, and does the AAD binding
   cover what it needs to;
5. whether the audit constraint swap widens what may be written in any way beyond
   *an account instead of a snowflake* — in particular, whether any human
   capability can now be written with no attribution at all.

**To Peter, as Acceptance Authority and accountable Security Reviewer:** the
original five decisions, plus the three in §6.

---

P3.0 remediation submitted for Codex re-review; P3.G0 remains open and P3.1 has not started.
