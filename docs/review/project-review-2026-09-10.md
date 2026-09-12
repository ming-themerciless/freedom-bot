# Independent project review — 2026-09-10

Disposition: **changes requested** for the active C-8 revision-3 design. Technical acceptance and execution approval are withheld. EH-R16-1 remains open; Package 5.0 remains not ready, P5.0-R5 Blocking and OD-62 Open.

Scope: the current working tree, with detailed review concentrated on the active handover's C-8 design, its source contracts and synthetic evidence. This is not a complete security audit of every project component or a package-gate approval. Existing user changes were preserved.

## PR-20260910-1 — Blocking: staged restoration reintroduces source substitution

Location: `phase-5-0-evidence-harness-c8-ownership-design-r16-3.md`, lines 435–440, with the source-binding claim in §5 C-4 and the R-C8-5 disposition.

The proposed materializer writes verified bytes to an exclusively created temporary file, then publishes it with pathname-based `rename`. A writer to the containing directory can unlink that temporary name and put another file there after the write/fsync but before rename. The descriptor still references the original file; rename consumes the replacement. The declared `postgres` directory owner can perform this substitution without changing the live destination first. Consequently arbitrary substituted bytes, not necessarily the held buffer, can become the live authentication configuration. Atomic publication does not establish source integrity. This exceeds R-C8-5's stated consequence of publishing known-good bytes over the wrong destination.

This conclusion follows from the documented pathname semantics of [rename(2)](https://man7.org/linux/man-pages/man2/rename.2.html) and descriptor semantics of [open(2)](https://man7.org/linux/man-pages/man2/open.2.html); it is a design inference, not a host exploit test.

Required correction: specify custody of the staged source through publication, including directory writers and in-place changes. Assess protected staging/exclusion and destination handling together. Add an injected replacement after successful staged write/fsync and before publication, asserting the exact bytes published. Retain an uninterrupted successful control. Do not describe the remaining exposure as destination substitution alone.

## PR-20260910-2 — Blocking: root guards suppress independently available configuration recovery

Location: the same design, lines 474–489 and §10.2 cases 18–19.

G-1 deliberately retains verified originals in the executor and restores from those bytes, independently of the disposable root. G-2 nevertheless declares RESTORE, RELOAD and VERIFY root-dependent and skips them on a mismatching root guard. If the root is replaced after B6-M1/B6-M2, the proposed rule leaves modified PostgreSQL authentication in place even though verified originals remain available. Cases 18–19 similarly demand no restoration when an obsolete disk capture changes, contradicting the held-buffer contract.

Required correction: give held-buffer recovery its own source and destination prerequisites. Refuse operations on the substituted root while allowing independently safe restoration, reload and verification. Specify separate behavior for missing/unverified buffers. Correct the test matrix and add a root replacement after configuration mutation with a valid held-buffer recovery control. Resolve finding 1's publication custody before claiming this recovery safe.

## PR-20260910-3 — Important: G-0 relies on a nonexistent parent descriptor

Location: the same design, lines 363–366 and §7.1's syscall inventory; `tools/phase_5_0_evidence/execution/case_program.py`, `_do_mkroot`, lines 562–608.

The design says parent facts come from a descriptor that mkroot already opens. The implementation calls `os.mkdir(path)` and opens only the newly named root. Its fstat reports the child, not the parent. Adding fstat to that descriptor cannot establish the proposed parent ownership, permissions or identity. The claimed interface/syscall inventory therefore omits a required lookup and its binding to creation.

Required correction: define acquisition and validation of the parent reference, when it occurs relative to creation, how creation is tied to that parent, and the corresponding source/syscall/observation changes. Include wrong-parent and replaced-parent model cases without claiming the create-to-identify residual is thereby eliminated.

## Evidence and limits

Independent local verification used the task-specific fallback interpreters, not the canonical oracle-test environment. `TEST_DATABASE_URL` was explicitly unset. Bot and web suites ran serially. Database skips are unverified assertions, not PostgreSQL evidence; the canonical web database run expects 80 skips rather than the 1362 seen here.

* `/opt/discord-bots/venv-web/bin/python -m pytest -q -rs` over `test_no_execution.py`, `test_r16_1_ownership_reproduction.py`, and `test_r13_remediation.py`: 263 passed.
* Same interpreter, `tests/phase_5_0_evidence`: 1391 passed. Passing defect reproductions confirm the current defect remains present.
* `/opt/discord-bots/venv/bin/python -m pytest -q -rs tests/test_*.py`: 2990 passed, 326 skipped, one warning.
* `/opt/discord-bots/venv-web/bin/python -m pytest -q -rs tests/web`: 1610 passed, 1362 skipped.
* `node --test 'foundry-module/tests/'*.test.mjs`: 171 passed, zero failed or skipped.
* Independently recomputed all 32 manifest source hashes: zero mismatches.
* `git diff --check`: passed before the review artifact was added; repeated at handback.

No product code or harness mechanism was changed. No SSH, synchronization, host preflight, database execution, privileged vectors, service changes or deployment occurred. No formatter, linter, type checker or compileall was run in this documentation-only review. No execution digest is approved. The evidence-label improvements are useful, but neither their passing tests nor this review closes EH-R16-1 or accepts a residual.
