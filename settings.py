import os

games_folder = os.path.dirname(__file__) + """/games/"""
sounds_folder = os.path.dirname(__file__) + """/sounds/"""
beep = "beep.wav"

window_title = "CHIP-8"
frequency = 1
timer_frequency = 60
pixel_size = 12
help_msg = '''CHIP-8 Emulator (версия 0.9)
Автор: Чуприлин Андрей <leofwin98@yandex.ru>'''

# blue colors
# active_color = "#D2D4E0"
# background_color = "#212435"

# beige colors
background_color = "#E9CB97"
active_color = "#AA967E"

# corall colors
# active_color = "#FE0002"
# background_color = "#FFCB99"

# standart colors
# active_color = "#008000"
# background_color = "#000000"

''' 
CHIP:		PC:
1 2 3 C		1 2 3 4
4 5 6 D		Q W E R
7 8 9 E		A S D F
A 0 B F		Z X C V
'''
key_codes = {49: 0x1, 50: 0x2, 51: 0x3, 52: 0xc,  # english letters
             81: 0x4, 87: 0x5, 69: 0x6, 82: 0xd,
             65: 0x7, 83: 0x8, 68: 0x9, 70: 0xe,
             90: 0xa, 88: 0x0, 67: 0xb, 86: 0xf,

             1049: 0x4, 1062: 0x5, 1059: 0x6, 1050: 0xd,  # russian letters
             1060: 0x7, 1067: 0x8, 1042: 0x9, 1040: 0xe,
             1071: 0xa, 1063: 0x0, 1057: 0xb, 1052: 0xf}
