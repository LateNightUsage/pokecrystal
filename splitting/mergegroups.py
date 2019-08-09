#!/usr/bin/env python3
# vim:set tabstop=4 shiftwidth=4 expandtab smarttab

from json import loads, dumps

from lib import read_symbols, get_group_limits, sort_groups

import argparse
parser = argparse.ArgumentParser()
parser.add_argument('groups', default="groups.json", type=argparse.FileType('r'))
parser.add_argument('-s', '--sym', default="pokecrystal.sym", type=argparse.FileType('r'))
parser.add_argument('-o', '--out', default="groups.merged.json", type=argparse.FileType('w'))
args = parser.parse_args()

syms = read_symbols(args.sym)
groups = loads(args.groups.read())

def overlap(x, y):
    return ((x[0] >= y[0] and x[0] <= y[1]) or
            (x[1] >= y[0] and x[1] <= y[1]) or
            (y[0] >= x[0] and y[0] <= x[1]) or
            (y[1] >= x[0] and y[1] <= x[1]))

def merge(dest, src):
    dest[0] = min(src[0], dest[0])
    dest[1] = max(src[1], dest[1])
    dest[2] += src[2]

# Store each group in an array with its limits
ranges = []
for group in groups:
    _min, _max = get_group_limits(syms, group)
    range = [_min, _max, group]
    ranges.append(range)

groups = []

# Merge all overlapping groups
ranges.sort(key=lambda x: x[0])
current = ranges[0]
for range in ranges[1:]:
    if overlap(current, range):
        merge(current, range)
    else:
        groups.append(current[2])
        current = range
groups.append(current[2])

args.out.write(dumps(sort_groups(groups, True), indent=4))
