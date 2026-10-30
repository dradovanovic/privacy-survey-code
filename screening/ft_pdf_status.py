"""Refresh pdf_status in the Stream A full-text sheet from data/fulltext/.

Run from code/: python screening/ft_pdf_status.py
found = <record_id with ':' -> '_'>.pdf exists; missing otherwise.
A status set by hand to not_retrievable or read_online is kept unless the PDF has appeared.
"""
import csv, io, os, collections

SHEET = 'data/screening/stream-a-v1.fulltext.csv'
PDFS = 'data/fulltext'

raw = open(SHEET, 'rb').read()
rd = csv.DictReader(io.StringIO(raw.decode('utf-8-sig')), delimiter=';')
fields, rows = rd.fieldnames, [r for r in rd if (r['n'] or '').strip()]
have = set(os.listdir(PDFS)) if os.path.isdir(PDFS) else set()
for r in rows:
    if r['pdf_file'] in have:
        r['pdf_status'] = 'found'
    elif r['pdf_status'] not in ('not_retrievable', 'read_online'):
        r['pdf_status'] = 'missing'
with open(SHEET, 'w', encoding='utf-8-sig', newline='') as f:
    w = csv.DictWriter(f, fieldnames=fields, delimiter=';', lineterminator='\r\n')
    w.writeheader()
    w.writerows(rows)
print(collections.Counter(r['pdf_status'] for r in rows))
extra = sorted(have - {r['pdf_file'] for r in rows} - {'.gitignore'})
if extra:
    print('PDFs not matching any record:', extra)
