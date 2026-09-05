# Manuscript draft

Draft prose for all four sections, written to be edited directly into the
manuscript rather than summarised again. Per the division of labour in
`PROJECT_BRIEF.md` section 12, Methods and Results are the modelling lead's
(Neil); Introduction and Discussion are the clinical and framing lead's
(Shreyan), added 2026-09-05 following the skeleton in `WRITING_PACK.tex`,
updated for the Diagnostic and Prognostic Research framing and the
literature review in `LITERATURE_REVIEW.md`.

Every number in Methods and Results traces to a file in `output/tables/`.
Nothing is rounded differently from its source. Every citation in
Introduction and Discussion is verified in `LITERATURE_REVIEW.md`.

---

# Title

Reported biomarker-cognition associations do not translate into predictive
utility: a pre-registered analysis of NHANES 2011-2014.

Decided 2026-09-05 by Shreyan Kancharla, from the three options in
`WRITING_PACK.tex`. Chosen over the alternatives because it is the only
option naming the population, dataset, cycles and design (pre-registered)
together, and because it matches Diagnostic and Prognostic Research's own
stated title convention of including the study design after a colon (e.g.
"A versus B in the treatment of C: a randomized controlled trial" — checked
against the journal's submission guidelines).

## Authors and title page

Shreyan Kancharla¹\*, Neil Patel²\*

\* These authors contributed equally to this work and share first
authorship, decided 2026-09-05.

Corresponding author: Shreyan Kancharla, shkancharla@davidson.edu,
ORCID: 0009-0009-8654-110X (verified 2026-09-05).

¹ Davidson College, Davidson, NC, USA.

² **[Neil's institutional affiliation and ORCID still needed — ask when
he's back from travel. DPR's title page requires a full institutional
address for every author.]**

Two conventions held throughout, both deliberate:

- The outcome is **low cognitive performance**. NHANES contains no clinical
  diagnosis, so *cognitive impairment* is never used.
- The design is cross-sectional, so no causal verb appears. Not *leads to*,
  *causes*, *improves*, *protects against*, or *reduces risk of*.

---

# Abstract

**Background.** Multiple studies report associations between blood metals,
nutritional biomarkers and cognitive performance among US adults aged 60 and
over in NHANES 2011-2014. None isolates the biomarkers' predictive
contribution beyond demographics, with calibration and decision-curve
analysis.

**Methods.** We analysed NHANES 2011-2012 and 2013-2014, restricted to
examined participants aged 60 and over. Low cognitive performance was
defined as the lowest quartile of a composite z-score from CERAD immediate
and delayed recall, animal fluency, and the Digit Symbol Substitution Test.
Four nested specifications were fixed in advance: demographics (M0);
demographics plus five blood metals (M1); demographics plus fifteen
nutritional and metabolic biomarkers (M2); and both blocks (M3). A
pre-specified secondary baseline (M0+) added eight routinely recorded
clinical covariates. Three algorithms (L2-penalized logistic regression,
random forest, gradient boosting) were evaluated by stratified 10-fold
cross-validation repeated five times, with preprocessing and tuning
performed inside training folds. The pre-specified primary measure was
delta-AUC(M3 - M0) with a 2,000-sample paired bootstrap interval; a
difference of 0.02 was declared in advance as the smallest meaningful
improvement. Reporting follows TRIPOD+AI.

**Results.** Of 3,124 participants with an outcome label, 1,784 had complete
predictor data, of whom 431 (24.2%) met the definition of low cognitive
performance. Demographics alone reached an AUC of 0.788. Delta-AUC(M3 - M0)
was -0.0019 (95% CI -0.0108 to 0.0071), with the upper bound below the
pre-specified 0.02 threshold; neither biomarker block contributed alone. M3
performed worse than the clinical baseline M0+ (delta-AUC -0.0158, 95% CI
-0.0295 to -0.0033) across all three algorithms, and decision-curve analysis
showed no net benefit at any threshold. Quantile
g-computation on the metal mixture matched demographics alone (AUC 0.7874).
The null persisted across all six pre-specified sensitivity analyses,
including multiple imputation on the full sample (n = 3,124; delta-AUC
0.0015, 95% CI -0.0030 to 0.0063).

**Conclusions.** Reported biomarker-cognition associations did not translate
into individual-level predictive utility beyond age, education and income,
and a twenty-analyte laboratory panel was outperformed by eight items of
routine clinical history. Because the confidence interval excludes the
improvement specified in advance as meaningful, this is a precise null
rather than an inconclusive one.

---

# Keywords

Cognitive performance; biomarkers; blood metals; prediction model;
NHANES; older adults; TRIPOD+AI; decision-curve analysis; pre-registration;
machine learning

Eight to ten, per DPR's requirement of three to ten. Open to trimming or
substitution — flag if any of these do not read as representative.

---

# Introduction

Low cognitive performance in older adults is examined routinely against blood
metals and nutritional biomarkers in the National Health and Nutrition
Examination Survey (NHANES), and panels of these analytes are proposed
periodically as adjuncts to demographic risk assessment. Every study making
that case for the population and cycles examined here, however, reports only
a regression coefficient or an odds ratio. None reports whether the
association translates into the ability to identify, at the level of one
participant, who has low cognitive performance, and none benchmarks that
ability against what is already known from a person's age, sex, race and
Hispanic origin, education and family income.

Seven studies span the NHANES 2011-2014 cycles and the population aged 60
years or older analysed here, and none closes that gap. In a preprint, Wang
et al. examined blood lead, cadmium, mercury, selenium and manganese in 1,460
participants using linear regression and restricted cubic splines [1]. Lu et
al. added serum iron to the same five metals in 2,002 participants using
weighted logistic regression [2]. Tang et al. evaluated the same five metals
against a dietary inflammatory index in 1,726 participants, using a
generalised linear model alongside three mixture-modelling methods: Bayesian
kernel machine regression, weighted quantile sum regression and quantile
g-computation [3]. Fu et al. examined lead, cadmium, mercury, selenium,
copper and zinc jointly in 811 participants using quantile regression and
Bayesian kernel machine regression [4]. Song et al. examined the same class
of mixture in 1,833 participants stratified by sex [5]. Laouali et al.
applied quantile g-computation to lead, cadmium and manganese in 1,777
participants, testing effect modification by two measures of diet quality
[6]. Huang and Ren examined an interaction between blood cadmium and dietary
omega-6 fatty acid intake in 1,918 participants using logistic regression
[7]. Not one of the seven reports discrimination, calibration or
cross-validation, and not one compares a biomarker-containing model against
a demographics-only baseline.

This is a different question, not a different exposure. Adding one more
metal or biomarker to an already saturated association literature is
incremental; asking whether any of it predicts, at the individual level and
benchmarked against demographics, is categorical. To our knowledge, that
test has not previously been performed on this population, with one recent
exception addressed directly here rather than left for the reader to find
independently. Ren et al. restricted their sample to NHANES
participants aged 60 or older, pooled across the 1999-2000, 2001-2002,
2011-2012 and 2013-2014 cycles, and trained a gradient-boosted model on
urinary metals and demographic data to classify what they term "cognitively
impaired" status, reporting a cross-validated area under the receiver
operating characteristic curve (AUC) of 0.90 [8]. Two things distinguish the
present study from theirs. First, NHANES contains no clinical diagnosis of
cognitive impairment; the outcome available is a low-performance
classification against normed test scores, which we term **low cognitive
performance** throughout, and we do not adopt their terminology. Second, and
more consequentially for the question this study asks, Ren et al. report the
discrimination of one combined model and stop there: their analysis does not
decompose that AUC into what demographics alone would achieve and what the
metals add beyond it. That decomposition — not combined-model discrimination
in isolation — is the quantity a demographics-only baseline is built to
measure, and it is what this study reports. A second study, by Nabavi et al.,
trained a stacking ensemble on heavy-metal biomarkers to predict cognitive
impairment across all adults aged 20 and older, reporting an AUC of 0.778,
but its population falls outside the age range examined here and it does not
report a demographics-only baseline either [9].

The gap between statistical association and predictive utility is a
recognised methodological problem beyond this specific exposure-outcome
pair, and reporting standards have moved to reflect it: the TRIPOD+AI
statement now specifies calibration, decision-curve analysis and internal or
external validation as expected components of any prediction-model report,
for regression or machine-learning methods alike [10]. None of the
association studies above provide any of these. This study does, reported
against the TRIPOD+AI checklist in full.

Two limits to this novelty claim are stated here rather than left implicit.
The data are not novel: NHANES 2011-2014 is a heavily analysed dataset. The
algorithms are not novel: penalised logistic regression, random forests and
gradient boosting are standard classifiers. The contribution is the
question, the evaluation framework built to answer it, and the reporting
standard applied to it — not a new exposure, outcome, or method.

**Objectives.** This study estimates how much predictive value blood metals
and nutritional biomarkers add, beyond demographics, for identifying low
cognitive performance in US adults aged 60 and older, quantified as the
change in cross-validated AUC between a demographics-only model and a model
additionally containing the biomarker panel, with calibration and
decision-curve analysis reported alongside discrimination. This is a model
development study with internal validation by repeated cross-validation; no
external validation cohort exists for this exposure-outcome pairing, and
this is stated as a limitation below. Hypotheses, the primary metric, the
threshold for a meaningful difference, and every sensitivity analysis were
fixed in writing before any outcome-predictor relationship was examined, and
are reported in full in `PREREGISTRATION.md`.

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

The cross-validated performance estimates below come from the nested-CV
procedure just described, in which each of the 50 folds fits its own
pipeline; no single coefficient set exists from that procedure. For
reporting compliance, the identical M3 pipeline was separately refit on
the complete analytic sample, with the regularisation strength selected
by the same grid via 10-fold cross-validation on the full sample (which
selected C=0.1, matching the mode across the original 50 folds).
Standardised coefficients, odds ratios, and 2,000-resample bootstrap 95%
CIs from that refit are reported in full in
`output/tables/10_m3_coefficients.md` (Supplementary Table).

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
69.4 years) and slightly more likely to meet the outcome definition (26.1% against
24.2%), with all differences under three percentage points (Table 1b).

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

# Discussion

Adding a panel of five blood metals and fifteen nutritional and metabolic
biomarkers to a demographics-only model did not improve identification of
low cognitive performance in US adults aged 60 and older. The primary
result, delta-AUC(M3 - M0) = -0.0019, 95% confidence interval [-0.0108,
0.0071], is a **precise** null rather than an uninformative one: because a
difference of 0.02 in AUC was declared in advance as the smallest change
worth calling meaningful, the interval's upper bound of 0.0071 rules out an
improvement of that magnitude, rather than merely failing to detect one.
That distinction is only available because the threshold was fixed before
the outcome-predictor relationship was examined, and it is the strongest
sentence this study can make.

The sharper finding is comparative. The full biomarker panel performed
**significantly worse**, not merely no better, than a baseline of
demographics plus eight items of routine clinical history — body-mass
index, smoking status, alcohol use, depressive symptoms, and self-reported
stroke, diabetes, hypertension and high cholesterol — none of which require
a laboratory. That difference held across all three algorithms, with
intervals excluding zero throughout (logistic regression, -0.0158
[-0.0295, -0.0033]; random forest, -0.0197 [-0.0338, -0.0055]; gradient
boosting, -0.0230 [-0.0385, -0.0063]). A twenty-analyte panel was
outperformed by a clinical questionnaire. This converts an absence of
evidence into a concrete statement about where identifying information
actually resides, and it is the most quotable result in the paper.

The mixture-modelling approach that dominates this literature fares no
better when evaluated on predictive rather than inferential criteria.
Quantile g-computation applied to the metals mixture reached a
cross-validated AUC of 0.7874, against 0.7884 for demographics alone: a
method built to decompose the joint effect of correlated exposures conferred
no advantage over ignoring the exposures entirely. Feature-importance
rankings compound the caution. Across 200 bootstrap resamples, the three
demographic predictors were essentially deterministic in rank, while every
biomarker's rank moved across a span of fifteen to twenty positions between
resamples. A single-run SHAP ranking over these correlated biomarkers, the
form in which such rankings are routinely reported, is not a reproducible
quantity. Taken together with Ren et al.'s report of an AUC of 0.90 for a
demographics-plus-metals model on a related population without decomposing
that figure [8], this suggests a broader reporting gap in this literature:
strong combined-model performance and inferentially motivated mixture
decompositions are both being reported in place of the specific quantity
that determines whether biomarkers are worth measuring for this purpose,
namely their contribution over demographics alone.

Three misreadings of this result are anticipated and foreclosed here. This
study does not show that any biomarker is unrelated to cognition; the
published associations behind the seven studies reviewed in the
Introduction may all be correct as association claims; NHANES is
cross-sectional, and nothing here tests, or could test, whether any
exposure leads to, causes, or protects against low cognitive performance.
Nor does it recommend against measuring these analytes for the clinical
purposes for which they are already ordered — vitamin B12 and folate
deficiency, glycaemic control, renal function, lipid management — none of
which this study evaluated. What it shows is narrower and specific: that
translating these published associations into an individual-level
prediction of low cognitive performance, in this population, adds nothing
measurable once demographics are known.

Several limitations bear on interpretation. The design is cross-sectional,
so no temporal or causal claim is possible in either direction. The
complete-case analytic sample is mildly non-random — participants excluded
for missing data were slightly older and slightly more likely to meet the
outcome definition, by under three percentage points on each measure — though
the dominant exclusion mechanism, the one-half random subsample used for
blood metals in the 2013-2014 cycle, is missing completely at random by
design; a sensitivity analysis using multiple imputation on the full
labelled sample of 3,124 produced the narrowest interval obtained under any
specification (0.0015 [-0.0030, 0.0063]) and remained null, which argues
against the sample restriction as an explanation for the result. Age is
top-coded at 80 years in the public-use file, compressing the range of the
single strongest predictor and likely attenuating, not inflating, any
demographic contribution. No external validation cohort exists for this
exposure-outcome pairing, so all performance estimates reflect internal,
cross-validated discrimination on one population and cycle range; whether
the same null holds in a different population is untested. No subgroup
fairness audit was pre-specified across race, Hispanic origin or sex, and
none is reported. Serum copper and zinc were excluded from the biomarker
panel because that assay was run on a one-third subsample in both cycles,
and their omission cannot be ruled out as a reason the nutritional block
underperforms, though the block's near-zero contribution held even before
that exclusion was applied to any single analyte. Finally, the outcome is
defined against pooled-sample quantiles, so an individual participant's
label depends on the distribution of the full sample; this is a declared
property of a relative outcome definition, made explicit in the
pre-registration, rather than an artefact discovered afterward, but it
means the label itself is not fixed independent of the sample analysed.

Reported against the TRIPOD+AI checklist, this study is, to our knowledge,
the first on this population and cycle range to report calibration,
decision-curve analysis, and a pre-registered, threshold-based test of
incremental predictive value for these biomarkers. The conclusion is a
negative one on the primary axis, and it is reported as such rather than
reframed: seven studies in this literature report statistically significant
associations between these biomarkers and cognition, and this study finds
that translating those associations into identifying which individuals have
low cognitive performance adds essentially nothing beyond age, education and
income, and measurably less than eight questions asked without a blood
draw.

---

# Declarations

DPR requires all seven sections below in every submission, with "Not
applicable" where genuinely not relevant. Three are drafted and verified;
four need author input before submission and are marked accordingly rather
than left blank or guessed.

## Ethics approval and consent to participate

NHANES protocol and procedures were approved by the National Center for
Health Statistics (NCHS) Ethics Review Board (formerly the NCHS Research
Ethics Review Board), and written informed consent was obtained from all
participants by NCHS prior to data collection. This study is a secondary
analysis of de-identified, publicly available data and involved no
additional contact with participants. **[Verify with your own institution
whether a separate determination letter — e.g. "not human subjects
research" — is required for secondary analysis of public NHANES data;
this varies by institution and is not something checked here.]**

## Consent for publication

Not applicable. No individual person's data, images, or identifiable
information are presented; all results are reported at the level of
aggregate statistics on a de-identified public dataset.

## Availability of data and materials

NHANES data are publicly available from the CDC at wwwn.cdc.gov and are not
redistributed here; `src/00b_download.py` rebuilds the raw dataset from the
original CDC URLs. The analysis code is available at
https://github.com/NeilP211/nhanes-ieee. **[Decided 2026-09-05: public on
submission. Action needed from Neil — the repository is currently private
and visibility can only be changed by its owner/an admin; the account used
in this session has write access only. Neil needs to either set the
repository to public himself or grant admin access before submission.]**

## Competing interests

The authors declare that they have no competing interests. **[Decided
2026-09-05, pending Neil's confirmation — flag before submission if this is
not accurate for either author.]**

## Funding

This research received no specific grant from any funding agency in the
public, commercial, or not-for-profit sectors. **[Decided 2026-09-05,
pending Neil's confirmation — flag before submission if either author's
institution or any other source funded this work.]**

## Authors' contributions

SK and NP contributed equally to this work and share first authorship, per
the division of labour in `PROJECT_BRIEF.md` section 12 and the work
actually completed. Shreyan Kancharla (SK): conceptualisation, literature
review and verification, project administration, writing — original draft
(Introduction, Discussion, Abstract), writing — review and editing,
corresponding author. Neil Patel (NP): conceptualisation, data curation,
formal analysis, methodology, software, validation, visualisation, writing
— original draft (Methods, Results). Both authors jointly decided the
analytic sample definition, the nested model specification, the
pre-registration, and the target journal; both authors read and approved
the final manuscript.

## Acknowledgements

Not applicable. **[Confirm with Neil before submission — update if there is
anyone to thank who does not meet authorship criteria, e.g. institutional
computing support.]**

---

# References (Introduction and Discussion)

Vancouver style, per DPR's submission guidelines: authors listed in full up
to six, first six followed by "et al." beyond that; journal names not
italicised; numbered in order of first appearance in the text above. Every
citation was checked against its source (publisher page, PMC, or PubMed)
during the literature review of 2026-09-05; see `LITERATURE_REVIEW.md` for
the verification notes, including the full author lists used to apply the
six-author rule below.

1. Wang N, Guo L, Shi M, Wang L, Zhou Y, Liu H, et al. Association of single
   and combined effects of blood heavy metals with cognitive function in
   older adults of the United States: a cross-sectional study. Research
   Square [Preprint]. 2024. Not confirmed as peer-reviewed at time of
   writing — cite as a preprint. Available from:
   https://www.researchsquare.com/article/rs-4786268/v1
2. Lu K, Liu T, Wu X, Zhong J, Ou Z, Wu W. Association between serum iron,
   blood lead, cadmium, mercury, selenium, manganese and low cognitive
   performance in old adults from National Health and Nutrition Examination
   Survey (NHANES): a cross-sectional study. Br J Nutr. 2023;130(10):
   1743-1753. doi:10.1017/S0007114523000740
3. Tang C, Shen M, Hong H. Uncovering the relationship between trace element
   exposure, cognitive function, and dietary inflammation index in elderly
   Americans from the National Health and Nutrition Examination Survey
   2011-2014. BMC Public Health. 2024;24:2516.
   doi:10.1186/s12889-024-20060-4
4. Fu Z, Xu X, Cao L, Xiang Q, Gao Q, Duan H, et al. Single and joint
   exposure of Pb, Cd, Hg, Se, Cu, and Zn were associated with cognitive
   function of older adults. Sci Rep. 2024;14:28567.
   doi:10.1038/s41598-024-79720-5
5. Song S, Liu N, Wang G, Wang Y, Zhang X, Zhao X, et al. Sex specificity in
   the mixed effects of blood heavy metals and cognitive function on
   elderly: evidence from NHANES. Nutrients. 2023;15(13):2874.
   doi:10.3390/nu15132874
6. Laouali N, Benmarhnia T, Lanphear BP, Weuve J, Mascari M,
   Boutron-Ruault MC, et al. Association between blood metals mixtures
   concentrations and cognitive performance, and effect modification by
   diet in older US adults. Environ Epidemiol. 2022;6(1):e192.
   doi:10.1097/EE9.0000000000000192
7. Huang G, Ren G. Interaction between omega-6 fatty acids intake and blood
   cadmium on the risk of low cognitive performance in older adults from
   National Health and Nutrition Examination Survey (NHANES) 2011-2014.
   BMC Geriatr. 2022. doi:10.1186/s12877-022-02988-7
8. Ren F, Zhao X, Yang Q, Liao H, Zhang Y, Liu X. A machine learning
   framework for predicting cognitive impairment in aging populations using
   urinary metal and demographic data. Front Genet. 2025;16:1631228.
   doi:10.3389/fgene.2025.1631228
9. Nabavi A, Safari F, Kashkooli M, Nabavizadeh SS, Molavi Vardanjani H.
   Early prediction of cognitive impairment in adults aged 20 years and
   older using machine learning and biomarkers of heavy metal exposure.
   Curr Res Toxicol. 2024;7:100198. doi:10.1016/j.crtox.2024.100198
10. Collins GS, Moons KGM, Dhiman P, Riley RD, Beam AL, Van Calster B, et
    al. TRIPOD+AI statement: updated guidance for reporting clinical
    prediction models that use regression or machine learning methods.
    BMJ. 2024;385:e078378. doi:10.1136/bmj-2023-078378
