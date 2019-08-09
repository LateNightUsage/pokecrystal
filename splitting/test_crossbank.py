#!/usr/bin/env python3
# vim:set tabstop=4 shiftwidth=4 expandtab smarttab

from json import loads
from lib import read_symbols

import argparse

parser = argparse.ArgumentParser()
parser.add_argument('refs', type=argparse.FileType('r'))
parser.add_argument('-s', '--sym', type=argparse.FileType('r'))
args = parser.parse_args()

refs = loads(args.refs.read())
symbols = read_symbols(args.sym)

result = 0

for symbol in refs:
    srcbank = symbols[symbol][0]
    for symbol2 in refs[symbol]:
        if refs[symbol][symbol2]:
            continue
        destbank = symbols[symbol2][0]
        if srcbank != destbank:
            print("%02X->%02X: %s -> %s" % (srcbank, destbank, symbol, symbol2))
            result = 1

exit(result)
