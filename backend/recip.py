import numpy as np
import pandas as pd
from functools import reduce
import requests
import dill
import ray #ray
import hashlib
from os import path
# from . import submatcher as sm
import submatcher as sm

headers = {
            'x-rapidapi-host': "spoonacular-recipe-food-nutrition-v1.p.rapidapi.com",
            'x-rapidapi-key': "12fea31ee1msh146064fe6ca066fp12ca78jsn6c3792ca5c3d"
            }

class GetRecipies:
    
    def __init__(self, foodlist, recnum = 2):
        self.response = None
        self.responsedict = None
        self.recser = None
        self.c = False
        self.rec = recnum
        foodlist.sort()
        self.foodlist = foodlist
        s = reduce(lambda a,b: f"{a}, {b}", foodlist)
        self.hash = int(hashlib.sha1(f"{self.rec}{s}".encode('utf-8')).hexdigest(), 16) % (10 ** 8)

        if path.exists(f'c/{self.hash}.pkl'):
        	print("Recipe cache found")
        	dbfile = open(f'c/{self.hash}.pkl', 'rb') 
        	self.response =  dill.load(dbfile)
        	self.c = True
        else:
        	print("No recipe cache found")
        	self.get()
        self.process()
    
    def __str__(self):
        if (type(self.recser) != pd.DataFrame):
            print(self.recser)
            return ""
        elif self.response != None:
            return f" {self.response.status_code} not yet processed!"
        else:
            return "not yet gotten!"
    
    def save_res(self):
        if (not self.c):
            with open(f'c/{self.hash}.pkl', 'wb') as f:
                dill.dump(self.response, f)
            print ("dumped recipes to pickle")

    def get(self):
        print(f"getting {self.foodlist} recipe")
        url = "https://spoonacular-recipe-food-nutrition-v1.p.rapidapi.com/recipes/findByIngredients"
        inpstr = reduce(lambda a,b: f"{a}, {b}", self.foodlist)
        querystring = {"number":f"{self.rec}","ranking":"1","ignorePantry":"true","ingredients":f"{inpstr}"}
        response = requests.request("GET", url, headers=headers, params=querystring)
        self.response = response

    def process(self):
        recipies = pd.DataFrame.from_dict(self.response.json())
        self.recser = recipies.apply(lambda r: Recipie(r),axis = 1,raw = False)
        self.save_res()
   
    def to_json(self):
        full = {}
        for i in range(len(self.recser)):
            r = self.recser.iloc[i]
            full[r.name] = r.to_json()
        return full



dct = ['id', 'amount', 'unit', 'originalString', 'image', 'name']

parseIngDict = lambda ld: [[d[i] for i in dct] for d in ld]

def parseIngs(ser):
    psed = parseIngDict(ser)
    # print(ser ,"\n\n\n")
    return [Ingredient(d) for d in psed]

def prf(self,d):
    gad = getattr(self,d)
    # print(type(gad),gad)
    return gad if type(gad) != list else [g.sname for g in gad]

class Recipie:

    def __init__(self, s):   
        '''
        Class built to hold and host a recipie from spoonacular API
        '''
        # step 1
        self.id = s.id
        self.name = s.title
        self.imglink = s.image
        self.missedCount = s.missedIngredientCount
        self.usedCount = s.usedIngredientCount
        # self.unusedCount = len(s.unusedIngredients)
        self.missedIngs = parseIngs(s.missedIngredients)
        # self.unusedIngs = parseIngs(s.unusedIngredients)
        self.usedIngs = parseIngs(s.usedIngredients)
        self.response = None
        self.c = False


        if path.exists(f'c/{self.id}.pkl'):
        	print(f"recipe {self.name} cache found")
        	dbfile = open(f'c/{self.id}.pkl', 'rb') 
        	self.response =  dill.load(dbfile)
        	self.c = True
        else:
        	print(f"No {self.name} cache found")
        	self.getRecipie()

        self.setVars()
        self.save()

    def __str__(self):

        top = [a for a in dir(self) if not a in dir(Recipie)]
        
        topl = [f"{d} - {prf(self,d)}" for d in top]
        for l in topl:
            print(l)
        return ""
    
    def to_json(self):
        dr = dir(Recipie)
        dr.append('response')
        top = [a for a in dir(self) if not a in dr]
        di = {d:prf(self,d) for d in top}
        di['cuisines'] = di['cuisines'].tolist()
        return di
    
    # @ray.remote
    def getRecipie(self):
        print(f"getting {self.name} recipe")
        url = f"https://spoonacular-recipe-food-nutrition-v1.p.rapidapi.com/recipes/{self.id}/information"
        self.response = requests.request("GET", url, headers=headers)

    def save(self):
        if (not self.c):
            with open(f'c/{self.id}.pkl', 'wb') as f:
                dill.dump(self.response, f)
            print (f"dumped {self.name} to pickle")    

    def setVars(self):
        rj = self.response.json()
        self.attrs = {i:rj[i] for i in ['vegetarian', 'vegan', 'glutenFree', "dairyFree"]}
        self.urls = {"source": rj['sourceUrl'], "img": rj['image'] }

        self.price = rj['pricePerServing']
        ## INGREDIENTS TRUE FALSE
        self.serving = rj['servings']
        self.cuisines = np.array(rj['cuisines'])
        # self.summary = rj['summary']
        self.subIngs = sm.takeIngs(self.missedIngs)
        
class Ingredient:

    '''
    Class built to hold and host an Ingredient from spoonacular API
    '''
    def __init__(self,inp):
        self.name = inp[3]
        self.amt = inp[1]
        self.unit = inp[2]
        self.id = inp[0]
        self.link = inp[4]
        self.sname = inp[5]
        # self.rname = sm.formatIng(self.name)

    def __str__(self):
        top = [a for a in dir(self) if a[0] != "_"]
        topl = [f"{d} - {getattr(self,d)}" for d in top]
        return str(topl)