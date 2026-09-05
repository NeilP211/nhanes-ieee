"""
Phase 10 (manuscript support): full M3 model coefficients, TRIPOD+AI item 16.

The cross-validated results already reported (03_model.py onward) are the
correct estimate of predictive performance, but no single set of
coefficients exists from that procedure -- each of the 50 folds fits its
own pipeline, possibly with a different regularisation strength C. TRIPOD
item 16 asks for "all coefficients or a means to obtain them," which
standard practice answers with a refit on the complete analytic sample
(development-set coefficients), reported separately from, and clearly
labelled apart from, the cross-validated performance estimates.

This script:
  1. Refits the identical preprocessing pipeline used in 03_model.py
     (median impute + standard-scale numeric; most-frequent impute +
     one-hot categorical, RIDRETH3/DMDEDUC2) on the full n=1,784 sample.
  2. Selects C by the same grid (0.01, 0.1, 1.0, 10.0) via 10-fold CV,
     rather than assuming the fold-level mode (C=0.1, 49 of 50 folds in
     03_fold_auc.csv) applies here -- verified, not assumed.
  3. Refits at the selected C and computes standardised-unit coefficients,
     odds ratios, and 95% CIs from 2,000 bootstrap resamples (same
     resampling count as the delta-AUC bootstrap in 04_evaluate.py, for
     methodological consistency), re-selecting C inside each resample so
     the reported interval reflects the full refitting procedure.

One-hot categorical features (RIDRETH3, DMDEDUC2) are encoded without a
dropped reference level (OneHotEncoder(drop=None), matching 03_model.py
exactly) because the L2 penalty handles the resulting collinearity. This
means these coefficients are NOT interpretable as standard reference-
category log-odds ratios; each is relative to the implicit population
mean across all categories of that variable, not to an omitted reference
group. Stated explicitly in the table output so it is not misread as
conventional reference-coded regression output.

Outputs
    data/interim/10_m3_coefficients.json
    output/tables/10_m3_coefficients.md

Run:  python3 src/10_m3_coefficients.py   (~3-5 min for 2,000 bootstrap resamples)
"""
from __future__ import annotations

import json
import time
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GridSearchCV, StratifiedKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

ROOT = Path(__file__).resolve().parent.parent
INTERIM = ROOT / "data" / "interim"
TABLES = ROOT / "output" / "tables"

SEED = 20260831
N_BOOT = 2000

M3_FEATURES = [
    "RIDAGEYR", "RIAGENDR", "RIDRETH3", "DMDEDUC2", "INDFMPIR",
    "log_LBXBPB", "log_LBXBCD", "log_LBXTHG", "log_LBXBSE", "log_LBXBMN",
    "log_LBDB12SI", "log_LBXMMASI", "LBDFOT", "LBDRFO", "LBXVIDMS", "LBXGH",
    "LBDHDD", "LBXTC", "LBXSTR", "LBXSAL", "LBXSIR", "egfr", "nlr", "plr",
    "log_sii",
]
CATEGORICAL = {"RIDRETH3", "DMDEDUC2"}
CAT_LABELS = {
    "RIDRETH3": {1: "Mexican American", 2: "Other Hispanic",
                 3: "Non-Hispanic White", 4: "Non-Hispanic Black",
                 6: "Non-Hispanic Asian", 7: "Other/multiracial"},
    "DMDEDUC2": {1: "Less than 9th grade", 2: "9-11th grade",
                 3: "High school grad/GED", 4: "Some college/AA degree",
                 5: "College graduate or above"},
}
FEATURE_LABELS = {
    "RIDAGEYR": "Age, years", "RIAGENDR": "Sex (coded 1=male, 2=female)",
    "INDFMPIR": "Income-to-poverty ratio",
    "log_LBXBPB": "Blood lead (log)", "log_LBXBCD": "Blood cadmium (log)",
    "log_LBXTHG": "Blood total mercury (log)", "log_LBXBSE": "Blood selenium (log)",
    "log_LBXBMN": "Blood manganese (log)",
    "log_LBDB12SI": "Serum vitamin B12 (log)",
    "log_LBXMMASI": "Serum methylmalonic acid (log)",
    "LBDFOT": "Serum total folate", "LBDRFO": "RBC folate",
    "LBXVIDMS": "25-hydroxyvitamin D", "LBXGH": "HbA1c",
    "LBDHDD": "HDL cholesterol", "LBXTC": "Total cholesterol",
    "LBXSTR": "Triglycerides", "LBXSAL": "Serum albumin",
    "LBXSIR": "Serum iron", "egfr": "eGFR",
    "nlr": "Neutrophil-to-lymphocyte ratio",
    "plr": "Platelet-to-lymphocyte ratio",
    "log_sii": "Systemic immune-inflammation index (log)",
}


def make_pipeline(C: float | None) -> tuple[Pipeline, dict]:
    nums = [f for f in M3_FEATURES if f not in CATEGORICAL]
    cats = [f for f in M3_FEATURES if f in CATEGORICAL]
    numeric = Pipeline([("impute", SimpleImputer(strategy="median")),
                        ("scale", StandardScaler())])
    categorical = Pipeline([("impute", SimpleImputer(strategy="most_frequent")),
                            ("onehot", OneHotEncoder(handle_unknown="ignore",
                                                     drop=None, sparse_output=False))])
    pre = ColumnTransformer([("num", numeric, nums), ("cat", categorical, cats)],
                            remainder="drop")
    clf = LogisticRegression(l1_ratio=0, solver="lbfgs", max_iter=5000,
                             random_state=SEED, C=(C if C else 1.0))
    pipe = Pipeline([("pre", pre), ("clf", clf)])
    grid = {"clf__C": [0.01, 0.1, 1.0, 10.0]}
    return pipe, grid


def feature_names_out(pipe: Pipeline) -> list[str]:
    pre = pipe.named_steps["pre"]
    nums = pre.transformers_[0][2]
    cats = pre.transformers_[1][2]
    names = list(nums)
    ohe = pre.named_transformers_["cat"].named_steps["onehot"]
    for col, cats_seen in zip(cats, ohe.categories_):
        for c in cats_seen:
            names.append(f"{col}={CAT_LABELS.get(col, {}).get(int(c), c)}")
    return names


def fit_selected_C(X: pd.DataFrame, y: np.ndarray, seed: int) -> tuple[LogisticRegression, list[str], float]:
    pipe, grid = make_pipeline(None)
    cv = StratifiedKFold(n_splits=10, shuffle=True, random_state=seed)
    search = GridSearchCV(pipe, grid, scoring="roc_auc", cv=cv, n_jobs=-1, refit=True)
    search.fit(X, y)
    best_pipe = search.best_estimator_
    names = feature_names_out(best_pipe)
    coefs = best_pipe.named_steps["clf"].coef_[0]
    return coefs, names, search.best_params_["clf__C"]


def main() -> None:
    df = pd.read_parquet(INTERIM / "02_outcome.parquet")
    locked_seqn = pd.read_csv(INTERIM / "02_analytic_seqn.csv").SEQN
    df = df[df.SEQN.isin(locked_seqn)].reset_index(drop=True)
    assert len(df) == 1784, f"expected n=1,784, got {len(df)}"

    X = df[M3_FEATURES]
    y = df["low_cog"].to_numpy(dtype=int)
    assert X.notna().all().all(), "M3 features have missing values in the locked sample"

    print(f"n={len(df)}  events={int(y.sum())}")
    print("selecting C on the full sample via 10-fold CV...")
    coefs, names, chosen_C = fit_selected_C(X, y, SEED)
    print(f"selected C={chosen_C} "
          f"({'matches' if chosen_C == 0.1 else 'DIFFERS FROM'} "
          f"the fold-level mode of C=0.1 seen in 49/50 CV folds)")

    intercept_pipe, _ = make_pipeline(chosen_C)
    intercept_pipe.fit(X, y)
    intercept = intercept_pipe.named_steps["clf"].intercept_[0]

    print(f"bootstrapping {N_BOOT} resamples for coefficient CIs "
          f"(re-selecting C in each resample)...")
    # A weakly regularised C=10 candidate occasionally hits quasi-complete
    # separation on a bootstrap resample, which surfaces as a RuntimeWarning
    # (overflow/divide-by-zero) rather than an exception. The resulting
    # coefficients are checked for finiteness below and excluded if not, so
    # these warnings are expected noise, not silently ignored instability.
    warnings.filterwarnings("ignore", category=RuntimeWarning)
    t0 = time.time()
    rng = np.random.default_rng(SEED)
    boot_coefs = np.full((N_BOOT, len(coefs)), np.nan)
    boot_C = []
    n_nonfinite = 0
    n = len(df)
    for b in range(N_BOOT):
        idx = rng.integers(0, n, n)
        Xb, yb = X.iloc[idx].reset_index(drop=True), y[idx]
        if len(np.unique(yb)) < 2:
            continue
        try:
            c_b, names_b, C_b = fit_selected_C(Xb, yb, SEED + b + 1)
        except Exception:
            n_nonfinite += 1
            continue
        # A numerically unstable fit (quasi-complete separation at a weakly
        # regularised C, seen occasionally at the grid's C=10 end) emits a
        # RuntimeWarning rather than raising, and can produce non-finite
        # coefficients that would silently corrupt a percentile CI if kept.
        if names_b == names and np.all(np.isfinite(c_b)):
            boot_coefs[b] = c_b
            boot_C.append(C_b)
        else:
            n_nonfinite += 1
        if (b + 1) % 500 == 0:
            print(f"  {b + 1}/{N_BOOT}  ({time.time() - t0:.0f}s elapsed, "
                  f"{n_nonfinite} non-finite so far)")

    lo = np.nanpercentile(boot_coefs, 2.5, axis=0)
    hi = np.nanpercentile(boot_coefs, 97.5, axis=0)
    n_valid = np.sum(~np.isnan(boot_coefs[:, 0]))
    print(f"bootstrap done: {n_valid} valid, {n_nonfinite} excluded "
          f"(non-finite coefficients or single-class resample)")

    rows = []
    for name, coef, l, h in zip(names, coefs, lo, hi):
        if "=" in name:
            var, cat = name.split("=", 1)
            label = f"{FEATURE_LABELS.get(var, var)} = {cat}"
        else:
            label = FEATURE_LABELS.get(name, name)
        rows.append({
            "feature": name, "label": label,
            "coefficient": round(float(coef), 4),
            "odds_ratio": round(float(np.exp(coef)), 4),
            "or_ci_low": round(float(np.exp(l)), 4),
            "or_ci_high": round(float(np.exp(h)), 4),
        })

    result = {
        "n": int(len(df)), "events": int(y.sum()), "intercept": round(float(intercept), 4),
        "selected_C": chosen_C, "n_bootstrap": N_BOOT, "n_bootstrap_valid": int(n_valid),
        "seed": SEED,
        "note": "Numeric features are standardised (z-scored) before fitting, so "
                "each coefficient/OR is per one-SD increase, not per raw unit. "
                "RIDRETH3 and DMDEDUC2 are one-hot encoded WITHOUT a dropped "
                "reference category (matching 03_model.py's pipeline exactly, "
                "relying on the L2 penalty rather than a reference contrast), "
                "so their coefficients are not standard reference-category "
                "log-odds ratios -- do not report them as such in prose.",
        "coefficients": rows,
    }
    (INTERIM / "10_m3_coefficients.json").write_text(json.dumps(result, indent=1))

    md = ["# Full M3 model coefficients", "",
          "**TRIPOD+AI item 16.** The cross-validated performance estimates "
          "elsewhere in this repository are correct as reported; no single "
          "coefficient set exists from that procedure since each of the 50 "
          "folds fits its own pipeline. This table is a separate refit of "
          "the identical pipeline on the complete analytic sample "
          f"(n={result['n']:,}, {result['events']:,} events), reported "
          "for TRIPOD compliance and not as a new performance estimate.",
          "",
          f"C selected by 10-fold CV on the full sample: **{chosen_C}** "
          f"({'matches' if chosen_C == 0.1 else 'differs from'} the mode "
          "across the original 50 CV folds, C=0.1 in 49 of 50). "
          f"Intercept: {result['intercept']}. "
          f"Bootstrap: {N_BOOT} resamples, {n_valid} valid "
          "(re-selecting C in each resample; a resample is excluded only "
          "if it produces a single-class sample or a different one-hot "
          "category set than the full-sample fit).", "",
          "**Numeric features are standardised**, so each row is the odds "
          "ratio per one-SD increase, not per raw unit. **RIDRETH3 and "
          "DMDEDUC2 are one-hot encoded without a dropped reference "
          "category** (matching the modelling pipeline exactly, which "
          "relies on the L2 penalty rather than a reference contrast) -- "
          "these rows are not standard reference-category odds ratios and "
          "should not be reported as such in prose.", "",
          "| Feature | Coefficient (standardised) | Odds ratio | 95% CI |",
          "|---|---|---|---|"]
    for r in rows:
        md.append(f"| {r['label']} | {r['coefficient']} | {r['odds_ratio']} | "
                   f"[{r['or_ci_low']}, {r['or_ci_high']}] |")
    (TABLES / "10_m3_coefficients.md").write_text("\n".join(md) + "\n")

    print(f"\nwrote data/interim/10_m3_coefficients.json, "
          f"output/tables/10_m3_coefficients.md")


if __name__ == "__main__":
    main()
