#!/usr/bin/env python3.10
import cli_display
from storage import CsvStorage
from core import CriteriaCalculator


def main():
    # Create storage for input and output data.
    engine_storage = CsvStorage("data/base_engines.csv")
    reg_coeficients_storage = CsvStorage("output/regressions.csv")
    B_D_storage = CsvStorage("output/B_D.csv")
    vibrations_storage = CsvStorage("output/vibrations.csv")
    engine_parameters = engine_storage.load()

    # Get user preferences and engine data.
    preferences = cli_display.get_preferences()
    cli_display.print_theory(preferences.criterion)
    engine = cli_display.get_engine()

    # Calculate critetion required by user.
    calculator = CriteriaCalculator(preferences, engine_parameters)
    calculator.get_engine_vibrations(engine)
    criterion = calculator.criterion
    # cli_display.print_vibrations(criterion)

    # Save calculations data.
    reg_coeficients_storage.save(criterion.results.df_regression)
    B_D_storage.save(criterion.results.df_B_D)
    vibrations_storage.save(criterion.results.df_vibrations)


if __name__ == "__main__":
    main()
