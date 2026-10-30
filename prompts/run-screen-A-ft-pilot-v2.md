# Instruction for Claude Code: full-text pilot re-run, screen-A-ft-v2 (draft)

Use this once, for the re-run of the 11 full-text pilot papers with prompt v2.
Paste everything below the line into Claude Code, started in `D:\02_Projects\privacy-survey`.

---

Re-run the full-text LLM check with the new draft prompt `code/prompts/screen-A-ft-v2.md` on the same 11 pilot papers.

**Hard rule: blinding.** As before: never open, read or reference `code/data/screening/stream-a-v1.fulltext.csv`, `code/data/screening/stream-a-v1.h1.csv`, `stream-a-v1.ft-pilot.compare.*`, or any of their backups (`*.before-*`, including those in `code/data/screening/_archive/`). The only record data you use is `code/data/screening/stream-a-v1.ft-pilot.input.csv`. Do not compare anything with my decisions.

**Other rules.** Do not edit either prompt file, `run_llm_screen.py`, `ft_extract_text.py`, any PDF, or the extracted text in `code/data/fulltext/text/` (re-use it as it is; do not re-extract). Never `git add` anything under `code/data/fulltext/`. Do not touch the v1 run files.

1. Check that `code/prompts/screen-A-ft-v2.md` has SHA-256 `305da17b45874d8256ad99b360fb488087946d2f9eab08fda22eb91b9bbb04b5`. If not, stop and tell me.
2. One small change to `code/screening/run_llm_fulltext.py`, nothing else: in `normalize()`, apply `unicodedata.normalize("NFKC", text)` first, so ligatures such as "ﬁ" match a plain "fi" in the quote check (add `import unicodedata`). Update the docstring of `normalize()` to say so. Show me the diff.
3. Run 1, then run 2, each with:
   - `--input code/data/screening/stream-a-v1.ft-pilot.input.csv`
   - `--text-dir code/data/fulltext/text`
   - `--prompt code/prompts/screen-A-ft-v2.md`
   - `--model claude-opus-5-5`
   - `--run 1` (then `--run 2`)
   - `--out code/data/screening/llm/stream-a-v1.ft-pilot.screen-A-ft-v2.run1.jsonl` (then `run2`)
4. Print the same summary per run as last time: decisions and primary codes with flags per paper, errors, retries, model reported, Claude Code version, token usage, and the quote-check counts.
5. Then stop. Do not change the prompt or the scripts after the run, and do not touch any other file.
