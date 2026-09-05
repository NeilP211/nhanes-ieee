# Literature review — verification of the seven-study gap table

**Compiled 2026-09-05** by Shreyan Kancharla, against `PROJECT_BRIEF.md` section 2.
Every citation below was checked against the source (publisher page, PMC, or
PubMed), not reconstructed from memory. Two papers not in the original table
were found during the search and are flagged separately because they report
predictive metrics — see section 2.

---

## 1. The seven-study table, verified

All seven rows are confirmed. **"Predictive metrics: None" holds for every
row.** Verified n matches the brief for six of seven; row 5's n was previously
"not recorded" and is now filled in.

| # | Citation | n | Exposure | Method | Predictive metrics |
|---|---|---|---|---|---|
| 1 | Wang N, Guo L, Shi M, et al. "Association of single and combined effects of blood heavy metals with cognitive function in older adults of the United States: A cross-sectional study." **Research Square preprint rs-4786268/v1, Sept 2024.** Not confirmed as peer-reviewed / published at time of check. | 1,460 | Pb, Cd, Hg, Se, Mn | Linear regression, restricted cubic spline | None |
| 2 | Lu K, Liu T, Wu X, Zhong J, Ou Z, Wu W (2023). "Association between serum iron, blood lead, cadmium, mercury, selenium, manganese and low cognitive performance in old adults from NHANES: a cross-sectional study." *Br J Nutr* 130(10):1743–1753. doi:10.1017/S0007114523000740 | 2,002 | Fe + 5 metals | Weighted logistic regression | None |
| 3 | Tang C, Shen M, Hong H (2024). "Uncovering the relationship between trace element exposure, cognitive function, and dietary inflammation index in elderly Americans from NHANES 2011–2014." *BMC Public Health* 24:2516. doi:10.1186/s12889-024-20060-4 | 1,726 | Pb, Cd, Hg, Mn, Se | GLM, BKMR, WQS, quantile g-computation | None |
| 4 | Fu Z, Xu X, Cao L, et al. (2024). "Single and joint exposure of Pb, Cd, Hg, Se, Cu, and Zn were associated with cognitive function of older adults." *Sci Rep* 14:28567. doi:10.1038/s41598-024-79720-5 | 811 | Pb, Cd, Hg, Se, Cu, Zn | Quantile regression, RCS, BKMR | None |
| 5 | Song S, Liu N, Wang G, et al. (2023). "Sex Specificity in the Mixed Effects of Blood Heavy Metals and Cognitive Function on Elderly: Evidence from NHANES." *Nutrients* 15(13):2874. doi:10.3390/nu15132874 | 1,833 | 5 metals | GLM, BKMR, WQS, Qgcomp | None. Self-states: *"this epidemiological study has no individual predictive value."* |
| 6 | Laouali N, Benmarhnia T, Lanphear BP, et al. (2022). "Association between blood metals mixtures concentrations and cognitive performance, and effect modification by diet in older US adults." *Environmental Epidemiology* 6(1):e192. doi:10.1097/EE9.0000000000000192 | 1,777 | Pb, Cd, Mn | Quantile g-computation | None |
| 7 | Huang G, Ren G (2022). "Interaction between ω-6 fatty acids intake and blood cadmium on the risk of low cognitive performance in older adults from NHANES 2011–2014." *BMC Geriatrics*. doi:10.1186/s12877-022-02988-7 | 1,918 | Cd + ω-6 intake | Logistic regression | None |

**Decided 2026-09-05 (Shreyan Kancharla):** include row 1, flagged explicitly
as a preprint in the Introduction text (e.g. "in a preprint, Wang et al.
report..."), not cited with the same evidentiary weight as the six
peer-reviewed rows. Worth a follow-up check closer to submission for whether
it has since been published in a journal.

---

## 2. New since the brief — must be addressed directly, not omitted

Two papers report predictive metrics on NHANES metals-and-cognition data.
Neither closes the gap this study claims, but both must be cited and
distinguished explicitly in the Introduction — a reviewer at a
prediction-modeling venue will find these in the same search we just ran.

### Ren F, Zhao X, Yang Q, Liao H, Zhang Y, Liu X (2025)

"A machine learning framework for predicting cognitive impairment in aging
populations using urinary metal and demographic data." *Front Genet*
16:1631228. doi:10.3389/fgene.2025.1631228

- **Restricted to adults 60+** — same population as this study.
- Pools four NHANES cycles: 1999-2000, 2001-2002, 2011-2012, 2013-2014.
  n = 1,230 (579 cognitively normal, 651 "cognitively impaired").
- Urinary metals + demographics, XGBoost, 5-fold CV, **AUC = 0.90**.
- **Does not fit or report a demographics-only baseline.** One combined
  model's AUC is reported and the analysis stops there — no delta-AUC, no
  isolation of what the metals contribute beyond what demographics alone
  would achieve. That decomposition is this study's central contribution,
  and this paper does not attempt it.
- Uses "cognitively impaired" as a binary label derived from NHANES
  cognitive test data — the same terminology error this project's own
  language rules exist to avoid, for the identical reason: NHANES contains
  no clinical diagnosis.
- **Decided 2026-09-05 (Shreyan Kancharla): include, with its own paragraph
  in the Introduction.** State plainly that a 2025 paper on the same
  population reports strong discrimination (AUC 0.90) for a
  demographics-plus-metals model, but does not test whether that performance
  is attributable to the metals or to demographics alone — which is the
  question this study answers, and the answer is that it is attributable
  almost entirely to demographics. This is a stronger, more specific novelty
  claim than "no one has done prediction here," and it is defensible because
  it is precise about what the other paper did and did not measure.

### Nabavi A, Safari F, Kashkooli M, Nabavizadeh SS, Molavi Vardanjani H (2024)

"Early prediction of cognitive impairment in adults aged 20 years and older
using machine learning and biomarkers of heavy metal exposure." *Curr Res
Toxicol* 7:100198. doi:10.1016/j.crtox.2024.100198

- **Not restricted to 60+** — ages 20 and up, n = 2,933. Outside this
  study's population per the brief's own scope note (section 2: restrict the
  gap claim to NHANES 2011-2014, adults 60+; other age ranges are context).
- Stacking ensemble, 5-fold CV, AUC = 0.778 on test data.
- Does not isolate a demographics-only baseline; reports "incorporating
  heavy metal biomarkers enhanced prediction" as a qualitative claim rather
  than a measured increment.
- **Action:** cite as context (different population), lower priority than
  Ren et al. 2025. Optional in the Introduction depending on length budget.

---

## 3. Net effect on the novelty claim

The claim survives but needs to be narrower than the brief's current
wording. Change from:

> "No published study reports predictive metrics for this exposure-outcome
> pair in this population."

to:

> "No published study on this population isolates the incremental predictive
> contribution of biomarkers over demographics — the quantity this study's
> primary outcome measures — with calibration and decision-curve analysis.
> One 2025 study reports strong combined-model discrimination (AUC 0.90) on
> the same population but does not decompose it; this study shows that,
> when decomposed, the increment is null."

This is a stronger claim than the original, not a weaker one: it turns a
close competitor into supporting evidence that the decomposition step is the
genuine missing piece, rather than leaving it as an uncomfortable omission a
reviewer discovers independently.

---

## Sign-off

| Role | Name | Date |
|---|---|---|
| Literature review | Shreyan Kancharla | 2026-09-05 |
