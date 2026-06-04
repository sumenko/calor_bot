import os
import re

weight = {
    'Гв.ерш.4,2-40': 0.0036,
    'Смр.4,5-40':	0.00282,
    'Смр.4,5-45':	0.00309,
    'Смр.4,5-50':	0.0034,
    'Смр.4,5-60':	0.00403,
    'Смр.4,5-70':	0.0046,
    'Смр.4,5-80':	0.0052,

    'Смр.5-40': 0.00423,


    'Шайба 12': 0.00423,
    'Шайба 16': 0.011295,
    'Шайба 20': 0.017156,
    'Шайба ув.16': 0.041,
    'Шайба ув.20': 0.078,
    
    'Гайка колп. М16': 0.0578,
    'Гайка колп. М20': 0.10213,
    'Гайка М16': 0.03761,
    'Гайка М20': 0.07144,
}


class ManageSettings:
    def __init__(self):
        self.ordering_list = []
        work_dir = '' #os.path.join('src', 'fast_calc')
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
            print(f'File not found: {fname} in {os.getcwd()}' )


if __name__ == "__main__":
    ms = ManageSettings()

