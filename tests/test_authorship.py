"""Test the authorship discovery algorithm. Credit for test cases to
Sandeep Shetty https://github.com/sandeepshetty/authorship-test-cases
"""

from __future__ import print_function
import mf2util
import mf2py


def load_test(testname, hentry_func=None):
    def fetch_mf2(url):
        testname = url
        prefix = 'http://example.com/'
        if testname.startswith(prefix):
            testname = testname[len(prefix):]

        with open('tests/authorship/' + testname) as f:
            return mf2py.parse(url=url, doc=f.read())

    url = 'http://example.com/' + testname
    parsed = fetch_mf2(url)
    hentry = hentry_func and hentry_func(parsed)

    return mf2util.find_author(
        parsed, url, hentry=hentry, fetch_mf2_func=fetch_mf2)


def test_p_author_string():
    blob = {
        'items': [
            {
                'type': ['h-entry'],
                'properties': {
                    'author': ['John Doe']
                }
            }
        ]
    }
    assert mf2util.find_author(blob) == {'name': 'John Doe'}


def test_h_entry_with_p_author_h_card():
    assert load_test('h-entry_with_p-author_h-card.html') == {
        'name': 'John Doe',
        'url': 'http://example.com/johndoe/',
        'photo': 'http://www.gravatar.com/avatar/fd876f8cd6a58277fc664d47ea10ad19.jpg?s=80&d=mm'
    }


def test_h_entry_with_rel_author():
    assert load_test('h-entry_with_rel-author.html') == {
        'name': 'John Doe',
        'url': 'http://example.com/h-card_with_u-url_that_is_also_rel-me.html',
        'photo': 'http://www.gravatar.com/avatar/fd876f8cd6a58277fc664d47ea10ad19.jpg?s=80&d=mm',
    }


def test_h_entry_with_u_author():
    assert load_test('h-entry_with_u-author.html') == {
        'name': 'John Doe',
        'url': 'http://example.com/h-card_with_u-url_equal_to_self.html',
        'photo': 'http://www.gravatar.com/avatar/fd876f8cd6a58277fc664d47ea10ad19.jpg?s=80&d=mm'
    }


def test_h_feed_with_p_author_h_card():
    def select_h_entry(parsed):
        hfeed = parsed['items'][0]
        assert hfeed['type'] == ['h-feed']
        assert len(hfeed['children']) == 3
        return hfeed['children'][1]

    assert load_test('h-feed_with_p-author_h-card.html', select_h_entry) == {
        'name': 'John Doe',
        'url': 'http://example.com/johndoe/',
        'photo': 'http://www.gravatar.com/avatar/fd876f8cd6a58277fc664d47ea10ad19.jpg?s=80&d=mm'
    }


def test_h_feed_with_u_author():
    def select_h_entry(parsed):
        hfeed = parsed['items'][0]
        assert hfeed['type'] == ['h-feed']
        assert len(hfeed['children']) == 3
        return hfeed['children'][2]

    assert load_test('h-feed_with_u-author.html', select_h_entry) == {
        'name': 'John Doe',
        'url': 'http://example.com/h-card_with_u-url_equal_to_u-uid_equal_to_self.html',
        'photo': 'http://www.gravatar.com/avatar/fd876f8cd6a58277fc664d47ea10ad19.jpg?s=80&d=mm'
    }
