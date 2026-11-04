"""
Phase 12 (revision): outcome-construction descriptives requested by reviewer 2.

Pre-registration Amendment 1, item A6. Descriptive only; nothing here touches a
predictor-outcome relationship.

  T1c  Cognitive phenotype of the analytic sample (n = 1,784), overall and by
       outcome status: raw scores for all four measures, the composite's
       distribution and cutoff, language of administration, and the number of
       component scores.
  S2   Missing cognitive scores by test and by the NHANES reason code, among
       the 3,472 examined participants aged 60 and over.
  S3   Missing cognitive scores by demographic group.
  S4   Three-score against four-score participants, in the labelled sample and
       in the analytic sample.
  S5   Labelled (>= 3 of 4 scores) against unlabelled participants.

Reason codes were checked against the CDC codebooks for CFQ_G and CFQ_H
(data/interim/cdc_cache/doc_CFQ_*.htm): CFASTAT 4 = ineligible, proxy;
5 = ineligible, other language; 6 = no test done. CFDCRNC, CFDARNC and CFDDRNC
share codes 1 = did not consent to audio record, 2 = communication problem,
3 = physical limitation, 4 = quit or gave up (CERAD only), 5 = refused,
6 = equipment failure, 7 = other.

Outputs
    data/interim/12_revision_outcome.json
    output/tables/12_revision_outcome.md

Run:  python3 src/12_revision_outcome.py
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
INTERIM = ROOT / "data" / "interim"
TABLES = ROOT / "output" / "tables"

TESTS = {"cerad_immediate": "CERAD immediate recall (sum of 3 trials, 0 to 30)",
         "cerad_delayed": "CERAD delayed recall (0 to 10)",
         "animal_fluency": "Animal fluency (animals named in 60 s)",
         "dsst": "Digit Symbol Substitution Test (correct symbols)"}
REASON_VAR = {"cerad_immediate": "CFDCRNC", "cerad_delayed": "CFDCRNC",
              "animal_fluency": "CFDARNC", "dsst": "CFDDRNC"}
REASON = {1: "Did not consent to audio recording", 2: "Communication problem",
          3: "Physical limitation", 4: "Quit or gave up", 5: "Refused",
          6: "Equipment failure", 7: "Other"}
STATUS = {4: "Not eligible: proxy respondent", 5: "Not eligible: language not offered",
          6: "No cognitive test done"}
LANG = {1: "English", 2: "Spanish", 3: "Asian language"}
RACE = {1: "Mexican American", 2: "Other Hispanic", 3: "Non-Hispanic White",
        4: "Non-Hispanic Black", 6: "Non-Hispanic Asian", 7: "Other/multiracial"}
EDUC = {1: "Less than 9th grade", 2: "9-11th grade", 3: "High school grad/GED",
        4: "Some college/AA degree", 5: "College graduate or above"}


def load_table1_helpers():
    spec = importlib.util.spec_from_file_location("t1", ROOT / "src" / "09_table1.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


T1 = load_table1_helpers()


def pct(n: int, d: int) -> str:
    return f"{n} ({100 * n / d:.1f}%)" if d else "0"


def missing_reason(row: pd.Series, test: str) -> str | None:
    """Why a score is missing, or None if it is present."""
    if pd.notna(row[test]):
        return None
    status = row["CFASTAT"]
    if status in STATUS:
        return STATUS[int(status)]
    code = row[REASON_VAR[test]]
    if pd.notna(code):
        return REASON[int(code)]
    return "Missing, no reason recorded"


def table_s2(df: pd.DataFrame) -> list[dict]:
    order = list(STATUS.values()) + list(REASON.values()) + ["Missing, no reason recorded"]
    counts = {t: df.apply(missing_reason, axis=1, test=t).value_counts() for t in TESTS}
    rows = []
    for reason in order:
        vals = {t: int(counts[t].get(reason, 0)) for t in TESTS}
        if any(vals.values()):
            rows.append({"reason": reason, **vals})
    rows.append({"reason": "Total missing", **{t: int(df[t].isna().sum()) for t in TESTS}})
    rows.append({"reason": "Score present", **{t: int(df[t].notna().sum()) for t in TESTS}})
    for r in rows[:-2]:
        assert r["reason"] in order
    for t in TESTS:
        assert sum(r[t] for r in rows[:-2]) == int(df[t].isna().sum()), t
    return rows


def groups(df: pd.DataFrame) -> list[tuple[str, pd.Series]]:
    age = df.RIDAGEYR
    out = [("All examined, aged 60+", pd.Series(True, index=df.index)),
           ("Age 60 to 69", age.between(60, 69)), ("Age 70 to 79", age.between(70, 79)),
           ("Age 80 (top-coded, 80 and over)", age >= 80),
           ("Male", df.RIAGENDR == 1), ("Female", df.RIAGENDR == 2)]
    out += [(name, df.RIDRETH3 == code) for code, name in RACE.items()]
    out += [(name, df.DMDEDUC2 == code) for code, name in EDUC.items()]
    out += [("Education missing", df.DMDEDUC2.isna())]
    return out


def table_s3(df: pd.DataFrame) -> list[dict]:
    rows = []
    for name, mask in groups(df):
        d = df[mask]
        n = len(d)
        row = {"group": name, "n": n}
        for t in TESTS:
            row[t] = f"{100 * d[t].isna().mean():.1f}%" if n else ""
        row["fewer_than_3_scores"] = f"{100 * (d.n_cog_scores < 3).mean():.1f}%" if n else ""
        rows.append(row)
    return rows


def describe_group(d: pd.DataFrame) -> dict:
    n = len(d)
    return {
        "n": n,
        "Age, years, mean (SD)": f"{d.RIDAGEYR.mean():.1f} ({d.RIDAGEYR.std():.1f})",
        "Female": pct(int((d.RIAGENDR == 2).sum()), n),
        "Less than high school education": pct(int(d.DMDEDUC2.isin([1, 2]).sum()), n),
        "Hispanic (Mexican American or other Hispanic)": pct(int(d.RIDRETH3.isin([1, 2]).sum()), n),
        "Non-Hispanic Black": pct(int((d.RIDRETH3 == 4).sum()), n),
        "Income-to-poverty ratio, mean (SD)": f"{d.INDFMPIR.mean():.2f} ({d.INDFMPIR.std():.2f})",
        "Tested in Spanish or an Asian language": pct(int(d.CFALANG.isin([2, 3]).sum()), n),
        "Missing score: CERAD immediate recall": pct(int(d.cerad_immediate.isna().sum()), n),
        "Missing score: CERAD delayed recall": pct(int(d.cerad_delayed.isna().sum()), n),
        "Missing score: animal fluency": pct(int(d.animal_fluency.isna().sum()), n),
        "Missing score: DSST": pct(int(d.dsst.isna().sum()), n),
        "Composite z, mean (SD)": f"{d.composite_z.mean():.2f} ({d.composite_z.std():.2f})",
        "Low cognitive performance": pct(int((d.low_cog == 1).sum()), n),
    }


def table_s4(labelled: pd.DataFrame, analytic: pd.DataFrame) -> dict:
    return {
        "labelled": {"Four scores": describe_group(labelled[labelled.n_cog_scores == 4]),
                     "Three scores": describe_group(labelled[labelled.n_cog_scores == 3])},
        "analytic": {"Four scores": describe_group(analytic[analytic.n_cog_scores == 4]),
                     "Three scores": describe_group(analytic[analytic.n_cog_scores == 3])},
    }


def table_s5(df: pd.DataFrame) -> dict:
    out = {}
    for name, d in [("Labelled (3 or 4 scores)", df[df.n_cog_scores >= 3]),
                    ("Unlabelled (0 to 2 scores)", df[df.n_cog_scores < 3])]:
        n = len(d)
        out[name] = {
            "n": n,
            "Age, years, mean (SD)": f"{d.RIDAGEYR.mean():.1f} ({d.RIDAGEYR.std():.1f})",
            "Age 80 (top-coded)": pct(int((d.RIDAGEYR >= 80).sum()), n),
            "Female": pct(int((d.RIAGENDR == 2).sum()), n),
            "Less than high school education": pct(int(d.DMDEDUC2.isin([1, 2]).sum()), n),
            "Hispanic (Mexican American or other Hispanic)": pct(int(d.RIDRETH3.isin([1, 2]).sum()), n),
            "Non-Hispanic Black": pct(int((d.RIDRETH3 == 4).sum()), n),
            "Income-to-poverty ratio, mean (SD)": f"{d.INDFMPIR.mean():.2f} ({d.INDFMPIR.std():.2f})",
            "Ever told had a stroke": pct(int((d.stroke == 1).sum()), n),
            "Ever told had diabetes": pct(int((d.diabetes == 1).sum()), n),
            "PHQ-9, median [IQR]": T1.summarise_continuous(d.phq9, True),
            "Proxy respondent or no test done": pct(int(d.CFASTAT.isin([4, 6]).sum()), n),
            "Not tested: language not offered": pct(int((d.CFASTAT == 5).sum()), n),
        }
    return out


def table_t1c(analytic: pd.DataFrame, cut: float) -> list[dict]:
    grp = {"Overall": analytic, "Low cognitive performance": analytic[analytic.low_cog == 1],
           "Not low cognitive performance": analytic[analytic.low_cog == 0]}
    rows = []

    def add(label, fn):
        rows.append({"characteristic": label, **{g: fn(d) for g, d in grp.items()}})

    for t, label in TESTS.items():
        use_median, stat = T1.decide_statistic(analytic[t])
        add(f"{label}, {stat}", lambda d, t=t, m=use_median: T1.summarise_continuous(d[t], m))
        if analytic[t].isna().any():
            add(f"   score missing", lambda d, t=t: pct(int(d[t].isna().sum()), len(d)))
    add("Composite z-score, mean (SD)",
        lambda d: f"{d.composite_z.mean():.2f} ({d.composite_z.std():.2f})")
    add("Composite z-score, median [IQR]", lambda d: T1.summarise_continuous(d.composite_z, True))
    add("Composite z-score, range",
        lambda d: f"{d.composite_z.min():.2f} to {d.composite_z.max():.2f}")
    for code, name in LANG.items():
        add(f"Language of administration = {name}",
            lambda d, c=code: pct(int((d.CFALANG == c).sum()), len(d)))
    add("Component scores = 4", lambda d: pct(int((d.n_cog_scores == 4).sum()), len(d)))
    add("Component scores = 3", lambda d: pct(int((d.n_cog_scores == 3).sum()), len(d)))
    rows.append({"characteristic": f"Outcome cutoff, composite z <= {cut:.3f} "
                 "(lowest quartile of the 3,124 labelled participants)",
                 "Overall": "", "Low cognitive performance": "",
                 "Not low cognitive performance": ""})
    return rows


def md_table(rows: list[dict], first: str, cols: list[str]) -> str:
    out = ["| " + first + " | " + " | ".join(cols) + " |",
           "|---|" + "|".join(["---"] * len(cols)) + "|"]
    for r in rows:
        out.append("| " + str(r[first]) + " | " + " | ".join(str(r.get(c, "")) for c in cols) + " |")
    return "\n".join(out)


def dict_table(d: dict) -> str:
    cols = list(d.keys())
    keys = list(next(iter(d.values())).keys())
    rows = [{"item": k, **{c: d[c][k] for c in cols}} for k in keys]
    return md_table(rows, "item", cols)


def main() -> None:
    TABLES.mkdir(parents=True, exist_ok=True)
    df = pd.read_parquet(INTERIM / "02_outcome.parquet")
    report = json.loads((INTERIM / "02_outcome_report.json").read_text())
    cut = report["composite"]["quartile_cut"]
    locked = set(pd.read_csv(INTERIM / "02_analytic_seqn.csv").SEQN)
    labelled = df[df.n_cog_scores >= 3]
    analytic = df[df.SEQN.isin(locked)]
    assert len(df) == 3472 and len(labelled) == 3124 and len(analytic) == 1784
    assert int(analytic.low_cog.sum()) == 431

    t1c = table_t1c(analytic, cut)
    s2 = table_s2(df)
    s3 = table_s3(df)
    s4 = table_s4(labelled, analytic)
    s5 = table_s5(df)

    (INTERIM / "12_revision_outcome.json").write_text(json.dumps({
        "amendment": "PREREGISTRATION.md Amendment 1, item A6 (post hoc, descriptive)",
        "quartile_cut_z": cut, "table1c": t1c, "s2_missing_by_reason": s2,
        "s3_missing_by_group": s3, "s4_three_vs_four": s4, "s5_labelled_vs_not": s5,
    }, indent=1))

    g3 = ["Overall", "Low cognitive performance", "Not low cognitive performance"]
    md = ["# Revision tables: outcome construction (Amendment 1, A6)", "",
          "## Table 1c. Cognitive phenotype, analytic sample (n = 1,784)", "",
          md_table(t1c, "characteristic", g3), "",
          "## Table S2. Missing cognitive scores by test and reason, all 3,472 "
          "examined participants aged 60+", "",
          md_table(s2, "reason", list(TESTS)), "",
          "## Table S3. Missing cognitive scores by demographic group", "",
          md_table(s3, "group", ["n", *TESTS, "fewer_than_3_scores"]), "",
          "## Table S4a. Three-score versus four-score participants, labelled sample (n = 3,124)", "",
          dict_table(s4["labelled"]), "",
          "## Table S4b. Three-score versus four-score participants, analytic sample (n = 1,784)", "",
          dict_table(s4["analytic"]), "",
          "## Table S5. Labelled versus unlabelled participants (n = 3,472)", "",
          dict_table(s5), ""]
    (TABLES / "12_revision_outcome.md").write_text("\n".join(md))
    print("\n".join(md))


if __name__ == "__main__":
    main()
