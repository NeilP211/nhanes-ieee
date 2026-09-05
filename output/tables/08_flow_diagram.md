# Participant flow diagram, data

**TRIPOD+AI item 14a.** Underlying data for the flow diagram figure (`output/figures/fig6_participant_flow.png`). Every stage traces to the source file listed.

| Stage | n | Excluded at this step | Source |
|---|---|---|---|
| Examined in NHANES 2011-2012 or 2013-2014, all ages | 19,931 | — | `output/tables/00_availability_audit.md` |
| Aged 60 years or older | 3,632 | 16,299 | `output/tables/00_availability_audit.md` |
| Completed the Mobile Examination Centre visit (RIDSTATR==2) | 3,472 | 160 | `data/interim/01_attrition.csv` |
| Received an outcome label (>=3 of 4 cognitive scores) | 3,124 | 348 | `data/interim/02_outcome_report.json` |
| Complete data on all Block 1-3 predictors and covariates (final locked analytic sample) | 1,784 | 1,340 | `data/interim/02_analytic_seqn.csv` |

## Reasons for exclusion at the final step (n=1,340 dropped from the outcome-eligible sample)

Not mutually exclusive; a participant can be missing more than one block, so these do not sum to the total excluded.

| Missing block | n of the 3,124 outcome-eligible participants |
|---|---|
| Any demographic (Block 1) | 275 |
| Any blood metal (Block 2) | 930 |
| Any nutritional/metabolic biomarker (Block 3) | 270 |
| Any clinical covariate (M0+ block) | 187 |

Cross-check: an independent recomputation of "complete data on all predictors" from `02_outcome.parquet` found 1,784 participants, against 1,784 in the locked `02_analytic_seqn.csv` (0 SEQN differ). This matches exactly.
