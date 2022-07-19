import pandas as pd


class Storage():
    def __init__(self, file):
        self.file = file

    def load(self) -> pd.DataFrame:
        raise NotImplementedError

    def save(self, data: pd.DataFrame) -> None:
        raise NotImplementedError


class CsvStorage(Storage):
    """Хранение данных в файле csv"""

    def __init__(self, file_path: str):
        self.file_path = file_path

    def load(self):
        return pd.read_csv(self.file_path)

    def save(self, data):
        data.to_csv(self.file_path, index=False)


class PostgresStorage(Storage):
    """Хранение данных в таблицах бд Postgres"""
    pass


if __name__ == "__main__":
    storage = CsvStorage("data/base_engines.csv")
    data = storage.load()
    print(data.columns)
    storage.save(data)
