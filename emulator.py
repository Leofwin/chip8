import random

import settings
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

        self.instructions = {
            0x0: self._op_0x0,
            0x00EE: self._op_0x00ee,
            0x1: self._op_0x1,
            0x2: self._op_0x2,
            0x3: self._op_0x3,
            0x4: self._op_0x4,
            0x6: self._op_0x6,
            0x7: self._op_0x7,
            0x8000: self._op_0x8__0,
            0x8002: self._op_0x8__2,
            0x8005: self._op_0x8__5,
            0xA: self._op_0xa,
            0xC: self._op_0xc,
            0xD: self._op_0xd,
            0xF00A: self._op_0xf_0a,
            0xF01E: self._op_0xf_1e,
            0xF055: self._op_0xf_55,
            0xF065: self._op_0xf_65
        }

    def reset(self):
        self.memory = memory.Memory()
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
        if not self.is_waiting_mode and opcode not in [0x1, 0x2, 0x00ee]:
            self._increase_memory_pointer()

    @staticmethod
    def parse_word(word):
        opcode = word >> 12
        args = []
        if word == 0x00e0 or word == 0x00ee:
            opcode = word
        elif opcode in {0xA, 0x1, 0x2, 0x0}:
            args.append(word & 0x0FFF)
        elif opcode == 0xD:
            for offset in range(2, -1, -1):
                mask = 0x000f << (offset * 4)
                args.append((word & mask) >> (offset * 4))
        elif opcode == 0x8:
            opcode = word & 0xF00F
            for offset in range(2, 0, -1):
                mask = 0x000f << (offset * 4)
                args.append((word & mask) >> (offset * 4))
        elif opcode == 0xf:
            opcode = word & 0xf0ff
            args.append((word & 0x0f00) >> 8)
        else:  # 0xC and 0x3 and 0x7 and 0x6 and 0x4
            args.append((word & 0x0F00) >> 8)
            args.append(word & 0x00FF)
        return opcode, args

    def _op_0xa(self, address):
        if address < 0 or address > self.memory.memory_size:
            raise ImpossibleOperationException()
        self.register_i = address

    def _op_0xc(self, register, byte):
        self.registers[register] = random.randint(0, 0xFF) & byte

    def _op_0x3(self, register, byte):
        if self.registers[register] == byte:
            self._increase_memory_pointer()

    def _op_0xd(self, vx, vy, bytes_count):
        data = self.memory.read(self.register_i, bytes_count)
        x = self.registers[vx]
        y = self.registers[vy]
        is_intersect = self.screen.draw_sprite(x, y, data)
        self.registers[0xF] = is_intersect

    def _op_0x7(self, vx, number):
        self.registers[vx] = (self.registers[vx] + number) % 256

    def _op_0x1(self, address):
        self.memory_pointer = address

    def _op_0x6(self, vx, number):
        self.registers[vx] = number

    def _op_0x8__0(self, vx, vy):
        self.registers[vx] = self.registers[vy]

    def _op_0x2(self, address):
        self._increase_memory_pointer()
        self.stack.append(self.memory_pointer)
        self.memory_pointer = address

    def _op_0xf_1e(self, vx):
        self.register_i += self.registers[vx]

    def _op_0xf_0a(self, vx):
        if self.pressed_button is None:
            self.is_waiting_mode = True
            return
        self.registers[vx] = self.pressed_button
        self.pressed_button = None
        self.is_waiting_mode = False

    def _op_0xf_55(self, x):
        data = bytearray(x + 1)
        for i in range(x + 1):
            data[i] = self.registers[i]
        self.memory.load_data(self.register_i, data)

    def _op_0x4(self, vx, number):
        if self.registers[vx] != number:
            self._increase_memory_pointer()

    def _op_0xf_65(self, x):
        data = self.memory.read(self.register_i, x + 1)

        for i in range(x + 1):
            self.registers[i] = data[i]

    def _op_0x8__2(self, vx, vy):
        self.registers[vx] = self.registers[vx] & self.registers[vy]

    def _op_0x8__5(self, vx, vy):
        value = self.registers[vx] - self.registers[vy]
        self.registers[0xF] = 1 if value >= 0 else 0
        self.registers[vx] = value % 256

    def _op_0x00ee(self):
        self.memory_pointer = self.stack.pop()

    def _op_0x0(self, address):
        pass
