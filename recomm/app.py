# FLASK_APP=app.py FLASK_DEBUG=1 flask run
# source venv/bin/activate
from flask import Flask, render_template, request, redirect, url_for
import asso_rules as ar
import feeling_lucky as fl
import pandas as pd
import search_dataset as sd
import json

app = Flask(__name__)
app.debug = True


@app.route("/", methods=['GET', 'POST'])
def home():

    print("inside home")

    res_exact = ""
    res_similar = ""

    if request.method == "POST":
        print("post request rcvd")

        title = request.form['bk_title'].upper()
        author = request.form['bk_author'].upper()
        publisher = request.form['bk_publisher'].upper()

        res_exact = sd.search_exact(
            title=title,
            auth=author,
            pub=publisher
        )

        res_similar = sd.search_similar(
            title=title,
            auth=author,
            pub=publisher
        )

    return render_template("index.html", res_exact=res_exact, res_similar=res_similar)


@app.route("/asso-results/<data>")
def show_result(data):
    args = json.loads(data)
    res = ar.mine_rules(args=args)
    return render_template("association_rules_results.html", args=args, res=res)


@app.route("/association-rules", methods=["GET", "POST"])
def asso():
    attrbs = {"start_date": "2016-05-06", "end_date": "2022-06-08", "min_supp_count": 10,
              "metric": "confidence", "threshold": 0.5, "save_result": "yes", "depts": [], "sort_results_by": [], "columns_in_result": []}
    res = ""

    if request.method == "POST":
        attrbs["start_date"] = request.form["start_date"]
        attrbs["end_date"] = request.form["end_date"]
        attrbs["min_supp_count"] = int(request.form["min_supp_count"])
        attrbs["metric"] = request.form["metric"]
        attrbs["threshold"] = float(request.form["threshold"])
        attrbs["depts"] = request.form.getlist("depts")
        attrbs["columns_in_result"] = request.form.getlist("columns_in_result")
        attrbs["sort_results_by"] = request.form.getlist("sort_results_by")

        data = json.dumps(attrbs)

        return redirect(url_for("show_result", data=data))
        # res = ar.mine_rules(args=attrbs)

    return render_template("association_rules.html", attrbs=attrbs, res=res)


@app.route("/feeling-lucky", methods=['GET', 'POST'])
def lucky():
    adm_no = ''
    msg = ''
    res = ''
    if request.method == 'POST':
        adm_no = request.form['adm_no']
        res, msg = fl.feelingLucky(adm_no)

    return render_template("feeling_lucky.html", res=res, adm_no=adm_no, msg=msg)


if __name__ == "__main__":
    app.run(debug=True)
