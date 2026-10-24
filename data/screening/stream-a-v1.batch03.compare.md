# Batch 3 comparison: H1 vs screen-A-v1 (records 261–360)

Date: 2026-10-17. Frozen prompt screen-A-v1 (SHA-256 `df082ced…0a53`), model `claude-opus-5-5`, two runs. All 200 answers are valid; run 2 needed 1 retry, which succeeded.
Per-record table: `stream-a-v1.batch03.compare.csv`. `ta_final` is pre-filled for the agreements and left empty for the 3 disagreements.

## Numbers

No record in this batch is `A-E7`, so all 100 count. Retain means include or maybe. The LLM vote is exclude only if both runs exclude.

| | LLM retain | LLM exclude |
|---|---|---|
| **H1 retain** | 9 | 0 |
| **H1 exclude** | 3 | 88 |

- Agreement is 97/100 and Cohen's κ is 0.84. H1 retains 9 % of records and the LLM retains 12 %.
- The one "discussed" row (264) agrees, so the figures are the same without it.
- Run 1 and run 2 gave the same decision in 99/100. The exception is row 304.
- The first exclusion code is the same on 80 of the 88 joint excludes.
- As in batch 2, the LLM excluded nothing that H1 kept.

## The 3 disagreements (all H1 exclude, LLM retain)

- **274, electricity-theft detection survey.** H1 coded A-E6; both LLM runs said `maybe ?A-I3`.
  - The record is smart-meter consumer data, and it carries the keywords "data privacy" and "federated learning".
  - The abstract names privacy only in a list of challenges. This is the same A-E6 vs `?A-I3` boundary as in earlier batches.
- **304, mechanism design for market-based demand-side management.** H1 coded A-E6. The two LLM runs split:
  - Run 1 said exclude A-E6, the same as H1.
  - Run 2 said `maybe ?A-I2;?A-I3`.
  - Privacy appears once, in a list of open challenges. This is a weak retain.
- **319, review of energy communities.** H1 coded A-E3; both LLM runs said `maybe ?A-I2;?A-I3`.
  - The abstract names "data management challenges", and "Data privacy" appears only as a keyword.
  - Domain and privacy depth are both open questions. This is the same type as row 183 in batch 2.

## Other points worth a look (not disagreements)

- **First-code differences (8 joint excludes).** These do not change any decision. The order rule (A-E1 → A-E3 → A-E2 → A-E6) decides which code comes first when both apply:
  - In 277, 292 and 301, H1's A-E1 correctly comes first.
  - In 323, 352 and 354, the LLM put A-E3 ahead of H1's A-E6 or A-E2. If you agree that the domain fails, A-E3 should be the first code.
  - 266 and 289 are judgement calls between codes.
- **H1 include vs LLM maybe (282, 287, 313, 321).** Both sides retain, so these are not disagreements. Two of them concern A-I4, which matters at full text:
  - 287 is a "Tutorial V" session record, so it may not be a peer-reviewed paper.
  - 313 has an empty venue field.
  - Both should get an A-I4 check at full text.

## Assessment

- This is the best batch so far: κ 0.84, compared with 0.66 in batch 2 and 0.43 in batch 1. No prompt problem appeared.
- All 3 disagreements are the known borderline types: A-E6 vs `?A-I3`, and domain unclear.

## Reconciliation (2026-10-17)

- The 3 disagreements were resolved as follows:
  - 274 retain: electricity-theft detection is part of smart-meter privacy.
  - 304 exclude: the scope is too broad.
  - 319 retain: data privacy and data management are mentioned.
- 287 and 313 changed from H1 include to exclude under A-E4: on checking, neither is a peer-reviewed article. Row 287 is a conference tutorial record and row 313 has no venue.
- 323, 352 and 354 keep their exclude decision. Their first code is A-E3 under the order rule. The blind file `stream-a-v1.h1.csv` is unchanged; the corrected code is recorded only in `ta_final_reason`.
- Final result: 9 retain, 91 exclude. A backup of the file before these edits is in `_archive/stream-a-v1.batch03.compare.before-codes.csv`.
