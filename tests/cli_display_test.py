import unittest
import sys
from io import StringIO

import controller


class TestCliDisplay(unittest.TestCase):
    def test_sample_input(self):
        sys.stdin = StringIO(
            f"86\n2\nasdf\n123\n123\n123\n123\n123\n123\n123\n123\n123\n123\n"
        )
        controller.main()


if __name__ == "__main__":
    sys.stdin = StringIO(
        f"86\n2\nasdf\n123\n123\n123\n123\n123\n123\n123\n123\n123\n123\n"
    )
    dvs_criteria_cli.main()
