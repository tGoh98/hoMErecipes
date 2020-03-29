from difflib import SequenceMatcher
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import requests
import re

def formatIng(i):
    ri = re.sub(r'\b\d[/\d().\- ]*(cup|teaspoon|grams|ounces|ounce|tablespoon)?s?[\) of]*', "", i)
    ri = re.sub(r'  ',"",ri)
    ri = re.sub(r'--'," ",ri)
    ri = re.sub(r'\(([\S ])*\)', '', ri)
    ri = re.sub(r'reduce[\S ]*','',ri)
    ri = re.sub(r':[\S ]*','',ri)
    ri = re.sub(r'enough'," ",ri)
    ri = re.sub(r'to make'," ",ri)
    ri = re.sub(r'  ',"",ri)
    return ri

def makesubdict(l):
    req  = requests.get(l)
    data = req.text
    soup = BeautifulSoup(data,features="lxml")
    t = soup.findAll("div", {"class":"component table"})

    nt = soup.findAll('table')[0]

    rows = nt.findAll('tr')
    rowtext = lambda cols: [cols[i].get_text().strip("\n") for i in [0,2]] #range(len(cols))
    tabletext = [rowtext(rows[i].findAll('td')) for i in range(1,len(rows))]
    tbdf = pd.DataFrame(tabletext)
    tbdf.columns = ["from","tou"]
    #colsmax = max(tbdf['tou'].map(lambda x: x.count("OR")))
    tbdf['toff'] = tbdf['tou'].map(lambda x: x.split("OR"))
    tbdf['tof'] = tbdf['toff'].map(lambda x:[formatIng(i) for i in x])
    tbdf['from'] = tbdf['from'].map(lambda x: x.lower().replace("-"," "))
    return tbdf

def matching(ingname):
    x = ingname.lower()
    tbdf = makesubdict("https://www.allrecipes.com/article/common-ingredient-substitutions/")
    tbdf['test'] = tbdf['from'].map(lambda y: strdist(x,y))
    toret = tbdf[tbdf.test > 0].sort_values("test",ascending = False)
    return toret[['from','tof','test']]

def strdist(x,y):
    rt = 0
    if (sum([1 if xc in y else 0 for xc in x]) / len(x)) > 0.8:
        v = np.var([y.find(xc) if xc in y else 0 for xc in x]) / len(x)
        if (v) < 0.3:
            rt = rt + (1-v)
    xs = x.split(" ")
    ys = y.split(" ")
    s = sum([1 if xsc in ys else 0 for xsc in xs])
    if (s) > 0: #/ len(y.split(" "))) >= 0.5:
        rt = rt + s
    smr = SequenceMatcher(None, x, y).ratio()
    rt = rt + smr if smr > 0.8 else rt + 0
    return rt

def takeIngs(rings):
	mi = [i.sname for i in rings]
	l = {}
	for x in mi:
	    smx = matching(x)
	    if len(smx) > 0:
	        mt = max(smx.test)
	        smxt = smx[smx.test == mt]
	        smxt.set_index(['from'],inplace = True)
	        t = smxt["tof"].map(lambda x: [i.strip("\xa0") for i in x]).to_dict()
	        l[x] = t
	return l