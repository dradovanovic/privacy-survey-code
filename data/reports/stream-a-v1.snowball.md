# Snowballing (collect and count): `stream-a-v1`

- run_id: 20261110T110809Z; corpus: `data/screening/stream-a-v1.corpus-initial.csv` (83 papers)
- backward = references of a corpus paper; forward = works citing it. Sources: OpenAlex, Semantic Scholar.
- This report counts only. No record is screened or removed; the data files hold every found work.

## 1. Per source and direction

| source | direction | corpus papers resolved | with >= 1 work | links (edges) | works found (unique in source) | API calls |
|---|---|---|---|---|---|---|
| openalex | backward | 83/83 | 82 | 8309 | 6411 | 65 |
| openalex | forward | 83/83 | 75 | 11062 | 9734 | 171 |
| semanticscholar | backward | 81/83 | 29 | 4501 | 4019 | 84 |
| semanticscholar | forward | 81/83 | 76 | 7053 | 6242 | 90 |

- openalex: 238 logged requests (2 to resolve the corpus DOIs); by HTTP status: 200: 238
    - retried 429/5xx responses (not logged as separate requests): 0
- semanticscholar: 174 logged requests; by HTTP status: 200: 168, 404: 4, 429: 2
    - retry pass retry-20261110T114403Z for (n, direction) [[1469, 'backward'], [1663, 'forward']]: 0 still failing; 2 retried 429/5xx responses
    - retried 429/5xx responses (not logged as separate requests): 246
    - error: n=241 references offset 0: HTTP 404
    - error: n=241 citations offset 0: HTTP 404
    - error: n=321 references offset 0: HTTP 404
    - error: n=321 citations offset 0: HTTP 404
    - error: n=1469 references offset 0: HTTP 429
    - error: n=1663 citations offset 0: HTTP 429
- openalex: 128 referenced work ids did not resolve to a work (kept in the edge file with the id only, not counted as works)

Corpus papers not resolved, by `n`:

- openalex backward: none
- openalex forward: none
- semanticscholar backward: 241, 321
- semanticscholar forward: 241, 321

Corpus papers resolved but without any work in that source and direction, by `n`:

- openalex backward: 1430
- openalex forward: 79, 184, 241, 721, 860, 918, 1174, 1430
- semanticscholar backward: 18, 32, 43, 56, 79, 85, 106, 274, 338, 344, 400, 515, 532, 566, 642, 646, 698, 701, 721, 742, 817, 857, 860, 901, 918, 922, 945, 980, 984, 998, 1037, 1051, 1059, 1123, 1134, 1137, 1147, 1198, 1354, 1364, 1368, 1379, 1405, 1430, 1469, 1472, 1519, 1544, 1583, 1623, 1634, 1663
- semanticscholar forward: 79, 817, 918, 1174, 1430
- of these, semanticscholar backward list withheld by the publisher (response `data: null`, 'fields have been elided by the publisher'): 18, 32, 43, 56, 79, 85, 106, 274, 338, 344, 400, 515, 532, 566, 642, 646, 698, 721, 742, 817, 857, 860, 901, 918, 980, 984, 998, 1037, 1051, 1059, 1123, 1134, 1137, 1147, 1198, 1354, 1364, 1379, 1405, 1430, 1469, 1472, 1519, 1544, 1583, 1623, 1634, 1663

## 2. Unique works after consolidation

Deduplicated across sources and directions by DOI, then by normalized title plus year (a missing year matches on the title alone).

- unique works: 16838
- `in_corpus` (one of the 83): 71
- `already_screened` (in the screening sheet, by DOI or title; includes the corpus papers): 469
- already screened and not in the corpus: 398
- **new** (neither): 16369

## 3. Nested filters on the new works (counts only)

Term lists and filters of the query definition, matched with the code of the local sensitivity variants. The `privacy` group is deliberately not used (D10, D17).

| filter | definition | new works |
|---|---|---|
| F0 | all new works | 16369 |
| F1 | F0, year in the query range, English or language unknown, allowed type or type unknown | 14673 |
| F2 | F1 and a `secondary_research` term in title, abstract or keywords | 3101 |
| F2t | F1 and a `secondary_research` term in the title | 1672 |
| F3 | F2 and a `domain` term in title, abstract or keywords | 1372 |
| F3t | F2t and a `domain` term in title, abstract or keywords | 704 |

- new works without a year (fail F1): 197

| filter | works | no abstract | abstract under 30 words (incl. none) | 1 link | 2 links | 3-4 links | 5+ links |
|---|---|---|---|---|---|---|---|
| F1 | 14673 | 3201 | 3238 | 12744 | 1339 | 453 | 137 |
| F3 | 1372 | 148 | 150 | 964 | 255 | 114 | 39 |
| F3t | 704 | 128 | 129 | 460 | 141 | 78 | 25 |

Links = number of corpus papers the work is linked to (either direction, either source).
Keywords are available for OpenAlex works only (machine-assigned keywords and concepts); Semantic Scholar gives none, and no language.

## 4. Seeds expected via snowballing

| seed | DOI | found | backward | forward | corpus links | abstract | passes | fails |
|---|---|---|---|---|---|---|---|---|
| Mohassel14a | 10.1016/j.ijepes.2014.06.025 | yes | openalex, semanticscholar | - | 8 (n = 566, 642, 808, 857, 1229, 1368, 1557, 1620) | yes | F1, F2, F2t, F3, F3t | - |
| Eskandarnia22a | 10.1007/s42979-022-01161-6 | yes | - | openalex, semanticscholar | 2 (n = 18, 1557) | no | F1, F2, F2t, F3, F3t | - |
| Komninos14a | 10.1109/comst.2014.2320093 | yes | openalex, semanticscholar | openalex, semanticscholar | 11 (n = 18, 19, 32, 642, 646, 857, 1161, 1229, 1354, 1368, 1405) | yes | F1, F2, F2t, F3, F3t | - |

## 5. Overlap of OpenAlex and Semantic Scholar

Unique works (after consolidation) found in each direction.

| direction | both | OpenAlex only | Semantic Scholar only |
|---|---|---|---|
| backward | 3383 | 2880 | 626 |
| forward | 5324 | 4365 | 897 |
