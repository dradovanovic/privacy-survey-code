# Batch 12 comparison: H1 vs screen-A-v1 (records 1161–1260)

Date: 2026-10-19. Frozen prompt screen-A-v1 (SHA-256 `df082ced…0a53`), model `claude-opus-5-5`, Claude Code 2.1.303, two runs.

- All 200 answers are valid, with no retries.
- Per-record table: `stream-a-v1.batch12.compare.csv`. `ta_final` is pre-filled for the agreements; the 16 disagreements are empty.

## Numbers

No record in this batch is `A-E7`, and none is marked "discussed", so all 100 count. Retain means include or maybe. The LLM vote is exclude only if both runs exclude.

| | LLM retain | LLM exclude |
|---|---|---|
| **H1 retain** | 8 | 1 |
| **H1 exclude** | 15 | 76 |

- Agreement is 84/100, and Cohen's κ is 0.43. H1 retains 9 % of records; the LLM retains 23 %.
- Run 1 and run 2 gave the same decision in 100/100, the first batch with no split.
- The first exclusion code is the same on 68 of the 76 joint excludes.

## The 16 disagreements

**H1 retain, LLM exclude (1)**

- **1228**, "Factors Influencing Smart Meter Acceptance in India: A Systematic Review". H1 said `maybe ?A-I1`; both runs excluded it as A-E6.
  - The LLM's reason: privacy appears only as one barrier in a list ("initial costs, privacy concerns, and cultural resistance").
  - H1's note names peer-review status as the open point, which would be `?A-I4`, not `?A-I1`. Both runs also flagged `?A-I4` (venue empty).

**H1 exclude, LLM retain (15)**

- *Domain, with privacy as a main theme* (1161, 1243, 1247): H1 coded A-E3.
  - 1161 is a PRISMA review of energy management with a dedicated privacy cluster (20 papers); smart meters are not named.
  - 1243 surveys machine unlearning for power systems, with smart-meter erasure as one of four use cases.
  - 1247 reviews information-theoretic privacy in networked control, with smart grids as one of two applications.
- *Domain, privacy in a list* (1171, 1176, 1259): H1 coded A-E3; the LLM `?A-I3`, sometimes with `?A-I2`.
- *Privacy in a list* (1178, 1179, 1213, 1233): H1 coded A-E6; the LLM `?A-I2;?A-I3`. 1178 and 1213 are book chapters with a DOI.
  - 1179: the abstract never mentions privacy; it appears only as the keyword "Data Privacy". A-E2 fits the text better than A-E6.
- *Synthesis or primary study* (1180, 1210, 1223, 1246, 1248): H1 coded A-E1; the LLM `?A-I1`, usually with other criteria.
  - 1223 (book chapter) and 1246 survey existing work and then propose and evaluate their own protocol or model.
  - 1248 combines a literature survey with empirical workshops on smart metering and NILM ethics. Privacy is one of 19 themes.
  - 1210 adds its own DoS experiments to a threat review.
  - 1180 introduces an ethics framework; privacy appears only as a keyword.

## A rule point

- Four disagreements are again the A-E6 vs `?A-I3` boundary from batch 11 (1178, 1179, 1213, 1233), and 1233's rationale cites the card's broad-survey line directly.
- Five are the synthesis-or-primary question. The card gives no rule for a survey that also proposes and evaluates its own method, so the LLM keeps `?A-I1` open while H1 decides on the main contribution.

## Other points (not disagreements)

- **1169** (federated learning, H1 include): both runs said `maybe ?A-I2;?A-I3`, citing the FL rule. The abstract names "threat models" but does not show privacy attacks, and covers the grid from consumer to utility level. Both sides retain.
- **1201** (POPIA framework, H1 include): both runs said `?A-I1;?A-I2`, because the main contribution is a new regulatory framework and smart meters are not named.
- **1225** (pseudonymised customers, H1 include): both runs said `?A-I4`, because CEUR Workshop Proceedings do not show peer review.
- **1174, 1229, 1257:** both runs included, the same as H1.
- **Book chapters (10):** all have a DOI. None was excluded on DOI grounds.
- **First-code differences on 8 joint excludes** (1162, 1172, 1185, 1212, 1231, 1245, 1250, 1256). None changes a decision.

## Assessment

- κ 0.43 is in line with batches 7 and 11. The runs agreed with each other on every record.
- All 16 disagreements are known types: domain, A-E6 vs `?A-I3`, and synthesis or primary study.
- Candidates worth a full-text look: 1161 and 1247 (privacy as a main theme) and 1223 and 1246 (survey plus own method) among the disagreements, and 1169 and 1201 among the includes.

## Reconciliation (2026-10-19)

- **The 16 disagreements:**
  - 8 retained (1161, 1176, 1178, 1213, 1243, 1246, 1247, 1259) to check privacy depth, the smart-meter domain or, in 1246, the review status at full text.
  - 8 excluded (1171, 1179, 1180, 1210, 1223, 1228, 1233, 1248). 1228 changed from H1 maybe to exclude.
- **I tidied the reasons without changing any decision:**
  - Spelling ("depht", "need to be checked", "to broad"), plus the code added to each exclude reason.
  - 1210, 1228 and 1233: the reasons gave A-E3, but they argue that privacy is only a side note, which is A-E6. The code is now A-E6.
  - 1171: the reason argues privacy depth, so it is now coded A-E6. The domain is met, since the review covers smart-home consumption data.
  - 1179 and 1180: the reasons said privacy is "only mentioned as a bullet point" or "one aspect", but neither abstract mentions privacy at all; it appears only as a keyword. 1179 now rests on A-E2, and 1180 on A-E1;route=none (it introduces a framework rather than reviewing work).
  - 1223 and 1228: the reasons cited questionable peer-review status. That is not an exclusion ground (it would mean `maybe ?A-I4`), so 1223 now rests on A-E1;route=C and 1228 on A-E6.
  - 1248: the reason said "only NILM perspective" and "privacy depth is not clear". The abstract covers smart metering and NILM, and an unclear depth would mean maybe. The reason now rests on A-E1;route=none (literature survey combined with a primary workshop study), the same as H1's screening code.
  - 1161 (added afterwards): spelling only ("need to be checked full paper").
  - The previous versions are in `_archive/stream-a-v1.batch12.compare.before-tidy.csv` and `before-tidy2.csv`.
- **Final result:** 16 retain, 84 exclude.
- **H1 file:** the 18 empty `;;;;;;` rows at the end of `stream-a-v1.h1.csv` were dropped when batch 13 was appended. The previous file is in `_archive/stream-a-v1.h1.before-batch13.csv`.
