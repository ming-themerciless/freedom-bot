"""T-L10 — the control-transfer and stack verifier (proposal §5.12.1, §5.14).

T-L10 checks **the listing text**: an instruction stream in the committed
listing's AT&T spelling, plus the image facts (entry, `.text`, `.rodata`, the
function table). It does not check the kernel (D9-1). T-L7 ties the listing's
bytes to the image; **T-L11, not T-L7 or T-L9, ties its decoding to the image**.
A T-L10 verdict is evidence only together with a passing T-L11 over the same
listing digest and an image whose digest equals `expected.sha256` (XD-7).

It has its own parser and shares no decoding or parsing code with XD.

What it checks, mechanically:

* every instruction's mnemonic is on the contract's permitted list, which
  contains no `call` and no `ret` (§5.14.1); no `%fs`/`%gs` operand; no
  indirect operand;
* CT classes and every direct target: `jcc`/`jmp` targets are instruction
  starts in the same function, except the single CT-4 `jmp`, `_start`'s last
  instruction, which targets `rp11_main`'s first (RI-2, RI-3);
* tiling: the function set is exactly `_start`, `rp11_main`; they tile `.text`;
  `_start` is the entry; terminal instructions (RI-1 … RI-3);
* the static `%rsp` offset by abstract interpretation: consistent at every join,
  never negative, maximum within the contract bound (RI-4);
* every store other than `push` is `disp(%rsp)` with constant `disp`, no index,
  `0 ≤ disp` and `disp + width ≤ o(i)` (RI-5); `_start` stores nothing but
  `push $0` and loads only `argc` (HR-6);
* every `syscall`'s number and arguments, by constant propagation over the
  graph with a zero-flag edge refinement: the §5.4 inventory, every output
  pointer NULL (RI-6), the exact `execve` vectors and `INVOCATION_ID` buffer,
  and every refusal's `write(2, line, length)` followed by `exit_group(status)`
  and `ud2` (§5.9, RI-3).

It emits the function table, the per-instruction `%rsp` offset, the store and
load tables, the call graph and the maximum stack depth, for HR-1 … HR-6.
Standard library only.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

CTV_VERSION = "rp11-ctverify/1"

# ---------------------------------------------------------------------------
# Listing parsing (T-L10's own grammar)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Line:
    address: int
    raw: bytes
    text: str


@dataclass(frozen=True)
class Facts:
    entry: int
    text: tuple[int, int]
    rodata: tuple[int, int]
    rodata_bytes: bytes
    functions: tuple[tuple[str, int, int], ...]


class ListingError(Exception):
    pass


def parse_listing(listing: str) -> tuple[Facts, list[Line]]:
    sections = _split_sections(listing)
    readelf = sections.get("readelf")
    dis = sections.get("disassembly")
    dump = sections.get("rodata")
    if readelf is None or dis is None or dump is None:
        raise ListingError("listing lacks a readelf, disassembly or .rodata section")
    entry = None
    sects: dict[str, tuple[int, int]] = {}
    funcs = []
    for line in readelf:
        m = re.match(r"^\s+Entry point address:\s+0x([0-9a-f]+)$", line)
        if m:
            entry = int(m.group(1), 16)
        m = re.match(r"^\s+\[\s*\d+\]\s+(\S+)\s+\S+\s+([0-9a-f]{16})\s+[0-9a-f]+\s+([0-9a-f]+)\s", line)
        if m:
            sects[m.group(1)] = (int(m.group(2), 16), int(m.group(3), 16))
        m = re.match(r"^\s+\d+:\s+([0-9a-f]{16})\s+(\d+)\s+FUNC\s+\S+\s+\S+\s+\S+\s+(\S+)$", line)
        if m:
            funcs.append((m.group(3), int(m.group(1), 16), int(m.group(2))))
    if entry is None or ".text" not in sects or ".rodata" not in sects:
        raise ListingError("readelf section lacks the entry or the .text/.rodata headers")
    ro_addr, ro_size = sects[".rodata"]
    ro = bytearray()
    for line in dump:
        m = re.match(r"^ ([0-9a-f]+) ((?:[0-9a-f]{2,8} ?){1,4})\s", line + " ")
        if m:
            addr = int(m.group(1), 16)
            if addr != ro_addr + len(ro):
                raise ListingError(".rodata dump is not contiguous")
            ro += bytes.fromhex(m.group(2).replace(" ", ""))
    if len(ro) != ro_size:
        raise ListingError(".rodata dump size differs from its section header")
    lines = []
    try:
        dis = dis[dis.index("Disassembly of section .text:") + 1:]
    except ValueError as exc:
        raise ListingError("no '.text' disassembly in the listing") from exc
    for raw_line in dis:
        if not raw_line.strip() or re.match(r"^[0-9a-f]{16} <", raw_line):
            continue
        m = re.match(r"^ +([0-9a-f]+):\t([0-9a-f ]+?)\s*\t(.*)$", raw_line)
        if not m:
            raise ListingError(f"unparsed disassembly line {raw_line!r}")
        lines.append(Line(int(m.group(1), 16), bytes.fromhex(m.group(2).replace(" ", "")),
                          " ".join(m.group(3).split())))
    text = (sects[".text"][0], sects[".text"][0] + sects[".text"][1])
    funcs.sort(key=lambda f: f[1])
    return Facts(entry, text, (ro_addr, ro_addr + ro_size), bytes(ro), tuple(funcs)), lines


def _split_sections(listing: str) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    current = None
    for line in listing.splitlines():
        if line.startswith("== readelf"):
            current = "readelf"
        elif line.startswith("== objdump -d"):
            current = "disassembly"
        elif line.startswith("== objdump -s"):
            current = "rodata"
        elif current:
            out.setdefault(current, []).append(line)
            continue
        else:
            continue
        out[current] = []
    return out


# ---------------------------------------------------------------------------
# AT&T operand parsing
# ---------------------------------------------------------------------------

_REGS = {}
for _num, names in enumerate(zip(
        ("rax", "rcx", "rdx", "rbx", "rsp", "rbp", "rsi", "rdi", "r8", "r9", "r10", "r11", "r12", "r13", "r14", "r15"),
        ("eax", "ecx", "edx", "ebx", "esp", "ebp", "esi", "edi", "r8d", "r9d", "r10d", "r11d", "r12d", "r13d", "r14d", "r15d"),
        ("ax", "cx", "dx", "bx", "sp", "bp", "si", "di", "r8w", "r9w", "r10w", "r11w", "r12w", "r13w", "r14w", "r15w"),
        ("al", "cl", "dl", "bl", "spl", "bpl", "sil", "dil", "r8b", "r9b", "r10b", "r11b", "r12b", "r13b", "r14b", "r15b"))):
    for width, name in zip((64, 32, 16, 8), names):
        _REGS[name] = (_num, width)
for _name, _num in (("ah", 0), ("ch", 1), ("dh", 2), ("bh", 3)):
    _REGS[_name] = (_num, 8)
RSP = 4
SUFFIX_WIDTH = {"b": 8, "w": 16, "l": 32, "q": 64}


@dataclass(frozen=True)
class Op:
    kind: str                 # reg, imm, mem, target
    reg: int = -1
    width: int = 0
    value: int = 0
    base: int = -1
    index: int = -1
    scale: int = 1
    disp: int = 0
    segment: str = ""
    indirect: bool = False


def _split_operands(s: str) -> list[str]:
    out, depth, cur = [], 0, ""
    for ch in s:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        if ch == "," and depth == 0:
            out.append(cur)
            cur = ""
        else:
            cur += ch
    if cur:
        out.append(cur)
    return out


def parse_operand(tok: str) -> Op:
    tok = tok.strip()
    indirect = tok.startswith("*")
    tok = tok.lstrip("*")
    if tok.startswith("%"):
        name = tok[1:]
        if name not in _REGS:
            return Op("bad", segment=name)
        num, width = _REGS[name]
        return Op("reg", reg=num, width=width, indirect=indirect)
    if tok.startswith("$"):
        return Op("imm", value=int(tok[1:], 16))
    m = re.match(r"^([0-9a-f]+) <[^>]+>$", tok)
    if m:
        return Op("target", value=int(m.group(1), 16), indirect=indirect)
    m = re.match(r"^(?:%([fg]s):)?(-?0x[0-9a-f]+)?\((%\w+)?(?:,(%\w+),(\d))?\)$", tok)
    if m:
        seg, disp, base, index, scale = m.groups()
        return Op("mem", base=_REGS[base[1:]][0] if base else -1,
                  index=_REGS[index[1:]][0] if index else -1, scale=int(scale or 1),
                  disp=int(disp, 16) if disp else 0, segment=seg or "", indirect=indirect)
    m = re.match(r"^(?:%([fg]s):)?(-?0x[0-9a-f]+)$", tok)
    if m:
        return Op("mem", disp=int(m.group(2), 16), segment=m.group(1) or "", indirect=indirect)
    return Op("bad", segment=tok)


@dataclass(frozen=True)
class Insn:
    address: int
    length: int
    text: str
    mnemonic: str
    ops: tuple[Op, ...]          # AT&T order: sources first, destination last


def to_insns(lines) -> list[Insn]:
    out = []
    for ln in lines:
        mnemonic, _, rest = ln.text.partition(" ")
        ops = tuple(parse_operand(t) for t in _split_operands(rest)) if rest else ()
        out.append(Insn(ln.address, len(ln.raw), ln.text, mnemonic, ops))
    return out


# ---------------------------------------------------------------------------
# Abstract values
# ---------------------------------------------------------------------------

TOP = ("top",)


def const(v: int) -> tuple:
    return ("const", v & 0xFFFFFFFFFFFFFFFF)


def stack(a: int) -> tuple:
    return ("stack", a)


INPUT = ("input",)


@dataclass
class State:
    o: int
    regs: list
    mem: dict                  # frame address offset a -> (width, value)
    zf_reg: int | None = None  # register whose zero-ness the zero flag reflects

    def copy(self) -> "State":
        return State(self.o, list(self.regs), dict(self.mem), self.zf_reg)

    def key(self):
        return (self.o, tuple(self.regs), tuple(sorted(self.mem.items())), self.zf_reg)


def _join_value(x: tuple, y: tuple) -> tuple:
    if x == y:
        return x
    # An input-derived pointer joined with NULL is still input-derived: a
    # NULL dereference faults (CT-8) and reads nothing.
    if {x, y} == {INPUT, const(0)}:
        return INPUT
    return TOP


def _join(a: State, b: State) -> State | None:
    if a.o != b.o:
        return None
    regs = [_join_value(x, y) for x, y in zip(a.regs, b.regs)]
    mem = {k: v for k, v in a.mem.items() if b.mem.get(k) == v}
    return State(a.o, regs, mem, a.zf_reg if a.zf_reg == b.zf_reg else None)


# ---------------------------------------------------------------------------
# Verification
# ---------------------------------------------------------------------------


class Verdict:
    def __init__(self) -> None:
        self.violations: list[str] = []

    def fail(self, msg: str) -> None:
        self.violations.append(msg)


def verify(facts: Facts, lines, contract: dict) -> dict:
    v = Verdict()
    insns = to_insns(lines)
    by_addr = {i.address: i for i in insns}
    order = [i.address for i in insns]
    nxt = {a: order[k + 1] for k, a in enumerate(order[:-1])}
    names = tuple(f[0] for f in facts.functions)
    permitted = set(contract["permitted_mnemonics"])
    transfers = set(contract["conditional_jumps"])

    # -- tiling and function set (RI-1, RI-2) --------------------------------
    if names != tuple(contract["functions"]):
        v.fail(f"function set {names} differs from {contract['functions']}")
    fn_of = {}
    for name, start, size in facts.functions:
        for a in order:
            if start <= a < start + size:
                fn_of[a] = name
    if facts.functions:
        (n0, s0, z0), *rest = facts.functions
        if not (s0 == facts.entry == facts.text[0]):
            v.fail("_start, e_entry and .text start differ")
        end = s0 + z0
        for _n, s, z in rest:
            if s != end:
                v.fail("functions do not tile .text")
            end = s + z
        if end != facts.text[1]:
            v.fail("functions do not end at the end of .text")
    if order and (order[0] != facts.text[0] or insns[-1].address + insns[-1].length != facts.text[1]):
        v.fail("the instruction stream does not cover .text exactly")
    for a, b in zip(insns, insns[1:]):
        if a.address + a.length != b.address:
            v.fail(f"gap or overlap at 0x{a.address:x}")

    # -- permitted list, operands, CT classes (§5.14.1) ----------------------
    start_insns = [i for i in insns if fn_of.get(i.address) == "_start"]
    main_start = next((s for n, s, _z in facts.functions if n == "rp11_main"), None)
    edges = []
    for ins in insns:
        if ins.mnemonic not in permitted:
            v.fail(f"0x{ins.address:x}: {ins.mnemonic!r} is not on the permitted list")
        for op in ins.ops:
            if op.kind == "bad":
                v.fail(f"0x{ins.address:x}: unparsed operand {op.segment!r}")
            if op.segment:
                v.fail(f"0x{ins.address:x}: segment operand %{op.segment}")
            if op.indirect:
                v.fail(f"0x{ins.address:x}: indirect operand")
        if ins.mnemonic == "jmp" or ins.mnemonic in transfers:
            if len(ins.ops) != 1 or ins.ops[0].kind != "target":
                v.fail(f"0x{ins.address:x}: transfer without a direct target")
                continue
            t = ins.ops[0].value
            if t not in by_addr:
                v.fail(f"0x{ins.address:x}: target 0x{t:x} is not an instruction start")
                continue
            is_entry = ins.mnemonic == "jmp" and start_insns and ins is start_insns[-1]
            if is_entry:
                if t != main_start:
                    v.fail("the CT-4 jmp does not target rp11_main's first instruction")
                edges.append(["_start", "rp11_main", "CT-4"])
            elif fn_of.get(t) != fn_of.get(ins.address):
                v.fail(f"0x{ins.address:x}: target 0x{t:x} leaves its function")
    if not start_insns or start_insns[-1].mnemonic != "jmp":
        v.fail("_start's last instruction is not the CT-4 jmp")
    for name, start, size in facts.functions:
        mine = [i for i in insns if fn_of.get(i.address) == name]
        if mine and mine[-1].mnemonic not in ("jmp", "ud2"):
            v.fail(f"{name} ends in {mine[-1].mnemonic}, not jmp or ud2")

    # -- abstract interpretation (RI-4 … RI-6, syscalls) ---------------------
    o_at: dict[int, int] = {}
    stores, loads, sites = [], [], []
    entry_state = State(0, [TOP] * 16, {})
    states: dict[int, State] = {facts.entry: entry_state}
    work = [facts.entry]
    seen_keys: dict[int, tuple] = {}
    visits = 0
    while work:
        visits += 1
        if visits > 200000:
            v.fail("abstract interpretation did not converge")
            break
        addr = work.pop()
        st = states[addr]
        k = st.key()
        if seen_keys.get(addr) == k:
            continue
        seen_keys[addr] = k
        ins = by_addr.get(addr)
        if ins is None:
            v.fail(f"control reaches 0x{addr:x}, not an instruction start")
            continue
        if st.o < 0:
            v.fail(f"0x{addr:x}: %rsp offset is negative")
        o_at[addr] = st.o
        succs = _step(ins, st.copy(), v, fn_of.get(addr), stores, loads, sites, facts, contract, nxt)
        for target, new in succs:
            if target in states:
                joined = _join(states[target], new)
                if joined is None:
                    v.fail(f"0x{target:x}: %rsp offset differs at a join")
                    continue
                if joined.key() != states[target].key():
                    states[target] = joined
                    work.append(target)
                elif target not in seen_keys:
                    work.append(target)
            else:
                states[target] = new
                work.append(target)
    for a in order:
        if a not in o_at:
            v.fail(f"0x{a:x} is unreached")

    max_main = max((o for a, o in o_at.items() if fn_of.get(a) == "rp11_main"), default=0)
    # _start: alignment can drop %rsp by up to 15 bytes, then push $0 (8).
    max_depth = 15 + 8 + max_main
    if max_main > contract["frame_bound"]:
        v.fail(f"rp11_main frame {max_main} exceeds {contract['frame_bound']}")
    if max_depth > contract["stack_bound"]:
        v.fail(f"maximum stack depth {max_depth} exceeds {contract['stack_bound']}")
    if max_main != contract["expected_frame"]:
        v.fail(f"rp11_main frame {max_main} differs from the contract's {contract['expected_frame']}")

    _check_sites(sites, v, contract, facts)
    for site in sites:
        if site.get("function") != "rp11_main":
            v.fail(f"0x{site['address']:x}: system call outside rp11_main")
        if site.get("name") == "exit_group":
            follow = by_addr.get(site["next"]) if site["next"] is not None else None
            site["followed_by_ud2"] = follow is not None and follow.mnemonic == "ud2"
            if not site["followed_by_ud2"]:
                v.fail(f"0x{site['address']:x}: exit_group is not followed immediately by ud2 (RI-3)")
    _dedupe(stores)
    _dedupe(loads)
    return {
        "ctverify_version": CTV_VERSION,
        "functions": [list(f) for f in facts.functions],
        "rsp_offset": {f"0x{a:x}": o_at[a] for a in sorted(o_at)},
        "stores": stores,
        "loads": loads,
        "syscalls": sorted(sites, key=lambda s: s["address"]),
        "call_graph": edges,
        "max_rp11_main_frame": max_main,
        "max_stack_depth": max_depth,
        "violations": sorted(set(v.violations)),
        "verdict": "pass" if not v.violations else "fail",
    }


def _dedupe(rows: list) -> None:
    seen, out = set(), []
    for r in sorted(rows, key=lambda r: json.dumps(r, sort_keys=True)):
        k = json.dumps(r, sort_keys=True)
        if k not in seen:
            seen.add(k)
            out.append(r)
    rows[:] = out


def _width_of(ins: Insn) -> int:
    for op in ins.ops:
        if op.kind == "reg":
            return op.width
    m = ins.mnemonic
    if m == "movabs":
        return 64
    if m[-1] in SUFFIX_WIDTH and m[:-1] in ("mov", "cmp", "add", "sub", "and", "or", "xor", "test", "inc", "dec"):
        return SUFFIX_WIDTH[m[-1]]
    return 64


def _addr_value(op: Op, st: State) -> tuple:
    """The abstract value of a memory operand's address."""
    if op.base == RSP and op.index < 0:
        return stack(op.disp - st.o)
    if op.base < 0 and op.index < 0:
        return const(op.disp)
    base = st.regs[op.base] if op.base >= 0 else const(0)
    if base == INPUT:
        return INPUT
    return TOP


def _read(op: Op, st: State, ins: Insn, loads, fn, facts, v: "Verdict") -> tuple:
    if op.kind == "imm":
        return const(op.value)
    if op.kind == "reg":
        val = st.regs[op.reg]
        if op.width == 64:
            return val
        if val[0] == "const":
            return const(val[1] & ((1 << op.width) - 1))
        return INPUT if val == INPUT else TOP
    if op.kind == "mem":
        addr = _addr_value(op, st)
        kind = {"stack": "frame", "input": "input-derived", "const": "absolute"}.get(addr[0], "unknown")
        row = {"address": ins.address, "text": ins.text, "function": fn, "base": kind}
        if addr[0] == "stack":
            row["frame_offset"] = addr[1]
        loads.append(row)
        if addr[0] == "stack" and fn == "rp11_main" and addr[1] >= 0:
            v.fail(f"0x{ins.address:x}: load at or above rp11_main's entry slot (BI-7)")
        if addr[0] in ("const", "top") and fn == "rp11_main":
            v.fail(f"0x{ins.address:x}: load through neither the frame nor an input pointer")
        if addr == INPUT:
            return INPUT
        return TOP
    return TOP


def _write_reg(st: State, op: Op, val: tuple) -> None:
    if op.width == 64:
        st.regs[op.reg] = val
    elif op.width == 32:
        st.regs[op.reg] = const(val[1] & 0xFFFFFFFF) if val[0] == "const" else (INPUT if val == INPUT else TOP)
    else:
        st.regs[op.reg] = INPUT if val == INPUT else TOP
    if st.zf_reg == op.reg:
        st.zf_reg = None


def _store(st: State, ins: Insn, op: Op, width: int, val: tuple, v: Verdict, stores, fn) -> None:
    if op.base != RSP or op.index >= 0:
        v.fail(f"0x{ins.address:x}: store not through a constant %rsp displacement (RI-5)")
        stores.append({"address": ins.address, "text": ins.text, "function": fn, "slot": None})
        return
    d, w = op.disp, width // 8
    if not (0 <= d and d + w <= st.o):
        v.fail(f"0x{ins.address:x}: store {d}+{w} outside the frame of depth {st.o} (RI-5)")
    a = d - st.o
    for k in [k for k, (kw, _x) in st.mem.items() if k < a + w and a < k + kw]:
        del st.mem[k]
    st.mem[a] = (w, val)
    stores.append({"address": ins.address, "text": ins.text, "function": fn,
                   "frame_offset": a, "width": w, "value": _describe(val)})


def _describe(val: tuple) -> str:
    if val[0] == "const":
        return f"0x{val[1]:x}"
    if val[0] == "stack":
        return f"frame{val[1]:+d}"
    return val[0]


_ARITH = {"add", "sub", "and", "or", "xor", "inc", "dec", "shr", "shl", "sar", "neg", "not"}


def _step(ins: Insn, st: State, v: Verdict, fn, stores, loads, sites, facts, contract, nxt):
    m = ins.mnemonic
    ops = ins.ops
    fall = nxt.get(ins.address)
    base = m.rstrip("bwlq") if m not in ("movabs", "sub", "sbb", "shl", "jb", "setb") else m
    if m in ("movb", "movw", "movl", "movq"):
        base = "mov"
    if m in ("cmpb", "cmpw", "cmpl", "cmpq"):
        base = "cmp"

    # Every memory operand read here is recorded in the load table.
    def src(op):
        return _read(op, st, ins, loads, fn, facts, v)

    if fn == "_start" and any(op.kind == "mem" for op in ops) and m not in ("lea",):
        mem = next(op for op in ops if op.kind == "mem")
        if not (m == "mov" and mem.base == RSP and mem.disp == 0 and st.o == 0):
            v.fail(f"0x{ins.address:x}: _start may load only argc at 0(%rsp) (HR-6)")

    if m in ("jmp",):
        if not ops or ops[0].kind != "target":
            return []
        if fn == "_start":
            # CT-4. RI-4 measures rp11_main's offset from its entry %rsp, which
            # points at the zero word _start pushed; that word is not frame.
            st = State(0, list(st.regs), {}, None)
        return [(ops[0].value, st)]
    if m in contract["conditional_jumps"]:
        taken, not_taken = st.copy(), st.copy()
        if st.zf_reg is not None and m in ("je", "jne"):
            zero = taken if m == "je" else not_taken
            zero.regs[st.zf_reg] = const(0)
        return [(ops[0].value, taken), (fall, not_taken)]
    if m == "ud2":
        return []
    if m == "syscall":
        sites.append(_site(ins, st, fn, nxt))
        for r in (0, 1, 11):     # %rax (result), %rcx and %r11 (AD-12)
            st.regs[r] = TOP
        st.zf_reg = None
        num = st.regs[0]
        return [(fall, st)] if fall is not None else []

    if base == "push":
        if fn == "_start" and not (ops[0].kind == "imm" and ops[0].value == 0):
            v.fail(f"0x{ins.address:x}: _start may push only $0")
        val = src(ops[0])
        st.o += 8
        _store(st, ins, Op("mem", base=RSP, disp=0), 64, val, v, [], fn)
        stores.append({"address": ins.address, "text": ins.text, "function": fn,
                       "frame_offset": -st.o, "width": 8, "value": _describe(val), "implicit": "push"})
    elif base == "pop":
        loads.append({"address": ins.address, "text": ins.text, "function": fn, "base": "frame",
                      "frame_offset": -st.o})
        st.o -= 8
        _write_reg(st, ops[0], TOP)
    elif m in ("mov", "movb", "movw", "movl", "movq", "movabs"):
        s, d = ops
        val = src(s)
        if d.kind == "reg":
            if d.reg == RSP:
                v.fail(f"0x{ins.address:x}: %rsp assigned (RI-4)")
            if s.kind == "imm" and d.width == 64 and m != "movabs":
                val = const(s.value if s.value < 0x80000000 else s.value | 0xFFFFFFFF00000000)
            _write_reg(st, d, val)
        else:
            _store(st, ins, d, _width_of(ins) if s.kind == "imm" else s.width, val, v, stores, fn)
    elif m == "lea":
        s, d = ops
        if s.base == RSP and s.index < 0:
            val = stack(s.disp - st.o)
        elif s.base >= 0 and s.index < 0 and st.regs[s.base] == INPUT:
            val = INPUT
        elif s.base >= 0 and s.index < 0 and st.regs[s.base][0] == "const":
            val = const(st.regs[s.base][1] + s.disp)
        else:
            val = TOP
        if fn == "_start":
            val = TOP if d.reg not in (6, 2) else INPUT
        if d.reg == RSP:
            v.fail(f"0x{ins.address:x}: lea into %rsp (RI-4)")
        _write_reg(st, d, val)
        if d.width == 64 and val[0] != "top":
            st.regs[d.reg] = val
    elif base in ("cmp", "test"):
        for op in ops:
            if op.kind == "mem":
                src(op)
        st.zf_reg = None
        if base == "test" and len(ops) == 2 and ops[0].kind == ops[1].kind == "reg" \
                and ops[0].reg == ops[1].reg and ops[0].width >= 32:
            st.zf_reg = ops[0].reg
    elif base in _ARITH or m in _ARITH:
        name = m if m in _ARITH else base
        d = ops[-1]
        s = ops[0] if len(ops) == 2 else None
        if d.kind == "mem":
            v.fail(f"0x{ins.address:x}: read-modify-write of memory")
            return [(fall, st)]
        if d.reg == RSP:
            if fn == "_start" and name == "and" and s is not None and s.kind == "imm" \
                    and s.value == 0xFFFFFFFFFFFFFFF0:
                pass  # RI-4: _start alone aligns; the offset is bounded below by 15 bytes
            elif name in ("sub", "add") and s is not None and s.kind == "imm":
                st.o += s.value if name == "sub" else -s.value
            else:
                v.fail(f"0x{ins.address:x}: %rsp changed other than by a constant (RI-4)")
            st.zf_reg = None
            return [(fall, st)] if fall is not None else []
        cur = st.regs[d.reg]
        sv = src(s) if s is not None else None
        if name == "xor" and s is not None and s.kind == "reg" and s.reg == d.reg:
            res = const(0)
        elif cur[0] == "const" and (sv is None or sv[0] == "const"):
            a = cur[1] & ((1 << d.width) - 1) if d.width < 64 else cur[1]
            b = sv[1] if sv is not None else 1
            res = const({"add": a + b, "sub": a - b, "and": a & b, "or": a | b, "xor": a ^ b,
                         "inc": a + 1, "dec": a - 1, "shr": a >> (b & 63), "shl": a << (b & 63),
                         "sar": a >> (b & 63), "neg": -a, "not": ~a}[name] & ((1 << d.width) - 1))
        elif cur == INPUT and name in ("add", "sub") and sv is not None and sv[0] == "const":
            res = INPUT
        else:
            res = TOP
        _write_reg(st, d, res)
        st.zf_reg = d.reg if d.width >= 32 and name in ("add", "sub", "and", "or", "xor", "inc", "dec") else None
        return [(fall, st)] if fall is not None else []
    else:
        v.fail(f"0x{ins.address:x}: no semantics for {m!r}")
    if base not in ("cmp", "test"):
        st.zf_reg = None if base not in ("mov", "movabs", "lea", "push", "pop") else st.zf_reg
    return [(fall, st)] if fall is not None else []


def _site(ins: Insn, st: State, fn, nxt) -> dict:
    def show(val):
        return _describe(val)
    regs = {"rax": st.regs[0], "rdi": st.regs[7], "rsi": st.regs[6], "rdx": st.regs[2], "r10": st.regs[10]}
    site = {"address": ins.address, "function": fn, "next": nxt.get(ins.address),
            "args": {k: show(v) for k, v in regs.items()}, "_raw": regs, "_mem": dict(st.mem)}
    return site


def _string_at(facts: Facts, addr: int) -> bytes | None:
    lo, hi = facts.rodata
    if not (lo <= addr < hi):
        return None
    data = facts.rodata_bytes[addr - lo:]
    end = data.find(b"\0")
    return data[:end] if end >= 0 else None


def _check_sites(sites, v: Verdict, contract: dict, facts: Facts) -> None:
    by_addr: dict[int, list] = {}
    for s in sites:
        by_addr.setdefault(s["address"], []).append(s)
    lines = {int(k): (bytes(v_["line"], "ascii"), v_["status"]) for k, v_ in contract["status_lines"].items()}
    inventory = {int(k): name for k, name in contract["syscalls"].items()}
    merged = []
    for addr, group in sorted(by_addr.items()):
        raw = group[0]["_raw"]
        for g in group[1:]:
            raw = {k: (x if x == g["_raw"][k] else TOP) for k, x in raw.items()}
        mem = group[0]["_mem"]
        for g in group[1:]:
            mem = {k: x for k, x in mem.items() if g["_mem"].get(k) == x}
        merged.append((addr, group[0], raw, mem))
    exit_after_write: dict[int, int] = {}
    for addr, site, raw, mem in merged:
        rax = raw["rax"]
        out = site
        out["args"] = {k: _describe(x) for k, x in raw.items()}
        del out["_raw"], out["_mem"]
        if rax[0] != "const" or rax[1] not in inventory:
            v.fail(f"0x{addr:x}: system-call number {_describe(rax)} is not in the inventory")
            continue
        name = inventory[rax[1]]
        out["name"] = name
        rdi, rsi, rdx, r10 = raw["rdi"], raw["rsi"], raw["rdx"], raw["r10"]

        def need(cond: bool, what: str) -> None:
            if not cond:
                v.fail(f"0x{addr:x}: {name}: {what}")

        if name == "fcntl":
            need(rsi == const(1), "command is not F_GETFD")
            need(rdi[0] == "const" and rdi[1] in (0, 1, 2), "descriptor is not 0, 1 or 2")
        elif name == "close_range":
            need(rdi == const(3) and rsi == const(0xFFFFFFFF) and rdx == const(0), "not close_range(3, ~0U, 0)")
        elif name == "rt_sigaction":
            need(rdx == const(0), "old-action pointer is not NULL (RI-6)")
            need(r10 == const(8), "sigset size is not 8")
            need(rsi[0] == "stack" and _zero_bytes(mem, rsi[1], 32), "new action is not 32 zero bytes")
        elif name == "rt_sigprocmask":
            need(rdi == const(2), "how is not SIG_SETMASK")
            need(rdx == const(0), "old-set pointer is not NULL (RI-6)")
            need(r10 == const(8), "sigset size is not 8")
            need(rsi[0] == "stack" and _zero_bytes(mem, rsi[1], 8), "new set is not 8 zero bytes")
        elif name == "umask":
            need(rdi == const(0o77), "mask is not 0077")
        elif name == "chdir":
            need(rdi[0] == "const" and _string_at(facts, rdi[1]) == b"/", "path is not \"/\"")
        elif name == "execve":
            _check_execve(rdi, rsi, rdx, mem, need, facts, contract)
        elif name == "write":
            need(rdi == const(2), "descriptor is not 2")
            line = None
            if rsi[0] == "const" and rdx[0] == "const":
                lo, _hi = facts.rodata
                line = facts.rodata_bytes[rsi[1] - lo:rsi[1] - lo + rdx[1]]
            match = [st for (ln, st) in lines.values() if ln == line]
            need(bool(match), "line is not one of the §5.9 class lines")
            if match:
                exit_after_write[addr] = match[0]
        elif name == "exit_group":
            need(rdi[0] == "const" and rdi[1] in {s for (_l, s) in lines.values()}, "status is not 111 ... 117")
    # Pairing: write, then the very next system call in the same block is
    # exit_group with that line's status, and ud2 follows it (§5.9, RI-3).
    site_at = {addr: (site, raw) for addr, site, raw, _m in merged}
    for waddr, status in exit_after_write.items():
        e = next((a for a in sorted(site_at) if a > waddr), None)
        if e is None or site_at[e][0].get("name") != "exit_group" or site_at[e][1]["rdi"] != const(status):
            v.fail(f"0x{waddr:x}: write is not followed by exit_group({status})")
    sites[:] = [site for _a, site, _r, _m in merged]


def _zero_bytes(mem: dict, a: int, n: int) -> bool:
    covered = 0
    for k in range(a, a + n):
        hit = [(ka, w, val) for ka, (w, val) in mem.items() if ka <= k < ka + w]
        if len(hit) != 1 or hit[0][2] != const(0):
            return False
        covered += 1
    return covered == n


def _byte_at(mem: dict, k: int):
    for ka, (w, val) in mem.items():
        if ka <= k < ka + w:
            if val[0] == "const":
                return (val[1] >> (8 * (k - ka))) & 0xFF
            return val[0]
    return None


def _check_execve(rdi, rsi, rdx, mem, need, facts, contract) -> None:
    need(rdi[0] == "const" and _string_at(facts, rdi[1]) == contract["execve_path"].encode(), "path literal differs")
    want_argv = [s.encode() for s in contract["execve_argv"]]
    need(rsi[0] == "stack", "argv is not a frame array")
    if rsi[0] == "stack":
        for k, want in enumerate(want_argv + [None]):
            slot = mem.get(rsi[1] + 8 * k)
            if want is None:
                need(slot == (8, const(0)), "argv is not null-terminated")
            else:
                need(slot is not None and slot[0] == 8 and slot[1][0] == "const"
                     and _string_at(facts, slot[1][1]) == want, f"argv[{k}] differs")
    need(rdx[0] == "stack", "envp is not a frame array")
    if rdx[0] == "stack":
        lits = [s.encode() for s in contract["execve_env_literals"]]
        for k, want in enumerate(lits):
            slot = mem.get(rdx[1] + 8 * k)
            need(slot is not None and slot[1][0] == "const" and _string_at(facts, slot[1][1]) == want,
                 f"envp[{k}] differs")
        idslot = mem.get(rdx[1] + 8 * len(lits))
        need(mem.get(rdx[1] + 8 * (len(lits) + 1)) == (8, const(0)), "envp is not null-terminated")
        need(idslot is not None and idslot[1][0] == "stack", "envp's INVOCATION_ID entry is not a frame buffer")
        if idslot is not None and idslot[1][0] == "stack":
            b = idslot[1][1]
            prefix = contract["invocation_id_prefix"].encode()
            for k, ch in enumerate(prefix):
                need(_byte_at(mem, b + k) == ch, f"idbuf[{k}] is not {chr(ch)!r}")
            for k in range(len(prefix), len(prefix) + 32):
                need(_byte_at(mem, b + k) == "input", f"idbuf[{k}] is not a copied input byte (HR-2)")
            need(_byte_at(mem, b + len(prefix) + 32) == 0, "idbuf is not NUL-terminated")


def verify_listing(listing: str, contract: dict) -> dict:
    facts, lines = parse_listing(listing)
    return verify(facts, lines, contract)


def tables_digest(result: dict) -> str:
    return hashlib.sha256(json.dumps(result, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def main(argv: list[str]) -> int:
    import argparse

    p = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    p.add_argument("--listing", type=Path, required=True)
    p.add_argument("--contract", type=Path, required=True, help="JSON control-transfer contract data")
    args = p.parse_args(argv)
    result = verify_listing(args.listing.read_text(), json.loads(args.contract.read_text()))
    print(json.dumps(result, sort_keys=True, indent=1))
    return 0 if result["verdict"] == "pass" else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
