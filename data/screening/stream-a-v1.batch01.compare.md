# Batch 1 comparison: H1 vs screen-A-v1 (records 61–160)

Date: 2026-10-15. Frozen prompt screen-A-v1 (SHA-256 `df082ced…0a53`), model `claude-opus-5-5`, two runs, 200/200 answers valid (3 retries after invalid JSON, all succeeded).
Batch 1 counts towards the reported figures: no prompt change was needed.
Per-record table: `stream-a-v1.batch01.compare.csv` (`ta_final` is pre-filled for agreements; the 11 disagreements are empty).

## Numbers

Retain = include or maybe. The LLM vote is exclude only if both runs exclude.

| | LLM retain | LLM exclude |
|---|---|---|
| **H1 retain** | 5 | 1 |
| **H1 exclude** | 10 | 84 |

- Agreement 89/100, Cohen's κ 0.43 (prevalence: H1 retains 6 %, LLM retains 15 %; κ is low because retains are rare). Without the 2 records marked "discussed": 88/98, κ 0.45.
- Run 1 vs run 2: same decision in 96/100.
- Same first exclusion code on 72 of the 84 joint excludes.

## The 11 disagreements

**H1 retain, LLM exclude (1)**
- 119, lattice-based post-quantum security survey for smart-grid networks: H1 maybe `?A-I3`; LLM A-E3 (mechanism only, smart meters not named). This is the direction where the LLM would miss a paper; H1's maybe stands unless the reconciliation says otherwise.

**H1 exclude, LLM retain (10)**
- *Privacy in a list of topics* (89, 133, 149, 157): H1 A-E6; LLM `maybe ?A-I3`. Both are within the rules: the card allows A-E6 when the abstract shows privacy is a side remark (one item in a list), and also says "when in doubt, maybe". The LLM chooses maybe more often.
- *Review plus own method* (90, 94): H1 A-E1; LLM `maybe ?A-I1`, because the abstract claims both a review and a proposed method. By the "first clear no" rule, an unclear question 2 is a maybe.
- *No abstract* (142, "Data analytics in metering infrastructure of smart grids – a review"): H1 A-E3 with the note "no abstract available"; LLM `maybe`. The title shows a review in the smart-meter domain, so by the rules this is `maybe` + `abstract_missing`, not A-E3.
- *Domain unclear* (79, privacy-themed legal/ethical review of digital energy systems at building and grid level): H1 A-E3; LLM `maybe ?A-I2`. Privacy is the main theme here; worth a full-text look.
- *Run split* (76, 146): one run exclude A-E3, the other maybe. Both mechanism-only cyber/crypto reviews outside smart-meter data; H1 A-E3.

## Assessment

- The LLM is the more inclusive reviewer, as intended for a second reviewer: it flagged 10 records H1 excluded, and missed only 1 that H1 kept.
- No disagreement points to a prompt error. Most come from the A-E6 vs `?A-I3` boundary and from mixed review/method papers, where the rules allow both readings.
- One H1 slip against the rules: 142 (no abstract, title in scope).

## Next

Reconcile the 11 rows in `stream-a-v1.batch01.compare.csv` (§5.3): fill `ta_final` (retain/exclude) and a one-line `ta_final_reason` saying why the other decision does not hold. When in doubt, retain. `stream-a-v1.h1.csv` stays as it is.
