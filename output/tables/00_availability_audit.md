# Phase 0: NHANES 2011-2014 Availability Audit

Generated 2026-08-30 by `src/00_audit.py`. Verified against the CDC data pages and, where stated, against the downloaded files themselves.

## 1. Headline findings

1. **All 22 required files exist in both cycles.** All five high-priority `_H` files (`FOLFMS_H`, `FOLATE_H`, `CUSEZN_H`, `MMA_H`, `VITB12_H`) are present. Nothing from the brief is missing or restricted.
2. **`PBCD_H` is a one-half subsample, not the full MEC sample.** The brief states blood metals have no subsample loss. That holds for `PBCD_G` only. This is the single most consequential finding in this audit.
3. **`CUSEZN` is a one-third subsample in both cycles.** The brief lists it as an ordinary Block 3 file. On the documented sampling fraction, requiring it would be expected to cut the analytic n to roughly a third. The exact overlap with our 60+ cognition sample was not measured (see section 7).
4. **The B12 variable is renamed between cycles** (`LBXB12` to `LBDB12`). A merge on the `_G` name yields all-missing B12 for 2013-2014 without erroring.
5. **NHANES stores a zero MEC weight as 5.4e-79, not 0.0.** A `WTMEC2YR > 0` filter silently retains interview-only participants.
6. **The cognitive score variables contain no reserved codes.** `CFDCST1` ranges 0 to 10, so 7 and 9 are legitimate scores. A blanket 7/9-to-NaN rule would corrupt the outcome.

## 2. File availability

`_G` = 2011-2012, `_H` = 2013-2014. URLs are the direct `.xpt` links used by the download step. Every URL was confirmed to return HTTP 200 and to begin with the SAS XPORT magic header, so none is a 200-status error page.

| Stem | Block | _G | _H | Special weight | Notes |
|---|---|---|---|---|---|
| `DEMO` | Block 1 | yes | yes | `WTINT2YR`, `WTMEC2YR` | Carries WTINT2YR, WTMEC2YR, SDMVSTRA, SDMVPSU. Halve WTMEC2YR when pooling the two cycles. Age is top-coded at 80. |
| `CFQ` | Outcome | yes | yes | none | Administered to MEC participants aged 60+ only. Row count equals the 60+ MEC count exactly in both cycles. Use WTMEC2YR. |
| `PBCD` | Block 2 | yes | yes | `WTSH2YR` | **Asymmetric.** _G is full MEC. _H is a one-half subsample of ages 12+ and carries its own weight WTSH2YR. Halves the 2013-2014 metals n. |
| `IHGEM` | Block 2 opt | yes | yes | `WTSH2YR` | Same one-half subsample as PBCD in _H (WTSH2YR present in _H only). |
| `VITB12` | Block 3 | yes | yes | none | **Variable renamed between cycles:** LBXB12 in _G, LBDB12 in _H. LBDB12SI (pmol/L) is present in both and is the safe pooling key. |
| `MMA` | Block 3 | yes | yes | none |  |
| `FOLFMS` | Block 3 | yes | yes | none |  |
| `FOLATE` | Block 3 | yes | yes | none |  |
| `VID` | Block 3 | yes | yes | none |  |
| `CUSEZN` | Block 3 | yes | yes | `WTSA2YR` | **One-third subsample of ages 6+ in BOTH cycles.** Requires WTSA2YR (Subsample A weights). Largest single threat to the Block 3 n. |
| `CBC` | Block 3 | yes | yes | none |  |
| `BIOPRO` | Block 3 | yes | yes | none |  |
| `GHB` | Block 3 | yes | yes | none | Documentation states glycohemoglobin is available for a full sample. |
| `HDL` | Block 3 | yes | yes | none |  |
| `TCHOL` | Block 3 | yes | yes | none |  |
| `TRIGLY` | Block 3 | yes | yes | `WTSAF2YR` | **Fasting subsample of ages 12+ in both cycles**, weight WTSAF2YR. Same objection the brief raises against FAS. |
| `BMX` | Covariate | yes | yes | none |  |
| `SMQ` | Covariate | yes | yes | none |  |
| `ALQ` | Covariate | yes | yes | none |  |
| `MCQ` | Covariate | yes | yes | none |  |
| `DPQ` | Covariate | yes | yes | none |  |
| `BPQ` | Covariate | yes | yes | none |  |

### Direct .xpt URLs

| Stem | _G URL | _H URL |
|---|---|---|
| `DEMO` | https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2011/DataFiles/DEMO_G.xpt | https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2013/DataFiles/DEMO_H.xpt |
| `CFQ` | https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2011/DataFiles/CFQ_G.xpt | https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2013/DataFiles/CFQ_H.xpt |
| `PBCD` | https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2011/DataFiles/PBCD_G.xpt | https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2013/DataFiles/PBCD_H.xpt |
| `IHGEM` | https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2011/DataFiles/IHGEM_G.xpt | https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2013/DataFiles/IHGEM_H.xpt |
| `VITB12` | https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2011/DataFiles/VITB12_G.xpt | https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2013/DataFiles/VITB12_H.xpt |
| `MMA` | https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2011/DataFiles/MMA_G.xpt | https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2013/DataFiles/MMA_H.xpt |
| `FOLFMS` | https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2011/DataFiles/FOLFMS_G.xpt | https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2013/DataFiles/FOLFMS_H.xpt |
| `FOLATE` | https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2011/DataFiles/FOLATE_G.xpt | https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2013/DataFiles/FOLATE_H.xpt |
| `VID` | https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2011/DataFiles/VID_G.xpt | https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2013/DataFiles/VID_H.xpt |
| `CUSEZN` | https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2011/DataFiles/CUSEZN_G.xpt | https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2013/DataFiles/CUSEZN_H.xpt |
| `CBC` | https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2011/DataFiles/CBC_G.xpt | https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2013/DataFiles/CBC_H.xpt |
| `BIOPRO` | https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2011/DataFiles/BIOPRO_G.xpt | https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2013/DataFiles/BIOPRO_H.xpt |
| `GHB` | https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2011/DataFiles/GHB_G.xpt | https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2013/DataFiles/GHB_H.xpt |
| `HDL` | https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2011/DataFiles/HDL_G.xpt | https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2013/DataFiles/HDL_H.xpt |
| `TCHOL` | https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2011/DataFiles/TCHOL_G.xpt | https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2013/DataFiles/TCHOL_H.xpt |
| `TRIGLY` | https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2011/DataFiles/TRIGLY_G.xpt | https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2013/DataFiles/TRIGLY_H.xpt |
| `BMX` | https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2011/DataFiles/BMX_G.xpt | https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2013/DataFiles/BMX_H.xpt |
| `SMQ` | https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2011/DataFiles/SMQ_G.xpt | https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2013/DataFiles/SMQ_H.xpt |
| `ALQ` | https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2011/DataFiles/ALQ_G.xpt | https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2013/DataFiles/ALQ_H.xpt |
| `MCQ` | https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2011/DataFiles/MCQ_G.xpt | https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2013/DataFiles/MCQ_H.xpt |
| `DPQ` | https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2011/DataFiles/DPQ_G.xpt | https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2013/DataFiles/DPQ_H.xpt |
| `BPQ` | https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2011/DataFiles/BPQ_G.xpt | https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2013/DataFiles/BPQ_H.xpt |

### Subsample and weight detail

Quoted from the CDC analytic notes for each file:

- **`PBCD_H`**: analytes were measured "in a one-half subsample of participants aged 12 years and older"; `WTSH2YR` must be used. `PBCD_G` has no weight column and no subsample language. Confirmed in the data: `PBCD_G` has 8,956 rows (equal to `CBC_G`, a full-MEC file) against 5,932 for `PBCD_H`.
- **`CUSEZN_G` and `CUSEZN_H`**: "measured in a one-third subsample of participants aged 6 years and older"; `WTSA2YR` required in both cycles.
- **`TRIGLY_G` and `TRIGLY_H`**: "measured in a fasting subsample of persons 12 years and older"; `WTSAF2YR` required.
- The `FOLFMS` subsample language refers to the historical 1999-2008 surplus specimen projects, not to 2011-2014. `FOLFMS_G` and `FOLFMS_H` carry no weight column.

## 3. Variable verification

Column lists below were read from the downloaded `.xpt` files, not from the documentation and not from memory.

### Cognitive tests (`CFQ_G`, `CFQ_H`)

Both cycles carry an identical 19-column layout. The four component scores are:

| Variable | Content | Observed range _G | Observed range _H |
|---|---|---|---|
| `CFDCST1`, `CFDCST2`, `CFDCST3` | CERAD word list, trials 1 to 3 (sum = immediate recall, 0 to 30) | 0 to 9 (trial 1) | 0 to 10 (trial 1) |
| `CFDCSR` | CERAD delayed recall | 0 to 10 | 0 to 10 |
| `CFDAST` | Animal fluency, total score | 1 to 40 | 3 to 39 |
| `CFDDS` | Digit symbol substitution score | 0 to 100 | 0 to 105 |

The brief describes DSST as 0 to 133. That is the instrument's box count. The observed maxima are 100 and 105, which is consistent and not a problem, but the z-scoring should use observed data rather than an assumed scale maximum.

Reason-not-completed and status variables:

| Variable | Content |
|---|---|
| `CFASTAT` | Cognitive functioning status: 1 = 3 tests, 2 = 2 tests, 3 = 1 test, 4 = ineligible proxy, 5 = ineligible other language, 6 = no test done |
| `CFDCRNC` | CERAD reason not complete (1 to 7) |
| `CFDARNC` | Animal fluency reason not done (1 to 7) |
| `CFDDRNC` | Digit symbol reason not done (1 to 7) |
| `CFDCCS` | CERAD completion status |
| `CFDAPP`, `CFDDPP` | Animal fluency and digit symbol sample practice pretest |
| `CFALANG` | Test language: 1 = English, 2 = Spanish, 3 = Asian language |

Two points that affect the outcome definition:

- `CFASTAT` counts **three** test instruments, not four. CERAD contributes two of the brief's four scores but is a single administration. If CERAD is not done, two of the four scores are lost simultaneously, so a "3 of 4" rule effectively requires CERAD plus at least one of animal fluency or DSST.
- `CFALANG` has a **third** category, Asian language (44 in `_G`, 31 in `_H`). The brief anticipates English and Spanish only.

### Blood metals (`PBCD_G`, `PBCD_H`)

| Concentration | Analyte | Comment or detection flag |
|---|---|---|
| `LBXBPB` (ug/dL) | Lead | `LBDBPBLC` |
| `LBXBCD` (ug/L) | Cadmium | `LBDBCDLC` |
| `LBXTHG` (ug/L) | Total mercury | `LBDTHGLC` |
| `LBXBSE` (ug/L) | Selenium | `LBDBSELC` |
| `LBXBMN` (ug/L) | Manganese | `LBDBMNLC` |

Each comment code is 0 = at or above the detection limit, 1 = below the lower detection limit. Percent below LOD among participants with a measured value:

| Analyte | `_G` | `_H` |
|---|---|---|
| Lead (`LBXBPB`) | 1.1% | 0.0% |
| Cadmium (`LBXBCD`) | 31.2% | 29.0% |
| Total mercury (`LBXTHG`) | 7.1% | 25.7% |
| Selenium (`LBXBSE`) | 0.0% | 0.0% |
| Manganese (`LBXBMN`) | 0.0% | 0.0% |

Cadmium and mercury carry substantial LOD substitution, as the brief predicts. Lead, selenium and manganese have none.

A units caveat: `LBDBCDSI` is labelled nmol/L in the `_G` codebook and umol/L in the `_H` codebook. The observed ratio to `LBXBCD` is 8.90 in both cycles, so both are numerically nmol/L and the `_H` label is a CDC documentation error. Use the conventional-unit columns (`LBX*`) throughout and ignore the SI columns.

### Vitamin B12 (`VITB12_G`, `VITB12_H`)

| Cycle | pg/mL variable | pmol/L variable |
|---|---|---|
| `_G` (2011-2012) | **`LBXB12`** | `LBDB12SI` |
| `_H` (2013-2014) | **`LBDB12`** | `LBDB12SI` |

The pg/mL variable is renamed between cycles. `LBDB12SI` is present in both under the same name and is the safer pooling key.

### WT-prefixed columns in the downloaded files

| File | WT columns |
|---|---|
| `DEMO_G`, `DEMO_H` | `WTINT2YR`, `WTMEC2YR` |
| `CFQ_G`, `CFQ_H` | none (use `WTMEC2YR` from DEMO) |
| `PBCD_G` | none |
| `PBCD_H` | **`WTSH2YR`** |
| `VITB12_G`, `VITB12_H` | none |
| `CBC_G`, `CBC_H` | none |

## 4. Sample size

Counts are unweighted and sequential. No imputation and no cleaning was applied.

| Step | `_G` 2011-2012 | `_H` 2013-2014 | Combined |
|---|---|---|---|
| DEMO rows (all ages) | 9,756 | 10,175 | 19,931 |
| Aged 60+ | 1,791 | 1,841 | 3,632 |
| ... MEC examined (`RIDSTATR` = 2) | 1,687 | 1,785 | 3,472 |
| ... with >= 3 of 4 cognitive scores | 1,454 | 1,670 | **3,124** |
| ... with all 4 cognitive scores | 1,361 | 1,573 | 2,934 |
| ... and all 5 blood metals | 1,388 | 806 | **2,194** |
| ... and B12 (cognition + B12 only) | 1,336 | 1,594 | 2,930 |
| ... cognition + metals + B12 | 1,334 | 786 | **2,120** |

The metals step is where the two cycles diverge sharply: 1,388 in `_G` against 806 in `_H`. That gap is the `PBCD_H` one-half subsample, not nonresponse. Of the 1,841 participants aged 60+ in `_H`, only 881 have a `PBCD_H` record at all.

### Sanity check against the literature

The brief cites published metals-plus-cognition intersections of 1,460 to 2,068. Our cognition-plus-all-five-metals count is **2,194**, just above that range, and cognition plus metals plus B12 is **2,120**, inside it. Published studies additionally drop participants with missing covariates, which we have not yet applied. The counts are therefore consistent with the literature and the brief's 1,400 to 1,900 planning figure.

## 5. Data integrity traps confirmed in this phase

| Trap | Evidence | Consequence if missed |
|---|---|---|
| Zero MEC weight stored as 5.397605e-79 | 104 (`_G`) and 56 (`_H`) records aged 60+, matching the interview-only counts exactly | `WTMEC2YR > 0` keeps interview-only participants; `== 0` matches nothing |
| B12 renamed across cycles | `LBXB12` vs `LBDB12` | Pooled B12 silently all-missing for one cycle |
| `PBCD_H` subsample | `WTSH2YR` present, 5,932 vs 8,956 rows | Metals n overstated by roughly 580 in `_H` |
| No reserved codes in cognitive scores | `CFDCST1` range is 0 to 10 | A blanket 7/9-to-NaN rule deletes valid scores |
| Age top-coded at 80 | 363 (`_G`) and 352 (`_H`) participants at exactly 80 | Age effects compressed in the M0 baseline |
| Cadmium SI unit mislabelled in `_H` | ratio to `LBXBCD` is 8.90 in both cycles | Cross-cycle unit error if SI columns are pooled |

## 6. Methods-benchmark feasibility (IEEE contribution)

The IEEE framing benchmarks the mixture-modelling methods used in environmental epidemiology against ML on predictive rather than inferential criteria. Nothing was installed for this assessment.

### Availability

| Method | R package | CRAN version and date | Python package | Verdict |
|---|---|---|---|---|
| Weighted quantile sum | `gWQS` | 3.0.5, 2023-11-16 | **none** | R only, stale |
| Quantile g-computation | `qgcomp` | 2.18.10, 2026-03-24 | **none** | R only, actively maintained |
| Bayesian kernel machine regression | `bkmr` | 0.2.2, 2022-03-28 | **none** | R only, stale |

PyPI was queried directly for 15 candidate names. There is no maintained Python implementation of any of the three. Two name collisions are worth recording so nobody installs the wrong thing: **`bkmr` on PyPI is a bookmark manager**, and `mixtures` is a mongoengine fixtures library. Neither is related to this literature.

Locally, neither `R`/`Rscript` nor `rpy2` is installed, so any R route starts with an R toolchain install.

### Assessment against a cross-validated prediction protocol

The binding constraint is that each method has to be refitted **inside every training fold** (10-fold, 5 repeats = 50 fits per model) and then produce individual-level predicted probabilities for the held-out fold. That requirement separates the three sharply.

**Quantile g-computation (`qgcomp`) is the clear winner.** It supports `family=binomial()`, and `predict.qgcompfit` accepts new data and re-quantizes it using the cutpoints stored from the original fit. That is exactly the fold-safe behaviour our leakage rule demands. Its predictive engine is also just a GLM on quantized exposures, so the fitted model yields predicted probabilities directly.

**WQS (`gWQS`) fits the protocol badly.** The package splits the data internally into training and validation partitions (`validation=`), which collides with our own outer CV, and the documentation describes no predict method for new data. The recommended settings are 100 bootstrap samples with 100 repeated holdouts; nesting that inside 50 outer folds is 500,000 model fits per specification.

**BKMR (`bkmr`) should be dropped.** Three independent reasons, any one sufficient:

1. **It is unreliable for binary outcomes, which is our primary outcome.** A 2026 simulation study of probit BKMR as implemented in `bkmr` found that only 30 of 431 fits met standard convergence criteria (rank-normalized R-hat <= 1.01 with bulk- and tail-ESS >= 400), roughly a 7% success rate, and warns that "completion of probit BKMR fits in bkmr should not be equated with convergence".
2. **Cost.** It is MCMC with a Gaussian process kernel and spike-and-slab variable selection. Fifty refits inside CV is orders of magnitude beyond the brief's under-2-hours compute budget.
3. **Purpose mismatch.** BKMR's outputs are posterior inclusion probabilities and exposure-response surfaces. It is an inferential instrument, and forcing it into a discrimination comparison is not the fight it is built for.

### Recommendation

**Reimplement quantile g-computation in Python and drop BKMR. Treat WQS as optional.**

Rationale. The non-bootstrap qgcomp estimator is, for prediction purposes, a logistic regression on exposures quantized against training-fold cutpoints. That is roughly 50 lines wrapping a scikit-learn transformer plus `LogisticRegression`, it drops straight into a `Pipeline` so it inherits fold-safe preprocessing for free, and it adds no R dependency inside the CV loop. Validate it once against R `qgcomp` on a fixed dataset with a fixed seed and report the agreement as evidence of correctness. That single validation is the only place R is needed, and it happens outside the CV loop where an rpy2 bridge or a one-off `Rscript` call is harmless.

If a second mixture method is wanted for the benchmark, WQS is reimplementable via constrained optimization (`scipy.optimize`, weights non-negative and summing to one) at moderate cost. Recommend deferring that decision until the M0 to M3 results exist, since the benchmark is only interesting if the biomarker blocks carry signal at all.

This keeps the IEEE contribution intact: the comparison becomes mixture methods versus penalized regression versus tree ensembles, all scored on delta-AUC, AUPRC, calibration and net benefit, which is the reframing section 7 of the brief asks for.

## 7. What this audit did not verify

Scope for Phase 0 was file availability and sample size. The following are recorded as open items rather than settled facts.

**Not downloaded, so availability and subsample status come from the CDC documentation pages only, not from the files themselves:** `MMA`, `FOLFMS`, `FOLATE`, `VID`, `CUSEZN`, `BIOPRO`, `GHB`, `HDL`, `TCHOL`, `TRIGLY`, `IHGEM`, `BMX`, `SMQ`, `ALQ`, `MCQ`, `DPQ`, `BPQ`. Their variable names are therefore **not yet verified against actual columns**. Given that `VITB12` turned out to be renamed across cycles, assume others may be too until checked.

**The Block 3 analytic n is still unknown.** The 2,120 figure covers cognition plus metals plus B12 only. It does not include folate, MMA, vitamin D, trace minerals, CBC, biochemistry, HbA1c or lipids, and it does not include covariates.

**The `CUSEZN` impact is documented but unmeasured.** CDC states a one-third subsample of ages 6+. How that subsample overlaps our 60+ cognition sample was not measured, because `CUSEZN` was outside the download scope for this phase.

**Covariate missingness was not assessed at all.** `INDFMPIR` (income to poverty ratio) and `DMDEDUC2` sit in the M0 baseline, so missingness there directly affects every delta-AUC. `DPQ` (PHQ-9) has a documented skip pattern that has not been examined.

**Reserved codes were checked only for the variables reported here** (CFQ scores and status, PBCD concentrations and comment codes, VITB12). The questionnaire files (`SMQ`, `ALQ`, `MCQ`, `DPQ`, `BPQ`) are where 7/9 and 77/99 codes actually live, and none of those codebooks has been read yet.

### Assumptions made to produce the counts

| Assumption | Alternative | Effect if changed |
|---|---|---|
| Aged 60+ means `RIDAGEYR >= 60` | none reasonable | none |
| Restricted to `RIDSTATR == 2` (MEC examined) | include interview-only | adds 104 and 56 participants who have no lab data anyway |
| CERAD immediate requires all 3 trials (`min_count=3`) | allow 2 of 3, prorated | small increase in the cognition count |
| "3 of 4 scores" counts CERAD immediate and delayed separately | count CERAD as one instrument, matching `CFASTAT` | changes who qualifies; see the `CFASTAT` note in section 3 |
| Metals require all 5 analytes present | require any | no difference: metals are all-or-nothing per participant in both cycles |

### Note on `data/raw/`

`BPQ_G.xpt` was already present in `data/raw/` before this session and was not downloaded, read or modified here. Flagging it because its provenance is unknown to this audit.

## 8. Reproducibility

- CDC listing pages and documentation pages are cached under `data/interim/cdc_cache/`.
- Downloaded `.xpt` files live in `data/raw/` and are never modified.
- Machine-readable audit record: `data/interim/00_audit.json`.
- Re-run with `python3 src/00_audit.py`.

