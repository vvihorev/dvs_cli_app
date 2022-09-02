from abc import ABC, abstractmethod
import pandas as pd


class Storage(ABC):
    def __init__(self, file):
        self.file = file

    @abstractmethod
    def load(self) -> pd.DataFrame:
        raise NotImplementedError

    @abstractmethod
    def save(self, data: pd.DataFrame) -> None:
        raise NotImplementedError


class CsvStorage(Storage):
    """Хранение данных в файле csv"""

    def __init__(self, file: str):
        self.file = "data/" + file + ".csv"

    def load(self) -> pd.DataFrame:
        return pd.read_csv(self.file)

    def save(self, data):
        data.to_csv(self.file, index=False)


class PostgresStorage(Storage):
    """Хранение данных в таблицах бд Postgres"""

    pass
