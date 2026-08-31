"""
Phase 0b: download the raw NHANES files.

Closes the reproducibility gap between a fresh clone and `01_cohort.py`.
`data/raw/` is deliberately not tracked in git (54 MB of SAS XPORT), so
without this step nothing downstream can run.

URLs are not hardcoded here. They come from `data/interim/00_audit.json`,
which `00_audit.py` produced by parsing the CDC data pages and which is
tracked in git. If the CDC ever moves a file, re-run `00_audit.py` and the
new URL flows through automatically.

Every download is verified to begin with the SAS XPORT header, so a
200-status HTML error page is caught rather than written to disk as data.
Existing files are left untouched: raw data is never modified.

Run:  python3 src/00b_download.py
      python3 src/00b_download.py --check    verify what is present, download nothing
"""
from __future__ import annotations

import json
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
AUDIT = ROOT / "data" / "interim" / "00_audit.json"

XPORT_MAGIC = b"HEADER RECORD*******LIBRARY HEADER RECORD"

# The locked file list. Matches VARIABLE_LOCK.md. CUSEZN and TRIGLY were
# dropped by decision (subsamples), IHGEM was optional and excluded.
STEMS = ["DEMO", "CFQ", "PBCD", "VITB12", "MMA", "FOLFMS", "FOLATE", "VID",
         "CBC", "BIOPRO", "GHB", "HDL", "TCHOL", "BMX", "SMQ", "ALQ", "MCQ",
         "DPQ", "BPQ"]
# DIQ was added after the Phase 0 audit ran, so it is not in the audit JSON.
EXTRA_URLS = {
    "DIQ_G": "https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2011/DataFiles/DIQ_G.xpt",
    "DIQ_H": "https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2013/DataFiles/DIQ_H.xpt",
}


def urls_from_audit() -> dict[str, str]:
    """Read the verified .xpt URLs recorded by 00_audit.py."""
    if not AUDIT.exists():
        raise SystemExit(f"{AUDIT} is missing. Run `python3 src/00_audit.py` first.")
    audit = json.loads(AUDIT.read_text())
    out = {}
    for row in audit["availability"]:
        if row["stem"] not in STEMS:
            continue
        for cyc in ("G", "H"):
            url = row.get(f"{cyc}_url")
            if url:
                out[f'{row["stem"]}_{cyc}'] = url
    out.update(EXTRA_URLS)
    return out


def is_xport(path: Path) -> bool:
    with path.open("rb") as fh:
        return fh.read(len(XPORT_MAGIC)) == XPORT_MAGIC


def download(name: str, url: str) -> str:
    """Fetch one file. Returns a short status string."""
    dest = RAW / f"{name}.xpt"
    if dest.exists():
        return "ok (present)" if is_xport(dest) else "CORRUPT (delete and re-run)"

    tmp = dest.with_suffix(".partial")
    req = urllib.request.Request(url, headers={"User-Agent": "nhanes-analysis"})
    try:
        with urllib.request.urlopen(req, timeout=180) as r:
            tmp.write_bytes(r.read())
    except Exception as exc:  # network or HTTP failure
        tmp.unlink(missing_ok=True)
        return f"FAILED ({type(exc).__name__})"

    if not is_xport(tmp):
        tmp.unlink(missing_ok=True)
        return "FAILED (not a SAS XPORT file)"

    tmp.rename(dest)
    return f"downloaded ({dest.stat().st_size / 1_048_576:.1f} MB)"


def main() -> None:
    check_only = "--check" in sys.argv
    RAW.mkdir(parents=True, exist_ok=True)
    urls = urls_from_audit()

    print(f"{len(urls)} files expected in {RAW.relative_to(ROOT)}\n")
    failures, present = [], 0
    for name, url in sorted(urls.items()):
        dest = RAW / f"{name}.xpt"
        if check_only:
            status = ("ok" if dest.exists() and is_xport(dest)
                      else "MISSING" if not dest.exists() else "CORRUPT")
        else:
            status = download(name, url)
        if status.startswith(("ok", "downloaded")):
            present += 1
        else:
            failures.append((name, status))
        print(f"  {name:<12} {status}")

    print(f"\n{present} of {len(urls)} files present and valid")
    if failures:
        print("\nfailures:")
        for name, status in failures:
            print(f"  {name}: {status}")
        raise SystemExit(1)
    print("Ready. Next: python3 src/01_cohort.py")


if __name__ == "__main__":
    main()
