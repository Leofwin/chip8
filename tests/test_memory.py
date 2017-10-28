import unittest
import sys
import os

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             os.path.pardir))

import memory


class MemoryTest(unittest.TestCase):
    def setUp(self):
        self.memory = memory.Memory()

    def try_catch_exception_when_execute_operation(self, command, exception, *args):
        try:
            command(*args)
            self.assertTrue(False)
        except exception:
            self.assertTrue(True)
        except Exception:
            self.assertTrue(False)

    def test_read__if_negative_length__exception(self):
        self.try_catch_exception_when_execute_operation(
            self.memory.read,
            memory.IncorrectAddressException,
            5, -2
        )

    def test_read__if_negative_address__exception(self):
        self.try_catch_exception_when_execute_operation(
            self.memory.read,
            memory.IncorrectAddressException,
            -2, 5
        )

    def test_read__if_start_address_more_than_memory_size__exception(self):
        self.try_catch_exception_when_execute_operation(
            self.memory.read,
            memory.IncorrectAddressException,
            5012, 5
        )

    def test_read__if_end_address_more_than_memory_size__exception(self):
        self.try_catch_exception_when_execute_operation(
            self.memory.read,
            memory.IncorrectAddressException,
            3012, 2048
        )

    def test_read__existing_part_of_memory__return_this_part(self):
        expected = bytearray(0x212 - 0x205)
        for i in range(0x205, 0x212, 1):
            expected[i - 0x205] = i - 0x205
            self.memory._memory[i] = i - 0x205

        actual = self.memory.read(0x205, 0x212 - 0x205)
        self.assertEqual(expected, actual)


if __name__ == '__main__':
    unittest.main()
