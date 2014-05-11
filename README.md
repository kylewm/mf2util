# Microformats2 Utilities

[![Build Status](https://travis-ci.org/kylewm/mf2util.svg?branch=master)](https://travis-ci.org/kylewm/mf2util)


Microformats2 provides an extremely flexible way to mark up HTML
documents, so that human-centric data is machine-discoverable. This
utility can be used to interpret a microformatted post or event, for
display as a [comment][] or [reply-context][].

The library itself has no dependencies, but it won't do you much good
without an mf2 parser. I use and recommend Kartik Prabhu's branch of
[mf2py](https://github.com/kartikprabhu/mf2py).

Compatibility: Python 2.6, 2.7, 3.3+

License: [Simplified BSD](http://opensource.org/licenses/BSD-2-Clause)

## Installation

I've done my best to create appropriate unit tests for this library,
but it is very much alpha software at this point.

To install, your best bet for installation is:

    pip install -e git+https://github.com/kylewm/mf2util

or add as a submodule to your own project.

I've used pytest for running unit tests (These are also run
automatically by Travis-CI)

    pip install pytest
    python -m pytest

## Quick Start

For received webmentions, use the method
`mf2util.interpret_comment`. This will return a dictionary with the
fields necessary to display the comment. For example:

    ```python
    import mf2py
    import mf2util

    # source_url = source_url of incoming webmention
    # target_url = target_url of incoming webmention

    parsed = mf2py.Parser(url=source_url).to_dict()
    comment = mf2util.interpret_comment(parsed, source_url, [target_url])

    # result
    {
     'type': 'entry',
     'name': 'Re: How to make toast',
     'content': '<p>This solved my problem, thanks!</p>',
     'url': 'http://facebook.com/posts/0123456789',
     'published': datetime.datetime(2014, 11, 24, 13, 24)
     'author': {
      'name': 'John Doe',
      'url': 'http://facebook.com/john.doe',
      'photo': 'http://img.facebook.com/johndoe-profile-picture.jpg'
     },
     'comment_type': ['reply']
    }
    ```

When display reply-context, you may not know the precise type of the
source document. Use the method `mf2util.interpret` to interpret the
document, it will figure out the document's primary h- type and return
the appropriate fields for display. Currently supports h-entry and
h-event style documents.

    ```python
    import mf2py
    import mf2util

    # reply_to_url = url being replied to

    parsed = mf2py.Parser(url=rely_to_url).to_dict()
    entry = mf2util.interpret(parsed, reply_to_url)

    # result
    {
     'type': 'event',
     'name': 'Homebrew Website Club',
     'start': datetime.datetime(2014, 5, 7, 18, 30),
     'end': datetime.datetime(2014, 5, 7, 19, 30),
     'content': '<p>Exchange information, swap ideas, talk shop, help work on a project ...</p>'
    }
    ```

For most users, these two methods alone may be sufficient.

## Comments

When processing an incoming webmention, you can use the
`mf2util.classify_comment` method to classify it as a reply, like, or
repost (or a combination thereof). The method returns a list of zero
or more strings (one of 'like', 'repost', or 'reply').

### Usage

    ```python
    import mf2py
    import mf2util

    # receive webmention from source_url to target_url
    target_url = 'http://my-domain.com/2014/04/12/1'
    alternate_url = 'http://doma.in/V4ls'
    parsed = mf2py.Parser(url=source_url)
    mentions = mf2util.classify_comment(parsed, [target_url, alternative_url])
    ```


## Datetimes

The `mf2util.parse_dt` function is useful for parsing microformats2
dates and datetimes. It can be used as a microformats-specific
alternative to larger, more general libraries like python-dateutil.

The definition for microformats2 dt-* properties are fairly lenient.
This module will convert a mf2 date string into either a datetime.date
or datetime.datetime object. Datetimes will be naive unless a timezone
is specified.

Timezones are specified as fixed offsets from UTC.

### Usage

    ```python
    import mf2py
    import mf2util

    parsed = mf2py.Parser(url=…)
    publishedstr = parsed.to_dict()['items'][0]['properties']['published'][0]
    published = mf2util.parse_dt(published)  # --> datetime.datetime
    ```

## Authorship

Use `mf2py.find_author` to determine an h-event's author name, url,
and photo. Uses the
[authorship algorithm][authorship] described
on the IndieWebCamp wiki.


## Contributing

If you find a bug or deficiency, feel free to file an issue, pull
request, or just message me in the #indiewebcamp channel on freenode.


 [reply-context]: http://indiewebcamp.com/reply-context
 [comment]: http://indiewebcamp.com/comments-presentation
 [authorship]: https://indiewebcamp.com/authorship
