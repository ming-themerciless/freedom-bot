# OD-63 / D5.0-10 — nine fencing numeric controls: ruling draft

Date drafted: 2026-08-31
Drafted by: Claude, implementer and working Technical Lead
Status: **SIGNED AND ACCEPTED — OPTION 1 — 2026-09-02**

This is the §0.2 change-control package for the one Package 5.0 decision that
carries **no Security Reviewer dependency** and is therefore rulable today.
OD-64, OD-65 and OD-66 are owned *on the Security Reviewer's review* and cannot
be ruled until Codex returns a recommendation. OD-62 is the risk acceptance the
other four price and is ruled last.

Peter Duscha accepted Option 1 on 2026-09-02. The register amendments in §5
are therefore authorized and effective.

---

## 1. What is being ruled

Nine numeric controls, proposed with reasoning in package plan §8.3. N5.0-1 …
N5.0-8 were accepted by OD-57 and are untouched. N5.0-9 … N5.0-13 and N5.0-15
were withdrawn with the lease design and are never silently reused.

| Ref | Threshold | Proposed | Owner |
|---|---|---|---|
| N5.0-14 | Activation deadline after `effective_at` | **24 hours** | Operations Owner |
| N5.0-16 | Maximum age of a quiescence observation at activation | **15 minutes** | Operations Owner |
| N5.0-17 | Writer drain timeout (`TimeoutStopSec`) after `SIGTERM` before `SIGKILL` | **45 seconds** | Operations Owner |
| N5.0-18 | Post-revocation margin before the final import reads the Sheet | **120 seconds — an operational margin, not a barrier** | Operations Owner |
| N5.0-19 | Sheets client's explicit per-request timeout | **30 seconds** | Operations Owner |
| N5.0-20 | Maximum unresolved dispatch-journal entries permitted at activation | **zero** | Operations Owner |
| N5.0-21 | Minimum free space on the journal filesystem below which the writer refuses to dispatch | **1 GiB** | Operations Owner |
| N5.0-22 | Maximum current-journal size before a privileged rotation is required | **64 MiB** | Operations Owner |
| N5.0-23 | Retention of a sealed, archived generation before `dispose` may run | **until plan §15.1's Sheet-retirement gate closes, and in no case less than 365 days** | **Data Owner** |

Peter Duscha holds the Operations Owner, Product Owner and Data Owner roles, so
all three signatures below are his. They are listed separately because N5.0-23
is a **data** decision — it governs when evidence may be destroyed — and should
be seen to have been taken as one.

## 2. The one real choice inside this decision

Eight of the nine are self-contained. **N5.0-18 is not.**

Package plan §8.3 records that Google publishes no propagation guarantee, so
**no value of this number bounds anything**. WP-13 was to measure a distribution
against a **disposable** spreadsheet and a **disposable** service account —
assumption **A-5.0-3, unconfirmed**. A measured distribution is not a maximum;
WP-13 was demoted at remediation R3 precisely because the margin was never a
control.

So there is a choice:

- **Option 1 (recommended).** Rule all nine now, with N5.0-18 at **120 seconds**
  and the sentence *"an operational margin, not a barrier"* recorded **beside the
  value in every register that carries it**. Re-rule the value if and when WP-13
  measures one. *Why recommended:* the number's status, not its magnitude, is
  what matters, and fixing that status now removes the risk that a later reader
  finds a bare "120 s" and mistakes it for a bound. A-5.0-3 stays unconfirmed
  either way.
- **Option 2.** Rule eight now and hold N5.0-18 until A-5.0-3 is confirmed and
  WP-13 runs. *Cost:* OD-63 stays partly open, and the register carries an
  unruled number into WP-1 for no gain, since the value cannot become a bound by
  being measured.

## 3. Impact assessment (§0.2 item 2)

| Dimension | Effect |
|---|---|
| **Scope** | None. No requirement, work package, schema object, table, column, trigger, refusal code, option or surface changes. The nine values already exist as proposals in package plan §8.3; ruling them converts *proposed* to *accepted*. |
| **Dependencies** | N5.0-17 (45 s) **must exceed** N5.0-19 (30 s) with margin; the proposed pair gives 15 s for connection setup and for writing the response to the journal. Ruling N5.0-17 without N5.0-19 would be incoherent, so the two are ruled together or not at all. N5.0-18 depends on A-5.0-3 for a *measured* value only — see §2. |
| **Estimate** | Unchanged. PERT 40.9 implementer-days, remediation allowance 11.9, contingency 4.0, security review 3.5–4.5 reviewer-days. Ruling a proposed value consumes no implementer time. |
| **Risk** | **R-5.0-11 is not narrowed and not widened.** N5.0-21's 1 GiB floor is one of the twenty-five fail-closed conditions and is already counted in that risk; ruling it changes nothing about the bounded-outage cost. No RAID row opens or closes. |
| **Testing** | The `TC-5.0-JNL` band already targets these thresholds. No case is added or removed. The band remains **unproducible** because A-5.0-5 is unconfirmed. |
| **Migration** | None. No migration is written, and `0014` remains unauthorized. |
| **Operations** | N5.0-17 becomes the deployed unit's `TimeoutStopSec` and N5.0-19 becomes an explicit client timeout in `connectors/sheets.py`, which **sets none today** (§8.1). **Neither is implemented by this ruling** — both are WP-scoped implementation work that remains unauthorized. |

## 4. What this ruling does not do

- It does **not** close P5.0-R1, P5.0-R4 or P5.0-R5. P5.0-R5 stays **Blocking**.
- It does **not** rule OD-62, OD-64, OD-65 or OD-66, and it must not be read as
  approving option G-A, A, A or J-1 by implication. N5.0-20's value of zero is
  the *control*; the residual it leaves is OD-62's, and OD-62 is untouched.
- It does **not** confirm A-5.0-3, A-5.0-4 or A-5.0-5.
- It does **not** make Package 5.0 ready, and it authorizes no implementation,
  migration, principal, host change, deployment or cutover.
- It does **not** require a new baseline version: no roadmap or release boundary
  moves (§0.2 item 5).

## 5. Register amendments to be applied on signature

Applied only after §6 is signed. Eight documents, in this order:

1. **`docs/discovery/open-decisions.md`** — OD-63 heading becomes
   `**CLOSED <date>**`; a dated ruling entry records the nine accepted values,
   the owner of each, the N5.0-18 status sentence, and the four "does not do"
   statements from §4. The Package 5.0 summary-table row drops OD-63.
2. **`docs/project-management/decision-register.md`** — the D5.0-10 / OD-63 row
   moves to `**Closed <date>**` with the accepted values.
3. **`docs/review/phase-5-0-package-plan.md`** §8.3 — the nine rows move from
   *Proposed — decision D5.0-10 / OD-63* to **accepted**, keeping every
   reasoning cell verbatim and keeping N5.0-18's status sentence attached to the
   value. §9.3 stop condition 1 drops D5.0-10.
4. **`docs/review/phase-5-0-logical-schema.md`** — only where a proposed value is
   quoted; no schema object changes.
5. **`docs/project-management/raid-register.md`** — a dated note recording that
   no row opened, closed or narrowed, and that A-5.0-3 remains unconfirmed.
6. **`docs/project-management/status.md`** — a current-update entry.
7. **`docs/project-management/change-log.md`** — entry **C-P5.0-X**, requester
   Peter Duscha, with §3 as its impact assessment and §4 as its limits.
8. **`docs/implementation-plan.md`** §20 — the readiness state restated.

A cross-document consistency scan and `git diff --check` follow the amendments.

## 6. Signature block — **signed 2026-09-02**

Per §0.2 items 3 and 4. The Technical Lead review is recorded; the three owner
recommendations and the approval are not.

| Role | Holder | Position | Date |
|---|---|---|---|
| Technical Lead (working) | Claude | **Recommends Option 1.** The nine values are internally consistent, N5.0-17 exceeds N5.0-19 with a stated margin, and the only value whose magnitude is unsettled is the one whose magnitude cannot matter | 2026-08-31 |
| Operations Owner | Peter Duscha | **Approves Option 1** | 2026-09-02 |
| Product Owner | Peter Duscha | **Approves Option 1** | 2026-09-02 |
| Data Owner (N5.0-23 only) | Peter Duscha | **Approves Option 1** | 2026-09-02 |
| Acceptance Authority | Peter Duscha | **Accepts and authorizes the §5 amendments** | 2026-09-02 |

**OD-63 / D5.0-10 is Closed.** The nine values are accepted, with N5.0-18
recorded everywhere as an operational margin rather than a barrier.
