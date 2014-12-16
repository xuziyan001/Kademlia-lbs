__author__ = 'X'


import unittest
from node import Node


class NodeTest(unittest.TestCase):

    def setUp(self):
        seed = []
        self.node = []
        for i in range(10):
            seed.append('127.0.0.1:'+str(i+10000))
        for each in seed:
            node = Node(each)
            self.node.append(node)

    def test_find_bucket_num(self):
        id1 = 109988570602406909885895740636038865475
        self.assertEqual(self.node[7].find_bucket_num(id1), -1)
        id2 = 109988570602406909885895740636038865476
        self.assertEqual(self.node[7].find_bucket_num(id2), 2)
        id3 = 109988570602406909885895740636038865474
        self.assertEqual(self.node[7].find_bucket_num(id3), 0)
        id4 = 0
        self.assertEqual(self.node[7].find_bucket_num(id4), 126)

    def test_parse_info(self):
        dic = {'a':'123','b':'345','c':'387'}
        self.assertDictEqual(self.node[7].parse_info('a=123&b=345&c=387'), dic)

    def test_dic_to_str(self):
        dic = {'a':123,'b':'345','c':3298498298420384938209482998}
        self.assertEqual(self.node[7].dic_to_str(dic), 'a=123&c=3298498298420384938209482998&b=345')

    #no need
    #def test_find_closest_node(self):

    def tearDown(self):
        self.node = None