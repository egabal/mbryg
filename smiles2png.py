#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
SMILES to PNG Converter
======================

A command-line utility to render SMILES strings as 2D molecular images with
molecular formulas and proper subscript formatting.

This script demonstrates how to:
- Parse SMILES strings using RDKit
- Generate 2D molecular coordinates
- Create publication-quality molecular images
- Add custom legends with molecular formulas
- Handle font rendering and subscripts

Example Usage:
    python smiles2png.py "CCO"  # Ethanol
    python smiles2png.py "CC(=O)OC1=CC=CC=C1C(=O)O" -o aspirin.png  # Aspirin
    python smiles2png.py "C1=CC=CC=C1" --size 800  # Benzene, larger image

Author: Hunter Heidenreich
Website: https://hunterheidenreich.com
"""

import argparse
import hashlib
import sys
from pathlib import Path

# RDKit imports
from rdkit import Chem
from rdkit.Chem import Draw, rdDepictor, rdMolDescriptors

# PIL imports for image manipulation
from PIL import Image, ImageDraw, ImageFont

# Constants for image configuration
DEFAULT_IMAGE_SIZE = 500
LEGEND_HEIGHT_RATIO = 0.08  # Legend height as ratio of image size
LEGEND_Y_OFFSET_RATIO = 0.02  # Y offset as ratio of image size
LEGEND_X_OFFSET_RATIO = 0.02  # X offset as ratio of image size
SUBSCRIPT_Y_OFFSET_RATIO = 0.006  # Subscript offset as ratio of image size

# Font size ratios based on image size
REGULAR_FONT_RATIO = 0.028  # Regular font size as ratio of image size
SUBSCRIPT_FONT_RATIO = 0.02  # Subscript font size as ratio of image size

# Font paths for different operating systems
FONT_PATHS = [
    "/System/Library/Fonts/Arial.ttf",  # macOS
    "/usr/share/fonts/truetype/arial.ttf",  # Linux
    "C:/Windows/Fonts/arial.ttf",  # Windows
]


def _calculate_dynamic_sizes(image_size: int):
    """Calculate dynamic sizing values based on image size."""
    return {
        'legend_height': int(image_size * LEGEND_HEIGHT_RATIO),
        'legend_y_offset': int(image_size * LEGEND_Y_OFFSET_RATIO),
        'legend_x_offset': int(image_size * LEGEND_X_OFFSET_RATIO),
        'subscript_y_offset': int(image_size * SUBSCRIPT_Y_OFFSET_RATIO),
        'regular_font_size': int(image_size * REGULAR_FONT_RATIO),
        'subscript_font_size': int(image_size * SUBSCRIPT_FONT_RATIO),
    }


def _load_fonts(regular_size: int, subscript_size: int):
    """Load system fonts for text rendering, with fallback to default font."""
    font_regular = None
    font_small = None

    for font_path in FONT_PATHS:
        try:
            font_regular = ImageFont.truetype(font_path, regular_size)
            font_small = ImageFont.truetype(font_path, subscript_size)
            break
        except (OSError, IOError):
            continue

    if font_regular is None:
        font_regular = ImageFont.load_default()
        font_small = ImageFont.load_default()

    return font_regular, font_small


def create_molecule_image(
    mol: Chem.Mol, smiles_string: str, size: int = DEFAULT_IMAGE_SIZE
) -> Image.Image:
    """
    Creates a molecule image with a legend showing molecular formula and SMILES string.

    Args:
        mol: RDKit molecule object (already validated)
        smiles_string: Original SMILES string for legend display
        size: Image size in pixels (square image)

    Returns:
        PIL Image object with molecule structure and formatted legend
    """
    # Calculate dynamic sizes based on image size
    sizes = _calculate_dynamic_sizes(size)
    
    rdDepictor.Compute2DCoords(mol)
    molecular_formula = rdMolDescriptors.CalcMolFormula(mol)

    mol_img = Draw.MolToImage(mol, size=(size, size))
    if mol_img.mode != "RGBA":
        mol_img = mol_img.convert("RGBA")

    total_height = size + sizes['legend_height']
    final_img = Image.new("RGBA", (size, total_height), "white")
    final_img.paste(mol_img, (0, 0))

    draw = ImageDraw.Draw(final_img)
    font_regular, font_small = _load_fonts(sizes['regular_font_size'], sizes['subscript_font_size'])

    _draw_molecular_formula(draw, molecular_formula, font_regular, font_small, sizes, size)
    _draw_smiles_legend(draw, smiles_string, font_regular, sizes, molecular_formula, size)

    return final_img


def _draw_molecular_formula(
    draw: ImageDraw.Draw, formula: str, font_regular, font_small, sizes: dict, image_size: int
) -> int:
    """Draw molecular formula with proper subscript formatting."""
    y_pos = image_size + sizes['legend_y_offset']
    x_pos = sizes['legend_x_offset']

    draw.text((x_pos, y_pos), "Formula: ", fill="black", font=font_regular)
    x_pos += draw.textlength("Formula: ", font=font_regular)

    for char in formula:
        if char.isdigit():
            draw.text(
                (x_pos, y_pos + sizes['subscript_y_offset']), char, fill="black", font=font_small
            )
            x_pos += draw.textlength(char, font=font_small)
        else:
            draw.text((x_pos, y_pos), char, fill="black", font=font_regular)
            x_pos += draw.textlength(char, font=font_regular)

    return x_pos


def _draw_smiles_legend(
    draw: ImageDraw.Draw, smiles: str, font_regular, sizes: dict, formula: str, image_size: int
) -> None:
    """Add SMILES string to the image legend."""
    y_pos = image_size + sizes['legend_y_offset']

    formula_width = sum(
        draw.textlength(char, font_regular) for char in f"Formula: {formula}"
    )
    x_pos = sizes['legend_x_offset'] + formula_width

    separator = " | SMILES: "
    draw.text((x_pos, y_pos), separator, fill="black", font=font_regular)
    x_pos += draw.textlength(separator, font=font_regular)
    draw.text((x_pos, y_pos), smiles, fill="black", font=font_regular)


def smiles_to_png(
    smiles_string: str, output_file: str, size: int = DEFAULT_IMAGE_SIZE
) -> None:
    """
    Convert a SMILES string to a PNG image with molecular formula legend.

    Args:
        smiles_string: Valid SMILES string representing a molecule
        output_file: Path where the PNG image will be saved
        size: Square image dimensions in pixels

    Raises:
        ValueError: If SMILES string is invalid or size is non-positive
        IOError: If file caP0+r4B33\nnot be saved to the specified location
    """
    if not smiles_string or not smiles_string.strip():
        raise ValueError("SMILES string cannot be empty")

    if size <= 0:
        raise ValueError(f"Image size must be positive, got: {size}")

    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    mol = Chem.MolFromSmiles(smiles_string.strip())
    if mol is None:
        raise ValueError(
            f"Invalid SMILES string: '{smiles_string}'. "
            f"Please check the syntax and try again."
        )

    img = create_molecule_image(mol, smiles_string.strip(), size)

    try:
        img.save(output_file, "PNG", optimize=True)
        print(f"Image successfully saved to: {output_file}")
    except Exception as e:
        raise IOError(f"Failed to save image to '{output_file}': {e}")


def create_safe_filename(smiles_string: str) -> str:
    """
    Generate a filesystem-safe filename from a SMILES string using MD5 hash.

    Args:
        smiles_string: The input SMILES string

    Returns:
        A safe filename ending with .png
    """
    clean_smiles = smiles_string.strip()
    hasher = hashlib.md5(clean_smiles.encode("utf-8"))
    return f"{hasher.hexdigest()}.png"


def main() -> None:
    """Command-line interface for the SMILES to PNG converter."""
    parser = argparse.ArgumentParser(
        description="Convert SMILES strings to publication-quality PNG images with molecular formulas.",
        epilog="""
Examples:
  %(prog)s "CCO"                           # Ethanol with auto-generated filename
  %(prog)s "CC(=O)OC1=CC=CC=C1C(=O)O"     # Aspirin with auto-generated filename
  %(prog)s "C1=CC=CC=C1" -o benzene.png   # Benzene with custom filename  
  %(prog)s "CCO" --size 800               # Ethanol with larger image size

Common SMILES patterns:
  CCO                     - Ethanol
  CC(=O)O                 - Acetic acid
  C1=CC=CC=C1             - Benzene
  CC(C)C                  - Isobutane
  NC(=O)C1=CC=CC=C1       - Benzamide
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "smiles",
        type=str,
        help="SMILES string of the molecule to visualize (e.g., 'CCO' for ethanol)",
    )

    parser.add_argument(
        "-o",
        "--output",
        type=str,
        metavar="FILE",
        help="Output PNG filename. If not provided, generates a unique filename "
        "based on the SMILES string hash. Extension .png will be added if missing.",
    )

    parser.add_argument(
        "-s",
        "--size",
        type=int,
        default=DEFAULT_IMAGE_SIZE,
        metavar="PIXELS",
        help=f"Square image size in pixels (default: {DEFAULT_IMAGE_SIZE}). "
        f"Typical values: 300 (small), 500 (medium), 800 (large).",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose output for debugging",
    )

    args = parser.parse_args()

    if args.verbose:
        print(f"Input SMILES: {args.smiles}")
        print(f"Image size: {args.size}x{args.size} pixels")

    if args.output:
        output_filename = (
            args.output
            if args.output.lower().endswith(".png")
            else f"{args.output}.png"
        )
        if args.verbose:
            print(f"Using custom filename: {output_filename}")
    else:
        output_filename = create_safe_filename(args.smiles)
        if args.verbose:
            print(f"Generated filename: {output_filename}")

    try:
        smiles_to_png(args.smiles, output_filename, args.size)

        if args.verbose:
            print("Conversion completed successfully!")

    except ValueError as e:
        print(f"Input Error: {e}", file=sys.stderr)
        print("Tip: Check your SMILES string syntax", file=sys.stderr)
        sys.exit(1)

    except IOError as e:
        print(f"File Error: {e}", file=sys.stderr)
        print("Tip: Check file permissions and disk space", file=sys.stderr)
        sys.exit(2)

    except ImportError as e:
        print(f"Dependencies Error: {e}", file=sys.stderr)
        print(
            "Tip: Install required packages with 'pip install rdkit pillow'",
            file=sys.stderr,
        )
        sys.exit(3)

    except Exception as e:
        print(f"Unexpected Error: {e}", file=sys.stderr)
        print("Tip: Please report this issue if it persists", file=sys.stderr)
        sys.exit(4)


if __name__ == "__main__":
    main()

