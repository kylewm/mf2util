Microformats2 Utilities
=======================

[![Build
Status](https://travis-ci.org/kylewm/mf2util.svg?branch=master)](https://travis-ci.org/kylewm/mf2util)
[![Documentation
Status](https://readthedocs.org/projects/mf2util/badge/?version=latest)](https://readthedocs.org/projects/mf2util/?badge=latest)

Microformats2 provides an extremely flexible way to mark up HTML
documents, so that human-centric data is machine-discoverable. This
utility can be used to interpret a microformatted post or event, for
display as a [comment](http://indiewebcamp.com/comments-presentation) or
[reply-context](http://indiewebcamp.com/reply-context).

The library itself has no dependencies, but it won't do you much good
without an mf2 parser. I use and recommend
[mf2py](https://github.com/tommorris/mf2py).

Compatibility: Python 2.6, 2.7, 3.3+

License: [Simplified BSD](http://opensource.org/licenses/BSD-2-Clause)

Installation
------------

I've done my best to create appropriate unit tests for this library, but
it is very much alpha software at this point.

Install via pip

    pip install mf2util

or add as a submodule to your own project.

I've used pytest for running unit tests (These are also run
automatically by Travis-CI)

    pip install pytest
    python -m pytest

Quick Start
-----------

For received webmentions, use the method `mf2util.interpret_comment`.
This will return a dictionary with the fields necessary to display the
comment. For example:

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

Comments
--------

When processing an incoming webmention, you can use the
`mf2util.classify_comment` method to classify it as a reply, like, or
repost (or a combination thereof). The method returns a list of zero or
more strings (one of 'like', 'repost', or 'reply').

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

Datetimes
---------

The `mf2util.parse_datetime` function is useful for parsing microformats2
dates and datetimes. It can be used as a microformats-specific
alternative to larger, more general libraries like python-dateutil.

The definition for microformats2 dt-\* properties are fairly lenient.
This module will convert a mf2 date string into either a datetime.date
or datetime.datetime object. Datetimes will be naive unless a timezone
is specified.

Timezones are specified as fixed offsets from UTC.

### Usage

```python
import mf2py
import mf2util

parsed = mf2py.Parser(=…)
publishedstr = parsed.to_dict()['items'][0]['properties']['published'][0]
published = mf2util.parse_datetime(published)  # --> datetime.datetime
```

Authorship
----------

Use `mf2py.find_author` to determine an h-event's author name, url, and
photo. Uses the [authorship
algorithm](https://indiewebcamp.com/authorship) described on the
IndieWebCamp wiki.

Contributing
------------

If you find a bug or deficiency, feel free to file an issue, pull
request, or just message me in the \#indiewebcamp channel on freenode.

Changes
-------

All notable changes to this project will be documented here.

### 0.5.2 - 2023-01-15

- Bugfix: post-type-discovery should only return org if name and org properties are present. Thanks @snarfed!

### 0.5.1 - 2018-11-04

- Add `follow` to `post_type_discovery()`.

### 0.5.0 - 2016-10-27

- Fully implement location parsing based on https://indieweb.org/location#How_to_determine_the_location_of_a_microformat
  thanks to @snarfed

### 0.4.3 - 2016-08-20

- representative_hcard now includes h-cards that are properties of
  other h-* entities, thanks to @angelogladding

### 0.4.2 - 2016-05-09

- Added properties "dt-deleted", "u-logo", "u-featured"

### 0.4.1 - 2016-05-04

- Minor bugfix: interpret was passing parameters in the wrong order
  when parsing nested reply contexts and comments, which meant (in
  practice) `want_json` was always false, and dates were included as
  strings rather than datetimes.

### 0.4.0 - 2016-04-23
#### Added

- Update authorship implementation (`find_author`) to support fetching
  a separate page to find the author's h-card.
- Added a new optional parameter to all `interpret_*` methods called
  `fetch_mf2_func`. A good value for this is `lambda url: mf2py.parse(url=url)`

### 0.3.3 - 2016-04-07
#### Changed

- minor bugfixes to prevent throwing errors on bad mf2 input
- when a value (e.g. "name") is expected to be simple and we get a
  dict instead
- when a e-* value has "html" but not "value"

### 0.3.2 - 2016-03-01
#### Changed

- `interpret_feed` now skips rel=syndication when parsing syndication
  values for individual entries. This value should be empty for feeds,
  but if it isn't, it will almost always be wrong.

### 0.3.1 - 2016-02-17
#### Changed

- Added "poster" to the recognized URL properties of a video tag.

### 0.3.0 - 2016-02-17
#### Changed

- Added `base_href` parameter to all interpret methods. Now when
  content is normalized, it will take into account the base tag if
  it's given.
- Added `audio`, `video`, and `source` tags to the list of tags that
  might contain URL attributes.

### 0.2.12 - 2016-02-15
#### Added

- Added "photo" to common URL properties.

### 0.2.11 - 2016-01-02
#### Changed

- `is_name_a_title` accepts bytestrings now, no longer throws an error
  if the input is not unicode.

### 0.2.10 - 2015-11-27
#### Added

- `representative_hcard()` implementation of
  http://microformats.org/wiki/representative-h-card-parsing. Search
  all h-cards on a page and find the one that represents the page's
  author/owner.

### 0.2.9 - 2015-10-28
#### Changed

- Guard against mf2 required fields being None to make it a little
  easier for third parties (in this case Bridgy) to write unit tests.

### 0.2.8 - 2015-10-28
#### Added

- `post_type_discovery()` implementation that takes an h-event or
  h-entry and returns a string defining the post type (e.g. "article",
  "note", "like", etc.)

#### Changed

- Consolidated modules into one flat file for simplicity
- Renamed `parse_dt` to `parse_datetime` (old name still works for
  backcompat)
- In python 3, use builtin timezone implementation instead of
  mf2util's custom implementation

### 0.2.7 - 2015-10-05
#### Added

- add parsing for comment, like, and repost h-cites nested inside an
  h-entry

### 0.2.6 - 2015-09-24
#### Added

- added property content-plain to preserve the e-content value

### 0.2.5 - 2015-09-14
#### Changed

- minor bugfix: interpret should pass want_json recursively when
  fetching reply contexts.

### 0.2.4 - 2015-09-14

#### Added

- interpret methods now have an optional want_json argument. If true,
  result will be pure json with no Python-only objects (i.e. datetimes)

### 0.2.3 - 2015-08-27

#### Added

-   parse simple location name and url from events and entries \#\#\#
    Changed
-   accept complex-valued "url" properties and fallback to their "value"

### 0.2.1 - 2015-06-08

#### Changed

-   more lenient parsing of content as either e-content or p-content

### 0.2.0 - 2015-06-08

#### Added

-   parse nested h-cite comments as entries under the top-level entry
-   check for bookmark-of \#\#\# Changed
-   in-reply-to, repost-of, like-of all parse into a list of objects now
    instead of a list of urls

### 0.1.9 - 2015-04-01

#### Added

-   Parse event invitations as type ['invite', 'reply'].
-   Parse the list of invitees.

### 0.1.5 - 2015-02-18

#### Added

-   in-reply-to, like-of, and repost-of properties added to the
    interpret\_entry result.

### 0.1.4 - 2015-01-27

#### Changed

-   Authorship algorithm was incorrectly using the first h-entry on a
    page, even when parsing an h-feed that has many.

### 0.1.3 - 2014-12-14

#### Changed

-   RSVP replies are now classified as type 'rsvp' instead of 'reply'

### 0.1.2 - 2014-09-20

#### Added

-   Utility methods for interpreting h-feeds that contain one or more
    entries.

#### Changed

-   Handle parsing errors more gracefully.
-   Distinguish between explicit h-entry titles and auto-generated
    p-names (junk) when determining whether a post has a title

### 0.1.1 - 2014-06-21

#### Added

-   Include "syndication" attribute for including syndication URLs (e.g.
    for de-duplicating received comments)
-   Convert URL attributes from relative paths to absolute URLs for
    displaying foreign content.

### 0.1.0 - 2014-05-11

#### Added

-   Migrated code from Red Wind for reasoning about raw microformats2
    data into this library.
-   Methods for interpreting h-entry, h-event, and received comments (to
    decide whether they are replies, likes, reposts, etc.)
-   No-dependency method for parsing datetimes described in
    [http://microformats.org/wiki/value-class-pattern#Date_and_time_parsing](http://microformats.org/wiki/value-class-pattern#Date_and_time_parsing)
