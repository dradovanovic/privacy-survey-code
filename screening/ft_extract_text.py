#!/usr/bin/env python3
"""Extract per-page text from full-text PDFs for the full-text LLM check.

One `pdftotext -enc UTF-8` call per page (no -layout). Each output file holds,
for every page in order, a marker line `[[page N]]` (N = PDF page index from 1
over the whole file) followed by that page's text with form feeds removed and
trailing whitespace stripped from each line; the text is not otherwise changed.
Standard library only; needs `pdftotext` on PATH.

Example (from the project root):
    python code/screening/ft_extract_text.py \
        --input code/data/screening/stream-a-v1.ft-pilot.input.csv \
        --pdfs code/data/fulltext --out code/data/fulltext/text
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import shutil
import subprocess
import sys
from pathlib import Path

LOW_TEXT_WORDS = 20
MANIFEST_COLUMNS = ("record_id", "pdf_file", "pages_used", "n_pages", "words", "low_text_pages",
                    "extractor", "extractor_version", "sha256_txt")


def extractor_version(exe: str) -> str:
    proc = subprocess.run([exe, "-v"], capture_output=True, text=True, encoding="utf-8")
    lines = (proc.stdout + proc.stderr).splitlines()
    return " | ".join(l.strip() for l in lines[:2] if l.strip())


def run_pdftotext(exe: str, pdf: Path, first: int | None = None, last: int | None = None) -> str:
    args = [exe, "-enc", "UTF-8"]
    if first is not None:
        args += ["-f", str(first), "-l", str(last)]
    proc = subprocess.run(args + [str(pdf), "-"], capture_output=True, check=True)
    return proc.stdout.decode("utf-8", errors="replace")


def page_count(exe: str, pdf: Path) -> int:
    """pdftotext ends every page with a form feed."""
    return run_pdftotext(exe, pdf).count("\f")


def parse_range(spec: str, total: int) -> tuple[int, int]:
    spec = spec.strip()
    if not spec:
        return 1, total
    first, last = (int(x) for x in spec.split("-"))
    if not 1 <= first <= last <= total:
        sys.exit(f"page range {spec} outside 1-{total}")
    return first, last


def clean_page(text: str) -> str:
    text = text.replace("\f", "")
    return "\n".join(line.rstrip() for line in text.splitlines()).strip("\n")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--input", type=Path, required=True)
    ap.add_argument("--pdfs", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)

    exe = shutil.which("pdftotext")
    if not exe:
        sys.exit("pdftotext not found on PATH")
    version = extractor_version(exe)
    with a.input.open(encoding="utf-8-sig", newline="") as fh:
        rows = list(csv.DictReader(fh))
    a.out.mkdir(parents=True, exist_ok=True)

    manifest = []
    for row in rows:
        pdf = a.pdfs / row["pdf_file"]
        first, last = parse_range(row.get("pdf_pages") or "", page_count(exe, pdf))
        blocks, words, low = [], 0, []
        for n in range(first, last + 1):
            page = clean_page(run_pdftotext(exe, pdf, n, n))
            w = len(page.split())
            words += w
            if w < LOW_TEXT_WORDS:
                low.append(str(n))
            blocks.append(f"[[page {n}]]\n{page}" if page else f"[[page {n}]]")
        data = ("\n".join(blocks) + "\n").encode("utf-8")
        (a.out / f"{Path(row['pdf_file']).stem}.txt").write_bytes(data)
        manifest.append({
            "record_id": row["record_id"], "pdf_file": row["pdf_file"],
            "pages_used": f"{first}-{last}", "n_pages": last - first + 1, "words": words,
            "low_text_pages": ";".join(low), "extractor": "pdftotext", "extractor_version": version,
            "sha256_txt": hashlib.sha256(data).hexdigest(),
        })

    with (a.out / "manifest.csv").open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=MANIFEST_COLUMNS, lineterminator="\n")
        w.writeheader()
        w.writerows(manifest)
    w = csv.DictWriter(sys.stdout, fieldnames=MANIFEST_COLUMNS, lineterminator="\n")
    w.writeheader()
    w.writerows(manifest)
    stop = [m["record_id"] for m in manifest
            if m["words"] == 0 or len(m["low_text_pages"].split(";")) * 2 > m["n_pages"] and m["low_text_pages"]]
    if stop:
        print(f"\nNOT READY (no text, or more than half of pages low-text): {stop}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
