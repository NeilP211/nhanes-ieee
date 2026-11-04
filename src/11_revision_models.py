"""
Phase 11 (revision): fit M4, the clinical baseline plus both biomarker blocks.

Reviewer 1 (comment 3) noted that M3 and M0+ are substitutes, not nested
models, so M3 - M0+ cannot say whether biomarkers add anything beyond clinical
history. M4 = M0+ + metals + nutritional answers that on properly nested models.
Pre-registration Amendment 1, item A2. Post hoc and exploratory.

Reuses make_pipeline, run_spec and audit_leakage from 03_model.py unchanged, so
M4 is fitted with the identical nested CV, grids, seed and locked row set as
M0 to M0+. Before fitting M4 it refits M0 logistic and checks the predictions
match the stored ones exactly, which proves the stored predictions and the new
ones come from the same procedure.

Outputs
    data/interim/11_oof_predictions_m4.parquet
    data/interim/11_revision_models.json

Run:  python3 src/11_revision_models.py
"""
from __future__ import annotations

import importlib.util
import json
import time
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
INTERIM = ROOT / "data" / "interim"


def load_phase3():
    spec = importlib.util.spec_from_file_location("phase3", ROOT / "src" / "03_model.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


P3 = load_phase3()
M4 = P3.DEMO + P3.COVARIATES + P3.METALS + P3.NUTR


def main() -> None:
    df = pd.read_parquet(INTERIM / "02_outcome.parquet")
    keep = pd.read_csv(INTERIM / "02_analytic_seqn.csv").SEQN
    df = df[df.SEQN.isin(keep)].reset_index(drop=True)
    stored = pd.read_parquet(INTERIM / "03_oof_predictions.parquet")

    assert len(df) == 1784 and len(M4) == 33, (len(df), len(M4))
    assert (stored.SEQN.to_numpy() == df.SEQN.to_numpy()).all(), "row order differs"
    assert df[M4].notna().all().all(), "locked row set has missing M4 features"
    y = df["low_cog"].to_numpy(dtype=int)
    assert (stored.y.to_numpy() == y).all()

    audit = P3.audit_leakage(df[M4], y)
    print(f"leakage audit on M4 features: {'PASS' if not audit else audit}")
    assert not audit, f"LEAKAGE DETECTED: {audit}"

    # Reproducibility check against the submitted predictions.
    oof, _ = P3.run_spec(df[P3.DEMO], y, P3.DEMO, "logistic")
    old = stored[[f"M0__logistic__r{r}" for r in range(P3.N_REPEATS)]].to_numpy().T
    max_diff = float(np.max(np.abs(oof - old)))
    print(f"M0 logistic refit vs stored predictions: max abs diff = {max_diff:.2e}")
    assert max_diff < 1e-10, "refit does not reproduce the stored predictions"

    preds, summary = {}, []
    for algo in ("logistic", "random_forest", "xgboost"):
        t0 = time.time()
        oof, rows = P3.run_spec(df[M4], y, M4, algo)
        for rep in range(P3.N_REPEATS):
            preds[f"M4__{algo}__r{rep}"] = oof[rep]
        mean_auc = float(np.mean([r["auc"] for r in rows]))
        best = pd.Series([r["best"] for r in rows]).value_counts().to_dict()
        summary.append({"algo": algo, "fold_auc_mean": round(mean_auc, 4),
                        "best_params_counts": best})
        print(f"  M4 {algo:<14} fold AUC={mean_auc:.4f}  ({time.time() - t0:.0f}s)")

    out = pd.DataFrame(preds)
    out.insert(0, "SEQN", df.SEQN.to_numpy())
    out.insert(1, "y", y)
    out.to_parquet(INTERIM / "11_oof_predictions_m4.parquet", index=False)
    (INTERIM / "11_revision_models.json").write_text(json.dumps({
        "amendment": "PREREGISTRATION.md Amendment 1, item A2 (post hoc)",
        "n": int(len(df)), "events": int(y.sum()),
        "M4_features": M4, "n_features": len(M4),
        "reproducibility_check_M0_logistic_max_abs_diff": max_diff,
        "leakage_audit": "pass", "fits": summary,
    }, indent=1))
    print("wrote", INTERIM / "11_oof_predictions_m4.parquet")


if __name__ == "__main__":
    main()
