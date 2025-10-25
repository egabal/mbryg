from flask import Flask
import csv

app = Flask(__name__)



@app.route("/")
def metabolite_list():
    with open('db.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        html = '<ul>'
        for row in reader:
            html += '<li><a href="/metabolite/{}">'.format(row["Compound_ID"]) + row["Pathway_Name"] + '</a></li>'
        html += '</ul>'
        return html
   

@app.route('/metabolite/<name>')
def show_metabolite(name):
    # show the user profile for that user
    return f"I will show you metabolite {name}"
