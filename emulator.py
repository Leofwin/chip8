import random

import memory
import screen


class ImpossibleOperationException(Exception):
    pass


class Emulator:
    def __init__(self):
        self.screen = screen.Screen()
        self.memory = memory.Memory()
        self.registers = bytearray(16)

        self.stack = []

        self.stack_counter = 0
        self.memory_pointer = 0x200
        self.register_i = 0x200

        self.delay_timer = 0
        self.sound_timer = 0

        self.is_waiting_mode = False
        self.pressed_button = None

        self.font = [
            0xF0, 0x90, 0x90, 0x90, 0xF0,
            0x20, 0x60, 0x20, 0x20, 0x70,
            0xF0, 0x10, 0xF0, 0x80, 0xF0,
            0xF0, 0x10, 0xF0, 0x10, 0xF0,
            0x90, 0x90, 0xF0, 0x10, 0x10,
            0xF0, 0x80, 0xF0, 0x10, 0xF0,
            0xF0, 0x80, 0xF0, 0x90, 0xF0,
            0xF0, 0x10, 0x20, 0x40, 0x40,
            0xF0, 0x90, 0xF0, 0x90, 0xF0,
            0xF0, 0x90, 0xF0, 0x10, 0xF0,
            0xF0, 0x90, 0xF0, 0x90, 0x90,
            0xE0, 0x90, 0xE0, 0x90, 0xE0,
            0xF0, 0x80, 0x80, 0x80, 0xF0,
            0xE0, 0x90, 0x90, 0x90, 0xE0,
            0xF0, 0x80, 0xF0, 0x80, 0xF0,
            0xF0, 0x80, 0xF0, 0x80, 0x80
        ]
        self._load_font_in_memory()

        self.instructions = {
            0x0: self._op_0x0,
            0x00E0: self._op_0x00e0,
            0x00EE: self._op_0x00ee,
            0x1: self._op_0x1,
            0x2: self._op_0x2,
            0x3: self._op_0x3,
            0x4: self._op_0x4,
            0x5000: self._op_0x5__0,
            0x6: self._op_0x6,
            0x7: self._op_0x7,
            0x8000: self._op_0x8__0,
            0x8001: self._op_0x8__1,
            0x8002: self._op_0x8__2,
            0x8003: self._op_0x8__3,
            0x8004: self._op_0x8__4,
            0x8005: self._op_0x8__5,
            0x8006: self._op_0x8__6,
            0x8007: self._op_0x8__7,
            0x800e: self._op_0x8__e,
            0x9000: self._op_0x9__0,
            0xA: self._op_0xa,
            0xB: self._op_0xb,
            0xC: self._op_0xc,
            0xD: self._op_0xd,
            0xE09E: self._op_0xe_9e,
            0xE0A1: self._op_0xe_a1,
            0xF007: self._op_0xf_07,
            0xF00A: self._op_0xf_0a,
            0xF015: self._op_0xf_15,
            0xF018: self._op_0xf_18,
            0xF01E: self._op_0xf_1e,
            0xF029: self._op_0xf_29,
            0xF033: self._op_0xf_33,
            0xF055: self._op_0xf_55,
            0xF065: self._op_0xf_65
        }

    def reset(self):
        self.memory.reset()
        self.screen.reset()
        self.registers = bytearray(16)

        self.stack = []
        self.stack_counter = 0
        self.memory_pointer = 0x200
        self.register_i = 0x200
        self.delay_timer = 0
        self.sound_timer = 0

        self.is_waiting_mode = False
        self.pressed_button = None

    def degrease_timers_if_need(self):
        if self.delay_timer > 0:
            self.delay_timer -= 1
        if self.sound_timer > 0:
            self.sound_timer -= 1

    def _load_font_in_memory(self):
        for index, byte in enumerate(self.font):
            self.memory.write_byte(index, byte)

    def load_file_in_memory(self, file_name):
        try:
            with open(file_name, 'rb') as f:
                data = f.read()
        except Exception:
            raise BlockingIOError("Can't read a file {}".format(file_name))

        self.memory.load_data(self.memory_pointer, data)

    def _increase_memory_pointer(self):
        self.memory_pointer += 0x2

    def _skip_next_instruction(self):
        self.memory_pointer += 0x4

    def make_tact(self):
        word = self.memory.read_opcode(self.memory_pointer)
        opcode, args = Emulator.parse_word(word)

        self.execute_instruction(opcode, args)

    def execute_instruction(self, opcode, args):
        if opcode not in self.instructions:
            raise ImpossibleOperationException()

        self.instructions[opcode](*args)

        # if not keypress waiting mode,
        # increase memory pointer to all commands except commands
        # which are changing memory pointer
        if not self.is_waiting_mode and opcode not in [0x1, 0xB, 0x2, 0x00ee]:
            self._increase_memory_pointer()

    @staticmethod
    def parse_word(word):
        opcode = word >> 12
        args = []
        if word == 0x00e0 or word == 0x00ee:
            opcode = word
        elif opcode in {0xA, 0x1, 0x2, 0x0, 0xB}:
            args.append(word & 0x0FFF)
        elif opcode == 0xD:
            for offset in range(2, -1, -1):
                mask = 0x000f << (offset * 4)
                args.append((word & mask) >> (offset * 4))
        elif opcode == 0x8 or opcode == 0x5 or opcode == 0x9:
            opcode = word & 0xF00F
            for offset in range(2, 0, -1):
                mask = 0x000f << (offset * 4)
                args.append((word & mask) >> (offset * 4))
        elif opcode == 0xf or opcode == 0xe:
            opcode = word & 0xf0ff
            args.append((word & 0x0f00) >> 8)
        else:  # 0xC and 0x3 and 0x7 and 0x6 and 0x4
            args.append((word & 0x0F00) >> 8)
            args.append(word & 0x00FF)
        return opcode, args

    @staticmethod
    def get_byte_in_bcd_format(number):
        if number < 0 or number >= 256:
            raise ValueError("Number should be more than zero and less than 256")

        hundreds = number // 100
        tens = (number // 10) % 10
        ones = number % 10

        return [hundreds, tens, ones]

    def _op_0x0(self, address):
        pass

    def _op_0x00e0(self):
        self.screen.reset()

    def _op_0x00ee(self):
        self.memory_pointer = self.stack.pop()

    def _op_0x1(self, address):
        self.memory_pointer = address

    def _op_0x2(self, address):
        self._increase_memory_pointer()
        self.stack.append(self.memory_pointer)
        self.memory_pointer = address

    def _op_0x3(self, x, byte):
        if self.registers[x] == byte:
            self._increase_memory_pointer()

    def _op_0x4(self, x, number):
        if self.registers[x] != number:
            self._increase_memory_pointer()

    def _op_0x5__0(self, x, y):
        if self.registers[x] == self.registers[y]:
            self._increase_memory_pointer()

    def _op_0x6(self, x, number):
        self.registers[x] = number

    def _op_0x7(self, x, number):
        self.registers[x] = (self.registers[x] + number) % 256

    def _op_0x8__0(self, x, y):
        self.registers[x] = self.registers[y]

    def _op_0x8__1(self, x, y):
        self.registers[x] |= self.registers[y]

    def _op_0x8__2(self, x, y):
        self.registers[x] &= self.registers[y]

    def _op_0x8__3(self, x, y):
        self.registers[x] ^= self.registers[y]

    def _op_0x8__4(self, x, y):
        value = self.registers[x] + self.registers[y]
        self.registers[0xF] = value // 256
        self.registers[x] = value % 256

    def _op_0x8__5(self, x, y):
        value = self.registers[x] - self.registers[y]
        self.registers[0xF] = 1 if value >= 0 else 0
        self.registers[x] = value % 256

    def _op_0x8__6(self, x, y):
        self.registers[0xF] = self.registers[x] & 0b1
        self.registers[x] = (self.registers[x] >> 1)

    def _op_0x8__7(self, x, y):
        value = self.registers[y] - self.registers[x]
        self.registers[x] = value % 256
        self.registers[0xF] = 0 if value < 0 else 1

    def _op_0x8__e(self, x, y):
        self.registers[0xF] = (self.registers[x] & (0b1 << 7)) >> 7
        self.registers[x] = (self.registers[x] << 1)

    def _op_0x9__0(self, x, y):
        if self.registers[x] != self.registers[y]:
            self._increase_memory_pointer()

    def _op_0xa(self, address):
        if address < 0 or address > self.memory.memory_size:
            raise ImpossibleOperationException()
        self.register_i = address

    def _op_0xb(self, address):
        self.memory_pointer = address + self.registers[0]

    def _op_0xc(self, register, byte):
        self.registers[register] = random.randint(0, 0xFF) & byte

    def _op_0xd(self, x, y, bytes_count):
        data = self.memory.read(self.register_i, bytes_count)
        start_x = self.registers[x]
        start_y = self.registers[y]
        is_intersect = self.screen.draw_sprite(start_x, start_y, data)
        self.registers[0xF] = is_intersect

    def _op_0xe_9e(self, x):
        if self.pressed_button == self.registers[x]:
            self._increase_memory_pointer()

    def _op_0xe_a1(self, x):
        if self.pressed_button != self.registers[x]:
            self._increase_memory_pointer()

    def _op_0xf_07(self, x):
        self.registers[x] = self.delay_timer

    def _op_0xf_0a(self, x):
        if self.pressed_button is None:
            self.is_waiting_mode = True
            return
        self.registers[x] = self.pressed_button
        self.pressed_button = None
        self.is_waiting_mode = False

    def _op_0xf_15(self, x):
        self.delay_timer = self.registers[x]

    def _op_0xf_18(self, x):
        self.sound_timer = self.registers[x]

    def _op_0xf_1e(self, x):
        value = self.register_i + self.registers[x]
        self.register_i = (value) % 4096
        self.registers[0xF] = value // 4096

    def _op_0xf_29(self, x):
        self.register_i = self.registers[x] * 5

    def _op_0xf_33(self, x):
        bcd_format = Emulator.get_byte_in_bcd_format(self.registers[x])

        for i in range(len(bcd_format)):
            self.memory.write_byte(self.register_i + i, bcd_format[i])

    def _op_0xf_55(self, x):
        data = bytearray(x + 1)
        for i in range(x + 1):
            data[i] = self.registers[i]
        self.memory.load_data(self.register_i, data)

    def _op_0xf_65(self, x):
        data = self.memory.read(self.register_i, x + 1)

        for i in range(x + 1):
            self.registers[i] = data[i]
