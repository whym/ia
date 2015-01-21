#! /usr/bin/env python
# -*- coding:utf-8 -*-

"""Baseline implementation of interactive grammar induction (N-gram based)"""

import sys
import argparse
import fileinput
import codecs
from pprint import pprint
from collections import namedtuple, defaultdict, Counter
import pygraphviz as pgv

larc_t = namedtuple('LArc', 'label begin end children')
BOS = '<BOS>'
EOS = '<EOS>'

class Lattice:
    """
    A Lattice is composed with lists of arcs and scores.
    """
    def __init__(self, seq, debug=False):
        self.debug = debug
        self.body = [BOS]
        self.sent_heads = [0];
        self.lattice = [{larc_t(BOS, 0, 1, ()): 0}]
        for (i,x) in enumerate(seq):
            if i == 0 and x == BOS:
                continue
            self.lattice.append({larc_t(x, len(self.body), len(self.body) + 1, ()): 0}) # adding 1 for 0:BOS
            if x == EOS:
                self.sent_heads.append(len(self.body) + 1)
            self.body.append(x)

        if self.body[-1] != EOS:
            self.lattice.append({larc_t(EOS, len(self.lattice), len(self.lattice) + 1, ()): 0})

    def find_arc(self, begin, end, targets):
        for n in cell[begin].keys():
            if n.begin == begin and n.end == end and n.targets == targets:
                return n
        return None

    def find_positions(self, seq):
        nsize = len(seq)
        for i in xrange(0, len(self.lattice) - nsize + 1):
            for j in xrange(0, nsize):
                if seq[j] not in [x.label for x in self.lattice[i+j].keys()]:
                    break
            else:
                yield i

    def add_confirmed_arc(self, label, targets, begin, end):
        if not isinstance(targets, tuple):
            targets = tuple(targets)
        if self.debug:
            for t in targets:
                if not self.find_arc(t.begin, t.end):
                    raise
        self.lattice[begin][larc_t(label, begin, end, targets)] = 1

    def __repr__(self):
        return 'Lattice(%s)' % self.lattice

    def sentences(self):
        return [(i,j-1) for (i,j) in zip(self.sent_heads, self.sent_heads[1:]+[len(self.lattice) - 1]) if i < j]

    def to_dot(self):
        dots = [self.to_partial_dot_from_span(x, y) for (x,y) in self.sentences()]
        return '''
strict digraph  {
rankdir=LR;
node[shape=none];
page="8.5,11";
charset="UTF-8";
%s

}''' % ('\n'.join(dots))

    def to_partial_dot_from_span(self, begin, end):
        lines = []
        cluster = 'c%d' % end

        # edges for the body string
        lines.append('''
subgraph cluster_%s{
    graph[style=invis];
    edge[style=dotted, arrowhead=none];
    node[shape=point, label=""];
''' % cluster)
        for i in xrange(begin, end+1):
            lines.append('P_%s_%d -> P_%s_%d [label="%s"];' % (cluster, i, cluster, i+1, self.body[i].replace('"', "'")))
        lines.append('}')

        # edges for (syntactic) arcs
        n = 1
        for p in xrange(begin, end):
            for arc in self.lattice[p].keys():
                if arc.end <= end and arc.end > arc.begin + 1:
                    lines.append('P_%s_%d -> A_%s_%d -> P_%s_%d;' % (cluster, arc.begin, cluster, n, cluster, arc.end))
                    lines.append('A_%s_%d node [label="%s"];' % (cluster, n, arc.label))
                    n += 1
        return '\n'.join(lines)

class Lexicon:
    """
    Lexicon stores candidates n-grams, and confirmed phrases.
    """
    def __init__(self, nsize, seq=[], counts=Counter(), scores=defaultdict(int)):
        self.nsize = nsize
        self.body = [BOS] + list(seq) + [EOS]
        self.counts = counts
        self.scores = scores
        for i in xrange(0, len(self.body) - nsize + 1):
            if EOS not in self.body[i:i+nsize-1]:
                self.new_entries_from_seq(self.body[i:i+nsize])

    def new_entries_from_seq(self, seq):
        tp = tuple(seq)
        self.counts[tp] += 1
        self.scores[tp] = 0
        
    def most_frequent(self):
        for (k,v) in self.counts.most_common():
            if self.scores[k] == 0: # zero means not presented to the annotator yet
                yield k

    def frequency(self, k):
        return self.counts[k]

    def find_positions(self, seq):
        seq = list(seq)
        nsize = len(seq)
        for i in xrange(0, len(self.body) - nsize + 1):
            if seq == self.body[i:i+len(seq)]:
                yield i

    def add_confirmed(self, ngram):
        self.scores[ngram] = 1

        # add counts for ngrams containing the new segment
        for p in self.find_positions(ngram):
            None

    def add_declined(self, ngram):
        self.scores[ngram] = -1

    def __repr__(self):
        return 'Lexicon(nsize=%d, counts=%s, scores=%s)' % (self.nsize, self.counts, self.scores)

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--ngram-size', type=int, default=2,
                        help='N-gram size')
    parser.add_argument('-o', '--output', type=str, default='out.pdf',
                        help='')
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
    try:
        while True:
            for k in lexicon.most_frequent():
                print >>sys.stderr, '"%s" (%d)' % (' '.join(k), lexicon.frequency(k))
                p = raw_input()
                if len(p) > 0 and p.lower()[0] != 'n':
                    lexicon.add_confirmed(k)
                    for pos in lattice.find_positions(k):
                        lattice.add_confirmed_arc(arc_id, (), pos, pos+len(k))
                        arc_id += 1
                    dot = lattice.to_dot()
                    if options.output.endswith('.dot'):
                        print >>codecs.open(options.output, 'w', encoding='utf-8'), dot
                    else:
                        a = pgv.AGraph(string=dot)
                        a.layout(prog='dot')
                        a.draw(options.output)

                else:
                    lexicon.add_declined(k)
                break
    except EOFError:
        None
    
    #pprint(lexicon)
    #pprint(lattice)
