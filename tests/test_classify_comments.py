import copy
import mf2util

TEST_BLOB = {
    "alternates": [
    ],
    "items": [
        {
            "properties": {
                "name": ["Author"],
                "photo": ["http://example.com/author_img.jpg"],
                "url": ["http://example.com"]
            },
            "type": ["h-card"],
            "value": "Author LastName"
        },
        {
            "properties": {
                "content": [
                    {
                        "html": "some content",
                        "value": "some content"
                    }
                ],
                "name": ["some title"],
                "published": ["2014-05-07T17:15:44+00:00"],
                "url": ["http://example.com/reply/2014/05/07/1"]
            },
            "type": [
                "h-entry"
            ]
        }
    ],
    "rels": {
    }
}


def test_no_reference():
    blob = copy.deepcopy(TEST_BLOB)
    assert mf2util.classify_comment(blob, ('http://example.com',)) == []

    # add some irrelevant references
    blob['items'][1]['in-reply-to'] = [
        "http://werd.io/2014/homebrew-website-club-4",
        "https://www.facebook.com/events/1430990723825351/"
    ]
    assert mf2util.classify_comment(blob, ('http://example.com',)) == []

    # no target url
    assert mf2util.classify_comment(blob, ()) == []


def test_rsvps():
    blob = copy.deepcopy(TEST_BLOB)

    blob['items'][1]['properties'].update({
        'in-reply-to': ['http://mydomain.com/my-post'],
        'rsvp': ['yes'],
    })

    assert mf2util.classify_comment(
        blob, ('http://mydoma.in/short', 'http://mydomain.com/my-post')) \
        == ['rsvp']


def test_likes():
    """make sure we find likes"""
    blob = copy.deepcopy(TEST_BLOB)

    # add some references
    blob['items'][1]['properties'].update({
        'in-reply-to': ['http://someoneelse.com/post'],
        'like-of': ['http://mydomain.com/my-post'],
    })

    assert mf2util.classify_comment(
        blob, ('http://mydoma.in/short', 'http://mydomain.com/my-post')) \
        == ['like']


def test_reposts():
    """make sure we find reposts"""
    blob = copy.deepcopy(TEST_BLOB)

    # add some references
    blob['items'][1]['properties'].update({
        'repost-of': ['http://mydomain.com/my-post'],
        'like-of': ['http://someoneelse.com/post'],
    })

    assert mf2util.classify_comment(
        blob, ('http://mydoma.in/short', 'http://mydomain.com/my-post')) \
        == ['repost']


def test_multireply():
    """check behavior if our post is one among several posts
    in a multireply"""
    blob = copy.deepcopy(TEST_BLOB)

    # add some references
    blob['items'][1]['properties'].update({
        'in-reply-to': [
            'http://someoneelse.com/post',
            'http://mydomain.com/my-post',
            'http://athirddomain.org/permalink',
        ],
    })

    assert mf2util.classify_comment(blob, ('http://mydomain.com/my-post')) \
        == ['reply']


def test_multimodal():
    """a mention can have more than one classification, make sure we find
    all of them. also tests some of the alternate/historical classnames"""
    blob = copy.deepcopy(TEST_BLOB)

    # add some references
    blob['items'][1]['properties'].update({
        'reply-to': ['http://noone.im/'],
        'repost-of': [
            'http://someoneelse.com',
            'http://mydomain.com/my-post',
        ],
        'like': [
            'http://mydoma.in/short',
            'http://someoneelse.com/post',
        ],
    })

    assert sorted(
        mf2util.classify_comment(
            blob, ('http://mydoma.in/short', 'http://mydomain.com/my-post')))\
        == ['like', 'repost']


def test_h_cite():
    """Test object references (e.g., class="p-in-reply-to h-cite")"""
    blob = copy.deepcopy(TEST_BLOB)

    # add some references
    blob['items'][1]['properties'].update({
        'in-reply-to': [{
            'type': 'h-cite',
            'properties': {
                'url': ['http://mydomain.com/my-post'],
            },
        }],
    })

    assert mf2util.classify_comment(blob, ('http://mydomain.com/my-post',))\
        == ['reply']
