# Change Log
All notable changes to this project will be documented in this file.

## 0.2.1 - 2015-08-27
### Added
- parse simple location name and url from events and entries
### Changed
- accept complex-valued "url" properties and fallback to their "value"

## 0.2.0 - 2015-06-08
### Added
- parse nested h-cite comments as entries under the top-level entry
- check for bookmark-of
### Changed
- in-reply-to, repost-of, like-of all parse into a list of objects now
  instead of a list of urls

## 0.1.9 - 2015-04-01
### Added
- Parse event invitations as type ['invite', 'reply'].
- Parse the list of invitees.

## 0.1.5 - 2015-02-18
### Added
- in-reply-to, like-of, and repost-of properties added to the
  interpret_entry result.

## 0.1.4 - 2015-01-27
### Changed
- Authorship algorithm was incorrectly using the first h-entry on a page,
  even when parsing an h-feed that has many.

## 0.1.3 - 2014-12-14
### Changed
- RSVP replies are now classified as type 'rsvp' instead of 'reply'

## 0.1.2 - 2014-09-20
### Added
- Utility methods for interpreting h-feeds that contain one or more
  entries.

### Changed
- Handle parsing errors more gracefully.
- Distinguish between explicit h-entry titles and auto-generated
  p-names (junk) when determining whether a post has a title

## 0.1.1 - 2014-06-21
### Added
- Include "syndication" attribute for including syndication URLs
  (e.g. for de-duplicating received comments)
- Convert URL attributes from relative paths to absolute URLs for
  displaying foreign content.

## 0.1.0 - 2014-05-11
### Added
- Migrated code from Red Wind for reasoning about raw microformats2
  data into this library.
- Methods for interpreting h-entry, h-event, and received comments (to
  decide whether they are replies, likes, reposts, etc.)
- No-dependency method for parsing datetimes described in
  http://microformats.org/wiki/value-class-pattern#Date_and_time_parsing
