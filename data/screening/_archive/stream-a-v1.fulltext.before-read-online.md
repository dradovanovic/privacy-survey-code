# Stream A full-text screening (screening_spec.md §6)

233 records retained at title/abstract (main run 221, pilot 12), one row each in `stream-a-v1.fulltext.csv` (';', UTF-8 with BOM), sorted by `n`.

## PDFs

- Save each PDF as `code/data/fulltext/<pdf_file>`; the name is the record id with ':' replaced by '_' (e.g. `openalex_W4399802073.pdf`).
- The folder has its own `.gitignore`: PDFs are copyrighted and are never committed.
- Refresh `pdf_status` from `code/`: `python screening/ft_pdf_status.py` (found / missing). If a paper cannot be obtained at all, set `pdf_status` to `not_retrievable` by hand; the script keeps it. These go to the PRISMA box "reports not retrieved".
- `pdf_pages`: when the PDF holds more than the paper (e.g. a whole proceedings volume), the PDF page range of the paper; only these pages are screened and sent to the LLM. `pdf_note`: why a PDF is missing, or anything odd about it.
- 3 records have no DOI (1225, 1423, 1673); their `url` column has the source link.

## Columns to fill (H1, blind)

| Column | Content |
|---|---|
| `ft_h1_decision` | `include` or `exclude` |
| `ft_h1_codes` | `A-I1;A-I2;A-I3;A-I4;A-I5` for an include; one primary `A-E` code for an exclude (PRISMA needs one reason) |
| `ev_A-I1` … `ev_A-I5` | where the evidence for each criterion is: section and/or page, e.g. `§5 Privacy, p. 12` (for A-I3 the dedicated privacy section, as in D17) |
| `ft_streams` | other streams the paper is useful for (`B`, `C`), optional |
| `ft_h1_note` | short reason, especially for excludes |
| `ft_h1_at` | date of the decision (dd.mm.yyyy) |

`ta_reason` carries the open point from title/abstract screening (or H1's note where both screeners agreed), so it is clear what the full text has to settle.

## Order and blinding

H1 decides each paper before any LLM full-text output for it exists or is opened. The LLM check (verbatim quote and page per criterion) uses a new frozen prompt, still to be written and piloted on a few papers.
