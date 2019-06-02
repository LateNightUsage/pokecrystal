INCLUDE "constants/maps_common.inc"

	object_const_def ; object_event constants
	const ROUTE5_POKEFAN_M


SECTION "maps/Route5.asm", ROMX

Route5_MapScripts::
	db 0 ; scene scripts

	db 0 ; callbacks

Route5PokefanMScript:
	jumptextfaceplayer Route5PokefanMText

Route5UndergroundPathSign:
	jumptext Route5UndergroundPathSignText

HouseForSaleSign:
	jumptext HouseForSaleSignText

Route5PokefanMText:
	text "La carretera está"
	line "cortada hasta que"

	para "arreglen la"
	line "CENTRAL ENERGÍA."
	done

Route5UndergroundPathSignText:
	text "VÍA SUBTERRÁNEA"

	para "CIUDAD CELESTE -"
	line "CIUDAD CARMÍN"
	done

HouseForSaleSignText:
	text "¿Qué es esto?"

	para "Casa en venta…"
	line "No vive nadie."
	done

Route5_MapEvents::
	db 0, 0 ; filler

	db 4 ; warp events
	warp_event 17, 15, ROUTE_5_UNDERGROUND_PATH_ENTRANCE, 1
	warp_event  8, 17, ROUTE_5_SAFFRON_GATE, 1
	warp_event  9, 17, ROUTE_5_SAFFRON_GATE, 2
	warp_event 10, 11, ROUTE_5_CLEANSE_TAG_HOUSE, 1

	db 0 ; coord events

	db 2 ; bg events
	bg_event 17, 17, BGEVENT_READ, Route5UndergroundPathSign
	bg_event 10, 11, BGEVENT_READ, HouseForSaleSign

	db 1 ; object events
	object_event 17, 16, SPRITE_POKEFAN_M, SPRITEMOVEDATA_STANDING_DOWN, 0, 0, -1, -1, PAL_NPC_RED, OBJECTTYPE_SCRIPT, 0, Route5PokefanMScript, EVENT_ROUTE_5_6_POKEFAN_M_BLOCKS_UNDERGROUND_PATH
