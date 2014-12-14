# Change Log
All notable changes to this project will be documented in this file.

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
