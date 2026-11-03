# Full-text batch 01: H1 vs LLM (screen-A-ft-v2, frozen)

Prompt SHA-256 `305da17b…04b5`; model `claude-opus-5-5`; two runs, 01.11.2026. Logs: `llm/stream-a-v1.ft-batch01.screen-A-ft-v2.run1.jsonl` / `.run2.jsonl`. Text manifest: `code/data/fulltext/text/manifest.stream-a-v1.ft-batch01.input.csv`.
40 calls ok, no retries, no schema errors. H1 decided blind (30.10.2026) and tidied 01.11.2026 before the run.

H1: 7 include, 13 exclude. Decision agreement with H1: run 1 18/20, run 2 18/20; run-to-run 18/20 (209 and 218 changed).
Final decisions in `stream-a-v1.ft-batch01.compare.csv`; the 16 agreements are prefilled with H1's decision; 198 (code differs) and the three disagreements are left for H1.

## Disagreements

### 73 WSN applications in smart grid: H1 exclude A-E3, LLM include (both runs)
- A-I2: H1 not met (WSN across generation, delivery and utilization; smart meters/WAMR one area, pp. 2–4). LLM met, p. 3: "A typical application of WSN for smart grid is wireless automatic meter reading (WAMR) systems, which can determine real-time energy consumption of the customers"; both runs call A-I2 borderline.
- A-I3: H1 not met (privacy embedded in security). LLM met via rule (a), privacy named in the stated aim, p. 1: "an application review and taxonomy of relevant cyber security and privacy issues is presented in this paper." Both runs add that the actual privacy discussion is thin (one paragraph in 3.1.1 plus 3.2.1).

### 209 Cyber-physical security in electric smart grid: H1 exclude A-E3, LLM include (run 1) / exclude A-E3 (run 2)
- Run 2 = H1 (A-I2 not met, p. 5: "This paper concentrates on uncovering the limitations of existing security models and methods in evolving smart grid architectures.").
- Run 1: A-I2 met (smart meters replacing electromechanical meters, p. 1); A-I3 met via rule (a) and the dedicated "X. PRIVACY ISSUES" section, which it calls "very thin, only three sentences" and "a borderline include worth discussing".
- Both runs judge A-I3 met; H1 not met (three sentences, no contribution).

### 218 PPML for IoT-integrated smart grids: H1 include, LLM include (run 1) / exclude A-E3 mechanism_only (run 2)
- Point of difference: A-I3 under the mechanism-survey threshold (the rule set after n 14).
- Run 2: §3 threats are security attacks (malware, DoS, MITM, poisoning); inference risks appear only as one- or two-sentence motivations, p. 12: "Quasi-identifier (QI) attributes, such as timestamps and the locations of smart meters, can indirectly reveal energy usage patterns, habits, and living standards of individual households." and NILM on p. 19.
- Run 1: met, but "borderline, because the risk discussion is brief compared with the mechanism coverage"; points to Table 3, column "Adversaries or Attacks Types".
- Also relevant: p. 9 has a paragraph on data leakage, but it concerns interception of unencrypted consumption data and a vendor breach (acquisition), not inference.

## Code differs (decision agrees)
- **198** IoT techniques for smart power systems: H1 A-E3 (A-I2 not met), LLM A-E6 in both runs (A-I2 met: "the system can be used to acquire data on the consumption of energy in distribution networks", p. 1).
- 47 and 149: same code A-E3, different ground: H1 A-I2 not met; LLM mechanism_only (47 run 1 also A-I2 not met).

## Pattern to watch
The LLM reads A-I2 more loosely than H1 for whole-grid surveys (generation to consumption) in which smart meters are one component: it agrees on 186, 204 and 209 (run 2) but calls A-I2 met on 73, 149, 198, 209 (run 1). Rule (a) for A-I3 ("privacy named in the stated aim") also lets "security and privacy" in an aim sentence meet A-I3 even when the paper's privacy content is thin (73, 209). The prompt is frozen, so these are reconciled case by case; if the pattern holds over the next batches, it is reported as a limitation of the LLM check (and, if needed, a v3 for a re-run).

## Quote check
200 quotes: 196 on page, 1 other page, 3 not found; all four checked and genuine.
- 204 (run 1, A-I1 p. 14 and A-I2 p. 4): the quoted sentences are split by the running footer "VOLUME 14, 2026" in the text layer.
- 198 (run 2, A-I3 p. 3): "The systems lack adequate provision for data privacy." is a Table 1 cell broken across lines in the text layer.
- 60 (run 1, A-I4): journal line cited on p. 1; the text layer has it on p. 1 in lower case and on p. 2 (running header) in the quoted capitalisation. Correct page, harmless.
