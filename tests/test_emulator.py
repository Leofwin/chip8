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

    def test_parse_word__if_0xA_0x2_0x1(self):
        words = [0xA123, 0x1456, 0x2abc]
        expected = [(0xA, [0x123]), (0x1, [0x456]), (0x2, [0xabc])]

        for i in range(len(words)):
            opcode, args = emulator.Emulator.parse_word(words[i])
            self.assertEqual(expected[i][0], opcode)
            self.assertEqual(expected[i][1], args)

    def test_parse_word__if_0xD(self):
        words = [0xD123, 0xD456]
        expected = [(0xD, [0x1, 0x2, 0x3]), (0xD, [0x4, 0x5, 0x6])]

        for i in range(len(words)):
            opcode, args = emulator.Emulator.parse_word(words[i])
            self.assertEqual(expected[i][0], opcode)
            self.assertEqual(expected[i][1], args)

    def test_parse_word__if_0x8(self):
        words = [0x8ab0, 0x8456]
        expected = [(0x8000, [0xa, 0xb]), (0x8006, [0x4, 0x5])]

        for i in range(len(words)):
            opcode, args = emulator.Emulator.parse_word(words[i])
            self.assertEqual(expected[i][0], opcode)
            self.assertEqual(expected[i][1], args)

    def test_parse_word__if_0xf(self):
        words = [0xfd07, 0xfe0a, 0xfc15, 0xfb18, 0xf129, 0xf533]
        expected = [(0xf007, [0xd]), (0xf00a, [0xe]), (0xf015, [0xc]), (0xf018, [0xb]),
                    (0xf029, [0x1]), (0xf033, [0x5])]

        for i in range(len(words)):
            opcode, args = emulator.Emulator.parse_word(words[i])
            self.assertEqual(expected[i][0], opcode)
            self.assertEqual(expected[i][1], args)

    def test_parse_word__if_0xc_0x3_0x7_0x6(self):
        words = [0xc493, 0x367e, 0x7ccc, 0x6ea4]
        expected = [(0xc, [0x4, 0x93]), (0x3, [0x6, 0x7e]),
                    (0x7, [0xc, 0xcc]), (0x6, [0xe, 0xa4])]

        for i in range(len(words)):
            opcode, args = emulator.Emulator.parse_word(words[i])
            self.assertEqual(expected[i][0], opcode)
            self.assertEqual(expected[i][1], args)

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
        self.chip_emulator.load_file_in_memory(settings.games_folder + file)

        self.assertEqual(data, self.chip_emulator.memory._memory[512:512+len(data)])

    def test_load_file__file_more_than_max_size__exception(self):
        file = "_test_file"
        try:
            self.chip_emulator.load_file_in_memory(settings.games_folder + file)
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

    '''def test_op_0xc__if_existing_address__change_selected_register_value(self):
        # не совсем понятно как тестировать, ибо внутри метода выбирается случайное число
        address = 0x5
        self.chip_emulator._op_0xc(address, 0x15)
        self.assertTrue(self.chip_emulator.registers[address] != 0)'''

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
        value = 0xdb
        self.chip_emulator._op_0x6(register_address, value)
        self.assertEqual(value, self.chip_emulator.registers[register_address])

    def test_op_0x8__0(self):
        vx = 0x9
        vy = 0xb
        value = 0xaa
        self.chip_emulator.registers[vy] = value
        self.chip_emulator._op_0x8__0(vx, vy)
        self.assertEqual(value, self.chip_emulator.registers[vy])

    def test_op_0xf_1e(self):
        self.chip_emulator.register_i = 14
        register = 0xa
        self.chip_emulator.registers[register] = 0x15
        expected = self.chip_emulator.register_i + self.chip_emulator.registers[register]

        self.chip_emulator._op_0xf_1e(0xa)
        self.assertEqual(expected, self.chip_emulator.register_i)

    def test_op_0xf_55(self):
        x = 5
        expected = bytearray(x + 1)
        for i in range(x + 1):
            self.chip_emulator.registers[i] = i
            expected[i] = i

        start_address = self.chip_emulator.register_i
        self.chip_emulator._op_0xf_55(x)
        for i in range(x + 1):
            self.assertEqual(
                expected[i],
                self.chip_emulator.memory.read_byte(start_address + i)
            )

    def test_op_0x4__if_different_values__increase_memory_pointer(self):
        number = 50
        address = 0x1
        self.chip_emulator.registers[address] = 45
        expected = self.chip_emulator.memory_pointer + 0x2

        self.chip_emulator._op_0x4(address, number)
        self.assertEqual(expected, self.chip_emulator.memory_pointer)

    def test_op_0x4__if_same_values__do_not_increase_memory_pointer(self):
        number = 50
        address = 0x1
        self.chip_emulator.registers[address] = number
        expected = self.chip_emulator.memory_pointer

        self.chip_emulator._op_0x4(address, number)
        self.assertEqual(expected, self.chip_emulator.memory_pointer)

    def test_op_0xf_65(self):
        data = [0x24, 0x65, 0xff, 0x74]
        start_address = 0x3ff
        self.chip_emulator.register_i = start_address

        for index, byte in enumerate(data):
            self.chip_emulator.memory.write_byte(start_address + index, byte)

        self.chip_emulator._op_0xf_65(len(data) - 1)

        for index, byte in enumerate(data):
            self.assertEqual(byte, self.chip_emulator.registers[index])

    def test_op_0x8__2(self):
        vx = 0xa
        vy = 0x5
        value_x = 0xef
        value_y = 0xdd
        expected = value_x & value_y
        self.chip_emulator.registers[vx] = value_x
        self.chip_emulator.registers[vy] = value_y

        self.chip_emulator._op_0x8__2(vx, vy)

        self.assertEqual(expected, self.chip_emulator.registers[vx])

    def test_op_0x8__5___if_vx_less_than_vy(self):
        vx = 0x5
        vy = 0x7
        value_x = 0x45
        value_y = 0x67
        expected = 256 + (value_x - value_y)

        self.chip_emulator.registers[vx] = value_x
        self.chip_emulator.registers[vy] = value_y

        self.chip_emulator._op_0x8__5(vx, vy)
        self.assertEqual(expected, self.chip_emulator.registers[vx])
        self.assertEqual(0, self.chip_emulator.registers[0xF])

    def test_op_0x8__5___if_vx_more_than_vy(self):
        vx = 0x5
        vy = 0x7
        value_x = 0x70
        value_y = 0x67
        expected = value_x - value_y

        self.chip_emulator.registers[vx] = value_x
        self.chip_emulator.registers[vy] = value_y

        self.chip_emulator._op_0x8__5(vx, vy)
        self.assertEqual(expected, self.chip_emulator.registers[vx])
        self.assertEqual(1, self.chip_emulator.registers[0xF])

    def test_op_0x8__5___if_vx_same_as_vy(self):
        vx = 0x5
        vy = 0x7
        value = 0x99

        self.chip_emulator.registers[vx] = value
        self.chip_emulator.registers[vy] = value

        self.chip_emulator._op_0x8__5(vx, vy)
        self.assertEqual(0, self.chip_emulator.registers[vx])
        self.assertEqual(1, self.chip_emulator.registers[0xF])

    def test_op_0x8__4___if_sum_more_than_byte__save_module_of_sum_and_raise_flag(self):
        vx = 0xa
        vy = 0x1
        value_x = 140
        value_y = 240
        self.chip_emulator.registers[vx] = value_x
        self.chip_emulator.registers[vy] = value_y
        expected_value = (value_x + value_y) % 256

        self.chip_emulator._op_0x8__4(vx, vy)
        self.assertEqual(expected_value, self.chip_emulator.registers[vx])
        self.assertEqual(1, self.chip_emulator.registers[0xF])

    def test_op_0x8__4___if_sum_less_than_byte__save_module_of_sum_and_set_carry_flag_is_zero(self):
        vx = 0xa
        vy = 0x1
        value_x = 140
        value_y = 110
        self.chip_emulator.registers[vx] = value_x
        self.chip_emulator.registers[vy] = value_y
        expected_value = (value_x + value_y) % 256

        self.chip_emulator._op_0x8__4(vx, vy)
        self.assertEqual(expected_value, self.chip_emulator.registers[vx])
        self.assertEqual(0, self.chip_emulator.registers[0xF])

    def test_get_byte_in_bcd_format__if_number_less_than_zero__exception(self):
        self.try_catch_exception_when_execute_operation(
            emulator.Emulator.get_byte_in_bcd_format,
            ValueError,
            -2
        )

    def test_get_byte_in_bcd_format__if_number_more_than_byte__exception(self):
        self.try_catch_exception_when_execute_operation(
            emulator.Emulator.get_byte_in_bcd_format,
            ValueError,
            1200
        )

    def test_get_byte_in_bcd_format__if_number_is_byte__exception(self):
        self.try_catch_exception_when_execute_operation(
            emulator.Emulator.get_byte_in_bcd_format,
            ValueError,
            256
        )

    def test_get_byte_in_bcd_format__if_correct_number__return_bcd_format(self):
        numbers = [240, 115]
        expected = [[0b10, 0b100, 0b0], [0b1, 0b1, 0b101]]

        for index, number in enumerate(numbers):
            actual = emulator.Emulator.get_byte_in_bcd_format(numbers[index])
            self.assertEqual(expected[index], actual)

    def test_op_0xf_33(self):
        vx = 0x4
        self.chip_emulator.registers[vx] = 249
        expected = [0b10, 0b100, 0b1001]

        self.chip_emulator._op_0xf_33(vx)

        for i in range(len(expected)):
            self.assertEqual(expected[i], self.chip_emulator.memory.read_byte(self.chip_emulator.register_i + i))

    def test_op_0xe_a1__if_different_values__increase_memory_pointer(self):
        x = 0xa
        expected = self.chip_emulator.memory_pointer + 0x2
        self.chip_emulator.registers[x] = 13
        self.chip_emulator.pressed_button = 0x2

        self.chip_emulator._op_0xe_a1(x)
        self.assertEqual(expected, self.chip_emulator.memory_pointer)

    def test_op_0xe_a1__if_same_values__increase_memory_pointer(self):
        x = 0xa
        value = 0xd
        expected = self.chip_emulator.memory_pointer
        self.chip_emulator.registers[x] = value
        self.chip_emulator.pressed_button = value

        self.chip_emulator._op_0xe_a1(x)
        self.assertEqual(expected, self.chip_emulator.memory_pointer)

    def test_op_0x8__3__change_vx_value(self):
        x = 0x3
        y = 0x7
        value_x = 240
        value_y = 255
        expected = value_x ^ value_y
        self.chip_emulator.registers[x] = value_x
        self.chip_emulator.registers[y] = value_y

        self.chip_emulator._op_0x8__3(x, y)

        self.assertEqual(expected, self.chip_emulator.registers[x])

    def test_op_0x5__0___if_same_values__increase_memory_pointer(self):
        x = 0xE
        y = 0xA
        value = 196
        self.chip_emulator.registers[x] = value
        self.chip_emulator.registers[y] = value
        expected = self.chip_emulator.memory_pointer + 0x2

        self.chip_emulator._op_0x5__0(x, y)

        self.assertEqual(expected, self.chip_emulator.memory_pointer)

    def test_op_0x5__0___if_different_values__do_not_increase_memory_pointer(self):
        x = 0xE
        y = 0xA
        value_x = 196
        value_y = 216
        self.chip_emulator.registers[x] = value_x
        self.chip_emulator.registers[y] = value_y
        expected = self.chip_emulator.memory_pointer

        self.chip_emulator._op_0x5__0(x, y)

        self.assertEqual(expected, self.chip_emulator.memory_pointer)

    def test_op_0x8__1(self):
        x = 0x5
        y = 0x2
        value_x = 240
        value_y = 255
        expected = value_x | value_y
        self.chip_emulator.registers[x] = value_x
        self.chip_emulator.registers[y] = value_y

        self.chip_emulator._op_0x8__1(x, y)

        self.assertEqual(expected, self.chip_emulator.registers[x])

    def test_op_0x8__6___if_least_significant_bit_is_zero__save_shift(self):
        x = 0x4
        y = 0x7
        value = 0b10001000
        self.chip_emulator.registers[y] = value
        expected = value > 1

        self.chip_emulator._op_0x8__6(x, y)

        self.assertEqual(expected, self.chip_emulator.registers[x])
        self.assertEqual(0, self.chip_emulator.registers[0xF])

    def test_op_0x8__6___if_least_significant_bit_is_one__save_shift_and_raise_flag(self):
        x = 0x2
        y = 0x9
        value = 0b10111001
        self.chip_emulator.registers[y] = value
        expected = value > 1

        self.chip_emulator._op_0x8__6(x, y)

        self.assertEqual(expected, self.chip_emulator.registers[x])
        self.assertEqual(1, self.chip_emulator.registers[0xF])

    def test_op_0x8__e___if_most_significant_bit_is_zero__save_shift(self):
        x = 0xa
        y = 0xe
        value = 0b1001000
        self.chip_emulator.registers[y] = value
        expected = value << 1

        self.chip_emulator._op_0x8__e(x, y)

        self.assertEqual(expected, self.chip_emulator.registers[x])
        self.assertEqual(0, self.chip_emulator.registers[0xF])

    def test_op_0x8__e___if_most_significant_bit_is_one__save_shift_and_raise_flag(self):
        x = 0x1
        y = 0x3
        value = 0b10111001
        self.chip_emulator.registers[y] = value
        expected = value < 1

        self.chip_emulator._op_0x8__e(x, y)

        self.assertEqual(expected, self.chip_emulator.registers[x])
        self.assertEqual(1, self.chip_emulator.registers[0xF])

    def test_op_0x8__7___if_vx_less_than_vy(self):
        vx = 0x5
        vy = 0x7
        value_x = 0x45
        value_y = 0x67
        expected = value_y - value_x

        self.chip_emulator.registers[vx] = value_x
        self.chip_emulator.registers[vy] = value_y

        self.chip_emulator._op_0x8__7(vx, vy)
        self.assertEqual(expected, self.chip_emulator.registers[vx])
        self.assertEqual(1, self.chip_emulator.registers[0xF])

    def test_op_0x8__7___if_vx_more_than_vy(self):
        vx = 0x5
        vy = 0x7
        value_x = 0x70
        value_y = 0x67
        expected = 256 + (value_y - value_x)

        self.chip_emulator.registers[vx] = value_x
        self.chip_emulator.registers[vy] = value_y

        self.chip_emulator._op_0x8__7(vx, vy)
        self.assertEqual(expected, self.chip_emulator.registers[vx])
        self.assertEqual(0, self.chip_emulator.registers[0xF])

    def test_op_0x8__7___if_vx_same_as_vy(self):
        vx = 0x5
        vy = 0x7
        value = 0x99

        self.chip_emulator.registers[vx] = value
        self.chip_emulator.registers[vy] = value

        self.chip_emulator._op_0x8__7(vx, vy)
        self.assertEqual(0, self.chip_emulator.registers[vx])
        self.assertEqual(1, self.chip_emulator.registers[0xF])

    def test_op_0x9__0__if_same_values__do_nothing(self):
        x = 0x6
        y = 0xe
        value = 15
        expected = self.chip_emulator.memory_pointer
        self.chip_emulator.registers[x] = value
        self.chip_emulator.registers[y] = value

        self.chip_emulator._op_0x9__0(x, y)

        self.assertEqual(expected, self.chip_emulator.memory_pointer)

    def test_op_0x9__0__if_different_values__increase_memory_pointer(self):
        x = 0x6
        y = 0xe
        value_x = 15
        value_y = 3
        expected = self.chip_emulator.memory_pointer + 0x2
        self.chip_emulator.registers[x] = value_x
        self.chip_emulator.registers[y] = value_y

        self.chip_emulator._op_0x9__0(x, y)

        self.assertEqual(expected, self.chip_emulator.memory_pointer)

    def test_op_0xb(self):
        value = 325
        self.chip_emulator.registers[0] = 16
        expected = self.chip_emulator.registers[0] + value

        self.chip_emulator._op_0xb(value)

        self.assertEqual(expected, self.chip_emulator.memory_pointer)

    def test_op_0xf_07(self):
        x = 5
        expected = 140
        self.chip_emulator.delay_timer = expected

        self.chip_emulator._op_0xf_07(x)

        self.assertEqual(expected, self.chip_emulator.registers[x])

    def test_op_0xf_15(self):
        x = 5
        expected = 240
        self.chip_emulator.registers[x] = expected

        self.chip_emulator._op_0xf_15(x)

        self.assertEqual(expected, self.chip_emulator.delay_timer)

    def test_op_0xf_18(self):
        x = 5
        expected = 3
        self.chip_emulator.registers[x] = expected

        self.chip_emulator._op_0xf_18(x)

        self.assertEqual(expected, self.chip_emulator.sound_timer)


if __name__ == '__main__':
    unittest.main()
