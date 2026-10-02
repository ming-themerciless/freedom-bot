"""cc1.v byte-level comparison and hard-stop reporting (C-P5.0-R5-RP11-I1-R3-R4-R5-R3).

Compares two retained `cc1.v` diagnostic streams (produced by gcc-15 -v in build.sh)
under LD-8:
* Reports both SHA-256 values.
* Computes exact differing byte offsets, lengths, and raw byte values.
* Fails closed: returns PASS only when inputs are byte-identical.
* Emits a mandatory HARD_STOP verdict for any difference; no unauthenticated
  label, regex or metadata mechanism can override this verdict.
"""
from __future__ import annotations

import argparse
import dataclasses
import difflib
import hashlib
import sys
from pathlib import Path


@dataclasses.dataclass(frozen=True)
class CC1ByteDiff:
    diff_type: str  # "replace", "delete", "insert"
    baseline_offset: int
    baseline_length: int
    baseline_bytes: bytes
    actual_offset: int
    actual_length: int
    actual_bytes: bytes
    line_number: int | None = None
    line_context: str | None = None


@dataclasses.dataclass(frozen=True)
class CC1ComparisonReport:
    baseline_sha256: str
    actual_sha256: str
    is_identical: bool
    differences: tuple[CC1ByteDiff, ...]
    verdict: str  # "PASS" or "HARD_STOP"

    def summary(self) -> str:
        lines = [
            f"baseline_sha256: {self.baseline_sha256}",
            f"actual_sha256:   {self.actual_sha256}",
            f"is_identical:    {self.is_identical}",
            f"total_diffs:     {len(self.differences)}",
            f"verdict:         {self.verdict}",
        ]
        if self.differences:
            lines.append("\nDiffering byte ranges (HARD_STOP):")
            for d in self.differences:
                line_str = f" [approx line {d.line_number}]" if d.line_number is not None else ""
                lines.append(
                    f"  offset base:{d.baseline_offset}+{d.baseline_length} "
                    f"act:{d.actual_offset}+{d.actual_length} ({d.diff_type}){line_str}:"
                )
                lines.append(f"    - baseline bytes ({d.baseline_length}): {d.baseline_bytes!r}")
                lines.append(f"    + actual bytes   ({d.actual_length}): {d.actual_bytes!r}")
                if d.line_context:
                    lines.append(f"    context: {d.line_context}")
        return "\n".join(lines)


def compare_cc1_v(
    baseline_bytes: bytes,
    actual_bytes: bytes,
) -> CC1ComparisonReport:
    """Compare two cc1.v byte streams and return a CC1ComparisonReport.

    Under LD-8:
    * Reports SHA-256 for both streams.
    * Returns PASS only when the byte streams are identical.
    * For every non-identical pair, records exact byte offsets and byte values,
      and enforces a HARD_STOP verdict.
    * No caller label, regex, or unauthenticated metadata can convert a non-identical
      stream into PASS.
    """
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

    diffs: list[CC1ByteDiff] = []
    matcher = difflib.SequenceMatcher(None, baseline_bytes, actual_bytes)

    for tag, alo, ahi, blo, bhi in matcher.get_opcodes():
        if tag == "equal":
            continue

        base_slice = baseline_bytes[alo:ahi]
        act_slice = actual_bytes[blo:bhi]
        base_len = ahi - alo
        act_len = bhi - blo

        line_no = None
        context_str = None
        if b"\n" in baseline_bytes or b"\n" in actual_bytes:
            if base_len > 0:
                line_no = baseline_bytes[:alo].count(b"\n") + 1
                l_start = baseline_bytes.rfind(b"\n", 0, alo) + 1
                l_end = baseline_bytes.find(b"\n", ahi)
                l_end = len(baseline_bytes) if l_end == -1 else l_end
                context_str = repr(baseline_bytes[l_start:l_end])
            else:
                line_no = actual_bytes[:blo].count(b"\n") + 1
                l_start = actual_bytes.rfind(b"\n", 0, blo) + 1
                l_end = actual_bytes.find(b"\n", bhi)
                l_end = len(actual_bytes) if l_end == -1 else l_end
                context_str = repr(actual_bytes[l_start:l_end])

        diffs.append(CC1ByteDiff(
            diff_type=tag,
            baseline_offset=alo,
            baseline_length=base_len,
            baseline_bytes=base_slice,
            actual_offset=blo,
            actual_length=act_len,
            actual_bytes=act_slice,
            line_number=line_no,
            line_context=context_str,
        ))

    return CC1ComparisonReport(
        baseline_sha256=baseline_sha,
        actual_sha256=actual_sha,
        is_identical=False,
        differences=tuple(diffs),
        verdict="HARD_STOP",
    )


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n", 1)[0])
    parser.add_argument("baseline", type=Path, help="Path to baseline cc1.v file")
    parser.add_argument("actual", type=Path, help="Path to actual cc1.v file")
    args = parser.parse_args(argv)

    if not args.baseline.exists():
        sys.stderr.write(f"Baseline file does not exist: {args.baseline}\n")
        return 2
    if not args.actual.exists():
        sys.stderr.write(f"Actual file does not exist: {args.actual}\n")
        return 2

    try:
        baseline_bytes = args.baseline.read_bytes()
    except Exception as exc:
        sys.stderr.write(f"Cannot read baseline file {args.baseline}: {exc}\n")
        return 2

    try:
        actual_bytes = args.actual.read_bytes()
    except Exception as exc:
        sys.stderr.write(f"Cannot read actual file {args.actual}: {exc}\n")
        return 2

    report = compare_cc1_v(baseline_bytes, actual_bytes)
    print(report.summary())
    return 0 if report.verdict == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
