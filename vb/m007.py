from sys import stderr
from collections import Counter

from base import iterdata, to_matrix, url_prefix, url_prefixes


def m007(label, cut_bound=10, drop_bound=1, max_level=10):
    """  """
    
    training = []
    test = []
    features = Counter()
        
    stderr.write('constructing training set... ')
    training_size = 0
    for id, lab, history in iterdata(label):
        training.append((id, lab, []))
        for url in history.iterkeys():
            if url[-1] == '/':
                url = url[:-1]
            training[training_size][2].append((url, 1))
            features[url] += 1
        training_size += 1
    stderr.write('done\n')

    stderr.write('modifying training set... \n')
    for level in range(max_level, -1, -1):
        stderr.write('\titeration with prefix length ' + str(level) + '... ')
        for i in range(training_size):
            for j in range(len(training[i][2])):
                url = training[i][2][j][0]
                if features[url] < cut_bound:
                    url = url_prefix(url, level)
                    training[i][2][j] = (url, 1)
                    features[url] += 1
        stderr.write('done\n')
    stderr.write('... done\n')

    stderr.write('selecting most visited URLs as features... ')
    features = set([f for f, c in features.iteritems() if c >= drop_bound])
    features_map = dict([(f, c) for c, f in enumerate(features)])
    stderr.write('done\n')

    stderr.write('constructing test set... ')
    test_size = 0
    for id, lab, history in iterdata(label, 'test'):
        test.append((id, lab, []))
        for url in history.iterkeys():
            if url[-1] == '/':
                url = url[:-1]
            for url in url_prefixes(url):
                if url in features:
                    break
            if url in features:
                test[test_size][2].append((url, 1))
        test_size += 1
    stderr.write('done\n')
    
    stderr.write('converting datasets to sparse matrices... ')
    X, y = to_matrix(training, features_map)
    X_test, y_test = to_matrix(test, features_map)
    stderr.write('done\n')
    
    return X, y, X_test, y_test, features_map
