# Full-text batch 05: H1 vs LLM (screen-A-ft-v2, frozen)

Prompt SHA-256 `305da17b…04b5`; model `claude-opus-5-5`; two runs, 03.11.2026. Logs: `llm/stream-a-v1.ft-batch05.screen-A-ft-v2.run1.jsonl` / `.run2.jsonl`.
18 papers run; **n 980 not run** (encoded text layer in all available versions; H1 include stands, not checked by the LLM). No retries, no schema errors, all quotes on the cited page.

H1 (19): 12 include, 7 exclude (H1 changed 915, 950, 972, 976 before the run, on Claude's remarks, not on LLM output). Decision agreement with H1 (18 run): run 1 16/18, run 2 16/18; run 1 vs run 2 18/18 (codes differ only for 972).

## Disagreements
- **1031** AI-powered smart grids in the 6G era (IEEE OJ-COMS 2025): H1 include; LLM exclude A-E1 in both runs (mixed-paper rule). The own SAFES-6G framework is named in the abstract as "a novel conceptual framework", announced in the roadmap (p. 4), developed in its own Section VIII (PDF pp. 32–38, about 7 of 43 pages: architecture, standards, evaluation plan, use case, rollout) and called "a key contribution" in the conclusion. Compare 400, 453, 686, 828 (A-E1).
- **915** NAN security review (IEEE 2018): H1 exclude A-E6; LLM include in both runs, literal reading: dedicated section "VI. DATA PRIVACY MEASURES" (p. 5) and data privacy named in the abstract. Both runs call it borderline: the section covers only encryption and IDS, inference risk appears only in two short sentences (pp. 2, 4). Compare 778 (security review whose privacy section lists mechanisms only → A-E3 mechanism_only).

## Code differs (decision agrees)
- **870** DR survey (CDC 2014): H1 A-E6 (A-I2 met, privacy one short subsection); LLM A-E3 in both runs (A-I2 not met: AMI only one challenge within "Grid Structure", p. 3; A-I3 doubtful).
- **972**: H1 A-E4 (edited chapter rule); run 1 A-E4, run 2 A-E3 → keep A-E4.
- **976**: H1 A-E4 (edited chapter rule, A-I4 first); LLM A-E1 (own Security Pyramid) with A-I4 unclear → keep A-E4.

## Reconciliation (H1, 03.11.2026)

| n | H1 blind | Final | Reason |
|---|---|---|---|
| 1031 | include | **exclude A-E1** (route none) | Own SAFES-6G framework is a main contribution (abstract, Section VIII pp. 32–38, conclusion). |
| 915 | exclude A-E6 | **exclude A-E3** (mechanism_only) | Privacy section lists security mechanisms only; as 778. |
| 870 | exclude A-E6 | **exclude A-E3** | Smart meters one challenge among many (A-I2 test). |
| 972, 976 | exclude A-E4 | **exclude A-E4** | Edited book chapters (rule 01.11.2026). |

Batch 05 closed: 11 include (860, 865, 901, 918, 922, 945, 980, 984, 996, 998, 1037; 980 not checked by the LLM), 8 exclude (3 A-E3: 870, 915, 950; 3 A-E4: 972, 976, 1039; 2 A-E1: 882, 1031).
