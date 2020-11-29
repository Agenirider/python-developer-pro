import unittest
import sys
import os.path

path = os.path.split(os.getcwd())[0]
sys.path.insert(0, path)

from log_analyzer import gzip_unpacker, log_parser, register_reader

log_sample = [['apiv2banner25019354', 0.390], ['api1photogenic_bannerslistserver_name=WIN7RB4', 0.133],
              ['apiv2banner16852664', 0.199]]


class LogParserTest(unittest.TestCase):

    def test_gzipunpacker(self):
        arr = gzip_unpacker(None, './log_file_sample')
        self.assertEqual(type(log_sample), type(arr))

    def test_logparser(self):
        arr = gzip_unpacker(None, './log_file_sample')
        self.assertEqual(log_parser(arr), log_sample)


if __name__ == '__main__':
    unittest.main()
