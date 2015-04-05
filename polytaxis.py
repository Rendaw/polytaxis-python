import tempfile
import shutil
import os

magic = b'polytaxis00'
size_size = 10
size_limit = 10 ** size_size
sep = b'='
sep2 = b'\n'
unsized_mark = b'<<<<\n'

def _encode_part(text):
    return ''.join({
        '=': '\\=', 
        '\n': '\\\n', 
        '\\': '\\\\',
    }.get(char, char) for char in text).encode('utf-8')

def encode_tag(key, value):
    key = key
    value = value if value is not None else None
    if value is None:
        return _encode_part(key)
    else:
        return b'='.join((
            _encode_part(key),
            _encode_part(value),
        ))

def encode_tags(tags):
    assembled = []
    for key, vals in tags.items():
        for val in vals:
            assembled.append(encode_tag(key, val))
    assembled.append(b'')
    return sep2.join(assembled)

def decode_tags(raw_tags, decode_one=False):
    tags = {}

    class State(object):
        out_key = bytearray()
        out_val = None
        skip = False
        before_split = True
    s = State()

    def finish():
        key = s.out_key.decode('utf-8')
        values = tags.get(key)
        if values is None:
            values = set()
            tags[key] = values
        values.add(
            s.out_val.decode('utf-8') 
            if s.out_val is not None 
            else None
        )

    def append(char):
        if s.before_split:
            s.out_key.append(char)
        else:
            if s.out_val is None:
                s.out_val = bytearray()
            s.out_val.append(char)

    for char in raw_tags:
        if not s.skip:
            if bytes([char]) == b'\\':
                s.skip = True
            elif s.before_split and bytes([char]) == b'=':
                s.before_split = False
            elif not decode_one and bytes([char]) == sep2:
                if s.out_key:
                    finish()
                s.out_key = bytearray()
                s.out_val = None
                s.before_split = True
            else:
                append(char)
        else:
            append(char)
            s.skip = False

    if decode_one and s.out_key:
        finish()

    return tags

def decode_tag(raw_tag):
    key, values = next(iter(decode_tags(raw_tag, True).items()), None)
    return (key, next(iter(values)))

def _sized_header_end(size):
    return len(magic) + 1 + size_size + 1 + size

def _read_magic(file):
    read = file.read(len(magic))
    if read != magic:
        file.seek(0)
        return False
    return True

def _read_size(file):
    size_type = file.read(1)
    if len(size_type) != 1:
        raise ValueError(
            'Missing size differentiator in file [{}]'.format(
                file.name,
            )
        )
    if size_type == b'u':
        size = -1
    else:
        pre_size = file.read(size_size)
        if len(pre_size) != size_size:
            raise ValueError(
                'file [{}] ends before header length could be read'
                .format(
                    file.name
                )
            )
            return None
        try:
            size = int(pre_size)
        except ValueError as e:
            raise ValueError(
                'error reading polytaxis header length in file [{}]: {}'
                .format(
                    file.name,
                    e,
                )
            )
    if file.read(1) != sep2:
        raise ValueError(
            'file [{}] missing post-size newline'
            .format(
                file.name
            )
        )
    return size

def _find_unsized_mark(file):
    aggregate = []
    last_buffer = b''
    while True:
        buffer = file.read(1024) or b''
        if not buffer:
            return None
        aggregate.append(buffer)
        check_buffer = last_buffer + buffer
        end_offset = -len(check_buffer)
        end = check_buffer.find(unsized_mark)
        if end != -1:
            end_offset = end_offset + end
            raw_tags = b''.join(aggregate)[:end_offset]
            file.seek(file.tell() + end_offset + len(unsized_mark))
            return raw_tags
        last_buffer = buffer

def write_tags(file, tags=None, raw_tags=None, unsized=False, minimize=False):
    if tags is None and raw_tags is None:
        raise TypeError('write_tags requires either \'tags\' or \'raw_tags\'.')
    file.write(magic)
    if tags is not None:
        raw_tags = encode_tags(tags)
    if unsized:
        file.write(b'u')
        file.write(sep2)
        file.write(raw_tags)
        file.write(unsized_mark)
    else:
        file.write(b' ')
        new_length = (
            len(raw_tags) if minimize else _shift_bit_length(len(raw_tags))
        )
        new_end = _sized_header_end(new_length)
        file.write(('%0*d' % (size_size, new_length)).encode())
        file.write(sep2)
        file.write(raw_tags)
        if file.tell() < new_end:
            file.write(b'\0')
        if file.tell() < new_end:
            file.seek(new_end - 1)
            file.write(b'\n')

def get_tags(filename):
    """Gets tags from a file with a tag header, or returns None."""
    with open(filename, 'rb') as file:
        if not _read_magic(file):
            return None
        size = _read_size(file)
        if size == -1:
            raw_tags = _find_unsized_mark(file)
            if raw_tags is None:
                raise ValueError(
                    'Could not find end of tags in [{}]'.format(
                        filename
                    )
                )
        else:
            raw_tags = file.read(size)
            if len(raw_tags) != size:
                raise ValueError(
                    'polytaxis header in [{}] should be length {}, '
                    'got length {}'
                    .format(
                        filename,
                        size,
                        len(raw_tags),
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
        if not seek_past_tags(file):
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
            'encoded tags (length {}) are too long (max length {})'
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
        size = _read_size(file)
        if size == -1:
            if _find_unsized_mark(file) is None:
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
            end = _sized_header_end(size)
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
                file.write(b'\0')

def seek_tags(file):
    """Seek a file to the start of the tag header."""
    target.seek(0)

def seek_past_tags(file):
    """Seek a file past the end of the tag header (start of non-tag data)."""
    file.seek(0)
    if not _read_magic(file):
        file.seek(0)
        return False
    size = _read_size(file)
    if size == -1:
        if _find_unsized_mark(file) is None:
            return False
    else:
        total = _sized_header_end(size)
        file.seek(total, 0)
        if file.tell() != total:
            return False
    return True

class UnwrappedFile(object):
    def __init__(self, filename, mode):
        if mode in ['ab']:
            self.f = open(filename, mode)
            return
        if mode == 'wb':
            mode = 'rb+'
        elif mode in ('rb'):
            pass
        else:
            raise ValueError('Unsupported mode {}'.format(mode))
        self.f = open(filename, mode)
        seek_past_tags(self.f)
        self.offset = self.f.tell()
    
    def __getattr__(self, name):
        return getattr(self.f, name)

    def fileno(self):
        raise NotImplementedError(
            'For safety reasons file descriptor access is disabled.',
        )

    def seek(self, offset, whence=os.SEEK_SET):
        if whence == os.SEEK_SET:
            if offset < 0:
                offset = 0
            self.f.seek(offset + self.offset, whence)
        elif whence == os.SEEK_CUR:
            self.f.seek(
                max(0, self.f.tell() - self.offset + offset) + self.offset,
                whence,
            )
        elif whence == os.SEEK_END:
            raise NotImplementedError(
                'Unwrapped files can\'t seek from end currently.'
            )

    def tell(self):
        return self.f.tell() - self.offset

    def truncate(self, size=0):
        self.f.truncate(max(0, size + self.offset))

class open_unwrap:
    def __init__(self, filename, mode):
        self.f = UnwrappedFile(filename, mode)
   
    def __getattr__(self, name):
        return getattr(self.f, name)

    def __enter__(self):
        return self.f

    def __exit__(self, type, value, traceback):
        self.f.close()
