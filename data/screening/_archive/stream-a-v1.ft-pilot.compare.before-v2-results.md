# Full-text pilot: H1 vs LLM (screen-A-ft-v1 draft)

Prompt `code/prompts/screen-A-ft-v1.md`, SHA-256 `abf8d733…3eef`; model `claude-opus-5-5`; two runs, 28.10.2026.
Logs: `llm/stream-a-v1.ft-pilot.screen-A-ft-v1.run1.jsonl` and `.run2.jsonl`. Text: `code/data/fulltext/text/` (pdftotext 4.00, Xpdf), manifest there.
All 22 calls ok, no retries, no schema errors. Whole paper sent each time (about 56k tokens for the largest checked).
H1 decided blind (27–28.10.2026) before the LLM ran.

## Decisions

| n | Paper (short) | H1 | LLM run 1 | LLM run 2 | Status |
|---|---|---|---|---|---|
| 3 | ML carbon-intensity estimation review | exclude A-E6 | exclude A-E6 | exclude A-E6 | agree |
| 14 | Blockchain in Smart Grids (Sensors 2019) | include | include | exclude A-E3, mechanism_only | **disagree (run 2)** |
| 15 | AI and blockchain for smart grid (SETA 2023) | exclude A-E1 | exclude A-E3, mechanism_only | exclude A-E3, mechanism_only | agree on exclude, **code differs** |
| 18 | Smart Meter Data Privacy: A Survey | include | include | include | agree |
| 19 | Intelligent Buildings in Smart Grids | include | include | include | agree (LLM flags text_incomplete, see below) |
| 26 | Privacy-preserving technologies for SG (2025) | include | include | include | agree |
| 106 | Differential privacy applied to smart meters | include | include | include | agree |
| 164 | Review on IoT-based SG architecture | exclude A-E6 | exclude A-E6 | exclude A-E6 | agree |
| 586 | SG challenges through the lens of the GDPR | exclude A-E1 | include | include | **disagree (both runs)** |
| 701 | Privacy and security issues in SG: a survey | include | include | include | agree |
| 857 | SG metering networks survey | include | include | include | agree |

Decision agreement with H1: run 1 10/11, run 2 9/11. Run-to-run: 10/11 (n 14 changed).

## Cases to discuss

### 586: H1 exclude A-E1, LLM include (both runs)
- Point of difference: **A-I1**. H1: the main contribution is the authors' own GDPR analysis of SGAM layers, data flows and challenges (§3–§4, pp. 5–15), supported by a literature review. LLM, p. 1: "We provide a review of existing works highlighting the importance of energy consumption as valuable personal data as well as an analysis of the established Smart Grid Architecture Model and its main challenges from a legal viewpoint". It reasons that the paper "proposes no new attack or mechanism".
- Why the prompt leans to include: A-E1 is defined as "new attack, mechanism, or system", and an original legal or conceptual analysis is none of these. The mixed-paper rule only mentions papers that propose "its own scheme".
- Type: prompt gap (unless H1 changes the decision).
- A-E5: the LLM suggested a duplicate check (an earlier ISD2019 version). Checked: only this one record is in `stream-a-v1.csv`, so there is no duplicate.

### 14: H1 include, LLM include (run 1) / exclude A-E3 mechanism_only (run 2)
- Point of difference: **A-I3** under the blockchain rule ("privacy risks or attacks discussed, not only mechanisms"). Both runs quote the same heading, "3.3. Security and Privacy-Preserving Techniques" (p. 10). Both note that the section states only one risk sentence, p. 10: "By analyzing the electricity consumption profile of the users, malicious entities can track the electricity usage pattern, thereby disclosing the users' private information". Run 1 calls that enough and borderline; run 2 calls it not enough.
- Type: prompt ambiguity. The rule has no threshold for "discussed", so the model flips between runs.
- Code inconsistency: run 2 has A-I2 met and A-I3 not_met but uses primary code A-E3, because the mechanism_only rule says "exclude with A-E3", while the decision order maps A-I3 not_met to A-E6/A-E2.

### 15: both exclude; H1 A-E1, LLM A-E3 (both runs)
- **A-I1**: H1 not met (the B-PDA framework, Multi-PoW/PoS and the scheduling architecture are own contributions, pp. 3, 6–8). LLM met: "its contributions list leads with the survey".
- **A-I2**: both not met (smart meters only as one component on the end-user side, p. 3).
- **A-I3**: H1 met; LLM run 1 met, run 2 not_met.
- Type: same gap as 586 (mixed papers with own framework). It does not change the decision, but it changes the code and the route.

## Quote check
- 110 quotes: 108 found on the cited page, 1 on the next page, 1 not found.
- Not found (run 1, n 18, A-I2): a ligature. The text layer has "ﬁ" (U+FB01) and the model wrote "fi". The quote is genuine; the check does not fold ligatures.
- Next page (run 1, n 857, A-I3): a section heading cited on p. 15 that sits on p. 16. Harmless.
- One quote has 41 words (run 2, n 14, A-I1); the limit is 40. Harmless.

## Text quality
- n 19 (`openalex_W3162781959.pdf`): pages 4–7, 11, 12, 15, 19 and 24 carry overlapping duplicate text layers in the PDF itself, so every extractor interleaves the characters (poppler 22.02 gives the same garbage). The LLM flagged `text_incomplete` in both runs, and no criterion depends on those pages. H1 and the LLM agree on include.

## Reconciliation (H1, 30.10.2026)

Final decisions are in `stream-a-v1.ft-pilot.compare.csv` (`ft_final_*`). H1's blind entries in `stream-a-v1.fulltext.csv` are unchanged.

| n | H1 blind | Final | Reason | Type |
|---|---|---|---|---|
| 586 | exclude A-E1 | **exclude A-E1** | H1 re-checked: the main contribution is the authors' own GDPR analysis of the SGAM layers and data flows, not a synthesis of existing work; outside the direct scope of the survey. | prompt gap → v2: own legal, conceptual or technical analysis as main contribution fails A-I1 |
| 14 | include | **exclude A-E3** (mechanism_only) | Privacy section 3.3 describes only mechanisms; one motivating risk sentence (p. 10) is not enough for A-I3. H1 changed the blind include after reviewing the LLM's evidence. | prompt ambiguity → v2: threshold "at least a paragraph on what can be inferred or how an attack works" |
| 15 | exclude A-E1 | **exclude A-E1** | H1 code kept: own B-PDA framework is a main contribution (pp. 3, 6–8); A-I2 also not met. | same gap as 586, fixed by the v2 mixed-paper rule |

Also in v2: mechanism_only and nilm_only exclusions keep code A-E3 (as at title/abstract and on the screening card), stated as an explicit exception to the decision order. Quote check: ligatures folded (NFKC) before matching.

All other 8 papers: agree, final = H1.
