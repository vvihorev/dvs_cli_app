import math
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TypedDict

import numpy as np
import pandas as pd

from preferences import Preferences

FREQUENCIES = ["63", "140", "250", "500", "1000", "2000", "4000", "8000"]


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
    """
    Класс для расчета вибраций двигателя по заданному критерию. Рассчитывает
    вибрации для двигателя, также сохраняет столбцы B и D, значения
    коэффициентов регрессии для дебага.
    """
    def __init__(self, preferences: Preferences, engine_parameters: pd.DataFrame):
        criteria = (FirstCriterion, SecondCriterion)
        self.criterion = criteria[preferences.criterion - 1](
            engine_parameters, preferences.base_vibration_level
        )

    def get_engine_vibrations(self, engine: Engine) -> None:
        self.criterion.process_engine(engine)


class Criterion(ABC):
    def __init__(self, engine_parameters: pd.DataFrame, base_vibration_level: float):
        self.engine_parameters = engine_parameters
        self.base_vibration_level = base_vibration_level
        self.regression_variables = ["a", "b"]
        self.results: CalculationResults = self._create_multiindexed_frames()

    @abstractmethod
    def process_engine(self, engine: Engine) -> None:
        pass

    def _get_omega(self, df_group):
        return df_group.nu.mean() * math.pi / 30

    def _linear_regression(self, x, y):
        A = np.vstack([x, np.ones(len(x))]).T
        a, b = np.linalg.lstsq(A, y, rcond=None)[0]
        return a, b

    def _create_multiindexed_frames(self) -> CalculationResults:
        arrays = [
            [FREQUENCIES[i // 2] for i in range(len(FREQUENCIES) * 2)],
            ["B", "D"] * len(FREQUENCIES),
        ]
        df_B_D = pd.DataFrame(index=self.engine_parameters.name, columns=arrays)
        arrays = [
            [f"Group {i // 2 + 1}" for i in range(8)],
            self.regression_variables * 4,
        ]
        df_regression = pd.DataFrame(index=arrays, columns=FREQUENCIES)
        df_vibrations = pd.DataFrame(
            index=self.engine_parameters.name, columns=FREQUENCIES
        )
        return CalculationResults(df_B_D, df_regression, df_vibrations)


class FirstCriterion(Criterion):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.regression_variables = ["C_1", "c"]

    def process_engine(self, engine: Engine) -> None:
        pass

    def _calculate_B_D(self, df_frequency_group: pd.DataFrame, frequency: str):
        pass

    def _predict_vibration(self, df, C_2, k, frequency):
        pass


class SecondCriterion(Criterion):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.regression_variables = ["C_2", "k"]

    def process_engine(self, engine: Engine) -> None:
        self.engine_parameters["omega"] = 0
        for group in self.engine_parameters.group.unique():
            df_group = self.engine_parameters[
                self.engine_parameters.group == group
            ].copy()
            df_group["omega"] = self._get_omega(df_group)

            frequency_count = 0
            for frequency in FREQUENCIES:
                b_d_results = self._calculate_B_D(df_group, frequency)
                C_2, k = self._linear_regression(b_d_results.B, b_d_results.D)
                V = self._predict_vibration(df_group, C_2, k, frequency)

                self.results.df_B_D[frequency, "B"][df_group.index] = b_d_results.B
                self.results.df_B_D[frequency, "D"][df_group.index] = b_d_results.D
                self.results.df_regression.loc[f"Group {group}", frequency] = C_2, k
                self.results.df_vibrations.iloc[df_group.index, frequency_count] = V
                frequency_count += 1

        self.engine_parameters.loc[len(self.engine_parameters.index)] = engine

    def _calculate_B_D(self, df_frequency_group: pd.DataFrame, frequency: str):
        """Рассчитывает векторы B и D для одной полосы частот, по второму критерию."""
        df = df_frequency_group
        res = pd.DataFrame()
        res["B"] = (
            df.S_n**2 * df.omega * df.D_c**2 * df.p_z / (df[frequency] * df.D_czb)
        )
        res["D"] = df.D_czvt / df.D_czb
        return res

    def _predict_vibration(self, df, C_2, k, frequency):
        return C_2 * df.omega * df.S_n**2 * df.D_c**2 * df.p_z / (df.D_czvt + (-k) * df.D_czb)
