#!/usr/bin/env python3.10

# from typing import NamedTuple

import pandas as pd

import cli_display
import storage
import core
from core import Engine, CalculationResults
from config import Preferences


def main():
    engine_storage = storage.CsvStorage('data/base_engines.csv')
    engine_parameters: pd.DataFrame = engine_storage.load()

    preferences: Preferences = cli_display.get_preferences()
    cli_display.print_theory(preferences.criterion)
    engine: Engine = cli_display.get_engine()

    calculator = core.CriteriaCalculator(preferences, engine_parameters)
    calculator.get_engine_vibrations(engine)    

    criterion = calculator.criterion
    cli_display.print_vibrations(criterion)

    # storage.save_engines_table(calculation_results.engines_table)
    # storage.save_regression_coefficients(calculation_results.regression_coefficients)


if __name__ == "__main__":
    main()
