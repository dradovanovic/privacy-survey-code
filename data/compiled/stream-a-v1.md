# Compiled search strings for `stream-a-v1` (stream A)

## ieee
```
(survey OR review OR "systematic review" OR "literature review" OR "systematic mapping" OR "mapping study" OR taxonomy OR tutorial OR overview OR "state of the art" OR "state-of-the-art") AND ("smart meter" OR "smart meters" OR "smart metering" OR "advanced metering infrastructure" OR AMI OR "smart grid" OR "smart grids" OR "load profile" OR "load profiles" OR "electricity consumption data" OR "energy consumption data") AND (privacy OR "consumer privacy" OR "data privacy" OR "information privacy" OR "privacy preserving" OR "privacy-preserving" OR anonymization OR anonymisation OR "de-identification" OR "re-identification")
  content_type ∈ ['Journals', 'Conferences', 'Magazines', 'Early Access']
  years 2009–2026
```

API params:
```json
{
  "querytext": "(survey OR review OR \"systematic review\" OR \"literature review\" OR \"systematic mapping\" OR \"mapping study\" OR taxonomy OR tutorial OR overview OR \"state of the art\" OR \"state-of-the-art\") AND (\"smart meter\" OR \"smart meters\" OR \"smart metering\" OR \"advanced metering infrastructure\" OR AMI OR \"smart grid\" OR \"smart grids\" OR \"load profile\" OR \"load profiles\" OR \"electricity consumption data\" OR \"energy consumption data\") AND (privacy OR \"consumer privacy\" OR \"data privacy\" OR \"information privacy\" OR \"privacy preserving\" OR \"privacy-preserving\" OR anonymization OR anonymisation OR \"de-identification\" OR \"re-identification\")",
  "start_year": 2009,
  "end_year": 2026,
  "content_types": [
    "Journals",
    "Conferences",
    "Magazines",
    "Early Access"
  ],
  "max_records": 200
}
```

## scopus
```
TITLE-ABS-KEY(survey OR review OR "systematic review" OR "literature review" OR "systematic mapping" OR "mapping study" OR taxonomy OR tutorial OR overview OR "state of the art" OR "state-of-the-art") AND TITLE-ABS-KEY("smart meter" OR "smart meters" OR "smart metering" OR "advanced metering infrastructure" OR AMI OR "smart grid" OR "smart grids" OR "load profile" OR "load profiles" OR "electricity consumption data" OR "energy consumption data") AND TITLE-ABS-KEY(privacy OR "consumer privacy" OR "data privacy" OR "information privacy" OR "privacy preserving" OR "privacy-preserving" OR anonymization OR anonymisation OR "de-identification" OR "re-identification") AND PUBYEAR > 2008 AND PUBYEAR < 2027 AND (DOCTYPE(ar) OR DOCTYPE(re) OR DOCTYPE(cp) OR DOCTYPE(ch)) AND LANGUAGE(english)
```

## acm
```
(Title:(survey OR review OR "systematic review" OR "literature review" OR "systematic mapping" OR "mapping study" OR taxonomy OR tutorial OR overview OR "state of the art" OR "state-of-the-art") OR Abstract:(survey OR review OR "systematic review" OR "literature review" OR "systematic mapping" OR "mapping study" OR taxonomy OR tutorial OR overview OR "state of the art" OR "state-of-the-art") OR Keyword:(survey OR review OR "systematic review" OR "literature review" OR "systematic mapping" OR "mapping study" OR taxonomy OR tutorial OR overview OR "state of the art" OR "state-of-the-art")) AND (Title:("smart meter" OR "smart meters" OR "smart metering" OR "advanced metering infrastructure" OR AMI OR "smart grid" OR "smart grids" OR "load profile" OR "load profiles" OR "electricity consumption data" OR "energy consumption data") OR Abstract:("smart meter" OR "smart meters" OR "smart metering" OR "advanced metering infrastructure" OR AMI OR "smart grid" OR "smart grids" OR "load profile" OR "load profiles" OR "electricity consumption data" OR "energy consumption data") OR Keyword:("smart meter" OR "smart meters" OR "smart metering" OR "advanced metering infrastructure" OR AMI OR "smart grid" OR "smart grids" OR "load profile" OR "load profiles" OR "electricity consumption data" OR "energy consumption data")) AND (Title:(privacy OR "consumer privacy" OR "data privacy" OR "information privacy" OR "privacy preserving" OR "privacy-preserving" OR anonymization OR anonymisation OR "de-identification" OR "re-identification") OR Abstract:(privacy OR "consumer privacy" OR "data privacy" OR "information privacy" OR "privacy preserving" OR "privacy-preserving" OR anonymization OR anonymisation OR "de-identification" OR "re-identification") OR Keyword:(privacy OR "consumer privacy" OR "data privacy" OR "information privacy" OR "privacy preserving" OR "privacy-preserving" OR anonymization OR anonymisation OR "de-identification" OR "re-identification"))
```
- note: final string used on 2026-10-08 (re-checked 2026-10-09): paste into ACM DL Advanced Search → Edit Query (field syntax, phrases quoted); collection ACM Full-Text Collection; publication date 2009–2026; no content-type filter; 77 hits, all exported as BibTeX (run `data/raw/acm/stream-a-v1/20261008T131500Z`). Edited by hand: `compile_acm` still produces an unquoted bracket string, so re-running `compile` overwrites this section.

## Sensitivity variants (applied locally to the retrieved set)

- **v2_title_restricted**: Secondary-research terms must appear in the title. Applied locally to the v1 result set (title is a subset of the metadata searched in v1).
- **v3_no_generic_grid**: Drop 'smart grid'/'smart grids' from the domain group to measure how many records are only reachable via the generic grid terms.