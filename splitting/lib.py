# vim:set tabstop=4 shiftwidth=4 expandtab smarttab

from functools import cmp_to_key

def sort_groups(groups, bankless):
    def cmpgroup(grp1, grp2):
        res1 = len(grp1)
        res2 = len(grp2)

        index = 0
        while res1 == res2 and (len(grp1) > index or len(grp2) > index):
            if len(grp1) > index and len(grp2) > index:
                res1 += grp1[index] > grp2[index]
                res2 += grp2[index] > grp1[index]
            else:
                res1 += len(grp1) > index
                res2 += len(grp2) > index
            index += 1

        return res2 - res1

    for group in groups:
        group.sort()

    if bankless:
        groups = [groups[0]] + sorted(groups[1:], key=cmp_to_key(cmpgroup))
    else:
        groups.sort(key=cmp_to_key(cmpgroup))

    return groups

def read_symbols(file):
    symbols = {}

    for line in file:
        line = line.split(";")[0].strip()
        split = line.split(" ")
        if len(split) < 2:
            continue

        splitaddr = split[0].split(":")
        if len(splitaddr) < 2:
            continue
        bank = int(splitaddr[0], 16)
        addr = int(splitaddr[1], 16)
        symbol = " ".join(split[1:]).strip()
        if "." in symbol:
            continue
        if addr >= 0x8000:
            continue
        symbols[symbol] = (bank, addr)

    return symbols

def get_rom_addr(syms, symbol):
    return syms[symbol][0] * 0x4000 + syms[symbol][1] % 0x4000

def get_group_limits(syms, group):
    min = None
    max = None

    for item in group:
        addr = get_rom_addr(syms, item)

        if not min: min = addr
        if not max: max = addr
        if addr < min: min = addr
        if addr > max: max = addr

    return min, max

def scrapelabels(file):
    labels = []
    for line in open(file):
        if not (line.startswith("\t") or line.startswith(" ") or line.startswith(";") or line.startswith(".")):
            split = line.split(":")
            if len(split) > 1:
                if split[1].split(";")[0].strip().lower() == "macro":
                    continue
                labels.append(split[0])
    return labels
