# stream-a-v1: snowballed records, LLM-first title/abstract screening (D21)

Sheet `screening/stream-a-v1.snowball.screening-input.csv` (1372 records, n 1688-3059; new works of snowball run 20261110T110809Z passing F3). Prompt screen-A-v1, two runs per record, `screening/run_llm_screen.py` unchanged. Triage sheet `screening/stream-a-v1.snowball.triage.csv`.

## Records per pile

| pile | records |
|---|---|
| h1_no_abstract | 143 |
| excluded_llm | 1142 |
| retained_llm | 2 |
| h1_unclear | 85 |
| total | 1372 |

QC sample: 115 of 1142 `excluded_llm` records (10 %, rounded up; `random.Random(20261110).sample` over them in `n` order).

## `excluded_llm`: run-1 primary code

| primary code (run 1) | records |
|---|---|
| A-E1 | 316 |
| A-E2 | 259 |
| A-E3 | 538 |
| A-E4 | 26 |
| A-E6 | 3 |

Run 1 and run 2 give a different primary code: 73 of 1142.

| run 1 | run 2 | records |
|---|---|---|
| A-E2 | A-E3 | 33 |
| A-E3 | A-E2 | 28 |
| A-E1 | A-E2 | 4 |
| A-E2 | A-E1 | 3 |
| A-E1 | A-E3 | 3 |
| A-E3 | A-E1 | 1 |
| A-E3 | A-E6 | 1 |

## Run-to-run agreement

Retain = `include` or `maybe`, exclude = `exclude` (a `maybe` is not excluded under D21).

- all records: 1371 records with two parsed answers; same decision 1338 (0.976); same retain/exclude 1338 (0.976)
- records with an abstract of >= 30 words: 1228 records with two parsed answers; same decision 1200 (0.977); same retain/exclude 1200 (0.977)

| run 1 \ run 2 | include | maybe | exclude |
|---|---|---|---|
| include | 2 | 0 | 0 |
| maybe | 0 | 157 | 17 |
| exclude | 0 | 16 | 1179 |

## Abstract backfill

Backfill run 20261110T124642Z (by DOI, `backfill-abstracts` fetchers, logged in `runs.csv` as `abstract_backfill`): OpenAlex, then Semantic Scholar. Crossref was not asked: `CROSSREF_MAILTO` is not configured, and the author decided to skip it (it filled 0 of 258 abstracts in the main backfill of 2026-10-09).

Records needing an abstract before backfill (none or < 30 words): 150 (16 without DOI).

| abstract source | records |
|---|---|
| openalex | 1072 |
| semanticscholar | 152 |
| openalex_backfill | 2 |
| crossref | 0 |
| semantic_scholar | 5 |
| (none) | 141 |

Filled by backfill: OpenAlex 2, Crossref 0, Semantic Scholar 5. Still without a usable abstract: 143 (141 with none) = pile `h1_no_abstract`.

## Snowballing seeds

| seed | DOI | n | pile | run 1 | run 2 |
|---|---|---|---|---|---|
| Mohassel14a | 10.1016/j.ijepes.2014.06.025 | 1695 | h1_unclear | maybe ?A-I3 | maybe ?A-I3 |
| Eskandarnia22a | 10.1007/s42979-022-01161-6 | 1939 | h1_no_abstract | maybe ?A-I3 ?A-I4 [abstract_missing] | maybe ?A-I3 ?A-I4 [abstract_missing] |
| Komninos14a | 10.1109/comst.2014.2320093 | 1690 | h1_unclear | maybe ?A-I3 | maybe ?A-I2 ?A-I3 |

## Errors and retries

- answers: 2744 (1372 run 1, 1372 run 2)
- retried after a first-attempt error: 10; still an error after the retry: 1 (counted as unclear)
  - run 1 openalex:W4206151196: invalid JSON: Expecting value: line 1 column 1 (char 0) -> ok
  - run 1 openalex:W4317892895: invalid JSON: Expecting value: line 1 column 1 (char 0) -> ok
  - run 1 openalex:W4296047041: invalid JSON: Expecting value: line 1 column 1 (char 0) -> ok
  - run 1 openalex:W2075841394: invalid JSON: Expecting value: line 1 column 1 (char 0) -> ok
  - run 1 openalex:W3179533990: invalid JSON: Expecting value: line 1 column 1 (char 0) -> ok
  - run 1 openalex:W4226248372: invalid JSON: Expecting value: line 1 column 1 (char 0) -> ok
  - run 2 openalex:W2978973406: invalid JSON: Expecting value: line 1 column 1 (char 0) -> ok
  - run 2 openalex:W2097481773: invalid JSON: Expecting value: line 1 column 1 (char 0) -> ok
  - run 2 openalex:W2075841394: invalid JSON: Expecting value: line 1 column 1 (char 0) -> still: invalid JSON: Expecting value: line 1 column 1 (char 0)
  - run 2 openalex:W4407752957: invalid JSON: Expecting value: line 1 column 1 (char 0) -> ok

## Model, version, usage

- model requested: claude-opus-5-5; model reported: claude-opus-5-5 (2744)
- Claude Code version: 2.1.322 (Claude Code) (2744)
- prompt SHA-256: df082ced81a8646e630811b84ffd4780665be4ff70ca4b3e9e65c5f475c00a53 (2744)
- screened 2026-11-10T12:50:26+00:00 to 2026-11-10T14:04:54+00:00
- total usage: input tokens 5,488, cache creation 2,059,025, cache read 9,950,132, output tokens 1,123,129; reported cost 40.95 USD (list price; subscription login); summed call time 3.3 h

