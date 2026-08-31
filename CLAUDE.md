# Working rules for this repository

You are helping build a reproducible analysis for a peer-reviewed publication.
`PROJECT_BRIEF.md` in this repo is the authoritative spec. Read it fully before
writing any code, and re-read the relevant section at the start of each phase.

---

## The single most important rule

**Never invent a variable name, file name, or codebook value.**

An earlier version of this project was planned around three NHANES files that do not
exist (`HSCRP_G`, `HSCRP_H`) or were mislabeled (`FOLATE_G` described as containing
B12; it contains RBC folate only). That error would have cost weeks.

Therefore:

- Before using any NHANES variable, verify it against the actual file. Load the file
  and print `df.columns.tolist()`. Do not rely on memory or on plausible-sounding
  naming conventions.
- Before interpreting any coded variable, check its codebook range on the CDC
  documentation page for that specific file and cycle.
- If you cannot verify something, say so explicitly and stop. Do not proceed on a
  guess. "I believe this variable is called X" is not acceptable — check.
- If a file or variable turns out to be missing, report it and wait. Do not silently
  substitute an alternative.

---

## Phase gates

Work in the phases defined in `PROJECT_BRIEF.md`. As of 2026-08-30 there are **two
review gates, not seven** (see `VARIABLE_LOCK.md`):

- **Gate 1: the variable list lock.** Cleared 2026-08-30.
- Phases 1 and 2 (cohort, outcome) run consecutively without review.
- **Gate 2: diagnostics review plus the dated pre-registration.** Blocking, and it
  cannot move. The pre-registration must be dated *before* anyone sees an
  outcome-predictor relationship or the pre-specification claim is void, and that
  claim is what TRIPOD+AI reporting and section 6 of the brief both rest on.
  **Do not start modeling because the cleaning "looks done."**
- Phases 3 to 6 (model, evaluate, interpret, sensitivity) run consecutively.

Chaining is permitted only because the guardrails below replace the removed reviews.
If a guardrail is not in place, stop instead of chaining.

**Guardrails that make chaining safe.** Every phase script must hard-fail rather than
warn: row counts after each merge, `SEQN` uniqueness, no reserved code surviving into
a numeric column, no column silently all-missing, weights summing to a plausible
population total. The leakage audit is an automated test that fails the run, not a
review step. Every phase writes to `data/interim/` so a late failure resumes rather
than restarts.

At each gate, report: what you did, what you verified, what you assumed, and what you
could not confirm. Each gate gets one diagnostics document, the way Phase 0 produced
one audit.

---

## Data integrity rules

**Reserved codes.** NHANES uses 7/77/777 for "refused" and 9/99/999 for "don't know",
and the specific codes vary by variable. Convert these to `NaN` before any arithmetic.
Averaging a 9 silently invalidates every downstream result. Verify the applicable
codes per variable against its codebook — do not apply a blanket rule.

**Skip patterns are not missingness.** A blank follow-up because someone answered "no"
upstream is structural. Distinguish the two and document which is which.

**Below detection limit.** NHANES substitutes LOD/sqrt(2) and flags it in a comment
variable. Report the imputed fraction per analyte. Cadmium will have many among
non-smokers.

**Survey weights.** `WTMEC2YR` must be halved when combining two cycles. Carry
`SDMVSTRA` and `SDMVPSU` through every merge. Never drop them.

---

## Modeling rules

**Data leakage is the failure mode that will silently ruin this project.**

Every preprocessing step — imputation, scaling, encoding, feature selection — must be
fitted **inside** each cross-validation fold, on training data only. Use sklearn
`Pipeline` objects inside the CV loop. Never call `.fit()` or `.fit_transform()` on
the full dataset before splitting.

After writing the modeling code, explicitly audit it for leakage and report what you
checked. If any transform touches held-out data, the reported AUCs are fabricated and
will look completely normal. This is not a hypothetical risk.

**Do not select models on accuracy.** Prevalence is ~25%; predicting "normal" for
everyone scores 75%. Use AUC and AUPRC.

**The primary result is delta-AUC against the demographics-only baseline (M0), with
bootstrap confidence intervals.** Not absolute AUC. Compute the deltas explicitly and
present them as the headline numbers.

**Set every random seed.** Pin package versions in `requirements.txt`.

---

## Reporting rules

**This is cross-sectional data.** Never write causal language — no "leads to",
"causes", "improves", "protects against", "reduces risk of". Associations and
predictions only. Flag any causal phrasing you notice in text I write.

**The outcome is "low cognitive performance", never "cognitive impairment".** NHANES
contains no clinical diagnosis. Correct this wherever it appears.

**Report null and negative results plainly.** If biomarkers add nothing beyond
demographics, that is the finding and it is publishable — see section 6 of the brief.
Do not search for a specification that produces a positive result. If you find
yourself trying alternative cutoffs or feature sets after seeing a disappointing
number, stop and say so.

**If gradient boosting does not beat penalized logistic regression, report that.**
It is the expected outcome at this sample size and it is a legitimate finding.

---

## Efficiency rules

- Save intermediate outputs to `data/interim/` after every phase so phases re-run
  independently. Never re-run the merge to fix a modeling bug.
- Do not print raw data into the conversation. Write summaries to disk and read those.
- One numbered script per phase, each independently runnable.
- Keep functions small and testable. This code will be scrutinized by reviewers and
  may need to be published as a supplement.

---

## When you are uncertain

Say so. Stop. Ask. An hour of clarification is cheaper than three weeks of analysis
built on a wrong assumption — and in this project, that has already nearly happened
once.
