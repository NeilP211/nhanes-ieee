"""
Phase 0: NHANES 2011-2014 file and variable availability audit.

Establishes what exists on the CDC site and how many participants we have.
Performs no cleaning and builds no analytic dataset.

Outputs
    data/interim/00_audit.json          machine-readable audit record
    output/tables/00_availability_audit.md   the Phase 0 report

Run:  python3 src/00_audit.py
"""
from __future__ import annotations

import html as ihtml
import json
import os
import re
import urllib.request
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
INTERIM = ROOT / "data" / "interim"
CACHE = INTERIM / "cdc_cache"
TABLES = ROOT / "output" / "tables"
BASE = "https://wwwn.cdc.gov"

CYCLES = {"G": "2011", "H": "2013"}
CYCLE_LABEL = {"G": "2011-2012", "H": "2013-2014"}
COMPONENTS = ["Laboratory", "Demographics", "Questionnaire", "Examination"]

# (stem, block, role).  Every file named in PROJECT_BRIEF.md sections 3 and 10.
TARGETS = [
    ("DEMO", "Block 1", "Demographics and survey design variables"),
    ("CFQ", "Outcome", "Cognitive functioning (CERAD, animal fluency, DSST)"),
    ("PBCD", "Block 2", "Blood Pb, Cd, total Hg, Se, Mn"),
    ("IHGEM", "Block 2 opt", "Blood Hg speciation (inorganic, ethyl, methyl)"),
    ("VITB12", "Block 3", "Serum vitamin B12"),
    ("MMA", "Block 3", "Methylmalonic acid"),
    ("FOLFMS", "Block 3", "Serum folate forms, total and individual"),
    ("FOLATE", "Block 3", "RBC folate"),
    ("VID", "Block 3", "25-hydroxyvitamin D"),
    ("CUSEZN", "Block 3", "Serum copper, selenium, zinc"),
    ("CBC", "Block 3", "Complete blood count (NLR, PLR, SII)"),
    ("BIOPRO", "Block 3", "Standard biochemistry profile (albumin, creatinine)"),
    ("GHB", "Block 3", "Glycohemoglobin (HbA1c)"),
    ("HDL", "Block 3", "HDL cholesterol"),
    ("TCHOL", "Block 3", "Total cholesterol"),
    ("TRIGLY", "Block 3", "Triglycerides and LDL"),
    ("BMX", "Covariate", "Body measures (BMI)"),
    ("SMQ", "Covariate", "Smoking, cigarette use"),
    ("ALQ", "Covariate", "Alcohol use"),
    ("MCQ", "Covariate", "Medical conditions (stroke, diabetes)"),
    ("DPQ", "Covariate", "PHQ-9 depression screener"),
    ("BPQ", "Covariate", "Blood pressure and cholesterol history"),
]

# Files downloaded in Phase 0 for the sample-size question only.
DOWNLOADED = ["DEMO", "CFQ", "PBCD", "VITB12", "CBC"]

METALS = ["LBXBPB", "LBXBCD", "LBXTHG", "LBXBSE", "LBXBMN"]
METAL_LC = ["LBDBPBLC", "LBDBCDLC", "LBDTHGLC", "LBDBSELC", "LBDBMNLC"]
# Verified: the B12 variable is renamed between cycles.
B12_VAR = {"G": "LBXB12", "H": "LBDB12"}

# NHANES encodes a zero MEC weight as this denormal, not as exact 0.0.
ZERO_WEIGHT = 1e-60


def fetch(url: str, dest: Path) -> str:
    """Fetch url to dest, reusing the cached copy when present."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    if not dest.exists():
        req = urllib.request.Request(url, headers={"User-Agent": "nhanes-audit"})
        with urllib.request.urlopen(req, timeout=90) as r:
            dest.write_bytes(r.read())
    return dest.read_text(encoding="utf-8", errors="replace")


def strip_tags(s: str) -> str:
    return re.sub(r"\s+", " ", ihtml.unescape(re.sub(r"<[^>]+>", " ", s))).strip()


def build_cdc_index() -> dict:
    """Parse the CDC data-listing pages into {STEM: {...}} for both cycles."""
    index = {}
    for comp in COMPONENTS:
        for cyc, year in CYCLES.items():
            url = f"{BASE}/nchs/nhanes/search/datapage.aspx?Component={comp}&CycleBeginYear={year}"
            page = fetch(url, CACHE / f"{comp}_{year}.html")
            for tr in re.findall(r"<tr>(.*?)</tr>", page, re.S):
                tds = re.findall(r"<td[^>]*>(.*?)</td>", tr, re.S)
                if len(tds) < 4:
                    continue
                doc = re.search(r'href="([^"]+)"', tds[1])
                dat = re.search(r'href="([^"]+)"', tds[2])
                if not dat:
                    continue
                stem = os.path.basename(dat.group(1)).rsplit(".", 1)[0].upper()
                index[stem] = dict(
                    component=comp,
                    cycle=cyc,
                    desc=strip_tags(tds[0]),
                    xpt_url=BASE + dat.group(1),
                    doc_url=BASE + doc.group(1) if doc else None,
                    size=strip_tags(tds[2]),
                    published=strip_tags(tds[3]),
                )
    return index


def doc_variables(stem_cyc: str, doc_url: str) -> dict:
    """Return the codebook variable list and any WT-prefixed weight columns."""
    page = fetch(doc_url, CACHE / f"doc_{stem_cyc}.htm")
    pairs = re.findall(r'<h3 class="vartitle" id="([A-Za-z0-9_]+)">\s*([^<]*)', page)
    # CDC anchors use display casing (MCQ160f); SAS column names are uppercase.
    variables = [(v.upper(), ihtml.unescape(d).strip()) for v, d in pairs]
    body = page[: page.find('class="vartitle"')] if 'class="vartitle"' in page else page
    text = strip_tags(body)
    subsample = bool(re.search(r"one[- ](?:half|third|quarter) subsample|subsample of", text, re.I))
    return dict(
        n_vars=len(variables),
        variables=variables,
        wt_vars=[v for v, _ in variables if v.upper().startswith("WT")],
        subsample_language=subsample,
    )


def read_xpt(stem: str, cyc: str) -> pd.DataFrame:
    df = pd.read_sas(RAW / f"{stem}_{cyc}.xpt", format="xport")
    df.columns = [str(c) for c in df.columns]
    return df


def cognitive_scores(cfq: pd.DataFrame) -> pd.DataFrame:
    """The four component scores. CERAD immediate requires all three trials."""
    return pd.DataFrame(
        {
            "cerad_immediate": cfq[["CFDCST1", "CFDCST2", "CFDCST3"]].sum(axis=1, min_count=3),
            "cerad_delayed": cfq["CFDCSR"],
            "animal_fluency": cfq["CFDAST"],
            "dsst": cfq["CFDDS"],
        }
    )


def cycle_counts(cyc: str) -> dict:
    """Attrition counts for one cycle. No imputation, no cleaning."""
    demo, cfq = read_xpt("DEMO", cyc), read_xpt("CFQ", cyc)
    pbcd, b12 = read_xpt("PBCD", cyc), read_xpt("VITB12", cyc)

    d60 = demo[demo.RIDAGEYR >= 60]
    mec = d60[d60.RIDSTATR == 2]
    nonzero_wt = int((mec.WTMEC2YR > ZERO_WEIGHT).sum())

    j = mec[["SEQN", "WTMEC2YR"]].merge(cfq, on="SEQN", how="left")
    n_scores = cognitive_scores(j).notna().sum(axis=1)
    cog = j[n_scores >= 3]

    m = cog.merge(pbcd, on="SEQN", how="left")
    has_metals = m[METALS].notna().all(axis=1)
    v = m.merge(b12, on="SEQN", how="left")
    has_b12 = v[B12_VAR[cyc]].notna()

    lod = {}
    for conc, lc in zip(METALS, METAL_LC):
        sub = pbcd[pbcd[conc].notna()]
        lod[conc] = round(100.0 * float((sub[lc] == 1).mean()), 1) if len(sub) else None

    return dict(
        cycle=CYCLE_LABEL[cyc],
        demo_rows=len(demo),
        aged_60plus=len(d60),
        mec_examined=len(mec),
        interview_only=int((d60.RIDSTATR == 1).sum()),
        nonzero_mec_weight=nonzero_wt,
        cfq_rows=len(cfq),
        cog_4of4=int((n_scores >= 4).sum()),
        cog_3of4=int((n_scores >= 3).sum()),
        cog_and_metals=int(has_metals.sum()),
        cog_and_b12=int(has_b12.sum()),
        cog_metals_b12=int((has_metals & has_b12).sum()),
        pbcd_rows=len(pbcd),
        pbcd_60plus_rows=int(d60.merge(pbcd, on="SEQN", how="inner").shape[0]),
        pct_below_lod=lod,
    )


def main() -> None:
    TABLES.mkdir(parents=True, exist_ok=True)
    INTERIM.mkdir(parents=True, exist_ok=True)

    index = build_cdc_index()
    availability = []
    for stem, block, role in TARGETS:
        rec = dict(stem=stem, block=block, role=role)
        for cyc in CYCLES:
            key = f"{stem}_{cyc}"
            hit = index.get(key)
            rec[f"{cyc}_present"] = hit is not None
            rec[f"{cyc}_url"] = hit["xpt_url"] if hit else None
            rec[f"{cyc}_desc"] = hit["desc"] if hit else None
            rec[f"{cyc}_size"] = hit["size"] if hit else None
            if hit and hit["doc_url"]:
                info = doc_variables(key, hit["doc_url"])
                rec[f"{cyc}_wt"] = info["wt_vars"]
                rec[f"{cyc}_nvars"] = info["n_vars"]
                rec[f"{cyc}_subsample_text"] = info["subsample_language"]
        availability.append(rec)

    columns = {}
    for stem in DOWNLOADED:
        for cyc in CYCLES:
            p = RAW / f"{stem}_{cyc}.xpt"
            if p.exists():
                df = read_xpt(stem, cyc)
                columns[f"{stem}_{cyc}"] = dict(
                    n_rows=int(len(df)), columns=[str(c) for c in df.columns]
                )

    counts = {cyc: cycle_counts(cyc) for cyc in CYCLES}
    combined = {
        k: counts["G"][k] + counts["H"][k]
        for k in ["aged_60plus", "mec_examined", "cog_3of4", "cog_4of4",
                  "cog_and_metals", "cog_and_b12", "cog_metals_b12"]
    }

    audit = dict(availability=availability, columns=columns, counts=counts, combined=combined)
    (INTERIM / "00_audit.json").write_text(json.dumps(audit, indent=1))
    write_report(audit)
    print("wrote", INTERIM / "00_audit.json")
    print("wrote", TABLES / "00_availability_audit.md")
    print("combined analytic counts:", json.dumps(combined, indent=1))


def write_report(audit: dict) -> None:
    from report_00 import render  # noqa: PLC0415

    (TABLES / "00_availability_audit.md").write_text(render(audit))


if __name__ == "__main__":
    main()
