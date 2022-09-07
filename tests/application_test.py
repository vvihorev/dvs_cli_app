import unittest
import sys
from io import StringIO

from storage import CsvStorage
from model import FirstCriterion, SecondCriterion, Engine, assign_engine_group
import controller


class CliDisplayTest(unittest.TestCase):
    """Functional test. Check if the program runs and reacts to user input"""

    def test_sample_first_criteria(self):
        sys.stdin = StringIO(
            "86\n1\ntest engine\n500\n294\n0.54\n5.1\n0.36\n16490\n0.0002\n81780\n13610\n1\n"
        )
        controller.main()

    def test_sample_second_criteria(self):
        sys.stdin = StringIO(
            "86\n2\ntest engine\n500\n294\n0.54\n5.1\n0.36\n16490\n0.0002\n81780\n13610\n1\n"
        )
        controller.main()


class FirstCriteriaCalculationsTest(unittest.TestCase):
    """Unit test. Test correctness of calculations performed with enginges"""

    # TODO: rewrite tests for first criteria based on hand calculated results

    def setUp(self):
        table_engines = CsvStorage("base_engines").load()
        crit = FirstCriterion(table_engines, 86.0)
        engine = Engine(
            {
                "name": "test engine",
                "nu": 500,
                "N_e": 294,
                "p_e": 0.54,
                "p_z": 5.1,
                "S_n": 0.36,
                "N_max": 16490,
                "delta": 0.0002,
                "D_czvt": 13610,
                "D_czb": 81780,
                "D_c": 1,
            }
        )
        engine["group"] = assign_engine_group(engine["nu"])
        crit.predict(engine)
        self.results = crit.results

    def test_B_D_calculations(self):
        b_d = self.results.df_B_D
        self.assertAlmostEqual(b_d.loc["6L278Rr", ("500")], -4.085295058497215e-05)
        self.assertAlmostEqual(b_d.loc["6L278Rr", ("D")], -0.216)

    def test_regression_calculations(self):
        regr = self.results.df_regression
        self.assertAlmostEqual(regr.loc[("Group 2", "a"), "500"], -540.3145563345213)
        self.assertAlmostEqual(regr.loc[("Group 2", "b"), "500"], -0.23066669946883683)

    def test_vibrations_calculations(self):
        vibr = self.results.df_vibrations
        self.assertAlmostEqual(vibr.loc["6L278Rr", "500"], 130.93536284658433)
        self.assertAlmostEqual(vibr.loc["6L278PN", "500"], 88.3741015493173)


class SecondCriteriaCalculationsTest(unittest.TestCase):
    """Unit test. Test correctness of calculations performed with enginges"""

    def setUp(self):
        table_engines = CsvStorage("base_engines").load()
        crit = SecondCriterion(table_engines, 86.0)
        engine = Engine(
            {
                "name": "test engine",
                "nu": 500,
                "N_e": 294,
                "p_e": 0.54,
                "p_z": 5.1,
                "S_n": 0.36,
                "N_max": 16490,
                "delta": 0.0002,
                "D_czvt": 13610,
                "D_czb": 81780,
                "D_c": 1,
            }
        )
        engine["group"] = assign_engine_group(engine["nu"])
        crit.predict(engine)
        self.results = crit.results

    def test_B_D_calculations(self):
        b_d = self.results.df_B_D
        self.assertAlmostEqual(b_d.loc["6L278Rr", ("500")], 1.19913696681069e-05)
        self.assertAlmostEqual(b_d.loc["6L278Rr", ("D")], 0.216)

    def test_regression_calculations(self):
        regr = self.results.df_regression
        self.assertAlmostEqual(regr.loc[("Group 2", "a"), "500"], -2233.57768241412)
        self.assertAlmostEqual(regr.loc[("Group 2", "b"), "500"], 0.236958861324529)

    def test_vibrations_calculations(self):
        vibr = self.results.df_vibrations
        self.assertAlmostEqual(vibr.loc["6L278Rr", "500"], 111.178656483576)
        self.assertAlmostEqual(vibr.loc["6L278PN", "500"], 142.177680030173)
