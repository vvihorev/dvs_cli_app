import pandas as pd
import numpy as np
import math


FREQUENCIES = ['63', '140', '250', '500', '1000', '2000', '4000', '8000']


def second_criteria_B_D(df: pd.DataFrame, frequency: str):
    """ Рассчитывает векторы B и D для одной полосы частот, по второму критерию.
        В 'df' должны быть столбцы: S_n, omega, D_c, p_z, V, D_czb, D_czvt """
    res = pd.DataFrame()
    res['B'] = df.S_n**2 * df.omega * df.D_c**2 * df.p_z / (df[frequency] * df.D_czb)
    res['D'] = df.D_czvt / df.D_czb
    return res


def second_criteria_predict_vibration(df, C_2, k):
    res = pd.DataFrame()
    for frequency in FREQUENCIES:
        res[frequency] = C_2 * df.omega * df.S_n**2 * df.D_c**2 * df.p_z / (df.D_czvt + (-k) * df.D_czb)
    return res


def get_omega(df_group):
    return df_group.nu.mean() * math.pi / 30


def linear_regression(x, y):
    A = np.vstack([x, np.ones(len(x))]).T
    a, b = np.linalg.lstsq(A, y, rcond=None)[0]
    return a, b 
