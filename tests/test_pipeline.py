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
    assert set(out) == {"ieee", "scopus", "wos", "acm"}
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
