# Snowball full-text batch 01: H1 vs LLM (screen-A-ft-v2, frozen)

Prompt SHA-256 `305da17b…04b5`; model `claude-opus-5-5`; Claude Code 2.1.325; two runs, 14.11.2026. Logs: `llm/stream-a-v1.sb-ft-batch01.screen-A-ft-v2.run1.jsonl` / `.run2.jsonl`.
20 papers run. No retries, no schema errors. Quotes not found on the page by the checker: 1690 A-I3 (both runs), 1695 A-I3 (run 1), 1702 A-I1 (both runs), 1790 A-I4 (run 1) and A-I5 (run 2); 1811 A-I5 on another page (run 1). None of them carries a disagreement except 1690, where the heading "2) Ensuring Privacy" is on p. 11 of the extracted text (hyphenation in the quote).

H1 (20): 5 include, 15 exclude. Decision agreement with H1: run 1 18/20, run 2 18/20; run 1 vs run 2 decisions 20/20, codes 20/20.

## Disagreements
- **1690** Komninos, Philippou, Pitsillides, "Survey in Smart Grid and Smart Home Security" (IEEE COMST 2014), seed Komninos14a: H1 A-E1 route none (own scenario-based threat analysis and impact evaluation, §III, pp. 5–11); LLM include in both runs (the scenario-based threat categorisation is read as the taxonomy that organises the review; "2) Ensuring Privacy", p. 11, and scenario SH_1 on what 15-minute data reveal). Facts from the text: the abstract and the three key points (p. 2) name first the scenarios, threat classification and impact evaluation (§III), second the literature review of countermeasures (§IV, pp. 11–17), third open issues. The paper calls itself a survey (p. 2). Privacy: 9 mentions on p. 11, further on pp. 12, 13, 17, 19.
- **1811** "Intelligent control and monitoring in smart metering systems: a systematic review" (Next Research 2026): H1 include (privacy in RQ4, §§3.4.3, 4.4.3, 9.5); LLM A-E6 in both runs. Facts from the text: privacy is one of five items in RQ4 (p. 3); §3.4.3 "Cybersecurity and privacy" (p. 9) and §9.5 (p. 20) list security risks; federated learning is described as a mechanism (pp. 10–11, 13, 21); no passage explains what can be inferred from consumption data; no privacy column in a comparison table. Precedent: 1657 (batch 09) and 1282, 1324 were set to A-E6 on the same grounds.

## Code differs (decision agrees)
- **1691, 1699, 1708, 1713, 1714, 1721, 1742, 1790, 1837**: H1 A-E3 (broad smart-grid survey, smart-meter data do not structure the review); LLM A-E6 in both runs (A-I2 met, privacy in passing). Run 2 calls A-I2 unclear for 1742. Same pattern as in the first round; H1's A-I2 judgment (rule of 02.11.2026) stands.
- **1710**: H1 A-E3; LLM A-E2 in both runs (A-I2 met; the word privacy does not appear). H1's A-I2 judgment stands.
- **1724** "Smart Meters in Smart Grid: An Overview" (GreenTech 2013): H1 A-E6; LLM A-E2 in both runs. A-I2 is met for both. The word privacy does not appear in the text; by the decision order "no privacy component at all" is A-E2, A-E6 needs privacy to be present.

## Reconciliation (H1, 14.11.2026)

| n | H1 blind | Final | Reason |
|---|---|---|---|
| 1690 | exclude A-E1 | **include** | §III is the threat taxonomy that organises the review; privacy subsection pp. 11–13, inference scenario SH_1, p. 6. Seed Komninos14a stays a seed. |
| 1811 | include | **exclude A-E6** | Privacy sections list security risks and describe federated learning as a mechanism; nothing on inference. |
| 1724 | exclude A-E6 | **exclude A-E2** | The word privacy does not appear; no privacy component at all. |

All other rows: H1's blind decision and code are final (11 code differences A-E3 vs A-E6/A-E2 rest on H1's A-I2 judgment).

Final batch 01: 5 include (1690, 1695, 1754, 1758, 1785), 15 exclude (10 A-E3, 4 A-E6, 1 A-E2).
