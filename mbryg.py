#!/usr/bin/env python3
"""
Author : pfb <pfb@localhost>
Date   : 2025-10-24
Purpose: Retrieve metabolite information from Virtual Human Metabolic Atlas.
"""

import argparse
import requests
import sys
import csv
from pprint import pprint
import kegg_pull.map as kmap
from KEGGRESTpy import kegg_link, kegg_get


#API_URL = "https://www.vmh.life/_api/metabolites/?search={}"
API_URL = "https://www.vmh.life/_api/metabolites/?organismtype={}&page_size=4000"

# --------------------------------------------------
def get_args():
    """Get command-line arguments"""

    parser = argparse.ArgumentParser(
        description="MetMapper",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "metabolite_name", metavar="ID", help="Metablite name"
    )

    parser.add_argument(
        "-o",
        "--outfile",
        help="The output file",
        metavar="FILE",
        type=argparse.FileType("wt"),
        default=sys.stdout,
    )

    return parser.parse_args()


# --------------------------------------------------
def main() -> None:
    """Make a jazz noise here"""

    args = get_args()
    print(args.metabolite_name)
    name = args.metabolite_name
    url = API_URL.format(name)
    results = []

    while True:
        if url:
            req = requests.get(url)
            if req.status_code != 200:
                sys.exit(f"Failed to get {url}")
            data = req.json()
            # pprint(data)
            results += data["results"]
            url = data["next"]
            break
        else:
            break
    if not results:
        sys.exit(f'Unable to find "{name}"')
    fieldnames = list(results[0].keys())
    writer = csv.DictWriter(args.outfile, fieldnames = fieldnames + ['Compound_ID', 'Pathway_ID', 'Pathway_Name'])
    writer.writeheader()

    for result in results:
        result['Compound_ID'] = ''
        result['Pathway_ID'] = ''
        result['Pathway_Name'] = ''
        if kegg_id := result['keggId']:
             # if you want all human pathways, use organism_id = "hsa"
            if kegg_id.lower() in ["human", "hsa"]:
                pathways = kegg_link("pathway", "hsa")   # get all human pathways
                compound = "human"
            else:
                pathways = kmap.entries_link(entry_ids=[kegg_id], target_database='pathway')
                compound = kegg_id

            # iterate properly through the mapping dictionary
            for compound_id, pathways_ids in pathways.items():
                for path_id in pathways_ids:
                    info = kegg_get(path_id)
                    if isinstance(info, dict) and 'NAME' in info:
                        result['Compound_ID'] = compound
                        result['Pathway_ID'] = path_id
                        result['Pathway_Name'] = info['NAME'][0]
        writer.writerow(result)

# --------------------------------------------------
if __name__ == "__main__":
    main()
