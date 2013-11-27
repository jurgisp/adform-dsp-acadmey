import sklearn.linear_model as lm
import sklearn.grid_search as grid
import sklearn.metrics as met
import pylab as pl
import cPickle as pickle
import operator as op
import pylab as pl

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
    
def plot_roc (label, fpr, tpr, auc):
    pl.clf()
    pl.figure(figsize=(3,3))
    pl.gcf().subplots_adjust(bottom=0.15)
    pl.gcf().subplots_adjust(left=0.18)
    pl.plot(fpr, tpr, 'g-')
    pl.axis([0,1,0,1])
    pl.xlabel('False Positive Rate', fontsize=10)
    pl.ylabel('True Positive Rate', fontsize=10)
    pl.title('ROC %s' % (label), fontsize=10)
    pl.savefig(label + '_roc.png', bbox_inches = 0) 

def plot_pr (label, r, p, auc):
    pl.clf()
    pl.figure(figsize=(3,3))
    pl.gcf().subplots_adjust(bottom=0.15)
    pl.gcf().subplots_adjust(left=0.18)
    pl.plot(r, p, 'g-')
    pl.axis([0,1,0,1])
    pl.xlabel('Recall', fontsize=10)
    pl.ylabel('Precision', fontsize=10)
    pl.title('Precision-Recall %s' % (label), fontsize=10)
    pl.savefig(label + '_pr.png', bbox_inches = 0)


classifiers = ['age_15_24']

params = {'r': [r'([a-zA-Z0-9]{1,})'],
          'b1' : [1],
          'b2' : [1],
          'url_path' : [1],
          'get' : [1],
          'adv' : [1]}

reg = {'gender_female' : frange(0.0011, 0.0048, 0.0005),
       'age_15_24' : frange(0.0041, 0.0121, 0.0006),
       'income_high' : frange(0.0001, 0.004, 0.0004)}

pop = {'gender_female' : 1,
       'age_15_24' : 3,
       'income_high' : 1}

for label in classifiers:
        
    dump_string('Logreg for ' + label, 1)

    for P in grid.ParameterGrid(params):
        

        X, Y, Xt, Yt, fmap = gen_data(classifier=label, regex=P['r'], b1 = P['b1'], b2 = P['b2'], 
                    url_path = P['url_path'],
                    get = P['get'],
                    add_adv = P['adv'],
                    lower_pop_bound = pop[label],
                    n_files = 47)
       
        #grid search for C
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
        
        #More data for best regularization strength
        dump_string('Best AUC %.8f, C = %.4f' % (best, bestC), 1)
        
         
        model = lm.LogisticRegression(C=bestC)
        model.fit(X, Y)
        out_test = model.predict_proba(Xt)
       
        #plotting graphs
        fpr, tpr, thresholds = met.roc_curve(Yt, out_test[:,1])
        roc_auc = met.auc(fpr, tpr)
        plot_roc(label, fpr, tpr, roc_auc)

        p, r, tresholds = met.precision_recall_curve(Yt, out_test[:,1])
        auc = met.auc(r, p)
        plot_pr(label, r, p, auc)
        
        

        #dumping features weights
        fmap = dict([(v,k) for k, v in fmap.iteritems()])
        features = []
        for key, feature in fmap.iteritems(): 
            features.append((feature,model.coef_[0][key]))
        features = sorted(features, key=op.itemgetter(1), reverse=True)
        ff = open(label + '_features.txt', 'w')
        for i in features:
            ff.write("%.8f %s\n" % (i[1], i[0]) )
        ff.close()
        

