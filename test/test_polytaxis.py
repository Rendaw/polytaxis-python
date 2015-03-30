import unittest
import io
import os
import collections

import polytaxis

normal_tags = {'a': set(['a'])}

raw_unsized_empty = (
    b'polytaxis00u\n'
    b'<<<<\n'
    b'wug'
)
 
raw_unsized_normal = (
    b'polytaxis00u\n'
    b'a=a\n'
    b'<<<<\n'
    b'wug'
)

raw_sized_empty = (
    b'polytaxis00 0000000000\n'
    b'wug'
)
     
raw_sized_normal = (
    b'polytaxis00 0000000004\n'
    b'a=a\n'
    b'wug'
)

def open2w(filename, text):
    with open(filename, 'wb') as file:
        file.write(text)

def open2r(filename):
    with open(filename, 'rb') as file:
        return file.read()

def res(filename):
    return os.path.join(os.path.dirname(__file__), filename)

class TestPolytaxis(unittest.TestCase):
    def test_encode_decode_tags(self):
        begin = collections.OrderedDict((
            ('a', set(['a'])),
            ('b', ['b1', 'b2']),
            ('c', set([None])),
            ('d\nd=d\\', set(['d\nd=d\\'])),
        ))
        temp = polytaxis.encode_tags(begin)

        self.assertEqual(
            temp,
            b'a=a\n'
            b'b=b1\n'
            b'b=b2\n'
            b'c\n'
            b'd\\\n'
            b'd\\=d\\\\=d\\\n'
            b'd\\=d\\\\\n'
        )

        end = polytaxis.decode_tags(temp)
        end['b'] = sorted(list(end['b']))
        self.assertEqual(begin, end)

    def test_write_unsized_empty(self):
        with io.BytesIO() as file:
            polytaxis.write_tags(file, unsized=True, minimize=True, tags={})
            file.write(b'wug')
            file.seek(0)
            self.assertEqual(file.read(), raw_unsized_empty)

    def test_write_unsized_normal(self):
        with io.BytesIO() as file:
            polytaxis.write_tags(
                file, 
                unsized=True, 
                minimize=True,
                tags=normal_tags,
            )
            file.write(b'wug')
            file.seek(0)
            self.assertEqual(file.read(), raw_unsized_normal)
    
    def test_write_sized_empty(self):
        with io.BytesIO() as file:
            polytaxis.write_tags(
                file, 
                minimize=True,
                tags={}
            )
            file.write(b'wug')
            file.seek(0)
            self.assertEqual(file.read(), raw_sized_empty)

    def test_write_sized_normal(self):
        with io.BytesIO() as file:
            polytaxis.write_tags(
                file, 
                minimize=True,
                tags=normal_tags,
            )
            file.write(b'wug')
            file.seek(0)
            self.assertEqual(file.read(), raw_sized_normal)

    def test_get_missing(self):
        self.assertEqual(
            polytaxis.get_tags(res('missing.txt')),
            None,
        )

    def test_get_unsized_empty(self):
        self.assertEqual(
            polytaxis.get_tags(res('unsized-empty.txt')),
            {},
        )

    def test_get_unsized_normal(self):
        self.assertEqual(
            polytaxis.get_tags(res('unsized-1.txt')),
            {'a': set(['a'])},
        )

    def test_get_sized_empty(self):
        self.assertEqual(
            polytaxis.get_tags(res('sized-empty.txt')),
            {},
        )

    def test_get_sized_normal(self):
        self.assertEqual(
            polytaxis.get_tags(res('sized-1.txt')),
            {'a': set(['a'])},
        )
    
    def test_seek_missing(self):
        with open(res('missing.txt'), 'rb') as file:
            polytaxis.seek_past_tags(file)
            self.assertEqual(file.read(), b'wug')

    def test_seek_unsized_empty(self):
        with open(res('unsized-empty.txt'), 'rb') as file:
            polytaxis.seek_past_tags(file)
            self.assertEqual(file.read(), b'wug')

    def test_seek_unsized_normal(self):
        with open(res('unsized-1.txt'), 'rb') as file:
            polytaxis.seek_past_tags(file)
            self.assertEqual(file.read(), b'wug')

    def test_seek_sized_empty(self):
        with open(res('sized-empty.txt'), 'rb') as file:
            polytaxis.seek_past_tags(file)
            self.assertEqual(file.read(), b'wug')

    def test_seek_sized_normal(self):
        with open(res('sized-1.txt'), 'rb') as file:
            polytaxis.seek_past_tags(file)
            self.assertEqual(file.read(), b'wug')

class TestPolytaxisFiles(unittest.TestCase):
    def setUp(self):
        with open(res('seed.txt'), 'wb') as file:
            file.write(b'wug')

    def tearDown(self):
        try:
            os.unlink(res('seed.txt'))
        except:
            pass
        try:
            os.unlink(res('seed.txt.p'))
        except:
            pass

    def test_set_unsized_new(self):
        polytaxis.set_tags(
            res('seed.txt'), 
            unsized=True, 
            tags=normal_tags,
        )
        self.assertEqual(
            open2r(res('seed.txt.p')), 
            raw_unsized_normal,
        )

    def test_set_unsized_existing(self):
        tags2 = {'b': set(['b'])}
        polytaxis.set_tags(
            res('seed.txt'), 
            unsized=True, 
            tags=tags2,
        )
        polytaxis.set_tags(
            res('seed.txt.p'), 
            unsized=True, 
            tags=normal_tags,
        )
        self.assertEqual(
            open2r(res('seed.txt.p')), 
            raw_unsized_normal,
        )

    def test_set_sized_new(self):
        polytaxis.set_tags(
            res('seed.txt'), 
            minimize=True,
            tags=normal_tags,
        )
        self.assertEqual(
            open2r(res('seed.txt.p')),
            raw_sized_normal,
        )

    def test_set_sized_existing(self):
        tags2 = {'b': set(['b'])}
        polytaxis.set_tags(
            res('seed.txt'), 
            minimize=True,
            tags=tags2,
        )
        polytaxis.set_tags(
            res('seed.txt.p'), 
            minimize=True,
            tags=normal_tags,
        )
        self.assertEqual(
            open2r(res('seed.txt.p')), 
            raw_sized_normal,
        )

    def test_convert_unsized_to_sized(self):
        polytaxis.set_tags(
            res('seed.txt'), 
            unsized=True, 
            minimize=True,
            tags=normal_tags,
        )
        polytaxis.set_tags(
            res('seed.txt.p'), 
            minimize=True,
            unsized=False,
            tags=normal_tags,
        )
        self.assertEqual(
            open2r(res('seed.txt.p')), 
            raw_sized_normal,
        )

    def test_convert_sized_to_unsized(self):
        polytaxis.set_tags(
            res('seed.txt'), 
            minimize=True,
            tags=normal_tags,
        )
        polytaxis.set_tags(
            res('seed.txt.p'), 
            unsized=True, 
            minimize=True,
            tags=normal_tags,
        )
        self.assertEqual(
            open2r(res('seed.txt.p')),
            raw_unsized_normal,
        )
    
    def test_strip_unsized(self):
        polytaxis.set_tags(
            res('seed.txt'), 
            unsized=True, 
            minimize=True,
            tags=normal_tags,
        )
        self.assertTrue(not os.path.exists(res('seed.txt')))
        polytaxis.strip_tags(
            res('seed.txt.p'),
        )
        self.assertTrue(not os.path.exists(res('seed.txt.p')))
        self.assertEqual(
            open2r(res('seed.txt')),
            b'wug',
        )
    
    def test_strip_sized(self):
        polytaxis.set_tags(
            res('seed.txt'), 
            minimize=True,
            tags=normal_tags,
        )
        self.assertTrue(not os.path.exists(res('seed.txt')))
        polytaxis.strip_tags(
            res('seed.txt.p'),
        )
        self.assertTrue(not os.path.exists(res('seed.txt.p')))
        self.assertEqual(
            open2r(res('seed.txt')),
            b'wug',
        )

    def test_overwrite_safety_new(self):
        open2w(res('seed.txt.p'), b'wug')
        with self.assertRaises(RuntimeError):
            polytaxis.set_tags(res('seed.txt'), tags={})
    
    def test_overwrite_safety_strip(self):
        polytaxis.set_tags(res('seed.txt'), tags={})
        open2w(res('seed.txt'), b'wug')
        with self.assertRaises(RuntimeError):
            polytaxis.strip_tags(res('seed.txt.p'))

class TestPolytaxisFilesInternal(unittest.TestCase):
    def setUp(self):
        open2w(res('seed.txt'), b'wug')

    def tearDown(self):
        try:
            os.unlink(res('seed.txt'))
        except:
            pass
        try:
            os.unlink(res('seed.txt.p'))
        except:
            pass
    
    def test_set_sized_existing_expand(self):
        tags2 = {}
        polytaxis.set_tags(
            res('seed.txt'), 
            minimize=True,
            tags=tags2,
        )
        polytaxis.set_tags(
            res('seed.txt.p'), 
            minimize=True,
            tags=normal_tags,
        )
        self.assertEqual(
            open2r(res('seed.txt.p')),
            raw_sized_normal,
        )

class TestRealLife(unittest.TestCase):
    def test_broken1(self):
        with open(res('broken1.txt.p'), 'rb') as file:
            polytaxis.seek_past_tags(file)
