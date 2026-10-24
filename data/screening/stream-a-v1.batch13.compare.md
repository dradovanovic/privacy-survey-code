# Batch 13 comparison: H1 vs screen-A-v1 (records 1261–1360)

Date: 2026-10-19. Frozen prompt screen-A-v1 (SHA-256 `df082ced…0a53`), model `claude-opus-5-5`, Claude Code 2.1.303, two runs.

- All 200 answers are valid, with no retries.
- Per-record table: `stream-a-v1.batch13.compare.csv`. `ta_final` is pre-filled for the agreements and the A-E7 row; the 8 disagreements are empty.

## Numbers

Row 1268 is `A-E7` (no abstract) and is left out, so 99 records count. No row is marked "discussed". Retain means include or maybe. The LLM vote is exclude only if both runs exclude.

| | LLM retain | LLM exclude |
|---|---|---|
| **H1 retain** | 10 | 0 |
| **H1 exclude** | 8 | 81 |

- Agreement is 91/99, and Cohen's κ is 0.67. H1 retains 10 % of records; the LLM retains 18 %.
- Run 1 and run 2 gave the same decision in 98/99. The split is 1317 (maybe vs exclude).
- The first exclusion code is the same on 73 of the 81 joint excludes.
- The LLM excluded nothing that H1 kept.

## The 8 disagreements (all H1 exclude, LLM retain)

- *Domain, privacy in a list* (1269, 1351, 1358): H1 coded A-E3; the LLM `?A-I2;?A-I3`.
  - 1269 is a systematic review of big-data energy management, with "security and privacy" as one of six challenges.
  - 1351 is an Internet-of-Energy review that names smart metering and data privacy among many challenges.
  - 1358 is a blockchain-in-energy review; the LLM cites the blockchain rule, since it cannot tell whether privacy risks or only mechanisms are covered.
- *Privacy in a list* (1281, 1287): H1 coded A-E6; the LLM `?A-I3`.
  - 1281 is a scoping review of smart meters, so the domain is met. Privacy appears as a drawback and a research gap.
  - 1287 is a book chapter with a DOI on smart-grid consumers.
- *Synthesis or primary study* (1273, 1299, 1317): H1 coded A-E1;route=none.
  - 1273 is a "broadbrush description" of smart-grid security; the LLM flagged all four criteria.
  - 1299 analyses security and privacy threats in P2P trading "via smart meters", so domain and privacy are met. It presents its own business-model analysis rather than a stated review, and the venue is empty.
  - 1317 is an AI-for-smart-grid review with case studies. Run 2 agrees with H1 (A-E6).

## Other points (not disagreements)

- **1308** (privacy-preserving data aggregation survey, H1 include): both runs said `maybe ?A-I3` under the mechanism rule, because the abstract does not show privacy risks or attacks. Both sides retain. This is the type of 493, 889 and 971.
- **H1 include vs LLM maybe** (1295, 1324, 1331): both sides retain.
  - 1295 is a legal analysis that argues for a new protection concept, so A-I1 is open, and peer review of the Edward Elgar chapter cannot be judged.
  - 1324: privacy risk to clients' power use is named, but the stated focus is protection against cyber-attacks.
  - 1331 calls itself "This talk" (SPIE), so peer review is unclear (`?A-I4`).
- **1334:** H1 now codes it A-E2, as raised at the H1 check. Both runs excluded it as A-E3.
- **1268** (A-E7, electricity-theft detection review): both runs said maybe. A-E7 rows stay excluded under D19.
- **Book chapters (11):** 10 have a DOI. 1286 has none and is A-E4 for H1; both runs excluded it as A-E3.
- **First-code differences on 8 joint excludes** (1264, 1286, 1297, 1300, 1332, 1334, 1347, 1359). None changes a decision.

## Assessment

- κ 0.67 equals batch 10, the third-best batch after batches 3 (0.84) and 8 (0.79).
- All 8 disagreements are the known types: domain, A-E6 vs `?A-I3`, and synthesis or primary study.
- Candidates worth a full-text look: 1299 and 1281 (domain met) among the disagreements, and 1308 and 1295 among the includes.

## Reconciliation (2026-10-19)

- **The 8 disagreements:**
  - 5 retained (1269, 1273, 1281, 1351, 1358) to check privacy depth at full text; for 1273 also whether it reviews existing work and was peer-reviewed.
  - 3 excluded (1287, 1299, 1317).
- **I tidied the reasons without changing any decision:**
  - Grammar ("need to be evaluated in full paper"), plus the code added to each exclude reason.
  - 1287 and 1317: coded A-E6, since privacy is only named as one challenge. "Bullet point" was replaced by the wording of each abstract.
  - 1299: the reason cited missing peer-review status, which is not an exclusion ground (it would mean `maybe ?A-I4`), and "does not fit a systematic literature review", while A-I1 asks for any secondary study. The reason now rests on A-E1;route=none: the paper presents its own business-model analysis rather than a review of existing work.
  - 1273: the reason now also names the open A-I1 and A-I4 points.
  - The previous version is in `_archive/stream-a-v1.batch13.compare.before-tidy.csv`.
- **Final result:** 15 retain, 85 exclude.
