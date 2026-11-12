import csv
import json
from pathlib import Path

import pytest

from survey_pipeline import records as rec
from survey_pipeline import snowball
from survey_pipeline.cli import main

QUERY = Path(__file__).parent.parent / "queries" / "stream_a_v1.json"
QID = "stream-a-v1"


def _oa(wid, title, year=2015, doi=None, typ="article", lang="en", refs=None, abstract=None):
    w = {"id": f"https://openalex.org/{wid}", "doi": f"https://doi.org/{doi}" if doi else None,
         "display_name": title, "publication_year": year, "type": typ, "language": lang,
         "primary_location": {"source": {"display_name": "Venue"}},
         "abstract_inverted_index": {t: [i] for i, t in enumerate(abstract.split())} if abstract else None}
    if refs is not None:
        w["referenced_works"] = [f"https://openalex.org/{r}" for r in refs]
    return w


def _s2(pid, title, year=None, doi=None, types=None):
    return {"paperId": pid, "externalIds": {"DOI": doi} if doi else {}, "title": title, "year": year,
            "venue": "", "publicationTypes": types, "abstract": None}


W10 = _oa("W10", "A survey of smart meter data analytics", 2015, "10.9/W10", "review")
W11 = _oa("W11", "Load forecasting method", 2012)
W20 = _oa("W20", "Already screened paper", 2020, "10.9/w20")
W21 = _oa("W21", "Smart Meter: eine Übersicht", 2020, lang="de")
W1 = _oa("W1", "Corpus one", 2018, "10.1/c1", refs=["W10", "W11", "W99"])
W2 = _oa("W2", "Corpus two", 2017, "10.1/c2", refs=["W10"])


@pytest.fixture
def project(tmp_path, monkeypatch):
    """A data dir with a 3-paper corpus (n=3 unknown to both sources) and stubbed APIs; returns (qpath, calls)."""
    from survey_pipeline import openalex_client, semanticscholar_client
    (tmp_path / "queries").mkdir()
    qpath = tmp_path / "queries" / "stream_a_v1.json"
    qpath.write_text(QUERY.read_text(encoding="utf-8"), encoding="utf-8")
    (tmp_path / "seeds").mkdir()
    (tmp_path / "seeds" / "stream_a_seeds.txt").write_text(
        "A survey of smart meter data analytics;10.9/w10;Seed10;snowballing;note\n"
        "Never found;10.9/none;SeedX;snowballing\nA database seed;10.9/db;SeedDb;ieee\n", encoding="utf-8")
    data = tmp_path / "data"
    (data / "screening").mkdir(parents=True)
    (data / "screening" / f"{QID}.corpus-initial.csv").write_text(
        "n,record_id,source,doi,title\n1,openalex:W1,main,10.1/C1,Corpus one\n"
        "2,openalex:W2,main,10.1/c2,Corpus two\n3,ieee:3,main,10.1/c3,Corpus three\n", encoding="utf-8-sig")
    (data / "screening" / f"{QID}.csv").write_text(
        "record_id,db,doi,title,decision\nieee:9,ieee,10.9/w20,Already screened paper,exclude\n", encoding="utf-8-sig")
    calls = {"openalex": [], "semanticscholar": []}

    def oa_get(self, params):
        calls["openalex"].append(params)
        flt = params["filter"]
        if flt.startswith("doi:"):
            assert flt in ("doi:10.1/c1|10.1/c2|10.1/c3", "doi:10.1/c1|10.1/c2")
            return {"meta": {"count": 2}, "results": [W1, W2]}, 200
        if flt == "cites:W1":
            assert params["select"] == snowball.OPENALEX_SELECT
            if params["cursor"] == "*":
                return {"meta": {"count": 2, "next_cursor": "c2"}, "results": [W20]}, 200
            assert params["cursor"] == "c2"
            return {"meta": {"count": 2, "next_cursor": None}, "results": [W21]}, 200
        if flt == "cites:W2":
            return {"meta": {"count": 2, "next_cursor": None}, "results": [W20, W1]}, 200
        assert flt == "openalex:W10|W11|W99"                       # W99 does not resolve
        return {"meta": {"count": 2}, "results": [W10, W11]}, 200

    def s2_get(self, path, params):
        calls["semanticscholar"].append((path, params["offset"], self.api_key))
        if self.api_key:
            return {"message": "Forbidden"}, 403
        if path == "paper/DOI:10.1/c1/references":
            return {"offset": 0, "data": [
                {"citedPaper": _s2("p10", "A Survey of Smart Meter Data Analytics", 2015, "10.9/W10", ["Review"])},
                {"citedPaper": _s2(None, "Unmatched title")},
                {"citedPaper": _s2("p12", "Load forecasting method", 2012)},
                {"citedPaper": _s2(None, None)}]}, 200
        if path == "paper/DOI:10.1/c1/citations":
            if params["offset"] == 0:
                return {"offset": 0, "next": 1, "data": [{"citingPaper": _s2("p20", "Other title", 2020, "10.9/w20")}]}, 200
            return {"offset": 1, "data": [{"citingPaper": _s2("p30", "Smart grid overview", 2005, None, ["Book"])}]}, 200
        if path == "paper/DOI:10.1/c2/references":                # reference list elided by the publisher
            return {"data": None, "citingPaperInfo": {"title": "Corpus two"}}, 200
        if "10.1/c2" in path:
            return {"offset": 0, "data": []}, 200
        return {"error": "Paper with id DOI:10.1/c3 not found"}, 404

    monkeypatch.setattr(openalex_client.OpenAlexClient, "_get", oa_get)
    monkeypatch.setattr(openalex_client, "load_api_key", lambda: "oa-key")
    monkeypatch.setattr(semanticscholar_client.SemanticScholarClient, "_get", s2_get)
    monkeypatch.setattr(semanticscholar_client, "load_api_key", lambda: "s2-key")
    monkeypatch.setattr("survey_pipeline.snowball.time.sleep", lambda s: None)
    return qpath, data, calls


def _csv(path):
    with open(path, encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def test_snowball_collects_logs_consolidates_and_reports(project):
    qpath, data, calls = project
    assert main(["--data-dir", str(data), "snowball", str(qpath)]) == 0

    log = _csv(data / "runs.csv")
    run_id = log[0]["run_id"]
    assert {r["run_id"] for r in log} == {run_id} and {r["query_id"] for r in log} == {QID}
    per = {}
    for r in log:
        per.setdefault((r["db"], r["content_type"]), []).append(r["status"])
    assert per[("openalex", "snowball_corpus")] == ["200"]
    assert per[("openalex", "snowball_forward")] == ["200"] * 3            # W1: two pages, W2: one
    assert per[("openalex", "snowball_backward")] == ["200"]
    assert sorted(per[("semanticscholar", "snowball_backward")]) == ["200", "200", "403", "404"]
    assert sorted(per[("semanticscholar", "snowball_forward")]) == ["200", "200", "200", "404"]
    # the rejected key is dropped after the first 403 and never sent again
    assert [k for _, _, k in calls["semanticscholar"]] == ["s2-key"] + [None] * 7
    assert "s2-key" not in (data / "runs.csv").read_text(encoding="utf-8")

    oa_raw = data / "raw" / "openalex" / "snowball" / run_id
    s2_raw = data / "raw" / "semanticscholar" / "snowball" / run_id
    assert {p.name for p in oa_raw.iterdir()} == {
        "params.json", "fetch_summary.json", "corpus_s000000.json", "refs_s000000.json",
        "cites_n0001_W1_p001.json", "cites_n0001_W1_p002.json", "cites_n0002_W2_p001.json"}
    assert (s2_raw / "citations_n0001_o000001.json").exists() and (s2_raw / "references_n0003_o000000.json").exists()
    assert json.loads((s2_raw / "fetch_summary.json").read_text())["key_rejected_403_fell_back_to_no_key"] is True

    edges = _csv(data / "normalized" / f"{QID}.snowball.edges.csv")
    assert list(edges[0]) == snowball.EDGE_COLUMNS and len(edges) == 13
    count = lambda d, s: sum(1 for e in edges if e["direction"] == d and e["source"] == s)   # noqa: E731
    assert (count("backward", "openalex"), count("forward", "openalex")) == (4, 4)
    assert (count("backward", "semanticscholar"), count("forward", "semanticscholar")) == (3, 2)
    assert {e["corpus_doi"] for e in edges} == {"10.1/c1", "10.1/c2"}      # corpus DOI lower-cased
    w99 = [e for e in edges if e["found_id"] == "openalex:W99"]
    assert len(w99) == 1 and w99[0]["found_title"] == ""                    # unresolved id kept, no metadata
    assert [e["found_id"] for e in edges if e["found_title"] == "Unmatched title"] == [""]

    recs = {r["title"]: r for r in _csv(data / "normalized" / f"{QID}.snowball.records.csv")}
    assert list(next(iter(recs.values()))) == snowball.RECORD_COLUMNS and len(recs) == 7
    w10 = recs["A survey of smart meter data analytics"]
    assert w10["found_ids"] == "openalex:W10; semanticscholar:p10"          # merged by DOI
    assert (w10["n_corpus_links"], w10["corpus_ns"], w10["directions"]) == ("2", "1; 2", "backward")
    assert w10["sources"] == "openalex; semanticscholar" and w10["language"] == "en"
    assert recs["Load forecasting method"]["found_ids"] == "openalex:W11; semanticscholar:p12"   # title + year
    assert recs["Already screened paper"]["already_screened"] == "1"        # S2 title differs: merged by DOI
    assert recs["Already screened paper"]["in_corpus"] == "0"
    assert recs["Corpus one"]["in_corpus"] == "1" and recs["Corpus one"]["directions"] == "forward"
    assert recs["Unmatched title"]["record_id"] == "" and recs["Smart grid overview"]["sources"] == "semanticscholar"

    report = (data / "reports" / f"{QID}.snowball.md").read_text(encoding="utf-8")
    for line in [
        "| openalex | backward | 2/3 | 2 | 4 | 3 | 1 |",
        "| openalex | forward | 2/3 | 2 | 4 | 3 | 3 |",
        "| semanticscholar | backward | 2/3 | 1 | 3 | 3 | 4 |",
        "| semanticscholar | forward | 2/3 | 1 | 2 | 2 | 4 |",
        "- openalex backward: 3", "- semanticscholar forward: 3",
        "- openalex backward: none", "- semanticscholar backward: 2", "- semanticscholar forward: 2",
        "semanticscholar backward list withheld by the publisher (response `data: null`, "
        "'fields have been elided by the publisher'): 2",
        "- openalex: 1 referenced work ids did not resolve",
        "the configured API key was rejected (403)",
        "- unique works: 7", "- `in_corpus` (one of the 3): 1", "- **new** (neither): 5",
        "| F0 | all new works | 5 |",
        "- new works without a year (fail F1): 1",
        "| F1 | 2 | 2 | 2 | 1 | 1 | 0 | 0 |",          # W10 (2 links) and W11 (1 link), neither has an abstract
        "| F3t | 1 | 1 | 1 | 0 | 1 | 0 | 0 |",
        "| Seed10 | 10.9/w10 | yes | openalex, semanticscholar | - | 2 (n = 1, 2) | no | F1, F2, F2t, F3, F3t | - |",
        "| SeedX | 10.9/none | **no** | - | - | 0 | no | - | - |",
        "| backward | 2 | 0 | 1 |", "| forward | 1 | 2 | 1 |",
    ]:
        assert line in report, line
    assert "SeedDb" not in report                                           # only seeds expected via snowballing
    assert not (data / "screening" / f"{QID}.snowball.csv").exists()        # no screening sheet is built


def test_snowball_replay_makes_no_requests_and_reproduces_outputs(project):
    qpath, data, calls = project
    assert main(["--data-dir", str(data), "snowball", str(qpath)]) == 0
    run_id = _csv(data / "runs.csv")[0]["run_id"]
    outputs = [data / "normalized" / f"{QID}.snowball.edges.csv", data / "normalized" / f"{QID}.snowball.records.csv",
               data / "reports" / f"{QID}.snowball.md", data / "runs.csv"]
    before = [p.read_bytes() for p in outputs]
    n_calls = {k: len(v) for k, v in calls.items()}
    for p in outputs[:3]:
        p.write_text("stale", encoding="utf-8")

    assert main(["--data-dir", str(data), "snowball", str(qpath), "--from-run", run_id]) == 0
    assert {k: len(v) for k, v in calls.items()} == n_calls                 # replay sends nothing
    assert [p.read_bytes() for p in outputs] == before
    assert main(["--data-dir", str(data), "snowball", str(qpath), "--from-run", "19990101T000000Z"]) == 2


def test_snowball_dry_run_limits_corpus_and_writes_no_outputs(project, capsys):
    qpath, data, calls = project
    assert main(["--data-dir", str(data), "snowball", str(qpath), "--dry-run", "--limit", "2"]) == 0
    out = capsys.readouterr().out
    assert "2 of 3 corpus papers" in out and "API calls" in out and "no edge, record or report file written" in out
    assert calls["openalex"][0]["filter"] == "doi:10.1/c1|10.1/c2"          # n=3 is not requested
    assert not any("c3" in path for path, _, _ in calls["semanticscholar"])
    assert not (data / "normalized").exists() and not (data / "reports").exists()
    assert len(_csv(data / "runs.csv")) == 5 + 6                            # requests are still logged


def test_consolidate_doi_then_title_plus_year():
    def r(db, rid, title, year, doi=None):
        return {"db": db, "record_id": rid, "title": title, "year": year, "doi": doi}
    found = {
        "openalex:W1": r("openalex", "openalex:W1", "Smart Grid Privacy: A Review", 2019, "10.1/a"),
        "semanticscholar:a": r("semanticscholar", "semanticscholar:a", "Preprint title", 2019, "10.1/a"),      # DOI
        "semanticscholar:b": r("semanticscholar", "semanticscholar:b", "Smart grid privacy - a review", 2019),  # title+year
        "semanticscholar:c": r("semanticscholar", "semanticscholar:c", "Smart grid privacy: a review", 2021),   # other year
        "semanticscholar:d": r("semanticscholar", "semanticscholar:d", "Smart grid privacy: a review", None),   # no year
        "openalex:W2": r("openalex", "openalex:W2", "", None),                                                   # no title
        "openalex:W3": r("openalex", "openalex:W3", "", None),
    }
    groups, where = snowball.consolidate(found)
    assert where["openalex:W1"] == where["semanticscholar:a"] == where["semanticscholar:b"] == where["semanticscholar:d"]
    assert where["semanticscholar:c"] != where["openalex:W1"]
    assert where["openalex:W2"] != where["openalex:W3"]                     # empty titles never merge
    assert len(groups) == 4 and groups[where["openalex:W1"]][0] == "openalex:W1"   # OpenAlex record leads


def test_filter_flags_nested_and_lenient_on_unknowns():
    from survey_pipeline import query_compiler as qc
    q = qc.load_query(QUERY)
    assert snowball.allowed_types(q) == {"article", "review", "conference-paper", "book-chapter"}

    def flags(title, year=2020, types=(), languages=(), abstract="", keywords=()):
        return snowball.filter_flags(q, {"title": title, "year": year, "types": list(types), "languages": list(languages),
                                         "abstract": abstract, "keywords": list(keywords)})
    f = flags("A survey on Advanced Metering Infrastructure")                 # no privacy term needed
    assert all(f.values())
    f = flags("Deep learning for load data", abstract="We review smart meter analytics.")
    assert (f["F2"], f["F2t"], f["F3"], f["F3t"]) == (True, False, True, False)
    f = flags("Deep learning: a review", keywords=["Smart grid"])
    assert (f["F2t"], f["F3t"]) == (True, True)                              # domain term in keywords counts
    assert flags("A survey of smart meters", types=["article", "preprint"])["F1"]      # any allowed type
    assert not flags("A survey of smart meters", types=["dissertation"])["F3t"]
    assert not flags("A survey of smart meters", languages=["de"])["F1"]
    assert not flags("A survey of smart meters", year=2008)["F1"]
    assert not flags("A survey of smart meters", year=None)["F1"]
    assert flags("A survey of smart meters", year=None)["F0"]
    assert rec.title_key("x") == "x"


def test_snowball_retry_failed_refetches_only_rate_limited_lists(project, monkeypatch):
    from survey_pipeline import semanticscholar_client
    qpath, data, calls = project
    stub = semanticscholar_client.SemanticScholarClient._get
    limited = {"on": True}

    def s2_get(self, path, params):                     # c1/citations is rate-limited during the first pass
        if limited["on"] and not self.api_key and path == "paper/DOI:10.1/c1/citations":
            calls["semanticscholar"].append((path, params["offset"], self.api_key))
            return {"message": "Too Many Requests"}, 429
        return stub(self, path, params)
    monkeypatch.setattr(semanticscholar_client.SemanticScholarClient, "_get", s2_get)
    monkeypatch.setattr(semanticscholar_client, "load_api_key", lambda: None)
    assert main(["--data-dir", str(data), "snowball", str(qpath)]) == 0
    run_id = _csv(data / "runs.csv")[0]["run_id"]
    report = (data / "reports" / f"{QID}.snowball.md").read_text(encoding="utf-8")
    assert "- semanticscholar forward: 1, 3" in report
    assert "| semanticscholar | forward | 1/3 | 0 | 0 | 0 | 3 |" in report

    limited["on"] = False
    n_oa, n_s2 = len(calls["openalex"]), len(calls["semanticscholar"])
    assert main(["--data-dir", str(data), "snowball", str(qpath), "--from-run", run_id, "--retry-failed"]) == 0
    assert len(calls["openalex"]) == n_oa                                   # nothing else is requested again
    assert [c[0] for c in calls["semanticscholar"][n_s2:]] == ["paper/DOI:10.1/c1/citations"] * 2   # 404s: no retry
    s2_raw = data / "raw" / "semanticscholar" / "snowball" / run_id
    assert "Too Many Requests" in (s2_raw / "citations_n0001_o000000.json").read_text()   # failed response kept
    assert len(list(s2_raw.glob("citations_n0001_o00000?.retry-*.json"))) == 2
    report = (data / "reports" / f"{QID}.snowball.md").read_text(encoding="utf-8")
    assert "| semanticscholar | forward | 2/3 | 1 | 2 | 2 | 5 |" in report and "- unique works: 7" in report
    assert "retry pass retry-" in report and "0 still failing" in report
    assert main(["--data-dir", str(data), "snowball", str(qpath), "--from-run", run_id, "--retry-failed"]) == 0
    assert len(calls["semanticscholar"]) == n_s2 + 2                        # nothing left to retry
