#!/usr/bin/env python3
"""
Author : Ken Youens-Clark <kyclark@gmail.com>
Date   : 2025-10-25
Purpose: Rock the Casbah
"""

import argparse
import csv
from typing import NamedTuple, TextIO


class Args(NamedTuple):
    """ Command-line arguments """
    file: TextIO
    outfile: TextIO


# --------------------------------------------------
def get_args() -> Args:
    """ Get command-line arguments """

    parser = argparse.ArgumentParser(
        description='Rock the Casbah',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('file',
                        help='Input file',
                        metavar='FILE',
                        type=argparse.FileType('rt'))

    parser.add_argument('-o',
                        '--outfile',
                        help='Output file',
                        metavar='FILE',
                        type=argparse.FileType('wt'),
                        default="out.csv")

    args = parser.parse_args()

    return Args(file=args.file, outfile=args.outfile)


# --------------------------------------------------
def main() -> None:
    """ Make a jazz noise here """

    args = get_args()
    reader = csv.DictReader(args.file)
    writer = csv.DictWriter(args.outfile, fieldnames=reader.fieldnames)
    output = dict()

    for rec in reader:
        key = rec["abbreviation"]
        if key not in output:
            output[key] = rec
            output[key]["pathway_ids"] = []
            output[key]["pathway_names"] = []

        output[key]["pathway_ids"].append(rec["Pathway_ID"])
        output[key]["pathway_names"].append(rec["Pathway_Name"])

    writer.writeheader()
    for abbr in sorted(output):
        rec = output[abbr]
        rec["Pathway_ID"] = ";".join(rec["pathway_ids"])
        rec["Pathway_Name"] = ";".join(rec["pathway_names"])
        del rec["pathway_ids"]
        del rec["pathway_names"]
        writer.writerow(rec)

    print("Done.")


# --------------------------------------------------
if __name__ == '__main__':
    main()
