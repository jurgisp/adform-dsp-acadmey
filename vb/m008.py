from sys import stderr
from collections import Counter

from base import iterdata, url_prefixes, to_matrix


def m008(label, lower_pop_bound=5):
    """  """
    
    training = []
    test = []
    features = Counter()
    
    # Constructing training set.
    # If http(s)://<X>/<folder> is visited, we say that
    # http(s)://<X> is also visited, and apply this recursively.
    stderr.write('constructing training set... ')
    training_size = 0
    for id, lab, history in iterdata(label):
        training.append((id, lab, set()))
        for url in history.iterkeys():
            for x in url_prefixes(url):
                training[training_size][2].add((x, 1))
                features[x] += 1
        training_size += 1
    stderr.write('done\n')

    stderr.write('selecting most visited URLs as features... ')
    features = set([f for f, c in features.iteritems()
                                            if c >= lower_pop_bound])
    features_map = dict([(f, c) for c, f in enumerate(features)])
    stderr.write('done\n')

    stderr.write('constructing test set... ')
    test_size = 0
    for id, lab, history in iterdata(label, 'test'):
        test.append((id, lab, set()))
        for url in history.iterkeys():
            for x in url_prefixes(url):
                if x in features:
                    test[test_size][2].add((x, 1))
        test_size += 1
    stderr.write('done\n')
    
    stderr.write('converting datasets to sparse matrices... ')
    X, y = to_matrix(training, features_map)
    X_test, y_test = to_matrix(test, features_map)
    stderr.write('done\n')
    
    return X, y, X_test, y_test, features_map
