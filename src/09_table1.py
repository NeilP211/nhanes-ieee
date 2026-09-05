"""
Phase 9 (manuscript support): Table 1, TRIPOD+AI item 14b.

Two tables, both computed fresh from `02_outcome.parquet` against the
locked analytic sample (`02_analytic_seqn.csv`), not copied from the
pre-lock Gate 2 diagnostics (which used a provisional n=1,789/1,335 before
the final variable-list amendment settled on n=1,784/1,340):

  Table 1a. Baseline characteristics of the analytic sample (n=1,784),
            overall and by outcome status. Every M3 feature plus the M0+
            covariates, matching the model specification in
            `data/interim/03_model_report.json` exactly.
  Table 1b. Included (n=1,784) versus excluded-but-outcome-eligible
            (n=1,340) comparison -- the selection check already summarised
            in prose in the Discussion; this is its underlying table.

Continuous variables are reported as mean (SD) unless sample skewness
exceeds 1 in absolute value, in which case median [IQR] is used instead
(documented per-variable in the output so the choice is auditable, not
applied silently).

Outputs
    data/interim/09_table1.json
    output/tables/09_table1.md

Run:  python3 src/09_table1.py
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import skew

ROOT = Path(__file__).resolve().parent.parent
INTERIM = ROOT / "data" / "interim"
TABLES = ROOT / "output" / "tables"

DEMO = ["RIDAGEYR", "RIAGENDR", "RIDRETH3", "DMDEDUC2", "INDFMPIR"]
METALS = ["LBXBPB", "LBXBCD", "LBXTHG", "LBXBSE", "LBXBMN"]
NUTR_CONT = ["LBDB12SI", "LBXMMASI", "LBDFOT", "LBDRFO", "LBXVIDMS", "LBXGH",
             "LBDHDD", "LBXTC", "LBXSTR", "LBXSAL", "LBXSIR", "egfr", "nlr",
             "plr", "sii"]
COVAR_CONT = ["BMXBMI", "drinks_per_day", "phq9"]
COVAR_BIN = ["stroke", "diabetes", "hypertension", "high_chol"]

CONTINUOUS = ["RIDAGEYR", "INDFMPIR"] + METALS + NUTR_CONT + COVAR_CONT
CATEGORICAL = {"RIAGENDR": {1: "Male", 2: "Female"},
               "RIDRETH3": {1: "Mexican American", 2: "Other Hispanic",
                            3: "Non-Hispanic White", 4: "Non-Hispanic Black",
                            6: "Non-Hispanic Asian",
                            7: "Other/multiracial"},
               "DMDEDUC2": {1: "Less than 9th grade",
                            2: "9-11th grade", 3: "High school grad/GED",
                            4: "Some college/AA degree",
                            5: "College graduate or above"}}
BINARY = {"stroke": "Ever told had a stroke",
          "diabetes": "Ever told had diabetes",
          "hypertension": "Ever told had high blood pressure",
          "high_chol": "Ever told had high cholesterol"}

# `smoking` is a derived categorical string ("never"/"former"/"current"),
# not binary -- checked against src/01_cohort.py rather than assumed, since
# an earlier version of this script wrongly tested it as `== 1` and
# reported 0.0% smokers in every group.
SMOKING_CATEGORIES = ["never", "former", "current"]

LABELS = {
    "RIDAGEYR": "Age, years", "INDFMPIR": "Income-to-poverty ratio",
    "LBXBPB": "Blood lead, ug/dL", "LBXBCD": "Blood cadmium, ug/L",
    "LBXTHG": "Blood total mercury, ug/L", "LBXBSE": "Blood selenium, ug/L",
    "LBXBMN": "Blood manganese, ug/L",
    "LBDB12SI": "Serum vitamin B12, pmol/L",
    "LBXMMASI": "Serum methylmalonic acid, umol/L",
    "LBDFOT": "Serum total folate, nmol/L", "LBDRFO": "RBC folate, nmol/L",
    "LBXVIDMS": "25-hydroxyvitamin D, nmol/L", "LBXGH": "HbA1c, %",
    "LBDHDD": "HDL cholesterol, mg/dL", "LBXTC": "Total cholesterol, mg/dL",
    "LBXSTR": "Triglycerides, mg/dL", "LBXSAL": "Serum albumin, g/dL",
    "LBXSIR": "Serum iron, ug/dL", "egfr": "eGFR, mL/min/1.73m2",
    "nlr": "Neutrophil-to-lymphocyte ratio",
    "plr": "Platelet-to-lymphocyte ratio", "sii": "Systemic immune-inflammation index",
    "BMXBMI": "Body mass index, kg/m2", "drinks_per_day": "Alcoholic drinks per day",
    "phq9": "PHQ-9 depression score",
}


def decide_statistic(s: pd.Series) -> tuple[bool, str]:
    """Decide mean(SD) vs median[IQR] once, from the full column (not a
    subgroup), so every subgroup in a row reports the same statistic."""
    s = s.dropna()
    sk = skew(s) if len(s) > 2 else 0.0
    return (True, "median [IQR]") if abs(sk) > 1 else (False, "mean (SD)")


def summarise_continuous(s: pd.Series, use_median: bool) -> str:
    s = s.dropna()
    if use_median:
        q1, med, q3 = s.quantile([0.25, 0.5, 0.75])
        return f"{med:.2f} [{q1:.2f}, {q3:.2f}]"
    return f"{s.mean():.2f} ({s.std():.2f})"


def build_table1a(df: pd.DataFrame) -> list[dict]:
    rows = []
    groups = {"Overall": df, "Low cognitive performance": df[df.low_cog == 1],
              "Not low cognitive performance": df[df.low_cog == 0]}

    def add_row(label, values):
        rows.append({"characteristic": label, **values})

    add_row("n", {g: str(len(d)) for g, d in groups.items()})

    for var in CONTINUOUS:
        use_median, stat_name = decide_statistic(df[var])
        vals = {g: summarise_continuous(d[var], use_median) for g, d in groups.items()}
        add_row(f"{LABELS.get(var, var)}, {stat_name}", vals)

    for var, mapping in CATEGORICAL.items():
        for code, name in mapping.items():
            vals = {}
            for g, d in groups.items():
                n = int((d[var] == code).sum())
                pct = 100 * n / len(d) if len(d) else float("nan")
                vals[g] = f"{n} ({pct:.1f}%)"
            add_row(f"{var} = {name}", vals)

    for cat in SMOKING_CATEGORIES:
        vals = {}
        for g, d in groups.items():
            n = int((d["smoking"] == cat).sum())
            pct = 100 * n / len(d) if len(d) else float("nan")
            vals[g] = f"{n} ({pct:.1f}%)"
        add_row(f"Smoking status = {cat}", vals)

    for var, label in BINARY.items():
        vals = {}
        for g, d in groups.items():
            n = int((d[var] == 1).sum())
            pct = 100 * n / len(d) if len(d) else float("nan")
            vals[g] = f"{n} ({pct:.1f}%)"
        add_row(label, vals)

    return rows


def build_table1b(eligible: pd.DataFrame, locked_seqn: set) -> list[dict]:
    included = eligible[eligible.SEQN.isin(locked_seqn)]
    excluded = eligible[~eligible.SEQN.isin(locked_seqn)]
    groups = {"Included (n=1,784)": included,
              f"Excluded (n={len(excluded):,})": excluded}

    rows = []

    def add_row(label, values):
        rows.append({"characteristic": label, **values})

    add_row("n", {g: str(len(d)) for g, d in groups.items()})
    for var in ["RIDAGEYR", "INDFMPIR", "phq9"]:
        use_median, stat_name = decide_statistic(eligible[var])
        vals = {g: summarise_continuous(d[var], use_median) for g, d in groups.items()}
        add_row(f"{LABELS.get(var, var)}, {stat_name}", vals)
    for var, label in [("RIAGENDR", "Female, %"), ("low_cog", "Low cognitive performance, %"),
                        ("diabetes", "Diabetes, %")]:
        vals = {}
        for g, d in groups.items():
            if var == "RIAGENDR":
                n = int((d[var] == 2).sum())
            else:
                n = int((d[var] == 1).sum())
            pct = 100 * n / len(d) if len(d) else float("nan")
            vals[g] = f"{pct:.1f}%"
        add_row(label, vals)
    return rows


def rows_to_markdown(rows: list[dict], group_cols: list[str]) -> str:
    header = "| Characteristic | " + " | ".join(group_cols) + " |"
    sep = "|---|" + "|".join(["---"] * len(group_cols)) + "|"
    lines = [header, sep]
    for r in rows:
        lines.append("| " + r["characteristic"] + " | " +
                      " | ".join(str(r.get(g, "")) for g in group_cols) + " |")
    return "\n".join(lines)


def main() -> None:
    df = pd.read_parquet(INTERIM / "02_outcome.parquet")
    locked_seqn = set(pd.read_csv(INTERIM / "02_analytic_seqn.csv").SEQN)
    eligible = df[df.n_cog_scores >= 3].copy()
    analytic = eligible[eligible.SEQN.isin(locked_seqn)].copy()

    assert len(analytic) == 1784, f"expected n=1,784, got {len(analytic)}"
    assert int(analytic.low_cog.sum()) == 431, \
        f"expected 431 events, got {int(analytic.low_cog.sum())}"

    table1a = build_table1a(analytic)
    table1b = build_table1b(eligible, locked_seqn)

    (INTERIM / "09_table1.json").write_text(json.dumps(
        {"table1a": table1a, "table1b": table1b}, indent=1))

    md = ["# Table 1: participant characteristics", "",
          "**TRIPOD+AI item 14b.** Computed fresh from `02_outcome.parquet` "
          "against the locked analytic sample; not copied from the "
          "pre-lock Gate 2 diagnostics. Skewed continuous variables "
          "(sample skewness > 1) are reported as median [IQR] rather than "
          "mean (SD); which statistic applies is stated per row.", "",
          "## Table 1a. Analytic sample (n = 1,784), overall and by outcome status",
          "",
          rows_to_markdown(table1a, ["Overall", "Low cognitive performance",
                                     "Not low cognitive performance"]),
          "",
          "## Table 1b. Included versus excluded, among the 3,124 "
          "outcome-eligible participants", "",
          "Underlies the selection-bias statement in the Discussion "
          "(\"participants excluded for missing data were slightly older "
          "and slightly more likely to meet the outcome definition\").",
          "",
          rows_to_markdown(table1b, list(table1b[0].keys())[1:]
                            if table1b else []),
          ]
    (TABLES / "09_table1.md").write_text("\n".join(md) + "\n")

    print(f"Table 1a: {len(table1a)} rows, groups: Overall / Low cognitive "
          f"performance / Not low cognitive performance")
    print(f"Table 1b: {len(table1b)} rows, included n={len(locked_seqn)}, "
          f"excluded n={len(eligible) - len(locked_seqn)}")
    print("wrote data/interim/09_table1.json, output/tables/09_table1.md")


if __name__ == "__main__":
    main()
