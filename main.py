from backend import recip
from flask import Flask, render_template, json, request, redirect, url_for
from collections import defaultdict

app = Flask(__name__)

@app.route('/', methods=['POST', 'GET'])
def index():
        did_update = False

        if request.method == 'POST':
                if (len(request.form) <= 0):
                        did_update = True
                else :
                        json.dump(request.form, open('selectedIng.json', 'w'))
                        return redirect(url_for('loading'))

        dairyIng = json.load(open("db/dairyIngredients.txt", "r"))
        vegetablesIng = json.load(open("db/vegetablesIngredients.txt", "r"))
        proteinsIng = json.load(open("db/proteinsIngredients.txt", "r"))
        fruitsIng = json.load(open("db/fruitsIngredients.txt", "r"))
        bakingIng = json.load(open("db/bakingIngredients.txt", "r"))
        oilsIng = json.load(open("db/oilsIngredients.txt", "r"))
        nutsIng = json.load(open("db/nutsIngredients.txt", "r"))
        sugarsIng = json.load(open("db/sugarsIngredients.txt", "r"))

        return render_template("index.html", dairyIng=dairyIng, vegetablesIng=vegetablesIng,
                proteinsIng=proteinsIng, fruitsIng=fruitsIng, bakingIng=bakingIng, 
                oilsIng=oilsIng, nutsIng=nutsIng, sugarsIng=sugarsIng, did_update=did_update)



@app.route('/loading')
def loading():
        return render_template("loading.html")


@app.route('/results', methods=['POST', 'GET'])
def results():
        cuisinesDict = json.load(open("db/cuisinesDict.json"))
        attrsDict = json.load(open("db/attrsDict.json"))

        if (request.method == 'POST'):
                attrList = set([])
                cuList = set([])
                for fil in request.form.keys():
                        if fil in cuisinesDict:
                                cuisinesDict[fil] = True
                                cuList.add(fil)
                        if fil in attrsDict:
                                attrsDict[fil]["isChecked"] = True
                                attrList.add(fil)

                # Process data with filters (no space, lower case)
                allIng = defaultdict(dict)
                foodSubs = defaultdict(dict)
                missingno = defaultdict(dict)

                allr = json.load(open("allRecipes.json", "r"))

                for recipe in allr:
                        skip = False
                        for attr in attrList:
                                if not attrsDict[attr]["isChecked"] or not allr[recipe]["attrs"][attrsDict[attr]["attrName"]]:
                                        skip = True
                                        break
                        if not skip:
                                for cu in cuList:
                                        if not cuisinesDict[cu] or cu not in allr[recipe]["cuisines"]:
                                                skip = True
                                                break
                        if skip:
                                continue
                        if (allr[recipe]["missedCount"] == 0):
                                # allIng
                                allIng[recipe]["attrs"] = allr[recipe]["attrs"]
                                allIng[recipe]["cuisines"] = allr[recipe]["cuisines"]
                                allIng[recipe]["source"] = allr[recipe]["urls"]["source"]
                                allIng[recipe]["img"] = allr[recipe]["urls"]["img"]
                                # Used ingredients
                                tempStr = ""
                                for ing in allr[recipe]["usedIngs"]:
                                        tempStr += ing + ", "
                                allIng[recipe]["usedIngs"] = tempStr.strip(", ")

                        else:
                                # missingno
                                missingno[recipe]["attrs"] = allr[recipe]["attrs"]
                                missingno[recipe]["cuisines"] = allr[recipe]["cuisines"]
                                missingno[recipe]["source"] = allr[recipe]["urls"]["source"]
                                missingno[recipe]["img"] = allr[recipe]["urls"]["img"]
                                # Missed ingredients
                                missingno[recipe]["missedCount"] = allr[recipe]["missedCount"]
                                missingStr = ""
                                for ing in allr[recipe]["missedIngs"]:
                                        missingStr += ing + ", "
                                missingno[recipe]["missedIngs"] = missingStr.strip(", ")
                        
                                # foodSubs
                                foodSubs[recipe]["attrs"] = allr[recipe]["attrs"]
                                foodSubs[recipe]["cuisines"] = allr[recipe]["cuisines"]
                                foodSubs[recipe]["source"] = allr[recipe]["urls"]["source"]
                                foodSubs[recipe]["img"] = allr[recipe]["urls"]["img"]
                                # Substituted ingredients
                                subMsg = ""
                                for origIng in allr[recipe]["subIngs"]:
                                        subMsg += origIng + " can be substituted with: "
                                        for subIng in allr[recipe]["subIngs"][origIng]:
                                                for subIngComp in allr[recipe]["subIngs"][origIng][subIng]:
                                                        subMsg += subIngComp + ", "
                                        subMsg += "\n"
                                                
                                foodSubs[recipe]["subIngs"] = subMsg.strip(", ")
        else:
                
                # Get recipes
                # TODO: UNCOMMENT THIS WHEN IMPORT WORKS
                # inp = json.load(open("selectedIng.json", "r"))
                # allr = recip.GetRecipies(inp)
                # allr.to_json()

                # TODO: REMOVE LOADING THIS TEST FILE
                allr = json.load(open("backend/testout.json"))

                # Save working copy for filtering
                json.dump(allr, open("allRecipes.json", "w"))

                # Process data
                allIng = defaultdict(dict)
                foodSubs = defaultdict(dict)
                missingno = defaultdict(dict)

                for recipe in allr:
                        if (allr[recipe]["missedCount"] == 0):
                                # allIng
                                allIng[recipe]["attrs"] = allr[recipe]["attrs"]
                                allIng[recipe]["cuisines"] = allr[recipe]["cuisines"]
                                allIng[recipe]["source"] = allr[recipe]["urls"]["source"]
                                allIng[recipe]["img"] = allr[recipe]["urls"]["img"]
                                # Used ingredients
                                tempStr = ""
                                for ing in allr[recipe]["usedIngs"]:
                                        tempStr += ing + ", "
                                allIng[recipe]["usedIngs"] = tempStr.strip(", ")

                        else:
                                # missingno
                                missingno[recipe]["attrs"] = allr[recipe]["attrs"]
                                missingno[recipe]["cuisines"] = allr[recipe]["cuisines"]
                                missingno[recipe]["source"] = allr[recipe]["urls"]["source"]
                                missingno[recipe]["img"] = allr[recipe]["urls"]["img"]
                                # Missed ingredients
                                missingno[recipe]["missedCount"] = allr[recipe]["missedCount"]
                                missingStr = ""
                                for ing in allr[recipe]["missedIngs"]:
                                        missingStr += ing + ", "
                                missingno[recipe]["missedIngs"] = missingStr.strip(", ")
                        
                                # foodSubs
                                foodSubs[recipe]["attrs"] = allr[recipe]["attrs"]
                                foodSubs[recipe]["cuisines"] = allr[recipe]["cuisines"]
                                foodSubs[recipe]["source"] = allr[recipe]["urls"]["source"]
                                foodSubs[recipe]["img"] = allr[recipe]["urls"]["img"]
                                # Substituted ingredients
                                subMsg = ""
                                for origIng in allr[recipe]["subIngs"]:
                                        subMsg += origIng + " can be substituted with: "
                                        for subIng in allr[recipe]["subIngs"][origIng]:
                                                for subIngComp in allr[recipe]["subIngs"][origIng][subIng]:
                                                        subMsg += subIngComp + ", "
                                        subMsg += "\n"
                                                
                                foodSubs[recipe]["subIngs"] = subMsg.strip(", ")

        return render_template("results.html", allIng=allIng, foodSubs=foodSubs, missingno=missingno,
                                                cuisinesDict=cuisinesDict, attrsDict=attrsDict)


# TODO: change to prod
if __name__ == '__main__':
    app.run(debug=True)
