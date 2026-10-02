"""rp11-launch/1 toolchain-dependent tests (C-P5.0-R5-RP11-I1-R3-R4-I7).

T-L5, T-L6, T-L7, T-L8, T-L9, T-L11 and IC-1 (proposal §5.12.1, §5.3.7). They
need the pinned build root, provisioned from `toolchain.lock` by
`infra/rp11-launch/buildroot/provision.py` and entered by `enter.py`, and run
only when `RP11_LAUNCH_BUILD_ROOT` names it. **Elsewhere every test here skips
with an explicit reason; a skip is never a pass** (AGENTS.md, "Running the
suites").

Every test first requires R-1: the manifest regenerated inside the root by the
pinned `find` and `sha256sum` must equal the committed `build-root.manifest`.

None of these is R-5. R-5 is an independent rebuild by a party other than the
implementer, in a separately provisioned environment, that actually varies at
least one of HA-1 … HA-3 (§5.3.5, LD-8); the mechanism here is the one R-5
would run, and running it on the implementer's host does not perform it.
"""
from __future__ import annotations

import hashlib
import os
import random
import subprocess
from pathlib import Path

import pytest

from tests import rp11_launch_support as S
from tools.phase_5_0_evidence import rp11_launch as C

ROOT = os.environ.get("RP11_LAUNCH_BUILD_ROOT")
pytestmark = pytest.mark.skipif(
    not ROOT,
    reason="RP11_LAUNCH_BUILD_ROOT is not set: no pinned rp11-launch build root is provisioned here "
    "(toolchain-dependent T-L5 … T-L9, T-L11 and IC-1 are not run)",
)

ENTER = S.load("enter", S.BUILDROOT)
ELF = S.load("elfcheck")
TL11 = S.load("tl11")
IC1 = S.load("ic1check")

DIGESTED = ("rp11-launch", "rp11-launch.map", "rp11-launch.x86_64.listing", "launch.s")


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
    return tmp_path_factory.mktemp("rp11-launch")


def _build(root: Path, work: Path, variant: str, ic1: bool = False):
    co = work / f"co-{variant}{'-ic1' if ic1 else ''}"
    touch = None
    if variant == "r4b-time":
        import time
        touch = time.time() + 86400 * 400
    ENTER.prepare_checkout(S.REPO, co, touch_time=touch)
    trace_dir = None
    strace = ()
    if ic1:
        trace_dir = work / f"ic1-trace-{variant}"
        trace_dir.mkdir(exist_ok=True)
        strace = ENTER.IC1_STRACE
    result = ENTER.build(root, co, variant, trace_dir, strace)
    assert result.returncode == 0, result.stderr.decode(errors="replace")[-2000:]
    out = co / "build-out"
    return out, {name: _sha(out / name) for name in (*DIGESTED, "cc1.v")}, trace_dir


@pytest.fixture(scope="module")
def r2(root, work):
    return _build(root, work, "r2")


def test_r1_the_regenerated_manifest_is_the_committed_one(root) -> None:
    assert ENTER.regenerate_manifest(root) == (S.LAUNCH / "build-root.manifest").read_bytes()


def test_tl5_one_build_gives_the_expected_digests(r2) -> None:
    _out, digests, _ = r2
    expected = dict(reversed(l.split("  ")) for l in (S.LAUNCH / "expected.sha256").read_text().splitlines())
    assert {k: digests[k] for k in DIGESTED} == expected
    assert digests["rp11-launch"] == C.EXPECTED_IMAGE_SHA256


@pytest.mark.parametrize("variant", ["r4a-path", "r4b-time", "r4c-user"])
def test_tl6_each_r4_variation_gives_identical_outputs(root, work, r2, variant) -> None:
    _out, digests, _ = _build(root, work, variant)
    assert digests == r2[1]


def test_tl7_binary_inspection_bi_1_to_bi_5_bi_8_bi_9_and_listing_bytes(r2) -> None:
    out, _d, _ = r2
    image = (out / "rp11-launch").read_bytes()
    assert ELF.check_image(image) == []
    assert ELF.check_listing_bytes(image, S.LISTING.read_text()) == []
    assert ELF.check_map((out / "rp11-launch.map").read_text()) == []


def test_tl9_the_regenerated_listing_is_the_committed_listing(r2) -> None:
    out, _d, _ = r2
    assert (out / "rp11-launch.x86_64.listing").read_bytes() == S.LISTING.read_bytes()


def test_tl11_xd_agrees_and_gates_tl10(r2) -> None:
    out, _d, _ = r2
    record, tables = TL11.run((out / "rp11-launch").read_bytes(), S.LISTING.read_bytes(),
                              (S.VERIFY / "xdecode-spelling.table").read_bytes(), C.control_contract(),
                              C.EXPECTED_IMAGE_SHA256)
    assert record["tl11_verdict"] == "pass", record["failures"]
    assert record["tl10_verdict"] == "pass" and record["tl10_evidence"] is True
    assert record["agreed_stream_sha256"] == C.AGREED_STREAM_SHA256
    assert record["xdecode_py_sha256"] == C.XD_SOURCE_SHA256
    assert record["spelling_table_sha256"] == C.XD_SPELLING_TABLE_SHA256
    assert tables["max_stack_depth"] == C.EXPECTED_STACK_DEPTH


@pytest.mark.parametrize("variant", ["r2", "r4a-path"])
def test_ic1_the_traced_build_opens_nothing_outside_the_bound_root(root, work, r2, variant) -> None:
    """IC-1 at R-2's checkout and at R-4(a)'s: every environment is compared,
    exactly, with the one specified for that checkout (I-7-R1)."""
    checkout = ENTER.VARIANTS[variant][0]
    _out, digests, trace_dir = _build(root, work, variant, ic1=True)
    assert digests == r2[1], "IC-1's outputs differ from R-2's"
    result = IC1.check((trace_dir / "ic1.trace").read_text(), (S.LAUNCH / "build-root.manifest").read_text(),
                       checkout)
    assert result["verdict"] == "pass", result["failures"]
    assert result["proc_sys_paths"] == ["/proc/self/exe"]
    assert result["exec_sequence"] == [p for p, _c in C.IC1_EXEC_SEQUENCE]
    for record, (path, cls) in zip(result["environments"], C.IC1_EXEC_SEQUENCE, strict=True):
        assert record["class"] == cls and record["path"] == path
        assert sorted(record["env"]) == sorted(C.ic1_environment(cls, checkout))


def test_ic1_the_driver_values_follow_from_the_pinned_driver(root, work) -> None:
    """The offload pair from the pinned driver's configuration string, read
    from its bytes, and no driver self-spec adding switches."""
    entries, links, _ex = IC1.load_manifest((S.LAUNCH / "build-root.manifest").read_text())
    resolved = IC1.canonical("/usr/bin/gcc-15", links)
    data = (root / resolved.lstrip("/")).read_bytes()
    lock_tool = next(l for l in (S.LAUNCH / "toolchain.lock").read_text().splitlines()
                     if l.startswith("tool=/usr/bin/gcc-15 "))
    assert hashlib.sha256(data).hexdigest() in lock_tool
    configure = next(s for s in data.split(b"\0") if b"--enable-offload-targets=" in s).decode()
    targets = configure.split("--enable-offload-targets=", 1)[1].split()[0]
    names = ":".join(t.split("=", 1)[0] for t in targets.split(","))
    pinned = dict(e.split("=", 1) for e in C.DRIVER_ADDED_ENV_VALUES)
    assert pinned["OFFLOAD_TARGET_NAMES"] == names
    assert "--enable-offload-defaulted" in configure.split() and pinned["OFFLOAD_TARGET_DEFAULT"] == "1"
    empty = work / "dumpspecs"
    empty.mkdir(exist_ok=True)
    specs = _in_root(root, empty, ["/usr/bin/gcc-15", "-dumpspecs"], chdir="/rp11/co").decode()
    self_spec = specs.split("*self_spec:\n", 1)[1].split("\n\n", 1)[0]
    assert self_spec.strip() == ""


# ---------------------------------------------------------------------------
# T-L8 — the selection source under the pinned compiler and the image's flags
# ---------------------------------------------------------------------------


def _compile_vector() -> list[str]:
    text = (S.LAUNCH / "build.sh").read_text().replace("\\\n", " ")
    gcc = next(l.split() for l in text.splitlines() if l.strip().startswith("/usr/bin/gcc-15"))
    return gcc[1:gcc.index("-o")]


def _in_root(root: Path, work: Path, argv: list[str], stdin: bytes | None = None,
             chdir: str = "/rp11/co/infra/rp11-launch/test-harness") -> bytes:
    cmd = [ENTER.BWRAP, "--unshare-all", "--die-with-parent", "--new-session", "--uid", "1000", "--gid", "1000",
           "--clearenv", "--setenv", "LC_ALL", "C", "--setenv", "PATH", "/usr/bin",
           "--ro-bind", str(root), "/", "--proc", "/proc", "--dev", "/dev", "--tmpfs", "/tmp",
           "--bind", str(work), "/rp11/co", "--chdir", chdir, "--", *argv]
    r = subprocess.run(cmd, input=stdin, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    assert r.returncode == 0, r.stderr.decode(errors="replace")[-2000:]
    return r.stdout


def _cases() -> list[tuple[str, list[bytes]]]:
    valid = b"INVOCATION_ID=" + b"0123456789abcdef" * 2
    cases: list[tuple[str, list[bytes]]] = [
        ("A", [b"x", b"--pass", b"A"]), ("A", [b"", b"--pass", b"A"]), ("A", [b"x"]), ("A", [b"x", b"--pass"]),
        ("A", [b"x", b"--pass", b"B"]), ("A", [b"x", b"--pass=A"]), ("A", [b"x", b"--PASS", b"A"]),
        ("A", [b"x", b"--pass", b"AA"]), ("A", [b"x", b"--pass", b""]), ("A", [b"x", b"--pass", b"A", b"extra"]),
        ("A", [b"x", b"--pas", b"A"]), ("A", [b"x", b"--passs", b"A"]),
        ("E", [valid]), ("E", []), ("E", [valid, valid]), ("E", [valid, valid.replace(b"0", b"1")]),
        ("E", [b"INVOCATION_ID"]), ("E", [valid, b"INVOCATION_ID"]), ("E", [b"INVOCATION_ID="]),
        ("E", [valid[:-1]]), ("E", [valid + b"0"]), ("E", [valid.replace(b"a", b"A", 1)]),
        ("E", [valid.replace(b"0", b"g", 1)]), ("E", [b"INVOCATION_IDX=" + valid[14:], valid]),
        ("E", [b"invocation_id=" + valid[14:]]), ("E", [b" INVOCATION_ID=" + valid[14:]]),
        ("E", [b"INVOCATION_I=" + valid[14:]]), ("E", [b"INVOCATION_ID\x80=" + valid[14:], valid]),
        ("E", [b"LONG=" + b"x" * 98000, valid, b"\xff" * 63]),
    ]
    rng = random.Random(20261001)
    alphabet = b"0123456789abcdefABCDEFgxyz=_ I\x80\xff"
    for _ in range(2000):
        envp = []
        for _k in range(rng.randrange(0, 6)):
            kind = rng.randrange(6)
            if kind == 0:
                envp.append(b"INVOCATION_ID=" + bytes(rng.choice(alphabet[:16]) for _ in range(rng.choice([31, 32, 32, 33]))))
            elif kind == 1:
                envp.append(b"INVOCATION_ID=" + bytes(rng.choice(alphabet) for _ in range(32)))
            elif kind == 2:
                envp.append(b"INVOCATION_ID"[: rng.randrange(1, 14)] + bytes(rng.choice(alphabet) for _ in range(rng.randrange(0, 40))))
            elif kind == 3:
                envp.append(b"INVOCATION_ID")
            else:
                envp.append(bytes(rng.randrange(1, 256) for _ in range(rng.randrange(0, 50))))
        cases.append(("E", envp))
        argv = [bytes(rng.randrange(1, 256) for _ in range(rng.randrange(0, 5)))]
        argv += [rng.choice([b"--pass", b"--pass", b"-pass", b"--pasS", b"A"]) for _ in range(rng.randrange(0, 4))]
        cases.append(("A", argv))
    return cases


def _expected(kind: str, strings: list[bytes]) -> str:
    if kind == "A":
        return str(S.check_argv(strings))
    sel = S.select_invocation_id(strings)
    return "null" if sel is None else f"{sel[0]} {sel[1]} {sel[2].hex()}"


def test_tl8_the_compiled_selection_source_matches_the_reference_model(root, work) -> None:
    """Narrow by design (LD-7): it tests the selection source and the pinned
    compiler under the image's flags, in a separate non-inlined context. It
    says nothing about the instructions inlined into rp11_main, the image's
    bytes or the installed image; HR-4 over the agreed stream covers those."""
    tl8 = work / "tl8"
    ENTER.prepare_checkout(S.REPO, tl8)
    _in_root(root, tl8, ["/usr/bin/gcc-15", *_compile_vector(), "-o", "shim.s", "select_shim.c"])
    _in_root(root, tl8, ["/usr/bin/as", "--64", "--noexecstack", "-mx86-used-note=no", "-o", "shim.o", "shim.s"])
    _in_root(root, tl8, ["/usr/bin/gcc-15", "-O1", "-no-pie", "-o", "harness", "select_harness.c", "shim.o"])
    cases = _cases()
    stdin = b"".join(
        (kind + " " + " ".join(s.hex() or "-" for s in strings) + "\n").encode() for kind, strings in cases
    )
    got = _in_root(root, tl8, ["./harness"], stdin).decode().splitlines()
    want = [_expected(kind, strings) for kind, strings in cases]
    assert len(got) == len(want) == len(cases)
    mismatches = [(cases[i], got[i], want[i]) for i in range(len(cases)) if got[i] != want[i]]
    assert not mismatches, mismatches[:3]
