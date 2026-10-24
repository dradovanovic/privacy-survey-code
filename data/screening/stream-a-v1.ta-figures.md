# Stream A title/abstract screening: figures (screening_spec.md §7)

Date: 2026-10-24. Source: `stream-a-v1.batch01–17.compare.csv` (records n = 61–1687), computed with `code/screening/ta_figures.py`. The 60 pilot records (development set) are left out of every performance figure and appear only in the PRISMA counts. Positive = retain (include or maybe). The LLM vote is exclude only if both runs exclude. 95 % CIs are Wilson intervals.

## Records

| | Count |
|---|---|
| Records screened at title/abstract | 1,687 (pilot 60 + main run 1,627) |
| Main run, excluded as A-E7 (no abstract, D19) | 18; left out of the figures below |
| Main run, analysed | 1,609 |
| Retained for full text | **233** (main run 221, pilot 12) |
| Excluded | 1,454 (main run 1,406, pilot 48) |

Exclusion reasons (first code of the final reason; main run + pilot): A-E3 657, A-E1 576 (route C 289, route B 34, none 253), A-E6 98, A-E4 54, A-E2 50, A-E7 19.

## H1 vs LLM on the blind decisions (n = 1,609)

| | LLM retain | LLM exclude |
|---|---|---|
| **H1 retain** | 146 | 7 |
| **H1 exclude** | 168 | 1,288 |

- Observed agreement 89.1 %, Cohen's κ **0.57**. Prevalence: H1 retains 9.5 %, the LLM 19.5 %; κ is held down by the low prevalence of retains.
- Per batch κ ranges from 0.33 (batch 9) to 0.84 (batch 3); batch 17 (n = 27) gives 0.37.
- Against H1's blind decision as reference, the LLM has sensitivity 0.954 [0.909, 0.978] and specificity 0.885 [0.867, 0.900].

## Disagreements and their outcome

- **H1 exclude, LLM retain: 168.** H1 changed 77 of them to retain after re-examination; 91 stayed excluded.
- **H1 retain, LLM exclude: 7.** All 7 ended excluded.
- Agreements changed later: 2 (287, 313: both retained by both sides, then excluded as A-E4 because they are not peer-reviewed articles).
- In total H1's blind decision differs from `ta_final` on 86 records.

## Against the final decision (`ta_final`, n = 1,609)

| Screener | Sensitivity [95 % CI] | Specificity [95 % CI] |
|---|---|---|
| H1 alone (blind) | 0.652 [0.587, 0.711] (144/221) | 0.994 [0.988, 0.997] |
| LLM, two-run vote | 1.000 [0.983, 1.000] (221/221) | 0.933 [0.919, 0.945] |
| LLM, run 1 alone | 0.986 [0.961, 0.995] | 0.942 [0.928, 0.953] |
| LLM, run 2 alone | 0.977 [0.948, 0.990] | 0.942 [0.928, 0.953] |

- **Value of the LLM as second reviewer:** 77 of the 221 retained records (35 %) were excluded by H1 at first and are retained only because the LLM flagged them. Which of them reach the final corpus is known after full-text screening.
- **Caveat for reporting:** `ta_final` is not independent of the LLM. Agreements became final without re-examination, and only disagreements were reconsidered, so no record that both screeners excluded could become a retain. The LLM's sensitivity of 1.000 is therefore an upper bound (incorporation bias), and so is H1's specificity. This needs to be stated next to the table.

## LLM run-to-run agreement (n = 1,609)

- Same decision in 1,569 (97.5 %), same retain/exclude in 1,577 (98.0 %), κ 0.93.
- The 40 splits are 32 exclude vs maybe and 8 include vs maybe; no record was include in one run and exclude in the other.

## Notes

- The `discussed` flag (regex `\bdiscussed\b` on H1's note) hit 96, 157, 264 and 1597. All four are descriptive uses of the word, not records discussed with anyone, so no record is left out for that reason.
- On the 18 A-E7 records, the LLM vote was retain in 12 and exclude in 6; under D19 they are excluded regardless.
- Record 119 was excluded with a reason but no exclusion code; A-E6 was added to its reason on 2026-10-24 (backup `_archive/stream-a-v1.batch01.compare.before-119.csv`).
