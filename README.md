# survey_pipeline

Reproducible literature-search pipeline for the smart-meter privacy survey.
Project context, rules and typical commands are in `../CLAUDE.md`; the data layout is
documented at the top of `survey_pipeline/cli.py`.

## Running

Everything runs in the `privacy-survey` container (Python 3.13). The API key comes from
`.env` through `docker-compose.yml`; `../paper` is mounted read-only at `/paper`.

```bash
docker compose run --rm privacy-survey python -m pytest -q tests
docker compose run --rm privacy-survey python -m survey_pipeline.cli summarize \
    queries/stream_a_v1.json --bib /paper/bibliography.bib
```

## ACM DL BibTeX import

ACM DL has no search API. Run the compiled ACM string (`data/compiled/<query_id>.md`) in the
Advanced Search UI, note the hit count, export every result page as BibTeX into a folder
under `code/` (the container sees only `code/` and `../paper`), then:

```bash
docker compose run --rm privacy-survey python -m survey_pipeline.cli import \
    queries/stream_a_v1.json --db acm --file acm_exports/p1.bib acm_exports/p2.bib \
    --hit-count 123 --bib /paper/bibliography.bib
```

If the run folder already exists (`data/raw/acm/<query_id>/<run_id>/` with the `.bib` files and a
`params.json` holding `query`, `hit_count`, `search_run_date_utc`, `start_year`/`end_year`,
`collection`), pass `--run-dir data/raw/acm/stream-a-v1/<run_id>` instead of `--file`/`--hit-count`.
The files are read in place, and `runs.csv` logs the search date and the UI query with its
collection and year filter. A run already in `runs.csv` is not logged again.

Otherwise the exports are copied to `data/raw/acm/`, one `runs.csv` row is logged per file, the overlap
with the API databases is written to `data/reports/<query_id>.acm.md`, and `summarize` runs
to regenerate the merged report, seed recall and screening sheet. In the merge, API records
win over ACM duplicates, so existing record ids in the screening sheet are kept.

## Git Bash on Windows: `MSYS_NO_PATHCONV`

Git Bash rewrites arguments that look like absolute POSIX paths into Windows paths
before `docker` sees them, so `--bib /paper/bibliography.bib` arrives in the container as
`C:/Program Files/Git/paper/bibliography.bib` and fails with `FileNotFoundError`.
Disable the conversion for the command:

```bash
MSYS_NO_PATHCONV=1 docker compose run --rm privacy-survey python -m survey_pipeline.cli \
    summarize queries/stream_a_v1.json --bib /paper/bibliography.bib
```

PowerShell and cmd do not rewrite paths and need no prefix.
