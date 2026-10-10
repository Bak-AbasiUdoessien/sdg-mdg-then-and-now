"""
analysis.py  -  The comparison logic: find values near key years and compare rates of progress.
"""

MDG_START, MDG_END = 2000, 2015          # the MDG era
BASELINE = 1990                          # MDG targets were measured against 1990


def value_near(series, year, tolerance=3):
    """
    Value for `year`, or the closest year within `tolerance` years if that exact year is missing.
    Returns (actual_year, value) or (None, None). Countries don't report every year, so this matters.
    """
    for gap in range(tolerance + 1):                              # try 0, then ±1, ±2, ±3 years
        for y in (year - gap, year + gap):
            if y in series:
                return y, series[y]
    return None, None


def per_year(series, start, end):
    """Average change per year between two points (None if either point is missing)."""
    y1, v1 = value_near(series, start)
    y2, v2 = value_near(series, end)
    if v1 is None or v2 is None or y2 <= y1:
        return None
    return (v2 - v1) / (y2 - y1)                                  # slope between the two points


def compare_eras(series, higher_is_better):
    """
    Compare the pace of progress during the MDG era (2000-2015) with the SDG era (2015-latest).
    Returns a dict ready for the report.
    """
    latest_year = max(series) if series else None
    result = {
        "baseline": value_near(series, BASELINE),
        "mdg_start": value_near(series, MDG_START),
        "mdg_end": value_near(series, MDG_END),
        "latest": (latest_year, series.get(latest_year)),
        "mdg_rate": per_year(series, MDG_START, MDG_END),
        "sdg_rate": per_year(series, MDG_END, latest_year) if latest_year and latest_year > MDG_END + 1 else None,
    }
    m, s = result["mdg_rate"], result["sdg_rate"]
    if m is None or s is None:
        result["verdict"] = "not enough data"
    else:
        sign = 1 if higher_is_better else -1                      # turn "lower is better" into "higher is better"
        m, s = m * sign, s * sign                                 # now positive always means progress
        if s <= 0 < m:
            result["verdict"] = "progress has reversed since 2015"
        elif s <= 0 and m <= 0:
            result["verdict"] = "no progress in either era"
        elif s >= m * 1.1:                                        # at least 10% faster
            result["verdict"] = "faster since 2015"
        elif s <= m * 0.9:                                        # at least 10% slower
            result["verdict"] = "slower since 2015"
        else:
            result["verdict"] = "about the same pace"
    return result
