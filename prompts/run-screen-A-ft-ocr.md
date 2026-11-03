# Instruction for Claude Code: OCR text for scanned full-text PDFs

Use this when the text extraction of a full-text batch reports papers with no text layer (scans). It is used together with `run-screen-A-ft-batch.md`: between its step 2 (extraction) and step 3 (runs).
Paste the paste-text the assistant gives you; the steps are below the line.

---

**Hard rules.** Same blinding and file rules as in `run-screen-A-ft-batch.md`: never open `stream-a-v1.fulltext.csv`, `stream-a-v1.h1.csv`, any `*.compare.*` file or their backups; do not edit the prompt, `run_llm_screen.py`, `run_llm_fulltext.py` or any PDF; never `git add` anything under `code/data/fulltext/`. Do not install anything without asking me first.

1. **Write `code/screening/ft_ocr_text.py`** (once; reuse it later). Arguments: `--input` (the batch input CSV), `--ids` (record ids to OCR, comma-separated), `--pdfs code/data/fulltext`, `--out code/data/fulltext/text`, `--lang eng`, `--dpi 300`.
   - Needs `pdftoppm` and `tesseract` on PATH. If either is missing, stop and tell me (I will decide whether to install them).
   - For each id: render each page in the paper's range (all pages, or `pdf_pages` when set; PDF page index from 1 over the whole file) with `pdftoppm -r <dpi> -png -f N -l N`, run `tesseract <png> - -l <lang>`, keep the text. Use a temporary folder outside the project for the images and remove it afterwards.
   - Write `<out>/<pdf_file stem>.txt` in exactly the format of `ft_extract_text.py`: UTF-8, LF, a line `[[page N]]` before each page, form feeds removed, trailing whitespace stripped, nothing else changed. This replaces the empty text file written by the extraction step for that paper.
   - Write `<out>/manifest.ocr.<input file stem>.csv` with the columns of the extraction manifest; `extractor` = `tesseract (OCR, pdftoppm <dpi> dpi)`, `extractor_version` = first line of `tesseract --version`.
   - Standard library only.
2. Run it for the ids I give you and show me the OCR manifest and the first 30 lines of each text file.
3. If a paper still has fewer than 20 words on more than half of its pages, do not run it; tell me.
