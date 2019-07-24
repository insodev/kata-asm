"""
start at 22:15 finished at 22:30

We want to create a simple interpreter of assembler which will support the following instructions:

mov x y - copies y (either a constant value or the content of a register) into register x
inc x - increases the content of register x by one
dec x - decreases the content of register x by one
jnz x y - jumps to an instruction y steps away (positive means forward, negative means backward), but only if x (a constant or a register) is not zero
Register names are alphabetical (letters only). Constants are always integers (positive or negative).

Note: the jnz instruction moves relative to itself. For example, an offset of -1 would continue at the previous instruction, while an offset of 2 would skip over the next instruction.

The function will take an input list with the sequence of the program instructions and will return a dictionary with the contents of the registers.

Also, every inc/dec/jnz on a register will always be followed by a mov on the register first, so you don't need to worry about uninitialized registers.

"""


class SimpleAssemblerInterpreter:
    def __init__(self, commands: list):
        self.commands = commands
        self.command_index = 0
        self.registers = {}

    def run(self):
        while self.command_index < len(self.commands):
            self.run_command(self.commands[self.command_index])

        return self.registers

    def run_command(self, command: str):
        command_name, *args = command.split()
        print(command_name, args, self.registers, self.command_index)
        getattr(self, command_name)(*args)

    def _get_value(self, constant_or_register):
        try:
            value = int(constant_or_register)
        except ValueError:
            value = self.registers.get(constant_or_register)

        return value

    def mov(self, x: str, y):
        self.registers[x] = self._get_value(y)
        self.command_index += 1

    def inc(self, x: str):
        self.registers[x] += 1
        self.command_index += 1

    def dec(self, x: str):
        self.registers[x] -= 1
        self.command_index += 1

    def jnz(self, x, y):
        x_value = self._get_value(x)

        if x_value:
            self.command_index += self._get_value(y)
        else:
            self.command_index += 1

    # @staticmethod
    # def get_jump_index(relative_delta: int) -> int:
    #     """
    #     Note: the jnz instruction moves relative to itself. For example, an offset of -1 would
    #     continue at the previous instruction, while an offset of 2 would skip over the next instruction.
    #     :param relative_delta:
    #     :return:
    #     """
    #
    #     if relative_delta < 0:
    #         return relative_delta


if __name__ == '__main__':
    print(SimpleAssemblerInterpreter(
        commands=[
            'mov a 5',
            'inc a',
            'dec a',
            'dec a',
            'jnz a -1',
            'inc a',
        ]).run())
