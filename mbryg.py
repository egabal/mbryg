#!/usr/bin/env python3
"""
Author : pfb <pfb@localhost>
Date   : 2025-10-24
Purpose: Rock the Casbah
"""

import argparse
import requests 
import sys
from pprint import pprint

API_URL = 'https://www.vmh.life/_api/metabolites/?fullName={}'


# --------------------------------------------------
def get_args():
    """ Get command-line arguments """

    parser = argparse.ArgumentParser(
        description='Rock the Casbah',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('metabolite_name',
                        metavar='ID',
                        help='Metablite name')

    

    return parser.parse_args()

 

# --------------------------------------------------
def main() -> None:
    """ Make a jazz noise here """

    args = get_args()
    print(args.metabolite_name)
    name = args.metabolite_name
    url = API_URL.format(name)
    r = requests.get(url)
    if r.status_code != 200:
        sys.exit(f'Failed to get {url}')
    #print(r.json())
    data = r.json()
    pprint(data)
    if data['count'] == 0:
        sys.exit(f'Unable to find "{name}"')
# --------------------------------------------------
if __name__ == '__main__':
    main()
