#!/usr/bin/env python3
# vim:set tabstop=4 shiftwidth=4 expandtab smarttab

from json import loads, dumps
from os import listdir
from os.path import join

from lib import read_symbols, sort_groups, scrapelabels

import argparse
parser = argparse.ArgumentParser()
parser.add_argument('groups', default="groups.json", type=argparse.FileType('r'))
parser.add_argument('-p', '--prefix', default="", type=str)
parser.add_argument('-r', '--refs', default="references.json", type=argparse.FileType('r'))
parser.add_argument('-o', '--out', default="groups.merged.json", type=argparse.FileType('w'))
args = parser.parse_args()

syms = read_symbols(open(join(args.prefix, "pokecrystal.sym")))
groups = loads(args.groups.read())
refs = loads(args.refs.read())

def mergegroup(labels):
    finalgroups = {}
    removegroups = []
    for label in labels:
        if syms[label][0] not in finalgroups:
            finalgroups[syms[label][0]] = []
        finalgroup = finalgroups[syms[label][0]]

        if label in finalgroup:
            continue
        for index, group in enumerate(groups):
            if label in group:
                finalgroup += group
                removegroups.append(index)
                break
        else:
            print("Not found:", label)
            exit(1)

    removegroups.sort(reverse=True)
    for index in removegroups:
        del groups[index]

    for group in finalgroups:
        groups.append(finalgroups[group])

maps = []
for line in open(join(args.prefix, "data", "maps", "attributes.asm")):
    if line.startswith("\tmap_attributes "):
        maps.append(line.strip().split(" ")[1].strip().split(",")[0].strip())

# These things are not worth splitting, because literally every label is
#   standalone, and they're all related.
mergegroup(scrapelabels(join(args.prefix, "gfx", "tilesets.asm")))
mergegroup(scrapelabels(join(args.prefix, "gfx", "battle_anims.asm")))
mergegroup(scrapelabels(join(args.prefix, "gfx", "sprites.asm")))
mergegroup(scrapelabels(join(args.prefix, "gfx", "font.asm")))
mergegroup(scrapelabels(join(args.prefix, "gfx", "emotes.asm")))
mergegroup(scrapelabels(join(args.prefix, "gfx", "pics.asm")))
mergegroup(["%s_MapAttributes" % x for x in maps])
mergegroup(scrapelabels(join(args.prefix, "data", "maps", "blocks.asm")))
for file in listdir(join(args.prefix, "data", "phone", "text")):
    mergegroup(scrapelabels(join(args.prefix, "data", "phone", "text", file)))
for file in ["common_%d.asm" % x for x in range(1, 4)] + ["std_text.asm"]:
    mergegroup(scrapelabels(join(args.prefix, "data", "text", file)))
mergegroup(scrapelabels(join(args.prefix, "data", "battle_tower", "trainer_text.asm")))
mergegroup(scrapelabels(join(args.prefix, "data", "battle_tower", "unknown.asm")))

# All of the phone scripts belong in at least the same bank,
#  there's no use splitting them beyond file boundaries.
callers = []
for file in listdir(join(args.prefix, "engine", "phone", "scripts")):
    # Except for the callers, which I can't really split in any meaningful way.
    # PhoneScript_HangupText_Male/Female are referenced by nearly everything.
    if file.endswith("_gossip.inc") or file.startswith("hangups") or file.startswith("reminders") or file in ["bike_shop.inc", "generic_caller.inc"]:
        callers += scrapelabels(join(args.prefix, "engine", "phone", "scripts", file))
        continue

    # And the family strings used by TiffanysFamilyMemebers...
    if file == "generic_callee.asm":
        labels = scrapelabels(join(args.prefix, "engine", "phone", "scripts", "generic_callee.asm"))
        family = ["GrandmaString", "GrandpaString", "MomString", "DadString", "SisterString", "BrotherString"]
        labels = [x for x in labels if x not in family]
        mergegroup(family)
        mergegroup(labels)
        continue

    mergegroup(scrapelabels(join(args.prefix, "engine", "phone", "scripts", file)))
mergegroup(callers)

# A lot of songs abuse fallthrough into non-local labels
#   (because whoever extracted them didn't bother fixing them afterwards, 
#   and there's really not a lot of sensible names you can give them anyway)
# These were already split up in a sensible manner, so there's no point to doing that again:
for file in listdir(join(args.prefix, "audio", "music")):
    mergegroup(scrapelabels(join(args.prefix, "audio", "music", file)))

# These scripts call upon asm that is only used here
mergegroup(scrapelabels(join(args.prefix, "engine", "events", "whiteout.asm")))

# DefaultMart doesn't need its own section despite being referenced through BANK()
mergegroup(["DefaultMart", "Marts"])

# BattleText_0x8188e is unused but belongs in BattleTexts
mergegroup(["BattleText_0x8188e", "BattleText_LinkErrorBattleCanceled"])

# These functions are empty and unused but _damn_
mergegroup(["Function823c6", "Function823c7", "Function82391"])

# The Egg assets _can_ all be in a different bank but there's really no reason to
mergegroup(["EggAnimation", "CelebiAnimation"])
mergegroup(["EggAnimationIdle", "CelebiAnimationIdle"])
mergegroup(["EggBitmasks", "CelebiBitmasks"])
mergegroup(["EggFrames", "CelebiFrames"])

# This function is only ever used by another one in the same bank, it doesn't need a separate section
mergegroup(["HDMATransfer_FillBGMap0WithBlack", "ReanchorBGMap_NoOAMUpdate"])
mergegroup(["CantCutScript", "TryCutOW"])
mergegroup(["SetMemEvent", "HiddenItemScript"])
mergegroup(["Script_JumpStdFromRAM", "CheckFacingTileForStdScript"])
mergegroup(["UnownDexATile", "UnownDexBTile", "_UnownPrinter"])
mergegroup(["Strings24f9a", "Function24fb2", "MenuData_0x24f91"])
mergegroup(["CardStatusGFX", "LeaderGFX", "LeaderGFX2", "BadgeGFX", "BadgeGFX2", "CardRightCornerGFX", "TrainerCard"])
mergegroup(["ChrisCardPic", "KrisCardPic", "CardGFX", "GetCardPic"])
mergegroup(["GameFreakLogo", "Copyright_GFPresents"])
mergegroup(["IntroGrass4GFX", "IntroScene15", "IntroScene19"])
mergegroup(["MysteryGiftJP_GFX", "Function1057d7"])
mergegroup(["LinkCommsBorderGFX", "__LoadTradeScreenBorder", "LinkComms_LoadPleaseWaitTextboxBorderGFX"])
mergegroup(["GFX_171848", "Function170d02"])
mergegroup(["GBPrinterHPIcon", "GBPrinterLvIcon", "PrintPartyMonPage1"])

# These scripts may be BANK()-referenced but they really do belong here
mergegroup(["PhoneScript_JustTalkToThem", "UnknownScript_0x90669", "Function90199"])

# These unused things are related
mergegroup(["UnreferencedString_HourJP", "UnreferencedString_MinuteJP", "RestartClock"])


def unsplitfiles(file1, file2):
    # Make sure that functions in split files stay grouped together if they're referenced by the same things.

    group1 = set()
    group2 = set()

    labels1 = scrapelabels(join(args.prefix, file1))
    labels2 = scrapelabels(join(args.prefix, file2))

    for label in labels1:
        for ref in refs[label]:
            if ref in labels2:
                group1.add(label)
                group2.add(ref)

    for label in labels2:
        for ref in refs[label]:
            if ref in labels1:
                group2.add(label)
                group1.add(ref)

    mergegroup(list(group1))
    mergegroup(list(group2))

# SPLIT: Fix consequences of engine/pokemon/health.asm split
mergegroup(["AnimateHPBar", "ComputeHPBarPixels"])

# SPLIT: Fix consequences of enigne/battle/read_trainer_attributes.asm split
mergegroup(["GetTrainerClassName", "GetTrainerAttributes"])

# SPLIT: Fix consequences of mobile/mobile_22.asm and mobile/mobile_22_2.asm split
unsplitfiles("mobile/mobile_22.asm", "mobile/mobile_22_2.asm")

# SPLIT: Fix consequences of engine/events/happiness_egg.asm and engine/events/haircut.asm split
mergegroup(["GetFirstPokemonHappiness", "CheckFirstMonIsEgg", "ChangeHappiness"])

# SPLIT: Fix consequences of engine/pokemon/move_mon.asm and engine/pokemon/breedmon_level_growth.asm split
mergegroup(["GetBreedMon1LevelGrowth", "GetBreedMon2LevelGrowth"])

args.out.write(dumps(sort_groups(groups, True), indent=4))
