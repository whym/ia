#! /usr/bin/env python

import unittest
import ia
from collections import Counter

class TestIA(unittest.TestCase):
    def setUp(self):
        None

    def test_cons_lattice(self):
        self.assertEquals(ia.Lattice(x for x in 'abc').lattice,
                          [[ia.lnode_t(label='<BOS>', begin=0, end=1, children=[]), 0],
                           [ia.lnode_t(label='a', begin=1, end=2, children=[]), 0],
                           [ia.lnode_t(label='b', begin=2, end=3, children=[]), 0],
                           [ia.lnode_t(label='c', begin=3, end=4, children=[]), 0],
                           [ia.lnode_t(label='<EOS>', begin=4, end=5, children=[]), 0]])

    def test_cons_table(self):
        self.assertEquals(ia.Lexicon(3, [x for x in 'abracadabra']).counts,
                          Counter({('b', 'r', 'a'): 2,
                                   ('a', 'b', 'r'): 2,
                                   ('a', 'c', 'a'): 1,
                                   ('r', 'a', 'c'): 1,
                                   ('d', 'a', 'b'): 1,
                                   ('a', 'd', 'a'): 1,
                                   ('c', 'a', 'd'): 1}))
        
if __name__ == '__main__':
    unittest.main()
