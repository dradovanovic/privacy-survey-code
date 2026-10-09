"""
survey_pipeline command line.

    python -m survey_pipeline.cli compile   queries/stream_a_v1.json [--db all]
    python -m survey_pipeline.cli search    queries/stream_a_v1.json --db ieee [--dry-run] [--max-pages N]
    python -m survey_pipeline.cli search    queries/stream_a_v1.json --db scopus [--dry-run] [--view COMPLETE|STANDARD]
    python -m survey_pipeline.cli search    queries/stream_a_v1.json --db openalex [--dry-run]
    python -m survey_pipeline.cli normalize queries/stream_a_v1.json --db ieee|scopus|openalex --run-id 2026...Z
    python -m survey_pipeline.cli import    queries/stream_a_v1.json --db acm --file acm1.bib [acm2.bib ...] --hit-count N
    python -m survey_pipeline.cli import    queries/stream_a_v1.json --db acm --run-dir data/raw/acm/stream-a-v1/<run_id>
    python -m survey_pipeline.cli summarize queries/stream_a_v1.json [--bib /paper/bibliography.bib]
    python -m survey_pipeline.cli diagnose-seeds queries/stream_a_v1.json   # one IEEE request per missed seed
    python -m survey_pipeline.cli lookup (--doi 10.1109/... | --title "Exact title")   # one logged IEEE request

All output lives under data/ (override with --data-dir):
    data/compiled/<query_id>.md            compiled strings for every database (supplement material)
    data/raw/<db>/<query_id>/<run_id>/     every raw API page, untouched
    data/raw/acm/<query_id>/<run_id>/      imported ACM DL BibTeX exports, untouched
    data/raw/ieee/lookup/                  raw DOI / title lookup responses
    data/normalized/<query_id>.<db>.jsonl  unified records
    data/reports/<query_id>.md             counts, variants, seed recall
    data/reports/<query_id>.acm.md         ACM import: overlap with the API databases, new records
    data/screening/<query_id>.csv          one row per unique record, ready for screening
    data/runs.csv                          request log (PRISMA numbers)
"""

from __future__ import annotations

import argparse
import collections
import csv
import json
import sys
from pathlib import Path

from . import query_compiler as qc
from . import records as rec


def _jsonl_read(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with open(path, encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def _db_order(path: Path) -> tuple[bool, str]:
    """API databases first (alphabetical), then imports (acm), so dedupe keeps API record ids."""
    db = path.name.rsplit(".", 2)[-2]
    return db not in API_DBS, db


def _load_normalized(data_dir: Path, qid: str) -> tuple[list[dict], set[str]]:
    """All normalized rows for a query, and the dbs searched (one file per db)."""
    rows: list[dict] = []
    searched: set[str] = set()
    for path in sorted((data_dir / "normalized").glob(f"{qid}.*.jsonl"), key=_db_order):
        rows += _jsonl_read(path)
        searched.add(path.name[len(qid) + 1:-len(".jsonl")])
    return rows, searched


def _fmt_recall(found: int, evaluated: int, recall: float | None) -> str:
    return f"{found}/{evaluated} seeds retrieved (recall = {recall:.2f})" if evaluated else "no seeds evaluated yet"


def _seed_recall_lines(rep: dict) -> list[str]:
    """Markdown lines: overall and per-source-db recall, missing and pending seeds."""
    lines = [f"- overall: {_fmt_recall(rep['n_found'], rep['n_evaluated'], rep['recall'])}; "
             f"{len(rep['pending'])} pending (source database not searched yet); "
             f"{rep['n_seeds']} seeds; searched: {', '.join(rep['searched_dbs']) or '—'}"]
    for db, d in sorted(rep["per_db"].items(), key=lambda kv: kv[0] or "~"):
        n_eval = len(d["found"]) + len(d["missing"])
        lines.append(f"- {db or 'untagged'}: {_fmt_recall(len(d['found']), n_eval, d['recall'])}"
                     + (f"; {len(d['pending'])} pending" if d["pending"] else ""))
    if rep["missing"]:
        lines += ["- missing:"] + [f"    - {m}" for m in rep["missing"]]
    if rep["pending"]:
        lines += ["- pending:"] + [f"    - {m}" for m in rep["pending"]]
    return lines


def _jsonl_write(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")


# ----------------------------------------------------------------------------
# compile
# ----------------------------------------------------------------------------

def cmd_compile(args) -> int:
    query = qc.load_query(args.query)
    targets = qc.COMPILERS if args.db == "all" else {args.db: qc.COMPILERS[args.db]}
    out_dir = Path(args.data_dir) / "compiled"
    out_dir.mkdir(parents=True, exist_ok=True)
    lines = [f"# Compiled search strings for `{query['query_id']}` (stream {query['stream']})", ""]
    for db, fn in targets.items():
        cq = fn(query)
        lines += [f"## {db}", "```", cq.display, "```"]
        for n in cq.notes:
            lines.append(f"- note: {n}")
        lines.append("")
        if db == "ieee":
            lines += ["API params:", "```json", json.dumps(cq.params, indent=2), "```", ""]
    variants = query.get("sensitivity_variants", {})
    if variants:
        lines += ["## Sensitivity variants (applied locally to the retrieved set)", ""]
        for name, spec in variants.items():
            lines.append(f"- **{name}**: {spec.get('description', '')}")
    text = "\n".join(lines)
    (out_dir / f"{query['query_id']}.md").write_text(text, encoding="utf-8")
    print(text)
    return 0


# ----------------------------------------------------------------------------
# search / normalize
# ----------------------------------------------------------------------------

API_DBS = ("ieee", "scopus", "openalex")   # databases wired to an API
IMPORT_DBS = ("acm",)                       # databases imported from UI exports


def _page_fns(db: str):
    """(page_items, normalize) for a database."""
    if db == "ieee":
        from .ieee_client import page_items
        return page_items, rec.normalize_ieee
    if db == "openalex":
        from .openalex_client import page_items
        return page_items, rec.normalize_openalex
    from .scopus_client import page_items
    return page_items, rec.normalize_scopus


def _normalize_run(db: str, query_id: str, run_dir: Path, run_id: str) -> list[dict]:
    page_items, normalize = _page_fns(db)
    rows = []
    for page in sorted(run_dir.glob("*_p*.json")):
        body = json.loads(page.read_text(encoding="utf-8"))
        for item in page_items(body):
            rows.append(normalize(item, query_id, run_id, str(page)))
    return rows


def _client(db: str, args, query: dict):
    """(client, page_total) for a database."""
    sleep = float(query.get("retrieval", {}).get("sleep_seconds", 1.0))
    if db == "ieee":
        from .ieee_client import IEEEClient, load_api_key, page_total
        return IEEEClient(load_api_key(), data_dir=args.data_dir, sleep_seconds=sleep), page_total
    if db == "openalex":
        from .openalex_client import OpenAlexClient, load_api_key, page_total
        return OpenAlexClient(load_api_key(), data_dir=args.data_dir, sleep_seconds=sleep), page_total
    from .scopus_client import ScopusClient, load_api_keys, page_total
    key, token = load_api_keys()
    return ScopusClient(key, token, data_dir=args.data_dir, view=args.view,
                        page_size=args.page_size, paging=args.paging, sleep_seconds=sleep), page_total


def cmd_search(args) -> int:
    if args.db not in API_DBS:
        print(f"only --db {' / '.join(API_DBS)} are wired to an API; use `compile` for the others",
              file=sys.stderr)
        return 2
    from .ieee_client import new_run_id

    query = qc.load_query(args.query)
    cq = qc.COMPILERS[args.db](query)
    client, page_total = _client(args.db, args, query)
    page_items, _ = _page_fns(args.db)
    run_id = new_run_id()
    max_pages = 1 if args.dry_run else args.max_pages
    totals: dict[str, int] = {}
    print(f"run_id={run_id}  query_id={query['query_id']}  db={args.db}  dry_run={args.dry_run}")
    pages = []
    for body, raw_path, ct in client.search(query["query_id"], cq.params, run_id=run_id, max_pages=max_pages):
        totals[ct] = page_total(body)
        pages.append(f"  {ct or 'all':<14} total_records={totals[ct]:>6}  returned={len(page_items(body)):>4}"
                     f"  cached -> {raw_path.name}")
        if not args.dry_run:
            print(pages[-1])
    if args.dry_run:
        print(f"TOTAL RESULTS: {sum(totals.values())}  (sum of total_records across content types)\n")
        print("\n".join(pages), "\n")
        print(cq.display)
        for n in cq.notes:
            print(f"- note: {n}")
        print("\ndry run: one page per content type retrieved; rerun without --dry-run to fetch all pages")
        return 0
    print(f"\nsum of total_records across content types: {sum(totals.values())}")
    run_dir = Path(args.data_dir) / "raw" / args.db / query["query_id"] / run_id
    rows = _normalize_run(args.db, query["query_id"], run_dir, run_id)
    out = Path(args.data_dir) / "normalized" / f"{query['query_id']}.{args.db}.jsonl"
    _jsonl_write(out, rows)
    print(f"normalized {len(rows)} records -> {out}")
    return 0


def cmd_normalize(args) -> int:
    if args.db not in API_DBS:
        print(f"--db must be one of {API_DBS}", file=sys.stderr)
        return 2
    query = qc.load_query(args.query)
    run_dir = Path(args.data_dir) / "raw" / args.db / query["query_id"] / args.run_id
    if not run_dir.exists():
        print(f"no such run: {run_dir}", file=sys.stderr)
        return 2
    rows = _normalize_run(args.db, query["query_id"], run_dir, args.run_id)
    out = Path(args.data_dir) / "normalized" / f"{query['query_id']}.{args.db}.jsonl"
    _jsonl_write(out, rows)
    print(f"normalized {len(rows)} records -> {out}")
    return 0


def _acm_run_dir_params(run_dir: Path, qid: str) -> tuple[dict, list[Path]] | str:
    """
    params.json and the .bib files of an existing ACM run folder
    (data/raw/acm/<query_id>/<run_id>/), or an error message.
    """
    if not run_dir.is_dir():
        return f"no such run folder: {run_dir}"
    if run_dir.parent.name != qid:
        return f"run folder {run_dir} is not under data/raw/acm/{qid}/"
    pfile = run_dir / "params.json"
    if not pfile.is_file():
        return f"{pfile} is missing"
    params = json.loads(pfile.read_text(encoding="utf-8"))
    absent = [k for k in ("query", "hit_count", "search_run_date_utc") if params.get(k) in (None, "")]
    if absent:
        return f"{pfile} lacks {', '.join(absent)}"
    files = [run_dir / f for f in params["files"]] if params.get("files") else sorted(run_dir.glob("*.bib"))
    missing = [str(f) for f in files if not f.is_file()]
    if missing or not files:
        return f"export files missing in {run_dir}: {', '.join(missing) or 'no .bib files'}"
    return params, files


def _acm_querytext(params: dict) -> str:
    """The UI query plus the settings the ACM query export does not record, as OpenAlex rows embed filters."""
    parts = [params["query"]]
    coll = "; ".join(v for v in (params.get("collection"), params.get("acm_filter")) if v)
    if coll:
        parts.append(f"collection: {coll}")
    if params.get("start_year") or params.get("end_year"):
        parts.append(f"publication_year: {params.get('start_year') or ''}-{params.get('end_year') or ''}")
    if params.get("content_type_filter"):
        parts.append(f"content_type: {params['content_type_filter']}")
    return " | ".join(parts)


def cmd_import(args) -> int:
    """
    Import ACM DL BibTeX exports. Two modes:

    --file F [F ...] --hit-count N   the exports are copied untouched to a new
        data/raw/acm/<query_id>/<run_id>/; runs.csv logs the import time and
        the compiled ACM string.
    --run-dir data/raw/acm/<query_id>/<run_id>   an existing run folder with
        params.json (query, hit_count, search_run_date_utc, year filter,
        collection) and the .bib files it lists; nothing is copied; runs.csv
        logs the search date and the UI query with its settings.

    One runs.csv row per file (total_records = the UI hit count, as API runs
    log the database's total); a run already in runs.csv is not logged again.
    Entries are normalized to data/normalized/<query_id>.acm.jsonl. The overlap
    with the API databases (by DOI, then normalized title) is written to
    data/reports/<query_id>.acm.md, then `summarize` regenerates the merged
    report, seed recall and screening sheet.
    """
    import shutil
    from datetime import datetime, timezone
    from .ieee_client import RUN_LOG_HEADER, new_run_id

    query = qc.load_query(args.query)
    qid = query["query_id"]
    data_dir = Path(args.data_dir)
    params: dict = {}
    if args.run_dir:
        run_dir = Path(args.run_dir)
        got = _acm_run_dir_params(run_dir, qid)
        if isinstance(got, str):
            print(got, file=sys.stderr)
            return 2
        params, files = got
        if args.hit_count is not None and args.hit_count != int(params["hit_count"]):
            print(f"--hit-count {args.hit_count} contradicts params.json hit_count {params['hit_count']}",
                  file=sys.stderr)
            return 2
        run_id, hit_count = run_dir.name, int(params["hit_count"])
        timestamp, querytext = params["search_run_date_utc"], _acm_querytext(params)
        raws = files
    else:
        if args.hit_count is None:
            print("--hit-count is required with --file", file=sys.stderr)
            return 2
        files = [Path(f) for f in args.file]
        for f in files:
            if not f.is_file():
                print(f"no such file: {f}", file=sys.stderr)
                return 2
        run_id, hit_count = new_run_id(), args.hit_count
        run_dir = data_dir / "raw" / args.db / qid / run_id
        run_dir.mkdir(parents=True)
        timestamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
        querytext = qc.COMPILERS[args.db](query).display
        raws = [run_dir / f"export_{i:03d}_{f.name}" for i, f in enumerate(files, 1)]
        for f, raw in zip(files, raws):
            shutil.copyfile(f, raw)

    run_log = data_dir / "runs.csv"
    new_log = not run_log.exists()
    logged = False
    if not new_log:
        with open(run_log, encoding="utf-8") as fh:
            logged = any(r["run_id"] == run_id and r["db"] == args.db for r in csv.DictReader(fh))
    rows: list[dict] = []
    per_file: list[tuple[Path, int]] = []
    for raw in raws:
        entries = rec.parse_bibtex(raw.read_text(encoding="utf-8"))
        rows += [rec.normalize_acm(e, qid, run_id, str(raw)) for e in entries]
        per_file.append((raw, len(entries)))
        print(f"  {raw.name}: {len(entries)} entries")
    if logged:
        print(f"run {run_id} is already in {run_log}; not logged again")
    else:
        with open(run_log, "a", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=RUN_LOG_HEADER)
            if new_log:
                w.writeheader()
            for raw, n in per_file:
                w.writerow({"timestamp": timestamp, "run_id": run_id, "db": args.db, "query_id": qid,
                            "content_type": "", "start_record": "", "max_records": "", "returned": n,
                            "total_records": hit_count, "status": "import", "querytext": querytext})
    out = data_dir / "normalized" / f"{qid}.{args.db}.jsonl"
    _jsonl_write(out, rows)
    types = collections.Counter(r["content_type"] for r in rows)
    print(f"run_id={run_id}  UI hit count={hit_count}  imported={len(rows)}  "
          f"({', '.join(f'{t} {n}' for t, n in types.most_common())})  -> {out}")
    if len(rows) != hit_count:
        print(f"note: {len(rows)} entries imported but the UI reported {hit_count} hits; "
              + (params.get("records_exported_note") or "check that every result page was exported"),
              file=sys.stderr)

    _write_import_report(data_dir, qid, args.db, run_id, len(raws), hit_count, rows)
    return cmd_summarize(args)


def _write_import_report(data_dir: Path, qid: str, db: str, run_id: str, n_files: int,
                         hit_count: int, rows: list[dict]) -> Path:
    """
    data/reports/<query_id>.<db>.md: overlap of the imported records with the
    API databases (by DOI, then normalized title), which is what the ACM spot
    check is about. Reads only the normalized files, so it can be regenerated
    without re-importing (e.g. after a corrected hit count).
    """
    api_rows, _ = _load_normalized(data_dir, qid)
    api_rows = [r for r in api_rows if r["db"] in API_DBS]
    dois = {r["doi"] for r in api_rows if r.get("doi")}
    titles = {rec.title_key(r["title"]) for r in api_rows}
    by_doi, by_title, new = [], [], []
    for r in rec.dedupe(rows)[0]:
        if r.get("doi") and r["doi"] in dois:
            by_doi.append(r)
        elif rec.title_key(r["title"]) in titles:
            by_title.append(r)
        else:
            new.append(r)
    types = collections.Counter(r["content_type"] for r in rows)
    lines = [f"# ACM DL import: `{qid}`", "",
             f"- run_id: {run_id}; files: {n_files}; UI hit count: {hit_count}",
             f"- entries imported: {len(rows)} ({', '.join(f'{t} {n}' for t, n in types.most_common())}); "
             f"unique within the export: {len(by_doi) + len(by_title) + len(new)}",
             f"- already retrieved by {', '.join(sorted({r['db'] for r in api_rows})) or '—'}: "
             f"{len(by_doi)} by DOI, {len(by_title)} by title",
             f"- not in the API databases: {len(new)}", "",
             "## Records not in the API databases", ""]
    lines += [f"- {r['record_id']} ({r.get('year') or '?'}, {r.get('venue') or '?'}): {r['title']}" for r in new]
    rep = data_dir / "reports" / f"{qid}.{db}.md"
    rep.parent.mkdir(parents=True, exist_ok=True)
    rep.write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines[2:6]) + f"\noverlap report -> {rep}\n")
    return rep


# ----------------------------------------------------------------------------
# summarize
# ----------------------------------------------------------------------------

def cmd_summarize(args) -> int:
    query = qc.load_query(args.query)
    qid = query["query_id"]
    data_dir = Path(args.data_dir)
    all_rows, searched = _load_normalized(data_dir, qid)
    if not all_rows:
        print(f"no normalized records for {qid}; run `search` first", file=sys.stderr)
        return 2

    unique, dropped = rec.dedupe(all_rows)
    per_db = collections.Counter(r["db"] for r in all_rows)
    per_ct = collections.Counter(r.get("content_type") or "?" for r in unique)
    per_year = collections.Counter(r.get("year") for r in unique)
    venues = collections.Counter(r.get("venue") or "?" for r in unique).most_common(15)

    # Does the record satisfy the query on title/abstract/keywords (with the
    # database's stemming approximated)? A second pass adds the venue name,
    # which IEEE's querytext also searches ("... Surveys & Tutorials").
    local_ok = [r for r in unique if rec.record_matches(query, r)]
    venue_ok = [r for r in unique if rec.record_matches(query, r, include_venue=True)]
    failing = collections.Counter()
    for r in unique:
        for g, ok in rec.group_matches(query, r, include_venue=True).items():
            if not ok:
                failing[g] += 1

    variant_counts = {}
    for name in query.get("sensitivity_variants", {}):
        vq = qc.apply_variant(query, name)
        variant_counts[name] = sum(1 for r in unique if rec.record_matches(vq, r))

    seed_report = None
    if query.get("seed_set"):
        seed_path = Path(args.query).parent.parent / query["seed_set"]
        if seed_path.exists():
            seeds = rec.load_seed_set(seed_path, args.bib)
            seed_report = rec.seed_recall(seeds, unique, searched)

    lines = [
        f"# Search report: `{qid}`", "",
        f"- raw records: {len(all_rows)}  ({dict(per_db)})",
        f"- unique after DOI/title dedupe: {len(unique)}  (dropped {len(dropped)})",
        f"- satisfy query locally on title/abstract/keywords: {len(local_ok)}",
        f"- satisfy query when the venue name is included: {len(venue_ok)} "
        f"(+{len(venue_ok) - len(local_ok)} via venue, e.g. survey journals)",
        f"- unexplained by title/abstract/keywords/venue: {len(unique) - len(venue_ok)} "
        f"(database-side stemming or index terms not exported)",
        "", "## Concept groups failing locally (incl. venue), across all unique records", "",
    ]
    lines += [f"- {g}: {n}" for g, n in failing.most_common()]
    lines += ["", "## Content types", ""]
    lines += [f"- {k}: {v}" for k, v in per_ct.most_common()]
    lines += ["", "## Years", ""]
    lines += [f"- {y}: {per_year[y]}" for y in sorted(k for k in per_year if k)]
    lines += ["", "## Top venues", ""]
    lines += [f"- {v}: {n}" for v, n in venues]
    if variant_counts:
        lines += ["", "## Sensitivity variants (unique records still matching)", ""]
        lines += [f"- {k}: {v}" for k, v in variant_counts.items()]
    if seed_report:
        lines += ["", "## Seed recall", ""] + _seed_recall_lines(seed_report)
        lines += ["", "Seeds retrieved by each searched database on its own (before dedupe; all seeds):", ""]
        for db, hit in rec.seed_hits_by_db(seeds, all_rows).items():
            miss = [sd["id"] for sd in seeds if sd["id"] not in hit]
            lines.append(f"- {db}: {len(hit)}/{len(seeds)}; not retrieved: {', '.join(miss) or '—'}")
        lines.append("")
        notes =[(sd["id"], sd["note"]) for sd in seeds if sd.get("note")]
        if notes:
            lines += ["- seed notes:"] + [f"    - {i}: {n}" for i, n in notes]
    text = "\n".join(lines)
    rep = data_dir / "reports" / f"{qid}.md"
    rep.parent.mkdir(parents=True, exist_ok=True)
    rep.write_text(text, encoding="utf-8")
    print(text)

    # Screening sheet: one row per unique record, decision columns empty.
    scr = data_dir / "screening" / f"{qid}.csv"
    scr.parent.mkdir(parents=True, exist_ok=True)
    cols = ["record_id", "db", "doi", "year", "content_type", "venue", "title", "abstract",
            "keywords", "citing_count", "url", "local_match", "venue_match",
            "decision", "criteria", "rationale", "screener"]
    with open(scr, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        ok_ids = {r["record_id"] for r in local_ok}
        venue_ids = {r["record_id"] for r in venue_ok}
        for r in sorted(unique, key=lambda r: (-(r.get("citing_count") or 0), r.get("year") or 0)):
            w.writerow({
                "record_id": r["record_id"], "db": r["db"], "doi": r.get("doi") or "",
                "year": r.get("year") or "", "content_type": r.get("content_type") or "",
                "venue": r.get("venue") or "", "title": r["title"], "abstract": r["abstract"],
                "keywords": "; ".join(r.get("keywords") or []), "citing_count": r.get("citing_count") or "",
                "url": r.get("url") or "", "local_match": int(r["record_id"] in ok_ids),
                "venue_match": int(r["record_id"] in venue_ids),
                "decision": "", "criteria": "", "rationale": "", "screener": "",
            })
    print(f"\nscreening sheet -> {scr}")
    return 0


# ----------------------------------------------------------------------------
# diagnose-seeds
# ----------------------------------------------------------------------------

def cmd_diagnose_seeds(args) -> int:
    """
    For every seed that the query did not retrieve: look it up in IEEE by DOI
    (one request each; a second, exact-title request when IEEE counts the DOI
    but returns no article) and report whether it is indexed at all, which content
    type / year it has, and which concept groups fail on its metadata. Splits
    'not in IEEE, expect it from another database' from 'in IEEE but missed
    by the query', which is the only kind of miss that should change the query.
    """
    from .ieee_client import COUNTED_NOT_RETURNED, IEEEClient, load_api_key

    query = qc.load_query(args.query)
    qid = query["query_id"]
    data_dir = Path(args.data_dir)
    seed_path = Path(args.query).parent.parent / query["seed_set"]
    seeds = rec.load_seed_set(seed_path, args.bib)
    rows, searched = _load_normalized(data_dir, qid)
    unique, _ = rec.dedupe(rows)
    report = rec.seed_recall(seeds, unique, searched)
    missing = [s for s in seeds if s["id"] in report["missing"]]

    client = IEEEClient(load_api_key(), data_dir=args.data_dir)
    filters = query.get("filters", {})
    allowed_ct = set(filters.get("content_types", {}).get("ieee", []))
    lines = [f"# Seed diagnosis: `{qid}`", "",
             f"retrieved {report['n_found']}/{report['n_evaluated']} evaluated seeds; "
             f"{len(report['pending'])} pending (source database not searched yet); "
             f"diagnosing {len(missing)} missing", ""]
    verdicts = collections.Counter()
    for s in missing:
        lines.append(f"## {s['id']}  —  {s.get('title') or ''}")
        if not s.get("doi"):
            lines += ["- no DOI in seed file; cannot look up. Add the DOI or check the other databases.", ""]
            verdicts["no doi"] += 1
            continue
        item = client.lookup_doi(s["doi"], query_id=qid)
        if item is None:
            lines += [f"- **not indexed in IEEE Xplore** (doi {s['doi']}). Expect it from Scopus / OpenAlex / ACM.", ""]
            verdicts["not in IEEE"] += 1
            continue
        if item.get("_status") == COUNTED_NOT_RETURNED:
            lines.append(f"- DOI lookup counted a match but returned no article (raw: {item['_raw']}); "
                         "falling back to exact-title lookup")
            item = client.lookup_title(s.get("title") or "", doi=s["doi"], query_id=qid) if s.get("title") else None
            if item is None:
                lines += ["- **in IEEE, but neither DOI nor title lookup returned the record**; "
                          "check it in the Xplore web UI.", ""]
                verdicts["in IEEE, not returned"] += 1
                continue
        r = rec.normalize_ieee(item, qid, "lookup", "lookup")
        gm = rec.group_matches(query, r, include_venue=True)
        failed = [g for g, ok in gm.items() if not ok]
        lines.append(f"- in IEEE: {r['year']} · {r.get('content_type')} · {r.get('venue')}")
        if r.get("content_type") and allowed_ct and r["content_type"] not in allowed_ct:
            lines.append(f"- **content type '{r['content_type']}' is outside the query filter** {sorted(allowed_ct)}")
            verdicts["filtered by content type"] += 1
        elif r.get("year") and ("start_year" in filters and r["year"] < filters["start_year"]):
            lines.append("- **year is outside the query filter**")
            verdicts["filtered by year"] += 1
        elif failed:
            lines.append(f"- **concept group(s) not satisfied on title/abstract/keywords/venue:** {failed}")
            for g in failed:
                lines.append(f"    - `{g}` terms absent; abstract starts: “{(r['abstract'] or '')[:220]}…”")
            lines.append(f"    - keywords: {', '.join(r['keywords'][:12]) or '—'}")
            verdicts["in IEEE, terminology miss"] += 1
        else:
            lines.append("- all groups match locally but the record was not retrieved: "
                         "re-check the compiled string in the Dynamic Query Tool or the year filter")
            verdicts["in IEEE, unexplained"] += 1
        lines.append("")
    lines += ["## Verdicts", ""] + [f"- {k}: {v}" for k, v in verdicts.most_common()]
    text = "\n".join(lines)
    out = data_dir / "reports" / f"{qid}.seeds.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")
    print(text)
    return 0


# ----------------------------------------------------------------------------
# lookup
# ----------------------------------------------------------------------------

def cmd_lookup(args) -> int:
    """One logged IEEE lookup by DOI or exact title; prints the raw response."""
    from .ieee_client import IEEEClient, load_api_key

    client = IEEEClient(load_api_key(), data_dir=args.data_dir)
    if args.doi:
        client.lookup_doi(args.doi, query_id=args.query_id)
    else:
        client.lookup_title(args.title, query_id=args.query_id)
    print(client.last_raw.read_text(encoding="utf-8"))
    print(f"raw -> {client.last_raw}", file=sys.stderr)
    return 0


# ----------------------------------------------------------------------------

def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="survey_pipeline")
    p.add_argument("--data-dir", default="data")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("compile"); s.add_argument("query"); s.add_argument("--db", default="all",
                                                                        choices=["all", *qc.COMPILERS])
    s.set_defaults(fn=cmd_compile)
    s = sub.add_parser("search"); s.add_argument("query"); s.add_argument("--db", default="ieee")
    s.add_argument("--dry-run", action="store_true"); s.add_argument("--max-pages", type=int, default=None)
    s.add_argument("--view", default="COMPLETE", choices=["COMPLETE", "STANDARD"],
                   help="Scopus only: COMPLETE has abstracts/keywords (needs entitlement), STANDARD does not")
    s.add_argument("--page-size", type=int, default=25,
                   help="Scopus only: records per request (25 without a subscription; STANDARD up to 200)")
    s.add_argument("--paging", choices=["cursor", "start"], default=None,
                   help="Scopus only: default cursor with SCOPUS_INST_TOKEN, start otherwise")
    s.set_defaults(fn=cmd_search)
    s = sub.add_parser("normalize"); s.add_argument("query"); s.add_argument("--db", default="ieee")
    s.add_argument("--run-id", required=True); s.set_defaults(fn=cmd_normalize)
    s = sub.add_parser("import", help="import UI exports (ACM DL BibTeX), then summarize")
    s.add_argument("query"); s.add_argument("--db", required=True, choices=IMPORT_DBS)
    g = s.add_mutually_exclusive_group(required=True)
    g.add_argument("--file", nargs="+", help="BibTeX export file(s) of one search; copied to a new run folder")
    g.add_argument("--run-dir", help="existing data/raw/acm/<query_id>/<run_id>/ with params.json; read in place")
    s.add_argument("--hit-count", type=int, default=None,
                   help="result count shown in the database UI (PRISMA records identified); "
                        "required with --file, read from params.json with --run-dir")
    s.add_argument("--bib", default=None, help="paper .bib for resolving key: seeds, as in summarize")
    s.set_defaults(fn=cmd_import)
    s = sub.add_parser("summarize"); s.add_argument("query"); s.add_argument("--bib", default=None)
    s.set_defaults(fn=cmd_summarize)
    s = sub.add_parser("diagnose-seeds"); s.add_argument("query"); s.add_argument("--bib", default=None)
    s.set_defaults(fn=cmd_diagnose_seeds)
    s = sub.add_parser("lookup"); g = s.add_mutually_exclusive_group(required=True)
    g.add_argument("--doi"); g.add_argument("--title")
    s.add_argument("--query-id", default="manual-lookup", help="query_id recorded in runs.csv")
    s.set_defaults(fn=cmd_lookup)

    args = p.parse_args(argv)
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
