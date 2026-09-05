# Variable list lock

**Locked 2026-08-30.** Supersedes the file and variable specifications in
`PROJECT_BRIEF.md` sections 3 and 10 wherever the two disagree.

Decisions recorded by Neil Patel (data and modeling lead) at the close of Phase 0.
Co-author sign-off line is at the bottom and is still open.

Changing anything in this document after Phase 1 begins requires re-running the
merge and every downstream phase. That is the most expensive avoidable event in
the project. Raise objections now.

---

## Decisions taken

| # | Question | Decision | Consequence |
|---|---|---|---|
| 1 | `CUSEZN` (serum Cu, Se, Zn), one-third subsample in both cycles | **Drop** | Lose serum copper and zinc. Selenium is retained via whole-blood `LBXBSE` in Block 2. Analytic n preserved at roughly 2,100 rather than falling to roughly 700. |
| 2 | `TRIGLY` (triglycerides, LDL), fasting subsample in both cycles | **Drop, take triglycerides from `BIOPRO`** | Lose LDL only. `LBXSTR` in `BIOPRO` supplies triglycerides on the full sample. Total cholesterol and HDL were already full-sample. |
| 3 | Diabetes covariate, absent from `MCQ` | **Add `DIQ_G` / `DIQ_H`** | 23rd file. `DIQ010` gives self-reported diagnosis, distinct from `LBXGH` (HbA1c) which we already hold. |

## Process decision

Phase gates reduced from seven to two, per agreement 2026-08-30:

- **Gate 1**: variable list lock (this document). Cleared.
- Phases 1 and 2 run consecutively without review.
- **Gate 2**: diagnostics review plus dated pre-registration, before any modeling.
- Phases 3 to 6 run consecutively without review.

`CLAUDE.md` updated to match.

---

## Locked file list, 21 files

Both cycles required for every file. `_G` = 2011-2012, `_H` = 2013-2014.

| File | Block | Purpose |
|---|---|---|
| `DEMO` | Design + Block 1 | Demographics, survey weights, variance units |
| `CFQ` | Outcome | Cognitive tests |
| `PBCD` | Block 2 | Blood metals |
| `VITB12` | Block 3 | Serum B12 |
| `MMA` | Block 3 | Methylmalonic acid |
| `FOLFMS` | Block 3 | Serum folate |
| `FOLATE` | Block 3 | RBC folate |
| `VID` | Block 3 | Vitamin D |
| `CBC` | Block 3 | Inflammation indices |
| `BIOPRO` | Block 3 | Albumin, creatinine, triglycerides |
| `GHB` | Block 3 | HbA1c |
| `HDL` | Block 3 | HDL cholesterol |
| `TCHOL` | Block 3 | Total cholesterol |
| `BMX` | Covariate | BMI |
| `SMQ` | Covariate | Smoking |
| `ALQ` | Covariate | Alcohol |
| `MCQ` | Covariate | Stroke |
| `DIQ` | Covariate | Diabetes |
| `DPQ` | Covariate | PHQ-9 |
| `BPQ` | Covariate | Hypertension, cholesterol history |

**Excluded and why.** `CUSEZN` and `TRIGLY` per decisions 1 and 2.
`IHGEM` (mercury speciation) was optional in the brief and is a subsample in `_H`;
excluded to avoid compounding the `PBCD_H` loss. `UHM` (urine metals), `FAS`
(serum fatty acids), `PAXMIN` (accelerometer), CRP, homocysteine, ferritin per
the brief.

---

## Locked variable list

### Survey design, from `DEMO`

`SEQN`, `WTMEC2YR` (halve when pooling), `SDMVSTRA`, `SDMVPSU`, `SDDSRVYR`, `RIDSTATR`

Zero MEC weights are stored as 5.397605e-79, not 0. Filter the cohort on
`RIDSTATR == 2`, never on the weight.

### Block 1, demographics, the M0 baseline

`RIDAGEYR` (top-coded at 80), `RIAGENDR`, `RIDRETH3`, `DMDEDUC2`, `INDFMPIR`

### Outcome, from `CFQ`

Scores: `CFDCST1`, `CFDCST2`, `CFDCST3` (sum to CERAD immediate, 0 to 30),
`CFDCSR`, `CFDAST`, `CFDDS`

Support: `CFASTAT`, `CFALANG`, `CFDCCS`, `CFDCRNC`, `CFDARNC`, `CFDDRNC`

These score variables carry **no reserved codes**. `CFDCST1` ranges 0 to 10, so
7 and 9 are valid scores. Do not apply a blanket recode here.

### Block 2, blood metals, from `PBCD`

Concentrations: `LBXBPB`, `LBXBCD`, `LBXTHG`, `LBXBSE`, `LBXBMN`

Detection flags: `LBDBPBLC`, `LBDBCDLC`, `LBDTHGLC`, `LBDBSELC`, `LBDBMNLC`

Weight: `WTSH2YR`, present in `_H` only. Its existence is why the 2013-2014
metals count is 806 rather than roughly 1,600.

### Block 3, nutritional biomarkers

| Variable | File | Note |
|---|---|---|
| `LBXB12` (`_G`) / `LBDB12` (`_H`) | `VITB12` | Renamed across cycles. Prefer `LBDB12SI`, identical name in both |
| `LBXMMASI` | `MMA` | SI units only, no conventional-unit variable exists |
| `LBDFOT` | `FOLFMS` | Serum total folate |
| `LBDRFO` | `FOLATE` | RBC folate |
| `LBXVIDMS` | `VID` | 25OHD2 + 25OHD3 |
| `LBXWBCSI`, `LBDNENO`, `LBDLYMNO`, `LBDMONO`, `LBXPLTSI` | `CBC` | For NLR, PLR, SII |
| `LBXSAL`, `LBXSCR`, `LBXSTR` | `BIOPRO` | Albumin, creatinine for eGFR, triglycerides |
| `LBXGH` | `GHB` | HbA1c |
| `LBDHDD` | `HDL` | Direct HDL |
| `LBXTC` | `TCHOL` | Total cholesterol |

### Covariates

| Variable | File | Note |
|---|---|---|
| `BMXBMI` | `BMX` | |
| `SMQ020`, `SMQ040` | `SMQ` | Smoked 100+, current smoking |
| `ALQ101`, `ALQ120Q`, `ALQ130` | `ALQ` | Drinking history, frequency, average drinks per day |
| `MCQ160F` | `MCQ` | Ever told had a stroke |
| `DIQ010` | `DIQ` | Ever told had diabetes |
| `DPQ010` through `DPQ090` | `DPQ` | PHQ-9 items, summed |
| `BPQ020`, `BPQ080` | `BPQ` | Told high blood pressure, told high cholesterol |

---

## Amendments

**2026-08-31, `ALQ120Q` added.** Alcohol quantity (`ALQ130`) is skipped whenever
drinking frequency (`ALQ120Q`) is zero, so 403 participants looked like missing
data when they are in fact non-drinkers. `ALQ120Q` is pulled solely to resolve
that skip pattern and is not itself a model feature. Reserved codes 777/999.
Effect: covariate-complete cases rose from 1,450 to 1,789 of 2,194. This is a
skip-pattern resolver within a file already locked, not a new construct.

## Open items carried into Phase 1

These are recorded rather than decided. Neither blocks the merge.

**Serum iron, `LBXSIR`.** The brief excludes serum iron as discontinued after
2009-2010. That is wrong: it is present in `BIOPRO` in both cycles on the full
sample. Not included in this lock. Because `BIOPRO` is already being merged,
adding it later costs one column rather than a re-clean, so this stays cheap to
reverse.

**The "3 of 4 scores" rule and `CFASTAT`.** `CFASTAT` counts three test
instruments, not four, because CERAD is a single administration producing two of
the four scores. Losing CERAD therefore drops two scores at once, so the
pre-specified ">= 3 of 4" rule effectively requires CERAD plus at least one other
instrument. Phase 2 proceeds with the brief's stated rule and will report the
alternative (CERAD counted as one instrument) alongside it, for decision at
Gate 2.

**Provenance.** Variable names for `DEMO`, `CFQ`, `PBCD`, `VITB12` and `CBC` were
read from the downloaded files. All others were read from the CDC codebook pages
and are confirmed against the actual columns as the first step of Phase 1.

---

## Sign-off

| Role | Name | Date |
|---|---|---|
| Data and modeling lead | Neil Patel | 2026-08-30 |
| Clinical and framing lead | Shreyan Kancharla | 2026-09-05 |
