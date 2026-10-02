"""Shared helpers for the rp11-launch tests (C-P5.0-R5-RP11-I1-R3-R4-I7).

* loaders for the evidence tooling under `infra/rp11-launch/verify/`, which is
  not a Python package (its directory name contains a hyphen);
* the §5.5/§5.6 Python reference model that T-L8 compares the compiled
  selection source with; and
* `image_from_listing`, which rebuilds a minimal ELF image from the committed
  listing's own `.text` bytes, `.rodata` dump and tables. **It is not the
  built image** and nothing about the built image follows from tests over it;
  it exists so that XD's agreement logic (XD-6, class g) can be exercised
  without a toolchain.
"""
from __future__ import annotations

import importlib.util
import re
import struct
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
LAUNCH = REPO / "infra" / "rp11-launch"
VERIFY = LAUNCH / "verify"
BUILDROOT = LAUNCH / "buildroot"
LISTING = LAUNCH / "rp11-launch.x86_64.listing"


def load(name: str, directory: Path = VERIFY):
    """Import one tool module by path; its own imports resolve beside it."""
    if str(directory) not in sys.path:
        sys.path.insert(0, str(directory))
    key = f"rp11_{directory.name}_{name}"
    if key in sys.modules:
        return sys.modules[key]
    spec = importlib.util.spec_from_file_location(key, directory / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[key] = module
    spec.loader.exec_module(module)
    return module


# ---------------------------------------------------------------------------
# reference model (proposal §5.5, §5.6)
# ---------------------------------------------------------------------------

HEX = set(b"0123456789abcdef")


def check_argv(argv: list[bytes]) -> int:
    """0 when argv is exactly `<anything> --pass A`, else 1."""
    return 0 if len(argv) == 3 and argv[1] == b"--pass" and argv[2] == b"A" else 1


def select_invocation_id(envp: list[bytes]) -> tuple[int, int, bytes] | None:
    """(entry index, offset 14, the 32 bytes) or None, exactly as §5.6 states."""
    count = 0
    candidate = None
    for k, e in enumerate(envp):
        if e[:13] != b"INVOCATION_ID":
            continue
        if e[13:14] == b"=":
            count += 1
            candidate = k
        elif len(e) == 13:
            count += 1
            candidate = None
    if count != 1 or candidate is None:
        return None
    value = envp[candidate][14:]
    if len(value) != 32 or any(b not in HEX for b in value):
        return None
    return candidate, 14, value


# ---------------------------------------------------------------------------
# an ELF image rebuilt from the committed listing
# ---------------------------------------------------------------------------


def listing_parts(listing: str) -> dict:
    entry = int(re.search(r"Entry point address:\s+0x([0-9a-f]+)", listing).group(1), 16)
    sects = {m.group(1): (int(m.group(2), 16), int(m.group(3), 16))
             for m in re.finditer(r"\]\s+(\.\w+)\s+PROGBITS\s+([0-9a-f]{16})\s+[0-9a-f]+\s+([0-9a-f]+)", listing)}
    funcs = [(m.group(3), int(m.group(1), 16), int(m.group(2)))
             for m in re.finditer(r"\d+:\s+([0-9a-f]{16})\s+(\d+)\s+FUNC\s+\S+\s+\S+\s+\S+\s+(\S+)", listing)]
    text = bytearray()
    inside = False
    for line in listing.splitlines():
        if line == "Disassembly of section .text:":
            inside = True
        elif inside and line.startswith("== "):
            inside = False
        elif inside:
            m = re.match(r"^ +[0-9a-f]+:\t([0-9a-f ]+?)\s*\t", line)
            if m:
                text += bytes.fromhex(m.group(1).replace(" ", ""))
    ro = bytearray()
    for m in re.finditer(r"^ [0-9a-f]+ ((?:[0-9a-f]{2,8} ?){1,4})", listing.split("Contents of section .rodata:")[1], re.M):
        ro += bytes.fromhex(m.group(1).replace(" ", ""))
    return {"entry": entry, "sections": sects, "functions": funcs, "text": bytes(text), "rodata": bytes(ro)}


def image_from_listing(listing: str) -> bytes:
    """A minimal ET_EXEC with the listing's .text, .rodata and FUNC symbols."""
    p = listing_parts(listing)
    text_addr, _ = p["sections"][".text"]
    ro_addr, _ = p["sections"][".rodata"]
    text_off = text_addr - 0x400000
    ro_off = ro_addr - 0x400000
    body = bytearray(ro_off + len(p["rodata"]))
    body[text_off:text_off + len(p["text"])] = p["text"]
    body[ro_off:ro_off + len(p["rodata"])] = p["rodata"]
    strtab = b"\0" + b"\0".join(n.encode() for n, _a, _s in p["functions"]) + b"\0"
    syms = bytearray(24)
    pos = 1
    for name, addr, size in p["functions"]:
        syms += struct.pack("<IBBHQQ", pos, 0x12, 0, 1, addr, size)
        pos += len(name) + 1
    shstr = b"\0.text\0.rodata\0.symtab\0.strtab\0.shstrtab\0"
    sym_off = len(body)
    body += syms
    str_off = len(body)
    body += strtab
    shs_off = len(body)
    body += shstr
    sh_off = len(body)
    sh = [
        (0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
        (1, 1, 6, text_addr, text_off, len(p["text"]), 0, 0, 1, 0),
        (7, 1, 0x32, ro_addr, ro_off, len(p["rodata"]), 0, 0, 1, 1),
        (15, 2, 0, 0, sym_off, len(syms), 4, 1, 8, 24),
        (23, 3, 0, 0, str_off, len(strtab), 0, 0, 1, 0),
        (31, 3, 0, 0, shs_off, len(shstr), 0, 0, 1, 0),
    ]
    for s in sh:
        body += struct.pack("<IIQQQQIIQQ", *s)
    header = bytearray(b"\x7fELF\x02\x01\x01\x00" + bytes(8))
    header += struct.pack("<HHIQQQIHHHHHH", 2, 62, 1, p["entry"], 0, sh_off, 0, 64, 56, 0, 64, len(sh), 5)
    body[:64] = header
    return bytes(body)


# ---------------------------------------------------------------------------
# IC-1's driver variables, derived from build.sh (I-7-R1, finding I7-R1-1)
# ---------------------------------------------------------------------------

#: Switches GCC saves in their separate canonical form (`-U NAME`, `-o FILE`).
SEPARATE_SWITCHES = ("-U", "-o")
#: GCC's `Negative()` cycle for the PIC/PIE switches (`common.opt`): within it,
#: the driver's `prune_options` drops a switch any later member cancels.
NEGATIVE_CYCLE = ("fpic", "fPIC", "fpie", "fPIE")


def build_driver_vector(out: str = "build-out") -> list[str]:
    """`build.sh`'s compiler-driver vector, `$out` expanded, without the
    standard-error redirection."""
    import shlex

    text = (LAUNCH / "build.sh").read_text().replace("\\\n", " ")
    line = next(l for l in text.splitlines() if l.strip().startswith("/usr/bin/gcc-15"))
    words = shlex.split(line.replace('"$out"', out))
    return words[:words.index("2>")]


def _cycle_member(switch: str) -> bool:
    name = switch[1:]
    if name.startswith("fno-"):
        name = "f" + name[4:]
    return name in NEGATIVE_CYCLE


def collect_gcc_options(vector: list[str]) -> str:
    """GCC 15 `set_collect_gcc_options` for a compile-only driver vector with
    one input and `-o`: the saved switches after `prune_options`, each quoted,
    then `-dumpdir` with the output's directory."""
    switches: list[list[str]] = []
    output = None
    words = iter(vector[1:])
    for word in words:
        if not word.startswith("-"):
            continue  # the input operand is not a switch
        head = next((s for s in SEPARATE_SWITCHES if word.startswith(s)), None)
        if head is not None:
            arg = word[len(head):] or next(words)
            switches.append([head, arg])
            if head == "-o":
                output = arg
        else:
            switches.append([word])
    pruned = [s for i, s in enumerate(switches)
              if not (_cycle_member(s[0]) and any(_cycle_member(t[0]) for t in switches[i + 1:]))]
    if output is None or "/" not in output:
        raise ValueError("the derivation covers a vector with -o into a directory only")
    dumpdir = output[:output.rindex("/") + 1]

    def quote(word: str) -> str:
        return "'" + word.replace("'", "'\\''") + "'"

    parts = [" ".join(quote(w) for w in s) for s in pruned]
    parts.append(f"{quote('-dumpdir')} {quote(dumpdir)}")
    return " ".join(parts)
