#! /usr/bin/env python
# -*- coding:utf-8 -*-

"""Baseline implementation of interactive grammar induction (N-gram based)"""

import sys
import argparse
import fileinput
import codecs
from collections import namedtuple, defaultdict, Counter

larc_t = namedtuple('LArc', 'label begin end children')
BOS = '<BOS>'
EOS = '<EOS>'

class Lattice:
    """
    Lattice is composed with a list of arcs and instance scores.
    """
    def __init__(self, seq, debug=False):
        self.debug = debug
        self.lattice = [{larc_t(BOS, 0, 1, ()): 0}]
        for (i,x) in enumerate(seq):
            self.lattice.append({larc_t(x, i+1, i+2, ()): 0})
        self.lattice.append({larc_t(EOS, len(self.lattice), len(self.lattice)+1, ()): 0})

    def find_arc(self, label, begin, end):
        for n in self.lattice:
            if n.labe == label and n.begin == begin and n.end == end:
                return n
        return None

    def find_positions(self, seq):
        nsize = len(seq)
        for i in xrange(0, len(self.lattice) - nsize + 1):
            flag = True
            for j in xrange(0, nsize):
                if seq[j] not in [x.label for x in self.lattice[i+j].keys()]:
                    flag = False
            if flag:
                yield i

    def add_confirmed_arc(self, label, targets, begin, end):
        if self.debug:
            for t in targets:
                if not self.find_arc(t.label, t.begin, t.end):
                    raise
        self.lattice.append([larc_t(label, begin, end, targets), 1])

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
        for i in xrange(0, len(seq) - nsize + 1):
            tp = tuple(seq[i:i+nsize])
            self.counts[tp] += 1
            self.scores[tp] = 0

    def most_frequent(self):
        for (k,v) in self.counts.most_common():
            if self.scores[k] == 0: # zero means not presented to the annotator yet
                yield k

    def add_confirmed(self, ngram):
        self.scores[ngram] = 1

    def add_declined(self, ngram):
        self.scores[ngram] = -1

    def __repr__(self):
        return 'Lexicon(nsize=%d, counts=%s, scores=%s)' % (self.nsize, self.counts, self.scores)

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--ngram-size', type=int, default=2,
                        help='N-gram size')
    parser.add_argument('-v', '--verbose', action='store_true', default=False,
                        help='turn on verbose message output')
    parser.add_argument('ifile')
    options = parser.parse_args()
    if options.verbose:
        print >>sys.stderr, options

    lines = [line.strip() for line in codecs.open(options.ifile, encoding='utf-8').readlines()]
    lattice = Lattice(lines)
    lexicon = Lexicon(options.ngram_size, lines)

    if options.verbose:
        print >>sys.stderr, lattice
        print >>sys.stderr, lexicon


    arc_id = 1
    while True:
        for k in lexicon.most_frequent():
            print k
            p = raw_input('? ')
            if p.lower()[0] != 'n':
                lexicon.add_confirmed(k)
                # TODO: implement # lattice.add_confirmed_arc(arc_id)
            else:
                lexicon.add_declined(k)
            break
