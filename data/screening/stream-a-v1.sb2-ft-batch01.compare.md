# Snowball round 2, full-text batch 01: H1 vs LLM (screen-A-ft-v2, frozen)

Prompt SHA-256 `305da17b…04b5`; model `claude-opus-5-5`; Claude Code 2.1.325; two runs, 16.11.2026. Logs: `llm/stream-a-v1.sb2-ft-batch01.screen-A-ft-v2.run1.jsonl` / `.run2.jsonl`.
10 of 10 papers run; all texts extracted without low-text pages. One retry (3085, run 2), no schema errors. Quote not on the page: 3075 A-I1 (run 2, not found); it carries no decision.

H1 (10): 10 exclude. Decision agreement with H1: run 1 10/10, run 2 10/10; run 1 vs run 2 decisions 10/10, codes 10/10.

## Code differs (decision agrees)
- **3062** IoT-enabled smart grid via SM (FGCS 2019): H1 A-E3; LLM A-E6 in both runs. The paper states its aim as a review of smart meters for power quality and reliability monitoring (p. 2), so smart meters are the principal subject and A-I2 is met; this is not the broad smart-grid pattern. Privacy: a few sentences in subsection 3.4.0.7 "Security" (p. 6: consumer data may reveal activities, devices in use, vacancy); no section, no comparison column.
- **3098** Blockchain-IoT enabled smart metering system (IEIT 2023): H1 A-E6; LLM A-E1 route C in both runs (flag `mechanism_only`). The abstract names the authors' own system as a contribution and it is developed in §§III–IV; the review covers six papers (§II). Mixed-paper rule; A-I1 comes before A-I3 (as 2928, 3014).
- **3156** review of modelling techniques for theft detection (RSER 2018): H1 A-E6; LLM A-E2 in both runs. Checked in the text: privacy occurs only in two reference titles (pp. 17–18); confidentiality and data protection do not occur.
- **3164** smart energy meters in renewable-energy-based networks (Eng. Proc. 2022): H1 A-E6; LLM A-E2 in both runs. Checked in the text: privacy, confidentiality and data protection do not occur; security appears once as an application (p. 3).
- **3168** smart meter: applications, security issues and challenges (ICOCI 2015): H1 A-E6; LLM A-E1 route none in both runs, with A-I3 judged met. Facts from the text: "Privacy (C5)" is one of five clusters of the attack classification (Table 2, pp. 4–5) with its own paragraph "Attacks on privacy" (p. 6, four sentences, no citations). A taxonomy branch meets A-I3 by the criteria card, so A-E6 does not fit. The classification is introduced as the authors' own ("we highlight additional attacks ... and we define five clusters", p. 4) and is the main section; the review of existing work is one paragraph ("Related works", p. 4). A-I1 is therefore the failing criterion.
- **3081, 3085**: H1 A-E3; LLM A-E6 (3081) and A-E2 (3085) in both runs. Known pattern (broad smart-grid overviews); H1's A-I2 judgment stands.

## Agreement
3061 (A-E3), 3075 (A-E6; run 2 notes that a stricter reading of the mixed-paper rule could give A-E1 because of the authors' experiments on the CER data), 3173 (A-E6).

## Reconciliation (H1)

H1 decisions, 16.11.2026: the five codes are changed as in both LLM runs. 3062 A-E3 → A-E6; 3098 A-E6 → A-E1; 3156 A-E6 → A-E2; 3164 A-E6 → A-E2; 3168 A-E6 → A-E1. 3081 and 3085 keep A-E3.

Batch closed on 16.11.2026: 0 include, 10 exclude (3 A-E3, 3 A-E6, 2 A-E1, 2 A-E2). Round 2 adds no study.
