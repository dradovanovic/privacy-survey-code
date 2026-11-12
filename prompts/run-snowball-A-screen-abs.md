# Instruction for Claude Code: Stream A snowballing, step 2b (LLM runs on records with a manually added abstract)

Use this after H1 has added abstracts by hand for the `h1_no_abstract` records (10.11.2026). 137 records now have an abstract of at least 30 words; they are in `code/data/screening/stream-a-v1.snowball.screening-input.abs-manual.csv` (same columns as the snowball sheet, `abstract_source = manual`) and in the ids files `stream-a-v1.sb-batch15.ids.csv` (69) and `stream-a-v1.sb-batch16.ids.csv` (68). Under D21 they are screened like every other snowballed record.
Paste everything below the line into Claude Code, started in `D:\02_Projects\privacy-survey`.

---

Run the frozen screen-A-v1 prompt on snowball batches 15 and 16, using the existing script `code/screening/run_llm_screen.py` unchanged.

1. Check that `code/prompts/screen-A-v1.md` has SHA-256 `df082ced81a8646e630811b84ffd4780665be4ff70ca4b3e9e65c5f475c00a53`. If not, stop and tell me.
2. For batch 15 and then batch 16, run 1 and then run 2, each with:
   - `--sheet code/data/screening/stream-a-v1.snowball.screening-input.abs-manual.csv`
   - `--ids code/data/screening/stream-a-v1.sb-batchNN.ids.csv`
   - `--prompt code/prompts/screen-A-v1.md`
   - `--model claude-opus-5-5`
   - `--run 1` (then `--run 2`)
   - `--out code/data/screening/llm/stream-a-v1.sb-batchNN.screen-A-v1.run1.jsonl` (then `run2`)
3. Print per run: decision counts, errors, retries, model reported, Claude Code version, usage.
4. Then stop. Do not edit the prompt, the script, the triage file, `stream-a-v1.snowball.h1.csv`, `stream-a-v1.snowball.qc.csv` or any other file; do not rebuild the triage. Commit nothing.
