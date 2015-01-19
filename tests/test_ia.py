#! /usr/bin/env python

import unittest
import ia
from collections import Counter

class TestIA(unittest.TestCase):
    def setUp(self):
        None

    def test_cons_lattice(self):
        self.assertEquals(ia.Lattice(x for x in 'abc').lattice,
                          [{ia.larc_t(label='<BOS>', begin=0, end=1, children=()): 0},
                           {ia.larc_t(label='a', begin=1, end=2, children=()): 0},
                           {ia.larc_t(label='b', begin=2, end=3, children=()): 0},
                           {ia.larc_t(label='c', begin=3, end=4, children=()): 0},
                           {ia.larc_t(label='<EOS>', begin=4, end=5, children=()): 0}])

    def test_cons_table(self):
        self.assertEquals(ia.Lexicon(3, [x for x in 'abracadabra']).counts,
                          Counter({('<BOS>', 'a', 'b'): 1,
                                   ('r', 'a', '<EOS>'): 1,
                                   ('b', 'r', 'a'): 2,
                                   ('a', 'b', 'r'): 2,
                                   ('a', 'c', 'a'): 1,
                                   ('r', 'a', 'c'): 1,
                                   ('d', 'a', 'b'): 1,
                                   ('a', 'd', 'a'): 1,
                                   ('c', 'a', 'd'): 1}))

    def test_dot_simple(self):
        lattice = ia.Lattice(x for x in 'abc')
        lattice.add_confirmed_arc('A', (), 1, 3)
        self.assertEquals(lattice.to_dot_from_span(0, 3).strip(), '''
strict digraph  {
node[shape=none];

subgraph cluster_body{
    graph[style=invis];
    edge[style=dotted, arrowhead=none];
    node[shape=point, label=""];

B_0 -> B_1 [label="<BOS>"];
B_1 -> B_2 [label="a"];
B_2 -> B_3 [label="b"];
}
B_1 -> A_1 -> B_3;
A_1 node [label="A"];
}
        '''.strip())
        
if __name__ == '__main__':
    unittest.main()
