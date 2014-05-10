# mf2datetime

[![Build Status](https://travis-ci.org/kylewm/mf2datetime.svg?branch=master)](https://travis-ci.org/kylewm/mf2datetime)

A microformats2 datetime parser for Python. This can be used as a
microformats-specific alternative to larger, more general libraries
like python-dateutil.

The definition for microformats2 dt-* properties are fairly lenient.
This module will convert a mf2 date string into either a datetime.date
or datetime.datetime object. Datetimes will be naive unless a timezone
is specified.

Timezones are specified as fixed offsets from UTC.

## Usage

```python
import mf2py import mf2datetime

parsed = mf2py.Parser(url='http://kylewm.com/note/2014/05/07/2')
publishedstr = parsed.to_dict()['items'][0]['properties']['published'][0]
published = mf2datetime.parse(published)  # --> datetime.datetime
```
