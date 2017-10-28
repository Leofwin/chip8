import logging
import random

import settings
import memory
import screen

logging.basicConfig(format=u'%(asctime)s [%(levelname)s <%(name)s>] %(message)s',
                    level=logging.DEBUG, filename=u'{0}'
                    .format(settings.log_file))


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

        self.instructions = {
            0xA: self._op_0xa,
            0xC: self._op_0xc,
            0x3: self._op_0x3,
            0xD: self._op_0xd,
            0x7: self._op_0x7,
            0x1: self._op_0x1,
            0x6: self._op_0x6,
            0x8: self._op_0x8
        }

    def load_file_in_memory(self, file_name):
        file_path = settings.games_folder + file_name
        try:
            with open(file_path, 'rb') as f:
                data = f.read()
        except Exception:
            raise BlockingIOError("Can't read a file {}".format(file_path))

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

        # increase memory pointer to all commands except commands
        # which are changing memory pointer
        if opcode not in [0x1, 0x2]:
            self._increase_memory_pointer()

    @staticmethod
    def parse_word(word):
        opcode = word >> 12
        args = []
        if opcode in {0xA, 0x1}:
            args.append(word & 0x0FFF)
        elif opcode == 0xD:
            for offset in range(2, -1, -1):
                mask = 0x000f << (offset * 4)
                args.append((word & mask) >> (offset * 4))
        elif opcode == 0x8:
            for offset in range(2, 0, -1):
                mask = 0x000f << (offset * 4)
                args.append((word & mask) >> (offset * 4))
        else: # 0xC and 0x3 and 0x7 and 0x6
            args.append((word & 0x0F00) >> 8)
            args.append(word & 0x00FF)
        return opcode, args

    def _op_0xa(self, address):
        if address < 0 or address > self.memory.memory_size:
            raise ImpossibleOperationException()
        self.register_i = address

    def _op_0xc(self, register, byte):
        self.registers[register] = random.randint(0, 255) & byte

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
        self.registers[vx] += number

    def _op_0x1(self, address):
        self.memory_pointer = address

    def _op_0x6(self, vx, number):
        self.registers[vx] = number

    def _op_0x8(self, vx, vy):
        self.registers[vx] = self.registers[vy]

    def _op_0x2(self, address):
        self._increase_memory_pointer()
        self.stack.append(self.memory_pointer)
        self.memory_pointer = address


if __name__ == '__main__':
    emulator = Emulator()
    emulator.load_file_in_memory("MAZE")
    for i in range(5):
        emulator.make_tact()
