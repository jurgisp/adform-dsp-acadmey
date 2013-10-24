
import sqlite3
import math


conn = sqlite3.connect("sample.db")
cur = conn.cursor()

cur.execute("select count(*) from domains;")
theta = [0.01] * (cur.fetchone()[0] + 1)
history = []
test = []
alfa = 0.001

def fill_history():
    global theta
    global history
    new_cur = conn.cursor()
    cur.execute("select id, class from class;")
    for (id, cl) in cur:
        new_cur.execute("select did from history where id=?;", (id,))
        dids = [0] + [did for (did,) in new_cur]
        history.append((id, cl, dids))

def fill_test():
    global theta
    global test
    new_cur = conn.cursor()
    cur.execute("select distinct id, class from test;")
    for (id, cl) in cur:
        new_cur.execute("select did from test where id=?;", (id,))
        dids = [0] + [did for (did,) in new_cur]
        test.append((id, cl, dids))

def parametrized(dids):
    global theta
    global history
    par = 1
    for i in range(len(dids)):
        par += theta[dids[i]]
    return par

def sigmoid(x):
    return 0.9999 / (1 + math.exp(-x))

def p(dids):
    return sigmoid(parametrized(dids))

def cost():
    global theta
    global history
    cost = 0
    for (id, cl, dids) in history:
        if cl == 1:
            cost -= math.log(p(dids))
        else:
            cost -= math.log(1 - p(dids))
    return cost

def update():
    global theta
    global history
    global alfa
    theta2 = theta
    sums_i = []
    for (id, cl, dids) in history:
        sums_i.append(p(dids) - cl)
    sums_j = [0] * len(theta)
    for i in range(len(history)):
        for did in history[i][2]:
            sums_j[did] += sums_i[i]
    for j in range(len(theta)):
        theta2[j] = theta[j] - alfa * sums_j[j]
    theta = theta2

def test_self():
    f = open("log.pred", "w")
    f.write("output model\n")
    for (id, cl, dids) in test:
        f.write(str(cl) + ' ' + str(p(dids)) + '\n')
    f.close()

fill_history()

    
