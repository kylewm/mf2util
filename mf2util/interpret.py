"""Interpret a parsed JSON document, for the purpose of displaying
received comments and/or reply contexts. Currently supports h-entry and
h-event."""

from . import util
from . import dt
import logging


def interpret_event(parsed, source_url, hevent=None):
    """Given a document containing an h-event, return a dictionary::

        {
         'type': 'event',
         'url': the permalink url of the document (may be different than source_url),
         'start': datetime or date,
         'end': datetime or date,
         'name': plain-text event name,
         'content': body of event description (contains HTML)
        }

    :param dict parsed: the result of parsing a document containing mf2 markup
    :param str source_url: the URL of the parsed document, not currently used
    :param dict hevent: (optional) the item in the above document representing
      the h-event. if provided, we can avoid a redundant call to
      find_first_entry
    :return: a dict with some or all of the described properties
    """
    # find the h-event if it wasn't provided
    if not hevent:
        hevent = util.find_first_entry(parsed, ['h-event'])
        if not hevent:
            return {}

    result = {'type': 'event'}
    url_prop = hevent['properties'].get('url')
    if url_prop:
        result['url'] = url_prop[0]

    content_prop = hevent['properties'].get('content')
    if content_prop:
        result['content'] = util.convert_relative_paths_to_absolute(
            source_url, content_prop[0]['html'].strip())

    name_prop = hevent['properties'].get('name')
    if name_prop:
        result['name'] = name_prop[0].strip()

    for prop in ('start', 'end', 'published', 'updated'):
        date_strs = hevent['properties'].get(prop)
        if date_strs:
            result[prop + '-str'] = date_strs[0]
            try:
                date = dt.parse(date_strs[0])
                if date:
                    result[prop] = date
            except ValueError:
                logging.warn('Failed to parse datetime %s', date_strs[0])

    # TODO parse event location

    return result


def interpret_entry(parsed, source_url, hentry=None):
    """Given a document containing an h-entry, return a dictionary::

        {
         'type': 'entry',
         'url': the permalink url of the document (may be different than source_url),
         'published': datetime or date,
         'updated': datetime or date,
         'name': title of the entry,
         'content': body of entry (contains HTML),
         'author': {
          'name': author name,
          'url': author url,
          'photo': author photo
         },
         'syndication': [
           'syndication url',
           ...
         ],
         'in-reply-to': [...],
         'like-of': [...],
         'repost-of': [...],
        }

    :param dict parsed: the result of parsing a document containing mf2 markup
    :param str source_url: the URL of the parsed document, used by the
      authorship algorithm
    :param dict hentry: (optional) the item in the above document
      representing the h-entry. if provided, we can avoid a redundant
      call to find_first_entry
    :return: a dict with some or all of the described properties
    """

    # find the h-entry if it wasn't provided
    if not hentry:
        hentry = util.find_first_entry(parsed, ['h-entry'])
        if not hentry:
            return {}

    result = {'type': 'entry'}
    url_prop = hentry['properties'].get('url')
    if url_prop:
        result['url'] = url_prop[0]

    author = util.find_author(parsed, source_url, hentry)
    if author:
        result['author'] = author

    content_prop = hentry['properties'].get('content')
    content_value = None
    if content_prop:
        result['content'] = util.convert_relative_paths_to_absolute(
            source_url, content_prop[0]['html'].strip())
        content_value = content_prop[0]['value'].strip()

    name_prop = hentry['properties'].get('name')
    if name_prop:
        title = name_prop[0].strip()
        if util.is_name_a_title(title, content_value):
            result['name'] = title

    for prop in ('published', 'updated'):
        date_strs = hentry['properties'].get(prop)
        if date_strs:
            result[prop + '-str'] = date_strs[0]
            try:
                date = dt.parse(date_strs[0])
                if date:
                    result[prop] = date
            except ValueError:
                logging.warn('Failed to parse datetime %s', date_strs[0])

    for prop in ('in-reply-to', 'like-of', 'repost-of'):
        for url_prop in hentry['properties'].get(prop, []):
            result.setdefault(prop, [])
            if isinstance(url_prop, dict):
                result.setdefault(prop, []).extend(
                    url_prop.get('properties', {}).get('url', []))
            else:
                result.setdefault(prop, []).append(url_prop)

    result['syndication'] = list(
        set((parsed['rels'].get('syndication', []) +
             hentry['properties'].get('syndication', []))))

    return result


def interpret_feed(parsed, source_url, hfeed=None):
    """Interpret a source page as an h-feed or as an top-level collection
    of h-entries.

    :param dict parsed: the result of parsing a mf2 document
    :param str source_url: the URL of the source document (used for authorship
        discovery)
    :param dict item: (optional) the item to be parsed. If provided,
        this will be used instead of the first element on the page.
    :return: a dict containing 'entries', a list of entries, and possibly other
        feed properties (like 'name').
    """
    result = {}
    # find the first feed if it wasn't provided
    if not hfeed:
        hfeed = util.find_first_entry(parsed, ['h-feed'])

    if hfeed:
        names = hfeed['properties'].get('name')
        if names:
            result['name'] = names[0]
        children = hfeed.get('children', [])
    # just use the top level 'items' as the feed children
    else:
        children = parsed.get('items', [])

    entries = []
    for child in children:
        entry = interpret(parsed, source_url, item=child)
        if entry:
            entries.append(entry)
    result['entries'] = entries
    return result


def interpret(parsed, source_url, item=None):
    """Interpret a permalink of unknown type. Finds the first interesting
    h-* element, and delegates to :func:`interpret_entry` if it is an
    h-entry or :func:`interpret_event` for an h-event

    :param dict parsed: the result of parsing a mf2 document
    :param str source_url: the URL of the source document (used for authorship
        discovery)
    :param dict item: (optional) the item to be parsed. If provided,
        this will be used instead of the first element on the page.
    :return: a dict as described by interpret_entry or interpret_event, or None
    """
    if not item:
        item = util.find_first_entry(parsed, ['h-entry', 'h-event'])

    if item:
        if 'h-event' in item['type']:
            return interpret_event(parsed, source_url, hevent=item)
        elif 'h-entry' in item['type']:
            return interpret_entry(parsed, source_url, hentry=item)


def interpret_comment(parsed, source_url, target_urls):
    """Interpret received webmentions, and classify as like, reply, or
    repost (or a combination thereof). Returns a dict as described
    in :func:`interpret_entry`, with the additional fields::

        {
         'comment_type': a list of strings, zero or more of
                         'like', 'reply', or 'repost'
         'rsvp': a string containing the rsvp response (optional)
        }

    :param dict parsed: a parsed mf2 parsed document
    :param str source_url: the URL of the source document
    :param list target_urls: a collection containing the URL of the target\
      document, and any alternate URLs (e.g., shortened links) that should\
      be considered equivalent when looking for references
    :return: a dict as described above, or None
    """
    item = util.find_first_entry(parsed, ['h-entry'])
    if item:
        result = interpret_entry(parsed, source_url, item)
        if result:
            result['comment_type'] = util.classify_comment(
                parsed, target_urls)

            rsvp = item['properties'].get('rsvp')
            if rsvp:
                result['rsvp'] = rsvp[0].lower()

        return result
