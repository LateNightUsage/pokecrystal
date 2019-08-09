#!/usr/bin/env python3
# vim:set tabstop=4 shiftwidth=4 expandtab smarttab

# The -s option should have a complete symfile, generated with -E
# The -m option should have the map file of the target codebase

from json import loads

from lib import read_symbols, get_rom_addr, get_group_limits

import argparse

parser = argparse.ArgumentParser()
parser.add_argument('groups', type=argparse.FileType('r'))
parser.add_argument('-s', '--sym', type=argparse.FileType('r'))
parser.add_argument('-m', '--map', type=argparse.FileType('r'))
args = parser.parse_args()

groups = loads(args.groups.read())
syms = read_symbols(args.sym)

# Figure out the start and end address of each section
sections = {}
curbank = 0
begin = None
end = None
for line in args.map:
    if not line.strip():
        continue

    if not line.startswith(" "):
        if not line.startswith("ROM Bank #"):
            break
        curbank = int(line.split("#")[1].split(":")[0].split(" ")[0])
        continue

    if line.startswith("  SECTION: "):
        addr = line.split()[1].split("-")
        if len(addr) < 2:
            continue

        begin = curbank * 0x4000 + int(addr[0].strip()[1:], 16) % 0x4000
        end = curbank * 0x4000 + int(addr[1].strip()[1:], 16) % 0x4000
        sections[begin] = end
        continue

# Make a lookup table from address to symbol for the original rom
addrs_lookup = {}
for sym in syms:
    addr = get_rom_addr(syms, sym)
    addrs_lookup[addr] = sym

# Figure out the group's limits for each group and sort them
groupstarts = []
for group_index, group in enumerate(groups):
    first, last = get_group_limits(syms, group)
    groupstarts.append((group_index, first, last))
groupstarts.sort(key=lambda k: k[1])

result = 0

for group in groupstarts:
    label1 = addrs_lookup[group[1]]
    label2 = addrs_lookup[group[2]]

    # Group 0 is just the entire home bank, we don't care about sections here.
    if group[0] == 0:
        continue

    # The BattleCommandPointers section starts with two bytes before the first label...
    if label1 == label2 == "BattleCommandPointers":
        group = (group[0], group[1] - 2, group[2])

    # We're required to split these sections up into multiple sections, due to charmap shenanigans
    if label1 == "Function100000" and label2 == "UnknownText_0x1021f4":
        if group[1] in sections:
            continue
    if label1 == "Function118000" and label2 == "TilemapPack_11bb7d":
        if group[1] in sections:
            continue

    # BattleTowerTrainerDataEnd is an empty label...
    if label1 == "BattleTowerTrainerData" and label2 == "BattleTowerTrainerDataEnd":
        group = (group[0], group[1], group[2] - 1)

    # The news data section starts with three bytes before the first label...
    if label1 == label2 == "Unreferenced_Function1f4003":
        group = (group[0], group[1] - 3, group[2])

    # Try to see if this group has been defined in sections
    if group[1] in sections:
        if group[2] <= sections[group[1]]:
            continue

    result = 1

    if label1 == label2:
        print("Group %d: %s" % (group[0], label1))
    else:
        print("Group %d: %s - %s" % (group[0], label1, label2))

exit(result)
