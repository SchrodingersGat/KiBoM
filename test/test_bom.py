from __future__ import print_function

import csv
import os


def check_files_exist():
    """
    Test that all expected generated BOM files are present
    """

    print("Checking output files...")

    assert(os.path.exists('test/bom-out_bom_A.csv'))
    assert(os.path.exists('test/bom-out_bom_A.xlsx'))
    assert(os.path.exists('test/bom-out_bom_A.xml'))
    assert(os.path.exists('test/bom-out_bom_A.html'))

    assert(os.path.exists('test/bomsubdir/bom-dir_bom_A.csv'))
    assert(os.path.exists('test/bomsubdir/secondsubdir/bom-dir2_bom_A.html'))


def check_csv_data():
    """
    Test the generated CSV data
    """

    print("Checking generated BOM...")

    BOM_FILE = "bom-out_bom_A.csv"

    BOM_FILE = os.path.join(os.path.dirname(__file__), BOM_FILE)

    lines = []

    with open(BOM_FILE, 'r') as bom_file:
        reader = csv.reader(bom_file, delimiter=',')

        lines = [line for line in reader]

    # Check that the header row contains the expected information
    assert 'Component' in lines[0]

    component_rows = []

    idx = 1

    while idx < len(lines):
        row = lines[idx]

        # Break on the first 'empty' row
        if len(row) == 0:
            break

        component_rows.append(row)

        idx += 1

    # We know how many component rows there should be
    assert len(component_rows) == 5

    # Create a list of components
    component_refs = []

    for row in component_rows:
        refs = row[3].split(" ")

        for ref in refs:
            # Ensure no component is duplicated in the BOM!
            if ref in component_refs:
                raise AssertionError("Component {ref} is duplicated".format(ref=ref))
        
    # R6 should be excluded from the BOM (marked as DNF)
    assert 'R6' not in component_refs


if __name__ == '__main__':

    print("Running BOM tests")

    check_files_exist()
    check_csv_data()

    print("All tests passed... OK...")
