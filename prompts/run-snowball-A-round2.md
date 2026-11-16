# Instruction for Claude Code: Stream A snowballing, round 2 (collect, F3 sheet, LLM-first screening, triage)

Use this after round 1 is closed (16.11.2026) and decision D23 (`docs/DECISION.md`): the 10 studies that round 1 added are snowballed with the unchanged rules of D21.
Start set: `code/data/screening/stream-a-v1.corpus-snowball1-new.csv` (10 studies, all with a DOI; columns as in `corpus-initial.csv`).
Paste everything below the line into Claude Code, started in `D:\02_Projects\privacy-survey`.

---

Carry out the steps below in order for Stream A (`stream-a-v1`), snowballing round 2. Read `docs/DECISION.md` D19, D21 and D23 and the two round-1 instructions `code/prompts/run-snowball-A-collect.md` and `code/prompts/run-snowball-A-screen.md` first. Round 2 repeats round 1 on a new start set; everything not stated here is done as in round 1.

**Rules.**
- **No round-1 file is overwritten or changed.** This holds for every file under `code/data/normalized/`, `code/data/reports/`, `code/data/screening/` and `code/data/raw/`. Round-2 outputs use the names given below (`snowball-r2`, `sb2-batchNN`). Before you write a file, check that it does not exist; if it does, stop and tell me.
- Do not change the frozen query `code/queries/stream_a_v1.json`, the frozen prompt `code/prompts/screen-A-v1.md`, or `code/screening/run_llm_screen.py`.
- Do not open any of these files or their backups; you do not need them: `stream-a-v1.fulltext.csv`, `stream-a-v1.h1.csv`, `stream-a-v1.snowball.fulltext.csv`, `stream-a-v1.snowball.h1.csv`, `stream-a-v1.snowball.qc.csv`, `stream-a-v1.snowball.recheck-silent.csv`, `stream-a-v1.snowball.ta-final.csv`, `stream-a-v1.snowball.triage*.csv`, any `*.compare.*` file, anything in `code/data/screening/_archive/`.
- Every API call is logged in `code/data/runs.csv` in the existing format and every raw response is saved under `code/data/raw/<source>/snowball/<run_id>/`. A run must be replayable from the raw files without new API calls.
- API keys come from the existing loaders; never print or commit a key.
- Never delete files. Commit nothing; show me the diffs and the outputs, I commit myself.

**Step 1. Code changes (smallest possible, defaults unchanged).**
- `survey_pipeline snowball`: add an option `--tag` (default empty). With `--tag r2` the outputs are `code/data/normalized/stream-a-v1.snowball-r2.edges.csv`, `stream-a-v1.snowball-r2.records.csv` and `code/data/reports/stream-a-v1.snowball-r2.md`. Without the option the names are as now.
- Add an option `--seen` (repeatable): further CSV files whose works count as already seen (matched by DOI, then by normalized title plus year, the existing rule). The records file gets a new column `seen_round1` next to `in_corpus` and `already_screened`. Without the option nothing changes.
- `code/screening/sb_screen.py`: add an option `--round 2` to `prepare` and `triage` that switches the constants to the round-2 values named in steps 3 to 6 (file names, snowball run id, first `n`, QC seed, no expected F3 count, no seed check). Without the option the script behaves exactly as now.
- Add tests in `code/tests/` for the new options, and run the whole test suite. Show me that a replay of round 1 (`--from-run 20261110T110809Z`, written to a scratch directory outside `code/data/`) still gives 16,838 unique works and 16,369 new, and that `sb_screen.py` without `--round` still selects 1,372 records (also into scratch; do not write round-1 files).

**Step 2. Collect.** Dry run on the first 3 start papers and show me request counts and works found per direction and source. Then the full run:
`snowball queries/stream_a_v1.json --corpus data/screening/stream-a-v1.corpus-snowball1-new.csv --tag r2 --seen data/normalized/stream-a-v1.snowball.records.csv`
The start set (`--corpus`, 10 papers) and the corpus used for the `in_corpus` mark (93 studies) differ in round 2; add an option `--corpus-mark <csv>` for the latter (default: the `--corpus` file, so round 1 is unchanged) and pass `data/screening/stream-a-v1.corpus-after-snowball1.csv`. For the marks use these definitions:
- `in_corpus`: the work is one of the 93 studies in `code/data/screening/stream-a-v1.corpus-after-snowball1.csv`;
- `already_screened`: it matches a record in `code/data/screening/stream-a-v1.csv` (use only `record_id`, `doi`, `title`);
- `seen_round1`: it matches one of the 16,838 works in `code/data/normalized/stream-a-v1.snowball.records.csv`;
- **new**: none of the three.
If a start paper cannot be resolved in OpenAlex, stop and tell me. Semantic Scholar failures other than 404 are retried with `--retry-failed` as in round 1.
The report `stream-a-v1.snowball-r2.md` has the round-1 sections 1, 2, 3 and 5 (section 4 on seeds is left out), with `seen_round1` counted in section 2 and the nested filters F0 to F3t applied to the new works.

**Stop here and tell me the numbers if** the number of new works passing F3 is 0 or more than 400. Otherwise continue.

**Step 3. F3 sheet.** With the existing `snowball.filter_flags`, select the new works that pass F3. Write `code/data/screening/stream-a-v1.snowball-r2.screening-input.csv` in the round-1 format. Number the records `n` = 3060 onwards (round 1 ended at 3059), ordered by `n_corpus_links` descending, then by title.

**Step 4. Abstract backfill.** As in round 1 (OpenAlex, then Semantic Scholar; Crossref is skipped as in round 1 because `CROSSREF_MAILTO` is not configured). Tell me how many were filled per source and how many remain without a usable abstract (none, or under 30 words).

**Step 5. LLM runs.** Batches of 100 in `n` order: `code/data/screening/stream-a-v1.sb2-batchNN.ids.csv`. Check that `code/prompts/screen-A-v1.md` has SHA-256 `df082ced81a8646e630811b84ffd4780665be4ff70ca4b3e9e65c5f475c00a53`; if not, stop. For every batch run 1, then run 2, with the unchanged script: `--sheet code/data/screening/stream-a-v1.snowball-r2.screening-input.csv`, `--ids` the batch file, `--prompt code/prompts/screen-A-v1.md`, `--model claude-opus-5-5`, `--run 1` (then `--run 2`), `--out code/data/screening/llm/stream-a-v1.sb2-batchNN.screen-A-v1.run1.jsonl` (then `run2`).

**Step 6. Triage.** Write `code/data/screening/stream-a-v1.snowball-r2.triage.csv` with the round-1 columns, piles and rules (';' delimiter, UTF-8 with BOM, CRLF; the `h1_*` columns stay empty). `qc_sample`: 1 for a random 10 % of the `excluded_llm` records (rounded up), drawn with `random.Random(20261116).sample` over those records in `n` order.

**Step 7. Summary.** Write `code/data/reports/stream-a-v1.snowball-r2.screen.md` as in round 1 (without the seed section). In your final message give me: unique works, `in_corpus`, `already_screened`, `seen_round1`, new; the F0 to F3t counts; records per pile; run-to-run agreement; backfill counts; errors and retries; model reported, Claude Code version and total usage; and the list of files you created or changed.
