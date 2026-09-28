# Search report: `stream-a-v1`

- raw records: 847  ({'ieee': 847})
- unique after DOI/title dedupe: 845  (dropped 2)
- satisfy query locally on title/abstract/keywords: 397
- satisfy query when the venue name is included: 414 (+17 via venue, e.g. survey journals)
- unexplained by title/abstract/keywords/venue: 431 (database-side stemming or index terms not exported)

## Concept groups failing locally (incl. venue), across all unique records

- domain: 325
- privacy: 156
- secondary_research: 35

## Content types

- Conferences: 558
- Journals: 251
- Magazines: 33
- Early Access Articles: 3

## Years

- 2010: 2
- 2011: 12
- 2012: 17
- 2013: 17
- 2014: 22
- 2015: 32
- 2016: 28
- 2017: 30
- 2018: 42
- 2019: 46
- 2020: 56
- 2021: 63
- 2022: 87
- 2023: 88
- 2024: 101
- 2025: 138
- 2026: 64

## Top venues

- IEEE Access: 71
- IEEE Internet of Things Journal: 39
- IEEE Communications Surveys & Tutorials: 29
- IEEE Transactions on Smart Grid: 23
- IEEE Transactions on Industrial Informatics: 16
- IEEE Communications Magazine: 7
- IEEE Network: 7
- Proceedings of the IEEE: 6
- 2023 International Conference on Power Energy, Environment & Intelligent Control (PEEIC): 5
- IEEE Open Journal of the Communications Society: 5
- IEEE Transactions on Intelligent Transportation Systems: 5
- CIRED 2020 Berlin Workshop (CIRED 2020): 4
- IEEE Transactions on Consumer Electronics: 4
- IEEE Transactions on Services Computing: 4
- IEEE Transactions on Power Systems: 4

## Sensitivity variants (unique records still matching)

- v2_title_restricted: 143
- v3_no_generic_grid: 163

## Seed recall

- overall: 9/9 seeds retrieved (recall = 1.00); 10 pending (source database not searched yet); 19 seeds; searched: ieee
- ieee: 9/9 seeds retrieved (recall = 1.00)
- scopus: no seeds evaluated yet; 9 pending
- snowballing: no seeds evaluated yet; 1 pending
- pending:
    - Mitra24a
    - Abdalzaher22a
    - Bibi25a
    - Mohassel14a
    - Avancini19a
    - Scheidt20a
    - Eskandarnia22a
    - Desai19a
    - Llaria21a
    - Komninos14a
- seed notes:
    - Komninos14a: metadata-unreachable: in IEEE, but no privacy term in title/abstract and no index terms returned (stream-a-v1 diagnosis 2026-09-28); expected via snowballing; A-I3 satisfied by section 'Ensuring Confidentiality and Privacy' (to be verified as recovered by snowballing)