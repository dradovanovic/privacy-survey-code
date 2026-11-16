# Stream A: PRISMA numbers, database search (initial corpus)

Date: 10.11.2026. Sources: `../reports/stream-a-v1.md` (identification), `stream-a-v1.ta-figures.md` (title/abstract), `stream-a-v1.fulltext.csv` (full text, batches pilot and 01–09). Snowballing ("other methods" column) is not run yet; this file covers the database column only.

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

## Seeds (15, after D20)

- Database-reachable seeds (12): all 12 are in the initial corpus (Finster14a 1037, Ashgar17a 18, Gross21a 1469, Mirzaee22a 1368, Mitra24a 56, Wang19a 1557, Kumar19a 857, Bibi25a 26, Liu12a 32, Desai19a 1634, Llaria21a 19, Erkin13a 1051).
- Alahakoon16a (1282) was removed from the seed set on 10.11.2026 (DECISION.md D20): excluded at full text as A-E6 (privacy only in passing; pp. 6, 7, 9; batch 07). The database search had retrieved it, so recall does not improve: metadata-reachable 12/12, database search on evaluated seeds 12/14 (0.86).
- Snowballing seeds (3): Mohassel14a, Eskandarnia22a, Komninos14a; recovery is checked after snowballing (`code/prompts/run-snowball-A-collect.md`).
