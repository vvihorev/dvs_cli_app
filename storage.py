import pandas as pd


class Storage:
    def __init__(self, file):
        self.file = file

    def load(self):
        raise NotImplementedError

    def save(self):
        raise NotImplementedError


class CsvStorage(Storage):
    """ Хранение данных в файле csv """
    def __init__(self, file):
        self.file = file

    def load(self) -> pd.DataFrame:
        return pd.read_csv(self.file)

    def save(self, data: pd.DataFrame) -> None:
        data.to_csv(self.file, index=False)


if __name__ == "__main__":
    storage = CsvStorage("data/base_engines.csv")
    data = storage.load()
    print(data.columns)
    storage.save(data)
