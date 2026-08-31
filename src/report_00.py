"""Renders the Phase 0 availability audit to markdown. Called by 00_audit.py."""
from __future__ import annotations

import datetime as _dt

CYCLE_LABEL = {"G": "2011-2012", "H": "2013-2014"}

# Curated notes, each verified by reading the CDC documentation page for that
# specific file and cycle. Keyed by stem.
NOTES = {
    "PBCD": "**Asymmetric.** _G is full MEC. _H is a one-half subsample of ages 12+ "
            "and carries its own weight WTSH2YR. Halves the 2013-2014 metals n.",
    "IHGEM": "Same one-half subsample as PBCD in _H (WTSH2YR present in _H only).",
    "CUSEZN": "**One-third subsample of ages 6+ in BOTH cycles.** Requires WTSA2YR "
              "(Subsample A weights). Largest single threat to the Block 3 n.",
    "TRIGLY": "**Fasting subsample of ages 12+ in both cycles**, weight WTSAF2YR. "
              "Same objection the brief raises against FAS.",
    "VITB12": "**Variable renamed between cycles:** LBXB12 in _G, LBDB12 in _H. "
              "LBDB12SI (pmol/L) is present in both and is the safe pooling key.",
    "GHB": "Documentation states glycohemoglobin is available for a full sample.",
    "CFQ": "Administered to MEC participants aged 60+ only. Row count equals the "
           "60+ MEC count exactly in both cycles. Use WTMEC2YR.",
    "DEMO": "Carries WTINT2YR, WTMEC2YR, SDMVSTRA, SDMVPSU. Halve WTMEC2YR when "
            "pooling the two cycles. Age is top-coded at 80.",
}


def _yn(v: bool) -> str:
    return "yes" if v else "**NO**"


def render(audit: dict) -> str:
    counts, comb = audit["counts"], audit["combined"]
    g, h = counts["G"], counts["H"]
    today = _dt.date.today().isoformat()
    L: list[str] = []
    A = L.append

    A("# Phase 0: NHANES 2011-2014 Availability Audit")
    A("")
    A(f"Generated {today} by `src/00_audit.py`. Verified against the CDC data pages "
      "and, where stated, against the downloaded files themselves.")
    A("")
    A("## 1. Headline findings")
    A("")
    A("1. **All 22 required files exist in both cycles.** All five high-priority `_H` "
      "files (`FOLFMS_H`, `FOLATE_H`, `CUSEZN_H`, `MMA_H`, `VITB12_H`) are present. "
      "Nothing from the brief is missing or restricted.")
    A("2. **`PBCD_H` is a one-half subsample, not the full MEC sample.** The brief "
      "states blood metals have no subsample loss. That holds for `PBCD_G` only. "
      "This is the single most consequential finding in this audit.")
    A("3. **`CUSEZN` is a one-third subsample in both cycles.** The brief lists it as "
      "an ordinary Block 3 file. On the documented sampling fraction, requiring it would "
      "be expected to cut the analytic n to roughly a third. The exact overlap with our "
      "60+ cognition sample was not measured (see section 7).")
    A("4. **The B12 variable is renamed between cycles** (`LBXB12` to `LBDB12`). A "
      "merge on the `_G` name yields all-missing B12 for 2013-2014 without erroring.")
    A("5. **NHANES stores a zero MEC weight as 5.4e-79, not 0.0.** A `WTMEC2YR > 0` "
      "filter silently retains interview-only participants.")
    A("6. **The cognitive score variables contain no reserved codes.** `CFDCST1` ranges "
      "0 to 10, so 7 and 9 are legitimate scores. A blanket 7/9-to-NaN rule would corrupt the outcome.")
    A("")

    A("## 2. File availability")
    A("")
    A("`_G` = 2011-2012, `_H` = 2013-2014. URLs are the direct `.xpt` links used by "
      "the download step. Every URL was confirmed to return HTTP 200 and to begin "
      "with the SAS XPORT magic header, so none is a 200-status error page.")
    A("")
    A("| Stem | Block | _G | _H | Special weight | Notes |")
    A("|---|---|---|---|---|---|")
    for r in audit["availability"]:
        wt = sorted(set((r.get("G_wt") or []) + (r.get("H_wt") or [])))
        wt_s = ", ".join(f"`{w}`" for w in wt) if wt else "none"
        A(f'| `{r["stem"]}` | {r["block"]} | {_yn(r["G_present"])} | {_yn(r["H_present"])} '
          f'| {wt_s} | {NOTES.get(r["stem"], "")} |')
    A("")
    A("### Direct .xpt URLs")
    A("")
    A("| Stem | _G URL | _H URL |")
    A("|---|---|---|")
    for r in audit["availability"]:
        A(f'| `{r["stem"]}` | {r["G_url"] or "n/a"} | {r["H_url"] or "n/a"} |')
    A("")

    A("### Subsample and weight detail")
    A("")
    A("Quoted from the CDC analytic notes for each file:")
    A("")
    A("- **`PBCD_H`**: analytes were measured \"in a one-half subsample of participants "
      "aged 12 years and older\"; `WTSH2YR` must be used. `PBCD_G` has no weight column "
      "and no subsample language. Confirmed in the data: `PBCD_G` has 8,956 rows "
      "(equal to `CBC_G`, a full-MEC file) against 5,932 for `PBCD_H`.")
    A("- **`CUSEZN_G` and `CUSEZN_H`**: \"measured in a one-third subsample of "
      "participants aged 6 years and older\"; `WTSA2YR` required in both cycles.")
    A("- **`TRIGLY_G` and `TRIGLY_H`**: \"measured in a fasting subsample of persons "
      "12 years and older\"; `WTSAF2YR` required.")
    A("- The `FOLFMS` subsample language refers to the historical 1999-2008 surplus "
      "specimen projects, not to 2011-2014. `FOLFMS_G` and `FOLFMS_H` carry no weight column.")
    A("")

    A("## 3. Variable verification")
    A("")
    A("Column lists below were read from the downloaded `.xpt` files, not from the "
      "documentation and not from memory.")
    A("")
    A("### Cognitive tests (`CFQ_G`, `CFQ_H`)")
    A("")
    A("Both cycles carry an identical 19-column layout. The four component scores are:")
    A("")
    A("| Variable | Content | Observed range _G | Observed range _H |")
    A("|---|---|---|---|")
    A("| `CFDCST1`, `CFDCST2`, `CFDCST3` | CERAD word list, trials 1 to 3 (sum = immediate recall, 0 to 30) | 0 to 9 (trial 1) | 0 to 10 (trial 1) |")
    A("| `CFDCSR` | CERAD delayed recall | 0 to 10 | 0 to 10 |")
    A("| `CFDAST` | Animal fluency, total score | 1 to 40 | 3 to 39 |")
    A("| `CFDDS` | Digit symbol substitution score | 0 to 100 | 0 to 105 |")
    A("")
    A("The brief describes DSST as 0 to 133. That is the instrument's box count. The "
      "observed maxima are 100 and 105, which is consistent and not a problem, but the "
      "z-scoring should use observed data rather than an assumed scale maximum.")
    A("")
    A("Reason-not-completed and status variables:")
    A("")
    A("| Variable | Content |")
    A("|---|---|")
    A("| `CFASTAT` | Cognitive functioning status: 1 = 3 tests, 2 = 2 tests, 3 = 1 test, 4 = ineligible proxy, 5 = ineligible other language, 6 = no test done |")
    A("| `CFDCRNC` | CERAD reason not complete (1 to 7) |")
    A("| `CFDARNC` | Animal fluency reason not done (1 to 7) |")
    A("| `CFDDRNC` | Digit symbol reason not done (1 to 7) |")
    A("| `CFDCCS` | CERAD completion status |")
    A("| `CFDAPP`, `CFDDPP` | Animal fluency and digit symbol sample practice pretest |")
    A("| `CFALANG` | Test language: 1 = English, 2 = Spanish, 3 = Asian language |")
    A("")
    A("Two points that affect the outcome definition:")
    A("")
    A("- `CFASTAT` counts **three** test instruments, not four. CERAD contributes two "
      "of the brief's four scores but is a single administration. If CERAD is not done, "
      "two of the four scores are lost simultaneously, so a \"3 of 4\" rule effectively "
      "requires CERAD plus at least one of animal fluency or DSST.")
    A("- `CFALANG` has a **third** category, Asian language (44 in `_G`, 31 in `_H`). "
      "The brief anticipates English and Spanish only.")
    A("")
    A("### Blood metals (`PBCD_G`, `PBCD_H`)")
    A("")
    A("| Concentration | Analyte | Comment or detection flag |")
    A("|---|---|---|")
    A("| `LBXBPB` (ug/dL) | Lead | `LBDBPBLC` |")
    A("| `LBXBCD` (ug/L) | Cadmium | `LBDBCDLC` |")
    A("| `LBXTHG` (ug/L) | Total mercury | `LBDTHGLC` |")
    A("| `LBXBSE` (ug/L) | Selenium | `LBDBSELC` |")
    A("| `LBXBMN` (ug/L) | Manganese | `LBDBMNLC` |")
    A("")
    A("Each comment code is 0 = at or above the detection limit, 1 = below the lower "
      "detection limit. Percent below LOD among participants with a measured value:")
    A("")
    A("| Analyte | `_G` | `_H` |")
    A("|---|---|---|")
    for conc, name in zip(
        ["LBXBPB", "LBXBCD", "LBXTHG", "LBXBSE", "LBXBMN"],
        ["Lead", "Cadmium", "Total mercury", "Selenium", "Manganese"],
    ):
        A(f'| {name} (`{conc}`) | {g["pct_below_lod"].get(conc)}% | {h["pct_below_lod"].get(conc)}% |')
    A("")
    A("Cadmium and mercury carry substantial LOD substitution, as the brief predicts. "
      "Lead, selenium and manganese have none.")
    A("")
    A("A units caveat: `LBDBCDSI` is labelled nmol/L in the `_G` codebook and umol/L in "
      "the `_H` codebook. The observed ratio to `LBXBCD` is 8.90 in both cycles, so both "
      "are numerically nmol/L and the `_H` label is a CDC documentation error. Use the "
      "conventional-unit columns (`LBX*`) throughout and ignore the SI columns.")
    A("")
    A("### Vitamin B12 (`VITB12_G`, `VITB12_H`)")
    A("")
    A("| Cycle | pg/mL variable | pmol/L variable |")
    A("|---|---|---|")
    A("| `_G` (2011-2012) | **`LBXB12`** | `LBDB12SI` |")
    A("| `_H` (2013-2014) | **`LBDB12`** | `LBDB12SI` |")
    A("")
    A("The pg/mL variable is renamed between cycles. `LBDB12SI` is present in both under "
      "the same name and is the safer pooling key.")
    A("")
    A("### WT-prefixed columns in the downloaded files")
    A("")
    A("| File | WT columns |")
    A("|---|---|")
    A("| `DEMO_G`, `DEMO_H` | `WTINT2YR`, `WTMEC2YR` |")
    A("| `CFQ_G`, `CFQ_H` | none (use `WTMEC2YR` from DEMO) |")
    A("| `PBCD_G` | none |")
    A("| `PBCD_H` | **`WTSH2YR`** |")
    A("| `VITB12_G`, `VITB12_H` | none |")
    A("| `CBC_G`, `CBC_H` | none |")
    A("")

    A("## 4. Sample size")
    A("")
    A("Counts are unweighted and sequential. No imputation and no cleaning was applied.")
    A("")
    A("| Step | `_G` 2011-2012 | `_H` 2013-2014 | Combined |")
    A("|---|---|---|---|")
    A(f'| DEMO rows (all ages) | {g["demo_rows"]:,} | {h["demo_rows"]:,} | {g["demo_rows"]+h["demo_rows"]:,} |')
    A(f'| Aged 60+ | {g["aged_60plus"]:,} | {h["aged_60plus"]:,} | {comb["aged_60plus"]:,} |')
    A(f'| ... MEC examined (`RIDSTATR` = 2) | {g["mec_examined"]:,} | {h["mec_examined"]:,} | {comb["mec_examined"]:,} |')
    A(f'| ... with >= 3 of 4 cognitive scores | {g["cog_3of4"]:,} | {h["cog_3of4"]:,} | **{comb["cog_3of4"]:,}** |')
    A(f'| ... with all 4 cognitive scores | {g["cog_4of4"]:,} | {h["cog_4of4"]:,} | {comb["cog_4of4"]:,} |')
    A(f'| ... and all 5 blood metals | {g["cog_and_metals"]:,} | {h["cog_and_metals"]:,} | **{comb["cog_and_metals"]:,}** |')
    A(f'| ... and B12 (cognition + B12 only) | {g["cog_and_b12"]:,} | {h["cog_and_b12"]:,} | {comb["cog_and_b12"]:,} |')
    A(f'| ... cognition + metals + B12 | {g["cog_metals_b12"]:,} | {h["cog_metals_b12"]:,} | **{comb["cog_metals_b12"]:,}** |')
    A("")
    A("The metals step is where the two cycles diverge sharply: "
      f'{g["cog_and_metals"]:,} in `_G` against {h["cog_and_metals"]:,} in `_H`. '
      "That gap is the `PBCD_H` one-half subsample, not nonresponse. Of the "
      f'{h["aged_60plus"]:,} participants aged 60+ in `_H`, only {h["pbcd_60plus_rows"]:,} '
      "have a `PBCD_H` record at all.")
    A("")
    A("### Sanity check against the literature")
    A("")
    A(f'The brief cites published metals-plus-cognition intersections of 1,460 to 2,068. '
      f'Our cognition-plus-all-five-metals count is **{comb["cog_and_metals"]:,}**, just above '
      "that range, and cognition plus metals plus B12 is "
      f'**{comb["cog_metals_b12"]:,}**, inside it. Published studies additionally drop '
      "participants with missing covariates, which we have not yet applied. The counts are "
      "therefore consistent with the literature and the brief's 1,400 to 1,900 planning figure.")
    A("")

    A("## 5. Data integrity traps confirmed in this phase")
    A("")
    A("| Trap | Evidence | Consequence if missed |")
    A("|---|---|---|")
    A(f'| Zero MEC weight stored as 5.397605e-79 | {g["aged_60plus"]-g["nonzero_mec_weight"]:,} '
      f'(`_G`) and {h["aged_60plus"]-h["nonzero_mec_weight"]:,} (`_H`) records aged 60+, '
      "matching the interview-only counts exactly | `WTMEC2YR > 0` keeps interview-only "
      "participants; `== 0` matches nothing |")
    A("| B12 renamed across cycles | `LBXB12` vs `LBDB12` | Pooled B12 silently all-missing for one cycle |")
    A("| `PBCD_H` subsample | `WTSH2YR` present, 5,932 vs 8,956 rows | Metals n overstated by roughly 580 in `_H` |")
    A("| No reserved codes in cognitive scores | `CFDCST1` range is 0 to 10 | A blanket 7/9-to-NaN rule deletes valid scores |")
    A("| Age top-coded at 80 | 363 (`_G`) and 352 (`_H`) participants at exactly 80 | Age effects compressed in the M0 baseline |")
    A("| Cadmium SI unit mislabelled in `_H` | ratio to `LBXBCD` is 8.90 in both cycles | Cross-cycle unit error if SI columns are pooled |")
    A("")

    A("## 6. Methods-benchmark feasibility (IEEE contribution)")
    A("")
    A("The IEEE framing benchmarks the mixture-modelling methods used in environmental "
      "epidemiology against ML on predictive rather than inferential criteria. Nothing "
      "was installed for this assessment.")
    A("")
    A("### Availability")
    A("")
    A("| Method | R package | CRAN version and date | Python package | Verdict |")
    A("|---|---|---|---|---|")
    A("| Weighted quantile sum | `gWQS` | 3.0.5, 2023-11-16 | **none** | R only, stale |")
    A("| Quantile g-computation | `qgcomp` | 2.18.10, 2026-03-24 | **none** | R only, actively maintained |")
    A("| Bayesian kernel machine regression | `bkmr` | 0.2.2, 2022-03-28 | **none** | R only, stale |")
    A("")
    A("PyPI was queried directly for 15 candidate names. There is no maintained Python "
      "implementation of any of the three. Two name collisions are worth recording so "
      "nobody installs the wrong thing: **`bkmr` on PyPI is a bookmark manager**, and "
      "`mixtures` is a mongoengine fixtures library. Neither is related to this literature.")
    A("")
    A("Locally, neither `R`/`Rscript` nor `rpy2` is installed, so any R route starts "
      "with an R toolchain install.")
    A("")
    A("### Assessment against a cross-validated prediction protocol")
    A("")
    A("The binding constraint is that each method has to be refitted **inside every "
      "training fold** (10-fold, 5 repeats = 50 fits per model) and then produce "
      "individual-level predicted probabilities for the held-out fold. That requirement "
      "separates the three sharply.")
    A("")
    A("**Quantile g-computation (`qgcomp`) is the clear winner.** It supports "
      "`family=binomial()`, and `predict.qgcompfit` accepts new data and re-quantizes it "
      "using the cutpoints stored from the original fit. That is exactly the fold-safe "
      "behaviour our leakage rule demands. Its predictive engine is also just a GLM on "
      "quantized exposures, so the fitted model yields predicted probabilities directly.")
    A("")
    A("**WQS (`gWQS`) fits the protocol badly.** The package splits the data internally "
      "into training and validation partitions (`validation=`), which collides with our "
      "own outer CV, and the documentation describes no predict method for new data. The "
      "recommended settings are 100 bootstrap samples with 100 repeated holdouts; nesting "
      "that inside 50 outer folds is 500,000 model fits per specification.")
    A("")
    A("**BKMR (`bkmr`) should be dropped.** Three independent reasons, any one sufficient:")
    A("")
    A("1. **It is unreliable for binary outcomes, which is our primary outcome.** A 2026 "
      "simulation study of probit BKMR as implemented in `bkmr` found that only 30 of 431 "
      "fits met standard convergence criteria (rank-normalized R-hat <= 1.01 with bulk- "
      "and tail-ESS >= 400), roughly a 7% success rate, and warns that \"completion of "
      "probit BKMR fits in bkmr should not be equated with convergence\".")
    A("2. **Cost.** It is MCMC with a Gaussian process kernel and spike-and-slab variable "
      "selection. Fifty refits inside CV is orders of magnitude beyond the brief's "
      "under-2-hours compute budget.")
    A("3. **Purpose mismatch.** BKMR's outputs are posterior inclusion probabilities and "
      "exposure-response surfaces. It is an inferential instrument, and forcing it into a "
      "discrimination comparison is not the fight it is built for.")
    A("")
    A("### Recommendation")
    A("")
    A("**Reimplement quantile g-computation in Python and drop BKMR. Treat WQS as optional.**")
    A("")
    A("Rationale. The non-bootstrap qgcomp estimator is, for prediction purposes, a "
      "logistic regression on exposures quantized against training-fold cutpoints. That is "
      "roughly 50 lines wrapping a scikit-learn transformer plus `LogisticRegression`, it "
      "drops straight into a `Pipeline` so it inherits fold-safe preprocessing for free, "
      "and it adds no R dependency inside the CV loop. Validate it once against R `qgcomp` "
      "on a fixed dataset with a fixed seed and report the agreement as evidence of "
      "correctness. That single validation is the only place R is needed, and it happens "
      "outside the CV loop where an rpy2 bridge or a one-off `Rscript` call is harmless.")
    A("")
    A("If a second mixture method is wanted for the benchmark, WQS is reimplementable via "
      "constrained optimization (`scipy.optimize`, weights non-negative and summing to "
      "one) at moderate cost. Recommend deferring that decision until the M0 to M3 results "
      "exist, since the benchmark is only interesting if the biomarker blocks carry signal "
      "at all.")
    A("")
    A("This keeps the IEEE contribution intact: the comparison becomes mixture methods "
      "versus penalized regression versus tree ensembles, all scored on delta-AUC, AUPRC, "
      "calibration and net benefit, which is the reframing section 7 of the brief asks for.")
    A("")
    A("## 7. What this audit did not verify")
    A("")
    A("Scope for Phase 0 was file availability and sample size. The following are "
      "recorded as open items rather than settled facts.")
    A("")
    A("**Not downloaded, so availability and subsample status come from the CDC "
      "documentation pages only, not from the files themselves:** `MMA`, `FOLFMS`, "
      "`FOLATE`, `VID`, `CUSEZN`, `BIOPRO`, `GHB`, `HDL`, `TCHOL`, `TRIGLY`, `IHGEM`, "
      "`BMX`, `SMQ`, `ALQ`, `MCQ`, `DPQ`, `BPQ`. Their variable names are therefore "
      "**not yet verified against actual columns**. Given that `VITB12` turned out to be "
      "renamed across cycles, assume others may be too until checked.")
    A("")
    A("**The Block 3 analytic n is still unknown.** The 2,120 figure covers cognition "
      "plus metals plus B12 only. It does not include folate, MMA, vitamin D, trace "
      "minerals, CBC, biochemistry, HbA1c or lipids, and it does not include covariates.")
    A("")
    A("**The `CUSEZN` impact is documented but unmeasured.** CDC states a one-third "
      "subsample of ages 6+. How that subsample overlaps our 60+ cognition sample was "
      "not measured, because `CUSEZN` was outside the download scope for this phase.")
    A("")
    A("**Covariate missingness was not assessed at all.** `INDFMPIR` (income to poverty "
      "ratio) and `DMDEDUC2` sit in the M0 baseline, so missingness there directly "
      "affects every delta-AUC. `DPQ` (PHQ-9) has a documented skip pattern that has not "
      "been examined.")
    A("")
    A("**Reserved codes were checked only for the variables reported here** (CFQ scores "
      "and status, PBCD concentrations and comment codes, VITB12). The questionnaire "
      "files (`SMQ`, `ALQ`, `MCQ`, `DPQ`, `BPQ`) are where 7/9 and 77/99 codes actually "
      "live, and none of those codebooks has been read yet.")
    A("")
    A("### Assumptions made to produce the counts")
    A("")
    A("| Assumption | Alternative | Effect if changed |")
    A("|---|---|---|")
    A("| Aged 60+ means `RIDAGEYR >= 60` | none reasonable | none |")
    A("| Restricted to `RIDSTATR == 2` (MEC examined) | include interview-only | adds 104 and 56 participants who have no lab data anyway |")
    A("| CERAD immediate requires all 3 trials (`min_count=3`) | allow 2 of 3, prorated | small increase in the cognition count |")
    A("| \"3 of 4 scores\" counts CERAD immediate and delayed separately | count CERAD as one instrument, matching `CFASTAT` | changes who qualifies; see the `CFASTAT` note in section 3 |")
    A("| Metals require all 5 analytes present | require any | no difference: metals are all-or-nothing per participant in both cycles |")
    A("")
    A("### Note on `data/raw/`")
    A("")
    A("`BPQ_G.xpt` was already present in `data/raw/` before this session and was not "
      "downloaded, read or modified here. Flagging it because its provenance is unknown "
      "to this audit.")
    A("")
    A("## 8. Reproducibility")
    A("")
    A("- CDC listing pages and documentation pages are cached under `data/interim/cdc_cache/`.")
    A("- Downloaded `.xpt` files live in `data/raw/` and are never modified.")
    A("- Machine-readable audit record: `data/interim/00_audit.json`.")
    A("- Re-run with `python3 src/00_audit.py`.")
    A("")
    return "\n".join(L) + "\n"
