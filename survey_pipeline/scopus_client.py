"""
Scopus Search API client (mirrors ieee_client.py).

Design rules
* Every raw page is written to disk before it is parsed (data/raw/scopus/
  <query_id>/<run_id>/), so a run can be re-normalized without spending quota.
* The compiled TITLE-ABS-KEY string is sent unchanged as `query`.
* Cursor pagination (cursor=* then cursor/@next), which is not capped at
  5,000 results like start-offset pagination. The offset is still logged as
  start_record so runs.csv reads like an IEEE run.
* view=COMPLETE returns abstracts and author keywords (needed for screening)
  but allows at most 25 records per page and needs institutional entitlement
  (IP range or SCOPUS_INST_TOKEN); view=STANDARD allows 200 per page but has
  no abstract.
* 429 / 5xx responses are retried with exponential backoff.
* Every request is appended to data/runs.csv; opensearch:totalResults is the
  PRISMA "records identified" number.

API reference: https://dev.elsevier.com/documentation/ScopusSearchAPI.wadl
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

from .ieee_client import RUN_LOG_HEADER, new_run_id  # noqa: F401  (re-exported for the CLI)

BASE_URL = "https://api.elsevier.com/content/search/scopus"
MAX_PAGE = {"COMPLETE": 25, "STANDARD": 200}


def load_api_keys() -> tuple[str, str | None]:
    """SCOPUS_API_KEY (required) and SCOPUS_INST_TOKEN (optional) from the environment / .env."""
    key, token = os.environ.get("SCOPUS_API_KEY"), os.environ.get("SCOPUS_INST_TOKEN")
    if not key:
        try:
            from dotenv import load_dotenv  # optional dependency
            load_dotenv()
            key, token = os.environ.get("SCOPUS_API_KEY"), os.environ.get("SCOPUS_INST_TOKEN")
        except ImportError:
            pass
    if not key:
        raise RuntimeError("SCOPUS_API_KEY not set (export it or put it in .env)")
    return key, token or None


def page_total(body: dict) -> int:
    return int(body.get("search-results", {}).get("opensearch:totalResults") or 0)


def page_items(body: dict) -> list[dict]:
    """Entries of one page; Scopus signals an empty result with an entry that only carries 'error'."""
    return [e for e in body.get("search-results", {}).get("entry") or [] if "error" not in e]


class ScopusClient:
    def __init__(self, api_key: str, inst_token: str | None = None, data_dir: str | Path = "data",
                 view: str = "COMPLETE", sleep_seconds: float = 1.0, timeout: int = 60,
                 max_retries: int = 5):
        if view not in MAX_PAGE:
            raise ValueError(f"view must be one of {sorted(MAX_PAGE)}")
        self.api_key = api_key
        self.inst_token = inst_token
        self.view = view
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
        headers = {"X-ELS-APIKey": self.api_key, "Accept": "application/json"}
        if self.inst_token:
            headers["X-ELS-Insttoken"] = self.inst_token
        delay = self.sleep
        for attempt in range(1, self.max_retries + 1):
            resp = self.session.get(BASE_URL, params=params, headers=headers, timeout=self.timeout)
            if resp.status_code == 200:
                return resp.json(), 200
            if resp.status_code in (429, 500, 502, 503, 504) and attempt < self.max_retries:
                time.sleep(delay)
                delay *= 2
                continue
            # 400 = malformed query, 401/403 = key or entitlement problem, or retries exhausted
            try:
                body = resp.json()
            except ValueError:
                body = {"error": resp.text[:500]}
            return body, resp.status_code
        raise RuntimeError("unreachable")

    def _log(self, row: dict) -> None:
        with open(self.run_log, "a", newline="", encoding="utf-8") as fh:
            csv.DictWriter(fh, fieldnames=RUN_LOG_HEADER).writerow(row)

    # --------------------------------------------------------------- search
    def search(self, query_id: str, params: dict, run_id: str | None = None,
               max_pages: int | None = None) -> Iterator[tuple[dict, Path, str]]:
        """
        Yield (page_json, raw_path, "") for every page of the query in
        params["query"]. Same contract as IEEEClient.search; the third element
        (content type) is empty because Scopus filters document types in the
        query string. max_pages=1 is a dry run that only measures totalResults.
        """
        run_id = run_id or new_run_id()
        page_size = min(int(params.get("max_records", MAX_PAGE[self.view])), MAX_PAGE[self.view])
        base = {"query": params["query"], "view": self.view, "count": page_size}
        raw_dir = self.data_dir / "raw" / "scopus" / query_id / run_id
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
                "run_id": run_id, "db": "scopus", "query_id": query_id,
                "content_type": "", "start_record": offset, "max_records": page_size,
                "returned": len(items), "total_records": total if total is not None else "",
                "status": status, "querytext": base["query"],
            })
            if status != 200:
                raise RuntimeError(f"Scopus API returned {status} (view={self.view}): {body}")
            yield body, raw_path, ""
            offset += len(items)
            nxt = body.get("search-results", {}).get("cursor", {}).get("@next")
            if not items or not nxt or (total is not None and offset >= total):
                break
            if max_pages and page >= max_pages:
                break
            cursor = nxt
            time.sleep(self.sleep)
