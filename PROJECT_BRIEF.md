# Predictive Value of Nutritional and Toxic-Metal Biomarkers for Cognitive Performance in Older Adults

**NHANES 2011-2014 | Full Project Specification**

---

## 0. The pitch in one paragraph

At least seven published studies report significant associations between blood metals, nutritional biomarkers, and cognitive performance among US adults aged 60+ in NHANES 2011-2014. Every one of them reports regression coefficients or odds ratios. None report whether those biomarkers actually *predict* who has low cognitive performance — no discrimination, no calibration, no cross-validation, and critically, no comparison against what you would already know from a person's age, sex, education, and income. We close that gap. Using the same data and the same population, we quantify how much predictive value a full biomarker panel contributes beyond demographics alone, with cross-validated discrimination, calibration, and decision-curve analysis, reported to TRIPOD+AI standards.

---

## 1. Research question and hypotheses

### Primary question

> Among US adults aged 60+, how much predictive value do blood metals and nutritional biomarkers add, beyond demographics, for identifying low cognitive performance?

### Formal hypotheses

**H1 (primary).** A model containing demographics plus blood metals plus nutritional biomarkers (M3) achieves higher cross-validated AUC than a demographics-only model (M0). Operationally: the bootstrap 95% CI for delta-AUC(M3 - M0) excludes zero.

**H0 (primary null).** delta-AUC(M3 - M0) is not distinguishable from zero — the biomarkers add nothing beyond demographics.

**H2 (secondary).** Nonlinear learners (random forest, XGBoost) outperform penalized logistic regression, consistent with U-shaped exposure-response for selenium and manganese, which are both essential nutrients and neurotoxicants.

**H3 (secondary).** The metals block (M1 - M0) and the nutritional block (M2 - M0) contribute non-redundantly; delta-AUC(M3 - M0) exceeds either alone.

**H4 (exploratory).** Predictive contributions differ across cognitive domains — biomarkers may predict processing speed (DSST) better than memory (CERAD), or vice versa.

### Pre-specified before any modeling

Lock these in writing, dated, before touching the data:

| Decision | Value |
|---|---|
| Primary outcome | Composite z-score, lowest quartile |
| Primary metric | delta-AUC(M3 - M0), bootstrap 95% CI |
| Primary model class | L2-penalized logistic regression |
| CV scheme | Stratified 10-fold, repeated 5x |
| Meaningful-difference threshold | delta-AUC >= 0.02 (state this in advance) |
| Everything else | Labeled exploratory |

---

## 2. Novelty and publication value

### The gap, with evidence

Published work on this exact population and cycle range:

| Study | n | Exposure | Method | Predictive metrics? |
|---|---|---|---|---|
| Blood metals & cognition, 60+ | 1,460 | 5 metals | Linear regression, RCS | None |
| Fe + 5 metals & low cognition | 2,002 | 6 elements | Weighted logistic | None |
| Trace elements + DII | 1,726 | 5 elements | GLM, BKMR, WQS, qg-comp | None |
| Joint metal exposure | 811 | 6 metals | Mixture models | None |
| Sex-specific metal mixtures | — | Metals | Mixture models | None |
| Metals x diet quality | 1,777 | Pb, Cd, Mn | Quantile g-computation | None |
| Cadmium x omega-6 intake | 1,918 | Cd + FA intake | Logistic | None |

The literature is saturated on association and empty on prediction. That asymmetry *is* the opportunity.

### Why this is strong novelty

**It is a different question, not a different variable.** Adding exposure #48 to a saturated association literature is incremental. Asking whether any of it predicts is categorical. A reviewer cannot say "this has been done" because it has not.

**It is not scoopable by the fast-moving competition.** The papers appearing monthly in this space are association studies. They do not compete with a prediction-model paper, and researchers producing them are not going to pivot to TRIPOD+AI reporting.

**It cannot produce a wasted result.** See section 6 — every plausible outcome yields a publishable paper. This is unusual and is the single strongest practical argument for the design.

**It addresses a recognized methodological problem.** The gap between statistical association and predictive utility is a live concern in epidemiology and clinical prediction. Demonstrating the gap concretely in a well-known dataset has value beyond this specific exposure-outcome pair.

**It is methodologically current.** Calibration, decision-curve analysis, and TRIPOD+AI reporting are what prediction-model reviewers expect in 2026 and what none of the comparison papers provide.

### Honest limits of the novelty claim

- The *data* are not novel. NHANES 2011-2014 is heavily mined.
- The *algorithms* are not novel. Penalized logistic, RF, XGBoost are standard.
- The *contribution* is the question, the evaluation framework, and the reporting standard. Be explicit about this in the paper rather than implying otherwise — overclaiming novelty is the fastest route to a hostile review.

---

## 3. Data

All files are SAS XPORT (.xpt) from wwwn.cdc.gov, joined on `SEQN`. Read with `pandas.read_sas(path, format="xport")`.

### Outcome — `CFQ_G` / `CFQ_H`

| Test | Domain | Range |
|---|---|---|
| CERAD Word List, immediate (3 x 10 words) | Learning / memory | 0-30 |
| CERAD Delayed Recall | Memory | 0-10 |
| Animal Fluency (60 s) | Verbal fluency / executive | count |
| Digit Symbol Substitution (WAIS-III, 133 boxes, 120 s) | Processing speed | 0-133 |

**Construction:** z-score each test within the pooled 60+ sample, average (require >=3 of 4 present), primary label = lowest quartile. Also retain the continuous composite for a companion regression, and each test separately for H4.

**Terminology:** *low cognitive performance*, never *cognitive impairment*. NHANES has no clinical diagnosis.

**Traps:**
- DSST non-completion reasons include physical, cognitive, and literacy barriers — plausibly your positive cases. Report n and reasons; run a sensitivity analysis coding "unable to complete" as impaired.
- Test language (English/Spanish) affects fluency and DSST comparability. Covariate at minimum; sensitivity analysis restricted to English administration.

### Block 1 — Demographics: `DEMO_G` / `DEMO_H`

`RIDAGEYR` (restrict >=60), `RIAGENDR`, `RIDRETH3`, `DMDEDUC2`, `INDFMPIR`
Design variables: `WTMEC2YR` (**halve for two cycles**), `SDMVSTRA`, `SDMVPSU`

### Block 2 — Blood metals: `PBCD_G` / `PBCD_H`

Lead, cadmium, total mercury, selenium, manganese (ICP-MS, whole blood). Full MEC sample — no subsample loss.
Optional: `IHGEM` for inorganic vs. methylmercury speciation.
**Avoid `UHM`** (urine metals) — subsample.

### Block 3 — Nutritional biomarkers

Verified present in 2011-2012. **`_H` versions need confirmation** (section 10).

| Domain | File | Content |
|---|---|---|
| B12 | `VITB12_G` | Serum B12 |
| B12 function | `MMA_G` | Methylmalonic acid |
| Folate | `FOLFMS_G` | Total + individual serum folate forms |
| Folate, long-term | `FOLATE_G` | RBC folate |
| Vitamin D | `VID_G` | 25-hydroxyvitamin D |
| Trace minerals | `CUSEZN_G` | Serum copper, selenium, zinc |
| Inflammation proxy | `CBC_G` | CBC to NLR, PLR, SII |
| Chemistry | `BIOPRO_G` | Albumin, creatinine to eGFR |
| Glycemia | `GHB_G` | HbA1c |
| Lipids | `HDL_G`, `TCHOL_G`, `TRIGLY_G` | HDL, total cholesterol, LDL/TG |

**Excluded, with reasons for the limitations section:** CRP and homocysteine — not measured in these cycles. Ferritin and serum iron — discontinued after 2009-2010. Serum fatty acids (`FAS`) — fasting subsample, would cut n by more than half. Accelerometer (`PAXDAY`) — non-wear attrition plus severe reverse causation.

### Covariates

`BMX` (BMI), `SMQ` (smoking), `ALQ` (alcohol), `MCQ` (stroke, diabetes), `DPQ` (PHQ-9), `BPQ` (hypertension/cholesterol history)

Depression is more important than it looks: it independently depresses test scores and correlates with both nutrition and metal exposure.

### Expected sample size

Published metals-plus-cognition intersections in this population run 1,460-2,068. Adding nutritional biomarkers costs further attrition. **Plan for 1,400-1,900.** Confirm empirically before finalizing the model plan.

---

## 4. Analysis plan

### Cleaning

1. Convert NHANES reserved codes (7/77/777, 9/99/999 — check each codebook's range) to `NaN` **before any arithmetic**. Silently averaging a 9 invalidates everything downstream.
2. Distinguish skip patterns from true missingness.
3. Log-transform right-skewed variables — all metals, MMA, B12.
4. Handle below-detection values explicitly. NHANES substitutes LOD/sqrt(2) and flags it in a comment variable. Cadmium will have many among non-smokers. **Report the imputed fraction.**
5. Multiple imputation for covariate missingness, fitted inside CV folds.

### Nested models

| Model | Features | Answers |
|---|---|---|
| M0 | Demographics only | The benchmark everything is measured against |
| M1 | Demographics + metals | What do metals add? |
| M2 | Demographics + nutritional biomarkers | What does nutrition add? |
| M3 | Demographics + metals + biomarkers | Is the combination non-redundant? |

Algorithms per model: **L2-penalized logistic regression** (primary), random forest, XGBoost. MLP and KNN optional — at n around 1,700 they will likely lose, which is itself reportable.

### Evaluation protocol

- Stratified 10-fold CV, repeated 5x with different seeds; report mean and spread
- **All preprocessing fits inside each training fold.** Imputation or scaling on the full dataset before splitting leaks and inflates every reported number. This is the single most common fatal error in applied ML papers
- Metrics: AUC, AUPRC, Brier score, calibration slope and intercept, calibration curve
- **Primary: delta-AUC(M1-M0), delta-AUC(M2-M0), delta-AUC(M3-M0), bootstrap 95% CIs**
- **Decision-curve analysis:** net benefit for M3 vs. M0 across threshold probabilities. This is the clinical-utility claim made concrete, and nobody in the comparison literature does it
- Never select on accuracy — at 25% prevalence, "everyone is normal" scores 75%

### Interpretation

- SHAP on the best model, rankings bootstrapped across resamples to show rank stability (correlated biomarkers make single-run rankings unreliable)
- Partial dependence plots for selenium and manganese — the U-shape test for H2
- Survey-weighted logistic regression (`SDMVSTRA`/`SDMVPSU`) for association claims; unweighted ML for prediction claims. **State which is which.** Reproducing the published association estimates is a validity check, not a competing result
- Four cognitive tests as separate secondary outcomes (H4)

### Sensitivity analyses

- Outcome cutoff at 10th and 20th percentiles
- Continuous composite as a regression outcome
- DSST "unable to complete" recoded as impaired
- English-only test administration
- Complete-case vs. imputed comparison

### Reporting

**TRIPOD+AI**, with the checklist as a supplement. This alone distinguishes the paper from every comparison study.

---

## 5. Compute and cost

### Local compute

| Item | Requirement |
|---|---|
| Total data download | ~30-60 MB across both cycles |
| RAM | Peak well under 2 GB; an 8 GB machine is ample |
| Penalized logistic, 50 fits (10-fold x 5 repeats) | Seconds |
| Random forest, 50 fits | 1-3 minutes |
| XGBoost, ~100-point hyperparameter grid x 50 fits | 20-60 min single-core; much less with `n_jobs=-1` |
| Bootstrapped SHAP (200 resamples, TreeSHAP) | 5-15 minutes |
| All four models x all sensitivity analyses | **Under 2 hours total** |
| GPU | **Not needed.** Tabular data, n < 2,000 |

There is no compute bottleneck in this project. The earlier "compute-heavy" concern came entirely from the minute-level accelerometer file, which is out of the design.

### Claude Code usage

Credit consumption depends on your plan and iteration count, so treat these as planning estimates rather than quotes.

| Phase | Sessions (est.) | Cost driver |
|---|---|---|
| Availability audit | 1-2 | Reading codebooks |
| Merge + clean | **5-10** | **Dominant cost.** Codebook edge cases, reserved codes, skip patterns |
| Outcome construction | 2-3 | |
| Modeling pipeline | 3-5 | Scripts are short; runs are local |
| Sensitivity analyses | 2-4 | Mostly reruns |
| Figures and tables | 2-4 | |
| Manuscript support | 3-6 | |

**Cost controls, in order of impact:**

1. **Save intermediates after every phase** to `data/interim/`. Never re-run the merge to fix a modeling bug. Biggest single saving available.
2. **Never paste raw data into the conversation.** Have scripts write summaries to disk and read those instead.
3. **Lock the variable list before writing code.** Re-cleaning after a variable change is the most expensive avoidable event in the project.
4. **Keep this document in the repo** as `PROJECT_BRIEF.md` so context persists across sessions instead of being re-explained.
5. **One script per phase, numbered**, each independently re-runnable.

---

## 6. What each possible result means

This is the section that makes the project safe. Read it before you start, so you are not tempted to torture the data toward a preferred answer.

### Primary axis: delta-AUC(M3 - M0)

**Scenario A — Large (delta-AUC >= 0.05), CI excludes zero.**
Biomarkers meaningfully improve identification of low cognitive performance.
*Title direction:* "Nutritional and toxic-metal biomarkers improve prediction of low cognitive performance beyond demographic risk factors."
*Where it goes:* Nutrients, BMC Geriatrics, J Nutr Health Aging, IEEE Access.
*Watch for:* verify it is not driven by one variable acting as a proxy for general illness (albumin and eGFR are the usual suspects). Run a leave-one-block-out check.

**Scenario B — Modest (0.02 <= delta-AUC < 0.05).** *Most likely outcome.*
Statistically detectable, clinically marginal. Decision-curve analysis becomes the centerpiece: does that improvement produce net benefit at any plausible threshold?
*Title direction:* "Limited incremental predictive value of nutritional and metal biomarkers for cognitive performance in older adults."
*Where it goes:* strong fit for BMC Public Health, Frontiers, PLOS ONE, DPR.
*This is a good result* — nuanced, honest, and the decision-curve framing gives you something concrete to say.

**Scenario C — Null (delta-AUC < 0.02 or CI includes zero).**
The cautionary result, and arguably the most interesting one.
*Title direction:* "Reported biomarker-cognition associations do not translate into predictive utility: a NHANES 2011-2014 analysis."
*Where it goes:* Diagnostic and Prognostic Research, Journal of Clinical Epidemiology, PLOS ONE.
*Framing:* seven studies report significant associations; we show that translating those into individual-level prediction adds essentially nothing beyond age and education. That is a real contribution to how this literature should be interpreted.
**Do not treat this as failure.** Write it up as the headline.

### Secondary axis: does ML beat penalized logistic?

**Scenario D — ML clearly wins (delta-AUC >= 0.03 over logistic).**
Supports H2. Show the U-shapes with partial dependence plots for selenium and manganese. Strengthens an IEEE or ML-venue submission substantially.

**Scenario E — ML ties or loses.** *Most likely.*
At n around 1,700 with ~35 features this is the expected outcome and is well documented. Report it plainly: "flexible learners did not outperform regularized regression, consistent with prior findings in low-dimensional clinical tabular data." This weakens an IEEE framing and strengthens a clinical-journal framing.

### Third axis: calibration

**Scenario F — Good discrimination, poor calibration.**
Common and worth reporting. Means the model ranks people correctly but its probability estimates are wrong — which matters enormously for a "risk calculator" use case. Report calibration slope and intercept, and recalibrate if needed.

### Decision rule for journal targeting

| Result | Lead framing | Primary target |
|---|---|---|
| A + D | ML-forward | IEEE Access, JBHI (reach) |
| A + E | Clinical-forward | Nutrients, JNHA |
| B + E | Nuanced clinical | BMC Public Health, Frontiers |
| C (any) | Methodological | DPR, JCE, PLOS ONE |

---

## 7. Journals

APCs are approximate; verify current rates before submitting.

### Clinical / nutrition venues

| Journal | Fit | Notes |
|---|---|---|
| **Nutrients** (MDPI) | Strong | Heavy NHANES cognition volume; fast; APC ~$3,000 |
| **BMC Public Health** | Strong | Published the trace-element/cognition/DII study; APC ~$3,000 |
| **Frontiers in Nutrition** / **Frontiers in Aging Neuroscience** | Strong | High volume, fast; APC ~$3,000-3,500 |
| **BMC Geriatrics** | Strong | Older-adult focus fits precisely |
| **Scientific Reports** | Good | Published a six-metal cognition paper; APC ~$2,500 |
| **PLOS ONE** | Good | Soundness-based criterion — friendly to a well-executed null |
| **J Nutrition, Health & Aging** | Reach | More selective, better perceived quality |
| **British Journal of Nutrition** | Reach | Published the Fe + five-metals cognition paper — direct precedent |
| **Environmental Research** | Reach | Strong on the metals angle; wants exposure science foregrounded |

### Prediction-methods venues — best conceptual fit

| Journal | Fit | Notes |
|---|---|---|
| **Diagnostic and Prognostic Research** (BMC) | **Excellent** | Exists specifically for prediction-model studies; TRIPOD-native; a rigorous "biomarkers add little beyond demographics" paper is exactly its remit |
| **Journal of Clinical Epidemiology** | Good | Publishes association-vs-prediction methodology critiques |

### IEEE venues — honest assessment

IEEE health-informatics venues reward *computational* contribution. Applying standard classifiers to a public dataset is applied work, not methodological work. Calibrate expectations accordingly.

| Venue | Realism | Notes |
|---|---|---|
| **IEEE Access** | **Realistic** | Broad scope, high volume, fast (weeks), open access, APC ~$1,950. Publishes applied health-ML on public datasets routinely. Your most likely IEEE outcome |
| **IEEE EMBC** (conference, annual) | **Realistic and recommended** | 4-page papers, achievable acceptance rate, good first-publication venue, real conference presence. Deadlines typically early in the year for a summer conference — check current dates |
| **IEEE BHI** (Int'l Conf. on Biomedical & Health Informatics) | Realistic | Conference; good fit for applied prediction work |
| **IEEE ICHI** (Int'l Conf. on Healthcare Informatics) | Realistic | Similar profile |
| **IEEE J. Biomedical and Health Informatics (JBHI)** | **Reach — likely desk reject as-is** | High impact factor. Wants novel methods or substantial clinical impact. "We benchmarked standard classifiers" is unlikely to clear the editor |
| **IEEE Trans. Computational Biology and Bioinformatics** | Poor fit | Oriented to bioinformatics, not epidemiological tabular data |

**How to raise IEEE odds if you want that route:**
Frame the nested incremental-value protocol as a *reusable evaluation framework* for biomarker studies, not as a one-off analysis — "a framework for assessing whether reported epidemiological associations confer predictive utility, demonstrated on NHANES." Add something with computational teeth: block-wise SHAP decomposition, formal comparison of mixture-modeling methods (BKMR/WQS) against ML on predictive rather than inferential criteria, or a nested-CV protocol for incremental value with proper uncertainty quantification. Scenario D (ML clearly beats logistic) also strengthens the case considerably.

**Strategic caution:** IEEE and nutrition journals want genuinely different papers. IEEE foregrounds the ML and treats cognition as the application; Nutrients foregrounds the nutrition and treats ML as the tool. The introductions are not interchangeable. **Pick a lane before your co-author starts drafting.**

Given that you have a co-author focused on clinical interpretation and literature review, the clinical route is the better structural fit. IEEE EMBC is worth considering as a parallel short-form conference submission — conference and journal papers on the same work are acceptable in this field if the journal version is substantially extended, but verify each venue's policy first.

---

## 8. Risks and mitigations

| Risk | Likelihood | Mitigation |
|---|---|---|
| `_H` files unavailable for some biomarkers | Medium | Audit first; drop to intersection or make G-only supplementary |
| Sample smaller than expected | Medium | Merge-and-count before finalizing model plan; drop MLP/KNN if n < 1,200 |
| Data leakage via preprocessing outside folds | **High if careless** | Pipeline objects; every transform fitted inside the fold. Review this specifically |
| ML underperforms logistic | High | Expected; pre-write it as a finding, not a failure |
| Someone publishes a similar prediction paper first | Low | The genre produces association studies, not prediction studies |
| Reviewer objects to arbitrary outcome cutoff | **High** | Pre-specified sensitivity across three cutoffs plus continuous outcome |
| Reviewer objects to survey weights + ML | Medium | Weighted regression for inference, unweighted ML for prediction, stated explicitly |
| Overclaiming novelty | Medium | Section 2 "honest limits" — state exactly what is and is not new |
| Causal language creeping into the discussion | **High** | Cross-sectional. Ban causal verbs in review; check the discussion specifically |

---

## 9. Timeline

| Phase | Duration | Deliverable |
|---|---|---|
| Availability audit + lock variable list | 2 days | Signed-off variable table |
| Download, merge, clean | 5-7 days | `data/processed/analytic.parquet` + attrition table |
| Outcome construction + validation | 2 days | Outcome distributions, alpha check |
| Pre-registration document | 1 day | Dated, before modeling |
| Modeling pipeline (M0-M3 x 3 algorithms) | 4-5 days | Results table |
| Sensitivity analyses | 3 days | Supplementary tables |
| Figures (calibration, DCA, SHAP, PDP) | 3 days | Figure set |
| Manuscript drafting (co-author) | 2-3 weeks | Full draft |
| Internal revision | 1 week | Submission-ready |

**Total: 7-9 weeks.** The original 6-8 week estimate is achievable if the audit happens first and the variable list does not change mid-stream.

---

## 10. Blocking tasks before any code

1. **Confirm `_H` files exist** for `FOLFMS`, `FOLATE`, `CUSEZN`, `MMA`, `VITB12` on the NHANES 2013-2014 Laboratory data page. `PBCD`, `CBC`, `BIOPRO`, `GHB`, `VID` and the lipid files are near-certain. Keep only the both-cycle intersection.
2. **Merge and count** to establish the real analytic n.
3. **Lock the variable list jointly, in writing, dated.**
4. **Write the pre-registration** (hypotheses, primary metric, threshold, CV scheme) before looking at any outcome-predictor relationship.

---

## 11. Repository structure

```
PROJECT_BRIEF.md          # this document - keep it in context
PREREGISTRATION.md        # dated, written before modeling
data/raw/                 # downloaded .xpt, never modified
data/interim/             # per-phase outputs
data/processed/           # analytic dataset
src/
  00_audit.py             # file/variable availability
  01_cohort.py            # merge, clean, attrition table
  02_outcome.py           # composite construction
  03_model.py             # nested M0-M3, all algorithms
  04_evaluate.py          # AUC, calibration, DCA, bootstrap CIs
  05_interpret.py         # SHAP, PDP
  06_sensitivity.py       # all sensitivity analyses
output/tables/
output/figures/
requirements.txt          # pinned versions
```

Set every random seed. Pin every package version.

---

## 12. Division of labor

**Data and modeling lead (Neil):** file acquisition, merging, cleaning, outcome construction, all modeling and evaluation, figures, methods and results sections.

**Clinical and framing lead:** literature review, introduction, discussion, clinical interpretation, journal selection, submission.

**Joint and non-negotiable:** the variable list, locked in writing before any code runs, and the pre-registration document. Three file specifications in the earlier project brief were wrong — `HSCRP_G`/`HSCRP_H` do not exist in NHANES, `FOLATE_G` is RBC folate rather than B12, and `PAXMIN` was the wrong granularity for accelerometer summaries. The person doing the data work is the one who discovers such errors, and always several weeks too late.
