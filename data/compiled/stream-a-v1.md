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

## wos
```
TS=(survey OR review OR "systematic review" OR "literature review" OR "systematic mapping" OR "mapping study" OR taxonomy OR tutorial OR overview OR "state of the art" OR "state-of-the-art") AND TS=("smart meter" OR "smart meters" OR "smart metering" OR "advanced metering infrastructure" OR AMI OR "smart grid" OR "smart grids" OR "load profile" OR "load profiles" OR "electricity consumption data" OR "energy consumption data") AND TS=(privacy OR "consumer privacy" OR "data privacy" OR "information privacy" OR "privacy preserving" OR "privacy-preserving" OR anonymization OR anonymisation OR "de-identification" OR "re-identification") AND PY=(2009-2026)
```
- note: paste into WoS Advanced Search; export as RIS/BibTeX with abstracts

## acm
```
[[[Title: survey] OR [Title: review] OR [Title: systematic review] OR [Title: literature review] OR [Title: systematic mapping] OR [Title: mapping study] OR [Title: taxonomy] OR [Title: tutorial] OR [Title: overview] OR [Title: state of the art] OR [Title: state-of-the-art]] OR [[Abstract: survey] OR [Abstract: review] OR [Abstract: systematic review] OR [Abstract: literature review] OR [Abstract: systematic mapping] OR [Abstract: mapping study] OR [Abstract: taxonomy] OR [Abstract: tutorial] OR [Abstract: overview] OR [Abstract: state of the art] OR [Abstract: state-of-the-art]] OR [[Keyword: survey] OR [Keyword: review] OR [Keyword: systematic review] OR [Keyword: literature review] OR [Keyword: systematic mapping] OR [Keyword: mapping study] OR [Keyword: taxonomy] OR [Keyword: tutorial] OR [Keyword: overview] OR [Keyword: state of the art] OR [Keyword: state-of-the-art]]] AND [[[Title: smart meter] OR [Title: smart meters] OR [Title: smart metering] OR [Title: advanced metering infrastructure] OR [Title: AMI] OR [Title: smart grid] OR [Title: smart grids] OR [Title: load profile] OR [Title: load profiles] OR [Title: electricity consumption data] OR [Title: energy consumption data]] OR [[Abstract: smart meter] OR [Abstract: smart meters] OR [Abstract: smart metering] OR [Abstract: advanced metering infrastructure] OR [Abstract: AMI] OR [Abstract: smart grid] OR [Abstract: smart grids] OR [Abstract: load profile] OR [Abstract: load profiles] OR [Abstract: electricity consumption data] OR [Abstract: energy consumption data]] OR [[Keyword: smart meter] OR [Keyword: smart meters] OR [Keyword: smart metering] OR [Keyword: advanced metering infrastructure] OR [Keyword: AMI] OR [Keyword: smart grid] OR [Keyword: smart grids] OR [Keyword: load profile] OR [Keyword: load profiles] OR [Keyword: electricity consumption data] OR [Keyword: energy consumption data]]] AND [[[Title: privacy] OR [Title: consumer privacy] OR [Title: data privacy] OR [Title: information privacy] OR [Title: privacy preserving] OR [Title: privacy-preserving] OR [Title: anonymization] OR [Title: anonymisation] OR [Title: de-identification] OR [Title: re-identification]] OR [[Abstract: privacy] OR [Abstract: consumer privacy] OR [Abstract: data privacy] OR [Abstract: information privacy] OR [Abstract: privacy preserving] OR [Abstract: privacy-preserving] OR [Abstract: anonymization] OR [Abstract: anonymisation] OR [Abstract: de-identification] OR [Abstract: re-identification]] OR [[Keyword: privacy] OR [Keyword: consumer privacy] OR [Keyword: data privacy] OR [Keyword: information privacy] OR [Keyword: privacy preserving] OR [Keyword: privacy-preserving] OR [Keyword: anonymization] OR [Keyword: anonymisation] OR [Keyword: de-identification] OR [Keyword: re-identification]]]
```
- note: paste into ACM DL Advanced Search 'Search Within' box; set publication date filter 2009–2026

## Sensitivity variants (applied locally to the retrieved set)

- **v2_title_restricted**: Secondary-research terms must appear in the title. Applied locally to the v1 result set (title is a subset of the metadata searched in v1).
- **v3_no_generic_grid**: Drop 'smart grid'/'smart grids' from the domain group to measure how many records are only reachable via the generic grid terms.