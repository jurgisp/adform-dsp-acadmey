import numpy
import random
import math
import cPickle

file = open('regression_train.b', 'rb')
data = cPickle.load(file)
file.close()
"""
data - formatu
[ [cookie_id, 'female', [0,1,4,62,234]],
  [cookie_id, 'male', [2, 4, 35, 132],
  ...
]
"""

classifier = '15_24'
# urls = 1..2795
#
data_len = float(len(data))
#how many features you have + 1 for theta0
coffs_len = 7443 + 1

    
#initial vector of coefficients
coffs = []
for i in range(coffs_len):
    coffs.append (random.random()/10 )
coffs[0] = 1    
    
def h (coffs, data_point):
    sum = coffs[0]
    for x in data_point[2]:
        sum += coffs[x[0]]
        #sum += coffs[x[0]] * x[1]
    return 1.0 / ( 1.0 + math.exp(-sum))

#ar reguliarizacija veikia - nesu tikras, kažkaip įtartinai ten būdavo.
def regularization(coffs):
    sum = 0.0
    for i in coffs:
        sum += abs(i)
    return sum
    
def cost_function(coffs):
    sum = 0
    #alphaR = 1/data_len
    alphaR = 1
    for i in data:
        if i[1] == classifier:
            sum += math.log(h(coffs, i))
        else:
            sum += math.log(1 - h(coffs, i))
    sum /= data_len
    #nutrink sum -= .... ir panaikinsi reguliaraizaciją, tada turėtų kažkiek veikt.
    sum -= regularization(coffs) * alphaR
    #print 'regularization: ', regularization(coffs) * alphaR
    return sum


#calculating partial derrivatives.
def update_coffs(coffs):
    coffs_n = [0] * coffs_len
    alpha = 0.1
    
    for point in data:
        hh = h(coffs, point)
        coffs_n[0] += (point[1] == classifier) - hh
        for url in point[2]:
            coffs_n[url[0]] += (point[1] == classifier) - hh
            #coffs_n[url[0]] += ((point[1] == classifier) - hh) * url[1]
            
    for i in range(coffs_len):
        coffs_n[i] /= data_len
        coffs_n[i] *= alpha
        
    return coffs_n
        
prev_cost = cost_function(coffs)
print prev_cost

#this is kinda gradient descent
while True:
    coffs_n = update_coffs(coffs)
    
    for i in range(coffs_len):
        coffs_n[i] = coffs[i] + coffs_n[i]
        
    new_cost = cost_function(coffs_n)
    
    coffs = coffs_n
    
    print prev_cost, '->', new_cost
    #for i in range (11):
    #    print coffs[i]
    
    if abs(prev_cost - new_cost) < 0.0000001:
        break
    prev_cost = new_cost

#dump weights
file = open("regression_weights.csv", 'w')
for i in range (coffs_len):
    file.write(str(i) + ',' + str(coffs[i]) + '\n');
file.close()


#write test roc data
# you can run yard-plot -show--auc curves_train.txt to get auc curve.
file = open("curves_train.txt", 'w')
file.write('output\tmethod\n')
for line in data:
    if (line[1] == classifier):
        file.write('+1\t' + str(h(coffs, line)) + '\n')
    else:
        file.write('-1\t' + str(h(coffs, line)) + '\n')
file.close()

  
#performing on a test set:
file = open("regression_test.b", 'rb')
data_test = cPickle.load(file)
file.close

# you can run yard-plot -show--auc curves_test.txt to get auc curve.
file = open("curves_test.txt", "w")
for line in data_test:
    if (line[1] == classifier):
        file.write('+1\t' + str(h(coffs, line)) + '\n')
    else:
        file.write('-1\t' + str(h(coffs, line)) + '\n')
file.close()  
  