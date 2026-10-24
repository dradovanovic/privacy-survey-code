# Batch 7 comparison: H1 vs screen-A-v1 (records 661–760)

Date: 2026-10-19. Frozen prompt screen-A-v1 (SHA-256 `df082ced…0a53`), model `claude-opus-5-5`, Claude Code 2.1.302, two runs.

- All 200 answers are valid. Run 2 needed one retry (empty first answer, `Expecting value: line 1 column 1`), and it succeeded. This is the same benign failure as in batches 1, 5 and 6, logged in `first_attempt_error`.
- Per-record table: `stream-a-v1.batch07.compare.csv`. `ta_final` is pre-filled for the agreements and the two A-E7 rows; the 12 disagreements are empty.

## Numbers

Rows 676 and 700 are `A-E7` (no abstract) and are left out, so 98 records count. No row is marked "discussed". Retain means include or maybe. The LLM vote is exclude only if both runs exclude.

| | LLM retain | LLM exclude |
|---|---|---|
| **H1 retain** | 7 | 0 |
| **H1 exclude** | 12 | 79 |

- Agreement is 86/98, and Cohen's κ is 0.48. H1 retains 7 % of records; the LLM retains 19 %.
- Run 1 and run 2 gave the same decision in 97/98. The split is 680.
- The first exclusion code is the same on 70 of the 79 joint excludes.
- The LLM excluded nothing that H1 kept.

## The 12 disagreements (all H1 exclude, LLM retain)

- *Domain unclear* (668, 680, 686): H1 coded A-E3; the LLM coded `?A-I2;?A-I3`.
  - 668 is an SLR on smart contracts in energy systems.
  - 680 is a distributed-optimization survey. Run 2 agrees with H1 (A-E3).
  - 686 surveys privacy-computing technology in the electric-power industry. Privacy is the main theme, so only the smart-meter domain is open.
- *Synthesis or primary study* (695): H1 coded A-E1;route=none; the LLM `?A-I1;?A-I2`. The paper analyses security and privacy issues in smart-grid software architectures.
- *Privacy in a list* (702, 718, 731, 732, 735, 742): H1 coded A-E6; the LLM `?A-I3`, sometimes with `?A-I2`.
  - 735 is a book chapter with a DOI (`10.1007/978-981-16-5936-2_6`).
  - 742 (electricity-theft SLR) names "privacy preservation-based methodologies" as one of its method groups. This is the same type as 274 in batch 3, which was retained.
- *No privacy in the abstract* (703): H1 coded A-E2; the LLM `?A-I3`. Privacy appears only as a keyword, so A-E2 holds on the text.
- *Concluding chapter* (711, "Conclusions and Future Directions"): H1 coded A-E1;route=none; the LLM flagged all four criteria as unclear. It is a book chapter with a DOI (`10.1007/978-3-319-04945-8_5`) and an abstract under 30 words, so the LLM had little to go on.

## Other points (not disagreements)

- **676** ("Protecting the Privacy of Electricity Consumers in the Smart City") has no abstract, so it is A-E7 under D19. Both LLM runs said maybe, but A-E7 rows are excluded and left out of the figures.
- **H1 include vs LLM maybe** (671, 698, 701): both sides retain.
  - 701 ("Privacy and security issues in smart grids: A survey") says it "proposes a comprehensive framework", so it may be partly a primary contribution (`?A-I1`). Worth a check at full text.
- **First-code differences on 9 joint excludes** (663, 669, 708, 713, 725, 734, 736, 739, 750). None changes a decision.

## Assessment

- κ 0.48 is in line with batches 4 to 6.
- All 12 disagreements are the known types: A-E6 vs `?A-I3`, domain unclear, and synthesis or primary study.
- Candidates worth a full-text look rather than a quick exclude: 686, 742 and 680, plus 701 among the includes.

## Reconciliation (2026-10-19)

- **The 12 disagreements:**
  - 5 retained (686, 695, 703, 718, 742) to check privacy depth or the smart-meter context at full text.
  - 7 excluded (668, 680, 702, 711, 731, 732, 735).
- **I tidied the reasons without changing any decision:**
  - Typos and grammar ("deph", "to short", "potentiall", "need to be"), plus the code added to each exclude reason.
  - 680: "distribution optimization" now reads "distributed optimization".
  - 711: the reason said privacy is only a side topic, but the one-sentence abstract describes the whole book as being about "secure and privacy-preserving communications in smart grids". The exclusion now rests on it being a concluding chapter (A-E1;route=none).
  - 718: the reason pointed to promising keywords, but the keyword field has none on privacy. The promising terms (federated learning, data privacy) are in the abstract highlights.
  - 732: the reason said privacy is listed as a challenge, but the abstract names it as something blockchain ensures. It is still a passing mention (A-E6).
  - The previous version is in `_archive/stream-a-v1.batch07.compare.before-tidy.csv`.
- **Final result:** 12 retain, 88 exclude.
