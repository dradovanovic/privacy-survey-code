"""
Compile a stream query definition (queries/*.json) into database-specific
search strings and API parameters.

One JSON file is the single source of truth for a search. Every database
string is derived from it, so the methodology section can state that all
databases were searched with the same concept groups, and the compiled
strings can be printed verbatim into the supplement.

Supported targets
-----------------
ieee    IEEE Xplore Metadata API  (querytext + filter params)
scopus  Scopus Search API         (TITLE-ABS-KEY / TITLE syntax)
wos     Web of Science            (TS= / TI= advanced search, paste into UI or API)
acm     ACM Digital Library       (bracket syntax for the advanced-search box)
openalex OpenAlex works API       (filter=title_and_abstract.search boolean + filters)

IEEE constraints encoded here (developer.ieee.org, "Search Parameters"):
* at most two wildcard words per query, each with >= 3 leading characters
* max 200 records per call, paginated with start_record
* boolean operators AND / OR / NOT with parentheses and quoted phrases
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

IEEE_MAX_WILDCARDS = 2
FIELD_SETS = {"title", "abstract", "keywords"}


class QueryValidationError(ValueError):
    pass


@dataclass
class CompiledQuery:
    db: str
    query_id: str
    display: str                     # human-readable string for logs / supplement
    params: dict[str, Any] = field(default_factory=dict)   # API params (ieee, scopus)
    notes: list[str] = field(default_factory=list)


# ----------------------------------------------------------------------------
# Loading and validation
# ----------------------------------------------------------------------------

def load_query(path: str | Path) -> dict:
    with open(path, encoding="utf-8") as fh:
        query = json.load(fh)
    validate(query)
    return query


def validate(query: dict) -> None:
    for key in ("query_id", "stream", "concept_groups"):
        if key not in query:
            raise QueryValidationError(f"missing top-level key: {key}")
    groups = query["concept_groups"]
    if not groups:
        raise QueryValidationError("concept_groups is empty")
    for name, group in groups.items():
        terms = _terms(group)
        if not terms:
            raise QueryValidationError(f"concept group '{name}' has no terms")
        for f in _fields(group):
            if f not in FIELD_SETS:
                raise QueryValidationError(f"unknown field '{f}' in group '{name}'")
    wildcard_terms = [t for g in groups.values() for t in _terms(g) if "*" in t]
    if len(wildcard_terms) > IEEE_MAX_WILDCARDS:
        raise QueryValidationError(
            f"IEEE allows at most {IEEE_MAX_WILDCARDS} wildcard words per query; "
            f"found {len(wildcard_terms)}: {wildcard_terms}. Enumerate variants instead."
        )
    for t in wildcard_terms:
        stem = t.split("*")[0].split()[-1]
        if len(stem) < 3:
            raise QueryValidationError(f"wildcard term '{t}' needs >= 3 characters before '*'")


def _terms(group: dict | list) -> list[str]:
    # Backwards compatible with the plain-list format {"domain": ["smart meter", ...]}
    if isinstance(group, list):
        return group
    return group.get("terms", [])


def _fields(group: dict | list) -> list[str]:
    if isinstance(group, list):
        return ["title", "abstract", "keywords"]
    return group.get("fields", ["title", "abstract", "keywords"])


def _operator(group: dict | list) -> str:
    if isinstance(group, list):
        return "OR"
    return group.get("operator", "OR").upper()


def _quote(term: str) -> str:
    """Quote phrases; leave single alphanumeric tokens bare."""
    if re.fullmatch(r"[A-Za-z0-9*]+", term):
        return term
    return f'"{term}"'


def _join(terms: list[str], op: str) -> str:
    return f" {op} ".join(_quote(t) for t in terms)


# ----------------------------------------------------------------------------
# IEEE Xplore
# ----------------------------------------------------------------------------

def compile_ieee(query: dict) -> CompiledQuery:
    """
    Build the querytext for the IEEE Metadata API.

    Groups searched in title+abstract+keywords are emitted as plain boolean
    clauses (querytext searches all configured metadata fields plus abstract,
    which is a slight superset: it also matches publication titles and index
    terms). A group restricted to the title only is emitted with the Xplore
    field qualifier "Document Title". Verify field-qualified syntax once in
    the Dynamic Query Tool (developer.ieee.org/io-docs); if it is rejected,
    run the unrestricted query and apply the title restriction locally with
    the sensitivity-variant filter, which is logically equivalent.
    """
    clauses = []
    notes = []
    for name, group in query["concept_groups"].items():
        terms, fields, op = _terms(group), set(_fields(group)), _operator(group)
        if fields == {"title"}:
            inner = f" {op} ".join(f'("Document Title":{_quote(t)})' for t in terms)
            notes.append(f"group '{name}' title-restricted via \"Document Title\" qualifier")
        else:
            inner = _join(terms, op)
            if fields != FIELD_SETS:
                notes.append(
                    f"group '{name}' requested fields {sorted(fields)} but IEEE querytext "
                    "searches all metadata; restriction applied locally in normalize step"
                )
        clauses.append(f"({inner})")
    gop = query.get("group_operator", "AND").upper()
    querytext = f" {gop} ".join(clauses)
    excl = query.get("exclusion_terms") or []
    if excl:
        querytext = f"({querytext}) NOT ({_join(excl, 'OR')})"

    filters = query.get("filters", {})
    params: dict[str, Any] = {"querytext": querytext}
    if "start_year" in filters:
        params["start_year"] = filters["start_year"]
    if "end_year" in filters:
        params["end_year"] = filters["end_year"]
    content_types = filters.get("content_types", {}).get("ieee", [])
    # The API takes one content_type per call; the client iterates over this list.
    params["content_types"] = content_types
    params["max_records"] = min(int(query.get("retrieval", {}).get("page_size", 200)), 200)

    display = querytext
    if content_types:
        display += f"\n  content_type ∈ {content_types}"
    if "start_year" in filters or "end_year" in filters:
        display += f"\n  years {filters.get('start_year', '')}–{filters.get('end_year', '')}"
    return CompiledQuery("ieee", query["query_id"], display, params, notes)


# ----------------------------------------------------------------------------
# Scopus
# ----------------------------------------------------------------------------

def compile_scopus(query: dict) -> CompiledQuery:
    clauses = []
    for name, group in query["concept_groups"].items():
        terms, fields, op = _terms(group), set(_fields(group)), _operator(group)
        if fields == {"title"}:
            func = "TITLE"
        elif fields == {"abstract"}:
            func = "ABS"
        elif fields == {"keywords"}:
            func = "KEY"
        else:
            func = "TITLE-ABS-KEY"
        clauses.append(f"{func}({_join(terms, op)})")
    gop = query.get("group_operator", "AND").upper()
    q = f" {gop} ".join(clauses)
    excl = query.get("exclusion_terms") or []
    if excl:
        q = f"({q}) AND NOT TITLE-ABS-KEY({_join(excl, 'OR')})"

    filters = query.get("filters", {})
    if "start_year" in filters:
        q += f" AND PUBYEAR > {int(filters['start_year']) - 1}"
    if "end_year" in filters:
        q += f" AND PUBYEAR < {int(filters['end_year']) + 1}"
    doctypes = filters.get("content_types", {}).get("scopus_doctypes", [])
    if doctypes:
        q += " AND (" + " OR ".join(f"DOCTYPE({d})" for d in doctypes) + ")"
    for lang in filters.get("languages", []):
        q += f" AND LANGUAGE({lang.lower()})"
    return CompiledQuery("scopus", query["query_id"], q, {"query": q})


# ----------------------------------------------------------------------------
# Web of Science (advanced search)
# ----------------------------------------------------------------------------

def compile_wos(query: dict) -> CompiledQuery:
    clauses = []
    for name, group in query["concept_groups"].items():
        terms, fields, op = _terms(group), set(_fields(group)), _operator(group)
        tag = "TI" if fields == {"title"} else "TS"   # TS = topic (title, abstract, keywords)
        clauses.append(f"{tag}=({_join(terms, op)})")
    gop = query.get("group_operator", "AND").upper()
    q = f" {gop} ".join(clauses)
    excl = query.get("exclusion_terms") or []
    if excl:
        q = f"({q}) NOT TS=({_join(excl, 'OR')})"
    filters = query.get("filters", {})
    if "start_year" in filters or "end_year" in filters:
        q += f" AND PY=({filters.get('start_year', 1900)}-{filters.get('end_year', 2100)})"
    return CompiledQuery("wos", query["query_id"], q, {"query": q},
                         ["paste into WoS Advanced Search; export as RIS/BibTeX with abstracts"])


# ----------------------------------------------------------------------------
# ACM Digital Library (advanced search box syntax)
# ----------------------------------------------------------------------------

def compile_acm(query: dict) -> CompiledQuery:
    def field_clause(fld: str, terms: list[str], op: str) -> str:
        return "[" + f" {op} ".join(f"[{fld}: {t}]" for t in terms) + "]"

    clauses = []
    for name, group in query["concept_groups"].items():
        terms, fields, op = _terms(group), set(_fields(group)), _operator(group)
        if fields == {"title"}:
            clauses.append(field_clause("Title", terms, op))
        else:
            # ACM has no combined title+abstract+keyword field; OR the three.
            parts = [field_clause(f, terms, op) for f in ("Title", "Abstract", "Keyword")]
            clauses.append("[" + " OR ".join(parts) + "]")
    gop = query.get("group_operator", "AND").upper()
    q = f" {gop} ".join(clauses)
    filters = query.get("filters", {})
    note = "paste into ACM DL Advanced Search 'Search Within' box"
    if "start_year" in filters:
        note += f"; set publication date filter {filters.get('start_year')}–{filters.get('end_year', '')}"
    return CompiledQuery("acm", query["query_id"], q, {"query": q}, [note])


# ----------------------------------------------------------------------------
# OpenAlex (works endpoint, filter=title_and_abstract.search)
# ----------------------------------------------------------------------------

OPENALEX_BASE_URL = "https://api.openalex.org/works"
OPENALEX_MAX_URL = 3500            # bytes; OpenAlex documents ~4 KB per request URL
# Scopus doctypes -> OpenAlex work types (help.openalex.org/data/work-types/)
OPENALEX_TYPES = {"ar": "article", "re": "review", "cp": "conference-paper", "ch": "book-chapter"}


def compile_openalex(query: dict) -> CompiledQuery:
    """
    One boolean string in filter=title_and_abstract.search:(...), ANDed with
    publication_year, language and type filters. OpenAlex searches title and
    abstract only (no keyword field) and stems quoted phrases too. A comma
    separates filters, so the boolean string must not contain one. Fails when
    the request URL (without the API key, which travels in a header) exceeds
    OPENALEX_MAX_URL.
    """
    from urllib.parse import urlencode

    clauses = [f"({_join(_terms(g), _operator(g))})" for g in query["concept_groups"].values()]
    gop = query.get("group_operator", "AND").upper()
    boolean = f" {gop} ".join(clauses)
    excl = query.get("exclusion_terms") or []
    if excl:
        boolean = f"({boolean}) NOT ({_join(excl, 'OR')})"
    if "," in boolean:
        raise QueryValidationError("OpenAlex: a comma inside the search string would split the filter")

    parts = [f"title_and_abstract.search:({boolean})"]
    filters = query.get("filters", {})
    if "start_year" in filters or "end_year" in filters:
        parts.append(f"publication_year:{filters.get('start_year', '')}-{filters.get('end_year', '')}")
    langs = [{"english": "en"}.get(l.lower(), l.lower()) for l in filters.get("languages", [])]
    if langs:
        parts.append("language:" + "|".join(langs))
    ct = filters.get("content_types", {})
    types = ct.get("openalex") or [OPENALEX_TYPES[d] for d in ct.get("scopus_doctypes", []) if d in OPENALEX_TYPES]
    if types:
        parts.append("type:" + "|".join(types))
    flt = ",".join(parts)

    url = f"{OPENALEX_BASE_URL}?{urlencode({'filter': flt})}"
    n = len(url.encode("utf-8"))
    if n > OPENALEX_MAX_URL:
        raise QueryValidationError(f"OpenAlex request URL is {n} bytes (limit {OPENALEX_MAX_URL}); split the query")
    notes = [f"request URL length: {n} bytes (limit {OPENALEX_MAX_URL}; API key sent as a header)",
             "searches title and abstract only; keywords are not searchable in OpenAlex",
             "quoted phrases are stemmed as well (OpenAlex search semantics)"]
    if not ct.get("openalex"):
        notes.append(f"types derived from scopus_doctypes: {'|'.join(types)}")
    return CompiledQuery("openalex", query["query_id"], flt, {"filter": flt}, notes)


COMPILERS = {
    "ieee": compile_ieee,
    "scopus": compile_scopus,
    "wos": compile_wos,
    "acm": compile_acm,
    "openalex": compile_openalex,
}


def compile_all(query: dict) -> dict[str, CompiledQuery]:
    return {db: fn(query) for db, fn in COMPILERS.items()}


# ----------------------------------------------------------------------------
# Sensitivity variants (applied locally to normalized records)
# ----------------------------------------------------------------------------

def apply_variant(query: dict, variant_name: str) -> dict:
    """Return a modified copy of the query definition for a named variant."""
    variants = query.get("sensitivity_variants", {})
    if variant_name not in variants:
        raise KeyError(f"unknown variant '{variant_name}'; available: {list(variants)}")
    spec = variants[variant_name]
    q = json.loads(json.dumps(query))  # deep copy
    q["query_id"] = f"{query['query_id']}+{variant_name}"
    if "restrict_group_to_title" in spec:
        g = spec["restrict_group_to_title"]
        grp = q["concept_groups"][g]
        if isinstance(grp, list):
            q["concept_groups"][g] = {"terms": grp, "fields": ["title"]}
        else:
            grp["fields"] = ["title"]
    for g, drop in (spec.get("drop_terms") or {}).items():
        grp = q["concept_groups"][g]
        terms = _terms(grp)
        kept = [t for t in terms if t not in drop]
        if isinstance(grp, list):
            q["concept_groups"][g] = kept
        else:
            grp["terms"] = kept
    for g, add in (spec.get("add_terms") or {}).items():
        grp = q["concept_groups"][g]
        if isinstance(grp, list):
            grp.extend(add)
        else:
            grp["terms"] = _terms(grp) + list(add)
    return q
