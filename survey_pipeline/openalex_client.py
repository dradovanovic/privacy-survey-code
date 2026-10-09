"""
OpenAlex works API client (mirrors ieee_client.py).

Design rules
* Every raw page is written to disk before it is parsed (data/raw/openalex/
  <query_id>/<run_id>/), so a run can be re-normalized without spending
  budget. Raw pages keep fields the normalized schema drops (referenced_works,
  topics, locations), which snowballing can reuse.
* The compiled filter string is sent unchanged as `filter`.
* Cursor pagination (cursor=* then meta.next_cursor), per-page 100: the
  documented maximum (help.openalex.org/api/paging/; older docs said 200).
* OPENALEX_API_KEY is sent as an Authorization header, never in the URL, so
  it cannot leak into logs, raw pages or error messages.
* 429 / 5xx responses are retried with exponential backoff. A `.search`
  filter call is billed at the search rate against the daily budget.
* Every request is appended to data/runs.csv; meta.count is the PRISMA
  "records identified" number.

API reference: https://help.openalex.org/api/
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

from .ieee_client import RUN_LOG_HEADER, new_run_id

BASE_URL = "https://api.openalex.org/works"
MAX_PAGE = 100
DOI_BATCH = 50   # DOIs per filter=doi:a|b|... request; OpenAlex allows up to 100 OR values, 50 keeps URLs short


def load_api_key() -> str:
    """Read OPENALEX_API_KEY from the environment (docker-compose passes .env through)."""
    key = os.environ.get("OPENALEX_API_KEY")
    if not key:
        try:
            from dotenv import load_dotenv  # optional dependency
            load_dotenv()
            key = os.environ.get("OPENALEX_API_KEY")
        except ImportError:
            pass
    if not key:
        raise RuntimeError("OPENALEX_API_KEY not set (export it or put it in .env)")
    return key


def page_total(body: dict) -> int:
    return int((body.get("meta") or {}).get("count") or 0)


def page_items(body: dict) -> list[dict]:
    return body.get("results") or []


class OpenAlexClient:
    def __init__(self, api_key: str, data_dir: str | Path = "data", page_size: int = MAX_PAGE,
                 sleep_seconds: float = 1.0, timeout: int = 60, max_retries: int = 5):
        self.api_key = api_key
        self.page_size = min(page_size, MAX_PAGE)
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
        headers = {"Authorization": f"Bearer {self.api_key}", "Accept": "application/json"}
        delay = self.sleep
        for attempt in range(1, self.max_retries + 1):
            resp = self.session.get(BASE_URL, params=params, headers=headers, timeout=self.timeout)
            if resp.status_code == 200:
                return resp.json(), 200
            if resp.status_code in (429, 500, 502, 503, 504) and attempt < self.max_retries:
                time.sleep(delay)
                delay *= 2
                continue
            # 400 = malformed filter, 401/403 = key problem, 429 = budget exhausted
            try:
                body = resp.json()
            except ValueError:
                body = {"error": resp.text[:500]}
            return body, resp.status_code
        raise RuntimeError("unreachable")

    def _log(self, row: dict) -> None:
        with open(self.run_log, "a", newline="", encoding="utf-8") as fh:
            csv.DictWriter(fh, fieldnames=RUN_LOG_HEADER).writerow(row)

    # ------------------------------------------------------------ DOI batch
    def works_by_doi(self, dois: list[str], query_id: str, run_id: str,
                     start: int = 0) -> tuple[dict, Path]:
        """
        One logged request for up to DOI_BATCH works by DOI (filter=doi:a|b|...).
        The raw response is written to data/raw/openalex/backfill/<run_id>/
        before it is parsed. runs.csv content_type is "abstract_backfill", so
        these rows are not counted as search results.
        """
        raw_path = self.data_dir / "raw" / "openalex" / "backfill" / run_id / f"batch_s{start:06d}.json"
        return self._doi_request(dois, query_id, run_id, raw_path, "abstract_backfill", start), raw_path

    def lookup_doi(self, doi: str, query_id: str = "manual-lookup") -> tuple[dict | None, Path]:
        """
        One logged request for a single DOI; raw response in
        data/raw/openalex/lookup/<doi>.json, runs.csv run_id "lookup".
        Returns (first work or None if OpenAlex has no work with that DOI, raw_path).
        """
        raw_path = self.data_dir / "raw" / "openalex" / "lookup" / f"{doi.replace('/', '_')}.json"
        items = page_items(self._doi_request([doi], query_id, "lookup", raw_path, "", 0))
        return (items[0] if items else None), raw_path

    def _doi_request(self, dois: list[str], query_id: str, run_id: str, raw_path: Path,
                     content_type: str, start: int) -> dict:
        if not 0 < len(dois) <= DOI_BATCH:
            raise ValueError(f"1 to {DOI_BATCH} DOIs per request")
        bad = [d for d in dois if "," in d or "|" in d]
        if bad:
            raise ValueError(f"DOIs containing ',' or '|' cannot go into a filter: {bad}")
        flt = "doi:" + "|".join(dois)
        body, status = self._get({"filter": flt, "per-page": MAX_PAGE})
        raw_path.parent.mkdir(parents=True, exist_ok=True)
        raw_path.write_text(json.dumps(body, indent=1), encoding="utf-8")
        self._log({
            "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "run_id": run_id, "db": "openalex", "query_id": query_id,
            "content_type": content_type, "start_record": start, "max_records": len(dois),
            "returned": len(page_items(body)) if status == 200 else 0,
            "total_records": page_total(body) if status == 200 else "",
            "status": status, "querytext": flt,
        })
        if status != 200:
            raise RuntimeError(f"OpenAlex API returned {status}: {body}")
        return body

    # --------------------------------------------------------------- search
    def search(self, query_id: str, params: dict, run_id: str | None = None,
               max_pages: int | None = None) -> Iterator[tuple[dict, Path, str]]:
        """
        Yield (page_json, raw_path, "") for every page of params["filter"].
        Same contract as IEEEClient.search; max_pages=1 is a dry run that only
        measures meta.count.
        """
        run_id = run_id or new_run_id()
        base = {"filter": params["filter"], "per-page": self.page_size}
        raw_dir = self.data_dir / "raw" / "openalex" / query_id / run_id
        raw_dir.mkdir(parents=True, exist_ok=True)
        (raw_dir / "params.json").write_text(json.dumps(base, indent=2), encoding="utf-8")

        cursor, offset, page, total = "*", 0, 0, None
        while True:
            page += 1
            body, status = self._get({**base, "cursor": cursor})
            items = page_items(body) if status == 200 else []
            total = page_total(body) if status == 200 else total
            raw_path = raw_dir / f"all_p{page:03d}_s{offset:06d}.json"
            raw_path.write_text(json.dumps(body, indent=1), encoding="utf-8")
            self._log({
                "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                "run_id": run_id, "db": "openalex", "query_id": query_id,
                "content_type": "", "start_record": offset, "max_records": self.page_size,
                "returned": len(items), "total_records": total if total is not None else "",
                "status": status, "querytext": base["filter"],
            })
            if status != 200:
                raise RuntimeError(f"OpenAlex API returned {status}: {body}")
            yield body, raw_path, ""
            offset += len(items)
            nxt = (body.get("meta") or {}).get("next_cursor")
            if not items or not nxt or (total is not None and offset >= total):
                break
            if max_pages and page >= max_pages:
                break
            cursor = nxt
            time.sleep(self.sleep)
