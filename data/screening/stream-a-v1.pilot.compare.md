# Pilot comparison: H1 vs screen-A-v1 (Stream A, 60 records)

Date: 2026-10-10. Model `claude-opus-5-5` via Claude Code 2.1.296 print mode, two runs, prompt SHA-256 `df082ced…0a53`.
Development set only: these figures are for tuning and are never reported as performance (`screening_spec.md` §4).
Per-record table with empty `ta_final` / `ta_final_reason` columns: `stream-a-v1.pilot.compare.csv`.

## Numbers

Retain = include or maybe. The LLM vote is exclude only if both runs exclude.

| | LLM retain | LLM exclude |
|---|---|---|
| **H1 retain** | 9 | 6 |
| **H1 exclude** | 10 | 35 |

- Agreement 44/60 (73 %), Cohen's κ 0.35.
- Records with an abstract (46): agreement 39/46 (85 %), κ 0.54.
- Records without an abstract (14): agreement 5/14. Eight of the ten "H1 exclude, LLM retain" cases are here.
- Run 1 vs run 2: same decision in 58/60, same retain/exclude in 59/60 (row 60 only).
- Same first exclusion code on 19 of the 35 joint excludes.

## Where the disagreements come from

**1. No abstract (rows 7, 8, 10, 16, 40, 41, 42, 60).** H1 excluded them; the LLM said `maybe` because the title alone does not fail questions 1–3. That is what the card and the prompt say to do ("No abstract → maybe, abstract_missing, unless the title alone clearly fails question 1–3"). H1's notes ("no privacy", "no survey") come from knowledge beyond the title. The LLM followed the rule; H1 did not.

**2. H1 retained using full-text knowledge (rows 35, 37, 52, 58).** H1's notes cite things an abstract cannot show ("privacy section", "privacy comparison dimension"). On the abstract alone:
- 35 and 58 are generic IoT surveys with no smart-meter mention → A-E3 under the criteria (A-E3 explicitly covers "privacy discussed only for generic IoT").
- 37 is a NILM survey where privacy is one item in a list of future challenges → A-E3 `nilm_only` under the NILM rule.
- 52 is a federated-learning review where privacy is only the motivation for the mechanism → A-E3 `mechanism_only` under the mechanism rule.
If these papers are valuable, they are `exclude` + `background`, not corpus papers, unless you decide to change the criteria.

**3. Genuine borderline calls (rows 3, 11, 21, 57).**
- 3: the abstract names "privacy preserving approaches"; H1 A-E6, LLM `maybe ?A-I3`. The card says use A-E6 at T/A only if the abstract itself shows a side remark; both readings are defensible.
- 11: IoT data-aggregation review, smart grids one item in a list; LLM A-E3. Your own note says "broader context with IoT".
- 21: the abstract never mentions privacy (only "secure"); LLM A-E3 is right on the text.
- 57: the abstract says "We review current approaches for protecting and monitoring AMIs"; H1 "no survey", LLM `maybe ?A-I1`. Retaining is the safer T/A call.

**4. First-code differences (16 joint excludes).** These do not change any decision. In rows 6, 24, 25, 45 the abstract describes a primary study ("we propose", "a new model … introduced"), so A-E1 comes first; in rows 39, 46 the NILM/mechanism rules make A-E3 come before A-E2. In rows 17, 29 the LLM judged the record a survey where H1 did not; that is a judgement call.

## Assessment

- No disagreement points to a prompt error. The model applied the criteria and borderline rules literally and was very stable across runs.
- The two systematic causes are on the input side: missing abstracts, and H1 using knowledge beyond the title and abstract.

## Recommended before the main run

1. **Fill missing abstracts** (239 of 1,687 records have no abstract or one under 30 words; 14 of the 60 pilot records), from the publisher page or the PDF's first page, with `abstract_source = manual`. Both H1 and the LLM then judge the same text. Records still without one stay `maybe` + `abstract_missing`.
2. **H1 screens from the title/abstract view only** (like `stream-a-v1.pilot.md`), without opening the full text.
3. **Freeze screen-A-v1 unchanged.** No prompt edit is needed from this pilot.
4. **Reconcile the 16 pilot disagreements** in `stream-a-v1.pilot.compare.csv` (§5.3), as practice for the main workflow. Blind decisions stay as they are.

## Notes added 2026-10-13

- H1 confirmed that the pilot decisions also used the papers' sections, not only title and abstract. The pilot H1 decisions are kept as recorded and are partly full-text informed; this explains causes 1 and 2 above.
- Row 1: the reading view `stream-a-v1.pilot.md` showed "(no abstract)", but the sheet has a 327-word abstract (Semantic Scholar), which the LLM received. Both decided exclude A-E3, so the outcome is unaffected. From batch 1 on, the reading view and the LLM read the same file.
- Outcome: screen-A-v1 frozen unchanged (`code/prompts/CHANGELOG.md`).

## Reconciliation (2026-10-22 to 2026-10-24)

H1 decided all 16 disagreements; `ta_final` is set for all 60 rows. Final: **12 retain, 48 exclude**. The pilot stays out of all figures (§7); its retained records go to full-text screening with the main run's.

- **Agreements (44):** pre-filled from the shared vote (9 retain, 35 exclude).
- **Abstracts:** 14 records had no abstract during the pilot and got a publisher or database abstract afterwards. `stream-a-v1.pilot.md` now shows them, marked "abstract added after the pilot" (backup `_archive/stream-a-v1.pilot.before-abstracts.md`). H1 decided 7, 8, 16, 35, 40, 41 and 60 on those abstracts. Only 42 still has none and is A-E7 (D19).
- **Retained (3):** 3 (`?A-I3`), 57 (`?A-I1`) and 60 (`?A-I1`, `?A-I2`), each with the open point named in `ta_final_reason`.
- **Excluded (13):** A-E6 for 7, 8, 10, 16, 40, 41; A-E3 for 11, 21, 35, 37 (nilm_only), 52, 58; A-E7 for 42. 8 carries a note as a source for Stream B snowballing (it is a review, so it is not routed).
- **Consistency:** 11 and 35 (IoT privacy reviews with the smart grid as one domain) were first retained, then excluded as A-E3 to match the 20 agreed exclusions of this pattern in batches 1–16.
- Tidy: reasons were reworded to name the code and the open point; "no abstract" reasons on records that now have one were replaced by H1's content decisions. Backups: `_archive/stream-a-v1.pilot.compare.before-prefill.csv`, `…before-tidy.csv`, `…before-tidy2.csv`, `…before-final-tidy.csv`. The blind H1 and LLM columns are unchanged.
