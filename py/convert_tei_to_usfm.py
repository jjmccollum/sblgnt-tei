#!/usr/bin/env python3

import argparse
from lxml import etree as et
from tei_usfm_converter import usfm_abbrevations, tei_usfm_converter

"""
Dictionary mapping witness references to sigla.
"""
wit_sigla = {
    "#ECM": "ECM",
    "#Greeven": "Greeven",
    "#Holmes": "Holmes",
    "#NA": "NA",
    "#NIV": "NIV",
    "#RP": "RP",
    "#TR": "TR",
    "#Treg": "Treg",
    "#Tregmarg": "Tregmarg",
    "#WH": "WH",
    "#WHapp": "WHapp",
    "#WHmarg": "WHmarg",
    "#WHspur": "WHspur"
}

"""
Entry point to the script. Parses command-line arguments and calls the core functions.
"""
def main():
    parser = argparse.ArgumentParser(description="Converts a labeled TEI XML collation to a USFM file.")
    parser.add_argument("-a", metavar="ignored_app_type", type=str, action="append", help="Variation type to ignore; this can used multiple times (e.g., -a vocalic -a orthographic).")
    parser.add_argument("input", type=str, help="TEI XML collation file to convert to USFM.")
    args = parser.parse_args()
    # Parse the I/O arguments:
    input_addr = args.input
    ignored_app_types = set() if args.a is None else set(args.a)
    # Create the parameters for the converter:
    converter_args = {}
    converter_args["wit_sigla"] = wit_sigla
    converter_args["ignored_app_types"] = ignored_app_types
    # Initialize the converter with these parameters:
    converter = tei_usfm_converter(**converter_args)
    # Parse the input XML document:
    input_xml = et.parse(input_addr)
    # Convert the input:
    usfm = converter.to_usfm(input_xml)
    # Then split the file into separate files for each book, and write the individual files to output:
    usfm_books = usfm.split("\\id ")
    for i, usfm_book in enumerate(usfm_books):
        if i == 0:
            continue
        output_addr = "usfm/%02d%sSBL.sfm" % (i, usfm_abbrevations[i - 1])
        with open(output_addr, "w", encoding="utf-8") as f:
            f.write("\\id " + usfm_book)
            f.close()
    exit(0)

if __name__=="__main__":
    main()
