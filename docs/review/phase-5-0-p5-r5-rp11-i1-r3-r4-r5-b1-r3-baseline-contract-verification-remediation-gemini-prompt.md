# Gemini prompt — `cc1.v` baseline-contract verification remediation

Work ID: `C-P5.0-R5-RP11-I1-R3-R4-R5-B1-R3`

Date: 2026-10-01

Assignee: Gemini

Status: **proposed assignment; not executable until Product Owner Peter Duscha explicitly accepts it and names Gemini as assignee**

## 1. Objective and review findings

Remediate the two findings from Codex's independent review of B1-R2 without
changing the accepted `cc1.v` fixture or expanding into B1 or R-5 execution.

### B1-R3-1 — Blocking: manifest verification bypass

`ReviewManifest.build()` currently recognizes the synthetic test value

```text
# infra/rp11-launch/verify/fixtures/cc1.v.baseline\n
```

and substitutes the trusted baseline metadata instead of verifying the supplied
bytes. Codex independently demonstrated that a 51-byte placeholder is accepted
while the manifest serializes a byte length of 5,120 and the accepted fixture
SHA-256.

This violates the B1-R2 requirement that manifest construction verify the
actual fixture bytes rather than serialize unchecked constants.

### B1-R3-2 — Blocking: required B1-R2 handback missing

B1-R2 did not create its required handback:

`docs/review/phase-5-0-p5-r5-rp11-i1-r3-r4-r5-b1-r2-baseline-contract-integration-remediation-handback.md`

The implementation therefore lacks the required scope accounting, file hashes,
commands, test totals and stop declaration.

## 2. Accepted values that must not change

The accepted diagnostic fixture is:

`infra/rp11-launch/verify/fixtures/cc1.v.baseline`

Its contract is:

- byte length: `5120`;
- SHA-256:
  `b77f92dcdcf899c5459fec606f16dc325ed5329516cbab5faea86b479992905b`.

The current review-manifest version is `29`. Codex independently regenerated
the B1-R2 output and observed:

- aggregate review-manifest digest:
  `4f0300856f1cffe1b2ad9aac6d73ddc205cfa065ebc413a5c4b14fa1913621eb`;
- checked-in manifest file SHA-256:
  `72274156d0c157e9c10220d16118d85d5e1a653d5a14a1e5598f2e6d1c006ebb`;
- checked-in concrete-plan file SHA-256:
  `3c358ce39a0367dfe4ee1ceb0b0d9008b78b075f33af0846c99da03a399a66b5`;
- focused tests: `4030 passed`; and
- `git diff --check`: clean.

These observations do not accept B1-R2. They are comparison inputs for this
remediation.

## 3. Required context

Before planning or editing, read:

1. `.agents/AGENTS.md` completely;
2. the reading map, §0, §13, §16, §17 and §20 of
   `docs/implementation-plan.md`;
3. `docs/review/Handover information`;
4. `docs/operations/disposable-test-server.md`, including its restriction
   banner;
5. the B1, B1-R1, B1-R2 prompts and available handbacks;
6. `tools/phase_5_0_evidence/review_manifest.py`;
7. `tools/phase_5_0_evidence/rp11_launch.py`;
8. the relevant tests under `tests/phase_5_0_evidence/`;
9. `tests/test_rp11_launch_gate.py`;
10. `tests/test_rp11_launch_source.py`; and
11. this assignment.

Inspect `git status` before editing. Preserve all unrelated worktree changes.

## 4. Required remediation

### 4.1 Remove the verification bypass

Change `ReviewManifest.build()` so every value supplied for
`infra/rp11-launch/verify/fixtures/cc1.v.baseline` is passed through the exact
length and SHA-256 verification contract.

Remove the synthetic-placeholder exception completely. There must be no byte
value, marker, mode, test-only flag or alternate constructor path by which
unverified fixture bytes can cause the accepted baseline metadata to be
serialized.

Do not weaken `verify_cc1_v_baseline()`. Do not introduce a mock mode or hidden
escape hatch in production code.

### 4.2 Correct test source fixtures

Update the shared test source-byte fixtures so tests that construct a complete
`ReviewManifest` supply the actual accepted baseline fixture bytes, or an
equally strict fixture loaded from that exact repository path.

Keep test setup explicit and deterministic. A test helper must not reproduce
or synthesize the accepted 5,120-byte content from constants.

Add regression tests proving:

1. the former 51-byte synthetic placeholder is rejected;
2. arbitrary bytes of the correct length are rejected;
3. actual accepted fixture bytes are accepted;
4. the serialized path, length and digest come from a successfully verified
   fixture contract; and
5. all existing missing, mutation, append, truncation, wrong-length and
   wrong-digest tests still pass.

### 4.3 Complete the missing record

Create the B1-R2 handback required by the accepted B1-R2 assignment:

`docs/review/phase-5-0-p5-r5-rp11-i1-r3-r4-r5-b1-r2-baseline-contract-integration-remediation-handback.md`

It must accurately describe the B1-R2 work as originally performed and must
include a dated B1-R3 review correction note stating:

- the original implementation contained the synthetic-placeholder bypass;
- the original B1-R2 handback was omitted;
- B1-R2 was not accepted by Codex;
- the B1-R3 correction removes the bypass; and
- no claim of B1-R2 or R-5 acceptance is made.

Do not retroactively claim that the original B1-R2 implementation satisfied
the actual-byte verification requirement.

## 5. Manifest and version discipline

The correction changes verification behavior and covered source bytes.
Determine the required manifest-version treatment from the existing manifest
contract and document it explicitly.

Unless the governing contract demonstrably requires otherwise:

- increment `MANIFEST_VERSION` from `29` to `30`;
- document that version 30 removes a bypass under which unverified placeholder
  bytes could be represented by accepted baseline metadata;
- regenerate the checked-in review manifest and concrete plan using the
  canonical dry-run/render command; and
- update directly affected exact version and digest assertions.

Do not change:

- the fixture bytes, length or digest;
- `infra/rp11-launch/expected.sha256`;
- the four normative launcher-output digests;
- the static launcher source or build inputs;
- `plan.is_executable=False`;
- RP-11's unwired/unmet state; or
- any execution authority.

If the governing contract indicates that a version increment would be wrong,
stop and explain the conflict in a partial handback rather than silently
retaining version 29.

## 6. Authorized files

Gemini may modify only:

- `tools/phase_5_0_evidence/review_manifest.py`;
- test fixtures and directly affected tests under
  `tests/phase_5_0_evidence/`;
- `docs/review/phase-5-0-evidence-harness-review-manifest.json`;
- `docs/review/phase-5-0-evidence-harness-concrete-plan.md`;
- directly affected current-state text in:
  - `docs/implementation-plan.md`;
  - `docs/project-management/status.md`;
  - `docs/review/Handover information`;
- archive snapshots and indices only where required by the established archive
  procedure;
- directly affected entries in:
  - `docs/project-management/change-log.md`;
  - `docs/project-management/decision-register.md`;
- the missing B1-R2 handback named in §4.3; and
- the B1-R3 handback required by §9.

Do not modify `tools/phase_5_0_evidence/rp11_launch.py` unless removing the
bypass demonstrably requires correcting a defect there. If such a change is
necessary, explain it before making any broader architectural change and record
it precisely in the handback.

Do not modify the baseline fixture, `expected.sha256`, launcher build inputs or
any unrelated file.

## 7. Authority and restrictions

This is a repository-only remediation. It authorizes only the reads, bounded
edits, dry-run generation and local tests specified here.

It does **not** authorize:

- changing the accepted fixture;
- provisioning or reusing a build root;
- executing `provision.py`, `enter.py build`, IC-1, B1 or R-5;
- inspecting or changing retained B1 `/tmp` evidence;
- `oracle-test`, SSH, rsync or other remote-host access;
- network access or downloads;
- `sudo`, package installation or host configuration;
- services, databases, secrets or operational paths;
- harness `--execute`;
- RP-11 wiring, H-1/H-2, PO-14 discharge or evidence-band execution;
- staging, commit, push or Git-history modification; or
- treating this work as acceptance of B1-R2, R-5 or Package 5.0.

R-5 remains stopped, Blocking, unaccepted and unauthorized throughout this
assignment. `plan.is_executable` must remain `False`; RP-11 remains unwired and
unmet; PO-9 and PO-14 remain open.

## 8. Required verification

Run, at minimum:

1. the complete `tests/phase_5_0_evidence` suite;
2. `tests/test_rp11_launch_gate.py`;
3. `tests/test_rp11_launch_source.py`;
4. `tests/test_rp11_launch_toolchain.py` only if it requires no provisioning,
   remote access or unaccepted build root;
5. a direct regression demonstrating that the former 51-byte placeholder is
   rejected by `ReviewManifest.build()`;
6. canonical dry-run manifest and concrete-plan regeneration;
7. byte-for-byte comparison of regenerated and checked-in outputs;
8. an independent hash and length check of the unchanged fixture;
9. verification that `expected.sha256` is unchanged and contains no baseline
   fixture entry;
10. applicable documentation structure and relative-link checks;
11. `git diff --check`; and
12. a final authorized-scope audit.

Use the documented repository environment with bytecode and pytest cache
creation disabled where supported. Do not install missing dependencies or
escalate privileges. Report blocked or skipped tests exactly; do not describe
them as passing.

## 9. Required B1-R3 handback

Write:

`docs/review/phase-5-0-p5-r5-rp11-i1-r3-r4-r5-b1-r3-baseline-contract-verification-remediation-handback.md`

Include:

- both finding identifiers and their disposition;
- the exact bypass removed;
- how test fixtures now provide verified baseline bytes;
- the regression proof that the former placeholder is rejected;
- every file modified or created and why;
- before/after SHA-256 for each modified non-generated file;
- previous and new manifest versions and aggregate digests;
- fixture length and SHA-256 before and after;
- `expected.sha256` SHA-256 before and after;
- exact generation and test commands with complete results;
- byte-comparison results for regenerated outputs;
- warnings, skips or environmental limitations;
- `git diff --check` result;
- final `git status --short`;
- confirmation that the two required handbacks now exist;
- confirmation that no prohibited action occurred;
- confirmation that R-5 was not performed or claimed; and
- remaining risks and the independent-review requirement.

## 10. Stop conditions

Stop and write a partial B1-R3 handback if:

- the fixture differs from the accepted length or digest;
- remediation would require changing the fixture or normative outputs;
- unverified fixture bytes can still produce accepted baseline metadata;
- manifest generation changes unrelated contract content;
- an unexplained test failure occurs;
- another agent changes an overlapping authorized file;
- work would require network, privileges, provisioning, retained-root reuse or
  remote access; or
- the work would cross an existing review gate.

After writing both required handbacks, stop. Do not begin B1, R-5 or any later
assignment.
