#!/usr/bin/env python3
# vim:set tabstop=4 shiftwidth=4 expandtab smarttab

from json import loads
from lib import read_symbols

import argparse

parser = argparse.ArgumentParser()
parser.add_argument('groups', type=argparse.FileType('r'))
parser.add_argument('-s', '--sym', type=argparse.FileType('r'))
args = parser.parse_args()

groups = loads(args.groups.read())
symbols = read_symbols(args.sym)

result = 0

for group in groups:
    bank = None
    for symbol in group:
        if not bank:
            bank = symbols[symbol][0]
            continue
        if symbols[symbol][0] != bank:
            print("%02X->%02X: %s (group %d)" % (bank, symbols[symbol][0], symbol, groups.index(group)))
            result = 1

exit(result)
