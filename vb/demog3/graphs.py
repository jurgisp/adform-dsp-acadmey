import cPickle as pickle

import matplotlib.pyplot as plt

def auc_vs_pop():
    
    res = pickle.load(open('grid.pickle', 'rb'))
    
    