# Batch 14 comparison: H1 vs screen-A-v1 (records 1361–1460)

Date: 2026-10-20 (LLM runs 2026-10-19). Frozen prompt screen-A-v1 (SHA-256 `df082ced…0a53`), model `claude-opus-5-5`, Claude Code 2.1.303, two runs.

- All 200 answers are valid. Each run needed one retry (empty first answer, `Expecting value: line 1 column 1`), and both retries succeeded. This is the same benign failure as in earlier batches, logged in `first_attempt_error`.
- Per-record table: `stream-a-v1.batch14.compare.csv`. `ta_final` is pre-filled for the agreements and the two A-E7 rows; the 13 disagreements are empty.
- At the H1 check I asked whether any tool helped draft the batch 14 decisions or notes, because the file was saved about five minutes after the batch was prepared. H1 confirmed that no tool helped (see Reconciliation).

## Numbers

Rows 1361 and 1424 are `A-E7` (no abstract) and are left out, so 98 records count. No row is marked "discussed". Retain means include or maybe. The LLM vote is exclude only if both runs exclude.

| | LLM retain | LLM exclude |
|---|---|---|
| **H1 retain** | 12 | 0 |
| **H1 exclude** | 13 | 73 |

- Agreement is 85/98, and Cohen's κ is 0.58. H1 retains 12 % of records; the LLM retains 26 %.
- Run 1 and run 2 gave the same decision in 95/98 and the same retain/exclude in 96/98. The splits are 1390 and 1457 (maybe vs exclude), and 1395 (maybe vs include).
- The first exclusion code is the same on 66 of the 73 joint excludes.
- The LLM excluded nothing that H1 kept.

## The 13 disagreements (all H1 exclude, LLM retain)

- *Privacy in a list* (1383, 1390, 1446, 1450, 1457): H1 coded A-E6; the LLM `?A-I2;?A-I3`.
  - Run 2 on 1390 and run 1 on 1457 agree with H1.
  - 1450 is a federated-learning review, where privacy is the motivation and one discussion aspect.
  - 1457: the abstract never mentions privacy; it appears only as the keyword "Data Privacy". A-E2 fits the text better than A-E6.
- *Domain* (1419, 1422, 1432): H1 coded A-E3.
  - 1419 reviews the development and implementation of smart meters, so the domain looks met even though water and gas metering are included. Privacy is one item in a list, which is A-E6 rather than A-E3.
  - 1422 is a blockchain Internet-of-Energy review, and 1432 an active-distribution-network review; privacy is one item in a list in both.
- *Mechanism* (1410, blockchain smart metering): H1 coded A-E3 `mechanism_only`; both runs said `maybe ?A-I3`, because the abstract names "data security and privacy issues" of centralized metering but does not show their depth.
- *Synthesis or primary study* (1373, 1378, 1388): H1 coded A-E1. All three are book chapters with a DOI.
  - 1373 is a regulatory overview chapter; 1378 builds its own threat model for home energy management; 1388 reviews access-control models and proposes its own scheme.
- *No privacy in the abstract* (1413): H1 coded A-E2; both runs said `?A-I3`. The abstract never mentions privacy, so A-E2 holds on the text.

## Other points (not disagreements)

- **1366 vs 1410:** H1 included 1366 (blockchain-integrated smart grids survey), where privacy is one application area among many. Both runs said `maybe ?A-I2;?A-I3`. 1410, which H1 excluded as `mechanism_only`, names privacy issues more directly. The two decisions point in opposite directions under the blockchain rule.
- **Mechanism-type includes:** 1405 agrees on include, because its abstract surveys "attacks of leaking privacy". 1394 (FL vulnerabilities) and 1408 (fault-tolerant and DP aggregation) got `maybe ?A-I3` under the mechanism rule.
- **H1 include vs LLM maybe** (1366, 1394, 1395, 1408, 1423, 1426, 1427, 1430): both sides retain.
  - 1423, 1426 and 1430 never name smart meters or consumer data (`?A-I2`).
  - 1427 is in a Chinese university journal (Huadong Shifan Daxue xuebao), so the English-language part of A-I4 needs a check.
- **A-E7 rows:** the LLM said maybe on 1361 (V2G security review) and exclude A-E4 on 1424 (special-section introduction). A-E7 rows stay excluded under D19.
- **Book chapters (8):** all have a DOI. None was excluded on DOI grounds.
- **First-code differences on 7 joint excludes** (1363, 1385, 1392, 1429, 1439, 1448, 1451). None changes a decision.

## Assessment

- κ 0.58 is between the batch 7 and 11 level (0.43–0.48) and batches 10 and 13 (0.67).
- All 13 disagreements are the known types: A-E6 vs `?A-I3`, domain, mechanism, and synthesis or primary study.
- Candidates worth a full-text look: 1419 (smart-meter domain met) and 1388 among the disagreements, and 1366 and 1427 among the includes.

## Reconciliation (2026-10-20)

- **The 13 disagreements:**
  - 7 retained (1378, 1383, 1413, 1419, 1432, 1446, 1450) to check privacy depth or, in 1378, whether it synthesizes existing work at full text.
  - 6 excluded (1373, 1388, 1390, 1410, 1422, 1457).
- **I tidied the reasons without changing any decision:**
  - Grammar ("need to be checked"), plus the code added to each exclude reason.
  - 1388: the reason said "synthesis of existing work can be identified", which argues against the exclusion. It now rests on A-E1;route=C, as in H1's screening code: the chapter reviews access-control models, but its main contribution is its own scheme. H1 confirmed this wording.
  - 1390: the reason said privacy "appears as an open issue", but the abstract names it only in a closing clause about preserving market participants' privacy (A-E6).
  - 1410: the reason said privacy is "listed as open issue". The abstract names privacy issues of centralized metering as the motivation for blockchain. The reason now rests on H1's screening code, A-E3 `mechanism_only`.
  - 1422: coded A-E6, since the reason argues privacy depth.
  - 1457: coded A-E2, since the abstract never mentions privacy.
  - 1413 (retained): the reason now notes that the abstract does not mention privacy, so the full-text check is about whether privacy is covered at all.
  - The previous version is in `_archive/stream-a-v1.batch14.compare.before-tidy.csv`.
- **Final result:** 19 retain, 81 exclude.
- H1 confirmed that no tool helped draft the batch 14 decisions or notes.
