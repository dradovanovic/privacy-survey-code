# Full-text batch 09: H1 vs LLM (screen-A-ft-v2, frozen)

Prompt SHA-256 `305da17b…04b5`; model `claude-opus-5-5`; two runs, 07.11.2026. Logs: `llm/stream-a-v1.ft-batch09.screen-A-ft-v2.run1.jsonl` / `.run2.jsonl`.
22 papers run. No retries, no schema errors. Quotes not on the page: 1654 A-I3 in both runs ("Maintaining Privacy" heading, p. 5): the checker did not match it, although Claude found the heading on p. 5 of the extracted text; the A-I3 judgments differ for other reasons.

H1 (22): 7 include, 15 exclude (H1 changed 1623, 1628, 1629, 1641, 1643 and 1686 before the run, on Claude's remarks, not on LLM output). Decision agreement with H1: run 1 17/22, run 2 15/22; run 1 vs run 2 decisions 18/22 (differ on 1561, 1635, 1654, 1657).

## Disagreements
- **1583** OTP authentication in smart metering (CISTEM 2022): H1 A-E3 (mechanism-focused); LLM include in both runs. Section III "Privacy issues of the smart metering system" (p. 2) explains what meter data reveal (habits, appliances, occupancy, targeted marketing, burglary); that meets the mechanism rule (at least a paragraph on inference; cf. 1308).
- **1663** AMI security and key-management survey (IC3I 2024): H1 A-E3 mechanism_only; LLM include in both runs. Page 3 has a paragraph "Ensuring the Security of End User Data" on what consumption data reveal (number of residents, presence, appliances, alarm systems, medical emergencies). Claude's earlier comment ("privacy only named, pp. 1, 6–7") missed this paragraph.
- **1610** V2G privacy survey (Computer Communications 2016): H1 A-E3; LLM include in both runs (privacy is the topic, attack and inference sections; both runs call A-I2 borderline: EV identity and location data, not smart-meter data).
- **1629** big-data challenges for DER control (EEEIC 2015): H1 A-E3; LLM include in both runs (survey; smart-meter privacy is one of four aims, Section IV.C, p. 4). Both runs call A-I2 borderline.
- **1657** 5G IoT for demand response (Applied Energy 2019): H1 include; run 1 A-E3 mechanism_only, run 2 include with a note that the privacy content is thin. Section 2.3 covers PKI, encryption and isolated networks; nothing on what can be inferred.
- **1635** privacy-preserving techniques in smart metering (SBSeg 2016): H1 A-E1; run 1 A-E1, run 2 include (borderline). Own experiments (Section 4, p. 9) and the authors' own noise-addition scheme (Section 3.1).
- **1654** smart-grid attacks review (IC2E3 2023): H1 A-E3; run 1 A-E6, run 2 include. "Maintaining Privacy" (p. 5) is a list of mechanisms; no inference paragraph.
- **1561** socio-economic acceptability review (J. Cleaner Production 2016): H1 A-E3; run 1 A-E3, run 2 unclear (A-I2). Privacy is a comparison column over the whole smart grid.

## Code differs (decision agrees)
- **1673** Frisby & Trotta (CommLaw Conspectus 2011): H1 A-E3; LLM A-E1 in both runs (own normative legal analysis, Section IV and the five principles, p. 33); run 1 also A-I4 unclear. Student-edited law review.
- **1628** DT–ML for smart buildings (CMES 2025): H1 A-E3; run 1 A-E6, run 2 A-E3 mechanism_only. Both runs find A-I2 met.

## Reconciliation (H1, 09.11.2026)

| n | H1 blind | Final | Reason |
|---|---|---|---|
| 1583 | exclude A-E3 | **include** | Inference section III (p. 2); mechanism rule met. |
| 1663 | exclude A-E3 | **include** | Inference paragraph p. 3; mechanism rule met. |
| 1657 | include | **exclude A-E6** | Privacy sections cover security only. |
| 1673 | exclude A-E3 | **exclude A-E4** | Student-edited law review; A-I4 first. |
| 1610 | exclude A-E3 | **exclude A-E3** | V2G/EV data, not smart-meter data (H1 A-I2 judgment). |
| 1629 | exclude A-E3 | **exclude A-E3** | Smart meters one of four topics (rule 02.11.2026). |
| 1635 | exclude A-E1 | **exclude A-E1** (route none) | Own experiments and own noise-addition scheme. |
| 1654 | exclude A-E3 | **exclude A-E3** | Whole smart grid; privacy subsection lists mechanisms only. |
| 1561 | exclude A-E3 | **exclude A-E3** | Privacy column over the whole smart grid. |
| 1628 | exclude A-E3 | **exclude A-E3** | Smart buildings and DT–ML; H1 A-I2 judgment kept. |

Final decisions agree with both LLM runs except 1610 and 1629 (LLM include, A-I2 borderline in both runs; H1 A-I2 judgment), and agree with one run for 1635, 1654, 1657 and 1561; 1628 and 1673 differ in code only.

Batch 09 closed: 8 include (1554, 1557, 1583, 1620, 1623, 1634, 1663, 1684), 14 exclude (7 A-E3: 1561, 1568, 1610, 1617, 1628, 1629, 1654; 3 A-E4: 1643, 1673, 1686; 2 A-E1: 1625, 1635; 2 A-E6: 1641, 1657).
