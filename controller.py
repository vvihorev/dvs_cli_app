#!/usr/bin/env python3.10
from view import CLIInterface
from model import VibrationsCalculator
from storage import CsvStorage


def main():
    # Create storage for input and output data.
    engine_storage = CsvStorage("base_engines")
    reg_coeficients_storage = CsvStorage("regression")
    B_D_storage = CsvStorage("B_D")
    vibrations_storage = CsvStorage("vibrations")
    table_engines = engine_storage.load()

    # Get user preferences and engine data.
    ui = CLIInterface()
    preferences = ui.get_preferences()
    ui.print_theory(preferences.criterion)
    engine = ui.get_user_engine()

    # Calculate critetion required by user.
    calculator = VibrationsCalculator(preferences, table_engines)
    calculator.predict(engine)
    criterion = calculator.criterion
    ui.print_vibrations(criterion)

    # Save calculations data.
    reg_coeficients_storage.save(criterion.results.df_regression)
    B_D_storage.save(criterion.results.df_B_D)
    vibrations_storage.save(criterion.results.df_vibrations)


if __name__ == "__main__":
    main()
