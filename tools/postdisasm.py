import re

substrings = [
	(r"ldh \[hROMBank\], a\n\tld \[\$2100\], a", "bankswitch"),
	(r"ldh \[hSRAMBank\], a\n\tld \[\$4100\], a", "sramswitch"),
	(r"ldh \[hVRAMBank\], a\n\tldh \[rVBK\], a", "vramswitch"),
	(r"ldh \[hWRAMBank\], a\n\tldh \[rSVBK\], a", "wramswitch"),
	(r"ld a, \$00\n\tldh \[hSRAMEnabled\], a\n\tld \[\$100\], a", "disable_sram"),
	(r"ld a, \$0a\n\tldh \[hSRAMEnabled\], a\n\tld \[\$100\], a", "enable_sram"),
]

def substitute_bgcoords(m):
	reg = m[1]
	addr = int(m[2], 16)
	which_map = ""
	if addr < 0x9c00:
		which_map = ""
		addr -= 0x9800
	else:
		which_map = ", v0BGMap1"
		addr -= 0x9c00
	y = addr // 0x20
	x = addr % 0x20
	return f"{reg}bgcoord {x}, {y}{which_map}"

def substitute_ldcoord_a(m):
	addr = int(m[1], 16)
	which_map = ""
	if addr < 0x9c00:
		which_map = ""
		addr -= 0x9800
	else:
		which_map = ", v0BGMap1"
		addr -= 0x9c00
	y = addr // 0x20
	x = addr % 0x20
	return f"ldcoord_a {x}, {y}{which_map}"

def substitute_lda_coord(m):
	addr = int(m[1], 16)
	which_map = ""
	if addr < 0x9c00:
		which_map = ""
		addr -= 0x9800
	else:
		which_map = ", v0BGMap1"
		addr -= 0x9c00
	y = addr // 0x20
	x = addr % 0x20
	return f"lda_coord {x}, {y}{which_map}"

def substitute_vram(m):
	reg = m[1]
	addr = int(m[2], 16)
	which_map = ""
	if addr >= 0x9000:
		which_map = "v0Tiles2"
		addr -= 0x9000
	elif addr >= 0x8800:
		which_map = "v0Tiles1"
		addr -= 0x8800
	else:
		which_map = "v0Tiles0"
		addr -= 0x8000
	tile = addr // 0x10
	return f"ld {reg}, {which_map} tile ${tile:02x}"

def process(body):
	for pattern, repl in substrings:
		body = re.sub(pattern, repl, body)

	body = re.sub(r"ld (hl|bc|de), \$(9[89a-f][a-f0-9]{2})", substitute_bgcoords, body)
	body = re.sub(r"ld \[\$(9[89a-f][a-f0-9]{2})\], a", substitute_ldcoord_a, body)
	body = re.sub(r"ld a, \[\$(9[89a-f][a-f0-9]{2})\]", substitute_lda_coord, body)
	body = re.sub(r"ld (hl|bc|de), \$([89][a-f0-9]{3})", substitute_vram, body)
	
	# unnecessary address comments
	body = re.sub(r"; 0x(.+)\n(\nFunc_\1:)", lambda m: m[2], body)

	return body
