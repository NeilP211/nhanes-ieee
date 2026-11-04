# DPR revision, round 1 (prepared 2026-11-04, due 2026-11-25)

Submission ID `6b0f095f-9022-4344-ae4f-122a3ff71428`. Decision: revise. The submitting
author (Shreyan) uploads everything.

## Read these first

1. `response_to_reviewers.pdf`: the point-by-point response. Covers the editor, all
   three Reviewer 1 comments, all Reviewer 2 comments (including Table 1 and tone),
   and a list of accuracy fixes we found ourselves.
2. `manuscript_marked_up.pdf`: every change against the submitted version, deletions
   struck in red, additions underlined in blue.
3. `manuscript_revised.pdf`: the clean revised manuscript.

## Decisions for both authors before uploading

- **Title changed** to "Blood metal and nutritional biomarkers do not improve
  identification of low cognitive performance beyond demographics in older US adults:
  a pre-registered analysis of NHANES 2011-2014". Reason: the new demographically
  adjusted analysis found the biomarkers do add some signal for performance lower than
  expected for demographic background, so the old title ("do not translate into
  predictive utility") overstates. If you prefer the old title, change it in
  `manuscript_revised.template.tex` and the response letter, and the portal metadata.
- **Countersign the pre-registration amendment.** `PREREGISTRATION.md` Amendment 1 and
  Additional file 1 show Shreyan's countersign as pending.
- **Authors' contributions** now say N.P. ran the peer-review analyses and both authors
  revised the manuscript. Edit if that is not how you want it recorded.
- **AI-use disclosure.** Springer Nature asks authors to document use of large language
  models in the Methods (copy editing excepted). Most of this revision's analysis code
  and text was drafted with Claude. The manuscript does not currently say so; decide
  together whether to add a sentence.
- **Response letter is not in the public repo.** It quotes the confidential reviewer
  reports verbatim, so `response_to_reviewers.*` and the zip are gitignored. Neil sends
  the PDF or zip directly.

## What to upload in the portal

| Portal slot | File |
|---|---|
| Point-by-point response (PDF) | `response_to_reviewers.pdf` |
| Manuscript (no tracked changes) | `nhanes_manuscript_revision.pdf` (same as `manuscript_revised.pdf`), plus `nhanes_manuscript_revision.zip` if LaTeX source is requested |
| Marked-up manuscript (related files) | `manuscript_marked_up.pdf` |
| Figures 1 to 6 | `figures_upload/Figure_1.tiff` to `Figure_6.tiff` (only Figure 2 changed) |
| Tables 1 to 3 | `tables_upload/Table_1.pdf`, `Table_2.pdf`, `Table_3.pdf` (Table 1 extended, Table 3 new) |
| Additional file 1 | `supplementary/Additional_file_1_Preregistration.pdf` (amendment appended) |
| Additional file 2 | `supplementary/Additional_file_2_TRIPOD_AI_checklist.pdf` (rows updated) |
| Additional file 3 | `supplementary/Additional_file_3_Table_S1_M3_coefficients.pdf` (title only) |
| Additional file 4 (new) | `supplementary/Additional_file_4_Revision_tables.pdf` (Tables S2 to S8) |

## How the numbers were produced

No number in the revised text is typed by hand where it comes from a new analysis.

```
python3 src/11_revision_models.py    # M4 (M0+ plus biomarkers), 3 algorithms; checks M0 reproduces exactly
python3 src/12_revision_outcome.py   # missingness, 3 vs 4 scores, labelled vs not, Table 1 cognitive rows
python3 src/13_revision_evaluate.py  # margins, all pairwise contrasts, complete battery, adjusted outcome
python3 src/07_figures.py            # Figure 2 (forest plot) redrawn from the phase 13 tables
python3 src/14_revision_tables.py    # LaTeX table bodies + numbers.json
python3 src/15_fill_revision_text.py # fills [[tokens]] in the templates; fails on any unresolved token
```

Phase 13 replays the original bootstrap random-number sequence and asserts that every
interval in the submitted manuscript reproduces before it computes anything new.

## Headline results of the new analyses

- M4 minus M0+ (biomarkers added to the clinical baseline): -0.0037, 95% CI -0.0112 to
  0.0029. Null on properly nested models, under all three algorithms.
- Margin analysis: the primary analysis excludes improvements above 0.0056, but the
  10th-percentile analysis only excludes improvements above 0.0132. "Precise null" is
  withdrawn everywhere.
- Complete battery (4 of 4 scores): still null (-0.0045).
- Demographically adjusted outcome (exploratory): every model is weak (AUC 0.56 to
  0.62); biomarkers beat demographics (+0.0362, 0.0068 to 0.0667) but not the clinical
  baseline (+0.0093, -0.0109 to 0.0284). Reported in the abstract and conclusions.
- Continuous-outcome R-squared gain now has an interval, and it includes zero.
