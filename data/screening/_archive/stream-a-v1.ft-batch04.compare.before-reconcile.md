# Full-text batch 04: H1 vs LLM (screen-A-ft-v2, frozen)

Prompt SHA-256 `305da17b…04b5`; model `claude-opus-5-5`; two runs, 02.11.2026. Logs: `llm/stream-a-v1.ft-batch04.screen-A-ft-v2.run1.jsonl` / `.run2.jsonl`.
**19 of 20 papers run: n 607 (`ieee:9461839`, Portuguese) is missing from both run files** although its text was extracted (12 pages, 10,814 words); it needs a resume run. One retry (601, run 2), no schema errors.

H1 (20): 9 include, 11 exclude (H1 changed 642, 721, 835 before the run, on Claude's remarks, not on LLM output). Decision agreement with H1 (19 run): run 1 13/19, run 2 13/19; run 1 vs run 2 19/19.

## Disagreements

### A. A-I1 depth threshold: H1 exclude A-E1 ("descriptive overview, not a synthesis"), LLM include in both runs
- **642** Attacks and countermeasures in SG metering networks (ICCMC 2021): LLM: self-described survey with no own scheme; §V "Threats to security and privacy" (p. 4) with inference of day-to-day life from intercepted readings.
- **646** Comparative work on data security and privacy (ICCS 2018): LLM: survey plus comparison table of existing schemes; privacy in the title and §1.3 (p. 2) explains occupancy/activity inference.
Also affected (code only): **703** H1 A-E1, LLM A-E6 in both runs (A-I1 met; privacy one paragraph, pp. 8–9). Earlier: 516, 550 (batch 03) have the same pattern.
Issue: A-E1 is defined as a primary study (own attack, mechanism, framework or analysis). The criteria have no depth threshold for a review; "weak evidence is never a reason to exclude". H1 decision needed (see thread).

### B. Mechanism-survey rule: H1 include, LLM exclude A-E3 mechanism_only in both runs
- **693** Privacy-preserving aggregation and authentication (Appl. Sci. 2017, Perspective): §3 (pp. 6–9) catalogues HE, signature and anonymization schemes; inference only in one motivating sentence, p. 2: "measurement information can be used by adversaries for inference of users’ behavioral patterns". The p. 6 passive-attack paragraph is about confidentiality. Unlike 566, this is an encryption survey, which the rule names explicitly.
- **778** ML for SG cybersecurity, SLR (ICICNIS 2025): §II.D "Privacy Preservation in Smart Grids" (p. 4) lists HE, DP, FL, Paillier, blockchain; one sentence on "inferential linkage attacks and behavioural fingerprinting". Both runs also call A-I2 borderline (mostly FDI, SCADA, substations).

### C. A-I4 unclear in both runs (expected)
- **721**: preprint shows no venue; unfilled journal-template Declarations block. A-I4 from the record's DOI (Taylor & Francis), as 236.
- **835**: text calls itself a book chapter, no publisher shown. H1 A-E4 under the edited-chapter rule.

## Agree, but checked against the A-I2 test (H1: compare after the run)
- **718** AI/ML for smart grids (ECM: X 2025): both runs include but call it borderline: A-I3 met only via the "Privacy Posture" column (Table 6); run 2 calls A-I2 borderline (whole grid). Under the batch 03 A-I2 test smart-meter data are recurring examples here, not a structuring element.
- **808** SG data analysis mapping study (TII 2020): both runs include; privacy is taxonomy category C8 with a re-identification example (p. 6); "“Smart Meter data” plays a major role both in C1 and C2 categories, being the main source of data for analysis" (p. 5).

## Code differs (decision agrees)
- **601**: H1 A-E3, run 1 A-E3, run 2 A-E6 → keep A-E3.
- **703**: see A.

## Quote check
808 run 1 A-I2 and 820 A-I3 (both runs) `not_found`: genuine; curly quotes in 808, a column break inside the 820 sentence (p. 3). 828 run 1 A-I3 heading on p. 13, cited p. 12 (page boundary); 828 run 1 flags text_incomplete (conclusion cut), not decision-relevant.

## Reconciliation (H1)
Open: 642, 646, 703, 693, 778, 718, 808, 721, 835; 607 resume run.
