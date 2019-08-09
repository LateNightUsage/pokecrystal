#!/usr/bin/env python3
# vim:set tabstop=4 shiftwidth=4 expandtab smarttab

from json import loads, dumps
from random import random

from lib import sort_groups

import argparse
parser = argparse.ArgumentParser()
parser.add_argument('references', default="references.json", type=argparse.FileType('r'))
parser.add_argument('bankless', default="bankless.json", type=argparse.FileType('r'))
parser.add_argument('-o', '--out', default="groups.json", type=argparse.FileType('w'))
args = parser.parse_args()

globalsyms = loads(args.references.read())
banklesssyms = loads(args.bankless.read())

makebanklessgroup = True

banklessgroup = set()
syms_groups = {}

for symbol in sorted(globalsyms, key=lambda x: random()):
    # Figure out what group this symbol belongs in
    curgroup = None
    if makebanklessgroup and symbol in banklesssyms:
        curgroup = banklessgroup
    if curgroup == None:
        if symbol in syms_groups:
            curgroup = syms_groups[symbol]
    if curgroup == None:
        curgroup = set()

    # Add this symbol to the group
    if symbol not in curgroup:
        curgroup.add(symbol)
        syms_groups[symbol] = curgroup

    # Add any symbol this symbol references directly to the same group
    for symbol2 in sorted(globalsyms[symbol], key=lambda x: random()):
        if globalsyms[symbol][symbol2]:
            continue

        # Check if this symbol already exists in any other group
        # If so, merge the two groups
        if symbol2 in syms_groups and syms_groups[symbol2] != curgroup:
            newgroup = syms_groups[symbol2]
            if makebanklessgroup and newgroup == banklessgroup:
                # Make sure the special-case "banklessgroup" keeps existing...
                x = curgroup
                curgroup = newgroup
                newgroup = x

            curgroup |= newgroup
            for x in newgroup:
                syms_groups[x] = curgroup
            continue

        if symbol2 not in curgroup:
            curgroup.add(symbol2)
            syms_groups[symbol2] = curgroup

groups = [banklessgroup] if makebanklessgroup else []
for sym in syms_groups:
    if syms_groups[sym] not in groups:
        groups.append(syms_groups[sym])
for group in range(len(groups)):
    groups[group] = list(groups[group])

args.out.write(dumps(sort_groups(groups, makebanklessgroup), indent=4))
