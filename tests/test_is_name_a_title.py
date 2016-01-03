import sys
import mf2util

PY3 = sys.version_info[0] >= 3


def test_is_name_a_title():
    for name, content, expected in [
            # simple
            ('this is the content', 'this is the content', False),
            ('This is a title', 'This is some content', True),
            # common case with no explicit p-name
            ('nonsensethe contentnonsense', 'the content', False),
            # ignore case, punctuation
            ('the content', 'ThE cONTeNT...', False),
            # test bytestrings
            (b'This is a title', b'This is some content', True),
    ]:
        assert expected == mf2util.is_name_a_title(name, content)
