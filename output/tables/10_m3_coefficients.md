# Full M3 model coefficients

**TRIPOD+AI item 16.** The cross-validated performance estimates elsewhere in this repository are correct as reported; no single coefficient set exists from that procedure since each of the 50 folds fits its own pipeline. This table is a separate refit of the identical pipeline on the complete analytic sample (n=1,784, 431 events), reported for TRIPOD compliance and not as a new performance estimate.

C selected by 10-fold CV on the full sample: **0.1** (matches the mode across the original 50 CV folds, C=0.1 in 49 of 50). Intercept: -1.1747. Bootstrap: 2000 resamples, 2000 valid (re-selecting C in each resample; a resample is excluded only if it produces a single-class sample or a different one-hot category set than the full-sample fit).

**Numeric features are standardised**, so each row is the odds ratio per one-SD increase, not per raw unit. **RIDRETH3 and DMDEDUC2 are one-hot encoded without a dropped reference category** (matching the modelling pipeline exactly, which relies on the L2 penalty rather than a reference contrast) -- these rows are not standard reference-category odds ratios and should not be reported as such in prose.

| Feature | Coefficient (standardised) | Odds ratio | 95% CI |
|---|---|---|---|
| Age, years | 0.572 | 1.7719 | [1.5611, 2.216] |
| Sex (coded 1=male, 2=female) | -0.18 | 0.8353 | [0.7145, 0.9668] |
| Income-to-poverty ratio | -0.3108 | 0.7328 | [0.6328, 0.8908] |
| Blood lead (log) | 0.0169 | 1.017 | [0.8803, 1.1725] |
| Blood cadmium (log) | 0.0555 | 1.0571 | [0.9194, 1.2129] |
| Blood total mercury (log) | -0.039 | 0.9617 | [0.8316, 1.1083] |
| Blood selenium (log) | -0.0715 | 0.931 | [0.8123, 1.0752] |
| Blood manganese (log) | -0.0439 | 0.9571 | [0.8412, 1.1021] |
| Serum vitamin B12 (log) | 0.162 | 1.1758 | [1.0302, 1.3963] |
| Serum methylmalonic acid (log) | 0.0906 | 1.0948 | [0.9546, 1.269] |
| Serum total folate | 0.1277 | 1.1362 | [0.9857, 1.4515] |
| RBC folate | -0.1017 | 0.9033 | [0.7279, 1.0555] |
| 25-hydroxyvitamin D | -0.1193 | 0.8875 | [0.7647, 1.0271] |
| HbA1c | 0.0745 | 1.0774 | [0.9449, 1.2233] |
| HDL cholesterol | 0.0155 | 1.0157 | [0.8527, 1.2226] |
| Total cholesterol | -0.0745 | 0.9282 | [0.8022, 1.0652] |
| Triglycerides | 0.0501 | 1.0514 | [0.8963, 1.2478] |
| Serum albumin | -0.0412 | 0.9597 | [0.8359, 1.1036] |
| Serum iron | -0.0939 | 0.9103 | [0.7976, 1.026] |
| eGFR | -0.081 | 0.9222 | [0.8026, 1.0756] |
| Neutrophil-to-lymphocyte ratio | 0.1324 | 1.1416 | [0.9793, 1.4352] |
| Platelet-to-lymphocyte ratio | -0.0653 | 0.9368 | [0.773, 1.1159] |
| Systemic immune-inflammation index (log) | 0.0097 | 1.0098 | [0.8069, 1.2559] |
| RIDRETH3 = Mexican American | 0.0469 | 1.048 | [0.6494, 1.4956] |
| RIDRETH3 = Other Hispanic | 0.3854 | 1.4701 | [1.1422, 2.2946] |
| RIDRETH3 = Non-Hispanic White | -0.3595 | 0.6981 | [0.5232, 0.919] |
| RIDRETH3 = Non-Hispanic Black | 0.1701 | 1.1855 | [0.919, 1.8108] |
| RIDRETH3 = Non-Hispanic Asian | -0.0677 | 0.9346 | [0.5933, 1.459] |
| RIDRETH3 = Other/multiracial | -0.1833 | 0.8325 | [0.1675, 1.3136] |
| DMDEDUC2 = Less than 9th grade | 1.0102 | 2.7462 | [2.2624, 4.6369] |
| DMDEDUC2 = 9-11th grade | 0.2881 | 1.3339 | [1.0118, 1.8329] |
| DMDEDUC2 = High school grad/GED | -0.0889 | 0.9149 | [0.6682, 1.1064] |
| DMDEDUC2 = Some college/AA degree | -0.5367 | 0.5847 | [0.3774, 0.6851] |
| DMDEDUC2 = College graduate or above | -0.6808 | 0.5062 | [0.2653, 0.6199] |
