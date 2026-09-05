# TRIPOD+AI reporting checklist

Supplementary file. TRIPOD+AI (Collins et al., BMJ 2024) is the reporting
standard for prediction-model studies developed with machine learning, extending
TRIPOD (2015).

**How to use this table.** The "Where addressed" column points at the repository
artifact that satisfies each item. Once the manuscript exists, replace those
pointers with section and page numbers; the repository references then move to
the data and code availability statement.

Status key: **done** means the substance exists and is locatable now.
**manuscript** means the analysis is complete but the text has not been written.

---

## Title and abstract

| # | Item | Where addressed | Status |
|---|---|---|---|
| 1 | Identify the study as developing a prediction model, specify the target population and outcome | `MANUSCRIPT_DRAFT.md`, Title: "Reported biomarker-cognition associations do not translate into predictive utility: a pre-registered analysis of NHANES 2011-2014" | done |
| 2 | Structured abstract: objectives, data, participants, outcome, predictors, analysis, results, conclusions | `MANUSCRIPT_DRAFT.md`, Abstract (345 words, Background/Methods/Results/Conclusions) | done |

## Introduction

| # | Item | Where addressed | Status |
|---|---|---|---|
| 3a | Rationale, including the clinical or scientific gap | `MANUSCRIPT_DRAFT.md` Introduction; `LITERATURE_REVIEW.md`. Seven studies report associations in this population, none isolating the biomarkers' incremental contribution over demographics; one 2025 study (Ren et al.) reports a combined-model AUC on a related population without that decomposition, addressed directly | done |
| 3b | Objectives, including whether development, validation, or both | Development with internal validation by repeated cross-validation. No external validation set exists | done |

## Methods: data

| # | Item | Where addressed | Status |
|---|---|---|---|
| 4a | Data source and rationale | NHANES 2011-2012 and 2013-2014, public. `output/tables/00_availability_audit.md` | done |
| 4b | Dates of data collection, and whether data were split | Two survey cycles, pooled. No train/test split; repeated 10-fold CV instead | done |
| 5a | Eligibility criteria | Aged 60+, MEC examined (`RIDSTATR == 2`), at least 3 of 4 cognitive scores. `src/01_cohort.py`, `src/02_outcome.py` | done |
| 5b | Setting and recruitment | NHANES complex multistage probability sample of the non-institutionalised US population | done |
| 5c | Details of treatments received, if relevant | Not applicable. Observational, cross-sectional, no intervention | done |

## Methods: outcome

| # | Item | Where addressed | Status |
|---|---|---|---|
| 6a | Outcome definition and how it was measured | Composite z-score of CERAD immediate, CERAD delayed, animal fluency, DSST; lowest quartile. `PREREGISTRATION.md` section 2 | done |
| 6b | Whether outcome assessors were blinded to predictors | Not applicable. Outcome measured by standardised test administration before any biomarker assay was linked | done |
| 6c | Any actions to blind assessment of the outcome | Not applicable, as above | done |

## Methods: predictors

| # | Item | Where addressed | Status |
|---|---|---|---|
| 7a | Predictors, including how and when measured | `VARIABLE_LOCK.md`, full list with source file and units. 25 features in three blocks | done |
| 7b | Whether predictor assessors were blinded to the outcome | Laboratory assays performed by CDC contract laboratories with no access to cognitive results | done |

## Methods: sample size and missing data

| # | Item | Where addressed | Status |
|---|---|---|---|
| 8 | How sample size was arrived at | Not a power calculation: the analytic sample is the whole eligible population. n = 1,784 with 431 events, 17.2 events per feature. `output/tables/02_gate2_diagnostics.md` | done |
| 9 | How missing data were handled | Complete-case on a single locked row set as primary; multiple imputation by chained equations fitted inside each fold as pre-specified sensitivity. `PREREGISTRATION.md` section 3 | done |

## Methods: analytical methods

| # | Item | Where addressed | Status |
|---|---|---|---|
| 10a | How predictors were handled in the analysis | Log transforms for right-skewed analytes, one-hot for categoricals, standardisation. All fitted inside folds. `src/03_model.py` | done |
| 10b | Model type, building procedure, and internal validation | L2-penalized logistic (primary), random forest, XGBoost. Nested CV: inner CV for hyperparameters, outer 10-fold x 5 repeats | done |
| 10c | How any model updating or recalibration was done | None performed. Calibration reported as observed, not corrected | done |
| 11 | Measures used to assess performance | AUC, AUPRC, Brier, calibration slope and intercept, decision-curve net benefit. `src/04_evaluate.py` | done |
| 12 | How heterogeneity or subgroups were handled | Two survey cycles pooled with cycle recorded; English-only administration as a pre-specified sensitivity analysis | done |

## Methods: specific to AI and machine learning

| # | Item | Where addressed | Status |
|---|---|---|---|
| A1 | Rationale for the chosen algorithms | Penalized regression as the pre-specified primary, two tree ensembles to test whether flexibility helps at this sample size. `PREREGISTRATION.md` section 5 | done |
| A2 | Hyperparameter tuning: search space and selection procedure | Grids stated in `src/03_model.py`; selected by inner 3-fold CV on training folds only | done |
| A3 | How data leakage was prevented | Every transform inside sklearn `Pipeline` objects fitted per fold. An automated audit (`audit_leakage`) refits a fold and asserts the scaler's fitted mean equals the training-fold mean and not the full-sample mean; it fails the run rather than warning. Result recorded as pass in `data/interim/03_model_report.json` | done |
| A4 | Computational resources and reproducibility | Single machine, no GPU, full pipeline under one hour. Master seed 20260831; versions pinned in `requirements.txt` | done |
| A5 | Model interpretability methods and their limitations | SHAP on the best tree model, with rankings bootstrapped over 200 resamples. The instability of biomarker ranks is reported as a finding, and the limitation of single-run SHAP is stated explicitly. `output/figures/fig4_shap_rank_stability.png` | done |
| A6 | Fairness considerations across subgroups | Race and ethnicity included as a predictor; the eGFR equation used is CKD-EPI 2021, which deliberately omits the race coefficient. No subgroup fairness audit was pre-specified. **Declare as a limitation** | done |

## Open science

| # | Item | Where addressed | Status |
|---|---|---|---|
| 13a | Funding and role of funders | `MANUSCRIPT_DRAFT.md` Declarations: unfunded, decided 2026-09-05, pending Neil's confirmation | done |
| 13b | Conflicts of interest | `MANUSCRIPT_DRAFT.md` Declarations: none declared, decided 2026-09-05, pending Neil's confirmation | done |
| 13c | Protocol and registration | `PREREGISTRATION.md`, dated 2026-08-31 before any outcome-predictor relationship was examined, with an explicit integrity statement to that effect | done |
| 13d | Data availability | NHANES is fully public. `src/00b_download.py` reconstructs the raw data from CDC URLs verified in the audit | done |
| 13e | Code availability | Complete pipeline, `src/00_audit.py` through `src/07_figures.py`, each independently runnable | done |

## Results

| # | Item | Where addressed | Status |
|---|---|---|---|
| 14a | Participant flow, ideally a diagram | `output/figures/fig6_participant_flow.png`/`.pdf`, data in `output/tables/08_flow_diagram.md` and `data/interim/08_flow_diagram.json`. Cross-checked: independent recomputation of the final analytic sample from raw predictor completeness matches the locked `02_analytic_seqn.csv` exactly (0 SEQN mismatch) | done |
| 14b | Participant characteristics, including missingness | `output/tables/09_table1.md` (Table 1a: by outcome status; Table 1b: included vs. excluded, recomputed fresh against the final locked sample -- corrected a stale figure carried over from the pre-lock `02_gate2_diagnostics.md`: 26.1%/24.2% low-cognitive-performance prevalence for excluded/included, not 26.2%/24.1%) | done |
| 15 | Number of participants and outcome events | 1,784 participants, 431 events, prevalence 0.2416 | done |
| 16 | Model specification: all coefficients or a means to obtain them | `output/tables/10_m3_coefficients.md` -- full M3 logistic regression refit on the complete analytic sample (n=1,784), standardised coefficients, odds ratios, 2,000-resample bootstrap 95% CIs. `output/tables/05_qgcomp.csv` holds the mixture coefficients separately | done |
| 17 | Model performance with uncertainty | `output/tables/04_performance.csv`, `04_delta_auc.csv`, figures 1 to 3 | done |
| 18 | Results of any model updating | None performed | done |

## Discussion

| # | Item | Where addressed | Status |
|---|---|---|---|
| 19 | Limitations | Cross-sectional design; complete-case selection is mildly non-random; age top-coded at 80; no external validation; no fairness audit; `PBCD_H` half-subsample reduces the 2013-2014 contribution | done, to be written up |
| 20 | Interpretation, considering objectives and prior evidence | `MANUSCRIPT_DRAFT.md` Discussion; `output/tables/07_results_summary.md` section 9 | done |
| 21 | Potential clinical use and implications | Decision-curve analysis shows no threshold at which the panel changes a decision | done |

---

## Items needing attention before submission

Four gaps, all documentation rather than analysis:

1. **Participant flow diagram.** The numbers exist in the attrition table; the figure does not.
2. **Table 1, participant characteristics.** The included-versus-excluded comparison exists; a conventional Table 1 does not.
3. **Full M3 coefficient table.** Item 16 asks for the model specification. Worth reporting the penalized logistic coefficients even though the model adds nothing, because a reader will want to see that no individual biomarker was doing anything either.
4. **Fairness audit (item A6).** Not pre-specified, so adding one now would be a post-hoc analysis. The honest route is to declare it as a limitation rather than run it and present it as planned.

## Note on why this checklist is worth filing

Of the seven comparison studies identified in `PROJECT_BRIEF.md` section 2, none
report to TRIPOD or TRIPOD+AI, and none report discrimination, calibration,
cross-validation, or decision-curve analysis at all. Items A3 (leakage
prevention), 13c (pre-registration) and 11 (performance measures) are where this
study differs most sharply from that literature, and they are the items a
prediction-model reviewer reads first.
