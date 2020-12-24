import unittest
import sys
import os.path
import logging

path = os.path.split(os.getcwd())
sys.path.insert(0, path)

from log_analyzer import log_parser, log_performer

log_sample = [ ['apiv2banner25019354', 0.390], 
            ['api1photogenic_bannerslistserver_name=WIN7RB4', 0.133],
            ['apiv2banner16852664', 0.199]
             ]

bad_log_sample = [  ['apiv2banner25019354' ], 
                ['api1photogenic_bannerslistserver_name=WIN7RB4', 'aaa'],
                ['apiv2banner16852664', 0.199]
                ]

raw_ok_log_sample = ['1.196.116.32 -  - [29Jun2017035022 +0300] GET apiv2banner25019354 HTTP1.1 200 927 - Lynx2.8.8dev.9 libwww-FM2.14 SSL-MM1.4.1 GNUTLS2.10.5 - 1498697422-2190034393-4708-9752759 dc7161be3 0.390',
                  '1.99.174.176 3b81f63526fa8  - [29Jun2017035022 +0300] GET api1photogenic_bannerslistserver_name=WIN7RB4 HTTP1.1 200 12 - Python-urllib2.7 - 1498697422-32900793-4708-9752770 - 0.133',
                  '1.169.137.128 -  - [29Jun2017035022 +0300] GET apiv2banner16852664 HTTP1.1 200 19415 - Slotovod - 1498697422-2118016444-4708-9752769 712e90144abee9 0.199']

raw_fail_log_sample = ['1.196.116.32 -  - [29Jun2017035022 +0300] GET HTTP1.1 200 927 - Lynx2.8.8dev.9 libwww-FM2.14 SSL-MM1.4.1 GNUTLS2.10.5 - 1498697422-2190034393-4708-9752759 dc7161be3 0.390',
                       '1.99.174.176 3b81f63526fa8  - [29Jun2017035022 +0300] GET api1photogenic_bannerslistserver_name=WIN7RB4 HTTP1.1 200 12 - Python-urllib2.7 - 1498697422-32900793-4708-9752770']



                  
class TestSuite(unittest.TestCase):
    def setUp(self):
        self.parsed_urls = []
        self.result = []
        self.arg_config = ['--config']

    def test_ok_log_parser(self):
        self.assertEqual(log_parser(raw_ok_log_sample, logger = None), log_sample)

    def test_fail_logparser(self):
        self.assertEqual(len(log_parser(raw_fail_log_sample, logger = None)), 1)


    def test_ok_log_performer(self):
        self.assertEqual(len(log_performer(log_sample, logger = None)), 3)

    def test_fail_log_performer(self):
        self.assertEqual(len(log_performer(log_sample)), 3)


if __name__ == '__main__':
    unittest.main()
