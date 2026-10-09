# Seed diagnosis (Scopus): `stream-a-v1`

retrieved 13/15 evaluated seeds; diagnosing 2 missed seeds expected from Scopus

Title, year and document type come from Scopus (view STANDARD). Abstract and keywords
come from OpenAlex, because STANDARD returns neither: OpenAlex keywords are
machine-assigned, not the Scopus author keywords and index terms that TITLE-ABS-KEY
searches, and an OpenAlex abstract can differ from the Scopus one.

## Mohassel14a  —  A survey on Advanced Metering Infrastructure
- DOI 10.1016/j.ijepes.2014.06.025; raw: 10.1016_j.ijepes.2014.06.025.json (scopus), 10.1016_j.ijepes.2014.06.025.json (openalex)
- in Scopus: 2014 · Article (ar) · International Journal of Electrical Power and Energy Systems · 2-s2.0-84904003700
- OpenAlex: abstract 145 words; 20 keywords/concepts

| concept group | title | abstract | keywords | group |
|---|---|---|---|---|
| secondary_research | survey | survey | — | match |
| domain | advanced metering infrastructure | advanced metering infrastructure, AMI, smart grid | advanced metering infrastructure, smart grid | match |
| privacy | — | — | — | **no match** |

- **verdict: terminology miss**: no term of ['privacy'] in title, abstract or keywords

## Eskandarnia22a  —  Deep learning techniques for smart meter data analytics: A review
- DOI 10.1007/s42979-022-01161-6; raw: 10.1007_s42979-022-01161-6.json (scopus), 10.1007_s42979-022-01161-6.json (openalex)
- in Scopus: 2022 · Review (re) · SN Computer Science · 2-s2.0-85128825797
- OpenAlex: abstract 0 words; 27 keywords/concepts

| concept group | title | abstract | keywords | group |
|---|---|---|---|---|
| secondary_research | review | — | — | match |
| domain | smart meter | — | smart meter, smart grid, energy consumption data | match |
| privacy | — | — | — | **no match** |

- **verdict: no term of ['privacy'] in the title; abstract not available to check**

## Verdicts

- in Scopus, terminology miss: 1
- in Scopus, abstract not checkable: 1