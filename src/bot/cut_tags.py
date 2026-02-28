test = """Down.Periscope.1996.WEBRip.1080p.mkv
Locke & Key 1 - LostFilm.TV [1080p]
Ponies.S01E08.1080p.rus.LostFilm.TV.mkv
28.Years.Later.The.Bone.Temple.1080p.rus.LostFilm.TV.mkv
McHales Navy [1997 WEB-DL 1080p].mkv
Harry.Potter.and.the.Philosopher's.Stone.2001.WEB-DL.OKKO.SDR.2160p-SOFCJ.mkv
Harry.Potter.and.the.Chamber.of.Secrets.2002.Extended.Cut.BDRip.1080p-SOFCJ.mkv
Harry.Potter.and.the.Sorcerer’s.Stone.2001.Extended.Cut.BDRip.1080p-SOFCJ.mkv
Harry.Potter.and.the.Prisoner.of.Azkaban.2004.WEB-DL.OKKO.SDR.2160p-SOFCJ.mkv
Harry.Potter.and.the.Goblet.of.Fire.2005.BDRip.1080p-SOFCJ.mkv
Harry.Potter.and.the.Order.of.the.Phoenix.2007.BDRip.1080p-SOFCJ.mkv
Harry.Potter.and.the.Half-Blood.Prince.2009.WEB-DL.OM.1080p-SOFCJ.mkv
Harry.Potter.and.the.Deathly.Hallows.Part.2.2011.BDRip.1080p-SOFCJ.mkv
Harry.Potter.and.the.Deathly.Hallows.Part.1.2010.BDRip.1080p-SOFCJ.mkv
"""


def clean_symbols(text, change_to='.'):
    skip_symbols = (' ', '*', '[', ']', '(', ')', '-', '/', '\\')
    for symbol in skip_symbols:
        text = text.replace(symbol, change_to)
    return text

def text_clean_to_list(text):
    clean_text = '.'.join(clean_symbols(text).split('.'))
    
    cut_tags = ('1080p', 'WEB', 'DL', 'LostFilm','OKKO', 'WEBRip', 'mkv', 'TV', '2160p', 'sdr', 'webdl', 'rus', 'sofcj', 'bdrip', 'om')
    cut_tags_lower = tuple(t.lower() for t in cut_tags)
    split_lines = clean_text.split('\n')
    clean_list_split_dots = [[a for a in line.lower().split('.') if a not in cut_tags_lower] for line in split_lines]
    # print(clean_list_split_dots)
    clean_lines = [' '.join([word.capitalize() for word in line]) for line in  clean_list_split_dots if line[0]]
    return clean_lines

def get_numbered_clean_list(list_text):
    return [f'{e}. {l}' for e, l in enumerate(text_clean_to_list(test), start=1)]

if __name__ == '__main__':
    print('\n'.join(get_numbered_clean_list(test)))
