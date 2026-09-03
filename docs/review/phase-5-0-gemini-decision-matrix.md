# Package 5.0 — Gemini decision matrix: OD-62 through OD-66

**Prepared by:** Gemini (adversarial readiness analyst, per
`docs/review/phase-5-0-gemini-preimplementation-prompt.md`).

**Date:** 2026-09-01

**Last revised:** 2026-09-01 — remediation R1, per
`docs/review/phase-5-0-gemini-readiness-remediation-prompt.md`. G-RA-1 and G-RA-2
removed as Important prerequisites; replaced by G-NOTE-1 (design note) and
G-EVIDENCE-1 (operational evidence prerequisite) respectively. Decision sequence
corrected: OD-63 is rulable now, before the Security Reviewer's recommendation.

**Authority:** This document is an option-neutral decision aid. It does not
select, recommend or approve any option, close any open decision, accept any
residual risk, issue a security recommendation, or confirm any assumption. Those
actions remain exclusively with the named accountable owners identified below.

**Required reading:** This matrix should be read alongside
`docs/review/phase-5-0-gemini-readiness-analysis.md` (adversarial analysis) and
`docs/review/phase-5-0-gemini-operational-evidence-runbook.md` (P5.0-R5 evidence
plan). Controlled documents take precedence over this matrix wherever they
conflict.

---

## Structure

Each section covers one open decision. For each:

- **Decision summary** — what is being decided and why it matters.
- **Accountable owners** — who must recommend, who must approve, and whether
  the Security Reviewer's recommendation is a prerequisite.
- **Prerequisites** — what must be complete before this decision can be ruled.
- **Options** — each option stated neutrally with its security, availability and
  operational trade-offs, affected residuals, and reversibility.
- **No-decision consequence** — what happens if the decision is deferred
  indefinitely.
- **Earliest ruling point** — when in the decision order this may be ruled.

---

## OD-63 / D5.0-10 — Numeric controls (timing and measurement)

**Package plan reference:** D5.0-10, §9.3 stop condition 1; ruling draft at
`docs/review/phase-5-0-od-63-ruling-draft.md`.

### Decision summary

Nine named numeric controls (N5.0-15 through N5.0-23) require binding values
before implementation. They cover quiescence wait, mutation window, health-check
timeouts, quorum thresholds, and soft-limit triggers. Without bound values, the
fence cannot be specified, tested or operated.

### Accountable owners

| Role | Person | Required action |
|------|--------|----------------|
| Operations Owner | Peter Duscha | Recommend (required) |
| Product Owner | Peter Duscha | Recommend (required) |
| Data Owner (N5.0-23) | Peter Duscha | Sign separately for N5.0-23 |
| Acceptance Authority | Peter Duscha | Approve and sign |

**Security Reviewer prerequisite:** None. OD-63 carries no Security Reviewer
dependency; the ruling draft confirms this explicitly. This decision may be ruled
at any time once the named owner is ready.

### Prerequisites

- None that are unmet. The ruling draft is complete and unsigned.

### Options

**Option 1 (recommended in the unsigned draft):** Adopt the nine values as
specified in the ruling draft. Consequences:

- N5.0-17 (45 s quiescence) is a 15-second margin above N5.0-19 (30 s health).
  This is stated in the draft as an operational margin, not a barrier; no
  evidence can make it a barrier without changing the fence's logic.
- N5.0-18 (5-minute mutation window) is similarly operational; the draft frames
  it correctly.
- N5.0-23 (Sheet retry policy) is a data decision: how long the platform retries
  before declaring a mutation failed. This affects player-visible data integrity
  during outages.
- All nine values are operational defaults. Operators may tune them within the
  bounds stated in the ruling draft (no value may cross a stated invariant).

**No other option is identified in the ruling draft.** If any value in Option 1
is unacceptable, the ruling must name a substitute value and the ruling draft must
be updated before signature.

### No-decision consequence

Stop condition 1 (§9.3) prevents implementation progress for WP-4b, WP-1,
WP-2/WP-14 and WP-4b/WP-15. Without OD-63, no work package that depends on a
numeric control may proceed. This is the lowest-risk decision to rule and
carries no Security Reviewer dependency.

### Earliest ruling point

**Now** — OD-63 carries no Security Reviewer dependency and is rulable today.
The unsigned ruling draft is complete; no predecessor decision is required.

---

## OD-64 / D5.0-11 — Database principal and `pg_hba.conf` entry

**Package plan reference:** D5.0-11, §2.12.3, §2.12.4.

### Decision summary

Package 5.0 introduces `freedom_migration_coordinator`, a new PostgreSQL role
with elevated grants (schema-owner writes during migration, not at runtime). The
decision governs: its `pg_hba.conf` method, its `pg_ident.conf` map, its grants
template, and the exact `reject` rules that close off broader access.

### Accountable owners

| Role | Person | Required action |
|------|--------|----------------|
| Security Reviewer | Codex | Recommend (blocking) |
| Operations Owner | Peter Duscha | Approve |
| Acceptance Authority | Peter Duscha | Approve and sign |

**Security Reviewer prerequisite:** Yes — this decision is explicitly owned on
the Security Reviewer's recommendation and is not rulable until that
recommendation exists.

### Prerequisites

1. Security Reviewer delivers the §9.2 recommendation (D-5.0-1).
2. Pre-change existing-file inspection of the current `pg_hba.conf` and
   `pg_ident.conf` (see G-EVIDENCE-1 in the readiness analysis). This is a
   required gate check, not a design defect; it cannot be performed before
   implementation is authorized.

### Options

**Option A:** Adopt `PASSWORD NULL`, peer authentication via a single-entry
`pg_ident.conf` map (`map=freedom_coord`), explicit `reject` lines for all
remaining local and TCP methods, and the grants template as specified in §2.12.4.

- *Security:* `PASSWORD NULL` prevents password-based authentication; the
  `peer` method limits authentication to the exact OS identity mapped in
  `pg_ident`. The explicit `reject` lines are the defense-in-depth layer —
  their ordering relative to pre-existing `pg_hba.conf` entries must be confirmed
  by the required pre-change inspection and post-reload tests (G-EVIDENCE-1).
- *Availability:* The role is used only at migration time. Its absence causes no
  runtime availability impact.
- *Operations:* Requires `visudo -c -f` verification and `SELECT pg_reload_conf()`
  after each `pg_hba.conf` edit. No restart required.
- *Reversibility:* Fully reversible — the role and its `pg_hba`/`pg_ident` lines
  may be removed without affecting the runtime role.
- *Affected residuals:* None directly. Required host-boundary configuration
  inspection (G-EVIDENCE-1) must be completed before this surface can be
  assessed as closed; this is a gate-evidence requirement, not a design defect.

No alternative option is identified in the controlled documents. If Option A is
unacceptable, a substitute must be proposed and the decision register amended
before ruling.

### No-decision consequence

WP-2 (database schema and grants) cannot proceed. WP-14 (denial matrix and
formal evidence) cannot close. The migration cannot begin.

### Earliest ruling point

After the Security Reviewer delivers §9.2 recommendation.

---

## OD-65 / D5.0-12 — OS identities, deployment path, and group-writable repository tree

**Package plan reference:** D5.0-12, §2.12.2, §2.12.5, §2.12.5a, §2.13.3;
extended by revision 12 to include reviewed-source provenance objects.

### Decision summary

This decision governs: the two OS service accounts (`freedomcoord`,
`freedomsheet`) and the shared group (`freedomjournal`); the root-owned
deployment path and its two-region partition; the three reviewed-source provenance
artifacts (`source.git`, `approved-source-revision`, `sheet-writer.provenance`);
and the pre-existing group-writable repository tree (H-1). In revision 12 the
scope extends to the canonical identity and group membership table (§2.12.2),
whose provisioning must be verified before anything else runs.

Option set has grown from three to four in revision 12 (option C now named
separately; option C leaves P5.0-SR1 unremediated per the implementer's
assessment).

### Accountable owners

| Role | Person | Required action |
|------|--------|----------------|
| Security Reviewer | Codex | Recommend (blocking) |
| Operations Owner | Peter Duscha | Approve |
| Acceptance Authority | Peter Duscha | Approve and sign |

**Security Reviewer prerequisite:** Yes — D5.0-12 is explicitly owned on the
Security Reviewer's recommendation.

### Prerequisites

1. Security Reviewer delivers the §9.2 recommendation.
2. P5.0-SR1 determined by the Security Reviewer (it is the provenance-chain
   finding this decision owns). G-NOTE-1 (supply-chain transport, design note)
   does not constitute a prerequisite for this ruling; see the readiness analysis
   for the Security Reviewer's reasoning.

### Options

**Option A:** Adopt all four elements — OS identities with `freedomjournal`,
deployment path with Algorithm D, the three provenance artifacts, and the
canonical membership table. The H-1 pre-existing condition is accepted as
qualified by Algorithm D reading no worktree path (JNL-51 case h).

- *Security:* Strongest available. The provenance chain closes the surface
  P5.0-SR1 found; JNL-51 case (h) is the evidence requirement. R-5.0-15 remains
  an operator-trust boundary.
- *Availability:* Emergency redeployment fails closed until an approved revision
  exists (R-5.0-16). Operations Owner must accept this.
- *Operations:* Requires custody procedure for `APR`, authenticated-origin fetch
  on each deployment, `JNL-52` membership verification before any provisioning
  step.
- *Reversibility:* The provenance objects may be removed, but removal returns the
  design to a state where P5.0-SR1 is unremediated. Not recommended.
- *Affected residuals:* R-5.0-15 remains; R-5.0-16 is intentional.

**Option B:** Adopt OS identities with `freedomjournal` and the deployment path,
but not the provenance artifacts. (Scope: pre-revision-12 design.)

- *Security:* Leaves P5.0-SR1 unremediated.
- *Affected residuals:* P5.0-SR1 re-opens.

**Option C:** Adopt OS identities with `freedomjournal` and the deployment path
and canonical membership table, but not the provenance objects.

- *Security:* Implementer's assessment: leaves P5.0-SR1 unremediated. The
  Security Reviewer must independently confirm this before option C may be selected
  or rejected.
- *Affected residuals:* P5.0-SR1 re-opens per implementer's assessment.

**Option D:** Retain existing OS identities (no `freedomsheet`, no
`freedomjournal`). Incompatible with the journal-evidence design.

- *Security:* Eliminates the journal-evidence capability entirely.
- *Affected residuals:* P5.0-R5 cannot be resolved; package design must be
  reconceived.

### No-decision consequence

WP-14 (denial matrix, C-4), WP-16 (deployment contract), and the provisioning
rehearsal (WP-9) cannot proceed. The database schema gate cannot close.

### Earliest ruling point

After the Security Reviewer delivers §9.2 recommendation and P5.0-SR1 is
determined (open or closed).

---

## OD-66 / D5.0-13 — Reviewed-source provenance verification mechanism

**Package plan reference:** D5.0-13, §2.12.5a, residual R-5.0-15; extended in
revision 12 to add option A-3.

### Decision summary

This decision governs how the reviewed-source provenance binding is verified —
specifically whether the approval record (`APR`) is root-ownership-and-mode only
(the baseline) or is additionally cryptographically signed against a root-held
keyring (option A-3, new in revision 12). Option A-3 would narrow R-5.0-15 to
its A5-only case (an attacker holding only root but not the signing key), but at
the cost of a signing key with its own custody, rotation, revocation and
availability failure modes.

### Accountable owners

| Role | Person | Required action |
|------|--------|----------------|
| Security Reviewer | Codex | Recommend (blocking) |
| Acceptance Authority | Peter Duscha | Approve and sign |

**Security Reviewer prerequisite:** Yes — D5.0-13 is explicitly owned on the
Security Reviewer's recommendation.

### Prerequisites

1. Security Reviewer delivers §9.2 recommendation, including assessment of
   R-5.0-15 and whether the A5 + A8 boundary is acceptable or requires narrowing.
2. OD-65 ruled (this decision governs the verification mechanism for the artifacts
   OD-65 adopts).

### Options

**Option A (baseline):** `APR` integrity rests on root ownership and mode
(`0444`). The `approved_source_revisions` database row provides a fourth copy
the host cannot write without A8. R-5.0-15 remains: an actor holding A5 + A8
can approve and register a revision of their choosing with no technical refusal.

- *Security:* Operator-trust boundary. Detecting abuse requires `sudo log_output`,
  journald, `audit_events`, offline backups, and the `review_reference` a human
  can check.
- *Availability:* No additional failure mode.
- *Operations:* No signing infrastructure required.
- *Reversibility:* Fully upgradeable to option A-2 or A-3 by amending the
  operations document and generating the required artifact.
- *Affected residuals:* R-5.0-15 remains in full.

**Option A-2 (prior revision option; unchanged):** `APR` carries a
TPM-sealed or coordinator-signed host-bound value as an independent integrity
check. Narrows R-5.0-15 to cases where an attacker also controls the TPM or
the coordinator signing key.

- *Security:* Stronger than A; narrower R-5.0-15.
- *Availability:* A legitimate restore onto replacement hardware fails closed
  until the TPM-sealed value is re-provisioned or the coordinator key is
  available. For a design whose purpose is that evidence survives a restore,
  this is a material availability cost.
- *Operations:* Requires TPM provisioning or coordinator key management.
- *Reversibility:* Reversible but requires re-provisioning.
- *Affected residuals:* R-5.0-15 narrowed (host-binding check added).

**Option A-3 (new in revision 12):** `APR` is additionally signed by a
root-held keyring. Signature verification at D0 and C0 makes A5 alone
insufficient; an attacker must also control the signing key.

- *Security:* R-5.0-15 narrowed to the A5-only case. The signing key is itself a
  governance artifact with custody, rotation, revocation and availability failure
  modes. A signing key this project does not yet have would need to be generated,
  stored, rotated and protected against loss.
- *Availability:* A legitimate emergency deployment fails closed when the signer
  is unavailable. For a design whose purpose is evidence survival during
  emergencies, this is a material availability cost.
- *Operations:* Highest operational complexity of the three options.
- *Reversibility:* Reversible to option A with loss of the narrowing.
- *Affected residuals:* R-5.0-15 narrowed to A5-only case.
- *Implementer's assessment:* Priced and deliberately not adopted; the
  Acceptance Authority may disagree.

**Options B, C, D (from prior revisions):** These options modify the scope of
what is verified but do not affect the signing mechanism. They remain unchanged
from prior revisions and are governed by OD-65.

### No-decision consequence

The verification mechanism for the provenance chain cannot be fixed. Algorithm D
and C0 cannot be finalized. The design remains at the baseline (option A) by
default.

### Earliest ruling point

After the Security Reviewer delivers §9.2 recommendation and OD-65 is ruled.

---

## OD-62 / D5.0-9 — Cutover boundary and credential handover

**Package plan reference:** D5.0-9, §2.10, §2.12.5 (cutover procedure).

### Decision summary

This is the risk-acceptance gate. It decides: when the Google Drive permission
is moved from the Freedom bot to `freedom-sheet-writer`; how that transfer is
authorized, verified and rolled back; what constitutes a successful cutover; and
what constitutes a rollback trigger. It is the decision that changes the
production Drive permission and moves the credential from the Freedom bot to the
new service.

OD-62 is **ruled last** because it accepts the risks all other decisions have
priced. It is the gate at which the Acceptance Authority formally accepts every
open residual.

### Accountable owners

| Role | Person | Required action |
|------|--------|----------------|
| Security Reviewer | Codex | Recommendation required (via OD-64/65/66) |
| Operations Owner | Peter Duscha | Recommend; witness cutover rehearsal (WP-9) |
| Data Owner | Peter Duscha | Approve Drive permission change |
| Acceptance Authority | Peter Duscha | Approve and sign; accept all residuals explicitly |

**Security Reviewer prerequisite:** Yes — OD-62 depends on OD-64, OD-65 and
OD-66, all of which depend on the Security Reviewer's recommendation.

### Prerequisites

1. All of OD-63, OD-64, OD-65 and OD-66 ruled and signed.
2. P5.0-R5 operational evidence collected (A-5.0-3, A-5.0-4 confirmed);
   see runbook.
3. WP-9 supervised rehearsal witnessed by Operations Owner.
4. Security Reviewer recommendation delivered with no Blocking or open Important
   finding.
5. All five residuals (R-5.0-12 through R-5.0-16) explicitly accepted by the
   Acceptance Authority.
6. Package gate readiness criteria in §9.4 all met.

### The residual-acceptance checklist

The following residuals must be explicitly accepted before OD-62 may close. This
list is an aide for the Acceptance Authority; it does not constitute acceptance.

| Residual | Description | Current status |
|----------|-------------|----------------|
| **R-5.0-12** | Host root + superuser can write both evidence copies; detection-only | Proposed; not accepted |
| **R-5.0-13** | Forged matching `/etc/machine-id` is not refused | Unaccepted |
| **R-5.0-14** | Probe residue directory persists until operator acts | Unaccepted |
| **R-5.0-15** | A5 + A8 scenario; operator-trust boundary | Proposed; not accepted |
| **R-5.0-16** | Emergency redeployment fails closed until approved revision exists | Proposed; not accepted |

No residual may be marked accepted in this document. Acceptance requires an
explicit affirmative act by the Acceptance Authority recorded in the controlled
registers.

### No-decision consequence

The platform cannot go live. The Freedom bot remains the sole authorized adapter.
No production Drive permission change occurs.

### Earliest ruling point

After OD-63, OD-64, OD-65 and OD-66 are all ruled, the Security Reviewer has
delivered the §9.2 recommendation, P5.0-R5 is resolved, and all gate criteria
in §9.4 are met.

---

## Decision dependency summary

```
OD-63 ─────────────────────────────────────────────────┐
                                                        │
Security Reviewer (§9.2 recommendation) ──┬── OD-64 ──┤
                                           ├── OD-65 ──┼── OD-62 (last)
                                           └── OD-66 ──┘
```

**OD-63** may be ruled immediately, by the Operations Owner / Acceptance
Authority, without waiting for the Security Reviewer.

**OD-64, OD-65, OD-66** are owned on the Security Reviewer's recommendation and
cannot be ruled until Codex delivers it.

**OD-62** requires all four predecessors and the full gate criteria.

---

## Signatures required (none in this document)

This document contains no signature field. It is an option-neutral decision aid.
All signatures, approvals, option selections, and risk acceptances must be
executed in the controlled documents and registers named in each section above.
