"""
Phase 1: build the analytic cohort.

Merges the 21 locked files across both cycles, applies per-variable reserved
codes, resolves skip patterns, derives row-wise indices, and writes an attrition
table. Fits nothing: every transform here is row-wise and therefore leakage-safe.
Scaling, imputation and encoding belong inside the CV folds in Phase 3.

Variable list is fixed by VARIABLE_LOCK.md. Do not add variables here without
updating that document first.

Outputs
    data/interim/01_cohort.parquet          one row per participant
    data/interim/01_attrition.csv           attrition table
    data/interim/01_cleaning_report.json    codes converted, per variable

Run:  python3 src/01_cohort.py
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
INTERIM = ROOT / "data" / "interim"

CYCLES = {"G": "2011-2012", "H": "2013-2014"}

# NHANES XPORT files encode every zero as this denormal when read by pandas.
# Verified across all 40 downloaded files: 330,496 cells hold it and not one
# cell holds a true 0.0. It is not confined to survey weights. It reaches
# cognitive scores of zero, PHQ-9 "not at all" responses, every below-detection
# comment code, and the alcohol frequency question. Any `== 0` test against raw
# NHANES data is therefore unreliable until this is normalised.
DENORMAL_ZERO = 5.397605346934028e-79
ZERO_EPS = 1e-60

# Reserved codes, verified against each variable's own codebook page.
# Absent from this map means the variable has no reserved codes. Applying a
# blanket 7/9 rule would corrupt ALQ130 (valid range 1 to 82) and every CFQ
# score (CFDCST1 ranges 0 to 10).
RESERVED = {
    "DMDEDUC2": [7, 9],
    "SMQ020": [7, 9],
    "SMQ040": [7, 9],
    "ALQ101": [7, 9],
    "ALQ120Q": [777, 999],
    "ALQ130": [777, 999],
    "MCQ160F": [7, 9],
    "DIQ010": [7, 9],
    "BPQ020": [7, 9],
    "BPQ080": [7, 9],
    **{f"DPQ0{i}0": [7, 9] for i in range(1, 10)},
}

DPQ_ITEMS = [f"DPQ0{i}0" for i in range(1, 10)]

# Columns pulled from each file. B12 is renamed per cycle, handled separately.
COLUMNS = {
    "DEMO": ["SEQN", "WTMEC2YR", "SDMVSTRA", "SDMVPSU", "SDDSRVYR", "RIDSTATR",
             "RIDAGEYR", "RIAGENDR", "RIDRETH3", "DMDEDUC2", "INDFMPIR"],
    "CFQ": ["SEQN", "CFDCST1", "CFDCST2", "CFDCST3", "CFDCSR", "CFDAST", "CFDDS",
            "CFASTAT", "CFALANG", "CFDCCS", "CFDCRNC", "CFDARNC", "CFDDRNC"],
    "PBCD": ["SEQN", "LBXBPB", "LBXBCD", "LBXTHG", "LBXBSE", "LBXBMN",
             "LBDBPBLC", "LBDBCDLC", "LBDTHGLC", "LBDBSELC", "LBDBMNLC"],
    "MMA": ["SEQN", "LBXMMASI"],
    "FOLFMS": ["SEQN", "LBDFOT"],
    "FOLATE": ["SEQN", "LBDRFO"],
    "VID": ["SEQN", "LBXVIDMS"],
    "CBC": ["SEQN", "LBXWBCSI", "LBDNENO", "LBDLYMNO", "LBDMONO", "LBXPLTSI"],
    "BIOPRO": ["SEQN", "LBXSAL", "LBXSCR", "LBXSTR", "LBXSIR"],
    "GHB": ["SEQN", "LBXGH"],
    "HDL": ["SEQN", "LBDHDD"],
    "TCHOL": ["SEQN", "LBXTC"],
    "BMX": ["SEQN", "BMXBMI"],
    "SMQ": ["SEQN", "SMQ020", "SMQ040"],
    "ALQ": ["SEQN", "ALQ101", "ALQ120Q", "ALQ130"],
    "MCQ": ["SEQN", "MCQ160F"],
    "DIQ": ["SEQN", "DIQ010"],
    "DPQ": ["SEQN"] + DPQ_ITEMS,
    "BPQ": ["SEQN", "BPQ020", "BPQ080"],
}

METALS = ["LBXBPB", "LBXBCD", "LBXTHG", "LBXBSE", "LBXBMN"]
LOD_FLAGS = {"LBXBPB": "LBDBPBLC", "LBXBCD": "LBDBCDLC", "LBXTHG": "LBDTHGLC",
             "LBXBSE": "LBDBSELC", "LBXBMN": "LBDBMNLC"}


def read_xpt(stem: str, cyc: str, cols: list[str] | None = None) -> pd.DataFrame:
    df = pd.read_sas(RAW / f"{stem}_{cyc}.xpt", format="xport")
    df.columns = [str(c) for c in df.columns]
    if cols is not None:
        missing = [c for c in cols if c not in df.columns]
        if missing:
            raise KeyError(f"{stem}_{cyc} is missing locked columns: {missing}")
        df = df[cols]
    if df["SEQN"].duplicated().any():
        raise ValueError(f"{stem}_{cyc} has duplicate SEQN values")
    return normalize_zeros(df)


def normalize_zeros(df: pd.DataFrame) -> pd.DataFrame:
    """Convert the NHANES denormal-zero encoding to a true 0.0.

    Applied to every float column before any comparison or arithmetic. Without
    this, `x == 0` silently matches nothing across the entire dataset.
    """
    for c in df.columns:
        if df[c].dtype.kind == "f":
            df.loc[df[c].abs() < ZERO_EPS, c] = 0.0
    return df


def apply_reserved_codes(df: pd.DataFrame) -> dict[str, int]:
    """Blank reserved codes in place. Returns count converted per variable."""
    converted = {}
    for var, codes in RESERVED.items():
        if var not in df.columns:
            continue
        hit = df[var].isin(codes)
        n = int(hit.sum())
        if n:
            df.loc[hit, var] = np.nan
        converted[var] = n
    return converted


def build_cycle(cyc: str) -> tuple[pd.DataFrame, dict]:
    """Merge one cycle onto the 60+ MEC-examined base."""
    demo = read_xpt("DEMO", cyc, COLUMNS["DEMO"])
    base = demo[(demo.RIDAGEYR >= 60) & (demo.RIDSTATR == 2)].copy()
    n_base = len(base)

    for stem, cols in COLUMNS.items():
        if stem == "DEMO":
            continue
        part = read_xpt(stem, cyc, cols)
        base = base.merge(part, on="SEQN", how="left")
        if len(base) != n_base:
            raise ValueError(f"merge of {stem}_{cyc} changed row count "
                             f"{n_base} -> {len(base)}")

    # B12 is LBXB12 in _G and LBDB12 in _H. LBDB12SI is common to both.
    b12 = read_xpt("VITB12", cyc, ["SEQN", "LBDB12SI"])
    base = base.merge(b12, on="SEQN", how="left")
    if len(base) != n_base:
        raise ValueError(f"merge of VITB12_{cyc} changed row count")

    base["cycle"] = CYCLES[cyc]
    converted = apply_reserved_codes(base)
    return base, converted


def derive(df: pd.DataFrame) -> pd.DataFrame:
    """Row-wise derivations only. Nothing here is fitted, so nothing leaks."""
    d = df.copy()

    # Cognitive component scores. CERAD immediate needs all three trials.
    d["cerad_immediate"] = d[["CFDCST1", "CFDCST2", "CFDCST3"]].sum(axis=1, min_count=3)
    d["cerad_delayed"] = d["CFDCSR"]
    d["animal_fluency"] = d["CFDAST"]
    d["dsst"] = d["CFDDS"]
    d["n_cog_scores"] = d[["cerad_immediate", "cerad_delayed",
                           "animal_fluency", "dsst"]].notna().sum(axis=1)

    # Smoking. SMQ040 is asked only when SMQ020 == 1, so a blank for a
    # never-smoker is a skip pattern, not missingness.
    never = d.SMQ020 == 2
    former = (d.SMQ020 == 1) & (d.SMQ040 == 3)
    current = (d.SMQ020 == 1) & d.SMQ040.isin([1, 2])
    d["smoking"] = pd.Series(pd.NA, index=d.index, dtype="object")
    d.loc[never, "smoking"] = "never"
    d.loc[former, "smoking"] = "former"
    d.loc[current, "smoking"] = "current"

    # Alcohol. Two nested skip patterns, both of which look like missingness.
    # ALQ101 asks about any one year of life, not the past year, so a person can
    # answer yes and still report no drinking in the past 12 months. ALQ130
    # (quantity) is skipped whenever ALQ120Q (frequency) is zero, which affects
    # 403 participants in this cohort. Both cases mean zero drinks, not unknown.
    d["drinks_per_day"] = d["ALQ130"]
    d.loc[d.ALQ101 == 2, "drinks_per_day"] = 0.0
    d.loc[d.ALQ120Q == 0, "drinks_per_day"] = 0.0

    # PHQ-9. All nine items required, which is the standard scoring rule.
    d["phq9"] = d[DPQ_ITEMS].sum(axis=1, min_count=9)

    # Inflammation indices from the CBC differential.
    lymph = d["LBDLYMNO"].replace(0, np.nan)
    d["nlr"] = d["LBDNENO"] / lymph
    d["plr"] = d["LBXPLTSI"] / lymph
    d["sii"] = d["LBXPLTSI"] * d["LBDNENO"] / lymph

    d["egfr"] = ckd_epi_2021(d["LBXSCR"], d["RIDAGEYR"], d["RIAGENDR"])

    # Binary covariates, with reserved codes already blanked.
    d["stroke"] = d["MCQ160F"].map({1: 1, 2: 0})
    d["diabetes"] = d["DIQ010"].map({1: 1, 2: 0, 3: 1})  # 3 = borderline
    d["hypertension"] = d["BPQ020"].map({1: 1, 2: 0})
    d["high_chol"] = d["BPQ080"].map({1: 1, 2: 0})

    # Right-skewed measures the brief calls for on a log scale.
    for col in METALS + ["LBXMMASI", "LBDB12SI", "sii"]:
        d[f"log_{col}"] = np.log(d[col].where(d[col] > 0))

    return d


def ckd_epi_2021(scr: pd.Series, age: pd.Series, sex: pd.Series) -> pd.Series:
    """CKD-EPI 2021 creatinine equation, without the race coefficient."""
    female = sex == 2
    kappa = np.where(female, 0.7, 0.9)
    alpha = np.where(female, -0.241, -0.302)
    ratio = scr / kappa
    egfr = (142.0
            * np.minimum(ratio, 1.0) ** alpha
            * np.maximum(ratio, 1.0) ** -1.200
            * 0.9938 ** age
            * np.where(female, 1.012, 1.0))
    return pd.Series(egfr, index=scr.index).where(scr.notna())


def attrition(df: pd.DataFrame) -> pd.DataFrame:
    """Sequential attrition, per cycle and combined."""
    steps = [
        ("Aged 60+, MEC examined", pd.Series(True, index=df.index)),
        ("... with >= 3 of 4 cognitive scores", df.n_cog_scores >= 3),
        ("... and all 5 blood metals", (df.n_cog_scores >= 3) & df[METALS].notna().all(axis=1)),
        ("... and serum B12", (df.n_cog_scores >= 3) & df[METALS].notna().all(axis=1)
         & df.LBDB12SI.notna()),
    ]
    rows = []
    for label, mask in steps:
        row = {"step": label}
        for cyc in CYCLES.values():
            row[cyc] = int((mask & (df.cycle == cyc)).sum())
        row["combined"] = int(mask.sum())
        rows.append(row)
    return pd.DataFrame(rows)


def check(df: pd.DataFrame) -> None:
    """Hard assertions. These abort the chain rather than warn."""
    assert df.SEQN.is_unique, "SEQN is not unique after stacking cycles"

    for var, codes in RESERVED.items():
        if var in df.columns:
            left = int(df[var].isin(codes).sum())
            assert left == 0, f"{var} still holds reserved codes {codes}: {left} rows"

    # CFQ scores must NOT have been touched: 7 and 9 are valid there.
    assert df.CFDCST1.max() <= 10, "CFDCST1 out of codebook range 0 to 10"
    assert (df.n_cog_scores <= 4).all(), "more than four cognitive scores counted"

    empty = [c for c in df.columns if df[c].notna().sum() == 0]
    assert not empty, f"columns are entirely missing: {empty}"

    assert (df.RIDAGEYR >= 60).all(), "cohort contains participants under 60"
    assert (df.RIDSTATR == 2).all(), "cohort contains non-MEC participants"

    left = {c: int((df[c] == DENORMAL_ZERO).sum()) for c in df.columns
            if df[c].dtype.kind == "f" and (df[c] == DENORMAL_ZERO).any()}
    assert not left, f"denormal-zero encoding survived cleaning in: {left}"

    assert (df.WTMEC2YR > ZERO_EPS).all(), "cohort contains zero-weight records"
    pop = df.WTMEC2YR.sum()
    assert 4e7 < pop < 9e7, f"weighted 60+ population implausible: {pop:,.0f}"


def main() -> None:
    INTERIM.mkdir(parents=True, exist_ok=True)
    frames, cleaning = [], {}
    for cyc in CYCLES:
        df, converted = build_cycle(cyc)
        cleaning[CYCLES[cyc]] = converted
        frames.append(df)

    cohort = pd.concat(frames, ignore_index=True)
    # Two cycles pooled, so the two-year MEC weight is halved.
    cohort["WTMEC2YR"] = cohort["WTMEC2YR"] / 2.0
    cohort = derive(cohort)
    check(cohort)

    lod = {c: round(100.0 * float((cohort.loc[cohort[c].notna(), f] == 1).mean()), 1)
           for c, f in LOD_FLAGS.items()}

    cohort.to_parquet(INTERIM / "01_cohort.parquet", index=False)
    table = attrition(cohort)
    table.to_csv(INTERIM / "01_attrition.csv", index=False)
    (INTERIM / "01_cleaning_report.json").write_text(json.dumps(
        {"reserved_codes_converted": cleaning,
         "pct_below_lod": lod,
         "weighted_population_60plus": float(cohort.WTMEC2YR.sum()),
         "n_rows": int(len(cohort)),
         "n_columns": int(cohort.shape[1])}, indent=1))

    print(f"cohort rows: {len(cohort)}  columns: {cohort.shape[1]}")
    print(f"weighted 60+ population: {cohort.WTMEC2YR.sum():,.0f}")
    print("\nattrition:")
    print(table.to_string(index=False))
    print("\npercent below LOD:", lod)
    print("\nreserved codes converted to NaN:")
    for cyc, d in cleaning.items():
        nz = {k: v for k, v in d.items() if v}
        print(f"  {cyc}: {nz if nz else 'none'}")
    print("\nwrote", INTERIM / "01_cohort.parquet")


if __name__ == "__main__":
    main()
