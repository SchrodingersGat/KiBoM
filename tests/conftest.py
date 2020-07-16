"""
Test configuration
"""


def pytest_addoption(parser):
    parser.addoption("--test_dir", action="store", default=None,
                     help="the test output dir to use (omit to use a temp dir). "
                     "If given, outputs will _not_ be cleared after testing.")
