import unittest
import sys
from io import StringIO

from storage import CsvStorage
from model import SecondCriterion, Engine
import controller


class CliDisplayTest(unittest.TestCase):
    """Functional test. Check if the program runs and reacts to user input"""

    def test_sample_input(self):
        sys.stdin = StringIO(
            f"86\n2\nasdf\n123\n123\n123\n123\n123\n123\n123\n123\n123\n123\n"
        )
        controller.main()


class SecondCriteriaCalculationsTest(unittest.TestCase):
    """Unit test. Test correctness of calculations performed with enginges"""

    def setUp(self):
        engine_parameters = CsvStorage("base_engines").load()
        crit = SecondCriterion(engine_parameters, 86.0)
        engine = Engine(
            {
                "name": "test engine",
                "nu": 500,
                "N_e": 500,
                "p_e": 500,
                "p_z": 500,
                "S_n": 500,
                "N_max": 500,
                "delta": 500,
                "D_czb": 500,
                "D_czvt": 500,
                "D_c": 500,
            }
        )
        crit.process_engine(engine)
        self.results = crit.results

    def test_B_D_calculations(self):
        b_d = self.results.df_B_D
        self.assertAlmostEqual(b_d.loc["6L278Rr", ("500", "B")], 1.19913696681069e-05)
        self.assertAlmostEqual(b_d.loc["6L278Rr", ("500", "D")], 0.216)

    def test_regression_calculations(self):
        regr = self.results.df_regression
        self.assertAlmostEqual(regr.loc[("Group 2", "a"), "500"], -2233.57768241412)
        self.assertAlmostEqual(regr.loc[("Group 2", "b"), "500"], 0.236958861324529)

    def test_vibrations_calculations(self):
        vibr = self.results.df_vibrations
        self.assertAlmostEqual(vibr.loc["6L278Rr", "500"], 111.178656483576)
        self.assertAlmostEqual(vibr.loc["6L278PN", "500"], 142.177680030173)
