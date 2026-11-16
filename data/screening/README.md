# Screening data, Stream A (`stream-a-v1`)

State: 16.11.2026. Corpus: 93 studies (83 database search, 10 snowballing round 1, 0 round 2). Numbers: `stream-a-v1.prisma.md`.
Every file here is part of the audit trail or is read by a script or an instruction in `code/prompts/`; file names must not change. Superseded versions and finished work lists are in `_archive/`. Raw LLM answers are in `llm/`.

## Results (start here)

| File | Content |
|---|---|
| `stream-a-v1.prisma.md` | PRISMA numbers for the database search and both snowballing rounds |
| `stream-a-v1.corpus-after-snowball1.csv` | The corpus: 93 studies |
| `stream-a-v1.corpus-initial.csv` | The 83 studies from the database search (start set of snowballing round 1) |
| `stream-a-v1.corpus-snowball1-new.csv` | The 10 studies added in round 1 (start set of round 2) |
| `stream-a-v1.ta-figures.md` | Title/abstract agreement figures, database search |

## Database search

| Files | Content |
|---|---|
| `stream-a-v1.csv`, `stream-a-v1.screening-input.csv`, `stream-a-v1.abstracts-manual.csv` | Deduplicated records (1,687), the sheet the LLM reads, abstracts added by hand |
| `stream-a-v1.batches.csv`, `stream-a-v1.pilot-selection.csv`, `stream-a-v1.pilot.md` | Batch assignment, pilot sample and pilot reading list |
| `stream-a-v1.h1.csv` | H1 title/abstract decisions |
| `stream-a-v1.pilot.compare.*`, `stream-a-v1.batchNN.compare.*` (01–17) | Title/abstract: H1 vs LLM, with reconciliation |
| `stream-a-v1.fulltext.csv`, `stream-a-v1.fulltext.md` | Full-text decisions with evidence (233 records) |
| `stream-a-v1.ft-pilot.*`, `stream-a-v1.ft-batchNN.input.csv`, `stream-a-v1.ft-batchNN.compare.*` (01–09) | Full text: LLM input and H1 vs LLM |

## Snowballing round 1 (D21)

| Files | Content |
|---|---|
| `stream-a-v1.snowball.screening-input.csv`, `.screening-input.abs-manual.csv`, `stream-a-v1.sb-batchNN.ids.csv` (01–16) | 1,372 records after pre-filter F3, abstracts added by hand, LLM batches |
| `stream-a-v1.snowball.triage.csv`, `.triage.abs-manual.csv` | LLM answers and piles |
| `stream-a-v1.snowball.h1.csv`, `.qc.csv`, `.recheck-silent.csv` | H1 decisions: open records, 10 % check sample, recheck of silent abstracts |
| `stream-a-v1.snowball.ta-final.csv` | Title/abstract result for all 1,372 records |
| `stream-a-v1.snowball.fulltext.csv` | Full-text decisions with evidence (64 records) |
| `stream-a-v1.sb-ft-batchNN.input.csv`, `stream-a-v1.sb-ft-batchNN.compare.*` (01–03, and `03-2949`) | Full text: LLM input and H1 vs LLM |

## Snowballing round 2 (D23)

| Files | Content |
|---|---|
| `stream-a-v1.snowball-r2.screening-input.csv`, `.screening-input.abs-manual.csv`, `stream-a-v1.sb2-batchNN.ids.csv` (01–03) | 115 records after pre-filter F3, abstracts added by hand, LLM batches |
| `stream-a-v1.snowball-r2.triage.csv` | LLM answers and piles |
| `stream-a-v1.snowball-r2.h1.csv`, `.qc.csv`, `.recheck-silent.csv` | H1 decisions: open records, check sample, recheck of A-E2 exclusions |
| `stream-a-v1.snowball-r2.ta-final.csv` | Title/abstract result for all 115 records |
| `stream-a-v1.snowball-r2.fulltext.csv` | Full-text decisions with evidence (10 records) |
| `stream-a-v1.sb2-ft-batch01.input.csv`, `stream-a-v1.sb2-ft-batch01.compare.*` | Full text: LLM input and H1 vs LLM |

## `_archive/`

Backups made before each edit (`*.before-<step>.*`), reading lists and ids files of finished title/abstract batches, retrieval lists, and the Excel copy of the first sheet. Nothing in it is read by a script. The backups are the only raw record of sheets before reconciliation (for example H1's blind codes), so they are kept under version control.
