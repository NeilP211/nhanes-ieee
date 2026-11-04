"""
Phase 13 (revision): every reviewer-requested estimate. Post hoc throughout.

Pre-registration Amendment 1, items A1 to A5 and A7.

  A1  Margin analysis. 90% and 95% paired-bootstrap CIs for delta-AUC(M3 - M0)
      in the primary and every pre-specified sensitivity analysis, with
      non-superiority and two-sided equivalence (TOST) decisions at margins of
      0.01, 0.015 and 0.02, and the smallest margin each analysis excludes.
  A2  M4 (M0+ plus both biomarker blocks): performance, delta-AUC(M4 - M0+),
      decision curve against M0+.
  A3  All pairwise contrasts among M0, M1, M2, M3, M0+ and M4 under each
      algorithm, and each nonlinear learner against logistic regression.
  A4  Complete cognitive battery (all four scores).
  A5  Demographically adjusted outcome (regression-based internal norms).
  A7  Paired bootstrap CI for the continuous-outcome delta R-squared.

Bootstrap draws. Contrasts already reported in the submission are recomputed by
replaying the original random-number sequence of 04_evaluate.py and
06_sensitivity.py, and the script asserts that the replay reproduces every
published interval. Their 90% intervals therefore come from exactly the same
2,000 resamples as their published 95% intervals. Each new contrast gets its own
fixed-seed stream of 2,000 resamples.

Outputs
    output/tables/13_pairwise_delta_auc.csv
    output/tables/13_margin_analysis.csv
    output/tables/13_m4_performance.csv
    output/tables/13_revision_summary.md
    data/interim/13_revision_evaluation.json

Run:  python3 src/13_revision_evaluate.py
"""
from __future__ import annotations

import importlib.util
import json
import time
from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score, brier_score_loss, roc_auc_score

ROOT = Path(__file__).resolve().parent.parent
INTERIM = ROOT / "data" / "interim"
TABLES = ROOT / "output" / "tables"


def load(name: str, file: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / "src" / file)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


P3 = load("phase3", "03_model.py")
P4 = load("phase4", "04_evaluate.py")
P6 = load("phase6", "06_sensitivity.py")

SEED, N_BOOT, N_REPEATS = P4.SEED, P4.N_BOOT, P4.N_REPEATS
ALGOS = P4.ALGOS
SPECS = ["M0", "M1", "M2", "M3", "M0plus", "M4"]
MARGINS = [0.01, 0.015, 0.02]
M4 = P3.DEMO + P3.COVARIATES + P3.METALS + P3.NUTR
DEMO, METALS, NUTR = P6.DEMO, P6.METALS, P6.NUTR


# ---------------------------------------------------------------- bootstrap
def boot(y: np.ndarray, pa: np.ndarray, pb: np.ndarray,
         rng: np.random.Generator) -> np.ndarray:
    """Paired bootstrap of AUC(a) - AUC(b). Consumes rng exactly as phases 4
    and 6 do, so replaying their sequence reproduces their draws."""
    n = len(y)
    d = np.empty(N_BOOT)
    k = 0
    while k < N_BOOT:
        idx = rng.integers(0, n, n)
        ys = y[idx]
        if ys.min() == ys.max():
            continue
        d[k] = roc_auc_score(ys, pa[idx]) - roc_auc_score(ys, pb[idx])
        k += 1
    return d


def summarise(y, pa, pb, draws: np.ndarray) -> dict:
    lo95, hi95 = np.percentile(draws, [2.5, 97.5])
    lo90, hi90 = np.percentile(draws, [5, 95])
    out = {"delta_auc": float(roc_auc_score(y, pa) - roc_auc_score(y, pb)),
           "ci95_low": float(lo95), "ci95_high": float(hi95),
           "ci90_low": float(lo90), "ci90_high": float(hi90),
           "ci95_excludes_zero": bool(lo95 > 0 or hi95 < 0),
           # One-sided: the largest improvement not excluded at alpha 0.05.
           "smallest_margin_excluded_one_sided": float(hi90),
           # Two-sided TOST: the narrowest symmetric margin the 90% CI fits in.
           "smallest_equivalence_margin": float(max(abs(lo90), abs(hi90)))}
    for m in MARGINS:
        out[f"non_superiority_{m}"] = bool(hi90 < m)
        out[f"equivalence_{m}"] = bool(lo90 > -m and hi90 < m)
    # Symmetric reading of the 0.02 margin, in either direction.
    out["ci95_beyond_0.02"] = bool(lo95 > 0.02 or hi95 < -0.02)
    return out


def new_stream(*key: int) -> np.random.Generator:
    return np.random.default_rng([SEED, 13, *key])


# ---------------------------------------------------------------- helpers
def mean_oof(df: pd.DataFrame, spec: str, algo: str) -> np.ndarray:
    cols = [f"{spec}__{algo}__r{r}" for r in range(N_REPEATS)]
    return df[cols].to_numpy().mean(axis=1)


def logistic_oof(X: pd.DataFrame, y: np.ndarray, feats: list[str]) -> np.ndarray:
    """Primary pipeline (tuned L2 logistic, nested CV), mean over repeats."""
    oof, _ = P3.run_spec(X[feats], y, feats, "logistic")
    return oof.mean(axis=0)


def check_close(label: str, got: float, published: float) -> None:
    assert abs(round(got, 4) - published) < 1.5e-4, f"{label}: {got:.5f} vs {published}"


# ---------------------------------------------------------------- A3 + replay of phase 4
def replay_phase4(y, P) -> dict:
    """Replays 04_evaluate.py's rng sequence. Returns draws keyed (algo, a, b)."""
    published = pd.read_csv(TABLES / "04_delta_auc.csv")
    rng = np.random.default_rng(SEED)
    draws = {}
    for algo in ALGOS:
        for a, b in P4.CONTRASTS:
            d = boot(y, P[(a, algo)], P[(b, algo)], rng)
            draws[(algo, a, b)] = d
            row = published[(published.algo == algo) &
                            (published.contrast == f"{a} - {b}")].iloc[0]
            lo, hi = np.percentile(d, [2.5, 97.5])
            check_close(f"{algo} {a}-{b} lo", lo, row.ci_low)
            check_close(f"{algo} {a}-{b} hi", hi, row.ci_high)
    for algo in ["random_forest", "xgboost"]:
        draws[("algo", "M3", algo)] = boot(y, P[("M3", algo)], P[("M3", "logistic")], rng)
    return draws


def pairwise(y, P, replay: dict) -> pd.DataFrame:
    rows = []
    for ai, algo in enumerate(ALGOS):
        for pi, (b, a) in enumerate(combinations(SPECS, 2)):
            if (algo, a, b) in replay:
                d, source = replay[(algo, a, b)], "replayed from submission"
            elif (algo, b, a) in replay:
                d, source = -replay[(algo, b, a)], "replayed from submission (sign reversed)"
            else:
                d, source = boot(y, P[(a, algo)], P[(b, algo)], new_stream(1, ai, pi)), "new"
            nested = set(SPEC_FEATURES[b]) < set(SPEC_FEATURES[a])
            rows.append({"algo": algo, "contrast": f"{a} - {b}", "nested": nested,
                         "draws": source, **summarise(y, P[(a, algo)], P[(b, algo)], d)})
    for si, spec in enumerate(SPECS):
        for algo in ["random_forest", "xgboost"]:
            key = ("algo", spec, algo)
            if key in replay:
                d, source = replay[key], "replayed from submission"
            else:
                d, source = boot(y, P[(spec, algo)], P[(spec, "logistic")],
                                 new_stream(2, si, ALGOS.index(algo))), "new"
            rows.append({"algo": f"{algo} vs logistic", "contrast": f"{spec}: {algo} - logistic",
                         "nested": False, "draws": source,
                         **summarise(y, P[(spec, algo)], P[(spec, "logistic")], d)})
    return pd.DataFrame(rows)


SPEC_FEATURES = {"M0": P3.DEMO, "M1": P3.DEMO + P3.METALS, "M2": P3.DEMO + P3.NUTR,
                 "M3": P3.DEMO + P3.METALS + P3.NUTR, "M0plus": P3.DEMO + P3.COVARIATES,
                 "M4": M4}


# ---------------------------------------------------------------- A1 + replay of phase 6
def replay_phase6(full: pd.DataFrame, locked: pd.DataFrame) -> tuple[list[dict], dict]:
    """Replays 06_sensitivity.py exactly, keeping the draws. Returns rows and
    the predictions needed for the continuous-outcome interval."""
    published = pd.read_csv(TABLES / "06_sensitivity.csv").set_index("analysis")
    rng = np.random.default_rng(SEED)
    rows = []

    def one(d: pd.DataFrame, label: str, name: str, impute: str, pub: str) -> None:
        d = d[d[label].notna()]
        y = d[label].to_numpy(dtype=int)
        t0 = time.time()
        p3 = P6.oof_probs(d[DEMO + METALS + NUTR], y, DEMO + METALS + NUTR, impute)
        p0 = P6.oof_probs(d[DEMO], y, DEMO, impute)
        dr = boot(y, p3, p0, rng)
        s = summarise(y, p3, p0, dr)
        check_close(f"{name} lo", s["ci95_low"], published.loc[pub, "ci_low"])
        check_close(f"{name} hi", s["ci95_high"], published.loc[pub, "ci_high"])
        rows.append({"analysis": name, "contrast": "M3 - M0", "status": "pre-specified",
                     "pipeline": "logistic, C = 1 (phase 6)", "n": len(d),
                     "events": int(y.sum()), **s})
        print(f"  {name:<44} {s['delta_auc']:+.4f} 90% [{s['ci90_low']:+.4f}, "
              f"{s['ci90_high']:+.4f}]  ({time.time() - t0:.0f}s)")

    one(locked, "low_cog", "Primary specification, phase 6 pipeline", "median",
        "primary (reference)")
    one(locked, "low_cog_p20", "20th percentile cutoff", "median", "cutoff at 20th percentile")
    one(locked, "low_cog_p10", "10th percentile cutoff", "median", "cutoff at 10th percentile")
    d = locked.copy()
    unable = d.CFDDRNC.notna()
    d["low_cog_dsst"] = d.low_cog.where(~unable, 1.0)
    one(d, "low_cog_dsst", "DSST not completed coded low", "median",
        f"DSST unable coded low (n={int(unable.sum())})")
    one(locked[locked.CFALANG == 1], "low_cog", "English-language administration only",
        "median", "English-only administration")
    labelled = full[full.low_cog.notna()].reset_index(drop=True)
    one(labelled, "low_cog", "Multiple imputation, full labelled sample", "mice",
        "MICE on full labelled sample")

    # Leave-one-block-out, same order and rng as phase 6.
    y = locked.low_cog.to_numpy(dtype=int)
    p_full = P6.oof_probs(locked[DEMO + METALS + NUTR], y, DEMO + METALS + NUTR, "median")
    for drop_name, drop, pub in [("without metals", METALS, "leave-one-block-out, without metals"),
                                 ("without nutritional", NUTR,
                                  "leave-one-block-out, without nutritional")]:
        feats = [f for f in DEMO + METALS + NUTR if f not in drop]
        p = P6.oof_probs(locked[feats], y, feats, "median")
        dr = boot(y, p_full, p, rng)
        s = summarise(y, p_full, p, dr)
        check_close(f"LOBO {drop_name}", s["ci95_low"], published.loc[pub, "ci_low"])
        rows.append({"analysis": f"Leave-one-block-out, M3 versus M3 {drop_name}",
                     "contrast": "M3 - reduced", "status": "pre-specified",
                     "pipeline": "logistic, C = 1 (phase 6)", "n": len(locked),
                     "events": int(y.sum()), **s})
    return rows


def continuous_interval(locked: pd.DataFrame) -> dict:
    """A7: paired bootstrap CI for delta R-squared, phase 6 predictions."""
    from sklearn.model_selection import RepeatedKFold
    cv = RepeatedKFold(n_splits=P6.N_SPLITS, n_repeats=P6.N_REPEATS, random_state=SEED)
    y = locked["composite_z"].to_numpy()
    preds = {}
    for name, feats in [("M0", DEMO), ("M3", DEMO + METALS + NUTR)]:
        oof = np.full((P6.N_REPEATS, len(y)), np.nan)
        for i, (tr, te) in enumerate(cv.split(locked)):
            pipe = P6.pipeline(feats, "median", task="reg")
            pipe.fit(locked.iloc[tr][feats], y[tr])
            oof[i // P6.N_SPLITS, te] = pipe.predict(locked.iloc[te][feats])
        preds[name] = oof.mean(axis=0)

    def r2(yy, pp):
        return 1 - np.sum((yy - pp) ** 2) / np.sum((yy - yy.mean()) ** 2)

    point = {k: float(r2(y, v)) for k, v in preds.items()}
    published = json.loads((INTERIM / "06_sensitivity.json").read_text())["continuous_outcome_r2"]
    assert abs(point["M0"] - published["M0"]) < 1e-9 and abs(point["M3"] - published["M3"]) < 1e-9
    rng = new_stream(7)
    n = len(y)
    d = np.empty(N_BOOT)
    for k in range(N_BOOT):
        idx = rng.integers(0, n, n)
        d[k] = r2(y[idx], preds["M3"][idx]) - r2(y[idx], preds["M0"][idx])
    lo, hi = np.percentile(d, [2.5, 97.5])
    return {"r2_M0": point["M0"], "r2_M3": point["M3"],
            "delta_r2": point["M3"] - point["M0"], "ci95_low": float(lo), "ci95_high": float(hi)}


# ---------------------------------------------------------------- A4, A5
def demographic_norm_label(full: pd.DataFrame) -> tuple[pd.Series, dict]:
    """A5: lowest quartile of the residual from a regression-based norm model
    fitted on all labelled participants with complete demographics."""
    lab = full[full.composite_z.notna() & full.DMDEDUC2.notna()].copy()
    age = lab.RIDAGEYR.to_numpy(float)
    X = pd.concat([
        pd.Series(1.0, index=lab.index, name="intercept"),
        pd.Series(age - 70, index=lab.index, name="age_c"),
        pd.Series((age - 70) ** 2, index=lab.index, name="age_c2"),
        (lab.RIAGENDR == 2).astype(float).rename("female"),
        pd.get_dummies(lab.DMDEDUC2.astype(int), prefix="educ", drop_first=True, dtype=float),
        pd.get_dummies(lab.RIDRETH3.astype(int), prefix="race", drop_first=True, dtype=float),
    ], axis=1)
    yv = lab.composite_z.to_numpy()
    beta, *_ = np.linalg.lstsq(X.to_numpy(), yv, rcond=None)
    resid = yv - X.to_numpy() @ beta
    r2 = 1 - np.sum(resid ** 2) / np.sum((yv - yv.mean()) ** 2)
    cut = float(np.quantile(resid, 0.25))
    label = pd.Series(np.nan, index=full.index)
    label.loc[lab.index] = (resid <= cut).astype(float)
    return label, {"n_norm_sample": int(len(lab)), "norm_model_r2": float(r2),
                   "residual_quartile_cut": cut,
                   "terms": list(X.columns), "coefficients": dict(zip(X.columns, beta.round(4)))}


def model_set(d: pd.DataFrame, label: str, name: str, key: int) -> list[dict]:
    """Logistic M0, M3, M0+, M4 on one sample; M3 - M0 and M4 - M0+."""
    d = d[d[label].notna()].reset_index(drop=True)
    y = d[label].to_numpy(dtype=int)
    t0 = time.time()
    p = {s: logistic_oof(d, y, SPEC_FEATURES[s]) for s in ["M0", "M3", "M0plus", "M4"]}
    rows = []
    for ci, (a, b) in enumerate([("M3", "M0"), ("M4", "M0plus")]):
        s = summarise(y, p[a], p[b], boot(y, p[a], p[b], new_stream(3, key, ci)))
        rows.append({"analysis": name, "contrast": f"{a} - {b}", "status": "post hoc",
                     "pipeline": "logistic, tuned (primary pipeline)", "n": len(d),
                     "events": int(y.sum()), "auc_a": float(roc_auc_score(y, p[a])),
                     "auc_b": float(roc_auc_score(y, p[b])), **s})
    print(f"  {name:<44} n={len(d)} events={int(y.sum())}  "
          f"M3-M0 {rows[0]['delta_auc']:+.4f}  M4-M0+ {rows[1]['delta_auc']:+.4f}  "
          f"({time.time() - t0:.0f}s)")
    return rows


# ---------------------------------------------------------------- A2 performance + DCA
def m4_performance(y, P, folds: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for spec in SPECS:
        for algo in ALGOS:
            p = P[(spec, algo)]
            slope, intercept = P4.calibration(y, p)
            rows.append({"spec": spec, "algo": algo, "auc": roc_auc_score(y, p),
                         "auprc": average_precision_score(y, p),
                         "brier": brier_score_loss(y, p),
                         "calib_slope": slope, "calib_intercept": intercept})
    return pd.DataFrame(rows).round(4)


def decision_curve(y, P) -> dict:
    thresholds = np.arange(0.05, 0.61, 0.01)
    nb = {s: np.array([P4.net_benefit(y, P[(s, "logistic")], float(t)) for t in thresholds])
          for s in ["M0", "M3", "M0plus", "M4"]}
    out = {}
    for a, b in [("M3", "M0"), ("M0plus", "M0"), ("M4", "M0plus"), ("M4", "M0")]:
        gain = nb[a] - nb[b]
        out[f"{a} vs {b}"] = {"thresholds": len(thresholds),
                              "n_thresholds_a_exceeds_b": int((gain > 0).sum()),
                              "max_gain": float(gain.max()), "min_gain": float(gain.min())}
    published = pd.read_csv(TABLES / "04_decision_curve.csv")
    assert np.allclose(published.M3.to_numpy(), nb["M3"], atol=6e-6)
    return out


def df_md(df: pd.DataFrame) -> str:
    """Plain markdown table, so no extra dependency is needed."""
    cols = [str(c) for c in df.columns]
    lines = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    for row in df.itertuples(index=False):
        lines.append("| " + " | ".join(str(v) for v in row) + " |")
    return "\n".join(lines)


def main() -> None:
    t_start = time.time()
    full = pd.read_parquet(INTERIM / "02_outcome.parquet")
    keep = set(pd.read_csv(INTERIM / "02_analytic_seqn.csv").SEQN)
    locked = full[full.SEQN.isin(keep)].reset_index(drop=True)
    stored = pd.read_parquet(INTERIM / "03_oof_predictions.parquet")
    m4 = pd.read_parquet(INTERIM / "11_oof_predictions_m4.parquet")
    assert (stored.SEQN.to_numpy() == m4.SEQN.to_numpy()).all()
    assert (stored.SEQN.to_numpy() == locked.SEQN.to_numpy()).all()
    y = stored.y.to_numpy(dtype=int)
    preds = stored.merge(m4.drop(columns="y"), on="SEQN")
    P = {(s, a): mean_oof(preds, s, a) for s in SPECS for a in ALGOS}

    print("A3: replaying phase 4 draws and computing all pairwise contrasts")
    replay = replay_phase4(y, P)
    pw = pairwise(y, P, replay)
    pw.round(4).to_csv(TABLES / "13_pairwise_delta_auc.csv", index=False)

    print("A2: M4 performance and decision curve")
    perf = m4_performance(y, P, pd.read_csv(INTERIM / "03_fold_auc.csv"))
    perf.to_csv(TABLES / "13_m4_performance.csv", index=False)
    dca = decision_curve(y, P)

    print("A1: replaying phase 6 sensitivity analyses with draws kept")
    margin_rows = []
    prim = pw[(pw.algo == "logistic") & (pw.contrast == "M3 - M0")].iloc[0].to_dict()
    margin_rows.append({"analysis": "Primary analysis", "contrast": "M3 - M0",
                        "status": "pre-specified", "pipeline": "logistic, tuned (primary pipeline)",
                        "n": len(y), "events": int(y.sum()),
                        **{k: prim[k] for k in prim if k not in ("algo", "contrast", "nested", "draws")}})
    m4row = pw[(pw.algo == "logistic") & (pw.contrast == "M4 - M0plus")].iloc[0].to_dict()
    margin_rows.append({"analysis": "Biomarkers added to the clinical baseline", "contrast": "M4 - M0plus",
                        "status": "post hoc", "pipeline": "logistic, tuned (primary pipeline)",
                        "n": len(y), "events": int(y.sum()),
                        **{k: m4row[k] for k in m4row if k not in ("algo", "contrast", "nested", "draws")}})
    margin_rows += replay_phase6(full, locked)

    print("A4, A5: complete battery and demographically adjusted outcome")
    complete = locked[locked.n_cog_scores == 4]
    margin_rows += model_set(complete, "low_cog", "Complete cognitive battery (4 of 4 scores)", 1)
    norm_label, norm_info = demographic_norm_label(full)
    full["low_cog_demadj"] = norm_label
    locked_adj = full[full.SEQN.isin(keep)].reset_index(drop=True)
    margin_rows += model_set(locked_adj, "low_cog_demadj",
                             "Demographically adjusted outcome (internal norms)", 2)

    cont = continuous_interval(locked)
    print(f"A7: delta R2 = {cont['delta_r2']:+.4f} [{cont['ci95_low']:+.4f}, {cont['ci95_high']:+.4f}]")

    margins = pd.DataFrame(margin_rows)
    margins.round(4).to_csv(TABLES / "13_margin_analysis.csv", index=False)

    (INTERIM / "13_revision_evaluation.json").write_text(json.dumps({
        "amendment": "PREREGISTRATION.md Amendment 1, A1 to A5 and A7 (post hoc)",
        "n_boot": N_BOOT, "margins": MARGINS,
        "replay_check": "every published interval reproduced from replayed draws",
        "pairwise": pw.round(5).to_dict(orient="records"),
        "margin_analysis": margins.round(5).to_dict(orient="records"),
        "performance": perf.to_dict(orient="records"),
        "decision_curve": dca, "continuous_outcome": cont,
        "demographic_norms": norm_info,
        "demographic_adjusted_prevalence_locked": float(locked_adj.low_cog_demadj.mean()),
        "complete_battery": {"n": int(len(complete)), "events": int(complete.low_cog.sum())},
    }, indent=1, default=float))

    cols = ["analysis", "contrast", "n", "events", "delta_auc", "ci95_low", "ci95_high",
            "ci90_low", "ci90_high", "smallest_margin_excluded_one_sided",
            "smallest_equivalence_margin"] + [f"non_superiority_{m}" for m in MARGINS] + \
           [f"equivalence_{m}" for m in MARGINS]
    md = ["# Revision results (Amendment 1, post hoc)", "",
          "## A1, A4, A5. Margin analysis", "", df_md(margins[cols].round(4)), "",
          "## A3. Pairwise contrasts", "",
          df_md(pw.drop(columns=[c for c in pw.columns
                            if c.startswith(("non_sup", "equiv"))]).round(4)), "",
          "## A2. Performance including M4", "", df_md(perf), "",
          "## A2. Decision curve, logistic", "", json.dumps(dca, indent=1), "",
          "## A5. Norm model", "", json.dumps(norm_info, indent=1, default=float), "",
          "## A7. Continuous outcome", "", json.dumps(cont, indent=1), ""]
    (TABLES / "13_revision_summary.md").write_text("\n".join(md))
    print(f"\ndone in {time.time() - t_start:.0f}s; wrote output/tables/13_*.csv and 13_revision_summary.md")


if __name__ == "__main__":
    main()
