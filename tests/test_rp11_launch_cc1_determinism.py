"""`cc1.v` determinism under host resource limits (C-P5.0-R5-RP11-FRESH-R5-R4-D1).

Finding `FRESH-R4-HS-1`: the exact `cc1.v` contract included GCC's
garbage-collector parameters, which `cc1` selects at startup from the host's
memory and resource limits. `build.sh` now fixes both. These tests show, with
the pinned compiler in the bound root, that the fixed build's `cc1.v` and
normative outputs do not move under lowered limits, that the same limits do
move the unfixed build's `GGC heuristics:` line and nothing else, and that GCC
keeps the last `--param` given, which is why each must appear exactly once.

Like `tests/test_rp11_launch_toolchain.py` they run only when
`RP11_LAUNCH_BUILD_ROOT` names a root that passes R-1, and otherwise skip with
an explicit reason; a skip is never a pass. They are kept out of that module so
that its accepted test set, which R-5's step 10 runs and counts, is unchanged.
None of this is R-5.
"""
from __future__ import annotations

import hashlib
import os
import resource
import subprocess
from pathlib import Path

import pytest

from tests import rp11_launch_support as S
from tools.phase_5_0_evidence import rp11_launch as C

ROOT = os.environ.get("RP11_LAUNCH_BUILD_ROOT")
pytestmark = pytest.mark.skipif(
    not ROOT,
    reason="RP11_LAUNCH_BUILD_ROOT is not set: no pinned rp11-launch build root is provisioned here "
    "(the toolchain-dependent cc1.v determinism tests are not run)",
)

ENTER = S.load("enter", S.BUILDROOT)
CC1CHECK = S.load("cc1check")
FIXTURE = S.VERIFY / "fixtures" / "cc1.v.baseline"
DIGESTED = ("rp11-launch", "rp11-launch.map", "rp11-launch.x86_64.listing", "launch.s")
FIXED_LINE = "\t--param=ggc-min-expand=100 --param=ggc-min-heapsize=131072 \\\n"
FIXED_GGC = b"GGC heuristics: --param ggc-min-expand=100 --param ggc-min-heapsize=131072\n"
#: An address-space limit below 1 GiB makes GCC's heuristic select a
#: `ggc-min-expand` below 100 on every host; the resident-set limit lowers
#: `ggc-min-heapsize` where the heuristic honours it. The exact values depend on
#: the host and are not asserted.
LIMITS = {"RLIMIT_AS": 800_000_000, "RLIMIT_RSS": 2_221_056}


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


@pytest.fixture(scope="module")
def root() -> Path:
    path = Path(ROOT).resolve()
    regenerated = ENTER.regenerate_manifest(path)
    assert regenerated == (S.LAUNCH / "build-root.manifest").read_bytes(), "R-1: the root is not the bound root"
    return path


@pytest.fixture(scope="module")
def work(tmp_path_factory) -> Path:
    return tmp_path_factory.mktemp("rp11-cc1")


def _build(root: Path, work: Path, name: str, edit=None, limits: dict | None = None):
    """R-2 in the bound root, after an optional edit of the checkout's
    `build.sh`, with optional lowered limits inherited by the whole build."""
    co = work / f"co-{name}"
    ENTER.prepare_checkout(S.REPO, co)
    if edit is not None:
        script = co / "infra/rp11-launch/build.sh"
        script.write_text(edit(script.read_text()))
    mount, uid, host = ENTER.VARIANTS["r2"]
    binds = ((str(co), mount, False), (str(co / "build-out"), f"{mount}/build-out", True))
    argv = ENTER._bwrap(root, uid=uid, gid=uid, hostname=host, binds=binds, chdir=mount)

    def lower() -> None:
        for key, value in (limits or {}).items():
            resource.setrlimit(getattr(resource, key), (value, value))

    result = subprocess.run(argv + list(ENTER.BUILD_ARGV), stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            preexec_fn=lower)
    assert result.returncode == 0, result.stderr.decode(errors="replace")[-2000:]
    out = co / "build-out"
    return (out / "cc1.v").read_bytes(), {key: _sha(out / key) for key in DIGESTED}


def _unfix(text: str) -> str:
    assert text.count(FIXED_LINE) == 1
    return text.replace(FIXED_LINE, "")


def _expected_outputs() -> dict[str, str]:
    return dict(reversed(l.split("  ")) for l in (S.LAUNCH / "expected.sha256").read_text().splitlines())


def _ggc_line(data: bytes) -> bytes:
    lines = [l + b"\n" for l in data.split(b"\n") if l.startswith(b"GGC heuristics:")]
    assert len(lines) == 1
    return lines[0]


def test_the_fixed_build_reproduces_the_fixture_without_and_with_lowered_limits(root, work) -> None:
    for name, limits in (("plain", None), ("limited", LIMITS)):
        cc1v, outputs = _build(root, work, name, limits=limits)
        assert outputs == _expected_outputs(), name
        report = CC1CHECK.compare_cc1_v(FIXTURE.read_bytes(), cc1v)
        assert report.verdict == "PASS", (name, report.summary())
    assert len(FIXTURE.read_bytes()) == C.CC1_V_BASELINE_LENGTH and _sha(FIXTURE) == C.CC1_V_BASELINE_SHA256


def test_the_same_limits_move_only_the_unfixed_ggc_line(root, work) -> None:
    """Evidence that the limits reach cc1: without the two arguments its
    heuristic values differ, and once the three insertions are removed from the
    fixture that line is the only difference. The outputs do not move."""
    cc1v, outputs = _build(root, work, "unfixed-limited", _unfix, LIMITS)
    assert outputs == _expected_outputs()
    line = _ggc_line(cc1v)
    assert line != FIXED_GGC and b"ggc-min-expand=100 " not in line
    stripped = FIXTURE.read_bytes() \
        .replace(b"'--param=ggc-min-expand=100' '--param=ggc-min-heapsize=131072' ", b"") \
        .replace(b" --param=ggc-min-expand=100 --param=ggc-min-heapsize=131072", b"")
    assert stripped.replace(FIXED_GGC, line) == cc1v
    assert CC1CHECK.compare_cc1_v(FIXTURE.read_bytes(), cc1v).verdict == "HARD_STOP"


@pytest.mark.parametrize("spelling", ["separate", "joined"])
def test_the_pinned_compiler_keeps_the_last_value_given(root, work, spelling) -> None:
    """Why the once-only rule matters: a later --param overrides the fixed one."""
    later = ("--param ggc-min-expand=94 --param ggc-min-heapsize=2169" if spelling == "separate"
             else "--param=ggc-min-expand=94 --param=ggc-min-heapsize=2169")

    def edit(text: str) -> str:
        anchor = "\t-Os -g0 -U_FORTIFY_SOURCE \\\n"
        assert text.count(anchor) == 1
        return text.replace(anchor, f"\t{later} \\\n{anchor}")

    cc1v, outputs = _build(root, work, f"override-{spelling}", edit)
    assert outputs == _expected_outputs()
    assert _ggc_line(cc1v) == b"GGC heuristics: --param ggc-min-expand=94 --param ggc-min-heapsize=2169\n"
