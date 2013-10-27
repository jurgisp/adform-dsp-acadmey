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


classifiers = ['income_high']
#classifiers = ['age_15_24', 'income_high', "gender_female"]
#classifiers = ['income_high']


params = {'r': [r'([a-zA-Z0-9]{2,})'],
          'n1' : [1],
          'n3' : [0],
	  'add_adv' : [1],
          'url_path' : [1],
  	  'get' : [1],
	  'pop' : [1]}
reg = {'gender_female' : frange(0.0001, 0.0201, 0.001),
       'age_15_24' : frange(0.0001, 0.0221, 0.001),
       'income_high' : frange(0.0001, 0.015, 0.0007)}
pop = {'gender_female' : 1,
       'age_15_24' : 5,
       'income_high' : 2} 
add_adv = {'gender_female' : 1,
	   'age_15_24' : 0,
	   'income_high' : 1}
"""          
reg = {'gender_female' : frange(0.0001, 0.0251, 0.001),
       'age_15_24' : frange(0.0001, 0.0321, 0.001),
       'income_high' : frange(0.0001, 0.015, 0.0008)}
"""        
  
for P in grid.ParameterGrid(params):
    print P 
    for label in classifiers:
	file = open('dump.txt','a')
        print 'LOGREG for ', label
	file.write('Logreg for ' + label + '\n')
        X, Y, Xt, Yt = gen_data(label, P['r'], P['n1'], 
				url_path = P['url_path'],
				get = P['get'],
				add_adv = add_adv[label], 
				lower_pop_bound = pop[label])
        file.close() 
        for CC in reg[label]:
            model = lm.LogisticRegression(C=CC)
            model.fit(X, Y)
            out_test = model.predict_proba(Xt)
            fpr, tpr, thresholds = met.roc_curve(Yt, out_test[:,1])
            roc_auc = met.auc(fpr, tpr)
            file = open('dump.txt','a')
            print 'AUC = %.8f,    C = %.4f' % (roc_auc, CC)
            file.write("AUC = %.8f,    C = %.4f\n" % (roc_auc, CC))
	    file.close() 
            
            
