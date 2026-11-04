"""
Phase 14 (revision): render every revision number into LaTeX table bodies.

Reads only files written by phases 9, 12 and 13, so no number in the revised
manuscript tables or Additional file 4 is typed by hand.

Outputs (output/revision/generated/)
    t1_cognitive_rows.tex      cognitive phenotype rows for Table 1
    t3_contrasts_rows.tex      Table 3, incremental discrimination and margins
    s2_missing_reason.tex      Table S2
    s3_missing_group.tex       Table S3
    s4_three_four.tex          Table S4 (labelled and analytic)
    s5_labelled.tex            Table S5
    s6_pairwise.tex            Table S6, every pairwise contrast
    s7_performance.tex         Table S7, performance including M4
    s8_margins.tex             Table S8, margin analysis for every analysis
    numbers.json               flat key-value list for prose checks

Run:  python3 src/14_revision_tables.py
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
INTERIM = ROOT / "data" / "interim"
TABLES = ROOT / "output" / "tables"
OUT = ROOT / "output" / "revision" / "generated"

NAMES = {"M0": "M0", "M1": "M1", "M2": "M2", "M3": "M3", "M0plus": "M0+", "M4": "M4"}
ALGO = {"logistic": "Logistic", "random_forest": "Random forest", "xgboost": "Gradient boosting"}
TESTS = {"cerad_immediate": "CERAD immediate", "cerad_delayed": "CERAD delayed",
         "animal_fluency": "Animal fluency", "dsst": "DSST"}


def tex(s: str) -> str:
    """Escape the characters that appear in our labels; true minus signs."""
    s = re.sub(r"(?<![\w.])-(\d)", "@@MINUS@@\\1", str(s))
    return (s.replace("\\", "\\textbackslash{}").replace("%", "\\%")
            .replace("&", "\\&").replace("_", "\\_").replace("<=", "$\\le$")
            .replace(">=", "$\\ge$").replace("ug/", "$\\mu$g/")
            .replace("@@MINUS@@", "$-$"))


def num(x: float) -> str:
    """Four decimals; negatives in math mode so they print a true minus sign."""
    return f"${x:.4f}$" if x < 0 else f"{x:.4f}"


def ci(lo: float, hi: float) -> str:
    return f"[{num(lo)}, {num(hi)}]"


def contrast_name(c: str) -> str:
    return c.replace("M0plus", "M0+").replace(" - ", " $-$ ")


def yesno(b) -> str:
    return "yes" if bool(b) else "no"


def write(name: str, body: str) -> None:
    (OUT / name).write_text(body + "\n")
    print(f"  wrote output/revision/generated/{name}")


def t1_cognitive(rev12: dict) -> str:
    lines = ["\\multicolumn{4}{l}{\\textit{Cognitive measures}}\\\\"]
    for r in rev12["table1c"]:
        label = tex(r["characteristic"])
        if label.strip() == "score missing":
            label = "\\quad score missing, $n$ (\\%)"
        elif label.startswith("Outcome cutoff"):
            continue
        lines.append(f"{label} & {tex(r['Overall'])} & "
                     f"{tex(r['Low cognitive performance'])} & "
                     f"{tex(r['Not low cognitive performance'])} \\\\")
    cut = rev12["quartile_cut_z"]
    lines.append(f"Outcome cutoff (lowest quartile of the 3,124 labelled participants) & "
                 f"\\multicolumn{{3}}{{r}}{{composite $z \\le {cut:.3f}$}} \\\\")
    lines.append("\\multicolumn{4}{l}{\\textit{Demographic, laboratory and clinical characteristics}}\\\\")
    return "\n".join(lines)


def t3_contrasts(pw: pd.DataFrame, mg: pd.DataFrame) -> str:
    log = pw[pw.algo == "logistic"].set_index("contrast")
    rows = [("M1 - M0", "Metals added to demographics", "nested"),
            ("M2 - M0", "Nutritional and metabolic biomarkers added to demographics", "nested"),
            ("M3 - M0", "Both biomarker blocks added to demographics (primary)", "nested"),
            ("M0plus - M0", "Clinical covariates added to demographics (post hoc)", "nested"),
            ("M4 - M0plus", "Both biomarker blocks added to the clinical baseline (post hoc)", "nested"),
            ("M0plus - M3", "Clinical baseline against biomarker model (substitutes)", "not nested")]
    out = []
    for key, label, kind in rows:
        r = log.loc[key]
        out.append(f"{label} & {contrast_name(key)} & {num(r.delta_auc)} & "
                   f"{ci(r.ci95_low, r.ci95_high)} & {ci(r.ci90_low, r.ci90_high)} & "
                   f"{yesno(r['equivalence_0.01'])} & {yesno(r['equivalence_0.015'])} & "
                   f"{yesno(r['equivalence_0.02'])} \\\\")
    return "\n".join(out)


def s2(rev12: dict) -> str:
    out = []
    for r in rev12["s2_missing_by_reason"]:
        bold = r["reason"] in ("Total missing", "Score present")
        cells = [str(r[t]) for t in TESTS]
        label = tex(r["reason"])
        if bold:
            label = "\\textit{" + label + "}"
        out.append(label + " & " + " & ".join(cells) + " \\\\")
    return "\n".join(out)


def s3(rev12: dict) -> str:
    out = []
    for r in rev12["s3_missing_by_group"]:
        out.append(f"{tex(r['group'])} & {r['n']} & " +
                   " & ".join(tex(r[t]) for t in TESTS) +
                   f" & {tex(r['fewer_than_3_scores'])} \\\\")
    return "\n".join(out)


def s4(rev12: dict) -> str:
    lab, ana = rev12["s4_three_vs_four"]["labelled"], rev12["s4_three_vs_four"]["analytic"]
    out = []
    for k in lab["Four scores"]:
        out.append(f"{tex(k)} & {tex(lab['Four scores'][k])} & {tex(lab['Three scores'][k])} & "
                   f"{tex(ana['Four scores'][k])} & {tex(ana['Three scores'][k])} \\\\")
    return "\n".join(out)


def s5(rev12: dict) -> str:
    d = rev12["s5_labelled_vs_not"]
    a, b = list(d)
    return "\n".join(f"{tex(k)} & {tex(d[a][k])} & {tex(d[b][k])} \\\\" for k in d[a])


def s6(pw: pd.DataFrame) -> str:
    out = []
    current = None
    algo_rows = pw[pw.algo.str.contains(" vs ")]
    pw = pd.concat([pw[~pw.algo.str.contains(" vs ")],
                    algo_rows.sort_values("algo", kind="stable")])
    for _, r in pw.iterrows():
        group = ALGO.get(r.algo, r.algo.replace("random_forest", "Random forest")
                         .replace("xgboost", "Gradient boosting"))
        if group != current:
            out.append(f"\\multicolumn{{6}}{{l}}{{\\textit{{{tex(group)}}}}}\\\\")
            current = group
        name = r.contrast.replace("random_forest", "random forest").replace("xgboost", "gradient boosting")
        out.append(f"{contrast_name(name)} & {'yes' if r.nested else 'no'} & {num(r.delta_auc)} & "
                   f"{ci(r.ci95_low, r.ci95_high)} & {ci(r.ci90_low, r.ci90_high)} & "
                   f"{yesno(r['ci95_beyond_0.02'])} \\\\")
    return "\n".join(out)


def s7(perf: pd.DataFrame) -> str:
    out = []
    for _, r in perf.iterrows():
        out.append(f"{NAMES[r.spec]} & {ALGO[r.algo]} & {r.auc:.4f} & {r.auprc:.4f} & "
                   f"{r.brier:.4f} & {r.calib_slope:.3f} & {num(r.calib_intercept)} \\\\")
    return "\n".join(out)


def s8(mg: pd.DataFrame) -> str:
    out = []
    for _, r in mg[~mg.analysis.str.startswith("Leave-one-block-out")].iterrows():
        out.append(f"{tex(r.analysis)} ({r.status}) & {contrast_name(r.contrast)} & "
                   f"{int(r.n)} & {int(r.events)} & {num(r.delta_auc)} & "
                   f"{ci(r.ci95_low, r.ci95_high)} & {ci(r.ci90_low, r.ci90_high)} & "
                   f"{r.smallest_margin_excluded_one_sided:.4f} & "
                   f"{r.smallest_equivalence_margin:.4f} \\\\")
    return "\n".join(out)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    rev12 = json.loads((INTERIM / "12_revision_outcome.json").read_text())
    rev13 = json.loads((INTERIM / "13_revision_evaluation.json").read_text())
    pw = pd.read_csv(TABLES / "13_pairwise_delta_auc.csv")
    mg = pd.read_csv(TABLES / "13_margin_analysis.csv")
    perf = pd.read_csv(TABLES / "13_m4_performance.csv")

    write("t1_cognitive_rows.tex", t1_cognitive(rev12))
    write("t3_contrasts_rows.tex", t3_contrasts(pw, mg))
    write("s2_missing_reason.tex", s2(rev12))
    write("s3_missing_group.tex", s3(rev12))
    write("s4_three_four.tex", s4(rev12))
    write("s5_labelled.tex", s5(rev12))
    write("s6_pairwise.tex", s6(pw))
    write("s7_performance.tex", s7(perf))
    write("s8_margins.tex", s8(mg))

    numbers = {"continuous": rev13["continuous_outcome"], "dca": rev13["decision_curve"],
               "norms": rev13["demographic_norms"],
               "demadj_prevalence": rev13["demographic_adjusted_prevalence_locked"],
               "complete_battery": rev13["complete_battery"]}
    for _, r in pw.iterrows():
        numbers[f"pw|{r.algo}|{r.contrast}"] = {k: round(float(r[k]), 4) for k in
                                                ["delta_auc", "ci95_low", "ci95_high",
                                                 "ci90_low", "ci90_high"]}
    for _, r in mg.iterrows():
        numbers[f"mg|{r.analysis}|{r.contrast}"] = {
            k: round(float(r[k]), 4) for k in
            ["delta_auc", "ci95_low", "ci95_high", "ci90_low", "ci90_high",
             "smallest_margin_excluded_one_sided", "smallest_equivalence_margin"]} | {
            "n": int(r.n), "events": int(r.events),
            **{f"ns_{m}": bool(r[f"non_superiority_{m}"]) for m in (0.01, 0.015, 0.02)},
            **{f"eq_{m}": bool(r[f"equivalence_{m}"]) for m in (0.01, 0.015, 0.02)}}
    for _, r in mg.iterrows():
        for k in ("auc_a", "auc_b"):
            if pd.notna(r.get(k)):
                numbers[f"mg|{r.analysis}|{r.contrast}"][k] = round(float(r[k]), 4)
    numbers["desc"] = {
        "t1c": {r["characteristic"].strip(): r for r in rev12["table1c"]},
        "s2": {r["reason"]: r for r in rev12["s2_missing_by_reason"]},
        "s3": {r["group"]: r for r in rev12["s3_missing_by_group"]},
        "s4": rev12["s4_three_vs_four"], "s5": rev12["s5_labelled_vs_not"],
        "cut": rev12["quartile_cut_z"]}
    for _, r in perf.iterrows():
        numbers[f"perf|{r.spec}|{r.algo}"] = {k: float(r[k]) for k in
                                              ["auc", "auprc", "brier", "calib_slope", "calib_intercept"]}
    (OUT / "numbers.json").write_text(json.dumps(numbers, indent=1, default=float))
    print("  wrote output/revision/generated/numbers.json")


if __name__ == "__main__":
    main()
