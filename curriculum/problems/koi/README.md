# KOI Problem Collection

Updated: 2026-05-18

## Source Policy

- Use the official KOI archive as the source of truth for problem statements,
  solutions, model code, and test data.
- Link to official PDFs instead of copying problem text into this repository.
- Use BIKO links for student submissions when available.
- Do not depend on BOJ as a primary judge for this curriculum, because the BOJ
  category page currently shows a service-termination notice dated 2026-04-28.

## Official Sources

- KOI archives: https://koi.or.kr/archives/
- BIKO: https://www.biko.kr/

## Current Local Indexes

- `official-link-index.md`: generated official link index for 2019-2025, rounds
  1 and 2.
- `official-link-index.json`: machine-readable version of the same index.
- `test-data-index.md`: official test-data zip link inventory.
- `2025-round2.md`: current-year official links and first-pass teaching notes.

## Current Coverage

Generated from official KOI pages on 2026-05-18:

- Pages checked: 14
- Indexed rows: 130
- Problem links: 119
- Solution links: 101
- Model-code links: 43
- Solution-code zip links: 39
- Test-data links: 85
- Judge links: 90

## Collection Script

Run this from the repository root:

```powershell
py scripts\collect_koi_links.py
```

The script regenerates:

- `official-link-index.json`
- `official-link-index.md`
- `test-data-index.md`
- `2025-round2.md`

## Download Policy

Official test-data zip links are indexed, but zip files are not redistributed in
this repository by default. If local downloads are needed for private lesson
preparation, put them under `curriculum/problems/koi/downloads/`; that directory
is ignored by git.

## Next Collection Steps

1. Assign one primary K-stage to each problem.
2. Mark boundary problems as bridge/challenge references in adjacent stages.
3. Create per-problem analysis files only for representative K4+ problems.
4. Decide which test-data zips, if any, should be downloaded locally for class
   preparation.
