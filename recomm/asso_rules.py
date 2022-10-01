import pandas as pd
import datetime as dt
import pickle as pk
from mlxtend.preprocessing import TransactionEncoder
from mlxtend.frequent_patterns import association_rules
from mlxtend.frequent_patterns import fpgrowth
import numpy as np


# convert data frame to table
def abbr(lst=None, df=None):
    _html = "("

    for i in lst:
        abbr_title = f"""title: {df.iloc[i, :]["title"]}, author: {df.iloc[i, :]["author"]}, publisher: {df.iloc[i, :]["publisher"]}, Copies: {df.iloc[i, :]["number_of_books"]}"""
        _html += f""" <abbr title="{abbr_title}">{i}</abbr>,"""

    print("finished abbr")
    return _html + ")"


def convert_to_table(data=None, args=None):

    if (data is None):
        return ""

    _table = """
    <div class='card'><div class='card-body' style='padding:20px'>
    <table class='table table-striped' style='table-layout: fixed;'><tr>"""

    for j in args["columns_in_result"]:
        _table += f"""<th>{j}</th>"""

    _table += "</tr>"

    unq_bks = pd.read_csv("rss/unq_bks2.csv", index_col=0)

    for index, row in data.iterrows():

        _table += "<tr>"

        for j in args["columns_in_result"]:
            if (j == "antecedents" or j == "consequents"):
                _table += f"""<td>{abbr(df=unq_bks, lst=list(row[j]))}</td>"""
            else:
                _table += f"""<td>{row[j]}</td>"""

        _table += "</tr>"

    print("finished convert to table")

    return _table + "</table></div></div>"


def fp(df2, min_support=0.001, metric=None, min_threshold=None, args=None):
    # running the fpgrowth algorithm
    assert min_support > 0
    res = fpgrowth(df2, min_support=min_support, use_colnames=True)

    res1 = association_rules(
        res,
        metric=metric,
        min_threshold=min_threshold
    )

    res2 = res1.sort_values(args["sort_results_by"], ascending=False)

    print("finished fp")

    return res2[res2.columns.intersection(args["columns_in_result"])]


def prepare_data(args=None):

    df2 = False

    df = pd.read_csv("rss/book_issue_with_book_id.csv")
    df["issue_date"] = pd.to_datetime(df["issue_date"])

    print(f"Size of data: {df.shape}")
    print(args)

    fdf = df[(df['issue_date'] >= dt.datetime.strptime(args["start_date"], "%Y-%m-%d"))
             & (df['issue_date'] <= dt.datetime.strptime(args["end_date"], "%Y-%m-%d"))
             & (df["department"].isin(args["depts"]))]

    total_transactions = (fdf.shape)[0]

    if (total_transactions > 0):
        min_support = int(args["min_supp_count"])/total_transactions
    else:
        return fdf, None

    # TODO: Find average support

    items = []

    unq_dates = fdf['issue_date'].drop_duplicates().tolist()

    for i in unq_dates:
        temp = fdf[fdf['issue_date'] == i]
        unq_ids = temp['id'].drop_duplicates().tolist()
        for j in unq_ids:
            items.append(temp[temp['id'] == j]['book_id'].tolist())

    te = TransactionEncoder()
    te_ary = te.fit(items).transform(items)

    df2 = pd.DataFrame(te_ary, columns=te.columns_)

    print("finshed preparedata")
    return df2, min_support


def valid(args=None):
    if (args):  # check if args dictionary is empty
        if (len(args["depts"]) != 0 and len(args["columns_in_result"]) != 0 and len(args["sort_results_by"]) != 0):
            if ("nan" in args["depts"]):
                args["depts"][args["depts"].index("nan")] = np.nan

            if (dt.datetime.strptime(args["start_date"], "%Y-%m-%d") < dt.datetime.strptime(args["end_date"], "%Y-%m-%d")):
                if(args["min_supp_count"] > 0):
                    if(args["metric"] == "confidence"):
                        if(args["threshold"] <= 1):
                            return True
                    elif(args["metric"] == "lift"):
                        return True
    print('finished valid check')
    return False


def mine_rules(args={}):

    if(not valid(args=args)):
        return "Please select valid arguments"  # TODO: Show some tips

    data, min_support = prepare_data(args=args)

    if (min_support == None):
        return "No data"

    fp_res = fp(
        data,
        min_support=min_support,
        metric=args["metric"],
        min_threshold=float(args["threshold"]),
        args=args
    )

    print("Finished mine_ruless")

    return convert_to_table(data=fp_res, args=args)
