"""
Phase 15 (revision): fill numbers into the revised manuscript and response.

Templates under output/revision/ contain tokens of the form [[key|field]] or
[[key|field#fmt]], resolved against output/revision/generated/numbers.json
(written by phase 14). Floats default to four decimals; '#d' prints an
integer, '#.3f' etc. any format, '#abs' the absolute value. Every token must
resolve or the run fails, so no number in the revised text is typed by hand.

    manuscript_revised.template.tex     ->  manuscript_revised.tex
    response_to_reviewers.template.tex  ->  response_to_reviewers.tex

Run:  python3 src/15_fill_revision_text.py
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REV = ROOT / "output" / "revision"
TOKEN = re.compile(r"\[\[([^\[\]]+?)\]\]")
# Generated table bodies are inlined, because \input inside a table row stops
# \multicolumn from being the first item in its cell.
INPUT = re.compile(r"\\input\{(generated/[^}]+)\}")
PAIRS = [("manuscript_revised.template.tex", "manuscript_revised.tex"),
         ("response_to_reviewers.template.tex", "response_to_reviewers.tex"),
         ("supplementary/Additional_file_4_Revision_tables.template.tex",
          "supplementary/Additional_file_4_Revision_tables.tex")]
BANNED = (chr(0x2014), chr(0x2013))  # em and en dash: never in this project's text


def resolve(numbers: dict, token: str):
    path, _, fmt = token.partition("#")
    parts = path.split("|")
    for cut in range(len(parts), 0, -1):
        key = "|".join(parts[:cut])
        if key in numbers:
            value = numbers[key]
            for p in parts[cut:]:
                value = value[p]
            return value, fmt
    raise KeyError(f"unresolved token [[{token}]]")


def render(value, fmt: str) -> str:
    if isinstance(value, str):
        value = value.replace("%", "\\%")
        return re.sub(r"(?<![\w.])-(\d)", r"$-$\1", value)
    if isinstance(value, bool):
        return "yes" if value else "no"
    if fmt == "d":
        return f"{int(round(value)):,}"
    if fmt == "abs":
        return f"{abs(value):.4f}"
    return format(value, fmt or ".4f")


def fill(text: str, numbers: dict) -> tuple[str, int]:
    count = 0

    def sub(m):
        nonlocal count
        count += 1
        return render(*resolve(numbers, m.group(1)))

    out = TOKEN.sub(sub, text)
    assert "[[" not in out, "a token was left unfilled"
    return out, count


def main() -> None:
    numbers = json.loads((REV / "generated" / "numbers.json").read_text())
    for src, dst in PAIRS:
        path = REV / src
        if not path.exists():
            print(f"  skip {src} (not written yet)")
            continue
        text = INPUT.sub(lambda m: (REV / m.group(1)).read_text().rstrip("\n"), path.read_text())
        out, n = fill(text, numbers)
        for bad in BANNED:
            assert bad not in out, f"{dst} contains a banned dash character"
        (REV / dst).write_text(out)
        print(f"  {src} -> {dst}: {n} numbers filled")


if __name__ == "__main__":
    main()
