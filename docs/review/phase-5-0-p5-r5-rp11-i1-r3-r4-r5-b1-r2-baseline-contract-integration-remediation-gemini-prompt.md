# Gemini prompt — `cc1.v` baseline-contract integration remediation

Work ID: `C-P5.0-R5-RP11-I1-R3-R4-R5-B1-R2`

Date: 2026-10-01

Assignee: Gemini

Status: **proposed assignment; not executable until Product Owner Peter Duscha explicitly accepts it and names Gemini as assignee**

## 1. Objective

Integrate the accepted Branch A `cc1.v` baseline fixture into the project's
machine-checked evidence contract.

The retained fixture is:

`infra/rp11-launch/verify/fixtures/cc1.v.baseline`

Its independently verified identity is:

- byte length: `5120`
- SHA-256:
  `b77f92dcdcf899c5459fec606f16dc325ed5329516cbab5faea86b479992905b`

The fixture currently exists and is documented, but it is absent from the exact
launcher coverage set in `tools/phase_5_0_evidence/review_manifest.py`.
Consequently, the current review-manifest and test contract do not detect
alteration, replacement or removal of the baseline that a future R-5 comparison
would trust.

Correct that integration gap without changing the fixture, rebuilding the
launcher, reproducing B1, or executing R-5.

## 2. Required context

Before planning or editing, read:

1. `.agents/AGENTS.md` completely;
2. the reading map, §0, §13, §16, §17 and §20 of
   `docs/implementation-plan.md`;
3. `docs/review/Handover information`;
4. `docs/operations/disposable-test-server.md`, including its restriction
   banner;
5. the B1 prompt, amended B1 handback, B1-R1 prompt and B1-R1 handback;
6. `tools/phase_5_0_evidence/review_manifest.py`;
7. `tools/phase_5_0_evidence/rp11_launch.py`;
8. the relevant tests under `tests/phase_5_0_evidence/`;
9. `tests/test_rp11_launch_gate.py`;
10. `tests/test_rp11_launch_source.py`;
11. `tests/test_rp11_launch_toolchain.py`; and
12. this assignment.

Inspect `git status` before editing. The worktree contains accepted concurrent
and historical work. Preserve every unrelated change.

## 3. Required implementation

Implement an explicit, deterministic baseline contract that binds all of:

- repository-relative fixture path:
  `infra/rp11-launch/verify/fixtures/cc1.v.baseline`;
- exact byte length: `5120`; and
- exact SHA-256:
  `b77f92dcdcf899c5459fec606f16dc325ed5329516cbab5faea86b479992905b`.

The implementation must satisfy all of the following:

1. Add the fixture to the explicitly enumerated reviewed launcher coverage set.
   Do not use directory globs or implicit recursive discovery.
2. Serialize the baseline path, byte length and SHA-256 in the `rp11_launch`
   section of the review manifest, using stable field names and deterministic
   ordering.
3. Ensure manifest construction verifies the actual fixture bytes rather than
   merely serializing unchecked constants.
4. Increment `MANIFEST_VERSION` from `28` to `29`.
5. Regenerate the checked-in review manifest using the repository's canonical
   dry-run/render process.
6. Update all directly affected version, digest and contract assertions.
7. Add tests proving that the contract rejects or detects:
   - a missing fixture;
   - a one-byte mutation;
   - an appended byte;
   - a truncated fixture;
   - a wrong expected length;
   - a wrong expected digest; and
   - omission of the fixture from the reviewed coverage set.
8. Preserve exact-byte comparison as the only route by which `cc1check.py`
   returns `PASS`.
9. Preserve the distinction between:
   - the four normative launcher outputs in `expected.sha256`; and
   - `cc1.v.baseline`, which is diagnostic comparison evidence.

Do **not** add `cc1.v.baseline` to `expected.sha256`. Do not redefine it as a
normative launcher output.

If the current architecture cannot verify the fixture without a broader design
change, stop and document the conflict rather than weakening the contract or
expanding scope.

## 4. Authorized files

Subject to actual dependency analysis, Gemini may modify only:

- `tools/phase_5_0_evidence/review_manifest.py`;
- `tools/phase_5_0_evidence/rp11_launch.py`;
- directly affected tests under `tests/phase_5_0_evidence/`;
- directly affected RP-11 launcher tests under `tests/`;
- `docs/review/phase-5-0-evidence-harness-review-manifest.json`;
- `docs/review/phase-5-0-evidence-harness-concrete-plan.md`;
- the active current-state portions of:
  - `docs/implementation-plan.md`;
  - `docs/project-management/status.md`;
  - `docs/review/Handover information`;
- corresponding archive snapshots and archive indices only where the governing
  archival procedure requires them;
- `docs/project-management/change-log.md`;
- `docs/project-management/decision-register.md`; and
- the remediation handback required by §7.

Do not modify the baseline fixture itself. Before finishing, report every
modified or created file and explain why it was necessary.

If another file must change to keep an existing exact contract consistent,
stop and identify it unless the change is purely generated output from the
authorized manifest regeneration.

## 5. Authority and restrictions

This is a repository-only remediation.

It authorizes:

- reading the repository files named above;
- editing only the authorized repository files;
- deterministic local manifest generation in dry-run/render mode;
- local, non-operational tests required by §6; and
- temporary test output under a unique `/tmp` directory.

It does **not** authorize:

- changing `infra/rp11-launch/verify/fixtures/cc1.v.baseline`;
- provisioning or reusing any build root;
- executing `provision.py`, `enter.py build`, IC-1, B1 or R-5;
- comparing against or modifying retained B1 `/tmp` evidence;
- `oracle-test`, SSH, rsync or other remote-host access;
- network access or downloads;
- `sudo`, package installation or host configuration;
- services, databases, secrets or operational paths;
- harness `--execute`;
- RP-11 wiring, H-1/H-2, PO-14 discharge or evidence-band execution;
- commit, push, staging or Git-history modification; or
- treating this remediation as acceptance of B1, R-5 or Package 5.0.

R-5 remains stopped, Blocking, unaccepted and unauthorized throughout this
assignment. `plan.is_executable` must remain `False`; RP-11 remains unwired and
unmet; PO-9 and PO-14 remain open.

## 6. Required verification

Run the applicable local test commands using the documented repository
environment, with bytecode and pytest cache creation disabled where supported.

At minimum verify:

1. the full `tests/phase_5_0_evidence` suite;
2. `tests/test_rp11_launch_gate.py`;
3. `tests/test_rp11_launch_source.py`;
4. `tests/test_rp11_launch_toolchain.py` only if it can run without
   provisioning, remote access or reusing an unaccepted build root;
5. the canonical dry-run review-manifest generation;
6. exact equality between regenerated and checked-in manifest output;
7. the fixture remains exactly 5,120 bytes and retains the authorized digest;
8. relevant documentation structural/link checks;
9. `git diff --check`; and
10. a final scope audit against the authorized-file list.

If namespace restrictions or missing local dependencies prevent a test, report
the exact environmental failure. Do not install dependencies, escalate
privileges or weaken the test.

Do not represent an unrun, skipped or environmentally blocked test as passing.

## 7. Required handback

Write:

`docs/review/phase-5-0-p5-r5-rp11-i1-r3-r4-r5-b1-r2-baseline-contract-integration-remediation-handback.md`

The handback must include:

- the work ID and exact scope;
- every file modified or created;
- the previous and new manifest versions;
- the previous and new aggregate review-manifest digests;
- the serialized baseline-contract fields and values;
- confirmation that the fixture is explicitly covered;
- confirmation that actual fixture bytes are checked;
- confirmation that `expected.sha256` is unchanged;
- confirmation that the fixture itself is unchanged;
- before/after SHA-256 for each modified non-generated file;
- the exact manifest-generation command;
- every test command and its complete pass/fail/skip totals;
- any warnings or environment limitations;
- `git diff --check` result;
- final `git status --short`;
- confirmation that no build, provisioning, network, remote-host or operational
  action occurred;
- confirmation that R-5 was not performed or claimed; and
- remaining risks and the required independent-review step.

## 8. Stop conditions

Stop immediately and write a partial handback if:

- the fixture bytes, length or digest differ from the authorized values;
- implementing the contract requires changing the fixture;
- the normative launcher digests would change;
- manifest regeneration changes unrelated contract content;
- an unexplained test failure occurs;
- another agent has modified an overlapping authorized file during this task;
- execution would require network, privilege escalation, provisioning,
  retained-root reuse or remote-host access; or
- the requested work would cross an existing review gate.

After filing the handback, stop. Do not start R-5 or any subsequent assignment.
