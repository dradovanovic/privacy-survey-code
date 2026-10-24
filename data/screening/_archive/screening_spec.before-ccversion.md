# Screening specification (human screening, LLM as blind second reviewer)

Version 2, 2026-10-10. Replaces version 1 (LLM first pass, human adjudication of `maybe` and a sample).
Decided by the user on 2026-10-10 (`DECISION.md` D18, superseding D11). Revised the same day: every disagreement is reconciled, and no second human is used.
Evidence and reasons: `docs/llm_screening_evidence.md`.

**Principle.** The eligibility criteria are fixed in advance (`search_protocol.md` §2.2).
For every paper, the author and the LLM apply the same criteria to the same text, each without knowing the other's decision.
The two decisions are then compared, and every disagreement is reconciled by the author with a written reason.
No paper enters or leaves the corpus on an LLM decision alone. There is one human reviewer; no second human is used.

## 1. Roles

- **Reviewer H1 (the author)**: screens every record at title/abstract level, reads the full text of every candidate, and makes every final decision. H1 is the reference standard.
- **Screener-LLM**: applies the same criteria independently to the same input and returns a structured decision with a rationale. Its output is hidden from H1 until H1 has recorded a decision for that record.

## 2. Output schema

### 2.1 LLM output (one JSON object per record per run)

```json
{
  "record_id": "ieee:9123456",
  "stream": "A",
  "decision": "include | exclude | maybe",
  "primary_code": "first failed code in the screening order | null",
  "criteria_met": ["A-I1", "A-I2", "A-I3"],
  "criteria_failed": ["A-E1"],
  "criteria_unclear": ["A-I3"],
  "route": "B | C | none | null",
  "rationale": "one or two sentences quoting the decisive phrase from the record",
  "flags": ["nilm_only", "mechanism_only", "abstract_missing", "ambiguous_ami"],
  "prompt_version": "screen-A-v1",
  "model": "<exact model string>",
  "run": 1,
  "screened_at": "ISO-8601"
}
```

The v1 `confidence` field is dropped. LLM self-reported confidence is not well calibrated, and in this workflow nothing depends on it.

### 2.2 Human record (one row per record)

| Field | Meaning |
|---|---|
| `h1_ta_decision` | `include`, `exclude` or `maybe`, recorded blind to the LLM |
| `h1_ta_codes` | criteria codes met or failed (same codes as the LLM) |
| `h1_ta_note` | optional free text |
| `h1_ta_at` | timestamp |
| `ta_agreement` | computed after unblinding (§5.2) |
| `ta_final` | `retain` or `exclude` after reconciliation |
| `ta_final_reason` | required when H1 keeps an exclude against an LLM retain (§5.3) |
| `ft_*` | full-text fields (§6) |

**Where H1 decisions live.** Not in the generated sheet `data/screening/stream-a-v1.csv`: that file is rebuilt when new sources are merged (Scopus), which would overwrite manual entries. H1 decisions go in a separate file, `data/screening/stream-a-v1.h1.csv`, one row per record, joined to the sheet by `record_id`:

```
record_id,h1_ta_decision,h1_ta_codes,h1_ta_note,h1_ta_at
ieee:9123456,exclude,A-E2,security-only (FDIA/IDS),2026-10-11
openalex:W123,include,A-I1;A-I2;A-I3;A-I4;A-I5,,2026-10-11
ieee:9234567,maybe,?A-I3,privacy depth unclear from abstract,2026-10-11
ieee:9345678,exclude,A-E1;route=B,proposes attribute-inference attack,2026-10-11
```

Coding rules:
- `h1_ta_decision`: exactly `include`, `exclude` or `maybe`, lower case.
- `h1_ta_codes`: for `exclude`, the decisive exclusion code (the first "no" in the screening order); for `include`, all inclusion codes; for `maybe`, the criterion that cannot be judged, prefixed with `?`. Several codes are separated by `;`. A-E1 adds `route=B` (attack study), `route=C` (defense) or `route=none` (primary study that is neither).
- `h1_ta_note`: a few words; flags (`nilm_only`, `mechanism_only`, `abstract_missing`, `ambiguous_ami`, `background`) go here. `background` marks an excluded record worth citing outside the systematic corpus; it never changes the decision.
- `h1_ta_at`: date (ISO 8601).
- A row is written once and never edited after the comparison with the LLM; reconciliation results go in `ta_final` / `ta_final_reason`.
- The file may be comma- or semicolon-separated (Excel with a German locale saves `;`); the compare step must accept both.
- The file may carry helper columns `n` (reading order) and `title`; they are ignored when joining.

**Pilot files (2026-10-10).** `stream-a-v1.h1.csv` holds the 60 pilot records; their texts are in `stream-a-v1.pilot.md`. They were drawn with seed 20261010 from the 1499-record IEEE+OpenAlex sheet: 20 at random, 5 seeds, and 35 likely hard cases picked by title/abstract patterns (security-only, NILM, mechanism-only, generic IoT, no review term, abstract missing). The group of each record is in `stream-a-v1.pilot-selection.csv`, which H1 opens only after the pilot is screened. Quick reference: `docs/screening_card_stream_a.md`.

Screener rules shared by H1 and the LLM (all streams):
- **Evidence limitations never justify `exclude`** (D6). They are recorded as flags (`small_sample`, `single_dataset`, `no_code`).
- Stream B: judge *disclosure capability*, not vocabulary (D7).
- Stream C: `include` requires a stated or evident link to an inference attack class; generic security mechanisms are `exclude` (C-E1) unless such a link is present (D8).
- `include` only if every inclusion criterion is judged met from the text available. If a criterion cannot be judged from the abstract (typically A-I3), the decision is `maybe`.
- `exclude` requires at least one exclusion code; A-E1 must set `route_to_stream`.
- The LLM rationale must point to text in the record, with no outside knowledge about the paper.
- Abstract missing or shorter than 30 words: `maybe` + flag `abstract_missing` (both reviewers).

## 3. Prompt structure (screen-A-v1)

1. Role and task: "You are screening records for a systematic survey. Apply the criteria literally. Do not use knowledge about the paper beyond the text given."
2. The survey scope paragraph (from `survey_design.md` §1).
3. The verbatim criteria list and borderline rules (from `search_protocol.md` §2.2).
4. Worked examples (few-shot) with the expected JSON: a clear include, a clear exclude (security-only, off-domain survey), and a `maybe` (blockchain smart-grid review with unclear privacy depth). They are taken **only from the development set** (§4), never from records whose performance is reported.
5. The record: title, year, venue, keywords, abstract.
6. Output instruction: JSON only, matching the schema. Model and run settings are in §4.1.

Prompt text lives in `code/prompts/screen-A-v1.md` and is versioned like queries.

## 4. Before the main run: pilot and prompt development

1. **Development set.** Draw about 60 records: about 20 at random from the screening sheet and about 40 chosen by H1 to cover hard cases (security-only, mechanism-only, NILM-only, off-domain, and borderline privacy depth). Seeds may be added as a sanity check, but they are not evidence of recall: they are well-known surveys the model has probably seen in training.
2. **H1 pilot.** H1 screens the development set first, blind. Any criterion H1 finds hard to apply is clarified in `search_protocol.md` §2.2 *before* the main run, with a change-log entry. This step calibrates the criteria and the human, not only the prompt.
3. **Prompt tuning.** Run the LLM on the development set, inspect every disagreement, fix the prompt, bump the version and rerun. Log each iteration in `code/prompts/CHANGELOG.md`.
4. **Freeze.** Record the frozen prompt version, model string and date in the change log. From this point the prompt is never edited.
5. Development-set records are screened by H1 like any other record, but they are **excluded from all reported LLM performance figures**, because the prompt was tuned on them.

**Pilot outcome (2026-10-13).** In the pilot, H1 also looked at the papers' sections, not only title and abstract, so the 60 H1 pilot decisions are partly full-text informed. They are kept as recorded and not re-screened: a re-screen would not be blind to the full text already seen, and the pilot is excluded from all figures anyway. The comparison showed no prompt error (`code/data/screening/stream-a-v1.pilot.compare.md`), so screen-A-v1 was frozen unchanged. If batch 1 of the main run shows a prompt problem, the prompt gets a new version and batch 1 joins the development set.

### 4.1 Run setup (decided 2026-10-10)

The LLM is called through **Claude Code in non-interactive print mode** (`claude -p`) on the author's existing Claude subscription, so no separate API billing is needed. The usage counts against the plan's normal limits.

- **One call per record per run.** A script calls `claude -p` once per record. Each call is a new session with no history, so no record and no earlier answer is visible to the model.
- **Input.** System prompt: the SYSTEM section of the prompt file, verbatim. Message: the USER template filled with title, year, venue, content type, keywords and abstract only. No other column of the screening sheet is sent.
- **Missing abstracts.** Records without an abstract (or under 30 words) are listed in `code/data/screening/stream-a-v1.abstracts-manual.csv`. H1 copies the abstract verbatim from the publisher page or the PDF's first page into `abstract`, sets `abstract_source` (`publisher` or `pdf`) and `filled_at`. The sheet `stream-a-v1.csv` is not edited by hand. Both the H1 screening view and the LLM run use the manual abstract where the sheet has none. A record with no abstract found keeps the `abstract_missing` rule.
- **No abstract at all → A-E7** (D19, 2026-10-16). Records with no abstract after the manual search are excluded with `A-E7` by H1 and are not screened. The frozen prompt still contains the older `abstract_missing` → `maybe` rule; it is not edited (the prompt hash must stay fixed). LLM outputs for A-E7 records are ignored, and these records are left out of all agreement and performance figures. They are reported as their own line in the PRISMA flow.
- **Pinned model.** `--model claude-opus-5-5` (exact ID). The same model is used for the pilot and the main run. A model change means a new prompt version and a rerun of the pilot.
- **No tools, no project context.** All tools are disabled, and every call runs from an empty working folder outside the project. The model cannot open `stream-a-v1.h1.csv` or any other file. The script itself never reads the H1 file.
- **Context added by Claude Code.** Print mode still adds, around the SYSTEM text: an identity sentence before it, a system reminder with account context, and an environment block (temporary folder, platform, model name, date). The SYSTEM text itself arrives verbatim. This is recorded per call in a `context_additions` field and stated in the supplement. Run with `--tools "" --strict-mcp-config --safe-mode --disable-slash-commands --no-session-persistence` (Claude Code 2.1.296 for the pilot).
- **Temperature.** Not settable in print mode; the model's default sampling is used. Variability is measured instead: two independent runs per record, and run-to-run agreement is reported (§7). This is stated in the methods section.
- **Logging.** One JSONL file per run (`code/data/screening/llm/<sheet>.<prompt_version>.run<k>.jsonl`). Each line holds `record_id`, `run`, `prompt_version`, the SHA-256 of the prompt file, the requested model, the model reported by the CLI, the Claude Code version, the exact command flags, `screened_at`, the raw answer text, the parsed JSON (or a parse error) and the CLI's usage metadata.
- **Failures.** A call that fails, or returns invalid JSON, is retried once and the retry is logged. If it still fails, it is recorded as `error` and listed; it is never filled in by hand.
- **Order.** Run 1 completes for all records, then run 2. Calls are sequential.
- **Blinding.** The comparison with H1 is a separate step, run only after both LLM runs are finished and after H1's decisions for that batch are recorded.

The instruction used for the pilot run is `code/prompts/run-screen-A-pilot.md`.

## 5. Title/abstract screening (every record)

### 5.1 Two independent passes

- **H1 pass.** H1 screens every record from title, abstract, keywords, year and venue only. The screening view must not show any LLM output. Records can be screened in batches.
- **Input and batches.** Both passes read `code/data/screening/stream-a-v1.screening-input.csv`: the sheet with the manual abstracts merged in (`abstract_source = manual_*`). The 1,627 non-pilot records are in a fixed random order (seed 20261013) in `stream-a-v1.batches.csv`, numbered `n` = 61–1687, in 17 batches of 100 (the last has 27). Per batch: a reading view `stream-a-v1.batchNN.md`, an ID list `stream-a-v1.batchNN.ids.csv`, and the rows in `stream-a-v1.h1.csv`. H1 screens the batch first; the LLM runs on it afterwards.
- **LLM pass.** The frozen prompt is run **twice** on every record (run 1, run 2), into a separate file that H1 does not open until H1's batch is finished. Either order (LLM before or after H1) is fine as long as H1 stays blind.
- **LLM vote.** The LLM counts as `retain` if either run returns `include` or `maybe`, and as `exclude` only if both runs return `exclude`. Run-to-run disagreement is logged and reported.

### 5.2 Comparison (after H1 finishes a batch)

H1 `include` and `maybe` both count as `retain`.

| H1 | LLM | Action | `ta_final` |
|---|---|---|---|
| retain | retain | none | retain |
| exclude | exclude | none | exclude |
| retain | exclude | **reconcile (§5.3)** | H1 decides |
| exclude | retain | **reconcile (§5.3)** | H1 decides |

### 5.3 Reconciling disagreements

Every disagreement, in either direction, is handled the same way:
- H1 re-reads the record together with the LLM's codes and rationale, checking both against the criteria text.
- H1 records the final decision, the criterion that decides it, and a one-line reason in `ta_final_reason` that says why the other decision does not hold. A bare "agree" or "disagree" is not allowed.
- If H1 changes their own decision, it is logged as `h1_changed_after_llm`; if H1 keeps it, as `h1_kept`.
- When in doubt at title/abstract level, retain. Reading the full text is the cheaper error.
- The blind decisions are never overwritten: `h1_ta_decision` and the LLM outputs stay as recorded, so agreement is always computed on the blind decisions.

Because the same person makes the blind decision and reconciles it, there is a risk of confirmation bias. The written reason per disagreement is the safeguard, and the paper states the single-reviewer design as a limitation.

## 6. Full-text screening (every paper retained at title/abstract)

Every record with `ta_final = retain` is read in full by H1. This is where H1 confirms or rejects each paper for the corpus.

1. **H1 decision, blind.** H1 reads the full text and records `ft_h1_decision` (`include` / `exclude`), the criteria codes, and for every inclusion criterion the location of the supporting evidence (section or page). For A-I3 this is the dedicated privacy section, as already done for Komninos14a, Mohassel14a and Eskandarnia22a (D17).
2. **LLM check.** The LLM receives the full text and the same criteria and returns, for each criterion, a judgment with a verbatim `{"quote": "...", "page": n}`. H1 does not see this until step 1 is recorded.
3. **Reconciliation.** Every disagreement, in either direction, is resolved by H1 against the PDF as in §5.3, with the outcome and reason logged. LLM quotes are checked against the PDF before they are used anywhere; an unverifiable quote is discarded.
4. **Final corpus.** A paper enters the corpus only with an H1 `include`, its criteria codes, and the evidence locations. Full-text exclusions keep one primary reason code each, for the PRISMA box.
5. Records found by snowballing (D13) go through §5 and §6 in the same way (re-screening stage, D12).

## 7. What is reported

Calculated on all records **except the development set**, using H1's blind decisions and the final decisions:

- Sensitivity and specificity of the LLM against `ta_final` and against H1's blind decision, with 95 % CIs (Wilson or Clopper–Pearson).
- **Sensitivity of H1 alone against `ta_final`**: the number of records H1 initially excluded that the LLM flagged and that ended up retained, and how many of those reached the final corpus. This is the measured value of the LLM as a second reviewer.
- Cohen's κ for H1–LLM on the blind decisions, reported with prevalence, because κ depends on it.
- Number of disagreements, split by direction, and how many ended with H1 changing their decision.
- LLM run-to-run agreement (run 1 vs run 2).
- Full text: H1–LLM agreement per criterion, and the number of LLM quotes that failed verification.
- PRISMA flow with human and LLM decisions shown separately at each stage (PRISMA-trAIce R1).

## 8. Disclosure text for the methods section (draft)

> Eligibility was assessed by a single human reviewer (the first author) against criteria fixed before screening.
> All records were screened at title and abstract level by the first author.
> A large language model (model, version and access dates in the supplement; called through the Claude Code command-line tool in non-interactive mode, one independent call per record, default sampling) screened the same records independently as a second reviewer, using the verbatim eligibility criteria and a prompt frozen after a pilot on *n* = 60 records that are excluded from all performance figures.
> The model ran twice per record; a record counted as an LLM exclusion only if both runs excluded it.
> The author's decisions were recorded before the model's output was shown.
> Every disagreement between the author and the model was re-examined against the criteria, and the final decision was recorded with a written reason; the blind decisions were retained for the agreement analysis.
> No second human reviewer was involved; this is acknowledged as a limitation.
> Every study in the final corpus was read in full and confirmed by the author against the eligibility criteria, with the supporting passage recorded.
> Sensitivity, specificity and Cohen's κ of the model against the author's decisions, run-to-run agreement, and the number of eligible studies first identified by the model are reported in Table X.
> Prompts, model identifiers, parameters and all decisions are provided as supplementary material.

Cite: PRISMA 2020 item 8 (Page et al., *BMJ* 2021), the Cochrane/Campbell/JBI/CEE position statement on AI in evidence synthesis (Flemyng et al., 2025), and PRISMA-trAIce (Holst et al., *JMIR AI* 2025). Keys still need to be added to `paper/bibliography.bib`.

## 9. Full-text extraction (outline; codebook to follow)

Same pattern: H1 extracts; the LLM may propose values, each with `{"quote": "...", "page": n}`; H1 verifies every quote against the PDF before a value enters a table. Fields per stream are listed in `survey_design.md` §6.

## 10. Implementation notes for the pipeline (local Claude Code)

Not done in this project; listed so the local pipeline work can pick it up.

- A screening view (CSV or small UI) that shows only record fields and H1 columns, with no LLM columns.
- LLM outputs written to a separate file per run (`code/data/screening/llm/<sheet>.<prompt_version>.run<k>.jsonl`, see §4.1), joined to the H1 sheet only by a `compare` step after H1 marks a batch done.
- A `compare` step that fills `ta_agreement`, lists the "H1 exclude, LLM retain" records for §5.3, and computes the §7 figures.
- The development-set record IDs stored in a file, so they can be excluded from §7.
