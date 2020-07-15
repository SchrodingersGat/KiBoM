"""
Simple tests

For debug information use:
pytest-3 --log-cli-level debug

"""

import os
import sys
import logging
# Look for the 'utils' module from where the script is running
prev_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if prev_dir not in sys.path:
    sys.path.insert(0, prev_dir)
# Utils import
from utils import context

BOM_DIR = 'BoM'
KIBOM_TEST_COMPONENTS = ['C1', 'C2', 'C3', 'C4', 'R1', 'R2', 'R3', 'R4', 'R5', 'R7', 'R8', 'R9', 'R10']

def test_bom_simple_csv():
    prj = 'kibom-test'
    ext = 'csv'
    ctx = context.TestContext('BoMSimpleCSV', prj, ext)
    ctx.run(no_config_file=True)
    out = prj+'_bom_A.'+ext
    rows, components = ctx.load_csv(out)
    assert len(rows) == 5
    assert len(components) == 13
    assert 'R6' not in components
    for c in KIBOM_TEST_COMPONENTS:
        assert c in components
    ctx.clean_up()


def test_bom_simple_html():
    prj = 'kibom-test'
    ext = 'html'
    ctx = context.TestContext('BoMSimpleHTML', prj, ext)
    ctx.run(no_config_file=True)
    out = prj+'_bom_A.'+ext
    rows, components, dnf = ctx.load_html(out)
    assert len(rows) == 6
    assert len(components) == 13
    assert 'R6' not in components
    for c in KIBOM_TEST_COMPONENTS:
        assert c in components
    assert len(dnf) == 1
    assert 'R6' in dnf
    ctx.clean_up()


def test_bom_simple_xml():
    prj = 'kibom-test'
    ext = 'xml'
    ctx = context.TestContext('BoMSimpleXML', prj, ext)
    ctx.run(no_config_file=True)
    out = prj+'_bom_A.'+ext
    rows, components = ctx.load_xml(out)
    assert len(rows) == 5
    assert len(components) == 13
    assert 'R6' not in components
    for c in KIBOM_TEST_COMPONENTS:
        assert c in components
    ctx.clean_up()

