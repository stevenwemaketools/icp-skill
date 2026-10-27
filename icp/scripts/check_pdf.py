#!/usr/bin/env python3
"""Check a PDF produced by make_pdf.py: structure, page count, expected and forbidden text, language, no prices.

Standard library only. Used by the /icp skill after rendering and by the skill's test cases.

Usage:
  python3 check_pdf.py icp.pdf --lang es --min-pages 6 --max-pages 9 --expect-text "..." --no-prices
  python3 check_pdf.py icp.pdf --json

Exit 0 when every check passes, 1 otherwise. The report lists each check with ok or FAIL.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import zlib
from pathlib import Path

REQUIRED_HEADINGS = {
    "es": ["El perfil", "Por qué este cliente", "Quién NO es tu cliente", "Dónde encontrarlo", "Plan de 30 días", "Siguiente paso", "NORTH STAR"],
    "en": ["The profile", "Why this customer", "Who is NOT your customer", "Where to find them", "30-day plan", "Next step", "NORTH STAR"],
}
PRICE_RE = re.compile(r"(?:US\$|USD|\$|€|RD\$)\s?\d|\d[\d.,]*\s?(?:USD|dólares|dollars|euros)\b", re.I)


def read_pdf(path: Path) -> bytes:
    return path.read_bytes()


def check_structure(data: bytes) -> tuple[list[str], int]:
    errors: list[str] = []
    if not data.startswith(b"%PDF-1."):
        errors.append("missing PDF header")
    if not data.rstrip().endswith(b"%%EOF"):
        errors.append("missing %%EOF")
    m = re.search(rb"startxref\s+(\d+)\s+%%EOF\s*$", data)
    if not m:
        errors.append("missing startxref")
        return errors, 0
    xref_at = int(m.group(1))
    head = re.match(rb"xref\s+0 (\d+)\s+", data[xref_at:])
    if not head:
        errors.append("startxref does not point at an xref table")
        return errors, 0
    count = int(head.group(1))
    pos = xref_at + head.end()
    for i in range(1, count):
        entry = data[pos + i * 20: pos + (i + 1) * 20]
        try:
            off = int(entry[:10])
        except ValueError:
            errors.append(f"xref entry {i} is malformed")
            continue
        if not re.match(rb"%d 0 obj" % i, data[off:off + 24]):
            errors.append(f"xref entry {i} does not point at object {i}")
    pages = len(re.findall(rb"/Type /Page\b(?!s)", data))
    if pages == 0:
        errors.append("no page objects")
    return errors, pages


def _unescape(raw: bytes) -> bytes:
    out = bytearray()
    i = 0
    while i < len(raw):
        b = raw[i]
        if b == 0x5C and i + 1 < len(raw):
            nxt = raw[i + 1]
            if 0x30 <= nxt <= 0x37:
                j = i + 1
                digits = b""
                while j < len(raw) and len(digits) < 3 and 0x30 <= raw[j] <= 0x37:
                    digits += bytes([raw[j]])
                    j += 1
                out.append(int(digits, 8))
                i = j
                continue
            mapping = {0x6E: 0x0A, 0x72: 0x0D, 0x74: 0x09, 0x62: 0x08, 0x66: 0x0C}
            out.append(mapping.get(nxt, nxt))
            i += 2
            continue
        out.append(b)
        i += 1
    return bytes(out)


def extract_text(data: bytes) -> str:
    """Pull every string shown with Tj out of every content stream, in order, one line per text object."""
    chunks: list[str] = []
    for m in re.finditer(rb"stream\r?\n(.*?)\r?\nendstream", data, re.S):
        body = m.group(1)
        if b"FlateDecode" in data[max(0, m.start() - 200):m.start()]:
            try:
                body = zlib.decompress(body)
            except zlib.error:
                continue
        for bt in re.finditer(rb"BT(.*?)ET", body, re.S):
            parts = []
            for t in re.finditer(rb"\((.*?)(?<!\\)\)\s*Tj", bt.group(1), re.S):
                parts.append(_unescape(t.group(1)).decode("cp1252", "replace"))
            if parts:
                chunks.append("".join(parts))
    return "\n".join(chunks)


def main() -> int:
    ap = argparse.ArgumentParser(description="Check a PDF made by make_pdf.py")
    ap.add_argument("pdf")
    ap.add_argument("--lang", choices=["es", "en"], help="assert the fixed headings of this language are present")
    ap.add_argument("--min-pages", type=int)
    ap.add_argument("--max-pages", type=int)
    ap.add_argument("--expect-pages", type=int)
    ap.add_argument("--expect-text", action="append", default=[], help="text that must appear (repeatable)")
    ap.add_argument("--forbid-text", action="append", default=None, help="text that must not appear (repeatable; default: em dash, en dash)")
    ap.add_argument("--no-prices", action="store_true", help="assert the last page shows no currency amount")
    ap.add_argument("--dump-text", action="store_true", help="print the extracted text and exit")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    path = Path(args.pdf)
    if not path.exists():
        print(f"not found: {path}")
        return 1
    data = read_pdf(path)
    text = extract_text(data)
    if args.dump_text:
        print(text)
        return 0
    norm = re.sub(r"\s+", " ", text)
    results: list[tuple[str, bool, str]] = []

    errors, pages = check_structure(data)
    results.append(("structure", not errors, "; ".join(errors) or f"{pages} pages, xref ok"))
    if args.expect_pages is not None:
        results.append((f"pages == {args.expect_pages}", pages == args.expect_pages, f"{pages} pages"))
    if args.min_pages is not None:
        results.append((f"pages >= {args.min_pages}", pages >= args.min_pages, f"{pages} pages"))
    if args.max_pages is not None:
        results.append((f"pages <= {args.max_pages}", pages <= args.max_pages, f"{pages} pages"))
    # the cover draws a North Star's final period as its own lime glyph, so compare without trailing periods
    norm_cmp = re.sub(r"\s+\.", ".", norm)
    for needle in args.expect_text:
        n = re.sub(r"\s+", " ", needle).strip().rstrip(". ")
        hit = n in norm_cmp
        results.append((f"contains: {n[:50]}", hit, "found" if hit else "not found in the PDF text"))
    forbidden = args.forbid_text if args.forbid_text is not None else ["\u2014", "\u2013"]
    for needle in forbidden:
        label = {"\u2014": "no em dash", "\u2013": "no en dash"}.get(needle, f"absent: {needle[:30]}")
        results.append((label, needle not in text, "clean" if needle not in text else f"found {text.count(needle)} time(s)"))
    if args.lang:
        missing = [h for h in REQUIRED_HEADINGS[args.lang] if h not in norm]
        results.append((f"headings for {args.lang}", not missing, "all present" if not missing else "missing: " + ", ".join(missing)))
    if args.no_prices:
        last = text.split("\n")
        # the closing page is the last ~40 text objects; look at the tail of the document
        tail = " ".join(last[-60:])
        m = PRICE_RE.search(tail)
        results.append(("no prices on the closing page", m is None, "clean" if m is None else f"found {m.group(0)!r}"))

    ok = all(r[1] for r in results)
    if args.json:
        print(json.dumps({"ok": ok, "pages": pages, "checks": [{"name": n, "ok": o, "detail": d} for n, o, d in results]}, ensure_ascii=False, indent=2))
    else:
        for n, o, d in results:
            print(f"  {'ok  ' if o else 'FAIL'} {n}: {d}")
        print("PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
