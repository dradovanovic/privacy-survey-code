# Batch 4 comparison: H1 vs screen-A-v1 (records 361–460)

Date: 2026-10-17. Frozen prompt screen-A-v1 (SHA-256 `df082ced…0a53`), model `claude-opus-5-5`, two runs, 200/200 answers valid, no retries.
Per-record table: `stream-a-v1.batch04.compare.csv`. `ta_final` is pre-filled for the agreements; the 11 disagreements are empty.

## Numbers

No record in this batch is `A-E7`, and none is marked "discussed". Retain means include or maybe. The LLM vote is exclude only if both runs exclude.

| | LLM retain | LLM exclude |
|---|---|---|
| **H1 retain** | 6 | 0 |
| **H1 exclude** | 11 | 83 |

- Agreement is 89/100 and Cohen's κ is 0.48. H1 retains 6 % of records and the LLM retains 17 %.
- Run 1 and run 2 gave the same decision in 98/100 and the same retain/exclude in 99/100. The exception is row 362, where both sides still retain.
- The first exclusion code is the same on 74 of the 83 joint excludes.
- For the fourth batch in a row, the LLM excluded nothing that H1 kept.

## The 11 disagreements (all H1 exclude, LLM retain)

- **Factual error, 437** ("Legal Protection of Personal Data in Smart Grid and Smart Metering Systems", a book chapter). H1 coded A-E4 because the chapter has no DOI.
  - The record does have a DOI, `10.1007/978-1-4471-6663-4_2`. The reading view did not show DOIs, and the LLM did not see them either.
  - Under the book-chapter rule, A-E4 no longer applies, so the chapter has to be judged on questions 2–4.
  - Privacy is the main theme and smart metering is in the title. The only open question is whether the chapter is a synthesis or the authors' own legal analysis (`?A-I1`).
  - Run 1 said maybe and run 2 said include.
- **Privacy in a list, or privacy not in the abstract** (389, 396, 441):
  - 389 and 441: H1 coded A-E6 and the LLM `?A-I3`.
  - 396: H1 coded A-E2, but the IEEE keyword "Privacy" is the only sign of privacy, and the abstract never mentions it.
- **Domain unclear** (365, 379, 384, 453): H1 coded A-E3 and the LLM `?A-I2`.
  - 365 names "smart meter data leakage risks" and "user privacy leakage risks" as risk categories.
  - 384 has a "privacy-preserving solutions" category and an attack taxonomy for it, but covers SCADA systems.
  - 453 is a privacy-technology review across the energy sector, with AMI as one example.
- **Synthesis or primary study** (369, 387, 393):
  - 369 and 393: H1 coded A-E1;route=C.
  - 387: H1 coded A-E3.
  - The LLM gave `?A-I1` on all three. In 393 privacy is the main theme, but the paper reports pilot projects, and it has no venue and no DOI.

## Other points (not disagreements)

- First-code differences on 9 joint excludes, none of which changes a decision:
  - 376, 391: H1 A-E2, LLM A-E3.
  - 380, 452: H1 A-E6, LLM A-E3.
  - 448: H1 A-E3, LLM A-E6.
  - 363, 398, 403, 444: within-run or between-run variation around A-E1.
- The reading view leaves out the DOI on purpose, so that H1 sees exactly what the LLM sees. The DOI matters only for the book-chapter rule, so from now on I check the DOI of every book chapter at the comparison step.

## Assessment

- κ dropped from 0.84 to 0.48 because this batch had more borderline surveys. The disagreements are the known types, plus one fact error (437) that needs correcting.
- Candidates worth a full-text look rather than a quick exclude: 437, 365, 384, 453 and 393.

## Reconciliation (2026-10-17)

- The 11 disagreements: 5 retain (365, 384, 389, 437, 453) and 6 exclude (369, 379, 387, 393, 396, 441).
  - 437: retained, because the DOI exists and privacy is a main topic.
  - 453: retained after H1 found the paper in the ACM Digital Library.
  - 393: excluded under A-E4 after H1 searched for the venue and found none.
- I tidied four entries without changing any decision:
  - 453: `ta_final` read "include"; I set it to "retain".
  - 369: I added the missing closing bracket.
  - 384 and 393: I fixed typos.
  - The previous version is in `_archive/stream-a-v1.batch04.compare.before-tidy.csv`.
- Final result: 11 retain, 89 exclude.
