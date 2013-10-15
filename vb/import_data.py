import cPickle as pickle
from collections import Counter
import time


# Read data from 'data/cookie_history_1' and 'data/cookies.txt'.
# Create history training and test sets as dicts
#     history[id] = (labels_dict, url_counter)
# where
#     labels_dict[label_bin] = class
#          label_bin = 'gender', 'age', ...
#          class = 'male', 'female', '15_24', ...
#     url_counter[url] = different_visitor_count
#
# Save data as pickles 'data/data.p' and 'data/data_test.p'.


beg = time.time()


history = dict()
history_test = dict()
f = open('data/cookie_history_1', 'r')

# fill history
for line in f:
    id, d, t, url = line.split()
    id = int(id)
    if abs(id) % 10 != 0:
        if id not in history:
            history[id] = dict(), Counter()
        history[id][1][url] += 1
    else:
        if id not in history_test:
            history_test[id] = dict(), Counter()
        history_test[id][1][url] += 1

f.close()


f = open('data/cookies.txt', 'r')

# fill labels
for line in f:
    id, lab, ua = line.split('\t')
    id = int(id)
    if id in history:
        lab = lab.split(';')
        for k, v in [tuple(l.split('_', 1)) for l in lab]:
            history[id][0][k] = v
    elif id in history_test:
        lab = lab.split(';')
        for k, v in [tuple(l.split('_', 1)) for l in lab]:
            history_test[id][0][k] = v

f.close()


data = []
data_test = []

for id, (labels, urls) in history.iteritems():
    data.append((id, labels, urls))
for id, (labels, urls) in history_test.iteritems():
    data_test.append((id, labels, urls))


pickle.dump(sorted(data), open('data/data.p', 'wb'))
pickle.dump(sorted(data_test), open('data/data_test.p', 'wb'))


print 'execution time:', time.time() - beg
