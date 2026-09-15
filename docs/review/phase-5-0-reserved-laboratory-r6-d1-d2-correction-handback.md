# Claude handback — correction of the applied D1/D2 amendment to runner contract r6

Date: 2026-09-15. Direction: Peter Duscha, in session: *"fix it and we give it
back to codex for review."*
Change record approving the amendment: **C-P5.0-LAB-D12**.
Amendment record: [proposed and approved text](phase-5-0-reserved-laboratory-r6-d1-d2-proposed-amendment.md).
Contract corrected: [runner contract r6](phase-5-0-reserved-laboratory-runner-contract-r6.md).

**Returned to Codex for independent review of the corrected contract delta.
Nothing here closes a finding or a gate.** The read-only target preflight is
authorized and stays queued behind this review. C-7 remains unresolved; EH-R16-1
**Open**; `plan.is_executable` **False**; all twelve target facts unconfirmed;
V6, V8 and V10 unperformed; LAB-R6 **Open**; Package 5.0 **not ready**; P5.0-R5
**Blocking**; OD-62 **Open**.

**New review-input digest:**
`5df172565b3b27fe769a87a56f9638e33f25c33c779178d62f0e35a15125d957`, replacing
`fe90f546a1032277d81f1f1d0384ce1d3d0e889300c4f86db76a597ebea96892`. **Review
input only. Do not pass it to `--execute`.**

**Independence, stated.** Claude wrote the D1/D2 proposal, Codex applied it, and
Claude reviewed the applied text and made this correction. Codex's review of this
handback is independent of the correction; it is not independent of the
application, which Codex made.

---

## 1. What the document review found, and what happened to each finding

The review was delivered in session, not as a separate record. Each finding is
repeated here with its disposition.

| # | Finding | Disposition |
|---|---|---|
| 1 | The amendment only adds text, so r6's operative steps still specified `renameat2(RENAME_NOREPLACE)`: §1.3.2's permitted `dirfd` uses, P2, §1.5, §2.3.3 step 9, T1 and T6, §5.10, §6.2's syscall list, the "prerequisite at preflight" paragraph, the V6 row, I3 and §10; M1 and §2.4 said `renameat2(…, 0)` where the new text says `renameat` | **Corrected** in every site, each marked *amended 2026-09-15, D1* (§2) |
| 2 | §6.4's "descriptors opened per run" row was replaced rather than extended, deleting the re-seal descriptor | **Corrected**: the deleted text is restored and D20 is added beside it |
| 3 | The interruption state was described as if nothing were published; after `linkat` and before `unlinkat` the final name **is** published. The operator recovery in `lifecycle_storage.FIRST_USE_RECOVERY` and r6 §5.10 said *"no record was published"*. The cited §2.13.2b is package-plan's residue precedent, and §5.9 covers only the ledger | **Corrected**: §6.2 now names the three states and every reader of the new one; the recovery text is corrected in r6 and in code (§3) |
| 4 | Codex's 2026-09-13 condition, *"tests retain the unexplained temporary"*, was not met for D1's own state; the only test injected its failure before publication | **Corrected**: four real-filesystem regressions reach the state through the real writers (§4) |
| 5 | V6's note said nothing waits on it; the dependency moved to hard-link support and `fs.protected_hardlinks` | **Corrected, and put as a question**: V6 is re-scoped to a read-only observation (§2, question 1) |
| 6 | §6.4's `ctypes` row claimed `execveat` is reached through `os` | **Corrected** to an open implementation item: Python 3.12 has no `os.execveat`, and X1 is unimplemented |
| 7 | The RAID entry said "LAB-D1 and LAB-D2" moved; those IDs are the C-7 producers and the twelve target facts | **Corrected** with a dated correction line |
| 8 | No dated marker in r6; stale amendment record; stale `CONTRACT_GAPS` | **Corrected**: r6 header note, amendment record status, `CONTRACT_GAPS` now empty and `LISTING_DESCRIPTOR` added |

**One claim in my review was wrong, and I did not act on it.** It cited r6
§5.12's *"a failure inside either publication before its rename leaves a
temporary"* as stale. §5.12's two publications, T11 and T12, replace an existing
file and are non-exclusive, so they use `renameat` and the sentence is right.
§5.12 is unedited.

## 2. Contract changes, by section

All in `phase-5-0-reserved-laboratory-runner-contract-r6.md`.

| Section | Change |
|---|---|
| header | dated amendment note: what D1 and D2 are, the marker convention, the correction, and that no fact, finding or authority changes |
| §1.3.2 | traversal descriptor's permitted `dirfd` uses: `linkat` and `renameat` replace `renameat2`. D20 paragraph marked D2 and made exact: its listing is one `os.listdir`, whose `fdopendir`/`readdir`/`rewinddir`/`closedir` issue `fcntl`, `fstat`, `getdents64`, `lseek` and `close` on a duplicate — a trace on this workstation, not the target |
| §1.3.3 D20 | permitted uses changed from *"`getdents`/`readdir`, and nothing else"* to the same exact list; never a `dirfd`, never `fsync` |
| §1.4.2 P2 | `linkat(…, 0)`; `unlinkat(…, 0)`; `fsync(D5.bin)` after both; `linkat`'s `EEXIST` proves the final name was free |
| §1.4.4 M1, §2.4 step 4 | `renameat` |
| §1.5 P2 | exclusive `linkat` in place of `RENAME_NOREPLACE` |
| §2.3.3 steps 9–10 | `linkat`, `unlinkat`, barrier 3; the record is published the same way |
| §5.7 T1, T6 | directory barrier after the exclusive `linkat` and `unlinkat`; T1's uncertain outcome points to §6.2's second state |
| §5.10 | creation rule and durability order; `interrupted_initialization` recovery distinguishes the published case |
| §6.2 | syscall list; *What exclusive publication needs from the target* (hard-link support and `proc_sys_fs(5)`'s `protected_hardlinks` conditions, including P2's change of owner before linking); the substitute paragraph; **the three interruption states** and a per-reader table for T1, T6, §2.3.3 and P2 |
| §6.4 | `ctypes` row as §1 finding 6; descriptor row restored plus D20 |
| §7 V6 | re-scoped observation, and a note stating it is a question |
| §9.2 | rows 70–73, labelled as real-filesystem regressions rather than [M] |
| §9.3 I3, §10 | re-scoped with V6 |

**[D] citations added**, all against man-pages 6.7 as installed here: `link(2)`
(`EEXIST`; `EPERM` for a filesystem without hard links and for
`protected_hardlinks`), `proc_sys_fs(5)` (the three conditions), and
`fexecve(3)` (uses `execveat(2)` since glibc 2.27 where the kernel provides it).

## 3. Code changes — text only, no behavior

| File | Change |
|---|---|
| `tools/phase_5_0_evidence/lifecycle_storage.py` | `FIRST_USE_RECOVERY[INTERRUPTED_INITIALIZATION]`: the two sentences saying nothing was published are replaced by three cases — final name absent (retry from the beginning), same inode (published; remove only the temporary; do not repeat initialization), anything else (stay refused) |
| `tools/phase_5_0_evidence/execution/descriptors.py` | module docstring section now describes D1 and D2 as approved amendments; `EXCLUSIVE_PUBLICATION_SUBSTITUTE` states the published second state and V6's re-scope; new `LISTING_DESCRIPTOR` (in `__all__`); `CONTRACT_GAPS` is `()`; `listing()` docstring points to D20 |
| `tools/phase_5_0_evidence/provisioning.py` | V6's `UNCONFIRMED_TARGET_FACTS` text and the module docstring describe the re-scoped observation |

No control flow, signature, refusal classification or schema changed.
`COVERED_SOURCES` stays **43**, `manifest_version` **12**,
`evidence_schema_version` **3**.

## 4. Evidence

Restricted local pass on this workstation. `TEST_DATABASE_URL` unset. Suites run
serially.

### 4.1 The new regressions, and failing-before

`tests/phase_5_0_evidence/test_lab_implementation.py`. A helper makes the
exclusive publication's `unlinkat` of one named temporary fail once, after
`linkat` has succeeded, and asserts the two names share `(st_dev, st_ino)` with
`st_nlink` 2. A process killed between the two calls leaves the same namespace;
this reaches it through the real writer without killing the test process.

| r6 §9.2 row | Test | Against the unmodified `tools/` |
|---|---|---|
| 70 — T1 | `test_d1_a_first_use_record_stopped_between_link_and_unlink_is_kept_and_refused` | **failed**, on the recovery text: `assert 'same inode' in '… The interrupted attempt published nothing, so no participant was ever admitted on it.'` |
| 71 — T6 | `test_d1_a_run_start_stopped_between_link_and_unlink_blocks_every_successor` | passed — a control: the survey already refused |
| 72 — §2.3.3 | `test_d1_a_capture_stopped_between_link_and_unlink_permits_no_mutation` | passed — a control |
| 73 — P2 | `test_d1_a_payload_stopped_between_link_and_unlink_is_neither_recorded_nor_removed` | passed — a control, **after** I corrected my own first draft, which wrongly asserted `_recorded == {}` although the five run directories are legitimately recorded |

The three controls confirm that the readers already failed closed. What makes them
evidence is §4.2. `test_the_module_under_test_names_its_two_deviations` is renamed
`…_names_its_two_amendments` and asserts D1's published-state wording, D20 in
`LISTING_DESCRIPTOR`, and `CONTRACT_GAPS == ()`.

### 4.2 Single-point reversals

`reversals.py` (scratchpad, not in the tree) edits one source file in place, runs
`test_lab_implementation.py -k "d1_ or two_amendments"` with the tests unchanged,
restores the file's bytes and verifies its SHA-256. Each run uses a fresh
`PYTHONPYCACHEPREFIX`.

| # | Removed | Result | Failing regression(s) |
|---|---|---|---|
| RV-unlink | a failed `unlinkat` is swallowed and the publication returns | 3 failed | rows 70, 71, 73 |
| RV-init-temporary | initialization stops checking the temporary first | 1 failed | row 70 |
| RV-publish-temporary | a publication stops refusing on a leftover temporary | 2 failed | rows 70, 71 |
| RV-survey-temporary | the survey stops counting a temporary as unreadable | 1 failed | row 71 |
| RV-discovery-temporary | discovery stops reporting a leftover temporary | 1 failed | row 72 |
| RV-recovery-text | the submitted first-use recovery text is restored | 1 failed | row 70 |
| RV-P2-record-first | P2 records the payload identity before publishing | 1 failed | row 73 |

Baseline and final: **5 passed**.

**RV-unlink catches rows 70, 71 and 73, and not row 72.** When the unlink is
swallowed, the capture's later verification refuses the store anyway, because the
leftover temporary makes the directory's name set wrong. I checked this directly,
by skipping that one unlink with no source edit: the publication returned
`published False`, `mutation_permitted False`, refusal
`stored-correspondence-does-not-verify` (*"the run directory does not hold the
complete reviewed capture set …"*), with `pg_hba.conf.tmp` beside
`pg_hba.conf`. So row 72's refusal is held independently by `_verify` and by
discovery, and a reversal of discovery alone is caught.

**A disclosed measurement defect.** The script's first version reused the tree's
bytecode cache. RV-P2-record-first moves one line, so the file keeps its size.
It was restored within the same second, so the **final control ran the reversed
bytecode** and reported 1 failed with every source hash correct. I added a fresh
bytecode cache per run and touched the four reversed sources (mtime only), then
re-ran everything. The table above is that run. An ordinary in-tree run
afterwards also passed 5 of 5.

### 4.3 Suites on the submitted tree

| Command | Result |
|---|---|
| `/opt/discord-bots/venv-web/bin/python -m pytest -q -rsfE tests/phase_5_0_evidence` (after installing the artifacts) | **2 229 passed, 0 skipped** (2 225 + 4) |
| `… tests/phase_5_0_evidence/test_lab_implementation.py tests/phase_5_0_evidence/test_no_execution.py` | **361 passed** |
| bot: `/opt/discord-bots/venv/bin/python -m pytest -q -rs tests/test_*.py` | **3 025 passed, 326 skipped**, 1 warning |
| web: `/opt/discord-bots/venv-web/bin/python -m pytest -q -rsfE tests/web` | **1 609 passed, 1 failed, 1 362 skipped** |
| `node --test foundry-module/tests/*.test.mjs` | **171 passed, 0 failed, 0 skipped** |
| `python3 .claude/hooks/test_guards.py` | **31 cases, all passed** |
| `python -m compileall -q tools/phase_5_0_evidence tests/phase_5_0_evidence` | succeeded |
| `git diff --check`; `git diff --no-index --check` on the changed untracked files | clean |

**Every skip is unverified.** Every bot skip (326) and web skip (1 333 + 29) has
the reason *TEST_DATABASE_URL is not configured …*. The database-enabled web
baseline is **80**, and these runs exit 0 without the variable. Nothing here is
PostgreSQL evidence.

**The web failure is the pre-existing one.**
`test_p3_4_static_assets.py::test_the_discovery_enumerates_untracked_files_rather_than_directories`
fails on its own guard, *"no untracked directory in this tree; this test proves
nothing"*. This work created no untracked directory.

**Interpreters.** `/opt/discord-bots/venv-web/bin/python` and
`/opt/discord-bots/venv/bin/python`, both Python 3.12.3 with pytest 8.4.2; node
v24.20.0. These are available local runners, not canonical-environment evidence.

## 5. Generated artifacts and the review-only digest

`lifecycle_storage.py`, `descriptors.py` and `provisioning.py` are covered sources.
The artifacts were regenerated through the **non-executing** CLI only:

```text
python -m tools.phase_5_0_evidence.execution.cli --manifest-out <scratch>/genN/manifest.json --render <scratch>/genN/plan.md
```

No `--execute`, `--confirm-target` or `--reviewed-digest`.

* Generations 1 and 2 are byte-identical: manifest `sha256 6b380b7d…7380`, plan
  `2bed40d3…443e`. Generation 1 was installed. Generation 3 is byte-identical to
  the installed files.
* `COVERED_SOURCES`, read from `review_manifest.py`'s syntax tree: **43** paths,
  equal to the manifest's path set. All 43 hashes recomputed from disk: **zero
  mismatches**.
* Exactly three `source_digests` entries changed: the three files above. Every
  other manifest field is identical.
* The installed plan differs from the previous one only in its digest line.
* Dry run: `executable : False`; `unresolved conflicts : 3 (C-7)`.

## 6. Files changed

| File | Change |
|---|---|
| `docs/review/phase-5-0-reserved-laboratory-runner-contract-r6.md` | §2 |
| `docs/review/phase-5-0-reserved-laboratory-r6-d1-d2-proposed-amendment.md` | status: r6 is the contract; the correction; the approved text left as approved; "Before its acceptance" marked historical |
| `docs/project-management/raid-register.md` | the 2026-09-15 entry's LAB-D1/LAB-D2 sentence, with a dated correction |
| `tools/phase_5_0_evidence/lifecycle_storage.py`, `execution/descriptors.py`, `provisioning.py` | §3 |
| `tests/phase_5_0_evidence/test_lab_implementation.py` | four regressions, two helpers, one import, one test renamed and rewritten |
| `docs/review/phase-5-0-evidence-harness-review-manifest.json`, `…-concrete-plan.md` | regenerated (§5) |
| `docs/review/Handover information` | a dated entry at the top |
| this handback | new |

No migration and no configuration or deployment change. `status.md`, the
decision register, implementation-plan §20 and the change log are **not edited**;
they record Peter's decision and are the maintainer's to update on disposition.

## 7. Security, interruption and residual observations

* **No behavior changed.** Every refusal the regressions exercise existed on the
  submitted tree; §4.2 shows each is load-bearing. The only operator-visible
  change is recovery text that no longer tells an operator nothing was published
  when something was.
* **Not established here:** what a participant that only *reads* the record does
  when it meets the record's temporary. §5.9 lists no refusal for it, and I made
  no claim about it (question 3).
* **Pre-existing discrepancy, not changed:** §2.3.2's barrier row 2 says a P2 data
  barrier failure removes the temporary. `install_case_program` does not remove
  it; it closes the descriptor and raises. This predates D1 and is outside this
  correction.
* **Not modelled:** `durability_model.py` still models an atomic exclusive rename,
  and its `MODEL_LIMITS` still names `RENAME_NOREPLACE`. Rows 70–73 cover the new
  state on real files instead. Changing the model is a separate slice.

## 8. Rollback

Repository-only; nothing was deployed or applied.

1. Delete this handback and the top entry of `docs/review/Handover information`.
2. Restore these files to their pre-correction bytes; copies are in the session
   scratchpad under `before/`:

   | File | Before | After |
   |---|---|---|
   | r6 | `6fc7fdf8…` | `b7ec2493…` |
   | amendment record | `41dfe526…` | `4bfa6611…` |
   | RAID register | `ed5fb3ca…` | `6bd44576…` |
   | `lifecycle_storage.py` | `c468eab9…` | `cc135b83…` |
   | `descriptors.py` | `f041f124…` | `91de32e2…` |
   | `provisioning.py` | `e4817c8b…` | `9658392c…` |
   | `test_lab_implementation.py` | `e3cf0211…` | `bf6ef693…` |
   | review manifest | `27e11439…` | `6b380b7d…` |
   | concrete plan | `5b8d7559…` | `2bed40d3…` |

   Several are untracked and carry earlier uncommitted work, so restore whole
   files rather than reverting hunks against `HEAD`.
3. The digest returns to `fe90f546…6892`.

## 9. Questions for Codex

1. **V6's re-scope.** Is the read-only observation in §7 — the filesystem type
   under each exclusive-publication directory, and
   `/proc/sys/fs/protected_hardlinks`, with no link created — the right
   replacement for `RENAME_NOREPLACE` support? It changes what the authorized
   preflight observes, so Peter decides after your recommendation.
2. **Reaching the state by failing the unlink.** Is an injected `OSError` on the
   one `unlinkat`, after a real `linkat`, acceptable evidence for the state a
   killed process leaves? It exercises every reader on real files. It does not
   exercise a signal.
3. **A reader of the record meeting its temporary.** Should admission refuse on
   the record's leftover temporary, as the ledger survey does for run files, or
   is admitting on a published, re-sealed record correct? Today T7 refuses, so the
   harness cannot proceed, but I did not establish what the six do.
4. **`execveat` without `ctypes`.** Is recording it as an open implementation item
   in §6.4 acceptable, or should the item be carried somewhere with an owner?
5. **Recovery wording.** §6.2's operator recoveries are marked [P]. Are they
   specific enough for the T1 and T6 cases, where the operator must compare
   `(st_dev, st_ino)` before removing anything?

---

**Stop point.** The next checkpoint is Codex's review of this corrected contract
delta. The read-only preflight does not begin until that review and Peter's
disposition. No preflight, provisioning or execution follows automatically.
