import json
from pathlib import Path

import pytest

from survey_pipeline import query_compiler as qc
from survey_pipeline import records as rec
from survey_pipeline.cli import main

QUERY = Path(__file__).parent.parent / "queries" / "stream_a_v1.json"


def test_compile_all_targets():
    q = qc.load_query(QUERY)
    out = qc.compile_all(q)
    assert set(out) == {"ieee", "scopus", "wos", "acm", "openalex"}
    assert '"smart meter"' in out["ieee"].params["querytext"]
    assert "TITLE-ABS-KEY" in out["scopus"].display
    assert out["ieee"].params["max_records"] == 200


def test_wildcard_limit_enforced():
    q = qc.load_query(QUERY)
    q["concept_groups"]["domain"]["terms"] += ["meter*", "grid*", "profil*"]
    with pytest.raises(qc.QueryValidationError):
        qc.validate(q)


def test_title_variant_uses_document_title_qualifier():
    q = qc.load_query(QUERY)
    v = qc.apply_variant(q, "v2_title_restricted")
    ieee = qc.compile_ieee(v)
    assert '"Document Title":survey' in ieee.params["querytext"]


def _rec(title, abstract="", keywords=(), doi=None, rid="ieee:1"):
    return {"record_id": rid, "db": "ieee", "doi": doi, "title": title,
            "abstract": abstract, "keywords": list(keywords)}


def test_record_matches_and_variants():
    q = qc.load_query(QUERY)
    r = _rec("Privacy in smart metering: a survey", "We review consumer privacy threats in AMI.")
    assert rec.record_matches(q, r)
    # 'survey' only in abstract -> fails the title-restricted variant
    r2 = _rec("Privacy in smart metering", "This survey reviews attacks on smart meters.")
    assert rec.record_matches(q, r2)
    assert not rec.record_matches(qc.apply_variant(q, "v2_title_restricted"), r2)
    # grid-only record disappears under v3
    r3 = _rec("A survey on smart grid privacy", "Privacy-preserving aggregation in the smart grid.")
    assert rec.record_matches(q, r3)
    assert not rec.record_matches(qc.apply_variant(q, "v3_no_generic_grid"), r3)


def test_hyphen_and_space_forms_are_equivalent():
    q = qc.load_query(QUERY)
    r = _rec("State of the art review of privacy preserving smart meter data")
    assert rec.record_matches(q, r)


def test_dedupe_by_doi_then_title():
    a = _rec("Same Title", doi="10.1/x", rid="ieee:1")
    b = _rec("Same Title", doi="10.1/X", rid="scopus:1")      # DOI case-insensitive
    c = _rec("Same  title!", doi=None, rid="wos:1")            # title fallback
    d = _rec("Other", doi="10.1/y", rid="ieee:2")
    u, dropped = rec.dedupe([a, {**b, "doi": rec._clean_doi(b["doi"])}, c, d])
    assert [r["record_id"] for r in u] == ["ieee:1", "ieee:2"]
    assert len(dropped) == 2


def test_end_to_end_summarize_on_mock_run(tmp_path):
    q = json.loads(QUERY.read_text())
    run_dir = tmp_path / "raw" / "ieee" / q["query_id"] / "20260101T000000Z"
    run_dir.mkdir(parents=True)
    page = {"total_records": 2, "articles": [
        {"article_number": "1", "doi": "10.1109/A.1", "title": "Smart meter privacy: a survey",
         "abstract": "We survey privacy in smart metering.", "publication_year": "2021",
         "publication_title": "IEEE COMST", "content_type": "Journals", "citing_paper_count": 50,
         "index_terms": {"author_terms": {"terms": ["privacy", "smart meter"]}},
         "authors": {"authors": [{"full_name": "A. Author"}]}, "html_url": "https://x/1"},
        {"article_number": "2", "doi": "10.1109/B.2", "title": "Voltage control in distribution grids",
         "abstract": "A survey of control methods for the smart grid.", "publication_year": "2019",
         "publication_title": "PES GM", "content_type": "Conferences"},
    ]}
    (run_dir / "Journals_p001_s000001.json").write_text(json.dumps(page))
    seeds = tmp_path / "seeds" / "stream_a_seeds.txt"
    seeds.parent.mkdir()
    seeds.write_text("doi:10.1109/A.1\ntitle:Some survey we did not retrieve\n")
    qpath = tmp_path / "queries" / "stream_a_v1.json"
    qpath.parent.mkdir()
    qpath.write_text(json.dumps(q))

    assert main(["--data-dir", str(tmp_path), "normalize", str(qpath), "--db", "ieee",
                 "--run-id", "20260101T000000Z"]) == 0
    assert main(["--data-dir", str(tmp_path), "summarize", str(qpath)]) == 0
    report = (tmp_path / "reports" / "stream-a-v1.md").read_text()
    assert "unique after DOI/title dedupe: 2" in report
    assert "satisfy query locally on title/abstract/keywords: 1" in report   # record 2 lacks privacy terms
    assert "secondary_research: 0" in report or "privacy: 1" in report
    assert "1/2 seeds retrieved" in report
    assert (tmp_path / "screening" / "stream-a-v1.csv").exists()


def test_semicolon_seed_format(tmp_path):
    f = tmp_path / "seeds.txt"
    f.write_text(
        "# title;doi;key\n"
        "Privacy-Aware Smart Metering: A Survey;10.1109/SURV.2014.052914.00090;Finster14a\n"
        "A survey without a DOI;;NoDoi20a\n"
        "Only a title;;\n"
        "doi:10.1109/X.1\n"
    )
    seeds = rec.load_seed_set(f)
    assert [s["id"] for s in seeds] == ["Finster14a", "NoDoi20a", "Only a title", "doi:10.1109/X.1"]
    assert seeds[0]["doi"] == "10.1109/surv.2014.052914.00090"
    hit = _rec("privacy aware smart metering a survey", doi="10.1109/surv.2014.052914.00090")
    report = rec.seed_recall(seeds, [hit])
    assert report["found"] == ["Finster14a"] and report["n_found"] == 1


def _stub_client(tmp_path, responses):
    """IEEEClient whose _get replays `responses` (list of (body, status)) in order."""
    from survey_pipeline.ieee_client import IEEEClient
    c = IEEEClient("test-key", data_dir=tmp_path, sleep_seconds=0)
    queue = list(responses)
    c.calls = []
    def fake_get(params):
        c.calls.append(params)
        return queue.pop(0)
    c._get = fake_get
    return c


def test_lookup_doi_saves_raw_and_flags_counted_not_returned(tmp_path):
    from survey_pipeline.ieee_client import COUNTED_NOT_RETURNED
    c = _stub_client(tmp_path, [
        ({"total_records": 1, "articles": [{"doi": "10.1/a", "title": "A"}]}, 200),
        ({"total_records": 1}, 200),
        ({"total_records": 0}, 200),
    ])
    assert c.lookup_doi("10.1/a")["title"] == "A"
    marker = c.lookup_doi("10.1/b")
    assert marker["_status"] == COUNTED_NOT_RETURNED
    assert Path(marker["_raw"]) == tmp_path / "raw" / "ieee" / "lookup" / "10.1_b.json"
    assert json.loads(Path(marker["_raw"]).read_text(encoding="utf-8")) == {"total_records": 1}
    assert c.lookup_doi("10.1/c") is None
    assert (tmp_path / "raw" / "ieee" / "lookup" / "10.1_c.json").exists()
    assert len((tmp_path / "runs.csv").read_text(encoding="utf-8").strip().splitlines()) == 4


def test_lookup_title_matches_by_doi_or_normalized_title(tmp_path):
    other = {"doi": "10.1/x", "title": "Something Else"}
    hit = {"doi": "10.1/y", "title": "Survey in Smart Grid: Issues"}
    c = _stub_client(tmp_path, [
        ({"total_records": 2, "articles": [other, hit]}, 200),
        ({"total_records": 1, "articles": [{"doi": "10.1/Z", "title": "Different wording"}]}, 200),
        ({"total_records": 1, "articles": [other]}, 200),
    ])
    assert c.lookup_title("Survey in smart grid -- issues") == hit
    assert c.calls[0]["article_title"] == '"Survey in smart grid -- issues"'
    assert c.calls[0]["max_records"] == 5
    assert c.lookup_title("No match here", doi="10.1/z")["doi"] == "10.1/Z"
    assert c.lookup_title("No match here") is None
    assert (tmp_path / "raw" / "ieee" / "lookup" / "title_nomatchhere.json").exists()
    assert len((tmp_path / "runs.csv").read_text(encoding="utf-8").strip().splitlines()) == 4


def test_diagnose_seeds_falls_back_to_title_lookup(tmp_path, monkeypatch):
    from survey_pipeline import ieee_client
    q = json.loads(QUERY.read_text())
    (tmp_path / "normalized").mkdir()
    (tmp_path / "normalized" / f"{q['query_id']}.ieee.jsonl").write_text("")
    seeds = tmp_path / "seeds" / "stream_a_seeds.txt"
    seeds.parent.mkdir()
    seeds.write_text("Smart Home Security: A Survey;10.1109/COMST.1;Home14a\n")
    q["seed_set"] = "seeds/stream_a_seeds.txt"
    qpath = tmp_path / "queries" / "q.json"
    qpath.parent.mkdir()
    qpath.write_text(json.dumps(q))

    article = {"doi": "10.1109/COMST.1", "title": "Smart Home Security: A Survey",
               "abstract": "We survey attacks on smart home networks.", "publication_year": "2014",
               "publication_title": "IEEE Communications Surveys & Tutorials", "content_type": "Journals"}
    responses = [({"total_records": 1}, 200), ({"total_records": 1, "articles": [article]}, 200)]
    calls = []
    def fake_get(self, params):
        calls.append(params)
        return responses.pop(0)
    monkeypatch.setattr(ieee_client.IEEEClient, "_get", fake_get)
    monkeypatch.setattr(ieee_client, "load_api_key", lambda: "test-key")
    monkeypatch.setattr(ieee_client.time, "sleep", lambda s: None)

    assert main(["--data-dir", str(tmp_path), "diagnose-seeds", str(qpath)]) == 0
    assert "doi" in calls[0] and "article_title" in calls[1]
    report = (tmp_path / "reports" / f"{q['query_id']}.seeds.md").read_text(encoding="utf-8")
    assert "falling back to exact-title lookup" in report
    assert "in IEEE: 2014" in report
    assert "not indexed in IEEE" not in report


def test_lookup_command_prints_raw_json(tmp_path, monkeypatch, capsys):
    from survey_pipeline import ieee_client
    body = {"total_records": 1, "articles": [{"doi": "10.1/a", "title": "T"}]}
    monkeypatch.setattr(ieee_client.IEEEClient, "_get", lambda self, params: (body, 200))
    monkeypatch.setattr(ieee_client, "load_api_key", lambda: "test-key")
    monkeypatch.setattr(ieee_client.time, "sleep", lambda s: None)
    assert main(["--data-dir", str(tmp_path), "lookup", "--title", "T"]) == 0
    assert json.loads(capsys.readouterr().out) == body
    assert "manual-lookup" in (tmp_path / "runs.csv").read_text(encoding="utf-8")
    with pytest.raises(SystemExit):
        main(["--data-dir", str(tmp_path), "lookup", "--doi", "x", "--title", "y"])


def test_seed_recall_per_source_db_with_pending(tmp_path):
    f = tmp_path / "seeds.txt"
    f.write_text(
        "Found in IEEE;10.1/a;A1;ieee\n"
        "Missed in IEEE;10.1/b;B1;IEEE\n"
        "Scopus only;10.1/c;C1;scopus\n"
        "Scopus but found via IEEE;10.1/d;D1;scopus\n"
        "Untagged;10.1/e;E1\n"
    )
    seeds = rec.load_seed_set(f)
    assert [s["source_db"] for s in seeds] == ["ieee", "ieee", "scopus", "scopus", None]
    records = [_rec("x", doi="10.1/a", rid="ieee:1"), _rec("y", doi="10.1/d", rid="ieee:2")]
    r = rec.seed_recall(seeds, records)
    assert r["searched_dbs"] == ["ieee"]
    assert r["found"] == ["A1", "D1"] and r["missing"] == ["B1", "E1"] and r["pending"] == ["C1"]
    assert r["n_evaluated"] == 4 and r["recall"] == 0.5
    assert r["per_db"]["ieee"]["recall"] == 0.5
    assert r["per_db"]["scopus"]["found"] == ["D1"] and r["per_db"]["scopus"]["pending"] == ["C1"]
    assert r["per_db"]["scopus"]["recall"] == 1.0
    assert r["per_db"][None]["missing"] == ["E1"]
    # once scopus is searched, C1 counts as missed
    r2 = rec.seed_recall(seeds, records, searched_dbs=["ieee", "scopus"])
    assert r2["pending"] == [] and "C1" in r2["missing"]


def test_summarize_reports_recall_per_source_db(tmp_path):
    q = json.loads(QUERY.read_text())
    (tmp_path / "normalized").mkdir()
    row = {"record_id": "ieee:1", "db": "ieee", "doi": "10.1/a", "title": "Smart meter privacy: a survey",
           "abstract": "", "keywords": [], "year": 2020}
    (tmp_path / "normalized" / f"{q['query_id']}.ieee.jsonl").write_text(json.dumps(row) + "\n")
    seeds = tmp_path / "seeds" / "stream_a_seeds.txt"
    seeds.parent.mkdir()
    seeds.write_text("Smart meter privacy: a survey;10.1/a;A1;ieee\nOther;10.1/b;B1;ieee\nS;10.1/c;C1;scopus\n")
    q["seed_set"] = "seeds/stream_a_seeds.txt"
    qpath = tmp_path / "queries" / "q.json"
    qpath.parent.mkdir()
    qpath.write_text(json.dumps(q))
    assert main(["--data-dir", str(tmp_path), "summarize", str(qpath)]) == 0
    report = (tmp_path / "reports" / f"{q['query_id']}.md").read_text(encoding="utf-8")
    assert "- overall: 1/2 seeds retrieved (recall = 0.50); 1 pending" in report
    assert "- ieee: 1/2 seeds retrieved (recall = 0.50)" in report
    assert "- scopus: no seeds evaluated yet; 1 pending" in report
    assert "- pending:\n    - C1" in report


def test_seed_note_field_may_contain_semicolons(tmp_path):
    f = tmp_path / "seeds.txt"
    f.write_text("T;10.1/a;K1;snowballing;metadata-unreachable; expected via snowballing\nU;10.1/b;K2;ieee\n")
    seeds = rec.load_seed_set(f)
    assert seeds[0]["source_db"] == "snowballing"
    assert seeds[0]["note"] == "metadata-unreachable; expected via snowballing"
    assert seeds[1]["note"] is None
    assert rec.seed_recall(seeds, [], searched_dbs=["ieee"])["pending"] == ["K1"]


SCOPUS_ENTRY = {
    "eid": "2-s2.0-1", "prism:doi": "10.3390/EN15197419", "dc:title": "Data Privacy Preservation in Smart Metering",
    "dc:description": "We survey privacy in smart meters.", "prism:coverDate": "2022-10-10",
    "prism:publicationName": "Energies", "subtypeDescription": "Review", "citedby-count": "12",
    "authkeywords": "privacy | smart meter | ", "author": [{"authname": "Abdalzaher M."}],
    "link": [{"@ref": "self", "@href": "https://api/x"}, {"@ref": "scopus", "@href": "https://scopus/x"}],
}


def test_normalize_scopus_complete_and_standard_views():
    r = rec.normalize_scopus(SCOPUS_ENTRY, "q", "run", "raw.json")
    assert r["record_id"] == "scopus:2-s2.0-1" and r["db"] == "scopus"
    assert r["doi"] == "10.3390/en15197419" and r["year"] == 2022 and r["citing_count"] == 12
    assert r["keywords"] == ["privacy", "smart meter"] and r["authors"] == ["Abdalzaher M."]
    assert r["url"] == "https://scopus/x" and r["content_type"] == "Review"
    std = {k: v for k, v in SCOPUS_ENTRY.items() if k not in ("dc:description", "authkeywords", "author")}
    r2 = rec.normalize_scopus({**std, "dc:creator": "Abdalzaher M."}, "q", "run", "raw.json")
    assert r2["abstract"] == "" and r2["keywords"] == [] and r2["authors"] == ["Abdalzaher M."]


def test_scopus_search_cursor_pagination_raw_cache_and_normalize(tmp_path, monkeypatch):
    from survey_pipeline import scopus_client
    e2 = {**SCOPUS_ENTRY, "eid": "2-s2.0-2", "prism:doi": "10.1/two"}
    pages = [
        ({"search-results": {"opensearch:totalResults": "2", "cursor": {"@next": "C2"}, "entry": [SCOPUS_ENTRY]}}, 200),
        ({"search-results": {"opensearch:totalResults": "2", "cursor": {"@next": "C3"}, "entry": [e2]}}, 200),
    ]
    calls = []
    def fake_get(self, params):
        calls.append(params)
        return pages.pop(0)
    monkeypatch.setattr(scopus_client.ScopusClient, "_get", fake_get)
    monkeypatch.setattr(scopus_client, "load_api_keys", lambda: ("k", None))
    monkeypatch.setattr(scopus_client.time, "sleep", lambda s: None)

    assert main(["--data-dir", str(tmp_path), "search", str(QUERY), "--db", "scopus", "--paging", "cursor"]) == 0
    assert [c["cursor"] for c in calls] == ["*", "C2"]
    assert calls[0]["view"] == "COMPLETE" and calls[0]["count"] == 25
    assert calls[0]["query"].startswith("TITLE-ABS-KEY(")
    run_dirs = list((tmp_path / "raw" / "scopus" / "stream-a-v1").iterdir())
    assert sorted(p.name for p in run_dirs[0].glob("*_p*.json")) == ["all_p001_s000000.json", "all_p002_s000001.json"]
    rows = [json.loads(l) for l in (tmp_path / "normalized" / "stream-a-v1.scopus.jsonl").read_text().splitlines()]
    assert [r["record_id"] for r in rows] == ["scopus:2-s2.0-1", "scopus:2-s2.0-2"]
    log = (tmp_path / "runs.csv").read_text(encoding="utf-8").strip().splitlines()
    assert len(log) == 3 and ",scopus," in log[1]


def test_scopus_empty_result_entry_is_ignored():
    from survey_pipeline.scopus_client import page_items, page_total
    body = {"search-results": {"opensearch:totalResults": "0", "entry": [{"@_fa": "true", "error": "Result set was empty"}]}}
    assert page_items(body) == [] and page_total(body) == 0


def test_scopus_start_offset_paging_is_default_without_inst_token(tmp_path, monkeypatch):
    from survey_pipeline import scopus_client
    e2 = {**SCOPUS_ENTRY, "eid": "2-s2.0-2"}
    pages = [
        ({"search-results": {"opensearch:totalResults": "2", "entry": [SCOPUS_ENTRY]}}, 200),
        ({"search-results": {"opensearch:totalResults": "2", "entry": [e2]}}, 200),
    ]
    calls = []
    def fake_get(self, params):
        calls.append(params)
        return pages.pop(0)
    monkeypatch.setattr(scopus_client.ScopusClient, "_get", fake_get)
    monkeypatch.setattr(scopus_client.time, "sleep", lambda s: None)
    c = scopus_client.ScopusClient("k", None, data_dir=tmp_path, view="STANDARD")
    assert c.paging == "start" and scopus_client.ScopusClient("k", "tok", data_dir=tmp_path).paging == "cursor"
    list(c.search("q", {"query": "TITLE-ABS-KEY(x)"}))
    assert [p["start"] for p in calls] == [0, 1] and all("cursor" not in p for p in calls)
    assert calls[0]["count"] == 25 and calls[0]["view"] == "STANDARD"


def test_openalex_compiler_filters_and_url_limit():
    q = qc.load_query(QUERY)
    cq = qc.compile_openalex(q)
    f = cq.params["filter"]
    assert f.startswith('title_and_abstract.search:((survey OR review')
    assert ',publication_year:2009-2026,language:en,type:article|review|conference-paper|book-chapter' in f
    assert f.count(",") == 3                      # exactly four filters, no comma inside the search string
    assert any("URL length" in n for n in cq.notes)
    q["concept_groups"]["domain"]["terms"] += [f"long domain phrase number {i}" for i in range(120)]
    with pytest.raises(qc.QueryValidationError, match="bytes"):
        qc.compile_openalex(q)
    q2 = qc.load_query(QUERY)
    q2["concept_groups"]["domain"]["terms"].append("meters, smart")
    with pytest.raises(qc.QueryValidationError, match="comma"):
        qc.compile_openalex(q2)
