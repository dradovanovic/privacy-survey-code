"""
Supplementary discovery: backward and forward snowballing of a study corpus
through OpenAlex and Semantic Scholar (search_protocol.md §1.7, DECISION.md D13).

For every corpus DOI
* backward (the references of the corpus paper): OpenAlex `referenced_works`
  (work ids, resolved in batches with filter=openalex:W1|W2|...) and Semantic
  Scholar paper/DOI:<doi>/references;
* forward (the works citing the corpus paper): OpenAlex filter=cites:<work id>
  (cursor paging) and Semantic Scholar paper/DOI:<doi>/citations (offset paging).

Design rules
* Two layers. `fetch_*` talks to the APIs and only writes raw responses
  (data/raw/<source>/snowball/<run_id>/) and runs.csv rows; `read_*`,
  `consolidate` and the report read only those raw files. A live run is
  fetch + build, a replay (--from-run) is build alone, so every output can be
  regenerated without a request.
* A corpus DOI a source cannot resolve is logged and skipped, never fatal.
* This step collects and counts. It writes no screening sheet and makes no
  eligibility decision; the nested filters F0..F3t are counts for choosing a
  pre-filter, and the data files are not filtered.

Raw files
    openalex/snowball/<run_id>/params.json
    openalex/snowball/<run_id>/corpus_s<start>.json           corpus DOIs -> works (with referenced_works)
    openalex/snowball/<run_id>/refs_s<start>.json             referenced work ids -> works
    openalex/snowball/<run_id>/cites_n<n>_<W id>_p<page>.json works citing corpus paper n
    semanticscholar/snowball/<run_id>/params.json
    semanticscholar/snowball/<run_id>/references_n<n>_o<offset>.json
    semanticscholar/snowball/<run_id>/citations_n<n>_o<offset>.json
    <source>/snowball/<run_id>/fetch_summary.json             retries, fallbacks and errors of the live run
"""

from __future__ import annotations

import collections
import csv
import json
import re
import time
from pathlib import Path

from . import query_compiler as qc
from . import records as rec

SOURCES = ("openalex", "semanticscholar")
DIRECTIONS = ("backward", "forward")
CT_CORPUS, CT_BACKWARD, CT_FORWARD = "snowball_corpus", "snowball_backward", "snowball_forward"

# OpenAlex: fields kept for the found works (everything normalize_openalex reads, plus language).
OPENALEX_SELECT = ("id,doi,display_name,publication_year,type,language,primary_location,"
                   "abstract_inverted_index,keywords,concepts,cited_by_count")
OPENALEX_ID_BATCH = 100      # OpenAlex allows up to 100 OR values per filter and 100 results per page
S2_FIELDS = "paperId,externalIds,title,year,venue,publicationTypes,abstract"
S2_PAGE = 500                # links per request (API maximum 1000; 500 keeps responses with abstracts small)
S2_KIND = {"backward": ("references", "citedPaper"), "forward": ("citations", "citingPaper")}
# Semantic Scholar publicationTypes -> the OpenAlex type names the query filter is expressed in
S2_TYPE = {"JournalArticle": "article", "Review": "review", "MetaAnalysis": "review",
           "Conference": "conference-paper", "BookSection": "book-chapter"}

EDGE_COLUMNS = ["corpus_n", "corpus_doi", "direction", "source", "found_id", "found_doi", "found_title",
                "found_year"]
RECORD_COLUMNS = ["record_id", "doi", "title", "year", "content_type", "language", "venue", "abstract",
                  "keywords", "found_ids", "n_corpus_links", "corpus_ns", "directions", "sources",
                  "in_corpus", "already_screened"]
SEEN_COLUMN = "seen_round1"          # only written when --seen files are given
FILTERS =("F0", "F1", "F2", "F2t", "F3", "F3t")
_LINE_BREAKS = re.compile(r"\s*[\r\n\t\v\f\x85  ]+\s*")


def _one_line(text) -> str:
    return _LINE_BREAKS.sub(" ", str(text or "")).strip()


def _wid(url_or_id: str | None) -> str:
    """'https://openalex.org/W123' -> 'W123'."""
    return (url_or_id or "").rsplit("/", 1)[-1]


# ----------------------------------------------------------------------------
# Inputs
# ----------------------------------------------------------------------------

def load_corpus(path: str | Path) -> list[dict]:
    """Corpus file (columns n, doi, title, ...) -> [{n, doi, title}], in file order. Every row needs a DOI."""
    with open(path, encoding="utf-8-sig", newline="") as fh:
        rows = list(csv.DictReader(fh))
    corpus = []
    for r in rows:
        doi = rec._clean_doi(r.get("doi"))
        if not doi:
            raise ValueError(f"corpus row n={r.get('n')} has no DOI")
        corpus.append({"n": int(r["n"]), "doi": doi, "title": r.get("title") or ""})
    return corpus


def load_screened(path: str | Path) -> tuple[set[str], set[str]]:
    """(DOIs, normalized titles) of the already-screened records; only doi and title are read."""
    dois, titles = set(), set()
    if not Path(path).exists():
        return dois, titles
    with open(path, encoding="utf-8-sig", newline="") as fh:
        for r in csv.DictReader(fh):
            doi, tk = rec._clean_doi(r.get("doi")), rec.title_key(r.get("title") or "")
            if doi:
                dois.add(doi)
            if tk:
                titles.add(tk)
    return dois, titles


def load_seen(paths) -> tuple[set[str], dict[str, set]]:
    """
    (DOIs, {normalized title: years}) of the works in earlier record files
    (--seen; columns doi, title, year). An empty year is stored as None.
    """
    dois: set[str] = set()
    titles: dict[str, set] = collections.defaultdict(set)
    for path in paths:
        with open(path, encoding="utf-8-sig", newline="") as fh:
            for r in csv.DictReader(fh):
                doi, tk = rec._clean_doi(r.get("doi")), rec.title_key(r.get("title") or "")
                if doi:
                    dois.add(doi)
                if tk:
                    titles[tk].add(int(r["year"]) if (r.get("year") or "").strip() else None)
    return dois, dict(titles)


def is_seen(seen: tuple[set[str], dict[str, set]], dois: set[str], tks: set[str], year) -> bool:
    """By DOI, then by normalized title plus year; a missing year on either side matches on the title alone
    (the rule of consolidate)."""
    s_dois, s_titles = seen
    if dois & s_dois:
        return True
    year = int(year) if year else None
    return any(y is None or year is None or y == year for tk in tks for y in s_titles.get(tk, ()))


# ----------------------------------------------------------------------------
# Fetch (live run only): raw files + runs.csv
# ----------------------------------------------------------------------------

def _write_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=1), encoding="utf-8")


def fetch_openalex(client, corpus: list[dict], qid: str, run_id: str, raw_dir: Path, corpus_file: str) -> dict:
    """Resolve the corpus DOIs, page through the citing works, resolve the referenced work ids."""
    from .openalex_client import DOI_BATCH, MAX_PAGE, page_items
    _write_json(raw_dir / "params.json", {"corpus_file": corpus_file, "corpus_n": [c["n"] for c in corpus],
                                          "select": OPENALEX_SELECT, "per-page": MAX_PAGE,
                                          "id_batch": OPENALEX_ID_BATCH})
    errors: list[str] = []
    by_doi = {c["doi"]: c for c in corpus}
    works: dict[int, list[dict]] = collections.defaultdict(list)
    dois = [c["doi"] for c in corpus]
    for start in range(0, len(dois), DOI_BATCH):
        flt = "doi:" + "|".join(dois[start:start + DOI_BATCH])
        body, status = client.logged_get({"filter": flt, "per-page": MAX_PAGE},
                                         raw_dir / f"corpus_s{start:06d}.json", run_id, qid, CT_CORPUS, start)
        if status != 200:
            errors.append(f"corpus DOI batch {start}: HTTP {status}")
            continue
        for w in page_items(body):
            c = by_doi.get(rec._clean_doi(w.get("doi")))
            if c:
                works[c["n"]].append(w)
        time.sleep(client.sleep)

    for c in corpus:                                              # forward
        for w in works.get(c["n"], []):
            wid, cursor, page, offset = _wid(w.get("id")), "*", 0, 0
            while True:
                page += 1
                body, status = client.logged_get(
                    {"filter": f"cites:{wid}", "select": OPENALEX_SELECT, "per-page": MAX_PAGE, "cursor": cursor},
                    raw_dir / f"cites_n{c['n']:04d}_{wid}_p{page:03d}.json", run_id, qid, CT_FORWARD, offset)
                time.sleep(client.sleep)
                if status != 200:
                    errors.append(f"n={c['n']} cites:{wid} page {page}: HTTP {status}")
                    break
                items = page_items(body)
                offset += len(items)
                cursor = (body.get("meta") or {}).get("next_cursor")
                if not items or not cursor:
                    break

    ref_ids = sorted({_wid(i) for ws in works.values() for w in ws for i in w.get("referenced_works") or []})
    for start in range(0, len(ref_ids), OPENALEX_ID_BATCH):       # backward
        batch = ref_ids[start:start + OPENALEX_ID_BATCH]
        body, status = client.logged_get(
            {"filter": "openalex:" + "|".join(batch), "select": OPENALEX_SELECT, "per-page": MAX_PAGE},
            raw_dir / f"refs_s{start:06d}.json", run_id, qid, CT_BACKWARD, start,
            querytext=f"openalex:<{len(batch)} work ids from referenced_works, sorted, from {batch[0]}>")
        if status != 200:
            errors.append(f"referenced works batch {start}: HTTP {status}")
        time.sleep(client.sleep)
    summary = {"retries_429_5xx": client.n_retries, "errors": errors}
    _write_json(raw_dir / "fetch_summary.json", summary)
    return summary


def fetch_semanticscholar(client, corpus: list[dict], qid: str, run_id: str, raw_dir: Path,
                          corpus_file: str, only: set[tuple[int, str]] | None = None, tag: str = "") -> dict:
    """
    paper/DOI:<doi>/references and /citations for every corpus DOI, all pages.
    If the configured key is rejected (403), the run continues without the
    key (shared pool), as the abstract backfill of 2026-10-09 had to.
    `only` + `tag` is the retry pass (--retry-failed): just those (n, direction)
    pairs, written next to the failed responses as ..._o<offset>.<tag>.json,
    so nothing is overwritten and the readers pick the new pages up.
    """
    if only is None:
        _write_json(raw_dir / "params.json", {"corpus_file": corpus_file, "corpus_n": [c["n"] for c in corpus],
                                              "fields": S2_FIELDS, "limit": S2_PAGE})
    errors: list[str] = []
    key_rejected = False
    for c in corpus:
        for direction in DIRECTIONS:
            if only is not None and (c["n"], direction) not in only:
                continue
            kind = S2_KIND[direction][0]
            ct = CT_BACKWARD if direction == "backward" else CT_FORWARD
            offset = 0
            while True:
                raw = raw_dir / f"{kind}_n{c['n']:04d}_o{offset:06d}{'.' + tag if tag else ''}.json"
                body, status = client.paper_links(c["doi"], kind, S2_FIELDS, raw, run_id, qid, ct, offset, S2_PAGE)
                if status == 403 and client.api_key:
                    key_rejected, client.api_key = True, None
                    continue                                       # same request again, without the key
                if status != 200:
                    errors.append(f"n={c['n']} {kind} offset {offset}: HTTP {status}")
                    break
                nxt = body.get("next")
                if not body.get("data") or nxt is None:
                    break
                offset = int(nxt)
    summary = {"retries_429_5xx": client.n_retries, "key_rejected_403_fell_back_to_no_key": key_rejected,
               "errors": errors}
    if only is not None:                       # retry pass: keep the first pass, append this one
        first = _load(raw_dir / "fetch_summary.json") if (raw_dir / "fetch_summary.json").is_file() else {}
        first.setdefault("retry_passes", []).append({"tag": tag, "pairs": sorted(map(list, only)), **summary})
        summary = first
    _write_json(raw_dir / "fetch_summary.json", summary)
    return summary


def failed_semanticscholar(run_log: Path, run_id: str, raw_dir: Path, corpus: list[dict]) -> set[tuple[int, str]]:
    """
    (n, direction) pairs of a run whose requests ended in an error other than
    404 (rate limit, server error) and that still have no usable response.
    """
    by_doi = {c["doi"]: c["n"] for c in corpus}
    kind_dir = {S2_KIND[d][0]: d for d in DIRECTIONS}
    failed = set()
    with open(run_log, encoding="utf-8", newline="") as fh:
        for r in csv.DictReader(fh):
            m = re.match(r"paper/DOI:(.+)/(references|citations) fields=", r["querytext"])
            if (r["run_id"] == run_id and r["db"] == "semanticscholar" and m
                    and r["status"] not in ("200", "404") and m.group(1) in by_doi):
                failed.add((by_doi[m.group(1)], kind_dir[m.group(2)]))
    stats = read_semanticscholar(raw_dir, corpus, "", run_id)[2]
    return {(n, d) for n, d in failed if n in stats["unresolved"][d]}


# ----------------------------------------------------------------------------
# Read raw files -> edges and normalized works
# ----------------------------------------------------------------------------

def _load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _run_corpus(raw_dir: Path, corpus: list[dict]) -> list[dict]:
    """The corpus papers a run covered (params.json corpus_n), so a dry run replays as a dry run."""
    ns = set(_load(raw_dir / "params.json")["corpus_n"])
    return [c for c in corpus if c["n"] in ns]


def normalize_openalex_found(item: dict, qid: str, run_id: str, raw_path: str) -> dict:
    r = rec.normalize_openalex(item, qid, run_id, raw_path)
    r["language"] = item.get("language")
    r["types"] = [item["type"]] if item.get("type") else []
    return r


def normalize_semanticscholar(paper: dict, qid: str, run_id: str, raw_path: str) -> dict:
    """
    Map a Semantic Scholar paper object (citedPaper / citingPaper) to the unified
    schema. Semantic Scholar gives no language and no keywords. A reference it
    could not match to a paper has paperId null and only a title; its record_id
    is then empty.
    """
    pid = paper.get("paperId")
    ptypes = paper.get("publicationTypes") or []
    return {
        "record_id": f"semanticscholar:{pid}" if pid else "",
        "db": "semanticscholar", "query_id": qid, "run_id": run_id,
        "doi": rec._clean_doi((paper.get("externalIds") or {}).get("DOI")),
        "title": (paper.get("title") or "").strip(),
        "abstract": (paper.get("abstract") or "").strip(),
        "year": paper.get("year"),
        "venue": paper.get("venue") or None,
        "content_type": "; ".join(ptypes) or None,
        "authors": [], "keywords": [], "citing_count": None,
        "url": f"https://www.semanticscholar.org/paper/{pid}" if pid else None,
        "pdf_url": None, "raw_path": raw_path,
        "language": None,
        "types": sorted({S2_TYPE.get(t, t) for t in ptypes}),
    }


def _edge(c: dict, direction: str, source: str, key: str, r: dict | None) -> dict:
    r = r or {}
    return {"corpus_n": c["n"], "corpus_doi": c["doi"], "direction": direction, "source": source,
            "found_id": "" if key.startswith("s2-unmatched:") else key,
            "found_doi": r.get("doi") or "", "found_title": _one_line(r.get("title")),
            "found_year": r.get("year") or "", "_key": key}


def read_openalex(raw_dir: Path, corpus: list[dict], qid: str, run_id: str) -> tuple[list[dict], dict, dict]:
    """(edges, {key: normalized work}, stats) from the raw files of one OpenAlex snowball run."""
    from .openalex_client import page_items
    corpus = _run_corpus(raw_dir, corpus)
    by_doi = {c["doi"]: c for c in corpus}
    cworks: dict[int, list[dict]] = collections.defaultdict(list)
    for p in sorted(raw_dir.glob("corpus_s*.json")):
        for w in page_items(_load(p)):
            c = by_doi.get(rec._clean_doi(w.get("doi")))
            if c:
                cworks[c["n"]].append(w)
    found: dict[str, dict] = {}
    for p in sorted(raw_dir.glob("refs_s*.json")):
        for w in page_items(_load(p)):
            found[f"openalex:{_wid(w.get('id'))}"] = normalize_openalex_found(w, qid, run_id, str(p))
    edges, seen = [], set()
    unresolved_refs: set[str] = set()
    n_with = {d: 0 for d in DIRECTIONS}
    for c in corpus:
        ref_keys = sorted({f"openalex:{_wid(i)}" for w in cworks.get(c["n"], []) for i in w.get("referenced_works") or []})
        n_with["backward"] += bool(ref_keys)
        for key in ref_keys:
            if key not in found:
                unresolved_refs.add(key)
            edges.append(_edge(c, "backward", "openalex", key, found.get(key)))
        n_fwd = 0
        for p in sorted(raw_dir.glob(f"cites_n{c['n']:04d}_*_p*.json")):
            for w in page_items(_load(p)):
                key = f"openalex:{_wid(w.get('id'))}"
                found.setdefault(key, normalize_openalex_found(w, qid, run_id, str(p)))
                if (c["n"], key) not in seen:            # a DOI with two OpenAlex works: count the link once
                    seen.add((c["n"], key))
                    edges.append(_edge(c, "forward", "openalex", key, found[key]))
                    n_fwd += 1
        n_with["forward"] += bool(n_fwd)
    resolved = [c["n"] for c in corpus if c["n"] in cworks]
    stats = {"corpus": len(corpus), "resolved": {d: resolved for d in DIRECTIONS},
             "unresolved": {d: [c["n"] for c in corpus if c["n"] not in cworks] for d in DIRECTIONS},
             "with_links": n_with, "unresolved_reference_ids": len(unresolved_refs)}
    return edges, found, stats


def read_semanticscholar(raw_dir: Path, corpus: list[dict], qid: str, run_id: str) -> tuple[list[dict], dict, dict]:
    """(edges, {key: normalized work}, stats) from the raw files of one Semantic Scholar snowball run."""
    corpus = _run_corpus(raw_dir, corpus)
    found: dict[str, dict] = {}
    edges = []
    resolved = {d: [] for d in DIRECTIONS}
    unresolved = {d: [] for d in DIRECTIONS}
    n_with = {d: 0 for d in DIRECTIONS}
    withheld = {d: [] for d in DIRECTIONS}
    for c in corpus:
        for direction in DIRECTIONS:
            kind, field = S2_KIND[direction]
            ok, seen = False, set()
            for p in sorted(raw_dir.glob(f"{kind}_n{c['n']:04d}_o*.json")):
                body = _load(p)
                if not isinstance(body, dict) or "data" not in body:       # saved error body (404, 429, ...)
                    continue
                ok = True
                if body["data"] is None:           # paper known, list elided by the publisher (see the disclaimer)
                    withheld[direction].append(c["n"])
                for link in body.get("data") or []:
                    paper = link.get(field) or {}
                    r = normalize_semanticscholar(paper, qid, run_id, str(p))
                    if not r["record_id"] and not r["title"]:
                        continue                                           # nothing to identify the work by
                    key = r["record_id"] or f"s2-unmatched:{rec.title_key(r['title'])}:{r['year'] or ''}"
                    found.setdefault(key, r)
                    if key not in seen:
                        seen.add(key)
                        edges.append(_edge(c, direction, "semanticscholar", key, found[key]))
            (resolved if ok else unresolved)[direction].append(c["n"])
            n_with[direction] += bool(seen)
    stats = {"corpus": len(corpus), "resolved": resolved, "unresolved": unresolved, "with_links": n_with,
             "withheld": withheld}
    return edges, found, stats


READERS = {"openalex": read_openalex, "semanticscholar": read_semanticscholar}


# ----------------------------------------------------------------------------
# Consolidation
# ----------------------------------------------------------------------------

def consolidate(found: dict[str, dict]) -> tuple[list[list[str]], dict[str, int]]:
    """
    Group the found works across sources and directions: by DOI, then by
    normalized title plus year. This is the rule of records.dedupe (first by
    DOI, else by title, the earlier work wins) with the year added to the
    title key; a missing year on either side cannot contradict, so it matches
    on the title alone. OpenAlex works are taken first, so a group's leading
    record is the OpenAlex one when both sources found the work.
    Returns (groups as lists of keys, {key: group index}).
    """
    order = sorted(found, key=lambda k: (SOURCES.index(found[k]["db"]), k))
    by_doi: dict[str, int] = {}
    by_title: dict[str, list[tuple[int | None, int]]] = collections.defaultdict(list)
    groups: list[list[str]] = []
    where: dict[str, int] = {}
    for key in order:
        r = found[key]
        doi, tk, year = r.get("doi"), rec.title_key(r.get("title") or ""), r.get("year") or None
        g = by_doi.get(doi) if doi else None
        if g is None and tk:
            g = next((gi for y, gi in by_title[tk] if y == year or y is None or year is None), None)
        if g is None:
            g = len(groups)
            groups.append([])
        groups[g].append(key)
        where[key] = g
        if doi:
            by_doi.setdefault(doi, g)
        if tk and (year, g) not in by_title[tk]:
            by_title[tk].append((year, g))
    return groups, where


def build_records(found: dict[str, dict], edges: list[dict], corpus: list[dict],
                  screened: tuple[set[str], set[str]], seen=None) -> list[dict]:
    """
    One record per unique work, with its links to the corpus and the in_corpus / already_screened marks;
    with `seen` (load_seen) also the seen_round1 mark.
    """
    groups, where = consolidate(found)
    links: dict[int, list[dict]] = collections.defaultdict(list)
    for e in edges:
        if e["_key"] in where:                        # an unresolved OpenAlex reference id has no work
            links[where[e["_key"]]].append(e)
    corpus_dois = {c["doi"] for c in corpus}
    corpus_titles = {rec.title_key(c["title"]) for c in corpus if c["title"]}
    s_dois, s_titles = screened
    out = []
    for gi, keys in enumerate(groups):
        members = [found[k] for k in keys]
        first = lambda f: next((m[f] for m in members if m.get(f)), None)   # noqa: E731
        dois = {m["doi"] for m in members if m.get("doi")}
        tks = {rec.title_key(m["title"]) for m in members if m.get("title")}
        es = links.get(gi, [])
        ns = sorted({e["corpus_n"] for e in es})
        out.append({
            "record_id": next((m["record_id"] for m in members if m["record_id"]), ""),
            "doi": first("doi") or "", "title": first("title") or "", "year": first("year"),
            "content_type": first("content_type") or "", "language": first("language") or "",
            "venue": first("venue") or "",
            "abstract": max((m.get("abstract") or "" for m in members), key=lambda a: len(a.split())),
            "keywords": next((m["keywords"] for m in members if m.get("keywords")), []),
            "found_ids": [m["record_id"] for m in members if m["record_id"]],
            "types": sorted({t for m in members for t in m.get("types") or []}),
            "languages": sorted({m["language"] for m in members if m.get("language")}),
            "n_corpus_links": len(ns), "corpus_ns": ns,
            "directions": sorted({e["direction"] for e in es}),
            "sources": sorted({e["source"] for e in es}),
            "by_direction": {d: sorted({e["source"] for e in es if e["direction"] == d}) for d in DIRECTIONS},
            "in_corpus": bool(dois & corpus_dois or tks & corpus_titles),
            "already_screened": bool(dois & s_dois or tks & s_titles),
            "dois": dois,
        })
        if seen is not None:
            out[-1][SEEN_COLUMN] = is_seen(seen, dois, tks, out[-1]["year"])
    return out


def is_new(r: dict) -> bool:
    """Not in the corpus, not already screened and (when marked) not seen in an earlier round."""
    return not r["in_corpus"] and not r["already_screened"] and not r.get(SEEN_COLUMN)


# ----------------------------------------------------------------------------
# Nested filters (counts only)
# ----------------------------------------------------------------------------

def allowed_types(query: dict) -> set[str]:
    """The OpenAlex type names the query's content-type filter allows (as compile_openalex derives them)."""
    ct = query.get("filters", {}).get("content_types", {})
    return set(ct.get("openalex") or [qc.OPENALEX_TYPES[d] for d in ct.get("scopus_doctypes", [])
                                      if d in qc.OPENALEX_TYPES])


def filter_flags(query: dict, r: dict) -> dict[str, bool]:
    """
    F1: year in range, English or language unknown, an allowed type or type
    unknown (a work passes if any source gives an allowed type). F2 / F2t: a
    secondary_research term in title, abstract or keywords / in the title.
    F3 / F3t: F2 / F2t plus a domain term in title, abstract or keywords.
    Matching is records.group_matches, as for the local sensitivity variants;
    the privacy group is not used.
    """
    f = query.get("filters", {})
    langs = {{"english": "en"}.get(l.lower(), l.lower()) for l in f.get("languages", [])}
    types = allowed_types(query)
    year = r.get("year")
    f1 = (bool(year) and f.get("start_year", 0) <= int(year) <= f.get("end_year", 9999)
          and (not r["languages"] or not langs or bool(set(r["languages"]) & langs))
          and (not r["types"] or not types or bool(set(r["types"]) & types)))
    gm = rec.group_matches(query, r)
    title_only = dict(r, abstract="", keywords=[])
    sec, sec_t, dom = gm["secondary_research"], rec.group_matches(query, title_only)["secondary_research"], gm["domain"]
    return {"F0": True, "F1": f1, "F2": f1 and sec, "F2t": f1 and sec_t,
            "F3": f1 and sec and dom, "F3t": f1 and sec_t and dom}


def _link_bin(n: int) -> str:
    return "1" if n <= 1 else "2" if n == 2 else "3-4" if n <= 4 else "5+"


LINK_BINS = ("1", "2", "3-4", "5+")


def filter_counts(query: dict, new: list[dict]) -> dict:
    counts = {k: 0 for k in FILTERS}
    detail = {k: {"no_abstract": 0, "under_30_words": 0, "links": dict.fromkeys(LINK_BINS, 0)}
              for k in ("F1", "F3", "F3t")}
    for r in new:
        r["_flags"] = flags = filter_flags(query, r)
        for k in FILTERS:
            counts[k] += flags[k]
        for k, d in detail.items():
            if flags[k]:
                d["no_abstract"] += not r["abstract"]
                d["under_30_words"] += rec.needs_abstract(r)
                d["links"][_link_bin(r["n_corpus_links"])] += 1
    return {"counts": counts, "detail": detail,
            "no_year": sum(1 for r in new if not r.get("year"))}


# ----------------------------------------------------------------------------
# Outputs
# ----------------------------------------------------------------------------

def write_edges(path: Path, edges: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=EDGE_COLUMNS, extrasaction="ignore")
        w.writeheader()
        w.writerows(edges)


def write_records(path: Path, records: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    columns = list(RECORD_COLUMNS)
    if records and SEEN_COLUMN in records[0]:
        columns.insert(columns.index("already_screened") + 1, SEEN_COLUMN)
    with open(path, "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=columns, extrasaction="ignore")
        w.writeheader()
        for r in sorted(records, key=lambda r: (-r["n_corpus_links"], r["record_id"], r["title"])):
            extra = {SEEN_COLUMN: int(r[SEEN_COLUMN])} if SEEN_COLUMN in r else {}
            w.writerow({**r, **extra, "title": _one_line(r["title"]), "abstract": _one_line(r["abstract"]),
                        "venue": _one_line(r["venue"]), "year": r["year"] or "",
                        "keywords": _one_line("; ".join(r["keywords"])),
                        "found_ids": "; ".join(r["found_ids"]),
                        "corpus_ns": "; ".join(str(n) for n in r["corpus_ns"]),
                        "directions": "; ".join(r["directions"]), "sources": "; ".join(r["sources"]),
                        "in_corpus": int(r["in_corpus"]), "already_screened": int(r["already_screened"])})


def api_calls(run_log: Path, run_id: str) -> dict[tuple[str, str], collections.Counter]:
    """{(db, content_type): Counter of HTTP status} for the logged requests of a run."""
    out: dict[tuple[str, str], collections.Counter] = collections.defaultdict(collections.Counter)
    if run_log.exists():
        with open(run_log, encoding="utf-8", newline="") as fh:
            for r in csv.DictReader(fh):
                if r["run_id"] == run_id and r["content_type"].startswith("snowball_"):
                    out[(r["db"], r["content_type"])][r["status"]] += 1
    return out


def source_table(edges: list[dict], stats: dict, calls: dict) -> list[dict]:
    """Per source and direction: corpus papers resolved, links, unique found works, logged requests."""
    rows = []
    for src in SOURCES:
        if src not in stats:
            continue
        for d in DIRECTIONS:
            es = [e for e in edges if e["source"] == src and e["direction"] == d]
            n_calls = sum(calls.get((src, CT_BACKWARD if d == "backward" else CT_FORWARD), {}).values())
            linked = {e["corpus_n"] for e in es}
            rows.append({"source": src, "direction": d, "corpus": stats[src]["corpus"],
                         "empty": [n for n in stats[src]["resolved"][d] if n not in linked],
                         "resolved": len(stats[src]["resolved"][d]), "with_links": stats[src]["with_links"][d],
                         "unresolved": stats[src]["unresolved"][d], "links": len(es),
                         "works": len({e["_key"] for e in es}), "calls": n_calls})
    return rows


def overlap(records: list[dict]) -> dict[str, dict[str, int]]:
    out = {}
    for d in DIRECTIONS:
        c = collections.Counter("both" if len(r["by_direction"][d]) == 2 else r["by_direction"][d][0]
                                for r in records if r["by_direction"][d])
        out[d] = {"both": c["both"], "openalex": c["openalex"], "semanticscholar": c["semanticscholar"]}
    return out


def seed_rows(seeds: list[dict], records: list[dict], query: dict) -> list[dict]:
    """The seeds expected via snowballing: found or not, where, links, filters passed."""
    by_doi = {d: r for r in records for d in r["dois"]}
    by_title = {rec.title_key(r["title"]): r for r in records if r["title"]}
    rows = []
    for s in seeds:
        if s.get("source_db") != "snowballing":
            continue
        r = by_doi.get(s.get("doi")) or by_title.get(rec.title_key(s.get("title") or ""))
        flags = filter_flags(query, r) if r else {}
        rows.append({"id": s["id"], "doi": s.get("doi") or "", "found": bool(r),
                     "by_direction": r["by_direction"] if r else {}, "n_corpus_links": r["n_corpus_links"] if r else 0,
                     "corpus_ns": r["corpus_ns"] if r else [], "has_abstract": bool(r and r["abstract"]),
                     "in_corpus": bool(r and r["in_corpus"]), "already_screened": bool(r and r["already_screened"]),
                     "passes": [k for k in FILTERS[1:] if flags.get(k)], "fails": [k for k in FILTERS[1:] if r and not flags[k]]})
    return rows


def report_lines(qid: str, run_id: str, corpus_file: str, n_corpus: int, table: list[dict], stats: dict,
                 calls: dict, summaries: dict, records: list[dict], fc: dict, seeds: list[dict] | None,
                 ov: dict, mark_file: str | None = None, n_mark: int | None = None,
                 seen_files: tuple[str, ...] = ()) -> list[str]:
    """seeds None leaves section 4 out (tagged rounds); mark_file / seen_files describe --corpus-mark / --seen."""
    new = [r for r in records if is_new(r)]
    seen_marked = bool(records) and SEEN_COLUMN in records[0]
    n_mark = n_corpus if n_mark is None else n_mark
    L = [f"# Snowballing (collect and count): `{qid}`", "",
         f"- run_id: {run_id}; corpus: `{corpus_file}` ({n_corpus} papers)"
         + (f"; `in_corpus` marked against `{mark_file}` ({n_mark} studies)" if mark_file else ""),
         *([f"- `{SEEN_COLUMN}` marked against: " + ", ".join(f"`{s}`" for s in seen_files)] if seen_files else []),
         "- backward = references of a corpus paper; forward = works citing it. Sources: OpenAlex, Semantic Scholar.",
         "- This report counts only. No record is screened or removed; the data files hold every found work.", "",
         "## 1. Per source and direction", "",
         "| source | direction | corpus papers resolved | with >= 1 work | links (edges) | works found (unique in source) | API calls |",
         "|---|---|---|---|---|---|---|"]
    for t in table:
        L.append(f"| {t['source']} | {t['direction']} | {t['resolved']}/{t['corpus']} | {t['with_links']} | "
                 f"{t['links']} | {t['works']} | {t['calls']} |")
    L.append("")
    for src in SOURCES:
        if src not in stats:
            continue
        n_corpus_calls = sum(calls.get((src, CT_CORPUS), {}).values())
        status = collections.Counter()
        for (db, _), c in calls.items():
            if db == src:
                status.update(c)
        L.append(f"- {src}: {sum(status.values())} logged requests"
                 + (f" ({n_corpus_calls} to resolve the corpus DOIs)" if n_corpus_calls else "")
                 + "; by HTTP status: " + ", ".join(f"{k}: {v}" for k, v in sorted(status.items())))
        s = summaries.get(src) or {}
        for rp in s.get("retry_passes") or []:
            L.append(f"    - retry pass {rp['tag']} for (n, direction) {rp['pairs']}: "
                     f"{len(rp['errors'])} still failing; {rp['retries_429_5xx']} retried 429/5xx responses")
        if s:
            L.append(f"    - retried 429/5xx responses (not logged as separate requests): {s.get('retries_429_5xx', 0)}"
                     + ("; the configured API key was rejected (403), the run continued without a key"
                        if s.get("key_rejected_403_fell_back_to_no_key") else ""))
            for e in s.get("errors") or []:
                L.append(f"    - error: {e}")
    if "openalex" in stats:
        L.append(f"- openalex: {stats['openalex']['unresolved_reference_ids']} referenced work ids did not resolve to "
                 "a work (kept in the edge file with the id only, not counted as works)")
    L += ["", "Corpus papers not resolved, by `n`:", ""]
    for t in table:
        L.append(f"- {t['source']} {t['direction']}: {', '.join(map(str, t['unresolved'])) or 'none'}")
    L += ["", "Corpus papers resolved but without any work in that source and direction, by `n`:", ""]
    for t in table:
        L.append(f"- {t['source']} {t['direction']}: {', '.join(map(str, t['empty'])) or 'none'}")
    for d in DIRECTIONS:
        wh = (stats.get("semanticscholar") or {}).get("withheld", {}).get(d)
        if wh:
            L.append(f"- of these, semanticscholar {d} list withheld by the publisher (response `data: null`, "
                     f"'fields have been elided by the publisher'): {', '.join(map(str, wh))}")

    L += ["", "## 2. Unique works after consolidation", "",
          "Deduplicated across sources and directions by DOI, then by normalized title plus year "
          "(a missing year matches on the title alone).", "",
          f"- unique works: {len(records)}",
          f"- `in_corpus` (one of the {n_mark}): {sum(r['in_corpus'] for r in records)}",
          f"- `already_screened` (in the screening sheet, by DOI or title; includes the corpus papers): "
          f"{sum(r['already_screened'] for r in records)}",
          f"- already screened and not in the corpus: {sum(r['already_screened'] and not r['in_corpus'] for r in records)}"]
    if seen_marked:
        L += [f"- `{SEEN_COLUMN}` (found in the earlier round, by DOI, then by normalized title plus year): "
              f"{sum(r[SEEN_COLUMN] for r in records)}",
              f"- seen in the earlier round and neither in the corpus nor already screened: "
              f"{sum(r[SEEN_COLUMN] and not r['in_corpus'] and not r['already_screened'] for r in records)}",
              f"- **new** (none of the three): {len(new)}"]
    else:
        L.append(f"- **new** (neither): {len(new)}")

    c, d = fc["counts"], fc["detail"]
    L += ["", "## 3. Nested filters on the new works (counts only)", "",
          "Term lists and filters of the query definition, matched with the code of the local sensitivity "
          "variants. The `privacy` group is deliberately not used (D10, D17).", "",
          "| filter | definition | new works |", "|---|---|---|",
          f"| F0 | all new works | {c['F0']} |",
          f"| F1 | F0, year in the query range, English or language unknown, allowed type or type unknown | {c['F1']} |",
          f"| F2 | F1 and a `secondary_research` term in title, abstract or keywords | {c['F2']} |",
          f"| F2t | F1 and a `secondary_research` term in the title | {c['F2t']} |",
          f"| F3 | F2 and a `domain` term in title, abstract or keywords | {c['F3']} |",
          f"| F3t | F2t and a `domain` term in title, abstract or keywords | {c['F3t']} |", "",
          f"- new works without a year (fail F1): {fc['no_year']}", "",
          "| filter | works | no abstract | abstract under 30 words (incl. none) | 1 link | 2 links | 3-4 links | 5+ links |",
          "|---|---|---|---|---|---|---|---|"]
    for k in ("F1", "F3", "F3t"):
        L.append(f"| {k} | {c[k]} | {d[k]['no_abstract']} | {d[k]['under_30_words']} | "
                 + " | ".join(str(d[k]["links"][b]) for b in LINK_BINS) + " |")
    L += ["", "Links = number of corpus papers the work is linked to (either direction, either source).",
          "Keywords are available for OpenAlex works only (machine-assigned keywords and concepts); "
          "Semantic Scholar gives none, and no language."]
    if seeds is not None:
        L += ["", "## 4. Seeds expected via snowballing", "",
              "| seed | DOI | found | backward | forward | corpus links | abstract | passes | fails |",
              "|---|---|---|---|---|---|---|---|---|"]
    for s in seeds or []:
        bd = s["by_direction"]
        L.append(f"| {s['id']} | {s['doi']} | {'yes' if s['found'] else '**no**'} | "
                 f"{', '.join(bd.get('backward') or []) or '-'} | {', '.join(bd.get('forward') or []) or '-'} | "
                 f"{s['n_corpus_links']}" + (f" (n = {', '.join(map(str, s['corpus_ns']))})" if s["corpus_ns"] else "")
                 + f" | {'yes' if s['has_abstract'] else 'no'} | {', '.join(s['passes']) or '-'} | "
                 f"{', '.join(s['fails']) or '-'} |")
    L += ["", "## 5. Overlap of OpenAlex and Semantic Scholar", "",
          "Unique works (after consolidation) found in each direction.", "",
          "| direction | both | OpenAlex only | Semantic Scholar only |", "|---|---|---|---|"]
    for dname in DIRECTIONS:
        L.append(f"| {dname} | {ov[dname]['both']} | {ov[dname]['openalex']} | {ov[dname]['semanticscholar']} |")
    return L


# ----------------------------------------------------------------------------
# Command
# ----------------------------------------------------------------------------

def run(query_path: str, data_dir: str | Path, corpus_file: str | None = None, limit: int | None = None,
        dry_run: bool = False, from_run: str | None = None, sources: tuple[str, ...] = SOURCES,
        bib: str | None = None, retry_failed: bool = False, tag: str = "", seen_files=(),
        corpus_mark: str | None = None) -> int:
    """
    Collect (unless from_run replays a saved run), consolidate, count.
    dry_run: the first `limit` (default 3) corpus papers; requests are made,
    saved and logged as always, counts are printed, no output file is written.
    tag: outputs <qid>.snowball-<tag>.*; a tagged round has no seed section (4).
    seen_files: record files of earlier rounds; adds the seen_round1 mark, and a seen work is not new.
    corpus_mark: the corpus the in_corpus mark is made against (default: the start corpus).
    """
    from .ieee_client import new_run_id

    if tag and not re.fullmatch(r"[a-z0-9]+", tag):
        raise ValueError(f"--tag must be lower-case letters and digits; got {tag!r}")
    query = qc.load_query(query_path)
    qid = query["query_id"]
    data_dir = Path(data_dir)
    corpus_path = Path(corpus_file) if corpus_file else data_dir / "screening" / f"{qid}.corpus-initial.csv"
    mark_path = Path(corpus_mark) if corpus_mark else corpus_path
    corpus = load_corpus(corpus_path)
    n_all = len(corpus)
    if dry_run and not limit:
        limit = 3
    if limit:
        corpus = corpus[:limit]
    run_id = from_run or new_run_id()
    raw = {s: data_dir / "raw" / s / "snowball" / run_id for s in sources}
    print(f"snowball run {run_id} ({'replay + retry of failed requests' if from_run and retry_failed else 'replay, no requests' if from_run else 'dry run' if dry_run else 'live'}): "
          f"{len(corpus)} of {n_all} corpus papers; sources: {', '.join(sources)}")

    summaries: dict[str, dict] = {}
    if from_run:
        missing = [str(p) for p in raw.values() if not (p / "params.json").is_file()]
        if missing:
            print(f"no saved snowball run {run_id}: {', '.join(missing)}")
            return 2
        if retry_failed and "semanticscholar" in sources:
            from .semanticscholar_client import SemanticScholarClient, load_api_key
            s2_corpus = _run_corpus(raw["semanticscholar"], corpus)
            only = failed_semanticscholar(data_dir / "runs.csv", run_id, raw["semanticscholar"], s2_corpus)
            print(f"  semanticscholar: retrying {sorted(only)} (requests that ended in an error other than 404)")
            if only:
                client = SemanticScholarClient(load_api_key(), data_dir=data_dir, max_retries=8)
                fetch_semanticscholar(client, s2_corpus, qid, run_id, raw["semanticscholar"], str(corpus_path),
                                      only=only, tag=f"retry-{new_run_id()}")
    else:
        if "openalex" in sources:
            from .openalex_client import OpenAlexClient, load_api_key
            sleep = float(query.get("retrieval", {}).get("sleep_seconds", 1.0))
            client = OpenAlexClient(load_api_key(), data_dir=data_dir, sleep_seconds=sleep)
            summaries["openalex"] = fetch_openalex(client, corpus, qid, run_id, raw["openalex"], str(corpus_path))
            print(f"  openalex: fetched; {summaries['openalex']}")
        if "semanticscholar" in sources:
            from .semanticscholar_client import SemanticScholarClient, load_api_key
            client = SemanticScholarClient(load_api_key(), data_dir=data_dir, max_retries=8)
            summaries["semanticscholar"] = fetch_semanticscholar(client, corpus, qid, run_id,
                                                                 raw["semanticscholar"], str(corpus_path))
            print(f"  semanticscholar: fetched; {summaries['semanticscholar']}")

    edges, found, stats = [], {}, {}
    for s in sources:
        e, f, stats[s] = READERS[s](raw[s], corpus, qid, run_id)
        edges += e
        found.update(f)
        if s not in summaries and (raw[s] / "fetch_summary.json").is_file():
            summaries[s] = _load(raw[s] / "fetch_summary.json")
    mark = load_corpus(mark_path)
    records = build_records(found, edges, mark, load_screened(data_dir / "screening" / f"{qid}.csv"),
                            seen=load_seen(seen_files) if seen_files else None)
    calls = api_calls(data_dir / "runs.csv", run_id)
    table = source_table(edges, stats, calls)
    new = [r for r in records if is_new(r)]
    fc = filter_counts(query, new)
    seed_path = Path(query_path).parent.parent / query.get("seed_set", "")
    if tag:
        seeds = None
    else:
        seeds = seed_rows(rec.load_seed_set(seed_path, bib), records, query) if query.get("seed_set") and seed_path.is_file() else []
    lines = report_lines(qid, run_id, corpus_path.as_posix(), stats[sources[0]]["corpus"], table, stats, calls, summaries,
                         records, fc, seeds, overlap(records),
                         mark_file=mark_path.as_posix() if corpus_mark else None, n_mark=len(mark),
                         seen_files=tuple(Path(s).as_posix() for s in seen_files))

    print()
    for t in table:
        print(f"  {t['source']:<16}{t['direction']:<9} resolved {t['resolved']}/{t['corpus']}  "
              f"links {t['links']:>6}  works {t['works']:>6}  API calls {t['calls']:>4}")
    for (db, ct), c in sorted(calls.items()):
        print(f"  requests {db} {ct}: {dict(c)}")
    print(f"  unique works: {len(records)}; in_corpus {sum(r['in_corpus'] for r in records)}; "
          f"already_screened {sum(r['already_screened'] for r in records)}; "
          + (f"{SEEN_COLUMN} {sum(r[SEEN_COLUMN] for r in records)}; " if seen_files else "")
          + f"new {len(new)}")
    print("  new works per filter: " + ", ".join(f"{k} {v}" for k, v in fc["counts"].items()))
    if dry_run:
        print("\ndry run: raw responses saved and requests logged; no edge, record or report file written")
        return 0
    name = f"{qid}.snowball" + (f"-{tag}" if tag else "")
    stem = data_dir / "normalized" / name
    write_edges(Path(f"{stem}.edges.csv"), edges)
    write_records(Path(f"{stem}.records.csv"), records)
    rep = data_dir / "reports" / f"{name}.md"
    rep.parent.mkdir(parents=True, exist_ok=True)
    rep.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"\nedges -> {stem}.edges.csv ({len(edges)})\nrecords -> {stem}.records.csv ({len(records)})\nreport -> {rep}")
    return 0
