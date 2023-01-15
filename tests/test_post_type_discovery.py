"""Tests for post_type_discovery
"""

import json
import mf2util


def test_post_type_discovery():
    for test, implied_type in [
            ('interpret/hwc-event', 'event'),
            ('interpret/reply_h-cite', 'reply'),
            ('interpret/reply_u-in-reply-to', 'reply'),
            ('interpret/reply_rsvp', 'rsvp'),
            ('interpret/note_with_comment_and_like', 'note'),
            ('interpret/article_naive_datetime', 'article'),
            ('interpret/article_non_ascii_content', 'article'),
            ('interpret/follow', 'follow'),
            ('posttype/tantek_photo', 'photo'),
            ('posttype/only_html_content', 'note'),
            ('posttype/hcard_no_name', 'person'),
            ('posttype/hcard_org', 'org'),
            # TODO add more tests
    ]:
        parsed = json.load(open('tests/' + test + '.json'))
        types = (['h-card'] if implied_type in ('person', 'org')
                 else ['h-entry', 'h-event'])
        entry = mf2util.find_first_entry(parsed, types)
        assert implied_type == mf2util.post_type_discovery(entry)
