# Instruction for Claude Code: full-text pilot, screen-A-ft-v1 (draft)

Use this once, for the full-text pilot on the 11 papers H1 has already decided.
Paste everything below the line into Claude Code, started in `D:\02_Projects\privacy-survey`.

---

Set up and run the full-text LLM check, prompt `code/prompts/screen-A-ft-v1.md` (draft), on the 11 pilot papers listed in `code/data/screening/stream-a-v1.ft-pilot.input.csv`.

**Hard rule: blinding.** Never open, read or reference `code/data/screening/stream-a-v1.fulltext.csv`, `code/data/screening/stream-a-v1.h1.csv`, or any of their backups (`*.before-*.csv`, including those in `code/data/screening/_archive/`). They hold my decisions. The only record data you use is `stream-a-v1.ft-pilot.input.csv` (columns `n, record_id, title, year, pdf_file, pdf_pages`). Do not compare anything with my decisions.

**Other rules.** Do not edit the prompt file, `code/screening/run_llm_screen.py`, or any PDF. The PDFs and the extracted text are copyrighted: never `git add` them (`code/data/fulltext/.gitignore` already ignores everything in that folder, including the `text/` subfolder). Standard library only, except the PDF text library in step 1. Do not install anything without asking me first.

## 1. Text extraction: write `code/screening/ft_extract_text.py`

- Arguments: `--input` (the pilot input CSV), `--pdfs code/data/fulltext`, `--out code/data/fulltext/text`.
- For each row, read `<pdfs>/<pdf_file>`. Pages: all pages, or only the inclusive range in `pdf_pages` (for example `229-239`) when it is not empty. Page numbers are always the PDF page index counted from 1 over the whole file (so a range keeps its own numbers, for example 229 to 239, not 1 to 11).
- Extractor: use `pdftotext` (poppler) if it is on PATH, one call per page with `-enc UTF-8` and without `-layout`. If it is not on PATH, ask me before installing PyMuPDF (`pymupdf`), then use `page.get_text()`. Use the same extractor for all 11 papers.
- Write `<out>/<pdf_file stem>.txt`, UTF-8, LF line endings. For each page in order write a line `[[page N]]`, then that page's text with form feeds removed and trailing whitespace stripped from each line. Do not change the text otherwise: no de-hyphenation, no re-wrapping, no spelling fixes.
- Write `<out>/manifest.csv` with: `record_id, pdf_file, pages_used, n_pages, words, low_text_pages, extractor, extractor_version, sha256_txt`. `low_text_pages` lists pages with fewer than 20 words (possible scans or figures).
- Print the manifest. If any paper has more than half of its pages in `low_text_pages`, or no text at all, do not continue to step 3 for it: list it and tell me.

## 2. Runner: write `code/screening/run_llm_fulltext.py`

Model it on `run_llm_screen.py` and import from it (unchanged) `build_args`, `loggable_args`, `claude_version`, `call_claude`, `strip_fence`, `done_ids` and `CONTEXT_ADDITIONS`, so the call setup is identical (print mode, `--system-prompt` from the SYSTEM section, no tools, no MCP, `--safe-mode`, a fresh empty temporary folder per call, API-key variables removed).

- Arguments: `--input`, `--text-dir code/data/fulltext/text`, `--prompt`, `--model`, `--run`, `--out`, `--limit`.
- Prompt file: SYSTEM is the text between `## SYSTEM` and the last `---` before `## USER (per paper)`; the USER template is everything after `## USER (per paper)`. Record the prompt file's SHA-256.
- User message: the template with `{title}` and `{year}` from the input CSV and `{fulltext}` replaced by the whole text file from step 1. Nothing else is sent.
- Parse the answer like `run_llm_screen.py` does (strip a code fence, `json.loads`), then check the schema. Any of these is a schema error:
  - `decision` not in `include`, `exclude`, `unclear`;
  - `primary_code` not one of `A-E1`…`A-E6`, `A-I5` or null; `exclude` without a `primary_code`; `include` or `unclear` with one;
  - `criteria` not holding exactly the keys `A-I1`…`A-I5`, each an object with `judgment` in `met`, `not_met`, `unclear`, `quote` a string, `page` an integer or null;
  - `include` while any judgment is not `met`; `exclude` while no judgment is `not_met`; `unclear` while a judgment is `not_met` or none is `unclear`;
  - `route` not in `B`, `C`, `none`, null; a non-null `route` without `primary_code` `A-E1`, or `A-E1` without a route;
  - `flags` not a list drawn from `nilm_only`, `mechanism_only`, `ambiguous_ami`, `text_incomplete`.
  On a schema error, or a CLI error, retry once, exactly as `run_llm_screen.py` does.
- Quote check (recorded, never a reason to retry or fail): for each criterion, compare the quote with the text under its `[[page N]]` marker, after collapsing all whitespace to single spaces and joining words hyphenated across a line break (`exam-\nple` → `example`) on both sides. Record `quote_check` per criterion as `on_page`, `other_page:N` (found only on another page; give the first), `not_found`, or `empty`. Also record `quote_words` (word count; the prompt asks for at most 40).
- Write one JSON line per paper to `--out`, with the same fields as `run_llm_screen.py` writes (`record_id`, `run`, `prompt_version`, `prompt_sha256`, `model_requested`, `model_reported`, `claude_code_version`, `cli_args`, `context_additions`, `screened_at`, `status`, `raw_text`, `parsed`, `parse_error`, `retried`, `first_attempt_error`, `usage`), plus `text_file`, `text_sha256`, `pages_used` and `quote_checks`. Skip papers already in `--out`, so an interrupted run can be resumed.

## 3. Run

1. Note the prompt file's SHA-256. It should be `abf8d733f3734cf4921de46d1035dacfe11bc4848f9a80d701d6ce290f413eef`; if not, stop and tell me.
2. Run step 1 and show me the manifest.
3. Smoke test: `--limit 1` with `--run 1` and `--out code/data/screening/llm/stream-a-v1.ft-pilot.screen-A-ft-v1.run1.jsonl`. Show the parsed answer and the quote checks. If it is a schema error or several quotes are `not_found`, stop and tell me.
4. Otherwise finish run 1 into the same file (it resumes after the smoke-test paper), then run 2 with `--run 2` into `...run2.jsonl`. Settings for both: `--input code/data/screening/stream-a-v1.ft-pilot.input.csv`, `--text-dir code/data/fulltext/text`, `--prompt code/prompts/screen-A-ft-v1.md`, `--model claude-opus-5-5`.
5. Print a summary per run: decisions and primary codes, errors, retries, model reported, Claude Code version, token usage, and the quote-check counts (`on_page` / `other_page` / `not_found` / `empty`).
6. Then stop. Do not change the prompt or the scripts after the run, and do not touch any other file.
