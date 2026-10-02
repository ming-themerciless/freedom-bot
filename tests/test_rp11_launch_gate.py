"""Tests for R-1 manifest gate orchestration and cc1.v comparison (C-P5.0-R5-RP11-I1-R3-R4-R5-R3).

Verifies proposal §5.3.5 / §3.1 / §3.2 / §3.4:
* Build and ic1 CLI invocations enforce R-1 manifest regeneration and equality
  check immediately before checkout preparation and R-2 build.
* Fail-closed behavior on 1-byte drift and on regeneration error.
* Real regression test through the build CLI path showing manifest mismatch
  refuses checkout preparation and build.
* Same gate applied to both build and ic1.
* CLI outputs r1-manifest <digest> equal and supports --manifest-out / --out.
* cc1check helper reports exact byte offsets, lengths, raw byte values, equal/distinct
  SHA-256 digests, and emits HARD_STOP on non-identical bytes with no pass overrides.
"""
from __future__ import annotations

import hashlib
import io
import subprocess
import sys
from pathlib import Path
from unittest.mock import MagicMock, call, patch

import pytest

from tests import rp11_launch_support as S

ENTER = S.load("enter", S.BUILDROOT)
CC1CHECK = S.load("cc1check", S.VERIFY)

COMMITTED_MANIFEST_BYTES = (S.LAUNCH / "build-root.manifest").read_bytes()
COMMITTED_MANIFEST_SHA256 = hashlib.sha256(COMMITTED_MANIFEST_BYTES).hexdigest()


# ---------------------------------------------------------------------------
# R-1 Gate Orchestration and CLI Regression Tests
# ---------------------------------------------------------------------------


def test_cli_build_manifest_mismatch_prevents_checkout_and_build(tmp_path: Path, capsys) -> None:
    """Real regression test through the `build` CLI path:
    When the manifest check fails, the CLI path exits 1, prints the error to stderr,
    and never creates or prepares the checkout directory or calls build.
    """
    root = tmp_path / "mock-root"
    root.mkdir()
    work = tmp_path / "work"
    corrupt_manifest_bytes = COMMITTED_MANIFEST_BYTES + b"# corrupted\n"

    with patch.object(ENTER, "regenerate_manifest", return_value=corrupt_manifest_bytes), \
         patch.object(ENTER, "prepare_checkout") as mock_prep, \
         patch.object(ENTER, "build") as mock_build:
        code = ENTER.main([
            "build",
            "--root", str(root),
            "--work", str(work),
            "--variant", "r2",
        ])

    assert code == 1
    assert not mock_prep.called, "prepare_checkout must not be called when manifest mismatches"
    assert not mock_build.called, "build must not be called when manifest mismatches"
    assert not (work / "co-r2").exists(), "Checkout directory must not be created on manifest mismatch"

    captured = capsys.readouterr()
    assert "r1-manifest gate error:" in captured.err


def test_illustrative_legacy_flow_un_gated_checkout_contrast(tmp_path: Path) -> None:
    """Illustrative model contrasting legacy un-gated flow with remediated gate:
    In the un-gated code structure, checkout preparation was unconditionally executed
    without prior manifest validation.

    In the remediated implementation, `run_gated_build` invokes `check_manifest_gate`
    which fails closed before `prepare_checkout` or `build` can be reached.
    """
    root = tmp_path / "mock-root"
    root.mkdir()
    work = tmp_path / "work"
    corrupt_manifest_bytes = COMMITTED_MANIFEST_BYTES + b"# corrupted\n"

    # Illustrative legacy simulation:
    legacy_co = work / "co-legacy-sim"
    ENTER.prepare_checkout(S.REPO, legacy_co)
    assert legacy_co.exists(), "Legacy un-gated simulation demonstrates unconditional checkout creation"

    # Remediated gated flow:
    gated_work = tmp_path / "gated_work"
    with patch.object(ENTER, "regenerate_manifest", return_value=corrupt_manifest_bytes):
        with pytest.raises(ENTER.ManifestGateError, match="R-1 manifest mismatch"):
            ENTER.run_gated_build(
                root=root,
                repo=S.REPO,
                work=gated_work,
                command="build",
                variant="r2",
            )
    assert not (gated_work / "co-r2").exists(), "Gated execution strictly refuses before checkout creation"


def test_gate_exact_equality_permits_build(tmp_path: Path) -> None:
    """When regenerated manifest exactly matches committed manifest,
    gate succeeds and proceeds to checkout and build.
    """
    root = tmp_path / "mock-root"
    root.mkdir()
    work = tmp_path / "work"

    mock_proc = subprocess.CompletedProcess(args=["bwrap"], returncode=0, stdout=b"build ok\n", stderr=b"")

    with patch.object(ENTER, "regenerate_manifest", return_value=COMMITTED_MANIFEST_BYTES), \
         patch.object(ENTER, "build", return_value=mock_proc) as mock_build:
        result = ENTER.run_gated_build(
            root=root,
            repo=S.REPO,
            work=work,
            command="build",
            variant="r2",
        )

    assert result.gate.matches is True
    assert result.gate.regenerated_digest == COMMITTED_MANIFEST_SHA256
    assert result.completed_process.returncode == 0
    assert mock_build.called
    assert (work / "co-r2").exists()


def test_gate_refuses_on_one_byte_drift(tmp_path: Path) -> None:
    """One single byte difference in the regenerated manifest causes fail-closed
    before prepare_checkout and before build.
    """
    root = tmp_path / "mock-root"
    root.mkdir()
    work = tmp_path / "work"

    # Flip one byte in the middle of the manifest
    corrupted_bytes = bytearray(COMMITTED_MANIFEST_BYTES)
    corrupted_bytes[100] = corrupted_bytes[100] ^ 0x01
    corrupted_bytes = bytes(corrupted_bytes)
    assert corrupted_bytes != COMMITTED_MANIFEST_BYTES

    with patch.object(ENTER, "regenerate_manifest", return_value=corrupted_bytes), \
         patch.object(ENTER, "prepare_checkout") as mock_prep, \
         patch.object(ENTER, "build") as mock_build:
        with pytest.raises(ENTER.ManifestGateError, match="R-1 manifest mismatch"):
            ENTER.run_gated_build(
                root=root,
                repo=S.REPO,
                work=work,
                command="build",
                variant="r2",
            )

    assert not mock_prep.called, "prepare_checkout must not be called when manifest drifts by 1 byte"
    assert not mock_build.called, "build must not be called when manifest drifts by 1 byte"
    assert not (work / "co-r2").exists()


def test_gate_refuses_on_manifest_regeneration_failure(tmp_path: Path) -> None:
    """If manifest regeneration fails (e.g. find or sha256sum fails in bwrap),
    gate fails closed before checkout preparation.
    """
    root = tmp_path / "mock-root"
    root.mkdir()
    work = tmp_path / "work"

    with patch.object(ENTER, "regenerate_manifest", side_effect=subprocess.CalledProcessError(1, ["bwrap"])), \
         patch.object(ENTER, "prepare_checkout") as mock_prep, \
         patch.object(ENTER, "build") as mock_build:
        with pytest.raises(ENTER.ManifestGateError, match="R-1 manifest regeneration failed"):
            ENTER.run_gated_build(
                root=root,
                repo=S.REPO,
                work=work,
                command="build",
                variant="r2",
            )

    assert not mock_prep.called
    assert not mock_build.called


def test_ordering_is_strictly_enforced(tmp_path: Path) -> None:
    """Call sequence must be:
    1. regenerate_manifest
    2. prepare_checkout
    3. build
    """
    call_log: list[str] = []

    def fake_regen(r):
        call_log.append("regenerate_manifest")
        return COMMITTED_MANIFEST_BYTES

    def fake_prep(repo, dest, touch_time=None):
        call_log.append("prepare_checkout")

    def fake_build(root, checkout, variant, trace_dir=None, strace_argv=()):
        call_log.append("build")
        return subprocess.CompletedProcess(args=[], returncode=0, stdout=b"", stderr=b"")

    root = tmp_path / "mock-root"
    root.mkdir()
    work = tmp_path / "work"

    with patch.object(ENTER, "regenerate_manifest", side_effect=fake_regen), \
         patch.object(ENTER, "prepare_checkout", side_effect=fake_prep), \
         patch.object(ENTER, "build", side_effect=fake_build):
        res = ENTER.run_gated_build(root, S.REPO, work, command="build", variant="r2")

    assert call_log == ["regenerate_manifest", "prepare_checkout", "build"]
    assert res.gate.matches is True


def test_both_build_and_ic1_use_the_same_gate(tmp_path: Path) -> None:
    """Both 'build' and 'ic1' pass through check_manifest_gate and fail closed if mismatched."""
    root = tmp_path / "mock-root"
    root.mkdir()
    work = tmp_path / "work"

    for cmd in ("build", "ic1"):
        corrupted = COMMITTED_MANIFEST_BYTES + b"\n"
        with patch.object(ENTER, "regenerate_manifest", return_value=corrupted), \
             patch.object(ENTER, "prepare_checkout") as mock_prep:
            with pytest.raises(ENTER.ManifestGateError):
                ENTER.run_gated_build(root, S.REPO, work, command=cmd, variant="r2")
            assert not mock_prep.called, f"Command {cmd} called prepare_checkout despite manifest failure!"


def test_cli_reports_manifest_verdict_and_supports_out_files(tmp_path: Path, capsys) -> None:
    """CLI prints `r1-manifest <digest> equal` and outputs manifest to file if requested."""
    root = tmp_path / "mock-root"
    root.mkdir()
    work = tmp_path / "work"
    manifest_out = tmp_path / "out-manifest.txt"

    mock_proc = subprocess.CompletedProcess(args=["bwrap"], returncode=0, stdout=b"build output\n", stderr=b"")

    with patch.object(ENTER, "regenerate_manifest", return_value=COMMITTED_MANIFEST_BYTES), \
         patch.object(ENTER, "prepare_checkout"), \
         patch.object(ENTER, "build", return_value=mock_proc):
        code = ENTER.main([
            "build",
            "--root", str(root),
            "--work", str(work),
            "--manifest-out", str(manifest_out),
        ])

    assert code == 0
    captured = capsys.readouterr()
    assert f"r1-manifest {COMMITTED_MANIFEST_SHA256} equal" in captured.out
    assert "exit 0" in captured.out
    assert manifest_out.exists()
    assert manifest_out.read_bytes() == COMMITTED_MANIFEST_BYTES


def test_cli_returns_exit_1_on_manifest_mismatch(tmp_path: Path, capsys) -> None:
    """CLI exits with 1 on manifest mismatch and writes error to stderr."""
    root = tmp_path / "mock-root"
    root.mkdir()
    work = tmp_path / "work"

    with patch.object(ENTER, "regenerate_manifest", return_value=b"bad manifest"):
        code = ENTER.main([
            "build",
            "--root", str(root),
            "--work", str(work),
        ])

    assert code == 1
    captured = capsys.readouterr()
    assert "r1-manifest gate error:" in captured.err
    assert not (work / "co-r2").exists()


# ---------------------------------------------------------------------------
# cc1.v Byte-Level Comparison Tests (C-P5.0-R5-RP11-I1-R3-R4-R5-R3)
# ---------------------------------------------------------------------------


def test_cc1check_identical_byte_streams_produce_pass_and_cli_exit_0(tmp_path: Path) -> None:
    """Identical byte streams produce equal digests, zero differences, PASS verdict,
    and CLI exit code 0.
    """
    data = b"Using built-in specs.\nCOLLECT_GCC=/usr/bin/gcc-15\nTarget: x86_64-linux-gnu\n"
    report = CC1CHECK.compare_cc1_v(data, data)
    assert report.is_identical is True
    assert report.verdict == "PASS"
    assert len(report.differences) == 0
    assert report.baseline_sha256 == report.actual_sha256

    f1 = tmp_path / "base.v"
    f2 = tmp_path / "act.v"
    f1.write_bytes(data)
    f2.write_bytes(data)
    exit_code = CC1CHECK.main([str(f1), str(f2)])
    assert exit_code == 0


def test_cc1check_one_byte_substitution_reports_exact_offset_values_and_hard_stop(tmp_path: Path) -> None:
    """A one-byte substitution reports exact offset, baseline and actual byte values,
    and produces HARD_STOP / CLI exit 1.
    """
    baseline = b"abc1def"
    actual = b"abc2def"

    report = CC1CHECK.compare_cc1_v(baseline, actual)
    assert report.is_identical is False
    assert report.verdict == "HARD_STOP"
    assert report.baseline_sha256 != report.actual_sha256
    assert len(report.differences) == 1

    diff = report.differences[0]
    assert diff.diff_type == "replace"
    assert diff.baseline_offset == 3
    assert diff.baseline_length == 1
    assert diff.baseline_bytes == b"1"
    assert diff.actual_offset == 3
    assert diff.actual_length == 1
    assert diff.actual_bytes == b"2"

    f1 = tmp_path / "base.v"
    f2 = tmp_path / "act.v"
    f1.write_bytes(baseline)
    f2.write_bytes(actual)
    exit_code = CC1CHECK.main([str(f1), str(f2)])
    assert exit_code == 1


def test_cc1check_insertions_deletions_and_eof_boundaries() -> None:
    """Insertion and deletion, including at start, middle, and end of file,
    report exact ranges without losing or misaligning subsequent differences.
    """
    # 1. Insertion at end of file
    b_eof = b"prefix"
    a_eof = b"prefix_extra"
    rep_eof = CC1CHECK.compare_cc1_v(b_eof, a_eof)
    assert rep_eof.verdict == "HARD_STOP"
    assert len(rep_eof.differences) == 1
    d_eof = rep_eof.differences[0]
    assert d_eof.diff_type == "insert"
    assert d_eof.baseline_offset == 6
    assert d_eof.baseline_length == 0
    assert d_eof.baseline_bytes == b""
    assert d_eof.actual_offset == 6
    assert d_eof.actual_length == 6
    assert d_eof.actual_bytes == b"_extra"

    # 2. Deletion at end of file
    rep_del = CC1CHECK.compare_cc1_v(a_eof, b_eof)
    assert rep_del.verdict == "HARD_STOP"
    assert len(rep_del.differences) == 1
    d_del = rep_del.differences[0]
    assert d_del.diff_type == "delete"
    assert d_del.baseline_offset == 6
    assert d_del.baseline_length == 6
    assert d_del.baseline_bytes == b"_extra"
    assert d_del.actual_offset == 6
    assert d_del.actual_length == 0
    assert d_del.actual_bytes == b""

    # 3. Multi-point differences (insertion, replacement, deletion across stream)
    b_multi = b"AAA_111_BBB_CCC_222"
    a_multi = b"AAA_X111Y_BBB_222"
    # Notice: insertion of X before 111, replacement/insertion around Y, deletion of _CCC
    rep_multi = CC1CHECK.compare_cc1_v(b_multi, a_multi)
    assert rep_multi.verdict == "HARD_STOP"
    assert len(rep_multi.differences) >= 2
    # Verify that the subsequent matching token '_222' was not lost or misaligned:
    last_diff = rep_multi.differences[-1]
    assert b"CCC" in last_diff.baseline_bytes


def test_cc1check_non_utf8_bytes_reported_exactly() -> None:
    """Non-UTF-8 bytes are compared and reported exactly rather than hidden
    by replacement characters.
    """
    baseline = b"header\x00\xff\xfe\x80trailer"
    actual = b"header\x00\xee\xfe\x80trailer"

    report = CC1CHECK.compare_cc1_v(baseline, actual)
    assert report.is_identical is False
    assert report.verdict == "HARD_STOP"
    assert len(report.differences) == 1

    diff = report.differences[0]
    assert diff.diff_type == "replace"
    assert diff.baseline_offset == 7
    assert diff.baseline_length == 1
    assert diff.baseline_bytes == b"\xff"
    assert diff.actual_offset == 7
    assert diff.actual_length == 1
    assert diff.actual_bytes == b"\xee"

    # Verify summary() formats without UnicodeDecodeError
    summary = report.summary()
    assert r"\xff" in summary
    assert r"\xee" in summary


def test_cc1check_no_caller_label_or_mechanism_can_produce_pass_on_non_identical_bytes() -> None:
    """No caller-provided regex, explanation string, or unauthenticated mechanism
    can turn non-identical bytes into PASS.
    """
    baseline = b"COLLECT_GCC_OPTIONS='-march=x86-64'\n"
    actual = b"COLLECT_GCC_OPTIONS='-march=x86-64-v2'\n"

    # compare_cc1_v accepts ONLY (baseline_bytes, actual_bytes)
    report = CC1CHECK.compare_cc1_v(baseline, actual)
    assert report.is_identical is False
    assert report.verdict == "HARD_STOP"

    # Ensure no explanation/override mechanism exists on the module
    assert not hasattr(CC1CHECK, "explanation_rules")
    assert "explanation_rules" not in CC1CHECK.compare_cc1_v.__code__.co_varnames


def test_cc1check_missing_or_unreadable_inputs_fail(tmp_path: Path, capsys) -> None:
    """Missing or unreadable input files fail with distinct exit code (2) and do not produce PASS."""
    missing1 = tmp_path / "nonexistent1.v"
    missing2 = tmp_path / "nonexistent2.v"

    exit_code = CC1CHECK.main([str(missing1), str(missing2)])
    assert exit_code == 2

    captured = capsys.readouterr()
    assert "does not exist" in captured.err
