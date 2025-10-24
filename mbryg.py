#!/usr/bin/env python3
"""
Author : pfb <pfb@localhost>
Date   : 2025-10-24
Purpose: Rock the Casbah
"""

import argparse
import requests 
import sys
import csv
from pprint import pprint

API_URL = 'https://www.vmh.life/_api/metabolites/?search={}'


# --------------------------------------------------
def get_args():
    """ Get command-line arguments """

    parser = argparse.ArgumentParser(
        description='Rock the Casbah',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('metabolite_name',
                        metavar='ID',
                        help='Metablite name')

    parser.add_argument('-o',
                        '--outfile',
                        help='The output file',
                        metavar='FILE',
                        type=argparse.FileType('wt'),
                        default=sys.stdout)

    return parser.parse_args()

 

# --------------------------------------------------
def main() -> None:
    """ Make a jazz noise here """

    args = get_args()
    print(args.metabolite_name)
    name = args.metabolite_name
    url = API_URL.format(name)
    req = requests.get(url)
    if req.status_code != 200:
        sys.exit(f'Failed to get {url}')
    #print(req.json())
    data = req.json()
    #pprint(data)
    if data['count'] == 0:
        sys.exit(f'Unable to find "{name}"')

    results = data["results"]
    while True:
        if next_url := data["next"]:
            #print(next_url)
            req = requests.get(next_url)
            if req.status_code != 200:
                sys.exit(f'Failed to get {next_url}')
            data = req.json()
            #pprint(data)
            results += data["results"]
        else:
            break
    #print(results, file=args.outfile)
    # for i, result in enumerate(results):
    #     if i == 0:
    #         print(",".join(result.keys()), file=args.outfile)
    #     print(",".join(map(str, result.values())), file=args.outfile)
    fieldnames = results[0].keys()
    writer = csv.DictWriter(args.outfile, fieldnames=fieldnames)
    writer.writeheader()
    for result in results:
        writer.writerow(result)

# --------------------------------------------------
if __name__ == '__main__':
    main()
