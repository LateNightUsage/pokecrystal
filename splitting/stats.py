#!/usr/bin/env python3
# vim:set tabstop=4 shiftwidth=4 expandtab smarttab

from json import loads

from lib import read_symbols, get_rom_addr, get_group_limits

import argparse

parser = argparse.ArgumentParser()
parser.add_argument('groups', type=argparse.FileType('r'))
parser.add_argument('-s', '--sym', type=argparse.FileType('r'))
parser.add_argument('-o', '--out', default="groups.txt", type=argparse.FileType('w'))
args = parser.parse_args()

groups = loads(args.groups.read())
syms = read_symbols(args.sym)

addrs_lookup = {}
for sym in syms:
    addr = get_rom_addr(syms, sym)
    addrs_lookup[addr] = sym

print("Total groups: %d" % len(groups), file=args.out)

lone = 0
for group in groups:
    if len(group) == 1:
        lone += 1
print("Single-item groups: %d" % lone, file=args.out)

groupstarts = []
for group_index, group in enumerate(groups):
    first, last = get_group_limits(syms, group)
    groupstarts.append((group_index, first, last))

groupstarts.sort(key=lambda k: k[1])

for group in groupstarts:
    label1 = addrs_lookup[group[1]]
    label2 = addrs_lookup[group[2]]
    if label1 == label2:
        print("Group %d: %s" % (group[0], label1), file=args.out)
    else:
        print("Group %d: %s - %s" % (group[0], label1, label2), file=args.out)
