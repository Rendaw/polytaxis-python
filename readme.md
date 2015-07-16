# What is `polytaxis-python`?

`polytaxis-python` is a reference python library for interacting with files with a polytaxis header.  It also provides the command line utility `ptmod` for manipulate polytaxis headers.

Requires Python 3.

# Installation

Run `pip install git+https://github.com/Rendaw/polytaxis-python`.

# Usage

## `ptmod` usage

Run `ptmod -h`.

## API reference

Note: All tags are specified in the format `{tagname: set([value or None])}`.  The `set` contains all values, and `None` for value-less tags.
Example: `author=rendaw` would be specified by `{'author': set(['rendaw'])}`.  
Example 2: `top_secret` would be specified by `{'top_secret': set([None])}`.

##### def encode_tag(key, value):

Encodes an individual tag.  `value` may be None.

##### def encode_tags(tags):

Encodes multiple tags, as in the tag block in the header. `tags` must be a dict with string keys of string/None sets.

##### def decode_tags(raw_tags, decode_one=False):

Decodes a string, as in the tag block in the header. Returns a dict of tags (see `encode_tags` for the structure).

##### def write_tags(file, tags=None, raw_tags=None, unsized=False, minimize=False):

Adds a polytaxis header to opened `file` at the current cursor location (make sure the cursor is at the beginning of the file), with the tags `tags` (or `raw_tags` if you've already encoded your tags).  

If `unsized`, writes the tags in an unsized header.  If not `unsized`, `minimize` will only allocate enough header space for the specified `tags`/`raw_tags`.

`tags` must be in the format described in `encode_tags`.

##### def get_tags(filename):

Returns a dict (see `encode_tags`) of tags in `filename` if it has a polytaxis header, otherwise `None`.

##### def strip_tags(filename):

Removes the polytaxis header from `filename`.

##### def set_tags(filename, tags, unsized=None, minimize=False):

Adds a polytaxis header if missing, or updates the polytaxis header otherwise.  See `write_tags` for an explanation of the parameters.

This can convert between unsized and sized headers if `unsized` is specified.

##### def seek_tags(file):

Seeks `file` to the beginning of the polytaxis header.

##### def seek_past_tags(file, filename='unknown'):

Seeks `file` to the end of the polytaxis header.

# Templates

[A template script to modify file tags](modify-template.py)

# Support

Ask questions and raise issues on the GitHub issue tracker.

See Contributing below for information about prioritizing issues.

# Contributing

1. Develop and submit pull requests.

2. Fund development via https://www.bountysource.com/
