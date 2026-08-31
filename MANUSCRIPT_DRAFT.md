# Methods and Results: working draft

Draft prose for the Methods and Results sections, written to be edited directly
into the manuscript rather than summarised again. Per the division of labour in
`PROJECT_BRIEF.md` section 12 these two sections are the modelling lead's; the
Introduction and Discussion are the clinical lead's.

Every number here traces to a file in `output/tables/`. Nothing is rounded
differently from its source.

Two conventions held throughout, both deliberate:

- The outcome is **low cognitive performance**. NHANES contains no clinical
  diagnosis, so *cognitive impairment* is never used.
- The design is cross-sectional, so no causal verb appears. Not *leads to*,
  *causes*, *improves*, *protects against*, or *reduces risk of*.

---

# Methods

## Study population and design

We analysed the National Health and Nutrition Examination Survey (NHANES) cycles
2011-2012 and 2013-2014, a complex multistage probability sample of the
non-institutionalised civilian US population. Analyses were restricted to
participants aged 60 years or older who completed the Mobile Examination Centre
visit, the population to whom the cognitive battery was administered. Because two
two-year cycles were pooled, the examination weight `WTMEC2YR` was halved, and the
variance strata and primary sampling units were carried through every merge.

The reporting follows TRIPOD+AI. The completed checklist is provided as a
supplementary file.

## Outcome

Cognitive performance was measured with four scores from three instruments: the
Consortium to Establish a Registry for Alzheimer's Disease (CERAD) word-list
learning task, scored as the sum of three immediate-recall trials and separately
as delayed recall; a one-minute animal fluency task; and the Digit Symbol
Substitution Test from the Wechsler Adult Intelligence Scale III.

Each score was standardised within the pooled sample aged 60 and over. A composite
was formed as the mean of the available standardised scores, requiring at least
three of four to be present, and the lowest quartile of that composite defined
**low cognitive performance**. Internal consistency across the four standardised
scores was acceptable (Cronbach alpha 0.795); the correlation between CERAD
immediate and delayed recall was 0.743, as expected for two scores from one
administration, while correlations among the three instruments ranged from 0.40 to
0.51.

The composite is defined against pooled-sample quantiles, so a participant's label
depends on the distribution of the whole sample. This is a property of the
definition rather than of the prediction procedure: the outcome is explicitly
relative, and defining it within folds would make the target itself vary between
folds. The choice was pre-specified.

## Predictors

Predictors were organised into three blocks fixed in writing before any analysis.

**Block 1, demographics.** Age, sex, race and Hispanic origin, education, and the
family income-to-poverty ratio.

**Block 2, blood metals.** Lead, cadmium, total mercury, selenium and manganese,
measured by inductively coupled plasma mass spectrometry in whole blood, each
entered on the natural log scale. Values below the limit of detection are
substituted by NHANES with the limit divided by the square root of two and flagged;
within the analytic sample this affected 5.2% of cadmium and 5.7% of mercury
measurements, and no lead, selenium or manganese measurements.

**Block 3, nutritional and metabolic biomarkers.** Serum vitamin B12,
methylmalonic acid, serum total folate, red blood cell folate, 25-hydroxyvitamin
D, glycohaemoglobin, HDL cholesterol, total cholesterol, triglycerides, albumin,
serum iron, estimated glomerular filtration rate (CKD-EPI 2021, without the race
coefficient), and three inflammation indices derived from the complete blood
count: the neutrophil-to-lymphocyte ratio, the platelet-to-lymphocyte ratio, and
the systemic immune-inflammation index. Vitamin B12, methylmalonic acid and the
systemic immune-inflammation index were log-transformed.

**Covariates.** Body mass index, smoking status, average alcoholic drinks per day,
the nine-item Patient Health Questionnaire depression score, and self-reported
stroke, diabetes, hypertension and high cholesterol. These were not entered in the
primary nested comparison, which is stated against demographics, but form a
pre-specified secondary baseline described below.

## Data preparation

Reserved codes for refusal and non-response were converted to missing on a
per-variable basis against each variable's own codebook rather than by a blanket
rule, because the applicable codes differ: alcohol quantity uses 777 and 999 over a
valid range of 1 to 82, while the cognitive score variables carry no reserved codes
at all and a blanket rule would have deleted valid scores of 7 and 9.

Two data properties required specific handling and are noted because both fail
silently. First, NHANES SAS transport files encode zero as a denormalised
floating-point value rather than as zero, in 330,496 cells across the files used
here, with no true zero present anywhere; any equality test against zero therefore
matches nothing until this is normalised. Second, alcohol consumption is governed
by two nested skip patterns: the screening question refers to any one year of life
rather than the past year, and the quantity item is skipped whenever the frequency
item is zero. Both indicate zero consumption rather than unknown consumption, and
403 participants were affected.

Derived quantities used in modelling (log transforms, ratios, estimated glomerular
filtration rate, depression score) are row-wise functions with no fitted
parameters and were computed before splitting; all fitted transformations are
described below.

## Models

Four nested models were specified in advance:

- **M0**, demographics alone, the benchmark against which everything is measured
- **M1**, demographics plus blood metals
- **M2**, demographics plus nutritional and metabolic biomarkers
- **M3**, demographics plus both biomarker blocks

A fifth, pre-specified secondary model **M0+** comprised demographics plus the
covariates listed above, representing information a clinician could record without
a laboratory.

Three algorithms were fitted to each specification: L2-penalized logistic
regression as the pre-specified primary model class, random forest, and gradient
boosting (XGBoost). Multilayer perceptron and k-nearest-neighbour models were
excluded in advance, as they were not expected to be competitive at this sample
size.

## Analytic sample

All models were fitted and evaluated on a single locked set of rows, those with
every Block 1 to 3 predictor and every covariate observed. Fitting nested models on
different samples would confound model content with sample composition and render
the primary contrast uninterpretable. Nothing was imputed in the primary analysis,
so the exposures of interest were never fabricated.

## Evaluation

Models were evaluated by stratified 10-fold cross-validation repeated five times.
Every preprocessing step (imputation, standardisation, one-hot encoding) and all
hyperparameter selection were performed inside the training folds using pipeline
objects constructed within the cross-validation loop; no transformation was fitted
on data used for evaluation. This was verified by an automated audit that refits a
fold and asserts that the fitted standardisation parameters equal the training-fold
values and not the full-sample values; the audit fails the analysis rather than
issuing a warning, and it passed.

Discrimination was summarised by the area under the receiver operating
characteristic curve (AUC) and the area under the precision-recall curve, overall
accuracy being uninformative at this prevalence. Calibration was summarised by the
calibration slope and the calibration-in-the-large intercept, the latter obtained
from the offset model rather than by the common shortcut of subtracting the mean
linear predictor from an intercept-only fit. Clinical utility was assessed by
decision-curve analysis across threshold probabilities from 0.05 to 0.60.

The pre-specified primary outcome measure was **delta-AUC between M3 and M0**, with
a 95% confidence interval from 2,000 bootstrap resamples of participants, scoring
both models on the same resampled rows so that the comparison remains paired. A
difference of at least 0.02 in AUC was declared in advance to be the smallest
meaningful improvement.

## Mixture-modelling benchmark

To compare the methods used in environmental epidemiology against machine learning
on predictive rather than inferential criteria, quantile g-computation was
reimplemented in Python. Exposures are quantised into quartiles using cutpoints
learned on the training fold and applied unchanged to held-out data, matching the
behaviour of the R implementation and preserving fold isolation. The joint mixture
effect is the sum of the exposure coefficients, and component weights are the
signed coefficients normalised within direction.

Bayesian kernel machine regression was excluded in advance: a 2026 simulation study
of its probit implementation reported that only 30 of 431 fits met standard
convergence criteria for binary outcomes, and refitting a Markov chain Monte Carlo
model inside 50 folds was not feasible within the analysis budget. Weighted
quantile sum regression was deferred, its package partitioning data internally in a
way that conflicts with an external cross-validation scheme.

## Interpretation

SHAP values were computed for the gradient-boosted M3 model, with feature rankings
recomputed across 200 bootstrap resamples to characterise rank stability, since
single-run rankings over correlated predictors are not reliable. Partial dependence
was examined for selenium and manganese, the two exposures for which non-monotonic
exposure-response was anticipated.

## Sensitivity analyses

Six analyses were specified in advance: outcome cutoffs at the 10th and 20th
percentiles; the continuous composite as a regression outcome; recoding
participants unable to complete the Digit Symbol Substitution Test as having low
performance; restriction to English-language administration; multiple imputation by
chained equations on the full labelled sample with imputation fitted inside folds;
and a leave-one-block-out comparison.

## Software and reproducibility

Analyses used Python 3.12.2 with pandas 3.0.3, scikit-learn 1.8.0, XGBoost 3.0.0,
SciPy 1.13.0 and SHAP 0.52.0. All random seeds were fixed at a single master value
and package versions are pinned. The complete pipeline, from file acquisition
through figures, is available as seven independently runnable scripts.

---

# Results

## Participants

Of 19,931 participants in the two cycles, 3,632 were aged 60 or older and 3,472
had completed the examination visit. Of these, 3,124 had at least three of four
cognitive scores and received an outcome label. Requiring complete data on all
predictors and covariates yielded the analytic sample of **1,784 participants, of
whom 431 (24.2%) met the definition of low cognitive performance**. The weighted
population represented was 59.7 million.

The 2013-2014 cycle contributed proportionally fewer participants (661) than
2011-2012 (1,123), because blood metals in that cycle were measured in a one-half
random subsample rather than in all examined participants.

Participants excluded for incomplete data were slightly older (mean 70.1 against
69.4 years) and slightly more likely to meet the outcome definition (26.2% against
24.1%), with all differences under three percentage points.

## Discrimination

Demographics alone discriminated moderately well (AUC 0.7884). Adding blood metals
(M1, 0.7868), nutritional biomarkers (M2, 0.7895), or both (M3, 0.7865) produced
no material change. The clinical baseline M0+ reached 0.8023.

**The primary result was delta-AUC(M3 - M0) = -0.0019, with a bootstrap 95%
confidence interval of [-0.0108, 0.0071].** The interval includes zero, so the
primary hypothesis was not supported. Its upper bound of 0.0071 falls below the
0.02 threshold declared in advance, so the analysis excludes an improvement of the
magnitude specified as meaningful rather than merely failing to detect one.

Neither block contributed individually: delta-AUC was -0.0015 [-0.0052, 0.0023]
for metals and 0.0011 [-0.0067, 0.0100] for nutritional biomarkers. The question of
non-redundancy between blocks does not arise.

The one contrast whose interval excluded zero was negative. **M3 performed worse
than the clinical baseline M0+**, by -0.0158 [-0.0295, -0.0033] under logistic
regression, -0.0197 [-0.0338, -0.0055] under random forest and -0.0230 [-0.0385,
-0.0063] under gradient boosting.

## Algorithm comparison

Penalized logistic regression matched or exceeded both flexible learners at every
specification. On M3, random forest differed by -0.0059 [-0.0175, 0.0060] and
gradient boosting by -0.0086 [-0.0187, 0.0007]. The secondary hypothesis that
nonlinear learners would outperform penalized regression was not supported.

Logistic regression was also the best calibrated (slope 1.004 on M3, intercept
0.002), whereas random forest was over-dispersed (slope 1.410) and gradient
boosting slightly under-dispersed (slope 0.904).

## Clinical utility

Decision-curve analysis showed no threshold probability at which M3 offered
meaningful net benefit over M0. M3 exceeded M0 at 21 of 56 thresholds examined,
with a maximum gain in net benefit of 0.0059. M0+ exceeded M0 at 52 of 56
thresholds.

## Mixture-modelling benchmark

Quantile g-computation applied to the five-metal mixture with demographic
adjustment achieved a cross-validated AUC of 0.7874, against 0.7884 for
demographics alone and 0.7868 for the same metals entered as individual features.
The joint mixture effect was -0.1162 in log-odds per simultaneous one-quartile
increase, with cadmium carrying 0.820 of the positive weight and mercury,
manganese and selenium loading negatively. A method designed for inferential
decomposition of a mixture therefore conferred no predictive advantage over either
comparator.

## Feature importance

Across 200 bootstrap resamples, education, age and the income-to-poverty ratio
occupied the top three ranks with medians of 1, 2 and 3 and appeared in the top
five in 100%, 100% and 99% of resamples respectively. The highest-ranked biomarker
was the neutrophil-to-lymphocyte ratio, with a median rank of 5 but a 95% interval
spanning ranks 3 to 19 and appearing in the top five in 51% of resamples. Cadmium
and selenium had median ranks of 14 and appeared in the top five in 4.5% and 2.5%
of resamples. Biomarker rankings were therefore not stable across resamples, while
demographic rankings were effectively deterministic.

Partial dependence for selenium and manganese showed no U-shaped
exposure-response; predicted probability varied by approximately 0.05 across the
observed range of each.

## Sensitivity analyses

The primary finding was unchanged in every pre-specified sensitivity analysis.
Delta-AUC(M3 - M0) was -0.0019 [-0.0130, 0.0092] at the 20th-percentile cutoff,
-0.0023 [-0.0200, 0.0153] at the 10th, -0.0020 [-0.0105, 0.0063] when
non-completion of the Digit Symbol Substitution Test was coded as low performance,
and -0.0066 [-0.0159, 0.0028] when restricted to English-language administration.

Multiple imputation on the full labelled sample of 3,124 gave 0.0015 [-0.0030,
0.0063], the narrowest interval obtained in any analysis and still consistent with
no difference, indicating that the complete-case restriction did not produce the
result.

Leave-one-block-out analysis showed that removing the metals block slightly
improved discrimination (-0.0028 [-0.0051, -0.0004]), while removing the
nutritional block had no effect (-0.0002 [-0.0081, 0.0078]).

With the continuous composite as the outcome, cross-validated R-squared rose from
0.3825 for M0 to 0.3908 for M3, a difference of 0.0083. This is the only analysis
in which the biomarker blocks contributed in the expected direction, and the
magnitude corresponds to under one percent of additional variance explained.

---

# Notes for the co-author

Three things to keep in view while drafting the Introduction and Discussion.

**The claim is about prediction, not about biology.** Nothing here demonstrates
that any biomarker is unrelated to cognition. The published associations may all be
correct. The finding is that they do not translate into the ability to identify
which individuals have low cognitive performance, once age, education and income
are known. That distinction is the paper.

**The null is precise, and this is the strongest sentence available.** Because the
0.02 threshold was fixed before the data were modelled, the confidence interval
excludes a meaningful improvement rather than merely failing to reach
significance. Phrase this carefully; it is the difference between a null result and
an uninformative one.

**The M0+ comparison is the most quotable result.** A twenty-analyte laboratory
panel was outperformed by eight items of routine clinical history, consistently and
with intervals excluding zero. It converts an absence of evidence into a concrete
statement about what actually carries information.

**Limitations to state plainly:** the design is cross-sectional; the complete-case
restriction is mildly non-random, though the dominant exclusion mechanism is a
random subsample by design; age is top-coded at 80, compressing its range; there is
no external validation cohort; no subgroup fairness audit was pre-specified; and
serum copper and zinc were excluded because that assay was performed on a one-third
subsample.
