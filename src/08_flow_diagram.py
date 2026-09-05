"""
Phase 8 (manuscript support): TRIPOD+AI participant flow diagram, item 14a.

Reproduces the attrition chain already stated in Results and verified
against `output/tables/00_availability_audit.md`, `data/interim/01_attrition.csv`
and `data/interim/02_analytic_seqn.csv`, then extends it one step further
than any existing file: from the outcome-eligible sample (n=3,124) down to
the final locked analytic sample (n=1,784), broken out by reason, computed
fresh from `02_outcome.parquet` rather than copied from the pre-lock Gate 2
diagnostics (which used a provisional n=1,789 before the final variable
list amendment).

Outputs
    data/interim/08_flow_diagram.json
    output/tables/08_flow_diagram.md
    output/figures/fig6_participant_flow.png / .pdf

Run:  python3 src/08_flow_diagram.py
"""
from __future__ import annotations

import json
import textwrap
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
INTERIM = ROOT / "data" / "interim"
TABLES = ROOT / "output" / "tables"
FIGURES = ROOT / "output" / "figures"

# M3's full feature list, used to define "complete predictor data" exactly as
# in 03_model.py's SPECS["M3"], plus the M0plus-only covariates, since the
# locked analytic sample requires every Block 1-3 feature AND every covariate
# (03_model.py line 151: "locked row set has missing features" assertion).
DEMO = ["RIDAGEYR", "RIAGENDR", "RIDRETH3", "DMDEDUC2", "INDFMPIR"]
METALS = ["log_LBXBPB", "log_LBXBCD", "log_LBXTHG", "log_LBXBSE", "log_LBXBMN"]
NUTR = ["log_LBDB12SI", "log_LBXMMASI", "LBDFOT", "LBDRFO", "LBXVIDMS", "LBXGH",
        "LBDHDD", "LBXTC", "LBXSTR", "LBXSAL", "LBXSIR", "egfr", "nlr", "plr",
        "log_sii"]
COVARIATES = ["BMXBMI", "smoking", "drinks_per_day", "phq9", "stroke",
              "diabetes", "hypertension", "high_chol"]
ALL_PREDICTORS = DEMO + METALS + NUTR + COVARIATES


def main() -> None:
    df = pd.read_parquet(INTERIM / "02_outcome.parquet")
    locked_seqn = pd.read_csv(INTERIM / "02_analytic_seqn.csv").SEQN

    assert df.SEQN.is_unique, "SEQN not unique in 02_outcome.parquet"

    eligible = df[df.n_cog_scores >= 3].copy()
    assert len(eligible) == 3124, f"expected 3,124 outcome-eligible, got {len(eligible)}"

    complete = eligible.dropna(subset=ALL_PREDICTORS)
    complete_seqn = set(complete.SEQN)
    locked_set = set(locked_seqn)

    # The locked sample (02_analytic_seqn.csv) is the authority; this
    # independent recomputation from raw predictor completeness should match
    # it exactly, or the discrepancy needs to be understood before reporting
    # either number in the manuscript.
    mismatch = complete_seqn.symmetric_difference(locked_set)
    if mismatch:
        print(f"WARNING: {len(mismatch)} SEQN differ between the recomputed "
              f"complete-predictor set (n={len(complete_seqn)}) and the "
              f"locked 02_analytic_seqn.csv (n={len(locked_set)}). Using the "
              f"locked file as authoritative for all downstream reporting; "
              f"investigate before final submission.")

    n_locked = len(locked_set)
    excluded_after_outcome = eligible[~eligible.SEQN.isin(locked_set)]

    # Reasons for exclusion among the outcome-eligible sample, in the same
    # block order as the nested models (metals first, since that is the
    # dominant driver via the PBCD_H one-half subsample, then nutritional,
    # then covariates).
    missing_metals = eligible[METALS].isna().any(axis=1)
    missing_nutr = eligible[NUTR].isna().any(axis=1)
    missing_covar = eligible[COVARIATES].isna().any(axis=1)
    missing_demo = eligible[DEMO].isna().any(axis=1)

    reasons = {
        "missing_any_demographic": int(missing_demo.sum()),
        "missing_any_metal": int(missing_metals.sum()),
        "missing_any_nutritional_biomarker": int(missing_nutr.sum()),
        "missing_any_covariate": int(missing_covar.sum()),
        # Not mutually exclusive -- a participant can be missing more than
        # one block. Reported as an overlap note, not summed.
        "note": "categories overlap; a participant may be missing more than one block"
    }

    stages = [
        {"stage": "Examined in NHANES 2011-2012 or 2013-2014, all ages", "n": 19931,
         "source": "output/tables/00_availability_audit.md"},
        {"stage": "Aged 60 years or older", "n": 3632,
         "source": "output/tables/00_availability_audit.md"},
        {"stage": "Completed the Mobile Examination Centre visit (RIDSTATR==2)",
         "n": 3472, "source": "data/interim/01_attrition.csv"},
        {"stage": "Received an outcome label (>=3 of 4 cognitive scores)",
         "n": 3124, "source": "data/interim/02_outcome_report.json"},
        {"stage": "Complete data on all Block 1-3 predictors and covariates "
                  "(final locked analytic sample)",
         "n": n_locked, "source": "data/interim/02_analytic_seqn.csv"},
    ]
    for a, b in zip(stages, stages[1:]):
        b["excluded"] = a["n"] - b["n"]

    result = {
        "stages": stages,
        "exclusion_reasons_at_final_step": reasons,
        "cross_check": {
            "recomputed_complete_predictor_n": len(complete_seqn),
            "locked_file_n": len(locked_set),
            "mismatch_n": len(mismatch),
        },
    }
    (INTERIM / "08_flow_diagram.json").write_text(json.dumps(result, indent=1))

    # --- Markdown table -----------------------------------------------
    lines = ["# Participant flow diagram, data", "",
             "**TRIPOD+AI item 14a.** Underlying data for the flow diagram "
             "figure (`output/figures/fig6_participant_flow.png`). Every "
             "stage traces to the source file listed.", "",
             "| Stage | n | Excluded at this step | Source |",
             "|---|---|---|---|"]
    for s in stages:
        excl = s.get("excluded", "—")
        lines.append(f"| {s['stage']} | {s['n']:,} | "
                      f"{excl if excl == '—' else f'{excl:,}'} | `{s['source']}` |")
    lines += ["", "## Reasons for exclusion at the final step "
              f"(n={3124 - n_locked:,} dropped from the outcome-eligible "
              "sample)", "",
              "Not mutually exclusive; a participant can be missing more "
              "than one block, so these do not sum to the total excluded.",
              "",
              "| Missing block | n of the 3,124 outcome-eligible "
              "participants |",
              "|---|---|",
              f"| Any demographic (Block 1) | {reasons['missing_any_demographic']:,} |",
              f"| Any blood metal (Block 2) | {reasons['missing_any_metal']:,} |",
              f"| Any nutritional/metabolic biomarker (Block 3) | "
              f"{reasons['missing_any_nutritional_biomarker']:,} |",
              f"| Any clinical covariate (M0+ block) | "
              f"{reasons['missing_any_covariate']:,} |",
              "",
              f"Cross-check: an independent recomputation of \"complete data "
              f"on all predictors\" from `02_outcome.parquet` found "
              f"{len(complete_seqn):,} participants, against "
              f"{len(locked_set):,} in the locked "
              f"`02_analytic_seqn.csv` ({len(mismatch)} SEQN differ). "
              + ("This matches exactly." if not mismatch else
                 "**This does not match exactly -- investigate before "
                 "submission; the locked file is used as authoritative "
                 "throughout the manuscript.**")]
    (TABLES / "08_flow_diagram.md").write_text("\n".join(lines) + "\n")

    # --- Figure ---------------------------------------------------------
    # Manually wrapped text (matplotlib's own `wrap=True` does not respect
    # a fixed box width, so long labels were overflowing the boxes in an
    # earlier version of this figure). Box width is fixed in inches and the
    # wrap width in characters is chosen to match it at this font size.
    n_stages = len(stages)
    box_w_in, box_h_in, gap_in = 5.6, 0.95, 0.55
    title_h_in = 0.5
    fig_w = 7.2
    fig_h = 0.4 + title_h_in + n_stages * box_h_in + (n_stages - 1) * gap_in

    wrap_chars = 46

    fig, ax = plt.subplots(figsize=(fig_w, fig_h))
    ax.set_position([0, 0, 1, 1])  # axes fill the whole figure; no default
                                    # subplot margin reserved for a title
    ax.axis("off")
    ax.set_xlim(0, fig_w)
    ax.set_ylim(0, fig_h)
    ax.text(fig_w / 2, fig_h - title_h_in / 2,
            "Participant flow, NHANES 2011-2012 and 2013-2014",
            ha="center", va="center", fontsize=12)

    box_x0 = 0.7
    y_top = fig_h - title_h_in - 0.35
    centers = []
    for i, s in enumerate(stages):
        y0 = y_top - i * (box_h_in + gap_in) - box_h_in
        centers.append(y0 + box_h_in / 2)
        ax.add_patch(plt.Rectangle((box_x0, y0), box_w_in, box_h_in,
                                    fill=False, edgecolor="black", linewidth=1.1))
        wrapped = textwrap.fill(s["stage"], wrap_chars)
        label = f"{wrapped}\nn = {s['n']:,}"
        ax.text(box_x0 + box_w_in / 2, y0 + box_h_in / 2, label,
                ha="center", va="center", fontsize=8.8, linespacing=1.4)

    for i in range(1, len(stages)):
        y_prev_bottom = centers[i - 1] - box_h_in / 2
        y_this_top = centers[i] + box_h_in / 2
        x_arrow = box_x0 + box_w_in / 2
        ax.annotate("", xy=(x_arrow, y_this_top), xytext=(x_arrow, y_prev_bottom),
                    arrowprops=dict(arrowstyle="->", lw=1.1))
        excl = stages[i]["excluded"]
        ax.text(box_x0 + box_w_in + 0.15, (y_prev_bottom + y_this_top) / 2,
                f"excluded\nn = {excl:,}", fontsize=7.6, ha="left",
                va="center", color="dimgray", linespacing=1.3)

    fig.savefig(FIGURES / "fig6_participant_flow.png", dpi=300, bbox_inches="tight")
    fig.savefig(FIGURES / "fig6_participant_flow.pdf", bbox_inches="tight")
    plt.close(fig)

    print("stages:")
    for s in stages:
        print(f"  {s['n']:>6,}  {s['stage']}")
    print(f"\ncross-check mismatch: {len(mismatch)} SEQN")
    print("\nwrote data/interim/08_flow_diagram.json, "
          "output/tables/08_flow_diagram.md, "
          "output/figures/fig6_participant_flow.png/.pdf")


if __name__ == "__main__":
    main()
