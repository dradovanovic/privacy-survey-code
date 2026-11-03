# Full-text batch 03: H1 vs LLM (screen-A-ft-v2, frozen)

Prompt SHA-256 `305da17b…04b5`; model `claude-opus-5-5`; two runs, 01.11.2026, plus n 572 on 02.11.2026 (replacement PDF with a text layer). Logs: `llm/stream-a-v1.ft-batch03.screen-A-ft-v2.run1.jsonl` / `.run2.jsonl`.
21 of 22 papers run; **n 505 not run** (scanned PDF without a text layer, OCR skipped; H1 A-E4 under the edited-chapter rule stands on its own). No retries, no schema errors.

H1 (22): 4 include (435, 453, 532, 566), 18 exclude. Decision agreement with H1 (21 run): run 1 15/21, run 2 15/21; run 1 vs run 2 19/21 (465, 566 differ).

## Disagreements

### A. Domain (A-I2): H1 exclude A-E3, LLM include in both runs
Prompt wording: "smart meters, AMI, smart-meter data, or smart-grid consumer-side data are **a** principal subject (not one example among many IoT domains)".

| n | Paper | LLM's evidence | Comment |
|---|---|---|---|
| 515 | Retail competition survey (Applied Energy 2014) | Smart metering is a keyword, a highlight and its own §4; privacy is a stated aim and §5 (p. 16 ff.) covers inference of habits from 15–60 min data, privacy-invasion classes (Table 9). | Strongest case for include: the whole privacy part is about smart-meter data. |
| 572 | Authentication and privacy preservation in SG (Wiley S&P 2019) | §4.2 p. 6: full paragraph on what 30-min/hourly data reveal (activities, appliances, surveillance, profiling); §6 privacy-preservation schemes are almost all SM data aggregation (EPPA, PAS, PDA…). | Privacy half close to 532 (included); authentication half is grid-wide (HAN/NAN/WAN). |
| 528 | Cyber–physical–social distribution systems (Proc. IEEE 2023) | §V.B "Data Privacy and Pricing" (p. 20 ff.) on sociodemographic inference from SM data. | SM is a recurring component of a broad review; privacy is one subsection. |
| 527 | Authentication, access control in SG (Energies 2015) | §2.2.6 Obj-7 "Confidentiality and Privacy", privacy column in Table 3; tracing of consumption patterns mentioned. | Authentication across the whole grid; privacy thin. |

### B. Other disagreements
- **453** Emerging PETs in energy systems (EICC 2024): H1 include; LLM exclude A-E1 route none in both runs. Mixed-paper rule: contribution 3 (p. 2) and §4 with Tables 1–3 are the authors' own mapping of four PETs (HE, SMPC, DP, FL) onto seven grid use cases; "landscape paper", few citations. Compare 400 and 586 (own framework → A-E1).
- **566** Privacy solutions for control in smart metering (CRITIS 2016, LNCS): H1 include; run 1 exclude A-E3 mechanism_only (inference only in motivating sentences, p. 188), run 2 include (privacy is the main theme; mechanism rule targets single-technology surveys).
- **465** Cloud-based SG security (ICREPQ'16): H1 exclude A-E3; run 1 exclude A-E3, run 2 include (calls itself borderline).

## Code differs (decision agrees)
485, 495, 575: H1 A-E3 (A-I2), LLM A-E6/A-E3 mechanism_only. 516, 550: H1 A-E1 (A-I1), LLM A-E6/A-E3. H1 codes kept: the criterion H1 judged not met comes first in the decision order.

## Quote check
482 run 2 A-I3: heading "5.3.4. Security and privacy" found on p. 12, cited p. 11 (page boundary). 527 run 2 A-I3: `not_found`, the quote joins table cells of Table 3 and is cut off; the text is in the paper. Neither is decision-relevant.

## Reconciliation (H1, 02.11.2026)

| n | H1 blind | Final | Reason |
|---|---|---|---|
| 453 | include | **exclude A-E1** (route none) | Own PET-to-use-case mapping (§4, Tables 1–3) is the main contribution; as 400, 586. |
| 515 | exclude A-E3 | **include** | Smart metering has its own §4; the privacy part (§5) is about smart-meter data. |
| 572 | exclude A-E3 | **include** | Privacy half about smart-meter data (§4.2 p. 6 inference; §6 aggregation schemes); as 532. |
| 566 | include | **include** | Privacy is the whole topic; mechanism_only not applied to a smart-metering privacy-solutions survey. |
| 465 | exclude A-E3 | **exclude A-E3** | Cloud computing for SG broadly; run 1 agrees. |
| 527, 528 | exclude A-E3 | **exclude A-E3** | Smart meters one component among many; privacy one subsection or objective. |

A-I2 test used from here on: met when smart-meter data structure the review (own section, or the whole privacy part is about them), not when they are only recurring examples.

Batch 03 closed: 5 include (435, 515, 532, 566, 572), 17 exclude (8 A-E3, 7 A-E1, 2 A-E4).

Update 02.11.2026 (H1 decision in batch 04: A-I1 has no depth threshold, A-E1 only for primary studies): 516 → **exclude A-E6** (privacy in passing, as the LLM), 550 → **exclude A-E3** (H1's A-I2 not met). Batch 03 now: 5 include, 17 exclude (9 A-E3, 5 A-E1, 2 A-E4, 1 A-E6).
