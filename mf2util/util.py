"""Utilities for interpreting mf2 data.

Microformats2 is a general way to mark up any HTML document with
classes and propeties. This module uses domain-specific assumptions
about the classes (specifically h-entry and h-event) to extract
certain interesting properties."""

from __future__ import unicode_literals
from collections import deque
from . import dt
import re

# 2/3 compatibility
try:
    from urllib.parse import urljoin
except ImportError:
    from urlparse import urljoin

H_CLASSES = ['h-entry', 'h-event']

URL_ATTRIBUTES = {
    'a': ['href'],
    'link': ['href'],
    'img': ['src'],
}


def find_first_entry(parsed):
    """Find the first interesting h-* (current h-entry or h-event) object
    in BFS-order

    :param dict parsed: a mf2py parsed dict
    :return: an mf2py item that is one of `H_CLASSES`, or None
    """
    queue = deque(item for item in parsed['items'])
    while queue:
        item = queue.popleft()
        if any(h_class in item['type'] for h_class in H_CLASSES):
            return item
        queue.extend(item.get('children', []))


def find_datetimes(parsed):
    """Find published, updated, start, and end dates.

    :param dict parsed: a mf2py parsed dict
    :return: a dictionary from property type to datetime or date
    """
    hentry = find_first_entry(parsed)
    result = {}

    if hentry:
        for prop in ('published', 'updated', 'start', 'end'):
            date_strs = hentry['properties'].get(prop, [])
            result[prop] = dt.parse(' '.join(date_strs))


def classify_comment(parsed, target_urls):
    """Find and categorize comments that reference any of a collection of
    target URLs. Looks for references of type reply, like, and repost.

    :param dict parsed: a mf2py parsed dict
    :param list target_urls: a collection of urls that represent the
      target post. this can include alternate or shortened URLs.
    :return: a list of applicable comment types ['like', 'reply', 'repost']
    """
    result = set()

    def process_references(objs, reftype):
        for obj in objs:
            if isinstance(obj, dict):
                if any(url in target_urls for url
                       in obj.get('properties', {}).get('url', [])):
                    result.add(reftype)

            elif obj in target_urls:
                result.add(reftype)

    hentry = find_first_entry(parsed)
    if hentry:
        # TODO handle rel=in-reply-to
        for prop in ('in-reply-to', 'reply-to', 'reply'):
            process_references(
                hentry['properties'].get(prop, []),
                'rsvp' if 'rsvp' in hentry['properties'] else 'reply')

        for prop in ('like-of', 'like'):
            process_references(
                hentry['properties'].get(prop, []), 'like')

        for prop in ('repost-of', 'repost'):
            process_references(
                hentry['properties'].get(prop, []), 'repost')

    return list(result)


def find_author(parsed, source_url=None):
    """Use the authorship discovery algorithm
    https://indiewebcamp.com/authorship to determine and h-entry's
    author.

    :param dict parsed: an mf2py parsed dict.
    :param str source_url: the source of the parsed document.
    :return: a dict containing the author's name, photo, and url
    """

    def parse_author(obj):
        result = {}
        if isinstance(obj, dict):
            names = obj['properties'].get('name')
            photos = obj['properties'].get('photo')
            urls = obj['properties'].get('url')
            if names:
                result['name'] = names[0]
            if photos:
                result['photo'] = photos[0]
            if urls:
                result['url'] = urls[0]
        else:
            result['name'] = obj
        return result

    hentry = find_first_entry(parsed)
    if not hentry:
        return None

    for obj in hentry['properties'].get('author', []):
        return parse_author(obj)

    # try to find an author of the top-level h-feed
    for hfeed in (card for card in parsed['items']
                  if 'h-feed' in card['type']):
        for obj in hfeed['properties'].get('author', []):
            return parse_author(obj)

    # top-level h-cards
    hcards = [card for card in parsed['items']
              if 'h-card' in card['type']]

    if source_url:
        for item in hcards:
            if source_url in item['properties'].get('url', []):
                return parse_author(item)

    rel_mes = parsed["rels"].get("me", [])
    for item in hcards:
        urls = item['properties'].get('url', [])
        if any(url in rel_mes for url in urls):
            return parse_author(item)

    rel_authors = parsed["rels"].get("author", [])
    for item in hcards:
        urls = item['properties'].get('url', [])
        if any(url in rel_authors for url in urls):
            return parse_author(item)

    # just return the first h-card
    if hcards:
        return parse_author(hcards[0])


def convert_relative_paths_to_absolute(source_url, html):
    """Attempt to convert relative paths in foreign content
    to absolute based on the source url of the document. Useful for
    displaying images or links in reply contexts and comments.

    Gets list of tags/attributes from `URL_ATTRIBUTES`. Note that this
    function uses a regular expression to avoid adding a library
    dependency on a proper parser.

    :param str source_url: the source of the parsed document.
    :param str html: the text of the source document
    :return: the document with relative urls replaced with absolute ones
    """
    def do_convert(match):
        return (match.string[match.start(0):match.start(1)] +
                urljoin(source_url, match.group(1)) +
                match.string[match.end(1):match.end(0)])

    if source_url:
        for tagname, attributes in URL_ATTRIBUTES.items():
            for attribute in attributes:
                pattern = re.compile(
                    '<%s[^>]*?%s\s*=\s*[\'"](.*?)[\'"]' % (tagname, attribute),
                    flags=re.DOTALL | re.MULTILINE | re.IGNORECASE)
                html = pattern.sub(do_convert, html)

    return html
