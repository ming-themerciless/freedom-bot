"""rp11-launch/1 toolchain-free tests (C-P5.0-R5-RP11-I1-R3-R4-I7).

T-L1 … T-L4, T-L10, T-L12 and the consistency of the committed launcher files
(proposal §5.12.1). They need no compiler and run in the ordinary suite.

**What they check is source text, committed files and the committed listing —
not the built image.** T-L10 here runs over the committed listing; its verdict
is evidence about the image only together with a passing T-L11 over the same
listing digest and an image whose digest equals `expected.sha256` (XD-7), which
is `tests/test_rp11_launch_toolchain.py`'s job. T-L12 tests XD against its
author's reading of the manuals, not the manuals themselves (AD-14).
"""
from __future__ import annotations

import hashlib
import json
import re

import pytest

from tests import rp11_launch_support as S
from tools.phase_5_0_evidence import rp11_launch as C

XD = S.load("xdecode")
CTV = S.load("ctverify")
ELF = S.load("elfcheck")
IC1 = S.load("ic1check")
ENTER = S.load("enter", S.BUILDROOT)

START_S = (S.LAUNCH / "start.s").read_text()
LAUNCH_C = (S.LAUNCH / "launch.c").read_text()
SELECT_H = (S.LAUNCH / "select.h").read_text()
BUILD_SH = (S.LAUNCH / "build.sh").read_text()
LINKER = (S.LAUNCH / "rp11-launch.ld").read_text()
LOCK = (S.LAUNCH / "toolchain.lock").read_text()
MANIFEST = (S.LAUNCH / "build-root.manifest").read_text()
LISTING = S.LISTING.read_text()
SPELLING = (S.VERIFY / "xdecode-spelling.table").read_text()
CORPUS = (S.VERIFY / "xdecode-corpus.txt").read_text()


def _sha(path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _code(text: str) -> str:
    """C text without comments."""
    return re.sub(r"/\*.*?\*/", "", text, flags=re.S)


# ---------------------------------------------------------------------------
# T-L1 — source structure (SR-1 … SR-8). Source text, not the built image.
# ---------------------------------------------------------------------------


def test_tl1_the_only_include_is_select_h_in_launch_c() -> None:
    assert [l for l in _code(LAUNCH_C).splitlines() if l.lstrip().startswith("#")] == ['#include "select.h"']
    assert not [l for l in _code(SELECT_H).splitlines() if l.lstrip().startswith("#")]
    assert "#" not in "".join(l.split("#", 1)[0] for l in START_S.splitlines() if not l.lstrip().startswith("#"))


def test_tl1_select_h_is_two_pure_always_inline_functions() -> None:
    code = _code(SELECT_H)
    defs = re.findall(r"static inline __attribute__\(\(always_inline\)\) (?:int|const char \*)\n(\w+)\(", code)
    assert defs == ["rp11_check_argv", "rp11_select_invocation_id"]
    for forbidden in ("asm", "syscall", "extern", "volatile"):
        assert forbidden not in code
    assert re.findall(r"\bstatic\b", code) == ["static", "static"]          # the two inline functions only
    assert not re.search(r"\]\s*=[^=]", code), "a store through an index (SR-2)"
    assert not re.search(r"^\s*\*+\s*[\w(]", code, re.M), "a store through a pointer (SR-2)"
    assert not re.search(r"\+\+\s*\*|\*\w+\s*\+\+", code)
    assert "->" not in code


def test_tl1_start_s_has_no_call_or_ret_and_ends_in_the_entry_jmp() -> None:
    insns = [l.split("#")[0].strip() for l in START_S.splitlines()]
    insns = [l for l in insns if l and not l.startswith(".") and not l.endswith(":")]
    assert insns == [
        "xorl	%ebp, %ebp", "movq	(%rsp), %rdi", "leaq	8(%rsp), %rsi",
        "leaq	16(%rsp,%rdi,8), %rdx", "andq	$-16, %rsp", "pushq	$0", "jmp	rp11_main",
    ]
    assert re.findall(r"^\s*\.globl\s+(\w+)", START_S, re.M) == ["_start"]
    assert not re.search(r"\b(call|ret)\w*\b", "\n".join(insns))


def test_tl1_rp11_main_is_the_only_non_inline_function_and_is_noreturn() -> None:
    code = _code(LAUNCH_C)
    functions = re.findall(r"^(?:static inline __attribute__\(\([^)]*\)\) )?\w[\w *]*\n(\w+)\(", code, re.M)
    assert "rp11_main" in functions
    for name in functions:
        if name == "rp11_main":
            continue
        assert re.search(rf"static inline __attribute__\(\(always_inline[^)]*\)\) \w[\w *]*\n{name}\(", code), name
    assert "__attribute__((noreturn, used)) void rp11_main(" in code
    assert "(*" not in code, "function pointer"
    assert "alloca" not in code and "= {" not in code and "struct" not in code


def test_tl1_every_system_call_number_is_in_the_inventory() -> None:
    enum = dict(re.findall(r"RP11_SYS_(\w+) = (\d+)", LAUNCH_C))
    assert {k.lower(): int(v) for k, v in enum.items()} == dict(C.SYSCALLS)
    used = set(re.findall(r"rp11_syscall\d\(RP11_SYS_(\w+)", LAUNCH_C))
    assert used == set(enum)


def test_tl1_every_exit_group_is_followed_by_builtin_trap() -> None:
    sites = [m.start() for m in re.finditer(r"rp11_syscall1\(RP11_SYS_EXIT_GROUP", LAUNCH_C)]
    assert len(sites) == 1
    after = LAUNCH_C[sites[0]:].split("\n")[1].strip()
    assert after == "__builtin_trap();"


def test_tl1_the_invocation_id_copy_is_32_written_out_constant_index_assignments() -> None:
    copies = re.findall(r"idbuf\[(\d+)\] = id\[(\d+)\];", LAUNCH_C)
    assert copies == [(str(14 + k), str(k)) for k in range(32)]
    # SR-3: the one loop in rp11_main writes no memory.
    loops = re.findall(r"for \(([^)]*)\) \{(.*?)\n\t\}", _code(LAUNCH_C), re.S)
    assert len(loops) == 1
    assert not re.search(r"[^=!<>]=[^=]", loops[0][1].replace("s == ", "").replace("!= 0", ""))


# ---------------------------------------------------------------------------
# T-L2 — literal drift (partial: entry_environment is owed by R2 slice I-6)
# ---------------------------------------------------------------------------


def test_tl2_execve_literals_equal_the_contract() -> None:
    argv = re.findall(r'argv_out\[(\d)\] = "([^"]*)";', LAUNCH_C)
    assert [v for _k, v in sorted(argv)] == list(C.EXECVE_ARGV)
    assert re.search(r"argv_out\[7\] = 0;", LAUNCH_C)
    env = re.findall(r'envp_out\[(\d)\] = "([^"]*)";', LAUNCH_C)
    assert [v for _k, v in sorted(env)] == list(C.EXECVE_ENV_LITERALS)
    assert "envp_out[2] = idbuf;" in LAUNCH_C and "envp_out[3] = 0;" in LAUNCH_C
    assert f'rp11_syscall3(RP11_SYS_EXECVE, (long)"{C.EXECVE_PATH}"' in LAUNCH_C
    prefix = "".join(re.findall(r"idbuf\[(?:\d|1[0-3])\] = '(.)';", LAUNCH_C))
    assert prefix == C.INVOCATION_ID_NAME + "="


def test_tl2_status_lines_and_lengths_equal_the_contract() -> None:
    fails = re.findall(r'rp11_fail\("([^"]*)\\n", (\d+), (\d+)\)', LAUNCH_C)
    by_status = {}
    for line, length, status in fails:
        by_status.setdefault(int(status), set()).add((line + "\n", int(length)))
    assert sorted(by_status) == [s for s, _c in C.STATUSES]
    for status, name in C.STATUSES:
        want = C.diagnostic_line(name)
        assert by_status[status] == {(want, len(want.encode()))}


def test_tl2_selection_literals_equal_the_contract() -> None:
    name = "".join(re.findall(r"\be\[(\d+)\] != '(.)'", SELECT_H)[k][1] for k in range(13))
    assert name == C.INVOCATION_ID_NAME
    passed = "".join(c for _i, c in re.findall(r"pass\[(\d)\] != '(.)'", SELECT_H))
    assert passed == C.ACCEPTED_ARGUMENTS[0]
    assert "value[0] != 'A'" in SELECT_H and "argc != 3" in SELECT_H
    assert "i < 32" in SELECT_H and "candidate[32] != '\\0'" in SELECT_H


def test_tl2_the_lb_2s_key_set_is_r2_section_7_9() -> None:
    """Against R2 §7.9's LB-2S key set as transcribed. The comparison with
    `entry_environment.KEY_SETS["LB-2S"]` and `LITERALS` is owed by R2 slice I-6,
    which is unimplemented (Peter Duscha's direction, 2026-10-01)."""
    assert tuple(sorted(C.EXECVE_ENV_KEYS)) == C.LB_2S_KEY_SET == ("INVOCATION_ID", "LC_ALL", "PATH")
    assert [e.split("=")[0] for e in C.EXECVE_ENV_LITERALS] == ["LC_ALL", "PATH"]


# ---------------------------------------------------------------------------
# T-L3 — build definition, lock and tree manifest
# ---------------------------------------------------------------------------

#: Proposal §5.3.3, transcribed, with the two fixed GCC parameters of the
#: FRESH-R4-HS-1 remediation (C-P5.0-R5-RP11-FRESH-R5-R4-D1) after the seed.
COMPILE_VECTOR = """-S -v -std=c11 -ffreestanding -nostdinc -fno-builtin
-fno-pic -fno-pie -fno-stack-protector -fno-stack-clash-protection
-fcf-protection=none -mindirect-branch=keep -mfunction-return=keep
-fno-asynchronous-unwind-tables -fno-unwind-tables
-fno-jump-tables -fno-tree-vectorize -fno-common -fno-ident
-fno-optimize-sibling-calls -fno-reorder-blocks-and-partition
-fno-partial-inlining -fno-ipa-cp-clone -fno-ipa-sra
-fno-tree-loop-distribute-patterns -fomit-frame-pointer
-falign-functions=1 -falign-jumps=1 -falign-loops=1 -falign-labels=1
-mgeneral-regs-only -mno-red-zone -march=x86-64 -mtune=generic
-frandom-seed=rp11-launch
--param=ggc-min-expand=100 --param=ggc-min-heapsize=131072
-Os -g0 -U_FORTIFY_SOURCE
-Wall -Wextra -Wvla -Werror""".split()
ASSEMBLE_VECTOR = "--64 --noexecstack -mx86-used-note=no".split()
LINK_VECTOR = """-m elf_x86_64 -static -nostdlib --build-id=none -z noexecstack
-z norelro --no-dynamic-linker""".split()


def _commands() -> list[list[str]]:
    joined = BUILD_SH.replace("\\\n", " ")
    lines = [l.split("#", 1)[0].strip() for l in joined.splitlines()]
    return [l.split() for l in lines if l]


def test_tl3_the_flag_vectors_appear_exactly() -> None:
    cmds = {c[0]: c for c in _commands() if c[0].startswith("/usr/bin/")}
    gcc = cmds["/usr/bin/gcc-15"]
    assert gcc[1:1 + len(COMPILE_VECTOR)] == COMPILE_VECTOR
    assert gcc[1 + len(COMPILE_VECTOR):] == ["-o", '../../"$out"/launch.s', "launch.c", "2>", '../../"$out"/cc1.v']
    assemblers = [c for c in _commands() if c[0] == "/usr/bin/as"]
    assert [c[1:4] for c in assemblers] == [ASSEMBLE_VECTOR, ASSEMBLE_VECTOR]
    assert [c[-1] for c in assemblers] == ["start.s", "launch.s"]
    ld = cmds["/usr/bin/ld.bfd"]
    assert ld[1:1 + len(LINK_VECTOR)] == LINK_VECTOR
    assert ld[1 + len(LINK_VECTOR):] == ["-T", "../infra/rp11-launch/rp11-launch.ld", "-Map",
                                         "rp11-launch.map", "-o", "rp11-launch", "start.o", "launch.o"]


def test_tl3_build_sh_uses_only_builtins_and_lock_tools_with_relative_arguments() -> None:
    tools = {re.match(r"tool=(\S+)", l).group(1) for l in LOCK.splitlines() if l.startswith("tool=")}
    builtins = {"set", "umask", "if", "then", "fi", "exit", "cd", "printf", "out=$1"}
    for cmd in _commands():
        head = cmd[0]
        assert head in builtins or head in tools, head
        if head in tools:
            assert all(not a.startswith("/") for a in cmd[1:]), cmd
    assert "$(" not in BUILD_SH and "`" not in BUILD_SH
    assert not re.search(r"[*?]", BUILD_SH.replace("# ", "")), "glob character"
    assert BUILD_SH.count("set -eu") == 1 and "umask 022" in BUILD_SH
    listing_cmds = [c for c in _commands() if c[0] in ("/usr/bin/objdump", "/usr/bin/readelf")]
    assert listing_cmds[1][:4] == ["/usr/bin/objdump", "-d", "-w", "-z"]


def test_tl3_build_sh_refuses_a_precompiled_header_beside_its_inputs() -> None:
    assert "if [ -e launch.c.gch ] || [ -e select.h.gch ]; then" in BUILD_SH


def test_tl3_the_linker_script_asserts_and_discards() -> None:
    assert "ENTRY(_start)" in LINKER
    assert "image PT_LOAD FILEHDR PHDRS FLAGS(5);" in LINKER and "stack PT_GNU_STACK FLAGS(6);" in LINKER
    for sect in (".data", ".bss", ".tdata", ".tbss", ".init_array", ".fini_array", ".preinit_array",
                 ".ctors", ".dtors", ".got", ".got.plt", ".plt", ".rela.dyn", ".interp", ".dynamic"):
        assert f"ASSERT(SIZEOF({sect}) == 0" in LINKER, sect
    assert "/DISCARD/ : { *(.note.*) *(.comment) *(.eh_frame)" in LINKER


def _lock() -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for line in LOCK.splitlines():
        if line and not line.startswith("#"):
            k, _, v = line.partition("=")
            out.setdefault(k, []).append(v)
    return out


def test_tl3_the_lock_parses_and_every_field_is_present() -> None:
    lock = _lock()
    for field in ("format", "target", "distribution", "archive_snapshot", "package", "tool", "build_argv",
                  "build_env", "shell_added_env", "manifest_argv", "build_root_manifest_sha256",
                  "entry_mechanism", "entry_added_env", "driver_added_env", "ic1_controlled_checkouts",
                  "ic1_exec_sequence", "ic1_env_entry", "ic1_env_shell", "ic1_env_source",
                  "ic1_env_compiler", "ic1_env_output"):
        assert field in lock, field
    assert lock["format"] == ["rp11-toolchain-lock/1"]
    assert lock["target"] == ["x86_64-linux-gnu"]
    assert re.fullmatch(r"\d{8}T\d{6}Z", lock["archive_snapshot"][0])
    for p in lock["package"]:
        name, version, sha, path = p.split()
        assert re.fullmatch(r"[0-9a-f]{64}", sha) and path.startswith("pool/main/")
    assert json.loads(lock["build_argv"][0]) == list(C.BUILD_ARGV) == list(ENTER.BUILD_ARGV)
    assert json.loads(lock["build_env"][0]) == list(C.BUILD_ENV)
    assert json.loads(lock["shell_added_env"][0]) == list(C.SHELL_ADDED_ENV)
    assert json.loads(lock["entry_added_env"][0]) == list(C.ENTRY_ADDED_ENV)
    assert json.loads(lock["driver_added_env"][0]) == list(C.DRIVER_ADDED_ENV)
    assert [json.loads(v) for v in lock["manifest_argv"]] == [list(v) for v in ENTER.MANIFEST_ARGV]
    assert lock["build_root_manifest_sha256"] == [_sha(S.LAUNCH / "build-root.manifest")]


def test_tl3_every_lock_tool_digest_is_the_manifest_digest_of_its_resolved_file() -> None:
    entries, links, _ex = IC1.load_manifest(MANIFEST)
    digests = {line.split(" ")[5]: line.split(" ")[6] for line in MANIFEST.splitlines()[1:] if line.startswith("f ")}
    for line in _lock()["tool"]:
        path = line.split(" | ")[0]
        sha = re.search(r"sha256=([0-9a-f]{64})", line).group(1)
        assert digests[IC1.canonical(path, links)] == sha, path


def test_tl3_the_tree_manifest_parses_is_sorted_and_names_its_exclusions() -> None:
    lines = MANIFEST.splitlines()
    assert lines[0] == "rp11-build-root/1"
    excludes = [l for l in lines[1:] if l.startswith("exclude ")]
    assert [e.split()[1] for e in excludes] == ["/proc", "/sys", "/dev", "/run", "/rp11"]
    assert all(len(e.split(" ", 2)) == 3 and e.split(" ", 2)[2].strip() for e in excludes)
    paths = [l.split(" ")[5].encode() for l in lines[1 + len(excludes):]]
    assert paths == sorted(paths) and len(paths) == len(set(paths))
    assert "/etc/ld.so.preload" not in {p.decode() for p in paths}
    for line in lines[1 + len(excludes):]:
        kind = line.split(" ")[0]
        assert kind in ("d", "f", "l"), line
        if kind == "f":
            assert re.fullmatch(r"[0-9a-f]{64}", line.split(" ")[6])
    for d in ("/tmp", "/var/tmp"):
        assert f" 1777 0 0 0 {d} -" in MANIFEST
        assert not any(p.decode().startswith(d + "/") for p in paths)


# ---------------------------------------------------------------------------
# T-L4 — coarse text screen over the committed listing (no decoding claim)
# ---------------------------------------------------------------------------


def test_tl4_start_is_the_entry_and_no_segment_or_legacy_trap_appears() -> None:
    entry = re.search(r"Entry point address:\s+(0x[0-9a-f]+)", LISTING).group(1)
    assert re.search(rf"^0000000000{entry[2:]} <_start>:$", LISTING, re.M)
    dis = LISTING.split("Disassembly of section .text:")[1].split("== objdump -s")[0]
    assert "%fs:" not in dis and "%gs:" not in dis
    assert not re.search(r"\t(int|sysenter|int3)\b", dis)


def test_tl4_every_syscall_is_preceded_in_its_block_by_a_write_to_eax() -> None:
    """Narrowed from §5.12.1's wording: the first build loads %rax by register
    copy at four write sites (`mov %r9,%rax`), so the screen requires a write
    to %eax/%rax in the block; that the value is in the inventory is T-L10's
    constant propagation, not this screen's."""
    dis = LISTING.split("Disassembly of section .text:")[1].split("== objdump -s")[0]
    block: list[str] = []
    for line in dis.splitlines():
        text = line.split("\t")[-1].strip() if "\t" in line else ""
        if not text:
            continue
        if text == "syscall":
            assert any(re.search(r",%(e|r)ax$", t) for t in block), block
            block = []
        elif re.match(r"(j\w+|ud2)\b", text):
            block = []
        else:
            block.append(text)


def test_tl4_rodata_holds_exactly_the_literal_strings() -> None:
    ro = S.listing_parts(LISTING)["rodata"]
    strings = ro.split(b"\0")[:-1]
    want = {C.diagnostic_line(n).encode() for _s, n in C.STATUSES} | {e.encode() for e in C.EXECVE_ARGV} \
        | {e.encode() for e in C.EXECVE_ENV_LITERALS} | {b"/"}
    assert set(strings) == want and len(strings) == len(want)


# ---------------------------------------------------------------------------
# T-L10 — over the committed listing (not evidence without T-L11; XD-7)
# ---------------------------------------------------------------------------


def _tl10(listing: str) -> dict:
    return CTV.verify_listing(listing, C.control_contract())


def test_tl10_passes_and_its_tables_agree_with_the_contract() -> None:
    r = _tl10(LISTING)
    assert r["verdict"] == "pass", r["violations"]
    assert [f[0] for f in r["functions"]] == list(C.FUNCTIONS)
    assert r["call_graph"] == [["_start", "rp11_main", "CT-4"]]
    assert r["max_rp11_main_frame"] == C.EXPECTED_FRAME
    assert r["max_stack_depth"] == C.EXPECTED_STACK_DEPTH <= C.STACK_BOUND
    names = [s.get("name") for s in r["syscalls"]]
    assert set(names) == {n for n, _k in C.SYSCALLS}
    assert all(s["followed_by_ud2"] for s in r["syscalls"] if s.get("name") == "exit_group")
    assert names.count("exit_group") == 10 and names.count("write") == 10
    assert {(l["function"], l["base"]) for l in r["loads"]} == {("_start", "frame"), ("rp11_main", "input-derived")}
    assert all(0 > s["frame_offset"] >= -C.EXPECTED_FRAME for s in r["stores"] if s["function"] == "rp11_main")


def _mutate(old: str, new: str) -> str:
    assert LISTING.count(old) >= 1, old
    return LISTING.replace(old, new, 1)


@pytest.mark.parametrize(
    "old, new, needle",
    [
        ("\tud2\n", "\tret\n", "not on the permitted list"),
        ("\tud2\n", "\tcall   4000cb <rp11_main>\n", "not on the permitted list"),
        ("jmp    4000cb <rp11_main>", "jmp    *%rax", "indirect operand"),
        ("jmp    4000cb <rp11_main>", "jmp    4000d1 <rp11_main+0x6>", "CT-4 jmp does not target"),
        ("mov    %rsi,0x30(%rsp)", "mov    %rsi,0xc8(%rsp)", "outside the frame"),
        ("mov    %rsi,0x30(%rsp)", "mov    %rsi,0x30(%rax)", "store not through a constant %rsp"),
        ("mov    $0x6f,%edi", "mov    $0x70,%edi", "write is not followed by exit_group(111)"),
        ("mov    $0xd,%eax", "mov    $0x9,%eax", "not in the inventory"),
        ("mov    $0x2,%edi\n  400117", "mov    $0x1,%edi\n  400117", "descriptor is not 2"),
        ("sub    $0xc0,%rsp", "sub    %rax,%rsp", "other than by a constant"),
        ("movq   $0x40067f,0x80(%rsp)", "movq   $0x400693,0x80(%rsp)", "argv[0] differs"),
        ("mov    %rcx,0x8(%rsp)", "mov    %rsi,0x8(%rsp)", "new set is not 8 zero bytes"),
        ("cmp    $0x3,%rdi", "cmp    0x8(%rsp),%rdi", "load at or above rp11_main's entry slot"),
    ],
)
def test_tl10_refuses_each_injected_violation(old, new, needle) -> None:
    r = _tl10(_mutate(old, new))
    assert r["verdict"] == "fail"
    assert any(needle in v for v in r["violations"]), r["violations"]


# ---------------------------------------------------------------------------
# T-L12 — XD's self-test corpus (XD-10)
# ---------------------------------------------------------------------------


def _corpus():
    for line in CORPUS.splitlines()[1:]:
        if line.strip() and not line.startswith("#"):
            yield line[0], [f.strip() for f in line[2:].split(" | ")]


POSITIVE = [f for k, f in _corpus() if k == "+"]
NEGATIVE = [f for k, f in _corpus() if k == "-"]
STREAMS = [f for k, f in _corpus() if k == "s"]


def test_tl12_the_corpus_header_and_size() -> None:
    assert CORPUS.splitlines()[0] == "rp11-xdecode-corpus/1"
    assert len(POSITIVE) >= len(XD.TABLE) and NEGATIVE and STREAMS


@pytest.mark.parametrize("row, hexbytes, expected, cite", POSITIVE, ids=[f"{p[0]}:{p[1]}" for p in POSITIVE])
def test_tl12_positive_vector_decodes_to_its_row_and_text(row, hexbytes, expected, cite) -> None:
    raw = bytes.fromhex(hexbytes)
    ins = XD.decode_one(raw, 0, 0x401000)
    assert (ins.row, ins.length, ins.canonical()) == (row, len(raw), expected)
    assert cite.startswith("SDM")


def test_tl12_every_table_row_has_a_positive_vector() -> None:
    assert {p[0] for p in POSITIVE} == {r.id for r in XD.TABLE}


@pytest.mark.parametrize("klass, hexbytes, what, cite", NEGATIVE, ids=[n[2] for n in NEGATIVE])
def test_tl12_negative_vector_fails_with_its_class(klass, hexbytes, what, cite) -> None:
    with pytest.raises(XD.DecodeError) as exc:
        XD.decode_one(bytes.fromhex(hexbytes), 0, 0x401000)
    assert exc.value.klass[0] == klass


def test_tl12_every_forbidden_form_named_by_xd_10_is_a_negative_vector() -> None:
    named = ["c3", "c2 10 00", "f3 c3", "f2 c3", "cb", "ca 10 00", "cf", "e8 00 00 00 00", "ff d0", "ff 18",
             "ff e0", "ff 28", "cc", "cd 80", "f1", "0f 34", "c8 10 00 00", "c9", "e2 fe", "e3 fe",
             "c7 f8 00 00 00 00", "f3 0f 1e fa", "64 48 8b 04 25 28 00 00 00", "65 48 8b 04 25 28 00 00 00",
             "f0 ff 00", "f3 a4", "c5 f8 77"]
    have = {n[1] for n in NEGATIVE}
    assert set(named) <= have


@pytest.mark.parametrize("klass, start, main, what", STREAMS, ids=[s[3] for s in STREAMS])
def test_tl12_stream_vector_reports_its_class(klass, start, main, what) -> None:
    s, m = bytes.fromhex(start), bytes.fromhex(main)
    fns = (XD.Function("_start", 0x401000, len(s)), XD.Function("rp11_main", 0x401000 + len(s), len(m)))
    r = XD.decode_text(s + m, 0x401000, fns, 0x401000, (("the .rodata section", 0x402000, 0x402040),))
    classes = {f.klass[0] for f in r.failures}
    assert (not classes) if klass == "pass" else klass in classes


def test_tl12_every_xd_5_class_is_exercised() -> None:
    covered = {n[0] for n in NEGATIVE} | {s[0] for s in STREAMS}
    assert {"b", "c", "d", "e", "f"} <= covered   # (a) and (g) below


def test_tl12_an_ambiguous_table_fails_to_load() -> None:
    dup = XD.TABLE + (XD.Row("dup-xor", "xor", (0x31,), "v", (32,), modrm=True, operands=("E", "G")),)
    with pytest.raises(XD.AmbiguousTable):
        XD.check_unambiguous(dup)
    overlap = XD.TABLE + (XD.Row("shadow", "nop", (0x90,), "none"),)
    with pytest.raises(XD.AmbiguousTable):
        XD.check_unambiguous(overlap)


def test_tl12_a_runtime_double_match_is_class_a() -> None:
    twin = XD.Row("twin", "nop", (0x90,), "none")
    with pytest.raises(XD.DecodeError) as exc:
        XD.decode_one(b"\x90", 0, 0x401000, table=XD.TABLE + (twin,))
    assert exc.value.klass == XD.AMBIGUOUS


def test_tl12_the_spelling_table_is_injective_and_complete() -> None:
    XD.Spelling.load(SPELLING)
    with pytest.raises(XD.SpellingError):
        XD.Spelling.load(SPELLING.replace("reg ebx %ebx", "reg ebx %eax"))
    with pytest.raises(XD.SpellingError):
        XD.Spelling.load(SPELLING.replace("mnem cmovl cmovl ambiguous", "mnem cmovl cmovle ambiguous"))
    with pytest.raises(XD.SpellingError):
        XD.Spelling.load(SPELLING.replace("reg r15b %r15b\n", ""))
    with pytest.raises(XD.SpellingError):
        XD.Spelling.load(SPELLING.replace("form mov-Z-Iv/64 movabs", "form mov-Z-Iv/64 mov"))


def test_xd_documents_its_provenance_and_limits() -> None:
    doc = XD.__doc__
    assert "325383-093US" in doc and "24594" in doc
    assert "before the first build" in doc and "without reading" in doc
    assert "AD-14" in doc


# ---------------------------------------------------------------------------
# XD agreement (XD-6, class g), over an image rebuilt from the listing.
# That image is NOT the built image; T-L11 proper is a toolchain test.
# ---------------------------------------------------------------------------

REBUILT = S.image_from_listing(LISTING)


def _xd(listing: str) -> dict:
    return XD.run(REBUILT, listing.encode(), SPELLING.encode())


def test_xd_agrees_with_the_committed_listing_over_its_own_bytes() -> None:
    v = _xd(LISTING)
    assert v["verdict"] == "pass", v["failures"]
    assert v["stream_sha256"] == C.AGREED_STREAM_SHA256
    assert v["instructions"] == 332


@pytest.mark.parametrize(
    "old, new",
    [
        ("xor    %ebp,%ebp", "xor    %ebx,%ebp"),
        ("jne    40010d <rp11_main+0x42>", "jne    40010e <rp11_main+0x43>"),
        ("movabs $0x495441434f564e49,%rax", "mov    $0x495441434f564e49,%rax"),
        ("cmpb   $0x2d,(%rax)", "cmp    $0x2d,(%rax)"),
        ("lea    0x8(%rsp),%rsi", "lea    0x10(%rsp),%rsi"),
    ],
)
def test_xd_reports_any_listing_disagreement_as_class_g(old, new) -> None:
    v = _xd(_mutate(old, new))
    assert v["verdict"] == "fail"
    assert {f["class"] for f in v["failures"]} == {XD.DISAGREEMENT}


def test_xd_reports_a_byte_or_boundary_disagreement() -> None:
    v = _xd(_mutate("  4000b0:\t31 ed                \t", "  4000b0:\t31 ec                \t"))
    assert any(f["class"] == XD.DISAGREEMENT and "bytes" in f["detail"] for f in v["failures"])


def test_xd_reads_the_image_not_the_listing() -> None:
    tampered = bytearray(REBUILT)
    off = REBUILT.index(bytes.fromhex("31ed488b3c24"))
    tampered[off:off + 2] = b"\xc3\x90"          # a ret at _start
    v = XD.run(bytes(tampered), LISTING.encode(), SPELLING.encode())
    assert v["verdict"] == "fail"
    assert v["failures"][0]["class"] == XD.UNSUPPORTED


def test_xd_refuses_an_extra_symbol_or_wrong_function_set() -> None:
    swapped = REBUILT.replace(b"rp11_main\0", b"rp11_maio\0")
    assert swapped != REBUILT
    v = XD.run(swapped, None, SPELLING.encode())
    assert v["verdict"] == "fail"


# ---------------------------------------------------------------------------
# T-L7's checks over the rebuilt image's structure (the real image: toolchain)
# ---------------------------------------------------------------------------


def test_tl7_listing_bytes_are_the_rebuilt_text() -> None:
    assert ELF.check_listing_bytes(REBUILT, LISTING) == []
    assert ELF.check_listing_bytes(REBUILT, _mutate("\t0f 0b                \t", "\t0f 0b 90             \t"))


def test_tl7_map_check() -> None:
    good = "LOAD start.o\nLOAD launch.o\nOUTPUT(rp11-launch elf64-x86-64)\n"
    assert ELF.check_map(good) == []
    assert ELF.check_map("LOAD launch.o\nLOAD start.o\n")
    assert ELF.check_map(good + "LOAD /usr/lib/x86_64-linux-gnu/libc.a\n")


# ---------------------------------------------------------------------------
# IC-1's checker, over synthetic traces
# ---------------------------------------------------------------------------

# The traces are written the way the pinned strace writes R-2's (`-f -v -y`):
# the shell `vfork`s, the child's `execve` is unfinished until the parent's
# `vfork` returns, and `chdir` takes the absolute directory. The environments
# come from the contract module; `test_ic1_the_exact_environments_are_these`
# pins them by hand, independently of it.

R2_CO, R4A_CO = C.IC1_CONTROLLED_CHECKOUTS
CHECKOUTS = {"r2": R2_CO, "r4a": R4A_CO}
CC1 = "/usr/libexec/gcc/x86_64-linux-gnu/15/cc1"
#: Where each successful execve happens: (pid, parent, forking call).
_PROCESSES = ((4, None, None), (4, None, None), (5, 4, "vfork"), (6, 5, "clone3"), (7, 4, "vfork"),
              (8, 4, "vfork"), (9, 4, "vfork"), (10, 4, "vfork"), (11, 4, "vfork"), (12, 4, "vfork"))


def _q(s: str) -> str:
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def _arr(items) -> str:
    return "[" + ", ".join(_q(i) for i in items) + "]"


def _env(index: int, co: str) -> list[str]:
    env = list(C.ic1_environment(C.IC1_EXEC_SEQUENCE[index][1], co))
    return env[::-1] if index % 2 else env  # the comparison is of mappings, not orders


def _fixture_cc1_argv() -> list[str]:
    """`cc1`'s argument vector as the driver printed it into the committed
    `cc1.v` fixture (its `-v` echo of the command it runs)."""
    text = (S.VERIFY / "fixtures" / "cc1.v.baseline").read_text()
    line = next(l for l in text.splitlines() if l.startswith(f" {CC1} "))
    return line.split()


#: The argument vectors of the driver (index 2) and `cc1` (index 3) in a
#: conforming trace; every other execve carries only its path.
_ARGVS = {2: S.build_driver_vector(), 3: _fixture_cc1_argv()}


def _trace(co: str = R2_CO, envs: dict | None = None, raw: dict | None = None,
           argvs: dict | None = None) -> str:
    """A conforming traced R-2 at `co`. `envs` replaces the environment of an
    execve by its index; `raw` replaces the text of its environment array;
    `argvs` replaces its argument vector."""
    envs, raw, argvs = envs or {}, raw or {}, {**_ARGVS, **(argvs or {})}
    src, out = f"{co}/infra/rp11-launch", f"{co}/build-out"
    lines: list[str] = []
    for i, (path, _cls) in enumerate(C.IC1_EXEC_SEQUENCE):
        pid, parent, fork = _PROCESSES[i]
        env_text = raw.get(i, _arr(envs.get(i, _env(i, co))))
        record = f"execve({_q(path)}, {_arr(argvs.get(i, [path]))}, {env_text}"
        if i == 2:
            lines.append(f'4     chdir("{src}") = 0')
            lines.append(f'4     newfstatat(AT_FDCWD<{src}>, "launch.c.gch", 0x7ffd, 0) = -1 ENOENT (No such file or directory)')
        if i == 5:
            lines.append(f'4     chdir("{out}") = 0')
        if parent is None:
            lines.append(f"{pid}     {record}) = 0")
        else:
            opening = "vfork(" if fork == "vfork" else "clone3({flags=CLONE_VM|CLONE_VFORK, exit_signal=SIGCHLD}, 88"
            lines.append(f"{parent}     {opening} <unfinished ...>")
            lines.append(f"{pid}     {record} <unfinished ...>")
            lines.append(f"{parent}     <... {fork} resumed>) = {pid}")
            lines.append(f"{pid}     <... execve resumed>) = 0")
        if i == 0:
            lines.append(f'4     openat(AT_FDCWD<{co}>, "/etc/ld.so.cache", O_RDONLY|O_CLOEXEC) = 3</etc/ld.so.cache>')
        if i == 1:
            lines.append(f'4     openat(AT_FDCWD<{co}>, "infra/rp11-launch/build.sh", O_RDONLY) = 3')
        if i == 2:
            lines.append('5     access("/usr/lib/gcc/x86_64-linux-gnu/15/specs", R_OK) = -1 ENOENT (No such file or directory)')
            lines.append('5     readlink("/proc/self/exe", "/usr/bin/x86_64-linux-gnu-gcc-15", 4095) = 32')
    return "\n".join(lines)


GOOD_TRACE = _trace()


def _ic1(trace: str, co: str = R2_CO) -> dict:
    return IC1.check(trace, MANIFEST, co)


def _fails_with(result: dict, *needles: str) -> None:
    assert result["verdict"] == "fail"
    for needle in needles:
        assert any(needle in f for f in result["failures"]), (needle, result["failures"])


def _without(env: list[str], name: str) -> list[str]:
    return [e for e in env if e.partition("=")[0] != name]


def _with(env: list[str], name: str, value: str) -> list[str]:
    return [f"{name}={value}" if e.partition("=")[0] == name else e for e in env]


@pytest.mark.parametrize("run", sorted(CHECKOUTS))
def test_ic1_checker_passes_a_conforming_trace(run) -> None:
    co = CHECKOUTS[run]
    r = _ic1(_trace(co), co)
    assert r["verdict"] == "pass", r["failures"]
    assert r["exec_sequence"] == [p for p, _c in C.IC1_EXEC_SEQUENCE]
    assert [e["class"] for e in r["environments"]] == [c for _p, c in C.IC1_EXEC_SEQUENCE]
    assert r["proc_sys_paths"] == ["/proc/self/exe"]
    assert r["pch_probes"] == [f"{co}/infra/rp11-launch/launch.c.gch"]


def test_ic1_the_exact_environments_are_these() -> None:
    """Written out by hand, for both controlled checkouts, so that the contract
    module, the lock and the checker are each compared with a fixed text."""
    base = {"LC_ALL": "C", "PATH": "/usr/bin", "SOURCE_DATE_EPOCH": "0", "TZ": "UTC0"}
    driver = {
        "COLLECT_GCC": "/usr/bin/gcc-15",
        "COLLECT_GCC_OPTIONS": S.collect_gcc_options(S.build_driver_vector()),
        "OFFLOAD_TARGET_DEFAULT": "1",
        "OFFLOAD_TARGET_NAMES": "nvptx-none:amdgcn-amdhsa",
    }
    for co in ("/rp11/co", "/rp11/alt/checkout"):
        src = {"OLDPWD": co, "PWD": co + "/infra/rp11-launch"}
        want = {
            "entry": {**base, "PWD": co},
            "shell": dict(base),
            "source": {**base, **src},
            "compiler": {**base, **src, **driver},
            "output": {**base, "OLDPWD": co + "/infra/rp11-launch", "PWD": co + "/build-out"},
        }
        for cls, env in want.items():
            assert dict(e.split("=", 1) for e in C.ic1_environment(cls, co)) == env, (co, cls)
            assert IC1.expected_environment(cls, co) == env, (co, cls)
    assert [c for _p, c in C.IC1_EXEC_SEQUENCE] == [
        "entry", "shell", "source", "compiler", "source", "output", "output", "output", "output", "output"]


def test_ic1_the_driver_values_are_derived_from_build_sh_not_observed() -> None:
    vector = S.build_driver_vector()
    assert vector[0] == "/usr/bin/gcc-15" and vector[-1] == "launch.c"
    pinned = dict(e.split("=", 1) for e in C.DRIVER_ADDED_ENV_VALUES)
    assert pinned["COLLECT_GCC"] == vector[0]
    assert pinned["COLLECT_GCC_OPTIONS"] == S.collect_gcc_options(vector) == IC1.COLLECT_GCC_OPTIONS
    assert dict(IC1.DRIVER_ADDED_VALUES) == pinned
    assert sorted(pinned) == sorted(C.DRIVER_ADDED_ENV) == sorted(IC1.DRIVER_ADDED)
    # the derivation's own rules, on vectors whose result is known
    assert S.collect_gcc_options(["gcc", "-fno-pic", "-fno-pie", "-o", "d/x.s", "a.c"]) == \
        "'-fno-pie' '-o' 'd/x.s' '-dumpdir' 'd/'"
    assert S.collect_gcc_options(["gcc", "-fno-pie", "-Ufoo", "-D'q", "-o", "../o/x.s", "a.c"]) == \
        "'-fno-pie' '-U' 'foo' '-D'\\''q' '-o' '../o/x.s' '-dumpdir' '../o/'"


def _env_cases():
    for run, co in sorted(CHECKOUTS.items()):
        for i, (path, cls) in enumerate(C.IC1_EXEC_SEQUENCE):
            for entry in C.ic1_environment(cls, co):
                name = entry.partition("=")[0]
                yield pytest.param(co, i, name, id=f"{run}-{i + 1}-{path.rsplit('/', 1)[1]}-{name}")


@pytest.mark.parametrize("co, index, name", list(_env_cases()))
def test_ic1_refuses_each_required_variable_missing(co, index, name) -> None:
    path = C.IC1_EXEC_SEQUENCE[index][0]
    r = _ic1(_trace(co, envs={index: _without(_env(index, co), name)}), co)
    _fails_with(r, f"{path}: required environment variable {name} is missing")


@pytest.mark.parametrize("co, index, name", list(_env_cases()))
def test_ic1_refuses_each_required_variable_changed(co, index, name) -> None:
    path = C.IC1_EXEC_SEQUENCE[index][0]
    value = dict(e.split("=", 1) for e in _env(index, co))[name]
    r = _ic1(_trace(co, envs={index: _with(_env(index, co), name, value + "x")}), co)
    _fails_with(r, f"{path}: {name} is {value + 'x'!r}, not {value!r}")


@pytest.mark.parametrize("run", sorted(CHECKOUTS))
@pytest.mark.parametrize("index", range(len(C.IC1_EXEC_SEQUENCE)))
def test_ic1_refuses_an_extra_variable(run, index) -> None:
    co = CHECKOUTS[run]
    path = C.IC1_EXEC_SEQUENCE[index][0]
    r = _ic1(_trace(co, envs={index: _env(index, co) + ["LD_PRELOAD=x"]}), co)
    _fails_with(r, f"{path}: unexpected environment variable LD_PRELOAD")


@pytest.mark.parametrize("index", [i for i, (_p, c) in enumerate(C.IC1_EXEC_SEQUENCE) if c != "compiler"])
def test_ic1_refuses_driver_variables_outside_cc1(index) -> None:
    path = C.IC1_EXEC_SEQUENCE[index][0]
    env = _env(index, R2_CO) + [e for e in C.DRIVER_ADDED_ENV_VALUES if e.startswith("COLLECT_GCC=")]
    _fails_with(_ic1(_trace(envs={index: env})), f"{path}: unexpected environment variable COLLECT_GCC")


@pytest.mark.parametrize("run", sorted(CHECKOUTS))
@pytest.mark.parametrize("index", [0, 3, 9])
@pytest.mark.parametrize("second", ["same", "different"])
def test_ic1_refuses_a_duplicated_variable(run, index, second) -> None:
    co = CHECKOUTS[run]
    env = _env(index, co)
    name, _, value = env[0].partition("=")
    extra = env[0] if second == "same" else f"{name}={value}x"
    r = _ic1(_trace(co, envs={index: env + [extra]}), co)
    _fails_with(r, f"duplicated environment variable {name}")


@pytest.mark.parametrize("entry", ["NOEQUALS", "=value", "1BAD=x", "", "A B=c"])
@pytest.mark.parametrize("index", [0, 1, 3, 6])
def test_ic1_refuses_a_malformed_variable(entry, index) -> None:
    r = _ic1(_trace(envs={index: _env(index, R2_CO) + [entry]}))
    _fails_with(r, f"malformed environment entry {entry!r}")


@pytest.mark.parametrize(
    "env_text, needle",
    [
        ('["LC_ALL=C", "PATH=/usr/bin"...]', "truncated string"),
        ('["LC_ALL=C", "PATH=/usr/bin", ...]', "malformed execve record"),
        ('[/* 6 vars */]', "malformed execve record"),
        ('["LC_ALL=C" "PATH=/usr/bin"]', "malformed array"),
        ('["LC_ALL=C", "PATH=/usr/b\\qin"]', "unknown escape"),
        ('["LC_ALL=C", "PATH=/usr/bin', "malformed execve record"),
        ('0x7ffd /* 6 vars */', "malformed execve record"),
    ],
)
def test_ic1_refuses_a_malformed_or_abbreviated_execve_record(env_text, needle) -> None:
    _fails_with(_ic1(_trace(raw={2: env_text})), needle)


def test_ic1_decodes_strace_escapes_before_comparing() -> None:
    path, argv, env = IC1.parse_execve(r'"/usr/bin/as", ["a\"b", "c\\d", "\101\x42\n"], []')
    assert (path, argv, env) == ("/usr/bin/as", ['a"b', "c\\d", "AB\n"], [])
    # an escaped spelling of a required value is the value, and still passes
    env = [e.replace("LC_ALL=C", "LC_ALL=\\103") for e in _env(6, R2_CO)]
    raw = "[" + ", ".join('"' + e + '"' for e in env) + "]"
    assert _ic1(_trace(raw={6: raw}))["verdict"] == "pass"


@pytest.mark.parametrize("run", sorted(CHECKOUTS))
@pytest.mark.parametrize("index", [0, 2, 3, 4, 5, 6, 9])
def test_ic1_refuses_wrong_pwd_and_oldpwd_at_each_checkout(run, index) -> None:
    """R-2 and R-4(a): the other run's directories, and the pair exchanged."""
    co = CHECKOUTS[run]
    other = R4A_CO if co == R2_CO else R2_CO
    path = C.IC1_EXEC_SEQUENCE[index][0]
    env = _env(index, co)
    want = dict(e.split("=", 1) for e in env)
    foreign = [e.replace(co, other) if e.startswith(("PWD=", "OLDPWD=")) else e for e in env]
    _fails_with(_ic1(_trace(co, envs={index: foreign}), co), f"{path}: PWD is {want['PWD'].replace(co, other)!r}")
    if "OLDPWD" in want:
        _fails_with(_ic1(_trace(co, envs={index: foreign}), co), f"{path}: OLDPWD is ")
        swapped = _with(_with(env, "PWD", want["OLDPWD"]), "OLDPWD", want["PWD"])
        _fails_with(_ic1(_trace(co, envs={index: swapped}), co),
                    f"{path}: PWD is {want['OLDPWD']!r}, not {want['PWD']!r}",
                    f"{path}: OLDPWD is {want['PWD']!r}, not {want['OLDPWD']!r}")


@pytest.mark.parametrize("run", sorted(CHECKOUTS))
def test_ic1_a_run_is_checked_against_its_own_checkout(run) -> None:
    co = CHECKOUTS[run]
    other = R4A_CO if co == R2_CO else R2_CO
    _fails_with(_ic1(_trace(co), other), "PWD is ", "OLDPWD is ")


@pytest.mark.parametrize(
    "name, value",
    [
        ("COLLECT_GCC", "gcc-15"),
        ("COLLECT_GCC", "/usr/bin/x86_64-linux-gnu-gcc-15"),
        ("COLLECT_GCC_OPTIONS", IC1.COLLECT_GCC_OPTIONS + " '-O2'"),
        ("COLLECT_GCC_OPTIONS", IC1.COLLECT_GCC_OPTIONS.replace("'-fno-pie'", "'-fno-pic' '-fno-pie'")),
        ("COLLECT_GCC_OPTIONS", ""),
        ("OFFLOAD_TARGET_NAMES", "nvptx-none"),
        ("OFFLOAD_TARGET_NAMES", "amdgcn-amdhsa:nvptx-none"),
        ("OFFLOAD_TARGET_DEFAULT", "0"),
        ("OFFLOAD_TARGET_DEFAULT", ""),
    ],
)
@pytest.mark.parametrize("run", sorted(CHECKOUTS))
def test_ic1_refuses_each_driver_variable_changed(run, name, value) -> None:
    co = CHECKOUTS[run]
    r = _ic1(_trace(co, envs={3: _with(_env(3, co), name, value)}), co)
    _fails_with(r, f"{CC1}: {name} is {value!r}, not ")


@pytest.mark.parametrize("name", sorted(C.DRIVER_ADDED_ENV))
@pytest.mark.parametrize("run", sorted(CHECKOUTS))
def test_ic1_refuses_each_driver_variable_missing(run, name) -> None:
    co = CHECKOUTS[run]
    r = _ic1(_trace(co, envs={3: _without(_env(3, co), name)}), co)
    _fails_with(r, f"{CC1}: required environment variable {name} is missing")


def test_ic1_refuses_a_different_execve_sequence() -> None:
    lines = GOOD_TRACE.splitlines()
    extra = f'4     execve("/usr/bin/objdump", ["/usr/bin/objdump"], {_arr(_env(9, R2_CO))}) = 0'
    _fails_with(_ic1(GOOD_TRACE + "\n" + extra), "execve #11 is /usr/bin/objdump; the build defines no further execve",
                "made 11 successful execve calls; the build defines 10")
    missing = "\n".join(l for l in lines if "readelf" not in l)
    _fails_with(_ic1(missing), "never executed", "made 9 successful execve calls")
    swapped = GOOD_TRACE.replace("/usr/bin/readelf", "@").replace('execve("/usr/bin/objdump", ["/usr/bin/objdump"], ', "%", 1)
    swapped = swapped.replace("@", "/usr/bin/objdump").replace("%", 'execve("/usr/bin/readelf", ["/usr/bin/readelf"], ')
    _fails_with(_ic1(swapped), "execve #8 is /usr/bin/objdump; the build defines /usr/bin/readelf")


def test_ic1_refuses_an_uncontrolled_checkout() -> None:
    _fails_with(_ic1(_trace(), "/home/x/co"), "'/home/x/co' is not a controlled checkout mount point")
    with pytest.raises(ValueError):
        IC1.expected_environment("entry", "/home/x/co")
    with pytest.raises(ValueError):
        C.ic1_environment("entry", "/rp11/co/")


@pytest.mark.parametrize(
    "extra, needle",
    [
        (f'9     execve("/usr/bin/make", ["/usr/bin/make"], {_arr(C.BUILD_ENV)}) = 0', "not a lock tool"),
        ('4     openat(AT_FDCWD</rp11/co>, "/opt/x/libfoo.so", O_RDONLY) = 3', "not in the manifest"),
        ('4     openat(AT_FDCWD</rp11/co>, "/run/foo", O_RDONLY) = -1 ENOENT (No such file)', "excluded /run"),
        ('4     openat(AT_FDCWD</rp11/co>, "infra/rp11-launch/README", O_RDONLY) = 3', "not an input"),
        ('4     openat(AT_FDCWD</rp11/co>, "/tmp/cc123.s", O_WRONLY|O_CREAT, 0600) = -1 EROFS', "temporary"),
    ],
)
def test_ic1_checker_refuses(extra, needle) -> None:
    _fails_with(_ic1(GOOD_TRACE + "\n" + extra), needle)


def test_ic1_checker_requires_every_tool_to_have_run() -> None:
    r = _ic1("\n".join(l for l in GOOD_TRACE.splitlines() if "readelf" not in l))
    assert any("never executed" in f for f in r["failures"])


def test_ic1_the_checker_contract_and_lock_agree() -> None:
    lock = _lock()
    assert json.loads(lock["ic1_controlled_checkouts"][0]) == list(C.IC1_CONTROLLED_CHECKOUTS) \
        == list(IC1.CONTROLLED_CHECKOUTS)
    assert sorted(C.IC1_CONTROLLED_CHECKOUTS) == sorted({m for m, _u, _h in ENTER.VARIANTS.values()})
    assert json.loads(lock["ic1_exec_sequence"][0]) == [list(s) for s in C.IC1_EXEC_SEQUENCE] \
        == [list(s) for s in IC1.EXEC_SEQUENCE]
    for cls, entries in C.IC1_ENV_CLASSES:
        assert json.loads(lock[f"ic1_env_{cls}"][0]) == list(entries), cls
        assert [f"{k}={v}" for k, v in dict(IC1.ENV_CLASSES)[cls]] == list(entries), cls
    assert {k for k in lock if k.startswith("ic1_env_")} == {f"ic1_env_{c}" for c, _e in C.IC1_ENV_CLASSES}
    assert [f"{k}={v}" for k, v in IC1.BUILD_ENV] == list(C.BUILD_ENV)
    assert sorted(IC1.SHELL_ADDED) == sorted(C.SHELL_ADDED_ENV)
    assert tuple(IC1.ENTRY_ADDED) == C.ENTRY_ADDED_ENV
    # the named additions are exactly what the classes add to build_env
    names = {cls: {e.partition("=")[0] for e in entries} - {e.partition("=")[0] for e in C.BUILD_ENV}
             for cls, entries in C.IC1_ENV_CLASSES}
    assert names == {"entry": set(C.ENTRY_ADDED_ENV), "shell": set(), "source": set(C.SHELL_ADDED_ENV),
                     "compiler": set(C.SHELL_ADDED_ENV) | set(C.DRIVER_ADDED_ENV),
                     "output": set(C.SHELL_ADDED_ENV)}
    section = C.manifest_section()["build"]["ic1_environment"]
    assert section["comparison"] == "exact"
    assert section["classes"] == {c: list(e) for c, e in C.IC1_ENV_CLASSES}
    assert section["exec_sequence"] == [{"path": p, "class": c} for p, c in C.IC1_EXEC_SEQUENCE]
    assert {p for p, _c in C.IC1_EXEC_SEQUENCE} == set(IC1.EXECUTABLES)


# ---------------------------------------------------------------------------
# consistency of the committed launcher files and the contract module
# ---------------------------------------------------------------------------


def test_expected_sha256_equals_the_contract_and_the_committed_listing() -> None:
    lines = dict(reversed(l.split("  ")) for l in (S.LAUNCH / "expected.sha256").read_text().splitlines())
    assert lines == {
        "rp11-launch": C.EXPECTED_IMAGE_SHA256,
        "rp11-launch.x86_64.listing": C.EXPECTED_LISTING_SHA256,
        "rp11-launch.map": C.EXPECTED_MAP_SHA256,
        "launch.s": C.EXPECTED_LAUNCH_S_SHA256,
    }
    assert _sha(S.LISTING) == C.EXPECTED_LISTING_SHA256


def test_the_contract_pins_the_lock_manifest_and_xd_digests() -> None:
    assert _sha(S.LAUNCH / "toolchain.lock") == C.TOOLCHAIN_LOCK_SHA256
    assert _sha(S.LAUNCH / "build-root.manifest") == C.BUILD_ROOT_MANIFEST_SHA256
    assert _sha(S.VERIFY / "xdecode.py") == C.XD_SOURCE_SHA256
    assert _sha(S.VERIFY / "xdecode-spelling.table") == C.XD_SPELLING_TABLE_SHA256


def test_the_manifest_section_states_unwired_and_uninstalled() -> None:
    section = C.manifest_section()
    json.dumps(section, sort_keys=True)
    assert section["installed"] is False and section["wired"] is False
    assert section["control"]["permitted_mnemonics"] == list(C.PERMITTED_MNEMONICS)
    assert not {"call", "ret", "callq", "retq"} & set(C.PERMITTED_MNEMONICS)
    assert C.SIGNALS_RESET == tuple(s for s in range(1, 65) if s not in (9, 19))


def test_the_contract_and_the_design_agree_on_line_lengths() -> None:
    """§5.9's length table, transcribed."""
    lengths = {"launch-usage": 28, "launch-invocation-id": 36, "launch-stdio": 28, "launch-descriptors": 34,
               "launch-signals": 30, "launch-chdir": 28, "launch-exec-failed": 34}
    assert {n: len(C.diagnostic_line(n)) for _s, n in C.STATUSES} == lengths


def test_the_contract_pins_the_cc1_v_baseline_fixture() -> None:
    """The cc1.v baseline fixture is pinned by path, length and sha256 in rp11_launch,
    and distinct from the four normative launcher outputs in expected.sha256 (prompt §3 items 8-9).
    """
    baseline_path = S.LAUNCH / "verify" / "fixtures" / "cc1.v.baseline"
    assert baseline_path.exists()
    baseline_bytes = baseline_path.read_bytes()
    assert len(baseline_bytes) == C.CC1_V_BASELINE_LENGTH == 5305
    assert _sha(baseline_path) == C.CC1_V_BASELINE_SHA256 == (
        "e99cee65a228339e304d4e578643de409961539a8240230d4e41bb1baf6bb13a"
    )

    # Preserve distinction: expected.sha256 contains ONLY the four normative outputs
    expected_lines = (S.LAUNCH / "expected.sha256").read_text().splitlines()
    assert len(expected_lines) == 4
    assert not any("cc1.v.baseline" in line for line in expected_lines)

    # Manifest section includes cc1_v_baseline contract
    section = C.manifest_section(baseline_bytes)
    assert section["cc1_v_baseline"] == {
        "byte_length": 5305,
        "path": C.CC1_V_BASELINE_PATH,
        "sha256": C.CC1_V_BASELINE_SHA256,
    }


def test_verify_cc1_v_baseline_mutations_and_mismatches() -> None:
    """verify_cc1_v_baseline rejects 1-byte mutation, append, truncation, and wrong expectations."""
    baseline_path = S.LAUNCH / "verify" / "fixtures" / "cc1.v.baseline"
    baseline_bytes = baseline_path.read_bytes()

    # Valid bytes pass
    verified = C.verify_cc1_v_baseline(baseline_bytes)
    assert verified["byte_length"] == 5305
    assert verified["sha256"] == C.CC1_V_BASELINE_SHA256

    # 1-byte mutation
    mutated = bytes([baseline_bytes[0] ^ 0x01]) + baseline_bytes[1:]
    with pytest.raises(Exception, match="sha256.*does not match expected sha256"):
        C.verify_cc1_v_baseline(mutated)

    # Appended byte
    with pytest.raises(Exception, match="length 5306 does not match expected length 5305"):
        C.verify_cc1_v_baseline(baseline_bytes + b"\x00")

    # Truncated
    with pytest.raises(Exception, match="length 5304 does not match expected length 5305"):
        C.verify_cc1_v_baseline(baseline_bytes[:-1])

    # Wrong expected length
    with pytest.raises(Exception, match="length 5305 does not match expected length 5304"):
        C.verify_cc1_v_baseline(baseline_bytes, expected_length=5304)

    # Wrong expected sha256
    with pytest.raises(Exception, match="does not match expected sha256"):
        C.verify_cc1_v_baseline(baseline_bytes, expected_sha256="f" * 64)


# ---------------------------------------------------------------------------
# FRESH-R4-HS-1 — GCC's garbage-collector parameters are fixed compiler inputs
# (C-P5.0-R5-RP11-FRESH-R5-R4-D1)
# ---------------------------------------------------------------------------

FIXED_TOKENS = tuple(f"--param={name}={value}" for name, value in C.COMPILER_FIXED_PARAMS)
#: The `-v` line in which `cc1` reports the values it uses.
GGC_LINE = "GGC heuristics: " + " ".join(f"--param {n}={v}" for n, v in C.COMPILER_FIXED_PARAMS)
#: The accepted B1 fixture (C-P5.0-R5-RP11-I1-R3-R4-R5-B1), compiled without the
#: two arguments on a host whose resources selected the same two values.
B1_FIXTURE = (5120, "b77f92dcdcf899c5459fec606f16dc325ed5329516cbab5faea86b479992905b")


def _fixed_param_failures(argv: list[str]) -> list[str]:
    failures: list[str] = []
    IC1._check_fixed_params("t", argv[0], argv, failures)
    return failures


def test_the_fixed_params_are_one_contract_in_every_place() -> None:
    assert C.COMPILER_FIXED_PARAMS == (("ggc-min-expand", 100), ("ggc-min-heapsize", 131072))
    assert IC1.FIXED_PARAMS == tuple((n, str(v)) for n, v in C.COMPILER_FIXED_PARAMS)
    assert IC1.FIXED_PARAM_EXECUTABLES == ("/usr/bin/gcc-15", CC1)
    assert C.manifest_section()["build"]["compiler_fixed_params"] == [
        {"name": "ggc-min-expand", "value": 100}, {"name": "ggc-min-heapsize", "value": 131072}]
    options = dict(e.split("=", 1) for e in C.DRIVER_ADDED_ENV_VALUES)["COLLECT_GCC_OPTIONS"]
    lock_compiler = json.loads(_lock()["ic1_env_compiler"][0])
    for token in FIXED_TOKENS:
        assert options.count(f"'{token}'") == 1 and IC1.COLLECT_GCC_OPTIONS.count(f"'{token}'") == 1
        assert sum(e.count(f"'{token}'") for e in lock_compiler) == 1
    assert "ggc" not in options.replace(FIXED_TOKENS[0], "").replace(FIXED_TOKENS[1], "")


def test_build_sh_supplies_each_fixed_param_exactly_once() -> None:
    vector = S.build_driver_vector()
    assert _fixed_param_failures(vector) == []
    assert [w for w in vector if "param" in w or "ggc" in w] == list(FIXED_TOKENS)
    assert not any(w.startswith("@") or w.startswith("-specs") for w in vector)
    # the caller's one argument reaches the vector only inside the -o path
    gcc_line = next(l for l in BUILD_SH.replace("\\\n", " ").splitlines()
                    if l.strip().startswith("/usr/bin/gcc-15"))
    assert gcc_line.count("$") == 2 and gcc_line.count('"$out"') == 2
    assert gcc_line.index("2>") > gcc_line.index("launch.c")


_PARAM_MUTATIONS = {
    "absent": lambda v: [w for w in v if w != FIXED_TOKENS[0]],
    "both absent": lambda v: [w for w in v if w not in FIXED_TOKENS],
    "duplicated": lambda v: v + [FIXED_TOKENS[1]],
    "changed value": lambda v: [w.replace("=100", "=94") for w in v],
    "changed heapsize": lambda v: [w.replace("=131072", "=2169") for w in v],
    "later joined override": lambda v: v + ["--param=ggc-min-expand=94"],
    "later separate override": lambda v: v + ["--param", "ggc-min-heapsize=2169"],
    "earlier separate override": lambda v: v[:1] + ["--param", "ggc-min-expand=94"] + v[1:],
    "response file": lambda v: v + ["@params.rsp"],
}


@pytest.mark.parametrize("mutation", sorted(_PARAM_MUTATIONS))
@pytest.mark.parametrize("vector", ["driver", "cc1"])
def test_the_fixed_param_rule_refuses_each_mutation(vector, mutation) -> None:
    base = S.build_driver_vector() if vector == "driver" else _fixture_cc1_argv()
    assert _fixed_param_failures(base) == []
    assert _fixed_param_failures(_PARAM_MUTATIONS[mutation](list(base))) != []


@pytest.mark.parametrize("mutation", ["reordered", "moved last"])
def test_reordering_the_fixed_params_breaks_the_driver_contract(mutation) -> None:
    """GCC treats the two independently, so a reordered vector passes the
    once-only rule; it is still refused, because the driver's echo of it, which
    IC-1 and cc1.v compare exactly, is no longer the pinned one."""
    vector = S.build_driver_vector()
    i = vector.index(FIXED_TOKENS[0])
    if mutation == "reordered":
        vector[i], vector[i + 1] = vector[i + 1], vector[i]
    else:
        del vector[i:i + 2]
        vector[vector.index("-o"):vector.index("-o")] = list(FIXED_TOKENS)
    assert _fixed_param_failures(vector) == []
    assert S.collect_gcc_options(vector) != IC1.COLLECT_GCC_OPTIONS


@pytest.mark.parametrize("index", [2, 3])
@pytest.mark.parametrize("mutation", sorted(_PARAM_MUTATIONS))
def test_ic1_refuses_a_traced_vector_without_exactly_one_fixed_param(index, mutation) -> None:
    argv = _PARAM_MUTATIONS[mutation](list(_ARGVS[index]))
    path = C.IC1_EXEC_SEQUENCE[index][0]
    r = _ic1(_trace(argvs={index: argv}))
    _fails_with(r, f": {path}: ")


def test_ic1_names_the_offending_fixed_param() -> None:
    cc1 = _ARGVS[3] + ["--param=ggc-min-expand=94"]
    _fails_with(_ic1(_trace(argvs={3: cc1})),
                f"{CC1}: ggc-min-expand is also given as ['--param=ggc-min-expand=94']")
    driver = [w for w in _ARGVS[2] if w != FIXED_TOKENS[1]]
    _fails_with(_ic1(_trace(argvs={2: driver})),
                "/usr/bin/gcc-15: --param=ggc-min-heapsize=131072 appears 0 times, not once")


def test_ic1_the_fixed_param_contract_is_load_bearing(monkeypatch) -> None:
    """Mutating the checker's contract makes a conforming trace fail."""
    assert _ic1(GOOD_TRACE)["verdict"] == "pass"
    monkeypatch.setattr(IC1, "FIXED_PARAMS", (("ggc-min-expand", "94"), ("ggc-min-heapsize", "131072")))
    _fails_with(_ic1(GOOD_TRACE), "--param=ggc-min-expand=94 appears 0 times, not once")


def test_the_fixture_records_the_fixed_values_exactly_once_per_line() -> None:
    text = (S.VERIFY / "fixtures" / "cc1.v.baseline").read_text()
    lines = text.splitlines()
    assert [l for l in lines if l.startswith("GGC heuristics:")] == [GGC_LINE]
    echo = [l for l in lines if l.startswith("COLLECT_GCC_OPTIONS=")]
    assert len(echo) == 2
    assert echo[0] == "COLLECT_GCC_OPTIONS=" + IC1.COLLECT_GCC_OPTIONS
    for line in [*echo, *(l for l in lines if l.startswith(f" {CC1} "))]:
        for token in FIXED_TOKENS:
            assert line.count(token) == 1, (token, line[:60])
    assert _fixed_param_failures(_fixture_cc1_argv()) == []


def test_the_fixture_differs_from_b1_only_by_the_fixed_params() -> None:
    """Removing the three insertions — two driver echoes and the cc1 command
    line — gives back the accepted B1 fixture byte for byte."""
    data = (S.VERIFY / "fixtures" / "cc1.v.baseline").read_bytes()
    echo = b" ".join(b"'" + t.encode() + b"'" for t in FIXED_TOKENS) + b" "
    cc1 = b" " + b" ".join(t.encode() for t in FIXED_TOKENS)
    assert data.count(echo) == 2 and data.count(cc1) == 1
    b1 = data.replace(echo, b"").replace(cc1, b"")
    assert (len(b1), _sha_bytes(b1)) == B1_FIXTURE
    assert b"--param" not in b1.replace(b"GGC heuristics: --param ggc-min-expand=100 --param ", b"")


def _sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


@pytest.mark.parametrize("ggc", [
    "GGC heuristics: --param ggc-min-expand=94 --param ggc-min-heapsize=2169",
    "GGC heuristics: --param ggc-min-expand=100 --param ggc-min-heapsize=131071",
])
def test_cc1check_still_hard_stops_on_any_ggc_difference(ggc) -> None:
    cc1check = S.load("cc1check")
    data = (S.VERIFY / "fixtures" / "cc1.v.baseline").read_bytes()
    actual = data.replace(GGC_LINE.encode(), ggc.encode())
    assert actual != data
    assert cc1check.compare_cc1_v(data, actual).verdict == "HARD_STOP"
    assert cc1check.compare_cc1_v(data, data).verdict == "PASS"
