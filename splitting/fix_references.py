#!/usr/bin/env python3
# vim:set tabstop=4 shiftwidth=4 expandtab smarttab

# Keywords used in this file:
# - BLANKET: A label that has no real contents, but is used to group a bunch of other labels together
# - SPLIT: A label that references another directly crossing a bunch of unrelated stuff.

from json import loads, dumps
from os.path import join

from lib import read_symbols, scrapelabels

import argparse

parser = argparse.ArgumentParser()
parser.add_argument('input', type=argparse.FileType('r'))
parser.add_argument('output', type=argparse.FileType('w'))
parser.add_argument('-p', '--prefix', type=str, default="")
args = parser.parse_args()

refs = loads(args.input.read())
syms = read_symbols(open(join(args.prefix, "pokecrystal.sym")))

predefs = set()
for line in open(join(args.prefix, "data", "predef_pointers.inc")):
    if line.startswith("\tadd_predef "):
        predefs.add(line.strip().split(" ")[1].strip() + "Predef")

specials = set()
for line in open(join(args.prefix, "data", "special_pointers.inc")):
    if line.startswith("\tadd_special "):
        specials.add(line.strip().split(" ")[1].strip() + "Special")

maps = []
for line in open(join(args.prefix, "data", "maps", "attributes.asm")):
    if line.startswith("\tmap_attributes "):
        maps.append(line.strip().split(" ")[1].strip().split(",")[0].strip())

for symbol in refs:
    # BLANKET: BattleText
    # Calling StdBattleTextbox is an implicit BANK(BattleText)
    # FailText_CheckOpponentProtect is used in the same way
    # Also make sure anything referenced through this is in the same bank
    if "StdBattleTextbox" in refs[symbol] or "FailText_CheckOpponentProtect" in refs[symbol]:
        for x in refs[symbol]:
            if syms["BattleText"][0] == syms[x][0]:
                refs[symbol][x] = True
                refs["BattleText"][x] = False

    # BLANKET: BattleCore
    # ...ditto for CallBattleCore into BattleCore
    if "CallBattleCore" in refs[symbol]:
        for x in refs[symbol]:
            if syms["BattleCore"][0] == syms[x][0]:
                refs[symbol][x] = True
                refs["BattleCore"][x] = False

    # The `predef` and `special` macros will reference the tables and indexes without a BANK()
    # This is corrected in the table itself...
    if (symbol != "PredefPointers" and symbol != "SpecialsPointers" and
            symbol != "GetPredefPointer" and symbol != "Special" and
            symbol not in predefs and symbol not in specials):
        for x in refs[symbol]:
            if (x in predefs or x in specials or
                    x == "PredefPointers" or x == "SpecialsPointers"):
                refs[symbol][x] = True

    # GetSpriteMovementFunction may only be used from the same bank as SpriteMovementData
    if "GetSpriteMovementFunction" in refs[symbol]:
        refs["GetSpriteMovementFunction"]["SpriteMovementData"] = True
        if "SpriteMovementData" not in refs[symbol]:
            refs[symbol]["SpriteMovementData"] = False

    # GetMapPointer and GetAnyMapPointer may only be used from the same bank as MapGroupPointers
    for x in ["GetMapPointer", "GetAnyMapPointer"]:
        if x not in refs[symbol]:
            continue
        refs[x]["MapGroupPointers"] = True
        if "MapGroupPointers" not in refs[symbol]:
            refs[symbol]["MapGroupPointers"] = False

    # BattleCommandPointers point to the same bank as the user
    if "BattleCommandPointers" in refs[symbol]:
        for x in refs["BattleCommandPointers"]:
            refs["BattleCommandPointers"][x] = True
            if x not in symbol:
                refs[symbol][x] = False

    # Calling GetMoveAttr is an implicit BANK(Moves)
    if "GetMoveAttr" in refs[symbol]:
        if "Moves" in refs[symbol]:
            refs[symbol]["Moves"] = True

    # Calling GetBattleMonBackpic_DoAnim and GetEnemyFrontpic_DoAnim is an implicit BANK(BattleAnimCommands)
    for x in ["GetEnemyMonFrontpic_DoAnim", "GetBattleMonBackpic_DoAnim"]:
        if x not in refs[symbol]:
            continue
        # We just filter for the only two functions that are referenced in this manner
        for x in ["BattleAnimCmd_RaiseSub", "BattleAnimCmd_MinimizeOpp"]:
            if x not in refs[symbol]:
                continue
            refs[symbol][x] = True

# BLANKET: PokedexEntries1, PokedexEntries2, PokedexEntries3, PokedexEntries4
# PokedexDataPointerTable doesn't actually directly reference any entries.
# Instead, link each dex entry to its proper bank
for symbol in refs["PokedexDataPointerTable"]:
    refs["PokedexDataPointerTable"][symbol] = True
    for x in ["PokedexEntries%d" % (x + 1) for x in range(4)]:
        if syms[x][0] == syms[symbol][0]:
            refs[symbol][x] = False
            break

# BLANKET: KantoFrames, JohtoFrames
# ...ditto for FramesPointers
for symbol in refs["FramesPointers"]:
    refs["FramesPointers"][symbol] = True
    for x in ["KantoFrames", "JohtoFrames"]:
        if syms[x][0] == syms[symbol][0]:
            refs[symbol][x] = False
            break

# BLANKET: AIScoring
# AIScoringPointers points to things in the AIScoring bank
for symbol in refs["AIScoringPointers"]:
    refs["AIScoringPointers"][symbol] = True
    refs["AIScoring"][symbol] = False

# BLANKET: GBPrinterStrings
# PrinterStatusStringPointers points to things in the GBPrinterStrings bank
for symbol in refs["PrinterStatusStringPointers"]:
    refs["PrinterStatusStringPointers"][symbol] = True
    refs["GBPrinterStrings"][symbol] = False

# BLANKET: BattleTowerMons
# These labels aren't explicitly referenced but just exist for code aesthetics...
# Only BattleTowerMons1 and 2 are referenced directly.
for symbol in ["BattleTowerMons%d" % x for x in range(1, 11)]:
    if symbol in refs:
        refs["BattleTowerMons"][symbol] = False

for map in maps:
    attributes = map + "_MapAttributes"
    scripts = map + "_MapScripts"
    events = map + "_MapEvents"
    blocks = map + "_Blocks"

    # MapScripts and MapEvents are expected to be in the same bank
    refs[attributes][events] = True
    refs[scripts][events] = False

    # Any blocks other than its own are referenced through `connection`,
    # their bank being extracted through looking for the respective MapAttributes
    # through the `map_id` info
    for symbol in refs[attributes]:
        if symbol.endswith("_Blocks") and symbol != blocks:
            refs[attributes][symbol] = True

for symbol in refs["Tilesets"]:
    # TilesetAnim should be in same bank as _AnimateTileset
    if symbol.endswith("Anim"):
        refs["Tilesets"][symbol] = True
        refs["_AnimateTileset"][symbol] = False

    # TilesetPalettes should be in the same bank as SwapTextboxPalettes and ScrollBGMapPalettes
    if symbol.endswith("PalMap"):
        refs["Tilesets"][symbol] = True
        refs["SwapTextboxPalettes"][symbol] = False
        refs["ScrollBGMapPalettes"][symbol] = False

# Make sure PredefPointers and SpecialPointers link to their children properly
for symbol in predefs:
    refs["PredefPointers"][symbol] = False
for symbol in specials:
    refs["SpecialsPointers"][symbol] = False

# HeldStatUpItems points to things in the same bank as BattleCommand_AttackUp
for symbol in refs["HeldStatUpItems"]:
    refs["HeldStatUpItems"][symbol] = True
    refs["BattleCommand_AttackUp"][symbol] = False

# BattleCommand_TimeBasedHealContinue expects a couple of functions to be in the same bank as GetMaxHP
for symbol in ["Get%sMaxHP" % s for s in ["Half", "Quarter", "Eighth"]]:
    refs["BattleCommand_TimeBasedHealContinue"][symbol] = True
    refs["GetMaxHP"][symbol] = False

# Init expects WriteOAMDMACodeToHRAM to be in the same bank as GameInit
refs["Init"]["WriteOAMDMACodeToHRAM"] = True
refs["GameInit"]["WriteOAMDMACodeToHRAM"] = False

# OpenText and RefreshScreen expect LoadFonts_NoOAMUpdate to be in the same bank as ReanchorBGMap_NoOAMUpdate
refs["OpenText"]["LoadFonts_NoOAMUpdate"] = True
refs["RefreshScreen"]["LoadFonts_NoOAMUpdate"] = True
refs["ReanchorBGMap_NoOAMUpdate"]["LoadFonts_NoOAMUpdate"] = False

# ScrollingMenu expects _InitScrollingMenu to be in the same bank as _ScrollingMenu
refs["ScrollingMenu"]["_InitScrollingMenu"] = True
refs["_ScrollingMenu"]["_InitScrollingMenu"] = False

# PlayMusic expects _MapSetup_Sound_Off to be in the same bank as _PlayMusic
refs["PlayMusic"]["_MapSetup_Sound_Off"] = True
refs["_PlayMusic"]["_MapSetup_Sound_Off"] = False

# BattleCommand_Present expects AICheckEnemyMaxHP to be in the same bank as AICheckPlayerMaxHP
refs["BattleCommand_Present"]["AICheckEnemyMaxHP"] = True
refs["AICheckPlayerMaxHP"]["AICheckEnemyMaxHP"] = False

# PursuitSwitch expects DoEnemyTurn to be in the same bank as DoPlayerTurn
refs["PursuitSwitch"]["DoEnemyTurn"] = True
refs["DoPlayerTurn"]["DoEnemyTurn"] = False

# UseHeldStatusHealingItem expects CalcPlayerStats to be in the same bank as CalcEnemyStats
refs["UseHeldStatusHealingItem"]["CalcEnemyStats"] = True
refs["CalcPlayerStats"]["CalcEnemyStats"] = False

# ReadAnyMail expects FrenchGermanFont and SpanishItalianFont to be in the same bank as StandardEnglishFont
refs["ReadAnyMail"]["FrenchGermanFont"] = True
refs["ReadAnyMail"]["SpanishItalianFont"] = True
refs["StandardEnglishFont"]["FrenchGermanFont"] = False
refs["StandardEnglishFont"]["SpanishItalianFont"] = False

# These functions expect PokemonPalettes and TrainerPalettes to be in the same bank
refs["Function818f4"]["PokemonPalettes"] = True
refs["Function81911"]["TrainerPalettes"] = True
refs["Function81cc2"]["PokemonPalettes"] = True
refs["PokemonPalettes"]["TrainerPalettes"] = False

# GetMonAnimPointer expects the animations and idles to be in the same bank
refs["GetMonAnimPointer"]["AnimationIdlePointers"] = True
refs["AnimationPointers"]["AnimationIdlePointers"] = False
refs["GetMonAnimPointer"]["UnownAnimationIdlePointers"] = True
refs["UnownAnimationPointers"]["UnownAnimationIdlePointers"] = False

# GetCardPic expects ChrisCardPic and KrisCardPic to be in the same bank
refs["GetCardPic"]["KrisCardPic"] = True
refs["ChrisCardPic"]["KrisCardPic"] = False

# BANK(BattleAnimations) is referenced through the call to GetBattleAnimPointer...
refs["ClearBattleAnims"]["BattleAnimations"] = True

# These graphics aren't referenced through BANK() in one of the calls.
refs["GBCOnlyScreen"]["GBCOnlyGFX"] = False

# Fallthrouhgs
refs["ReadPartyMonMail"]["ReadAnyMail"] = False
refs["StatsScreen_LoadFont"]["LoadStatsScreenPageTilesGFX"] = False
refs["HandleNewMap"]["InitCommandQueue"] = False

# Not actual references (label is used in calculation)
refs["MysteryGift_CopyReceivedDecosToPC"]["DecorationIDs"] = True
refs["MysteryGift_CopyReceivedDecosToPC"]["TrophyIDs"] = True
refs["NamingScreen"]["KrisSpriteGFX"] = True
refs["SpecialAerodactylChamber"]["RuinsOfAlphAerodactylChamber_MapAttributes"] = True
refs["SpecialKabutoChamber"]["RuinsOfAlphKabutoChamber_MapAttributes"] = True

# Invalid references through unused code/data
refs["CheckObjectTime"]["CopyObjectStruct"] = True
refs["GetBaseData"]["UnknownEggPic"] = True
refs["InitList"]["ItemAttributes"] = True
refs["InitList"]["ItemNames"] = True
refs["InitList"]["PokemonNames"] = True
refs["NamesPointers"]["MoveDescriptions"] = True
refs["Unreferenced_Function241d5"]["AdvanceMobileInactivityTimerAndCheckExpired"] = True
refs["Unreferenced_Function241d5"]["HDMATransferTileMapToWRAMBank3"] = True
refs["Unused_PlaceEnemyHPLevel"]["CopyMonToTempMon"] = True # SPLIT
refs["Unused_PlaceEnemyHPLevel"]["DrawEnemyHP"] = True # SPLIT


def splitfiles(file1, file2):
    labels1 = scrapelabels(join(args.prefix, file1))
    labels2 = scrapelabels(join(args.prefix, file2))

    for label in labels1:
        for ref in refs[label]:
            if not refs[label][ref] and ref in labels2:
                refs[label][ref] = True

    for label in labels2:
        for ref in refs[label]:
            if not refs[label][ref] and ref in labels1:
                refs[label][ref] = True

# SPLIT: TiffanysFamilyMembers -> BrotherString (and co.)
for symbol in refs["TiffanysFamilyMembers"]:
    if not refs["TiffanysFamilyMembers"][symbol]:
        refs["TiffanysFamilyMembers"][symbol] = True

# SPLIT: Untangle engine/pokemon/health.asm from engine/battle/anim_hp_bar.asm
refs["AnimateHPBar"]["_AnimateHPBar"] = True
refs["_AnimateHPBar"]["ComputeHPBarPixels"] = True
refs["LongAnim_UpdateVariables"]["ComputeHPBarPixels"] = True
refs["LongHPBarAnim_UpdateTiles"]["ComputeHPBarPixels"] = True

# SPLIT: Untangle engine/battle/ai/items.asm from data/trainers/attributes.asm
refs["AI_SwitchOrTryItem"]["TrainerClassAttributes"] = True
refs["AI_TryItem"]["TrainerClassAttributes"] = True

# SPLIT: Untangle engine/pokemon/party_menu.asm from engine/pokemon/mon_stats.asm
refs["PlacePartyMonStatus"]["PlaceStatusString"] = True
refs["PlacePartyMonGender"]["GetGender"] = True

# SPLIT: There's a bunch of shit between these files with some useful things in the middle
splitfiles("mobile/mobile_22.asm", "mobile/mobile_22_2.asm")

# SPLIT: This copytilemapatonce is only used by engine/battle/battle_transition.asm
refs["DoBattleTransition"]["BattleStart_CopyTilemapAtOnce"] = True
refs["StartTrainerBattle_LoadPokeBallGraphics"]["BattleStart_CopyTilemapAtOnce"] = True

# SPLIT: Untangle engine/events/happiness_egg.asm from engine/events/haircut.asm
refs["GetFirstPokemonHappiness"]["CopyPokemonName_Buffer1_Buffer3"] = True
refs["CheckFirstMonIsEgg"]["CopyPokemonName_Buffer1_Buffer3"] = True
refs["HaircutOrGrooming"]["ChangeHappiness"] = True

# SPLIT: Untangle engine/pokemon/move_mon.asm from engine/pokemon/breedmon_level_growth.asm and engine/events/bug_contest/caught_mon.asm
refs["RetrieveMonFromDayCareMan"]["GetBreedMon1LevelGrowth"] = True
refs["RetrieveMonFromDayCareLady"]["GetBreedMon2LevelGrowth"] = True
refs["BugContest_SetCaughtContestMon"]["GeneratePartyMonStats"] = True

# SPLIT: Untangle engine/phone/phone.asm from engine/pokegear/pokegear.asm
refs["PokegearPhone_MakePhoneCall"]["Function90199"] = True
refs["PokegearPhone_UpdateDisplayList"]["Function90380"] = True

# SPLIT: Misc.
refs["MapObjectMovementPattern"]["CanObjectMoveInDirection"] = True
refs["ReanchorBGMap_NoOAMUpdate"]["ApplyBGMapAnchorToObjects"] = True
refs["GameInit"]["WriteOAMDMACodeToHRAM"] = True
refs["GiveItem"]["TryGiveItemToPartymon"] = True
refs["ComputeAIContestantScores"]["CheckBugContestContestantFlag"] = True
refs["Kurt_SelectQuantity_InterpretJoypad"]["BuySellToss_InterpretJoypad"] = True
refs["_DummyGame"]["ret_e00ed"] = True
refs["BugContestResultsWarpScript"]["Movement_ContestResults_WalkAfterWarp"] = True

# SPLIT: Acknowledged maps
refs["RuinsOfAlphKabutoChamberScientistScript"]["RuinsOfAlphResearchCenterScientist1Text_GotAllUnown"] = True
refs["Route36NationalParkGate_MapEvents"]["BugCatchingContestExplanationSign"] = True
refs["CeladonDeptStore6F_MapEvents"]["CeladonDeptStore1FElevatorButton"] = True
refs["TradeCenter_MapEvents"]["CableClubFriendScript"] = True
splitfiles("maps/BattleTower1F.asm", "maps/BattleTowerBattleRoom.asm")
splitfiles("maps/BattleTower1F.asm", "maps/BattleTowerElevator.asm")
splitfiles("maps/BattleTower1F.asm", "maps/BattleTowerHallway.asm")

# SPLIT: Acknowledged music
splitfiles("audio/music/wildpokemonvictory.asm", "audio/music/successfulcapture.asm")
splitfiles("audio/music/lookrival.asm", "audio/music/aftertherivalfight.asm")
splitfiles("audio/music/johtowildbattle.asm", "audio/music/johtowildbattlenight.asm")
splitfiles("audio/music/lookrocket.asm", "audio/music/rockettheme.asm")

args.output.write(dumps(refs, indent=4))
