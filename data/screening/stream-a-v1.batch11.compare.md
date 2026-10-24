# Batch 11 comparison: H1 vs screen-A-v1 (records 1061–1160)

Date: 2026-10-19. Frozen prompt screen-A-v1 (SHA-256 `df082ced…0a53`), model `claude-opus-5-5`, Claude Code 2.1.303, two runs.

- All 200 answers are valid. Each run needed one retry (empty first answer, `Expecting value: line 1 column 1`), and both retries succeeded. This is the same benign failure as in earlier batches, logged in `first_attempt_error`.
- Per-record table: `stream-a-v1.batch11.compare.csv`. `ta_final` is pre-filled for the agreements and the three A-E7 rows; the 10 disagreements are empty.

## Numbers

Rows 1075, 1136 and 1158 are `A-E7` (no abstract) and are left out, so 97 records count. No row is marked "discussed". Retain means include or maybe. The LLM vote is exclude only if both runs exclude.

| | LLM retain | LLM exclude |
|---|---|---|
| **H1 retain** | 5 | 0 |
| **H1 exclude** | 10 | 82 |

- Agreement is 87/97, and Cohen's κ is 0.46. H1 retains 5 % of records; the LLM retains 15 %.
- Run 1 and run 2 gave the same decision in 94/97. The splits are 1088, 1108 and 1124, all maybe vs exclude.
- The first exclusion code is the same on 72 of the 82 joint excludes.
- The LLM excluded nothing that H1 kept.

## The 10 disagreements (all H1 exclude, LLM retain)

- *Privacy in a list* (1065, 1071, 1120, 1124, 1128): H1 coded A-E6; the LLM `?A-I3`, sometimes with `?A-I2`.
  - 1124 (6LoWPAN security review) uses lifestyle inference only as motivation. Run 1 agrees with H1.
- *No privacy in the abstract* (1084, 1088, 1137): H1 coded A-E2.
  - In all three the abstract never mentions privacy, so A-E2 holds on the text. Run 2 on 1088 agrees with H1.
  - 1137 is a systematic review of deep learning on smart-meter data, so the domain is met; only privacy is missing.
- *Domain* (1108, 1114): H1 coded A-E3.
  - 1108 is an IoT-in-energy review. Run 1 excluded it too, as A-E6.
  - 1114 covers blockchain trading in energy communities, and privacy appears only as a keyword.

## A rule point

The five A-E6 disagreements come from two lines of the screening card that pull in different directions:

- "A survey listing 'security and privacy' as one of many topics with no visible depth → `maybe ?A-I3`."
- "Use `A-E6` at title/abstract only if the abstract itself shows privacy is a side remark (e.g. one word among many topics)."

H1 reads these cases under the second line and the LLM under the first. This is the most frequent disagreement type in every batch so far. Whether to settle it in the card is a protocol decision for H1; it would not change the frozen prompt.

## Other points (not disagreements)

- **1081 and 1123** (blockchain surveys H1 included): both runs said maybe, so they agree on retain.
  - 1081 names "Privacy and Security" as one of four focal areas but does not show privacy risks.
  - 1123 makes privacy the main theme and names "important privacy challenges" from blockchain transparency, which goes beyond mechanisms.
- **1147:** H1 included it; both runs said `?A-I2` because smart meters are never named.
- **A-E7 rows:** the LLM said maybe on 1075 and 1136 and exclude on 1158. A-E7 rows stay excluded under D19.
- **Book chapters (8):** all have a DOI except 1136, which is A-E7. None was excluded on DOI grounds.
- **First-code differences on 10 joint excludes** (1070, 1077, 1082, 1094, 1104, 1117, 1118, 1119, 1138, 1156). None changes a decision.

## Assessment

- κ 0.46 is in line with batches 4 to 7.
- All 10 disagreements are the known types, and half of them are the A-E6 vs `?A-I3` boundary above.
- Candidates worth a full-text look: 1137 (smart-meter domain met) among the disagreements, and 1081 among the includes.

## Reconciliation (2026-10-19)

- **The 10 disagreements:**
  - 3 retained (1065, 1128, 1137) to check privacy at full text.
  - 7 excluded (1071, 1084, 1088, 1108, 1114, 1120, 1124).
- **I tidied the reasons without changing any decision:**
  - Spelling ("analzyed", "apperes", "need to be checked"), plus the code added to each exclude reason.
  - 1084 and 1088: the reasons said privacy is "only mentioned", but neither abstract mentions privacy at all. The reasons now say so, which is what A-E2 means.
  - 1114: the reason said privacy appears "once as side note", but it appears only as a keyword, not in the abstract. The exclusion rests on the domain (A-E3).
  - 1071: the reason also said "peer-review status not clear". An unclear peer-review status is not an exclusion ground (it would mean `maybe ?A-I4`), so the reason now rests on A-E6 alone.
  - The previous version is in `_archive/stream-a-v1.batch11.compare.before-tidy.csv`.
- **Final result:** 8 retain, 92 exclude.
