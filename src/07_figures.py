"""
Phase 7: the manuscript figure set.

Renders every figure from the tables written by phases 4 to 6. Computes no
new statistics: if a number appears here it was produced upstream, so the
figures cannot drift from the reported results.

Palette is colorblind-safe and was validated before use (OKLab CVD separation,
chroma floor, lightness band, contrast against the surface). Colors are
assigned to models in fixed order and never cycled, so a model keeps its color
across every figure.

Outputs, each as PNG at 300 dpi for review and PDF vector for submission
    output/figures/fig1_delta_auc_forest.*
    output/figures/fig2_calibration.*
    output/figures/fig3_decision_curve.*
    output/figures/fig4_shap_rank_stability.*
    output/figures/fig5_partial_dependence.*

Run:  python3 src/07_figures.py
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib as mpl
import numpy as np
import pandas as pd

mpl.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
INTERIM = ROOT / "data" / "interim"
TABLES = ROOT / "output" / "tables"
FIGS = ROOT / "output" / "figures"

# Validated categorical palette, fixed order. Model identity, never rank.
TEAL, BRICK, PURPLE = "#0E8F80", "#B03A26", "#6E5B9E"
MODEL_COLOR = {"M0": TEAL, "M3": BRICK, "M0plus": PURPLE}
INK, INK2, INK3, RULE = "#15201E", "#44514E", "#6D7A77", "#D2DAD8"
THRESHOLD = 0.02

mpl.rcParams.update({
    "figure.dpi": 110, "savefig.dpi": 300, "savefig.bbox": "tight",
    "font.family": "sans-serif",
    "font.sans-serif": ["Helvetica Neue", "Helvetica", "Arial", "DejaVu Sans"],
    "font.size": 9, "axes.labelsize": 9.5, "axes.titlesize": 10.5,
    "axes.titleweight": "600", "axes.edgecolor": INK3, "axes.linewidth": 0.8,
    "axes.labelcolor": INK2, "text.color": INK,
    "xtick.color": INK3, "ytick.color": INK3,
    "xtick.labelsize": 8.5, "ytick.labelsize": 8.5,
    "legend.frameon": False, "legend.fontsize": 8.5,
    "axes.spines.top": False, "axes.spines.right": False,
    "grid.color": RULE, "grid.linewidth": 0.6,
})


def save(fig, name: str) -> None:
    FIGS.mkdir(parents=True, exist_ok=True)
    for ext in ("png", "pdf"):
        fig.savefig(FIGS / f"{name}.{ext}", facecolor="white")
    plt.close(fig)
    print(f"  wrote output/figures/{name}.png and .pdf")


def fig1_forest() -> None:
    """Delta-AUC with 95% (thin) and 90% (thick) bootstrap CIs.

    Revised at peer review: reads the phase 13 tables, adds the nested M4 - M0+
    contrast and the two post hoc sensitivity analyses, and draws the 0.01,
    0.015 and 0.02 margins on both sides of zero so the reader can apply any of
    them, in either direction. Run phase 13 before this figure.
    """
    pw = pd.read_csv(TABLES / "13_pairwise_delta_auc.csv")
    mg = pd.read_csv(TABLES / "13_margin_analysis.csv").set_index("analysis")
    log = pw[pw.algo == "logistic"].set_index("contrast")
    cols = ["delta_auc", "ci95_low", "ci95_high", "ci90_low", "ci90_high"]

    rows = [("Biomarkers added (nested)", None)]
    rows += [(lab, log.loc[key, cols].to_numpy(float)) for lab, key in [
        ("M1 - M0    metals", "M1 - M0"), ("M2 - M0    nutritional", "M2 - M0"),
        ("M3 - M0    both blocks, primary", "M3 - M0"),
        ("M4 - M0+   both blocks, clinical baseline *", "M4 - M0plus")]]
    rows += [("Clinical covariates", None)]
    rows += [(lab, log.loc[key, cols].to_numpy(float)) for lab, key in [
        ("M0+ - M0   added to demographics *", "M0plus - M0"),
        ("M0+ - M3   substitutes, not nested", "M0plus - M3")]]
    rows += [("Sensitivity analyses, M3 - M0", None)]
    rows += [(lab, mg.loc[key, cols].to_numpy(float)) for lab, key in [
        ("20th percentile cutoff", "20th percentile cutoff"),
        ("10th percentile cutoff", "10th percentile cutoff"),
        ("DSST not completed coded low", "DSST not completed coded low"),
        ("English-language administration", "English-language administration only"),
        ("Multiple imputation, n = 3,124", "Multiple imputation, full labelled sample")]]
    for lab, key in [("Complete battery, 4 of 4 scores *", "Complete cognitive battery (4 of 4 scores)"),
                     ("Demographically adjusted outcome *",
                      "Demographically adjusted outcome (internal norms)")]:
        sub = pd.read_csv(TABLES / "13_margin_analysis.csv")
        r = sub[(sub.analysis == key) & (sub.contrast == "M3 - M0")].iloc[0]
        rows.append((lab, r[cols].to_numpy(float)))

    fig, ax = plt.subplots(figsize=(8.6, 6.6))
    ticks, labels = [], []
    y = len(rows)
    xmin, xmax = -0.03, 0.07
    lab_x = ax.get_yaxis_transform()
    for name, vals in rows:
        if vals is None:
            ax.text(-0.012, y, name, va="center", ha="right", fontsize=9,
                    fontweight="600", color=INK, transform=lab_x, clip_on=False)
            y -= 1
            continue
        est, lo95, hi95, lo90, hi90 = vals
        c = BRICK if (lo95 > 0 or hi95 < 0) else TEAL
        primary = "primary" in name
        ax.plot([lo95, hi95], [y, y], color=c, lw=1.3, solid_capstyle="butt", zorder=3)
        for v in (lo95, hi95):
            ax.plot([v, v], [y - 0.14, y + 0.14], color=c, lw=1.3, zorder=3)
        ax.plot([lo90, hi90], [y, y], color=c, lw=4.2, solid_capstyle="butt",
                alpha=0.55, zorder=3)
        ax.plot([est], [y], "o", ms=7.5 if primary else 6, color=c, mec="white",
                mew=1.3, zorder=4)
        ax.text(xmax + 0.012, y, f"{est:+.4f}", va="center", ha="right", fontsize=8,
                family="monospace", color=INK if primary else INK2, clip_on=False)
        ticks.append(y)
        labels.append(name)
        y -= 1

    for m, ls, lw in [(0.01, (0, (1, 2)), 0.9), (0.015, (0, (2, 2)), 0.9),
                      (0.02, (0, (4, 3)), 1.1)]:
        for sgn in (-1, 1):
            ax.axvline(sgn * m, color="#9A5A0B", lw=lw, ls=ls, zorder=2, alpha=0.8)
        ax.text(m, len(rows) + 0.7, f"{m:g}", fontsize=7, color="#9A5A0B",
                ha="center", va="center")
        ax.text(-m, len(rows) + 0.7, f"-{m:g}", fontsize=7, color="#9A5A0B",
                ha="center", va="center")
    ax.axvline(0, color=INK3, lw=1.1, zorder=1)
    ax.text(xmax + 0.012, len(rows) + 0.7, "delta-AUC", fontsize=7.5, color=INK3,
            va="center", ha="right", clip_on=False)

    ax.set_yticks(ticks)
    ax.set_yticklabels(labels, fontsize=8.3, color=INK2)
    ax.set_ylim(0.3, len(rows) + 1.2)
    ax.set_xlim(xmin, xmax)
    ax.set_xlabel("delta-AUC (point, thick bar 90% CI, thin bar 95% CI)")
    ax.spines["left"].set_visible(False)
    ax.tick_params(axis="y", length=0)
    ax.grid(axis="x", zorder=0)
    ax.set_axisbelow(True)

    handles = [plt.Line2D([], [], color=TEAL, lw=2, marker="o", ms=6, mec="white",
                          label="95% CI includes zero"),
               plt.Line2D([], [], color=BRICK, lw=2, marker="o", ms=6, mec="white",
                          label="95% CI excludes zero"),
               plt.Line2D([], [], color="#9A5A0B", lw=1, ls=(0, (4, 3)),
                          label="candidate margins 0.01, 0.015, 0.02")]
    ax.legend(handles=handles, loc="upper left", bbox_to_anchor=(-0.02, -0.09), ncol=3,
              fontsize=7.8)
    ax.text(0.0, -0.2, "* post hoc, added at peer review", fontsize=7.5, color=INK3,
            transform=ax.transAxes, clip_on=False)
    save(fig, "fig1_delta_auc_forest")


def fig2_calibration() -> None:
    """Observed against predicted risk, decile bins, with the diagonal."""
    p = pd.read_parquet(INTERIM / "03_oof_predictions.parquet")
    perf = pd.read_csv(TABLES / "04_performance.csv")
    y = p["y"].to_numpy()

    fig, ax = plt.subplots(figsize=(4.6, 4.5))
    ax.plot([0, 0.85], [0, 0.85], color=INK3, lw=1, ls=(0, (3, 3)), zorder=1,
            label="perfect calibration")
    for spec, name in [("M0", "M0, demographics"), ("M3", "M3, all biomarkers"),
                       ("M0plus", "M0+, clinical baseline")]:
        pred = p[[f"{spec}__logistic__r{r}" for r in range(5)]].to_numpy().mean(axis=1)
        q = pd.qcut(pred, 10, labels=False, duplicates="drop")
        xs = [pred[q == i].mean() for i in range(q.max() + 1)]
        ys = [y[q == i].mean() for i in range(q.max() + 1)]
        row = perf[(perf.spec == spec) & (perf.algo == "logistic")].iloc[0]
        ax.plot(xs, ys, "-o", color=MODEL_COLOR[spec], lw=2, ms=5.5, mec="white",
                mew=1.2, zorder=3,
                label=f"{name}  (slope {row.calib_slope:.2f})")
    ax.set_xlabel("Predicted probability")
    ax.set_ylabel("Observed proportion")
    ax.set_title("Calibration, out-of-fold, decile bins", loc="left", pad=10)
    ax.set_xlim(0, 0.85)
    ax.set_ylim(0, 0.85)
    ax.set_aspect("equal")
    ax.grid(True)
    ax.set_axisbelow(True)
    ax.legend(loc="upper left")
    save(fig, "fig2_calibration")


def fig3_decision_curve() -> None:
    """Net benefit against threshold probability."""
    d = pd.read_csv(TABLES / "04_decision_curve.csv")
    fig, ax = plt.subplots(figsize=(6.4, 4.2))
    ax.plot(d.threshold, d.treat_all, color=INK3, lw=1.2, ls=(0, (4, 3)),
            label="screen everyone", zorder=2)
    ax.axhline(0, color=INK3, lw=1.2, ls=(0, (1, 2)), label="screen no one", zorder=2)
    for spec, name in [("M0", "M0, demographics"), ("M3", "M3, all biomarkers"),
                       ("M0plus", "M0+, clinical baseline")]:
        ax.plot(d.threshold, d[spec], color=MODEL_COLOR[spec], lw=2, label=name, zorder=3)
    ax.set_xlabel("Threshold probability")
    ax.set_ylabel("Net benefit")
    ax.set_title("Decision-curve analysis", loc="left", pad=10)
    ax.set_xlim(0.05, 0.6)
    ax.set_ylim(-0.06, 0.22)
    ax.grid(True)
    ax.set_axisbelow(True)
    ax.legend(loc="upper right")
    n_better = int((d.M3 > d.M0).sum())
    ax.text(0.35, -0.045, f"M3 exceeds M0 at {n_better} of {len(d)} thresholds\n"
            f"maximum gain {(d.M3 - d.M0).max():+.4f}", fontsize=7.5, color=INK3)
    save(fig, "fig3_decision_curve")


def fig4_shap() -> None:
    """Bootstrapped SHAP rank intervals. Demographics are stable, biomarkers are not."""
    s = pd.read_csv(TABLES / "05_shap_ranking.csv").head(14).iloc[::-1]
    pretty = {"DMDEDUC2": "Education", "RIDAGEYR": "Age", "INDFMPIR": "Income/poverty",
              "RIAGENDR": "Sex", "RIDRETH3": "Race and ethnicity", "nlr": "NLR",
              "plr": "PLR", "log_sii": "SII (log)", "egfr": "eGFR",
              "LBDHDD": "HDL cholesterol", "LBXTC": "Total cholesterol",
              "LBXGH": "HbA1c", "LBXVIDMS": "Vitamin D", "LBXSAL": "Albumin",
              "LBXSIR": "Serum iron", "LBXSTR": "Triglycerides",
              "LBDFOT": "Serum folate", "LBDRFO": "RBC folate",
              "log_LBDB12SI": "Vitamin B12 (log)", "log_LBXMMASI": "MMA (log)",
              "log_LBXBPB": "Lead (log)", "log_LBXBCD": "Cadmium (log)",
              "log_LBXTHG": "Mercury (log)", "log_LBXBSE": "Selenium (log)",
              "log_LBXBMN": "Manganese (log)"}
    demo = {"DMDEDUC2", "RIDAGEYR", "INDFMPIR", "RIAGENDR", "RIDRETH3"}

    fig, ax = plt.subplots(figsize=(7.4, 5.0))
    for i, (_, r) in enumerate(s.iterrows()):
        is_demo = r.feature in demo
        c = PURPLE if is_demo else TEAL
        ax.plot([r["rank_p2.5"], r["rank_p97.5"]], [i, i], color=c, lw=2,
                solid_capstyle="round", alpha=0.85, zorder=3)
        ax.plot([r.median_rank], [i], "o", ms=7, color=c, mec="white", mew=1.3, zorder=4)
        ax.text(28.6, i, f"{r['pct_in_top5']:.0f}%", va="center", ha="right",
                fontsize=7.5, family="monospace", clip_on=False,
                color=INK if is_demo else INK3)
    ax.set_yticks(range(len(s)))
    ax.set_yticklabels([pretty.get(f, f) for f in s.feature], fontsize=8.5, color=INK2)
    ax.set_xlabel("SHAP importance rank  (point = median, bar = 95% interval)")
    ax.set_title("Rank stability across 200 bootstrap resamples",
                 loc="left", pad=16)
    ax.text(28.6, len(s) - 0.25, "in top 5", fontsize=7.5, ha="right",
            color=INK3, clip_on=False)
    ax.set_xlim(0, 25.5)
    ax.set_ylim(-0.8, len(s) - 0.1)
    ax.spines["left"].set_visible(False)
    ax.tick_params(axis="y", length=0)
    ax.grid(axis="x")
    ax.set_axisbelow(True)
    handles = [plt.Line2D([], [], color=PURPLE, lw=2, marker="o", ms=7, mec="white",
                          label="demographic"),
               plt.Line2D([], [], color=TEAL, lw=2, marker="o", ms=7, mec="white",
                          label="biomarker")]
    ax.legend(handles=handles, loc="upper center", ncol=2,
              bbox_to_anchor=(0.5, -0.115))
    save(fig, "fig4_shap_rank_stability")


def fig5_pdp() -> None:
    """Partial dependence for selenium and manganese, the U-shape test."""
    d = pd.read_csv(TABLES / "05_partial_dependence.csv")
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.4), sharey=True)
    for ax, (name, unit) in zip(axes, [("selenium", "Blood selenium (ug/L)"),
                                       ("manganese", "Blood manganese (ug/L)")]):
        sub = d[d.feature == name]
        ax.plot(sub.value, sub.predicted_prob, color=TEAL, lw=2, zorder=3)
        ax.set_xlabel(unit)
        ax.set_title(name.capitalize(), loc="left", pad=8)
        ax.grid(True)
        ax.set_axisbelow(True)
        rng = sub.predicted_prob.max() - sub.predicted_prob.min()
        ax.text(0.97, 0.95, f"range {rng:.3f}", transform=ax.transAxes,
                ha="right", va="top", fontsize=7.5, color=INK3)
    axes[0].set_ylabel("Predicted probability of\nlow cognitive performance")
    fig.suptitle("No U-shaped exposure-response is present for either essential metal",
                 x=0.008, ha="left", fontsize=10.5, fontweight="600", y=1.04)
    save(fig, "fig5_partial_dependence")


def main() -> None:
    print("rendering manuscript figures")
    fig1_forest()
    fig2_calibration()
    fig3_decision_curve()
    fig4_shap()
    fig5_pdp()
    meta = {"palette": {"teal": TEAL, "brick": BRICK, "purple": PURPLE},
            "palette_validated": "OKLab CVD separation, chroma floor, "
                                 "lightness band, contrast vs surface",
            "model_colors": MODEL_COLOR,
            "figures": sorted(p.name for p in FIGS.glob("*.png"))}
    (INTERIM / "07_figures.json").write_text(json.dumps(meta, indent=1))
    print(f"\n{len(meta['figures'])} figures in output/figures/ (PNG at 300 dpi + PDF vector)")


if __name__ == "__main__":
    main()
