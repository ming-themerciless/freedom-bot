"""IC-1 — the input-closure check over one traced R-2 run (proposal §5.3.7).

Class-E evidence tooling. It reads the pinned `strace` record of one R-2 run
(`-f -v -y -e trace=%file,%process,fchdir`) and the committed
`build-root.manifest`, and checks:

1. every successful `execve` is one of the lock's class-B or listing tools
   (X-5 … X-10, and X-12 and X-13, which `build.sh` runs to write the listing);
2. every path looked up resolves — through the manifest's own symbolic links —
   either to a manifest entry (when the call succeeded) or to a path the
   manifest binds as absent: not listed, and under no exclusion (when it
   failed). The exceptions are named: the five repository inputs; `build-out/`;
   the checkout's own directories, for stat-family calls; the two
   precompiled-header probes `cc1` makes beside its inputs (whose absence
   `build.sh` enforces); `/dev/null`; and every `/proc` or `/sys` path, which is
   listed by name as kernel-provided input under HA-1;
3. *(I-7-R1, finding I7-R1-1)* the successful `execve` calls are exactly
   `EXEC_SEQUENCE`, in order, and each one's environment **equals** — as a
   complete name/value mapping — the one its position defines in
   `ENV_CLASSES`, with ``{co}`` replaced by the run's controlled checkout
   (`CONTROLLED_CHECKOUTS`). A required variable that is missing, a value that
   differs, any other variable, a duplicated name and a malformed entry or
   record each fail. The values are specified, never taken from the trace:
   `build_env`; the entry mechanism's `PWD` for the first process (X-3 → X-5);
   the shell's `PWD` and `OLDPWD` for its children (X-6, `shell_added_env`),
   which are the directories `build.sh` changes into; and the compiler
   driver's four variables for `cc1` (X-7 → X-8, `driver_added_env`), derived
   from `build.sh`'s driver vector and the pinned driver's configuration (see
   `DRIVER_ADDED_VALUES`). Each `PWD` must also be the process's traced
   working directory;
4. nothing under `/tmp` or `/var/tmp` is created; and
5. *(FRESH-R4-HS-1)* the argument vectors of the driver (X-7) and of `cc1`
   (X-8) each carry every `FIXED_PARAMS` entry exactly once, as the one token
   `--param=<name>=<value>`, and no other token names that parameter, so no
   later or differently spelled `--param` can override it; and neither vector
   carries an `@file` response-file argument.

The output digests are compared with R-2's by the caller.
"""
from __future__ import annotations

import json
import posixpath
import re
import sys
from pathlib import Path

BUILD_ENV = (("LC_ALL", "C"), ("PATH", "/usr/bin"), ("SOURCE_DATE_EPOCH", "0"), ("TZ", "UTC0"))
ENTRY_ADDED = ("PWD",)
SHELL_ADDED = ("PWD", "OLDPWD")
DRIVER_ADDED = ("COLLECT_GCC", "COLLECT_GCC_OPTIONS", "OFFLOAD_TARGET_NAMES", "OFFLOAD_TARGET_DEFAULT")

#: The checkout mount points a traced build may use (`enter.py` VARIANTS):
#: R-2, R-4(b) and R-4(c) at the first, R-4(a) at the second.
CONTROLLED_CHECKOUTS = ("/rp11/co", "/rp11/alt/checkout")
CHECKOUT_TOKEN = "{co}"
CC1 = "/usr/libexec/gcc/x86_64-linux-gnu/15/cc1"

#: GCC 15's `set_collect_gcc_options` over `build.sh`'s driver vector: every
#: switch in order, quoted; `-U` and `-o` in their separate canonical form; then
#: the driver's `-dumpdir`, which for one compile-only input with `-o` is the
#: output's directory. Before that, the driver's `prune_options` drops a switch
#: that a later one cancels through its `Negative()` chain (`fpic` → `fPIC` →
#: `fpie` → `fPIE` → `fpic`), so `-fno-pie` removes the earlier `-fno-pic`.
#: The pinned driver has an empty `self_spec`, and its configured defaults
#: (`--with-tune`, `--with-arch-32`) add no switch to this vector, which names
#: `-march` and `-mtune` and not `-m32`.
COLLECT_GCC_OPTIONS = (
    "'-S' '-v' '-std=c11' '-ffreestanding' '-nostdinc' '-fno-builtin' '-fno-pie' "
    "'-fno-stack-protector' '-fno-stack-clash-protection' '-fcf-protection=none' "
    "'-mindirect-branch=keep' '-mfunction-return=keep' '-fno-asynchronous-unwind-tables' "
    "'-fno-unwind-tables' '-fno-jump-tables' '-fno-tree-vectorize' '-fno-common' '-fno-ident' "
    "'-fno-optimize-sibling-calls' '-fno-reorder-blocks-and-partition' '-fno-partial-inlining' "
    "'-fno-ipa-cp-clone' '-fno-ipa-sra' '-fno-tree-loop-distribute-patterns' '-fomit-frame-pointer' "
    "'-falign-functions=1' '-falign-jumps=1' '-falign-loops=1' '-falign-labels=1' "
    "'-mgeneral-regs-only' '-mno-red-zone' '-march=x86-64' '-mtune=generic' "
    "'-frandom-seed=rp11-launch' '--param=ggc-min-expand=100' '--param=ggc-min-heapsize=131072' "
    "'-Os' '-g0' '-U' '_FORTIFY_SOURCE' '-Wall' '-Wextra' '-Wvla' "
    "'-Werror' '-o' '../../build-out/launch.s' '-dumpdir' '../../build-out/'"
)
#: The driver's additions for `cc1`. `COLLECT_GCC` is the driver's `argv[0]`
#: in `build.sh`. The offload pair follows from the pinned driver's
#: configuration, `--enable-offload-targets=nvptx-none=…,amdgcn-amdhsa=…` (names
#: kept, joined by `:`) and `--enable-offload-defaulted`.
DRIVER_ADDED_VALUES = (
    ("COLLECT_GCC", "/usr/bin/gcc-15"),
    ("COLLECT_GCC_OPTIONS", COLLECT_GCC_OPTIONS),
    ("OFFLOAD_TARGET_DEFAULT", "1"),
    ("OFFLOAD_TARGET_NAMES", "nvptx-none:amdgcn-amdhsa"),
)
#: (FRESH-R4-HS-1) GCC's garbage-collector parameters, which `cc1` otherwise
#: selects at startup from the host's memory and resource limits and prints on
#: the `GGC heuristics:` line of `cc1.v`. `build.sh` fixes them; GCC keeps the
#: last value given, so each must reach the driver and `cc1` exactly once.
FIXED_PARAMS = (("ggc-min-expand", "100"), ("ggc-min-heapsize", "131072"))
#: The executables whose argument vectors must carry `FIXED_PARAMS`.
FIXED_PARAM_EXECUTABLES = ("/usr/bin/gcc-15", CC1)
_SOURCE_DIRS = (("OLDPWD", "{co}"), ("PWD", "{co}/infra/rp11-launch"))
#: The exact environment of each process class; ``{co}`` is the checkout.
ENV_CLASSES = (
    ("entry", BUILD_ENV + (("PWD", "{co}"),)),
    ("shell", BUILD_ENV),
    ("source", BUILD_ENV + _SOURCE_DIRS),
    ("compiler", BUILD_ENV + _SOURCE_DIRS + DRIVER_ADDED_VALUES),
    ("output", BUILD_ENV + (("OLDPWD", "{co}/infra/rp11-launch"), ("PWD", "{co}/build-out"))),
)
#: Every successful `execve` of the traced build, in order, and its class:
#: `build_argv`, then `build.sh` line by line.
EXEC_SEQUENCE = (
    ("/usr/bin/env", "entry"),
    ("/bin/sh", "shell"),
    ("/usr/bin/gcc-15", "source"),
    (CC1, "compiler"),
    ("/usr/bin/as", "source"),
    ("/usr/bin/as", "output"),
    ("/usr/bin/ld.bfd", "output"),
    ("/usr/bin/readelf", "output"),
    ("/usr/bin/objdump", "output"),
    ("/usr/bin/objdump", "output"),
)
EXECUTABLES = {
    "/usr/bin/env": "X-5", "/bin/sh": "X-6", "/usr/bin/gcc-15": "X-7",
    "/usr/libexec/gcc/x86_64-linux-gnu/15/cc1": "X-8", "/usr/bin/as": "X-9",
    "/usr/bin/ld.bfd": "X-10", "/usr/bin/objdump": "X-12", "/usr/bin/readelf": "X-13",
}
INPUTS = ("start.s", "launch.c", "select.h", "rp11-launch.ld", "build.sh")
PCH_PROBES = ("launch.c.gch", "select.h.gch")
STAT_CALLS = {"newfstatat", "stat", "lstat", "fstatat", "statx", "access", "faccessat",
              "faccessat2", "readlink", "readlinkat", "getcwd", "chdir"}

_LINE = re.compile(r"^(\d+) +(.*)$")
_CALL = re.compile(r"^([a-z_0-9]+)\((.*)\) += (-?\d+|\?)(?: (\w+))?")
_STR = re.compile(r'"((?:[^"\\]|\\.)*)"')
_DIRFD = re.compile(r"^(?:AT_FDCWD|\d+)<([^>]*)>, ")
_NAME = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
_ESCAPES = {"\\": 0x5C, '"': 0x22, "n": 0x0A, "t": 0x09, "r": 0x0D, "v": 0x0B, "f": 0x0C}


def expected_environment(env_class: str, checkout: str) -> dict[str, str]:
    """The exact environment of `env_class` for a run at `checkout`."""
    if checkout not in CONTROLLED_CHECKOUTS:
        raise ValueError(f"{checkout!r} is not a controlled checkout mount point")
    pairs = dict(ENV_CLASSES)[env_class]
    return {name: value.replace(CHECKOUT_TOKEN, checkout) for name, value in pairs}


def _parse_string(text: str, i: int) -> tuple[str, int]:
    """One strace-quoted string starting at `text[i]`; a truncated one fails."""
    if text[i:i + 1] != '"':
        raise ValueError(f"expected a string at offset {i}")
    out = bytearray()
    i += 1
    while True:
        if i >= len(text):
            raise ValueError("unterminated string")
        c = text[i]
        if c == '"':
            i += 1
            break
        if c != "\\":
            out += c.encode("utf-8", "surrogateescape")
            i += 1
            continue
        e = text[i + 1:i + 2]
        if e in _ESCAPES:
            out.append(_ESCAPES[e])
            i += 2
        elif e and e in "01234567":
            j = i + 1
            while j < min(i + 4, len(text)) and text[j] in "01234567":
                j += 1
            out.append(int(text[i + 1:j], 8) & 0xFF)
            i = j
        elif e == "x" and re.fullmatch(r"[0-9a-fA-F]{2}", text[i + 2:i + 4]):
            out.append(int(text[i + 2:i + 4], 16))
            i += 4
        else:
            raise ValueError(f"unknown escape at offset {i}")
    if text.startswith("...", i):
        raise ValueError("truncated string")
    return out.decode("utf-8", "surrogateescape"), i


def _parse_array(text: str, i: int) -> tuple[list[str], int]:
    """A complete strace string array; an abbreviated one fails."""
    if text[i:i + 1] != "[":
        raise ValueError(f"expected an array at offset {i}")
    i += 1
    items: list[str] = []
    if text[i:i + 1] == "]":
        return items, i + 1
    while True:
        item, i = _parse_string(text, i)
        items.append(item)
        if text[i:i + 1] == "]":
            return items, i + 1
        if text[i:i + 2] != ", ":
            raise ValueError(f"malformed array at offset {i}")
        i += 2


def parse_execve(args: str) -> tuple[str, list[str], list[str]]:
    """`execve`'s path, argument vector and environment, parsed exactly."""
    path, i = _parse_string(args, 0)
    if args[i:i + 2] != ", ":
        raise ValueError("malformed execve record")
    argv, i = _parse_array(args, i + 2)
    if args[i:i + 2] != ", ":
        raise ValueError("malformed execve record")
    env, i = _parse_array(args, i + 2)
    if i != len(args):
        raise ValueError("trailing text in execve record")
    return path, argv, env


def load_manifest(text: str):
    entries, links, excludes = {}, {}, []
    for line in text.splitlines()[1:]:
        if line.startswith("exclude "):
            excludes.append(line.split()[1])
            continue
        parts = line.split(" ")
        kind, path = parts[0], parts[5].encode().decode("unicode_escape")
        entries[path] = kind
        if kind == "l":
            links[path] = parts[7]
    return entries, links, excludes


def canonical(path: str, links: dict) -> str:
    """Resolve symbolic links component by component, using the manifest."""
    parts = [p for p in path.split("/") if p]
    out: list[str] = []
    hops = 0
    while parts:
        p = parts.pop(0)
        if p == ".":
            continue
        if p == "..":
            if out:
                out.pop()
            continue
        cand = "/" + "/".join(out + [p])
        if cand in links:
            hops += 1
            if hops > 40:
                raise ValueError(f"symlink loop at {cand}")
            target = links[cand]
            parts = [q for q in target.split("/") if q] + parts
            if target.startswith("/"):
                out = []
            continue
        out.append(p)
    return "/" + "/".join(out)


def _join_records(lines):
    """Rejoin `<unfinished ...>` / `<... resumed>` halves by process id."""
    pending: dict[str, str] = {}
    for raw in lines:
        m = _LINE.match(raw)
        if not m:
            continue
        pid, body = m.groups()
        if body.endswith("<unfinished ...>"):
            pending[pid] = body[: -len("<unfinished ...>")].rstrip()
            continue
        r = re.match(r"^<\.\.\. [a-z_0-9]+ resumed>(.*)$", body)
        if r and pid in pending:
            body = pending.pop(pid) + r.group(1)
        yield pid, body


def check(trace: str, manifest_text: str, checkout: str) -> dict:
    entries, links, excludes = load_manifest(manifest_text)
    cwd: dict[str, str] = {}
    failures: list[str] = []
    executed: dict[str, int] = {}
    proc_sys: set[str] = set()
    pch_probes: set[str] = set()
    envs: list[dict] = []
    sequence: list[str] = []
    if checkout not in CONTROLLED_CHECKOUTS:
        failures.append(f"{checkout!r} is not a controlled checkout mount point {list(CONTROLLED_CHECKOUTS)}")
    src_dir = posixpath.join(checkout, "infra/rp11-launch")
    checkout_dirs = {checkout, posixpath.join(checkout, "infra"), src_dir}
    inputs = {posixpath.join(src_dir, n) for n in INPUTS}
    out_dir = posixpath.join(checkout, "build-out")
    images: dict[str, str] = {}

    for pid, body in _join_records(trace.splitlines()):
        m = _CALL.match(body)
        if not m:
            continue
        call, args, result, errno = m.groups()
        cur = cwd.setdefault(pid, checkout)
        if call in ("vfork", "fork", "clone", "clone3") and result.isdigit():
            cwd[result] = cur
            images[result] = images.get(pid, "")
            continue
        strings = _STR.findall(args)
        if call == "getcwd":
            continue
        if call in ("exit_group", "wait4", "fchdir") or not strings:
            if call == "fchdir":
                failures.append(f"{pid}: fchdir is not expected in R-2")
            continue
        d = _DIRFD.match(args)
        base = d.group(1) if d else cur
        path = strings[0]
        full = path if path.startswith("/") else posixpath.join(base, path)
        ok = result != "?" and not result.startswith("-")

        if call == "execve":
            if ok:
                try:
                    path, argv, env = parse_execve(args)
                except ValueError as exc:
                    failures.append(f"{pid}: malformed execve record ({exc})")
                    path, argv, env = strings[0], None, None
                if path in FIXED_PARAM_EXECUTABLES and argv is not None:
                    _check_fixed_params(pid, path, argv, failures)
                tool = EXECUTABLES.get(path)
                if tool is None:
                    failures.append(f"{pid}: executed {path}, which is not a lock tool")
                executed[path] = executed.get(path, 0) + 1
                images[pid] = path
                position = len(sequence)
                sequence.append(path)
                want = EXEC_SEQUENCE[position] if position < len(EXEC_SEQUENCE) else None
                envs.append({"pid": pid, "path": path, "class": want[1] if want else None, "env": env})
                if want is None or want[0] != path:
                    failures.append(f"{pid}: execve #{position + 1} is {path}; the build defines "
                                    f"{want[0] if want else 'no further execve'}")
                elif env is not None and checkout in CONTROLLED_CHECKOUTS:
                    _check_env(pid, path, env, expected_environment(want[1], checkout), cur, failures)
            else:
                failures.append(f"{pid}: execve {path} failed ({errno})")
            continue

        if call == "chdir" and ok:
            cwd[pid] = full if full.startswith("/") else posixpath.join(cur, full)
            cwd[pid] = posixpath.normpath(cwd[pid])

        norm = posixpath.normpath(full)
        creating = "O_CREAT" in args
        if norm.startswith(checkout + "/") or norm == checkout:
            if norm in inputs or norm == out_dir or norm.startswith(out_dir + "/"):
                continue
            if norm in checkout_dirs and call in STAT_CALLS:
                continue
            if norm in {posixpath.join(src_dir, n) for n in PCH_PROBES} and not ok:
                pch_probes.add(norm)
                continue
            failures.append(f"{pid}: {call} {norm} in the checkout is not an input or build-out")
            continue
        if norm == "/dev/null":
            continue
        if norm.startswith("/proc/") or norm == "/proc" or norm.startswith("/sys/"):
            proc_sys.add(norm)
            continue
        if norm.startswith("/dev/"):
            failures.append(f"{pid}: {call} {norm} is a device other than /dev/null")
            continue
        try:
            canon = canonical(norm, links)
        except ValueError as exc:
            failures.append(str(exc))
            continue
        if creating and (canon.startswith("/tmp") or canon.startswith("/var/tmp")):
            failures.append(f"{pid}: creates {canon} under a temporary directory")
        excluded = next((x for x in excludes if canon == x or canon.startswith(x + "/")), None)
        if excluded:
            failures.append(f"{pid}: {call} {canon} lies under the excluded {excluded}")
        elif ok and canon not in entries:
            failures.append(f"{pid}: {call} {canon} succeeded but is not in the manifest")
        elif not ok and canon in entries and errno == "ENOENT":
            failures.append(f"{pid}: {call} {canon} is in the manifest but was not found")

    want = set(EXECUTABLES)
    missing = sorted(want - set(executed))
    if missing:
        failures.append(f"tools never executed: {missing}")
    if len(sequence) != len(EXEC_SEQUENCE):
        failures.append(f"the traced build made {len(sequence)} successful execve calls; "
                        f"the build defines {len(EXEC_SEQUENCE)}")
    return {
        "checkout": checkout,
        "executed": dict(sorted(executed.items())),
        "exec_sequence": sequence,
        "environments": envs,
        "proc_sys_paths": sorted(proc_sys),
        "pch_probes": sorted(pch_probes),
        "failures": failures,
        "verdict": "pass" if not failures else "fail",
    }


def _check_fixed_params(pid, path, argv, failures) -> None:
    """Each fixed parameter exactly once, as its one canonical token; no other
    token naming it; no response file."""
    for name, value in FIXED_PARAMS:
        token = f"--param={name}={value}"
        count = argv[1:].count(token)
        if count != 1:
            failures.append(f"{pid}: {path}: {token} appears {count} times, not once")
        others = [a for a in argv[1:] if name in a and a != token]
        if others:
            failures.append(f"{pid}: {path}: {name} is also given as {others!r}")
    responses = [a for a in argv[1:] if a.startswith("@")]
    if responses:
        failures.append(f"{pid}: {path}: response-file argument {responses!r}")


def _check_env(pid, path, env, expected, cwd, failures) -> None:
    """The received environment must equal `expected` exactly."""
    pairs: dict[str, str] = {}
    for entry in env:
        name, sep, value = entry.partition("=")
        if not sep or not _NAME.fullmatch(name):
            failures.append(f"{pid}: {path}: malformed environment entry {entry!r}")
            continue
        if name in pairs:
            failures.append(f"{pid}: {path}: duplicated environment variable {name}")
            continue
        pairs[name] = value
    for name in sorted(set(expected) - set(pairs)):
        failures.append(f"{pid}: {path}: required environment variable {name} is missing")
    for name in sorted(set(pairs) - set(expected)):
        failures.append(f"{pid}: {path}: unexpected environment variable {name}")
    for name in sorted(set(pairs) & set(expected)):
        if pairs[name] != expected[name]:
            failures.append(f"{pid}: {path}: {name} is {pairs[name]!r}, not {expected[name]!r}")
    if "PWD" in pairs and pairs["PWD"] != cwd:
        failures.append(f"{pid}: {path}: PWD {pairs['PWD']!r} is not its working directory {cwd!r}")


def main(argv: list[str]) -> int:
    import argparse

    p = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    p.add_argument("--trace", type=Path, required=True)
    p.add_argument("--manifest", type=Path, required=True)
    p.add_argument("--checkout", default="/rp11/co")
    a = p.parse_args(argv)
    result = check(a.trace.read_text(), a.manifest.read_text(), a.checkout)
    print(json.dumps(result, indent=1, sort_keys=True))
    return 0 if result["verdict"] == "pass" else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
