# Claude handback — P2/I3 ruling and I3 verifier implemented — 2026-09-19

Authorization: **C-P5.0-LAB-I3-R2**, which implements Peter Duscha's ruling
**C-P5.0-LAB-I3-D1**. Implementing Technical Lead: Claude. Independent Technical
and Security Reviewer: Codex. The assignment is the top entry of
`docs/review/Handover information`.

## 1. Result

**Implemented in the repository and returned for independent review. Nothing was
run on any host.** No SSH, synchronization, inspection or mutation of
`oracle-test`; no `sudo`; no change to real users, groups, permissions or
capabilities; nothing created under real `/run`, `/var/lib` or
`/opt/freedom-blades`; no V7, participant, harness, database, generated vector,
real boundary or materializer, and no `--execute`. Every write this pass made in
a test was under `tmp_path` or the session scratchpad.

**I3 remains unconfirmed.** V7 remains excluded, V8 and V10 unperformed,
`plan.is_executable=False`, `reservation.REAL_EXECUTION_REFUSAL` unconditional,
LAB-SECRETS-1 Open and Low, LAB-V6-P2 deferred, and Package 5.0 **not ready**.
Claude closes no finding, confirms no I3 fact, approves no digest and advances
no gate.

## 2. What the ruling required, and where each item landed

| Ruling item | Implementation |
|---|---|
| 1. P2 is `root:root 0555` | `case_runtime.CASE_PROGRAM_MODE` `"0755"` → `"0555"`; owner and group stay `root`/`root`. P2's effect row and `P-04` both derive from the constant. `P-04`'s purpose string was a literal `root:root 0755` and now derives from the constants. The `P-04` real-output fixture in `test_r13_remediation.py` is now `0 0 555 regular file`. The regenerated concrete plan says `root:root 0555` for B3-07 (P2) and P-04 |
| 2. The owner condition, not `CAP_FOWNER` | `provisioning.VERIFICATION_PROCEDURE`'s capability row no longer says P2 depends on `CAP_FOWNER`. r6 §§6.2, 7.2(6) and 9.3 already carried the ruling (documentation reconciliation). The verifier observes the owner condition directly: the file's `st_uid`, read back from its creating descriptor, must equal the filesystem uid from `/proc/self/status` before `linkat`. The unrelated band cases (E5, E6, A10/A11, `JNL-49-…`) are untouched |
| 3. Capability masks are evidence | `CapInh`, `CapPrm`, `CapEff`, `CapBnd`, `CapAmb` and `NoNewPrivs` are read at admission and again immediately before every `linkat`, and must be unchanged between the two reads. `classify_capabilities` reads each mask from its own field. `CAP_DAC_OVERRIDE`, `CAP_DAC_READ_SEARCH` and `CAP_FOWNER` are reported per mask. `NOT_ATTRIBUTION` is printed on every rendering |
| 4. One dedicated entry point, four contexts | `execution/i3_verifier_cli.py` over `execution/i3_verifier.py`. `--identity root` runs T1 under V4, §2.3.3 under V5 and P2 under canonical `R/bin`. `--identity ubuntu` runs T6 under V9. These are separate invocations, and neither changes identity or capability |
| 5. Decision B's narrow exception | Only P2's context creates `R` (`root:root 0700`) and `R/bin` (`root:root 0755`). Each uses exclusive `mkdirat`, `fchown`/`fchmod` on a compared descriptor, read-back, a parent barrier and a mount re-observation, and each is recorded. Each is removed only after an immediately preceding identity comparison and an emptiness check. `provisioning.EVIDENCE_ROOT_TRACE` states the exception |

The complete procedure is **runner contract r6 §7.4**, which is new. §§6.2, 6.4
(the privileged-writer row), 1.3.3 and 9.3 are amended, §9.2 rows **90–105**
are added, and a dated header entry records the pass. Passages this pass changed
are marked *amended 2026-09-19, C-P5.0-LAB-I3-R2*.

## 3. The publication primitive — factored, not duplicated

`PosixFilesystem.renameat(noreplace=True)` called `os.link` and then
`os.unlink` inside one call, so r6 §6.2's second interruption state could not be
observed through it. That state is both names on one inode with link count two.
**Reuse was unsafe for this one purpose.** A second `os.link` in the verifier
would have been a divergent implementation of the same guarantee. The link is
therefore factored into `PosixFilesystem.linkat`, which is the exclusive claim
alone: `EEXIST` refusal, flags `0`, one component under a registered traversal
descriptor. `renameat(noreplace=True)` now calls `linkat` and then unlinks, and
its behaviour for T1, T6, §2.3.3 and P2 is unchanged. This is stated in
`descriptors.EXCLUSIVE_LINK_PRIMITIVE`. Row 105 asserts that `descriptors.py`
holds the package's only `os.link`.

Two other small additions support accounting and leave existing callers
unchanged. `PosixFilesystem.release()` returns whether `close()` succeeded, and
`close()` still ignores the answer. `DescriptorInventory.release_all()` names
each role whose release failed, and `close()` calls it. `create_file`'s literal
`0o600` became `EXCLUSIVE_CREATION_MODE`.

## 4. Procedure and authority model (r6 §7.4, summarized)

* **Gates.** The default does nothing. The command-line flag
  `--arm-i3-controlled-write` is the first gate. Without it, `main` returns
  before constructing a lookup, a probe or a verifier. The second gate is
  `I3ControlledWriteVerifier.armed`, which must be exactly `True`. It is checked
  when `run()` starts and again before each creating effect. Rows 90–91 reverse
  each gate alone.
* **Admission, before the first write.** Each check below refuses with its own
  member of `ADMISSION_REFUSALS`:
  * the payload digest;
  * the approved host, kernel and architecture;
  * every reviewed account;
  * all four uid and gid fields, including the **filesystem** uid, plus agreement
    with `getresuid`/`getresgid`;
  * `freedomlab` membership for `ubuntu`;
  * well-formed, consistent masks;
  * `protected_hardlinks == 1`;
  * `/var/lib` owned by root and not group- or other-writable;
  * V12, V4, V5 or V9 held one no-follow component at a time, each exactly its
    §7 item;
  * every mount of the approved type and device, read-write;
  * barrier descriptors bound;
  * `R` absent;
  * no earlier verifier name present;
  * both names inside the admitted grammar and unoccupied;
  * every linked file owned by the filesystem uid.
* **Per context.** The sequence is:
  1. exclusive temporary;
  2. complete write;
  3. data `fsync`;
  4. `fchown` (P2 only) and `fchmod` on the descriptor;
  5. read-back and owner-condition check;
  6. write-descriptor release;
  7. status re-read;
  8. `linkat`;
  9. **both names observed**: the same `(st_dev, st_ino)`, a regular file, link
     count 2, owner, group and mode, and the pinned bytes read through each name;
  10. guarded unlink of the temporary;
  11. the final name observed at link count 1;
  12. guarded unlink of the final name;
  13. directory barrier;
  14. absence of both names.

  P2 then makes a guarded, emptiness-checked `rmdir` of `R/bin` and then of `R`,
  each followed by a barrier, and checks that `R` is absent.
* **Names and bytes.** The names are `.fb-i3-verify-<32 hex>-staged` and
  `-linked`. They start with a dot and use none of the `.tmp`, `.record` or
  lifecycle names and none of the case-program names. The payload is 125 fixed
  ASCII bytes with SHA-256
  `d3daa410d7889c5a04baff5159d8ce0ae621309b3ef5ebb85000042ddac1617a`.
* **Per-context file state before `linkat`.** Each follows its real writer:
  * T1 is creator-owned, mode `0600`;
  * §2.3.3 is creator-owned, mode `0400` (`STORED_OBJECT_MODE`);
  * T6 is creator-owned, group from V9's setgid bit, mode `0600`;
  * P2 is `root:root 0555`.

## 5. Capability evidence semantics

The masks are **recorded, not admitted against values**. No reviewed exact mask
exists for either identity. `capability.E7_TARGET_FACTS` are unconfirmed, and
V6/I12 recorded `ubuntu`'s masks as an observation. Admission therefore
requires the masks to be present, well-formed and consistent with
`CapEff ⊆ CapPrm` and `CapAmb ⊆ CapPrm ∩ CapInh`. It fixes no value. A state
that differs at the operation from the admission state fails the context before
`linkat`.

`CapBnd` is never read as `CapEff`: row 96 checks this, including against a
syntax-tree reversal. The verifier does **not** isolate, require or prove
`CAP_FOWNER`. Row 97 checks that the only `CAP_FOWNER` sentence in any output is
the disclaimer. `securebits`, the twelfth identity key, is not observed. It is
readable only through `prctl(2)`, and the single `ctypes` exception belongs to
the case program.

## 6. Partial states, cleanup and results

* **Tracking.** Every created object is tracked from creation with its recorded
  identity, or with none if no identity was established. The first causal
  failure is recorded as `(stage, classification)` from closed vocabularies.
  Later contexts are marked `not-attempted`.
* **Cleanup.** Cleanup walks the context's objects in reverse. It removes only
  objects whose identity still matches and, for directories, only empty ones.
  Each removal is followed by a barrier on the parent.
* **What is never removed.** The following are reported by fate and left in
  place:
  * an object with no identity;
  * a replaced or foreign object;
  * a non-empty directory;
  * an object whose removal failed or could not be confirmed.

  A foreign object at an occupied name is never tracked at all.
* **Survey and descriptors.** A bounded survey lists each held publication
  directory and checks `R`. Inventory descriptors are released and failures are
  counted. Nothing is retried.
* **Results.** Exit codes are distinct:

  | Result | Exit |
  |---|---|
  | `verified` | 0 |
  | not armed | 3 |
  | refused before any write | 4 |
  | `failed-no-residue` | 5 |
  | unclassified | 6 |
  | `failed-operator-attention` | 7 |

  `failed-no-residue` requires every object removed through its guard, every
  barrier and descriptor finished, a clean survey, no foreign object and no
  failed removal barrier. Everything else is `failed-operator-attention`.
  `final_status` is the single place where the result is decided.

## 7. Safe-output analysis

The output uses no free text. Each printed field is one of the following:

* an enumeration value admitted by membership;
* an integer rebuilt from itself;
* `st_dev:st_ino` rebuilt from two integers;
* a mask rebuilt as 16 hex digits;
* a nonce admitted by shape;
* one of the two fixed constants.

Admission refusals and stage failures are closed frozensets. The exception types
`_Refusal` and `_Failure` coerce any unknown classification to "unclassified".
Account-lookup text, OS messages, `/proc` content and paths are never read into
the output. An exception escaping the verifier exits `6` and prints only a fixed
sentence. Row 104 injects secret-looking status lines, masks, lookup text, mount
lines, OS messages and hostile field values, and asserts that none of them
appears in the output.

## 8. Files changed

**New:**
* `tools/phase_5_0_evidence/execution/i3_verifier.py`
* `tools/phase_5_0_evidence/execution/i3_verifier_cli.py`
* `tests/phase_5_0_evidence/test_i3_verifier.py`
* this handback

**Modified:**
* `execution/descriptors.py` — the `linkat` factoring, `release`,
  `release_all` and `EXCLUSIVE_CREATION_MODE`;
* `case_runtime.py` — `0555`;
* `concrete_plan.py` — the P-04 purpose and a docstring example;
* `provisioning.py` — the verification text and the evidence-root trace;
* `review_manifest.py` — `MANIFEST_VERSION` 15 and the two covered sources;
* `tests/phase_5_0_evidence/test_no_execution.py` — the two execution-tier
  declarations;
* `tests/phase_5_0_evidence/test_r16_remediation.py` — the version assertion,
  now 15;
* `tests/phase_5_0_evidence/test_r13_remediation.py` — the P-04 fixture `555`;
* `tests/web/test_p3_4_static_assets.py` — the two allowlist rows;
* runner contract r6;
* the two regenerated artifacts;
* `docs/review/Handover information` — top entry.

These files had earlier uncommitted changes, and those changes are preserved.
**No migration** was added. No configuration, `.env.example` or deployment file
changed.

## 9. Commands and results

Interpreter: `/opt/freedom-blades/runtime/venv-web/bin/python` (Python 3.12.3,
pytest 9.1.1), on this workstation. Every command was run with
`TEST_DATABASE_URL` unset and serially.

| Command | Result |
|---|---|
| Baseline before any change: `python -m pytest -q -rs tests/phase_5_0_evidence` | 2492 passed, 0 skipped, 2 warnings |
| Narrow: `python -m pytest -q tests/phase_5_0_evidence/test_i3_verifier.py` | **137 passed**, 0 failed, 0 skipped, 2 warnings |
| Full: `python -m pytest -q -rs tests/phase_5_0_evidence` | **2637 passed**, 0 failed, **0 skipped**, 2 warnings |
| `python3 .claude/hooks/test_guards.py` | 41 cases (27 refused, 14 allowed), all passed |
| `python -m compileall -q tools/phase_5_0_evidence tests/phase_5_0_evidence` | clean |
| `git diff --check` | clean |
| `python -m pytest -q tests/web/test_p3_4_static_assets.py` (the allowlist file touched) | 110 passed, **1 failed**, see the next paragraph |

Both warnings are pytest's `PytestConfigWarning` about the unknown
`asyncio_mode` and `asyncio_default_fixture_loop_scope` options in
`pytest.ini`. They were present at baseline.

**The single web failure existed before this pass and is caused by the
environment.**
`test_the_discovery_enumerates_untracked_files_rather_than_directories`
asserts that the tree contains an **untracked directory**. The tree has none:
`git status --porcelain --untracked-files=normal` lists 0 directories, and the
session-start status listed only untracked files. This pass added files only
inside directories Git already tracks, so it cannot have caused or cured the
failure. The allowlist assertions in that file passed.

**Formatter, linter and type checker:** none is configured in this repository.
`pytest.ini` is the only tool configuration, and there is no `pyproject.toml`
or `setup.cfg`. None was run, and this is a missing tool, not a pass.

## 10. Deterministic artifacts and the review-input digest

I ran the existing non-executing generation path twice into the scratchpad:
`python -m tools.phase_5_0_evidence.execution.cli --manifest-out … --render …`,
which is the default dry run. Both runs produced byte-identical output. A third
run wrote to `docs/review/` and matched the scratchpad files byte for byte. The
hand-added "stale" banner on the concrete plan is gone because the artifact now
comes from the corrected source.

| Artifact | SHA-256 |
|---|---|
| `phase-5-0-evidence-harness-review-manifest.json` | `781a355f95d6141ca9b3d8d5eb8a381c296ab013fba5c4ba8bf0a822505a4837` |
| `phase-5-0-evidence-harness-concrete-plan.md` | `fa813bfc7ee520a426d115b7638ea1f61ca7d8751a4d50dd82561c20889e9825` |

**Review-manifest digest, review input only:**
`17ed549e7266d9630dc8fbfd259b977458aab36ebe102db084fa6b88459d4da0`. It is not an
approval and must never be passed to `--execute`.

Source identity: `HEAD` `2fb1d6fd88013752d53af76fc97b4db07fc31181` on
`docs/platform-plan`, with 62 uncommitted or untracked paths. Working-tree
SHA-256 values at 2026-09-19T21:36Z:

| File | SHA-256 |
|---|---|
| r6 | `91b88a7fbde5300d77a947809ea2c75a81a1b5bfb34bbded97692903c580f2f6` |
| `execution/i3_verifier.py` | `2783f4de2d5624cc70bff1ade384ac9f1249e6c2f9bc5954e37b12f74f87ca6c` |
| `execution/i3_verifier_cli.py` | `9421331ddb8155e86c78a2995f8bc6f81c9945b7ea110727d6252e149f8fc3bd` |
| `execution/descriptors.py` | `6b75bbdb5fbbe1fba1aa8d4edb8a99b521ceec97a4fbd33ccff42e9252ed948b` |
| `case_runtime.py` | `f4c89f6eab7cad2b89977e3532edd1b1f5b5f2088c40235639ded6a9f971450e` |
| `concrete_plan.py` | `1e23f13a06c5905e280ad29917b8ed18737e3e087424e43133ff3c4470657059` |
| `provisioning.py` | `318aa55f462b3a672cddc55f4e55e7150db897556f90320904095ae15294f8e6` |
| `review_manifest.py` | `3a07f24b85b5f7d3bf80703134a7cbcf91e28ca0d635e3445fe3aeb563bcb5b7` |
| `test_i3_verifier.py` | `ec137bfe855b0cf468b0d13965388fbf0c256d16ab1915a00e9b6347f3c435ca` |

## 11. Tests and single-point reversals

§9.2 rows 90–105 map every required property to named tests. Each reversal below
deliberately breaks one guard, either by editing the module's syntax tree and
executing the result or by swapping in a primitive. The test then shows the
unsafe outcome the guard prevents, and the unmodified code shows the safe
outcome.

| Guard | Reversal | Unsafe outcome shown |
|---|---|---|
| command-line arm | the early return deleted | the verifier is armed from the absent flag and still refuses; no read, no write |
| in-code gate | `_require_armed` emptied | the CLI without the flag still writes nothing; an unarmed verifier without the gate **writes** |
| precondition admission | `parse_policy` always returns `1` | a policy-`0` host is written to |
| exclusive publication | `linkat` replaced by a rename onto the name | an occupant's bytes are destroyed |
| mask classification | `CapEff` read from `CapBnd` | an effective capability the process lacks is reported |
| identity comparison | `_same_object` accepts any object | a foreign file is removed |
| residue enforcement | `final_status` ignores accounting | a run with residue reports `failed-no-residue` |

Row 101 injects a failure at each of 20 state boundaries, from the exclusive
open to both `rmdir` calls. Each run is checked to be non-success and to have
accounting that matches the disk.

## 12. Checks not run, and why

* **Anything on `oracle-test`.** The restriction forbids it. This pass produced
  no PostgreSQL evidence and no target evidence. The local models confirm no
  target fact, so V8, I2, I3 and I8 all remain open.
* **The full bot and web suites and the Foundry tests.** They are outside this
  assignment's required set. Only the static-asset file I touched was run.
* **Formatter, linter and type checker.** None is configured.
* **A real root or a real `ubuntu` run.** The suite resolves every reviewed
  account to the test process's own ids. Real `fchown` to uid 0, real root
  capability masks and the real `freedomlab` group were therefore never
  exercised.

## 13. Rollback

This pass is repository-only, and rollback does not touch any host.

1. Delete the three new files and this handback.
2. Revert the edits listed in §8, using `git diff` on each file. Each of those
   files also carries earlier uncommitted work, so revert only this pass's hunks.
3. Regenerate the two artifacts through the same dry-run command.
4. Remove the top entry of `docs/review/Handover information`.

## 14. Unresolved questions and discrepancies — reported, not changed

1. **`R`'s mode from `mkroot`.** The ruling and r6 C1 say `R` is `0700`.
   `case_program.ROOT_DIRECTORY_MODE` and the concrete plan's `mkroot` read-back
   create and assert `0755`. The verifier follows the ruling. The concrete
   plan's value predates this pass and is unchanged, because reconciling it was
   not assigned. **Maintainer decision needed.**
2. **P2's temporary creation mode.** r6 §1.4.2 says `openat(…, 0500)`, but
   `executor.install_case_program` creates the temporary through `create_file`
   at `0600` before `fchmod 0555`. The final mode is unaffected. The difference
   is noted, not changed.
3. **Capability admission uses no exact values** (§5). If the maintainer wants
   exact-mask admission for either identity, that requires reviewed values,
   which are the E7 facts and a `ubuntu` statement.
4. **§2.3.3 is exercised in V5 itself.** The real publication happens in
   `V5/<run-id>`, which is the same directory type, identity, filesystem and
   mount one level down. The assignment names V5, so V5 is what the verifier
   uses.
5. **The host check includes kernel release and architecture** from
   `APPROVED_TARGET_FACTS`. If the target's kernel has changed since
   2026-09-05, the verifier refuses `target-mismatch`. That is fail-closed, but
   it is my reading of "exact target".
6. **Registers are not updated.** The status, RAID, decision and change
   registers, §20 and the disposable-server banner are the maintainer's to
   update after review. The banner's sentence that the implementation "has not
   yet been reconciled" is now out of date.

**Proposed RAID item, not recorded.** LAB-I3-3 (Issue, Technical Lead): the
`mkroot` `0755` versus C1 `0700` discrepancy in item 1.

## 15. Reviewer focus

1. Whether factoring `linkat` out of `renameat(noreplace=True)` keeps one
   primitive with unchanged guarantees for T1, T6, §2.3.3 and P2 (§3).
2. The admission set (§4). Does anything a controlled write needs remain
   unobserved? Is the no-value capability admission (§5) acceptable?
3. Cleanup's first-causal-failure rule and the `failed-no-residue` /
   `failed-operator-attention` split in `final_status`. Should any other
   failure count as operator attention?
4. That the verifier holds `/var/lib` under its own role, `i3-state-parent`,
   rather than `plan.EVIDENCE_ROLE`, and that this is consistent with
   decision D.
5. Discrepancies 1 and 2 in §14.
6. Whether the evidence the entry point prints is sufficient for a later I3
   closure decision.
