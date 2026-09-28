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
