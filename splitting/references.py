#!/usr/bin/env python3
# vim:set tabstop=4 shiftwidth=4 expandtab smarttab

from sys import argv, exit, stderr
from struct import unpack, calcsize
from enum import Enum
from json import dumps

from bisect import bisect_right

import argparse

class symtype(Enum):
    LOCAL = 0
    IMPORT = 1
    EXPORT = 2

class sectype(Enum):
    WRAM0 = 0
    VRAM = 1
    ROMX = 2
    ROM0 = 3
    HRAM = 4
    WRAMX = 5
    SRAM = 6
    OAM = 7

def unpack_file(fmt, file):
    size = calcsize(fmt)
    return unpack(fmt, file.read(size))

def read_string(file):
    buf = bytearray()
    while True:
        b = file.read(1)
        if b is None or b == b'\0':
            return buf.decode()
        else:
            buf += b

def parse_object(file):
    obj = {
        "symbols": [],
        "sections": []
    }

    num_symbols, num_sections = unpack_file("<II", file)

    for x in range(num_symbols):
        symbol = {}

        symbol["name"] = read_string(file)
        symbol["type"] = symtype(unpack_file("<B", file)[0])
        if symbol["type"] != symtype.IMPORT:
            symbol["filename"] = read_string(file)
            symbol["line_num"], symbol["section"], symbol["value"] = unpack_file("<III", file)

        obj["symbols"].append(symbol)

    for x in range(num_sections):
        section = {}

        section["name"] = read_string(file)
        size, type, section["org"], section["bank"], section["align"] = unpack_file("<IBIII", file)
        section["type"] = sectype(type)

        if section["type"] == sectype.ROMX or section["type"] == sectype.ROM0:
            section["data"] = file.read(size)

            section["patches"] = []
            num_patches = unpack_file("<I", file)[0]
            for x in range(num_patches):
                patch = {}

                patch["filename"] = read_string(file)
                patch["line"], patch["offset"], patch["type"], rpn_size = unpack_file("<IIBI", file)
                patch["rpn"] = file.read(rpn_size)

                section["patches"].append(patch)

        obj["sections"].append(section)

    return obj

def find_le(a, x):
    'Find rightmost value less than or equal to x'
    i = bisect_right(a, x)
    if i:
        return a[i-1]
    raise ValueError

def is_valid_symbol(symbol):
    """ Checks whether a symbol is an actual label. """

    if symbol["name"] == "@":
        return False

    if "." in symbol["name"]:
        return False

    return True

def get_symbol_name(symbol):
    """ Get the name of a symbol, preceeded by the filename if it's local """
    name = symbol["name"]
    if symbol["type"] == symtype.LOCAL and name not in globalsyms:
        name = filename + ":" + symbol["name"]
    return name


parser = argparse.ArgumentParser()
parser.add_argument('files', nargs='+', type=str)
parser.add_argument('-o', '--out', default="references.json", type=argparse.FileType('w'))
parser.add_argument('-b', '--bankless', default="bankless.json", type=argparse.FileType('w'))
parser.add_argument('-p', '--prefix', default="", type=str)
args = parser.parse_args()

# This dict stores all of the symbols and what they reference
globalsyms = {}

# This set tracks what symbols are considered "bankless" (i.e. they're in ROM0)
banklesssyms = set()

# This set tracks any symbols that aren't in ROM
ramsyms = set()

for filename in args.files:
    print(filename, file=stderr)

    file = open(filename, "rb")

    id = unpack_file("4s", file)[0]
    if id != b'RGB6':
        print("File %s is of an unknown format." % filename, file=stderr)
        exit(1)

    obj = parse_object(file)

    file.close()
    if filename.startswith(args.prefix):
        filename = filename[len(args.prefix):]

    # Populate globalsyms with the appropriate name.
    # If the name is "global", it'll appear as just the name,
    #   if the name is only defined locally in a single object,
    #   prefix it with the path and filename of the object.
    local = 0
    imports = 0
    exports = 0
    for symbol in obj["symbols"]:
        if not is_valid_symbol(symbol):
            continue

        name = symbol["name"]

        if symbol["type"] == symtype.LOCAL:
            local += 1
            if name not in globalsyms:
                name = filename + ":" + symbol["name"]
        elif symbol["type"] == symtype.IMPORT:
            imports += 1
        elif symbol["type"] == symtype.EXPORT:
            exports += 1
            if filename + ":" + symbol["name"] in globalsyms:
                del globalsyms[filename + ":" + symbol["name"]]

        if name not in globalsyms:
            globalsyms[name] = {}

    print("Locals:", local, file=stderr)
    print("Imports:", imports, file=stderr)
    print("Exports:", exports, file=stderr)
    print(file=stderr)

    # Build a lookup table from the values of symbols to their names
    # If there's symbols with the same value, associate them together right now.
    sectionsyms = {}
    for section in range(len(obj["sections"])):
        sectionsyms[section] = {
            "array": [],
            "lookup": {}
        }

    for symbol in obj["symbols"]:
        if not is_valid_symbol(symbol):
            continue

        if symbol["type"] != symtype.IMPORT:
            if symbol["section"] == 0xffffffff:
                continue

            if symbol["value"] not in sectionsyms[symbol["section"]]["lookup"]:
                sectionsyms[symbol["section"]]["array"].append(symbol["value"])
                sectionsyms[symbol["section"]]["lookup"][symbol["value"]] = symbol
            else:
                name = get_symbol_name(symbol)
                alias = sectionsyms[symbol["section"]]["lookup"][symbol["value"]]
                alias_name = get_symbol_name(alias)
                globalsyms[name][alias_name] = False

    # Sort all of the sections' arrays
    for x in sectionsyms:
        sectionsyms[x]["array"].sort()

    # Time to parse the RPN data
    for section in obj["sections"]:
        if section["type"] != sectype.ROMX and section["type"] != sectype.ROM0:
            continue

        for patch in section["patches"]:
            rpn = patch["rpn"]

            pos = 0
            while pos < len(rpn):
                if rpn[pos] == 0x51:
                    # Skip a string
                    pos += 1
                    while rpn[pos] != 0:
                        pos += 1
                    continue
                elif rpn[pos] == 0x80:
                    # Skip long integer
                    pos += 5
                    continue
                elif rpn[pos] != 0x50 and rpn[pos] != 0x81:
                    # Skip byte
                    pos += 1
                    continue

                # Parse a symbol
                # 0x50: BANK(symbol)
                # 0x81: symbol

                # Find the symbol that preceeds this patch
                current_section = obj["sections"].index(section)
                try:
                    current_sym_offs = find_le(sectionsyms[current_section]["array"], patch["offset"])
                    current_sym = sectionsyms[current_section]["lookup"][current_sym_offs]
                except ValueError:
                    # If such a symbol doesn't exist, create a symbol using the section's name
                    if section["name"] not in globalsyms:
                        globalsyms[section["name"]] = {}
                    current_sym = {"name": section["name"], "type": symtype.EXPORT}

                    if section["type"] == sectype.ROM0:
                        banklesssyms.add(current_sym["name"])

                # Get the symbol that it's referencing
                ref_sym_id = unpack("<I", rpn[pos + 1:pos + 5])[0]
                ref_sym = obj["symbols"][ref_sym_id]
                isbankref = True if rpn[pos] == 0x50 else False
                pos += 5

                if not is_valid_symbol(ref_sym):
                    continue

                current_sym_name = get_symbol_name(current_sym)
                ref_sym_name = get_symbol_name(ref_sym)

                if current_sym_name != ref_sym_name:
                    # Add the symbol to the list of references by current_sym_name
                    # If it already exists, but we've now encountered a bank reference to it,
                    #   set it to True.
                    if ref_sym_name not in globalsyms[current_sym_name]:
                        globalsyms[current_sym_name][ref_sym_name] = isbankref
                    elif isbankref:
                        globalsyms[current_sym_name][ref_sym_name] = isbankref

    # Populate banklessyms and ramsyms
    for symbol in obj["symbols"]:
        if not is_valid_symbol(symbol):
            continue

        if symbol["type"] == symtype.IMPORT:
            continue

        symbol_name = get_symbol_name(symbol)

        if symbol["section"] == 0xffffffff:
            ramsyms.add(symbol_name)
            continue

        sect = obj["sections"][symbol["section"]]["type"]

        if sect == sectype.ROM0:
            banklesssyms.add(symbol_name)
        elif sect != sectype.ROMX:
            ramsyms.add(symbol_name)

# Remove any RAM symbols from globalsyms
for symbol in dict(globalsyms):
    if symbol in ramsyms:
        del globalsyms[symbol]

for symbol in globalsyms:
    # Remove any references to RAM symbols
    for symbol2 in dict(globalsyms[symbol]):
        if symbol2 in ramsyms:
            del globalsyms[symbol][symbol2]

    # All references to symbols in ROM0 from ROMX might as well be done through BANK()
    if symbol not in banklesssyms:
        for symbol2 in globalsyms[symbol]:
            if symbol2 in banklesssyms:
                globalsyms[symbol][symbol2] = True

args.out.write(dumps(globalsyms, indent=4))
args.bankless.write(dumps({x: True for x in banklesssyms}, indent=4))
