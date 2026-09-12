# Cover letter

Addressed to the Editor-in-Chief, *Diagnostic and Prognostic Research*. No
specific editor name is known to either author, so the letter stays
addressed generically to the Editor-in-Chief — confirmed 2026-09-12.

---

2026-09-12

Dear Editor,

We submit our manuscript, "Reported biomarker-cognition associations do not
translate into predictive utility: a pre-registered analysis of NHANES
2011-2014," for consideration as a research article in *Diagnostic and
Prognostic Research*.

At least seven published studies report statistically significant
associations between blood metals, nutritional biomarkers, and cognitive
performance among US adults aged 60 and over in the NHANES 2011-2014
cycles. Every one reports a regression coefficient or an odds ratio; none
reports discrimination, calibration, or cross-validated predictive
performance, and none benchmarks a biomarker panel against what is already
known from demographics alone. We close that gap using the same data and
population. Four nested models (demographics; demographics plus blood
metals; demographics plus nutritional biomarkers; both blocks) were
evaluated by repeated stratified cross-validation, with a pre-registered
primary metric — the change in cross-validated AUC when the biomarker panel
is added to demographics — and a meaningful-difference threshold fixed
before any outcome-predictor relationship was examined.

The result is a precise null. The confidence interval for the primary
contrast excludes the improvement specified in advance as meaningful, which
lets us report that biomarkers are ruled out as conferring a worthwhile
predictive gain, rather than merely that we failed to detect one. A
sharper, more concrete finding follows from a pre-specified secondary
comparison: the full twenty-analyte panel performed significantly worse
than a baseline of demographics plus eight items of routine clinical
history, consistently across three algorithms. We also show that quantile
g-computation — the mixture-modelling method most commonly used in this
literature — confers no predictive advantage over demographics alone when
evaluated on predictive rather than inferential criteria, and that
single-run SHAP rankings over these correlated biomarkers are not
reproducible across bootstrap resamples.

We believe this manuscript is well suited to *Diagnostic and Prognostic
Research* specifically because the journal's remit is the evaluation of
prediction models rather than novel exposures or algorithms — the
contribution here is the question, the evaluation framework, and TRIPOD+AI
reporting, applied to a literature that has so far reported associations
only. We disclose this candidly in the manuscript. A pre-registered,
precise null is, we think, exactly the kind of methodologically rigorous
negative result the journal exists to publish, and we report it as such
rather than reframing it toward a more favourable-sounding claim.

The manuscript is reported in full against the TRIPOD+AI checklist
(supplementary file). All hypotheses, the primary metric, the
meaningful-difference threshold, and every sensitivity analysis were fixed
in writing, dated, before any outcome-predictor relationship was examined;
the pre-registration document is available as a supplementary file and, on
request, the dated record of its timing.

One reference we want to flag rather than have you find unannounced:
reference 1 (Wang et al.) is a Research Square preprint, not yet peer
reviewed, and is labelled as such both in the reference list and at its
first citation in the Background. We understand your submission
guidelines restrict citable references to articles, clinical trial
registration records and abstracts that have been published or are in
press, and we are glad to remove or reposition this citation if your
editorial policy does not permit preprints — we kept it because it is,
to our knowledge, the only report of blood-metal associations with
cognition in this specific population and cycle range beyond the six
peer-reviewed studies also cited, and dropping it silently seemed worse
than flagging it for your judgment.

This manuscript is not under consideration elsewhere. The authors declare
no competing interests, and this research received no specific funding
(confirmed by both authors 2026-09-12 — see the Declarations section of
the manuscript). We look forward to your consideration and are happy to
suggest reviewers if useful.

Sincerely,

**Shreyan Kancharla**, corresponding author
Davidson College, Davidson, NC, USA
shkancharla@davidson.edu
ORCID: 0009-0009-8654-110X
on behalf of the authors: Shreyan Kancharla and Neil Patel, who contributed
equally to this work and share first authorship.

---

## Notes for the authors, not part of the letter

- Springer/BMC-family journals submit via Editorial Manager or Snapshot;
  the cover letter is typically pasted into a text box or uploaded as a
  separate file — check the specific prompt at submission.
- Suggested reviewers are optional at DPR but can be entered at submission
  if you want to propose any; opposed reviewers can also be listed with
  reasons if there is a conflict to flag.
- Keep this letter's claims consistent with whatever the Declarations
  section in `MANUSCRIPT_DRAFT.md` ends up saying once funding and
  competing interests are finalised — the two should never disagree.
