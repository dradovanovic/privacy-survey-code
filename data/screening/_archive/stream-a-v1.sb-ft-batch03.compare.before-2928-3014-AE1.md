# Snowball full-text batch 03: H1 vs LLM (screen-A-ft-v2, frozen)

Prompt SHA-256 `305da17b…04b5`; model `claude-opus-5-5`; Claude Code 2.1.325; two runs, 16.11.2026. Logs: `llm/stream-a-v1.sb-ft-batch03.screen-A-ft-v2.run1.jsonl` / `.run2.jsonl`.
19 of 20 papers run. **2949** (Uribe-Pérez et al., Applied Sciences 2016) has no result in either run although its text was extracted (24 pages, 11,110 words, no low-text pages); it has to be run separately (`stream-a-v1.sb-ft-batch03-2949.input.csv`). No retries, no schema errors. Quotes not on the page: 2901 A-I1 (run 1, not found), 3014 A-I3 (run 2, on p. 41 instead of p. 40); neither carries a decision.

H1 (20): 20 exclude. Decision agreement with H1 on the 19 papers run: run 1 16/19, run 2 16/19; run 1 vs run 2 decisions 19/19, codes 18/19 (2499).

## Disagreements
- **2630** smart meter data and occupant behaviour (Energies 2021): H1 A-E6 (privacy "dedicated but brief", no systematic attack or PET synthesis); LLM include in both runs. Facts from the text: §1.4 "Privacy Concerns" (pp. 4–5) has about 850 words in several paragraphs: what meter data reveal (appliance brands and malfunctions, expensive appliances, absence of occupants, real-time monitoring, surveillance within the family), two counter-algorithms, and the legal side (ECHR, the Dutch rollout, U.S. v. Miller, Kyllo v. U.S.). Privacy appears on 10 of 23 pages and as a variable of adoption (pp. 16–18). The criterion asks for a dedicated section beyond one paragraph, not for a systematic synthesis; 1695 was included on a section of similar length (§3.1, pp. 6–7).
- **2636** EU laws and AI adoption in smart grids (Energies 2025): H1 A-E3 (grid-wide regulatory review; smart-meter data one application context); LLM include in both runs (§3.1.1 "Data Privacy and GDPR Compliance", p. 5, on smart-meter readings that reveal household patterns; §3.1.4 ePrivacy; "Privacy Protection" column in Table 3). Privacy is substantive for both; the difference is A-I2 only.
- **2706** means and methods of collecting indicators for energy supply companies (Advances in Cyber-Physical Systems 2024): H1 A-E6; LLM include in both runs "on a literal reading", both calling the treatment shallow. Facts from the text: section G "Security and data privacy" (p. 4) has five short paragraphs on cybersecurity strategies, encryption, GDPR compliance and consumer confidence; nothing on what can be inferred. Precedents: 1657 and 1811 (sections that cover security only are A-E6).

## Code differs (decision agrees)
- **2834, 2894, 2930**: H1 A-E6; LLM A-E2 in both runs. The word privacy does not appear in any of the three texts; "no privacy component at all" is A-E2 (as 1724 in batch 01).
- **2928** smart metering policy review (2016): H1 A-E6; LLM A-E1 route none in both runs. Two of the three stated objectives (p. 2) are the authors' own proposals (liberalised "energy spots", communication standards), developed in §3. A-I1 comes before A-I3.
- **3014** blockchain-based transactive energy review: H1 A-E3; LLM A-E1 route none in both runs (flag `mechanism_only`). An own generalised framework is named in the title and abstract (p. 1), listed as contribution 1 (p. 41) and developed in §6 with Fig. 29. A-I1 comes before A-I2.
- **2375, 2791, 2901, 2903, 2912**: H1 A-E3; LLM A-E6 in both runs. Known pattern; H1's A-I2 judgment stands. **2499**: H1 A-E3; run 1 A-E3, run 2 A-E6.

## Reconciliation (H1)

H1 decisions, 16.11.2026:

| n | H1 before | LLM | Final | Reason |
|---|---|---|---|---|
| 2630 | exclude A-E6 | include / include | **include** (stream B) | §1.4 "Privacy Concerns" (pp. 4–5) is a dedicated section beyond one paragraph; A-I3 met. |
| 2636 | exclude A-E3 | include / include | **include** (stream C) | A-I2 judged met: smart-meter data are the object of the data-protection analysis (§3.1.1, §3.1.4); privacy substantive (Table 3). |
| 2706 | exclude A-E6 | include / include | exclude A-E6 | Section G covers encryption and GDPR compliance only; nothing on inference (as 1657, 1811). |
| 2834 | exclude A-E6 | A-E2 / A-E2 | exclude A-E2 | No privacy term in the text. |
| 2894 | exclude A-E6 | A-E2 / A-E2 | exclude A-E2 | No privacy term in the text. |
| 2930 | exclude A-E6 | A-E2 / A-E2 | exclude A-E2 | No privacy term in the text. |

2375, 2499, 2791, 2901, 2903, 2912: H1's A-E3 stands (known pattern). All other papers agree.

Note on consistency: with 2636 H1 judges A-I2 met for a broad smart-grid review. The nearest comparable exclusion is 2126 (batch 02, A-E3, one LLM run include).

Still open: 2928 and 3014 (A-E1 proposed instead of A-E6 / A-E3; decision exclude either way); 2949 not yet run by the LLM (H1: exclude A-E6).

State of batch 03 after this step: 2 include (2630, 2636), 18 exclude.
