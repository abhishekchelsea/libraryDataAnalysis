import pandas as pd
import json
import re
import os

path_crs_codes = "/home/aca/Documents/S6_Lab/Projects/libraryDataAnalysis/model/feeling_lucky/course_codes.json"
path_recom_books = "/home/aca/Documents/S6_Lab/Projects/libraryDataAnalysis/model/feeling_lucky/recommended_bks"


def report_mail(sub="", body=""):
    return f"""<a href= "mailto:group10@gecskp.ac.in?subject={sub}&body={body}"> Report</a> """


MIN_B = 2019
MAX_B = 2022

batch_sem = {
    '2019': "7",
    '2020': "5",
    '2021': "3",
    '2022': "1"
}


def filter(data=None):

    if data is None:
        return None

    dlt = []

    for k in data.keys():

        # Empty string keys
        if re.match(r'^\s*$', str(k)) or len(data[k]) <= 0:
            dlt.append(k)

    for i in dlt:
        del data[i]

    if len(data.keys()) == 0:
        return None

    return data


def to_table(data=None):

    data = filter(data)

    if data is None:  # 💡
        return ""

    _table = """
    <div class='card'><div class='card-body' style='padding:20px'>
    <table class='table table-striped' style='table-layout: fixed;'><tr>"""

    heads = [
        "Title", "Author", "Publication", "Number of copies", 'id', '?'
    ]

    for h in heads:
        _table += f"<th>{h}</th>"

    _table += "</tr>"

    for k in data.keys():
        for l in data[k]:
            _table += f"""
            <tr>
                <td>{l['title']}</td>
                <td>{l['author']}</td>
                <td>{l['publisher']}</td>
                 <td>{l['number_of_books']}</td>
                <td>{l['book_id']}</td>
                <td>
                    <abbr style="text-decoration:none"
                        title = "May be useful for course {l['course_code']}. Looks similar to {k} ({l['score']})">💡</abbr></td>
            </tr>
            """

    return _table + "</table></div></div><div style='height:20px'></div>"


def getDetails(adm_no):
    try:
        df = pd.read_csv(
            "/home/aca/Documents/S6_Lab/Projects/libraryDataAnalysis/venv/recomm/rss/lib_user.csv")
        df1 = df[df['id'] == adm_no.upper()][['department', 'batch']]
        batch = int(df1['batch'].values[0])
        dept = str(df1['department'].values[0])
        if dept in ['IT', 'CS', 'EEE', 'EC', 'CE', 'ME']:
            if batch >= MIN_B and batch <= MAX_B:
                return [dept, batch_sem[str(batch)]]
        return False
    except:
        return False


def feelingLucky(adm_no):

    try:

        details = getDetails(adm_no)  # dept, sem

        print(details)

        if details[1] == '1' or details[1] == '2':
            details[0] = 'Any'

        if not details:
            return "Couldn't find user details. " + report_mail(sub=f"UserNotFound:{adm_no}", body="Please give additional details if any."),  "Have you ever visited library?"

        crs_codes = None
        tables = ""

        with open(path_crs_codes, 'r') as c:
            try:
                crs_codes = json.load(c)[details[0]][details[1]]
            except:
                return "Error while reading course codes"

        for i in crs_codes:
            with open(os.path.join(path_recom_books, i + ".json"), 'r') as f:
                bks = json.load(f)
                tables += to_table(bks)

        if re.match(r'^\s*$', tables):
            tables = "Sorry No recommendation at this time. Please report to help us improve your experience next time " + \
                report_mail(sub=f"NoSuggestions:{adm_no}")

        return tables, f"Suggestions based on S{details[1]} syllabus"
    except:
        return "", ""
