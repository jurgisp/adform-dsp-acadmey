import re
import random
import urllib2
import itertools
import tldextract
import random
import operator as op
import string
import sys
import cPickle as pickle

def get_domain (url):
    a = tldextract.extract(url)
    return a.domain + '.' + a.suffix

rubbish = set(['adservinginternational.com', 'adnxs.com','doubleclick.net',
               'emediate.eu', 'google.com', 'google.dk', 'emediate.se',
               'adform.net', 'google.co.in', 'specificclick.net', 'sharedaddomain.com'
               ])
garbage = set (['facebook.com', 'bing.com'])        
        
def parse_url (url=''):    
    url = urllib2.unquote(url)
    
    #extract main domain.
    matches = re.findall(r'^http[s]*://(.*?)/', url)
    if matches:
        domain = get_domain(matches[0])
    else:
        domain = 'UNKNOWN'
    
    #extract domains encoded in query
    matches = re.findall(r'(?:=http[s]*://([a-zA-Z0-9.]+?)/)', url)
    if matches:
        #print matches
        for key, val in enumerate(matches):
            matches[key] = get_domain(val)
        matches = list(set(matches) - rubbish)
        if matches:
            if len(matches) > 1:
                matches = list(set(matches) - garbage)
                random.shuffle(matches)
                if matches:
                    return matches[0]
                else:
                    return domain
            else:
                return matches[0]  
        else:
            return get_domain(domain)
    else:
        return domain
    

if __name__ == "__main__":

    fileH = open('cookies/f97535c3-1612-4b18-91b6-e66f644178d5_000000', 'r')
    
    fileC = open('cookies/cookies.txt')
    llist = ['gender','age','income','education','employment','children','household']
    labellist = ['gender','age','income']
    #labellist = ['income']
    CID_indexes = {}
    COO = []
    
    NU = len(labellist) + 1
 
    sys.stderr.write("Creating struct for cookies\n")
    
    #Read cookies and store the relevant info in a structure
    line = fileC.readline().replace("\n","")    
    i = 0
    while line != '':
        (id, labels, uagent) = tuple ( string.split (line, '\t', 2))
        id = int(id)
        
        labels = [tuple( l.split('_', 1)) for l in labels.split(';')]
        labels = {i[0] : i[1] for i in labels}
        for label in llist:
            if label not in labels:
                labels[label] = None
        
        dataPoint = []
        dataPoint.append(id)
        for label in labellist:
            dataPoint.append(labels[label])
        dataPoint.append([])
        
        COO.append(dataPoint)
        CID_indexes[id] = i
        
        i += 1
        line = fileC.readline().replace('\n', '')
    fileC.close()
    
    
    #Process the information of history up to a given point N 
    #save it in the structure of the form ['cookieid','gender','age','income',['http://ekstra.dk','http://google.dk']]
    N = 10000000
    URLS = {}
    prev_id = 'papa'
    index = 0
    dict = set()
    data, data_test, dataPoint = [], [], []
    
    
    for X in range (N):
        if (X % (N/100) == 0):
            sys.stderr.write(str(X/(N/100)+1) + "%\n")
        line = fileH.readline().replace("\n","")
        line = str.split(line, '\t', 2)
        cid = int(line[0])
        url = parse_url(line[2])
        
        if (cid != prev_id):
            if (prev_id != 'papa'):
                for key in dict:
                    dataPoint[NU].append(key)
                if prev_id % 10 == 0:
                    data_test.append(dataPoint)
                else:
                    data.append(dataPoint)
            prev_id = cid
            dict = set()
            index = CID_indexes[cid]
            dataPoint = COO[index]
       
        dict.add(url)
        
        #count the total occurances of the URLS
        if url in URLS:
            URLS[url] += 1
        else:
            URLS[url] = 1
    
    
    
    
    sys.stderr.write("Enumerating urls in data..\n")
    
    #enumerate URL's by popularity     
    Ulist = sorted(URLS.iteritems(), key=op.itemgetter(1), reverse=True)
    for key, u in enumerate(Ulist):
        URLS[u[0]] = key
   
    #replace url's with id's in data arrays
    for d, dataPoint in enumerate(data):
        for key, value in enumerate(dataPoint[NU]):
            data[d][NU][key] = URLS[data[d][NU][key]]
        data[d][NU].sort()
    
    for d, dataPoint in enumerate(data_test):
        for key, value in enumerate(dataPoint[NU]):
            data_test[d][NU][key] = URLS[data_test[d][NU][key]]
        data_test[d][NU].sort()
    
    
    
    #pickle dump the data structures
    sys.stderr.write("Pickle dumping data..\n")
    file = open('regression_train_import.b', 'wb')
    pickle.dump(data, file)
    file.close()
    
    file = open('regression_test_import.b', 'wb')
    pickle.dump(data_test, file)
    file.close()
    
    