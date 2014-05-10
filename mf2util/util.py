"""Utilities for interpreting mf2 data.

Microformats2 is a general way to mark up any HTML document with
classes and propeties. This module uses domain-specific assumptions
about the classes (specifically h-entry and h-event) to extract
certain interesting properties."""

from collections import deque


H_CLASSES = ['h-entry', 'h-event']


def find_first_entry(parsed):
    """Find the first interesting h-* object in BFS-order

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
