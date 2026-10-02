# Handback — R-5 R3 `cc1.v` Comparison Remediation

Work ID: `C-P5.0-R5-RP11-I1-R3-R4-R5-R3`

Date: 2026-10-01

Assignee: **Gemini** (independent rebuilder)

Controlling Prompt:
[`docs/review/phase-5-0-p5-r5-rp11-i1-r3-r4-r5-r3-cc1-comparison-remediation-gemini-prompt.md`](phase-5-0-p5-r5-rp11-i1-r3-r4-r5-r3-cc1-comparison-remediation-gemini-prompt.md)

Status: **Repository-only remediation completed; NO host action or rerun performed. Gemini has stopped.**

---

## 1. Requirements Implemented and Files Changed

This remediation implements all requirements of prompt `C-P5.0-R5-RP11-I1-R3-R4-R5-R3`:

1. **Conservative, Fail-Closed Byte Comparison Helper (`infra/rp11-launch/verify/cc1check.py`, §3.1):**
   - Remediated `cc1check.py` to operate directly on raw `bytes` rather than lines of decoded text.
   - Reports SHA-256 for both inputs.
   - Uses `difflib.SequenceMatcher` over raw byte sequences to compute exact differing byte offsets (`baseline_offset`, `actual_offset`), lengths (`baseline_length`, `actual_length`), and raw byte values (`baseline_bytes`, `actual_bytes`).
   - Handles arbitrary binary and non-UTF-8 bytes losslessly and safely without decoding errors or lossy replacement characters.
   - **Fails closed:** Returns `verdict = "PASS"` if and only if the byte streams are identical. For every non-identical pair, it emits a mandatory `verdict = "HARD_STOP"`.
   - **Completely removed regex-based explanation mechanisms:** Omitted all caller-provided rules, allowlists, or labels that could convert non-identical bytes into `PASS`.
   - Deterministic CLI behavior: exits 0 on identical inputs, exits 1 on differing inputs (`HARD_STOP`), and exits 2 on missing or unreadable inputs.

2. **Replaced Unsafe Tests with Strict Verification (`tests/test_rp11_launch_gate.py`, §3.2):**
   - Removed the unsafe `test_cc1check_explained_difference_permits_pass` test.
   - Added focused tests verifying:
     - Identical byte streams produce equal digests, zero differences, `PASS`, and CLI exit 0 (`test_cc1check_identical_byte_streams_produce_pass_and_cli_exit_0`).
     - One-byte substitution reports exact offset and both byte values, producing `HARD_STOP` and CLI exit 1 (`test_cc1check_one_byte_substitution_reports_exact_offset_values_and_hard_stop`).
     - Insertions and deletions, including start, middle, and EOF boundaries, report exact ranges without losing or misaligning subsequent differences (`test_cc1check_insertions_deletions_and_eof_boundaries`).
     - Non-UTF-8 bytes are compared and reported exactly (`test_cc1check_non_utf8_bytes_reported_exactly`).
     - No caller label, regex, or mechanism can turn non-identical bytes into `PASS` (`test_cc1check_no_caller_label_or_mechanism_can_produce_pass_on_non_identical_bytes`).
     - Missing or unreadable input files exit 2 without passing (`test_cc1check_missing_or_unreadable_inputs_fail`).
   - Corrected earlier orchestration tests:
     - Retained a real regression test through the `build` CLI path proving manifest mismatch prevents checkout creation and build execution (`test_cli_build_manifest_mismatch_prevents_checkout_and_build`).
     - Clarified the legacy comparison as an illustrative simulation (`test_illustrative_legacy_flow_un_gated_checkout_contrast`).

3. **Amended Earlier R2 Handback Record (`phase-5-0-p5-r5-rp11-i1-r3-r4-r5-r2-orchestration-remediation-handback.md`, §3.3):**
   - Withdrew claims that the former helper performed byte-level analysis and verified causal explanations.
   - Accurately described the remediated helper's exact, conservative behavior.
   - Corrected the regression test description to distinguish the real CLI regression test from an illustrative legacy simulation.
   - Retained the accurate R-1/R-2 orchestration implementation and test verifications.
   - Stated that accepted baseline bytes remain unavailable and the `cc1.v` difference remains unresolved.
   - Retained the stopped status and fresh-rerun requirement for R-5.

---

## 2. Before / After SHA-256 for Every Changed File

| File | Before SHA-256 | After SHA-256 | Status |
|---|---|---|---|
| `infra/rp11-launch/verify/cc1check.py` | `463271949f916020d1463a81f6032e10f5f71b8f25dd9eef016d1f662745de02` | `16b784622d46150dee768e399d3e89ddb8a996111af5264928761a5bc08a4b72` | Modified |
| `tests/test_rp11_launch_gate.py` | `52dc2f8a493e4598034c84975fdc1b96e572d16e603cf899f7e11c80a4757785` | `5ae37681787d5f85c9a159f2ae94fd2d0529b630a0763f221ba604eec1d05002` | Modified |
| `docs/review/phase-5-0-p5-r5-rp11-i1-r3-r4-r5-r2-orchestration-remediation-handback.md` | `fa4c13e5aa4955b57fc68006e8853b05f2571217e997f7481ba3169fc9caeeea` | `c676ba0e7d7e63b5de4eb2df241c2a0899d0fe0c48048f9c97ca6acecc33dd36` | Modified |

*Note: `infra/rp11-launch/buildroot/enter.py` (`cf467c17df4135cc5f431a3ffe5c86afef930df3b880ae4425ad6209e397807a`) and all immutable files (`toolchain.lock`, `build-root.manifest`, `expected.sha256`, launcher source files, listing) were verified and remain strictly unmodified.*

---

## 3. Exact Byte-Difference Representation and Boundary Behavior

### Data Structure (`CC1ByteDiff`)

```python
@dataclasses.dataclass(frozen=True)
class CC1ByteDiff:
    diff_type: str        # "replace", "delete", "insert"
    baseline_offset: int  # 0-indexed byte offset in baseline
    baseline_length: int  # length in bytes (0 for pure insertion)
    baseline_bytes: bytes # exact raw byte slice
    actual_offset: int    # 0-indexed byte offset in actual
    actual_length: int    # length in bytes (0 for pure deletion)
    actual_bytes: bytes   # exact raw byte slice
    line_number: int | None = None
    line_context: str | None = None
```

### Boundary and Binary Alignment Behavior

1. **Direct Byte Operation:** `difflib.SequenceMatcher(None, baseline_bytes, actual_bytes)` is executed directly against the input `bytes` objects. Python treats `bytes` as sequences of integers (`0..255`), guaranteeing exact character-set-agnostic matching.
2. **End-of-File Boundaries:**
   - Insertion at EOF (`b"prefix"` vs `b"prefix_extra"`): produces `diff_type="insert"`, `baseline_offset=6`, `baseline_length=0`, `baseline_bytes=b""`, `actual_offset=6`, `actual_length=6`, `actual_bytes=b"_extra"`.
   - Deletion at EOF (`b"prefix_extra"` vs `b"prefix"`): produces `diff_type="delete"`, `baseline_offset=6`, `baseline_length=6`, `baseline_bytes=b"_extra"`, `actual_offset=6`, `actual_length=0`, `actual_bytes=b""`.
   - Proved by `test_cc1check_insertions_deletions_and_eof_boundaries`.
3. **Multi-Point Differences:** Multiple differences across a file do not desynchronize subsequent matching tokens. Matching blocks between differences are retained with exact indices.
4. **Non-UTF-8 Resilience:** Slices of raw `bytes` (e.g. `b"\x00\xff\xfe\x80"`) are preserved without decoding. `repr` of `bytes` is used in summary formatting, eliminating any risk of `UnicodeDecodeError` or lossy substitution characters.

---

## 4. Proof That No Non-Identical Input Can Receive `PASS`

In `infra/rp11-launch/verify/cc1check.py`:

```python
def compare_cc1_v(
    baseline_bytes: bytes,
    actual_bytes: bytes,
) -> CC1ComparisonReport:
    baseline_sha = hashlib.sha256(baseline_bytes).hexdigest()
    actual_sha = hashlib.sha256(actual_bytes).hexdigest()

    if baseline_bytes == actual_bytes:
        return CC1ComparisonReport(
            baseline_sha256=baseline_sha,
            actual_sha256=actual_sha,
            is_identical=True,
            differences=(),
            verdict="PASS",
        )

    # ... compute diffs ...

    return CC1ComparisonReport(
        baseline_sha256=baseline_sha,
        actual_sha256=actual_sha,
        is_identical=False,
        differences=tuple(diffs),
        verdict="HARD_STOP",
    )
```

1. **No Conditional Verdict Logic:** The function takes only `(baseline_bytes, actual_bytes)`.
2. **Strict Identity Requirement:** The branch returning `verdict="PASS"` is executed **only** if `baseline_bytes == actual_bytes`.
3. **Deterministic Hard Stop:** Any input where `baseline_bytes != actual_bytes` unconditionally reaches `return CC1ComparisonReport(..., verdict="HARD_STOP")`.
4. **Zero Bypass Mechanisms:** There are no function arguments, configuration options, allowlist tables, regex matching hooks, or global variables that can modify this verdict. This property is asserted in `test_cc1check_no_caller_label_or_mechanism_can_produce_pass_on_non_identical_bytes`.

---

## 5. Corrected R2 Handback Claims

[`phase-5-0-p5-r5-rp11-i1-r3-r4-r5-r2-orchestration-remediation-handback.md`](phase-5-0-p5-r5-rp11-i1-r3-r4-r5-r2-orchestration-remediation-handback.md) was amended as follows:
- **Withdrew Causal Claims:** Replaced statements claiming regex pattern matching "verified causal explanation rules" with an explicit withdrawal in Section 1 and Section 6.
- **Byte-Level Contract:** Described `cc1check.py`'s true behavior: exact byte offsets, lengths, raw byte values, and fail-closed `HARD_STOP` emission.
- **Clarified Regression vs Simulation:** Updated Section 4 to clearly present `test_cli_build_manifest_mismatch_prevents_checkout_and_build` as the actual CLI regression test, and `test_illustrative_legacy_flow_un_gated_checkout_contrast` as an illustrative legacy simulation.
- **Test Counts Updated:** Reflected the updated 15 passed gate/cc1 tests.

---

## 6. Fresh Test Results

All tests were freshly run with `/opt/freedom-blades/runtime/venv-web/bin/pytest`:

| Suite / Test | Command | Count | Result |
|---|---|---|---|
| **Orchestration Gate & cc1.v Suite** | `pytest -v tests/test_rp11_launch_gate.py` | 15 items | **15 passed in 0.10s** (exit 0) |
| **Toolchain-Free Launcher Suite** | `pytest tests/test_rp11_launch_source.py` | 634 items | **634 passed in 1.91s** (exit 0) |
| **Evidence Harness Suite** | `pytest tests/phase_5_0_evidence` | 3,370 items | **3,370 passed in 32.70s** (exit 0) |
| **Toolchain-Dependent Suite** | `pytest tests/test_rp11_launch_toolchain.py` | 12 items | **12 skipped in 0.06s** (clean skip; no local root) |
| **Total Test Verification** | Combined test run | 4,031 items | **4,019 passed, 12 skipped, 0 failed** |
| **Python Bytecode Compilation** | `python3 -m py_compile` | 2 files | **Compiled with exit 0** |
| **Whitespace & Formatting** | `git diff --check` | repository | **Clean with exit 0** |

---

## 7. Checks Not Run and Why

- **Host Rerun on `oracle-test`:** Absolutely no SSH, rsync, provisioning, package operations, or rerun on `oracle-test` was performed. Remediation Prompt §5 strictly confines this work to repository-only remediation.
- **Toolchain-Dependent Tests (`tests/test_rp11_launch_toolchain.py`):** Skipped because `RP11_LAUNCH_BUILD_ROOT` is not set locally on the development machine. Per prompt §4, all 12 skips are reported as unverified locally.
- **Platform Database Suites:** Not run, as prohibited by AGENTS.md and implementation-plan §5 (RP11 launcher has no database dependency).

---

## 8. Unresolved Baseline Evidence and Residual Trust

- **Baseline Bytes Status:** The baseline `cc1.v` bytes corresponding to Claude's recorded digest `b77f92dcdcf899c5459fec606f16dc325ed5329516cbab5faea86b479992905b` are not committed to the repository. Only the SHA-256 digest exists in historical handback documents.
- **Unresolved LD-8 Stop Condition:** Without baseline bytes, `cc1check.py` cannot compute a byte-level diff. The intermediate difference between Claude's digest and Gemini's digest (`cdc0fe118866d838a9b399d35975e7627e22b3f43e8ab2bfcdf9ed5ff19045f9`) remains an unexplained difference under LD-8.
- **Decision-Ready Options for Baseline Resolution:**
  1. *Recover Claude's Retained Bytes:* If Claude's session environment or log archive retained `build-out/cc1.v`, retrieve and check in those exact bytes.
  2. *Re-derive Reference Baseline:* Execute a reference build on an environment matching Claude's baseline host facts (`6.8.0-139-generic`, AMD EPYC-Milan, bubblewrap 0.9.0) with `--work` to preserve `build-out/cc1.v`.
  3. *Establish Committed Intermediate Specification:* If `cc1.v` is to be an auditable intermediate under LD-8, commit the baseline bytes or a deterministic diagnostic specification to the test suite so future rebuilds can run automated byte-level diffs.

---

## 9. Security, Configuration, Deployment and Rollback Implications

- **Security:** Removing regex-based pattern matching prevents unauthenticated strings or arbitrary caller metadata from turning non-identical compiler diagnostics into passing verdicts.
- **Configuration & Deployment:** No changes to environment variables, deployment scripts, systemd units, or database tables.
- **Rollback:** Entirely self-contained in repository Python helper and test files. Cleanly reversible via standard Git revert.

---

## 10. Proposed Reviewer Focus

Codex and Peter Duscha should focus review on:
1. **Strict Fail-Closed Logic:** Confirming that `compare_cc1_v` in `infra/rp11-launch/verify/cc1check.py` allows no override of `HARD_STOP` on differing bytes.
2. **Exact Byte Representation:** Verification that `CC1ByteDiff` captures exact slice offsets, lengths, and byte values.
3. **Regression Tests:** Verification of `test_rp11_launch_gate.py` test coverage and assertions.
4. **Baseline Evidence Decision:** Peter's determination on how to obtain or establish comparable baseline `cc1.v` bytes before authorizing a fresh R-5 rerun.

---

## 11. Stop Gate

In accordance with Remediation Prompt §6, Gemini **stops here**. No host action or R-5 rerun has been initiated. Gemini awaits independent review by Codex and explicit authorization from maintainer Peter Duscha.
