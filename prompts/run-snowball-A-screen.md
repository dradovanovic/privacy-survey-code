# Instruction for Claude Code: Stream A snowballing, step 2 (F3 sheet, LLM-first screening, triage)

Use this after step 1 (`run-snowball-A-collect.md`, run 20261110T110809Z) and decision D21 (`docs/DECISION.md`): pre-filter F3, frozen prompt screen-A-v1 run twice, both-exclude records are excluded, both-include records are retained, everything else goes to H1.
Paste everything below the line into Claude Code, started in `D:\02_Projects\privacy-survey`.

---

Carry out the steps below in order. Read `docs/DECISION.md` D19 and D21 first.

**Rules.**
- Do not change `code/prompts/screen-A-v1.md`, `code/screening/run_llm_screen.py`, the query file, or any existing file under `code/data/screening/`. You only add the new files named below.
- No new API collection: build everything from `code/data/normalized/stream-a-v1.snowball.records.csv` of run 20261110T110809Z (abstract backfill in step 2 is the only exception and is logged in `runs.csv` like the earlier backfill).
- Never delete files. Commit nothing; show me the outputs, I commit myself. Never print or commit an API key.

**Step 1. F3 sheet.** With the existing `snowball.filter_flags` (no re-implementation), select the new works (`in_corpus = 0` and `already_screened = 0`) that pass F3. Expected: **1,372**. If the number differs, stop and tell me. Check that Mohassel14a (10.1016/j.ijepes.2014.06.025), Eskandarnia22a (10.1007/s42979-022-01161-6) and Komninos14a (10.1109/comst.2014.2320093) are among them.
Write `code/data/screening/stream-a-v1.snowball.screening-input.csv` in the format `run_llm_screen.py` reads (UTF-8 with BOM, comma, at least `record_id, doi, year, content_type, venue, title, abstract, abstract_source, keywords, url`), plus `n, n_corpus_links, corpus_ns, directions, sources`. Number the records `n` = 1688 onwards, ordered by `n_corpus_links` descending, then by title. `abstract_source` is the source that gave the abstract (`openalex` or `semanticscholar`), empty if there is none.

**Step 2. Abstract backfill.** For records with no abstract or one under 30 words, try to fill it by DOI with the existing clients, in this order: OpenAlex, Crossref, Semantic Scholar (the same sources and logging as `backfill-abstracts`). Write the abstract and its `abstract_source` into the sheet. Tell me how many were filled per source and how many remain without a usable abstract.

**Step 3. Batches.** Write ids files `code/data/screening/stream-a-v1.sb-batchNN.ids.csv` (columns `n, record_id`), 100 records each in `n` order (the last one smaller).

**Step 4. LLM runs.** Check that `code/prompts/screen-A-v1.md` has SHA-256 `df082ced81a8646e630811b84ffd4780665be4ff70ca4b3e9e65c5f475c00a53`; if not, stop. First run batch 01 with `--limit 5` as a smoke test into a scratch output outside `code/data/` and show me the 5 answers. Then, for every batch, run 1 and then run 2 with the unchanged script:
- `--sheet code/data/screening/stream-a-v1.snowball.screening-input.csv`
- `--ids code/data/screening/stream-a-v1.sb-batchNN.ids.csv`
- `--prompt code/prompts/screen-A-v1.md`
- `--model claude-opus-5-5`
- `--run 1` (then `--run 2`)
- `--out code/data/screening/llm/stream-a-v1.sb-batchNN.screen-A-v1.run1.jsonl` (then `run2`)
The script resumes from its output file, so rerun a batch if it is interrupted. A record whose answer could not be parsed after the script's retry counts as unclear in step 5.

**Step 5. Triage.** Write `code/data/screening/stream-a-v1.snowball.triage.csv` (';' delimiter, UTF-8 with BOM, CRLF), one row per record in `n` order, with columns:
`n; record_id; doi; title; year; venue; content_type; n_corpus_links; abstract_words; llm_run1; llm_run2; llm_rationale1; llm_rationale2; pile; qc_sample; h1_decision; h1_codes; h1_note; h1_at`
- `llm_run1` / `llm_run2`: decision, primary code, route and flags as one short string, e.g. `exclude A-E1 route=C` or `maybe ?A-I3 [abstract_missing]`.
- `pile`, by these rules in this order:
  1. `h1_no_abstract`: no abstract or under 30 words after step 2 (D19), whatever the LLM said;
  2. `excluded_llm`: both runs `exclude`;
  3. `retained_llm`: both runs `include`;
  4. `h1_unclear`: everything else (a `maybe` in either run, include vs exclude, or a parse error).
- `qc_sample`: 1 for a random 10 % of the `excluded_llm` records (rounded up), drawn with `random.Random(20261110).sample` over those records in `n` order; 0 otherwise.
- The `h1_*` columns stay empty.

**Step 6. Summary.** Write `code/data/reports/stream-a-v1.snowball.screen.md` with: records per pile; for `excluded_llm` the counts by run-1 primary code and how often the two runs give different codes; run-to-run agreement (same decision, same retain/exclude); abstract backfill counts; the pile and both LLM answers for the three seeds named in step 1; errors and retries; model reported, Claude Code version and total usage. Give me these numbers in your final message, with the list of files you created.
