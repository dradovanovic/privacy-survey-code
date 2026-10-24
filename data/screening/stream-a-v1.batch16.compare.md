# Batch 16 comparison: H1 vs screen-A-v1 (records 1561–1660)

Date: 2026-10-22 (LLM runs 2026-10-21). Frozen prompt screen-A-v1 (SHA-256 `df082ced…0a53`), model `claude-opus-5-5`, Claude Code 2.1.304, two runs.

- All 200 answers are valid. Run 2 needed two retries (empty first answer, `Expecting value: line 1 column 1`), and both succeeded. This is the same benign failure as in earlier batches, logged in `first_attempt_error`.
- At the H1 check, the batch 16 rows had been pasted one column to the right and had no notes. H1 corrected this before the LLM runs started (h1 file saved 11:14, run 1 started 11:15).
- Per-record table: `stream-a-v1.batch16.compare.csv`. `ta_final` is pre-filled for the agreements and the A-E7 row; the 11 disagreements are empty.

## Numbers

Row 1642 is `A-E7` (no abstract) and is left out, so 99 records count. The `discussed` flag on 1597 is a false positive: H1's note says privacy "is discussed mainly as an architectural advantage". Retain means include or maybe. The LLM vote is exclude only if both runs exclude.

| | LLM retain | LLM exclude |
|---|---|---|
| **H1 retain** | 16 | 0 |
| **H1 exclude** | 11 | 72 |

- Agreement is 88/99, and Cohen's κ is 0.68, the best since batch 8 (0.79). H1 retains 16 % of records; the LLM retains 27 %.
- Run 1 and run 2 gave the same decision in 96/99 and the same retain/exclude in 97/99. The splits are 1567 and 1597 (maybe vs exclude; one run agrees with H1 in each), and 1657 (maybe vs include).
- The first exclusion code is the same on 68 of the 72 joint excludes.
- The LLM excluded nothing that H1 kept.

## The 11 disagreements (all H1 exclude, LLM retain)

- **1604**, "On preserving user privacy in Smart Grid advanced metering infrastructure applications". H1 coded A-E1;route=C; both runs said include.
  - The abstract says it "identifies the threats regarding user and data privacy in AMI applications and comprehensively surveys the existing solutions", with pros and cons.
  - Its second contribution evaluates an existing solution (homomorphic encryption) rather than proposing a new one, so the LLM did not read it as a primary study.
- **1588**, "RETRACTED: A Taxonomy on Accountability and Privacy Issues in Smart Grids". H1 coded A-E4; both runs said `maybe ?A-I4`. The LLM finds A-I1 to A-I3 met and leaves the retraction to the lead reviewer, since the card has no rule for retracted papers.
- *Privacy in a list* (1568, 1592, 1597, 1654): H1 coded A-E6; the LLM `?A-I3`, sometimes with `?A-I2`. Run 1 on 1597 agrees with H1. 1597 is a book chapter with a DOI.
- *No privacy in the abstract* (1567, 1600): H1 coded A-E2. Neither abstract mentions privacy (1600 has it only as a keyword), so A-E2 holds on the text. Run 2 on 1567 agrees with H1.
- *Domain* (1587, 1610): H1 coded A-E3.
  - 1587 (book chapter with a DOI) covers 5G in local energy systems, with smart metering as one focus area and "consumer privacy" as one challenge.
  - 1610 is a privacy survey for V2G networks. Privacy is the main theme; the open point is whether V2G data (location, billing) counts as consumer-side data.
- *Synthesis or practice report* (1625): H1 coded A-E1;route=none; both runs `?A-I1`. Smart-meter data and privacy are central, and the open point is whether an overview of approved Dutch use cases is a synthesis of existing work.

## Other points (not disagreements)

- **H1 include vs LLM maybe** (1561, 1571, 1615, 1617, 1623, 1632, 1635, 1641, 1657, 1658): both sides retain.
  - 1617 says it "will also propose solutions", and 1635 experiments with five approaches, so A-I1 is open in both.
  - 1615 and 1632 may be position or legal-policy papers rather than syntheses (`?A-I1`).
  - 1561, 1571, 1623 and 1658 never name smart meters or consumer data (`?A-I2`).
- **1642** (A-E7): both runs excluded it as A-E3.
- **Book chapters (15):** 14 have a DOI. 1570 has none and is A-E4 for H1; both runs excluded it as A-E3.
- **First-code differences on 4 joint excludes** (1563, 1570, 1637, 1655). None changes a decision.

## Assessment

- κ 0.68 is among the best batches, after batches 3 (0.84) and 8 (0.79).
- 9 of the 11 disagreements are the known types: A-E6 vs `?A-I3`, privacy only as a keyword, domain, and synthesis or primary study.
- Two are new: a retracted paper (1588), for which the card has no rule, and a survey whose second part evaluates an existing method (1604).
- Candidates worth a full-text look: 1604 and 1610 among the disagreements, and 1617 and 1635 among the includes.

## Reconciliation (2026-10-22)

- **The 11 disagreements:**
  - 5 retained (1568, 1604, 1610, 1625, 1654) for a full-text check.
  - 6 excluded (1567, 1587, 1588, 1592, 1597, 1600).
- **I tidied the reasons without changing any decision:**
  - Spelling ("intendet", "need to be checked"), plus the code added to each exclude reason.
  - 1567: the reason said privacy is "not handled in the intended depth", but the abstract never mentions privacy, which is A-E2.
  - 1592 and 1597: coded A-E6, since both reasons argue privacy depth. 1597's reason gave A-E3, but the domain is not in question there.
  - 1587: the reason now names both points: the domain (A-E3) and privacy as one listed challenge.
  - The retained rows now name the open point for the full-text check instead of "full paper needs to be checked": the main contribution (1604), V2G data as consumer-side data (1610), and synthesis (1625).
  - The previous version is in `_archive/stream-a-v1.batch16.compare.before-tidy.csv`.
- **1588** (retracted paper): first retained, then changed by H1 to exclude, A-E4. The screening card has no rule for retracted publications yet. The version before this change is in `_archive/stream-a-v1.batch16.compare.before-tidy2.csv`.
- **Final result:** 21 retain, 79 exclude.
