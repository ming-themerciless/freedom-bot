# Claude handback — P5.0-R5 operational-evidence prompt drafting — 2026-09-24

Author: Claude, drafting under the assignment in `docs/review/Handover
information` (2026-09-24) and its controlling prompt,
[`phase-5-0-p5-r5-operational-evidence-prompt-drafting-claude-prompt.md`](phase-5-0-p5-r5-operational-evidence-prompt-drafting-claude-prompt.md).
Peter Duscha's session instruction was *"Please implement …/Handover
information"*. Codex remains the Independent Reviewer and did not take part in
this pass.

**Repository-only.** No command was issued to `oracle-test` or to any other
host. No SSH, synchronization, inspection, `sudo`, database access, provisioning,
verifier, evidence band, controlled write or reboot occurred. The protected
`/tmp` artifacts were not accessed. No secrets scan was run. No guard or tool
refused a call. Nothing was committed or pushed.

**Nothing here authorizes the drafted prompt, sets `plan.is_executable=True`,
closes P5.0-R5, makes OD-62 G-A binding, approves a digest or declares Package
5.0 ready.**

---

## 1. Outcome

Both deliverables are returned for Codex's independent pre-execution review:

1. [`phase-5-0-p5-r5-operational-evidence-authorization-prompt.md`](phase-5-0-p5-r5-operational-evidence-authorization-prompt.md):
   the draft **C-P5.0-R5-OP1**, containing all sixteen required elements; and
2. this handback.

**The central finding, stated first because it governs everything else: the
drafted feasibility pass cannot be executed against the repository as it
stands.** The draft therefore has two parts.

* **Pass A** covers local admission, the one synchronization, and a read-only
  preflight that freshly observes every MD-2 target fact and the twelve
  unconfirmed harness facts. It can be admitted once three things exist: Codex
  acceptance, Peter's authorization, and two maintainer inputs (the MD-5
  disposition and a pinned commit).
* **Pass B** covers harness provisioning, controlled mutation, database
  evidence, the three MD-4 recovery rehearsals, the MD-3 supervised reboot, and
  the final clean-state survey. It is fully structured, but it is **not
  admissible**. It depends on nine repository prerequisites (RP-1 … RP-9) that
  are unmet. Several of them are code or artifacts that do not exist.

The draft states Pass B's commands exactly wherever the repository fixes them.
Where a producer does not exist, the draft uses a typed placeholder and does
not invent a command.

### 1.1 Why Pass B cannot run today — four independent blocks in the pinned source

The local dry run at drafting (executed nothing) reported:

```
steps planned 138 · mutations declared 43 · cleanup steps derived 47
unresolved conflicts 4 (C-7, C-S4-3)
unconfirmed facts: interpreter_sha256, interpreter_real_path, E7.{cap_amb,cap_bnd,
  cap_eff,cap_inh,cap_prm,gid,groups,no_new_privs,securebits,uid}
review manifest digest ac5ffb3cc1a077618d8fc0590a803ec42282a3a1011d4edfc9ff1eafb5137dad
executable False
```

1. **C-S4-3** and **C-7** keep `plan.is_executable=False`.
2. The **twelve reviewed target facts** are unconfirmed. `ExecutingRunner`
   refuses construction until they are supplied **in source**, and supplying
   them needs Pass A's observations first. Pass B can therefore never share a
   pass with the first observation of those facts.
3. **`reservation.REAL_EXECUTION_REFUSAL`** refuses every real execution while
   EH-R16-1 is open. `admit()` receives `ownership_remedy_accepted=False` by
   default, and the CLI supplies nothing else.
4. The laboratory has no V7 lifecycle record (`V7_EXCLUSION`). V8 and V10
   remain unconfirmed target facts.

### 1.2 What no artifact in the repository can produce

* **MD-3's reboot case.** Nothing creates a facsimile generation with a
  genesis record, a seal body, a hash chain and an unresolved `dispatch`.
  Nothing re-verifies such a generation after boot. The harness's
  `000001.journal` and `000001.seal` are provisioned with `+a`/`+i`, but they
  carry no records, and the single-process harness cannot span a reboot
  (reconciliation row 44).
* **MD-4's three recovery rehearsals.** R-5.0-14 and R-5.0-16 rest on the three
  unresolved C-7 producers. R-5.0-11 has no producer at all. The WP-9 recovery
  document, `docs/operations/migration-cutover-and-rollback.md`, which package
  plan §2.13.2b names as the home of the procedures, **does not exist**.
* **Vectors** for `JNL-13`, 21 of 24 `JNL-49`/`JNL-50` cases, `JNL-48(b)`,
  `JNL-30` and `JNL-48(d)`.

**Recommendation for Codex and the maintainer.** Review Pass A as a separable,
immediately admissible read-only pass. Treat RP-1 … RP-9 as the repository work
Pass B needs. RP-1 would be a small pass once Pass A returns; RP-5 and RP-6 are
the largest. Re-review an amended draft before any mutation, database, rehearsal
or reboot authority is considered. Under MD-3, P5.0-R5 cannot close until RP-5
exists and B6 runs.

---

## 2. Files read

* `CLAUDE.md`; `.agents/AGENTS.md` (complete).
* `docs/implementation-plan.md`: the reading map, §0, §12 (intro, §12.0 and the
  Phase 5 package table), §13, §14, §15.1, §16, §17, §20.
* `docs/review/Handover information` (current), and the relevant blocks of
  `Handover-information-through-2026-09-24.md` (the R1 and R2 review/remediation
  blocks).
* `docs/operations/disposable-test-server.md`: the current restriction banners,
  §§1–4.
* `docs/review/phase-5-0-p5-r5-evidence-reconciliation-handback.md` (complete).
* The MD decision records: MD-1 through MD-5 (2026-09-23) and MD-6
  (2026-09-24).
* The R1–R4 chain: the R1, R2 (header), R3 (via registers) and R4 (via
  registers) handbacks, and the R3 and R4 acceptance records. The R2 and R3
  handbacks were not read in full. The draft rests on their accepted outcomes
  as recorded in the acceptance records, the change log and status history.
* `docs/review/phase-5-0-package-plan.md`: header; §2.13.2b, §2.13.6, §2.13.7
  and §2.13.8 (complete); §7.4 (located); section index for §§2.12, 6, 8 and
  9. **Not read in full:** §2.12.2–2.12.8, §6.1–6.5, §8.1–8.4, §9.2 and §9.4.
  Their content bearing on this draft was taken from the reconciliation's
  citations. Codex should check the draft against them.
* `docs/review/phase-5-0-evidence-harness-concrete-plan.md` (§§1, 1.1, 2, 3
  steps, 5d, 6) and `phase-5-0-evidence-harness-review-manifest.json`.
* Source, read-only: `execution/cli.py` (argument set and `--execute` path),
  `evidence_cli.py` and `provisioning_cli.py` (headers), `reservation.py`
  (`REAL_EXECUTION_REFUSAL` and `admit`), `boundary.py` (launch identity),
  `participants.py` (`RUN_IDENTIFIER`), `capability.py` (E7 facts),
  `case_runtime.py` (interpreter facts), `provisioning.py` (V-items and
  unconfirmed facts); searches of `journal.py` and `case_program.py`.
* Registers: `status.md` and `status-through-2026-09-24.md` (recent blocks); the
  `change-log.md` top rows; `raid-register.md` (the P5.0-R5 row and the
  R-5.0-11 … R-5.0-16 rows).
* Precedent, used for safety structure only:
  `phase-5-0-reserved-laboratory-i3-r8-controlled-write-claude-prompt.md`.
* `.claude/hooks/guard-secrets.py` (header), to keep the drafting checks clear
  of the guard.

## 3. Files changed

| File | Change |
|---|---|
| `docs/review/phase-5-0-p5-r5-operational-evidence-authorization-prompt.md` | **new**: the draft |
| `docs/review/phase-5-0-p5-r5-operational-evidence-prompt-drafting-handback.md` | **new**: this handback |
| `docs/review/Handover information` | a returned-for-review pointer at the top of the active assignment |
| `docs/project-management/status.md` | the current status records the return for Codex review |

No source, test, hook, manifest, generated artifact, migration, schema,
configuration, Package 5.0 design or register row was changed. The drafting
prompt was not edited. The RAID, decision and change registers, implementation
plan §20 and the disposable-server banner were **deliberately not changed**.
This pass records no decision, closes nothing and changes no restriction, and
the handover asked only for the handover and `status.md` to be updated.

## 4. Decisions and restrictions carried into the draft

* **MD-1:** the evidence is labelled `feasibility-facsimile` throughout. §8
  separates `feasibility` from `production-gate` rows, and §15 states what
  success does not establish.
* **MD-2:** every target fact is freshly observed in Band A1. No package-plan
  §8.1 value is used as an expectation.
* **MD-3:** B6 is mandatory. A Pass B that stops before B6 leaves P5.0-R5 open,
  and it is never reported as an accepted Not Run.
* **MD-4:** RR-11, RR-14 and RR-16 are mandatory in B5, each shown as a refusal
  first and then a named recovery. No residual is reopened.
* **MD-5:** precondition A-6; the local classifier tests (A0-06); the
  synchronized-byte proof (A1-S1/S2, pinned `journal.py` and `unit_sandbox.py`
  digests).
* **MD-6:** JNL-40(b) is excluded, and `/etc/machine-id` is read only as a
  digest.
* The handover's host, artifact, secrets and no-retry restrictions carry into
  §§11 and 12. They adopt the I3-R8 precedent's stop-on-refusal wording, with
  one pre-declared exception: B6.5's bounded, read-only reconnection after the
  reboot.

## 5. Evidence scope

**Included as feasibility** (draft §8): reconciliation rows 01–05, 08–10,
12–15 (15 conditionally on RP-2), 20–23, 25, 26 (host half), 44, 49–54; the
three recovery rehearsals; and the MD-2 target facts (row 63).

**Included as local only:** rows 34, 36 and 55 (the MD-5 classifier preflight).

**Excluded:**

* production-gate rows 06, 07, 11, 16, 17–19, 24, 26 (FK half), 27–31, 32(a),
  33, 35, 37–43, 45–48, 56, 57 and 58;
* JNL-40(b), by MD-6;
* rows 59–62, 65 and 66, as already decided;
* row 64, as not applicable.

The PostgreSQL peer-map band runs inside the harness but is recorded as P5.0-R4
support, not as P5.0-R5 closure evidence.

**The feasibility/production-gate division is my proposal** (§8 states the
rule). Codex should test it. Row 40 (`fsync` injection, A-5.0-5(k)) is
classified production-gate and flagged, because no MD requires it.

## 6. Unresolved placeholders and prerequisites

**Maintainer inputs (§4.5):**

* `MI.operator`;
* `MI.pinned_commit` and `MI.pinned_commit_B`;
* `MI.md5_disposition`;
* the pass windows;
* `MI.run_id`, `MI.reservation_id`, `MI.deadline` and the two owners;
* **`MI.run_record_path`** (unresolved: no reviewed location found that avoids
  `/tmp`, the worktree, `R` and the laboratory directories);
* `MI.reboot_go`;
* `MI.producer_argv.*`.

**Repository prerequisites (§4.4):**

* **RP-1**: the twelve facts, from Pass A;
* **RP-2**: C-S4-3. **Open question:** may a reviewed facsimile unit stand in for
  the non-existent `freedom-sheet-writer.service` for feasibility?
* **RP-3**: the C-7 producers;
* **RP-4**: EH-R16-1;
* **RP-5**: the reboot-durability producer;
* **RP-6**: the rehearsal producers and the written procedures;
* **RP-7**: the missing vectors;
* **RP-8**: V7, V8 and V10, and the inventory;
* **RP-9**: the design rulings — `SUPPORTED_DROP_INS`, J-12/J-17, J-02/J-20,
  whether MD-4 covers the systemd-identity cost, and the conflict between
  package plan §2.13.8 (`freedom_test`) and concrete plan M-39
  (`fb_evidence_p5_0`).

**Two findings Codex should weigh:**

1. **MD-5 is not formally recorded as satisfied.** Codex's R1 review raised no
   finding against the classifier part, and later prompts call the C-1…C-4
   mappings "accepted". But no maintainer acceptance of C-P5.0-R5-R1 exists,
   and its change-log row still reads *"Not approved; design amendments pending
   review"*. The draft makes this precondition A-6.
2. **The tree is uncommitted** (140 porcelain entries before this pass). A pass
   that synchronizes the working tree would bind evidence to a state no commit
   identifies. The draft therefore requires `MI.pinned_commit` and a clean
   status.

**Proposals Codex should confirm:** the timestamp format (UTC ISO 8601, `Z`);
the 2 GiB free-space floor; the 1 % free-space tolerance in B7; the 12 × 60 s
reconnection bound.

## 7. Security, data-authority, rollback and reboot implications

* **Security.** The draft introduces no new privileged path.
  * Every mutation goes through the reviewed harness or a reviewed RP producer.
    No ad-hoc `chattr`, `rm`, `useradd` or `psql` write is permitted outside
    RR-14's named residue procedure.
  * Contents of `pg_hba.conf`, `pg_ident.conf`, `/etc/machine-id` and process
    argument vectors are never printed; only digests are recorded.
  * No `/tmp` path appears in any command.
  * The `rsync` is the documented guard-admitted form, byte for byte.
* **Data authority.** Unchanged.
  * No production host, credential, Sheet or database is in scope.
  * `freedom_test` and `freedom_dev` are never written.
  * Database work is limited to the disposable `fb_evidence_p5_0` and a
    `PASSWORD NULL` role, both removed.
  * Migration `0014` does not exist and is prohibited.
  * The maintainer's attestation establishes A-5. No secrets scan is used.
* **Rollback.** Derived cleanup only. Residue is preserved and stops the pass,
  except RR-14's deliberately planted residue. V7 and the laboratory ledger are
  irreversible by contract. No Git rewrite is permitted, and nothing is
  restored from `HEAD`.
* **Reboot.** One supervised `systemctl reboot` runs only after the live
  confirmation `MI.reboot_go`, with every service restarting and `/run`
  cleared. If the host does not return, the pass stops and console recovery
  falls to the Operations Owner. The pre/post comparison covers `boot_id`,
  the machine-id digest, kernel, owner, mode, inode, device, size, flags,
  digests, the `current` target and the unresolved set.

## 8. Checks run, and checks not run

**Run on the repository host, read-only unless stated:**

1. `git status --porcelain=v1`: 140 entries before this pass. `git rev-parse
   HEAD`: `2fb1d6fd88013752d53af76fc97b4db07fc31181`.
2. `sha256sum` of the review manifest JSON (`ea5d22c1…`) and the concrete plan
   (`54371475…`).
3. A read-only Python script comparing all 48 manifest `source_digests` with
   the working tree: **48 covered, 0 mismatched** at `MANIFEST_VERSION` 21. It
   also printed ten pinned source digests and the confirmation token.
4. `env -u TEST_DATABASE_URL PYTHONDONTWRITEBYTECODE=1
   /opt/freedom-blades/runtime/venv-web/bin/python -m
   tools.phase_5_0_evidence.execution.cli`, a dry run with no output flags. It
   executed nothing and wrote nothing. It reported the §1.1 figures and digest
   `ac5ffb3c…`, **validating the A0-05/A1-S1 command and its expected output**.
5. A read-only import of `tools.phase_5_0_evidence.provisioning` (with
   `dont_write_bytecode`) to list the V-item owners and modes used in A1-21.
6. `grep`-based internal consistency checks of the draft's section and band
   references, with the band references corrected where they were stale.
7. `git diff --check` over the changed and new files (§9).

**Not run:**

* anything on `oracle-test` (prohibited);
* any database, verifier, evidence band or provisioner (prohibited);
* the focused classifier tests named in A0-06. They would validate the
  classifier, not the draft's text, so the drafting prompt's test allowance
  does not cover them;
* the bot, web and Foundry suites (not needed for documentation;
  `TEST_DATABASE_URL` stayed unset);
* a secrets scan (prohibited);
* formatter, linter and type checker (none configured; no code changed);
* the draft's remote commands. They are untested by construction, and each
  expected output is a statement for review, not an observation.

## 9. Git status

Before: 140 porcelain entries. After: the same entries plus the two new
untracked files. `Handover information` and `status.md` were already modified
before this pass and remain modified. No file was restored from `HEAD`.

## 10. Proposed Codex independent-review checklist

1. **Admissibility split.** Is Pass A safely separable and genuinely read-only?
   In particular: `sudo grep … /proc/self/status`, `sudo capsh --print`,
   `sudo sha256sum` of the PostgreSQL files, and the catalog reads under
   AUTH-DBREAD.
2. **The four execution blocks (§1.1).** Confirm each against source, and
   confirm that no command in the draft routes around one.
3. **RP-1 sequencing.** Pass A observes, a repository pass supplies, and Codex
   re-reviews, so observation never becomes source inside one operational pass.
4. **The §8 feasibility/production-gate division.** Especially rows 15 (RP-2),
   25/26 (RR-16), 39/40 and 48, and whether any row MD-1 requires is missing.
5. **MD-3.** Is B6 sufficient evidence for *"journal, append-only attribute,
   immutable seal and chain intact and re-verifiable"*? Are RP-5's stated
   requirements complete? Is the B6.5 reconnection exception acceptable under
   the no-retry rule?
6. **MD-4.** Are RR-11, RR-14 and RR-16's minimum contents adequate, and should
   the missing WP-9 procedure document come before RP-6?
7. **MD-5 / A-6.** Should a maintainer acceptance of C-P5.0-R5-R1 be recorded,
   or does Codex's R1 review plus the later accepted chain satisfy MD-5?
8. **Pinning.** `MI.pinned_commit` against an uncommitted 140-entry tree;
   whether the harness's `--confirm-target` token changes when RP-1 regenerates.
9. **Secrets and protected artifacts.** Confirm that no command names a `/tmp`
   path or a secret file and that the `rsync` is byte-identical to §3.2. Check
   that digests-only reporting is sufficient.
10. **Timestamp format, `MI.run_record_path` location, free-space floor and
    B7 tolerances** (§6 proposals).
11. **RP-9 rulings,** especially package plan §2.13.8's `freedom_test` sentence
    against finding F-6.
12. **Parts of the package plan this pass did not read in full** (§§2.12.2–8,
    6.x, 8.x, 9.2, 9.4). Check the draft against them.

Claude has stopped. The next action is Codex's independent technical,
security, operational and evidence review of the exact draft. Only a later
explicit maintainer decision may accept and authorize any operational pass.
