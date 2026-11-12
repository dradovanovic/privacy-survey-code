# Full-text batch 08: H1 vs LLM (screen-A-ft-v2, frozen)

Prompt SHA-256 `305da17b…04b5`; model `claude-opus-5-5`; two runs, 07.11.2026. Logs: `llm/stream-a-v1.ft-batch08.screen-A-ft-v2.run1.jsonl` / `.run2.jsonl`.
22 papers run (1531 on PDF pp. 178–197 and 1547 on pp. 125–135 of their volumes). No retries, no schema errors. Quotes not on the page: 1413 A-I2 (both runs) and A-I3 (run 1), p. 2; the quotes are split by the two-column text layer and the judgments (met) are not in dispute.

H1 (22): 12 include, 10 exclude (H1 changed 1408 and 1419 before the run, on Claude's remarks, not on LLM output). Decision agreement with H1: run 1 18/22, run 2 18/22; run 1 vs run 2 decisions 22/22 (codes differ only for 1531).

## Disagreements
- **1394** FL for smart grid survey (ACM TCPS 2026): H1 include; LLM A-E1 in both runs (own FedGridShield framework named in the abstract and contribution (4), own Section 5, p. 20). Both runs call it borderline: Section 5 is a few sentences and the tool only implements the reviewed attacks and defences.
- **1395** consumer adoption challenges (Journal of Service Science 2012): H1 A-E1 (no systematic method); LLM include in both runs (self-described qualitative literature review, p. 1; own "Privacy" section on load profiling). A-I1 has no depth threshold (rule 02.11.2026). Venue is a Clute Institute journal; its peer review is not confirmed from the text.
- **1413** smart-meter data sharing (IEEE Power & Energy Magazine 2024): H1 include; LLM A-E1, route C, in both runs (review pp. 2–6, then the authors' own case studies pp. 7–12: searchable-encryption framework, proposed federated split learning with own experiments, HiFi-Gas; named in the abstract and conclusion).
- **1426** SDN-based smart-grid communication survey (IEEE COMST 2019): H1 include; LLM A-E3 in both runs (smart-grid communication as a whole; AMI is one subsection, VII.B, p. 23; privacy part mostly security).

## Code differs (decision agrees)
- **1446** smart-grid cyber-attacks (SASG 2025): H1 A-E6; LLM A-E3 in both runs (smart grid as a whole, AMI one of about twelve applications, p. 2). A-I2 is checked before A-I3.
- **1531** MATLAB data security and privacy chapter (ISRL 247, 2023): H1 A-E1; run 1 A-E1 (route C), run 2 A-E4 (chapter in an edited Springer volume, p. 178). A-I4 is checked before A-I1 (rule 01.11.2026).

## Reconciliation (H1, 07.11.2026)

| n | H1 blind | Final | Reason |
|---|---|---|---|
| 1394 | include | **exclude A-E1** (route none) | Own FedGridShield framework in abstract, contribution (4) and Section 5; mixed-paper rule, borderline. |
| 1395 | exclude A-E1 | **exclude A-E4** | Clute Institute journal; peer review not confirmed. |
| 1413 | include | **exclude A-E1** (route C) | Own case studies pp. 7–12, named in title and abstract. |
| 1426 | include | **exclude A-E3** | Whole-grid SDN communication; AMI one subsection (VII.B). |
| 1446 | exclude A-E6 | **exclude A-E3** | Whole smart grid; A-I2 before A-I3. |
| 1531 | exclude A-E1 | **exclude A-E4** | Edited-volume chapter (ISRL 247); A-I4 before A-I1. |

All final decisions agree with both LLM runs except 1395 (LLM include; H1 venue judgment) and 1531 (run 1 A-E1, code only).

Batch 08 closed: 9 include (1405, 1408, 1430, 1469, 1472, 1475, 1515, 1519, 1544), 13 exclude (8 A-E3: 1426, 1432, 1446, 1450, 1488, 1535, 1538, 1547; 2 A-E1: 1394, 1413; 2 A-E4: 1395, 1531; 1 A-E6: 1419).
