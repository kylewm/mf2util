"""Utilities for interpreting mf2 data.

Microformats2 is a general way to mark up any HTML document with
classes and propeties. This module uses domain-specific assumptions
about the classes (specifically h-entry and h-event) to extract
certain interesting properties."""

from .dt import parse as parse_dt
from .util import find_first_entry, classify_comment, find_author
from .interpret import interpret, interpret_event, interpret_entry,\
    interpret_comment, interpret_feed

__all__ = ['interpret', 'interpret_comment', 'interpret_event',
           'interpret_entry', 'interpret_feed', 'parse_dt',
           'find_first_entry', 'classify_comment', 'find_author']
