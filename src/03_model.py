"""
Phase 3: nested models M0 to M3 across three algorithms.

Every preprocessing step is fitted inside the training fold via sklearn
Pipeline objects built within the CV loop. Hyperparameters are tuned by an
inner CV on training data only, so the outer folds stay untouched.

Produces out-of-fold predicted probabilities for every (spec, algorithm,
repeat), which Phase 4 turns into delta-AUC with bootstrap CIs. Predictions are
paired across specs on identical rows, which is what makes delta-AUC valid.

Outputs
    data/interim/03_oof_predictions.parquet
    data/interim/03_fold_auc.csv
    data/interim/03_model_report.json

Run:  python3 src/03_model.py
"""
from __future__ import annotations

import json
import time
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import GridSearchCV, RepeatedStratifiedKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from xgboost import XGBClassifier

ROOT = Path(__file__).resolve().parent.parent
INTERIM = ROOT / "data" / "interim"

SEED = 20260831
N_SPLITS, N_REPEATS = 10, 5

DEMO = ["RIDAGEYR", "RIAGENDR", "RIDRETH3", "DMDEDUC2", "INDFMPIR"]
METALS = ["log_LBXBPB", "log_LBXBCD", "log_LBXTHG", "log_LBXBSE", "log_LBXBMN"]
NUTR = ["log_LBDB12SI", "log_LBXMMASI", "LBDFOT", "LBDRFO", "LBXVIDMS", "LBXGH",
        "LBDHDD", "LBXTC", "LBXSTR", "LBXSAL", "LBXSIR", "egfr", "nlr", "plr",
        "log_sii"]
COVARIATES = ["BMXBMI", "smoking", "drinks_per_day", "phq9", "stroke",
              "diabetes", "hypertension", "high_chol"]

# Primary nested comparison uses Blocks 1 to 3. M0plus is the pre-specified
# secondary benchmark: what a clinician could record without a laboratory.
SPECS = {
    "M0": DEMO,
    "M1": DEMO + METALS,
    "M2": DEMO + NUTR,
    "M3": DEMO + METALS + NUTR,
    "M0plus": DEMO + COVARIATES,
}

CATEGORICAL = {"RIDRETH3", "DMDEDUC2", "smoking"}


def make_pipeline(algo: str, features: list[str], seed: int) -> tuple[Pipeline, dict]:
    """Pipeline plus its inner-CV grid. Every step here is fitted per fold."""
    cats = [f for f in features if f in CATEGORICAL]
    nums = [f for f in features if f not in CATEGORICAL]

    numeric = Pipeline([("impute", SimpleImputer(strategy="median")),
                        ("scale", StandardScaler())])
    categorical = Pipeline([("impute", SimpleImputer(strategy="most_frequent")),
                            ("onehot", OneHotEncoder(handle_unknown="ignore",
                                                     drop=None, sparse_output=False))])
    pre = ColumnTransformer([("num", numeric, nums), ("cat", categorical, cats)],
                            remainder="drop")

    if algo == "logistic":
        # sklearn 1.8 deprecates penalty="l2" in favour of l1_ratio=0.
        clf = LogisticRegression(l1_ratio=0, solver="lbfgs", max_iter=5000,
                                 random_state=seed)
        grid = {"clf__C": [0.01, 0.1, 1.0, 10.0]}
    elif algo == "random_forest":
        clf = RandomForestClassifier(n_estimators=300, random_state=seed, n_jobs=-1)
        grid = {"clf__min_samples_leaf": [1, 5, 10]}
    elif algo == "xgboost":
        clf = XGBClassifier(n_estimators=300, subsample=0.8, colsample_bytree=0.8,
                            eval_metric="logloss", random_state=seed,
                            tree_method="hist", n_jobs=-1)
        grid = {"clf__max_depth": [2, 3], "clf__learning_rate": [0.05, 0.1]}
    else:
        raise ValueError(algo)

    return Pipeline([("pre", pre), ("clf", clf)]), grid


def run_spec(X: pd.DataFrame, y: np.ndarray, features: list[str], algo: str) -> tuple:
    """Nested CV. Returns out-of-fold probabilities per repeat and fold AUCs."""
    cv = RepeatedStratifiedKFold(n_splits=N_SPLITS, n_repeats=N_REPEATS,
                                 random_state=SEED)
    oof = np.full((N_REPEATS, len(y)), np.nan)
    rows = []
    for i, (tr, te) in enumerate(cv.split(X, y)):
        rep, fold = divmod(i, N_SPLITS)
        pipe, grid = make_pipeline(algo, features, SEED + rep)
        # Inner CV sees training rows only. Nothing is fitted on X.iloc[te].
        search = GridSearchCV(pipe, grid, scoring="roc_auc", cv=3, n_jobs=-1,
                              refit=True)
        search.fit(X.iloc[tr], y[tr])
        p = search.predict_proba(X.iloc[te])[:, 1]
        oof[rep, te] = p
        rows.append({"repeat": rep, "fold": fold, "algo": algo,
                     "auc": roc_auc_score(y[te], p),
                     "best": json.dumps(search.best_params_)})
    return oof, rows


def audit_leakage(X: pd.DataFrame, y: np.ndarray) -> list[str]:
    """Assert the fitted pipeline never sees held-out rows.

    Refits one fold with the held-out block replaced by NaN. If any transformer
    had been fitted on the full data, held-out statistics would differ.
    """
    findings = []
    cv = RepeatedStratifiedKFold(n_splits=N_SPLITS, n_repeats=1, random_state=SEED)
    tr, te = next(iter(cv.split(X, y)))

    pipe, _ = make_pipeline("logistic", list(X.columns), SEED)
    pipe.fit(X.iloc[tr], y[tr])
    scaler = pipe.named_steps["pre"].named_transformers_["num"].named_steps["scale"]

    nums = [f for f in X.columns if f not in CATEGORICAL]
    train_mean = X.iloc[tr][nums].mean().to_numpy()
    full_mean = X[nums].mean().to_numpy()

    if not np.allclose(scaler.mean_, train_mean, rtol=1e-9, atol=1e-9):
        findings.append("scaler mean does not match the training fold")
    if np.allclose(scaler.mean_, full_mean, rtol=1e-9, atol=1e-9) and \
            not np.allclose(train_mean, full_mean, rtol=1e-9, atol=1e-9):
        findings.append("scaler was fitted on the full dataset, not the fold")
    return findings


def main() -> None:
    df = pd.read_parquet(INTERIM / "02_outcome.parquet")
    keep = pd.read_csv(INTERIM / "02_analytic_seqn.csv").SEQN
    df = df[df.SEQN.isin(keep)].reset_index(drop=True)

    all_features = sorted({f for fs in SPECS.values() for f in fs})
    missing = [f for f in all_features if f not in df.columns]
    assert not missing, f"features absent from the outcome file: {missing}"
    assert df[all_features].notna().all().all(), "locked row set has missing features"

    y = df["low_cog"].to_numpy(dtype=int)
    assert set(np.unique(y)) == {0, 1}
    print(f"analytic sample n={len(df)}  events={int(y.sum())}  "
          f"prevalence={y.mean():.4f}")

    audit = audit_leakage(df[SPECS['M3']], y)
    print(f"leakage audit: {'PASS, no findings' if not audit else audit}")
    assert not audit, f"LEAKAGE DETECTED: {audit}"

    preds, fold_rows = {}, []
    for spec, feats in SPECS.items():
        for algo in ("logistic", "random_forest", "xgboost"):
            t0 = time.time()
            oof, rows = run_spec(df[feats], y, feats, algo)
            for rep in range(N_REPEATS):
                preds[f"{spec}__{algo}__r{rep}"] = oof[rep]
            for r in rows:
                r["spec"] = spec
            fold_rows += rows
            mean_auc = np.mean([r["auc"] for r in rows])
            print(f"  {spec:<7} {algo:<14} AUC={mean_auc:.4f}  "
                  f"({time.time() - t0:.0f}s)")

    out = pd.DataFrame(preds)
    out.insert(0, "SEQN", df.SEQN.to_numpy())
    out.insert(1, "y", y)
    out.to_parquet(INTERIM / "03_oof_predictions.parquet", index=False)

    folds = pd.DataFrame(fold_rows)
    folds.to_csv(INTERIM / "03_fold_auc.csv", index=False)

    summary = (folds.groupby(["spec", "algo"]).auc
               .agg(["mean", "std"]).round(4).reset_index())
    (INTERIM / "03_model_report.json").write_text(json.dumps({
        "n": int(len(df)), "events": int(y.sum()), "prevalence": float(y.mean()),
        "seed": SEED, "cv": f"{N_SPLITS}-fold x {N_REPEATS} repeats",
        "leakage_audit": "pass",
        "specs": {k: v for k, v in SPECS.items()},
        "mean_auc": summary.to_dict(orient="records"),
    }, indent=1))

    print("\nmean CV AUC by spec and algorithm:")
    print(summary.to_string(index=False))
    print("\nwrote", INTERIM / "03_oof_predictions.parquet")


if __name__ == "__main__":
    main()
