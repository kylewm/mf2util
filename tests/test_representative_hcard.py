"""Test representative h-card parsing
"""

import mf2util


def test_url_matches_uid():
    p = {
        'rels': {},
        'items': [
            {
                'type': ['h-card'],
                'properties': {
                    'url': ['http://foo.com/bar', 'http://tilde.club/~foobar'],
                    'name': ['Bad'],
                }
            }, {
                'type': ['h-card'],
                'properties': {
                    'url': ['http://foo.com/bar', 'http://tilde.club/~foobar'],
                    'uid': ['http://foo.com/bar'],
                    'name': ['Good'],
                }
            },
        ]
    }
    hcard = mf2util.representative_hcard(p, 'http://foo.com/bar')
    assert hcard
    assert hcard['properties']['name'][0] == 'Good'

    # removing the uid should prevent us from finding the h-card
    del p['items'][1]['properties']['uid']
    hcard = mf2util.representative_hcard(p, 'http://foo.com/bar')
    assert not hcard


def test_nested_hcard():
    p = {
        'rels': {},
        'items': [
            {
                'type': ['h-card'],
                'properties': {
                    'url': ['http://foo.com/bar', 'http://tilde.club/~foobar'],
                    'name': ['Bad'],
                }
            }, {
                'type': ['h-entry'],
                'children': [
                    {
                        'type': ['h-card'],
                        'properties': {
                            'url': ['http://foo.com/bar', 'http://tilde.club/~foobar'],
                            'uid': ['http://foo.com/bar'],
                            'name': ['Good'],
                        }
                    },
                ]
            },
        ]
    }
    hcard = mf2util.representative_hcard(p, 'http://foo.com/bar')
    assert hcard
    assert hcard['properties']['name'][0] == 'Good'


def test_url_matches_rel_me():
    # rel-me points to identity hosted on about.me
    p = {
        'rels': {
            'me': ['http://about.me/foobar'],
        },
        'items': [
            {
                'type': ['h-card'],
                'properties': {
                    'url': ['http://tilde.club/~foobar'],
                    'name': ['Bad'],
                }
            }, {
                'type': ['h-card'],
                'properties': {
                    'url': ['http://about.me/foobar', 'http://tilde.club/~foobar'],
                    'name': ['Good'],
                }
            },
        ]
    }
    hcard = mf2util.representative_hcard(p, 'http://foo.com/bar')
    assert hcard
    assert hcard['properties']['name'][0] == 'Good'


def test_one_matching_url():
    p = {
        'rels': {},
        'items': [
            {
                'type': ['h-card'],
                'properties': {
                    'url': ['http://tilde.club/~foobar'],
                    'name': ['Bad'],
                }
            }, {
                'type': ['h-card'],
                'properties': {
                    'url': ['http://foo.com/bar', 'http://tilde.club/~foobar'],
                    'name': ['Good'],
                }
            },
        ]
    }
    hcard = mf2util.representative_hcard(p, 'http://foo.com/bar')
    assert hcard
    assert hcard['properties']['name'][0] == 'Good'

    p['items'].append({
        'type': ['h-card'],
        'properties': {
            'url': ['http://foo.com/bar', 'http://flickr.com/photos/foobar'],
            'name': ['Too Many Cooks'],
        }
    })
    hcard = mf2util.representative_hcard(p, 'http://foo.com/bar')
    assert not hcard
