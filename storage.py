from abc import ABC, abstractmethod
import pandas as pd
import sqlite3


class Storage(ABC):
    """Storage interface"""

    def __init__(self, file):
        self.file = file

    @abstractmethod
    def load(self) -> pd.DataFrame:
        raise NotImplementedError

    @abstractmethod
    def save(self, data: pd.DataFrame) -> None:
        raise NotImplementedError


class CsvStorage(Storage):
    """Store data using csv files."""

    def __init__(self, file: str):
        self.file = "data/" + file + ".csv"

    def load(self) -> pd.DataFrame:
        return pd.read_csv(self.file)

    def save(self, data: pd.DataFrame):
        data.to_csv(self.file, index=False)


class TableStorage(Storage):
    """Individual table in SqliteStorage."""

    def __init__(self, con: sqlite3.Connection, table_name: str):
        self.con = con
        self.table_name = table_name

    def load(self) -> pd.DataFrame:
        return pd.read_sql(f"SELECT * FROM {self.table_name}", self.con)

    def save(self, data: pd.DataFrame) -> None:
        data.to_sql(self.table_name, self.con, if_exists="replace")


class SqliteStorage:
    """Store data using sqlite3 tables."""

    def __init__(self, db_filename: str) -> None:
        self.con = sqlite3.connect(db_filename)

    def use_table(self, table_name: str) -> TableStorage:
        return TableStorage(self.con, table_name)

    def close(self) -> None:
        self.con.commit()
        self.con.close()
