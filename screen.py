class InvalidCoordinatesException(Exception):
    """Ошибка при попытке обратиться к несуществующей координате"""
    pass


class Screen:
    def __init__(self):
        self.height = 32
        self.width = 64
        self.size = self.height * self.width

        self._screen = bytearray(self.size)

    def set_value(self, x, y, value):
        if x >= self.width or y >= self.height or x < 0 or y < 0:
            raise InvalidCoordinatesException()

        index = self._get_index(x, y)
        if index >= self.size:
            raise InvalidCoordinatesException()

        if value not in {0x0, 0x1}:
            raise ValueError("Value can be only 0 or 1")

        self._screen[index] = value

    def get_value(self, x, y):
        index = self._get_index(x, y)
        return self._screen[index]

    def reset(self):
        self._screen = bytearray(self.size)

    @staticmethod
    def decode_byte_to_pixels(byte):
        if byte < 0x0 or byte > 0xff:
            raise ValueError("Value must be more than 0 and less than 255")
        result = []

        for i in range(7, -1, -1):
            mask = 0b1 << i
            bit = (byte & mask) >> i
            result.append(bit)

        return result

    def _get_index(self, x, y):
        if x < 0 or y < 0 or x > self.width or y > self.height:
            raise InvalidCoordinatesException()
        result = y * self.width + x
        if result >= self.size:
            raise InvalidCoordinatesException()
        return result

    def draw_sprite(self, x, y, data):
        collision = False
        for y_offset, byte in enumerate(data):
            pixels = Screen.decode_byte_to_pixels(byte)

            for x_offset, pixel in enumerate(pixels):
                screen_x = (x + x_offset) % self.width
                screen_y = (y + y_offset) % self.height
                index = self._get_index(screen_x, screen_y)
                collision |= bool(self._screen[index] & pixel)
                self._screen[index] ^= pixel

        return collision
