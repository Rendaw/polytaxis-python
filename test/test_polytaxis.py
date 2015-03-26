import unittest
import cStringIO
import os

import polytaxis

normal_tags = {'a': set(['a'])}

raw_unsized_empty = (
    'polytaxis00 -0000000001\n'
    '<<<<\n'
    'wug'
)
 
raw_unsized_normal = (
    'polytaxis00 -0000000001\n'
    'a=a\n'
    '<<<<\n'
    'wug'
)

raw_sized_empty = (
    'polytaxis00 00000000000\n'
    'wug'
)
     
raw_sized_normal = (
    'polytaxis00 00000000004\n'
    'a=a\n'
    'wug'
)

def res(filename):
    return os.path.join(os.path.dirname(__file__), filename)

class TestPolytaxis(unittest.TestCase):
    def test_encode_decode_tags(self):
        begin = {
            'a': set(['a']),
            'b': set(['b1', 'b2']),
            'c': set([None]),
            'd\nd=d\\': set(['d\nd=d\\']),
        }
        temp = polytaxis.encode_tags(begin)
        end = polytaxis.decode_tags(temp)

        self.assertEqual(
            temp,
            'a=a\n'
            'd\\\n'
            'd\\=d\\\\=d\\\n'
            'd\\=d\\\\\n'
            'c\n'
            'b=b1\n'
            'b=b2\n'
        )
        self.assertEqual(begin, end)

    def test_write_unsized_empty(self):
        file = cStringIO.StringIO()
        polytaxis.write_tags(file, unsized=True, minimize=True, tags={})
        file.write('wug')
        file.seek(0)
        self.assertEqual(file.read(), raw_unsized_empty)

    def test_write_unsized_normal(self):
        file = cStringIO.StringIO()
        polytaxis.write_tags(
            file, 
            unsized=True, 
            minimize=True,
            tags=normal_tags,
        )
        file.write('wug')
        file.seek(0)
        self.assertEqual(file.read(), raw_unsized_normal)
    
    def test_write_sized_empty(self):
        file = cStringIO.StringIO()
        polytaxis.write_tags(
            file, 
            minimize=True,
            tags={}
        )
        file.write('wug')
        file.seek(0)
        self.assertEqual(file.read(), raw_sized_empty)

    def test_write_sized_normal(self):
        file = cStringIO.StringIO()
        polytaxis.write_tags(
            file, 
            minimize=True,
            tags=normal_tags,
        )
        file.write('wug')
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
            self.assertEqual(file.read(), 'wug')

    def test_seek_unsized_empty(self):
        with open(res('unsized-empty.txt'), 'rb') as file:
            polytaxis.seek_past_tags(file)
            self.assertEqual(file.read(), 'wug')

    def test_seek_unsized_normal(self):
        with open(res('unsized-1.txt'), 'rb') as file:
            polytaxis.seek_past_tags(file)
            self.assertEqual(file.read(), 'wug')

    def test_seek_sized_empty(self):
        with open(res('sized-empty.txt'), 'rb') as file:
            polytaxis.seek_past_tags(file)
            self.assertEqual(file.read(), 'wug')

    def test_seek_sized_normal(self):
        with open(res('sized-1.txt'), 'rb') as file:
            polytaxis.seek_past_tags(file)
            self.assertEqual(file.read(), 'wug')

class TestPolytaxisFiles(unittest.TestCase):
    def setUp(self):
        open(res('seed.txt'), 'wb').write('wug')

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
            open(res('seed.txt.p'), 'rb').read(), 
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
            open(res('seed.txt.p'), 'rb').read(), 
            raw_unsized_normal,
        )

    def test_set_sized_new(self):
        polytaxis.set_tags(
            res('seed.txt'), 
            minimize=True,
            tags=normal_tags,
        )
        self.assertEqual(
            open(res('seed.txt.p'), 'rb').read(), 
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
            open(res('seed.txt.p'), 'rb').read(), 
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
            open(res('seed.txt.p'), 'rb').read(), 
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
            open(res('seed.txt.p'), 'rb').read(), 
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
            open(res('seed.txt'), 'rb').read(), 
            'wug',
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
            open(res('seed.txt'), 'rb').read(), 
            'wug',
        )

    def test_overwrite_safety_new(self):
        open(res('seed.txt.p'), 'wb').write('wug')
        with self.assertRaises(RuntimeError):
            polytaxis.set_tags(res('seed.txt'), tags={})
    
    def test_overwrite_safety_strip(self):
        polytaxis.set_tags(res('seed.txt'), tags={})
        open(res('seed.txt'), 'wb').write('wug')
        with self.assertRaises(RuntimeError):
            polytaxis.strip_tags(res('seed.txt.p'))

class TestPolytaxisFilesInternal(unittest.TestCase):
    def setUp(self):
        open(res('seed.txt'), 'wb').write('wug')

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
            open(res('seed.txt.p'), 'rb').read(), 
            raw_sized_normal,
        )
