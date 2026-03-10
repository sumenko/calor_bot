import os
import re

weight = {
    'Гв.ерш.4,2-40': 0.0036,
    'Смр.5-40': 0.0026,
    'Шайба 16': 0.0026,
    'Шайба ув.16': 0.0026,
    'Шайба ув.20': 0.0026,
    'Гайка колп. М20': 0.10213,
    'Гайка колп. М16': 0.0578,
}


class ManageSettings:
    def __init__(self):
        self.ordering_list = []
        work_dir = '' #os.path.join('src', 'fast_calc')
        self.read_weight(os.path.join(work_dir, 'settings_ordering.txt'))
        self.read_ordering(os.path.join(work_dir, 'settings_ordering.txt'))

    def clean_data(self, text : str):
        return re.sub('\s+', '\n', text).strip().split('\n')

    def read_ordering(self, fname):
        try:
            with open(fname, 'r', encoding='utf-8') as inp:
                lines = self.clean_data(inp.read())
                self.ordering_list = lines
                # print(lines)
        except FileNotFoundError:
            print(f'File not found:{fname} in ', os.getcwd())

    def read_weight(self, fname):
        pass


if __name__ == "__main__":
    ms = ManageSettings()

