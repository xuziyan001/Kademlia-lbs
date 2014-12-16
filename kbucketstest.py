__author__ = 'X'


import unittest
from kbuckets import KBuckets


class KBucketsTest(unittest.TestCase):
    def setUp(self):
        self.kbucket = KBuckets()

    def test_bucket_length(self):
        self.assertEqual(len(self.kbucket.bucket), 160)

    def test_add_bucket(self):
        self.kbucket.add_bucket((123,8080), 5)
        self.kbucket.add_bucket((1234, 8081), 5)
        self.assertEqual(self.kbucket.bucket[5], [(123,8080), (1234, 8081)])
        self.kbucket.add_bucket((12345,8082), 5)
        self.kbucket.add_bucket((123,8080), 5)
        self.assertEqual(self.kbucket.bucket[5], [(1234, 8081), (12345, 8082), (123,8080)])
        self.kbucket.add_bucket((1,8080), 5)
        self.kbucket.add_bucket((12,8080), 5)
        self.kbucket.add_bucket((123456,8080), 5)
        self.assertEqual(self.kbucket.bucket[5], [(1234, 8081), (12345, 8082), (123,8080), (1,8080), (12,8080)])

    def test_delete_bucket(self):
        self.kbucket.add_bucket((123,8080),5)
        self.kbucket.add_bucket((1234, 8081),5)
        self.kbucket.delete_bucket((123,8080), 5)
        self.assertEqual(self.kbucket.bucket[5], [(1234, 8081)])

    def test_find_closest_node(self):
        self.kbucket.add_bucket((123,8080),5)
        self.kbucket.add_bucket((1234, 8081),5)
        #self.kbucket.add_bucket((12344,8082),5)
        self.kbucket.add_bucket((1239,8083),4)
        self.kbucket.add_bucket((1223,8084),3)
        self.kbucket.add_bucket((1235,8085),6)
        self.kbucket.add_bucket((1253,8086),6)
        self.kbucket.add_bucket((1252,8087),6)
        self.assertEqual(self.kbucket.find_closest_node(1238,5), [(1239,8083),(1234, 8081),(1235,8085)])
