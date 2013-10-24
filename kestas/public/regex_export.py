import pymysql
import cPickle as pickle

#read the files dumped by regex_history.py
#leave it in format:
#[cookie_id, LABEL, [url_id1, url_id2, url_id3..]]
#this can be used by scikit_regression.py
LABEL = 'gender'

conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='sA4iPjas', db='adform')
cur = conn.cursor()

def extract_label (datapoint):
    if LABEL == 'gender':
        return datapoint[1]
    elif LABEL == 'age':
        return datapoint[2]
    elif LABEL == 'income':
        return datapoint[3]

def pickle_dump (file_import, file_export):
    
    file = open(file_import, 'rb')
    a = pickle.load(file)
    file.close()
    
    data = []
    i = 0
    maxas = 0
    for dataPoint in a:
        label = extract_label(dataPoint)
        #print dataPoint
        if label is not None:
            data.append([])
            data[i].append(dataPoint[0])
            data[i].append(label)
            data[i].append(dataPoint[4])
            for j in dataPoint[4]:
                maxas = max(maxas, j)
            i += 1
            
    file = open(file_export, 'wb')
    pickle.dump(data, file)
    file.close()
    
    del a
    print len(data), 'lines exported from ',file_import
    print 'MAX =', maxas
    del data
    
pickle_dump('regression_train_import.b', 'regression/regression_train.b')
pickle_dump('regression_test_import.b', 'regression/regression_test.b')