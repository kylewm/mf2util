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
        hevent = util.find_first_entry(parsed)
        if not hevent or 'h-event' not in hevent['type']:
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

    for prop in ('start', 'end'):
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
         'name': plain-text event name,
         'content': body of event description (contains HTML),
         'author': {
          'name': author name,
          'url': author url,
          'photo': author photo
         }
        }

    :param dict parsed: the result of parsing a document containing mf2 markup
    :param str source_url: the URL of the parsed document, used by the
      authorship algorithm
    :param dict hevent: (optional): the item in the above document
      representing the h-entry. if provided, we can avoid a redundant
      call to find_first_entry
    :return: a dict with some or all of the described properties
    """

    # find the h-entry if it wasn't provided
    if not hentry:
        hentry = util.find_first_entry(parsed)
        if not hentry or 'h-entry' not in hentry['type']:
            return {}

    result = {'type': 'entry'}
    url_prop = hentry['properties'].get('url')
    if url_prop:
        result['url'] = url_prop[0]

    author = util.find_author(parsed, source_url)
    if author:
        result['author'] = author

    content_prop = hentry['properties'].get('content')
    content_value = None
    if content_prop:
        result['content'] = content_prop[0]['html'].strip()
        content_value = content_prop[0]['value'].strip()

    name_prop = hentry['properties'].get('name')
    if name_prop:
        title = name_prop[0].strip()
        if title != content_value:
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

    result['syndication'] = parsed['rels'].get('syndication', []) +\
        hentry['properties'].get('syndication', [])

    return result


def interpret(parsed, source_url):
    """Interpret an document of unknown type. Finds the first interesting
    h-* element, and delegates to :func:`interpret_entry` if it is an h-entry
    or :func:`interpret_event` if it is an h-event


    :param dict parsed: the result of parsing a mf2 document
    :param str source_url: the URL of the source document (used for authorship
        discovery)
    :return: a dict as described by interpret_entry or interpret_event, or None
    """
    item = util.find_first_entry(parsed)
    if item:
        if 'h-event' in item['type']:
            return interpret_event(parsed, source_url, hevent=item)
        else:
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
    item = util.find_first_entry(parsed)
    if item and 'h-entry' in item['type']:
        result = interpret_entry(parsed, source_url, item)
        if result:
            result['comment_type'] = util.classify_comment(
                parsed, target_urls)

            rsvp = item['properties'].get('rsvp')
            if rsvp:
                result['rsvp'] = rsvp[0]

        return result
