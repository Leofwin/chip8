import unittest
import sys
import os

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             os.path.pardir))

import screen


class ScreenTest(unittest.TestCase):
    def setUp(self):
        self.screen = screen.Screen()

    def try_catch_exception_when_execute_operation(self, command, exception, *args):
        try:
            command(*args)
            self.assertTrue(False)
        except exception:
            self.assertTrue(True)
        except Exception:
            self.assertTrue(False)

    def test_set_value__if_negative_x__exception(self):
        self.try_catch_exception_when_execute_operation(
            self.screen.set_value,
            screen.InvalidCoordinatesException,
            -2, 5, 1
        )

    def test_set_value__if_negative_y__exception(self):
        self.try_catch_exception_when_execute_operation(
            self.screen.set_value,
            screen.InvalidCoordinatesException,
            4, -5, 1
        )

    def test_set_value__if_x_more_than_width__exception(self):
        self.try_catch_exception_when_execute_operation(
            self.screen.set_value,
            screen.InvalidCoordinatesException,
            68, 4, 1
        )

    def test_set_value__if_y_more_than_height__exception(self):
        self.try_catch_exception_when_execute_operation(
            self.screen.set_value,
            screen.InvalidCoordinatesException,
            5, 33, 1
        )

    def test_set_value__if_x_y_out_of_size__exception(self):
        self.try_catch_exception_when_execute_operation(
            self.screen.set_value,
            screen.InvalidCoordinatesException,
            500, 4000, 1
        )

    def test_set_value__if_value_not_one_or_zero__exception(self):
        self.try_catch_exception_when_execute_operation(
            self.screen.set_value,
            ValueError,
            4, 5, 12
        )

    def test_set_value__if_exist_coordinate_and_one_value__set_needed_value(self):
        x = 5
        y = 4
        value = 1

        self.screen.set_value(x, y, value)

        index = y * self.screen.height + x
        self.assertEqual(value, self.screen._screen[index])

    def test_decode_byte_to_pixels__if_byte_less_than_zero__exception(self):
        self.try_catch_exception_when_execute_operation(
            screen.Screen.decode_byte_to_pixels,
            ValueError,
            -20
        )

    def test_decode_byte_to_pixels__if_byte_more_than_255__exception(self):
        self.try_catch_exception_when_execute_operation(
            screen.Screen.decode_byte_to_pixels,
            ValueError,
            256
        )

    def test_decode_byte_to_pixels__if_correct_value__return_pixels(self):
        expected = [[0, 1, 0, 0, 1, 0, 0, 1], [1, 0, 0, 0, 0, 1, 0, 1]]
        values = [0x49, 0x85]

        for i in range(len(values)):
            actual = screen.Screen.decode_byte_to_pixels(values[i])
            self.assertEqual(expected[i], actual)

    def test_get__index__if_negative_x__exception(self):
        self.try_catch_exception_when_execute_operation(
            self.screen._get_index,
            screen.InvalidCoordinatesException,
            -50, 4
        )

    def test_get__index__if_negative_y__exception(self):
        self.try_catch_exception_when_execute_operation(
            self.screen._get_index,
            screen.InvalidCoordinatesException,
            3, -4
        )

    def test_get__index__if_x_more_than_width__exception(self):
        self.try_catch_exception_when_execute_operation(
            self.screen._get_index,
            screen.InvalidCoordinatesException,
            68, 3
        )

    def test_get__index__if_y_more_than_height__exception(self):
        self.try_catch_exception_when_execute_operation(
            self.screen._get_index,
            screen.InvalidCoordinatesException,
            3, 37
        )

    def test_get__index__if_coordinate_more_than_size__exception(self):
        self.try_catch_exception_when_execute_operation(
            self.screen._get_index,
            screen.InvalidCoordinatesException,
            54, 37
        )

    def test_draw_sprite__if_not_intersect__false(self):
        data = bytearray(4)
        data[0] = 0b10000001
        data[1] = 0b00111001
        data[2] = 0b01010101
        data[3] = 0b10000011
        self.assertFalse(self.screen.draw_sprite(0, 0, data))

        expected = [
            [1, 0, 0, 0, 0, 0, 0, 1],
            [0, 0, 1, 1, 1, 0, 0, 1],
            [0, 1, 0, 1, 0, 1, 0, 1],
            [1, 0, 0, 0, 0, 0, 1, 1]
        ]

        for y, list in enumerate(expected):
            length = len(list)
            for x in range(length):
                self.assertEqual(
                    expected[y][x],
                    self.screen._screen[self.screen._get_index(x, y)]
                )


if __name__ == '__main__':
    unittest.main()
