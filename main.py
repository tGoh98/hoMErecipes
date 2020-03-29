# import json, createpeople, modeleval
from flask import Flask, render_template, json, request, redirect, url_for

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


@app.route('/results')
def results():
        return render_template("results.html")


if __name__ == '__main__':
    app.run(debug=True)
