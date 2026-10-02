# Gemini prompt — B1-R3 verification-record accuracy remediation

Work ID: `C-P5.0-R5-RP11-I1-R3-R4-R5-B1-R4`

Date: 2026-10-02

Assignee: Gemini

Status: **proposed documentation-only assignment; not executable until Product Owner Peter Duscha explicitly accepts it and names Gemini as assignee**

## 1. Objective

Correct five factual record defects found by Codex in the B1-R3 handback and
one stale test-helper module description.

The B1-R3 implementation itself passed independent technical verification:

- the synthetic-placeholder bypass is removed;
- every supplied baseline value is verified unconditionally;
- the former placeholder is rejected;
- manifest version 30 regenerates deterministically;
- the new aggregate digest is
  `28a4f4c2b7596e9042f6b12a34f5684b3499a3fafd997e306fe25f6798e8a526`;
- the fixture remains 5,120 bytes with SHA-256
  `b77f92dcdcf899c5459fec606f16dc325ed5329516cbab5faea86b479992905b`;
- `expected.sha256` is unchanged;
- Codex independently reproduced 4,034 passing tests and 12 expected
  toolchain skips; and
- `git diff --check` passes.

Do not change the accepted implementation. Correct only the record and the
stale module description specified below.

## 2. Required context

Before editing, read:

1. `.agents/AGENTS.md` completely;
2. the reading map, §0, §13, §16, §17 and §20 of
   `docs/implementation-plan.md`;
3. `docs/review/Handover information`;
4. the B1-R2, B1-R3 prompts and handbacks;
5. `tools/phase_5_0_evidence/review_manifest.py`, especially
   `ReviewManifest.build()`;
6. `tools/phase_5_0_evidence/rp11_launch.py`, especially
   `verify_cc1_v_baseline()` and its constants;
7. `tests/phase_5_0_evidence/test_concrete_plan.py`, especially the B1-R3
   regression tests;
8. `tests/phase_5_0_evidence/harness_fixtures.py`; and
9. this assignment.

Inspect `git status` and preserve every unrelated change.

## 3. Required corrections

### 3.1 Correct the former-placeholder description

In the B1-R3 handback, describe the actual removed bypass exactly.

The former special-case value was:

```python
f"# {rp11_launch.CC1_V_BASELINE_PATH}\n".encode("utf-8")
```

For the accepted path, this produces the 51-byte value:

```python
b"# infra/rp11-launch/verify/fixtures/cc1.v.baseline\n"
```

Do not describe it as:

```python
b"synthetic cc1.v.baseline fixture bytes for testing\n"
```

Correct every occurrence in the handback, including the executive summary,
finding table, removed-code description and regression-test description.

### 3.2 Correct exception, constant and return-type descriptions

The actual contract is:

- `verify_cc1_v_baseline()` raises `PlanRefused`, not `ValueError`, for length
  or digest mismatches;
- the length constant is `CC1_V_BASELINE_LENGTH`, not the nonexistent
  `CC1_V_BASELINE_SIZE_BYTES`;
- `verify_cc1_v_baseline()` returns a dictionary containing `byte_length`,
  `path` and `sha256`; it does not return an object with `.path`, `.sha256` or
  `.byte_length` attributes; and
- `ReviewManifest.build()` now assigns the verified dictionary directly:

  ```python
  baseline_contract = rp11_launch.verify_cc1_v_baseline(baseline_bytes)
  ```

Correct all prose and illustrative code accordingly. Do not invent or
reconstruct code that was not present.

### 3.3 Correct the previous aggregate digest

Replace the incorrect version-29 previous aggregate digest with the
independently verified value:

`4f0300856f1cffe1b2ad9aac6d73ddc205cfa065ebc413a5c4b14fa1913621eb`

Retain the independently reproduced version-30 digest:

`28a4f4c2b7596e9042f6b12a34f5684b3499a3fafd997e306fe25f6798e8a526`

### 3.4 Correct the affected test-module count

The B1-R3 handback says 13 test modules were updated but lists 14. Correct the
count to 14 after verifying the list. Do not add or remove files merely to make
the count fit.

### 3.5 Preserve the assigned finding severity

The accepted B1-R3 prompt classified both `B1-R3-1` and `B1-R3-2` as Blocking.
The B1-R3 handback changed `B1-R3-2` to Important without authority.

Restore `B1-R3-2` to Blocking everywhere it is classified. Its disposition may
remain Closed as remediated because the missing B1-R2 handback now exists.

### 3.6 Correct the stale test-helper module description

`tests/phase_5_0_evidence/harness_fixtures.py` says that nothing in the module
touches a file. The newly added `load_test_source_bytes()` reads the covered
repository source files, including the accepted baseline fixture.

Narrow the module description so it accurately states that:

- it performs no host, operational or target-system inspection;
- it starts no process and opens no socket;
- its only file reads are deterministic reads of the repository files in
  `COVERED_SOURCES` for test-fixture construction; and
- this repository-file access is exercised under the test suite, not an
  execution boundary or operational run.

Do not change `load_test_source_bytes()` or any executable behavior.

## 4. Authorized files

Gemini may modify only:

- `docs/review/phase-5-0-p5-r5-rp11-i1-r3-r4-r5-b1-r3-baseline-contract-verification-remediation-handback.md`;
- the module-level explanatory docstring in
  `tests/phase_5_0_evidence/harness_fixtures.py`; and
- the B1-R4 handback required by §7.

No other file is authorized. Do not modify the B1-R2 handback, prompt files,
manifest, concrete plan, production or planning code, test behavior, governance
documents, archives, launcher files or fixture.

## 5. Authority and restrictions

This assignment authorizes documentation corrections only. The
`harness_fixtures.py` change is restricted to its module-level explanatory
docstring.

It does **not** authorize:

- implementation or test-behavior changes;
- a manifest-version change or manifest regeneration;
- changing any digest-bearing artifact;
- changing the baseline fixture or `expected.sha256`;
- provisioning, building, B1 reproduction, IC-1 or R-5;
- retained `/tmp` evidence access;
- `oracle-test`, SSH, rsync, network access or downloads;
- `sudo`, packages, host configuration, services or databases;
- harness `--execute`;
- RP-11 wiring or any operational action;
- staging, commit, push or Git-history modification; or
- accepting B1-R3, R-5 or Package 5.0.

R-5 remains stopped, Blocking, unaccepted and unauthorized.
`plan.is_executable` remains `False`; RP-11 remains unwired and unmet; PO-9 and
PO-14 remain open.

## 6. Required verification

Perform only the following bounded checks:

1. inspect the final diff for the two authorized existing files;
2. verify the final handback contains neither
   `CC1_V_BASELINE_SIZE_BYTES` nor the false placeholder text
   `synthetic cc1.v.baseline fixture bytes for testing`;
3. verify it consistently names `PlanRefused` for baseline length/digest
   refusal;
4. verify it contains the exact previous and current aggregate digests from
   §3.3;
5. verify it classifies both findings as Blocking and records their remediated
   disposition;
6. verify the affected-module count and enumerated list both equal 14;
7. run the repository's relevant documentation/AST hygiene check for
   `harness_fixtures.py` if one exists, without changing test behavior;
8. run `git diff --check` limited to the three authorized files; and
9. perform a final authorized-scope audit.

Do not rerun the full 4,034-test suite merely for these prose corrections. Do
not claim tests that were not run. Preserve Codex's independently reproduced
test result as historical review evidence, not as a new Gemini run.

## 7. Required handback

Write:

`docs/review/phase-5-0-p5-r5-rp11-i1-r3-r4-r5-b1-r4-verification-record-accuracy-remediation-handback.md`

Include:

- work ID and scope;
- exact before/after wording for each of the six corrections;
- every modified or created file;
- SHA-256 before and after for the amended B1-R3 handback and
  `harness_fixtures.py`;
- SHA-256 of the new B1-R4 handback;
- commands actually run and their results;
- `git diff --check` result;
- final `git status --short`;
- confirmation that implementation, tests, fixture, manifest, concrete plan,
  manifest version and digests were not changed;
- confirmation that no prohibited action occurred;
- confirmation that R-5 was not executed or claimed; and
- the required independent-review and Product Owner acceptance steps.

## 8. Stop conditions

Stop and write a partial handback if:

- any correction would require executable-code or test-behavior changes;
- any digest-bearing artifact changes;
- the fixture, `expected.sha256`, manifest or concrete plan changes;
- another agent changes either authorized existing file during the task;
- network, privileges, provisioning, retained evidence or remote access would
  be required; or
- the work would cross an existing review gate.

After writing the B1-R4 handback, stop. Do not begin R-5 or another assignment.
