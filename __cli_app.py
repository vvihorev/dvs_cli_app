import pandas as pd
import cli_display
import __calculate as calculate


def get_calculations(df, save_calculations=False):
    df['omega'] = 0
    for group in df.group.unique():
        df_group = df[df.group == group].copy()
        df_group['omega'] = calculate.get_omega(df_group)

        for frequency in calculate.FREQUENCIES:
            _res = calculate.second_criteria_B_D(df_group, frequency)
            C_2, k = calculate.linear_regression(_res.B, _res.D)
            V = calculate.second_criteria_predict_vibration(df_group, C_2, k)
            
            df_B_D[frequency, 'B'][df_group.index] = _res.B
            df_B_D[frequency, 'D'][df_group.index] = _res.D
            df_regression.loc[f'Group {group}', frequency] = C_2, k
            df_vibration.iloc[df_group.index] = V

    if save_calculations:
        df_B_D.to_excel('output/B_D.xlsx')
        df_regression.to_excel('output/regression.xlsx')
        df_vibration.to_excel('output/vibration.xlsx')

    return {'B_D': df_B_D, 'regression': df_regression, 'vibration': df_vibration}


def main():
    engine_data = cli_display.get_engine()
    engine_data['group'] = cli_display._assign_engine_group(engine_data['nu'])
    base_data = get_calculations(pd.read_csv('data/base_engines.csv'), save_calculations=True)


if __name__ == "__main__":
    main()
