# Instruction for Claude Code: Stream A snowballing, step 1 (seed update, collect, count)

Use this after the initial study corpus is fixed in `code/data/screening/stream-a-v1.corpus-initial.csv` (83 studies, all with a DOI; 10.11.2026).
Paste everything below the line into Claude Code, started in `D:\02_Projects\privacy-survey`.
This step only collects and counts. It builds no screening sheet and makes no eligibility decision; H1 decides the pre-filter from the counts (step 5) before anything is screened.

---

Carry out the steps below in order for Stream A (`stream-a-v1`). Read `docs/search_protocol.md` §1 (principles 6 and 7) and §5, and `docs/DECISION.md` D10, D16, D17 and D20 first.

**Rules.**
- Do not change the frozen query `code/queries/stream_a_v1.json`, the frozen prompts, or any file under `code/data/screening/` except the new files named below.
- Do not open `stream-a-v1.fulltext.csv`, `stream-a-v1.h1.csv` or any `*.compare.*` file; you do not need them. The corpus is `stream-a-v1.corpus-initial.csv`; the already-screened records are in `code/data/screening/stream-a-v1.csv` (use only `record_id`, `doi`, `title`).
- Every API call is logged in `code/data/runs.csv` in the existing format, and every raw response is saved under `code/data/raw/<source>/snowball/<run_id>/`, as the existing clients do. A run must be replayable from the raw files without new API calls.
- API keys come from the existing loaders; never print or commit a key. Use the polite pool / mailto settings already configured.
- Never delete files. Commit nothing; show me the diffs and the outputs, I commit myself.

**Step 1. Seed update (D20).** Remove the line for `Alahakoon16a` from `code/seeds/stream_a_seeds.txt` (keep a copy of the old file as `code/seeds/_archive/stream_a_seeds.before-D20.txt`). Regenerate the seed reports with the existing `summarize` command. Expected: 15 seeds; metadata-reachable 12/12; 3 pending (snowballing). Show me the seed section of the regenerated report. If the numbers differ, stop and tell me.

**Step 2. Add a `snowball` command.** Add it to `survey_pipeline` (new module plus a CLI entry; reuse `openalex_client.py`, `semanticscholar_client.py` and `records.py`, change existing behaviour of nothing else, add tests in `code/tests/`). For each DOI in the corpus file it collects:
- **backward** (the references of the corpus paper): OpenAlex `referenced_works`, and Semantic Scholar `paper/DOI:<doi>/references`;
- **forward** (the works citing the corpus paper): OpenAlex `filter=cites:<work id>` (all pages, cursor paging), and Semantic Scholar `paper/DOI:<doi>/citations` (all pages).
Resolve the retrieved works to the normalized record schema (title, DOI, year, type, language, venue, abstract where the source gives one). If a corpus DOI cannot be resolved in a source, log it and continue; list these at the end.
Write one edge file `code/data/normalized/stream-a-v1.snowball.edges.csv` with columns `corpus_n, corpus_doi, direction (backward|forward), source (openalex|semanticscholar), found_id, found_doi, found_title, found_year`.

**Step 3. Consolidate.** Deduplicate the found works across sources and directions by DOI, then by normalized title plus year (the same rule the pipeline already uses). Write `code/data/normalized/stream-a-v1.snowball.records.csv`, one row per unique work, with the normalized fields plus: `n_corpus_links` (how many corpus papers it is linked to), `directions`, `sources`, `in_corpus` (is one of the 83), `already_screened` (matches a record in `stream-a-v1.csv` by DOI or title).

**Step 4. Dry run first.** Before the full run, do a dry run on the first 3 corpus papers and show me the request counts and the number of works found per direction and source. Then run all 83.

**Step 5. Report, no filtering of the data.** Write `code/data/reports/stream-a-v1.snowball.md` with:
1. Per source and direction: corpus papers resolved, works found, API calls. Corpus papers not resolved, by `n`.
2. Unique works after consolidation; of these `in_corpus`, `already_screened`, and **new** (neither).
3. For the **new** works only, the counts under each of these nested filters, applied locally with the term lists and filters of `stream_a_v1.json` (same matching code as the local sensitivity variants):
   - F0: all new works;
   - F1: F0 with year 2009–2026, English (or language unknown), and a type the query allows (journal article, review, conference paper, book chapter; unknown type kept);
   - F2: F1 with a `secondary_research` term in the title, abstract or keywords;
   - F2t: F1 with a `secondary_research` term in the **title**;
   - F3: F2 with a `domain` term in the title, abstract or keywords;
   - F3t: F2t with a `domain` term in the title, abstract or keywords;
   - for F1, F3 and F3t also: how many have no abstract, and how many are linked to 1, 2, 3–4 and 5 or more corpus papers.
   The `privacy` group is deliberately not used as a filter: the three snowballing seeds fail exactly that group on metadata (D10, D17).
4. The three snowballing seeds, Mohassel14a (10.1016/j.ijepes.2014.06.025), Eskandarnia22a (10.1007/s42979-022-01161-6) and Komninos14a (10.1109/COMST.2014.2320093): for each, found or not, in which direction and source, linked to how many corpus papers, and which of F1, F2, F2t, F3, F3t it passes.
5. How much OpenAlex and Semantic Scholar overlap: works found by both, by OpenAlex only, by Semantic Scholar only (for backward and forward separately).

**Step 6. Tell me** the numbers of report items 2, 3 and 4 in your final message, any corpus paper that could not be resolved, any API error or rate limit you hit, and the list of files you created or changed. Do not build a screening sheet.
