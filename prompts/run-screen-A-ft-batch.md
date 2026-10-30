# Instruction for Claude Code: full-text LLM check on one batch, screen-A-ft-v2 (frozen)

Use this only after H1 has decided every paper of the batch in `stream-a-v1.fulltext.csv`, and after the batch input file `code/data/screening/stream-a-v1.ft-batchNN.input.csv` has been prepared (columns `n, record_id, title, year, pdf_file, pdf_pages`, no decisions).
Paste everything below the line into Claude Code, started in `D:\02_Projects\privacy-survey`, and change `01` to the batch number.

---

Run the frozen full-text prompt screen-A-ft-v2 on full-text batch 01, using the existing scripts `code/screening/ft_extract_text.py` and `code/screening/run_llm_fulltext.py` unchanged.

**Hard rule: blinding.** Never open, read or reference `code/data/screening/stream-a-v1.fulltext.csv`, `code/data/screening/stream-a-v1.h1.csv`, any `*.compare.*` file, or any of their backups (`*.before-*`, including those in `code/data/screening/_archive/`). The only record data you use is `code/data/screening/stream-a-v1.ft-batch01.input.csv`. Do not compare anything with my decisions.

**Other rules.** Do not edit the prompt, the scripts or any PDF (except the one-time change in step 0). Never `git add` anything under `code/data/fulltext/`.

0. **Batch 01 only, one-time change.** `ft_extract_text.py` currently overwrites `manifest.csv` on every run. Change it to write `manifest.<input file stem>.csv` instead (for example `manifest.stream-a-v1.ft-batch01.input.csv`), and rename the existing `code/data/fulltext/text/manifest.csv` to `manifest.stream-a-v1.ft-pilot.input.csv`. Change nothing else, update the docstring, and show me the diff. Skip this step from batch 02 on.

1. Check that `code/prompts/screen-A-ft-v2.md` has SHA-256 `305da17b45874d8256ad99b360fb488087946d2f9eab08fda22eb91b9bbb04b5`. If not, stop and tell me.
2. Extract the text: `ft_extract_text.py --input code/data/screening/stream-a-v1.ft-batch01.input.csv --pdfs code/data/fulltext --out code/data/fulltext/text`. Show me the batch's manifest. If a paper has no text or more than half of its pages in `low_text_pages`, or its text is visibly garbled (for example shifted characters), do not run it: list it and tell me.
3. Run 1, then run 2, each with `--input code/data/screening/stream-a-v1.ft-batch01.input.csv`, `--text-dir code/data/fulltext/text`, `--prompt code/prompts/screen-A-ft-v2.md`, `--model claude-opus-5-5`, `--run 1` (then `--run 2`), `--out code/data/screening/llm/stream-a-v1.ft-batch01.screen-A-ft-v2.run1.jsonl` (then `run2`).
4. Print a summary per run: decision, primary code, route and flags per paper; errors, retries, model reported, Claude Code version, token usage, and quote-check counts with every quote that is not `on_page`.
5. Then stop. Do not touch any other file.
