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