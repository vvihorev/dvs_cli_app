import sys
from io import StringIO

import dvs_criteria_cli

sys.stdin = StringIO(f"86\n2\nasdf\n123\n123\n123\n123\n123\n123\n123\n123\n123\n123\n")
dvs_criteria_cli.main()
