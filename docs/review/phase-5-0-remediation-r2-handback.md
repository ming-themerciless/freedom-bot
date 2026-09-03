# Package 5.0 — design remediation R2 handback

Review disposition, 2026-08-29: **changes requested.** Codex kept P5.0-R1 and
P5.0-R4 Blocking and requested remediation R3. P5.0-R2 remains closed and OD-55
remains preserved. This handback is retained as superseded review evidence.

**Superseded by [`phase-5-0-remediation-r3-handback.md`](phase-5-0-remediation-r3-handback.md)
(revision 4, remediation R3), 2026-08-29.** Two claims below are **withdrawn** by
that remediation and must not be read as current: that termination plus
Google-side write-access revocation constitutes an *enforceable* Sheet fence, and
that a call accepted by Google before revocation *"is captured by the final
import"*. Package plan §2.10.2 concludes that no barrier for accepted-request
completion exists in the published Google APIs. The rest of this document — the
option comparisons, the database-side fence and the removal of self-attested
proof — stands and is carried forward.

Date: 2026-08-29 · Package 5.0 — Migration and cutover harness

Prepared by: Claude — implementer and working Technical Lead (designated, OD-61)

Returned to: Peter Duscha (Acceptance Authority, Product Owner, Data Owner,
Operations Owner, Delivery Lead) and Codex (Independent Reviewer and independent
logical-schema reviewer, OD-61).

In response to: `docs/review/Handover information`, *Package 5.0 — design
remediation R2 handoff*, which **authorizes design and documentation remediation
only**.

> **Claude claims no finding closed.** P5.0-R1 and P5.0-R4 are closed by the
> Independent Reviewer, not here. What follows is a design intended to close
> them, the comparison that produced it, and the decisions it raises.

---

## The seven required handback items

### 1. The revised plan and schema

| Artifact | Revision | What it now contains |
|---|---|---|
| [`phase-5-0-package-plan.md`](phase-5-0-package-plan.md) | **3 — remediation R2** | The two option comparisons (§2.10, §2.11), the rewritten cutover/rollback sequence (§7.2), the failure table (§7.1), the work breakdown and estimate (§3, §4), the reframed and new decisions (§5.3), the reduced numeric register (§8.3), the enlarged security-review scope (§9.2), the extended stop conditions (§9.3) and the handoff's nine-item evidence plan (§6.5) |
| [`phase-5-0-logical-schema.md`](phase-5-0-logical-schema.md) | **3 — remediation R2** | Five tables instead of six; the withdrawn lease and acknowledgement tables; the new `migration_quiescence_evidence` table (§3.5); the database authority fence (§2.2A); the lifecycle boundary (§2.2B, §2.3); observed-not-attested evidence (§2.4); the three-principal grant model (§4.3); and the preserved P5.0-R2 matrix (§2.1) and effective-time model (§2.5) |

### 2. An option comparison and recommendation for each Blocking finding

**P5.0-R1 — package plan §2.10.** The four options the handoff names, each
answered against `SIGSTOP`, process resume, GC pause, out-of-systemd duplicates,
a request already beyond its last check, partial shutdown, failed restart,
rollback and operator death; plus the two rejected designs from revisions 1 and 2,
retained so the record shows why they fail.

- **F-6** stop the legacy-writing process, verify at the process/cgroup level,
  restart a build whose legacy writer is disabled — *necessary, not sufficient
  alone; whole-bot outage.*
- **F-7** isolate the writer in a separately terminable helper process — **the
  recommended host-side control**; same guarantee as F-6 with the outage scoped
  to Sheet mutations.
- **F-8** revoke the Google write access for the cutover's duration — **the
  recommended independent second control**; the only mechanism that reaches a
  request past every local boundary. Its propagation latency must be measured
  (WP-13), and it is a production access change. **F-8b**, key rotation, is
  rejected: it removes reads too and a minted token stays valid.
- **F-9** a Google-supported conditional/fencing mechanism — **not available.**
  No precondition, ETag, `If-Match`, revision id or compare-and-swap exists on
  the Sheets v4 write methods. Stated as *not found in the published API
  surface*, not as a proof of absence.

**Recommendation: F-7 + F-8, with F-6 + F-8 as the declared fallback.** The two
controls are recommended together because their residuals are disjoint: the host
control makes the writer absent, the Google control makes its access absent.

**P5.0-R4 — package plan §2.11.** The three options the handoff names, each
traced for who authenticates the writer, which SQL principal PostgreSQL sees, who
may write which row, how credentials are provisioned and rotated, and whether a
compromised process can falsify another instance's proof.

- **O-1** per-role or per-instance principals with RLS or security-definer
  procedures — **rejected as the primary control.** `current_user` is a role, not
  an instance; it stops cross-process forgery and does nothing about a process
  forging its own proof, which is the case that matters. It also adds three
  distributed credentials.
- **O-2** a privileged coordinator that alone records observed evidence, with
  runtime roles holding no authority-proof write privilege — **the mechanism.**
- **O-3** remove runtime-authored acknowledgements entirely — **the
  recommendation**, available precisely because R1's remediation replaced a
  self-reported drain with an externally observed lifecycle event.

**Recommendation: O-3, realized through O-2.** One element of O-1 is kept: the
runtime role holds no write privilege anywhere on the authority plane.

### 3. The exact enforceable boundary that closes P5.0-R1

There are two, because there are two stores, and the handoff's counterexample
must be defeated in both.

**For PostgreSQL-authoritative writes — a `BEFORE` trigger inside the writing
transaction.** Every write to a database-authoritative table reads the unit's
current activated disposition *in that transaction* and is refused unless it is
`cutover` or `database`.

> The paused-process counterexample: a process paused after any check and resumed
> after activation commits nothing, because the check is not in the past. The
> check and the write are the same transaction. No elapsed time, lease, clock or
> snapshot participates. The runtime role holds `SELECT` only on dispositions, so
> no process can lie to the trigger.

**For the Google Sheet — the writer process does not exist, and its credential
cannot write.**

> **The process:** the Sheet write surface (today one function,
> `connectors/sheets.py:31`, called from `models/actor.py:230` and
> `models/trade.py:66`) moves into `freedom-sheet-writer`, its own systemd unit.
> `systemctl stop` terminates its cgroup; the `SIGKILL` escalation kills a
> `SIGSTOP`ped process, because `SIGKILL` is not blockable and is delivered to a
> stopped process. **A killed process cannot resume**, which is exactly the
> property the lease lacked. Termination is proved as an empty set: the unit
> reports `inactive`/`dead`, its `cgroup.procs` is empty, and a host-wide scan
> finds no other process running the writer entry point.
>
> **The credential:** the service account's Drive **write** permission on the
> spreadsheet is downgraded for the duration of the cutover. Google evaluates it
> when the request arrives, so a request that escaped every host-side control —
> a duplicate, a survivor, a call dispatched late — is refused with `403` by
> Google rather than by us.

**Ordering, which is part of the boundary and not a detail:** revoke access →
stop the unit → observe termination three ways → wait N5.0-17 for any dispatched
call to return → run the owning package's import or replay → activate → restart
the writer → restore the permission.

**The residual, stated and not mitigated away.** `host_scan_clear` is a
point-in-time observation, so a writer started between the scan and the
activation is not observed. It writes nothing, because its access is revoked —
but that depends on the revocation having propagated, which Google does not
contractually specify and which **WP-13 must measure** before N5.0-18 is fixed.
Recorded as **R-5.0-5**, narrowed: it no longer includes the paused-process case.

### 4. The database-enforced identity/ownership model that closes P5.0-R4

**No application process writes any authority proof, for any instance, including
its own.** The tables that held self-attested proof — `migration_authority_leases`
and `migration_quiesce_acknowledgements` — are **withdrawn**, not secured.

| Principal | Authenticated how | Holds, on the five package-5.0 tables |
|---|---|---|
| schema owner | host-local, by the deployment | DDL and the migration's seed. Defeated by the append-only triggers for `UPDATE`/`DELETE`, as it is for `audit_events` today |
| `__APP_ROLE__` — shared by `freedom-bot`, `freedom-web`, `freedom-worker`, `freedom-sheet-writer` | password/socket credential in each service's environment file | **`SELECT` on four tables; nothing at all on `migration_quiescence_evidence`.** No `INSERT`, `UPDATE`, `DELETE` or `TRUNCATE` anywhere in this package |
| **`freedom_migration_coordinator`** — proposed, D5.0-11 / OD-64 | **peer** authentication over the Unix-domain socket, by the host account running `python -m tools.migration_authority`. No password, no TCP login, no service unit references it | `SELECT, INSERT` on revisions, dispositions and quiescence evidence; `SELECT` on units and transitions. No `UPDATE`, no `DELETE`, no `TRUNCATE` |

**Credentials.** The coordinator has none to distribute: peer authentication makes
the secret host access, already governed by
`docs/operations/break-glass-credential-custody.md`. Rotation is a `pg_hba.conf`
and grant change, not a secret redistribution. No environment file, `.env`,
service unit or secret store gains an entry.

**Can a compromised bot, web or worker process falsify another instance's proof?**
No, and it cannot falsify its own either — there is no row it is permitted to
write. The forgery class is **unconstructable**, and the evidence for that is a
`has_table_privilege` assertion rather than a test that attempts and fails.

**What the evidence contains** is what a supervisor observed — systemd's
`ActiveState`/`SubState`, an empty cgroup, a clear host scan, Google's own
response to the permission change — never what the fenced writer said about
itself. The activation trigger reads only those rows.

**This is a database role and credential-topology change.** It requires an impact
assessment and the named Security Reviewer's review, and it is raised as
**D5.0-11 / OD-64** rather than adopted. It does not change the accepted
production topology: OD-20, OD-21 and OD-22 stand — same host, loopback, separate
roles and environment files. **If the preferred solution would change the
accepted production topology or credential contract, work stops for Peter's
ruling before it is treated as binding** (package plan §9.3, stop condition 2).

### 5. Changed decisions, credentials, topology, estimates, risks and tests

**Decisions.**

| Ref | Change |
|---|---|
| **D5.0-9 / OD-62** | **Reframed, not extended.** The revision-2 options were priced around the lease and are withdrawn. The question is now which enforceable boundary is adopted and which of its three costs — a bounded Freedom-bot mutation outage, a fourth systemd unit holding the Google credential, or a production Drive-permission change at each cutover — is accepted. Four options, priced. **Blocks WP-4b** |
| **D5.0-10 / OD-63** | **Reduced from seven controls to four.** N5.0-9 … N5.0-13 and N5.0-15 are withdrawn with the lease. N5.0-14 is retained; N5.0-16, N5.0-17 and N5.0-18 are new. **N5.0-18 should be ruled after WP-13 measures it**, not before |
| **D5.0-11 / OD-64** | **New.** The authority-plane database principal. **Blocks WP-2** |
| D5.0-1 … D5.0-8 | Unchanged. OD-60 is explicitly unaffected: the coordinator is a *database role for a human-run command*, not a service principal |

**Credentials and topology.**

- **Proposed:** one new database role, `freedom_migration_coordinator`, peer
  authenticated, with no secret to distribute (D5.0-11).
- **Proposed:** the Google service-account credential moves out of the Freedom
  bot process and into `freedom-sheet-writer` (D5.0-9, option A). The bot process
  then holds no Sheets write credential at all.
- **Proposed as a cutover procedure, not an implementation step:** a production
  Drive permission is revoked and restored at each fenced transition (D5.0-9).
- **Withdrawn:** revision 2's standing PostgreSQL availability dependency for
  Freedom-bot mutations. With the lease gone, the bot's legacy mutation path takes
  **no** runtime database dependency; only a startup authority read remains.
- **Unchanged:** OD-20/21/22 production and staging topology; no service moves, no
  port opens, no credential is shared.

**Estimate.** PERT **23.7** implementer-days, up from 20.8. Decomposed: −2.0 for
withdrawing the lease apparatus; +2.5 for the separately terminable writer; +1.4
for the coordinator principal and observed evidence; +1.0 for the Google-access
feasibility measurement. Remediation allowance 6.8 days; contingency 3.0; security
review raised to 1.0–1.5 reviewer-days. Confidence low-to-moderate, with drivers
stated in package plan §4.

**Risks.** R-5.0-2 superseded a second time; **R-5.0-5 restated and narrowed** —
it no longer includes the paused-process case; **R-5.0-6 restated** — the
PostgreSQL availability dependency is withdrawn and replaced by the fence-window
mutation outage; **R-5.0-7 new** — a Drive permission revoked and not restored;
**A-5.0-3 new and unconfirmed** — disposable Google resources for WP-13; **D-5.0-2
extended** to three rulings.

**Tests.** The clock-injection band is **withdrawn** — no fencing decision
measures elapsed time in a process, so there is nothing to inject. Added:
held-transaction fence refusals across an activation, two connections and a
barrier; termination of a `SIGSTOP`ped writer with an empty-cgroup assertion; an
out-of-systemd duplicate detected by host scan and refused at the API boundary;
an in-flight external call held at the dispatch boundary; a per-principal direct-
SQL denial matrix; four activation-proof refusals (forged, missing, stale,
cross-revision); a failed shutdown that records nothing and refuses; and an
assertion that `observed_detail` never carries credential material. Package plan
§6.5 maps each to the handoff's nine required evidence items.

### 6. Confirmation that P5.0-R2 and OD-55 remain preserved

**P5.0-R2 — preserved.** The accepted state matrix is restated **in full** in
logical schema §2.1 rather than referenced, so a reviewer can diff it. Every
accepted element stands unchanged:

- PostgreSQL is read- and write-authoritative in `cutover`;
- `database` is accepted completion — `cutover → database` transfers nothing and
  closes the bounded verification window;
- authority transfers at `shadow → cutover`;
- authorization and activation are separate operations;
- only an activated disposition carries authority, and authority is never read
  from the revision table;
- `effective_at` is the earliest instant a revision may be **activated**, not an
  instant at which anything becomes true;
- `verification_until` is required for `cutover` and forbidden for `database`;
- no state dual-writes, in any of the four columns.

The only change touching this area is the **removal of `lease_horizon_at`** from
the revision table, which existed solely for the withdrawn lease protocol and
carried no P5.0-R2 semantics.

**OD-55 — preserved.** Package 5.0 still creates no comparison-telemetry table,
column, grant, write path, decision-table row, access pattern, evidence claim or
risk. The common contract remains prose in package plan §11, unchanged, with
package 5.1 recorded as the implementation and schema owner and OD-56's
constraints carried into it. R-5.0-4 stays re-owned by 5.1.

**OD-54, OD-56 … OD-61** are traced in package plan §5.2 with any change in how
they are realized named. **OD-58** stands: no ledger table, and R-P4-4 remains
Active and owned by package 5.2.

### 7. Explicit statement that no implementation or environment change occurred

**No implementation or environment change occurred in producing this
remediation.**

- No production code was written or modified.
- No migration was written; migration `0014` does not exist and the head remains
  `0013`.
- No table, index, trigger, sequence, grant, database role or `pg_hba.conf` entry
  was created or altered, in any database.
- No configuration file, environment variable, `.env`, systemd unit or deployment
  artifact was created or altered. `freedom-sheet-writer` is a proposal in a
  document, not a unit on this host.
- No credential was read, written, created, rotated, revoked or distributed.
- **No Google access was changed.** No Drive permission, spreadsheet ACL or
  service-account key was read, modified or exercised. No Sheet was accessed, in
  any mode.
- No service was deployed, started, stopped or restarted.
- No data was mutated, in any database.
- No authority cutover occurred; every migration unit remains `Legacy` in the
  controlled register, and no control plane exists to record otherwise.
- No Package 5.1+ work was begun.
- **No test was run for this package, because no code exists for it.** The
  environment facts in package plan §8.1 are dated observations of this host and
  each states how it was observed; the code facts in §2.9 are the result of a
  repository-wide search on 2026-08-29.

The changed files are: the two design artifacts, this handback, and the status,
RAID, decision, open-decision and change-log registers.

---

## What is requested next

1. **Codex independent re-review** of both design artifacts, against P5.0-R1 and
   P5.0-R4, with P5.0-R2 and OD-55 confirmed still closed and still applied.
2. **Peter's rulings** on D5.0-9 / OD-62 (reframed), D5.0-10 / OD-63 (reduced)
   and D5.0-11 / OD-64 (new).
3. **A named Security Reviewer**, whose scope is now larger: a new database
   principal, a credential relocation and a production-access procedure.
4. **Confirmation of A-5.0-3** — that a disposable Google spreadsheet and service
   account can be made available for WP-13. If they cannot, N5.0-18 stays
   unmeasured, F-8 cannot be relied on, and D5.0-9's option set narrows to B or D.

**Implementation remains unauthorized.** No work package starts while either
Blocking finding, D5.0-9, D5.0-10, D5.0-11 or the Security Reviewer assignment
remains open.
