# -*- coding: utf-8 -*-

import re


def natural_sort(string):
    """
    Natural sorting function which sorts by numerical value of a string,
    rather than raw ASCII value.
    """
    return [int(s) if s.isdigit() else s for s in re.split(r'(\d+)', string)]
