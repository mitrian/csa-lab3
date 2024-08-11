import json
from enum import Enum


class Opcode(Enum):
    ADD: str = 'ADD'
    SUB: str = 'SUB'
    INC: str = 'INC'
    DEC: str = 'DEC'
    AND: str = 'AND'
    OR: str = 'OR'
    NOT: str = 'NOT'
    NEG: str = 'NEG'
    LD: str = 'LD'
    ST: str = 'ST'
    CMP: str = 'CMP'
    JMP: str = 'JMP'
    JZ: str = 'JZ'
    HLT: str = 'HLT'
    MOD: str = 'MOD'
    INPP: str = 'INPP'
    OUTT: str = 'OUTT'
    LEA: str = 'LEA'
    JN: str = 'JN'

    def __str__(self):
        return self.name
    

class Register(Enum):
    AC: str = 'AC'
    DRR: str = 'DRR'
    IP: str = 'IP'
    AR: str = 'AR'
    CR: str = 'CR'
    DRW: str = 'DRW'
    
    def __str__(self):
        return self.name
    

class AddressingMode(Enum):
    IMMEDIATE: str = 'IMMEDIATE'
    DIRECT: str = 'DIRECT'
    INDIRECT: str = 'INDIRECT'

    def __str__(self):
        return self.name
    

class Instruction:
    opcode: Opcode
    operand: int | None
    addressing_mode: AddressingMode | None

    def __init__(self, opcode: Opcode, operand: int | None, addressing_mode: AddressingMode | None):
        self.opcode = opcode
        self.operand = operand
        self.addressing_mode = addressing_mode

    def __str__(self):
        return f'[opcode: {self.opcode!s}, operand: {self.operand!s}, addressing_mode: {self.addressing_mode!s}]'
    

class MemoryCell:
    index: int
    is_instruction: bool = False
    instruction: Instruction | None = None
    data: int = 0

    def __init__(self, index: int, is_instruction: bool, instruction: Instruction | None, data: int = 0):
        self.index = index
        self.is_instruction = is_instruction
        self.instruction = instruction
        self.data = data

    def _data_str(self) -> str:
        if self.data < 0 or self.data > 255:
            return str(self.data)
        else:
            return chr(self.data)

    def __str__(self):
        return f'index: {self.index} is_instruction: {self.is_instruction} instruction: {self.instruction!s} data: {self._data_str()}'
    

class CustomEnumEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Enum):
            return f'{o!s}'
        return super().default(o)
    
def write_code(filename: str, memory: list[MemoryCell]) -> None:
    with open(filename, 'w', encoding='utf-8') as file:
        buf: list[str] = []
        for cell in memory:
            data: str = ''
            if cell.is_instruction:
                data = json.dumps(
                    {
                        'index': cell.index,
                        'is_instruction': cell.is_instruction,
                        'instruction': {
                            'opcode': cell.instruction.opcode,
                            'operand': cell.instruction.operand,
                            'addressing_mode': cell.instruction.addressing_mode,
                        },
                        'data': 0,
                    },
                    cls=CustomEnumEncoder,
                )
            else:
                data = json.dumps(
                    {
                        'index': cell.index,
                        'is_instruction': cell.is_instruction,
                        'instruction': None,
                        'data': cell.data,
                    },
                    cls=CustomEnumEncoder,
                )
            buf.append(data)
        file.write('[' + ',\n'.join(buf) + ']')


def read_code(filename: str) -> list[MemoryCell]:
    with open(filename, 'r', encoding='utf-8') as file:
        memory_json: list[dict] = json.loads(file.read())

    memory: list[MemoryCell] = []
    for memory_cell_json in memory_json:
        instruction: Instruction | None = None if not memory_cell_json['is_instruction'] else Instruction(
            Opcode[memory_cell_json['instruction']['opcode']],
            memory_cell_json['instruction']['operand'],
            None if memory_cell_json['instruction']['addressing_mode'] is None else AddressingMode[memory_cell_json['instruction']['addressing_mode']]
        )
        data: int = 0 if memory_cell_json['is_instruction'] else memory_cell_json['data']
        memory_cell: MemoryCell = MemoryCell(
            memory_cell_json['index'],
            memory_cell_json['is_instruction'],
            instruction,
            data
        )
        memory.append(memory_cell)
    return memory