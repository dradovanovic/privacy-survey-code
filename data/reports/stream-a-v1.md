# Search report: `stream-a-v1`

- raw records: 1848  ({'ieee': 847, 'openalex': 924, 'acm': 77})
- unique after DOI/title dedupe: 1551  (dropped 297)
- satisfy query locally on title/abstract/keywords: 865
- satisfy query when the venue name is included: 882 (+17 via venue, e.g. survey journals)
- unexplained by title/abstract/keywords/venue: 669 (database-side stemming or index terms not exported)

## Concept groups failing locally (incl. venue), across all unique records

- domain: 408
- privacy: 304
- secondary_research: 204

## Content types

- Conferences: 558
- article: 445
- Journals: 251
- book-chapter: 115
- conference-paper: 83
- inproceedings: 36
- Magazines: 33
- review: 20
- proceedings: 7
- Early Access Articles: 3

## Years

- 2009: 1
- 2010: 10
- 2011: 17
- 2012: 33
- 2013: 36
- 2014: 46
- 2015: 58
- 2016: 54
- 2017: 58
- 2018: 70
- 2019: 73
- 2020: 105
- 2021: 121
- 2022: 151
- 2023: 147
- 2024: 185
- 2025: 231
- 2026: 155

## Top venues

- IEEE Access: 71
- ?: 68
- IEEE Internet of Things Journal: 39
- IEEE Communications Surveys & Tutorials: 29
- IEEE Transactions on Smart Grid: 23
- Energies: 23
- Elsevier eBooks: 18
- IEEE Transactions on Industrial Informatics: 16
- Lecture notes in computer science: 15
- Sensors: 11
- Applied Sciences: 9
- Lecture notes in networks and systems: 9
- Communications in computer and information science: 8
- IEEE Communications Magazine: 7
- IEEE Network: 7

## Sensitivity variants (unique records still matching)

- v2_title_restricted: 320
- v3_no_generic_grid: 350

## Seed recall

- overall: 13/13 seeds retrieved (recall = 1.00); 6 pending (source database not searched yet); 19 seeds; searched: acm, ieee, openalex
- ieee: 9/9 seeds retrieved (recall = 1.00)
- scopus: 4/4 seeds retrieved (recall = 1.00); 5 pending
- snowballing: no seeds evaluated yet; 1 pending
- pending:
    - Abdalzaher22a
    - Mohassel14a
    - Avancini19a
    - Scheidt20a
    - Eskandarnia22a
    - Komninos14a

Seeds retrieved by each searched database on its own (before dedupe; all seeds):

- acm: 0/19; not retrieved: Finster14a, Ashgar17a, Gross21a, Mirzaee22a, Mitra24a, Wang19a, Kumar19a, Abdalzaher22a, Bibi25a, Mohassel14a, Liu12a, Avancini19a, Alahakoon16a, Scheidt20a, Eskandarnia22a, Desai19a, Llaria21a, Komninos14a, Erkin13a
- ieee: 9/19; not retrieved: Mitra24a, Abdalzaher22a, Bibi25a, Mohassel14a, Avancini19a, Scheidt20a, Eskandarnia22a, Desai19a, Llaria21a, Komninos14a
- openalex: 12/19; not retrieved: Abdalzaher22a, Mohassel14a, Avancini19a, Alahakoon16a, Scheidt20a, Eskandarnia22a, Komninos14a

- seed notes:
    - Komninos14a: metadata-unreachable: in IEEE, but no privacy term in title/abstract and no index terms returned (stream-a-v1 diagnosis 2026-09-28); expected via snowballing; A-I3 satisfied by section 'Ensuring Confidentiality and Privacy' (to be verified as recovered by snowballing)