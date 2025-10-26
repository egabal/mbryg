from flask import Flask, url_for
import csv

app = Flask(__name__)
DB_FILE = "db.csv"


@app.route("/")
def metabolite_list():
    with open(DB_FILE) as csvfile:
        reader = csv.DictReader(csvfile)
        html = '<link rel="stylesheet" href="{}">'.format(
            url_for("static", filename="styles.css")
        )
        html += '<main class="container"><h1>Metabolite List</h1><ul class="compound-list">'
        metabolites = dict()
        for row in reader:
            name = row.get("fullName", "Unknown name")
            metabolites[name] = row

        for name in sorted(metabolites):
            rec = metabolites[name]
            abbr = rec["abbreviation"]
            # html += f'<li><a href="/compound/{compound_id}">{full_name} = {compound_id}</a></li>'
            html += f'<li><a href="/metabolite/{abbr}">{name}</a></li>'
        html += "</ul></main>"
        return html


@app.route("/metabolite/<name>")
def show_metabolite(name):
    with open(DB_FILE) as csvfile:
        reader = csv.DictReader(csvfile)

        html = '<link rel="stylesheet" href="{}">'.format(
            url_for("static", filename="styles.css")
        )
        html += '<main class="container">'
        full_name = ""
        description = ""
        pathways = set()

        record = None
        for row in reader:
            if row["abbreviation"] == name:
                record = row

        if record:
            pathway_ids = record.get("Pathway_ID").split(";")
            pathway_names = record.get("Pathway_Name").split(";")
            pathways = zip(pathway_names, pathway_ids)

            full_name = record.get("fullName", "Unknown chemical")
            description = record.get(
                "description", "No description available"
            )
            # pathways.add((row["Pathway_ID"], row["Pathway_Name"]))
            html += f"<h1>{full_name}</h1>"
            html += f"<p><strong>Metabolite:</strong> {name}</p>"
            html += f"<p><strong>Description:</strong> {description}</p>"

            html += "<h2>Associated Pathways</h2>"
            html += "<table class='data-table'><tr><th>Pathway ID</th><th>Pathway Name</th></tr>"
            for pid, pname in sorted(pathways):
                html += f"<tr><td>{pid}</td><td>{pname}</td></tr>"
            html += "</table>"

            if row["smile"]:
                html += "<img src='/static/images/" + record["abbreviation"] + ".png'>"

            html += "<a class='back' href='/'>← Back to list</a></main>"
            return html

        else:
            return f"<main class='container'><h1>Compound {compound_id} not found</h1><a class='back' href='/'>← Back</a></main>"


@app.route("/compound/<compound_id>")
def show_compound(compound_id):
    with open(DB_FILE) as csvfile:
        reader = csv.DictReader(csvfile)

        html = '<link rel="stylesheet" href="{}">'.format(
            url_for("static", filename="styles.css")
        )
        html += '<main class="container">'
        full_name = ""
        description = ""
        pathways = set()

        for row in reader:
            print(row)
            if row["Compound_ID"] == compound_id:
                if not full_name:
                    full_name = row.get("fullName", "Unknown chemical")
                    description = row.get(
                        "description", "No description available"
                    )
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
            if row["smile"]:
                html += "<img src='/images/" + row["abbreviation"] + ".png'>"
            html += "<a class='back' href='/'>← Back to list</a></main>"
            return html

        else:
            return f"<main class='container'><h1>Compound {compound_id} not found</h1><a class='back' href='/'>← Back</a></main>"
