# mbryg

Command line tool for retrieving metabolic information from Human Genome-scale metabolic model
# Purpose
Mbryg (M-bridge) aims to simplify the proces of biological research by providing a condensed, user-fiendly web-interface for collecting information on metabolites. Data on Mbryg is sourced from the Kyoto Encyclopedia of Genes and Genomes (KEGG) and the Virtual Human Metabolic (VHM) databases, providing information on the structure and pathways various metabolites are involved in.
# Highlights
1.) Compiling Data
```python
#!/usr/bin/env python3
"""
Author : Esraa Gabal <esraa.gabal93@gmail.com> & Julianne Fazekas <julianne_fazekas1@baylor.edu>
Date   : 2025-10-25
Purpose: pfb2025 project (CSHL: Programming for Biology)
"""

import argparse
import requests
import sys
import csv
from pprint import pprint
import kegg_pull.map as kmap
from KEGGRESTpy import kegg_get


API_URL = "https://www.vmh.life/_api/metabolites/?organismtype={}&page_size=4000"


#--------------------------------------------------
def get_args():
    parser = argparse.ArgumentParser(
        description="MetMapper",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("metabolite_name", metavar="ID", help="Metabolite name")
    parser.add_argument(
        "-o",
        "--outfile",
        help="Output file",
        metavar="FILE",
        type=argparse.FileType("wt"),
        default=sys.stdout,
    )
    return parser.parse_args()


#--------------------------------------------------
def main() -> None:
    args = get_args()
    print(args.metabolite_name)
    name = args.metabolite_name
    url = API_URL.format(name)
    results = []

    # ---- get metabolites from VMH API ----
    while True:
        if url:
            req = requests.get(url)
            if req.status_code != 200:
                sys.exit(f"Failed to get {url}")
            data = req.json()
            results += data["results"]
            url = data["next"]
            break
        else:
            break

    if not results:
        sys.exit(f'Unable to find "{name}"')

    # ---- prepare CSV writer ----
    fieldnames = list(results[0].keys()) + ["Compound_ID", "Pathway_ID", "Pathway_Name"]
    writer = csv.DictWriter(args.outfile, fieldnames=fieldnames)
    writer.writeheader()

    # ---- map KEGG IDs to pathways ----
    for result in results:
        kegg_id = result.get("keggId", "")
        result["Compound_ID"] = ""
        result["Pathway_ID"] = ""
        result["Pathway_Name"] = ""

        # Skip missing or malformed IDs
        if not kegg_id:
            writer.writerow(result)
            continue

        # Add proper prefix if missing
        if not kegg_id.startswith("cpd:"):
            kegg_id = f"cpd:{kegg_id}"

        try:
            pathways = kmap.entries_link(entry_ids=[kegg_id], target_database="pathway")
        except Exception as e:
            print(f" KEGG request failed for {kegg_id}: {e}")
            writer.writerow(result)
            continue

        for compound, pathways_ids in pathways.items():
            for path_id in pathways_ids:
                info = kegg_get(path_id)
                if isinstance(info, dict) and "NAME" in info:
                    result["Compound_ID"] = kegg_id
                    result["Pathway_ID"] = path_id
                    result["Pathway_Name"] = info["NAME"][0]
                    writer.writerow(result)

#--------------------------------------------------
if __name__ == "__main__":
    main()
```
2a.) Building the Website
```python

from flask import Flask, url_for
import csv

"""
Author : Esraa Gabal & Julianne Fazekas <julianne_fazekas1@baylor.edu> <esraa.gabal93@gmail.com>
Date   : 2025-10-25
Purpose: pfb2025 project (CSHL: Programming for Biology)
"""

app = Flask(__name__)

#-----------------------------------------------------------
# HOME PAGE — shows Human with an icon
#-----------------------------------------------------------
@app.route("/")
def homepage():
    html = '<link rel="stylesheet" href="{}">'.format(url_for('static', filename='styles.css'))
    html += '''
    <main class="container">
      <h1>Organisms</h1>
      <ul class="compound-list">
        <li>
          <a href="/human" class="human-link">
            🧬 <span>Human</span>
          </a>
        </li>
      </ul>
    </main>
    
        <a href="/microbiota" class="microbiota-link">
            🦠 <span>Gut Microbiota</span>
          </a>
        </li>
      </ul>
    </main>
    '''
    return html


#-----------------------------------------------------------
# HUMAN PAGE — list of metabolites
#-----------------------------------------------------------
@app.route("/human")
def metabolite_list():
    with open('human_mets_new.csv', newline='') as csvfile:
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
        html += '<main class="container"><h1>Human Metabolites</h1><ul class="compound-list">'
        for compound_id, full_name in sorted_compounds:
            html += f'<li><a href="/compound/{compound_id}">{full_name}</a></li>'
        html += '</ul>'
        html += "<a class='back' href='/'>← Back to main</a></main>"
        return html


#-----------------------------------------------------------
# COMPOUND DETAILS PAGE
#-----------------------------------------------------------
@app.route('/compound/<compound_id>')
def show_compound(compound_id):
    with open('human_mets_new.csv', newline='') as csvfile:
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


#-----------------------------------------------------------
# GUT MICROBIOTA PAGE — list of species
#-----------------------------------------------------------
@app.route("/microbiota")
def species_list():
    import csv

    species = []
    with open('./microbes/bacteria_sp.csv', newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if len(row) > 0:
                species.append(row[0].strip())  # first column = species name

    html = f'<link rel="stylesheet" href="{url_for("static", filename="styles.css")}">'
    html += '<main class="container"><h1>Gut Microbiota Species</h1><ul class="compound-list">'
    for name in species:
        html += f'<li>{name}</li>'
    html += '</ul>'
    html += "<a class='back' href='/'>← Back to main</a></main>"
    return html
```
2b.) Website aesthetics
```python
.data-table {
  width: 50%;
  border-collapse: separate;
  border-spacing: 6px 3px; 
  margin-top: 16px;
  border-radius: 10px;
}

.compound-list {
  list-style-type: none;   
  padding-left: 0;         
  margin-left: 0;
}

.data-table th,
.data-table td {
  text-align: left;
  padding: 8px 12px;
  vertical-align: top
}

.data-table th {
  border-bottom: 2px solid #2a2e3b;
  font-weight: bold;
}

body {
  font-family: system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif;
  margin: 0;
  padding: 20px;
}


.back {
  display: inline-block;
  margin-top: 20px;
  text-decoration: none;
}

.back:hover {
  text-decoration: underline;
}

.human-link {
  font-size: 30px;           
  text-decoration: none;
  color: #6ea8fe;
  display: flex;
  align-items: center;
  gap: 10px;                 
  margin-top: 10px;
}

.human-link:hover {
  text-decoration: underline;
  color: #88bbff;
}

.microbiota-link {
  font-size: 30px;           
  text-decoration: none;
  color: #6ea8fe;
  display: flex;
  align-items: center;
  gap: 10px;                 
  margin-top: 10px;
}

.microbiota-link:hover {
  text-decoration: underline;
  color: #88bbff;
}
```
3.) Image Generation
```python
#!/usr/bin/env python3
"""
Author : Esraa Gabal
Date   : 2025-10-25
Purpose: Generate chemical structure images from SMILES strings.
"""

import argparse
import csv
import os
import sys
from typing import NamedTuple, TextIO
from subprocess import getstatusoutput


class Args(NamedTuple):
    """Command-line arguments"""
    file: TextIO
    outdir: str


#--------------------------------------------------
def get_args() -> Args:
    """Get command-line arguments"""

    parser = argparse.ArgumentParser(
        description="Generate chemical structure images from SMILES strings",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "file",
        metavar="CSV",
        type=argparse.FileType("rt"),
        help="CSV file containing SMILES data",
    )

    parser.add_argument(
        "-o", "--outdir",
        help="Output directory for images",
        metavar="DIR",
        default="smiles",
    )

    args = parser.parse_args()

    if not os.path.isdir(args.outdir):
        os.makedirs(args.outdir)

    return Args(file=args.file, outdir=args.outdir)


#--------------------------------------------------
def main() -> None:
    """Main execution"""

    args = get_args()
    reader = csv.DictReader(args.file)

    seen = set()  # track compounds we already processed

    for rec in reader:
        smile = rec.get("smile", "").strip()
        compound = rec.get("abbreviation", "").strip()

        # Skip if missing either SMILES or compound name
        if not smile or not compound:
            continue

        # Skip duplicates
        if compound in seen:
            continue

        seen.add(compound)
        outfile = os.path.join(args.outdir, f"{compound}.png")

        # Only generate if it doesn't exist already
        if not os.path.isfile(outfile):
            print(f"Generating: {compound}")
            rv, out = getstatusoutput(f"./smiles2png.py '{smile}' -o '{outfile}'")
            if rv != 0:
                print(f"⚠️ Error generating {compound}: {out}", file=sys.stderr)

    print(f"\n✅ Done. Generated {len(seen)} unique compound images in '{args.outdir}'.")


# --------------------------------------------------
if __name__ == "__main__":
    main()
```
