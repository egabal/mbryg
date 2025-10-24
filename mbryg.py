#!/usr/bin/env python3
"""
Author : pfb <pfb@localhost>
Date   : 2025-10-24
Purpose: Rock the Casbah
"""

import argparse


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
# --------------------------------------------------
if __name__ == '__main__':
    main()
