# stream-a-v1: snowballed records (round 2), LLM-first title/abstract screening (D21, D23)

Sheet `screening/stream-a-v1.snowball-r2.screening-input.csv` (115 records, n 3060-3174; new works of snowball run 20261116T110934Z passing F3). Prompt screen-A-v1, two runs per record, `screening/run_llm_screen.py` unchanged. Triage sheet `screening/stream-a-v1.snowball-r2.triage.csv`.

## Records per pile

| pile | records |
|---|---|
| h1_no_abstract | 15 |
| excluded_llm | 92 |
| retained_llm | 0 |
| h1_unclear | 8 |
| total | 115 |

QC sample: 10 of 92 `excluded_llm` records (10 %, rounded up; `random.Random(20261116).sample` over them in `n` order).

## `excluded_llm`: run-1 primary code

| primary code (run 1) | records |
|---|---|
| A-E1 | 37 |
| A-E2 | 18 |
| A-E3 | 34 |
| A-E4 | 3 |

Run 1 and run 2 give a different primary code: 6 of 92.

| run 1 | run 2 | records |
|---|---|---|
| A-E1 | A-E3 | 2 |
| A-E2 | A-E3 | 2 |
| A-E3 | A-E2 | 1 |
| A-E2 | A-E4 | 1 |

## Run-to-run agreement

Retain = `include` or `maybe`, exclude = `exclude` (a `maybe` is not excluded under D21).

- all records: 114 records with two parsed answers; same decision 111 (0.974); same retain/exclude 111 (0.974)
- records with an abstract of >= 30 words: 99 records with two parsed answers; same decision 97 (0.980); same retain/exclude 97 (0.980)

| run 1 \ run 2 | include | maybe | exclude |
|---|---|---|---|
| include | 0 | 0 | 0 |
| maybe | 0 | 13 | 1 |
| exclude | 0 | 2 | 98 |

## Abstract backfill

Backfill run 20261116T111309Z (by DOI, `backfill-abstracts` fetchers, logged in `runs.csv` as `abstract_backfill`): OpenAlex, then Semantic Scholar. Crossref was not asked: `CROSSREF_MAILTO` is not configured, and the author decided to skip it (it filled 0 of 258 abstracts in the main backfill of 2026-10-09).

Records needing an abstract before backfill (none or < 30 words): 16 (2 without DOI).

| abstract source | records |
|---|---|
| openalex | 83 |
| semanticscholar | 16 |
| openalex_backfill | 0 |
| crossref | 0 |
| semantic_scholar | 1 |
| (none) | 15 |

Filled by backfill: OpenAlex 0, Crossref 0, Semantic Scholar 1. Still without a usable abstract: 15 (15 with none) = pile `h1_no_abstract`.

## Errors and retries

- answers: 230 (115 run 1, 115 run 2)
- retried after a first-attempt error: 3; still an error after the retry: 1 (counted as unclear)
  - run 1 openalex:W2899880163: invalid JSON: Expecting value: line 1 column 1 (char 0) -> ok
  - run 2 openalex:W2981785763: invalid JSON: Expecting value: line 1 column 1 (char 0) -> still: invalid JSON: Expecting value: line 1 column 1 (char 0)
  - run 2 openalex:W4412161828: invalid JSON: Expecting value: line 1 column 1 (char 0) -> ok

## Model, version, usage

- model requested: claude-opus-5-5; model reported: claude-opus-5-5 (230)
- Claude Code version: 2.1.325 (Claude Code) (230)
- prompt SHA-256: df082ced81a8646e630811b84ffd4780665be4ff70ca4b3e9e65c5f475c00a53 (230)
- screened 2026-11-16T11:13:29+00:00 to 2026-11-16T11:34:31+00:00
- total usage: input tokens 460, cache creation 182,385, cache read 830,731, output tokens 90,643; reported cost 3.44 USD (list price; subscription login); summed call time 0.3 h

