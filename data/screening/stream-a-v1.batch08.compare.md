# Batch 8 comparison: H1 vs screen-A-v1 (records 761–860)

Date: 2026-10-19. Frozen prompt screen-A-v1 (SHA-256 `df082ced…0a53`), model `claude-opus-5-5`, Claude Code 2.1.303, two runs.

- All 200 answers are valid, with no retries.
- The CLI updated itself from 2.1.302 to 2.1.303 before this batch. Both runs used 2.1.303, and every output line records it. `screening_spec.md` §4.1 now reads "2.1.300 to 2.1.303"; the previous version is in `_archive/screening_spec.before-cc303.md`.
- Per-record table: `stream-a-v1.batch08.compare.csv`. `ta_final` is pre-filled for the agreements; the 5 disagreements are empty.

## Numbers

No record in this batch is `A-E7`, and none is marked "discussed", so all 100 count. Retain means include or maybe. The LLM vote is exclude only if both runs exclude.

| | LLM retain | LLM exclude |
|---|---|---|
| **H1 retain** | 11 | 0 |
| **H1 exclude** | 5 | 84 |

- Agreement is 95/100, and Cohen's κ is 0.79. H1 retains 11 % of records; the LLM retains 16 %.
- Run 1 and run 2 gave the same decision in 98/100. The splits are 808 and 820.
- The first exclusion code is the same on 72 of the 84 joint excludes.
- The LLM excluded nothing that H1 kept.

## The 5 disagreements (all H1 exclude, LLM retain)

- **779**, "Privacy Measures and Storage Technologies for Battery-Based Load Hiding - an Overview and Experimental Study". H1 coded A-E1;route=C (mixed overview and experiment); both runs said `?A-I1;?A-I4`.
  - Smart-meter privacy is the main theme. The open point is whether the synthesis or the experiment is the main contribution.
  - The venue field is empty, so peer review cannot be confirmed from the record.
- **808**, "Smart Grids Data Analysis: A Systematic Mapping Study". H1 coded A-E3. The runs split: run 1 said `maybe ?A-I3`, run 2 said exclude A-E2.
  - Both runs note that privacy is not among the mapped facets, and that "private datasets" means data availability. This is a weak retain.
- **827**, ICT in demand-side management. H1 coded A-E6; both runs `?A-I3`. Data privacy is named only in a list of open issues. This is the known A-E6 vs `?A-I3` boundary.
- **828**, "Post-Quantum Secure Blockchain-Based Federated Learning Framework". H1 coded A-E1;route=C; both runs `?A-I1;?A-I2;?A-I3`.
  - The paper reviews 206 articles but also proposes its own framework, and privacy is framed through mechanisms.
- **840**, cyber-attack review. H1 coded A-E2; the LLM `?A-I2;?A-I3`. Privacy appears only as the keyword "user privacy", so A-E2 holds on the text.

## Other points (not disagreements)

- **820** (blockchain survey) agrees on retain only because run 2 said maybe. Run 1 excluded it as A-E3 `mechanism_only`: privacy appears only as "data privacy protection based on blockchain-based data aggregation technology", with no privacy risks named.
  - H1's include stands as recorded. It is the same type as 493, 562 and 646, so it is worth a check at full text.
- **816 and 834** (federated learning): H1 included both; both runs said maybe because the abstract shows privacy only as mechanisms.
  - 834 also "proposes a fractal-aware federated AI framework", so A-I1 needs a full-text check, as with 701 in batch 7.
- **782 and 783** (book chapters): H1 included both; the LLM said maybe because neither abstract names smart meters or consumer data. 782's abstract shows no privacy content beyond the title.
- **Book chapters (6):** all have a DOI. None was excluded on DOI grounds.
- **First-code differences on 12 joint excludes,** none of which changes a decision:
  - 780, 781, 819, 823, 859: H1 coded A-E6, the LLM A-E3. A-E3 comes first under the order rule if the domain fails.
  - 787, 803: H1 coded A-E1, the LLM A-E3.
  - 775: H1 coded A-E2, the LLM A-E3.
  - 802: H1 coded A-E3, the LLM A-E2.
  - 850: H1 coded A-E3, the LLM A-E6.
  - 764, 767: run split between A-E1 and A-E3.

## Assessment

- κ 0.79 is the second-best batch so far, after batch 3 (0.84).
- The disagreements are the known types: synthesis or primary study, A-E6 vs `?A-I3`, and privacy only as a keyword.
- Candidates worth a full-text look: 779 among the disagreements, and 820 and 834 among the includes.

## Reconciliation (2026-10-19)

- **The 5 disagreements:**
  - 3 retained (779, 808, 828) to check A-I1 or the privacy dimension at full text.
  - 2 excluded (827, 840).
- **I tidied the reasons without changing any decision:**
  - Grammar ("need to be checked"), plus the code added to each exclude reason.
  - 840: the reason said privacy is "a side note for open challenges", but the abstract never mentions privacy. It appears only as the keyword "user privacy", so the exclusion rests on A-E2.
  - The previous version is in `_archive/stream-a-v1.batch08.compare.before-tidy.csv`.
- **Final result:** 14 retain, 86 exclude.
