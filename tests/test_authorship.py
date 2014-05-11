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
    assert mf2util.find_author(blob) == {'name': 'John Doe'}


def test_p_author():
    assert load_test('h-entry_with_p-author') == {
        'name': 'John Doe',
        'url': 'http://example.com/johndoe/',
        'photo': 'http://www.gravatar.com/avatar/fd876f8cd6a58277fc664d47ea10ad19.jpg?s=80&d=mm'
    }


def test_no_h_card():
    assert not load_test('no_h-card')


def test_h_card_rel_me():
    testname = 'h-card_with_u-url_that_is_also_rel-me'
    assert load_test(testname) == {
        'name': 'John Doe',
        'url': '%s.html' % testname,
        'photo': 'http://www.gravatar.com/avatar/fd876f8cd6a58277fc664d47ea10ad19.jpg?s=80&d=mm'
    }


def test_h_card_self():
    testname = 'h-card_with_u-url_equal_to_u-uid_equal_to_self'
    assert load_test(testname) == {
        'name': 'John Doe',
        'url': '%s.html' % testname,
        'photo': 'http://www.gravatar.com/avatar/fd876f8cd6a58277fc664d47ea10ad19.jpg?s=80&d=mm'
    }


def test_h_card_rel_author():
    assert load_test('h-entry_with_rel-author_pointing_to_h-card_with_u-url_equal_to_u-uid_equal_to_self') == {
        'name': 'John Doe',
        'url': 'h-card_with_u-url_equal_to_u-uid_equal_to_self.html'
    }


def test_rel_author_to_rel_author():
    assert load_test('h-entry_with_rel-author_and_h-card_with_u-url_pointing_to_rel-author_href') == {
        'name': 'John Doe',
        'url': 'no_h-card.html',
        'photo': 'http://www.gravatar.com/avatar/fd876f8cd6a58277fc664d47ea10ad19.jpg?s=80&d=mm'
    }


def test_rel_author_to_rel_me():
    assert load_test('h-entry_with_rel-author_pointing_to_h-card_with_u-url_that_is_also_rel-me') == {
        'name': 'John Doe',
        'url': 'h-card_with_u-url_that_is_also_rel-me.html'
    }
