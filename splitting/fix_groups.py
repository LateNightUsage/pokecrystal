#!/usr/bin/env python3
# vim:set tabstop=4 shiftwidth=4 expandtab smarttab

from json import loads, dumps
from os.path import join

from lib import read_symbols, sort_groups

import argparse

parser = argparse.ArgumentParser()
parser.add_argument('input', type=argparse.FileType('r'))
parser.add_argument('output', type=argparse.FileType('w'))
parser.add_argument('-p', '--prefix', type=str, default="")
args = parser.parse_args()

groups = loads(args.input.read())
syms = read_symbols(open(join(args.prefix, "pokecrystal.sym")))

# These labels shouldn't be taken into account once we're done making the groups
BLANKET = [
    "BattleText",
    "BattleCore",
    "PokedexEntries1",
    "PokedexEntries2",
    "PokedexEntries3",
    "PokedexEntries4",
    "KantoFrames",
    "JohtoFrames",
    "PicAnimations",
    "UnownAnimations",
    "AIScoring",
    "GBPrinterSettings",
    "BattleTowerMons"
]

for group in groups:
    for blanket in BLANKET:
        while blanket in group:
            group.remove(blanket)

args.output.write(dumps(sort_groups(groups, True), indent=4))
