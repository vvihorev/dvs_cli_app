from typing import NamedTuple

from model import Engine, Criterion, assign_engine_group
from preferences import Preferences


class CLIInterface:
    def print_theory(self, criterion: int, display_width=80) -> None:
        """Выводит теорию по программе для заданного номера критерия"""
        with open(f"theory/criterion_{criterion}.txt", "r") as file:
            theory = file.read()
        for paragraph in theory.split("\n"):
            if paragraph[:2] == "# ":
                formatted_paragraph = self._center_text(paragraph[2:], display_width)
            elif paragraph[:2] == "eq":
                formatted_paragraph = self._center_text(paragraph[2:], display_width)
            else:
                formatted_paragraph = self._wrap_text(paragraph, display_width)
            formatted_paragraph += "\n"
            print(formatted_paragraph)

    def print_vibrations(self, criterion: Criterion):
        print(f"Прогнозные значения вибраций двигателя на частотных полосах:")
        for level in criterion.engine_vibrations.keys():
            print(f"{level}: {criterion.engine_vibrations[level][0]}")

    def get_preferences(self) -> Preferences:
        """Запрашивает у пользователя настройки программы"""
        base_vibration_level = float(input("Задайте базовый уровень вибрации в дБ: "))
        criterion = int(input("Задайте номер критерия для расчета (1, 2): "))
        print("\n")
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
        engine["group"] = assign_engine_group(int(engine["nu"]))
        print("\n")
        return engine

    def _center_text(self, text, display_width):
        output = ""
        if len(text) > display_width:
            text = self._wrap_text(text, display_width)
        for line in text.split("\n"):
            if len(output) > 0:
                output += "\n"
            padding = " " * ((display_width - len(line)) // 2)
            output += padding + line + padding
        return output

    def _wrap_text(self, text, display_width):
        lines = 0
        length = 0
        output = ""
        while length < len(text):
            for word in text.split(" "):
                length += len(word) + 1
                if length // display_width > lines:
                    lines += 1
                    output += "\n"
                output += word + " "
        return output
