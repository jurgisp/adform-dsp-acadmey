import cPickle as pickle

from sklearn.grid_search import ParameterGrid as params
from sklearn.linear_model import LogisticRegression as logreg
from sklearn.metrics import roc_auc_score as score
from sklearn.metrics import roc_curve
from sklearn.metrics import precision_recall_curve
import matplotlib.pyplot as plt

from constr import constr

def C_score(C, X, y, X_test, y_test):
    
    m = logreg(C=C)
    m.fit(X, y)
    
    return score(y_test, m.decision_function(X_test))


def search(new_grid, Cs):
    grid = {'segment' : ['gender_female'], 'files_n' : [5],
               'lower_pop_bound' : [3],
               'ngram_ns' : [[1, 2]], 'min_word_length' : [2], 'word_type' : ['alphanumeric'],
               'use_urls' : [True], 'min_url_depth' : [1]}
    for k, v in new_grid.iteritems():
        grid[k] = v
    
    res = []
    for p in params(grid):
        X, y, X_test, y_test, features_map = \
            constr(segment=p['segment'], files_n=p['files_n'],
                   lower_pop_bound=p['lower_pop_bound'],
                   ngram_ns=p['ngram_ns'], min_word_length=p['min_word_length'], word_type=p['word_type'],
                   use_urls=p['use_urls'], min_url_depth=p['min_url_depth'])
        sc = set()
        for C in Cs:
            sc.add((C, C_score(C, X, y, X_test, y_test)))
        res.append((p, X.shape, sc))
    
    print res
    
    return res


def add_result(grid, Cs):
    # CAUTION, file grid.pickle must already exist (be [], for example)
    
    new = search(grid, Cs)
    
    current = pickle.load(open('grid.pickle', 'rb'))
    for r in new:
        i = 0
        while i < len(current):
            if current[i][0] == r[0]:
                current[i][2].update(r[2])
                break
            i += 1
        if i == len(current):
            current.append(r)
    
    pickle.dump(current, open('grid.pickle', 'wb'), -1)
    
    return current        


def roc_graph(segment):
    plt.clf()
    X, y, X_test, y_test, features_map = \
        pickle.load(open('prepared/' + segment + '_allegedly_best.pickle', 'rb'))
    models = pickle.load(open('prepared/' + segment + '_logreg.pickle', 'rb'))
    m = max(models, key=lambda t: score(y_test, t.decision_function(X_test)))

    y_pred = [l[1] for l in m.predict_proba(X_test)]
    fpr, tpr, thresholds = roc_curve(y_test, y_pred)
    plt.figure(figsize=(3, 3))
    plt.gcf().subplots_adjust(bottom=0.15)
    plt.gcf().subplots_adjust(left=0.18)
    plt.plot(fpr, tpr, 'g-')
    plt.xlabel('false positive rate', fontsize=10)
    plt.ylabel('true positive rate', fontsize=10)
    plt.axis([0, 1, 0, 1])
    plt.title(segment + ' ROC', fontsize=10)
    plt.savefig('graphs/' + segment + '_roc.png')


def precision_recall_graph(segment):
    plt.clf()
    X, y, X_test, y_test, features_map = \
        pickle.load(open('prepared/' + segment + '_allegedly_best.pickle', 'rb'))
    models = pickle.load(open('prepared/' + segment + '_logreg.pickle', 'rb'))
    m = max(models, key=lambda t: score(y_test, t.decision_function(X_test)))

    y_pred = [l[1] for l in m.predict_proba(X_test)]
    precision, recall, thresholds = precision_recall_curve(y_test, y_pred)
    plt.figure(figsize=(3, 3))
    plt.gcf().subplots_adjust(bottom=0.15)
    plt.gcf().subplots_adjust(left=0.18)
    plt.plot(recall, precision, 'g-')
    plt.xlabel('recall', fontsize=10)
    plt.ylabel('precision', fontsize=10)
    plt.axis([0, 1, 0, 1])
    plt.title(segment + ' precision / recall', fontsize=10)
    plt.savefig('graphs/' + segment + '_precision_recall.png')
