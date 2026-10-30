# Smart-Meter Privacy Survey — project context

This folder holds two repositories for one IEEE Communications Surveys & Tutorials
submission on privacy inference from smart-meter data and derived artifacts.

- `paper/` — LaTeX manuscript, `bibliography.bib`, PDFs of included studies, legacy notes
  (`_Legacy/03_Literature_Summary`).
- `code/` — reproducible literature-search and screening pipeline (`survey_pipeline/`),
  query definitions (`queries/`), seed sets (`seeds/`), retrieved data (`data/`).
  Runs inside Docker (`docker compose run --rm privacy-survey ...`; `../paper` is mounted
  read-only at `/paper`).
- `docs/` — design documents both repos follow. Read before non-trivial work:
  `survey_design.md` (scope, privacy definition, RQs, streams, contributions, evidence
  dimensions, gaps, codebook mapping), `search_protocol.md` (per-stream search and
  eligibility protocol, PRISMA logging, change log), `screening_spec.md` (LLM-assisted
  screening schema and calibration).

## The survey in one paragraph

Attack- and data-centric survey of privacy in smart metering at operational resolutions
(15 min or coarser). Privacy is treated as **inferential information exposure**, not as
anonymity or access control: a leak occurs when access to a data artifact, aggregate, or
learned model raises an adversary's ability to infer protected information about a privacy
subject beyond prior and auxiliary knowledge. Privacy is separated from cybersecurity along
the chain **access mechanism → exposed artifact → privacy inference attack → disclosed
information → affected privacy subject**; eavesdropping and unauthorized access are
acquisition mechanisms, FDI/poisoning/evasion are integrity or robustness attacks unless
they directly enable disclosure. Three attack surfaces: data-level (raw, pseudonymized,
anonymized, perturbed, transformed measurements), aggregate-level (aggregates,
microaggregates, statistical outputs), model-level (models, parameters, gradients,
embeddings, representations). Privacy subjects: individuals, households, contributors,
groups, neighborhoods, feeders, regions. Six RQs are answered through streams A (survey
landscape), B (primary attack studies), C (attack-driven defenses). The contribution
chain the paper builds is **data-use context → exposed artifact → privacy attack → privacy
subject → empirical evidence → defense → grid utility**.

## Non-negotiable rules

1. **Never read, print, or copy `.env` or any API key.** Secrets are injected by docker-compose.
2. **Never invent a reference.** Cite only BibTeX keys that exist in `paper/bibliography.bib` and
   correspond to a record in the study corpus. If a claim needs a source not in the corpus,
   say so and leave `\todo{}`; never fabricate a key or DOI. This includes the conceptual
   foundations (Barker et al. 2009, LINDDUN, Pfitzmann–Hansen terminology, k-anonymity
   family, differential privacy): cite them only through keys that exist.
3. **Every search run is logged** through `survey_pipeline` (raw pages, compiled strings,
   `data/runs.csv`). No ad-hoc database queries from notebooks.
4. **Query definitions and prompts are versioned, never edited in place after a run.**
   New terms → new `query_id`/prompt version + entry in the change log.
5. **Screening and extraction outputs are structured JSON** with criteria codes,
   rationales, and (extraction) verbatim quotes with page numbers.
6. **Evidence limitations are not eligibility failures.** Small datasets, one region, weak
   external validation, or missing code never exclude a study; they are recorded in the
   evidence assessment.
7. **Evidence is assessed on four separate dimensions** — methodological validity, attack
   realism, generalizability, reproducibility — and never collapsed into one quality score.
8. **Do not overstate collective privacy.** Use "collective privacy" / "inferential group
   privacy" cautiously; empirical evidence is predominantly household-level and the text
   must say so.
9. **Do not change scope, RQs, definitions, or taxonomy wording** in `docs/` on your own;
   propose changes in a message. The privacy definition is marked *under construction*.
10. **Do not modify PDFs or `_Legacy/`.** They are inputs.

## Conventions

- Python 3.13 (container image `python:3.13-slim`), `requests`, `pytest`. Tests, from `code/`:
  `docker compose run --rm privacy-survey python -m pytest -q tests`.
- Data layout under `code/data/` is documented in `survey_pipeline/cli.py`. Commit
  `compiled/`, `reports/`, `runs.csv`, `normalized/*.jsonl`, `seeds/`. Raw API responses under
  `raw/` stay out of git. Manual exports that no API can re-fetch (`raw/acm/...`) are tracked
  (force-added past `.gitignore`), because they cannot be reproduced; `.gitattributes` marks
  `data/raw/**` as `-text` so git never rewrites their line endings.
- Record identity: DOI (lower-case) first, normalized title as fallback (`records.dedupe`).
- Retrieval stages, use these names: database search → record consolidation → eligibility
  screening → initial study corpus → supplementary discovery → re-screening → final corpus.
- Stream tags `A`, `B`, `C`; criteria codes `A-I1`, `A-E1`, `B-I1`, … (see `search_protocol.md`).
- Canonical privacy-objective labels (see `survey_design.md` §3; two open decisions there):
  re-identification & linkage · attribute inference · property inference (incl. group
  property) · membership / participation & contribution inference · reconstruction & model
  inversion · representation leakage.
- LaTeX: one sentence per line, `\gls{}` for defined acronyms, tables generated by scripts
  into `paper/tables/` and `\input`-ed, never hand-edited.
- Writing voice: formal, precise, hedged where evidence is thin. Prefer "reported",
  "demonstrated under", "evaluated on" over "proves", "shows that".

## Typical commands

```bash
cd code   # every command below runs as: docker compose run --rm privacy-survey <command>
python -m survey_pipeline.cli compile        queries/stream_a_v1.json
python -m survey_pipeline.cli search         queries/stream_a_v1.json --db ieee --dry-run
python -m survey_pipeline.cli search         queries/stream_a_v1.json --db ieee
python -m survey_pipeline.cli search         queries/stream_a_v1.json --db openalex   # or scopus
python -m survey_pipeline.cli import         queries/stream_a_v1.json --db acm --file acm.bib --hit-count N --bib /paper/bibliography.bib
python -m survey_pipeline.cli search         queries/stream_a_v1.json --db scopus --view STANDARD --page-size 25 --paging start
python -m survey_pipeline.cli backfill-abstracts queries/stream_a_v1.json --db scopus   # --from-run <run_id> replays without requests
python -m survey_pipeline.cli summarize      queries/stream_a_v1.json --bib /paper/bibliography.bib
python -m survey_pipeline.cli diagnose-seeds queries/stream_a_v1.json --bib /paper/bibliography.bib
python -m survey_pipeline.cli lookup         --title "Exact title"   # or --doi 10.1109/...
```

From Git Bash, prefix with `MSYS_NO_PATHCONV=1` so `/paper/...` is not rewritten to a
Windows path (see `code/README.md`).

## Current status

- Databases (`search_protocol.md` §1.5): IEEE Xplore, Scopus, OpenAlex (all API). Web of Science is
  not used (paid, no account; DECISION.md D14). ACM DL is searched by hand in the web UI, and all hits are exported
  as BibTeX and imported (D9, revised 2026-10-09).
- Stream A: `stream-a-v1` **frozen** (2026-09-28).
  - IEEE: done, 847 raw records.
  - OpenAlex: done, meta.count 921, 924 records.
  - Scopus: done 2026-10-09 (run 20261009T124109Z), STANDARD view, 37 requests, totalResults 911
    (dry run on 2026-09-28: 906), 911 records. Abstracts filled from OpenAlex by DOI (D15; backfill
    run 20261009T124359Z): 634 filled, 277 still missing (22 without DOI, 255 with a DOI that has
    no OpenAlex abstract, mostly Springer and Elsevier), flagged `abstract_missing`.
  - Merged IEEE + OpenAlex + Scopus + ACM: 1687 unique (screening sheet 1687 rows).
  - Abstract backfill for all flagged sheet records (2026-10-09, `backfill-abstracts --db all
    --sources crossref,semanticscholar`): of 280 flagged (265 with DOI), Crossref filled 0 (run
    20261009T133716Z; 258 DOIs registered, none with an abstract; publisher names stored), Semantic
    Scholar filled 42 (run 20261009T135100Z, unauthenticated: the configured key got 403).
    **238 still flagged `abstract_missing`** (15 without DOI), almost all Elsevier and Springer.
    `abstract_missing` is cleared only at >= 30 words.
  - Seed set: 16 seeds after D16 removed Abdalzaher22a, Avancini19a and Scheidt20a (not eligible).
  - Seeds retrieved on each database's own: IEEE 9/16, OpenAlex 12/16, Scopus 13/16, ACM 0/16.
  - Recall by expected source: ieee 9/9, scopus 4/4, snowballing 3 pending (Komninos14a,
    Mohassel14a, Eskandarnia22a, all metadata-unreachable). Overall 13/13 on evaluated seeds.
    Mohassel14a and Eskandarnia22a moved from scopus to snowballing (D17) after
    `diagnose-seeds --db scopus` (2026-10-09): both are in Scopus, but no privacy term appears in
    their title or keywords (Mohassel14a: nor in the OpenAlex abstract; Eskandarnia22a: no
    OpenAlex abstract to check).
- ACM DL: searched 2026-10-08/09, 77 hits, export in `data/raw/acm/stream-a-v1/20261008T131500Z/`. Imported: 77 entries, 74 unique; 22 already retrieved by IEEE or OpenAlex (21 by DOI, 1 by title); 52 new records added to the screening sheet (1551 rows before Scopus). After the Scopus merge, 41 ACM records remain as ACM rows; 11 are now kept under their Scopus id.
- Tooling: `diagnose-seeds` (IEEE DOI lookup, falls back to exact title), `lookup --doi|--title`,
  per-database seed hits in `summarize`, dry runs print the total count first.
- Two open decisions in `survey_design.md` §9 pending (representation leakage as
  objective vs. channel; canonical name for the membership row).

Update this section when a stage completes.
