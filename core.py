from dataclasses import dataclass
from config import Preferences
from typing import TypedDict
import pandas as pd


FREQUENCIES = ['63', '140', '250', '500', '1000', '2000', '4000', '8000']


class Engine(TypedDict):
    ID: int
    name: str
    N_e: float
    nu: float
    p_e: float
    p_z: float
    N_max: float
    delta: float
    D_czvt: float
    D_czb: float
    group: float
    S_n: float
    D_c: float
    f63: float
    f140: float
    f250: float
    f500: float
    f1000: float
    f2000: float
    f4000: float
    f8000: float


@dataclass
class CalculationResults:
    df_B_D: pd.DataFrame
    df_regression: pd.DataFrame
    df_vibrations: pd.DataFrame


class CriteriaCalculator:
    def __init__(self, preferences: Preferences, engine_parameters: pd.DataFrame):
        self.criterion = (
            FirstCriterion(engine_parameters, preferences.base_vibration_level),
            SecondCriterion(engine_parameters, preferences.base_vibration_level)
        )[preferences.criterion - 1]

    def get_engine_vibrations(self, engine: Engine):
        self.criterion.process_engine(engine)


class Criterion:
    def __init__(self, engine_parameters: pd.DataFrame, base_vibration_level: float):
        self.engine_parameters = engine_parameters
        self.base_vibration_level = base_vibration_level
        self.results: CalculationResults = self._create_multiindexed_frame(self.engine_parameters)

    def _get_omega(df_group):
        return df_group.nu.mean() * math.pi / 30

    def _linear_regression(x, y):
        A = np.vstack([x, np.ones(len(x))]).T
        a, b = np.linalg.lstsq(A, y, rcond=None)[0]
        return a, b 

    def _create_multiindexed_frame(engine_parameters: pd.DataFrame,
        regression_variables: list[str]) -> CalculationResults:
        arrays = [
            [FREQUENCIES[i // 2] for i in range(len(FREQUENCIES) * 2)],
            ['B', 'D'] * len(FREQUENCIES)
        ]
        df_B_D = pd.DataFrame(index=engine_parameters.name, columns=arrays)
        arrays = [
            [f'Group {i // 2 + 1}' for i in range(8)],
            regression_variables * 4
        ]
        df_regression = pd.DataFrame(index=arrays, columns=FREQUENCIES)
        df_vibrations = pd.DataFrame(index=engine_parameters.name, columns=FREQUENCIES)
        return CalculationResults(df_B_D, df_regression, df_vibrations)


class FirstCriterion(Criterion):
    def __init__(self, engine_parameters: pd.DataFrame, base_vibration_level: float):
        Criterion.__init__(self, engine_parameters, base_vibration_level)


class SecondCriterion(Criterion):
    def __init__(self, engine_parameters: pd.DataFrame, base_vibration_level: float):
        self.regression_variables = ['C_2', 'k']

    def process_engine(engine_parameters: pd.DataFrame, engine: Engine) -> CalculationResults:
        engine_parameters['omega'] = 0
        for group in engine_parameters.group.unique():
            df_group = engine_parameters[engine_parameters.group == group].copy()
            df_group['omega'] = _get_omega(df_group)

            for frequency in FREQUENCIES:
                b_d_results = _calculate_B_D(df_group, frequency)
                C_2, k = _linear_regression(b_d_results.B, b_d_results.D)
                V = _predict_vibration(df_group, C_2, k)
                
                self.results.df_B_D[frequency, 'B'][df_group.index] = b_d_results.B
                self.results.df_B_D[frequency, 'D'][df_group.index] = b_d_results.D
                self.results.df_regression.loc[f'Group {group}', frequency] = C_2, k
                self.results.df_vibration.iloc[df_group.index] = V

    def _calculate_B_D(engine_parameters: pd.DataFrame, frequency: str):
        """ Рассчитывает векторы B и D для одной полосы частот, по второму критерию. """
        res = pd.DataFrame()
        res['B'] = df.S_n**2 * df.omega * df.D_c**2 * df.p_z / (df[frequency] * df.D_czb)
        res['D'] = df.D_czvt / df.D_czb
        return res

    def _predict_vibration(df, C_2, k):
        res = pd.DataFrame()
        for frequency in FREQUENCIES:
            res[frequency] = C_2 * df.omega * df.S_n**2 * df.D_c**2 * df.p_z / (df.D_czvt + (-k) * df.D_czb)
        return res


if __name__ == "__main__":
    import storage
    preferences = Preferences(86, 2)
    engine_data = storage.CsvStorage('data/base_engines.csv').load()
    engine = engine_data.iloc[1,].to_dict()
    cc = CriteriaCalculator(preferences, engine_data)
