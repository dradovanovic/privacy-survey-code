# Snowballing (collect and count): `stream-a-v1`

- run_id: 20261116T110934Z; corpus: `data/screening/stream-a-v1.corpus-snowball1-new.csv` (10 papers); `in_corpus` marked against `data/screening/stream-a-v1.corpus-after-snowball1.csv` (93 studies)
- `seen_round1` marked against: `data/normalized/stream-a-v1.snowball.records.csv`
- backward = references of a corpus paper; forward = works citing it. Sources: OpenAlex, Semantic Scholar.
- This report counts only. No record is screened or removed; the data files hold every found work.

## 1. Per source and direction

| source | direction | corpus papers resolved | with >= 1 work | links (edges) | works found (unique in source) | API calls |
|---|---|---|---|---|---|---|
| openalex | backward | 10/10 | 10 | 685 | 663 | 7 |
| openalex | forward | 10/10 | 7 | 1393 | 1363 | 21 |
| semanticscholar | backward | 9/10 | 7 | 630 | 621 | 10 |
| semanticscholar | forward | 9/10 | 7 | 1240 | 1216 | 12 |

- openalex: 29 logged requests (1 to resolve the corpus DOIs); by HTTP status: 200: 29
    - retried 429/5xx responses (not logged as separate requests): 0
- semanticscholar: 22 logged requests; by HTTP status: 200: 20, 404: 2
    - retried 429/5xx responses (not logged as separate requests): 28
    - error: n=1937 references offset 0: HTTP 404
    - error: n=1937 citations offset 0: HTTP 404
- openalex: 10 referenced work ids did not resolve to a work (kept in the edge file with the id only, not counted as works)

Corpus papers not resolved, by `n`:

- openalex backward: none
- openalex forward: none
- semanticscholar backward: 1937
- semanticscholar forward: 1937

Corpus papers resolved but without any work in that source and direction, by `n`:

- openalex backward: none
- openalex forward: 1754, 1785, 1937
- semanticscholar backward: 1690, 1754
- semanticscholar forward: 1754, 1785
- of these, semanticscholar backward list withheld by the publisher (response `data: null`, 'fields have been elided by the publisher'): 1690

## 2. Unique works after consolidation

Deduplicated across sources and directions by DOI, then by normalized title plus year (a missing year matches on the title alone).

- unique works: 2227
- `in_corpus` (one of the 93): 27
- `already_screened` (in the screening sheet, by DOI or title; includes the corpus papers): 84
- already screened and not in the corpus: 60
- `seen_round1` (found in the earlier round, by DOI, then by normalized title plus year): 705
- seen in the earlier round and neither in the corpus nor already screened: 639
- **new** (none of the three): 1501

## 3. Nested filters on the new works (counts only)

Term lists and filters of the query definition, matched with the code of the local sensitivity variants. The `privacy` group is deliberately not used (D10, D17).

| filter | definition | new works |
|---|---|---|
| F0 | all new works | 1501 |
| F1 | F0, year in the query range, English or language unknown, allowed type or type unknown | 1378 |
| F2 | F1 and a `secondary_research` term in title, abstract or keywords | 311 |
| F2t | F1 and a `secondary_research` term in the title | 163 |
| F3 | F2 and a `domain` term in title, abstract or keywords | 115 |
| F3t | F2t and a `domain` term in title, abstract or keywords | 59 |

- new works without a year (fail F1): 20

| filter | works | no abstract | abstract under 30 words (incl. none) | 1 link | 2 links | 3-4 links | 5+ links |
|---|---|---|---|---|---|---|---|
| F1 | 1378 | 321 | 326 | 1358 | 19 | 1 | 0 |
| F3 | 115 | 16 | 16 | 112 | 3 | 0 | 0 |
| F3t | 59 | 15 | 15 | 58 | 1 | 0 | 0 |

Links = number of corpus papers the work is linked to (either direction, either source).
Keywords are available for OpenAlex works only (machine-assigned keywords and concepts); Semantic Scholar gives none, and no language.

## 5. Overlap of OpenAlex and Semantic Scholar

Unique works (after consolidation) found in each direction.

| direction | both | OpenAlex only | Semantic Scholar only |
|---|---|---|---|
| backward | 522 | 130 | 98 |
| forward | 1064 | 295 | 149 |
