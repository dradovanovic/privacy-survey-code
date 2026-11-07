# Full-text batch 06: H1 vs LLM (screen-A-ft-v2, frozen)

Prompt SHA-256 `305da17b…04b5`; model `claude-opus-5-5`; two runs, 04.11.2026. Logs: `llm/stream-a-v1.ft-batch06.screen-A-ft-v2.run1.jsonl` / `.run2.jsonl`.
19 papers run; **n 1176 not run** (no text layer: Microsoft Print to PDF, 17 pages; H1 exclude A-E3 stands, not checked by the LLM). No retries, no schema errors; all quotes on the cited page except one A-I2 quote for 1059 in run 1 (not found; run 2 quote for the same criterion found).

H1 (20): 13 include, 7 exclude (H1 changed 1081, 1128 and 1225 before the run, on Claude's remarks, not on LLM output). Decision agreement with H1 (19 run): run 1 17/19, run 2 16/19; run 1 vs run 2 18/19 (1169).

## Disagreements
- **1065** DSM review (IEEE ICET 2021): H1 exclude A-E6; LLM include in both runs, literal reading: dedicated subsection "J. Preserving User's Privacy in DSM" (p. 3) and a row in Table I (p. 4). Both runs call it borderline: the subsection is one paragraph summarising three mechanism papers [42]–[44], with no inference risks. Compare 915 (literal dedicated section, A-E3 mechanism_only) and 870.
- **1169** FL in smart grids (Knowledge and Information Systems 2026): H1 include; run 1 include, run 2 exclude A-E3 (mechanism_only). Privacy attacks are only named (Table 5, p. 28: "Inference attacks, membership inference, privacy leakage"; layer list pp. 28–29; p. 75); the only inference statement is the motivating sentence opening Section 4.2.1 (p. 29), which then lists mechanisms (aggregation, DP, synthetic data, pp. 29–31). Under the FL rule this reads as mechanism_only, as 1081; contrast 918 (include: explicit model-centric privacy threats).

## LLM unclear (decision not reached)
- **1225** (CEUR-WS 2014): LLM unclear in both runs, A-I4 unclear because the text shows no venue; A-I1–A-I3 met. H1 A-E4 from the record: ESSoS Doctoral Symposium 2014 (CEUR-WS Vol-1298, dblp), short overview plus the author's PhD plan (p. 5), treated like 1039. Final A-E4.

## Reconciliation (H1, 04.11.2026)

| n | H1 blind | Final | Reason |
|---|---|---|---|
| 1065 | exclude A-E6 | **exclude A-E6** | One-paragraph privacy subsection, no inference risks (one-paragraph mention). |
| 1169 | include | **exclude A-E3** (mechanism_only) | Attacks only named, privacy part lists mechanisms; as 1081. |
| 1225 | exclude A-E4 | **exclude A-E4** | Doctoral-symposium paper; LLM cannot judge A-I4 from the text. |

Batch 06 closed: 12 include (1051, 1059, 1060, 1109, 1123, 1134, 1137, 1147, 1161, 1174, 1198, 1229), 8 exclude (5 A-E3: 1081, 1128, 1169, 1176, 1204; 1 A-E6: 1065; 1 A-E1: 1201; 1 A-E4: 1225; 1176 not checked by the LLM).
