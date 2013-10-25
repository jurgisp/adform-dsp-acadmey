import re
import urllib2
import itertools
from collections import Counter
import cPickle as pickle
import random
import tldextract
import operator as op
import string
import sys
import argparse

rubbish = set(['adservinginternational.com', 'adnxs.com','doubleclick.net',
               'emediate.eu', 'google.com', 'google.dk', 'emediate.se',
               'adform.net', 'google.co.in', 'specificclick.net', 'sharedaddomain.com'
               ])

def get_domain (url):
    a = tldextract.extract(url)
    return a.domain + '.' + a.suffix

def parse_url (url = '', query=True):
    matches = re.findall(r'=http[s]?(?:(?:[:])|(?:%3A))(?:(?:/)|(?:%2F)){2}([^&;]*)', url)    
    if matches: 
        for u in matches:
            u = urllib2.unquote(u)
            if get_domain(u) not in rubbish:
                yield u
    else:
        yield urllib2.unquote(url)


def produrator (label, set='training', n_files=2):
    if set == 'training':
        suffixes = ['000001', '000008', '000010', '000011', '000012', '000013',
                    '000014', '000015', '000016', '000017', '000018', '000019',
                    '000020', '000021', '000022', '000023', '000024', '000025',
                    '000026', '000027', '000028', '000029', '000030', '000031',
                    '000032', '000033', '000034', '000035', '000036', '000037',
                    '000038', '000039', '000040', '000041', '000042', '000043',
                    '000044', '000045', '000046', '000047', '000048', '000049',
                    '000066', '000067', '000068', '000069', '000071'][:n_files]
    else:
        #suffixes = ['ALL_MOD_9']
        suffixes = ['000001', '000008', '000010', '000011', '000012', '000013']
    
    for suffix in suffixes:
        file = open ('cookies/20131015_female/8191ca07-4888-4484-8bf6-44bdb7c66a77_' + suffix)
        for line in file.readlines():
            (browser, os, screensize, country, clicker, urls, domains,
                verticals, agent, cookiemod, id, segments, negative,
                positive) = line.split('\t')
            id = int(id)    
               
            if ((set == 'training' and cookiemod == '9') or
                (set == 'testing' and cookiemod != '9')):
                continue
                
            if label in segments:
                 label_class = 1
            elif label[:label.find('_')] in segments:
                label_class = 0
            else:
                continue
                
            history = []
            
            urls = re.split(';https?://', urls)
            if urls:
                urls[0] = re.sub(r'https?://', '', urls[0])
                for url in urls:
                    for u in parse_url(url):
                        history.append(u)
            
            domains = domains.split(';')
           
            for u in domains:
                history.append(u)
            yield (int(id), label_class, history)
            #exit()
        file.close()

        
        