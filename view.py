from typing import NamedTuple

from model import Engine, Criterion


class CLIInterface:
    def print_theory(self, criterion: int) -> None:
        """Выводит теорию по программе для заданного номера критерия"""
        with open(f"theory/criterion_{criterion}.txt", "r") as file:
            theory = file.read()
        print(theory)


    def print_vibrations(self, criterion: Criterion):
        print(criterion.results.df_vibrations)


    def get_preferences(self) -> Preferences:
        """Запрашивает у пользователя настройки программы"""
        base_vibration_level = float(input("Задайте базовый уровень вибрации в дБ: "))
        criterion = int(input("Задайте номер критерия для расчета (1, 2): "))
        return Preferences(base_vibration_level, criterion)


    def get_engine(self) -> Engine:
        """Запрашивает у пользователя данные двигателя"""
        engine = Engine()
        print("\nВведите данные двигателя:")
        engine["name"] = input("Марка: ")

        engine_parameters = {
            "nu": "Частота вращения n: ",
            "N_e": "Эффективная мощность N_e: ",
            "p_e": "Среднее эффективное давление p_e: ",
            "p_z": "Максимальное давление цикла p_z: ",
            "S_n": "Ход поршня S_n: ",
            "N_max": "Максимальное значение боковой силы N_max: ",
            "delta": "Зазор между поршнем и втулкой delta: ",
            "D_czb": "Жесткость блока цилиндров D_czb: ",
            "D_czvt": "Жесткость втулки D_czvt: ",
            "D_c": "Диаметр цилиндра D_c: ",
        }

        for brief_name in engine_parameters:
            engine[brief_name] = float(input(f"{engine_parameters[brief_name]}: "))
        engine["group"] = self._assign_engine_group(int(engine["nu"]))
        return engine


    def _assign_engine_group(self, nu: int) -> int:
        """Определяет номер группы двигателя по частоте вращения вала"""
        groups = {1: (0, 500), 2: (500, 750), 3: (750, 1500), 4: (1500, 10000)}
        for group in groups.keys():
            if groups[group][0] <= nu < groups[group][1]:
                return group
        return 0

