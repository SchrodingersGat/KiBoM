# -*- coding: utf-8 -*-

from .csv_writer import WriteCSV
from .xml_writer import WriteXML
from .html_writer import WriteHTML
from .xlsx_writer import WriteXLSX

from . import columns
from . import debug
from .preferences import BomPref

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
            debug.info("CSV Output -> {fn}".format(fn=filename))
            result = True
        else:
            debug.error("Error writing CSV output")

    elif ext in ["htm", "html"]:
        if WriteHTML(filename, groups, net, headings, prefs):
            debug.info("HTML Output -> {fn}".format(fn=filename))
            result = True
        else:
            debug.error("Error writing HTML output")

    elif ext in ["xml"]:
        if WriteXML(filename, groups, net, headings, prefs):
            debug.info("XML Output -> {fn}".format(fn=filename))
            result = True
        else:
            debug.error("Error writing XML output")

    elif ext in ["xlsx"]:
        if WriteXLSX(filename, groups, net, headings, prefs):
            debug.info("XLSX Output -> {fn}".format(fn=filename))
            result = True
        else:
            debug.error("Error writing XLSX output")

    else:
        debug.error("Unsupported file extension: {ext}".format(ext=ext))

    return result
