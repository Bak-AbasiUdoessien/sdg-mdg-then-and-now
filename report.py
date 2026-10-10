"""
report.py  -  MDG -> SDG "Then and Now" report (all goals)
For one country, compares where things stood in 1990 (MDG baseline), 2000 (MDGs start),
2015 (MDGs end / SDGs start) and the latest year, and asks: has progress sped up or
slowed down since the SDGs began? Writes report.md plus one small SVG chart per indicator.

Run:
    python report.py              # Nigeria
    python report.py GHA          # any ISO3 country code
    python report.py --offline    # made-up DEMO data
"""

import argparse
import sys
from pathlib import Path

import worldbank
from analysis import MDG_END, MDG_START, compare_eras

ROOT = Path(__file__).parent

# (MDG it belonged to, SDG it lives on in, label, World Bank code, higher_is_better)
INDICATORS = [
    ("MDG 1", "SDG 1.1", "Extreme poverty (% of people)", "SI.POV.DDAY", False),
    ("MDG 2", "SDG 4.1", "Primary completion rate (%)", "SE.PRM.CMPT.ZS", True),
    ("MDG 3", "SDG 4.5", "School gender parity (girls per boy)", "SE.ENR.PRSC.FM.ZS", True),
    ("MDG 4", "SDG 3.2", "Under-5 deaths per 1,000 births", "SH.DYN.MORT", False),
    ("MDG 5", "SDG 3.1", "Maternal deaths per 100,000 births", "SH.STA.MMRT", False),
    ("MDG 6", "SDG 3.3", "HIV prevalence, ages 15-49 (%)", "SH.DYN.AIDS.ZS", False),
    ("MDG 7", "SDG 6.1", "Basic drinking water (%)", "SH.H2O.BASW.ZS", True),
]


def fmt(pair):
    """Format a (year, value) pair as 'value (year)', or a dash if missing."""
    year, value = pair
    if value is None:
        return "–"
    return f"{value:,.2f} ({year})" if value < 10 else f"{value:,.1f} ({year})"   # more decimals for small numbers


def sparkline_svg(series, path):
    """A small line chart (300x80) with the MDG era shaded. Plain SVG, no libraries."""
    if len(series) < 2:
        return False
    years = sorted(series)
    lo, hi = min(series.values()), max(series.values())
    span = (hi - lo) or 1                                          # avoid dividing by zero for a flat line
    w, h, pad = 300, 80, 6
    x = lambda yr: pad + (yr - 1990) / (2025 - 1990) * (w - 2 * pad)   # fixed 1990-2025 axis for every chart
    y = lambda v: h - pad - (v - lo) / span * (h - 2 * pad)
    pts = " ".join(f"{x(yr):.1f},{y(series[yr]):.1f}" for yr in years)
    path.write_text(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h + 14}" font-family="sans-serif" font-size="9">'
        f'<rect width="100%" height="100%" fill="white"/>'
        f'<rect x="{x(MDG_START):.1f}" y="0" width="{x(MDG_END) - x(MDG_START):.1f}" height="{h}" fill="#eef3f8"/>'
        f'<polyline points="{pts}" fill="none" stroke="#2f6fa7" stroke-width="2"/>'
        f'<text x="{x(MDG_START) + 2:.1f}" y="10" fill="#7a8a99">MDG era</text>'
        f'<text x="{pad}" y="{h + 11}" fill="#666">1990</text>'
        f'<text x="{w - pad}" y="{h + 11}" fill="#666" text-anchor="end">2025</text></svg>',
        encoding="utf-8")
    return True


def main():
    p = argparse.ArgumentParser(description="MDG vs SDG era progress report for one country.")
    p.add_argument("country", nargs="?", default="NGA", help="ISO3 code (default NGA)")
    p.add_argument("--offline", action="store_true", help="made-up demo data")
    a = p.parse_args()
    country = "DEMO" if a.offline else a.country.upper()

    charts = ROOT / "charts"
    charts.mkdir(exist_ok=True)
    lines = [f"# {country}: from the MDGs to the SDGs", ""]
    if a.offline:
        lines += ["> **DEMO DATA - these numbers are made up.**", ""]
    lines += ["Shaded area in each chart = MDG era (2000–2015). Values show the nearest reported year in brackets.", "",
              "| Goal | Indicator | 1990 | 2000 | 2015 | Latest | Per year 2000–15 | Per year since 2015 | Verdict |",
              "|---|---|---|---|---|---|---|---|---|"]
    details, got_any = [], False
    for mdg, sdg, label, code, higher_better in INDICATORS:
        try:
            series = worldbank.demo(code) if a.offline else worldbank.fetch(country, code)
        except OSError as err:
            print(f"  ! {code}: {err}")
            series = {}
        r = compare_eras(series, higher_better)
        got_any = got_any or bool(series)
        rate = lambda v: "–" if v is None else (f"{v:+.3f}" if abs(v) < 0.1 else f"{v:+.2f}")  # + sign shows direction; more decimals for tiny rates
        lines.append(f"| {mdg} → {sdg} | {label} | {fmt(r['baseline'])} | {fmt(r['mdg_start'])} | "
                     f"{fmt(r['mdg_end'])} | {fmt(r['latest'])} | {rate(r['mdg_rate'])} | "
                     f"{rate(r['sdg_rate'])} | **{r['verdict']}** |")
        print(f"{mdg:<6}{label:<40}{r['verdict']}")
        if sparkline_svg(series, charts / f"{code}.svg"):
            details.append(f"### {label} ({mdg} → {sdg})\n![{label}](charts/{code}.svg)\n")

    if not got_any:
        sys.exit("No data downloaded. Check your connection, or try --offline.")
    lines += ["", "## Charts", ""] + details + [
        "## How to read the verdict",
        "- *Per year* = average change per year between the two points; a `+` means the number went up.",
        "- The verdict compares the **pace of progress** in each era (10% tolerance), taking into account",
        "  whether a higher value is good (school completion) or bad (child deaths).",
        "", "Source: World Bank Open Data (World Development Indicators)."]
    (ROOT / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\nSaved report.md and charts/ - open report.md in VS Code and press Ctrl+Shift+V to preview it")


if __name__ == "__main__":
    main()
