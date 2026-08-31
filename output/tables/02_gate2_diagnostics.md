# Gate 2: cohort and outcome diagnostics

**2026-08-31.** Phases 1 and 2 complete. This is the review document for the
blocking gate. Modeling does not start until this is reviewed and
`PREREGISTRATION.md` is written and dated.

Numbers are reproducible from `data/interim/01_cleaning_report.json` and
`data/interim/02_outcome_report.json`. Regenerate the pipeline with
`python3 src/01_cohort.py && python3 src/02_outcome.py`.

---

## 1. What ran

| Script | Output | Status |
|---|---|---|
| `src/01_cohort.py` | `01_cohort.parquet`, 3,472 rows, 93 columns | All assertions pass |
| `src/02_outcome.py` | `02_outcome.parquet`, outcome columns added | All assertions pass |

Assertions that must hold before the chain continues, all currently passing:
`SEQN` unique after stacking; no reserved code surviving in any numeric column;
no denormal-zero surviving; no column entirely missing; every row aged 60+ and
MEC-examined; no zero-weight record; weighted 60+ population inside a plausible
range; every z-score centred at zero with unit variance; prevalence near the
intended quartile; no ineligible row carrying a label.

Weighted 60+ population: **59,659,564**, against a true US 60+ population of
roughly 60 to 63 million in 2011-2014. Consistent.

---

## 2. Two bugs found and fixed during Phase 1

Both were silent. Both produced plausible-looking numbers.

### 2.1 NHANES encodes every zero as a denormal

Reading NHANES XPORT with pandas yields `5.397605346934028e-79` wherever the
value is zero. Verified across all 40 downloaded files: **330,496 cells hold
this value and not a single cell holds a true `0.0`.**

This is not confined to survey weights, which is how it was first noticed in
Phase 0. It reaches cognitive scores of zero, PHQ-9 "not at all" responses,
every below-detection comment code, participant age for infants, and the alcohol
frequency question. Any `== 0` comparison against raw NHANES data silently
matches nothing.

`01_cohort.py` now normalises this at read time in `normalize_zeros()`, applied
to every float column before any comparison or arithmetic. An assertion fails
the run if any denormal survives. No legitimate value in any file falls between
zero and 1e-60, so the epsilon rule is safe.

### 2.2 Alcohol had two nested skip patterns read as missingness

`ALQ101` asks whether the participant had 12+ drinks in **any one year of life**,
not in the past year. A person can answer yes and still report no drinking in the
past 12 months. Separately, `ALQ130` (quantity) is skipped whenever `ALQ120Q`
(frequency) is zero, which the denormal bug above had made invisible.

Both cases mean **zero drinks, not unknown**. 403 participants were affected.

Effect of the fix on the analytic sample:

| | Complete cases across all covariates |
|---|---|
| Before | 1,450 of 2,194 (66.1%) |
| After | **1,789 of 2,194 (81.5%)** |

`ALQ120Q` was added to the pulled columns to resolve this. Recorded as an
amendment in `VARIABLE_LOCK.md`.

### 2.3 A related documentation gap

CDC codebook pages document five variables that do not exist in the actual
files: `ALQ154`, `DIQ065`, `DIQ159`, `DIQ229`, `DIQ295`. The codebook is a
superset of the file. None of our locked variables is affected, but it confirms
that codebook verification alone is insufficient.

---

## 3. Attrition

| Step | 2011-2012 | 2013-2014 | Combined |
|---|---|---|---|
| Aged 60+, MEC examined | 1,687 | 1,785 | 3,472 |
| ... with >= 3 of 4 cognitive scores | 1,454 | 1,670 | **3,124** |
| ... and all 5 blood metals | 1,388 | 806 | 2,194 |
| ... and serum B12 | 1,334 | 786 | 2,120 |

Identical to the Phase 0 figures, computed by an independent implementation.
The `_G` versus `_H` divergence at the metals step is the `PBCD_H` one-half
subsample, not nonresponse.

### Reserved codes converted to NaN

Per variable, verified against each variable's own codebook. Totals across both
cycles: `BPQ080` 33, `DPQ` items 46 across all nine, `MCQ160F` 7, `DMDEDUC2` 7,
`ALQ101` 7, `ALQ120Q` 6, `BPQ020` 7, `ALQ130` 3, `SMQ020` 3, `DIQ010` 2.

`ALQ130` uses **777/999**, not 7/9, and its valid range is 1 to 82. The CFQ
score variables have **no reserved codes at all**: `CFDCST1` ranges 0 to 10, so
7 and 9 are legitimate scores. A blanket rule would have corrupted both.

### Below detection limit, within the 60+ cohort

| Analyte | Percent below LOD |
|---|---|
| Lead | 0.0% |
| Cadmium | 5.2% |
| Total mercury | 5.7% |
| Selenium | 0.0% |
| Manganese | 0.0% |

These are lower than the file-wide figures reported in Phase 0 (cadmium 29%,
mercury 26%) because those covered all ages. Cadmium accumulates with age and
smoking, so the 60+ subset sits well above the detection limit. Both figures are
correct for their respective denominators.

---

## 4. The outcome

Composite of four z-scored tests, averaged with at least 3 of 4 present, lowest
quartile taken as the label. Terminology is **low cognitive performance**.

| Metric | Value |
|---|---|
| Eligible for the outcome | 3,124 |
| Prevalence, primary quartile cut | 0.2500 |
| Prevalence at 20th percentile | 0.2001 |
| Prevalence at 10th percentile | 0.1002 |
| Composite quartile cut (z) | -0.5428 |
| Cronbach alpha across the four z-scores | **0.795** |

Inter-test correlations:

| | CERAD imm | CERAD del | Fluency | DSST |
|---|---|---|---|---|
| CERAD immediate | 1.000 | 0.743 | 0.423 | 0.477 |
| CERAD delayed | 0.743 | 1.000 | 0.396 | 0.466 |
| Animal fluency | 0.423 | 0.396 | 1.000 | 0.510 |
| DSST | 0.477 | 0.466 | 0.510 | 1.000 |

Alpha of 0.795 is acceptable for a four-test composite. The CERAD
immediate-to-delayed correlation of 0.743 is expected: they are two scores from
one administration.

### The "3 of 4" rule question is settled

Phase 0 flagged that `CFASTAT` counts three instruments rather than four, so the
brief's ">= 3 of 4 scores" rule is not the same as ">= 2 of 3 instruments".
Both were computed:

| Rule | Eligible |
|---|---|
| Primary, >= 3 of 4 scores | 3,124 |
| Alternative, >= 2 of 3 instruments | 3,137 |
| **Classified differently** | **13** |

Thirteen participants out of 3,124, or 0.4%. **The concern is immaterial.**
Recommend keeping the brief's pre-specified rule and noting the comparison in
one sentence in the methods.

### Items for the DSST sensitivity analysis

Among the 3,124 labelled participants, DSST was not completed by 52 people:
27 refused, 18 physical limitation, 6 communication problem, 1 other. The brief
requires a sensitivity analysis coding "unable to complete" as impaired, and
these are the participants it applies to.

Test language: 2,733 English, 322 Spanish, 69 Asian language. The brief
anticipated only English and Spanish, so the English-only sensitivity analysis
should exclude both non-English groups rather than only Spanish.

---

## 5. The decision that blocks modeling

**The four nested models do not currently share a sample, so delta-AUC across
them would not be comparable.**

| Model | Features | Complete cases | With covariates |
|---|---|---|---|
| M0, demographics | 5 | 2,849 | 2,689 |
| M1, + metals | 10 | 1,993 | 1,899 |
| M2, + nutritional | 19 | 2,616 | 2,481 |
| M3, all | 24 | 1,877 | **1,789** |

Delta-AUC(M3 - M0) is the primary result of this paper. If M0 is fitted on 2,689
people and M3 on 1,789, the difference confounds model content with sample
composition and the headline number is uninterpretable. **All four models must be
fitted and evaluated on identical rows.** Two ways to achieve that:

**Option A. Common complete-case sample, n = 1,789.**
Fit every model on the rows where all M3 features are observed. No exposure is
ever imputed. Delta-AUC is comparable by construction. Costs 1,335 labelled
participants.

**Option B. Multiple imputation inside the folds, n = 3,124.**
Pre-specified in the brief's cleaning plan. Retains the full labelled sample, but
requires imputing the metals block for 36% of participants, and those are the
primary exposure of interest.

### Recommendation: Option A as primary, Option B as the pre-specified sensitivity

Three reasons.

**The dominant exclusion is random by design.** 930 of the 1,335 exclusions are
missing metals, and most of those are the `PBCD_H` one-half subsample, which is a
random draw. That is missing-completely-at-random by construction, the benign
case. Cycle composition shows it plainly: 77.2% of 2011-2012 participants are
retained against 39.9% of 2013-2014.

**n = 1,789 is inside the planned range and adequately powered.** The brief
planned for 1,400 to 1,900. There are 470 events at 24 features, so 19.6 events
per feature, comfortably inside conventional guidance.

**Imputing the exposure is the weaker choice.** Imputing 36% of the primary
exposure to then ask how much that exposure adds to prediction invites an
obvious reviewer objection.

The restriction is mildly selective and this belongs in the limitations:

| Characteristic | Included (1,789) | Excluded (1,335) | Difference |
|---|---|---|---|
| Age, mean | 69.37 | 70.10 | -0.73 |
| Female, % | 50.75 | 52.51 | -1.75 |
| Low cognitive performance, % | 24.09 | 26.22 | -2.13 |
| Diabetes, % | 27.45 | 30.08 | -2.64 |
| PHQ-9, mean | 3.01 | 3.56 | -0.55 |
| Education (1 to 5), mean | 3.37 | 3.25 | +0.12 |

Excluded participants are slightly older and slightly worse off on every axis,
but all differences are under 3 percentage points. Option B as a sensitivity
analysis is exactly the check on this, which is why it stays pre-specified rather
than being dropped.

---

## 6. Still open, both cheap

**Serum iron, `LBXSIR`.** The brief excludes it as discontinued after 2009-2010.
That is wrong: it is in `BIOPRO`, both cycles, full sample. `BIOPRO` is already
merged, so adding it is one column rather than a re-clean. Include it or not?

**Label definition uses pooled-sample quantiles.** A held-out participant's label
depends on the whole sample's distribution. This is definitional rather than
predictive leakage, since the outcome is explicitly relative ("lowest quartile of
this population"), and defining it per-fold would make the target move between
folds. It should be stated explicitly in the pre-registration so a reviewer sees
it was a deliberate choice.

---

## 7. What the pre-registration needs to fix in writing

Per the brief, dated before any outcome-predictor relationship is examined:

1. Primary outcome: composite z-score, lowest quartile. Settled.
2. Primary metric: delta-AUC(M3 - M0), bootstrap 95% CI. Settled.
3. Meaningful-difference threshold: delta-AUC >= 0.02. Settled.
4. Primary model class: L2-penalized logistic regression. Settled.
5. CV scheme: stratified 10-fold, repeated 5x. Settled.
6. **Analytic sample: Option A or Option B above. Open.**
7. **Serum iron in or out. Open.**
8. The pooled-quantile label definition, stated explicitly.
9. Every random seed, and pinned versions in `requirements.txt`.

---

## 8. Status

Phases 1 and 2 are complete and reproducible. **Modeling has not started and will
not start** until items 6 and 7 are decided and the pre-registration is dated.
