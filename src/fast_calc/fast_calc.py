from tabulate import tabulate
from decimal import Decimal, ROUND_UP
from os import getcwd
import re
from item_ordering import ordering, weight
import time


class FastTabCalcError(Exception):
    def __init__(self, m):
        print(f'message: {m}')
        print(f'no result given')


class FastTabCalc:
    def __init__(self, tabulated_text, node_symbol='#'):
        self.node_symbol = node_symbol
        self.ordering_list = [(a[0], a[1].lower()) for a in enumerate(ordering)]
        # print(self.ordering_list)
        self.norm_weights = self.read_weights()

        clean_text_lines = self.skip_useless_lines(tabulated_text)
        il = self.list_indents(clean_text_lines)
        tree = self.expand_tree(il)
        sdt, nodes = self.normilize_tree(tree)
        self.nodes = nodes
        totals = self.collapse_totals(sdt)

        self.result_string = self.get_totals_but_nodes_tabulated(totals, nodes)

    def read_weights(self):
        norm_weights = {}
        for k in weight:
            norm_weights[k.lower().replace(' ', '')] = weight[k]
        return norm_weights


    def skip_useless_lines(self, string_text):
        clean_text_lines = []
        line_counter = 1
        for line in string_text.split('\n'):
            a = len(line)
            b = line.count('\t')
            c = line.count(' ')
            if a == b+c:
                continue
            if len(line) - len(line.lstrip(' ')):
                raise FastTabCalcError(f'Error: l:{line_counter} check spaces: {line.replace(" ", ".")}')

            l = line.rstrip(' ').rstrip('\t')
            clean_text_lines.append(l)
            line_counter+=1
        return clean_text_lines

    def list_indents(self, clean_text_lines):
        return [[len(s)-len(s.lstrip('\t')), s.lstrip('\t')] for s in clean_text_lines]

    def expand_tree(self, lines):
        family = [lines[0].copy()]
        dirty_tree = []
        for line__ in lines[1:]:
            # last = False
            # TODO !!!!!!!!
            line = [line__[0], re.sub('\t+', '\t', line__[1])]
            try:
                if line[0] > family[-1][0]:
                    dirty_tree.append(family.copy())
                    family.append(line.copy())
                else:
                    dirty_tree.append(family.copy())
                    while line[0] <= family[-1][0]:
                        family.pop()
                    family.append(line)
            except IndexError:
                raise FastTabCalcError(f'lines {lines}, family {family}')
                # last = True
        # if last:
        dirty_tree.append(family.copy())

        return [[(dirty_p[1].split('\t')) for dirty_p in path] for path in dirty_tree]

    def split_item_with_units(self, item : str):
        """ 123.231шт. split to => 123.231 шт """
        
        pat = r'\d+\.?\d*\s*' 
        decimal = ''
        try:
            decimal = re.match(pat, item.replace(',', '.'))[0]
        except UnboundLocalError as u:
            print(item, u)
        except TypeError as e:
            print(item, e)
        return Decimal(decimal), item.replace(decimal, '')

    def normilize_tree(self, tree, default=1):
        nodes = set()
        for path in tree:
            for item in path:
                try:
                    clean_item, _ = self.split_item_with_units(item[1].strip('\t'))
                    item[1] = clean_item
                    if item[0].startswith(self.node_symbol):
                        nodes.add(item[0])
                except IndexError:
                    nodes.add(item[0])
                    item.append(default)
        return tree, nodes

    def calc_last_item(self, path: list):
        key = path[-1][0]
        value = 1
        for item in path:
            value*=item[1]
        return (key, value)


    def collapse_totals(self, expanded_tree: list):
        totals = {}
        for path in expanded_tree:
            k, v = self.calc_last_item(path)
            try:
                totals[k] += v
            except KeyError:
                totals[k] = v
        return totals
    
    def get_priority(self, item):
        try:
            return [item[0].lstrip(self.node_symbol).lower().startswith(x[1]) for x in self.ordering_list].index(True)
        except ValueError:
            return 1000
    def get_weight(self, name, qty):
        # print(name in weight, name, weight)
        clean_name = name.lower().replace(' ', '')
        if clean_name in self.norm_weights:
            return Decimal(Decimal(self.norm_weights[clean_name])*Decimal(qty)).quantize(Decimal('0.1'), ROUND_UP)
        return 0

    def get_totals_but_nodes_tabulated(self, data_dict, nodes):
        l = [(k, data_dict[k], self.get_weight(k, data_dict[k])) for k in data_dict if k not in nodes]
        l.sort(key = lambda k: self.get_priority(k))
        return tabulate(l, 
                    headers=('Наименование', 'Кол.', 'Вес, кг'))
    
    def __str__(self):
        return self.result_string


if __name__ == '__main__':
    try:
        text = ''
        try:
            with open('test_calc.txt', 'r', encoding='UTF-8') as txt:
                text = txt.read().split('ИТОГО')[0].rstrip('\n')
        
        except FileNotFoundError as e:
            print(getcwd())
            input(e)
            
        x = FastTabCalc(text, node_symbol='#')
        with open('test_calc.txt', 'w', encoding='UTF-8') as txt:
            txt.write(text)
            txt.write('\n\nИТОГО\t'+ time.strftime("%Y-%m-%d %H:%M")+ '\n\n')

            txt.write(','.join([a[1] for a in x.ordering_list])+'\n' +'\n')
            txt.write(x.__str__())


        
    except FastTabCalcError as e:
        x = None
