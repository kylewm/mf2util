from . import util
from . import dt


def interpret_event(parsed, hevent, source_url):
    result = {'type': 'event'}
    for prop in ('start', 'end'):
        date = dt.parse(' '.join(hevent['properties'].get(prop, [])))
        if date:
            result[prop] = date

    content_prop = hevent['properties'].get('content')
    if content_prop:
        result['content'] = content_prop[0]['html'].strip()

    name_prop = hevent['properties'].get('name')
    if name_prop:
        result['name'] = name_prop[0].strip()

    return result


def interpret_entry(parsed, hentry, source_url):
    result = {'type': 'entry'}
    for prop in ('published', 'updated'):
        date = dt.parse(' '.join(hentry['properties'].get(prop, [])))
        if date:
            result[prop] = date

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

    author = util.find_author(parsed, source_url)
    if author:
        result['author'] = author

    return result


def interpret(parsed, url):
    item = util.find_first_entry(parsed)
    if item:
        if 'h-event' in item['type']:
            return interpret_event(parsed, item, url)
        else:
            return interpret_entry(parsed, item, url)
