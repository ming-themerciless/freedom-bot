"""Enter the rp11-launch build root: the entry mechanism X-3 (proposal §5.3.7).

Class **P**. It is not pinned by `toolchain.lock`, because nothing inside the
root can verify it (HA-3); its identity is recorded as `entry_mechanism`. It
runs `bwrap` (bubblewrap) on the host, unprivileged, with a user namespace and
no network, and presents the provisioned root **read-only** at `/`. Only the
checkout's `build-out/` directory, and for IC-1 the trace directory, are
writable.

Commands, one per step of §5.3.5 and §5.3.7:

``ldconfig``  run the root's own ``ldconfig`` to create ``/etc/ld.so.cache``
              (provisioning step 4 of ``provision.py``; the root is writable
              for this one command and for nothing else).
``manifest``  R-1: regenerate the tree manifest with the pinned ``find`` and
              ``sha256sum`` (``manifest_argv``), inside the root.
``build``     R-2 and the R-4 variations: start exactly the R-2 vector as the
              first process in the root.
``ic1``       IC-1: the same as ``build``, under the pinned ``strace``.
``versions``  the first ``--version`` line of every lock tool, inside the root.

**"The same session" (R-1 and R-2).** bwrap runs one command per entry. R-1
(two ``find`` vectors) and R-2 are therefore three consecutive entries made by
one ``enter.py build`` run, over the same read-only root bind, with nothing
else in between. The interval is HA-3's "trusted for the seconds between R-1
and R-2". This is recorded as an implementation interpretation in the I-7
handback for review.
"""
from __future__ import annotations

import argparse
import dataclasses
import hashlib
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
LAUNCH_DIR = HERE.parent
COMMITTED_MANIFEST = LAUNCH_DIR / "build-root.manifest"
BWRAP = "/usr/bin/bwrap"

BUILD_ENV = (("LC_ALL", "C"), ("PATH", "/usr/bin"), ("SOURCE_DATE_EPOCH", "0"), ("TZ", "UTC0"))
BUILD_ARGV = (
    "/usr/bin/env", "-i", "LC_ALL=C", "PATH=/usr/bin", "SOURCE_DATE_EPOCH=0", "TZ=UTC0",
    "/bin/sh", "infra/rp11-launch/build.sh", "build-out",
)
#: §5.3.2 exclusions, each with its reason. Nothing else is excluded.
EXCLUSIONS = (
    ("/proc", "kernel-provided mount (HA-1); not a file of the root"),
    ("/sys", "kernel-provided mount (HA-1); not a file of the root"),
    ("/dev", "device nodes presented by the entry mechanism (HA-3)"),
    ("/run", "runtime directory; mounted over by nothing and opened by no class-B or class-E tool (IC-1)"),
    ("/rp11", "the checkout and IC-1 trace mount points; the checkout is a named exclusion (§5.3.2)"),
)
_PRUNE = ["("]
for i, (path, _reason) in enumerate(EXCLUSIONS):
    _PRUNE += (["-o"] if i else []) + ["-path", path]
_PRUNE += [")", "-prune", "-o"]
MANIFEST_ARGV = (
    ("/usr/bin/find", "/", *_PRUNE, "-printf", r"%y\0%m\0%U\0%G\0%s\0%p\0%l\0"),
    ("/usr/bin/find", "/", *_PRUNE, "-type", "f", "-exec", "/usr/bin/sha256sum", "-z", "--", "{}", "+"),
)
#: The class-B and class-E executables of §5.3.7 that live in the root.
LOCK_TOOLS = (
    ("/usr/bin/env", True),
    ("/bin/sh", False),
    ("/usr/bin/gcc-15", True),
    ("/usr/libexec/gcc/x86_64-linux-gnu/15/cc1", True),
    ("/usr/bin/as", True),
    ("/usr/bin/ld.bfd", True),
    ("/usr/bin/objdump", True),
    ("/usr/bin/readelf", True),
    ("/usr/bin/sha256sum", True),
    ("/usr/bin/find", True),
    ("/usr/bin/strace", False),
)

#: R-2 and the three R-4 variations: checkout mount point, uid/gid, user, host.
VARIANTS = {
    "r2": ("/rp11/co", 1000, "rp11-build"),
    "r4a-path": ("/rp11/alt/checkout", 1000, "rp11-build"),
    "r4b-time": ("/rp11/co", 1000, "rp11-build"),
    "r4c-user": ("/rp11/co", 1001, "rp11-variant"),
}

OUTPUTS = ("rp11-launch", "rp11-launch.map", "rp11-launch.x86_64.listing", "launch.s", "cc1.v")


def _bwrap(root: Path, *, uid: int, gid: int, hostname: str, writable_root: bool = False,
           binds: tuple[tuple[str, str, bool], ...] = (), chdir: str = "/") -> list[str]:
    argv = [
        BWRAP, "--unshare-all", "--die-with-parent", "--new-session",
        "--uid", str(uid), "--gid", str(gid), "--hostname", hostname,
        "--clearenv",
    ]
    for k, v in BUILD_ENV:
        argv += ["--setenv", k, v]
    argv += ["--bind" if writable_root else "--ro-bind", str(root), "/",
             "--proc", "/proc", "--dev", "/dev"]
    for src, dst, rw in binds:
        argv += ["--bind" if rw else "--ro-bind", src, dst]
    argv += ["--chdir", chdir, "--"]
    return argv


def run_ldconfig(root: Path) -> None:
    subprocess.run(_bwrap(root, uid=0, gid=0, hostname="rp11-provision", writable_root=True)
                   + ["/usr/sbin/ldconfig", "-X", "-i"], check=True)
    aux = root / "var/cache/ldconfig/aux-cache"
    if aux.exists():
        # Records inode numbers and times of the provisioning host; it is a
        # cache ldconfig itself may ignore (-i), never read by the loader.
        aux.unlink()


def _escape(path: bytes) -> str:
    out = []
    for b in path:
        out.append(chr(b) if 0x21 <= b <= 0x7E and b != 0x5C else f"\\x{b:02x}")
    return "".join(out)


def regenerate_manifest(root: Path) -> bytes:
    """R-1: the two `manifest_argv` vectors inside the root, merged into the
    `rp11-build-root/1` text. The merge is a pure function of their output."""
    listing = subprocess.run(_bwrap(root, uid=0, gid=0, hostname="rp11-build") + list(MANIFEST_ARGV[0]),
                             check=True, stdout=subprocess.PIPE).stdout
    sums = subprocess.run(_bwrap(root, uid=0, gid=0, hostname="rp11-build") + list(MANIFEST_ARGV[1]),
                          check=True, stdout=subprocess.PIPE).stdout
    return merge_manifest(listing, sums)


def merge_manifest(listing: bytes, sums: bytes) -> bytes:
    fields = listing.split(b"\0")
    if fields[-1] != b"" or (len(fields) - 1) % 7:
        raise SystemExit("find output is not a whole number of 7-field records")
    digests: dict[bytes, str] = {}
    for rec in sums.split(b"\0"):
        if not rec:
            continue
        digest, path = rec[:64], rec[66:]
        if rec[64:66] != b"  ":
            raise SystemExit("unexpected sha256sum -z record")
        digests[path] = digest.decode()
    entries = []
    for i in range(0, len(fields) - 1, 7):
        y, m, u, g, s, p, link = fields[i:i + 7]
        kind = y.decode()
        if kind == "f":
            tail = digests.pop(p)
        elif kind == "l":
            tail = "-> " + _escape(link)
        else:
            tail = "-"
            s = b"0" if kind == "d" else s
        entries.append((p, f"{kind} {int(m, 8):04o} {u.decode()} {g.decode()} {s.decode()} {_escape(p)} {tail}"))
    if digests:
        raise SystemExit(f"sha256sum covered files find did not list: {sorted(digests)[:3]}")
    entries.sort(key=lambda e: e[0])
    text = ["rp11-build-root/1"]
    text += [f"exclude {path} {reason}" for path, reason in EXCLUSIONS]
    text += [line for _p, line in entries]
    return ("\n".join(text) + "\n").encode()


def prepare_checkout(repo: Path, dest: Path, *, touch_time: float | None = None) -> None:
    """A checkout holding `infra/rp11-launch/` exactly as in the working tree,
    and an empty `build-out/`."""
    if dest.exists():
        shutil.rmtree(dest)
    src = repo / "infra/rp11-launch"
    shutil.copytree(src, dest / "infra/rp11-launch", symlinks=True,
                    ignore=shutil.ignore_patterns("__pycache__"))
    (dest / "build-out").mkdir()
    if touch_time is not None:
        for p in (dest / "infra/rp11-launch").rglob("*"):
            os.utime(p, (touch_time, touch_time), follow_symlinks=False)


def build(root: Path, checkout: Path, variant: str, trace_dir: Path | None = None,
          strace_argv: tuple[str, ...] = ()) -> subprocess.CompletedProcess:
    mount, uid, host = VARIANTS[variant]
    binds = [(str(checkout), mount, False), (str(checkout / "build-out"), f"{mount}/build-out", True)]
    if trace_dir is not None:
        binds.append((str(trace_dir), "/rp11/trace", True))
    argv = _bwrap(root, uid=uid, gid=uid, hostname=host, binds=tuple(binds), chdir=mount)
    return subprocess.run(argv + list(strace_argv) + list(BUILD_ARGV),
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE)


IC1_STRACE = (
    "/usr/bin/strace", "-f", "-qq", "-v", "-y", "-s", "65536",
    "-e", "trace=%file,%process,fchdir", "-o", "/rp11/trace/ic1.trace", "--",
)


def digests(out: Path) -> dict[str, str]:
    return {name: hashlib.sha256((out / name).read_bytes()).hexdigest()
            for name in OUTPUTS if (out / name).exists()}


def tool_versions(root: Path) -> dict[str, str]:
    out = {}
    for path, has_version in LOCK_TOOLS:
        if not has_version:
            continue
        res = subprocess.run(_bwrap(root, uid=1000, gid=1000, hostname="rp11-build") + [path, "--version"],
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        out[path] = res.stdout.decode("utf-8", "replace").splitlines()[0] if res.stdout else ""
    return out


def bwrap_identity() -> str:
    v = subprocess.run([BWRAP, "--version"], stdout=subprocess.PIPE, check=True).stdout.decode().strip()
    return f"{v}; flags --unshare-all --die-with-parent --new-session --clearenv --ro-bind <root> /"


class ManifestGateError(RuntimeError):
    """Raised when R-1 manifest regeneration fails or does not match committed."""
    pass


@dataclasses.dataclass(frozen=True)
class ManifestGateResult:
    regenerated_bytes: bytes
    regenerated_digest: str
    committed_digest: str
    matches: bool


@dataclasses.dataclass(frozen=True)
class GatedBuildResult:
    gate: ManifestGateResult
    completed_process: subprocess.CompletedProcess
    output_digests: dict[str, str]


def check_manifest_gate(root: Path, committed_manifest: Path = COMMITTED_MANIFEST) -> ManifestGateResult:
    """Regenerate the manifest using the root's pinned find and sha256sum,
    and verify exact byte equality against the committed manifest.
    Fails closed before preparing checkouts or invoking build if bytes differ or regeneration fails.
    """
    if not committed_manifest.exists():
        raise ManifestGateError(f"Committed manifest not found: {committed_manifest}")
    committed_bytes = committed_manifest.read_bytes()
    committed_digest = hashlib.sha256(committed_bytes).hexdigest()
    try:
        regen_bytes = regenerate_manifest(root)
    except Exception as exc:
        raise ManifestGateError(f"R-1 manifest regeneration failed: {exc}") from exc
    regen_digest = hashlib.sha256(regen_bytes).hexdigest()
    matches = (regen_bytes == committed_bytes)
    result = ManifestGateResult(
        regenerated_bytes=regen_bytes,
        regenerated_digest=regen_digest,
        committed_digest=committed_digest,
        matches=matches,
    )
    if not matches:
        raise ManifestGateError(
            f"R-1 manifest mismatch: regenerated {regen_digest} != committed {committed_digest}"
        )
    return result


def run_gated_build(
    root: Path,
    repo: Path,
    work: Path,
    command: str,
    variant: str = "r2",
    committed_manifest: Path = COMMITTED_MANIFEST,
    manifest_out: Path | None = None,
) -> GatedBuildResult:
    """Run R-1 manifest gate immediately followed by R-2 / IC-1 build in one invocation.
    Fails closed before creating work directory, preparing checkout, or entering build
    if the manifest gate fails.
    """
    gate = check_manifest_gate(root, committed_manifest=committed_manifest)
    if manifest_out is not None:
        manifest_out.write_bytes(gate.regenerated_bytes)

    work.mkdir(parents=True, exist_ok=True)
    co = work / f"co-{variant}"
    touch = time.time() + 86400 * 400 if variant == "r4b-time" else None
    prepare_checkout(repo, co, touch_time=touch)

    trace_dir = None
    strace = ()
    if command == "ic1":
        trace_dir = work / "ic1-trace"
        if trace_dir.exists():
            shutil.rmtree(trace_dir)
        trace_dir.mkdir()
        strace = IC1_STRACE

    res = build(root, co, variant, trace_dir, strace)
    out_digests = digests(co / "build-out")
    return GatedBuildResult(
        gate=gate,
        completed_process=res,
        output_digests=out_digests,
    )


def main(argv: list[str]) -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    p.add_argument("command", choices=("ldconfig", "manifest", "build", "ic1", "versions"))
    p.add_argument("--root", type=Path, required=True)
    p.add_argument("--repo", type=Path, default=LAUNCH_DIR.parent.parent)
    p.add_argument("--work", type=Path, help="scratch directory for checkouts and outputs")
    p.add_argument("--variant", default="r2", choices=sorted(VARIANTS))
    p.add_argument("--out", type=Path, help="manifest output path")
    p.add_argument("--manifest-out", type=Path, help="write regenerated manifest bytes to this path during build/ic1")
    args = p.parse_args(argv)
    root = args.root.resolve()
    if args.command == "ldconfig":
        run_ldconfig(root)
    elif args.command == "manifest":
        data = regenerate_manifest(root)
        if args.out:
            args.out.write_bytes(data)
        else:
            sys.stdout.buffer.write(data)
    elif args.command == "versions":
        for k, v in tool_versions(root).items():
            print(f"{k}\t{v}")
    else:
        if not args.work:
            p.error("--work is required for build and ic1")
        work = args.work.resolve()
        manifest_out = args.manifest_out or args.out
        try:
            res = run_gated_build(
                root=root,
                repo=args.repo.resolve(),
                work=work,
                command=args.command,
                variant=args.variant,
                committed_manifest=COMMITTED_MANIFEST,
                manifest_out=manifest_out,
            )
        except ManifestGateError as exc:
            print(f"r1-manifest gate error: {exc}", file=sys.stderr)
            return 1

        sys.stdout.buffer.write(res.completed_process.stdout)
        sys.stderr.buffer.write(res.completed_process.stderr)
        print(f"r1-manifest {res.gate.regenerated_digest} equal")
        print(f"exit {res.completed_process.returncode}")
        for k, v in res.output_digests.items():
            print(f"{v}  {k}")
        return res.completed_process.returncode
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
