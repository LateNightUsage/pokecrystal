#!/usr/bin/env python3
# vim:set tabstop=4 shiftwidth=4 expandtab smarttab

from sys import stderr, exit
from json import loads

from lib import scrapelabels

import argparse

parser = argparse.ArgumentParser()
parser.add_argument('files', type=str, nargs='+')
parser.add_argument('-r', '--refs', type=argparse.FileType('r'))
args = parser.parse_args()

refs = loads(args.refs.read())

labels = {}
for file in args.files:
    for label in scrapelabels(file):
        labels[label] = file

for label in labels:
    if label == "\\1_":
        continue

    for ref in refs[label]:
        if not refs[label][ref]:
            if not ref in labels:
                continue
            if labels[label] != labels[ref]:
                print("%s:%s -> %s:%s" % (labels[label], label, labels[ref], ref))
