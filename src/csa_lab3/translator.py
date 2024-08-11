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
        if line.startswith('.data'):  # check which section
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




class DuplicateLabelInitializationException(Exception):
    pass