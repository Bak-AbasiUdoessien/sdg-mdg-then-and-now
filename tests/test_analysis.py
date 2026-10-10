"""Unit tests for analysis.py. Run:  python -m unittest discover tests"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from analysis import compare_eras, per_year, value_near  # noqa: E402


class AnalysisTests(unittest.TestCase):
    def test_value_near_prefers_exact_then_closest(self):
        s = {1999: 5, 2002: 8}
        self.assertEqual(value_near(s, 2000), (1999, 5))      # 1 year away beats 2 years away
        self.assertEqual(value_near(s, 2010), (None, None))   # nothing within 3 years

    def test_per_year(self):
        self.assertEqual(per_year({2000: 10, 2015: 40}, 2000, 2015), 2.0)

    def test_slower_since_2015(self):
        s = {2000: 0, 2015: 30, 2023: 38}                     # +2/yr in MDG era, +1/yr after
        self.assertEqual(compare_eras(s, True)["verdict"], "slower since 2015")

    def test_lower_is_better(self):
        s = {2000: 200, 2015: 170, 2023: 130}                 # deaths falling 2/yr, then 5/yr
        self.assertEqual(compare_eras(s, False)["verdict"], "faster since 2015")

    def test_reversal(self):
        s = {2000: 50, 2015: 65, 2023: 60}                    # rose, then fell back
        self.assertEqual(compare_eras(s, True)["verdict"], "progress has reversed since 2015")


if __name__ == "__main__":
    unittest.main()
