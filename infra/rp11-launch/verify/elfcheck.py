"""T-L7 — structural inspection of the built image (proposal §5.12.1, §5.12.2).

A pure-Python ELF parser (standard library `struct` only) that applies BI-1 …
BI-5 to the image, BI-8 to the linker map and BI-9 to `.text`, and checks that
the concatenated instruction bytes of the committed listing equal the image's
`.text` exactly (BI-10's byte half).

**That is byte equality only.** It shows nothing about where instructions
begin, what they are, or where they transfer: those are the listing's
decoding, which T-L11 (XD) checks. It shares no code with XD or T-L10.
"""
from __future__ import annotations

import hashlib
import json
import re
import struct
import sys
from pathlib import Path

PT = {0: "NULL", 1: "LOAD", 2: "DYNAMIC", 3: "INTERP", 4: "NOTE", 6: "PHDR", 7: "TLS",
      0x6474E550: "GNU_EH_FRAME", 0x6474E551: "GNU_STACK", 0x6474E552: "GNU_RELRO",
      0x6474E553: "GNU_PROPERTY"}
ALLOWED_SECTIONS = ("", ".text", ".rodata", ".symtab", ".strtab", ".shstrtab")
SHT_REL, SHT_RELA, SHT_RELR = 9, 4, 19


def _u(fmt: str, data: bytes, off: int):
    return struct.unpack_from("<" + fmt, data, off)


def parse(data: bytes) -> dict:
    """The facts BI-1 … BI-5 need, from the image bytes."""
    ident = data[:16]
    (e_type, e_machine, e_version, e_entry, e_phoff, e_shoff, e_flags, e_ehsize,
     e_phentsize, e_phnum, e_shentsize, e_shnum, e_shstrndx) = _u("HHIQQQIHHHHHH", data, 16)
    phdrs = []
    for i in range(e_phnum):
        p_type, p_flags, p_offset, p_vaddr, _pa, p_filesz, p_memsz, p_align = _u(
            "IIQQQQQQ", data, e_phoff + i * e_phentsize)
        phdrs.append({"type": PT.get(p_type, hex(p_type)), "flags": p_flags, "offset": p_offset,
                      "vaddr": p_vaddr, "filesz": p_filesz, "memsz": p_memsz})
    raw_sections = [_u("IIQQQQIIQQ", data, e_shoff + i * e_shentsize) for i in range(e_shnum)]
    shstr_off = raw_sections[e_shstrndx][4]

    def name_at(off: int, idx: int) -> str:
        end = data.index(b"\0", off + idx)
        return data[off + idx:end].decode("ascii")

    sections = []
    for sh in raw_sections:
        sections.append({"name": name_at(shstr_off, sh[0]), "type": sh[1], "flags": sh[2],
                         "addr": sh[3], "offset": sh[4], "size": sh[5], "link": sh[6]})
    by_name = {s["name"]: s for s in sections}
    symbols = []
    if ".symtab" in by_name:
        st = by_name[".symtab"]
        strtab = sections[st["link"]]
        for off in range(st["offset"], st["offset"] + st["size"], 24):
            st_name, st_info, _o, st_shndx, st_value, st_size = _u("IBBHQQ", data, off)
            symbols.append({"name": name_at(strtab["offset"], st_name), "bind": st_info >> 4,
                            "type": st_info & 0xF, "shndx": st_shndx, "value": st_value, "size": st_size})
    text = by_name.get(".text")
    return {
        "ident": ident.hex(), "e_type": e_type, "e_machine": e_machine, "e_entry": e_entry,
        "phdrs": phdrs, "sections": sections, "symbols": symbols,
        "text_bytes": data[text["offset"]:text["offset"] + text["size"]] if text else b"",
    }


def check_image(data: bytes) -> list[str]:
    f = parse(data)
    bad = []
    ident = bytes.fromhex(f["ident"])
    # BI-1
    if ident[:4] != b"\x7fELF" or ident[4] != 2 or ident[5] != 1 or ident[7] != 0:
        bad.append("BI-1: not ELFCLASS64 / ELFDATA2LSB / OS ABI SYSV")
    if f["e_type"] != 2 or f["e_machine"] != 62:
        bad.append("BI-1: not ET_EXEC / EM_X86_64")
    start = [s for s in f["symbols"] if s["name"] == "_start"]
    if len(start) != 1 or start[0]["value"] != f["e_entry"]:
        bad.append("BI-1: e_entry is not the value of _start")
    # BI-2
    types = [p["type"] for p in f["phdrs"]]
    if sorted(types) != ["GNU_STACK", "LOAD"]:
        bad.append(f"BI-2: program headers {types}, not exactly one LOAD and one GNU_STACK")
    for p in f["phdrs"]:
        if p["type"] == "LOAD" and p["flags"] != 5:
            bad.append("BI-2: the LOAD segment is not exactly read and execute")
        if p["type"] == "GNU_STACK" and p["flags"] != 6:
            bad.append("BI-2: GNU_STACK is not exactly read and write")
    # BI-3
    names = tuple(s["name"] for s in f["sections"])
    if names != ALLOWED_SECTIONS:
        bad.append(f"BI-3: sections {names}, not {ALLOWED_SECTIONS}")
    # BI-4
    for s in f["symbols"][1:]:
        if s["shndx"] == 0:
            bad.append(f"BI-4: undefined symbol {s['name']!r}")
        if s["type"] in (6, 10):
            bad.append(f"BI-4: STT_TLS or STT_GNU_IFUNC symbol {s['name']!r}")
    if not start or start[0]["bind"] != 1:
        bad.append("BI-4: _start is not global")
    # BI-5
    if any(s["type"] in (SHT_REL, SHT_RELA, SHT_RELR) for s in f["sections"]):
        bad.append("BI-5: a relocation section is present")
    # BI-9
    if len(f["text_bytes"]) >= 4096:
        bad.append("BI-9: .text is 4 KiB or larger")
    return bad


_INSN = re.compile(r"^ +([0-9a-f]+):\t([0-9a-f ]+?)\s*\t")


def listing_text_bytes(listing: str) -> bytes:
    """The concatenated byte fields of the listing's disassembly lines."""
    out = bytearray()
    inside = False
    for line in listing.splitlines():
        if line == "Disassembly of section .text:":
            inside = True
            continue
        if inside and line.startswith("== "):
            break
        if inside:
            m = _INSN.match(line)
            if m:
                out += bytes.fromhex(m.group(2).replace(" ", ""))
    return bytes(out)


def check_listing_bytes(image: bytes, listing: str) -> list[str]:
    """BI-10's byte half: the listing omits and adds no byte of `.text`."""
    if listing_text_bytes(listing) != parse(image)["text_bytes"]:
        return ["BI-10: the listing's instruction bytes differ from .text"]
    return []


def check_map(map_text: str) -> list[str]:
    """BI-8: the map names exactly start.o then launch.o, and nothing else."""
    loads = re.findall(r"^LOAD (\S+)$", map_text, re.M)
    bad = []
    if loads != ["start.o", "launch.o"]:
        bad.append(f"BI-8: map loads {loads}, not start.o then launch.o")
    if re.search(r"\.a\(|linker stubs|\blibc\b|crt\w*\.o|libgcc", map_text):
        bad.append("BI-8: map names an archive member, a library or a start file")
    return bad


def facts(image: bytes) -> dict:
    """The three-way agreement half of XD-1: T-L7's section and symbol values."""
    f = parse(image)
    text = next(s for s in f["sections"] if s["name"] == ".text")
    rodata = next(s for s in f["sections"] if s["name"] == ".rodata")
    funcs = sorted(([s["name"], s["value"], s["size"]] for s in f["symbols"] if s["type"] == 2),
                   key=lambda x: x[1])
    return {"e_entry": f["e_entry"], "text_addr": text["addr"], "text_offset": text["offset"],
            "text_size": text["size"], "rodata": [rodata["addr"], rodata["addr"] + rodata["size"]],
            "functions": funcs}


def main(argv: list[str]) -> int:
    import argparse

    p = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    p.add_argument("--image", type=Path, required=True)
    p.add_argument("--listing", type=Path, required=True)
    p.add_argument("--map", type=Path, required=True)
    a = p.parse_args(argv)
    image = a.image.read_bytes()
    bad = check_image(image) + check_listing_bytes(image, a.listing.read_text()) + check_map(a.map.read_text())
    print(json.dumps({"image_sha256": hashlib.sha256(image).hexdigest(), "facts": facts(image),
                      "violations": bad, "verdict": "pass" if not bad else "fail"}, indent=1, sort_keys=True))
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
