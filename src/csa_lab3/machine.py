from __future__ import annotations

import logging
import sys

from csa_lab3.controlunit import ControlUnit
from csa_lab3.datapath import DataPath, Reader
from csa_lab3.isa import MemoryCell, Register, read_code


def simulation(memory: list[MemoryCell], stdin_data: list[str], limit: int) -> tuple[str, int]:
    reader: Reader = Reader(stdin_data)
    data_path: DataPath = DataPath(memory, reader)
    control_unit: ControlUnit = ControlUnit(data_path)
    counter: int = 0

    for i in memory:
        if i.is_instruction:
            control_unit.data_path.latch_register(Register.IP, i.index)
            break
    logging.debug("%s", control_unit)

    resume: bool = True
    while counter < limit and resume:
        resume = control_unit.decode_and_execute_instr()
        counter += 1

    if counter >= limit:
        logging.warning("Instruction counter limit exceeded!")

    return "".join(data_path.printer.output), counter


def main(memory_filename: str, stdin_filename: str) -> None:
    memory: list[MemoryCell] = read_code(memory_filename)

    stdin_data: list[str] = []
    with open(stdin_filename) as stdin_f:
        text: str = stdin_f.read()
        for char in text:
            stdin_data.append(char)
    output, instr_counter = simulation(memory, stdin_data, 600)
    print(output)
    print("instruction_counter: ", instr_counter)


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.DEBUG)
    logging.basicConfig(filename="result.log")
    assert len(sys.argv) == 3, "Wrong arguments: machine.py <memory_file> <stdin_file>"
    _, memory_file, stdin_file = sys.argv
    main(memory_file, stdin_file)
