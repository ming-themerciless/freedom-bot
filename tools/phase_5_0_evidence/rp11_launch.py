"""`rp11-launch/1`: the static first image's contract, as reviewed data.

C-P5.0-R5-RP11-I1-R3-R4-I7, 2026-10-01. Implements the Python side of the
accepted D2-R2 design
(`docs/review/phase-5-0-p5-r5-rp11-i1-r3-r4-d2-static-launcher-design-proposal.md`,
§5.4 … §5.9, §5.11, §5.14, §5.15). The image's source and build definition
are `infra/rp11-launch/`; the C literals there and the values here are one
contract in two copies, and T-L2 asserts that they agree byte for byte.

**This module is data.** It reads no file, starts no process and is wired to
nothing. It is in the planning tier rather than beside the (not yet
implemented) `execution/entry_environment.py` that R2 §9 names, because it
needs none of that tier's permissions. Nothing here installs, builds or runs
`rp11-launch`, and nothing here satisfies RP-11: PO-9 and PO-14 remain open,
`plan.is_executable` remains `False`, and RP-11 remains unwired and unmet.

**T-L2 is partial.** R2 T-B14 and proposal T-L2 compare the C literals with
`entry_environment.KEY_SETS["LB-2S"]` and `LITERALS`. That module belongs to
R2 slice I-6, which is unimplemented; on Peter Duscha's 2026-10-01 direction
the comparison is made against the values below, transcribed from R2
§4.4.3.4 and §7.9, and the `entry_environment` half remains owed by I-6.
"""
from __future__ import annotations

import hashlib

from .errors import PlanRefused

CONTRACT_ID = "rp11-launch/1"
ARCHITECTURE = "x86_64"
MINIMUM_KERNEL = (5, 9)

# -- §5.5 accepted argv ------------------------------------------------------

ARGC = 3
#: argv[1] and argv[2]; argv[0] is not examined (V-7).
ACCEPTED_ARGUMENTS = ("--pass", "A")

# -- §5.6 envp handling ------------------------------------------------------

INVOCATION_ID_NAME = "INVOCATION_ID"
INVOCATION_ID_GRAMMAR = "[0-9a-f]{32}"
INVOCATION_ID_LENGTH = 32

# -- §5.8 the literal execve (R2 §4.4.3.4 item 5; §7.9 LB-2S) -----------------

EXECVE_PATH = "/usr/bin/python3.12"
EXECVE_ARGV = (
    "/usr/bin/python3.12",
    "-I",
    "-S",
    "/usr/local/libexec/freedom-blades-rp11/rp11_entry.py",
    "run",
    "--pass",
    "A",
)
#: The entry's environment, in order; the third is `INVOCATION_ID=` and the 32
#: selected bytes. Its key set is R2 §7.9's LB-2S set.
EXECVE_ENV_LITERALS = ("LC_ALL=C", "PATH=/usr/bin")
EXECVE_ENV_KEYS = ("LC_ALL", "PATH", "INVOCATION_ID")
LB_2S_KEY_SET = ("INVOCATION_ID", "LC_ALL", "PATH")

# -- §5.9 statuses and diagnostics ---------------------------------------------

STATUSES = (
    (111, "launch-usage"),
    (112, "launch-invocation-id"),
    (113, "launch-stdio"),
    (114, "launch-descriptors"),
    (115, "launch-signals"),
    (116, "launch-chdir"),
    (117, "launch-exec-failed"),
)
RESERVED_STATUSES = (110, 118, 119)


def diagnostic_line(class_name: str) -> str:
    """The exact bytes written to descriptor 2 for one class (§5.9)."""
    return f"{CONTRACT_ID}: {class_name}\n"


# -- §5.4 the closed system-call inventory -------------------------------------

SYSCALLS = (
    ("write", 1),
    ("rt_sigaction", 13),
    ("rt_sigprocmask", 14),
    ("execve", 59),
    ("fcntl", 72),
    ("chdir", 80),
    ("umask", 95),
    ("exit_group", 231),
    ("close_range", 436),
)
SIGNALS_RESET = tuple(s for s in range(1, 65) if s not in (9, 19))

# -- §5.14 control-transfer and stack contract (T-L10) -------------------------

FUNCTIONS = ("_start", "rp11_main")
#: The permitted instruction list, fixed from the first build (2026-10-01) and
#: reviewed, in the listing's spelling. It contains no `call` and no `ret`.
#: Adding to it is a reviewed contract change (§5.14.1).
PERMITTED_MNEMONICS = (
    "add", "and", "cmp", "cmpb", "dec", "inc", "ja", "jbe", "je", "jmp", "jne",
    "lea", "mov", "movabs", "movb", "movl", "movq", "movw", "push", "shr",
    "sub", "syscall", "test", "ud2", "xor",
)
CONDITIONAL_JUMPS = ("ja", "jbe", "je", "jne")
FRAME_BOUND = 512
STACK_BOUND = 1024
#: rp11_main's frame in the first build: `push %rbx` and `sub $0xc0,%rsp`.
EXPECTED_FRAME = 200
#: 15 bytes of worst-case alignment, `_start`'s pushed word, and the frame.
EXPECTED_STACK_DEPTH = 223

# -- §5.3 build contract ---------------------------------------------------------

BUILD_ARGV = (
    "/usr/bin/env", "-i", "LC_ALL=C", "PATH=/usr/bin", "SOURCE_DATE_EPOCH=0",
    "TZ=UTC0", "/bin/sh", "infra/rp11-launch/build.sh", "build-out",
)
BUILD_ENV = ("LC_ALL=C", "PATH=/usr/bin", "SOURCE_DATE_EPOCH=0", "TZ=UTC0")
#: Established by IC-1 (§5.3.7): the names the shell adds for its children.
#: Their exact values are `IC1_ENV_CLASSES`.
SHELL_ADDED_ENV = ("OLDPWD", "PWD")
#: Recorded by IC-1 and named for review, not foreseen by the design text:
#: bubblewrap sets `PWD` for the first process (X-3 → X-5), and the compiler
#: driver sets four variables for `cc1` (X-7 → X-8). Their exact values are
#: `IC1_ENV_CLASSES` and `DRIVER_ADDED_ENV_VALUES`.
ENTRY_ADDED_ENV = ("PWD",)
DRIVER_ADDED_ENV = ("COLLECT_GCC", "COLLECT_GCC_OPTIONS", "OFFLOAD_TARGET_DEFAULT", "OFFLOAD_TARGET_NAMES")

# -- IC-1's exact environment contract (§5.3.7; I-7-R1, finding I7-R1-1) ---------

#: The checkout mount points a traced build may use: R-2, R-4(b) and R-4(c) at
#: the first, R-4(a) at the second. ``{co}`` below stands for the run's own.
IC1_CONTROLLED_CHECKOUTS = ("/rp11/co", "/rp11/alt/checkout")
IC1_CHECKOUT_TOKEN = "{co}"
#: The driver's additions for `cc1`, **specified, not observed**: `COLLECT_GCC`
#: is `build.sh`'s driver `argv[0]`; `COLLECT_GCC_OPTIONS` is GCC 15's
#: `set_collect_gcc_options` over `build.sh`'s driver vector after the driver's
#: `prune_options` (the later `-fno-pie` cancels `-fno-pic` through the
#: `Negative()` chain), with `-U` and `-o` in separate canonical form and the
#: driver's `-dumpdir` last; the offload pair follows from the pinned driver's
#: `--enable-offload-targets=nvptx-none=…,amdgcn-amdhsa=…` and
#: `--enable-offload-defaulted`.
DRIVER_ADDED_ENV_VALUES = (
    "COLLECT_GCC=/usr/bin/gcc-15",
    "COLLECT_GCC_OPTIONS="
    "'-S' '-v' '-std=c11' '-ffreestanding' '-nostdinc' '-fno-builtin' '-fno-pie' "
    "'-fno-stack-protector' '-fno-stack-clash-protection' '-fcf-protection=none' "
    "'-mindirect-branch=keep' '-mfunction-return=keep' '-fno-asynchronous-unwind-tables' "
    "'-fno-unwind-tables' '-fno-jump-tables' '-fno-tree-vectorize' '-fno-common' '-fno-ident' "
    "'-fno-optimize-sibling-calls' '-fno-reorder-blocks-and-partition' '-fno-partial-inlining' "
    "'-fno-ipa-cp-clone' '-fno-ipa-sra' '-fno-tree-loop-distribute-patterns' '-fomit-frame-pointer' "
    "'-falign-functions=1' '-falign-jumps=1' '-falign-loops=1' '-falign-labels=1' "
    "'-mgeneral-regs-only' '-mno-red-zone' '-march=x86-64' '-mtune=generic' "
    "'-frandom-seed=rp11-launch' '-Os' '-g0' '-U' '_FORTIFY_SOURCE' '-Wall' '-Wextra' '-Wvla' "
    "'-Werror' '-o' '../../build-out/launch.s' '-dumpdir' '../../build-out/'",
    "OFFLOAD_TARGET_DEFAULT=1",
    "OFFLOAD_TARGET_NAMES=nvptx-none:amdgcn-amdhsa",
)
_IC1_SOURCE_DIRS = ("OLDPWD={co}", "PWD={co}/infra/rp11-launch")
#: The exact environment, as a complete set of entries, of each process class.
IC1_ENV_CLASSES = (
    ("entry", BUILD_ENV + ("PWD={co}",)),
    ("shell", BUILD_ENV),
    ("source", BUILD_ENV + _IC1_SOURCE_DIRS),
    ("compiler", BUILD_ENV + _IC1_SOURCE_DIRS + DRIVER_ADDED_ENV_VALUES),
    ("output", BUILD_ENV + ("OLDPWD={co}/infra/rp11-launch", "PWD={co}/build-out")),
)
#: Every successful `execve` of the traced build, in order, with its class.
IC1_EXEC_SEQUENCE = (
    ("/usr/bin/env", "entry"),
    ("/bin/sh", "shell"),
    ("/usr/bin/gcc-15", "source"),
    ("/usr/libexec/gcc/x86_64-linux-gnu/15/cc1", "compiler"),
    ("/usr/bin/as", "source"),
    ("/usr/bin/as", "output"),
    ("/usr/bin/ld.bfd", "output"),
    ("/usr/bin/readelf", "output"),
    ("/usr/bin/objdump", "output"),
    ("/usr/bin/objdump", "output"),
)


def ic1_environment(env_class: str, checkout: str) -> tuple[str, ...]:
    """The exact environment entries of `env_class` for a run at `checkout`."""
    if checkout not in IC1_CONTROLLED_CHECKOUTS:
        raise ValueError(f"{checkout!r} is not a controlled checkout mount point")
    entries = dict(IC1_ENV_CLASSES)[env_class]
    return tuple(e.replace(IC1_CHECKOUT_TOKEN, checkout) for e in entries)

# -- expected digests (§5.11; equal to infra/rp11-launch/expected.sha256) -------

EXPECTED_IMAGE_SHA256 = "04218ed2d834c1c7abe417a850831d8956f087711befd692eefc2e61b2668572"
EXPECTED_LISTING_SHA256 = "8c1fedee1c717b17a14d7c746669ffcec3c41d155e5cc4c63d24a5f2527cd188"
EXPECTED_MAP_SHA256 = "5a8b058084edcb1e3f6f7ddea13b60da6af71102300ea276225ae4ab0e8bc34d"
EXPECTED_LAUNCH_S_SHA256 = "b37280d53eecce690210021a793cde5d5b73a8f9c027d187e4bd1338e7e27706"
TOOLCHAIN_LOCK_SHA256 = "f92380735e32f9d7747834d684657d4087f14c7a22c0178703a50a70eef784cf"
BUILD_ROOT_MANIFEST_SHA256 = "f08ba9de4374374fa91012021ce12fb83f6370be5547ee4e214232100c38e76f"

# -- independent decoding (§5.15, XD-8) -------------------------------------------

XD_SOURCE_SHA256 = "84598d0683f377fcdb2282ae8080d07d4ce144e46adcc236d1d0677766038c97"
XD_SPELLING_TABLE_SHA256 = "d20406488804d7d3559917a3d55512d44b40789c018849977d6737a86ba67b66"
#: XD's decoded stream of the expected image (T-L11's agreed stream).
AGREED_STREAM_SHA256 = "e1354c29e4abddd115fad9b1f83fd69b3b93aae2971db6a448964baa8edbf8e0"


# -- cc1.v diagnostic baseline fixture (C-P5.0-R5-RP11-I1-R3-R4-R5-B1-R2) -----

CC1_V_BASELINE_PATH = "infra/rp11-launch/verify/fixtures/cc1.v.baseline"
CC1_V_BASELINE_LENGTH = 5120
CC1_V_BASELINE_SHA256 = (
    "b77f92dcdcf899c5459fec606f16dc325ed5329516cbab5faea86b479992905b"
)


def verify_cc1_v_baseline(
    data: bytes,
    expected_length: int = CC1_V_BASELINE_LENGTH,
    expected_sha256: str = CC1_V_BASELINE_SHA256,
) -> dict[str, object]:
    """Verify that fixture bytes satisfy the cc1.v baseline contract.

    Checks:
    - exact byte length == expected_length (5120)
    - exact SHA-256 == expected_sha256 (b77f92dcdcf899c5459fec606f16dc325ed5329516cbab5faea86b479992905b)

    Raises PlanRefused if length or SHA-256 does not match.
    Returns the serialized baseline dictionary:
        {
            "byte_length": expected_length,
            "path": CC1_V_BASELINE_PATH,
            "sha256": expected_sha256,
        }
    """
    actual_length = len(data)
    if actual_length != expected_length:
        raise PlanRefused(
            f"The cc1.v baseline fixture {CC1_V_BASELINE_PATH!r} length {actual_length} "
            f"does not match expected length {expected_length}."
        )
    actual_sha256 = hashlib.sha256(data).hexdigest()
    if actual_sha256 != expected_sha256:
        raise PlanRefused(
            f"The cc1.v baseline fixture {CC1_V_BASELINE_PATH!r} sha256 {actual_sha256!r} "
            f"does not match expected sha256 {expected_sha256!r}."
        )
    return {
        "byte_length": expected_length,
        "path": CC1_V_BASELINE_PATH,
        "sha256": expected_sha256,
    }


def control_contract() -> dict:
    """The contract data T-L10 checks the agreed stream against."""
    return {
        "functions": list(FUNCTIONS),
        "permitted_mnemonics": list(PERMITTED_MNEMONICS),
        "conditional_jumps": list(CONDITIONAL_JUMPS),
        "frame_bound": FRAME_BOUND,
        "stack_bound": STACK_BOUND,
        "expected_frame": EXPECTED_FRAME,
        "syscalls": {str(number): name for name, number in SYSCALLS},
        "status_lines": {
            str(status): {"line": diagnostic_line(name), "status": status}
            for status, name in STATUSES
        },
        "execve_path": EXECVE_PATH,
        "execve_argv": list(EXECVE_ARGV),
        "execve_env_literals": list(EXECVE_ENV_LITERALS),
        "invocation_id_prefix": INVOCATION_ID_NAME + "=",
    }


def manifest_section(baseline: dict[str, object] | bytes | None = None) -> dict:
    """The serialised `rp11_launch` section of the review manifest (§5.11).

    Review input only. Its presence pins what a later H-1 would compare the
    installed image against; it authorizes no build, installation or pass.
    """
    if isinstance(baseline, bytes):
        baseline_data = verify_cc1_v_baseline(baseline)
    elif isinstance(baseline, dict):
        baseline_data = dict(baseline)
    elif baseline is None:
        baseline_data = {
            "byte_length": CC1_V_BASELINE_LENGTH,
            "path": CC1_V_BASELINE_PATH,
            "sha256": CC1_V_BASELINE_SHA256,
        }
    else:
        raise TypeError(f"Invalid baseline parameter type: {type(baseline)}")

    return {
        "contract": CONTRACT_ID,
        "architecture": ARCHITECTURE,
        "minimum_kernel": ".".join(str(p) for p in MINIMUM_KERNEL),
        "argc": ARGC,
        "accepted_arguments": list(ACCEPTED_ARGUMENTS),
        "invocation_id": {
            "name": INVOCATION_ID_NAME,
            "grammar": INVOCATION_ID_GRAMMAR,
        },
        "execve": {
            "path": EXECVE_PATH,
            "argv": list(EXECVE_ARGV),
            "env_literals": list(EXECVE_ENV_LITERALS),
            "env_keys": list(EXECVE_ENV_KEYS),
        },
        "statuses": [
            {"status": s, "class": c, "line": diagnostic_line(c)} for s, c in STATUSES
        ],
        "syscalls": [{"name": n, "number": k} for n, k in SYSCALLS],
        "control": control_contract(),
        "expected_stack_depth": EXPECTED_STACK_DEPTH,
        "build": {
            "argv": list(BUILD_ARGV),
            "env": list(BUILD_ENV),
            "shell_added_env": list(SHELL_ADDED_ENV),
            "entry_added_env": list(ENTRY_ADDED_ENV),
            "driver_added_env": list(DRIVER_ADDED_ENV),
            "ic1_environment": {
                "controlled_checkouts": list(IC1_CONTROLLED_CHECKOUTS),
                "checkout_token": IC1_CHECKOUT_TOKEN,
                "classes": {name: list(entries) for name, entries in IC1_ENV_CLASSES},
                "exec_sequence": [{"path": p, "class": c} for p, c in IC1_EXEC_SEQUENCE],
                "comparison": "exact",
            },
        },
        "expected_sha256": {
            "image": EXPECTED_IMAGE_SHA256,
            "listing": EXPECTED_LISTING_SHA256,
            "map": EXPECTED_MAP_SHA256,
            "launch_s": EXPECTED_LAUNCH_S_SHA256,
            "toolchain_lock": TOOLCHAIN_LOCK_SHA256,
            "build_root_manifest": BUILD_ROOT_MANIFEST_SHA256,
        },
        "independent_decoding": {
            "xdecode_py_sha256": XD_SOURCE_SHA256,
            "spelling_table_sha256": XD_SPELLING_TABLE_SHA256,
            "agreed_stream_sha256": AGREED_STREAM_SHA256,
        },
        "cc1_v_baseline": baseline_data,
        "installed": False,
        "wired": False,
    }


__all__ = [
    "ACCEPTED_ARGUMENTS", "AGREED_STREAM_SHA256", "ARCHITECTURE", "ARGC",
    "BUILD_ARGV", "BUILD_ENV", "BUILD_ROOT_MANIFEST_SHA256",
    "CC1_V_BASELINE_LENGTH", "CC1_V_BASELINE_PATH", "CC1_V_BASELINE_SHA256",
    "CONDITIONAL_JUMPS", "CONTRACT_ID", "DRIVER_ADDED_ENV",
    "DRIVER_ADDED_ENV_VALUES", "ENTRY_ADDED_ENV", "EXECVE_ARGV",
    "EXECVE_ENV_KEYS", "EXECVE_ENV_LITERALS", "EXECVE_PATH",
    "EXPECTED_FRAME", "EXPECTED_IMAGE_SHA256", "EXPECTED_LAUNCH_S_SHA256",
    "EXPECTED_LISTING_SHA256", "EXPECTED_MAP_SHA256", "EXPECTED_STACK_DEPTH",
    "FRAME_BOUND", "FUNCTIONS", "IC1_CHECKOUT_TOKEN", "IC1_CONTROLLED_CHECKOUTS",
    "IC1_ENV_CLASSES", "IC1_EXEC_SEQUENCE", "INVOCATION_ID_GRAMMAR", "INVOCATION_ID_LENGTH",
    "INVOCATION_ID_NAME", "LB_2S_KEY_SET", "MINIMUM_KERNEL", "PERMITTED_MNEMONICS",
    "RESERVED_STATUSES", "SHELL_ADDED_ENV", "SIGNALS_RESET", "STACK_BOUND",
    "STATUSES", "SYSCALLS", "TOOLCHAIN_LOCK_SHA256", "XD_SOURCE_SHA256",
    "XD_SPELLING_TABLE_SHA256", "control_contract", "diagnostic_line",
    "ic1_environment", "manifest_section", "verify_cc1_v_baseline",
]
