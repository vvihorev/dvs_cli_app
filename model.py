import math
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TypeVar, TypedDict, Dict, NamedTuple, Tuple

import numpy as np
import pandas as pd


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


class Preferences(NamedTuple):
    base_vibration_level: float
    criterion: int


class VibrationsCalculator:
    """Sets up criterion for calculation, calls vibration prediction."""

    def __init__(self, preferences: Preferences, table_engines: pd.DataFrame):
        criteria = [FirstCriterion, SecondCriterion]
        self.criterion = criteria[preferences.criterion - 1](
            table_engines, preferences.base_vibration_level
        )

    def process_user_engine(self, engine: Engine) -> dict:
        self.criterion.engine_vibrations = self.criterion.predict(engine)
        return self.criterion.engine_vibrations


class Criterion(ABC):
    def __init__(self, table_engines: pd.DataFrame, base_vibration_level: float):
        self.table_engines = table_engines
        self.base_vibration_level = base_vibration_level

        self.regression_variables = ["a", "b"]
        self.results: CalculationResults = self.create_results_frames()
        self.engine_vibrations: Dict[str, float] = {}
        self.fit()

    def fit(self) -> None:
        """
        Calculates B,D, regression coefficients, and vibrations for given table
        of engines and stores Calculation Results in Criterion().results.
        """
        self.table_engines["omega"] = 0
        for group in self.table_engines.group.unique():
            df_group = self.table_engines[self.table_engines.group == group].copy()
            df_group["omega"] = self.get_omega(df_group)
            for frequency_count, frequency in enumerate(FREQUENCIES):
                b_d_results = self.calculate_B_D(df_group, frequency)
                a, b = self.linear_regression(b_d_results.B, b_d_results.D)
                V = self.predict_vibration(df_group, a, b)
                self.results.df_B_D[frequency][df_group.index] = b_d_results.B
                self.results.df_B_D["D"][df_group.index] = b_d_results.D
                self.results.df_regression.loc[f"Group {group}", frequency] = a, b
                self.results.df_vibrations.iloc[df_group.index, frequency_count] = V

    def predict(self, engine) -> Dict[str, float]:
        """
        Using regression coefficients for group of engines,
        predicts vibrations on each frequency for user engine.
        """
        engine_vibrations = {}
        df_group = self.table_engines[
            self.table_engines.group == engine["group"]
        ].copy()
        df_group["omega"] = self.get_omega(df_group)
        engine["omega"] = df_group["omega"].mean()
        df = pd.DataFrame([engine])
        for frequency in FREQUENCIES:
            # TODO: values are too large
            a, b = self.results.df_regression.loc[f'Group {engine["group"]}', frequency]
            engine_vibrations[frequency] = self.predict_vibration(df, a, b)[0] 
        return engine_vibrations

    def create_results_frames(self) -> CalculationResults:
        """
        Creates empty Calculations Results frames,
        frames for B_D and regression are created multiindexed.
        """
        arrays = [
            [f"Group {i // 2 + 1}" for i in range(8)],
            self.regression_variables * 4,
        ]
        df_regression = pd.DataFrame(index=arrays, columns=FREQUENCIES)
        df_B_D = pd.DataFrame(index=self.table_engines.name, columns=[*FREQUENCIES, "D"])
        df_vibrations = pd.DataFrame(index=self.table_engines.name, columns=FREQUENCIES)
        return CalculationResults(df_B_D, df_regression, df_vibrations)

    def get_omega(self, df_group: pd.DataFrame) -> float:
        """Calculates omega for given group of engines."""
        return df_group.nu.mean() * math.pi / 30

    @abstractmethod
    def calculate_B_D(self, df_frequency_group: pd.DataFrame, frequency: str) -> pd.DataFrame:
        """Calculates B and D vectors for engines of given group and frequency."""
        pass

    def linear_regression(self, x, y) -> Tuple[int]:
        """Calculates linear regression coefficients for input vectors."""
        A = np.vstack([x, np.ones(len(x))]).T
        a, b = np.linalg.lstsq(A, y, rcond=None)[0]
        return a, b

    @abstractmethod
    def predict_vibration(self, df_group: pd.DataFrame, a: float, b: float):
        """Predicts vibrations for engines of given group and frequency."""
        pass


class FirstCriterion(Criterion):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.regression_variables = ["C_1", "c"]

    def calculate_B_D(self, df_frequency_group: pd.DataFrame, frequency: str):
        """Calculates B and D vectors for engines of one group and one frequency"""
        df = df_frequency_group
        res = pd.DataFrame()
        res['B'] = -df.S_n * df.omega * df.N_max * df.delta / (df[frequency] * df.D_czb)
        res['D'] = -df.D_czvt / df.D_czb
        return res

    def predict_vibration(self, df, C_1, c):
        assert len(df.group.unique()) == 1, f"Usage: pass one group of engines at a time as 'df'"
        return (
            C_1
            * df.omega
            * df.S_n
            * df.N_max
            * df.delta
            / (c * df.D_czb + df.D_czvt)
        )


class SecondCriterion(Criterion):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.regression_variables = ["C_2", "k"]

    def calculate_B_D(self, df_frequency_group: pd.DataFrame, frequency: str):
        """Calculates B and D vectors for engines of one group and one frequency"""
        df = df_frequency_group
        res = pd.DataFrame()
        res["B"] = (
            df.S_n**2 * df.omega * df.D_c**2 * df.p_z / (df[frequency] * df.D_czb)
        )
        res["D"] = df.D_czvt / df.D_czb
        return res

    def predict_vibration(self, df: pd.DataFrame, C_2: float, k: float) -> pd.Series:
        """Calculates predicted vibrations for engines of one group and one frequency."""
        assert len(df.group.unique()) == 1, f"Usage: pass one group of engines at a time as 'df'"
        return (
            C_2
            * df.omega
            * df.S_n**2
            * df.D_c**2
            * df.p_z
            / (df.D_czvt + (-k) * df.D_czb)
        )


def assign_engine_group(nu: int) -> int:
    """Return engine group, based on 'nu' of the input engine."""
    groups = {1: (0, 500), 2: (500, 750), 3: (750, 1500), 4: (1500, 10000)}
    for group in groups.keys():
        if groups[group][0] <= nu < groups[group][1]:
            return group
    return 0
