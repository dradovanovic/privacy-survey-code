# Stream A: PRISMA numbers, database search (initial corpus) and snowballing round 1

Date: 10.11.2026. Sources: `../reports/stream-a-v1.md` (identification), `stream-a-v1.ta-figures.md` (title/abstract), `stream-a-v1.fulltext.csv` (full text, batches pilot and 01–09). Snowballing ("other methods" column) was added on 16.11.2026 in its own section below.

## Identification

| Box | Count |
|---|---|
| Records identified from databases | **2,759** (IEEE Xplore 847, Scopus 911, OpenAlex 924, ACM DL 77, searched by hand) |
| Duplicate records removed (DOI/title) | **1,072** |
| Records removed for other reasons | 0 |

## Screening

| Box | Count |
|---|---|
| Records screened (title/abstract) | **1,687** (pilot 60, main run 1,627) |
| Records excluded | **1,454**: A-E3 657, A-E1 576, A-E6 98, A-E4 54, A-E2 50, A-E7 (no abstract, D19) 19 |
| Reports sought for retrieval | **233** |
| Reports not retrieved | **34** (`pdf_status = not_retrievable`) |
| Reports assessed for eligibility | **199** (1378 and 1604 screened online by H1 only; no PDF, so no LLM check) |
| Reports excluded | **116**: A-E3 not in domain 58, A-E1 primary study 31, A-E4 not peer-reviewed / not in English 17, A-E6 privacy not substantive 10; no A-E2 or A-E5 |
| Studies included (initial corpus) | **83**, in `stream-a-v1.corpus-initial.csv` |

Checks: 1,687 − 1,454 = 233; 233 − 34 = 199 = 83 + 116.

## Initial corpus

- 83 studies, all with a DOI. Years 2012–2026 (2021: 10, 2022: 9, 2019, 2025 and 2026: 8 each).
- `ft_streams` (H1): B;C 61, C 14, B 3, none 5.
- No duplicate DOIs; the two closest title pairs (26/43, 32/85) are different papers.

## Other methods: snowballing, round 1 (added 16.11.2026)

Sources: DECISION.md D21 (run 20261110T110809Z, pre-filter F3), `stream-a-v1.snowball.ta-final.csv` (title/abstract), `stream-a-v1.snowball.fulltext.csv` (full text, snowball batches 01–03), `stream-a-v1.sb-ft-batch0{1,2,3}.compare.md`.

| Box | Count |
|---|---|
| Records identified by citation searching (backward and forward from the 83 corpus papers; OpenAlex, Semantic Scholar) | **16,838** unique works, **16,369** of them new |
| Records removed before screening by pre-filter F3 (D21) | **14,997** |
| Records screened (title/abstract) | **1,372** |
| Records excluded | **1,308**: A-E3 657, A-E1 346, A-E2 257, A-E4 38, A-E6 6, A-E7 3, A-E5 1 (decided by: both LLM runs exclude, not re-read by H1, 1,060; H1 248 = QC sample 114, LLM disagreements and short abstracts 70, recheck of silent abstracts 64) |
| Reports sought for retrieval | **64** (60 maybe, 4 include; decided by H1 62, both LLM runs include 2) |
| Reports not retrieved | **4** (2061, 2117, 2217, 2845) |
| Reports assessed for eligibility | **60** |
| Reports excluded | **50**: A-E3 not in domain 24, A-E6 privacy not substantive 16, A-E1 primary study or mixed paper 6, A-E2 no privacy component 4 |
| Studies included | **10** (1690, 1695, 1754, 1758, 1785, 1937, 1962, 2093, 2630, 2636) |

Checks: 16,369 − 14,997 = 1,372; 1,372 − 1,308 = 64; 64 − 4 = 60 = 10 + 50.

Full-text agreement of the frozen LLM prompt with H1's blind decisions is reported per batch in the comparison files. 2949 was run separately despite partly garbled text (see batch 03 comparison).

## Corpus after snowballing round 1

- **93 studies** (83 database + 10 snowballing), in `stream-a-v1.corpus-after-snowball1.csv`. All with a DOI; no duplicate DOIs or titles.
- Years 2012–2026 (2021 and 2026: 12 each; 2019, 2022 and 2025: 9 each).
- `ft_streams` (H1): B;C 63, C 21, B 4, none 5.
- Yield of the round: 10 new studies from 83 start papers (12 % growth). Whether a second round is run (from these 10) is not yet decided.

## Seeds (14, after D20 and D22)

- Database-reachable seeds (12): all 12 are in the initial corpus (Finster14a 1037, Ashgar17a 18, Gross21a 1469, Mirzaee22a 1368, Mitra24a 56, Wang19a 1557, Kumar19a 857, Bibi25a 26, Liu12a 32, Desai19a 1634, Llaria21a 19, Erkin13a 1051).
- Alahakoon16a (1282) was removed from the seed set on 10.11.2026 (DECISION.md D20): excluded at full text as A-E6 (privacy only in passing; pp. 6, 7, 9; batch 07). The database search had retrieved it, so recall does not improve: metadata-reachable 12/12, database search on evaluated seeds 12/14 (0.86).
- Snowballing seeds (2): Mohassel14a (snowball record 1695) and Komninos14a (1690). Both were found by snowballing and included at full text (snowball batch 01, 14.11.2026).
- Eskandarnia22a (snowball record 1939) was removed from the seed set on 16.11.2026 (DECISION.md D22): found by snowballing, but excluded at full text as A-E1 (own experiment named in the abstract, own section pp. 10–11; snowball batch 02). Database search on evaluated seeds: 12/13 (0.92).
