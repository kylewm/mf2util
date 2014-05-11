"""Utilities for interpreting the JSON result of parsing (e.g., with
mf2py) a microformats document
"""

from .dt import parse as parse_dt
from .util import find_first_entry, classify_comment, find_author
from .interpret import interpret, interpret_event, interpret_entry,\
    interpret_comment
