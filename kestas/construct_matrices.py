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

def generate (url = '', bigram_regex='', n1 = 0, n3 = 0, url_path=0, get=0):
    url = re.sub(r'([/?]*)$', '', url)
    if (url_path):
	if not get:
	    yield cut_get(url)
	else:
	    yield url

    if not get:
		url = cut_get(url)
 
    domain = get_domain(url)
    yield domain.replace('.', '?')   
 
    matches = re.findall(bigram_regex, url)
    
    for i in range(len(matches)-1):
        yield matches[i] + '?' + matches[i+1]
    
    if n1:
        for i in matches:
            yield i
        
    if n3:
        for i in range(min(n3, len(matches)-2)):
            yield '?'.join(matches[j] for j in range(i, i + 3)) 
	"""        
    if url_path == 0:
        pass
    else:
        yield url
        
	for i in range (url_path-1):
            if url.find('/') != -1:
                base, path = url[:url.find('/')], url[url.find('/'):]
                if path.rfind('/') > -1:
                    path = path[:path.rfind('/')]
                    url = base + path
                    yield url
	"""
                    
def to_sparse (data, map):
    print len(data), len(map)
    X, Y = sparse.lil_matrix((len(data), len(map))), []
    for i, point in enumerate(data):
        Y.append(point[1])
        for u in point[2]:
            if u in map:
                X[i, map[u]] = 1
    return X, Y

def gen_data (classifier, regex='', n1 = 0, n3 = 0, url_path=0, get = 0, add_adv = 0, lower_pop_bound=0):
    train, test = [], []
    #features = Counter()
    features = Counter()
    
    stderr.write("Training set...\n")
    for id, label, history in produrator(classifier, adv_url = add_adv):
        dataPoint = [id, label, set()]
        for url in history:
            for u in generate(url, regex, n1, n3, url_path):
                dataPoint[2].add(u)
                features[u] += 1
        train.append(dataPoint)
        
    stderr.write("Enumerating features...\n")

    features = set([f for f, c in features.iteritems()
				 if c > lower_pop_bound])
    features_map = dict([(f,c) for c, f in enumerate(features)])
   
 
    stderr.write("Test set...\n")
    for id, label, history in produrator(classifier, set='testing', adv_url = add_adv):
        dataPoint = [id, label, set()]
        for url in history:
            for u in generate(url, regex, n1, n3, url_path):
                if u in features:
                    dataPoint[2].add(u)
        test.append(dataPoint)    
            
    X, Y = to_sparse(train, features_map)
    Xt, Yt = to_sparse(test, features_map)
            
    return X, Y, Xt, Yt
