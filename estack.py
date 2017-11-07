class StackOverflowException(Exception):
    """Переполнение стэка"""
    pass


class Stack:
    def __init__(self):
        self.max_length = 16
        self.stack_pointer = 0
        self._stack = []
        for i in range(self.max_length):
            self._stack.append(0)

    def push(self, value):
        if self.stack_pointer >= self.max_length:
            raise StackOverflowException("Can't add to stack because of full stack")
        self._stack[self.stack_pointer] = value
        self.stack_pointer += 1

    def pop(self):
        value = self._stack[self.stack_pointer]
        self.stack_pointer -= 1
        return value
