INCLUDE "constants/maps_common.inc"

	object_const_def ; object_event constants
	const ROUTE43MAHOGANYGATE_OFFICER


SECTION "maps/Route43MahoganyGate.asm", ROMX

Route43MahoganyGate_MapScripts::
	db 0 ; scene scripts

	db 0 ; callbacks

Route43MahoganyGateOfficer:
	faceplayer
	opentext
	checkevent EVENT_CLEARED_ROCKET_HIDEOUT
	iftrue .RocketsCleared
	writetext Route43MahoganyGateOfficerText
	waitbutton
	closetext
	end

.RocketsCleared:
	writetext Route43MahoganyGateOfficerRocketsClearedText
	waitbutton
	closetext
	end

Route43MahoganyGateOfficerText:
	text "Últimamente sólo"
	line "pasaban por aquí"

	para "los que iban al"
	line "LAGO DE LA FURIA."
	done

Route43MahoganyGateOfficerRocketsClearedText:
	text "Ahora nadie va al"
	line "LAGO DE LA FURIA."
	done

Route43MahoganyGate_MapEvents::
	db 0, 0 ; filler

	db 4 ; warp events
	warp_event  4,  0, ROUTE_43, 1
	warp_event  5,  0, ROUTE_43, 2
	warp_event  4,  7, MAHOGANY_TOWN, 5
	warp_event  5,  7, MAHOGANY_TOWN, 5

	db 0 ; coord events

	db 0 ; bg events

	db 1 ; object events
	object_event  0,  4, SPRITE_OFFICER, SPRITEMOVEDATA_STANDING_RIGHT, 0, 0, -1, -1, PAL_NPC_RED, OBJECTTYPE_SCRIPT, 0, Route43MahoganyGateOfficer, -1
