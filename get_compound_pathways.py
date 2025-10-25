#!/usr/bin/env python3
"""
Author : Ken Youens-Clark <kyclark@gmail.com>
Date   : 2025-10-25
Purpose: Rock the Casbah
"""

import argparse
import re
import sys
from collections import defaultdict
from typing import NamedTuple, TextIO


class Args(NamedTuple):
    """ Command-line arguments """
    file: TextIO


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

    args = parser.parse_args()

    return Args(file=args.file)


# --------------------------------------------------
def main() -> None:
    """ Make a jazz noise here """

    args = get_args()
    compound_to_pathway = defaultdict(list)
    entry_re = re.compile(r"^ENTRY\s+(C\d+)")
    cur_compound = ""
    in_pathways = False

    for line in map(str.rstrip, args.file):
        if matches := entry_re.search(line):
            cur_compound = matches.group(1)
        elif line.startswith("PATHWAY"):
            if not cur_compound:
                sys.exit("Found PATHWAY but don't have compound")
            in_pathways = True
            cols = re.split(r"\s+", line, maxsplit=2)
            assert len(cols) == 3
            compound_to_pathway[cur_compound].append((cols[1], cols[2]))
        elif in_pathways:
            # Check if a new section
            if re.search(r"^[A-Z]+\s+", line):
                in_pathways = False
            else:
                cols = re.split(r"\s+", line.strip(), maxsplit=1)
                assert len(cols) == 2
                compound_to_pathway[cur_compound].append((cols[0], cols[1]))
        elif line == "///":
            cur_compound = ""
            in_pathways = False

    for compound, pathways in compound_to_pathway.items():
        for pathway in pathways:
            print("\t".join([compound, pathway[0], pathway[1]]))


# --------------------------------------------------
if __name__ == '__main__':
    main()
