# Batch 5 comparison: H1 vs screen-A-v1 (records 461–560)

Date: 2026-10-17.

- Setup: frozen prompt screen-A-v1 (SHA-256 `df082ced…0a53`), model `claude-opus-5-5`, Claude Code 2.1.302, two runs.
- All 200 answers are valid. One retry was needed in run 1, and it succeeded.
- Per-record table: `stream-a-v1.batch05.compare.csv`. `ta_final` is pre-filled for the agreements and for the A-E7 row; the 15 disagreements are empty.

## Numbers

Row 500 is `A-E7` (no abstract) and is left out, so 99 records count. No row is marked "discussed". Retain means include or maybe. The LLM vote is exclude only if both runs exclude.

| | LLM retain | LLM exclude |
|---|---|---|
| **H1 retain** | 10 | 1 |
| **H1 exclude** | 14 | 74 |

- Agreement is 84/99 and Cohen's κ is 0.49. H1 retains 11 % of records and the LLM retains 24 %.
- Run 1 and run 2 gave the same decision in 98/99. The two splits are 543 and 556.
- The first exclusion code is the same on 67 of the 74 joint excludes.

## The 15 disagreements

**H1 retain, LLM exclude (1).** This is the direction where the LLM would miss a paper.

- **493**, "Privacy-Preserving in Data Aggregation for Smart Grid: A Comprehensive Review". H1 included it; both LLM runs excluded it as A-E3, applying the `mechanism_only` rule.
- The abstract's "primary focus is on aggregation schemes based on homomorphic encryption". The privacy risks (eavesdropping, data breaches) appear only as motivation.
- The rule says an encryption survey is included only if privacy risks or attacks are discussed, not only mechanisms. Unclear means `maybe ?A-I3`.
- That makes H1's include stronger than the abstract supports. It also makes the LLM's exclude stricter than the rule's "unclear → maybe". Retain is the safe reconciliation.

**H1 exclude, LLM retain (14)**

- **Privacy in a list, or privacy depth unclear** (466, 480, 485, 490, 501): H1 coded A-E6 and the LLM `?A-I3`. These are the known boundary.
- **No privacy in the abstract** (479): H1 coded A-E2 and the LLM `?A-I2;?A-I3`. The abstract never mentions privacy, so A-E2 holds on the text.
- **Domain unclear** (528, 542, 557): H1 coded A-E3 and the LLM `?A-I2`.
- **Synthesis or primary study** (482, 537): H1 coded A-E1 and the LLM `?A-I1` or `?A-I2`. Data privacy is a stated main theme of 537.
- **Peer review or status unclear** (503, 543, 556): H1 coded A-E1;route=none and the LLM `?A-I4`.
  - 503 is a privacy overview of smart-meter data with no venue.
  - 543 is an overview of the DLMS/COSEM standard, held in a Turkish repository. The LLM points out that the abstract is partly in Turkish and calls the paper a "bildiri" (conference paper), so English publication is also in question.
  - 556 is the introductory chapter of an edited book. The two LLM runs split: run 1 said maybe and run 2 said exclude A-E4.

## Other points (not disagreements)

- **Book chapters (8).** All have a DOI, and the five re-judged chapters (505, 530, 542, 556, 557) no longer use the DOI argument.
- **First-code differences on 7 joint excludes,** none of which changes a decision:
  - 498 and 549: H1 A-E2, LLM A-E3. A-E3 comes first under the order rule if the domain fails.
  - 529 ("Notice of Violation of IEEE Publication Principles"): H1 A-E4, LLM A-E1. H1's A-E4 is the better first code.
- **Claude Code version.** The CLI updated itself between sessions: 2.1.296 for the pilot, 2.1.300 for batch 1, 2.1.301 for batches 2–3 and 2.1.302 for batches 4–5. Both runs within each batch used the same version, and the version is logged per line. This is now stated in `screening_spec.md` §4.1.

## Assessment

- κ 0.49 is in line with batch 4. The LLM again retains about twice as often as H1.
- The new element is 493, the first record in batches 3–5 where the LLM would exclude a paper H1 keeps.
- Candidates worth a full-text look rather than a quick exclude: 493, 503, 537 and 543.

## Reconciliation (2026-10-17)

- **493** changed from H1 include to exclude: the paper surveys encryption mechanisms only, so the `mechanism_only` rule applies (A-E3).
- **The other 14 disagreements:**
  - 6 retained: 482, 485, 490, 501, 528 and 537.
  - 8 excluded: 466, 479, 480, 503, 542, 543, 556 and 557.
- **I tidied the reasons without changing any decision:**
  - Spelling: "depht", "to broad", "englisch" and similar.
  - 503: removed "abstract in Turkish". That applies to 543, not 503.
  - 542: removed "no peer-reviewed version". The chapter has a DOI (`10.1201/b22998-14`), so the exclusion rests on the domain (A-E3).
  - The previous version is in `_archive/stream-a-v1.batch05.compare.before-tidy.csv`.
- **Final result:** 16 retain, 84 exclude.
