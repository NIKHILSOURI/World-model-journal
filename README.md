# Interactive World Models for Games and Virtual Environments: review screening materials

Materials for the title and abstract screening stage of a systematic review of interactive world models for games and virtual environments. Searches were run on 16 October 2026 (Scopus, IEEE Xplore, ACM Digital Library; publication years 2018 to 2026). Reviewers: Nikhil, Tarun, Sameen.

## Repository layout

```
.
├── screening_bundle/          Everything the three reviewers need to screen (self-contained)
│   ├── README.md              Step-by-step reviewer instructions
│   ├── screening_tool.html    Offline screening tool (open in Chrome, Edge or Firefox)
│   ├── criteria.json          Draft inclusion (I1 to I4) and exclusion (E1 to E4) criteria
│   ├── corpus/                The 662 deduplicated records (RIS)
│   ├── agreement/             20% agreement sample (133 records) screened by all three reviewers
│   ├── screening/             The other 529 records, split into three batches, plus assignment.csv
│   └── scripts/               draw_sample.py, agreement.py, combine.py (Python 3, standard library only)
└── search_records/            How the corpus was built (for the PRISMA flow and methods)
    ├── raw_exports/           Records exactly as exported from each database
    ├── deduplication_log.xlsx Status of every identified record, and why it was removed or kept
    └── quasi_gold_set.xlsx    Quasi-gold-standard papers, search-string revision log, skipped results
```

## Record flow

| Step | Records |
|---|---|
| Identified: Scopus / IEEE Xplore / ACM DL | 491 / 307 / 35 (833 in total) |
| Removed: ineligible document type (IEEE book chapters, magazines) | 25 |
| Removed: duplicates (same DOI, or same title and year when no DOI) | 146 |
| **Records to screen** | **662** |

The full log is in `search_records/deduplication_log.xlsx`.

## Getting started

Reviewers: open `screening_bundle/README.md` and follow Steps 1 to 4. Run the scripts from inside `screening_bundle/`, because they use paths relative to that folder.

## Reproducibility

The agreement sample and the three batches are drawn with a fixed seed (`20261016`, fraction `0.20`). Running `python scripts/draw_sample.py` from `screening_bundle/` regenerates the committed files byte for byte (checked before publishing). Report the seed and fraction in the methods.

## Data and licensing notes

* `search_records/raw_exports/` and the corpus files contain bibliographic records (titles, abstracts, author details) exported from Scopus, IEEE Xplore and the ACM Digital Library. Check each database's terms before making this repository public, or keep the repository private.
* No software license has been chosen yet. Add a `LICENSE` file before sharing the code.
