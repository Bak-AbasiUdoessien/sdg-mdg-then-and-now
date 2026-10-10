# From the MDGs to the SDGs: Then and Now (all goals)

The Millennium Development Goals (2000–2015) set 1990 as their baseline. In 2015 the Sustainable Development Goals took over. This project asks one question for a country:

> **Has progress sped up or slowed down since the SDGs began?**

For seven indicators that were MDG targets and live on as SDG targets, it fetches real World Bank data and finds the values for **1990, 2000, 2015 and the latest year**. It then compares the **pace of change per year** in the MDG era with the SDG era and writes **`report.md`**, a Markdown report with a table and an SVG chart for each indicator, which GitHub displays directly.

| MDG → SDG | Indicator | World Bank code |
|---|---|---|
| 1 → 1.1 | Extreme poverty | `SI.POV.DDAY` |
| 2 → 4.1 | Primary completion | `SE.PRM.CMPT.ZS` |
| 3 → 4.5 | School gender parity | `SE.ENR.PRSC.FM.ZS` |
| 4 → 3.2 | Under-5 mortality | `SH.DYN.MORT` |
| 5 → 3.1 | Maternal mortality | `SH.STA.MMRT` |
| 6 → 3.3 | HIV prevalence | `SH.DYN.AIDS.ZS` |
| 7 → 6.1 | Basic drinking water | `SH.H2O.BASW.ZS` |

## Run it
```bash
python report.py              # Nigeria
python report.py GHA          # any ISO3 code
python report.py --offline    # made-up demo data
python -m unittest discover tests
```
Open `report.md` in VS Code and press **Ctrl+Shift+V** to preview it with the charts.

**Tip for your portfolio:** run it for Nigeria with real data, then commit `report.md` and `charts/`. GitHub will display the finished report on the repo page.

## Logic worth explaining (`analysis.py`)
- **Missing years:** countries don't report every year, so `value_near()` takes the closest year within ±3 and shows which year it used.
- **Rate per year** = (later value − earlier value) ÷ years between them.
- **Fair verdicts:** for "lower is better" indicators such as deaths and poverty, the sign is flipped so that positive always means progress. The pace counts as "faster" or "slower" only beyond a 10% difference. A reversal (progress before 2015 but none since) is called out separately.

## Limitations
- Two points per era is a simplification. A regression over all the years in between would be more robust (see the sdg-progress-tracker project).
- For gender parity the ideal is 1.0, not "higher". A value above 1.03 means boys are behind, so read that row with care.
- Some indicators start after 1990. Drinking water, for example, starts in 2000, so its 1990 column shows "–".

## ⚠️ Data note
`--offline` uses **invented** smooth trends. Only quote results from real downloads.
