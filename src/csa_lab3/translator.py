from csa_lab3.isa import MemoryCell


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