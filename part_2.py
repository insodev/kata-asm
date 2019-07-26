"""
24/07/19:
    starting at 00:15
    stop at 2:15
26/07/19
    start at 14:30
    stop at 18:40

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

import unittest


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
            ';': self.inc_ci,
            '_label': self.inc_ci,
            '': self.inc_ci,
        }

        self.available_instructions_tuple = tuple(self.available_instructions.keys())
        self.parsed_instructions = [self.parse_instruction(instruction=x) for x in self.commands]
        self.parse_labels()

    def inc_ci(self, *args):
        self.command_index += 1

    def parse_labels(self):
        for index, instruction in enumerate(self.parsed_instructions):
            command, args = instruction
            if command == '_label':
                self.labels[args[0]] = index + 1

    def _get_value(self, constant_or_register):
        try:
            value = int(constant_or_register)
        except ValueError:
            value = self.registers.get(constant_or_register)

        return value

    def mov(self, register, constant_or_register):
        self.registers[register] = self._get_value(constant_or_register)
        self.inc_ci()

    def inc(self, register):
        self.registers[register] += 1
        self.inc_ci()

    def dec(self, register: str):
        self.registers[register] -= 1
        self.inc_ci()

    def add(self, register, constant_or_register):
        self.registers[register] += self._get_value(constant_or_register)
        self.inc_ci()

    def sub(self, register, constant_or_register):
        self.registers[register] -= self._get_value(constant_or_register)
        self.inc_ci()

    def mul(self, register, constant_or_register):
        self.registers[register] *= self._get_value(constant_or_register)
        self.inc_ci()

    def div(self, register, constant_or_register):
        self.registers[register] //= self._get_value(constant_or_register)
        self.inc_ci()

    def jmp(self, label):
        self.command_index = self.labels[label]

    def cmp(self, x, y):
        _x, _y = self._get_value(x), self._get_value(y)
        self._cmp_flag = _x - _y
        self.inc_ci()

    def jne(self, label):
        if self._cmp_flag:
            self.jmp(label)
        else:
            self.inc_ci()

    def je(self, label):
        if not self._cmp_flag:
            self.jmp(label)
        else:
            self.inc_ci()

    def jge(self, label):
        if self._cmp_flag >= 0:
            self.jmp(label)
        else:
            self.inc_ci()

    def jg(self, label):
        if self._cmp_flag > 0:
            self.jmp(label)
        else:
            self.inc_ci()

    def jle(self, label):
        if self._cmp_flag <= 0:
            self.jmp(label)
        else:
            self.inc_ci()

    def jl(self, label):
        if self._cmp_flag < 0:
            self.jmp(label)
        else:
            self.inc_ci()

    def call(self, label):
        self.call_stack.append(self.command_index + 1)
        self.jmp(label)

    def ret(self):
        self.command_index = self.call_stack.pop()

    def msg(self, *args):
        strings = []

        for arg in args:
            assert isinstance(arg, str)
            if arg.startswith('\''):
                strings.append(arg[1:-1])
            else:
                strings.append(str(self._get_value(arg)))

        self.messages.append(''.join(strings))
        self.inc_ci()

    def end(self):
        self.command_index = len(self.commands)
        self.success_flag = True

    def comment(self, *args):
        self.inc_ci()

    def exit_message(self):
        if self.success_flag:
            return ''.join(self.messages)
        else:
            return -1

    def run_parsed(self):
        while self.command_index < len(self.parsed_instructions):
            command, args = self.parsed_instructions[self.command_index]

            # print(self.command_index, command, args)

            if command:
                self.available_instructions[command](*args)
            else:
                self.inc_ci()

        return self.exit_message()

    @staticmethod
    def parse_instruction(instruction: str):
        def valid_symbol(v):
            from string import ascii_letters, digits
            valid = ascii_letters + '_' + digits
            return v in valid

        command = ''
        args = []
        i = 0

        instruction = instruction.strip()

        try:
            while i < len(instruction):
                if valid_symbol(instruction[i]):
                    while i < len(instruction) and valid_symbol(instruction[i]):
                        command += instruction[i]
                        i += 1

                        try:
                            if instruction[i] == ':':
                                args.append(command)
                                command = '_label'
                                raise StopIteration()
                        except IndexError:
                            pass

                    i += 1
                    while i < len(instruction):
                        if valid_symbol(instruction[i]):
                            current_arg = ''

                            while i < len(instruction) and valid_symbol(instruction[i]):
                                current_arg += instruction[i]
                                i += 1
                            else:
                                args.append(current_arg)

                        elif instruction[i] == '-' or instruction[i].isdigit():
                            current_arg = instruction[i]
                            i += 1

                            while i < len(instruction) and instruction[i].isdigit():
                                current_arg += instruction[i]
                                i += 1
                            else:
                                args.append(current_arg)

                        elif instruction[i] == "'":
                            current_arg = instruction[i]
                            i += 1
                            while i < len(instruction) and instruction[i] != "'":
                                current_arg += instruction[i]
                                i += 1
                            else:
                                current_arg += "'"
                                args.append(current_arg)

                        elif instruction[i] == ';':
                            raise StopIteration()

                        i += 1
                    break

                elif instruction[i] == ';':
                    break
                i += 1
        except StopIteration:
            pass

        return command, args


def assembler_interpreter(program):
    return Interpreter(program_lines=program).run_parsed()


class AssemblerInterpreterTests(unittest.TestCase):
    def test_00_first_program(self):
        program = '''
        ; My first program
        mov  a, 5
        inc  a
        call function
        msg  '(5+1)/2 = ', a    ; output message
        end

        function:
            div  a, 2
            ret
        '''

        self.assertEqual(assembler_interpreter(program), '(5+1)/2 = 3')

    def test_01_program_factorial(self):
        program_factorial = '''
        mov   a, 5
        mov   b, a
        mov   c, a
        call  proc_fact
        call  print
        end

        proc_fact:
            dec   b
            mul   c, b
            cmp   b, 1
            jne   proc_fact
            ret

        print:
            msg   a, '! = ', c ; output text
            ret
        '''

        self.assertEqual(assembler_interpreter(program_factorial), '5! = 120')

    def test_02_program_fibonacci(self):
        program_fibonacci = '''
        mov   a, 8            ; value
        mov   b, 0            ; next
        mov   c, 0            ; counter
        mov   d, 0            ; first
        mov   e, 1            ; second
        call  proc_fib
        call  print
        end

        proc_fib:
            cmp   c, 2
            jl    func_0
            mov   b, d
            add   b, e
            mov   d, e
            mov   e, b
            inc   c
            cmp   c, a
            jle   proc_fib
            ret

        func_0:
            mov   b, c
            inc   c
            jmp   proc_fib

        print:
            msg   'Term ', a, ' of Fibonacci series is: ', b        ; output text
            ret
        '''

        self.assertEqual(assembler_interpreter(program_fibonacci), 'Term 8 of Fibonacci series is: 21')

    def test_03_program_mod(self):
        program_mod = '''
        mov   a, 11           ; value1
        mov   b, 3            ; value2
        call  mod_func
        msg   'mod(', a, ', ', b, ') = ', d        ; output
        end

        ; Mod function
        mod_func:
            mov   c, a        ; temp1
            div   c, b
            mul   c, b
            mov   d, a        ; temp2
            sub   d, c
            ret
        '''

        self.assertEqual(assembler_interpreter(program_mod), 'mod(11, 3) = 2')

    def test_04_program_gcd(self):
        program_gcd = '''
        mov   a, 81         ; value1
        mov   b, 153        ; value2
        call  init
        call  proc_gcd
        call  print
        end

        proc_gcd:
            cmp   c, d
            jne   loop
            ret

        loop:
            cmp   c, d
            jg    a_bigger
            jmp   b_bigger

        a_bigger:
            sub   c, d
            jmp   proc_gcd

        b_bigger:
            sub   d, c
            jmp   proc_gcd

        init:
            cmp   a, 0
            jl    a_abs
            cmp   b, 0
            jl    b_abs
            mov   c, a            ; temp1
            mov   d, b            ; temp2
            ret

        a_abs:
            mul   a, -1
            jmp   init

        b_abs:
            mul   b, -1
            jmp   init

        print:
            msg   'gcd(', a, ', ', b, ') = ', c
            ret
        '''

        self.assertEqual(assembler_interpreter(program_gcd), 'gcd(81, 153) = 9')

    def test_05_program_fail(self):
        program_fail = '''
        call  func1
        call  print
        end

        func1:
            call  func2
            ret

        func2:
            ret

        print:
            msg 'This program should return -1'
        '''

        self.assertEqual(assembler_interpreter(program_fail), -1)

    def test_06_program_power(self):
        program_power = '''
        mov   a, 2            ; value1
        mov   b, 10           ; value2
        mov   c, a            ; temp1
        mov   d, b            ; temp2
        call  proc_func
        call  print
        end

        proc_func:
            cmp   d, 1
            je    continue
            mul   c, a
            dec   d
            call  proc_func

        continue:
            ret

        print:
            msg a, '^', b, ' = ', c
            ret
        '''

        self.assertEqual(assembler_interpreter(program_power), '2^10 = 1024')


class ParseInstructionTests(unittest.TestCase):
    def test_comment(self):
        command, args = Interpreter.parse_instruction(';1234')

        self.assertEqual(command, '')

    def test_command(self):
        command, args = Interpreter.parse_instruction('     mov a, 5')
        self.assertEqual(command, 'mov')

    def test_label(self):
        command, args = Interpreter.parse_instruction('lbl:;1234')

        self.assertEqual('_label', command)
        self.assertEqual(['lbl'], args)

    def test_command_with_register(self):
        command, args = Interpreter.parse_instruction('inc  a')
        self.assertEqual('inc', command)
        self.assertEqual(['a'], args)

    def test_command_with_registers(self):
        command, args = Interpreter.parse_instruction('mov a, b')
        self.assertEqual('mov', command)
        self.assertEqual(['a', 'b'], args)

    def test_command_with_registers_comment(self):
        command, args = Interpreter.parse_instruction('mov a, b ;123')
        self.assertEqual('mov', command)
        self.assertEqual(['a', 'b'], args)

    def test_command_with_constants(self):
        command, args = Interpreter.parse_instruction('jmp 5')
        self.assertEqual('jmp', command)
        self.assertEqual(['5', ], args)

    def test_command_with_negative_constants(self):
        command, args = Interpreter.parse_instruction('cmp 5, -5 ;')
        self.assertEqual('cmp', command)
        self.assertEqual(['5', '-5', ], args)

    def test_command_with_string(self):
        command, args = Interpreter.parse_instruction('msg \'hello\'')
        self.assertEqual(["'hello'", ], args)

    def test_command_with_args(self):
        command, args = Interpreter.parse_instruction("msg 'hello ', user, '!', -7")
        self.assertEqual('msg', command)
        self.assertEqual(["'hello '", 'user', "'!'", '-7'], args)

    def test_only_command(self):
        command, args = Interpreter.parse_instruction('ret')
        self.assertEqual('ret', command)
        self.assertEqual([], args)

    def test_parse_program(self):
        program_power = '''
                ;test program for parse
        
                mov   a, 2            ; value1
                mov   c, a            ; temp1

                call  proc_func
                end

                proc_func:
                    cmp   d, 1
                    je    continue
                    call  proc_func

                continue:
                    ret

                print:
                    msg a, '^', b, ' = ', c
                    ret
                '''

        decoded = [
            ['', []],
            ['', []],
            ['', []],
            ['mov', ['a', '2']],
            ['mov', ['c', 'a']],
            ['', []],
            ['call', ['proc_func']],
            ['end', []],
            ['', []],
            ['_label', ['proc_func']],
            ['cmp', ['d', '1']],
            ['je', ['continue']],
            ['call', ['proc_func']],
            ['', []],
            ['_label', ['continue']],
            ['ret', []],
            ['', []],
            ['_label', ['print']],
            ['msg', ["a", "'^'", "b", "' = '", "c"]],
            ['ret', []],
            ['', []],
        ]

        d_index = 0
        for instruction in program_power.splitlines():
            command, args = Interpreter.parse_instruction(instruction)
            _command, _args = decoded[d_index]

            msg = '%s, %s' % (d_index, instruction)

            self.assertEqual(_command, command, msg=msg)
            self.assertEqual(_args, args, msg=msg)

            d_index += 1

    def test_labels_with_digits(self):
        command, args = Interpreter.parse_instruction('func_0:')
        self.assertEqual('_label', command)
        self.assertEqual(['func_0'], args)

        command, args = Interpreter.parse_instruction('call func_0')
        self.assertEqual('call', command)
        self.assertEqual(['func_0'], args)
