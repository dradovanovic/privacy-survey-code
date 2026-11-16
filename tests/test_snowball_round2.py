"""Snowballing round 2 options (DECISION.md D23): snowball --tag / --seen / --corpus-mark, sb_screen.py --round 2."""
import csv
import json
import sys
from pathlib import Path

import pytest

from survey_pipeline import snowball
from survey_pipeline.cli import main

from test_snowball import QID, _csv, project  # noqa: F401  (fixture)

sys.path.insert(0, str(Path(__file__).parent.parent / "screening"))
import sb_screen  # noqa: E402


def _round2_files(data: Path):
    """Mark corpus: the 3 corpus papers plus one more; seen file: two works of the stub run."""
    mark = data / "screening" / "mark.csv"
    mark.write_text("n,record_id,source,doi,title\n1,openalex:W1,main,10.1/c1,Corpus one\n"
                    "2,openalex:W2,main,10.1/c2,Corpus two\n3,ieee:3,main,10.1/c3,Corpus three\n"
                    "4,x:4,snowball,10.9/other,Some other study\n", encoding="utf-8-sig")
    seen = data / "normalized" / "seen.csv"
    seen.parent.mkdir(parents=True, exist_ok=True)
    seen.write_text("record_id,doi,title,year\n"
                    "openalex:W11,,Load forecasting method,2012\n"     # title + year match
                    "x:1,,Unmatched title,2001\n"                      # the found work has no year: title alone
                    "x:2,,Smart grid overview,2006\n", encoding="utf-8-sig")   # found 2005: no match
    return mark, seen


def _live_run(qpath, data) -> str:
    assert main(["--data-dir", str(data), "snowball", str(qpath)]) == 0
    return _csv(data / "runs.csv")[0]["run_id"]


def test_is_seen_doi_then_title_plus_year(tmp_path):
    p = tmp_path / "seen.csv"
    p.write_text("doi,title,year\n10.1/A,Title one,2010\n,Title two,\n", encoding="utf-8-sig")
    seen = snowball.load_seen([p])
    tk = lambda t: {snowball.rec.title_key(t)}                                   # noqa: E731
    assert snowball.is_seen(seen, {"10.1/a"}, set(), None)                     # DOI lower-cased
    assert snowball.is_seen(seen, set(), tk("Title one"), 2010)
    assert not snowball.is_seen(seen, set(), tk("Title one"), 2011)            # year contradicts
    assert snowball.is_seen(seen, set(), tk("Title one"), None)                # missing year: title alone
    assert snowball.is_seen(seen, set(), tk("Title two"), 1999)                # seen without year
    assert not snowball.is_seen(seen, {"10.1/b"}, tk("Other"), 2010)


def test_snowball_tag_seen_and_corpus_mark_leave_round1_outputs_alone(project):
    qpath, data, calls = project
    run_id = _live_run(qpath, data)
    r1 = [data / "normalized" / f"{QID}.snowball.edges.csv", data / "normalized" / f"{QID}.snowball.records.csv",
          data / "reports" / f"{QID}.snowball.md", data / "runs.csv"]
    before = [p.read_bytes() for p in r1]
    n_calls = {k: len(v) for k, v in calls.items()}
    mark, seen = _round2_files(data)

    assert main(["--data-dir", str(data), "snowball", str(qpath), "--from-run", run_id, "--tag", "r2",
                 "--seen", str(seen), "--corpus-mark", str(mark)]) == 0
    assert [p.read_bytes() for p in r1] == before                              # round-1 files untouched
    assert {k: len(v) for k, v in calls.items()} == n_calls                     # replay: no requests

    edges = _csv(data / "normalized" / f"{QID}.snowball-r2.edges.csv")
    assert len(edges) == 13
    rows = _csv(data / "normalized" / f"{QID}.snowball-r2.records.csv")
    cols = list(rows[0])
    assert cols == snowball.RECORD_COLUMNS[:cols.index("already_screened") + 1] + ["seen_round1"]
    recs = {r["title"]: r for r in rows}
    assert recs["Load forecasting method"]["seen_round1"] == "1"
    assert recs["Unmatched title"]["seen_round1"] == "1"
    assert recs["Smart grid overview"]["seen_round1"] == "0"
    assert recs["Corpus one"]["in_corpus"] == "1"

    report = (data / "reports" / f"{QID}.snowball-r2.md").read_text(encoding="utf-8")
    for line in ["- `in_corpus` (one of the 4): 1", "- `seen_round1` (found in the earlier round",
                 "- **new** (none of the three): 3", "| F0 | all new works | 3 |", "## 5. Overlap",
                 "`in_corpus` marked against"]:
        assert line in report, line
    assert "## 4." not in report and "Seed10" not in report                    # no seed section


def test_snowball_without_new_options_is_unchanged(project):
    qpath, data, _ = project
    run_id = _live_run(qpath, data)
    rec_path = data / "normalized" / f"{QID}.snowball.records.csv"
    before = rec_path.read_bytes()
    rec_path.write_text("stale", encoding="utf-8")
    assert main(["--data-dir", str(data), "snowball", str(qpath), "--from-run", run_id]) == 0
    assert rec_path.read_bytes() == before
    assert "seen_round1" not in before.decode("utf-8-sig")
    assert not list((data / "normalized").glob("*-r2*"))


def test_snowball_rejects_bad_tag(project):
    qpath, data, _ = project
    with pytest.raises(ValueError):
        main(["--data-dir", str(data), "snowball", str(qpath), "--tag", "../x"])


@pytest.fixture
def keep_sb_screen_globals(monkeypatch):
    """use_round rebinds module constants; restore them after the test."""
    for k in [*sb_screen.ROUND2, "DATA", "LLM_DIR"]:
        monkeypatch.setattr(sb_screen, k, getattr(sb_screen, k))


def test_sb_screen_round1_constants_by_default(keep_sb_screen_globals):
    sb_screen.use_round(1)
    assert sb_screen.SNOWBALL_RUN == "20261110T110809Z" and sb_screen.FIRST_N == 1688
    assert sb_screen.EXPECTED_F3 == 1372 and sb_screen.QC_SEED == 20261110 and len(sb_screen.SEEDS) == 3
    assert sb_screen.SHEET.name == f"{QID}.snowball.screening-input.csv"
    assert sb_screen.batch_path(1).name == f"{QID}.sb-batch01.ids.csv"
    assert sb_screen.jsonl_path(2, 1).name == f"{QID}.sb-batch02.screen-A-v1.run1.jsonl"


def test_sb_screen_round2_constants(keep_sb_screen_globals):
    sb_screen.use_round(2)
    assert sb_screen.FIRST_N == 3060 and sb_screen.QC_SEED == 20261116
    assert sb_screen.EXPECTED_F3 is None and sb_screen.SEEDS == {}
    assert sb_screen.SHEET.name == f"{QID}.snowball-r2.screening-input.csv"
    assert sb_screen.TRIAGE.name == f"{QID}.snowball-r2.triage.csv"
    assert sb_screen.REPORT.name == f"{QID}.snowball-r2.screen.md"
    assert sb_screen.batch_path(1).name == f"{QID}.sb2-batch01.ids.csv"
    assert sb_screen.jsonl_path(1, 2).name == f"{QID}.sb2-batch01.screen-A-v1.run2.jsonl"
    assert sb_screen.START_CORPUS.name == f"{QID}.corpus-snowball1-new.csv"
    assert sb_screen.MARK_CORPUS.name == f"{QID}.corpus-after-snowball1.csv"
    assert [p.name for p in sb_screen.SEEN_FILES] == [f"{QID}.snowball.records.csv"]


def _answer(rid, run, decision, code=None):
    return {"record_id": rid, "run": run, "status": "ok", "retried": False, "model_reported": ["m"],
            "claude_code_version": "v", "prompt_sha256": "s", "screened_at": "2026-11-16T00:00:00+00:00",
            "usage": {"total_cost_usd": 0.01, "usage": {"input_tokens": 1, "output_tokens": 2}},
            "parsed": {"decision": decision, "primary_code": code, "rationale": "r", "flags": []}}


def test_sb_screen_round2_prepare_and_triage(project, keep_sb_screen_globals, monkeypatch, capsys):
    qpath, data, _ = project
    run_id = _live_run(qpath, data)
    mark, seen = _round2_files(data)
    assert main(["--data-dir", str(data), "snowball", str(qpath), "--from-run", run_id, "--tag", "r2",
                 "--seen", str(seen), "--corpus-mark", str(mark)]) == 0
    scr = data / "screening"
    monkeypatch.setattr(sb_screen, "CODE", data.parent)
    monkeypatch.setattr(sb_screen, "DATA", data)
    monkeypatch.setattr(sb_screen, "LLM_DIR", scr / "llm")
    monkeypatch.setitem(sb_screen.ROUND2, "SNOWBALL_RUN", run_id)
    monkeypatch.setitem(sb_screen.ROUND2, "BACKFILL_RUN", "test-backfill")
    for k, p in [("SHEET", scr / f"{QID}.snowball-r2.screening-input.csv"),
                 ("TRIAGE", scr / f"{QID}.snowball-r2.triage.csv"),
                 ("REPORT", data / "reports" / f"{QID}.snowball-r2.screen.md"),
                 ("RECORDS", data / "normalized" / f"{QID}.snowball-r2.records.csv"),
                 ("START_CORPUS", scr / f"{QID}.corpus-initial.csv"), ("MARK_CORPUS", mark), ("SEEN_FILES", (seen,))]:
        monkeypatch.setitem(sb_screen.ROUND2, k, p)

    capsys.readouterr()
    assert sb_screen.main(["prepare", "--round", "2",
                           "--skip-backfill-source", "openalex,crossref,semanticscholar"]) == 0
    out = capsys.readouterr().out
    assert "new works passing F3: 1" in out and "expected" not in out and "seed" not in out
    sheet = _csv(scr / f"{QID}.snowball-r2.screening-input.csv")
    assert [(r["n"], r["title"]) for r in sheet] == [("3060", "A survey of smart meter data analytics")]
    ids = _csv(scr / f"{QID}.sb2-batch01.ids.csv")
    assert ids == [{"n": "3060", "record_id": sheet[0]["record_id"]}]
    assert not (scr / f"{QID}.snowball.screening-input.csv").exists()          # no round-1 name written
    assert not (scr / f"{QID}.sb-batch01.ids.csv").exists()

    rid = sheet[0]["record_id"]
    (scr / "llm").mkdir()
    for run in (1, 2):
        (scr / "llm" / f"{QID}.sb2-batch01.screen-A-v1.run{run}.jsonl").write_text(
            json.dumps(_answer(rid, run, "exclude", "A-E2")) + "\n", encoding="utf-8")
    assert sb_screen.main(["triage", "--round", "2"]) == 0
    raw = (scr / f"{QID}.snowball-r2.triage.csv").read_bytes()
    assert raw.startswith(b"\xef\xbb\xbf") and b"\r\n" in raw
    with open(scr / f"{QID}.snowball-r2.triage.csv", encoding="utf-8-sig", newline="") as fh:
        tri = list(csv.DictReader(fh, delimiter=";"))
    assert list(tri[0]) == sb_screen.TRIAGE_COLUMNS
    assert tri[0]["pile"] == "h1_no_abstract" and tri[0]["llm_run1"] == "exclude A-E2"   # no abstract in the stub
    report = (data / "reports" / f"{QID}.snowball-r2.screen.md").read_text(encoding="utf-8")
    assert "(round 2)" in report and "D21, D23" in report and "Snowballing seeds" not in report
