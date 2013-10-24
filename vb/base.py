from sys import stderr
import cPickle as pickle
import urlparse
import urllib
import urllib2
import re
from collections import Counter

import numpy as np
from scipy import sparse

    

def urls_in_url(url = '', query=True):
    if query:
        matches = re.findall(r'=(http[s]?(?:(?::)|(?:%3A))(?:(?:/)|(?:%2F)){2}[^&;]*)', url)
    else:
        matches = re.findall(r'=(http[s]?(?:(?::)|(?:%3A))(?:(?:/)|(?:%2F)){2}(?:(?!%3F|%3D)[^&;?=])*)', url)
    if matches:
        for url in matches:
            yield urllib2.unquote(url)
    else:
        yield url


def n_grams(n, urls_str):
    grams = set()
    urls = '_'.join(re.findall(r"[a-zA-Z]{2,}", urls_str))
    urls = re.split(r"_?https?_?", urls)
    for url in urls:
        if url:
            words = url.split('_')
            for i in range(len(words) - n + 1):
                grams.add('_'.join(words[i:i + n]))
    return grams
    
        

def iterraw(label, set='training', files_n=1):
    if set == 'training':
        suffixes = ['000001', '000008', '000010', '000011', '000012', '000013',
                    '000014', '000015', '000016', '000017', '000018', '000019',
                    '000020', '000021', '000022', '000023', '000024', '000025',
                    '000026', '000027', '000028', '000029', '000030', '000031',
                    '000032', '000033', '000034', '000035', '000036', '000037',
                    '000038', '000039', '000040', '000041', '000042', '000043',
                    '000044', '000045', '000046', '000047', '000048', '000049',
                    '000066', '000067', '000068', '000069', '000071'][:files_n]
    else:
        suffixes = ['ALL_MOD_9']
        
    for suffix in suffixes:
        filename = 'data/20131015_female/8191ca07-4888-4484-8bf6-44bdb7c66a77_' + suffix
        f = open(filename, 'r')
        for line in f.readlines():
            (browser, os, screensize, country, clicker, urls, domains,
                verticals, agent, cookiemod, id, segments, negative,
                positive) = line.split('\t')
            segments = segments.split(';')
            if ((set == 'training' and cookiemod == '9')
                        or (set == 'test' and cookiemod != '9')):
                continue
            if label in segments:
                 label_class = 1
            elif label.split('_', 1)[0] in [x.split('_', 1)[0] for x in segments]:
                label_class = 0
            else:
                continue
                
            id = int(id)
            
            yield (id, label_class, urls, domains)

def iterprod2(label, set='training', files_n=1):
    if set == 'training':
        suffixes = ['000001', '000008', '000010', '000011', '000012', '000013',
                    '000014', '000015', '000016', '000017', '000018', '000019',
                    '000020', '000021', '000022', '000023', '000024', '000025',
                    '000026', '000027', '000028', '000029', '000030', '000031',
                    '000032', '000033', '000034', '000035', '000036', '000037',
                    '000038', '000039', '000040', '000041', '000042', '000043',
                    '000044', '000045', '000046', '000047', '000048', '000049',
                    '000066', '000067', '000068', '000069', '000071'][:files_n]
    else:
        suffixes = ['ALL_MOD_9']
        
    for suffix in suffixes:
        filename = 'data/20131015_female/8191ca07-4888-4484-8bf6-44bdb7c66a77_' + suffix
        f = open(filename, 'r')
        for line in f.readlines():
            (browser, os, screensize, country, clicker, urls, domains,
                verticals, agent, cookiemod, id, segments, negative,
                positive) = line.split('\t')
            segments = segments.split(';')
            if ((set == 'training' and cookiemod == '9')
                        or (set == 'test' and cookiemod != '9')):
                continue
            if label in segments:
                 label_class = 1
            elif label.split('_', 1)[0] in [x.split('_', 1)[0] for x in segments]:
                label_class = 0
            else:
                continue
                
            id = int(id)
            history = []
            if urls:
                urls = re.split(';https?://', urls)
                for x in urls_in_url(urls[0]):
                    if x[-1] == '/':
                        x = x[:-1]
                    history.append(x)
                for url in urls[1:]:
                    for x in urls_in_url('http://' + url):
                        #######################################
                        if len(x) == 0:
                            print url
                        #######################################
                        if x[-1] == '/':
                            x = x[:-1]
                        history.append(x)
            for domain in domains.split(';'):
                history.append('http://' + domain)
            yield (id, label_class, history)



def iterprod(label, set='training', files_n=1):
    if set == 'training':
        suffixes = ['000001', '000008', '000010', '000011', '000012', '000013',
                    '000014', '000015', '000016', '000017', '000018', '000019',
                    '000020', '000021', '000022', '000023', '000024', '000025',
                    '000026', '000027', '000028', '000029', '000030', '000031',
                    '000032', '000033', '000034', '000035', '000036', '000037',
                    '000038', '000039', '000040', '000041', '000042', '000043',
                    '000044', '000045', '000046', '000047', '000048', '000049',
                    '000066', '000067', '000068', '000069', '000071'][:files_n]
    else:
        suffixes = ['ALL_MOD_9']
        
    for suffix in suffixes:
        filename = 'data/20131015_female/8191ca07-4888-4484-8bf6-44bdb7c66a77_' + suffix
        f = open(filename, 'r')
        for line in f.readlines():
            (browser, os, screensize, country, clicker, urls, domains,
                verticals, agent, cookiemod, id, segments, negative,
                positive) = line.split('\t')
            segments = segments.split(';')
            if ((set == 'training' and cookiemod == '9')
                        or (set == 'test' and cookiemod != '9')):
                continue
            if label in segments:
                 label_class = 1
            elif label.split('_', 1)[0] in [x.split('_', 1)[0] for x in segments]:
                label_class = 0
            else:
                continue
                
            id = int(id)
            history = []
            if urls:
                urls = re.split(';https?://', urls)
                if urls[0][-1] == '/':
                    urls[0] = urls[0][:-1]
                history.append(urls[0])
                for url in urls[1:]:
                    if url[-1] == '/':
                        url = url[:-1]
                    history.append('http://' + url)
            for domain in domains.split(';'):
                history.append('http://' + domain)
            yield (id, label_class, history)
            

def iterdata(label, set='training'):
    """Iterator over Adform demography training or test dataset.
    
    iterdata() yields tuples (id, class, history), where

        id is unique user's cookie id,

        class equals to
            1, if user falls under the given label,
            0  otherwise,

        history is a Counter() object of visited URLs.
        
    Iterator skips users with unknown label class (e.g.,
    iterdata('gender_female') would not yield users whose
    gender is unknown).
    """
    
    if set == 'training':
        data = pickle.load(open('data/data.p', 'rb'))
    else:
        data = pickle.load(open('data/data_test.p', 'rb'))

    category, label = label.split('_', 1)
    for id, labels, history in data:
        if category in labels:
            if labels[category] == label:
                yield id, 1, history
            else:
                yield id, 0, history


def to_matrix(data, features_map):
    
    items_num = len(data)
    features_num = len(features_map)
    X = sparse.lil_matrix((items_num, features_num), dtype=np.float)
    y = np.empty((items_num, ), dtype=np.int)

    i = 0
    for id, label, feature_values in data:
        y[i] = label
        for feature, value in feature_values:
            if feature in features_map:
                X[i, features_map[feature]] = value
        i += 1
    
    return sparse.csr_matrix(X), y



def url_prefixes(url):
    """Iterator, best explained by example:
    
    url_prefixes('http://full.domain.com/one/two?three=x')
    would yield
        'http://full.domain.com/one/two?three=x'
        'http://full.domain.com/one/two'
        'http://full.domain.com/one'
        'http://full.domain.com'
    """
    
    url = urlparse.urlparse(url)
    if url.params or url.query or url.fragment:
        yield urlparse.urlunparse(url)
    path = url.path.replace('/', ' ').split()
    for num in range(len(path), -1, -1):
        yield urlparse.urlunparse((url.scheme, url.netloc
                                   , '/'.join(path[:num]), '', '', ''))

def url_prefix(url, depth=0):
    """Returns url with shortened path (only _depth_ number
    of folders in path)."""
    url = urlparse.urlparse(url)
    path = url.path.replace('/', ' ').split()
    if depth > len(path):
        return urlparse.urlunparse(url)
    else:
        return urlparse.urlunparse((url.scheme, url.netloc
                                    , '/'.join(path[:depth]), '', '', ''))
