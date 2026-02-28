from time import process_time
from mock_data import td_mock
from pprint import pprint

class TagsContainer:
    def __init__(self):
        self.tag_file_name = 'list_tags.txt'
        self.cut_tags = self.read_tags()
        self.sort_tags()

    def tags_list(self):
        return self.cut_tags
    
    def sort_tags(self):
        self.cut_tags.sort()

    def read_tags(self):
        with open(self.tag_file_name, 'r') as tags_file:
            return [t.lower().replace('_', ' ') for t in tags_file.read().split()]

    def flush_tags(self):
        with open(self.tag_file_name, 'w') as tags_file:
            tags_file.write(' '.join(self.cut_tags))

    def add_tag(self, tag, flush=False):
        if not tag in self.cut_tags:
            self.cut_tags.append(tag)
            if flush:
                self.flush_tags()
            return True
        return False

    def rm_tag(self, tag, flush=False):
        if tag in self.cut_tags:
            self.cut_tags.pop(self.cut_tags.index(tag))
            if flush:
                self.flush_tags()
            return True
        return False


class TorrentFileNameCleaner(TagsContainer):
    def clean_symbols(self, text, change_to=' '):
        skip_symbols = ('.', '*', '[', ']', '(', ')', '-', '/', '\\')
        for symbol in skip_symbols:
            text = text.replace(symbol, change_to)
        return text

    def clean_line(self, text):
        result = text
        # print('Clean: ', text, ' => ', end='')
        for tag in self.cut_tags:
            result = result.replace(tag, '')
        # print(result)
        return result

    def text_clean_to_list(self, text):
        clean_text = ' '.join(self.clean_symbols(text).split(' '))
        cut_tags = self.tags_list()
        cut_tags_lower = tuple(t.lower() for t in cut_tags)
        split_lines = clean_text.split('\n')
        clean_lines = []
        for line in split_lines:
            clean_lines.append(self.clean_line(line.lower()))
        # clean_list_split_dots = [[a for a in line.lower().split('.') if a not in cut_tags_lower] for line in split_lines]
        # clean_lines = [' '.join([word.capitalize() for word in line]) for line in  clean_list_split_dots if line[0]]
        return clean_lines

    def get_numbered_clean_list(self, list_text):
        return [f'{e}. {l}' for e, l in enumerate(self.text_clean_to_list(list_text), start=1) if l != '']
    
    def get_clean_numbered_text(self, text):
        return '\n'.join(self.get_numbered_clean_list(text))


if __name__ == '__main__':

    test = td_mock
    tfc = TorrentFileNameCleaner()

    # print(tfc.tags_list())
    print(tfc.get_clean_numbered_text(test))
    # print(tfc.clean_line('locke & key 1   lostfilm tv  1080p'))

