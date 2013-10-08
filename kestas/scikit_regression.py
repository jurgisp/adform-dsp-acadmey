import numpy
import random
import math
import cPickle
import scipy.sparse 
import sklearn.linear_model as lm
import sklearn.metrics as met
import pylab as pl

coffs_len = 13712 + 1
classifier = 'female'
penalty_ = 'l1'

#transform dump of regex_export to scipy sparse matrix
def extract_data(filename):
    file = open(filename, 'rb')
    data = cPickle.load(file)
    file.close()
    
    data_len = len(data)
    X = scipy.sparse.lil_matrix((data_len, coffs_len))
    Y = []
    n = 0
    for i in data:
        for j in i[2]:
            #X[n, j[0]] = j[1]
            X[n, j] = 1
        n += 1
        Y.append(i[1] == classifier)
    del data
    return X, Y
    
X, Y = extract_data('regression_train.b')
Xt, Yt = extract_data('regression_test.b')


print 'Data is extracted'
print 'Regularization: ' + penalty_

model = lm.LogisticRegression(penalty=penalty_)
#model = lm.SGDClassifier(loss='log', penalty='elasticnet', alpha=0.0015, l1_ratio=0.2, n_iter=2000, eta0=0.001)
model.fit(X, Y)

out_train = model.predict_proba(X)
fpr, tpr, thresholds = met.roc_curve(Y, out_train[:,1])
roc_auc = met.auc(fpr, tpr)
print 'AUC for train = %0.4f' % roc_auc

out_test = model.predict_proba(Xt)
fpr, tpr, thresholds = met.roc_curve(Yt, out_test[:,1])
roc_auc = met.auc(fpr, tpr)
print 'AUC for test = %0.4f' % roc_auc
