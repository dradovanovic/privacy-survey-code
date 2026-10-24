# Batch 10 comparison: H1 vs screen-A-v1 (records 961–1060)

Date: 2026-10-19. Frozen prompt screen-A-v1 (SHA-256 `df082ced…0a53`), model `claude-opus-5-5`, Claude Code 2.1.303, two runs.

- All 200 answers are valid. Run 1 needed one retry (empty first answer, `Expecting value: line 1 column 1`), and it succeeded. This is the same benign failure as in earlier batches, logged in `first_attempt_error`.
- Per-record table: `stream-a-v1.batch10.compare.csv`. `ta_final` is pre-filled for the agreements and the A-E7 row; the 9 disagreements are empty.

## Numbers

Row 1049 is `A-E7` (no abstract) and is left out, so 99 records count. No row is marked "discussed". Retain means include or maybe. The LLM vote is exclude only if both runs exclude.

| | LLM retain | LLM exclude |
|---|---|---|
| **H1 retain** | 12 | 2 |
| **H1 exclude** | 7 | 78 |

- Agreement is 90/99, and Cohen's κ is 0.67. H1 retains 14 % of records; the LLM retains 19 %.
- Run 1 and run 2 gave the same decision in 96/99 and the same retain/exclude in 98/99.
  - The splits are 973 (maybe vs exclude), and 996 and 1008 (maybe vs include).
- The first exclusion code is the same on 67 of the 78 joint excludes.

## The 9 disagreements

**H1 retain, LLM exclude (2)**

- **971**, "Recent advances on privacy-preserving distributed optimisation algorithms and their applications in smart grid". H1 included it; both runs excluded it as A-E3.
  - The LLM's reason: the review is organised by mechanism (encryption, differential privacy, correlated randomness). Privacy risks appear only as "information exchange among agents raises significant privacy concerns". Smart-meter or consumer data are not named.
  - This is the `mechanism_only` pattern of 493, 562 and 889, plus a domain question.
- **1053**, "Federated Learning for Privacy-Preserving Energy Management in Distributed Power Systems". H1 said `maybe ?A-I3`; both runs excluded it as A-E3.
  - The LLM's reason: the review is about energy-market frameworks and blockchain trading, not smart-meter data, and privacy appears only in the title and keywords.

**H1 exclude, LLM retain (7)**

- *Privacy in a list* (972, 973, 982): H1 coded A-E6; the LLM `?A-I2;?A-I3`. 972 and 982 are book chapters with a DOI. Run 2 on 973 agrees with H1.
- *No privacy in the abstract* (990, 1017): H1 coded A-E2. In both, privacy appears only as a keyword, so A-E2 holds on the text.
- *Primary study or position paper* (1039, 1045): H1 coded A-E1;route=none.
  - 1039 ("Privacy and security challenges in the smart grid user domain"): privacy is the main theme and names inference risks (presence, sleep-and-wake cycles). The abstract never says it reviews existing work, and the venue field is empty.
  - 1045: "a survey is presented" with "an analysis of the survey results" reads as a questionnaire, which supports H1.

## Other points (not disagreements)

- **The three mechanism-type includes** flagged at the H1 check:
  - 1036 (privacy-preserving aggregation, book chapter): both runs said include. The abstract names the inference risk directly ("an attacker can deduce whether a house is empty"), so it is not `mechanism_only`. This is the difference from 493.
  - 998 (homomorphic encryption) and 1051 (privacy-preserving aggregation): both runs said `maybe ?A-I3`, because the abstract centres on mechanisms. Both agree on retain.
- **H1 include vs LLM maybe** (976, 980, 1031, 1059): both sides retain.
  - 976 also presents its own "security pyramid" approach and a substation case study, so A-I1 is open.
  - 980, 1031 and 1059 never name smart meters or consumer data in the abstract.
- **1049** (A-E7, "Dualism in approach to protecting personal data"): both runs said maybe. A-E7 rows stay excluded under D19.
- **Book chapters (10):** all have a DOI. None was excluded on DOI grounds.
- **First-code differences on 11 joint excludes** (969, 974, 987, 1003, 1013, 1024, 1030, 1033, 1050, 1055, 1056). None changes a decision.

## Assessment

- κ 0.67 is the third-best batch, after batches 3 (0.84) and 8 (0.79).
- The two LLM excludes are both mechanism or domain cases, the same type H1 reconciled to exclude in batches 5, 6 and 9.
- Candidates worth a full-text look: 1039 among the disagreements, and 976 and 998 among the includes.

## Reconciliation (2026-10-19)

- **971** changed from H1 include to exclude, and **1053** from H1 maybe to exclude, both under A-E3:
  - 971 is organised by privacy-preserving mechanisms (`mechanism_only`), the same as 493, 562 and 889.
  - 1053 covers energy-market trading, not smart-meter data.
- **The other 7 disagreements:**
  - 3 retained (972, 982, 1039) to check privacy depth, or in 1039 the review and peer-review status, at full text.
  - 4 excluded (973, 990, 1017, 1045).
- **I tidied the reasons without changing any decision:**
  - Spelling ("depht", "besids", "its organized"), plus the code added to each exclude reason.
  - 973: the reason said privacy is a side note "besides cyber security". The abstract mentions privacy only as "federated learning for privacy preservation", and lists cyberattacks separately among the issues. The reason now says so (A-E6).
  - 1017: the reason said privacy is covered "in the connection to blockchain". The abstract never mentions privacy; it appears only as the keyword "Data privacy". The reason now rests on A-E2.
  - 1039: the reason said privacy depth needs a check, but privacy is the main theme and inference risks are named. The open points are whether the paper is a review (A-I1) and whether it was peer-reviewed (A-I4, venue empty).
  - The previous version is in `_archive/stream-a-v1.batch10.compare.before-tidy.csv`.
- **Final result:** 15 retain, 85 exclude.
