import mf2util.dt
from datetime import timedelta, date, datetime
import pytest


def test_none():
    assert mf2util.dt.parse(None) is None


def test_parse_dates():
    assert mf2util.dt.parse('2014-04-27') == date(2014, 4, 27)
    assert mf2util.dt.parse('2014-9-2') == date(2014, 9, 2)
    assert mf2util.dt.parse('1982-11-24') == date(1982, 11, 24)

    with pytest.raises(ValueError):
        # day/month switched
        mf2util.dt.parse('2014-24-11')

    with pytest.raises(ValueError):
        # 2-character year
        mf2util.dt.parse('14-09-27')


def test_parse_datetimes_no_tz():
    # tantek.com -- no seconds, no timezone
    assert mf2util.dt.parse('2014-05-09T17:53') == datetime(2014, 5, 9, 17, 53)
    # same as above without 'T'
    assert mf2util.dt.parse('2014-05-09 17:53') == datetime(2014, 5, 9, 17, 53)
    # Homebrew Website Club
    assert mf2util.dt.parse('2014-04-23T18:30') == datetime(2014, 4, 23, 18, 30)

    with pytest.raises(ValueError):
        # hour only
        mf2util.dt.parse('2012-09-01T12')

    with pytest.raises(ValueError):
        # invalid hour minute
        mf2util.dt.parse('2014-04-23T30:90')



def test_parse_datetimes():
    def assert_with_tz(dt, naive, offset):
        """return a tuple with naive datetime, and an timedelta tz offset"""
        assert naive == dt.replace(tzinfo=None)
        assert offset == dt.tzinfo.utcoffset(dt)

    # waterpigs.co.uk -- utc time
    assert_with_tz(mf2util.dt.parse('2014-05-10T10:48:28+00:00'),
                   datetime(2014, 5, 10, 10, 48, 28), timedelta(hours=0))

    # same as above with Zulu time
    assert_with_tz(mf2util.dt.parse('2014-05-10T10:48:28Z'),
                   datetime(2014, 5, 10, 10, 48, 28), timedelta(hours=0))

    # snarfed.org -- pacific time
    assert_with_tz(mf2util.dt.parse('2014-05-05T09:59:08-07:00'),
                   datetime(2014, 5, 5, 9, 59, 8), timedelta(hours=-7))

    # same as above, no colon in tz
    assert_with_tz(mf2util.dt.parse('2014-05-05T09:59:08-0700'),
                   datetime(2014, 5, 5, 9, 59, 8), timedelta(hours=-7))

    with pytest.raises(ValueError):
        # cannot read timezones by name
        mf2util.dt.parse('2013-07-04T11:22 PST')
