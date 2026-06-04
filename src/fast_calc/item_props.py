import csv
import os
import re
import unittest
from decimal import Decimal, ROUND_UP
from pprint import pprint

class ItemProperties:
    def __init__(self, path, extension='.txt', show_errors=False):
        self.item_db = {}
        self.errors_list = []
        self.read_files(path, extension)
        # self.read_item_properties_from('src/item_data/Саморезы.txt')
        if show_errors:
            print('\n'.join(self.errors_list))
        

    def read_files(self, path, extension):

        for filename in os.listdir(path):
            if filename.endswith(extension):
                self.read_item_properties_from(os.path.join(path, filename))

    def log_error(self, text):
        self.errors_list.append(text)

    def match_value_number(self, number):
        return (re.fullmatch('[0-9]+\.[0-9]+', number) or
                re.fullmatch('[0-9]+\.[0-9]*', number) or
                re.fullmatch('[0-9]*\.[0-9]+', number))
    
    def match_key(self, key_name):
        if not key_name[0].isalpha():
            return None
        return True

    def read_item_properties_from(self, filename, replace_comma=True):
        ratio = 1
        bname = os.path.basename(filename)
        if 'm1000' in bname:
            ratio = 1/1000
        if bname in self.item_db:
            self.log_error(f'Duplicated file \'{bname}\'. Skip')
            return
        # self.item_db[bname] = {}
        
        try:
            with open(filename, 'r', encoding='utf-8') as csv_file:
                reader = csv.reader(csv_file, delimiter='\t')
                for num, row in enumerate(reader, start=1):
                    k, v = row[0], row[1]
                    if len(k) == 0:
                        self.log_error(f'File \'{filename}\': L{num :03d} Empty line. Skip')
                        continue

                    if ',' in v:
                        v = v.replace(',', '.')
                        self.log_error(f'File \'{filename}\': L{num :03d} Replace comma to dot \'{k}\' = {v}')

                    if not self.match_value_number(v):
                        self.log_error(f'File \'{filename}\': L{num :03d} Wrong number \'{v}\'. Skip')
                        continue

                    if not self.match_key(k):
                        self.log_error(f'File \'{filename}\': L{num :03d} Wrong key \'{k}\'. Skip')
                        continue

                    if k in self.item_db:
                        self.log_error(f'File \'{filename}\': L{num :03d} Add duplicated key \'{k}\' = {v}')

                    self.item_db[k] = {'value': Decimal(Decimal(v) * Decimal(ratio)).quantize(Decimal('0.00001'), ROUND_UP).__str__(), 'file': bname}
                        
        except FileNotFoundError as e:
            print('Error: ', e)

    def get_weight_kv(self):
        kv = {}
        for item in self.item_db:
            kv[item] = self.item_db[item]['value']
        return kv
            
        
class TestItemPropertiesClass(unittest.TestCase, ItemProperties):
    def test_isupper(self):
        self.assertTrue('SMOKE'.isupper())
    
    def test_match_value_correct_number(self):
        for v in ('0.01', '.01', '10.', '0.019'):
            self.assertIsNotNone(self.match_value_number(v))

    def test_match_value_incorrect_number(self):
        for v in ('11.0.1','a.0', '1.a'):
            self.assertIsNone(self.match_value_number(v))
            

if __name__=='__main__':
    ip = ItemProperties(os.path.join('src', 'item_data'), extension='.txt', show_errors=False)
    pprint(ip.get_weight_kv())
    # unittest.main()
    
