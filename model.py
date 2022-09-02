import math
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

    def calculate_engine_vibrations(self, engine: Engine) -> None:
        self.criterion.predict_group_vibrations()
        self.criterion.engine_vibrations = (
            self.criterion.calculate_engine_vibrations_prediction(engine)
        )


class Criterion:
    def __init__(self, engine_parameters: pd.DataFrame, base_vibration_level: float):
        self.engine_parameters = engine_parameters
        self.base_vibration_level = base_vibration_level
        self.regression_variables = ["a", "b"]
        self.results: CalculationResults = self._create_multiindexed_frames()

    def predict_group_vibrations(self) -> None:
        """Calculates B, D, regression coefficients, and vibrations for groups of engines on all frequencies."""
        self.engine_parameters["omega"] = 0
        for group in self.engine_parameters.group.unique():
            df_group = self.engine_parameters[
                self.engine_parameters.group == group
            ].copy()
            df_group["omega"] = self._get_omega(df_group)
            frequency_count = 0
            for frequency in FREQUENCIES:
                b_d_results = self._calculate_B_D(df_group, frequency)
                a, b = self._linear_regression(b_d_results.B, b_d_results.D)
                V = self._predict_vibration(df_group, a, b, frequency)
                self.results.df_B_D[frequency, "B"][df_group.index] = b_d_results.B
                self.results.df_B_D[frequency, "D"][df_group.index] = b_d_results.D
                self.results.df_regression.loc[f"Group {group}", frequency] = a, b
                self.results.df_vibrations.iloc[df_group.index, frequency_count] = V
                frequency_count += 1

    def calculate_engine_vibrations_prediction(self, engine):
        engine_vibrations = {}
        df_group = self.engine_parameters[
            self.engine_parameters.group == engine["group"]
        ].copy()
        df_group["omega"] = self._get_omega(df_group)
        engine["omega"] = df_group["omega"].mean()
        df = pd.DataFrame([engine])
        for frequency in FREQUENCIES:
            a, b = self.results.df_regression.loc[f'Group {engine["group"]}', frequency]
            engine_vibrations[frequency] = self._predict_vibration(df, a, b, frequency)
        return engine_vibrations

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

    def _calculate_B_D(self, df_frequency_group: pd.DataFrame, frequency: str):
        pass

    def _predict_vibration(self, df, C_2, k, frequency):
        pass


class SecondCriterion(Criterion):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.regression_variables = ["C_2", "k"]

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
        return (
            C_2
            * df.omega
            * df.S_n**2
            * df.D_c**2
            * df.p_z
            / (df.D_czvt + (-k) * df.D_czb)
        )


def assign_engine_group(nu: int) -> int:
    """Определяет номер группы двигателя по частоте вращения вала"""
    groups = {1: (0, 500), 2: (500, 750), 3: (750, 1500), 4: (1500, 10000)}
    for group in groups.keys():
        if groups[group][0] <= nu < groups[group][1]:
            return group
    return 0
