# Batch 17 comparison: H1 vs screen-A-v1 (records 1661–1687)

Date: 2026-10-22 (LLM runs 2026-10-22). Frozen prompt screen-A-v1 (SHA-256 `df082ced…0a53`), model `claude-opus-5-5`, Claude Code 2.1.304, two runs. This is the last batch.

- All 54 answers are valid. Run 1 needed one retry on ieee:10311539 (empty first answer, `Expecting value: line 1 column 1`), and it succeeded. This is the same benign failure as in earlier batches, logged in `first_attempt_error`.
- At the H1 check, the dates read 20.10.2026 although the batch was prepared on 22.10 at 07:56, and 1671 was coded A-E1;route=none for a pattern coded A-E6 elsewhere. H1 changed 1671 to A-E6 and most dates before the runs (h1 file saved 08:19:48, run 1 started 08:21:01). Rows 1665, 1672 and 1681 still read 20.10.2026.
- Per-record table: `stream-a-v1.batch17.compare.csv`. `ta_final` is pre-filled for the agreements; the 5 disagreements are empty.

## Numbers

No row is `A-E7`, so all 27 records count. No note contains "discussed". Retain means include or maybe. The LLM vote is exclude only if both runs exclude.

| | LLM retain | LLM exclude |
|---|---|---|
| **H1 retain** | 2 | 0 |
| **H1 exclude** | 5 | 20 |

- Agreement is 22/27, and Cohen's κ is 0.37. With 27 records and only 2 H1 retains, κ is unstable; one record moves it a lot. H1 retains 7 % of records; the LLM retains 26 %.
- Run 1 and run 2 gave the same decision in 25/27 and the same retain/exclude in 25/27. The splits are 1671 (exclude vs maybe) and 1680 (maybe vs exclude); in each, one run agrees with H1.
- The first exclusion code is the same on 15 of the 20 joint excludes.
- The LLM excluded nothing that H1 kept.

## The 5 disagreements (all H1 exclude, LLM retain)

- **1684**, "Review of the Data-Driven Methods for Electricity Fraud Detection in Smart Metering Systems". H1 coded A-E6; both runs said include.
  - The abstract has a dedicated privacy part: "we investigate how to preserve the consumers' privacy, using encryption and federated learning", and it names the inference risk of fine-grained readings.
  - The open point is whether a privacy section within a fraud-detection review is substantive (A-I3) or secondary (A-E6).
- *Privacy in a list or in passing* (1663, 1668, 1671): H1 coded A-E6; the LLM `?A-I3`, with `?A-I2` on 1668 and 1671.
  - 1663 has "Security and Privacy" in the title, but the abstract centres on security and key management and mentions privacy once.
  - 1668 and 1671 are broad smart-grid overviews that list privacy among several challenges. Run 1 on 1671 excluded it, as A-E3.
- *Domain* (1680): H1 coded A-E3. A review of ML on low-voltage substation load data that explicitly avoids new meters; privacy appears as one motivation. Run 2 agrees with H1 (A-E3).

## Other points (not disagreements)

- **Both H1 maybes are retained by both runs** (1673, 1686). Both are overviews with privacy as a main theme, held as maybe only because peer-review status is unclear: 1673 is in a law school repository (Scholarship at Catholic Law), 1686 in a TU München repository. H1 codes `?A-I1`, the LLM `?A-I4`. Under H1's rule that only definitely peer-reviewed papers are eligible, these are to be settled at full text.
- **Book chapter (1)**: 1665 has a DOI; H1 and both runs exclude it as A-E1.
- **First-code differences on 5 joint excludes**: 1664, 1670, 1672 (one run), 1682 are A-E1;route=none for H1 and A-E3 for the LLM; 1675 is A-E6 for H1 and A-E3 for the LLM. None changes a decision.

## Assessment

- All 5 disagreements are known types: A-E6 vs `?A-I3` (4) and domain (1). No new type appeared.
- Candidate worth a full-text look: 1684, the only record both runs include.
