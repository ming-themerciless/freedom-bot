# Claude handback — C-P5.0-R5-RP11-I1 — RP-11 capture mechanism and B0-RA — 2026-09-27

**Status: returned incomplete, because the session's usage limit was reached.** The implementation and tests are done and pass. This handback is shorter than the assignment's §2.5 asks for. **The pointer updates of §2.6 were not made:** Handover, status.md, plan §20 and the disposable-server banner are unchanged. RP-11 is **not** satisfied. Neither pass is authorized, `plan.is_executable=False`, and P5.0-R5 remains Blocking. No host, SSH, network, database, `--execute`, secrets scan, commit or push occurred.

## Maintainer decisions taken during the pass (Peter Duscha, in session)

1. **P-7 publication.** Records and index states are written into an unnamed `O_TMPFILE` inode, file-synced, and then given their first and only name by one `linkat` through `/proc/self/fd/N`. The link fails with EEXIST and never replaces an entry. This is a stated deviation from P-5's "temporary name" and P-7's "rename": no temporary name ever exists.
2. **Read-only state** (§9.5.3 step 4) is a behavioural seal. No `chmod` is issued, so C-7's modes stand and X-3 stays the only write.
3. **The single `os.link` site.** `descriptors.py`'s one `os.link` call now lives in `_exclusive_link`. `PosixFilesystem.linkat` calls it with `follow=False` (unchanged behaviour). The new `link_unnamed_descriptor` calls it with `follow=True`, and refuses an inode that already has a name. `EXCLUSIVE_LINK_PRIMITIVE` is amended to say so. The I3-R2 one-link guard test passes unmodified.

## Files

- New: `tools/phase_5_0_evidence/capture_contract.py` (planning tier), `execution/capture_store.py`, `execution/capture_mechanism.py`, `execution/retention_check.py`.
- Changed: `execution/boundary.py` (adds `StreamCaptureLauncher`: pipes, no shell, raw bytes to sinks, bound enforced by kill without truncation, drain limit; unarmed by default) and `execution/descriptors.py` (item 3 above).
- `review_manifest.py`: covered set +4, `MANIFEST_VERSION` 22. The regenerated `docs/review/phase-5-0-evidence-harness-review-manifest.json` has SHA-256 `3c3a6d79…`. The regenerated `…-concrete-plan.md` has SHA-256 `4fc2e9e9…`. The review-input digest is `adeabe172a89c181a397a7df62cb46895b7b864975a18b70bb278d9d2a1f7de3`. It is review input only, and was produced by the default dry run, which executed nothing.
- Tests: new `rp11_fixtures.py`, `test_rp11_capture.py` and `test_rp11_retention.py`. Tier declarations were added in `test_no_execution.py`, with no rule relaxed. The version pin in `test_r16_remediation.py` moves 21 → 22.

## Results

Command: `env -u TEST_DATABASE_URL PYTHONDONTWRITEBYTECODE=1 /opt/freedom-blades/runtime/venv-web/bin/python -m pytest -q -rs -p no:cacheprovider` over the RP-11 suites and the directly affected structural suites (`test_no_execution`, `test_concrete_plan`, `test_r16_remediation`, `test_i3_verifier`, `test_boundary_identity`, `test_lab_integration`, `test_v6_provisioning`, `test_lab_implementation`, `test_r5_r4_s4_3_producer_reporting`). Result: **1170 passed, 0 failed, 0 skipped**. `git diff --check` on the task files is clean. The full suite was not run, as instructed.

Deliberate source mutations were each caught: no probe, *F* without unadmitted objects, merged streams, barrier retry, one-directional comparison, no second enumeration, no link-count check, and no after-read `fstat`. Two of these (the link-count and after-read checks) needed a new test each before they were caught.

## Not done / open questions for review

- The full §2.5 content: a requirement-to-test table and a platform-assumptions list. Assumptions include Linux `O_TMPFILE`, `/proc`, ext4, `st_ctime` granularity, and uid 1000 with umask 0002 locally.
- The §2.6 pointer updates.
- **C-11 is unresolved.** A wrapper invocation carrying the §5 `rsync` text would be *refused* by `guard-secrets.py`, not hidden from it. How the synchronization is issued through RP-11 is therefore still open.
- The handback binding block format needs pinning into draft §14. That is an amendment, which was not made.
- The operational environment passed to the launcher (for example, SSH agent variables) is undecided. The launcher inherits nothing.
- RP-11 tests start local processes (the current interpreter with inert arguments) through the reviewed launcher. This is permitted by the prompt, but it departs from the suite's earlier "no process" premise.
- The retention check's residual (a same-time rewrite) is stated in `retention_check.py`.

Independent Codex technical, security, operational and evidence review is required. Claude has stopped.
