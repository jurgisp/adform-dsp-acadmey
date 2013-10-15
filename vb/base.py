from sys import stderr
import cPickle as pickle
import urlparse

import numpy as np
from scipy import sparse


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
