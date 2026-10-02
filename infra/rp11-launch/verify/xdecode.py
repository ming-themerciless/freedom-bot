"""XD — the independent decoder of `rp11-launch`'s `.text` (proposal §5.15).

XD reads the **image file**, not the committed listing, `objdump` or `readelf`
output. With its own ELF reader it finds `.text`, `_start` and `rp11_main`,
then decodes every byte of `.text` under a **closed encoding table** written
from the architecture manuals:

* Intel 64 and IA-32 Architectures Software Developer's Manual, Volume 2
  (2A, 2B, 2C & 2D), Order Number **325383-093US** (PDF metadata dated
  2026-09-18; fetched from cdrdv2.intel.com, getContent 671110; SHA-256
  `d137a7887787bbb06c1a8b8bafd51958d8d2e16b4dff987a03226c845cca1516`).
  Cited below as **SDM**.
* AMD64 Architecture Programmer's Manual, Volume 3, Publication **24594**,
  Revision **3.20**, May 2013 (a non-AMD-hosted copy; SHA-256
  `0157e483411521e0d0abd346b2772ed8e1ca488eae6fcb52a372eb8e9c818240`).
  Cited below as **APM**. AMD's portal was not reachable non-interactively;
  the copy's provenance is recorded, not vouched for, and SDM is primary.

**Provenance (XD-9).** The table, the decoder and the T-L12 corpus were
written from those two manuals' instruction-format chapters (SDM §2.1–§2.2,
APM §1.1–§1.8), their per-instruction opcode tables (SDM chapters 3–6, APM
chapter 3) and their opcode maps (SDM Appendix A, APM Appendix A). They were
written **before the first build of the image existed**, without reading
binutils source, binutils opcode tables, `objdump` output or the committed
listing. The author is a language model; the absence of binutils influence on
its prior knowledge is a review fact (TD-3), not something this file can show.
The *spelling table* (`xdecode-spelling.table`) is different: it is
presentation only, and it necessarily describes the listing's print format.
Nothing in it can change a boundary, a length, a byte or a target, which XD
compares numerically (XD-6).

**What XD checks** (XD-1 … XD-7): complete linear-sweep decoding of `.text`
from `_start`; an independent reachability pass; the closed table; every
failure class (a) … (g) of XD-5; and exact agreement with the listing.

**What XD cannot show** (§5.15.3): that the manuals are right or that the CPU
follows them (AD-14), anything about the kernel, or the meaning of a store or
load (HR-1 … HR-6). It is not shown correct by reproducibility.

Standard library only. Python ≥ 3.10. Class-E evidence tooling (X-17), never a
build input.
"""
from __future__ import annotations

import hashlib
import json
import re
import struct
import sys
from dataclasses import dataclass, field
from pathlib import Path

XD_VERSION = "rp11-xdecode/1"

# ---------------------------------------------------------------------------
# Failure classes (XD-5)
# ---------------------------------------------------------------------------

AMBIGUOUS = "a-ambiguity"
UNSUPPORTED = "b-unsupported-encoding"
UNDECODED = "c-undecoded-byte"
OVERLAP = "d-overlapping-decode"
BAD_TARGET = "e-bad-target"
UNREACHED = "f-unreached-instruction"
DISAGREEMENT = "g-disagreement"
#: Not an XD-5 class: the image is not one XD will decode at all (wrong ELF
#: shape, missing `.text`, a function set other than `_start` and `rp11_main`).
STRUCTURE = "x-image-structure"

FAILURE_CLASSES = (
    AMBIGUOUS, UNSUPPORTED, UNDECODED, OVERLAP, BAD_TARGET, UNREACHED,
    DISAGREEMENT,
)


class AmbiguousTable(Exception):
    """The closed table lets two rows match one byte pattern (XD-5 a)."""


@dataclass(frozen=True)
class Failure:
    klass: str
    address: int | None
    detail: str

    def as_dict(self) -> dict:
        return {"class": self.klass, "address": self.address, "detail": self.detail}


# ---------------------------------------------------------------------------
# Citations
# ---------------------------------------------------------------------------

SDM = "SDM 325383-093US"
APM = "APM 24594 r3.20"
#: The format chapters every row also depends on.
FORMAT_CITATION = (
    f"{SDM} Vol.2A §2.1.1 (prefixes), §2.1.3-§2.1.5 and Tables 2-2/2-3 "
    "(ModR/M, SIB), §2.2.1-§2.2.1.7 and Tables 2-4/2-5/2-7 (REX, special "
    "cases, displacement, immediates, RIP-relative, default 64-bit operand "
    f"size), pp. 2-1..2-12; {APM} §1.1-§1.8 (encoding, prefixes, REX, ModRM/SIB, "
    "displacement, immediate, RIP-relative)"
)


def _cite(sdm: str, apm: str) -> str:
    return f"{SDM} {sdm}; {APM} {apm}"


# ---------------------------------------------------------------------------
# The closed table (XD-3)
# ---------------------------------------------------------------------------
#
# Operand specifiers:
#   E   r/m operand at the row's operand size     Eb  r/m, 8-bit
#   Ew  r/m, 16-bit                               Ed  r/m, 32-bit
#   G   ModRM.reg at the row's operand size       Gb  ModRM.reg, 8-bit
#   M   memory only (address, not accessed)       Z   register in opcode low 3 bits
#   Zb  register in opcode low 3 bits, 8-bit      A   rAX at the operand size
#   AL  the AL register                           CL  the CL register
#   ONE the literal 1                             Ib  imm8   Iz imm16/imm32
#   Iv  imm16/imm32/imm64 by operand size         J   relative displacement
#
# Operand-size modes:
#   "v"   16 (66, REX.W=0), 32 (no 66, REX.W=0) or 64 (REX.W=1, no 66), as the
#         row's `sizes` allow (SDM §2.2.1.2 Table 2-4; APM §1.2.2, §1.2.7)
#   "b"   byte operation: no 66, REX.W=0
#   "d64" default 64-bit (near branches and implicit-RSP instructions,
#         SDM §2.2.1.7): no 66, REX.W=0
#   "none" no operand size (syscall, ud2): no 66, no REX at all


@dataclass(frozen=True)
class Row:
    id: str
    mnemonic: str
    opcode: tuple[int, ...]
    osz: str
    sizes: tuple[int, ...] = ()
    modrm: bool = False
    reg: int | None = None          # required ModRM.reg digit, None = /r
    mod: str = "any"                # "any", "reg" (mod=11), "mem" (mod!=11)
    plus_r: bool = False            # low 3 bits of last opcode byte = register
    plus_cc: bool = False           # low 4 bits of last opcode byte = condition
    operands: tuple[str, ...] = ()
    imm: str = ""                   # "", "b", "z", "v"
    rel: int = 0                    # 1 or 4 byte displacement
    ct: str = "CT-1"
    stack: int = 0                  # implicit %rsp change
    e_access: str = ""              # "r", "w", "rw" or "" for the E operand
    implicit: str = ""              # "push" / "pop" implicit stack access
    sext: bool = False              # immediate sign-extended to operand size
    cite: str = ""

    def opcode_set(self) -> list[tuple[int, ...]]:
        """Every concrete opcode byte string the row accepts."""
        if self.plus_r:
            return [self.opcode[:-1] + (self.opcode[-1] + r,) for r in range(8)]
        if self.plus_cc:
            return [self.opcode[:-1] + (self.opcode[-1] + c,) for c in range(16)]
        return [self.opcode]


CONDITION_CODES = (
    "o", "no", "b", "ae", "e", "ne", "be", "a",
    "s", "ns", "p", "np", "l", "ge", "le", "g",
)

_ALU = (
    # mnemonic, base opcode, group-1 digit, SDM section+page, APM entry
    ("add", 0x00, 0, "Vol.2A §3.3 ADD p.3-14", "§3 ADD"),
    ("or", 0x08, 1, "Vol.2B §4.3 OR p.4-163", "§3 OR"),
    ("and", 0x20, 4, "Vol.2A §3.3 AND p.3-60", "§3 AND"),
    ("sub", 0x28, 5, "Vol.2B §4.3 SUB p.4-685", "§3 SUB"),
    ("xor", 0x30, 6, "Vol.2D §6.1 XOR p.6-40", "§3 XOR"),
    ("cmp", 0x38, 7, "Vol.2A §3.3 CMP p.3-161", "§3 CMP"),
)

_V = (16, 32, 64)


def _rows() -> tuple[Row, ...]:
    rows: list[Row] = []
    add = rows.append

    for name, base, digit, sdm, apm in _ALU:
        acc = "r" if name == "cmp" else "rw"
        c = _cite(sdm, f"{apm}; Appendix A Tables A-1/A-2, A-6 (group 1)")
        add(Row(f"{name}-Eb-Gb", name, (base,), "b", modrm=True,
                operands=("Eb", "Gb"), e_access=acc, cite=c))
        add(Row(f"{name}-E-G", name, (base + 1,), "v", _V, modrm=True,
                operands=("E", "G"), e_access=acc, cite=c))
        add(Row(f"{name}-Gb-Eb", name, (base + 2,), "b", modrm=True,
                operands=("Gb", "Eb"), e_access="r", cite=c))
        add(Row(f"{name}-G-E", name, (base + 3,), "v", _V, modrm=True,
                operands=("G", "E"), e_access="r", cite=c))
        add(Row(f"{name}-AL-Ib", name, (base + 4,), "b",
                operands=("AL", "Ib"), imm="b", cite=c))
        add(Row(f"{name}-A-Iz", name, (base + 5,), "v", _V,
                operands=("A", "Iz"), imm="z", sext=True, cite=c))
        add(Row(f"{name}-80", name, (0x80,), "b", modrm=True, reg=digit,
                operands=("Eb", "Ib"), imm="b", e_access=acc, cite=c))
        add(Row(f"{name}-81", name, (0x81,), "v", _V, modrm=True, reg=digit,
                operands=("E", "Iz"), imm="z", sext=True, e_access=acc, cite=c))
        add(Row(f"{name}-83", name, (0x83,), "v", _V, modrm=True, reg=digit,
                operands=("E", "Ib"), imm="b", sext=True, e_access=acc, cite=c))

    c = _cite("Vol.2B §4.3 TEST p.4-721", "§3 TEST; Appendix A Tables A-1, A-2, A-6 (group 3)")
    add(Row("test-Eb-Gb", "test", (0x84,), "b", modrm=True, operands=("Eb", "Gb"), e_access="r", cite=c))
    add(Row("test-E-G", "test", (0x85,), "v", _V, modrm=True, operands=("E", "G"), e_access="r", cite=c))
    add(Row("test-AL-Ib", "test", (0xA8,), "b", operands=("AL", "Ib"), imm="b", cite=c))
    add(Row("test-A-Iz", "test", (0xA9,), "v", _V, operands=("A", "Iz"), imm="z", sext=True, cite=c))
    add(Row("test-F6", "test", (0xF6,), "b", modrm=True, reg=0, operands=("Eb", "Ib"), imm="b", e_access="r", cite=c))
    add(Row("test-F7", "test", (0xF7,), "v", _V, modrm=True, reg=0, operands=("E", "Iz"), imm="z", sext=True, e_access="r", cite=c))

    for name, digit, sdm in (("inc", 0, "Vol.2A §3.3 INC p.3-457"), ("dec", 1, "Vol.2A §3.3 DEC p.3-262")):
        c = _cite(sdm, f"§3 {name.upper()}; Appendix A Table A-6 (groups 4, 5)")
        add(Row(f"{name}-FE", name, (0xFE,), "b", modrm=True, reg=digit, operands=("Eb",), e_access="rw", cite=c))
        add(Row(f"{name}-FF", name, (0xFF,), "v", _V, modrm=True, reg=digit, operands=("E",), e_access="rw", cite=c))

    for name, digit, sdm in (("not", 2, "Vol.2B §4.3 NOT p.4-161"), ("neg", 3, "Vol.2B §4.3 NEG p.4-158")):
        c = _cite(sdm, f"§3 {name.upper()}; Appendix A Table A-6 (group 3)")
        add(Row(f"{name}-F6", name, (0xF6,), "b", modrm=True, reg=digit, operands=("Eb",), e_access="rw", cite=c))
        add(Row(f"{name}-F7", name, (0xF7,), "v", _V, modrm=True, reg=digit, operands=("E",), e_access="rw", cite=c))

    for name, digit in (("shl", 4), ("shr", 5), ("sar", 7)):
        c = _cite("Vol.2B §4.3 SAL/SAR/SHL/SHR p.4-603",
                  f"§3 {name.upper()}; Appendix A Table A-6 (group 2)")
        add(Row(f"{name}-C0", name, (0xC0,), "b", modrm=True, reg=digit, operands=("Eb", "Ib"), imm="b", e_access="rw", cite=c))
        add(Row(f"{name}-C1", name, (0xC1,), "v", _V, modrm=True, reg=digit, operands=("E", "Ib"), imm="b", e_access="rw", cite=c))
        add(Row(f"{name}-D0", name, (0xD0,), "b", modrm=True, reg=digit, operands=("Eb", "ONE"), e_access="rw", cite=c))
        add(Row(f"{name}-D1", name, (0xD1,), "v", _V, modrm=True, reg=digit, operands=("E", "ONE"), e_access="rw", cite=c))
        add(Row(f"{name}-D2", name, (0xD2,), "b", modrm=True, reg=digit, operands=("Eb", "CL"), e_access="rw", cite=c))
        add(Row(f"{name}-D3", name, (0xD3,), "v", _V, modrm=True, reg=digit, operands=("E", "CL"), e_access="rw", cite=c))

    c = _cite("Vol.2B §4.3 MOV p.4-28", "§3 MOV; Appendix A Tables A-1, A-2, A-6 (group 11)")
    add(Row("mov-Eb-Gb", "mov", (0x88,), "b", modrm=True, operands=("Eb", "Gb"), e_access="w", cite=c))
    add(Row("mov-E-G", "mov", (0x89,), "v", _V, modrm=True, operands=("E", "G"), e_access="w", cite=c))
    add(Row("mov-Gb-Eb", "mov", (0x8A,), "b", modrm=True, operands=("Gb", "Eb"), e_access="r", cite=c))
    add(Row("mov-G-E", "mov", (0x8B,), "v", _V, modrm=True, operands=("G", "E"), e_access="r", cite=c))
    add(Row("mov-Zb-Ib", "mov", (0xB0,), "b", plus_r=True, operands=("Zb", "Ib"), imm="b", cite=c))
    add(Row("mov-Z-Iv", "mov", (0xB8,), "v", _V, plus_r=True, operands=("Z", "Iv"), imm="v", cite=c))
    add(Row("mov-C6", "mov", (0xC6,), "b", modrm=True, reg=0, operands=("Eb", "Ib"), imm="b", e_access="w", cite=c))
    add(Row("mov-C7", "mov", (0xC7,), "v", _V, modrm=True, reg=0, operands=("E", "Iz"), imm="z", sext=True, e_access="w", cite=c))

    c = _cite("Vol.2B §4.3 MOVZX p.4-130", "§3 MOVZX; Appendix A Table A-4")
    add(Row("movzx-G-Eb", "movzx", (0x0F, 0xB6), "v", _V, modrm=True, operands=("G", "Eb"), e_access="r", cite=c))
    add(Row("movzx-G-Ew", "movzx", (0x0F, 0xB7), "v", (32, 64), modrm=True, operands=("G", "Ew"), e_access="r", cite=c))
    c = _cite("Vol.2B §4.3 MOVSX/MOVSXD p.4-120", "§3 MOVSX, MOVSXD; Appendix A Tables A-1, A-4")
    add(Row("movsx-G-Eb", "movsx", (0x0F, 0xBE), "v", _V, modrm=True, operands=("G", "Eb"), e_access="r", cite=c))
    add(Row("movsx-G-Ew", "movsx", (0x0F, 0xBF), "v", (32, 64), modrm=True, operands=("G", "Ew"), e_access="r", cite=c))
    add(Row("movsxd-G-Ed", "movsxd", (0x63,), "v", (64,), modrm=True, operands=("G", "Ed"), e_access="r", cite=c))

    c = _cite("Vol.2A §3.3 LEA p.3-547", "§3 LEA; Appendix A Table A-2")
    add(Row("lea", "lea", (0x8D,), "v", _V, modrm=True, mod="mem", operands=("G", "M"), cite=c))

    c = _cite("Vol.2A §3.3 CMOVcc p.3-157", "§3 CMOVcc; Appendix A Tables A-3, A-5")
    add(Row("cmovcc", "cmov{cc}", (0x0F, 0x40), "v", _V, modrm=True, plus_cc=True, operands=("G", "E"), e_access="r", cite=c))
    c = _cite("Vol.2B §4.3 SETcc p.4-623", "§3 SETcc; Appendix A Tables A-4, A-5")
    add(Row("setcc", "set{cc}", (0x0F, 0x90), "b", modrm=True, reg=0, plus_cc=True, operands=("Eb",), e_access="w", cite=c))

    c = _cite("Vol.2B §4.3 PUSH p.4-522", "§3 PUSH; Appendix A Tables A-1, A-2, A-6 (group 5)")
    add(Row("push-Z", "push", (0x50,), "d64", plus_r=True, operands=("Z",), stack=-8, implicit="push", cite=c))
    add(Row("push-FF", "push", (0xFF,), "d64", modrm=True, reg=6, operands=("E",), stack=-8, implicit="push", e_access="r", cite=c))
    add(Row("push-Ib", "push", (0x6A,), "d64", operands=("Ib",), imm="b", sext=True, stack=-8, implicit="push", cite=c))
    add(Row("push-Iz", "push", (0x68,), "d64", operands=("Iz",), imm="z", sext=True, stack=-8, implicit="push", cite=c))
    c = _cite("Vol.2B §4.3 POP p.4-398", "§3 POP; Appendix A Tables A-1, A-6 (group 1a)")
    add(Row("pop-Z", "pop", (0x58,), "d64", plus_r=True, operands=("Z",), stack=8, implicit="pop", cite=c))
    add(Row("pop-8F", "pop", (0x8F,), "d64", modrm=True, reg=0, operands=("E",), stack=8, implicit="pop", e_access="w", cite=c))

    c = _cite("Vol.2B §4.3 NOP p.4-160", "§3 NOP; Appendix A Tables A-2, A-7 (group P/0F 1F)")
    add(Row("nop-90", "nop", (0x90,), "none", cite=c))
    add(Row("nop-0F1F", "nop", (0x0F, 0x1F), "v", (16, 32), modrm=True, reg=0, operands=("E",), cite=c))

    add(Row("syscall", "syscall", (0x0F, 0x05), "none", ct="CT-6",
            cite=_cite("Vol.2B §4.3 SYSCALL p.4-699", "§3 SYSCALL; Appendix A Table A-3")))
    add(Row("ud2", "ud2", (0x0F, 0x0B), "none", ct="CT-7",
            cite=_cite("Vol.2B §4.3 UD p.4-737", "§3 UD2; Appendix A Table A-3")))

    c = _cite("Vol.2A §3.3 Jcc p.3-499", "§3 Jcc; Appendix A Tables A-1, A-4, A-5")
    add(Row("jcc-rel8", "j{cc}", (0x70,), "d64", plus_cc=True, operands=("J",), rel=1, ct="CT-2", cite=c))
    add(Row("jcc-rel32", "j{cc}", (0x0F, 0x80), "d64", plus_cc=True, operands=("J",), rel=4, ct="CT-2", cite=c))
    c = _cite("Vol.2A §3.3 JMP p.3-504", "§3 JMP (Near); Appendix A Table A-2")
    add(Row("jmp-rel8", "jmp", (0xEB,), "d64", operands=("J",), rel=1, ct="CT-3", cite=c))
    add(Row("jmp-rel32", "jmp", (0xE9,), "d64", operands=("J",), rel=4, ct="CT-3", cite=c))
    return tuple(rows)


TABLE: tuple[Row, ...] = _rows()

#: The prefix bytes XD knows by name, so a rejection can say which one it saw.
LEGACY_PREFIXES = {
    0x66: "operand-size", 0x67: "address-size", 0xF0: "lock",
    0xF2: "repne", 0xF3: "rep", 0x2E: "cs", 0x36: "ss", 0x3E: "ds",
    0x26: "es", 0x64: "fs", 0x65: "gs",
}
#: Escapes that begin VEX, EVEX or XOP instructions in 64-bit mode
#: (SDM §2.3, §2.7; APM §1.9). None is in the table.
VEX_ESCAPES = {0xC4: "VEX3", 0xC5: "VEX2", 0x62: "EVEX"}


def _size_keys(row: Row) -> list[str]:
    """The operand-size encodings a row accepts, as keys for the overlap check."""
    if row.osz == "v":
        keys = []
        if 16 in row.sizes:
            keys.append("66")
        if 32 in row.sizes:
            keys.append("-")
        if 64 in row.sizes:
            keys.append("W")
        return keys
    return ["-"]


def check_unambiguous(rows: tuple[Row, ...]) -> None:
    """Fail to load if two rows can match one byte pattern (XD-5 a).

    Every row is expanded to concrete keys — opcode bytes, operand-size
    encoding, ModRM.reg value and ModRM class (register or memory) — and no key
    may belong to two rows.
    """
    seen: dict[tuple, str] = {}
    for row in rows:
        regs = [row.reg] if row.reg is not None else list(range(8))
        if not row.modrm:
            regs = [None]
        mods = {"any": ["reg", "mem"], "reg": ["reg"], "mem": ["mem"]}[row.mod]
        if not row.modrm:
            mods = [None]
        for op in row.opcode_set():
            for sk in _size_keys(row):
                for r in regs:
                    for m in mods:
                        key = (op, sk, r, m)
                        if key in seen:
                            raise AmbiguousTable(
                                f"rows {seen[key]} and {row.id} both match "
                                f"opcode {bytes(op).hex()} size {sk} reg {r} mod {m}"
                            )
                        seen[key] = row.id


check_unambiguous(TABLE)


def table_digest(rows: tuple[Row, ...] = TABLE) -> str:
    """SHA-256 of the table's canonical serialisation (recorded with verdicts)."""
    payload = json.dumps(
        [row.__dict__ for row in rows], sort_keys=True, separators=(",", ":")
    ).encode()
    return hashlib.sha256(payload).hexdigest()


# ---------------------------------------------------------------------------
# Registers
# ---------------------------------------------------------------------------

_R64 = ("rax", "rcx", "rdx", "rbx", "rsp", "rbp", "rsi", "rdi",
        "r8", "r9", "r10", "r11", "r12", "r13", "r14", "r15")
_R32 = ("eax", "ecx", "edx", "ebx", "esp", "ebp", "esi", "edi",
        "r8d", "r9d", "r10d", "r11d", "r12d", "r13d", "r14d", "r15d")
_R16 = ("ax", "cx", "dx", "bx", "sp", "bp", "si", "di",
        "r8w", "r9w", "r10w", "r11w", "r12w", "r13w", "r14w", "r15w")
_R8_REX = ("al", "cl", "dl", "bl", "spl", "bpl", "sil", "dil",
           "r8b", "r9b", "r10b", "r11b", "r12b", "r13b", "r14b", "r15b")
_R8_LEGACY = ("al", "cl", "dl", "bl", "ah", "ch", "dh", "bh")


def reg_name(num: int, width: int, rex: bool) -> str:
    """SDM §2.1.5 Table 2-2 and §2.2.1.2; APM §1.8.1 (byte registers)."""
    if width == 64:
        return _R64[num]
    if width == 32:
        return _R32[num]
    if width == 16:
        return _R16[num]
    if rex:
        return _R8_REX[num]
    return _R8_LEGACY[num]


# ---------------------------------------------------------------------------
# Decoded instructions
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Operand:
    kind: str                       # "reg", "mem", "imm", "rel", "one"
    width: int = 0
    reg: str = ""
    base: str = ""
    index: str = ""
    scale: int = 1
    disp: int = 0
    disp_size: int = 0
    rip: bool = False
    value: int = 0                  # imm: raw encoded unsigned value
    size: int = 0                   # imm/rel: encoded byte count
    target: int = 0                 # rel: absolute target

    def canonical(self) -> str:
        if self.kind == "reg":
            return self.reg
        if self.kind == "one":
            return "1"
        if self.kind == "imm":
            return f"i{self.size * 8}:0x{self.value:x}"
        if self.kind == "rel":
            return f"rel{self.size * 8}:0x{self.target:x}"
        parts = []
        if self.rip:
            parts.append("rip")
        if self.base:
            parts.append(self.base)
        if self.index:
            parts.append(f"{self.index}*{self.scale}")
        expr = "+".join(parts)
        if self.disp_size:
            sign = "-" if self.disp < 0 else "+"
            expr += f"{sign}0x{abs(self.disp):x}" if expr else f"0x{self.disp & 0xFFFFFFFF:x}"
        return f"m{self.width}[{expr}]"

    def as_dict(self) -> dict:
        d = {"kind": self.kind}
        for k in ("width", "reg", "base", "index", "scale", "disp", "disp_size",
                  "rip", "value", "size", "target"):
            d[k] = getattr(self, k)
        return d


@dataclass(frozen=True)
class Instruction:
    address: int
    raw: bytes
    row: str
    mnemonic: str
    operands: tuple[Operand, ...]
    ct: str
    stack: int
    mem_read: bool
    mem_write: bool
    target: int | None
    width: int                      # operand size in bits (0 if none)
    rex: int | None

    @property
    def length(self) -> int:
        return len(self.raw)

    @property
    def end(self) -> int:
        return self.address + len(self.raw)

    def canonical(self) -> str:
        ops = ", ".join(op.canonical() for op in self.operands)
        return f"{self.mnemonic} {ops}" if ops else self.mnemonic

    def as_dict(self) -> dict:
        return {
            "address": self.address,
            "length": self.length,
            "bytes": self.raw.hex(),
            "row": self.row,
            "mnemonic": self.mnemonic,
            "operands": [op.as_dict() for op in self.operands],
            "canonical": self.canonical(),
            "transfer_class": self.ct,
            "target": self.target,
            "stack_effect": self.stack,
            "mem_read": self.mem_read,
            "mem_write": self.mem_write,
        }


class DecodeError(Exception):
    def __init__(self, klass: str, detail: str):
        super().__init__(detail)
        self.klass = klass
        self.detail = detail


MAX_LENGTH = 15  # SDM §2.2.1 (15-byte limit); APM §1.1


def _signed(value: int, size: int) -> int:
    bits = size * 8
    return value - (1 << bits) if value & (1 << (bits - 1)) else value


def decode_one(code: bytes, offset: int, address: int,
               table: tuple[Row, ...] = TABLE) -> Instruction:
    """Decode one instruction at `offset` of `code`, which is at `address`.

    Raises `DecodeError` with class (a) ambiguity, (b) unsupported encoding or
    (c) undecoded byte (the bytes run out).
    """
    end = len(code)
    pos = offset

    def need(n: int) -> bytes:
        nonlocal pos
        if pos + n > end:
            raise DecodeError(UNDECODED, f"instruction at 0x{address:x} runs past the end of .text")
        chunk = code[pos:pos + n]
        pos += n
        return chunk

    # Legacy prefixes: only a single 66 is permitted, and only on rows that list it.
    opsize = False
    while pos < end and code[pos] in LEGACY_PREFIXES:
        b = code[pos]
        if b != 0x66:
            raise DecodeError(UNSUPPORTED, f"{LEGACY_PREFIXES[b]} prefix {b:02x} at 0x{address:x}")
        if opsize:
            raise DecodeError(UNSUPPORTED, f"repeated 66 prefix at 0x{address:x}")
        opsize = True
        pos += 1
    if pos >= end:
        raise DecodeError(UNDECODED, f"prefix at 0x{address:x} runs past the end of .text")

    rex = None
    if 0x40 <= code[pos] <= 0x4F:
        rex = code[pos]
        pos += 1
        if pos >= end:
            raise DecodeError(UNDECODED, f"REX at 0x{address:x} runs past the end of .text")
        nxt = code[pos]
        if 0x40 <= nxt <= 0x4F or nxt in LEGACY_PREFIXES:
            raise DecodeError(UNSUPPORTED, f"REX at 0x{address:x} does not immediately precede the opcode")
    if code[pos] in VEX_ESCAPES:
        raise DecodeError(UNSUPPORTED, f"{VEX_ESCAPES[code[pos]]} escape {code[pos]:02x} at 0x{address:x}")
    rex_w = bool(rex is not None and rex & 0x8)
    rex_r = 8 if rex is not None and rex & 0x4 else 0
    rex_x = 8 if rex is not None and rex & 0x2 else 0
    rex_b = 8 if rex is not None and rex & 0x1 else 0

    op1 = code[pos]
    two = op1 == 0x0F
    if two:
        if pos + 1 >= end:
            raise DecodeError(UNDECODED, f"escape at 0x{address:x} runs past the end of .text")
        opcode = (0x0F, code[pos + 1])
    else:
        opcode = (op1,)
    after_opcode = pos + len(opcode)
    modrm_byte = code[after_opcode] if after_opcode < end else None

    matches: list[tuple[Row, int]] = []
    for row in table:
        if opcode not in row.opcode_set():
            continue
        width = _row_width(row, opsize, rex, rex_w)
        if width is None:
            continue
        if row.modrm:
            if modrm_byte is None:
                continue
            mod = modrm_byte >> 6
            reg = (modrm_byte >> 3) & 7
            if row.reg is not None and reg != row.reg:
                continue
            if row.mod == "reg" and mod != 3:
                continue
            if row.mod == "mem" and mod == 3:
                continue
        matches.append((row, width))
    if len(matches) > 1:
        raise DecodeError(AMBIGUOUS, f"{len(matches)} rows match at 0x{address:x}: "
                          + ", ".join(r.id for r, _ in matches))
    if not matches:
        if modrm_byte is None and any(opcode in r.opcode_set() and r.modrm for r in table):
            raise DecodeError(UNDECODED, f"ModR/M at 0x{address:x} runs past the end of .text")
        raise DecodeError(UNSUPPORTED, "no table row matches "
                          f"{code[offset:min(end, offset + 4)].hex()} at 0x{address:x}")
    row, width = matches[0]
    pos = after_opcode

    cc = opcode[-1] & 0xF if row.plus_cc else None
    mnemonic = row.mnemonic.replace("{cc}", CONDITION_CODES[cc]) if cc is not None else row.mnemonic

    modrm = None
    mem: Operand | None = None
    e_reg = None
    if row.modrm:
        modrm = need(1)[0]
        mod, reg_field, rm = modrm >> 6, (modrm >> 3) & 7, modrm & 7
        if mod == 3:
            e_reg = rm | rex_b
        else:
            mem = _decode_memory(code, need, mod, rm, rex_x, rex_b, address)

    operands: list[Operand] = []
    imm_op = None
    for spec in row.operands:
        if spec in ("E", "Eb", "Ew", "Ed", "M"):
            w = {"E": width, "Eb": 8, "Ew": 16, "Ed": 32, "M": width}[spec]
            if e_reg is not None:
                operands.append(Operand("reg", w, reg=reg_name(e_reg, w, rex is not None)))
            else:
                assert mem is not None
                operands.append(Operand("mem", 0 if spec == "M" else w, base=mem.base, index=mem.index,
                                        scale=mem.scale, disp=mem.disp, disp_size=mem.disp_size, rip=mem.rip))
        elif spec in ("G", "Gb"):
            w = width if spec == "G" else 8
            operands.append(Operand("reg", w, reg=reg_name(((modrm >> 3) & 7) | rex_r, w, rex is not None)))
        elif spec in ("Z", "Zb"):
            w = width if spec == "Z" else 8
            operands.append(Operand("reg", w, reg=reg_name((opcode[-1] & 7) | rex_b, w, rex is not None)))
        elif spec == "A":
            operands.append(Operand("reg", width, reg=reg_name(0, width, rex is not None)))
        elif spec == "AL":
            operands.append(Operand("reg", 8, reg="al"))
        elif spec == "CL":
            operands.append(Operand("reg", 8, reg="cl"))
        elif spec == "ONE":
            operands.append(Operand("one"))
        elif spec in ("Ib", "Iz", "Iv"):
            n = {"Ib": 1, "Iz": 2 if width == 16 else 4, "Iv": width // 8}[spec]
            imm_op = Operand("imm", width, value=int.from_bytes(need(n), "little"), size=n)
            operands.append(imm_op)
        elif spec == "J":
            disp = _signed(int.from_bytes(need(row.rel), "little"), row.rel)
            # The target is relative to the next instruction (SDM Jcc/JMP).
            operands.append(Operand("rel", 64, size=row.rel, disp=disp))
        else:  # pragma: no cover - the table is closed
            raise AssertionError(spec)

    length = pos - offset
    if length > MAX_LENGTH:
        raise DecodeError(UNSUPPORTED, f"instruction at 0x{address:x} is longer than 15 bytes")
    target = None
    final_ops = []
    for op in operands:
        if op.kind == "rel":
            target = (address + length + op.disp) & 0xFFFFFFFFFFFFFFFF
            op = Operand("rel", 64, size=op.size, disp=op.disp, target=target)
        final_ops.append(op)

    mem_read = mem_write = False
    if mem is not None and row.e_access:
        mem_read = "r" in row.e_access
        mem_write = "w" in row.e_access
    if row.implicit == "push":
        mem_write = True
    if row.implicit == "pop":
        mem_read = True

    return Instruction(
        address=address, raw=bytes(code[offset:pos]), row=row.id, mnemonic=mnemonic,
        operands=tuple(final_ops), ct=row.ct, stack=row.stack, mem_read=mem_read,
        mem_write=mem_write, target=target, width=width, rex=rex,
    )


def _row_width(row: Row, opsize: bool, rex: int | None, rex_w: bool) -> int | None:
    """The operand size the prefixes select for this row, or None if they do
    not fit it. SDM §2.2.1.2 Table 2-4, §2.2.1.7; APM §1.2.2, §1.2.7."""
    if row.osz == "none":
        return 0 if (not opsize and rex is None) else None
    if row.osz == "b":
        return 8 if (not opsize and not rex_w) else None
    if row.osz == "d64":
        if opsize or rex_w:
            return None
        if rex is not None and not _row_uses_register_extension(row):
            return None
        return 64
    if opsize and rex_w:
        return None
    width = 64 if rex_w else 16 if opsize else 32
    return width if width in row.sizes else None


def _row_uses_register_extension(row: Row) -> bool:
    return any(s in ("E", "G", "Z", "Gb", "Eb", "Zb") for s in row.operands)


def _decode_memory(code, need, mod, rm, rex_x, rex_b, address) -> Operand:
    """ModR/M + SIB memory form, 64-bit addressing.

    SDM §2.1.5 Tables 2-2/2-3, §2.2.1.2 Table 2-5, §2.2.1.6 Table 2-7;
    APM §1.4.1, §1.4.2, §1.4.4, §1.7.
    """
    base = index = ""
    scale = 1
    rip = False
    disp_size = {0: 0, 1: 1, 2: 4}[mod]
    if rm == 4:
        sib = need(1)[0]
        ss, idx, bas = sib >> 6, (sib >> 3) & 7, sib & 7
        scale = 1 << ss
        idx_full = idx | rex_x
        if idx_full != 4:
            index = _R64[idx_full]
        if bas == 5 and mod == 0:
            disp_size = 4
        else:
            base = _R64[bas | rex_b]
    elif rm == 5 and mod == 0:
        rip = True
        disp_size = 4
    else:
        base = _R64[rm | rex_b]
    disp = 0
    if disp_size:
        disp = _signed(int.from_bytes(need(disp_size), "little"), disp_size)
    return Operand("mem", 0, base=base, index=index, scale=scale, disp=disp,
                   disp_size=disp_size, rip=rip)


# ---------------------------------------------------------------------------
# Whole-.text decoding (XD-2, XD-5)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Function:
    name: str
    start: int
    size: int

    @property
    def end(self) -> int:
        return self.start + self.size


@dataclass
class TextDecode:
    stream: list[Instruction] = field(default_factory=list)
    failures: list[Failure] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.failures


CONTRACT_FUNCTIONS = ("_start", "rp11_main")


def decode_text(code: bytes, text_addr: int, functions: tuple[Function, ...],
                entry: int, other_ranges: tuple[tuple[str, int, int], ...] = (),
                table: tuple[Row, ...] = TABLE) -> TextDecode:
    """Decode `.text` by linear sweep, then check it by reachability.

    `functions` is the contract function set in address order; `other_ranges`
    names non-text ranges (for example `.rodata`) only so that a target into
    one can be reported by name.
    """
    out = TextDecode()
    fail = out.failures.append
    text_end = text_addr + len(code)

    # Linear sweep (XD-2): every byte belongs to exactly one instruction.
    offset = 0
    while offset < len(code):
        addr = text_addr + offset
        try:
            ins = decode_one(code, offset, addr, table)
        except DecodeError as exc:
            fail(Failure(exc.klass, addr, exc.detail))
            return out
        out.stream.append(ins)
        offset += ins.length
    boundaries = {ins.address: ins for ins in out.stream}

    def function_of(addr: int) -> Function | None:
        for fn in functions:
            if fn.start <= addr < fn.end:
                return fn
        return None

    # Targets (XD-5 e): an instruction start, in the same function, inside
    # .text — except the single CT-4 entry jump, which must land on
    # rp11_main's first instruction.
    main = next((f for f in functions if f.name == "rp11_main"), None)
    start_fn = next((f for f in functions if f.name == "_start"), None)
    entry_jumps = 0
    reclassified: list[Instruction] = []
    for ins in out.stream:
        if ins.target is None:
            reclassified.append(ins)
            continue
        t = ins.target
        src_fn = function_of(ins.address)
        if not (text_addr <= t < text_end):
            named = next((n for n, lo, hi in other_ranges if lo <= t < hi), "outside .text")
            fail(Failure(BAD_TARGET, ins.address, f"target 0x{t:x} is in {named}"))
            reclassified.append(ins)
            continue
        if t not in boundaries:
            fail(Failure(BAD_TARGET, ins.address, f"target 0x{t:x} is inside an instruction"))
            reclassified.append(ins)
            continue
        dst_fn = function_of(t)
        is_entry = (
            ins.mnemonic == "jmp" and src_fn is start_fn and start_fn is not None
            and main is not None and t == main.start
            and ins is out.stream[_last_index_in(out.stream, start_fn)]
        )
        if is_entry:
            entry_jumps += 1
            ins = Instruction(**{**ins.__dict__, "ct": "CT-4"})
        elif dst_fn is not src_fn:
            fail(Failure(BAD_TARGET, ins.address,
                         f"target 0x{t:x} leaves {src_fn.name if src_fn else '?'}"))
        reclassified.append(ins)
    out.stream = reclassified
    boundaries = {ins.address: ins for ins in out.stream}
    if start_fn is not None and main is not None and entry_jumps != 1:
        fail(Failure(BAD_TARGET, None, f"{entry_jumps} CT-4 entry jumps; exactly one is required"))

    # Reachability (XD-2, XD-5 d, f): decode afresh from every reached
    # position rather than reusing the sweep, so a position the sweep did not
    # produce is detected as an overlap.
    reached: set[int] = set()
    work = [entry]
    while work:
        addr = work.pop()
        if addr in reached:
            continue
        if not (text_addr <= addr < text_end):
            continue
        if addr not in boundaries:
            fail(Failure(OVERLAP, addr, f"reachability reaches 0x{addr:x}, which is not a sweep boundary"))
            continue
        reached.add(addr)
        try:
            ins = decode_one(code, addr - text_addr, addr, table)
        except DecodeError as exc:  # cannot differ from the sweep, but fail closed
            fail(Failure(exc.klass, addr, exc.detail))
            continue
        if ins.raw != boundaries[addr].raw:
            fail(Failure(OVERLAP, addr, "reachability decoded a different instruction"))
            continue
        if ins.mnemonic == "ud2":
            continue
        if ins.target is not None:
            work.append(ins.target)
            if ins.mnemonic == "jmp":
                continue
        work.append(ins.end)
    for ins in out.stream:
        if ins.address not in reached:
            fail(Failure(UNREACHED, ins.address, f"{ins.canonical()} is never reached from _start"))
    return out


def _last_index_in(stream: list[Instruction], fn: Function) -> int:
    idx = -1
    for i, ins in enumerate(stream):
        if fn.start <= ins.address < fn.end:
            idx = i
    return idx


# ---------------------------------------------------------------------------
# The ELF reader (XD-1). Its own; it shares no code with T-L7 or T-L10.
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ImageFacts:
    entry: int
    text_addr: int
    text_offset: int
    text_size: int
    rodata: tuple[int, int] | None
    functions: tuple[Function, ...]
    text: bytes

    def as_dict(self) -> dict:
        return {
            "e_entry": self.entry,
            "text_addr": self.text_addr,
            "text_offset": self.text_offset,
            "text_size": self.text_size,
            "rodata": list(self.rodata) if self.rodata else None,
            "functions": [[f.name, f.start, f.size] for f in self.functions],
        }


class ImageError(Exception):
    pass


def read_image(data: bytes) -> ImageFacts:
    if len(data) < 64 or data[:4] != b"\x7fELF":
        raise ImageError("not an ELF file")
    if data[4] != 2 or data[5] != 1:
        raise ImageError("not ELFCLASS64 / ELFDATA2LSB")
    (e_type, e_machine, _ver, e_entry, _phoff, e_shoff, _flags, _ehsize,
     _phentsize, _phnum, e_shentsize, e_shnum, e_shstrndx) = struct.unpack_from(
        "<HHIQQQIHHHHHH", data, 16)
    if e_machine != 62:
        raise ImageError("e_machine is not EM_X86_64")
    if e_shentsize != 64 or e_shnum == 0:
        raise ImageError("no usable section header table")
    sections = []
    for i in range(e_shnum):
        sh = struct.unpack_from("<IIQQQQIIQQ", data, e_shoff + i * 64)
        sections.append(sh)
    shstr = sections[e_shstrndx]

    def cstr(table_off: int, idx: int) -> str:
        endpos = data.index(b"\x00", table_off + idx)
        return data[table_off + idx:endpos].decode("ascii")

    named = {}
    for sh in sections:
        named[cstr(shstr[4], sh[0])] = sh
    if ".text" not in named:
        raise ImageError("no .text section")
    text = named[".text"]
    text_addr, text_off, text_size = text[3], text[4], text[5]
    rodata = None
    if ".rodata" in named:
        r = named[".rodata"]
        rodata = (r[3], r[3] + r[5])
    if ".symtab" not in named:
        raise ImageError("no .symtab section")
    symtab = named[".symtab"]
    strtab = sections[symtab[6]]
    funcs = []
    others = []
    for off in range(symtab[4], symtab[4] + symtab[5], 24):
        st_name, st_info, _other, st_shndx, st_value, st_size = struct.unpack_from("<IBBHQQ", data, off)
        styp = st_info & 0xF
        if st_name == 0 and styp == 0:
            continue
        name = cstr(strtab[4], st_name)
        if styp in (3, 4):  # STT_SECTION, STT_FILE
            continue
        if styp == 2:
            funcs.append(Function(name, st_value, st_size))
        else:
            others.append(name)
    if others:
        raise ImageError(f"non-function symbols present: {sorted(others)}")
    if e_type != 2:
        raise ImageError("e_type is not ET_EXEC")
    funcs.sort(key=lambda f: f.start)
    return ImageFacts(
        entry=e_entry, text_addr=text_addr, text_offset=text_off, text_size=text_size,
        rodata=rodata, functions=tuple(funcs),
        text=bytes(data[text_off:text_off + text_size]),
    )


def structural_failures(facts: ImageFacts) -> list[Failure]:
    """RI-1 and the tiling half of RI-2, as XD reads them from the image."""
    out = []
    names = tuple(f.name for f in facts.functions)
    if names != CONTRACT_FUNCTIONS:
        out.append(Failure(STRUCTURE, None, f"function set {names} is not {CONTRACT_FUNCTIONS}"))
        return out
    start, main = facts.functions
    if not (start.start == facts.entry == facts.text_addr):
        out.append(Failure(STRUCTURE, start.start, "_start, e_entry and .text start differ"))
    if start.end != main.start or main.end != facts.text_addr + facts.text_size:
        out.append(Failure(STRUCTURE, main.start, "_start and rp11_main do not tile .text"))
    return out


def decode_image(data: bytes) -> tuple[ImageFacts, TextDecode]:
    facts = read_image(data)
    result = TextDecode()
    result.failures.extend(structural_failures(facts))
    if result.failures:
        return facts, result
    others = (("the .rodata section", *facts.rodata),) if facts.rodata else ()
    result = decode_text(facts.text, facts.text_addr, facts.functions, facts.entry, others)
    return facts, result


# ---------------------------------------------------------------------------
# The spelling table and rendering into the listing's spelling (XD-6)
# ---------------------------------------------------------------------------


class SpellingError(Exception):
    pass


@dataclass(frozen=True)
class Spelling:
    registers: dict[str, str]
    mnemonics: dict[str, tuple[str, str]]     # canonical -> (spelling, suffix policy)
    suffixes: dict[int, str]
    forms: dict[tuple[str, int], str]         # (row id, operand size) -> spelling
    target_format: str

    @classmethod
    def load(cls, text: str) -> "Spelling":
        regs: dict[str, str] = {}
        mnems: dict[str, tuple[str, str]] = {}
        sufs: dict[int, str] = {}
        forms: dict[tuple[str, int], str] = {}
        target_format = ""
        lines = text.splitlines()
        if not lines or lines[0].strip() != "rp11-xdecode-spelling/1":
            raise SpellingError("missing format line rp11-xdecode-spelling/1")
        for n, line in enumerate(lines[1:], 2):
            line = line.split("#", 1)[0].strip()
            if not line:
                continue
            parts = line.split()
            kind = parts[0]
            if kind == "reg" and len(parts) == 3:
                if parts[1] in regs:
                    raise SpellingError(f"line {n}: register {parts[1]} spelled twice")
                regs[parts[1]] = parts[2]
            elif kind == "mnem" and len(parts) == 4:
                if parts[1] in mnems:
                    raise SpellingError(f"line {n}: mnemonic {parts[1]} spelled twice")
                if parts[3] not in ("ambiguous", "never", "ext"):
                    raise SpellingError(f"line {n}: unknown suffix policy {parts[3]}")
                mnems[parts[1]] = (parts[2], parts[3])
            elif kind == "form" and len(parts) == 3:
                row_id, _, width = parts[1].partition("/")
                if row_id not in {r.id for r in TABLE}:
                    raise SpellingError(f"line {n}: form names unknown row {row_id}")
                forms[(row_id, int(width))] = parts[2]
            elif kind == "suffix" and len(parts) == 3:
                sufs[int(parts[1])] = parts[2]
            elif kind == "target" and len(parts) >= 2:
                target_format = line.split(None, 1)[1]
            else:
                raise SpellingError(f"line {n}: unrecognised entry {line!r}")
        sp = cls(regs, mnems, sufs, forms, target_format)
        sp._check_injective()
        return sp

    def _check_injective(self) -> None:
        """XD-6: two different decodings must not print alike."""
        if len(set(self.registers.values())) != len(self.registers):
            raise SpellingError("register spelling is not injective")
        if len(set(self.suffixes.values())) != len(self.suffixes):
            raise SpellingError("size suffixes are not injective")
        produced: dict[str, str] = {}
        for canon, (spelling, policy) in self.mnemonics.items():
            forms = [spelling]
            if policy == "ambiguous":
                forms += [spelling + s for s in self.suffixes.values()]
            if policy == "ext":
                # The extension rows take only a byte or word source (XD table).
                forms = [spelling + self.suffixes[a] + self.suffixes[b]
                         for a in (8, 16) for b in self.suffixes]
            for form in forms:
                if form in produced and produced[form] != canon:
                    raise SpellingError(f"{form!r} would spell both {produced[form]} and {canon}")
                produced[form] = canon
        for (row_id, width), form in self.forms.items():
            if form in produced:
                raise SpellingError(f"form spelling {form!r} for {row_id}/{width} is not distinct")
            produced[form] = f"{row_id}/{width}"
        missing = {r.mnemonic.replace("{cc}", cc) for r in TABLE for cc in
                   (CONDITION_CODES if "{cc}" in r.mnemonic else ("",))} - set(self.mnemonics)
        if missing:
            raise SpellingError(f"no spelling for {sorted(missing)}")
        for regs in (_R64, _R32, _R16, _R8_REX, _R8_LEGACY):
            for r in regs:
                if r not in self.registers:
                    raise SpellingError(f"no spelling for register {r}")


def _hex(value: int) -> str:
    return f"0x{value:x}"


def render(ins: Instruction, sp: Spelling, functions: tuple[Function, ...]) -> str:
    """The instruction in the listing's AT&T spelling: mnemonic, a space, the
    operands in source-then-destination order, comma-separated."""
    spelling, policy = sp.mnemonics[ins.mnemonic]
    if (ins.row, ins.width) in sp.forms:
        spelling, policy = sp.forms[(ins.row, ins.width)], "never"
    ops = [o for o in ins.operands]
    has_reg = any(o.kind == "reg" for o in ops)
    mnem = spelling
    if policy == "ambiguous" and not has_reg and ins.width and any(o.kind in ("mem", "imm") for o in ops):
        mnem = spelling + sp.suffixes[ins.width]
    elif policy == "ext":
        src = ops[1]
        mnem = spelling + sp.suffixes[src.width] + sp.suffixes[ops[0].width]

    rendered = []
    for o in reversed(ops):
        rendered.append(_render_operand(o, ins, sp, functions))
    text = mnem
    if rendered:
        text += " " + ",".join(rendered)
    return text


def _render_operand(o: Operand, ins: Instruction, sp: Spelling, functions) -> str:
    if o.kind == "reg":
        return sp.registers[o.reg]
    if o.kind == "one":
        return "$0x1"
    if o.kind == "imm":
        value = o.value
        bits = o.size * 8
        if ins.row in _SEXT_ROWS and value & (1 << (bits - 1)):
            width = 64 if ins.mnemonic == "push" else ins.width
            value = (value - (1 << bits)) & ((1 << width) - 1)
        return "$" + _hex(value)
    if o.kind == "rel":
        return _render_target(o.target, sp, functions)
    # memory
    inner = ""
    if o.rip:
        inner = "(%rip)"
    elif o.base or o.index:
        inner = "("
        if o.base:
            inner += sp.registers[o.base]
        if o.index:
            inner += f",{sp.registers[o.index]},{o.scale}"
        inner += ")"
    if o.disp_size:
        d = o.disp
        if not o.base and not o.index and not o.rip:
            disp = _hex(d & 0xFFFFFFFF)
        else:
            disp = ("-" + _hex(-d)) if d < 0 else _hex(d)
        return disp + inner
    return inner


_SEXT_ROWS = {r.id for r in TABLE if r.sext}


def _render_target(t: int, sp: Spelling, functions) -> str:
    fn = next((f for f in functions if f.start <= t < f.end), None)
    label = "" if fn is None else (f"<{fn.name}>" if t == fn.start else f"<{fn.name}+0x{t - fn.start:x}>")
    return sp.target_format.replace("{addr}", f"{t:x}").replace("{label}", label)


# ---------------------------------------------------------------------------
# The listing's disassembly, parsed by a fixed grammar (XD-6)
# ---------------------------------------------------------------------------

_FUNC_LINE = re.compile(r"^([0-9a-f]{16}) <([^>]+)>:$")
_INSN_LINE = re.compile(r"^ +([0-9a-f]+):\t((?:[0-9a-f]{2} )+)\s*\t?(.*)$")


@dataclass(frozen=True)
class ListedInstruction:
    address: int
    raw: bytes
    text: str


def parse_listing(listing: str) -> tuple[list[tuple[str, int]], list[ListedInstruction]]:
    """The disassembly section of the committed listing: function-start lines
    and instruction lines. Any other line inside the section is an error."""
    lines = listing.splitlines()
    try:
        start = lines.index("Disassembly of section .text:")
    except ValueError as exc:
        raise SpellingError("listing has no '.text' disassembly section") from exc
    funcs: list[tuple[str, int]] = []
    insns: list[ListedInstruction] = []
    for line in lines[start + 1:]:
        if line.startswith("== "):
            break
        if not line.strip():
            continue
        m = _FUNC_LINE.match(line)
        if m:
            funcs.append((m.group(2), int(m.group(1), 16)))
            continue
        m = _INSN_LINE.match(line)
        if not m:
            raise SpellingError(f"unparseable disassembly line {line!r}")
        raw = bytes.fromhex(m.group(2).replace(" ", ""))
        text = " ".join(m.group(3).split())
        insns.append(ListedInstruction(int(m.group(1), 16), raw, text))
    return funcs, insns


def agree(result: TextDecode, facts: ImageFacts, listing: str, sp: Spelling) -> list[Failure]:
    """XD-6: exact agreement, instruction for instruction and in count."""
    out = []
    funcs, listed = parse_listing(listing)
    want_funcs = [(f.name, f.start) for f in facts.functions]
    if funcs != want_funcs:
        out.append(Failure(DISAGREEMENT, None, f"listing functions {funcs} != image {want_funcs}"))
    if len(listed) != len(result.stream):
        out.append(Failure(DISAGREEMENT, None,
                           f"listing has {len(listed)} instructions, XD decoded {len(result.stream)}"))
    for ins, lst in zip(result.stream, listed):
        if ins.address != lst.address:
            out.append(Failure(DISAGREEMENT, ins.address, f"boundary: listing 0x{lst.address:x}"))
            break
        if ins.raw != lst.raw:
            out.append(Failure(DISAGREEMENT, ins.address,
                               f"bytes/length: XD {ins.raw.hex()} listing {lst.raw.hex()}"))
            continue
        mine = " ".join(render(ins, sp, facts.functions).split())
        if mine != lst.text:
            out.append(Failure(DISAGREEMENT, ins.address, f"text: XD {mine!r} listing {lst.text!r}"))
        if ins.target is not None:
            m = re.match(r"^\S+ ([0-9a-f]+) <", lst.text)
            if not m or int(m.group(1), 16) != ins.target:
                out.append(Failure(DISAGREEMENT, ins.address, "direct target differs"))
    return out


def rendered_stream(result: TextDecode, facts: ImageFacts, sp: Spelling) -> list[dict]:
    """XD's stream in the listing's spelling, for T-L10 (XD-7)."""
    return [
        {"address": ins.address, "bytes": ins.raw.hex(), "text": " ".join(render(ins, sp, facts.functions).split())}
        for ins in result.stream
    ]


def stream_digest(result: TextDecode) -> str:
    payload = "".join(
        json.dumps(ins.as_dict(), sort_keys=True, separators=(",", ":")) + "\n"
        for ins in result.stream
    ).encode()
    return hashlib.sha256(payload).hexdigest()


# ---------------------------------------------------------------------------
# Verdict (XD-8)
# ---------------------------------------------------------------------------

HERE = Path(__file__).resolve().parent
SPELLING_PATH = HERE / "xdecode-spelling.table"


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def run(image: bytes, listing: bytes | None, spelling: bytes) -> dict:
    """Decode an image, compare with a listing if given, and return the
    deterministic verdict record with every digest XD-8 requires."""
    sp = Spelling.load(spelling.decode("utf-8"))
    failures: list[Failure] = []
    try:
        facts, result = decode_image(image)
    except ImageError as exc:
        return _verdict(image, listing, spelling, None, None, [Failure(STRUCTURE, None, str(exc))])
    failures.extend(result.failures)
    if listing is not None and not result.failures:
        failures.extend(agree(result, facts, listing.decode("utf-8"), sp))
    return _verdict(image, listing, spelling, facts, result, failures)


def _verdict(image, listing, spelling, facts, result, failures) -> dict:
    return {
        "xd_version": XD_VERSION,
        "xdecode_py_sha256": _sha(Path(__file__).read_bytes()),
        "spelling_table_sha256": _sha(spelling),
        "table_sha256": table_digest(),
        "interpreter": sys.version.split()[0],
        "image_sha256": _sha(image),
        "listing_sha256": _sha(listing) if listing is not None else None,
        "image": facts.as_dict() if facts else None,
        "instructions": len(result.stream) if result else 0,
        "stream_sha256": stream_digest(result) if result else None,
        "failures": [f.as_dict() for f in failures],
        "verdict": "pass" if not failures else "fail",
    }


def main(argv: list[str]) -> int:
    import argparse

    p = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    p.add_argument("--image", required=True, type=Path)
    p.add_argument("--listing", type=Path)
    p.add_argument("--spelling", type=Path, default=SPELLING_PATH)
    p.add_argument("--stream-out", type=Path, help="write XD's decoded stream (JSON lines)")
    args = p.parse_args(argv)
    image = args.image.read_bytes()
    listing = args.listing.read_bytes() if args.listing else None
    verdict = run(image, listing, args.spelling.read_bytes())
    if args.stream_out:
        _facts, result = decode_image(image)
        args.stream_out.write_text("".join(
            json.dumps(i.as_dict(), sort_keys=True, separators=(",", ":")) + "\n" for i in result.stream))
    print(json.dumps(verdict, sort_keys=True, indent=1))
    return 0 if verdict["verdict"] == "pass" else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
