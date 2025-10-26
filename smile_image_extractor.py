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


# --------------------------------------------------
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


# --------------------------------------------------
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
