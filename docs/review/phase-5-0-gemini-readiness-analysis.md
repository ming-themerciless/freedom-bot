# Package 5.0 — Gemini pre-implementation readiness analysis

**Prepared by:** Gemini (adversarial readiness analyst, per
`docs/review/phase-5-0-gemini-preimplementation-prompt.md`).

**Date:** 2026-09-01

**Last revised:** 2026-09-01 — remediation R1, per
`docs/review/phase-5-0-gemini-readiness-remediation-prompt.md`. Original
classifications of G-RA-1 and G-RA-2 as Important findings were withdrawn
following Security Reviewer (Codex) review. See §12 (Remediation history).

**Revision of design under review:** Package plan revision 12 / logical schema
revision 12. Awaiting independent security re-review by the named Security
Reviewer (Codex).

**Scope authority:** Read-only technical review and documentation-preparation
only. This document does not authorize implementation, migration, host changes,
database changes, or any external-state mutation. It does not close P5.0-SR1,
P5.0-SR2, or any other finding. It does not confirm any assumption, accept any
residual, approve any option, or issue a security-readiness recommendation. All
such actions remain with the roles named in the controlled documents.

---

## 1. Executive outcome

Package 5.0 revision 12 **remains not ready**. The design's own security review
returned two findings (P5.0-SR1 Blocking, P5.0-SR2 Important); both are
**materially addressed on paper** by revision 12. Both claims require independent
security re-review before any finding may be considered closed. This advisory
document does not close P5.0-SR1 or P5.0-SR2 and does not issue the official
§9.2 security-readiness recommendation; Codex records those actions separately.

After Security Reviewer review and the remediation corrections recorded in §12,
this analysis identifies **no additional Blocking or Important security design
finding** in revision 12. The analysis identifies **one design note** (G-NOTE-1,
supply-chain defense in depth), **one operational evidence prerequisite**
(G-EVIDENCE-1, database host-boundary configuration inspection), **one Optional
observation** (G-RA-3, unchanged), and **one cross-document consistency note**
(G-CB-1, resolved informational).

Operational evidence, owner decisions and risk acceptance remain outstanding.

The **five unaccepted residuals** R-5.0-12 through R-5.0-16 appear accurately
bounded within the limits of what can be verified without executing privileged
operations. No sixth residual is identified.

---

## 2. Scope and authority limitations

### 2.1 What was done

- All twelve security-relevant surfaces in package-plan §9.2 were analyzed
  adversarially. The implementer's arguments were tested against the Linux
  kernel, POSIX, the PostgreSQL documentation, and the Git object model.
- Cross-document consistency was checked across the revision-12 package plan,
  logical schema, security brief, R11 handback, open decisions, decision register,
  and RAID register.
- Read-only repository searches and manual document inspection were used.

### 2.2 Checks run

| Check | Result |
|-------|--------|
| `git status --short` | Confirmed dirty tree; no file was modified by this work |
| Repository searches for key identifiers (group names, section numbers, evidence IDs, counts) | Completed |
| Read of all thirteen required files per the prompt | Completed |
| Manual inspection of package-plan §2.12, §2.13, §9.2; logical schema §3.7, §3.8; open-decisions OD-62–OD-66 | Completed |

### 2.3 Checks not run

| Check | Reason |
|-------|--------|
| **C-1**: read `/etc/sudoers.d/` | Permission denied on 2026-08-29 (§8.1 H-7); re-attempt not authorized under this prompt |
| **C-3**: append-only capability probe | Requires `sudo`, `systemd-run`, `chattr` — all prohibited by prompt |
| **C-4**: denial-matrix execution | Requires OS accounts and groups (A-5.0-5, unconfirmed); prohibited |
| Database constraint, trigger or RLS tests | Requires DDL/DML; prohibited |
| Execution of Algorithm C or D | Requires root and host objects that do not exist |
| Any network call | Prohibited |

### 2.4 Authority limits

This analyst may not close P5.0-SR1, P5.0-SR2, or any other finding. Findings
in §5 are presented for Codex's consideration. Codex holds the Security Reviewer,
Independent Reviewer and independent logical-schema reviewer roles for this
package.

---

## 3. Twelve-surface review matrix

| # | Short description | Implementer claim | Adversarial assessment |
|---|------------------|-------------------|------------------------|
| **1** | Authorization-bearing operator command | Isolated to root-run coordinator; peer-authenticated database role; fixed `sudoers` executable | Passes paper review. Post-provisioning host-boundary evidence required; see G-EVIDENCE-1 |
| **2** | Five append-only histories | Triggers enforce append-only; grants exclude mutation from runtime role | Passes paper review. Superuser bypass is residual R-5.0-12, accurately characterized |
| **3** | Database-enforced activation precondition | Trigger requires registered generation, quiescence evidence, journal-clear flag | Passes paper review. Stop condition 10b prevents describing the constraint as a barrier |
| **4** | New database principal and `pg_hba` entry | `freedom_migration_coordinator` `PASSWORD NULL`, peer-authenticated, line placed above broader rules | Passes paper review. Required configuration inspection evidence; see G-EVIDENCE-1 |
| **5** | Credential relocation and Drive-permission procedure | `sheet-writer.env` at `root:freedomsheet 0640`; permission changed per cutover per OD-62 ruling | Passes paper review. Awaits OD-62 ruling |
| **6** | Two new OS identities, `sudoers`, `pg_hba`/`pg_ident` | `freedomcoord`, `freedomsheet`, `freedomjournal`; exact drop-ins, no `NOPASSWD`, no wildcard | Passes paper review. C-1 not executable; OS membership and filesystem-access matrix (JNL-49/JNL-50/JNL-52) not run |
| **7** | Root-owned deployment path and Algorithm D | Algorithm D `D0…D8`; two-region partition; rollback at D7/D8 | Passes paper review. Supply-chain transport note; see G-NOTE-1 |
| **8** | Pre-existing group-writable repository tree and unhardened bot unit | H-1 qualified by Algorithm D reading no worktree path (JNL-51 case h); H-2 addressed by OD-65 items | Passes paper review. JNL-51 case (h) must be run before the worktree-exclusion claim is proven |
| **9** | Privileged tool `freedom-journal-admin` | Root-owned, single fixed executable, `log_output`; only path that can destroy evidence | Passes paper review. Requires C-1 to confirm no competing `sudoers` rule |
| **10** | Root-owned durable state hierarchy | Ownership/mode primary; `chattr +a` second layer probed not inferred; manipulation matrix with per-`errno` rows | Passes paper review. `chattr +a` claim not confirmed on this host; A-5.0-5 unconfirmed |
| **11** | Deliberate relaxations: `freedomjournal` grant and probe arena | Writer can read seal; two transient directories during provisioning | Passes paper review. See G-RA-3 (Optional observation) |
| **12** | Reviewed-source provenance chain (new in revision 12) | `APR + 0700 object store + TM + SM + PVR`; Algorithm D; C0 refuses on absent PVR | Passes paper review. Supply-chain transport note; see G-NOTE-1 |

---

## 4. P5.0-SR1 and P5.0-SR2 recommended dispositions for Codex's consideration

### 4.1 P5.0-SR1 — Deployment integrity check skippable silently

**Finding (revision 11):** `deployment_manifest_digest()` compared live deployed
bytes against a caller-supplied copy of the same value. No step refused when the
comparison against the reviewed commit was omitted.

**Revision 12 remediation:** §2.12.5a replaces the single-sentence control with
Algorithm D (`D0…D8`, refusals `DEP-01…DEP-09`). Three independent artifacts must
agree: `APR` (root-installed approval record naming the reviewed commit), `TM`
(trusted manifest from object bytes in a `0700 root:root` bare Git store, by
object ID through no ref), and `SM` (deployed-source manifest over live bytes).
C0 refuses on absent `PVR`; `V-R` refuses without a matching
`approved_source_revisions` row; the generation carries a `NOT NULL` foreign key.

**Adversarial assessment:** The remediation structurally addresses the stated
finding. The trusted side no longer comes from the artifact being checked. Three
distinct sources must agree, and the database holds a fourth copy the host cannot
write without A9. See G-NOTE-1 for a supply-chain transport observation. The
residual R-5.0-15 (A5 + A8 scenario) is accurately stated as an operator-trust
boundary.

**Disposition (per Security Reviewer):** P5.0-SR1 is materially addressed on
paper by revision 12. The Security Reviewer should confirm the SHA-1/SHA-256
reasoning and the two-region partition closure before determining whether the
finding is closed. This advisory document does not close P5.0-SR1.

### 4.2 P5.0-SR2 — OS identity contract contradicted journal group contract

**Finding (revision 11):** §2.12.2 said `freedomcoord` and `freedomsheet` were
members of their own groups only, while §2.13.3 and E1–E8 required both to be
members of `freedomjournal`. The two contracts were mutually exclusive.

**Revision 12 remediation:** §2.12.2 is now the single canonical
primary/supplementary membership table. The isolation sentence is withdrawn.
§2.12.2 states explicit groups for every identity; an inverse lists each group's
exact members; three claims replace the withdrawn sentence. `JNL-52` checks the
membership matrix before any provisioning step.

**Adversarial assessment:** The internal contradiction is resolved. The reviewer
must confirm every downstream argument still holds: that `freedomjournal`
membership remains minimal, that no group membership was accidentally introduced
or missed, and that E8 matches the corrected `freedomcoord` provisioning.

**Tentative disposition for Codex's consideration:** The stated finding appears
addressed on paper. The Security Reviewer should confirm §2.12.2 identity by
identity before determining whether the finding is closed.

---

## 5. Observations, notes and evidence prerequisites

Severity classifications follow implementation-plan §16.4.

Formerly G-RA-1 and G-RA-2 were classified Important findings. Following
Security Reviewer review they are reclassified as a design note (G-NOTE-1) and
an operational evidence prerequisite (G-EVIDENCE-1) respectively. The original
classifications are preserved in §12 (Remediation history). G-RA-3 remains an
Optional observation.

### G-NOTE-1 — Supply-chain transport: defense-in-depth recommendation (Design note, non-blocking)

*Formerly classified G-RA-1 (Important). Classification withdrawn per Security
Reviewer review. See §12.*

**Surfaces noted:** 12 (reviewed-source provenance chain), 7 (root-owned
deployment path).

**Claim under test:** §2.12.5a asserts that `source_manifest_digest()` is
computed from Git object bytes addressed by object ID. The plan argues that
recomputing SHA-256 over those bytes makes a Git SHA-1 object-ID collision
insufficient — the adversary must find a SHA-256 collision to substitute a
different tree.

**Reasoning:** The SHA-256-over-extracted-bytes binding is correct, and the
Security Reviewer has confirmed the following:

- The out-of-band approval record carries the independently approved SHA-256
  `source_manifest_digest`.
- Algorithm D recomputes that digest from the selected Git object bytes and
  refuses disagreement before deployment provenance is registered.
- A malicious or unauthenticated origin can withhold the approved object,
  return unrelated objects, advertise excessive objects, or otherwise cause an
  availability or resource failure. It cannot cause different deployed source
  bytes to match the independently approved SHA-256 manifest without breaking
  the SHA-256 binding.
- Fetching broadly rather than narrowly may be an operational efficiency or
  denial-of-service concern, but it does not widen R-5.0-15 from A5 to a
  network-only attacker while the approval digest remains independently fixed.
- Certificate pinning, signed tags, or a new signing-key system would be new
  policy and operational complexity; prescribing one as the smallest remediation
  to P5.0-SR1 is not appropriate.

**Classification:** Design note only. The operations document should specify an
authenticated transport and bounded fetch behavior as defense in depth. The
absence of that specification in revision 12 is not a Blocking or Important
defect, and does not widen R-5.0-15 or introduce a sixth residual.

---

### G-EVIDENCE-1 — Database host-boundary configuration inspection required before rehearsal (Operational evidence prerequisite)

*Formerly classified G-RA-2 (Important). Classification withdrawn per Security
Reviewer review. See §12.*

**Surfaces affected:** 4 (new database principal), 6 (OS identities and
`pg_hba`/`pg_ident` ordering).

**Design assessment:** Revision 12 specifies the required first-match ordering,
peer map, explicit rejects, `PASSWORD NULL`, grants and post-reload positive and
negative tests. The design is correct on its face. The proposed configuration does
not exist yet because implementation is not authorized. The absence of
post-implementation evidence before the objects exist is not a design defect.

**Required evidence (not yet collected, cannot exist before implementation):**

1. Pre-change existing-file inspection — the current `pg_hba.conf` and
   `pg_ident.conf` must be read before any line is inserted, to confirm that no
   pre-existing `trust` or wildcard rule would appear before the Package 5.0
   `reject` lines once added. If such a rule exists, insertion ordering must
   account for it or the rehearsal must stop.
2. Exact insertion placement and syntax validation (`pg_hba_file_rules` view or
   equivalent).
3. Configuration reload (`SELECT pg_reload_conf()`) and positive/negative
   authentication tests.
4. The OS membership and filesystem-access matrix (JNL-49, JNL-50, JNL-52) —
   this is the deny matrix for OS identities and filesystem capabilities, not a
   `pg_hba.conf` authentication test. The database host-boundary authentication
   evidence is the Band 2 matrix defined separately in the package plan and
   logical schema. Do not conflate JNL-52 with the `pg_hba`/`pg_ident` checks.

**Classification:** Operational evidence prerequisite. No security-readiness
recommendation may be treated as proof that these checks passed. No design
change is required.

---

### G-RA-3 — Probe-arena cleanup after SIGKILL (Optional)

**Surface affected:** 11 (deliberate relaxations: probe arena).

**Claim under test:** §2.13.2b states `…/probe` and `…/probe-ro` are removed in
a `finally` block. A failed cleanup leaves residue; the next invocation refuses.
R-5.0-14 records this as an accepted cost.

**Analysis:** A Python `finally` block does not execute after `SIGKILL`. If
`verify-capability` is killed by the OOM killer or `kill -9`, neither transient
directory is removed. The design's answer is correct and already specified: next
invocation refuses; operator clears manually (§2.13.2b, stop condition 10f).
The residue window (a `0770 root:freedomsheet` directory) is outside
`ReadWritePaths=` in the deployed unit, so the running writer cannot reach it.
No gap in the design is identified.

**Severity:** Optional. The design addresses this class of issue. The question
is proportionality: is the operational cost of R-5.0-14 acceptable?

**Smallest remediation:** None required in the design documents. The Security
Reviewer should answer the §9.2 question: "is refusing on residue the right
choice rather than cleaning it?"

---

## 6. Residual-risk completeness analysis

All five residuals are **unaccepted**. Acceptance requires an explicit affirmative
act by the Acceptance Authority recorded in the controlled registers; no such act
has occurred.

| Ref | Short description | Assessment |
|-----|------------------|------------|
| **R-5.0-12** | Host root + PostgreSQL superuser writes both evidence copies; no check refuses | Accurately bounded as detection-only (`sudo log_output`, journald, `audit_events`, offline backups) |
| **R-5.0-13** | Forged matching `/etc/machine-id` is not refused | Accurately bounded; every copy carries the same value; the design concedes this |
| **R-5.0-14** | Residue directory persists until operator acts | Accurately bounded; operational cost specified by §2.13.2b and stop condition 10f; not yet accepted |
| **R-5.0-15** | A5 + A8: root rewrites provenance artifacts and registers own revision | Accurately bounded as operator-trust boundary; signed alternative is OD-66 option A-3, not adopted |
| **R-5.0-16** | Emergency redeployment fails closed until approved revision exists | Accurately bounded; intentional fail-closed; the fail-closed direction is correct |

**No sixth residual is identified.** G-NOTE-1 (supply-chain transport) does not
widen R-5.0-15 to include a network-only attacker while the approval digest
remains independently fixed. See G-NOTE-1 for the Security Reviewer's reasoning.

---

## 7. Cross-document consistency results

No unresolved discrepancy found. Items verified:

| Item | Result |
|------|--------|
| Revision 12 stated consistently across all controlled documents | Consistent |
| Seven proposed tables in logical schema (including `approved_source_revisions`) | Consistent |
| Twelve security surfaces in §9.2 | Consistent; twelve stated, twelve reviewed here |
| Fifty-three evidence identifiers, one hundred and fourteen evidence cases (WP-8) | Consistent with package plan §5.1 / WP-8 row |
| PERT 47.6 implementer-days, 13.9 remediation days, 4.5–5.5 reviewer-days | Consistent |
| Five unaccepted residuals (R-5.0-12 through R-5.0-16) | Consistent; no residual is accepted |
| OD-62 through OD-66 Open; no ruling applied from revision 12 | Consistent |
| P5.0-SR1, P5.0-SR2 open pending re-review | Consistent |
| P5.0-R5 Blocking | Consistent |
| A-5.0-3, A-5.0-4, A-5.0-5 unconfirmed | Consistent |
| C-1 not completed; C-3, C-4 not run | Consistent |
| Decision order: OD-63 rulable now (no Security Reviewer dependency); security rec → OD-64/65/66 → OD-62 | Consistent — OD-63 carries no Security Reviewer dependency per ruling draft §0 |
| OD-63 ruling draft unsigned; no register amended from it | Confirmed |
| Package 5.0 summary table (implementation-plan §20) vs §9.4 | Consistent |
| Five append-only histories (including `approved_source_revisions`) | Consistent; upgrade from four to five reflected in all documents |
| Eleven-authority model (A1–A11) | Consistent across package plan and logical schema |
| `freedomjournal` membership: exactly `freedomcoord` and `freedomsheet` | Consistent after revision 12 correction |
| E8 matches `freedomcoord` provisioning | Claimed corrected in revision 12; not independently verifiable without C-4 |

### G-CB-1 — Package plan §5.1 estimate figure (Resolved informational)

The RAID register update for revision 12 notes that §5.1 "still read `35.5`, the
revision-4 value, through six estimate changes" and was corrected in revision 12.

**Verified:** Package plan §5.1 now reads PERT 47.6, not 35.5. The RAID
register's correction note is accurate. G-CB-1 is closed as an informational note;
no action required.

---

## 8. OD-63 ruling draft review (Workstream C, item 1)

The unsigned ruling draft (`docs/review/phase-5-0-od-63-ruling-draft.md`) was
reviewed for completeness, internal consistency, and change-control effects.

**Findings:**

1. Internally consistent. N5.0-17 (45 s) correctly exceeds N5.0-19 (30 s) with a
   15-second margin.
2. N5.0-18 is framed correctly as "an operational margin, not a barrier" with the
   reasoning present. Option 1 (recommended in the draft) is the right choice.
3. The eight register amendments in §5 are listed in a coherent order; the
   cross-document scan step is included.
4. The signature block in §6 correctly identifies all three roles Peter Duscha
   holds (Operations Owner, Product Owner, Data Owner) separately.
5. §5 item 3 states "§9.3 stop condition 1 drops D5.0-10" — verified as accurate;
   no correction required.
6. **No signature, effective ruling, or option approval is proposed or implied by
   this review.**

**Overall assessment:** The ruling draft is ready for Peter Duscha's signature
with no design change identified here.

---

## 9. Checks run and not run (summary)

### Run (read-only, no elevation)

- Repository searches (`rg`) across all controlled documents
- Manual reading of all thirteen required files
- Manual analysis of §9.2, §2.12, §2.13, §3.7, §3.8, OD-62–OD-66, decision
  register, RAID register
- Cross-reference of counts, identifiers, and status fields across documents

### Not run

| Check | Reason not run |
|-------|---------------|
| **C-1**: `/etc/sudoers.d/` read | Access denied on host; prohibited by prompt |
| **C-3**: append-only capability probe | Requires `sudo`, `systemd-run`, `chattr`; prohibited |
| **C-4**: denial matrix (`JNL-49`, `JNL-50`, `JNL-52`) | Requires OS accounts (A-5.0-5 unconfirmed); prohibited |
| Algorithm C or D execution | Requires root and non-existent host objects |
| Database constraint/trigger tests | Requires DDL/DML; prohibited |
| Any network call | Prohibited |

---

## 10. Confirmation of no implementation or external mutation

No production code was written or modified. No migration was written. No database
object was created or changed. No host object (account, group, directory, file,
mode, filesystem attribute, service, `pg_hba.conf`, `pg_ident.conf`, `sudoers`)
was created or modified. No credential, token, secret, or environment file was
read, written, or referenced by name. No network call was made. No Git write
(commit, reset, revert, stage, fetch, push) was performed. No controlled status,
roadmap, RAID, decision, change-log, package-plan, schema, security-review, or
handover document was edited. The only filesystem changes made by this work are
the three new files at the paths authorized by the prompt.

Real player data was not read or written. Package 5.1+ work was not performed.
Discord, Google Sheets, Foundry VTT, and the production PostgreSQL database were
not accessed.

Package 5.0 remains `not ready`. Implementation remains unauthorized.

---

## 11. Next actions

### For Codex (Security Reviewer)

1. Re-review revision 12 against P5.0-SR1: confirm the SHA-256 source-manifest
   computation's independence from SHA-1 object IDs at every extraction step;
   confirm Algorithm D rollback cannot leave live bytes without a current `PVR`;
   confirm the two-region partition is genuinely closed.
2. Re-review revision 12 against P5.0-SR2: confirm §2.12.2 is the sole live
   authority, identity by identity, including E8 versus `freedomcoord`
   provisioning.
3. Determine whether P5.0-SR1 and P5.0-SR2 may be closed or whether further
   remediation is required.
4. Determine whether C-1 and the Band 2 host-boundary evidence must complete
   before the security-readiness recommendation can be issued, or whether they
   may be deferred to WP-14.

### For Peter Duscha (Product Owner, Acceptance Authority, Operations Owner)

1. **OD-63:** May be ruled **immediately** — no Security Reviewer dependency.
   Review and sign the unsigned ruling draft. This analysis found it ready for
   signature with no design change required.
2. **OD-64, OD-65, OD-66:** Owned on the Security Reviewer's recommendation;
   cannot be ruled until Codex delivers it.
3. **OD-62:** Requires OD-63, OD-64, OD-65, OD-66 and full gate criteria; ruled
   last.
4. **P5.0-R5 operational evidence:** See
   `docs/review/phase-5-0-gemini-operational-evidence-runbook.md`. Authorize the
   disposable-environment steps when ready.

---

## 12. Remediation history

### R1 — 2026-09-01 (per `phase-5-0-gemini-readiness-remediation-prompt.md`)

Codex, acting as Security Reviewer, reviewed the original R0 artifacts and
required corrections. The following original classifications were withdrawn:

**G-RA-1 (formerly Important) → G-NOTE-1 (Design note, non-blocking):**
The original finding classified the absence of an explicit authenticated-fetch
specification in §2.12.5a as an Important gap that could widen R-5.0-15 to a
network-only attacker. Codex confirmed this reasoning is incorrect: the approval
record carries the independently approved SHA-256 digest; Algorithm D recomputes
that digest from object bytes and refuses disagreement; a network-capable attacker
without host root cannot substitute different deployed source bytes without
breaking the SHA-256 binding. The operational recommendation (specify authenticated
transport as defense in depth) is retained as G-NOTE-1.

**G-RA-2 (formerly Important) → G-EVIDENCE-1 (Operational evidence prerequisite):**
The original finding classified the unconfirmed `pg_hba.conf`/`pg_ident.conf`
current file state as an Important design defect. Codex confirmed this reasoning
is incorrect: revision 12 specifies the required ordering, rejects, `PASSWORD
NULL`, grants and post-reload tests correctly. The proposed configuration does not
exist because implementation is not authorized; the absence of post-implementation
evidence is not a design defect. The required evidence checklist is retained as
G-EVIDENCE-1. Note: JNL-52 (C-4) is the OS membership and filesystem-access
matrix, not a `pg_hba.conf` authentication test; the Band 2 database
host-boundary evidence is a separate artifact.

**Decision sequence corrected:** The original document stated a decision order of
"security rec → OD-64/65/66 → OD-63 → OD-62". This is incorrect. OD-63 carries
no Security Reviewer dependency and is rulable immediately, per the ruling draft
§0. The corrected order is: OD-63 (rulable now); then security recommendation;
then OD-64/65/66 in their documented dependency order; then OD-62 last.

**Residual vocabulary corrected:** The original document described residuals as
"three unaccepted, two proposed". All five residuals are unaccepted; no residual
has been formally accepted by the Acceptance Authority.

**G-CB-1 resolved:** The original document noted uncertainty about whether §5.1
now reads 47.6. Direct reading of package plan §5.1 confirms it reads 47.6
(corrected from 35.5 in revision 12 as documented in the RAID register). G-CB-1
is closed as resolved informational.
