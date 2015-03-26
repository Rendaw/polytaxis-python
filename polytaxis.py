import tempfile
import shutil
import os

magic = 'polytaxis00 '
size_size = 11
size_limit = 10 ** size_size
sep = '='
sep2 = '\n'
unsized_mark = '<<<<\n'

def _encode_part(text):
    return ''.join({
        u'=': u'\\=', 
        u'\n': u'\\\n', 
        u'\\': u'\\\\'
    }.get(char, char) for char in text)

def encode_tag(key, value):
    if value is None:
        return _encode_part(key)
    else:
        return u'{}={}'.format(
            _encode_part(key),
            _encode_part(value),
        )

def encode_tags(tags):
    assembled = []
    for key, vals in tags.items():
        for val in vals:
            assembled.append(encode_tag(key, val))
    assembled.append('')
    return sep2.join(assembled)

def decode_tags(raw_tags, decode_one=False):
    tags = {}

    class State(object):
        out_key = []
        out_val = None
        skip = False
        before_split = True
    s = State()

    def finish():
        key = ''.join(s.out_key)
        values = tags.get(key)
        if values is None:
            values = set()
            tags[key] = values
        values.add(
            ''.join(s.out_val) if s.out_val is not None else None
        )

    def append(char):
        if s.before_split:
            s.out_key.append(char)
        else:
            if s.out_val is None:
                s.out_val = []
            s.out_val.append(char)

    for char in raw_tags:
        if not s.skip:
            if char == '\\':
                s.skip = True
            elif s.before_split and char == '=':
                s.before_split = False
            elif not decode_one and char == sep2:
                if s.out_key:
                    finish()
                s.out_key = []
                s.out_val = None
                s.before_split = True
            else:
                append(char)
        else:
            append(char)
            s.skip = False

    return tags

def _header_end(size):
    return len(magic) + size_size + 1 + size

def _read_magic(file):
    read = file.read(len(magic))
    if read != magic:
        file.seek(0)
        return False
    return True

def _read_size(file, filename):
    pre_size = file.read(size_size)
    if len(pre_size) != size_size:
        raise ValueError(
            u'file [{}] ends before header length could be read'
            .format(
                filename
            )
        )
        return None
    if file.read(1) != sep2:
        raise ValueError(
            u'file [{}] missing post-size newline'
            .format(
                filename
            )
        )
    try:
        return int(pre_size)
    except ValueError as e:
        raise ValueError(
            u'error reading polytaxis header length in file [{}]: {}'
            .format(
                filename,
                e,
            )
        )

def _find_unsized_mark(file):
    aggregate = []
    last_buffer = ''
    while True:
        buffer = file.read(1024) or ''
        if not buffer:
            return None
        aggregate.append(buffer)
        end_offset = -(min(len(unsized_mark), len(last_buffer)) + len(buffer))
        check_buffer = last_buffer[-len(unsized_mark):] + buffer
        end = check_buffer.find(unsized_mark)
        if end != -1:
            end_offset = end_offset + end
            raw_tags = ''.join(aggregate)[:end_offset]
            file.seek(file.tell() + end_offset + len(unsized_mark))
            return raw_tags
        last_buffer = buffer

def write_tags(file, tags=None, raw_tags=None, unsized=False, minimize=False):
    if tags is None and raw_tags is None:
        raise TypeError('write_tags requires either \'tags\' or \'raw_tags\'.')
    if tags is not None:
        raw_tags = encode_tags(tags)
    new_length = (
        len(raw_tags) if minimize else _shift_bit_length(len(raw_tags))
    )
    new_end = _header_end(new_length)
    file.write(magic)
    if unsized:
        file.write(('{:0' + '{}d'.format(size_size) + '}').format(-1))
    else:
        file.write(('{:0' + '{}d'.format(size_size) + '}').format(new_length))
    file.write(sep2)
    file.write(raw_tags)
    if unsized:
        file.write(unsized_mark)
    else:
        if file.tell() < new_end:
            file.write('\0')
        file.seek(new_end)

def get_tags(filename):
    """Gets tags from a file with a tag header, or returns None."""
    with open(filename, 'rb') as file:
        if not _read_magic(file):
            return None
        size = _read_size(file, filename)
        if size == -1:
            raw_tags = _find_unsized_mark(file)
        else:
            raw_tags = file.read(size)
            if len(raw_tags) != size:
                raise ValueError(
                    u'polytaxis header in [{}] should be length {}, '
                    u'got length {}'
                    .format(
                        filename,
                        size,
                        len(raw_Tags),
                    )
                )
        tags = decode_tags(raw_tags)
        return tags

def _shift_bit_length(x):
    # http://stackoverflow.com/questions/14267555/how-can-i-find-the-smallest-power-of-2-greater-than-n-in-python  # noqa
    return max(512, 1<<(x-1).bit_length())

def _insert_tags(raw_tags, file, dest_name, unsized=False, minimize=False):
    with tempfile.NamedTemporaryFile(mode='wb', delete=False) as file2:
        file2_name = file2.name
        write_tags(
            file2, 
            unsized=unsized, 
            minimize=minimize, 
            raw_tags=raw_tags,
        )
        while True:
            buffer = file.read(1024**2)
            if not buffer:
                break
            file2.write(buffer)
    file.close()
    if file.name != dest_name and os.path.exists(dest_name):
        raise RuntimeError(
            'Cannot add tags to [{}] because destination [{}] already exists.'
            .format(
                file.name,
                dest_name,
            )
        )
    shutil.move(file2_name, dest_name)

def strip_tags(filename):
    new_filename = filename
    if filename.endswith('.p'):
        new_filename = filename[:-2]
        if os.path.exists(new_filename):
            raise RuntimeError(
                'Cannot strip [{}] because destination [{}] already exists.'
                .format(
                    filename,
                    new_filename,
                )
            )
    with open(filename, 'rb') as file:
        if not seek_past_tags(file, filename):
            raise RuntimeError(
                'Could not find end of polytaxis data. File may be corrupt.'
            )
        with tempfile.NamedTemporaryFile(mode='wb', delete=False) as file2:
            file2_name = file2.name
            while True:
                buffer = file.read(1024**2)
                if not buffer:
                    break
                file2.write(buffer)
    shutil.move(file2_name, new_filename)
    if new_filename != filename:
        os.unlink(filename)

def set_tags(filename, tags, unsized=None, minimize=False):
    """Replaces or adds a tag header to a file."""
    raw_tags = encode_tags(tags)
    if len(raw_tags) > size_limit:
        raise ValueError(
            u'encoded tags (length {}) are too long (max length {})'
            .format(
                len(raw_tags),
                size_limit,
            )
        )
    with open(filename, 'r+b') as file:
        if not _read_magic(file):
            _insert_tags(
                raw_tags, 
                file, 
                '{}.p'.format(filename), 
                unsized=unsized if unsized is not None else False,
                minimize=minimize,
            )
            os.remove(filename)
            return
        size = _read_size(file, filename)
        if size == -1:
            if not _find_unsized_mark(file):
                raise ValueError(
                    'Could not find end of tags in [{}]'.format(
                        filename
                    )
                )
            _insert_tags(
                raw_tags, 
                file, 
                filename, 
                unsized=unsized if unsized is not None else True,
                minimize=minimize,
            )
        else:
            end = _header_end(size)
            if size < len(raw_tags):
                file.seek(end)
                _insert_tags(
                    raw_tags, 
                    file, 
                    filename,
                    unsized=unsized if unsized is not None else False,
                    minimize=minimize,
                )
                return
            if unsized == True:
                file.seek(end)
                _insert_tags(
                    raw_tags, 
                    file, 
                    filename,
                    unsized=True,
                    minimize=minimize,
                )
                return
            file.write(raw_tags)
            if file.tell() < end:
                file.write('\0')

def seek_tags(file):
    """Seek a file to the start of the tag header."""
    target.seek(0)

def seek_past_tags(file, filename='unknown'):
    """Seek a file past the end of the tag header (start of non-tag data)."""
    file.seek(0)
    if not _read_magic(file):
        file.seek(0)
        return False
    size = _read_size(file, filename)
    if size == -1:
        if not _find_unsized_mark(file):
            return False
    else:
        total = _header_end(size)
        file.seek(total, 0)
        if file.tell() != total:
            return False
    return True

