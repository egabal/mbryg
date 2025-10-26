#!/usr/bin/env python3
"""
Author : pfb <pfb@localhost>
Date   : 2025-10-24
Purpose: Retrieve metabolite information from Virtual Human Metabolic Atlas
         and map each metabolite to its KEGG pathways.
"""

import argparse
import requests
import sys
import csv
from pprint import pprint
import kegg_pull.map as kmap
from KEGGRESTpy import kegg_get


API_URL = "https://www.vmh.life/_api/metabolites/?organismtype={}&page_size=4000"


# --------------------------------------------------
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


# --------------------------------------------------
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

# --------------------------------------------------
if __name__ == "__main__":
    main()
