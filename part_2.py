"""

starting at 00:15
stop at 2:15

We want to create an interpreter of assembler which will support the following instructions:

mov x, y - copy y (either an integer or the value of a register) into register x.
inc x - increase the content of register x by one.
dec x - decrease the content of register x by one.
add x, y - add the content of the register x with y (either an integer or the value of a register)
    and stores the result in x (i.e. register[x] += y).
sub x, y - subtract y (either an integer or the value of a register) from the register x
    and stores the result in x (i.e. register[x] -= y).
mul x, y - same with multiply (i.e. register[x] *= y).
div x, y - same with integer division (i.e. register[x] /= y).
label: - define a label position (label = identifier + ":", an identifier being a string
    that does not match any other command). Jump commands and call are aimed to these labels positions in the program.
jmp lbl - jumps to to the label lbl.
cmp x, y - compares x (either an integer or the value of a register) and y (either an integer or
    the value of a register). The result is used in the conditional jumps (jne, je, jge, jg, jle and jl)
jne lbl - jump to the label lbl if the values of the previous cmp command were not equal.
je lbl - jump to the label lbl if the values of the previous cmp command were equal.
jge lbl - jump to the label lbl if x was greater or equal than y in the previous cmp command.
jg lbl - jump to the label lbl if x was greater than y in the previous cmp command.
jle lbl - jump to the label lbl if x was less or equal than y in the previous cmp command.
jl lbl - jump to the label lbl if x was less than y in the previous cmp command.
call lbl - call to the subroutine identified by lbl. When a ret is found in a subroutine,
    the instruction pointer should return to the instruction next to this call command.
ret - when a ret is found in a subroutine, the instruction pointer should return to the
    instruction that called the current function.
msg 'Register: ', x - this instruction stores the output of the program. It may contain text strings (delimited by
    single quotes) and registers. The number of arguments isn't limited and will vary, depending on the program.
end - this instruction indicates that the program ends correctly, so the stored output is
    returned (if the program terminates without this instruction it should return the default output: see below).
; comment - comments should not be taken in consideration during the execution of the
    program.
"""


class Interpreter:
    def __init__(self, program_lines: str):
        self.commands = [x.strip() for x in program_lines.splitlines()]
        self.command_index = 0
        self.registers = {}
        self.labels = {}
        self.call_stack = []
        self._cmp_flag = None
        self.success_flag = False
        self.messages = []

        self.available_instructions = {
            'mov': self.mov,
            'inc': self.inc,
            'dec': self.dec,
            'add': self.add,
            'sub': self.sub,
            'mul': self.mul,
            'div': self.div,
            'jmp': self.jmp,
            'cmp': self.cmp,
            'jne': self.jne,
            'je': self.je,
            'jge': self.jge,
            'jg': self.jg,
            'jle': self.jle,
            'jl': self.jl,
            'call': self.call,
            'ret': self.ret,
            'msg': self.msg,
            'end': self.end,
            ';': self.comment,
        }

        self.available_instructions_tuple = tuple(self.available_instructions.keys())
        self.parse_labels()

    def is_label(self, instruction: str):
        return not instruction.startswith(self.available_instructions_tuple)

    def parse_labels(self):
        for index, instruction in enumerate(self.commands):
            if self.is_label(instruction):
                label = instruction[:-1]
                self.labels[label] = index

    def _get_value(self, constant_or_register):
        try:
            value = int(constant_or_register)
        except ValueError:
            value = self.registers.get(constant_or_register)

        return value

    def mov(self, args: str):
        register, constant_or_register = args.split(', ')
        self.registers[register] = self._get_value(constant_or_register)
        self.command_index += 1

    def inc(self, args: str):
        self.registers[args] += 1
        self.command_index += 1

    def dec(self, args: str):
        self.registers[args] -= 1
        self.command_index += 1

    def add(self, args: str):
        register, constant_or_register = args.split(', ')
        self.registers[register] += self._get_value(constant_or_register)
        self.command_index += 1

    def sub(self, args: str):
        register, constant_or_register = args.split(', ')
        self.registers[register] -= self._get_value(constant_or_register)
        self.command_index += 1

    def mul(self, args: str):
        register, constant_or_register = args.split(', ')
        self.registers[register] *= self._get_value(constant_or_register)
        self.command_index += 1

    def div(self, args: str):
        register, constant_or_register = args.split(', ')
        self.registers[register] //= self._get_value(constant_or_register)
        self.command_index += 1

    def jmp(self, args: str):
        self.command_index = self.labels[args]

    def cmp(self, args: str):
        _x, _y = args.split(', ')
        x, y = self._get_value(_x), self._get_value(_y)
        self._cmp_flag = x - y

    def jne(self, args: str):
        if self._cmp_flag:
            self.jmp(args)

    def je(self, args: str):
        if not self._cmp_flag:
            self.jmp(args)

    def jge(self, args: str):
        if self._cmp_flag >= 0:
            self.jmp(args)

    def jg(self, args: str):
        if self._cmp_flag > 0:
            self.jmp(args)

    def jle(self, args: str):
        if self._cmp_flag <= 0:
            self.jmp(args)

    def jl(self, args: str):
        if self._cmp_flag < 0:
            self.jmp(args)

    def call(self, args: str):
        self.call_stack.append(self.command_index + 1)
        self.jmp(args)

    def ret(self, args: str):
        self.command_index = self.call_stack.pop()

    def msg(self, args: str):
        strings = []
        i = 0

        while i < len(args):
            if args[i] == '\'':
                i += 1
                current_argument = []
                while args[i] != '\'':
                    current_argument.append(args[i])
                    i += 1
                strings.append(''.join(current_argument))
            elif args[i].isalpha():
                current_key = []
                while i < len(args) and args[i].isalpha():
                    current_key.append(args[i])
                    i += 1
                strings.append(str(self.registers[''.join(current_key)]))
            elif args[i] == ';':
                break

            i += 1

        self.messages.append(''.join(strings))
        self.command_index += 1

    def end(self, args: str):
        self.command_index = len(self.commands)
        self.success_flag = True

    def comment(self, args: str):
        self.command_index += 1

    def exit_message(self):
        if self.success_flag:
            return ''.join(self.messages)
        else:
            return -1

    def run(self):
        while self.command_index < len(self.commands):
            self.run_command(self.commands[self.command_index])

        return self.exit_message()

    def skip_label(self):
        self.command_index += 1

    def run_command(self, command: str):
        # print(command, self.registers)

        if self.is_label(command):
            self.skip_label()
        else:
            command_name, *args_list = command.split(maxsplit=1)
            if args_list:
                args = args_list[0].strip()
            else:
                args = None

            self.available_instructions[command_name](args)


if __name__ == '__main__':
    program = """
                ; My first program
                mov  a, 4
                inc  a
                call function
                msg  '(5+1)/2 = ', a, '(5+1)/2 = ', a    ; output message
                end
                
                function:
                    div  a, 2
                    ret
                """

    print(Interpreter(program_lines=program).run())
