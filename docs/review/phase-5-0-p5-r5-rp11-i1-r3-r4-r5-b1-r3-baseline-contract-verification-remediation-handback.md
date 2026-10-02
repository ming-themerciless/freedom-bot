# Phase 5.0 R-5 RP-11 I-1 R-3 R-4 R-5 B1-R3 Baseline Contract Verification Remediation Handback

- **Work ID:** `C-P5.0-R5-RP11-I1-R3-R4-R5-B1-R3`
- **Date:** 2026-10-01
- **Assignee:** Gemini
- **Requester / Authority:** Peter Duscha, Product Owner and Acceptance Authority
- **Assignment Prompt:** [`docs/review/phase-5-0-p5-r5-rp11-i1-r3-r4-r5-b1-r3-baseline-contract-verification-remediation-gemini-prompt.md`](phase-5-0-p5-r5-rp11-i1-r3-r4-r5-b1-r3-baseline-contract-verification-remediation-gemini-prompt.md)
- **Status:** Complete; stop after producing both required handbacks; R-5 not executed.

---

## 1. Executive Summary

This handback reports the completion of the baseline contract verification remediation under assignment `C-P5.0-R5-RP11-I1-R3-R4-R5-B1-R3`. Both review findings raised against B1-R2 are remediated in full:

1. **Finding `B1-R3-1` (Blocking):** Remediated. The synthetic-placeholder bypass in `ReviewManifest.build()` has been removed. All `cc1.v.baseline` fixture bytes must now satisfy exact byte length (5,120) and exact SHA-256 (`b77f92dcdcf899c5459fec606f16dc325ed5329516cbab5faea86b479992905b`) verification unconditionally via `rp11_launch.verify_cc1_v_baseline(baseline_bytes)`. No synthetic bytes or placeholders can ever be represented by accepted baseline metadata.
2. **Finding `B1-R3-2` (Blocking):** Remediated. The missing B1-R2 handback has been authored and placed at [`docs/review/phase-5-0-p5-r5-rp11-i1-r3-r4-r5-b1-r2-baseline-contract-integration-remediation-handback.md`](phase-5-0-p5-r5-rp11-i1-r3-r4-r5-b1-r2-baseline-contract-integration-remediation-handback.md) with a prominent dated B1-R3 review correction note documenting the bypass defect and its remediation.

Additionally:
- Shared test source-byte fixtures in `tests/phase_5_0_evidence/harness_fixtures.py` were updated to load real fixture bytes from `infra/rp11-launch/verify/fixtures/cc1.v.baseline` via `load_test_source_bytes()`. All 14 test files in `tests/phase_5_0_evidence/` that previously defined or used 51-byte synthetic placeholders now use `load_test_source_bytes()`.
- Four regression tests were added to `tests/phase_5_0_evidence/test_concrete_plan.py` directly proving that:
  - The former 51-byte synthetic placeholder (`b"# infra/rp11-launch/verify/fixtures/cc1.v.baseline\n"`) is rejected with `PlanRefused` (invalid length 51 != 5120);
  - Arbitrary bytes of the correct length (5,120) are rejected with `PlanRefused` (SHA-256 mismatch);
  - Actual fixture bytes (5,120 bytes, matching SHA-256) are accepted;
  - Serialization produces the verified contract matching `rp11_launch.CC1_V_BASELINE_SHA256` and `rp11_launch.CC1_V_BASELINE_LENGTH`.
- Manifest version advanced from 29 to 30. Review manifest and concrete plan were regenerated deterministically using the canonical CLI invocation and verified byte-for-byte with `cmp`.
- Complete test suite passes: 4,034 passed, 12 toolchain-dependent skips (cleanly skipped due to lack of unaccepted build root).
- `git diff --check` passes cleanly with exit code 0.
- Both required handbacks (`B1-R2` and `B1-R3`) exist in `docs/review/`.
- No remote access, build root, network access, or R-5 execution occurred. R-5 remains stopped, Blocking, and unaccepted.

---

## 2. Finding Dispositions

| Finding ID | Severity | Description | Disposition | Evidence / Notes |
|---|---|---|---|---|
| **B1-R3-1** | Blocking | `ReviewManifest.build()` contained a bypass allowing a 51-byte synthetic placeholder (`b"# infra/rp11-launch/verify/fixtures/cc1.v.baseline\n"`) to bypass hash and length verification while serializing the real SHA-256 digest and length into the manifest contract. | **Closed, remediated** | Bypass eliminated from `tools/phase_5_0_evidence/review_manifest.py`. Unconditional call to `rp11_launch.verify_cc1_v_baseline(baseline_bytes)` enforced. 4 regression tests prove rejection of placeholder and arbitrary bytes. |
| **B1-R3-2** | Blocking | B1-R2 handback document was missing from the repository. | **Closed, remediated** | [`phase-5-0-p5-r5-rp11-i1-r3-r4-r5-b1-r2-baseline-contract-integration-remediation-handback.md`](phase-5-0-p5-r5-rp11-i1-r3-r4-r5-b1-r2-baseline-contract-integration-remediation-handback.md) created, including the required dated B1-R3 correction note. |

---

## 3. Detailed Technical Remediation

### 3.1 Exact Bypass Removed

In `tools/phase_5_0_evidence/review_manifest.py`, `ReviewManifest.build()` previously recognized the 51-byte synthetic test value produced by `f"# {rp11_launch.CC1_V_BASELINE_PATH}\n".encode("utf-8")` (`b"# infra/rp11-launch/verify/fixtures/cc1.v.baseline\n"`) and substituted trusted metadata instead of verifying the supplied bytes:

```python
# FORMER CODE (REMOVED):
if baseline_bytes == f"# {rp11_launch.CC1_V_BASELINE_PATH}\n".encode("utf-8"):
    baseline_contract = {
        "path": rp11_launch.CC1_V_BASELINE_PATH,
        "sha256": rp11_launch.CC1_V_BASELINE_SHA256,
        "byte_length": rp11_launch.CC1_V_BASELINE_LENGTH,
    }
else:
    baseline_contract = rp11_launch.verify_cc1_v_baseline(baseline_bytes)
```

This bypass allowed callers (such as unit tests) to supply unverified placeholder bytes while receiving a serialized manifest containing the authoritative length and SHA-256 digest.

This conditional bypass was removed completely; `ReviewManifest.build()` now assigns the verified dictionary directly from unconditional verification:

```python
# CURRENT CODE:
baseline_contract = rp11_launch.verify_cc1_v_baseline(baseline_bytes)
```

If `baseline_bytes` does not exactly match length 5,120 and SHA-256 `b77f92dcdcf899c5459fec606f16dc325ed5329516cbab5faea86b479992905b`, `rp11_launch.verify_cc1_v_baseline` immediately raises `PlanRefused`.

### 3.2 Test Fixtures and Shared Sources

In `tests/phase_5_0_evidence/harness_fixtures.py`:
- Added `load_test_source_bytes()` which reads the actual committed `cc1.v.baseline` fixture bytes directly from the repository at `REPOSITORY_ROOT / rp11_launch.CC1_V_BASELINE_PATH`.
- Verified that `load_test_source_bytes()[rp11_launch.CC1_V_BASELINE_PATH]` returns the 5,120-byte verified fixture.

Updated 14 test modules across `tests/phase_5_0_evidence/` that previously defined or used local synthetic placeholder constants (`f"# {rp11_launch.CC1_V_BASELINE_PATH}\n".encode("utf-8")`, evaluating to `b"# infra/rp11-launch/verify/fixtures/cc1.v.baseline\n"`):
- `test_capture_refusal.py`
- `test_concrete_plan.py`
- `test_executor.py`
- `test_executor_cleanup.py`
- `test_expectations.py`
- `test_lab_call_graph.py`
- `test_lab_live_authority.py`
- `test_late_binding.py`
- `test_no_execution.py`
- `test_r13_remediation.py`
- `test_r14_remediation.py`
- `test_r16_1_ownership_reproduction.py`
- `test_r16_c6_c7_c8.py`
- `test_root_identity.py`

All tests now obtain test source bytes via `load_test_source_bytes()`.

### 3.3 Regression Proofs

In `tests/phase_5_0_evidence/test_concrete_plan.py`, four regression tests were added:

1. `test_baseline_contract_rejects_former_51_byte_synthetic_placeholder`:
   Supplies `f"# {rp11_launch.CC1_V_BASELINE_PATH}\n".encode("utf-8")` (`b"# infra/rp11-launch/verify/fixtures/cc1.v.baseline\n"`, 51 bytes) to `ReviewManifest.build()` and `rp11_launch.verify_cc1_v_baseline()` and asserts `pytest.raises(PlanRefused, match="length 51 does not match expected length 5120")`.
2. `test_baseline_contract_rejects_arbitrary_bytes_of_correct_length`:
   Supplies 5,120 null bytes `b"\x00" * rp11_launch.CC1_V_BASELINE_LENGTH` to `ReviewManifest.build()` and `rp11_launch.verify_cc1_v_baseline()` and asserts `pytest.raises(PlanRefused, match="sha256.*does not match expected sha256")`.
3. `test_baseline_contract_accepts_actual_fixture_bytes`:
   Supplies actual fixture bytes from the repository to `rp11_launch.verify_cc1_v_baseline()` and `ReviewManifest.build()` and verifies successful build with `manifest.baseline_contract["sha256"] == rp11_launch.CC1_V_BASELINE_SHA256`.
4. `test_baseline_contract_serialized_from_verified_contract`:
   Verifies that `manifest.as_mapping()["rp11_launch"]["cc1_v_baseline"]` correctly serializes the verified path, sha256, and byte length.

---

## 4. Manifest and Output Regeneration

`MANIFEST_VERSION` was incremented from 29 to 30 with documented rationale.

### 4.1 Canonical Regeneration Command

```bash
python3 -m tools.phase_5_0_evidence.execution.cli \
  --manifest-out docs/review/phase-5-0-evidence-harness-review-manifest.json \
  --render docs/review/phase-5-0-evidence-harness-concrete-plan.md
```

### 4.2 Aggregate Review Manifest Digests and Versions

- **Previous Manifest Version:** 29
- **Previous Aggregate Digest:** `4f0300856f1cffe1b2ad9aac6d73ddc205cfa065ebc413a5c4b14fa1913621eb`
- **New Manifest Version:** 30
- **New Aggregate Digest:** `28a4f4c2b7596e9042f6b12a34f5684b3499a3fafd997e306fe25f6798e8a526`

### 4.3 Deterministic Output Verification

Regenerated outputs were written to temporary paths and compared against checked-in files via `cmp`:
- `docs/review/phase-5-0-evidence-harness-review-manifest.json`: byte-for-byte identical (0 byte differences).
- `docs/review/phase-5-0-evidence-harness-concrete-plan.md`: byte-for-byte identical (0 byte differences).

---

## 5. Fixture and Contract Verification

### 5.1 Baseline Fixture (`infra/rp11-launch/verify/fixtures/cc1.v.baseline`)

- **Length before:** 5,120 bytes
- **Length after:** 5,120 bytes (unchanged)
- **SHA-256 before:** `b77f92dcdcf899c5459fec606f16dc325ed5329516cbab5faea86b479992905b`
- **SHA-256 after:** `b77f92dcdcf899c5459fec606f16dc325ed5329516cbab5faea86b479992905b` (unchanged)

### 5.2 Expected Launcher Outputs (`infra/rp11-launch/expected.sha256`)

- **SHA-256 before:** `6e87a54207f7f7aa3392fcd61f2f1c3303c0c7823fb1ef746dd28f5527a83625`
- **SHA-256 after:** `6e87a54207f7f7aa3392fcd61f2f1c3303c0c7823fb1ef746dd28f5527a83625` (unchanged)
- **Entries in file:** Exactly 4 entries (`rp11-launch`, `rp11-launch.x86_64.listing`, `rp11-launch.map`, `launch.s`). Contains no baseline fixture entry.

---

## 6. Files Created and Modified

### 6.1 Modified Non-Generated Files and SHA-256 Hashes

| File Path | SHA-256 Before (`HEAD`) | SHA-256 After (Working Tree) | Rationale |
|---|---|---|---|
| `tools/phase_5_0_evidence/review_manifest.py` | `be0dd079980530f24cad39acc21efb4067b6d6fa7cf140a52a03526de1f05117` | `311f1d0300e3e98f5b3b33ea6c4598bfc744ad8e9ba61bf0d2adb2d62f5c1844` | Advance `MANIFEST_VERSION` to 30; eliminate synthetic placeholder bypass; make `baseline_contract` non-optional |
| `tests/phase_5_0_evidence/harness_fixtures.py` | `a8a34f1f51202187c6697d2b4036857bc5b485afb6f9bb5a6aefe1462d94902c` | `1361d9cc36265607338b323a11a4c6ebef5e072af52d1cbf9ea77096fdd82a1b` | Add `load_test_source_bytes()` reading actual fixture bytes |
| `tests/phase_5_0_evidence/test_concrete_plan.py` | `29f49774146c5ca27b5ff391c4fce5b362bd307ddf52df211e501be5b2731eb8` | `1055fdb2a33686a7b6da93ad48b1a6550f6d5a925c1aefefea21579264fd7e2f` | Use `load_test_source_bytes()`; add 4 baseline contract regression tests |
| `tests/phase_5_0_evidence/test_capture_refusal.py` | `f44f8f46e5fcb5250a17b2537935d7bc929f35215a302c96435f7b283d1d071d` | `cdbceeb8ad81b839c8261937806ebe535eab8422085dbd4bc805dec0b4079d1e` | Use `load_test_source_bytes()` |
| `tests/phase_5_0_evidence/test_executor.py` | `78f452125d6768bf630f15e7673e04e07a3d305f3c1666fd24038dbd2ffdaf0c` | `fa96ca291e842f0850cbf865b03feab56486ba046ee5f365cca869fea17e9367` | Use `load_test_source_bytes()` |
| `tests/phase_5_0_evidence/test_executor_cleanup.py` | `e9d638b8753efd862a750d3871c819a6dbb3b1c5ab3da2671ba2dd1c8e9ef168` | `4a470dcb2671c1d00a554dc2e61323660351f54817809b78fe0986bfe611f41c` | Use `load_test_source_bytes()` |
| `tests/phase_5_0_evidence/test_expectations.py` | `b97ce67d7495d2e1c3439c77cb33cdc2192d47d3c4d529fd8db274bd8cfd4d3f` | `76fa300f9fc1cc9e5683bd9a33fdc4700e4d051000e3b1ce4ed55e74ead3744b` | Use `load_test_source_bytes()` |
| `tests/phase_5_0_evidence/test_lab_call_graph.py` | `fbae594f44079cd7b0c4c1811c045b54b986c4f22675830600cd7384b7c5619c` | `5b3cc921d23b9e64331f3bd526c7bd6fa7b0875fe590657432462ed4cecc7fbe` | Use `load_test_source_bytes()` |
| `tests/phase_5_0_evidence/test_lab_live_authority.py` | `98b03ae15144a8558d0e93a5347d15460fe50a6ccb5953eec5d179397a922c1a` | `6e73bed3d02a3e10a7fd7d472a86252f4df009708f7d1487327f4fde736dc3cc` | Use `load_test_source_bytes()` |
| `tests/phase_5_0_evidence/test_late_binding.py` | `54a19e2876001ab2667e4e8da1bc0a662f318948f684d0bc450a5ec527b501ab` | `431b6fb478e55bc16a9c695cfc6810e25778a1579e4789d88e7b1dc64bc41eba` | Use `load_test_source_bytes()` |
| `tests/phase_5_0_evidence/test_no_execution.py` | `76e5da9b351d40fa0a572cf93106adad2df41d95570b118fa6fb9b44f3cb3eb6` | `f2acbd0766f3af9745601769414e68f2953ef7467a4f7d07e6d3a3af246852eb` | Allow `load_test_source_bytes` in AST inspection |
| `tests/phase_5_0_evidence/test_r13_remediation.py` | `f805eee19e83edeeecefed07c4840057266e279bce3e4b384095cae6d13de58c` | `715d0292be13817fb872b9b2eb5cfd7cf2e075770f05303edaba5990d4844b4a` | Use `load_test_source_bytes()` |
| `tests/phase_5_0_evidence/test_r14_remediation.py` | `51da0c7015fedc1a1e8c41bf3c548a24c5b6a9ef4124a7457aed6aeb27f08255` | `569e4db030e6b2a695d4c3a47677e9a9fa41f71df74f6f3a9380a99da52125ef` | Use `load_test_source_bytes()` |
| `tests/phase_5_0_evidence/test_r16_1_ownership_reproduction.py` | `035e7de42776f5da09b252338589257f13b07c2884627d0b457ad5727688dfff` | `0df55163f4c216c18c1ddc769e2284d694e7b019c908fdab6f62d8919838f399` | Use `load_test_source_bytes()` |
| `tests/phase_5_0_evidence/test_r16_c6_c7_c8.py` | `80e73dd84a0b60df90c6824ae1e6365c41f888586104b170d665ba2ed4139d6a` | `7c04e82a1f1e78331ba94c4588aa132cae43783636ca5977e1274051904e5b64` | Use `load_test_source_bytes()` |
| `tests/phase_5_0_evidence/test_r16_remediation.py` | `949fba3046206a065f164b64d39843c000bd02dfac0f79622d5b205439fc7302` | `13a3817a95af04489720d8a5bc34aeed9381d2750f12c007f3a2a26e4856441e` | Update manifest version assertion to 30 |
| `tests/phase_5_0_evidence/test_root_identity.py` | `a95f3dee3a0028712ba174ee801e98a003272ff57df7411555c8b1b2517b9dc6` | `425a99db8de9f62fd88d183ad479ee08b76ce44c6da27acc9a6adb3a8af7fbc6` | Use `load_test_source_bytes()` |
| `docs/implementation-plan.md` | `4665217d8e7fdeac09034d1d3007c0da2b84a231ab788ef3c1abd3b7a4a3e225` | `a6dcd3505fa4565134fc0bd10f4fb3c6d2e44d3de4d61bfab7a494888cbdca01` | Update §20 current action text for B1-R3 |
| `docs/implementation-plan-archive/README.md` | `863aa3f9d37e9817de749c1d6117ed973bf0787c116be0ffbecb803b01540ac2` | `753ef6713c8d54a6f81bc3cc0a6ee318063fc2aca6687abf94e16b4a0c343cb1` | Index snapshot in archive README |
| `docs/project-management/status.md` | `92edb6b9a941d0bbd024be0ab3222bf7ad1d8f7dec22fdb4c8ee577f0332e859` | `ff5b1739cae31015d559fe94c62b6193999207f2424dd891428e1e2e09660212` | Update status current action for B1-R3 |
| `docs/project-management/status-archive/README.md` | `32773dd3f86d9b673863bb0de024d61f4169e73026fe366c17b5c0508849156c` | `006f1d27b5ce1f163611f9937078680b72f2058c4d9259dab32948b288ce861f` | Index status snapshot |
| `docs/review/Handover information` | `de2c5aa26705ff26354d7adfa5c4bac982e13fed3659227e0c7e816105242635` | `9731b88bd28641ee7a56ba93edf3d3d36ae9ea824c3dbc6e10f9bd6a0f4c2ead` | Update Handover active assignment for B1-R3 |
| `docs/review/handover-archive/README.md` | `9ea0bcd32be3287b662302af284bc75713566469ab46f5b7f544ef009623605c` | `a93fd9505e1f22ebd9309d233442d340a48278312f913bef4e4f8bbbf0947056` | Index Handover snapshot |
| `docs/project-management/change-log.md` | `a88f7511b487050ea5cb5baca9c261a55a75d890ced5a2e22530e6887422fb8e` | `cbe4338f291cfeec58b0b020ee221c20451c327db9067db528d5b77ed4e510cc` | Add B1-R3 change log entry |
| `docs/project-management/decision-register.md` | `cf85a21f722124dd6d1b1f4b97e96c93c96983ade43ea374b9217cadccc1978f` | `36e93043de7c1664ae05513feb281bd5448e0f6f355feead16142db105ce1911` | Add B1-R3 assignment entry |
| `docs/operations/disposable-test-server.md` | `4bb7cb83e48ace55ff9c2a8fb5ddd256298de711bfba065dfe818b0299f25877` | `e55e3eced92b2f7f8aa22b8affc9de0912d2b6db827a13cc8e5455c72901a72f` | B1 restriction banner updated in earlier B1 step |
| `docs/operations/disposable-test-server-archive/README.md` | `3f6eae4ca335b7a379402372ad4855d763f143c5803ac5af39411adbaeecdc01` | `7d885bd49dc72e761a5d884e771dfe9ffdf8e75fac668fe853e44421eb85c8fc` | B1 archive README updated in earlier B1 step |

### 6.2 Generated Output Files

- `docs/review/phase-5-0-evidence-harness-review-manifest.json`: SHA-256 `c9afaf7cd32a398e9714e39779fef522d6af053ec71cd2c403e0a4c2eaba4b5c`
- `docs/review/phase-5-0-evidence-harness-concrete-plan.md`: SHA-256 `f02b7acfa14b1c108ab53942bd3f89a9bd629eccb6c2c685419e07bf729dec3d`

### 6.3 Created Handback and Archive Files

- `docs/review/phase-5-0-p5-r5-rp11-i1-r3-r4-r5-b1-r2-baseline-contract-integration-remediation-handback.md`: SHA-256 `5990d3d2eed405e5aa91729da3c523239af988cb363df112d3411576a145eacf`
- `docs/review/phase-5-0-p5-r5-rp11-i1-r3-r4-r5-b1-r3-baseline-contract-verification-remediation-handback.md` (this file)
- `docs/implementation-plan-through-2026-10-01-r5-b1-reference-reproduction.md`: SHA-256 `4868bfb7f19224cf8b67428b22f0b687c6ef9b1379cfc99d649cc9bf3aab0c3f`
- `docs/project-management/status-through-2026-10-01-r5-b1-reference-reproduction.md`: SHA-256 `6f88525edd43721186e24f466a5818feea75da9e5e3a6efdca6a1adf758be76b`
- `docs/review/Handover-information-through-2026-10-01-r5-b1-reference-reproduction.md`: SHA-256 `4744c4e4bca100bc097574032109f79f20c2a39d7cccd12dad991794f8d00b24`

---

## 7. Test and Verification Execution

### 7.1 Test Suites

Command executed:
```bash
PYTHONDONTWRITEBYTECODE=1 /opt/freedom-blades/runtime/venv-web/bin/pytest -p no:cacheprovider \
  tests/phase_5_0_evidence \
  tests/test_rp11_launch_gate.py \
  tests/test_rp11_launch_source.py \
  tests/test_rp11_launch_toolchain.py
```

Result:
- **`tests/phase_5_0_evidence`:** 3,383 passed (includes 4 new regression tests).
- **`tests/test_rp11_launch_gate.py` & `tests/test_rp11_launch_source.py`:** 651 passed.
- **`tests/test_rp11_launch_toolchain.py`:** 12 skipped (cleanly skipped with reason: `toolchain-dependent tests require build root, compiler or bwrap`).
- **Total:** 4,034 passed, 12 skipped in 27.24s.
- **Errors / Failures:** 0.

### 7.2 Code and Diff Hygiene

Command:
```bash
git diff --check
```
Result: Exit code 0 (clean, no trailing whitespace, no merge conflicts).

---

## 8. Confirmations and Invariants

1. **Both required handbacks exist:**
   - [`docs/review/phase-5-0-p5-r5-rp11-i1-r3-r4-r5-b1-r2-baseline-contract-integration-remediation-handback.md`](phase-5-0-p5-r5-rp11-i1-r3-r4-r5-b1-r2-baseline-contract-integration-remediation-handback.md) (remediates B1-R3-2)
   - [`docs/review/phase-5-0-p5-r5-rp11-i1-r3-r4-r5-b1-r3-baseline-contract-verification-remediation-handback.md`](phase-5-0-p5-r5-rp11-i1-r3-r4-r5-b1-r3-baseline-contract-verification-remediation-handback.md) (remediates B1-R3-1 and completes prompt §9)
2. **No prohibited action occurred:**
   - No `sudo` or privilege escalation.
   - No `oracle-test`, SSH, rsync, or remote access.
   - No network access or downloads.
   - No build-root provisioning (`provision.py`), `enter.py build`, IC-1, or B1 rerun.
   - No harness `--execute`.
   - No RP-11 wiring, H-1/H-2, or operational authority created.
   - No Git commit, push, or history modification.
3. **R-5 was NOT performed or claimed:**
   - `plan.is_executable = False` remains strictly unchanged.
   - RP-11 remains unwired and unmet.
   - P5.0-R5 remains stopped, Blocking, and unaccepted.
   - Package 5.0 remains not ready.

---

## 9. Remaining Risks and Independent Review Requirement

- **Independent Review:** In accordance with repository governance, all changes are subject to independent review by Codex and acceptance by Peter Duscha before any subsequent phase or action.
- **R-5 Status:** The R-5 independent rebuild remains stopped, Blocking, and unaccepted. Execution of R-5 is not authorized.
