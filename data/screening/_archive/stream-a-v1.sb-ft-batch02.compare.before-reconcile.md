# Snowball full-text batch 02: H1 vs LLM (screen-A-ft-v2, frozen)

Prompt SHA-256 `305da17b…04b5`; model `claude-opus-5-5`; Claude Code 2.1.325; two runs, 14.11.2026. Logs: `llm/stream-a-v1.sb-ft-batch02.screen-A-ft-v2.run1.jsonl` / `.run2.jsonl`.
20 papers run. No retries, no schema errors, all quotes on the page. Flag `text_incomplete`: 1909 (run 1, table contents not extracted) and 2093 (run 2); neither changes a decision.

H1 (20): 5 include, 15 exclude. Decision agreement with H1: run 1 16/20, run 2 17/20; run 1 vs run 2 decisions 18/20 (differ on 1962 and 2126).

## Disagreements
- **1939** Eskandarnia, Al-Ammal, Ksantini, "Deep Learning Techniques for Smart Meter Data Analytics: A Review" (SN Computer Science 2022), seed Eskandarnia22a: H1 include (stream C; "supplementary clustering experiment"); LLM A-E1 route none in both runs, both calling A-I2 and A-I3 met ("Security and Privacy", p. 9; privacy and security column in Table 3). Facts from the text: the abstract announces the experiment ("an experiment is conducted comparing various classical load profiling techniques with deep clustering"), and it has its own section "Load Profiling Experimental Results" (pp. 10–11 of 16). Both conditions of the mixed-paper rule hold literally. Run 1 calls it borderline because the experiment illustrates the review. Precedents for A-E1 on own experiments: 1635 (batch 09), 1604.
- **2174** review of NILM-enabled demand response (RSER 2026): H1 include (stream C; §4.2 and §6.2 on privacy protection); LLM A-E3 with `nilm_only` and `mechanism_only` in both runs. Facts from the text: §4 "The trade-off between centralized control and privacy protection" and §4.2 (pp. 10–11) compare local deployment, edge computing, federated learning and differential privacy; the risk appears only in motivating sentences ("raising concerns about potential privacy breaches", p. 6; "increases the risk of user information exposure", p. 10); no passage explains what an adversary can infer. Appliance inference is treated as a capability for demand response (p. 4). H1's note says the same.
- **1962** "Enhancing privacy in smart energy systems" (e+i 2019): H1 include; run 1 unclear (A-I1: mostly a summary of the authors' own centre's results), run 2 include. The paper states that it presents no original research (p. 2); privacy of smart-meter load profiles is the stated subject.
- **2126** "A Comprehensive Review on Smart Grids: Challenges and Opportunities" (Sensors 2021): H1 A-E3; run 1 unclear (A-I2), run 2 include (borderline; privacy preserving is one class in Table 6). Review of 94 smart-grid articles; AMI is one application subclass.

## Code differs (decision agrees)
- **2205** big-data management review (Power Electronics and Drives 2019): H1 A-E3; LLM A-E1 route none in both runs. The abstract states "The contribution of this paper is building a recommender system" (p. 1); developed in §4.4 with Fig. 7. A-I1 comes before A-I2 in the decision order.
- **1938** data-driven management of distribution networks (Energy Reports 2025): H1 A-E3; LLM A-E1 route none in both runs. The framework is in the title, announced in the introduction (p. 2) and developed in §10 (p. 14). H1's own A-I1 evidence names the "conceptual system-of-systems framework".
- **1922** value conflicts in the smart electricity grid (RSER 2019): H1 A-E3; LLM A-E1 route none in both runs. The three prioritisation factors are named in the abstract and the contributions (p. 9) and developed in §§5.2–5.4; the literature part is a topic-model analysis of 24,799 publications. Privacy has a subsection (§4.2.1).
- **1852, 1908, 1909, 2248**: H1 A-E3 (smart-meter data do not structure the review); LLM A-E6 in both runs (A-I2 met, privacy in passing). Known pattern; H1's A-I2 judgment stands.

## Reconciliation (H1)

Open: 1939, 2174; codes of 2205, 1938, 1922. Kept as H1 decided: 1962 (include), 2126 (A-E3).
