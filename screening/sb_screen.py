#!/usr/bin/env python3
"""Stream A snowballing, step 2: F3 sheet, abstract backfill, batches, triage (DECISION.md D21).

Instruction: code/prompts/run-snowball-A-screen.md.

    prepare  (in Docker, from code/):  python screening/sb_screen.py prepare
             Replays snowball run 20261110T110809Z from its raw files (no requests),
             selects the new works passing F3 with snowball.filter_flags, writes the
             screening-input sheet (n = 1688 onwards), backfills missing abstracts by
             DOI (OpenAlex, Crossref, Semantic Scholar; the backfill-abstracts fetchers,
             logged in runs.csv; --backfill-run <run_id> replays the sources saved
             under that run and requests the others; --skip-backfill-source leaves
             a source out), and writes the batch ids files.
             Run 2026-11-10: prepare --backfill-run 20261110T124642Z --skip-backfill-source crossref
             (CROSSREF_MAILTO not configured; Crossref skipped by the user's decision).
    triage   (stdlib only, from code/): python screening/sb_screen.py triage
             Reads the sheet and the run1/run2 jsonl files of run_llm_screen.py and
             writes the triage sheet and the summary report.
"""

from __future__ import annotations

import argparse
import collections
import csv
import hashlib
import json
import math
import random
import sys
from pathlib import Path

CODE = Path(__file__).resolve().parent.parent
QUERY = CODE / "queries" / "stream_a_v1.json"
DATA = CODE / "data"
QID = "stream-a-v1"
SNOWBALL_RUN = "20261110T110809Z"
SHEET = DATA / "screening" / f"{QID}.snowball.screening-input.csv"
TRIAGE = DATA / "screening" / f"{QID}.snowball.triage.csv"
REPORT = DATA / "reports" / f"{QID}.snowball.screen.md"
LLM_DIR = DATA / "screening" / "llm"
PROMPT_VERSION = "screen-A-v1"
EXPECTED_F3 = 1372
FIRST_N = 1688
BATCH = 100
MIN_WORDS = 30
QC_SEED = 20261110
SEEDS = {"Mohassel14a": "10.1016/j.ijepes.2014.06.025", "Eskandarnia22a": "10.1007/s42979-022-01161-6",
         "Komninos14a": "10.1109/comst.2014.2320093"}
SHEET_COLUMNS = ["record_id", "db", "doi", "year", "content_type", "venue", "title", "abstract", "abstract_source",
                 "flags", "keywords", "url", "n", "n_corpus_links", "corpus_ns", "directions", "sources"]
TRIAGE_COLUMNS = ["n", "record_id", "doi", "title", "year", "venue", "content_type", "n_corpus_links",
                  "abstract_words", "llm_run1", "llm_run2", "llm_rationale1", "llm_rationale2", "pile",
                  "qc_sample", "h1_decision", "h1_codes", "h1_note", "h1_at"]
PILES = ("h1_no_abstract", "excluded_llm", "retained_llm", "h1_unclear")
BACKFILL_ORDER = ("openalex", "crossref", "semanticscholar")
BACKFILL_RUN = "20261110T124642Z"
BACKFILL_NOTE = ("Crossref was not asked: `CROSSREF_MAILTO` is not configured, and the author decided to skip it "
                 "(it filled 0 of 258 abstracts in the main backfill of 2026-10-09).")


def words(text: str) -> int:
    return len((text or "").split())


def batch_path(k: int) -> Path:
    return DATA / "screening" / f"{QID}.sb-batch{k:02d}.ids.csv"


def jsonl_path(k: int, run: int) -> Path:
    return LLM_DIR / f"{QID}.sb-batch{k:02d}.{PROMPT_VERSION}.run{run}.jsonl"


# ----------------------------------------------------------------------------
# prepare (steps 1-3)
# ----------------------------------------------------------------------------

def replay_records(query: dict) -> tuple[list[dict], list[list[dict]]]:
    """build_records of the snowball run from its raw files, plus the member works of each record."""
    from survey_pipeline import snowball as sb
    corpus_path = DATA / "screening" / f"{QID}.corpus-initial.csv"
    corpus = sb.load_corpus(corpus_path)
    edges, found = [], {}
    for s in sb.SOURCES:
        e, f, _ = sb.READERS[s](DATA / "raw" / s / "snowball" / SNOWBALL_RUN, corpus, QID, SNOWBALL_RUN)
        edges += e
        found.update(f)
    records = sb.build_records(found, edges, corpus, sb.load_screened(DATA / "screening" / f"{QID}.csv"))
    groups, _ = sb.consolidate(found)            # build_records emits one record per group, in group order
    if len(groups) != len(records):
        sys.exit("consolidate and build_records disagree; stop")
    for r, keys in zip(records, groups):
        if not r["record_id"]:   # only Semantic Scholar references without a paperId (title and year only)
            r["record_id"] = "s2-unmatched:" + hashlib.sha1(keys[0].encode("utf-8")).hexdigest()[:12]
    return records, [[found[k] for k in keys] for keys in groups]


def abstract_source(members: list[dict], abstract: str) -> str:
    """The source of the abstract build_records chose (the first member with the longest one)."""
    if not abstract:
        return ""
    best = max(members, key=lambda m: words(m.get("abstract") or ""))
    return best["db"]


def write_sheet(rows: list[dict]) -> None:
    with open(SHEET, "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=SHEET_COLUMNS, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def cmd_prepare(a) -> int:
    from survey_pipeline import query_compiler as qc
    from survey_pipeline import records as rec
    from survey_pipeline import snowball as sb
    from survey_pipeline.cli import BACKFILL_FETCH, SOURCE_LABEL
    from survey_pipeline.ieee_client import new_run_id

    query = qc.load_query(str(QUERY))
    records, members = replay_records(query)
    with open(DATA / "normalized" / f"{QID}.snowball.records.csv", encoding="utf-8-sig", newline="") as fh:
        saved = {(r["record_id"], r["title"]) for r in csv.DictReader(fh)}
    replayed = {("" if r["record_id"].startswith("s2-unmatched:") else r["record_id"], sb._one_line(r["title"]))
                for r in records}
    if replayed != saved:
        print(f"replay differs from records.csv: {len(replayed ^ saved)} rows; stop")
        return 2
    print(f"replayed run {SNOWBALL_RUN}: {len(records)} records, identical to {QID}.snowball.records.csv")

    sel = []
    for r, ms in zip(records, members):
        if r["in_corpus"] or r["already_screened"]:
            continue
        if sb.filter_flags(query, r)["F3"]:
            sel.append((r, ms))
    print(f"step 1: new works passing F3: {len(sel)} (expected {EXPECTED_F3})")
    if len(sel) != EXPECTED_F3:
        print("count differs; stop")
        return 2
    sel_dois = {d for r, _ in sel for d in r["dois"]}
    for name, doi in SEEDS.items():
        print(f"  seed {name} ({doi}): {'in the F3 set' if doi in sel_dois else 'MISSING'}")
    if not all(d in sel_dois for d in SEEDS.values()):
        return 2

    sel.sort(key=lambda t: (-t[0]["n_corpus_links"], sb._one_line(t[0]["title"]).casefold(), t[0]["record_id"]))
    rows = []
    for i, (r, ms) in enumerate(sel):
        ab = sb._one_line(r["abstract"])
        rows.append({
            "record_id": r["record_id"], "db": {"s2-unmatched": "semanticscholar"}.get(r["record_id"].split(":")[0], r["record_id"].split(":")[0]), "doi": r["doi"],
            "year": r["year"] or "", "content_type": r["content_type"], "venue": sb._one_line(r["venue"]),
            "title": sb._one_line(r["title"]), "abstract": ab, "abstract_source": abstract_source(ms, r["abstract"]),
            "flags": "", "keywords": sb._one_line("; ".join(r["keywords"])),
            "url": next((m["url"] for m in ms if m.get("url")), "") or "",
            "n": FIRST_N + i, "n_corpus_links": r["n_corpus_links"],
            "corpus_ns": "; ".join(str(n) for n in r["corpus_ns"]),
            "directions": "; ".join(r["directions"]), "sources": "; ".join(r["sources"]),
        })
    if len({r["record_id"] for r in rows}) != len(rows) or not all(r["record_id"] for r in rows):
        print("record ids not unique or empty; stop")
        return 2
    for r in rows:
        r["flags"] = "abstract_missing" if words(r["abstract"]) < MIN_WORDS else ""
    write_sheet(rows)
    print(f"  sheet -> {SHEET.relative_to(CODE)} ({len(rows)} rows, n {rows[0]['n']}-{rows[-1]['n']}); "
          f"abstract from openalex {sum(r['abstract_source'] == 'openalex' for r in rows)}, "
          f"semanticscholar {sum(r['abstract_source'] == 'semanticscholar' for r in rows)}, "
          f"none {sum(not r['abstract'] for r in rows)}; under {MIN_WORDS} words (incl. none) "
          f"{sum(words(r['abstract']) < MIN_WORDS for r in rows)}")

    # step 2: backfill
    targets = [r for r in rows if rec.needs_abstract(r)]
    run_id = a.backfill_run or new_run_id()
    skip = {s.strip() for s in (a.skip_backfill_source or "").split(",") if s.strip()}
    print(f"step 2: backfill run {run_id}: {len(targets)} records "
          f"need an abstract ({sum(1 for r in targets if r['doi'])} with DOI)")
    for r in targets:
        r["flags"] = ["abstract_missing"]
    filled = {}
    for src in BACKFILL_ORDER:
        dois = sorted({r["doi"] for r in targets if r["doi"] and rec.needs_abstract(r)})
        if src in skip:
            print(f"  {src}: skipped (--skip-backfill-source)")
            continue
        # a source already saved under this run is replayed (no requests); otherwise it is requested now
        replay = (DATA / "raw" / src / "backfill" / run_id).is_dir()
        if not dois:
            filled[src] = 0
            continue
        print(f"  {src}: {'replay of saved responses' if replay else 'live'}")
        by_doi, _ = BACKFILL_FETCH[src](dois, QID, run_id, DATA, query, replay)
        by_doi = {d: sb._one_line(t) for d, t in by_doi.items()}
        filled[src] = rec.fill_abstracts(targets, by_doi, SOURCE_LABEL[src])
        print(f"  {src}: {len(dois)} DOIs asked, {filled[src]} abstracts filled")
    for r in targets:
        r["flags"] = "; ".join(r["flags"])
    still = [r for r in rows if rec.needs_abstract(r)]
    write_sheet(rows)
    print(f"  filled: {', '.join(f'{s} {n}' for s, n in filled.items())}; still without a usable abstract "
          f"(none or < {MIN_WORDS} words): {len(still)} ({sum(not r['abstract'] for r in still)} with none, "
          f"{sum(1 for r in still if not r['doi'])} without DOI)")

    # step 3: batches
    k = 0
    for k, start in enumerate(range(0, len(rows), BATCH), 1):
        with open(batch_path(k), "w", newline="", encoding="utf-8-sig") as fh:
            w = csv.writer(fh)
            w.writerow(["n", "record_id"])
            w.writerows([r["n"], r["record_id"]] for r in rows[start:start + BATCH])
    print(f"step 3: {k} batch files, {batch_path(1).name} .. {batch_path(k).name}")
    return 0


# ----------------------------------------------------------------------------
# triage (steps 5-6)
# ----------------------------------------------------------------------------

def load_jsonl(path: Path) -> dict[str, dict]:
    out = {}
    if path.exists():
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                if line.strip():
                    d = json.loads(line)
                    out[d["record_id"]] = d          # a resumed run appends; the last line counts
    return out


def answer_string(d: dict | None) -> str:
    if d is None:
        return "MISSING"
    p = d.get("parsed")
    if not p:
        return "ERROR"
    parts = [p["decision"]]
    if p.get("primary_code"):
        parts.append(p["primary_code"])
    elif p["decision"] != "include" and p.get("criteria_unclear"):
        parts += ["?" + c for c in p["criteria_unclear"]]
    if p.get("route"):
        parts.append(f"route={p['route']}")
    if p.get("flags"):
        parts.append("[" + ", ".join(p["flags"]) + "]")
    return " ".join(parts)


def decision(d: dict | None) -> str | None:
    return ((d or {}).get("parsed") or {}).get("decision")


def cmd_triage(a) -> int:
    with open(SHEET, encoding="utf-8-sig", newline="") as fh:
        rows = sorted(csv.DictReader(fh), key=lambda r: int(r["n"]))
    nb = math.ceil(len(rows) / BATCH)
    runs = {1: {}, 2: {}}
    for k in range(1, nb + 1):
        for run in (1, 2):
            runs[run].update(load_jsonl(jsonl_path(k, run)))
    missing = [r["record_id"] for r in rows if r["record_id"] not in runs[1] or r["record_id"] not in runs[2]]
    if missing and not a.allow_missing:
        print(f"{len(missing)} records lack a run-1 or run-2 answer, e.g. {missing[:5]}; stop")
        return 2

    out = []
    for r in rows:
        d1, d2 = runs[1].get(r["record_id"]), runs[2].get(r["record_id"])
        dec1, dec2 = decision(d1), decision(d2)
        if words(r["abstract"]) < MIN_WORDS:
            pile = "h1_no_abstract"
        elif dec1 == dec2 == "exclude":
            pile = "excluded_llm"
        elif dec1 == dec2 == "include":
            pile = "retained_llm"
        else:
            pile = "h1_unclear"
        out.append({"n": r["n"], "record_id": r["record_id"], "doi": r["doi"], "title": r["title"],
                    "year": r["year"], "venue": r["venue"], "content_type": r["content_type"],
                    "n_corpus_links": r["n_corpus_links"], "abstract_words": words(r["abstract"]),
                    "llm_run1": answer_string(d1), "llm_run2": answer_string(d2),
                    "llm_rationale1": ((d1 or {}).get("parsed") or {}).get("rationale", ""),
                    "llm_rationale2": ((d2 or {}).get("parsed") or {}).get("rationale", ""),
                    "pile": pile, "qc_sample": 0, "h1_decision": "", "h1_codes": "", "h1_note": "", "h1_at": "",
                    "_d1": d1, "_d2": d2, "_doi": r["doi"].lower()})
    excl = [o for o in out if o["pile"] == "excluded_llm"]
    k_qc = math.ceil(len(excl) / 10)
    for o in random.Random(QC_SEED).sample(excl, k_qc):
        o["qc_sample"] = 1
    with open(TRIAGE, "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=TRIAGE_COLUMNS, delimiter=";", lineterminator="\r\n",
                           extrasaction="ignore")
        w.writeheader()
        w.writerows(out)

    REPORT.write_text("\n".join(report_lines(rows, out, excl, k_qc, runs)) + "\n", encoding="utf-8")
    print(f"triage -> {TRIAGE}\nreport -> {REPORT}")
    print(REPORT.read_text(encoding="utf-8"))
    return 0


def report_lines(rows, out, excl, k_qc, runs) -> list[str]:
    piles = collections.Counter(o["pile"] for o in out)
    pc = lambda d: ((d or {}).get("parsed") or {}).get("primary_code") or "-"   # noqa: E731
    L = [f"# {QID}: snowballed records, LLM-first title/abstract screening (D21)", "",
         f"Sheet `screening/{SHEET.name}` ({len(rows)} records, n {rows[0]['n']}-{rows[-1]['n']}; new works of "
         f"snowball run {SNOWBALL_RUN} passing F3). Prompt {PROMPT_VERSION}, two runs per record, "
         f"`screening/run_llm_screen.py` unchanged. Triage sheet `screening/{TRIAGE.name}`.", "",
         "## Records per pile", "", "| pile | records |", "|---|---|"]
    L += [f"| {p} | {piles[p]} |" for p in PILES] + [f"| total | {len(out)} |", ""]
    L += [f"QC sample: {k_qc} of {len(excl)} `excluded_llm` records (10 %, rounded up; "
          f"`random.Random({QC_SEED}).sample` over them in `n` order).", ""]

    L += ["## `excluded_llm`: run-1 primary code", "", "| primary code (run 1) | records |", "|---|---|"]
    for code, n in sorted(collections.Counter(pc(o["_d1"]) for o in excl).items()):
        L.append(f"| {code} | {n} |")
    diff = sum(1 for o in excl if pc(o["_d1"]) != pc(o["_d2"]))
    L += ["", f"Run 1 and run 2 give a different primary code: {diff} of {len(excl)}.", ""]
    pairs = collections.Counter((pc(o["_d1"]), pc(o["_d2"])) for o in excl if pc(o["_d1"]) != pc(o["_d2"]))
    if pairs:
        L += ["| run 1 | run 2 | records |", "|---|---|---|"]
        L += [f"| {x} | {y} | {n} |" for (x, y), n in sorted(pairs.items(), key=lambda t: -t[1])] + [""]

    def agreement(sub, label):
        both = [o for o in sub if decision(o["_d1"]) and decision(o["_d2"])]
        same = sum(1 for o in both if decision(o["_d1"]) == decision(o["_d2"]))
        ret = lambda o, k: decision(o[k]) != "exclude"     # noqa: E731
        same_bin = sum(1 for o in both if ret(o, "_d1") == ret(o, "_d2"))
        tab = collections.Counter((decision(o["_d1"]), decision(o["_d2"])) for o in both)
        lines = [f"- {label}: {len(both)} records with two parsed answers; same decision {same} "
                 f"({same / len(both):.3f}); same retain/exclude {same_bin} ({same_bin / len(both):.3f})"
                 if both else f"- {label}: none"]
        return lines, tab
    l_all, tab = agreement(out, "all records")
    l_ab, _ = agreement([o for o in out if o["pile"] != "h1_no_abstract"], "records with an abstract of >= 30 words")
    L += ["## Run-to-run agreement", "",
          "Retain = `include` or `maybe`, exclude = `exclude` (a `maybe` is not excluded under D21).", ""]
    L += l_all + l_ab + ["", "| run 1 \\ run 2 | include | maybe | exclude |", "|---|---|---|---|"]
    for x in ("include", "maybe", "exclude"):
        L.append(f"| {x} | " + " | ".join(str(tab[(x, y)]) for y in ("include", "maybe", "exclude")) + " |")
    L.append("")

    src = collections.Counter(r["abstract_source"] for r in rows)
    backfilled = ("openalex_backfill", "crossref", "semantic_scholar")
    flagged = [r for r in rows if r["abstract_source"] in backfilled or words(r["abstract"]) < MIN_WORDS]
    L += ["## Abstract backfill", "",
          f"Backfill run {BACKFILL_RUN} (by DOI, `backfill-abstracts` fetchers, logged in `runs.csv` as "
          f"`abstract_backfill`): OpenAlex, then Semantic Scholar. {BACKFILL_NOTE}", "",
          f"Records needing an abstract before backfill (none or < {MIN_WORDS} words): {len(flagged)} "
          f"({sum(1 for r in flagged if not r['doi'])} without DOI).", "",
          "| abstract source | records |", "|---|---|"]
    for s in ("openalex", "semanticscholar", "openalex_backfill", "crossref", "semantic_scholar", ""):
        L.append(f"| {s or '(none)'} | {src[s]} |")
    L += ["", f"Filled by backfill: OpenAlex {src['openalex_backfill']}, Crossref {src['crossref']}, "
          f"Semantic Scholar {src['semantic_scholar']}. Still without a usable abstract: "
          f"{sum(words(r['abstract']) < MIN_WORDS for r in rows)} "
          f"({sum(not r['abstract'] for r in rows)} with none) = pile `h1_no_abstract`.", ""]

    L += ["## Snowballing seeds", "", "| seed | DOI | n | pile | run 1 | run 2 |", "|---|---|---|---|---|---|"]
    for name, doi in SEEDS.items():
        o = next((o for o in out if o["_doi"] == doi), None)
        L.append(f"| {name} | {doi} | {o['n']} | {o['pile']} | {o['llm_run1']} | {o['llm_run2']} |" if o
                 else f"| {name} | {doi} | - | not in sheet | | |")
    L.append("")

    lines_all = [d for run in (1, 2) for d in runs[run].values()]
    errors = [d for d in lines_all if d["status"] != "ok"]
    retried = [d for d in lines_all if d.get("retried")]
    L += ["## Errors and retries", "",
          f"- answers: {len(lines_all)} ({len(runs[1])} run 1, {len(runs[2])} run 2)",
          f"- retried after a first-attempt error: {len(retried)}; still an error after the retry: {len(errors)} "
          f"(counted as unclear)"]
    for d in retried:
        L.append(f"  - run {d['run']} {d['record_id']}: {str(d.get('first_attempt_error'))[:160]}"
                 + (f" -> still: {str(d.get('parse_error'))[:160]}" if d["status"] != "ok" else " -> ok"))
    L.append("")

    models = collections.Counter(m for d in lines_all for m in d.get("model_reported") or [])
    versions = collections.Counter(d.get("claude_code_version") for d in lines_all)
    shas = collections.Counter(d.get("prompt_sha256") for d in lines_all)
    u = collections.Counter()
    for d in lines_all:
        us = d.get("usage") or {}
        u["cost"] += us.get("total_cost_usd") or 0
        u["ms"] += us.get("duration_ms") or 0
        for k in ("input_tokens", "output_tokens", "cache_creation_input_tokens", "cache_read_input_tokens"):
            u[k] += (us.get("usage") or {}).get(k) or 0
    first = min((d["screened_at"] for d in lines_all), default="")
    last = max((d["screened_at"] for d in lines_all), default="")
    L += ["## Model, version, usage", "",
          f"- model requested: claude-opus-5-5; model reported: "
          + ", ".join(f"{m} ({n})" for m, n in models.items()),
          f"- Claude Code version: " + ", ".join(f"{v} ({n})" for v, n in versions.items()),
          f"- prompt SHA-256: " + ", ".join(f"{s} ({n})" for s, n in shas.items()),
          f"- screened {first} to {last}",
          f"- total usage: input tokens {u['input_tokens']:,}, cache creation {u['cache_creation_input_tokens']:,}, "
          f"cache read {u['cache_read_input_tokens']:,}, output tokens {u['output_tokens']:,}; "
          f"reported cost {u['cost']:.2f} USD (list price; subscription login); summed call time "
          f"{u['ms'] / 3.6e6:.1f} h", ""]
    return L


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("prepare")
    p.add_argument("--backfill-run", help="continue or replay this abstract backfill run: sources saved under it "
                                          "are replayed, the others are requested under the same run_id")
    p.add_argument("--skip-backfill-source", help="comma list of backfill sources not to ask")
    p.set_defaults(func=cmd_prepare)
    t = sub.add_parser("triage")
    t.add_argument("--allow-missing", action="store_true", help="write the triage although answers are missing")
    t.set_defaults(func=cmd_triage)
    a = ap.parse_args(argv)
    return a.func(a)


if __name__ == "__main__":
    sys.exit(main())
