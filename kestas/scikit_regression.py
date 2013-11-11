import sklearn.linear_model as lm
import sklearn.grid_search as grid
import sklearn.metrics as met
import pylab as pl
import cPickle as pickle
import operator as op

from construct_matrices import gen_data

def frange (x, y, jump):
    ret = []
    while (x <= y):
        ret.append(x)
        x += jump
    return ret

def dump_string (s, p=0):
    if (p):
        print s 
    file = open('dump.txt','a')
    file.write(s + "\n")
    file.close()
    

classifiers = ['gender_female', 'age_15_24', 'income_high']

params = {'r': [r'([a-zA-Z0-9]{2,})'],
          'n1' : [1],
          'url_path' : [1],
          'get' : [1],
          'adv' : [1]}

reg = {'gender_female' : frange(0.0011, 0.0048, 0.0005),
       'age_15_24' : frange(0.0041, 0.0121, 0.0006),
       'income_high' : frange(0.0001, 0.004, 0.0004),
       'income_medium' : frange(0.0021, 0.007, 0.0005),
       'income_low' : frange(0.0021, 0.007, 0.0005)}

pop = {'gender_female' : 1,
       'age_15_24' : 5,
       'income_high' : 1,
       'income_medium' : 1,
       'income_low' : 1} 

for label in classifiers:
        
    dump_string('Logreg for ' + label, 1)

    for P in grid.ParameterGrid(params):
        
        #dump_string('  '.join([key+'_'+str(value) for key, value in P.iteritems()]), 0)
        #print 'ADV = ', P['adv']
        
        X, Y, Xt, Yt, fmap = gen_data(label, P['r'], P['n1'], 
                url_path = P['url_path'],
                get = P['get'],
                add_adv = P['adv'],
                lower_pop_bound = pop[label])
        
        best, bestC = 0, 0
        for CC in reg[label]:
            
            model = lm.LogisticRegression(C=CC)
            model.fit(X, Y)
            out_test = model.predict_proba(Xt)
            fpr, tpr, thresholds = met.roc_curve(Yt, out_test[:,1])
            roc_auc = met.auc(fpr, tpr)
            if (best < roc_auc):
                bestC = CC
                best = max(best, roc_auc)  
            dump_string ('AUC = %.8f,    C = %.4f' % (roc_auc, CC), 1)
        
        dump_string('Best AUC %.8f, C = %.4f' % (best, bestC), 1)
        
        model = lm.LogisticRegression(C=bestC)
        model.fit(X, Y)
        
        fmap = dict([(v,k) for k, v in fmap.iteritems()])
        features = []

        for key, feature in fmap.iteritems(): 
            features.append((feature,model.coef_[0][key]))
        features = sorted(features, key=op.itemgetter(1), reverse=True)
        
        for i in range(10):
            print features[i]

        ff = open(label + '_features.txt', 'w')
        for i in features:
            ff.write("%.8f %s\n" % (i[1], i[0]) )
        ff.close()

