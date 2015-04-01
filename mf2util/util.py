"""Utilities for interpreting mf2 data.

Microformats2 is a general way to mark up any HTML document with
classes and propeties. This module uses domain-specific assumptions
about the classes (specifically h-entry and h-event) to extract
certain interesting properties."""

from __future__ import unicode_literals
from collections import deque
from . import dt
import re
import unicodedata

# 2/3 compatibility
try:
    from urllib.parse import urljoin
except ImportError:
    from urlparse import urljoin

URL_ATTRIBUTES = {
    'a': ['href'],
    'link': ['href'],
    'img': ['src'],
}


def find_first_entry(parsed, types):
    """Find the first interesting h-* object in BFS-order

    :param dict parsed: a mf2py parsed dict
    :param list types: target types, e.g. ['h-entry', 'h-event']
    :return: an mf2py item that is one of `types`, or None
    """
    queue = deque(item for item in parsed['items'])
    while queue:
        item = queue.popleft()
        if any(h_class in item['type'] for h_class in types):
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
    def process_references(objs, reftypes, result):
        for obj in objs:
            if isinstance(obj, dict):
                if any(url in target_urls for url
                       in obj.get('properties', {}).get('url', [])):
                    result += (r for r in reftypes if r not in result)
            elif obj in target_urls:
                result += (r for r in reftypes if r not in result)

    result = []
    hentry = find_first_entry(parsed, ['h-entry'])
    if hentry:
        reply_type = []
        if 'rsvp' in hentry['properties']:
            reply_type.append('rsvp')
        if 'invitee' in hentry['properties']:
            reply_type.append('invite')
        reply_type.append('reply')

        # TODO handle rel=in-reply-to
        for prop in ('in-reply-to', 'reply-to', 'reply'):
            process_references(
                hentry['properties'].get(prop, []), reply_type, result)

        for prop in ('like-of', 'like'):
            process_references(
                hentry['properties'].get(prop, []), ('like',), result)

        for prop in ('repost-of', 'repost'):
            process_references(
                hentry['properties'].get(prop, []), ('repost',), result)

    return result


def parse_author(obj):
    """Parse the value of a u-author property, can either be a compound
    h-card or a single name or url.

    :param object obj: the mf2 property value, either a dict or a string
    :result: a dict containing the author's name, photo, and url
    """
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
    elif obj:
        if obj.startswith('http://') or obj.startswith('https://'):
            result['url'] = obj
        else:
            result['name'] = obj
    return result


def find_author(parsed, source_url=None, hentry=None):
    """Use the authorship discovery algorithm
    https://indiewebcamp.com/authorship to determine and h-entry's
    author.

    :param dict parsed: an mf2py parsed dict.
    :param str source_url: the source of the parsed document.
    :return: a dict containing the author's name, photo, and url
    """
    if not hentry:
        hentry = find_first_entry(parsed, ['h-entry'])
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


def is_name_a_title(name, content):
    """Determine whether the name property represents an explicit title.

    Typically when parsing an h-entry, we check whether p-name ==
    e-content (value). If they are non-equal, then p-name likely
    represents a title.

    However, occasionally we come across an h-entry that does not
    provide an explicit p-name. In this case, the name is
    automatically generated by converting the entire h-entry content
    to plain text. This definitely does not represent a title, and
    looks very bad when displayed as such.

    To handle this case, we broaden the equality check to see if
    content is a subset of name. We also strip out non-alphanumeric
    characters just to make the check a little more forgiving.

    :param str name: the p-name property that may represent a title
    :param str content: the plain-text version of an e-content property
    :return: True if the name likely represents a separate, explicit title
    """
    def normalize(s):
        s = unicodedata.normalize('NFKD', s)
        s = s.lower()
        s = re.sub('[^a-z0-9]', '', s)
        return s
    if not content:
        return True
    if not name:
        return False
    return normalize(content) not in normalize(name)
