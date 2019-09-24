# -*- coding: utf-8 -*-

from bomlib.csv_writer import WriteCSV
from bomlib.xml_writer import WriteXML
from bomlib.html_writer import WriteHTML
from bomlib.xlsx_writer import WriteXLSX

import bomlib.columns as columns
from bomlib.preferences import BomPref

import os
import shutil


def TmpFileCopy(filename, fmt):
    # Make a tmp copy of a given file

    filename = os.path.abspath(filename)

    if os.path.exists(filename) and os.path.isfile(filename):
        shutil.copyfile(filename, fmt.replace("%O", filename))


def WriteBoM(filename, groups, net, headings=columns.ColumnList._COLUMNS_DEFAULT, prefs=None):
    """
    Write BoM to file
    filename = output file path
    groups = [list of ComponentGroup groups]
    headings = [list of headings to display in the BoM file]
    prefs = BomPref object
    """

    filename = os.path.abspath(filename)

    # No preferences supplied, use defaults
    if not prefs:
        prefs = BomPref()

    # Remove any headings that appear in the ignore[] list
    headings = [h for h in headings if not h.lower() in [i.lower() for i in prefs.ignore]]

    # If no extension is given, assume .csv (and append!)
    if len(filename.split('.')) < 2:
        filename += ".csv"

    # Make a temporary copy of the output file
    if prefs.backup is not False:
        TmpFileCopy(filename, prefs.backup)

    ext = filename.split('.')[-1].lower()

    result = False

    # CSV file writing
    if ext in ["csv", "tsv", "txt"]:
        if WriteCSV(filename, groups, net, headings, prefs):
            print("CSV Output -> {fn}".format(fn=filename))
            result = True
        else:
            print("Error writing CSV output")

    elif ext in ["htm", "html"]:
        if WriteHTML(filename, groups, net, headings, prefs):
            print("HTML Output -> {fn}".format(fn=filename))
            result = True
        else:
            print("Error writing HTML output")

    elif ext in ["xml"]:
        if WriteXML(filename, groups, net, headings, prefs):
            print("XML Output -> {fn}".format(fn=filename))
            result = True
        else:
            print("Error writing XML output")

    elif ext in ["xlsx"] and prefs.xlsxwriter_available:
        if WriteXLSX(filename, groups, net, headings, prefs):
            print("XLSX Output -> {fn}".format(fn=filename))
            result = True
        else:
            print("Error writing XLSX output")

    else:
        print("Unsupported file extension: {ext}".format(ext=ext))

    return result
