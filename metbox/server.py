from flask import Flask, url_for
import csv
import os 

"""
Author : Esraa Gabal & Juliana <esraa.gabal93@gmail.com>
Date   : 2025-10-25
Purpose: pfb2025 project (CSHL: Programming for Biology)
"""

app = Flask(__name__)

# -----------------------------------------------------------
# HOME PAGE — shows Human with an icon
# -----------------------------------------------------------
@app.route('/')
def home():
    html = f'<link rel="stylesheet" href="{url_for("static", filename="styles.css")}">'
    html += f"""
    <main class="homepage">
        <img src="{url_for('static', filename='images/IM_presentation.png')}" 
             alt="MetBox Logo" class="logo">
        <h1>METBOX</h1>
        <a href="/human" class="human-link">🧬 Human Metabolites</a>
        <a href="/microbiota" class="microbiota-link">🦠 Gut Microbiota</a>

        <div class="authors">
            <p><strong>Authors:</strong> Esraa Gabal & Julianne Fazekas</p>
            <p><strong>Contact:</strong> esraa.gabal93@gmail.com, jfazekas617@gmail.com</p>
        </div>
    </main>
    """
    return html



# -----------------------------------------------------------
# HUMAN PAGE — list of metabolites
# -----------------------------------------------------------
@app.route("/human")
def metabolite_list():
    with open('human_mets.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        compounds = {}
        for row in reader:
            compound_id = row["Compound_ID"]
            full_name = row.get("fullName", "Unknown name")
            abbreviation = row.get("abbreviation")
            if compound_id not in compounds:
                compounds[compound_id] = full_name

        sorted_compounds = sorted(compounds.items(), key=lambda x: x[1].lower())

        html = '<link rel="stylesheet" href="{}">'.format(url_for('static', filename='styles.css'))
        html += '<main class="container"><h1>Metabolites</h1><ul class="compound-list">'
        for compound_id, full_name in sorted_compounds:
            html += f'<li><a href="/compound/{compound_id}">{full_name}</a></li>'
        html += '</ul>'
        html += "<a class='back' href='/'>← Back to main</a></main>"
        return html

# -----------------------------------------------------------
# COMPOUND DETAILS PAGE
# -----------------------------------------------------------
@app.route('/compound/<compound_id>')
def show_compound(compound_id):
    with open('human_mets.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)

        html = '<link rel="stylesheet" href="{}">'.format(url_for('static', filename='styles.css'))
        html += '<main class="container">'
        full_name = ""
        abbreviation = ""
        description = ""
        pathways = set()

        for row in reader:
            if row['Compound_ID'] == compound_id:
                if not full_name:
                    full_name = row.get("fullName", "Unknown chemical")
                    abbreviation = row.get("abbreviation", "N/A") 
                    image_url = url_for('static', filename=f'images/{abbreviation}.png')
                    description = row.get("description", "No description available")
                pathways.add((row["Pathway_ID"], row["Pathway_Name"]))

        if full_name:
            html += f"<h1>{full_name}</h1>"
            html += f"<p><strong>Compound ID:</strong> {compound_id}</p>"
            html += f"<p><strong>Description:</strong> {description}</p>"
            html += f'<p><img src="{image_url}" alt="{abbreviation}" style="max-width:600px; display:block; margin:15px auto;"></p>'
            html += f"<p><strong>Abbreviation:</strong> {abbreviation}</p>"

            html += "<h2>Associated Pathways</h2>"
            html += "<table class='data-table'><tr><th>Pathway ID</th><th>Pathway Name</th></tr>"
            for pid, pname in sorted(pathways):
                kegg_url = f"https://www.genome.jp/dbget-bin/www_bget?{pid}"
                html += f"<tr><td><a href='{kegg_url}' target='_blank'>{pid}</a></td><td>{pname}</td></tr>"
            html += "</table>"
            html += "<a class='back' href='/human'>← Back to Human Metabolites</a></main>"
            return html

        else:
            return f"<main class='container'><h1>Compound {compound_id} not found</h1><a class='back' href='/human'>← Back</a></main>"

# -----------------------------------------------------------
# GUT MICROBIOTA PAGE — list of species
# -----------------------------------------------------------
@app.route("/microbiota")
def species_list():
    species = []
    with open('./microbes/bacteria_sp.csv', newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if len(row) > 0:
                species.append(row[0].strip())
                break

    html = f'<link rel="stylesheet" href="{url_for("static", filename="styles.css")}">'
    html += '<main class="container"><h1>Species</h1><ul class="compound-list">'

    for name in species:
        html += f'<li><a href="/microbiota/{name}">{name}</a></li>'

    html += '</ul>'
    html += "<a class='back' href='/'>← Back to main</a></main>"
    return html

# -----------------------------------------------------------
# MICROBIOTA SPECIES PAGE — show metabolites for that species
# -----------------------------------------------------------
@app.route("/microbiota/<species_name>")
def microb_metabolite_list(species_name):
    with open('bt_pathways.csv', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)

        seen = set()
        compounds = []

        for row in reader:
            full_name_raw = row.get("fullName", "")
            full_name = full_name_raw.strip().lower()  # normalize spaces and case
            compound_id = row.get("Compound_ID", "").strip()

            # skip blanks and true duplicates (case-insensitive)
            if not full_name or full_name in seen:
                continue
            seen.add(full_name)

            # store the properly formatted display name (original casing)
            display_name = full_name_raw.strip()
            compounds.append((compound_id, display_name))

        # sort alphabetically by display name
        sorted_compounds = sorted(compounds, key=lambda x: x[1].lower())

        html = f'<link rel="stylesheet" href="{url_for("static", filename="styles.css")}">'
        html += "<table class='data-table'>"

        for compound_id, full_name in sorted_compounds:
            html += f'<tr><td><a href="/microbiota/{species_name}/{compound_id}">{full_name}</a></td></tr>'

        html += "</table>"
        html += "<a class='back' href='/'>← Back to main</a></main>"
        return html


# -----------------------------------------------------------
# Micobial COMPOUND DETAILS PAGE
# -----------------------------------------------------------
@app.route('/microbiota/<species_name>/<compound_id>')
def micro_show_compound(species_name, compound_id):
    with open('bt_pathways.csv', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)

        html = '<link rel="stylesheet" href="{}">'.format(url_for('static', filename='styles.css'))
        html += '<main class="container">'
        full_name = ""
        abbreviation = ""
        description = ""
        pathways = set()

        for row in reader:
            if row['Compound_ID'].strip() == compound_id.strip():
                if not full_name:
                    full_name = row.get("fullName", "Unknown chemical")
                    abbreviation = row.get("abbreviation", "N/A")
                    image_url = url_for('static', filename=f'images/{abbreviation}.png')
                    description = row.get("description", "No description available")
                pathways.add((row.get("Pathway_ID", ""), row.get("Pathway_Name", "")))

        if full_name:
            html += f"<h1>{full_name}</h1>"
            html += f"<p><strong>Compound ID:</strong> {compound_id}</p>"
            html += f"<p><strong>Description:</strong> {description}</p>"
            html += f'<p><img src="{image_url}" alt="{abbreviation}" style="max-width:600px; display:block; margin:15px auto;"></p>'
            html += f"<p><strong>Abbreviation:</strong> {abbreviation}</p>"

            html += "<h2>Associated Pathways</h2>"
            html += "<table class='data-table'><tr><th>Pathway ID</th><th>Pathway Name</th></tr>"
            for pid, pname in sorted(pathways):
                kegg_url = f"https://www.genome.jp/dbget-bin/www_bget?{pid}"
                html += f"<tr><td><a href='{kegg_url}' target='_blank'>{pid}</a></td><td>{pname}</td></tr>"
            html += "</table>"
            html += f"<a class='back' href='/microbiota/{species_name}'>← Back to {species_name.replace('_',' ')} metabolites</a></main>"
            return html

        else:
            return f"<main class='container'><h1>Compound {compound_id} not found</h1><a class='back' href='/microbiota/{species_name}'>← Back</a></main>"
