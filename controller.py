#!/usr/bin/env python3.10
from view import CLIInterface
from model import CriteriaCalculator
from storage import CsvStorage


def main():
    # Create storage for input and output data.
    engine_storage = CsvStorage("base_engines")
    reg_coeficients_storage = CsvStorage("regression")
    B_D_storage = CsvStorage("B_D")
    vibrations_storage = CsvStorage("vibrations")
    engine_parameters = engine_storage.load()

    # Get user preferences and engine data.
    ui = CLIInterface()
    preferences = ui.get_preferences()
    ui.print_theory(preferences.criterion)
    engine = ui.get_engine()

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
