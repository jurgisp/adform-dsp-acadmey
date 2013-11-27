import re
from collections import Counter
import itertools
import cPickle as pickle
import operator as op
import string
from sys import stderr
import argparse
import scipy.sparse as sparse

from read_history import produrator, get_domain

def cut_get (url):
    if url.find('?') != -1:
	url = url[:url.find('?')]
    return re.sub(r'([/?]*)$', '', url)

def generate (url = '', bigram_regex='', b1 = 0, b2 = 0, url_path = 0, get = 0):
    if not get:
        url = cut_get(url)
 
    matches = re.findall(bigram_regex, url)
    
    for i, m in enumerate(matches):
        matches[i] = m.lower()

    if b2:
        for i in range(len(matches)-1):
            yield matches[i] + '_' + matches[i+1]
    if b1:
        for i in matches:
            yield i
    
    if url_path:
        yield url
        url = cut_get(url)
        yield url
        while (url.rfind('/') != -1):
            url = url[:url.rfind('/')]
            yield url


                    
def to_sparse (data, length):
    print len(data), length
    X, Y = sparse.lil_matrix((len(data), length)), []
    for i, point in enumerate(data):
        Y.append(point[1])
        for u in point[2]:
            X[i, u] = 1
    return X, Y

def gen_data (classifier, regex='', b1 = 0, b2 = 0, url_path=0, get = 0, add_adv = 0, lower_pop_bound=0, n_files=47):
    train, test = 0, 0
    features = Counter()
    
    stderr.write("Reading features...\n")
    for id, label, history in produrator (classifier, adv_url = add_adv, n_files = n_files):
        train += 1
        s = set()
        for url in history:
            for u in generate(url, regex, b1, b2, url_path, get):
                s.add(u)
        for url in s:
            features[url] += 1
    
    stderr.write("Enumerating features...\n")

    features = set([f for f, c in features.iteritems()
				 if c > lower_pop_bound])
    features_map = dict([(f,c) for c, f in enumerate(features)])
   
    stderr.write("Counting testing...\n")
    for id, label, history in produrator(classifier, set='testing', adv_url = add_adv, n_files = n_files):
        test += 1

    
    stderr.write("Training set...\n")
    i, X, Y = 0, sparse.lil_matrix((train, len(features))), []
    for id, label, history in produrator(classifier, adv_url = add_adv, n_files = n_files):
        Y.append(label)
        s = set()
        for url in history:
            for u in generate(url, regex, b1, b2, url_path, get):
                if u in features:
                    s.add(features_map[u])
        for u in s:
            X[i, u] = 1
        i += 1
    X = sparse.csr_matrix(X)
    
    stderr.write("Test set...\n")
    i, Xt, Yt = 0, sparse.lil_matrix((test, len(features))), []
    for id, label, history in produrator(classifier, set='testing', adv_url = add_adv, n_files = n_files):
        Yt.append(label)
        s = set()
        for url in history:
            for u in generate(url, regex, b1, b2, url_path, get):
                if u in features:
                    s.add(features_map[u])
        for u in s:
            Xt[i, u] = 1
        i += 1
    Xt = sparse.csr_matrix(Xt)
    stderr.write("Train: %d, Test: %d, Features: %d\n" % (train, test, len(features)))

    del features

    return X, Y, Xt, Yt, features_map
