"""
Unified record schema shared by all databases, plus helpers to
* normalize raw IEEE API items into that schema,
* evaluate a query definition locally against a record (used for
  sensitivity variants and for checking that the API honoured the query),
* deduplicate across databases,
* load a seed set (DOIs / titles) from a BibTeX file or a plain text list.

Record schema (one JSON object per line in data/normalized/<query_id>.jsonl)
----------------------------------------------------------------------------
record_id      "<db>:<native id>"           e.g. "ieee:9123456"
db             "ieee" | "scopus" | "wos" | "acm"
query_id       query definition that retrieved it
run_id         timestamped run folder under data/raw/
doi            lower-case DOI or null
title          str
abstract       str
year           int or null
venue          publication title
content_type   e.g. "Journals"
authors        [str]
keywords       [str]   author keywords + index terms
citing_count   int or null
url            html landing page
pdf_url        str or null
raw_path       file the raw item came from (for audit)
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable

from .query_compiler import _terms, _fields, _operator  # noqa: F401  (private helpers reused)


# ----------------------------------------------------------------------------
# Normalization
# ----------------------------------------------------------------------------

def _clean_doi(doi: str | None) -> str | None:
    if not doi:
        return None
    doi = doi.strip().lower()
    doi = re.sub(r"^(https?://)?(dx\.)?doi\.org/", "", doi)
    return doi or None


def normalize_ieee(item: dict, query_id: str, run_id: str, raw_path: str) -> dict:
    """Map one element of the IEEE API 'articles' array to the unified schema."""
    terms = item.get("index_terms") or {}
    keywords: list[str] = []
    for key in ("author_terms", "ieee_terms", "mesh_terms"):
        keywords.extend((terms.get(key) or {}).get("terms") or [])
    authors = [a.get("full_name", "") for a in (item.get("authors") or {}).get("authors") or []]
    year = item.get("publication_year")
    try:
        year = int(year) if year not in (None, "") else None
    except (TypeError, ValueError):
        year = None
    return {
        "record_id": f"ieee:{item.get('article_number')}",
        "db": "ieee",
        "query_id": query_id,
        "run_id": run_id,
        "doi": _clean_doi(item.get("doi")),
        "title": (item.get("title") or "").strip(),
        "abstract": (item.get("abstract") or "").strip(),
        "year": year,
        "venue": item.get("publication_title"),
        "content_type": item.get("content_type"),
        "authors": authors,
        "keywords": keywords,
        "citing_count": item.get("citing_paper_count"),
        "url": item.get("html_url"),
        "pdf_url": item.get("pdf_url"),
        "raw_path": raw_path,
    }


# ----------------------------------------------------------------------------
# Local evaluation of a query against a record
# ----------------------------------------------------------------------------

_SUFFIX = r"(?:s|es|ed|ing)?"


def _word_pattern(word: str) -> str:
    r"""
    Approximate the database's stemming: 'survey' also matches surveys/surveyed/
    surveying, 'taxonomy' matches taxonomies. A trailing '*' becomes \w*.
    """
    if word.endswith("*"):
        return re.escape(word[:-1]) + r"\w*"
    if len(word) > 3 and word.endswith("y"):
        return re.escape(word[:-1]) + r"(?:y" + _SUFFIX + r"|ies)"
    return re.escape(word) + _SUFFIX


def _term_regex(term: str) -> re.Pattern:
    """
    Whole-word, case-insensitive match of a term; words may be separated by
    space or hyphen in the text ('smart grid' matches 'smart-grid'); each word
    tolerates common inflectional suffixes.
    """
    words = re.split(r"[\s-]+", term.strip().lower())
    body = r"[-\s]+".join(_word_pattern(w) for w in words if w)
    return re.compile(rf"(?<!\w){body}(?!\w)", re.IGNORECASE)


_REGEX_CACHE: dict[str, re.Pattern] = {}


def _match(term: str, text: str) -> bool:
    rx = _REGEX_CACHE.get(term)
    if rx is None:
        rx = _REGEX_CACHE[term] = _term_regex(term)
    return bool(rx.search(text))


def _field_text(record: dict, fields: Iterable[str]) -> str:
    chunks = []
    for f in fields:
        if f == "title":
            chunks.append(record.get("title") or "")
        elif f == "abstract":
            chunks.append(record.get("abstract") or "")
        elif f == "keywords":
            chunks.append(" ; ".join(record.get("keywords") or []))
        elif f == "venue":
            chunks.append(record.get("venue") or "")
    return "\n".join(chunks)


def group_matches(query: dict, record: dict, include_venue: bool = False) -> dict[str, bool]:
    """Per-concept-group match on the group's fields (optionally plus the venue name)."""
    out = {}
    for name, group in query["concept_groups"].items():
        fields = list(_fields(group)) + (["venue"] if include_venue else [])
        text = _field_text(record, fields)
        hits = [_match(t, text) for t in _terms(group)]
        out[name] = any(hits) if _operator(group) == "OR" else all(hits)
    return out


def record_matches(query: dict, record: dict, include_venue: bool = False) -> bool:
    """True if the record satisfies the concept groups on title/abstract/keywords."""
    gop = query.get("group_operator", "AND").upper()
    results = list(group_matches(query, record, include_venue).values())
    ok = all(results) if gop == "AND" else any(results)
    excl = query.get("exclusion_terms") or []
    if ok and excl:
        text = _field_text(record, ("title", "abstract", "keywords"))
        ok = not any(_match(t, text) for t in excl)
    return ok


# ----------------------------------------------------------------------------
# Deduplication
# ----------------------------------------------------------------------------

def title_key(title: str) -> str:
    return re.sub(r"[^a-z0-9]", "", (title or "").lower())


def dedupe(records: Iterable[dict]) -> tuple[list[dict], list[tuple[str, str]]]:
    """
    Keep the first record per DOI, else per normalized title. Returns
    (unique_records, [(dropped_record_id, kept_record_id), ...]).
    """
    seen_doi: dict[str, str] = {}
    seen_title: dict[str, str] = {}
    unique, dropped = [], []
    for r in records:
        doi, tk = r.get("doi"), title_key(r.get("title", ""))
        if doi and doi in seen_doi:
            dropped.append((r["record_id"], seen_doi[doi]))
            continue
        if tk and tk in seen_title:
            dropped.append((r["record_id"], seen_title[tk]))
            continue
        if doi:
            seen_doi[doi] = r["record_id"]
        if tk:
            seen_title[tk] = r["record_id"]
        unique.append(r)
    return unique, dropped


# ----------------------------------------------------------------------------
# Seed sets
# ----------------------------------------------------------------------------

_BIB_ENTRY = re.compile(r"@(\w+)\s*\{\s*([^,\s]+)\s*,(.*?)\n\}", re.DOTALL)
_BIB_FIELD = re.compile(r"(\w+)\s*=\s*(\{(?:[^{}]|\{[^{}]*\})*\}|\"[^\"]*\")", re.DOTALL)


def load_bib_entries(bib_path: str | Path) -> list[dict]:
    """Minimal BibTeX reader: returns [{key, type, title, doi, year}]. Good enough for seed matching."""
    text = Path(bib_path).read_text(encoding="utf-8", errors="replace")
    entries = []
    for m in _BIB_ENTRY.finditer(text):
        etype, key, body = m.group(1), m.group(2), m.group(3)
        fields = {k.lower(): v.strip("{}\" ").replace("\n", " ") for k, v in _BIB_FIELD.findall(body)}
        entries.append({
            "key": key,
            "type": etype.lower(),
            "title": re.sub(r"[{}]", "", fields.get("title", "")),
            "doi": _clean_doi(fields.get("doi")),
            "year": fields.get("year"),
            "keywords": fields.get("keywords", ""),
        })
    return entries


def load_seed_set(path: str | Path, bib_path: str | Path | None = None) -> list[dict]:
    """
    seeds/<stream>_seeds.txt lines are one of
        Title;DOI;BibKey[;source_db[;note]]  (semicolon format; DOI or BibKey may be empty;
                                         the note is free text and may contain ';')
        doi:10.1109/...
        key:BibKey2021                    (resolved through the .bib)
        title:Exact or near-exact title
    Blank lines and '#' comments are ignored. The seed id is the BibKey when
    present, else the DOI, else the title. source_db (lower-case, e.g. ieee,
    scopus, snowballing) names where the seed is expected from; None when absent.
    """
    bib = {e["key"]: e for e in load_bib_entries(bib_path)} if bib_path else {}
    seeds = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ";" in line and not re.match(r"^(doi|key|title)\s*:", line, re.IGNORECASE):
            parts = [p.strip() for p in line.split(";")]
            title = parts[0]
            doi = _clean_doi(parts[1]) if len(parts) > 1 else None
            key = parts[2] if len(parts) > 2 and parts[2] else None
            if key and key in bib and not doi:
                doi = bib[key]["doi"]
            source_db = parts[3].lower() if len(parts) > 3 and parts[3] else None
            note = line.split(";", 4)[4].strip() or None if len(parts) > 4 else None
            seeds.append({"id": key or doi or title, "doi": doi, "title": title, "key": key,
                          "source_db": source_db, "note": note})
            continue
        kind, _, value = line.partition(":")
        kind, value = kind.strip().lower(), value.strip()
        if kind == "doi":
            seeds.append({"id": line, "doi": _clean_doi(value), "title": "", "source_db": None})
        elif kind == "key":
            e = bib.get(value)
            if e is None:
                raise KeyError(f"seed key '{value}' not found in {bib_path}")
            seeds.append({"id": line, "doi": e["doi"], "title": e["title"], "source_db": None})
        elif kind == "title":
            seeds.append({"id": line, "doi": None, "title": value, "source_db": None})
        else:
            raise ValueError(f"unrecognised seed line: {line}")
    return seeds


def _recall(found: list, missing: list) -> float | None:
    n = len(found) + len(missing)
    return len(found) / n if n else None


def seed_recall(seeds: list[dict], records: list[dict],
                searched_dbs: Iterable[str] | None = None) -> dict:
    """
    Which seeds were retrieved (by DOI, else by normalized title). A seed that
    was not retrieved and whose source_db is not in `searched_dbs` (default:
    the dbs of `records`) is "pending", not missed; recall is computed over
    found + missing only. A seed without source_db is always evaluated.
    `per_db` holds the same split per source_db (None key for untagged seeds).
    """
    searched = {d.lower() for d in (searched_dbs if searched_dbs is not None
                                    else (r["db"] for r in records))}
    dois = {r["doi"] for r in records if r.get("doi")}
    titles = {title_key(r["title"]) for r in records}
    found, missing, pending = [], [], []
    per_db: dict[str | None, dict] = {}
    for s in seeds:
        hit = (s["doi"] and s["doi"] in dois) or (s["title"] and title_key(s["title"]) in titles)
        db = s.get("source_db")
        bucket = "found" if hit else ("pending" if db and db not in searched else "missing")
        {"found": found, "missing": missing, "pending": pending}[bucket].append(s["id"])
        per_db.setdefault(db, {"found": [], "missing": [], "pending": []})[bucket].append(s["id"])
    for d in per_db.values():
        d["recall"] = _recall(d["found"], d["missing"])
    return {
        "n_seeds": len(seeds),
        "n_found": len(found),
        "n_evaluated": len(found) + len(missing),
        "recall": _recall(found, missing),
        "found": found,
        "missing": missing,
        "pending": pending,
        "searched_dbs": sorted(searched),
        "per_db": per_db,
    }
