from collections import namedtuple
import sqlite3
import time
import urlparse

import numpy as np
from scipy import sparse


all_labels = ['gender_male', 'gender_female',
              'age_15_24', 'age_25_34', 'age_35_44', 'age_45_54', 'age_55',
              'income_low', 'income_medium', 'income_high',
              'education_university', 'education_nonuniversity',
              'employment_employed', 'employment_student', 'employment_other',
              'children_yes', 'children_no',
              'household_1', 'household_2', 'household_3', 'household_4',
                                                                'household_5']

labels_map = {'gender'     : ['male', 'female'],
              'age'        : ['15_24', '25_34', '35_44', '45_54', '55'],
              'income'     : ['low', 'medium', 'high'],
              'education'  : ['university', 'nonuniversity'],
              'employment' : ['employed', 'student', 'other'],
              'children'   : ['yes', 'no'],
              'household'  : ['1', '2', '3', '4', '5'] }



class DemogData:
    """Class DemogData allows easy access to Adform demographics and
    history dataset without directly using sqlite3 queries.
    
        Supported methods:
    iterurls() - iterator over history entries.
    iterids() - iterator over cookie ids.
    id_label() - returns label value of cookie id, given label.
    """

    def __init__(self):
        self._conn = sqlite3.connect('data/data.sqlite3')
        self.all_labels = all_labels
        self.labels_map = labels_map

    
    def iterurls(self, label='', limit=0):
        """Returns an iterator of history entries. Items in iterator
        are tuples (id, url)
        
            Parameters:
        label - must be either empty string or label from all_labels.
            If label is empty, iterurls() will iterate over all history.
            If label is given, only history of cookies which fall under
            the given label or under a label from the same category will
            be given (e.g., if label='gender_female', iterator will yield
            both men and women history, but not history of cookies for
            which gender is unknown).
        limit - integer, maximum limit of history entries to yield.
            limit=0  means no restrictions.
        """
        
        cur = self._conn.cursor()
        if limit:
            limit = ' limit ' + str(limit)
        if label:
            label = ' where ' + label + ' is not null'
        cur.execute('select id, url from history' + label + limit + ';')
        for row in cur:
            yield row


    def iterids(self, label, limit=''):
        """Returns an iterator over cookie ids and their label values.
        Only cookies which fall under the given label or the a label
        from the same category will be included (e.g., both men and
        women will be included if label='gender_female', but not those
        cookies for which gender is unknown). Items in iterator are
        tuples (id, label_value), where id is cookie id and label_value is
            1, if cookie falls under the given label,
            0, if cookie doesn't fall under the given label.
        
            Parameters:
        label - must be label from all_labels.
        limit - integer, maximum limit of history entries to yield.
                limit=0 means no restrictions.
        """
        
        cur = self._conn.cursor()
        if limit:
            limit = ' limit ' + str(limit)
        label_query = ' where ' + label + ' is not null'
        cur.execute('select id, ' + label +' from labels'
                    + label_query + limit + ';')
        for row in cur:
            yield row
    
    def id_label(self, id, label):
        """Return label value of cookie id for some given label.
        Label value is
            1, if cookie falls under the given label,
            0, if cookie falls under any other label from the same
                category (e.g. label='income_low' and cookie is
                labeled as 'gender_medium')
            None, otherwise (e.g., label='gender_female', but
                cookie is not labeled as either male or female).
        
            Parameters:
        id - valid cookie id.
        label - label from all_labels.
        """

        cur = self._conn.cursor()
        cur.execute('select id, ' + label + ' from labels where id=?;', (id, ))
        return cur.fetchone()[1]


class PopCounter:
    """Popularity counter for features.
    
    Features can be any strings. PopCounter object counts keeps track of
    how many times every feature has been added."""
    
    def __init__(self):
        self.features = dict()
        
    def add(self, feature):
        """Add a feature."""
        if feature in self.features:
            self.features[feature] += 1
        else:
            self.features[feature] = 1
    
    def add_many(self, features):
        """Add features in an iterable."""
        for feature in features:
            self.add(feature)
    
    def pop_unpopular(self, n):
        """Pops features with less than n counts as feature:count dict."""
        unpopular = dict()
        for feat, count in self.features.iteritems():
            if count <= n:
                unpopular[feat] = self.features[feat]
        for x in unpopular.iterkeys():
            del self.features[x]
        return unpopular
    
    def feature_codes(self):
        """Returns enumerated features as feature:code dict."""
        codes = dict()
        for c, f in enumerate(self.features.iterkeys()):
            codes[f] = c
        return codes
        


class BinaryConstruct:
    """Training set and test set constructor."""
    
    def __init__(self, label, feat_codes=dict()):
        """Parameters:
        label - must be a label from all_labels.
        feat_codes - a dict of enumerated features (feat_codes[str]=int).
        """
        self.dataset = dict()
        self.feat_codes = feat_codes
        self.feat_num = len(feat_codes)
        self.label = label
        if feat_codes:
            self.train = False
        else:
            self.train = True
    
    def add(self, id, feat):
        """Adds a feature feat for cookie id. If feat_codes was given at
        initialization and feat is not in it, feat will be ignored."""

        if self.train and feat not in self.feat_codes:
            self.feat_codes[feat] = self.feat_num
            self.feat_num += 1 
        if feat in self.feat_codes:
            if id in self.dataset:
                self.dataset[id].add(self.feat_codes[feat])
            else:
                self.dataset[id] = set([self.feat_codes[feat]])
    
#    def add_many(self, ):
        

    def to_train_test(self):
        """Creates attributes X, y, X_test, y_test, where
        X, X_test - scipy.sparse.csr_matrix, training and test
                    feature matrixes.
        y, y_test - numpy.array, training and test label arrays."""
        
        self.dataset_test = dict()
        for id, codes in self.dataset.iteritems():
            if abs(id) % 10 == 0:
                self.dataset_test[id] = codes
        for k in self.dataset_test.iterkeys():
            del self.dataset[k]
                
        self.X = sparse.lil_matrix((len(self.dataset), len(self.feat_codes)), dtype=np.int)
        self.y = np.empty((len(self.dataset), ), dtype=np.int)
        i = 0
        for id, feats in self.dataset.iteritems():
            self.y[i] = DemogData().id_label(id, self.label)
            for feat in self.dataset[id]:
                self.X[i, feat] = 1
            i += 1
        self.X = sparse.csr_matrix(self.X)

        self.X_test = sparse.lil_matrix((len(self.dataset_test), len(self.feat_codes)), dtype=np.int)
        self.y_test = np.empty((len(self.dataset_test), ), dtype=np.int)
        i = 0
        for id, feats in self.dataset_test.iteritems():
            self.y_test[i] = DemogData().id_label(id, self.label)
            for feat in self.dataset_test[id]:
                self.X_test[i, feat] = 1
            i += 1
        self.X_test = sparse.csr_matrix(self.X_test)

