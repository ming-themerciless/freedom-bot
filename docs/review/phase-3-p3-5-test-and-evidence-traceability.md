# P3.5 final requirements-to-evidence traceability

**Artifact 2 of `phase-3-p3-5-readiness-and-execution-plan.md` §12.1**, produced by
**EX-1** and **EX-2**. **Prepared:** 2026-08-26 by Claude, P3.5 working Technical
Lead.

**Repository:** `/opt/freedom-blades/platform` · **Branch:** `docs/platform-plan`

**Baselines:** `docs/contracts/phase-3-test-traceability.md` (the accepted
contract; **no row of it is changed here**) · `docs/review/phase-3-delivery-plan.md`
§11 · `docs/implementation-plan.md` §12.

**This document closes nothing and requests no gate decision.**

---

## 1. Method, and why it is checkable

The accepted contract states, for each requirement, an ID, a test, an evidence
level and a citation. This document asks one question of every row: **does the
cited evidence actually exist, and does the citation resolve?**

That question was answered **mechanically and in both directions**, not by
reading down the table and agreeing with it:

1. every `TC-…` row defined in the contract was extracted — **318 rows**, plus
   one withdrawn (`TC-BG-05`, replaced by `TC-BG-05a…05e`);
2. every test function and file that actually exists under `tests/` and
   `foundry-module/` was extracted from source;
3. a row counts as **resolved** if *either* direction links it to something real —
   a test naming the `TC-…` ID, **or** the contract row naming a test that exists.

**Why both directions were needed, and it is worth recording.** A first pass
searched only for tests naming their `TC-…` ID and reported **99 uncited rows**.
That number was **wrong**, and it was wrong in the direction that would have
alarmed a reader: for a large family of rows the contract names the test rather
than the test naming the contract. The corrected bidirectional pass is what §2
reports. It is recorded here because a reviewer should be able to see that the
alarming intermediate figure was checked rather than published.

**Five citation styles are in use**, which is the reason a mechanical check needs
care rather than a single regular expression:

| Style | Example | Resolvable mechanically? |
|---|---|---|
| Explicit | `test_shell_navigation_contract.py::test_each_caller_state_…` | yes |
| Bare function | `test_migration_0012_round_trip.py` | yes |
| Wildcard | `::test_a_public_page_*` | yes, once expanded |
| Two-sided fragment | `…reaped_lease_and_a_new_claim…` | yes, by substring |
| One-sided fragment | `` `…repeated_recovery_passes_publish_once` `` | **only after widening the matcher** |
| Relative | "same file, …" | only by reading the preceding row |

---

## 2. Result

| Class | Rows |
|---|---:|
| **Resolved to a real, existing test** | **294** |
| **Staging / browser / device rows** — Not Run or partial by evidence level, not by omission | **19** |
| **No resolvable citation** | **5** |
| **Total contract rows** | **318** |
| Withdrawn (`TC-BG-05`) | 1 |

### 2.1 The five rows with no resolvable citation — **all five are covered**

Each was chased individually rather than reported as a gap. **Every one has a
passing test; not one is a coverage gap.** What is missing is the *link*, and the
citations are supplied here.

| Row | Requirement | The test that covers it, located by behaviour |
|---|---|---|
| **TC-AUTH-17** | Migration 0009's rotation objects appear on upgrade and disappear on downgrade; a pre-existing branched chain makes the re-upgrade refuse | `tests/test_oauth_completion_binding_migration.py` — `::test_the_rotation_keys_declare_restrict_and_reference_the_predecessors_own_values`, `::test_the_linear_rotation_index_is_unique_and_scoped_to_rotations` and `::test_the_re_upgrade_refuses_a_branched_rotation_chain_it_cannot_describe`, one per clause of the row. The file is named for its **subject** rather than its migration number, which is why neither search direction resolved it |
| **TC-BG-19** | N-32a: challenge issuance and assertion verification hold **separate** per-address budgets | Three tests in `tests/web/test_rate_limits_and_outage.py`: `test_the_eleventh_challenge_from_one_address_is_refused` (issuance), `test_the_sixth_webauthn_assertion_from_one_address_is_refused` (assertion), and `test_a_full_ceremony_spends_one_unit_of_each_budget`, whose docstring states the ten issue-then-verify pairs the row requires |
| **TC-MIG-19** | R-28 never calls a revoked confirmation active | `tests/web/test_identity_migration_command.py::test_r28_never_calls_a_revoked_confirmation_active`, and `::test_another_active_link_cannot_make_a_revoked_confirmation_look_active` for the row's second clause |
| **TC-MIG-21** | A superseded evidence run cannot authorize | `tests/web/test_identity_migration_command.py::test_a_superseded_run_cannot_create_authorization` |
| **TC-MIG-28** | Below the boundary the downgrade is genuinely supported with realistic rows | `tests/web/test_migration_0013_rollback_boundary.py::test_the_downgrade_and_re_upgrade_succeed_below_the_boundary_with_realistic_rows` |

**Finding N-8 — traceability, Minor.** Five accepted rows carry no citation that
resolves in either direction. **No requirement is untested**, and no behaviour is
at risk. The defect is that the contract cannot be verified end to end by anything
but a person who already knows where the tests are — which is exactly the property
a traceability contract exists to remove. **The accepted contract is not edited
here**; the citations above are supplied in this artifact, and whether to fold
them back into the contract is a decision for the Acceptance Authority after
review.

### 2.2 The 19 staging, browser and device rows

These are `Not Run` or partial **because of their evidence level**, not because
anything was overlooked. Each maps to the procedure that would close it.

| Row | Status | Procedure | Owner |
|---|---|---|---|
| TC-LIM-02 | **Not Run** | SP-13 | Peter + Claude |
| TC-SEC-07 browser half | **Not Run** | SP-14 | Peter (browser) |
| TC-OPS-01 | **Not Run** | SP-09 | Peter + Claude |
| TC-OPS-02 | **Disposable half Passed** 2026-08-25/26 (EX-3, EX-4); **staging half Not Run** | SP-10 | Peter + Claude |
| TC-OPS-03 | **Not Run** — needs the snapshot transport step first (N-3) | SP-11 | Peter (browser) |
| TC-OPS-04 | **Not Run** | SP-08 | Peter + Claude |
| **TC-OPS-05** | **Failed** 2026-08-26 — finding **N-7**, remediated in the repository, not yet deployed | SP-12, to be re-run | Peter |
| TC-PERF-01 | **Not Run — never measured** | SP-15 | Peter + Claude |
| TC-PERF-02 | **Not Run — never measured at all** (RR-06); apply reported as **n = 1** under D-m | SP-15 | Peter + Claude |
| TC-PERF-03 | **Not Run** — bound must be stated **before** the run | SP-16 | Peter + Claude |
| TC-UI-01 | **Passed**, one browser one platform | plan-SP-23 | Peter (browser) |
| TC-UI-02 | **Passed**, one browser one platform | plan-SP-23 | Peter (browser) |
| TC-UI-03 | **Partly** — recorded Not Run against the full row | plan-SP-23 | Peter (browser) |
| TC-UI-04 | **Not Run** at its accepted level | plan-SP-23 | Peter (browser) |
| TC-UI-05 | **Partly** — one of six states | plan-SP-23 | Peter (browser) |
| TC-UI-07 | **Not Run** at its accepted level — static half passes | plan-SP-23 | Peter (browser) |
| TC-UI-08 | **Not Run** | SP-18 | **Peter only** |
| TC-UI-09 | **Not Run — permanently for Phase 3 (D-f)** | SP-19 | — |
| TC-BG-02 browser half | **Passed** 2026-08-24 | supervised session §4 | Peter (browser) |

Detail for the TC-UI rows is in
`phase-3-p3-5-accessibility-and-browser-evidence.md`; for the TC-OPS rows in
`phase-3-p3-5-staging-and-operations-evidence.md`.

---

## 3. EX-2 — the two label reconciliations

### 3.1 Finding F-1 — the TC-UI renumbering

The P3.4 submission's accessibility matrix renumbered the TC-UI rows relative to
the accepted contract §16. **The tests were always named for the contract's
numbering** — `test_tc_ui_04_prefers_reduced_motion_media_query` and
`test_tc_ui_07_wcag_contrast_matrix` sit exactly where §16 puts those subjects —
so the code is right and the submission's **labels** drifted.

The consequence F-1 identified is real: **TC-UI-03** and **TC-UI-05** ended with
no citation under their own ID despite passing evidence existing for both.
**Reconciled in `phase-3-p3-5-accessibility-and-browser-evidence.md` §1 and §2.2**,
where both rows are given their citations under the accepted numbering. **No
accepted contract row is changed**, and the misalignment is recorded openly rather
than silently repaired.

### 3.2 Finding N-1 — the SP-23 identifier collision

**The identifier `SP-23` now denotes two different procedures**, and neither usage
can simply be deleted:

| Source | SP-23 means |
|---|---|
| Execution plan §6.2 | Browser-observed rendering at 320/768/1280 and 200%, keyboard traversal, skip links, HTMX and no-JS paths, real-engine contrast, reduced motion |
| Supervised-session evidence and the operational addendum | Retirement below two enabled credentials is refused (A-05 criterion 3) |

The evidence documents additionally use **SP-24, SP-25 and SP-26**, beyond the
plan's SP-01…SP-23 range. And the execution plan's *actual* SP-23 content **was
executed** on 2026-08-24 — recorded under the label "§4.2" rather than under its
own ID.

**Resolution used throughout this package, and it is deliberately not a
renumbering.** Renumbering timestamped evidence records is worse than the
collision: it edits history to tidy a label. Instead:

- **`plan-SP-23`** always means the execution plan's browser procedure;
- **`evidence-SP-23`** always means the retirement-refusal observation;
- SP-24, SP-25 and SP-26 are recorded as **extensions** beyond the plan's range,
  valid as evidence and outside the plan's numbering;
- the 2026-08-24 browser work is cited under **plan-SP-23**, which is the row it
  actually discharges.

**Raised for Codex.** Whether to renumber, and which document should yield, is an
Acceptance Authority decision, not the Technical Lead's.

---

## 4. Delivery plan §11 and implementation plan §12

Every §11 row and every §12 Phase 3 mandatory test maps through the accepted
contract's §18 and §19 tables, which this document does **not** restate — doing so
would create a second mapping that could drift from the first. What this document
adds is the **status** of each mapping's evidence, which §18 and §19 do not carry.

| Class of §11 row | Rows | Status |
|---|---|---|
| Authorization, object-level access, matrix, capability, break-glass boundary | many | **Resolved and passing.** Web suite 2398 passed / 80 skipped, bot suite 2377 passed, Foundry module 155 passed |
| CSRF, origin, host, cookies, redirects, headers and CSP | TC-SEC-01…14 | **Resolved and passing**, except **TC-SEC-07's browser half** |
| Bounds, limits, content type, filenames | TC-LIM-01…06 | **Resolved and passing**, except **TC-LIM-02** |
| Durable jobs, restart, lease, retry, recovery, double-click, two-browser | TC-JOB-01…37 | **Resolved and passing** automatically; **the deployed observation (SP-17) is Not Run** |
| Audit append-only, search, pagination, runtime-role denial | TC-AUD-01…22 | **Resolved and passing** |
| Identity, accounts, linking, legacy evidence, migrations | TC-ID, TC-MIG | **Resolved and passing** |
| Migration apply/downgrade/upgrade and recovery | TC-MIG-04, TC-MIG-07, TC-OPS-02 | **Resolved and passing**; **EX-3/EX-4 executed 2026-08-25/26**, staging half Not Run |
| Responsive, keyboard, focus, reduced motion, error states | TC-UI-01…09 | **See §2.2 and artifact 4** |
| Full gate package | §13.3 checklist, TC-OPS-01…05, TC-PERF-01…03 | **Incomplete — this is what P3.5 is for** |

**No §11 row and no §12 mandatory test is dropped.** Where the accepted contract
already maps a row, that mapping stands unchanged.

---

## 5. What this document establishes, and what it does not

**Establishes:**

- 294 of 318 contract rows resolve to a real, existing test, verified
  mechanically in both directions;
- the 19 staging/browser/device rows are Not Run or partial **by evidence level**,
  each with a named procedure and owner;
- the 5 rows with no resolvable citation are **citation gaps, not coverage gaps** —
  every one was chased and every one has a passing test (**N-8**);
- F-1's TC-UI renumbering and N-1's SP-23 collision are both reconciled without
  editing an accepted contract row or a timestamped evidence record.

**Does not establish:**

- that any staging, browser, device or assistive-technology row has been
  satisfied — 19 rows say otherwise;
- that TC-OPS-05 passes — it **Failed** on 2026-08-26 and its remediation is not
  yet deployed;
- that I-06, A-05, A-06 or R-23 may close;
- any gate decision, which is Peter's alone after both Codex passes.
