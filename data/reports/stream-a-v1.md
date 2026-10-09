# Search report: `stream-a-v1`

- raw records: 2759  ({'ieee': 847, 'openalex': 924, 'scopus': 911, 'acm': 77})
- unique after DOI/title dedupe: 1687  (dropped 1072)
- satisfy query locally on title/abstract/keywords: 871
- satisfy query when the venue name is included: 891 (+20 via venue, e.g. survey journals)
- unexplained by title/abstract/keywords/venue: 796 (database-side stemming or index terms not exported)

## Concept groups failing locally (incl. venue), across all unique records

- domain: 488
- privacy: 391
- secondary_research: 256

## Content types

- Conferences: 558
- article: 443
- Journals: 251
- book-chapter: 115
- conference-paper: 83
- Article: 45
- Review: 36
- Conference Paper: 34
- Magazines: 33
- Book Chapter: 32
- inproceedings: 27
- review: 20
- proceedings: 7
- Early Access Articles: 3

## Years

- 2009: 2
- 2010: 11
- 2011: 17
- 2012: 35
- 2013: 36
- 2014: 47
- 2015: 59
- 2016: 57
- 2017: 64
- 2018: 75
- 2019: 78
- 2020: 116
- 2021: 129
- 2022: 166
- 2023: 162
- 2024: 196
- 2025: 254
- 2026: 183

## Top venues

- IEEE Access: 71
- ?: 68
- IEEE Internet of Things Journal: 39
- IEEE Communications Surveys & Tutorials: 29
- Energies: 27
- IEEE Transactions on Smart Grid: 23
- Elsevier eBooks: 18
- IEEE Transactions on Industrial Informatics: 16
- Lecture notes in computer science: 15
- Sensors: 12
- Renewable and Sustainable Energy Reviews: 12
- Applied Sciences: 9
- Lecture notes in networks and systems: 9
- Communications in computer and information science: 8
- IEEE Communications Magazine: 7

## Abstract backfill (OpenAlex by DOI)

- scopus records: 911
- abstracts filled from OpenAlex by DOI: 634
- abstracts still missing (flag abstract_missing): 277 (22 without DOI, 255 with a DOI that OpenAlex has no abstract for)

## Sensitivity variants (unique records still matching)

- v2_title_restricted: 323
- v3_no_generic_grid: 351

## Seed recall

- overall: 13/13 seeds retrieved (recall = 1.00); 3 pending (source database not searched yet); 16 seeds; searched: acm, ieee, openalex, scopus
- ieee: 9/9 seeds retrieved (recall = 1.00)
- scopus: 4/4 seeds retrieved (recall = 1.00)
- snowballing: no seeds evaluated yet; 3 pending
- pending:
    - Mohassel14a
    - Eskandarnia22a
    - Komninos14a

Seeds retrieved by each searched database on its own (before dedupe; all seeds):

- acm: 0/16; not retrieved: Finster14a, Ashgar17a, Gross21a, Mirzaee22a, Mitra24a, Wang19a, Kumar19a, Bibi25a, Mohassel14a, Liu12a, Alahakoon16a, Eskandarnia22a, Desai19a, Llaria21a, Komninos14a, Erkin13a
- ieee: 9/16; not retrieved: Mitra24a, Bibi25a, Mohassel14a, Eskandarnia22a, Desai19a, Llaria21a, Komninos14a
- openalex: 12/16; not retrieved: Mohassel14a, Alahakoon16a, Eskandarnia22a, Komninos14a
- scopus: 13/16; not retrieved: Mohassel14a, Eskandarnia22a, Komninos14a

- seed notes:
    - Mohassel14a: metadata-unreachable: in Scopus, but no privacy term in title, abstract (OpenAlex) or keywords (diagnose-seeds --db scopus, 2026-10-09); expected via snowballing; A-I3 satisfied by section 3.1 'End users privacy' (checked by hand 2026-10-09)
    - Eskandarnia22a: metadata-unreachable: in Scopus, but no privacy term in title or keywords; abstract not checkable (none in OpenAlex) (diagnose-seeds --db scopus, 2026-10-09); expected via snowballing; A-I3 satisfied by the 'Security and Privacy' section (p. 9) and privacy concerns (p. 12) (checked by hand 2026-10-09)
    - Komninos14a: metadata-unreachable: in IEEE, but no privacy term in title/abstract and no index terms returned (stream-a-v1 diagnosis 2026-09-28); expected via snowballing; A-I3 satisfied by section 'Ensuring Confidentiality and Privacy' (section confirmed by hand 2026-10-09; recovery by snowballing still to be verified)