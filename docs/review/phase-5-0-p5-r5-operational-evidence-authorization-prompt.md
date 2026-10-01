# DRAFT — NOT AUTHORIZED — P5.0-R5 harness-facsimile feasibility-evidence pass on `oracle-test`

> # DRAFT ONLY. NOT ACCEPTED. NOT AUTHORIZED. DO NOT EXECUTE.
>
> Proposed identifier: **C-P5.0-R5-OP1**. Claude drafted this on 2026-09-24
> under the repository-only assignment in
> [`phase-5-0-p5-r5-operational-evidence-prompt-drafting-claude-prompt.md`](phase-5-0-p5-r5-operational-evidence-prompt-drafting-claude-prompt.md).
> Codex reviewed those bytes on 2026-09-27 and requested changes
> ([review](project-review-2026-09-27-p5-r5-operational-evidence-prompt.md)).
> Claude amended this file in place on 2026-09-27 under
> [`phase-5-0-p5-r5-operational-evidence-prompt-remediation-claude-prompt.md`](phase-5-0-p5-r5-operational-evidence-prompt-remediation-claude-prompt.md)
> (**C-P5.0-R5-OP1-R1**); the changes are listed in the
> [remediation handback](phase-5-0-p5-r5-operational-evidence-prompt-remediation-handback.md).
> Codex re-reviewed those bytes (`7a73d3da…`) on 2026-09-27 and requested
> changes ([R1 re-review](project-review-2026-09-27-p5-r5-operational-evidence-prompt-r1.md),
> finding OP1-R1-1: the RP-11 capture contract was not crash-consistent).
> Claude amended this file in place again on 2026-09-27 under
> [`phase-5-0-p5-r5-operational-evidence-prompt-r2-durability-remediation-claude-prompt.md`](phase-5-0-p5-r5-operational-evidence-prompt-r2-durability-remediation-claude-prompt.md)
> (**C-P5.0-R5-OP1-R2**), a requirements-only correction of RP-11 and §9.5;
> the changes are listed in the
> [R2 handback](phase-5-0-p5-r5-operational-evidence-prompt-r2-durability-remediation-handback.md).
> Codex reviewed those bytes (`308e788c…`) on 2026-09-27 and requested
> changes ([R2 review](project-review-2026-09-27-p5-r5-operational-evidence-prompt-r2.md),
> findings OP1-R2-1, one capture root for both passes, and OP1-R2-2, the
> stop and finalization order). Claude amended this file in place again on
> 2026-09-27 under
> [`phase-5-0-p5-r5-operational-evidence-prompt-r3-contract-consistency-remediation-claude-prompt.md`](phase-5-0-p5-r5-operational-evidence-prompt-r3-contract-consistency-remediation-claude-prompt.md)
> (**C-P5.0-R5-OP1-R3**), a requirements-only correction; the changes are
> listed in the
> [R3 handback](phase-5-0-p5-r5-operational-evidence-prompt-r3-contract-consistency-remediation-handback.md).
> Codex reviewed those bytes (`026edf43…`) on 2026-09-27 and requested
> changes ([R3 review](project-review-2026-09-27-p5-r5-operational-evidence-prompt-r3.md),
> finding OP1-R3-1: Pass B did not verify that Pass A's retained capture root
> and final index still exist and match the Pass A handback). Claude amended
> this file in place again on 2026-09-27 under
> [`phase-5-0-p5-r5-operational-evidence-prompt-r4-retention-verification-remediation-claude-prompt.md`](phase-5-0-p5-r5-operational-evidence-prompt-r4-retention-verification-remediation-claude-prompt.md)
> (**C-P5.0-R5-OP1-R4**), a requirements-only correction; the changes are
> listed in the
> [R4 handback](phase-5-0-p5-r5-operational-evidence-prompt-r4-retention-verification-remediation-handback.md).
> Codex reviewed those bytes (`20fa2ce0…`) on 2026-09-27 and requested
> changes ([R4 review](project-review-2026-09-27-p5-r5-operational-evidence-prompt-r4.md),
> finding OP1-R4-1: B0-RA did not detect the absence of an unadmitted file
> named by Pass A's final state). Claude amended this file in place again on
> 2026-09-27 under
> [`phase-5-0-p5-r5-operational-evidence-prompt-r5-unadmitted-retention-remediation-claude-prompt.md`](phase-5-0-p5-r5-operational-evidence-prompt-r5-unadmitted-retention-remediation-claude-prompt.md)
> (**C-P5.0-R5-OP1-R5**), a requirements-only correction; the changes are
> listed in the
> [R5 handback](phase-5-0-p5-r5-operational-evidence-prompt-r5-unadmitted-retention-remediation-handback.md).
> Codex reviewed those R5 bytes (`5e06a388…`) with no findings, and Peter
> Duscha accepted that requirements correction on 2026-09-27
> ([R5 review](project-review-2026-09-27-p5-r5-operational-evidence-prompt-r5.md);
> [acceptance](project-review-2026-09-27-p5-r5-operational-evidence-prompt-r5-acceptance.md)).
> Codex then reviewed the returned RP-11 implementation and requested changes
> ([RP-11 review](project-review-2026-09-28-p5-r5-rp11-capture-mechanism.md),
> findings RP11-I1-1, publication by an unnamed inode and an exclusive link
> rather than the accepted temporary name and rename, and RP11-I1-2, the
> publication route did not reproduce on the review host). Claude amended this
> file in place on 2026-09-28 under
> [`phase-5-0-p5-r5-rp11-i1-r1-publication-contract-and-portability-remediation-claude-prompt.md`](phase-5-0-p5-r5-rp11-i1-r1-publication-contract-and-portability-remediation-claude-prompt.md)
> (**C-P5.0-R5-RP11-I1-R1**), a requirements-only proposal; the changes are
> listed in the
> [I1-R1 handback](phase-5-0-p5-r5-rp11-i1-r1-publication-contract-and-portability-remediation-handback.md).
> Codex reviewed the I1-R1 bytes (`186ff546…`) and an I1-R2 diagnostic
> correction and requested changes
> ([I1-R1 review](project-review-2026-09-28-p5-r5-rp11-i1-r1.md);
> [I1-R2 review](project-review-2026-09-28-p5-r5-rp11-i1-r2.md)). Peter Duscha
> then accepted a change of publication design
> ([I1-R3 proposal](phase-5-0-p5-r5-rp11-i1-r3-publication-redesign-proposal.md);
> [acceptance](project-review-2026-09-28-p5-r5-rp11-i1-r3-redesign-acceptance.md)).
> Claude amended this file in place again on 2026-09-28 under
> [`phase-5-0-p5-r5-rp11-i1-r3-retained-alias-implementation-claude-prompt.md`](phase-5-0-p5-r5-rp11-i1-r3-retained-alias-implementation-claude-prompt.md)
> (**C-P5.0-R5-RP11-I1-R3-I1**), together with the unwired RP-11 source; the
> changes are listed in the
> [I1-R3 handback](phase-5-0-p5-r5-rp11-i1-r3-retained-alias-implementation-handback.md).
> **The I1-R3 amendment supersedes only the I1-R1 publication amendment**: the
> unnamed-inode route through `/proc/self/fd` and the mutating §9.5.4 capability
> probe are replaced by an exclusively created staging name, one non-replacing
> descriptor-relative hard link to the final name, and retention and indexing
> of both names, with no automatic unlink, rename, repair or alias cleanup
> (§9.5.1). It reopens no accepted R5 retention requirement.
> Claude corrected state wording only, on 2026-09-28, under
> [`phase-5-0-p5-r5-rp11-i1-r3-r1-retained-alias-review-remediation-claude-prompt.md`](phase-5-0-p5-r5-rp11-i1-r3-r1-retained-alias-review-remediation-claude-prompt.md)
> (**C-P5.0-R5-RP11-I1-R3-R1**, finding RP11-I1-R3-3): statements that no RP-11
> mechanism exists now state that unwired, unaccepted repository source and
> focused tests exist and that RP-11 remains unmet, and the unadmitted-pair
> rule is marked as awaiting a decision of record (finding RP11-I1-R3-1). No
> requirement is added, removed or changed by that correction.
> Peter Duscha then accepted **Option 1** for that rule
> (**C-P5.0-R5-RP11-I1-R3-D2**, 2026-09-28), after Codex re-reviewed the R2
> descriptor-release remediation and found no new Blocking or Important
> finding. RP11-I1-R3-1 is Closed by that decision; RP11-I1-R3-2 and
> RP11-I1-R3-3 are Closed as remediated. The
> [decision and review record](project-review-2026-09-28-p5-r5-rp11-i1-r3-r2-and-unadmitted-pair-decision.md)
> records all three dispositions. Codex amended this file in place on
> 2026-09-28 under **C-P5.0-R5-RP11-I1-R3-D2-DOC1**
> ([handback](phase-5-0-p5-r5-rp11-i1-r3-d2-option-1-documentation-alignment-handback.md)),
> replacing the pending-decision markers in RP-11 row (e), §7.1 B0-RA and
> §9.5.2 X-4 with that decision. Claude corrected its wording on 2026-09-28
> under **C-P5.0-R5-RP11-I1-R3-D2-DOC1-R1**
> ([handback](phase-5-0-p5-r5-rp11-i1-r3-d2-doc1-r1-alignment-review-remediation-handback.md)):
> this attribution, §4.3's list of stale manifest versions and B0-RA's
> unresolved clause. The Option-1 rule adds no requirement beyond the
> metadata-only pair exception already stated, and RP-11 remains unwired and
> unmet.
> **These amended bytes have not been reviewed or accepted.** Until Codex
> independently reviews them and Peter Duscha accepts these exact bytes, the
> accepted R5 bytes (`5e06a388…`) remain the requirements baseline, and no
> implementation may claim to satisfy this amendment. The draft remains
> unaccepted and unauthorized.
>
> It grants **no** authority. It authorizes no SSH, synchronization,
> inspection, `sudo`, database access, provisioning, controlled write, verifier
> or evidence-band invocation, reboot or `--execute`. It remains inert until
> all three of the following are recorded, in this order and against the same
> file bytes:
>
> 1. Codex's independent technical, security, operational and evidence
>    pre-execution acceptance of this exact amended draft and the pinned
>    repository state (§4.1 A-1);
> 2. Peter Duscha's explicit, band-by-band written authorization (§4.2); and
> 3. assignment of a named operator (§1).
>
> **Admission status as amended — neither pass is executable.**
>
> * **Pass A** (§6, Bands A0–A1: local admission, then **synchronization plus a
>   read-only host preflight**) is **not admissible**. Its one planned target
>   mutation is the `rsync --delete` of §5. It needs **RP-11**, a reviewed
>   client-side evidence-capture mechanism with a crash-consistent publication
>   sequence for stream files, per-act records and the capture index (§9.5).
>   RP-11 is unmet: repository source and focused tests for a candidate
>   mechanism exist, but that implementation is unreviewed, unaccepted, not
>   pinned and wired to no operational command. Pass A also needs
>   the maintainer inputs `MI.pinned_commit`, Pass A's own capture root
>   `MI.capture_root_A` and the MD-5 independent acceptance (A-6), none of
>   which exists. Its corroborative target-fact steps (A1-C) additionally need
>   RP-10.
> * **Pass B** (§7, Bands B0–B7) is **not admissible**. The repository
>   prerequisites RP-1 through RP-12 (§4.4) are unmet. Several are code or
>   artifacts that do not exist, and none of them is satisfied by Pass A.
>   Pass B also needs its own capture root `MI.capture_root_B`, distinct from
>   Pass A's retained root (§4.5), and a successful read-only retention
>   verification (B0-RA, §7.1) proving that Pass A's retained root and final
>   index state still match the Pass A handback, and that the names present
>   under that root and the names Pass A's final state accounts for agree in
>   both directions, before `MI.capture_root_B` is created or any Pass B host
>   command is issued.
>
> Either pass may be authorized only after an amended draft pins every
> prerequisite it depends on as satisfied, the reviewed tree is a clean pinned
> commit, any changed covered source has a new manifest version and reviewed
> digest, and Codex has independently re-reviewed those exact bytes.

---

## 0. How to read this prompt

| Part | Contents |
|---|---|
| §1 | Target, operator, Independent Reviewer and authorization owner |
| §2 | Evidence class. Feasibility is not production-code evidence |
| §3 | The binding decisions MD-1 through MD-6 and the restrictions carried forward |
| §4 | Admission: authority preconditions, the authorization matrix, repository pins, repository prerequisites, maintainer inputs, typed observation preconditions and the provenance rule for stated target facts (§4.7) |
| §5 | The one synchronization method |
| §6 | **Pass A**: Band A0 (local admission) and Band A1 (synchronization plus read-only host preflight), with exact commands |
| §7 | **Pass B**: Bands B0 through B7 (local re-admission, synchronization and read-only re-preflight, harness provisioning and controlled mutation, database evidence, remaining facsimile producers including `fsync` failure injection, recovery rehearsals, supervised reboot, cleanup and clean-state survey) |
| §8 | Case-to-requirement matrix |
| §9 | Expected outputs, artifact locations, ownership and modes, evidence-manifest fields, and the client-side capture contract (§9.5), including the retained-alias publication route (§9.5.1) and its capability test, the first real X-1 publication (§9.5.4) |
| §10 | Rollback and cleanup |
| §11 | Stop conditions, the global stop-on-refusal rule and the no-retry rule |
| §12 | Secrets, credentials and protected historical `/tmp` artifacts |
| §13 | Intended target-side changes and the final clean-state survey |
| §14 | Handback template |
| §15 | What success does and does not establish |

Placeholders take one of four typed forms, and each form fails closed:

* `⟨PIN.name⟩` is a value fixed by the reviewed repository state. It is resolved
  in this draft wherever the repository fixes it (§4.3). Where it is not yet
  resolvable, the admission check refuses.
* `⟨RP-n⟩` is a repository prerequisite that is not yet met (§4.4). Any band
  that depends on one is not admissible.
* `⟨MI.name⟩` is a maintainer input, supplied in the written authorization
  (§4.5). A band that needs a missing input does not start.
* `⟨OP.name : shape⟩` is a value that only observation can supply (§4.6). A
  value that does not match its shape, or that differs from its expected value,
  stops the band.

**No placeholder may be filled by the operator's own judgement, by a default,
or by a value that "looks right".**

---

## 1. Parties

| Role | Party |
|---|---|
| **Target** | `oracle-test`: the approved disposable host, IPv4 `138.2.182.39`, kernel nodename `Test`, Ubuntu `26.04.1 LTS`, `x86_64`, active kernel `7.0.0-31-generic`. Confirmed disposable by Peter Duscha as Operations Owner on 2026-09-05. Under MD-2 it is the only host whose facts count ([MD-2](project-review-2026-09-23-p5-r5-md2-host-facts-baseline.md)) |
| **Approved disposable run root** | `/var/lib/fb-evidence-p5-0`, the only canonical run root `R`. V11 and `/opt/freedom-blades/evidence` were withdrawn |
| **Approved disposable database** | `fb_evidence_p5_0` on PostgreSQL `16/main`, port `5432`, socket directory `/var/run/postgresql`. **Never** `freedom_test` or `freedom_dev` |
| **Harness confirmation token** | `oracle-test:/var/lib/fb-evidence-p5-0:fb_evidence_p5_0#fc2a9c9b9d581cc7` (manifest v21) |
| **Operator** | `⟨MI.operator⟩`. The proposal is **Claude, as implementing operator**, following the C-P5.0-LAB-I3-R8 precedent. The authorization must name the operator. Nobody else may issue a host command under this prompt |
| **Independent Reviewer** | **Codex**: technical, security, operational and evidence review, before execution (this draft) and after it (the returned evidence). Codex does not operate the pass and cannot approve its own recommendation |
| **Authorization owner** | **Peter Duscha**, as Acceptance Authority, Operations Owner and Data Owner. Only he authorizes host access, synchronization, controlled mutation, database work, recovery rehearsals and the supervised reboot. Only he decides P5.0-R5 closure after independent review |

---

## 2. Evidence class — feasibility, not production code

Under [MD-1](project-review-2026-09-23-p5-r5-md1-evidence-criterion.md), this
pass produces **harness-facsimile feasibility evidence** only.

* Every record this pass produces is labelled
  **`evidence_class: feasibility-facsimile`**, and every handback heading says
  *feasibility*.
* **Feasibility evidence** establishes that the reviewed mechanisms can be
  built and exercised safely on the approved disposable target: filesystem
  attributes, identities, capability constructions, sandbox attribution,
  durability across a supervised reboot, and rehearsed recovery procedures.
* **Production-code evidence** establishes that the implemented Sheet writer,
  `freedom-journal-admin`, the coordinator and migration `0014` enforce the
  accepted contract. **None of these exists**, and nothing in this pass
  implements, deploys, simulates or stands in for them. Such evidence is
  mandatory at the later implementation/release gate. The same gate repeats the
  JNL-02b reboot against the production writer (MD-3) and repeats the
  R-5.0-11, R-5.0-14 and R-5.0-16 recovery rehearsals against production
  journal code (MD-4).
* **The two classes are not substitutable in either direction.** A passing
  facsimile case is never reported as a writer, coordinator, admin-tool or
  migration result. A case classified in §8 as `production-gate` is never run,
  approximated or reported here.

---

## 3. Binding decisions and restrictions carried forward

| Decision | Record | How this prompt preserves it |
|---|---|---|
| **MD-1** — feasibility evidence may close P5.0-R5; production-code evidence stays mandatory at the implementation/release gate; the classes are separate | [MD-1](project-review-2026-09-23-p5-r5-md1-evidence-criterion.md) | §2 labelling. §8 separates `feasibility` from `production-gate` rows. §15 |
| **MD-2** — only freshly observed `oracle-test` facts count; package-plan §8.1 development-host observations are historical context | [MD-2](project-review-2026-09-23-p5-r5-md2-host-facts-baseline.md) | Band A1 observes the host facts fresh and binds them to the pass's target identity and pinned artifacts. The twelve harness target facts are freshly observed by the harness's own `P-05` and `P-06` steps in Pass B and compared there with **owner-stated, independently verified** expectations (RP-1, RP-10, §4.7); a fresh observation is never also the expectation it is compared with. **No §8.1 value is used as an expected value.** A fact that differs from §8.1 is reported as a target fact and is not normalized away |
| **MD-3** — the supervised reboot durability case (JNL-02b) is mandatory for feasibility closure and may not be Not Run or turned into a residual | [MD-3](project-review-2026-09-23-p5-r5-md3-reboot-requirement.md) | Band B6 is **mandatory**. A Pass B that stops before B6 completes leaves P5.0-R5 **open**. It is never reported as "reboot Not Run, accepted" |
| **MD-4** — `R-5.0-10` … `R-5.0-16` accepted as active residuals; recovery rehearsals for `R-5.0-11`, `R-5.0-14` and `R-5.0-16` are mandatory evidence | [MD-4](project-review-2026-09-23-p5-r5-md4-residual-dispositions.md) | Band B5 carries the three rehearsals, and each is mandatory. No residual is re-opened, re-scoped or claimed closed |
| **MD-5** — the classifier corrections must have passed independent review before any band is executable | [MD-5](project-review-2026-09-23-p5-r5-md5-classifier-prerequisite.md) | Precondition A-6: **unmet** until a durable, dated, independent acceptance record of the C-1 … C-4 corrections exists. The local classifier tests (A0-06, B0) and the synchronized-byte checks (A1-S1, A1-S2) are **preflight evidence only**: they show that the pinned bytes are present and pass their own tests, and they are never that acceptance |
| **MD-6** — JNL-40(b)'s second-host or `/etc/machine-id` rewrite is not required; `R-5.0-13` stays active with its external-evidence controls | [MD-6](project-review-2026-09-24-p5-r5-md6-jnl-40b-disposition.md) | JNL-40(b) is **excluded** (§8). **`/etc/machine-id` is never written.** It is read only as a digest, for the reboot identity check |

**Controlling state, unchanged by this prompt:** P5.0-R5 remains **Blocking**.
OD-62 G-A remains conditional and not binding. `plan.is_executable=False`
remains controlling. Package 5.0 remains not ready. No implementation,
migration `0014`, deployment, production or `--execute` authority exists until
the authorization in §4.2 grants a specific band.

**Always prohibited, whatever is authorized:**

* production-host access;
* production credentials;
* the production Google Sheets;
* any production database;
* `freedom_test` and `freedom_dev`, as a target of any write;
* migration `0014` anywhere. It does not exist. Even if it did, it could run
  only on an explicitly authorized disposable database;
* any change to the live Freedom bot or to Discord;
* any secrets scan;
* protected historical `/tmp` artifacts (§12);
* Git history rewrites, `git reset --hard` and `git checkout --`;
* broad or recursive deletion;
* any weakening or bypass of a guard.

---

## 4. Admission

### 4.1 Authority preconditions — all of them before the first host command of either pass

| # | Precondition | How it is shown | If unmet |
|---|---|---|---|
| **A-1** | Codex has accepted **this exact amended draft**, identified by its SHA-256 `⟨PIN.prompt_sha256⟩`, and the pinned repository state in §4.3: a **clean** commit `⟨MI.pinned_commit⟩` and, where any covered source changed, the new manifest version and reviewed digest. The acceptance must be independent, pre-execution and technical, security, operational and evidence review. A review of earlier bytes, including the 2026-09-27 review of `9bd4f5b5…`, the 2026-09-27 R1 re-review of `7a73d3da…`, the 2026-09-27 R2 review of `308e788c…`, the 2026-09-27 R3 review of `026edf43…` and the 2026-09-27 R4 review of `20fa2ce0…`, is not this acceptance | a dated review record under `docs/review/` naming the prompt digest, the commit and the reviewed digest | no pass starts |
| **A-2** | Peter Duscha's written authorization grants the specific rows of §4.2 for this pass and names the operator | a dated decision record under `docs/review/`, quoted verbatim in the handback | no pass starts. An ungranted row's band does not start |
| **A-3** | No newer handover, restriction banner, decision or status record supersedes or narrows this prompt | the operator reads the top of `docs/review/Handover information`, the first banner of `docs/operations/disposable-test-server.md`, `docs/project-management/status.md` and implementation-plan §20 immediately before Band A0. Each must name this prompt (by identifier and digest) as the active authorized assignment | stop before any host command |
| **A-4** | The approved target identity is confirmed | Band A1 observations A1-01 … A1-06 equal the expected values in §6.2 | stop at the first mismatch |
| **A-5** | The target holds no production data and no production credential | **Peter Duscha's written attestation** in the A-2 record, as Operations Owner and Data Owner, dated on or after the date of the A-2 authorization. **No secrets scan and no content inspection is performed to establish this** (§12). The 2026-09-05 sentence in concrete plan §1 is **not** that attestation (reconciliation S-8) | no pass starts |
| **A-6** | MD-5's prerequisite is met: the C-1 … C-4 classifier corrections of C-P5.0-R5-R1 have passed independent review | a **durable, dated, independent acceptance record** under `docs/review/` that names the C-1 … C-4 corrections and the `journal.py` digest it accepts, referenced by `⟨MI.md5_disposition⟩`. **MD-5 is unmet today.** The repository holds no explicit acceptance of C-P5.0-R5-R1 itself: Codex's R1 review raised only PLAN-1 and DESIGN-1, later assignments refer to "the accepted C-1…C-4 journal classifier mappings", and the change-log row for R1 still reads *"Not approved; design amendments pending review"*. A maintainer statement without that independent record, a green A0-06, or a matching A1-S2 digest is **not** the acceptance | no band beyond A0 starts |

### 4.2 Authorization matrix — each row is granted or refused separately

| Row | Grants | Needed by | State in this draft |
|---|---|---|---|
| **AUTH-SYNC** | The one synchronization of §5, once per pass | A1, B1 | **not granted** |
| **AUTH-READ** | The read-only host observations of Band A1 and the Band B1 re-check, including `sudo` for reading only | A1, B1, B6, B7 | **not granted** |
| **AUTH-DBREAD** | Read-only PostgreSQL catalog queries (`pg_database`, `pg_roles`) as `postgres` against the `postgres` maintenance database | A1-D, B7 | **not granted.** If refused, A1-D is recorded as not run, and Pass B cannot start |
| **AUTH-V7** | Initialization of laboratory record V7 (`/var/lib/freedom-blades/laboratory/lifecycle.json`). This is **irreversible by contract**: a used host is never reinitialized | B1 | **not granted.** Also blocked by `V7_EXCLUSION` in source (RP-8) |
| **AUTH-HARNESS** | The single reviewed harness `--execute` invocation of Band B2. It includes provisioning (M-01 … M-43), controlled mutation (identity, filesystem, capability and probe bands), the PostgreSQL band (M-39 … M-42 and B6-01 … B6-08) and derived cleanup (CL-01 … CL-47). **The harness cannot run a subset**, so this row cannot be granted without AUTH-DB | B2, B3, B4 | **not granted.** Blocked by RP-1 … RP-4 and RP-8 |
| **AUTH-DB** | Creation and removal of `fb_evidence_p5_0` and role `freedom_migration_coordinator` (`PASSWORD NULL`); the byte-exact capture, replacement and restoration of `pg_hba.conf` and `pg_ident.conf` on cluster `16/main`, and the reload. **No migration of any kind** | B2, B3 | **not granted** |
| **AUTH-PRODUCERS** | The reviewed facsimile producers of RP-3, RP-5, RP-6, RP-7 and RP-12, each by its pinned argv | B4a, B4b, B5, B6 | **not granted.** Blocked: the producers do not exist |
| **AUTH-RR** | The three mandatory recovery rehearsals of Band B5, including the named operator recovery acts they require | B5 | **not granted** |
| **AUTH-REBOOT** | One supervised reboot of `oracle-test` in Band B6, after the live `⟨MI.reboot_go⟩` confirmation | B6 | **not granted** |

**Pass A** needs AUTH-SYNC and AUTH-READ; AUTH-DBREAD is optional. **Pass B**
needs every row, and a further live confirmation for the reboot. **No row is
usable while RP-11 is unmet**: every host command of either pass, including the
synchronization, must be issued through the reviewed capture mechanism of §9.5,
and a granted row does not substitute for it.

### 4.3 Repository pins — resolved from the repository on 2026-09-24

These are the values the drafting pass observed. **None of the
C-P5.0-R5-OP1-R1, C-P5.0-R5-OP1-R2, C-P5.0-R5-OP1-R3, C-P5.0-R5-OP1-R4 and
C-P5.0-R5-OP1-R5 and C-P5.0-R5-RP11-I1-R1 remediations re-derived them**; each changed documentation only (I1-R1 also added one diagnostic test module, which is not a covered source). **Four later repository passes changed covered sources and so made
`PIN.manifest_version`, `PIN.reviewed_digest`, `PIN.manifest_json_sha256`,
`PIN.concrete_plan_sha256` and `PIN.covered_sources` stale:** C-P5.0-R5-RP11-I1
(manifest version 22, review-input digest `adeabe17…`),
C-P5.0-R5-RP11-I1-R3-I1 (manifest version 23, review-input digest
`264674daf8ac4f6a385e3c056510d213321c767b1d482a143b18a139b108df1e`),
C-P5.0-R5-RP11-I1-R3-R2 (manifest version 24, review-input digest
`bccd26e59aa94a64dc8888eb6265c68da7d4c8c7d1705d85932e5ebad01a05d7`) and
C-P5.0-R5-RP11-I1-R3-D2-DOC1 (manifest version 25, review-input digest
`f63cf3596a95701e3c24813f5362955dcdb5524e7b4fcaf749159db66f91cdb8`). None
re-pins anything here; each is review input only, and a later amended draft
must re-pin the values from a clean, reviewed commit. They are
review inputs, not approvals. The Codex review re-derives each one. The operator
re-checks each one in Band A0 or B0, and **any difference refuses admission**.
Any prerequisite satisfied by changing a covered source (at least RP-1, and
RP-11 or RP-12 if either is placed in a covered source) produces a new manifest
version and reviewed digest, which a further amended draft must pin before
Codex's re-review.

| Pin | Value at drafting | Note |
|---|---|---|
| `PIN.head` | `2fb1d6fd88013752d53af76fc97b4db07fc31181` | branch `docs/platform-plan` |
| `PIN.worktree` | **unresolved: the tree is uncommitted.** `git status --porcelain=v1` lists 140 entries, including every Package 5.0 harness change since `HEAD` | **`⟨MI.pinned_commit⟩` is required.** The maintainer commits, or directs a commit of, the exact reviewed tree on a non-default branch, and Codex reviews that commit. A0-02 then requires `HEAD == ⟨MI.pinned_commit⟩` and a porcelain status that is empty. This pass never synchronizes an unpinned working tree |
| `PIN.manifest_version` | `21` | `tools/phase_5_0_evidence/review_manifest.py` |
| `PIN.reviewed_digest` | `ac5ffb3cc1a077618d8fc0590a803ec42282a3a1011d4edfc9ff1eafb5137dad` | Review input only, **not approved**. Pass A pins `⟨PIN.reviewed_digest_A⟩`, which equals this value **only if** the satisfied RP-11 changes no covered source; otherwise it is the new reviewed digest. Pass B needs a new digest (RP-1 changes covered source), so Pass B pins `⟨PIN.reviewed_digest_B⟩` |
| `PIN.capture_tool_sha256` | **unresolved: no reviewed RP-11 mechanism exists.** The returned, unaccepted implementation computes a candidate value; it is review input only and is not pinned here | **Scope (proposed by C-P5.0-R5-RP11-I1-R1 for review; unchanged by I1-R3).** The digest covers exactly these seven complete source files, as whole files and in this order: `tools/phase_5_0_evidence/capture_contract.py`, `errors.py`, `execution/boundary.py`, `execution/capture_mechanism.py`, `execution/capture_store.py`, `execution/descriptors.py` and `execution/retention_check.py`. Its construction is the one the returned source defines as schema `rp11-capture-tool/1`: the SHA-256 of the canonical JSON document `{"schema": "rp11-capture-tool/1", "sources": [[path, SHA-256 of that file's bytes], …]}` in that fixed order. **Why whole modules:** the mechanism's process start lives in `boundary.py` and its one link call site lives in `descriptors.py`, and both modules also carry reviewed code for other harness callers. No reviewed canonical construction exists for a digest over part of a module, and none is invented here. **Consequence, stated plainly:** any change to any byte of any of the seven files — including a change to `boundary.py` or `descriptors.py` that is unrelated to RP-11 — produces a different digest and invalidates the pin, and requires a new review before either pass can use it. A0-08, B0-08 |
| `PIN.manifest_json_sha256` | `ea5d22c1bf6826f0296d5c2ee4b2295331d612eab6d250c0772fdf1068b6cd66` | `docs/review/phase-5-0-evidence-harness-review-manifest.json` |
| `PIN.concrete_plan_sha256` | `5437147546f268e3d1b81c84270ff9a7255d2a079a9534da775dd5a478840cfd` | `docs/review/phase-5-0-evidence-harness-concrete-plan.md` |
| `PIN.covered_sources` | 48 covered sources. All 48 match the manifest's `source_digests` byte for byte | checked by a read-only script at drafting |
| `PIN.journal_py` | `b9ecf08c87ad0928e8d31436fd3ab1e5f0a4442ae451c80364ef09cbea93d0a9` | the MD-5 classifier |
| `PIN.unit_sandbox_py` | `edd360fbd01aaded56ee29bdf61af5cb9ae0882d0f990ad8f4e620fd8fc7a92c` | S4-3's four conditions |
| `PIN.case_program_py` | `5ec710a5f8ba3f1f40b33ea3768baef4721cc8a361c4b1681f6e63686a7dd2b6` | installed byte-for-byte as `R/bin/case` |
| `PIN.cli_py` | `485f960f1dee97feaef4a6c1f8e002c27262a427db470cd91c5dd36f057cb4d1` | the only `--execute` entry point |
| `PIN.reservation_py` | `aa37107590755a6307b79bea7e37b1cca45e44709f99a54f1e390e09dc52340b` | holds `REAL_EXECUTION_REFUSAL` |
| `PIN.dry_run` | `steps planned 138`, `mutations declared 43`, `cleanup steps derived 47`, `unresolved conflicts 4 (C-7, C-S4-3)`, twelve unconfirmed facts (`interpreter_sha256`, `interpreter_real_path`, `E7.{cap_amb,cap_bnd,cap_eff,cap_inh,cap_prm,gid,groups,no_new_privs,securebits,uid}`), `executable False` | the local dry run at drafting, which executed nothing |
| `PIN.prompt_sha256` | set by Codex at review of the exact amended bytes; a file cannot contain its own digest. The digests Codex reviewed on 2026-09-27 (`9bd4f5b5…`, then `7a73d3da…`, then `308e788c…`, then `026edf43…`, then `20fa2ce0…`) are superseded by this amendment | A0-03 |
| `PIN.interpreter` | `/opt/freedom-blades/runtime/venv-web/bin/python`, flags `-I -S`, Python 3.12 | AGENTS.md "Running the suites". The disposable-server document records 3.12.14 on the target |

### 4.4 Repository prerequisites — unmet today; each blocks the bands named

These are **not** observation-dependent values. They are repository artifacts
or decisions that do not exist. Each needs its own separately assigned
repository pass, independent review and, where stated, a maintainer decision.
This draft does not create any of them and does not specify their code. It
states only what the passes require of them. **No pass satisfies a
prerequisite**, and none is reduced or waived to make a pass appear executable.

| # | Prerequisite | Why the band cannot run without it | Blocks |
|---|---|---|---|
| **RP-1** | The twelve reviewed target facts are supplied in source: `case_runtime.EXPECTED_INTERPRETER_SHA256`, `EXPECTED_INTERPRETER_REAL_PATH` and the ten `capability.E7_TARGET_FACTS`. **Each value is an owner-stated expectation that meets the §4.7 provenance rule and has been independently verified by the method RP-10 establishes.** No value is taken from Pass A, from `grep`, `/proc`, `id` or `capsh`, or from `P-01`, `P-02`, `P-05` or `P-06`; an observation is never both the expectation and the thing compared with it. The manifest is then regenerated to a new version and digest. **RP-1 cannot be satisfied while RP-10 is unmet** | `ExecutingRunner` refuses construction while any of them is unconfirmed. `capability.py` states the sentinel stays until *"the Operations Owner states it for the current target and an independent reviewer verifies it there"*; `case_runtime.py` states the same for the interpreter facts; concrete plan `P-06` requires the E7 expectations to be *"supplied from outside and verified by an independent reviewer … none … learned from P-01, P-02, this observation, /proc, id or capsh"* | B2 … B4 |
| **RP-2** | Conflict **C-S4-3** is resolved, or the maintainer records an explicit feasibility-scope decision for S4-3. Resolution requires a reviewed unit and drop-in policy, a capture vector for all 12 `unit_sandbox.COMPARED_PROPERTIES`, the canonical `ReadWritePaths=` substitution, and a reviewed `SystemdIdentity` producer. **Open question for Codex and the maintainer:** under MD-1, may a reviewed *facsimile* unit stand in for the non-existent deployed `freedom-sheet-writer.service` for feasibility? This draft does not decide it | `plan.is_executable` is `False` while C-S4-3 is unresolved | B2 … B4 |
| **RP-3** | Conflict **C-7** is resolved. Reviewed, bounded, evidence-only producers exist for `JNL-47-NO-GENERATION-ON-FAILURE`, `JNL-47-RECOVERY-STATE` and `JNL-51-PROVENANCE-OMITTED`, with their outputs routed through `execution.evidence_cli` | `plan.is_executable` is `False` while C-7 is unresolved. R-5.0-14 and R-5.0-16 have no rehearsal producer | B2 … B5 |
| **RP-4** | **EH-R16-1** has an accepted ownership remedy, reflected in the reviewed source path that sets `ownership_remedy_accepted` | `reservation.REAL_EXECUTION_REFUSAL` refuses every real execution unconditionally. *"It is not cleared by a preflight, a green suite or an exclusive host"* | B2 … B4 |
| **RP-5** | A reviewed **reboot-durability producer**, pinned by argv and source digest in a manifest. It must create, exclusively under `R`, a harness-facsimile generation laid out per package-plan §2.13.3: a journal file `freedomsheet:freedomcoord 0640` with `FS_APPEND_FL`; a seal `root:freedomjournal 0440` with `FS_IMMUTABLE_FL`; a `current` symlink; and a genesis record, one `startup` record and **one `dispatch` record with no `outcome`**, encoded per §2.13.8 with a verifiable hash chain. It must also provide a read-only **re-verify** mode that re-derives the chain and the unresolved set, and a reviewed **cleanup** that clears the attributes as root and removes exactly what it created. **Its lifecycle spans a reboot**, so it cannot be a step of the single-process harness run | MD-3's required evidence (*"a harness-created disposable generation containing an unresolved dispatch … journal, append-only attribute, immutable seal and chain intact and re-verifiable"*) has no producer today. Reconciliation row 44 |
| **RP-6** | Reviewed facsimile producers, **and the written recovery procedures they exercise**, for the three mandatory rehearsals: **RR-11** (R-5.0-11), **RR-14** (R-5.0-14) and **RR-16** (R-5.0-16), with the minimum content in §7.5. `docs/operations/migration-cutover-and-rollback.md` (WP-9), which package plan §2.13.2b names as the home of the recovery procedures, **does not exist**. Until it does, the only written procedures are package-plan §2.13.2b and §2.13.7 | MD-4 makes the rehearsals mandatory, and there is nothing to run | B5 |
| **RP-7** | Missing vectors for the feasibility rows in §8: the `JNL-13` fifteen-row manipulation matrix (with the parent-rename row), the remaining 21 `JNL-49`/`JNL-50` cases, `JNL-48(b)`, `JNL-30` and `JNL-48(d)` | Those rows have no producer | B4 |
| **RP-8** | Laboratory prerequisites for reservation admission: `V7_EXCLUSION` lifted in source and V7 initialized (AUTH-V7); **V8** (directory `fsync` as the containing-entry barrier) and **V10** (all seven participants run as `ubuntu`) confirmed by the method the maintainer approves; the host inventory complete | admission refuses an incomplete inventory, and the lifecycle record is absent by contract | B1, B2 |
| **RP-9** | Open design rulings recorded rather than guessed: `unit_sandbox.SUPPORTED_DROP_INS` being empty (R1 §10 item 2); the J-12/J-17 unreadable-seal and J-02 → `J-20` coordinator readings (R1 §3); whether the systemd-identity availability cost is inside MD-4's acceptance of R-5.0-11/R-5.0-16 (open under the R3 acceptance and not addressed by MD-4's text); and the conflict between package plan §2.13.8 (*"the disposable `freedom_test` database"*) and concrete plan M-39 (*"never freedom_test … finding F-6"*). **This prompt follows the concrete plan and finding F-6** | a band built on an unruled reading would encode a choice the maintainer has not made | B2 … B5 |
| **RP-10** | **A reviewed provenance and independent-verification method for owner-stated target facts** (§4.7). The governing sources require the twelve facts to be *stated* by the Operations Owner (or a maintainer) for `oracle-test` and *verified there* by an independent reviewer, and forbid learning them from the observations named in RP-1. **They do not say what non-observational basis a statement may rest on, or how the reviewer verifies it on the host without that verification becoming the source.** For E7 in particular, every obvious basis (the kernel's `CAP_LAST_CAP`, the `sudo` policy's effect on a root process, the launcher's bounding set) is itself a host observation. This draft does not choose a method. A later, separately assigned repository pass must propose one; Codex must review it for technical soundness; and the maintainer must accept it. If no sound method exists for some fact, the maintainer must decide that explicitly — this draft does not | RP-1 has no admissible input, so `ExecutingRunner` stays refused. The A1-C corroborative steps have no pinned statement to corroborate | RP-1 (so B2 … B4); A1-C |
| **RP-11** | **A reviewed client-side evidence-capture mechanism** meeting every requirement of §9.5: exact argv, separate and complete stdout and stderr bytes with their SHA-256 digests, client UTC start and end, exit status, a per-act record bound to its command, a fixed, **pass-specific** capture root on the repository host outside the worktree (`⟨MI.capture_root_A⟩` for every act of Pass A and `⟨MI.capture_root_B⟩` for every act of Pass B, distinct and each with its own index chain; C-6, C-14), and fail-closed behaviour — **with no file created on `oracle-test`**. It must also implement the **crash-consistent publication contract** of §9.5.1 and §9.5.2 (C-13, C-14): both stream files completed, closed, file-synchronized and their directory entries made durable before the record that publishes their digests exists; each per-act record written under an exclusively created **staging name** in the directory that will hold it, checked and file-synchronized, given its final name by one non-replacing, no-follow, descriptor-relative **exclusive final link** of the same inode (§9.5.1), followed by a successful synchronization of its containing directory and verification of both names, and **admitted only by the next durable index state**, which records both names and their shared inode, before the next act begins — **with both names retained and no automatic unlink, rename, repair or alias cleanup**; and one capture index per pass, under that pass's own capture root, created, advanced and finalized by the same barriers, with a defined final state whose SHA-256 the handback states. A failure of any file or directory barrier is an `inconclusive` stop under C-10 and §11.2, followed by the single ordered stop transition of §9.5.3. It must also provide the **read-only Pass A retention verification** that Pass B's admission step B0-RA performs (`⟨RP-11.retention_check⟩`, §7.1, C-8): before Pass B's X-1, it establishes that `⟨MI.capture_root_A⟩` is the root the Pass A handback records, that the root and the final index state the handback names still exist, that the re-derived SHA-256 of that state equals the handback's capture index SHA-256, that X-4 still holds for Pass A's retained chain, records and bound stream files, and that one complete recursive enumeration of the relative names under that root agrees **in both directions** with the names Pass A's final state accounts for, each at its exact relative name and expected object type (§7.1, B0-RA condition 5) — by listing names and object types, reading bytes and re-deriving digests only, and without writing, moving, renaming, truncating, completing, repairing, adopting, deleting or changing the permissions of anything under that root. For an unadmitted object, which has no recorded digest, it establishes presence, relative name and object type only, **never that its bytes or metadata are unchanged**. **Which interfaces achieve these semantics, and the proof that they do on the repository host's filesystem — including how the check safely resolves relative names and detects duplicate or ambiguous names, path aliases, traversal outside the root and unexpected object types, and the proof that the retention verification changes nothing under `⟨MI.capture_root_A⟩` — belong to RP-11's implementation and review; this draft names the required semantics only and does not claim RP-11 is satisfied.** **State (corrected by C-P5.0-R5-RP11-I1-R3-R1):** repository source and focused tests for a candidate mechanism exist (`capture_contract.py`, `execution/capture_store.py`, `execution/capture_mechanism.py`, `execution/retention_check.py` and the RP-11 route in `execution/descriptors.py`); that implementation, this requirements amendment and the review-manifest digest over them are unreviewed and unaccepted; the mechanism is wired to no operational command; C-11 and the pinned launcher environment below remain unresolved; no real capture root and no Pass A handback exist; and RP-11 remains unmet. The harness's `capture.py` deliberately keeps no raw output (*"raw output has no representation that survives this module"*), and the client transcript is merged and may be truncated, so neither can establish separate byte-exact stream digests. RP-11 must also state, and Codex must review, how the §5 synchronization is captured **without changing the command `guard-secrets.py` inspects**; a capture method that hides the `rsync` from the guard is a bypass and is not acceptable. **Amended by C-P5.0-R5-RP11-I1-R1 and, for publication, by C-P5.0-R5-RP11-I1-R3 (proposed, unreviewed):** RP-11 must also provide (a) the **retained-alias publication** of §9.5.1, whose capability is tested, fail-closed, by the pass's first real publication — its X-1 genesis state — before any host command, with **no separate mutating probe** (§9.5.4); (b) the **one shared, no-follow link call site** of §9.5.1 serving exactly two reviewed named-source contracts, stated there; (c) the **behavioural terminal seal** of §9.5.3 step 4 as the meaning of *read-only*; (d) the fixed **`rp11-capture-binding/1` block** of §14, which is the only part of the Pass A handback B0-RA parses; and (e) the **one alias exception** of X-4 and B0-RA: a recorded staging/final pair of one object may share an inode, and nothing else may (§9.5.2 X-4, §7.1). **Two RP-11 blockers remain unresolved and are not decided by this amendment:** how the §5 synchronization is issued through the mechanism without changing what `guard-secrets.py` inspects (C-11), and the exact process environment the mechanism supplies to the `ssh` and `rsync` invocations it launches, which must be pinned in reviewed bytes before any wiring and is never inferred or inherited at execution time. No mechanism may be wired to an operational command while either is open | §9.3's per-act record cannot be produced, so no host command's evidence could be admitted; and Pass A's retention cannot be verified at Pass B admission | **A1**, **B0-RA** and every host command of **B1 … B7** |
| **RP-12** | **A bounded, reviewed `fsync` fault-injection producer and its evidence contract** (reconciliation row 40, JNL-17/J-14, A-5.0-5(k)). No injection mechanism exists or is specified in the harness. Package plan §4 (estimate and capacity) names two candidates without choosing — *"a loopback device with `dm-error`, or a `LD_PRELOAD` interposer in the harness"* — and this draft chooses neither. The reviewed contract must at least fix: the mechanism; its exact scope (only objects the producer creates under `R`, affecting no other file, filesystem, device or process); the facsimile consumer whose `fsync` fails and what it must record (the failure observed, the facsimile generation treated as terminal, dispatch refused, non-zero exit); the pinned argv; its reviewed cleanup and a read-only survey proving nothing remains; and whether it needs any package, kernel module or device not already present — **which would need a separate maintainer decision and an amendment of §13.1** | row 40 is remaining **P5.0-R5 feasibility work** (§8) and has no producer. Only a new, explicit maintainer disposition naming the resulting residual may defer it; this draft makes no such disposition | **B4b**, and therefore P5.0-R5 feasibility closure |

### 4.5 Maintainer inputs — supplied in the A-2 authorization, never by the operator

| Input | Shape | Used by |
|---|---|---|
| `MI.operator` | a named person or agent | all |
| `MI.pinned_commit`, `MI.pinned_commit_B` | 40 lowercase hex each; `_B` is the commit carrying the satisfied RP work | A0-02, B0 |
| `MI.md5_disposition` | a reference to a dated record | A-6 |
| `MI.pass_a_window_utc` / `MI.pass_b_window_utc` | a start and end instant (UTC, ISO 8601) | the operator may not start outside the window |
| `MI.run_id` | `\A[A-Za-z0-9][A-Za-z0-9._-]{0,63}\Z` (`participants.RUN_IDENTIFIER`) | B2 |
| `MI.reservation_id` | non-blank, and the same value in every B-band reference | B2 |
| `MI.deadline` | UTC ISO 8601 `YYYY-MM-DDTHH:MM:SSZ` | B2 |
| `MI.reservation_owner`, `MI.recovery_owner` | named person. The proposal is Peter Duscha for both | B2 |
| `MI.run_record_path` | an absolute path, reviewed by Codex. It must lie **outside** `/tmp`, the synchronized worktree, `R`, V4, V9 and V5 unless runner contract r6 expressly permits the location. **Unresolved: a typed blocker.** No governing source fixes it and this draft does not invent one; B2 does not start without it | B2 |
| `MI.capture_root_A` | **Pass A's own capture root**: an absolute path on the **repository host**, reviewed by Codex, that does not exist before Pass A, lies outside the Git worktree (so A0-02's empty status holds) and outside `/tmp`, on a filesystem whose file and directory synchronization semantics and same-directory hard links RP-11's review has accepted — and whose support for the §9.5.1 route is tested, fail-closed, by Pass A's own X-1 genesis publication (§9.5.4) — and is created exclusively by the RP-11 mechanism in Pass A's X-1, with its own genesis state and index chain (§9.5, C-6, C-14). After Pass A it is **retained and unmodified, and never used as Pass B evidence** (C-8): it is never removed, renamed, reused or modified to make `⟨MI.capture_root_B⟩` absent. Pass B's only access to it is B0-RA's read-only retention verification (§7.1). **Unresolved: a typed blocker** | A0-08 and Pass A's X-1; every host command of A1; Pass A's X-2 … X-4 and handback; **B0-RA, read-only, as a retention check only. Never Pass B evidence** |
| `MI.pass_a_handback` | the repository path of the Pass A handback (§9.1) and its SHA-256, supplied in Pass B's A-2 authorization. From those exact bytes, after authenticating them by that SHA-256, B0-RA parses **only** the handback's one fixed `rp11-capture-binding/1` block (§14) and takes from it, **as recorded and never re-typed, inferred or supplied by the operator**: the pass ID, the capture root, the X-3 outcome, the X-4 validity, the final index state's name and the capture index SHA-256 (§9.5 C-12). No prose line of the handback is parsed. A handback without exactly one well-formed block is not admissible input, and B0-RA stops. **Unresolved: no Pass A handback exists** | B0-RA |
| `MI.capture_root_B` | **Pass B's own capture root**: an absolute path on the repository host, reviewed by Codex, that **differs from `⟨MI.capture_root_A⟩`**, lies neither within it nor contains it, and **independently** meets every condition stated for `⟨MI.capture_root_A⟩`: absent before Pass B, outside the Git worktree and `/tmp`, on a filesystem RP-11's review has accepted, whose support for the §9.5.1 route is tested, fail-closed, by Pass B's own X-1 genesis publication (§9.5.4), and created exclusively by the RP-11 mechanism in Pass B's X-1, with its own genesis state and index chain. It is never derived from, created inside or made available by changing Pass A's root. **Unresolved: a typed blocker** | B0-08, only after B0-RA has succeeded, and Pass B's X-1; every host command of B1 … B7; Pass B's X-2 … X-4 and handback |
| `MI.target_fact_statement` | a reference to the dated, digest-pinned record of the twelve owner-stated target facts and their provenance (§4.7), with the independent verification RP-10 requires. **Unresolved: blocked by RP-10** | RP-1; A1-C |
| `MI.reboot_go` | Peter Duscha's live confirmation in the operating session, given after Band B6.1 has been reported to him, quoted verbatim | B6.3 |
| `MI.producer_argv.*` | the pinned argv of every RP-3, RP-5, RP-6, RP-7 and RP-12 producer | B4a … B6 |

*Timestamp format.* The harness validates `--at`, `--requested-at` and
`--deadline` only as non-blank as far as this drafting read found. This prompt
fixes UTC ISO 8601 `YYYY-MM-DDTHH:MM:SSZ` for all three. Codex should confirm
this against the record schema.

### 4.6 Typed observation preconditions — observed fresh, never invented

| Value | Shape | Expected | On mismatch |
|---|---|---|---|
| `OP.nodename` | string | `Test` | stop (A-4) |
| `OP.kernel_release` | string | `7.0.0-31-generic` | stop, and report as a target fact (MD-2). A-5.0-5(h)'s premise is stated for 6.8.x, so the difference is recorded, never normalized |
| `OP.arch` | string | `x86_64` | stop |
| `OP.os_pretty_name` | string | `Ubuntu 26.04.1 LTS` | stop |
| `OP.boot_id_*` | lowercase UUID | recorded. B6 requires pre ≠ post | stop if unreadable |
| `OP.machine_id_sha256` | 64 lowercase hex, the digest only | recorded. B6 requires pre = post | stop |
| `OP.var_lib_mount` | `SOURCE FSTYPE OPTIONS` | `/dev/sda1 ext4 rw,…` (source and type exact; options start `rw`) | stop |
| `OP.protected_hardlinks` | integer | `1` | stop |
| `OP.interpreter_real_path` | an absolute normalized path | **corroborative only** (A1-C). Compared with the pinned `MI.target_fact_statement`; **never an RP-1 input** | stop if not absolute, or if it differs from the statement (reported, never used to amend the statement) |
| `OP.interpreter_sha256` | 64 lowercase hex | **corroborative only** (A1-C), as above | stop if unreadable or different, as above |
| `OP.interpreter_version` | `3.12.x` | major.minor `3.12` (`case_runtime.INTERPRETER_PYTHON_VERSION`, a source constant) | stop |
| `OP.sudo_root_status.*`, `OP.sudo_capsh.*` | the shapes in `capability._E7_FACT_SHAPES` (`uid`/`gid`/`no_new_privs` decimal; `groups` comma-separated decimal; five masks 1–16 hex; `securebits` 1–2 hex) | **corroborative only** (A1-C). They describe a `sudo`-launched `grep` and a `sudo`-launched `capsh` process, **not** the final interpreted E7 process, and are **never an RP-1 input** | stop if unparseable; a difference from the statement is reported, never reconciled |
| `OP.capsh` | owner, mode and package version | present, `root:root`, not group- or world-writable | stop |
| `OP.systemd_identity` | `systemctl --version` first line and the `dpkg-query` version | recorded. RP-2 input | — |
| `OP.pg_hba_sha256`, `OP.pg_ident_sha256` | 64 hex each | recorded. B7 requires equality with the B1 values, which must equal Pass A's | stop in B7 on inequality |
| `OP.free_bytes_var_lib` | integer | recorded, compared with N5.0-21 = 1 GiB | stop Pass B if below 2 GiB (proposal; Codex to confirm the margin) |

### 4.7 Stated target facts — provenance, independence and the corroboration rule

The twelve RP-1 facts are **expectations**, and the harness's `P-05` and `P-06`
steps in Pass B are the **observations** compared with them. The two must have
independent origins; otherwise the comparison checks a value against itself.
Any RP-10 method the maintainer accepts must meet at least these requirements.
This draft states them as requirements and does not claim a method exists that
meets them.

1. **Stated, not learned.** Each value is stated by the Operations Owner (or,
   for the interpreter facts, a maintainer) for `oracle-test`, in a dated,
   digest-pinned record (`MI.target_fact_statement`). The record gives, for
   every fact, the **basis** of the statement. A basis that consists of reading
   the value on the host — by `grep`, `/proc`, `id`, `capsh`, `sha256sum`,
   `readlink`, `P-01`, `P-02`, `P-05`, `P-06`, Pass A or any other observation
   — is not admissible.
2. **Fixed before corroboration.** The record is pinned by digest before the
   A1-C steps run and before Pass B, so no observation made under this prompt
   can have shaped it. Earlier recorded observations of `oracle-test` already
   exist (for example R8's corroboration of a full root `CapBnd`,
   reconciliation rows 51–52). The record must name every such observation its
   author had seen, and RP-10 must rule whether that exposure disqualifies the
   stated basis. This draft does not rule on it.
3. **Independently verified.** A reviewer who did not author the statement
   verifies each value by the method RP-10 establishes, and records the
   verification. **How that verification can be performed on the host without
   becoming the statement's source is exactly what the governing sources leave
   open, and it is why RP-10 is a blocker.**
4. **Corroboration is one-way.** A1-C's observations (A1-11, A1-12, A1-14,
   A1-15) and any later re-reading are compared with the pinned statement and
   reported. A mismatch stops the band and is reported as a target fact. It is
   **never** used to amend the statement, and an amended statement is a new
   record that needs its own independent verification, a new source change,
   a new manifest digest and a further re-review.
5. **Process identity is stated honestly.** A1-14 observes a `sudo`-launched
   `grep` process and A1-15 a `sudo`-launched `capsh` process. Neither is the
   final interpreted E7 process, which exists only inside the harness's `P-06`
   step. Their agreement with the statement is corroboration about a similar
   process, not an observation of E7.
6. **Fail-closed.** While any requirement is unmet, every fact stays
   `UNCONFIRMED` in source, `ExecutingRunner` stays refused, and the A1-C steps
   are recorded `not_run (RP-10 unmet)`.

---

## 5. Synchronization — one method, no alternative, no retry

**Method.** The single documented invocation from
`docs/operations/disposable-test-server.md` §3.2, byte for byte. Its source is
the repository host's `/opt/freedom-blades/platform/` at `⟨MI.pinned_commit⟩`,
with a clean status. Its destination is
`oracle-test:/opt/freedom-blades/platform/`. It is **the only planned target
mutation of Pass A**, and it happens only if AUTH-SYNC is granted. The operator
issues it **once per pass**, from the repository host, as one plain call
through the client's ordinary execution path, captured as RP-11 (§9.5)
specifies. **Until RP-11 states how this command is captured without changing
what `guard-secrets.py` inspects, the synchronization is not executable.**

```bash
rsync -avz --delete \
  --include='.env.example' \
  --exclude='.env*' \
  --exclude='*.pem' \
  --exclude='*.key' \
  --exclude='yt-cookies.txt' \
  --exclude='*service_account*.json' \
  --exclude='*credentials*.json' \
  --exclude='__pycache__/' \
  --exclude='*.py[cod]' \
  --exclude='.pytest_cache/' \
  /opt/freedom-blades/platform/ oracle-test:/opt/freedom-blades/platform/
```

* Do not alter, re-quote, reorder or add an option. Do not use
  `--exclude-from`, `--delete-excluded`, `scp`, `sftp`, a second `rsync` or any
  file list.
* **A refusal by `guard-secrets.py` or any other layer, or a non-zero `rsync`
  exit, ends the pass (§11.1).** Nothing is re-issued in another form.
* `--delete` may remove target-side files absent from the pinned source. That
  is the documented behaviour, and it is listed in §13.1.

---

## 6. Pass A — synchronization plus read-only host preflight (**not admissible: RP-11 and the A-6 and MI inputs are unmet**)

Pass A is **not read-only as a whole**. Its one planned target mutation is the
§5 `rsync --delete`, which replaces the target worktree and may remove
target-side files absent from the pinned source, and which happens only under a
granted AUTH-SYNC. Every host step after it is read-only. Unavoidable incidental
system-log entries (`sshd`, `sudo`, journald) are side effects listed in §13.1,
not planned acts. Pass A invokes no verifier, provisioner, harness `--execute`
or evidence band. Its output is the MD-2 host-fact record and, only where
RP-10 is satisfied, **corroboration** of an already-pinned target-fact
statement. **It is never an input to RP-1.**

### 6.1 Band A0 — local admission on the repository host; no host contact

Run from `/opt/freedom-blades/platform`, in this order. Each command must
produce exactly the expected result, or the pass stops.

| Step | Command | Expected |
|---|---|---|
| A0-01 | read the four current-state records named in A-3 | each names this prompt, by identifier and `⟨PIN.prompt_sha256⟩`, as the active authorized assignment |
| A0-02 | `git -C /opt/freedom-blades/platform rev-parse HEAD` then `git -C /opt/freedom-blades/platform status --porcelain=v1` | `⟨MI.pinned_commit⟩`, then empty output |
| A0-03 | `sha256sum docs/review/phase-5-0-p5-r5-operational-evidence-authorization-prompt.md` | `⟨PIN.prompt_sha256⟩` |
| A0-04 | `sha256sum docs/review/phase-5-0-evidence-harness-review-manifest.json docs/review/phase-5-0-evidence-harness-concrete-plan.md` | `PIN.manifest_json_sha256` and `PIN.concrete_plan_sha256` |
| A0-05 | `env -u TEST_DATABASE_URL PYTHONDONTWRITEBYTECODE=1 /opt/freedom-blades/runtime/venv-web/bin/python -m tools.phase_5_0_evidence.execution.cli` | `DRY RUN — nothing was executed.` with every `PIN.dry_run` figure, including `review manifest digest:` equal to `⟨PIN.reviewed_digest_A⟩` and `executable : False` |
| A0-06 | `env -u TEST_DATABASE_URL PYTHONDONTWRITEBYTECODE=1 /opt/freedom-blades/runtime/venv-web/bin/python -m pytest -q -rs -p no:cacheprovider tests/phase_5_0_evidence/test_r5_r1_journal_classifier.py tests/phase_5_0_evidence/test_r5_r1_stage4_s4_3.py` | 0 failed, **0 skipped**; the pass count recorded exactly. This is a **local MD-5 preflight only**. It shows the pinned classifier passes its own tests. It is **not** MD-5's independent acceptance (A-6), and it says nothing about any band |
| A0-07 | no command. The operator states that `TEST_DATABASE_URL` is not exported in the operating shell. No environment is printed (§12) | statement recorded |
| A0-08 | `⟨RP-11.admission_check⟩`: the reviewed check that the capture mechanism's bytes equal `⟨PIN.capture_tool_sha256⟩` and that `⟨MI.capture_root_A⟩` does not yet exist; then the mechanism creates `⟨MI.capture_root_A⟩` exclusively and publishes Pass A's genesis index state there by the §9.5.1 retained-alias sequence (§9.5.2 X-1). **That genesis publication is the fail-closed capability test of the route (§9.5.4); there is no separate probe.** If it does not reach verification of both of its names, the pass stops here, before any host command; no X-3 attempt is made; whatever X-1 created is retained unmodified and reported by exact relative name as bounded residue; and nothing is retried. **No host command is issued before X-1 succeeds** | as RP-11 fixes it. **Unresolved: RP-11 is unmet** — its repository implementation is unwired and unaccepted, no capture tool digest is pinned, C-11 and the pinned launcher environment are open, and no real capture root exists — **so A0-08 is unusable and Pass A cannot be admitted** |
| A0-09 | no command. The operator confirms that A-6's independent acceptance record and, for A1-C, the digest-pinned `MI.target_fact_statement` with its RP-10 verification exist, and records their references | both referenced, or A1-C is recorded `not_run (RP-10 unmet)`. A missing A-6 record stops the pass |

### 6.2 Band A1 — synchronization plus read-only host preflight on `oracle-test`

Needs AUTH-SYNC and AUTH-READ; A1-D also needs AUTH-DBREAD; **every step needs
RP-11**. Every host command is one plain `ssh oracle-test "…"` call, as
written, issued through the reviewed RP-11 capture mechanism (§9.5), which
records its exact argv, separate stdout and stderr bytes and their digests, UTC
start and end, and exit status **on the repository host**, and publishes them
through the crash-consistent sequence of §9.5.1 and §9.5.2 before the next
command is issued. **No redirection,
no pipe to a file, no output file on `oracle-test`, and no `/tmp` path.** The
client transcript is a convenience and **is not evidence**. `sudo` appears
only where written, and only to read.

**A1-00 — synchronize:** the §5 invocation, exactly once.

**A1-S — the synchronized tree is the pinned tree.**

| Step | Command | Expected |
|---|---|---|
| A1-S1 | `ssh oracle-test "cd /opt/freedom-blades/platform && env -u TEST_DATABASE_URL PYTHONDONTWRITEBYTECODE=1 /opt/freedom-blades/runtime/venv-web/bin/python -m tools.phase_5_0_evidence.execution.cli"` | identical to A0-05 in every line. This is a dry run that executes nothing. It shows that the synchronized classifier, `unit_sandbox` and harness bytes are **byte-identical to the pinned tree**, because the digest covers every covered source. It is **not** evidence that those bytes are independently accepted; that is A-6 |
| A1-S2 | `ssh oracle-test "cd /opt/freedom-blades/platform && sha256sum tools/phase_5_0_evidence/journal.py tools/phase_5_0_evidence/unit_sandbox.py tools/phase_5_0_evidence/execution/case_program.py tools/phase_5_0_evidence/execution/cli.py tools/phase_5_0_evidence/reservation.py"` | the five `PIN.*_py` values |

**A1-T — target identity and host facts (MD-2).**

| Step | Command | Expected / recorded |
|---|---|---|
| A1-01 | `ssh oracle-test "uname -n"` | `Test` |
| A1-02 | `ssh oracle-test "uname -r"` | `7.0.0-31-generic` |
| A1-03 | `ssh oracle-test "uname -m"` | `x86_64` |
| A1-04 | `ssh oracle-test "grep -E '^PRETTY_NAME=' /etc/os-release"` | `PRETTY_NAME="Ubuntu 26.04.1 LTS"` |
| A1-05 | `ssh oracle-test "cat /proc/sys/kernel/random/boot_id"` | `OP.boot_id_A` recorded |
| A1-06 | `ssh oracle-test "sha256sum /etc/machine-id"` | `OP.machine_id_sha256` recorded. **The digest only**; the value is never printed on its own |
| A1-07 | `ssh oracle-test "findmnt --target /var/lib --noheadings --output SOURCE,FSTYPE,OPTIONS"` | `/dev/sda1 ext4 rw,…` |
| A1-08 | `ssh oracle-test "sysctl fs.protected_hardlinks"` | `fs.protected_hardlinks = 1` |
| A1-09 | `ssh oracle-test "df --output=avail -B1 /var/lib"` | `OP.free_bytes_var_lib` |
| A1-10 | `ssh oracle-test "timedatectl show --property=NTPSynchronized --property=Timezone"` | recorded. UTC timestamps in the handback are taken from the client, and this line records whether the host clock is synchronized |

**A1-I — interpreter version, host tools and corroborative target facts.**
Steps marked **A1-C** are corroborative only (§4.7). They run **only if** A0-09
has referenced a digest-pinned `MI.target_fact_statement` with its RP-10
verification; otherwise each is recorded `not_run (RP-10 unmet)` and the rest
of Pass A continues. Their output is compared with the pinned statement and
reported. **It never becomes an RP-1 input and never amends the statement.**

| Step | Command | Class | Recorded as |
|---|---|---|---|
| A1-11 | `ssh oracle-test "readlink -f /opt/freedom-blades/runtime/venv-web/bin/python"` | **A1-C** | `OP.interpreter_real_path`, compared with the statement |
| A1-12 | `ssh oracle-test "sha256sum ⟨OP.interpreter_real_path⟩"`, with the literal A1-11 output substituted by the operator. No command substitution is used | **A1-C** | `OP.interpreter_sha256`, compared with the statement |
| A1-13 | `ssh oracle-test "/opt/freedom-blades/runtime/venv-web/bin/python -I -S -c 'import sys; print(sys.version_info[:3], sys.flags.isolated, sys.flags.no_site)'"` | host fact | `OP.interpreter_version` (expected `3.12` from source) and the flags `1 1` |
| A1-14 | `ssh oracle-test "sudo grep -E '^(Uid|Gid|Groups|CapInh|CapPrm|CapEff|CapBnd|CapAmb|NoNewPrivs):' /proc/self/status"` | **A1-C** | `OP.sudo_root_status.*`: the status of a **`sudo`-launched `grep` process**. It is **not** the final interpreted E7 process; E7 is observed only by the harness's own `P-06` `identity` step in Pass B, against RP-1's stated expectations |
| A1-15 | `ssh oracle-test "sudo /usr/sbin/capsh --print"` | **A1-C** | `OP.sudo_capsh.*`: the securebits and bounding set of a **`sudo`-launched `capsh` process** (context for `P-01`; not `P-01` and not E7) |
| A1-16 | `ssh oracle-test "stat --format='%n %U:%G %a' /usr/sbin/capsh /usr/bin/chattr /usr/bin/lsattr /usr/bin/systemd-run /usr/bin/setpriv"` | host fact | `OP.capsh` and presence of the other tools. The owner must be `root:root`, and none may be group- or world-writable |
| A1-17 | `ssh oracle-test "dpkg-query --show --showformat='\${Package} \${Version}\n' libcap2-bin e2fsprogs systemd util-linux"` | host fact | recorded. A-5.0-5(g) and RP-2 inputs |
| A1-18 | `ssh oracle-test "systemctl --version"` | host fact | `OP.systemd_identity` |

**A1-L — laboratory and run-root state (read-only survey; no V-item is created or changed).**

| Step | Command | Expected |
|---|---|---|
| A1-19 | `ssh oracle-test "stat --format=%F /var/lib/fb-evidence-p5-0"` | exit `1`: `R` does not resolve. **Exit 0 stops the pass**, and nothing under it is touched |
| A1-20 | `ssh oracle-test "getent group freedomlab"` | present, member `ubuntu` (V1, V2) |
| A1-21 | `ssh oracle-test "stat --format='%n %U:%G %a %F' /etc/tmpfiles.d/freedom-blades-laboratory.conf /var/lib/freedom-blades /var/lib/freedom-blades/laboratory /var/lib/freedom-blades/laboratory/runs /var/lib/freedom-blades/recovery"` | V3 `root:root 644`; V12 `root:root 755`; V4 `root:freedomlab 750`; V9 `root:freedomlab 3770`; V5 `root:root 700` |
| A1-22 | `ssh oracle-test "stat --format=%F /var/lib/freedom-blades/laboratory/lifecycle.json"` | exit `1`: V7 absent, as `V7_EXCLUSION` requires |
| A1-23 | `ssh oracle-test "getent group freedomjournal"`, and separately `freedomcoord`, `freedomsheet` and `fbprobe`, then `getent passwd freedomcoord`, `freedomsheet` and `fbprobe`, each as its own call | exit `2` for all seven. **Any present identity stops the pass**, because the harness's ownership model requires their absence |
| A1-24 | `ssh oracle-test "systemctl show --property=LoadState fb-evidence-s4.service"` | `LoadState=not-found` |

**A1-Q — quiescence and inventory inputs (V10 and RP-8).** Process names
only; argument vectors are never printed (§12).

| Step | Command | Recorded |
|---|---|---|
| A1-25 | `ssh oracle-test "ps -eo uid=,user=,comm= --sort=uid"` | V10 input, and the baseline for B7 |
| A1-26 | `ssh oracle-test "systemctl list-units --type=service --state=running --no-legend --plain"` | the running-service baseline |
| A1-27 | `ssh oracle-test "systemctl list-timers --all --no-legend"` | the timer baseline |
| A1-28 | `ssh oracle-test "loginctl list-sessions --no-legend"` | the session baseline |

**A1-D — PostgreSQL baseline (needs AUTH-DBREAD; read-only).**

| Step | Command | Expected |
|---|---|---|
| A1-29 | `ssh oracle-test "systemctl is-active postgresql@16-main"` | `active` |
| A1-30 | `ssh oracle-test "pg_lsclusters --no-header"` | `16 main 5432 online …`; `18 main 5433 down …` |
| A1-31 | `ssh oracle-test "sudo -u postgres /usr/bin/psql --no-psqlrc --no-password --set ON_ERROR_STOP=1 --host /var/run/postgresql --tuples-only --no-align --dbname postgres --command 'SELECT datname FROM pg_database ORDER BY 1'"` | contains **no** `fb_evidence_p5_0` |
| A1-32 | the same, with `--command 'SELECT rolname FROM pg_roles ORDER BY 1'` | contains **no** `freedom_migration_coordinator` |
| A1-33 | `ssh oracle-test "sudo sha256sum /etc/postgresql/16/main/pg_hba.conf /etc/postgresql/16/main/pg_ident.conf"` | `OP.pg_hba_sha256`, `OP.pg_ident_sha256`. **Digests only**; the contents are never printed |

**A1-Z — Pass A final-state survey (read-only).** Repeat A1-19, A1-21 … A1-24
and, only under AUTH-DBREAD, A1-29 … A1-33, each through RP-11. Every value
must equal its earlier Pass A value: Pass A created nothing on the target
except the synchronized worktree. A difference stops the pass and is reported.

**Pass A ends here.** The operator writes the Pass A handback (§14) and stops.
**Pass A's observations are never RP-1's inputs**, through any later pass or
otherwise (§4.7). Pass A never edits source. Its host facts serve MD-2, and its
A1-C results, if run, are reported corroboration of a statement fixed before
them.

---

## 7. Pass B — feasibility evidence (**not admissible until RP-1 … RP-12 are satisfied and an amended draft is re-reviewed**)

This section fixes Pass B's structure, order, commands where the repository
already fixes them, stop conditions and evidence. Where a producer does not
exist, the command is the typed placeholder `⟨MI.producer_argv.*⟩`. **No
substitute command may be improvised.**

### 7.1 Band B0 — local re-admission; no host contact

Repeat A0-01 … A0-07 and A0-09 against `⟨MI.pinned_commit_B⟩` and
`⟨PIN.reviewed_digest_B⟩`. A0-08 is **not** repeated with Pass A's value.
Two Pass B steps follow, in this order and only after those repeats have
passed: **B0-RA** verifies, read-only, that Pass A's retained evidence is still
what the Pass A handback and Pass A's final state recorded, within the
evidentiary limit B0-RA states for unadmitted files (C-8); only then does **B0-08**, the Pass B
equivalent of A0-08, act against `⟨MI.capture_root_B⟩`.

| Step | Command | Expected |
|---|---|---|
| B0-RA | `⟨RP-11.retention_check⟩`: the reviewed, **non-mutating** Pass A retention verification, on the repository host with no host contact. It first re-derives the SHA-256 of `⟨MI.pass_a_handback⟩` and requires it to equal the supplied digest; it then parses **only** that handback's one `rp11-capture-binding/1` block under the §14 rules, and requires that block to record the pass ID `C-P5.0-R5-OP1-A`, an X-3 outcome of *succeeded at the finalization point*, X-4 validity *valid*, and a final index state name and capture index SHA-256 other than `none`. It then establishes all of the following: **(1)** `⟨MI.capture_root_A⟩` is exactly, byte for byte, the capture root recorded in the Pass A handback's binding block; **(2)** that root exists, and the final index state named by the Pass A handback (Pass A's *F*) exists under it under that final name; **(3)** the SHA-256 re-derived over the bytes of Pass A's *F* equals the Pass A handback's capture index SHA-256; **(4)** X-4 (§9.5.2) still succeeds for Pass A's retained evidence: Pass A's *F* is the only final state; its chain of preceding-state digests is intact back to Pass A's *I*-0; its record list is gap-free from 1 and equals that of the last durable open state; every listed record exists with its listed digest; and every stream file each listed record binds exists with its bound digest; and **(5)** **bidirectional retained-name agreement.** B0-RA takes one complete, recursive enumeration of every name under the root, at every depth and not only the root's immediate entries, as the set *O* of observed relative names, each with its observed object type. From Pass A's *F* and the fixed rules of §9.5.2 it forms the set *R* of accounted relative names, each with its expected object type: *F* itself, each state of *F*'s chain, each listed per-act record and each stream file a listed record binds (each a regular file, as §9.5 defines them); each subdirectory *F* records the mechanism as having created under the root (a directory, C-6); and each object *F* records as unadmitted, at the relative name and object type *F* records for it (X-3). Each accounted name belongs to exactly one of these categories. **Observed to recorded:** every name in *O* is in *R* with the same object type. **Recorded to observed:** every name in *R*, including every unadmitted name, is in *O* at that exact relative name with its expected object type. Names are compared exactly, in the one fixed representation RP-11 defines, and not after any normalization the comparison did not declare. **The one alias exception (C-P5.0-R5-RP11-I1-R3).** Two names may reach one inode **only** when they are the staging name and final name of one object as Pass A's *F* records them (§9.5.1). For an **admitted** pair, both names, their roles, the object type, the owner *F* records, mode `0600`, the device and inode *F*'s chain records, link count two, and — through the final name, whose bytes conditions (3) and (4) digest — the size and digest must agree with that durable state (§9.5.2 X-4). For a pair *F* records as **unadmitted**, only metadata is compared: both recorded names present, regular, sharing one inode at link count two, shared with no other name; nothing is opened, read or digested. **This is Peter Duscha's accepted Option-1 decision** (`C-P5.0-R5-RP11-I1-R3-D2`, 2026-09-28; [decision record](project-review-2026-09-28-p5-r5-rp11-i1-r3-r2-and-unadmitted-pair-decision.md)); RP11-I1-R3-1 is Closed. A third link, a cross-object alias, a missing pair member, a pair whose members are different inodes, a name in two pairs, a wrong link count, an identity or type that differs from *F*'s record, or any other name reaching an accounted inode is a path alias and a fail-closed stop. X-4's barrier-success condition is a fact about Pass A's publication, not a property of the retained bytes; it is taken from the Pass A handback's X-3 and X-4 lines above and is not re-observed. **Evidentiary limit.** For each listed record, bound stream file and index state, conditions (3) and (4) re-derive digests and so establish its bytes. For an unadmitted object and for a recorded subdirectory, which have no recorded digest, condition (5) establishes **only** that the object is present at its recorded relative name with its recorded object type. It does **not** establish that an unadmitted object's bytes or metadata are unchanged, and no unadmitted object is digested, admitted or used as evidence by this check. The check **may only** list names and object types under `⟨MI.capture_root_A⟩`, read bytes and re-derive digests. It **must not** write, move, rename, truncate, complete, repair, adopt, delete or change the permissions of the root or anything beneath it; create anything under it; use any of it as Pass B evidence; or continue, copy or reuse Pass A's index chain. Its result is recorded in the Pass B handback as an admission result, not as a Pass B capture record: no Pass B capture root exists yet. It runs once and is never retried. **It establishes retention at the moment of the check only.** It does not monitor, protect or guarantee Pass A's root afterwards, and this prompt claims nothing about a change made after it | all five conditions hold. **Absence, a mismatch, an X-4 failure, a recorded name absent from *O* (including an absent unadmitted name), an observed name not in *R*, a name whose observed object type differs from its expected type, a duplicate or ambiguous name (a name accounted for twice, in two categories or in two pairs, or two entries the fixed representation cannot tell apart), a path alias (an entry that reaches an accounted object by a second name, or through a symbolic link) **other than the one exception below**, a name that resolves outside the root, an object type that no category expects, or inability to complete the enumeration or either direction of the comparison is a fail-closed B0 stop**: B0-08 does not run, **no `⟨MI.capture_root_B⟩` is created, no X-1 is performed and no Pass B host command is issued**, and nothing under either root is written. The stop is recorded in the Pass B handback and is not retried (§11.3). **Unresolved: RP-11 is unmet** — its repository implementation, including this retention check, is unwired and unaccepted — **and no real Pass A capture root and no Pass A handback exist, so B0-RA is unusable** |
| B0-08 | runs **only after B0-RA has succeeded**. `⟨RP-11.admission_check⟩`: the reviewed check that the capture mechanism's bytes equal `⟨PIN.capture_tool_sha256⟩`; that `⟨MI.capture_root_B⟩` differs from `⟨MI.capture_root_A⟩` and lies neither within it nor contains it; and that `⟨MI.capture_root_B⟩` does not yet exist. Then the mechanism creates `⟨MI.capture_root_B⟩` exclusively and publishes Pass B's own genesis index state there by the §9.5.1 retained-alias sequence (§9.5.2 X-1). **That genesis publication is Pass B's own fail-closed capability test (§9.5.4)**; Pass A's result is never reused for Pass B. If it does not reach verification of both of its names, Pass B stops here, before any Pass B host command; no X-3 attempt is made; whatever X-1 created under `⟨MI.capture_root_B⟩` is retained and reported as bounded residue; and nothing is retried. Nothing under `⟨MI.capture_root_A⟩` is written, moved, renamed or removed, and nothing of Pass A's root is used as Pass B evidence. **No host command is issued before X-1 succeeds** | as RP-11 fixes it. **Unresolved: RP-11 is unmet** — its repository implementation is unwired and unaccepted, and C-11 and the pinned launcher environment are open — **and B0-RA cannot yet succeed, so B0-08 is unusable** |

A0-05 must now show `unresolved conflicts : 0`,
`unconfirmed facts : none` and `executable : True`. **If it does not, Pass B
does not start.** These values come only from the reviewed RP passes, and the
twelve target facts only from the §4.7 statement. Pass B never produces them
itself, and a Pass A result is never evidence that they are satisfied.

### 7.2 Band B1 — synchronization and read-only re-preflight

Repeat the §5 synchronization once, then A1-S1/A1-S2 against the B pins, then
A1-01 … A1-33, every command through RP-11 and captured under
`⟨MI.capture_root_B⟩`. Any change from the Pass A value is
reported as a target fact. **Pass B stops if an A1-C corroborative value
differs from the RP-1 stated expectation** (interpreter or E7); the difference
is reported and never reconciled into the statement. Then:

| Step | Check |
|---|---|
| B1-Q | A1-25 … A1-28 show no process, unit, timer or session outside the maintainer-approved inventory. Only then may the operator pass `--processes-ended true --transactions-settled true --transient-units-inactive true` in B2. **An unobserved condition is omitted rather than asserted**, which quarantines by design |
| B1-S | A1-09 ≥ 2 GiB |

**B1-V7 (only if AUTH-V7 is granted).** The V7 initialization follows the
reviewed r6 §5.10 procedure named by RP-8, by its pinned command
`⟨MI.producer_argv.v7_init⟩`, exactly once. Then the read-only check
`ssh oracle-test "stat --format='%n %U:%G %a %h %F' /var/lib/freedom-blades/laboratory/lifecycle.json"`
must show `root:freedomlab 640`, one link, a regular file. **It has no
rollback** (§10 item 4).

### 7.3 Bands B2–B4 — one reviewed harness invocation: provisioning, controlled mutation and database evidence

The harness executes as **one process**. It performs, in its reviewed order:
discovery (`R-01` … `R-B-UNIT`); capability prerequisites (`P-01` … `P-06`);
identity provisioning and checks (`B2-01` … `B2-21`), which are **Band B2
provisioning**; filesystem hierarchy and access (`B3-01` … `B3-38`); the
four-stage probe (`B4-01` … `B4-34`); capability identities (`B5-E1` …
`B5-C6-11`), which together are **Band B3 controlled mutation**; the PostgreSQL
band (`B6-01` … `B6-08`, M-39 … M-42), which is **Band B4 database evidence**;
and derived cleanup (`CL-01` … `CL-47`). **The operator cannot pause between
these.** The per-band stop conditions in §11.2 are the harness's own
fail-closed stops, and the operator's only act on a stop is to record it.

Exact command, issued once from the repository host:

```bash
ssh oracle-test "cd /opt/freedom-blades/platform && sudo /opt/freedom-blades/runtime/venv-web/bin/python -m tools.phase_5_0_evidence.execution.cli --execute --confirm-target 'oracle-test:/var/lib/fb-evidence-p5-0:fb_evidence_p5_0#fc2a9c9b9d581cc7' --reviewed-digest '⟨PIN.reviewed_digest_B⟩' --run-id '⟨MI.run_id⟩' --reservation '⟨MI.reservation_id⟩' --author '⟨MI.operator⟩' --at '⟨OP.at : YYYY-MM-DDTHH:MM:SSZ, the client UTC time at issue⟩' --reservation-owner '⟨MI.reservation_owner⟩' --requested-at '⟨OP.requested_at : YYYY-MM-DDTHH:MM:SSZ⟩' --deadline '⟨MI.deadline⟩' --recovery-owner '⟨MI.recovery_owner⟩' --observed-by '⟨MI.operator⟩' --processes-ended true --transactions-settled true --transient-units-inactive true --run-record-out '⟨MI.run_record_path⟩'"
```

* The launcher must be effective UID 0; `sudo` supplies that, and the
  boundary refuses otherwise (`root-identity-unavailable`).
* The confirmation token must stay exactly as above unless RP-1's
  regeneration changes it. In that case `⟨PIN.token_B⟩` replaces it.
* The three quiescence flags are passed **only** if B1-Q observed each
  condition. Otherwise that flag is omitted.

**Expected result:** exit `0`; `state` naming a completed cleanup;
`stopped at : —`; `residue : none`; `configuration : no unresolved risk`;
`cleanup skipped : 0`; `artifact eligible : True`; a `run record` path equal
to `⟨MI.run_record_path⟩`; `reservation` concluded; `release durable : True`;
`run completed : True`; `run unsettled : False`. The whole stdout and stderr
are captured **separately** by RP-11 (§9.5), with their digests; the client
transcript is not the record.

### 7.4 Band B4a — facsimile producers for the remaining feasibility vectors (RP-7) and C-7 (RP-3)

Each producer runs by its pinned argv `⟨MI.producer_argv.jnl13⟩`,
`⟨…jnl49_50⟩`, `⟨…jnl48b⟩`, `⟨…jnl30⟩`, `⟨…jnl48d⟩` and `⟨…c7.*⟩`, in the
order the amended draft fixes, each after the previous one's clean result. C-7
observations enter only through `execution.evidence_cli`, never through a hand
edit:

```bash
ssh oracle-test "cd /opt/freedom-blades/platform && env -u TEST_DATABASE_URL PYTHONDONTWRITEBYTECODE=1 /opt/freedom-blades/runtime/venv-web/bin/python -m tools.phase_5_0_evidence.execution.evidence_cli --observations '⟨RP-3.observations_path⟩' --artifact-out '⟨RP-3.artifact_path⟩' --run-id '⟨MI.run_id⟩'"
```

### 7.4b Band B4b — `fsync` failure injection (reconciliation row 40, A-5.0-5(k); RP-12)

Needs AUTH-PRODUCERS and RP-12, and runs after B4a has settled. This is
**remaining P5.0-R5 feasibility work**, not a production-gate deferral. It
exercises the bounded injection mechanism against a **facsimile** consumer on
`oracle-test`; the production writer's own JNL-17 behaviour is production-code
evidence under MD-1, and neither substitutes for the other.

| Step | Act | Exact command | Expected / stop |
|---|---|---|---|
| B4b-1 | Inject and observe | `⟨MI.producer_argv.fsync_inject⟩` | as RP-12's reviewed evidence contract fixes it. At least: the injected `fsync` failure is observed by the facsimile consumer; the facsimile generation is treated as terminal; dispatch is refused; the exit is non-zero **in the way the contract names**; nothing outside RP-12's declared scope is affected. **Stop on anything else** |
| B4b-2 | Reviewed cleanup | `⟨MI.producer_argv.fsync_cleanup⟩` | exit 0; every object the producer created removed. **Residue stops the pass and is preserved** (§10) |
| B4b-3 | Read-only survey | `⟨RP-12.survey_argv⟩` | no injection artifact remains (for example, no device, mapping or preload configuration, as the reviewed mechanism defines). Repeated as B7-12 |

**Unresolved: RP-12 does not exist.** No injection mechanism is chosen here,
and no command is improvised. Until RP-12 is satisfied, row 40 stays open as
feasibility work, and P5.0-R5 cannot close on this pass unless the maintainer
records a new, explicit disposition naming the resulting residual. This draft
makes no such disposition.

### 7.5 Band B5 — the three mandatory recovery rehearsals (MD-4)

Needs AUTH-PRODUCERS and AUTH-RR, and runs after B2–B4b have settled. **Each
rehearsal is feasibility evidence against a facsimile, labelled as such, and
must be repeated against production journal code at the implementation/release
gate.** RP-6 must supply, for each rehearsal, the procedure text, the pinned
producer argv, and the exact operator acts. The minimum content each must
evidence:

| Rehearsal | Residual | Minimum facsimile evidence | Operator recovery acts that must be named and exercised |
|---|---|---|---|
| **RR-11** | R-5.0-11 — fail-closed refusal until an operator acts | For at least **one filesystem-level** condition (J-13: free space below N5.0-21 on a disposable **loopback** filesystem under `R`, never on `/var/lib` itself) and **one generation-integrity** condition (J-06: `FS_APPEND_FL` cleared by root on the facsimile journal): the facsimile validator refuses with the classifier's named writer and C-a codes, and the refusal carries no path, exception text or `errno` in its operator-safe form. After the named recovery, validation passes again. **The refusal must be observed before the recovery is applied** | J-13: free space restored on the loopback filesystem, then re-validated. J-06: the facsimile rotation (seal, archive `+i`, new generation) per §2.13.7. The old generation is **archived, never edited** |
| **RR-14** | R-5.0-14 — failed privileged cleanup leaves writer-writable residue and blocks generation creation | §2.13.2b state **S-B** produced twice (once after a probe-stage failure, once after a fully passing probe) by planting an artifact the cleanup cannot remove. Required observations: exit code 3; residue named by absolute path with its operation and `errno`; the residue byte-for-byte unchanged; **the next invocation refuses and does not clean**; after the named operator recovery, a re-run is admitted | §2.13.2b's procedure: read the reported paths; `lsattr` each; clear `FS_IMMUTABLE_FL` or `FS_APPEND_FL` as root **only on the named residue paths**; remove exactly those artifacts and the two directories; re-run. **Automatic cleanup stays prohibited.** Every path must lie under `R` |
| **RR-16** | R-5.0-16 — missing approval, missing provenance or deployed-tree drift blocks generation creation and Sheet mutations | Against a **disposable** object store, approval record and deployment root (never `/etc/freedom-blades` on a production host; on `oracle-test` only paths the amended draft pins under `R`): `APR` absent → `DEP-01`; `PVR` removed → the J-26 facsimile refusal; one deployed region-S byte changed → the J-27 facsimile refusal. Then the named recovery restores each, and admission passes | the approval, installation, deployment and rotation recovery path of §2.12.5a and §2.13.7, each step named, in order |

**No rehearsal may touch `/var/lib` outside `R`, `/etc/freedom-blades`, the
PostgreSQL clusters, or any path the amended draft does not pin.**

### 7.6 Band B6 — the mandatory supervised reboot (MD-3, JNL-02b)

Needs AUTH-PRODUCERS (RP-5), AUTH-READ, AUTH-REBOOT, RP-11 and the live
`⟨MI.reboot_go⟩`. Every host command below, including each B6.5 connection
attempt, is issued through RP-11 and gets its own record. It runs **only
after** B2–B5 have settled with no residue,
no unsettled reservation and the PostgreSQL configuration restored: the
§13.2 checks B7-05 and B7-06 are run first, and both must pass. A reboot restarts every service and clears `/run`, so no
harness run may be in progress.

| Step | Act | Exact command | Expected / stop |
|---|---|---|---|
| **B6.1a** | Create the disposable generation | `⟨MI.producer_argv.reboot_create⟩` | exit 0. It reports the generation id, the journal and seal paths under `R`, the `request_id` of the one unresolved `dispatch`, and the record count. **Stop on anything else** |
| **B6.1b** | Pre-reboot durable state | `ssh oracle-test "sudo stat --format='%n %U:%G %a %i %d %s' ⟨RP-5.journal_path⟩ ⟨RP-5.seal_path⟩"`; `ssh oracle-test "sudo lsattr ⟨RP-5.journal_path⟩ ⟨RP-5.seal_path⟩"`; `ssh oracle-test "sudo sha256sum ⟨RP-5.journal_path⟩ ⟨RP-5.seal_path⟩"`; `ssh oracle-test "readlink ⟨RP-5.current_path⟩"`; `⟨MI.producer_argv.reboot_verify⟩` | journal `freedomsheet:freedomcoord 640` with the `a` flag; seal `root:freedomjournal 440` with the `i` flag; the digests recorded; re-verify reports the chain intact and **unresolved set = {that `request_id`}** |
| **B6.1c** | Durability barrier and pre-reboot identity | `ssh oracle-test "sync"`; `ssh oracle-test "cat /proc/sys/kernel/random/boot_id"`; `ssh oracle-test "sha256sum /etc/machine-id"`; `ssh oracle-test "uptime --since"` | `OP.boot_id_pre` and the machine-id digest recorded. The machine-id digest must equal Pass A's |
| **B6.2** | Report to the authorization owner | the operator reports B6.1a–c to Peter Duscha in the operating session | — |
| **B6.3** | **Operator confirmation** | `⟨MI.reboot_go⟩`: Peter Duscha's explicit go, quoted verbatim | **no confirmation means no reboot.** The pass stops, and P5.0-R5 stays open (MD-3) |
| **B6.4** | Supervised reboot | `ssh oracle-test "sudo systemctl reboot"` | **The only expected outcomes are exit 0, or the SSH session closed by the remote (exit 255) with no other diagnostic.** Anything else — a refusal, a `sudo` prompt, an error text — stops the pass, and nothing is re-issued |
| **B6.5** | Bounded reconnection | no earlier than 120 s after B6.4: `ssh -o ConnectTimeout=10 oracle-test "cat /proc/sys/kernel/random/boot_id"`. If it fails to connect, the same command at intervals of at least 60 s, **at most 12 attempts** (about 15 minutes in all). **These pre-declared connection attempts are the only repetition this prompt permits.** They are not a retry of a refused operation. A refusal (as distinct from a connection timeout) ends the pass | a connection, and `OP.boot_id_post` ≠ `OP.boot_id_pre`. **If the host does not return, stop.** Console recovery is outside this prompt and belongs to the Operations Owner |
| **B6.6** | Post-reboot identity | A1-01 … A1-04, A1-06 and A1-07, and `ssh oracle-test "uptime --since"`. A changed SSH host key is refused by `StrictHostKeyChecking` and is a stop | the same values as B6.1c and Pass A. Machine-id digest equal. Kernel equal. `/var/lib` on `/dev/sda1 ext4 rw` |
| **B6.7** | Post-reboot verification | the B6.1b commands again, in the same order | **every** value equal to B6.1b: owner, mode, inode, device, size, `a` and `i` flags, both SHA-256 digests, the `current` target; re-verify reports the chain intact and the **same** unresolved set. Any difference is a **failed** JNL-02b, recorded as such and never re-run |
| **B6.8** | Post-reboot services | A1-26 and A1-29/A1-30 | PostgreSQL 16 `active`, 18 `down`. The laboratory lock has been re-created by `systemd-tmpfiles` from V3 (observed with `ssh oracle-test "stat --format='%n %U:%G %a %F' /run/freedom-blades/laboratory.lock"`) |
| **B6.9** | Reboot-generation cleanup | `⟨MI.producer_argv.reboot_cleanup⟩` | exit 0. Every created object removed, and `R` absent (A1-19). **Residue stops the pass and is preserved** (§10) |

### 7.7 Band B7 — final clean-state survey

The §13.2 survey, in full, after every other band. Then the Pass B handback.

---

## 8. Case-to-requirement matrix

The row numbers are those of the reconciliation handback §3. The classes are:
`feasibility` (required for P5.0-R5 closure under MD-1 … MD-6, produced in this
pass); `production-gate` (writer, admin-tool, coordinator or migration-`0014`
behaviour; carried to the implementation/release gate under MD-1; **not run
here**); `excluded` (by a named decision); `decided` (a design or maintainer
disposition, needing no operational act); `local` (repository-only evidence,
produced in Band A0/B0).

**The division between `feasibility` and `production-gate` is this draft's
proposal. Codex must review it, and it needs the maintainer's acceptance.**
The rule applied: a proposition about a kernel, filesystem, identity,
capability, sandbox or durability mechanism that a harness facsimile can
exercise on `oracle-test` is `feasibility`. A proposition whose subject is the
behaviour of the writer, V-W, C-a … C-f, V-R, `init-generation`, `seal`,
`rotate`, `archive-verify`, the activation trigger or `0014` is
`production-gate`.

**RP-11 blocks every row whose band is a host band** (A1 or B1 … B7) and is
not repeated in each row. Row 40 is `feasibility` under the Codex review
(OP1-R2); it is no longer this draft's proposal to classify it
`production-gate`.

| Row | Proposition (short) | Class | Band / producer | Blocking prerequisite |
|---|---|---|---|---|
| 01 | JNL-01 — the journal path is non-`tmpfs`, block-backed and read-write | feasibility | A1-07 (corroborative); B3 `B4-10`, `B4-11` | RP-1, RP-2, RP-4, RP-8 |
| 02 | §2.13.3 hierarchy owners, modes and flags | feasibility | B3 M-10 … M-23, M-33 … M-37; `B3-19`, `B3-20` | same |
| 03 | the parent is `root:root 0755`; no service identity can rename `…/journal` | feasibility | B4a `JNL-13` parent row | RP-7 |
| 04 | JNL-52 case 2 — `freedomsheet` refusals | feasibility | B3 `B3-25` … `B3-27` | RP-1, RP-2, RP-4, RP-8 |
| 05 | JNL-13 — fifteen manipulation rows under E1, plus the E2 corroboration | feasibility | B4a | RP-7 |
| 06 | the writer cannot rotate, seal, archive or dispose (the `sudoers` drop-in) | production-gate | — | `freedom-journal-admin` does not exist |
| 07 | JNL-33 — full V-W using only the seal read | production-gate | — | — |
| 08 | JNL-27 — Stage-1 controls C-1 … C-6 | feasibility | B3 `B4-12` … `B4-18` | RP-1, RP-2, RP-4, RP-8 |
| 09 | JNL-01/28 — Stage-2 P-1 … P-9; **security check C-3** | feasibility | B3 `B4-19` … `B4-27`. **The 2026-09-05 sentence is not C-3** | same |
| 10 | JNL-28 attribution (`EACCES`/`EROFS`/`EPERM`) | feasibility (producible part); `ENOTTY` stays `local` | B3; A0-06 | same |
| 11 | the created journal's `st_dev` = `PR.probe_device` | production-gate | — | `init-generation` |
| 12 | JNL-48(a)/29 — S4-0 before S4-2 | feasibility | B3 `B4-28` … `B4-31` | same |
| 13 | S4-1/S4-2 — `EROFS` inside the transient unit | feasibility | B3 `B4-32`, `B4-33`; M-43 | same |
| 14 | JNL-48(b) — mis-provisioned target → `inconclusive` | feasibility | B4a | RP-7 |
| 15 | S4-3 — the four security-review conditions | feasibility **if RP-2 permits a facsimile unit**; otherwise production-gate | B3 `B4-34` widened | RP-2 (open question) |
| 16 | the deployed `freedom-sheet-writer.service` hardening | production-gate | — | — |
| 17–19 | construction order C0 … C13; manifest-digest refusals at C0/C2; JNL-31 genesis derivation | production-gate (the model tests stay `local`) | A0-06 covers only the classifier | — |
| 20 | JNL-47 — no generation on failure (S-A ×4) | feasibility | B4a C-7 producer | RP-3 |
| 21 | JNL-47 — recovery (S-B ×2) | feasibility — **RR-14** | B5 | RP-3, RP-6 |
| 22 | JNL-30 — planted residue refused, never cleaned | feasibility — **RR-14** | B5 | RP-6, RP-7 |
| 23 | JNL-48(d) — undeletable artifact → S-B, and recovery | feasibility — **RR-14** | B5 | RP-6, RP-7 |
| 24 | C5 … C11 partial generation → `repair` | production-gate | — | — |
| 25 | JNL-51(a)–(f),(h) — the deploy step's refusals | feasibility — **RR-16** (facsimile deploy step) | B5 | RP-6 |
| 26 | JNL-51(g) — `PVR` omitted; FK refusal | feasibility for the host half (C-7 `JNL-51-PROVENANCE-OMITTED`); **production-gate for the FK half** (`0014`) | B4a, B5 | RP-3, RP-6 |
| 27–31, 33 | writer and coordinator J-26/J-27; C-d sixteen values; F-1 … F-12; `append_only_probe_digest` in `SB` | production-gate | — | — |
| 32 | JNL-40(a) unforged host change | production-gate (W10/C-d) | — | — |
| 32 | **JNL-40(b)** forged `/etc/machine-id` | **excluded — MD-6** | — | `R-5.0-13` stays active |
| 34, 36 | the C-1 … C-4 classifier contradictions | **local** (MD-5 preflight) | A0-06, A1-S1/S2, B0, B1 | A-6 |
| 35, 37 | JNL-32a/b; J-02 torn tail | production-gate | — | — |
| 38, 41, 46, 47, 56 | activation trigger; outcome append; rotation index; restore; generation table | production-gate (`0014`) | — | — |
| 39 | JNL-16 disk-full refuses before dispatch | production-gate. The **mechanism** (loopback `ENOSPC`) is exercised as feasibility inside RR-11 | B5 | RP-6 |
| 40 | JNL-17 `fsync` injection; A-5.0-5(k) | **feasibility — remaining P5.0-R5 work.** The bounded injection mechanism and its facsimile evidence are produced here; the production writer's JNL-17 behaviour is additionally repeated as production-code evidence under MD-1. Deferral needs a new, explicit maintainer disposition naming the residual; none exists | **B4b** | **RP-12**, AUTH-PRODUCERS |
| 42, 43, 45 | JNL-14/15; JNL-02a process `SIGKILL`; JNL-03 restart | production-gate | — | — |
| **44** | **JNL-02b — an unresolved entry survives a supervised host reboot** | **feasibility — mandatory (MD-3)** | **B6** | **RP-5**, AUTH-REBOOT |
| 48 | `archive-verify` | production-gate. RR-11's facsimile rotation re-verifies the archive as feasibility only | — | — |
| 49 | JNL-52 precondition — exact group membership | feasibility | B2 `B2-10` … `B2-15` | RP-1, RP-2, RP-4, RP-8 |
| 50 | JNL-52 cases 1–8 — **security check C-4** | feasibility | B2 `B2-16` … `B2-21`; B3 `B3-21` … `B3-38` | same |
| 51 | E1 … E8 construction | feasibility | B3 `B5-E1` … `B5-E8`, `P-03` … `P-06` | same |
| 52 | launcher bounding set | feasibility | `P-01`. A1-15 is corroborative context about a `sudo`-launched `capsh`, run only under A1-C | same |
| 53 | JNL-49 cases 11/12 (E4/E6, E5) | feasibility | B3 `B5-C6-01` … `11` | same |
| 54 | the remaining 21 JNL-49/JNL-50 cases | feasibility | B4a | RP-7 |
| 55 | control forms C-I/C-II | local | A0-06-adjacent (`test_bands.py`) | — |
| 57 | **security check C-1** — the `freedom-journal-admin` `sudoers` drop-in | production-gate (production host; the drop-in does not exist on `oracle-test`) | — | — |
| 58 | N5.0-23 retain/dispose | decided (OD-63/OD-66) and production-gate | — | — |
| 59–62, 65, 66 | withdrawn sentence; I-SHEET-COMPLETE; residual dispositions; criterion split; PostgreSQL-records statement; register | decided (MD-1, MD-4, design review) | — | — |
| 63 | which host's facts count | decided (MD-2). The facts themselves are feasibility | A1-01 … A1-10, A1-13, A1-16 … A1-18; the twelve harness target facts by `P-05`/`P-06` in B2 against the §4.7 statement. A1-C is corroboration only | RP-1, RP-10, RP-11 |
| 64 | I3/R8 as closure evidence | not applicable | — | — |
| — | **RR-11** (R-5.0-11 recovery) | feasibility — **mandatory (MD-4)** | B5 | RP-6 |
| — | PostgreSQL §2.12.3 peer-map authentication (P5.0-R4 support) | inside the harness plan. **Recorded, but not P5.0-R5 closure evidence** | B4 (`B6-01` … `B6-08`) | AUTH-DB |

---

## 9. Outputs, locations, ownership and evidence-manifest fields

### 9.1 Where evidence lives

| Artifact | Location | Owner / mode | Retained? |
|---|---|---|---|
| Per-act capture records, stream files and capture index states (**the primary evidence** for every operator-issued command), each admitted only once its §9.5.1/§9.5.2 barriers have succeeded and it is covered by the durable final index state | the pass's own capture root on the **repository host**, as §9.5 fixes: `⟨MI.capture_root_A⟩` for Pass A and `⟨MI.capture_root_B⟩` for Pass B, each with its own genesis state, index chain and final state. **Nothing on `oracle-test`** | the operator's repository-host account; directory `0700`, files `0600` | yes, unmodified, until the post-execution review and a maintainer disposition (§9.5, C-8). Pass A's root stays retained and unmodified, and is never used as Pass B evidence, while Pass B is admitted and executed; it is never removed, renamed, reused or modified to make Pass B's root absent. Pass B reads it only in B0-RA's non-mutating retention verification (§7.1), which must succeed before Pass B's root is created. Never committed. Unadmitted files (C-15) are retained and reported in the same way, by exact relative name and object type, never completed or removed. B0-RA verifies their presence, name and type, not their content |
| Client transcript | the operating session | — | a convenience only. It is merged and may be truncated, so it is **not evidence** and is never the source of a digest |
| Pass A handback | `docs/review/phase-5-0-p5-r5-op1-a-preflight-handback.md` | repository | yes |
| Pass B handback | `docs/review/phase-5-0-p5-r5-op1-b-feasibility-evidence-handback.md` | repository | yes |
| Harness run record | `⟨MI.run_record_path⟩`. Written only if `artifact eligible: True`, then read back and validated by `artifact.write_run_record` | root-written. Mode per `artifact.py` | yes. Retrieved into the handback by the authorized read `ssh oracle-test "sudo cat ⟨MI.run_record_path⟩"` |
| C-7 classified artifact | `⟨RP-3.artifact_path⟩` via `evidence_cli --artifact-out` | per `evidence_cli` | yes |
| Run ledger and reservation entries | V9 `/var/lib/freedom-blades/laboratory/runs` (`root:freedomlab 3770`) and V4 | written only by the harness participant protocol | yes. **Never edited or removed by the operator** |
| Independent recovery store (pre-change `pg_hba.conf`/`pg_ident.conf` captures) | V5 `/var/lib/freedom-blades/recovery` (`root:root 0700`) | harness | retained per cleanup's `retained inputs` line |
| `sudo` log output, journald | system locations | system | external evidence for R-5.0-12, R-5.0-13 and R-5.0-15. **Never truncated** |

### 9.2 The disposable hierarchy the harness creates (expected ownership and modes)

| Object | Expected |
|---|---|
| `R` = `/var/lib/fb-evidence-p5-0` | created exclusively by `B3-01` (`mkdir`), not by the operator |
| `R/journal` | `root:freedomjournal 0750` |
| `R/journal/000001.journal` | `freedomsheet:freedomcoord 0640`, `+a` |
| `R/journal/000001.seal` | `root:freedomjournal 0440`, `+i` |
| `R/journal/current` | symlink → `000001.journal` |
| `R/archive` | `root:freedomcoord 0750`; archived files `0440`, `+i` |
| `R/probe` | `root:freedomsheet 0770` |
| `R/probe-ro` | outside the substituted `ReadWritePaths=` |
| `R/bin/case` | the byte-for-byte install of `case_program.py` (`PIN.case_program_py`) |
| `fb_evidence_p5_0`, role `freedom_migration_coordinator` | disposable. The role is `PASSWORD NULL` |

**Every one of these is removed by derived cleanup.** Their expected absence is
surveyed in §13.2.

### 9.3 Evidence-manifest fields — one record per case or act

`pass_id` (`C-P5.0-R5-OP1-A` or `-B`); `evidence_class`
(`feasibility-facsimile`); `band`; `step_or_case_id`; `requirement` (the §8 row
and JNL/RR identifier); `decision_basis` (MD-n); `producer` (the harness step
id, or the RP producer name and source digest); `argv` (exact); `run_as`;
`host`; `target_identity`; `confirmation_token`; `manifest_version`;
`reviewed_digest`; `boot_id`; `started_utc` and `ended_utc` (client clock);
`exit_status`; `stdout_sha256` and `stderr_sha256` plus a safe excerpt;
`expected`; `observed`; `classification` (`passed` | `failed` | `inconclusive`
| `not_run`); `not_run_reason`; `residue` (absolute paths, or `none`);
`deviation` (or `none`); `refusal` (or `none`); `operator`;
`independent_review_inputs`; and, for every operator-issued command,
`capture_seq` and `capture_record_sha256` (§9.5).

`argv`, `started_utc`, `ended_utc`, `exit_status`, `stdout_sha256` and
`stderr_sha256` are **taken from the RP-11 capture record and from nothing
else**, and only from a record that was durably published under §9.5.1 and is
listed in the pass's durable final capture index state (§9.5.2). A field the
capture record does not supply, or a record that is not so published and
listed, is not filled from the transcript or from memory; the act is
`inconclusive`. **Until RP-11 is met — reviewed, accepted, pinned and wired
— these fields cannot be produced, so neither pass is executable.**

### 9.4 Inputs for independent review

Codex reviews: the handback; the safe excerpts drawn from the capture records; the run record and C-7
artifact (with their digests); the reproduced manifest digest; the
target-identity table from Pass A and from B6.6; the B6.1b-versus-B6.7
comparison table; the RR-11/14/16 refusal-then-recovery sequences; the B4b
`fsync`-injection records; the §13.2 survey; for each pass separately, its
capture root, the outcome of its X-3 finalization attempt (§9.5.3), its final
capture index state and digest and every earlier index state of its own chain
(§9.5.2), with access to that root's retained capture records, stream files
and any unadmitted files (C-15); for Pass B, the B0-RA retention-verification
result against the Pass A handback, with its outcome for each of its five
conditions (§7.1), including each direction of the condition-5 name-set
comparison and every name in either set difference, or `none` for each; and
every deviation, warning, skip and refusal. For an unadmitted object, B0-RA's
result is evidence of presence, relative name and object type only, not of
unchanged content.

### 9.5 Client-side capture contract — RP-11 (**unmet: no reviewed mechanism exists**)

This section states what RP-11 must provide. It is a requirement, not a
design: this draft specifies no code and names no tool. **Until a mechanism
meeting every item has been implemented in a separately assigned pass,
independently reviewed and pinned (`PIN.capture_tool_sha256`), neither pass is
executable.**

The retained stream files, per-act records and capture index are the pass's
**primary evidence**, so each must survive a crash or restart of the
repository host exactly as published, or be demonstrably absent. C-13 … C-15
state the crash-consistent publication contract that makes that true. They
name the required durability semantics. **One exception, proposed by
C-P5.0-R5-RP11-I1-R3 in place of the I1-R1 route:** the publication route of
P-5 … P-8 is named here exactly — an exclusively created staging name, one
non-replacing, no-follow, descriptor-relative hard link of the same inode to
the final name, and retention of both names as an indexed pair (§9.5.1) —
because the retained alias it leaves is part of what X-4 and B0-RA verify, and
because its capability is tested by the pass's first real publication
(§9.5.4). **Every other interface, and the evidence that the barriers hold on
the filesystem holding each pass's capture root, remain RP-11's
implementation-and-review obligation.** Nothing in this section claims RP-11 is satisfied.

Throughout §9.5, **the pass's capture root** means `⟨MI.capture_root_A⟩` for
every act of Pass A and `⟨MI.capture_root_B⟩` for every act of Pass B (§4.5).
Each pass has exactly one capture root, one genesis state, one index chain,
one final state and one handback binding, all its own. Nothing of one pass is
written, listed or chained under the other pass's root. Pass B's only access
to Pass A's root is B0-RA's read-only retention verification (§7.1): it lists
names and object types, reads bytes and re-derives digests there, writes
nothing there, and uses nothing there as Pass B evidence. Every name a record
or index state carries, and every name a handback reports for that pass's
capture, is the object's exact relative name under that pass's capture root.

| # | Requirement |
|---|---|
| C-1 | **Exact argv.** The mechanism records, before execution, the exact command text as issued **and** the argv vector the executed client process received, so the record states exactly what ran. If the reviewed invocation passes through a client-side shell (the §5 command's single-quoted exclusions are shell syntax), the contract says so and records both forms. The remote command string for `ssh` is one argv element and is recorded byte for byte |
| C-2 | **Separate, complete streams.** stdout and stderr are read through separate channels to end-of-file and written to two separate client-side files, each created exclusively under a name unique to its `capture_seq` and never reused. Nothing is merged, interleaved or truncated. A stream is **complete** only when the executed client process has ended, its channel has reached end-of-file and its file has been **closed to further writing**. No record is written for publication before both streams are complete and have passed their file and directory barriers (§9.5.1 P-2, P-3). A declared maximum size per stream is part of the reviewed contract; exceeding it makes the act `inconclusive` and stops the pass rather than truncating |
| C-3 | **Digests.** `stdout_sha256` and `stderr_sha256` are computed over exactly the bytes of the completed stream file, and can be re-derived from the retained files. A digest is **published**, in a record, only after that stream file's file barrier and directory barrier have succeeded (§9.5.1). An empty stream is still a stream file, passes the same barriers, and has the digest of the empty string, recorded as such |
| C-4 | **Time and status.** `started_utc` and `ended_utc` come from the client clock in `YYYY-MM-DDTHH:MM:SS.ffffffZ` form, with the clock source named; `exit_status` is the exact code, or the terminating signal |
| C-5 | **One record per act.** Each act produces at most one published record carrying `pass_id`, `capture_seq` (strictly increasing from 1, no gaps), `step_or_case_id`, argv, the four C-3/C-4 values, and the **exact relative names (under the pass's capture root) and SHA-256 digests of its two already-durable stream files**. It is published by the ordered sequence P-1 … P-8 of §9.5.1, and the pass-level **capture index** is advanced under §9.5.2, before the next act starts. The capture index lists every admitted record's SHA-256 in `capture_seq` order. **A record is durable only when P-1 … P-8 have all succeeded, and admitted only when the next durable index state records both of its names and their shared inode (§9.5.2 X-2)**; a record whose staging name exists but whose final link was refused, reported as failed or not confirmed, or whose content check, file barrier, containing-directory barrier or pair verification did not succeed, or that no durable index state admits, is not evidence. Its names are retained, unadmitted (C-15) |
| C-6 | **Location — one distinct root per pass.** Everything a pass captures is under **that pass's own capture root** on the repository host: `⟨MI.capture_root_A⟩` for Pass A only, `⟨MI.capture_root_B⟩` for Pass B only. The two are distinct absolute paths, and neither lies within the other. **Each independently** is outside the Git worktree (A0-02 must stay empty) and outside `/tmp`, on a filesystem RP-11's review has accepted (§4.5), and **absent before its own pass**; the mechanism creates it exclusively in that pass's X-1 (A0-08 for Pass A, B0-08 for Pass B). Its creation, and the creation of any subdirectory the mechanism makes, is made durable by a successful directory barrier on the directory that contains it, before that pass's genesis index state is published (§9.5.2 X-1). Pass A's root is never removed, renamed, reused or modified to make Pass B's root absent (C-8). This draft names no common parent directory. If the two roots have one, it already exists, is not created, cleaned up or otherwise written by the mechanism or the operator beyond each root's own entry, and holds no capture file itself; each root is still separately and exclusively created and independently durable. **No file is created on `oracle-test`**: the remote command never redirects, tees or writes a capture |
| C-7 | **Ownership and mode; immutability.** Owned by the operator's repository-host account; the directory `0700`, every file `0600`. Stream files, records and index states are never modified, truncated, appended to, renamed or replaced after publication, and a published name is never reused. A file whose barrier failed is never afterwards published, and a staging name, or a staging/final pair, that no durable index state admits is unadmitted (C-15). **Each record and index state is exactly one inode with exactly two names — its staging name and its final name — and that pair is the only permitted hard-link alias** (§9.5.1). Neither name is ever unlinked, renamed, repaired or cleaned up, and no third name is ever given to it |
| C-8 | **Retention.** Stream files, records, every index state and every unadmitted file (C-15) are retained unmodified until Codex's post-execution review and a maintainer disposition. Removal needs a later explicit maintainer decision. They are **never committed**: raw streams may carry host facts beyond what the handback may publish. In particular, `⟨MI.capture_root_A⟩` and everything under it stay retained and unmodified, and are never used as Pass B evidence, while Pass B is admitted and executed. Pass B's admission never depends on removing, renaming, reusing or modifying it. It depends instead on **B0-RA** (§7.1), which verifies read-only, before Pass B's X-1 and before any Pass B host command, that the root and the final index state the Pass A handback names still exist, that the final state's re-derived SHA-256 equals the handback's capture index SHA-256, that X-4 still holds for Pass A's retained chain, records and bound stream files, and that the complete recursive set of relative names under the root and the set Pass A's final state accounts for agree in both directions, with matching object types — so that an absent unadmitted file, like an absent record, stops Pass B. B0-RA only lists names and object types, reads bytes and re-derives digests; any failure is a fail-closed B0 stop. **Retention of an unadmitted file is required, but only its presence, relative name and object type are verified.** It has no recorded digest, so its unchanged content is not verified, and it is never digested afterwards to make it evidence: a file whose durability barrier failed is not promoted into evidence by hashing it later. B0-RA establishes retention at the moment of the check only, and is not a monitor or a guarantee against a later change |
| C-9 | **Redaction boundary.** Raw stream files are the sealed record and are not published. The handback carries only argv, times, exit status, digests, `capture_seq`, record digests and **safe excerpts** chosen under §12: no contents of `pg_hba.conf`, `pg_ident.conf` or `/etc/machine-id`, no process argument vectors, no environment and no secret. If a stream unexpectedly contains a credential or secret-bearing value, the operator stops, does not reproduce it anywhere, and notifies the maintainer (AGENTS.md "Configuration and secrets") |
| C-10 | **Failure behaviour.** If the mechanism cannot start the command; capture either stream in full or close it; compute a digest; complete a record; or obtain the success of **any file barrier or directory barrier** of §9.5.1 or §9.5.2 — on a stream file, a record, an index state, the capture root or a subdirectory — the act is `inconclusive` and the pass **stops** under §11.2. A failed barrier is **not retried**, and a later successful synchronization does not cure it: after a reported failure the stable state of the affected file or entry is unknown. The act is never rewritten, repaired, completed, linked or renamed into place, re-linked or reissued, no staging or final name is removed, and no record is published for it. If the remote command may have run but its evidence was not durably published, that is reported explicitly as a host act without admissible evidence. The stop transition of §9.5.3 then applies, in its order: command execution stops at once and no host command is issued, retried or reissued; if the capture mechanism and the repository host remain available, the **only** permitted write is one X-3 finalization attempt (§9.5.2), which records the stop; and the pass's capture root is read-only once that attempt reaches its outcome, or at once after an interruption (C-15) |
| C-11 | **Guards.** The mechanism's invocation is reviewed against `guard-secrets.py` and `guard-git.py`. It must not become a way to issue a command a guard would refuse if issued directly — in particular it must not hide the §5 `rsync` from the secrets guard. Any refusal is a §11.1 stop, never a reason to reshape the invocation |
| C-12 | **Binding in the handback.** Every measured-fact row names its `capture_seq` and `capture_record_sha256`, and that record must be listed in the pass's durable, valid final index state (§9.5.2 X-4). Each pass's handback states **its own** capture root (`⟨MI.capture_root_A⟩` in the Pass A handback, `⟨MI.capture_root_B⟩` in the Pass B handback), the outcome of its X-3 finalization attempt (§9.5.3), its final index state's name and SHA-256 (the **capture index SHA-256**), its terminal status, its X-4 validity, every subdirectory the mechanism created under its capture root, and every unadmitted file (C-15) by exact relative name and object type, or `none`, as its final state records them. The Pass A handback states its capture root exactly, byte for byte, because B0-RA verifies `⟨MI.capture_root_A⟩`, the final state's name and the capture index SHA-256 against those recorded values; a Pass A handback that records no admissible final state gives B0-RA nothing to verify, and Pass B is not admitted. The capture root, the X-3 outcome, the X-4 validity, the final state's name and the capture index SHA-256 are stated **in the one fixed `rp11-capture-binding/1` block of §14**, which is the only part of a handback B0-RA parses; the prose lines repeat them for the reader and are never parsed. A Pass B row is never bound to a record under Pass A's root, or the reverse. A row without such a record is not a measured fact |
| C-13 | **Crash-consistent publication of streams and records.** Every act follows the ordered sequence P-1 … P-8 of §9.5.1: durable stream files first; then a complete record under an exclusively created staging name in its destination directory, checked for size and digest; then that inode's file barrier; then publication by one exclusive final link of the same inode that replaces nothing; then the containing-directory barrier; then verification of both names. A publication has succeeded only when that verification has succeeded, and the record is admitted only by the next durable index state. The next act does not begin until P-8 and the index advance (§9.5.2 X-2) have succeeded |
| C-14 | **Crash-consistent capture index.** One capture index per pass, under that pass's own capture root, created, advanced and finalized by X-1 … X-4 of §9.5.2 as a chain of separate, immutable index states, each published by the same retained-alias sequence: staging name, content check, file barrier, exclusive final link, directory barrier, verification of both names. Each state is admitted by its successor's record of its pair; *F* records its own. No published record is modified to maintain it. Pass B's chain begins at its own genesis state; it never continues, reuses or references Pass A's chain, and there is no index shared by the two passes. The final index state has one defined finalization point, and its SHA-256 is the digest the handback states |
| C-15 | **Interruption and unadmitted files.** A crash, power loss or restart of the repository host, or termination of the mechanism, during a pass is a capture failure and ends it. No X-3 finalization attempt is made after recovery, and X-4 applies directly (§9.5.3). Files that are not admitted evidence are retained and reported, never completed or adopted (§9.5.3) |

#### 9.5.1 Publication sequence for each act (C-13)

Terms, stated as required semantics, not as interfaces:

* **File barrier** — a completed, closed file's data, and the metadata needed
  to read those bytes back, are flushed from every buffer the mechanism
  controls and synchronized to stable storage, and the synchronization reports
  success.
* **Directory barrier** — after an entry is created in a directory (including
  by the exclusive final link of P-7),
  that containing directory is synchronized to stable storage, and the
  synchronization reports success, so that the entry itself survives a crash.
* **Staging name** — one deterministic, object-specific name in the directory
  that will hold the published file, derived by a fixed rule only from the
  already-bound record or index identity: the final name followed by
  `.staging` (for example `records/000007.json.staging`). It is one path
  component, ASCII and byte-safe, and it is never the final name of any object.
  It is created **exclusively**, relative to the destination directory's
  descriptor, with `O_CREAT | O_EXCL | O_WRONLY | O_NOFOLLOW | O_CLOEXEC` and
  mode `0600`. **An occupied staging name refuses**: it is not read, removed,
  replaced or recorded as the mechanism's object, and it is a capture failure
  (C-10). Once published it is **not a temporary**: it is the retained staging
  alias of the object.
* **Exclusive final link (atomic publication)** — **exactly one** call of the
  package's shared, descriptor-relative, **no-follow** exclusive-link primitive,
  from the staging name to the final name in the same directory. It either
  gives the already-synchronized inode its final name or creates nothing, and it
  **never replaces an existing entry**: an occupied final name is refused by
  the kernel (`EEXIST`), which is the only non-replacement check — the final
  name is **not** pre-checked in its place — and that refusal is a capture
  failure, never an overwrite. **A final-name occupant is not the mechanism's
  object** and is never recorded as one. No rename, no replacing call, no
  followed source, no `O_TMPFILE`, no `/proc/self/fd` and no second link to the
  same inode is part of this route.
* **Retained alias pair** — after publication the object is **one inode with
  exactly two names, link count two**: its staging name and its final name.
  **Neither name is ever unlinked, renamed, repaired, adopted or cleaned up** by
  the mechanism or the operator. Both names, their roles and the shared inode
  identity (`st_dev`, `st_ino`) are recorded in the next durable index state
  (§9.5.2), and only that state admits the object. This pair is the **only**
  permitted hard-link alias under a capture root; X-4 and B0-RA refuse every
  other (§9.5.2 X-4, §7.1).
* **One shared link call site, two reviewed no-follow contracts.** The
  package's single `os.link` call site (`descriptors._exclusive_link`) always
  links a **name** relative to a directory descriptor with no-follow semantics;
  it takes no follow argument. It serves exactly two callers: **(i)** the
  existing I3 named-source caller, `PosixFilesystem.linkat`, whose behaviour,
  flags and guarantee are those Codex previously reviewed for I3 and are
  unchanged; and **(ii)** RP-11's `link_named_exclusive`, which links one
  component to another relative to the capture root's directory descriptors.
  **The I1-R1 contract amendment that gave RP-11 a follow-semantics caller
  through `/proc/self/fd` is withdrawn**, with that caller
  (`descriptors.EXCLUSIVE_LINK_PRIMITIVE`; see the I1-R3 handback for the exact
  source and tests).
* **Platform prerequisites of this route.** A capture-root filesystem that
  supports hard links within one directory and the file and directory barriers
  RP-11's review accepts, and an execution context that permits a no-follow,
  descriptor-relative `linkat` of a file the operator's account owns. **No
  procfs, no `O_TMPFILE` support and no followed link is required.** Neither
  prerequisite is assumed: the pass's own X-1 genesis publication tests them,
  fail-closed, before any host command (§9.5.4).

For act *n* (`capture_seq` = *n*), in this order, each step only after the
previous one has succeeded:

| Step | Requirement |
|---|---|
| P-1 | **Execute and capture.** The command runs; stdout and stderr are read through separate channels into their two stream files (C-2); the C-1 and C-4 values are recorded |
| P-2 | **Complete and synchronize the streams.** After the client process has ended and both channels have reached end-of-file, each stream file is closed to further writing and receives a file barrier |
| P-3 | **Make the stream entries durable.** Each directory that holds a stream file of act *n* receives a directory barrier |
| P-4 | **Digest.** `stdout_sha256` and `stderr_sha256` are computed over the completed files (C-3) |
| P-5 | **Complete record under its staging name.** The staging name is created exclusively (see *Staging name*); the bound inode is verified as a regular file owned by the operator's account, with exact mode `0600`, link count one, on the capture root's device. The whole record (C-5), binding the exact names and digests of the two stream files that P-2 and P-3 made durable, is written with a **checked loop** that either writes every byte or fails. The staging name is then reopened no-follow and read-only, and must be the bound inode with the exact size and SHA-256 of the record: a partial, zero-length or falsely reported write fails here |
| P-6 | **Record file barrier.** The bound inode receives a file barrier while only its staging name exists |
| P-7 | **Atomic publication.** Exactly one exclusive final link gives the same inode its final name, unique to *n*. It replaces nothing |
| P-8 | **Containing-directory barrier, then verification.** The directory holding both names receives a directory barrier. Then **both names** are opened no-follow and read-only and each must be the bound inode: regular, operator-owned, mode `0600`, on the expected device, link count two, with the record's exact size and SHA-256. The descriptor is then closed. **The publication has succeeded only when this verification has succeeded**; the record is **admitted** only when the next durable index state records both of its names and their shared inode (§9.5.2 X-2) |

Then the capture index is advanced (§9.5.2 X-2), and only after that has
succeeded may act *n* + 1 begin. **A failure at any step is an `inconclusive`
stop under C-10.** A stream file whose P-2 or P-3 barrier failed is never bound
by a record. A record whose P-5 content check, P-6 barrier, P-7 link, P-8
barrier or P-8 verification did not succeed is not durable and is never
admitted, even if both of its names later appear present and correct.

**Publication states, which apply equally to every index state (§9.5.2).** A
publication is always in exactly one of these states, and the mechanism fails
closed in each:

| State | Names that exist | Meaning |
|---|---|---|
| no staging entry | none | the P-5 creation failed before an entry existed, or refused an occupied staging name. Nothing is the mechanism's, and nothing is recorded as unadmitted |
| staging without a confirmed final link | the staging name | P-5's verification, write or content check, P-6, or the P-7 link failed or was refused (`EEXIST`). The staging name is unadmitted |
| both names before the directory barrier | staging and final | the P-7 link was confirmed — by its success, or, where it was reported as failed, by one no-follow inspection showing the bound inode at the final name — but P-8's barrier did not succeed. Both are unadmitted |
| both names after the barrier, unverified | staging and final | P-8's barrier succeeded but its verification of both names did not. Both are unadmitted |
| both names verified, not index-admitted | staging and final | the publication succeeded, but no durable index state records it yet. Both are unadmitted |
| both names admitted | staging and final | a durable index state records both names, their roles and the shared inode. Only this state is evidence |

**Before admission, every staging name and every staging/final pair is
unadmitted.** It is retained unmodified and reported by exact relative name and
object type, and it is **never** completed, linked, re-linked, adopted,
repaired, digested to make it evidence, admitted later or used as evidence. A
failed or unconfirmed barrier is **never** retried, repeated or cured by a
later synchronization. A final-name occupant that was not the mechanism's is
never recorded as the mechanism's object; B0-RA later finds it unaccounted and
stops, which is the fail-closed direction. **Every** failure is an
`inconclusive` stop under C-10: no retry of any step, no repair, no clean-up,
no republication under this or another name, and no further command. The
§9.5.3 stop transition follows. After an interruption of the mechanism or the
repository host, any later discovery of these names is read-only and no X-3
attempt is made (C-15).

#### 9.5.2 Capture index — creation, advance and finalization (C-14)

Each pass has its own capture index: a chain of **index states**. Each state
is a separate file under the pass's capture root, named uniquely by a fixed
rule from its state number, published once by the same retained-alias
sequence as P-5 … P-8 (staging name → content check → file barrier → exclusive
final link → directory barrier → verification of both names), with the same
publication states (§9.5.1), and never modified, replaced or renamed
afterwards, with neither of its names ever removed (C-7). Each state carries
`pass_id`, the pass's capture root (`⟨MI.capture_root_A⟩` or
`⟨MI.capture_root_B⟩`), `PIN.capture_tool_sha256`, the operator account's
numeric owner (`owner_uid`), its own state number, a **predecessor link** (none
for the genesis state) giving the preceding state's final name, staging name,
SHA-256 and shared inode (`st_dev`, `st_ino`), a status (`open` or `final`) and
the ordered list of admitted records — for each, its `capture_seq`, final name,
staging name, SHA-256 and shared inode — complete, strictly increasing from 1
and gap-free, as C-5 and C-12 require. **The predecessor link is what admits
the preceding state; a record's entry is what admits the record.** *F*, which
has no successor, additionally records **its own pair**: its final name,
staging name and shared inode — known before a byte of it is written, because
its staging name is created first — and never its own digest.

| Step | Requirement |
|---|---|
| X-1 | **Create.** After the pass's admission check (A0-08 for Pass A; for Pass B, B0-RA's successful retention verification of Pass A's root and then B0-08), and **before the pass's first host command**, the mechanism creates the pass's capture root exclusively (C-6) and publishes that pass's genesis state *I*-0 (`open`, no records) by the §9.5.1 sequence. **This first real publication is the pass's fail-closed capability test (§9.5.4).** *I*-0 is durable when both of its names have been verified; it is admitted later, by its successor. A failure is an `inconclusive` stop before any host act; with no durable *I*-0, there is no chain to finalize, no X-3 attempt is made (§9.5.3), no final state can satisfy X-4, and none is constructed to make it do so. Whatever X-1 created is retained and reported by exact relative name |
| X-2 | **Advance.** After act *n*'s P-8 has succeeded, the mechanism publishes state *I*-*n* (`open`), listing records 1 … *n* — record *n* with both of its names and its shared inode — and carrying the predecessor link to *I*-(*n* − 1). Act *n* + 1 does not begin until both of *I*-*n*'s names have been verified. Only then are record *n* and *I*-(*n* − 1) **admitted**. If *I*-*n* cannot be published durably, record *n* is **not admitted** and its names are retained as unadmitted, and the pass stops under C-10 |
| X-3 | **Finalize — one attempt.** When the pass ends — completed, or stopped for any reason, including a §11.1 refusal, a §11.2 stop or a C-10 capture failure — the mechanism makes **exactly one finalization attempt**, where the stop transition of §9.5.3 permits one. The attempt publishes one final state *F* (`final`) by the §9.5.1 retained-alias sequence. *F* lists exactly the records of the last durable open state, carries the predecessor link to that state (which admits it) and *F*'s own pair, a terminal status (`completed`, or `stopped` with the `capture_seq`, step and reason of the stop), the relative name of every subdirectory the mechanism created under the capture root (C-6), and every unadmitted file it knows of (C-15) — including every staging name and every staging/final name that no durable state admits — each by its **exact relative name under the capture root and its object type**, recorded as stated facts and not left to be inferred. *F* records no content digest for an unadmitted file, and none is computed for it later. The attempt is a local repository-host act and, after a stop, the **only** permitted write: it issues no host command, creates nothing but *F*'s two names (its staging name and, through the one exclusive final link, its final name), does not write, rename, move or remove any stream file, per-act record, earlier index state, staging name or unadmitted file, and is neither a retry nor a repair. **The finalization point is the successful verification of both of *F*'s names after the directory barrier that follows *F*'s exclusive final link**; reaching it is the attempt's success. A step of the attempt that does not succeed, including a failed or unconfirmed barrier, is the attempt's failure, which is not retried or cured. **When the attempt reaches either outcome, the pass's capture root becomes read-only (§9.5.3).** No attempt is made after an interruption of the capture mechanism or repository host (C-15). **The capture index SHA-256 stated in the handback is the SHA-256 of *F*** |
| X-4 | **Validity.** *F* is admissible only if: it exists under its final name and its barriers succeeded; it is the only final state; its chain of preceding-state digests is intact back to the same pass's *I*-0; its record list is gap-free from 1 and equals that of the last durable open state; every listed record exists with the listed digest, and every stream file each record binds exists with the bound digest; every published record under the pass's capture root is either listed in *F* or named in it as unadmitted; and **every admitted record and index state, *F* included, is exactly its recorded pair**: both names present, regular, one inode equal to the `st_dev` and `st_ino` its admitting state records, owned by the recorded `owner_uid`, mode `0600`, link count two, and — read through the final name — the recorded size and digest. **The one alias exception** is that pair, and — for a staging/final pair *F* records as unadmitted — the two recorded names sharing one inode at link count two, checked by metadata only (accepted Option 1, `C-P5.0-R5-RP11-I1-R3-D2`; [decision record](project-review-2026-09-28-p5-r5-rp11-i1-r3-r2-and-unadmitted-pair-decision.md)). A missing pair member, an identity or type that differs from the record, a wrong link count, a third link, a cross-object alias, a name in two pairs or categories, a duplicate or ambiguous encoding or any unexpected name reaching an accounted inode makes *F* inadmissible. **A missing, stale, non-durable or internally inconsistent final index state is an `inconclusive` stop**: no row of that pass is a measured fact, and *F* is **never** written, completed or reconstructed afterwards — not from the transcript, from memory, from the intermediate states or by hand. A failed X-3 attempt is not repeated, and the resulting final state is not repaired or completed. **Pass B's B0-RA re-applies this check to Pass A's retained evidence** (§7.1): read-only, before Pass B's X-1, with the barrier-success condition taken from the Pass A handback rather than re-observed. B0-RA adds a bidirectional comparison (B0-RA condition 5): every name observed anywhere under Pass A's root must be accounted for by Pass A's *F*, and every name *F* accounts for — including every unadmitted name — must be present at its exact relative name with its expected object type. Neither X-4 nor B0-RA establishes the content of an unadmitted file: it has no recorded digest, so only its presence, relative name and object type can be verified. That re-application is verification only; it never writes, completes, repairs, adopts or reconstructs anything, and a failure stops Pass B at B0 |

#### 9.5.3 Interruption, stops and unadmitted files (C-15)

* **Repository-host interruption.** A crash, power loss or restart of the
  repository host, or termination of the capture mechanism, during a pass ends
  the pass as a capture failure. The act in progress is `inconclusive`; if its
  remote command may have run, it is reported as a host act without admissible
  evidence. No further host command is issued and the pass is not resumed.
  **No X-3 finalization attempt is made, including after recovery**, and the
  pass's capture root is read-only from the interruption (step 5 below). If
  X-3 had not reached its finalization point, there is no admissible final
  index state, and X-4 applies directly.
* **The B6 reboot is not such an interruption.** It restarts `oracle-test`,
  not the repository host, and every B6 command — including B6.4, whose remote
  session may close — completes P-1 … P-8 and X-2 before the next one is
  issued.
* **Unadmitted files.** Any file under the pass's capture root that is a
  stream file not bound by an admitted record, a record not admitted under
  X-2, an index state outside *F*'s chain, a staging name or a staging/final
  pair of any publication that no durable index state admits — whichever
  §9.5.1 state it stopped in — or a name left by a failed X-3 attempt is
  **unadmitted**. A publication whose P-5 creation failed before any entry
  existed, or refused an occupied staging name, left no object of the
  mechanism's and nothing is recorded for it. An unadmitted object is retained
  unmodified (C-8),
  recorded in *F* and reported in the handback by its exact relative name and
  object type (X-3, C-12), and never completed, renamed, deleted, adopted,
  digested to make it evidence, or used as evidence. B0-RA later verifies its
  presence, name and type, not its content (§7.1).

**Stop transition — one order, for every stop.** When a pass stops — on a
§11.1 refusal, a §11.2 stop or a C-10 capture failure — the following apply in
this order. C-10, C-15, X-3, X-4, §10 and §11 all refer to this transition and
none of them states a different one.

1. **Stop further commands.** Command execution stops immediately. After the
   stop no host command is issued, retried or reissued, not even a read-only
   one, and the failed act is not completed, repaired or re-run.
2. **One local X-3 finalization attempt, only where possible.** If the capture
   mechanism and the repository host both remain available and the pass has a
   durable genesis state *I*-0, the mechanism makes **one** X-3 finalization
   attempt (§9.5.2). It is the **only** write permitted under the pass's
   capture root after the failure or refusal. It creates only *F*'s staging
   and final names, alters or removes no stream file, per-act record, earlier
   index state, staging name or unadmitted file, issues no host command, and
   is not a retry or a repair. It may **account** for names already known to
   have been created; it never completes, links or repairs a publication.
3. **One outcome.** The attempt **succeeds** when it reaches the X-3
   finalization point: the successful verification of both of *F*'s names
   after the directory barrier that follows *F*'s exclusive final link. It **fails** at the first of its steps that does not succeed,
   including a failed or unconfirmed file or directory barrier, or an
   interruption during the attempt. A failed attempt, including a failed
   finalization barrier, is not retried or cured, and the resulting final
   state is not repaired, completed or reconstructed; X-4 then decides
   admissibility.
4. **Read-only state — a behavioural terminal seal.** The pass's capture root
   becomes read-only when the attempt reaches either outcome. *Read-only* in
   this contract means a **behavioural terminal seal**, and nothing more: the
   mechanism enters a terminal state, releases every file and directory
   descriptor it holds, and from then on **every writing operation it offers
   refuses** without touching the filesystem. **No `chmod` or other permission
   change is performed**, so the C-7 modes (`0700`, `0600`) are unchanged. **The
   seal is not operating-system write protection.** It does not stop another
   process of the operator's account, or root, from writing under the root; it
   relies on the operator's conduct under this prompt and on the repository
   host's access boundary, under which the `0700` root is writable only by the
   operator's account and by root. From then on the operator may only list
   names and re-derive digests under it for the handback and the review.
   Nothing there is written, moved or removed, and the stop is not repaired.
   A later change by anyone would not be prevented by the seal; B0-RA's check
   (§7.1) is what detects, at the moment of that check, the changes it can.
5. **No attempt after an interruption.** If the capture mechanism or the
   repository host was interrupted (C-15), no X-3 attempt is possible, before
   or after recovery. The capture root is read-only from the interruption, and
   X-4 applies directly: without an admissible *F*, the pass's capture evidence
   is `inconclusive`. Likewise, if X-1 did not durably publish *I*-0, there is
   no chain to finalize, no attempt is made, and the root, if it was created,
   is read-only from that failure.

When a pass **completes** without a stop, steps 2 to 4 apply in the same way:
one X-3 attempt, one outcome, then the read-only state.

For Pass B, the whole transition acts only on `⟨MI.capture_root_B⟩`. Pass A's
root is already read-only from the end of Pass A and is never written, even by
Pass B's X-3 attempt. A B0-RA stop precedes Pass B's X-1: no
`⟨MI.capture_root_B⟩` exists, so there is no *I*-0, no X-3 attempt and
nothing to make read-only, and no host command has been issued.

#### 9.5.4 Capability test — the first real X-1 publication (C-P5.0-R5-RP11-I1-R3)

**There is no separate mutating publication probe.** The I1-R1 pre-admission
capability check, its probe directories (`MI.publication_probe_directory_A`
and `_B`) and its clean-up are withdrawn. Each pass's **first real
publication — its X-1 genesis state, published by the exact §9.5.1 sequence
before any host command** — is the fail-closed test that the route works in
that mechanism process, on that capture root's filesystem, at that moment.

* **Success** is the X-1 genesis publication reaching verification of both of
  its names. Only then may the pass's first host command be issued.
* **Failure** of any step — the root or a subdirectory not created or not
  made durable; the staging name refused or not verified; the write or its
  content check; the file barrier; the exclusive final link refused, reported
  as failed or not confirmed; the directory barrier; or the verification of
  both names — is an `inconclusive` stop of that pass **before any host
  command**, with exactly the bounded, classified residue and stop semantics
  of every later publication (§9.5.1, §9.5.3): no durable *I*-0, so no X-3
  attempt; whatever X-1 created is retained unmodified and reported in the
  pass handback by exact relative name and object type as an admission result,
  never removed, completed, linked or repaired; and **nothing is retried**, in
  that process or another, with another location or with a weaker rule. Any
  different mechanism needs a new requirements proposal and independent review.
* **What it establishes** is only that the route worked for that X-1, in that
  process, at that moment. It is not evidence that any later capture will
  succeed; each later publication is checked by its own steps.

No reviewed record yet establishes that the §9.5.1 route works in the
repository-host runtime that will operate the passes; that remains part of
RP-11's review, and the first X-1 of each pass decides it fail-closed.

---

## 10. Rollback and cleanup — evidence preserved, nothing broad

1. **Derived cleanup only.** The harness's `CL-01` … `CL-47`, and the RP
   producers' own reviewed cleanup, are the only removal acts. The operator
   never runs `rm -r`, `rm -rf`, `find … -delete`, a glob removal, `chattr` on
   any path outside the rehearsal's named residue, `userdel`/`groupdel` by
   hand, `dropdb`/`DROP` by hand, or any `/tmp` operation.
2. **Residue is evidence.** Any residue a harness or producer reports is
   **preserved, reported by absolute path and left in place**, and the pass
   stops. Its recovery is a separate maintainer decision. The only exception is
   inside RR-14, where the residue is planted deliberately and removed by the
   named §2.13.2b operator procedure the rehearsal exists to exercise.
3. **PostgreSQL configuration.** Restoration is the harness's byte-exact
   restore from V5 and its reload. B7 compares the digests with Pass A's. On
   inequality the pass stops. The operator does not edit either file, and
   reports the retained capture's path.
4. **Laboratory records** (V4, V9, V5, and V7 once initialized) are durable by
   design and are never rolled back. **V7 has no rollback by contract.**
5. **Reboot.** A reboot cannot be reversed. If the host does not return, the
   pass stops and the Operations Owner recovers it through the provider
   console, outside this prompt.
6. **Repository.** The pass changes only the handback and the current-state
   pointers. Rollback of a handback edit is a new dated correction.
   **Never** `git reset --hard`, `git checkout --`, `git restore`, `git stash`,
   an amend, a rebase or a force push. Uncommitted earlier work is never
   restored from `HEAD`.
7. **Synchronized worktree.** It is not rolled back. A later authorized
   synchronization replaces it.
8. **`fsync` injection (B4b).** Removal is RP-12's reviewed cleanup only,
   followed by its read-only survey (B4b-3, B7-12). Residue is preserved and
   stops the pass, as in item 2. The operator never removes an injection
   device, mapping or configuration by hand.
9. **Capture records (§9.5).** Stream files, records, index states and
   unadmitted files are retained and are never rolled back, edited, completed,
   renamed or deleted by the operator. Unadmitted files are retained as
   records of the failure, never as admitted evidence. A failed capture or durability barrier
   is reported under C-10 and C-15, not repaired, and a missing or invalid
   final index state is never reconstructed (X-4). After a stop, the
   mechanism's one X-3 finalization attempt is the only write, and the root
   is read-only once it reaches its outcome (§9.5.3). Neither pass's capture
   root is rolled back or cleaned up, and `⟨MI.capture_root_A⟩` is never
   removed, renamed, reused or modified to admit Pass B (C-8). B0-RA only
   reads it to verify retention, including that every name Pass A's final
   state accounts for, unadmitted names among them, is still present with its
   expected object type; for an unadmitted file that is presence, not content.
   If B0-RA fails, nothing under it is repaired, completed, restored or
   re-created, and no absent or mistyped name is re-created or replaced; the
   failure is reported and Pass B does not start. A staging name, or a
   staging/final pair, that no durable index state admits (§9.5.1) is retained
   like any other unadmitted file; it is never linked, re-linked, removed,
   renamed or republished. **An admitted object's staging name is part of its
   retained evidence, not a temporary**: it is never unlinked, renamed or
   cleaned up. "Read-only" is the §9.5.3 behavioural terminal seal; no
   permission is changed to roll anything back.
10. **No publication probe (§9.5.4).** There is no probe, probe directory
   or probe clean-up. A failed X-1 genesis publication — the capability test —
   leaves its residue under the pass's own capture root, where it is retained
   and reported under item 2 and item 9; the operator removes nothing, and
   nothing in RP-11 unlinks, renames or cleans up any name.

---

## 11. Stop conditions

### 11.1 Global stop-on-refusal rule — overrides every other instruction

Each of the following **immediately consumes the entire pass's authority**,
whether it happens before or after host contact:

1. a refusal by `guard-secrets.py`, `guard-git.py`, any other `PreToolUse`
   guard or any repository guard;
2. a denial, refusal, rejection or block by the client, the execution harness,
   a sandbox, a permission classifier, a policy layer or a command tool;
3. a request or indication that elevated, bypass, unsandboxed or exceptional
   tool permission is needed;
4. a `sudo` password prompt, or a `sudo` refusal;
5. any uncertainty whether a response is a refusal, or whether the exact plain
   command ran.

On any of these the operator does not request approval or escalation; does not
add, remove or change a tool parameter; does not re-quote, split, chain,
unchain, wrap, reformulate, substitute or retry; and issues **no further host
command**, not even a read-only one. The capture mechanism's one X-3
finalization attempt is not a host command and not a retry; it follows the
§9.5.3 stop transition. The operator records the exact attempted
call and the exact refusal in a repository-only stopped-pass handback and
returns it for maintainer direction and independent Codex review. **Only a
later fresh authorization can say otherwise.** The client's ordinary default
execution path is the only permitted path: no `dangerouslyDisableSandbox`,
escalation flag or equivalent.

### 11.2 Per-band stop conditions — stop, record, never repair

| Band | Stop on |
|---|---|
| Every band | any RP-11 capture failure under §9.5 C-10: a command not started; a stream not captured in full or not closed; a stream over its declared maximum; a digest not computed; a failed or unconfirmed file barrier on a stream file, record or index state; a failed or unconfirmed directory barrier after creating the capture root or a subdirectory, or after publishing a stream file, record or index state; a staging name that is occupied, cannot be created, or is not a regular, operator-owned, mode-`0600`, link-count-one inode on the capture root's device; a write whose content check finds a size or digest other than the record's; an exclusive final link refused because the final name is occupied, reported as failed, or not confirmed; a pair verification after the directory barrier that fails; an index state not advanced (X-2); or a repository-host interruption (C-15). The act is `inconclusive`, and nothing is retried, repaired or re-issued. The §9.5.3 stop transition then applies in order: no further host command; if the capture mechanism and the repository host remain available, one X-3 finalization attempt as the only write; the pass's capture root read-only once that attempt succeeds at its finalization point or fails. After an interruption of the mechanism or the repository host (C-15), no attempt is made and X-4 applies directly. A missing, stale, non-durable or inconsistent final index state (X-4) makes the pass's capture evidence `inconclusive` |
| A0 / B0 / B1 | any pin mismatch; a non-empty porcelain status; a dry-run line that differs; any failed or skipped classifier test; a missing A-1 … A-6 or MI input, including a missing independent MD-5 acceptance record; A0-08 not satisfied (RP-11 unmet, its digest different, `⟨MI.capture_root_A⟩` already present, or Pass A's X-1 genesis publication — the §9.5.4 capability test — not reaching verification of both of its names); B0-RA not satisfied (RP-11 absent; `⟨MI.pass_a_handback⟩` missing or its digest different; the Pass A handback recording no successful X-3 finalization, no valid X-4 or no final index state; `⟨MI.capture_root_A⟩` not exactly the recorded root; the root or the named final index state absent; the re-derived capture index SHA-256 different; X-4 failing for Pass A's retained chain, records or bound stream files; in the complete recursive comparison of condition 5, a name observed under the root not accounted for by Pass A's final state, a name that final state accounts for — including an unadmitted name — absent at its exact relative name, an object-type mismatch, a duplicate or ambiguous name, a path alias other than a recorded staging/final pair, an admitted pair whose members, inode, owner, mode, link count or digest differ from Pass A's durable state, an unadmitted recorded pair whose members are not one inode at link count two, a name resolving outside the root or an unexpected object type; or the enumeration or either direction of the comparison not completed) — a fail-closed stop before B0-08, so no `⟨MI.capture_root_B⟩` is created and no Pass B host command is issued; B0-08 attempted without a successful B0-RA; B0-08 not satisfied (RP-11 absent, its digest different, `⟨MI.capture_root_B⟩` already present, equal to `⟨MI.capture_root_A⟩`, within it or containing it, or Pass B's own X-1 genesis publication — its §9.5.4 capability test — not reaching verification of both of its names); `⟨MI.pass_a_handback⟩` without exactly one well-formed `rp11-capture-binding/1` block (§14); any act that would write, move, rename, truncate, complete, repair, adopt, delete or change the permissions of anything under `⟨MI.capture_root_A⟩`, including during B0-RA, or use any of it as Pass B evidence; a current-state record that does not name this prompt |
| A1 | a sync exit other than 0; a digest that differs; any target-identity mismatch; `R` present; any of the seven identities present; `fb-evidence-s4.service` loaded; `fb_evidence_p5_0` or `freedom_migration_coordinator` present; a V-item differing from its expected state; an unreadable or unparseable host fact; an A1-C value that differs from the pinned statement (reported, never reconciled); an A1-Z value that differs from its earlier Pass A value |
| B2–B4 | any `REFUSED —` line; a non-zero exit; `stopped at` other than `—`; residue other than `none`; `configuration` other than `no unresolved risk`; `cleanup skipped` > 0; `artifact eligible: False`; `run unsettled: True`; a run record that is not written, read back and validated |
| B4a | a producer exit other than 0; an `evidence_cli` refusal; an artifact that does not read back |
| B4b | any result other than RP-12's reviewed expectation; any effect outside RP-12's declared scope; a cleanup exit other than 0; residue; a B4b-3 survey that finds an injection artifact |
| B5 | a refusal not observed **before** its recovery is applied; a recovery act on a path the rehearsal did not name; residue after recovery; any touch outside `R` |
| B6 | anything in the B6 table's stop column; no `⟨MI.reboot_go⟩`; a host that does not return within the bounded reconnection; a changed host key; `boot_id` unchanged; any B6.1b ≠ B6.7 value (recorded as a **failed** JNL-02b and never re-run) |
| B7 | any §13.2 survey item differing from its expectation |

### 11.3 No-retry rule

**Nothing is retried, repeated or re-attempted after a stop**, including a
harness run, a producer, an `fsync` injection, a rehearsal, a reboot, a
synchronization, a command whose capture failed, a failed capture
durability barrier (§9.5 C-10), a failed or unconfirmed exclusive final link
or pair verification (§9.5.1), a failed X-1 genesis publication (§9.5.4), a failed X-3
finalization attempt (§9.5.3), or
a failed or incomplete B0-RA retention verification (§7.1), including a
failed or incomplete enumeration or name-set comparison,
unless a later written
authorization says otherwise. B6.5's bounded reconnection is the
only repetition permitted. It is pre-declared, read-only and not a retry of a
refused operation.

---

## 12. Secrets, credentials and protected artifacts

* **No secrets scan is part of either pass**, and no command expected to engage
  a secrets guard is issued. A-5 is established by the maintainer's
  attestation, not by inspection.
* Never read, print, copy, transfer or modify `.env` files,
  `yt-cookies.txt`, service-account or credential JSON, keys, certificates,
  `.pgpass`, Discord tokens, OAuth secrets, database URLs or Foundry
  credentials, on either host. The §5 exclusions keep them out of the
  synchronization, and `.env.example` is the only exempt name.
* Commands print **digests, not contents**, for `/etc/machine-id`,
  `pg_hba.conf`, `pg_ident.conf` and the interpreter. Process listings print
  `comm` only, never argument vectors. No environment is printed.
* `TEST_DATABASE_URL` is never exported. No suite is part of either pass.
* **Protected historical artifacts:** `/tmp/fb-i3-root.out`,
  `/tmp/fb-i3-root.err` and `/tmp/fb-i3-r6-filelist.txt` must not be read,
  inspected, `stat`ed, written, deleted, truncated, overwritten, moved,
  modified or reused. **No command in this prompt names or globs any `/tmp`
  path.** A command that would has not been reviewed and must not be issued.
  Referring to this restriction is not access to them.
* No auxiliary file (capture, script, file list, wrapper or scratch file) is
  created on `oracle-test` by the operator. Command output is captured **only
  on the repository host**, under the pass's own capture root
  (`⟨MI.capture_root_A⟩` or `⟨MI.capture_root_B⟩`), by the RP-11 mechanism
  and under the §9.5 redaction boundary; the raw stream files are never
  committed or published. The only objects on `oracle-test` are those the
  reviewed harness and producers create and remove, the synchronized worktree,
  the laboratory records and `⟨MI.run_record_path⟩`.

---

## 13. Intended target-side changes and the final clean-state survey

### 13.1 Intended changes

| Change | Pass | Reversed by | Persists? |
|---|---|---|---|
| `/opt/freedom-blades/platform` replaced by the pinned tree (`rsync --delete`) | A, B | a later authorized sync | yes |
| V7 `lifecycle.json` initialized (if AUTH-V7) | B | **none, by contract** | yes |
| Run ledger, reservation and recovery-store entries in V4, V9 and V5 | B | none, by design | yes |
| The seven disposable OS identities (M-01 … M-09) | B | `CL-*` | no |
| `R` and its hierarchy, `+a`/`+i` attributes, `R/bin/case` (M-10 … M-38) | B | `CL-*` | no |
| `fb_evidence_p5_0` and `freedom_migration_coordinator` (M-39, M-40) | B | `CL-*` | no |
| `pg_hba.conf`/`pg_ident.conf` lines (M-41, M-42) and PostgreSQL reloads | B | byte-exact restore and reload | no |
| Transient unit `fb-evidence-s4.service` (M-43) | B | ends with its run | no |
| RP-3, RP-5, RP-6, RP-7 and RP-12 producer objects, all under `R` or pinned disposable paths | B | each producer's reviewed cleanup | no |
| RP-12's `fsync` injection state (whatever the reviewed mechanism declares, confined to its scope) | B | RP-12's reviewed cleanup, then B4b-3 and B7-12 | no |
| One supervised reboot: every service restarted, `/run` re-created, a new `boot_id` | B | — | the fact of the reboot |
| `⟨MI.run_record_path⟩` and `⟨RP-3.artifact_path⟩` | B | — | yes (evidence) |
| System logs (`sshd`, `sudo`, journald) — incidental side effects of access, not planned acts | A, B | — | yes (external evidence) |

In Pass A the `rsync --delete` is the **only** planned change; everything else
in Pass A is read-only apart from the incidental log entries above. The capture
records of §9.5 live on the repository host and are not a target-side change.

**Nothing else may change.** In particular: no package installation, no
dependency update, no `chmod`/`chown` outside the harness, no group change for
`ubuntu`, and no change to `freedom_test`, `freedom_dev`, PostgreSQL 18,
`/etc/freedom-blades`, `/etc/sudoers.d`, `/opt/freedom-blades/runtime`, the
Freedom bot or any service unit.

### 13.2 Final clean-state survey (Band B7; Pass A's subset is A1-Z)

| # | Command | Expected |
|---|---|---|
| B7-01 | A1-19 | exit `1`: `R` absent |
| B7-02 | A1-23 (all seven) | exit `2` each |
| B7-03 | A1-24 | `LoadState=not-found` |
| B7-04 | A1-21 and `ssh oracle-test "stat --format='%n %U:%G %a %F' /var/lib/freedom-blades/laboratory/lifecycle.json /run/freedom-blades/laboratory.lock"` | V-items unchanged in owner and mode; V7 as authorized; the lock as V3 defines it |
| B7-05 | A1-31, A1-32 | no `fb_evidence_p5_0`, no `freedom_migration_coordinator` |
| B7-06 | A1-33 | equal to `OP.pg_hba_sha256` and `OP.pg_ident_sha256` |
| B7-07 | A1-29, A1-30 | 16 `active`/online, 18 `down` |
| B7-08 | A1-25 … A1-28 | no process, service, timer or session outside the baseline except those the reboot legitimately re-created, each named |
| B7-09 | A1-07, A1-09 | mount unchanged; free space within 1 % of B1 (proposal) |
| B7-10 | A1-S1 | the dry run still reproduces `⟨PIN.reviewed_digest_B⟩` |
| B7-11 | A1-01 … A1-06 | identity unchanged; `boot_id` = `OP.boot_id_post` |
| B7-12 | `⟨RP-12.survey_argv⟩` (B4b-3) | no `fsync` injection artifact remains. **Unresolved until RP-12 exists** |

Every B7 command is issued through RP-11. **Pass A's subset** is A1-Z (§6.2):
B7-01 … B7-03, the A1-21/A1-22 part of B7-04, and, only under AUTH-DBREAD,
B7-05 … B7-07, each expected equal to its earlier Pass A value.

---

## 14. Handback template

Each pass returns a dated, repository-only handback at the §9.1 path, then
updates `docs/review/Handover information`, `docs/project-management/status.md`
and implementation-plan §20 **only** to what actually happened. It updates the
RAID, decision and change registers only where an event occurred.

**The capture binding block (proposed by C-P5.0-R5-RP11-I1-R1).** A pass whose
X-1 created its capture root states its capture binding in **exactly one**
fenced block of the fixed form `rp11-capture-binding/1`, shown in the template
below. A pass whose X-1 did not create its root carries **no** block and says
so in its outcome; a Pass A handback without a block gives B0-RA nothing to
verify, and Pass B is not admitted. The rules are exact:

* **Encoding.** The handback is UTF-8 with LF line endings. It is authenticated
  by its SHA-256 (`⟨MI.pass_a_handback⟩`) before anything in it is parsed.
* **Single occurrence.** Exactly one line of the handback equals the opening
  fence `` ```rp11-capture-binding `` exactly, and that fence text occurs
  nowhere else in the file, not even quoted. Zero or more than one is a
  refusal.
* **Body.** The seven lines immediately after the opening fence are, in this
  order and with no other line between them: `format`, `pass_id`,
  `capture_root`, `x3_outcome`, `x4_validity`, `final_state`,
  `capture_index_sha256`. Each is the key, a colon, **one** ASCII space and a
  non-empty value with no leading or trailing whitespace and no carriage
  return. The line immediately after the seventh is exactly `` ``` ``. A
  missing, extra, reordered, repeated or differently spaced key is a refusal.
* **Values.** `format` is exactly `rp11-capture-binding/1`. `pass_id` is the
  pass's identifier (`C-P5.0-R5-OP1-A` or `C-P5.0-R5-OP1-B`), matching
  `\A[A-Za-z0-9][A-Za-z0-9._-]{0,63}\Z`. `capture_root` is the pass's capture
  root **byte for byte**: absolute, no trailing slash, and every component
  matching `\A[A-Za-z0-9_-][A-Za-z0-9._-]{0,254}\Z`, at most 4096 bytes, with
  no normalization applied. `x3_outcome` is one of `succeeded`, `failed`,
  `not-made`. `x4_validity` is `valid` or `inconclusive`. `final_state` is
  `index/NNNNNN.final.json` (six digits, state number at least 1) or `none`.
  `capture_index_sha256` is 64 lowercase hexadecimal characters or `none`.
* **What B0-RA reads.** After authenticating the handback digest, **B0-RA
  parses only this block**, and no other line of the handback. It requires
  `pass_id: C-P5.0-R5-OP1-A`, `x3_outcome: succeeded`, `x4_validity: valid`,
  and a `final_state` and `capture_index_sha256` other than `none`; anything
  else is a fail-closed B0 stop. The prose lines of §2 repeat the same values
  for the reader and are never parsed. A disagreement between the prose and
  the block is a handback defect for review; B0-RA does not resolve it.

````markdown
# Claude handback — C-P5.0-R5-OP1-<A|B>; P5.0-R5 feasibility evidence — <YYYY-MM-DD>

Evidence class: FEASIBILITY — harness facsimile — oracle-test. Not production-code evidence.
Authority: <A-1 review record + digest>; <A-2 authorization record, quoted>; operator <name>.

## 1. Outcome
<one of: completed | stopped at <band/step> | refused at <call>>. P5.0-R5 remains Blocking
pending independent review and maintainer decision. <If B6 did not complete: "MD-3 is not
satisfied; P5.0-R5 cannot close on this pass.">

## 2. Measured facts   (observed in this pass; every value from an admitted RP-11 capture record)
<Only if this pass's X-1 created its capture root; exactly once in the handback:>
```rp11-capture-binding
format: rp11-capture-binding/1
pass_id: <C-P5.0-R5-OP1-A | C-P5.0-R5-OP1-B>
capture_root: <this pass's capture root, byte for byte>
x3_outcome: <succeeded | failed | not-made>
x4_validity: <valid | inconclusive>
final_state: <index/NNNNNN.final.json | none>
capture_index_sha256: <64 lowercase hex | none>
```
X-1 genesis publication — the capability test (§9.5.4; an admission result, not a measured
fact): <both names verified at <client UTC> | stopped at <stage>: <classification>; publication
state <§9.5.1 state>; residue retained <none | each exact relative name and object type>>.
Capture root (this pass's own): <A: MI.capture_root_A | B: MI.capture_root_B |
B: not created (stopped at B0-RA)>.
<B only: B0-RA retention verification (§7.1; an admission result, not a measured fact) against
the Pass A handback <path, SHA-256>: <passed at <client UTC>: root matches, final state <name>
present, capture index SHA-256 matches, X-4 valid, recursive name sets agree in both
directions with matching object types (observed-not-recorded: none; recorded-not-observed:
none) | stopped: <condition>, <reason>, <each name in either set difference, or each
mismatched, duplicate, aliased or escaping name>>. It establishes retention at that moment
only. For unadmitted files it establishes presence, relative name and object type only, not
unchanged content. Pass A capture root
MI.capture_root_A: read only by B0-RA; not written, moved, renamed or removed by this pass, and
not used as Pass B evidence.>
<A only: capture root stated exactly, byte for byte; it, the final state name and the capture
index SHA-256 below are B0-RA's inputs for Pass B, and B0-RA compares the root's contents
with every relative name and object type the final state records.>
X-3 finalization attempt (§9.5.3): <succeeded at the finalization point | failed at <step>:
<reason> | not made: <interruption | no durable I-0>>. Final index state: <name | none>;
capture index SHA-256 (of the final state, §9.5.2 X-3): <64 hex | none>; terminal status:
<completed | stopped at capture_seq <k>, <step>, <reason>>; X-4 validity: <valid | inconclusive:
<reason>>. Index states: I-0 … I-<n>, then final. Admitted records: <n>, seq 1–<n>, no gaps.
Subdirectories created by the mechanism (X-3): <none | relative names>.
Unadmitted files (§9.5.3): <none | each by exact relative name and object type, as the final
state records it, staging names and staging/final pairs included>. Their content is retained but
not digested and not verified; they are not evidence. Every admitted record and index state is a
retained staging/final pair on one inode; no name was unlinked, renamed or cleaned up.
| # | Band/step | capture_seq | capture_record_sha256 | Exact argv | run_as | UTC start–end | Exit | stdout_sha256 | stderr_sha256 | Observed (safe excerpt) | Expected | Classification |

## 3. Inferences   (each marked as inference and naming the facts it rests on)

## 4. Case results by §8 row
| Row | Case | Producer | passed | failed | inconclusive | not_run (reason) |
Totals: passed <n>, failed <n>, inconclusive <n>, not run <n>, skipped <n>.

## 5. Reboot (B6)   pre vs post table: boot_id, machine-id digest, kernel, owner, mode,
inode, device, size, flags, journal/seal SHA-256, current target, unresolved set.

## 6. Recovery rehearsals (RR-11, RR-14, RR-16)   refusal observed → recovery act → re-admission.

## 6a. `fsync` failure injection (B4b, row 40)   injection → facsimile observation → cleanup → survey.

## 6b. Stated target facts (A1-C / P-05 / P-06)   statement record and digest; RP-10 verification
reference; each observation compared with it; any mismatch reported, never reconciled.

## 7. Warnings, deviations and refusals   (every one; "none" stated explicitly)
Guard/tool/harness/sandbox/classifier/policy refusal: <none | exact call + exact refusal>.
Approval or escalation requested: <no>.

## 8. Residue, cleanup and rollback   residue by absolute path (or none); cleanup summary;
retained recovery inputs; anything preserved; rollback performed (or none).

## 9. Final clean-state survey (§13.2)   every row with its observation.

## 10. Checks not run, and why

## 11. Protected artifacts and secrets   /tmp artifacts not accessed; no secrets scan; no
secret file read or transferred.

## 12. What this does not establish   (§15, restated)

## 13. Proposed independent-review focus
````

---

## 15. What success does and does not establish

A pass that completes cleanly and is then independently accepted establishes
**feasibility only**: on `oracle-test`, the reviewed hierarchy, identities,
capability constructions and probe stages behave as designed; a bounded
`fsync` failure can be injected and is observed by a facsimile consumer; a
harness-created generation's unresolved dispatch, `+a`, `+i` and chain survive
a supervised reboot; and the named recovery procedures for R-5.0-11, R-5.0-14
and R-5.0-16 work against facsimiles.

It **does not**:

* constitute production-code evidence, or substitute for the JNL-02b and
  RR-11/14/16 repetitions against the production writer, admin tool,
  coordinator and `0014` at the implementation/release gate;
* close P5.0-R5 (only Peter Duscha decides that, after Codex's independent
  review of the evidence);
* make OD-62 G-A binding, confirm A-5.0-5 (including component (k)), set
  `plan.is_executable=True` as an approval, or declare Package 5.0 ready;
* satisfy MD-5: a green local classifier preflight is not its independent
  acceptance;
* authorize implementation, migration `0014`, deployment, any production host
  or any further operational pass;
* narrow or close `R-5.0-10` … `R-5.0-16`, or say anything about the
  late-Google-apply residual R-5.0-8;
* approve a digest for any purpose beyond this pass.

---

**Draft reminder:** this document is an amended draft for Codex's independent
pre-execution re-review. It authorizes nothing. Option 1 is the accepted policy,
but these exact amended requirements bytes and the RP-11 implementation remain
unaccepted; the accepted R5 bytes (`5e06a388…`) remain the baseline until these
exact bytes are accepted. There
is no separate publication probe: each pass's X-1 genesis publication is its
fail-closed capability test, before any host command (§9.5.4). Neither pass is
executable while the C-11 synchronization route and the launcher environment
are undecided in reviewed bytes. Pass A is not admissible until
RP-11, A-6, `MI.pinned_commit` and `MI.capture_root_A` are met (and its A1-C
steps need RP-10). Pass B is not admissible until RP-1 through RP-12 are met,
its own distinct `MI.capture_root_B` and `MI.pass_a_handback` are supplied,
and B0-RA has verified, read-only, that Pass A's retained root and final
index state still match the Pass A handback and that the names under that
root agree in both directions with the names its final state accounts for.
Either requires a further amended draft, a clean pinned commit, any new
reviewed digest and Codex's re-review of those exact bytes.
