import sys
from csa_lab3.isa import AddressingMode, Instruction, MemoryCell, Opcode, write_code


def process_source(filename: str) -> list[MemoryCell]:
    memory: list[MemoryCell] = []
    lines: list[str] = []
    with open(filename) as source_file:
        lines = source_file.readlines()
    labels: dict[str, int] = {}

    # preprocess labels
    index: int = 0
    for line in lines:
        line = line.strip()
        if line.startswith('.data'):  
            current_section = '.data'
            continue
        elif line.startswith('.text'):
            current_section = '.text'
            continue

        
        labeled: bool = False
        if current_section == '.data':
            data_line_components: list[str] = line.split(' ', 1)
            if data_line_components[0].endswith(':'):
                if  data_line_components[0][:len(data_line_components[0]) - 1] in labels:
                    raise DuplicateLabelInitializationException('Duplicate label initialization')
                labels[data_line_components[0][:len(data_line_components[0]) - 1]] = index
                if data_line_components[1].count('\'') != 0:
                    index = index + len(data_line_components[1])-2
        elif current_section == '.text':
            line_data: list[str] = line.strip().split(' ')
            if line_data[0].endswith(':'):  # label found
                if line_data[0][:len(line_data[0]) - 1] in labels:
                    raise DuplicateLabelInitializationException('Duplicate label initialization')

                labels[line_data[0][:len(line_data[0]) - 1]] = index
        if line != '':
            index += 1

    # process sources
    index = 0
    current_section: str = ''
    for line in lines:
        line = line.strip()
        if len(line) == 0:
            current_section = ''
            continue
        if line.startswith('.data'):  
            current_section = '.data'
            continue
        elif line.startswith('.text'):
            current_section = '.text'
            continue

        labeled: bool = False
        if current_section == '.data':
            data_line_components: list[str] = line.split(' ', 1)
            if data_line_components[0].endswith(':'):
                labels[data_line_components[0][:len(data_line_components[0]) - 1]] = index
                labeled = True

            if labeled:
                stored_data_components: list[str] = data_line_components[1].split('\', ')
                for element in stored_data_components:
                    if element.startswith('\'') and element.endswith('\''):
                        element+=chr(0)
                        str_memory, index = _store_static_str(element[1:len(element) - 2], index)
                        for el in str_memory:
                            memory.append(el)
                    else:
                        int_memory, index = _store_static_int(int(element), index)
                        memory.append(int_memory)

        elif current_section == '.text':
            instr_line_components: list[str] = line.split(' ')
            if instr_line_components[0].endswith(':'):
                labels[instr_line_components[0][:len(instr_line_components[0]) - 1]] = index
                labeled = True
            if labeled:
                opcode: Opcode = Opcode[instr_line_components[1].upper()]
                operand: int | None = None
                addressing_mode: AddressingMode | None = None
                # check for opcode and fill port into operand
                if len(instr_line_components) > 2:
                    operand_str: str = instr_line_components[2]
                    if opcode == Opcode.INPP:
                        operand = int(operand_str)
                        if operand != 2:
                            raise InvalidInputPortException('Possible inpp port: 2')
                    elif opcode == Opcode.OUTT:
                        operand = int(operand_str)
                        if operand not in [0, 1]:
                            raise InvalidOutputPortException('Possible outt pors: 0, 1')
                    elif operand_str.startswith('$'):
                        operand = int(operand_str[1:])
                        addressing_mode = AddressingMode.IMMEDIATE
                    elif operand_str.startswith('@'):
                        if operand_str[1:].isdigit():
                            operand = int(operand_str[1:])
                        else:
                            operand = labels[operand_str[1:]]
                        addressing_mode = AddressingMode.DIRECT
                    elif operand_str.startswith('#'):
                        if operand_str[1:].isdigit():
                            operand = int(operand_str[1:])
                        else:
                            operand = labels[operand_str[1:]]
                        addressing_mode = AddressingMode.INDIRECT
                    else:
                        if operand_str not in labels.keys():
                            raise NoLabelFoundException('Label not found')
                        operand = labels[operand_str]
                        addressing_mode = AddressingMode.DIRECT
                memory.append(MemoryCell(index, True, Instruction(opcode, operand, addressing_mode)))

            else:
                opcode: Opcode = Opcode[instr_line_components[0].upper()]
                operand: int | None = None
                addressing_mode: AddressingMode | None = None
                if len(instr_line_components) > 1:
                    operand_str: str = instr_line_components[1]
                    if opcode == Opcode.INPP:
                        operand = int(operand_str)
                        if operand != 2:
                            raise InvalidInputPortException('Possible inpp port: 2')
                    elif opcode == Opcode.OUTT:
                        operand = int(operand_str)
                        if operand not in [0, 1]:
                            raise InvalidOutputPortException('Possible outt pors: 0, 1')
                    elif operand_str.startswith('$'):
                        operand = int(operand_str[1:])
                        addressing_mode = AddressingMode.IMMEDIATE
                    elif operand_str.startswith('@'):
                        if operand_str[1:].isdigit():
                            operand = int(operand_str[1:])
                        else:
                            operand = labels[operand_str[1:]]
                        addressing_mode = AddressingMode.DIRECT
                    elif operand_str.startswith('#'):
                        if operand_str[1:].isdigit():
                            operand = int(operand_str[1:])
                        else:
                            operand = labels[operand_str[1:]]
                        addressing_mode = AddressingMode.INDIRECT
                    else:
                        if operand_str not in labels.keys():
                            raise NoLabelFoundException('Label not found')
                        operand = labels[operand_str]
                        addressing_mode = AddressingMode.DIRECT
                memory.append(MemoryCell(index, True, Instruction(opcode, operand, addressing_mode)))
        index += 1
    return memory


def _store_static_str(some_str: str, starting_index: int) -> tuple[list[MemoryCell], int]:
    result: list[MemoryCell] = []
    for ch in some_str:
        result.append(MemoryCell(starting_index, False, None, ord(ch)))
        starting_index += 1
    result.append(MemoryCell(starting_index, False, None, 0))
    return result, starting_index

def _store_static_int(some_int: int, index: int) -> tuple[MemoryCell, int]:
    result: MemoryCell = MemoryCell(index, False, None, some_int)
    return result, index


class DuplicateLabelInitializationException(Exception):
    pass


class InvalidInputPortException(Exception):
    pass


class InvalidOutputPortException(Exception):
    pass


class NoLabelFoundException(Exception):
    pass

def main(source, target):
    """Функция запуска транслятора. Параметры -- исходный и целевой файлы."""
    memory = process_source(source)
    write_code(target, memory)


if __name__ == "__main__":
    assert len(sys.argv) ==3, "Wrong arguments: translator.py <input_file> <target_file>"
    _, source, target = sys.argv
    main(source, target)