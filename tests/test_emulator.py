import unittest
import sys
import os

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             os.path.pardir))

import emulator
import settings
import memory


class EmulatorTest(unittest.TestCase):
    def setUp(self):
        self.chip_emulator = emulator.Emulator()

    def try_catch_exception_when_execute_operation(self, command, exception, *args):
        try:
            command(*args)
            self.assertTrue(False)
        except exception:
            self.assertTrue(True)
        except Exception:
            self.assertTrue(False)

    def test_load_file__not_exist_file__exception(self):
        try:
            self.chip_emulator.load_file_in_memory("Ma1")
        except BlockingIOError:
            self.assertTrue(True)
        except Exception:
            self.assertTrue(False)

    def test_load_file__exist_file__fill_memory(self):
        file = "MAZE"
        with open(settings.games_folder + file, 'rb') as f:
            data = f.read()
        self.chip_emulator.load_file_in_memory(file)

        self.assertEqual(data, self.chip_emulator.memory._memory[512:512+len(data)])

    def test_load_file__file_more_than_max_size__exception(self):
        file = "_test_file"
        try:
            self.chip_emulator.load_file_in_memory(file)
            self.assertTrue(False)
        except memory.MemoryOverflowException:
            self.assertTrue(True)
        except Exception:
            self.assertTrue(False)

    def test_op_0xa__if_negative_address__exception(self):
        self.try_catch_exception_when_execute_operation(
            self.chip_emulator._op_0xa,
            emulator.ImpossibleOperationException,
            -30
        )

    def test_op_0xa__if_address_more_than_memory_size__exception(self):
        self.try_catch_exception_when_execute_operation(
            self.chip_emulator._op_0xa,
            emulator.ImpossibleOperationException,
            4097
        )

    def test_op_0xa__if_existing_address__change_register_address(self):
        address = 0x205
        self.chip_emulator._op_0xa(address)
        self.assertEqual(address, self.chip_emulator.register_i)

    def test_op_0xc__if_existing_address__change_selected_register_value(self):
        # не совсем понятно как тестировать, ибо внутри метода выбирается случайное число
        address = 0x5
        self.chip_emulator._op_0xc(address, 0x15)
        self.assertTrue(self.chip_emulator.registers[address] != 0)

    def test_op_0x3__if_values_are_same__increase_memory_pointer(self):
        address = 0x5
        byte = 0x15
        self.chip_emulator.registers[address] = byte
        original_value = self.chip_emulator.memory_pointer
        self.chip_emulator._op_0x3(address, byte)
        self.assertEqual(original_value + 0x2, self.chip_emulator.memory_pointer)

    def test_op_0x3__if_values_are_different__do_not_edit_memory_pointer(self):
        address = 0x5
        byte = 0x15
        self.chip_emulator.registers[address] = byte
        original_value = self.chip_emulator.memory_pointer
        self.chip_emulator._op_0x3(address, byte + 0x1)
        self.assertEqual(original_value, self.chip_emulator.memory_pointer)

    def test_op_0x7(self):
        register = 0xa
        prev_value = self.chip_emulator.registers[register]
        number = 50
        self.chip_emulator._op_0x7(register, number)
        self.assertEqual(prev_value + number, self.chip_emulator.registers[register])

    def test_op_0x1(self):
        address = 0xaf6
        self.chip_emulator._op_0x1(address)
        self.assertEqual(address, self.chip_emulator.memory_pointer)

    def test_op_0x6(self):
        register_address = 0xb
        value = 0xdbf
        self.chip_emulator._op_0x6(register_address, value)
        self.assertEqual(value, self.chip_emulator.registers[register_address])

    def test_op_0x8(self):
        vx = 0x9
        vy = 0xb
        value = 0xaaa
        self.chip_emulator.registers[vy] = value
        self.chip_emulator._op_0x8(vx, vy)
        self.assertEqual(value, self.chip_emulator.registers[vy])


if __name__ == '__main__':
    unittest.main()
