"""Interpret a parsed JSON document, for the purpose of displaying
received comments and/or reply contexts. Currently supports h-entry and
h-event."""

from . import util
from . import dt
import logging


def _interpret_common_properties(parsed, source_url, hentry, want_json):
    result = {}
    for prop in ('url', 'uid'):
        url_strs = hentry['properties'].get(prop)
        if url_strs:
            if isinstance(url_strs[0], dict):
                result[prop] = url_strs[0].get('value')
            else:
                result[prop] = url_strs[0]

    for prop in ('start', 'end', 'published', 'updated'):
        date_strs = hentry['properties'].get(prop)
        if date_strs:
            if want_json:
                result[prop] = date_strs[0]
            else:
                result[prop + '-str'] = date_strs[0]
                try:
                    date = dt.parse(date_strs[0])
                    if date:
                        result[prop] = date
                except ValueError:
                    logging.warn('Failed to parse datetime %s', date_strs[0])

    author = util.find_author(parsed, source_url, hentry)
    if author:
        result['author'] = author

    content_prop = hentry['properties'].get('content')
    content_value = None
    if content_prop:
        if isinstance(content_prop[0], dict):
            content_html = content_prop[0]['html'].strip()
            content_value = content_prop[0]['value'].strip()
        else:
            content_value = content_html = content_prop[0]
        result['content'] = util.convert_relative_paths_to_absolute(
            source_url, content_html)
        result['content-plain'] = content_value

    # TODO handle h-adr and h-geo variants
    locations = hentry['properties'].get('location')
    if locations:
        result['location'] = {}
        if isinstance(locations[0], dict):
            for loc_prop in ('url', 'name', 'latitude', 'longitude'):
                loc_values = locations[0]['properties'].get(loc_prop)
                if loc_values:
                    result['location'][loc_prop] = loc_values[0]
        else:
            result['location'] = {'name': locations[0]}

    result['syndication'] = list(
        set((parsed['rels'].get('syndication', []) +
             hentry['properties'].get('syndication', []))))

    return result


def interpret_event(parsed, source_url, hevent=None, want_json=False):
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
    :param boolean want_json: (optional, default false) if true, the result
      will be pure json with datetimes as strings instead of python objects
    :return: a dict with some or all of the described properties
    """
    # find the h-event if it wasn't provided
    if not hevent:
        hevent = util.find_first_entry(parsed, ['h-event'])
        if not hevent:
            return {}

    result = _interpret_common_properties(
        parsed, source_url, hevent, want_json)
    result['type'] = 'event'

    name_prop = hevent['properties'].get('name')
    if name_prop:
        result['name'] = name_prop[0].strip()

    return result


def interpret_entry(parsed, source_url, hentry=None, want_json=False):
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
    :param boolean want_json: (optional, default False) if true, the result
      will be pure json with datetimes as strings instead of python objects
    :return: a dict with some or all of the described properties
    """

    # find the h-entry if it wasn't provided
    if not hentry:
        hentry = util.find_first_entry(parsed, ['h-entry'])
        if not hentry:
            return {}

    result = _interpret_common_properties(
        parsed, source_url, hentry, want_json)
    if 'h-cite' in hentry.get('type', []):
        result['type'] = 'cite'
    else:
        result['type'] = 'entry'

    name_prop = hentry['properties'].get('name')
    if name_prop:
        title = name_prop[0].strip()
        if util.is_name_a_title(title, result.get('content-plain')):
            result['name'] = title

    for prop in ('in-reply-to', 'like-of', 'repost-of', 'bookmark-of',
                 'comment', 'like', 'repost'):
        for url_val in hentry['properties'].get(prop, []):
            if isinstance(url_val, dict):
                result.setdefault(prop, []).append(
                    interpret(parsed, source_url, url_val, want_json))
            else:
                result.setdefault(prop, []).append({
                    'url': url_val,
                })

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


def interpret(parsed, source_url, item=None, want_json=False):
    """Interpret a permalink of unknown type. Finds the first interesting
    h-* element, and delegates to :func:`interpret_entry` if it is an
    h-entry or :func:`interpret_event` for an h-event

    :param dict parsed: the result of parsing a mf2 document
    :param str source_url: the URL of the source document (used for authorship
      discovery)
    :param dict item: (optional) the item to be parsed. If provided,
      this will be used instead of the first element on the page.
    :param boolean want_json: (optional, default False) If true, the result
      will be pure json with datetimes as strings instead of python objects
    :return: a dict as described by interpret_entry or interpret_event, or None
    """
    if not item:
        item = util.find_first_entry(parsed, ['h-entry', 'h-event'])

    if item:
        if 'h-event' in item['type']:
            return interpret_event(
                parsed, source_url, hevent=item, want_json=want_json)
        elif 'h-entry' in item['type'] or 'h-cite' in item['type']:
            return interpret_entry(
                parsed, source_url, hentry=item, want_json=want_json)


def interpret_comment(parsed, source_url, target_urls, want_json=False):
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
    :param boolean want_json: (optional, default False) If true, the result
      will be pure json with datetimes as strings instead of python objects
    :return: a dict as described above, or None
    """
    item = util.find_first_entry(parsed, ['h-entry'])
    if item:
        result = interpret_entry(parsed, source_url, item, want_json)
        if result:
            result['comment_type'] = util.classify_comment(
                parsed, target_urls)

            rsvp = item['properties'].get('rsvp')
            if rsvp:
                result['rsvp'] = rsvp[0].lower()

            invitees = item['properties'].get('invitee')
            if invitees:
                result['invitees'] = [
                    util.parse_author(inv) for inv in invitees]

        return result
