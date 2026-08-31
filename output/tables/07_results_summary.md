# Results summary

**2026-08-31.** Phases 3 to 6 complete. All analyses were pre-specified in
`PREREGISTRATION.md`, dated before any outcome-predictor relationship was
examined. Nothing below was selected after seeing a result.

Reproduce with `python3 src/03_model.py && python3 src/04_evaluate.py &&
python3 src/05_interpret.py && python3 src/06_sensitivity.py`.

---

## 1. The primary result

**delta-AUC(M3 - M0) = -0.0019, bootstrap 95% CI [-0.0108, 0.0071].**

Adding five blood metals and fifteen nutritional and metabolic biomarkers to a
demographics-only model does not improve identification of low cognitive
performance in US adults aged 60+.

The CI includes zero, so H1 is not supported and H0 is retained. More
informatively, the **upper bound of 0.0071 lies well below the pre-specified
meaningful-difference threshold of 0.02**. This is therefore a precise null
rather than an underpowered one: the data rule out an improvement large enough
to matter, which is a stronger statement than a failure to reach significance.
That distinction is only available because the threshold was fixed in advance.

| Contrast, L2-penalized logistic | delta-AUC | 95% CI | Excludes 0 | Exceeds 0.02 |
|---|---|---|---|---|
| M1 - M0, metals block | -0.0015 | [-0.0052, 0.0023] | no | no |
| M2 - M0, nutritional block | +0.0011 | [-0.0067, 0.0100] | no | no |
| **M3 - M0, both blocks** | **-0.0019** | **[-0.0108, 0.0071]** | **no** | **no** |
| M3 - M0+, versus clinical baseline | -0.0158 | [-0.0295, -0.0033] | **yes** | no |

H3 is not supported: neither block contributes, so the question of whether they
contribute non-redundantly does not arise.

---

## 2. The biomarker panel is worse than a clinical questionnaire

The one contrast whose CI excludes zero is negative. **M3 performs
significantly worse than M0+**, the pre-specified secondary baseline of
demographics plus routinely recorded clinical covariates (BMI, smoking, alcohol,
PHQ-9 depression, stroke, diabetes, hypertension, high cholesterol).

This holds across all three algorithms:

| Algorithm | delta-AUC(M3 - M0+) | 95% CI |
|---|---|---|
| Logistic | -0.0158 | [-0.0295, -0.0033] |
| Random forest | -0.0197 | [-0.0338, -0.0055] |
| XGBoost | -0.0230 | [-0.0385, -0.0063] |

A twenty-analyte laboratory panel is outperformed by eight questions a clinician
can ask without drawing blood. This is a sharper and more actionable finding
than the primary null.

---

## 3. Discrimination and calibration

Mean out-of-fold across 5 repeats of stratified 10-fold CV, n = 1,784.

| Spec | Algorithm | AUC | AUPRC | Brier | Calib. slope | Calib. intercept |
|---|---|---|---|---|---|---|
| M0 | logistic | 0.7884 | 0.5471 | 0.1459 | 1.088 | 0.001 |
| M0 | random forest | 0.7843 | 0.5363 | 0.1466 | 1.148 | 0.004 |
| M0 | xgboost | 0.7845 | 0.5399 | 0.1470 | 0.898 | 0.004 |
| M1 | logistic | 0.7868 | 0.5456 | 0.1465 | 1.069 | 0.002 |
| M2 | logistic | 0.7895 | 0.5420 | 0.1461 | 1.026 | 0.002 |
| M3 | logistic | 0.7865 | 0.5392 | 0.1470 | 1.004 | 0.002 |
| M3 | random forest | 0.7806 | 0.5384 | 0.1501 | 1.410 | -0.012 |
| M3 | xgboost | 0.7779 | 0.5201 | 0.1497 | 0.904 | 0.024 |
| **M0+** | **logistic** | **0.8023** | **0.5618** | **0.1423** | **1.042** | **0.003** |

Every model discriminates reasonably (AUC around 0.78 to 0.80), and essentially
all of that comes from age, education and income.

Calibration is good throughout for logistic (slope near 1, intercept near 0).
Random forest is consistently over-dispersed (slope up to 1.41) and XGBoost
slightly under (slope around 0.90), so the simplest model is best calibrated as
well as best discriminating.

---

## 4. H2: nonlinear learners do not win

| Contrast on M3 | delta-AUC | 95% CI |
|---|---|---|
| Random forest - logistic | -0.0059 | [-0.0175, 0.0060] |
| XGBoost - logistic | -0.0086 | [-0.0187, 0.0007] |

H2 is not supported. Penalized logistic regression matches or beats both
flexible learners on every specification. This is the expected outcome at
n = 1,784 with 25 features and is consistent with prior findings in
low-dimensional clinical tabular data.

The rationale behind H2 also fails on its own terms. Partial dependence for
selenium and manganese, the two exposures expected to show U-shaped
exposure-response, shows no such shape: the extremum sits near an end of the
range rather than in the middle, and the total swing in predicted probability is
about 0.05 for both.

---

## 5. Clinical utility: decision-curve analysis

Net benefit for M3 against M0 across threshold probabilities from 0.05 to 0.60.

- M3 exceeds M0 at **21 of 56 thresholds**, which is indistinguishable from
  chance.
- Maximum net-benefit gain of M3 over M0 is **+0.0059**, negligible.
- M0+ exceeds M0 at **52 of 56 thresholds**.

There is no plausible decision threshold at which adding the biomarker panel
would change a decision. The clinical-utility claim is null on its own terms,
not merely on discrimination.

---

## 6. Mixture-method benchmark, the IEEE contribution

Quantile g-computation, reimplemented in Python with training-fold quantile
cutpoints so it fits inside the CV loop without leakage.

| Model | Cross-validated AUC |
|---|---|
| Demographics only (M0) | 0.7884 |
| **Quantile g-computation, metals mixture + demographics** | **0.7874** |
| M1, metals as individual features + demographics | 0.7868 |

**psi = -0.1162** joint mixture log-odds per simultaneous one-quantile increase.
Component weights: cadmium 0.820 and lead 0.180 in the positive direction;
mercury -0.376, manganese -0.365 and selenium -0.260 in the negative.

The mixture-modelling approach that dominates this literature therefore performs
no better than demographics alone, and no better than entering the same metals
as ordinary features. This is the framework contribution made concrete: a method
designed for inferential decomposition of a mixture confers no predictive
advantage when evaluated on predictive criteria.

BKMR was excluded in advance (convergence fragility for binary outcomes, and
cost inside 50 folds). WQS was deferred and, given that the metals block carries
no predictive signal, there is no basis for adding it.

---

## 7. Feature importance and rank stability

Bootstrapped SHAP over 200 resamples of the M3 XGBoost model.

| Feature | Median rank | 95% rank interval | In top 5 |
|---|---|---|---|
| Education (`DMDEDUC2`) | 1 | 1 to 2 | 100% |
| Age (`RIDAGEYR`) | 2 | 1 to 2 | 100% |
| Income to poverty (`INDFMPIR`) | 3 | 3 to 5 | 99% |
| NLR | 5 | 3 to 19 | 51% |
| eGFR | 7 | 4 to 19 | 34% |
| HDL | 7 | 4 to 19 | 35% |
| B12 | 8 | 4 to 19 | 25% |
| Cadmium | 14 | 5 to 24 | 4.5% |
| Selenium | 14 | 6 to 23 | 2.5% |

The three demographics are rank-stable to the point of determinism. Every
biomarker swings across a 15 to 20 rank interval between resamples.

That instability is itself a result. Single-run SHAP rankings over correlated
biomarkers are not reproducible, which is a direct methodological caution for a
literature that routinely reports them without resampling.

---

## 8. Sensitivity analyses

All six were pre-specified. The null holds in every one.

| Analysis | n | delta-AUC(M3 - M0) | 95% CI |
|---|---|---|---|
| Primary (reference) | 1,784 | -0.0020 | [-0.0103, 0.0066] |
| Cutoff at 20th percentile | 1,784 | -0.0019 | [-0.0130, 0.0092] |
| Cutoff at 10th percentile | 1,784 | -0.0023 | [-0.0200, 0.0153] |
| DSST "unable" coded low (25 recoded) | 1,784 | -0.0020 | [-0.0105, 0.0063] |
| English-only administration | 1,575 | -0.0066 | [-0.0159, 0.0028] |
| **MICE on the full labelled sample** | **3,124** | **+0.0015** | **[-0.0030, 0.0063]** |

The multiple-imputation analysis matters most. It is Option B, the alternative
we did not adopt as primary, run on the full labelled sample with imputation
fitted inside each fold. It produces the **tightest CI of any analysis**,
[-0.0030, 0.0063], and remains null. The choice of complete-case sampling
therefore did not create the null result, which forecloses the most obvious
reviewer objection to the sample decision.

**Leave-one-block-out.**

| Dropped block | delta-AUC vs full M3 | 95% CI |
|---|---|---|
| Without metals | -0.0028 | [-0.0051, -0.0004] |
| Without nutritional | -0.0002 | [-0.0081, 0.0078] |

Removing the metals block slightly **improves** discrimination, with a CI
excluding zero. The metals contribute noise rather than signal.

**Continuous outcome.** Cross-validated R-squared for the composite z-score is
0.3825 for M0 and 0.3908 for M3, a gain of **+0.0083**. Reported for
completeness and because it is the one result pointing marginally in the
positive direction: on the continuous scale the biomarkers explain about
0.8% additional variance. That does not translate into discrimination for the
binary outcome, and it is far too small to alter the conclusion.

---

## 9. What this means

Against the brief's section 6 decision framework, this is **Scenario C**
(null on the primary axis) combined with **Scenario E** (flexible learners do
not beat penalized regression).

Both were pre-written as legitimate, publishable outcomes. Scenario C is
described there as "the cautionary result, and arguably the most interesting
one", with the framing: seven published studies report significant associations
between these biomarkers and cognition in this exact population, and translating
those associations into individual-level prediction adds essentially nothing
beyond age, education and income.

Three findings strengthen that message beyond a bare null:

1. The null is **precise**, not underpowered. The CI excludes the pre-specified
   meaningful difference.
2. The biomarker panel is **significantly worse** than eight routinely collected
   clinical covariates.
3. The **mixture-modelling method** used throughout this literature confers no
   predictive advantage either, and single-run SHAP rankings over these
   biomarkers are not reproducible across resamples.

**No causal language applies.** These data are cross-sectional. Nothing here
says any biomarker does or does not affect cognition. The finding is strictly
about predictive utility, and about the gap between statistical association and
individual-level prediction.

The outcome throughout is **low cognitive performance**, never cognitive
impairment.

### Consequence for venue

The brief's own decision rule routes Scenario C to Diagnostic and Prognostic
Research, Journal of Clinical Epidemiology, or PLOS ONE, and notes that
Scenario E "weakens an IEEE framing". That tension is now real and is a decision
for both authors.

The counter-argument for keeping the IEEE framing: the contribution was
reframed as a **reusable evaluation protocol** for testing whether reported
epidemiological associations confer predictive utility. A precise null arguably
demonstrates that protocol better than a positive result would, and sections 6
and 7 above (the mixture-method benchmark and the rank-stability analysis) are
genuine computational content rather than a standard classifier comparison.
