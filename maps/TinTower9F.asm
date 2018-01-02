const_value set 2
	const TINTOWER9F_POKE_BALL

TinTower9F_MapScriptHeader:
.SceneScripts:
	db 0

.MapCallbacks:
	db 0

TinTower9FHPUp:
	itemball HP_UP

TinTower9F_MapEventHeader:
	; filler
	db 0, 0

.Warps:
	db 7
	warp_def 12, 3, 2, TIN_TOWER_8F
	warp_def 2, 5, 3, TIN_TOWER_8F
	warp_def 12, 7, 4, TIN_TOWER_8F
	warp_def 7, 9, 1, TIN_TOWER_ROOF
	warp_def 16, 7, 5, TIN_TOWER_7F
	warp_def 6, 13, 5, TIN_TOWER_8F
	warp_def 8, 13, 6, TIN_TOWER_8F

.CoordEvents:
	db 0

.BGEvents:
	db 0

.ObjectEvents:
	db 1
	object_event 9, 1, SPRITE_POKE_BALL, SPRITEMOVEDATA_ITEM_TREE, 0, 0, -1, -1, 0, OBJECTTYPE_ITEMBALL, 0, TinTower9FHPUp, EVENT_TIN_TOWER_9F_HP_UP
