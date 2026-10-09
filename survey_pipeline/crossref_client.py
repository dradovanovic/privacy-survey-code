"""
Crossref REST API client for abstract backfill (one work per DOI).

Design rules
* Polite pool: CROSSREF_MAILTO is sent as the `mailto` parameter and in the
  User-Agent. It is required, so every request identifies the project.
  It is not written to runs.csv or the raw files.
* Every response is written to data/raw/crossref/backfill/<run_id>/ before it
  is parsed; a 404 (DOI not registered with Crossref) is saved as
  {"status": 404, "message": ...} so a replay sees the same outcome.
* 429 / 5xx responses are retried with exponential backoff, honouring
  Retry-After. A pause of sleep_seconds separates requests.
* Every request is appended to data/runs.csv with content_type
  "abstract_backfill", so these rows are not counted as search results.

API reference: https://api.crossref.org/swagger-ui/index.html
"""

from __future__ import annotations

import csv
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote

import requests

from .ieee_client import RUN_LOG_HEADER

BASE_URL = "https://api.crossref.org/works/"


def load_mailto() -> str:
    """CROSSREF_MAILTO from the environment (docker-compose passes .env through)."""
    mailto = os.environ.get("CROSSREF_MAILTO")
    if not mailto:
        try:
            from dotenv import load_dotenv  # optional dependency
            load_dotenv()
            mailto = os.environ.get("CROSSREF_MAILTO")
        except ImportError:
            pass
    if not mailto:
        raise RuntimeError("CROSSREF_MAILTO not set (put a contact address in .env for the polite pool)")
    return mailto


def raw_name(doi: str) -> str:
    """File name for a DOI; percent-encoded, because DOIs may contain characters Windows forbids."""
    return quote(doi, safe="") + ".json"


def work_message(body: dict) -> dict | None:
    """The work record of a saved response, or None for a 404 / error body."""
    return body.get("message") if body.get("status") == "ok" else None


class CrossrefClient:
    def __init__(self, mailto: str, data_dir: str | Path = "data", sleep_seconds: float = 0.2,
                 timeout: int = 60, max_retries: int = 5):
        self.mailto = mailto
        self.data_dir = Path(data_dir)
        self.sleep = sleep_seconds
        self.timeout = timeout
        self.max_retries = max_retries
        self.session = requests.Session()
        self.session.headers["User-Agent"] = f"survey_pipeline/1.0 (mailto:{mailto})"
        self.run_log = self.data_dir / "runs.csv"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        if not self.run_log.exists():
            with open(self.run_log, "w", newline="", encoding="utf-8") as fh:
                csv.writer(fh).writerow(RUN_LOG_HEADER)

    def _get(self, doi: str) -> tuple[dict, int]:
        delay = self.sleep or 1.0
        for attempt in range(1, self.max_retries + 1):
            resp = self.session.get(BASE_URL + quote(doi, safe=""), params={"mailto": self.mailto},
                                    timeout=self.timeout)
            if resp.status_code == 200:
                return resp.json(), 200
            if resp.status_code in (429, 500, 502, 503, 504) and attempt < self.max_retries:
                time.sleep(float(resp.headers.get("Retry-After") or delay))
                delay *= 2
                continue
            return {"status": resp.status_code, "message": resp.text[:500]}, resp.status_code
        raise RuntimeError("unreachable")

    def work(self, doi: str, query_id: str, run_id: str, n: int = 0) -> tuple[dict | None, Path]:
        """
        One logged request for one DOI. Returns (work record or None, raw_path).
        404 is a normal outcome (DOI not registered with Crossref); other
        errors raise after the response is saved and logged.
        """
        body, status = self._get(doi)
        raw_dir = self.data_dir / "raw" / "crossref" / "backfill" / run_id
        raw_dir.mkdir(parents=True, exist_ok=True)
        raw_path = raw_dir / raw_name(doi)
        raw_path.write_text(json.dumps(body, indent=1), encoding="utf-8")
        with open(self.run_log, "a", newline="", encoding="utf-8") as fh:
            csv.DictWriter(fh, fieldnames=RUN_LOG_HEADER).writerow({
                "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                "run_id": run_id, "db": "crossref", "query_id": query_id,
                "content_type": "abstract_backfill", "start_record": n, "max_records": 1,
                "returned": int(status == 200), "total_records": int(status == 200),
                "status": status, "querytext": f"works/{doi}",
            })
        if status not in (200, 404):
            raise RuntimeError(f"Crossref returned {status} for {doi}: {body.get('message')}")
        return work_message(body), raw_path
