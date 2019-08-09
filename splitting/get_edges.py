#!/usr/bin/env python3
# vim:set tabstop=4 shiftwidth=4 expandtab smarttab

from sys import stderr, exit
from json import loads

from lib import read_symbols, get_rom_addr

import argparse

parser = argparse.ArgumentParser()
parser.add_argument('label', type=str)
parser.add_argument('-g', '--groups', type=argparse.FileType('r'))
parser.add_argument('-r', '--refs', type=argparse.FileType('r'))
parser.add_argument('-s', '--syms', type=argparse.FileType('r'))
args = parser.parse_args()

groups = loads(args.groups.read())
refs = loads(args.refs.read())
syms = read_symbols(args.syms)

group = None
for g in groups:
    if args.label in g:
        group = g
        break
else:
    print("Couldn't find label '%s'" % args.label, file=stderr)
    exit(1)

last = None

for label in group:
    for ref in refs[label]:
        if not refs[label][ref]:
            diff = abs(get_rom_addr(syms, label) - get_rom_addr(syms, ref))
            if not last or diff > last[0]:
                last = (diff, label, ref)

print(last)
