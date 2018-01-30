; WritePartyMenuTilemap.Jumptable indexes (see engine/party_menu.asm)
	const_def
	const PARTYMENUQUALITY_NICKNAMES
	const PARTYMENUQUALITY_HP_BAR
	const PARTYMENUQUALITY_HP_DIGITS
	const PARTYMENUQUALITY_LEVEL
	const PARTYMENUQUALITY_STATUS
	const PARTYMENUQUALITY_TMHM_COMPAT
	const PARTYMENUQUALITY_EVO_STONE_COMPAT
	const PARTYMENUQUALITY_GENDER

partymenuqualities: MACRO
rept _NARG
	db PARTYMENUQUALITY_\1
shift
endr
	db -1 ; end
ENDM


PartyMenuQualityPointers: ; 503b2
; entries correspond to PARTYMENUACTION_* constants
	dw .Default  ; PARTYMENUACTION_CHOOSE_POKEMON
	dw .Default  ; PARTYMENUACTION_HEALING_ITEM
	dw .Default  ; PARTYMENUACTION_SWITCH
	dw .TMHM     ; PARTYMENUACTION_TEACH_TMHM
	dw .Default  ; PARTYMENUACTION_MOVE
	dw .EvoStone ; PARTYMENUACTION_EVO_STONE
	dw .Gender   ; PARTYMENUACTION_GIVE_MON
	dw .Default  ; PARTYMENUACTION_GIVE_ITEM
; 503c6

.Default:  partymenuqualities NICKNAMES, HP_BAR, HP_DIGITS, LEVEL, STATUS
.TMHM:     partymenuqualities NICKNAMES, TMHM_COMPAT,       LEVEL, STATUS
.EvoStone: partymenuqualities NICKNAMES, EVO_STONE_COMPAT,  LEVEL, STATUS
.Gender:   partymenuqualities NICKNAMES, GENDER,            LEVEL, STATUS
; 503e0
