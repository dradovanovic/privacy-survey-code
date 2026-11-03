# Full-text batch 02: H1 vs LLM (screen-A-ft-v2, frozen)

Prompt SHA-256 `305da17b…04b5`; model `claude-opus-5-5`; two runs, 01.11.2026. Logs: `llm/stream-a-v1.ft-batch02.screen-A-ft-v2.run1.jsonl` / `.run2.jsonl`.
**Only 19 of 20 papers were run: n 368 (`openalex:W3179706379`) is missing from both run files**, although its text was extracted (16 pages, 13,302 words). It needs a resume run (the runner skips papers already done).
No retries, no schema errors in the 38 calls. H1 decided blind (01.11.2026); codes put in decision order before the run (282, 305, 384, 389).

H1 (all 20): 9 include, 11 exclude. Decision agreement with H1 (19 run): run 1 11/19, run 2 12/19.

## Disagreements

### A. Mechanism-survey rule (set after n 14; applied to n 218): H1 include, LLM exclude A-E3 mechanism_only in both runs
| n | Paper | LLM's evidence |
|---|---|---|
| 232 | Blockchain for SG management (Energies) | §2.5 and §4.3.5 "Security and Privacy" list schemes (PETra, private aggregation); the attacks explained are security attacks (jabbing, puppet, DoS); no passage on what can be inferred. |
| 321 | When blockchain meets smart grids | §5.3 "Blockchain for power grid privacy" catalogues signatures, pseudonyms, encryption; the open-issues paragraph (p. 17) lists privacy types and ledger transparency, but nothing on inference about households. |
| 338 | Securing SG with blockchain (ITC 2023) | Only one sentence on what AMI data reveals, p. 2: "any breach in such data can reveal a person’s identity, location, generation pattern, and lifestyle [13]"; §IV.A describes schemes (CS2V, ring signatures). Same pattern as n 14. |
| 241 | FL for energy-theft detection | Risks only in single sentences: p. 4 "the potential for the CS to infer user behavior from received parameters poses a privacy risk", p. 5 membership inference / model inversion in one line. A-I4 also unclear (no venue in the text). |

H1's evidence for all four cites privacy sections and mechanisms; the question is the paragraph threshold H1 set for n 14 ("at least a paragraph that explains what can be inferred or how an attack works"). For consistency with 14 and 218, each needs such a paragraph to stay included.

### B. Other disagreements
- **400** Data sharing and privacy in electricity access (Proc. IEEE): H1 include; LLM exclude A-E1 (both runs) under the mixed-paper rule, p. 2: "we synthesize literature … and draw from industry and institutional reports, anecdotes, and analogs … to construct a framework", plus the authors' own workshop evidence; run 2 calls it borderline. Compare n 586 (own conceptual analysis → A-E1). H1 noted "the workshop evidence is supplementary".
- **236** Reconciling privacy and utility management (ETT): H1 include; LLM unclear (both runs) only because A-I4 cannot be judged: the PDF's text shows no journal name, footer or dates. Record: DOI 10.1002/ett.2708, Transactions on Emerging Telecommunications Technologies (Wiley). Everything else met.
- **305** Cyber security challenges in smart grids (2011): H1 exclude A-E3; LLM include (run 1) / unclear (run 2, A-I4: only an IEEE Xplore download footer). LLM counts A-I2 as met (consumer side, smart meters, p. 4) and A-I3 via the dedicated "E. Consumers' privacy" section. Same A-I2 pattern as batch 01 (whole-grid surveys).
- **384** Fog-based SCADA security: H1 exclude A-E3; LLM include (run 1, "borderline") / exclude A-E3 mechanism_only (run 2). Both runs call A-I2 met. Decision-relevant only if H1 changes A-I2.

## Code differs (decision agrees)
- **246** Privacy preserving for big data in power systems: H1 A-E3 (A-I2 not met); LLM A-E1 route C (both runs): own "framework of privacy preserving approaches" named in the abstract and developed in §V (Figure 3); both runs call it borderline because the section is short.
- **348** SG properties and challenges: H1 A-E3; LLM A-E6 (A-I2 unclear/met, one SM/AMI subsection). Same case as n 198 → keep A-E3.

## Quote check
All quotes not on the cited page are genuine: 348's heading "4.3.3 Smart meters and advanced metering infrastructure (AMI)" is on p. 6; 241's FVC sentence is cut by the column layout on p. 3; 241's ICASET reference sits on p. 8, not p. 7. Empty quotes only for A-I4 `unclear` (236, 241), as the prompt allows.

## Reconciliation (H1, 01.11.2026)

| n | H1 blind | Final | Reason |
|---|---|---|---|
| 232 | include | **exclude A-E3** (mechanism_only) | Schemes and security attacks only; data privacy only as an open challenge (Table 1). Kept as a gap example for the motivation. |
| 321 | include | **exclude A-E3** (mechanism_only) | Strict reading: the p. 17 paragraph explains access to ledger data, not inference; consistent with 14, 218, 338. |
| 338 | include | **exclude A-E3** (mechanism_only) | One risk sentence (p. 2). |
| 241 | include | **exclude A-E3** (mechanism_only) | Risks only in single sentences (pp. 4–5). |
| 400 | include | **exclude A-E1** | Own framework from reports, anecdotes and workshop evidence (p. 2, Section III, Section V); as 586. |
| 236 | include | **include** | A-I4 from the record's DOI (Wiley ETT); the PDF text shows no venue. |
| 305, 384 | exclude A-E3 | **exclude A-E3** | Whole-grid / SCADA security surveys; consistent with 73, 149, 209. |
| 246, 348 | exclude A-E3 | **exclude A-E3** | H1 code kept (348 as 198). |

Gap examples for the motivation (privacy only as mechanisms or an open challenge, no inference analysis), noted in the final reasons: 14 (pilot), 218 (batch 01), 232, 241, 321, 338 (batch 02). Before citing them: CLAUDE.md rule 2 allows citing only records of the study corpus; H1 decides whether excluded records may be cited as background.

n 368 (resume run, 01.11.2026): LLM exclude A-E6 in both runs, H1 exclude A-E3 → final A-E3 (as 198, 348). Batch 02 closed: 4 include (236, 240, 274, 344), 16 exclude (13 A-E3, 3 A-E1).
