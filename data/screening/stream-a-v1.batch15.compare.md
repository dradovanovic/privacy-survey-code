# Batch 15 comparison: H1 vs screen-A-v1 (records 1461–1560)

Date: 2026-10-20. Frozen prompt screen-A-v1 (SHA-256 `df082ced…0a53`), model `claude-opus-5-5`, Claude Code 2.1.304, two runs.

- All 200 answers are valid. Run 1 needed one retry and run 2 two (empty first answer, `Expecting value: line 1 column 1`), and all retries succeeded. This is the same benign failure as in earlier batches, logged in `first_attempt_error`.
- The CLI updated itself from 2.1.303 to 2.1.304 before this batch. Both runs used 2.1.304, and every output line records it. `screening_spec.md` §4.1 now reads "2.1.300 to 2.1.304"; the previous version is in `_archive/screening_spec.before-cc304.md`.
- Per-record table: `stream-a-v1.batch15.compare.csv`. `ta_final` is pre-filled for the agreements and the two A-E7 rows; the 12 disagreements are empty.

## Numbers

Rows 1462 and 1485 are `A-E7` (no abstract) and are left out, so 98 records count. No row is marked "discussed". Retain means include or maybe. The LLM vote is exclude only if both runs exclude.

| | LLM retain | LLM exclude |
|---|---|---|
| **H1 retain** | 10 | 0 |
| **H1 exclude** | 12 | 76 |

- Agreement is 86/98, and Cohen's κ is 0.56. H1 retains 10 % of records; the LLM retains 22 %.
- Run 1 and run 2 gave the same decision in 92/98 and the same retain/exclude in 93/98, the most splits so far.
  - The retain/exclude splits are 1499, 1508, 1522, 1529 and 1559; in each, one run agrees with H1.
  - 1475 split between include and maybe.
- The first exclusion code is the same on 72 of the 76 joint excludes.
- The LLM excluded nothing that H1 kept.

## The 12 disagreements (all H1 exclude, LLM retain)

- *Privacy as a main finding* (1475): H1 coded A-E6; run 1 said include, run 2 `maybe ?A-I3`.
  - The review of residential load-profile models names participants' privacy concerns as "the most important challenge" and proposes an anonymisation algorithm and "privacy-proof smart-meters". This is more than a list item.
- *Privacy in a list* (1490, 1508, 1529, 1535, 1538): H1 coded A-E6; the LLM `?A-I3`, mostly with `?A-I2`.
  - Run 2 on 1508 and run 1 on 1529 agree with H1.
  - 1490 (electricity-theft review) names "privacy-preserving computation" as a technique family and "privacy exposure" as an evaluation factor.
- *No privacy in the abstract* (1499, 1519): H1 coded A-E2.
  - 1499 never mentions privacy; run 2 agrees with H1.
  - 1519 (AMI survey) mentions privacy only as a keyword, so A-E2 holds on the text.
- *Domain* (1522, 1559): H1 coded A-E3. Run 2 on 1522 and run 1 on 1559 agree with H1. Neither names smart meters or consumer data.
- *Mechanism or NILM* (1547, 1517): H1 coded A-E3.
  - 1547 (`mechanism_only`): both runs flagged `?A-I2`, and run 1 also `?A-I3` under the mechanism rule.
  - 1517 (`nilm_only`): the overview of neural NILM motivates FL with privacy ("energy data can reveal in-home activities and occupancy"). The LLM cites the NILM and FL rules.

## Other points (not disagreements)

- **1469 vs 1547:** both runs included 1469 and said explicitly that the `mechanism_only` rule does not apply, because privacy in the smart-meter domain is the review's stated aim. For 1547 they said maybe. Under the LLM's reading, the two are not the same case, mainly because 1547 never names smart meters.
- **1461** (title and abstract mismatch): both runs excluded it as A-E1, treating the abstract as missing and judging the title as a primary simulation study.
- **H1 include vs LLM maybe** (1472, 1515, 1531, 1544, 1549): both sides retain.
  - 1472 is an encryption-mechanism review; its threat branch may cover only cryptographic threats.
  - 1531 centres on a MATLAB implementation with case studies, so A-I1 is open.
  - 1549 is a legal overview, so it is open whether it synthesises existing work.
- **A-E7 rows:** the LLM said maybe on 1462, and split on 1485. A-E7 rows stay excluded under D19.
- **Book chapters (11):** all have a DOI. None was excluded on DOI grounds.
- **First-code differences on 4 joint excludes** (1470, 1477, 1505, 1520). None changes a decision.

## Assessment

- κ 0.56 is close to batch 14 (0.58).
- The 12 disagreements are the known types: A-E6 vs `?A-I3`, privacy only as a keyword, domain, and mechanism or NILM.
- The runs split more often than before (6 records). Each retain/exclude split had one run agreeing with H1, so these sit right on the boundary.
- Candidates worth a full-text look: 1475 among the disagreements, and 1472 and 1531 among the includes.

## Reconciliation (2026-10-21)

- **The 12 disagreements:**
  - 6 retained (1475, 1519, 1535, 1538, 1547, 1559) to check privacy depth at full text; for 1519 whether privacy is covered at all.
  - 6 excluded (1490, 1499, 1508, 1517, 1522, 1529).
- **I tidied the reasons without changing any decision:**
  - Spelling and grammar ("hanldes", "need to be checked in full paper"), plus the code added to each exclude reason.
  - 1475: `ta_final` was entered as "include"; it is now "retain", the value the file uses for every kept record. The reason now states what the abstract says about privacy.
  - 1499: the reason said privacy "is not handled in depth", but the abstract never mentions privacy, which is A-E2.
  - 1522: the reason said privacy "is only used to motivate the application", but the abstract lists data privacy as one of many application areas. The reason now rests on the domain (A-E3), H1's screening code.
  - 1517: coded A-E3 `nilm_only`, as in H1's screening code; privacy appears only as the motivation for federated learning.
  - 1490 and 1508: coded A-E6 with the abstract's wording; 1519 (retained) now notes that privacy is only a keyword.
  - 1475: the run 2 rationale had been merged into the run 1 cell and the run 2 cell emptied, probably during editing. Both cells are restored from the LLM output files, and all LLM columns of the batch now match them.
  - The previous version is in `_archive/stream-a-v1.batch15.compare.before-tidy.csv`.
- **Final result:** 16 retain, 84 exclude.
