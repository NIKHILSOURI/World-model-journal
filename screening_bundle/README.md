# Title and abstract screening: Interactive World Models for Games and Virtual Environments

Reviewers: **Nikhil (R1), Tarun (R2), Sameen (R3)**. 662 deduplicated records (Scopus, IEEE Xplore, ACM DL; searches run 16 Oct 2026; years 2018 to 2026).

## What is in this folder

| File | What it is |
|---|---|
| `screening_tool.html` | The Screening Desk for three reviewers. Open it in Chrome, Edge or Firefox. All records, sets and criteria are built in. |
| `criteria.json` | The agreed inclusion (I1 to I6) and exclusion (E1 to E6) criteria. Already built into the tool. |
| `corpus/Deduplicated_corpus_662_records.ris` | The full deduplicated corpus. |
| `agreement/agreement_sample_133.ris` | Random 20% sample (133 records). **All three reviewers screen it.** |
| `agreement/agreement_sample.csv` | The same 133 records as a list (order, ID, title, year, source). |
| `screening/screener_1.ris`, `_2`, `_3` | The other 529 records, split at random: Nikhil 177, Tarun 176, Sameen 176. |
| `screening/assignment.csv` | Which record is in which batch, and whose batch it is. |
| `scripts/draw_sample.py` | Draws the sample and batches. Seed `20261016`, fraction 0.20. Same seed, same files. |
| `scripts/agreement.py` | Agreement statistics from the three exports (same numbers as the tool). |
| `scripts/combine.py` | Merges every decision into the list for full-text screening. |

The scripts need Python 3 only, no extra packages. Run them from this folder.

## Before you start (all three together)

1. The six criteria pairs in `criteria.json` are built into the tool, so there is nothing to load. If you change the wording later, load the new file in the tool (Corpus tab, Criteria, "Load a different criteria.json") on each computer.
2. Batches are fixed by name: Nikhil screens Batch 1, Tarun Batch 2, Sameen Batch 3.

## Step 1: agreement round (each reviewer alone)

1. Open `screening_tool.html`. At the top, choose your name.
2. The Phase switch shows **Agreement** and the 133-record sample opens by itself.
3. On the **Screen** tab, go through all 133. For each record, tick the criteria the abstract meets (left column) or fails (right column), then press **Keep** (1), **Maybe** (2) or **Discard** (3).
   * Keep needs at least one I code, Discard at least one E code, Maybe a short reason.
   * E5 is for full-text screening only, so it cannot be the only code on a Discard. An abstract that describes an implemented system but reports no results is kept (I5).
   * Every export records the criteria version (`criteria_version`). The Resolve tab warns if the files were screened under different versions.
   * Do not discuss records with each other during this round.
4. Your decisions are saved in your browser as you go. When you finish, go to the **Corpus** tab and click **Export decisions (JSON)**. You get `agreement_R1_nikhil.json`, `agreement_R2_tarun.json` or `agreement_R3_sameen.json`.
5. Send your file to the other two reviewers.

## Step 2: agreement check and reconciling (together)

1. One person opens the tool, goes to **Resolve**, and drops in the JSON files. Two or three files both work: with two reviewers the pass mark is Cohen's kappa, with three it is Fleiss' kappa.
2. The pass mark is **binary Fleiss' kappa of 0.80 or more**, with Maybe counted as Keep. The tab also shows pairwise Cohen's kappa for each pair of reviewers, Krippendorff's alpha, how the votes split, and which criteria codes the disagreements came from.
3. **If it passes:** go through every record in the Reconcile list (all disagreements plus every Maybe), agree on Keep or Discard, and click **Export final decisions**. Save it as `agreement/adjudicated_agreement_sample.json`. Click **Export agreement summary (.md)** for the numbers and a draft methods paragraph.
4. **If it does not pass:** reword the criteria that pull apart, draw a new sample with a new seed (`python scripts/draw_sample.py --seed 20261017`), and do the agreement round again on the new sample. Do not re-score the same records.

Optional check from the command line, with the three exports saved in `agreement/`:

```
python scripts/agreement.py
```

It writes `agreement/agreement_report.md` and `agreement/records_to_discuss.csv` (a sheet to work through in the meeting).

## Step 3: screening your batch (each reviewer alone)

1. Switch the Phase to **Screening**. Your batch opens by itself. Maybe is switched off: if unsure, Keep.
2. Screen every record, then export your JSON (`screened_batch1_nikhil.json`, `screened_batch2_tarun.json`, `screened_batch3_sameen.json`). Put it in `screening/`.

## Step 4: combine

When the adjudicated sample and all three batch files are in place:

```
python scripts/combine.py
```

It writes `fulltext/title_abstract_decisions.csv` (every record with its final decision and who made it) and `fulltext/fulltext_candidates_<n>.ris` (the records to retrieve for full-text screening). It also prints the counts for the PRISMA diagram and warns about any record without a decision.

## Good to know

* Decisions are stored per browser, per set and per name. Use the same browser every time, and export at the end of each session as a backup. **Import a decisions file** on the Corpus tab restores an export.
* Switching phase or name never deletes anything; each set keeps its own decisions.
* Agreement uses only the records every loaded file shares, so each reviewer should finish the full sample before you compare. The Resolve tab tells you how many records were left out.
* Sample size: 20% (133 records) was chosen over 10% (66) because with three reviewers and a likely keep rate under 25%, a 66-record sample would hold too few Keeps for a stable kappa. For a 10% sample run `python scripts/draw_sample.py --fraction 0.10`.
