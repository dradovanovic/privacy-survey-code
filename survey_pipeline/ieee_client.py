"""
IEEE Xplore Metadata API client.

Design rules
* Every raw page is written to disk before it is parsed, so a run can be
  re-normalized later without spending API quota, and the raw responses can
  be archived as supplementary material.
* One content_type per request (the API filters on a single value); the
  client iterates over the list from the query definition and unions locally.
* Pagination uses start_record in steps of max_records (<= 200).
* 429 / 5xx responses are retried with exponential backoff.
* Every request is appended to data/runs.csv with its total_records, which
  is the number that goes into the PRISMA "records identified" box.

API reference: https://developer.ieee.org/docs/read/Metadata_API_details
"""

from __future__ import annotations

import csv
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator

import requests

from .records import _clean_doi, title_key

BASE_URL = "https://ieeexploreapi.ieee.org/api/v1/search/articles"
RUN_LOG_HEADER = [
    "timestamp", "run_id", "db", "query_id", "content_type", "start_record",
    "max_records", "returned", "total_records", "status", "querytext",
]
# lookup marker: IEEE counts a match but the response carries no article
COUNTED_NOT_RETURNED = "counted_not_returned"


def load_api_key() -> str:
    """Read IEEE_API_KEY from the environment (docker-compose passes .env through)."""
    key = os.environ.get("IEEE_API_KEY")
    if not key:
        try:
            from dotenv import load_dotenv  # optional dependency
            load_dotenv()
            key = os.environ.get("IEEE_API_KEY")
        except ImportError:
            pass
    if not key:
        raise RuntimeError("IEEE_API_KEY not set (export it or put it in .env)")
    return key


def new_run_id() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


class IEEEClient:
    def __init__(self, api_key: str, data_dir: str | Path = "data",
                 sleep_seconds: float = 1.0, timeout: int = 60, max_retries: int = 5):
        self.api_key = api_key
        self.data_dir = Path(data_dir)
        self.sleep = sleep_seconds
        self.timeout = timeout
        self.max_retries = max_retries
        self.session = requests.Session()
        self.run_log = self.data_dir / "runs.csv"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        if not self.run_log.exists():
            with open(self.run_log, "w", newline="", encoding="utf-8") as fh:
                csv.writer(fh).writerow(RUN_LOG_HEADER)

    # ------------------------------------------------------------------ HTTP
    def _get(self, params: dict) -> tuple[dict, int]:
        params = {**params, "apikey": self.api_key, "format": "json"}
        delay = self.sleep
        for attempt in range(1, self.max_retries + 1):
            resp = self.session.get(BASE_URL, params=params, timeout=self.timeout)
            if resp.status_code == 200:
                return resp.json(), 200
            if resp.status_code in (429, 500, 502, 503, 504) and attempt < self.max_retries:
                time.sleep(delay)
                delay *= 2
                continue
            # 400 = malformed query, 401/403 = key problem, or retries exhausted
            try:
                body = resp.json()
            except ValueError:
                body = {"error": resp.text[:500]}
            return body, resp.status_code
        raise RuntimeError("unreachable")

    def _log(self, row: dict) -> None:
        with open(self.run_log, "a", newline="", encoding="utf-8") as fh:
            csv.DictWriter(fh, fieldnames=RUN_LOG_HEADER).writerow(row)

    # --------------------------------------------------------------- lookups
    def _lookup(self, params: dict, raw_name: str, querytext: str,
                query_id: str) -> tuple[list[dict], int, Path]:
        """
        One logged lookup request. The raw response is written to
        data/raw/ieee/lookup/<raw_name>.json before it is parsed. Returns
        (articles, total_records, raw_path).
        """
        body, status = self._get(params)
        raw_dir = self.data_dir / "raw" / "ieee" / "lookup"
        raw_dir.mkdir(parents=True, exist_ok=True)
        raw_path = raw_dir / f"{raw_name}.json"
        raw_path.write_text(json.dumps(body, indent=1), encoding="utf-8")
        articles = (body.get("articles") or []) if status == 200 else []
        total = body.get("total_records", "") if status == 200 else ""
        self._log({
            "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "run_id": "lookup", "db": "ieee", "query_id": query_id, "content_type": "",
            "start_record": 1, "max_records": params.get("max_records", ""),
            "returned": len(articles), "total_records": total,
            "status": status, "querytext": querytext,
        })
        if status != 200:
            raise RuntimeError(f"IEEE API returned {status} for {querytext}: {body}")
        time.sleep(self.sleep)
        return articles, int(total or 0), raw_path

    def lookup_doi(self, doi: str, query_id: str = "doi-lookup") -> dict | None:
        """
        Fetch one record by DOI (the API ignores every other search parameter
        when `doi` is given). Returns the raw article dict, None if IEEE does
        not index it, or the marker {"_status": "counted_not_returned",
        "_raw": <path>} when IEEE counts a match (total_records >= 1) but
        returns no article. Costs one request; logged like any other.
        """
        articles, total, raw_path = self._lookup(
            {"doi": doi, "max_records": 1}, doi.replace("/", "_"), f"doi={doi}", query_id)
        if articles:
            return articles[0]
        if total >= 1:
            return {"_status": COUNTED_NOT_RETURNED, "_raw": str(raw_path)}
        return None

    def lookup_title(self, title: str, doi: str | None = None,
                     query_id: str = "title-lookup") -> dict | None:
        """
        Fetch a record by exact title (article_title, quoted, max_records 5).
        Returns the first article whose DOI equals `doi` or whose normalized
        title equals the normalized `title`; None if no returned article
        matches. Raw response saved and request logged like lookup_doi.
        """
        key = title_key(title)
        articles, _, _ = self._lookup(
            {"article_title": f'"{title}"', "max_records": 5}, f"title_{key[:120]}",
            f'article_title="{title}"', query_id)
        want_doi = _clean_doi(doi)
        for a in articles:
            if (want_doi and _clean_doi(a.get("doi")) == want_doi) or title_key(a.get("title", "")) == key:
                return a
        return None

    # --------------------------------------------------------------- search
    def search(self, query_id: str, params: dict, run_id: str | None = None,
               max_pages: int | None = None) -> Iterator[tuple[dict, Path, str]]:
        """
        Yield (page_json, raw_path, content_type) for every page of every
        content type in params["content_types"]. Pass max_pages=1 for a
        dry run that only measures total_records per content type.
        """
        run_id = run_id or new_run_id()
        base = {k: v for k, v in params.items() if k != "content_types"}
        page_size = int(base.get("max_records", 200))
        content_types = params.get("content_types") or [None]
        raw_dir = self.data_dir / "raw" / "ieee" / query_id / run_id
        raw_dir.mkdir(parents=True, exist_ok=True)
        (raw_dir / "params.json").write_text(json.dumps(params, indent=2), encoding="utf-8")

        for ct in content_types:
            start, page, total = 1, 0, None
            while True:
                page += 1
                p = {**base, "start_record": start, "max_records": page_size}
                if ct:
                    p["content_type"] = ct
                body, status = self._get(p)
                articles = body.get("articles", []) if status == 200 else []
                total = body.get("total_records", total) if status == 200 else total
                fname = f"{(ct or 'all').replace(' ', '_')}_p{page:03d}_s{start:06d}.json"
                raw_path = raw_dir / fname
                raw_path.write_text(json.dumps(body, indent=1), encoding="utf-8")
                self._log({
                    "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                    "run_id": run_id, "db": "ieee", "query_id": query_id,
                    "content_type": ct or "", "start_record": start, "max_records": page_size,
                    "returned": len(articles), "total_records": total if total is not None else "",
                    "status": status, "querytext": base.get("querytext", ""),
                })
                if status != 200:
                    raise RuntimeError(f"IEEE API returned {status} for content_type={ct}: {body}")
                yield body, raw_path, ct or ""
                if not articles or (total is not None and start + len(articles) > total):
                    break
                if max_pages and page >= max_pages:
                    break
                start += len(articles)
                time.sleep(self.sleep)
