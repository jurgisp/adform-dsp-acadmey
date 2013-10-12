

"""
This script exports data in cookies.txt and cookie_history_1
to sqlite3 database. It creates two tables that will be used
by class DemogData in module base.
"""


from sys import stderr
import sqlite3
import urlparse

import tldextract

from base import all_labels, labels_map


history_path = 'data/cookie_history_1'
labels_path = 'data/cookies.txt'
history_table = 'history'
labels_table = 'labels'
database = sqlite3.connect('data/data.sqlite3')



# the set of all cookie ids that have history entries in history file
ids = set()


def find_ids():
    stderr.write('inserting ids... ')
    f = open(history_path, 'r')
    for line in f:
        id, date, time, url = line.split()
        ids.add(int(id))
    f.close()
    stderr.write('done\n')

def create_labels_table():
    """Creates sqlite3 table for cookie IDs' labels.
    
    Table columns are:

    id, gender_male, gender_female, age_15_24, <...>, household_5

    where id is integer primary key and other columns are integers.
    
    """
    
    stderr.write('creating labels table... ')
    cur = database.cursor()
    cur.execute('drop table if exists ' + labels_table + ';')
    cur.execute('create table ' + labels_table + ' (id integer primary key, '
                +  ', '.join([label + ' int' for label in all_labels]) + ');')
    stderr.write('done\n')

def insert_labels():
    """Fills labels table in sqlite3 database.
    
    After execution, for every row each label column X (gender_male,
    gender_female, age_15_24, ...) stores:
            1, if user (cookie id) falls under label X
            0, if user falls under label from the same category as X
                (e.g., gender_female column is 0 if gender_male is 1)
            null, if user doesn't fall under any labels from the
                category of X (e.g., income_high is null if user's
                income is unknown)
    """
    
    stderr.write('inserting labels... ')
    cur = database.cursor()
    f = open(labels_path, 'r')
    for line in f:
        id_str, labels_str, ua_str = line.split('\t')
        id = int(id_str)
        if id not in ids:
            continue
        user_labels = labels_str.split(';')
        row = [id]
        for label in all_labels:
            if label in user_labels:
                row.append(1)
            elif label.split('_', 1)[0] in [x.split('_', 1)[0]
                                            for x in user_labels]:
                row.append(0)
            else:
                row.append(None)
        cur.execute('insert into ' + labels_table + ' values (?'
                    + ', ?' * (len(row) - 1) + ');', tuple(row))
    stderr.write('done\n')
    stderr.write('committing... ')
    database.commit()
    stderr.write('done\n')


def create_history_table():
    """History table has all the columns that labels table has and
    a few more:
    
        year int, month int, day int, hour int, minute int, second int,
        domain text, netloc text, url text

    netloc is full domain with subdomain, e.g. 'what-if.xkcd.com' for
    url 'http://what-if.xkcd.com/63/'. Domain here would be 'xkcd.com'
    
    The values in columns
        id, gender_male, gender_female, ..., household_5
    are the same in every history entry for the same user (cookie id).
    This redundancy results in slightly faster implementation of
    python iterator over history entries in DemogData (in base.py).
    """
    stderr.write('creating history table... ')
    cur = database.cursor()
    cur.execute('drop table if exists ' + history_table + ';')
    cur.execute('create table ' + history_table + ' (id int, '
                +  ', '.join([label + ' int' for label in all_labels])
                + ', year int, month int, day int'
                + ', hour int, minute int, second int'
                + ', domain text, netloc text, url text);')
    stderr.write('done\n')

def insert_history():
    stderr.write('inserting history...\n')
    f = open(history_path, 'r')
    cur = database.cursor()
    i = 0
    for line in f:
        row = line.split()
        row[1:2] = row[1].split('-')
        row[4:5] = row[4].split(':')
        row[:-1] = [int(x) for x in row[:-1]]
        parsed_url = tldextract.extract(row[-1])
        if parsed_url.suffix:
            domain = parsed_url.domain + '.' + parsed_url.suffix
        else:
            domain = parsed_url.domain
        netloc = urlparse.urlparse(row[-1]).netloc
        row[-1:-1] = [domain]
        row[-1:-1] = [netloc]
        cur.execute('select * from ' + labels_table
                    + ' where id=?;', (row[0], ))
        labels_row = list(cur.fetchone())
        row[1:1] = labels_row[1:]
        cur.execute('insert into ' + history_table + ' values '
                    + '(' + ', '.join(['?'] * len(row)) + ');', tuple(row))
        i += 1
        if i % 500000 == 0:
            stderr.write('\t' + str(i) + ' rows inserted...\n')
    stderr.write('... done\n')
    
    stderr.write('creating index on ' + history_table + ' (id)... ')
    cur.execute('create index ' + history_table
                + '_id on ' + history_table + ' (id);')
    stderr.write('done\n')
    
    stderr.write('committing... ')
    database.commit()
    stderr.write('done\n')



find_ids()
create_labels_table()
insert_labels()
create_history_table()
insert_history()

