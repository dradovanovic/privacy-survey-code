# Batch 2 comparison: H1 vs screen-A-v1 (records 161–260)

Date: 2026-10-16. Frozen prompt screen-A-v1 (SHA-256 `df082ced…0a53`), model `claude-opus-5-5`, two runs, 200/200 answers valid (2 retries, both succeeded).
Per-record table: `stream-a-v1.batch02.compare.csv` (`ta_final` is pre-filled for agreements and A-E7 rows; the 9 disagreements are empty).

## Numbers

Three records are `A-E7` (no abstract, D19) and are left out. Retain = include or maybe; the LLM vote is exclude only if both runs exclude.

| | LLM retain | LLM exclude |
|---|---|---|
| **H1 retain** | 11 | 0 |
| **H1 exclude** | 9 | 77 |

- Agreement 88/97 (91 %), Cohen's κ 0.66 (H1 retains 11 %, LLM retains 21 %). The 2 "discussed" rows (170, 224) agree, so the figures are the same without them.
- Run 1 vs run 2: same decision in 95/97.
- Same first exclusion code on 68 of the 77 joint excludes.
- The LLM excluded nothing that H1 kept.

## The 9 disagreements (all H1 exclude, LLM retain)

- *Privacy in a list of topics* (184, 198, 204, 253, 255): H1 A-E6; LLM `maybe ?A-I3`. Same boundary as in batch 1.
- *Domain unclear* (183, 192, 220): H1 A-E3; LLM `maybe ?A-I2`. In 183 (renewable energy communities, privacy in a dedicated chapter) and 220 (EV–grid privacy as a stated aim), privacy is central; the open question is only whether smart-meter data is a principal subject.
- *Review or primary study* (166, grid-edge digital privacy incl. smart metering, criteria-based assessment with an expert survey): H1 A-E1; LLM `maybe ?A-I1`.

## Assessment

- Better agreement than batch 1 (κ 0.66 vs 0.43), and again no prompt problem.
- The disagreements are the same two borderline types as before: A-E6 vs `?A-I3`, and domain or study type unclear. Both are judgement calls the rules allow either way, which is what reconciliation is for.
- Candidates worth a full-text look rather than a quick exclude: 166, 183, 220 (privacy is central in each).
