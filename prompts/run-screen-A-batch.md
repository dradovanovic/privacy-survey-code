# Instruction for Claude Code: LLM run on one main-run batch, screen-A-v1 (frozen)

Use this only after you have screened the batch yourself in `stream-a-v1.h1.csv`.
Paste everything below the line into Claude Code, started in `D:\02_Projects\privacy-survey`, and change `01` to the batch number.

---

Run the frozen screen-A-v1 prompt on batch 01, using the existing script `code/screening/run_llm_screen.py` unchanged.

**Hard rule: blinding.** Never open, read or reference `code/data/screening/stream-a-v1.h1.csv` or any `stream-a-v1.h1.before-*.csv` (including those in `code/data/screening/_archive/`). Do not compare anything with my decisions.

1. Check that `code/prompts/screen-A-v1.md` has SHA-256 `df082ced81a8646e630811b84ffd4780665be4ff70ca4b3e9e65c5f475c00a53`. If not, stop and tell me.
2. Run 1, then run 2, each with:
   - `--sheet code/data/screening/stream-a-v1.screening-input.csv`
   - `--ids code/data/screening/stream-a-v1.batch01.ids.csv`
   - `--prompt code/prompts/screen-A-v1.md`
   - `--model claude-opus-5-5`
   - `--run 1` (then `--run 2`)
   - `--out code/data/screening/llm/stream-a-v1.batch01.screen-A-v1.run1.jsonl` (then `run2`)
3. Print the same summary per run as for the pilot: decision counts, errors, retries, model reported, Claude Code version, usage.
4. Then stop. Do not edit the prompt or the script, and do not touch any other file.
