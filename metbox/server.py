from flask import Flask, url_for
import csv

app = Flask(__name__)

# -----------------------------------------------------------
# HOME PAGE — shows just "Human"
# -----------------------------------------------------------
@app.route("/")
def homepage():
    html = '<link rel="stylesheet" href="{}">'.format(url_for('static', filename='styles.css'))
    html += (
        '<main class="container">'
        '<h1>Organisms</h1>'
        '<ul class="compound-list">'
        f'<li><a href="/human">Human</a></li>'
        '</ul>'
        '</main>'
    )
    return html


# -----------------------------------------------------------
# HUMAN PAGE — shows list of human metabolites
# -----------------------------------------------------------
@app.route("/human")
def metabolite_list():
    with open('human_mets_new.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        compounds = {}

        # collect compound_id → full_name pairs
        for row in reader:
            compound_id = row["Compound_ID"]
            full_name = row.get("fullName", "Unknown name")
            if compound_id not in compounds:
                compounds[compound_id] = full_name

        # sort alphabetically by full name
        sorted_compounds = sorted(compounds.items(), key=lambda x: x[1].lower())

        html = '<link rel="stylesheet" href="{}">'.format(url_for('static', filename='styles.css'))
        html += '<main class="container"><h1>Human Metabolites</h1><ul class="compound-list">'
        for compound_id, full_name in sorted_compounds:
            html += f'<li><a href="/compound/{compound_id}">{full_name}</a></li>'
        html += '</ul>'
        html += "<a class='back' href='/'>← Back to main</a></main>"
        return html


# -----------------------------------------------------------
# COMPOUND DETAILS PAGE — shows pathways and info
# -----------------------------------------------------------
@app.route('/compound/<compound_id>')
def show_compound(compound_id):
    with open('human_mets_new.csv', newline='') as csvfile:
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
            html += "<a class='back' href='/human'>← Back to Human Metabolites</a></main>"
            return html

        else:
            return f"<main class='container'><h1>Compound {compound_id} not found</h1><a class='back' href='/human'>← Back</a></main>"
