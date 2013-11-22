import urllib
import re


def urls_in_str(urls_str, query_extract='none'):
    urls = set()
    i = urls_str.find(';http')
    while i >= 0:
        urls.add(urllib.unquote(urls_str[:i]))
        urls_str = urls_str[i + 1:]
        i = urls_str.find(';http')
    urls.add(urllib.unquote(urls_str))
    return urls


def n_grams(urls, ns, min_word_length=2, word_type='alphanumeric'):
    
    grams = set()
    for n in ns:
        for url in urls:
        
            if word_type == 'letters':
                sequence = re.findall(r"[a-zA-Z]{" + str(min_word_length) + ",}", url)  
            elif word_type == 'alphanumeric':
                sequence = re.findall(r"[a-zA-Z0-9]{" + str(min_word_length) + ",}", url)
            elif word_type == 'alphanumeric_':
                sequence = re.findall(r"[a-zA-Z0-9_]{" + str(min_word_length) + ",}", url)

            for i in range(len(sequence) - n + 1):
                grams.add('_'.join(sequence[i:i + n]).lower())

    return grams






def iterraw(segment, mode='all', files_n=1):
    """Iterator over dataset.
    
    Parameters:
        segment - string from ['gender_male', 'age_15_24', ...].
        mode - 'training' - only yield data items with CookieMod10 != 9,
               'test'     - only yield data items with CookieMod10 = 9,
               'all'      - yield all data items.
        files_n - integer, 0 < files_n < 48. Yield data from first
                  files_n files.

    iterraw() yields tuples (cookie_id, label, urls_visited,
                                                domains_visited_rtb), where
        cookie_id - CookieID,
        label - 1, if user belongs to the given segment, 0 otherwise,
        urls_visited - string of urls separated by ';',
        domains_visited_rtb - string of domains separated by ';'."""

    if mode == 'test':
        suffixes = ['ALL_MOD_9']
    elif mode == 'training' or mode == 'all':
        suffixes = ['000001', '000008', '000010', '000011', '000012', '000013',
                    '000014', '000015', '000016', '000017', '000018', '000019',
                    '000020', '000021', '000022', '000023', '000024', '000025',
                    '000026', '000027', '000028', '000029', '000030', '000031',
                    '000032', '000033', '000034', '000035', '000036', '000037',
                    '000038', '000039', '000040', '000041', '000042', '000043',
                    '000044', '000045', '000046', '000047', '000048', '000049',
                    '000066', '000067', '000068', '000069', '000071'][:files_n]

    for suffix in suffixes:
        filename = ('data/20131015_female/'
                    + '8191ca07-4888-4484-8bf6-44bdb7c66a77_' + suffix)
        f = open(filename, 'r')
        for line in f.readlines():
            
            (browser, os, screen_size, country, clicker, urls_visited,
                domains_visited_rtb, user_verticals, user_agent, cookie_mod_10,
                cookie_id, segments, negative, positive) = line.split('\t')
            
            if mode == 'training' and cookie_mod_10 == '9':
                continue
            elif mode == 'train' and cookie_mod_10 != '9':
                continue
            
            if segment in segments:
                label = 1
            elif segment[:segment.find('_')] in segments:
                label = 0
            else:
                continue

            cookie_id = int(cookie_id)

            yield (cookie_id, label, urls_visited, domains_visited_rtb)

        f.close()