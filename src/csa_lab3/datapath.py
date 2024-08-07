from typing import Callable
from csa_lab3.isa import MemoryCell, Opcode, Register


class ALU:
    is_negative: bool = False
    is_zero: bool = False

    min_value: int = -(2 ** 31)
    max_value: int = 2 ** 31 - 1

    def set_flags(self, value: int) -> None:
        if value > self.max_value:
            value = value & self.min_value

        if value < self.min_value:
            value = value & self.min_value
        self.is_negative = value < 0
        self.is_zero = value == 0

    def alu_add(self, a, b):
        return a + b
    
    def alu_sub(self, a, b):
        return a - b
    
    def alu_inc(self, a, b: int = 0):
        return a + 1
    
    def alu_dec(self, a, b: int = 0):
        return a - 1
    
    def alu_and(self, a, b):
        return a and b
    
    def alu_or(self, a, b):
        return a or b
    
    def alu_neg(self, a, b):
        return ~a + 1
    
    def alu_cmp(self, a, b):
        return a + ~b + 1
    
    def alu_not(self, a, b):
        return ~a
    
    def alu_mod(self, a, b):
        return a%b
    
    def exec(self, opcode: Opcode, operand1: int, operand2: int) -> int:
        operations: dict[Opcode, Callable[[int, int], int]] = {
            Opcode.ADD: self.alu_add,
            Opcode.SUB: self.alu_sub,
            Opcode.INC: self.alu_inc,
            Opcode.DEC: self.alu_dec,
            Opcode.AND: self.alu_and,
            Opcode.OR: self.alu_or,
            Opcode.CMP: self.alu_cmp,
            Opcode.NEG: self.alu_neg,
            Opcode.NOT: self.alu_not,
            Opcode.MOD: self.alu_mod
        }
        operation: Callable[[int, int], int] = operations.get(opcode, None)
        result: int = 0
        if operation is None:
            raise UnknownALUOperationException('Unknown ALU operation')
        result = operation(operand1, operand2)
        self.set_flags(result)
        return result



class Mux:
    inputs: list[Callable[[], int]]

    def __init__(self, inputs: list[Callable[[], int]]) -> None:
        self.inputs = inputs

    def run(self, select: int) -> int:
        return self.inputs[select]()

class Printer():
    output: list[str]
    def __init__(self) -> None:
        self.output = []

    def write_port(self, port_id, value) -> None:
        if port_id == 0:
            self.output.append(str(value))
        elif port_id == 1:
            self.output.append(chr(value))


class Reader():
    input: list[str]
    port: int = 2

    def __init__(self, input) -> None:
        self.input = input

    def read_port(self, port: int):        
        if port == self.port:
            if len(self.input) != 0:
                return ord(self.input.pop(0))
            else:
                return 0


class DataPath:
    memory: list[MemoryCell]
    registers: dict[Register, int]
    memory_size: int
    alu: ALU = None
    printer: Printer
    reader: Reader
    mux_left: Mux
    mux_right: Mux
    
    def __init__(self, memory: list[MemoryCell], reader: Reader, memory_size: int = 2048):
        self.memory = memory
        self.printer = Printer()
        self.reader = reader
        self.registers = {}
        for register in Register:
            self.registers[register] = 0
        self.memory_size = memory_size
        self.alu = ALU()
        self.mux_left = Mux([lambda: self.registers[Register.IP], 
                             lambda: self.registers[Register.AC], 
                             lambda: 0])
        self.mux_right = Mux([lambda: self.registers[Register.DRR], 
                              lambda: 0])
        
    def latch_register(self, register: Register, value: int) -> None:
        self.registers[register] = value

    def register_output_wire(self, register: Register) -> int:
        return self.registers[register]
    
    def execute_arithmetic(self, opcode: Opcode, operand1: int = 0, operand2: int = 0) -> int:
        return self.alu.exec(opcode, operand1, operand2)
    
    def work_with_memory(self, read_signal: bool, write_signal: bool) -> None:
        address: int = self.registers[Register.AR]
        if read_signal:
            if self.memory[address].is_instruction:
                raise MistreatedInstructionAsDataException('Cannot read instruction as data')
            self.latch_register(Register.DRR, self.memory[address].data)

        if write_signal:
            self.memory[address].is_instruction = False
            self.memory[address].instruction = None
            self.memory[address].data = self.registers[Register.DRW]
    
    def is_zero(self) -> bool:
        return self.alu.is_zero

    def is_negative(self) -> bool:
        return self.alu.is_negative
    
    def read(self, port: int) -> int:
        if port == 2: 
            return self.reader.read_port(2)
 
    def write(self, symb: int, port: int) -> None:
        if port in [0, 1]:
            self.printer.write_port(port, symb)


class UnknownALUOperationException(Exception):
    pass


class MistreatedInstructionAsDataException(Exception):
    pass
