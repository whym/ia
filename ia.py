#! /usr/bin/env python
# -*- coding:utf-8 -*-

"""Baseline implementation of interactive grammar induction (N-gram based)"""

import sys
import argparse
from collections import namedtuple, defaultdict, Counter

lnode_t = namedtuple('LNode', 'label begin end children')
BOS = '<BOS>'
EOS = '<EOS>'

class Lattice:
    """
    Lattice is composed with a list of nodes and instance scores.
    """
    def __init__(self, seq):
        self.lattice = [[lnode_t(BOS, 0, 1, []), 0]]
        for (i,x) in enumerate(seq):
            self.lattice.append([lnode_t(x, i+1, i+2, []), 0])
        self.lattice.append([lnode_t(EOS, len(self.lattice), len(self.lattice)+1, []), 0])

    def add_confirmed_arc(self, label, targets, begin, end):
        self.lattice.append([lnode_t(label, begin, end, targets), 1])

    def __repr__(self):
        return 'Lattice(%s)' % self.lattice

class Lexicon:
    """
    Lexicon stores candidates n-grams, and confirmed phrases.
    """
    def __init__(self, nsize, seq=[], counts=Counter(), scores=defaultdict(int)):
        self.nsize = nsize
        self.counts = counts
        self.scores = scores
        for i in range(0, len(seq) - nsize + 1):
            tp = tuple(seq[i:i+nsize])
            self.counts[tp] += 1
            self.scores[tp] = 0

    def most_frequent(self):
        for (k,v) in self.counts.most_common():
            if self.scores[k] == 0:
                yield k

    def add_confirmed(self, ngram):
        self.scores[ngram] = 1

    def __repr__(self):
        return 'Lexicon(nsize=%d, counts=%s, scores=%s)' % (self.nsize, self.counts, self.scores)

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('-N', '--ngram-size', type=int, default=2,
                        help='N-gram size')
    parser.add_argument('-v', '--verbose', action='store_true', default=False,
                        help='turn on verbose message output')
    options = parser.parse_args()
    if options.verbose:
        print >>sys.stderr, options

    lines = [line.strip() for line in sys.stdin]
    lattice = Lattice(lines)
    lexicon = Lexicon(options.ngram_size, lines)

    if options.verbose:
        print >>sys.stderr, lattice
        print >>sys.stderr, lexicon
