"""Test the interpret module, the unification of the other utility methods.
Uses test cases from around the indieweb.
"""
from __future__ import unicode_literals
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
    assert result['in-reply-to'] == [{
        'type': 'cite',
        'author': {
            'name': 'Lynne Baer',
            'photo': 'http://aaronparecki.com/images/nouns/user.svg',
            'url': 'http://datahiveconsulting.com/author/lynne/',
        },
        'content': "Last week, a friend asked me what I thought of IndieWebify.Me, a movement intended to allow people to publish on the web without relying on the tools and storage of the giant corporations that currently control the majority of the social web. I\u2019m the kind of person who gladly supports her local independent bookstores and farmers\u2019 markets and food purveyors, links to IndieBound.org instead of Amazon to buy books, and admires the ideals of Open Source Software. So, I\u2019m biased towards an ...",
        'content-plain': "Last week, a friend asked me what I thought of IndieWebify.Me, a movement intended to allow people to publish on the web without relying on the tools and storage of the giant corporations that currently control the majority of the social web. I\u2019m the kind of person who gladly supports her local independent bookstores and farmers\u2019 markets and food purveyors, links to IndieBound.org instead of Amazon to buy books, and admires the ideals of Open Source Software. So, I\u2019m biased towards an ...",
        'url': 'http://datahiveconsulting.com/2014/04/10/indiewebify-me-and-the-knowledge-gap/',
        'syndication': [],
    }]
    assert result['syndication'] == ['https://twitter.com/aaronpk/status/465247041078034432']


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
    assert result['in-reply-to'] == [{'url': 'https://willnorris.com/2014/03/display-likes-in-a-facepile'}]
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
    assert result['comment_type'] == ['rsvp', 'reply']
    assert result['rsvp'] == 'yes'


def test_reply_invite():
    parsed = load_test('reply_invite')
    result = mf2util.interpret_comment(
        parsed, 'https://www.facebook.com/1565113317092307#10155109753190015',
        ['https://kylewm.com/2015/03/homebrew-website-club-2015-march-25'])
    assert result['name'] == 'invited'
    assert result['comment_type'] == ['invite', 'reply']
    assert result['invitees'] == [{
        'name': 'Silona Bonewald',
        'url': 'https://www.facebook.com/10155109753190015',
        'photo': 'https://graph.facebook.com/v2.2/10155109753190015/picture?type=large',
    }]


def test_comment_and_like():
    parsed = load_test('note_with_comment_and_like')
    result = mf2util.interpret(
        parsed, 'https://kylewm.com/2015/10/big-thing-missing-from-my-indieweb-experience-is')
    assert result['type'] == 'entry'

    assert len(result['comment']) == 1

    assert result['comment'][0]['type'] == 'cite'
    assert result['comment'][0]['author'] == {
        'name': 'Aaron Parecki',
        'photo': 'https://twitter.com/aaronpk/profile_image?size=original',
        'url': 'http://aaronparecki.com',
    }
    assert result['comment'][0]['content'] == '<a href=\"https://twitter.com/kylewmahan\">@kylewmahan</a> I usually click through a couple levels up looking to see if any of the URLs up the chain show comments <a href=\"https://twitter.com/search?q=%23indieweb\">#indieweb</a>'

    assert len(result['like']) == 1
    assert result['like'][0]['type'] == 'cite'
    assert result['like'][0]['author'] == {
        'name': '',
        'url': 'https://twitter.com/benwerd',
        'photo': 'https://kylewm.com/imageproxy?url=https%3A%2F%2Ftwitter.com%2Fbenwerd%2Fprofile_image%3Fsize%3Doriginal&size=48&sig=fde7ce5635f5ea132a2545ff5c7d3d33',
    }


def test_article_naive_datetime():
    parsed = load_test('article_naive_datetime')
    result = mf2util.interpret(
        parsed, 'http://tantek.com/2014/120/b1/markup-people-focused-mobile-communication')
    assert result['type'] == 'entry'
    assert result['name'] == 'Markup For People Focused Mobile Communication'
    assert '<h2>Action labels not app names</h2>' in result['content']
    assert result['published'] == datetime(2014, 4, 30, 12, 11)
    assert result['updated'] == datetime(2014, 4, 30, 12, 11)


def test_article_two_published_dates():
    """Test for a case that was throwing exceptions. Could not interpret
    datetime on posts with two dt-published dates because I was
    concatenating them. Should just take the first instead.
    """
    parsed = load_test('article_two_published_dates')
    result = mf2util.interpret(
        parsed, 'article.html')
    assert result['type'] == 'entry'
    assert result['name'] == 'Test Article with Two Published Dates'
    assert result['published'].replace(tzinfo=None) == datetime(2014, 4, 30, 12, 11, 00)
    assert result['published'].utcoffset() == timedelta(hours=-8)


def test_convert_relative_paths():
    parsed = load_test('relative_paths')
    result = mf2util.interpret(
        parsed, 'http://example.com/blog/', base_href='../')
    assert result['content'] == 'This is an <img alt="alt text" title="the title" src="http://example.com/static/img.jpg"/> example document with <a href="http://example.com/relative_paths.html">relative paths</a>.'


def test_no_p_name():
    parsed = load_test('article_no_p-name')
    result = mf2util.interpret(
        parsed, 'http://example.com')
    assert 'Give me crayons and I will draw a rocketship.' in result['content']
    assert 'name' not in result


def test_p_content():
    """make sure p-content (instead of the usual e-content) doesn't cause
    us to throw an exception
    """
    parsed = {"items": [{"properties": {"author": [{"properties": {"name": ["Kyle"],
                                                                   "url": ["https://kylewm.com"]},
                                                    "type": ["h-card"], "value": "Kyle"}],
                                        "content": ["Thanks for hosting!"],
                                        "in-reply-to": ["https://snarfed.org/2014-06-16_homebrew-website-club-at-quip"],
                                        "name": ["I'm attending\n Homebrew Website Club at Quip\n Thanks for hosting!\n Kyle"],
                                        "rsvp": ["yes"]},
                         "type": ["h-entry"]}],
              "rel-urls": {}, "rels": {}}
    result = mf2util.interpret(parsed, 'http://kylewm.com/test/rsvp.html')
    assert 'Thanks for hosting!' == result.get('content')
