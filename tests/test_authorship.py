"""Test the authorship discovery algorithm. Credit for test cases to
Sandeep Shetty https://github.com/sandeepshetty/authorship-test-cases
"""

import mf2util
import json


def load_test(testname):
    parsed = json.load(open('tests/authorship/%s.json' % testname))
    return mf2util.find_author(parsed, '%s.html' % testname)


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
    name, url, photo = mf2util.find_author(blob)
    assert 'John Doe' == name
    assert url is None
    assert photo is None


def test_p_author():
    name, url, photo = load_test('h-entry_with_p-author')
    assert 'John Doe' == name
    assert 'http://example.com/johndoe/' == url
    assert 'http://www.gravatar.com/avatar/fd876f8cd6a58277fc664d47ea10ad19.jpg?s=80&d=mm' == photo


def test_no_h_card():
    name, url, photo = load_test('no_h-card')
    assert name is None
    assert url is None
    assert photo is None


def test_h_card_rel_me():
    testname = 'h-card_with_u-url_that_is_also_rel-me'
    name, url, photo = load_test(testname)
    assert 'John Doe' == name
    assert '%s.html' % testname == url
    assert 'http://www.gravatar.com/avatar/fd876f8cd6a58277fc664d47ea10ad19.jpg?s=80&d=mm' == photo


def test_h_card_self():
    testname = 'h-card_with_u-url_equal_to_u-uid_equal_to_self'
    name, url, photo = load_test(testname)
    assert 'John Doe' == name
    assert '%s.html' % testname == url
    assert 'http://www.gravatar.com/avatar/fd876f8cd6a58277fc664d47ea10ad19.jpg?s=80&d=mm' == photo


def test_h_card_rel_author():
    name, url, photo = load_test('h-entry_with_rel-author_pointing_to_h-card_with_u-url_equal_to_u-uid_equal_to_self')
    assert 'John Doe' == name
    assert 'h-card_with_u-url_equal_to_u-uid_equal_to_self.html' == url
    assert None == photo


def test_rel_author_to_rel_author():
    name, url, photo = load_test('h-entry_with_rel-author_and_h-card_with_u-url_pointing_to_rel-author_href')
    assert 'John Doe' == name
    assert 'no_h-card.html' == url
    assert 'http://www.gravatar.com/avatar/fd876f8cd6a58277fc664d47ea10ad19.jpg?s=80&d=mm' == photo


def test_rel_author_to_rel_me():
    name, url, photo = load_test('h-entry_with_rel-author_pointing_to_h-card_with_u-url_that_is_also_rel-me')
    assert 'John Doe' == name
    assert 'h-card_with_u-url_that_is_also_rel-me.html' == url
    assert None == photo
