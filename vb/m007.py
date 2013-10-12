from sys import stderr
import pickle

from sklearn.linear_model import LogisticRegression as logreg
from sklearn.metrics import roc_auc_score as auc

from base import DemogData
from base import PopCounter
from base import BinaryConstruct
from url_tools import strip_url, strip_urls



class M007:
    
    def __init__(self, label, pop_threshold=25, max_path=5, leftovers=True):
        self.model_name = 'M007'
        self.results = []
        self.reload_data(label, pop_threshold, max_path, leftovers)


    def reload_data(self, label, pop_threshold=25, max_path=5, leftovers=True):

        self.label = label
        self.pop_threshold = pop_threshold
        self.max_path = max_path
        self.leftovers = leftovers

        self.feature_codes = self._get_features(label, pop_threshold, max_path, leftovers)

        self.X, self.y, self.X_test, self.y_test = self._get_matrices()


    def auc_score(self, C=0.1):
        
        m = logreg(C=C)
        m.fit(self.X, self.y)
        test_score = auc(self.y_test, m.decision_function(self.X_test))
        train_score = auc(self.y, m.decision_function(self.X))
        
        params = (self.label, self.pop_threshold, self.max_path,
                  self.leftovers, C, test_score, train_score)
        
        if params not in self.results:
            self.results.append(params)
        
        return test_score, train_score
    

    def self_dump(self):
        pickle.dump(self, open('data/' + self.model_name + '.p', 'w'))


    def _get_features(self, label, pop_threshold, max_path, leftovers):
        
        data = DemogData()
        pop = PopCounter()

        stderr.write('counting urls... ')
        for id, url in data.iterurls(self.label):
            pop.add(url)
        stderr.write('done\n')
        
        stderr.write('popularizing unpopular... ')
        pop.add_many(strip_urls(pop.pop_unpopular(self.pop_threshold)))
        for i in range(self.max_path, -1, -1):
            pop.add_many(strip_urls(pop.pop_unpopular(self.pop_threshold), i))
        if not self.leftovers:
            pop.pop_unpopular(self.pop_threshold)
        stderr.write('done\n')
        
        return pop.feature_codes()

    
    def _get_matrices(self):

        constr = BinaryConstruct(self.label, self.feature_codes)
        data = DemogData()

        stderr.write('creating train and test matrices... ')
        for id, url in data.iterurls(self.label):
            if url not in constr.feat_codes:
                url = strip_url(url)
            i = 5
            while url not in constr.feat_codes and i >= 0:
                url = strip_url(url, i)
                i -= 1
            constr.add(id, url)
        constr.to_train_test()
        stderr.write('done\n')
        
        return constr.X, constr.y, constr.X_test, constr.y_test
