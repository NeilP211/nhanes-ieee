"""
Phase 4: evaluation, delta-AUC with bootstrap CIs, calibration, decision curves.

The primary result is delta-AUC against the demographics-only baseline M0, not
absolute AUC. Bootstrap resamples participants and scores both models on the
same resampled rows, so the comparison stays paired.

Outputs
    output/tables/04_performance.csv     per-model discrimination and calibration
    output/tables/04_delta_auc.csv       the headline numbers
    output/tables/04_decision_curve.csv  net benefit across thresholds
    data/interim/04_evaluation.json

Run:  python3 src/04_evaluate.py
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import brentq
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, brier_score_loss, roc_auc_score

ROOT = Path(__file__).resolve().parent.parent
INTERIM = ROOT / "data" / "interim"
TABLES = ROOT / "output" / "tables"

SEED = 20260831
N_BOOT = 2000
N_REPEATS = 5
ALGOS = ["logistic", "random_forest", "xgboost"]
SPECS = ["M0", "M1", "M2", "M3", "M0plus"]

# Pre-specified in PREREGISTRATION.md section 5.
MEANINGFUL_DELTA = 0.02

# Primary contrast first. M3 vs M0plus is the pre-specified secondary.
CONTRASTS = [("M1", "M0"), ("M2", "M0"), ("M3", "M0"), ("M3", "M0plus")]


def mean_oof(df: pd.DataFrame, spec: str, algo: str) -> np.ndarray:
    """Average the out-of-fold probability across repeats, per participant."""
    cols = [f"{spec}__{algo}__r{r}" for r in range(N_REPEATS)]
    return df[cols].to_numpy().mean(axis=1)


def calibration(y: np.ndarray, p: np.ndarray) -> tuple[float, float]:
    """Calibration slope, and calibration-in-the-large intercept.

    Slope is the coefficient from regressing the outcome on the linear
    predictor. The intercept is the proper offset model: the value of a solving
    y ~ Bernoulli(sigmoid(a + logit(p))), found from its score equation, which
    is monotonic in a. Fitting an intercept-only model and subtracting the mean
    logit is a common shortcut but is not the same quantity.
    """
    eps = 1e-6
    q = np.clip(p, eps, 1 - eps)
    logit = np.log(q / (1 - q))
    slope = float(LogisticRegression(C=1e12, solver="lbfgs", max_iter=1000)
                  .fit(logit.reshape(-1, 1), y).coef_[0][0])

    def score(a: float) -> float:
        return float(np.sum(y - 1.0 / (1.0 + np.exp(-(a + logit)))))

    lo, hi = -20.0, 20.0
    if score(lo) * score(hi) > 0:
        return slope, float("nan")
    intercept = float(brentq(score, lo, hi, xtol=1e-10))
    return slope, intercept


def net_benefit(y: np.ndarray, p: np.ndarray, t: float) -> float:
    """Net benefit at threshold probability t."""
    pred = p >= t
    n = len(y)
    tp = float(np.sum(pred & (y == 1)))
    fp = float(np.sum(pred & (y == 0)))
    return tp / n - (fp / n) * (t / (1 - t))


def bootstrap_delta(y: np.ndarray, pa: np.ndarray, pb: np.ndarray,
                    rng: np.random.Generator) -> dict:
    """Paired bootstrap of AUC(a) - AUC(b) over participants."""
    n = len(y)
    deltas = np.empty(N_BOOT)
    drawn = 0
    while drawn < N_BOOT:
        idx = rng.integers(0, n, n)
        ys = y[idx]
        if ys.min() == ys.max():
            continue
        deltas[drawn] = roc_auc_score(ys, pa[idx]) - roc_auc_score(ys, pb[idx])
        drawn += 1
    lo, hi = np.percentile(deltas, [2.5, 97.5])
    return {"delta_auc": float(roc_auc_score(y, pa) - roc_auc_score(y, pb)),
            "ci_low": float(lo), "ci_high": float(hi),
            "excludes_zero": bool(lo > 0 or hi < 0),
            "exceeds_threshold": bool(lo > MEANINGFUL_DELTA)}


def main() -> None:
    TABLES.mkdir(parents=True, exist_ok=True)
    df = pd.read_parquet(INTERIM / "03_oof_predictions.parquet")
    y = df["y"].to_numpy(dtype=int)
    folds = pd.read_csv(INTERIM / "03_fold_auc.csv")
    rng = np.random.default_rng(SEED)

    perf = []
    for spec in SPECS:
        for algo in ALGOS:
            p = mean_oof(df, spec, algo)
            slope, intercept = calibration(y, p)
            spread = folds[(folds.spec == spec) & (folds.algo == algo)].auc
            perf.append({
                "spec": spec, "algo": algo,
                "auc": roc_auc_score(y, p),
                "auprc": average_precision_score(y, p),
                "brier": brier_score_loss(y, p),
                "calib_slope": slope, "calib_intercept": intercept,
                "fold_auc_mean": spread.mean(), "fold_auc_sd": spread.std(ddof=1),
            })
    perf_df = pd.DataFrame(perf).round(4)
    perf_df.to_csv(TABLES / "04_performance.csv", index=False)

    deltas = []
    for algo in ALGOS:
        for a, b in CONTRASTS:
            r = bootstrap_delta(y, mean_oof(df, a, algo), mean_oof(df, b, algo), rng)
            deltas.append({"algo": algo, "contrast": f"{a} - {b}", **r})
    delta_df = pd.DataFrame(deltas).round(4)
    delta_df.to_csv(TABLES / "04_delta_auc.csv", index=False)

    # Best algorithm against logistic, on M3, to test H2.
    h2 = []
    for algo in ["random_forest", "xgboost"]:
        r = bootstrap_delta(y, mean_oof(df, "M3", algo),
                            mean_oof(df, "M3", "logistic"), rng)
        h2.append({"contrast": f"M3 {algo} - M3 logistic", **r})

    thresholds = np.arange(0.05, 0.61, 0.01)
    dca = []
    for t in thresholds:
        row = {"threshold": round(float(t), 3),
               "treat_all": float(y.mean() - (1 - y.mean()) * (t / (1 - t))),
               "treat_none": 0.0}
        for spec in ["M0", "M3", "M0plus"]:
            row[spec] = net_benefit(y, mean_oof(df, spec, "logistic"), float(t))
        dca.append(row)
    dca_df = pd.DataFrame(dca).round(5)
    dca_df.to_csv(TABLES / "04_decision_curve.csv", index=False)

    primary = next(d for d in deltas
                   if d["algo"] == "logistic" and d["contrast"] == "M3 - M0")
    (INTERIM / "04_evaluation.json").write_text(json.dumps({
        "n": int(len(y)), "events": int(y.sum()), "n_bootstrap": N_BOOT,
        "meaningful_threshold": MEANINGFUL_DELTA,
        "primary_result": primary,
        "performance": perf_df.to_dict(orient="records"),
        "delta_auc": delta_df.to_dict(orient="records"),
        "h2_ml_vs_logistic": h2,
    }, indent=1))

    print(f"n={len(y)}  events={int(y.sum())}  bootstrap={N_BOOT}\n")
    print("Discrimination and calibration (mean out-of-fold across 5 repeats):")
    print(perf_df[["spec", "algo", "auc", "auprc", "brier",
                   "calib_slope", "calib_intercept"]].to_string(index=False))
    print("\nDelta-AUC with bootstrap 95% CI:")
    print(delta_df.to_string(index=False))
    print("\nH2, nonlinear learners against penalized logistic on M3:")
    print(pd.DataFrame(h2).round(4).to_string(index=False))

    print("\n" + "=" * 66)
    print("PRIMARY RESULT: delta-AUC(M3 - M0), L2-penalized logistic")
    print(f"   delta-AUC = {primary['delta_auc']:.4f}  "
          f"95% CI [{primary['ci_low']:.4f}, {primary['ci_high']:.4f}]")
    print(f"   CI excludes zero          : {primary['excludes_zero']}")
    print(f"   CI exceeds 0.02 threshold : {primary['exceeds_threshold']}")
    print("=" * 66)


if __name__ == "__main__":
    main()
