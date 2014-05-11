"""Utilities for interpreting mf2 data.

Microformats2 is a general way to mark up any HTML document with
classes and propeties. This module uses domain-specific assumptions
about the classes (specifically h-entry and h-event) to extract
certain interesting properties."""

from collections import deque


H_CLASSES = ['h-entry', 'h-event']


def find_first_entry(parsed):
    """Find the first interesting h-* (current h-entry or h-event) object
    in BFS-order

    Args:
     parsed: a mf2py parsed dict

    Return:
     an mf2py item that is one of H_CLASSES, or None

    """
    queue = deque(item for item in parsed['items'])
    while queue:
        item = queue.popleft()
        if any(h_class in item['type'] for h_class in H_CLASSES):
            return item
        queue.extend(item.get('children', []))


def find_mentions(parsed, target_urls):
    """Find and categorize mentions that reference any of a collection of
    target URLs. Looks for references of type reply, like, and repost.

    Args:
     parsed: a mf2py parsed dict
     target_urls: a collection of urls that represent the target post.
                  this can include alternate or shortened URLs.

    Return:
     a list of tuples, (target URL, reference type)
    """

    def process_references(objs, reftype):
        refs = []
        for obj in objs:
            if isinstance(obj, dict):
                refs += [(url, reftype) for url
                         in obj.get('properties', {}).get('url', [])
                         if url in target_urls]
            elif obj in target_urls:
                refs.append((obj, reftype))

        return refs

    hentry = find_first_entry(parsed)
    references = []

    if hentry:
        for prop in ('in-reply-to', 'reply-to', 'reply'):
            references += process_references(
                hentry['properties'].get(prop, []), 'reply')

        for prop in ('like-of', 'like'):
            references += process_references(
                hentry['properties'].get(prop, []), 'like')

        for prop in ('repost-of', 'repost'):
            references += process_references(
                hentry['properties'].get(prop, []), 'repost')

    return references


def find_author(parsed, source_url=None):
    """Use the authorship discovery algorithm
    https://indiewebcamp.com/authorship to determine and h-entry's
    author.

    Args:
     parsed: an mf2py parsed dict
     source_url: the source of the parsed document (optional)

    Return:
     a tuple containing the author's name, photo, and url
    """

    def parse_author(obj):
        if isinstance(obj, dict):
            names = obj['properties'].get('name')
            photos = obj['properties'].get('photo')
            urls = obj['properties'].get('url')
            return (names and names[0],
                    urls and urls[0],
                    photos and photos[0])
        else:
            return obj, None, None

    hentry = find_first_entry(parsed)
    if not hentry:
        return None, None, None

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

    # we're out of options
    return None, None, None
