# Claude handback — C-P5.0-R5-E1; P5.0-R5 evidence reconciliation — 2026-09-22

*Disposition update, 2026-09-23:* Peter Duscha decided **MD-1**. P5.0-R5 may
close on independently reviewed harness-facsimile feasibility evidence from the
approved disposable target; evidence from actual production journal code
remains mandatory at the implementation/release gate. The evidence classes are
separate and non-substitutable. No implementation or host authority was
created. [Decision record](project-review-2026-09-23-p5-r5-md1-evidence-criterion.md).

*Disposition update, 2026-09-23:* Peter Duscha decided **MD-2**. `oracle-test`
is the approved target whose host facts count for feasibility evidence; §8.1's
development-host observations remain historical context only. Fresh target
observation requires separate authority, which this decision does not create.
[Decision record](project-review-2026-09-23-p5-r5-md2-host-facts-baseline.md).

*Disposition update, 2026-09-23:* Peter Duscha decided **MD-3**. The supervised
reboot durability case is mandatory for P5.0-R5 harness-facsimile feasibility
closure and may not end as Not Run or an accepted residual. This requirement
does not authorize the reboot or any host action.
[Decision record](project-review-2026-09-23-p5-r5-md3-reboot-requirement.md).

*Disposition update, 2026-09-23:* Peter Duscha decided **MD-4**. Residual risks
`R-5.0-10` through `R-5.0-16` are explicitly accepted on their stated terms;
`R-5.0-12` through `R-5.0-16` enter RAID. Recovery rehearsals for
`R-5.0-11`, `R-5.0-14` and `R-5.0-16` remain mandatory. This decision does
not close P5.0-R5 or grant implementation or host authority.
[Decision record](project-review-2026-09-23-p5-r5-md4-residual-dispositions.md).

*Disposition update, 2026-09-23:* Peter Duscha decided **MD-5**. The journal
classifier contradictions must be corrected and independently reviewed before
any evidence band is executable. `plan.is_executable=False` remains
controlling; this decision grants no implementation or host authority.
[Decision record](project-review-2026-09-23-p5-r5-md5-classifier-prerequisite.md).

*Disposition update, 2026-09-24:* Peter Duscha decided **MD-6**. `R-5.0-13`
is accepted without requiring JNL-40(b)'s second-host or `machine-id` rewrite
for P5.0-R5 closure. The residual remains active with its external-evidence
controls; no host or execution authority is created.
[Decision record](project-review-2026-09-24-p5-r5-md6-jnl-40b-disposition.md).

Author: Claude (implementer of the bounded repository-only reconciliation).
Authority: [C-P5.0-R5-E1 prompt](phase-5-0-p5-r5-evidence-reconciliation-claude-prompt.md),
taken as accepted and assigned by Peter Duscha's direct instruction to Claude
in a Claude Code session on 2026-09-22 (*"Please implement
docs/review/phase-5-0-p5-r5-evidence-reconciliation-claude-prompt.md"*). The
prompt carries a draft banner and no written acceptance was recorded before
this pass, so **Peter Duscha should confirm the assignment** when he reviews
this handback. This follows the C-P5.0-LAB-I3-R8-R6 precedent. Codex remains the
Independent Reviewer and did not perform this pass.

**Nothing here closes P5.0-R5, confirms A-5.0-5, makes OD-62 G-A binding,
closes OD-62, changes `plan.is_executable=False`, declares Package 5.0 ready,
authorizes implementation or migration `0014`, approves a digest or authorizes
`--execute` or any action on `oracle-test`.** No command was issued to
`oracle-test`, no database was accessed, and the protected `/tmp` artifacts
were not accessed. No secrets scan was run, and no guard or tool refused a
call.

---

## 1. Executive conclusion

**`additional_authorized_operational_evidence_required`**, preceded by
repository work and maintainer decisions that must come first.

1. **No P5.0-R5 acceptance proposition is supported by accepted operational
   evidence.** Of 66 matrix rows, 0 are `accepted`.
2. **The accepted V6/I12 and I3/R8 evidence is about a different mechanism.**
   It covers the reserved laboratory's topology (`freedomlab`,
   `/var/lib/freedom-blades/laboratory`, `…/runs`, `…/recovery`) and exclusive
   `openat` → `linkat` publication under `fs.protected_hardlinks=1`. It
   exercises no `/var/lib/freedom-sheet-writer`-style hierarchy, no
   `freedomsheet`, `freedomcoord` or `freedomjournal` identity, no
   `FS_APPEND_FL` or `FS_IMMUTABLE_FL`, no seal, no genesis record, no hash
   chain and no generation. It corroborates three narrow environment facts
   (§7) and nothing more.
3. **Most of the `TC-5.0-JNL` band cannot be produced by any authorized
   artifact today.** Package-plan §2.13.8 says the band runs against *"a harness
   writer, a disposable generation … and the disposable database"*. But the
   writer, `freedom-journal-admin` (`verify-capability`, `init-generation`,
   `seal`, `rotate`, `repair`, `archive-verify`, `dispose`), the coordinator's
   `observe`/`register-journal-generation` and migration `0014` (whose head
   would carry `sheet_writer_journal_generations`, `approved_source_revisions`
   and activation-trigger condition 5) **do not exist in the repository**. The
   repository's migration head is `0013`. The evidence harness is planning and
   classification only. Its generated concrete plan is unexecuted and
   `executable=False`, with three Band-7 cases declared unresolved under
   conflict C-7 because *"the coordinator tooling that would produce them is
   Package 5.0's gated product work and does not exist"*.
4. **Closure is therefore structurally blocked on a maintainer decision** (§5,
   MD-1). Either P5.0-R5 closes on design plus disposable-host
   feasibility evidence from a harness facsimile, with production-code journal
   evidence carried into the implementation and release gate (the
   [laboratory direction](phase-5-0-reserved-laboratory-direction.md) already
   requires *"Label feasibility evidence separately from implementation
   evidence; carry actual production-code tests into the implementation/release
   gate"*, and the package plan requires *"Any required criterion split must
   return for an explicit decision"*). Or P5.0-R5 stays Blocking until
   Package 5.0 product implementation exists, which in turn waits on OD-62,
   which waits on P5.0-R5. **The second reading is circular**, and resolving it
   is the maintainer's decision, not the implementer's.
5. **Two harness contradictions must be fixed or explicitly dispositioned
   before any band is executed** (rows 34 and 36). Otherwise a real run could
   classify a correct refusal as a failure, or a wrong one as a pass.

Per the prompt, **no operational execution prompt is drafted.** §5 lists the
smallest missing facts.

---

## 2. Method and state vocabulary

Every row is graded by the **strongest evidence the repository actually holds
for that proposition**. No production implementation of any journal component
exists, so no row can be graded on product code.

| State | Meaning in this matrix |
|---|---|
| `accepted` | supported by operational evidence that an independent review accepted and the maintainer dispositioned for this proposition |
| `implemented_not_verified` | an evidence-harness producer exists: an argument vector in the generated concrete plan plus a classifier with repository tests. It has never been executed |
| `test_only` | only a pure classifier or model over *supplied* observations exists, with repository tests. No producer or vector exists |
| `design_only` | specified in the package plan or logical schema. No producer, vector or classifier exists. *"Design accepted"* in a row means Codex's design or security review raised no open finding. That is not operational evidence |
| `missing` | a stated requirement that no design element, producer or test yet addresses |
| `contradicted` | a repository artifact asserts something the controlling design contradicts |
| `decision_pending` | cannot move without a maintainer decision |
| `not_applicable` | the cited evidence does not bear on the proposition as closure evidence |

Evidence-type codes: **DR** design review · **RT** repository test · **PG**
PostgreSQL test · **HO** disposable-host read-only observation · **CM**
controlled host mutation · **RB** reboot · **MD** maintainer decision.

Abbreviations: **PP** = `docs/review/phase-5-0-package-plan.md` (revision 12);
**LS** = `docs/review/phase-5-0-logical-schema.md`; **CP** =
`docs/review/phase-5-0-evidence-harness-concrete-plan.md` (generated, *NOT
EXECUTED*); **H** = `tools/phase_5_0_evidence/`; **T** =
`tests/phase_5_0_evidence/`. "None" under V6/I12/I3/R8 means that evidence does
not measure the proposition at all.

---

## 3. The matrix

### 3.1 Storage and hierarchy

| # | ID · source | Proposition (falsifiable) | Evidence | Implementation | Test · case | Artifact · disposition | State | V6/I12/I3/R8 support, narrowly | Smallest remaining action | New host authority? |
|---|---|---|---|---|---|---|---|---|---|---|
| 01 | JNL-01; M-1/M-2 · PP §2.13.2 S-1, §2.13.2a Stage 3 | The journal path is on a non-`tmpfs`, block-backed, read-write filesystem, observed at the journal path by the probe | HO | H `filesystem.py` (Stage 3); CP B4-10, B4-11 | T `test_bands.py` four-stage tests | PP §8.1 H-5 is a 2026-08-29 read on the **development host** (`/dev/vda1`, kernel 6.8.0-138), not by `verify-capability` and not on the approved target | implemented_not_verified | **Partial, corroborative only.** R8 §4 read `/dev/sda1 ext4 rw,…` for `/var/lib` on `oracle-test`. It was an I3 prerequisite read of a different path, not M-1/M-2 at a journal path | execute Band 4 under an approved plan | yes |
| 02 | PP §2.13.3 hierarchy table | `…/journal` `root:freedomjournal 0750`; journal `freedomsheet:freedomcoord 0640 +a`; seal `root:freedomjournal 0440 +i`; `current` root symlink; `…/archive` `root:freedomcoord 0750`; archived files `0440 +i` | CM + HO | CP M-10 … M-23, M-33 … M-37 (facsimile under `/var/lib/fb-evidence-p5-0`) | CP B3-19/B3-20 (`JNL-52-APPEND-CONFIRMED`, `-IMMUTABLE-CONFIRMED`) | none | implemented_not_verified | None. V4/V9/V5 are laboratory directories with other groups and modes | execute Bands 2–3 | yes |
| 03 | PP §2.13.3 property 3; §2.13.4 row "rename/rmdir `…/journal`" | No service identity can rename or shadow `…/journal` (`EACCES`), because the parent is `root:root 0755` | CM + HO | CP M-10 creates the facsimile parent only | none. The `JNL-13` row is not generated | none | design_only | None. V12 is `root:root 0755` on a different tree and measures no rename attempt | add a `JNL-13` vector | yes |
| 04 | JNL-52 case 2 · PP §2.13.8 | As `freedomsheet`: create, unlink and rename in `…/journal` → `EACCES`; `open(seal, O_WRONLY)` → `EPERM`; `…/archive` → `EACCES` | CM + HO | H `identity.py`; CP B3-25 … B3-27 | T `test_bands.py` access-case tests | none | implemented_not_verified | None | execute Band 3 | yes |
| 05 | JNL-13 · PP §2.13.4 (fifteen rows) | Under identity E1, each of the fifteen manipulation rows returns its stated `errno`, including `chattr -a` on the journal and `chattr -i` on the seal and on an archived file (also `EPERM` under E2) | CM | none. No `JNL-13` vector in CP | none | none | design_only | None | generate the fifteen-row matrix | yes |
| 06 | PP §2.13.7; §6.5 item 11 | The writer cannot rotate, seal, archive or dispose, because those acts are `freedom-journal-admin` running as root under a separate `sudoers` drop-in that grants no service identity anything | CM + HO | none (no tool). H `sudoers.py` analyses supplied drop-in text | T `test_analysis.py` | security review C-1 **not completed** | design_only | None | implement the tool (gated), complete C-1, add `TC-5.0-HB` vectors | yes |
| 07 | JNL-33 · PP §2.13.8 | The writer's seal access is exactly read, and full V-W completes using only that read | CM | none. V-W does not exist | none | none | design_only | None | needs a writer or harness writer | yes |

### 3.2 `FS_APPEND_FL` capability probe (C-3)

| # | ID · source | Proposition | Evidence | Implementation | Test · case | Artifact · disposition | State | V6/I12/I3/R8 | Remaining action | Host authority? |
|---|---|---|---|---|---|---|---|---|---|---|
| 08 | JNL-27; C-1 … C-6 · PP §2.13.2a Stage 1 | As `freedomsheet` on an arena file without `+a`, all six control operations succeed. Any failure yields `inconclusive`, never `passed` | CM | H `filesystem.py`; CP B4-12 … B4-18 | T `test_a_failing_stage_one_control_makes_every_stage_two_case_inconclusive` and siblings | none | implemented_not_verified | None | execute Band 4 | yes |
| 09 | JNL-01, JNL-28; P-1 … P-9; security check **C-3** · PP §2.13.2a Stage 2 | With root-set `FS_APPEND_FL`, P-1 … P-5 → `EPERM` (flag confirmed); P-6/P-7 append at EOF; P-8 → `EPERM` with the flag retained; P-9 reports the flag | CM | H `filesystem.py`; CP B4-19 … B4-27 | T `test_a_stage_two_refusal_beside_its_passing_control_is_a_pass` | **Not accepted as evidence:** CP §1 and H `approved_target.py:65` repeat a 2026-09-05 statement that Codex *"independently verified … ext4 append-attribute support"* on `oracle-test`. No method, command or output is recorded in the repository and no disposition treats it as C-3 | implemented_not_verified | None | execute Band 4. Do not cite the 2026-09-05 sentence as C-3 | yes |
| 10 | JNL-28 · PP §2.13.2a attribution table | `EACCES`→DAC and `EROFS`→bind are each classified correctly; `ENOTTY`/`EOPNOTSUPP` from `GETFLAGS` → failed probe | RT + CM | H `filesystem.attribute_observation` | T `test_eaccess_in_stage_two_is_inconclusive…`, `test_enotty_from_getflags_is_a_failed_probe…` | none | test_only | None | executing Band 4 covers the producible observations. `ENOTTY` is not producible on ext4 and stays test-only by nature | yes (for the producible part) |
| 11 | PP §2.13.5a C6/C7; §2.13.2a | The created journal's `st_dev` equals `PR.probe_device`, so the report is bound to the tested filesystem | CM | none (`init-generation` absent) | none | none | design_only | None | needs `init-generation` or a harness equivalent | yes |

### 3.3 Systemd sandbox attribution (Stage 4)

| # | ID · source | Proposition | Evidence | Implementation | Test · case | Artifact · disposition | State | V6/I12/I3/R8 | Remaining action | Host authority? |
|---|---|---|---|---|---|---|---|---|---|---|
| 12 | JNL-48(a), JNL-29; S4-0 · PP §2.13.2a | S4-0 succeeds on the exact `…/probe-ro/s4-2.target`, outside any unit, before S4-2 in every execution. A report with S4-2 passing while S4-0 is absent or failing is refused | CM | H `filesystem.py`; CP B4-28 … B4-31 | T `test_s4_2_cannot_pass_without_a_present_and_passing_s4_0` | none | implemented_not_verified | None | execute Band 4 | yes |
| 13 | JNL-29, JNL-48(c); S4-1/S4-2 · PP §2.13.2a | Inside a transient unit whose substituted `ReadWritePaths=` names only the arena, S4-1 succeeds and S4-2 on the same inode, path, mount and uid returns `EROFS` and nothing else | CM | CP M-43 `fb-evidence-s4.service`, B4-32, B4-33 | T `test_s4_2_succeeding_is_a_failed_stage`, `test_erofs_in_s4_2_without_a_passing_s4_0_attributes_nothing` | none | implemented_not_verified | None | execute Band 4 | yes |
| 14 | JNL-48(b) · PP §2.13.8 | A deliberately mis-provisioned target (`root:root 0600`) yields `EACCES` → `inconclusive` and a non-zero exit | CM | classifier only; no mis-provisioning vector | T classifier tests | none | test_only | None | add the mis-provisioned vector | yes |
| 15 | S4-3 · PP §2.13.2a; security review rev 11, "Stage 4 remains conditional" | S4-3 parses a **closed allowlist** of unit directives, rejects duplicate or unknown authority-bearing directives including drop-ins, builds `ReadWritePaths=` from the fixed canonical probe path, compares the **complete normalized** applied property set, and is invalidated by a systemd/package upgrade even when deployed bytes are unchanged | DR + CM | CP B4-34 captures a directive set. No allowlist, normalization or upgrade invalidation found in H `filesystem.py` (targeted search) | none | security review 2026-08-31 made these implementation conditions. The rev-12 re-review did not withdraw them | **missing** | None | specify and implement the four conditions in the harness and the design | no (repository), then yes |
| 16 | PP §2.13.3 unit block | The deployed `freedom-sheet-writer.service` carries `CapabilityBoundingSet=` (empty), `NoNewPrivileges=true`, `ProtectSystem=strict` and the rest, and is the unit Stage 4 reads | DR + HO | none. No such unit template in the repository (`infra/systemd/` holds the bot, web and worker templates) | none | none | design_only | None | product implementation (gated) | yes |

### 3.4 Construction order C0–C13 and value consumption

| # | ID · source | Proposition | Evidence | Implementation | Test · case | Artifact · disposition | State | V6/I12/I3/R8 | Remaining action | Host authority? |
|---|---|---|---|---|---|---|---|---|---|---|
| 17 | JNL-46(a); I-1 … I-5 · PP §2.13.5a | An ordered walk of C0 … C13 shows every value existing, final and validated per its class before first consumption. C0 reads no probe result; C1 is the sole creation point of `PR`; `probe_report_digest` is computed once at C2 | CM + RT | none (`init-generation` absent). H `observations.py` notes `JNL-46` is not in the observation set | none | design accepted (rev-9/10/11 re-reviews) | design_only | None | needs `init-generation` or a harness construction-order walker | yes |
| 18 | JNL-46(b)–(e), (h), (i) · PP §2.13.2c, §2.12.5a | `deployment_manifest_digest()` and `deployed_source_manifest_digest()` are distinct functions. Malformed, wrong and changed-between-C0-and-C2 digests are refused before C5. An unaccounted file refuses by the closed partition. Three call sites agree | RT + CM | H `manifest.py` (functions and partition) | T `test_the_two_manifest_functions_are_different_functions`, `test_an_unaccounted_file_is_refused_by_the_closed_partition` | none | test_only | None | refusal at C0/C2 needs `init-generation` | yes |
| 19 | JNL-31 · PP §2.13.5a C3/C4 | An independent implementation derives record 0 from `SB` alone, byte for byte, and `SB` excludes `genesis_record_digest`, `journal_device`, `journal_inode` and `seal_digest` | RT | none | none | design accepted | design_only | None | repository-only once a seal encoder exists (gated product work) | no |
| 20 | JNL-47 no-generation (four stages + cleanup) · PP §2.13.2b S-A | A failure injected at each stage leaves no journal, seal, `current`, `.close` or row, exit code 2, and no residue when cleanup succeeds | CM + PG | H `journal.py` `classify_stage_failure`. **Producer absent**: CP §6 `BAND7-JNL-47-NO-GENERATION-ON-FAILURE`, conflict C-7 | T `test_r13_remediation.py`, `test_feasibility.py` | CP declares it unresolved | test_only | None | an evidence-only producer (C-7), or a maintainer decision | yes |
| 21 | JNL-47 recovery (two S-B variants) · PP §2.13.2b S-B | Cleanup failure after a probe failure, and after a fully passing probe, each gives exit code 3, residue named by absolute path, residue unchanged, next run refused without cleaning, and named operator recovery then admits a re-run | CM | H `journal.py` `classify_cleanup_failure_state`, `cleanup.py` S-A/S-B/S-C. Producer absent (C-7) | T `test_plan_and_cleanup.py`, `test_r13_remediation.py` | CP unresolved | test_only | None | as row 20 | yes |
| 22 | JNL-30 · PP §2.13.2a cleanup, §2.13.2b | Planted residue is reported and refused, never cleaned and never reused; `verify-capability` refuses while the writer unit is active | CM | H `journal.classify_recovery` (`JNL-30-recovery`) | T `test_the_recovery_procedure_is_operator_run_and_leaves_no_residue` | none | test_only | None | needs `verify-capability` or a harness producer | yes |
| 23 | JNL-48(d) · PP §2.13.2b | An undeletable artifact in `…/probe-ro` reaches S-B and is named, retained and refused, and recovery clears it | CM | H `cleanup.py` classifier | T cleanup tests | none | test_only | None | producer | yes |
| 24 | PP §2.13.5a failure-cost table C5 … C11, C13 | A refusal at C5 … C11 leaves a named, unregistered partial generation and recovery is `repair`. At C13, J-16 refuses the unregistered generation | CM + PG | none | none | none | design_only | None | gated product work | yes |

### 3.5 Deployment-source provenance

| # | ID · source | Proposition | Evidence | Implementation | Test · case | Artifact · disposition | State | V6/I12/I3/R8 | Remaining action | Host authority? |
|---|---|---|---|---|---|---|---|---|---|---|
| 25 | JNL-51(a)–(f), (h); DEP-01 … DEP-09 · PP §2.12.5a Algorithm D | The deploy step refuses a missing `APR`, a missing commit, a non-reproducing tree, lock drift and an unaccounted file, rolls back after D7, writes `PVR` last and outside the root, and reads nothing under the worktree | RT + CM | H `provenance.py` (four-way comparison, worktree check). No deploy tool | T `test_the_four_way_provenance_comparison_names_the_source_that_disagreed`, `test_the_deploy_path_reads_no_file_in_the_group_writable_worktree` | P5.0-SR1 Closed **on design** 2026-09-02 | test_only | None | deploy tool (gated) plus a disposable object store | yes |
| 26 | JNL-51(g) omission test · PP §2.12.5a; SR1 | With `PVR` omitted, `init-generation` refuses at C0 with J-26, the probe never runs, no artifact or row exists, and a direct SQL insert naming an unapproved revision is refused by the `NOT NULL` FK under coordinator and schema owner | CM + PG | H `provenance.classify_missing_provenance`. **Producer absent**: CP §6 `BAND7-JNL-51-PROVENANCE-OMITTED` (C-7). FK needs migration `0014` | T `test_the_missing_provenance_case_refuses_and_creates_nothing` | CP unresolved | test_only | None | producer, plus `0014` on a disposable DB | yes |
| 27 | JNL-53 writer/coordinator J-26, J-27 · PP §2.13.5b W11a, §2.13.6 | The writer refuses at W11a (`SW-J26`/`SW-J27`) before W17 and appends nothing. The coordinator refuses at C-a/C-d and writes no evidence | CM | none | none | none | design_only | None | gated product work | yes |

### 3.6 Seal, genesis, inode, digest and registered-generation agreement

| # | ID · source | Proposition | Evidence | Implementation | Test · case | Artifact · disposition | State | V6/I12/I3/R8 | Remaining action | Host authority? |
|---|---|---|---|---|---|---|---|---|---|---|
| 28 | J-16; C-d sixteen values · PP §2.13.5b, LS §3.7 | Seal, record 0 and the registered row agree on sixteen values, and any single mismatch refuses | CM + PG | H `journal.SealBody` models 11 fields as a classifier input only | none for C-d | design accepted | design_only | None | gated product work plus `0014` | yes |
| 29 | JNL-42 … 45; F-9 … F-12 · PP §2.13.5b binding table | Altering only `BND.genesis_record_digest`, `journal_device` or `journal_inode`, or appending a `sealed_at` field, is refused by W5/W7/W3 with the named code | CM | none | none | design accepted | design_only | None | seal encoder and V-W (gated) | yes |
| 30 | JNL-34a/34b; F-1a/F-1b · PP §2.13.5c | F-1a is refused by the writer without a database. F-1b completes V-W **without** refusal and is refused only by the coordinator against PostgreSQL | CM + PG | none | none | design accepted | design_only | None | gated | yes |
| 31 | JNL-35 … 39, 41; F-2 … F-6, F-8 · PP §2.13.5c | Each independent alteration is refused at its named step and code, with the corrected minimum combinations (F-2 under E2; F-5 via E4 → `EPERM`) | CM + PG | none | none | design and security accepted (rev-12 re-review) | design_only | None | gated, plus capability vectors | yes |
| 32 | JNL-40(a)/(b); F-7 · PP §2.13.5c; R-5.0-13 | (a) An unforged host change is refused at W10/C-d. (b) A forged matching `/etc/machine-id` is **not** refused, and the test asserts the limit | CM (second host or `machine-id` rewrite) + MD | none | none | R-5.0-13 proposed, **not dispositioned** | decision_pending | None | MD: accept R-5.0-13 or adopt OD-66 A-2; authorize a second host or rewrite | yes |
| 33 | JNL-29 digest; W4; JNL-41 · PP §2.13.8a | `append_only_probe_digest` covers exactly the four-stage report inside `SB`, and W4 re-derives it | CM | none (no report builder) | none | design accepted | design_only | None | gated | yes |

### 3.7 Journal chain, startup record and typed refusals

| # | ID · source | Proposition | Evidence | Implementation | Test · case | Artifact · disposition | State | V6/I12/I3/R8 | Remaining action | Host authority? |
|---|---|---|---|---|---|---|---|---|---|---|
| 34 | J-07 … J-10, J-18, J-21; W13/W14 · PP §2.13.5b, §2.13.6, §2.13.8 | Each chain defect refuses with **its own** code. A record from another generation is J-18/`SW-J18`, and V-W checks in W1 … W18 order | RT + CM | H `journal.py` models the chain as one Boolean (`chain_intact`) | T `test_each_condition_produces_its_own_named_refusal` | — | **contradicted** | None | see §3.12 C-2 and C-4; fix or disposition before execution | no |
| 35 | JNL-32a/32b; W17/W18 · PP §2.13.5b | Syscall trace: with `+a` set, W17 is the only write and appends one `startup` record. With `+a` absent, W9 refuses (`SW-J06`) with no write-mode open and bytes unchanged | CM | none | none | design accepted | design_only | None | gated | yes |

### 3.8 Missing, empty, corrupt, replaced, unreadable, stale, cross-generation and incomplete evidence

| # | ID · source | Proposition | Evidence | Implementation | Test · case | Artifact · disposition | State | V6/I12/I3/R8 | Remaining action | Host authority? |
|---|---|---|---|---|---|---|---|---|---|---|
| 36 | JNL-04 … 12; J-03 … J-06, J-11, J-12, J-17 · PP §2.13.6, §2.13.5b | Each bad state refuses with its named writer code **and** the coordinator records no evidence with the matching J-row | RT + CM | H `journal.py` five-condition classifier | T `test_each_condition_is_diagnosed_as_itself` | — | **contradicted** | None | see §3.12 C-1 and C-3; the classifier has no J-05, J-06 or J-12 condition | no |
| 37 | J-02; W15 · PP §2.13.6 | A torn tail makes the generation `suspect`. Only `repair` clears it, and the coordinator counts it as one unknown unresolved entry | CM | none | none | design accepted | design_only | None | gated | yes |
| 38 | JNL-22 … 26; LS §3.4 condition 5 | The activation trigger refuses missing, stale, cross-generation, corrupt and incomplete journal evidence, each with a named reason, against real PostgreSQL | PG | none. Migration `0014` absent | none | design accepted | design_only | None | `0014` (gated), then PG tests on a disposable DB | yes (DB) |

### 3.9 Disk-full, `fsync`, append and outcome failures

| # | ID · source | Proposition | Evidence | Implementation | Test · case | Artifact · disposition | State | V6/I12/I3/R8 | Remaining action | Host authority? |
|---|---|---|---|---|---|---|---|---|---|---|
| 39 | JNL-16; J-13; N5.0-21 = 1 GiB | Below the free-space threshold or with `ENOSPC`/`EROFS`, the writer refuses before dispatch and the Sheets client is never called | CM (loopback fs) | none | none | N5.0-21 accepted (OD-63) | design_only | None | gated writer plus a loopback-fs vector | yes |
| 40 | JNL-17; J-14 | An injected `fsync` failure is terminal for the generation (`suspect`), dispatch is refused, and exit is non-zero | CM (fault injection) | none. No injection mechanism is specified in the harness | none | none | design_only | None | specify an injection mechanism (A-5.0-5) | yes |
| 41 | JNL-18; J-15 | An outcome-append failure leaves the request unresolved, `dispatch_journal_clear` is refused, and activation is refused | CM + PG | none | none | none | design_only | None | gated | yes |
| 42 | JNL-14, JNL-15 | `SIGKILL` after durable intent means the request was never sent. After dispatch and before outcome, a durable unresolved entry names its ranges and digest | CM | none | none | none | design_only | None | gated harness writer | yes |

### 3.10 Restart, kill, rotation, archive, restore, rollback and reboot

| # | ID · source | Proposition | Evidence | Implementation | Test · case | Artifact · disposition | State | V6/I12/I3/R8 | Remaining action | Host authority? |
|---|---|---|---|---|---|---|---|---|---|---|
| 43 | JNL-02a | A process-level `SIGKILL` between dispatch and outcome leaves the entry unresolved after restart | CM | none | none | none | design_only | None | gated | yes |
| 44 | JNL-02b; J-01 · PP §2.13.8, §8.1 | An unresolved entry survives a supervised host reboot. *"If the Operations Owner will not authorize a reboot it is recorded as a check not run rather than claimed"* | RB + MD | none | none | none | decision_pending | None | MD-3 (§6) | yes (reboot) |
| 45 | JNL-03 | A restart appends and never creates, `seq` continues, a creation attempt fails `EACCES`, and a `suspect` generation refuses to start | CM | none | none | none | design_only | None | gated | yes |
| 46 | JNL-19 · PP §2.13.7 seal/rotate | `init-generation` refuses while the predecessor is unsealed. The archive is `+i`. A successor requires `predecessor_close_digest`. The partial unique index refuses a second head | CM + PG | none | none | design accepted | design_only | None | gated plus `0014` | yes |
| 47 | JNL-21 | A successor registered after evidence makes the trigger refuse. A database restore predating a rotation makes `status` refuse before any service starts | PG + CM | none | none | none | design_only | None | gated | yes |
| 48 | PP §2.13.7 `archive-verify`; V-R | `archive-verify` re-derives the genesis and re-validates the chain against `.close` at every successor registration and after any restore | CM | none | none | none | design_only | None | gated | yes |

### 3.11 Identities, groups and capability identities E1–E8

| # | ID · source | Proposition | Evidence | Implementation | Test · case | Artifact · disposition | State | V6/I12/I3/R8 | Remaining action | Host authority? |
|---|---|---|---|---|---|---|---|---|---|---|
| 49 | JNL-52 precondition · PP §2.12.2 | `getent group` for `freedomjournal`, `freedomcoord`, `freedomsheet`, `discordbot`, `sudo` and `fbprobe` lists **exactly** §2.12.2's members | CM + HO | H `identity.py`; CP M-01 … M-09, R-02, B2-10 … B2-15 | T `test_the_canonical_membership_is_matched_as_a_set_not_a_containment` and 13 siblings | P5.0-SR2 Closed on design | implemented_not_verified | **None.** V1/V2 establish only `freedomlab` (gid 986) with `ubuntu`. None of the five named identities existed at I3 | execute Band 2 | yes |
| 50 | JNL-52 cases 1–8 = security check **C-4** | Positive and negative `id`, `namei -l` and `open` for `freedomsheet`, `freedomcoord`, `discordbot` and `freedomweb`, with traverse-to-parent controls | CM + HO | H `identity.py`; CP B2-16 … B2-21, B3-21 … B3-38 | T `test_an_access_denial_is_not_interpreted_without_its_traverse_control` | security review: C-4 not run | implemented_not_verified | None | execute Bands 2–3 | yes |
| 51 | E1 … E8 construction · PP §2.13.5c | The seven-step `capsh` construction yields the declared P/E/I/A/B masks and securebits `0x4`, each asserted from `/proc/self/status` and `PR_GET_SECUREBITS` before any operation | CM | H `capability.py`; CP B5-E1 … B5-E8, P-03 … P-06 | T `test_every_declared_mask_is_reproduced_by_the_derivation`, `test_e4_and_e6_differ_in_exactly_cap_fowner` | design and security accepted | implemented_not_verified | **Narrow, corroborative.** R8 §7.1: the root verifier process on `oracle-test` showed `CapPrm`/`CapEff`/`CapBnd 000001ffffffffff`, `CapInh`/`CapAmb 0`, `NoNewPrivs 0`. That matches E7's declared masks on the approved target. Securebits were not observed, and E1–E6/E8 were not constructed | execute Band 5 | yes |
| 52 | Launcher prerequisite · PP §2.13.5c | The launching process's bounding set contains the seven required capabilities, otherwise `inconclusive` | HO | CP P-01 `CAP-LAUNCHER-BND` | T `test_a_short_launcher_bounding_set_makes_the_run_inconclusive` | none | implemented_not_verified | **Corroborative:** R8 observed a full `CapBnd` for a `sudo` root process on `oracle-test` on 2026-09-21. It is not the harness launcher, and a later session could differ | P-01 at run time | yes |
| 53 | JNL-49 case 11 (E4/E6), case 12 (E5) · PP §2.13.8 | E4 is refused (`EPERM`) clearing `+i` on a root-owned archive file, E6 succeeds, and E5 clears and then gets `EACCES` on `O_WRONLY` | CM | CP B5-C6-01 … 11; H `required_cases.py` | T `test_the_isolating_control_for_an_e4_refusal_is_e6_and_not_e2` | none | implemented_not_verified | None | execute Band 5 | yes |
| 54 | JNL-49 cases 1–10 and JNL-50 cases 1–12 (21 remaining of 24) | Each case under its named identity with its stated syscall, result and `errno`, including JNL-50 case 4's C-II control and case 11 (writer opens no database connection) | CM + PG | none. CP generates only the three required cases in row 53 | none | design and security accepted | design_only | None | generate the remaining vectors | yes |
| 55 | Control forms C-I/C-II · PP §2.13.5c | A negative flag case is interpreted only beside its isolating positive control, and E2 is corroborating, never isolating, for E4 | RT | H `capability.py` | T `test_the_two_control_forms_are_named_and_a_third_is_refused`, `test_an_e4_refusal_beside_a_control_that_did_not_clear_the_flag_is_inconclusive` | none | test_only | None | — | no |

### 3.12 PostgreSQL, privileged lifecycle, retention and governance

| # | ID · source | Proposition | Evidence | Implementation | Test · case | Artifact · disposition | State | V6/I12/I3/R8 | Remaining action | Host authority? |
|---|---|---|---|---|---|---|---|---|---|---|
| 56 | LS §3.7, §3.8; J-28; JNL-53 J-28 cases | The generation table is append-only against every principal, with one linear chain, a `NOT NULL` FK to `approved_source_revisions`, and V-R refusing J-28 | PG | none. Migration `0014` unauthorized | none | design and security accepted | design_only | None | `0014` (gated) | DB |
| 57 | PP §2.13.7 `sudoers` drop-in; security check **C-1** | `freedom-journal-admin` is reachable only by `foundry` through its own `env_reset`, `!setenv`, `log_output` drop-in with no `NOPASSWD`, and no existing rule collides with or pre-empts it | HO (privileged read) + DR | H `sudoers.py` analyses supplied text | T `test_analysis.py` | security review: C-1 **not completed** (direct enumeration denied; `sudo` required a password) | test_only | None | privileged read of `/etc/sudoers.d` on the relevant host | yes (read) |
| 58 | N5.0-23 · PP §2.13.7 retain/dispose | Archived generations are retained until the §15.1 gate closes and never less than 365 days. `dispose` requires the gate, Data Owner approval and a passing `archive-verify`, and leaves audit plus a change-log entry | MD + CM | none (no tool) | none | **N5.0-23 accepted** (OD-63 Option 1; OD-66 J-1, 2026-09-02) | design_only | None | gated product work. The decision is already made | yes |
| 59 | PP §2.13.9; LS §2.9 | The false *"nothing depends on completeness"* sentence is withdrawn, the control is kept, and the residual is named R-5.0-10 | DR | — | — | design accepted | design_only | None | disposition R-5.0-10 (MD-4) | no |
| 60 | PP §2.13.10; stop condition 10b | The journal is never described as a barrier for I-SHEET-COMPLETE, and R-5.0-8 is not narrowed | DR | — | — | design accepted | design_only | None | — | no |
| 61 | R-5.0-10 … R-5.0-16 · PP §7.4 | Each residual is explicitly accepted, rejected or mitigated | MD | — | — | OD-66 closure: *"does not silently accept R-5.0-12 through R-5.0-16"*. R-5.0-12 … 16 are only **proposed** rows (PP §7.4) and have no row in the RAID table | decision_pending | None | MD-4 | no |
| 62 | Criterion split · lab direction; PP header 2026-09-10 | Which evidence closes P5.0-R5: harness-facsimile feasibility evidence, or production-code evidence | MD | — | — | undecided | decision_pending | — | MD-1 | no |
| 63 | Target of the host facts · PP §8.1 vs CP §1 | Which host's facts count. §8.1 H-4 … H-6 were read on the development host (kernel 6.8.0-138, `/dev/vda1`, E7 derived for `CAP_LAST_CAP = 40` there). The approved target is `oracle-test` (7.0.0-31-generic, `/dev/sda1`). The production host is not provisioned | MD | CP P-02 re-reads E7 on the target | T `test_e7s_masks_are_read_rather_than_derived` | undecided | decision_pending | R8 read kernel `7.0.0-31-generic` and `/dev/sda1` on `oracle-test`. That fixes which host the lab evidence describes, and nothing about production | MD-2 | no |
| 64 | Prompt's "relationship of I3/R8 to P5.0-R5" | I3/R8 is closure evidence for any P5.0-R5 proposition | — | — | — | I3 Closed 2026-09-22 at its measured scope | not_applicable | See §7 | — | no |
| 65 | PP §2.13.8a | PostgreSQL enforces shape, structure, history, authority and fencing, and **merely records** the probe and sandbox attestations | DR | — | — | design accepted | design_only | None | — | no |
| 66 | PP §2.13.5c kernel-requirement table, A1 … A11, holder table | The register matches the two `FS_IOC_SETFLAGS` checks, and holders are assessed separately from primitives | DR + CM | H `capability.py` | T band tests | design and security accepted. Executable proof is rows 53/54 | design_only | None | rows 53/54 | yes |

### 3.13 The two contradictions, stated exactly

These are harness defects in classifier code. **This pass does not fix them**:
changing source or tests is prohibited.

* **C-1 — a replaced inode is classified as corruption under the wrong code.**
  `H/journal.py` `diagnose()` returns `CORRUPT` when `(st_dev, st_ino)`
  disagrees with the seal, and `CONDITION_REFUSALS[CORRUPT]` is
  `("SW-J04", "J-17")`. PP §2.13.5b W7 and §2.13.6 J-11 require `SW-J11`.
  `WRITER_REFUSALS` even lists `SW-J11` for this case, but no condition
  produces it. The in-code comment ("refused by name at W7") contradicts the
  code beneath it. A real `JNL-11`/`JNL-38` observation of `SW-J11` would be
  classified **failed**.
* **C-2 — cross-generation is mapped to the chain-rewrite code.**
  `CROSS_GENERATION` → `SW-J09`. PP §2.13.6 J-18 and W14 give `SW-J18`.
* **C-3 — missing-artifact and coordinator codes diverge from the J-rows.** A
  missing journal file or `current` symlink is `MISSING` → `SW-J17`. PP J-03
  (W1/`open`) gives `SW-J03`, and `SW-J17` is the seal row. On the coordinator
  side, `MISSING` → `J-16` and `CORRUPT` → `J-17`, while PP §2.13.5b C-a
  refuses with *"the matching `J-xx` row"*. The classifier also has no
  condition for J-05 (owner/mode), J-06 (`+a` absent) or J-12 (unreadable).
* **C-4 — the stated order is not the writer's order.** `diagnose()`'s
  docstring says *"The order matters and is the writer's own"*, but it checks
  the deployment digest last. V-W checks it at W11, **before** W13/W14. An
  observation with both a stale deployment and a broken chain is `CORRUPT` in
  the harness and `SW-J22` in the design.
* **Adjacent overstatement.** `journal.py`'s module docstring calls its five
  conditions *"the five refusals P5.0-R5 needs evidence for"*. §2.13.6 has
  twenty-eight. `p5_0_r5_evidence_complete()` returns `complete=True` over those
  five, while its message correctly says P5.0-R5 remains Blocking. The name
  overstates what the function measures.

The focused tests in §9 pass, and they pass **with** these mappings: the tests
encode the harness's own table, not §2.13.6's.

### 3.14 Totals by state

| State | Rows | Count |
|---|---|---|
| `accepted` | — | **0** |
| `implemented_not_verified` | 01, 02, 04, 08, 09, 12, 13, 49, 50, 51, 52, 53 | **12** |
| `test_only` | 10, 14, 18, 20, 21, 22, 23, 25, 26, 55, 57 | **11** |
| `design_only` | 03, 05, 06, 07, 11, 16, 17, 19, 24, 27, 28, 29, 30, 31, 33, 35, 37, 38, 39, 40, 41, 42, 43, 45, 46, 47, 48, 54, 56, 58, 59, 60, 65, 66 | **34** |
| `missing` | 15 | **1** |
| `contradicted` | 34, 36 | **2** |
| `decision_pending` | 32, 44, 61, 62, 63 | **5** |
| `not_applicable` | 64 | **1** |
| **Total** | | **66** |

Of the 114 `TC-5.0-JNL` cases, the generated concrete plan carries vectors
touching `JNL-01` (Stage 2/3), `JNL-27` … `JNL-29`, `JNL-48(a)/(c)`, all of
`JNL-52`, and three of the 24 `JNL-49`/`JNL-50` cases. None has been executed.

---

## 4. A-5.0-5, component by component

A-5.0-5 is **unconfirmed in every component**. No component is confirmed by
V6/I12/I3/R8.

| # | Component (PP §7.4 A-5.0-5; RAID A-5.0-5) | Disposition | Nearest evidence, and why it does not confirm |
|---|---|---|---|
| a | a root-owned durable hierarchy can be created on the journal filesystem | **unconfirmed** | V6 provisioned root-owned laboratory directories on `oracle-test` ext4 (V12/V4/V9/V5). Different paths, groups and modes, no `+a`/`+i` — analogous, not the journal hierarchy |
| b | a writer-owned disposable arena, with probe cases run under the writer's uid via `setpriv` | **unconfirmed** | `freedomsheet` does not exist anywhere evidenced |
| c | `chattr +a` set and cleared by root and honoured (C-3) | **unconfirmed** | the 2026-09-05 unrecorded "verified append attributes" sentence is not admissible (row 09) |
| d | a transient `systemd-run` unit started as root with the deployed hardening | **unconfirmed** | CP M-43 unexecuted |
| e | a deployed `freedom-sheet-writer.service` to read directives from | **unconfirmed; the artifact does not exist** | row 16 |
| f | `…/probe-ro` on the same mount and S4-0 outside any unit | **unconfirmed** | CP M-28 … M-30 unexecuted |
| g | E1 … E8 constructible: `capsh` present, launcher bounding set sufficient | **unconfirmed** | H-6 read `capsh` on the development host. R8 corroborates a full root `CapBnd` on `oracle-test` (rows 51–52). `capsh` presence on `oracle-test` rests on the 2026-09-05 "required tools" sentence, with no recorded output |
| h | `SECBIT_NO_SETUID_FIXUP` and `PR_CAP_AMBIENT_RAISE` behave per `capabilities(7)` on the target kernel | **unconfirmed**, and its premise moved. PP states it for kernel 6.8.x. The approved target runs 7.0.0-31-generic | — |
| i | the disposable `fbprobe` identity can be created and removed | **unconfirmed** | CP M-04/M-07 unexecuted |
| j | a second host, or a rewritable `/etc/machine-id`, for `JNL-40(b)` | **unconfirmed, and decision-bearing** | row 32 |
| k | an `fsync` failure can be injected | **unconfirmed; no mechanism specified** | row 40 |
| l | a supervised host reboot, if the Operations Owner authorizes it | **unconfirmed; Not Run by contract unless authorized** | row 44 |
| m | (rev 12) a disposable object store, approval record and provenance record for `JNL-51` | **unconfirmed; producers absent** | rows 25–26 |

**Owner inconsistency.** The RAID and PP give A-5.0-5 to the Operations Owner.
The Gemini runbook's P5.0-R5 path says confirmation is *"the Security
Reviewer's, not the Operations Owner's"* (see S-7).

---

## 5. Minimum remaining work, grouped

The smallest missing facts are marked **(fact)**. No operational prompt is
drafted.

**Maintainer decisions — first, because each one changes the others.**

* **MD-1 (fact): which evidence closes P5.0-R5.** Either harness-facsimile
  feasibility on the approved target, with production-code evidence carried to
  the implementation/release gate, or production-code evidence only. Without
  this ruling, rows 07, 16, 17, 19, 24, 27–31, 33, 35, 37–48 and 56 cannot even
  be scoped.
* **MD-2 (fact): which host's facts count.** Choose between the development
  host of PP §8.1 and `oracle-test` 7.0.0-31/`/dev/sda1`, and decide whether
  §8.1 is re-baselined.
* **MD-3: the reboot** (§6).
* **MD-4: explicit dispositions of R-5.0-10 … R-5.0-16,** and whether
  R-5.0-12 … 16 enter the RAID table.
* **MD-5: whether the §3.13 classifier contradictions are fixed before any
  band executes.** Recommended: yes.
* **MD-6: JNL-40(b)'s second host or `machine-id` rewrite,** or acceptance of
  R-5.0-13 without that case.

**Repository-only work (each item needs its own assignment).**

1. Fix or disposition §3.13 C-1 … C-4 in `journal.py` and its tests (source
   change, not authorized here).
2. Specify and implement row 15's four security-review conditions for S4-3.
3. Generate the vectors the concrete plan lacks: `JNL-13` (fifteen rows), the
   remaining 21 `JNL-49`/`JNL-50` cases, `JNL-48(b)`, and a construction-order
   walker for `JNL-46(a)`/`JNL-31` if MD-1 permits a facsimile.
4. Resolve conflict C-7 (Band 7 producers) or record a decision that those
   cases wait for product implementation.
5. Correct the stale claims in §8, by dated erratum where historical text must
   remain.
6. The existing EH-R16-1 real-execution refusal and
   `plan.is_executable=False` stand. Nothing here proposes changing them.

**Database evidence** (needs migration `0014`, which is unauthorized): rows 26
(FK), 38, 41, 46, 47 and 56, and PP §6.5 item 6's direct-SQL matrix, on a
disposable database (CP names `fb_evidence_p5_0`, never `freedom_test`).

**Disposable-host read-only evidence** (needs fresh authority): C-1
`/etc/sudoers.d` enumeration with privilege (row 57); `capsh` presence and mode
on `oracle-test`; a fresh P-01/P-02 read at run time.

**Controlled host mutation** (needs Codex pre-execution approval and fresh
authority): execution of CP Bands 2–6 (rows 01, 02, 04, 08, 09, 12, 13, 49–53);
a loopback-filesystem disk-full vector (row 39); an `fsync` fault-injection
mechanism (row 40); Band 7 producers (rows 20–23, 26).

**Reboot evidence:** row 44 only.

---

## 6. The supervised reboot

**Recommendation: required for closure of the durability proposition. The
maintainer may instead accept an explicitly recorded residual. It should not
stay silently Not Run.**

* The accepted contract permits it to end as a check not run (PP §2.13.8
  `JNL-02b`, §8.1). Recording it Not Run is therefore **compliant**.
* J-01 is, in PP's own words, *"the single most important row in the table"*.
  It is the exact property P5.0-R5 was raised about: `/run` emptied at boot. Every
  other row can pass while this one remains an inference from the filesystem
  type. Using the filesystem type as evidence is the defect P5.0-R5 was raised
  against.
* `oracle-test` is explicitly disposable and exists for destructive drills, so
  the cost is small. A reboot there, after a harness-created disposable
  generation with a dispatch record and no outcome, would show that the file,
  its `+a` flag, its seal `+i` and its chain survive a boot. The full
  dispatch-between-outcome variant belongs to the WP-9 rehearsal against the
  real writer.
* If Peter declines, the handback that closes P5.0-R5 should carry J-01 as a
  named, accepted residual rather than as a passed row.

---

## 7. What the accepted I3/R8 evidence proves, and does not

**Proves, at its measured scope** (R8 handback §11; I3 closed 2026-09-22):

* on `oracle-test`, four contexts performed exclusive `openat`, `fsync`,
  descriptor ownership/mode, `linkat` publication, dual-name observation,
  identity-guarded removal and a directory barrier, with the
  `protected_hardlinks=1` owner condition observed at each publication;
* the environment facts read at admission: kernel `7.0.0-31-generic`, `/var/lib`
  on `/dev/sda1 ext4 rw`, `fs.protected_hardlinks=1`, V1/V2/V3/V12/V4/V9/V5 as
  provisioned, V7 absent, and root capability masks as in row 51.

**Does not prove, for P5.0-R5:**

* anything about `FS_APPEND_FL`/`FS_IMMUTABLE_FL`, the probe, the seal, the
  genesis, the chain, a generation, V-W, V-C, V-R or any J-row;
* any §2.12.2 identity or group, or C-3/C-4;
* durability across a reboot or crash: R8's barriers were *issued, not
  verified* (I2/V8 untouched);
* capability causation (R8 §11);
* any fact about the production host, which is not provisioned.

R6 is not counted anywhere in this reconciliation (retained historical
evidence only). V6/I12 closure explicitly *"confirms only the approved
read-only prerequisite survey"*.

---

## 8. Stale, superseded or contradicted P5.0-R5 claims in controlled documents

Identified, **not corrected** in this pass (corrections need assignment).
Dated historical narrative that states a then-current count is not listed.

| # | Location | Claim | Current fact |
|---|---|---|---|
| S-1 | `docs/project-management/raid-register.md:1760`, P5.0-R5 status cell | The narrative ends at revision 10 (*"Codex decides whether this route closes the finding"*) | Revisions 11 and 12, P5.0-SR1/SR2 closure (2026-09-02), OD-66 J-1 closure, I3 closure and this reconciliation are absent from the controlling row |
| S-2 | `raid-register.md:1780`, R-5.0-11 | *"twenty-one conditions"*, `SW-J01 … SW-J21` | twenty-eight conditions, `SW-J01 … SW-J28` (PP §2.13.6) |
| S-3 | `raid-register.md:1787`, A-5.0-5 | Lacks revision 12's provenance widening (component m). Its R8 clause (*"`setpriv --ambient-caps=+linux_immutable`"*) is phrased as a live widening in the same row that withdraws it | PP §7.4 A-5.0-5 |
| S-4 | PP §6.1 row 13 | *"`TC-5.0-JNL-01…26`"*; *"the ten-row manipulation matrix"* | 53 identifiers, 114 cases; fifteen rows (PP §2.13.8, §2.13.4) |
| S-5 | PP §6.5 item 12 | *"the **thirteen-row** manipulation matrix"* | fifteen rows |
| S-6 | PP §8.1 first rows | Test interpreters `/opt/discord-bots/venv*/bin/python`; all H-rows describe the development host | AGENTS.md canonical interpreter is `/opt/freedom-blades/runtime/venv-web/bin/python` on `oracle-test`, and the approved target differs (MD-2) |
| S-7 | `docs/review/phase-5-0-gemini-operational-evidence-runbook.md` "P5.0-R5 resolution path" | Numbering skips item 2. *"C-4 JNL-49 and JNL-50 executed and passed: All 96 cases"*. C-3 reduced to one `O_TRUNC` `EPERM`. A-5.0-5 owned by the Security Reviewer. Closure conditions omit most of the band | C-4 is `JNL-52`; `JNL-49`/`JNL-50` hold 24 cases; the band is 114; C-3 is the four-stage probe; A-5.0-5's owner is the Operations Owner |
| S-8 | CP §1 and `tools/phase_5_0_evidence/approved_target.py:65` (generated/source text) | *"Codex independently verified … ext4 append-attribute support"* | No recorded method or output. Must not be read as C-3 or A-5.0-5 evidence (row 09) |
| S-9 | `tools/phase_5_0_evidence/journal.py` docstrings | *"the five refusals P5.0-R5 needs evidence for"*; *"The order matters and is the writer's own"* | §3.13 |

---

## 9. OD-62 G-A — effect, analysis only

OD-62's binding ruling is gated on *"independent acceptance that P5.0-R5's
enumeration control is fail-closed"*. On this reconciliation that precondition
is **not met**, and nothing in it moves closer without MD-1.

* **If MD-1 chooses facsimile-plus-carry-forward:** a closure review becomes
  reachable after the harness bands execute cleanly, the §3.13 contradictions
  are resolved and R-5.0-10 … 16 are dispositioned. G-A could then become
  binding before product implementation, and product-code journal evidence
  becomes a release-gate condition.
* **If MD-1 requires production-code evidence:** G-A cannot bind until Package
  5.0 implementation exists. But implementation is gated on OD-62. That cycle
  has to be broken by an explicit decision, not by reading.
* **Either way, G-A's residual is unchanged.** The journal is not a barrier
  (§2.13.10). R-5.0-8, the late-Google-apply case, is neither narrowed nor
  widened by any row here. What a closed P5.0-R5 would add is that the
  **enumeration** the operator adjudicates at a supervised cutover is
  trustworthy across reboot and tampering. That is the part of Peter's
  in-principle acceptance (small user base, known supervised time) that
  depends on P5.0-R5.

This does not make G-A binding, close OD-62 or recommend either.

---

## 10. Files inspected

`CLAUDE.md`; `.agents/AGENTS.md` (complete); `docs/implementation-plan.md` (reading
map, §0, Phase 5 package table in §12, §13, §15.1, §16, §17, §18–§20);
`docs/review/Handover information` (current and recent blocks);
`docs/operations/disposable-test-server.md` (restriction banner);
`docs/review/phase-5-0-package-plan.md` (header, §2.13.1 – §2.13.11 complete,
§6.1, §6.5, §7.4 A-5.0-5 and R-5.0-12 … 16, §8.1, §8.3 N5.0-20 … 23);
`docs/review/phase-5-0-security-review.md`;
`docs/review/phase-5-0-security-rereview-revision-12.md`;
`docs/review/phase-5-0-security-review-brief.md` §4;
`docs/review/phase-5-0-logical-schema.md` (section index for §2.9, §3.4, §3.5,
§3.7, §3.7.1, §3.8, §4.3); `docs/project-management/status.md` (current
blocks); `docs/project-management/raid-register.md` (P5.0-R5, R-5.0-10/11,
A-5.0-5, LAB-R5 rows, R-5.0-15/16 notes);
`docs/project-management/decision-register.md` (OD-62 block);
`docs/discovery/open-decisions.md` (OD-62, OD-63 … OD-66 headings, OD-66
body); `docs/review/project-review-2026-09-19-reserved-laboratory-i12-v6-closure.md`;
`docs/review/project-review-2026-09-21-reserved-laboratory-i3-r8-prompt-acceptance.md`;
`docs/review/project-review-2026-09-22-r8-r4-acceptance-and-r8-dispositions.md`;
`docs/review/project-review-2026-09-22-r6-findings-and-i3-disposition.md`;
`docs/review/phase-5-0-reserved-laboratory-i3-r8-controlled-write-handback.md`
(§§1, 2, 4, 5, 7 – 11); `docs/review/phase-5-0-reserved-laboratory-direction.md`
(decision and repercussions);
`docs/review/phase-5-0-evidence-harness-concrete-plan.md` (§1, §2, §3 step
table, §5d, §6); `docs/review/phase-5-0-evidence-harness-execution-plan.md`
(targeted); `docs/review/phase-5-0-gemini-disposable-server-remediation-handback.md`
§8; `docs/review/phase-5-0-gemini-operational-evidence-runbook.md` (header,
P5.0-R5 path); `docs/review/phase-5-0-remediation-r4-handback.md` (targeted);
`tools/phase_5_0_evidence/__init__.py`, `journal.py`, `required_cases.py`,
`filesystem.py`, `durability_model.py`, `lifecycle_storage.py` (headers),
`approved_target.py` (targeted); `tests/phase_5_0_evidence/test_bands.py`
(test index and journal tests); `migrations/versions/` (listing).

The full R8-R1 … R8-R6 handbacks were not re-read. Their findings are closed by
maintainer disposition, they changed documentation and no measured value (per
the dispositions read above), and none bears on a P5.0-R5 proposition.

## 11. Files changed

| File | Change |
|---|---|
| `docs/review/phase-5-0-p5-r5-evidence-reconciliation-handback.md` | **new** — this handback |
| `docs/review/Handover information` | a new top block recording the assignment, consumption and return |
| `docs/implementation-plan.md` §20 | a new *Current action* paragraph; the former one relabelled *Superseded action* |
| `docs/project-management/status.md` | a new *Current status* section; the former one relabelled *Superseded status* |
| `docs/operations/disposable-test-server.md` | a new *Restriction unchanged* banner |

No source, test, hook, manifest, generated artifact, migration, schema,
configuration, Package 5.0 design or evidence artifact was changed. The prompt
file was not edited. The RAID, decision and change registers were deliberately
**not** changed: this pass records no decision and closes nothing, and S-1 … S-3
are reported rather than corrected.

**Git status:** 103 paths before (per `git status --porcelain=v1`), 104
expected after. The one new path is this handback. The four pointer files were
already modified before this pass and remain modified.

## 12. Checks run, and checks not run

**Run:**

1. `git status --porcelain=v1`, before (103 paths) and after.
2. Focused local tests, database-free, answering rows 08–10, 12–13, 18, 22, 25,
   26, 34, 36, 49–53 and 55:
   `env -u TEST_DATABASE_URL PYTHONDONTWRITEBYTECODE=1 /opt/freedom-blades/runtime/venv-web/bin/python -m pytest -q -rs -p no:cacheprovider tests/phase_5_0_evidence/test_bands.py tests/phase_5_0_evidence/test_no_execution.py`
   → **342 passed, 0 skipped, 0 failed, 2 warnings** (`PytestConfigWarning`
   for the unknown options `asyncio_mode` and
   `asyncio_default_fixture_loop_scope`). This ran on the **repository host**,
   not `oracle-test`, with Python 3.12.3 and pytest 9.1.1. `TEST_DATABASE_URL`
   was unset. Neither module touches a database (`test_no_execution.py` only
   reads source to assert forbidden imports are absent). **A pass here proves
   the classifiers agree with their own tests, not with §2.13.6.** See §3.13.
   The tree was unchanged afterwards (103 paths).
3. Targeted `grep` consistency searches for every row's identifiers, the S-1 …
   S-9 claims, `JNL-` case identifiers in `tools/` and `tests/`, and
   production-journal symbols (none found outside the evidence harness).
4. `git diff --check` over the changed files, after the edits (§13).

**Not run:**

* anything on `oracle-test` (prohibited);
* any database-marked, bot, web or Foundry suite (unnecessary for a
  documentation-only reconciliation, and a database run is prohibited);
* the full `tests/phase_5_0_evidence` directory (not needed to answer a row);
* a secrets scan (prohibited);
* formatter, linter, type checker (none configured; no code changed).

## 13. Security, data-authority, rollback and deployment implications

* **Security:** none introduced. The pass surfaces one missing security-review
  condition (row 15) and four classifier contradictions (§3.13) that would
  mis-attribute refusals if a band ran as-is.
* **Data authority:** unchanged. No PostgreSQL, Sheet or Foundry state was read
  or written.
* **Deployment:** none.
* **Rollback:** delete this handback and remove only the four inserted pointer
  blocks named in §11, restoring the two relabelled headings (*"Superseded
  action, 2026-09-22 — accept and assign, or revise, the draft C-P5.0-R5-E1
  evidence-reconciliation prompt."* back to *"Current action, …"* in plan §20,
  and *"Superseded status — draft P5.0-R5 evidence-reconciliation prompt
  prepared"* back to *"Current status — …"* in `status.md`). **Do not** use
  `git checkout --` on any of the four files: each carried earlier-pass,
  uncommitted changes before this pass, and restoring `HEAD` would erase them.

## 14. Proposed Codex independent-review focus

1. Whether the state vocabulary in §2 is applied consistently, and especially
   whether any `implemented_not_verified` row should be `test_only`.
2. §3.13 C-1 … C-4: confirm against PP §2.13.5b/§2.13.6, and decide whether
   they are findings against the accepted harness.
3. Row 15: whether the 2026-08-31 Stage 4 conditions survived the rev-12
   re-review as open requirements, as read here.
4. §7: whether any R8 fact is over- or under-credited, and whether the
   corroborations in rows 01, 51 and 52 should be removed rather than noted.
5. MD-1's framing, and whether the circularity in §9 is stated correctly.
6. The reboot recommendation in §6.
7. S-1 … S-9 completeness.
