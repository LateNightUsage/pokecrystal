#!/usr/bin/env python3
# vim:set tabstop=4 shiftwidth=4 expandtab smarttab

from sys import stderr, exit
from json import loads

import argparse

parser = argparse.ArgumentParser()
parser.add_argument('label', type=str)
parser.add_argument('-g', '--groups', type=argparse.FileType('r'))
parser.add_argument('-r', '--refs', type=argparse.FileType('r'))
parser.add_argument('-I', '--noindirect', action='store_true')
args = parser.parse_args()

groups = loads(args.groups.read())
refs = loads(args.refs.read())

group = None
for g in groups:
    if args.label in g:
        group = g
        break
else:
    print("Couldn't find label '%s'" % args.label, file=stderr)
    exit(1)

out = open("graph.dot", "w")
print("digraph {", file=out)
print("\trankdir=LR;", file=out)
for label in group:
    for ref in refs[label]:
        if refs[label][ref]:
            if not args.noindirect:
                print("\t\"%s\" -> \"%s\"[style=dashed];" % (label, ref), file=out)
        else:
            print("\t\"%s\" -> \"%s\"[style=solid];" % (label, ref), file=out)
print("}", file=out)
