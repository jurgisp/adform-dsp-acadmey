import sklearn.linear_model as lm
import sklearn.grid_search as grid
import sklearn.metrics as met
import pylab as pl
import cPickle as pickle

from construct_matrices import gen_data

def frange (x, y, jump):
    ret = []
    while (x <= y):
        ret.append(x)
        x += jump
    return ret


classifiers = ['gender_female', 'age_15_24', 'income_high']
#classifiers = ['income_high']


params = {'r': [r'([\w\d]{3,})'],
          'n1' : [1],
          'n3' : [0],
          'up' : [0]}
          
reg = {'gender_female' : frange(0.05, 0.4, 0.05),
       'age_15_24' : frange(0.05, 0.4, 0.05),
       'income_high' : frange(0.005, 0.02, 0.005)}
          
for P in grid.ParameterGrid(params):
    
    for label in classifiers:
        print 'LOGREG for ', label
        X, Y, Xt, Yt = gen_data(label, P['r'], P['n1'])
        
        for CC in reg[label]:
            
            model = lm.LogisticRegression(C=CC)
            model.fit(X, Y)
            out_test = model.predict_proba(Xt)
            fpr, tpr, thresholds = met.roc_curve(Yt, out_test[:,1])
            roc_auc = met.auc(fpr, tpr)
            print 'AUC = %.8f,    C = %.4f' % (roc_auc, CC)
            
            
            