"""
Phase 6: pre-specified sensitivity analyses.

Every analysis here was declared in PREREGISTRATION.md section 7 before any
modeling. Each re-estimates the primary contrast, delta-AUC(M3 - M0) under the
L2-penalized logistic model, with one condition changed.

All preprocessing stays inside the CV folds, including the multiple imputation
used for the full-sample analysis.

Outputs
    output/tables/06_sensitivity.csv
    data/interim/06_sensitivity.json

Run:  python3 src/06_sensitivity.py
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.experimental import enable_iterative_imputer  # noqa: F401
from sklearn.impute import IterativeImputer, SimpleImputer
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import RepeatedStratifiedKFold, RepeatedKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

ROOT = Path(__file__).resolve().parent.parent
INTERIM = ROOT / "data" / "interim"
TABLES = ROOT / "output" / "tables"

SEED = 20260831
N_SPLITS, N_REPEATS, N_BOOT = 10, 5, 2000

DEMO = ["RIDAGEYR", "RIAGENDR", "RIDRETH3", "DMDEDUC2", "INDFMPIR"]
METALS = ["log_LBXBPB", "log_LBXBCD", "log_LBXTHG", "log_LBXBSE", "log_LBXBMN"]
NUTR = ["log_LBDB12SI", "log_LBXMMASI", "LBDFOT", "LBDRFO", "LBXVIDMS", "LBXGH",
        "LBDHDD", "LBXTC", "LBXSTR", "LBXSAL", "LBXSIR", "egfr", "nlr", "plr",
        "log_sii"]
CATEGORICAL = {"RIDRETH3", "DMDEDUC2"}


def pipeline(features: list[str], impute: str = "median", task: str = "clf") -> Pipeline:
    cats = [f for f in features if f in CATEGORICAL]
    nums = [f for f in features if f not in CATEGORICAL]
    num_impute = (IterativeImputer(random_state=SEED, max_iter=10, sample_posterior=True)
                  if impute == "mice" else SimpleImputer(strategy="median"))
    pre = ColumnTransformer([
        ("num", Pipeline([("impute", num_impute), ("scale", StandardScaler())]), nums),
        ("cat", Pipeline([("impute", SimpleImputer(strategy="most_frequent")),
                          ("onehot", OneHotEncoder(handle_unknown="ignore",
                                                   sparse_output=False))]), cats),
    ], remainder="drop")
    model = (Ridge(alpha=1.0, random_state=SEED) if task == "reg"
             else LogisticRegression(l1_ratio=0, solver="lbfgs", max_iter=5000,
                                     C=1.0, random_state=SEED))
    return Pipeline([("pre", pre), ("clf", model)])


def oof_probs(X: pd.DataFrame, y: np.ndarray, features: list[str],
              impute: str) -> np.ndarray:
    cv = RepeatedStratifiedKFold(n_splits=N_SPLITS, n_repeats=N_REPEATS,
                                 random_state=SEED)
    oof = np.full((N_REPEATS, len(y)), np.nan)
    for i, (tr, te) in enumerate(cv.split(X, y)):
        pipe = pipeline(features, impute)
        pipe.fit(X.iloc[tr], y[tr])
        oof[i // N_SPLITS, te] = pipe.predict_proba(X.iloc[te])[:, 1]
    return oof.mean(axis=0)


def delta_with_ci(y: np.ndarray, pa: np.ndarray, pb: np.ndarray,
                  rng: np.random.Generator) -> dict:
    n = len(y)
    d = np.empty(N_BOOT)
    k = 0
    while k < N_BOOT:
        idx = rng.integers(0, n, n)
        if y[idx].min() == y[idx].max():
            continue
        d[k] = roc_auc_score(y[idx], pa[idx]) - roc_auc_score(y[idx], pb[idx])
        k += 1
    lo, hi = np.percentile(d, [2.5, 97.5])
    return {"auc_m3": float(roc_auc_score(y, pa)), "auc_m0": float(roc_auc_score(y, pb)),
            "delta_auc": float(roc_auc_score(y, pa) - roc_auc_score(y, pb)),
            "ci_low": float(lo), "ci_high": float(hi),
            "excludes_zero": bool(lo > 0 or hi < 0)}


def run(df: pd.DataFrame, label: str, name: str, impute: str,
        rng: np.random.Generator) -> dict:
    """One sensitivity condition: delta-AUC(M3 - M0)."""
    d = df[df[label].notna()]
    y = d[label].to_numpy(dtype=int)
    p3 = oof_probs(d[DEMO + METALS + NUTR], y, DEMO + METALS + NUTR, impute)
    p0 = oof_probs(d[DEMO], y, DEMO, impute)
    out = {"analysis": name, "n": int(len(d)), "events": int(y.sum()),
           **delta_with_ci(y, p3, p0, rng)}
    print(f"  {name:<42} n={out['n']:<5} delta-AUC={out['delta_auc']:+.4f} "
          f"[{out['ci_low']:+.4f}, {out['ci_high']:+.4f}]")
    return out


def continuous_outcome(df: pd.DataFrame) -> dict:
    """Composite z as a regression outcome. Reports cross-validated R squared."""
    cv = RepeatedKFold(n_splits=N_SPLITS, n_repeats=N_REPEATS, random_state=SEED)
    y = df["composite_z"].to_numpy()
    res = {}
    for name, feats in [("M0", DEMO), ("M3", DEMO + METALS + NUTR)]:
        oof = np.full((N_REPEATS, len(y)), np.nan)
        for i, (tr, te) in enumerate(cv.split(df)):
            pipe = pipeline(feats, "median", task="reg")
            pipe.fit(df.iloc[tr][feats], y[tr])
            oof[i // N_SPLITS, te] = pipe.predict(df.iloc[te][feats])
        pred = oof.mean(axis=0)
        ss_res = float(np.sum((y - pred) ** 2))
        ss_tot = float(np.sum((y - y.mean()) ** 2))
        res[name] = 1 - ss_res / ss_tot
    res["delta_r2"] = res["M3"] - res["M0"]
    return res


def main() -> None:
    TABLES.mkdir(parents=True, exist_ok=True)
    full = pd.read_parquet(INTERIM / "02_outcome.parquet")
    keep = set(pd.read_csv(INTERIM / "02_analytic_seqn.csv").SEQN)
    locked = full[full.SEQN.isin(keep)].reset_index(drop=True)
    rng = np.random.default_rng(SEED)

    print("Pre-specified sensitivity analyses, delta-AUC(M3 - M0), logistic\n")
    rows = [run(locked, "low_cog", "primary (reference)", "median", rng)]

    # 1. Alternative outcome cutoffs.
    rows.append(run(locked, "low_cog_p20", "cutoff at 20th percentile", "median", rng))
    rows.append(run(locked, "low_cog_p10", "cutoff at 10th percentile", "median", rng))

    # 3. DSST not completed recoded as low performance.
    d = locked.copy()
    unable = d.CFDDRNC.notna()
    d["low_cog_dsst"] = d.low_cog.where(~unable, 1.0)
    rows.append(run(d, "low_cog_dsst", f"DSST unable coded low (n={int(unable.sum())})",
                    "median", rng))

    # 4. English-only administration. Excludes Spanish and Asian-language.
    eng = locked[locked.CFALANG == 1]
    rows.append(run(eng, "low_cog", "English-only administration", "median", rng))

    # 5. Multiple imputation on the full labelled sample, fitted in-fold.
    labelled = full[full.low_cog.notna()].reset_index(drop=True)
    rows.append(run(labelled, "low_cog", "MICE on full labelled sample", "mice", rng))

    # 6. Leave-one-block-out on the M3 sample.
    y = locked.low_cog.to_numpy(dtype=int)
    p_full = oof_probs(locked[DEMO + METALS + NUTR], y, DEMO + METALS + NUTR, "median")
    lobo = []
    for drop_name, drop in [("without metals", METALS), ("without nutritional", NUTR)]:
        feats = [f for f in DEMO + METALS + NUTR if f not in drop]
        p = oof_probs(locked[feats], y, feats, "median")
        r = delta_with_ci(y, p_full, p, rng)
        lobo.append({"analysis": f"leave-one-block-out, {drop_name}", **r})
        print(f"  {'LOBO ' + drop_name:<42} delta-AUC={r['delta_auc']:+.4f} "
              f"[{r['ci_low']:+.4f}, {r['ci_high']:+.4f}]")

    cont = continuous_outcome(locked)
    print(f"\n  continuous composite: R2 M0={cont['M0']:.4f}  M3={cont['M3']:.4f}  "
          f"delta={cont['delta_r2']:+.4f}")

    table = pd.DataFrame(rows + lobo).round(4)
    table.to_csv(TABLES / "06_sensitivity.csv", index=False)
    (INTERIM / "06_sensitivity.json").write_text(json.dumps(
        {"sensitivity": table.to_dict(orient="records"),
         "continuous_outcome_r2": cont}, indent=1))
    print("\nwrote", TABLES / "06_sensitivity.csv")


if __name__ == "__main__":
    main()
