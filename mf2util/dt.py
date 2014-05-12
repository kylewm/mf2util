import re
from datetime import tzinfo, timedelta, datetime, date


def parse(s):
    """The definition for microformats2 dt-* properties are fairly
    lenient.  This method converts an mf2 date string into either a
    datetime.date or datetime.datetime object. Datetimes will be naive
    unless a timezone is specified.

    :param str s: a mf2 string representation of a date or datetime
    :return: datetime.date or datetime.datetime
    :raises ValueError: if the string is not recognizable
    """

    if not s:
        return None

    s = re.sub('\s+', ' ', s)
    date_re = "(?P<year>\d{4,})-(?P<month>\d{1,2})-(?P<day>\d{1,2})"
    time_re = "(?P<hour>\d{1,2}):(?P<minute>\d{2})(:(?P<second>\d{2})(\.(?P<microsecond>\d+))?)?"
    tz_re = "(?P<tzz>Z)|(?P<tzsign>[+-])(?P<tzhour>\d{1,2}):?(?P<tzminute>\d{2})"
    dt_re = "%s((T| )%s ?(%s)?)?$" % (date_re, time_re, tz_re)

    m = re.match(dt_re, s)
    if not m:
        raise ValueError('unrecognized datetime %s' % s)

    year = m.group('year')
    month = m.group('month')
    day = m.group('day')

    hour = m.group('hour')

    if not hour:
        return date(int(year), int(month), int(day))

    minute = m.group('minute') or "00"
    second = m.group('second') or "00"

    if hour:
        dt = datetime(int(year), int(month), int(day), int(hour),
                      int(minute), int(second))
    if m.group('tzz'):
        dt = dt.replace(tzinfo=utc)
    else:
        tzsign = m.group('tzsign')
        tzhour = m.group('tzhour')
        tzminute = m.group('tzminute') or "00"

        if tzsign and tzhour:
            offset = timedelta(hours=int(tzhour),
                               minutes=int(tzminute))
            if tzsign == '-':
                offset = -offset
            dt = dt.replace(tzinfo=FixedOffset(
                offset, '%s%s:%s' % (tzsign, tzhour, tzminute)))

    return dt


ZERO = timedelta(0)


class UTC(tzinfo):
    """UTC timezone, from Python documentation
    https://docs.python.org/2/library/datetime.html#tzinfo-objects"""

    def utcoffset(self, dt):
        return ZERO

    def tzname(self, dt):
        return "UTC"

    def dst(self, dt):
        return ZERO

utc = UTC()


class FixedOffset(tzinfo):
    """A class building tzinfo objects for fixed-offset time zones.
    Note that FixedOffset(0, "UTC") is a different way to build a
    UTC tzinfo object.

    Fixed offset in minutes east from UTC. from Python 2 documentation
    https://docs.python.org/2/library/datetime.html#tzinfo-objects"""

    def __init__(self, offset, name):
        self.__offset = offset
        self.__name = name

    def utcoffset(self, dt):
        return self.__offset

    def tzname(self, dt):
        return self.__name

    def dst(self, dt):
        return ZERO
