class IncorrectAddressException(Exception):
    """Обращение к несуществующему адресу"""
    pass


class MemoryOverflowException(Exception):
    """"""
    pass


class Memory:
    def __init__(self):
        self.memory_size = 4096
        self._memory = bytearray(self.memory_size)

    def read_byte(self, address):
        if address < 0 or address >= self.memory_size:
            raise IncorrectAddressException()
        return self._memory[address]

    def write_byte(self, address, byte):
        if address < 0 or address >= self.memory_size:
            raise IncorrectAddressException()
        self._memory[address] = byte

    def load_data(self, start_address, data):
        if start_address < 0 or start_address >= self.memory_size:
            raise IncorrectAddressException()

        for offset, byte in enumerate(data):
            if start_address + offset >= self.memory_size:
                raise MemoryOverflowException()
            self._memory[start_address + offset] = byte

    def read_opcode(self, address):
        high_byte = self._memory[address] << 8
        low_byte = self._memory[address + 1]
        return high_byte + low_byte

    def read(self, start_address, length):
        if start_address < 0 or length < 0 or \
                start_address >= self.memory_size or \
                start_address + length >= self.memory_size:
            raise IncorrectAddressException()

        return self._memory[start_address:start_address + length]
