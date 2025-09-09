import unittest
import os
import shutil
from fmtool import FileManager

class TestFileManager(unittest.TestCase):
    def setUp(self):
        self.fm = FileManager('.')
        self.test_file = 'test_file.txt'
        self.test_dir = 'test_dir'
        self.test_zip = 'test.zip'

    def tearDown(self):
        for path in [self.test_file, self.test_zip, self.test_dir]:
            if self.fm.exists(path):
                self.fm.delete(path)

    def test_touch_and_write_read(self):
        self.fm.touch(self.test_file)
        self.fm.write_text(self.test_file, 'hello world!')
        content = self.fm.read_text(self.test_file)
        self.assertEqual(content, 'hello world!')

    def test_write_read_bytes(self):
        data = b'bytes content'
        self.fm.write_bytes(self.test_file, data)
        read_data = self.fm.read_bytes(self.test_file)
        self.assertEqual(read_data, data)

    def test_mkdir_and_exists(self):
        self.fm.mkdir(self.test_dir)
        self.assertTrue(self.fm.exists(self.test_dir))

    def test_rename(self):
        self.fm.touch(self.test_file)
        new_name = 'renamed.txt'
        self.fm.rename(self.test_file, new_name)
        self.assertTrue(self.fm.exists(new_name))
        self.fm.delete(new_name)

    def test_zip_and_unzip(self):
        self.fm.mkdir(self.test_dir)
        self.fm.write_text(os.path.join(self.test_dir, 'a.txt'), 'content')
        self.fm.zip_dir(self.test_dir, self.test_zip)
        self.assertTrue(self.fm.exists(self.test_zip))

        unzip_dir = 'unzipped'
        self.fm.unzip(self.test_zip, unzip_dir)
        self.assertTrue(self.fm.exists(os.path.join(unzip_dir, 'a.txt')))
        self.fm.delete(unzip_dir)

    def test_stat_and_hash(self):
        self.fm.touch(self.test_file)
        self.fm.write_text(self.test_file, 'hash me')
        info = self.fm.stat(self.test_file, human_readable=False)
        self.assertEqual(info['is_file'], True)
        file_hash = self.fm.hash_file(self.test_file, 'sha256')
        self.assertIsInstance(file_hash, str)

if __name__ == '__main__':
    unittest.main()
