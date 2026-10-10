"""
worldbank.py  -  Download indicator data from the World Bank Open Data API (free, no key).
Each response is cached in data/ so it is only downloaded once.
"""

import json
import math
import urllib.request
from pathlib import Path

CACHE = Path(__file__).parent / "data"
API = ("https://api.worldbank.org/v2/country/{country}/indicator/{code}"
       "?format=json&per_page=200&date=1990:2025")              # from 1990, the MDG baseline year


def fetch(country, code):
    """Return {year: value} for one country and indicator, skipping years with no data."""
    CACHE.mkdir(exist_ok=True)
    cache_file = CACHE / f"{country}_{code}.json"
    if cache_file.exists():
        payload = json.loads(cache_file.read_text(encoding="utf-8"))
    else:
        with urllib.request.urlopen(API.format(country=country, code=code), timeout=30) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
        cache_file.write_text(json.dumps(payload), encoding="utf-8")
    if len(payload) < 2 or payload[1] is None:                  # only metadata = no data
        return {}
    return {int(r["date"]): float(r["value"]) for r in payload[1] if r["value"] is not None}


def demo(code):
    """MADE-UP smooth series for offline practice (not real statistics)."""
    start, yearly = {"SI.POV.DDAY": (60, -0.9), "SH.DYN.MORT": (210, -4.5), "SH.STA.MMRT": (1200, -18),
                     "SE.PRM.CMPT.ZS": (55, 0.7), "SH.H2O.BASW.ZS": (45, 1.1),
                     "SE.ENR.PRSC.FM.ZS": (0.78, 0.007), "SH.DYN.AIDS.ZS": (2.5, -0.03)}[code]
    return {y: max(0.0, start + yearly * (y - 1990) + 0.02 * start * math.sin(y))   # trend + a small wobble
            for y in range(1990, 2024)}
