import numpy as np
import pandas as pd
from functools import reduce
import requests
import dill
# import ray #ray
from . import submatcher as sm 

headers = {
            'x-rapidapi-host': "spoonacular-recipe-food-nutrition-v1.p.rapidapi.com",
            'x-rapidapi-key': "12fea31ee1msh146064fe6ca066fp12ca78jsn6c3792ca5c3d"
            }

class GetRecipies:
    
    def __init__(self, foodlist, recnum = 2):
        self.foodlist = foodlist
        self.response = None
        self.responsedict = None
        self.recser = None
        self.rec = recnum
        # self.get()
    
    def __str__(self):
        if (type(self.recser) != pd.DataFrame):
            print(self.recser)
            return ""
        elif self.response != None:
            return f" {self.response.status_code} not yet processed!"
        else:
            return "not yet gotten!"
    
    def save(self):
        if (type(self.recser) != pd.DataFrame):
            self.recser.to_csv(f"gr{self.foodlist}.csv",header = True)
            print ("dumped processed to csv")
        elif (self.response):
            with open('resp.pkl', 'wb') as f:
                dill.dump(self.response, f)
            print ("dumped response to pickle")
        else:
            print ("nothing to save")

    def get(self):
        url = "https://spoonacular-recipe-food-nutrition-v1.p.rapidapi.com/recipes/findByIngredients"
        inpstr = reduce(lambda a,b: f"{a}, {b}", self.foodlist)
        querystring = {"number":f"{self.rec}","ranking":"1","ignorePantry":"false","ingredients":f"{inpstr}"}
        response = requests.request("GET", url, headers=headers, params=querystring)
        self.response = response
        self.process()

    def process(self):
        recipies = pd.DataFrame.from_dict(self.response.json())
        self.recser = recipies.apply(lambda r: Recipie(r),axis = 1,raw = False)
   
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
    return gad if type(gad) != list else [g.name for g in gad]

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

        self.getRecipie()

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
        url = f"https://spoonacular-recipe-food-nutrition-v1.p.rapidapi.com/recipes/{self.id}/information"
        self.response = requests.request("GET", url, headers=headers)
        self.setVars()

    def save(self):
        if (self.response):
            with open('respr.pkl', 'wb') as f:
                dill.dump(self.response, f)
            print ("dumped response to pickle")    

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

    def __str__(self):
        top = [a for a in dir(self) if a[0] != "_"]
        topl = [f"{d} - {getattr(self,d)}" for d in top]
        return str(topl)