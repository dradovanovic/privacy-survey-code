# Full-text batch 07: H1 vs LLM (screen-A-ft-v2, frozen)

Prompt SHA-256 `305da17b…04b5`; model `claude-opus-5-5`; two runs, 07.11.2026. Logs: `llm/stream-a-v1.ft-batch07.screen-A-ft-v2.run1.jsonl` / `.run2.jsonl`.
20 papers run (1257 on PDF pp. 164–175 of the LNCS volume). No retries, no schema errors. Quotes not on the page: 1281 A-I4 empty in both runs (judged unclear, no venue in the text); 1358 A-I3 run 1 not found only because of a curly versus straight apostrophe (quote is on p. 13).

H1 (20): 10 include, 10 exclude (H1 changed 1257, 1273, 1288, 1324 and 1379 before the run, on Claude's remarks, not on LLM output). Decision agreement with H1: run 1 14/20, run 2 14/20; run 1 vs run 2 20/20 (flags differ only for 1243).

## Disagreements
- **1257** residential DSM privacy survey (LNCS 8448, 2014): H1 include; LLM A-E1 in both runs (mixed-paper rule: own analysis of three DR types in the BSI Smart Meter Gateway setting, Section 4, pp. 167–170, named in the abstract; own household privacy component, Section 5.1, p. 170). Borderline in both runs; A-I3 itself is met (Section 2, p. 165).
- **1273** smart-grid security issues (IEEE S&P 2010): H1 include; LLM A-E4 in both runs ("Building Security In" department with department editors, p. 1 → column).
- **1282** smart meter data intelligence survey (IEEE TII 2016): H1 include; LLM A-E6 in both runs (privacy not a stated aim, no section or comparison dimension; pp. 6, 7, 9 only).
- **1288** privacy preservation in smart grids (IGI Global chapter, 2019): H1 include; LLM A-E4 in both runs (book chapter, "Chapter 7", p. 1; edited-book rule 01.11.2026).
- **1308** PPDA survey (JKSU-CIS 2025): H1 A-E3 mechanism_only; LLM include in both runs (privacy is the stated aim; inference paragraph p. 2; differential-attack leakage p. 15; narrow margin).
- **1324** IoT-based smart grid review (ICRITO 2021): H1 include; LLM A-E6 in both runs (privacy only in scattered sentences, pp. 1–2).

## Code differs (decision agrees)
- **1243** machine unlearning survey (Array 2026): H1 A-E3; LLM A-E1 in both runs (own compliance workflow, certification framework and audit architecture, contributions list p. 4; Sections 2.2.3, 6.2, 6.3.1). A-I1 is checked before A-I2.
- **1259** digital transformation of energy systems (IET Smart Grid 2026): H1 A-E3; LLM A-E1 in both runs (own six-dimensional data governance framework, p. 2, Section 5); both runs also find A-I2 not met.
- **1269** big data smart energy management (RSER 2016): H1 A-E3; LLM A-E6 in both runs → keep A-E3 (H1's A-I2 judgment).

## Reconciliation (H1, 07.11.2026)

| n | H1 blind | Final | Reason |
|---|---|---|---|
| 1257 | include | **exclude A-E1** (route none) | Own DR-type privacy analysis (Section 4) and household privacy component (5.1) named in the abstract; mixed-paper rule. |
| 1273 | include | **exclude A-E4** | Department column in IEEE S&P. |
| 1282 | include | **exclude A-E6** | Privacy only in passing (pp. 6, 7, 9). |
| 1288 | include | **exclude A-E4** | IGI Global edited-book chapter (rule 01.11.2026). |
| 1308 | exclude A-E3 | **include** | Privacy aim, inference paragraph p. 2, differential-attack leakage p. 15; narrowly beyond mechanism_only. |
| 1324 | include | **exclude A-E6** | Privacy only in scattered sentences. |
| 1243 | exclude A-E3 | **exclude A-E1** (route none) | Own compliance, certification and audit frameworks; A-I1 before A-I2. |
| 1259 | exclude A-E3 | **exclude A-E1** (route none) | Own data governance framework; A-I1 before A-I2. |
| 1269 | exclude A-E3 | **exclude A-E3** | H1 A-I2 judgment kept (LLM A-E6). |

All final decisions agree with both LLM runs except 1269 (code only).

Batch 07 closed: 6 include (1308, 1350, 1354, 1364, 1368, 1379), 14 exclude (5 A-E3: 1247, 1269, 1351, 1358, 1383; 4 A-E1: 1243, 1246, 1257, 1259; 3 A-E6: 1281, 1282, 1324; 2 A-E4: 1273, 1288).
