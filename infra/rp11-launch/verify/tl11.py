"""T-L11 — decoding agreement, and the T-L10 verdict it gates (§5.12.1, XD-7).

For one image and one listing:

1. XD decodes `.text` from the image bytes (XD-1 … XD-5) and its stream must
   equal the listing's on every boundary, byte field, mnemonic, operand and
   direct target (XD-6);
2. the image facts must agree three ways: XD's own ELF reader, T-L7's parser,
   and the listing's `readelf` tables as T-L10 parses them (XD-1);
3. T-L10 runs over the listing's stream and over XD's rendered stream, with
   XD's facts, and the two verdicts and tables must be identical (XD-7).

**Any disagreement is a stop**, never resolved by preferring either decoder
(§4.5). The record carries every digest XD-8 requires, and states whether the
image digest equals the expected digest: a T-L10 verdict is evidence only if
it does and T-L11 passed on the same digests.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import ctverify  # noqa: E402
import elfcheck  # noqa: E402
import xdecode  # noqa: E402


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def run(image: bytes, listing: bytes, spelling: bytes, contract: dict, expected_image_sha256: str) -> dict:
    failures: list[str] = []
    verdict = xdecode.run(image, listing, spelling)
    failures += [f"XD {f['class']}: {f['detail']}" for f in verdict["failures"]]
    facts_xd, result = xdecode.decode_image(image)
    sp = xdecode.Spelling.load(spelling.decode("utf-8"))

    # Three-way image facts (XD-1).
    t7 = elfcheck.facts(image)
    lst_facts, lst_lines = ctverify.parse_listing(listing.decode("utf-8"))
    xd_view = {"e_entry": facts_xd.entry, "text": [facts_xd.text_addr, facts_xd.text_addr + facts_xd.text_size],
               "rodata": list(facts_xd.rodata), "functions": [[f.name, f.start, f.size] for f in facts_xd.functions]}
    t7_view = {"e_entry": t7["e_entry"], "text": [t7["text_addr"], t7["text_addr"] + t7["text_size"]],
               "rodata": t7["rodata"], "functions": t7["functions"]}
    lst_view = {"e_entry": lst_facts.entry, "text": list(lst_facts.text), "rodata": list(lst_facts.rodata),
                "functions": [list(f) for f in lst_facts.functions]}
    if not (xd_view == t7_view == lst_view):
        failures.append(f"image facts disagree: XD {xd_view} T-L7 {t7_view} listing {lst_view}")

    # T-L10 twice (XD-7).
    tl10_listing = ctverify.verify(lst_facts, lst_lines, contract)
    ro_lo, ro_hi = facts_xd.rodata
    ro_off = ro_lo - facts_xd.text_addr + facts_xd.text_offset
    xd_facts = ctverify.Facts(
        entry=facts_xd.entry, text=(facts_xd.text_addr, facts_xd.text_addr + facts_xd.text_size),
        rodata=(ro_lo, ro_hi), rodata_bytes=image[ro_off:ro_off + (ro_hi - ro_lo)],
        functions=tuple((f.name, f.start, f.size) for f in facts_xd.functions))
    xd_lines = [ctverify.Line(r["address"], bytes.fromhex(r["bytes"]), r["text"])
                for r in xdecode.rendered_stream(result, facts_xd, sp)]
    tl10_xd = ctverify.verify(xd_facts, xd_lines, contract)
    if lst_facts.rodata_bytes != xd_facts.rodata_bytes:
        failures.append("the listing's .rodata dump differs from the image's .rodata")
    if tl10_listing != tl10_xd:
        failures.append("T-L10 over XD's stream differs from T-L10 over the listing")
    if tl10_listing["verdict"] != "pass":
        failures += [f"T-L10: {v}" for v in tl10_listing["violations"]]

    image_sha = _sha(image)
    return {
        "image_sha256": image_sha,
        "image_is_expected": image_sha == expected_image_sha256,
        "listing_sha256": _sha(listing),
        "xdecode_py_sha256": verdict["xdecode_py_sha256"],
        "spelling_table_sha256": verdict["spelling_table_sha256"],
        "xd_table_sha256": verdict["table_sha256"],
        "ctverify_py_sha256": _sha((HERE / "ctverify.py").read_bytes()),
        "interpreter": sys.version.split()[0],
        "instructions": verdict["instructions"],
        "agreed_stream_sha256": verdict["stream_sha256"],
        "tl10_tables_sha256": ctverify.tables_digest(tl10_listing),
        "tl10_verdict": tl10_listing["verdict"],
        "tl11_verdict": "pass" if not failures else "fail",
        "tl10_evidence": (not failures) and image_sha == expected_image_sha256,
        "failures": failures,
    }, tl10_listing


def main(argv: list[str]) -> int:
    import argparse

    p = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    p.add_argument("--image", type=Path, required=True)
    p.add_argument("--listing", type=Path, required=True)
    p.add_argument("--spelling", type=Path, default=HERE / "xdecode-spelling.table")
    p.add_argument("--tables-out", type=Path, help="write T-L10's emitted tables (JSON)")
    a = p.parse_args(argv)
    sys.path.insert(0, str(HERE.parents[2]))
    from tools.phase_5_0_evidence import rp11_launch

    record, tables = run(a.image.read_bytes(), a.listing.read_bytes(), a.spelling.read_bytes(),
                         rp11_launch.control_contract(), rp11_launch.EXPECTED_IMAGE_SHA256)
    if a.tables_out:
        a.tables_out.write_text(json.dumps(tables, indent=1, sort_keys=True) + "\n")
    print(json.dumps(record, indent=1, sort_keys=True))
    return 0 if record["tl11_verdict"] == "pass" else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
