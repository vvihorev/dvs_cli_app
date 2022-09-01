import pandas as pd


class Storage:
    def __init__(self, file):
        self.file = file

    def load(self) -> pd.DataFrame:
        raise NotImplementedError

    def save(self, data: pd.DataFrame) -> None:
        raise NotImplementedError


class CsvStorage(Storage):
    """Хранение данных в файле csv"""

    def __init__(self, file: str):
        self.file = "data/" + file + ".csv"

    def load(self):
        return pd.read_csv(self.file)

    def save(self, data):
        data.to_csv(self.file, index=False)


class PostgresStorage(Storage):
    """Хранение данных в таблицах бд Postgres"""

    pass
