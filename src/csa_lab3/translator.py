from __future__ import annotations

import sys

from csa_lab3.isa import AddressingMode, Instruction, MemoryCell, Opcode, write_code


def preprocess_labels(lines: list[str]) -> dict[str, int]:
    index: int = 0
    labels: dict[str, int] = {}
    for line in lines:
        line = line.strip()
        if line.startswith(".data"):
            current_section = ".data"
            continue
        if line.startswith(".text"):
            current_section = ".text"
            continue
        if current_section == ".data":
            index, labels = preprocess_data_section_line(line, labels, index)
        elif current_section == ".text":
            index, labels = preprocess_text_section_line(line, labels, index)
        if line != "":
            index += 1
    return labels


def preprocess_text_section_line(line, labels, index):
    line_data: list[str] = line.strip().split(" ")
    if line_data[0].endswith(":"):  # label found
        if line_data[0][: len(line_data[0]) - 1] in labels:
            raise DuplicateLabelInitializationError()
        labels[line_data[0][: len(line_data[0]) - 1]] = index
    return index, labels


def preprocess_data_section_line(line, labels, index):
    data_line_components: list[str] = line.split(" ", 1)
    if data_line_components[0].endswith(":"):
        if data_line_components[0][: len(data_line_components[0]) - 1] in labels:
            raise DuplicateLabelInitializationError()
        labels[data_line_components[0][: len(data_line_components[0]) - 1]] = index
        if data_line_components[1].count("'") != 0:
            index = index + len(data_line_components[1]) - 2
    return index, labels


def process_data_section_line(line: str, index: int, labels: dict[str, int], memory: list[MemoryCell]):
    data_line_components: list[str] = line.split(" ", 1)
    if data_line_components[0].endswith(":"):
        labels[data_line_components[0][: len(data_line_components[0]) - 1]] = index
        labeled = True

    if labeled:
        stored_data_components: list[str] = data_line_components[1].split("', ")
        for element in stored_data_components:
            if element.startswith("'") and element.endswith("'"):
                element += chr(0)
                str_memory, index = _store_static_str(element[1 : len(element) - 2], index)
                for el in str_memory:
                    memory.append(el)
            else:
                int_memory, index = _store_static_int(int(element), index)
                memory.append(int_memory)
    return memory, labels


def process_data_line(line: str, index: int, labels: dict[str, int], memory: list[MemoryCell]) -> int:
    """Обрабатывает одну строку данных и возвращает обновлённый индекс."""
    data_line_components: list[str] = line.split(" ", 1)
    label, labeled = process_label(data_line_components[0], index, labels)

    if labeled:
        stored_data_components: list[str] = data_line_components[1].split("', ")
        index = process_data_elements(stored_data_components, index, memory)

    return index


def process_label(component: str, index: int, labels: dict[str, int]) -> tuple[str, bool]:
    """Обрабатывает метку в строке данных, если она существует."""
    if component.endswith(":"):
        label = component[:-1]  # Удаляем двоеточие
        labels[label] = index
        return label, True
    return "", False


def process_data_elements(elements: list[str], index: int, memory: list[MemoryCell]) -> int:
    """Обрабатывает каждый элемент данных и обновляет память и индекс."""
    for element in elements:
        if is_string_element(element):
            index = store_string_element(element, index, memory)
        else:
            index = store_integer_element(element, index, memory)
    return index


def is_string_element(element: str) -> bool:
    """Проверяет, является ли элемент строкой."""
    return element.startswith("'") and element.endswith("'")


def store_string_element(element: str, index: int, memory: list[MemoryCell]) -> int:
    """Сохраняет строковый элемент в памяти."""
    element += chr(0)  # Добавляем символ окончания строки
    str_memory, index = _store_static_str(element[1:-2], index)  # Убираем кавычки
    memory.extend(str_memory)  # Добавляем строку в память
    return index


def store_integer_element(element: str, index: int, memory: list[MemoryCell]) -> int:
    """Сохраняет целочисленный элемент в памяти."""
    int_memory, index = _store_static_int(int(element), index)
    memory.append(int_memory)
    return index


def process_operand(
    opcode: Opcode, operand_str: str, labels: dict[str, int]
) -> tuple[int | None, AddressingMode | None]:
    """Обрабатывает операнд и возвращает его вместе с режимом адресации."""
    if opcode in {Opcode.INPP, Opcode.OUTT}:  # Объединяем проверки для INPP и OUTT
        operand = int(operand_str)
        if opcode == Opcode.INPP and operand != 2:
            raise InvalidInputPortError()
        if opcode == Opcode.OUTT and operand not in {0, 1}:
            raise InvalidOutputPortError()
        return operand, None

    addressing_mode_map = {"$": AddressingMode.IMMEDIATE, "@": AddressingMode.DIRECT, "#": AddressingMode.INDIRECT}

    prefix = operand_str[0]
    if prefix in addressing_mode_map:
        return process_addr_operand(operand_str, labels), addressing_mode_map[prefix]

    if operand_str not in labels:
        raise NoLabelFoundError()

    return labels[operand_str], AddressingMode.DIRECT


def process_addr_instruction(
    op_ind: int, instr_line_components: list[str], labels: dict[str, int], operand_str: str
) -> tuple[Opcode, int | None, AddressingMode | None]:
    """Обрабатывает инструкцию и возвращает opcode, operand и addressing_mode."""
    opcode: Opcode = Opcode[instr_line_components[op_ind].upper()]
    operand: int | None = None
    addressing_mode: AddressingMode | None = None

    operand, addressing_mode = process_operand(opcode, operand_str, labels)

    return operand, addressing_mode


def process_addr_operand(operand_str: str, labels):
    if operand_str[1:].isdigit():
        return int(operand_str[1:])
    return labels[operand_str[1:]]


def process_text_line(line: str, index: int, labels: dict[str, int], memory: list[MemoryCell]) -> int:
    instr_line_components: list[str] = line.split(" ")

    # Проверяем метку
    labeled: bool = False
    if instr_line_components[0].endswith(":"):
        labels[instr_line_components[0][:-1]] = index
        labeled = True

    if labeled:
        opcode = Opcode[instr_line_components[1].upper()]
        operand, addressing_mode = None, None
        if len(instr_line_components) > 2:
            operand_str = instr_line_components[2]
            operand, addressing_mode = process_addr_instruction(1, instr_line_components, labels, operand_str)
    else:
        opcode = Opcode[instr_line_components[0].upper()]
        operand, addressing_mode = None, None
        if len(instr_line_components) > 1:
            operand_str = instr_line_components[1]
            operand, addressing_mode = process_addr_instruction(0, instr_line_components, labels, operand_str)

    memory.append(MemoryCell(index, True, Instruction(opcode, operand, addressing_mode)))
    return index


def process_source(filename: str) -> list[MemoryCell]:
    memory: list[MemoryCell] = []
    lines: list[str] = []
    with open(filename) as source_file:
        lines = [line.strip() for line in source_file if line.strip()]  # Читаем и сразу убираем пустые строки

    labels: dict[str, int] = {}

    # preprocess labels
    labels = preprocess_labels(lines)

    # process sources
    index = 0
    current_section: str = ""
    for line in lines:
        line = line.strip()
        if len(line) == 0:
            current_section = ""
            continue
        if line.startswith(".data"):
            current_section = ".data"
            continue
        if line.startswith(".text"):
            current_section = ".text"
            continue

        if current_section == ".data":
            index = process_data_line(line, index, labels, memory)

        elif current_section == ".text":
            index = process_text_line(line, index, labels, memory)
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


class DuplicateLabelInitializationError(Exception):
    def __init__(self):
        super().__init__("Duplicate label initialization")


class InvalidInputPortError(Exception):
    def __init__(self):
        super().__init__("Possible inpp port: 2")


class InvalidOutputPortError(Exception):
    def __init__(self):
        super().__init__("Possible outt port: 0,1")


class NoLabelFoundError(Exception):
    def __init__(self):
        super().__init__("Label not found")


def main(source, target):
    """Функция запуска транслятора. Параметры -- исходный и целевой файлы."""
    memory = process_source(source)
    write_code(target, memory)


if __name__ == "__main__":
    assert len(sys.argv) == 3, "Wrong arguments: translator.py <input_file> <target_file>"
    _, source, target = sys.argv
    main(source, target)
