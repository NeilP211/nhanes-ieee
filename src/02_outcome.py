"""
Phase 2: construct the cognitive outcome.

Z-scores the four test scores within the pooled 60+ sample, averages them under
the pre-specified ">= 3 of 4 present" rule, and cuts the lowest quartile to form
the primary label.

Terminology: the label is LOW COGNITIVE PERFORMANCE. NHANES contains no clinical
diagnosis, so it is never cognitive impairment.

A note for the pre-registration. The label is defined against pooled-sample
quantiles, so a held-out participant's label depends on the whole sample's
distribution. That is definitional, not predictive leakage: the outcome is
explicitly relative ("lowest quartile of this population"), and defining it
per-fold would make the target itself move between folds. Pre-specify it.

Outputs
    data/interim/02_outcome.parquet      cohort plus outcome columns
    data/interim/02_outcome_report.json  distributions, alpha, rule comparison

Run:  python3 src/02_outcome.py
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
INTERIM = ROOT / "data" / "interim"

TESTS = ["cerad_immediate", "cerad_delayed", "animal_fluency", "dsst"]
PRIMARY_CUT = 0.25
SENSITIVITY_CUTS = [0.10, 0.20]


def zscore(s: pd.Series) -> pd.Series:
    """Z-score within the pooled sample, ignoring missing values."""
    return (s - s.mean()) / s.std(ddof=1)


def cronbach_alpha(df: pd.DataFrame) -> float:
    """Standard alpha over complete cases of the supplied item columns."""
    d = df.dropna()
    k = d.shape[1]
    item_var = d.var(axis=0, ddof=1).sum()
    total_var = d.sum(axis=1).var(ddof=1)
    return float((k / (k - 1)) * (1 - item_var / total_var))


def build_composite(df: pd.DataFrame, min_scores: int) -> pd.Series:
    """Mean of available z-scores, requiring at least min_scores present."""
    z = df[[f"z_{t}" for t in TESTS]]
    return z.mean(axis=1).where(z.notna().sum(axis=1) >= min_scores)


def main() -> None:
    cohort = pd.read_parquet(INTERIM / "01_cohort.parquet")

    # Z-score within the pooled 60+ sample, per the brief.
    for t in TESTS:
        cohort[f"z_{t}"] = zscore(cohort[t])

    cohort["composite_z"] = build_composite(cohort, min_scores=3)
    eligible = cohort.composite_z.notna()

    # Primary label: lowest quartile of the composite.
    cut = cohort.loc[eligible, "composite_z"].quantile(PRIMARY_CUT)
    cohort["low_cog"] = np.where(eligible, (cohort.composite_z <= cut).astype("float"), np.nan)

    # Pre-specified sensitivity cutoffs.
    for q in SENSITIVITY_CUTS:
        c = cohort.loc[eligible, "composite_z"].quantile(q)
        cohort[f"low_cog_p{int(q * 100)}"] = np.where(
            eligible, (cohort.composite_z <= c).astype("float"), np.nan)

    # H4: each test as its own outcome, lowest quartile of that test.
    for t in TESTS:
        z = cohort[f"z_{t}"]
        c = z.quantile(PRIMARY_CUT)
        cohort[f"low_{t}"] = np.where(z.notna(), (z <= c).astype("float"), np.nan)

    # Alternative eligibility rule for the Gate 2 decision. CFASTAT counts three
    # instruments, so CERAD's two scores are not independent of each other.
    cerad_done = cohort[["z_cerad_immediate", "z_cerad_delayed"]].notna().any(axis=1)
    n_instruments = (cerad_done.astype(int)
                     + cohort.z_animal_fluency.notna().astype(int)
                     + cohort.z_dsst.notna().astype(int))
    alt_eligible = n_instruments >= 2
    cohort["eligible_alt_rule"] = alt_eligible

    report = {
        "definition": {
            "tests": TESTS,
            "rule": ">= 3 of 4 z-scored component scores present",
            "primary_cut": "lowest quartile of the pooled composite",
            "terminology": "low cognitive performance, never cognitive impairment",
        },
        "n": {
            "cohort": int(len(cohort)),
            "eligible_primary_rule": int(eligible.sum()),
            "eligible_alt_rule_2_of_3_instruments": int(alt_eligible.sum()),
            "differ_between_rules": int((eligible != alt_eligible).sum()),
        },
        "composite": {
            "mean": float(cohort.loc[eligible, "composite_z"].mean()),
            "sd": float(cohort.loc[eligible, "composite_z"].std(ddof=1)),
            "quartile_cut": float(cut),
        },
        "prevalence": {
            "low_cog_primary": float(cohort.low_cog.mean(skipna=True)),
            **{f"low_cog_p{int(q * 100)}": float(cohort[f"low_cog_p{int(q * 100)}"].mean(skipna=True))
               for q in SENSITIVITY_CUTS},
        },
        "internal_consistency": {
            "cronbach_alpha_4_z_scores": cronbach_alpha(cohort[[f"z_{t}" for t in TESTS]]),
            "pairwise_correlations": cohort[[f"z_{t}" for t in TESTS]].corr().round(3).to_dict(),
        },
        "component_missingness_in_cohort": {
            t: int(cohort[t].isna().sum()) for t in TESTS
        },
        "test_language": cohort.CFALANG.value_counts(dropna=False).to_dict(),
        "dsst_not_done_reasons": cohort.CFDDRNC.value_counts(dropna=False).to_dict(),
        "analytic_n_with_predictors": {
            "eligible_and_all_metals": int(
                (eligible & cohort[["LBXBPB", "LBXBCD", "LBXTHG", "LBXBSE", "LBXBMN"]]
                 .notna().all(axis=1)).sum()),
        },
    }

    check(cohort, eligible)
    cohort.to_parquet(INTERIM / "02_outcome.parquet", index=False)
    (INTERIM / "02_outcome_report.json").write_text(
        json.dumps(report, indent=1, default=str))

    print(f"eligible for outcome (>= 3 of 4 scores): {int(eligible.sum())}")
    print(f"prevalence of low cognitive performance: {cohort.low_cog.mean(skipna=True):.4f}")
    print(f"cronbach alpha across the four z-scores : "
          f"{report['internal_consistency']['cronbach_alpha_4_z_scores']:.3f}")
    print(f"composite quartile cut (z)              : {cut:.4f}")
    print("\nprevalence at each pre-specified cutoff:")
    for k, v in report["prevalence"].items():
        print(f"   {k:<18} {v:.4f}")
    print("\nrule comparison (Gate 2 decision):")
    print(f"   primary rule, >= 3 of 4 scores        : {int(eligible.sum())}")
    print(f"   alternative, >= 2 of 3 instruments    : {int(alt_eligible.sum())}")
    print(f"   participants classified differently   : "
          f"{report['n']['differ_between_rules']}")
    print("\nwrote", INTERIM / "02_outcome.parquet")


def check(df: pd.DataFrame, eligible: pd.Series) -> None:
    """Hard assertions."""
    prev = df.low_cog.mean(skipna=True)
    assert 0.20 < prev < 0.30, f"prevalence {prev:.3f} is not near the intended quartile"
    assert df.loc[~eligible, "low_cog"].isna().all(), "ineligible rows carry a label"
    assert df.loc[eligible, "low_cog"].notna().all(), "eligible rows missing a label"
    for t in TESTS:
        z = df[f"z_{t}"]
        assert abs(z.mean()) < 1e-9, f"z_{t} is not centred"
        assert abs(z.std(ddof=1) - 1) < 1e-9, f"z_{t} is not unit variance"
    assert df.composite_z.notna().sum() == int(eligible.sum())


if __name__ == "__main__":
    main()
