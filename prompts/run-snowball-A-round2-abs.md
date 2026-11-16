# Instruction for Claude Code: Stream A snowballing round 2, step 2b (LLM runs on records with a manually added abstract)

Use this after H1 has added abstracts by hand for the `h1_no_abstract` records of round 2 (16.11.2026). 14 of the 15 records now have an abstract of at least 30 words (3088 has none and stays with H1); they are in `code/data/screening/stream-a-v1.snowball-r2.screening-input.abs-manual.csv` (same columns as the round-2 sheet, `abstract_source = manual`) and in the ids file `stream-a-v1.sb2-batch03.ids.csv`. Under D21 they are screened like every other snowballed record.
Paste everything below the line into Claude Code, started in `D:\02_Projects\privacy-survey`.

---

Run the frozen screen-A-v1 prompt on snowball round-2 batch 03, using the existing script `code/screening/run_llm_screen.py` unchanged.

1. Check that `code/prompts/screen-A-v1.md` has SHA-256 `df082ced81a8646e630811b84ffd4780665be4ff70ca4b3e9e65c5f475c00a53`. If not, stop and tell me.
2. Run 1 and then run 2, each with:
   - `--sheet code/data/screening/stream-a-v1.snowball-r2.screening-input.abs-manual.csv`
   - `--ids code/data/screening/stream-a-v1.sb2-batch03.ids.csv`
   - `--prompt code/prompts/screen-A-v1.md`
   - `--model claude-opus-5-5`
   - `--run 1` (then `--run 2`)
   - `--out code/data/screening/llm/stream-a-v1.sb2-batch03.screen-A-v1.run1.jsonl` (then `run2`)
3. Print per run: decision, primary code and flags per record; errors, retries, model reported, Claude Code version, usage.
4. Then stop. Do not open or edit `stream-a-v1.snowball-r2.h1.csv`, `stream-a-v1.snowball-r2.qc.csv` or `stream-a-v1.snowball-r2.recheck-silent.csv`; do not edit the prompt, the script, the triage file or any other file; do not rebuild the triage. Commit nothing.
