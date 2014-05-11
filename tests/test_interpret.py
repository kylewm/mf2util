"""Test the interpret module, the unification of the other utility methods.
Uses test cases from around the indieweb.
"""
from datetime import datetime, date, timedelta
import mf2util
import json


def load_test(testname):
    return json.load(open('tests/interpret/%s.json' % testname))


def test_event():
    # HWC event from werd.io
    parsed = load_test('hwc-event')
    result = mf2util.interpret(
        parsed, 'http://werd.io/2014/homebrew-website-club-4')

    assert result['type'] == 'event'
    assert result['name'] == 'Homebrew Website Club'
    assert 'Are you building your own website?' in result['content']
    assert result['start'].replace(tzinfo=None) == datetime(2014, 5, 7, 18, 30)
    assert result['start'].utcoffset() == timedelta(hours=0)
    assert result['end'].replace(tzinfo=None) == datetime(2014, 5, 7, 19, 30)
    assert result['end'].utcoffset() == timedelta(hours=0)


def test_reply_h_cite():
    # reply with reply-context from aaronnparecki.com
    parsed = load_test('reply_h-cite')
    result = mf2util.interpret_comment(
        parsed, 'http://aaronparecki.com/replies/2014/05/10/1/indieweb',
        ['http://datahiveconsulting.com/2014/04/10/indiewebify-me-and-the-knowledge-gap/', 'http://datahiveconsulting.com/2014/04/10'])

    assert result['type'] == 'entry'
    assert not result.get('name')
    assert "We're working on it ;-)" in result.get('content')
    assert result['published'].replace(tzinfo=None)\
        == datetime(2014, 5, 10, 14, 48, 33)
    assert result['published'].utcoffset() == timedelta(hours=-7)
    assert result['comment_type'] == ['reply']


def test_u_in_reply_to():
    # reply with simple u-in-reply-to link from snarfed.org
    parsed = load_test('reply_u-in-reply-to')
    result = mf2util.interpret_comment(
        parsed, 'https://snarfed.org/2014-03-09_re-display-likes-in-a-facepile',
        ['https://willnorris.com/2014/03/display-likes-in-a-facepile'])

    assert result['type'] == 'entry'
    assert result['name'] == 'Re: Display likes in a facepile'
    assert 'oh man, so cool!' in result.get('content')
    assert result['published'].replace(tzinfo=None)\
        == datetime(2014, 3, 9, 22, 48, 22)
    assert result['published'].utcoffset() == timedelta(hours=-7)
    assert result['comment_type'] == ['reply']


def test_reply_rsvp():
    parsed = load_test('reply_rsvp')
    result = mf2util.interpret_comment(
        parsed, 'https://snarfed.org/2014-05-05_homebrew-website-club-3',
        ['http://werd.io/2014/homebrew-website-club-4'])

    assert result['type'] == 'entry'
    assert result['name'] == 'Homebrew Website Club'
    assert '<a class="u-in-reply-to"' in result.get('content')
    assert result['published'].replace(tzinfo=None)\
        == datetime(2014, 5, 5, 10, 10, 53)
    assert result['published'].utcoffset() == timedelta(hours=-7)
    assert result['comment_type'] == ['reply']
    assert result['rsvp'] == 'yes'


def test_article_naive_datetime():
    parsed = load_test('article_naive_datetime')
    result = mf2util.interpret(
        parsed, 'http://tantek.com/2014/120/b1/markup-people-focused-mobile-communication')
    assert result['type'] == 'entry'
    assert result['name'] == 'Markup For People Focused Mobile Communication'
    assert '<h2>Action labels not app names</h2>' in result['content']
    assert result['published'] == datetime(2014, 4, 30, 12, 11)
    assert result['updated'] == datetime(2014, 4, 30, 12, 11)
