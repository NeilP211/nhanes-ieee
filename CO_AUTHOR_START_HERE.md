# Start here, Shreyan

Everything on the data and modelling side is finished, checked and locked. This
file is the entry point: what is done, what is decided, what is still yours, and
where every number lives.

Neil is travelling and will be slow to reply. Nothing below needs him to unblock
it.

---

## Read these three things, in this order

| Order | File | Time | Why |
|---|---|---|---|
| 1 | `WRITING_PACK.pdf` | 20 min | The whole project in 12 pages. Every number, the venue question, a ready-to-edit abstract, the Intro and Discussion skeletons, and a table of likely reviewer objections with the answers we already have. |
| 2 | `output/results_review.html` | 10 min | The full results review as one page. Open it in a browser, no software needed. |
| 3 | `MANUSCRIPT_DRAFT.md` | 20 min | Methods and Results already written in manuscript prose. The last section is a set of notes written specifically for you. |

If you read only one, read the PDF.

---

## The finding, in one sentence

Biomarkers that this literature reports as associated with cognition do not help
identify who has low cognitive performance, once you know a person's age,
education and income.

The precise version: delta-AUC(M3 - M0) = -0.0019, bootstrap 95% CI [-0.0108,
0.0071], n = 1,784, 431 events. The upper bound falls below the 0.02 improvement
we declared meaningful **before** modelling, so we exclude a worthwhile gain
rather than merely failing to detect one.

The most quotable version: a twenty-analyte laboratory panel was outperformed by
eight questions a clinician can ask without drawing blood.

---

## What is locked and cannot change

This is the part worth understanding before you suggest an analysis.

The pre-registration is dated **before** any outcome-predictor relationship was
examined. That date is what lets us say the null is *precise* rather than
*inconclusive*, which is the single strongest sentence in the paper. Adding,
dropping or re-running an analysis now would void that claim, and we would lose
the thing that makes this publishable.

So: every number is final. The variable list, the outcome definition, the four
nested models, the three algorithms, the six sensitivity analyses, the 0.02
threshold. All fixed in writing, all dated, all in `PREREGISTRATION.md` and
`VARIABLE_LOCK.md`.

If something looks wrong or missing, say so and we will discuss it as a
limitation to state in the paper. That is a normal and expected outcome. What we
cannot do is quietly re-run things until a number moves.

---

## What we need from you, in priority order

### 1. Countersign the pre-registration

`PREREGISTRATION.md` section 10 still reads `_pending countersign_` for the
clinical and framing lead. Neil signed 2026-08-31. Please add your name and a
date, commit it, and that is closed.

This takes two minutes and it is the highest-value thing on the list, because
every framing claim in the paper depends on that document being agreed by both
authors.

### 2. Call the venue — DECIDED 2026-09-05: Diagnostic and Prognostic Research

Shreyan and Neil agree: **Diagnostic and Prognostic Research (BMC)** is the
target venue. J Clin Epi is the fallback reach, PLOS ONE the fast fallback if
both reject. IEEE Access was considered and set aside — Scenario E (ML did not
beat penalized logistic) undercuts the computational-contribution case IEEE
reviewers look for, and retrofitting the paper toward an ML framing after
seeing that result would risk shaping the Introduction around the venue
rather than the finding. This closes item 2 below; the Introduction should be
written for a methodological prediction-research audience.

Original argument, kept for the record. Full version on page 2 of the PDF.
Short version:

The result landed as **Scenario C** (null on the primary axis) plus **Scenario
E** (flexible learners did not beat penalized regression). The project brief's
own decision rule routes that combination to a methodological venue:
**Diagnostic and Prognostic Research**, Journal of Clinical Epidemiology, or
PLOS ONE. The brief also says Scenario E "weakens an IEEE framing."

Neil's recommendation is **Diagnostic and Prognostic Research (BMC)**. It is the
only venue the brief rates "Excellent," it exists specifically for
prediction-model studies, it is TRIPOD-native and our completed TRIPOD+AI
checklist is already in `output/`, and the brief argues the clinical route fits
the team we actually have.

The honest counter-argument, so you can weigh it: we did build the two things
the brief said would raise IEEE odds, namely a mixture-method benchmark judged
on predictive rather than inferential criteria, and a bootstrapped rank-stability
analysis. Those are real computational content. What we did not get is Scenario
D, where ML beats logistic, which was the other lever. So IEEE Access is
arguable but is now the harder sell.

**Why you cannot defer this.** Brief section 7, in bold: "IEEE and nutrition
journals want genuinely different papers. The introductions are not
interchangeable. Pick a lane before your co-author starts drafting." Whichever
lane we pick, you are writing a different Introduction.

### 3. The literature review

This is the piece only you can do, and it is the concrete task you can start on
today.

The Introduction rests on one structural claim: this literature is saturated on
association and empty on prediction. We have the shape of the evidence but not
the citations. Here is the table as it stands, from brief section 2:

| Study | n | Exposure | Method | Predictive metrics? |
|---|---|---|---|---|
| Blood metals and cognition, 60+ | 1,460 | 5 metals | Linear regression, RCS | None |
| Iron plus 5 metals, low cognition | 2,002 | 6 elements | Weighted logistic | None |
| Trace elements plus DII | 1,726 | 5 elements | GLM, BKMR, WQS, qg-comp | None |
| Joint metal exposure | 811 | 6 metals | Mixture models | None |
| Sex-specific metal mixtures | not recorded | Metals | Mixture models | None |
| Metals by diet quality | 1,777 | Pb, Cd, Mn | Quantile g-computation | None |
| Cadmium by omega-6 intake | 1,918 | Cd plus FA intake | Logistic | None |

**What we need:** the real citation for each row, verification that the last
column is still "None" for each, and a check on whether anything new has appeared
since the brief was written. If any of them *does* report AUC, calibration or
cross-validation, that is important and changes how we position the paper, so
flag it immediately rather than dropping the row.

Scope note: restrict to NHANES 2011-2014, adults aged 60 and over. Papers on
other cycles or other age ranges are context, not the gap claim.

### 4. ~~Draft the Introduction and Discussion~~

Done 2026-09-05 — see `MANUSCRIPT_DRAFT.md`. Introduction and Discussion
drafted from the skeleton, updated for the DPR framing and the Ren et al.
2025 finding from the literature review; title and structured abstract
added as well (title checked against DPR's own convention, abstract
trimmed to the journal's verified 350-word limit, not the brief's ~360
estimate). The manuscript draft is now complete end to end: title,
abstract, Introduction, Methods, Results, Discussion, references.

Methods and Results are Neil's and were left unchanged.

---

## Language rules, non-negotiable

These held throughout Methods and Results. Breaking them in your sections creates
an inconsistency a reviewer will find.

1. **The outcome is "low cognitive performance", never "cognitive impairment".**
   NHANES contains no clinical diagnosis. This is not style; claiming impairment
   claims a diagnosis we do not have.
2. **No causal verbs anywhere.** The design is cross-sectional. Not "leads to",
   "causes", "improves", "protects against", "reduces risk of".
3. **The null is about prediction, not biology.** Nothing here shows any
   biomarker is unrelated to cognition. The published associations may all be
   correct. Our finding is that they do not translate into identifying *which
   individuals* have low cognitive performance. That distinction is the paper.
4. **Phrase the precision deliberately.** "The interval excludes an improvement
   of the magnitude specified in advance as meaningful" is far stronger than "the
   difference was not statistically significant". Do not weaken it into ordinary
   non-significance language.
5. **Every result says whether it is an association claim or a prediction
   claim.** Survey weights for association, unweighted machine learning for
   prediction. See `PREREGISTRATION.md` section 8.

---

## Where the numbers live

You should never need to run code to write your sections.

| You want | Look at |
|---|---|
| The headline and all contrasts | `output/tables/07_results_summary.md` |
| Everything in one browsable page | `output/results_review.html` |
| Raw result tables | `output/tables/*.csv` |
| Figures, 300 dpi PNG and vector PDF | `output/figures/` |
| What was pre-specified, and when | `PREREGISTRATION.md` |
| The variable list and its amendments | `VARIABLE_LOCK.md` |
| Reporting compliance | `output/TRIPOD_AI_checklist.md` |
| Data traps we hit and fixed | `output/tables/00_availability_audit.md` |

Figures, in order: forest plot of the delta-AUC contrasts; calibration by decile
bins; decision-curve analysis; rank stability across 200 bootstrap resamples;
partial dependence showing no U-shape for either essential metal.

---

## If you do want to run it

Not required. Everything reproduces in under an hour on one machine with no GPU.

```
pip install -r requirements.txt
python3 src/00b_download.py      # fetch 40 NHANES files (54 MB)
python3 src/01_cohort.py
python3 src/02_outcome.py
python3 src/03_model.py          # ~25 min
python3 src/04_evaluate.py
python3 src/05_interpret.py
python3 src/06_sensitivity.py
python3 src/07_figures.py
```

Raw data is not in the repo. `00b_download.py` rebuilds it from CDC URLs.

To rebuild the writing pack PDF: `tectonic -X compile WRITING_PACK.tex` from the
repo root. The fonts are macOS system faces, so on another machine swap the three
`\set*font` lines at the top for anything you have.

---

## Ground rules for the repo

- `CLAUDE.md` is the working spec for this repository. Read it if you touch code.
- Never invent an NHANES variable name. The codebooks document five variables
  that do not exist in the data, and an earlier version of this project was
  planned around three files that were wrong or mislabelled. Load the file and
  print the columns.
- Do not rewrite history. Commit on top.

---

## Open questions for you

1. ~~Countersign the pre-registration, or tell us what needs to change first.~~
   Done 2026-09-05 — see `PREREGISTRATION.md` section 10. (`VARIABLE_LOCK.md`
   countersigned the same day.)
2. ~~DPR, or make the case for IEEE. Either is defensible; we need one.~~
   Decided 2026-09-05 — Diagnostic and Prognostic Research.
3. ~~Anything in the seven-study table that already reports predictive
   metrics.~~ Done 2026-09-05 — see `LITERATURE_REVIEW.md`. All seven rows
   verified, none report predictive metrics. Two new papers found (not in
   the original table): Ren et al. 2025 (same 60+ population, AUC 0.90, no
   demographics-only baseline — gets its own Introduction paragraph) and
   Nabavi et al. 2024 (ages 20+, lower priority). Row 1 of the table is an
   unpublished preprint, cited but flagged as such.
4. Any limitation you think we have understated. Current list (in the
   Discussion): cross-sectional design, mildly non-random complete-case
   sample, age top-coded at 80, no external validation cohort, no subgroup
   fairness audit, serum copper/zinc excluded, outcome defined against
   pooled-sample quantiles.

## Submission decisions, closed 2026-09-05 pending Neil's confirmation

Decided while Neil is travelling; flagged in `MANUSCRIPT_DRAFT.md` for him
to confirm or correct, not presented as unchangeable:

- **Authorship:** Shreyan Kancharla and Neil Patel contribute equally and
  share first authorship.
- **Corresponding author:** Shreyan Kancharla.
- **Competing interests / funding:** none to declare, unfunded.
- **Code availability:** public on submission. **Action needed from
  Neil** — the GitHub repository (`NeilP211/nhanes-ieee`) is currently
  private, and changing visibility requires owner/admin access, which this
  session does not have (write access only). Neil needs to make it public,
  or grant admin access, before submission.

**Title page, updated 2026-09-05:** Shreyan's affiliation (Davidson
College, Davidson, NC) and ORCID (0009-0009-8654-110X, verified against
the public ORCID record) are filled in on the title page and cover letter.
Neil's institution (University of North Carolina at Chapel Hill) is now
filled in too. Still needed: his department/school and ORCID.

## Analysis-side TRIPOD gaps, closed 2026-09-05

The three items `output/TRIPOD_AI_checklist.md` flagged as outstanding
(originally Neil's side of the division of labour, taken over by Shreyan
while Neil travels) are now built, each cross-checked rather than assumed:

- **Participant flow diagram** (item 14a) —
  `output/figures/fig6_participant_flow.png`/`.pdf`. The final step (from
  n=3,124 to the locked n=1,784) was recomputed independently from
  `02_outcome.parquet` and matches `02_analytic_seqn.csv` exactly (0 SEQN
  mismatch).
- **Table 1** (item 14b) — `output/tables/09_table1.md`. Caught and fixed
  two bugs before trusting it: "current smoker" was reading 0.0% because
  the derived smoking variable is categorical, not binary; and several
  rows mixed mean(SD) for one subgroup with median[IQR] for another
  because skewness was computed per-subgroup instead of once per
  variable. Also caught a small stale-number drift in the existing
  Results text (26.2%/24.1% carried over from the pre-lock n=1,789
  sample rather than the final n=1,784) and corrected it to 26.1%/24.2%.
- **Full M3 coefficients** (item 16) — `output/tables/10_m3_coefficients.md`.
  Refit on the complete analytic sample with 2,000-resample bootstrap
  CIs; caught a numerical-stability edge case (non-finite coefficients
  possible at the grid's weakly-regularised end) before trusting the
  CIs, and verified 0 resamples were actually affected.

The pinned Python 3.12.2 environment (system Python was 3.9.6) was set up
via Homebrew to run these against the exact versions in
`requirements.txt`, not mismatched ones.
