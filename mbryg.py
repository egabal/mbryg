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
from collections import defaultdict


#API_URL = "https://www.vmh.life/_api/metabolites/?search={}"
API_URL = "https://www.vmh.life/_api/metabolites/?organismtype={}&page_size=5"


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
    fieldnames = results[0].keys()
    writer = csv.DictWriter(args.outfile, fieldnames=fieldnames)
    writer.writeheader()

    compound_to_pathway = defaultdict(list)
    for result in results:
        #writer.writerow(result)
        kegg_id = result['keggId']
        #print(kegg_id)
        pathways = kmap.entries_link(entry_ids=[kegg_id], target_database='pathway')
        print(pathways)
    #     key = f"cpd:{kegg_id}"
    #     if key in pathways:
    #         compound_to_pathway[kegg_id] = pathways[key]
    # print(compound_to_pathway)

# --------------------------------------------------
if __name__ == "__main__":
    main()
