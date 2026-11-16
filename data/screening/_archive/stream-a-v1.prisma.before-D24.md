# Stream A: PRISMA numbers, database search (initial corpus) and snowballing rounds 1 and 2

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
- Yield of the round: 10 new studies from 83 start papers (12 % growth). A second round was run from these 10 (D23) and added nothing; see the next section.

## Other methods: snowballing, round 2 (added 16.11.2026)

Sources: DECISION.md D23 (run 20261116T110934Z, start set: the 10 studies added in round 1), `../reports/stream-a-v1.snowball-r2.md`, `stream-a-v1.snowball-r2.ta-final.csv`, `stream-a-v1.snowball-r2.fulltext.csv`, `stream-a-v1.sb2-ft-batch01.compare.md`.

| Box | Count |
|---|---|
| Records identified by citation searching (backward and forward from the 10 studies; OpenAlex, Semantic Scholar) | **2,227** unique works |
| Removed as already known | **726**: in the corpus 27, in the database screening sheet 60, found in round 1 639 |
| New works | **1,501** |
| Records removed before screening by pre-filter F3 (D21) | **1,386** |
| Records screened (title/abstract) | **115** |
| Records excluded | **105**: A-E3 46, A-E1 44, A-E2 9, A-E4 5, A-E7 1 (decided by: both LLM runs exclude, not re-read by H1, 73; H1 32 = check sample 9, recheck of A-E2 exclusions 19, unclear or no abstract 4) |
| Reports sought for retrieval | **10** (all decided by H1: 5 unclear, 4 recheck, 1 check sample) |
| Reports not retrieved | **0** |
| Reports assessed for eligibility | **10** |
| Reports excluded | **10**: A-E3 not in domain 3, A-E6 privacy not substantive 3, A-E1 primary study or mixed paper 2, A-E2 no privacy component 2 |
| Studies included | **0** |

Checks: 2,227 − 726 = 1,501; 1,501 − 1,386 = 115; 115 − 105 = 10 = 0 + 10.

Check sample (D21): 10 of the 92 records excluded by both LLM runs were screened blind by H1; 9 agree, 1 retained (3062, a smart-meter review with an abstract silent on privacy, the gap known from round 1; excluded at full text as A-E6). Every LLM exclusion with code A-E2 in either run was re-read by H1: 17 in the recheck sheet and 2 in the check sample, plus 6 records excluded as A-E2 after their abstracts were added by hand (23 rechecked: 19 excluded, 4 retained for full text). At full text both LLM runs agree with H1 on all 10 decisions.

Round 2 adds no study. The corpus remains at **93 studies** (`stream-a-v1.corpus-after-snowball1.csv`).

## Seeds (14, after D20 and D22)

- Database-reachable seeds (12): all 12 are in the initial corpus (Finster14a 1037, Ashgar17a 18, Gross21a 1469, Mirzaee22a 1368, Mitra24a 56, Wang19a 1557, Kumar19a 857, Bibi25a 26, Liu12a 32, Desai19a 1634, Llaria21a 19, Erkin13a 1051).
- Alahakoon16a (1282) was removed from the seed set on 10.11.2026 (DECISION.md D20): excluded at full text as A-E6 (privacy only in passing; pp. 6, 7, 9; batch 07). The database search had retrieved it, so recall does not improve: metadata-reachable 12/12, database search on evaluated seeds 12/14 (0.86).
- Snowballing seeds (2): Mohassel14a (snowball record 1695) and Komninos14a (1690). Both were found by snowballing and included at full text (snowball batch 01, 14.11.2026).
- Eskandarnia22a (snowball record 1939) was removed from the seed set on 16.11.2026 (DECISION.md D22): found by snowballing, but excluded at full text as A-E1 (own experiment named in the abstract, own section pp. 10–11; snowball batch 02). Database search on evaluated seeds: 12/13 (0.92).
