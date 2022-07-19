import unittest
import sys
from io import StringIO

import dvs_criteria_cli


class TestCliDisplay(unittest.TestCase):
    def test_sample_input(self):
        sys.stdin = StringIO(
            f"86\n2\nasdf\n123\n123\n123\n123\n123\n123\n123\n123\n123\n123\n"
        )
        dvs_criteria_cli.main()
