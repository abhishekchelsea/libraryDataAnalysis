import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer

# Searching books in dataset to find exact matches.

path_unq_bks = "rss/unq_bks2.csv"


def df_to_html(data):
    # Convert dataframe of exact matches into html code with
    # bootstrap sytlings

    _t = f"""<table class='table table-striped' style='table-layout:fit;'>
    <tr>
        <th>Title</th>
        <th>Author</th>
        <th>Publisher</th>
        <th>Number of copies</th>
    </tr>
    """
    for index, row in data.iterrows():
        _t += f"""
        <tr>
            <td>{row["title"]}</td>
            <td>{row["author"]}</td>
            <td>{row["publisher"]}</td>
            <td>{row["number_of_books"]}</td>
        </tr>   
        """
    return _t + "</table>"


def search_exact(auth="", pub="", title=""):

    # Finding non empty arguments
    fields = {}
    if (title != ""):
        fields["title"] = title
    if (pub != ""):
        fields["publisher"] = pub
    if (auth != ""):
        fields["author"] = auth

    # Check if there is atleast one argument.
    if(not fields):
        return "<div>You need to provide atleast one input</div>"

    # List contains title, author, and publisher details entered by user.
    # This is displayed for convenience of user
    search_query = [i for i in fields.values()]

    data = pd.read_csv(path_unq_bks, index_col=0)

    if (data is None):
        print("No dataframe selected")
        return ""

    # New dataframe for storing the search result
    res = pd.DataFrame()

    # Iterate through non empty arguments. Combine them using AND logic.
    for key, val in fields.items():
        data = data.loc[data[key].str.upper() == val]

    if (data.shape[0] <= 0):
        return f"<div class='alert alert-warning'>Sorry! We couldn't find any exact matches to {search_query} </div>"
    else:
        return f"<div class='alert alert-primary'>Showing results for {search_query}</div><div class='card'><div class='card-body' style='padding:20px;'><h3>Exact matches ({data.shape[0]})</h3> " + df_to_html(data) + "</div></div>"

# function to combine features for similar searches


def combine_features(data=None, valid_args=None):

    if (data is None or valid_args is None):
        print("No dataframe selected/No arguments passed to combine")
        return

    _keys = list(valid_args.keys())

    # If you're passing scalar values, you have to pass an index
    # https://stackoverflow.com/a/17840195/12616968
    _row = pd.DataFrame(valid_args, index=[0])

    data = pd.concat([data, _row], axis=0, ignore_index=True)

    features = []

    sz = data.shape[0]

    try:
        for i in range(sz):
            fea = ""
            for j in _keys:
                fea += data[j][i] + " "
            features.append(fea)
    except:
        print(i)
    finally:
        data["combined"] = features
        return data

# Search similar books based on cosine similarity.


def search_similar(auth="", pub="", title=""):

    valid_args = {}

    if (title != ""):
        valid_args["title"] = title
    if (pub != ""):
        valid_args["publisher"] = pub
    if (auth != ""):
        valid_args["author"] = auth

    if (not valid_args):
        return ""

    data = pd.read_csv(path_unq_bks, index_col=0)

    if (data is None):
        return "<div class='alert alert-danger'>No data frame selected</div>"

    _temp = combine_features(
        data=data[list(valid_args.keys())], valid_args=valid_args)

    cm = CountVectorizer().fit_transform(_temp["combined"])

    # get cosine similarity mtx
    cs = cosine_similarity(cm)

    index = cs.shape[0]-1  # index of the added row

    a = list(enumerate((cs[index])))

    # Sort scores in descending order. More score means higher similarity
    sorted_scores = sorted(a, key=lambda x: x[1], reverse=True)

    _html = "<table class ='table table-striped' style='table-layout: fixed;'><tr><th>Title</th><th>Author</th><th>Publisher</th><th>Number of copies</th><th>Score</th></tr>"

    count = 0
    for i in sorted_scores[1:]:
        if (i[1] <= 0):
            continue
        try:
            _html += f"""
            <tr>
                <td>{data[data.index == i[0]]['title'].values[0]}</td>
                <td>{data[data.index == i[0]]['author'].values[0]}</td>
                <td>{data[data.index == i[0]]['publisher'].values[0]}</td>
                <td>{data[data.index == i[0]]['number_of_books'].values[0]}</td>
                <td>{round(i[1], 2)}</td>
            </tr>
            """
            count += 1
        except IndexError:
            continue

    if (count == 0):
        return f"<div class='alert alert-warning'>Sorry! We couldn't find any exact matches to {[i for i in valid_args.values()]} </div>"

    _html += "</table>"

    _prefix = f"""
    <div class='card'>
    <div class='card-body' style='padding:20px;'>
    </h2><h3>Similar results ({count})</h3>
    """

    return _prefix + _html + "</div></div>"
