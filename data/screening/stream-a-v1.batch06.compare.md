# Batch 6 comparison: H1 vs screen-A-v1 (records 561–660)

Date: 2026-10-17. Frozen prompt screen-A-v1 (SHA-256 `df082ced…0a53`), model `claude-opus-5-5`, Claude Code 2.1.302, two runs.

All 200 answers are valid. Two records per run needed a retry, and every retry succeeded.
- The failure was the same each time: the first answer came back empty (`Expecting value: line 1 column 1`), and the retry gave a valid exclude.
- This happened before: 3 times in batch 1 and once in batch 5, 9 calls in total.
- The script logs the error in `first_attempt_error`. This is covered by the "one retry" rule in `screening_spec.md` §4.1.

Per-record table: `stream-a-v1.batch06.compare.csv`. `ta_final` is pre-filled for agreements and the A-E7 row; the 12 disagreements are empty.

## Numbers

Row 612 is `A-E7` (no abstract) and is left out, so 99 records count. No row is marked "discussed".

| | LLM retain | LLM exclude |
|---|---|---|
| **H1 retain** | 8 | 1 |
| **H1 exclude** | 11 | 79 |

- Agreement is 87/99, and Cohen's κ is 0.51. H1 retains 9 % of records; the LLM retains 19 %.
- Run 1 and run 2 gave the same decision in 94/99 and the same retain/exclude in 95/99. The splits are 586, 601, 615, 639 and 646.
- The first exclusion code is the same on 74 of the 79 joint excludes.

## The 12 disagreements

**H1 retain, LLM exclude (1)**

- 562, "Review on data privacy and security for IoT-based multifunctional layers of cyber-physical systems in smart grids". H1 included it; both LLM runs excluded it as A-E3.
- The LLM gives two reasons:
  - AMI is one CPS component next to SCADA and WAMS.
  - The abstract "highlights cryptographic techniques as significant mechanisms", with no visible privacy risks or inference, so it reads as a mechanism-only survey.
- This is the same pattern as 493 in batch 5, which H1 reconciled to exclude.

**H1 exclude, LLM retain (11)**

- *Privacy in a list or as future work* (565, 568, 575, 601): H1 coded A-E6; the LLM coded `?A-I3`, and run 2 on 601 said exclude.
- *Domain unclear* (576, 606, 614, 639, 643): H1 coded A-E3; the LLM coded `?A-I2`.
  - 576 and 614 have privacy in the title: "while maintaining user privacy" and "privacy preserving local energy markets".
- *Synthesis or primary study* (615, 657): H1 coded A-E1;route=none.
  - Run 1 on 615 agrees with H1, quoting the abstract: "not intended to be a comprehensive review".

## Other points (not disagreements)

- **646** (comparison of cryptographic approaches) agrees on retain only because run 1 said maybe; run 2 excluded it as A-E3 `mechanism_only`.
  - H1's include stands as recorded.
  - It has the same issue as 493 and 562, so it is worth a check at full text.
- **Book chapters (9):** all have a DOI. None was excluded on DOI grounds.
- **First-code differences on 5 joint excludes,** none of which changes a decision:
  - 589 and 641: H1 coded A-E1;route=C, the LLM A-E3.
  - 592: H1 coded A-E3, the LLM A-E6.
  - 613 (off-topic book review): H1 coded A-E4, the LLM A-E3.
  - 618: run split.

## Assessment

- κ 0.51 is in line with batches 4 and 5.
- The disagreements are the known types: A-E6 vs `?A-I3`, domain unclear, and synthesis or primary study.
- One more mechanism-only case (562) appears in the direction where the LLM would drop a paper H1 keeps.
- Candidates worth a full-text look rather than a quick exclude: 562, 576, 614 and 646.

## Reconciliation (2026-10-17)

- **562** changed from H1 include to exclude: the paper covers cryptographic approaches only, with no explicit privacy part (`mechanism_only`, A-E3). This matches the decision on 493 in batch 5.
- **The other 11 disagreements:**
  - 3 retained (565, 575, 601) to check privacy depth at full text.
  - 8 excluded (568, 576, 606, 614, 615, 639, 643, 657).
- **I tidied the reasons without changing any decision:**
  - Typos, plus the code added to each reason.
  - 614: the reason said "different smart meter applications", but the abstract never names smart meters. It now says smart-meter data is not named (A-E3).
  - The previous version is in `_archive/stream-a-v1.batch06.compare.before-tidy.csv`.
- **Final result:** 11 retain, 89 exclude.
