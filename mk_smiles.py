#!/usr/bin/env python3
"""
Author : Ken Youens-Clark <kyclark@gmail.com>
Date   : 2025-10-25
Purpose: Rock the Casbah
"""

import argparse
import csv
import os
from typing import NamedTuple, TextIO

from pprint import pprint


class Args(NamedTuple):
    """ Command-line arguments """
    file: TextIO
    outdir: str


# --------------------------------------------------
def get_args() -> Args:
    """ Get command-line arguments """

    parser = argparse.ArgumentParser(
        description='Rock the Casbah',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('file',
                        metavar='STR',
                        type=argparse.FileType("rt"),
                        help='SMILE string')

    parser.add_argument('-o',
                        '--outdir',
                        help='Ouput dir',
                        metavar='DIR',
                        default='smiles')

    args = parser.parse_args()

    if not os.path.isdir(args.outdir):
        os.makedirs(args.outdir)

    return Args(file=args.file, outdir=args.outdir)


# --------------------------------------------------
def main() -> None:
    """ Make a jazz noise here """

    args = get_args()
    reader = csv.DictReader(args.file, delimiter='\t')

    for rec in reader:
        if smile := rec["smile"]:
            #pprint(rec)
            print("./smiles2png.py '{}' -o {}".format(
                smile,
                os.path.join(args.outdir, rec["abbreviation"] + ".png")
            ))
    #print(f"Done, see \"{args.outdir}\"")

    
# --------------------------------------------------
if __name__ == '__main__':
    main()
