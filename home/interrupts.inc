; Game Boy hardware interrupts

SECTION "home/interrupts.inc@vblank", ROM0[$0040]
int_vblank:
	jp VBlank

SECTION "home/interrupts.inc@lcd", ROM0[$0048]
int_lcd:
	jp LCD

SECTION "home/interrupts.inc@timer", ROM0[$0050]
int_timer:
	jp Timer

SECTION "home/interrupts.inc@serial", ROM0[$0058]
int_serial:
	jp Serial

SECTION "home/interrupts.inc@joypad", ROM0[$0060]
int_joypad:
	jp JoypadInt
