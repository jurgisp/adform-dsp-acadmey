from collections import Counter
import re

import numpy
from scipy import sparse

from base import *


def item_features(urls_str, domains_str,
                  ngram_ns, min_word_length, word_type,
                  use_urls, min_url_depth):

    itemfeat = set()
    
    urls = [x[x.find('//') + 2:] for x in urls_in_str(urls_str)]
    urls += domains_str.split(';') 
    for x in n_grams(urls, ngram_ns, min_word_length, word_type):
        itemfeat.add(x)

    if not use_urls:
        return itemfeat
        
    for url in urls:
        i = min(url.find('?'), url.find(';'))
        if i != -1:
            parts = url[:i].split('/') + [url[i:]]
        else:
            parts = url.split('/')
        if min_url_depth <= 0:
            min_url_depth = len(parts) + min_url_depth 
        for i in range(min_url_depth, len(parts) + 1):
            itemfeat.add('/'.join(parts[:i]))
    
    return itemfeat


def constr(segment='gender_female', files_n=5,
           lower_pop_bound=3,
           ngram_ns=[1, 2], min_word_length=2, word_type='alphanumeric',
           use_urls=True, min_url_depth=1):

    """ """
    
    print 'counting features...'
    items_num = 0
    features = Counter()
    for id, label, urls_str, domains_str in iterraw(segment, 'training', files_n):
        items_num += 1
        for x in item_features(urls_str, domains_str, ngram_ns,
                               min_word_length, word_type,
                               use_urls, min_url_depth):
            features[x] += 1
    
    print 'selecting features...'
    features = set([f for f, c in features.iteritems() if c >= lower_pop_bound])
    features_map = dict([(f, c) for c, f in enumerate(features)])
    del features
    features_num = len(features_map)
    
    print 'creating training matrix...'
    X = sparse.lil_matrix((items_num, features_num), dtype=numpy.float)
    y = numpy.empty((items_num, ), dtype=numpy.int)
    i = 0
    for id, label, urls_str, domains_str in iterraw(segment, 'training', files_n):
        y[i] = label
        features = set()
        urls = urls_in_str(urls_str)
        for x in item_features(urls_str, domains_str, ngram_ns,
                               min_word_length, word_type,
                               use_urls, min_url_depth):
            if x in features_map:
                X[i, features_map[x]] = 1
        i += 1
    X = sparse.csr_matrix(X)
    
    print 'counting test items...'
    items_num = 0
    for id, label, urls_str, domains in iterraw(segment, 'test'):
        items_num += 1
        
    print 'creating test matrix...'
    X_test = sparse.lil_matrix((items_num, features_num), dtype=numpy.float)
    y_test = numpy.empty((items_num, ), dtype=numpy.int)
    i = 0
    for id, label, urls_str, domains_str in iterraw(segment, 'test'):
        y_test[i] = label
        features = set()
        urls = urls_in_str(urls_str)
        for x in item_features(urls_str, domains_str, ngram_ns,
                               min_word_length, word_type,
                               use_urls, min_url_depth):
            if x in features_map:
                X_test[i, features_map[x]] = 1
        i += 1
    X_test = sparse.csr_matrix(X_test)


    return X, y, X_test, y_test, features_map