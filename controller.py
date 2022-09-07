#!/usr/bin/env python3.10
from view import CLIInterface
from model import VibrationsCalculator
from storage import CsvStorage, SqliteStorage
import sqlite3


def main():
    # Create storage for input and output data.
    db = SqliteStorage('db.sqlite')
    engine_storage = db.use_table("base_engines")
    reg_coeficients_storage = db.use_table("regression")
    B_D_storage = db.use_table("B_D")
    vibrations_storage = db.use_table("vibrations")
    table_engines = engine_storage.load()

    # Get user preferences and user engine data.
    ui = CLIInterface()
    preferences = ui.get_preferences()
    ui.print_theory(preferences.criterion)
    user_engine = ui.get_user_engine()

    # Calculate critetion required by user.
    calculator = VibrationsCalculator(preferences, table_engines)
    calculator.process_user_engine(user_engine)
    criterion = calculator.criterion
    ui.print_vibrations(criterion)

    # Save calculations data.
    reg_coeficients_storage.save(criterion.results.df_regression)
    B_D_storage.save(criterion.results.df_B_D)
    vibrations_storage.save(criterion.results.df_vibrations)
    db.close()


if __name__ == "__main__":
    main()
