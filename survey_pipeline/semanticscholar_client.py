"""
Semantic Scholar Academic Graph API client for abstract backfill
(POST graph/v1/paper/batch, fields=abstract).

Design rules
* SEMANTIC_SCHOLAR_API_KEY, when set, is sent as the x-api-key header (never
  in the URL, runs.csv or raw files). Without it the shared unauthenticated
  pool is used, which throttles hard.
* Rate limit: keys start at 1 request per second, so requests are spaced by
  at least sleep_seconds (default 1.1 s); 429 / 5xx are retried with
  exponential backoff, honouring Retry-After.
* The batch response is a list aligned with the request ids (null for an
  unknown id), so each batch is saved as two files under
  data/raw/semanticscholar/backfill/<run_id>/: batch_sNNNNNN.json (response,
  untouched) and batch_sNNNNNN.request.json (the ids sent).
* Every request is appended to data/runs.csv with content_type
  "abstract_backfill".

API reference: https://api.semanticscholar.org/api-docs/graph#tag/Paper-Data/operation/post_graph_get_papers
"""

from __future__ import annotations

import csv
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

from .ieee_client import RUN_LOG_HEADER

BATCH_URL = "https://api.semanticscholar.org/graph/v1/paper/batch"
BATCH_MAX = 500     # ids per request (API maximum)
FIELDS = "abstract,externalIds"


def load_api_key() -> str | None:
    """SEMANTIC_SCHOLAR_API_KEY from the environment / .env; optional."""
    key = os.environ.get("SEMANTIC_SCHOLAR_API_KEY")
    if not key:
        try:
            from dotenv import load_dotenv  # optional dependency
            load_dotenv()
            key = os.environ.get("SEMANTIC_SCHOLAR_API_KEY")
        except ImportError:
            pass
    return key or None


def abstracts_by_doi(ids: list[str], response: list) -> dict[str, str]:
    """{doi: abstract} from a batch request (DOI:<doi> ids) and its aligned response."""
    out = {}
    for rid, paper in zip(ids, response):
        if paper and paper.get("abstract") and rid.startswith("DOI:"):
            out[rid[4:].lower()] = paper["abstract"].strip()
    return out


class SemanticScholarClient:
    def __init__(self, api_key: str | None = None, data_dir: str | Path = "data",
                 sleep_seconds: float = 1.1, timeout: int = 60, max_retries: int = 6):
        self.api_key = api_key
        self.data_dir = Path(data_dir)
        self.sleep = sleep_seconds
        self.timeout = timeout
        self.max_retries = max_retries
        self.session = requests.Session()
        self._last = 0.0
        self.run_log = self.data_dir / "runs.csv"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        if not self.run_log.exists():
            with open(self.run_log, "w", newline="", encoding="utf-8") as fh:
                csv.writer(fh).writerow(RUN_LOG_HEADER)

    def _post(self, ids: list[str]) -> tuple[list | dict, int]:
        headers = {"x-api-key": self.api_key} if self.api_key else {}
        delay = max(self.sleep, 1.0)
        for attempt in range(1, self.max_retries + 1):
            wait = self.sleep - (time.monotonic() - self._last)
            if wait > 0:
                time.sleep(wait)
            resp = self.session.post(BATCH_URL, params={"fields": FIELDS}, json={"ids": ids},
                                     headers=headers, timeout=self.timeout)
            self._last = time.monotonic()
            if resp.status_code == 200:
                return resp.json(), 200
            if resp.status_code in (429, 500, 502, 503, 504) and attempt < self.max_retries:
                time.sleep(float(resp.headers.get("Retry-After") or delay))
                delay *= 2
                continue
            try:
                body = resp.json()
            except ValueError:
                body = {"error": resp.text[:500]}
            return body, resp.status_code
        raise RuntimeError("unreachable")

    def batch(self, dois: list[str], query_id: str, run_id: str, start: int = 0) -> tuple[list, list[str], Path]:
        """One logged request for up to BATCH_MAX DOIs. Returns (response list, ids sent, raw_path)."""
        if not 0 < len(dois) <= BATCH_MAX:
            raise ValueError(f"1 to {BATCH_MAX} DOIs per request")
        ids = [f"DOI:{d}" for d in dois]
        body, status = self._post(ids)
        raw_dir = self.data_dir / "raw" / "semanticscholar" / "backfill" / run_id
        raw_dir.mkdir(parents=True, exist_ok=True)
        raw_path = raw_dir / f"batch_s{start:06d}.json"
        raw_path.write_text(json.dumps(body, indent=1), encoding="utf-8")
        (raw_dir / f"batch_s{start:06d}.request.json").write_text(
            json.dumps({"fields": FIELDS, "ids": ids}, indent=1), encoding="utf-8")
        found = sum(1 for p in body if p) if status == 200 else 0
        with open(self.run_log, "a", newline="", encoding="utf-8") as fh:
            csv.DictWriter(fh, fieldnames=RUN_LOG_HEADER).writerow({
                "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                "run_id": run_id, "db": "semanticscholar", "query_id": query_id,
                "content_type": "abstract_backfill", "start_record": start, "max_records": len(ids),
                "returned": found, "total_records": len(ids), "status": status,
                "querytext": f"paper/batch fields={FIELDS} ids=DOI:<{len(ids)} DOIs>",
            })
        if status != 200:
            raise RuntimeError(f"Semantic Scholar returned {status}: {body}")
        return body, ids, raw_path
