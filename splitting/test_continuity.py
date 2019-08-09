#!/usr/bin/env python3
# vim:set tabstop=4 shiftwidth=4 expandtab smarttab

from json import loads
from bisect import bisect_left

from lib import read_symbols, get_rom_addr, get_group_limits

import argparse

parser = argparse.ArgumentParser()
parser.add_argument('groups', type=argparse.FileType('r'))
parser.add_argument('-s', '--sym', type=argparse.FileType('r'))
args = parser.parse_args()

groups = loads(args.groups.read())
syms = read_symbols(args.sym)

result = 0

addrs_array = []
addrs_lookup = {}
for group in groups:
    for sym in group:
        addr = get_rom_addr(syms, sym)
        if addr in addrs_lookup:
            continue
        addrs_array.append(addr)
        addrs_lookup[addr] = sym
addrs_array.sort()

result = 0

for group_index, group in enumerate(groups):
    min, max = get_group_limits(syms, group)

    notingroup = []

    index = bisect_left(addrs_array, min)
    while index < len(addrs_array) and addrs_array[index] <= max:
        sym = addrs_lookup[addrs_array[index]]
        index += 1

        if sym not in group:
            notingroup.append(sym)

    if notingroup:
        print("Group %04d:" % group_index, notingroup)
        result = 1

exit(result)
