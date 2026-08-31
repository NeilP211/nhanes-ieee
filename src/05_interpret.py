"""
Phase 5: interpretation and the mixture-method benchmark.

Three parts.

1. Quantile g-computation, reimplemented in Python. No maintained Python
   implementation of WQS, qgcomp or BKMR exists (audited in Phase 0), and the
   R packages cannot be refitted inside 50 CV folds cheaply. The non-bootstrap
   qgcomp estimator is, for prediction purposes, a logistic regression on
   exposures quantised against training-fold cutpoints, so it is expressible as
   a scikit-learn transformer and inherits fold-safe preprocessing.

2. SHAP on the best M3 model, with rankings bootstrapped to show rank
   stability. Correlated biomarkers make a single-run ranking unreliable.

3. Partial dependence for selenium and manganese, the U-shape test for H2.

Outputs
    output/tables/05_qgcomp.csv          psi, weights, and CV discrimination
    output/tables/05_shap_ranking.csv    bootstrapped SHAP rank stability
    output/tables/05_partial_dependence.csv
    data/interim/05_interpretation.json

Run:  python3 src/05_interpret.py
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import RepeatedStratifiedKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from xgboost import XGBClassifier

ROOT = Path(__file__).resolve().parent.parent
INTERIM = ROOT / "data" / "interim"
TABLES = ROOT / "output" / "tables"

SEED = 20260831
N_SPLITS, N_REPEATS = 10, 5
N_BOOT_SHAP = 200
N_QUANTILES = 4

DEMO = ["RIDAGEYR", "RIAGENDR", "RIDRETH3", "DMDEDUC2", "INDFMPIR"]
METALS = ["log_LBXBPB", "log_LBXBCD", "log_LBXTHG", "log_LBXBSE", "log_LBXBMN"]
NUTR = ["log_LBDB12SI", "log_LBXMMASI", "LBDFOT", "LBDRFO", "LBXVIDMS", "LBXGH",
        "LBDHDD", "LBXTC", "LBXSTR", "LBXSAL", "LBXSIR", "egfr", "nlr", "plr",
        "log_sii"]
CATEGORICAL = {"RIDRETH3", "DMDEDUC2"}


class Quantizer(BaseEstimator, TransformerMixin):
    """Quantise exposures into q bins using cutpoints learned on training data.

    This is the step that makes quantile g-computation fold-safe. The R package
    behaves the same way: its predict method re-quantises new data using the
    cutpoints stored from the original fit, rather than recomputing them.
    """

    def __init__(self, q: int = N_QUANTILES):
        self.q = q

    def fit(self, X, y=None):
        X = np.asarray(X, dtype=float)
        # Interior cutpoints only, so q bins need q-1 boundaries.
        probs = np.linspace(0, 1, self.q + 1)[1:-1]
        self.cutpoints_ = [np.quantile(X[:, j], probs) for j in range(X.shape[1])]
        self.n_features_in_ = X.shape[1]
        return self

    def transform(self, X):
        X = np.asarray(X, dtype=float)
        out = np.empty_like(X)
        for j in range(X.shape[1]):
            out[:, j] = np.searchsorted(self.cutpoints_[j], X[:, j], side="right")
        return out


def qgcomp_pipeline(exposures: list[str], covariates: list[str]) -> Pipeline:
    """Quantised exposures plus untransformed covariates, into a logistic model."""
    cats = [c for c in covariates if c in CATEGORICAL]
    nums = [c for c in covariates if c not in CATEGORICAL]
    pre = ColumnTransformer([
        ("exposure", Pipeline([("impute", SimpleImputer(strategy="median")),
                               ("quant", Quantizer(N_QUANTILES))]), exposures),
        ("num", Pipeline([("impute", SimpleImputer(strategy="median")),
                          ("scale", StandardScaler())]), nums),
        ("cat", Pipeline([("impute", SimpleImputer(strategy="most_frequent")),
                          ("onehot", OneHotEncoder(handle_unknown="ignore",
                                                   sparse_output=False))]), cats),
    ], remainder="drop")
    return Pipeline([("pre", pre),
                     ("clf", LogisticRegression(l1_ratio=0, solver="lbfgs",
                                                max_iter=5000, C=1.0,
                                                random_state=SEED))])


def qgcomp_effects(pipe: Pipeline, exposures: list[str]) -> dict:
    """psi (the mixture effect) and the signed component weights."""
    beta = pipe.named_steps["clf"].coef_[0][:len(exposures)]
    psi = float(beta.sum())
    pos, neg = beta[beta > 0].sum(), -beta[beta < 0].sum()
    weights = {}
    for name, b in zip(exposures, beta):
        denom = pos if b > 0 else neg
        weights[name] = float(b / denom) if denom > 0 else 0.0
    return {"psi": psi, "weights": weights,
            "coefficients": dict(zip(exposures, beta.astype(float)))}


def cv_auc(pipe_factory, X: pd.DataFrame, y: np.ndarray) -> tuple[np.ndarray, float]:
    """Out-of-fold probabilities averaged over repeats, and the resulting AUC."""
    cv = RepeatedStratifiedKFold(n_splits=N_SPLITS, n_repeats=N_REPEATS,
                                 random_state=SEED)
    oof = np.full((N_REPEATS, len(y)), np.nan)
    for i, (tr, te) in enumerate(cv.split(X, y)):
        rep = i // N_SPLITS
        pipe = pipe_factory()
        pipe.fit(X.iloc[tr], y[tr])
        oof[rep, te] = pipe.predict_proba(X.iloc[te])[:, 1]
    mean_p = oof.mean(axis=0)
    return mean_p, float(roc_auc_score(y, mean_p))


def shap_rank_stability(X: pd.DataFrame, y: np.ndarray, features: list[str]) -> pd.DataFrame:
    """Refit XGBoost on bootstrap resamples and record SHAP rank per feature."""
    import shap

    rng = np.random.default_rng(SEED)
    n = len(y)
    ranks = {f: [] for f in features}
    for _ in range(N_BOOT_SHAP):
        idx = rng.integers(0, n, n)
        if y[idx].min() == y[idx].max():
            continue
        model = XGBClassifier(n_estimators=300, max_depth=3, learning_rate=0.05,
                              subsample=0.8, colsample_bytree=0.8,
                              eval_metric="logloss", random_state=SEED,
                              tree_method="hist", n_jobs=-1)
        model.fit(X.iloc[idx][features], y[idx])
        vals = np.abs(shap.TreeExplainer(model).shap_values(X[features])).mean(axis=0)
        order = pd.Series(vals, index=features).rank(ascending=False)
        for f in features:
            ranks[f].append(order[f])
    rows = []
    for f in features:
        r = np.array(ranks[f])
        rows.append({"feature": f, "median_rank": float(np.median(r)),
                     "rank_p2.5": float(np.percentile(r, 2.5)),
                     "rank_p97.5": float(np.percentile(r, 97.5)),
                     "pct_in_top5": float(np.mean(r <= 5) * 100)})
    return pd.DataFrame(rows).sort_values("median_rank").reset_index(drop=True)


def partial_dependence_curve(model, X: pd.DataFrame, feature: str,
                             grid: np.ndarray) -> np.ndarray:
    """Marginal predicted probability across a grid, averaging over all rows."""
    out = []
    for v in grid:
        Xg = X.copy()
        Xg[feature] = v
        out.append(float(model.predict_proba(Xg)[:, 1].mean()))
    return np.array(out)


def main() -> None:
    TABLES.mkdir(parents=True, exist_ok=True)
    df = pd.read_parquet(INTERIM / "02_outcome.parquet")
    keep = pd.read_csv(INTERIM / "02_analytic_seqn.csv").SEQN
    df = df[df.SEQN.isin(keep)].reset_index(drop=True)
    y = df["low_cog"].to_numpy(dtype=int)
    m3_features = DEMO + METALS + NUTR

    # 1. Quantile g-computation, metals mixture adjusted for demographics.
    X = df[METALS + DEMO]
    _, qg_auc = cv_auc(lambda: qgcomp_pipeline(METALS, DEMO), X, y)
    fitted = qgcomp_pipeline(METALS, DEMO).fit(X, y)
    eff = qgcomp_effects(fitted, METALS)
    qg_rows = [{"exposure": k, "coefficient": round(eff["coefficients"][k], 4),
                "weight": round(v, 4)} for k, v in eff["weights"].items()]
    pd.DataFrame(qg_rows).to_csv(TABLES / "05_qgcomp.csv", index=False)
    print(f"quantile g-computation, metals mixture ({N_QUANTILES} quantiles)")
    print(f"   psi (joint mixture log-odds per quantile increase) = {eff['psi']:.4f}")
    print(f"   cross-validated AUC                                = {qg_auc:.4f}")
    print(pd.DataFrame(qg_rows).to_string(index=False))

    # 2. SHAP rank stability on M3.
    print(f"\nbootstrapping SHAP rankings, {N_BOOT_SHAP} resamples ...")
    shap_df = shap_rank_stability(df, y, m3_features)
    shap_df.round(3).to_csv(TABLES / "05_shap_ranking.csv", index=False)
    print(shap_df.head(12).round(2).to_string(index=False))

    # 3. Partial dependence for selenium and manganese, the U-shape test.
    base = XGBClassifier(n_estimators=300, max_depth=3, learning_rate=0.05,
                         subsample=0.8, colsample_bytree=0.8,
                         eval_metric="logloss", random_state=SEED,
                         tree_method="hist", n_jobs=-1).fit(df[m3_features], y)
    pdp_rows = []
    for feat, label in [("log_LBXBSE", "selenium"), ("log_LBXBMN", "manganese")]:
        lo, hi = df[feat].quantile([0.02, 0.98])
        grid = np.linspace(lo, hi, 40)
        curve = partial_dependence_curve(base, df[m3_features], feat, grid)
        for g, c in zip(grid, curve):
            pdp_rows.append({"feature": label, "log_value": float(g),
                             "value": float(np.exp(g)), "predicted_prob": float(c)})
    pdp_df = pd.DataFrame(pdp_rows)
    pdp_df.round(5).to_csv(TABLES / "05_partial_dependence.csv", index=False)

    shape = {}
    for label in ("selenium", "manganese"):
        c = pdp_df[pdp_df.feature == label].predicted_prob.to_numpy()
        # A U or inverted-U puts the extremum away from both ends.
        shape[label] = {
            "argmin_position": float(np.argmin(c) / (len(c) - 1)),
            "argmax_position": float(np.argmax(c) / (len(c) - 1)),
            "range": float(c.max() - c.min()),
        }

    (INTERIM / "05_interpretation.json").write_text(json.dumps({
        "qgcomp": {"psi": eff["psi"], "cv_auc": qg_auc,
                   "quantiles": N_QUANTILES, "weights": eff["weights"],
                   "coefficients": eff["coefficients"]},
        "shap_top10": shap_df.head(10).to_dict(orient="records"),
        "pdp_shape": shape,
        "n_bootstrap_shap": N_BOOT_SHAP,
    }, indent=1))

    print("\npartial dependence shape (position 0 = low end, 1 = high end):")
    for k, v in shape.items():
        print(f"   {k:<10} min at {v['argmin_position']:.2f}, "
              f"max at {v['argmax_position']:.2f}, range {v['range']:.4f}")
    print("\nwrote", TABLES / "05_qgcomp.csv")


if __name__ == "__main__":
    main()
