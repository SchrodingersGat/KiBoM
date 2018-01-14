import re

#'better' sorting function which sorts by NUMERICAL value not ASCII
def natural_sort(string):
	return [int(s) if s.isdigit() else s for s in re.split(r'(\d+)',string)]
