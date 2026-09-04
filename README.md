# Predictive value of nutritional and toxic-metal biomarkers for cognitive performance

NHANES 2011-2014, adults aged 60 and over. A pre-registered test of whether
biomarkers reported as associated with cognition actually predict who has low
cognitive performance, beyond what age, education and income already tell you.

**Headline: they do not.** delta-AUC(M3 - M0) = **-0.0019**, bootstrap 95% CI
[-0.0108, 0.0071], n = 1,784, 431 events. The interval's upper bound falls below
the 0.02 threshold fixed in advance, so this excludes a meaningful improvement
rather than merely failing to detect one.

---

## Start here

| If you want to | Read |
|---|---|
| **Join this project as a co-author** | **`CO_AUTHOR_START_HERE.md`** |
| Get the whole thing in 12 pages | `WRITING_PACK.pdf` |
| See the results | `output/results_review.html`, or `output/tables/07_results_summary.md` |
| Write the paper | `MANUSCRIPT_DRAFT.md`, methods and results in prose |
| Check what was pre-specified | `PREREGISTRATION.md`, dated before modelling |
| Check the variable list | `VARIABLE_LOCK.md` |
| Check reporting compliance | `output/TRIPOD_AI_checklist.md` |
| Understand the data traps | `output/tables/00_availability_audit.md` |

## Reproducing

```
pip install -r requirements.txt
python3 src/00b_download.py      # fetch 40 NHANES files (54 MB) into data/raw/
python3 src/01_cohort.py         # merge, clean, attrition
python3 src/02_outcome.py        # composite z-score, lowest quartile
python3 src/03_model.py          # nested M0-M3 x 3 algorithms (~25 min)
python3 src/04_evaluate.py       # delta-AUC, calibration, decision curves
python3 src/05_interpret.py      # qgcomp, bootstrapped SHAP, partial dependence
python3 src/06_sensitivity.py    # six pre-specified sensitivity analyses
python3 src/07_figures.py        # the manuscript figure set
```

Each script is independently runnable and writes to `data/interim/`, so a later
phase can be re-run without repeating the merge. Every random seed is fixed and
every package version is pinned. Total runtime is under an hour on one machine
with no GPU.

`data/raw/` is not tracked in git. `00b_download.py` rebuilds it from CDC URLs
that `00_audit.py` verified and recorded in `data/interim/00_audit.json`.

## What is where

```
CO_AUTHOR_START_HERE.md     entry point for the clinical lead: what is locked, what is open
WRITING_PACK.pdf            12-page pack: every number, the venue call, abstract draft,
                            Intro and Discussion skeletons, reviewer objections answered
WRITING_PACK.tex            source for the above (tectonic -X compile WRITING_PACK.tex)
PROJECT_BRIEF.md            the original specification
VARIABLE_LOCK.md            variable list, locked and dated, with amendments
PREREGISTRATION.md          hypotheses and analysis plan, dated before modelling
MANUSCRIPT_DRAFT.md         methods and results in manuscript prose
src/00_audit.py             file and variable availability against the CDC site
src/00b_download.py         raw data acquisition
src/01_cohort.py            merge 21 files x 2 cycles, reserved codes, skip patterns
src/02_outcome.py           outcome construction and validation
src/03_model.py             nested models, in-fold pipelines, leakage audit
src/04_evaluate.py          discrimination, calibration, decision curves
src/05_interpret.py         quantile g-computation, SHAP, partial dependence
src/06_sensitivity.py       pre-specified sensitivity analyses
src/07_figures.py           figures, rendered from the tables
output/tables/              results as CSV and markdown
output/figures/             five figures, PNG at 300 dpi and PDF vector
data/interim/               per-phase outputs and machine-readable reports
```

## Design decisions worth knowing

**All models share one row set.** Fitting nested models on different samples
would confound model content with sample composition, making delta-AUC
uninterpretable. The locked rows are in `data/interim/02_analytic_seqn.csv`.

**Nothing is fitted outside a fold.** Imputation, scaling, encoding and
hyperparameter selection all happen inside training folds. `03_model.py` contains
an audit that refits a fold and asserts the fitted scaler matches training-fold
statistics rather than full-sample statistics. It fails the run rather than
warning.

**Reserved codes are per-variable, never blanket.** The applicable codes differ
between variables, and the cognitive score variables have none at all: a blanket
7-and-9 rule would delete valid scores.

## Two data properties that fail silently

Both were found here and both would have survived into the results unnoticed.

**NHANES encodes every zero as a denormal.** Reading the SAS transport files
yields `5.397605346934028e-79` wherever the value is zero: 330,496 cells across
the 40 files used here, with no true `0.0` anywhere. Any `== 0` test matches
nothing. `01_cohort.py` normalises this at read time and asserts none survives.

**Alcohol has two nested skip patterns.** The screening question asks about any
one year of life rather than the past year, and the quantity item is skipped
whenever the frequency item is zero. Both mean zero drinks, not unknown. 403
participants were affected; correcting it recovered 339 for the analytic sample.

## Corrections to the original brief

Verified against the files rather than the codebooks, which document five
variables that do not exist in the data.

| Claim in the brief | Actual |
|---|---|
| Blood metals are full-sample | `PBCD_H` is a one-half subsample of ages 12+ |
| `CUSEZN` is an ordinary Block 3 file | One-third subsample in both cycles; dropped |
| `MCQ` covers stroke and diabetes | Stroke yes; diabetes is in `DIQ`, a file the brief never names |
| Serum iron discontinued after 2009-2010 | Present in `BIOPRO`, both cycles, full sample |
| Serum B12 is one variable | Renamed across cycles: `LBXB12` then `LBDB12` |

## Data source

NHANES is public and de-identified, collected by the US National Center for
Health Statistics. No ethical approval is required for secondary analysis.
Raw files are downloaded from `wwwn.cdc.gov` and never modified.
