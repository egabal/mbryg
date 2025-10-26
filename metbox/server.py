from flask import Flask, url_for
import csv

app = Flask(__name__)

@app.route("/")
def metabolite_list():
    with open('db.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        html = '<link rel="stylesheet" href="{}">'.format(url_for('static', filename='styles.css'))
        html += '<main class="container"><h1>Chemical List</h1><ul class="compound-list">'
        compounds_seen = set()
        for row in reader:
            compound_id = row["Compound_ID"]
            full_name = row.get("fullName", "Unknown name")
            if compound_id not in compounds_seen:
                compounds_seen.add(compound_id)
                html += f'<li><a href="/compound/{compound_id}">{full_name}</a></li>'
        html += '</ul></main>'
        return html


@app.route('/compound/<compound_id>')
def show_compound(compound_id):
    with open('db.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)

        html = '<link rel="stylesheet" href="{}">'.format(url_for('static', filename='styles.css'))
        html += '<main class="container">'
        full_name = ""
        description = ""
        pathways = set()

        for row in reader:
            if row['Compound_ID'] == compound_id:
                if not full_name:
                    full_name = row.get("fullName", "Unknown chemical")
                    description = row.get("description", "No description available")
                pathways.add((row["Pathway_ID"], row["Pathway_Name"]))

        if full_name:
            html += f"<h1>{full_name}</h1>"
            html += f"<p><strong>Compound ID:</strong> {compound_id}</p>"
            html += f"<p><strong>Description:</strong> {description}</p>"

            html += "<h2>Associated Pathways</h2>"
            html += "<table class='data-table'><tr><th>Pathway ID</th><th>Pathway Name</th></tr>"
            for pid, pname in sorted(pathways):
                html += f"<tr><td>{pid}</td><td>{pname}</td></tr>"
            html += "</table>"
            # if row["smile"]:
            #     html += "<img src='/images/" + row["abbreviation"] + ".png'>"
            html += "<a class='back' href='/'>← Back to list</a></main>"
            return html

        else:
            return f"<main class='container'><h1>Compound {compound_id} not found</h1><a class='back' href='/'>← Back</a></main>"
