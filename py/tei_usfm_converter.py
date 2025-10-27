#!/usr/bin/env python3

import argparse
from lxml import etree as et
import re

"""
XML namespaces
"""
xml_ns = "http://www.w3.org/XML/1998/namespace"
tei_ns = "http://www.tei-c.org/ns/1.0"

"""
Full book names list
"""
long_book_names = [
    "Matthew",
    "Mark",
    "Luke",
    "John",
    "Acts",
    "Romans",
    "1 Corinthians",
    "2 Corinthians",
    "Galatians",
    "Ephesians",
    "Philippians",
    "Colossians",
    "1 Thessalonians",
    "2 Thessalonians",
    "1 Timothy",
    "2 Timothy",
    "Titus",
    "Philemon",
    "Hebrews",
    "James",
    "1 Peter",
    "2 Peter",
    "1 John",
    "2 John",
    "3 John",
    "Jude",
    "Revelation"
]

"""
USFM abbreviations list
"""
usfm_abbrevations = [
    "MAT",
    "MRK",
    "LUK",
    "JHN",
    "ACT",
    "ROM",
    "1CO",
    "2CO",
    "GAL",
    "EPH",
    "PHP",
    "COL",
    "1TH",
    "2TH",
    "1TI",
    "2TI",
    "TIT",
    "PHM",
    "HEB",
    "JAS",
    "1PE",
    "2PE",
    "1JN",
    "2JN",
    "3JN",
    "JUD",
    "REV"
]

"""
SBL abbreviations list
"""
sbl_abbrevations = [
    "Matt",
    "Mark",
    "Luke",
    "John",
    "Acts",
    "Rom",
    "1 Cor",
    "2 Cor",
    "Gal",
    "Eph",
    "Phil",
    "Col",
    "1 Thess",
    "2 Thess",
    "1 Tim",
    "2 Tim",
    "Titus",
    "Phlm",
    "Heb",
    "Jas",
    "1 Pet",
    "2 Pet",
    "1 John",
    "2 John",
    "3 John",
    "Jude",
    "Rev"
]

"""
Class for converting a transcription (including collation data) in TEI XML format to USFM format.
"""
class tei_usfm_converter:
    def __init__(self, **kwargs):
        # Populate a String referring to the book's filename base:
        self.filebase = kwargs["filebase"] if "filebase" in kwargs else ""
        # Populate a Dictionary of witness sigla, keyed by witness references (e.g., "#WLC"):
        self.wit_sigla = kwargs["wit_sigla"] if "wit_sigla" in kwargs else {}
        # Populate a Set of ignored apparatus types:
        self.ignored_app_types = kwargs["ignored_app_types"] if "ignored_app_types" in kwargs else set()
        # Initialize counters for the current book, chapter, and verse:
        self.book_n = ""
        self.chapter_n = ""
        self.verse_n = ""
        # Initialize a flag indicating whether or not we're currently processing an apparatus entry:
        self.app_flag = False
        return
        
    """
    Recursively converts a transcription (including collation data) in TEI XML format to USFM format.
    """
    def to_usfm(self, xml):
        usfm = ""
        # If the input is an XML tree and not an element, then return the serialization of its root element:
        if not et.iselement(xml):
            usfm += self.to_usfm(xml.getroot())
            # Post-process this USFM text, moving paragraph breaks before new chapters to a position after the new chapters
            # and removing superfluous line breaks and spaces:
            usfm = re.sub(r"\\p\s*\\c (\d+)\s*\\m", r"\\c \1\n\\p", usfm)
            usfm = usfm.replace(" . ", ". ")
            usfm = usfm.replace(" , ", ", ")
            usfm = usfm.replace(" · ", "· ")
            usfm = usfm.replace(" ; ", "; ")
            usfm = usfm.replace(" — ", "—")
            usfm = usfm.replace("\n\n", "\n")
            usfm = usfm.replace("  ", " ")
            return usfm
        # Otherwise, proceed according to the tag of the current element:
        raw_tag = xml.tag.replace("{%s}" % tei_ns, "")
        # If this element is a TEI, teiHeader, fileDesc, titleStmt, text, body or lem element, then process its children recursively:
        if raw_tag in ["TEI", "teiHeader", "fileDesc", "titleStmt", "text", "body", "lem"]:
            for child in xml:
                usfm += self.to_usfm(child)
        # If this element is a div, then it marks the start of a new book;
        # add a new line followed by the identifiers, headers, and ToC entries,
        # and then recursively process its child elements:
        if raw_tag == "div":
            if xml.get("{%s}id" % xml_ns) is not None:
                self.book_n = xml.get("{%s}id" % xml_ns).split("B")[1]
                long_book_name = long_book_names[int(self.book_n) - 1]
                usfm_abbreviation = usfm_abbrevations[int(self.book_n) - 1]
                sbl_abbreviation = sbl_abbrevations[int(self.book_n) - 1]
                if self.book_n != "01":
                    usfm += "\n\n"
                usfm += "\\id %s - SBL Greek New Testament\n" % usfm_abbreviation
                usfm += "\\h %s\n" % long_book_name
                usfm += "\\toc1 The Book of %s\n" % long_book_name
                usfm += "\\toc2 %s\n" % long_book_name
                usfm += "\\toc3 %s\n" % sbl_abbreviation
            for child in xml:
                usfm += self.to_usfm(child)
        # If this element is an ab element, then it marks an incipit;
        # add a \mt macro for the main title,
        # and then recursively process its child elements:
        if raw_tag == "ab":
            usfm += "\\mt "
            for child in xml:
                usfm += self.to_usfm(child)
        # If this element is a milestone, then print a chapter or verse
        if raw_tag == "milestone":
            unit = xml.get("unit")
            # If this is an incipit, then add a \mt macro for the main title:
            if unit == "incipit":
                usfm += "\\mt "
            # If it is a new chapter, then add a new line followed by a \c macro (or a \bd macro, if we're in a variant reading) followed by the chapter number:
            if unit == "chapter":
                if xml.get("{%s}id" % xml_ns) is not None:
                    self.chapter_n = xml.get("{%s}id" % xml_ns).split("K")[1]
                    if self.app_flag:
                        usfm += "\\bd %s:\\bd*" % self.chapter_n
                    else:
                        usfm += "\n\\c %s" % self.chapter_n
                        # Add a no-indent paragraph after it:
                        usfm += "\n\\m"
            # If it is a new verse, then add a \v macro (or a \bd macro, if we're in a variant reading) followed by the verse number:
            if unit == "verse":
                if xml.get("{%s}id" % xml_ns) is not None:
                    self.verse_n = xml.get("{%s}id" % xml_ns).split("V")[1]
                    if self.app_flag:
                        usfm += "\\bd %s\\bd* " % self.verse_n
                    else:
                        usfm += "\n\\v %s " % self.verse_n
        # If this element is a p element, then it constitutes a paragraph; 
        # add a paragraph marker, then process its child elements recursively:
        if raw_tag == "p":
            usfm += "\n\\p\n"
            for child in xml:
                usfm += self.to_usfm(child)
        # If this element is an app element, then proceed according to its type:
        if raw_tag == "app":
            app_type = xml.get("type") if xml.get("type") is not None else "substantive"
            # Save the current chapter and verse reference, and get the lemma text to be set in the main text later:
            # current_chapter_n = self.chapter_n
            # current_verse_n = self.verse_n
            # Use the loc attribute of this variation unit, and get the lemma text to be set in the main text later:
            app_loc = xml.get("loc")
            lem = xml.find("tei:lem", namespaces={"tei": tei_ns})
            lem_usfm = self.to_usfm(lem)
            # Then process the apparatus entry if necessary:
            if app_type not in self.ignored_app_types:
                # If this variation unit's type is not an ignored type, then add a text-critical footnote 
                # and surround the lemma with the appropriate marks in the main text.
                # Set the flag for processing apparatus entries:
                self.app_flag = True
                # Add a footnote marker and prefix the apparatus entry by the location reference 
                # and the appropriate variant type marker:
                usfm += "\\f - \\fr %s \\ft " % app_loc
                if app_type == "addition":
                    usfm += "\u2e06 "
                elif app_type == "transposition":
                    usfm += "\u2e09 "
                elif app_type == "omission":
                    usfm += "\u2e0b "
                else:
                    usfm += "\u2e02 "
                # Then recursively parse the contents of the readings, separated by broken bars:
                usfm += "\u00a6 ".join([self.to_usfm(rdg) for rdg in xml.findall("tei:rdg", namespaces={"tei": tei_ns})])
                # Then close the footnote and turn off the flag for processing apparatus entries:
                usfm += "\\f*"
                self.app_flag = False
                # Add the appropriate critical marks around the lemma text:
                if app_type == "addition":
                    usfm += "\u2e06 "
                elif app_type == "transposition":
                    usfm += "\u2e09 %s\u2e0a " % lem_usfm
                elif app_type == "omission":
                    usfm += "\u2e0b %s\u2e0c " % lem_usfm
                else:
                    usfm += "\u2e02 %s\u2e03 " % lem_usfm
            else:
                # If this variation unit's type is an ignored type, then just print the lemma text:
                usfm += lem_usfm
        # If this element is a rdg element, then print its contents and then print its witnesses in a \fw block:
        if raw_tag == "rdg":
            rdg_usfm = xml.text
            # If the reading is empty, then replace it with an en-dash:
            if rdg_usfm is None:
                rdg_usfm = "\u2013 "
            usfm += rdg_usfm
            usfm += "\\fw %s \\fw* " % (" ".join([self.wit_sigla[wit] for wit in xml.get("wit").split()]))
        # If this element is a w element, then print its text, followed by a space:
        if raw_tag == "w":
            usfm += xml.text + " "
        # If this element is a pc element, then print its text, followed by a space:
        if raw_tag == "pc":
            usfm += xml.text + " "
        # Finally, return the parsed USFM text:
        return usfm