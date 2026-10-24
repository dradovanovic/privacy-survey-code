# Batch 9 comparison: H1 vs screen-A-v1 (records 861–960)

Date: 2026-10-19. Frozen prompt screen-A-v1 (SHA-256 `df082ced…0a53`), model `claude-opus-5-5`, Claude Code 2.1.303, two runs.

- All 200 answers are valid. Run 2 needed one retry (empty first answer, `Expecting value: line 1 column 1`), and it succeeded. This is the same benign failure as in earlier batches, logged in `first_attempt_error`.
- Per-record table: `stream-a-v1.batch09.compare.csv`. `ta_final` is pre-filled for the agreements and the A-E7 row; the 13 disagreements are empty.

## Numbers

Row 898 is `A-E7` (no abstract) and is left out, so 99 records count. No row is marked "discussed". Retain means include or maybe. The LLM vote is exclude only if both runs exclude.

| | LLM retain | LLM exclude |
|---|---|---|
| **H1 retain** | 4 | 1 |
| **H1 exclude** | 12 | 82 |

- Agreement is 86/99, and Cohen's κ is 0.33, the lowest of all batches. H1 retains 5 % of records; the LLM retains 16 %.
- Run 1 and run 2 gave the same decision in 98/99 and the same retain/exclude in 99/99. The split is 918 (maybe vs include).
- The first exclusion code is the same on 72 of the 82 joint excludes.

## The 13 disagreements

**H1 retain, LLM exclude (1)**

- **889**, "Federated intelligence for smart grids: a comprehensive review of security and privacy strategies". H1 included it; both runs excluded it as A-E3 `mechanism_only`.
  - The LLM's reason: privacy appears only as a property of FL, and the abstract names no privacy risks or inference attacks on consumer or smart-meter data. The attacks it names are FDI and DDoS.
  - This is the same pattern as 493 and 562, which H1 reconciled to exclude.

**H1 exclude, LLM retain (12)**

- *Domain unclear, with privacy as a main theme* (865, 922, 927, 950): H1 coded A-E3.
  - 865 is a differential-privacy survey for CPS, with energy systems as one of four applications.
  - 922 is a systematic review whose main theme is personal information and "users' privacy protection" in energy big data, with smart meters as one strand.
  - 927 reviews privacy-preserving computation for electricity-market transactions.
  - 950 is a privacy-preservation overview for cyber-physical power systems that never names smart meters.
- *Domain unclear, privacy as one item* (863, 870, 951): H1 coded A-E3; the LLM `?A-I2;?A-I3`.
- *Primary study or framework* (882): H1 coded A-E3; the LLM `?A-I1;?A-I2`. It is a taxonomy of FL attacks, including inference attacks, but it also proposes its own threat model.
- *Smart-meter domain, privacy in a list* (869, 921, 934, 937): H1 coded A-E6; the LLM `?A-I3`. The domain is met in all four, since smart meters or AMI are the subject.

## A rule point

- Seven of the eight A-E3 excludes above give the same reason: smart-meter or AMI data is "not the principal subject".
- In 865, 922, 927 and 950 the abstract does not rule the domain in or out, and privacy is the main theme.
- The card says that a criterion which cannot be confirmed from the abstract makes the record maybe, not exclude. The LLM applies that rule here, which is why κ dropped.
- In batches 4 to 7, H1 retained similar cases at reconciliation (453, 686).

## Other points (not disagreements)

- **918** (privacy-aware FL survey) agrees on retain. Run 1 said maybe under the FL rule, and run 2 said include.
- **901 and 915:** H1 included both; both runs said `?A-I3` because privacy is one item in the abstract.
- **898** (A-E7): both runs also excluded it.
- **Book chapters (3):** all have a DOI. None was excluded on DOI grounds.
- **First-code differences on 10 joint excludes** (875, 897, 900, 906, 914, 928, 932, 944, 953, 956). None changes a decision.

## Assessment

- κ 0.33 is the lowest so far. The drop comes from H1 being stricter on the domain criterion (A-E3), not from the LLM.
- Candidates worth a full-text look rather than a quick exclude: 922, 950, 865 and 927 (privacy as a main theme), and 921 and 937 (smart-meter domain met).

## Reconciliation (2026-10-19)

- **889** changed from H1 include to exclude: privacy appears only as a property of federated learning (`mechanism_only`, A-E3). This matches the decisions on 493 and 562.
- **The other 12 disagreements:**
  - 5 retained (865, 870, 882, 922, 950) to check the smart-meter domain or privacy depth at full text.
  - 7 excluded (863, 869, 921, 927, 934, 937, 951).
- H1 confirmed that no tool helped draft the batch 8 or batch 9 decisions or notes.
- **I tidied the reasons without changing any decision:**
  - Grammar ("need to be checked", "to far aways"), plus the code added to each exclude reason.
  - 921, 934 and 937: the reasons gave A-E3, but smart meters or AMI are the subject of all three, so the domain is met (card question 3). The code is now A-E6.
  - 927: now coded as `mechanism_only` (A-E3), since the review covers privacy-preserving computation and blockchain mechanisms, and privacy breaches appear only as motivation.
  - 951: the reason said "domain is not clear" and "not technical". Neither is an exclusion ground: an unclear domain means maybe. The reason now states why the domain fails (smart-grid technologies in general, smart meters not named).
  - The previous version is in `_archive/stream-a-v1.batch09.compare.before-tidy.csv`.
- **Final result:** 9 retain, 91 exclude.
