# Prompt change log

| Version | Date | Change | Reason | Pilot result |
|---|---|---|---|---|
| screen-A-v1 (draft) | 2026-10-10 | First draft: criteria from `search_protocol.md` §2.2 incl. A-E6 and the 2026-10-10 clarifications; decision order from the screening card; JSON with `primary_code` and `criteria_unclear`; worked examples from pilot records 18 (include), 44 (exclude), 14 (maybe). | Pilot of 60 records screened by the author | pending: not yet run |
| screen-A-v1 (draft) | 2026-10-10 | A-I4/A-E4 wording: magazine feature articles eligible; editorials, columns, news, trade magazines A-E4. | user decision after pilot | pending |
| screen-A-v1 (draft) | 2026-10-10 | Run settings only (prompt text unchanged): Claude Code print mode on the subscription, model `claude-opus-5-5`, no tools, default sampling. | no API billing; see `screening_spec.md` §4.1 | pending |
| **screen-A-v1 FROZEN** | 2026-10-13 | No change after the pilot. Frozen file SHA-256 `df082ced81a8646e630811b84ffd4780665be4ff70ca4b3e9e65c5f475c00a53`; model `claude-opus-5-5`; Claude Code 2.1.296 print mode (`screening_spec.md` §4.1). The file's header still says DRAFT; it is left unedited so the hash stays the same. | Pilot: no disagreement traced to the prompt | `stream-a-v1.pilot.compare.md` |
