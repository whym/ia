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

    def test_sentences(self):
        lattice = ia.Lattice(['<BOS>'] + [x for x in 'abc'] + ['<EOS>', '<BOS>'] + [x for x in 'de'] + ['<EOS>'])
        print lattice.body
        print lattice.lattice
        self.assertEquals(lattice.sentences(),
                          [(0,4), (5,8)])

    def test_dot_simple(self):
        lattice = ia.Lattice(x for x in 'abc')
        lattice.add_confirmed_arc('A', (), 1, 3)
        self.assertEquals(lattice.to_dot().strip(), '''

strict digraph  {
rankdir=LR;
node[shape=none];
page="8.5,11";
charset="UTF-8";

subgraph cluster_c3{
    graph[style=invis];
    edge[style=dotted, arrowhead=none];
    node[shape=point, label=""];

P_c3_0 -> P_c3_1 [label="<BOS>"];
P_c3_1 -> P_c3_2 [label="a"];
P_c3_2 -> P_c3_3 [label="b"];
P_c3_3 -> P_c3_4 [label="c"];
}
P_c3_1 -> A_c3_1 -> P_c3_3;
A_c3_1 node [label="A"];

}
        '''.strip())
        
if __name__ == '__main__':
    unittest.main()
